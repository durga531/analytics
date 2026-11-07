---
name: fitness
description: Reads scan, weigh-in and lift data as trends and returns an evidence-graded memo with this week's changes to training, protein and recovery, never weight loss as the goal. Use when __OWNER__ shares a scan, lift log, form video or progress photo, or asks am I on track.
model: __MID_MODEL__
effort: medium
argument-hint: <scan, log, photo or question> [period]
---
# /fitness
An executive memo on training, physique and recovery built from __OWNER__'s own numbers, with next week's targets. Routing: mid tier (recurring ask 13).

## Read first
- `.claude/rules/self.md`.
- The latest logs in `05-Self/` (lift log, weigh-ins, waist, scan reports, photos) with their dates; say which dates the read is built on (M6).
- __OS_DIR__/active-areas.md: Personal, the training and physique area (status, current numbers and targets, good output, rejected).
- __OS_DIR__/templates.md: T1 (executive answer structure).
- __OS_DIR__/output-standards.md: Writing voice (executive memo); Anti-hallucination.
- __OS_DIR__/thinking-patterns.md: time series over single points.

## Steps
1. Load the current numbers and targets from the area and the latest logs. A number found in neither is asked for, never assumed.
2. Turn readings into trends: bodyweight as a rolling seven-day average, waist as a weekly series, each compound lift as a series of top sets. One reading never moves the plan.
3. Compare a composition scan only with earlier scans taken the same way (device, time of day, hydration, food and training beforehand); name any difference that breaks the comparison.
4. Photos and form videos: comment only on what the frame shows; flag angle, lighting, distance or pump that makes a conclusion unsafe, and ask for a standard re-take.
5. Training: progressive overload on the compound lifts; next week's targets as load, reps and sets per lift. When a lift stalls for two to three weeks, change volume, rest or schedule a deload before adding exercises.
6. Nutrition: protein against the daily range the area records, checked as a weekly average; the eating pattern on record is worked with, not replaced.
7. Supplements, skin and hair: graded like everything else; prescriptions, lab values, pain and injury go to a qualified professional.
8. Grade each recommendation strong, moderate, weak or anecdotal, and name the evidence type behind it.
9. Where a coach's programme exists, the memo sits beside it: flag conflicts, never override it.

## Rules enforced here
- Never weight loss as the goal: the target is the composition and strength numbers the area sets; scale weight is read only beside waist and lifts.
- Executive memo, not generic advice: every line ties to __OWNER__'s own numbers or names the missing data.
- Trends over points: no conclusion from a single weigh-in, scan, photo or session.
- Cite the primary producer of every claim (the trial, meta-analysis or position stand), never a blog, video or aggregator that repackages it; trace each figure to its original publisher before citing it [B5].
- No diagnosis; health particulars stay in 05-Self and never enter __OS_DIR__.

## Delegate
- Evidence lookups (a supplement, a protocol, a claim from a video) to runner, each returned with the primary source and its date.
- Charting or averaging a long log to runner as a script over the note table or CSV.

## Output
- T1 memo: the bottom line in one sentence; a table Metric | Last four weeks | Seven-day average or latest | Target | Read; this week's changes (training, protein, recovery, sleep); the one risk; the so-what.
- A dated check-in note in `05-Self/` holding the table. A change to the area's numbers or targets in active-areas.md is proposed through /close or /weekly and applied only on approval.
- M1 no em dashes. M5 no invented study, effect size or number; "I do not have reliable data on this" where the evidence is thin. M6 say which log dates the read uses.
