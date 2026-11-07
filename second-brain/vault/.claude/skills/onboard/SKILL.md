---
name: onboard
description: Health-checks the second brain after an install or update (hooks, guard lists, agents, skills, rules, tools), merges .kit-new copies on approval, then walks the folder mapping and the schedules. Use when __OWNER__ says onboard, set me up, check the setup or is it working.
model: __SMALL_MODEL__
effort: medium
argument-hint: <check, mapping or schedule; default all three>
---
# /onboard
A health table for the installed engine, then the merge of any kit updates, the folder-mapping decision and the schedules. Routing: small tier (recurring ask 14, the commands half); setup architecture goes to strategist.

## Read first
- The installer's report if __OWNER__ pasted it, and `.claude/.kit-manifest.json` (what the kit installed).
- `CLAUDE.md` (imports and routing table) and `.claude/settings.json` (SessionStart, UserPromptSubmit, PreToolUse, PostToolUse and Stop hooks).
- __OS_DIR__/recurring-asks.md: Routing implication, the tiers every skill and agent must match.
- `01-Inbox/Folder Mapping - Proposed.md` when the mapping is in scope.
- This skill never writes inside __OS_DIR__; an OS-file change is proposed and applied only on __OWNER__'s approval.

## Steps
1. Six files: all present in __OS_DIR__, templates.md with numbered headings, recurring-asks.md with its Routing implication section; every @import in CLAUDE.md resolves to a file.
2. Hooks and digest: settings.json registers all five hook events, each calling a script inside `.claude/hooks/`; run `python3 .claude/hooks/session_context.py`, which must print live context and the four-file digest, and the same digest must have opened this session.
3. Guard lists: `.claude/guard/config.json`, `kill-list.txt` and `fact-base-numbers.txt` exist; if not, run `python3 .claude/hooks/guard.py extract` (add `--force` after an OS-file change). Report line counts only, never the contents.
4. Guard smoke test: `f=$(mktemp) && python3 -c "print('a' + chr(0x2014) + 'b')" > "$f" && python3 .claude/hooks/guard.py lint "$f"; echo "exit $?"; rm -f "$f"` must print a BLOCK line and exit 1. Never paste the flagged character into chat.
5. Rendering: `grep -rnE "__(OWNER|OS_DIR|[A-Z]+_MODEL)__" CLAUDE.md .claude/agents .claude/skills .claude/rules .claude/settings.json` returns nothing; a hit means the installer did not render that file.
6. Inventory: `grep -H "^model:" .claude/agents/*.md .claude/skills/*/SKILL.md` checked against the routing table; exactly four agents (strategist, critic, drafter, runner) and seven rule files. Agents or skills left by an earlier kit are listed as leftovers and moved to `99-Archive/` only on approval; notes __OWNER__ wrote are never touched.
7. Kit updates: `find . -name "*.kit-new" -not -path "./.obsidian/*"`; for each, show the diff with __OWNER__'s file and propose a merge that keeps __OWNER__'s edits; apply on approval, then move the .kit-new copy to `99-Archive/`.
8. Tools: `command -v claude uvx node soffice pdftoppm`; give the install line for each one missing (brew install uv, node or poppler; brew install --cask libreoffice). `claude mcp list` shows the obsidian bridge; inside the vault it is optional, because Claude Code reads the files directly.
9. Engine stays generic: grep CLAUDE.md and `.claude/` for the client and firm names in active-areas.md's headings, and confirm that templates bound to one firm or engagement (T15 engagement deck rule set, T18 template operating system) load only when that template is the working one. Flag every hit.
10. Gaps: `grep -n "not found in history" __OS_DIR__/*.md`; ask at most two questions, only where the answer changes behaviour (routing, prioritisation, a template whose body is missing). Stage each answer through /lesson.
11. Mapping: walk the proposal row by row (folder, destination, move yes or no) and record __OWNER__'s calls in the file; set `status: approved` only when __OWNER__ says so; run `python3 .claude/tools/apply_mapping.py .` as a dry run, show the plan, and add `--apply` only after a second yes. Every move is logged in `99-Archive/Moves Log.md`.
12. Schedules: in the Claude desktop app, open the Code tab and create a scheduled task with this vault as its folder; /today on weekday mornings and /weekly on Sunday, at times __OWNER__ picks. Runs need the app open and the machine awake; cloud runs need the vault in a private Git repository.

## Rules enforced here
- The session digest loads at every start, so project memory and preferences are re-read rather than recalled from an earlier session [A16]; the prompt preflight fires on build requests, so the latest working file and its version are named before any build [A7]. A missing hook is fixed before any other step.
- No check is marked ok unless its command ran; each status cites the output it rests on.
- __OWNER__'s edits win every merge; nothing is moved, renamed or deleted without approval; the private lists never leave the vault.

## Delegate
- Setup architecture (a taxonomy change, a routing or tier change, a new skill or rule) to strategist, briefed with the check table.
- A .kit-new conflict inside CLAUDE.md or a rule file to strategist for a merge proposal; applying it stays here.

## Output
- One table, Check | Status (ok, fixed, needs __OWNER__) | Evidence or fix, in step order; then the mapping decision, the questions asked and the schedule steps.
- Three habits for week one: /today each morning, /close each evening, the T2 maker-checker loop on anything that matters.
- M1 no em dashes in the report; the smoke test shows the guard enforces it. M2, M3, M4 and M6 depend on the guard and the prompt hook: report each as active or name the fix. Switching the guard off is __OWNER__'s call, never a way past a failed check.
