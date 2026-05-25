# Handoff: `extraction-harness-brainstorm` post-framing review

**Date written:** 2026-05-14
**Originating convo:** [`../../convos/20260514_research_arc_doc.md`](../../convos/20260514_research_arc_doc.md) on `extraction-harness-brainstorm`
**Parallel review:** [`20260514_post_framing_compendium_review_handoff.md`](20260514_post_framing_compendium_review_handoff.md) — audits Compendium 2.0 against the same framing. Reviewers stay in lane; cross-branch reading not required.
**Framing reference:** [`docs/RESEARCH_ARC.md`](../../../../RESEARCH_ARC.md) on main (commit `86dc02e`).

## Context for the spawn

The 2026-05-14 research-arc review session (originating convo above) clarified the project framing in ways that pre-date most of the harness branch work. The branch has 3 of 4 extraction components shipped (`models_v2`, `chunks_v2`, `retrieval_v2`) under TDD; the 4th (`scoring_v2`) was brainstorm-locked the morning of 2026-05-14, with the framing-clarification landing the afternoon of the same day. Implementation of `scoring_v2` has not yet started.

The purpose of this review is **not** to re-open the just-locked `scoring_v2` brainstorm. It is to surface findings that, under the corrected framing, should change either (a) the scope of the still-to-write `scoring_v2` implementation plan, or (b) the priorities for downstream work (Phase C consumer ergonomics, Prong 2 inheritance budget, Ralph-loop glue). Read-only; report-only; commit one file on the branch you are spawned in.

---

## Prompt (self-contained — execute below as if no other context exists)

You are auditing the `extraction-harness-brainstorm` branch against a recently-clarified framing of what the project is for. You have zero prior session context; this prompt is self-contained.

### What the project is (clarified 2026-05-14)

Read `docs/RESEARCH_ARC.md` on main first. Two load-bearing claims:

1. **Prong 2 + Prong 3 is the product.** Prong 1 (statute → SMR) is *upstream scaffolding* — typed-cell schema reference makes Prong 2 cheaper; the legal-vs-practical gap is itself a research artifact.

2. **The Ralph loop is Phase C–driven.** Objective: `loss(prompt) = Σ over (state, vintage, rubric) |f_rubric(SMR) − published_score|`. Noise floor (`σ_noise` from independent re-runs) is a prerequisite for coherent prompt iteration.

The harness branch has 3 of 4 extraction components shipped (`models_v2`, `chunks_v2`, `retrieval_v2`) and `scoring_v2` brainstorm-locked but not yet implemented. Most of this was built before the corrected framing was articulated. Your job is to check whether what we built supports the framing we now have.

### What to read (in this order — 1-2 hours total)

1. `docs/RESEARCH_ARC.md` (~213 lines).
2. `docs/active/extraction-harness-brainstorm/RESEARCH_LOG.md` (~270 lines, newest first) — branch trajectory.
3. The 3 shipped v2 modules + the in-flight prompt:
   - `src/lobby_analysis/models_v2/`
   - `src/lobby_analysis/chunks_v2/`
   - `src/lobby_analysis/retrieval_v2/`
   - `src/scoring/retrieval_agent_prompt_v2.md`
4. The most-recent brainstorm + its handoff (the `scoring_v2` plan-write brief):
   - `docs/active/extraction-harness-brainstorm/convos/20260514_brief_writer_brainstorm.md`
   - `docs/active/extraction-harness-brainstorm/plans/_handoffs/20260514_brief_writer_impl_plan_write_handoff.md`
5. The 4-component impl plans (reference, not exhaustive read):
   - `.../plans/20260514_v2_pydantic_cell_models_implementation_plan.md`
   - `.../plans/20260514_chunks_implementation_plan.md`
   - `.../plans/20260514_retrieval_implementation_plan.md`

### Questions to answer

**Q1.** Does `models_v2.StateVintageExtraction` make `f_rubric(SMR) → score` ergonomic for Phase C consumers? Cross-reference the projection mapping docs at `docs/historical/compendium-source-extracts/results/projections/`. Will Phase C fight the cell-access pattern (`cells: dict[(row_id, axis), CompendiumCell]`) or is it a natural fit?

**Q2.** Where in the architecture does the Ralph loop's noise-floor measurement live? The loop needs: (a) call `extraction(prompt, state, vintage) → SMR` N times, (b) call Phase C projections, (c) compute scalar `loss`, (d) compare runs across prompt versions. None of the 4 harness components is positioned to do (a)-(d). Is glue code expected to live somewhere? If not, is that a gap that should land in the `scoring_v2` impl plan?

**Q3.** Practical-axis reuse: how much of `retrieval_v2` / `scoring_v2` is statute-coupled vs portal-agnostic? Prong 2 inherits primitives from Prong 1. Specific call-outs welcome (e.g., "Citations API document-block construction is statute-text-shaped; portal HTML/PDF needs different handling").

**Q4.** Scale failures: is the code positioned to surface them cleanly? The retrieval brainstorm flagged blind spots on Citations API + tool-use composition under longer statutes and longer tool-call chains. T0 + T1 pass; T2+ hasn't run. Will failures emit useful diagnostics, or fail silently?

**Q5.** Anything in the brief-writer / `scoring_v2` brainstorm lock that the corrected framing should reopen? The brainstorm was 2026-05-14 morning; framing-clarification was the afternoon. Re-read the 10 locked Q's + 2 pushbacks. Any lean on the now-corrected framing (e.g., Prong 1 as product)? Surface open questions; do NOT propose new locks.

**Q6.** The retrieval impl plan's Phase 7 "pause-and-surface" directive triggered cleanly on T1 (the fixture-decouple incident). Is the same directive present in the upcoming `scoring_v2` impl plan brief at the handoff? If not, should it be?

### Output

Save your report to:
`docs/active/extraction-harness-brainstorm/results/20260514_post_framing_review.md`

Structure:

```markdown
# extraction-harness-brainstorm post-framing review

**Date:** 2026-05-14
**Framing reference:** `docs/RESEARCH_ARC.md`
**Originating handoff:** `docs/active/extraction-harness-brainstorm/plans/_handoffs/20260514_post_framing_harness_review_handoff.md`

## Top 3-5 findings that should change what we work on next

(Severity-tagged: BLOCKER / SHOULD-FIX / OBSERVATION. Rank by load-bearing-ness.
If fewer than 3 meaningful findings, say so — don't pad.)

## Q1. Phase C ergonomics of StateVintageExtraction
## Q2. Ralph-loop glue location
## Q3. Practical-axis reuse budget
## Q4. Scale-failure diagnostics
## Q5. Scoring_v2 brainstorm decisions to reopen
## Q6. Pause-and-surface directive for scoring_v2

## Out of scope / not checked
```

### Constraints

- **Read-only.** No code or doc edits beyond writing your report.
- **Commit your report on whatever branch you are spawned in.** Do not push. Do not open PRs. Do not modify STATUS.md or RESEARCH_LOG.md.
- **Multi-committer awareness.**
- **No decoration**, no emoji, no preamble. Severity tags only.
- **If a question has no meaningful finding, say so.**
