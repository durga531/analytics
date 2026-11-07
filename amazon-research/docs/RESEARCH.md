# Investigated approaches

Research date: 7 November 2026. Links are discovery and implementation references, not endorsements or proof that a service will work for every Amazon.in product/account.

## Findings

| Approach | What it can contribute | Limitation and project decision |
| --- | --- | --- |
| Plain HTTPS + HTML parser | Search cards and publicly accessible review cards, with minimal setup | The build environment's first Amazon.in request returned HTTP 503. Implemented as an optional bounded transport with explicit denial logs. |
| Camoufox + a dedicated persistent session | Rendered pages and the operator's own manually prepared session | Browser behaviour does not remove an account-level restriction. Implemented without automatic CAPTCHA solving, proxy rotation or account creation. |
| One-click browser DOM capture | The product/review cards already loaded during normal browsing | Requires manual page navigation. It captures a sample, not hidden pages or the full corpus. Implemented as a local Chrome/Edge extension. |
| Saved HTML and normalized CSV/JSONL | Reuses data you already possess and decouples extraction from analysis | The file must actually contain the rendered cards, and provenance still matters. Implemented with the same parsers/storage. |
| Amazon Creators API | Official structured catalog operations for eligible Associates | Associates and qualifying-sales prerequisites make it a poor fit for this non-commercial research workflow. It is not presented as an unrestricted review archive. |
| Amazon Reviews'23 | Large historical corpus for method development | The published interaction range ends in September 2023. It does not establish current Amazon.in pricing, SKU coverage or Indian review provenance. Keep benchmark data separate from current buying comparisons. |
| Paid third-party collectors | Potentially maintained extraction and operational diagnostics | Their marketing is not a test of your ASINs, account state, depth or reuse rights. No subscription, credentials or purchase was made. Request a small ASIN-level sample before paying. |

## Primary references

1. **Camoufox documentation** — Playwright compatibility and browser launch parameters. Persistent context support was also checked against the installed Python package. <https://camoufox.com/python/usage/>
2. **Playwright Python BrowserType** — persistent-context API and dedicated browser-profile behaviour. <https://playwright.dev/python/docs/api/class-browsertype#browser-type-launch-persistent-context>
3. **Clearzero22 / amazon-camoufox-scraper** — inspected its README and scraper source through GitHub. Its source targets `amazon.com` and uses search-card selectors; its anti-detection claims are not evidence of a working Amazon.in review history collector. No code was copied into this project. <https://github.com/Clearzero22/amazon-camoufox-scraper>
4. **ScraperAPI incident report** — its November/December 2024 report says review-page access requires an Amazon login and its public collector does not scrape behind login. This is historical provider evidence, not a claim about every current Indian page. <https://status.scraperapi.com/issues/673b128e10bdfb2f6e9544bc>
5. **Amazon Creators API introduction** — catalog operations, marketplace Associates enrollment and qualifying-sales prerequisites. <https://affiliate-program.amazon.com/creatorsapi/docs/en-us/introduction>
6. **Amazon PA-API deprecation notice** — PA-API 5 is replaced by Creators API; a new project should not assume old PA-API tutorials still apply. <https://affiliate-program.amazon.com/creatorsapi/docs/en-us/paapiv5-deprecation>
7. **McAuley Lab Amazon Reviews'23** — dataset scope, 571.54 million reviews, interaction range May 1996–September 2023, and category downloads. <https://amazon-reviews-2023.github.io/>
8. **VADER upstream documentation** — a lexicon/rule sentiment method with a normalized compound score between −1 and +1. This project adds a small explicit product lexicon; its English baseline is not an aspect sentiment ground truth. <https://github.com/cjhutto/vaderSentiment>
9. **Apify w3crawler Amazon India Reviews Scraper** — a vendor-authored page documenting direct-only extraction and explicit access diagnostics. It reports public-page limitations and does not demonstrate unrestricted review depth. Not run or purchased. <https://apify.com/w3crawler/amazon-reviews-scraper>
10. **Amazon India seller-site terms** — a primary Amazon example of restrictions on automated extraction. The retail help URL could not be retrieved by the research tool during this task, so this seller-site document should not be mistaken for a verified copy of the retail terms. Review the retail terms in your normal browser before deployment. <https://sell.amazon.in/standards/terms-of-use>

## Community evidence, treated as anecdotal

A September 2026 Reddit thread reports that logged-in Amazon.com sessions returned the same eight reviews on later pages, despite trying different accounts and proxy settings. It concerns Amazon.com and cannot establish the exact behaviour of Amazon.in. Its practical lesson for this build is to detect repeated review IDs and avoid claiming a deep corpus when pagination merely repeats a sample.

<https://www.reddit.com/r/webscraping/comments/1wtyma7/amazon_review_scraping_amazoncom_restricts_review/>

A broader search including Substack did not produce a useful, verifiable Substack implementation worth basing this build on. Generic scraper marketing repeatedly conflicts on login and review availability; the software therefore measures what a particular request returned rather than encoding those claims as facts.

## What this means for choosing products

Start with a small, manually curated comparison group. Record search prices once, capture the reviews you can actually access, and inspect aspect evidence with sample counts. The software can organize and summarize that evidence. Determining a best buy also requires correct specifications, long-term reliability evidence, service coverage, warranty and your friends' preferences; a favourable text score alone does not establish those facts.
