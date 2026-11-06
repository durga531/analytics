---
paths:
  - "03-Work/**"
---
# Client and engagement work

Applies to every deliverable for a client, a firm or a prospect. output-standards.md (Deck rules, Excel and data rules, Process) is the rulebook; this file says how to apply it here.

## Before any build (M6)
- Open the engagement's area in active-areas.md: status, what good output looked like, what was rejected.
- Open the latest version of the working file; if several exist, use the one __OWNER__ last shared or edited, and say which.
- Check templates.md for the engagement's own rule set (for example T15, when that engagement) and the template it names. The template __OWNER__ names is the authority: template slides used as they are, content customised [C4] [C5]. T18 applies only when its template is the working one.
- Read the engagement's decision log (T5) so removed slides stay removed and agreed templates hold [A15].

## Always
- A final deck, never a version-control deck (M3); partner test on every slide: why is this here [A1].
- Change only the slides or sections named; never redesign finalised slides; replacement slides go out standalone [A10] [A13]. After a build, list which slides changed (`python3 .claude/tools/deck_diff.py <new file>`).
- A change that touches agreed structure: think and tell first [A14]. Data conflicts and judgment calls: surface them.
- The base-deck and client vocabulary; no informal, folksy or extreme words; no abbreviations; no term or ID before it is defined [A13] [A17] [A18].
- Every figure traces to a source; source notes name the primary producer, never the workbook or an aggregator; unvalidated figures carry their tag [B5].
- Private instructions, reviewer names and thinking-direction notes never appear in a deliverable [B6].

## Working files in the engagement folder
- `<Engagement>.md` hub in the active-areas format (Status, Good output, Rejected, Sources) plus decisions, next steps, owners and data requests (T35).
- Meetings: T34 talk track before, T5 decision and action log after. Transcripts and stakeholder feedback go to /diagnose (T4).
- Reviews of our own work are logged in `<Engagement> Review Log.md` in the T3 format.

## Confidentiality
Client names and numbers stay in the engagement folder and never go into web searches or anything outside the vault. Benchmarked companies and consulting clients are anonymised in client material as output-standards.md requires. Firm AI-use and outside-engagement policy are live constraints.
