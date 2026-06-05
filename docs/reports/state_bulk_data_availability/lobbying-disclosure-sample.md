# State Lobbying Disclosure Data — Access & Granularity Report

**Sample build (6 states): OH, WI, MI, NC, FL, MD**
**Compiled:** 2026-06-04 · **Scope:** State-level only (county/municipal regimes excluded)
**Status:** Sample for review before scaling to all 50 states

---

## Schema

Each state is assessed for **six data categories** — *principals, lobbyists, lawmakers, bills, activity & expenditure, positions* — across **two independent axes**, plus state-level access facts.

### Per-category fields

**`access`** — *how* you can obtain the data:
| Value | Meaning |
|---|---|
| `download` | Official downloadable file (CSV/Excel/PDF/delimited) |
| `api` | Programmatic API endpoint |
| `search-only` | Viewable via search UI; no export. Routable by scraping or records request |
| `none-collected` | The state does not collect this data. **Dead end — no method recovers it** |
| `unknown` | Not yet verified |

**`granularity`** — *what you get* when you obtain it:
| Value | Meaning |
|---|---|
| `transactional` | Row-level / itemized records (who, what, when, how much) |
| `aggregate` | Pre-summed totals only |
| `directory` | Entity listing (names, registrations, contact/interest fields) |
| `n-a` | Not applicable (data not collected) |

**`rollup`** — derived skim value combining the two:
| Rollup | Condition | Analytical usability |
|---|---|---|
| **bulk-transactional** | download + transactional | Best — analyze directly |
| **bulk-directory/aggregate** | download + directory or aggregate | Usable but limited |
| **search-transactional** | search-only + transactional | Good data, requires extraction effort |
| **search-thin** | search-only + aggregate/directory | Extraction effort for limited payoff |
| **dead-end** | none-collected | Not obtainable by any means |
| **unknown** | unverified | — |

### Key distinction this schema enforces
`search-only` (data exists, just not exported -> routable via scrape/request) is **categorically different** from `none-collected` (state never gathered it -> no method helps). The old single scale collapsed both into "not available." It also separates `download`+`aggregate` (visible but analytically thin) from `download`+`transactional` (the real prize), which a one-value scale cannot represent.

---

## State-level access facts (apply to all categories)

| State | Portal | legal_basis | scraping_status | data_request_channel |
|---|---|---|---|---|
| **OH** | OLAC — jlec-olig.state.oh.us | ORC SS101.70-101.79; SS121.60-121.69 | silent | JLEC public-records request |
| **WI** | lobbying.wi.gov | Wis. Stat. ch. 13 subch. III | silent | Ethics Commission records request |
| **MI** | MiTN — mi-boe.entellitrak.com | MCL S4.411 et seq. | silent | Bureau of Elections |
| **NC** | sosnc.gov/divisions/lobbying | N.C.G.S. ch. 120C | **prohibited-with-alternative** (paid Data Subscription) | SOS Communications/Public Info Office |
| **FL** | floridalobbyist.gov | Fla. Stat. SS11.045-11.062; S112.3215 | moot (free bulk provided) | Lobbyist Registration Office |
| **MD** | lobby-ethics.maryland.gov | Md. Gen. Prov. SS5-701-5-704 | silent | State Ethics Commission |

*Reminder: `scraping_status: silent` = no prohibiting clause found in surfaced materials; the binding instrument is each site's Terms of Use, not robots.txt. Under the operating rule (mandated + openly published + no TOS prohibition -> legal & ethical), all silent states default to acceptable, pending a positive TOS check during the full run.*

---

## Per-category matrix

Legend for verification: **[LIVE]** = confirmed via direct portal inspection · **[SRCH]** = from web search only, not yet portal-verified.

### Wisconsin (WI) — [LIVE], fully mapped

| Category | access | granularity | rollup |
|---|---|---|---|
| Principals | `download` | `directory` | bulk-directory |
| Lobbyists | `download` | `directory` | bulk-directory |
| Lawmakers | `none-collected` | `n-a` | **dead-end** |
| Bills | `search-only` | `transactional` | search-transactional |
| Activity & expenditure | `download` **and** `search-only` | `aggregate` (download) / `transactional` (search) | **split: bulk-aggregate + search-transactional** |
| Positions | `none-collected` (stance) | `n-a` | **dead-end** (see note) |

**WI notes (the analytically important caveats):**
- *Principals & lobbyists:* free Excel/PDF full-directory export, no login. Endpoint pattern `.../ReportExport?outRpt=Excel`. 974 principals this session.
- *Activity & expenditure — the split case:* the **downloadable** export is **aggregate only** (total expenditures by principal / by hours / by dollars). Itemized/transactional activity exists but only through the search UI and per-principal reports — not in any downloadable file. This is exactly the case the single-value scale could not represent.
- *Bills:* 15,951 legislative matters (bills, budget subjects, admin rules, topics) searchable; **no export on the results grid** -> scrape or records request.
- *Positions:* WI records *that* a principal registered on a matter + notification/communication dates, but **does not record a support/oppose/neutral stance**. So directional "position" is `none-collected`. (If your schema defines "position" merely as principal-matter linkage, that IS collected — it's `search-only`/`transactional` via the per-matter detail pages, "Print" link only. Flagging the definitional fork.)
- *Lawmakers:* WI's registry has no legislator-keyed dataset. Closest is "State Agency Legislative Liaisons" (agency staff directory), which is not lawmakers.

### Ohio (OH) — [LIVE], corrected from search pass

| Category | access | granularity | rollup |
|---|---|---|---|
| Principals (employers) | `download` (.csv, daily) | `directory` | bulk-directory |
| Lobbyists (agents) | `download` (.csv, daily) | `directory` | bulk-directory |
| Lawmakers | `unknown` | `unknown` | unknown |
| Bills | `unknown` | `unknown` | unknown |
| Activity & expenditure | `search-only` (expenditure searches) | `transactional` | search-transactional |
| Positions | `unknown` | `unknown` | unknown |

**OH notes [LIVE] — search-pass assumption corrected:**
- I previously guessed the daily Agent/Employer lists were HTML report views (`search-only`). **Wrong.** At `…/olac/Reports/AgentEmployerLists` they are explicit **".csv Download"** links — "Listed by Agent (.csv Download)" and "Listed by Employer (.csv Download)", updated daily, covering all currently registered agents/lobbyists and employers (private + public sector). So OH principals & lobbyists = `download`/`directory`, not search-only.
- Activity & expenditure remains via OLAC expenditure searches (transactional, search-only) — not re-verified this pass.
- Note: OH's CSV lists are *current registrants* (a snapshot directory), not historical/time-series.

### Michigan (MI) — [SRCH], recently migrated to MiTN — high priority for LIVE check

| Category | access | granularity | rollup |
|---|---|---|---|
| Principals | `unknown` | `directory` | unknown |
| Lobbyists | `unknown` | `directory` | unknown |
| Lawmakers | `unknown` | `unknown` | unknown |
| Bills | `unknown` | `unknown` | unknown |
| Activity & expenditure | `search-only` | `transactional` | search-transactional |
| Positions | `unknown` | `unknown` | unknown |
*Third-party (Accountability Project) redistributes MI lobbying data in bulk, implying an obtainable source, but the official channel is unconfirmed. Platform recently changed (entellitrak/Tyler backend) — any documented export path is suspect until verified live.

### North Carolina (NC) — [LIVE] download page confirmed

| Category | access | granularity | rollup |
|---|---|---|---|
| Principals | `download` (free Excel/Text) | `directory` (likely) | bulk-directory |
| Lobbyists | `download` (free Excel/Text) | `directory` (likely) | bulk-directory |
| Lawmakers | `unknown` | `unknown` | unknown |
| Bills | `unknown` | `unknown` | unknown |
| Activity & expenditure | `download` (paid subscription) / free file scope TBD | `transactional` (likely) | needs granularity check |
| Positions | `unknown` | `unknown` | unknown |

**NC notes [LIVE]:**
- **Free bulk download confirmed** at `sosnc.gov/online_services/lobbying/download`: four files — **2026 (Excel)**, **2026 (Text)**, **All previous terms (Excel)**, **All previous terms (Text)**. Current year + full history, two formats. This is *in addition to* the paid Data Subscription Service noted earlier; basic registration data is free.
- Download links are JS-triggered (`void(0)` handlers) — **not clicked** (would initiate a file download; held for user confirmation, and no screen access to handle save dialog). **What the files contain (which categories, granularity) is therefore unconfirmed** — needs one file opened to verify columns. Marked `(likely)` accordingly.
- Reconciles with the earlier finding that NC **prohibits scripted access to the interactive search** but provides sanctioned bulk paths. The free download makes scraping doubly unnecessary for registration data.

### Florida (FL) — [LIVE], with a significant caveat

| Category | access | granularity | rollup |
|---|---|---|---|
| Principals | `download` (free) — **but see staleness flag** | `directory`/`transactional` | bulk — currency uncertain |
| Lobbyists | `download` (free) — **but see staleness flag** | `directory`/`transactional` | bulk — currency uncertain |
| Lawmakers | `unknown` | `unknown` | unknown |
| Bills | `unknown` | `unknown` | unknown |
| Activity & expenditure | `download` (delimited compensation data) — verify currency | `unknown` | needs LIVE check |
| Positions | `unknown` | `unknown` | unknown |

**FL notes [LIVE] — caveat partly resolved:**
- **Two FL download locations exist.** (1) Legacy `leg.state.fl.us` page: free tab-delimited Legislative/Executive lobbyist files, but stamped **"Last Update: 12/31/2014"** despite "updated daily" text — almost certainly a stale legacy page. (2) **Active portal `floridalobbyist.gov` → Other Resources → Downloads** carries: *Download Formatted Lobbyist Registration Data*, *Download Delimited Compensation Report Data*, *2006 Compensation Report Archives*, and *Compensation Report **Aggregate** Totals*.
- **Granularity inference:** the active portal lists "Aggregate Totals" as a *separate* file from "Delimited Compensation Report Data" — strongly implying the delimited compensation file is **transactional** (row-level), with aggregate offered as a distinct rollup. This is the good case for analysis.
- The active-portal download links are base64 data-URI/handler links (masked by the extension) that likely trigger direct downloads — **not clicked** (download action, held for user; no screen to handle save). So the active files' *timestamps* aren't directly visible; currency is **strongly likely current** (active portal, live registration counts seen earlier) but not positively confirmed.
- **Net:** earlier "best case" rating is largely restored *if* downloads come from `floridalobbyist.gov`, not the 2014 legacy page. Use the active portal. Confirm currency by opening one file when at a screen.

### Maryland (MD) — [LIVE], registration layer mapped; others inferred from report-type menu

| Category | access | granularity | rollup |
|---|---|---|---|
| Principals (employers) | `download` (via results "Export") | `directory`/`transactional` | bulk-transactional |
| Lobbyists (registrants) | `download` (via results "Export") | `directory`/`transactional` | bulk-transactional |
| Lawmakers | `unknown` | `unknown` | unknown |
| Bills | `none-collected`? (no bill-keyed report type; subject-matter taxonomy instead) | `n-a`? | likely dead-end — verify |
| Activity & expenditure | `download` (Activity Reports type + Export) | `transactional` | bulk-transactional (verify granularity of export) |
| Positions | `none-collected` (stance); subject-matter coded instead | `n-a` | dead-end |

**MD notes [LIVE]:**
- Portal `lobby-ethics.maryland.gov/public_access` is JS-rendered (text extraction shows only a placeholder; had to inspect DOM + run a search to see structure).
- **Export confirmed:** running a Lobbying Registrations search (Nov 2025–Oct 2026) produced a results grid with columns ID / Lobbyist-Registrant / Organization-Firm / Employer / Registration Period, **and an "Export" control** on the results. So MD data IS downloadable — but only *after* executing a search, not from a standing bulk-file page. Access = `download`, gated behind a query.
- **Search params ride in the URL query string** (GET, not POST) — so searches are trivially parameterizable/automatable across report types and years.
- **MD collects more report types than WI**, which expands category coverage: report-type menu includes Lobbying Registrations, Activity Reports, Event Reports, Personal Disclosures, Board & Commission Disclosures, Political Contributions, Business Transactions, and four Gift Report types. Activity & expenditure and gift/contribution data are first-class here.
- **Bills:** MD organizes by an 80-entry *subject-matter taxonomy* (Agriculture, Energy, Taxes-Income, etc.), not by individual bill numbers — so a bill-keyed dataset appears absent. Flag to verify, but likely `none-collected` in the bill-number sense.
- **Positions:** as with WI, no support/oppose stance field surfaced; lobbying is coded by subject matter. Directional position = `none-collected`.
- State regime only — Montgomery County etc. are separate and excluded.

---

## What the WI worked example demonstrates for the 50-state run

1. **The two-field schema earns its complexity on the very first state.** WI's activity/expenditure row is a genuine split (downloadable aggregate + searchable transactional) that a single scale would have mislabeled. Expect this pattern wherever a state publishes summary reports but gates itemized data behind search.

2. **`none-collected` vs `search-only` is a real, frequent distinction.** WI has two dead-ends (lawmakers, directional positions) that are NOT routable — versus bills, which are search-only and fully routable. Lumping these as "not available" would have overstated the dead-ends and understated the routable gaps.

3. **Category definitions need pinning before the run.** "Positions" forked into stance (not collected in WI) vs principal-matter linkage (collected, searchable). Decide the canonical definition now or the 50-state column won't be comparable.

4. **Most [SRCH] rows are honestly `unknown`, not "No."** Search can confirm a download exists but rarely confirms its granularity or rules out an export. The unknowns above are real and need LIVE portal checks (MI and MD most urgent — both newly migrated).
