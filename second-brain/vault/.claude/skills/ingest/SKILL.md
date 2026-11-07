---
name: ingest
description: Clears 01-Inbox oldest first, classifying, filing, linking and archiving each item; logs actions in T5 form, queues corrections verbatim, sends transcripts to /diagnose and holds unclear items with one question. Use when __OWNER__ says ingest, clear the inbox or file these.
model: __MID_MODEL__
effort: medium
context: fork
agent: drafter
argument-hint: <item or subfolder, default all of 01-Inbox>
---
# /ingest
Every item in `01-Inbox/` filed, linked and archived, or held with one question. Routing: mid tier, forked to drafter (inbox rhythm).

## Read first
- `01-Inbox/`, oldest first. Skip `Folder Mapping - Proposed.md`; it belongs to /onboard.
- `.claude/guard/config.json`: the existing topic folders and the role each one serves.
- __OS_DIR__/active-areas.md: the live engagements and areas, so material lands in its own folder.
- __OS_DIR__/templates.md: T5 (decision and action log).
- `09-Reviews/Lessons Queue.md`, the note templates in `08-Library/Templates/`, and the rules file in `.claude/rules/` for each destination (work, invest, self, learn, people) before writing there.

## Steps
1. Classify each item: engagement material, investing, personal, knowledge, person, framework or prompt, correction or preference, transcript or stakeholder feedback, task.
2. File it: engagement material to `03-Work/<Engagement>/`; investing to `04-Invest/`, linked from `04-Invest/Theses/<TICKER>.md` when that note exists and never written into it; personal to `05-Self/`, where it stays; knowledge to the matching existing topic folder, else `06-Learn/`; people facts to `07-People/`; frameworks to `08-Library/Frameworks/`, prompts and tool notes to `08-Library/Prompts and Tools/`.
3. A working file (pptx, xlsx, docx) keeps its version in its name and gets a row in the hub's working-files table, newest first, so the next build finds the latest version.
4. Extract only what the item states: actions in T5 form (Owner | Action | When) into the hub's action table, or as a dated task in the filed note; decisions as T5 decisions; facts and commitments into the person's note.
5. Transcripts and stakeholder feedback: filed verbatim into a Meeting note in the engagement folder and flagged for /diagnose, which owns T4 (stakeholder feedback diagnosis). No summary and no reading for meaning here.
6. Corrections and preferences: a pending row in the lessons queue, quoted verbatim with date and context, by the /lesson procedure; never written into the OS files.
7. Link each filed note to its hub or area note and to the people it names. Frontmatter carries type, status, created, updated, tags and source; the note name is unique in the vault.
8. Archive the raw item to `99-Archive/Inbox/` and link it as the source. Never delete anything.
9. An ambiguous item stays in `01-Inbox/` with a one-line question at its top.
10. Reconcile: items at the start equal items filed plus items held; name any gap.

## Rules enforced here
- Data __OWNER__ collected, scraped or verified is filed as __OWNER__'s own primary work, never as supplied, third-party or vendor data [B4].
- The source field names the primary producer of each data point, traced past any aggregator or intermediary that repackaged it; a producer that cannot be traced reads "primary source not traced", never a guess [B5].
- Classify, file and log only: no analysis, diagnosis or rewording; the item's own words are kept.
- Client material stays inside its engagement folder; no web lookups on it.
- A note that already exists is appended to, never overwritten.

## Delegate
- Runs forked as drafter and delegates nothing further. Hand-offs it returns: /diagnose for each transcript, /equity for an item that may move a call, /learn for a source worth an atomic note, and the queued lesson rows for __OWNER__ to approve.

## Output
- Return at most ten lines: counts by destination, lessons queued, hand-offs with note links, then each held item with its question.
- M1 no em dashes. M2 investing items keep the verdict vocabulary; no sell, trim or exit wording is added. M4 a resume number found in the inbox is filed as found and flagged, never added to the locked fact base in T50 (resume architecture and fact base). M5 no source, date or owner is invented: an untraced source says so, a missing date or owner reads "[confirm]". M6 working files are filed so the latest version is the one the next build finds.
