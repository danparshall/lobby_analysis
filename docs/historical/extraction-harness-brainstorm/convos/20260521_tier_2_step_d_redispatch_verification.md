# Tier-2 Step D — re-dispatch verification

**Date:** 2026-05-21
**Branch:** extraction-harness-brainstorm

## Summary

Executed **Step D** of
[`plans/20260521_tier_2_schema_adapter_fixes.md`](../plans/20260521_tier_2_schema_adapter_fixes.md)
— the re-dispatch verification deferred from the 2026-05-21 Tier-2 execution
session (deferred then because both API keys were unset). Step D re-runs the 18
dispatches that each carried one `instantiation_failed` error in the Tier-1
legal-axis run, against the now-committed A/B/C fixes, to check whether the
fixes hold against **real API output**.

Result: **2 of 3 fixes clear cleanly; Fix B is partial and surfaced a new
finding.** The plan's zero-error pass criterion is **not met** — 15/18
re-dispatches are error-free, but the 3 `claude registration_thresholds` runs
still error on one cell, in a new way. Per Step-D discipline ("any remaining
error is a new finding — stop and report, do not patch") nothing was patched.

Full analysis: [`results/tier_1/20260521_tier_2_step_d_redispatch_writeup.md`](../results/tier_1/20260521_tier_2_step_d_redispatch_writeup.md).

## Topics Explored

- Re-dispatch mechanics: moved the 18 original Tier-1 result JSONs for the 3
  error-bearing chunks to `results/tier_1/_superseded/` (preserved, not
  deleted), let the runner's resume logic re-dispatch exactly those 18 triples.
- Fix A (`int`/`float` → `Decimal`) verified against a real bare-JSON-`int`
  emission.
- Fix C (null `FreeTextCell` → abstention) verified against the conditional
  `*_other_specification` rows.
- Fix B (dict-shape keys hint) traced from "did it steer the shape?" (yes) to
  "did the cell instantiate?" (no) — the error mutated rather than cleared.

## Provisional Findings

- **Fix A — positively verified.** `gpt registration_thresholds` runs 2/3
  emitted `"value": 50` (bare JSON `int`); both instantiated cleanly to
  `DecimalCell(Decimal("50"))`. The coercion path fired on real output.
- **Fix C — verified.** All 12 spending-report dispatches error-free; the
  null-valued `*_other_specification` rows route to `unscoreable_emissions`
  with `reason: "conditional cell not applicable (value null)"`.
- **Fix B — partial.** The keys-only hint successfully moved claude off the
  bare-string failure — all 3 runs now emit a proper `{magnitude, unit}` dict,
  so the original class-B `TypeError` is gone. But a **new error** surfaced:
  claude fills `unit` with out-of-domain values (`main_purpose_qualitative`,
  `qualitative`) and once `magnitude` with a string (`main_purpose`).
- **The new finding — `TimeThresholdCell` cannot represent a qualitative
  jurisdiction.** Claude's own justifications (all 3 runs) correctly state that
  OH has *no numeric time-percentage threshold* — registration triggers on a
  qualitative "main purposes" test. `TimeThresholdCell` ({magnitude, unit})
  cannot encode that, so the model — instructed by Fix B's hint to emit the
  dict — invents `unit` values. **GPT abstains on this exact cell, all 3 runs,
  with the same reasoning** — the correct behavior. Claude *under-abstains*.
- This is structurally a **class-C sibling** (model right, schema can't
  represent the answer) and an **abstention-calibration** failure — Tier-1
  writeup **blocker 3**, *not* blocker 2 (enum-domain pinning).

## Decisions Made

- **No patch.** Step-D discipline: a new error is reported, not patched. The
  writeup recommends *against* a narrow Fix-B patch (e.g. routing an invalid
  `TimeThresholdCell` to abstention) because it would bury the real signal —
  claude under-abstaining on qualitative-trigger jurisdictions, which will
  recur across the other 49 states.
- **Pushed back on the handoff's framing.** The handoff proposed that a fumbled
  `unit` enum would trigger revisiting the dropped enum-domain expansion. The
  evidence contradicts this: expanding the prompt hint to list the 4 valid
  `unit` literals would not help — none fit, because OH has no quantitative
  threshold at all. The finding routes to abstention calibration (blocker 3),
  and enum-domain pinning (blocker 2) is not implicated.
- Superseded Tier-1 JSONs **moved, not deleted** — `results/tier_1/_superseded/`
  with a provenance README. The committed Tier-1 writeup's evidence is intact.

## Results

- [`results/tier_1/20260521_tier_2_step_d_redispatch_writeup.md`](../results/tier_1/20260521_tier_2_step_d_redispatch_writeup.md)
  — Step-D writeup: run facts, fix-by-fix verdict, the new finding.
- 18 re-dispatch result JSONs in `results/tier_1/` (3 chunks × 2 models × 3
  runs); 18 originals preserved in `results/tier_1/_superseded/`.
- Run cost **$1.8157** (within the $10 session ceiling). The handoff's
  "~12 calls / ~$1" undercounted — all 18 files in the 3 named chunks carried
  an error, so all 18 triples were re-dispatched (~$1.81).

## Commits

On top of `4b5c3b6` (the Tier-2 execution convo commit):

- One Step-D checkpoint commit — the 18 `git mv` renames into `_superseded/`,
  the 18 new re-dispatch JSONs, the `_superseded/README.md` provenance banner,
  the writeup, this convo, and the RESEARCH_LOG / STATUS / plan updates.

## Open Questions / Next Steps

- **Blocker 1 status:** the Tier-2 schema/adapter fixes (Tier-1 verdict
  blocker 1) are **partially cleared** — A and C verified against real output,
  the original class-B mechanism cleared, but the `TimeThresholdCell` cell now
  fails in a new way that is not a schema/adapter typing bug.
- **Next — blocker 3 (abstention-calibration policy).** The `TimeThresholdCell`
  qualitative-jurisdiction case is concrete evidence for the policy the Phase-2
  verifier needs. Candidate scorer-prompt change: instruct the scorer that a
  cell whose typed shape cannot encode the statute's actual rule is an
  abstention, not a forced `record_cell`.
- **Then — blocker 2 (enum-domain pinning).** Independent of the above; still
  future work.
- **Open design question:** should `_instantiate_cell` route a
  `TimeThresholdCell` with an invalid `unit` to abstention (the class-C move)?
  The writeup argues *not* as a standalone patch — it would suppress the
  under-abstention signal. Revisit once the blocker-3 policy is decided.
