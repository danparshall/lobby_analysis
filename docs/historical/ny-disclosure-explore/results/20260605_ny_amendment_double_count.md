<!-- Generated during: convos/20260605_ny_phase2_grain_collapse.md -->

# NY amendment double-count — finding + verified dedup rule (client_semiannual, 2025)

**Date:** 2026-06-05
**Branch:** `ny-disclosure-explore`
**Method:** read-only live Socrata probes against `data.ny.gov` (qym9-xzj6). Scripts: `scripts/ny_probe_amendments.py`, `scripts/ny_probe_amendment_ordering.py`. Raw evidence: `results/ny_amendment_probe_2025.json`, `results/ny_amendment_ordering_probe_2025.json`.
**Why:** the plan / Phase-0 findings said the grain-collapse dedup is *"keep latest `filing_type` per `form_submission_id`"*. Before building the load-bearing dollar-conservation guard, verify that rule.

---

## TL;DR

The plan's dedup rule is **wrong** (a no-op), and the plan's conservation test would **not** have caught the resulting double-count. An amendment is a **new submission with its own `form_submission_id`** that supersedes the prior submission for the same business key. Summing compensation over distinct `form_submission_id` therefore counts every superseded version.

## Evidence

**A — amendments are common.** 2025 `client_semiannual`: 8.63M `Original` rows, 2.57M `Amendment` rows.

**B — no `form_submission_id` carries both filing types.** The `min(filing_type) <> max(filing_type)` group query returned **zero** rows. So *"keep latest `filing_type` per `form_submission_id`"* never drops anything — it is a no-op.

**C — the smoking gun.** `THE PARKSIDE GROUP LLC` / `GRAHAM WINDHAM`, 2025 July/Dec exists as two submissions: `775553` (Original, $0) and `793896` (Amendment, $24,000). The amendment is a separate `form_submission_id` superseding the original.

**E — magnitude + ordering.** Worst-case keys carry 1 Original + **3** Amendments. `RIDDETT ASSOCIATES INC` / `TRIAL LAWYERS ASSOCIATION (NYS)`, Jan/June: submissions `729762`/`745650`/`752918`/`782077` with comp $265,002 / $265,002 / $265,002 / **$255,536** (final). Naive distinct-`form_submission_id` sum = **$1,050,542** for a **$255,536** filing → **4.1× overcount** on one key. `n_rows` also grows across amendments (2934 → 6858 → 13716), so row-weighting doesn't help.

**Monotonicity confirmed.** For all five worst-case keys, every Amendment id is strictly greater than the Original id (`monotonic_amend_gt_orig: true`). So `max(form_submission_id)` per business key = the latest version, with no filed-date column needed.

**Business key validated.** With key `(reporting_year, reporting_period, principal_lobbyist, beneficial_client, contractual_client_name)`, every examined multi-submission key had exactly **one** Original — no evidence the key is too coarse.

## Verified dedup rule (implemented in `io/ny/grain.py`)

Per business key `(reporting_year, reporting_period, principal_lobbyist, beneficial_client, contractual_client_name)`, keep only rows where `form_submission_id == max(form_submission_id)` for that key; drop all other submissions **before** collapsing to bill grain. The conservation test asserts a superseded Original is **not** double-counted (Original $20k → Amendment $24k must collapse to $24k, not $44k).

## Caveats / open items

- Relation to **GH #37**: that ticket tracks the *cross-dataset* double-count (client_semiannual + lobbyist_bimonthly). This is a *within-dataset* axis; both are now documented on #37.
- The `bill_id` State-Bill scoping question is separate (see convo "Open Questions"): the Phase-0 `starts_with(level_of_government, 'State')` filter would wrongly drop a `State Bill` row filed at `Both (State and Municipal)` level (e.g. `S550-A`). Deferred to the parser step.
