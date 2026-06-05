<!-- Generated during: convos/20260514_pri_2010_tdd.md -->
# PRI 2010 projection — module + tests landed

**Date:** 2026-05-14
**Convo:** [`../convos/20260514_pri_2010_tdd.md`](../convos/20260514_pri_2010_tdd.md)
**Spec doc:** [`../../../historical/compendium-source-extracts/results/projections/pri_2010_projection_mapping.md`](../../../historical/compendium-source-extracts/results/projections/pri_2010_projection_mapping.md)
**Rollup spec:** [`../../../historical/pri-calibration/results/20260419_pri_rollup_rule_spec.md`](../../../historical/pri-calibration/results/20260419_pri_rollup_rule_spec.md)

## What landed

Module `src/lobby_analysis/projections/pri_2010.py` (388 LOC):

- **`PRI_2010_DISCLOSURE_ATOMIC_IDS`** — tuple of the 54 disclosure-law atomic items the rollup reads (11 A + 4 B + 1 C0 + 1 D0 + 19 E1 + 18 E2).
- **`PRI_2010_ACCESSIBILITY_ATOMIC_IDS`** — tuple of the 22 accessibility atomic items (Q1..Q6, Q7a..Q7o, Q8).
- **`project_pri_atomic_item(item_id, cells)`** — single-item projection. Binary items return 0/1 from the cell value on the specified axis; Q8 passes through 0..15 typed value. Missing cell -> 0.
- **`project_pri_atomic_items(cells)`** — all 76 items in one pass.
- **`project_pri_2010_disclosure_law(cells, state)`** — top-level; wires cells -> per-item helpers -> `scoring.calibration.rollup_disclosure_law` -> `PRI2010DisclosureLawScore` (carrying state, atomic_scores, A/B/C/D/E_info_disclosed, total, percent).
- **`project_pri_2010_accessibility(cells, state)`** — top-level; analogous, using `scoring.calibration.rollup_accessibility` -> `PRI2010AccessibilityScore` (state, atomic_scores, Q1..Q6, Q7_raw, Q8_normalized, total, percent).
- **`rank_pri_2010_states(scores)`** — competition (1224) ranking, verified to reproduce published rank column.
- **`load_pri_2010_{disclosure_law,accessibility}_reference(repo_root)`** — loaders for the published 50-state sub-aggregate CSVs.

### Architectural choice — declarative spec table

CPI 2015 used one function per indicator (14 functions). PRI 2010's 76 atomic items would have been verbose under the same pattern, with 75 of 76 being near-identical binary passthroughs. The CPI session's Open Question ("Per-rubric helpers vs cross-rubric template ... defer until rubric #2") resolves here as: **introduce a declarative spec table for PRI 2010**, since the verbosity cost is concrete.

The spec table `_ATOMIC_SPEC: dict[str, (v2_row_id, axis)]` enumerates every PRI atomic item -> (compendium row, axis). The single `project_pri_atomic_item()` helper dispatches: typed passthrough for Q8, binary 0/1 otherwise. Adding a new PRI atomic item is one row in the table, no new function.

## Validation results

**Per-item layer (76 atomic items × 3 cases each = 225 binary tests + 16 Q8 tier tests + counts/wiring tests):** all 266 new tests pass.

**Existing calibration rollup tests (114 tests in `tests/test_calibration.py`):** continue to pass — the projection layer reuses `scoring.calibration.rollup_*` without modification.

**Accessibility end-to-end 50-state round-trip:** for each of 50 published states, build a cells dict from Q1..Q6 binaries + Q7_raw sum + Q8_normalized (recovered as Q8_raw = round(Q8_normalized × 15)). Run the full projection. Verify totals within ±1.0. All 50 pass with max residual ~0.05 (1-decimal rounding artifact on PRI's published total_2010 column). Q8 raw recovery introduces at most 1/30 = 0.033 per state on Q8_normalized; well inside tolerance.

**Disclosure-law per-state validation:** intentionally limited. PRI 2010 publishes only sub-aggregates (A/B/C/D/E_info_disclosed), not per-atomic-item answers. Wiring tests exercise every disclosure-law code path (A sum, B reverse-score, C0/D0 gates, E max(base) + fg double-count + E1j separate, total = sum, percent = total/37×100). Full end-to-end against the published 50-state matrix is blocked until the extraction harness (Track B) ships per-state cells.

**Rank projection:** competition-ranking (1224) reproduces the published `rank_2010` column exactly for all 50 disclosure-law totals. Verified: Alabama and Colorado both score 19 and share rank 36 (next-rank skips to 38).

## Naming-drift correction documented

The projection spec doc (written pre-`compendium-v2-promote`) used the working name pattern `principal_report_*` / `lobbyist_report_*`. The v2 TSV uses `principal_spending_report_*` / `lobbyist_spending_report_*`. Two specific cross-rubric collapses:

- **E1f_i** (`principal_report_includes_direct_compensation` in spec) -> `principal_spending_report_includes_compensation_paid_to_lobbyists` in v2 — same row CPI #203 reads.
- **E2f_i** (`lobbyist_report_includes_direct_compensation` in spec) -> `lobbyist_spending_report_includes_total_compensation` in v2 — multi-rubric row shared by CPI 2015, HG 2007, Sunlight 2015, Newmark 2005/2017, Opheim 1991, FOCAL 2024.

The 8-rubric reach on `lobbyist_spending_report_includes_total_compensation` is the kind of cross-rubric agreement the Compendium 2.0 success criterion was built to test — once two projection modules read it, a `test_lobbyist_compensation_consistent_across_rubrics` cross-rubric audit becomes well-defined.

## Items intentionally skipped (YAGNI)

7 PRI atomic items the published rollup does not read are not projected:

- **C1, C2, C3** — descriptive sub-criteria of C (definition relies on ownership / revenue structure / charter). Paper scores C as 0/1 gate (C0) only.
- **D1_present, D1_value, D2_present, D2_value** — typed materiality cells. Paper scores D as 0/1 gate (D0) only.

These remain real distinguishing observables of state law and stay in the compendium for downstream consumers and other rubrics. They are not projected because no consumer reads them today. Add helpers when a consumer needs them.

## Letter grade confirmation (per handoff)

PRI 2010 does NOT publish per-category letter grades. Published columns in both ground-truth CSVs: state name, sub-aggregates, total, percent, rank. No grade column.

This is the second rubric confirmed without per-category letter grades — CPI 2015 was the first (see CPI session's "Provisional Findings"). The handoff anticipated this: "Rubrics #2-#8 likely the same — confirm rubric-by-rubric." Confirmed for PRI.

## Phase 3 retirement (PRI-MVP) — same session

`src/scoring/smr_projection.py` -> `src/scoring/_deprecated/smr_projection.py` (with SUPERSEDED banner). `tests/test_smr_projection.py` -> `tests/_deprecated/test_smr_projection.py` (banner + import update). `pyproject.toml` adds `norecursedirs = ["_deprecated"]` so the deprecated tests are excluded from default pytest collection (still runnable when targeted directly: 10 pass + 5 skip on missing real-artifact data).

`cmd_build_smr` and its `build-smr` subparser registration removed from `src/scoring/orchestrator.py`, along with the helpers it owned exclusively (`_STATE_NAMES`, `_detect_multi_set_frequencies`).

The PRI-MVP pipeline is now under `_deprecated/`, not deleted — recoverable per the memory note on research artifacts.
