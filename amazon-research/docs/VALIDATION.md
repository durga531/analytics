# Validation performed

Build/test date: **7 November 2026**. This project was built in a remote development workspace, not installed on Durga's own laptop.

## Results at a glance

| Check | Result | What it establishes |
| --- | --- | --- |
| Automated tests | **30 passed** | Parser fields, repeated ASIN slots, explicit denials, date/count parsing, SQL/CSV contracts, deduplication, body updates, pooled-review exclusions, sentiment/aspects, import timestamps and comparison exclusions |
| End-to-end synthetic demo | **Passed** | 3 fictional products, 3 search-card observations, 6 unique invented reviews, 4 English texts scored, 1 Hindi text withheld for language review, 1 empty body withheld |
| Real Camoufox browser with intercepted local search fixture | **Passed** | Browser capture function → JSON → parser → SQLite: 3 rows |
| Real Camoufox browser with intercepted local review fixture | **Passed** | Browser capture function → JSON → parser → SQLite: 2 rows |
| HTML report in Camoufox | **Passed** | Report renders a table with 3 products and an explicit synthetic-data heading; layout was visually inspected |
| JavaScript/Python syntax | **Passed** | Capture JavaScript passed Node syntax checking; Python source parsed successfully |
| SQLite integrity/foreign-key checks | **Passed** | Demo database reported `ok` and no foreign-key violations |
| Live direct HTTPS Amazon.in search | **HTTP 503; zero rows** | This environment did not receive a supported listing page |
| Live Camoufox Amazon.in search | **HTTP 503; zero rows** | After resolving the workspace's certificate trust issue, a real browser request still did not receive product data |
| Separate available cloud Chrome browser | **Amazon rejected the session/client; zero rows** | Visible page title was “500 - Amazon.in” and the page said it did not support this session or client |

The browser fixture checks use locally fulfilled synthetic pages at the test URL. **They are not successful live Amazon requests.** They exercise the extension's extraction function in a real DOM; the full extension install/popup permission flow was not installed or tested on the user's own Chrome.

## Live-access details

The first Camoufox attempt encountered `SEC_ERROR_UNKNOWN_ISSUER` because Firefox did not trust this remote workspace's pre-existing network CA. Importing that existing trusted CA into the isolated test profile resolved certificate verification; HTTPS verification was not disabled. The subsequent request returned HTTP 503 and terminated with an explicit `service_unavailable` result and a failed snapshot sidecar.

The separate cloud Chrome browser displayed: “We are sorry for the inconvenience. We do not support your session or client. Please try again with a different, up-to-date browser or the Amazon Shopping mobile app.” This is evidence about that browser's access, not evidence that Amazon is down or that the user's normal browser will be rejected.

No CAPTCHA was solved, no account was created, no credentials were collected, no proxy service was purchased, and no paid data API was invoked. No live product or review rows were collected. `demo_output` contains only invented data and should never be used for an actual purchase recommendation.

See `live_access_results.json` for the sanitized run outcomes. Browser profiles, cookies, certificates, screenshots and browser binaries are excluded from the ZIP.

## Environment

* Python 3.12.14; Linux.
* beautifulsoup4 4.15.0; httpx 0.28.1; vaderSentiment 3.3.2; langdetect 1.0.9.
* pytest 9.2.0; Playwright 1.62.0; Camoufox Python package 0.4.11.
* Camoufox browser v158.0.1-beta.41 was downloaded from its official GitHub release for browser checks.
* One pytest deprecation warning came from the preinstalled anyio test plugin. All 30 project tests passed.

## Reproduce

```bash
python -m pip install -e ".[dev]"
python -m pytest
```

For browser checks (optional; downloads a large browser package):

```bash
python -m pip install -e ".[camoufox]"
python -m camoufox fetch
python tests/browser_smoke.py
```

Open the included `demo_output/comparison/report.html` without running anything. To regenerate the demo, first rename/remove the included `demo_output` folder, then run `python demo.py`.

## Limits that remain

Live search/review extraction on the user's own normal connection/session is **not yet verified**. The project deliberately reports failure when Amazon returns unsupported pages. Browser capture, imports and the sentiment/report pipeline are ready to use with pages/data the operator can actually access.

English rule-based sentiment is a transparent baseline, not a validated multilingual recommendation model. There is no measured accuracy claim. Before recommending real products, hand-label a representative sample of the relevant Indian category reviews and check aspect extraction, negative cases, variant pooling and missing-data effects. Monthly outputs describe the collected sample, not all buyers.

## Update, 7 November 2026: Keepa connector and product-page capture

| Check | Result | What it establishes |
| --- | --- | --- |
| Automated tests | **43 passed** (30 original, 9 Keepa, 4 product capture) | Keepa time and history decoding, the rating window measured from Keepa's last rating update, rank drops, stale-rating and short-history flags, waiting on HTTP 429 and retrying, batches of 20, the key redacted from every error, brand folding and shares summing to 1, the HTML and CSV report, product-fact parsing, saving a product page with no reviews, and `capture-check` |
| Extension `capturePage()` in real Chromium | **Passed** on a synthetic Amazon.in product page | All 9 product facts on that page found, including "bought in past month" split across two tags; the capture parsed and imported |
| Live Keepa API | **Not run** | No Keepa subscription exists yet, and this cloud environment cannot reach api.keepa.com. Payload shapes follow Keepa's published documentation, read on 7 November 2026. |
| Live Amazon.in product page | **Not run** | Amazon blocks this environment. The selectors are best known; run `capture-check` on your first real capture. |

The Keepa key is read only from an environment variable on the user's computer. It is never written to the database, the reports or any log, and the tests check that errors redact it.
