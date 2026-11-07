# Data contract

The authoritative SQL is `amazon_research/schema.sql`. SQLite uses foreign keys and WAL journaling. Timestamps use UTC; the default comparison date follows Asia/Kolkata.

## Search observations

The emitted CSV header is exactly:

```text
asin,title,brand_guess,price_inr,mrp_inr,discount_pct,rating,review_count,sponsored,page,position,url
```

Each card is flushed to CSV as it is written. The database adds `run_id` and uses `(run_id,page,position)` as its primary key. ASIN can recur in ad/organic positions and future snapshots. The canonical URL uses `https://www.amazon.in/dp/ASIN`.

`brand_guess` is the first title token unless a known multiword prefix is supplied with `search --brands examples/brands.json`. It remains an inference. An invalid MRP is preserved as source evidence but produces no derived discount when below selling price. Missing values are blank in CSV / NULL in SQLite. Sponsored is true only with positive markup/text evidence, otherwise unknown. Position counts supported search-result card slots, not every banner or carousel on the page.

The sidecar records collection time and status separately to preserve the requested 12-column CSV. Browser capture preserves original `captured_at`, distinct from `imported_at`. Raw saved HTML without capture metadata has an import/collection timestamp, not proof of the page's earlier capture time.

## Requested corpus tables

`products`: `asin` (primary key), `name`, `category`, `compare_group`, `added_at`.

`reviews`: `review_id` (primary key), `asin` (foreign key), `product_name`, `rating`, `title`, `body`, `author`, `review_date`, `verified`, `helpful_votes`, `scraped_at`.

`verified` accepts 0 or 1 from imported files and NULL when the badge was not observed. Review-body absence is preserved as empty text and excluded from sentiment. Dates are parsed from supported English Amazon date strings and kept as ISO dates; unparseable date text remains in observations. The master is curated: scraping search results does not silently add every discovered listing to your cross-brand review comparison.

Duplicate review IDs are upserted. A richer preview is retained over a shorter preview; explicit full review-page and normalized imports can replace older text, including with a shorter edited review. Changed bodies invalidate existing sentiment/aspects until rescoring. An ID observed under another ASIN is recorded in `review_observations` without adding another review vote or silently moving its first product assignment.

## Sentiment tables and output

| Table/view | Grain | Main fields |
| --- | --- | --- |
| `review_sentiment` | Review ID × scorer version | Body hash, score, label, score status, estimated language, language probability, aspect tags JSON, quality flags JSON, scored_at |
| `review_aspects` | Review ID × scorer version × aspect | Mean clause sentiment and evidence JSON containing the matched clause texts and scores |
| `sentiment_rollup` | ASIN × comparison group × review month × scorer | Mean score, review/scored/negative/verified/empty/uncertain-language counts |
| `compare_group_sentiment` | Comparison group × review month × scorer | Review-weighted mean, review/scored/negative counts, number of products |
| `aspect_rollup` | ASIN × comparison group × month × scorer × aspect | Mean score and count of review-level aspect mentions |

`sentiment_output.csv` joins current products and reviews to sentiment, yielding the requested `asin`, `compare_group`, `sentiment_score`, `aspect_tags_json`, `period`, plus row-level IDs, version and quality information. Unparseable dates appear in `undated`, rather than being silently assigned to scrape month. Rollups exclude IDs actually observed under multiple ASINs. The comparison excludes undated reviews and unscored text and defaults to a 180-day posted-date window.

Scoring statuses are `scored`, `empty_body` and `needs_language_review`. Language probability is the language detector's estimate, **not** sentiment confidence. No calibrated sentiment-confidence number is invented. VADER positive/negative thresholds are +0.05/−0.05. The aspect parser splits at sentence boundaries and contrast words and uses configurable regexes; multiple aspects in one clause can still share sentiment incorrectly. Inspect evidence before relying on an aspect claim.

## Collection and provenance tables

`collection_runs` records engine, query, scope, start/end time, status and JSON metadata. `fetches` records each page URL, HTTP status, outcome, parsed/new-row counts, optional content SHA-256 and error. Full authenticated page HTML is not archived by the automated collector. `review_observations` records observed product links, page kind, country/variant/raw-date context and time.

Examples of statuses: `completed`, `captcha`, `login_required`, `mfa_required`, `access_denied`, `review_access_restricted`, `rate_limited`, `service_unavailable`, `parse_empty`, `repeated_review_page`, `repeated_search_page`, `browser_setup_error`, `error`, `interrupted`. A run can retain earlier committed observations and still terminate with one of those failure statuses. A completed run does not imply an exhaustive corpus.

## Important limits

ASIN is marketplace specific and review presentation may pool models/variants or show international buyers. Country and observed variant are stored when present, but missing provenance cannot be reconstructed. The baseline does not detect fraud, translate Hindi, distinguish all forms of Hinglish, or guarantee representative trends. No permanent raw-HTML archive means an exact future reparse requires keeping your original page captures separately.

## Product snapshots (browser capture)

`product_snapshots`: one row per `(asin, captured_at)`. It holds the title, the byline, `rating`, `ratings_count`, `histogram_json` (star to percent), `price_inr`, `mrp_inr`, `bought_past_month_floor`, `customers_say`, `aspects_json`, `fields_found_json` and `imported_at`.

It has no foreign key to `products`, so a page can be captured before the product is curated. Any fact the page did not show is stored as NULL, never as zero.

## Keepa tables

`keepa_runs`: one row per Keepa run. It holds the kind (`bestsellers` or `products`), your group label, the category, start and finish times, the status and the tokens used.

`keepa_snapshots`: one row per `(run_id, asin)`. It holds the best-seller rank and `summary_json`, the flattened product. The summary covers rating, rating count, new ratings in the window, ratings as-of date, the "bought past month" floor, sales rank, rank drops, prices and flags.

`keepa_series`: history points `(asin, series, ts, value)`. The series are `rating_count`, `rating`, `sales_rank`, `amazon_price`, `new_price` and `list_price`. Prices are in rupees; rating is from 0 to 5. Points accumulate across runs.
