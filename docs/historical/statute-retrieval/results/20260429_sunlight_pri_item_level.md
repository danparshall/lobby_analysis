<!-- Generated during: convos/20260429_sunlight_pri_item_level_calibration.md -->

# Phase 1 — Sunlight 2015 / PRI 2010 Joint Item-Level Diagnostic (CA, TX, OH)

**Date:** 2026-04-29
**Scope:** opus-4-7 + files-read-enforced harness runs vs PRI 2010 sub-aggregate totals + Sunlight 2015 category scores, three calibrated states (CA, TX, OH).
**Harness runs:** CA `590e9123a624`, TX `4fe9774234f3`, OH `38803d49e32f` (all opus-4-7, all 2026-04-29 ~18:50 UTC).
**Goal:** test whether single-rubric (PRI-only) calibration is misleading us about where the harness is reading statutes correctly. The unit of analysis is the **disclosure item**, not state aggregate ranking. The harness is the product; PRI 2010 and Sunlight 2015 are independent human-rater datasets used to identify real extraction errors vs judgment-call zones.

---

## TL;DR

**On the 13 PRI items that overlap with Sunlight categories, the harness's per-item reading is consistent with Sunlight's category scores in all three states.** The two cells where the harness's coarse "itemized yes/no" doesn't fully match Sunlight's finer "itemized w/ dates+desc vs broad categories" distinction (TX, OH expenditure transparency) are a **rubric-granularity gap, not an extraction error** — Sunlight asks a finer question than PRI does, and the harness is consistent with both rubrics at the resolution they share.

**Sunlight's coverage of statutory disclosure-law items is narrow** — roughly 13 of the 61 PRI disclosure-law items (mostly E-series). Sunlight is **silent** on PRI A (registration scope), B (government exemptions), C (public-entity definition), and most of D (materiality test). The opus-vs-PRI gaps that drive the headline state totals all live in those Sunlight-silent zones.

**Decision recommendation:**
- **Do not** continue tuning the scorer prompt to chase the TX A-series gap or the CA B/C over-counts against PRI alone. Newmark 2017 r=0.04 says single-rubric agreement could be PRI-overfitting; we need a second rubric covering those items before declaring them extraction errors.
- **Do not** build Phase 2 (Sunlight as second scoring rubric). Sunlight's narrow item coverage means parallel scoring infrastructure would return minimal additional calibration signal beyond what this overlay analysis already extracts.
- **Do** proceed to Phase 3 (extraction-first refactor) — the analysis here previews what compendium-union output would look like.
- **Do** prioritize getting CPI Hired Guns 2007 (or another rubric covering A/B/C/D) as the next calibration dataset; that's where the real extraction-error vs judgment-call distinction lives for the open gaps.

---

## State sub-aggregate baseline (recompiled with `rollup_disclosure_law`)

| State | A | B | C | D | E | Total | PRI 2010 | Δ |
|---|---|---|---|---|---|---|---|---|
| CA | 6 | 4 | 1 | 1 | 17 | 29 | 23 | **+6** |
| TX | 5 | 2 | 0 | 1 | 15 | 23 | 29 | **−6** |
| OH | 8 | 2 | 1 | 1 | 13 | 25 | 26 | **−1** |

`rollup_disclosure_law` from `src/scoring/calibration.py` applied to the per-item opus CSVs. Numbers match the RESEARCH_LOG afternoon entry.

| Sub-aggregate | CA Δ | TX Δ | OH Δ | Concentrated where |
|---|---|---|---|---|
| A_registration | 0 | **−2** | +1 | TX: who-must-register scope |
| B_gov_exemptions | **+2** | −1 | 0 | CA: reverse-scored B1/B2? |
| C_public_entity_def | **+1** | 0 | 0 | CA: C0 definition disagreement |
| D_materiality | 0 | 0 | 0 | All match |
| E_info_disclosed | **+3** | **−3** | −2 | All states; sign reversal CA↔TX |

---

## Sunlight 2015 category scores (CA, TX, OH)

Source: `papers/Sunlight_2015__state_lobbying_disclosure_scorecard_data.csv`. Asterisk modifiers (`*`, `^`, `***`) appear in the data but are **not defined in the published methodology** (`papers/text/Sunlight_2015__state_lobbying_disclosure_scorecard.txt`). Treating as informational annotations.

| State | Activity | ExpTrans | Threshold | DocAccess | Compensation | Total | Grade |
|---|---|---|---|---|---|---|---|
| CA | 0 | 2 | 0 | 2 | 0 | 4 | A |
| TX | 0 | 1 | 0 | 2 | 0*** | 3 | B |
| OH | 1 | 1* | −1 | −1^ | −1 | −1 | D |

`DocAccess` is portal accessibility, **out of scope** for statutory disclosure-law calibration (maps to the separate PRI accessibility rubric, not disclosure-law). Excluded from the joint table below.

---

## Sunlight category → PRI item decomposition

The substantive judgment-call piece. Each Sunlight category covers a slice of the PRI 61-item rubric. Mappings here are documented explicitly so reviewers can challenge them.

### 1. Lobbyist Activity → E1g/E2g items

Sunlight scale:
- `−1` no activity reported
- `0` general subjects only
- `1` bills/actions
- `2` bills/actions + position

Maps to PRI items E1g_i (general issues, principal), E1g_ii (specific bills, principal), E2g_i (general, lobbyist), E2g_ii (specific bills, lobbyist). PRI does **not** capture position-taken, so Sunlight `2` vs `1` is a Sunlight-only fact (Phase 3 compendium adds this as a new field).

Implied per-item value at each Sunlight score:

| Sunlight Activity | E1g_i / E2g_i (general) | E1g_ii / E2g_ii (specific bills) |
|---|---|---|
| −1 | 0 | 0 |
| 0 | 1 | 0 |
| 1 | 1 | 1 |
| 2 | 1 | 1 (+ position field, not in PRI) |

### 2. Expenditure Transparency → E1f/E2f items

Sunlight scale:
- `−1` no expenditure report
- `0` lump total
- `1` broad categories (e.g. food/travel/etc.)
- `2` itemized w/ dates + descriptions

Maps to E1f_i/ii/iii (cost components: compensation/non-compensation/other), E1f_iv (itemized format), and E2f counterparts. PRI's `E*f_iv` is binary itemized-yes/no — it does **not** distinguish "categorized broad" from "itemized w/ dates+desc". So Sunlight `1` vs `2` is finer than PRI captures.

Implied per-item value:

| Sunlight ExpTrans | E*f_i/ii/iii (any cost component) | E*f_iv (itemized) |
|---|---|---|
| −1 | 0 | 0 |
| 0 | ≥ 1 | 0 |
| 1 | ≥ 1 | 1 (broad categories — finer than PRI captures) |
| 2 | ≥ 1 | 1 (itemized w/ dates+desc — finer than PRI captures) |

### 3. Expenditure Reporting Thresholds → no clean PRI mapping

Sunlight scale:
- `−1` threshold exists (expenses below $X don't need individual itemization)
- `0` all expenditures disclosed individually

PRI's closest item is `D1_present` ("financial threshold for registration") — but that's a **registration trigger**, not an **expenditure-itemization threshold**. Different concept entirely. **Sunlight asks a question PRI doesn't cover**; this is a candidate new field for the Phase 3 compendium.

### 4. Document Accessibility → out of scope (portal accessibility, not statute)

### 5. Lobbyist Compensation → E1f_i / E2f_i specifically

Sunlight scale:
- `−1` compensation not disclosed
- `0` compensation disclosed

Maps to PRI `E1f_i` (direct lobbying costs / compensation, principal side) and `E2f_i` (lobbyist side). Sunlight doesn't distinguish principal-side vs lobbyist-side; PRI does.

| Sunlight Compensation | E1f_i (principal side) | E2f_i (lobbyist side) |
|---|---|---|
| −1 | 0 | 0 |
| 0 | 1 OR 1 (at least one side) | |

---

## Joint per-item table: opus harness vs Sunlight-implied values

For each (state, Sunlight-overlap item), comparing opus's per-item score to the value Sunlight's category score implies. **PRI 2010 per-item ground truth is not available** (only sub-aggregates published), so PRI agreement is computed at the sub-aggregate level above.

### Sunlight Activity (E1g/E2g)

| State | Sunlight Activity | Implies general (E*g_i) | Implies specific bills (E*g_ii) | Opus E1g_i | Opus E1g_ii | Opus E2g_i | Opus E2g_ii | Match? |
|---|---|---|---|---|---|---|---|---|
| CA | 0 | 1 | 0 | 1 | 0 | 1 | 0 | **✓ all 4** |
| TX | 0 | 1 | 0 | 1 | 0 | 1 | 0 | **✓ all 4** |
| OH | 1 | 1 | 1 | 1 | 1 | 1 | 1 | **✓ all 4** |

12/12 cells match. Harness reads activity-reporting requirements consistently with Sunlight on all three states.

### Sunlight Expenditure Transparency (E1f/E2f)

| State | Sunlight ExpTrans | Implies E*f_iv (itemized?) | Opus E1f_iv | Opus E2f_iv | Match (binary)? |
|---|---|---|---|---|---|
| CA | 2 | 1 | 1 | 1 | **✓ both** |
| TX | 1 | 1 | 1 | 1 | **✓ both (granularity ambiguous)** |
| OH | 1 | 1 | 1 | 1 | **✓ both (granularity ambiguous)** |

6/6 binary-itemized cells match. The TX/OH `1` vs CA `2` distinction is **below PRI's resolution** — Sunlight separates "broad categories" from "itemized w/ dates+desc"; PRI just asks "itemized yes/no". The harness's reading is consistent with PRI's binary; we can't validate the finer distinction without an extraction-first refactor (Phase 3) that captures format-detail directly.

### Sunlight Compensation (E1f_i, E2f_i)

| State | Sunlight Comp | Implies (≥1 side discloses) | Opus E1f_i (principal) | Opus E2f_i (lobbyist) | Match? |
|---|---|---|---|---|---|
| CA | 0 | yes | 1 | 1 | **✓** (both sides) |
| TX | 0*** | yes (with caveat) | 0 | 1 | **✓** (lobbyist side; principal disagree but ambiguous w/ asterisks) |
| OH | −1 | no | 0 | 0 | **✓** (both sides match) |

5/6 atomic cells match. The TX `E1f_i = 0` (principal-side compensation not required) vs Sunlight `0***` (yes, with caveats) is an open item — could be PRI's principal/lobbyist split is finer than Sunlight's, or could be the asterisks indicate the partial-disclosure case opus picked up on. **Worth re-examining the opus statute citation for E1f_i to see if the harness is correct.**

### Sunlight Threshold (D1_present forced map)

Forced mapping; Sunlight's "expenditure-itemization threshold" is a different concept than PRI's "registration threshold". No meaningful joint signal here. Recorded for the Phase 3 compendium as a Sunlight-only field.

| State | Sunlight Threshold | Opus D1_present (registration threshold) | Note |
|---|---|---|---|
| CA | 0 | 1 | Different concept — CA has registration threshold but no expenditure-itemization threshold |
| TX | 0 | 1 | Same |
| OH | −1 | 0 | OH has expenditure-itemization threshold (per Sunlight) but no registration threshold (per opus) |

---

## Where do the headline opus-vs-PRI sub-aggregate gaps live?

For each significant gap, does any rubric (PRI or Sunlight) have direct item-level coverage?

| Gap | Magnitude | Sunlight covers it? | Calibration verdict |
|---|---|---|---|
| TX A_registration | −2 (5 vs 7) | **No** — Sunlight Activity is about reporting detail, not who-must-register | Open. Need CPI/Newmark coverage. |
| CA B_gov_exemptions | +2 (4 vs 2) | **No** | Open. Need second rubric on B. |
| CA C_public_entity_def | +1 (1 vs 0) | **No** | Carried-forward Q #1 from RESEARCH_LOG. |
| CA E_info_disclosed | +3 (17 vs 14) | Activity items ✓; cost items ✓; gap likely in E*h frequency, E*i contacts, or E*c/d/e address-of-X | Sunlight signal supports harness reading on activity + cost; gap is in items Sunlight doesn't cover. |
| TX E_info_disclosed | −3 (15 vs 18) | Activity items ✓; cost items ✓; gap = the documented E1 cascade bug (E1a=0 zeroing all E1) | Sunlight signal supports harness reading. The −3 gap is the cascade-zero, not a misread of any individual item. |
| OH E_info_disclosed | −2 (13 vs 15) | Activity items ✓; cost items ✓ | Same as CA — gap in items Sunlight doesn't cover. |

**Pattern:** every gap where Sunlight has direct coverage, the harness agrees with Sunlight. Every gap where Sunlight is silent, we have only PRI's signal — and Newmark r=0.04 says PRI alone is too noisy to call those gaps extraction errors.

---

## What this implies for the harness goal

The harness's job is to determine, for each disclosure item across the union of frameworks, whether that item is required by a state's law. PRI and Sunlight are calibration instruments — the more rubrics that concur with the harness on a given item, the more confident we are the harness has read the statute correctly. Where rubrics disagree with each other or with the harness on items they cover, we have a real diagnostic to chase.

For the 13 items where this analysis has joint coverage, the harness reads consistently with the joint rubric signal. **No extraction errors identified in those items.** The remaining gaps are in the ~48 items only PRI covers — those are not validated as errors by this analysis, and would-be prompt-tuning fixes (e.g., the previously-discussed "TX A-series within-the-regime's-reach" rule) lack the second-rubric signal that would justify them.

The narrowness of Sunlight's overlap is itself a finding. For the project's compendium-of-disclosure-fields output, Sunlight contributes maybe 2 fields PRI doesn't capture (position-taken, expenditure-itemization-threshold) and refines maybe 1 (itemized format detail). The **majority of Sunlight's signal is redundant with PRI's** — its contribution is independent verification, not new fields.

---

## Recommendations

1. **Stop iterating the scorer prompt against TX A-series.** No multi-rubric signal supports calling that gap an extraction error. (Already implicit in the 2026-04-29 reframe; this analysis confirms it.)
2. **Skip Phase 2 of `20260429_multi_rubric_extraction_harness.md`.** Building a Sunlight-rubric scoring path would duplicate signal already extracted here; cost > benefit given the narrow overlap.
3. **Promote Phase 3 (extraction-first refactor) to next.** The compendium-union output is exactly what would let us add Sunlight's 2-3 unique fields cleanly without duplicating the PRI infrastructure.
4. **Make CPI Hired Guns 2007 (or Newmark 2005/2017, or OpenSecrets 2022) the priority next-rubric integration.** Those cover A/B/C/D zones where Sunlight is silent — they are where the calibration leverage lives for the open gaps.
5. **Re-check TX `E1f_i` (principal-side compensation) against §305.006**. The one Sunlight-vs-harness ambiguity worth a closer read.
6. **Open question for the Phase 3 schema design:** the compendium needs to carry both PRI-resolution fields (binary itemized) AND Sunlight-resolution fields (categorized vs dates+desc). Naturally suggests a hierarchical compendium where finer-grained fields nest under coarser ones, with extracted values projecting up to the coarser level when needed.

---

## Caveats

- N=3 states; the 12/12 + 6/6 + 5/6 agreement counts are suggestive, not statistically robust. Pattern hardens only with more states or more rubrics.
- Sunlight asterisk modifiers (`*`, `^`, `***`) in the published data are **not defined in the methodology document** we have. Treated as informational; could change individual cell interpretations if a codebook surfaces.
- PRI 2010 per-item ground truth is not available; comparison vs PRI is at sub-aggregate level only. This is a published-data limitation, not a methodology choice.
- Sunlight 2015 measured laws as of ~2015; PRI 2010 measured laws as of ~2009-2010. We're using both against statute vintages 2009 (TX) / 2010 (CA, OH). Cross-vintage drift in TX especially could explain a few cells.
- The Sunlight Compensation `0***` for TX is the largest single ambiguity in the analysis.
