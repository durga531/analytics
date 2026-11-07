---
name: independent-build
description: Designs __OWNER__'s independent builds (market models, data sites, civic analysis, capability decks) on validated data, labelled number classes and full coverage. Use when __OWNER__ says build the model, next version, add this layer, fix the map or share the build.
model: __TOP_MODEL__
effort: high
argument-hint: <build and what to change> [inputs]
---
# /independent-build
The next version of an independent build (model, data product, civic analysis or its capability deck) at a bar a senior partner or investor would be proud of. Routing: top tier for design (recurring asks 7 and 19); every data pull and all QA run on runner.

## Read first
- Latest version of the build, its build log and every input __OWNER__ has shared for it (M6); state which version you are building on.
- __OS_DIR__/output-standards.md: Deck rules (Deck type and scope; Template discipline; Numbers and evidence; Design), Excel and data rules, Anti-hallucination, the second verbatim-corrections list in full, and [A1] [A11] [A19] in the first.
- __OS_DIR__/templates.md: T13 (deck intake and cardinal rules) for intake; T40 (market pillars), T41 (unit brief), T42 (story step grammar), T43 (number classes), T44 (capability deck storyline), T45 (use-case table by industry), T46 (outlet-density model method), T31 (micro-market cascade), T54 (note sharing an own build).
- __OS_DIR__/active-areas.md: the build's entry under Independent and civic (status, good output, rejected, open decisions).
- __OS_DIR__/identity.md: Built assets and How I think, for what is __OWNER__'s own work and the quality bar.
- __OS_DIR__/thinking-patterns.md: Questions I ask; What I push on; Closed debates (settled product-shape questions stay settled).

## Steps
1. Intake per T13, one or two questions at a time and only what the request and the record leave open: who the build and its deck are for, the decision they must produce and the design language; proceed once those three are known. On opening a big build, also ask the one or two decisions that change the design. When __OWNER__ says infer, infer from the record.
2. List every input __OWNER__ has asked for, this round and earlier ones; the list is the completeness checklist.
3. Benchmark first: set a real-world deliverable that defines the bar beside the build, and state what this version must match and beat and what it gives that existing vendors and tools do not. Judge __OWNER__'s version only after that.
4. Design on this tier: the questions per T40, the unit view per T41, each story step per T42, the cascade per T31. Each view states the hypothesis it tests; a variable earns its place by answering a question another view uses.
5. Data through runner: real, validated sources only, each named by its primary producer and date; __OWNER__'s own collected data credited as such; every figure carries its T43 class, directional versus exact called out.
6. Build the views: method text per view, a distinct colour scheme per view, sources in subscript or hover, nothing private in the product. Civic builds keep a data-only register, let the data structure argue the conclusion and stay bilingual when the brief asks.
7. QA through runner, on the render: map alignment, colours, whitespace, coverage counts by unit, every prior layer and language still present, every checklist item ticked.
8. Story and sharing: T44 for the capability deck and T45 for use cases; T46's public-description rules whenever the model is described outside; T54 when the build is shared, its maturity stated honestly.
9. After a correction, restructure completely; never patch a rejected structure.

## Rules enforced here
- Whatever an outside reader sees is final: no content on what changed, what moved or what goes where, no new or updated tags, no version numbers or notes in the product or its deck; a page a senior reader opening it cold would question is cut. Version history lives only in the build log [A1].
- No excess whitespace: every view, page and slide fills its content area so the impact lands; a render with large empty regions fails QA and is redesigned, judged on the rendered images, not the code [A11].
- No pivot-level description: every view and story step states a hypothesis, the root cause behind the pattern and its implication, robust enough to survive a senior partner's challenge; an earlier version's analysis is re-examined from first principles, never reused as is [A19].
- Variables talk to each other: no dump of metrics; each view keeps the few that drive the decision and shows how they interact, so a senior partner gets one reading without going through every element [B1].
- Sources sit in subscript, footnote or hover, never called out in headlines or body text where they break the flow [B2].
- Coverage at the level the model claims: no threshold or floor that leaves most units unscored; partial coverage is closed before release, or the model stops claiming that level [B3].
- Data __OWNER__ collected, scraped or verified is credited as __OWNER__'s own primary work, never described as supplied, third-party or vendor data [B4].
- Each data set is credited to its primary producer, never to an aggregator that republishes it [B5].
- Private instructions, thinking-direction notes and reviewer personas never appear in the product, its notes or its file properties [B6].
- Each view or layer gets a colour scheme clearly distinct from the others, checked on the render [B7].
- Reference visuals are recreated in __OWNER__'s own style, never pasted as snapshots that carry another firm's look [B8].
- Method text changes with the view, level or lens selected; one static block is a defect [B9].
- Map surfaces sit exactly on the geographic outline, with no offset, scale or projection drift, checked in the rendered output, not in code [B10].
- Every requested input is captured, relative and derived measures and their impact included; the step 2 checklist is reconciled item by item before anything is called done [B11].
- No fake, illustrative or placeholder data anywhere, and no AI slop.

## Delegate
- Data pulls, scraping, cleaning, joins, coverage counts and render QA to runner, in parallel where independent; design and judgement stay on this tier.
- The capability deck's mechanical build to /deck-build; the sharing note to drafter.
- An independent check against T3 (independent review brief) and the rules above to critic before anything is shared.

## Output
- The build files in the build's working folder, plus a dated build-log entry: decisions, sources with producer and date, coverage counts, number-class mix, open gaps.
- In chat: what the version now does, the checklist with ticks, coverage counts and the gaps that remain.
- M1 no em dashes. M3 any deck from the build is a final deck. M5 no fake or illustrative data; "I do not have reliable data on this" where data is missing. M6 build on the latest version and say which.
