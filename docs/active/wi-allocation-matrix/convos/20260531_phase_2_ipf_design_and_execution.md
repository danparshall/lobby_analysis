# Phase 2 IPF — design and execution

**Date:** 2026-05-31
**Branch:** `wi-allocation-matrix`
**Originating convo:** [`20260530_phase_0_and_1_execution.md`](20260530_phase_0_and_1_execution.md) (Phase 0/1 produced the open questions this session resolved)
**Plan executed:** [`plans/wi_allocation_matrix.md`](../plans/wi_allocation_matrix.md), Phase 2 (steps 21–31) plus the Phase 2-tagged `min_hours_for_ratio_flag` add-on flagged at the Phase 1 boundary.

## Summary

Phase 2 — IPF fit per connected component, materialize to TSV, end-to-end CLI — landed in a single session with 27 new tests, zero regressions, and four hand-verified spot-checks. The bigger story is what the session *learned* before writing tests: the plan's "Pettack column-sum exclusion mechanism" assumption (drop her marginal from the giant CC fit) was based on a model of where Pettack sits in the graph that the actual data disagrees with. Pettack is in her own 6-lobbyist × 6-principal CC where the marginals balance natively (730.2 hrs comm both sides, 3,454.5 vs 3,466.8 other), so the IPF converges cleanly without any marginal surgery. The "exclusion" collapses from a fit-modification question to a labeling question — cells in her row get `confidence='aggregation_flagged'`, and the math runs unchanged.

The session also produced the right confidence-label schema (negotiated with Dan): `exact` for singleton CCs, `ipf_fit` for free-CC nonzero-marginal cells, `zero_filed` for cells where the lobbyist reported (0, 0) hours, and `aggregation_flagged` for cells in the row of any `flag_outliers`-returned lobbyist. The `zero_filed` category is deliberately preserved (not dropped from the output) per Dan's call: a journalist or downstream check can spot "principal paid significant money but their authorized lobbyist filed 0 hrs" patterns from these cells. 47 H1 / 121 H2 cells fall into this category and are real signal, not noise.

The session also surfaced a Phase 3-relevant pattern that wasn't in the plan: **small-CC over-attribution**. Eight free CCs (out of 70 in H1) have principal-side hours exceeding the sum of their authorized lobbyists' filed hours — same mechanism as the giant CC's zero-marginal-lobbyists-with-edges, but more concentrated. CC #4 (3L × 1P × 3E): principal reports 19.9 hrs, only 1 of 3 lobbyists filed (14 hrs), IPF assigns all 19.9 to the one filing lobbyist → 42% over-attribution. The fit is mathematically correct (the data has to land somewhere), but the `ipf_fit` label doesn't distinguish "well-pinned cell" from "cell absorbing over-attribution because co-lobbyists are zero_filed." Flagged in the writeup as a Phase 3+ refinement candidate.

## Topics Explored

### Empirical ipfn API probe (before any tests)
- 3×3 toy from ipfn docstring: API works, converges in <1ms, residual ~1e-7
- **Bipartite support pattern via seed=1.0 on edges, 0.0 elsewhere:** confirmed empirically that zero seed cells stay at exactly 0.0 (machine zero) through every iteration; max leak in non-support cells = 0.0. No explicit constraint handling needed for bipartite structure.
- **Pettack-style marginal exclusion:** mathematically, you can emulate "leave row marginal free" by replacing the row target with `T_col - sum_of_other_rows`. Verified on toy. **But moot for the real data** because Pettack's CC marginals balance natively.
- **Scale:** 312×523 dense matrix with 1,441 nonzero seed cells (giant CC) converges in ~340 ms for hours_comm, ~80 ms for hours_other. Per-CC iteration on all 70 free components ~ sub-second total.

### Pettack-not-in-giant-CC discovery
- Found by directly inspecting which CC contains lobbyist 11072
- Pettack CC #2: 6 lobbyists × 6 principals × 11 edges, all 6 principals are SAA-family (10960, 10963, 10965, 10966, 10967, 11211)
- Marginal balance within the CC: hours_comm 730.2 == 730.2 exactly; hours_other 3454.5 vs 3466.8 (diff -12.2, ~0.4%)
- Plan and Phase 1 results had assumed exclusion from the *giant* CC — that assumption is wrong; the marginal-imbalance mechanism the exclusion was supposed to fix doesn't manifest in Pettack's actual CC

### Pushback exchange with Dan on Pettack labeling
- Dan asked "is this an illegal filing pattern?"
- Session pushed back: three readings (filing convention / firm-registered / actually non-compliant) are all plausible; we don't have evidence to discriminate; legal speculation overreaches what the data supports
- Dan re-framed: the data are the data; if Pettack gets bad publicity for the org-aggregation pattern, that's on them, not us. Just flag the aggregation pattern descriptively and let downstream consumers (Suhan, journalists) do what they want with it.
- Landed on `confidence='aggregation_flagged'` — describes the observable pattern without claiming legality

### Phase 2 test design and residual tolerance
- Plan literal "< 0.01 per-row residual" is unachievable on real giant CC (worst-row 10% comm, 86% other, both driven by zero-marginal lobbyists)
- Three test designs offered to Dan: aggregate-only with per-row reported in writeup (recommended), per-row with tiny-hours carveouts, plan literal with surgery
- Settled on aggregate-only with per-row reported; documented per-CC stats in the writeup including the imbalanced-marginal small-CC over-attribution table

### Implementation
- `min_hours_for_ratio_flag` parameter on `flag_outliers` (Phase 1 follow-up): 5 RED tests → GREEN
- `fit_component(component, hours_type)` in `ipf.py`: 7 toy + 6 real-data tests → GREEN
- `fit_all(graph)` orchestration: 5 tests → GREEN
- `materialize_allocation_matrix(release_dir, output_dir)` + 7 tests → GREEN
- CLI module + stdout capture (ipfn unconditionally prints "ipfn converged" regardless of verbose level) → clean output
- Hand-spot-check of 4 cells against the source TSVs: exact cell round-trip ✓, Pettack row total within 0.4% of source ✓, zero_filed cells match source (0,0) ✓, DoorDash column sum **exactly** matches source (83.90 == 83.9, 87.50 == 87.5) ✓

## Provisional Findings

- **Bipartite support via zero-seed encoding works at scale.** No leak; no explicit handling. The ipfn library's zero-stays-zero invariant is the right primitive for bipartite IPF.
- **Per-CC IPF is the right granularity.** 70 free CCs per semester; the giant CC is 75% of edges; all others are small enough to be near-trivial. No need for sparse-matrix representation (~174K cells dense is 1.4MB).
- **Pettack is not the only over-attribution case, but she IS the only one currently flagged.** The small-CC over-attribution pattern (CC #4 type) affects ~8 H1 CCs but lobbyists in those CCs don't trip the `>2,000 hrs/semester` absolute check. Different mechanism, same root cause (zero-marginal lobbyists with edges in the same CC).
- **Aggregate row residual on giant CC: 1.3% comm / 2.8% other.** Median per-row residual: 0.78% comm / 2.33% other. Worst per-row: 10.2% comm (87→95.9 hrs, real miss), 85.7% other (3.5→6.5 hrs, tiny-absolute case).
- **ipfn's `converged` flag is unreliable as a fit-quality signal.** 3 of 70 H1 CCs hit `max_iteration=500` with `agg_res=0` — the convergence-rate metric oscillates but the fit is numerically excellent. The aggregate row residual is the better signal.
- **Materialized output schema:** 1,912 rows H1 / 2,055 rows H2 (= active edge counts). Distribution: 6.4-6.8% `exact`, 87-91% `ipf_fit`, 2.5-5.9% `zero_filed`, 0.3% `aggregation_flagged`.

## Decisions Made

- **No marginal surgery for Pettack.** IPF runs as-is on every free CC. The fit converges within her balanced 6×6 CC; cells in her row are labeled `aggregation_flagged` by `fit_all` based on the `flag_outliers` output. The plan's "drop her column-sum constraint" mechanism is unnecessary.
- **`zero_filed` cells preserved in the output** (not dropped). Dan's call. Downstream comparisons can use these to surface filing gaps.
- **Confidence label precedence:** `aggregation_flagged` > `zero_filed` > `ipf_fit`. Carries maximum downstream caution.
- **`min_hours_for_ratio_flag` default in `fit_all` is 10.0.** Suppresses the 4 H1/H2 tiny-hours false positives from Phase 1. Pettack still caught via the per-semester absolute axis.
- **Aggregate row residual < 5% per CC tested on giant only.** Per-row residual distribution reported in writeup, not asserted. Small-CC over-attribution acknowledged as data-quality fixture.
- **Materialize CLI defaults:** `releases/wi` → `data/allocations/WI/`. CLI is a thin argparse wrapper over `materialize_allocation_matrix`.
- **Stop at Phase 2 for the session.** Phase 3 (bill sponsorship scrape + chain composition) is a substantial new arc starting with the OpenStates-vs-scrape Q1 boundary question for Dan.

## Results

- [`results/20260531_phase_2_ipf_fit.md`](../results/20260531_phase_2_ipf_fit.md) — Phase 2 writeup (per-CC convergence stats, giant-CC residual distribution, small-CC over-attribution table, spot-check verification, Phase 3 implications)

## Commits this session (on `wi-allocation-matrix`)

| SHA | What |
|---|---|
| `945cefb` | `phase 2.0: add min_hours_for_ratio_flag param to flag_outliers` |
| `6a6ae63` | `phase 2.1: RED tests for WI allocation IPF fit` |
| `5bfb476` | `phase 2.2: WI allocation IPF fit GREEN` |
| `fc08b2a` | `phase 2.3a: WI allocation materialize GREEN` |
| `03702b8` | `phase 2.3b: WI allocation CLI + ipf stdout cleanup` |

## Open Questions

- **Q1 (Phase 3 boundary):** OpenStates first vs direct WI Legislature scrape first? Plan default: OpenStates first. **Ask Dan at Phase 3 entry.**
- **Q3 (Phase 3 boundary):** Emit chain rows for "Topics Not Yet Assigned" bucket (31.7% of bill-efforts), or filter?
- **Q4 (Phase 4 boundary):** CFIS investigation scope — 0.5 day timebox vs open-ended?
- **Q6 (Phase 0-raised, Phase 3 boundary):** Percent-rounding interpretation — renormalize / take literal / investigate WI portal first.
- **New Q (Phase 2-raised):** Per-cell row-residual exposure for downstream over-attribution detection. The small-CC over-attribution pattern (CC #4-class) is invisible in the current `ipf_fit` label. Recommendation: defer to Phase 3+ refinement.
- **Pettack legality (separate WI-statute branch):** Whether org-aggregation of staff hours under one registered lobbyist's name is permissible under WI §13.62. Not blocking Phase 2 or Phase 3; flagged as a compendium-side question that would belong on a different branch entirely.

## Handoff for next session

Start at Phase 3 of [`plans/wi_allocation_matrix.md`](../plans/wi_allocation_matrix.md) (steps 32–42). **Pause immediately at step 32 to ask Dan Q1 (OpenStates vs direct scrape).** Read this convo summary first for the Phase 2 trajectory — especially the Pettack-not-in-giant finding (changes how `aggregation_flagged` cells are interpreted) and the small-CC over-attribution pattern (Phase 3 chain composition decisions on what to do with these cells, related to Q3 on the "Topics Not Yet Assigned" bucket). The materialized H1 + H2 TSVs at `data/allocations/WI/WI_lobbyist_principal_hours_h{1,2}_2025.tsv` are the Phase 3 input contract — schema `(lobbyist_id, principal_id, hours_comm, hours_other, confidence)`.
