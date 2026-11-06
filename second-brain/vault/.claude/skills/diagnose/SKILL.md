---
name: diagnose
description: Turns transcripts and stakeholder feedback into a root-cause diagnosis, a decision and action log and the fixes to slides, inputs and structure. Use when __OWNER__ pastes a partner or client transcript or says diagnose this call, why these comments or what do we fix.
model: __TOP_MODEL__
effort: high
argument-hint: <transcript, notes or file> [engagement]
---
# /diagnose
A root-cause diagnosis (T4) and a decision and action log (T5) from transcripts and stakeholder inputs, with the fixes they drive. Routing: top tier (recurring ask 8).

## Read first
- Latest version of the deck or file the comments refer to, plus this engagement's previous diagnosis if one exists (M6); state which version the comments are read against.
- __OS_DIR__/output-standards.md: Deck rules (Deck type and scope; Storyline and headers; Numbers and evidence; Process), Anti-hallucination, and the first verbatim-corrections list.
- __OS_DIR__/templates.md: T4 (stakeholder feedback diagnosis), T5 (decision and action log), T38 (internal update to the partner), T39 (client cover note).
- __OS_DIR__/active-areas.md: the engagement's area (status, good output, rejected), so a repeat of an earlier rejection is named as a repeat.
- __OS_DIR__/identity.md: Current working context, to place each speaker as partner, internal team or client.
- __OS_DIR__/thinking-patterns.md: Challenge vs execution; Closed debates (one raised again is logged and flagged, never reopened).

## Steps
1. Transcribe faithfully. Translate Hindi-English into plain English without smoothing; keep the original wording beside any line that may be quoted. Speaker labels are unreliable: attribute from content and context. Unclear audio or an uncertain speaker reads "[confirm]". Never fill a gap with a guess; never comment on transcription quality.
2. Put every comment in the T4 comment register, attributed, with why it matters, its fix and the input it needs. Nothing heard is dropped.
3. Read for root causes: why each comment arose and what in the structure, the inputs or the slides must change. Group comments under the few causes that explain them; each cause cites its evidence in the calls.
4. Split partner direction from client feedback. Direction is executed as given, blessed wording verbatim; feedback is diagnosed.
5. Recompute every number a comment touches and confirm its unit before proposing a fix.
6. Draft T4 in full: bottom line, root causes, comment register, structural changes, evidence pages, risks to the current picks, inputs to request, agreed next steps.
7. Draft T5: decisions with their implication for the build, what the client liked, templates agreed, workstreams, actions with owner and date, open items marked "[confirm]".
8. A structural change that touches agreed architecture is proposed with its reasoning and waits for __OWNER__'s approval.
9. When asked, draft T38 for the partner and T39 for the client from the agreed diagnosis.

## Rules enforced here
- Partner direction is executed exactly: a slide or item marked for removal is removed and nothing else; its content is never carried forward onto another slide; every calculation and its unit, per-unit basis included, is rechecked before the fix is called done [A15].
- Diagnose why, not only what: a pivot-level description that restates cuts of the data is not insight; each root cause names the mechanism behind the comment and the change it forces, at a level that survives a senior partner's challenge [A19].
- Hold the programme-level frame: a diagnosis that reads mostly about one workstream or playbook is reframed to the overall programme before it goes out [A20].
- Disagreements between stakeholders are surfaced as open items with both positions, never resolved silently.
- Quotes stay verbatim and are attributed to the right speaker; nothing is put in a stakeholder's mouth.
- Fixes land in the final deck in place; no "what changed" slide, "new" tag or version note [A1].

## Delegate
- Long transcripts, file sweeps and the earlier diagnosis to runner: extraction with timestamps, no judgement.
- Inputs to request to /data-request; T38 and T39 drafting to drafter once the diagnosis is agreed.
- An independent check of the diagnosis against the transcript to critic when stakes are high.
- The rebuild to /storyline (structure), /initiative (initiative design) or /deck-build (named slides).

## Output
- T4 and T5 written into the meeting note (from the Meeting template) in `03-Work/<Engagement>/`; decisions and actions added to the hub's T5 tables; __OWNER__'s own actions added to today's note in `02-Daily/` as dated tasks; blessed wording to the speaker's note in `07-People/`.
- Corrections about how Claude works go to /lesson verbatim, never into the diagnosis.
- In chat: the bottom line, the root causes, the "[confirm]" items and the first three actions. Nothing else.
- M1 no em dashes. M3 fixes land in a final deck with no version language. M5 nothing invented from the audio; unclear items stay "[confirm]". M6 name the file version the comments were read against.
