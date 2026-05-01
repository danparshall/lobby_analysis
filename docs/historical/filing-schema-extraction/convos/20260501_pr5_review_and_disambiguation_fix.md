# PR #5 Review and Disambiguation Fix

**Date:** 2026-05-01
**Branch:** filing-schema-extraction

## Summary

Reviewed PR #5 (compendium audit v2 + v1.2 schema bump). Verified per-rubric atomic-item counts (19/18/22/48/7) against the source papers, the dedup-map, and the per-source-framework counts (all line up). Walked the 23 NEW row IDs to confirm they exist with the claimed domains; walked the 7 `domain="definitions"` rows against the "who is a lobbyist?" predicate and found them defensible. Disclosure-only scoping holds across the 27 `OUT_OF_SCOPE` dispositions. Tests pass 24/24.

Pushed back on Decision Log D11 (v1.2 schema bump). Two issues surfaced:

1. **D11 contradicted D9 in the row descriptions.** The new `DEF_EXPENDITURE_STANDARD` / `DEF_TIME_STANDARD` rows described themselves as inclusion-framed parallels of the (D9-renamed) `THRESHOLD_LOBBYING_*_PRESENT` rows, while those `THRESHOLD_*` rows' own descriptions still claimed to capture both inclusion- and exemption-framings. Harness had no rule for which row a given statute populates.
2. **Symmetry-gap argument initially seemed to overgeneralize.** `DEF_COMPENSATION_STANDARD` is genuinely income-side vs PRI D1's expenditure-side (real asymmetry); the question was whether expenditure-vs-time inclusion/exemption splits mirror that asymmetry or just split a single mechanism on a linguistic seam.

User produced a concrete counter-example: a statute reading "spends their primary time on lobbying, unless their total expenses are < $1k." That statute populates `DEF_TIME_STANDARD` (inclusion-framed time trigger) AND `THRESHOLD_LOBBYING_EXPENDITURE_PRESENT` (exemption-framed expenditure carve-out) — independent statutory mechanisms on different axes. Issue #2 retracted; cross-axis case justifies the split.

Same-axis case still ambiguous, so tightened both row pairs' descriptions: `THRESHOLD_LOBBYING_*_PRESENT` exemption-framed only; `DEF_*_STANDARD` inclusion-framed only; each row's description points to its counterpart and states that both populate when the statute combines an inclusion trigger on one axis with an exemption carve-out on another.

Also reconciled durable-record arithmetic in `results/20260430_compendium_audit.md` — Summary line OOS count, Excluded-items log enforcement count, and per-rubric Items folded/excluded for Opheim and CPI now match the dedup map.

## Topics Explored

- Per-rubric count verification (19/18/22/48/7 for Newmark 2017 / Newmark 2005 / Opheim 1991 / CPI Hired Guns / OpenSecrets 2022) against source papers, dedup-map entries, and per-rubric tables
- 23 NEW rows: existence, domain placement, conceptual fit
- `domain="definitions"` placement for the 7 rows under the "who is a lobbyist?" rule
- D9 (threshold rename) vs D11 (v1.2 schema bump): contradiction analysis in row descriptions
- Symmetry-gap argument: same-axis vs cross-axis statutory mechanisms
- Audit-doc summary number reconciliation (Summary section, Excluded-items log, per-rubric tables)

## Provisional Findings

- The cross-axis case (e.g., time-trigger + expenditure-exemption) is real and justifies the v1.2 split between `DEF_*_STANDARD` and `THRESHOLD_LOBBYING_*_PRESENT`. Same-axis statutes populate one row or the other, not both.
- The audit-doc Summary line's `41 OUT_OF_SCOPE` claim was inconsistent with both its own per-rubric tables (sum to 27) and the dedup-map (27 OOS entries). Per-rubric Items excluded for Opheim (claimed 8, actual 7) and CPI (claimed 10, actual 11) had opposite-sign typos that cancelled in the per-rubric sum but were individually wrong.
- Per-rubric atomic-item counts hold against paper text. Opheim 1991 explicitly states "The sum of all 22 items"; Newmark 2017 explicitly states "the above 19 categories"; Newmark 2005 explicitly states "range of 0 to 18"; CPI questions Q1–Q48 are sequentially numbered.

## Decisions Made

- **Disambiguation rule for `DEF_*_STANDARD` ↔ `THRESHOLD_LOBBYING_*_PRESENT` row pairs.** `THRESHOLD_*_PRESENT` is now exemption-framed only; `DEF_*_STANDARD` is inclusion-framed only. Both rows in a pair populate when a state combines an inclusion trigger on one axis with an exemption carve-out on another. Encoded in row descriptions; recorded as a Decision Log D11 addendum in the audit doc.
- **Audit-doc reconciliation.** Summary line's NEW (22 → "21 net + 2 v1.2 = 23"), OOS (41 → 27), and EXISTS/MERGE (51 → 87 dedup-map entries) reframed for honest accounting; Excluded-items-log enforcement count fixed (14 → 12); per-rubric Opheim folded 14 → 15, excluded 8 → 7; per-rubric CPI folded 22 → 21, excluded 10 → 11.
- **Audit-doc lifecycle move.** On merge to main, `docs/active/filing-schema-extraction/results/20260430_compendium_audit.md` moves to repo-level `docs/COMPENDIUM_AUDIT.md` per the plan (anti-loop artifact discoverable in pre-flight reads).

## Results

- `data/compendium/disclosure_items.csv`: 4 row descriptions tightened (no schema or row-count change)
- `docs/active/filing-schema-extraction/results/20260430_compendium_audit.md`: arithmetic reconciliation + D11 disambiguation addendum (later moved to `docs/COMPENDIUM_AUDIT.md` on merge)

## Open Questions

- Coverage matrix (`data/compendium/coverage_matrix.csv`) generation still deferred — small follow-up task.
- Harness brainstorm against the 108-row statute-side universe (kickoff plan's design questions Q1–Q7) is the next concrete piece of work.
