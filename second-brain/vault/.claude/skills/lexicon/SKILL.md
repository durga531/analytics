---
name: lexicon
description: Runs a standing-rules wording pass on a deck and workbook (banned, informal and extreme words, version language, abbreviations, source notes, undefined terms), applying approved items via one lexicon. Use when __OWNER__ asks for a lexicon pass, wording audit or neutral wording.
model: __SMALL_MODEL__
effort: low
argument-hint: <deck file> [workbook file]
---
# /lexicon
A T6 wording audit of one deck and its workbook, applied on approval through a single lexicon. Routing: small tier (recurring ask 5, the standing-rules pass; its headers-only storyline review belongs to /storyline).

## Read first
- The latest version of the deck and its backing workbook (M6); name both files.
- `.claude/rules/work.md`: path-scoped rules load only when a work file is touched, so read it before the pass.
- __OS_DIR__/output-standards.md: Formatting bans (banned words, banned informal words, extreme words, abbreviations, headline limits); Deck rules, subsections Deck type and scope (final deck, no version language), Language (standard terms, define before use, journey-map stages) and Numbers and evidence (source-note format, allowed source labels).
- __OS_DIR__/templates.md: T6 (wording audit) for the table and reply format; T13 (deck intake and cardinal rules) for banned words with replacements; T15 (engagement deck rule set) when the deck belongs to that engagement.
- __OS_DIR__/active-areas.md: the engagement's area (words rejected, terms approved) and any base deck or lexicon its hub names.
- __OS_DIR__/thinking-patterns.md: Challenge vs execution; an approved wording pass is execution, not debate.

## Steps
1. Detect: run `python3 .claude/hooks/guard.py lint <deck> <workbook>`, then read every slide, note and sheet string for what the lint cannot see: informal words from the rejected lists, extreme words in body text, abbreviations, version language, and source notes citing the workbook, its tabs or an aggregator.
2. Version language: flag every tag or label that marks content as new, updated or revised since an earlier version, every version number or change note, and any line on what changed, what moved or what goes where, in slide text and speaker notes alike.
3. Definitions: list each term, code and ID with the slide that defines it; any use before that slide is a finding. Flag every time view that shows month-on-month without year-on-year.
4. Propose in the T6 format: sections by theme (storyline language, client vocabulary, version language, sources, abbreviations, definitions and IDs); each row # | Where | Today | Proposed a or b | Basis, where the basis is the base deck and page or the output-standards.md rule.
5. Wait for the reply, for example "A1 b, B2 yes" (audit row IDs, not correction tags), and apply only the approved items.
6. Apply through one lexicon (term to replacement) to the deck and its workbook together, so each term reads the same everywhere; verbatim quotes and competition-law guardrail wording keep their words.
7. Re-run the lint and confirm the deck still opens without a repair prompt; then hand the headers-only storyline review to /storyline, which runs it on the final wording.

## Rules enforced here
- The deck reads as a final deck: version language in slide text or notes is always a finding, and its fix deletes the words, never adds a change note or a slide on what changed [A1].
- No extreme or absolute words in client slides; neutral maturity wording that names the stage reached, so the client is not put on the defensive. The pass changes words only and never redesigns a finalised slide [A13].
- Re-read memory and preferences on words, focus and formats before the pass; lexicon items approved in earlier passes carry forward [A16].
- Base-deck vocabulary replaces informal, folksy or AI-sounding words; every proposal names its basis [A17].
- No abbreviations in client slide text; every time view carries year-on-year alongside month-on-month [A18].
- Source notes name the primary producer and never the workbook or its tabs; no term or ID appears before its definition.
- Journey stages use the standard stage lexicon in output-standards.md (Language), never invented labels.
- Headlines stay within the length and punctuation limits in output-standards.md (Formatting bans); a fix that would change the argument goes to /storyline instead.

## Delegate
- The headers-only storyline review is strategic: hand it to /storyline once this pass is applied.
- Structure, chart grammar, density or design findings go to /review or /deck-build, never into this pass.
- Validate, repair and render after a large apply to runner (T14 slide-craft standard and toolchain).

## Output
- The T6 table in chat, grouped by theme with a count per section; after approval, one line: items applied, files written, lint result.
- Approved term pairs are added to the lexicon list in the engagement hub, so the next pass starts from them.
- M1 no em dashes in any replacement. M3 no version language, new tags or change notes in slide text. M5 never invent a basis, source or term. M6 latest deck and workbook, named.
