PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS products (
  asin TEXT PRIMARY KEY, name TEXT NOT NULL, category TEXT NOT NULL,
  compare_group TEXT NOT NULL, added_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS reviews (
  review_id TEXT PRIMARY KEY, asin TEXT NOT NULL REFERENCES products(asin),
  product_name TEXT NOT NULL, rating REAL CHECK(rating BETWEEN 0 AND 5),
  title TEXT NOT NULL, body TEXT NOT NULL, author TEXT NOT NULL,
  review_date TEXT, verified INTEGER CHECK(verified IN (0,1)), helpful_votes INTEGER,
  scraped_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_reviews_asin_date ON reviews(asin,review_date);
-- Product facts from a captured product page. No foreign key: a product can be captured before it is curated.
CREATE TABLE IF NOT EXISTS product_snapshots (
  asin TEXT NOT NULL, captured_at TEXT NOT NULL, url TEXT NOT NULL, title TEXT, byline TEXT,
  rating REAL CHECK(rating BETWEEN 0 AND 5), ratings_count INTEGER, histogram_json TEXT,
  price_inr REAL, mrp_inr REAL, bought_past_month_floor INTEGER, customers_say TEXT, aspects_json TEXT,
  fields_found_json TEXT NOT NULL, imported_at TEXT NOT NULL,
  PRIMARY KEY(asin,captured_at)
);
CREATE TABLE IF NOT EXISTS collection_runs (
  run_id TEXT PRIMARY KEY, kind TEXT NOT NULL, query TEXT, engine TEXT NOT NULL,
  source_scope TEXT NOT NULL, started_at TEXT NOT NULL, finished_at TEXT,
  status TEXT NOT NULL, metadata_json TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS search_observations (
  run_id TEXT NOT NULL REFERENCES collection_runs(run_id),
  asin TEXT NOT NULL, title TEXT NOT NULL, brand_guess TEXT,
  price_inr REAL, mrp_inr REAL, discount_pct REAL, rating REAL, review_count INTEGER,
  sponsored INTEGER, page INTEGER NOT NULL, position INTEGER NOT NULL, url TEXT NOT NULL,
  PRIMARY KEY(run_id,page,position)
);
CREATE INDEX IF NOT EXISTS idx_search_asin ON search_observations(asin);
CREATE TABLE IF NOT EXISTS fetches (
  fetch_id INTEGER PRIMARY KEY, run_id TEXT NOT NULL REFERENCES collection_runs(run_id),
  source_url TEXT NOT NULL, page_kind TEXT NOT NULL, http_status INTEGER,
  outcome TEXT NOT NULL, parsed_rows INTEGER NOT NULL, new_rows INTEGER NOT NULL,
  content_sha256 TEXT, error TEXT, fetched_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS review_observations (
  review_id TEXT NOT NULL REFERENCES reviews(review_id), asin TEXT NOT NULL REFERENCES products(asin),
  run_id TEXT NOT NULL REFERENCES collection_runs(run_id), source_url TEXT NOT NULL,
  page_kind TEXT NOT NULL, country TEXT, variant TEXT, review_date_raw TEXT,
  observed_at TEXT NOT NULL,
  PRIMARY KEY(review_id,asin,run_id,source_url)
);
CREATE TABLE IF NOT EXISTS review_sentiment (
  review_id TEXT NOT NULL REFERENCES reviews(review_id) ON DELETE CASCADE,
  scorer_version TEXT NOT NULL, body_sha256 TEXT NOT NULL,
  sentiment_score REAL CHECK(sentiment_score BETWEEN -1 AND 1),
  sentiment_label TEXT NOT NULL, score_status TEXT NOT NULL,
  language TEXT, language_probability REAL, aspect_tags_json TEXT NOT NULL,
  quality_flags_json TEXT NOT NULL, scored_at TEXT NOT NULL,
  PRIMARY KEY(review_id,scorer_version)
);
CREATE TABLE IF NOT EXISTS review_aspects (
  review_id TEXT NOT NULL, scorer_version TEXT NOT NULL, aspect TEXT NOT NULL,
  sentiment_score REAL NOT NULL, evidence_json TEXT NOT NULL,
  PRIMARY KEY(review_id,scorer_version,aspect),
  FOREIGN KEY(review_id,scorer_version) REFERENCES review_sentiment(review_id,scorer_version) ON DELETE CASCADE
);
CREATE VIEW IF NOT EXISTS sentiment_rollup AS
SELECT r.asin,p.compare_group,COALESCE(substr(r.review_date,1,7),'undated') AS period,
       s.scorer_version,COUNT(*) AS n_reviews,
       SUM(CASE WHEN s.score_status='scored' THEN 1 ELSE 0 END) AS n_scored,
       AVG(s.sentiment_score) AS sentiment_score,
       SUM(CASE WHEN s.sentiment_label='negative' THEN 1 ELSE 0 END) AS n_negative,
       SUM(CASE WHEN r.verified=1 THEN 1 ELSE 0 END) AS n_verified,
       SUM(CASE WHEN length(r.body)=0 THEN 1 ELSE 0 END) AS n_empty,
       SUM(CASE WHEN s.score_status='needs_language_review' THEN 1 ELSE 0 END) AS n_language_review
FROM reviews r JOIN products p ON p.asin=r.asin JOIN review_sentiment s ON s.review_id=r.review_id
WHERE (SELECT COUNT(DISTINCT o.asin) FROM review_observations o WHERE o.review_id=r.review_id)<=1
GROUP BY r.asin,p.compare_group,period,s.scorer_version;
CREATE VIEW IF NOT EXISTS aspect_rollup AS
SELECT r.asin,p.compare_group,COALESCE(substr(r.review_date,1,7),'undated') AS period,
       a.scorer_version,a.aspect,COUNT(*) AS n_mentions,AVG(a.sentiment_score) AS sentiment_score
FROM review_aspects a JOIN reviews r ON r.review_id=a.review_id JOIN products p ON p.asin=r.asin
WHERE (SELECT COUNT(DISTINCT o.asin) FROM review_observations o WHERE o.review_id=r.review_id)<=1
GROUP BY r.asin,p.compare_group,period,a.scorer_version,a.aspect;
CREATE VIEW IF NOT EXISTS compare_group_sentiment AS
SELECT p.compare_group,COALESCE(substr(r.review_date,1,7),'undated') AS period,s.scorer_version,
       COUNT(*) AS n_reviews,COUNT(DISTINCT r.asin) AS n_products,
       SUM(CASE WHEN s.score_status='scored' THEN 1 ELSE 0 END) AS n_scored,
       AVG(s.sentiment_score) AS sentiment_score,
       SUM(CASE WHEN s.sentiment_label='negative' THEN 1 ELSE 0 END) AS n_negative
FROM reviews r JOIN products p ON p.asin=r.asin JOIN review_sentiment s ON s.review_id=r.review_id
WHERE (SELECT COUNT(DISTINCT o.asin) FROM review_observations o WHERE o.review_id=r.review_id)<=1
GROUP BY p.compare_group,period,s.scorer_version;
