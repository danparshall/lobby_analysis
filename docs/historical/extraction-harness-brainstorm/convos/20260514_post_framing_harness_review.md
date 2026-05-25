# Post-framing harness review (spawn + result)

**Date:** 2026-05-14
**Branch:** extraction-harness-brainstorm
**Originating handoff:** [`plans/_handoffs/20260514_post_framing_harness_review_handoff.md`](../plans/_handoffs/20260514_post_framing_harness_review_handoff.md)
**Result:** [`results/20260514_post_framing_review.md`](../results/20260514_post_framing_review.md) (committed in `0ccbb86`)
**Parent session ran on:** `main` worktree (orchestration-only); review work lives on this branch via spawned agent.

## Summary

Thin orchestration session. The user invoked this session from `main` with a self-contained brief: spawn the harness reviewer against the post-framing-review handoff that the prior session left in `plans/_handoffs/`. The handoff was authored after the 2026-05-14 research-arc doc clarified the project framing (Prong 2 + Prong 3 is the product, Prong 1 is upstream scaffolding; Phase C is the Ralph-loop eval function, not a sanity check) and asked: under this corrected framing, do the 3 shipped harness components (`models_v2`, `chunks_v2`, `retrieval_v2`) and the brainstorm-locked-but-unimplemented `scoring_v2` actually support what we now know we need?

A `general-purpose` subagent was spawned with the absolute handoff path. The agent read RESEARCH_ARC.md, the branch RESEARCH_LOG, the 3 shipped v2 modules + the in-flight prompt, the most-recent brainstorm + handoff, and the 4 component impl plans; answered the 6 questions in the handoff; saved a report to `results/` and committed it on this branch as `0ccbb86`. The agent honored the read-only constraint, did not push, did not touch STATUS.md or RESEARCH_LOG.md. The parent session (this convo) handles those updates.

## Topics Explored

- Whether `StateVintageExtraction.cells: dict[(row_id, axis), CompendiumCell]` is ergonomic for Phase C projection consumers (Q1).
- Where the Ralph-loop noise-floor measurement and per-rubric loss aggregation will live, given none of the 4 harness components is positioned for it (Q2).
- How much of `retrieval_v2` / `scoring_v2` is statute-coupled vs. portal-reusable for the eventual practical-axis sibling (Q3).
- Whether the code surfaces scale failures cleanly at T2+ (Citations API + long tool-use chains) or fails silently (Q4).
- Whether any of the 10 `scoring_v2` brainstorm locks (or the 2 pushbacks) should be reopened under the corrected framing (Q5).
- Whether the retrieval impl plan's Phase-7 "pause-and-surface" directive carries forward to the upcoming `scoring_v2` impl plan brief (Q6).

## Provisional Findings

The reviewer surfaced 3 findings ranked by severity (full text in `results/20260514_post_framing_review.md`):

1. **[SHOULD-FIX] `EvidenceSpan` is two incompatible public classes.** `models_v2.EvidenceSpan` (section_reference + 200-char `quoted_span`) and `retrieval_v2.EvidenceSpan` (citation_type + char/page/block indices) are both exported as public names. The `scoring_v2` brainstorm Q8 locked `CompendiumCell.provenance: tuple[EvidenceSpan, ...]` without naming which class. The natural producer (Citations API → retrieval-shaped) and natural consumer (Phase C projection → semantic-shaped) disagree. Cannot be unified by aliasing; needs explicit decision (pick one + adapter, or carry both) before the `scoring_v2` impl plan is written.

2. **[SHOULD-FIX] Ralph loop has no home in the 4-component architecture.** Noise-floor measurement (N independent re-runs at fixed prompt-sha) and per-rubric loss aggregation across `(state, vintage)` aren't ownable by any of `models_v2` / `chunks_v2` / `retrieval_v2` / `scoring_v2`. "The orchestrator" is uniformly named as out-of-scope in chunks (line 147), retrieval (line 130), and brief-writer (lines 86, 185) brainstorms — but is the thing the Ralph loop requires. Recommendation: name the orchestrator as the next-component-after-`scoring_v2` and track it explicitly (otherwise post-merge it gets rediscovered as a gap).

3. **[OBSERVATION] Practical-axis seam in `StateVintageExtraction`.** Legal-only scoring produces SMRs missing the 50 practical-only cells + 5 dual-axis practical halves. The brainstorm Q6 lock correctly defers practical-axis brief-writer, but the cell-spec registry / chunks manifest / `StateVintageExtraction.cells` treat the 186-cell space as flat. Without a typed-state distinction (`partial=True` flag, or separate `LegalAxisExtraction` / `PracticalAxisExtraction` merging into `StateVintageExtraction`), Phase C consumers can silently project from half-filled SMRs.

The reviewer additionally found that the Phase C dict-access pattern is a natural fit (Q1) but recommends a small accessor helper (`smr.get_cell(row_id, axis)`) to avoid 8 projection modules re-implementing defensive lookups. Reuse budget from `retrieval_v2` to a future portal-axis sibling is ~30-40% structural — kwargs-returning brief-writer pattern, parser shape, cell-class dispatch all carry; tools, document-block construction, and prompt content are statute-specific (Q3). Scale-failure diagnostics will not fail silently at T0/T1 but have one quiet failure mode at T2+: unknown tool names get skipped silently after citation-buffer reset (intentional but masks model-hallucinated tool names like `record_cross_ref`); zero-output chunks won't raise (Q4). Of the 10 `scoring_v2` brainstorm locks, only Q8 (provenance EvidenceSpan type) needs reopening; Q3 (retrieval annotations in user text) is borderline for Ralph reproducibility — `ExtractionRun.prompt_sha` should clarify whether it's `prompt_sha` alone or `(prompt_sha, retrieval_output_sha)` so two runs at the "same" prompt with different retrieval don't read as same-prompt noise (Q5). The pause-and-surface directive flow is wired into the brief-writer handoff at lines 72, 192, 210 — the concrete bullet list is the impl-plan-writer's deliverable (Q6).

## Decisions Made

None this session — this was a read-only audit producing findings, not locks. The 3 open questions for user input are surfaced and waiting:

1. Which `EvidenceSpan` shape goes into `CompendiumCell.provenance`? (Finding 1 / Q5 Q8 reopen.)
2. Does the `scoring_v2` impl plan name Ralph-loop glue as the next component, or are the four components meant to suffice? (Finding 2 / Q2.)
3. Should `ExtractionRun.prompt_sha` also hash retrieval output, given Q3's lock puts retrieval annotations in uncached user text? (Q5 borderline.)

## Results

- [`results/20260514_post_framing_review.md`](../results/20260514_post_framing_review.md) — full review report (committed in `0ccbb86`)

## Open Questions

The three above for user input before the `scoring_v2` impl plan gets written. Additionally:

- Whether to track the practical-axis `partial=True` / typed-state-distinction recommendation (Finding 3) as a follow-up that lands before the practical-axis sibling brainstorm, or after.
- Whether to add a minimum-emit-count diagnostic ("if scoring a 10-row chunk returns 0 `record_cell` calls, raise") to the upcoming `scoring_v2` impl plan, in addition to the pause-and-surface directive that's already inherited from retrieval (Q4 recommendation).
- Out-of-scope on this branch but flagged by the review: the practical-axis sibling brainstorm will need its own framing review against the same Ralph-loop / Phase-C eval framing — none of the legal-axis review's findings translate directly.

## Notes on session shape

The orchestration was thin enough that no Nori pre-flight reads were performed on `main` before spawning the subagent — the handoff was self-contained per its own design ("execute below as if no other context exists"). All actual document-reading happened inside the subagent. The subagent (`a00a165fb531e34aa`) is still alive and can be resumed via SendMessage if follow-up is needed without re-spawning.
