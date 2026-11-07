---
name: pov
description: Builds an independent outside-in point-of-view deck on a target firm or civic question from verified primary data, stripped of firm branding, with a cover message. Use when __OWNER__ says POV deck, outside-in deck, cold outreach deck, deck for a named firm or civic data deck.
model: __TOP_MODEL__
effort: high
argument-hint: <target firm or issue> [recipient or role] [inputs]
---
# /pov
An independent point-of-view deck that opens a door: titles that carry the argument, one dominant insight per page, every figure verified at its primary producer, plus the cover message. Routing: top tier (recurring asks 11 and 19); research pulls and the pptx build, validation and render run on runner.

## Read first
- The latest version of any earlier deck for this target and every input __OWNER__ has shared (M6); say which version you build on.
- `.claude/rules/work.md`: path-scoped rules load only when a work file is touched, so read it for POV work.
- __OS_DIR__/output-standards.md: Writing voice (no sycophancy towards the recipient); Formatting bans (headline rules, public showcase bans); Deck rules (Deck type and scope, Template discipline for independent decks, Storyline and headers, Numbers and evidence, Design); all three verbatim-correction lists.
- __OS_DIR__/templates.md: T1 (executive answer structure) for the opening argument and the chat reply; T13 (deck intake and cardinal rules) for intake; T51 (outside-in outreach deck) for page grammar and sequence; T52 (outreach message pattern) for the cover message; T19 (argument-first headline chain) as the exemplar; T14 (slide-craft standard and toolchain); T20 (reusable deck tables); T28 (case study template) and T48 (benchmark case study playbook) for benchmark pages; T43 (number classes); T50 (resume architecture and fact base) for proof points.
- __OS_DIR__/active-areas.md: Independent outreach decks and Job transition (what was sent, good output, rejected); for civic work, its civic area.
- __OS_DIR__/identity.md: Built assets, for what counts as __OWNER__'s own work; on any number the fact base (T50) wins over identity.md.
- __OS_DIR__/thinking-patterns.md: What I push on (uniqueness, credit, primary producers, firm policy); Challenge vs execution.

## Steps
1. Intake (T13): one or two questions at most, and only what the request and the record leave open: the target, the reader, the conversation the deck should open and, when a role is in play, the gap it fills. The design language is __OWNER__'s own neutral style.
2. Find the spiky insight first: what this deck shows that the target's own team and common sources do not. If there is none yet, say so before building.
3. Evidence through runner: annual reports, filings, disclosures, call transcripts, official statistics; each figure traced to its primary producer with date, unit and T43 number class, the latest corrected value only.
4. Storyboard titles first against T19 and the headline rules, with the opening page in the T1 shape; then lay each page to the T51 page grammar and sequence, one dominant insight per page with a risk or so-what line.
5. Benchmark pages through T48 and T28; every case shows money invested, impact in absolute terms and the timeline. T20 tables where a capability, crisis or phased-outcome view fits.
6. Add the "what would change my mind" page: the facts that would overturn the thesis.
7. Runner builds the pptx on the T14 toolchain with native editable charts and a neutral design, strips all firm branding (theme names and file authors included), applies the footer output-standards.md specifies for independent decks, validates, renders and returns every slide image; read each one.
8. Civic and political POVs: a data-only register in which the data structure argues the conclusion; the decisive comparison drawn at a scale that makes the point visible; bilingual when the brief asks, with both languages kept in step through every revision.
9. Cover message to T52 (or /outreach when it goes with an application): it opens on one verified finding from the deck and draws proof points only from the locked fact base. A positioning deck keeps the ask out of the deck itself.
10. Critic reviews before anything is sent; every must-fix is fixed.

## Rules enforced here
- A final deck: nothing on the deck's own history, versions or changes and no "new" tags; every page earns its place with a senior reader who opens it cold [A1].
- Summary and argument lines are precise, specific statements a senior reader at the target would accept read alone; never slogans, colloquial or sweeping lines [A4].
- No page or summary opens with or commits to a value figure or range; lead with what the finding means and what it addresses, and any value sits on its evidence page with its build and number class [A5].
- No excess whitespace: content fills each page's content area, judged on the rendered images [A11].
- No variable dumps: keep the few drivers that decide the argument and show how they interact (an index, a driver tree or a decision rule) [B1].
- Titles alone read as one compelling, flowing storyline in sequence and are rewritten before any page is built; where __OWNER__ has edited a version, that edit is the base [C1].
- Sources sit in subscript or the foot-of-page source line (hover in interactive builds), never in a headline or called out mid-argument, because an explicit call-out breaks the flow [B2].
- Data __OWNER__ gathered or built is credited as __OWNER__'s own work, never described as supplied or third-party; a proprietary dataset is credited without being named where active-areas.md keeps it private [B4].
- Every source line names the primary producer of the data, never an aggregator or platform that republishes it [B5].
- __OWNER__'s private instructions, reviewer personas and notes to the assistant never appear on a slide, in speaker notes or in file properties [B6].
- Visuals from reference decks are recreated in __OWNER__'s own style, never pasted as snapshots that carry another firm's colours or branding [B8].
- Every figure carries its T43 number class, exact or directional, in its source line or notes; public showcase versions carry no confidence labels or proof-of-sourcing language in the body.
- No sycophancy: no flattering cover line, dedication or addressee framing; the deck argues, it does not court.
- Only the latest corrected figures: a number from an earlier deck returns only if it survives the corrected version.
- Never attach or build on a firm-templated deck; nothing from a client engagement appears; firm policy on outside work and AI-use disclosure is checked before anything is sent.
- Every statistic is verified at its primary source; unverifiable claims are cut, not caveated.

## Delegate
- Research pulls and figure validation to runner: each fact back with its producer, date and link.
- The pptx build, validation and render to runner (T14 toolchain); the argument, titles and insight stay here.
- An independent review to critic before sending: T3 (independent review brief) house rules and the T2 (maker-checker rubric) gates.
- The cover message to /outreach when it goes with an application; the resume to /resume.

## Output
- In the target's working folder: the pptx with native charts, a PDF with speaker notes removed for sending, and a source register (figure, producer, date, number class, link).
- In chat, in the T1 shape: the spiky insight in one line, the titles-only chain, open gaps, then the cover message.
- M1 no em dashes. M3 a final deck: no version language, change notes or "new" tags. M4 proof points in the cover message only from the locked fact base. M5 nothing fabricated; "I do not have reliable data on this" where data is missing. M6 the latest version and the latest corrected figures, named.
