# Phase B projection mappings — kickoff with CPI 2015 C11

**Date:** 2026-05-07 (eve, continuation of same-day Phase A session)
**Branch:** compendium-source-extracts
**Plan executed:** [`plans/20260507_atomic_items_and_projections.md`](../plans/20260507_atomic_items_and_projections.md) Phase B (first rubric only)
**Handoff consumed:** [`plans/_handoffs/20260507_phase_b_handoff.md`](../plans/_handoffs/20260507_phase_b_handoff.md)
**Spawning artifact:** the Phase B handoff written at end of the (pm) session.

## Summary

First Phase B projection-mapping doc shipped: CPI 2015 C11 (Lobbying Disclosure), the smallest concrete first target per the locked Phase C order. Operationalized the per-item template from the plan into a real per-rubric mapping and surfaced concrete schema decisions that will recur across the other 8 score-projection rubrics.

Three iteration cycles with the user before the doc landed clean. (1) Initial draft pushed back on cell type for `def_target_executive_branch` — user direction was "split into separate items for each case, most flexibility for downstream users", so the row split into `def_target_legislative_branch / legislative_staff / governors_office / executive_agency / independent_agency`, all binary, projecting via Boolean expressions. Granularity-bias was added to the doc-conventions block as a reusable rule for the rest of Phase B. (2) Confirmed the typed-cell-on-`MatrixCell.value` pattern (cleaner than named-scalar-with-citation) for the v2.0 schema migration; updated convention. (3) After draft, user pointed out evidence-companion field already exists in v1.1 schema (`FieldRequirement.evidence_source` + `evidence_notes` + `legal_citation`); retracted the misdiagnosed Open Issue 5 and replaced with the harder concern: de-facto cells in 2015 vintage face evidence-circularity if populated from CPI's own scores (validating against itself).

Mid-session: re-extracted scoring rules from `papers/CPI_2015__sii_criteria.xlsx` to fix TSV truncation (~300 char cap on previous extraction). Bonus discovery — the xlsx contains per-state per-indicator scores for all 50 states × 14 indicators, extracted to `cpi_2015_c11_per_state_scores.csv` (700 cells of ground truth, not just category aggregate). This dramatically strengthens Phase C validation.

Re-extraction also surfaced that **8 de-facto items use 5-tier scoring (0/25/50/75/100), not 3-tier** as the published criteria text suggests. CPI's published scoring rules document only 100/50/0 anchors but the realized data uses 25 and 75 as scorer-judgment partial credit between anchors. All 8 de-facto cell types in the doc updated from 3-tier enum to typed `int` ∈ {0, 25, 50, 75, 100}.

## Topics Explored

- Per-item projection mapping for all 14 CPI 2015 C11 items per the plan's Phase B template (rubric-item / compendium-rows / cell-type / axis / scoring-rule / source-quote).
- Schema decision: typed cells on `MatrixCell.value` vs named-scalar fields. The v1.1 schema declares `CompendiumItem.data_type` Literal but `MatrixCell` has no `value` field — gap to be filled in v2.0 schema bump alongside retiring the PRI-shape vestigial `de_minimis_*` named scalars.
- Granularity-bias convention for compendium row splitting: split on every distinguishing case (one row per registrant target type, etc.) for max downstream flexibility; projection logic combines via Boolean expressions.
- Re-extraction of full scoring-rule text from the criteria xlsx (previous TSV truncated at ~300 chars); discovery of per-state per-indicator scores (50 × 14 = 700 ground-truth cells).
- 5-tier vs 3-tier scoring discrepancy: published criteria document 3 anchors, realized data uses 5 tiers across all 8 de-facto items. Worked through 2 concrete examples (IND_205 access, IND_208 audits).
- Aggregation rule still TBD but Phase C now has both per-item per-state and category-aggregate ground truth — fitting any candidate aggregation formula is well-determined with this much data.
- Evidence-circularity concern for de-facto items: populating cells from CPI's own scores and projecting CPI back from those cells is a self-validation, not a real round-trip. Phase C may need to stage de-jure validation first (clean primary-source citations) and hold de-facto until practical-availability extraction can populate cells from primary observation.

## Provisional Findings

- The Phase B per-item template is workable for compound items (1-N row reads per item) without modification — IND_201 reads 3 rows, IND_205 reads 3 rows, the template handles both cleanly.
- Cluster IDs from the 3-way consensus output are useful provenance hints but NOT authoritative row identifiers — mapping work picks projection-meaningful row names and references clusters as `cf. strict-c_NNN` parentheticals only. (User reminder mid-session reinforced this: "earlier embedding groups aren't sacred, just guidelines. The real test will be this compendium-rubric mapping.")
- The v1.1 schema already partially supports what compendium 2.0 needs: `RegistrationRequirement.role` Literal enumerates exactly the granular target-type roles the user wants (governors_office / executive_agency / legislative_branch / independent_agency / etc.); `CompendiumItem.data_type` declares typed cells; `FieldRequirement.evidence_source` + `legal_citation` carry the evidence-companion. The gap is `MatrixCell.value` (typed value carrier missing) and the PRI-shape vestigial `StateMasterRecord.de_minimis_*` named scalars (should be retired in favor of generic compendium rows).
- CPI 2015 atomization is **higher-abstraction than HG 2007 / Newmark / Opheim** but **finer than a one-rubric-per-row mapping** would suggest — 14 CPI items map to 21 distinct compendium rows when the granularity-bias convention is applied. Splitting comes from the per-target-type def rows (5 from IND_196 alone) and from compound-item decompositions (#201 → 3 rows, #205 → 3 rows).
- All 6 de jure CPI items map cleanly: 1 is 2-tier (IND_196), 5 are 3-tier (YES/MODERATE/NO). All 8 de facto items are 5-tier (0/25/50/75/100). De jure axis lives on `legal_availability`, de facto on `practical_availability` — direct empirical validation of the v1.1 two-axis design.

## Decisions Made

| Topic | Decision |
|---|---|
| First Phase B target | CPI 2015 C11, completed |
| Granularity convention | Split on every distinguishing case (binary cells per case, Boolean projection composition); locked into doc-conventions block for reuse |
| Typed-cell pattern | `MatrixCell.value: Any` constrained by `CompendiumItem.data_type`; v2.0 schema bump retires named-scalar `de_minimis_*` fields |
| Cluster ID notation | `strict-c_NNN` / `loose-c_NNN` to disambiguate the two consensus files which use independent numbering |
| De-facto cell type | 5-tier typed int {0,25,50,75,100}, not 3-tier enum (correction from realized xlsx data) |
| Enforcement-adjacent items (#207/208/209) | Kept in scope — measure whether enforcement exists at all (precondition for disclosure to function), not enforcement strictness |
| Source-quote re-extraction | Done from xlsx; updated `items_CPI_2015_lobbying.tsv` with full text, no more 300-char truncation |
| Per-state per-indicator scores | Extracted to `cpi_2015_c11_per_state_scores.csv` (700 cells, 6 cells with data-quality glitches noted) |

## Results

- [`results/projections/cpi_2015_c11_projection_mapping.md`](../results/projections/cpi_2015_c11_projection_mapping.md) — Phase B mapping doc (251 lines, 14 items, 21 distinct compendium rows touched, 6 open issues for design-team review)
- [`results/cpi_2015_c11_per_state_scores.csv`](../results/cpi_2015_c11_per_state_scores.csv) — 700 cells (50 states × 14 indicators) of per-state per-indicator ground truth from the xlsx criteria sheet
- [`results/items_CPI_2015_lobbying.tsv`](../results/items_CPI_2015_lobbying.tsv) — updated with full scoring-rule text (no more truncation)

## Open Questions

1. **Aggregation rule for CPI category score.** With 700 per-cell + 50 category-aggregate ground-truth values, fitting any candidate aggregation formula is well-determined but requires Phase C to actually do the regression. Most likely candidates: (a) simple mean of 14 items, (b) sub-category mean → category mean, (c) de-jure-half + de-facto-half → mean. Verify against AK=97.5, AL=66.3, AZ=53.8 etc. once Phase C lands.
2. **De-facto 5-tier boundary semantics.** The 25 and 75 scores aren't documented in the published criteria — they're scorer-judgment partial credit. CPI's full SII methodology document might have additional guidance; not in our archive. Phase C will need to make a deterministic call on the boundaries OR pass cell values through directly (if compendium cells carry CPI-compatible 5-tier judgments rather than primary observable features).
3. **Evidence sourcing for de-facto cells in 2015 round-trip validation.** Populating from CPI's own scores creates self-validation circularity. Recommendation in mapping doc: stage Phase C — de-jure half first (statute-extracted, clean citations), de-facto half held until practical-availability extraction can populate from primary evidence (portal scrape, audit reports, FOIA). User decision pending whether to stage.
4. **Same template for other 8 rubrics?** PRI 2010 is next (83 items × 50 states = stress-test the template). User preference at session start was draft-CPI-first-then-review-before-fanout; CPI is reviewed and shipped, so PRI is the next concrete target.

## Mistakes recorded

1. **3-tier vs 5-tier mis-spec on first draft.** Initial doc had 3-tier enum cell types for de-facto items based on the published criteria text. Realized data uses 5 tiers. Caught only when re-extracting per-state scores from xlsx as a Phase C input. Corrected doc-wide before commit.
2. **Misdiagnosed an evidence-companion schema concern.** Open Issue 5 in first draft proposed adding a practical-availability evidence-narrative field. User pointed out the field already exists in v1.1 (`FieldRequirement.evidence_source` + `evidence_notes` + `legal_citation`) — schema concern was a non-issue. Retracted; replaced with the actual hard concern (evidence circularity in 2015 round-trip).
3. **Compound-item flagging as exception.** First draft framed compound items (1 rubric-item → 3 compendium-rows) as an exception to the template. User confirmed they're normal. Softened framing.
4. **Cluster-ID conflation between strict and loose files.** First read of the cpi-vs-consensus pre-walk doc would suggest strict and loose cluster IDs are interchangeable; they're independent numbering systems. Doc now disambiguates with `strict-c_NNN` / `loose-c_NNN` notation.

## Next Steps

1. **PRI 2010 Phase B mapping.** 83 items × 50 states. Same per-item template. Will stress-test compound-item handling at scale and likely add 30-50 new compendium rows the granular CPI mapping didn't surface (PRI E1f_i-iv itemization, E1h/E2h cadence options, A1-A11 registrant taxonomy with finer breakdowns than the 5 already in CPI's mapping).
2. **CPI 2015 source-quote completeness check.** Now that scoring rules are full-text, Phase B per-item template's "Source quote" entries are no longer truncated. No further action.
3. **Phase C scaffolding decision** (when ready) — `tests/fixtures/projection_inputs/cpi_2015_<state>.json` hand-population from the per-state-scores CSV is now a one-liner for the de-jure half (clean ground truth, no circularity). De-facto half held per Open Issue 3 above.
