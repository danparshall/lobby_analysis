# NY `client_semiannual` 10k-row sample

A small, committed real-data slice of the `data.ny.gov` Socrata `client_semiannual`
dataset (Beginning 2019), projected to the 10 columns the Phase-2 pipeline reads.
Useful as a real-shape fixture for tests that benefit from genuine field
contents (e.g. quote-aware CSV counting, schema validation, edge-case discovery)
rather than mocked bytes.

## Provenance

| | |
|---|---|
| Source | `https://data.ny.gov` — `client_semiannual` dataset (Socrata id [`qym9-xzj6`](https://data.ny.gov/d/qym9-xzj6), "Client Semi-Annual Report Beginning 2019") |
| Pulled | 2026-06-08 (claude.ai sandbox, `ny-disclosure-explore` branch) |
| Query | `https://data.ny.gov/resource/qym9-xzj6.csv?$select=<10 cols>&$where=reporting_year='2025'&$limit=10000` |
| Columns | `form_submission_id, reporting_year, reporting_period, principal_lobbyist, beneficial_client, contractual_client_name, current_period_compensation, type_of_lobbying_focus, focus_identifying_number, parties_lobbied` |
| Order | **No `$order` clause** — Socrata's default order. (`$order` on this 11.2M-row view times out; this is the same constraint that drives the paginate-by-id-range approach in `scripts/ny_pull_2025.py`.) |
| Rows | 10,000 |
| Bytes | 2,687,863 (~2.7 MB) |
| SHA-256 | `a6a4c6c12b25825aba92203462cfc55987e088ed858850e16e7374ec38a48fe6` |

## Shape

| Property | Value |
|---|---:|
| Distinct `form_submission_id` | 133 |
| Reporting periods | `Jan/June`, `July/Dec` |
| Rows with non-empty `parties_lobbied` | 9,949 (99.49%) |
| Rows with literal `,` in `parties_lobbied` | 454 |

**Sampling bias warning.** Socrata's default order is not random. The 10k slice
spans only 133 of the year's 8,613 distinct `form_submission_id`s — i.e. it is
heavily weighted toward the **largest filings** (the small ones have a handful
of rows each; the largest single filing in 2025 has 2,219,319 rows). The shape
is fine for schema/edge-case fixture purposes, but **do not** infer per-filing
fan-out statistics from this slice — use the full pull aggregate for that.

The 2025 per-filing row-count distribution (from the live group-by aggregate
run during this pull, 8,613 filings) was:

| Quantile | Rows per filing |
|---|---:|
| min | 1 |
| 10% | 1 |
| 50% (median) | 6 |
| 80% | 55 |
| 90% | 216 |
| max | 2,219,319 |
| mean | 1,300 |

## Use cases

- **Schema-fixture for the acquisition-hardening tests**
  ([`plans/ny_acquire_paginate_verify.md`](../plans/ny_acquire_paginate_verify.md)) — a real
  payload to confirm `_count_csv_records` handles real Socrata CSV quoting and
  field shapes (not just hand-crafted edge cases).
- **Schema validation** of the projected-column subset when iterating on
  `io/ny/columns.py` or `parse.py`.
- **Sandbox-side prototyping** of NY work without requiring the full 3.3 GB
  2025 pull. The full pull remains the gold source (`scripts/ny_pull_2025.py`,
  verified `count(*)`).

## Not in scope

- This is **not** a grain-representative sample (see bias warning).
- This is **not** the input to the chain (`releases/ny/NY_clients.tsv` and the
  others are gitignored derived artifacts produced by `materialize_cli`, not
  by raw projection from the source).
- The matching `parties_lobbied` resolution to `ocd-person` IDs is **not**
  pre-computed here — that lives in the gitignored
  `releases/ny/NY_filing_parties_lobbied.tsv`.

## Regeneration

```bash
curl -sS \
  -H "User-Agent: claude-researcher-sample-pull" \
  "https://data.ny.gov/resource/qym9-xzj6.csv?\$select=form_submission_id,reporting_year,reporting_period,principal_lobbyist,beneficial_client,contractual_client_name,current_period_compensation,type_of_lobbying_focus,focus_identifying_number,parties_lobbied&\$where=reporting_year='2025'&\$limit=10000" \
  -o docs/active/ny-disclosure-explore/results/20260608_client_semiannual_sample_10k.csv
```

The exact bytes may drift if the live dataset is updated; the sha256 above
pins this particular snapshot.
