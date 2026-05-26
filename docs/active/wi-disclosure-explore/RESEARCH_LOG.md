# wi-disclosure-explore — Research Log

Index for the `wi-disclosure-explore` branch. One entry per session, newest first. See `convos/` for full session summaries and `plans/` for implementation plans.

**Branch purpose:** Build the data layer for Wisconsin lobbying disclosure — entity tables (lobbyists, principals, state-agency liaisons), authorization relationships, and SLAE expenditure reports — for the 2025-2026 session. Parallel to the existing `nc-disclosure-explore` line.

---

## Session: 2026-05-26 — wi_authorization_scrape_implementation

### Topics Explored
- Executed [`plans/wi_authorization_scrape.md`](plans/wi_authorization_scrape.md) under TDD
- AJAX endpoint discovery on lobbying.wi.gov: the LobbyistList grid POSTs to `/Who/Lobbyists/{session_id}/ShowLobbyistList` with `pageSize=1000` returning all 774 IDs in one response — derived from `/Content/site.js`'s `refreshGrid`
- Mocking-library decision (skipped `requests_mock`/`responses` in favor of in-test `FakeSession`)
- Pandas decision (skipped for materialize; `csv.DictWriter` for 4-column TSV)
- Live-portal hit threshold: small-batch (10 lobbyists, ~11 sec) before full scrape
- Permission-prompt friction on cross-directory `cp` — Dan picked (c): all remaining file ops via Write/Edit tools, all HTTP via `uv run python` + requests (no more curl)

### Provisional Findings
- **Plan's "lobbyist IDs not in the .xls" known unknown resolves cleanly** via one POST to the grid AJAX endpoint with `pageSize=1000`. Discovery is now a 353 KB single-shot, not a 31-page paginated walk.
- **Live portal matches the test fixture exactly for lobbyist 11042** (9 principals, same IDs). End-to-end validated against fresh data, not just the saved fixture.
- **Withdrawal-date branch is exercised in live data** — the 10-lobbyist sanity batch surfaced lobbyist 11045 → principal 10941, authorized 2024-12-10, withdrawn 2025-07-01. Parser handles both N/A→None (from fixture) AND real dates correctly.
- **774 lobbyists, not 776** — plan was off by 2 (likely delisted between the 5/25 `.xls` print and the 5/26 scrape).
- **Fetch rate: ~1.1 s/lobbyist** at delay=1.0 including HTTP latency. Full scrape extrapolation: ~14 min wall.
- **Pre-existing test failures in `tests/test_pipeline.py`** (3) — same on `origin/main`; archived-line-owned (scoring/pri-2026-rescore); not introduced by this session, flagged but not fixed.
- **Numerical scrape results**: 774 lobbyists scraped (1 soft-404 → 773 with real pages → 745 with ≥1 authorization), 2,251 total `(lobbyist, principal)` authorization rows, 942 distinct principals authorized (vs 904 in the directory `.xls` — 40-entry gap worth investigating), 258 currently-withdrawn rows, 4 pending-authorization rows. Full scrape wall: 851 sec at delay=1.0. Top principal (tied at 15 lobbyists): Wisconsin Automobile and Truck Dealers Association + Wisconsin Hospital Association. Top lobbyist: Bryan Brooks (41 principals). Two real-data bugs surfaced during materialize and fixed test-first: `Authorized On = N/A` (4 rows) → `authorized_on: date | None`; soft-404s (1 row, lobbyist 12717) → body-marker detection in fetcher. Full writeup in [`results/20260526_wi_authorization_scrape_results.md`](results/20260526_wi_authorization_scrape_results.md).

### Results
- Code: 5 new modules under `src/lobby_analysis/io/wi/` + 19 new behavior tests, all green
- Fixtures: `tests/fixtures/wi/lobbyist_11042.html` (34 KB) + `tests/fixtures/wi/lobbyist_grid_2025REG.html` (353 KB)
- Convo: [`convos/20260526_wi_authorization_scrape_implementation.md`](convos/20260526_wi_authorization_scrape_implementation.md)
- Results doc: [`results/20260526_wi_authorization_scrape_results.md`](results/20260526_wi_authorization_scrape_results.md)
- Data (gitignored): `~/data/lobby_analysis/disclosures/WI/_authorization_scrape_checkpoints/` (774 `{id}.json` + cached grid HTML) + `~/data/lobby_analysis/disclosures/WI/WI_lobbyist_principal_authorizations.tsv`

### Next Steps
- Send the drafted email to `lobbying@wi.gov` (Dan handling); if a CSV comes back, cross-validate against the scrape.
- Pull the State Agency Liaisons table (`/Who/StateAgencies/2025REG/ReportExport?outRpt=Excel`) — flagged in the prior session and still held over.
- Cross-validate by scraping the principal-side ("Authorized Lobbyists" section on per-principal pages) — should yield the same bipartite graph; cheap insurance.
- Investigate `principal_id` stability across legislative sessions (2023REG vs 2025REG) — needed for cross-biennium time-series of the influence graph.
- Address the pre-existing `tests/test_pipeline.py` failures at a future cleanup — not on this branch (archived-line ownership).

---

## Session: 2026-05-26 — wi_data_ingest_and_join_key_investigation

### Topics Explored
- Convention for state-specific data layout (chose NC-parallel flat: `data/disclosures/WI/`)
- Inspection of the two WI Ethics Commission `.xls` directory exports — shape, columns, encoding artifacts
- Portal investigation: where the lobbyist↔principal authorization relationship is exposed (and where it isn't)
- SSRS endpoint status (currently 500ing server-side for direct URL hits)
- Comparative cost of scraping from the lobbyist side vs. principal side

### Provisional Findings
- WI lobbyist directory: 776 licensed lobbyists, 12 columns, 3 header rows, Excel-serial date encoding on `Surrendered Date`. 62 have surrender dates (~714 currently active).
- WI principals directory: ~905 registered principals, 24 columns (3 are empty Excel-spacer artifacts), 3 header rows. 3 have cessation dates (~902 currently active). `Principal ID` is a clean integer foreign key.
- The two files **do not join cleanly** — the lobbyist file references employers by *Organization Name* (string), not by *Principal ID*.
- The authorization relationship exists in the portal database and is visible on per-entity detail pages but is **not exposed as a bulk export**. The four `/Who/.../ReportExport?outRpt=Excel` endpoints cover only the three entity rosters (lobbyists, principals, state agency liaisons).
- **Cheapest scrape path**: lobbyist detail pages (~34 KB × 776 ≈ 26 MB) vs. principal detail pages (~560 KB × 905 ≈ 500 MB). Spot-check confirmed lobbyist page DOM parses cleanly: lobbyist 11042 → 9 principal IDs in `Principals Represented` with `Authorized On` dates.
- SSRS direct endpoint (`/Reports/Report.aspx?ReportPath=...`) returns `Failed call to SSRSAgent.GetReportList()` even with browser UA — server-side problem, also seen in 2026-05-01 portal snapshot.

### Results
This session produced no analytical results files. Numerical findings pinned in [`convos/20260526_wi_data_ingest_and_join_key_investigation.md`](convos/20260526_wi_data_ingest_and_join_key_investigation.md). Plan for follow-on work in [`plans/wi_authorization_scrape.md`](plans/wi_authorization_scrape.md).

### Next Steps
- Decide whether to email `ETHLobbying@wi.gov` requesting an authorizations CSV (could skip the scrape entirely).
- Execute [`plans/wi_authorization_scrape.md`](plans/wi_authorization_scrape.md): build parser under TDD → scraper with checkpointing → materialize join table → spot-check.
- While at the portal, also grab `/Who/StateAgencies/2025REG/ReportExport?outRpt=Excel` (third entity table, low-cost addition).
- Verify whether withdrawn authorizations are visible on the lobbyist-side detail page (only confirmed for principal-side in this session).
