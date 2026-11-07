# Amazon.in personal product research

A runnable Python project for Durga's personal product comparisons. It collects product listings and accessible reviews, imports browser captures or existing files, stores a cumulative SQLite corpus, scores review **body text**, and exports a comparison report.

**Live-access status:** a plain HTTPS search probe on 7 November 2026 returned HTTP 503 from the build environment. See `docs/VALIDATION.md` for the final browser result. The included demo data is invented and labelled **SYNTHETIC**; it is not evidence about real products. No Amazon account or previous scraper code was available in this workspace.

> **Two routes that work.** Use the Keepa API for category and brand scale (`keepa-categories`, `keepa-bestsellers`, `keepa-products`, `keepa-brands`). Use the browser extension for reading a few products closely; it now saves product facts too. Read [START_HERE.md](START_HERE.md) first. The automated collectors below are kept for reference only: Amazon blocks cloud and automated clients, so they will usually fail.

## Start here: test without Amazon or an account

Use Python 3.10 or later. From the extracted project folder:

```bash
python -m venv .venv
```

Activate it on macOS/Linux with `source .venv/bin/activate`, or on Windows PowerShell with `.venv\Scripts\Activate.ps1`. Then:

```bash
python -m pip install -e ".[dev]"
python -m pytest
python demo.py
```

Open `demo_output/comparison/report.html`. The ZIP already includes a generated demo, so **before rerunning `demo.py`, rename or remove `demo_output`**. The script refuses to overwrite a previous demo database.

Use `python -m amazon_research` in the commands below, or the installed `amazon-research` command.

## 1. Maintain your product master

The root `products.csv` starts with headers only. Add actual ASINs and product names:

```csv
asin,name,category,compare_group,added_at
```

`examples/products.demo.csv` shows the shape using fictional products. Group truly comparable specifications together, such as 1200mm BLDC ceiling fans. Refresh the catalog whenever you change groups:

```bash
python -m amazon_research init --products products.csv
```

Existing `added_at` values are preserved during updates. Removing a row from the CSV does not erase its historical reviews from the database.

## 2. Use normal browsing with one-page capture

This is the most practical starting path when automated access is blocked. It uses the page your normal browser has already loaded; it does not promise access to reviews Amazon withholds.

1. In desktop Chrome, open `chrome://extensions` (Edge: `edge://extensions`).
2. Enable Developer mode, choose **Load unpacked**, and select this project's `browser_capture` folder.
3. Browse Amazon.in normally. Sign in yourself if required and set the relevant delivery location.
4. Open a search, product, or accessible review page. Click the extension, then **Export page as JSON**.
5. Import the downloaded JSON. Repeat manually for other pages you can access.

For a search page:

```bash
python -m amazon_research import-capture /path/to/amazon-search-123.json --out data/fans-2026-11-07.csv
```

For reviews on a product/review page whose ASIN is in your master:

```bash
python -m amazon_research import-capture /path/to/amazon-B0XXXXXXXX-123.json
```

Capture is user-triggered, one page at a time. It reads product/review cards, product title, page URL and timestamp. It has no background collector or external server. It omits account headers, address/navigation panels, cookies and local storage. Reviewer display names inside review cards remain part of your requested local corpus. The shareable report omits those identities and full review text. The extension requires a desktop Chromium browser; it is not an iOS Safari extension.

Alternatively, save an HTML page from your browser:

```bash
python -m amazon_research import-html saved-search.html --kind search --page 1 --out data/search-2026-11-07.csv --url "https://www.amazon.in/s?k=ceiling+fan"
python -m amazon_research import-html saved-product.html --kind reviews --asin B0XXXXXXXX --url "https://www.amazon.in/dp/B0XXXXXXXX"
```

Replace `B0XXXXXXXX` and the paths with real values. A generic Save Page operation may capture less rendered content than the extension.

## 3. Try bounded automated collection locally

The HTTP engine needs no browser installation:

```bash
python -m amazon_research search "1200mm BLDC ceiling fan" --pages 1 --out data/fans-2026-11-07.csv --location-note "Cox Town, Bengaluru; location set manually in browser"
```

The location note records context; it **does not** set Amazon's delivery location for HTTP requests. Prices can vary by delivery setting, session, variant and time.

For Camoufox, matching your earlier approach:

```bash
python -m pip install -e ".[camoufox]"
python -m camoufox fetch
python -m amazon_research session --engine camoufox --profile profiles/amazon-research
python -m amazon_research search "1200mm BLDC ceiling fan" --engine camoufox --profile profiles/amazon-research --pages 2 --out data/fans-browser-2026-11-07.csv
python -m amazon_research reviews --engine camoufox --profile profiles/amazon-research --mode featured
python -m amazon_research reviews --engine camoufox --profile profiles/amazon-research --mode pages --pages 3 --asin B0XXXXXXXX
```

The `session` command opens a visible browser. You sign in yourself and press Enter in the terminal when done. The dedicated profile stores session cookies locally with restricted directory permissions on Unix. It is **not an encrypted credential vault**; keep it private and do not share it. Do not point this tool at your everyday browser profile. The project does not ask for, print, export or package passwords or OTPs.

For ordinary Chromium instead:

```bash
python -m pip install -e ".[browser]"
python -m playwright install chromium
python -m amazon_research session --engine chromium
python -m amazon_research reviews --engine chromium --mode featured
```

Linux browser installations may also need operating-system browser dependencies. After a session is prepared, `--headless` is optional. Collection is sequential, with eight seconds between page requests by default and no automatic retries on denial. Search output filenames must be new; snapshots are never silently overwritten.

Featured reviews are collected from product pages. They are a **selected, incomplete sample**. The `pages` mode follows accessible next-page links and stops on repeated review IDs; it cannot promise the full review corpus. Login, MFA, CAPTCHA, account restrictions, HTTP 403/429/503 and unexpected empty results are recorded explicitly. Automatic challenge solving, account fabrication and proxy rotation are not included.

## 4. Import your existing datasets

For your normalized review CSV or JSONL:

```bash
python -m amazon_research import-reviews reviews.csv
python -m amazon_research import-reviews reviews.jsonl
```

Required: `review_id`, `asin`. Other requested review fields are supported; missing text stays empty and unknown values stay NULL. Products must already exist in `products.csv`. `review_date` must be ISO `YYYY-MM-DD`; `verified` accepts 0, 1 or blank. JSONL uses one review object per line; an example is provided. Imports commit per review, so previously imported rows remain available if a later row is invalid. The failure is recorded in `fetches` with committed row counts.

Raw vendor responses need mapping into those fields first. No paid service, API key or contract is silently configured. The historical McAuley dataset uses a different schema and lacks a general Amazon.in provenance guarantee; do not import it as current Indian buyer evidence.

## 5. Score and compare

```bash
python -m amazon_research score
python -m amazon_research export --out data/export
python -m amazon_research compare --group "1200mm BLDC fans" --days 180 --verified-only --out data/comparison
```

The default scorer is a local English VADER baseline, with a small explicit product lexicon and clause-level aspect keywords. No review text is sent to an AI API. It scores `body`, not star rating; stars are used only to flag possible disagreement. Scores range from −1 to +1 and are **not probabilities**. Aspect evidence is retained for inspection. Automatic language detection skips non-English/uncertain text; multilingual validation is still needed. Only when you have checked that your texts are English, you can use `score --language en`. This creates a different scorer version.

To customize aspects, supply a JSON object mapping each aspect to regex patterns with `score --aspects my-aspects.json`. The scorer version includes a configuration hash. Compare/export carries that version so different configurations are not blended. Compare uses the most recently scored version unless you pass `--scorer-version` explicitly.

Outputs include:

| Output | Contents |
| --- | --- |
| Search CSV | Your exact 12 columns, flushed after each card |
| Search `.meta.json` sidecar | Query/source, snapshot timestamp, run ID and status |
| `research.sqlite` | Products, cumulative reviews, observations, sentiment and access logs |
| `sentiment_output.csv` | `asin`, `compare_group`, `review_id`, `review_date`, `period`, `sentiment_score`, label, aspect tags, scorer version, status and quality flags |
| `sentiment_rollup.csv` | Product × comparison group × review month × scorer, with sample counts |
| `compare_group_sentiment.csv` | Comparison group × review month × scorer; review-weighted group summary |
| `aspect_rollup.csv` | Product × group × month × aspect, with mention counts and mean scores |
| `comparison.csv` / `report.html` | Time-window comparison, observed price, sample sizes, exclusions and quality flags |

Compare orders products by a sample-size-adjusted sentiment mean within each group, using a prior strength of 20 reviews toward that group's observed mean. That is an exploratory ordering, not a validated recommendation model. It does not weight helpful votes, infer fake reviews, reward suspicious MRP discounts or invent a score for a product with no reviews. Rows under 20 scored reviews are flagged. Review periods use the posted date, not the scrape date. Undated, unscored and review IDs observed under multiple ASINs are excluded from comparisons and pooled IDs are excluded from monthly rollups.

## Schema decisions that matter

* **ASIN is not the search-observation primary key.** A product can occupy multiple slots and recur next week. SQLite uses `(run_id, page, position)`; your CSV column order stays unchanged.
* **Search listings show visibility and offered prices, not actual units sold.** This project does not infer sales from rank.
* **Unknown is preserved.** An absent sponsored marker becomes NULL, rather than a claim that a slot is organic. Missing rating/count/verification/helpfulness is also NULL. `verified=0` remains supported for explicit imported values; the parser records `1` only when it sees the badge. Absence of a badge is not proof of no purchase.
* **Reviews can be pooled across variants.** `reviews.review_id` stays unique. `review_observations` preserves all observed ASIN links, country, variant text and raw date. The first assignment is retained and ambiguous pooled review IDs are excluded from comparative statistics. Pooling that Amazon does not expose cannot be fully detected.
* **A cumulative sample is not automatically a representative time series.** Monthly sentiment describes collected reviews, and top/featured selection can distort the trajectory. Source scope and counts travel with the data.

See [docs/RESEARCH.md](docs/RESEARCH.md) for investigated approaches and references, [docs/SCHEMA.md](docs/SCHEMA.md) for table definitions, and [docs/VALIDATION.md](docs/VALIDATION.md) for what was actually tested.

## Troubleshooting

```bash
python -m amazon_research doctor
python -m amazon_research --help
```

`--db` is a global option and goes **before** the command, for example `python -m amazon_research --db data/fans.sqlite init --products products.csv`.

Exit status: `0` completed, `2` invalid input/setup, `3` explicit access or browser problem, `130` interrupted. Inspect `fetches` and `collection_runs` for the exact reason; a header-only failed snapshot is labelled as a failed run in its sidecar, never presented as successful collection.

Non-commercial intent does not itself grant Amazon permission or guarantee access. Amazon's terms restrict automated extraction; this project is a technical implementation, not a grant of data rights. Use it only for content and workflows you are entitled to access and reuse.
