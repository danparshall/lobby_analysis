<!-- Generated during: convos/20260610_ftm_ny_sample_query.md -->

# FTM API sample query — NY (Stewart-Cousins, 2024 cycle) — DRAFT SKELETON

**Date:** 2026-06-10
**Branch:** `leave-behind-prep`
**Task:** [#44](https://github.com/danparshall/lobby_analysis/issues/44)
**Originating convo:** [`../convos/20260610_ftm_ny_sample_query.md`](../convos/20260610_ftm_ny_sample_query.md)
**Parent convo:** [`../convos/20260609_wi_vs_ny_chain_parity.md`](../convos/20260609_wi_vs_ny_chain_parity.md)
**WI comparison baseline:** [`docs/historical/wi-cfis-scoping/results/20260603_ftm_sample_query_lemahieu.md`](../../../historical/wi-cfis-scoping/results/20260603_ftm_sample_query_lemahieu.md)
**Raw captures:** [`ftm_ny_raw/`](ftm_ny_raw/) — one file per query + `query_log.jsonl`. API key masked as `<FTM_KEY>` in all artifacts.

**STATUS: skeleton — queries not yet run.** Pre-staged while blocked on browser permission grant + key recovery. Sections below mirror the WI LeMahieu writeup for apples-to-apples comparison.

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

_(fill: queries consumed before any gate; verbatim gate wording if it fires — compare against WI's "Institute will be in contact within the next two business days..." for post-OpenSecrets-integration drift.)_

## Opportunistic adds (if executed)

_(cross-cycle 2020 stability; MA/CA triangulation; chain-relevant-sponsor pull.)_

## Implications for #43

_(fill: portability verdict; IP-reachability constraint; canonicalization reuse; taxonomy reuse.)_
