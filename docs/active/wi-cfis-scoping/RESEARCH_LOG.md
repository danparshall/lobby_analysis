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
| 2026-06-03 | [`results/20260603_phase_4_cfis_scoping.md`](results/20260603_phase_4_cfis_scoping.md) — CFIS access surface characterized; FollowTheMoney.org recommended as cheapest credible source; Selenium-Sunshine via IRW model as coverage-gap fallback; FTM TOS / CC BY-NC-SA 3.0 US licensing and attribution requirements documented (§7); **recommendation = cut separate `wi-campaign-finance` implementation branch** (Phase 0 = calendar wait for the Institute-initiated review email (per quota-exceed SLA — no proactive application; only reach out if no contact by day 3-5); Phase 1 = full FTM ingest + chain join, 3-5 days post-approval). | [`2026-06-03`](convos/20260603_wi_cfis_access_surface_scoping.md) |
| 2026-06-03 | [`results/20260603_ftm_sample_query_lemahieu.md`](results/20260603_ftm_sample_query_lemahieu.md) — FTM API sample query end-to-end. LeMahieu identified (`c-t-eid=3073941`); 15-field transactional schema decoded; FTM has already canonicalized donor entities + has 3-level industry taxonomy built in; chain cross-validated (Xcel #21 donor matches chain SB 28 position; WEC PAC visible at $2K/2019); `d-llink` lobbying-flag = ~5% coverage (partial); basic-tier quota hit after ~15 queries. | [`2026-06-03`](convos/20260603_wi_cfis_access_surface_scoping.md) |

## Plans

None yet — this branch is write-only by design (Phase 4 of the parent plan).
