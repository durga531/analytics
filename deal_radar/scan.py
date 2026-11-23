#!/usr/bin/env python3
"""Deal Radar: Black Friday price-drop and cross-retailer arbitrage scanner (AU).

Signals (advertised "was" prices are ignored; AU discounters inflate them):
  PRICE_DROP  - price fell vs the lowest price we previously recorded for that item.
  ARBITRAGE   - same product (barcode or model ref + brand) is materially cheaper at
                one AU retailer than the next-cheapest AU retailer.
  NEW_LISTING - item first seen after baseline, priority brand, already below an
                existing listing of the same product elsewhere.
  OZBARGAIN   - new OzBargain post matching watched keywords.

Stdlib only. State lives in deal_radar/state (committed to git between runs).
"""
import gzip
import json
import re
import sys
import time
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
STATE = ROOT / "state"
REPORTS = ROOT / "reports"
UA = "Mozilla/5.0 (compatible; deal-radar/1.0)"


def load_json(path, default):
    try:
        if str(path).endswith(".gz"):
            with gzip.open(path, "rt") as f:
                return json.load(f)
        return json.loads(Path(path).read_text())
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return default


def save_json(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    if str(path).endswith(".gz"):
        with gzip.open(path, "wt") as f:
            json.dump(obj, f, separators=(",", ":"))
    else:
        path.write_text(json.dumps(obj, indent=2, ensure_ascii=False))


def fetch(url, timeout=30, retries=2):
    last = None
    for i in range(retries + 1):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read()
        except Exception as e:  # noqa: BLE001
            last = e
            time.sleep(2 * (i + 1))
    raise last


# ---------------------------------------------------------------- matching keys
REF_RE = re.compile(r"\b([A-Z0-9]+(?:[-./][A-Z0-9]+)*)\b")
SEIKO_LIKE = re.compile(r"^([A-Z]{3,4}\d{2,3})[A-Z]?\d?$")


def norm_brand(v):
    v = (v or "").lower().strip()
    v = re.sub(r"[^a-z0-9 ]", "", v)
    return v.replace("watches", "").replace("watch", "").strip()


def ref_candidates(text):
    out = set()
    for tok in REF_RE.findall((text or "").upper()):
        t = re.sub(r"[-./]", "", tok)
        if 5 <= len(t) <= 20 and re.search(r"\d", t) and re.search(r"[A-Z]", t):
            m = SEIKO_LIKE.match(t)
            out.add(m.group(1) if m else t)
    return out


PF_EXCLUDE = re.compile(r"\b(tester|set|piece|pc|sample|mini|travel|atomi[sz]er|vial|refill|unboxed|deodorant|lotion|gel|body|hair|candle|shower|balm|soap|coffret|duo|trio|pack)\b")
BRAND_NOISE = re.compile(r"\b(christian|parfums?|paris|fragrances?|perfumes?|by|the|and|co|ltd)\b")


BRAND_ALIAS = {
    "ysl": "yves saint laurent", "yvessaintlaurent": "yves saint laurent", "saintlaurent": "yves saint laurent",
    "giorgioarmani": "armani", "emporioarmani": "armani", "armani": "armani",
    "dolcegabbana": "dolce gabbana", "dolceandgabbana": "dolce gabbana", "dg": "dolce gabbana",
    "jeanpaulgaultier": "jean paul gaultier", "jpg": "jean paul gaultier",
    "pacorabanne": "rabanne", "rabanne": "rabanne", "hugoboss": "boss", "boss": "boss",
    "calvinklein": "calvin klein", "ck": "calvin klein", "carolinaherrera": "carolina herrera",
    "dior": "dior", "chanel": "chanel", "versace": "versace", "gianniversace": "versace",
    "maisonmargiela": "maison margiela", "margiela": "maison margiela", "tomford": "tom ford",
}


def pf_key(brand, title, vtitle):
    t = f"{title} {vtitle if vtitle and vtitle != 'Default Title' else ''}".lower()
    t = t.replace("&", " and ").replace("*", " ").replace("’", "'")
    t = re.sub(r"\bl'?eau de", "eau de", t)
    if PF_EXCLUDE.search(t):
        return None
    m = re.search(r"(\d+(?:\.\d+)?)\s*ml\b", t)
    if not m:
        return None
    ml = str(int(round(float(m.group(1)))))
    if re.search(r"eau de parfum|\bedp\b", t):
        conc = "edp"
    elif re.search(r"eau de toilette|\bedt\b", t):
        conc = "edt"
    elif re.search(r"\bextrait\b|\bparfum\b|\belixir\b", t):
        conc = "parfum"
    elif re.search(r"eau de cologne|\bedc\b", t):
        conc = "edc"
    else:
        return None
    b = BRAND_NOISE.sub(" ", re.sub(r"[^a-z0-9 ]", " ", (brand or "").lower()))
    b = " ".join(b.split())
    raw_brand_words = set(b.split())
    b = BRAND_ALIAS.get(b.replace(" ", ""), b)
    name = re.sub(r"eau de (parfum|toilette|cologne)|\b(edp|edt|edc|extrait|spray|intense?)\b", " ", t)
    name = re.sub(r"\d+(\.\d+)?\s*ml\b", " ", name)
    name = re.sub(r"\b(for (men|women|him|her|unisex)|men|women|homme|femme|pour)\b", " ", name)
    name = re.sub(r"[^a-z0-9 ]", " ", name)
    stop = set(b.split()) | raw_brand_words | {"christian", "giorgio", "emporio", "parfum", "elixir", "and", "by", "new"}
    words = sorted({w for w in name.split() if w not in stop})
    if not words or not b:
        return None
    flags = "-intense" if re.search(r"\bintense\b", t) else ""
    flags += "-elixir" if "elixir" in t else ""
    return f"pf:{b.replace(' ', '')}:{'-'.join(words)}:{conc}{flags}:{ml}"


def product_keys(p, v, category):
    """Return matching keys for cross-store comparison."""
    keys = set()
    sku = (v.get("sku") or "").strip()
    bc = (v.get("barcode") or "").strip()
    for code in (bc, sku):
        if re.fullmatch(r"\d{12,14}", code):
            keys.add("ean:" + code.lstrip("0"))
    if category == "perfume":
        k = pf_key(p.get("vendor"), p.get("title"), v.get("title"))
        if k:
            keys.add(k)
    if category == "watches":
        brand = norm_brand(p.get("vendor"))
        for r in ref_candidates(sku) | ref_candidates(p.get("title")):
            keys.add(f"ref:{brand}:{r}")
    return sorted(keys)


# ---------------------------------------------------------------- shopify scan
def scan_shopify(store, max_pages):
    items = {}
    dom = store["domain"]
    for page in range(1, max_pages + 1):
        try:
            data = json.loads(fetch(f"https://{dom}/products.json?limit=250&page={page}"))
        except Exception as e:  # noqa: BLE001
            print(f"  ! {dom} page {page}: {e}", file=sys.stderr)
            break
        prods = data.get("products", [])
        if not prods:
            break
        for p in prods:
            avail = [v for v in p.get("variants", []) if v.get("available")]
            if not avail:
                continue
            if store["category"] == "perfume":
                chosen = avail  # each bottle size is its own item
            else:
                chosen = [min(avail, key=lambda x: float(x.get("price") or 1e9))]
            for v in chosen:
                price = float(v.get("price") or 0)
                if price <= 0:
                    continue
                cmp_ = float(v.get("compare_at_price") or 0) or None
                multi = store["category"] == "perfume" and len(p.get("variants", [])) > 1
                vt = v.get("title") if multi else ""
                pid = f"{p['id']}:{v['id']}" if multi else str(p["id"])
                url = f"https://{dom}/products/{p.get('handle')}" + (f"?variant={v['id']}" if multi else "")
                items[pid] = {
                    "t": (p.get("title", "") + (f" {vt}" if vt else ""))[:140],
                    "b": p.get("vendor", ""),
                    "ty": p.get("product_type", ""),
                    "p": price,
                    "c": cmp_,
                    "u": url,
                    "k": product_keys(p, v, store["category"]),
                }
        time.sleep(0.4)
    return items


def is_priority(brand, title, category, cfg):
    hay = f"{brand} {title}".lower()
    return any(b in hay for b in cfg["priority_brands"].get(category, []))


# ---------------------------------------------------------------- ozbargain
OZB_NS = {"ozb": "https://www.ozbargain.com.au", "dc": "http://purl.org/dc/elements/1.1/"}


def scan_ozbargain(cfg, seen):
    out = []
    kws = [k.lower() for k in cfg["ozbargain"]["keywords"]]
    for feed in cfg["ozbargain"]["feeds"]:
        try:
            root = ET.fromstring(fetch(feed))
        except Exception as e:  # noqa: BLE001
            print(f"  ! ozbargain {feed}: {e}", file=sys.stderr)
            continue
        for it in root.iter("item"):
            link = it.findtext("link") or ""
            node = link.rstrip("/").split("/")[-1]
            if node in seen:
                continue
            title = it.findtext("title") or ""
            cats = [c.text or "" for c in it.findall("category")]
            meta = it.find("ozb:meta", OZB_NS)
            votes = int(meta.get("votes-pos", 0)) if meta is not None else 0
            expired = it.find("ozb:title-msg", OZB_NS)
            if expired is not None and expired.get("type") == "expired":
                continue
            hay = (title + " " + " ".join(cats)).lower()
            hit = [k for k in kws if re.search(r"\b" + re.escape(k) + r"\b", hay)]
            fashion_beauty = any(c in ("Fashion & Apparel", "Health & Beauty") for c in cats)
            if hit or (fashion_beauty and votes >= cfg["ozbargain"]["min_votes_for_generic"]):
                out.append({
                    "type": "OZBARGAIN", "node": node, "title": title, "url": link,
                    "merchant_url": meta.get("url") if meta is not None else None,
                    "votes": votes, "keywords": hit, "categories": cats,
                    "expires": meta.get("expiry") if meta is not None else None,
                })
                seen[node] = datetime.now(timezone.utc).isoformat()
            elif fashion_beauty:
                pass  # re-evaluate later when votes may have grown
    # dedupe across feeds
    uniq = {o["node"]: o for o in out}
    return list(uniq.values())


# ---------------------------------------------------------------- main
def main():
    cfg = load_json(ROOT / "config.json", {})
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    hist = load_json(STATE / "items.json.gz", {})       # {domain: {pid: {...,"lo":min price,"f":first_seen}}}
    alerted = load_json(STATE / "alerted.json", {})     # {alert_id: price_at_alert}
    ozb_seen = load_json(STATE / "ozb_seen.json", {})
    runlog = load_json(STATE / "runs.json", [])
    first_run = not hist

    alerts, current, store_stats = [], {}, {}
    for store in cfg["shopify_stores"]:
        dom, cat = store["domain"], store["category"]
        print(f"scanning {dom} ...", file=sys.stderr)
        items = scan_shopify(store, cfg["max_pages_per_store"])
        prev = hist.get(dom, {})
        store_stats[dom] = {"items": len(items), "baseline": not prev}
        if not items and prev:  # fetch failure: keep old state, skip
            current[dom] = prev
            store_stats[dom]["error"] = True
            continue
        th = cfg["thresholds"][cat]
        for pid, it in items.items():
            old = prev.get(pid)
            it["lo"] = min(it["p"], old["lo"]) if old else it["p"]
            it["f"] = old["f"] if old else now
            it["cat"], it["store"], it["dom"] = cat, store["name"], dom
            if not old or not prev:
                continue
            ref = old["lo"]  # lowest price we have ever recorded
            drop = 1 - it["p"] / ref if ref else 0
            if (drop * 100 >= th["min_drop_pct"] and ref - it["p"] >= th["min_saving_aud"]
                    and ref >= th["min_price_aud"]):
                alerts.append({
                    "type": "PRICE_DROP", "id": f"drop:{dom}:{pid}", "category": cat,
                    "store": store["name"], "title": it["t"], "brand": it["b"], "url": it["u"],
                    "price": it["p"], "previous_low": ref, "saving": round(ref - it["p"], 2),
                    "drop_pct": round(drop * 100, 1), "advertised_rrp": it["c"],
                    "priority_brand": is_priority(it["b"], it["t"], cat, cfg),
                })
        current[dom] = items

    # ---- cross-retailer arbitrage
    groups = {}
    for dom, items in current.items():
        for pid, it in items.items():
            for k in it.get("k", []):
                groups.setdefault(k, {})
                best = groups[k].get(dom)
                if best is None or it["p"] < best[1]["p"]:
                    groups[k][dom] = (pid, it)
    arb_seen = set()
    ac = cfg["arbitrage"]
    for k, by_dom in groups.items():
        if len(by_dom) < 2:
            continue
        ranked = sorted(by_dom.values(), key=lambda x: x[1]["p"])
        (pid1, c1), (_, c2) = ranked[0], ranked[1]
        gap = c2["p"] - c1["p"]
        gap_pct = gap / c2["p"] * 100
        # guard against mismatched products (e.g. 30ml vs 100ml) sharing a weak key
        if gap_pct > 70:
            continue
        sig = (c1["dom"], pid1)
        if sig in arb_seen:
            continue
        if gap_pct >= ac["min_gap_pct"] and gap >= ac["min_gap_aud"]:
            arb_seen.add(sig)
            alerts.append({
                "type": "ARBITRAGE", "id": f"arb:{c1['dom']}:{pid1}", "category": c1["cat"],
                "store": c1["store"], "title": c1["t"], "brand": c1["b"], "url": c1["u"],
                "price": c1["p"], "next_best_store": c2["store"], "next_best_price": c2["p"],
                "next_best_url": c2["u"], "saving": round(gap, 2), "gap_pct": round(gap_pct, 1),
                "all_prices": {v[1]["store"]: v[1]["p"] for v in ranked}, "match_key": k,
                "advertised_rrp": c1["c"],
                "priority_brand": is_priority(c1["b"], c1["t"], c1["cat"], cfg),
            })

    # ---- dedupe against previous alerts (re-alert only if materially cheaper)
    extra = cfg["realert_extra_drop_pct"] / 100
    fresh = []
    for a in alerts:
        prev_price = alerted.get(a["id"])
        if prev_price is not None and a["price"] > prev_price * (1 - extra):
            continue
        fresh.append(a)

    def score(a):
        return a["saving"] * (2.0 if a.get("priority_brand") else 1.0) * (1.3 if a["type"] == "PRICE_DROP" else 1.0)

    fresh.sort(key=score, reverse=True)
    per_cat = cfg.get("max_alerts_per_category", 6)
    top, used = [], {}
    for a in fresh:
        if used.get(a["category"], 0) < per_cat and len(top) < cfg["max_alerts_per_run"]:
            top.append(a)
            used[a["category"]] = used.get(a["category"], 0) + 1
    for a in top:
        alerted[a["id"]] = a["price"]

    ozb = scan_ozbargain(cfg, ozb_seen) if cfg["ozbargain"].get("feeds") else []
    ozb.sort(key=lambda o: o["votes"], reverse=True)

    # ---- persist
    slim = {d: {pid: {k: v for k, v in it.items() if k not in ("cat", "store", "dom")}
                for pid, it in items.items()} for d, items in current.items()}
    save_json(STATE / "items.json.gz", slim)
    save_json(STATE / "alerted.json", alerted)
    save_json(STATE / "ozb_seen.json", ozb_seen)
    runlog.append({"at": now, "first_run": first_run, "stores": store_stats,
                   "alerts_total": len(fresh), "alerts_sent": len(top), "ozbargain": len(ozb)})
    save_json(STATE / "runs.json", runlog[-200:])

    result = {"generated_at": now, "first_run": first_run, "store_stats": store_stats,
              "alerts": top, "alerts_suppressed_or_overflow": len(fresh) - len(top),
              "ozbargain": ozb[:25]}
    save_json(REPORTS / "latest.json", result)
    (REPORTS / "latest.md").write_text(render_md(result))
    print(json.dumps({"alerts": len(top), "ozbargain": len(ozb), "stores": store_stats}))


def render_md(r):
    L = [f"# Deal Radar run {r['generated_at']}", ""]
    if r["first_run"]:
        L += ["_Baseline run: price-drop signals start next run. Arbitrage signals below are live._", ""]
    for a in r["alerts"]:
        star = "★ " if a.get("priority_brand") else ""
        if a["type"] == "ARBITRAGE":
            L.append(f"- {star}**ARBITRAGE** [{a['title']}]({a['url']}) ${a['price']:.0f} at {a['store']} "
                     f"vs ${a['next_best_price']:.0f} at {a['next_best_store']} "
                     f"(save ${a['saving']:.0f}, {a['gap_pct']}%)")
        else:
            L.append(f"- {star}**PRICE DROP** [{a['title']}]({a['url']}) ${a['price']:.0f} at {a['store']}, "
                     f"down from ${a['previous_low']:.0f} (-{a['drop_pct']}%, save ${a['saving']:.0f})")
    if r["ozbargain"]:
        L += ["", "## OzBargain"]
        for o in r["ozbargain"]:
            L.append(f"- [{o['title']}]({o['url']}) (+{o['votes']} votes)")
    if not r["alerts"] and not r["ozbargain"]:
        L.append("No new qualifying deals this run.")
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    main()
