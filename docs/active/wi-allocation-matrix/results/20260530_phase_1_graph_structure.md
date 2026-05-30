# Phase 1 — WI Allocation Matrix Graph Structure

**Date:** 2026-05-30
**Branch:** `wi-allocation-matrix`
**Plan reference:** [`plans/wi_allocation_matrix.md`](../plans/wi_allocation_matrix.md) Phase 1 (steps 11–20)
**Prior phase:** [`results/20260530_phase_0_data_audit.md`](20260530_phase_0_data_audit.md)
**Scope:** Build the bipartite (lobbyist, principal) graph from active authorizations per semester, run connected-component decomposition, classify components into exactly-pinned vs free, flag outliers. Set up the IPF problem size for Phase 2.

---

## TL;DR

| | H1 2025 | H2 2025 |
|---|---:|---:|
| Active edges | 1,912 | 2,055 |
| Distinct lobbyists | 632 | 678 |
| Distinct principals | 823 | 880 |
| Total bipartite nodes | 1,455 | 1,558 |
| Connected components | 192 | 211 |
| Largest component (nodes) | **835** | **900** |
| Largest component (edges) | **1,441** | **1,560** |
| Exactly-pinned singleton-edge components | 122 | 140 |
| Free (≥2-edge) components | 70 | 71 |
| Edges in exactly-pinned components | 122 (6.4%) | 140 (6.8%) |
| Edges in free components | 1,790 (93.6%) | 1,915 (93.2%) |
| Outliers flagged | 2 | 4 |

**The IPF problem to solve in Phase 2:** ~70 free components per semester, dominated by one giant component (~1,500 edges). The other ~69 free components have ≤ 50 edges each. **~93% of edges need IPF; ~6.5% are exactly pinned.**

---

## Phase 1 deliverables (plan steps 11–20)

| Step | Item | Status |
|---|---|---|
| 11 | `tests/test_wi_allocation_load.py` (4 RED loader test groups) | ✓ committed `2d160ca` |
| 12 | Confirm load tests RED | ✓ (ModuleNotFoundError) |
| 13 | `tests/test_wi_allocation_graph.py` (toy + real graph tests) | ✓ committed `2d160ca` |
| 14 | Confirm graph tests RED | ✓ (ModuleNotFoundError) |
| 15 | `src/lobby_analysis/allocation/wi/__init__.py` | ✓ committed `3711e99` |
| 16 | `src/lobby_analysis/allocation/wi/load.py` (4 loaders) | ✓ committed `3711e99` |
| 17 | Load tests GREEN | ✓ 20/20 pass |
| 18 | `src/lobby_analysis/allocation/wi/graph.py` (BipartiteGraph + 4 fns) | ✓ committed `78ceddd` |
| 19 | Graph tests GREEN | ✓ 17/17 pass |
| 20 | This results doc | ✓ |

**Full pytest suite after Phase 1:** 1,578 passed (= baseline 1,541 + 37 new) + 3 known `test_pipeline.py` baseline failures (unchanged). Zero regressions.

**Net new code:** 470 lines in `src/lobby_analysis/allocation/wi/` (`load.py` 158, `graph.py` 261, two `__init__.py` 21+30). 557 lines of behavior tests. New dep: `networkx>=3.6.1`.

---

## Connected-component structure

The H1 2025 component size distribution:

| Component size (nodes) | Count | Cumulative nodes | Edges in these CCs |
|---:|---:|---:|---:|
| 2 (singleton edge) | 122 | 244 | 122 |
| 3 | 38 | 358 | 76 |
| 4–5 | 17 | 433 | 49 |
| 6–15 | 8 | 530 | 79 |
| 16–33 | 4 | 620 | 64 |
| **835 (giant)** | **1** | **1,455** | **1,441** |

The giant component contains **75% of all H1 2025 edges** (1,441 / 1,912) on 57% of all nodes (835 / 1,455). It is the IPF problem — everything else is either trivial (singleton edges, structurally pinned) or small enough to solve trivially.

H2 2025 is structurally similar but slightly larger (900-node / 1,560-edge giant component). The next-largest H2 component is 36 nodes. The "one giant CC" scenario the plan anticipated is real and persistent across semesters.

---

## Exactly-pinned cells

A singleton-edge component (one lobbyist, one principal, one edge) means **only one possible cell value is consistent with both marginals**: the lobbyist's marginal must equal the principal's marginal, both equal the cell. The IPF stage has nothing to fit.

H1 2025 has **122** such cells; H2 2025 has **140**. Combined across semesters, ~262 cells are known with zero modeling error.

**Caveat — orphan-lobbyist singletons.** A handful of singleton components have a lobbyist on the orphan list (11513, 12717 — Phase 0 finding §6). For those, there is **no lobbyist marginal** — we fall back to the principal's marginal. The cell value is still structurally determined (only one principal involved), but the implicit assumption is "the principal's marginal IS the work done by this lobbyist." For orphan lobbyists this is plausible (they only appear in a single edge) but not literally verified.

---

## Outlier flags

Two checks, one `OutlierFlag` per flagged lobbyist:

1. **Marginal-ratio check** (plan default): `lobbyist_hours > 2× sum(attributable principal marginals)`.
2. **Per-semester absolute check** (added during implementation): `lobbyist_hours > 2,000` (~16 hrs/day across 125 working days, the "non-human" threshold).

### Pettack (11072) — only flagged by per-semester check

The plan assumed the marginal-ratio check alone would catch Pettack. The data disagrees:

- Pettack's H1 hours: 4,007.5 (651 comm + 3,356.5 other)
- Pettack's 6 authorized principals (10960, 10963, 10965, 10966, 10967, 11211) have combined H1 marginal: **4,197 hrs**
- Ratio: 4,007.5 / 4,197 = **0.95×** — well below 2× → marginal-ratio check is silent

Why: Pettack is the dominant or sole lobbyist for all 6 principals (3 are solo-Pettack; 3 share with lobbyists that have negligible marginals). The 6 principals collectively booked 4,197 hrs of activity, and Pettack essentially owns all of it. The marginal arithmetic is internally consistent.

The **per-day arithmetic** is what's impossible: 4,007.5 hrs / 125 working days = **32 hrs/day for one individual**. The README's "organization aggregates org-wide staff hours under one lobbyist" interpretation is consistent with this. The per-semester absolute check (2,000 hr cap = 16 hrs/day) catches Pettack at both semesters (H1: 4,007.5; H2: 3,603.5).

This is a finding worth documenting beyond the test — **the plan's marginal-ratio heuristic alone is insufficient for the Pettack-class data-entry pattern**. The org-family-of-principals registration pattern (one lobbyist named across many related principals) is invisible to ratio-based checks. Phase 2 must use the per-day absolute check OR a more refined attribution analysis to scope this kind of outlier.

### "False-positive" ratio flags (tiny hours, zero attributable)

A small number of lobbyists are ratio-flagged with very low absolute hours:

| Semester | Lobbyist | Hours | Max attributable | Note |
|---|---:|---:|---:|---|
| H1 | 11065 | 0.2 | 0.0 | Tiny hours; principal(s) are zero-marginal |
| H2 | 13854 | 0.7 | 0.0 | Same pattern |
| H2 | 12709 | 6.0 | 0.0 | Same pattern |
| H2 | 13856 | 0.7 | 0.0 | Same pattern |

These aren't really "outliers" — they're cases where the lobbyist reported a tiny amount of work for principals whose marginals are 0 (likely low-spend-exempt principals per Phase 0 caveat #2). The ratio check trips trivially when the denominator is 0.

For Phase 2: consider suppressing ratio flags where `lobbyist_hours < threshold_min_hours` (e.g., 10 hrs) — these don't impact the IPF fit meaningfully because they're tiny.

---

## Implications for Phase 2 (IPF)

**The IPF problem per semester:**
- 70-71 free components requiring IPF
- One giant component (~1,500 free cells, ~835-900 nodes)
- ~69 small components (≤ 50 edges each) where IPF converges trivially

**Giant component sub-problem analysis (H1):**
- 1,441 free cells
- ~400 lobbyists + ~435 principals (rough split of 835 nodes)
- **~835 marginal constraints** (one per node) for **1,441 free cells** → **under-determined by ~606 dimensions**
- Max-entropy resolution: IPF picks the unique solution maximizing entropy subject to the marginals

The under-determination is fundamental to the bipartite-matrix-completion problem. The plan's `confidence ∈ {exact, ipf_fit, outlier_flagged}` column will be:
- ~6.4-6.8% `exact` (singleton-edge cells)
- ~93% `ipf_fit` (cells in free components; max-entropy modeled)
- A small `outlier_flagged` tail (Pettack-class cells excluded from the fit)

**Outlier handling for IPF (per plan defaults):**
- **Pettack 11072**: flag + exclude her column-sum constraint from the giant component fit. Her 6 principals' rows still constrain the remaining cells.
- **Low-hours ratio-trips (4 lobbyists, < 10 hrs each)**: no action needed; the IPF fit on these cells will be near-0 by marginal constraint.

**Orphan lobbyists (11513, 12717):**
- Edges remain in the graph (per design — load layer is faithful, graph layer drops nothing).
- Their components are singleton-edges (each is a sole lobbyist for one principal).
- Classified as `ExactlyPinned` via principal-marginal fallback.
- IPF doesn't see them (singletons don't enter IPF input).
- Phase 2 needs no special handling — the classification already accommodates them.

---

## Open items for Phase 2 boundary

- **Ratio-flag suppression for low-hours cases.** Add an optional `min_hours_for_ratio_flag` param to `flag_outliers`. Default: 0 (current behavior); recommended Phase 2 setting: 10 hrs.
- **Pettack column-sum exclusion mechanism.** Decide: drop her column from the marginals dict, or set it to a sentinel? `ipfn` may not accept missing constraints — verify before designing.
- **Giant-component fit budget.** With ~835 marginals and 1,441 free cells, IPF iterations should be modest (< 100 typically for this size); set a max-iteration cap of 500 with `1e-6` convergence per the plan's tests.
- **Open follow-up from Phase 0 still applies.** Percent-rounding semantic (Q6) is for Phase 3, not Phase 2. The IPF fit doesn't consume the bill-effort percents.

---

## Phase 1 complete

All 4 plan deliverables landed (`load.py`, `graph.py`, RED tests, GREEN tests). Phase 2 (IPF) entry conditions met. Next: per the plan's pause-points, ask Dan Q1 (OpenStates vs scrape) at the Phase 3 boundary and Q4 (CFIS timebox) at the Phase 4 boundary. Phase 2 has no scheduled pause — proceed when ready.
