import csv
import hashlib
import json
import sqlite3
import uuid
from importlib.resources import files
from pathlib import Path
from .models import SEARCH_FIELDS, REVIEW_FIELDS, now, valid_asin


def digest(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def connect(path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path, timeout=30)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys=ON")
    db.execute("PRAGMA journal_mode=WAL")
    db.executescript(files("amazon_research").joinpath("schema.sql").read_text())
    return db


def load_products(db, path):
    with open(path, newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        if not {"asin", "name", "category", "compare_group"}.issubset(reader.fieldnames or []):
            raise ValueError("products.csv needs asin,name,category,compare_group (added_at is optional)")
        # Validate before mutating, so one bad row cannot leave a partial catalog.
        rows = []
        seen = set()
        for line, row in enumerate(reader, 2):
            asin = valid_asin(row["asin"])
            if asin in seen:
                raise ValueError(f"Duplicate ASIN in products.csv, line {line}: {asin}")
            seen.add(asin)
            if any(not (row.get(key) or "").strip() for key in ("name", "category", "compare_group")):
                raise ValueError(f"Blank product name/category/compare_group on line {line}")
            rows.append((asin,row["name"].strip(),row["category"].strip(),row["compare_group"].strip(),row.get("added_at") or now()))
    with db:
        db.executemany("""INSERT INTO products VALUES (?,?,?,?,?) ON CONFLICT(asin) DO UPDATE SET
            name=excluded.name,category=excluded.category,compare_group=excluded.compare_group""", rows)
    return len(rows)


def start_run(db, kind, engine, scope, query=None, **metadata):
    run_id = uuid.uuid4().hex
    with db:
        db.execute("INSERT INTO collection_runs VALUES (?,?,?,?,?,?,?,?,?)", (run_id,kind,query,engine,scope,now(),None,"running",json.dumps(metadata,ensure_ascii=False)))
    return run_id


def finish_run(db, run_id, status):
    with db:
        db.execute("UPDATE collection_runs SET finished_at=?,status=? WHERE run_id=?", (now(),status,run_id))


def record_fetch(db, run_id, url, kind, status, outcome, parsed=0, added=0, html=None, error=None):
    with db:
        db.execute("""INSERT INTO fetches(run_id,source_url,page_kind,http_status,outcome,parsed_rows,new_rows,content_sha256,error,fetched_at)
        VALUES (?,?,?,?,?,?,?,?,?,?)""", (run_id,url,kind,status,outcome,parsed,added,digest(html) if html is not None else None,error,now()))


def write_search_page(db, run_id, rows, handle, writer):
    for row in rows:
        value = row.as_dict()
        with db:
            db.execute("INSERT INTO search_observations VALUES (" + ",".join("?" for _ in range(13)) + ")", (run_id,*(value[key] for key in SEARCH_FIELDS)))
        # Flush every card; sidecar run metadata provides time and query context.
        writer.writerow(value)
        handle.flush()


def upsert_reviews(db, run_id, rows, url, kind):
    inserted = 0
    with db:
        for row in rows:
            old = db.execute("SELECT * FROM reviews WHERE review_id=?", (row.review_id,)).fetchone()
            if old is None:
                inserted += 1
                db.execute("INSERT INTO reviews VALUES (" + ",".join("?" for _ in REVIEW_FIELDS) + ")", tuple(row.as_dict().values()))
            elif old["asin"] == row.asin:
                # Prefer fuller previews, but a full review-page or normalized
                # import may intentionally contain an edited, shorter review.
                body = row.body if kind in {"review_page","imported"} or len(row.body) >= len(old["body"]) else old["body"]
                if body != old["body"]:
                    db.execute("DELETE FROM review_sentiment WHERE review_id=?", (row.review_id,))
                db.execute("""UPDATE reviews SET product_name=?,rating=COALESCE(?,rating),title=?,body=?,author=?,
                  review_date=COALESCE(?,review_date),verified=COALESCE(?,verified),helpful_votes=COALESCE(?,helpful_votes),scraped_at=? WHERE review_id=?""",
                  (row.product_name,row.rating,row.title,body,row.author,row.review_date,row.verified,row.helpful_votes,row.scraped_at,row.review_id))
            # A pooled review can be observed under many ASINs. Keep its original
            # assignment and preserve links, rather than duplicating sentiment votes.
            db.execute("INSERT OR REPLACE INTO review_observations VALUES (?,?,?,?,?,?,?,?,?)", (row.review_id,row.asin,run_id,url,kind,row.country,row.variant,row.review_date_raw,now()))
    return inserted


def export_table(db, query, path, parameters=()):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    cursor = db.execute(query, parameters)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow([column[0] for column in cursor.description])
        writer.writerows(cursor)
    return path


def export_all(db, destination):
    destination = Path(destination)
    tables = {"products":"products", "reviews":"reviews", "review_sentiment":"review_sentiment", "sentiment_rollup":"sentiment_rollup", "compare_group_sentiment":"compare_group_sentiment", "aspect_rollup":"aspect_rollup", "collection_runs":"collection_runs", "fetches":"fetches", "review_observations":"review_observations"}
    result = []
    for filename, table in tables.items():
        result.append(str(export_table(db,f"SELECT * FROM {table}",destination / (filename + ".csv"))))
    result.append(str(export_table(db,"""SELECT r.asin,p.compare_group,r.review_id,r.review_date,
      COALESCE(substr(r.review_date,1,7),'undated') AS period,s.sentiment_score,s.sentiment_label,
      s.aspect_tags_json,s.scorer_version,s.score_status,s.quality_flags_json
      FROM review_sentiment s JOIN reviews r ON r.review_id=s.review_id JOIN products p ON p.asin=r.asin""",destination / "sentiment_output.csv")))
    return result
