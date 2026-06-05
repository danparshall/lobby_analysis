# RESEARCH_LOG — wi-cfis-scoping

Branch: `wi-cfis-scoping` — cut 2026-06-03 off post-merge main `e84d2a1`.

Origin: Phase 4 of the archived `wi-allocation-matrix` plan (`docs/historical/wi-allocation-matrix/plans/wi_allocation_matrix.md` §178-187). The chain shipped on `wi-allocation-matrix` (115K-row TSV at `releases/wi/chain/WI_chain_2025.tsv`) maps principal → lobbyist → bill → primary-sponsor lawmaker, but is structurally missing the **lawmaker → $-flow** leg — both (a) principal → lawmaker $-contributions and (b) lobbyist → lawmaker personal $-contributions. Both live in the WI Ethics Commission's CFIS (Campaign Finance Information System), separate from the WI lobbying-disclosure source feeding `releases/wi/`.

**Scope of this branch (write-only, no scrape):** characterize CFIS access surface, identify cheapest viable ingestion path, document join keys back to the chain, and recommend whether to cut a separate `wi-campaign-finance` implementation branch.

**Timebox:** open-ended until clean schema characterization (Dan, 2026-06-03 — Q4 from the originating plan).

## Sessions

Newest first.

| Date | Convo | Status |
|---|---|---|
| 2026-06-04 | [`convos/20260604_branch_finalization.md`](convos/20260604_branch_finalization.md) | Branch-finalization wrap; archived to `docs/historical/wi-cfis-scoping/` |
| 2026-06-03 | [`convos/20260603_wi_cfis_access_surface_scoping.md`](convos/20260603_wi_cfis_access_surface_scoping.md) | Phase 4 CFIS scoping investigation — completed |

## Results

| Date | Result | Convo |
|---|---|---|
| 2026-06-03 | [`results/20260603_phase_4_cfis_scoping.md`](results/20260603_phase_4_cfis_scoping.md) — CFIS access surface characterized; FollowTheMoney.org recommended as cheapest credible source; Selenium-Sunshine via IRW model as coverage-gap fallback; FTM TOS / CC BY-NC-SA 3.0 US licensing and attribution requirements documented (§7); **recommendation = cut separate `wi-campaign-finance` implementation branch** (Phase 0 = calendar wait for the Institute-initiated review email (per quota-exceed SLA — no proactive application; only reach out if no contact by day 3-5); Phase 1 = full FTM ingest + chain join, 3-5 days post-approval). | [`2026-06-03`](convos/20260603_wi_cfis_access_surface_scoping.md) |
| 2026-06-03 | [`results/20260603_ftm_sample_query_lemahieu.md`](results/20260603_ftm_sample_query_lemahieu.md) — FTM API sample query end-to-end. LeMahieu identified (`c-t-eid=3073941`); 15-field transactional schema decoded; FTM has already canonicalized donor entities + has 3-level industry taxonomy built in; chain cross-validated (Xcel #21 donor matches chain SB 28 position; WEC PAC visible at $2K/2019); `d-llink` lobbying-flag = ~5% coverage (partial); basic-tier quota hit after ~15 queries. | [`2026-06-03`](convos/20260603_wi_cfis_access_surface_scoping.md) |

## Plans

| Date | Plan | Originating convo | Targets branch |
|---|---|---|---|
| 2026-06-03 | [`plans/wi_campaign_finance.md`](plans/wi_campaign_finance.md) — three-phase plan for the successor `wi-campaign-finance` branch (Phase 0 calendar wait for FTM expanded-access review → Phase 1 FTM ingest + lawmaker / principal / lobbyist crosswalks + materialize `releases/wi/campaign_finance/` → conditional Phase 2 Selenium-Sunshine gap-fill). Assumes the implementing agent has zero codebase context. | [`2026-06-03`](convos/20260603_wi_cfis_access_surface_scoping.md) | `wi-campaign-finance` (not yet cut) |

---

## Session: 2026-06-04 — branch_finalization

### Topics Explored

- Test-suite baseline verification on this zero-code branch (matches `wi-allocation-matrix` merge baseline: 3 failed / 1636 passed / 3 skipped / 3 xfailed).
- Branch / merge-status verification: confirmed unmerged, no PR open, ready for `finishing-a-research-branch`.
- Worktree-ordering decision: merge `wi-cfis-scoping` → main first (matches plan §17 verbatim), then cut `wi-campaign-finance` off updated main.

### Provisional Findings

- Test suite is baseline-clean. No regressions possible on a write-only scoping branch.
- All scoping deliverables (1 convo + 2 results + 1 handoff plan) shipped 2026-06-03; nothing on this branch is in-flight.

### Decisions Made

- Archive `wi-cfis-scoping` → `docs/historical/` via `finishing-a-research-branch`; merge to main; then cut successor `wi-campaign-finance` worktree.

### Next Steps

Successor work picks up on `wi-campaign-finance`:

- Phase 0 = FTM Institute expanded-access calendar wait. Dan emailed `info@opensecrets.org` proactively on 2026-06-03 to accelerate the review.
- Phase 1 starts once a probe query confirms expanded access is live.

---

## Session: 2026-06-03 — wi_cfis_access_surface_scoping

### Topics Explored

- WI Ethics Commission Sunshine (ex-CFIS) access surface — confirmed Civera-hosted Next.js SPA, no documented public API, internal Route Handlers behind same-origin CSP, 65K-row UI-export cap. All probed `/api/*` paths returned 404.
- FollowTheMoney.org as cheapest credible alternative — 50-state coverage current through 2024, single REST endpoint, free non-commercial-research access. Endpoint live-confirmed via probe.
- Investigative Reporting Workshop's `accountability_datacleaning` repo as Selenium fallback model — 8.39M-record proven scale against old CFIS through 2023, 18-column schema documented in their R-markdown processing diary.
- Wisconsin Democracy Campaign rejected as automated source (behind Sucuri CloudProxy JS gate).
- FTM API sample query executed end-to-end mid-session against LeMahieu's 2022 cycle (`c-t-eid=3073941`, 2,803 transactions / $609K / 1,822 contributors).
- Phase 0 framing iterated 3x: proactive-email recommendation → wait-and-see correction (review is Institute-initiated per quota-exceed response + TOS) → Dan opted to send proactive note anyway.
- Affiliation framing corrected: Canary Institute is not yet a 501(c)(3); the qualifying argument is the Corda Democracy Fellowship at Analogy Group + open-source non-commercial research + the published 115K-row chain TSV on main.
- FTM Terms of Service folded into the scoping doc §7 with practical attribution-surface checklist for the implementation branch.

### Provisional Findings

- **FTM has already done the donor-entity canonicalization we'd otherwise have to build.** Transaction rows expose both `Original_Name` (raw filer string) and `Contributor` (canonical entity with stable `d-eid`). The principal-side join collapses from "build a fuzzy-matcher across 1,108 principals" to "build a one-time `principal_id ↔ d-eid` crosswalk."
- **FTM ships a 3-level industry taxonomy** (`Broad_Sector` / `General_Industry` / `Specific_Business`), eliminating another piece of work.
- **Chain cross-validation works.** Xcel Energy at #21 in LeMahieu's top-25 donors matches Xcel's chain SB 28 #7 lobbying-filer position (39.9 hrs). WEC Energy Group PAC at $2K on 2019-05-04 in transaction page 0 matches WEC's chain SB 28 #2 lobbying-filer position (134.4 hrs). The infrastructure produces semantically correct connections.
- **The SB 28 / electric-utility coalition is NOT visible from LeMahieu's top-donor view alone.** It's diluted by his broader Senate-Majority-Leader receipts; ATC Management (chain SB 28 #1 at 331 hrs) doesn't appear in his donor list. **CFIS is a complement to the chain's lobbying-side activity data, not a substitute.** Both legs are needed to surface the SB 28 signal.
- **`d-llink` "Lobbying Entity?" flag is partial (~5% coverage on LeMahieu's 2022 contributions).** Concentrated on $2K corporate-PAC cluster; doesn't catch individual lobbyist contributions. Soft confirming signal, not a shortcut for the lobbyist-personal-contribution slice.
- **Basic-tier API quota is tighter than the TOS's "1,000 records/year" reads.** Dan's account exhausted basic-tier quota after ~15 queries; flagged for Institute review with documented 2-business-day SLA.

### Decisions Made

- **Cut a separate `wi-campaign-finance` implementation branch** off post-merge main, with the plan at [`plans/wi_campaign_finance.md`](plans/wi_campaign_finance.md).
- **FTM-first; Sunshine-Selenium is a coverage-gap supplement, not a duplicate ingest.**
- **Lawmaker-side crosswalk sized for ~165 sitting WI legislators** (not just the chain's 132 primary sponsors), so the parent plan's cosponsor-parsing refinement does not later trigger crosswalk rework.
- **Phase 0 of the implementation branch = calendar wait** for FTM Institute review; Dan sent a proactive email to `info@opensecrets.org` to accelerate.
- **No third Suhan-facing committed doc** — the two existing results docs are already lead-friendly; chat-side ~300-word summary drafted for Dan to send directly.

### Results

- [`results/20260603_phase_4_cfis_scoping.md`](results/20260603_phase_4_cfis_scoping.md) — full Phase 4 writeup, 9 sections including TOS / attribution requirements.
- [`results/20260603_ftm_sample_query_lemahieu.md`](results/20260603_ftm_sample_query_lemahieu.md) — FTM API decoded; LeMahieu sample query end-to-end; top-25 donor table; quota-hit observation; chain cross-validation.

### Next Steps

This branch's deliverable is complete. Successor work picks up on `wi-campaign-finance`:

- **Watch the FTM account inbox** for Institute review email (~2 business days).
- **Cut the `wi-campaign-finance` worktree** off post-merge main.
- **Execute the plan** at [`plans/wi_campaign_finance.md`](plans/wi_campaign_finance.md). Phase 0 = wait. Phase 1 = ingest + 3 crosswalks + materialize. Phase 2 = conditional Sunshine gap-fill.
