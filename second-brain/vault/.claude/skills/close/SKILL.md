---
name: close
description: Five-minute shutdown that writes Close in today's note, logs decisions and actions in T5 form, routes durable items to hubs, people notes and the lessons queue, and proposes status changes for approval. Use when __OWNER__ says close, wrap up, shut down or end of day.
model: __MID_MODEL__
effort: medium
argument-hint: <anything to add, dictated is fine>
---
# /close
The Close section of today's note, every durable item filed where it belongs, and a five-line reply. Routing: mid tier, main session (daily rhythm).

## Read first
- Today's note in `02-Daily/`: Plan (what was promised) and Log (__OWNER__'s own words).
- What changed today: this session's conversation, meeting notes and engagement hubs in `03-Work/`, and files modified today.
- `09-Reviews/Now.md` and `09-Reviews/Lessons Queue.md`.
- __OS_DIR__/templates.md: T5 (decision and action log).
- __OS_DIR__/active-areas.md: the Status line of every area touched today.
- __OS_DIR__/thinking-patterns.md: Closed debates.
- `.claude/rules/journal.md`; `work.md` and `people.md` in `.claude/rules/` before writing to a hub or a person note.

## Steps
1. Infer before asking: ticked must-dos, files written, messages sent, decisions recorded. Ask only what the record cannot answer, one or two questions at most; a dictated reply is fine.
2. Done: each finished item, linked to its file or note. An unfinished must-do moves to Open loops with its reason.
3. Decisions in T5 form: # | Decision | Implication for the build. Actions: Owner | Action | When. Anything unclear in a note or recording reads "[confirm]".
4. Corrections and lessons: each correction __OWNER__ gave today, quoted verbatim with its context, added to the lessons queue as a pending row by the /lesson procedure.
5. Open loops: __OWNER__'s own as dated tasks; other people's as waiting-on lines with a chase date. Carry-over dispositions __OWNER__ confirmed today are applied where each task sits: a new date, or cancelled with the reason.
6. Tomorrow: the first one to three moves, which /today reads first.
7. Route durable items: engagement decisions and actions to the hub's T5 tables in `03-Work/<Engagement>/`; facts, commitments and blessed wording (verbatim) to the person's note in `07-People/`; a transcript or stakeholder feedback is filed as received and flagged for /diagnose, never read for meaning here.
8. Areas that moved: propose one new Status line per area for active-areas.md, each with its source; apply only on __OWNER__'s approval.
9. Now.md: mark must-wins done and add new deadlines or commitments; change a must-win only when __OWNER__ said so today.

## Rules enforced here
- A removal the decision owner directed is recorded as a T5 decision naming exactly what was removed and by whom, so no later build carries its content forward [A15].
- A design rule given once binds every later build without being restated: any rule __OWNER__ stated today is staged through /lesson tonight, never left in the chat [A12].
- Build on today's note as it stands, which carries __OWNER__'s own edits: the Log and any text __OWNER__ wrote are never overwritten or reworded; Close goes in its own section [C1].
- Classify, file and log only: no diagnosis, analysis or rewording of what was said.
- A decision that cuts across a closed debate in thinking-patterns.md is logged as said and flagged; the debate stays closed until __OWNER__ reopens it.
- The six OS files change only on approval; Now.md, hubs, person notes and the queue are updated directly.

## Delegate
- A sweep of files changed today to runner when the day touched more than one engagement: paths, modified times and versions only.
- Transcripts and stakeholder feedback to /diagnose; corrections through /lesson; anything that may move an investment call to /equity.

## Output
- The Close section of today's note (Done, Decisions, Corrections and lessons, Open loops, Tomorrow), plus the hub, person-note, queue and Now.md updates routed above.
- Reply in five lines: done; decisions and actions logged; lessons queued; open loops; tomorrow's first move and any approval waiting.
- M1 no em dashes. M5 no decision, owner or date is invented; unclear items stay "[confirm]".
