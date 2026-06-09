# gpt-5-mini reasoning effort — three-arm dispatch

**Date:** 2026-06-09
**Branch:** leave-behind-prep
**Surface:** claude.ai

**Predecessor:** [`20260609_gpt5mini_day2_phase0_hardening_partial_run1.md`](20260609_gpt5mini_day2_phase0_hardening_partial_run1.md) — that session surfaced mini's $317-extrapolated cost (vs plan's $100-150) and stopped at 55/305 for the user to call the next move. This session followed up.

## Summary

Picked up the partial Run 1 handoff. The previous session diagnosed mini's per-filing cost as 2-3× the plan's projection, driven by ~3× completion tokens vs Sonnet. Spent the first part of this session inspecting on-disk artifacts from the handoff dir and identifying the most likely root cause: **gpt-5-mini's `reasoning_effort` defaults to `medium`, which budgets significant reasoning tokens that are billed as completion tokens but invisible in the structured output.** The current `extract_openai.py` was passing no `reasoning_effort` argument — i.e., paying the medium-reasoning cost by default.

Implemented the threading (`extract_openai.py` → `pipeline_openai.py` → `dispatch.py`) under TDD plus added a `--max-concurrent` flag with `ThreadPoolExecutor` so the 3-arm experiment could run in ~15 min wall-clock instead of ~3 hours. Pushed 4 commits to the branch. User ran all three arms (medium top-up to 100 + low 100 + minimal 100). Then built a cross-arm field agreement analyzer to compare sonnet vs mini-medium vs mini-low on the 100-filing intersection — strict equality, both-null counted separately per user's design call.

Headline findings: minimal is not viable for production (97-98% null on reporting_period); low is materially cheaper than medium (~40% lower) but with measurably worse field-emission rates; medium is the most defensible shipping setting. On fields where both Sonnet and mini-medium emit, agreement is excellent (95-100% across identity, name, list-length, and dollar-amount fields). The genuine quality gap is in reporting_period date *values* (13-16 disagreements out of 74-77 both-emitted cells, ~85-91% agreement) and field-emission asymmetry (mini doesn't fill is_itemized / total_other_costs / total_expenditure as often as Sonnet does).

## Topics Explored

- Hypothesis-testing the verbosity finding via on-disk evidence: bytes/completion-token ratio of 1.1-1.5 across 5 matched pairs (vs 2.5-4 typical for dense JSON) confirmed reasoning-token overhead before any new dispatch
- Schema-side hypotheses (empty nested-object skeletons, verbose `extraction_warnings`, new schema fields populated when source is silent) — set aside in favor of the reasoning_effort hypothesis once the bytes/token ratio was visible
- TDD-shaped implementation: `reasoning_effort` keyword param threaded through 3 layers, default `None` preserves byte-identical legacy SDK requests
- Parallelization design: extracted `_process_one_filing` as the shared worker, serial path preserved at `max_concurrent=1`, futures-based parallel path with thread-safe results aggregation + log serialization
- Run-label coupling to reasoning_effort (`mini_medium_run_1`, `mini_low_run_1`, `mini_minimal_run_1`) so each arm writes to a disjoint on-disk namespace
- Idempotent rename of the 55 existing partial-Run-1 dirs from `mini_run_1_*` → `mini_medium_run_1_*` (those were dispatched at API-default reasoning, which is medium for gpt-5-mini as of 2026-06)
- Cross-arm agreement analyzer design — exact equality after JSON canonicalization, both-null surfaced as its own bucket rather than counted as agreement, named-objects compared by `.name`, lists compared by length

## Provisional Findings

### Cost (per-filing avg, full-corpus extrapolation across 45,605 OH AERs)

| arm | reasoning_effort | $/filing | full corpus | vs Sonnet |
|---|---|---|---|---|
| Sonnet baseline | — | ~$0.0175 | $800 | reference |
| **medium** | API default | **$0.0079** | **$359** | 2.2× cheaper |
| **low** | low | **$0.0047** | **$212** | 3.7× cheaper |
| **minimal** | minimal | **$0.0041** | **$188** | 4.2× cheaper |

Minimal hits a cost floor: dropping from low to minimal cut completion tokens 15% but cost only 12% — structured-output JSON serialization is hitting a hard ~600-800 completion-token floor per filing that reasoning_effort can't compress further.

### Quality — null-rate divergence (n=100 per arm vs Sonnet 100% baseline)

`reporting_period_start` null count: medium 13 → low 20 → **minimal 98**. Monotonic with reasoning_effort. `reporting_period_end` follows the same shape (15 → 32 → 97). Minimal essentially stops populating reporting_period altogether — not abstention, the model isn't bothering with the field.

### Quality — when both arms emit (sonnet vs mini-medium, n=100)

| field | both_null | one_null | agree | disagree | rate (excl. nulls) |
|---|---:|---:|---:|---:|---:|
| filer_role / filing_id / filing_action / filer_person | 0 | 0 | 100 | 0 | 100% |
| filed_date / expenditures (len) / gifts (len) | 0 | 0 | 100 | 0 | 100% |
| total_expenditure | 28 | 58 | **14 / 14** | 0 | **100%** |
| is_itemized | 59 | 36 | **5 / 5** | 0 | **100%** |
| employer (name) / positions (len) | 0 | 0-5 | 95-99 | 1-5 | 95-99% |
| reporting_period_end | 0 | 15 | 77 | 8 | 90.6% |
| reporting_period_start | 0 | 13 | 74 | 13 | 85.1% |
| extraction_warnings (count) | 0 | 0 | 30 | 70 | 30% |

`extraction_warnings` 30% is brief-design difference, not extraction quality — mini was instructed to emit interpretive notes; Sonnet emits fewer. Not a worry.

`reporting_period_start` 85% is the lowest "real" agreement number. Worth digging into a few of the 13 disagreements to see whether they're 1-day-off normalization issues, semester boundary judgment calls, or genuinely different reads.

### Long-tail filing cost is reasoning-effort sensitive in the wrong direction

| filing | medium | low | minimal |
|---|---|---|---|
| 1423176 | (not in fresh-45) | $0.0289, 181s | **$0.0443, 244s, 21,427 completion tokens** |
| 1412254 | — | $0.0142, 85s | $0.0208, 110s, 9,782 completion tokens |

Mini's pathological cases get *more* expensive at lower reasoning effort — opposite of what a naive "less thinking = less cost" model would predict. The model spins in output mode when it can't think its way through. Real implication: full-corpus extrapolations using the median understate the tail; ~1% of filings could push total cost up by $20-30 regardless of setting.

### filer_organization is 100% both-null everywhere

Neither Sonnet nor any mini arm populates `filer_organization` on OH AERs (employer is in the dedicated `employer` slot). Not a mini-vs-Sonnet finding; an OH-AER-shape finding. Worth noting so it doesn't surface as a false issue later.

## Decisions Made

- **Drop minimal from the leave-behind framing.** It's below the quality floor for reporting_period; 97-98% null is not abstention calibration, it's the model skipping the field. Frame the comparison as Sonnet vs mini-medium for shipping, with mini-low as an "even cheaper if you can tolerate ~30% reporting_period nulls" option.
- **Medium is the production-defensible setting.** $359 full-corpus, ~85-91% agreement on date fields when both emit, 100% agreement on all dollar amounts and identity fields when both emit.
- **Surface the long-tail tax** (1423176 type) in the writeup. It's a real finding, not a measurement artifact, and Batches API + transient retry (task #35) is the principled fix.
- **Don't normalize dates yet** in the cross-arm analyzer. The 13-16 reporting_period disagreements at strict equality are the right baseline; spot-check a few before deciding whether normalization tightens or hides the signal.
- **STATUS.md line deferred** until cross-arm output was in (the output landed during this session writeup); will append a one-liner per the next entry.

## Results

- [`results/20260609_cross_arm_agreement.md`](../results/20260609_cross_arm_agreement.md) — per-(arm-pair, field) agreement table across sonnet × medium × low on the 100-filing intersection.

The three arm-1 dispatches themselves land as on-disk JSONs under `data/oh_portal/extracted_openai/<rid>/mini_<effort>_run_1_*/filing.json`; not promoted to `results/` as markdown since the cross-arm table is the analysis output that matters.

## Open Questions

- **Are the 13-16 reporting_period disagreements (medium) date normalization issues or genuinely different reads?** Easiest answer comes from grepping the on-disk filings for any 1-3 mismatches and eyeballing.
- **Is filing 1423176's pathology source-content-driven (long AER, ambiguous structure) or model-behavior-driven (loop on certain phrasings)?** Pulling that filing's raw HTML and reading it should answer in 2 minutes.
- **Should we re-add a Sonnet vs mini-medium per-list-content comparison?** The agreement-by-length numbers (95-100%) are encouraging, but a same-length disagreement on content could hide quality issues. Cheap follow-up if needed.
- **Suhan-facing writeup framing:** medium-only as the recommendation, or medium-as-default + low-as-budget-option? Depends on how downstream consumers use reporting_period.
- **Do we run passes 2 and 3 on each arm?** The original plan called for 3-pass self-consistency; with the 3-arm shape, that's 9 total passes. The cross-arm comparison is already a form of self-consistency check (3 different settings × 1 pass each). Probably not worth burning 6 more passes ($6-8) unless the medium-only inter-run noise floor is needed for the writeup.

## Spend this session

- Arm A (medium top-up, 45 fresh + 55 resume-skip): $0.3546 OpenAI
- Arm B (low, 100 fresh): $0.4652 OpenAI
- Arm C (minimal, 100 fresh): $0.4132 OpenAI
- **Total: ~$1.23 OpenAI** (no Anthropic)

Cumulative on this branch: ~$1.95 OpenAI + $0.31 Anthropic from this morning's 5 re-Sonnet runs = ~$2.26.
