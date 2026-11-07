# Start here

## What works, and what does not

Amazon refuses cloud and automated clients before any sign-in, with HTTP 503 or "We do not support your session or client". That is why the first build collected nothing. A login does not change it, and this kit does not try to get around it.

There are two routes that work:

| Need | Route | What you get |
|---|---|---|
| Category and brand scale: hundreds of products, tracked over time | **Keepa API**, a licensed Amazon data service that covers Amazon.in. Paid, from €49 a month. | Ratings, rating-count growth (the best public sign of what sells), Amazon's "bought in past month" floor, best-seller rank and price history. A brand table and an HTML report. No review text. |
| Deep reading on a few products | **The browser extension**, on your own laptop while you browse normally | The product facts on a page (stars, number of ratings, the 5-to-1-star breakdown, price, M.R.P., "bought in past month", Amazon's "Customers say" summary) and any loaded review cards, saved one page at a time. |

## Set up once on your laptop

You need Python 3.10 or later. From this folder, create a virtual environment:

```
python -m venv .venv
```

Activate it on macOS or Linux:

```
source .venv/bin/activate
```

Or on Windows PowerShell:

```
.venv\Scripts\Activate.ps1
```

Then install the kit and check it works:

```
python -m pip install -e ".[dev]"
```

```
python -m pytest
```

All 43 tests should pass.

## Route 1: Keepa (category and brand scale)

1. Subscribe at https://keepa.com/#!api (the entry plan gives 20 tokens a minute) and copy your API key.
2. Put the key in an environment variable on your laptop. Never paste it into a chat, a file in this folder or a spreadsheet.
   - macOS or Linux: add `export KEEPA_API_KEY="your key"` to `~/.zshrc`, then open a new terminal.
   - Windows PowerShell: run `setx KEEPA_API_KEY "your key"`, then open a new terminal.
3. Find the category ID (costs 1 token):

```
python -m amazon_research keepa-categories "ceiling fan"
```

4. Fetch that category's top 100 best sellers. This costs 50 tokens for the list and about 2 per product, so allow about 15 minutes on the entry plan. The kit waits for tokens by itself.

```
python -m amazon_research keepa-bestsellers 1234567031 --group "Ceiling fans" --top 100
```

5. Build the brand table and report. This uses no network.

```
python -m amazon_research keepa-brands --group "Ceiling fans"
```

6. Open `data/keepa/keepa_brands.html`. The CSV files sit beside it.

To track your own shortlist instead of best sellers, run `keepa-products --asins B0XXXXXXXX,B0YYYYYYYY --group "My fans"`. Without `--asins`, it fetches every product in your `products.csv`.

Keepa refreshes ratings from Amazon only from time to time. The report flags products whose ratings are more than 30 days old. `--refresh-ratings` asks Keepa to re-read them now, at about 6 tokens a product.

**How to read the brand table.** "Share of new ratings" is each brand's share of the ratings added in the window, across the products you fetched. It shows who is selling now, not market share, because only some buyers leave a rating. "Bought past month" is Amazon's own bracketed floor (for example 1,000+), and Amazon shows it for some products only.

## Route 2: the browser extension (deep reading)

1. In Chrome, open `chrome://extensions` (in Edge, `edge://extensions`). Turn on Developer mode, choose **Load unpacked** and select the `browser_capture` folder. If you loaded the earlier version, click reload.
2. Browse Amazon.in normally. On a product page, a search page or a review page, click the extension, then **Export page as JSON**.
3. Check what was captured (no database needed):

```
python -m amazon_research capture-check ~/Downloads/amazon-B0XXXXXXXX-123.json
```

4. Import the capture:

```
python -m amazon_research import-capture ~/Downloads/amazon-B0XXXXXXXX-123.json
```

A product page with no reviews loaded is now saved as a product snapshot; the earlier version rejected it. For reviews, add the product to `products.csv` and run `init` first. Then run `score` and `compare` as described in the [README](README.md).

**First real capture.** The page selectors were tested on synthetic pages in a real browser, not on live Amazon.in, because Amazon blocks the build environment. If `capture-check` lists the rating, number of ratings or price as missing on a normal product page, Amazon's layout differs. Send that one JSON file and the selectors can be fixed in minutes. The file holds no account details.

## What is in the box

- Keepa connector: `amazon_research/keepa.py`.
- Capture extension: `browser_capture/`.
- Parsers, storage, sentiment and reports: the rest of `amazon_research/`.
- Tests: `tests/`. Fixtures are synthetic and labelled as such.

The [README](README.md) covers every command. [Validation](docs/VALIDATION.md) records what was tested and what was not.
