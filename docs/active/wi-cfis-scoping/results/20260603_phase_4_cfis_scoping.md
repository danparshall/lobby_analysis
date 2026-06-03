<!-- Generated during: convos/20260603_wi_cfis_access_surface_scoping.md -->

# Phase 4 — WI CFIS access-surface scoping

**Date:** 2026-06-03
**Branch:** `wi-cfis-scoping` (cut off post-merge main `e84d2a1`)
**Originating convo:** [`../convos/20260603_wi_cfis_access_surface_scoping.md`](../convos/20260603_wi_cfis_access_surface_scoping.md)
**Originating plan:** [`docs/historical/wi-allocation-matrix/plans/wi_allocation_matrix.md`](../../../historical/wi-allocation-matrix/plans/wi_allocation_matrix.md) §178-187 (Phase 4)
**Joins against:** `releases/wi/chain/WI_chain_2025.tsv` (115,229 rows, 132 unique primary sponsors), `releases/wi/WI_principals.tsv` (1,108 principal rows), `releases/wi/WI_lobbyists.tsv` (773 lobbyist rows)
**Timebox:** open-ended (Dan, Q4 — chose clean schema characterization over 0.5-day box)
**Code written this branch:** zero (write-only by design)
**Sample query executed end-to-end:** yes — see companion writeup [`20260603_ftm_sample_query_lemahieu.md`](20260603_ftm_sample_query_lemahieu.md). Dan opened an FTM account mid-session, surfacing the API-key path; the sample query against LeMahieu's 2022 cycle (`c-t-eid=3073941`) confirmed schema, entity canonicalization, partial `d-llink` lobbying flag (~5% coverage), and cross-validated the chain (WEC PAC + Xcel both visible). Basic-tier quota hit after ~15 queries — expanded-access request now a hard Phase 1 prerequisite.

---

## TL;DR

WI campaign-finance data **is publicly accessible** and **can close the chain's missing $-flow leg**. The cheapest credible path is **FollowTheMoney.org** (National Institute on Money in State Politics, under OpenSecrets) — schema confirmed end-to-end via a live sample query in this session (LeMahieu `c-t-eid=3073941`; 2,803 transactions / $609K / 1,822 contributors for the 2022 cycle). **FTM has already done the donor-entity canonicalization and industry classification** we'd otherwise have to build, and **the chain's SB 28 / ROFR coalition cross-validates** — Xcel Energy appears at #21 in LeMahieu's top-25 donors; WEC Energy Group's PAC shows up in transaction-level page 0; both match their chain positions as top SB 28 lobbying filers.

The catch: **basic-tier API quota is much tighter than the TOS's "1,000 records/year" reads.** Dan's account exhausted basic-tier quota after ~15 queries in this scoping session and is now flagged for Institute review with a 2-business-day approval window. **Phase 1 of the implementation branch MUST start with the expanded-access request to `info@opensecrets.org`** — Canary Institute's 501(c)(3) status qualifies per the FTM TOS — then resume work after the gate clears.

The fallback if FTM coverage turns out to be insufficient for specific gaps is **Selenium-driving Sunshine** (the ex-CFIS portal, now a Civera Next.js SPA at `wi.sunshine.civera.com`, no documented API, 65K-row UI-export cap). The Investigative Reporting Workshop's open-source `accountability_datacleaning` repo proved this approach at 8.39M-record scale against the old CFIS. With FTM-first, Sunshine becomes a coverage-gap supplement, not a duplicate ingest.

**Lobbyist personal contributions** are NOT a separate filing in WI — they're commingled with all other contributions, identifiable only by name-string match against the 773-entry lobbyist roster + `Occupation`/`EmployerName` disambiguation at $200+. WI §13.625 imposes narrow "windows" on when lobbyists can give, which makes the lobbyist slice small and tractable. FTM's `d-llink` "Lobbying Entity?" flag covers only ~5% of contributions and is concentrated on corporate PACs, so it does not shortcut the individual-lobbyist join.

**Recommendation: cut a separate `wi-campaign-finance` implementation branch.** Phase 0 = submit expanded-access request, wait ~2 business days. Phase 1 = full FTM ingest + chain join (3-5 days post-approval). Phase 2 = Selenium-Sunshine gap-fill, only if needed. Full FTM TOS / licensing constraints documented in §7; data use is bound by CC BY-NC-SA 3.0 US with mandatory attribution to **"National Institute on Money in State Politics"**.

---

## 1 — Access surface

| Path | Owner | Coverage | Bulk download | API | Sample-cost | Verdict |
|---|---|---|---|---|---|---|
| **Sunshine** (`campaignfinance.wi.gov` / `wi.sunshine.civera.com`) | WI Ethics Commission via Civera (vendor) | 2008-07 → present | No documented path | Internal Next.js Route Handlers, not public, same-origin CSP-locked | Hours to discover via browser DevTools; then Selenium for production | **Official, but expensive to ingest** |
| **Old CFIS** (`cfis.wi.gov`) | WI Ethics Commission, legacy | Replaced by Sunshine in 2025; 301 → `campaignfinance.wi.gov` | — | — | — | Defunct |
| **FollowTheMoney** (`api.followthemoney.org`) | National Institute on Money in Politics (under OpenSecrets since merger) | All 50 states, current through 2024 election cycle | Yes, via export icons after running a query in the web UI | **Documented REST API at single PHP endpoint**, basic key auto-issued on account creation; **expanded-access request to `info@opensecrets.org` required for any production-shape work** (basic-tier quota exhausts after ~15 queries per the sample-query writeup); 2-business-day Institute review | Account signup ~5 min; sample query ~seconds; expanded-access wait ~2 business days | **Cheapest credible path** (post-expanded-access approval) |
| **The Accountability Project** (`publicaccountability.org`) | Investigative Reporting Workshop / MuckRock | 2008-01 → 2023-06-04 only (8.39M WI records); stale by ~3 years | CSV download via UI search results | None | Free, browser-driven | Useful for historical bulk; stale for recent |
| **Wisconsin Democracy Campaign** (`wisdc.org`) | WisDC, nonprofit (since 1993) | 1993 → present (some 1989 records) | No public CSV / API observed | Behind Sucuri CloudProxy JS gate (bot-protected) | Headless browser; same effort as Sunshine | Best human-research interface; not for automated ingest |

### 1.1 Why Sunshine itself is expensive

- The site is a **Next.js SPA on Civera infrastructure** (`wi.sunshine.civera.com`). Initial HTML is a 36-line shell that loads ~20 Next.js chunks before any data renders. WebFetch can't see past "Loading site data, please wait."
- The Content-Security-Policy `connect-src 'self'` directive locks XHR to same origin — there's no separate public API host to discover.
- All `/api/*` paths I probed (`/api/transactions`, `/api/v1/transactions`, `/api/transactions/search`, `/api/receipts`, `/api/registrants`, `/api/search`, `/api/data`) returned **404**. The API exists but is named under the app's internal Next.js routing, discoverable only by inspecting the running app's XHR calls in a real browser.
- The documented user-facing export path (per WI Ethics Commission and Civera) is the **Transaction Search → "Export to CSV"** button, capped at **65,000 records per export**. For statewide bulk ingestion, this means Selenium-style page-driving (the IRW model below).

### 1.2 Why the IRW model is the realistic Sunshine fallback

The Investigative Reporting Workshop (Columbia / American U) maintains [`irworkshop/accountability_datacleaning`](https://github.com/irworkshop/accountability_datacleaning), which already includes a working WI contributions scraper:

- **Path:** `state/wi/contribs/docs/wi_contribs_diary.md` (the R-markdown processing diary)
- **Method:** Selenium-driven export against the old CFIS UI, in 65K-row batches
- **Stack:** R + `campfin` package (their own; supplies `normal_address`, `normal_zip`, `normal_state`, `normal_city`, `normal_phone` — the entity-resolution primitives we'd otherwise have to rebuild)
- **Output:** `ReceiptsList.csv` schema (next section)
- **Reach:** 1995-12-31 → 2023-05-03, 8.39M records on their 2023-06-04 dump

The 2025 transition from CFIS to Sunshine means **the IRW Selenium script will not run as-is against the new UI**. But the export format is documented to be the same shape (committees, contributors, payees, transactions), the 65K-row cap carries over, and the column set is unlikely to have changed materially. **Porting their R Selenium driver to Python against the new Sunshine UI is ~1-2 days of engineering** — a known finite cost.

### 1.3 Why FTM is the right first attempt

- **National scope, normalized.** The Institute on Money in Politics has been ingesting all 50 states' campaign finance data since the early 2000s, with a stable entity-ID model. Two entity IDs are exposed:
  - `c-t-eid` — the candidate Entity ID (career-spanning, stable across cycles); LeMahieu = 3073941.
  - `d-eid` — the contributor Entity ID; WISCONSIN ENERGY CORP = 9524. **FTM has already canonicalized the donor side** — every transaction row exposes `Original_Name` (raw filer spelling, e.g. "WEC ENERGY GROUP PAC (WEC PAC)") alongside `Contributor` (canonical entity, e.g. "WISCONSIN ENERGY CORP" with `d-eid=9524`). This eliminates the principal-side name-canonicalization layer we'd otherwise have to build.
- **Built-in industry classification.** Every contribution carries a three-level taxonomy (`Specific_Business` / `General_Industry` / `Broad_Sector`) — e.g., `"Gas & electric utilities"` / `"Electric Utilities"` / `"Energy & Natural Resources"`. We do not have to build our own industry mapping for sector rollups.
- **API exists and is reachable.** Direct probe and full end-to-end sample-query verified (see [`20260603_ftm_sample_query_lemahieu.md`](20260603_ftm_sample_query_lemahieu.md)) — schema decoded, dimension dictionary captured, LeMahieu's 2022 cycle pulled (2,803 transactions / $609K), top-25 donors enumerated.
- **Chain cross-validation confirms WI coverage.** Xcel Energy ($2K) in LeMahieu's top-25 donors matches Xcel's chain position (#7 SB 28 filer at 39.9 hrs). WEC Energy Group's PAC ($2K, 2019-05-04) appears in transaction-level page 0, matching WEC's chain position (#2 SB 28 filer at 134.4 hrs).
- **`d-llink` partial lobbying-entity flag.** FTM tags some contributors with a lobbying-entity link (semantics: `d-llink` value = the contributor's `d-eid` when FTM matches the donor to a known lobbying entity, else `?`). Coverage is **~5% of LeMahieu's 2022 contributions** — concentrated on the $2K corporate-PAC cluster. It's a useful soft signal for the principal-side join but NOT a complete shortcut, and it does not flag individual lobbyist personal contributions.
- **Already updated through 2024**, with continuing updates. The Plural Policy chain bills are 2025-2026; FTM may lag the most recent cycle but should have the bulk of 2025-cycle filings.
- **One-API path, not two.** If we go FTM, we don't need to maintain a Sunshine scraper at all — FTM does the scraping for us. The chain ingest becomes a single dependency on a stable API instead of two scrape pipelines.

The risk that justifies a fallback plan: FTM drops a few state-specific CFIS fields — `EmployerAddress`, `Comment`, `72Hr. Reports`, `SegregatedFundFlag`, `ETHCFID`, `Conduit` (probably), `AddressLine1/2`. None of these are blocking for the chain join. The one that matters — `ETHCFID` — is replaceable by FTM's `c-t-eid` as the lawmaker-side anchor; same shape, different stable key. **Field-coverage risk: largely cleared by the sample query.** What remains is the quota gate (next bullet).

**Quota gate.** Basic-tier API quota is much more restrictive than the TOS's "1,000 records/year" reads. Dan's account exhausted basic-tier quota after **~15 queries** in the scoping session, returning the "Institute will be in contact within the next two business days to approve continued API usage" gate. **Expanded-access request is now a Phase 1 hard prerequisite** — see §6.

---

## 2 — CFIS / Sunshine raw schema

From the IRW diary (against old CFIS; Sunshine export format is likely the same or a strict superset):

```
TransactionDate
FilingPeriodName
ContributorName              ← donor side, name-string
ContributionAmount
AddressLine1
AddressLine2
City
StateCode
ZIP
Occupation                   ← donor occupation (only on contributions > $200)
EmployerName                 ← donor employer (only on contributions > $200)
EmployerAddress
ContributorType              ← Individual | PAC | Conduit | etc.
ReceivingCommitteeName       ← recipient committee name-string
ETHCFID                      ← Ethics Commission committee ID — the stable recipient join key
Conduit                      ← if routed through a conduit (e.g., realtors' conduit)
Branch                       ← office name string ("State Senate District 9", "Governor", "Assembly District 17")
Comment
72 Hr. Reports
SegregatedFundFlag
```

Notable absences:
- **No FEIN, no state taxpayer ID** on the donor side. Donor identity is entirely name-string-based.
- **No lobbyist-affiliation flag.** A lobbyist's personal contribution lands here as just another row with their name as `ContributorName`.
- **No principal-affiliation flag** on the donor side either — a registered lobbying principal (e.g., WEC Energy Group) shows up either by its own name or via a PAC/conduit, with no link back to the lobbying-side registration.

Notable presences:
- **`ETHCFID`** is stable, so any join we build on the recipient side is durable. This is the primary join key for "lawmaker → contribution received."
- **`Occupation` + `EmployerName`** above the $200 threshold give us a soft signal for the lobbyist join — a contribution from "Smith, John" who lists `Occupation = "Lobbyist"` and `EmployerName = "Hamilton Consulting"` is a near-certain match to a registered lobbyist named John Smith at Hamilton Consulting.

---

## 3 — Lobbyist personal-donation disclosure path

There is **no separate lobbyist personal-contribution disclosure filing in WI**. Lobbyist personal contributions are:

1. **Restricted by §13.625 to narrow regulatory windows:**
   - For partisan state offices and current legislators: only between the first day nomination papers can circulate and the day of the general/special election, AND only after the Legislature concludes its final floor period (per Joint Resolution), AND not during special/extraordinary sessions.
   - For local, non-partisan, county-level partisan, District Attorney, and national offices: no temporal restrictions if the candidate isn't a current partisan state office holder.
2. **Reported by the receiving committee** (not by the lobbyist), via the same Sunshine/CFIS filings that capture all other contributions.
3. **Distinguishable from non-lobbyist donations only via name-string match** against the registered-lobbyist roster (`releases/wi/WI_lobbyists.tsv`, 773 entries). The `Occupation` and `EmployerName` fields (populated on contributions > $200) provide a secondary signal.

**Implication for the chain:** the lobbyist→lawmaker leg is built by the consumer, not exposed pre-tagged. Workflow:

```
1. Pull all CFIS receipts for 2025-2026 (where ReceivingCommitteeName resolves to a state legislator).
2. Filter to ContributorName ∈ {names in WI_lobbyists.tsv after canonicalization}.
3. Confirm via Occupation/EmployerName when populated.
4. Emit (lobbyist_id, lawmaker_id, amount, date, ReceivingCommitteeName).
```

The §13.625 windows mean this slice will be SMALL — likely a few hundred to low thousands of records per cycle, which is well under any pagination cap. Dollar amounts are also capped per §11 (low-thousands typical limit per candidate per cycle).

**Cross-check we can do without scraping:** WisDC's `Look Up Contributors` UI already lets a human enter a lobbyist name and see their giving history. If we're skeptical that the join will work, we can pilot it manually against 5-10 known lobbyists before committing engineering time.

---

## 4 — Join keys back to the chain

### 4.1 Principal-side join: CFIS donor → `WI_principals.tsv`

| Item | Notes |
|---|---|
| **Method** | Name-string match + canonicalization |
| **CFIS columns to match against** | `ContributorName` (when the principal donates directly), `EmployerName` (when the donor is an employee of the principal — relevant for executive PAC checks), `Conduit` (when the principal sponsors a conduit PAC) |
| **Chain side** | `WI_principals.tsv.name` (1,108 entries) |
| **Difficulty** | **Medium.** WI law since 2015 substantially limits direct corporate contributions to state candidate committees; most principal-side flow now routes through PACs, conduits, or executive personal giving. Name-canonicalization needs to handle "WEC Energy Group, Inc." ↔ "WEC Energy Group" ↔ "Wisconsin Energy Corporation" ↔ "WEC PAC" and similar variants. |
| **Cost estimator** | Off-the-shelf normalization (IRW's `campfin::normal_*()` primitives or equivalent Python) handles ~80% of variants; the residual 20% needs hand-curation against the chain's top-100 principals (which cover most of the $$ volume). |

### 4.2 Lobbyist-side join: CFIS donor → `WI_lobbyists.tsv`

| Item | Notes |
|---|---|
| **Method** | Name-string match, plus `Occupation`/`EmployerName` as disambiguators when populated |
| **CFIS columns** | `ContributorName` (primary), `Occupation`, `EmployerName` |
| **Chain side** | `WI_lobbyists.tsv.name` (773 entries) |
| **Difficulty** | **Lower.** Smaller universe, narrow time windows (§13.625 restrictions), and the $200-threshold occupation field is high-signal. The chain already includes lobbyist `contact_details_json` with addresses that can cross-check against `Address*` fields when needed. |

### 4.3 Lawmaker-side join: CFIS recipient → `ocd-person/...` chain ID

This is the more architecturally significant join.

| Item | Notes |
|---|---|
| **Method** | Two-step: CFIS `ETHCFID` (committee ID) → candidate name → `ocd-person/...` |
| **CFIS columns** | `ETHCFID` (stable committee ID, primary), `ReceivingCommitteeName` (verbose string for human review), `Branch` (office disambiguator) |
| **Chain side** | `sponsor_lawmaker_id` (`ocd-person/...` UUIDs, 132 unique in the chain — but if cosponsors are added per the parent plan's Refinement #2, this grows to ~all 132 + many Assembly co-author names; design for "all sitting WI legislators" not "132 sponsors") |
| **Crosswalk source candidates** | (a) **OpenStates** `Person.identifiers[]` — Plural Policy may already have `wi-ethcfid` or similar there; needs verification. (b) **Ballotpedia** publishes candidate→committee linkages per cycle, scrapable. (c) **Manual curation** for the 132-name set is tractable. (d) **WI Ethics Commission's Registrant Search UI** publishes committee → candidate name; reverse-mappable. |
| **Recommendation** | Try (a) first; if missing, build a small one-time crosswalk via (d) for the 132 sponsors. |

**Important architectural note:** the parent plan's Refinement #2 (cosponsor parsing) is currently un-done. Implementing CFIS join sized to "132 primary sponsors" risks rework if cosponsors land later. The implementation branch should size the lawmaker-side crosswalk to **all sitting WI legislators** (132 senators + assembly, ~130 House + 33 Senate ≈ 165 individuals per session), not just primary sponsors. This is a small enough N that "complete coverage" is the safer design.

---

## 5 — Sample query — what was and wasn't run

Sample query against FTM **was run end-to-end this session.** Dan opened a `myFollowTheMoney.org` account mid-session and pasted a sample URL; I used that to find LeMahieu's `c-t-eid`, pull a transaction-level page (100 of 2,803 rows), and execute the rollup queries that confirm the schema and chain cross-validation. Full writeup: [`20260603_ftm_sample_query_lemahieu.md`](20260603_ftm_sample_query_lemahieu.md). Headline confirmations:

- **FTM API endpoint is live and works as documented.** Single PHP endpoint at `api.followthemoney.org/`; parameters decoded.
- **LeMahieu's stable FTM identity:** `c-t-eid=3073941`. His 2022 cycle: 2,803 transactions / $609,272 / 1,822 unique contributors.
- **Transaction-level schema is 15 fields** (vs. 18 in raw CFIS), with two additions FTM has done for us: donor-entity canonicalization (`Contributor`/`d-eid`) and a three-level industry taxonomy (`Broad_Sector` / `General_Industry` / `Specific_Business`). The CFIS fields FTM drops are mostly low-value (`AddressLine1/2`, `Comment`, `72Hr. Reports`, `SegregatedFundFlag`, `FilingPeriodName`, `EmployerAddress`). The one that matters — `ETHCFID` — is replaced by FTM's own `c-t-eid`, same shape, different anchor.
- **Chain cross-validation works:** Xcel Energy at #21 in LeMahieu's top-25 donors matches Xcel's chain position (#7 SB 28 filer at 39.9 hrs); WEC Energy Group's PAC ($2K, 2019-05-04) in transaction-level page 0 matches WEC's chain position (#2 SB 28 filer at 134.4 hrs).
- **`d-llink` is a partial flag, not a complete shortcut.** ~5% of LeMahieu's 2022 contributions are flagged with a lobbying-entity link, concentrated on the $2K corporate-PAC cluster. The individual lobbyist personal-contribution slice still requires our own name-string match against `WI_lobbyists.tsv`.
- **Basic-tier quota is tighter than the TOS implies.** After ~15 session queries Dan's account hit the gate: *"This account has reached its free API call limit pending Institute review of data usage."* Expanded-access request is now a Phase 1 prerequisite (§6, Phase 0).

I did NOT run a Sunshine UI export end-to-end:
- Sunshine SPA's API is not curl-reachable (§1.1). Driving the UI requires Playwright or Selenium.
- The IRW diary's existence is a stronger proof-of-feasibility than a one-off manual export would be — it documents a worked pipeline at 8.39M-record scale.
- With FTM confirmed as the primary path, a Sunshine sample is moot for the recommendation.

---

## 6 — Recommendation

**Yes, cut a separate `wi-campaign-finance` implementation branch.**

The CFIS leg is structurally separable from the lobbying-chain ingest (different source, different schema, different temporal cadence), and the work to close it isn't a "small follow-on" to `wi-allocation-matrix` — it has its own design decisions (FTM vs Selenium-Sunshine vs hybrid), its own entity-resolution work, and benefits from being on a clean branch with focused tests.

### Suggested first phase of `wi-campaign-finance`

(Phase 1's viability test was substantially executed in this scoping session — see [`20260603_ftm_sample_query_lemahieu.md`](20260603_ftm_sample_query_lemahieu.md). What remains for Phase 1 below is the expanded-access gate + a structured re-run once the gate clears.)

**Phase 0 — expanded-access request (calendar wait, ~2 business days).**

1. From the Canary Institute account, email `info@opensecrets.org` with the expanded-access request. Template in §6.6 of the sample-query writeup.
2. Wait for Institute approval. **Do not run further API queries before approval lands** — additional traffic against the throttled account risks deprioritization.

**Phase 1 — full FTM ingest + chain join (3-5 days, starts after Phase 0 approval).**

3. Build a small Python client (`httpx` + `pydantic`) hitting `api.followthemoney.org/`. Parameter conventions are decoded in [`20260603_ftm_sample_query_lemahieu.md`](20260603_ftm_sample_query_lemahieu.md) §1.
4. Pull WI 2024 and 2025-2026 cycle contributions for all sitting state legislators (~165 entities × 2 cycles ≈ a few hundred K transactions).
5. Materialize `releases/wi/campaign_finance/WI_contributions_2024_2026.tsv` with the 15-field FTM transactional schema.
6. Build the principal-side crosswalk: `WI_principals.tsv.principal_id` ↔ FTM `d-eid` (manual review of ~525 chain-active principals against FTM canonical entities; substantially simplified by FTM's existing canonicalization).
7. Build the lawmaker-side crosswalk: chain `sponsor_lawmaker_id` (`ocd-person/...`) ↔ FTM `c-t-eid` for all ~165 sitting WI legislators. Use OpenStates `Person.identifiers` if present; otherwise hand-curate.
8. Build the lobbyist personal-contribution slice: name-string match `WI_lobbyists.tsv.name` against FTM `Contributor` (for individuals); 773-row universe, narrow §13.625 windows make this tractable.
9. Materialize `releases/wi/campaign_finance/WI_chain_v2_2025.tsv` (chain + $-flow).

**Phase 2 (conditional on Phase 1 surfacing material coverage gaps that FTM cannot cover) — Selenium-Sunshine port (5-7 days).**

10. Port IRW's R Selenium driver to Python against the new Sunshine UI.
11. Implement the 65K-row batched export loop.
12. Use it ONLY to fill specific gaps surfaced in Phase 1 (likely: `Conduit` field, `Comment`/`SegregatedFundFlag` if either turns out to matter, and any high-traffic committees whose FTM mapping is stale). Do not duplicate the full FTM ingest.

### Why not just start with Selenium-Sunshine?

Because **FTM is a strictly cheaper test of feasibility**, and the worst case for FTM (it's too coarse) is the best case for "now we know exactly which fields we need that FTM doesn't expose," which sharpens the Selenium-Sunshine scope. Doing FTM first risks zero engineering rework; doing Selenium first risks shipping a scraper we didn't need.

### Architectural decisions the implementation branch will need to make (flagged, not decided)

- **Should `wi-campaign-finance` materialize a TSV in `releases/wi/` parallel to the lobbying-side TSVs, or a `releases/wi/campaign_finance/` sub-namespace?** Suggested: sub-namespace, since the schemas are independent and the cadence differs.
- **Cosponsor parsing (parent plan's Refinement #2) — does it block this work?** Recommended ordering from the synthesis doc was B (cosponsor parsing) → C (CFIS). The cost of doing C without B is that the chain's lawmaker side is currently 132 primary sponsors only, growing to ~all 165 legislators when cosponsors are added. Design the lawmaker-side CFIS crosswalk for the full 165, so cosponsor parsing later doesn't trigger a rework.
- **Multi-cycle coverage.** WI lobbying is 2-year biennial; campaign finance is dominated by even-year general election cycles. Decide v1 scope: 2024 cycle (already final) vs 2025-2026 cycle (ongoing) vs both.

---

## 7 — Data licensing, attribution, and usage discipline

FTM publishes terms of use that bind any project consuming their data. Reproduced here for the implementation branch's reference; the operative source is the FTM site's data-export terms.

### Verbatim terms (from FTM site, 2026-06-03)

> **Data Export**
>
> All contents and data on this site is licensed under a Creative Commons Attribution-Noncommercial-Share Alike 3.0 United States License by the National Institute on Money in State Politics
>
> - You may copy, distribute, display, remix, build on, and perform work — and derivative works based upon our database — for noncommercial purposes only. Resulting new works based on Institute data must also acknowledge the Institute and be non-commercial.
> - Information provided by the Institute on our Web site, in custom files or via our APIs is meant for research or educational purposes only.
> - The Institute provides web access and downloads of up to 1,000 records per year to all users. The data will not be used for commercial purposes, used in political campaigns, to solicit contributions, or sold to third-parties.
> - Appropriate credit will be given to the Institute for all reports, articles, mashups, or other visual displays that use our data.
> - The Institute is allowed to cite mashups, reports, articles and other products using data in our fundraising efforts.
> - The Institute reviews all users that exceed usage limits and will grant expanded access to users that meet the Institute's non-commercial, non-electoral criteria.
> - Expanded access will be granted to users associated with accredited academic institutions, journalism organizations and registered 501(c)(3), 501(c)(5) and 501(c)(6) entities.
> - Expanded access will not be granted to electoral entities such as 527s, SuperPACs, party committees, 501(c)(4)s, and candidate campaign committees.
> - Commercial entities can contact the institute for information on obtaining a commercial usage license.

### Practical implications for `lobby_analysis`

1. **License = CC BY-NC-SA 3.0 US.** Any TSV / chart / writeup containing FTM-derived data inherits this license. Attribution is mandatory; commercial use is forbidden; derivative works must propagate the same license.
2. **Project-eligibility self-assessment:** Canary Institute is a 501(c)(3) and `lobby_analysis` is open-source non-electoral research — both meet FTM's expanded-access criteria.
3. **Attribution credit, verbatim string:** **"National Institute on Money in State Politics"** (the legal entity name; OpenSecrets is the parent post-merger, but the Institute is the data steward and is the named licensor in the CC BY-NC-SA grant). Any release including FTM-derived rows must credit them by this name.
4. **Required attribution surfaces** (for the implementation branch):
   - `releases/wi/campaign_finance/README.md` — full attribution paragraph, license name, dataset coverage, link to `followthemoney.org`.
   - Per-TSV header comment (top-of-file metadata block) — short attribution.
   - `README.md` repo-level acknowledgments section — credit alongside Plural Policy (for bills) and the IRW Accountability Project (for legacy WI contributions, if used).
   - Any Suhan-facing slides / weekly updates / write-ups that quote dollar figures derived from FTM data.
5. **Non-commercial discipline.** `lobby_analysis` is currently a non-commercial Corda Fellowship project — fine. If Canary Institute later spins out a commercial offering on top of this infrastructure, the FTM-derived layers would need re-licensing (contact the Institute for a commercial license) OR replacement with directly-scraped CFIS data (where Sunshine's data is public-domain — no FTM-imposed downstream constraints).
6. **Non-electoral discipline.** The TOS explicitly excludes 527s / SuperPACs / party committees / 501(c)(4)s / candidate committees from expanded access. The infrastructure should not be made directly available to those entity types either; the chain's public-research framing must be preserved.
7. **Cannot solicit contributions / be used in political campaigns.** Project framing as research is sufficient as long as outputs stay descriptive (no "support X / oppose Y" voter-targeting overlays).

---

## 8 — What I did NOT investigate (in scope of "clean schema characterization" but not done)

- **Did not enumerate the exact Sunshine UI Export column schema.** Confirmed it's likely the same as IRW's documented `ReceiptsList.csv` shape, but a real browser session against the live SPA would resolve any drift. Two minutes in DevTools the next time someone has Sunshine open in a browser. Now lower-priority since FTM-first plan reduces our Sunshine dependence to a coverage-gap-only fallback.
- **Did not enumerate WI conduit PACs that lobbying principals control.** Could matter: WEC Energy Group's contributions to LeMahieu flow through "WEC PAC" (FTM `d-eid=9524` = "WISCONSIN ENERGY CORP"). The sample query showed FTM has canonicalized this for us, but the full conduit-PAC inventory for the 525 chain-active principals needs to be built once in Phase 1. Manageable.
- **Did not validate the 2015 corporate-contribution-ban scope.** WI eased restrictions in 2015 but I did not pin down which corporate flows are still banned vs. just funneled through PACs. The implementation branch needs a half-day legal-text read on §11.1101 to know what to expect in the data.
- **Did not verify `d-llink` semantics formally.** Hypothesis is "value = contributor's `d-eid` when FTM matches them as a lobbying entity, else `?`." Holds against the sampled flag values. Implementation branch should confirm by cross-checking against FTM's published lobbying-entity list (per state).

These are deliberate stop-points — they belong in implementation, not scoping.

---

## 9 — Provenance / sources

- WI Ethics Commission Sunshine portal — `https://campaignfinance.wi.gov/` (redirects to `https://wi.sunshine.civera.com/`)
- WI Ethics Commission CFIS legacy redirect — `https://cfis.wi.gov/` (301 → Sunshine)
- WI Ethics Commission CF Overview docs — `https://ethics.wi.gov/Resources/CF%20Overview%20-%20State%20Candidate%20Committees.pdf`
- IRW Accountability Project WI dataset — `https://publicaccountability.org/datasets/411/new-wisconsin-ca/`
- IRW WI contribs processing diary — `https://github.com/irworkshop/accountability_datacleaning/blob/master/state/wi/contribs/docs/wi_contribs_diary.md`
- IRW `campfin` R package — `https://github.com/irworkshop/campfin`
- FollowTheMoney — `https://www.followthemoney.org/` and API root `https://api.followthemoney.org/`
- Wisconsin Democracy Campaign — `https://www.wisdc.org/follow-the-money`
- Transparency USA WI explanation — `https://www.transparencyusa.org/data-explanation-for-wisconsin` (HTTP 403 from non-browser; documented for completeness)
- Sample-query session artifacts — [`20260603_ftm_sample_query_lemahieu.md`](20260603_ftm_sample_query_lemahieu.md) (LeMahieu `c-t-eid=3073941`; 2,803-transaction cycle; chain cross-validation; quota-hit observation)
