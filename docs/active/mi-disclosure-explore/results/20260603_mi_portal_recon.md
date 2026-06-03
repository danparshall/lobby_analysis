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
   pass. **⚠️ MUST verify MiTN/SoS Terms of Use for a scripted-search prohibition BEFORE
   scraping** — robots.txt absence ≠ permission. Precedent: **North Carolina** explicitly
   forbids it ("Automated or scripted searches … are not permitted. For bulk access … use our
   Data Subscription Services"), which is why the NC activity data is not freely obtainable.
   If MiTN carries equivalent language, the scrape path is blocked and we'd be limited to
   manual/per-filing export or a paid/again-FOIA route — same wall NC hit.
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
