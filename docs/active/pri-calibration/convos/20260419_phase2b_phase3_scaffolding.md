# 2026-04-19 — Phase 2b calibration harness + Phase 3 scaffolding

**Date:** 2026-04-19
**Branch:** pri-calibration

## Summary

Closed out Phase 2b (calibration harness) and Phase 3 task 2 (statute-run
orchestration), then surfaced and fixed two additional Phase 3 TDD gaps.
Branch is now fully scaffolded end-to-end for a baseline scoring run:
retrieve → prepare → dispatch → finalize → consistency → agreement report.

Key artifact: a PRI sub-aggregate rollup rule derived line-by-line from the
2010 paper and codified as the single authoritative spec for **both** this
calibration branch and `pri-2026-rescore`'s eventual 50-state reporting.
Phase 2b surfaced that the plan's "group by sub_component and sum" edge
case was wrong — PRI's published B/C/D/E sub-aggregates use non-trivial
rules (B1/B2 reverse, C/D gate-only, E higher-of-principal-or-lobbyist
with F/G summed and J independent and h-frequency collapsed). Spec doc
pins these down with line citations.

No live LLM dispatch this session — everything done with TDD against
fixtures. Final regression: 130/130 tests green, ruff clean.

## Topics Explored

- PRI 2010 paper §III.B-E + §IV.7-8 for the sub-aggregate rollup rules.
- The 2026 rubric's `source` column (`pri_2010_kept` vs `new_2026`) as
  the mechanism for excluding Q9-Q16 from calibration agreement.
- Q8_normalized rounding (PRI publishes 1-dp; we compute float) and how
  to tolerate it in agreement checks.
- Statute-run path convention (`data/scores/<STATE>/statute/<vintage>/<run_id>/`)
  vs portal-run (`data/scores/<STATE>/<snapshot_date>/<run_id>/`) and how
  to keep the two cleanly separated in the orchestrator.
- Whether to build an adjudicator now for the 3 temp-0 runs (decision:
  no — report per-run + cross-run variance instead, defer adjudicator
  to Phase 4+).
- OpenStates scrapers repo (https://github.com/openstates/openstates-scrapers)
  flagged as potentially relevant — investigation deferred to next session.

## Provisional Findings

- PRI's E aggregation math reconciles cleanly to the 0-20 column cap when
  read as: `max(base_E1, base_E2) + fg_E1 + fg_E2 + E1j` with
  `base = a+b+c+d+e+h_collapsed+i` and `h_collapsed = (h_i or h_ii or h_iii)`.
- No per-state atomic-level PRI ground truth exists anywhere — only the
  paper's 50-state sub-aggregate tables. Calibration agreement can
  therefore only be measured at sub-aggregate granularity, not item-level.
- The existing `analyze-consistency` subcommand hardcodes the portal path
  convention, so statute-based self-consistency needed its own path helper
  (`statute_csv_path`) + subcommand (`calibrate-analyze-consistency`).

## Decisions Made

- **Rollup rule:** 9 methodology differences from PRI 2010 explicitly
  documented in `results/20260419_pri_rollup_rule_spec.md` so any
  calibration disagreement can be attributed to the right source (coder
  type, sharpened guidance, Q8 holistic scoring, null handling, etc.).
- **Data model for statute runs:** separate `StatuteRunMetadata` pydantic
  class rather than overloading `RunMetadata` with optional fields.
  Downstream analysis can filter cleanly by type.
- **ScoredRow schema:** `snapshot_manifest_sha` column re-used as the
  corpus sha regardless of corpus type (YAGNI — no rename / migration).
- **Coverage tier for statute runs:** hard-coded to `"clean"` (no WAF/SPA
  semantics apply to Justia-retrieved text).
- **Calibration rubric set:** `pri_accessibility` + `pri_disclosure_law`
  only. `focal_indicators` skipped since no 2010 FOCAL reference exists.
- **Adjudication:** deferred. Phase 2b's `calibrate` subcommand accepts
  multiple `--run-id` values and renders per-run + cross-run variance;
  proper majority-vote/LLM-adjudicate logic waits for Phase 4.

## Results

- [`results/20260419_pri_rollup_rule_spec.md`](../results/20260419_pri_rollup_rule_spec.md)
  — line-cited rollup rule for PRI 2010 disclosure law + accessibility;
  9 methodology differences between our calibration setup and PRI's
  original protocol.

## Code delivered

- `src/scoring/calibration.py` — `rollup_disclosure_law`, `rollup_accessibility`,
  `load_pri_reference_scores`, `compute_agreement`, `load_atomic_scores_from_csv`,
  `render_agreement_markdown`, `render_multi_run_agreement_markdown`.
- `src/scoring/models.py` — new `StatuteRunMetadata` pydantic model.
- `src/scoring/consistency.py` — refactored `compute_consistency` to take a
  `csv_paths_by_run_id` dict; added `statute_csv_path` helper.
- `src/scoring/orchestrator.py` — four new subcommands:
  - `calibrate-prepare-run`
  - `calibrate-finalize-run`
  - `calibrate-analyze-consistency`
  - `calibrate` (multi-run aware)
- Tests: `test_calibration.py` (36), `test_orchestrator_calibrate.py` (7),
  `test_orchestrator_calibrate_run.py` (9),
  `test_orchestrator_calibrate_consistency.py` (3). All green.

## Commits pushed

- `f435984` — Phase 2b-0 PRI rollup rule spec
- `c928336` — Phase 2b rollup + reference loader + agreement metrics
- `fc101b4` — Phase 2b calibrate subcommand
- `51bc4e7` — Phase 3.2 calibrate-prepare-run + calibrate-finalize-run
- `28ebba7` — Phase 3.3 statute-aware consistency + multi-run calibrate

## Open Questions

- **Live Phase 3 dispatch not yet attempted.** The plan's 30 subagent
  calls (5 states × 2 rubrics × 3 temp-0 runs) against statute bundles
  is exploratory (not TDD). Next session should run this end-to-end.
- **How noisy will self-consistency be on statute text vs portal
  snapshots?** Hypothesis per prior-session plan: lower, because statute
  text is more definitive than portal summaries. Needs empirical check.
- **Is OpenStates scrapers useful to this project?** User flagged the
  repo at session end; investigation deferred.
- **Q8 interpretation:** paper says 0-15 raw, no atomic decomposition.
  Our LLM is asked to judge holistically. Expected source of divergence
  from PRI — watch this column in the baseline report.

## Next Steps

- Investigate openstates-scrapers repo: what does it provide, how does
  it relate to our OpenStates dependency path, does it change our build
  vs. depend decision from the `research-prior-art` scoping work.
- After that: execute Phase 3 baseline scoring run. Prepare briefs for
  all 5 calibration states × 3 runs each, dispatch subagents, finalize,
  analyze consistency, run calibrate, write the baseline report.
- Pause-point per plan: discuss convergence target with Dan before Phase 4.
