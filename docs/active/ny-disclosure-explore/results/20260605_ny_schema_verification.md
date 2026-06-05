<!-- Generated during: convos/20260605_ny_pipeline_kickoff.md (Phase 0 execution) -->

# NY schema verification (Phase 0) — live Open NY pull, 2025

**Date:** 2026-06-05
**Branch:** `ny-disclosure-explore`
**Method:** live Socrata API probes against `data.ny.gov` (no auth). Scripts: `scripts/ny_discover_datasets.py`, `ny_sample_schema.py`, `ny_sample_retry.py`, `ny_probe_billshare.py`, `ny_probe_grain.py`. Raw evidence committed under `tests/fixtures/ny/` (sample rows) and `results/ny_*_2025.json` (aggregates).
**Purpose:** resolve the plan's gating Phase 0 — confirm/refute (a) transactional spend, (b) real bill numbers on linkage rows, (c) stance absent — before committing to the no-allocation architecture.

---

## TL;DR

The architecture **mostly holds**, with two refinements that the original plan did not anticipate:

1. **Bill linkage is a *typed subset*, not universal — but a large one.** A real bill number lives in `focus_identifying_number` only when the row's focus type is **`State Bill`**. That's **87.7%** of client-semiannual rows and **96.3%** of lobbyist-bimonthly rows for 2025. Bill format is the Open States key with an amendment suffix (`S550-A`, `A10003`). The rest are subject/funding free text (won't join to Open States). **Chain closes for the State-Bill subset, which is the overwhelming majority.**
2. **The API is denormalized ~1,300×.** Client-semiannual 2025 is **11.2M rows but only 8,613 distinct filings** (1,334 lobbyist firms, 4,376 clients, 8,303 distinct state bills). `current_period_compensation` is the **filing-level** total, *replicated on every row*. This kills two assumptions: you cannot sum compensation across raw rows (overcounts ~1,300×), and you cannot pull the full dataset by API pagination (71M+ rows for 2025 across the two core datasets). **Use the bulk CSV export + collapse to filing grain locally.**

All three gating questions resolve **in favor of the pipeline**:

| Gating question | Verdict | Evidence |
|---|---|---|
| (a) Spend transactional? | **YES** (per filing-period) — *with* a per-bill allocation caveat (comp is filing-level, not per-bill) | `current_period_compensation` = 24000/6000/17160 per filing; itemized `expense_*` rows in bimonthly |
| (b) Real bill # on linkage rows? | **YES, on the `State Bill` subset (88–96%)** | `focus_identifying_number` = `S550-A`, `A10003` when focus type = `State Bill` |
| (c) Stance absent? | **CONFIRMED none-collected** | no support/oppose field in any of the 6 datasets; closest is `monitoring_only` (Yes/No) + `type_of_lobbying_communication` (Direct/Grassroots) |

**No IPF is needed** — the lobbyist↔bill edge is directly disclosed. The NY-specific work is bulk-CSV ingestion, filing-grain de-duplication, bill-id normalization (strip the `-A`/`-B` amendment suffix to hit the Open States key), and a dollar-attribution decision.

---

## The 6 datasets ("Beginning 2019")

| Role | Dataset | Socrata id | Notes |
|---|---|---|---|
| Registration (retained/employed) | Lobbyist Statement of Registration | `se5j-cmbb` | contract comp (anticipated), subjects, focus id |
| **Lobbyist activity + itemized expenses** | Lobbyist Bi-Monthly Reports | `t9kf-dqbc` | per-period `compensation`, itemized `expense_*`, individual lobbyist names, bill focus |
| **Client spend (chain spine)** | Client Semi-Annual Report | `qym9-xzj6` | `current_period_compensation`, retained relationship, bill focus, `parties_lobbied` |
| Public-money disbursements | Disbursement of Public Monies Bi-Monthly | `i574-v3dp` | `current_period_compensation`/`reimbursement`, `parties_lobbied` |
| Public-corp registration | Public Corporation Statement of Registration | `2pde-cfs9` | in-house lobbyists, `lobbying_focus_identifying_number` |
| Public-corp activity | Public Corporation Bi-Monthly Report | `ffd8-nyat` | in-house comp + expenses, bill focus (`A10003`) |

**Reporting-year coverage (client semiannual):** 2019 (10.1M rows) → 2025 (11.2M) all present; 2026 just starting (1,059 rows). Clean bulk from 2019 confirmed.

---

## Schema landmines for the implementer

- **Inconsistent column names across datasets** for the same concept:
  - bill discriminator: `type_of_lobbying_focus` (client_semiannual, public_corp) **vs** `lobbying_focus_type` (lobbyist_bimonthly, lobbyist_registration).
  - bill id: `focus_identifying_number` (lobbyist datasets) **vs** `lobbying_focus_identifying_number` (public_corp).
  - client: `beneficial_client` (client_semiannual) **vs** `beneficial_client_name` (others); `principal_lobbyist` vs `principal_lobbyist_name`.
  - individual people: `individual_lobbyist_name` / `individual_lobbyist_s` / `individual_lobbyists` (semicolon-delimited list, needs splitting).
  The parser needs a per-dataset column map; do **not** assume one schema.
- **Money is dirty:** mixes `"$1000"` (registration) and `"13469"`/`"6000"` (reports); `total_contribution_amount` seen as the literal `"$"` (empty). Coerce defensively → Decimal; treat `"$"`/`""` as 0/None.
- **Bill ids carry amendment suffixes** (`S550-A`). Open States identifiers are typically the base (`S550`) — the normalizer must decide whether `-A`/`-B` map to the base bill or a distinct version. (NY treats `S550` and `S550-A` as the same bill, different print.) Likely strip suffix for the join, but **verify the OS join rate both ways** in Phase 4.
- **`Municipal Bill`** is a separate focus type (~260K + 164K rows) with municipal bill numbers — **out of scope** (state-level only). Filter on `level_of_government` starts-with `State` AND focus = `State Bill`.
- **Filing identity** = `form_submission_id`; `filing_type` ∈ {Original, Amendment} — must keep only the latest amendment per filing (the samples were almost all `Amendment`). De-dup logic needed.
- **`unique_id`** is a composite synthetic key (encodes submission/role/timestamps/focus); useful as the row-level provenance handle (the NY analog of WI's `item_id`).

---

## What this does to the plan

| Plan element | Change |
|---|---|
| IO layer | **Bulk CSV export** (`https://data.ny.gov/api/views/<id>/rows.csv?accessType=DOWNLOAD`) is the primary path, not API pagination — the API client stays for probing/schema only. Stream the CSV, filter + collapse with pandas. |
| Grain / dedup | New mandatory step: collapse the ~1,300× row explosion to **(reporting_year, reporting_period, form_submission_id, principal_lobbyist, beneficial_client, bill_id)**, keeping the latest `filing_type` per `form_submission_id`. |
| Dollar conservation | Compensation attaches at **filing grain**, replicated across rows. Conservation invariant: sum of distinct-filing comp == filing total; **never** sum raw linkage rows. |
| Per-bill dollar attribution | **We model it (even-split), we do not punt.** Ship `comp_per_bill = filing_compensation / n_bills_in_filing` as the headline per-bill number, AND keep `filing_compensation` + `n_bills_in_filing` on each chain row for re-aggregation. This mirrors WI shipping *both* `modeled_hours_per_sponsor` (the modeled column) and `modeled_hours` (the raw). **Precision vs. WI:** WI's per-*bill* split used disclosed effort percentages (`principal_filed_percent`); NY discloses **no per-bill weight**, so NY's per-bill split is uniform — analogous to WI's per-*sponsor* split, not its per-bill split. NY's spend chain is therefore *less* modeled than WI's; even-split is the honest neutral default and must be flagged as an assumption. (Corrected 2026-06-05 after Dan flagged that the original "let the consumer divide" framing was the opposite of modeling.) |
| Bill-id normalization | NY appends a print-version letter to amended bills: `S550-A` = Senate Bill 550, first amendment (`-B` second, etc.). The **base number is the bill's identity**; Open States keys NY bills by the base (`openstates.org/ny/bills/.../S6196`; NY Senate URLs are `/bills/2023/S108/amendment/A`). **Normalizer: strip the `-A/-B/...` suffix to join to OS; preserve the original suffixed string as a `bill_print_version` metadata column** (it records which print was lobbied — more specific than OS). Phase 4 measures the OS match rate both with and without stripping. Sources: [NY Assembly Rule III](https://nyassembly.gov/Rules/?sec=r3), [NYC Bar legislative glossary](https://www.nycbar.org/issues-policy/policy-department-resources/new-york-state-legislative-process-glossary-of-frequently-used-phrases/), [NY Senate S108A](https://www.nysenate.gov/legislation/bills/2023/S108/amendment/A). |
| No allocation/IPF | **Still confirmed.** lobbyist↔bill is disclosed; no graph/IPF module. |
| Chain coverage | Realistic closure ceiling ≈ 88–96% of activity rows (the `State Bill` share). Non-bill focus rows are emitted to `releases/ny/` but flagged `chain_eligible=false`. |
| "parties lobbied" | Present (`parties_lobbied`, `first_and_last_name_or_title_of_person_lobbied`) but **not used** per Dan's call — Open States is the lawmaker spine. Kept as a column for optional future validation. |

---

## Open question sharpened for Dan (was plan Q2)

**Which dataset is the canonical chain spend source — `client_semiannual` or `lobbyist_bimonthly`?** They overlap (both carry comp + bill focus for the retained universe). Recommendation: **`client_semiannual` (qym9-xzj6) as the chain spine** — it's client→lobbyist→bill+$ at semi-annual grain with the cleanest client identity, and it's ~5× smaller (11.2M vs 60M rows). Use `lobbyist_bimonthly` as the source of **itemized expenses + individual-lobbyist-person resolution** (it names the people; the client report names only the firm). The two public-corp datasets cover the in-house/public-corporation universe and can be a Phase-2 add-on. **Not blocking the build; flagging the overlap so we don't double-count dollars across the two.**
