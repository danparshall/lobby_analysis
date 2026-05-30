# RESEARCH_LOG — wi-allocation-matrix

Branch index. Newest entries first.

---

## Branch charter

Take the merged WI 2025-2026 lobbying-disclosure release (`releases/wi/`, 6 TSVs, ~2.9 MB, $47.5M total spend across 944 principals) and build the **{principal, lobbyist, lawmaker, bill}** influence graph that Suhan asked for. The WI lobbying data gives us **3 of 6 pairwise relations directly** (principal↔lobbyist, principal↔bill with effort %, lobbyist↔hours-aggregated-marginal); the remaining 3 are either inferable from constraints, scrapable from a free external source, or structurally absent without a separate dataset.

Three legs to the stool:

1. **Bipartite matrix completion** (within WI lobbying data): infer per-(lobbyist, principal) hours from the principal-side row sums + lobbyist-side column sums, using the authorization edges as the support pattern. Then attribute through principals' per-bill effort %s to get a modeled **lobbyist → bill** matrix.

2. **WI Legislature bill-sponsorship scrape** (`docs.legis.wisconsin.gov`): direct **lawmaker → bill** edges (sponsor, cosponsors, committee membership). Free, structured, in-scope.

3. **WI CFIS campaign finance** (Wisconsin Ethics Commission, separate database): direct **principal → lawmaker** $-flow edges via PAC + corporate-contribution disclosures, and **lobbyist → lawmaker** personal-donation edges. Closes the two relations the lobbying data structurally cannot.

With all three legs, the chain Suhan asked for — "company W spends X via lobbyist Y on bill Z sponsored by lawmaker A who received $B from W" — is **fully populated** for WI 2025-2026 from public-record disclosure data.

## Convos

- [`convos/20260530_wi_allocation_matrix_kickoff.md`](convos/20260530_wi_allocation_matrix_kickoff.md) — kickoff: 6-relation classification, IPF framing, 3-leg architecture, plan-only decision.
- [`convos/20260530_phase_0_and_1_execution.md`](convos/20260530_phase_0_and_1_execution.md) — Phase 0 (audit, no code) + Phase 1 (TDD: loaders + bipartite graph + CC decomposition + outlier flagging); landed Phase 1 with 32 new tests + zero regressions.

## Plans

- [`plans/wi_allocation_matrix.md`](plans/wi_allocation_matrix.md) — implementation plan for a fresh session (5 phases + Phase 0 setup; charter is "do all 3 legs"; CFIS leg ends in scoping writeup, not code).

## Results

- [`results/20260530_phase_0_data_audit.md`](results/20260530_phase_0_data_audit.md) — Phase 0 audit. Four findings reshape the plan: lobbyist filings are semester (not quarterly) → IPF marginals align natively; percent-rounding is structural (only 41% of (principal, period) groups sum to 100%, max 100%) → Phase 3 attribution math needs a decision; active edges per semester ~1,912 (H1) / ~2,055 (H2), not the biennium-union 2,254; one giant 835-node CC dominates the H1 graph (only ~6.4% exactly-pinned cells).
- [`results/20260530_phase_1_graph_structure.md`](results/20260530_phase_1_graph_structure.md) — Phase 1 graph + CC writeup. H1 / H2 both dominated by one giant CC (835 / 900 nodes); 122 / 140 exactly-pinned singletons; 70 / 71 free components for Phase 2 IPF. Pettack catchable only via per-day arithmetic (the plan's marginal-ratio heuristic alone is silent — her 6 SAA-family principals' combined 4,197 hr marginal "explains" her 4,007.5 hrs). 4 low-hours ratio-trips against zero-marginal principals — candidate for `min_hours_for_ratio_flag` suppression in Phase 2.

---

## Session: 2026-05-30 (evening) — phase_1_loaders_and_graph

**Convo:** [`convos/20260530_phase_0_and_1_execution.md`](convos/20260530_phase_0_and_1_execution.md)

### Topics Explored
- TDD cycle: RED tests for loaders (4 fns) + graph (4 fns + 5 dataclasses); confirmed RED via ModuleNotFoundError
- Loader: 4 entry points, semester-string ("2025-H1") input form; active-edge filter `auth <= period_end AND (wd null OR wd >= period_start)`; null-`authorized_on` exclusion (4 edges)
- Graph: NetworkX-backed CC decomp; BipartiteGraph/Component/ExactlyPinned/FreeComponent/OutlierFlag dataclasses
- Outlier-flag heuristic adjustment mid-implementation: marginal-ratio check ALONE doesn't catch Pettack (the SAA-family 6 principals "explain" her hours at the marginal level); added per-semester absolute check (>2000 hr, ~16 hrs/day)

### Provisional Findings
- Orphan lobbyists (11513, 12717) in authorizations but not in roster — loader surfaces faithfully; graph layer falls back to principal marginal in singleton classify
- Per-semester structure stable: H2 slightly larger than H1 across the board (more auths accumulate by mid-year); same "one giant CC" pattern
- 93% of edges live in free components (need IPF); 6.5% are exactly-pinned singletons; outliers ~ 2-4 per semester

### Results
- [`results/20260530_phase_1_graph_structure.md`](results/20260530_phase_1_graph_structure.md)

### Next Steps
- Phase 2: IPF on free components (toy 3×3 + sparse + max-entropy verification + real giant CC); use `ipfn` package per plan
- Phase 3 boundary will surface Q1 (OpenStates vs scrape) to Dan; Phase 4 boundary will surface Q4 (CFIS timebox)
- Optional Phase 2 refinements: `min_hours_for_ratio_flag` to suppress the 4 low-hours false positives

---

## Session: 2026-05-30 (afternoon) — phase_0_data_audit

**Convo:** [`convos/20260530_phase_0_and_1_execution.md`](convos/20260530_phase_0_and_1_execution.md)

### Topics Explored
- Walked all 6 TSVs of `releases/wi/` against plan Phase 0 steps 1–10
- Confirmed `WI_principal_bill_efforts.tsv` has embedded newlines in `item_description` — pandas-correct, `wc -l` undercounts by 4
- Audited percent-rounding distribution across all 1,428 (principal, period) groups
- Verified Pettack 11072 outlier (7,611 hrs = 1,216.5 comm + 6,394.5 other; 2.84× next-highest lobbyist)
- Computed H1 2025 connected-component decomposition (preview of Phase 1)
- Diagnosed lobbyist-filings-are-semester (release README is wrong; source code at `tier_2_materialize.py:12` is correct)

### Provisional Findings
- See Results doc TL;DR: 4 findings reshape the plan. Key: percent-rounding is asymmetric (max 100%, median 95%, 5th-pctl 35.7%) → structural undercounting, not noise.
- Confidence column in Phase 2 output will be ~6.4% `exact` / ~93.6% `ipf_fit` / small `outlier_flagged` tail — dominated by the giant CC.

### Results
- [`results/20260530_phase_0_data_audit.md`](results/20260530_phase_0_data_audit.md)

### Next Steps
- Phase 1 (graph construction + CC analysis) — TDD: write failing tests RED → loader + graph → GREEN → CC writeup
- Q6 (percent-rounding interpretation) remains open until Phase 3 boundary
- Release-README mislabel ("quarterly") flagged but not fixed on this branch — separate small commit on release-maintenance line

---

## Session: 2026-05-30 — wi_allocation_matrix_kickoff

### Topics Explored
- Walked WI 2025-2026 release against Suhan's "company → lobbyist → lawmaker → bill" ask
- Clarified principal-files-bill-efforts (direct disclosure, not attribution)
- Enumerated 6 pairwise relations: 3 direct in WI lobbying, 1 IPF-inferable, 1 free external scrape, 2 need CFIS
- Bipartite matrix completion math: ~2,254 cells / semester, ~3,432 constraints with both hours-types; decomposes into components with many exactly-pinned cells
- Three legs of the stool: matrix completion (WI lobbying), bill sponsorship (WI Legislature / OpenStates), CFIS (Wisconsin campaign finance — scoping only this branch)

### Provisional Findings
- Company → bill is **direct sworn disclosure** in WI, not modeling — corrects earlier framing
- Matrix completion is genuinely tractable (standard IPF / RAS), with a non-trivial fraction of cells exactly pinned in singleton CC components
- The "lobbyist X targeted bills sponsored by lawmaker Y" derived edge is a defensible proxy for influence target but NOT for direct contact; flag clearly in any Suhan-facing output
- CFIS is the structural completion of Suhan's chain — without it the chain is incomplete for the (principal → lawmaker) $-edge

### Results
(none — plan-only session)

### Next Steps
- Fresh-context session executes `plans/wi_allocation_matrix.md` starting at Phase 0
- Implementing agent must read `convos/20260530_wi_allocation_matrix_kickoff.md` first for the reasoning trajectory
