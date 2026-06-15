<!-- Generated during: convos/20260605_oh_discover_all_and_slice_validation.md -->

# OH extraction — 300-filing slice validation

**Date:** 2026-06-05 · **Branch:** oh-portal-aprime-batch · **Model:** claude-sonnet-4-6

## What was run

1. `discover --all --years 2025,2026` → `data/oh_portal/discover/recent.tsv` (45,605 AERs).
2. Systematic-sample 300 filings from `recent.tsv` (every 152nd row → spread across all
   agents/periods): `_slice_validation_300.tsv` — 300 filings, 231 agents, 279 employers,
   periods {Jan-Apr26: 82, Sep-Dec25: 72, Jan-Apr25: 66, May-Aug25: 80}.
3. `batch --file _slice_validation_300.tsv` (serial).

## Discover universe

| Metric | Value |
|---|---|
| AER filings (2025–2026) | **45,605** |
| — 2025 | 34,080 |
| — 2026 | 11,525 (May–Aug26 just opening: 39) |
| Distinct agents | 2,684 |
| Distinct employers | 2,741 |
| Employer-populated | 100% |
| Duplicate report_ids | 0 |

## Extraction validation (300 filings)

| Metric | Value |
|---|---|
| Extracted (first pass) | 299 / 300 |
| Failed (first pass) | 1 (report 1396214) |
| Failure cause | transient `OverloadedError` (HTTP 529), API-side |
| Recovered on retry | ✅ yes (1 retry → clean `filing.json`) |
| **Effective extractable rate** | **300 / 300** |
| Genuine parse/schema failures | 0 |
| Wall-clock | 77.8 min (15.6 s/filing, serial) |
| Output size avg | ~4.5 KB (~1,122 tokens) |
| Cost/filing (sonnet-4-6, no cache) | ~$0.035 |
| Slice cost | ~$10 |

## Full-universe projection (45,605 filings)

| Route | Cost | Wall-clock | Robustness |
|---|---|---|---|
| Serial (current `batch.py`) | ~$1,600 | **~8 days** | ❌ manual re-runs only |
| Concurrency (~20 workers) | ~$1,600 | ~10 hr | ⚠️ hammers OLAC; needs retry code |
| **Batches API + caching** | **~$800** (50% off; caching cuts more) | async ≤24 hr | ✅ server-side retries, idempotent |

## Findings → recommendations

- **Pipeline is sound at scale.** No genuine extraction failures across 300 diverse
  filings; the lone failure was transient infra.
- **Add transient-error retry.** Single API call, no retry → 529/429 permanently drops a
  filing. At 45K this silently loses filings unless re-run.
- **Do not run the full universe serially.** ~8 days. Route through the Message Batches API
  (cheaper + async + server-side retry + idempotent).
- **Add prompt caching.** The brief + tool schema (~5K identical tokens) are re-sent
  full-price on every call; caching them ~halves input cost.
- **Pre-existing cache-path bug:** `discover._discover_dir()` writes to a doubled
  `data/oh_portal/oh_portal/discover/` path (DATA_DIR already ends in `oh_portal`). Cosmetic
  for the run; fix + migrate cache before relying on the documented path.
