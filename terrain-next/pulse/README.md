# Brand Pulse

Brand Pulse shows what India watches and says about brands in three categories: paints, two-wheelers and quick commerce. Beside it, a map shows where each category's demand sits, using district data already in TERRAIN.

| Question | Source | Geography |
|---|---|---|
| Which brands draw independent attention? | YouTube Data API v3: views on the 25 most relevant Indian videos per brand over 30 days | National |
| Who is talking, and what do they praise or complain about? | Comments on up to eight of the most-discussed independent videos per brand, read and labelled by hand | National |
| Where does the category's demand sit? | TERRAIN district fields: two-wheeler registrations and electric share, new building, upper-wealth households, dark stores | District |

**Can say:** which brands draw independent attention on YouTube this month, who is talking, and what they praise or complain about, nationally.

**Cannot say:** market share, sales, or how any district or state feels. Three limits:

- YouTube comments carry no location.
- Samples are small.
- Comment sections lean toward reviews and complaints.

## Files

| File | What it does |
|---|---|
| `brands.json` | One query per brand, with exclusions for share-price and off-topic noise. Also holds the patterns that mark the brand's own channel, and the names that tie a comment to a brand. |
| `fetch_youtube.py` | Fetches videos, view counts and comments. Standard library only. The API key never appears in code: the network proxy adds it as the `X-goog-api-key` header for `www.googleapis.com`. One run uses about 1,650 of the 10,000 daily quota units. |
| `labels/<date>.txt` | One line per sampled comment: who is talking (consumer, trade, investor, ad reaction, or not about the brand), tone and topic. Comment IDs only; no comment text is stored in the repo. |
| `pulse_reads.json` | The analyst read for each category and brand, the main worry, and quotes paraphrased in English with their source video. |
| `aggregate_pulse.py` | Joins the fetch, labels and reads into `data/next/pulse/brand_pulse.json`. It reports consumer tone only when at least 8 consumer comments were read. |
| `context.py` | Writes the district fields the Pulse map uses to `data/next/pulse/context.json` (50 KB instead of TERRAIN's 5 MB district file). |

## Refresh

```
python3 fetch_youtube.py brands.json /tmp/pulse_raw.json 30
```

Then:

1. Sample about 20 comments per brand, spread across videos and ranked by likes.
2. Read them in the original language and write `labels/<date>.txt`.
3. Update `pulse_reads.json`.
4. Run the aggregation:

```
python3 aggregate_pulse.py /tmp/pulse_raw.json labels/<date>.txt pulse_reads.json /path/to/site/data/next/pulse/brand_pulse.json
```

```
python3 context.py /path/to/site/data/terrain/districts.json /path/to/site/data/next/pulse/context.json
```

## First read, 7 November 2026

| Category | Read |
|---|---|
| Paints | 96% of paint views sit on brand channels. Independent talk comes from investors (Asian Paints' share price) and painters (scheme points and payouts), rarely from homeowners. |
| Two-wheelers | The only category where talk is about the product. TVS has the largest share of independent views, 37%. Ather's owners are the most negative: 15 of 16 comments, on the belt drive and the price of the Pro Pack. |
| Quick commerce | Two viral shorts carry 57% of independent views. Blinkit consumer comments are negative on food quality (7 of 9). |
| Quick-commerce white space | The largest upper-wealth districts with no dark store recorded in March 2026 are Malappuram (4.7 lakh upper-wealth households), Sundargarh and Kasaragod. Check these before acting: the store list may be incomplete. |
