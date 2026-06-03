# 2026-06-03 — WI CFIS access-surface scoping

**Branch:** `wi-cfis-scoping`
**Originating plan:** [`../../../historical/wi-allocation-matrix/plans/wi_allocation_matrix.md`](../../../historical/wi-allocation-matrix/plans/wi_allocation_matrix.md) §178-187 (Phase 4)
**Originating chain:** `releases/wi/chain/WI_chain_2025.tsv` (115,229 rows, published 2026-06-02)

## Goal

Phase 4 of the archived wi-allocation-matrix plan: scope the WI Ethics Commission's Campaign Finance Information System (CFIS) as the missing $-flow leg of the WI 2025-2026 lobbying chain. The synthesis at `docs/historical/wi-allocation-matrix/results/20260602_wi_chain_synthesis.md` identifies CFIS as the structurally-missing path for:

- **principal → lawmaker** ($-contributions from registered lobbying principals to elected officials they lobby)
- **lobbyist → lawmaker** (personal $-contributions from registered lobbyists to officials; partial proxy for direct-contact disclosure, which WI does not mandate)

## Pre-session decisions

- **Q4 (timebox):** Dan picked open-ended until clean schema characterization (not 0.5-day boxed). Implication: investigate until WI CFIS's principal/recipient/contribution schema is cleanly mapped to the chain's `WI_principals.tsv` join keys and to `ocd-person/...` lawmaker IDs.
- **Write-only branch.** Per the parent plan, this branch produces a scoping writeup + (at most) one sample query end-to-end. No production scrape, no ingestion code. The recommendation deliverable decides whether a separate `wi-campaign-finance` branch gets cut.

## Investigation plan (this session)

1. Identify the CFIS public access surface (bulk download? API? scrape only?) via WI Ethics Commission website.
2. Characterize the principal-identifier shape in CFIS (name string / FEIN / state ID / committee ID).
3. Locate the lobbyist personal-donation disclosure path.
4. Check whether FollowTheMoney (followthemoney.org / National Institute on Money in Politics) already ingests WI campaign finance — if yes, that's substantially cheaper than direct scraping.
5. Run one sample query end-to-end against a known WI lawmaker (LeMahieu — Senate Majority Leader, already characterized in the chain's SB 28 / ROFR finding).
6. Document join keys back to `releases/wi/WI_principals.tsv` (likely string-match + canonicalization) and to the chain's `ocd-person/...` lawmaker IDs.
7. Write `results/20260603_phase_4_cfis_scoping.md` with an explicit go/no-go recommendation.

## Findings

Full writeup: [`../results/20260603_phase_4_cfis_scoping.md`](../results/20260603_phase_4_cfis_scoping.md).

### Access surface (TL;DR)

1. **CFIS → Sunshine (2025 transition).** `cfis.wi.gov` 301-redirects to `campaignfinance.wi.gov`, which is a thin marketing wrapper around `wi.sunshine.civera.com` — Civera-hosted Next.js SPA. The old CFIS portal Selenium scraping work the Investigative Reporting Workshop did (`irworkshop/accountability_datacleaning`) does NOT run as-is against Sunshine but the architectural shape is the same.
2. **No documented Sunshine API.** Probed `/api/transactions`, `/api/v1/transactions`, `/api/transactions/search`, `/api/receipts`, `/api/registrants`, `/api/search`, `/api/data` — all 404. CSP `connect-src 'self'` rules out separate API hosts. The internal Next.js Route Handlers are discoverable only via real-browser DevTools.
3. **Documented bulk path = UI Transaction Search → CSV export, 65K rows/export.** Inherited from old CFIS, kept by Sunshine. The IRW Selenium scraper iterates this in batches.
4. **FollowTheMoney.org is the cheapest credible source.** 50-state coverage current through 2024, free API for academic/nonprofit. `curl api.followthemoney.org` returns `{"error":"Invalid API Key"}` — endpoint live-confirmed, gating not absence.
5. **Wisconsin Democracy Campaign** (wisdc.org) is behind Sucuri CloudProxy anti-bot. Useful for human research, not automated ingest.
6. **Accountability Project** has 2008→Jun 2023 / 8.39M WI records, stale by ~3 years. Good for historical baseline, not for current cycle.

### Schema (from IRW's `wi_contribs_diary.md`)

Raw CFIS `ReceiptsList.csv`: 18 cols — `TransactionDate, FilingPeriodName, ContributorName, ContributionAmount, AddressLine1, AddressLine2, City, StateCode, ZIP, Occupation, EmployerName, EmployerAddress, ContributorType, ReceivingCommitteeName, ETHCFID, Conduit, Branch, Comment, 72 Hr. Reports, SegregatedFundFlag`.

- **No FEIN.** Donor identity is name-string only.
- **No lobbyist-affiliation tag.** Lobbyist personal contributions are commingled.
- **`ETHCFID` is stable** — primary join key on the recipient side.
- **`Occupation` + `EmployerName`** populated only for contributions > $200; high-signal for lobbyist-side disambiguation when present.

### Lobbyist personal contributions

No separate filing. §13.625 imposes narrow temporal windows (between nomination paper circulation and election day for partisan state offices and current legislators; after final floor period; not in special/extraordinary sessions). Match via name-string against `releases/wi/WI_lobbyists.tsv` (773 entries).

### Join keys

| Side | Method | Anchor in chain | Anchor in CFIS | Rosters |
|---|---|---|---|---|
| Principal | Name canonicalization | `WI_principals.tsv.name` | `ContributorName` / `EmployerName` / `Conduit` | 1,108 principals |
| Lobbyist | Name canonicalization + occupation/employer disambiguation | `WI_lobbyists.tsv.name` | `ContributorName` + `Occupation` + `EmployerName` | 773 lobbyists |
| Lawmaker | `ETHCFID` → committee name → `ocd-person/...` crosswalk (try OpenStates `Person.identifiers` first, fallback manual ~165-row table) | `sponsor_lawmaker_id` | `ETHCFID` + `ReceivingCommitteeName` + `Branch` | 132 unique sponsors (in chain) — but design for ~165 sitting legislators in case cosponsor parsing lands |

### Sample query — RUN END-TO-END (updated mid-session)

Dan opened an FTM account and pasted his API URL into chat mid-session, so the punted-to-implementation sample query became resolvable here. Full writeup: [`../results/20260603_ftm_sample_query_lemahieu.md`](../results/20260603_ftm_sample_query_lemahieu.md). Key results:

- LeMahieu's FTM identity: `c-t-id=325785` (2022 cycle) / `c-t-eid=3073941` (career). 2022 cycle = 2,803 transactions / $609,272 / 1,822 contributors.
- 15-field transactional schema decoded; FTM ALREADY does donor-entity canonicalization (`Original_Name` raw → `Contributor`/`d-eid` canonical) and 3-level industry classification.
- Chain cross-validation: Xcel Energy at #21 in top-25 donors matches Xcel's chain #7 SB 28 position (39.9 hrs); WEC Energy Group PAC in transaction page 0 ($2K, 2019-05-04) matches WEC's chain #2 SB 28 position (134.4 hrs).
- `d-llink` "Lobbying Entity?" flag covers only ~5% of LeMahieu's 2022 contributions — concentrated on corporate PACs, doesn't catch individual lobbyist contributions. Useful soft signal, not a shortcut.
- **Basic-tier quota exhausted after ~15 queries.** Account flagged for Institute review with 2-business-day approval window. Expanded-access request to `info@opensecrets.org` now a Phase 1 hard prerequisite.
- Sunshine UI sample export NOT run — moot given FTM-first path; would be a coverage-gap-only fallback now.

### Recommendation (revised post-sample-query)

**Yes, cut a separate `wi-campaign-finance` implementation branch.** Now with concrete shape:

- **Phase 0** (calendar wait): wait for the Institute's automatic review email (~2 business days per the quota-exceed response SLA); reply with affiliation + project context when it arrives. Proactive email to `info@opensecrets.org` only if no contact by ~end of business day 3-5.
- **Phase 1** (3-5 days post-approval): full FTM ingest of WI 2024 + 2025-2026 cycle contributions for all ~165 sitting WI legislators; principal-side / lawmaker-side / lobbyist-side crosswalks; materialize `releases/wi/campaign_finance/WI_contributions_*.tsv` and `WI_chain_v2_2025.tsv`.
- **Phase 2** (conditional, 5-7 days): Selenium-Sunshine port to fill specific gaps Phase 1 surfaces. NOT a full duplicate ingest.

Full Phase 4 writeup at `results/20260603_phase_4_cfis_scoping.md`; sample-query artifact at `results/20260603_ftm_sample_query_lemahieu.md`; FTM TOS + attribution requirements at scoping doc §7.

## Next steps

This branch's deliverable is the scoping doc; no further sessions planned here. Successor work belongs on a fresh `wi-campaign-finance` branch:

1. **Sign up for a free academic/nonprofit FollowTheMoney.org API key** (Canary Institute affiliation qualifies).
2. **Cut `wi-campaign-finance` worktree** off post-merge main (after this `wi-cfis-scoping` branch merges, so the scoping doc is on main for reference).
3. **Phase 1: FTM viability test.** Query for contributions received by Devin LeMahieu's candidate committee, 2024–2026 cycles. Spot-check against the 29 SB 28 principals (`docs/historical/wi-allocation-matrix/results/20260602_lemahieu_bill_inspection.md`) — does FTM see ATC Management, WEC Energy Group, WI Industrial Energy Group, etc.? Determine GO/NO-GO on FTM as primary source.
4. **Hold over for the implementation branch:** the parent plan's Refinement #2 (cosponsor parsing) and whether to do it before or after the CFIS implementation work. The scoping doc recommends sizing the lawmaker-side crosswalk to all ~165 sitting legislators regardless of when cosponsors land, so the order is no longer load-bearing.

