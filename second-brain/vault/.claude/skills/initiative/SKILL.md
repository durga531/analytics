---
name: initiative
description: Designs priority initiatives past benchmark parity (T7), specifying their pages, scoring, scheme design, pilots and readiness roadmap as the client's own plan. Use when __OWNER__ asks for initiatives, our play, schemes, picks, scoring, business case, roadmap or co-create pages.
model: __TOP_MODEL__
effort: high
argument-hint: <engagement> [initiatives or slides]
---
# /initiative
Initiative designs that find the true gap, plus page content ready for /deck-build. Routing: top tier (recurring ask 2, strategic half).

## Read first
- The latest version of the deck, the initiative slides named and the raw sources behind them: transcripts, data, documents (M6). Say which version you build on.
- `.claude/rules/work.md`: path-scoped rules load only when a work file is touched, so read it for chat-only initiative work.
- __OS_DIR__/output-standards.md: Deck rules (Numbers and evidence, Design, Language, Process) and Formatting bans.
- __OS_DIR__/templates.md: T7 (initiative refinement method); T22 (initiative page set) and its field spec; T23 (second-wave initiative card); T24 (co-create page); T26 (journey map slide); T27 (persona page); T28 (case study template); T29 (KPI strip); T30 (readiness-gated roadmap); T31 (micro-market cascade); T32 (scoring and selection); T33 (business case page); T48 (benchmark case study playbook); T15 (engagement deck rule set) when the work belongs to that engagement.
- __OS_DIR__/active-areas.md: the engagement's area, above all what the client and the partner rejected.
- __OS_DIR__/thinking-patterns.md: Challenge vs execution (initiative design is a challenge zone); Frameworks (test and control, readiness gates, adopt or adapt or avoid, scoring with robustness); Closed debates.

## Steps
1. Run T7 on each initiative in order: what specifically breaks today, read from raw sources; what a peer-standard fix leaves untouched; the design that goes past it; what better looks like in numbers.
2. Diagnose before designing: for each gap state the hypothesis, the root cause and its implication, and re-derive inherited analysis from the raw sources rather than reuse it [A19].
3. Find the true gap and design the difference-maker; never stop at benchmark parity. Picks may change on the evidence: say which and why before building.
4. Write it as the client's own plan: start from what the client already runs, state as-is mechanics correctly, and sequence by capability so no step outruns readiness.
5. Select with T32: score against its fixed rubric, quote the weights and cut-off from T32 (never invent them), rerun the selection under several alternative weightings, mark each pick robust or weight-sensitive, and place the rubric in the appendix.
6. Specify the pages: T22 for priority initiatives, T23 for the second wave, T24 for co-creation sessions, T26 and T27 for journeys and personas, T28 and T48 for benchmark cases, T29 for the KPI strip, T31 for the cascade, T33 for the business case.
7. Co-creation decks: T33 is switched off and the T22 value fields (investment and value, the value stats, the business-case page) are left out; no value, return or scenario numbers appear anywhere in the deck.
8. Pilots run as test and control with a scale gate; the roadmap is gated on readiness, not months (T30).
9. Channel schemes carry the competition-law guardrails in output-standards.md (Numbers and evidence), written into the scheme design itself: only a recommended price ceiling, no conditions on resale, and no pricing discussion with distributors.
10. Closed debates in thinking-patterns.md stay closed; a design never reopens one.

## Rules enforced here
- Our-play pages are never plain text: each shows the design visually (design table or flow), what will not be done, and the pilot with its control group [A9].
- Less text, more visual; push the page design until each page would survive a top-tier partner review, and redesign any text-heavy page before it leaves [A8].
- Scheme pages show the design (eligibility, the payout trigger, the step-up, the funding source, the settlement route), never rates or payout amounts; rates read "set at pilot" and illustrative rates go to the appendix. A design instruction given once binds every later build without being restated [A12].
- Change only the initiative slides asked for; every other slide stays untouched, even where the template or your own judgement suggests a change; flag it and ask instead [A10].
- The agreed levers and house stay intact; for any structural change, think and tell first and change only once agreed [A14].
- Each initiative leads with what it addresses and what we are building, never a value figure or a committed range; value sits only on the business-case page with its build and basis [A5].
- Analysis is never pivot-level description: each as-is finding carries its hypothesis, root cause and implication and must survive a senior challenge [A19].
- Numbers not yet built read "TBD, to size"; unconfirmed facts read "to validate"; co-creation pages carry no value or return numbers.
- Case studies carry the money invested, the impact in absolute terms and in money, and the timeline (T28).
- Journey pages use the standard stage lexicon and an inputs placeholder row (T26), never invented labels.

## Delegate
- Client or partner feedback on the deck (transcripts, comments) to /diagnose first; design from its T4 (stakeholder feedback diagnosis), not from raw comments.
- Benchmark, case and fact lookups (with source and date) to runner; scoring arithmetic and weighting reruns to runner, while the rubric judgement stays here.
- Data the business case needs to /data-request (T35 data request workbook), raised as the critical path.
- The agreed page content to /deck-build; an independent check to critic before anything leaves.

## Output
- Per initiative: the four T7 answers, the root cause behind the gap, the pick with its robustness tag, then page content in the T22 field spec (T23 or T24 where those apply; value fields off for co-creation decks), ready for /deck-build.
- In chat: picks that changed and why, structural proposals awaiting approval, and the data gaps that block sizing.
- Agreed decisions go to the engagement hub (T5 decision and action log).
- M1 no em dashes. M3 final deck pages only, no version language. M5 never invent a number, rate, case or quote. M6 name the file version you built on.
