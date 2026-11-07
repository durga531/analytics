---
name: pick
description: Gives one recommendation for a purchase, film, series or book, plus one alternative and the reason, matched to __OWNER__'s recorded taste and preference for premium over mediocre. Use when __OWNER__ asks what to buy, which one to get, what to watch or read next, or for a pick.
model: __SMALL_MODEL__
effort: low
argument-hint: <category> [budget or constraints]
---
# /pick
One pick, one alternative, the reason: a recommendation, never a list. Routing: small tier (recurring asks 21 shopping, 26 entertainment).

## Read first
- __OS_DIR__/identity.md: Interests, for taste (genres, formats and creators already rated highly) and the stated preference for quality over price.
- __OS_DIR__/active-areas.md: Other threads on record, for the current setup and constraints that change the answer (what is already owned, home setup).
- __OS_DIR__/output-standards.md: Writing voice; Formatting bans (no superlatives without a benchmark); Anti-hallucination.
- __OS_DIR__/recurring-asks.md: asks 21 and 26.
- Earlier pick notes in `05-Self/` or `06-Learn/`, so nothing already watched, read or owned comes back.

## Steps
1. Pin the decision: category, use, budget ceiling if stated, and the one constraint that rules options out (space, power, platform, language, running time). Ask one question only if the answer changes the pick; otherwise infer and state the inference in a clause.
2. Match taste: anchor on what __OWNER__ already rates highly and name the link in a phrase; drop anything rejected or already consumed.
3. Shopping: compare a short internal shortlist on the property that matters for the use, then build quality, reliability and after-sales; check current price and availability from the maker or seller, with the date. Premium over mediocre: paying more is right when the quality gap is real, never for the badge.
4. Entertainment: check where it streams or is sold in __OWNER__'s market, and the format (episodes, length).
5. Choose one pick and one alternative that differs on a clear axis (cheaper, smaller, lighter in mood, shorter).
6. Self-check before replying: no superlative without a benchmark, no invented specification, price, rating or availability.

## Rules enforced here
- A recommendation, not a list: exactly one pick and one alternative; the shortlist stays internal.
- Premium over mediocre; the reason names the property that justifies the price.
- Taste comes from the record, never from a generic bestseller or top-ten list.
- Every price, specification and availability claim carries its source and date; anything unknown reads "I do not have reliable data on this".

## Delegate
- Price, stock and streaming-availability lookups to runner, returned with source and date.
- A purchase large enough to be a financial decision goes to /decide.

## Output
Three lines in chat, no preamble:
- Pick: name, price or platform, and the one-sentence reason tied to taste or use.
- Alternative: name and the axis on which it differs.
- Check: source and date for the price or availability.
- M1 no em dashes. M5 never invent a price, specification, rating or availability.
