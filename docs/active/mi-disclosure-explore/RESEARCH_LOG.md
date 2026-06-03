# Research Log: mi-disclosure-explore

**Created:** 2026-06-03
**Purpose:** Acquire a structured Michigan lobbying-disclosure dataset (and the MI lobbying
statutes), mirroring the Wisconsin data-grab where the data model allows.

Newest entries first.

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
