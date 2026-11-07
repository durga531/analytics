---
name: today
description: Writes the morning plan into the Plan section of today's daily note from Now.md, area status, yesterday's close, open tasks, reviews due, the inbox and the calendar, and returns a brief of at most 12 lines. Use when __OWNER__ says today, morning, plan my day or what's on.
model: __MID_MODEL__
effort: medium
context: fork
agent: drafter
argument-hint: <date, default today>
---
# /today
The Plan section of `02-Daily/YYYY-MM-DD.md` and a morning brief of at most 12 lines. Routing: mid tier, forked to drafter (daily rhythm).

## Read first
- `09-Reviews/Now.md`: this week's must-wins, deadlines and commitments, and what is parked.
- __OS_DIR__/active-areas.md: the Status line of every live area, with its dated next steps and anything waiting on __OWNER__.
- Yesterday's note, or the latest earlier note in `02-Daily/`: Tomorrow first, then Open loops and the actions logged in T5 (decision and action log) form.
- Open tasks in Tasks plugin format across the vault (skip `.obsidian`, `.claude` and `99-Archive`) with their due dates and the note each sits in; notes whose `review_on` is today or earlier; the item count in `01-Inbox/`.
- The calendar, when a calendar connector is connected; otherwise only meeting notes dated today in `03-Work/`.
- `.claude/rules/journal.md` and `08-Library/Templates/Daily.md`.

## Steps
1. Open today's note, or create it from the Daily template with the dates filled in. Write inside the Plan section only.
2. Must do: at most three items, each a step toward a Now.md must-win or a dated commitment, finishable today, verb first and ending with its done-test ("done when ..."), written as Tasks plugin tasks due today. A build item names the working file and the version it starts from.
3. Think about: one question for __OWNER__'s own thinking, drawn from an open decision, a must-win at risk or a review due. A question, never a task.
4. Meetings: time, who, the one outcome wanted, and a link to the meeting note; for a client session its prep is the T34 (talk track) section.
5. Reviews due: each note with `review_on` today or earlier, linked, with what the review tests. A thesis note is reviewed against its thesis-breaker datapoint under T10 (investment committee rules).
6. Carry-overs (added under Plan when any exist): open tasks from earlier daily notes and overdue tasks anywhere, linked where they sit and never copied, with their age in days since first planned. At day three each gets a proposed disposition: do (it becomes a must-do), delegate (to whom), schedule (to which date) or drop (cancelled with a reason). __OWNER__ confirms; /close applies the confirmed ones where each task sits.
7. If Now.md holds no must-wins, say so, plan from yesterday's Tomorrow and the dated commitments, and suggest /weekly.
8. When two engagements compete for the same slot, thinking-patterns.md records no rule for choosing between them: name the clash in one line and leave the call to __OWNER__.

## Rules enforced here
- Re-read, never recall: the plan comes only from files read in this run; nothing is carried over from an earlier session's memory, and a stale or missing file is named, never filled in [A16].
- Build on today's note as it stands, which may already carry __OWNER__'s own lines; never overwrite them, and merge the plan around them [C1].
- At most three must-dos, each finishable today with a done-test; anything bigger is cut to its first finishable step.
- No task is carried past day three without a disposition; a dropped task stays dropped.
- This skill writes the Plan section of today's note and nothing else: Now.md, active-areas.md and every other note change through /close and /weekly.

## Delegate
- Runs forked as drafter and delegates nothing further. The brief names the hand-offs: /ingest when the inbox is above ten items, /diagnose for a transcript waiting in a meeting note, /equity or /decide for a review due, /close tonight.

## Output
- The Plan section of today's note: Must do, Think about, Meetings, Reviews due and, when needed, Carry-overs.
- Return at most 12 lines: the must-dos with their done-tests, the question, meetings, reviews due, carry-overs needing a disposition, the inbox count, any clash, and "calendar not connected" when so.
- M1 no em dashes. M2 a thesis review is framed in the verdict vocabulary; no sell, trim or exit task is written. M5 no meeting, deadline or task is invented; what the files do not show stays out. M6 a build must-do names the file version it starts from.
