---
name: storyline
description: Builds the deck storyline before any slide exists, from intake and a signed-off problem to titles that read as one argument; owns the headers-only review. Use when __OWNER__ says storyline, storyboard, headers do not flow, exec summary, headers-only review or new deck.
model: __TOP_MODEL__
effort: high
argument-hint: <engagement or deck file> [audience] [decision]
---
# /storyline
A signed-off storyline: problem, governing thought, key lines and a titles-only chain that /deck-build can build without guessing. Routing: top tier (recurring ask 2, strategic half; the headers-only review, the strategic half of ask 5).

## Read first
- The latest version of the working deck and every input shared (M6); where __OWNER__ has edited the file, that edit is the base and is never overwritten [C1]. Say which file and date you build on.
- `.claude/rules/work.md`: path-scoped rules load only when a work file is touched, so read it for chat-only storyline work.
- The engagement hub's T5 (decision and action log): decisions taken, slides removed, templates agreed.
- __OS_DIR__/output-standards.md: Deck rules (Deck type and scope, Storyline and headers, Language, Numbers and evidence, Process) and Formatting bans (banned and extreme words, headline limits).
- __OS_DIR__/templates.md: T13 (deck intake and cardinal rules); T21 (playbook deck storyline); T25 (working-session deck structure); T19 (argument-first headline chain) as the exemplar; T42 (story step grammar) and T44 (capability deck storyline) for product decks; T47 (directional choices workshop) for workshops; T14 (slide-craft standard and toolchain); T43 (number classes); T15 (engagement deck rule set) when the deck belongs to that engagement.
- T18 (template operating system), build protocol step 1, only when that template is the working template. T18 is never the default: otherwise the template __OWNER__ names governs [C4] [C5] and its design language is asked at intake (T13).
- __OS_DIR__/active-areas.md: the area this deck serves (status, good output, rejected) and its agreed architecture and sections.
- __OS_DIR__/thinking-patterns.md: Challenge vs execution (a new playbook and any structural change are challenge zones); Closed debates stay closed.

## Steps
1. Intake with the T13 questions, one or two at a time, skipping any the request or the record already answers. Proceed only once audience, decision and design language are known; when __OWNER__ says infer, infer from the record and state each inference.
2. Define the problem before any slide: one specific, measurable problem statement and the decision the deck must produce, for whom and by when. Get sign-off.
3. Choose the spine: T21 for programme and playbook decks, T25 for co-creation working sessions (no value or return numbers), T42 with T44 for product decks, T47 for workshops. Open at programme level.
4. Write the governing thought, then the key lines. Draft the executive summary first; each of its lines points to the slide that proves it.
5. Storyboard titles before content: one complete-sentence conclusion per slide under the T13 title rules, one message per slide, each planned as title, insight, evidence and implication (T14) with its exhibit, source and T43 number class, marked exact or directional. Missing evidence reads "TBD, source required"; never fill a gap with a guess.
6. Map each title to a slide of the working template: slides are picked from that template and its chain of command, never designed from scratch, and its slide structure stays as it is with only the content customised [C4] [C5].
7. Headers-only round: read the titles alone, in order, against T19; rework the whole chain until it carries the case end to end; show __OWNER__ the titles-only list and wait before anything is built.
8. Partner test every slide and cut what does not earn its place; detailed tables and registers go to the appendix. Tick every input and requested change against the chain [B11]. Confirm the agreed architecture is intact; if the better story needs a structural change, stop, explain and wait.
9. The headers-only review of an existing deck is owned here: run it after any /lexicon pass, on the final wording; extract the titles in order and run steps 7 and 8 only, reworking no finalised slide that __OWNER__ has not reopened.

## Rules enforced here
- Headers read in sequence as one compelling, flowing storyline; after a critique the whole chain is reworked until it reads end to end, never patched line by line [C1].
- Frame at the level of the overall programme: each playbook or workstream is shown serving the programme objective and none crowds out the programme story [A20].
- The executive summary states what we found, what we are building and what each solution fixes relative to the as-is; it never opens with, headlines or commits to a value figure or range, and value sits only on the business-case page with its build [A5].
- Executive-summary lines are precise, client-credible statements that make sense read alone, in the working template's executive-summary structure; never slogans, colloquial or sweeping lines [A4].
- No extreme or absolute words (the list in output-standards.md); neutral maturity wording that names the stage reached, so the client is not put on the defensive. A finalised executive summary is kept, never redrafted [A13].
- Change only the slides the request covers; finalised slides are not reworked unless __OWNER__ reopens them, even when the template or a better story suggests it; flag and ask instead [A10].
- The agreed architecture (levers, house, sections) is never silently broken; confirm it is intact, and for structural change think and tell first and change only once agreed [A14].
- Client headers carry no exact numbers; use percentages or approximations. Header wording a partner has blessed is used verbatim. No term, code or initiative ID appears before the slide that defines it.
- Sources sit in notes, subscript or hover, never in a headline or called out in the body, because a call-out breaks the flow [B2].
- __OWNER__'s private instructions, thinking-direction notes and reviewer personas never enter titles, slide text or speaker notes; the storyline note keeps them apart from anything /deck-build will place [B6].
- Every input and requested change __OWNER__ gave, relative and derived measures included, is mapped to a slide or parked with a stated reason; nothing is silently dropped [B11].
- Every slide passes the partner test (would a partner reading it cold ask why it is there); the outline is a final deck with no slide on what changed, what moved or what goes where [A1].

## Delegate
- Fact gaps and lookups (validate or disprove, with source and date) to runner.
- Transcripts and stakeholder feedback to /diagnose first; build on its T4 (stakeholder feedback diagnosis).
- Initiative design and initiative pages to /initiative.
- An independent check of the titles-only chain to critic (T3 independent review brief).
- The agreed outline to /deck-build; slides are never built on this tier.

## Output
- `03-Work/<Engagement>/<Deck> Storyline.md`: problem statement, audience and decision, governing thought, key lines, the numbered titles-only chain, then per slide the template slide, exhibit, evidence source, number class (exact or directional) and status (to validate, or TBD, source required); then the input checklist.
- In chat: the titles-only list for the headers-only round, and any structural change proposed with its reason, awaiting approval.
- Agreed decisions go to the engagement hub (T5 decision and action log).
- M1 no em dashes. M3 final deck only, no version language. M5 never invent a number, source, quote or case; unverifiable claims are cut, not caveated. M6 name the file version you built on.
