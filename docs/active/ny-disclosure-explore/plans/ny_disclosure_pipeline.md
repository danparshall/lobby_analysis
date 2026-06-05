# New York Lobbying-Disclosure Pull Pipeline — Implementation Plan

**Goal:** Produce, for New York, a set of normalized `releases/ny/` disclosure TSVs and an `NY_chain_<years>.tsv` that maps **principal (client) → lobbyist → bill + $**, joined to Open States/Plural on the bill number to recover the **lawmaker → bill** half — the same deliverable shape as `releases/wi/`, built from NY's Open NY (Socrata) bulk API.

**Originating conversation:** [`../convos/20260605_ny_pipeline_kickoff.md`](../convos/20260605_ny_pipeline_kickoff.md)

**Context:** The 2026-06-05 state-data-availability research (`docs/reports/state_bulk_data_availability/`) rates NY the **strongest Tier-1 state in the US**: COELIG / Open NY publishes ~278M records across 6 Socrata datasets (2019–present) with **transactional** compensation + itemized expenses and **bill-level** lobbyist→bill→client linkage. Unlike WI (which files only aggregate lobbyist hours and forced an IPF allocation step), NY discloses the lobbyist↔bill edge directly — so the NY chain is largely a *join*, not a model.

**Confidence:** Medium-high (raised after Phase 0). The *strategy* (Tier-1, bulk → chain → Open States join, **no IPF**) is confirmed against live data. Phase 0 (executed 2026-06-05, see [`../results/20260605_ny_schema_verification.md`](../results/20260605_ny_schema_verification.md)) verified all three gating claims and surfaced two refinements now folded in below: (1) bill linkage is a *typed subset* (`focus type = State Bill`, 88–96% of rows); (2) the API is denormalized ~1,300× — **pull via bulk CSV, collapse to filing grain, and never sum compensation across raw rows.** Phases 1–4 are now grounded in the real schema, not portal docs.

> **Phase 0 is DONE.** Findings: [`../results/20260605_ny_schema_verification.md`](../results/20260605_ny_schema_verification.md). The 6 dataset ids, real columns, bill-coverage %, and grain counts are all recorded there. Read it before implementing.

**Architecture:** A NY pull pipeline in two thin layers, mirroring WI's package layout but dropping the allocation layer:
- `src/lobby_analysis/io/ny/` — a Socrata client + per-dataset fetchers + parsers + a `materialize` step that emits `releases/ny/` TSVs, reusing the Popolo/OCD Pydantic models in `src/lobby_analysis/models/`.
- `src/lobby_analysis/allocation/ny/chain.py` (chain composer only — **no IPF**) — joins the `releases/ny/` linkage records to Open States/Plural bill sponsors and emits `NY_chain_<years>.tsv`.

**Branch:** `ny-disclosure-explore` (worktree at `/Users/dan/code/lobby_analysis/.worktrees/ny-disclosure-explore`, cut from `main` @ `ce9bacf`).

**Tech Stack:** Python 3.12, `uv`, `requests` (already a dep) for the Socrata API, `pandas` (already a dep) for TSV materialization, `pytest` + `ruff`. Reuse existing `src/lobby_analysis/models/` (Pydantic, Popolo/OCD). Open States bill-sponsor bulk CSV from Plural Policy (same source WI used).

---

## Why this mirrors WI but is smaller

| Concern | WI (`io/wi` + `allocation/wi`) | NY (this plan) |
|---|---|---|
| Acquire data | HTML scrape of CFIS portal: Tier-1 authorization grid + Tier-2 detail-page crawl, HTML checkpoints, bespoke parsers | **Socrata REST API** on `data.ny.gov` (+ bulk CSV fallback). No HTML, no per-page crawl. |
| Lobbyist→bill edge | **Modeled** via bipartite graph + IPF (`allocation/wi/{graph,ipf}.py`) because WI files only aggregate lobbyist hours | **Directly disclosed** (transactional, bill-keyed). **No IPF, no `graph.py`, no `modeled_hours`/confidence labels.** |
| Spend grain | aggregate download (forced the modeling) | transactional (compensation + itemized expenses) |
| Lawmaker→bill | Open States/Plural bulk CSV, join on bill # | **identical** — carries over |
| Output | `releases/wi/` 6 TSVs + `chain/WI_chain_2025.tsv` | `releases/ny/` TSVs + `chain/NY_chain_<years>.tsv` (same discipline: provenance, deterministic sort, conservation tests) |

**Net:** the genuinely hard WI work (`allocation/wi/` IPF) has no NY analogue. NY's new work is the Socrata client, cross-year entity handling, and bill-id normalization to the Open States key.

---

## Testing Plan

(Write **all** tests before any implementation behavior — TDD per repo norms. Network and disk are mocked/fixtured; no live API in the test suite.)

1. **Socrata client (unit).** Mock `requests` at the transport boundary. Test that the client (a) paginates correctly via `$limit`/`$offset` until a short page signals the end, (b) sends the app token header when configured, (c) raises a typed error (not a silent empty list) on HTTP error, (d) passes through `$where`/`$select` query params verbatim. **Test behavior** (pagination assembles the full record set; an error surfaces), never just "the mock was called."

2. **Per-dataset parsers (unit, fixture-driven).** Capture a small real sample (5–20 rows) from each NY dataset during Phase 0 as a committed JSON fixture under `tests/fixtures/ny/`. Test that each parser maps fixture rows → the Pydantic model (`entities.py` / `filings.py`) with correct field extraction, type coercion (money strings → Decimal, date strings → dates), and `contact_details_json` assembly — matching the conventions already used by `releases/wi/`. Assert on parsed *values*, including at least one row with a missing/empty optional field and one money/date edge case.

3. **`materialize` step (integration).** Feed fixtured parsed records through the materializer; assert it writes the expected `releases/ny/*.tsv` files with the agreed header rows and that round-tripping (write → re-read) preserves values. Assert the principal/lobbyist/linkage row counts match the fixture.

4. **Chain composer (integration).** With a tiny hand-built fixture of NY linkage rows (principal, lobbyist, bill #, $) + a tiny Open States legislator/bill-sponsor CSV, assert the composer emits one chain row per `(period, principal, lobbyist, bill, sponsor)` tuple, attaches the correct sponsor(s), and that a NY bill # that has **no** Open States match is handled explicitly (emitted with a null/flagged sponsor, **not** silently dropped — mirror WI's "don't silently drop" discipline).

5. **Conservation / no-loss invariant (integration).** Two assertions, given Phase 0's filing-level comp replication: (a) **filing-comp conservation** — summing `filing_compensation` over *distinct* `form_submission_id` equals the source filing total (proves we de-duplicated the ~1,300× explosion and did not overcount); (b) **even-split conservation** — `SUM(comp_per_bill)` over the bills of one filing equals that filing's `filing_compensation` exactly (proves the even-split neither loses nor fabricates dollars). This is the NY analog of WI's `modeled_hours_per_sponsor` conservation test.

6. **Bill-id normalization (unit).** Test the NY-bill-# → Open States key normalizer against real Phase-0 identifiers: `S550-A` → base `S550` (+ `bill_print_version="S550-A"` preserved), `A10003` → `A10003`, plus whitespace/case variants. Assert the function (a) strips the `-A/-B/...` amendment suffix for the join key and (b) preserves the original suffixed string as metadata. This is the linchpin of chain closure; Phase 4 additionally records the OS match rate with vs. without stripping.

NOTE: I will write *all* tests before I add any implementation behavior.

---

## Phases & bite-sized steps

### Phase 0 — Schema verification (GATING) — ✅ DONE 2026-06-05

Executed live against `data.ny.gov`. Full writeup: [`../results/20260605_ny_schema_verification.md`](../results/20260605_ny_schema_verification.md). Evidence committed under `tests/fixtures/ny/` + `../results/ny_*_2025.json`. Outcome:

- ✅ venv set up (`uv venv --python 3.12` + `uv sync --extra dev`). **NOTE: full `pytest` baseline not yet run** — implementer should run `uv run --active pytest -q` first and confirm ~1550 pass before writing code.
- ✅ 6 datasets identified (ids in the findings doc). 2019→2025 coverage confirmed.
- ✅ Real columns captured for all 6. Gating verdicts: **(a) transactional YES** (filing-period comp + itemized expenses), **(b) real bill # YES on the `State Bill` subset = 88–96% of rows** (`focus_identifying_number` = `S550-A`), **(c) stance absent CONFIRMED**.
- ✅ Decision gate PASSED — no-allocation architecture holds. Two refinements folded into Phases 1–4 below.

**Carried-forward facts the implementer must honor (from Phase 0):**
- Pull via **bulk CSV export**, not API pagination (client_semiannual 2025 alone = 11.2M rows / only 8,613 filings).
- Per-dataset **column map** required (names differ across datasets — see findings "Schema landmines").
- Collapse to **filing grain**. **CORRECTED 2026-06-05** (see [`../results/20260605_ny_amendment_double_count.md`](../results/20260605_ny_amendment_double_count.md)): "keep latest `filing_type` per `form_submission_id`" is a **no-op** — an amendment is a *separate* submission with its own `form_submission_id`. Dedup must be on the **business key** `(reporting_year, reporting_period, principal_lobbyist, beneficial_client, contractual_client_name)`, keeping `max(form_submission_id)` (verified monotonic with submission order). **Implemented in `io/ny/grain.py`.**
- **Dollar conservation:** comp is filing-level, replicated — dedup before summing. *And* drop superseded submissions first, else naive distinct-`form_submission_id` summing double-counts every superseded amendment (4.1× on the worst real key).
- Chain spine = `client_semiannual` (`qym9-xzj6`); `lobbyist_bimonthly` (`t9kf-dqbc`) supplies itemized expenses + individual-person names. Don't double-count across the two.

### Phase 1 — Acquisition (`io/ny/acquire.py`)

**Primary path = bulk CSV** (Phase 0 found the API too denormalized to paginate: 71M+ rows for 2025 across the two core datasets). The Socrata API client is kept only for cheap aggregate probes (counts, distinct-value checks), not full pulls.

- [ ] Write failing tests for a bulk-CSV downloader: streams `https://data.ny.gov/api/views/<id>/rows.csv?accessType=DOWNLOAD` to `data/raw/ny/<year>/<dataset>.csv`, resumes/skips if the file already exists and is non-empty, and surfaces HTTP errors as typed exceptions (not a silent partial file). Mock the transport.
- [ ] Write failing tests for a thin probe client (`$select`/`$group`/`$where` passthrough, app-token header from `SOCRATA_APP_TOKEN`, typed error on HTTP failure).
- [ ] Run them; confirm they fail.
- [ ] Implement both (`requests`, streaming download with a `.part` temp-then-rename so a truncated download is never mistaken for complete). Green. Commit.

### Phase 2 — Per-dataset fetch + parse + materialize (`io/ny/`)

For each of the 6 datasets, a parser reads the bulk CSV → Pydantic models via a **per-dataset column map** (names differ — see findings "Schema landmines"). A **grain-collapse** step dedups the ~1,300× row explosion to filing grain, resolving superseded amendments on the business key first (see correction above). Then one `materialize` step + CLI mirroring `io/wi/tier_2_materialize_cli.py`.

> **DONE 2026-06-05:** the grain-collapse step (`io/ny/grain.py`, `collapse_to_filing_grain`) and the column map (`io/ny/columns.py`, `normalize_columns`, 2 core datasets) are implemented + tested (13 tests). The remaining Phase 2 work below — `bill_id` derivation, the entity/filing/linkage parsers, and `materialize_ny` — is the next pickup. **`bill_id` open question:** Phase-0's `starts_with(level_of_government,'State')` filter wrongly drops a `State Bill` row filed at `Both` level (`S550-A` in the fixture); likely use `focus_type=='State Bill'` alone — resolve when building the parser.

- [x] **DONE 2026-06-05.** Grain-collapse step: collapses denormalized rows to the agreed grain `(reporting_year, reporting_period, form_submission_id, principal_lobbyist, beneficial_client, bill_id)`; the *latest submission* (max `form_submission_id` per business key) wins and superseded submissions are dropped; comp is **not** summed across the explosion *or* across superseded amendments. 9 tests in `tests/test_ny_grain.py` (incl. a NaN-business-key dollar-loss regression test found in code review).

- [ ] Write failing parser tests for the **entity** datasets (principals/clients, lobbyists) against the Phase-0 fixtures.
- [ ] Implement those parsers → `Organization`/`Person`-style models. Green. Commit.
- [ ] Write failing parser tests for the **filing/linkage** datasets (reports with compensation/expenses; the lobbyist→bill→client linkage rows). Cover money/date coercion + a missing-field row.
- [ ] Implement those parsers → filing models. Green. Commit.
- [ ] Write failing test for `materialize_ny` (fixtures → `releases/ny/*.tsv` with agreed headers, round-trip preserves values, counts match).
- [ ] Implement `materialize_ny` + a thin `io/ny/materialize_cli.py`. Green. Commit.
- [ ] Write `releases/ny/README.md` modeled on `releases/wi/README.md` (Provenance table, Files table with row counts + columns, Schema reference pointing at `models/`, Headline aggregates, Caveats). Fill aggregates after the first real run.

### Phase 3 — Real data pull + `releases/ny/`

- [ ] Run the materialize CLI against the live API for the first target year(s) (decide year scope from Phase 0 — start with one recent year, e.g. 2024 or 2025, to keep the first run small). Use checkpoint/resume discipline (write per-dataset raw JSON to `data/raw/ny/<year>/` first, materialize from disk) so a re-run is idempotent and never re-hits the API unnecessarily — per repo Experiment Data Integrity rules.
- [ ] Sanity-check headline aggregates (total compensation, total expenses, #principals, #lobbyists, #linkage rows, #distinct bills). Spot-check 1–2 large filers against the live portal, as WI did with WMC/DoorDash.
- [ ] Fill in `releases/ny/README.md` aggregates. Commit `releases/ny/` (TSVs are the deliverable; raw JSON stays in gitignored `data/`).

### Phase 4 — Chain composer (`allocation/ny/chain.py`) + Open States join

- [ ] Write the failing bill-id normalizer test (Phase-0 NY identifiers → canonical Open States key).
- [ ] Implement the normalizer. Green.
- [ ] Acquire the NY Open States/Plural bulk CSV (https://open.pluralpolicy.com/data/session-csv/) for the matching session(s); stage under `data/bills/NY/<year>/` like WI. Record `ocd-person` sponsor-id coverage.
- [ ] Write the failing chain-composer + no-loss-invariant tests (fixtures).
- [ ] Implement `materialize_chain` (no IPF): join `releases/ny/` linkage rows → Open States sponsors on the **stripped** bill key; one row per `(period, principal, lobbyist, bill, sponsor)`; emit `comp_per_bill` (even-split) + `filing_compensation` + `n_bills_in_filing` + `bill_print_version` + source `unique_id` for traceability; deterministic sort; unmatched-bill rows flagged not dropped. Green.
- [ ] Add `allocation/ny/cli.py` (a single `chain` subcommand — no `allocation` subcommand). Run it; produce `releases/ny/chain/NY_chain_<years>.tsv`.
- [ ] Write `releases/ny/chain/README.md` (schema, the Open States join methodology, **and the honest limitations**: no stance, 2019 bulk cutoff, any bills that don't resolve to Open States, "parties lobbied" handled separately if at all).
- [ ] Sanity-check: pick one high-spend principal and one high-traffic bill; confirm the chain reads sensibly end-to-end and the lawmaker side resolves via Open States.

---

**Testing Details:** Tests assert real behavior, not mocks: the Socrata client test asserts that pagination *reassembles a multi-page record set* and that errors *surface as typed exceptions*; parser tests assert *extracted values* (money/date coercion, missing-field handling) against committed real-sample fixtures; the chain test asserts *correct sponsor attachment and that unmatched bills are flagged, not dropped*; the conservation test asserts *dollars are neither lost nor duplicated* across the join. No test exercises a datastructure or a type for its own sake. Fixtures are small real API samples captured in Phase 0, so parser tests track the *actual* NY schema.

**Implementation Details:**
- Reuse `src/lobby_analysis/models/` (Popolo/OCD entities + filings) — do **not** invent a NY schema; `releases/ny/` should be shape-compatible with `releases/wi/`.
- No `allocation/ny/{graph,ipf}.py`. NY discloses lobbyist→bill directly; the chain is a join. (If Phase 0 refutes this, escalate — do not silently reintroduce IPF.)
- Socrata API: `https://data.ny.gov/resource/<dataset_id>.json`, SoQL params (`$limit`,`$offset`,`$where`,`$select`); optional `X-App-Token`. Bulk CSV download is the fallback if the API is rate-limited for a full historical pull.
- Checkpoint raw JSON to gitignored `data/raw/ny/`; materialize TSVs from disk; resume = skip datasets already on disk. Never delete raw pulls to re-run — write a new dated dir.
- The Open States/Plural bill-sponsor spine is the **same** mechanism WI used (`allocation/wi/` chain stage). Lift its join logic; only the bill-id normalizer is NY-specific.
- Deterministic sort on the chain TSV so reruns diff cleanly (WI convention).
- Decimal for money, not float.

**What could change:**
- **If Phase 0 shows spend is aggregate or linkage is subject-matter-only** (contradicting the report), NY drops from "direct join" toward the WI allocation pattern — major plan revision; stop and flag.
- **Bill-id ↔ Open States key mismatch.** If NY identifiers don't normalize cleanly to the Open States `identifier`/`bill_id`, chain closure rate drops and a resolution/fallback strategy is needed (the chain-closure report's Tier-2 "targeted query" idea, even though NY is nominally Tier-1).
- **Cosponsors.** WI shipped primaries-only and flagged cosponsors as a refinement (Plural's bulk CSV keeps cosponsors only in `bill_actions` text). Same limitation will apply to NY; scope primaries-first.
- **"Parties lobbied" dataset.** NY uniquely publishes a lawmaker-side tabulation. This plan treats the lawmaker edge as coming from Open States (consistent with the standing architectural decision); whether to *also* ingest "parties lobbied" as a direct/validating edge is an open enhancement, not v1 scope.
- **Year scope.** Plan starts with one recent year for a fast first loop; multi-year backfill to 2019 is a follow-on once the single-year pipeline is proven.

**Questions** (for Dan — none block drafting; several block *implementation*):
1. **Target year for v1?** Phase 0 confirms 2025 is the right test year (11.2M client rows, 8,613 filings, full coverage). Building 2025 first, then backfilling 2019–2024. (Dan greenlit "just 2025 is fine for testing.")
2. ~~Client vs. lobbyist anchor~~ — **RESOLVED in Phase 0.** Chain spine = `client_semiannual` (`qym9-xzj6`); `lobbyist_bimonthly` supplies itemized expenses + individual-person names. Don't double-count dollars across the two. (See findings doc.)
3. ~~"parties lobbied" in v1?~~ — **RESOLVED.** Dan: skip it, Open States is the lawmaker spine (confirmed solid for NY — live OS bill pages with real `S####`/`A####` ids). `parties_lobbied` kept as a passthrough column for optional future validation, not used in the chain.
4. **Per-bill dollar attribution — DECIDED 2026-06-05 (Dan).** We *model* it, even-split: ship `comp_per_bill = filing_compensation / n_bills_in_filing` as the headline per-bill number, AND keep `filing_compensation` + `n_bills_in_filing` for re-aggregation (mirrors WI shipping both `modeled_hours_per_sponsor` and `modeled_hours`). Flag the uniform-split assumption explicitly. **Precision:** NY discloses no per-bill effort weight, so this is uniform — analogous to WI's per-*sponsor* split, not WI's disclosed-% per-*bill* split; NY's spend chain is less modeled than WI's. (Supersedes the earlier "let the consumer divide" framing, which Dan correctly flagged as *declining* to model, not mirroring WI.)
5. **Bill-id amendment suffix — DECIDED.** `S550-A` = Senate Bill 550, first amended print (`-B` second, …); base number is the bill identity and Open States keys by the base. **Strip `-A/-B/...` for the OS join; preserve the suffixed original as a `bill_print_version` column.** Phase 4 measures OS match rate both with and without stripping. (See findings doc "Bill-id normalization" row for sources.)
6. **Single branch OK?** Everything stays on `ny-disclosure-explore` (no `allocation/ny` worktree split — there's no allocation work). WI split io vs. allocation because the IPF was substantial; NY doesn't warrant it.
