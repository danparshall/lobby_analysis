# WI Authorization Scrape — Implementation Session

**Date:** 2026-05-26
**Branch:** wi-disclosure-explore
**Previous convo:** [`20260526_wi_data_ingest_and_join_key_investigation.md`](20260526_wi_data_ingest_and_join_key_investigation.md)
**Plan executed:** [`plans/wi_authorization_scrape.md`](../plans/wi_authorization_scrape.md)

## Summary

This session executed the implementation plan from yesterday's investigation convo. The deliverable: a polite, resumable scraper that walks the 774 per-lobbyist detail pages on `lobbying.wi.gov`, extracts each lobbyist's "Principals Represented" table, and materializes the bipartite `(lobbyist_id, principal_id, authorized_on, withdrawn_on)` join table — the relationship the bulk `.xls` directory exports don't carry.

The scrape ran clean. The architectural rest of the session was the test-first build of four small modules (parser, fetcher, materializer, lobbyist-ID discovery) under TDD, with a fifth thin CLI orchestrator on top. **One mid-plan finding became its own piece of work:** the plan flagged "lobbyist IDs not in the `.xls`" as a known unknown to be solved later by scraping the SearchNames hub; the actual portal turned out to have a single AJAX endpoint (`POST /Who/Lobbyists/2025REG/ShowLobbyistList` with `pageSize=1000`) that returns all 774 IDs in one 353 KB response. That endpoint discovery + the ID parser landed as a separate module (`lobbyist_id_discovery.py`) before the scrape, rather than as an ad-hoc bash step inside the CLI.

The "Email AND scrape in parallel" decision came up early in the session: Dan picked it via AskUserQuestion, the email draft was prepared but left for Dan to send, and the scrape proceeded immediately.

## Topics Explored

- Plan execution under TDD: write all tests RED first per the `test-driven-development` skill, watch them fail, then GREEN
- WI portal's LobbyistList grid AJAX endpoint — derivation from `/Content/site.js`'s `refreshGrid` function (`{appPath}/{controller}/Show{type}` URL pattern, form fields `pageNumber` / `pageSize` etc.)
- Mocking-library decision: skip `requests_mock` / `responses` in favor of a small in-test `FakeSession` so dev deps stay minimal and tests avoid "the mock was called with X" anti-patterns
- Pandas decision: skip pandas at the materialize layer too — 4-column TSV fits `csv.DictWriter` cleanly and the only previous pandas use was an ephemeral `.xls` inspection
- Live-portal politeness floor: 1 s polite-sleep between requests, browser-realistic UA, session-cookied (`/Home/Welcome` warmup before the AJAX POST)
- Permission-prompt friction: a `cp /tmp/... ~/code/...` triggered a permission prompt despite `Bash(cp *)` being allowed; investigated but not fully diagnosed (Claude Code's built-in path validator is one suspect). Dan picked Option (c) — sidestep the question entirely by doing all remaining file ops via the `Write`/`Edit` tools and all remaining HTTP via `uv run python`. Curl was retired mid-session for the same reason (every curl prompts; `requests` doesn't)

## Provisional Findings

- **Plan's "ID discovery known unknown" resolves cleanly via one POST.** The AJAX endpoint `https://lobbying.wi.gov/Who/Lobbyists/{session_id}/ShowLobbyistList` accepts `pageSize=1000` and returns the full grid HTML in a single 353 KB response. URL pattern derived from the public `/Content/site.js` (`refreshGrid` → `urls.view = {appPath}/{controller}/Show{type}`).
- **Lobbyist 11042's live page matches the test fixture exactly** (9 principals, same IDs). Small-batch run (10 lobbyists, 11 sec) validated the parser end-to-end against fresh portal data, not just the saved fixture.
- **The plan's "do withdrawals appear on the lobbyist page" open question is answered: yes.** The 10-lobbyist sanity batch surfaced one withdrawn authorization (lobbyist 11045 → principal 10941, authorized 2024-12-10, withdrawn 2025-07-01). The parser's `withdrawn_on` branch — previously exercised only by the fixture's "N/A → None" case — now has real ground truth too.
- **Rate of fetch ≈ 1.1 s/lobbyist** including HTTP latency at delay=1.0. Small-batch wall: 11 s for 10 fetches. Full-scrape extrapolation: ~14 min for the remaining 764.
- **Plan said 776 lobbyists; portal says 774.** Two were apparently delisted between the `.xls` export print date (5/25/2026) and the scrape (5/26/2026), or the original count rounded.
- **`robots.txt` is absent at `lobbying.wi.gov`** — server returns the standard 404-as-HTML page for `/robots.txt`. No machine-readable scraping restriction.
- **Pre-existing failures in `tests/test_pipeline.py`** (3 of them — `test_ca_snapshot_loads_and_flags_incapsula_stubs`, `test_brief_contains_all_rubric_items_and_instructs_subagent`, `test_stamp_rows_adds_provenance`) are not introduced by this session. Same code on `origin/main` (`SNAPSHOT_DATE_DEFAULT = "2026-04-13"`) but `data/portal_snapshots/CA/` only has `2026-05-01/`. These tests belong to the archived `scoring` / `pri-2026-rescore` research lines; flagged here, not fixed (multi-committer hygiene).

## Decisions Made

- **Module location**: `src/lobby_analysis/io/wi/` (Dan via AskUserQuestion). Long-lived project code, parallel to the eventual `nc/`.
- **Dep approach**: `uv add` for project deps (Dan via AskUserQuestion). Added `lxml`; `beautifulsoup4` was already explicit.
- **No `requests_mock`/`responses` dev dep**: in-test `FakeSession` instead. Keeps dev deps minimal; assertions stay on outcomes (returned HTML, on-disk file contents), not on mock-call shapes.
- **No `pandas` dep for materialize**: `csv.DictWriter` instead. Pandas can come in via ephemeral `uv run --with` if later analysis wants it.
- **Checkpoints store raw HTML**, not pre-parsed authorizations. Parser fix → re-materialize, not re-scrape.
- **404s are persisted** (`{"html": null, "status_code": 404}`) so a resumed run doesn't re-attempt the network for known-missing pages.
- **Discovery is also checkpointed**: the grid HTML is saved to `_lobbyist_grid_{session_id}.html` in the checkpoint dir, so re-runs skip the discovery POST too.
- **Email**: drafted for `lobbying@wi.gov` (note: the portal footer lists `lobbying@wi.gov`, not `ETHLobbying@wi.gov` from the plan — likely a typo in the previous convo). Dan handling the send himself.

## Architecture

Five modules under `src/lobby_analysis/io/wi/` + corresponding tests:

| Module | Public surface | Tests |
|---|---|---|
| `authorization_parser.py` | `Authorization` (frozen dataclass), `ParseError`, `parse_lobbyist_authorizations(html, lobbyist_id) -> list[Authorization]` | 4 |
| `lobbyist_id_discovery.py` | `parse_lobbyist_ids(html) -> list[int]`, `fetch_lobbyist_grid_html(session, ...)` | 4 |
| `authorization_fetcher.py` | `fetch_lobbyist_page(lobbyist_id, session, *, delay, max_retries) -> str \| None`, `fetch_or_load(lobbyist_id, checkpoint_dir, session, ...) -> dict` | 7 |
| `authorization_materialize.py` | `iter_authorizations_from_checkpoints(dir) -> Iterator[Authorization]`, `write_authorizations_tsv(rows, path) -> int` | 4 |
| `scrape_authorizations.py` | `main(argv)` — argparse CLI tying the above together | — (integration test = Step 9 small batch) |

Two test fixtures (committed to the repo):
- `tests/fixtures/wi/lobbyist_11042.html` (34 KB) — per-lobbyist detail page, ground truth = 9 authorizations
- `tests/fixtures/wi/lobbyist_grid_2025REG.html` (353 KB) — full LobbyistList grid AJAX response with all 774 lobbyist links

19 new behavior tests, all green. Full suite: 1425 passed / 3 pre-existing fails (not ours) / 3 skipped / 3 xfailed.

## Results

Full numerical writeup: [`results/20260526_wi_authorization_scrape_results.md`](../results/20260526_wi_authorization_scrape_results.md).

Headline:

- **Lobbyists scraped:** 774 (the LobbyistList grid count for 2025REG)
- **Soft 404s:** 1 (lobbyist 12717 — HTTP 200 + "Page Not Found" body)
- **Lobbyists with ≥1 authorization:** 745 (29 lobbyists, incl. the soft-404, contributed no edges)
- **Total `(lobbyist, principal)` authorization rows:** 2,251
- **Distinct principals authorized:** 942 (40 more than the 904 in `WI_directory_principals.xls` — worth investigation)
- **Withdrawn rows:** 258
- **Pending-authorization rows (`authorized_on IS NULL`):** 4
- **Output TSV:** `/Users/dan/data/lobby_analysis/disclosures/WI/WI_lobbyist_principal_authorizations.tsv` (gitignored)
- **Wall time of full scrape:** 851 sec (14 min 11 sec), ~1.11 s/req including HTTP

### Two real-data bugs surfaced during materialize, fixed TDD-style

Both before the TSV could be written; both shipped as new behavior tests + parser/fetcher changes in the same checkpoint commit.

1. **Parser: `Authorized On = N/A`** — 4 of 2,251 rows have this shape (lobbyists 11112, 12666, 12748, 13865; Wisconsin Reading Corps appears in 2 of the 4). The parser was raising `ParseError` on these because `authorized_on` was typed `date` (required). Fix: changed `Authorization.authorized_on: date | None`, unified the date extractor to use the optional path for both date columns. Wrote the failing test against synthetic HTML reproducing the row shape; saw it fail with the original ParseError; landed the type-and-extractor change; new + existing tests all green. Materialize writer also updated to write blank instead of crashing on None.
2. **Fetcher: soft-404s** — WI portal returns HTTP 200 with a `<title>Page Not Found</title>` body for nonexistent lobbyist IDs (observed: 12717). Status-code-only detection treated it as a real fetch and fed an error-page body into the parser. Fix: added `_is_soft_404(html)` body-marker check; if matched, `fetch_lobbyist_page` returns None just like an HTTP 404. New behavior test asserts the soft-404 body path produces None. Original 12717 capture preserved as `12717.diagnostic_soft_404_capture.json` per experiment-data-integrity; re-fetched cleanly with the new logic (1.3 sec via the resume contract).

Both bugs are the kind that wouldn't be caught by mocked or fixture-only testing — they were surfaced by the live data shape. The TDD discipline (failing test FIRST, then fix) was tightened around real reproducible inputs as a result.

## Open Questions

- **Will `lobbying@wi.gov` actually deliver an SSRS CSV?** Email drafted; Dan to send. Cross-validating their CSV against the scrape (if they share one) would catch any rows the scraper missed.
- **What does the State Agency Liaisons table look like?** Third entity table flagged for this session but never fetched — would be one extra POST/GET to `/Who/StateAgencies/2025REG/ReportExport?outRpt=Excel`. Held over.
- **Cross-session ID stability.** Is `principal_id` stable across biennia? Important for time-series; untested.
- **Does the principal-side scrape produce the same edges?** Cheap cross-validation; held over.

## Captured Tasks

(None new this session.)
