# Phase 0: chain × parties_lobbied grain-join sanity check

_Run: 20260608._  Script: [`scripts/ny_chain_pl_grain_check.py`](../../../../scripts/ny_chain_pl_grain_check.py).  Plan: [`plans/ny_chain_completion_sketch.md`](../plans/ny_chain_completion_sketch.md), Phase 0.

## Inputs

- Chain: `releases/ny/chain/NY_chain_2025.tsv` — **83,786 rows**
- Parties: `releases/ny/NY_filing_parties_lobbied.tsv` — **168,430 rows** (96,980 resolved to `ocd-person`)

## Join geometry

- Distinct `(filing_id, lobbyist_id)` groups in chain: **4,328**
- Distinct `(filing_id, lobbyist_id, client_id)` groups in chain: **4,328**
- `(filing_id, lobbyist_id)` groups spanning >1 `client_id`: **0**

## Coverage

| Join key | Chain rows with ≥1 resolved disclosed person | % |
|---|---:|---:|
| A: `(filing_id, lobbyist_id)`            | 81,803 / 83,786 | **97.63%** |
| B: `(filing_id, lobbyist_id, client_id)` | 81,803 / 83,786 | **97.63%** |

## Fan-out (distinct resolved persons per chain row's join group)

Percentiles — how many disclosed legislators a typical chain row will see:

| pct | Key A | Key B |
|---:|---:|---:|
| p10 | 5 | 5 |
| p25 | 12 | 12 |
| p50 | 36 | 36 |
| p75 | 94 | 94 |
| p90 | 94 | 94 |
| p95 | 96 | 96 |
| p99 | 158 | 158 |
| p100 | 209 | 209 |

## Verdict

**GREEN** — key A coverage 97.63% ≥ 90%. Phase 1 proceeds under key A `(filing_id, lobbyist_id)`.
