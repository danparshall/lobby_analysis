# Research Log: ny-disclosure-explore

Created: 2026-06-05
Purpose: Build a New York state lobbying-disclosure pull pipeline — `releases/ny/` normalized TSVs + an `NY_chain.tsv` (company → lobbyist → bill + $, joined to Open States for the lawmaker → bill half) — modeled on the WI pipeline but adapted to NY's Socrata/Open NY bulk API.

Newest entries first.

> **HANDOFF (next session) — Phase 3 DONE + validated; `releases/ny/` shipped; a $108.9M firm-collapse bug was found & fixed. Next = Phase 4.**
>
> Phase 3 ran on this CLI machine (the prior "blocked" handoff was the **Web agent's** proxy egress — `data.ny.gov` is reachable here). The live 2025 `client_semiannual` pull → four `releases/ny/` TSVs is committed (`05dee22`), README written from real aggregates, and **independently validated two ways** (full from-raw total recompute delta $0; Brown & Weinraub spot-check exact). NY suite **66 green**, ruff clean.
>
> **THE BIG FINDING (now a settled fact, see Caveat 1 in the release README):** `form_submission_id` is the **client's** semi-annual report id, **not a per-firm filing key** — 26% of submissions list >1 firm, each with its own comp. The grain docstring's "submission primary key" assumption was wrong. This caused a **$108.9M / 32%** dollar drop (firms colliding in the materializer's filings dict) which the mandated large-filer spot-check caught. **Fixed** (`cb59653`): filing identity is now `FILING_KEY = (year, period, submission, firm, client)` in both `grain.py` (n_bills) and `materialize.py` (filings dict + even-split + ids). **Any join of these tables MUST include `lobbyist_id`, never `filing_id` alone.**
>
> **Settled, do not re-litigate:** four-TSV shape (unchanged); even-split conservation (0 violations / 4,328 filings on real data); Decimal money end-to-end; State-Bill scoping = `focus_type` alone; dedup = `max(form_submission_id)` per business key. **New since prior handoff:** acquisition is `io/ny/acquire.download_resource_csv` (SODA `/resource/.csv`, `$select`+`$where`, field-name headers) — **NOT** `download_bulk_csv`, which dumps all 66.9M rows with display-name headers the pipeline can't consume (GH [#39](https://github.com/danparshall/lobby_analysis/issues/39)). Pull via `scripts/ny_pull_2025.py`.
>
> **Your pickup — Phase 4:** chain composer (`allocation/ny/chain.py`, no IPF) joining `NY_filing_bill_links.tsv` → Open States/Plural sponsors on the **stripped** `bill_id` base key. **Phase-4 correctness blocker:** bill-number zero-padding is inconsistent at source (`A00804-C` vs `A804` vs `A1001`) — canonicalize padding before the OS join, or the same bill forks. Measure OS match rate with vs. without the `-A/-B` suffix (`bill_print_version` preserves the suffixed form). Coverage context: State Bill = 87.7% of rows, 85.4% parse to a `bill_id`; some non-parsers embed bills in prose ("(S8417/A8888)") — an extraction opportunity.
>
> **Open follow-ups (not blockers):** coalition `beneficial_client` cells (semicolon-list → one entity; splitting is a modeling decision, no disclosed weights); `&amp;` HTML entities undecoded; `LobbyingFiling.total_compensation` `Decimal`-typing pass; whether to fold in `lobbyist_bimonthly` (expenses + individual people) and multi-year. GH [#37](https://github.com/danparshall/lobby_analysis/issues/37) (amendment dedup), [#38](https://github.com/danparshall/lobby_analysis/issues/38) (3 non-NY scoring reds — leave), [#39](https://github.com/danparshall/lobby_analysis/issues/39) (download_bulk_csv gap).

---

## 2026-06-05 — Phase 3 real 2025 pull + releases/ny + firm-collapse bug fix

- **Convo:** [`convos/20260605_ny_phase3_pull_firm_collapse_fix.md`](convos/20260605_ny_phase3_pull_firm_collapse_fix.md)
- **Results:** [`results/20260605_ny_phase3_aggregates.md`](results/20260605_ny_phase3_aggregates.md)
- **Egress was the Web agent's block, not this machine.** `curl data.ny.gov` → 200 here; Phase 3 ran on this CLI.
- **Acquisition extended (TDD, Dan's pick):** `download_resource_csv` + `resource_csv_url` (SODA `/resource/.csv`, `$select`/`$where`/`$order`/`$limit`, field-name headers) — the as-built `download_bulk_csv` dumps all 66.9M rows with display-name headers the column-map can't consume (GH #39). 7 new acquire tests. Pull = `scripts/ny_pull_2025.py` (single streamed filtered request, row-count verified vs live `count(*)` = 11,200,080).
- **MAJOR BUG found via the mandated large-filer spot-check + fixed (TDD):** `form_submission_id` is the **client's** report id shared across firms (26% of submissions list >1 firm), not a filing key. The materializer's `(submission, client)` filing key collided co-retained firms → **$108.9M / 32% comp drop**; `grain.py`'s `n_bills` by submission alone over-counted bills per firm. Fixed → filing identity `FILING_KEY = (year, period, submission, firm, client)`. 3 regression tests reproduce the real Accenture shape. NY suite 63→66 green, ruff clean.
- **Validated two independent ways:** Brown & Weinraub spot-check exact ($24,217,924, 0 dropped); full from-raw total recompute **$345,762,462, delta $0**; even-split conservation 0 violations / 4,328 bill-linked filings.
- **`releases/ny/` shipped** (`05dee22`): 4,373 clients · 1,333 firms · 10,870 filings · 47,204 bill links · 6,352 distinct bills (→5,449 base). 44% of comp on bill-linked filings. README written from real aggregates with 9 caveats.
- **Coverage probe (plan-requested):** State Bill = 87.7% of rows; 85.4% of State-Bill rows parse to a `bill_id`.
- **Next:** Phase 4 chain composer + OS join. **Blocker for Phase 4:** canonicalize bill-number zero-padding before the join (`A00804` vs `A804`).

---

## 2026-06-05 (later) — Green claim settled (56/56 NY tests); Phase 3 blocked on data.ny.gov egress

- **Convo:** [`convos/20260605_ny_green_verification_and_phase3_block.md`](convos/20260605_ny_green_verification_and_phase3_block.md)
- **Owed verification discharged (NY-scoped).** Ran the NY suite on a networked machine against freshly-installed real deps (`pydantic` 2.13.4, `pandas` 3.0.3): **56/56 NY tests pass** across all 7 NY test files (`acquire` 10, `bill_id` 8, `columns` 4, `entities` 7, `filings` 7, `grain` 9, `materialize` 11) in 0.8 s; **`ruff check` clean** on `io/ny/` + the NY tests. This upgrades the prior session's "46 green locally" claim — it now holds against real Pydantic models on a clean checkout, all 7 files collected (nothing skipped). Commit `f1098b6b27`'s `materialize_ny` + `materialize_cli` are green.
- **Method (sandbox without git):** git clone/push blocked (CONNECT rejected); worked via the GitHub REST API. Reconstructed the NY-scoped tree (7 `io/ny/` source files + `models/` + `pyproject.toml` + 7 NY test files + 2 fixtures) from the Contents API into a local venv and ran `PYTHONPATH=src pytest tests/test_ny_*.py`. The NY suite is network-mocked + fixture-driven by design, so it verifies fully offline.
- **Did NOT re-run the full ~1650-test repo suite** — it needs the whole tree and carries the 3 known non-NY `scoring` reds (GH #38). The NY modules import only `io/ny/*` + `models/{entities,filings}`, so they can't have regressed unrelated suites; the grain-collapse session already recorded full-suite green (1659 passed) at an earlier commit and nothing since touches non-NY code.
- **Phase 3 is BLOCKED in this environment, not done.** The data source `data.ny.gov` is **off this sandbox's bash egress allowlist** — the proxy returns `HTTP 403 / x-deny-reason: host_not_allowed` on the `qym9-xzj6` bulk-CSV URL (a proxy host-deny, not a server 403). The 2025 `client_semiannual` bulk CSV (11.2M rows) is unreachable from here, so the real pull could not run.
- **`releases/ny/README.md` deliberately NOT written.** With no real pull there are no real aggregates, and the plan forbids a placeholder aggregates section. Writing it now would mean inventing numbers — stopped instead.
- **Unblock paths:** an org owner can add `data.ny.gov` to the egress allowlist for a future agent session; short of that, run Phase 3 from a networked machine that can reach it (the OH branch handled the analogous block by handing the live run to a US-based collaborator).
- **No code changed this session** — verify-and-checkpoint only.
- **Next steps (unchanged):** Phase 3 real pull (`acquire.download_bulk_csv` `qym9-xzj6` 2025 → `materialize_cli` → sanity-check aggregates + spot-check large filers), **then** `releases/ny/README.md` from the real run, then Phase 4 chain composer + Open States join.

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
