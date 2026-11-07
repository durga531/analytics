---
name: workbook
description: Builds and fills formula-driven Excel workbooks and dashboards by script, recalculated headless with live checks, zero formula errors and a render check. Use when __OWNER__ says build the workbook, Excel for these slides, benchmark matrix, dashboard tab or fill this sheet.
model: __SMALL_MODEL__
effort: medium
argument-hint: <workbook purpose or file> [slides it feeds]
---
# /workbook
A formula-driven workbook (analysis, backing model, benchmark matrix, dashboard or data request) built and filled by script, recalculated clean and passing its own checks. Routing: small tier (recurring ask 6, build and filling); what to measure is designed by strategist, never on this tier.

## Read first
- Latest version of the workbook and of the deck or slides it feeds (M6); extend that version, never an older copy, and say which.
- `.claude/rules/work.md` when the workbook serves an engagement.
- __OS_DIR__/output-standards.md: Excel and data rules; Deck rules (Numbers and evidence) for anything a slide will cite; Anti-hallucination.
- __OS_DIR__/templates.md: T49 (benchmark workbook flow and practice test) for benchmark and workshop workbooks; T43 (number classes); T35 (data request workbook) when the file is a data request.
- __OS_DIR__/active-areas.md: the area the workbook belongs to (status, good output, rejected), including the level of detail the reader accepted.
- __OS_DIR__/thinking-patterns.md: Closed debates (a validated estimation method stays as validated; analyses already ruled out are not rerun).

## Steps
1. Confirm the design before building: the decision the workbook serves, its metrics, unit universe, scoring criteria and weights. If the request and the record leave any of these unsettled, stop and send the design to strategist (or ask __OWNER__); never invent the frame here.
2. Script the build in Python with openpyxl: raw tabs feed reference sheets, reference feeds helpers, helpers feed dashboards; inputs kept apart from formulas; a checks tab. A data request instead keeps to two tabs at most.
3. Write formulas, not pasted values, so every output traces to its raw rows; each row carries its source and its T43 class.
4. Build time series: year-on-year beside month-on-month wherever the data is periodic.
5. Benchmark and workshop workbooks follow the T49 flow and practice test: facts recorded, not scored; only capability scored, against written criteria; no evidence, no score, so a practice seen only in public disclosure stays unscored.
6. Use a new data cut only after its weights are reconstructed and validated against the published pack; re-derive a challenged number with a breakup and a source, or send it to /audit.
7. Live checks: totals tie, shares sum to 100%, row counts match the unit universe, every lookup resolves.
8. Recalculate headless with LibreOffice (`soffice --headless`), because openpyxl writes formulas without cached values; then scan every sheet. Zero formula errors (#REF!, #DIV/0!, #VALUE!, #NAME?, #N/A) is the only pass.
9. Render check: convert to PDF with soffice, render the pages with pdftoppm and read the images for truncated labels, cells showing ###, a broken header hierarchy and leftover placeholders.
10. Dashboards use the three-level hierarchy (ALL-CAPS chapter header, bold underlined sub-header, body) and connect their metrics into one reading.
11. When __OWNER__ asks for less detail, cut a short version from the same evidence rather than trimming cells.

## Rules enforced here
- A data-request workbook is one file with at most two tabs of compact, exact fill-in tables, each table naming the slides and initiatives it feeds; no dense multi-table sheet and no extra tab [A6].
- Every time-based metric shows year-on-year alongside month-on-month, as a time series rather than single points; no abbreviations in sheet names, headers or labels; the engagement's named template where one exists [A18].
- Pivot-level description is not analysis: a workbook that only cuts the data fails; the hypothesis, root cause and implication it must evidence come from strategist, and an inherited analysis is re-examined there from first principles before it is rebuilt here [A19].
- Dashboards never dump variables: they keep the few metrics that drive the decision and show how they interact (a combined index, a driver tree or a decision rule), so the reader gets one integrated answer [B1].
- Full coverage at the level the workbook claims: no threshold or floor that leaves most units unscored; any gap shows as a count, never hidden [B3].
- Every source column names the primary producer, never an aggregator, so a slide built on the workbook cites that producer and never the workbook or its tabs [B5].
- Formula-driven with live checks and zero formula errors before anything is delivered.
- No fake, illustrative or placeholder data; a missing value stays blank and flagged.

## Delegate
- What to measure (decision, metrics, unit universe, scoring criteria and weights) and any root-cause reading to strategist; __OWNER__ decides where strategist cannot.
- Large fills across many sources or tabs to runner, in parallel.
- A challenged figure to /audit; slides built on the workbook to /deck-build; a data request's table design to /data-request.

## Output
- The xlsx saved beside the latest version as the next version, in the engagement or build folder; a data request carries "Data Request" in its file name so the guard checks its tab count.
- In chat: the path, the tab flow in one line, check status (all pass, zero errors), the render check, coverage count and open gaps.
- M1 no em dashes in cells, labels or notes. M5 no fake or illustrative data. M6 build on the latest workbook and say which.
