# Third-Party Pipelines, Parsers & Normalized Datasets for State-Level Lobbying Data

*Research report 2 of 2. Companion to research-01 (official sources). Identifies non-governmental redistributors/parsers researchers can use instead of or alongside raw official sources.*
*Source: deep-research pass run during the "State lobby disclosure data availability report" session.*

## TL;DR
- Only one true multi-state, actively-maintained, downloadable lobbying redistributor exists: **OpenSecrets** (absorbed National Institute on Money in Politics / FollowTheMoney), covering lobbyist/client registration in all 50 states and spending in 19–20 states.
- **The Accountability Project (TAP)** is the other major aggregator (~20 states of lobbying data) but most lobbying tables are stale (2020–2023 snapshots) and registration-heavy.
- For California, the **California Civic Data Coalition (CCDC)** pipeline is gold-standard — open-source, still releasing (raw-data last released Jul 12 2024; processed-data Apr 24 2025), daily-updated hosted download at Stanford Big Local News — but California-only and code-heavy.
- Most state-specific third-party pipelines are abandoned, code-only, or commercial. Sunlight's Influence Explorer is dead; academic compilations (Strickland Dataverse) are static; commercial platforms (Quorum, FiscalNote, LegiScan, Transparency USA) are paywalled and not raw redistributors.

## Key findings
1. **No comprehensive, normalized, actively-maintained 50-state third-party lobbying dataset exists.** The two genuine multi-state aggregators (OpenSecrets, TAP) both inherit the underlying problem that only ~19 states make meaningful spending data available; the rest provide only registration.
2. **OpenSecrets is the most production-ready multi-state option.** Created by 2021 merger of Center for Responsive Politics + NIMP/FollowTheMoney. Registration for all 50 states; spending for 19 (tool dropdown shows 20 jurisdictions, Montana frozen at 2019). State data last updated Dec 4 2023 — lags recent cycles but normalized and industry-coded.
3. **TAP is the best open, documented redistributor for registration in ~20 states**, with a transparent open-source R pipeline (campfin package, GitHub: irworkshop/accountability_datacleaning) and CSV downloads via AWS. But lobbying tables are mostly one-time 2020–2023 snapshots; registration-heavy.
4. **CCDC remains the single best state-specific pipeline** — but solves only California, and is fundamentally code-you-run plus a hosted bulk download.
5. **Academic datasets (Strickland) are valuable for historical/longitudinal work but static.**
6. Negatives are soft: "none found" = no maintained third-party pipeline surfaced, not proof none exists.

## Summary table

| Pipeline | Org | States | Lobbying? | Coverage | Currency | Access |
|---|---|---|---|---|---|---|
| CAL-ACCESS pipeline (django-calaccess) | California Civic Data Coalition / palewire | CA only | Yes (CF + lobbying) | 2000–present | ACTIVE (raw v5.0.7 Jul 12 2024; processed v1.0.15 Apr 24 2025; hosted daily) | Open-source code + hosted bulk (Big Local News / Internet Archive) |
| OpenSecrets state lobbying (incl. NIMP/FTM) | OpenSecrets | Reg: all 50; Spend: 19–20 | Yes | Reg ~15yr; spend since 2015 | Maintained but lagging (state data Dec 4 2023; MT frozen 2019) | Search/profiles; bulk; legacy FollowTheMoney.org |
| The Accountability Project (TAP) | Investigative Reporting Workshop (American U.) / Center for Public Integrity | ~20 states + federal | Yes (reg + some exp) | Mostly 2008–2023 snapshots | Stale-ish (one-time pulls) | Search UI; CSV (AWS); Datasette; open R pipeline |
| Strickland state lobbying dataset | James Strickland (ASU/FSU/UMich) | All 50 (reg counts) | Yes (reg counts, longitudinal) | ~1980s–2010s | Static research snapshots | Harvard/ASU Dataverse |
| Digital Democracy | CalMatters + Cal Poly IATPP | CA (NY historically) | Lobbyist registrations among many types | 2015–present | Active (CA) | Website + API |
| Influence Explorer | Sunlight Foundation (defunct) | Multi-state (historical) | Yes (aggregated) | Through Q2 2015 | DEAD (org closed Sept 24 2020) | Static archive only |
| Commercial (Quorum, FiscalNote, LegiScan, BillTrack50, LegiStorm, Transparency USA) | Various for-profit | Most/all 50 | Varies (mostly bill tracking) | Current | Active (commercial) | Paid subscription / API |

## Major multi-state aggregators (detail)

### OpenSecrets / NIMP (FollowTheMoney)
- Provenance: 2021 merger of CRP + NIMP. Legacy FollowTheMoney.org still shows state data "current through 2024" but warns it isn't maintained during integration.
- Lobbying coverage: registration ALL 50 states; meaningful SPENDING for 19 states since 2015. Tool dropdown lists 20 jurisdictions; Montana frozen at 2019.
- The 19 spending states (with original coverage start years): CA (2002–), NY (2007–), FL (2007–), TX (2012–), CO (2002–), NJ (2012–), WI (2011–), CT (2012–), MI (2012–), MA (2014–), KY (2012–), AK (2012–), WA (2014–), SC (2012–), ME (2007–), OR (2014–), IA (2014–), MT (2011–2019), VT (2014–). Of these, only seven (CO, MA, MT, NJ, NY, SC, WI) require disclosure of BOTH the specific bill/action AND the position taken.
- Currency: state data last updated Dec 4 2023; federal refreshed quarterly. State lobbying spending hit $1.8B in 2022; exceeded $1.4B in 2023.
- Access: search/profiles on opensecrets.org; bulk downloads (CC BY-NC-SA); legacy FollowTheMoney.org for state campaign finance.
- Quality: normalized, industry/sector-coded (13 sectors, ~100 industries). Caveat: data "as collected" — states variously report client→firm vs client→lobbyist, so cross-state comparison needs care.

### The Accountability Project (TAP)
- Org: Investigative Reporting Workshop, American University; since transferred to Center for Public Integrity. Funded by Reva and David Logan Foundation, Knight Foundation.
- Lobbying state coverage (~20): AL (reg 2008–Jun 2023), CA (reg, Mar 2023), CO (reg, Mar 2023), GA (reg 2006–2022 + 2001–2003 + exp), IL (reg+exp, 2020 pull), IA (reg 2009–2022), LA (exp 2009–2019, 170,718 rec), ME (lobbyist exp 2015–2019, 303 rec), MI (reg, Apr 2023, 8,261 rec), MS (reg 2010–2022), MO (reg+exp 2004–2020), NE (reg, Jul 2023), NJ (reg, Jun 2020), NY (lobbying exp 2011–2018), NC (reg, Mar 2023), PA (lobbying), RI (reg+exp, Feb 2020), SD (registration), WV (reg 2019–2020), WI (exp 2013–2019). Plus federal 1999–2022.
- NOTE: Minnesota lobbying NOT found (TAP holds MN campaign finance only) — corrects an earlier assumption.
- Provenance: each pulls from official state source, often via open-records request. Per-state R "diaries" on GitHub.
- Currency: mostly one-time 2020–2023 snapshots; not on a refresh cadence. Treat as point-in-time.
- Access: search at publicaccountability.org; CSV from AWS S3 (publicaccountability); Datasette SQL; pipeline at github.com/irworkshop/accountability_datacleaning.
- Quality: light normalization (parties, date, amount; ZIP/year; basic strings). Not deep entity resolution.

### California Civic Data Coalition (CCDC)
- What: open-source team (formed 2014, Ben Welsh + Agustín Armendáriz) building Django apps to download/parse/clean/republish CAL-ACCESS (campaign finance + lobbying).
- Currency (verified): ACTIVE. raw-data PyPI v5.0.7 Jul 12 2024; processed-data v1.0.15 Apr 24 2025. Repos now under palewire GitHub account.
- Hosted + code: both. Hosted cleaned bulk downloads update DAILY, now at Big Local News (Stanford), Internet Archive mirror.
- Coverage: CAL-ACCESS electronic filings from Jan 1 2000; ~80 raw tables; parses 99.9998% of records.
- License: MIT (code). Quality: documented data dictionaries; processed flat files. Caveat: underlying CAL-ACCESS is dirty; state excludes some tables from nightly dump.

## Academic / research datasets
- **James Strickland (ASU/FSU/UMich):** most comprehensive scholarly compilation of state lobbyist REGISTRATIONS across all 50 states, multiple decades. Harvard Dataverse (e.g. DOI 10.7910/DVN/QSSIHL; 10.7910/DVN/YQYZ6O; 10.7910/DVN/84FBLB) + ASU Dataverse. Static research snapshots — excellent for longitudinal, not a live pipeline.
- **Other Harvard Dataverse:** "Cities as Lobbyists" (municipal lobbying 1999–2012, DOI 10.7910/DVN/RSD5BV); "The Partisan Logic of City Mobilization" (50-state municipal panel). Static.

## Civic-tech / journalism
- **Digital Democracy (CalMatters + Cal Poly IATPP):** relaunched Mar 2024. CA legislative hearings, bills, votes, contributions, gifts, behests, lobbyist registrations, with API. CA-focused (NY historically). Active for CA.
- **MapLight:** now primarily a govtech vendor building disclosure SYSTEMS (clients incl. CA SOS, Minneapolis, Denver, Maine). Not an open multi-state redistributor anymore.
- **Sunlight Foundation — Influence Explorer (DEAD):** not updated since Q2 2015; org ceased Sept 24 2020. Some assets migrated (Foreign Influence Explorer/Party Time → OpenSecrets; Congress tools → ProPublica). Do not use.
- **ProPublica:** federal lobbying API (Congress API) + state lobbying reporting, but NO normalized multi-state lobbying dataset.
- **Texans for Public Justice:** historical TX lobby-watch reports from TEC filings. Periodic reporting, not a live feed.

## Open-source parsers (code-only, mostly federal)
The-Politico/scraper_senate-lobbying-disclosures; influence-usa/lobbying_federal_domestic; dhess/lobbyists (Senate LD-1/LD-2); shmcminn/analyze-senate-lobbying-disclosures. Useful as patterns, not state redistributors. aachokey/SunScrape scrapes FL campaign finance (not lobbying). spartypkp/open-source-legislation (legislation text, not lobbying) ABANDONED Aug 2024. Open States/Plural standardizes legislative data (bills, legislators, votes) for all 50 states + DC + PR but does NOT cover lobbying disclosure.

## Commercial platforms (note, not raw redistributors)
Quorum, FiscalNote (PolicyNote/CQ/State), Bloomberg Government, LegiScan (API, all 50), BillTrack50, StateScape, TrackBill, LegiStorm, Transparency USA. Paywalled, bill-tracking-oriented, generally no raw bulk normalized lobbying downloads for re-use.

## Per-state index (third-party LOBBYING coverage)
All 50 have OpenSecrets registration; marginal value is greatest where TAP cleaned downloads (or, for CA, CCDC) exist. TAP = Accountability Project; OS reg/OS-spend = OpenSecrets.

- AL — TAP (reg 2008–2023); OS reg
- AK — OS-spend (2012–); OS reg
- AZ — OS reg
- AR — OS reg
- CA — CCDC (best); Digital Democracy; TAP (reg); OS-spend (2002–) — strongest of any state
- CO — TAP (reg 2023); OS-spend (2002–)
- CT — OS-spend (2012–); OS reg
- DE — OS reg
- FL — OS-spend (2007–); OS reg
- GA — TAP (reg 2006–2022 + exp); OS reg
- HI — OS reg
- ID — OS reg
- IL — TAP (reg+exp 2020); OS reg
- IN — OS reg
- IA — TAP (reg 2009–2022); OS-spend (2014–)
- KS — OS reg
- KY — OS-spend (2012–); OS reg
- LA — TAP (exp 2009–2019); OS reg
- ME — TAP (lobbyist exp 2015–2019); OS-spend (2007–); MapLight (govtech system)
- MD — OS reg
- MA — OS-spend (2014–); OS reg (TAP lobbying NOT found)
- MI — TAP (reg 2023); OS-spend (2012–)
- MN — OS reg (TAP lobbying NOT found — campaign finance only)
- MS — TAP (reg 2010–2022); OS reg
- MO — TAP (reg+exp 2004–2020); OS reg
- MT — OS-spend (2011–2019 frozen); OS reg
- NE — TAP (reg 2023); OS reg
- NV — OS reg
- NH — OS reg
- NJ — TAP (reg 2020); OS-spend (2012–)
- NM — OS reg
- NY — TAP (exp 2011–2018); OS-spend (2007–); Digital Democracy (historical)
- NC — TAP (reg 2023); OS reg
- ND — OS reg
- OH — OS reg
- OK — OS reg
- OR — OS-spend (2014–); OS reg
- PA — TAP (lobbying); OS reg
- RI — TAP (reg+exp 2020); OS reg
- SC — OS-spend (2012–); OS reg
- SD — TAP (registration); OS reg
- TN — OS reg
- TX — OS-spend (2012–); OS reg; ProPublica/Texas Tribune reporting; Texans for Public Justice (historical); Transparency USA
- UT — OS reg
- VT — OS-spend (2014–); OS reg (TAP lobbying NOT found)
- VA — OS reg
- WA — OS-spend (2014–); OS reg
- WV — TAP (reg 2019–2020); OS reg
- WI — TAP (exp 2013–2019); OS-spend (2011–)
- WY — OS reg

## Recommendations
Stage 1 (default stack): CA → CCDC hosted bulk (daily, Stanford Big Local News). Multi-state / spending → OpenSecrets (19 spending states + 50-state reg; budget around Dec 2023 lag). Registration for ~20 TAP states → TAP CSVs (verify 2020–2023 vintage).
Stage 2 (specialized): longitudinal/historical → Strickland Dataverse. CA legislative-process linkage → Digital Democracy. Municipal lobbying → Harvard "Cities as Lobbyists."
Stage 3 (most states): only OpenSecrets registration + no cleaned pipeline → go to official source (research-01) and budget own parsing/entity resolution. Commercial platform only if turnkey monitoring needed and budgeted (not raw redistributors).
Benchmarks to change recommendations: if OpenSecrets completes FTM integration + resumes frequent state updates → unambiguous default. If TAP resumes active refresh (watch GitHub commit cadence) → promote from snapshot. A CCDC-style pipeline for TX/NY/FL would leapfrog. Do NOT rely on Influence Explorer/Sunlight (dead) or any project with last commit/release before ~2022 without verifying currency.

## Caveats
- Negatives soft: "none found" reflects search limits, not proof of absence.
- Registration ≠ spending: OpenSecrets "all 50" is registration; only 19–20 have usable spending (function of state law, not the pipelines).
- Cross-state comparability limited (client→firm vs client→lobbyist; TX bands; some omit compensation).
- Currency is the central risk: CCDC (daily) and OpenSecrets federal (quarterly) fresh; OpenSecrets state (Dec 2023) and TAP lobbying (2020–2023) lag. Always check official source for newest filings.
- The "20th" OpenSecrets state is unconfirmed (text says 19, dropdown shows 20; identity beyond the named 19 with MT frozen not verified — check the dropdown directly).
- Commercial-platform capabilities/pricing drawn from vendor/comparison pages, may be marketing-influenced; verify with a trial.
