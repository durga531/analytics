"""Keepa connector tests. All products, brands and numbers here are SYNTHETIC, shaped like Keepa's documented payloads."""
import csv
import json
import pytest
from amazon_research import keepa
from amazon_research.cli import main
from amazon_research.storage import connect

N = 7_000_000          # a fixed "now" in Keepa minutes
D = 1440               # minutes in a day
KEY = "SECRET-TEST-KEY-123"


def product(asin, brand, counts, ratings, ranks, price, rating_update_days_ago=5, monthly=None, parent=None):
    csv_arr = [None] * 18
    csv_arr[keepa.AMAZON] = price
    csv_arr[keepa.SALES] = ranks
    csv_arr[keepa.RATING] = ratings
    csv_arr[keepa.COUNT_REVIEWS] = counts
    p = {"asin": asin, "title": f"Example {brand} fan {asin[-2:]}", "brand": brand, "csv": csv_arr,
         "lastRatingUpdate": N - rating_update_days_ago * D if counts else None, "lastUpdate": N - D, "parentAsin": parent,
         "categoryTree": [{"catId": 1, "name": "Home"}, {"catId": 2, "name": "Ceiling Fans"}]}
    if monthly:
        p["monthlySold"], p["lastSoldUpdate"] = monthly, N - 2 * D
    return p


A = product("B0SYNTH001", "Breezo", [N - 200 * D, 1000, N - 80 * D, 1100, N - 10 * D, 1300], [N - 200 * D, 42, N - 10 * D, 43],
            [N - 100 * D, 500, N - 80 * D, 300, N - 60 * D, 400, N - 30 * D, 200], [N - 50 * D, 349900], monthly=1000)
B = product("B0SYNTH002", " breezo", [N - 300 * D, 50, N - 20 * D, 150], [N - 300 * D, 38], [N - 10 * D, 900], [N - 5 * D, 199900])
C = product("B0SYNTH003", "Windara", [N - 400 * D, 4000, N - 70 * D, 4100], [N - 400 * D, 45], [N - 400 * D, 50], [N - 9 * D, 459900],
            rating_update_days_ago=40)
E = product("B0SYNTH004", "Windara", None, None, None, [N - 9 * D, -1])


def test_summarize_window_drops_price_and_flags():
    s = keepa.summarize(A, 90, now_minutes=N)
    assert s["new_ratings_90d"] == 300          # 1300 now against 1000 in force 95 days before the rating update
    assert s["rating"] == 4.3 and s["rating_count"] == 1300
    assert s["rank_drops_90d"] == 2             # 500 to 300 and 400 to 200 inside the window
    assert s["amazon_price_inr"] == 3499.0
    assert s["monthly_sold_floor"] == 1000
    assert s["category_path"] == "Home > Ceiling Fans"
    assert s["flags"] == ""
    c = keepa.summarize(C, 90, now_minutes=N)
    assert "ratings_older_than_30_days" in c["flags"] and c["new_ratings_90d"] == 100
    e = keepa.summarize(E, 90, now_minutes=N)
    assert e["new_ratings_90d"] is None and "no_rating_history" in e["flags"] and e["amazon_price_inr"] is None


def test_short_history_uses_first_point_and_says_so():
    young = product("B0SYNTH005", "Breezo", [N - 30 * D, 10, N - 2 * D, 60], [N - 30 * D, 40], None, None)
    s = keepa.summarize(young, 90, now_minutes=N)
    assert s["new_ratings_90d"] == 50 and "rating_history_shorter_than_window" in s["flags"]


def fake_fetch(responses, calls):
    def fetch(url, params):
        calls.append((url, dict(params)))
        return responses.pop(0)
    return fetch


def test_out_of_tokens_waits_for_refill_then_retries():
    calls, slept = [], []
    responses = [(429, {"tokensLeft": -3, "refillIn": 1500, "error": {"message": "You are out of tokens."}}),
                 (200, {"tokensLeft": 10, "tokensConsumed": 1, "products": [A]})]
    client = keepa.KeepaClient(key=KEY, fetch=fake_fetch(responses, calls), sleep=slept.append)
    assert [p["asin"] for p in client.products(["B0SYNTH001"])] == ["B0SYNTH001"]
    assert len(calls) == 2 and slept == [2.5] and client.tokens_left == 10
    assert calls[0][1]["domain"] == keepa.DOMAIN_IN and calls[0][1]["rating"] == 1


def test_key_never_appears_in_errors():
    calls = []
    responses = [(400, {"tokensLeft": 5, "error": {"message": f"bad request for key={KEY}"}})]
    client = keepa.KeepaClient(key=KEY, fetch=fake_fetch(responses, calls))
    with pytest.raises(keepa.KeepaError) as err:
        client.categories("ceiling fan")
    assert KEY not in str(err.value) and "<key>" in str(err.value)


def test_missing_key_is_a_clear_setup_error(monkeypatch):
    monkeypatch.delenv("KEEPA_API_KEY", raising=False)
    with pytest.raises(ValueError, match="KEEPA_API_KEY"):
        keepa.KeepaClient()


def test_batches_of_twenty():
    calls = []
    asins = [f"B0SYNTH{i:03d}" for i in range(45)]
    responses = [(200, {"products": []}) for _ in range(3)]
    client = keepa.KeepaClient(key=KEY, fetch=fake_fetch(responses, calls))
    list(client.products(asins, batch=20))
    assert [len(c[1]["asin"].split(",")) for c in calls] == [20, 20, 5]


def test_bestsellers_store_rollup_and_report(tmp_path, monkeypatch):
    monkeypatch.setattr(keepa, "keepa_now", lambda epoch_seconds=None: N)
    db = connect(tmp_path / "k.sqlite")
    calls = []
    responses = [(200, {"tokensConsumed": 50, "bestSellersList": {"asinList": ["B0SYNTH001", "B0SYNTH003", "B0SYNTH002", "B0SYNTH004"], "lastUpdate": N - 60}}),
                 (200, {"tokensConsumed": 4, "tokensLeft": 100, "products": [A, C, B, E]})]
    client = keepa.KeepaClient(key=KEY, fetch=fake_fetch(responses, calls))
    res = keepa.cmd_bestsellers(db, client, "1234", "Ceiling fans (synthetic)", top=4)
    assert res["products"] == 4 and res["tokens_used"] == 54
    assert db.execute("SELECT COUNT(*) FROM keepa_series WHERE asin='B0SYNTH001' AND series='rating_count'").fetchone()[0] == 3
    run, rows = keepa.latest_rows(db, "Ceiling fans (synthetic)")
    assert [r["bestseller_rank"] for r in rows] == [1, 2, 3, 4]
    brands, total = keepa.brand_rollup(rows)
    assert total == 300 + 100 + 100
    assert [b["brand"] for b in brands] == ["Breezo", "Windara"]       # " breezo" folds into Breezo
    assert brands[0]["new_ratings_90d"] == 400 and brands[0]["share_of_new_ratings"] == 0.8
    assert abs(sum(b["share_of_new_ratings"] for b in brands) - 1) < 1e-9
    assert brands[1]["products_with_stale_ratings"] == 1
    # CLI report, no network
    out = tmp_path / "rep"
    db.close()
    assert main(["--db", str(tmp_path / "k.sqlite"), "keepa-brands", "--group", "Ceiling fans (synthetic)", "--out", str(out)]) == 0
    html = (out / "keepa_brands.html").read_text()
    assert "Breezo drew 80% of new ratings" in html and "Cannot say" in html and KEY not in html
    with (out / "keepa_brands.csv").open() as h:
        assert next(csv.DictReader(h))["brand"] == "Breezo"


def test_empty_bestseller_list_charges_nothing(tmp_path):
    db = connect(tmp_path / "k.sqlite")
    client = keepa.KeepaClient(key=KEY, fetch=fake_fetch([(200, {"tokensConsumed": 0})], []))
    assert keepa.cmd_bestsellers(db, client, "999", "Nothing")["status"] == "empty_list"


def test_cli_without_key_exits_cleanly(tmp_path, monkeypatch, capsys):
    monkeypatch.delenv("KEEPA_API_KEY", raising=False)
    assert main(["--db", str(tmp_path / "k.sqlite"), "keepa-categories", "ceiling fan"]) == 2
    assert "KEEPA_API_KEY" in capsys.readouterr().err
