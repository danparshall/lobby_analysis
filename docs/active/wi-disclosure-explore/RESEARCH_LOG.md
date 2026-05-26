# wi-disclosure-explore — Research Log

Index for the `wi-disclosure-explore` branch. One entry per session, newest first. See `convos/` for full session summaries and `plans/` for implementation plans.

**Branch purpose:** Build the data layer for Wisconsin lobbying disclosure — entity tables (lobbyists, principals, state-agency liaisons), authorization relationships, and SLAE expenditure reports — for the 2025-2026 session. Parallel to the existing `nc-disclosure-explore` line.

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
