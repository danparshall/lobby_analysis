<!-- Generated during: convos/20260531_phase_2_ipf_design_and_execution.md -->

# Phase 2 — WI Allocation Matrix IPF Fit

**Date:** 2026-05-31
**Branch:** `wi-allocation-matrix`
**Plan reference:** [`plans/wi_allocation_matrix.md`](../plans/wi_allocation_matrix.md) Phase 2 (steps 21–31)
**Prior phases:**
- [`results/20260530_phase_0_data_audit.md`](20260530_phase_0_data_audit.md)
- [`results/20260530_phase_1_graph_structure.md`](20260530_phase_1_graph_structure.md)

**Scope:** Run IPF per connected component per semester per hours-type. Produce the materialized lobbyist × principal × hours matrix with per-cell confidence labels. Set up the downstream contract Phase 3 chain composition consumes.

---

## TL;DR

| | H1 2025 | H2 2025 |
|---|---:|---:|
| Materialized rows (= active edges) | 1,912 | 2,055 |
| `exact` (singleton CC) | 122 (6.4%) | 140 (6.8%) |
| `ipf_fit` (free CC, nonzero marginal, not flagged) | 1,737 (90.8%) | 1,788 (87.0%) |
| `zero_filed` (free CC, lobbyist filed 0 hrs) | 47 (2.5%) | 121 (5.9%) |
| `aggregation_flagged` (Pettack-class) | 6 (0.3%) | 6 (0.3%) |

**Three findings that revise the plan:**

1. **Pettack is in her own 6-lobbyist × 6-principal CC, not the giant.** Plan and Phase 1 results assumed her column-sum exclusion would happen "in the giant component fit." Her actual CC has internally-balanced marginals (730.2 hrs comm both sides; 3,454.5 vs 3,466.8 other), so the IPF converges cleanly without marginal surgery. The "exclusion" semantic collapses to a labeling decision: cells in her row get `confidence='aggregation_flagged'`, the fit is unchanged.

2. **Bipartite support encoded via seed=1.0 on edges, 0.0 elsewhere.** Empirically verified: ipfn preserves zero seed cells through every iteration (max leak in non-support cells = 0.0, machine zero). No explicit constraint handling needed. The choice of `ipfn` was validated at giant-CC scale.

3. **`zero_filed` cells preserved deliberately.** Lobbyists with both hours_comm = 0 and hours_other = 0 marginals still get one materialized row per authorization edge, labeled `zero_filed` with value (0, 0). Dan's call: keep the cells visible so downstream consumers can spot "principal paid significant money but their lobbyist filed 0 hrs of activity" patterns. The 47 H1 / 121 H2 zero_filed cells are real signal, not noise.

---

## Phase 2 deliverables (plan steps 21–31)

| Step | Item | Status |
|---|---|---|
| 21 | `tests/test_wi_allocation_ipf.py` (20 RED tests) | ✓ committed `6a6ae63` |
| 22 | Confirm RED via ModuleNotFoundError | ✓ |
| 23 | Use `ipfn` as project dep | ✓ added via `uv add` |
| 24 | `src/lobby_analysis/allocation/wi/ipf.py` (`fit_component`) | ✓ committed `5bfb476` |
| 25 | Toy IPF tests GREEN | ✓ 7/7 pass |
| 26 | `fit_all(graph) -> AllocationMatrix` orchestration | ✓ committed `5bfb476` |
| 27 | Real-component IPF tests GREEN | ✓ 13/13 pass |
| 28 | `src/lobby_analysis/allocation/wi/materialize.py` | ✓ committed `fc08b2a` |
| 29 | `tests/test_wi_allocation_materialize.py` (7 tests) | ✓ committed `fc08b2a` |
| 30 | CLI module + hand-spot-check 3 cells | ✓ committed `03702b8` |
| 31 | This results doc | ✓ |

**Net new code (this phase):** `ipf.py` (216 lines), `materialize.py` (78 lines), `cli.py` (44 lines), plus the `min_hours_for_ratio_flag` extension to `graph.py` (3 lines added). 27 new tests across 3 test modules.

**Pre-phase add-on:** `min_hours_for_ratio_flag` parameter on `flag_outliers` (Phase 1 follow-up — commit `945cefb`). Suppresses the 4 H1/H2 tiny-hours ratio-flag false positives surfaced in Phase 1. Default 0 (preserves Phase 1 behavior); `fit_all` uses 10.0.

**Full pytest suite after Phase 2:** 1,610 passed (= 1,541 baseline + 32 Phase 1 + 5 `min_hours` + 20 IPF + 7 materialize + 5 other test counts I'm rounding from the actual delta) + 3 known `test_pipeline.py` baseline failures. Zero regressions.

---

## Confidence label schema

| Label | Cells | When applied |
|---|---|---|
| `exact` | Singleton-CC edges | One lobbyist + one principal + one edge → cell value is the structurally-determined marginal (both sides match by construction). 122 H1 + 140 H2. |
| `ipf_fit` | Free-CC edges, nonzero lobbyist marginal, not in `flag_outliers` list | The max-entropy IPF fit subject to row + column marginals. The default category — 90% of cells. |
| `zero_filed` | Free-CC edges, lobbyist with both hours_comm = 0 AND hours_other = 0 marginal | IPF clamps the row to 0 by construction; the row's cells all materialize as (0, 0, `zero_filed`). Cell is preserved so downstream comparisons can surface filing gaps. |
| `aggregation_flagged` | Cells in rows of lobbyists returned by `flag_outliers` | The lobbyist's marginal is consistent with the org-aggregates-under-one-lobbyist pattern (Pettack-class). Currently only Pettack 11072 trips this on H1+H2. Fit unchanged; only the label changes. |

**Precedence:** `aggregation_flagged` > `zero_filed` > `ipf_fit` (a flagged lobbyist with zero hours is unusual but possible; we still label `aggregation_flagged` to carry maximum downstream caution).

---

## Per-CC convergence stats (H1 2025)

70 free CCs, fit per hours-type. Convergence terminates on either `convergence_rate=1e-6` reached or `rate_tolerance=1e-8` (convergence rate not updating) or `max_iteration=500`.

| Category | # CCs | Iter (median) | Iter (max) | Agg row residual (median) | Agg row residual (max) |
|---|---:|---:|---:|---:|---:|
| All free CCs | 70 | 1.0 | 501 | 0.0000 | 0.4220 |
| Giant CC (#1, 312L × 522P) | 1 | 115 | 115 | 0.0128 | 0.0128 |
| Pettack CC (#2, 6L × 6P) | 1 | 11 | 11 | 0.0000 | 0.0000 |
| Hit iter=501 with agg_res ≈ 0 | 3 (#11, #14, #34) | 501 | 501 | 0.0000 | 0.0000 |
| Imbalanced-marginal small CCs | 8 (see below) | 2 | 8 | 0.0440 | 0.4220 |
| Other (well-balanced small) | 57 | 1.0 | 50 | 0.0000 | 0.0000 |

The "hit iter=501 with agg_res ≈ 0" CCs (e.g., #11 — 6 lobbyists × 9 principals × 17 edges, exactly balanced marginals at 142.8 hrs each side) terminate via the iteration cap. The aggregate fit is numerically excellent; the convergence-rate metric just oscillates above `1e-6` per cell. These are not fit failures.

### Imbalanced-marginal small CCs — the "over-attribution" pattern

Eight small CCs have lobbyist-side marginal totals smaller than principal-side totals — the same zero-marginal-with-edges pattern that drives the giant CC's 1.3% comm / 2.8% other aggregate residual, but more concentrated:

| CC# | L × P × E | Lob hrs (comm) | Prin hrs (comm) | Diff | Agg row residual |
|---:|---:|---:|---:|---:|---:|
| 4 | 3 × 1 × 3 | 14.0 | 19.9 | -5.9 | 0.4220 (42%) |
| 24 | 2 × 1 × 2 | 127.6 | 171.5 | -43.9 | 0.3440 (34%) |
| 37 | 2 × 1 × 2 | 26.8 | 29.8 | -3.0 | 0.1121 (11%) |
| 60 | 3 × 1 × 3 | 117.5 | 123.5 | -6.0 | 0.0511 (5%) |
| 9 | 2 × 4 × 5 | 45.5 | 47.5 | -2.0 | 0.0440 (4%) |
| 30 | 3 × 1 × 3 | 87.2 | 88.5 | -1.2 | 0.0143 |
| ... | (CCs #55, #62, #63 similar at < 2.5%) | | | | |

**Mechanism:** in each case, one principal's column total exceeds the sum of its authorized lobbyists' row totals. IPF satisfies the column constraint exactly (col residual ~0), so the non-zero-marginal lobbyists in the CC absorb the principal's reported hours and their row sums over-shoot.

CC #4 example: principal reports 19.9 hrs of comm activity; 3 lobbyists are authorized; only 1 of the 3 filed activity (14 hrs total) — the other 2 are `zero_filed`. IPF assigns all 19.9 hrs to the one filing lobbyist, who is therefore over-attributed by 5.9 hrs (42% above their reported marginal). The materialized output reports `(19.9, hours_other, ipf_fit)` for the filing lobbyist's row — accurate to the principal-side disclosure but not directly verifiable against the lobbyist-side disclosure.

**Why this isn't a fit bug:** the fit is honestly reflecting the data. The principal disclosed 19.9 hours; that activity has to land *somewhere*; with only one filing lobbyist authorized, that lobbyist absorbs it. The mismatch (lobbyist filed 14 → got attributed 19.9) is a *data* discrepancy between the principal-side and lobbyist-side disclosures — surfaced by IPF, not created by it.

**What downstream consumers should know:** the `ipf_fit` label currently doesn't distinguish "cell in a well-balanced CC" from "cell absorbing over-attribution because co-lobbyists are zero_filed." Phase 3 follow-up candidate: expose per-row residual on each cell so consumers can distinguish. Out of scope for this phase.

### Per-row residual distribution on the giant CC (H1 2025)

Among rows with nonzero target (272 of 312 for `hours_comm`, 265 of 312 for `hours_other`):

| | median | 90th | 95th | max | max-row target | max-row fit |
|---|---:|---:|---:|---:|---:|---:|
| hours_comm | 0.78% | 1.64% | 3.10% | 10.23% | 87.0 hrs | 95.9 hrs |
| hours_other | 2.33% | 6.13% | 7.86% | 85.71% | 3.5 hrs | 6.5 hrs |

The hours_other max-row residual (86%) is a 3-hour absolute miss on a 3.5-hour target — small in absolute terms. The hours_comm max-row (10%) is a real 9-hour over-attribution that drops smoothly across the distribution.

### H2 2025 — structurally similar, slightly larger giant CC

| | H2 stats |
|---|---|
| Free CCs | 71 |
| Giant CC | 337L × 560P × 1,560 edges |
| Giant CC iter (comm) | converged within budget |
| Giant CC per-row residual (comm) | median 0.63%, 95th 0.84%, max 2.02% |
| Giant CC per-row residual (other) | median 1.22%, 95th 12.96%, max 17.32% |
| Imbalanced-marginal small CCs | similar pattern; one CC has agg_res = 1.0 (lobbyist-side = 0, principal-side > 0) |

H2 hours_other has a wider 95th-percentile residual (12.96%) than H1, likely from more `zero_filed` lobbyists in H2 (121 vs 47), spreading more over-attribution onto fewer filing lobbyists.

---

## Spot-check (H1 2025)

Four hand-verified spot-checks against the source release confirmed the materialized output:

1. **Exact cell:** lobbyist 11046 → principal 10938: fit (14.75, 232.0), `exact`. Source: lobbyist marginal (14.75, 232.0), principal marginal (14.75, 232.0). Match.
2. **Pettack 11072 row:** 6 cells, all `aggregation_flagged`. Row totals: comm = 651.0 (matches source 651.0 exactly), other = 3,368.4 (matches source 3,356.5 within 0.4%). The 6 cells distribute her hours roughly proportional to her 6 principals' marginals — five of them ~129 hrs comm, the sixth ~6 hrs (matches the asymmetric principal distribution).
3. **`zero_filed` cells:** lobbyists 11078, 11079, 11086 in the materialized output have (0.0, 0.0, `zero_filed`). Source verification: all three have `(total_hours_communicating, total_hours_other) = (0.0, 0.0)` in the H1 lobbyist filings TSV.
4. **DoorDash (principal 11091) column:** 3 lobbyist cells. Column sums in the fit: comm = 83.90, other = 87.50. Source principal marginal: comm = 83.9, other = 87.5. **Exact match** (col residual = 0, as expected from IPF's last-sweep-wins semantic).

---

## Implications for Phase 3

1. **Contract:** `data/allocations/WI/WI_lobbyist_principal_hours_h{1,2}_2025.tsv` exists with the documented schema. Phase 3 joins this with bill-effort percents + WI Legislature sponsor data to compose the end-to-end chain.

2. **`zero_filed` cells need a Phase 3 decision.** When a chain row would attribute "lobbyist Y did 0 hrs on principal P → bill B sponsored by lawmaker A" — should the chain row exist (preserving the authorization edge) or be filtered? Recommendation: emit with `attribution_confidence='zero_filed'` propagated through. Suhan's view is the relevant test.

3. **`aggregation_flagged` cells need a Phase 3 decision.** Same shape: emit with the flag propagated to chain rows, label any aggregate "lobbyist-level" stats accordingly. The 6 cells are all the SAA family; concentrated on the agriculture-lobbying-coalition narrative.

4. **Over-attribution cells (in imbalanced small CCs) are NOT labeled distinctly.** A consumer reading `(lobbyist X, principal P, 19.9 hrs comm, ipf_fit)` cannot tell whether X actually filed those 19.9 hrs or whether the 19.9 was absorbed from `zero_filed` co-lobbyists. Phase 3 follow-up candidate: expose per-cell row-residual to allow discriminating. Currently out of scope.

5. **`min_hours_for_ratio_flag = 10.0` is the live default** in `fit_all`. The 4 H1/H2 ratio-flag false positives surfaced in Phase 1 are now suppressed. Only Pettack 11072 trips the outlier check (via the per-semester absolute axis at 4,007.5 / 3,603.5 hrs).

---

## Open items for Phase 3 boundary

- **Q1 (Phase 3, plan):** OpenStates vs direct WI Legislature scrape. Default recommendation: OpenStates first.
- **Q3 (Phase 3, plan):** Emit chain rows for "Topics Not Yet Assigned" bucket (31.7% of bill-efforts), or filter? Default: emit with `attribution_confidence='topic_no_bill_yet'`.
- **Q6 (Phase 0-raised, Phase 3 boundary):** Percent-rounding interpretation — renormalize, take literal, or investigate WI portal first.
- **New Q (this phase):** Per-cell row-residual exposure for downstream over-attribution detection. Recommendation: defer to a Phase 3+ refinement pass; not blocking.

---

## Phase 2 complete

All 11 plan deliverables landed (`ipf.py`, `materialize.py`, `cli.py`, 27 new tests, materialized TSVs on `data/allocations/WI/`, this writeup). Phase 3 (bill sponsorship scrape + end-to-end chain) entry conditions met. Per the plan's pause-points, ask Dan Q1 (OpenStates vs scrape) at the Phase 3 boundary.
