# Gifts-empty spot-check — findings

**Date:** 2026-06-15
**Branch:** `oh-chain-composer`
**Trigger:** Q1 from the 2026-06-14 convo Open Questions — "Are the 0 gift-event rows a sampling artifact or an extraction-prompt scope issue?"

## TL;DR

**The 0-gifts result is neither.** It's an **empirical base-rate finding**: across the 305 cached filings in the 2025 reporting window, **zero filings have any non-empty itemized content in Section II.A (Gifts), II.B (Itemized Meals), or II.C-Legislative (Dinner/Party)**. All disclosed expenditure activity is concentrated in the **non-itemized sub-$50 meal aggregate** (Section II.D-Legislative / II.C-Executive).

The extraction brief at `src/lobby_analysis/oh_portal/extraction_brief.py` is **correctly scoped** for Section II.A and the prompt is being applied faithfully. The empty gifts release is a real measurement, not a defect.

**Implication for the PR:** branch is shippable. Update the `releases/oh/gifts/README.md` framing from "likely sampling artifact; secondary hypothesis is extraction-prompt scope" to "OH AERs in the 2025 window had zero itemized gifts; all expenditure activity is sub-$50 meal aggregates."

**Two orthogonal quality findings** also surfaced (form-type mismatch, line item below).

## Method

Three scripts under `/tmp/` (paths preserved for re-run):

1. `/tmp/oh_gifts_spotcheck.py` — first pass: regex Section II.A-D headers in raw.html. Returned 0 matches; revealed my regex was wrong because the actual HTML uses different markup.
2. `/tmp/oh_form_type_audit.py` — second pass: count filings by `<title>` form type.
3. `/tmp/oh_find_with_expenditures.py` — third pass: find filings where raw.html does NOT contain "No expenditures", cross-reference extracted JSON.

Then two direct reads of representative `raw.html` files (one Legislative-with-content, one Executive-with-content) to confirm the HTML structure of each form's Section II.

## Empirical findings

### 1. Form-type composition of the 305-filing cache

| Form | Count | % | Section II structure |
|------|-------|----|---------------------|
| Legislative AER | 164 | 54% | A (gifts) / B (meals) / C (dinner/party) / D (aggregate) — **matches brief** |
| Executive AER | 140 | 46% | A (gifts) / B (meals) / C (aggregate) — **brief expects B/C/D, finds A/B/C only** |
| Retirement AER | 1 | <1% | not inspected; almost certainly a third regime |

The brief is titled "OH legislative-agent AER" but the extraction pipeline applies it uniformly to all 305 cached filings, including 141 (46%) that are not legislative.

### 2. Section II content distribution

| Status | Total | Legislative | Executive | Retirement |
|--------|-------|-------------|-----------|------------|
| "No expenditures" in source | 286 (93.8%) | 147 | 138 | 1 |
| Has Section II content | 19 (6.2%) | 17 | 2 | 0 |

Of the **19 with-content filings**:

- **Zero** have any itemized content in Section II.A (Gifts).
- **Zero** have any itemized content in Section II.B (Itemized Meals).
- **Zero** have any itemized content in Section II.C-Legislative (Dinner/Party/Function).
- **17 of 17 Legislative filings** have content **only** in Section II.D ("Non-Itemized Meals and Beverages" — Meals Under $50 / Speaking Engagements / National Conference Meals).
- **2 of 2 Executive filings** have content **only** in Section II.C-Executive (the same Non-Itemized sub-$50 aggregate, renumbered).

Sample: filing `1398614` (Legislative, Susan Jagers / Ohio Poverty Law Center, Jan-Apr 2025) — `$142.25` in "Meals Under $50", all other rows zero or empty `<tbody>`.

### 3. Extraction outcomes

- 17 Legislative-with-content → 17 extracted `entertainment` rows (1 per filing, mapping Section II.D total to a single row per brief Rule 3). ✓
- 2 Executive-with-content → 2 extracted `entertainment` rows. ✓ — the model correctly maps Section II.C-Executive (which the brief literally describes as "Dinner/Party/Function itemized") to the same entertainment-aggregate semantics, *despite* the brief's section-letter mismatch.
- 2 with-content filings extracted 0 expenditures: both have all-zero dollar values (`$0.00` across all rows), so the brief's Rule 3 ("if Section D has a non-zero total, emit ONE row") correctly skips. Expected behavior.
- **Zero `gift`-category extractions** across the entire 305-filing cache — consistent with zero itemized Section II.A content in source.

## Conclusions

### Primary: 0 gifts is real, not a defect

The extraction brief explicitly covers Section II.A (Rule 2) and the model is applying it. The empty result reflects the empirical reality of the 2025 reporting window: **itemized gifts are essentially absent** from this sample. OH lobbying disclosure in this window is dominated by sub-$50 meal aggregates (Section II.D-Legislative / II.C-Executive).

### Secondary: form-type mismatch in the brief

The brief is titled for Legislative AERs but is applied uniformly to all 305 filings, including 141 (46%) Executive and Retirement AERs. Two specific issues:

- **Executive AERs have three subsections (A/B/C), not four (A/B/C/D).** The brief's Rule 2 says "Section II.A-C are itemized... (Gifts; Itemized Meals; Dinner/Party)" — true for Legislative, **false for Executive** where Section II.C is the non-itemized aggregate. Rule 3 says "Section II.D is a non-itemized aggregate" — **does not exist in Executive AERs**.
- The model recovers gracefully (correctly extracts the Executive II.C aggregate as one entertainment row), but this is brittle to model version, edge cases, and future regulatory form changes.

**Recommended remediation** (NOT in this branch, but worth filing as a follow-up issue):
- Either parameterize the brief by form type (Legislative / Executive / Retirement) and route at extraction time
- Or filter the discovery pipeline to Legislative-only, so the brief's scope matches its input

### Tertiary: extraction-prompt scope hypothesis is conclusively ruled out

The original chain-composer convo flagged extraction-prompt scope as a "secondary hypothesis" for the 0-gift result. This spot-check rules it out: the prompt covers Section II.A correctly, and the source data has zero II.A content to extract.

## Impact on the PR

- The `releases/oh/gifts/` empty TSV is honest output, not a quality concern.
- The `releases/oh/gifts/README.md` should be updated from "likely sampling artifact / secondary extraction-prompt scope" to an empirical base-rate framing.
- The top-level `releases/oh/README.md` should similarly reframe the gifts caveat.
- The form-type mismatch finding can be filed as a separate issue (or addressed in a follow-up branch) — it does not block this preview release.

## Impact on the $800 #35 full-corpus run

- **The brief does NOT need changes before the run.** Section II.A coverage is correct.
- **Expected gifts rate at full corpus:** still very sparse. If 0/305 in the 2025-window sample, full-corpus gifts will likely be 0 or single-digit absolute count. Worth confirming the base rate empirically rather than projecting.
- **Form-type filtering question** should be resolved before the run if discovery has expanded to include Executive/Retirement AERs at scale. If those forms are intentionally in scope, the brief needs to be split.

## Re-run artifacts

- `/tmp/oh_form_type_audit.py` — form-type composition counter
- `/tmp/oh_find_with_expenditures.py` — Section-II-content finder with JSON cross-reference

Both can be moved into `results/` if/when this branch keeps them as canonical re-run scripts.
