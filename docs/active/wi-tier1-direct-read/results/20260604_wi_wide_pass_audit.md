<!-- Generated during: convos/20260604_wide_pass_commit3_redispatch_and_audit.md -->
<!-- Plan: plans/20260604_wide_prompt_text_pass.md (Commit 3) -->

# WI Tier-1 Wide-Pass Re-dispatch + Audit

**Date:** 2026-06-04 (afternoon, immediately after Commit 2 YAML population)
**Branch:** `wi-tier1-direct-read`
**Spend:** $2.5442 (predicted ~$2.50 ✓); cumulative WI Tier-1 ledger $4.7504 + $2.5442 = **$7.2946**
**Dispatch:** 36/36 successful, 0 skipped, 0 dispatch failures, ~20 min wall
**Integrity:** 36 files / `corrupt: []` / per-file `cost_usd_estimate` sum matches log `session_cost` exactly ($2.5442)

## Headline metric — inter-model agreement on jointly-stable cells

| | Narrow-pass (baseline) | Wide-pass | Δ |
|---|---|---|---|
| Total cells | 84 | 84 | 0 |
| Jointly within-model stable | 66 | 65 | −1 |
| Inter-model AGREE | 65 | 59 | **−6** |
| Inter-model DISAGREE | 1 | 6 | **+5** |
| Agreement % on jointly-stable | **98.5%** | **90.8%** | **−7.7 pts** |

Per-model σ_noise (`pct_stable`):

| Model | Narrow-pass | Wide-pass | Δ | Decomposition (wide) |
|---|---|---|---|---|
| Claude Opus 4.7 | 86.90% | **82.14%** | **−4.76 pts** | n_stable=69, n_value_unstable=10, n_scoreability_unstable=1, n_incomplete=4 |
| GPT-5.2 | 82.14% | 82.14% | 0 | n_stable=69, n_value_unstable=8, n_scoreability_unstable=5, n_incomplete=2 |

**Headline read:** Inter-model agreement dropped from 98.5% to 90.8%. Claude per-model stability dropped 4.76 pts; GPT held steady. **This is a real shift, but the decomposition below shows the architecture is sound — the regression is content-level YAML quality, not the renderer change.**

## Decomposition of the 6 wide-pass disagreements

Compared cell-by-cell against the narrow-pass baseline (archived to `results/tier_1/WI_2025/_pre_wide_pass/`):

| # | Row | Narrow-pass | Wide-pass | Verdict |
|---|---|---|---|---|
| 1 | `lobbyist_registration_threshold_expenditure_dollars` (registration_thresholds) | both models UNSTABLE (not in 66 jointly stable) | Claude=`"0"` / GPT=unscoreable | **Wide-pass stabilized both models** into opposing readings: Claude treats "no statutory expenditure threshold for lobbyist registration" as zero; GPT treats it as unscoreable. **Not a regression** — was unstable before, now stable but inter-model disagree. Philosophical disagreement about "absence-of-threshold = 0 vs unscoreable." |
| 2 | `lobbyist_registration_amendment_deadline_days` (registration_mechanics) | Claude UNSTABLE, GPT stable-unscoreable | Claude=`10` / GPT=unscoreable | Same pattern. Wide-pass stabilized Claude on §13.695(2)'s 10-day rule for principal-side changes; GPT consistently says that rule is principal-side, not lobbyist-side. Not a regression. |
| 3 | `lobbyist_registration_deadline_days_after_first_lobbying` (registration_mechanics) | Claude UNSTABLE, GPT stable-unscoreable | Claude=`0` / GPT=unscoreable | Same pattern. Claude interprets "must register before lobbying" as "deadline = 0 days after lobbying"; GPT says no numeric deadline is specified. Not a regression. |
| 4 | `lobbyist_registration_renewal_cadence` (registration_mechanics) | **both models stable + agreed at value=`24`** (months) | Claude=incomplete (instantiation failed) / GPT=`2` (years) | **REAL regression.** Was a clean 65/65 agreement; now Claude can't instantiate AND GPT's unit changed (24 months → 2 years; same biennial reality, different encoding). Cause: see Section "Instantiation failures." |
| 5 | `lobbyist_spending_report_filing_cadence` (lobbyist_spending_report) | Claude stable-`"none"`, GPT UNSTABLE | Claude=`"50"` / GPT=incomplete | Partial. Narrow-pass cell wasn't in 66 jointly stable (GPT was unstable). Wide-pass: Claude moved from `"none"` to `"50"` (more correct — WI files semi-annually, matching the CPI 50-tier rubric); GPT consistently incomplete. |
| 6 | `lobbying_violation_penalties_imposed_in_practice` (enforcement_and_audits — known Pattern C mis-axed row) | Claude=`True` (scored), GPT=unscoreable (THE narrow-pass single disagreement) | Claude=incomplete / GPT=unscoreable | Partial regression. Pattern C disagreement persists, but Claude's instantiation degraded from scored → incomplete. Cause: see Section "Instantiation failures." |

**Net read of the 6:**
- 3 of 6 (rows 1-3) are **newly-stable-into-disagree** — the wide-pass substantive prompts gave each model enough material to anchor consistently; they landed on opposing readings of a real philosophical question. **Ralph-tractable** with clarifiers like the narrow-pass Pattern A pattern.
- 1 of 6 (row 4 `renewal_cadence`) is a **real regression** — was agreed, now Claude can't instantiate. Caused by a prompt-cell-type mismatch (see below).
- 1 of 6 (row 5 `filing_cadence`) was already unstable; Claude improved (`"none"` → `"50"`), GPT degraded; net mixed.
- 1 of 6 (row 6 Pattern C) is the known mis-axed row whose Claude side regressed from scored to incomplete.

## Instantiation failures — the load-bearing finding

Surveyed `errors` field across all 36 wide-pass JSONs and the 36 narrow-pass JSONs (`_pre_wide_pass/`).

| Pass | Total instantiation failures | Failure classes |
|---|---|---|
| Narrow-pass (baseline) | 7 | 6 × TimeThresholdCell.unit literal-enum gap (KNOWN — v2.2 ledger Entry 1) + 1 × GPT None→EnumCell |
| Wide-pass | 17 | 6 × same TimeThresholdCell.unit + **11 NEW failures on 4 specific rows** |

The 11 NEW wide-pass instantiation failures are all the same root cause: **the wide-pass YAML population copied source-rubric scoring vocabulary verbatim into `prompt:` fields without reconciling the rubric's scoring language with the v2 cell type for that row.**

| Row | v2 cell type | Failures | Model emitted | Source of bad vocab |
|---|---|---|---|---|
| `lobbying_violation_penalties_imposed_in_practice` | `BinaryCell` (true/false) | 3 (Claude all 3 runs) | `'100'`, `'50'` | YAML prompt has CPI/PRI **100/50/0 score** language; cell expects bool |
| `lobbyist_registration_renewal_cadence` | `IntCell` | 3 (Claude all 3 runs) | `'"YES"'`, `'"MODERATE"'` | YAML prompt has CPI **YES/MODERATE/NO** language; cell expects int |
| `lobbyist_filing_itemization_de_minimis_threshold_dollars` | `DecimalCell` (non-negative) | 2 (Claude) | `-1` (sentinel) | Model using -1 as "not applicable" sentinel; cell forbids negative |
| `lobbyist_spending_report_filing_cadence` | `EnumCell` (string) | 3 (GPT all 3 runs) | `0` (int) | GPT submitting int 0 to a string-typed enum |

The 6 TimeThresholdCell.unit failures persist in both narrow and wide; this is the **known v2.2 ledger Entry 1 schema gap** (WI §13.62(11)'s 5-days-per-reporting-period gate has no representation in the current `TimeThresholdCell.unit` literal enum). Out of scope for prompt fixes.

## Architecture verdict — opaque-handle renderer is sound

Forensic check on Claude's incomplete cells (`/tmp/diagnose_claude_incomplete.py`, ad hoc): every Claude run for every failing chunk emitted clean `record_cell` tool_use blocks with valid `handle: 'row_NNN'` fields. The parser correctly routed handle → row_id via the per-chunk map. **No renderer bug, no handle-mapping bug, no parser bug.**

The wide-pass renderer (opaque handles, no row_id in model input, citations stripped) is **architecturally sound**. The wide-pass results' regressions decompose into:

1. **3 cells that were within-model unstable in narrow-pass became stable but inter-model disagreed in wide-pass** (rows 1-3). The wide-pass substantive prompts did exactly what they were designed to do — anchor each model into a consistent reading. They just exposed legitimate philosophical disagreements about absence-vs-zero that the narrow-pass row_id-only renderer didn't surface. These are Ralph-tractable.

2. **4 cells where the YAML prompt's verbatim rubric vocabulary conflicts with the v2 cell type** (rows 2, 4 in disagreement table; the `de_minimis_threshold_dollars` row and the GPT-side `filing_cadence` rounding both add to the instantiation-failure tally). These are tractable **mechanically** via a pre-flight YAML audit — they don't need Ralph iteration.

3. **6 TimeThresholdCell.unit failures** — independent schema gap (v2.2 ledger Entry 1), preserved across both passes, not addressable at prompt level.

## What the wide-pass actually validated

- **The YAML SSOT design works.** Per-row `source_quotes:` (immutable provenance) + `prompt:` (mutable model-facing string) is clean; loader works; smoke probes confirm full 181-row coverage.
- **The opaque-handle renderer works.** Zero row_id leakage into model input; clean handle→row_id round-trip via the per-chunk map; parser rejects malformed responses.
- **The wide-pass YAML population was too mechanical.** Lifting verbatim source quotes works when the rubric vocabulary aligns with the v2 cell type; it fails when CPI's YES/MODERATE/NO meets an IntCell, or CPI's 100-score tiers meet a BinaryCell. This was foreseeable in retrospect; the Commit 2 plan didn't address it.

## What's next — Phase A (Commit 4) + Phase B/C (Ralph design)

**Phase A — pre-flight prompt audit (no/minimal API spend).** Commit 4 on this branch.
- Walk all 181 rows × YAML prompt × v2 cell type. Flag rows where the prompt's natural vocabulary doesn't match the cell type (CPI YES/MODERATE/NO for IntCell, 100/50/0 scoring tiers for BinaryCell, -1 sentinels for non-negative Decimal, etc.).
- Patch each flagged row's YAML prompt to reconcile vocabulary with cell type. E.g., for `renewal_cadence` (IntCell): rewrite the prompt to ask for "number of years between mandatory renewals (e.g., 1 = annual, 2 = biennial)" instead of echoing CPI's YES/MODERATE/NO scoring language.
- Smoke probe verifies all 181 prompts render cleanly.
- Optional cheap WI re-dispatch (~$2.50) to verify the patches collapse the new instantiation failures.

**Phase B — Ralph design (NOT on this branch).** Brainstorm:
- Per-row iteration loop, with prior-art rubric authors' published per-state scores as the external oracle.
- Multi-rubric oracle (any rubric that reads the row, not just `first_introduced_by`).
- Convergence criterion is shape-dependent on what per-item ground truth actually exists per rubric — most rubrics published aggregate per-state scores, not per-item answers. **Pending 9-rubric oracle granularity audit** (`results/20260604_oracle_granularity_audit.md`) before picking the first Phase B row.
- Tractable starting candidates: PRI 2010 (per-item × 50 states from `pri-2026-rescore` transcription) + likely FOCAL 2024 (L-N 2025 Suppl File 1 granularity TBD) + Sunlight 2015 (5-tier categorical per-state).
- First Phase B row done **by hand** to see what iteration moves actually look like before deciding what to automate.

**v2.2 ledger updates** (separate session):
- Entry 1 (TimeThresholdCell.unit): no change — 6 failures persist as expected.
- New entry: cells where rubric vocabulary structurally mismatches v2 cell type. E.g., `lobbyist_registration_renewal_cadence` — CPI 2015's natural answer is categorical (YES/MODERATE/NO); v2 forced it to IntCell. Either the cell type should evolve, or the row should accept categorical input. Flag as v2.2 input.

## Provenance

- Dispatch script: `scripts/tier_1_direct_read_legal_axis.py` (unchanged since Commit 1)
- Renderer: opaque-handle path, per Commit 1 (commit `003a9f9`)
- YAML SSOT: `compendium/source_quotes.yaml` populated for 181 rows, per Commit 2 (commit `13ae80a`)
- Raw results: `docs/active/wi-tier1-direct-read/results/tier_1/WI_2025/*.json` (36 files)
- Archived narrow-pass baseline: `docs/active/wi-tier1-direct-read/results/tier_1/WI_2025/_pre_wide_pass/*.json` (36 files)
- Forensic scripts (ad hoc, not committed): `/tmp/wide_pass_integrity.py`, `/tmp/audit_pre_wide_pass.py`, `/tmp/compare_disagreements_narrow_vs_wide.py`, `/tmp/diagnose_claude_incomplete.py`, `/tmp/instantiation_failure_survey.py`. If any need to persist, move into `results/disagreement_audit/` or a new `results/wide_pass_diagnosis/` subdir.
