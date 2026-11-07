"""Keepa API connector for Amazon.in: licensed product, rating, review-count, sales-rank and price history.

Keepa is a paid data service (https://keepa.com/#!api). It is not Amazon and does not scrape on your behalf
from your machine; you query Keepa's own database. The key is read from an environment variable
(KEEPA_API_KEY by default) and is never printed, logged or stored. Keepa takes the key as a URL
parameter, so every error message is redacted before it leaves this module.

Signals and what they mean:
  * new ratings in a window: the change in Amazon's rating count. The best public proxy for units sold;
    only a fraction of buyers rate, and that fraction differs by category and brand.
  * monthly_sold: Amazon's own "bought in past month" badge, in brackets such as 100+. A floor, set for
    some products only.
  * sales-rank drops: each improvement in best-seller rank roughly marks a sale, useful for slow sellers.
  * rating: Amazon's star average, 0 to 5.
None of these is market share. A brand rollup describes the products you fetched, not the category.
"""
from __future__ import annotations

from collections import defaultdict
import csv
import html
import json
import os
from pathlib import Path
import statistics
import time
from datetime import datetime, timezone

from .models import now, valid_asin

API = "https://api.keepa.com/"
DOMAIN_IN = 10
KEEPA_TIME_OFFSET = 21564000  # minutes between the Unix epoch and Keepa time zero
# csv history indices (Keepa product object)
AMAZON, NEW, SALES, LISTPRICE, RATING, COUNT_REVIEWS = 0, 1, 3, 4, 16, 17
SERIES = {"amazon_price": AMAZON, "new_price": NEW, "sales_rank": SALES, "list_price": LISTPRICE, "rating": RATING, "rating_count": COUNT_REVIEWS}
PRICE_SERIES = {"amazon_price", "new_price", "list_price"}


class KeepaError(RuntimeError):
    def __init__(self, message, http_status=None, tokens_left=None, refill_in_ms=None):
        super().__init__(message)
        self.http_status, self.tokens_left, self.refill_in_ms = http_status, tokens_left, refill_in_ms


# ---------------------------------------------------------------- time and series helpers
def keepa_now(epoch_seconds=None):
    return int((time.time() if epoch_seconds is None else epoch_seconds) // 60) - KEEPA_TIME_OFFSET


def keepa_to_iso(minutes):
    if minutes is None or minutes <= 0:
        return None
    return datetime.fromtimestamp((minutes + KEEPA_TIME_OFFSET) * 60, timezone.utc).isoformat(timespec="minutes")


def series(product, index):
    data = product.get("csv") or []
    arr = data[index] if index < len(data) else None
    if not arr:
        return []
    return [(arr[i], arr[i + 1]) for i in range(0, len(arr) - 1, 2)]


def last_value(points):
    for t, v in reversed(points):
        if v is not None and v >= 0:
            return t, v
    return None, None


def value_at(points, t):
    """Value in force at Keepa minute t: the last point at or before t. None if t precedes the history."""
    found = None
    for pt, v in points:
        if pt <= t:
            found = v
        else:
            break
    return None if found is None or found < 0 else found


def rank_drops(points, since):
    """Count improvements in best-seller rank after `since` (each roughly marks a sale)."""
    drops, prev = 0, None
    for t, v in points:
        if v is None or v <= 0:
            prev = None
            continue
        if prev is not None and t >= since and v < prev:
            drops += 1
        prev = v
    return drops


def money(paise):
    return None if paise is None or paise < 0 else round(paise / 100, 2)


def norm_brand(value):
    return " ".join(str(value or "").replace(" ", " ").split()).casefold()


# ---------------------------------------------------------------- summary of one product
def summarize(product, window_days=90, now_minutes=None):
    """Flatten a Keepa product object into the fields the research kit stores and compares."""
    t_now = keepa_now() if now_minutes is None else now_minutes
    win = window_days * 1440
    pts = {name: series(product, idx) for name, idx in SERIES.items()}
    stats = product.get("stats") or {}
    rating_as_of = product.get("lastRatingUpdate") or last_value(pts["rating_count"])[0]
    # Measure the rating window from the date Keepa last refreshed ratings, not from today, so stale data
    # does not look like zero sales.
    anchor = rating_as_of if rating_as_of and rating_as_of > 0 else t_now
    _, count_now = last_value(pts["rating_count"])
    count_then = value_at(pts["rating_count"], anchor - win)
    flags = []
    first_count_t = pts["rating_count"][0][0] if pts["rating_count"] else None
    if count_now is not None and count_then is None and first_count_t is not None:
        count_then = next((v for _, v in pts["rating_count"] if v is not None and v >= 0), None)
        flags.append("rating_history_shorter_than_window")
    new_ratings = (count_now - count_then) if count_now is not None and count_then is not None else None
    if new_ratings is not None and new_ratings < 0:
        flags.append("rating_count_fell")  # Amazon removes ratings at times, or variations were regrouped
        new_ratings = 0
    if rating_as_of and t_now - rating_as_of > 30 * 1440:
        flags.append("ratings_older_than_30_days")
    if count_now is None:
        flags.append("no_rating_history")
    _, rating_raw = last_value(pts["rating"])
    _, rank_now = last_value(pts["sales_rank"])
    drops = stats.get(f"salesRankDrops{window_days}") if window_days in (30, 90, 180, 365) else None
    if drops is None and pts["sales_rank"]:
        drops = rank_drops(pts["sales_rank"], t_now - win)
    if product.get("parentAsin"):
        flags.append("variation_of_" + product["parentAsin"])
    tree = product.get("categoryTree") or []
    return {
        "asin": product.get("asin"),
        "title": product.get("title") or "",
        "brand": (product.get("brand") or product.get("manufacturer") or "").strip() or None,
        "manufacturer": product.get("manufacturer"),
        "model": product.get("model"),
        "parent_asin": product.get("parentAsin"),
        "root_category": product.get("rootCategory"),
        "category_path": " > ".join(c.get("name", "") for c in tree) or None,
        "listed_since": keepa_to_iso(product.get("listedSince")),
        "rating": round(rating_raw / 10, 1) if rating_raw is not None else None,
        "rating_count": count_now,
        f"new_ratings_{window_days}d": new_ratings,
        "ratings_as_of": keepa_to_iso(rating_as_of),
        "monthly_sold_floor": product.get("monthlySold"),
        "monthly_sold_as_of": keepa_to_iso(product.get("lastSoldUpdate")),
        "sales_rank": rank_now,
        f"rank_drops_{window_days}d": drops,
        "amazon_price_inr": money(last_value(pts["amazon_price"])[1]),
        "new_price_inr": money(last_value(pts["new_price"])[1]),
        "list_price_inr": money(last_value(pts["list_price"])[1]),
        "keepa_updated": keepa_to_iso(product.get("lastUpdate")),
        "flags": ";".join(flags),
    }


# ---------------------------------------------------------------- client
class KeepaClient:
    """Sequential, token-aware client. `fetch` is injectable for tests: fetch(url, params) -> (status, dict)."""

    def __init__(self, key=None, key_env="KEEPA_API_KEY", domain=DOMAIN_IN, fetch=None, max_wait_s=900, sleep=time.sleep):
        self._key = key if key is not None else os.environ.get(key_env, "")
        if not self._key:
            raise ValueError(f"No Keepa key found. Set the {key_env} environment variable on this computer; never paste the key into a chat or a file in this project.")
        self.domain, self.max_wait_s, self.sleep = domain, max_wait_s, sleep
        self._fetch = fetch or self._http
        self.tokens_left = None
        self.tokens_used = 0

    def _redact(self, text):
        return str(text).replace(self._key, "<key>") if self._key else str(text)

    def _http(self, url, params):
        import httpx
        try:
            r = httpx.get(url, params=params, timeout=120, headers={"Accept-Encoding": "gzip"})
        except httpx.HTTPError as exc:  # the URL inside the exception carries the key
            raise KeepaError(self._redact(f"Network error calling Keepa: {exc}")) from None
        try:
            body = r.json()
        except ValueError:
            body = {"error": {"message": self._redact(r.text[:200])}}
        return r.status_code, body

    def get(self, endpoint, **params):
        params = {"key": self._key, "domain": self.domain, **params}
        waited = 0.0
        while True:
            status, body = self._fetch(API + endpoint, params)
            self.tokens_left = body.get("tokensLeft", self.tokens_left)
            self.tokens_used += body.get("tokensConsumed", 0) or 0
            payload = any(body.get(k) for k in ("products", "bestSellersList", "categories"))
            if status == 200 and (payload or not body.get("error")):
                return body  # in a batch, an error can sit beside good results
            err = body.get("error") or {}
            msg = self._redact(err.get("message") or f"HTTP {status}")
            if status == 429:  # out of tokens: wait for the bucket to refill, then retry the same request
                wait = max(1.0, (body.get("refillIn") or 60000) / 1000 + 1)
                if waited + wait > self.max_wait_s:
                    raise KeepaError(f"Out of Keepa tokens and the refill wait exceeds {self.max_wait_s:.0f} s. Rerun later or use a smaller batch.", 429, body.get("tokensLeft"), body.get("refillIn"))
                self.sleep(wait)
                waited += wait
                continue
            hint = {402: "The key does not grant API access: check the subscription on keepa.com.",
                    400: "Keepa rejected the request; check the ASINs or category ID."}.get(status, "")
            raise KeepaError(f"Keepa {status}: {msg}. {hint}".strip(), status, body.get("tokensLeft"), body.get("refillIn"))

    def products(self, asins, window_days=90, batch=20, history_days=400, refresh_ratings=False):
        """Yield product objects. rating=1 adds rating and rating-count history for up to 1 extra token.
        refresh_ratings=True asks Keepa to re-read offers and ratings from Amazon now: about 6 tokens a product."""
        asins = [valid_asin(a) for a in asins]
        for i in range(0, len(asins), batch):
            params = {"asin": ",".join(asins[i:i + batch]), "stats": window_days, "rating": 1, "days": history_days}
            if refresh_ratings:
                params.update({"offers": 20, "only-live-offers": 1})
            body = self.get("product", **params)
            for p in body.get("products") or []:
                yield p

    def bestsellers(self, category, range_days=90):
        body = self.get("bestsellers", category=category, range=range_days)
        lst = body.get("bestSellersList") or {}
        return lst.get("asinList") or [], keepa_to_iso(lst.get("lastUpdate"))

    def categories(self, term):
        body = self.get("search", type="category", term=term)
        out = []
        for cid, c in (body.get("categories") or {}).items():
            out.append({"category_id": int(cid), "name": c.get("name"), "parent": c.get("parent"), "products": c.get("productCount"),
                        "avg_rating": (c.get("avgRating") / 10) if c.get("avgRating") not in (None, -1) else None,
                        "avg_ratings_per_product": c.get("avgReviewCount"), "brands": c.get("brandCount"),
                        "top_brands": ", ".join(c.get("topBrands") or [])})
        return sorted(out, key=lambda r: -(r["products"] or 0))


# ---------------------------------------------------------------- storage
SCHEMA = """
CREATE TABLE IF NOT EXISTS keepa_runs (
  run_id TEXT PRIMARY KEY, kind TEXT NOT NULL, grp TEXT, category_id INTEGER, started_at TEXT NOT NULL,
  finished_at TEXT, status TEXT NOT NULL, tokens_used INTEGER, metadata_json TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS keepa_snapshots (
  run_id TEXT NOT NULL REFERENCES keepa_runs(run_id), asin TEXT NOT NULL, grp TEXT, bestseller_rank INTEGER,
  fetched_at TEXT NOT NULL, summary_json TEXT NOT NULL, PRIMARY KEY(run_id, asin));
CREATE TABLE IF NOT EXISTS keepa_series (
  asin TEXT NOT NULL, series TEXT NOT NULL, ts TEXT NOT NULL, value REAL, PRIMARY KEY(asin, series, ts));
"""


def ensure_schema(db):
    db.executescript(SCHEMA)


def store_products(db, run_id, products, grp=None, ranks=None, window_days=90):
    ensure_schema(db)
    n = 0
    for p in products:  # commit per product, so a failure later in a run keeps what was already fetched
        s = summarize(p, window_days)
        if not s["asin"]:
            continue
        with db:
            db.execute("INSERT OR REPLACE INTO keepa_snapshots VALUES (?,?,?,?,?,?)",
                       (run_id, s["asin"], grp, (ranks or {}).get(s["asin"]), now(), json.dumps(s, ensure_ascii=False)))
            for name, idx in SERIES.items():
                for t, v in series(p, idx):
                    if t is None or t <= 0:
                        continue
                    val = None if v is None or v < 0 else (v / 100 if name in PRICE_SERIES else v / 10 if name == "rating" else v)
                    db.execute("INSERT OR IGNORE INTO keepa_series VALUES (?,?,?,?)", (s["asin"], name, keepa_to_iso(t), val))
        n += 1
    return n


def start(db, kind, grp=None, category_id=None, **meta):
    import uuid
    ensure_schema(db)
    run_id = uuid.uuid4().hex
    with db:
        db.execute("INSERT INTO keepa_runs VALUES (?,?,?,?,?,?,?,?,?)", (run_id, kind, grp, category_id, now(), None, "running", None, json.dumps(meta)))
    return run_id


def finish(db, run_id, status, tokens):
    with db:
        db.execute("UPDATE keepa_runs SET finished_at=?, status=?, tokens_used=? WHERE run_id=?", (now(), status, tokens, run_id))


# ---------------------------------------------------------------- commands
def cmd_categories(term, client):
    return {"categories": client.categories(term), "tokens_left": client.tokens_left,
            "next_step": "Pick a category_id, then run keepa-bestsellers with it."}


def cmd_bestsellers(db, client, category, grp, top=100, range_days=90, window_days=90, batch=20, refresh_ratings=False):
    if not 1 <= top <= 500:
        raise ValueError("--top must be between 1 and 500")
    run_id = start(db, "bestsellers", grp, int(category) if str(category).isdigit() else None, top=top, range=range_days, window_days=window_days)
    try:
        asins, list_updated = client.bestsellers(category, range_days)
        asins = asins[:top]
        if not asins:
            finish(db, run_id, "empty_list", client.tokens_used)
            return {"status": "empty_list", "note": "Keepa has no best-seller list for this category on amazon.in; no tokens were charged."}
        ranks = {a: i + 1 for i, a in enumerate(asins)}
        stored = store_products(db, run_id, client.products(asins, window_days, batch, refresh_ratings=refresh_ratings), grp, ranks, window_days)
        finish(db, run_id, "completed", client.tokens_used)
    except BaseException:
        finish(db, run_id, "failed", client.tokens_used)
        raise
    return {"status": "completed", "run_id": run_id, "group": grp, "products": stored, "list_updated": list_updated,
            "tokens_used": client.tokens_used, "tokens_left": client.tokens_left}


def cmd_products(db, client, asins, grp, window_days=90, batch=20, refresh_ratings=False):
    run_id = start(db, "products", grp, None, count=len(asins), window_days=window_days)
    try:
        stored = store_products(db, run_id, client.products(asins, window_days, batch, refresh_ratings=refresh_ratings), grp, None, window_days)
        finish(db, run_id, "completed", client.tokens_used)
    except BaseException:
        finish(db, run_id, "failed", client.tokens_used)
        raise
    return {"status": "completed", "run_id": run_id, "group": grp, "products": stored, "tokens_used": client.tokens_used, "tokens_left": client.tokens_left}


def latest_rows(db, grp, window_days=90):
    ensure_schema(db)
    run = db.execute("SELECT run_id, kind, started_at FROM keepa_runs WHERE grp=? AND status='completed' ORDER BY started_at DESC LIMIT 1", (grp,)).fetchone()
    if not run:
        raise ValueError(f"No completed Keepa run for group {grp!r}. Run keepa-bestsellers or keepa-products with --group first.")
    rows = [dict(json.loads(r["summary_json"]), bestseller_rank=r["bestseller_rank"])
            for r in db.execute("SELECT * FROM keepa_snapshots WHERE run_id=? ORDER BY COALESCE(bestseller_rank, 99999), asin", (run["run_id"],))]
    return run, rows


def brand_rollup(rows, window_days=90):
    key = f"new_ratings_{window_days}d"
    drops_key = f"rank_drops_{window_days}d"
    groups, names = defaultdict(list), defaultdict(lambda: defaultdict(int))
    for r in rows:
        b = norm_brand(r.get("brand")) or "(no brand)"
        groups[b].append(r)
        names[b][r.get("brand") or "(no brand)"] += 1
    total_new = sum((r.get(key) or 0) for r in rows)
    out = []
    for b, rs in groups.items():
        rated = [r for r in rs if r.get("rating") is not None and r.get("rating_count")]
        weight = sum(r["rating_count"] for r in rated)
        new = sum((r.get(key) or 0) for r in rs)
        prices = [r.get("amazon_price_inr") or r.get("new_price_inr") for r in rs]
        prices = [p for p in prices if p]
        ranks = [r["bestseller_rank"] for r in rs if r.get("bestseller_rank")]
        out.append({
            "brand": max(names[b].items(), key=lambda kv: kv[1])[0],
            "products": len(rs),
            "best_rank": min(ranks) if ranks else None,
            f"new_ratings_{window_days}d": new,
            "share_of_new_ratings": round(new / total_new, 4) if total_new else None,
            "rating_weighted": round(sum(r["rating"] * r["rating_count"] for r in rated) / weight, 2) if weight else None,
            "ratings_total": weight,
            "bought_past_month_floor": sum(r.get("monthly_sold_floor") or 0 for r in rs) or None,
            f"rank_drops_{window_days}d": sum(r.get(drops_key) or 0 for r in rs),
            "median_price_inr": round(statistics.median(prices)) if prices else None,
            "products_with_stale_ratings": sum(1 for r in rs if "ratings_older_than_30_days" in (r.get("flags") or "")),
        })
    out.sort(key=lambda r: (-(r[f"new_ratings_{window_days}d"] or 0), r["best_rank"] or 99999))
    return out, total_new


def cmd_brands(db, grp, out_dir, window_days=90):
    run, rows = latest_rows(db, grp, window_days)
    brands, total_new = brand_rollup(rows, window_days)
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    for name, data in (("keepa_products.csv", rows), ("keepa_brands.csv", brands)):
        with (out / name).open("w", encoding="utf-8", newline="") as h:
            w = csv.DictWriter(h, fieldnames=list(data[0]) if data else ["empty"])
            w.writeheader()
            w.writerows(data)
    build_brand_html(grp, run, rows, brands, total_new, out / "keepa_brands.html", window_days)
    return {"group": grp, "run_started": run["started_at"], "products": len(rows), "brands": len(brands),
            "csv": [str(out / "keepa_products.csv"), str(out / "keepa_brands.csv")], "report": str(out / "keepa_brands.html")}


def build_brand_html(grp, run, rows, brands, total_new, path, window_days):
    e = lambda v: html.escape("" if v is None else str(v))
    key = f"new_ratings_{window_days}d"
    stale = sum(1 for r in rows if "ratings_older_than_30_days" in (r.get("flags") or ""))
    top = brands[0] if brands else None
    lead = (f"{e(top['brand'])} drew {round(100 * (top['share_of_new_ratings'] or 0))}% of new ratings across these {len(rows)} products in the last {window_days} days."
            if top and top.get("share_of_new_ratings") else "Too few rating changes to rank brands.")
    bar = lambda s: f'<span class="bar"><i style="width:{round(100 * (s or 0))}%"></i></span>'
    brow = "".join(f"<tr><td>{e(b['brand'])}</td><td class=n>{e(b['products'])}</td><td class=n>{e(b['best_rank'])}</td><td class=n>{e(b[key])}</td>"
                   f"<td>{bar(b['share_of_new_ratings'])} {e(round(100 * b['share_of_new_ratings'], 1) if b['share_of_new_ratings'] is not None else '')}%</td>"
                   f"<td class=n>{e(b['rating_weighted'])}</td><td class=n>{e(b['bought_past_month_floor'])}</td><td class=n>{e(b['median_price_inr'])}</td></tr>" for b in brands)
    prow = "".join(f"<tr><td class=n>{e(r.get('bestseller_rank'))}</td><td><a href='https://www.amazon.in/dp/{e(r['asin'])}'>{e(r['asin'])}</a></td><td>{e((r.get('title') or '')[:80])}</td><td>{e(r.get('brand'))}</td>"
                   f"<td class=n>{e(r.get('rating'))}</td><td class=n>{e(r.get('rating_count'))}</td><td class=n>{e(r.get(key))}</td><td class=n>{e(r.get('monthly_sold_floor'))}</td>"
                   f"<td class=n>{e(r.get('amazon_price_inr') or r.get('new_price_inr'))}</td><td class=f>{e(r.get('ratings_as_of', '') and r['ratings_as_of'][:10])}</td><td class=f>{e(r.get('flags'))}</td></tr>" for r in rows)
    doc = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(grp)}: brands on Amazon.in</title><style>
body{{font:14px/1.5 system-ui,-apple-system,Segoe UI,sans-serif;color:#1d1d1b;background:#fbfaf7;margin:0;padding:24px;max-width:1180px}}
h1{{font:400 26px/1.25 Georgia,serif;margin:0 0 6px}} .k{{color:#a35f00;font-size:11px;letter-spacing:.08em;text-transform:uppercase;font-weight:700}}
table{{border-collapse:collapse;width:100%;margin:12px 0 28px;background:#fff}} th,td{{padding:7px 8px;border-bottom:1px solid #e6e1d8;text-align:left;vertical-align:top}}
th{{font-size:11px;text-transform:uppercase;letter-spacing:.05em;color:#6b665e}} td.n{{text-align:right;font-variant-numeric:tabular-nums}} td.f{{font-size:11.5px;color:#6b665e}}
.bar{{display:inline-block;width:110px;height:8px;background:#efedf5;border-radius:4px;vertical-align:middle}} .bar i{{display:block;height:8px;background:#756bb1;border-radius:4px}}
.box{{border:1px solid #e6e1d8;background:#fff;border-radius:10px;padding:10px 14px;margin:14px 0}} .box p{{margin:4px 0}} a{{color:#b4321e}}
</style></head><body>
<div class="k">Keepa · Amazon.in · {e(run['kind'])} run of {e(run['started_at'][:10])}</div>
<h1>{lead}</h1>
<div class="box"><p><b>Can say:</b> which brands are gaining ratings fastest among the products fetched, their star averages, prices and Amazon's own "bought in past month" floor.</p>
<p><b>Cannot say:</b> market share, offline sales or sales in any district. Only some buyers leave a rating and the share differs by brand and price. "Bought in past month" is a bracketed floor that Amazon shows for some products only.</p>
<p>{stale} of {len(rows)} products have ratings older than 30 days in Keepa; rerun with --refresh-ratings to update them (about 6 tokens a product).</p></div>
<h2>Brands</h2><table><tr><th>Brand</th><th>Products</th><th>Best rank</th><th>New ratings, {window_days} days</th><th>Share of new ratings</th><th>Stars (weighted)</th><th>Bought past month, floor</th><th>Median price ₹</th></tr>{brow}</table>
<h2>Products</h2><table><tr><th>Rank</th><th>ASIN</th><th>Title</th><th>Brand</th><th>Stars</th><th>Ratings</th><th>New, {window_days} days</th><th>Bought past month</th><th>Price ₹</th><th>Ratings as of</th><th>Flags</th></tr>{prow}</table>
<p class="k">Source: Keepa API (licensed Amazon data). Generated {e(now()[:16])} UTC.</p></body></html>"""
    Path(path).write_text(doc, encoding="utf-8")
