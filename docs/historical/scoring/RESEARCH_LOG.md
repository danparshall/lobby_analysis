# Research Log: scoring

Created: 2026-04-14
Purpose: Build a unified PRI + FOCAL scoring pipeline that evaluates all three locked rubrics (PRI accessibility, PRI disclosure-law, FOCAL 2026) against the frozen 2026-04-13 portal-snapshot corpus for all 50 states, producing provenance-stamped CSVs with a 3× temperature-0 self-consistency check.

## Trajectory

Newest first.

- **2026-04-17 (pm) — Pilot executed; methodology pivot to PRI 2010 calibration.** Ran the full Phase 3 pilot (CA / CO / WY × 3 temp-0 runs × 3 rubrics = 27 scored cells + 2026-04-14 CA dry-run as CA's 3rd run). Disagreement flags: PRI disclosure-law **flagged on all 3 states** (CA 37.7%, CO 11.5%, WY 11.5%); CO focal_indicators flagged at 13.0%; PRI accessibility stable on CO + WY (3.4%–8.5%), flagged on CA (11.9%) via WAF-stub variance. Root cause of disclosure-law disagreement: snapshot is same-host-only, so we're measuring *portal summaries* of the law, not the law itself — subagents disagree on whether portal silence means `unable_to_evaluate` or `score=0`. **Pivoted** to a calibration plan: use PRI 2010 human-rater scores + 2010 statutes as ground truth, iterate prompt, apply to 2026 statutes. Phase 4 (50-state scale-up) **paused** until calibration converges. Also extended `scoring.orchestrator` with reusable subcommands (`prepare-run`, `finalize-run`, `analyze-consistency`) and added `src/scoring/consistency.py`. Detail: `convos/20260417_pilot_and_calibration_pivot.md`.
- **2026-04-17 (am) — Data inventory (desktop).** Checked out scoring branch on desktop machine; discovered `data/` (snapshots + CA scores) only exists on laptop. Decision: continue scoring work on laptop where data lives. No code changes. Cross-machine data sync deferred. Detail: `convos/20260417_scoring_data_inventory.md`.
- **2026-04-14 — Phase 2 CA dry-run successful.** Pipeline end-to-end validated against real CA snapshot. 174 rows produced (PRI accessibility 59, PRI disclosure-law 61, FOCAL 54), all pydantic-validated on first attempt, all provenance-stamped. unable_to_evaluate rate: 80% PRI accessibility (Imperva blocks cal-access search UI — the rubric signal), 31% PRI disclosure-law, 2% FOCAL. Subagents honestly flagged WAF stubs rather than guessing. Detail: `results/20260414_ca_dry_run.md`.
- **2026-04-14 — Phase 1 pipeline build.** `src/scoring/` Python package (uv + pydantic, no anthropic SDK), locked scorer prompt at v1, snapshot/rubric loaders, output writer with provenance stamping, two-stage `prepare`/`finalize` orchestrator CLI. 9 pipeline tests pass against real rubric CSVs and CA snapshot manifest. Architecture: subagent-only (Agent tool) — confirmed by user; resolves the handoff plan's `anthropic + pydantic` vs. "Agent tool not SDK" contradiction in favor of the latter.

## Plans

- `plans/20260417_pri_ground_truth_calibration.md` — **next action.** Calibrate the scoring pipeline against PRI 2010 human-rater scores and 2010-era statutes; apply the calibrated prompt to 2026 statutes. Intended to be executed by a fresh agent on a new branch. Originating convo: `convos/20260417_pilot_and_calibration_pivot.md`.
- (inherited, for reference — both live on their source branches)
  - `docs/active/focal-extraction/plans/20260414_scoring_branch_handoff.md` — 5-phase plan this branch executes
  - `docs/active/pri-2026-rescore/plans/20260414_pri_focal_unified_scoring_handoff.md` — unified-pipeline architecture rationale

## Convos

- 2026-04-17 (pm) — `convos/20260417_pilot_and_calibration_pivot.md` — Phase 3 pilot executed; PRI disclosure-law flagged on all 3 pilot states. Root cause is methodology: snapshots capture portal summaries of the law, not the law. Pivoted to PRI 2010 ground-truth calibration approach.
- 2026-04-17 (am) — `convos/20260417_scoring_data_inventory.md` — Brief desktop session. Data inventory: snapshots + CA scores live on laptop only. Decision to continue there.
- 2026-04-14 — `convos/20260414_scoring_pipeline_phase1_build.md` — Phase 1 pipeline build + Phase 2 CA dry-run. Architecture confirmed: subagent-only (Agent tool), no anthropic SDK. Deps: uv + pydantic.

## Results

- 2026-04-17 — `results/20260417_ca_consistency.md` — CA triad inter-run disagreement: pri_accessibility 11.86% FLAGGED, pri_disclosure_law 37.70% FLAGGED, focal_indicators 9.26% ok. Runs: `bc11ca624efc`, `1934fb5034f6`, `ca8b98a32d46`.
- 2026-04-17 — `results/20260417_co_consistency.md` — CO triad: pri_accessibility 8.47% ok, pri_disclosure_law 11.48% FLAGGED, focal_indicators 12.96% FLAGGED. Runs: `061ea915571e`, `c97b3fa3744d`, `d9c3defc9a37`.
- 2026-04-17 — `results/20260417_wy_consistency.md` — WY triad: pri_accessibility 3.39% ok, pri_disclosure_law 11.48% FLAGGED, focal_indicators 3.70% ok. Runs: `6f58ff450be0`, `078ef7b10127`, `1ddd60f9f5c4`.
- 2026-04-14 — `results/20260414_ca_dry_run.md` — Phase 2 CA dry-run report (run_id `bc11ca624efc`). Pipeline validated; raw JSONs + stamped CSVs + run_metadata under `data/scores/CA/2026-04-13/bc11ca624efc/`.
