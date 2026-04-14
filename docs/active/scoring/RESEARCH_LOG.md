# Research Log: scoring

Created: 2026-04-14
Purpose: Build a unified PRI + FOCAL scoring pipeline that evaluates all three locked rubrics (PRI accessibility, PRI disclosure-law, FOCAL 2026) against the frozen 2026-04-13 portal-snapshot corpus for all 50 states, producing provenance-stamped CSVs with a 3× temperature-0 self-consistency check.

## Trajectory

Newest first.

## Plans

- (inherited, for reference — both live on their source branches)
  - `docs/active/focal-extraction/plans/20260414_scoring_branch_handoff.md` — 5-phase plan this branch executes
  - `docs/active/pri-2026-rescore/plans/20260414_pri_focal_unified_scoring_handoff.md` — unified-pipeline architecture rationale

## Convos

- 2026-04-14 — `convos/20260414_scoring_pipeline_phase1_build.md` — Phase 1 pipeline build + Phase 2 CA dry-run. Architecture confirmed: subagent-only (Agent tool), no anthropic SDK. Deps: uv + pydantic.

## Results

(empty)
