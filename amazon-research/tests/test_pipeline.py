import csv
import io
import json
from pathlib import Path
import pytest
from amazon_research import collector
from amazon_research.cli import main
from amazon_research.models import AccessProblem, SEARCH_FIELDS, Review, amazon_url, now
from amazon_research.parsers import check_access,count,parse_reviews,parse_search,posted_date
from amazon_research.report import compare
from amazon_research.sentiment import score_reviews
from amazon_research.storage import connect,load_products,start_run,upsert_reviews,write_search_page

FIXTURES = Path(__file__).parent/"fixtures"
ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def db(tmp_path):
    connection = connect(tmp_path/"test.sqlite")
    load_products(connection,ROOT/"examples/products.demo.csv")
    yield connection
    connection.close()


def test_card_fields_price_count_and_nonunique_asin():
    rows = parse_search((FIXTURES/"search.html").read_text(),page=2,brands=["Example Air"])
    assert len(rows) == 3
    assert rows[0].asin == rows[2].asin
    assert rows[0].brand_guess == "Example Air"
    assert rows[0].price_inr == 3499.5
    assert rows[0].discount_pct == 30.01
    assert rows[0].review_count == 1234
    assert rows[0].rating == 4.2
    assert rows[0].sponsored is True
    assert rows[1].price_inr == 2999
    assert rows[1].mrp_inr == 1
    assert rows[1].discount_pct is None
    assert rows[1].sponsored is None
    assert rows[2].page == 2 and rows[2].position == 3


def test_review_parse():
    rows = parse_reviews((FIXTURES/"reviews.html").read_text(),"B0DEMO0001")
    assert len(rows) == 2
    assert rows[0].title == "Quiet and efficient"
    assert rows[0].review_date == "2026-11-01"
    assert rows[0].helpful_votes == 1
    assert rows[1].helpful_votes == 23
    assert rows[0].verified == 1
    assert rows[1].verified is None
    assert rows[0].country == "India"
    assert rows[0].variant == "Colour: White | Size: 1200mm"
    assert not rows[0].body.endswith("Read more")
    assert rows[1].rating == 2


@pytest.mark.parametrize("status,label",[(401,"login_required"),(403,"access_denied"),(429,"rate_limited"),(503,"service_unavailable")])
def test_http_denials(status,label):
    with pytest.raises(AccessProblem) as caught:
        check_access("<html/>",status=status)
    assert caught.value.status == label


@pytest.mark.parametrize("html,label",[
    ('<title>Robot Check</title>',"captcha"),
    ('<form name="signIn"><input id="ap_email"></form>',"login_required"),
    ('<input id="auth-mfa-otpcode">',"mfa_required"),
    ('We limit review access when we detect unusual activity',"review_access_restricted")
])
def test_access_pages_not_success(html,label):
    with pytest.raises(AccessProblem) as caught:
        check_access(html)
    assert caught.value.status == label


def test_silent_empty_not_allowed():
    with pytest.raises(AccessProblem,match="No product cards"):
        parse_search("<html><body>Unexpected markup</body></html>")
    assert parse_search("<h1>No results for unknownquery</h1>") == []


@pytest.mark.parametrize("url",["https://evil.example/path","https://www.amazon.in.evil.example/","https://amazon.in@evil.example/","http://amazon.in/","https://amazon.in:444/"])
def test_url_boundary(url):
    with pytest.raises(ValueError):
        amazon_url(url)


def test_dates_and_counts():
    assert posted_date("Reviewed in the United States on October 21, 2026") == "2026-10-21"
    assert posted_date("unparseable") is None
    assert count("1.2K ratings") == 1200
    assert count("1,23,456 ratings") == 123456
    assert count("One person found this helpful") == 1


def test_search_csv_exact_order_streaming_preserves_repeated_asin(db):
    run = start_run(db,"search","test","fixture")
    rows = parse_search((FIXTURES/"search.html").read_text())
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer,fieldnames=SEARCH_FIELDS)
    writer.writeheader()
    write_search_page(db,run,rows,buffer,writer)
    assert list(csv.DictReader(io.StringIO(buffer.getvalue())).fieldnames) == SEARCH_FIELDS
    assert db.execute("SELECT COUNT(*) FROM search_observations WHERE asin='B0DEMO0001'").fetchone()[0] == 2


def seed_reviews(db):
    run = start_run(db,"reviews","test","fixture")
    rows = parse_reviews((FIXTURES/"reviews.html").read_text(),"B0DEMO0001")
    return run,rows,upsert_reviews(db,run,rows,"https://www.amazon.in/dp/B0DEMO0001","featured")


def test_cumulative_dedup_and_short_preview_does_not_destroy_body(db):
    run,rows,added = seed_reviews(db)
    assert added == 2
    assert upsert_reviews(db,run,rows,"https://www.amazon.in/dp/B0DEMO0001","featured") == 0
    original = rows[0].body
    rows[0].body = "The fan"
    upsert_reviews(db,run,rows[:1],"https://www.amazon.in/dp/B0DEMO0001","featured")
    assert db.execute("SELECT body FROM reviews WHERE review_id=?",(rows[0].review_id,)).fetchone()[0] == original


def test_pooled_reviews_preserved_as_links_and_excluded_from_comparison(db,tmp_path):
    run,rows,_ = seed_reviews(db)
    rows[0].asin = "B0DEMO0002"
    upsert_reviews(db,run,rows[:1],"https://www.amazon.in/dp/B0DEMO0002","featured")
    assert db.execute("SELECT COUNT(*) FROM reviews").fetchone()[0] == 2
    assert db.execute("SELECT COUNT(DISTINCT asin) FROM review_observations WHERE review_id=?",(rows[0].review_id,)).fetchone()[0] == 2
    score_reviews(db,language="en")
    compare(db,tmp_path/"report",as_of="2026-11-07")
    values = list(csv.DictReader((tmp_path/"report/comparison.csv").open()))
    product = next(row for row in values if row["asin"] == "B0DEMO0001")
    assert product["n_scored"] == "1"
    assert product["excluded_pooled"] == "1"


def test_body_sentiment_aspects_and_language_flags(db):
    seed_reviews(db)
    collector.import_reviews(db,ROOT/"examples/reviews.demo.jsonl")
    result = score_reviews(db)
    assert result["processed"] == 6
    assert result["empty_body"] == 1
    assert result["needs_language_review"] >= 1
    result = score_reviews(db,language="en")
    mixed = db.execute("SELECT aspect,sentiment_score FROM review_aspects WHERE review_id='DEMO_REVIEW_2' AND scorer_version=?",(result["scorer_version"],)).fetchall()
    aspect_scores = dict(mixed)
    assert aspect_scores["airflow"] > 0
    assert aspect_scores["build_quality"] < 0
    assert aspect_scores["service_warranty"] < 0
    positive = db.execute("SELECT sentiment_score FROM review_sentiment WHERE review_id='DEMO_REVIEW_1' AND scorer_version=?",(result["scorer_version"],)).fetchone()[0]
    assert positive > 0


def test_updated_full_body_invalidates_old_scores(db):
    run,rows,_ = seed_reviews(db)
    score_reviews(db,language="en")
    assert db.execute("SELECT COUNT(*) FROM review_sentiment WHERE review_id='DEMO_REVIEW_1'").fetchone()[0] == 1
    rows[0].body += " This additional sentence is part of an updated full review."
    upsert_reviews(db,run,rows[:1],"https://www.amazon.in/dp/B0DEMO0001","review_page")
    assert db.execute("SELECT COUNT(*) FROM review_sentiment WHERE review_id='DEMO_REVIEW_1'").fetchone()[0] == 0
    assert db.execute("SELECT COUNT(*) FROM review_aspects WHERE review_id='DEMO_REVIEW_1'").fetchone()[0] == 0


class FixtureTransport:
    engine = "test"
    def __init__(self,html=None,error=None):
        self.html,self.error,self.calls = html,error,0
    def fetch(self,url,kind=None):
        self.calls += 1
        if self.error:
            raise self.error
        return self.html,200,url


def test_repeated_review_page_stops_without_duplicate_votes(db):
    transport = FixtureTransport((FIXTURES/"reviews.html").read_text())
    with pytest.raises(AccessProblem) as caught:
        collector.reviews(db,transport,"B0DEMO0001",pages=4,mode="pages")
    assert caught.value.status == "repeated_review_page"
    assert transport.calls == 2
    assert db.execute("SELECT COUNT(*) FROM reviews").fetchone()[0] == 2
    assert db.execute("SELECT status FROM collection_runs ORDER BY rowid DESC LIMIT 1").fetchone()[0] == "repeated_review_page"


def test_repeated_search_page_stops_without_fake_pagination(db,tmp_path):
    transport = FixtureTransport((FIXTURES/"search.html").read_text())
    with pytest.raises(AccessProblem) as caught:
        collector.search(db,transport,"fans",tmp_path/"repeated.csv",pages=4)
    assert caught.value.status == "repeated_search_page"
    assert transport.calls == 2
    assert db.execute("SELECT COUNT(*) FROM search_observations").fetchone()[0] == 3


def test_full_review_edit_can_replace_with_shorter_text(db):
    run,rows,_ = seed_reviews(db)
    rows[0].body = "It broke."
    upsert_reviews(db,run,rows[:1],"https://www.amazon.in/product-reviews/B0DEMO0001","review_page")
    assert db.execute("SELECT body FROM reviews WHERE review_id=?",(rows[0].review_id,)).fetchone()[0] == "It broke."


def test_blocked_search_persists_diagnostic_and_failed_sidecar(db,tmp_path):
    transport = FixtureTransport(error=AccessProblem("service_unavailable","HTTP 503",503))
    target = tmp_path/"blocked.csv"
    with pytest.raises(AccessProblem):
        collector.search(db,transport,"fans",target,pages=3)
    assert transport.calls == 1
    assert json.loads(Path(str(target)+".meta.json").read_text())["status"] == "service_unavailable"
    assert db.execute("SELECT outcome FROM fetches ORDER BY fetch_id DESC LIMIT 1").fetchone()[0] == "service_unavailable"


def test_capture_import_preserves_collection_time(db,tmp_path):
    capture = {"format":"amazon-research-capture-v1","kind":"search","url":"https://www.amazon.in/s?k=fan&page=2","captured_at":"2026-10-31T12:00:00Z","html":(FIXTURES/"search.html").read_text()}
    file = tmp_path/"capture.json"
    file.write_text(json.dumps(capture))
    out = tmp_path/"captured.csv"
    result = collector.import_capture(db,file,out)
    meta = json.loads(Path(str(out)+".meta.json").read_text())
    assert meta["captured_at"] == "2026-10-31T12:00:00Z"
    assert db.execute("SELECT page FROM search_observations WHERE run_id=?",(result["run_id"],)).fetchone()[0] == 2


def test_empty_product_not_given_a_recommendation(db,tmp_path):
    seed_reviews(db)
    score_reviews(db,language="en")
    compare(db,tmp_path/"output",as_of="2026-11-07")
    rows = list(csv.DictReader((tmp_path/"output/comparison.csv").open()))
    no_reviews = next(row for row in rows if row["asin"] == "B0DEMO0003")
    assert no_reviews["sentiment_score"] == ""
    assert no_reviews["adjusted_sentiment"] == ""
    assert "insufficient_evidence" in no_reviews["quality_flags"]


def test_bad_product_file_is_atomic(db,tmp_path):
    bad = tmp_path/"bad.csv"
    bad.write_text("asin,name,category,compare_group\nB0DEMO0004,Good,Fans,Group\nBAD,Bad,Fans,Group\n")
    with pytest.raises(ValueError):
        load_products(db,bad)
    assert not db.execute("SELECT 1 FROM products WHERE asin='B0DEMO0004'").fetchone()


def test_cli_returns_nonzero_for_invalid_input(tmp_path,capsys):
    assert main(["--db",str(tmp_path/"empty.sqlite"),"compare"]) == 2
    assert '"status": "error"' in capsys.readouterr().err
