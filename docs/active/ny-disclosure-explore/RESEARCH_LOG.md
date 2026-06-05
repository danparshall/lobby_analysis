# Research Log: ny-disclosure-explore

Created: 2026-06-05
Purpose: Build a New York state lobbying-disclosure pull pipeline — `releases/ny/` normalized TSVs + an `NY_chain.tsv` (company → lobbyist → bill + $, joined to Open States for the lawmaker → bill half) — modeled on the WI pipeline but adapted to NY's Socrata/Open NY bulk API.

Newest entries first.

> **HANDOFF (next session):** Phase 1 (acquisition) is done — `io/ny/acquire.py` ships `download_bulk_csv()` + `SocrataProbeClient`, 10 green tests (commit `db64354`). Pick up at **Phase 2 (per-dataset parse + materialize)** in [`plans/ny_disclosure_pipeline.md`](plans/ny_disclosure_pipeline.md), starting with the **grain-collapse** step (the load-bearing dollar-conservation guard) and the per-dataset **column map** (Phase 0 flagged inconsistent names across the 6 datasets). Build 2025 first via the `client_semiannual` (qym9-xzj6) spine. Still open before merge: GH [#37](https://github.com/danparshall/lobby_analysis/issues/37) (semiannual-vs-bimonthly double-count). Baseline note: clean green count on this machine is **1636**; 3 pre-existing `scoring` reds are tracked in GH [#38](https://github.com/danparshall/lobby_analysis/issues/38) (not NY-scoped).

---

## 2026-06-05 — Phase 1 acquisition layer implemented (TDD)

- **Convo:** [`convos/20260605_ny_phase1_acquisition.md`](convos/20260605_ny_phase1_acquisition.md)
- **What happened:** Ran the mandated full `pytest` baseline (1636 passed, 3 failed). Diagnosed the 3 failures as out-of-scope `scoring`-module data drift (`SNAPSHOT_DATE_DEFAULT="2026-04-13"` pinned, but only the `2026-05-01` CA snapshot exists in local `data/`) — captured as GH #38, left untouched per multi-committer hygiene. Then implemented Phase 1 test-first.
- **Shipped (commit `db64354`, pushed):** `io/ny/acquire.py` — `download_bulk_csv()` (streaming Socrata bulk CSV export, resume-skip, `force`, app-token, atomic `.part`-then-rename, typed `NYAcquisitionError`) + `SocrataProbeClient` (SoQL `$select/$where/$group/$limit` passthrough, `from_env` reads `SOCRATA_APP_TOKEN`). 10 TDD tests, all green; full suite collects 1655.
- **Decisions:** task-issue (not in-branch fix) for the `scoring` reds; stop at the Phase 1 checkpoint (no Phase 2 this session).
- **Next steps:** Phase 2 — grain-collapse (dollar-conservation invariant) + per-dataset column-map parsers + `materialize_ny`.

---

## 2026-06-05 — Phase 0 schema verification EXECUTED (live Open NY, 2025)

- **Result doc:** [`results/20260605_ny_schema_verification.md`](results/20260605_ny_schema_verification.md)
- **Evidence:** `tests/fixtures/ny/sample_schema_*.json` (real sample rows, 6 datasets); `results/ny_focus_breakdown_2025.json` + `results/ny_grain_2025.json` (aggregates). Probe scripts in `scripts/ny_*.py`.
- **Gating verdicts (all pass):** (a) spend transactional **YES**; (b) real bill # on `State Bill` rows **YES** (88–96% of rows; `focus_identifying_number` = `S550-A`); (c) stance **absent, confirmed**. No-allocation/no-IPF architecture **holds**.
- **Two refinements folded into the plan:** (1) bill linkage is a *typed subset* (`focus type = State Bill`), not universal — chain closes for the 88–96% majority; (2) the API is denormalized **~1,300×** (client_semiannual 2025 = 11.2M rows but only **8,613 filings**, 1,334 lobbyist firms, 4,376 clients, 8,303 distinct state bills). Consequences: **pull via bulk CSV not API pagination**, **collapse to filing grain**, **never sum comp across raw rows** (it's filing-level, replicated).
- **Decisions locked:** chain spine = `client_semiannual` (`qym9-xzj6`); `lobbyist_bimonthly` for itemized expenses + individual people; Open States is the lawmaker spine (confirmed solid for NY); skip `parties_lobbied`.
- **Decisions resolved with Dan (same day):**
  - *Per-bill dollars:* **model it, even-split** — ship `comp_per_bill = filing_compensation / n_bills_in_filing` + keep raw filing comp + `n_bills_in_filing` (mirrors WI shipping both `modeled_hours_per_sponsor` and `modeled_hours`). Dan flagged that my first framing ("let the consumer divide") was *declining* to model, the opposite of the WI pattern — corrected. Note NY discloses no per-bill weight, so the split is uniform (analogous to WI's per-*sponsor* split, not its disclosed-% per-*bill* split); NY's spend chain is less modeled than WI's.
  - *Bill-id suffix:* `S550-A` = SB 550, first amended print (web-confirmed). Base number is the bill identity; OS keys by base. **Strip suffix for the join, preserve as `bill_print_version`; measure OS match rate both ways in Phase 4.**
- **Status:** Phase 0 complete; both follow-up decisions locked into the plan; ready for Phase 1 (bulk-CSV acquisition) implementation.

---

## 2026-06-05 — Branch kickoff + plan drafted (session: agent, Dan AFK)

- **Convo:** [`convos/20260605_ny_pipeline_kickoff.md`](convos/20260605_ny_pipeline_kickoff.md)
- **Plan:** [`plans/ny_disclosure_pipeline.md`](plans/ny_disclosure_pipeline.md)
- **What happened:** Read the new `docs/reports/state_bulk_data_availability/` reports (NY = Tier-1, "strongest in the US," Open NY / Socrata, 6 datasets, ~278M records, 2019–present, transactional spend + bill-level linkage). Studied the WI pipeline (`io/wi/` scrape + `allocation/wi/` IPF + chain) as the model. Drafted a phased implementation plan.
- **Central architectural finding:** NY is structurally *simpler* than WI on two axes. (1) IO is a **Socrata API client**, not an HTML scraper — no per-detail-page crawl. (2) The **entire IPF/allocation layer is unnecessary** — the lobbyist↔bill link that WI had to *model* (because WI lobbyists file only aggregate hours) is **directly disclosed** in NY (transactional, bill-keyed). NY's chain is largely a direct join. What carries over from WI: the `releases/<state>/` TSV target shape, the Open States/Plural bill-sponsor spine for the lawmaker edge, provenance/traceability discipline, deterministic sort, conservation-invariant tests.
- **Top risk flagged:** NY's column-level schema is **not yet verified** (the report explicitly says NY/CO assessments are from portal docs, not from pulling files). Plan Phase 0 is a gating schema-verification step — pull one file from each of the 6 datasets and inspect actual columns before committing to the normalization design. Everything downstream is provisional on Phase 0.
- **Status:** Plan drafted, not yet implemented. Awaiting Dan's review.
