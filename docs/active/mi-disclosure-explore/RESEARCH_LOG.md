# Research Log: mi-disclosure-explore

**Created:** 2026-06-03
**Purpose:** Acquire a structured Michigan lobbying-disclosure dataset (and the MI lobbying
statutes), mirroring the Wisconsin data-grab where the data model allows.

Newest entries first.

---

## 2026-06-03 (later) — Phase 0 desk recon: no bulk download → scrape MiTN

**Session type:** recon (desk).
**Result doc:** [`results/20260603_mi_portal_recon.md`](results/20260603_mi_portal_recon.md)
**Decisions locked by Dan:** (a1) entity+expenditure MVP, no chain; (a2) **2025 vintage only**;
(a3) proceed with recon.

**Findings:**
- **No reliable public bulk download for 2025 MI lobby data.** Acquisition primitive =
  **scrape/drive the MiTN entellitrak app** (`mi-boe.entellitrak.com/etk-mi-boe-prod/`).
- Michigan has two lobby systems: **MiTN** (2024+, holds 2025, JS/AJAX, per-result export
  only) and **legacy NIC** (`miboecfr.ni{c,ct}usa.com`, relationship data 1982–2023, bulk
  `mi_lobby.sh` dump, but host is **decaying** — expired TLS cert, timeouts). The legacy bulk
  dump is the **wrong vintage** for our 2025 target; useful only as a historical cross-check.
- Confirmed facets incl. **"Employed By"** (the WI authorization-graph analog) and the
  **Itemized Expenditure Form (LR-4)** + semi-annual Financial Report Summary.
- `robots.txt` = 404 (no declared restrictions); still use ≥1.0 s delay.

**Next:** short **live-browser recon** (Playwright / webapp-testing) to capture the
entellitrak AJAX endpoint + decide between (A) search-and-export vs. (B) WI-style
enumerate-and-fetch. Then start Phase 1.

---

## 2026-06-03 — kickoff: WI reconstruction, MI recon, chunked acquisition plan

**Session type:** planning / reconnaissance (no code).
**Convo:** [`convos/20260603_mi_data_grab_planning_and_kickoff.md`](convos/20260603_mi_data_grab_planning_and_kickoff.md)
**Plan produced:** [`plans/mi_data_acquisition.md`](plans/mi_data_acquisition.md)

**What happened:**
- Reconstructed the WI data-grab from `releases/wi/`, `src/lobby_analysis/io/wi/`, and the
  archived `docs/historical/wi-disclosure-explore/` branch: a two-tier scrape of
  `lobbying.wi.gov` producing 6 TSVs (entities, authorization edges, principal/lobbyist
  filings, per-bill effort allocations) + a derived principal→lobbyist→bill→sponsor chain,
  plus a separate statute retrieval (WI Ch. 13, Justia, 2010/2015/2025 vintages).
- Recon'd Michigan: lobby disclosure lives in **MiTN** (Michigan Transparency Network,
  launched 2024, on the **entellitrak** platform at `mi-boe.entellitrak.com`); legacy
  **E-Lobby** data migrated in; MiTN supports per-filing export; older NIC CGI endpoint
  also exists for itemized expenditure analysis.

**Key finding (load-bearing):** Michigan's lobby disclosure is **expenditure-centric, not
bill-centric**. MI lobbyists file semi-annual Financial Report Summaries with itemized
expenditures benefitting public officials, but report **no bills, no positions, no per-bill
effort**. WI's bill-effort table and the entire allocation chain were enabled by a
WI-specific filing field that **does not exist in MI**. Therefore:
- The **entity + expenditure** dataset ports (registrants, the "Employed By" employer graph,
  expenditure filings).
- The **bill-attribution chain does not** port from disclosure data alone.

**Decisions:**
- Branch/worktree `mi-disclosure-explore` created; `data/` symlinked.
- Plan scope = data + statute acquisition only; analysis deferred.
- Plan is chunked (Phase 0 recon → Phase 1 registrants → Phase 2 employer graph →
  Phase 3 expenditure filings → Phase 4 statutes), each chunk sized for a focused subagent.

**Open questions:** bulk vs. per-filing export (gates everything); vintage depth from the
E-Lobby migration; whether entity+expenditure alone is the accepted MI MVP. See convo.

**Next:** Dan to review the plan + the no-chain finding; then execute Phase 0 recon to
resolve the export question before committing to a scrape vs. download strategy.
