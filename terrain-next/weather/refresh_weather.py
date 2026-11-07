#!/usr/bin/env python3
"""Daily weather for every TERRAIN district (Open-Meteo, CC BY 4.0). Standard library only.

usage: python3 refresh_weather.py OUT_JSON   (reads district_points.json and district_meta.json beside this file)
Flags use stated thresholds: IMD rainfall categories (heavy 64.5 mm, very heavy 115.6 mm, extremely heavy 204.5 mm a day),
IMD heat thresholds (40 C plains; 45 C extreme; in hills, where the forecast point is at 1,000 m or more, 30 C and at least
4.5 C above the same model's past-week mean maximum), a cold threshold (minimum 10 C plains, 0 C hills), the US NWS
heat-index 'danger' band (feels-like 41 C), warming or cooling of 3 C against the same model's past week, and TERRAIN's own
exterior-work window (under 2 mm a day and 12 to 35 C for seven days). Anomalies use the same source on both sides; the
1991-2020 normals (NASA POWER) are used only for the wet-week rainfall comparison. Temperatures are downscaled by Open-Meteo to each district's population-weighted elevation (where people live), not the
centre point's own height. Planning signals, not official warnings.
"""
import json, os, sys, time, urllib.request, urllib.parse, datetime, calendar
HERE = os.path.dirname(os.path.abspath(__file__))
API = "https://api.open-meteo.com/v1/forecast"
DAILY = "temperature_2m_max,temperature_2m_min,apparent_temperature_max,precipitation_sum,precipitation_probability_max"

def fetch(batch, meta):
    elev = ",".join(str(meta.get(k, {}).get("elev")) if (meta.get(k, {}).get("elev") or 0) > 0 else "nan" for k, _ in batch)
    q = {"latitude": ",".join(str(p[1]) for _, p in batch), "longitude": ",".join(str(p[0]) for _, p in batch), "elevation": elev,
         "daily": DAILY, "timezone": "Asia/Kolkata", "forecast_days": 7, "past_days": 7}
    url = API + "?" + urllib.parse.urlencode(q)
    for attempt in range(4):
        try:
            with urllib.request.urlopen(url, timeout=60) as r:
                data = json.load(r)
            return data if isinstance(data, list) else [data]
        except Exception as e:  # noqa: BLE001
            if attempt == 3:
                raise
            time.sleep(2 ** (attempt + 1))

def main(out):
    pts = json.load(open(os.path.join(HERE, "district_points.json")))
    meta = json.load(open(os.path.join(HERE, "district_meta.json")))
    ids = sorted(pts, key=int)
    res = {}
    for i in range(0, len(ids), 100):
        batch = [(k, pts[k]) for k in ids[i:i + 100]]
        for (k, _), r in zip(batch, fetch(batch, meta)):
            res[k] = r["daily"]; res[k]["_elev"] = r.get("elevation")
        time.sleep(1)
    days = res[ids[0]]["time"]
    today = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=5, minutes=30))).date().isoformat()
    ti = days.index(today) if today in days else 7
    fut = slice(ti, ti + 7); past = slice(max(0, ti - 7), ti)
    month = int(days[ti][5:7]); ndays = calendar.monthrange(int(days[ti][:4]), month)[1]
    districts, counts = {}, {}
    def r1(x): return None if x is None else round(x, 1)
    for k in ids:
        d = res[k]; m = meta.get(k, {})
        tx = d["temperature_2m_max"][fut]; tn = d["temperature_2m_min"][fut]; at = d["apparent_temperature_max"][fut]
        pr = d["precipitation_sum"][fut]; pp = d["precipitation_probability_max"][fut]; pr_past = d["precipitation_sum"][past]
        hill = (d.get("_elev") or 0) >= 1000
        tx_past = [x for x in d["temperature_2m_max"][past] if x is not None]
        tn_past = [x for x in d["temperature_2m_min"][past] if x is not None]
        txp = sum(tx_past) / len(tx_past) if tx_past else None
        mean_past = (sum(tx_past) + sum(tn_past)) / (len(tx_past) + len(tn_past)) if tx_past and tn_past else None
        flags = []
        t0x, t0n, a0, p0 = tx[0], tn[0], at[0], pr[0]
        if t0x is not None and t0x >= 45: flags.append("heat_extreme")
        elif t0x is not None and not hill and t0x >= 40: flags.append("heat")
        elif t0x is not None and hill and t0x >= 30 and txp is not None and t0x - txp >= 4.5: flags.append("heat")
        if a0 is not None and a0 >= 41 and "heat_extreme" not in flags: flags.append("humid_heat")
        pmax3 = max([x for x in pr[:3] if x is not None] or [0])
        if pmax3 >= 204.5: flags.append("rain_extreme")
        elif pmax3 >= 115.6: flags.append("rain_very_heavy")
        elif pmax3 >= 64.5: flags.append("rain_heavy")
        if t0n is not None and t0n <= (0 if hill else 10): flags.append("cold")
        wk = sum(x or 0 for x in pr)
        norm_wk = (m["pr"][month - 1] * 7 / ndays) if m.get("pr") else None
        if norm_wk is not None and wk >= 50 and wk >= 2 * norm_wk: flags.append("wet_week")
        if all((x or 0) < 2 for x in pr) and all(t is not None and 12 <= t <= 35 for t in tx): flags.append("dry_window")
        anom = None
        nx = [((a or 0) + (b or 0)) / 2 for a, b in zip(tx[:3], tn[:3]) if a is not None and b is not None]
        if nx and mean_past is not None:
            anom = round(sum(nx) / len(nx) - mean_past, 1)
            if anom >= 3: flags.append("warming")
            if anom <= -3: flags.append("cooling")
        for f in flags: counts.setdefault(f, {"districts": 0, "hh": 0, "aff": 0}); counts[f]["districts"] += 1; counts[f]["hh"] += m.get("hh", 0); counts[f]["aff"] += m.get("aff", 0)
        districts[k] = {"tx": [r1(x) for x in tx], "tn": [r1(x) for x in tn], "at": [r1(x) for x in at], "pr": [r1(x) for x in pr],
                        "pp": pp, "pr7_past": r1(sum(x or 0 for x in pr_past)), "pr7_next": r1(wk),
                        "pr7_norm": None if norm_wk is None else r1(norm_wk), "d3": anom, "elev": d.get("_elev"), "flags": flags}
    doc = {"built_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="minutes"), "today": days[ti],
           "days": days[fut], "source": "Open-Meteo forecast API (open-meteo.com, CC BY 4.0), point at each district's centre; normals NASA POWER 1991-2020 monthly",
           "label": "directional", "counts": counts, "districts": districts}
    json.dump(doc, open(out, "w"), separators=(",", ":"))
    print("weather for", len(districts), "districts, today", days[ti], {k: v["districts"] for k, v in counts.items()})

if __name__ == "__main__":
    main(sys.argv[1])
