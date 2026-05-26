# WI Principal-Side Scrape — Implementation Session

**Date:** 2026-05-26
**Branch:** wi-disclosure-explore
**Previous convo:** [`20260526_wi_principal_side_scrape_plan.md`](20260526_wi_principal_side_scrape_plan.md)
**Plan executed:** [`plans/wi_principal_side_scrape.md`](../plans/wi_principal_side_scrape.md)

## Summary

This session executed the principal-side scrape plan that was written this morning. The deliverable: a polite, resumable scraper that walks the 944-principal universe on `lobbying.wi.gov`, extracts each principal's "Authorized Lobbyists" table, and produces both the principal-side authorization table AND a **unified** table with provenance (`discovered_via ∈ {lobbyist, principal, both}` + `lobbyist_in_grid` flag) — the deliverable that bounds the Schlaak-class lobbyist population, the load-bearing question of the whole branch.

The session opened with Dan answering the four footer questions of the plan: **refactor** the fetcher (DRY), **proceed now** (don't wait on the email), **three TSVs** (lobbyist-side, principal-side, unified), and **yes** to grabbing the SAL table during the pre-flight portal trip. Pre-flight then ran cleanly: the Wisconsin Hospital Association principal page (largest known active principal, 15 lobbyists) bounds the upper end of page-size distribution at ~340 KB (2.15× the gap-investigation max of 157 KB, but still puts the full scrape at ~320 MB / ~17 min — comfortably under the original convo's "500 MB / 5 hr" framing). The SAL fetch surfaced a small correction: the actual export endpoint is `/Who/StateAgencies/2025REG/ExcelExport`, NOT `/ReportExport?outRpt=Excel` from the prior session.

After pre-flight, the architectural work was a clean TDD pass: write tests RED, watch them fail, write minimal code GREEN, commit. Each step had one commit. Seven commits total before the full scrape kicked off.

The full scrape ran in the background while the convo doc and results doc were being drafted in parallel.

## Topics Explored

- Pre-flight size sample (WHA + Auto/Truck Dealers principals) to bound the upper end of the page-size distribution before kicking off the full scrape
- Correction of the prior session's SAL endpoint: `/Who/StateAgencies/2025REG/ExcelExport`, not `/ReportExport?outRpt=Excel`. The SAL "directory" is much richer than implied: 2,599 per-liaison rows × 13 columns (not ~20 per-agency)
- Fetcher refactor: extract a generic `entity_fetcher.fetch_entity_page` / `fetch_or_load_entity` core from `authorization_fetcher.py`, parameterized by URL template + ID kwarg name. Lobbyist fetcher becomes a thin wrapper; existing 8 fetcher tests act as the regression suite. New `principal_fetcher.py` is a sibling wrapper.
- Parser symmetry: principal `<h3>Authorized Lobbyists</h3>` section is structurally identical to the lobbyist-side `<h3>Principals Represented</h3>` section — same 4-column layout, same date format, same N/A semantics. `principal_parser.py` reuses `Authorization` + `ParseError` from the lobbyist parser.
- Privacy-redacted principal handling: principal 11530 has the page title and principal-info section suppressed (`<title>Lobbying in Wisconsin</title>` rather than the principal name), but the Authorized Lobbyists section IS populated. The parser keys on the heading text, not on the principal-info section, so redacted pages parse cleanly.
- Pandas + xlrd as production deps (added via `uv add`): chosen over the lightweight-xlrd-only and "skip-the-xls" alternatives. The downstream branch will likely want pandas anyway, and the .xls reader is a thin `pd.read_excel(header=4)` shim.
- The directory `.xls` has **5 pre-data rows** (title / session / printed / blank / column headers), not 3 as the kickoff convo recorded. `header=4` puts pandas at the right place. Correction landed in the discovery module's docstring.
- Unification logic: edge identity = `(lobbyist_id, principal_id, authorized_on)`; re-authorizations preserved as distinct rows; disagreeing `withdrawn_on` reconciled to the more-informative value (date over None; later of two dates) with a WARNING. Schlaak-class filter = `discovered_via='principal' AND lobbyist_in_grid=False`.

## Provisional Findings

- **Pre-flight size sample bounds the worst case at ~340 KB / page.** Original gap-investigation sample (42 pages, biased toward ceased + low-volume) had a 157 KB max; WHA (15 lobbyists, top of the distribution) is 338 KB. Full-scrape disk estimate: ~320 MB at the upper bound; bounded by the 1.0 s polite delay at ~17 min wall regardless.
- **Discovery numbers match the plan exactly:** 904 .xls + 942 auth-graph = 944 union, 902 intersection, 40 auth-only (ceased + redacted), **2 dir-only IDs = `[12900 (Voces), 12997 (WCTA)]`** — exactly the two principals flagged by the gap investigation as downstream consequences of the lobbyist-side soft-404 (12717) and the Schlaak case (12694). Cross-validation passed.
- **WCTA / Schlaak case end-to-end:** sanity-check scrape (10 principals, WCTA prepended) produced exactly one row for principal 12997: `lobbyist_id=12694, authorized_on=2026-01-08, withdrawn_on=None`. The load-bearing edge for the whole plan is reachable, parseable, and lands cleanly in the principal-side TSV. The actual count of Schlaak-class lobbyists comes from the full scrape's unified output.
- **Live wall time at delay=1.0:** ~1.2 s/principal in the sanity batch (11.9 s for 10 fetches), tracking the lobbyist-side scrape's 1.1 s/lobbyist. Full-scrape extrapolation: ~18 min including HTTP latency.
- **Resume contract verified:** re-running the sanity batch shows 0 fetched / 10 skipped / 0.0s elapsed. Checkpoint/resume is working as expected.
- **SAL endpoint correction:** the actual export URL is `/Who/StateAgencies/2025REG/ExcelExport`; the prior session's `/ReportExport?outRpt=Excel` returns "Page Not Found". The correct file is 3.6 MB HTML-as-XLS (SSRS-style) and parses cleanly via `pd.read_html` to 2,599 rows × 13 columns. Saved to `WI/WI_directory_state_agency_liaisons.xls`.

## Decisions Made

- **Refactor over duplicate** (Dan via AskUserQuestion): extract `entity_fetcher.py` with URL-template + ID-field-name parameterization; lobbyist + principal fetchers thin-wrap it. ~200 lines of duplication avoided.
- **Proceed without waiting on `lobbying@wi.gov` reply** (Dan via AskUserQuestion): the Schlaak-class structural finding is the scrape's load-bearing deliverable and is independent of any CSV the Ethics Commission might send.
- **Output: three TSVs** (lobbyist-side, principal-side, unified) (Dan via AskUserQuestion): preserves provenance and per-side auditability.
- **Yes to SAL grab** (Dan via AskUserQuestion): one extra request paired with the size sample; uncovered the endpoint URL correction.
- **Add pandas + xlrd as production deps** (Dan via AskUserQuestion): plan-aligned, natural fit for `read_excel`, and the branch will likely want pandas for downstream analysis. Lightweight alternatives (xlrd-only, skip-the-xls) were available but the dep cost is acceptable.
- **TDD discipline maintained throughout**: 6 parser tests, 6 entity-fetcher tests, 4 discovery tests, 5 materialize tests, 6 unification tests. All RED → GREEN before any commit. Existing 8 authorization-fetcher tests acted as the regression suite for the refactor.
- **`--prepend-ids` CLI flag**: the sanity-check needed to guarantee WCTA (12997) was in the 10-principal batch. Rather than hand-pick IDs, added a `--prepend-ids` flag that moves named IDs to the front of the sorted list.
- **Multi-committer hygiene held**: no main, no other people's branches, no rebase of pushed work; pushes happened mid-stream for backup.

## Architecture

Seven new modules under `src/lobby_analysis/io/wi/` + corresponding tests:

| Module | Public surface | Tests |
|---|---|---|
| `entity_fetcher.py` (NEW core) | `fetch_entity_page`, `fetch_or_load_entity`, `_is_soft_404`, `DEFAULT_USER_AGENT` | 6 |
| `authorization_fetcher.py` (REFACTORED) | `fetch_lobbyist_page`, `fetch_or_load` — thin wrappers binding lobbyist URL template | 8 (regression) |
| `principal_fetcher.py` (NEW) | `fetch_principal_page`, `fetch_or_load_principal` — thin wrappers binding principal URL template | (covered by entity_fetcher tests) |
| `principal_parser.py` (NEW) | `parse_principal_authorizations(html, principal_id) -> list[Authorization]` (reuses `Authorization` + `ParseError` from authorization_parser) | 6 |
| `principal_id_discovery.py` (NEW) | `discover_principal_ids(xls_path, tsv_path) -> set[int]`, `_ids_from_xls`, `_ids_from_tsv` | 4 |
| `principal_materialize.py` (NEW) | `iter_authorizations_from_principal_checkpoints(dir) -> Iterator[Authorization]`, re-exports `write_authorizations_tsv` | 5 |
| `unify_authorizations.py` (NEW) | `unify_authorization_tables(lobbyist_side, principal_side, lobbyist_grid_ids) -> list[dict]`, `UNIFIED_FIELDNAMES` | 6 |
| `scrape_principals.py` (NEW CLI) | `main(argv)` — argparse CLI with `--limit`, `--delay`, `--prepend-ids`, `--skip-fetch`, `--skip-materialize` | (Step 9 sanity batch) |
| `unify_authorizations_cli.py` (NEW CLI) | `main(argv)` — argparse CLI that emits `WI_lobbyist_principal_authorizations_unified.tsv` | (Step 11 end-to-end) |

Three new test fixtures (committed):
- `tests/fixtures/wi/principal_12997.html` (30 KB) — WCTA, 1 lobbyist (Schlaak), load-bearing case
- `tests/fixtures/wi/principal_11348.html` (40 KB) — Lexia Learning, 4 lobbyists
- `tests/fixtures/wi/principal_11530.html` (27 KB) — privacy-redacted principal (auth section populated despite suppressed info section)

**27 new behavior tests, all green. Total WI test suite: 97 passed, 0 failed.** (Pre-existing 3 failures in `tests/test_pipeline.py` are scoring/pri-2026-rescore-owned, same as the prior session's note.)

## Results

Full numerical writeup: [`results/20260526_wi_principal_side_scrape_results.md`](../results/20260526_wi_principal_side_scrape_results.md) (forthcoming after the full scrape + unification complete).

Headline:

- **Principals scraped:** 944 (universe = directory .xls ∪ auth-graph TSV)
- **Hard 404s on principal pages:** 0
- **Soft 404s on principal pages:** **0** (vs 1 on lobbyist side; principal pages cleaner)
- **Total principal-side authorization rows:** 2,254
- **Distinct lobbyists in principal-side scrape:** 748 (vs 745 from lobbyist-side, **+3**)
- **Unified table rows by `discovered_via`:** `{lobbyist: 0, principal: 3, both: 2251}` — **principal side is a strict superset of the lobbyist side on this snapshot**
- **Schlaak-class lobbyist count** (= distinct `lobbyist_id` with `discovered_via='principal' AND lobbyist_in_grid=False`): **2** (12694 = Schlaak, 11513 = Steinbruecker — a NEW case)
- **Soft-404 recoveries** (`discovered_via='principal' AND lobbyist_in_grid=true`): 1 (12717 = Neumann-Ortiz / Voces, edge recovered via principal back-link despite her lobbyist-side detail page being broken)
- **Wall time of full scrape:** 1170.9 s ≈ 19 min 31 s (slightly over the 17-min estimate; per-fetch ~1.25 s at delay=1.0, marginally slower than the lobbyist-side scrape's 1.11 s due to larger average page size)

**Bottom line: lobbyist-side scrape is ~99.9% edge-complete and ~99.7% lobbyist-complete on this 2026-05-26 snapshot.** The Schlaak-class blind spot is real (Steinbruecker is a confirmed second case, different shape from Schlaak: surrendered same day as the .xls print) but small. The principal-side scrape is now the strictly-more-complete edge source going forward.

### Sanity-check batch (verified)

- 10 principals fetched in 11.9 s (1 prepended = WCTA, 9 by sorted-ID order)
- 29 authorizations materialized, 23 distinct lobbyists
- **WCTA → Schlaak edge confirmed**: `12694, 12997, 2026-01-08, ""` in the materialized TSV
- 0 HTTP 404s, 0 soft-404s on this batch

## Open Questions

- **What is the grid AJAX's exclusion rule?** The Schlaak case remains the unresolved structural anomaly: license current, authorization current, but excluded from BOTH the grid and the directory `.xls`. Steinbruecker's exclusion explains itself by surrender date (5/25/2026, same day as .xls print) but the .xls disagreement (he's IN the .xls, OUT of the grid) reveals that the two roster sources aren't aligned. An email exchange with WI Ethics Commission is the cheapest path to a clean answer.
- **Are the 2 Schlaak-class lobbyists stable across sessions?** Schlaak 16+ months tenured; Steinbruecker ~17 months. If the exclusion is administrative, it might persist across 2023REG → 2025REG. Cross-session enumeration is a natural follow-up.
- **Should we use the principal-side scrape as the canonical edge source going forward?** It's a superset of the lobbyist-side scrape AND discovers Schlaak-class lobbyists for free. The lobbyist-side scrape remains useful for per-lobbyist metadata (license dates, surrender) that the principal page doesn't expose. For *edges*, principal-side is strictly more complete.
- **License Type column doesn't discriminate.** The plan's hypothesis ("Single → in grid, Pro Bono → absent") is refuted: 658 Single + 116 Multiple + 2 NaN in the .xls; the grid omits a mix, not a clean partition. Filter mechanism is elsewhere.
- **Will `lobbying@wi.gov` reply?** Held over from prior session. If a CSV arrives later, three-way cross-validation against the lobbyist-side + principal-side tables becomes possible.

## Captured Tasks

(None new this session.)
