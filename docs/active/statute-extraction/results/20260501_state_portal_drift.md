<!-- Generated during: convos/20260501_eve_issue6_data_restoration.md -->

# State portal drift, 2026-04-13 → 2026-05-01

Re-running Stage 1 URL discovery for 8 priority states (CA + CO/NY/WA/TX/WI/IL/FL) after a laptop crash forced a rebuild surfaced **substantive drift in 5 of 8 portals over an 18-day window**. This is the kind of churn the project should expect baseline; quarterly re-snapshotting per state is probably the right cadence even when nothing forces a rebuild.

| State | Drift observed | Implication |
|---|---|---|
| CA | CARS (Cal-ACCESS Replacement System) public go-live now firmly dated **2026-11-26**. FPPC About URL moved (`/about-the-fppc.html` → `/about-fppc/`). Bulk data confirmed live on `campaignfinance.cdn.sos.ca.gov` (650 MB ZIP) — solves the historical "fppc DNS-failed" caveat. | Re-snap CA quarterly (and especially right after Nov 26). Old portal URLs will break at cutover. |
| CO | Hostname **shifted** `sos.state.co.us` → `coloradosos.gov` (same Struts app). Old SOS-hosted statute mirror 404s — replaced by official OLLS Title 24 PDF on `content.leg.colorado.gov`. **New finding:** 10-dataset Socrata mirror at `data.colorado.gov` (cleaner programmatic feed than the 12 daily TXT files). | Code that hardcoded `sos.state.co.us` would silently fail on WAF 403s. |
| NY | **JCOPE webapps fully retired** (Ethics Commission Reform Act of 2022, eff. 2022-07-08). Successor stack: COELIG / CELG at `reports.ethics.ny.gov` + 6-dataset Open NY Socrata partnership (Oct 2023, now canonical bulk layer). Cumulative Bi-Monthly Reports dataset alone is 122M+ records. | Anything pointing at `webapps.jcope.ny.gov/public` is dead (ECONNREFUSED, not redirected). |
| WA | **RCW 42.17A recodified to Title 29B** effective **2026-01-01**; lobbying now at Ch. 29B.50 (13 sections). AccessHub deprecated → 302s into `pdc.wa.gov`. | Any code keying on the literal string "42.17A" needs a 29B mapping. The Justia URL config (`lobbying_statute_urls.py`) doesn't yet have a WA entry, so this hasn't bitten us — flag if/when WA gets added. |
| TX | TEC bulk ZIP **migrated** `ethics.state.tx.us/search/lobby/TEC_LA_CSV.zip` (404) → `prd.tecprd.ethicsefile.com/public/lobby/public/TEC_LA_CSV.zip`. Parallel `ethics.texas.gov` host returned 401 on every probed path — possible staging migration in progress. | Old bulk-download links are dead. |
| WI | No URL changes; new finding: SSRS canned-report endpoints under `/Reports/Report.aspx` are the only true bulk-download surface but 500 under WebFetch (`Failed call to SSRSAgent.GetReportList()`) — needs cookie-warmed Chrome UA or Playwright. Two ethics.wi.gov nav-menu .aspx pages now 404 (`StateAgencyLiaisons`, `ReportLobbyingActivity`); functionality moved to `lobbying.wi.gov`. | Bulk data is technically present but practically inaccessible without browser automation. |
| IL | WAF posture **unchanged** from the historical pass — every `ilsos.gov` and `apps.ilsos.gov` host blocks WebFetch the same way it blocked curl HTTP/2 in April. Two URL-scheme migrations: ILGA moved its ILCS path from `ilcs3.asp?ActID=...` → `Legislation/ILCS/Articles?ActID=...` (old links 404); the canonical `data.illinois.gov/dataset/daily-lobbyist-data` is now at the categorized Socrata path. | Stage 2 reproduces the partial-WAF state without Playwright; that's a known structural gap, not a regression. |
| FL | No URL changes; bifurcated regime captured this pass (5 legislative + 5 executive + 5 cross-regime seeds). New finding: `dl_data.cfm` files show timestamps frozen at **12/31/2014** despite "daily-refreshed" advertising. | Needs a HEAD-check follow-up: are FL's bulk files actually fresh? If frozen for 11 years, FL is effectively a no-bulk state regardless of what its portal claims. |

## Aggregate

- 5 of 8 states (CA, CO, NY, WA, TX) had at least one URL move that would silently break code keying on the old URL.
- 2 states (NY, WA) had structural reorganizations (full regulator successor in NY, statute recodification in WA).
- 0 states added net-new WAF posture; the WAF gap is structural and stable (IL is partial, FL has SPA-shells, WI has SSRS endpoints inaccessible without a browser).
- The `compendium/portal_urls/<ABBR>.json` files now committed at the repo-root locked-contract location should make the *next* re-discovery cheaper — a future agent can diff against the current JSONs to pinpoint what changed.

## Caveat

The Stage 1 subagent prompts included priming context from training-data state-government knowledge ("WA PDC", "RCW 42.17A", "CELG"). The WA agent caught and corrected my wrong RCW citation (I told it 42.17A; it discovered the 29B recodification). That suggests verification is doing its job, but the priming-correction loop is a real failure mode to monitor — if a subagent silently accepts a wrong primer, it could miss a real change. None of the 7 priming hints I gave this session were silently accepted as wrong, but the sample is small.
