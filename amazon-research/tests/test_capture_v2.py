"""Product-page capture tests. The capture below is SYNTHETIC, shaped like the browser extension's v2 export."""
import json
from amazon_research.cli import main
from amazon_research.collector import check_capture, import_capture
from amazon_research.parsers import parse_product_summary
from amazon_research.storage import connect

PRODUCT = {
    "title": "Example Breezo 1200 mm BLDC Ceiling Fan",
    "byline": "Visit the Breezo Store",
    "rating_text": "4.2 out of 5 stars",
    "ratings_count_text": "12,345 ratings",
    "histogram_text": ["5 star 61%", "4 stars represent 20% of rating 4 star 20%", "62 percent of reviews have 3 stars", "2 star 4%", "1 star 6%"],
    "price_text": "₹2,499.00",
    "mrp_text": "₹3,990.00",
    "bought_text": "1K+ bought in past month",
    "customers_say": "Customers like the airflow and the quiet motor; some mention remote problems.",
    "aspects": ["Airflow, 120 positive mentions", "Remote, 30 negative mentions"],
}
PRODUCT["fields_found"] = [k for k, v in PRODUCT.items() if v]


def capture(tmp_path, product=PRODUCT, kind="product"):
    data = {"format": "amazon-research-capture-v2", "kind": kind, "url": "https://www.amazon.in/dp/B0SYNTH001", "captured_at": "2026-11-07T10:00:00Z",
            "asin": "B0SYNTH001", "card_count": 0, "scope": "featured_nonrepresentative", "product": product, "html": "<!doctype html><html><body></body></html>"}
    path = tmp_path / "cap.json"
    path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    return path


def test_parse_product_summary():
    f = parse_product_summary(PRODUCT)
    assert f["rating"] == 4.2 and f["ratings_count"] == 12345
    assert f["histogram"] == {5: 61, 4: 20, 3: 62, 2: 4, 1: 6}
    assert f["price_inr"] == 2499.0 and f["mrp_inr"] == 3990.0
    assert f["bought_past_month_floor"] == 1000


def test_missing_facts_stay_unknown():
    f = parse_product_summary({"title": "x", "fields_found": ["title"]})
    assert f["rating"] is None and f["ratings_count"] is None and f["bought_past_month_floor"] is None and f["histogram"] is None


def test_product_page_without_reviews_is_saved(tmp_path):
    db = connect(tmp_path / "c.sqlite")
    res = import_capture(db, capture(tmp_path))
    assert res["status"] == "product_snapshot_saved"
    row = db.execute("SELECT * FROM product_snapshots").fetchone()
    assert row["asin"] == "B0SYNTH001" and row["ratings_count"] == 12345 and row["bought_past_month_floor"] == 1000
    assert json.loads(row["histogram_json"])["5"] == 61


def test_capture_check_names_missing_fields(tmp_path, capsys):
    thin = {"title": "x", "rating_text": "4.0 out of 5 stars", "fields_found": ["title", "rating_text"]}
    out = check_capture(capture(tmp_path, thin))
    assert "price_text" in out["product_fields_missing"] and out["parsed"]["rating"] == 4.0
    assert main(["capture-check", str(capture(tmp_path, thin))]) == 0
    assert "product_fields_missing" in capsys.readouterr().out
