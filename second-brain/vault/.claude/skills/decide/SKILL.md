---
name: decide
description: Writes a memo for a consequential personal or career choice, with the gut call and confidence first, wider options, the case against, a pre-mortem and a review date; the call stays with __OWNER__. Use when __OWNER__ says should I, help me decide, or is torn between options.
model: __CARE_MODEL__
effort: high
argument-hint: <the decision in one sentence> [deadline]
---
# /decide
A decision memo that protects __OWNER__'s judgement: gut call on record, the best case for each option, a pre-mortem and a date to check the outcome. Routing: care tier (recurring ask 18, decisions), kept on the stronger model by design.

## Read first
- `.claude/rules/self.md`.
- Any earlier decision note on the same question in `05-Self/` (gut call, confidence, review), and the latest version of any file the choice rests on, such as an offer, a budget or a plan (M6); say which version.
- __OS_DIR__/identity.md: Ambitions; Roles and employers for titles and dates only.
- __OS_DIR__/active-areas.md: the personal and career areas the choice touches, and the standing life directives.
- __OS_DIR__/thinking-patterns.md: Challenge vs execution (personal choices and theses are challenged; __OWNER__ wants to hear when the preferred option is weak); Closed debates.
- __OS_DIR__/templates.md: T1 (executive answer structure) for the memo; T8 (life diagnostic) when the choice shapes life direction; T50 (resume architecture and fact base) for any figure about __OWNER__'s own record; T10 (investment committee rules) and T11 (fresh-capital research brief) when money moves into markets.
- `08-Library/Templates/Decision.md`.

## Steps
1. Frame it in one sentence: what is being decided, by when, and what waiting costs. If the stated question is not the real one, say so once and propose the better question.
2. Gut call first: unless already given, ask for a one-line instinct and a confidence percentage before any analysis, and record both verbatim.
3. Size the door: a one-way door (hard to reverse) gets the full memo, and any doubt is settled first with the one or two questions whose answers would change the call; a two-way door gets five lines and a fast decision.
4. Options: the ones on the table plus at least one that is not (wait for a named trigger, a staged or reversible version, a different question).
5. Criteria: three to five, drawn from what __OWNER__ has said matters (ambitions, the standing directives), weighted explicitly; say where two criteria pull against each other.
6. Evidence: facts carry source and date; estimates carry a percentage and their basis; unknowns are named as unknown.
7. Answer in T1 shape: the recommendation in one sentence, the logic tree behind it, the single risk that could overturn it, and what to do this week.
8. Argue the other side: the strongest case against the option __OWNER__ prefers, answered or conceded. Where the gut call and the analysis disagree, say which you back and why.
9. Pre-mortem: the leading option has failed a year from now; the three likeliest reasons and the early warning for each.
10. When the choice shapes life direction, test it against T8's findings and levers before the final call.
11. State what would change the answer, set review_on, and stop: the call is __OWNER__'s.

## Rules enforced here
- Care and directness: no cheerleading and no sugarcoating; when the evidence says no, say no plainly.
- A choice about current holdings goes to /equity under M2; this skill never recommends selling, trimming, exiting, reducing, a stop-loss or a tax-loss move, however the question is framed.
- Whether to apply for a role, and with which resume, goes to /resume, where the strategist makes the fit call first. Any figure about __OWNER__'s record comes from the locked fact base, which beats identity.md and every other file (M4).
- Engagement decisions belong in that engagement's T5 (decision and action log), not here.
- No invented base rate, statistic or case; closed debates stay closed; a standing directive changes only when __OWNER__ says so.

## Delegate
- Fact lookups (costs, rules, timelines, market data) to runner, each returned with source and date; the brief carries only the detail the lookup needs.
- Deploying new money to /equity (T10, T11).
- For a one-way door, offer the T2 maker-checker loop on the memo before the final call; the critic grades the reasoning, it never decides.

## Output
- In chat: the gut call and confidence as recorded, the T1 answer, a table Option | Upside | Downside | Reversible | Fit with directives, the pre-mortem, what would change the answer, the review date.
- Saved: `05-Self/YYYY-MM-DD Decision - <title>.md` from the Decision template, status open, confidence and review_on set. On the review date, compare outcome with expectation and separate decision quality from luck.
- M1 no em dashes. M2 no sell, trim, exit, reduce, stop-loss or tax-loss suggestion on any holding. M4 fact-base numbers only for __OWNER__'s record. M5 nothing fabricated; "I do not have reliable data on this" where data is missing. M6 name the version of any file the choice rests on.
