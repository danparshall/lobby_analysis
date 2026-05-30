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

## Plans

- [`plans/wi_allocation_matrix.md`](plans/wi_allocation_matrix.md) — implementation plan for a fresh session (5 phases + Phase 0 setup; charter is "do all 3 legs"; CFIS leg ends in scoping writeup, not code).

## Results

(none yet)

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
