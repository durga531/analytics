---
name: learn
description: Turns a book, article, lecture, podcast or idea into atomic linked notes with evidence, source and the strongest counter-argument, or tutors __OWNER__ by testing application. Use when __OWNER__ shares a source, says I learned, explain, teach me, or connect this.
model: __MID_MODEL__
effort: high
argument-hint: capture <source> | tutor <topic> | connect <idea>
---
# /learn
Durable knowledge: one claim per note, sourced at the primary producer, linked into what __OWNER__ already knows. Routing: mid tier (knowledge capture; not a numbered recurring ask).

## Read first
- `.claude/rules/learn.md`.
- Existing notes on the same claim or source in the matching topic folder and `06-Learn/`; search before writing, and update the latest version of a note rather than duplicating it.
- `08-Library/Templates/Learning Note.md`.
- __OS_DIR__/identity.md: Interests, to place a note and choose examples that land.
- __OS_DIR__/thinking-patterns.md: Frameworks I keep reaching for, to connect new ideas to the ones in use.
- __OS_DIR__/output-standards.md: Anti-hallucination; Numbers and evidence (primary producers, time series).
- __OS_DIR__/templates.md: T1 (executive answer structure) for explanations; T43 (number classes) for any figure kept in a note.

## Steps
### Capture
1. Pin the source: author, title, date, edition, and page or timestamp. When __OWNER__ shares a summary, trace each claim to its primary producer before citing it.
2. Keep only the ideas worth keeping: one idea per note, the claim as the title, in __OWNER__'s words where given.
3. Fill the Learning Note template: claim, evidence, source, strongest counter-argument, so-what (for the work, the portfolio or life), at least two links.
4. File in the existing topic folder that matches, else `06-Learn/`; create or update the source hub in `06-Learn/Sources/` linking every note.
5. Mark contested history, interpretation and economics as contested, with the main competing reading; keep fact, the author's argument and labelled inference apart.
6. Numbers: a series over a single point where one exists; each figure with source, date and its T43 class.
7. Complete capture, when asked for everything (a course, every chapter, a manual-style digest): one entry per source item in source order, then the count check.
### Tutor
8. __OWNER__ explains first. Find the gaps and misconceptions and explain only those, each with one concrete example; test with two or three application questions, not recall; offer to capture what stuck.
### Connect
9. Find the closest existing notes; say whether the new idea extends, contradicts or reframes each one; propose the links; name any clash with a framework __OWNER__ already uses.

## Rules enforced here
- Cite the primary producer of every claim and figure, never an aggregator, summary site or repackager; trace each one to its original publisher before citing it [B5].
- A complete capture covers every source item one by one, in source order, with nothing skipped, merged or summarised away; before delivery, the count of source items is checked against the count of entries written [C3].
- Never fabricate a quote, page number or citation; a quote that cannot be checked against the source is cut, not caveated.
- Atomic notes: a note carrying two claims is split; a near-duplicate is merged into the existing note.

## Delegate
- Fetching sources, transcripts and page references to runner, each returned with its link or page and date.
- Vault sweeps for near-duplicates and link candidates to runner; the connect judgement stays here.

## Output
- In chat: the notes created or updated, one line each (claim and folder), any contested flags, and for a complete capture the count line (source items, entries written).
- Explanations in T1 shape: the answer first, then the logic, the one caveat, the so-what.
- M1 no em dashes. M5 nothing fabricated; "I do not have reliable data on this" where the source is silent.
