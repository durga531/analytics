"""End-to-end demo using invented data only. Does not contact Amazon."""
from pathlib import Path
import json
from amazon_research.collector import import_html, import_reviews
from amazon_research.report import compare
from amazon_research.sentiment import score_reviews
from amazon_research.storage import connect, export_all, load_products

root = Path(__file__).resolve().parent
output = root/"demo_output"
output.mkdir(exist_ok=True)
database = output/"demo.sqlite"
if database.exists():
    raise SystemExit("demo_output/demo.sqlite exists; choose another folder or remove the old demo before rerunning")
db = connect(database)
try:
    load_products(db,root/"examples/products.demo.csv")
    import_html(db,root/"tests/fixtures/search.html","search",output/"search.csv",url="https://www.amazon.in/s?k=SYNTHETIC+DEMO")
    import_html(db,root/"tests/fixtures/reviews.html","reviews",asin="B0DEMO0001")
    import_reviews(db,root/"examples/reviews.demo.jsonl")
    print(json.dumps(score_reviews(db),indent=2))
    export_all(db,output/"csv")
    print(json.dumps(compare(db,output/"comparison",as_of="2026-11-07"),indent=2))
    report = output/"comparison/report.html"
    report.write_text(report.read_text().replace("What the collected reviews say","SYNTHETIC DEMO — invented products and reviews"),encoding="utf-8")
    db.execute("PRAGMA wal_checkpoint(TRUNCATE)")
finally:
    db.close()
print("SYNTHETIC DEMO ONLY: no real product recommendation or live Amazon data.")
