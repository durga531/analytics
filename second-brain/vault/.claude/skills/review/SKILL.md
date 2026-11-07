---
name: review
description: Reviews __OWNER__'s own deck, workbook, model, manual, resume or message read-only against the full correction set; returns a verdict with must fix and should fix tables. Use when __OWNER__ says review this, check the deck, is this ready, partner test it, or before sending.
model: __CRITIC_MODEL__
effort: high
context: fork
agent: critic
argument-hint: <file path> [previous version] [engagement]
---
# /review
A verdict and exact fixes on __OWNER__'s own deliverable, graded cold and never edited. Routing: critic tier (quality gate before anything leaves, on recurring asks 1, 2, 6, 7, 10 and 20).

## Read first
- The deliverable at its latest version (M6) and, for a deck, its previous version; name both files and dates. For pptx, docx or xlsx, extract text and notes, render to PDF and page images in a temporary folder outside the vault when possible, and read every image.
- `.claude/rules/work.md` (and `.claude/rules/career.md` for a resume or outreach message): path-scoped rules load only when a matching file is touched, so read them here.
- __OS_DIR__/output-standards.md: Formatting bans; Deck rules (every subsection); Excel and data rules or Resume rules when the file is one; Anti-hallucination; all three verbatim-correction lists in full, [A1] to [A20], [B1] to [B11] and [C1] to [C5].
- __OS_DIR__/templates.md: T3 (independent review brief) house rules and output format; T13 (deck intake and cardinal rules) title, bullet and banned-word rules; T15 (engagement deck rule set) when the file belongs to that engagement; T18 (template operating system) QA gates only when that template is the working template, never by default.
- __OS_DIR__/active-areas.md: the area the deliverable belongs to, above all what was rejected.
- The request being answered, the engagement hub with its T5 (decision and action log), and `03-Work/<Engagement>/<Engagement> Review Log.md`: open items and earlier findings, so nothing is raised twice.

## Steps
1. Name the deliverable type and load its tags from the full set. Every type: [A7] [A10] [A16] [B6] [B11]. Deck: [A1] to [A5], [A8] [A9], [A11] to [A15], [A17] to [A20], [B1] [B2] [B4] [B5] [B7] [B8] [B10], [C1] [C2] [C4] [C5]. Workbook: [A6] for a data request, [A15] [A18] [A19] [B1] [B3] [B5]. Model or product: [A11] [A19], [B1] to [B5], [B7] to [B10]. Manual: [C3]. Message: [A13] when client-facing, [B4] [B5]. Resume: the Resume rules with [A11].
2. Judge the file as found, with no build context. Read the titles alone in order: one argument, one message per slide, each executive summary line backed by a page.
3. Walk every slide, page or sheet against the tags loaded and the rules below, then the T3 house rules in full.
4. For a deck, run `python3 .claude/tools/deck_diff.py <file> <previous version>` (new file first) and set every changed, added or removed slide against the request.
5. Run the template's QA (the T18 QA gates when that template is in use) and `python3 .claude/hooks/guard.py lint <file>` (add `--resume` for a resume); fold each BLOCK and WARN into the findings.
6. Trace every figure to a source or its validation tag and redo the arithmetic and units; an unverifiable claim is flagged to cut, never to caveat.
7. List every change and input the request named and mark each made or missing.
8. Grade each finding per T3: must fix breaks a rule, a mandate or a fact; should fix lifts impact. Never rewrite the deliverable.

## Rules enforced here
- Final deck: no what-changed, what-moved or what-goes-where slides, new tags or version notes; every slide justifies its place to a partner reading it cold [A1].
- Built on the most recent file __OWNER__ shared, with __OWNER__'s edits intact; headers read in sequence as one compelling, flowing storyline [C1].
- Only the requested slides changed, finalised slides included; any other change in the deck_diff list is must fix [A10]. The agreed architecture (levers, house, sections) is intact; an unagreed structural change is must fix [A14].
- A slide the decision owner removed stays removed and its content is not carried forward (check the T5 log); calculations and units (per-unit basis, denominators) are re-checked on every numeric slide or sheet [A15].
- Framed at the level of the overall programme; no single playbook or workstream crowds out the programme story [A20].
- Executive-summary lines are precise, client-credible and make sense read alone; a slogan, colloquial or sweeping line is must fix [A4]. No value figure or committed range leads the executive summary, a section or an initiative [A5].
- One definition per metric on a chart, never two versions of the same measure; the template's chart grammar, with a value label above each bar or a stacked bar, one number per bar [A2].
- Key insights are clean, complete sentences stating a non-obvious implication, one or two numbers at most [A3].
- Less text, more visual, dense with impact [A8]; no excess whitespace on a slide or at the foot of a resume page [A11]. Our-play pages are never text-only [A9].
- Scheme slides show the design, not rates; rates read "set at pilot" and illustrative rates sit in the appendix [A12].
- No extreme or absolute words that would put the client on the defensive; slides __OWNER__ finalised match the finalised version unless reopened [A13].
- Base-deck vocabulary, each informal or folksy word flagged with its base-deck replacement [A17]. Year-on-year shown alongside month-on-month; no abbreviations in slide text [A18].
- No variable or metric dumps: the few drivers that decide, shown interacting [B1]. Sources in subscript, footnote or hover, never in a headline or the body flow [B2]. Each source names the primary producer, never an aggregator, the workbook or its tabs [B5].
- No private instructions, reviewer personas or notes to the assistant anywhere in the file, speaker notes and file properties too [B6].
- Built on the latest file and every input shared, never an older copy, with the project's memory and preferences on words, focus and formats applied [A7] [A16].
- A data request is one file of at most two tabs, with compact, exact fill-in tables that each name the slides and initiatives they feed [A6].
- Analysis states its hypothesis, root cause and implication; pivot-level description is must fix [A19]. A model covers the full universe at the level it claims; a coverage floor that leaves most units unscored is must fix [B3].
- Data __OWNER__ collected or built is credited as __OWNER__'s own work, never as supplied or third-party [B4]. Each view or layer has its own discernible colour [B7].
- The file opens without a repair prompt; a corrupted slide is rebuilt from the template package and shared alone [C2]. A manual covers every source item in order, none skipped or merged, with a count against the source [C3].
- No pasted screenshots of other decks; reference visuals are recreated natively in __OWNER__'s template and style [B8]. Map layers register exactly on the base outline, checked on the render [B10].
- Every change and input the request named is made; list each with where it landed, and a missing one is must fix [B11].
- Every slide comes from the template and respects its chain of command; lookalike elements and off-template layouts are must fix [C4]. Template slide structure unchanged: content customised only, new slides cloned from template slides [C5].

## Delegate
- Nothing inside this fork: the critic grades and never rewrites. The main session routes fixes: wording to /lexicon, slide mechanics to /deck-build, storyline or initiative logic to /storyline or /initiative, resume lines to /resume.

## Output
- Line one: READY or NOT READY, with the count of must fix and should fix items.
- A must fix table, then a should fix table: Location | Offending text | What is wrong | Exact fix; each row names its correction tag or mandate.
- The deck_diff changed-slide list set against the request, and the requested-change checklist, each item made or missing.
- The same rows in the review-log columns (date, file, location, offending text, what is wrong, exact fix, severity, status open) for the main session to append to the engagement's review log; this fork writes nothing.
- M1 an em dash is must fix. M3 any version language is must fix. M4 on a resume or outreach message, a number outside the locked fact base or a kill-list claim is must fix. M5 an unsourced or unverifiable figure is must fix: cut, not caveated. M6 review the latest version and name it.
