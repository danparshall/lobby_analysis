# 2026-04-14 — Scoring pipeline Phase 1 build

**Branch:** `scoring` (cut from main at `15fa471` post focal-extraction merge)
**Upstream plan:** `docs/active/focal-extraction/plans/20260414_scoring_branch_handoff.md`
**Unified-architecture doc:** `docs/active/pri-2026-rescore/plans/20260414_pri_focal_unified_scoring_handoff.md`

## Context at session start

All three rubrics locked (PRI accessibility 59 items, PRI disclosure-law 61 items, FOCAL 2026 54 items). Portal snapshots frozen 2026-04-13 for all 50 states (981 artifacts, ~350 MB, per-state manifest.json with sha256 + challenge-stub flags). Unified pipeline architecture decided: one scoring pass per state, three rubrics against shared snapshot corpus, provenance-stamped rows, 3× temp-0 self-consistency, Agent-tool subagents (not SDK).

## Architecture decision (2026-04-14)

**Subagent-only (Option A), confirmed by user.** The handoff plan had an internal contradiction — step 2 listed `anthropic + pydantic` as deps, step 7 said "Agent tool, not SDK." Resolved in favor of step 7 + auto-memory preference (`feedback_prefer_subagents_over_sdk.md`).

Consequence:
- Python (`src/scoring/`) is a utility library only — no LLM calls.
- Python responsibilities: load snapshots, load rubrics, assemble per-(state, rubric) prompt bundles, validate returned CSV against pydantic schema, stamp provenance columns at orchestrator layer.
- The LLM call is a Claude Code Agent-tool subagent, one per (state, rubric) invocation. For a full 50-state, 3-run, 3-rubric sweep that's 50 × 3 × 3 = 450 subagent invocations; orchestrator checkpoints per-state for resumability.
- Deps: `uv` env + `pydantic` only. No `anthropic`.

Downside acknowledged: subagent output isn't schema-enforced by tool-use. Mitigation: strict pydantic validation + retry-on-schema-break protocol.

## Work plan this session

1. Seed `docs/active/scoring/` — done.
2. Init `src/scoring/` uv package (pyproject.toml, .python-version=3.12, `uv sync`).
3. Write locked scorer prompt (`src/scoring/scorer_prompt.md`).
4. Snapshot loader.
5. Rubric loader.
6. Scored-row pydantic model + CSV writer with provenance stamping.
7. Per-state orchestrator (subagent dispatch + checkpointing).
8. Phase 2: CA dry-run (1×, temp 0) across all three rubrics. Validate + commit.

Stop at end of Phase 2 for user review before pilot.

## Outcome

- Phase 1 done. 9 tests pass. Committed.
- Phase 2 done. CA run_id `bc11ca624efc`. 174 rows scored, all schema-valid, all provenance-stamped. Detail: `results/20260414_ca_dry_run.md`.
- Mid-session correction: hatchling needed `[tool.hatch.build.targets.wheel.sources]` mapping for the `src/scoring → scoring` rename. Pydantic Literal on `data_type` was too strict (rubrics carry author-defined enums like `ordinal_0_to_15`, `numeric_percent_or_null`); relaxed to `str`.
- User pushed back on dispatching all three subagents simultaneously ("all *THREE* rubrics?"); after clarification that PRI is two rubrics + FOCAL = three (per the locked rubric set), proceeded.

## Open for user review before Phase 3

1. Sanity-check the 12 scored PRI accessibility items + 42 scored disclosure-law items against your read of the snapshot.
2. Decide: proceed to Phase 3 (CA/CO/WY × 3 runs each) on the same pipeline, or sharpen any rubric items first?
3. AZ/VT (inaccessible tier): score now from statute-only with high null rate, or defer until Playwright supplements?

## Open questions to revisit during build

- Coverage-tier column: plan step recommends adding `coverage_tier` to output CSV. Implementing as a join against a state→tier mapping derived from snapshot-sufficiency audit.
- AZ/VT: score from statute text only; annotate `coverage_tier=inaccessible`; Playwright re-run overwrites later.
