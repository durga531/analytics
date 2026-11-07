from collections import defaultdict
import csv
from datetime import date, datetime, timedelta
import html
import json
from pathlib import Path
from zoneinfo import ZoneInfo
from .models import now


def compare(db,output,group=None,days=180,as_of=None,verified_only=False,prior_strength=20,scorer_version=None):
    if days < 1 or prior_strength < 0:
        raise ValueError("days must be positive; prior-strength must be nonnegative")
    today = date.fromisoformat(as_of) if as_of else datetime.now(ZoneInfo("Asia/Kolkata")).date()
    cutoff = (today-timedelta(days=days-1)).isoformat()
    if not scorer_version:
        latest = db.execute("SELECT scorer_version FROM review_sentiment ORDER BY scored_at DESC,rowid DESC LIMIT 1").fetchone()
        if not latest:
            raise ValueError("No sentiment results yet; run 'score' first")
        scorer_version = latest[0]
    products = db.execute("SELECT * FROM products" + (" WHERE compare_group=?" if group else "") + " ORDER BY compare_group,asin",(group,) if group else ()).fetchall()
    if not products:
        raise ValueError("No products in this comparison group")
    scores, stats = defaultdict(list),defaultdict(lambda:defaultdict(int))
    for row in db.execute("""SELECT r.*,s.sentiment_score,s.score_status,
        (SELECT COUNT(DISTINCT o.asin) FROM review_observations o WHERE o.review_id=r.review_id) AS observed_asins
        FROM reviews r LEFT JOIN review_sentiment s ON s.review_id=r.review_id AND s.scorer_version=?""",(scorer_version,)):
        stat = stats[row["asin"]]
        stat["total_collected"] += 1
        if row["observed_asins"] > 1:
            stat["excluded_pooled"] += 1
            continue
        if not row["review_date"]:
            stat["excluded_undated"] += 1
            continue
        if not cutoff <= row["review_date"] <= today.isoformat():
            stat["excluded_outside_window"] += 1
            continue
        if verified_only and row["verified"] != 1:
            stat["excluded_not_verified"] += 1
            continue
        stat["n_in_window"] += 1
        if row["score_status"] != "scored":
            stat["excluded_unscored"] += 1
            continue
        scores[row["asin"]].append(row["sentiment_score"])
        stat["n_verified"] += int(row["verified"] == 1)
        stat["n_negative"] += int(row["sentiment_score"] <= -.05)
    grouped = defaultdict(list)
    for product in products:
        grouped[product["compare_group"]].extend(scores[product["asin"]])
    result = []
    for product in products:
        asin = product["asin"]
        values,stat = scores[asin],stats[asin]
        all_values = grouped[product["compare_group"]]
        prior = sum(all_values)/len(all_values) if all_values else None
        mean = sum(values)/len(values) if values else None
        adjusted = ((sum(values)+prior_strength*prior)/(len(values)+prior_strength)) if values and prior is not None else None
        offer = db.execute("""SELECT o.price_inr,r.started_at,r.metadata_json,r.engine FROM search_observations o
            JOIN collection_runs r ON r.run_id=o.run_id WHERE o.asin=? AND o.price_inr IS NOT NULL
            ORDER BY COALESCE(json_extract(r.metadata_json,'$.captured_at'),r.started_at) DESC,o.page,o.position LIMIT 1""",(asin,)).fetchone()
        price_at = None
        if offer:
            price_at = json.loads(offer["metadata_json"]).get("captured_at") or offer["started_at"]
        flags = ["selection_biased_sample","sentiment_baseline_requires_validation"]
        if len(values) < 20:
            flags.append("insufficient_evidence_for_recommendation")
        if not offer:
            flags.append("no_observed_price")
        if price_at:
            try:
                if (today-date.fromisoformat(price_at[:10])).days > 7:
                    flags.append("price_older_than_7_days")
            except ValueError:
                flags.append("price_date_unknown")
        result.append({"asin":asin,"name":product["name"],"compare_group":product["compare_group"],"period_start":cutoff,"period_end":today.isoformat(),"n_scored":len(values),"n_in_window":stat["n_in_window"],"n_verified":stat["n_verified"],"sentiment_score":round(mean,4) if mean is not None else None,"adjusted_sentiment":round(adjusted,4) if adjusted is not None else None,"negative_share":round(stat["n_negative"]/len(values),4) if values else None,"latest_price_inr":offer["price_inr"] if offer else None,"price_observed_at":price_at,"total_collected":stat["total_collected"],"excluded_pooled":stat["excluded_pooled"],"excluded_undated":stat["excluded_undated"],"excluded_outside_window":stat["excluded_outside_window"],"excluded_unscored":stat["excluded_unscored"],"excluded_not_verified":stat["excluded_not_verified"],"quality_flags":";".join(flags),"scorer_version":scorer_version})
    # An exploratory ordering within each group; this is never a best-buy verdict.
    result.sort(key=lambda row:(row["compare_group"],-(row["adjusted_sentiment"] if row["adjusted_sentiment"] is not None else -2),row["asin"]))
    output = Path(output)
    output.mkdir(parents=True,exist_ok=True)
    with (output/"comparison.csv").open("w",encoding="utf-8",newline="") as handle:
        writer = csv.DictWriter(handle,fieldnames=list(result[0]))
        writer.writeheader()
        writer.writerows(result)
    build_html(result,output/"report.html",verified_only,prior_strength,scorer_version)
    return {"products":len(result),"csv":str(output/"comparison.csv"),"report":str(output/"report.html"),"scorer_version":scorer_version}


def build_html(rows,path,verified_only,prior_strength,version):
    escape = lambda value: html.escape(str(value))
    flag_labels = {"selection_biased_sample":"Selected review sample", "sentiment_baseline_requires_validation":"Sentiment needs validation", "insufficient_evidence_for_recommendation":"Fewer than 20 scored reviews", "no_observed_price":"Price not captured", "price_older_than_7_days":"Price more than 7 days old", "price_date_unknown":"Price date unknown"}
    def time_label(value):
        if not value:
            return ""
        try:
            return datetime.fromisoformat(value.replace("Z","+00:00")).astimezone(ZoneInfo("Asia/Kolkata")).strftime("%d %b %Y, %H:%M IST")
        except ValueError:
            return value
    sections = []
    for group in dict.fromkeys(row["compare_group"] for row in rows):
        cards = []
        for row in rows:
            if row["compare_group"] != group:
                continue
            score = "—" if row["sentiment_score"] is None else f'{row["sentiment_score"]:+.2f}'
            adjusted = "—" if row["adjusted_sentiment"] is None else f'{row["adjusted_sentiment"]:+.2f}'
            price = "Not captured" if row["latest_price_inr"] is None else f'₹{row["latest_price_inr"]:,.2f}'
            flags = " · ".join(flag_labels.get(flag,flag.replace("_"," ")) for flag in row["quality_flags"].split(";"))
            cards.append(f'<tr><td><a href="https://www.amazon.in/dp/{escape(row["asin"])}" rel="noopener noreferrer">{escape(row["name"])}</a><small>{escape(row["asin"])}</small></td><td>{escape(price)}<small>{escape(time_label(row["price_observed_at"]))}</small></td><td>{row["n_scored"]}<small>{row["n_verified"]} with badge</small></td><td>{score}<small>adjusted {adjusted}</small></td><td>{escape(flags)}</td></tr>')
        sections.append(f'<section><h2>{escape(group)}</h2><div class="scroll"><table><thead><tr><th>Product</th><th>Observed price</th><th>Reviews scored</th><th>Text sentiment</th><th>Evidence limits</th></tr></thead><tbody>{"".join(cards)}</tbody></table></div></section>')
    document = f'''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Personal product research</title>
<style>body{{font:16px/1.5 system-ui;background:#f4f2ed;color:#182c2e;margin:0}}main{{max-width:1200px;margin:48px auto;padding:0 24px}}h1{{font-size:38px;letter-spacing:-1px;margin-bottom:8px}}.eyebrow{{color:#326d65;font-size:12px;font-weight:750;letter-spacing:2px}}.note,section{{background:white;padding:24px;border-radius:14px;margin:24px 0}}.note{{border-left:5px solid #b8832e}}.scroll{{overflow:auto}}table{{border-collapse:collapse;width:100%;text-align:left;font-size:14px}}td,th{{padding:16px 12px;border-bottom:1px solid #e2e7e5;vertical-align:top}}th{{color:#53736f}}td:first-child{{min-width:200px}}small{{display:block;color:#58706b;font-size:12px;margin-top:5px}}a{{color:#176659}}footer{{font-size:12px;color:#58706b}}</style>
<main><p class="eyebrow">PERSONAL RESEARCH / AMAZON.IN</p><h1>What the collected reviews say</h1><p>Review window: {escape(rows[0]["period_start"])} to {escape(rows[0]["period_end"])}. {"Verified-badge reviews only." if verified_only else "All collected reviews, including unknown verification."}</p>
<div class="note"><strong>Exploratory evidence, not an automatic best-buy verdict.</strong> Featured and captured reviews are a selected sample. Small samples, pooled variants, recent price changes and imperfect sentiment can change the ordering. Search rank does not measure sales. Check product specifications and warranty before recommending a purchase.</div>
{"".join(sections)}<footer>Generated {escape(now())}. English rule-based sentiment ranges from −1 to +1; it is not a probability or a star rating. Adjusted sentiment = (sum of product scores + {prior_strength} × group mean) / (product review count + {prior_strength}). No-review products remain unscored. Pooled review IDs, undated reviews and unscored languages are excluded from the ordering.<br>Scorer: {escape(version)}. Reviewer identities and full review text are omitted from this report.</footer></main></html>'''
    path.write_text(document,encoding="utf-8")
