---
name: deck-build
description: Builds the finished pptx from an agreed storyline by cloning the working template's slides, then validates, repairs, renders, lints and diffs it. Use when __OWNER__ names slides to build, change or rebuild, or asks for the final deck, replacement slides, proposal or Gantt pages.
model: __MID_MODEL__
effort: medium
argument-hint: <storyline note or deck file> [slides]
---
# /deck-build
The finished, client-ready pptx, or standalone replacement slides, built on the working template from an agreed storyline. Routing: mid tier (recurring ask 2, mechanical half; ask 22 proposal pages).

## Read first
- M6 before touching anything: the latest version of the deck and every input shared; where __OWNER__ has edited the deck, that edit is the base. Say which file and date you build on.
- `.claude/rules/work.md`: path-scoped rules load only when a work file is touched, so read it before the build starts.
- The engagement hub's T5 (decision and action log): decisions taken, slides removed, templates agreed [A15].
- __OS_DIR__/output-standards.md: Deck rules (every subsection) and Formatting bans; Excel and data rules for any backing workbook.
- __OS_DIR__/templates.md: T14 (slide-craft standard and toolchain); T13 (deck intake and cardinal rules); T22 (initiative page set) field spec; T26 (journey map slide); T27 (persona page); T20 (reusable deck tables); T17 (four-horizon capability table); T43 (number classes); T15 (engagement deck rule set) when the work belongs to that engagement.
- T18 (template operating system) only when that template is the working template. It is never the default: any other template __OWNER__ names governs through its own slides, guides and elements [C4] [C5], and if its design language is not on record, ask at intake (T13).
- __OS_DIR__/active-areas.md: the engagement's area (template in use, good output, rejected).
- __OS_DIR__/thinking-patterns.md: Challenge vs execution; named slides, a given template or an issued correction mean execute, and a correction means a full restructure, never a patch of the rejected one.
- The agreed storyline note and, for initiative pages, the /initiative output. No agreed storyline: stop and route to /storyline.

## Steps
1. Scope: list the slides the request covers; everything else stays untouched. Replacement slides go out as a standalone file to paste in. Before any structural edit (sections, levers, house, slide order), stop, explain the change and wait for agreement.
2. Map each title to a slide of the working template: with T18's template, through its build protocol, chain of command, standing orders and layout by tag; with any other, through that template's own guides, picking its closest slide. Honour any slide-level override before editing. Proposal pages (governance, scope, risks, Gantt) use the named template slide, never a generic structure.
3. Runner clones the template's own slides and elements, writes text into existing shapes and renumbers IDs on duplication. Never draw a lookalike or put a new text box where a template element belongs; rebuild pasted slides, and duplicated slides that misbehave, from the untouched template package so each keeps its proper layout binding.
4. Fill content in place (title, subheaders, body, chart data) from the storyline and the T22, T26, T27, T20 or T17 field specs; every data or qualitative slide carries the sources and notes line in the output-standards.md format, and every figure its T43 number class, exact or directional. Co-creation decks: T33 (business case page) is off and the T22 value fields (investment and value, the value stats) stay out.
5. Hygiene: delete every placeholder string and guidance sticker, replace names carried over from template pages, re-point hyperlinks.
6. Runner validates against the original, repairs until the file opens without a repair prompt, renders through the T14 toolchain and runs `python3 .claude/hooks/guard.py lint <deck>`; read every slide image yourself, maps included.
7. Runner runs `python3 .claude/tools/deck_diff.py <new deck> <previous version>` (new file first; with one argument it finds the previous version itself); check the changed, added and removed slides against the request.
8. Pass the template's QA (the T18 QA gates when that template is in use) and clear every lint BLOCK and every WARN that applies; then /review before it leaves __OWNER__'s hands.

## Rules enforced here
- Final deck only: every slide passes the partner test; no what-changed slides, new tags or version notes [A1].
- Build on the latest slides and inputs shared, after re-reading memory and project rules on words, focus and formats [A7] [A16]; __OWNER__'s edited version wins over any earlier copy and is never overwritten [C1].
- Only the template's own slides and elements; nothing breaks its chain of command [C4]. Its slide structure is used as is: content is customised and new slides are cloned from template slides [C5].
- Only the slides requested change; finalised slides stay untouched; replacement slides are delivered standalone [A10].
- Stop and explain before any structural edit; the agreed architecture (levers, house, sections) never changes without agreement [A14].
- A slide the decision owner removed stays removed and its content is never carried forward (check the T5 log); calculations and units (per-unit basis, denominators) are re-checked on every numeric slide [A15].
- Executive-summary lines are precise, client-credible statements that make sense read alone, never slogans or colloquial lines [A4]; no value figure or committed range leads the executive summary, a section or an initiative, and value sits on the business-case page with its build [A5].
- No extreme or absolute words in slide text; neutral maturity wording, with verbatim quotes and competition-law guardrail wording exempt; a finalised executive summary is kept [A13].
- Our-play pages are never plain text: the design shown visually, what will not be done, the pilot with its control group [A9].
- One definition per metric on a chart, never two versions of the same measure; a value label above each bar, or a stacked bar, so exactly one number reads per bar, using the template's own chart elements [A2].
- Key-insight panels are clean, complete sentences stating a non-obvious implication, each carrying one or two numbers at most; never number strings or fragments [A3].
- Less text, more visual, impact clear on first read; no excess whitespace, judged on the rendered images [A8] [A11].
- Scheme slides show the design, never rates; rates read "set at pilot" and illustrative rates sit in the appendix [A12].
- Base-deck vocabulary, no informal words [A17]; no abbreviations, and year-on-year shown alongside month-on-month [A18].
- Source notes name the primary producer, never the workbook, its tabs or an aggregator [B5]; they sit in notes or subscript, never in headlines or the body flow [B2].
- Private instructions, reviewer personas and notes to the assistant never appear on a slide, in its notes or in file properties [B6].
- Each view or series gets its own discernible colour [B7]; reference visuals recreated in the template's style, never pasted as snapshots [B8]; map layers register exactly on the base outline with no offset, checked in the render [B10].
- A corrupted slide is rebuilt from the template package and shared alone [C2].

## Delegate
- Template cloning, validate, repair, render, lint and deck_diff to runner (T14 toolchain); this mechanical half never runs on the top tier.
- A title that does not hold or a storyline gap to /storyline; initiative design questions to /initiative; transcripts and stakeholder feedback to /diagnose.
- Wording-only passes to /lexicon; the independent check to /review (critic).

## Output
- The deck saved in `03-Work/<Engagement>/` as the next file version, never over __OWNER__'s copy, or the standalone replacement slides; plus the PDF render.
- In chat only, never on a slide: the version built on, the deck_diff list of slides changed, added or removed, QA gates passed, the lint result, and any data conflict or judgement call surfaced, not resolved.
- M1 no em dashes in slides or notes. M3 final deck: no version language, new tags or change notes in slide text. M5 never invent a number, source, quote or case; gaps read "TBD, to size" or "to validate". M6 latest version and project rules first.
