# Research Log: scoring

Created: 2026-04-14
Purpose: Build a unified PRI + FOCAL scoring pipeline that evaluates all three locked rubrics (PRI accessibility, PRI disclosure-law, FOCAL 2026) against the frozen 2026-04-13 portal-snapshot corpus for all 50 states, producing provenance-stamped CSVs with a 3× temperature-0 self-consistency check.

## Trajectory

Newest first.

- **2026-04-17 — Data inventory (desktop).** Checked out scoring branch on desktop machine; discovered `data/` (snapshots + CA scores) only exists on laptop. Decision: continue scoring work on laptop where data lives. No code changes. Cross-machine data sync deferred. Detail: `convos/20260417_scoring_data_inventory.md`.
- **2026-04-14 — Phase 2 CA dry-run successful.** Pipeline end-to-end validated against real CA snapshot. 174 rows produced (PRI accessibility 59, PRI disclosure-law 61, FOCAL 54), all pydantic-validated on first attempt, all provenance-stamped. unable_to_evaluate rate: 80% PRI accessibility (Imperva blocks cal-access search UI — the rubric signal), 31% PRI disclosure-law, 2% FOCAL. Subagents honestly flagged WAF stubs rather than guessing. Detail: `results/20260414_ca_dry_run.md`.
- **2026-04-14 — Phase 1 pipeline build.** `src/scoring/` Python package (uv + pydantic, no anthropic SDK), locked scorer prompt at v1, snapshot/rubric loaders, output writer with provenance stamping, two-stage `prepare`/`finalize` orchestrator CLI. 9 pipeline tests pass against real rubric CSVs and CA snapshot manifest. Architecture: subagent-only (Agent tool) — confirmed by user; resolves the handoff plan's `anthropic + pydantic` vs. "Agent tool not SDK" contradiction in favor of the latter.

## Plans

- (inherited, for reference — both live on their source branches)
  - `docs/active/focal-extraction/plans/20260414_scoring_branch_handoff.md` — 5-phase plan this branch executes
  - `docs/active/pri-2026-rescore/plans/20260414_pri_focal_unified_scoring_handoff.md` — unified-pipeline architecture rationale

## Convos

- 2026-04-17 — `convos/20260417_scoring_data_inventory.md` — Brief desktop session. Data inventory: snapshots + CA scores live on laptop only. Decision to continue there.
- 2026-04-14 — `convos/20260414_scoring_pipeline_phase1_build.md` — Phase 1 pipeline build + Phase 2 CA dry-run. Architecture confirmed: subagent-only (Agent tool), no anthropic SDK. Deps: uv + pydantic.

## Results

- 2026-04-14 — `results/20260414_ca_dry_run.md` — Phase 2 CA dry-run report (run_id `bc11ca624efc`). Pipeline validated; raw JSONs + stamped CSVs + run_metadata under `data/scores/CA/2026-04-13/bc11ca624efc/`.
