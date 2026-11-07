---
name: refresh
description: Mid-session reload of memory, preferences and the latest working files, so the next build starts from the current version and the current rules. Use when __OWNER__ says refresh, reload, re-read, check the latest version, or after files were edited outside this session.
model: __SMALL_MODEL__
effort: low
---
# /refresh

Reloads what a fresh session would know, without restarting. Routing: small tier (recurring ask 24). The session-start hook does this automatically at the start of every session; /refresh repeats it mid-session [A7] [A16].

## Steps
1. Run `python3 .claude/hooks/session_context.py` and read its output: live context, the latest working files, the routing implication, the closed debates, the template index and the area statuses.
2. Name the active area from the conversation (engagement, investing, career or personal) and open its entry in `__OS_DIR__/active-areas.md`.
3. For the active area, list the working files newest first (version number and modified time) and name the one to build on. If two candidates are close, ask which one __OWNER__ edited last.
4. Re-read the rules that govern the next piece of work:
   - decks and workbooks: output-standards.md (Deck rules, Excel and data rules, Process), `.claude/rules/work.md`, the engagement's rule set in templates.md when that engagement (for example T15), and its decision log (T5)
   - resumes and outreach: output-standards.md (Resume rules), `.claude/rules/career.md`, T50
   - equity: output-standards.md (Equity research standard), `.claude/rules/invest.md`, T10
5. Check `09-Reviews/Lessons Queue.md` for approved corrections that are not yet in output-standards.md and flag them.

## Output
Three lines: what is loaded (files and sections), the working file and version to build on, and anything stale or conflicting. Then stop and wait for the next instruction.
- M6: the next build starts from the file named here.
- M1: no em dashes.
