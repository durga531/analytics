---
name: interview
description: Prepares interviews and cases for a role (fit call, STAR story bank, case drills, writing samples, a mock that pushes back), numbers only from the locked fact base. Use when __OWNER__ says interview prep, case prep, mock me, story bank, should I apply or which CV to send.
model: __TOP_MODEL__
effort: high
argument-hint: <company and role, or job description> [round or case type] [mock]
---
# /interview
Interview-ready material for one role: the fit call, a story bank mapped to what each round tests, case drills and a mock that pushes back, every number traceable to the locked fact base. Routing: top tier (recurring ask 9, and the fit call in ask 1).

## Read first
- The job description, recruiter or interviewer notes, the latest resume sent for this role and `05-Self/Career/Story Bank.md`, newest versions (M6); say which you use.
- `.claude/rules/career.md`: it loads only when a resume file is touched, so read it here.
- __OS_DIR__/templates.md: T55 (case interview framework); T50 (resume architecture and fact base) for the locked numbers, the role framing and __OWNER__'s own builds; T1 (executive answer structure) for the fit call.
- __OS_DIR__/output-standards.md: Resume rules (locked fact base, kill-list claims, writing samples, anti-AI tells); Anti-hallucination; Writing voice.
- __OS_DIR__/identity.md: role titles and dates only, from Roles and employers and Education; Ambitions informs the fit call and never supplies resume content. The fact base wins over identity.md and every other file on every number and contact field.
- __OS_DIR__/active-areas.md: Job transition (status, good output, rejected).
- __OS_DIR__/thinking-patterns.md: Challenge vs execution (high-stakes cases are clarified before answering; weak fits are told no).

## Steps
1. Fit call, when __OWNER__ asks whether to apply or which version to send: answer first in T1 shape with a real chance or not and the reason, the base version and format to start from, the experience to foreground and the gap in one line. A weak fit gets a plain no. Drafting goes to /resume.
2. Decode the role: what each round tests, the competencies or principles the company publishes, and the questions that follow. Facts come from runner with source and date; anything unconfirmed is marked to verify, never guessed.
3. Story bank: one STAR story per competency, built only from the record: __OWNER__'s own action, the mechanism, and the result with its fact-base number. Missing detail is a [FILL] marker for __OWNER__; any claim not yet checked against the fact base carries [VERIFY]. Spread the stories so no single project carries the interview.
4. Cases: use only T55's recorded structure, issue trees across the problem-statement types it lists, then ask, validate, answer. The body of T55 is not on record; say so plainly, and label any framework built past that structure "new for this case".
5. Case fact base: every market or company fact with its source, date and a confidence tag; a gap reads "I do not have reliable data on this", never a plausible number.
6. Writing samples: Situation, Approach, Impact; first person singular throughout (I, never we); numbers in every sample, from the fact base only; customer impact leads.
7. Mock mode on request: one question at a time as a sceptical interviewer; push back on vague, unquantified or we-led answers; after each answer give the verdict, the gap and a stronger version; close with the three weakest answers to drill again.
8. Gap flags: each requirement the record cannot evidence is named with an honest bridge, never papered over. When an answer still sounds rehearsed after two rewrites, ask __OWNER__ for a dictated account before drafting again.

## Rules enforced here
- M4: numbers only from the locked fact base; kill-list claims never return in stories, samples or mock answers; vary order and emphasis by role, never the numbers; ownership verbs follow the role framing the fact base locks.
- Every case answer states a hypothesis, the root cause of the gap and its implication, able to survive senior challenge; descriptive, pivot-level analysis is rejected, and inherited analysis is re-examined from first principles, never reused as is [A19].
- An issue tree keeps the few drivers that decide the case and shows how they interact (driver tree, combined index or decision rule), so the interviewer gets one integrated answer, never a dump of variables or metrics [B1].
- Data __OWNER__ collected, scraped or verified is credited in stories and samples as __OWNER__'s own primary work, never as supplied, third-party or vendor data [B4].
- Each case fact cites its primary producer, traced to the original publisher, never an aggregator or intermediary that repackages it [B5].
- No invented story, outcome, interviewer or question attributed to a company; what cannot be verified is cut, not caveated.
- On a high-stakes case, clarify before answering: one or two questions, only where the answer changes the output.

## Delegate
- Company, role and round research to runner: each fact with source and date.
- First drafts of STAR stories and writing samples to drafter, briefed with the fact base and the story slots; the selection, the framing and the mock stay here.
- Resume or cover letter changes the prep exposes to /resume; thank-you and follow-up notes to /outreach.
- A final-round story bank to critic for the T2 (maker-checker rubric) gates before the day.

## Output
- `05-Self/Career/<Company> <Role>.md` (type application): the fit call, the round map, case drills with their fact base, gap flags and the drill list, linking the stories used.
- `05-Self/Career/Story Bank.md`: STAR stories and writing samples with their markers. Run `python3 .claude/hooks/guard.py lint "05-Self/Career/Story Bank.md" --resume` and fix every BLOCK; case facts are not linted this way, since market figures are not resume numbers.
- In chat: the fit call or the next drill first, then the paths.
- M1 no em dashes. M4 fact-base numbers only; kill-list claims never return; the fact base wins on every number and contact field. M5 never invent a number, source, quote or case; "I do not have reliable data on this". M6 build on the latest resume and story bank, and name them.
