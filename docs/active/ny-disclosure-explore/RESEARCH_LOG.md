# Research Log: ny-disclosure-explore

Created: 2026-06-05
Purpose: Build a New York state lobbying-disclosure pull pipeline — `releases/ny/` normalized TSVs + an `NY_chain.tsv` (company → lobbyist → bill + $, joined to Open States for the lawmaker → bill half) — modeled on the WI pipeline but adapted to NY's Socrata/Open NY bulk API.

Newest entries first.

---

## 2026-06-05 — Phase 0 schema verification EXECUTED (live Open NY, 2025)

- **Result doc:** [`results/20260605_ny_schema_verification.md`](results/20260605_ny_schema_verification.md)
- **Evidence:** `tests/fixtures/ny/sample_schema_*.json` (real sample rows, 6 datasets); `results/ny_focus_breakdown_2025.json` + `results/ny_grain_2025.json` (aggregates). Probe scripts in `scripts/ny_*.py`.
- **Gating verdicts (all pass):** (a) spend transactional **YES**; (b) real bill # on `State Bill` rows **YES** (88–96% of rows; `focus_identifying_number` = `S550-A`); (c) stance **absent, confirmed**. No-allocation/no-IPF architecture **holds**.
- **Two refinements folded into the plan:** (1) bill linkage is a *typed subset* (`focus type = State Bill`), not universal — chain closes for the 88–96% majority; (2) the API is denormalized **~1,300×** (client_semiannual 2025 = 11.2M rows but only **8,613 filings**, 1,334 lobbyist firms, 4,376 clients, 8,303 distinct state bills). Consequences: **pull via bulk CSV not API pagination**, **collapse to filing grain**, **never sum comp across raw rows** (it's filing-level, replicated).
- **Decisions locked:** chain spine = `client_semiannual` (`qym9-xzj6`); `lobbyist_bimonthly` for itemized expenses + individual people; Open States is the lawmaker spine (confirmed solid for NY); skip `parties_lobbied`.
- **Open for Dan:** per-bill dollar attribution (recommend filing-comp + `n_bills_in_filing`, no fabricated per-bill split); bill-id `-A` suffix handling for the OS join.
- **Status:** Phase 0 complete; plan updated; ready for Phase 1 (bulk-CSV acquisition) implementation.

---

## 2026-06-05 — Branch kickoff + plan drafted (session: agent, Dan AFK)

- **Convo:** [`convos/20260605_ny_pipeline_kickoff.md`](convos/20260605_ny_pipeline_kickoff.md)
- **Plan:** [`plans/ny_disclosure_pipeline.md`](plans/ny_disclosure_pipeline.md)
- **What happened:** Read the new `docs/reports/state_bulk_data_availability/` reports (NY = Tier-1, "strongest in the US," Open NY / Socrata, 6 datasets, ~278M records, 2019–present, transactional spend + bill-level linkage). Studied the WI pipeline (`io/wi/` scrape + `allocation/wi/` IPF + chain) as the model. Drafted a phased implementation plan.
- **Central architectural finding:** NY is structurally *simpler* than WI on two axes. (1) IO is a **Socrata API client**, not an HTML scraper — no per-detail-page crawl. (2) The **entire IPF/allocation layer is unnecessary** — the lobbyist↔bill link that WI had to *model* (because WI lobbyists file only aggregate hours) is **directly disclosed** in NY (transactional, bill-keyed). NY's chain is largely a direct join. What carries over from WI: the `releases/<state>/` TSV target shape, the Open States/Plural bill-sponsor spine for the lawmaker edge, provenance/traceability discipline, deterministic sort, conservation-invariant tests.
- **Top risk flagged:** NY's column-level schema is **not yet verified** (the report explicitly says NY/CO assessments are from portal docs, not from pulling files). Plan Phase 0 is a gating schema-verification step — pull one file from each of the 6 datasets and inspect actual columns before committing to the normalization design. Everything downstream is provisional on Phase 0.
- **Status:** Plan drafted, not yet implemented. Awaiting Dan's review.
