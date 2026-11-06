---
name: deck-build
description: Builds the finished pptx on the template from an agreed storyline by cloning template slides, then validates, repairs, renders and lints it. Use when __OWNER__ names slides to build, change or rebuild, or asks for the final deck, replacement slides, proposal or Gantt pages.
model: __MID_MODEL__
effort: medium
argument-hint: <storyline note or deck file> [slides]
---
# /deck-build
The finished, client-ready pptx, or standalone replacement slides, built on the template from an agreed storyline. Routing: mid tier (recurring ask 2, mechanical half; ask 22 proposal pages).

## Read first
- M6 before touching anything: the latest version of the deck and its inputs; where __OWNER__ has edited the deck, that edit is the base. Say which file and date you build on.
- __OS_DIR__/output-standards.md: Deck rules (every subsection) and Formatting bans; Excel and data rules for any backing workbook.
- __OS_DIR__/templates.md: T18 (template operating system); T14 (slide-craft standard and toolchain); T13 (deck intake and cardinal rules); T22 (initiative page set) field spec; T26 (journey map slide); T27 (persona page); T20 (reusable deck tables); T15 (engagement deck rule set) when the work belongs to that engagement.
- __OS_DIR__/active-areas.md: the engagement's area (template in use, good output, rejected).
- __OS_DIR__/thinking-patterns.md: Challenge vs execution; named slides, a given template or an issued correction mean execute, and a correction means a full restructure, never a patch of the rejected one.
- The agreed storyline note and, for initiative pages, the /initiative output. No agreed storyline: stop and route to /storyline.

## Steps
1. Scope: list the slides the request covers; everything else stays untouched. Replacement slides go out as a standalone file to paste in.
2. Follow the T18 build protocol in order. Map each title to a template slide through the chain of command, standing orders and layout by tag; favourites first; honour any slide-level override in the template before editing. Proposal pages (governance, scope, risks, Gantt) use the named template slide, never a generic structure.
3. Runner clones the template's own slides and elements, writes text into existing shapes and renumbers IDs on duplication. Never draw a lookalike or add a text box in place of a template element; rebuild pasted slides, and duplicated slides that misbehave, from the original template package with correct layout bindings.
4. Fill content in place (title, subheaders, body, chart data) from the storyline and the T22, T26, T27 or T20 field specs; every data or qualitative slide carries the sources and notes line in the output-standards.md format.
5. Hygiene: delete every placeholder string and guidance sticker, replace names carried over from template pages, re-point hyperlinks.
6. Runner validates against the original, repairs until the file opens without a repair prompt, renders through the T14 toolchain and runs `python3 .claude/hooks/guard.py lint <deck>`; read every slide image yourself.
7. Pass the T18 QA gates (story, structure, charts, hygiene) and clear every lint BLOCK and every WARN that applies; then /review before it leaves __OWNER__'s hands.

## Rules enforced here
- Final deck only: every slide passes the partner test; no what-changed slides, new tags or version notes [A1].
- Build on the latest slides and inputs shared, after re-reading memory and project rules on words, focus and formats [A7] [A16]; __OWNER__'s edited version wins over any earlier copy [C1].
- Only template slides; nothing breaks the template's chain of command [C4]. Template slide structure is used as is, content is customised and the template itself never changes [C5].
- Only the slides requested change; replacement slides are delivered standalone [A10].
- One metric definition per chart; percentages on top of bars or stacked bars so one number reads per bar [A2].
- Key insights are clean complete sentences with at most one or two numbers [A3].
- Less text, more visual, impact clear on first read; no excess whitespace [A8] [A11].
- Scheme slides show the design, never rates; rates read "set at pilot" and illustrative rates sit in the appendix [A12].
- Base-deck vocabulary, no informal words [A17]; no abbreviations, and year-on-year shown alongside month-on-month [A18].
- Source notes name the primary producer, never the workbook, its tabs or an aggregator [B5]; they sit in notes or subscript, never in headlines [B2].
- Private instructions, reviewer personas and notes to Claude never appear on a slide or in its notes [B6].
- Each view or series gets its own discernible colour [B7]; reference visuals recreated in the template's style, never pasted as snapshots [B8].
- A corrupted slide is rebuilt from the template package and shared alone [C2].

## Delegate
- Template cloning, validate, repair, render and lint to runner (T14 toolchain); this mechanical half never runs on the top tier.
- A title that does not hold or a storyline gap to /storyline; initiative design questions to /initiative.
- Wording-only passes to /lexicon; the independent check to /review (critic).

## Output
- The deck saved in `03-Work/<Engagement>/` as the next file version, never over __OWNER__'s copy, or the standalone replacement slides; plus the PDF render.
- In chat: the version built on, slides changed, QA gates passed, the lint result, and any data conflict or judgement call surfaced, not resolved.
- M1 no em dashes in slides or notes. M3 final deck: no version language, new tags or change notes in slide text. M5 never invent a number, source, quote or case; gaps read "TBD, to size" or "to validate". M6 latest version and project rules first.
