<!-- Generated during: convos/20260610_ftm_ny_sample_query.md -->

# FTM API sample query — NY (Stewart-Cousins, 2024 cycle) — DRAFT SKELETON

**Date:** 2026-06-10
**Branch:** `leave-behind-prep`
**Task:** [#44](https://github.com/danparshall/lobby_analysis/issues/44)
**Originating convo:** [`../convos/20260610_ftm_ny_sample_query.md`](../convos/20260610_ftm_ny_sample_query.md)
**Parent convo:** [`../convos/20260609_wi_vs_ny_chain_parity.md`](../convos/20260609_wi_vs_ny_chain_parity.md)
**WI comparison baseline:** [`docs/historical/wi-cfis-scoping/results/20260603_ftm_sample_query_lemahieu.md`](../../../historical/wi-cfis-scoping/results/20260603_ftm_sample_query_lemahieu.md)
**Raw captures:** [`ftm_ny_raw/`](ftm_ny_raw/) — one file per query + `query_log.jsonl`. API key masked as `<FTM_KEY>` in all artifacts.

**STATUS: blocked at quota (1,083/1,000 records used for the year) — see §7, which is complete. §§2–6 pending expanded-access grant (Exemption Request filed 2026-06-10? — confirm).** Sections mirror the WI LeMahieu writeup for apples-to-apples comparison.

---

## TL;DR

_(fill after queries: tx count + total $, schema-delta verdict, d-llink coverage vs WI ~5%, canonicalization verdict, quota behavior)_

## 0 — Targets and reachability

**Target legislator (primary):** Andrea Stewart-Cousins — Senate Majority Leader since 2019-01-02, re-elected to the post Dec 2024; Senate District 35; `ocd-person/5f3e7bcf-9e43-423b-946b-982cc6ecc154` (Open States). Office-analog of WI's LeMahieu.
**Secondary (quota permitting):** Carl Heastie — Assembly Speaker since 2015-02-03; Assembly District 83; `ocd-person/2049da3a-132c-47b4-b53d-c28b574fff63`.
Both are also the top two disclosed individual lobbying targets in NY `parties_lobbied` (75,286 and 62,574 raw rows respectively, per `ny-disclosure-explore` 20260605 recon).

**Cycle:** 2024 (most recent complete; both targets ran in 2024).

**Reachability finding (2026-06-10, pre-key):** `api.followthemoney.org` AND `www.followthemoney.org` both return connection-timeout 503s from the claude.ai sandbox (GCP egress, 35.238.x.x), while the site loads from Dan's residential browser. Consistent with FTM dropping datacenter-IP traffic, though "still partially down" not excluded. **Load-bearing for #43 if confirmed:** a cloud-hosted ingest pipeline may not be able to reach FTM directly. Query execution for this writeup routed through the browser (Dan's IP) instead of the sandbox.

## 1 — Endpoint and parameter shape: NY deltas vs WI

_(fill: does the WI-decoded param table hold verbatim for s=NY? any new/missing params in `availableGrouping`?)_

## 2 — Identity confirmed

_(fill: c-t-id / c-t-eid for Stewart-Cousins from `?s=NY&y=2024&gro=c-t-id&so=u-tot&sod=0&p=0`; note Heastie's if visible on the same page. Record where on the page she appeared — descending-$ rank is itself a datum.)_

## 3 — Cycle totals

_(fill: #_of_Records + Total_$ for 2024 cycle. WI baseline: LeMahieu 2022 = 2,803 tx / $609,272.)_

## 4 — Transaction-level schema (NY specimen)

_(fill: one full record reproduced; field-by-field match vs WI's 15 fields; NY-specific fields; missing-vs-WI fields; value-distribution sanity. This is the load-bearing section for the 50-state portability claim.)_

## 5 — Donor canonicalization spot-check

_(fill: pick a non-individual donor from §4's page where Original_Name ≠ Contributor; query its d-eid with gro=c-t-id for recipient fan-out. Verify 3-tier taxonomy fields — Broad_Sector / General_Industry / Specific_Business — populate for NY donors.)_

## 6 — d-llink coverage

_(fill: gro=d-llink split for the target's 2024 cycle. WI baseline ~5%.)_

## 7 — Quota behavior

**Gate fired at probe #1 (2026-06-10, ~16:45 UTC), before any NY query ran.** Two surfaces:

1. **Account page** (`/account/download-limits`, logged in): "Your account has accessed
   1,083 of 1,000 records this year. This account allows you to download up to 1,000
   records per year." Plus: "The National Institute on Money in Politics now charges a
   fee for downloading large (greater than 1,000 records/year) datasets... Members of
   the academic and nonprofit advocacy and journalism communities may apply for free
   expanded access."
2. **Export gate** (modal on the show-me results page, on clicking the JSON API link
   for a 1-record aggregate query): "Download Limit Exceeded — You have already
   downloaded 1083 during this period. Downloading 1 additional record would exceed
   your available download limit of 1000."

**Deltas vs WI (2026-06-03):**
- The WI gate read "This account has reached its free API call limit pending Institute
  review... The Institute will be in contact within the next two business days to
  approve continued API usage." The 2026-06-10 gate carries **no review promise** —
  flat refusal with record arithmetic. Consistent with the 2026-06-03 proactive email
  to info@opensecrets.org receiving no response: the Institute-initiated review path
  appears not to have survived the OpenSecrets integration. The **Exemption Request
  form** (`/account` sidebar) is the only documented unblock as of 2026-06-10.
- Enforcement is a **pre-flight record-count check** at the website-export layer (the
  modal fired before the API URL was opened; the probe likely consumed 0 records).
  The raw API-side gate wording (what a #43 pipeline would actually see) is NOT yet
  captured — requires navigating directly to a keyed `api.followthemoney.org` URL.
- Quota semantics confirmed: the limit counts **underlying records per year** (1,000),
  not API calls. Retroactively explains WI's "~15 queries before throttle": ~11 pages
  × ~100 records ≈ 1,083.

**Consequence:** the §2–§6 query sequence is hard-blocked until expanded access is
granted. This writeup documents the blocked state with evidence rather than claiming
NY validation.

## Opportunistic adds (if executed)

_(cross-cycle 2020 stability; MA/CA triangulation; chain-relevant-sponsor pull.)_

## Implications for #43

_(fill: portability verdict; IP-reachability constraint; canonicalization reuse; taxonomy reuse.)_
