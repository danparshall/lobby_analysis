# Newmark 2017 + Newmark 2005 modules shipped

**Date:** 2026-05-18
**Branch:** phase-c-projection-tdd
**Predecessor convo:** [`20260518_scope_correction.md`](20260518_scope_correction.md)
**Spec docs (Phase B mappings):**
- [`newmark_2017_projection_mapping.md`](../../../historical/compendium-source-extracts/results/projections/newmark_2017_projection_mapping.md)
- [`newmark_2005_projection_mapping.md`](../../../historical/compendium-source-extracts/results/projections/newmark_2005_projection_mapping.md)
- Plans mined for rename tables only (process framing ignored per scope-correction): [`plans/20260518_newmark_2017_plan.md`](../plans/20260518_newmark_2017_plan.md), [`plans/20260518_newmark_2005_plan.md`](../plans/20260518_newmark_2005_plan.md).

## Summary

Implemented `src/lobby_analysis/projections/newmark_2017.py` and `newmark_2005.py` — deterministic Python that maps populated SMR cells to per-item 0/1 scores plus reproducible sub-aggregates (where the published rubric structure supports them). Both modules use the `sunlight_2015.py` shape: a `LEGAL_AXIS` constant, `IN_SCOPE_ITEMS` / `EXCLUDED_ITEMS` / `UNABLE_TO_EVALUATE` module-level constants, a frozen Pydantic score model, per-item helpers + a dispatcher, and a top-level `project_newmark_<year>` function. Zero LLM imports across both modules. 14 in-scope items each.

Newmark 2005 imports `project_gifts_actor_agnostic_or` from `newmark_2017` (the gifts/entertainment OR helper is the same observable in both rubrics). Newmark 2005 introduces one new helper, `project_cadence_more_than_annual_or`, for its frequency item — 8-cell OR over `{lobbyist, principal} × {monthly, quarterly, triannual, semiannual}` cadence cells, deliberately not reading the `_annual` or `_other` cadence cells (regression-guarded).

82 new tests (45 Newmark 2017 + 37 Newmark 2005), all passing. Full projections suite: 676 passed in 0.97s.

## Topics Explored

- Cell-mapping content from the Newmark 2017 / 2005 mapping docs (14 items each)
- 15 spec-doc → v2 row-name renames (7 inherited from Newmark 2017 + 8 cadence renames for the 2005 freq item)
- The 2017 → 2005 structural delta:
  - Newmark 2017 has 7 disclosure items; Newmark 2005 has 6 (no `contributions_from_others` parallel)
  - Newmark 2005 adds 1 frequency item (`freq_reporting_more_than_annual`) that 2017 dropped
- How sub-aggregate exposure should differ between modules:
  - Newmark 2017 → exposes `def_section_total` + `disclosure_section_total` (Table 2 publishes these per state)
  - Newmark 2005 → exposes ONLY `per_item_scores` (Table 1 publishes only per-state totals; exposing sub-aggregates would claim reproducibility against unpublished data)

## Decisions Made

- **Architecture: declarative spec table + dedicated helpers for multi-row reads.** Mirrors `pri_2010.py` for the 11 (Newmark 2017) / 11 (Newmark 2005) single-row items. Dedicated helpers for gifts OR (shared across both modules) and cadence OR (new in 2005).
- **Sub-aggregate exposure asymmetry.** Newmark 2017's `Newmark2017Score` carries `def_section_total` and `disclosure_section_total` (each 0–7, with `None` if any item in the battery is `unable_to_evaluate`). Newmark 2005's `Newmark2005Score` carries only `per_item_scores` + `panel` label — no sub-aggregates exposed. Rationale: the paper publishes them in one case but not the other; an API for the unpublished case smuggles claims-of-reproducibility we don't have.
- **No `index.total` in either module.** Both rubrics' headline totals require excluded items (5 `prohib.*` for 2017; 4 `prohib_*` + 1 `penalty_stringency_2003` for 2005). Regression-guarded absent at the module level (`not hasattr(...)`) and at the score-model level (`"index_total" not in fields`).
- **`unable_to_evaluate` semantics:** binary items return the sentinel when row is missing OR axis value is None; typed-cell `IS NOT NULL` items return sentinel only when the row is absent from the cells dict (axis None projects to 0 — "no threshold defined in law"). Matches `sunlight_2015.py` precedent.
- **No-variation cells read honestly.** `def_target_legislative_branch` (uniformly TRUE across 50 states in 2015) and the gifts OR (uniformly TRUE in 2015) are projected per the cell value, not coerced to TRUE. The empirical uniformity is a property of the world, not a property of the projection. Regression-guarded.
- **Falsified-2017-speculation regression-guarded.** Newmark 2005 has NO `contributions_from_others` item; the corresponding cell is not read; the regression test passes the cell-with-True and confirms it doesn't affect Newmark 2005's output.

## Results

Code:
- `src/lobby_analysis/projections/newmark_2017.py` (305 lines)
- `src/lobby_analysis/projections/newmark_2005.py` (282 lines)

Tests (4 files, 82 tests):
- `tests/projections/test_newmark_2017_per_item.py` (29 tests covering 14 in-scope items)
- `tests/projections/test_newmark_2017_aggregation.py` (16 tests; end-to-end + regression guards)
- `tests/projections/test_newmark_2005_per_item.py` (21 tests; spot-checks + full cadence-helper coverage)
- `tests/projections/test_newmark_2005_aggregation.py` (16 tests; end-to-end + regression guards + falsified-2017 guard)

All 676 projection tests pass (594 pre-existing + 45 Newmark 2017 + 37 Newmark 2005). Ruff clean on all new files.

## Open Questions / Deferred

1. **Per-state ground-truth CSVs not in repo.** Newmark 2017 publishes Table 2 (50 states × 4 sub-aggregate columns); Newmark 2005 publishes Table 1 (50 states × 6 panels). Neither has been extracted to a CSV. The 50-state validation harness is deferred. Per-item helper tests + aggregation fixtures cover the projection logic without it.
2. **3 pre-existing pipeline-test failures (unrelated).** `tests/test_pipeline.py` has 3 failures pointing at missing `data/portal_snapshots/CA/2026-04-13/manifest.json`. Verified pre-existing on this branch (failures reproduce with my new files stashed). The local data only has `2026-05-01`; this is the cross-machine data-sync lag, not a code bug. Not fixed per the "data symlink is intentional; don't auto-fix" guidance.
3. **Remaining branch work.** HG 2007 and FOCAL 2024 still need their modules. Opheim 1991 remains blocked on Track A's 1988-89 statute support.

## Next steps

- HG 2007 (38 items, declarative `_ATOMIC_SPEC`) — next focused session per scope-correction's "Session B."
- FOCAL 2024 (50 indicators × weighted aggregation; L-N 2025 Suppl File 1 ground truth = 1,372 cells) — "Session C."
- After all 4 land + tests pass, branch is mergeable. The 8-rubric-confirmed promotion on `lobbyist_spending_report_includes_total_compensation` (at FOCAL landing) is the last "interesting" milestone.
