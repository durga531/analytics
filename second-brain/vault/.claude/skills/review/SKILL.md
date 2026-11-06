---
name: review
description: Reviews __OWNER__'s own deck, resume or workbook read-only before it goes out and returns a verdict with must fix and should fix tables. Use when __OWNER__ says review this, check the deck, is this ready, partner test it, or before anything is sent.
model: __CRITIC_MODEL__
effort: high
context: fork
agent: critic
argument-hint: <file path> [engagement]
---
# /review
A verdict and exact fixes on __OWNER__'s own deliverable, graded cold and never edited. Routing: critic tier (quality gate on recurring asks 1, 2 and 6).

## Read first
- The deliverable at its latest version (M6); name the file and date reviewed. For pptx, docx or xlsx, extract text and notes, render to PDF and page images in a temporary folder outside the vault when possible, and read every image.
- __OS_DIR__/output-standards.md: Formatting bans; Deck rules (every subsection); Resume rules or Excel and data rules when the file is one; Anti-hallucination; the three verbatim-correction lists.
- __OS_DIR__/templates.md: T3 (independent review brief) house rules and output format; T18 (template operating system) QA gates; T13 (deck intake and cardinal rules) title, bullet and banned-word rules.
- __OS_DIR__/active-areas.md: the area the deliverable belongs to, above all what was rejected.
- The engagement hub and `03-Work/<Engagement>/<Engagement> Review Log.md`: open items and earlier findings, so nothing is raised twice.

## Steps
1. Judge the file as found, with no build context. Read the titles alone in order: one argument, one message per slide, each executive summary line backed by a page.
2. Walk every slide, page or sheet against the rules below, then the T3 house rules: headline limits, extreme words, terms or IDs before definition, version language, traceable figures, verbatim quotes, cross-slide consistency, competition-law guardrails.
3. Run the T18 QA gates: story, structure, charts, hygiene.
4. Run `python3 .claude/hooks/guard.py lint <file>` (add `--resume` for a resume) and fold each BLOCK and WARN into the findings.
5. Trace every figure to a source or its validation tag; an unverifiable claim is flagged to cut, never to caveat.
6. Grade each finding: must fix breaks a rule, a mandate or a fact; should fix lifts impact. Never rewrite the deliverable.

## Rules enforced here
- Final deck: no what-changed or where-it-moved slides, new tags or version notes; every slide justifies its place to a partner reading it cold [A1].
- One metric definition per chart, in the template's chart grammar: percentages on top of bars or stacked bars [A2].
- Key insights are clean complete sentences with at most one or two numbers [A3].
- Less text, more visual, dense with impact [A8]; no excess whitespace on a slide or at the foot of a resume page [A11].
- Our-play pages are never text-only [A9].
- Scheme slides show the design, not rates; rates read "set at pilot" and illustrative rates sit in the appendix [A12].
- No extreme or absolute words; slides __OWNER__ finalised are unchanged from the finalised version unless reopened [A13].
- Base-deck vocabulary; each informal or folksy word is flagged with its base-deck replacement [A17].
- Year-on-year shown alongside month-on-month; no abbreviations in slide text [A18].
- No private instructions, reviewer personas or notes to Claude anywhere in the file, speaker notes too [B6].
- Every slide comes from the template and respects its chain of command; lookalike elements and off-template layouts are must fix [C4].

## Delegate
- Nothing inside this fork: the critic grades and never rewrites. The main session routes fixes: wording to /lexicon, slide mechanics to /deck-build, storyline or initiative logic to /storyline or /initiative, resume lines to /resume.

## Output
- Line one: READY or NOT READY, with the count of must fix and should fix items.
- A must fix table, then a should fix table: Location | Offending text | What is wrong | Exact fix.
- The same rows in the review-log columns (date, file, location, offending text, what is wrong, exact fix, must or should, status open) for the main session to append to the engagement's review log; this fork writes nothing.
- M1 an em dash is must fix. M3 any version language is must fix. M4 on a resume, a number outside the locked fact base or a kill-list claim is must fix. M5 an unsourced or unverifiable figure is must fix: cut, not caveated. M6 review the latest version and name it.
