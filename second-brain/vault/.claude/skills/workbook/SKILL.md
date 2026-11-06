---
name: workbook
description: Builds formula-driven Excel workbooks, backing models and dashboards with live checks, zero formula errors, evidence-based scoring and full coverage. Use when __OWNER__ says build the workbook, Excel for these slides, benchmark matrix, dashboard tab or fill this sheet.
model: __MID_MODEL__
effort: medium
argument-hint: <workbook purpose or file> [slides it feeds]
---
# /workbook
A formula-driven workbook (analysis, backing model, benchmark matrix or dashboard) that recalculates clean and passes its own checks. Routing: mid tier (recurring ask 6, build); filling on runner; what to measure is a top-tier call.

## Read first
- Latest version of the workbook and of the deck or slides it feeds (M6); extend that version, never an older copy, and say which.
- __OS_DIR__/output-standards.md: Excel and data rules; Deck rules (Numbers and evidence) for anything a slide will cite; Anti-hallucination.
- __OS_DIR__/templates.md: T49 (benchmark workbook flow and practice test) for benchmark and workshop workbooks; T43 (number classes).
- __OS_DIR__/active-areas.md: the area the workbook belongs to (status, good output, rejected), including the level of detail the reader accepted.
- __OS_DIR__/thinking-patterns.md: Closed debates (a validated estimation method stays as validated; analyses already ruled out are not rerun).

## Steps
1. Settle what to measure first: the decision the workbook serves, its metrics and its unit universe. If that is open, stop and take it to __OWNER__ or strategist; never invent the frame.
2. Lay out the flow one way: raw tabs feed reference sheets, reference feeds helpers, helpers feed dashboards; inputs kept apart from formulas; a checks tab.
3. Write formulas, not pasted values, so every output traces to its raw rows; each row carries its source and its T43 class.
4. Build time series: year-on-year beside month-on-month wherever the data is periodic.
5. Benchmark and workshop workbooks follow the T49 flow and practice test: facts recorded, not scored; only capability scored, against written criteria; no evidence, no score, so a practice seen only in public disclosure stays unscored.
6. Use a new data cut only after its weights are reconstructed and validated against the published pack; re-derive a challenged number with a breakup and a source, or send it to /audit.
7. Live checks: totals tie, shares sum to 100%, row counts match the unit universe, every lookup resolves.
8. openpyxl writes formulas without cached values, so recalculate headless (soffice) before reading any value back; then scan every sheet. Zero formula errors (#REF!, #DIV/0!, #VALUE!, #NAME?, #N/A) is the only pass.
9. Dashboards use the three-level hierarchy: ALL-CAPS chapter header, bold underlined sub-header, body.
10. When __OWNER__ asks for less detail, cut a short version from the same evidence rather than trimming cells.

## Rules enforced here
- Year-on-year as well as month-on-month, time series over point data, no abbreviations in sheet names, headers or labels, and the engagement's named template where one exists [A18].
- Full coverage at the level the workbook claims: no threshold or floor that leaves most units unscored; any gap shows as a count, never hidden [B3].
- Every source column names the primary producer, never an aggregator, so a slide built on the workbook cites that producer and never the workbook or its tabs [B5].
- Formula-driven with live checks and zero formula errors before anything is delivered.
- No fake, illustrative or placeholder data; a missing value stays blank and flagged.

## Delegate
- Data entry, filling, recalculation, the error scan and rendering to runner.
- What to measure, scoring criteria and weights to strategist or __OWNER__.
- A challenged figure to /audit; slides built on the workbook to /deck-build.

## Output
- The xlsx saved beside the latest version as the next version, in the engagement or build folder.
- In chat: the path, the tab flow in one line, check status (all pass, zero errors), coverage count and open gaps.
- M1 no em dashes in cells, labels or notes. M5 no fake or illustrative data. M6 build on the latest workbook and say which.
