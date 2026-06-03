# RESEARCH_LOG — wi-cfis-scoping

Branch: `wi-cfis-scoping` — cut 2026-06-03 off post-merge main `e84d2a1`.

Origin: Phase 4 of the archived `wi-allocation-matrix` plan (`docs/historical/wi-allocation-matrix/plans/wi_allocation_matrix.md` §178-187). The chain shipped on `wi-allocation-matrix` (115K-row TSV at `releases/wi/chain/WI_chain_2025.tsv`) maps principal → lobbyist → bill → primary-sponsor lawmaker, but is structurally missing the **lawmaker → $-flow** leg — both (a) principal → lawmaker $-contributions and (b) lobbyist → lawmaker personal $-contributions. Both live in the WI Ethics Commission's CFIS (Campaign Finance Information System), separate from the WI lobbying-disclosure source feeding `releases/wi/`.

**Scope of this branch (write-only, no scrape):** characterize CFIS access surface, identify cheapest viable ingestion path, document join keys back to the chain, and recommend whether to cut a separate `wi-campaign-finance` implementation branch.

**Timebox:** open-ended until clean schema characterization (Dan, 2026-06-03 — Q4 from the originating plan).

## Sessions

Newest first.

| Date | Convo | Status |
|---|---|---|
| 2026-06-03 | [`convos/20260603_wi_cfis_access_surface_scoping.md`](convos/20260603_wi_cfis_access_surface_scoping.md) | In progress — Phase 4 CFIS scoping investigation |

## Results

| Date | Result | Convo |
|---|---|---|
| 2026-06-03 | [`results/20260603_phase_4_cfis_scoping.md`](results/20260603_phase_4_cfis_scoping.md) — CFIS access surface characterized; FollowTheMoney.org recommended as cheapest credible source; Selenium-Sunshine via IRW model as fallback; **recommendation = cut separate `wi-campaign-finance` implementation branch** (Phase 1 = FTM viability test against LeMahieu/SB 28). | [`2026-06-03`](convos/20260603_wi_cfis_access_surface_scoping.md) |

## Plans

None yet — this branch is write-only by design (Phase 4 of the parent plan).
