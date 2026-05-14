# 3-way consensus design for compendium 2.0 assembly

**Date:** 2026-05-06
**Branch:** compendium-source-extracts

## Summary

Began as a plan-review session over `plans/20260506_comp_assembly_via_regex.md` (the regex-based parallel assembly plan written at the end of the prior 2026-05-06 embedding session). The session went through three reframings:

1. **Critical review of the regex plan** surfaced concerns about cross-method comparison framing being biased toward embedding-as-baseline, undefined `compendium_role` assignment under the regex method, CPI_2015 noise threading through the dedup pipeline, and an unspecified PRI rule-writing chunk hidden inside step 6.

2. **User pushback on methodological purity:** the goal isn't an objective "ONE TRUE LIST" — it's creating a comprehensive set where rubrics with overlapping items (`"Disclosure required: lobbyist principal"` ↔ `"Is the lobbyist principal required to be reported?"`) collapse to a single canonical question. Most of the assistant's review concerns dropped as overthinking; what survived was the CPI_2015 upfront filter and the PRI rule pre-write. Plan was updated to lead with the LobbyView-for-states framing and the per-state-question goal — every canonical row is one disclosure question we ask of all 50 states.

3. **Pivot to manual grouping**, then **pivot to 3-method × 3-run consensus.** User proposed dropping the regex pipeline in favor of having an LLM (initially Claude in this session, then 9 subagents) read the 287 items and group them by judgment. The 3×3 design separates *method instability* (within-method variance across 3 runs of the same method) from *method disagreement* (between-method variance), giving sharper signal than any single method's output.

## Topics Explored

- Critical review of the regex plan: framing-strip mechanics traced through the existing prototype (`tools/normalize_state_items.py`); confirmed the rules already do "Disclosure required: X" → "X (disclosure)" and "Is X required?" → "X" — token-overlap dedup would cluster these — but PRI rules don't exist yet and Newmark's `(disclosure)` / `(prohibited)` suffixes interact non-trivially with similarity metrics.
- LobbyView-for-states framing: the README's headline ("LobbyView, for all 50 states") is the load-bearing context. The compendium IS the per-state question set; recognition that two rubrics ask the same question with different framing is exactly what enables the per-state matrix to be coherent.
- Methodological independence as the basis for triangulation: 2 methods that are too similar produce correlated outputs and triangulation buys nothing; the 3 methods need to be cognitively distinct for cross-method agreement to be informative.
- M3 candidate selection: top-down taxonomy (assistant initial suggestion) vs. paraphrase-then-group vs. FOCAL-anchored. User chose FOCAL-anchored after correcting the assistant's earlier flagging of "FOCAL has zero Prohibitions, minimal Personnel" as a blind spot — those are *not* disclosure-mechanism items, so anchoring on FOCAL biases toward what the project actually cares about (StateMasterRecord-populating fields).
- Local subagent dispatch via Task tool (MAX plan), not API key. Cost concern drops; parallel dispatch is fine.

## Provisional Findings

- The regex plan's cross-method-comparison framing was implicitly treating embedding as ground truth ("if embedding clustered items together but regex didn't, that's a recall miss for regex"). User's reframing made clear that disagreement is symmetric and the more useful product of running multiple methods is identifying ambiguity, not validating one method against another.
- Manual grouping by judgment (LLM doing the same dedup the regex method would do, but with judgment instead of rules) is plausibly stronger than the regex pipeline for this corpus, because the hard parts of regex (PRI rule writing, Newmark suffix handling, CPI filtering) are all judgment calls dressed as engineering. Provenance is preserved automatically by the long-format mapping output (`source_paper, source_id, ..., group_id, group_label`).
- 3-method × 3-run is meaningfully different from 1-method × 9-run: the 3-method version separates two distinct sources of variance (method instability vs. method disagreement), whereas 9 runs of the same method only measure run-to-run instability of that one method.
- FOCAL's 50 indicators are designed as a comprehensive disclosure-transparency checklist for cross-jurisdiction comparison. The "blind spots" critique against FOCAL anchoring (no Prohibitions, minimal Personnel) only applies if those items are in scope for the project — they are not. FOCAL anchoring biases the M3 output toward exactly what compendium 2.0 needs as its load-bearing core.
- The `~150 items` expected output size is the user's gut estimate, not derived from a model. The implementing agent should treat it as a soft anchor (≤80 = chained over-merging; ≥250 = under-merging) but defer to the eyeball-check protocol over the count.

## Decisions Made

| topic | decision |
|---|---|
| Plan supersession | `20260506_comp_assembly_via_regex.md` is superseded; replacement is `20260506_comp_assembly_3way_consensus.md`. The regex plan is preserved with a SUPERSEDED banner for traceability of the methodological pivot. |
| Method 1 (M1) | Cluster-anchored: subagent reads the 28 embedding clusters at sim ≥ 0.68 as starting prior, validates / splits / merges by judgment, walks unclustered items individually. |
| Method 2 (M2) | Blind: subagent reads 252 items only, groups by pure judgment with no priors. |
| Method 3 (M3) | FOCAL-anchored: subagent uses FOCAL's 50 indicators as the backbone, absorbs other rubrics into FOCAL groups OR creates "extension" groups (e.g. Opheim's enforcement battery → extension). |
| Replication | 3 runs per method = 9 total subagent dispatches. |
| Subagent dispatch | Local via Claude Code Task tool (MAX plan), `subagent_type="general-purpose"`. NOT via Anthropic API. |
| Output schema | Long-format: `source_paper, source_id, source_text, group_id, group_label`. Uniform across all 9 runs so consensus tooling is straightforward. |
| Consensus tooling | `tools/consensus_grouping.py` computes per-pair agreement count (0–9 across the 9 runs) + per-method counts; produces strict (≥8/9), loose (≥6/9), and human-review (3–5/9) views. |
| CPI_2015 handling | Filter upfront in pre-stage script — 15 of 16 rows are non-lobbying-domain noise; only the single Lobbying-Disclosure row is in scope. |
| PRI inclusion | IN scope for this run, per the 2026-05-06 partial PRI clearance (`feedback_pri_not_privileged.md` memory). PRI loaded from `results/items_PRI_2010.tsv` (separate file from the 8-rubric `cross_rubric_items_clustered.csv`). |
| Plan-doc next step | Implementing agent (next session, possibly user) follows the new plan: pre-stage, write briefs, dispatch 9, validate, run consensus tool, surface to user. |

## Mistakes recorded

1. **Assistant initially over-engineered the regex plan critique.** Concerns 1, 2, and 4 of the initial review (cross-method baseline asymmetry, undefined `compendium_role` under regex, similarity-metric-as-user-question) were methodological perfectionism that the user's "we don't need rigorous justification" framing made obviously misplaced. The surviving concerns (CPI upfront filter, PRI rule pre-write, Newmark suffix interaction) were the actually-load-bearing ones. Lesson: when the user has already framed the goal as "fairly comprehensive set, judgment is fine," don't relitigate methodology.
2. **Assistant confabulated derivation math** for the ~150 expected-size estimate (claimed it was "the rough fixed-point of each canonical question appearing in 2-3 rubrics on average"). User clarified it was gut instinct only. Plan updated to flag the estimate as gut anchor, not target.
3. **Assistant initially flagged FOCAL's "zero Prohibitions, minimal Personnel" as a blind spot for M3.** User correctly noted that those are out of project scope (statutory restrictions, not disclosure mechanisms — they don't populate SMR cells). FOCAL anchoring biases TOWARD what the project cares about. Lesson: project scope is "disclosure-related items, what populates the StateMasterRecord" — keep this front-of-mind when evaluating any rubric's coverage.

## Results

- Plan doc: [`plans/20260506_comp_assembly_3way_consensus.md`](../plans/20260506_comp_assembly_3way_consensus.md) — the active execution plan.
- Plan doc (superseded): [`plans/20260506_comp_assembly_via_regex.md`](../plans/20260506_comp_assembly_via_regex.md) — preserved with SUPERSEDED banner.

No code or data artifacts produced this session — this was a planning conversation. The plan is the deliverable.

## Open Questions (deferred to implementing agent or follow-up sessions)

- Within `tools/build_usa_tradition_input.py`, the exact `indicator_id` for the single in-scope CPI_2015 row needs to be filled in by inspection of the 16 rows. The plan's pre-stage code marks this with a TODO.
- Method-brief tuning: if the first dispatch returns degenerate output (all-1-group or 252-singletons), the brief needs tightening before re-dispatch. The plan budgets 2 iteration cycles; if the corpus turns out to be harder than that suggests, the plan should be revisited.
- After consensus: who picks the canonical-text representative within each strict-consensus cluster? The plan's default is "FOCAL phrasing if available, else longest, else alphabetical first" — implementing agent can document the rule chosen and surface for user override.
- The 3-way consensus is for the USA-tradition rubrics only. Whether to do a parallel pass on European-tradition rubrics (as `cmp_*` reference items) is a separate decision deferred to a follow-up plan.
