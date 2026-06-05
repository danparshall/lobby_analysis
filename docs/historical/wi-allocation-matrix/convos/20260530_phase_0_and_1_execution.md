# Phase 0 + Phase 1 execution

**Date:** 2026-05-30 (afternoon → evening, single session)
**Branch:** `wi-allocation-matrix`
**Originating convo:** [`20260530_wi_allocation_matrix_kickoff.md`](20260530_wi_allocation_matrix_kickoff.md) (plan-only kickoff earlier today)
**Plan executed:** [`plans/wi_allocation_matrix.md`](../plans/wi_allocation_matrix.md), Phase 0 + Phase 1 of 5.

## Summary

This session executed the implementation work the kickoff convo deferred — Phase 0 (data audit, no code) and Phase 1 (loader + bipartite graph + CC decomposition + outlier flagging, TDD). The kickoff convo had set the 3-leg architecture (matrix completion → bill sponsorship scrape → CFIS scoping) and written the plan; this session was strict execution with the additional discipline of "audit before code."

Phase 0 surfaced four findings that reshape the plan before any code was written: (1) lobbyist filings are semester-granular, not quarterly as the release README claims — confirmed against `tier_2_materialize.py:12` source code — which moots the convo's "time-granularity mismatch" framing and eliminates an aggregation step; (2) per-bill effort percentages are structurally undercount, not noise — only 41% of (principal, period) groups sum to 100%, median 95%, max 100%, with **no group exceeding 100%** — a finding that affects Phase 3 attribution math and warrants a new Q6; (3) active edges per semester are ~1,912 (H1) / 2,055 (H2), not the 2,254 biennium-union figure cited in plan and convo; (4) one giant 835-node connected component dominates H1 2025 (and a similar 900-node one in H2), confirming the plan's "What could change" worst-case — most cells will be IPF-modeled rather than exactly pinned.

Phase 1 then went through the strict RED → GREEN → writeup cycle for both loaders and the bipartite graph + CC layer, ending at 1,578 passing tests (= baseline 1,541 + 37 new) with zero regressions. The most surprising Phase 1 finding: **the plan's marginal-ratio outlier heuristic alone does not catch Pettack**. Her 6 SAA-family principals collectively have 4,197 H1 marginal hours, "explaining" her 4,007.5 hrs at ratio 0.95×. The actual impossibility is per-day arithmetic (32 hrs/day for one individual). I added a per-semester absolute check (>2000 hrs ≈ 16 hrs/day) to `flag_outliers`; that's what catches her. The plan's heuristic by itself is silent for the org-family-of-principals registration pattern.

## Topics Explored

### Phase 0 (data audit)
- All 6 TSVs in `releases/wi/` inspected against plan Phase 0 steps 1–10
- Percent-rounding distribution audited across all 1,428 (principal, period) groups in `WI_principal_bill_efforts.tsv`
- Authorization date coverage: 4 null `authorized_on` edges; 88.5% open edges; year breakdown (62% 2025, 32% 2024, 6% 2026)
- Pettack 11072 outlier verified at the marginal level (7,611 hrs session total, 2.84× next-highest)
- Connected-component teaser run on H1 2025 (192 components, largest 835 nodes, 122 singleton-edges)
- `tier_2_materialize.py` + `models/filings.py` read for downstream contract understanding
- Archived `wi-disclosure-explore` results writeup read

### Phase 1 (implementation)
- TDD discipline: all 32 tests written + RED-confirmed before any implementation
- Loader API: 4 entry points (`load_principal_totals`, `load_lobbyist_totals`, `load_active_edges`, `load_bill_effort_percents`) parametrized by semester string ("2025-H1" form)
- Active-edge filter: `auth_dt ≤ period_end AND (wd_dt null OR wd_dt ≥ period_start)`, with null-`authorized_on` exclusion
- Graph layer: NetworkX-backed CC decomp; `BipartiteGraph` / `Component` / `ExactlyPinned` / `FreeComponent` / `OutlierFlag` dataclasses; ("L", id) / ("P", id) node-tagging to keep sides disjoint
- Orphan handling: load layer faithfully surfaces orphans (11513, 12717); graph layer's `classify_components` falls back to principal marginal for orphan-lobbyist singletons; no special-casing required downstream
- Outlier heuristic adjustment: marginal-ratio + per-semester absolute, both checked per lobbyist, all triggered reasons concatenated into one `OutlierFlag`

## Provisional Findings

### Phase 0
- Release README mislabel ("quarterly" → should read "semester") — flagged but not fixed on this branch (multi-committer hygiene: belongs to the archived `wi-disclosure-explore` line)
- Percent-rounding pattern: max 100%, median 95%, 5th-pctl 35.7%, min 5% — strongly asymmetric undercounting (525 / 1,428 groups sum <90%). Three candidate explanations: (a) WI filings allow under-100% by design (a tracked-items share with implicit "general lobbying" residual), (b) parser-side filtering missing rows (unlikely per archived `wi-disclosure-explore` parser posture), (c) `%` is per-item, not per-period — needs WI portal investigation to resolve
- Active edges per semester are smaller than the plan and convo claimed; recomputed values landed in the Phase 0 doc
- 2026 lobbyist filings exist as zero-fill forward-look (78 nonzero comm in 2026-H1; 5 in 2026-H2) — IPF runs only on 2025-H1 and 2025-H2 where principal-side constraints exist

### Phase 1
- Pettack's data-entry pattern is invisible to marginal-ratio checks — her 6 SAA-family principals (10960, 10963, 10965, 10966, 10967, 11211) collectively booked enough hours to "explain" her at the marginal level; the impossibility is per-day, not per-marginal
- 4 H1/H2 low-hours ratio-flag false positives (lobbyists with <10 hrs against zero-marginal low-spend-exempt principals) — candidate for Phase 2 suppression via `min_hours_for_ratio_flag` param (Dan approved adding this in Phase 2)
- Free-component IPF budget: ~70 free components per semester, dominated by one giant component (~1,500 free cells, ~835-900 nodes). Smaller free components are trivial (≤50 edges)
- Test-driven discipline caught 2 mid-implementation drift issues: (a) Phase 0 2026-H2 nonzero count was conflated comm↔other; (b) loader consistency test assumed all edge-lobbyists in roster (wrong — orphans exist). Both fixed at test time.

## Decisions Made

- **No release-README fix on this branch** (multi-committer hygiene). The quarterly→semester typo is flagged in Phase 0 doc for whoever owns release maintenance.
- **`load_active_edges` stays raw** — emits orphan edges; graph layer handles them via marginal fallback. Avoids coupling load functions to roster lookup.
- **Outlier heuristic expanded** to per-semester absolute check (>2000 hrs). Both checks now run per lobbyist; reasons concatenated.
- **`networkx>=3.6.1`** added as project dep via `uv add` (Dan approved over scipy.sparse.csgraph and hand-rolled union-find).
- **Stop after Phase 1** for the session — Phase 2 (IPF + sparse matrix shape decisions + Pettack column-sum exclusion in `ipfn`'s API + materialize CLI + writeup) is a substantial new arc better started fresh.
- **Phase 2 will add `min_hours_for_ratio_flag` param** to `flag_outliers` (default 0, recommended 10) to suppress the 4 low-hours false positives.

## Results

- [`results/20260530_phase_0_data_audit.md`](../results/20260530_phase_0_data_audit.md) — Phase 0 audit (TL;DR + step-by-step against plan steps 1–10 + decisions locked + Q6 added)
- [`results/20260530_phase_1_graph_structure.md`](../results/20260530_phase_1_graph_structure.md) — Phase 1 writeup (H1+H2 CC stats, exactly-pinned vs free split, outlier findings, implications for Phase 2 IPF)

## Commits this session (on `wi-allocation-matrix`)

| SHA | What |
|---|---|
| `75dd826` | `phase 0: WI allocation matrix data audit` — Phase 0 results doc + RESEARCH_LOG update |
| `2d160ca` | `phase 1.1: RED tests for WI allocation loaders + bipartite graph` — 32 tests |
| `3711e99` | `phase 1.2: WI allocation loaders GREEN` — `src/lobby_analysis/allocation/wi/load.py` + `networkx` dep |
| `78ceddd` | `phase 1.3: bipartite graph + CC decomposition GREEN` — `src/lobby_analysis/allocation/wi/graph.py` |
| `b1388f6` | `phase 1.4: Phase 1 graph-structure results writeup` — results doc + RESEARCH_LOG update |

## Open Questions

- **Q6 (Phase 0 raised, Phase 3 boundary):** percent-rounding semantic — renormalize, take literal, or investigate the WI portal form first. Recommendation: (c) first, then (b) if form allows under-100%.
- **Pettack column-sum exclusion mechanism for IPF.** `ipfn` may not natively support "leave this row marginal free." Phase 2 design question — verify against the ipfn API on a giant-component-sized synthetic before locking in the approach.
- **Sparse representation in `ipfn`.** Giant component is ~400×435 (~174K cells) with only ~1,441 free cells. Dense numpy is ~1.4MB → fine; sparse would require checking `ipfn`'s API.
- **Original plan Q1 (OpenStates vs scrape) and Q4 (CFIS timebox)** still apply at the Phase 3 and Phase 4 boundaries respectively.

## Handoff for next session

Start at Phase 2 of [`plans/wi_allocation_matrix.md`](../plans/wi_allocation_matrix.md) (steps 21–31). Read this convo summary first for the trajectory of the Phase 0/1 findings, especially the Pettack-heuristic adjustment (so the Phase 2 IPF outlier-handling design accounts for the per-day-arithmetic axis, not just marginal-ratio). Add the `min_hours_for_ratio_flag` parameter to `flag_outliers` as part of Phase 2 work. The free-component IPF budget is ~70 components per semester, dominated by one ~1,500-cell / ~835-node giant component — verify the `ipfn` API handles this scale + figure out the Pettack column-sum exclusion mechanism before writing tests.
