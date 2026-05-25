# 20260518 — Tier-0 plan review, scoring_v2 impl plan write, EvidenceSpan resolution

> **FORWARD-POINTER 2026-05-19:** Two of this session's outputs were superseded one session later: (a) the Tier-0 plan revisions (hop=2, prompt-sha) became moot when the plan was tabled entirely after 4 preconditions failed at execution time; (b) the 0979779 EvidenceSpan migration was found to have introduced a structural circular import — `EvidenceSpan` ended up in the wrong module (`retrieval_v2.models`); fix is to relocate to `models_v2/citations.py`. The scoring_v2 impl plan (commit `067dfac`) survives as the escape-hatch path if direct-read fails empirically. See [`20260518_tier_0_execution_pivot_to_direct_read.md`](20260518_tier_0_execution_pivot_to_direct_read.md) for the pivot reasoning and [`plans/20260518_tier_0_direct_read_smoke_test.md`](../plans/20260518_tier_0_direct_read_smoke_test.md) for the replacement plan.

**Date:** 2026-05-18
**Branch:** extraction-harness-brainstorm
**Predecessor:** [`20260518_synopsis_walkthrough_and_tier_0_scoping.md`](20260518_synopsis_walkthrough_and_tier_0_scoping.md) (same-day; this session reviewed its plan output)

## Summary

Session opened with user asking for a critical review of [`plans/20260518_tier_0_minimal_pipeline.md`](../plans/20260518_tier_0_minimal_pipeline.md) — the Tier-0 smoke-test plan produced by the predecessor session. Review surfaced **one blocker** (the plan's "4 v2 modules to wire together" claim was a dependency-graph error — the WIP component is the scorer brief-writer in a hypothetical `scoring_v2/` module that doesn't exist on this branch, not `retrieval_v2/brief_writer.py` which shipped 2026-05-14) plus a handful of substantive issues (testing-anti-pattern test design in Step 2, narrow success criterion #3, Step 6 implicit-refactor coupling, unsourced cost budget). User confirmed: the scoring_v2 impl plan was indeed never written (only the plan-sketch and an exhaustive handoff exist) — green-lit writing it now.

Dispatched a `general-purpose` subagent to execute the existing handoff and produce the impl plan. Subagent shipped a 1400-line TDD-shaped plan (commit `067dfac`) mirroring the retrieval impl plan structure: 6 test files / 51 named test signatures, full v2 scorer prompt inlined (7 cell-anchored rules, zero PRI key leakage), full tool schemas inlined. Verified independently: the subagent's audit claim (`grep -rn "provenance=" tests/ src/` returns 1 line) matched my own run; commit + structure check clean.

User then asked to "make sure the EvidenceSpan issue is solved" — to which the answer was: the decision is documented (use `retrieval_v2.EvidenceSpan`, retire `models_v2.EvidenceSpan`) but not applied to code, and both queued plans (Tier-0 Step 2, scoring_v2 Phase 7) had deferred the deletion citing "non-trivial import audit." A real audit showed the surface was 6 files / 5 edit sites / 130 line-diff — tractable in one commit. User authorized the full deletion. Shipped as commit `0979779`; 480 tests pass / 8 skip / 3 pre-existing baseline `test_pipeline.py` failures unchanged. Two follow-up doc commits collapsed Tier-0 Step 2 and scoring_v2 Phase 7 to verify-already-done.

Also applied two pre-confirmed Tier-0 fixes from the review: hop=2 locked in Step 3 (was an open question with implementer-choice ambiguity); prompt-sha capture added to Step 5 + writeup (for σ_noise bisects in Tier 1).

## Topics Explored

- **Tier-0 plan review — dependency-graph error.** Read the plan + originating convo + RESEARCH_LOG end-to-end. Cross-checked `ls src/lobby_analysis/` (no `scoring_v2/`), `ls retrieval_v2/` (brief_writer.py shipped), `ls plans/` (only `20260514_brief_writer_plan_sketch.md`, no impl plan). The plan's framing — "wire up 4 v2 modules including the WIP brief-writer in `retrieval_v2/brief_writer.py`" — conflated the retrieval brief-writer (shipped, calls `record_cross_reference`) with the scorer brief-writer (not built, would call `record_cell`). Steps 4–5 of Tier-0 require the scorer brief-writer to exist; without scoring_v2, the plan can't run.

- **Other substantive Tier-0 issues flagged** (not all addressed this session; see Open Questions): Step 2's failing test was testing-anti-pattern by the plan's own definition (tests Pydantic acceptance of a tuple type — i.e., testing the library); success criterion #3 (`cells == 2`) forecloses legitimate `record_unscoreable_cell` outcomes — should be `cells + unscoreable_cells == 2`; Step 6 implies a refactor (extract "wiring helpers" for unit tests) that Steps 3–5 don't name; cost budget of $1–2/run is unsourced and 20–40× the retrieval T1 baseline of ~$0.06.

- **Subagent dispatch for scoring_v2 impl plan.** Used the existing `_handoffs/20260514_brief_writer_impl_plan_write_handoff.md` — exhaustive enough that the subagent didn't need to re-litigate decisions. Pattern matches prior subagent dispatches on this branch (post-framing reviews, compendium audit). Subagent ran 8m52s, 199K tokens, 37 tool calls. Output: 1400-line plan with the full v2 prompt drafted and inlined; 51 test signatures named; phase ordering bakes in the retrieval-lesson (prompt md before brief_writer because brief_writer reads prompt at call time).

- **Subagent's plan-write decisions** (handoff §"What you DO decide"): `row_id` as plain string with parser-side `build_cell_spec_registry()` validation (NOT a 186-entry enum); `ScoringOutput.chunk_id: str` (per-call single chunk, multi-chunk is advanced usage); parser logs warning + skips on unknown `(row_id, axis)` rather than raising (mirrors retrieval's unknown-tool-name handling); added `_instantiate_with_special_shapes` helper for `TimeThresholdCell` / `CountWithFTECell` / etc. whose tool `value` is a dict, not a scalar.

- **EvidenceSpan audit (the real one).** Subagent's `provenance=` audit was 1 line (test_models_v2_cells.py:69) — but `EvidenceSpan` import surface is broader. Full audit: 1 production-side consumer (`cells.py` lines 23, 40) + 1 export site (`__init__.py` lines 31, 43) + 1 module file (`provenance.py`) + 3 test files (`test_models_v2_provenance.py` entirely, `test_models_v2_init.py` 2 lines, `test_models_v2_cells.py` 2 lines). Tractable as a single commit; the Tier-0 and scoring_v2 plans' "non-trivial; defer deletion" assertions were overcautious.

- **Tier-0 fixes confirmed pre-deletion.** Hop=2 lock in Step 3 (was an "implementer's call" open question; lock matches Tier 1, cost delta is small); prompt-sha capture added to Step 5 (sha256 of scorer prompt content, persisted in results JSON) + writeup (for Tier-1 σ_noise bisects). Question section cleaned up: Q1 (hop) and Q4 (Step 2 ordering, always moot) removed.

## Provisional Findings

- **The Tier-0 plan's `scoring_v2` blind spot was not a misjudgment — it was a referential slip.** The opening paragraph said "the WIP brief-writer in `retrieval_v2/brief_writer.py`" — that path exists and shipped, but the WIP component lives at `scoring_v2/brief_writer.py` which doesn't exist. A naming-slip cascaded into Steps 4–5 implicitly assuming the scoring brief-writer was the retrieval one. Took an outside-the-plan check (`ls src/lobby_analysis/`) to surface.

- **The scoring_v2 brainstorm-handoff pattern proved durable.** Handoff was written 2026-05-14, sat unexecuted for 4 days while the post-framing reviews / synopsis / Tier-0 scoping work intervened. The subagent picked it up cold and shipped a clean plan with no AskUserQuestion escalations. Mirror-retrieval-impl-plan-shape directive in the handoff made the structural lift cheap.

- **"Deferred deletion" was a misjudgment.** Two plans (Tier-0 Step 2, scoring_v2 Phase 7) both said `models_v2.EvidenceSpan` deletion required a "full import-graph audit" and deferred to a follow-on plan that may never have been scheduled. The actual audit took one grep; the deletion took one commit. Pattern worth surfacing: estimates of "non-trivial" should be quantified before being committed to a plan — even a fast grep would have changed the framing.

- **scoring_v2 impl plan ships symmetric with retrieval_v2** in nearly every architectural decision (Q1, Q2, Q3, Q7-sub, Q8, Q9, Q10 all mirror per the brainstorm). The intentional symmetry pays off — review surface is smaller, the implementer's mental model is one module not two, the structural template makes the second module much faster to plan than the first.

## Decisions Made

- **Wrote scoring_v2 impl plan.** Subagent dispatch, committed as `067dfac` (1400 lines, 51 test signatures, full v2 prompt + tool schemas inlined). Ready for an implementation session (separate API-launched sub-branch per the precedent).

- **Locked Tier-0 hop count at `hop=2`.** Step 3 updated; Q1 removed from Questions section. Matches Tier 1; cost delta vs hop=1 is small.

- **Added prompt-sha tracking to Tier-0.** Step 5 captures `prompt_sha = hashlib.sha256(scorer_prompt_v2_text.encode()).hexdigest()` and persists it in the results JSON; Step 7 writeup includes it. Anchors the smoke-test run for future bisects when prompt content changes.

- **Resolved EvidenceSpan duplication via full deletion** (not deferred). Commit `0979779` deleted `src/lobby_analysis/models_v2/provenance.py` + `tests/test_models_v2_provenance.py`; migrated `CompendiumCell.provenance: EvidenceSpan | None = None` → `tuple[retrieval_v2.EvidenceSpan, ...] = ()`; updated `__init__.py` exports + 2 test files. 480/8/3 (was 484/8/3 — the 4 deleted tests targeted dead code). Closes Fork 1 from the 2026-05-16 review synopsis; the Citations-API span is the single provenance shape.

- **Collapsed Tier-0 plan Step 2 to verify-already-done.** Cross-references commit `0979779`. If verification fails (branch state surprise), implementer surfaces rather than re-executing.

- **Collapsed scoring_v2 impl plan Phase 7 to verify-already-done** (commit `2d8e395`). Same cross-reference pattern. Original "coordinate with Tier-0 Step 2 via STATUS.md" instruction is now moot.

- **Did NOT apply the deeper Tier-0 fixes** (Step 2 testing-anti-pattern, success criterion #3 broadening, Step 6 refactor wording, cost-budget rebaseline, hand-eyeball failure-path). Held per user — likely worth deeper Tier-0 rewrite after scoring_v2 ships and the actual API surface is visible.

## Results

(No analysis outputs this session. The deliverables are the doc/plan commits and the EvidenceSpan deletion commit, all linked above.)

## Open Questions

- The 4 unaddressed Tier-0 issues (Step 2 testing-anti-pattern, success criterion #3, Step 6 refactor, cost-budget rebaseline / hand-eyeball failure path). Best timing for fixes: after scoring_v2 ships and Tier-0 surfaces real cell shapes — the fixes will be more concrete with the actual API in hand.

- **Should the implementation session for scoring_v2 run now or after a separate brainstorm pass?** The plan is ready; the implementer-agent precedent (retrieval_v2) ran clean under strict TDD via API-launched sub-branch. Likely "run now," but not asked this session.

- **Practical-axis brief-writer brainstorm** remains the next-after-scoring_v2 sibling component (per Q6 deferral). Not in scope here.

## Cross-session continuity note

The predecessor session ([`20260518_synopsis_walkthrough_and_tier_0_scoping.md`](20260518_synopsis_walkthrough_and_tier_0_scoping.md)) and its plan output ([`plans/20260518_tier_0_minimal_pipeline.md`](../plans/20260518_tier_0_minimal_pipeline.md)) were sitting untracked when this session started — finish-convo from that session didn't run. This session's finish-convo commits both (along with this convo and the Tier-0 plan edits applied on top). Future agents reading the link graph should treat the predecessor convo as the original framing context for Tier-0; this convo is the review + execution-prep layer on top.
