import argparse
import importlib.metadata
import importlib.util
import json
from pathlib import Path
import sqlite3
import sys
from .models import AccessProblem
from .keepa import KeepaError
from .storage import connect, export_all, load_products


def page_limit(value):
    value = int(value)
    if not 1 <= value <= 20:
        raise argparse.ArgumentTypeError("pages must be between 1 and 20")
    return value


def add_transport(parser,session=False):
    parser.add_argument("--engine",choices=["chromium","camoufox"] if session else ["http","chromium","camoufox"],default="chromium" if session else "http")
    parser.add_argument("--profile",default="profiles/amazon-research",help="Dedicated local browser profile; never use your everyday browser profile")
    parser.add_argument("--delay",type=float,default=8,help="Seconds between pages; default 8, minimum 3")
    if not session:
        parser.add_argument("--headless",action="store_true",help="Run a prepared browser session without a visible window")


def parser():
    root = argparse.ArgumentParser(description="Amazon.in personal research: collection, diagnostics, sentiment and comparisons")
    root.add_argument("--db",default="data/research.sqlite",help="SQLite path (place this option before the subcommand)")
    sub = root.add_subparsers(dest="command",required=True)
    p = sub.add_parser("init",help="Initialize database and load a curated products.csv")
    p.add_argument("--products",required=True)
    p = sub.add_parser("search",help="Collect a timestamped search-listing snapshot")
    p.add_argument("query")
    p.add_argument("--out",required=True)
    p.add_argument("--pages",type=page_limit,default=1)
    p.add_argument("--location-note",help="Delivery pincode/location context; does not change Amazon's location setting")
    p.add_argument("--brands",help="JSON array of known multiword brands")
    add_transport(p)
    p = sub.add_parser("reviews",help="Collect featured reviews or accessible review pagination")
    p.add_argument("--asin",help="One curated ASIN; default all curated products")
    p.add_argument("--mode",choices=["featured","pages"],default="featured")
    p.add_argument("--pages",type=page_limit,default=3)
    add_transport(p)
    p = sub.add_parser("session",help="Prepare your own session with manual sign-in in a dedicated visible browser")
    add_transport(p,session=True)
    p = sub.add_parser("import-html",help="Parse a page you saved yourself")
    p.add_argument("path")
    p.add_argument("--kind",choices=["search","reviews"],required=True)
    p.add_argument("--asin")
    p.add_argument("--out")
    p.add_argument("--url")
    p.add_argument("--page",type=page_limit,default=1)
    p = sub.add_parser("import-capture",help="Import a one-page export from the supplied browser capture extension")
    p.add_argument("path")
    p.add_argument("--out",help="Required for a search capture")
    p = sub.add_parser("capture-check",help="Show which product facts and cards a capture file holds; no database")
    p.add_argument("path")
    p = sub.add_parser("import-reviews",help="Import normalized review CSV or JSONL")
    p.add_argument("path")
    p = sub.add_parser("score",help="Compute local body-text sentiment and aspect tags")
    p.add_argument("--aspects",help="JSON mapping of aspect names to regex lists")
    p.add_argument("--language",choices=["auto","en"],default="auto",help="auto skips texts not confidently detected as English; en is an explicit operator override")
    p = sub.add_parser("export",help="Export corpus, audit logs and sentiment CSVs")
    p.add_argument("--out",default="data/export")
    p = sub.add_parser("compare",help="Create an evidence table and a shareable HTML report")
    p.add_argument("--out",default="data/comparison")
    p.add_argument("--group")
    p.add_argument("--days",type=int,default=180)
    p.add_argument("--as-of",help="YYYY-MM-DD; default today's India date")
    p.add_argument("--verified-only",action="store_true")
    p.add_argument("--prior-strength",type=float,default=20)
    p.add_argument("--scorer-version")
    sub.add_parser("doctor",help="Inspect installed dependencies and database counts; no network")
    # Keepa: licensed Amazon.in data (paid key in the KEEPA_API_KEY environment variable)
    p = sub.add_parser("keepa-categories",help="Find Amazon.in category IDs by name (Keepa; 1 token)")
    p.add_argument("term")
    add_keepa(p)
    p = sub.add_parser("keepa-bestsellers",help="Fetch a category's best sellers with ratings, rank and price history (Keepa; 50 tokens + about 2 per product)")
    p.add_argument("category",help="Category ID from keepa-categories")
    p.add_argument("--group",required=True,help="Your label for this comparison, e.g. 'Ceiling fans'")
    p.add_argument("--top",type=int,default=100)
    p.add_argument("--range",type=int,choices=[0,30,90,180],default=90,help="Rank list by current rank (0) or a 30/90/180-day average")
    add_keepa(p,fetch=True)
    p = sub.add_parser("keepa-products",help="Fetch chosen ASINs, or every ASIN in products.csv (Keepa; about 2 tokens per product)")
    p.add_argument("--asins",help="Comma-separated ASINs; default: all products in the database")
    p.add_argument("--group",required=True)
    add_keepa(p,fetch=True)
    p = sub.add_parser("keepa-brands",help="Brand table and HTML report from the latest Keepa run of a group; no network")
    p.add_argument("--group",required=True)
    p.add_argument("--window",type=int,choices=[30,90,180,365],default=90)
    p.add_argument("--out",default="data/keepa")
    return root


def add_keepa(parser,fetch=False):
    parser.add_argument("--key-env",default="KEEPA_API_KEY",help="Environment variable that holds your Keepa key")
    if fetch:
        parser.add_argument("--window",type=int,choices=[30,90,180,365],default=90,help="Days for new ratings and rank drops")
        parser.add_argument("--batch",type=int,default=20,help="ASINs per request; 20 suits the entry plan's 20 tokens a minute")
        parser.add_argument("--refresh-ratings",action="store_true",help="Ask Keepa to re-read ratings from Amazon now; about 6 tokens a product")


def main(argv=None):
    args = parser().parse_args(argv)
    db = None
    try:
        if args.command == "capture-check":
            from .collector import check_capture
            print(json.dumps(check_capture(args.path),indent=2,ensure_ascii=False))
            return 0
        if args.command == "session":
            from .transport import Transport
            with Transport(args.engine,args.profile,args.delay) as transport:
                transport.prepare_session()
            result = {"status":"session_saved","profile":args.profile}
        else:
            db = connect(args.db)
            if args.command == "init":
                result = {"products_loaded":load_products(db,args.products),"db":args.db}
            elif args.command in {"search","reviews"}:
                from . import collector
                from .transport import Transport
                with Transport(args.engine,args.profile,args.delay,args.headless) as transport:
                    if args.command == "search":
                        brands = json.loads(Path(args.brands).read_text()) if args.brands else None
                        result = collector.search(db,transport,args.query,args.out,args.pages,args.location_note,brands)
                    else:
                        result = collector.reviews(db,transport,args.asin,args.pages,args.mode)
            elif args.command == "import-html":
                from .collector import import_html
                result = import_html(db,args.path,args.kind,args.out,args.asin,args.url,args.page)
            elif args.command == "import-capture":
                from .collector import import_capture
                result = import_capture(db,args.path,args.out)
            elif args.command == "import-reviews":
                from .collector import import_reviews
                result = import_reviews(db,args.path)
            elif args.command == "score":
                from .sentiment import score_reviews
                result = score_reviews(db,args.aspects,args.language)
            elif args.command == "export":
                result = {"files":export_all(db,args.out)}
            elif args.command.startswith("keepa-"):
                from . import keepa
                if args.command == "keepa-brands":
                    result = keepa.cmd_brands(db,args.group,args.out,args.window)
                else:
                    client = keepa.KeepaClient(key_env=args.key_env)
                    if args.command == "keepa-categories":
                        result = keepa.cmd_categories(args.term,client)
                    elif args.command == "keepa-bestsellers":
                        result = keepa.cmd_bestsellers(db,client,args.category,args.group,args.top,args.range,args.window,args.batch,args.refresh_ratings)
                    else:
                        asins = [a for a in (args.asins or "").split(",") if a.strip()] or [r[0] for r in db.execute("SELECT asin FROM products ORDER BY asin")]
                        if not asins:
                            raise ValueError("No ASINs: pass --asins or load products.csv with init first")
                        result = keepa.cmd_products(db,client,asins,args.group,args.window,args.batch,args.refresh_ratings)
            elif args.command == "compare":
                from .report import compare
                result = compare(db,args.out,args.group,args.days,args.as_of,args.verified_only,args.prior_strength,args.scorer_version)
            else:
                packages = {}
                for name in ["beautifulsoup4","httpx","vaderSentiment","langdetect","playwright","camoufox"]:
                    try:
                        packages[name] = importlib.metadata.version(name)
                    except importlib.metadata.PackageNotFoundError:
                        packages[name] = "not installed"
                result = {"packages":packages,"counts":{table:db.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0] for table in ["products","reviews","search_observations","review_sentiment","fetches"]}}
        print(json.dumps(result,indent=2,ensure_ascii=False))
        return 0
    except KeepaError as exc:
        print(json.dumps({"status":"keepa_error","error":str(exc),"http_status":exc.http_status,"tokens_left":exc.tokens_left},ensure_ascii=False),file=sys.stderr)
        return 3
    except AccessProblem as exc:
        print(json.dumps({"status":exc.status,"error":str(exc),"http_status":exc.http_status,"next_step":"Inspect the access log; use your own browser's page capture or an accessible saved page."},ensure_ascii=False),file=sys.stderr)
        return 3
    except KeyboardInterrupt:
        print("Interrupted; committed rows remain saved.",file=sys.stderr)
        return 130
    except (ValueError,KeyError,OSError,sqlite3.Error,ImportError) as exc:
        print(json.dumps({"status":"error","error":str(exc)},ensure_ascii=False),file=sys.stderr)
        return 2
    finally:
        if db is not None:
            db.close()


if __name__ == "__main__":
    raise SystemExit(main())
