# New York Lobbying-Disclosure Pull Pipeline — Implementation Plan

**Goal:** Produce, for New York, a set of normalized `releases/ny/` disclosure TSVs and an `NY_chain_<years>.tsv` that maps **principal (client) → lobbyist → bill + $**, joined to Open States/Plural on the bill number to recover the **lawmaker → bill** half — the same deliverable shape as `releases/wi/`, built from NY's Open NY (Socrata) bulk API.

**Originating conversation:** [`../convos/20260605_ny_pipeline_kickoff.md`](../convos/20260605_ny_pipeline_kickoff.md)

**Context:** The 2026-06-05 state-data-availability research (`docs/reports/state_bulk_data_availability/`) rates NY the **strongest Tier-1 state in the US**: COELIG / Open NY publishes ~278M records across 6 Socrata datasets (2019–present) with **transactional** compensation + itemized expenses and **bill-level** lobbyist→bill→client linkage. Unlike WI (which files only aggregate lobbyist hours and forced an IPF allocation step), NY discloses the lobbyist↔bill edge directly — so the NY chain is largely a *join*, not a model.

**Confidence:** Medium. The *strategy* (Tier-1, bulk → chain → Open States join) is high-confidence and matches the proven WI pattern. The *column-level schema* is **unverified** — the report is explicit that NY's assessment comes from portal documentation, not from pulling files. **Phase 0 is a gating verification step; Phases 1–4 are provisional on its findings.**

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

5. **Conservation / no-loss invariant (integration).** Assert that total disclosed dollars in the source linkage rows equal the sum of dollars across chain rows grouped back to their source `item_id`/record id (NY needs no per-sponsor *re-division* of dollars unless Phase 0 shows a one-bill-many-sponsor money-duplication risk — if it does, add a `*_per_sponsor` column and test its conservation exactly as WI did with `modeled_hours_per_sponsor`).

6. **Bill-id normalization (unit).** Test the NY-bill-# → Open States key normalizer against a table of real NY identifiers captured in Phase 0 (e.g. `A1749`, `S1234`, pref/suffix and whitespace variants) → expected canonical key. This function is the linchpin of chain closure; it gets its own focused test.

NOTE: I will write *all* tests before I add any implementation behavior.

---

## Phases & bite-sized steps

### Phase 0 — Schema verification (GATING; pure investigation, no TDD)

The whole plan rests on the untested assumption that NY's columns are what the report infers. Resolve this first.

- [ ] Set up the worktree venv: from the worktree root, `uv venv --python 3.12` then `uv sync --extra dev` (the `dev` extra installs pytest + ruff; plain `uv sync` does not — see MEMORY note about worktree venv resolution).
- [ ] Baseline the suite: `uv run pytest -q`. Record pass count (expect ~1550 passed per the WI handoff). If anything fails on a clean checkout, report before proceeding.
- [ ] Find the **6 NY lobbying datasets** on `data.ny.gov` (COELIG / "Commission on Ethics and Lobbying in Government"; formerly JCOPE). Record each dataset's Socrata 4x4 ID, title, row count, and update cadence. Likely set (verify, do not assume): bi-monthly lobbyist reports, semi-annual client reports, registrations, a client/principal directory, a lobbyist directory, and the "parties lobbied" tabulation. **Save each dataset's data dictionary.**
- [ ] Pull **one small sample** (`$limit=20`) from each dataset via the API. Inspect actual columns. For each dataset write down: the principal/client key, lobbyist key, **bill-number field** (exact name + example values), dollar fields (compensation vs. expenses, and their grain), reporting-period fields, and any linkage join keys.
- [ ] Commit the samples as test fixtures under `tests/fixtures/ny/` and write `results/20260605_ny_schema_verification.md` documenting the real schema, mapping each NY field → the target `releases/ny/` column and → the Pydantic model field. **Explicitly confirm or refute:** (a) spend is transactional, (b) a real bill number is present on linkage rows, (c) stance is absent.
- [ ] **Decision gate:** if any of (a)/(b)/(c) is false — especially if spend turns out aggregate or bill linkage is subject-matter-only — STOP and flag to Dan; the no-allocation architecture may not hold and the plan needs revision.

### Phase 1 — Socrata client (`io/ny/socrata_client.py`)

- [ ] Write the failing client tests (pagination, app-token header, error surfacing, query passthrough).
- [ ] Run them; confirm they fail.
- [ ] Implement the minimal `requests`-based client: a `fetch_all(dataset_id, where=None, select=None)` generator/list with `$limit`/`$offset` pagination and optional `X-App-Token` from env (`SOCRATA_APP_TOKEN` in `.env.local`; the API works tokenless but rate-limits harder). No app-specific parsing here.
- [ ] Run tests; confirm green. Commit.

### Phase 2 — Per-dataset fetch + parse + materialize (`io/ny/`)

For each of the 6 datasets, a fetcher (thin wrapper over the client with the dataset id + any `$where` for the target year) and a parser (rows → Pydantic models). Then one `materialize` step + CLI mirroring `io/wi/tier_2_materialize_cli.py`.

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
- [ ] Implement `materialize_chain` (no IPF): join `releases/ny/` linkage rows → Open States sponsors on the normalized bill key; one row per `(period, principal, lobbyist, bill, sponsor)`; carry source record id for traceability; deterministic sort; unmatched-bill rows flagged not dropped. Green.
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
1. **Target year(s) for v1?** Recommend one recent full year (2024 or 2025) first, then backfill to 2019. OK?
2. **Client vs. lobbyist as the "principal" anchor.** NY's filer model differs from WI's (NY has lobbyist bi-monthly reports *and* client semi-annual reports). Which is the canonical spend source for the chain — or do we reconcile both? (Phase 0 will surface the overlap; flagging now because it affects the dollar-conservation invariant.)
3. **Do we want the "parties lobbied" edge ingested in v1**, or is Open States the sole lawmaker source for now (matching the WI architecture)?
4. **Single branch OK?** This plan keeps everything on `ny-disclosure-explore` (no separate allocation branch, since there's no allocation work). WI split io vs. allocation across two branches because the allocation was substantial; NY doesn't warrant the split.
