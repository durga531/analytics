---
name: prompt-for
description: Writes copy-ready prompts for other AI tools (deep-research engines, agent platforms, custom assistants, slide generators) with __OWNER__'s constraints, the mandates and the exact return format built in. Use when __OWNER__ says write a prompt for, brief the research tool, prompt the agent or convert my holdings to text.
model: __MID_MODEL__
effort: medium
argument-hint: <target tool> <task> [holdings, data or files]
---
# /prompt-for
One copy-ready prompt for another tool that carries __OWNER__'s standards, the mandates that apply and the exact format wanted back, so /audit can grade what returns. Routing: mid tier (recurring ask 23).

## Read first
- The latest files the prompt draws on: holdings export, thesis notes, deck or data (M6); say which versions.
- __OS_DIR__/templates.md: T11 (fresh-capital research brief) as the structure for equity research prompts; T10 (investment committee rules) for the policy, framework, self-audit and ACTION CARD the prompt must require.
- __OS_DIR__/output-standards.md: Equity research standard; Anti-hallucination; Formatting bans; Deck rules when the target is a slide tool.
- __OS_DIR__/active-areas.md: the area the prompt serves (good output, rejected), including failures of earlier tool runs the prompt must pre-empt.
- __OS_DIR__/thinking-patterns.md: Challenge vs execution (third-party frameworks are challenged; the mandate is fixed).

## Steps
1. Name the target tool and read any capability notes __OWNER__ supplies for it. Size the prompt to the tool: a deep-research engine gets a full brief, an agent platform gets inputs, steps and stop conditions, a slide tool gets the deck rules and a slide-by-slide spec.
2. Open with __OWNER__'s request preserved verbatim, then the role, the objective and the decision the output serves.
3. Equity research follows T11: an evidence-dated memo; primary documents first; time series of 8+ quarters or 3+ years; prices with IST timestamps; the T10 policy quoted, never summarised; the T10 framework, self-audit and ACTION CARD as the required output; sizing in percentages so it scales; a contrarian verdict free to argue against __OWNER__'s thesis; insight beyond what common retail sources carry.
4. Paste the mandate block below, word for word, into every equity prompt ahead of the task.
5. Holdings or data: convert to plain-text tables when asked, one row per holding with the columns the analysis needs; a missing field is marked missing, never filled.
6. Specify the return format exactly: section order, table columns, an F, S, I or ND grade on every decision-driving claim, dated sources with links, no em dashes, and a closing list of what the tool could not verify.
7. Slide tools: carry the deck rules that matter: a final deck with no version language; conclusion titles that read as one storyline; less text, more visual, no excess whitespace; no extreme or absolute words; sources in subscript; no abbreviations; the given template as the authority; no firm branding on independent decks.
8. A framework or prompt __OWNER__ brings from elsewhere is tested before it is reused: say whether it holds up and what to drop.
9. Every prompt, equity or not, carries the block's anti-fabrication line.

Mandate block, word for word:
```text
Verdicts are BUY, ACCUMULATE, HOLD, WATCH or AVOID only. Never suggest selling, trimming, exiting, reducing, stop-losses or tax-loss moves on holdings; use pause triggers and thesis-breakers instead.
Never fabricate a number, source, quote or case. Where data is missing, write "I do not have reliable data on this". Cut unverifiable claims; do not caveat them.
```

## Rules enforced here
- Every equity prompt carries the block's first line (M2) word for word; no prompt asks a tool for a sell-type verdict, an exit plan, stop levels or tax-loss moves, whatever the request says.
- Every prompt carries the block's second line (M5) and asks for dated, checkable sources.
- __OWNER__'s request is quoted verbatim, never paraphrased away; the T10 policy is quoted, never re-derived.
- Client names, client data and engagement material never enter a prompt for an outside tool; anonymise or code-name them as output-standards.md requires.
- The return format is exact enough for /audit to grade each claim as holds, breaks or unverifiable.
- Plain instructions: no flattery of the tool, no filler, no superlatives without a benchmark.

## Delegate
- Holdings conversion from broker exports and other data extraction to runner.
- The research frame itself, when that is the open question, to /equity.
- The tool's returned output to /audit: claims graded, the best version merged.

## Output
- In chat: the prompt in one copy-ready block, then one line naming what to attach alongside it.
- A prompt worth reusing saved to `08-Library/Prompts/<Tool> <purpose>.md` when __OWNER__ asks.
- M1 no em dashes in the prompt or in the format it demands. M2 the mandate block in every equity prompt, word for word. M5 the anti-fabrication line in every prompt. M6 built from the latest holdings and files, and name them.
