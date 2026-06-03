<!-- Generated during: convos/20260603_wi_cfis_access_surface_scoping.md -->

# FTM API sample query — LeMahieu 2022 cycle (end-to-end)

**Date:** 2026-06-03
**Branch:** `wi-cfis-scoping`
**Originating convo:** [`../convos/20260603_wi_cfis_access_surface_scoping.md`](../convos/20260603_wi_cfis_access_surface_scoping.md)
**Companion writeup:** [`20260603_phase_4_cfis_scoping.md`](20260603_phase_4_cfis_scoping.md)
**API key in transcript:** Dan pasted his FTM key into chat during the session. All artifacts here have `<FTM_KEY>` masking; raw curls in the bash history retain the key (low-stakes, read-only API).

This is the sample-query artifact for the parent plan's Phase 4 spec step 44 ("Try one sample query end-to-end against a known WI lawmaker") — which the main scoping doc had punted as belonging in the implementation branch. With Dan's account in hand, we executed it now.

---

## TL;DR

A six-query sequence against `api.followthemoney.org/` produced:
- LeMahieu's FTM identity (`c-t-id=325785` for the 2022 cycle / `c-t-eid=3073941` career).
- The full 15-field transaction-level schema (vs. 18 fields in raw CFIS — see §3).
- Two pieces of chain cross-validation: WEC Energy's PAC sent LeMahieu $2,000 in 2019 (Record 2 in §3); Xcel Energy appeared in LeMahieu's top-25 2022-cycle donors (§4). Both companies are top-tier SB 28 lobbying filers per the chain's `20260602_lemahieu_bill_inspection.md`.
- Confirmation that **FTM has already canonicalized the donor entities** — every transaction row has a `Contributor` field with FTM's `d-eid` (a stable entity ID) alongside the raw `Original_Name`. We do not have to build the principal-side name-canonicalization layer; we map our 1,108 principals to FTM's `d-eid` once.
- Confirmation that **`d-llink` ("Lobbying Entity?") is a partial flag**, not a complete shortcut: ~5% of LeMahieu's 2022 contributions are flagged with a lobbying-entity link; 95% are unflagged.
- Confirmation that **the basic-tier API quota is much tighter than the TOS's 1,000-records/year reads** — Dan's account hit the quota wall after ~15 queries in this session, returning the message: *"This account has reached its free API call limit pending Institute review of data usage. The Institute will be in contact within the next two business days to approve continued API usage per the data usage terms and conditions."*

The practical implication: **the FTM path is cheap enough to commit to, but Phase 1 of `wi-campaign-finance` must START with the expanded-access request to `info@opensecrets.org`** and the 2-business-day approval wait, then resume.

---

## 1 — Endpoint and parameter shape (decoded)

The FTM API root is a single PHP endpoint:

```
https://api.followthemoney.org/?<params>&APIKey=<key>&mode={json|xml|html}
```

Parameter dimensions (from the `availableGrouping` dict in JSON responses):

| Token | Meaning | Example value |
|---|---|---|
| `dt` | Dataset type | `1` = contributions (others: not yet enumerated) |
| `s` | Election Jurisdiction (state) | `WI` |
| `y` | Election Year | `2022`, `2024` |
| `f-s` | Filing Jurisdiction | `WI` |
| `f-eid` | Filer (committee entity ID) | — |
| `c-t-id` | Candidate ID (per-cycle) | `325785` (LeMahieu 2022) |
| `c-t-eid` | Candidate Entity ID (career-spanning, stable) | `3073941` (LeMahieu) |
| `c-r-osid` | Office Sought (specific) | `8757` (WI Senate District 9) |
| `c-r-ot` | Office Type (general) | — |
| `d-id` | Contribution record ID | — |
| `d-eid` | Contributor Entity ID (canonicalized donor) | `9524` (WISCONSIN ENERGY CORP) |
| `d-et` | Contributor Type | `3` = Non-Individual |
| `d-nme` | Original Name (raw filer's spelling) | `"WEC ENERGY GROUP PAC (WEC PAC)"` |
| `d-amt` / `d-dte` | Amount / Date | `2000.00` / `2019-05-04` |
| `d-typ` | Type of Transaction | `DIR` = direct (codes: `EH`, etc. — not enumerated) |
| `d-llink` | "Lobbying Entity?" flag (see §5) | partial, see §5 |
| `d-ccg` / `d-cci` / `d-ccb` | Broad Sector / General Industry / Specific Business | `"Energy & Natural Resources"` / `"Electric Utilities"` / `"Gas & electric utilities"` |
| `d-par` / `d-empl` / `d-occupation` | Parent Org / Employer / Occupation (for individuals) | — |
| `d-ad-cty` / `d-ad-st` / `d-ad-zip` | Donor address | `MILWAUKEE` / `WI` / `53203` |
| `d-ins` | In-State? | `1` |
| `gro=` | Group-by dimension | `gro=c-t-id` / `gro=d-eid` / `gro=d-llink` |
| `so=` / `sod=` | Sort key / direction | `so=u-tot&sod=0` = descending total $ |
| `p=` | Page (0-indexed, 100 records/page) | `p=0`, `p=1`, `p=2` |

**Lookup workflow:**
1. To find a candidate's `c-t-eid`: query `?s=<STATE>&y=<YEAR>&gro=c-t-id&...` and page through. Each result row has the candidate's `c-t-id` (per-cycle) and `c-t-eid` (career).
2. To pull contributions to that candidate: query `?c-t-eid=<EID>&y=<YEAR>&gro=d-id&...` for transaction-level, or `?c-t-eid=<EID>&y=<YEAR>&gro=d-eid&...` for donor-level rollup.

---

## 2 — LeMahieu identity confirmed

Query: `?s=WI&y=2022&gro=c-t-id&mode=json&p=0..2`. Found in page 0 (record 15):

```json
{
  "Candidate":        {"token":"c-t-id",      "id":"325785",  "Candidate":       "LEMAHIEU, DEVIN"},
  "Candidate_Entity": {"token":"c-t-eid",     "id":"3073941", "Candidate_Entity":"LEMAHIEU, DEVIN"},
  "Election_Status":  {"token":"c-t-ftsts",   "id":"Won-General"},
  "Specific_Party":   {"token":"c-t-pt",      "id":"139",     "Specific_Party":  "REPUBLICAN"},
  "Election_Jurisdiction": {"token":"s",      "id":"WI"},
  "Election_Year":    {"token":"y",           "id":"2022"},
  "Office_Sought":    {"token":"c-r-osid",    "id":"8757",    "Office_Sought":   "SENATE DISTRICT 009"},
  "Incumbency_Status":{"token":"c-t-ico",     "id":"I",       "Incumbency_Status":"Incumbent"},
  "#_of_Records":     {"#_of_Records":"2803"},
  "Total_$":          {"Total_$":"609272.06"}
}
```

LeMahieu's 2022 cycle: **2,803 transactions totaling $609,272**. This is the FTM-cycle definition, which includes contributions back to the previous cycle's end (so LeMahieu's 2022 cycle covers contributions roughly 2017→2022).

For the 132-unique-sponsor crosswalk the implementation branch needs, this query shape (page through `gro=c-t-id` filtered by state and election year) is the lookup mechanism. The lawmaker-side crosswalk is then:

```
ocd-person/...  (from chain)  ↔  FTM c-t-eid  (from this query)
```

joined by name + party + chamber/district. Per-cycle `c-t-id` is the WI Ethics Commission's per-cycle filing identifier in disguise (one per candidacy per cycle); `c-t-eid` is the career-stable join key. **For the chain join, use `c-t-eid`.**

---

## 3 — Transaction-level schema (15 fields)

Query: `?c-t-eid=3073941&y=2022&gro=d-id&mode=json&p=0` returned 100 transaction rows (of the 2,803 total in cycle). Record 2 is reproduced below as the schema specimen:

```json
{
  "record_id": 2,
  "request":   "dt=1&y=2022&c-t-eid=3073941&d-id=185523204",
  "Original_Name":   {"token":"d-nme", "id":"19690031", "Original_Name":"WEC ENERGY GROUP PAC (WEC PAC)"},
  "Contributor":     {"token":"d-eid", "id":"9524",     "Contributor":  "WISCONSIN ENERGY CORP"},
  "Type_of_Contributor": {"token":"d-et", "id":"3",     "Type_of_Contributor":"Non-Individual"},
  "Specific_Business":   {"token":"d-ccb","id":"104",   "Specific_Business":"Gas & electric utilities"},
  "General_Industry":    {"token":"d-cci","id":"36",    "General_Industry": "Electric Utilities"},
  "Broad_Sector":        {"token":"d-ccg","id":"5",     "Broad_Sector":     "Energy & Natural Resources"},
  "Amount":              {"token":"d-amt","id":"2000.00","Amount":"2000.00"},
  "Date":                {"token":"d-dte","id":"2019-05-04","Date":"2019-05-04"},
  "Last_Updated":        {"token":"d-ludte","id":"2020-08-14","Last_Updated":"2020-08-14"},
  "Type_of_Transaction": {"token":"d-typ","id":"1",     "Type_of_Transaction":"DIR"},
  "Purpose":             {"token":"d-purp","id":"185523204","Purpose":""},
  "City":  {"token":"d-ad-cty","id":"MILWAUKEE", "City":"MILWAUKEE"},
  "State": {"token":"d-ad-st", "id":"WI",        "State":"WI"},
  "Zip":   {"token":"d-ad-zip","id":"53203",     "Zip":"53203"},
  "In-State": {"token":"d-ins", "id":"1",        "In-State":"1"}
}
```

### Mapping FTM schema → raw CFIS columns (from IRW diary)

| Raw CFIS column | FTM equivalent | Notes |
|---|---|---|
| `TransactionDate` | `Date` (`d-dte`) | ✓ |
| `FilingPeriodName` | — | Not exposed; FTM aggregates to election cycle |
| `ContributorName` | `Original_Name` (`d-nme`) | ✓ — raw filer's spelling |
| `ContributionAmount` | `Amount` (`d-amt`) | ✓ |
| `AddressLine1`, `AddressLine2` | — | Not exposed; FTM exposes lat/long via `d-ad-lat`/`d-ad-long` (Advanced) |
| `City` | `City` (`d-ad-cty`) | ✓ |
| `StateCode` | `State` (`d-ad-st`) | ✓ |
| `ZIP` | `Zip` (`d-ad-zip`) | ✓ |
| `Occupation` | `d-occupation` (Advanced) | ✓ — separate dimension, available on query |
| `EmployerName` | `d-empl` (Advanced) | ✓ |
| `EmployerAddress` | — | Not exposed in transactional shape |
| `ContributorType` | `Type_of_Contributor` (`d-et`) | ✓ |
| `ReceivingCommitteeName` | — (recipient already in query filter) | Implicit |
| `ETHCFID` | — | **Not exposed** — FTM uses its own `c-t-eid` / `c-t-id` instead of pass-through Ethics Commission IDs |
| `Conduit` | — | Possibly under `d-par` (Parent Org); not confirmed |
| `Branch` | `Office_Sought` (`c-r-osid`) | ✓ — at the candidate, not transaction, level |
| `Comment` | — | Not exposed |
| `72 Hr. Reports` | — | Not exposed |
| `SegregatedFundFlag` | — | Not exposed |
| — | **`Contributor` (`d-eid`) — canonicalized donor entity ID** | **NEW — not in raw CFIS** |
| — | **`Specific_Business`/`General_Industry`/`Broad_Sector`** | **NEW — FTM's industry classification** |
| — | **`d-llink` — lobbying-entity flag** | NEW — see §5 |

**The trade:** FTM drops `EmployerAddress`, `Conduit` (probably), `Comment`, `72Hr. Reports`, `SegregatedFundFlag`, `FilingPeriodName`, `ETHCFID`, and `AddressLine1/2` from the raw CFIS schema. In exchange it adds **entity canonicalization** (the single most valuable addition), a **three-level industry taxonomy** (which would otherwise be expensive to build), and the partial-coverage `d-llink` lobbying flag. For our use case — joining principal-donations and lobbyist-donations into the chain — the FTM additions are worth substantially more than the dropped fields.

**The one CFIS field whose loss matters:** `ETHCFID`, which we'd hoped to use as the stable recipient-side join key. FTM substitutes its own `c-t-eid`, so the lawmaker-side crosswalk is just translated from "`ETHCFID → ocd-person/...`" to "`c-t-eid → ocd-person/...`". Same shape, different anchor; not actually worse.

---

## 4 — Top-25 donors to LeMahieu (2022 cycle, descending by total $)

Query: `?c-t-eid=3073941&y=2022&gro=d-eid&mode=json&so=u-tot&sod=0&p=0`.

| # | Contributor | Records | Total $ | FTM `d-eid` |
|---:|---|---:|---:|---:|
| 1 | WISCONSIN REPUBLICAN PARTY | 1 | $15,863.00 | 4957 |
| 2 | AT&T | 3 | $3,500.00 | 259 |
| 3 | GENERAL MOTORS | 5 | $2,750.00 | 1087 |
| 4 | PARKS, RICK *(individual)* | 3 | $2,350.00 | 15171261 |
| 5 | VELDBOOM, GORDON J *(individual)* | 4 | $2,250.00 | 2990196 |
| 6 | LEIBHAM, HEATHER *(individual)* | 3 | $2,100.00 | 3444890 |
| 7 | BNSF RAILWAY CO | 3 | $2,000.00 | 435 |
| 8 | CHARTER COMMUNICATIONS LLC | 1 | $2,000.00 | 557 |
| 9 | ELI LILLY & CO | 3 | $2,000.00 | 900 |
| 10 | HOME DEPOT | 2 | $2,000.00 | 1261 |
| 11 | JOHNSON CONTROLS | 3 | $2,000.00 | 1399 |
| 12 | LIBERTY MUTUAL CO | 4 | $2,000.00 | 1540 |
| 13 | MICROSOFT CORP | 1 | $2,000.00 | 1725 |
| 14 | MOLINA HEALTHCARE | 1 | $2,000.00 | 1753 |
| 15 | NORTHWESTERN MUTUAL LIFE INSURANCE | 2 | $2,000.00 | 1909 |
| 16 | TRAVELERS COMPANIES | 3 | $2,000.00 | 2636 |
| 17 | UNION PACIFIC CORP | 2 | $2,000.00 | 2675 |
| 18 | UNITEDHEALTH GROUP | 3 | $2,000.00 | 2692 |
| 19 | ALTRIA CLIENT SERVICES | 3 | $2,000.00 | 2695 |
| 20 | WALMART | 4 | $2,000.00 | 2772 |
| 21 | **XCEL ENERGY** | 4 | $2,000.00 | 2908 |
| 22 | WISCONSIN REALTORS ASSOCIATION | 2 | $2,000.00 | 4459 |
| 23 | WISCONSIN CREDIT UNION LEAGUE | 3 | $2,000.00 | 5524 |
| 24 | MILWAUKEE POLICE ASSOCIATION | 3 | $2,000.00 | 7812 |
| 25 | WISCONSIN ELECTRIC COOPERATIVE ASSOCIATION | 1 | $2,000.00 | 9518 |

### Chain cross-validation

The chain's `20260602_lemahieu_bill_inspection.md` identifies the SB 28 / ROFR coalition as 29 distinct principals filing lobbying effort on the bill. We can spot-check FTM's donor list against that lobbying-side coalition. Matches in the top-25:

- **Xcel Energy** (#21 donor, $2,000) — chain #7 SB 28 filer at 39.9 hrs.
- **Wisconsin Electric Cooperative Association** (#25 donor, $2,000) — adjacent to chain entities; the chain has "Municipal Electric Utilities of Wisconsin" at 28.1 hrs (different org). Worth confirming with the implementation branch whether WECA and Municipal Electric Utilities map to the same FTM entity or two distinct ones.

Not in top-25 but confirmed in transaction-level page 0:

- **WEC Energy Group** (Record 2, $2,000 on 2019-05-04, FTM eid 9524 = "WISCONSIN ENERGY CORP") — chain #2 SB 28 filer at 134.4 hrs.

Conspicuously absent from top-25 donors (within the 2022 cycle):

- **ATC Management** — chain #1 SB 28 filer at 331 hrs. ATC is a transmission-only company without an obvious candidate-committee PAC vehicle; their political activity may flow through industry associations (Wisconsin Utilities Association, which IS in the chain's principal list) rather than direct contributions.
- **Wisconsin Industrial Energy Group** — chain #3 SB 28 filer at 124.3 hrs.

**Interpretive finding:** the top-donor list looks like Senate-Majority-Leader-default — broad multi-industry corporate PAC giving at the $2K WI cap, dominated by party/AT&T/healthcare/insurance/utilities/realtors. The SB 28 / electric-utility coalition's lobbying-side concentration (29 filers, electric-utility-dominated) is NOT visible at LeMahieu's top-donor view — it's diluted by his broader party-leader receipts. This is consistent with the chain's earlier finding that the lobbying-side concentration on SB 28 is a single-bill phenomenon, not a sustained-donor-base phenomenon. **The chain's signal would not have been findable from CFIS contribution data alone** — it needs the lobbying-side activity data the chain already has. This argues strongly that CFIS is a **complement** to the chain, not a substitute for the lobbying data; both legs are needed to see the full picture.

---

## 5 — `d-llink` ("Lobbying Entity?") semantics

Query: `?c-t-eid=3073941&y=2022&gro=d-llink&mode=json`. Result: 77 flag buckets across the 2,803 contributions.

```
flag='?'            records=2,659  total=$498,078.10   ← UNFLAGGED bucket (95% of records)
flag='259'          records=    3  total=  $3,500.00   ← AT&T (eid=259)
flag='1087'         records=    5  total=  $2,750.00   ← General Motors (eid=1087)
flag='435'          records=    3  total=  $2,000.00   ← BNSF Railway (eid=435)
flag='557'          records=    1  total=  $2,000.00   ← Charter Communications (eid=557)
...
```

**Semantic hypothesis (not fully confirmed):** `d-llink` value = FTM `d-eid` of the lobbying-entity-of-record when the contributor maps to a known lobbying entity, or `?` (null) when no mapping. The flag values match the top-donor `d-eid` values directly (AT&T eid=259 matches flag=259, etc.), so this is "this contribution is from a contributor that FTM also tracks as a lobbying entity."

**Coverage:** ~5% of LeMahieu's 2022 contributions are flagged (~144 records). The flagged set is dominated by corporate PACs (the $2K WI-cap cluster). Individual personal contributions — including those from registered WI lobbyists — appear in the unflagged "?" bucket.

**Implication for the chain join:** `d-llink` is a useful soft signal for the principal-side donor join (it confirms FTM thinks the donor is lobbying-active), but it is NOT a substitute for the principal-side canonicalization work. The lobbyist personal-contribution slice — the smaller piece we care about for the `lobbyist → lawmaker` leg — is NOT recoverable from `d-llink` alone; it requires the name-string match against `WI_lobbyists.tsv` we described in the main scoping doc.

---

## 6 — Quota hit — what we learned

After ~15 queries in this session (six covering LeMahieu, the rest exploratory), Dan's account returned:

> `{"error":"This account has reached its free API call limit pending Institute review of data usage. The Institute will be in contact within the next two business days to approve continued API usage per the data usage terms and conditions."}`

This is much more restrictive than the TOS's documented "1,000 records/year" cap would suggest — the quota appears to count something closer to "API calls" than "records returned," OR record-rollup queries count their aggregated underlying records.

**Practical implication:** the basic tier is for ONE-OFF schema exploration, not for any production-shape work. The implementation branch's Phase 0 is a **calendar wait for the Institute's automatic review**, not a proactive email application.

The error response wording — "The Institute will be in contact within the next two business days" — combined with the TOS's "The Institute reviews all users that exceed usage limits and will grant expanded access to users that meet the Institute's non-commercial, non-electoral criteria" — reads as **review-on-exceed, initiated by the Institute, not by the user**. No documented application form exists; an earlier search hit suggesting "academic users may apply for expanded access" turned out to refer to this same automatic review, not a separate application process.

**Workflow:**

1. Quota exceeded → account flagged → wait.
2. **When the Institute's review email arrives** (per the documented 2-business-day SLA), reply with:
   - Affiliation: Canary Institute 501(c)(3), Corda Democracy Fellowship at Analogy Group.
   - Project framing: non-commercial open-source state-level lobbying-disclosure data infrastructure; repo `github.com/danparshall/lobby_analysis`.
   - Planned use: WI 2024-2026 cycle contributions to ~165 sitting state legislators (~few hundred K transactions estimated) to link to existing lobbying-disclosure registrations.
   - Compliance commitment: outputs non-commercial, non-electoral, attributed to "National Institute on Money in State Politics" per CC BY-NC-SA 3.0 US.
   - Optional: link to `releases/wi/chain/WI_chain_2025.tsv` + `docs/active/wi-cfis-scoping/results/20260603_phase_4_cfis_scoping.md` as evidence of the upstream research context.
3. **Only proactively email `info@opensecrets.org` if no contact arrives by ~end of business day 3-5.** Phrase as a status check on the existing review, not a new application.

---

## 7 — Net effect on the scoping recommendation

The Phase 4 scoping writeup's recommendation (cut a separate `wi-campaign-finance` implementation branch) **stands and is strengthened**. The empirical findings from this sample query:

1. **Strengthen the FTM-first plan** — the donor-side canonicalization is already done; the schema is good enough for the chain join; the LeMahieu / WEC / Xcel cross-validation confirms FTM sees the right Wisconsin entities.
2. **Add a hard prerequisite** — Phase 1 must include "submit expanded-access request, wait 2 business days." This adds 2 calendar days to the timeline but is non-negotiable.
3. **Reduce the principal-side canonicalization scope** from "build a fuzzy-matcher across 1,108 principals" to "build a one-time crosswalk between `WI_principals.tsv.principal_id` and FTM `d-eid`." That's a manual-review task on ~525 chain-active principals, no `recordlinkage` library needed.
4. **Confirm the lawmaker-side join shape** — `c-t-eid` is the FTM-side anchor. `c-t-eid ↔ ocd-person/...` is a ~165-row crosswalk for sitting WI legislators.
5. **Confirm the lobbyist personal-contribution slice needs manual name-string matching** — `d-llink` is too sparse on individuals.

---

## 8 — Provenance

- Sample-query script `/tmp/probe_ftm_lemahieu.py` (Python 3.13, stdlib only)
- Sample-query response artifacts (local-only; not committed): `/tmp/ftm_lemahieu_llink.json`, `/tmp/ftm_lemahieu_donors.json`, `/tmp/ftm_lemahieu_top_desc.json`, `/tmp/ftm_lemahieu_txns_p0.json`
- FTM API root: `https://api.followthemoney.org/`
- Companion writeup: [`20260603_phase_4_cfis_scoping.md`](20260603_phase_4_cfis_scoping.md)
