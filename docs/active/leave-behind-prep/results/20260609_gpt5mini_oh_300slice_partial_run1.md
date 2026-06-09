# gpt-5-mini OH 300-slice — Day 2 partial Run 1

**Status:** Run 1 stopped at **55/305 filings** by user request after surfacing
a cost-over-projection finding. **Not a failure.** Next agent should
parallelize the dispatch and either resume Run 1 or restart from clean,
depending on whether the verbosity finding warrants further investigation
first.

## Headline finding (the reason we stopped)

**Mini's per-filing cost is 2-3× the plan's projection** because mini emits
~3× more completion tokens per filing than the plan implicitly assumed.

| | plan estimate | observed (n=55) |
|---|---|---|
| per-filing prompt tokens | (not specified; ~4-5K brief) | 4,585 avg |
| per-filing completion tokens | ~850-1,300 (implied by $100-150 full-corpus) | **2,933 avg** |
| per-filing cost (mini) | $0.0022-$0.0033 | **$0.0070** |
| per-pass 305-slice cost | $1 | **$2.14 (extrapolated)** |
| 3-pass validation cost | $3 | **$6.42 (over $5 cap)** |
| 1× mini, full corpus (45,605) | $100-150 | **$317** |
| 1× Sonnet, full corpus (plan ref) | $800 | — (not re-run; uses prompt caching) |

The Sonnet/mini *ratio* is still favorable (~2.5× cheaper), just not the
5-8× the plan hoped for. Sonnet's $800 full-corpus baseline implies
~1,000 output tokens/filing assuming Anthropic prompt caching on the brief.
Mini's 2,900 is ~3× chattier.

**Possible causes of mini verbosity (not yet investigated):**
- Empty nested entity objects fully serialized (contact_details=[],
  identifiers=[], etc. — every nullable nested field gets the full skeleton)
- `extraction_warnings` populated with 2+ thoughtful sentences each
- New schema fields (`employer`, `total_hours_*`) emit even when source has
  no data
- Mini may be more aggressive about emitting all schema fields explicitly
  vs Sonnet's more selective null-omission behavior

A look at any one of the 55 mini outputs vs the corresponding Sonnet baseline
should make the difference visible.

## Speed (Run 1 wall-clock)

The dispatcher is serial — one filing at a time, blocking on each OpenAI
HTTP call. ~32s per filing × 305 = ~2.7 hr per pass. Per the user's
direction, **the next agent should parallelize** the dispatch (10-way
ThreadPoolExecutor should drop wall-clock to ~15-20 min per pass; HTTP-bound
so concurrency wins linearly; existing per-filing error isolation and
idempotent resume make parallelism safe).

## What's on disk

- `data/oh_portal/extracted_openai/<report_id>/mini_run_1_<ts>_<uuid>/` —
  55 report_ids, each with `filing.json` + `extraction_run.json` (the
  latter has full per-filing usage + duration).
- `data/oh_portal/extracted_openai/_log_run1.txt` — per-filing log.
- `data/oh_portal/extracted_openai/_summary_run1.json` — reconstructed
  from the per-filing metadata via
  `scripts/gpt5mini_oh_300slice_reconstruct_summary.py` (the native summary
  isn't written when dispatch is killed mid-pass).

The 55 report_ids covered (alphabetical numeric sort, first 55 of 305):
`1394434, 1394636, ..., 1419738, 1427844` (full list visible via
`ls data/oh_portal/extracted_openai/`).

## Day-2 spend so far

| line item | spend |
|---|---|
| 5 re-Sonnet runs (legacy-baseline cleanup) | ~$0.31 Anthropic |
| 3 mini smoke runs on 1427844 | ~$0.025 OpenAI |
| Mini Run 1, 55 of 305 filings | $0.39 OpenAI |
| **total** | **~$0.72** |

## Pre-flight & infra changes still in place (committed, pushed)

1. `gpt5mini_oh_300slice_preflight.py` (0.1 + 0.2 operator script)
2. `gpt5mini_oh_300slice_smoke_diff.py` (0.4 operator script; symmetric
   key-set WARN, only wild array divergence is a hard fail)
3. `gpt5mini_oh_300slice_cost_check.py` (Phase 2 watchdog) — note: this
   only fires AFTER a pass completes; if the next agent wants pre-spend
   guardrails, project from per-filing average not post-pass totals.
4. `gpt5mini_oh_300slice_reconstruct_summary.py` (this session) — rebuild
   `_summary_run<N>.json` from on-disk per-filing metadata after a kill.
5. `MODEL_ID_DATED = "gpt-5-mini-2025-08-07"` pinned.
6. `_latest_filing_json` switched to mtime-based selection in all 4 places;
   run_ids now date-prefixed for human readability.
7. The 5 legacy-schema Sonnet baselines re-extracted (305/305 now modern).

## Resume path

`uv run python scripts/gpt5mini_oh_300slice_dispatch.py --pass 1` with the
existing `--resume` default will skip the 55 done and pick up at filing #56.
A parallelized variant should: (a) keep the `--resume` semantics; (b) ensure
the per-filing skip-check is concurrency-safe (it reads disk; should be
fine); (c) consider TPM/RPM budgeting — at 10 concurrent the requests-per-
minute is well under typical mini limits but worth checking the account's
tier before pushing higher.

## Open question for the user

The plan baked in $100-150 mini / $800 Sonnet as the "leave-behind" cost
comparison for the decisions doc. Actual mini at $317 changes that message
materially:

- **$800 Sonnet → $317 mini** is still a cost reduction worth surfacing,
  but the case for "opportunistic mini-based extraction" is weaker.
- **The 3-pass validation cost** ($6-7) is small in absolute terms; running
  it is still warranted if mini quality holds up, since the deliverable to
  Suhan is the *measured* cost not the *projected* one.

These are decisions for the user, not for the next agent.
