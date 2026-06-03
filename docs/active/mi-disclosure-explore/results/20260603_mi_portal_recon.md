# MI Portal Recon (Phase 0) — desk recon results

**Date:** 2026-06-03
**Branch:** `mi-disclosure-explore`
**Plan:** [`../plans/mi_data_acquisition.md`](../plans/mi_data_acquisition.md) Phase 0
**Method:** web search + automated fetch (desk recon). **Live-browser portion deferred** —
see "Remaining (needs a browser)" below.

## Headline

**There is no reliable public bulk download for 2025 Michigan lobby data.** The acquisition
primitive is therefore **drive/scrape the MiTN (entellitrak) app**, not download. Two
sub-options remain to be chosen in a live browser session (see end).

## The two Michigan lobby systems (and why only one has 2025)

| System | Host | Era / coverage | Bulk data? | Holds 2025? |
|---|---|---|---|---|
| **MiTN** (Michigan Transparency Network) | `mi-boe.entellitrak.com/etk-mi-boe-prod/` | Launched **March 2024**; E-Lobby data migrated in | **No** dedicated bulk lobby download. JS/AJAX search app with a per-result "export to spreadsheet" feature. | **Yes** ← our target |
| **Legacy NIC/Tyler** | `miboecfr.nicusa.com` (search) / `miboecfr.nictusa.com` (dumps) | Pre-2024; relationship data **1982–2023** | **Yes** — `cfr/dumpdata/.../mi_lobby.sh` bulk dump (8,261 lobbyist↔principal records, last updated **2023-04-09**) | **No** (superseded by MiTN) |

**Implication for our 2025-only target (a2):** the legacy bulk dump is the wrong vintage and
the host is **decaying** (`nictusa.com` returned an **expired TLS certificate**; the lobby
CGI endpoints **timed out** repeatedly). It is useful only as a historical cross-check /
schema reference, **not** as a 2025 source. 2025 lives only in MiTN, which has no bulk export.

## Q-by-Q (Phase 0 questions)

1. **Bulk vs. per-filing export — ANSWERED.** No public bulk lobby download for 2025.
   Searches explicitly contrast campaign finance ("downloadable CSV/tab-delimited legacy
   data") with lobby (no equivalent). MiTN offers only a per-search/per-filing "spreadsheet
   to export reported disclosures." → **Primitive = scrape/drive MiTN.**
2. **Registrant ID discovery — PARTIAL.** MiTN lobby search confirmed at
   `page.request.do?page=page.miboeLobbyPublicSearch`. Facets present: **Lobbyist/Agent,
   Addresses, Filings, Expenditures, Expenditures Itemized, Fees, Notifications, Employees,
   Employed By.** Results load via JS ("loading…" placeholders) — the AJAX endpoint shape is
   **not visible in static HTML**; needs a browser network capture.
3. **Detail-page URL template — UNKNOWN (needs browser).**
4. **"Employed By" relationship — CONFIRMED as a facet** (agent↔employer graph exists; the
   WI authorization-graph analog). Edge fields not yet captured.
5. **Filing structure — PARTIAL.** Official forms identified: **Financial Report Summary**
   + **Itemized Expenditure Form (LR-4)**. Itemized rows = single expenditures > $100 with
   {date, purpose, recipient name+address, amount, YTD}, categories = financial transactions
   / travel-lodging / food-beverage benefitting public officials, over statutory thresholds.
   Cadence = **semi-annual** (Jan 31 + Aug 31). Exact on-screen field list needs browser.
6. **2025 availability — YES.** MiTN is the live 2025 system.
7. **robots/politeness/TOS — PARTIAL.** `mi-boe.entellitrak.com/robots.txt` → **404** (no
   robots file = no declared crawl restrictions). Still use a conservative delay (≥1.0 s,
   WI convention) and a real UA. Check entellitrak for session/CSRF tokens during the browser
   pass. **Read MiTN/SoS Terms of Use for a scripted-search prohibition** — not as a go/no-go
   gate, but to know which world we're in: "just download/export" vs. "ask/demand it." If MiTN
   carries NC-style language ("automated or scripted searches not permitted"), that does **not
   stop us** — it becomes a practical-availability finding and triggers a records request.
   See "Access posture & strategy" below.
8. **Volume estimate — UNKNOWN (needs browser).** Historical scale reference: the legacy NIC
   dump held 8,261 lobbyist↔principal records over 1982–2023 (cumulative, not per-year).

## External cross-check sources (for later validation, not acquisition)

- **The Accountability Project** (IRW): MI lobbying *registration* dataset, 1982–2023, 8,261
  records, sourced from `miboecfr.nicusa.com/cgi-bin/cfr/lobby_srch_res.cgi`, processed in R,
  documented on their GitHub. Good historical cross-check; **stale (2023), wrong vintage.**
- **Transparency USA** and **MCFN** (Michigan Campaign Finance Network) also publish MI data,
  primarily campaign-finance-focused.

## Remaining (needs a live browser — Playwright / webapp-testing skill)

The JS/AJAX nature of MiTN means these can't be resolved by static fetch:
- Capture the entellitrak AJAX request/response for a lobby search (endpoint, params, paging).
- Determine whether the **built-in spreadsheet export** returns a *full* result set for a
  broad search (→ cheap "search-all + export" path) or only a single filing (→ full scrape).
- Capture a registrant detail-page URL template + a real "Employed By" edge + a real
  Financial Report Summary / LR-4 itemized schedule, to seed parser fixtures.

## Access posture & strategy (TOS vs. statutory public-records obligation)

**Principle (applies to every state; see the parallel note on the `nc-disclosure-explore`
branch).** A state's online-search **Terms of Use is a click-through contract of adhesion and
does not override a statutory public-records obligation.** Where a lobbying-disclosure statute
requires records to be public, the duty to make them *available* is on the state. So for this
project an access barrier — a scripted-search prohibition, a JS-only per-record search, a
paywalled bulk option — is **a practical-availability finding to record on the N×50×2 matrix,
not a stop.**

- **The lever that honors the statute is to put it back on the agency:** a public-records
  request (or a direct ask) for the bulk electronic file in usable form. A refusal or paywall
  on statutorily-public data is itself a documentable finding. (This is the same move the WI
  work flagged — emailing `lobbying@wi.gov` to ask Ethics to run the authorization CSV.)
- **Keep one distinction clean:** the statute typically guarantees *access* (often satisfiable
  by per-record inspection or fee-based copies), not specifically *bulk machine-readable
  provision*. So the request/demand is the right instrument. Scraping publicly-accessible data
  is legally defensible post-*hiQ v. LinkedIn* (not a CFAA violation), and a **state actor's**
  TOS purporting to restrict access to its own statutorily-public records is on weak ground —
  but it carries practical risk (IP blocking regardless of legality) and an optics cost for a
  democracy-fellowship project. **Hold scraping in reserve; lead with the records request.**

**MI access posture (current best understanding):** lobby disclosure is **public by statute**
(Michigan Lobby Registration Act, Act 472 of 1978, MCL 4.411–4.430). The 2025 data lives in
MiTN, which offers a JS/AJAX search + per-result/per-filing export but **no free bulk
download**. MiTN's full TOS has **not yet been read** — that's a recon item, but per the
principle above it's not a gate. If MiTN allows broad search-and-export, that's the cheapest
path; if it prohibits automation, we request the bulk file from the SoS/Bureau of Elections.
Either way the data is public and the ask is on them.

## Recommendation (acquisition primitive)

**Scrape/drive MiTN entellitrak.** Next concrete step is a short **live browser recon** to
choose between:
- **(A) Search-and-export:** if one broad per-facet search returns all rows and the export
  yields the full set, acquisition is "issue ~9 facet searches → export → parse spreadsheets."
  Dramatically cheaper than WI; little custom scraping.
- **(B) Enumerate-and-fetch (WI-style):** discover registrant IDs, fetch each detail page via
  the entellitrak AJAX endpoint, checkpoint full HTML/JSON, parse. Fallback if (A)'s export is
  per-filing-only or capped.

Either way the data model is **entity + employer-graph + expenditure** (incl. MI's
itemized-to-officials table); **no bill chain** (confirmed — MI collects no bill-level data).
