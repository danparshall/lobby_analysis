# State-Level Lobbying Disclosure Data: 50-State Accessibility Report

*Research report 1 of 2. Scope: U.S. state government lobbying registries only. County/municipal/local lobbying regimes excluded. Current as of June 2026.*
*Source: deep-research pass run during the "State lobby disclosure data availability report" session. ~22 states primary-source verified; remainder flagged unknown (honest not-found, NOT confirmed negatives).*

## TL;DR
- ~A dozen states publish genuine bulk/open lobbying data (NY, WA, IL, CA, CO, TX, OH, NC, FL, WI, CT, MS — verified to varying degrees); the rest range from search-only portals (scrapeable/FOIA-able) to vendor-platform systems needing live-browser verification. Almost no state collects directional support/oppose stance — the most consistent gap nationwide.
- Three separate legal axes: can you get it (download/api/search-only); can you scrape it (the binding instrument is site Terms of Use, NOT robots.txt); can you USE it (WA and MI bar commercial use of lobbyist person-lists — RCW 42.56.070(9); MCL 4.421(3) — surviving even free download).
- High-confidence for ~22 directly-verified states; remainder flagged unknown.

## Key findings
1. **Stance (support/oppose) is the rarest field.** Only Colorado clearly publishes directional positions in a downloadable file (supporting/opposing/amending/monitoring per client per bill, with date ranges). NY, WI, IL, TX collect linkage (principal→bill/subject) but not stance. Most states collect neither bills nor stance — only subject-matter categories.
2. **Lawmaker-keyed data (who is lobbied) is mostly absent.** NY is the strongest exception (publishes "parties lobbied"). Virginia collects named officials on Schedule A/B but search-only. Most states capture officials only as expenditure recipients (gifts/meals). MI, WI, MD, TX, IL maintain no legislator-keyed dataset.
3. **Open-data portals (Socrata/CKAN) are the gold standard:** NY (Open NY), WA (data.wa.gov), IL (data.illinois.gov), CT (data.ct.gov), CO (Colorado Information Marketplace + SOS TXT exports).
4. **Vendor-platform portals need live-browser verification.** MI's MiTN (entellitrak/Tyler) is search-only, no full bulk export; VA is CAPTCHA-gated; GA, PA, MA, OR, MN, CT, MD run JS/ASP.NET search UIs.
5. **Use-restrictions are real.** WA PDC stamps every dataset with a no-commercial-use condition (RCW 42.56.070(9)); MI statute (MCL 4.421(3)) bars commercial sale/use with civil penalty up to $1,000. Both survive free download. [NOTE: moot for the not-for-profit project this research supports.]

## National summary table

| State | Agency | Portal | Bulk exists? Type | Use-restriction / Live-browser flag |
|---|---|---|---|---|
| Alabama | Ethics Commission | ethics.alabama.gov | Annual lobbyist list (PDF); reports search-only | Live-browser: ASP.NET |
| Alaska | APOC | aws.state.ak.us | Unknown/unverified | — |
| Arizona | Secretary of State | apps.azsos.gov | Unknown; likely records request | Unverified |
| Arkansas | Secretary of State | Unknown | Unknown | — |
| California | SOS (CAL-ACCESS) | cal-access.sos.ca.gov | Yes — raw tab-delimited bulk dumps, daily | Aging system, replacement planned |
| Colorado | Secretary of State | sos.state.co.us/pubs/lobby | Yes — daily/hourly TXT exports (incl. positions+bills) + Socrata | Strongest stance case |
| Connecticut | Office of State Ethics | oseapps.ct.gov + data.ct.gov | Yes — Socrata + Excel combined lists | Live-browser: CAPTCHA on OSE app |
| Delaware | Public Integrity Commission | Unknown | Unknown | — |
| Florida | Lobbyist Registration Office / Ethics | floridalobbyist.gov | Yes — registration + delimited compensation + aggregate totals | Legacy leg.state.fl.us page stale (2014) |
| Georgia | Transparency & Campaign Finance Commission | ethics.ga.gov | Search-only (roster export possible) | Live-browser: ASP.NET |
| Hawaii | State Ethics Commission | Unknown | Unknown | — |
| Idaho | Secretary of State | Unknown | Unknown | — |
| Illinois | Secretary of State | ilsos.gov + data.illinois.gov | Yes — daily CSVs + API (CKAN) | — |
| Indiana | Indiana Lobby Registration Commission | Unknown | Unknown | — |
| Iowa | Legislature + Ethics & Campaign Disclosure Board | Unknown (likely bill-position declarations) | Unknown | Verify — candidate for stance data |
| Kansas | SOS / Govt Ethics Commission | Unknown | Unknown | — |
| Kentucky | Legislative Ethics Commission | klec.ky.gov | Unknown | — |
| Louisiana | Ethics Administration Program | ethics.la.gov | Bulk via records request | Unverified |
| Maine | Commission on Govt Ethics | mainecampaignfinance.com | Unknown | — |
| Maryland | State Ethics Commission | lobby-ethics.maryland.gov | Yes — results-grid Export (after search) | Live-browser: new system, GET-param searches |
| Massachusetts | Secretary of the Commonwealth | sec.state.ma.us | Search-only (data 2005–present) | Live-browser: ASP.NET |
| Michigan | Dept of State / Bureau of Elections | mi-boe.entellitrak.com | No full bulk export; curated Excel/PDF only | Use-restriction (MCL 4.421(3)); Live-browser (entellitrak); scraping banned |
| Minnesota | Campaign Finance & Public Disclosure Board | cfb.mn.gov | Current lists; search-only otherwise | Live-browser: JS search |
| Mississippi | Secretary of State | sos.ms.gov | Yes — lobbyists + clients files (2010–2022) | — |
| Missouri | Ethics Commission | mec.mo.gov | Unknown | — |
| Montana | Commissioner of Political Practices | politicalpractices.mt.gov | Likely paper-based after 2019 | Probable structural negative — verify |
| Nebraska | Accountability & Disclosure Commission | nadc.nebraska.gov | Unknown | — |
| Nevada | Legislative Counsel Bureau | lobbyist.leg.state.nv.us | Unknown | Verify — searchable tracker |
| New Hampshire | Secretary of State | Unknown | Unknown | — |
| New Jersey | Election Law Enforcement Commission | elec.nj.gov | Reports (PDF) + summary data (aggregate) | — |
| New Mexico | Secretary of State | Unknown | Unknown | — |
| New York | COELIG | ethics.ny.gov + Open NY | Yes — Socrata, 6 datasets, 2019–present, download+API | Gold standard |
| North Carolina | Secretary of State | sosnc.gov | Yes — free Excel/Text (all terms) + paid subscription | Interactive search prohibits scripting; downloads provided |
| North Dakota | Secretary of State | sos.nd.gov | Unknown | — |
| Ohio | JLEC (OLAC) | jlec-olig.state.oh.us | Yes — daily CSV (agents/employers); activity search-only | — |
| Oklahoma | Ethics Commission | Unknown | Unknown | — |
| Oregon | Govt Ethics Commission | oregon.gov/ogec | Public records lookup (EFS) | Live-browser: apps.oregon.gov |
| Pennsylvania | Department of State | pa.gov | Search-only | Live-browser; HB1175 mandated e-filing |
| Rhode Island | Secretary of State | sos.ri.gov | Unknown | Verify — known lobby tracker |
| South Carolina | State Ethics Commission | Unknown | Unknown | — |
| South Dakota | Secretary of State | sos.sd.gov | Unknown | — |
| Tennessee | Bureau of Ethics & Campaign Finance | Unknown | Unknown | — |
| Texas | Texas Ethics Commission | ethics.state.tx.us | Yes — Excel+PDF registration lists + CSV activities DB | Compensation in coded bands |
| Utah | Lieutenant Governor | Unknown | Unknown | Verify — searchable reports |
| Vermont | Secretary of State | sos.vermont.gov | Unknown | Verify — downloads likely |
| Virginia | Conflict of Interest & Ethics Advisory Council | ethicssearch.dls.virginia.gov | Unknown | Live-browser: CAPTCHA-gated |
| Washington | Public Disclosure Commission | pdc.wa.gov + data.wa.gov | Yes — Socrata, daily, download+API | No-commercial-use (RCW 42.56.070(9)) |
| West Virginia | Ethics Commission | Unknown | Unknown | — |
| Wisconsin | Ethics Commission | lobbying.wi.gov | Yes — Excel/PDF directories; expenditure download aggregate only | — |
| Wyoming | Secretary of State | Unknown | Unknown | — |

## Verified-state detail (per-category access × granularity)

### New York — COELIG / Open NY (Socrata). Legal: Legislative Law Art. 1-A. ~278M records, 6 datasets, 2019–present, data dictionaries, queryable+downloadable+API.
| Category | access | granularity |
|---|---|---|
| Principals | open-data | directory + transactional |
| Lobbyists | open-data | directory |
| Lawmakers | open-data | aggregate ("parties lobbied") |
| Bills | open-data | transactional (real bill IDs) |
| Activity & expenditure | open-data | transactional (compensation + itemized expenses) |
| Positions — stance | none-collected | n-a |
| Positions — linkage | open-data | transactional (lobbyist→bill→client) |
Scraping: silent; API designed for it. Use-restriction: none found. Confidence: HIGH.

### Washington — PDC + data.wa.gov (Socrata). Legal: RCW 42.17A. Daily, download+API.
| Category | access | granularity |
|---|---|---|
| Principals (employers) | open-data | directory |
| Lobbyists | open-data | directory |
| Lawmakers | none-collected | n-a |
| Bills | unknown | (subject/agency only) |
| Activity & expenditure | open-data | transactional (compensation/expenses by source) |
| Positions — stance | none-collected | n-a |
| Positions — linkage | open-data | transactional (employer↔agent) |
USE-RESTRICTION CRITICAL: every dataset carries the no-commercial-use condition (RCW 42.56.070(9) and AGO 1975 No. 15). Confidence: HIGH.

### Illinois — SOS + data.illinois.gov (CKAN). Legal: 25 ILCS 170. Daily CSVs + API.
| Category | access | granularity |
|---|---|---|
| Principals | open-data | directory + transactional (client data) |
| Lobbyists | open-data | directory |
| Lawmakers | none-collected | n-a |
| Bills | none-collected | n-a (subject matter + agency intent, not bill numbers) |
| Activity & expenditure | search-only | transactional (bulk exp via records request) |
| Positions — stance | none-collected | n-a |
| Positions — linkage | open-data | transactional (entity→agency, entity→subject) |
Confidence: HIGH.

### California — SOS (CAL-ACCESS). Legal: Political Reform Act (Gov. Code §81000 et seq.). Raw tab-delimited bulk dumps, daily, data dictionaries.
| Category | access | granularity |
|---|---|---|
| Principals | download | directory + transactional |
| Lobbyists | download | directory + transactional |
| Lawmakers | none-collected | n-a |
| Bills | none-collected | n-a (subject-matter) |
| Activity & expenditure | download | transactional |
| Positions — stance | none-collected | n-a |
| Positions — linkage | download | transactional (lobbyist↔employer↔payments) |
CAL-ACCESS is aging/slated for replacement; California Civic Data Coalition publishes cleaned parses. Confidence: HIGH.

### Texas — Texas Ethics Commission. Legal: Gov. Code ch. 305. Excel+PDF lists + CSV activities DB; exp back to 1993; compensation in coded bands.
| Category | access | granularity |
|---|---|---|
| Principals | download | directory + transactional |
| Lobbyists | download | directory + transactional |
| Lawmakers | none-collected | n-a (gov-recipient list for expenditures only) |
| Bills | none-collected | n-a (subject-matter, not bill numbers) |
| Activity & expenditure | download | transactional (CSV) + aggregate; compensation banded |
| Positions — stance | none-collected | n-a |
| Positions — linkage | download | transactional (lobbyist→client→subject) |
Confidence: HIGH.

### Ohio — JLEC/OLAC. Legal: ORC 101.70–.79 & 121.60–.69. Daily downloadable agent/employer lists.
| Category | access | granularity |
|---|---|---|
| Principals (employers) | download | directory |
| Lobbyists (agents) | download | directory |
| Lawmakers | none-collected | n-a |
| Bills | none-collected | n-a |
| Activity & expenditure | search-only | transactional (viewable, not bulk-exported) |
| Positions — stance | none-collected | n-a |
| Positions — linkage | search-only | transactional (agent↔employer; subject areas) |
Confidence: HIGH.

### Wisconsin — Ethics Commission "Eye on Lobbying." Legal: Wis. Stat. ch. 13 subch. III. Data back to 2003–2004.
| Category | access | granularity |
|---|---|---|
| Principals | download | directory (Generate Excel/PDF) |
| Lobbyists | download | directory |
| Lawmakers | none-collected | n-a |
| Bills | search-only | transactional (which orgs lobbied each bill/budget subject/rule/topic) |
| Activity & expenditure | download (aggregate) / search-only (itemized) | aggregate download; itemized search-only |
| Positions — stance | none-collected | n-a (subject/topic coded) |
| Positions — linkage | search-only | transactional |
Confidence: HIGH.

### North Carolina — SOS, Lobbying Compliance Division. Legal: N.C.G.S. ch. 120C. Free Excel/Text (current + historical) + paid Data Subscription Service.
| Category | access | granularity |
|---|---|---|
| Principals | download | directory (free Excel/Text) |
| Lobbyists | download | directory |
| Activity & expenditure | download + paid | transactional |
| Bills / Positions — stance | none-collected | n-a (subject-area) |
| Positions — linkage | download | transactional |
Scraping: interactive search prohibits scripted access, BUT bulk downloads provided (not a blocker). Confidence: HIGH.

### Florida — Lobbyist Registration Office (Legislature) + Commission on Ethics. Legal: Fla. Stat. §11.045 & §112.3215. Use floridalobbyist.gov (active); leg.state.fl.us is stale (2014).
| Category | access | granularity |
|---|---|---|
| Principals | download | directory |
| Lobbyists | download | directory |
| Activity & expenditure | download | transactional (delimited compensation, quarterly) + aggregate totals |
| Lawmakers / Bills / Positions — stance | none-collected | n-a |
| Positions — linkage | download | transactional (firm→principal→compensation) |
Compensation reported in ranges. Confidence: HIGH.

### Maryland — State Ethics Commission. Portal: lobby-ethics.maryland.gov (new). Legal: Md. Gen. Provisions §5-701–5-704. Export control appears after running a search; GET-param searchable; many report types (gifts, contributions, business transactions).
| Category | access | granularity |
|---|---|---|
| Principals (employers) | search-only → export | directory |
| Lobbyists | search-only → export | directory |
| Lawmakers | none-collected | n-a |
| Bills | none-collected | n-a |
| Activity & expenditure | search-only → export | transactional (compensation + expenditures) |
| Positions — stance | none-collected | n-a |
| Positions — linkage | search-only | transactional |
Live-browser flag: YES. STATE regime only (Montgomery County etc. excluded). Confidence: HIGH.

### Michigan — Dept of State / Bureau of Elections; MiTN (mi-boe.entellitrak.com, Tyler/entellitrak), replaced E-Lobby Dec 2024. Legal: Lobby Registration Act, PA 472 of 1978 (MCL 4.411 et seq.).
| Category | access | granularity |
|---|---|---|
| Principals (employers) | search-only | directory |
| Lobbyists & agents | search-only | directory |
| Lawmakers | none-collected | n-a (officials appear only as expenditure recipients) |
| Bills | none-collected (confirmed) | n-a (no bill field in forms or MiTN schema) |
| Activity & expenditure | search-only | transactional (semiannual LR305; itemized LR404); one curated Itemized-expenditures-2024.xlsx on SOS site |
| Positions — stance | none-collected | n-a |
| Positions — linkage | search-only | (lobbyist↔employer) |
SCRAPING EXPLICITLY PROHIBITED (michigan.gov Terms of Use bars automated means/scripts/crawlers/scrapers). USE-RESTRICTION: MCL 4.421(3) bars commercial sale/use, civil penalty up to $1,000. data_request_channel: FinancialDisclosure@Michigan.gov or FOIA via MDOS-FOIA@Michigan.gov. Live-browser flag: YES. Confidence: HIGH.

### Colorado — Secretary of State. Legal: C.R.S. §24-6-301 et seq. THE strongest "positions" case. Hosts "Client positions - subjects and bills" TXT that updates hourly + 5-year-history TXT; Socrata presence (CIM).
| Category | access | granularity |
|---|---|---|
| Principals (clients) | download | directory (TXT + PDF) |
| Lobbyists | download | directory |
| Lawmakers | none-collected | n-a |
| Bills | download | transactional (per-bill client positions) |
| Activity & expenditure | download | transactional (monthly income/expenditures) + aggregate |
| Positions — stance | download | transactional (support/oppose/amend/monitor) |
| Positions — linkage | download | transactional |
Confidence: HIGH.

### Connecticut — Office of State Ethics + data.ct.gov (Socrata). Legal: Conn. Gen. Stat. ch. 10, Part II. Socrata datasets per biennium (CSV/JSON/XML/API) + large Excel "Combined Lobbyist List."
- Principals/Lobbyists (communicators): open-data/directory + Excel. Activity & expenditure: search-only → PDF/transactional (quarterly financial reports). Bills/issues: collected (searchable by issue); bill-level unconfirmed. Lawmakers: none-collected. Stance: unknown. Linkage: open-data + search-only/transactional. Live-browser: CAPTCHA on oseapps. Confidence: MEDIUM-HIGH.

### Mississippi — Secretary of State. Legal: Miss. Code §5-8-1 et seq. SOS makes lobbying registration available in two downloadable files (lobbyists, clients), 2010–2022.
- Principals/Lobbyists: download/directory. Activity & expenditure: unknown (likely search-only/reports). Lawmakers/Bills/stance: none-collected. Linkage: download/directory. Confidence: MEDIUM (via aggregator + SOS).

### Additional medium-confidence verified states
- **Alabama** — Ethics Commission; Ala. Code Title 36 ch. 25. Annual lobbyist list PDF + ASP.NET search. Subject-matter not bills. Live-browser: yes. TAP holds AL lobbying 2008–June 2023.
- **Massachusetts** — Secretary of the Commonwealth; M.G.L. ch. 3 §§39–50. Searchable 2005–present incl. activity/bill + contributions. Bulk export unconfirmed. Live-browser: yes.
- **New Jersey** — ELEC; N.J.S.A. 52:13C-18 et seq. Annual financial reports + quarterly summaries; bulk transactional download not confirmed (PDF + aggregate). 
- **Oregon** — Govt Ethics Commission; ORS 171.725–.785. Quarterly expenditure reports, search-only. Bulk unconfirmed. Live-browser: apps.oregon.gov.
- **Georgia** — Transparency & Campaign Finance Commission; O.C.G.A. §21-5-70 et seq. Roster + reports searchable. Live-browser: ASP.NET.
- **Virginia** — Conflict of Interest & Ethics Advisory Council; Va. Code §2.2-418 to -432. Schedules A/B NAME officials lobbied (search-only, not bulk). Live-browser: CAPTCHA-gated.
- **Minnesota** — Campaign Finance & Public Disclosure Board; Minn. Stat. ch. 10A. Disbursement reports + current lists. Subjects only, no bills. Live-browser: JS search.
- **Pennsylvania** — Dept of State; 65 Pa.C.S. ch. 13A. Searchable DB + quarterly expense reports. Bulk unconfirmed. Live-browser.

## Unverified states (honest "unknown" — NOT confirmed negatives)
AK, AZ, AR, DE, HI, ID, IN, IA, KS, KY, LA, ME, MO, MT, NE, NV, NH, NM, ND, OK, RI, SC, SD, TN, UT, VT, WV, WY. For each, the best-known responsible agency/statute is listed in the summary table; ALL access/granularity axes are unknown pending live verification. Notable flags: Iowa (possible bill-level position declarations — second stance candidate after CO); Rhode Island, Vermont, Utah, Nevada (known searchable trackers likely offering exports); Montana (probable post-2019 paper-only dead-end).

## Caveats
- Confidence tiered: ~22 states primary-source verified; ~28 unknown (do not treat as negatives).
- "None-collected" backed by evidence only where stated (firmest for MI, TX, WI, IL, CA). Elsewhere, absence in a search UI is suggestive not dispositive.
- Legal citations at chapter/section granularity; verify exact section numbers before legal reliance. NY's COELIG replaced JCOPE (2022); MD and MI migrated platforms (2024). MI commercial-use bar is §11(3) = MCL 4.421(3), though the Act starts at MCL 4.411.
- robots.txt vs Terms of Use: the binding instrument is the Terms of Use. "Silent" = no prohibiting clause found, not a guarantee none exists. MI is the only confirmed explicit automated-access prohibition.
