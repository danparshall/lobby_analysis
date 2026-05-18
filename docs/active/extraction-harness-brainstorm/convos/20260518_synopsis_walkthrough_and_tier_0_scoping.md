# 20260518 — Review synopsis walkthrough and Tier 0 scoping

**Date:** 2026-05-18
**Branch:** extraction-harness-brainstorm

## Summary

Session opened with the user asking to walk through [`results/20260516_review_synopsis.md`](../results/20260516_review_synopsis.md) — the post-framing synopsis of the two parallel 2026-05-14 reviews. The walkthrough produced three substantive turns: (1) Fork 1 (EvidenceSpan duplication) resolved against the data flow, landing on **`retrieval_v2.EvidenceSpan` everywhere** with `models_v2.EvidenceSpan` retired as dead code; (2) the synopsis's H-F2 "missing orchestrator" finding reframed — the Ralph loop and the orchestrator are the same component, not distinct, so the load-bearing next move is building a minimal end-to-end pipeline before any of Plan A/B/C work; (3) the minimal pipeline scoped against **CPI 2015 vs OH 2015** as validation target, with a **Tier 0 smoke test** (1 chunk, no projection) preceding **Tier 1** (6 chunks, 6 de-jure CPI items, σ_noise via N=3 re-runs, first real Ralph-loop data point).

User instructed plan to be written for Tier 0 with Tier 1 scope as a forward-pointer. Plan output at [`plans/20260518_tier_0_minimal_pipeline.md`](../plans/20260518_tier_0_minimal_pipeline.md).

## Topics Explored

- **Fork 1: EvidenceSpan duplication.** Read both class definitions ([`models_v2/provenance.py`](../../../../src/lobby_analysis/models_v2/provenance.py) vs [`retrieval_v2/models.py`](../../../../src/lobby_analysis/retrieval_v2/models.py)). Walked through four candidate shapes (A: semantic-only; B: machine-only; C: wrap both; D: use `CrossReference` one level up). Initial recommendation was C; user pushed back twice toward "use the Citations API standard everywhere." Established that section_reference is **not derivable** from char_indices anywhere in the codebase — `chunks_v2` partitions compendium rows, not statute byte ranges; section_reference comes only from the retrieval agent's tool calls (`tools.py:38`, captured at `parser.py:72`). Combined with (a) Phase C reads cell values, not section refs, and (b) QA can join scorer spans against persisted retrieval `CrossReference`s at read time, the right answer is `tuple[retrieval_v2.EvidenceSpan, ...]` on `CompendiumCell.provenance`.

- **H-F2 reframe — Ralph loop IS the orchestrator.** Walked the end-to-end process (statute bundle → retrieval agent → brief-writer per chunk → scorer dispatch → parser → assemble SMR → Phase C projection → Δ vs ground truth). Identified the "scorer dispatch" step as the missing wiring. The synopsis treats the orchestrator as missing component #5; the user's reframe was that this is THE Ralph loop in skeletal form. Once a pipeline runs end-to-end once, the EvidenceSpan and axis_coverage forks resolve empirically rather than by debate.

- **Minimal pipeline target.** Picked OH 2015 vs CPI 2015 because CPI has the strongest ground truth (700 per-state-per-item cells = 50 states × 14 items; Sunlight 2015's 200 cells is the next-best, then everything else is sub-aggregate or weak-inequality only).

- **De-jure / de-facto split.** Identified that only **6 of CPI's 14 items are de-jure** (extractable from statute text); the other 8 are de-facto (require portal observation, Track B's domain). The legal-only pipeline on this branch can validate against the 6 de-jure items; de-facto half stays open per CPI projection doc Open Issue #5.

- **Chunk-set mapping for CPI's 6 de-jure items.** Applied the row-id renamer to CPI 2015's projection mapping doc (which uses pre-v2-freeze working names per C-F4 in the synopsis). The 6 items touch 6 chunks: `lobbying_definitions`, `registration_thresholds`, `registration_mechanics_and_exemptions`, `lobbyist_spending_report`, `principal_spending_report`, `enforcement_and_audits`. ~88 cells extracted per re-run to produce ~11 CPI-relevant cells.

- **IND_201 name resolution.** The projection doc names `lobbyist_spending_report_includes_compensation`, which has no exact v2 match. Resolution: v2's granularity-bias policy split it into `_includes_total_compensation` and `_includes_compensation_broken_down_by_payer`; the projection rolls up via boolean OR per the user-stated policy ("we always err towards more granularity, because we can always roll up"). The C-F4 synopsis-proposed mitigation script (`tools/check_mapping_doc_row_ids.py`) wouldn't catch this case — 1→2 splits aren't in `RENAMES` and aren't 1:1.

## Provisional Findings

- **`models_v2.EvidenceSpan` is dead code under post-Citations-API data flow.** Section reference doesn't belong on per-cell provenance; it belongs at the retrieval-agent-output level (`CrossReference`) and can be joined back at QA time. Storing it on every cell duplicates the retrieval agent's work and silently mis-models where the provenance hierarchy lives.

- **The synopsis's H-F2 finding understates what's blocking.** "Name a 5th component, the orchestrator" reads as a should-fix. The substance is that nothing currently dispatches an end-to-end pipeline. The orchestrator IS the next load-bearing module, not a should-fix on the side.

- **CPI 2015 de-jure half is a clean validation target.** Per the projection doc's Open Issue #5: "validate the de-jure half against published per-state scores first (cells populated from statute, no circularity); de-facto half stays open until practical-availability extraction can populate cells from primary evidence." Tier 1 inherits this scoping.

- **C-F4 has two failure modes, not one.** Pre-rename working names that the renamer catches via `RENAMES` (renamer fixes them mechanically). Pre-finalize working names that v2 SPLIT into multiple granular rows (renamer doesn't catch these; the projection doc itself needs updating to either pick one v2 row or roll up across N). The synopsis-proposed `check_mapping_doc_row_ids.py` script catches the first class but not the second.

## Decisions Made

- **Tier 0 — smoke test, this session's plan output.** One chunk (`enforcement_and_audits`, 2 rows → 2 legal cells extracted). No projection, no Δ vs ground truth. Just: does retrieval → brief-writer → scorer → parser wire up end-to-end and produce a valid partial `StateVintageExtraction`? Plan written: [`plans/20260518_tier_0_minimal_pipeline.md`](../plans/20260518_tier_0_minimal_pipeline.md).

- **Tier 1 — forward-pointer, separate plan to be written after Tier 0 lands.** 6 chunks covering CPI's 6 de-jure items, σ_noise via N=3 re-runs at fixed prompt-sha, real Δ vs CPI 2015 OH scores. First real Ralph-loop data point.

- **EvidenceSpan locked to machine.** `CompendiumCell.provenance: tuple[retrieval_v2.EvidenceSpan, ...]`. Pre-locks the synopsis's Fork 1 brainstorm gate; the Tier 0 plan implements the schema lock in Step 2 before wiring anything downstream. `models_v2.EvidenceSpan` deprecated this session; full deletion deferred to a follow-on plan (import audit non-trivial).

- **Phase C projection for IND_207 (and broader CPI 2015 projection) is parallel work on `phase-c-projection-tdd`.** User taking that branch. Not in scope for this branch's Tier 0; Tier 1 will import the projection function rather than stubbing locally.

- **Plan A/B/C from the synopsis are deferred.** The minimal pipeline is the next-load-bearing work; the Plan A quick wins, Plan B design forks (EvidenceSpan now resolved; axis_coverage resolves once Tier 1 surfaces partial-SMR shape empirically), and Plan C handoff notes can wait or run in parallel after Tier 0 lands.

## Results

(No analysis outputs this session — the deliverable is the plan doc linked under Decisions Made.)

## Open Questions

- Where will the OH 2015 statute bundle live in the worktree once symlinked? User said `~/data/statutes/OH/2015/` is the canonical location but the symlink isn't set up on this worktree yet.
- For Tier 0 success: is "pipeline ran end-to-end without crashing + produced 2 cells with non-null provenance + cell values type-check" sufficient, or do we want cell values hand-eyeballed for plausibility before declaring Tier 0 passed? (Plan currently includes the eyeball as a soft check.)
- Tier 0 dispatches retrieval with `hop=1` or `hop=2`? Retrieval brainstorm landed on 2 hops as default; minimal-cost Tier 0 might do 1. Tier 1 should be 2 either way.
- The `models_v2.EvidenceSpan` deletion follow-on plan — its own session, or fold into the Tier 1 plan?
