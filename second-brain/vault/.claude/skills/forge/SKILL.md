---
name: forge
description: Runs the T2 maker-checker loop on an answer that matters, a draft graded by the critic on eight gates and revised only where it fails, at most three passes, then shows only the final answer and a CHECK footer. Use when a message starts with FORGE or __OWNER__ says forge this.
model: __TOP_MODEL__
effort: high
argument-hint: <the request>
---
# /forge
The T2 maker-checker protocol: a full draft, independent grading, targeted revision, and only the final answer shown. Routing: top tier (quality protocol); the critic agent grades on __CRITIC_MODEL__ as T2 sets.

## Read first
- __OS_DIR__/templates.md: T2 (maker-checker rubric, FORGE), its eight gates, the pass limit and the CHECK footer, read fresh on every run; T1 (executive answer structure), the shape the draft takes.
- __OS_DIR__/output-standards.md: Writing voice; Formatting bans; Anti-hallucination.
- __OS_DIR__/thinking-patterns.md: Challenge vs execution (a flawed premise is challenged, a set mandate is executed); Closed debates (never reopened as a counterargument).
- The domain skill and rules file the request falls under (for example /equity with invest.md, /storyline with work.md, /resume with career.md), and the latest version of any file the request touches (M6).

## Steps
1. Trigger: a message that starts with the FORGE prefix (the prompt hook flags it) or /forge with a request. Strip the prefix; the rest is the request.
2. When the request belongs to a domain skill, run that skill's Read first and rules inside the draft. This loop adds the checker; it never replaces the domain's rules or mandates.
3. Draft the full answer in T1 shape to `.claude/forge/DRAFT.md`, under a header with the request, the date and the pass number. Do not show it.
4. Send the draft and the request to the critic agent with T2. It returns each of the eight gates as PASS or FAIL with the exact failure, and never rewrites.
5. Revise only the items that failed; passing text stays as it is. Log the pass and the gate results in DRAFT.md.
6. Re-grade. Stop when every gate passes or after the third pass, whichever comes first.
7. Fix by gate, not by polish: a number without a source or confidence is sourced or cut, never caveated (gate 5); a flawed premise is named in the opening lines, not answered straight (gate 6); the strongest counterargument is stated and answered (gate 4); hedging, buzzwords and em dashes go (gate 8).
8. Show only the final answer, then the CHECK footer. If a gate still fails after the third pass, show the answer and name the gate and the gap; never present it as passed.

## Rules enforced here
- Descriptive, pivot-level analysis fails gates 2 to 4: the answer states a hypothesis, the root cause of the gap and its implication, strong enough to survive senior challenge, and inherited analysis is re-derived from first principles, never reused as is [A19].
- Critic grades and drafting notes are working notes: they never appear in the answer or in any deliverable (slide text, speaker notes, comments, document metadata); only the CHECK footer is shown [B6].
- Maker and checker stay separate: the critic never rewrites, and the maker never marks its own draft as passed.
- A mandate is executed, not debated: M2 to M4 are never offered as gate 4's counterargument, and closed debates stay closed.
- Three passes at most; no silent fourth pass, and no pass count presented as proof of quality.

## Delegate
- Gate grading to critic (T2), plus T3 (independent review brief) house rules when the answer is a deck, document or message.
- Facts the critic flags as unverifiable to runner, to validate or disprove with source and date.
- Domain sub-work to its own skill inside the draft step (for example data pulls for /equity).

## Output
- The final answer in T1 shape, with nothing about the loop above it.
- The CHECK footer, two lines: Assumptions (what the answer took as given) and Rejected framings (the framings considered and set aside). When a gate is unresolved, one more line names the gate and the gap.
- `.claude/forge/DRAFT.md` keeps the last run's draft and grades for audit; nothing from it is pasted into a deliverable.
- M1 no em dashes (gate 8). M5 nothing fabricated; unverifiable claims are cut (gate 5). M2, M3, M4 and M6 apply whenever the request is equity, a client deck, a resume or a build.
