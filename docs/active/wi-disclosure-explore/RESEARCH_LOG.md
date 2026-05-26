# wi-disclosure-explore — Research Log

Index for the `wi-disclosure-explore` branch. One entry per session, newest first. See `convos/` for full session summaries and `plans/` for implementation plans.

**Branch purpose:** Build the data layer for Wisconsin lobbying disclosure — entity tables (lobbyists, principals, state-agency liaisons), authorization relationships, and SLAE expenditure reports — for the 2025-2026 session. Parallel to the existing `nc-disclosure-explore` line.

---

## Session: 2026-05-26 — wi_tier_2_parser_plan

### Topics Explored
- What data the per-principal and per-lobbyist HTML pages expose beyond authorization edges (three-tier framing: edges / per-period summaries / per-(lobbyist, principal, period) itemizations)
- Whether the Schlaak case "WCTA" is the Cable Telecommunications Assn or the County Treasurers Assn (the two principal-side scrape results docs disagreed; web-search resolution + fixture body)
- Whether Neumann-Ortiz's soft-404 could be a hyphen-encoding issue (refuted)
- The fit of Tier-2 data into the existing v1.1 `LobbyingFiling` schema, and the hours-field gap
- The model-versioning convention (no code-level `__version__`; versioning lives in plan/RESEARCH_LOG docs; the v1.1 TDD pattern at `tests/test_models_v1_1.py` is the template)
- ID-scheme convention for downstream cross-state joins (WI is the first state-extraction branch in the actual repo; sets the convention)
- Whether tier 3 is in scope (it is not; explicitly held over)

### Provisional Findings
- **The 3 committed principal fixtures are not a representative sample for parser TDD.** 12997 is low-spend-pledge-exempt ($0.00 everywhere); 11530 is privacy-redacted; 11348 (Lexia) uses only "Topics Not Yet Assigned" allocation bucket at 100%. None populate the Legislative Bills/Resolutions, Budget Bill Subjects, or Rulemaking sections. Implementing agent needs to capture new fixtures from high-volume principals (e.g., WHA, WMC) before TDD.
- **The 944 principal HTMLs + 774 lobbyist HTMLs are already on disk.** All Tier-2 data accessible without any new HTTP fetches.
- **Tier 2 maps onto `LobbyingFiling` after a v1.2 bump.** Two new optional fields: `total_hours_communicating`, `total_hours_other`. Non-breaking additive change. Versioning is documentary (docs/plans), not a code-level constant.
- **`Organization` records for principals are missing from the current scrape output entirely.** The auth-edge scraping treated principals as bare IDs; static principal metadata (lobbying interests, CEO, contact details) has no current landing place.
- **Schlaak / WCTA documentation drift:** the principal-side scrape results doc (`results/20260526_wi_principal_side_scrape_results.md:65`) names principal 12997 as "Wisconsin Cable Telecommunications Association"; the gap-investigation results doc and the fixture body both confirm it is **Wisconsin County Treasurers Association** (Schlaak is a county treasurer serving as the association's legislative chair). The acronym "WCTA" is genuinely ambiguous in WI lobbying (Cable Telecommunications and County Treasurers both use it); the scrape writeup got the expansion wrong from context. To be fixed in plan Phase 7.
- **The Schlaak-class Mechanism A reframes** from "unknown grid-AJAX filter" to "likely a public-sector-self-advocacy filter" given Schlaak is a public official, not a paid corporate lobbyist. Testable downstream (would predict that other state-officials-association-affiliated lobbyists are similarly omitted from the grid). Not in scope for this plan.
- **Hyphen-encoding hypothesis for Neumann-Ortiz's soft-404 is dead.** 9 other hyphenated lobbyist surnames in the grid AJAX fetched cleanly; her URL is keyed by ID, not by name.
- **No `nc-disclosure-explore` branch exists in the actual repo**, despite the WI RESEARCH_LOG's branch-purpose statement claiming WI is "parallel to" it. WI is the first state-extraction line; sets conventions for downstream states.

### Decisions Made
- **Scope:** Tier 2 only. Parse what's already on disk. No new fetches.
- **Sequencing:** Principal-side parser first, lobbyist-side mirrors after (symmetric coverage; staged execution).
- **Schema bump:** v1.1 → v1.2 on `src/lobby_analysis/models/filings.py`. Add `total_hours_communicating: float | None` and `total_hours_other: float | None` to `LobbyingFiling`. Mandatory Phase 1 of the plan.
- **Schema-layer scope reminder:** the bump applies to `models/` (disclosure-data contract for actual filings). It does NOT apply to `models_v2/` (statute-metadata cell contract for Prong 1). The two layers are related but version independently.
- **ID scheme:** `WI-principal-{id}` for `Organization.id`; `WI-lobbyist-{id}` for `Person.id`. Matches the uppercase-two-letter `source_state` convention already established in `Person` and `Organization`.
- **Documentation-drift fix** on principal 12997 in scope as a Phase 7 step.

### Results
- No analytical results files this session. The plan IS the deliverable.
- Plan: [`plans/wi_tier_2_parser.md`](plans/wi_tier_2_parser.md)
- Convo: [`convos/20260526_wi_tier_2_parser_plan.md`](convos/20260526_wi_tier_2_parser_plan.md)

### Next Steps
- Phase 0 of the plan requires capturing 2-3 high-volume principal fixtures + 1 high-volume lobbyist fixture from Dan's gitignored data store. Implementing agent blocks until those fixtures land on the branch.
- Plan has 2 open Questions in its footer for the implementing agent to surface at Phase 4: (1) populate `LobbyingFiling.provenance` (recommended yes), (2) any other cheap add-ins beyond doc-drift fix (currently no).
- Held over from prior sessions: (1) reply from `lobbying@wi.gov`, (3) State Agency Liaisons table pull into a parser/ingestion pipeline (data captured as `WI_directory_state_agency_liaisons.xls` already; not yet wired).
- Possible PR + merge of `wi-disclosure-explore` after Tier-2 lands — Dan's call.

---

## Session: 2026-05-26 — wi_principal_side_scrape_implementation

### Topics Explored
- Pre-flight Step 6: size sample on Wisconsin Hospital Association + Auto/Truck Dealers (top-tied at 15 lobbyists) to bound page-size upper end before kicking off the full scrape
- Correction of the prior session's SAL endpoint URL — actual path is `/Who/StateAgencies/2025REG/ExcelExport`, not `/ReportExport?outRpt=Excel`
- Fetcher refactor: extract generic `entity_fetcher.fetch_entity_page` / `fetch_or_load_entity` parameterized by URL template + ID kwarg + checkpoint id_field_name; lobbyist + principal fetchers become thin wrappers
- TDD pass on all new principal-side modules: parser (6 tests), id_discovery (4 tests), materialize (5 tests), unification (6 tests), entity_fetcher (6 tests) — RED → GREEN before commit on each
- Pandas + xlrd added as production deps for the principal-id discovery `.xls` read; corrected the prior session's "3 header rows" note (it's 5)
- Schlaak-class enumeration via the unified `discovered_via` + `lobbyist_in_grid` provenance schema
- Filter-rule hypothesis investigation: cross-checked Steinbruecker (NEW Schlaak-class case) and Schlaak against `WI_directory_lobbyists.xls` + their live detail pages

### Provisional Findings
- **Pre-flight size sample:** WHA = 338 KB (2.15× the prior gap-investigation max of 157 KB); AutoTruckDealers = 100 KB. Worst-case full scrape ≈ 320 MB / 17 min wall, well under the original "500 MB / 5 hr" framing.
- **Discovery numbers match the plan exactly:** 904 .xls + 942 auth-graph = **944 union, 902 intersection, 40 auth-only, 2 dir-only = [12900, 12997]** — the two principals predicted by the gap investigation. Cross-validation passed.
- **Full scrape clean:** 944/944 fetched in 1170.9 s (19.5 min, ~1.25 s/req); **0 hard 404s, 0 soft-404s** on principal pages (vs 1 soft-404 on lobbyist side; principal endpoint is cleaner).
- **Principal side is a strict superset of lobbyist side:** 0 rows `discovered_via='lobbyist'`, 3 rows `discovered_via='principal'`, 2,251 rows `discovered_via='both'`. The principal-side scrape catches every edge the lobbyist side caught, plus 3 additional ones.
- **2 Schlaak-class lobbyists** (`discovered_via='principal' AND lobbyist_in_grid=false`):
  - **12694 = Schlaak** (WCTA, license current, structural anomaly persists)
  - **11513 = Steinbruecker (NEW)** — ACLU of Wisconsin, license surrendered 5/25/2026 (same day as `.xls` print). He IS in the .xls (the snapshot caught him pre-surrender) but NOT in the grid (which reflects the same-day surrender). The .xls's Surrendered Date column is empty for him.
- **1 soft-404 recovery** (`discovered_via='principal' AND lobbyist_in_grid=true`): 12717 = Neumann-Ortiz / Voces — both rosters knew about her, but her lobbyist-side detail page returns soft-404 in the portal; the principal-side scrape recovered her edge via the back-link.
- **Lobbyist-side scrape is ~99.9% edge-complete and ~99.7% lobbyist-complete on this 2026-05-26 snapshot.** The blind spot the gap investigation flagged is *real* (Steinbruecker confirms it's not just one weird lobbyist) but *small*.
- **The directory `.xls` is a point-in-time snapshot, NOT a "still active" filter.** Refuted by the Steinbruecker case (in .xls with empty Surrendered Date despite his detail page showing a surrender on the .xls print date).
- **Withdrawn dates agree perfectly between the two sides** — zero warnings emitted by the unify step's disagreement-warning instrumentation across all 2,251 `discovered_via='both'` rows.

### Results
- Code (8 commits): generic `entity_fetcher.py`, `principal_fetcher.py`, `principal_parser.py`, `principal_id_discovery.py`, `principal_materialize.py`, `unify_authorizations.py`, `scrape_principals.py` CLI, `unify_authorizations_cli.py` CLI; **27 new behavior tests, all green** (97 WI tests total: 76 broader + 21 new wave; 3 pre-existing `test_pipeline.py` failures are scoring/pri-2026-rescore-owned, same as prior session)
- Fixtures: `tests/fixtures/wi/principal_{12997,11348,11530}.html` (WCTA / Lexia / privacy-redacted)
- Data (gitignored): 944 `{principal_id}.json` checkpoints under `~/data/lobby_analysis/disclosures/WI/_principal_scrape_checkpoints/`, principal-side TSV (2,254 rows), unified TSV with provenance (2,254 rows × 6 cols), SAL table at `WI_directory_state_agency_liaisons.xls` (2,599 liaison rows × 13 cols)
- Convo: [`convos/20260526_wi_principal_side_scrape_implementation.md`](convos/20260526_wi_principal_side_scrape_implementation.md)
- Results: [`results/20260526_wi_principal_side_scrape_results.md`](results/20260526_wi_principal_side_scrape_results.md)

### Next Steps
- **Schlaak's grid exclusion remains unexplained.** Email to `lobbying@wi.gov` (Dan handling — same email thread as the prior session's draft) is the cheapest path to a clean answer. Brute-force ID enumeration in 10000–13500 range is deferred per the plan's "What could change."
- **Cross-session principal_id stability**: still held over; relevant for time-series. Now-resolved: principal-side scrape is the right edge source for that analysis.
- **State Agency Liaisons table**: grabbed in pre-flight (2,599 rows × 13 cols at `WI_directory_state_agency_liaisons.xls`). NOT yet wired into a parser / ingestion pipeline; held over.
- **PR + merge of `wi-disclosure-explore`?** Dan's call. The branch has shipped two end-to-end scrapes + the unification deliverable; natural milestone.

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
