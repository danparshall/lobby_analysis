# wi-disclosure-explore — Research Log

Index for the `wi-disclosure-explore` branch. One entry per session, newest first. See `convos/` for full session summaries and `plans/` for implementation plans.

**Branch purpose:** Build the data layer for Wisconsin lobbying disclosure — entity tables (lobbyists, principals, state-agency liaisons), authorization relationships, and SLAE expenditure reports — for the 2025-2026 session. Parallel to the existing `nc-disclosure-explore` line.

---

## Session: 2026-05-26 — wi_principal_side_scrape_plan

### Topics Explored
- Re-fetch of `/Who/LobbyistInformation/2025REG/Information/12694` (Schlaak detail page) to verify the prior session's structural omission finding is persistent
- Bilateral re-check: also re-POSTed the LobbyistList grid AJAX (`/Who/Lobbyists/2025REG/ShowLobbyistList?pageSize=1000`) to confirm Schlaak is still absent from THAT side
- Reconnaissance over 42 captured principal HTMLs from the gap investigation to characterize size distribution + parse target for the new plan
- Reuse analysis on `src/lobby_analysis/io/wi/` — fetcher is lobbyist-URL-specific; plan needs to refactor generic or duplicate
- Composition of the principal universe for the scrape: `{dir .xls}` ∪ `{auth graph}` = 944 distinct IDs

### Provisional Findings
- **Bilateral omission persists.** Both Schlaak's detail page (25,551 bytes, sha256 `bf616576fb1b2632`) and the grid AJAX (353,140 bytes, sha256 `68b792835c41547f`, 774 IDs) are byte-identical to the captures from ~5 hours earlier. Schlaak still absent from grid, page still resolves.
- **Byte-identity is itself informative.** Suggests edge-cached / daily-snapshot serving rather than live DB query — the "few hours later" check is weaker than originally framed because we may be hitting the same materialized snapshot both times. The 16-month tenure pinpoint from the prior session remains the dominant evidence for structural-vs-transient.
- **Principal page sizes are much smaller than originally estimated.** Empirical: 26 KB min / 40 KB median / 47 KB mean / 157 KB max across 42 captures (biased toward ceased + low-volume). Original convo's "~560 KB" was a bad spot-check. Even 3× the upper bound (active-high-volume principals) gives ~140 MB total, not 500 MB.
- **Wall time at delay=1.0 for 944 pages: ~17 min.** Bounded by politeness, not transfer; same envelope as the lobbyist scrape's 851 sec / ~14 min for 774. The "~5 hr" framing in the prior session's "Next Steps" was wrong.
- **WCTA → Schlaak back-link confirmed in capture.** `principal_12997.html` regex-search for `/Who/LobbyistInformation/2025REG/Information/(\d+)` yields `[12694]`. Parse target well-defined.

### Results
- Plan: [`plans/wi_principal_side_scrape.md`](plans/wi_principal_side_scrape.md) — 12 implementation steps, 6 parser tests (RED → GREEN), unification module with `discovered_via ∈ {lobbyist, principal, both}` + `lobbyist_in_grid` provenance flag, decision point on fetcher refactor-vs-duplicate, 4 open questions for Dan.
- Re-fetch artifacts (gitignored, durable): `~/data/lobby_analysis/disclosures/WI/_principal_gap_investigation/lobbyist_12694_recheck.html` (byte-identical to prior) + `~/data/lobby_analysis/disclosures/WI/_principal_gap_investigation/lobbyist_grid_2025REG_recheck.html` (byte-identical to prior fixture).
- Convo: [`convos/20260526_wi_principal_side_scrape_plan.md`](convos/20260526_wi_principal_side_scrape_plan.md).

### Next Steps
- Execute [`plans/wi_principal_side_scrape.md`](plans/wi_principal_side_scrape.md). First implementation step asks Dan whether to refactor `authorization_fetcher.py` to a generic `entity_fetcher.py` (DRY, recommended) or duplicate as `principal_fetcher.py` (safer for lobbyist code path).
- Pre-flight Step 6 of the plan: sample one known-large active principal page (Wisconsin Hospital Association or Auto Dealers, both with 15 lobbyists) to bound the size-distribution upper end before kicking off the full 944-principal scrape.
- Still held over from prior sessions: (1) `lobbying@wi.gov` reply, (3) State Agency Liaisons table pull (one extra `curl` while at the portal; plan-adjacent).

---

## Session: 2026-05-26 — wi_principal_gap_investigation

### Topics Explored
- Bidirectional set-difference reconstruction of the auth-graph ⇄ directory `.xls` principal-ID gap; asymmetric pair `(40 auth-only, 2 dir-only)` netting to the headline 38
- Live-portal classification of all 40 auth-only principal IDs via `/Who/PrincipalInformation/2025REG/Information/{id}` (1.0 s delay, descriptive UA)
- Investigation of the 2 dir-only principals to identify which lobbyists they reference, with cross-checks against (a) the cached 774-ID LobbyistList grid HTML, (b) our 745-with-auth scrape result, (c) the 776-row `WI_directory_lobbyists.xls`
- Direct fetch of an "invisible" lobbyist's detail page to confirm he's real, licensed, currently authorized, and 16 months tenured

### Provisional Findings
- **Headline 40-principal gap fully explained.** 38 of 40 are cleanly ceased (directory `.xls` filter is empirically `cessation_date IS NULL`); 2 are privacy-redacted "low-spend pledge" entities under the WI Ethics Commission's <$500/year exemption (principal-info detail suppressed but authorization graph fully visible).
- **WI portal data model has 3 principal states**, not 2: active, ceased, and active-but-suppressed (low-spend pledge). The third class matters because their auth graph IS published; our scrape correctly captures them via lobbyist-side pages.
- **Structural finding (more important than the headline gap):** the LobbyistList grid AJAX response is **not exhaustive**. At least one currently-active, licensed, currently-authorized Wisconsin lobbyist (Schlaak, ID 12694) is silently omitted from BOTH the grid response (774 IDs) and `WI_directory_lobbyists.xls` (776 rows). His detail page resolves cleanly by direct URL. The omission isn't a race condition — he was in the system 16 months before our scrape.
- **Our auth graph has unknown lobbyist-side completeness.** Can't bound the Schlaak-class population from this side. The principal-side scrape (handoff option 4) is the only mechanism to enumerate it — reframes (4) from "cheap insurance / cross-validation" to "the only way to bound a real completeness gap."
- **The 2 dir-only principals are downstream consequences:** Voces (12900) ← lob 12717 (the prior session's already-documented soft-404) → orphaned in our graph; WCTA (12997) ← lob 12694 (the Schlaak case) → invisible to our discovery layer.

### Results
- [`results/20260526_wi_principal_gap_investigation_results.md`](results/20260526_wi_principal_gap_investigation_results.md) — full writeup: gap arithmetic, classification of all 40 IDs, structural finding analysis, open questions
- New committed test fixtures: `tests/fixtures/wi/principal_{10949,10973,11017}.html` (Apex Clean Energy, Secure Elections Project, Indivior — canonical ceased-principal examples for future parser tests)
- Gitignored investigation artifacts (durable under `~/data/lobby_analysis/disclosures/WI/_principal_gap_investigation/`): 40 auth-only principal HTMLs + 2 dir-only principal HTMLs + 1 lobbyist HTML (Schlaak) + `gap_classification.csv`

### Next Steps
- **Re-prioritize handoff option (4)** — principal-side scrape — given its newly-clarified completeness role. The case for spending the ~500 MB / ~5 hr wall is now stronger than it was in the prior session's framing.
- Before executing (4): quick re-fetch of `/Who/LobbyistInformation/2025REG/Information/12694` to confirm Schlaak's omission from the grid isn't a one-day glitch — cheap, single HTTP call.
- Investigate the License Type column in `WI_directory_lobbyists.xls` — what value does Neumann-Ortiz have, what value does Schlaak's detail page list? Could help characterize the directory's lobbyist-side filter rule.
- Still held over from prior session: (1) reply from `lobbying@wi.gov`, (3) State Agency Liaisons table pull.
- Convo: [`convos/20260526_wi_principal_gap_investigation.md`](convos/20260526_wi_principal_gap_investigation.md).

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
