# Sonnet validation → employer/warnings schema fix → statute-extraction archive

**Date:** 2026-06-04
**Branch:** oh-portal-aprime-batch (PR #33)

## Summary

Picked up the handoff to validate switching the OH extraction model from opus to
sonnet before the bulk grab. Validated against the (A') ground-truth filing 1427844
(same cached HTML the opus baseline `bd540187` used, so the only variable was the
model). `claude-sonnet-4-7` does not exist (404); sonnet is still on `4-6` while opus
advanced to `4-7`. Across 3 runs sonnet was **consistent** and on pure row-accuracy
matched or beat opus (it even fixes opus's one MISSING field, `is_itemized`) — but it
diverged on one field: it put the employer ("ARC Gaming & Technologies") into
`filer_organization`, where opus had left it null.

Reading the brief showed this is a **prompt/spec problem, not a model-quality
problem**: brief rule 6 said "populate ... employer name" but `LobbyingFiling` has no
employer slot, so the spec was internally contradictory and the two models broke the
tie differently (opus drops, sonnet jams). Both behaviors are silent. The fix is a
real schema slot + a channel for the model to flag content it can't represent.

A regime tangent (does the statute side's `regime` concept serve us here?) was run
down with help from a second agent: the branch/level axis was deliberately re-encoded
in v2 as controlled-vocab row IDs (`actor_*`/`def_target_*`), but `regime` as an
orthogonal *multiplier* (OH's parallel legislative/executive/retirement schemes) was
genuinely dropped in the v2 rebuild — a real v2.2 design gap, captured in the untracked
`state_regime_splitting.md`. Decision: do **not** add `regime` to `LobbyingFiling`
now; stamp it in run metadata and defer the first-class axis to v2.2.

Implemented the fix test-first, verified both models converge, switched the model to
sonnet, committed/pushed PR #33, and archived `statute-extraction` on main.

## Topics Explored

- Sonnet-4-6 vs opus-4-7 extraction of OH AER 1427844 (3 sonnet runs for consistency)
- Root-causing the `filer_organization` divergence to brief rule 6's contradictory spec
- Where `regime` lives on the statute side (`FieldRequirement.regime` freeform vs the
  controlled `RegistrationRequirement.role` / `actor_*` row-id vocabulary)
- Whether `statute-extraction` holds unmerged canonical schema (it does/did: commit
  `44fc762`; verified absent from `main`)
- The v2 selective carry-forward: `condition_text` kept, target/level re-encoded,
  regime-multiplier dropped

## Provisional Findings

- Sonnet's divergence is stable (3/3), so it's behavior, not noise — and it traces to
  the prompt, not model competence. After the brief fix, **both opus and sonnet route
  the employer to `employer`, leave `filer_organization` null, and populate
  `extraction_warnings`** (both flag the Section II.D sub-breakdown loss).
- Residual nit: sonnet lightly normalizes names (dropped the source "&." typo → "&");
  opus preserves verbatim. Low stakes; a one-line "preserve names verbatim" brief rule
  would close it if needed.
- Cost: sonnet-4-6 ($3/$15) vs opus-4-7 (~$5/$25) ≈ 1.67× cheaper (~40%), not the 5×
  I initially (wrongly) claimed. Per-filing cost is small either way.
- `regime` on the statute side is freeform `str | None` (NOT a Literal); the controlled
  branch/level vocabulary is a *different* axis (`actor_*` row IDs / `role` enum).

## Decisions Made

- **`MODEL_ID` → `claude-sonnet-4-6`** for the bulk OH extraction (both models correct
  post-fix; sonnet ~40% cheaper + fixes `is_itemized`).
- **Schema (additive):** `LobbyingFiling.employer: Organization | None` +
  `LobbyingFiling.extraction_warnings: list[str]`.
- **Brief:** route employer → `employer` (explicitly not `filer_organization`); add the
  warnings rule; delete the phantom `regime=` instruction; cut the internal `(A')` jargon.
- **`regime`:** caller-stamped in `extraction_run.json` (constant per OH-legislative
  brief); first-class regime axis deferred to the v2.2 gather-first schema pass.
- **Archived `statute-extraction`** (STATUS Active→Archived on main, commit `20ee37a`):
  harness superseded by compendium-2.0; marked DO-NOT-USE; stranded-schema findings
  recorded. Branch retained on origin (not merged, not deleted).

Commits: `e5d2da3` (fix, on oh-portal-aprime-batch) · `20ee37a` (archive, on main).

## Results

- [`results/20260604_sonnet_opus_validation.md`](../results/20260604_sonnet_opus_validation.md)
  — before/after model comparison (the validation behind the sonnet switch).

## Open Questions

- The actual **bulk OH discover→batch run** is still pending (gated on go + a
  robots.txt/ToS check). Now unblocked technically.
- **`state_regime_splitting.md` is untracked** — should be committed to preserve the
  regime-multiplier design rec before it's lost.
- **v2.2 regime-multiplier gap**: the row-per-target v2 model can't represent OH-style
  parallel statutory regimes for non-registration obligations. To be resolved
  deliberately in the gather-first v2.2 pass, not inherited by accident.
- Verbatim name fidelity under sonnet (typo normalization) — add a brief rule iff it
  matters downstream.
