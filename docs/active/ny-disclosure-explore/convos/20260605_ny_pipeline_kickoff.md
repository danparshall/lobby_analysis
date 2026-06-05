# Convo: NY pipeline kickoff — scope, WI comparison, plan provenance

**Date:** 2026-06-05
**Branch:** `ny-disclosure-explore` (new worktree, cut from `main` @ `ce9bacf`)
**Participants:** Dan (AFK — "draft a plan, try not to prompt me"), agent
**Produced:** [`plans/ny_disclosure_pipeline.md`](../plans/ny_disclosure_pipeline.md)

---

## The ask

Dan pointed at the freshly-merged data-availability research in
`docs/reports/state_bulk_data_availability/` and asked for a plan to build a **NY
pipeline, similar to what we did for WI**. He was AFK and asked not to be prompted, so this
session makes reasonable design decisions and records open questions in the plan rather than
blocking on them.

## What "what we did for WI" means (disambiguation)

There are two WI workstreams in the repo and they are easy to confuse:

1. **The WI data pipeline** — `src/lobby_analysis/io/wi/` (scrape the CFIS "Eye on Lobbying"
   portal) + `src/lobby_analysis/allocation/wi/` (IPF allocation + chain assembly) →
   `releases/wi/` (6 TSVs) + `releases/wi/chain/WI_chain_2025.tsv` (115,229 rows). This is the
   "pull track" the README describes. **This is what the ask refers to.**
2. **`wi-tier1-direct-read`** — the *statute-extraction harness* (Prong 1, legal-axis Tier-0/1/2,
   reading WI ch. 13 statute text with LLMs). The "Tier-1" there is a harness tier, **not** the
   chain-closure Tier-1. This is *not* what we're modeling.

The plan models workstream (1).

## Key reports read

- `SUMMARY.md` / `lobbying-chain-closure.md` — the strategic frame: the influence chain is
  `company → lobbyist → bill + $` (from disclosure data) joined to `lawmaker → bill` (from
  **Open States / Plural**, all 50 states) **on the bill number**. Bill-number granularity is the
  linchpin. NY is **Tier 1** (chain closes from bulk alone) and rated "strongest in the US."
- `research-01-official-50state-sources.md` §New York — COELIG / Open NY (Socrata), Legislative
  Law Art. 1-A, ~278M records, **6 datasets, 2019–present**, data dictionaries, queryable +
  downloadable + API. Per-category: principals/lobbyists/bills/activity+expenditure/linkage all
  `open-data`; spend is **transactional** (compensation + itemized expenses); linkage is
  **transactional** (lobbyist→bill→client, real bill IDs); **stance = none-collected** (same as
  WI); uniquely also publishes a "parties lobbied" tabulation (a partial lawmaker edge in-corpus).

## Central architectural finding — NY is simpler than WI

WI needed two heavy layers that NY does **not**:

| Layer | WI | NY |
|---|---|---|
| IO | HTML scrape of CFIS portal (directory + search-only, no API); Tier-1 grid + Tier-2 detail pages | **Socrata API** (`data.ny.gov`) + bulk CSV; no scraping |
| Spend→bill allocation | **IPF / max-entropy** — WI lobbyists file only *aggregate* hours, so lobbyist↔bill must be *modeled* (bipartite graph → IPF → `modeled_hours` with confidence labels) | **Not needed** — NY discloses lobbyist→bill→client linkage *transactionally* with dollars. Direct join. |
| Lawmaker→bill | Open States / Plural bulk CSV, joined on bill # | **Same spine** (carries over unchanged) |

So the hard, novel modeling WI required (the entire `allocation/wi/` IPF machinery) collapses to
data-cleaning + schema-mapping + a join in NY. The new work is the Socrata client, entity
resolution across years, and bill-id normalization to the Open States key.

## Decisions made (AFK, recorded for review)

- **Branch/worktree:** `ny-disclosure-explore`, matching the `mi-/nc-disclosure-explore`
  convention. Created with `data/` symlink per repo policy.
- **No `allocation/ny/`.** Unless Phase 0 reveals NY spend is coarser than the report claims, NY
  needs no allocation module. The chain composer reads `releases/ny/` directly.
- **Reuse the existing Pydantic models** (`src/lobby_analysis/models/` — Popolo/OCD entities +
  filings) rather than inventing a NY schema, so `releases/ny/` is shape-compatible with
  `releases/wi/`.
- **Output target:** `releases/ny/` TSVs + `releases/ny/chain/NY_chain_<years>.tsv`, mirroring WI.

## Top risk

NY's column-level schema is **unverified** — the report says so explicitly ("high-confidence from
portal documentation … not column-level confirmed by pulling files"). The plan makes Phase 0 a
**gating** schema-verification step (pull one file per dataset, inspect columns, write a schema
note) before any normalization code. Everything downstream is provisional on Phase 0 findings.

## Open questions carried into the plan

- Exact Socrata dataset IDs for the 6 NY datasets (plan instructs discovery, does not hardcode).
- NY bill-id format vs. the Open States `bill_id` / `identifier` key — the join hinges on this.
- Reporting cadence (bi-monthly lobbyist reports vs. semi-annual client reports) and how periods
  map to the WI-style `reporting_period_start/end` fields.
- 2019 bulk-data cutoff — confirm and decide first target year(s).
- Whether NY filings need an entity-resolution pass (same principal across years/filings).

---

## Update — Phase 0 executed same session (Dan: "try the schema-verification now, just 2025")

Ran the gating Phase 0 live against `data.ny.gov` (scripts `scripts/ny_*.py`; venv set up). Full writeup: [`../results/20260605_ny_schema_verification.md`](../results/20260605_ny_schema_verification.md). Evidence committed under `tests/fixtures/ny/` (sample rows) + `../results/ny_*_2025.json` (aggregates).

**Gating verdicts — all pass:** (a) spend transactional **YES** (per filing-period comp + itemized expenses); (b) real bill # **YES on the `State Bill` focus subset = 87.7% of client rows / 96.3% of lobbyist rows** (`focus_identifying_number` = `S550-A`); (c) stance **absent, confirmed**. No-IPF/no-allocation architecture **holds**.

**Two refinements not anticipated in the kickoff plan:**
1. **Bill linkage is a typed subset** (`focus type = State Bill`), not universal — chain closes for the 88–96% majority; other focus rows are subject/funding free text.
2. **The API is denormalized ~1,300×.** Client semi-annual 2025 = 11.2M rows but only **8,613 distinct filings** (1,334 lobbyist firms, 4,376 clients, 8,303 distinct state bills). Compensation is filing-level, *replicated across rows*. ⇒ pull via **bulk CSV** (not API pagination), **collapse to filing grain**, **never sum comp across raw rows**.

**Decisions locked (Dan):** chain spine = `client_semiannual` (`qym9-xzj6`); `lobbyist_bimonthly` (`t9kf-dqbc`) for itemized expenses + individual people; Open States is the lawmaker spine (web-confirmed solid for NY); skip `parties_lobbied` (kept as passthrough column only).

## Update — two follow-up decisions (a1/a2)

- **a1 — per-bill dollar attribution.** Dan challenged my framing: "carry filing comp + n_bills, let the consumer divide" is *declining* to model, the opposite of WI's `modeled_hours_per_sponsor` (which committed to a uniform allocation and shipped it). **Corrected: model it, even-split** — ship `comp_per_bill = filing_compensation / n_bills_in_filing` AND keep `filing_compensation` + `n_bills_in_filing` for re-aggregation. Precision: NY discloses no per-bill weight, so the split is uniform — analogous to WI's per-*sponsor* split, not its disclosed-% per-*bill* split; NY's spend chain is *less* modeled than WI's.
- **a2 — bill-id suffix.** Web-confirmed: `S550-A` = Senate Bill 550, first amended print (`-B` second, …); base number is the bill identity, Open States keys by base. **Strip `-A/-B` for the OS join, preserve original as `bill_print_version`, measure OS match rate both ways in Phase 4.** Sources cited in the findings doc.

**Session outcome:** Phase 0 closed; plan + RESEARCH_LOG updated with both refinements and both decisions; ready for Phase 1 (bulk-CSV acquisition) whenever Dan greenlights the build. Commits: `2a6d32b` (kickoff plan), `b11f15b` (Phase 0), `74c3c21` (a1/a2 decisions).

## Captured Tasks

- [#37: NY: verify no dollar double-count across client_semiannual + lobbyist_bimonthly](https://github.com/danparshall/lobby_analysis/issues/37) — captured 2026-06-05
