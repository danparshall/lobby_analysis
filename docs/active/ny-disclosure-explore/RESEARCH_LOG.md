# Research Log: ny-disclosure-explore

Created: 2026-06-05
Purpose: Build a New York state lobbying-disclosure pull pipeline — `releases/ny/` normalized TSVs + an `NY_chain.tsv` (company → lobbyist → bill + $, joined to Open States for the lawmaker → bill half) — modeled on the WI pipeline but adapted to NY's Socrata/Open NY bulk API.

Newest entries first.

> **HANDOFF (next session) — Phase 2 is code-complete; next is the real Phase-3 pull, then `releases/ny/README.md`.**
>
> `materialize_ny` + `io/ny/materialize_cli.py` shipped (commit `f1098b6b27`, 11 new tests, NY-scoped suite 46 green locally, ruff clean). The full Phase-2 pipeline (`normalize_columns → add_bill_id_column → collapse_to_filing_grain → materialize_ny`) now runs end-to-end and writes the four `releases/ny/` TSVs. **Settled, do not re-litigate:**
>
> 1. **The four-TSV output shape is locked:** `NY_clients.tsv` + `NY_lobbyists.tsv` (Popolo `Organization`s, `NY-{role}-{slug}` ids, deduped) + `NY_filings.tsv` (one row per (submission, client) at filing grain, comp carried once) + `NY_filing_bill_links.tsv` (one row per (filing, real bill): even-split `comp_per_bill` + `filing_compensation` + `n_bills_in_filing` + `bill_print_version`). Shape-compatible with `releases/wi/`. A filing with no real bills is in `NY_filings` (dollars preserved) but contributes zero bill-link rows. (Design choice flagged to Dan: filing split into two tables rather than one denormalized table — reversible if the consumer wants otherwise.)
> 2. **Even-split conservation holds exactly**, including odd division (integer-cent arithmetic: `100/3 → 33.34 + 33.33 + 33.33 = 100.00`). NY analog of WI's `modeled_hours_per_sponsor` conservation invariant.
> 3. **Money stays Decimal end-to-end.** The materializer writes the Decimal straight from the grain, bypassing `LobbyingFiling.total_compensation` (which is typed `float` and would silently coerce). So the TSVs are exact; the model's float field can disagree at the last digit. A `Decimal`-typing pass on the filings model is a candidate follow-up, out of scope here.
>
> **Your pickup, in order:** (a) **Phase 3 real pull** — acquire the `client_semiannual` (`qym9-xzj6`) 2025 bulk CSV via `io/ny/acquire.download_bulk_csv` into `data/raw/ny/2025/`, then `uv run python -m lobby_analysis.io.ny.materialize_cli --input data/raw/ny/2025/client_semiannual.csv --dataset client_semiannual --output-dir releases/ny`; sanity-check headline aggregates + spot-check 1–2 large filers against the live portal (as WI did with DoorDash/WMC). (b) **Then `releases/ny/README.md`** modeled on `releases/wi/README.md` — fill the aggregates from the real run (deliberately deferred until now so it isn't a placeholder). (c) **Then Phase 4** (chain composer + Open States join). At Phase-3 start, also run the low-risk live parse-rate probe on `Both`-level State-Bill rows (coverage check, not a correctness blocker — `derive_bill_id` degrades malformed ids to "not chain-eligible", so it cannot corrupt the chain).
>
> **OWED VERIFICATION (important):** this session's code was written test-first and verified GREEN *locally* against the real Pydantic models + the Phase-0 fixture, but the full repo `pytest`/`ruff` was **not** run (git push blocked in the agent env; worked via the GitHub REST API). Before trusting the green claim, a networked machine should run `uv run pytest tests/test_ny_materialize.py` and the full suite.
>
> **Carry-forward facts (unchanged, still true):** dedup is `max(form_submission_id)` per business key `(reporting_year, reporting_period, principal_lobbyist, beneficial_client, contractual_client_name)` — in `grain.py`; GH [#37](https://github.com/danparshall/lobby_analysis/issues/37). Money is Decimal; `"$"`/`""`/None → None not 0 (`coerce_money`). 3 pre-existing `scoring` reds (GH [#38](https://github.com/danparshall/lobby_analysis/issues/38)) are NOT NY-scoped — leave them; clean NY-scoped baseline is 46 NY tests green. **Process note for committing (confirmed working again this session):** build GitHub Git-Data-API commit payloads in Python (create blobs → tree on `base_tree` → commit → PATCH the ref with `force: false`) and read file content from disk, not through shell string interpolation (it mangles newlines / breaks on dash). A reusable multi-file-commit recipe is still a pending addition to the project instructions (agreed with Dan; not yet written).

---

## 2026-06-05 — Phase 2 materialize: materialize_ny + materialize_cli (TDD)

- **Convo:** [`convos/20260605_ny_phase2_materialize.md`](convos/20260605_ny_phase2_materialize.md)
- **Shipped (TDD, green; commit `f1098b6b27`):** `io/ny/materialize.py` — `materialize_ny(grain, output_dir)` projects the collapsed filing grain into **four** `releases/ny/` TSVs (shape-compatible with `releases/wi/`): `NY_clients.tsv` + `NY_lobbyists.tsv` (Popolo `Organization`s, `NY-{role}-{slug}` ids, deduped by id, `contact_details_json` column), `NY_filings.tsv` (one row per (submission, client) at filing grain, comp carried once, `filer_role='firm'`, `filing_type='expenditure_report'`), `NY_filing_bill_links.tsv` (one row per (filing, real bill): even-split `comp_per_bill` + `filing_compensation` + `n_bills_in_filing` + `bill_print_version`). Plus `io/ny/materialize_cli.py` — thin CLI wiring the full Phase-2 pipeline over a raw Open NY bulk CSV (`read_csv(dtype=str) → normalize_columns → add_bill_id_column → collapse_to_filing_grain → materialize_ny`), mirroring `io/wi/tier_2_materialize_cli.py` (adapted: NY reads raw CSV, WI reads pre-parsed checkpoints).
- **Conventions mirrored from WI's materializer:** `csv.DictWriter` with `\t` delimiter + `\n` lineterminator (byte-identical re-runs), `None → ""` empty cell, compact deterministic JSON columns, deterministic sort, `materialize_*` returns a per-file row-count dict.
- **Even-split conservation holds exactly under odd division** — integer-cent arithmetic distributes the remainder so `SUM(comp_per_bill) == filing_compensation` (verified `100/3 → 33.34 + 33.33 + 33.33 = 100.00`). NY analog of WI's `modeled_hours_per_sponsor` conservation invariant.
- **Money stays Decimal end-to-end:** the materializer writes the Decimal straight from the grain via `coerce_money`, **bypassing** `LobbyingFiling.total_compensation` (typed `float`, would silently coerce). TSVs are exact; the model's float field can disagree at the last digit. `Decimal`-typing pass on the filings model is a candidate follow-up, out of scope.
- **A filing with no real bills** (`n_bills_in_filing = 0`) appears in `NY_filings.tsv` (dollars preserved) but contributes **zero** bill-link rows — not chain-eligible, not lost.
- **Tests:** 11 new in `tests/test_ny_materialize.py` (4-TSV write + count match; entity dedup; one filing row per (submission, client); filing-comp conservation summed over distinct filings; even-split conservation; print-version preservation; no-bill → no-link; absent-comp → empty cell not 0; entity round-trip; byte-identical rerun; empty-grain → header-only). RED confirmed (`ModuleNotFoundError` on the absent module) before implementing. NY-scoped suite 35 → **46 green locally**; `ruff check` + `ruff format` clean on all 3 files.
- **Verification caveat:** full repo `pytest`/`ruff` **not** run this session — git push is blocked in the agent env, so work went via the GitHub REST API and tests were verified GREEN locally against the real Pydantic models + the Phase-0 fixture (and the CLI end-to-end against a CSV built from the fixture rows). A networked `uv run pytest` run is owed before fully trusting green.
- **Design choice flagged to Dan (not silently assumed):** filing output split into two TSVs (filing grain + per-bill links) rather than one denormalized table — mirrors WI shipping both the aggregate and the split; reversible.
- **Next steps:** Phase 3 real pull (acquire `client_semiannual` 2025 bulk CSV → run the CLI → sanity-check aggregates + spot-check large filers), **then** `releases/ny/README.md` (deferred until after the real run so aggregates aren't placeholders), then Phase 4 chain composer + Open States join.

---

## 2026-06-05 — Phase 2 parser step: bill_id derivation + entity/filing parsers (TDD)

- **Convo:** [`convos/20260605_ny_phase2_parser_step.md`](convos/20260605_ny_phase2_parser_step.md)
- **Decision (load-bearing): State-Bill scoping = `focus_type == 'State Bill'` alone**, not `focus_type AND level starts-with 'State'`. Resolved against data, not reasoning: fixture `S550-A` is a real state bill at `level = 'Both (State and Municipal)'`; the `level` clause drops **2.45M of 9.82M** State-Bill rows (25%) for 2025 (`results/ny_focus_breakdown_2025.json` vs `ny_grain_2025.json`). `level` is the engagement's jurisdictional scope, not the bill's identity; `Municipal Bill` is a distinct `focus_type`, excluded without consulting `level`.
- **Shipped (TDD, green; commit `59b9d546`):** `io/ny/parse.py` — `derive_bill_id` / `add_bill_id_column` (canonical bill_id, suffix preserved, takes no `level` arg by design); `parse_principal_lobbyist` / `parse_client` / `parse_individual_lobbyists` (name-keyed Popolo `Organization`/`Person`, `NY-{role}-{slug}` ids, trailing-`;` + semicolon-list cleaning + dedupe); `coerce_money` (`$`/`,` strip → Decimal; `"$"`/`""`/None → None not 0; explicit `0` preserved); `parse_filing` (grain row → `LobbyingFiling`, firm filer, `filer_role='firm'`, `filing_type='expenditure_report'` per WI's spend-report convention). 22 tests across `test_ny_bill_id.py` (8) / `test_ny_entities.py` (7) / `test_ny_filings.py` (7).
- **REFACTOR correction (own RED→GREEN):** `filing_type` `activity_report` → `expenditure_report` to match WI (spend report = expenditure_report).
- **Integration verified:** `normalize_columns → add_bill_id_column → collapse_to_filing_grain` composes on the real fixture; `S550-A` `Both`-level row survives with a real `bill_id` (the row the old filter dropped). `add_bill_id_column` emits an object-dtype `bill_id` column so null bill rows are preserved (not coerced) for grain's `.notna()` / `.nunique()`.
- **Suite:** NY-scoped tests 23 → **45 green**; ruff clean on new files. (Full `pytest` not re-run from the sandbox extract; the 3 `scoring` reds are pre-existing + non-NY, GH #38.)
- **Process:** first two commit attempts had a bad message (`read -d` bashism under dash → empty; then shell interpolation collapsed JSON newlines). Fixed via Python-built payload POSTed from file. Bad commits orphaned. Discussed codifying — agreed a Git-Data-API multi-file-commit recipe belongs in the project instructions; not yet written.
- **Next steps:** `materialize_ny` + `io/ny/materialize_cli.py` (remaining Phase 2), then `releases/ny/README.md`, then Phase 3 real pull. At Phase-3 start, run the live parse-rate probe on the `Both`-level State-Bill subset (low-risk coverage check, not a correctness blocker).

---

## 2026-06-05 — Phase 2 grain-collapse + column map (TDD); amendment double-count finding

- **Convo:** [`convos/20260605_ny_phase2_grain_collapse.md`](convos/20260605_ny_phase2_grain_collapse.md)
- **Finding (load-bearing):** verified the plan's amendment-dedup rule against live data before building the guard. *"Keep latest `filing_type` per `form_submission_id`"* is a **no-op** (no `form_submission_id` carries both Original and Amendment) and the underlying model is wrong: an amendment is a **separate submission with its own id** superseding the prior one. Naive distinct-`form_submission_id` comp summing double-counts every superseded version — **4.1× overcount** on `RIDDETT ASSOCIATES`/`TRIAL LAWYERS ASSN` (4 submissions, final comp $255,536 booked as $1,050,542). The plan's conservation test #5a wouldn't have caught it. Evidence: [`results/20260605_ny_amendment_double_count.md`](results/20260605_ny_amendment_double_count.md) + raw probe JSON in `results/`. Logged on GH #37.
- **Verified rule:** `form_submission_id` is monotonic with submission order (amendment ids strictly exceed their original's; checked on 5 worst-case keys), so dedup = keep `max(form_submission_id)` per business key `(reporting_year, reporting_period, principal_lobbyist, beneficial_client, contractual_client_name)`, dropping superseded submissions before grain collapse.
- **Shipped (TDD, green):** `io/ny/grain.py` (`collapse_to_filing_grain` — supersede resolution + explosion collapse to `(year, period, form_submission_id, principal_lobbyist, beneficial_client, bill_id)` grain + `n_bills_in_filing`, comp carried-not-summed) with 9 tests; `io/ny/columns.py` (`normalize_columns` — raw→canonical per-dataset rename, 2 core datasets) with 4 tests. Probe scripts `scripts/ny_probe_amendments.py`, `scripts/ny_probe_amendment_ordering.py`.
- **Code review caught a real bug:** NaN in any business-key column made pandas `groupby` drop the group → `transform("max")` NaN → the filing's rows silently dropped (dollar loss). Fixed with `dropna=False` + regression test.
- **Suite:** full `pytest` = 1659 passed, 3 skipped, 3 xfailed; only the 3 pre-existing #38 `scoring` reds fail (not NY-scoped, untouched).
- **Next steps:** parser step — derive `bill_id` (resolve State-Bill/level scoping), parse entity + filing/linkage datasets to Pydantic, then `materialize_ny` + CLI.

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
