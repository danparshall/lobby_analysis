<!--
Generated during: convos/20260520_tier_0_direct_read_execution.md (execution session)
Plan: plans/20260518_tier_0_direct_read_smoke_test.md (Steps 5-7)
Originating convo: convos/20260518_tier_0_execution_pivot_to_direct_read.md
-->

# Tier 0 — Direct-read smoke test: writeup + architecture verdict

**Run date:** 2026-05-20 (UTC) · **Machine:** Dans-MacBook-Air · **Chunk:** `enforcement_and_audits` · **State-vintage:** OH 2025

## What the script does

`scripts/tier_0_direct_read_smoke.py` makes a **single API call per model**. The full OH 2025 Chapter 101 statute bundle (30 section files, ≈36K tokens) is embedded in a cache-controlled system prompt; a per-chunk user message lists the 4 `enforcement_and_audits` cells and asks the model to answer each via `record_cell` (or abstain via `record_unscoreable_cell`). It dispatches Claude Opus 4.7 and GPT-5.2 independently, parses tool calls into typed `CompendiumCell` instances, and saves raw + parsed JSON per model. No retrieval pass, no Citations API, no orchestrator.

## Run facts

| Model | Wall-clock | Cost (est.) | Tool calls | Typed cells | Unscoreable | Type-errors |
|---|---|---|---|---|---|---|
| claude-opus-4-7 | 17.48 s | $0.037 \* | 4 | 2 | 0 | **2** |
| gpt-5.2-2025-12-11 | 6.73 s | $0.059 | 4 | 1 | 3 | 0 |

\* Claude cost uses placeholder opus-4-**6** pricing (Steps 1–4 convo, caveat 1). Treat as order-of-magnitude. Total session dispatch ≈ **$0.10** — far under the $5 ceiling.

## Per-cell comparison

| Cell `(row_id, axis)` | Expected class | Claude | GPT |
|---|---|---|---|
| `penalties_imposed_in_practice, legal` | BinaryCell | `True` — cites §101.99;101.71;101.72(G);101.77 | `True` — cites §101.99(A)-(B) |
| `penalties_imposed_in_practice, practical` | GradedIntCell | `"2"` → **type-error** (string, not int) | **unscoreable** — "no evidence penalties imposed in practice" |
| `audit_required_in_law, legal` | EnumCell | `"review_only"` — cites §101.72(G);101.79 | **unscoreable** — "would need provisions not included" |
| `audit_required_in_law, practical` | GradedIntCell | `"1"` → **type-error** (string, not int) | **unscoreable** — "no info on audit frequency in practice" |

## Hand-eyeball verdicts (cited sections checked against bundle text)

- **§101.99** — verified verbatim. "(A) Whoever violates division (A),(B),(C) of section 101.71 … is guilty of a misdemeanor of the fourth degree. (B) … division (D) … first degree." Both models' `penalties_imposed_in_practice, legal = True` is **correct and well-cited**. GPT's `§101.99(A)-(B)` is the tightest precise cite; Claude's broader citation is also accurate.
- **§101.72(G)** — verified verbatim. JLEC executive director "shall be responsible for reviewing each registration statement … determining whether [it] contains all of the information required," issues deficiency notices, assesses a "late filing fee equal to twelve dollars and fifty cents per day, up to a maximum of one hundred dollars." Claude's justification (review-for-completeness + the $12.50/day-to-$100 fee) is **accurate verbatim**.
- **§101.79** — verified verbatim. "The attorney general … may investigate compliance with sections 101.70 to 101.78 … and, in the event of an apparent violation, shall report his findings to the prosecuting attorney of Franklin county." Both models read this correctly.

Verdict on Claude's `audit_required_in_law, legal = "review_only"`: **substantively correct** — the bundle shows a completeness-review mechanism (§101.72(G)) and discretionary AG investigation (§101.79) but no provision mandating systematic/financial audits. (Not cross-checked against `EnumCell`'s allowed value set — a Tier-1 verification. If `review_only` is a valid option, this is the right answer.)

## Success criteria (plan §"Success criteria")

| # | Criterion | Result |
|---|---|---|
| 1 | Script runs to completion, no uncaught exceptions | ✅ |
| 2 | Each model produces a `ScoringOutput`-like structure | ✅ |
| 3 | Each output contains 4 cells | ✅ (Claude 2 typed + 2 errored; GPT 1 typed + 3 unscoreable) |
| 4 | Each cell carries non-empty `cited_section` + `justification` | ✅ (incl. the errored cells) |
| 5 | Each cell `value` type-checks against `expected_cell_class` | ❌ **FAIL — Claude** (2 GradedIntCell cells) |
| 6 | Hand-eyeball plausibility | ✅ legal-axis verified; practical-axis — see below |
| 7 | Cell-by-cell side-by-side comparison | ✅ (this writeup) |

Per the plan: criterion 5 failed, so this is **reported, not patched**. The script is left as-is; the fix is Tier-1's job.

## The type-check failure (criterion 5) — root cause

Claude emitted `record_cell` for both `practical`-axis `GradedIntCell`s with `value="2"` and `value="1"` — JSON **strings**. `GradedIntCell.value` requires `int`; Pydantic rejected both (`int_type` validation error). The values are *content-correct stringified integers*, not garbage — this is an **encoding mismatch, not a reasoning error**.

Root cause: the shared `RECORD_CELL_INPUT_SCHEMA` `value` field is a loose `oneOf` that includes `{"type": "string"}` alongside `number`/`integer`. Claude picked the string branch for a graded int. This is exactly the plan's "What could change" item 3 (loose JSON typing may fail to type-check). Fixes available for Tier 1: tighten the schema's `value` type per cell-class, or add `str→int` coercion in `_instantiate_cell` (Pydantic lenient mode would also catch it). **Not done here** — plan says the failure mode is the deliverable.

**Why GPT shows 0 errors:** not better type handling — GPT *abstained* (`record_unscoreable_cell`) on the exact two cells where Claude attempted a score. GPT never attempted a `GradedIntCell`, so it never reached the buggy path. If GPT had scored those cells it would likely have hit the same string/int ambiguity.

## Practical axis: structurally unanswerable from a statute-only bundle

The most important finding. Both `practical`-axis cells ask about real-world behavior — *are penalties imposed* / *are audits conducted in practice*. A statute bundle cannot answer that.

- **GPT got this right.** Its two practical-axis unscoreable reasons ("no evidence penalties are actually imposed in practice," "no information on the frequency or extent of audits in practice") are well-calibrated — the statute text genuinely lacks enforcement data.
- **Claude over-reached.** It scored both practical cells (`2`, `1`) while its own justifications concede the gap — e.g., "the bundle does not show enforcement statistics to confirm frequency in practice." Scoring a practical cell from purely legal text, by the model's own admission, is the weaker behavior.

This is **not a direct-read architecture failure**, and critically **not something the Citations+retrieval escape hatch would fix** — retrieval over the same statute corpus hits the identical wall. Practical-axis cells need a *different data source* (enforcement records, agency reports, FOIA, news), not a different architecture.

## Model divergence (plan deliverable §7)

Two models, identical input, sharply different behavior:

1. **Scoreability philosophy.** Claude attempts all 4 cells (aggressive); GPT abstains on 3 of 4 (conservative). On `audit_required_in_law, legal` this produced a real disagreement: Claude scored `review_only` (correct — the law's *non-requirement* of an audit, combined with a present review mechanism, **is** a determinate answer); GPT called it unscoreable, treating absence-of-audit-mandate as missing information. Here GPT was **over-conservative** — for a "required in law?" question over a complete 30-section chapter, the requirement being absent is the answer.
2. **Output volume / latency.** Claude: 1339 output tokens, 17.5 s. GPT: 308 completion tokens, 6.7 s. Claude writes ~4× more justification text.
3. **Agreement where both scored:** 1 cell (`penalties…legal` = `True`), and they agree, both correct.

## Architecture verdict

**Direct-read is viable for the `legal` axis.** The wiring works end-to-end; both legal-axis cells are answerable from the bundle and were answered correctly (Claude 2/2; GPT 1/2 + 1 over-cautious abstention). The one mechanical failure (string-vs-int) is a trivial, well-understood schema bug, not an architectural problem.

**Direct-read cannot serve the `practical` axis with a statute-only bundle** — but neither could the Citations+retrieval escape hatch over the same corpus. The escape hatch is **not indicated** by this run: the failure that occurred is a data-*source* gap, not a retrieval gap.

So Tier 0 does not cleanly select either forward branch from the plan. It selects a **third path**:

1. **Fix the `value` typing bug** (schema tightening or `_instantiate_cell` coercion) — small, do it first in Tier 1.
2. **Decide the scope of the `practical` axis.** Either (a) exclude practical-axis cells from a statute-fed pipeline, or (b) source a separate practical-evidence corpus. This is a research decision for the user, not an implementation detail.
3. **Proceed to Tier 1 direct-read on the `legal` axis** across the 6 CPI-2015 de-jure chunks — that is what this run shows is ready.
4. **The Claude-aggressive / GPT-conservative split** is itself a signal the Phase-2 verifier agent must handle: a verifier needs an explicit abstention-calibration policy, because the two models disagree on *when a cell is scoreable* even when they agree on the underlying statute facts.

## Surprises

- **GPT's 0 type-errors is an artifact, not a virtue** — it dodged the buggy path by abstaining, not by handling types better.
- **The bug and the divergence are entangled:** the same two cells that trigger the string/int bug are the ones the models disagree about scoring. A different prompt that pushed both models to score would have surfaced the bug symmetrically.
- **Over-conservative abstention is a failure mode too.** GPT marking `audit_required_in_law, legal` unscoreable looks safe but discards a correct, determinable answer. Abstention is not free.
- **`record_cell.value` schema looseness bit on the very first run** — the plan flagged it as a "what could change"; it changed immediately.

## Files produced this run

- `results/20260518_tier_0_raw_anthropic_enforcement_and_audits.json`
- `results/20260518_tier_0_parsed_anthropic_enforcement_and_audits.json`
- `results/20260518_tier_0_raw_openai_enforcement_and_audits.json`
- `results/20260518_tier_0_parsed_openai_enforcement_and_audits.json`
- `results/20260518_tier_0_direct_read_writeup.md` (this file)
