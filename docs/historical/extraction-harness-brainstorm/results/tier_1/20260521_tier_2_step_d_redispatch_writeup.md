<!--
Generated during: convos/20260521_tier_2_step_d_redispatch_verification.md
Plan: plans/20260521_tier_2_schema_adapter_fixes.md (Step D)
Extends: results/tier_1/20260520_tier_1_legal_axis_writeup.md ("Errors — 3 new classes")
-->

# Tier-2 Step D — re-dispatch verification of the A/B/C schema/adapter fixes

**Run date:** 2026-05-21 (UTC) · **Machine:** Dans-MacBook-Air · **State-vintage:** OH 2025
**Scope:** the 3 error-bearing chunks of the Tier-1 legal-axis run
(`registration_thresholds`, `lobbyist_spending_report`, `principal_spending_report`)
× `[claude-opus-4-7, gpt-5.2]` × 3 runs = **18 re-dispatches**.

## What this step does

Step D is the integration test for the Tier-2 plan
([`../../plans/20260521_tier_2_schema_adapter_fixes.md`](../../plans/20260521_tier_2_schema_adapter_fixes.md)).
Fixes A/B/C were committed and unit-tested in the 2026-05-21 Tier-2 execution
session, but whether they hold against **real API output** was deferred (both
API keys were unset that session). This step re-runs the 18 dispatches that
each carried exactly one `instantiation_failed` error in Tier-1, against the
now-committed fixes.

The 18 original Tier-1 result JSONs for these 3 chunks were moved (not deleted)
to [`_superseded/`](_superseded/) — they are the evidence behind the committed
Tier-1 writeup. The runner's resume logic then re-dispatched exactly the 18
now-missing triples into this directory; the other 3 chunks' files were left in
place and skipped.

## Run facts

| | |
|---|---|
| Re-dispatches | 18 / 18 completed (exit 0) |
| Session cost | **$1.8157** (within the plan's $10 session ceiling; max per-call $0.187) |
| Wall clock | ≈ 13 min |
| Prompt sha256 | `f1f90342…d79cb43` — identical to the Tier-1 run (same statute bundle, same system prompt) |

The handoff estimated "~12 calls / ~$1." The real scope was 18: **every** file
in all 3 named chunks carried an error in Tier-1, so all 18 triples were
re-dispatched. Cost tracked the Tier-1 cost for these chunks ($1.81).

## Pass criterion: NOT met — 15 / 18 clean, 3 still error

The plan's Step-D pass criterion is **zero `instantiation_failed` errors across
the re-dispatched chunks**. Result:

| Chunk | claude | gpt | Fix exercised |
|---|---|---|---|
| `registration_thresholds` | **3 errors** (run 1/2/3) | 0 errors | B (claude) / A (gpt) |
| `lobbyist_spending_report` | 0 errors | 0 errors | C |
| `principal_spending_report` | 0 errors | 0 errors | C |

The 3 remaining errors are all the **same cell** —
`lobbyist_registration_threshold_time_percent` (`TimeThresholdCell`), claude
only — and they are a **new finding**, not a recurrence of class B. Per Step-D
discipline ("any remaining error is a new finding — stop and report, do not
patch") nothing was patched.

## Fix-by-fix verdict

### Fix A — `int`/`float` → `Decimal` coercion — ✅ POSITIVELY VERIFIED

`gpt-5.2 registration_thresholds` runs 2 and 3 emitted
`{"row_id": "lobbyist_filing_itemization_de_minimis_threshold_dollars",
"value": 50, …}` — a **bare JSON `int`**, the exact input that triggered class A
in Tier-1. Both instantiated cleanly to a `DecimalCell` with value `Decimal("50")`.
Zero `instantiation_failed` errors in any of the 3 gpt `registration_thresholds`
runs. The coercion path fired on real output — this is a positive verification,
not merely an absence of failure.

(GPT abstained on the other `registration_thresholds` cells, consistent with
Tier-1's headline finding — see below — so only the one de-minimis cell
exercised the coercion. One real exercise is enough to confirm the path.)

### Fix C — null-valued `FreeTextCell` → abstention — ✅ VERIFIED

All 12 `lobbyist_spending_report` + `principal_spending_report` dispatches
(both models, all 3 runs) completed with **zero errors**. The conditional
`*_other_specification` rows that produced 12/12 class-C errors in Tier-1 now
route to `unscoreable_emissions` with
`reason: "conditional cell not applicable (value null)"`. The Tier-1-side
adapter sentinel works exactly as designed.

### Fix B — dict-shape `value` keys hint — ⚠️ PARTIAL: shape steered, new error surfaced

Fix B did **half** its job and surfaced a new problem with the other half.

**What worked.** In Tier-1, claude emitted a *bare string* for
`lobbyist_registration_threshold_time_percent`, failing with
`TypeError('TimeThresholdCell expects dict-shaped value, got str')` — class B.
Post-fix, all 3 claude runs emit a proper **JSON object** with the
`{magnitude, unit}` keys. The keys-only roster hint successfully steered the
model onto the dict shape; the class-B `TypeError` is gone.

**What broke.** The error *mutated* into a Pydantic validation error on the
field values:

| run | emitted `value` | error |
|---|---|---|
| 1 | `{"magnitude": null, "unit": "main_purpose_qualitative"}` | `unit` literal_error |
| 2 | `{"magnitude": "main_purpose", "unit": "qualitative"}` | `magnitude` is_instance_of + `unit` literal_error |
| 3 | `{"magnitude": null, "unit": "main_purpose_qualitative"}` | `unit` literal_error |

The valid `unit` domain is
`hours_per_quarter | hours_per_year | days_per_year | percent_of_work_time`.
Claude is inventing values (`main_purpose_qualitative`, `qualitative`) and once
a string `magnitude` (`main_purpose`).

## The new finding — and why "expand the enum domain" would NOT fix it

This is **not** a fumbled enum (a model picking a misspelled variant of a value
that exists). Read the model's own justifications — all 3 runs independently and
**correctly** reason that OH's statute has *no numeric time-percentage
threshold at all*:

> run 3: *"The statute defines a legislative agent as someone engaged 'during
> at least a portion of the individual's time to actively advocate as one of
> the individual's main purposes' — a qualitative 'main purpose' test, not a
> numeric time-percentage threshold."*

`TimeThresholdCell` is `{magnitude: Decimal | None, unit: TimeUnitLiteral | None}`.
It can represent "20 % of work time" or "no threshold" (`{null, null}`). It
**cannot** represent "this jurisdiction triggers registration on a qualitative
standard." The model, *instructed by Fix B's hint to emit a `{magnitude, unit}`
object*, is forced to invent a `unit` value to carry a concept the schema has no
slot for.

**The handoff proposed that a fumbled `unit` enum would be the trigger to
revisit the dropped enum-domain expansion. The evidence says otherwise.**
Expanding the prompt hint to list the 4 valid `unit` literals would not help:
none of the 4 fit, because OH genuinely has no quantitative threshold. Listing
them would, if anything, pressure the model to fabricate a wrong numeric answer
to satisfy the schema. This is a value-domain problem only in the trivial sense
that *any* error on a `Literal` field is; the substance is elsewhere.

**The substance: this is an abstention-calibration failure, and structurally a
class-C sibling.** The honest output for this cell is
`record_unscoreable_cell` — "OH uses a qualitative 'main purposes' test; there
is no time-percentage threshold to record." That is **exactly what GPT does**:
all 3 gpt `registration_thresholds` runs abstain on this cell with that
reasoning. Claude *under-abstains* — it has the same correct understanding (its
justifications prove it) but forces a malformed `record_cell` instead.

Like class C, the model is right and the schema cannot represent the answer.
Class C was "not applicable → `null` on a non-optional field"; this is
"qualitative law → no `{magnitude, unit}` exists." Both belong to the same
family: **the cell's type cannot encode a legitimate real-world answer, and the
model should abstain.**

**Fix B's hint may actively aggravate the under-abstention.** Appending
"emit `value` as a JSON object with keys: magnitude, unit" to the roster line
reads as an instruction to *produce that shape*. Pre-fix, claude's bare string
was at least a gesture at a non-numeric answer; the hint converted that into a
confidently-malformed dict. Fix B traded a `TypeError` for a `literal_error`
and plausibly nudged the model one step further from the correct abstention.

This routes to **Tier-1 writeup blocker 3 (the Phase-2 verifier's
abstention-calibration policy)** — not blocker 2 (enum-domain pinning). The
Tier-1 writeup already identified the `registration_thresholds`
qualitative-trigger divergence (Claude `0` vs GPT abstain) as the dominant
cross-model disagreement; this is the same fault line, surfacing here as an
*instantiation error* rather than a silent value disagreement.

## σ_noise (recomputed — read with care)

The runner recomputes inter-run agreement over all 6 chunks. Because only 3
chunks were re-dispatched, this figure is a **mix** of 3 original-Tier-1 chunks
and 3 post-fix chunks — it is not a clean re-measurement and should not be
compared head-to-head with the Tier-1 writeup's table.

| Model | n_cells | stable | value-unstable | scoreability-unstable | incomplete | % stable |
|---|---|---|---|---|---|---|
| claude-opus-4-7 | 84 | 72 | 7 | 4 | 1 | 85.71 % |
| gpt-5.2 | 84 | 67 | 11 | 5 | 1 | 79.76 % |

`incomplete` dropped from 3→1 (claude) and 6→1 (gpt): Fixes A and C removed
those cells from the error state. Claude's single remaining `incomplete` is the
`TimeThresholdCell` cell above. The headline % barely moved for claude (85.7 →
85.71) because the recovered cells landed as value/scoreability-unstable, not
stable.

## Verdict

Step D **clears 2 of the 3 Tier-1 error classes against real API output** (A and
C, positively verified) and **clears the original class-B mechanism** (bare
string → `TypeError`). It does **not** meet the plan's zero-error pass criterion:
the `TimeThresholdCell` cell now fails in a new way that Fix B cannot reach,
because the failure is not a schema/adapter typing bug — it is a model
emitting a `record_cell` where it should emit `record_unscoreable_cell`.

**Recommended next step:** fold this into blocker 3. The `TimeThresholdCell`
qualitative-jurisdiction case is concrete evidence for the abstention-calibration
policy the Phase-2 verifier needs — and a candidate scorer-prompt change
(instruct the scorer that a cell whose typed shape cannot encode the statute's
actual rule is an abstention, not a forced `record_cell`). Enum-domain pinning
(blocker 2) is genuinely independent and not implicated here.

**Do not patch Fix B further** without that policy decision. A narrow patch
(e.g. routing a `TimeThresholdCell` with an invalid `unit` to abstention, the
class-C move) would suppress the error but bury the real signal: claude is
under-abstaining on qualitative-trigger jurisdictions, and that will recur
across the other 49 states' definition chunks.

## Files produced

- `docs/active/extraction-harness-brainstorm/results/tier_1/` — 18 re-dispatch
  result JSONs (the 3 chunks above), replacing the originals.
- `docs/active/extraction-harness-brainstorm/results/tier_1/_superseded/` — the
  18 original Tier-1 JSONs for these chunks, preserved with a provenance README.
- This writeup.
