# Research Log: ny-disclosure-explore

Created: 2026-06-05
Purpose: Build a New York state lobbying-disclosure pull pipeline — `releases/ny/` normalized TSVs + an `NY_chain.tsv` (company → lobbyist → bill + $, joined to Open States for the lawmaker → bill half) — modeled on the WI pipeline but adapted to NY's Socrata/Open NY bulk API.

Newest entries first.

> **HANDOFF (next session) — start at `materialize_ny`; the parser step is done.**
>
> The parser step shipped and is committed on the branch (`io/ny/parse.py`, commit `59b9d546`, 22 new tests, NY suite 23→45 green, ruff clean). The two things a handoff usually invites re-checking are **already settled — do not re-litigate them, just build on them:**
>
> 1. **State-Bill scoping: RESOLVED to `focus_type == 'State Bill'` alone (no `level_of_government` filter).** This was the open question in the prior handoff; it is now decided *and verified against data*, not just reasoned. The fixture row `S550-A` is a genuine state bill at `level = 'Both (State and Municipal)'`, and the old `level` clause drops 2.45M of 9.82M State-Bill rows (25%) for 2025. `derive_bill_id` takes no `level` argument, so `level` structurally cannot affect bill identity. Treat this as locked.
> 2. **The grain/columns/parse layers compose.** Verified end-to-end on the real fixture: `normalize_columns → add_bill_id_column → collapse_to_filing_grain` runs clean and the `S550-A` `Both`-level row survives with a real `bill_id`. The pipeline up to filing grain works; you are extending it, not auditing it.
>
> **Your pickup = the remaining Phase 2 work in [`plans/ny_disclosure_pipeline.md`](plans/ny_disclosure_pipeline.md): `materialize_ny` + a thin `io/ny/materialize_cli.py`** (mirror `io/wi/tier_2_materialize_cli.py` and the `releases/wi/` TSV shapes). Then `releases/ny/README.md`, then Phase 3 (real pull). Build 2025 first via `client_semiannual` (`qym9-xzj6`); `lobbyist_bimonthly` (`t9kf-dqbc`) supplies itemized expenses + individual people. TDD per repo norms (read `skills/test-driven-development` and `skills/using-skills` first).
>
> **One genuinely-open verification (low-risk, do at Phase 3 start, not before `materialize_ny`):** confirm `State Bill` rows at `Both` level carry well-formed bill ids (`S###`/`A###`±suffix), not free text. `derive_bill_id` already yields `None` for non-bill text, so malformed ids degrade to "not chain-eligible" and **cannot corrupt the chain** — this is a coverage-quality check, not a correctness blocker. Needs a live `data.ny.gov` aggregate probe (the sandboxed agent env can't reach it; a networked machine can). Don't let it gate the materialize work.
>
> **Carry-forward facts (unchanged, still true):** dedup is `max(form_submission_id)` per business key `(reporting_year, reporting_period, principal_lobbyist, beneficial_client, contractual_client_name)` — implemented in `grain.py`; GH [#37](https://github.com/danparshall/lobby_analysis/issues/37). Money is Decimal; `"$"`/`""`/None → None not 0 (`coerce_money`). 3 pre-existing `scoring` reds (GH [#38](https://github.com/danparshall/lobby_analysis/issues/38)) are NOT NY-scoped — leave them; clean NY-scoped baseline is the 45 NY tests green. **Process note for committing:** build GitHub Git-Data-API commit payloads in Python and POST from a file (`curl -d @payload.json`); do not route multi-line commit messages or file content through shell string interpolation (it mangles newlines / breaks on dash). A reusable multi-file-commit recipe is a pending addition to the project instructions (agreed with Dan; not yet written).

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
