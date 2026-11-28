# Deal Radar (AU, through Black Friday 2026)

Scans Australian watch, perfume and clothing retailers every 2 hours, 7am to 11pm Sydney time,
from 23 to 28 November 2026, and pushes a phone notification when something real turns up.

## What counts as a deal
Advertised "was" prices are ignored. AU perfume discounters show a strike-through price on
almost the whole catalogue, so a "% off RRP" figure carries no signal. Only three things trigger an alert:

| Signal | Rule (defaults in `config.json`) |
|---|---|
| PRICE_DROP | Price falls below the lowest price recorded for that item (watches -10% and -$40, perfume -15% and -$20, clothes -30% and -$30) |
| ARBITRAGE | The same product (barcode, watch model ref + brand, or perfume brand + name + concentration + ml) is 15% and $40 or more cheaper than at the next-cheapest AU retailer |
| BEATEN | A big retailer's "sale" price (Chemist Warehouse, Angus & Coote) is beaten by a feed retailer |

An OzBargain keyword watch covers everything else.

## Coverage
- Full catalogue feeds (around 32k items): Watch Depot, Starbuy, Watch Direct, The Perfume Warehouse,
  My Perfume Shop, Perfume Clearance Centre, Culture Kings, Universal Store.
- Page scrapes via Firecrawl: Chemist Warehouse (Fragrance Frenzy, Black Friday), Angus & Coote (Black Friday).
- OzBargain: fashion, health & beauty, and front page.

## Tuning
Edit `config.json`: `priority_brands` (2x ranking weight), `thresholds`, `arbitrage`,
`shopify_stores` (any Shopify store works; its host must be on the environment's network
allowlist). The run procedure is in `AGENT_RUN.md`.

## Caveats
- Watch Direct sells some grey-import stock. A cheaper price can mean an international warranty rather than an AU one.
- Matching is exact on normalised keys, so it misses some matches but rarely pairs the wrong products. Gaps over 70% are discarded as likely mismatches.
