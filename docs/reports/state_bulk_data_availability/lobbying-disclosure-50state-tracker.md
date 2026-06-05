# State Lobbying Disclosure — 50-State Access Tracker (Tier-1)

**Compiled:** 2026-06-04 · **Scope:** State-level only
**Method:** Tier-1 = ~1 targeted search per state. Captures portal, whether bulk exists, legal basis, and notes. **Does NOT reliably establish granularity or per-category coverage** — that requires the deeper pass (as done for the 6 sample states in the companion file `lobbying-disclosure-sample.md`).

## Bulk-availability legend
- **open-data** = full datasets on a Socrata/CKAN-style open-data portal (download + usually API), strongest case
- **download** = downloadable files (CSV/Excel/Text/PDF) on the agency site
- **search-only** = searchable DB, no bulk export found at tier-1 (may exist deeper; routable by scrape/request)
- **paid** = bulk gated behind a paid subscription
- **unclear** = tier-1 inconclusive; needs deeper check
- **[!use]** = data carries a use-restriction (e.g. no commercial use) even if freely downloadable

---

## Completed (with verification depth noted)

| State | Portal | Bulk | Legal basis | Notes |
|---|---|---|---|---|
| **OH** [LIVE] | OLAC (jlec-olig.state.oh.us) | download | ORC 101.70–.79; 121.60–.69 | Daily .csv for agents & employers. Activity/expend search-only. |
| **WI** [LIVE] | lobbying.wi.gov | download (directory) + search (activity) | Wis. Stat. ch. 13 III | Principals/lobbyists Excel/PDF. Expenditure download = aggregate only; itemized via search. No lawmaker/stance data. |
| **MI** [BLOCKED] | MiTN (mi-boe.entellitrak.com) | unclear | MCL 4.411 et seq. | Portal not on allowlist; not verified. 3rd-party bulk redistribution exists. |
| **NC** [LIVE] | sosnc.gov/divisions/lobbying | download (free Excel/Text) + paid subscription | N.C.G.S. ch. 120C | Free current+historical files. Scripted access to search prohibited (but downloads provided). |
| **FL** [LIVE] | floridalobbyist.gov | download (free) | Fla. Stat. 11.045–.062; 112.3215 | Active portal has registration + delimited compensation (likely transactional) + aggregate totals. Legacy leg.state.fl.us page stale (2014). |
| **MD** [LIVE] | lobby-ethics.maryland.gov | download (via results Export) | Md. Gen. Prov. 5-701–704 | Export appears after running a search; GET-param searchable. Many report types (gifts, contributions). No bill# or stance data. |
| **CA** [SRCH] | CAL-ACCESS (cal-access.sos.ca.gov) | download (raw tab-delimited, daily) | Political Reform Act (Gov. Code 81000 et seq.) | Full raw DB dumps incl. lobbying; data dictionaries; no SOS tech support. Unredacted address lists via Data Processing Request. |
| **TX** [SRCH] | Texas Ethics Commission (ethics.state.tx.us) | download (PDF + Excel) | Gov. Code ch. 305 | Registration lists in Excel/PDF, multiple sorts, by year-range; compensation coded in bands. |
| **NY** [SRCH] | COELIG + Open NY (ethics.ny.gov) | open-data (+API) | Legislative Law 1-A; Exec. Order 95 | 6 lobbying datasets on Open NY, 2019–present, data dictionaries, queryable+downloadable+API. Among the best. |
| **PA** [SRCH] | pa.gov/.../lobbying-disclosure | search-only (+ PDF annual reports) | 65 Pa.C.S. ch. 13A (Act 2 of 2018) | Searchable DB; downloadable annual report PDFs; no obvious bulk dataset at tier-1. |
| **IL** [SRCH] | ilsos.gov + data.illinois.gov | open-data (daily CSV) | Lobbyist Registration Act, 25 ILCS 170 | Daily CSVs: client data, intent (agency), intent (subject), non-compliance, consultants. |
| **MA** [SRCH] | sec.state.ma.us/lobbyistpublicsearch | search-only (rich) | M.G.L. ch. 3 §§39–50 | Searchable 2005–present incl. activity/bill + contributions. No bulk dataset found at tier-1. |
| **WA** [SRCH] | PDC + data.wa.gov | open-data (+API) **[!use]** | RCW 42.17A; WAC Title 390 | Multiple daily lobbyist datasets. **CONDITION OF RELEASE: no commercial use** of person-lists (RCW 42.56.070(9)). |

---

## Remaining (not yet researched) — 37 states

AK, AZ, AR, CO, CT, DE, GA, HI, ID, IN, IA, KS, KY, LA, ME, MN, MS, MO, MT, NE, NV, NH, NJ, NM, ND, OK, OR, RI, SC, SD, TN, UT, VT, VA, WV, WY

*(50 total − 13 above = 37 remaining.)*

---

## Cross-cutting findings so far

1. **A third legal axis is now confirmed real: use-restrictions.** WA freely publishes downloadable lobbyist data but **statutorily bars commercial use** of the person-lists. "Downloadable" ≠ "unrestricted." Added `[!use]` flag. For policy work this matters; watch for it in other states (several PDC-style agencies carry similar conditions).

2. **Open-data portals are the high-value tier** (NY, IL, WA, CA-style raw dumps). Where a state is on Socrata/CKAN, you typically get download + API + data dictionary + daily refresh — no scraping question at all.

3. **"Bulk exists" still says nothing about granularity at tier-1.** TX bulk = registration directory (Excel), not necessarily itemized activity. NY/WA/IL bulk = transactional. The companion sample file shows why the access×granularity split matters; tier-1 cannot fill it.

4. **MI remains the one hard block** — vendor portal off the allowlist. Needs a one-time domain authorization to verify.
