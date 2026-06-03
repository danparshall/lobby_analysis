<!-- Generated during: convos/20260603_wi_cfis_access_surface_scoping.md -->

# Phase 4 — WI CFIS access-surface scoping

**Date:** 2026-06-03
**Branch:** `wi-cfis-scoping` (cut off post-merge main `e84d2a1`)
**Originating convo:** [`../convos/20260603_wi_cfis_access_surface_scoping.md`](../convos/20260603_wi_cfis_access_surface_scoping.md)
**Originating plan:** [`docs/historical/wi-allocation-matrix/plans/wi_allocation_matrix.md`](../../../historical/wi-allocation-matrix/plans/wi_allocation_matrix.md) §178-187 (Phase 4)
**Joins against:** `releases/wi/chain/WI_chain_2025.tsv` (115,229 rows, 132 unique primary sponsors), `releases/wi/WI_principals.tsv` (1,108 principal rows), `releases/wi/WI_lobbyists.tsv` (773 lobbyist rows)
**Timebox:** open-ended (Dan, Q4 — chose clean schema characterization over 0.5-day box)
**Code written this branch:** zero (write-only by design)

---

## TL;DR

WI campaign-finance data **is publicly accessible** and **can close the chain's missing $-flow leg**, but the cheapest credible path is **NOT the WI Ethics Commission's own portal** (Sunshine, ex-CFIS), which is a JS-heavy SPA with no documented API and a 65K-row UI-export cap. The cheapest credible path is **FollowTheMoney.org** (National Institute on Money in Politics, now under OpenSecrets), which has 50-state coverage current through 2024, a free REST API for academic/nonprofit use that Canary Institute qualifies for, and a documented entity-ID model that gives stable joins. The fallback if FTM turns out to be too coarse — missing employer/occupation/conduit/lobbyist-window fields — is Selenium-driving Sunshine in 65K-row batches, which the Investigative Reporting Workshop's open-source `accountability_datacleaning` repo has already done for the old CFIS (2008→Jun 2023, 8.39M records, all 18 columns documented). Both paths are workable; FTM is the right first attempt.

**Lobbyist personal contributions** are NOT a separate filing in WI — they're commingled with all other contributions in CFIS/Sunshine and identifiable only by **name-string match** against the lobbyist roster. WI §13.625 imposes narrow "windows" on when lobbyists can give, which makes lobbyist contributions a relatively small slice of CFIS volume and easier to enumerate exhaustively.

**Recommendation: cut a separate `wi-campaign-finance` implementation branch.** Phase 1: prove the FTM path on one sponsor (LeMahieu — already characterized in the SB 28 ROFR finding) end-to-end. Detailed first-phase scope in §6.

---

## 1 — Access surface

| Path | Owner | Coverage | Bulk download | API | Sample-cost | Verdict |
|---|---|---|---|---|---|---|
| **Sunshine** (`campaignfinance.wi.gov` / `wi.sunshine.civera.com`) | WI Ethics Commission via Civera (vendor) | 2008-07 → present | No documented path | Internal Next.js Route Handlers, not public, same-origin CSP-locked | Hours to discover via browser DevTools; then Selenium for production | **Official, but expensive to ingest** |
| **Old CFIS** (`cfis.wi.gov`) | WI Ethics Commission, legacy | Replaced by Sunshine in 2025; 301 → `campaignfinance.wi.gov` | — | — | — | Defunct |
| **FollowTheMoney** (`api.followthemoney.org`) | National Institute on Money in Politics (OpenSecrets, since merger) | All 50 states, current through 2024 election cycle | Yes, via export icons on the website | **Documented REST API**, free key for academic/nonprofit | API-key signup ~10 min; one query ~seconds | **Cheapest credible path** |
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

- **National scope, normalized.** The Institute on Money in Politics has been ingesting all 50 states' campaign finance data since the early 2000s, with a stable entity-ID model (`Entity ID` links a candidate's full history across cycles, races, and committees they registered).
- **API exists and is reachable.** Direct probe — `curl https://api.followthemoney.org/?dataset=1&p=200&y=2024&s=WI&APIKey=` — returns `{"error":"Invalid API Key"}`, confirming the endpoint is alive and the gating mechanism is just a key.
- **Free academic/nonprofit access.** Canary Institute as a public-interest nonprofit qualifies. Signup is at `myFollowTheMoney.org`.
- **Already updated through 2024**, with continuing updates. The Plural Policy chain bills are 2025-2026; FTM may lag the most recent cycle but should have the bulk of 2025-cycle filings.
- **One-API path, not two.** If we go FTM, we don't need to maintain a Sunshine scraper at all — FTM does the scraping for us. The chain ingest becomes a single dependency on a stable API instead of two scrape pipelines.

The risk that justifies a fallback plan: FTM normalizes data for cross-state comparability, which sometimes drops state-specific fields. In WI, the at-risk fields are `Occupation`, `EmployerName`, `Conduit`, and the lobbyist-window flagging in `Comment`. Phase 1 of the implementation branch should pull one query end-to-end and confirm field-level coverage before committing.

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

I did NOT run a Sunshine UI export end-to-end this session, because:

- The Sunshine SPA's API is not curl-reachable (§1.1). Driving the UI requires Playwright or Selenium, which crosses the "write-only branch" line the parent plan set for Phase 4.
- The IRW diary's existence is a stronger proof-of-feasibility than a one-off manual export would be — it documents a worked pipeline at 8.39M-record scale.

I DID confirm:
- **FTM API endpoint is live.** `curl 'https://api.followthemoney.org/?dataset=1&p=200&y=2024&s=WI&APIKey='` returns `{"error":"Invalid API Key"}` — the expected gating response. Endpoint, error format, and gating mechanism are confirmed.
- **Sunshine is on Civera / Next.js.** Documented for the implementation branch's tech-decision step.
- **WisDC is behind Sucuri CloudProxy.** Documented as not a candidate for automated ingest.

**The smallest end-to-end test belongs in Phase 1 of the implementation branch**, not here. Specifically: with a free FTM API key, query for contributions to Devin LeMahieu's candidate committee in 2024–2026 cycles, and confirm the field-level coverage matches what the IRW diary documents for raw CFIS. LeMahieu is the right sample target — the chain's SB 28 / ROFR finding (see `docs/historical/wi-allocation-matrix/results/20260602_lemahieu_bill_inspection.md`) gives us 29 principals and a list of expected donors against which to spot-check FTM's coverage.

---

## 6 — Recommendation

**Yes, cut a separate `wi-campaign-finance` implementation branch.**

The CFIS leg is structurally separable from the lobbying-chain ingest (different source, different schema, different temporal cadence), and the work to close it isn't a "small follow-on" to `wi-allocation-matrix` — it has its own design decisions (FTM vs Selenium-Sunshine vs hybrid), its own entity-resolution work, and benefits from being on a clean branch with focused tests.

### Suggested first phase of `wi-campaign-finance`

**Phase 1 — FTM viability test (2-3 days).**

1. Sign up for free academic/nonprofit FTM API key via `myFollowTheMoney.org` (Canary Institute affiliation).
2. Build a 50-line Python client (`httpx` + `pydantic`) hitting `api.followthemoney.org/` with the WI dataset filter.
3. Query for contributions received by Devin LeMahieu's candidate committee, 2024–2026 cycles.
4. Inspect the returned schema: which of (donor name, occupation, employer, amount, date, conduit, comment) come through cleanly?
5. Spot-check against the 29 SB 28 principals from `docs/historical/wi-allocation-matrix/results/20260602_lemahieu_bill_inspection.md` — does FTM see contributions from ATC Management, WEC Energy Group, WI Industrial Energy Group, etc.?
6. Write a phase-1 results doc with the GO/NO-GO call on FTM as the primary source.

**Phase 2 (conditional on Phase 1 GO) — full ingest + chain join (3-5 days).**

7. Pull WI 2025-2026 contributions from FTM into a TSV with stable schema.
8. Build the principal-name canonicalization layer (port IRW's `campfin::normal_*()` to Python or use `recordlinkage`).
9. Build the lawmaker-side crosswalk: try OpenStates `Person.identifiers` first; fall back to manual ~165-row crosswalk if needed.
10. Build the lobbyist personal-contribution slice (small N, manual review feasible for v1).
11. Materialize `WI_contributions_2025.tsv` and `WI_chain_v2_2025.tsv` (chain + $-flow).

**Phase 3 (conditional on Phase 1 NO-GO or Phase 2 surfacing coverage gaps) — Selenium-Sunshine port (5-7 days).**

12. Port IRW's R Selenium driver to Python against the new Sunshine UI.
13. Implement the 65K-row batched export loop.
14. Re-validate against the FTM Phase 1 results for any overlap window.
15. Rejoin to the chain as in Phase 2.

### Why not just start with Selenium-Sunshine?

Because **FTM is a strictly cheaper test of feasibility**, and the worst case for FTM (it's too coarse) is the best case for "now we know exactly which fields we need that FTM doesn't expose," which sharpens the Selenium-Sunshine scope. Doing FTM first risks zero engineering rework; doing Selenium first risks shipping a scraper we didn't need.

### Architectural decisions the implementation branch will need to make (flagged, not decided)

- **Should `wi-campaign-finance` materialize a TSV in `releases/wi/` parallel to the lobbying-side TSVs, or a `releases/wi/campaign_finance/` sub-namespace?** Suggested: sub-namespace, since the schemas are independent and the cadence differs.
- **Cosponsor parsing (parent plan's Refinement #2) — does it block this work?** Recommended ordering from the synthesis doc was B (cosponsor parsing) → C (CFIS). The cost of doing C without B is that the chain's lawmaker side is currently 132 primary sponsors only, growing to ~all 165 legislators when cosponsors are added. Design the lawmaker-side CFIS crosswalk for the full 165, so cosponsor parsing later doesn't trigger a rework.
- **Multi-cycle coverage.** WI lobbying is 2-year biennial; campaign finance is dominated by even-year general election cycles. Decide v1 scope: 2024 cycle (already final) vs 2025-2026 cycle (ongoing) vs both.

---

## 7 — What I did NOT investigate (in scope of "clean schema characterization" but not done)

- **Did not enumerate the exact Sunshine UI Export column schema.** Confirmed it's likely the same as IRW's documented `ReceiptsList.csv` shape, but a real browser session against the live SPA would resolve any drift. Two minutes in DevTools the next time someone has Sunshine open in a browser.
- **Did not register an FTM API key or run one live query.** Punted to Phase 1 of the implementation branch deliberately, since it's a sign-up-then-API-call test that belongs in the implementation flow, not the scoping flow.
- **Did not enumerate WI conduit PACs that lobbying principals control.** Could matter: WEC Energy Group's contributions to LeMahieu may flow through "WEC PAC" or similar rather than from "WEC Energy Group, Inc." directly. The implementation branch's principal-side canonicalization needs to learn these aliases.
- **Did not validate the 2015 corporate-contribution-ban scope.** WI eased restrictions in 2015 but I did not pin down which corporate flows are still banned vs. just funneled through PACs. The implementation branch needs a half-day legal-text read on §11.1101 to know what to expect in the data.

These are deliberate stop-points — they belong in implementation, not scoping.

---

## 8 — Provenance / sources

- WI Ethics Commission Sunshine portal — `https://campaignfinance.wi.gov/` (redirects to `https://wi.sunshine.civera.com/`)
- WI Ethics Commission CFIS legacy redirect — `https://cfis.wi.gov/` (301 → Sunshine)
- WI Ethics Commission CF Overview docs — `https://ethics.wi.gov/Resources/CF%20Overview%20-%20State%20Candidate%20Committees.pdf`
- IRW Accountability Project WI dataset — `https://publicaccountability.org/datasets/411/new-wisconsin-ca/`
- IRW WI contribs processing diary — `https://github.com/irworkshop/accountability_datacleaning/blob/master/state/wi/contribs/docs/wi_contribs_diary.md`
- IRW `campfin` R package — `https://github.com/irworkshop/campfin`
- FollowTheMoney — `https://www.followthemoney.org/` and API root `https://api.followthemoney.org/`
- Wisconsin Democracy Campaign — `https://www.wisdc.org/follow-the-money`
- Transparency USA WI explanation — `https://www.transparencyusa.org/data-explanation-for-wisconsin` (HTTP 403 from non-browser; documented for completeness)
