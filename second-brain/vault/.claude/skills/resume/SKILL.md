---
name: resume
description: Tailors the one-page resume, cover letter or application answers to a named role from the locked fact base, after a fit call on whether to apply. Use when __OWNER__ pastes a job description or says tailor my resume, CV for this role, cover letter or fix these bullets.
model: __MID_MODEL__
effort: high
argument-hint: <job description or role> [base version] [text or docx]
---
# /resume
A one-page resume, cover letter or set of application answers for one role, selected and reframed from the locked fact base, as plain text in chat or a rendered docx. Routing: mid tier (recurring ask 1, drafting); the fit call runs on strategist and the file build on runner.

## Read first
- The job description and the latest resume version __OWNER__ shared or edited for this kind of role (M6); say which file and date you build on.
- `.claude/rules/career.md`: it loads only when a resume file is touched, so read it here.
- __OS_DIR__/output-standards.md: Resume rules, the primary source (one page with no whitespace at the bottom, two-zone bullet lengths, the summary sentence, header and bullet roles, anti-AI tells, cover letters, the kill-list claims); Writing voice; Formatting bans.
- __OS_DIR__/templates.md: T50 (resume architecture and fact base) for structure, the locked numbers and the build notes.
- __OS_DIR__/identity.md: Roles and employers and Education for titles and dates only. The fact base wins over identity.md and every other file on every number and contact field, the header block's phone and email included.
- __OS_DIR__/active-areas.md: Job transition (status, good output, rejected).

## Steps
1. Fit call first, delegated to strategist with the job description and the fact base: a real chance or not, which base version to start from, which experience to foreground, the gap in one line. Skip it only when the call for this role is already on record in its application note. A no is reported plainly and nothing is drafted.
2. Map the job description to the record: the few things the role is buying, each matched to fact-base evidence or flagged as a gap.
3. Use the format the fit call names: capability-labelled headers for consulting laterals, flat bullets for tech recruiters.
4. Select and order from the fact base; vary order and emphasis by role, never the numbers. Echo the job description's language adjacently, never mirror it.
5. Summary: one complete sentence, implied third person, past-tense verbs, no pipes.
6. Headers carry outcome and scale; bullets carry mechanism and secondary numbers and never repeat the header's figure. Outcome first, mechanism second; one connective per bullet, never two; bold only for metrics and key nouns; black and white and ATS-clean.
7. Every bullet sits in one of the two zones Resume rules set (one full line or two full lines); the middle zone is dead, and no bullet ends with one or two orphan words on a new line.
8. Strip AI tells: uniform bullet shapes, hedged ownership verbs, self-scoring commentary, symmetry for its own sake.
9. Cover letters when asked: two to three bullets in one strong version, with no manufactured intersections and no competency __OWNER__ cannot defend. Application answers: first person, specific, fact-base numbers only. After three rewrites that miss, ask __OWNER__ for a dictated account before a fourth.
10. Text asked for: plain text in chat and no file. File asked for: runner builds the docx per T50, renders it and confirms one page, no bottom whitespace and no orphan words; reshape and rerun until it passes.

## Rules enforced here
- M4: numbers only from the locked fact base; kill-list claims never return, whether they come from old files, other tools or memory; ownership verbs follow the role framing the fact base locks.
- One page, strict, with no whitespace at the bottom, per output-standards.md Resume rules (the primary source). Cross-reference [A11]: content fills the page so the impact lands; judged on the rendered page, any empty region fails QA and is reworked before delivery.
- The independent work section credits data __OWNER__ collected, scraped or verified as __OWNER__'s own primary work, never as supplied, third-party or vendor data [B4]. An own model is described only by its public-description rules (T46, outlet-density model method).
- Before any edit, open the latest resume version and every input __OWNER__ has shared, state which file and version the work is built on, never build on an older copy, and ask once if the latest cannot be identified [A7].
- Private instructions, reviewer personas, thinking-direction notes and working notes never appear in the resume text, comments or document properties; strip them before delivery [B6].
- Honest gap flags; no inflated claim, no keyword stuffing, no job-description mirroring.
- Change only the bullets or sections named; a line __OWNER__ finalised stays final unless reopened.

## Delegate
- The fit call to strategist (top tier).
- The docx build, word counts per bullet, PDF conversion and the one-page render check to runner, scripted per T50's build notes.
- Interview and case prep for the role to /interview; the cover message or cold note to /outreach.

## Output
- Text asked for: plain text in chat, summary first, then headers and bullets in final order, then gap flags in one block.
- File asked for: `05-Self/Career/<Company> <Role> Resume.docx` and its PDF, delivered only after `python3 .claude/hooks/guard.py lint <file> --resume` returns no BLOCK.
- The fit call, the base version and the file paths logged in `05-Self/Career/<Company> <Role>.md`.
- M1 no em dashes. M4 fact-base numbers only; kill-list claims never return; the fact base wins on every number and contact field. M5 never invent a number, role, award or outcome; "I do not have reliable data on this". M6 build on the latest resume version and name it.
