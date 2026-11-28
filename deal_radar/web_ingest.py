#!/usr/bin/env python3
"""Match products scraped from non-feed retailers (Chemist Warehouse, Angus & Coote, ...)
against the Shopify price book in state/items.json.gz, and track their own price drops.

Input: JSON file, list of {"store","category","brand","title","price","url"} (price in AUD).
Output: reports/web_latest.json with ARBITRAGE / BEATEN / PRICE_DROP findings, deduped
against state/alerted.json.

Usage: python3 web_ingest.py /path/to/scraped.json
"""
import json
import sys
from datetime import datetime, timezone

import re

from scan import STATE, REPORTS, ROOT, load_json, save_json, pf_key, ref_candidates, norm_brand, is_grail


def keys_for(row):
    if row["category"] == "perfume":
        k = pf_key(row.get("brand"), row["title"], "")
        return [k] if k else []
    if row["category"] == "watches":
        b = norm_brand(row.get("brand"))
        return [f"ref:{b}:{r}" for r in ref_candidates(row["title"])]
    return []


def main(path):
    cfg = load_json(ROOT / "config.json", {})
    rows = json.loads(open(path).read())
    book = load_json(STATE / "items.json.gz", {})
    stores = {s["domain"]: s["name"] for s in cfg["shopify_stores"]}
    alerted = load_json(STATE / "alerted.json", {})
    web_hist = load_json(STATE / "web_items.json", {})
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")

    index = {}
    for dom, items in book.items():
        for it in items.values():
            for k in it.get("k", []):
                cur = index.get(k)
                if cur is None or it["p"] < cur["p"]:
                    index[k] = {"p": it["p"], "store": stores.get(dom, dom), "url": it["u"], "t": it["t"]}

    ac = cfg["arbitrage"]
    out = []
    g = cfg.get("grail", {})
    junk = re.compile(r"repair|parts|not working|spares|replica|homage|strap only|box only|dial only|movement only", re.I)
    for r in rows:
        try:
            price = float(str(r["price"]).replace(",", "").replace("$", ""))
        except (KeyError, TypeError, ValueError):
            continue
        if junk.search(r.get("title", "")):
            continue
        preowned = str(r.get("condition", "")).lower().startswith(("pre", "used", "vintage"))
        min_gap_pct = g.get("preowned_min_gap_pct", 45) if preowned else ac["min_gap_pct"]
        floors = g.get("absolute_floor_aud", {})
        hay = f"{r.get('brand','')} {r['title']}".lower()
        for fb, floor in floors.items():
            if re.search(r"(?<![a-z])" + re.escape(fb) + r"(?![a-z])", hay) and price < floor:
                out.append({"type": "BELOW_FLOOR", "id": f"floor:{r['url']}", "store": r["store"], "title": r["title"],
                            "url": r["url"], "price": price, "floor": floor, "saving": round(floor - price, 2),
                            "category": "watches", "condition": r.get("condition"), "grail": True,
                            "verify": "Open this listing page and confirm it is a genuine, complete, working watch "
                                      "(not parts, strap, box, replica) before notifying."})
                break
        prev = web_hist.get(r["url"])
        lo = min(price, prev["lo"]) if prev else price
        th = cfg["thresholds"].get(r["category"], cfg["thresholds"]["clothes"])
        if prev and prev["lo"] - price >= th["min_saving_aud"] and (1 - price / prev["lo"]) * 100 >= th["min_drop_pct"]:
            out.append({"type": "PRICE_DROP", "id": f"drop:{r['url']}", "store": r["store"], "title": r["title"],
                        "url": r["url"], "price": price, "previous_low": prev["lo"],
                        "saving": round(prev["lo"] - price, 2), "category": r["category"]})
        web_hist[r["url"]] = {"lo": lo, "p": price, "t": r["title"], "seen": now}
        for k in keys_for(r):
            other = index.get(k)
            if not other:
                continue
            gap = other["p"] - price
            if gap >= ac["min_gap_aud"] and gap / other["p"] * 100 >= min_gap_pct:
                out.append({"type": "ARBITRAGE", "id": f"arb:{r['url']}", "store": r["store"], "title": r["title"],
                            "url": r["url"], "price": price, "next_best_store": other["store"],
                            "next_best_price": other["p"], "next_best_url": other["url"],
                            "saving": round(gap, 2), "gap_pct": round(gap / other["p"] * 100, 1),
                            "category": r["category"], "match_key": k, "condition": r.get("condition"),
                            "compared_to": "cheapest new price at an AU dealer feed"})
            elif -gap >= ac["min_gap_aud"] and -gap / price * 100 >= ac["min_gap_pct"]:
                # the advertised "sale" is beaten by a feed retailer
                out.append({"type": "BEATEN", "id": f"beat:{r['url']}", "store": other["store"],
                            "title": other["t"], "url": other["url"], "price": other["p"],
                            "sale_store": r["store"], "sale_price": price, "sale_url": r["url"],
                            "saving": round(-gap, 2), "category": r["category"], "match_key": k})
            break

    extra = cfg["realert_extra_drop_pct"] / 100
    fresh = [a for a in out if alerted.get(a["id"]) is None or a["price"] <= alerted[a["id"]] * (1 - extra)]
    for a in fresh:
        if a["type"] == "BELOW_FLOOR":
            continue
        gp = a.get("gap_pct") or (round((1 - a["price"] / a["previous_low"]) * 100, 1) if a.get("previous_low") else 0)
        a["grail"] = bool(g) and a["type"] in ("ARBITRAGE", "PRICE_DROP") and \
            is_grail("", a["title"], a["category"], cfg) and a["price"] + a["saving"] >= g.get("min_price_aud", 0) and \
            gp >= (g.get("min_gap_pct", 20) if a["type"] == "ARBITRAGE" else g.get("min_drop_pct", 20))
    fresh.sort(key=lambda a: (a.get("grail", False), a["saving"]), reverse=True)
    for a in fresh:
        alerted[a["id"]] = a["price"]
    save_json(STATE / "alerted.json", alerted)
    save_json(STATE / "web_items.json", web_hist)
    save_json(REPORTS / "web_latest.json", {"generated_at": now, "input_rows": len(rows), "findings": fresh})
    print(json.dumps({"input_rows": len(rows), "findings": len(fresh)}))


if __name__ == "__main__":
    main(sys.argv[1])
