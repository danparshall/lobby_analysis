# WI Data Ingest and Join-Key Investigation

**Date:** 2026-05-26
**Branch:** wi-disclosure-explore

## Summary

This is the kickoff session for the `wi-disclosure-explore` branch — a new research line for Wisconsin lobbying disclosure data, parallel to the existing `nc-disclosure-explore`. Dan dropped two `.xls` files from the WI Ethics Commission into `~/Downloads/lobby/wi/` and asked to move them into the data store and summarize them. The session then turned into a portal investigation when summary inspection revealed the two files don't carry a foreign-key relationship between lobbyists and principals.

The two files are WI Ethics Commission directory exports for the 2025–2026 legislative session, printed 5/25/2026: 776 licensed lobbyists and ~905 registered lobbying principals (each in its own flat file). Investigation of the WI Ethics Commission's "Eye on Lobbying" portal (`lobbying.wi.gov`) found that the bulk Excel exports available there cover exactly these two entity tables and one sister table (state agency liaisons). The authorization relationship — which lobbyist is authorized to lobby on behalf of which principal — exists in the underlying SSRS database and is publicly visible on per-entity detail pages, but is not exposed via any bulk download endpoint we could find.

The session ended with a plan written for the next agent to scrape per-lobbyist detail pages (34 KB each, ~776 total) and reconstruct the authorization table from the embedded "Principals Represented" sections.

## Topics Explored

- Convention for state-specific data in the repo (`data/disclosures/<STATE>/` flat per the NC precedent; `data/` is a gitignored symlink to `/Users/dan/data/lobby_analysis/`)
- Structure of the two WI directory exports (legacy `.xls`, header rows at 0–2, real data from row 3; Excel-serial date encoding for `Surrendered Date`)
- Where the join key (lobbyist ↔ principal authorization) lives in the WI portal — and where it doesn't
- SSRS endpoint status: currently returning `Failed call to SSRSAgent.GetReportList()` to all direct hits, both UA-spoofed and not — server-side problem, not scraping/UA
- Per-entity detail page structure: principal pages are ~560 KB (carry SLAE data) with an "Authorized Lobbyists" section; lobbyist pages are ~34 KB with a "Principals Represented" section and "Authorized On" dates
- Symmetric scrape directions (lobbyist→principals vs principal→lobbyists) produce the same bipartite graph

## Provisional Findings

These are observations from this session — not settled conclusions:

- **No bulk authorization export exists on the public portal.** The four "Who" search hubs (`/Who/Lobbyists/`, `/Who/Principals/`, `/Who/StateAgencies/`, `/Who/LobbyingRegistryChanges/`) each expose a `ReportExport?outRpt=Excel` endpoint, but only for the first three (entity rosters). The Changes-to-Registry hub does not have a `ReportExport` route (probe returned 404). No SSRS canned report we could probe matched the authorization-table shape.
- **The data is reachable via HTML scraping.** Per-lobbyist detail pages embed `/Who/PrincipalInformation/2025REG/Information/{ID}` hrefs in a "Principals Represented" section alongside "Authorized On" dates. These are stable URLs with the principal ID as a clean foreign key to the principal table we already have. Spot-check confirmed: lobbyist 11042 → 9 principal IDs.
- **Scraping from the lobbyist side is ~17× more efficient than from the principal side** (34 KB pages × 776 vs 560 KB × 905). Both sides should produce the same edges; cross-validation is cheap.
- **The `Principal Number Of Members` field in the principals export is semantically inconsistent.** 3M reports 679,000 (likely total employees); trade associations would report members; corporations vs. associations vs. unions all use the field differently. Don't treat it as a comparable scalar without cleaning.
- **SSRS endpoint is currently broken for direct URL hits** (`Failed call to SSRSAgent.GetReportList()` returned to browser-UA requests too). The user-facing `/Who/.../ReportExport` MVC routes work around this somehow, but the canonical `https://lobbying.wi.gov/Reports/Report.aspx?ReportPath=...` URLs do not. This was already documented in the 2026-05-01 portal snapshot's `skipped` section; re-verified live today.

## Decisions Made

- Created new branch + worktree `wi-disclosure-explore` parallel to `nc-disclosure-explore`.
- Filed the two `.xls` files under `/Users/dan/data/lobby_analysis/disclosures/WI/` (NC-parallel flat layout) with NC-parallel naming: `WI_directory_lobbyists.xls` and `WI_directory_principals.xls`.
- Scraping path chosen: **from the lobbyist side** (smaller pages, cleaner DOM, principal IDs as foreign keys).
- Plan written: [`plans/wi_authorization_scrape.md`](../plans/wi_authorization_scrape.md).
- **Wildcard option flagged but not pursued:** email `ETHLobbying@wi.gov` asking whether the Ethics Commission can run a CSV of `(lobbyist_id, principal_id, authorized_on, withdrawn_on?)` from the SSRS database directly. Cost is one email; saves the scrape entirely if they say yes. Dan to decide whether to send.

## Results

This session produced no analytical results files (no plots, tables, or analysis outputs). The two `.xls` files are in `data/disclosures/WI/` and the in-conversation summary lives here in this convo doc. Numerical findings worth pinning:

- `WI_directory_lobbyists.xls` — 779 rows × 12 columns; 3 header rows; ~776 real lobbyist records; 62 with surrender dates (~714 currently active); License Type values: `Single`, `Multiple`; `Surrendered Date` stored as Excel serial.
- `WI_directory_principals.xls` — 910 rows × 24 columns (3 cols are empty Excel-spacer artifacts: `Unnamed: 0/7/16`); 3 header rows; ~905 real principal records; 3 with cessation dates (~902 currently active); `Principal ID` is a clean integer key (e.g. 11158 = Wisconsin Agri-Business Association).

## Open Questions

- **Will the Ethics Commission share an authorization CSV on request?** Unknown. Smaller states are often responsive but no precedent set here.
- **Do per-lobbyist detail pages also show *withdrawn* authorizations** (i.e., a lobbyist who was authorized for principal X and then withdrew during the session)? Confirmed visible on principal pages (the cofetched page for principal 11158 showed "authorization dates and withdrawal status"); unverified on lobbyist pages from this session's probe.
- **Is `Principal ID` stable across sessions?** Important if we want to time-series the authorization graph across biennia. Untested — would need to fetch a 2023REG principal page and check whether the same entity has the same ID.
- **What is the rate-limit posture of `lobbying.wi.gov`?** The 2026-05-01 portal snapshot fetched 16 pages without issue. 776 detail pages at 1 req/sec ≈ 13 min — likely safe but not guaranteed. Plan specifies polite defaults.
- **State agency liaisons** — a third entity table (`/Who/StateAgencies/.../ReportExport?outRpt=Excel`) exists but was not pulled this session. Lower priority but worth grabbing for completeness when next agent is at the portal anyway.
