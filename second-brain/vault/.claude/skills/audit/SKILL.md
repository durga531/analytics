---
name: audit
description: Audits other models' and reviewers' outputs like a senior partner and defends challenged numbers, grading each claim as holds, breaks or unverifiable before merging the best. Use when __OWNER__ says evaluate both, check this number, reconcile, validate or disprove.
model: __TOP_MODEL__
effort: high
argument-hint: <outputs, file or figure to test> [engagement]
---
# /audit
A claim-by-claim verdict on outputs from other models, tools or reviewers, or on a challenged number, then the merged or defended version. Routing: top tier (recurring asks 15 and 16, and the reconciliation half of 17).

## Read first
- Latest version of every output in scope and of the working file it feeds (M6); list each with its source tool or author and date.
- __OS_DIR__/output-standards.md: Deck rules (Numbers and evidence; Process), Excel and data rules, Anti-hallucination, and the Equity research standard or Resume rules when the output is one of those.
- __OS_DIR__/templates.md: T2 (maker-checker rubric, FORGE), T3 (independent review brief), T43 (number classes).
- __OS_DIR__/active-areas.md: the area the output belongs to (status, good output, rejected), including errors caught in earlier rounds.
- __OS_DIR__/thinking-patterns.md: Challenge vs execution (external reviews and third-party frameworks are challenged, not executed); Closed debates.

## Steps
### Model-output audit (ask 15)
1. Read every version side by side, Claude's own included, with no home bias.
2. Stress-test each statement, data point and analysis as a senior partner would before changing anything: true, sourced, computed correctly, specific to this case, decision-relevant.
3. Recompute every calculation and trace every figure to its source; judge whether a third-party framework holds up and deserves to be used. For a build by another tool, give the verdict slide by slide.
4. Send the versions to critic for the eight T2 gates and, for slides, the T3 house rules.
5. External review (a reviewer's or another tool's critique of __OWNER__'s work): present the findings and discuss; change nothing until __OWNER__ agrees.
6. Merge the best version and list what came from where, what was cut and why.
### Number defence (asks 16 and 17)
1. Restate the challenged figure with its definition, unit, period and scope.
2. Re-derive it with a breakup that sums to the total, each component with a source.
3. Reconcile conflicting shares by definition (what is counted, on which base) before calling either wrong.
4. Before trusting a new data cut, reconstruct its weights and validate them against the published pack within the tolerance output-standards.md sets; label footprint-based estimates as such.
5. Label every figure with its T43 class and say whether it is directional or exact.

## Rules enforced here
- Check calculations and units: every figure is recomputed in its stated unit and per-unit basis, and one that fails the recompute breaks. When merging, content __OWNER__ or the partner removed stays removed and is never revived from another version [A15].
- Insight over pivots: an output that only restates pivot-level cuts of the data is graded description, not insight; the merged version keeps the findings that say why and what to do [A19].
- Unverifiable claims are cut, not caveated; a fabricated source or number in any version is named as fabricated.
- Only the latest corrected figure stands: a number from __OWNER__'s own earlier deck or file is challenged like any other source once a corrected version exists, and never carried into the merge.
- A sell, trim, exit, reduce, stop-loss or tax-loss suggestion in an audited equity output is flagged and never merged.
- A resume number outside the locked fact base, or a kill-list claim, is flagged and removed.

## Delegate
- Lookups and validate-or-disprove checks to runner: each fact back with its source and date.
- T2 gate grading and T3 house-rule checks to critic, which grades and never rewrites.
- Filing, transcript and data pulls for a re-derivation to runner; the reconciliation logic stays here.

## Output
- Verdict table: Claim | Version | Holds, breaks or unverifiable | Evidence and source | Fix.
- Number defence: the breakup table with a source and T43 class per component, then the one-line defence __OWNER__ can give in the room.
- Then the merged version with its provenance list; for an external review, only after agreement.
- Saved in `03-Work/<Engagement>/` when the work belongs to an engagement, with defended figures added to the hub's sources.
- M1 no em dashes. M2 a sell-type verdict is never merged. M4 resume numbers only from the fact base. M5 nothing fabricated; "I do not have reliable data on this" where data is missing. M6 audit the latest version and say which.
