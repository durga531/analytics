---
name: lesson
description: Captures a correction verbatim with date and context, states the exact rule behind it, merges any equivalent and queues it; on approval appends quote and rule to the OS files. Use when __OWNER__ corrects how Claude works or says remember this, always, never or note this.
model: __MID_MODEL__
effort: low
argument-hint: <the correction in __OWNER__'s words> [context]
---
# /lesson
One row in `09-Reviews/Lessons Queue.md` and, once approved, the quote and its rule in the OS files. Routing: mid tier, main session (memory loop).

## Read first
- The correction as given, in the conversation or the note it sits in, and the work it was about.
- `09-Reviews/Lessons Queue.md`: every row still pending.
- __OS_DIR__/output-standards.md: the three verbatim-corrections lists, tagged A1 to A20, B1 to B11 and C1 to C5 in file order, and the sections a rule can land in.
- __OS_DIR__/thinking-patterns.md: Challenge vs execution and Working habits, the home for how-to-work patterns; Closed debates.
- `.claude/rules/journal.md`.

## Steps
1. Quote: __OWNER__'s exact words, spelling and typos kept, nothing tidied; then the date and the context (file, slide or section, area, what was being built).
2. Rule: what must always or never happen, as a testable rule exactly as strict as the correction; generalise only as far as the words support. If the scope is unclear, ask one question.
3. Equivalent: search the lists, the sections and the pending rows. A pending match is merged into its row with the new quote added. A match with an existing rule is a repeat: the row cites that rule's tag and names the skill, rule or hook that let it slip, and no second rule is written.
4. Conflict: a correction that contradicts an existing rule or a closed debate is queued with the conflict named; the existing rule stands until __OWNER__ approves the change.
5. Target: the output-standards.md section the rule belongs in, or thinking-patterns.md for a how-to-work pattern.
6. Queue the row: Date | Verbatim correction, with its context | Rule behind it | Target section | Status pending.
7. Apply the rule to the current work at once; approval governs the OS files, not compliance.
8. On __OWNER__'s approval: append the quote to the end of the matching list in output-standards.md (a new engagement or project starts a new list after the last); add the rule to its target section with its source, in the file's own citation style; set `updated:`; mark the row done with its new tag.

## Rules enforced here
- A design rule given once binds every later build without being restated: the rule applies now and is staged so every later session loads it [A12].
- Never rely on recall from earlier sessions: a correction lives in the files each session re-reads, never only in the chat [A16].
- A quote is never reconstructed: if __OWNER__'s exact words are not in the conversation or a file, ask for them or log the row as an observed edit, unquoted.
- The rule is precise and enforceable, never softened into a preference ("try to", "where possible").
- Append only: existing entries are never inserted between, reordered or reworded, so every tag keeps its meaning across the skills.
- The six files change only on approval; the queue is the one place this skill writes without it.
- An em dash inside a quote is written as a spaced hyphen; it is the only change a quote may take.

## Delegate
- Nothing by default. Rows not approved now wait for /weekly, which decides them with __OWNER__; a repeat that exposes a broken skill or hook is raised there for a fix.

## Output
- One line: the rule, its target section and the row's status, ending "approve now, or leave it for /weekly".
- M1 no em dashes. M5 no quote, date or context is invented.
