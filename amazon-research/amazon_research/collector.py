import csv
import json
from pathlib import Path
import re
from urllib.parse import urlencode
from .models import AccessProblem, SEARCH_FIELDS, Review, amazon_url, now, valid_asin
from .parsers import check_access, next_page, page_number, parse_reviews, parse_search
from .storage import digest, finish_run, record_fetch, start_run, upsert_reviews, write_search_page


def search(db, transport, query, output, pages=1, location_note=None, brands=None):
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists() or output.with_suffix(output.suffix + ".meta.json").exists():
        raise ValueError(f"Output already exists: {output}; choose a new snapshot filename")
    run_id = start_run(db,"search",transport.engine,"search_listing",query,location_note=location_note,requested_pages=pages)
    metadata = {"run_id":run_id,"captured_at":now(),"query":query,"marketplace":"amazon.in","currency":"INR","location_note":location_note,"csv":str(output),"status":"running","rows":0,"warnings":["Rank indicates search visibility, not units sold.","MRP and sponsored detection can be incomplete."]}
    status = "completed"
    signatures = set()
    try:
        with output.open("x", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=SEARCH_FIELDS)
            writer.writeheader()
            handle.flush()
            for page in range(1,pages+1):
                url = "https://www.amazon.in/s?" + urlencode({"k":query,"page":page})
                html = None
                http_status = None
                try:
                    html,http_status,final_url = transport.fetch(url,"search")
                    rows = parse_search(html,page,brands)
                    signature = tuple(row.asin for row in rows)
                    if rows and signature in signatures:
                        raise AccessProblem("repeated_search_page", "Search pagination returned the identical product sequence. Run stopped.")
                    signatures.add(signature)
                    write_search_page(db,run_id,rows,handle,writer)
                    metadata["rows"] += len(rows)
                    record_fetch(db,run_id,final_url,"search",http_status,"ok" if rows else "no_results",len(rows),len(rows),html)
                    if not rows:
                        break
                except AccessProblem as exc:
                    record_fetch(db,run_id,url,"search",exc.http_status or http_status,exc.status,html=html,error=str(exc))
                    raise
    except BaseException as exc:
        status = exc.status if isinstance(exc,AccessProblem) else "interrupted" if isinstance(exc,KeyboardInterrupt) else "error"
        metadata["error"] = str(exc)
        raise
    finally:
        metadata.update(status=status,finished_at=now())
        output.with_suffix(output.suffix + ".meta.json").write_text(json.dumps(metadata,indent=2,ensure_ascii=False),encoding="utf-8")
        finish_run(db,run_id,status)
    return metadata


def reviews(db, transport, asin=None, pages=3, mode="featured"):
    products = db.execute("SELECT * FROM products" + (" WHERE asin=?" if asin else ""),(valid_asin(asin),) if asin else ()).fetchall()
    if not products:
        raise ValueError("No matching curated products. Import products.csv first.")
    scope = "featured_nonrepresentative" if mode == "featured" else "review_pages_nonexhaustive"
    run_id = start_run(db,"reviews",transport.engine,scope,requested_pages=pages,products=len(products),sort="recent" if mode != "featured" else None)
    status,parsed,inserted = "completed",0,0
    try:
        for product in products:
            url = f'https://www.amazon.in/dp/{product["asin"]}' if mode == "featured" else f'https://www.amazon.in/product-reviews/{product["asin"]}/?sortBy=recent&pageNumber=1'
            seen_sets,visited = set(),set()
            for _ in range(1 if mode == "featured" else pages):
                if url in visited:
                    raise AccessProblem("pagination_loop", "The next-page link points to an already visited URL")
                visited.add(url)
                html,http_status = None,None
                try:
                    html,http_status,final_url = transport.fetch(url,"reviews")
                    rows = parse_reviews(html,product["asin"],product["name"])
                    if not rows:
                        check_access(html,final_url,http_status)
                        if re.search(r"no customer reviews|no reviews yet|no customer review",html,re.I):
                            outcome = "no_reviews"
                        else:
                            raise AccessProblem("parse_empty", "No review cards found: possible changed markup, incomplete load, or missing review access.")
                    else:
                        outcome = "ok"
                        signature = tuple(sorted(r.review_id for r in rows))
                        if signature in seen_sets:
                            raise AccessProblem("repeated_review_page", "Pagination returned the same review IDs. Run stopped without duplicating rows.")
                        seen_sets.add(signature)
                    added = upsert_reviews(db,run_id,rows,final_url,"featured" if mode == "featured" else "review_page")
                    parsed += len(rows)
                    inserted += added
                    record_fetch(db,run_id,final_url,"reviews",http_status,outcome,len(rows),added,html)
                    if mode == "featured" or not rows:
                        break
                    following = next_page(html)
                    if not following:
                        break
                    # Follow only this product's review pagination.
                    if f'/product-reviews/{product["asin"]}' not in following:
                        raise AccessProblem("unexpected_next_link", "Next link is outside this product's reviews")
                    url = following
                except AccessProblem as exc:
                    record_fetch(db,run_id,url,"reviews",exc.http_status or http_status,exc.status,html=html,error=str(exc))
                    raise
    except BaseException as exc:
        status = exc.status if isinstance(exc,AccessProblem) else "interrupted" if isinstance(exc,KeyboardInterrupt) else "error"
        raise
    finally:
        finish_run(db,run_id,status)
    return {"run_id":run_id,"parsed":parsed,"inserted":inserted,"status":status,"scope":scope}


def import_html(db,path,kind,output=None,asin=None,url=None,page=1,brands=None):
    html = Path(path).read_text(encoding="utf-8-sig")
    url = amazon_url(url or (f"https://www.amazon.in/dp/{valid_asin(asin)}" if asin else "https://www.amazon.in/"))
    check_access(html,url)
    run_id = start_run(db,kind,"saved_html","manual_page_sample",source_file=Path(path).name)
    status = "completed"
    try:
        if kind == "search":
            if not output:
                raise ValueError("--out is required for search HTML")
            if Path(output).exists():
                raise ValueError("Choose a new --out path; existing snapshots are never overwritten")
            rows = parse_search(html,page,brands)
            Path(output).parent.mkdir(parents=True,exist_ok=True)
            with open(output,"x",newline="",encoding="utf-8") as handle:
                writer = csv.DictWriter(handle,fieldnames=SEARCH_FIELDS)
                writer.writeheader()
                write_search_page(db,run_id,rows,handle,writer)
            Path(str(output)+".meta.json").write_text(json.dumps({"run_id":run_id,"captured_at":now(),"source_url":url,"status":"completed","source":"saved_html","rows":len(rows)},indent=2),encoding="utf-8")
            added = len(rows)
        else:
            asin = valid_asin(asin)
            product = db.execute("SELECT name FROM products WHERE asin=?",(asin,)).fetchone()
            if not product:
                raise ValueError(f"ASIN {asin} is not in products.csv")
            rows = parse_reviews(html,asin,product["name"])
            if not rows:
                raise AccessProblem("parse_empty","Saved page contains no supported review cards")
            added = upsert_reviews(db,run_id,rows,url,"manual_capture")
        record_fetch(db,run_id,url,kind,None,"ok",len(rows),added,html)
        return {"run_id":run_id,"parsed":len(rows),"inserted":added,"status":"completed"}
    except BaseException as exc:
        status = exc.status if isinstance(exc,AccessProblem) else "error"
        record_fetch(db,run_id,url,kind,None,status,error=str(exc))
        raise
    finally:
        finish_run(db,run_id,status)


def import_capture(db,path,output=None,brands=None):
    from tempfile import TemporaryDirectory
    capture = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    if capture.get("format") not in {"amazon-research-capture-v1","amazon-research-capture-v2"} or capture.get("kind") not in {"search","reviews","product"}:
        raise ValueError("Unsupported capture format; use the supplied browser extension")
    url = amazon_url(capture["url"])
    captured_at = capture.get("captured_at")
    if not captured_at:
        raise ValueError("Capture has no captured_at timestamp")
    snapshot = store_product_snapshot(db,capture,url,captured_at) if capture.get("product") else None
    if capture["kind"] == "product":
        return {"status":"product_snapshot_saved","asin":capture.get("asin"),"snapshot":snapshot}
    with TemporaryDirectory() as temporary:
        target = Path(temporary)/"capture.html"
        target.write_text(capture["html"],encoding="utf-8")
        result = import_html(db,target,capture["kind"],output,capture.get("asin"),url,page_number(url),brands)
    with db:
        db.execute("UPDATE collection_runs SET engine='browser_capture',source_scope=?,metadata_json=? WHERE run_id=?", (capture.get("scope") or "manual_page_sample",json.dumps({"captured_at":captured_at,"imported_at":now(),"source_file":Path(path).name,"query":capture.get("query"),"location_note":capture.get("location_note")}),result["run_id"]))
    if snapshot:
        result["product_snapshot"] = snapshot
    if output and capture["kind"] == "search":
        sidecar = Path(str(output)+".meta.json")
        value = json.loads(sidecar.read_text())
        value.update(captured_at=captured_at,imported_at=now(),source="browser_capture",query=capture.get("query"))
        sidecar.write_text(json.dumps(value,indent=2),encoding="utf-8")
    return result


def import_reviews(db,path):
    """Import normalized CSV or JSONL without any vendor/API credentials."""
    path = Path(path)
    handle = path.open(encoding="utf-8-sig",newline="")
    run_id = start_run(db,"reviews","file_import","imported_sample",source_file=path.name)
    added,total,status = 0,0,"completed"
    try:
        with handle:
            values = (json.loads(line) for line in handle if line.strip()) if path.suffix.lower() in {".jsonl",".ndjson"} else csv.DictReader(handle)
            for row in values:
                asin = valid_asin(row["asin"])
                if not db.execute("SELECT 1 FROM products WHERE asin=?",(asin,)).fetchone():
                    raise ValueError(f"Unknown ASIN {asin}; load products.csv first")
                if not str(row.get("review_id","")).strip():
                    raise ValueError("review_id is required; never synthesize an Amazon ID")
                rating = float(row["rating"]) if row.get("rating") not in {None,""} else None
                if rating is not None and not 0 <= rating <= 5:
                    raise ValueError("Review rating must be between 0 and 5")
                verified = row.get("verified")
                if str(verified).lower() not in {"0","1","true","false","none",""}:
                    raise ValueError("verified must be 0, 1, or blank")
                verified = None if verified in {None,""} else int(str(verified).lower() in {"1","true"})
                review_date = row.get("review_date") or None
                if review_date:
                    from datetime import date
                    date.fromisoformat(review_date)
                product_name = row.get("product_name") or db.execute("SELECT name FROM products WHERE asin=?",(asin,)).fetchone()[0]
                helpful = int(row["helpful_votes"]) if row.get("helpful_votes") not in {None,""} else None
                if helpful is not None and helpful < 0:
                    raise ValueError("helpful_votes must be nonnegative")
                review = Review(str(row["review_id"]),asin,product_name,rating,row.get("title") or "",row.get("body") or "",row.get("author") or "",review_date,verified,helpful,row.get("scraped_at") or now())
                added += upsert_reviews(db,run_id,[review],f"https://www.amazon.in/dp/{asin}","imported")
                total += 1
        record_fetch(db,run_id,"local:"+path.name,"import",None,"ok",total,added)
        return {"run_id":run_id,"parsed":total,"inserted":added,"status":status}
    except BaseException as exc:
        status = "error"
        record_fetch(db,run_id,"local:"+path.name,"import",None,"error",total,added,error=str(exc))
        raise
    finally:
        finish_run(db,run_id,status)


def store_product_snapshot(db,capture,url,captured_at):
    from .parsers import parse_product_summary
    asin = valid_asin(capture["asin"])
    facts = parse_product_summary(capture["product"])
    with db:
        db.execute("""INSERT OR REPLACE INTO product_snapshots VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (asin,captured_at,url,facts["title"],facts["byline"],facts["rating"],facts["ratings_count"],
             json.dumps(facts["histogram"]) if facts["histogram"] else None,facts["price_inr"],facts["mrp_inr"],
             facts["bought_past_month_floor"],facts["customers_say"],json.dumps(facts["aspects"],ensure_ascii=False),
             json.dumps(facts["fields_found"]),now()))
    return {k:v for k,v in facts.items() if k not in {"aspects","customers_say"}} | {"aspects":len(facts["aspects"])}


def check_capture(path):
    """Report what a capture contains, without a database: use it when Amazon changes its page layout."""
    from .parsers import parse_product_summary
    capture = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    expected = ["title","byline","rating_text","ratings_count_text","histogram_text","price_text","mrp_text","bought_text","customers_say","aspects"]
    out = {"format":capture.get("format"),"kind":capture.get("kind"),"asin":capture.get("asin"),"cards":capture.get("card_count"),"url":capture.get("url")}
    if capture.get("product"):
        found = capture["product"].get("fields_found") or []
        out["product_fields_found"] = found
        out["product_fields_missing"] = [k for k in expected if k not in found]
        out["parsed"] = parse_product_summary(capture["product"])
        out["note"] = "Some fields exist only on some products (bought in past month, customers say). Several missing core fields (rating, ratings count, price) mean Amazon changed its layout: send this file for a selector update."
    return out
