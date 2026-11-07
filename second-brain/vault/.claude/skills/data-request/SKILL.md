---
name: data-request
description: Drafts data request workbooks, input templates, expert sourcing briefs and visit question banks, each table designed from the slides it feeds. Use when __OWNER__ says data request, data sheet, what data do we need, input template, expert brief or question bank.
model: __MID_MODEL__
effort: medium
argument-hint: <engagement> [slides or initiatives to feed]
---
# /data-request
A data request the recipient can fill in one sitting, designed backwards from the slides it must feed. Routing: mid tier (recurring ask 12).

## Read first
- Latest version of the deck or storyline the data must feed, and the engagement hub's data-request table (M6); say which deck version the request maps to.
- `.claude/rules/work.md`: opened here because path-scoped rules load only when a file in `03-Work/` is touched, and a request is usually drafted in chat first.
- __OS_DIR__/output-standards.md: Excel and data rules; Deck rules (Language; Numbers and evidence); the first verbatim-corrections list.
- __OS_DIR__/templates.md: T35 (data request workbook), T36 (expert sourcing brief), T37 (account visit pack); T15 (engagement deck rule set) only when that engagement is the working one.
- __OS_DIR__/active-areas.md: the engagement's area and its data-request entry where one exists (status, good output, rejected).
- __OS_DIR__/thinking-patterns.md: What I push on (data as the critical path); Challenge vs execution.

## Steps
1. List the slides and initiatives that lack data and, for each, the exact data point, unit, period and granularity the chart or claim needs.
2. Design each table backwards from those slides: rows and columns are the cut the chart will show; ask for the finest grain the recipient holds when the slide needs its own cut.
3. Consolidate: one table may feed several slides; merge duplicates; drop any ask no slide uses.
4. Lay out T35: one file, two tabs at most (the client's own inputs; experts and competitors); compact fill-in tables, each headed with the slides and initiatives it feeds, the unit, the period, the owner and the due date.
5. When that engagement is the working one, T15 governs the wording: its defined terms and vocabulary in every label, no term or code before the deck defines it, no abbreviations.
6. Expert sourcing (T36): the people needed (industries, companies, profiles), the data needed, the question bank and the data table template that screens experts for data, not views.
7. Account visits (T37): accounts grouped into trips, must-ask questions by segment and audience, and the pre-read with its sender and send-by date.
8. Input templates for analysts or build partners follow the same logic: every field is set by what the build must show.
9. Cover note: data framed constructively as the critical path to the next session; what we are already doing ourselves; draft numbers marked illustrative until the data lands.
10. Send the request first; the slide discussions it unblocks follow. Log each table in the hub's T35 table with owner, due date and status.

## Rules enforced here
- One file, at most two tabs; exact, compact fill-in tables; each table names the slides and initiatives it feeds; a dense multi-table layout is rebuilt, not trimmed [A6].
- No table without a slide it feeds; the slide's chart sets the table's design.
- Labels use the client's and the base deck's vocabulary, never informal or invented labels [A17]; tables ask for year-on-year as well as month-on-month wherever a slide shows a trend, and nothing is abbreviated [A18]; no term or initiative code appears before the deck defines it.
- Example rows show units and formats only, never invented figures.
- Data gaps are raised as the critical path, constructively, never as blame.

## Delegate
- Building the xlsx (two tabs, formats, validation lists, units in headers) to runner.
- The cover note and pre-read emails to drafter.
- If the storyline is not settled, /storyline first: the request follows the slides, not the reverse.

## Output
- The request file in `03-Work/<Engagement>/`, with "Data Request" in its file name so the guard checks the tab count, and the hub's T35 table updated.
- In chat: each table with the slides it feeds, its owner and due date, then the open questions.
- M1 no em dashes. M5 no invented figures in examples or pre-fills; a pre-filled value carries its source. M6 map to the latest deck version and say which.
