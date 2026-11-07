# Second-brain engine for Obsidian and Claude Code

A non-destructive installer that turns an Obsidian vault into a Claude Code workspace governed by six operating-system files the owner writes about themselves. This repository holds only the generic engine. Everything personal (the six files, the kill list, the fact base, the folder mapping) stays inside the owner's vault and is generated there.

## What it installs

| Layer | What | Where in the vault |
|---|---|---|
| Operating manual | Loads `identity.md` and `output-standards.md` in full every session, states six hard mandates, the routing table and the working rules | `CLAUDE.md` |
| Session digest | Live context plus a digest of the other four OS files (routing, closed debates, template index, area status) under Claude Code's hook size cap | `.claude/hooks/session_context.py` |
| Guard | Enforces the hard mandates on every write, every shell-written file, every Office file and every final answer | `.claude/hooks/guard.py` |
| Agents | Four, one per model tier: strategist (top), critic (grades, never rewrites), drafter (mid), runner (small) | `.claude/agents/` |
| Skills | One per recurring ask, each pinned to its tier and citing templates by T-number | `.claude/skills/` |
| Rules | Path-scoped standards for work, investing, career, self, learning, people and journal notes, extended to the vault's existing topic folders | `.claude/rules/` |
| Dashboard and templates | `Home.md` (Tasks and Dataview), note scaffolds, `09-Reviews/Now.md`, the lessons queue | vault root, `08-Library/Templates/`, `09-Reviews/` |
| Folder mapping | A proposal for where existing notes sit in the numbered taxonomy; nothing moves until approved | `01-Inbox/Folder Mapping - Proposed.md`, `.claude/tools/` |

## The six operating-system files

The engine expects these in `00-Operating-System/` (change with `--os-dir`): `identity.md`, `active-areas.md`, `output-standards.md`, `thinking-patterns.md`, `templates.md` (numbered `### N.` headings, cited as TN) and `recurring-asks.md` (with a "Routing implication" section). They are the single source of truth; the engine references them and never copies them.

## Install (macOS)

1. Download the kit and preview the install. Nothing is written in a dry run:

```bash
cd /tmp && curl -fsSL -o sb.zip https://github.com/durga531/analytics/archive/refs/heads/claude/practical-mendel-st31z5.zip && rm -rf sb && unzip -q sb.zip -d sb
```

```bash
bash /tmp/sb/*/second-brain/install.sh "<path to your vault>" --dry-run
```

2. Install for real (it asks before adding the login item and the MCP bridge):

```bash
bash /tmp/sb/*/second-brain/install.sh "<path to your vault>"
```

3. Start Claude Code inside the vault and run the first-time check:

```bash
cd "<path to your vault>" && claude
```

Then type `/onboard`.

Options: `--name NAME`, `--os-dir DIR`, `--top-model fable`, `--critic-model opus`, `--main-model opus`, `--care-model opus`, `--mid-model sonnet`, `--small-model haiku`, `--yes`, `--no-mcp`, `--no-autostart`.

## What the installer never does

- Write inside the operating-system folder or `.obsidian/plugins`, or change which plugins are enabled.
- Move, rename or delete a note. Folder moves are proposed in `01-Inbox/Folder Mapping - Proposed.md` and applied only after the owner sets `status: approved` and runs `.claude/tools/apply_mapping.py --apply`.
- Overwrite a file the owner edited. Kit files the owner has not touched are updated on re-run; anything else gets the new version beside it as `<name>.kit-new`, which `/onboard` helps merge.
- Put personal data anywhere outside the vault.

## Hard mandates and how they are enforced

| Mandate | Enforced by |
|---|---|
| M1 No em dashes in any generated text | guard: blocks writes and edits, lints shell-written and Office files, asks for a rewrite of a final answer |
| M2 Equity verdicts BUY, ACCUMULATE, HOLD, WATCH or AVOID only; no sell, trim, exit, reduce, stop-loss or tax-loss suggestions | guard on investing paths, ACTION CARD content and equity conversations; prompt reminder; invest rule; equity skills |
| M3 Client decks are final decks, no version-control content | guard pptx lint; work rule; deck skills |
| M4 Resume numbers only from the locked fact base; the kill list never returns | guard on resume files and resume conversations, using lists generated locally from the OS files |
| M5 Never fabricate a number, source or quote | manual, critic gates, every skill's output step |
| M6 Read the latest file version and the project rules before any build | prompt preflight injected on build requests; work rule; build skills |

Prove every mandate end to end from the vault folder with `python3 .claude/hooks/guard.py selftest`: it fires each hook the way Claude Code does, with synthetic text, prints PASS or FAIL per mandate and never prints the private lists. /onboard runs it.

Switch the guard off temporarily with `touch .claude/guard/OFF` (delete the file to switch back on).

## Model routing

| Tier | Typical work | Default model |
|---|---|---|
| Top | storylines, initiative design, equity research, transcript diagnosis, outside-in POV decks, audits of other models' outputs, number defence, interview prep, independent builds | fable |
| Critic | independent review and maker-checker grading | opus |
| Mid | resume drafting, headers, outreach, data requests, deck and workbook builds, daily rhythm | sonnet |
| Small | lexicon passes, workbook filling, validate-repair-render, lookups, conversions, manuals, picks | haiku |
| Care | personal and life decisions | opus |
| Session default | conversation and orchestration | opus |

Skills pin their tier, so routing happens without re-prompting. If the top model is not available on a plan, install with `--top-model opus`.

## Daily rhythm and scheduled runs

`/today` in the morning, `/close` in the evening, `/weekly` on Sunday, `/ingest` when the inbox passes ten items. To run `/today` on a schedule, create a scheduled task in the Claude desktop app (Code tab) with the vault as its folder; it runs while the app is open and the machine is awake. Cloud scheduled runs need the vault in a private Git repository.

## Updating

Download the kit again and re-run the installer. Unedited kit files update in place; edited ones get a `.kit-new` copy beside them.

## Tests

```bash
python3 -m unittest discover -s second-brain/tests -v
```

The tests use synthetic fixtures only.
