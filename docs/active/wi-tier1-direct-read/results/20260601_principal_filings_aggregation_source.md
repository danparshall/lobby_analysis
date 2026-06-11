# WI principal-filings aggregation: portal-publication choice or scrape loss?

**Date:** 2026-06-01
**Source plan:** [`../plans/20260601_post_phase3_followups.md`](../plans/20260601_post_phase3_followups.md) Item 5.
**Originating evidence:** [`20260601_wi_statute_vs_portal_spending.md`](20260601_wi_statute_vs_portal_spending.md) — the 4 principal-side gaps surfaced in the statute-vs-portal cross-validation.
**Session convo:** [`../convos/20260601_phase3_followups_execution.md`](../convos/20260601_phase3_followups_execution.md).
**Verdict:** **Neither hypothesis (A) nor (B) cleanly — it's "Tier-3 was deliberately deferred."** The currently-scraped per-principal page exposes only aggregates (matching A's shape), but the WI portal itself does publish the itemized data — in a separate page family the current `wi-disclosure-explore` Tier-2 scrape explicitly does not fetch.

---

## Recap of the 4 gaps

From [`20260601_wi_statute_vs_portal_spending.md`](20260601_wi_statute_vs_portal_spending.md), per-cell statute-vs-portal status on the principal side:

| Compendium row | Statute citation | Portal column | Status |
|---|---|---|---|
| `principal_spending_report_includes_compensation_paid_to_lobbyists` | §13.68(1)(a)1., (a)6. | none | GAP |
| `principal_spending_report_includes_gifts_entertainment_transport_lodging` | §13.68(1)(d) | none | GAP |
| `principal_spending_report_includes_indirect_costs` | §13.68(1)(b) | none | GAP |
| `principal_spending_report_uses_itemized_format` | §13.68(1)(c) | none (only `total_expenditure` scalar) | GAP |

All 4 reduce to "statute requires itemization; `WI_principal_filings.tsv` exposes only `total_expenditure`."

## What the current scrape actually fetches

The current WI scrape hits exactly **four URL families** (`grep "URL_TEMPLATE\|http" src/lobby_analysis/io/wi/`):

1. `https://lobbying.wi.gov/Who/PrincipalInformation/{session_id}/Information/{principal_id}` — per-principal info page (the `total_expenditure` source).
2. `https://lobbying.wi.gov/Who/LobbyistInformation/{session_id}/Information/{lobbyist_id}` — per-lobbyist info page (the `total_hours_*` source).
3. `https://lobbying.wi.gov/Who/Lobbyists/{session_id}/ShowLobbyistList` — directory index.
4. `https://lobbying.wi.gov/Home/Welcome` — root for session cookie.

There are **no** per-statement, per-CC-1, or per-SLAE fetches in the codebase.

## What `principal_meta_parser` reads vs drops

`src/lobby_analysis/io/wi/principal_meta_parser.py` (`_extract_total_lobbying_effort_filings`, lines 362–444) parses the **"Total Lobbying Effort"** table on the principal info page. That table has exactly **three labeled rows** (keys, lines 144–146 of the same file):

- `_TLE_LABEL_EXPENDITURE = "Total Lobbying Expenditures"` → `total_expenditure`
- `_TLE_LABEL_HRS_COMM = "Total Hours Communicating"` → `total_hours_communicating`
- `_TLE_LABEL_HRS_OTHER = "Total Hours Other"` → `total_hours_other`

The parser reads all 3. **Nothing is silently dropped.** The page DOM does not contain rows for compensation-per-lobbyist, gifts, indirect costs, or itemized line-items — those don't exist on this page in any form.

The 4 page sections the parser walks (per the module docstring, lines 1–87):
1. Organization metadata block.
2. Free-text strongs (CEO name, business-or-interest, lobbying-interests prose).
3. "Total Lobbying Effort" table (the 3 rows above).
4. "Percent Allocation of Lobbying Effort" cross-tab (per-bill % only, **no $ amounts**).

Plus the bipartite edge table at the bottom of the same page, handled by `principal_parser.parse_principal_authorizations` ("Authorized Lobbyists" — name/exclusive-duties/dates only, no $).

## So where does the itemized data live?

The archived `wi-disclosure-explore` branch already answered this question — explicitly, twice. From [`docs/historical/wi-disclosure-explore/plans/wi_tier_2_parser.md`](../../../historical/wi-disclosure-explore/plans/wi_tier_2_parser.md):

> **Architecture:** … Tier-2 only; tier-3 (per-(lobbyist, principal, semester) detailed time reports + **per-principal SLAE itemizations**) is out of scope.
>
> **No tier-3 work.** Per-(lobbyist, principal, semester) detailed time reports and per-principal SLAE itemizations are a separate plan. They require both new fetches and a reconnaissance step on at least one page first.
>
> **No `LobbyingPosition` / `LobbyingExpenditure` / `LobbyingEngagement` / `Gift` sub-entities.** Those need tier-3 data to populate meaningfully (the Tier-2 summary fields are aggregate totals, not itemized lines).

And from [`docs/historical/wi-disclosure-explore/convos/20260526_wi_data_ingest_and_join_key_investigation.md`](../../../historical/wi-disclosure-explore/convos/20260526_wi_data_ingest_and_join_key_investigation.md), the captured-task pointer:

> [#28: Pull WI expenditure data (15-day reports + 6-month SLAEs)](https://github.com/danparshall/lobby_analysis/issues/28) — captured 2026-05-26

GH #28 body confirms the data sources:

> WI Ethics Commission exposes lobbying expenditure data via two report families: **15-day notifications (Wis. Stat. §13.67(1))** and **6-month SLAEs**, plus per-bill/topic aggregates at `/What/WhatAreTheyLobbyingAbout/2025REG/ReportExport`. The wi-disclosure-explore branch currently covers entity directories + lobbyist↔principal authorizations only — expenditure pull is deferred but explicitly wanted.

So: the WI portal publishes the itemized data. The current scrape's coverage was scoped to Tier-2 deliberately, with Tier-3 work tracked.

## What this means for the 4 gaps

The right framing for the WI cross-validation doc's "the next question (the wi-disclosure-explore archive should know)" is **already answered**:

| Gap | What's missing today | What lives in tier-3 | Tracking |
|---|---|---|---|
| `compensation_paid_to_lobbyists` | per-(principal, lobbyist) compensation $ | SLAE itemization — per the archived plan, `LobbyingExpenditure.recipient_name/role` was named the v1.3-target shape | GH #28 |
| `gifts_entertainment_transport_lodging` | per-category itemization | SLAE itemization — `Gift` sub-entity was named in the deferred set | GH #28 |
| `indirect_costs` | indirect/overhead line | SLAE itemization (statute §13.68(1)(b) requires it; expected on the form) | GH #28 |
| `uses_itemized_format` | (meta gap; downstream of above) | structurally, SLAE pages ARE itemized | GH #28 |

The 4 gaps are **not** parser bugs and **not** a portal-publication choice in the broad sense. They are the symptom of one specific decision: Tier-2 fetched and parsed only the per-principal summary page, and Tier-3 (per-SLAE itemization) was held over for a separate plan.

## Open question (not in scope for this writeup)

**No one has yet inspected a Tier-3 SLAE itemization page.** The archived plan notes: "Per-(lobbyist, principal, semester) time reports + per-principal SLAE itemizations would require ~1500-3000 new fetches and we haven't yet inspected even one tier-3 page to know what it contains." It's *plausible* but not *confirmed* that the Tier-3 SLAE page exposes all 4 gap categories. A 1-page reconnaissance pull would close that loop cheaply (and is the natural Phase-1 of the GH #28 implementation). Suggested follow-up: when GH #28 is taken on, the first step is a single SLAE page fetch + DOM inspection, gated on user review before any bulk fetch.

## Sequencing implication for MI

Per the followups plan Item 4, MI Tier-1 should be paired with a parallel portal cross-validation. This Item 5 finding adds a check for MI: when MI's portal is scraped, the cross-validation should explicitly note **what's scraped vs what the MI portal also publishes that isn't yet fetched**. The WI lesson: a gap in `releases/<state>/` does not necessarily mean the data isn't on the portal — it may mean the same deferred-Tier-3 shape.

## Acceptance criteria from the plan

- [x] Read the Tier-2 parser modules at `src/lobby_analysis/io/wi/`. Specifically looked at whether `principal_meta` parsers see itemized fields and intentionally drop them — they do not.
- [x] Conclusion captured: not scrape loss; not portal-publication absence; it's a Tier-2/Tier-3 scope decision, with Tier-3 work tracked at GH #28.
- [x] Note for sequencing: this is the answer for "what the practical-side data layer can ever look like for WI" — it can include itemization once GH #28 is done; today's `total_expenditure`-only TSV is the Tier-2 ceiling.

## Cost

Zero spend (code-reading only).
