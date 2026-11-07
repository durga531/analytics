"""Optional real-browser smoke test. Uses synthetic intercepted pages, no Amazon requests.

Run after installing Camoufox: python tests/browser_smoke.py
"""
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from amazon_research.collector import import_capture
from amazon_research.storage import connect,load_products
from amazon_research.transport import Transport

ROOT = Path(__file__).resolve().parents[1]
script = (ROOT/"browser_capture/popup.js").read_text().split("document.getElementById('capture')")[0]
with TemporaryDirectory() as temporary:
    temporary = Path(temporary)
    db = connect(temporary/"smoke.sqlite")
    try:
        load_products(db,ROOT/"examples/products.demo.csv")
        with Transport("camoufox",temporary/"profile",headless=True) as browser:
            for kind,path,url,expected in [
                ("search","search.html","https://www.amazon.in/s?k=fan&page=2",3),
                ("reviews","reviews.html","https://www.amazon.in/dp/B0DEMO0001",2)
            ]:
                # The hostname is needed to test the extension's marketplace
                # boundary. Interception fulfills locally; there is no request.
                fixture = (ROOT/"tests/fixtures"/path).read_text()
                browser.page.unroute("**/*")
                browser.page.route("**/*",lambda route,_request,body=fixture:route.fulfill(status=200,content_type="text/html",body=body))
                browser.page.goto(url)
                capture = browser.page.evaluate("() => {"+script+";return capturePage();}")
                assert capture["kind"] == kind
                assert capture["card_count"] == expected
                assert "cookie" not in capture
                capture_file = temporary/(kind+".json")
                capture_file.write_text(json.dumps(capture),encoding="utf-8")
                result = import_capture(db,capture_file,temporary/"search.csv" if kind == "search" else None)
                assert result["parsed"] == expected
                print(kind,"capture -> parser -> SQLite",result["parsed"],"rows: passed")
            report = ROOT/"demo_output/comparison/report.html"
            if report.exists():
                browser.page.unroute("**/*")
                browser.page.goto(report.resolve().as_uri())
                assert browser.page.locator("tbody tr").count() == 3
                assert "SYNTHETIC DEMO" in browser.page.locator("h1").inner_text()
                print("synthetic HTML report rendered: passed")
    finally:
        db.close()
