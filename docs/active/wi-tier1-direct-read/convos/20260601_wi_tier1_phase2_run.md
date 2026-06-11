# WI Tier-1 direct-read — Phase 2 (paid run) + Phase 3 (write-up)

**Session:** 2026-06-01 (UTC) · machine: `Dans-MacBook-Air`
**Branch:** `wi-tier1-direct-read` (worktree at `.worktrees/wi-tier1-direct-read`, off `0f34781`)
**Plan:** `plans/20260530_wi_2025_tier1_direct_read.md`
**Handoff in:** `HANDOFF.md` (the Phase-2 runbook authored at end of the 2026-05-30 → 06-01 setup session)
**Prior convo:** `convos/20260530_wi_tier1_setup_and_phase1.md`
**Status at session start:** Phase 1 done + verified; Phase 2 deferred from MacBook-Pro due to ENOSPC. This session: run Phase 2 on Air (105 Gi free / 48% used), then write up Phase 3.

## Goal

Dispatch the 36 Tier-1 direct-read calls (2 models × 6 chunks × 3 runs) against WI 2025 statute bundle, compute per-model `sigma_noise`, compare to OH 2025 pilot, and flag WI-specific surprises (qualitative-trigger rows, out-of-bundle cross-refs).

## Pre-flight (this session)

- **Disk:** 105 Gi free / 48% used on Air — comfortable.
- **Bundle:** `data/statutes/WI/2025/sections` resolves via worktree `data/` symlink; 16 `.txt` confirmed.
- **API keys:** `.env.local` was *missing* at the main worktree (collateral of the laptop data-loss event). Recreated from `.env.corporate` at `/Users/dan/code/lobby_analysis/.env.local`; the symlink chain `wi-tier1-direct-read/.env.local → compendium-source-extracts/.env.local → main/.env.local` now resolves (intermediate symlink to the archived `compendium-source-extracts` worktree dir is weird-but-functional — flagged not fixed).
- **Tests:** `tests/test_tier_1_state_keying.py + tests/test_tier_1_legal_axis.py` → 34 passed (matches Phase 1 verification).
- **Dry-run probe** (`/tmp/wi_tier1_dryrun_probe.py`, imports the same modules the main script does): 16 statute files / registry 186 / 6 chunks / 84 legal cells / `('claude-opus-4-7', 'gpt-5.2-2025-12-11')` / 36 dispatches planned — matches HANDOFF reference exactly.
- **Launch wrapper:** `/tmp/run_phase2.sh` — `set -a; source .env.local; set +a; exec uv run python …` (avoids the env-var-persistence question across Bash calls; cleaner than inline `VAR=… VAR=… python`).

## Phase 2 — run

Launched in background; ran 20 min wall. **36/36 dispatched, 0 skipped, 0 dispatch failures.** Output buffered through `tee` (Python block-buffers stdout under a pipe; `uv run` doesn't pass `-u`) — appeared empty until completion. Visible progress came from watching the result JSONs land in `results/tier_1/WI_2025/`.

**Headline numbers:**

| Metric | Claude Opus 4.7 | GPT-5.2 (2025-12-11) |
|---|---|---|
| σ_noise (pct_stable across 3 runs — **per-model**) | **85.71%** | **84.52%** |
| n_stable | 72 | 71 |
| n_value_unstable | 9 | 5 |
| n_scoreability_unstable | 2 | 7 |
| n_incomplete | 1 | 1 |
| Per-vendor cost | $1.5263 | $1.0444 |

**Cross-validation against `releases/wi/` portal data (added later in session, see `results/20260601_wi_statute_vs_portal_spending.md`)** surfaced a second, un-reported metric: **inter-model alignment**. Of 84 legal cells, 65 are jointly within-model stable (both models internally agree on their 3 runs); of those 65, only 47 (72.3%) agree across models, leaving **18 cells (27.7%) where Claude and GPT deterministically disagree at high confidence on the same legal question**. The σ_noise metric as designed is correct per-model but doesn't report this. On WI the disagreement is concentrated in the `lobbyist_spending_report` chunk (~13 of the 18), where Claude reads "is this info required to flow through the lobbyist?" → TRUE and GPT reads "does the lobbyist file a spending report?" → FALSE. **Portal data (`WI_lobbyist_filings.tsv` has only hours columns, zero expenditure columns) is independent ground truth that confirms GPT's structural reading.** **Open candidate (Dan 2026-06-01, not yet decided):** at 27.7% disagreement, the Citations API is *worth considering* as a way to recover each model's cited statute text for adjudication — to evaluate after Dan does a closer read of the 18 disagreeing cells.

**Total session cost: $2.5708** (HANDOFF predicted ~$2–4; well under $10 session ceiling, all 36 calls also under $1 per-call ceiling — max single call was Claude / `lobbyist_spending_report` / run1 at $0.1988).

**Per-chunk per-call timing** (mean wall, both vendors):

| Chunk | Legal cells | Mean wall (s) |
|---|---|---|
| lobbying_definitions | 15 | ~29 |
| registration_thresholds | 6 | ~14 |
| registration_mechanics_and_exemptions | 8 | ~15 |
| lobbyist_spending_report | 30 | ~50 |
| principal_spending_report | 23 | ~37 |
| enforcement_and_audits | 2 | ~6 |

Per-vendor: Claude ~32 s/dispatch, GPT ~17 s/dispatch. **Issue [#31](https://github.com/danparshall/lobby_analysis/issues/31)** captures the parallelization opportunity surfaced by Dan watching this run.

**Integrity check** (HANDOFF §3, executed via `/tmp/wi_tier1_integrity_check.py`): 36 files / `corrupt: []` / even split (18 Claude + 18 GPT) / 6 per chunk / file-cost sum `$2.5708` matches log's `session_cost` (provenance internally consistent). No ENOSPC artifacts on Air — discipline carries from the MBP-deferral, not needed in practice this run.

## Phase 3 — results + interpretation

### Cross-state σ_noise comparison (the load-bearing research point)

| Model | OH 2025 (Tier-1 pilot) | WI 2025 (this run) | Δ |
|---|---|---|---|
| Claude Opus 4.7 | 85.7% | **85.71%** | ~0 |
| GPT-5.2 | 73.8% | **84.52%** | **+10.7 pts** |

Claude is essentially **state-invariant** at this resolution — the OH pilot writeup flagged that the 85.7% number is partly deflated by unpinned enum-label churn + 3 schema/adapter error classes, and the *same* underlying floor (whatever it is) reappears on WI. The true model-reasoning σ_noise floor is higher than 85.71% in both cases.

GPT got **notably more stable on WI than on OH** — a 10.7-point jump that is too large to be sampling noise (n=84 cells, std error of a 78% stability would be ~4.5 points). Possible explanations to investigate:

1. **Easier statute.** WI ch. 13 is shorter (16 sections / ~20 K prompt tokens) than the OH 2025 bundle, with more numerically-anchored thresholds in some chunks. Less surface for divergent disambiguation.
2. **GPT's class-B (dict-shape value roster hint) Fix B from Tier-2 may matter more on OH-shaped statutes** than WI-shaped — selective fix that helped OH disproportionately would compress the gap.
3. **The 10.7-point shift is mostly composition.** GPT's `n_scoreability_unstable=7` vs Claude's `2` shows GPT is *less stable in deciding what to abstain on* but matches Claude on actual value stability. That's a different failure mode and worth segmenting in v2.2 metrics.

### Load-bearing WI-specific finding — `registration_thresholds` errors

**Both models, every single run (6/6)** failed instantiation on exactly the same cell with exactly the same error class:

```
key=['lobbyist_registration_threshold_time_percent', 'legal']
reason='instantiation_failed'
arguments: value={'magnitude': 5, 'unit': 'days_per_reporting_period'}
            cited_section='§13.62(11)'
error: 2 validation errors for TimeThresholdCell
  magnitude: Input should be an instance of Decimal [input_value=5, input_type=int]
  unit:      Input should be 'hours_per_quarter', 'hours_per_year', 'days_pe…' [literal]
```

WI §13.62(11) defines a lobbyist via a **5-days-per-reporting-period** activity gate (if an individual's duties for a principal are not exclusively lobbying, they're still a lobbyist if their lobbying activity ≥ 5 days/reporting period). Both Claude and GPT correctly extract this trigger every time. The schema rejects it for **two distinct reasons**:

1. **`magnitude: int → Decimal` not coerced on the dict-shape path.** The OH Tier-2 "Fix A" (int→Decimal coercion, shipped on the now-archived `extraction-harness-brainstorm` branch and verified against real API output in Step D) is supposed to handle exactly this. Either Fix A's coercion doesn't apply to this code path (dict-shaped roster value vs. direct cell value?) or it regressed between branches. **Needs investigation** before next state run.
2. **`unit` literal-enum gap.** `TimeThresholdCell.unit` literal set covers `hours_per_quarter`, `hours_per_year`, `days_per_…<something truncated in error>`. Both models propose `days_per_reporting_period` or `days_per_6_month_reporting_period`. The cell shape literally cannot encode WI's time threshold structure — exactly the shape of finding the OH Tier-2 writeup verdict warned about: *"model right, schema can't represent the answer."*

### Other WI structural findings (visible in unscoreable emissions)

- **No $ compensation threshold for lobbyist registration in WI.** Both models correctly mark `lobbyist_registration_threshold_compensation_dollars` unscoreable with substantively identical justifications: §13.62(11) requires only receipt of "economic consideration, other than reimbursement for actual expenses" — no minimum dollar amount.
- **The $500 threshold in §13.64(1) / §13.621(5) applies to *principal* registration, not lobbyist registration.** Both models distinguish this correctly — GPT specifically flags `lobbyist_registration_threshold_expenditure_dollars` unscoreable on this distinction.
- **WI has a 10-hours-per-reporting-period employee exclusion** in §13.68(1) for non-lobbyist principal employees. Different schema slot — GPT correctly flags this as not being a lobbyist-side de minimis.

These are the kinds of distinctions that the gather-first (v2.2) intermediate-JSON format is *designed* to preserve. Under v2.1 typed cells, every one of these correct-but-unrepresentable findings collapses to `unscoreable` and the structural signal is lost.

### What this run is evidence of

1. **Single extraction pipeline reads multiple states reliably.** Both models, on a fully different state's statute, hold the same σ_noise structure as on OH — consistent with the Compendium 2.0 success criterion #3 (multi-year reliability, extended here to multi-state reliability).
2. **The v2.1 cell schema has at least one concrete, model-agreed gap** (`TimeThresholdCell.unit` doesn't admit days-per-reporting-period). This is exactly the input the gather-first pivot was paused to collect.
3. **A potential Fix A regression in the dict-shape value path** — claimed-fixed on the archived `extraction-harness-brainstorm` branch but reproducing here. Worth a focused root-cause trace before next state.

### Cost provenance

Cost is stamped per-call (`cost_usd_estimate` key in each result JSON) AND aggregated to `session_cost` at end of run. The two match exactly ($2.5708). Cost is computed via `tier0._estimate_cost_usd(model, usage)` from API-returned token usage — so it tracks billed reality, not a static price table.

## Next

All items below have been folded into [`plans/20260601_post_phase3_followups.md`](../plans/20260601_post_phase3_followups.md) (originally written as `HANDOFF_followups.md` then promoted to `plans/` per doc-protocol). Summary:

- **(Item 1)** Investigate Fix A regression (the `magnitude: int → Decimal` failure on the dict-shape value path; 6/6 runs fail on `lobbyist_registration_threshold_time_percent`).
- **(Item 2)** Capture `TimeThresholdCell.unit` enum gap as v2.2 design input (`days_per_reporting_period` and related missing).
- **(Item 3, candidate per Dan 2026-06-01 — to evaluate, not yet decided)** Closer look at the 18 inter-model disagreement cells from the WI cross-validation. If the disagreement is substantive (not annotation artifacts), the Anthropic Citations API is a candidate mechanism for adjudication — it would recover the actual statute text each model latched onto. Decision deferred until Dan reviews.
- **(Item 4)** Bake portal cross-validation into the MI session: run Tier-1 *and* load `releases/mi/` in parallel, same comparison structure as `results/20260601_wi_statute_vs_portal_spending.md`.
- **(Item 5)** Investigate principal-filings aggregation: is `WI_principal_filings.tsv`'s `total_expenditure` aggregate-by-portal-design or aggregate-by-scrape-loss? Answer determines whether the 4 WI principal-side transparency gaps are real or recoverable from re-parsing.
- **(Item 6, separate track)** σ_noise WI-vs-OH composition study (GPT's `scoreability_unstable` 2 → 7 jump). Decomposable from the existing per-model artifacts; no API spend.
- **Next-state target:** MI (was NC; swapped per Dan 2026-06-01).

## Captured Tasks

- [#31: Parallelize Tier-1 dispatch loop (cross-vendor + within-vendor)](https://github.com/danparshall/lobby_analysis/issues/31) — captured 2026-06-01
