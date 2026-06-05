# 20260514 — Research arc doc

**Date:** 2026-05-14
**Branch:** extraction-harness-brainstorm

## Summary

Started as a status query ("what's left on `extraction-harness-brainstorm`?") and evolved into a research-arc review that landed one repo-level doc on main. The status portion confirmed the branch state (3 of 4 extraction components shipped — `models_v2`, `chunks_v2`, `retrieval_v2`; brief-writer/scorer-v2 brainstorm locked today; impl plan write outstanding). The arc-review portion produced three substantive reframes vs. how the agent had been holding the project mentally, then a written `docs/RESEARCH_ARC.md` to memorialize the corrected framing.

Three reframes worth tracking, in order:

1. **Phase C is the Ralph-loop evaluation function, not a downstream consumer.** User correction: there is no published 50-state ground-truth at the typed-cell level, so projecting our extracted cells back into each rubric's published scoring rule and comparing to published scores is the only tractable accuracy signal. The "locked rubric order" then reads (loosely) as the eval-strength gradient for Ralph iterations — strongest ground truth first.
2. **Prong 2 + Prong 3 is the product; Prong 1 is upstream scaffolding.** User correction to the agent's mistakenly-flat three-prong framing. The SMR's job is to encode what each state's regime *legally requires*; the gap between that and what portals *actually expose* (Prong 2's domain) is itself a research artifact journalists and activists can use. Prong 1 also makes Prong 2 dramatically cheaper (shared typed-cell schema across 50 state pipelines instead of 50 bespoke extractors). "Stairs of leverage" pattern: prior-art rubrics → Prong 1 (via Phase C); Prong 1 → Prong 2.
3. **Locked rubric order is mostly convenience, not a rigid signal-strength optimization.** User correction to the agent's earlier "signal-strength gradient" framing. Order respects dependencies (Newmark 2005 reuses Newmark 2017's cells; HG 2007 waits on Track A's HG retrieval sub-task) and starts where ground truth is strongest, but reordering on empirical results is fine.

Doc subsequently extended with a concrete Ralph-loop objective function, noise-floor prerequisite, and three-risk register after user concretized the loop shape.

## Topics Explored

- Branch state: what's left on `extraction-harness-brainstorm`. Three components shipped (cells, chunks, retrieval) including desktop-T1 clearance the agent flagged as docs-divergent at session start (RESEARCH_LOG had since been updated by the unseen 2-commit fast-forward, resolving the divergence).
- The overall research arc: compendium → 3 tracks (`oh-statute-retrieval` / `extraction-harness-brainstorm` / `phase-c-projection-tdd`) → within Track B, 4 sub-components.
- Phase C's role relative to Prong 1: downstream sanity-check (agent's initial framing) vs Ralph-loop evaluation function (user's correction).
- The three-prong framing: roughly-coequal pipeline stages (agent's initial framing) vs P2+P3-product / P1-scaffolding (user's correction).
- Existing repo docs surveyed for an arc-overview: `README.md`, `STATUS.md`, `docs/active/ARCHITECTURE.md` (misnamed — actually Prong-3-scoped), `docs/LANDSCAPE.md`. **No mermaid diagrams anywhere in repo** prior to this session.
- Concrete Ralph loop objective: `loss(prompt) = Σ over (state, vintage, rubric) |f_rubric(SMR) − published_score|`. Single scalar.
- Noise floor as prerequisite: `Var(loss | fixed prompt)` from independent re-runs sets a floor below which prompt iteration is chasing noise; distinct from Track A's across-vintage stability check.
- Three named risks for the Ralph loop: implicit weighting in `Σ |diff|` across rubrics of unequal size; Goodhart on projection-distance (rubrics have degenerate solutions, optimizer can't distinguish "got cells right" from "got cells convenient"); cost asymmetry (single-state OH-only Ralph ≈ $4/iter vs 50-state ≈ $150/iter under ARCHITECTURE.md's $50–500/mo budget).
- "Ralph loop" etymology check: agent flagged uncertainty about the reference (best guess: Geoff Huntley's "Ralph Wiggum" blog pattern — dumb-but-persistent loop). User confirmed "close enough" and provided concrete loop shape.
- Cherry-pick path for the repo-level doc: stage on this branch, fast-forward main first, cherry-pick onto main, push both.

## Provisional Findings

- The "extraction-harness-brainstorm is one impl-plan + one TDD-impl session away from a complete single-state legal-axis harness" framing the agent surfaced at session start is *extraction-complete*, not *quality-validated*. The first Ralph-loop iteration requires three-branch convergence: `scoring_v2` (this branch) + CPI 2015 C11 projection (`phase-c-projection-tdd`) + OH 2015 statute bundle (`oh-statute-retrieval`). Worth naming as a cross-track milestone.
- Track A's within-state across-vintage stability check is load-bearing for Goodhart defense — it's the only signal that *doesn't* go through a rubric, so it's an out-of-distribution sanity check on the Ralph optimizer. Should be treated as a co-equal signal, not a footnote.
- Phase C is not *strictly* required for Prong 1 to ship — Prong 1 produces SMRs regardless. It is required for Prong 1 to be *measurably* good. Under the corrected scaffolding framing, that's not "Prong 1 is unmeasurable so it's worthless"; it's "Prong 1 quality matters in proportion to how much we lean on the legal-vs-actual gap as a finding."

## Decisions Made

- **New repo-level doc landed: `docs/RESEARCH_ARC.md`** (213 lines, two mermaid diagrams: three-prong overview + Ralph loop). Committed on this branch as `ee75e3a` then cherry-picked to main as `86dc02e`; both pushed.
- **Mid-session fast-forward** of the 2 unseen commits on `origin/extraction-harness-brainstorm` (`5f262e9` + `7d6f20d` — desktop T1 cleared + fixture decouple) before the new doc commit. No conflicts; no file overlap.
- **README.md discoverability link deferred** per user preference ("yeah it's fine for now"). The doc lives at `docs/RESEARCH_ARC.md` but isn't linked from README's repo-layout section yet.
- **Rubric-order framing softened** in the doc: described as convenience + dependency-respect, not a rigid signal-strength gradient.
- **Practical-axis cells documented as Prong-1-schema / Prong-2-populated**: SMR schema carries both legal and practical axes; Prong 1 fills legal; Prong 2 fills practical. Today's brief-writer brainstorm's Q6 deferral aligns with this seam.

## Results

The session's output is the doc itself, not analysis artifacts. Reference: [`docs/RESEARCH_ARC.md`](../../../RESEARCH_ARC.md) (repo-level, also on main as of `86dc02e`).

## Open Questions

- **Score-distance threshold for "Prong-1-validated."** Concretized in the doc as σ_noise units (clear >Nσ on the noise floor to count), but what N is left open. Probably depends on downstream use — publishing legal-vs-actual gap as a finding requires tighter accuracy than just using the schema as a reference for Prong 2.
- **Per-rubric weighting in `Σ |diff|`.** Naive sum weights FOCAL's 58-row state error same as Sunlight's 13-row state error. Open whether to accept implicit weighting, normalize per-rubric (`|diff|/max_score`), or per-rubric-then-mean. Cheap to change later; deferred.
- **`docs/active/ARCHITECTURE.md` misnaming.** Doc is Prong-3-scoped (Postgres / FastAPI / GraphQL / MCP) but the name suggests overall architecture. Flagged for future cleanup; not this session's scope.
- **The brief-writer/scorer-v2 implementation plan** is still outstanding per the prior session's handoff at [`plans/_handoffs/20260514_brief_writer_impl_plan_write_handoff.md`](../plans/_handoffs/20260514_brief_writer_impl_plan_write_handoff.md). That's the natural next-work-session.

## Process notes

- **Agent flagged uncertainty mid-session on "Ralph loop" terminology** rather than nodding through. User confirmed close-enough on reading.
- **Three reframes were user-initiated corrections to agent framing**, not agent-generated insights. The agent's initial mental model of Phase C, prong relationships, and rubric-order rigidity were all flat-er and more rigid than reality.
- **Walked the doc system link graph before pushing** per the user's persistent-memory feedback: doc references existing files (README, STATUS, ARCHITECTURE, LANDSCAPE, compendium README, projection mappings in historical) which all live on main; cherry-pick lands the doc consistent with its referents. Multi-committer rule satisfied (pull-before-push on both branches; no STATUS.md row conflicts).
- **Agent walked back an earlier overclaim** mid-conversation: "harness feature-complete for a single-state pilot after scoring_v2 ships" was extraction-complete, not quality-validated. Surfaced and corrected.
