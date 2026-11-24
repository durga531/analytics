# Deal Radar: scheduled run procedure

The owner's real target: **Longines, Grand Seiko and watches of that standard at a one-off,
throwaway price.** These are rare. Most runs should end with no phone notification. Never
invent prices; only report figures produced by the scripts or read from a page in this run.

## 0. Guard
Sydney time = UTC+11. If the Sydney date is after `end_date_sydney` in `config.json`
(2026-11-28), reply "Deal Radar finished (Black Friday is over)." and stop.

## 1. Sync state
```
cd <repo root>
git fetch origin claude/nifty-galileo-rwa6a5
git checkout -B claude/nifty-galileo-rwa6a5 FETCH_HEAD
```

## 2. Feed scan (deterministic, about 8 min)
`python3 deal_radar/scan.py` (timeout 900000 ms). It reads 11 Shopify retailers, including the
authorised luxury dealers Monards, House of Kennedy and Hardy Brothers, and writes
`deal_radar/reports/latest.json`. Alerts with `"grail": true` are the only feed alerts that
justify a push.

## 3. Web layer (Firecrawl; 8 or fewer scrapes per run)
**a. Chrono24 Australia, cheapest first.** Scrape each URL in `config.json > grail.chrono24_pages`
with `firecrawl_scrape` (formats ["markdown"], onlyMainContent true, maxAge 0). From each page
take every listing: title (keep any reference number), price AUD, condition (pre-owned or new,
"pre-owned" if unclear) and listing URL.

**b. Chemist Warehouse / Angus & Coote.** Scrape at most these two:
https://www.chemistwarehouse.com.au/shop-online/fragrance-frenzy (waitFor 6000) and
https://www.anguscoote.com.au/promotion/black-friday-watches

Write all rows to `/tmp/scraped.json` as a JSON list of
`{"store","category":"watches"|"perfume","brand","title","price","url","condition"}`, then run
`cd deal_radar && python3 web_ingest.py /tmp/scraped.json`. It drops parts/repair/replica
listings and writes `reports/web_latest.json`. Findings with `"grail": true` justify a push:
- ARBITRAGE: at least 30% below the cheapest new AU dealer price for the same reference (45% for pre-owned).
- BELOW_FLOOR: under the brand's absolute floor in `grail.absolute_floor_aud`. **Verify first:**
  scrape that one listing page and push only if it is a complete, genuine, working watch. Say if
  it is vintage, needs a service, has no papers, or the seller is private. If it fails
  verification, do not push and mention it in one digest line.

**c. OzBargain.** `alexandria_library_read`, provider `ozbargain-com-au`, capability
`deals/list_deals`, one call with entries `{"category":"fashion-apparel"}`,
`{"category":"health-beauty"}` and `{"feed":"frontpage"}`. Keep keyword matches from
`config.json > ozbargain.keywords` and skip node ids in `deal_radar/state/ozb_seen.json`; add the
ones you report and save the file. An OzBargain post naming a grail brand counts as grail only if
its price is at least 30% under the dealer price for that model in `latest.json` or the feeds.

## 4. Notify
- **Grail hit:** load `PushNotification` (ToolSearch `select:PushNotification`) and send ONE
  notification, under 200 chars, leading with the watch, e.g.
  `GRAIL: Grand Seiko SBGW323 $3,900 on Chrono24 AU vs $8,400 new at Monards (-54%). Verified working.`
- **No grail hit:** send no notification, whatever else was found.
- Final message: grail items first (with verification notes), then at most 8 lines of non-grail
  deals (type, product, price @ store, comparison, saving, link). Flag grey-market or
  "international warranty" stock.

## 5. Persist
```
git add deal_radar/state deal_radar/reports
git commit -m "deal-radar: run $(date -u +%FT%H%MZ)"
git push -u origin claude/nifty-galileo-rwa6a5
```
Retry the push up to 4 times with backoff. If it is rejected, run `git pull --no-edit origin
claude/nifty-galileo-rwa6a5` (on conflicts in state files keep your own version) and push again.
