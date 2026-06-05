# Project Summary — State Lobbying Disclosure Data Availability

**Compiled:** 2026-06-05
**Full conversation:** available in the Claude Web UI as **`State lobby disclosure data availability report`**
**Project context:** Canary Institute / Corda Democracy Fellowship / Analogy Group (all not-for-profit; commercial-use data restrictions do not apply)

---

## Objective

Map the availability and accessibility of **state-level** lobbying disclosure data across all 50 states, in service of assembling an influence chain:

> **company → lobbyist → lawmaker → bill**, with money on the edges
> (e.g. "company W spent $X via lobbyist Y on bill Z," joined to "lawmaker sponsored/voted on bill Z")

County/municipal lobbying regimes are out of scope throughout.

---

## What's in this folder

| File | Contents |
|---|---|
| `lobbying-disclosure-sample.md` | Deep 6-state schema (OH, WI, MI, NC, FL, MD) on the two-axis **access × granularity** model, with the derived rollup. The methodological worked example. |
| `lobbying-disclosure-50state-tracker.md` | Tier-1 tracker of official state sources (portal, bulk availability, legal basis) for the states verified during the live/search pass. |
| `lobbying-chain-closure.md` | **The key strategic deliverable.** Reframes the problem as chain *connectivity* and tiers states by whether the influence chain closes. |
| `SUMMARY.md` | This file. |

| `research-01-official-50state-sources.md` | Full official-sources research report — per-state access×granularity for all six categories, national summary table, well-supported negatives. |
| `research-02-thirdparty-pipelines.md` | Full third-party pipelines report — OpenSecrets/FollowTheMoney, The Accountability Project, CCDC, academic datasets, per-state pipeline index. |

(Both research reports were also rendered as artifacts in the Web UI conversation; the on-disk versions here are reconstructed from those artifacts and are the canonical record.)

---

## Schema developed

**Six data categories:** principals (companies/employers), lobbyists, lawmakers, bills, activity & expenditure (spending), positions.
- "Positions" splits into **stance** (support/oppose/neutral — very rare) and **linkage** (principal↔matter, no direction — common). Project uses **linkage**.

**Two independent axes per category:**
- `access`: download / api / open-data / search-only / paid / none-collected / unknown
- `granularity`: transactional / aggregate / directory / n-a

**Three distinct legal axes** (a recurring theme):
1. Can you get it? (access)
2. Can you scrape it? (the binding instrument is the site **Terms of Use**, not robots.txt)
3. Can you *use* it? (use-restrictions — WA and MI bar commercial use of person-lists; **moot for this not-for-profit project**)

**Negatives discipline:** "none-collected" (confirmed dead-end, requires statutory/structural evidence) is kept strictly distinct from "search-only" (exists, not bulk-exported — routable) and "unknown" (not found ≠ confirmed absent).

---

## Central strategic finding (chain-closure)

The chain has **two halves that join on the bill key:**
- **Lobbying half** (company → lobbyist → bill + $) comes from disclosure data.
- **Legislative half** (lawmaker → bill, via sponsorship/committee/votes) comes from **Open States / Plural**, which covers all 50 states with real bill IDs — *not* from lobbying data.

**Consequence:** the near-universally-empty "lawmaker" column in lobbying data matters far less than it appears — **provided the lobbying data reaches a real bill number.** Bill-number granularity is therefore the linchpin. Subject-matter coding ("Taxation") severs the bridge to Open States; an actual bill number (SB 1047) closes it.

**Standing architectural decision:** source the lawmaker→bill edge from Open States for all 50 states as a bill-keyed spine. Each state's lobbying data then only needs to reach a real bill number to light up the full chain.

### State tiers

- **Tier 1 — chain closes from bulk alone:** **New York, Colorado, Wisconsin.** (CO uniquely also has directional stance. WI needs one targeted query for itemized vs. aggregate spending.)
- **Tier 2 — breaks only at the bill join (big valuable states):** CA, TX, IL, WA, FL, NC, MD. Break because they code by subject-matter, not bill number. Close via **targeted queries** (resolve subject→bill on per-filing detail pages) or **imputation** (subject × session × industry → probable bills).
- **Tier 3 — access-constrained:** **Michigan** (bill data confirmed *not collected* — chain cannot reach bill level regardless of effort; scraping also explicitly banned). **Virginia** (CAPTCHA-gated, but uniquely *names officials lobbied* — the one place to study the lobbyist→lawmaker edge as disclosed rather than imputed).

### Methodological order of operations
1. Build the bulk skeleton (company→lobbyist→bill/subject→$).
2. Identify the missing/coarse edge per state.
3. Fill gaps with **targeted queries** (a few hundred specific lookups — legally and operationally cleaner than wholesale scraping, which the bulk skeleton makes unnecessary).
4. Impute residual gaps where targeted queries don't reach.

---

## Best-bet states: thoroughness & obtainability

**New York — deepest dataset + highly obtainable.** Six datasets on Open NY (Socrata), ~278M records, 2019–present. Transactional compensation AND expenses (not banded/aggregate), bill-number-level linkage, and uniquely publishes a "parties lobbied" tabulation (a piece of the lawmaker edge in-corpus). API + downloads + data dictionaries, no paywall, no use-restriction. Gaps: clean bulk starts 2019; no directional stance. **Start here for end-to-end pipeline validation.**

**Colorado — only observed stance, very obtainable.** Closes the chain and adds directional positions (support/oppose/amend/monitor per client per bill, with date ranges) — the only bulk stance source in the US. Bill-number granularity; monthly income/expenditure. TXT exports that **update hourly** plus a Socrata presence; no paywall. Gaps: smaller universe than NY; no lawmaker-contact data (reach lawmakers via bill→Open States). **Use to build/calibrate any stance methodology before imputing stance elsewhere.**

**Verification caveat:** NY and CO assessments are high-confidence from portal documentation and the research pass, **not** column-level confirmed by pulling files. Recommended next step before pipeline design: pull one file from each and inspect the actual schema.

---

## Open items / next steps

1. **Pilot the Tier-2 subject→bill resolution rate** (one state, one session) before committing query budget — the whole Tier-2 strategy rests on the untested assumption that per-filing detail pages name specific bills even when bulk exports carry only the subject code. If resolution is low, Tier 2 degrades to imputation-only.
2. **Column-level verification** of NY and CO schemas (see caveat above).
3. **~28 unverified states** still need the deep access×granularity pass; several (Iowa, Rhode Island) are flagged as likely bill-level and would join Tier 1 if confirmed.
4. **Michigan live-browser check** remains the one outstanding access item (entellitrak vendor portal blocked direct read; would need a one-time domain authorization) — though MI's confirmed lack of bill-level data limits its value regardless.
5. Optionally **save the two Web-UI research-report artifacts** into this folder for a complete on-disk record.
