# Opheim 1991 — projection mapping

**Plan:** [`../../plans/20260507_atomic_items_and_projections.md`](../../plans/20260507_atomic_items_and_projections.md) Phase B (sixth rubric to ship, after CPI 2015 C11, PRI 2010, Sunlight 2015, Newmark 2017, and Newmark 2005; OpenSecrets 2022 was tabled 2026-05-13).
**Handoff (most recent):** [`../../plans/_handoffs/20260511_phase_b_continued_remaining_7.md`](../../plans/_handoffs/20260511_phase_b_continued_remaining_7.md). Watchpoints for Opheim are in the per-rubric section there.
**Prior handoff:** [`../../plans/_handoffs/20260507_phase_b_handoff.md`](../../plans/_handoffs/20260507_phase_b_handoff.md).
**Atomic items source:** [`../items_Opheim.tsv`](../items_Opheim.tsv) (26 rows total: 22 atomic items + 3 sub-aggregate composites + 1 index composite; **the 7 `enforce.*` items are OUT of scope** per the disclosure-only Phase B qualifier).
**Atomic items audit:** [`../items_Opheim.md`](../items_Opheim.md) — documents the atomization judgment calls (3-way split of the "compensation, expenditure, time" sentence; fines-vs-penalties separation; catch-all under-definition).
**Predecessor mappings (for conventions):** [`cpi_2015_c11_projection_mapping.md`](cpi_2015_c11_projection_mapping.md), [`pri_2010_projection_mapping.md`](pri_2010_projection_mapping.md), [`sunlight_2015_projection_mapping.md`](sunlight_2015_projection_mapping.md), [`newmark_2017_projection_mapping.md`](newmark_2017_projection_mapping.md), [`newmark_2005_projection_mapping.md`](newmark_2005_projection_mapping.md).

---

## Doc conventions

All five conventions from the predecessor mappings apply verbatim:

- Compendium row IDs are working names, not cluster-derived.
- Typed cells live on `MatrixCell.value` (v2.0 schema bump assumed).
- Granularity bias: split on every distinguishing case.
- Axis is `legal_availability` for de jure observables; Opheim reads no de facto observables (no `practical_availability` rows).
- **"Collect once, map to many."** Each row entry carries a `[cross-rubric: …]` annotation listing every other rubric that reads the same observable. Opheim is the sixth Phase B mapping, so most annotated readers are well-established by now.

**Opheim is the EARLIEST contributing rubric (1988–89 vintage, published 1991) and the explicit predecessor to Newmark 2005.** Newmark 2005 cites it directly ("Similar to Opheim's (1991) measure" — Newmark 2005 paper line 117). The 15 in-scope items have **substantial structural overlap with Newmark 2005**: 14 of 15 in-scope items reuse rows the Newmark mappings already touched. Opheim's contribution to compendium 2.0 is **temporal-depth validation** — the 1988–89 panel is the earliest cross-rubric ground truth in the contributing set, predating Newmark 2005's first panel (1990–91) by 1–2 years. Not novel observables.

**Net reuse rate: 14/14 distinct row families = 100% of in-scope rows reused. Zero new rows introduced.** Same headline as Newmark 2005 (which makes intuitive sense — Opheim is structurally where Newmark 2005's items came from). The one Opheim disclosure item that is NOT scorable (`disclosure.other_influence_peddling_or_conflict_of_interest`) reads no specific compendium cell because Opheim's operational definition for it is fully implicit; see §"What Opheim doesn't ask that other rubrics will" for the projection-of-undefined treatment.

## Watchpoint resolutions (per [handoff](../../plans/_handoffs/20260511_phase_b_continued_remaining_7.md) Opheim section)

1. **Watchpoint 1 — β AND-projection on `disclosure.legislation_supported_or_opposed`: APPLIED.** Opheim's source item bundles bill-identifier AND position into one binary ("legislation approved or opposed by the lobbyist" — Opheim paper line 130–131). Projection reads two compendium cells AND'd: `lobbyist_spending_report_includes_bill_or_action_identifier AND lobbyist_spending_report_includes_position_on_bill`. Both rows pre-exist from the Sunlight mapping's α form-type split. The TSV source is not edited; the conjunction lives in the projection. See `disclosure.legislation_supported_or_opposed` entry below for full mapping.

2. **Watchpoint 2 — `def_actor_class_*` row family now 3-rubric-confirmed.** Opheim's `def.elective_officials` and `def.public_employees` are the third readers of `def_actor_class_elected_officials` and `def_actor_class_public_employees` (after Newmark 2017 and Newmark 2005). **Per the handoff's explicit guidance** ("**Open Issue 1 from the Newmark 2017 mapping should be pulled forward to compendium 2.0 freeze planning** rather than indefinitely deferred — three rubrics reading the same row family is high enough confidence to lock its design"), Open Issue 1 should now be pulled forward. The PRI A-family no-overlap finding (Newmark 2005 Watchpoint 1) stands: PRI A1–A11 are structural-actor / institutional-entity observables (the Governor's office as an institution registering when it lobbies); `def_actor_class_*` is the individual-actor classification (an individual elected official, personally lobbying, falling under the lobbyist definition). Three distinct row families: CPI `def_target_*`, PRI `actor_*`, Newmark/Opheim `def_actor_class_*`. The `def_actor_class_*` family is no longer "fragile" — it's load-bearing in 3 rubric mappings.

3. **Watchpoint 3 — `disclosure.frequency` reads PRI E1h/E2h cadence at finer binary cut: CONFIRMED.** Opheim paper lines 115–118 (verbatim): "States which require reports to be filed monthly during the session or both in and out of session were coded 1, while states which require reports quarterly, semi-annually, or annually were coded 0." Opheim's binary cut is **monthly-only** (lobbyist monthly OR principal monthly). This is FINER than Newmark 2005's cut ("more frequently than annual" — quarterly/triannual/semi-annual/monthly all → 1). Same underlying compendium row family (PRI E1h_*/E2h_* — 8 binary cells); different binary projection per rubric. Tri-annual is omitted from Opheim's prose ("quarterly, semi-annually, or annually were coded 0" doesn't include tri-annual); interpreted strictly = tri-annual → 0 (less frequent than monthly). See `disclosure.frequency` entry below for the 2-cell OR-projection.

4. **Watchpoint 4 — `contributions_from_others` parallel in Opheim's 7-item info-category battery: NO DIRECT PARALLEL.** Walked. Opheim's 7 disclosure categories are: (1) total spending, (2) spending by category, (3) expenditures benefiting public employees including gifts, (4) legislation approved or opposed, (5) sources of income, (6) total income, (7) other influence peddling or conflict of interest. Categories (5) and (6) — "sources of income" and "total income" — structurally parallel Newmark's "compensation broken down by employer" + "total compensation" pair, NOT third-party contributions earmarked for lobbying. The catch-all (7) "other activities that might constitute influence peddling or conflict of interest" is operationally undefined (per `items_Opheim.md` §7: "the single most under-defined item in the index") and could plausibly cover third-party-contributions disclosure, but the under-definition prevents a deterministic projection. **Result: Newmark 2017's `lobbyist_or_principal_report_includes_contributions_received_for_lobbying` row remains single-rubric in the current contributing set** (CPI, PRI, Sunlight, Newmark 2005, Opheim — none confirmed parallel). Remaining checks: HG 2007, FOCAL 2024, LobbyView.

## Scope qualifier — 7 items OUT

Per the plan's disclosure-only Phase B qualifier, **all 7 `enforce.*` items are excluded from this projection** without further analysis:

| Excluded item | Why excluded |
|---|---|
| `enforce.thoroughness_of_reviews` | Enforcement-side. Reviews of filed reports by oversight agency — not a disclosure requirement on lobbyists. |
| `enforce.subpoena_witnesses` | Enforcement-side. Agency prosecutorial authority. |
| `enforce.subpoena_records` | Enforcement-side. Agency prosecutorial authority. |
| `enforce.conduct_administrative_hearings` | Enforcement-side. Agency prosecutorial authority. |
| `enforce.impose_administrative_fines` | Enforcement-side. Agency prosecutorial authority. |
| `enforce.impose_administrative_penalties` | Enforcement-side. Agency prosecutorial authority. |
| `enforce.file_independent_court_actions` | Enforcement-side. Agency prosecutorial authority. |

These items re-enter scope in a later round (per `STATUS.md` Current Focus: "Once disclosure-side prototype is solid, expand to prohibitions / enforcement / personnel / itemization-granularity"). Seven items × 47 states × 1 vintage (1988–89) = up to 329 ground-truth cells parked for later, not lost.

**Implication for index reproducibility:** With all 7 `enforce.*` items excluded — plus the catch-all `disclosure.other_influence_peddling_or_conflict_of_interest` item not projectable — this projection **cannot reproduce `index.total`** (Opheim's headline 0–22 score, published per state in Table 1). Opheim publishes per-state index totals only; no sub-aggregate breakdown is published. This makes Opheim's Phase C validation utility **as structurally weak as Newmark 2005's** — only a weak inequality check is available (see §"Phase C validation").

## Aggregation rule

Opheim's published structure (paper lines 89–94 + line 151):

- `index.total = def.section_total + disclosure.section_total + enforce.section_total` (0–22; unweighted sub-aggregate sum)
- Section maxima: definitions = 7, disclosure = 8, enforcement = 7
- Each section's contribution is the unweighted sum of its atomic items
- Each atomic item: 1 if the state's CSG Blue Book–coded statute includes the provision, 0 otherwise (per `items_Opheim.tsv` `scoring_rule` columns: paper line 109–111 for definitions, line 117–118 for frequency, line 132–134 for disclosure categories, line 141–142 for thoroughness, line 149–150 for prosecutorial authority)
- Two items have collapsed-from-finer-granularity coding (`disclosure.frequency` and `enforce.thoroughness_of_reviews` — Opheim explicitly notes "some finer distinction is lost in the simple 0/1 coding procedure" at paper line 152–154)

Phase C `project_opheim_1991_disclosure_side(state, 1988_89)` produces:

```
def.section_total_partial             = sum of 7 def.* atomic projections    ∈ [0, 7]
disclosure.section_total_partial      = sum of 7 in-scope disclosure projections (1 freq + 6 categories; catch-all excluded)  ∈ [0, 7]
```

The 7 `enforce.*` items and the catch-all `disclosure.other_influence_peddling_or_conflict_of_interest` item are **not produced** (treated as `unable_to_evaluate`, not as 0). Maximum reproducible partial = 7 + 7 = **14/22**.

**Convention note** (matches Newmark 2005 §"Per-state per-indicator data" treatment): items we cannot project are excluded from the partial rather than zeroed. The weak inequality `our_projected_partial ≤ paper_total` is the available Phase C check; it does not require us to assume excluded items are 0.

## Per-state per-indicator data

**Opheim publishes per-state TOTAL scores only.** Table 1 (paper line 174 caption, with the 47-state ranking running through ~line 200) publishes `index.total` for each of 47 states for the 1988–89 vintage. **Sub-aggregate totals are NOT published per state**, and **per-atomic-item per-state data is NOT published either.** This is the same published-data shape as Newmark 2005's Table 1 — weaker than Newmark 2017's Table 2.

**Sample exclusions:** Montana, South Dakota, and Virginia have no Opheim score (paper line 176 Table 1 caption: "Data for Montana, South Dakota, and Virginia were unavailable"). 47 of 50 states have ground-truth values.

**Practical consequence for Phase C:**

- Per-atomic-item validation against Opheim's published data is impossible (only totals are published).
- Per-section-total validation is also impossible (sub-aggregates not published).
- The only Opheim-direct Phase C check is: `our_projected_partial ≤ paper_total` — a weak inequality, since `enforce.section_total + catch_all ∈ [0, 8]` is unknown but non-negative.
- **Cross-rubric validation remains the actual quality check.** Opheim's BoS-sourced atomic items are correct-by-construction when the same cells are validated against PRI 2010 per-state per-item data (`docs/historical/pri-2026-rescore/`), CPI 2015 C11 per-state data (`results/cpi_2015_c11_per_state_scores.csv`), Newmark 2017 sub-aggregates, and Sunlight 2015 per-item data.

**Distribution context** (from paper Table 1 caption, line 174):

| Vintage | `index.total` range (observed) | Notes |
|---|---|---|
| 1988–89 | 0 – 18 | "0 - weakest / 18 - strongest"; max possible is 22; no state reaches 19, 20, 21, or 22. |

The observed ceiling of 18 against a possible 22 suggests every state has at least 4 enforcement / catch-all items it doesn't satisfy, OR equivalent gaps elsewhere — not interpretable without sub-aggregate breakdown.

## Phase C validation

47 states × **1 vintage (1988–89)** = 47 per-state `index.total` ground-truth values. Of these:

- **0 are usable for sub-aggregate tolerance check** (paper doesn't publish sub-aggregates).
- **0 are usable for per-atomic-item check** (paper doesn't publish per-item per-state data).
- **47 are usable for the weak inequality check** (`our_projected_partial ≤ paper_total` always must hold).
- **47 become usable for full tolerance check IF the 7 deferred `enforce.*` items + the catch-all are extracted** in a later round (and the catch-all then admits a deterministic projection).

This is a meaningful regression in Phase C utility relative to Newmark 2017 (which contributes 100 sub-aggregate cells of full-tolerance ground truth). Opheim's contribution is **temporal-depth validation** — the 1988–89 vintage is the earliest cross-rubric ground truth available, predating Newmark 2005's earliest panel (1990–91) by 1–2 years. Combined with Newmark 2005's six panels (1990–91 through 2003) and Newmark 2017's 2015 vintage, the contributing-rubric set covers ~28 years of BoS-derived observables.

Federal LDA out of scope (Opheim is state-only, 1988–89, predating LDA's 1995 enactment).

---

## Structural delta from Newmark 2005

Newmark 2005 explicitly cites Opheim ("Similar to Opheim's (1991) measure" — Newmark 2005 paper line 117) and inherits much of Opheim's item set. Newmark 2005 then makes 4 additions and 3 omissions vs Opheim:

| Concept | Opheim 1991 | Newmark 2005 | Net effect on row family |
|---|---|---|---|
| Definition section size | 7 items (legislative, administrative, elective officials, public employees, comp std, exp std, time std) | 7 items (verbatim same set) | Identical. Newmark 2005 atomizes the same way. |
| Disclosure frequency | **1 item, finer binary cut** (monthly-only → 1; quarterly+/annually → 0) | **1 item, coarser binary cut** (>annual → 1; annual or less → 0) | Same compendium row family (PRI E1h/E2h cadence); different binary cuts. Opheim reads 2/8 cells; Newmark 2005 reads 8/8 cells. |
| Disclosure categories | **7 items** (total spending, spending by category, expenditures benefiting public employees, legislation supported/opposed, sources of income, total income, other influence peddling/conflict of interest) | **6 items** (subject matter, expenditures benefiting officials, compensation by employer, total compensation, categories of expenditures, total expenditures) | Newmark 2005 **drops** Opheim's "legislation supported/opposed" (replaces with broader "subject matter" item) and Opheim's catch-all "other influence peddling/conflict of interest" (drops entirely). Newmark 2005 **renames** "sources of income" → "compensation by employer" and "total income" → "total compensation." Categories battery is structurally similar but Newmark 2005 is cleaner. |
| Prohibitions | **None** (Opheim has no prohibition section) | **4 items** (campaign contrib any time, during session, expenditures over threshold, solicitation by officials) | Newmark 2005 ADDS prohibitions — Opheim's earlier framing didn't have them. (All 4 OOS for both rubrics under disclosure-only Phase B.) |
| Enforcement | **7 items** (thoroughness + 6 prosecutorial-authority sub-items) | **None** (Newmark 2005 has no enforcement section; adds the 2003-only `penalty_stringency` add-on but that's a different concept) | Opheim's 7 enforcement items are OOS for disclosure-only Phase B. Newmark 2005's `penalty_stringency_2003` is separately OOS. |

**Net for Phase B:** Opheim and Newmark 2005 read **a near-identical disclosure-side row set** at the compendium level, with two key differences:
- Opheim splits the bill-identifier/position observable (item `legislation_supported_or_opposed`, projecting via β AND on bill_id + position); Newmark 2005 reads only the coarse subject-matter row.
- Opheim's binary cadence cut is finer (monthly-only) than Newmark 2005's (>annual); they read the same row family at different granularities.

The Opheim catch-all (`other_influence_peddling_or_conflict_of_interest`) is the only Opheim disclosure item with no Newmark 2005 parallel — and is the one un-projectable item in this mapping.

---

## Per-item mappings

### Definitions battery (7 items, all in scope; all reused from Newmark 2017/2005 mappings)

Opheim's "statutory definition of a lobbyist" sub-aggregate. The seven items decompose into:
- 2 **activity-type** observables (legislative / administrative lobbying triggers registration)
- 2 **actor-class** observables (elective officials / public employees as lobbyists)
- 3 **lobbyist-status threshold** observables (compensation / expenditure / time standards)

All 7 rows pre-exist in the compendium (3 from CPI mapping, 4 from Newmark 2017 mapping).

#### opheim_1991.def.legislative_lobbying — Legislative lobbying as inclusion criterion

- **Compendium rows:** `def_target_legislative_branch` (binary; legal)
  [cross-rubric: CPI #196 (one of three target-type reads in IND_196's compound); HG Q1 (inverse-framed); FOCAL `scope.3` (legislative branches as targets); Newmark 2017 `def.legislative_lobbying`; Newmark 2005 `def_legislative_lobbying`; PRI A7 actor-side (`actor_legislative_branch_registration_required`, parallel-but-not-identical observable)]
  Already in CPI mapping; pre-existing.
- **Cell type:** binary.
- **Axis:** `legal_availability`.
- **Scoring rule:** `cell == TRUE → 1; else → 0`.
- **Source quote:** "Only two states - Arkansas and Illinois which have no statutory designation of lobbyists - fail to include 'legislative' lobbying as a criterion for definition." (Opheim 1991 paper line 103–105).
- **Note on 1988-89 vs 2015 vintage:** Opheim observes 45/47 = 96% of states scoring TRUE; Newmark 2017 paper line 518 reports "all 50 states require registration for lobbying the legislature" (100% in 2015). Slight drift toward universality over 27 years — consistent with both rubrics treating this as a near-saturation observable. (Arkansas and Illinois were the two 1988-89 exceptions; both had no statutory lobbyist designation at all per Opheim.)

#### opheim_1991.def.administrative_lobbying — Administrative lobbying as inclusion criterion

- **Compendium rows:** `def_target_executive_agency` (binary; legal)
  [cross-rubric: CPI #196 (compound second arm — "executive officials"); HG Q1; FOCAL `scope.3`; Newmark 2017 `def.administrative_agency_lobbying`; Newmark 2005 `def_administrative_agency_lobbying`]
  Already in CPI mapping; pre-existing.
- **Cell type:** binary.
- **Axis:** `legal_availability`.
- **Scoring rule:** `cell == TRUE → 1; else → 0`.
- **Source quote:** "By contrast, thirty states fail to include 'administrative' lobbying as a criterion." (Opheim 1991 paper line 105–106).
- **Note on cross-vintage drift:** 17/47 = 36% of states scored TRUE in 1988-89 per Opheim (thirty exclusions out of 47); Newmark 2017 reports administrative lobbying as a definitional component still varying across states in 2015. Multi-vintage signal across Opheim + Newmark 2005 + Newmark 2017 lets us measure exact drift rate — Phase C extraction can test temporal consistency on this row.

#### opheim_1991.def.elective_officials — Elective officials designated as lobbyists

- **Compendium rows:** `def_actor_class_elected_officials` (binary; legal)
  [cross-rubric: Newmark 2017 `def.elective_officials_as_lobbyists`; Newmark 2005 `def_elected_officials_as_lobbyists`]
  Already in Newmark 2017 mapping; pre-existing.
- **Cell type:** binary.
- **Axis:** `legal_availability`.
- **Scoring rule:** `cell == TRUE → 1; else → 0`.
- **Source quote:** "Seven states designate 'elective officials' as lobbyists" (Opheim 1991 paper line 106–107).
- **Note on row family — now 3-rubric-confirmed:** This row was introduced by the Newmark 2017 mapping as a fragile new family; Newmark 2005 confirmed it as a second reader (after the PRI A-family no-overlap check); Opheim now confirms it as the third reader. **Per the handoff, Open Issue 1 should be pulled forward to compendium 2.0 freeze planning** — 3-rubric confirmation is high enough confidence to lock the design. 7/47 = 15% of states scored TRUE in 1988-89 per Opheim (rare observable; consistent with the row being a genuine variable across statutes).

#### opheim_1991.def.public_employees — Public employees designated as lobbyists

- **Compendium rows:** `def_actor_class_public_employees` (binary; legal)
  [cross-rubric: Newmark 2017 `def.public_employees_as_lobbyists`; Newmark 2005 `def_public_employees_as_lobbyists`]
  Already in Newmark 2017 mapping; pre-existing.
- **Cell type:** binary.
- **Axis:** `legal_availability`.
- **Scoring rule:** `cell == TRUE → 1; else → 0`.
- **Source quote:** "while seven others designate 'public employees.'" (Opheim 1991 paper line 107–108).
- **Note:** Same row family as `def_actor_class_elected_officials`; same 3-rubric-confirmed status. Opheim observes 7/47 = 15% of states scoring TRUE in 1988-89.

#### opheim_1991.def.compensation_standard — Specific compensation standard

- **Compendium rows:** `compensation_threshold_for_lobbyist_registration` (typed `Optional[Decimal]`; legal)
  [cross-rubric: CPI #197 (reads the dollar value at 3-tier); HG Q2 (reads as 5-tier ordinal); FOCAL `scope.2` (combined with filing-de-minimis per handoff threshold table); Newmark 2017 `def.compensation_standard`; Newmark 2005 `def_compensation_standard`]
  Already in CPI mapping; pre-existing typed cell.
- **Cell type:** `Optional[Decimal]` representing the compensation dollar threshold above which the lobbyist-definition triggers.
- **Axis:** `legal_availability`.
- **Scoring rule:** `cell IS NOT NULL → 1; else → 0`. Opheim reads only the presence of a standard, not the value (paper line 110–111: "each coded 1 if a criterion was included in the state's definition of lobbyists and 0 if it was not").
- **Source quote:** "some states include specific compensation, expenditure, and time standards to delineate lobbying activity." (Opheim 1991 paper line 107–109).
- **Note on threshold-concept distinction:** This is the **lobbyist-status threshold** (one of five distinct threshold concepts per the handoff doc's threshold-concepts table). Not to be confused with filing-de-minimis (PRI D1), itemization-de-minimis (Sunlight #3 / HG Q15), or prohibition-threshold (Newmark 2005's OOS `prohib_expenditures_over_threshold`). Opheim's atomization explicitly splits comp/exp/time per paper line 109 + `items_Opheim.md` §4 ("Opheim says the section has 7 items, and the only way to reach 7 is by splitting these").

#### opheim_1991.def.expenditure_standard — Specific expenditure standard

- **Compendium rows:** `expenditure_threshold_for_lobbyist_registration` (typed `Optional[Decimal]`; legal)
  [cross-rubric: Newmark 2017 `def.expenditure_standard`; Newmark 2005 `def_expenditure_standard`; potential FOCAL `scope.2` partial read]
  Already in Newmark 2017 mapping; pre-existing typed cell.
- **Cell type:** `Optional[Decimal]` representing the expenditure dollar threshold above which the lobbyist-definition triggers. Distinct cell from the compensation-threshold row above.
- **Axis:** `legal_availability`.
- **Scoring rule:** `cell IS NOT NULL → 1; else → 0`.
- **Source quote:** "some states include specific compensation, expenditure, and time standards to delineate lobbying activity." (Opheim 1991 paper line 107–109).
- **Note:** Opheim enumerates this as a separate definitional component verbatim parallel to Newmark 2005 and Newmark 2017. The three-threshold-cell structure (compensation / expenditure / time) is now 3-rubric-confirmed (Newmark 2017 + Newmark 2005 + Opheim) — same status as `def_actor_class_*`.

#### opheim_1991.def.time_standard — Specific time standard

- **Compendium rows:** `time_threshold_for_lobbyist_registration` (typed `Optional[TimeThreshold]`; legal)
  [cross-rubric: Newmark 2017 `def.time_standard`; Newmark 2005 `def_time_standard`; potential FOCAL `scope.2` partial read; Federal LDA 20%-of-work-time rule]
  Already in Newmark 2017 mapping; pre-existing typed cell.
- **Cell type:** `Optional[TimeThreshold]` where `TimeThreshold = {magnitude: Decimal, unit: enum{hours_per_quarter, hours_per_year, days_per_year, percent_of_work_time, ...}}`.
- **Axis:** `legal_availability`.
- **Scoring rule:** `cell IS NOT NULL → 1; else → 0`.
- **Source quote:** "some states include specific compensation, expenditure, and time standards to delineate lobbying activity. The seven criteria for definition of lobbyists were each coded 1 if a criterion was included in the state's definition of lobbyists and 0 if it was not." (Opheim 1991 paper line 107–111).
- **Note:** Same row-family-confirmation pattern as the other two threshold cells.

### Disclosure battery (8 items: 7 in scope + 1 un-projectable catch-all)

Opheim's "frequency and quality of disclosure" sub-aggregate. The 8 items decompose into:
- 1 **cadence** observable (frequency) — projects from existing PRI cadence row family at a finer binary cut than Newmark 2005's.
- 7 **information-category** observables — 6 reuse existing rows; 1 (the catch-all) is operationally undefined and un-projectable.

#### opheim_1991.disclosure.frequency — Frequency of reporting (monthly-only-during-session-or-in-and-out → 1)

- **Compendium rows:** OR over 2 cells from the existing PRI cadence row family:
  `lobbyist_report_cadence_includes_monthly` OR
  `principal_report_cadence_includes_monthly`
  (Reads 2 of the 8 cells in the cadence family. Quarterly, tri-annual, semi-annual, annual cells → 0 in Opheim's projection.)
  [cross-rubric: PRI E2h_i (lobbyist monthly; canonical atomization) + PRI E1h_i (principal monthly; canonical atomization); Newmark 2005 `freq_reporting_more_than_annual` (reads same cadence family at a coarser cut — 8-cell OR over monthly + quarterly + triannual + semiannual); CPI #202 (`lobbyist_spending_report_filing_cadence` — enum read derived from binaries); FOCAL `timeliness.*` battery (overlap deferred to FOCAL mapping); HG Q11 (gateway: spending report required — implies a cadence exists)]
  Pre-existing row family from PRI mapping; **no new rows introduced.**
- **Cell type:** projection only — reads 2 binary cells, OR-aggregated.
- **Axis:** `legal_availability`.
- **Scoring rule:** `(lobbyist_report_cadence_includes_monthly OR principal_report_cadence_includes_monthly) → 1; else → 0`.
- **Source quote:** "Frequency of reporting was coded dichotomously to reflect the most extreme differences in frequency. States which require reports to be filed monthly during the session or both in and out of session were coded 1, while states which require reports quarterly, semi-annually, or annually were coded 0." (Opheim 1991 paper line 115–118).
- **Note on the "monthly during session" vs "monthly in-and-out-of-session" sub-distinction:** Opheim's source quote bundles two intensive-monthly variants ("monthly during the session" and "monthly in-and-out-of-session") into the same 1-bucket. PRI atomization captures "Monthly" as a single binary without distinguishing session-bounded vs always. **Projection convention:** treat any state where the monthly cadence binary is TRUE as Opheim = 1. If a state requires monthly during session only AND that's encoded in PRI's "Monthly" cell as TRUE, the projection matches Opheim's coding. If the session-bounded vs always distinction matters downstream (e.g., for a finer-cut rubric), the cell may need a v2.0 split — flag for compendium 2.0 freeze (Open Issue 1, below).
- **Note on tri-annual treatment:** Opheim's prose explicitly enumerates "quarterly, semi-annually, or annually were coded 0" but omits tri-annual (PRI E1h_iii / E2h_iii, "Tri-annually linked with legislative calendar"). Strict interpretation: tri-annual goes to 0 (less frequent than monthly). PRI tri-annual is plausibly equivalent to "monthly during a short session" in some statutes, but Opheim's binary cut treats it as the 0 side. No new compendium row needed; the projection reads only the monthly cells.
- **Note on Newmark 2005 vs Opheim cuts:** Same row family, different binary cuts. Newmark 2005 reads 8 cadence cells OR'd ("more frequent than annual"); Opheim reads 2 cadence cells OR'd ("monthly only"). A state with quarterly reporting gets Newmark 2005 = 1 / Opheim = 0. Both are correct projections of their respective rubric's published rule; the underlying row family is identical.
- **Note on registration vs reporting cadence:** Opheim's source quote conflates registration and reporting cadence into a single binary (parallel to Newmark 2005's `freq_reporting_more_than_annual` note about the same conflation). **Projection convention:** read *reporting* cadence (PRI E1h/E2h rows), not registration cadence (CPI #199 `lobbyist_registration_renewal_cadence`). Rationale: Opheim's broader category is "frequency and quality of disclosure" — reporting framing dominates. Same convention as Newmark 2005.

#### opheim_1991.disclosure.total_spending — Lobbyist's total spending

- **Compendium rows:** `lobbyist_spending_report_includes_total_expenditures` (binary; legal)
  [cross-rubric: Newmark 2017 `disclosure.total_expenditures`; Newmark 2005 `disc_total_expenditures`; HG Q11 (gateway: spending report required); HG Q36 (state agency provides overall lobbying spending total — different observable, public-access side); CPI #201 (compound — total spending implicit in "detailed spending reports"); Sunlight #2 tier 0+ (implicit)]
  Already in Newmark 2017 mapping; pre-existing.
- **Cell type:** binary.
- **Axis:** `legal_availability`.
- **Scoring rule:** `cell == TRUE → 1; else → 0`.
- **Source quote:** "Information disclosed in these reports includes the lobbyist's total spending" (Opheim 1991 paper line 119;128–129).
- **Note:** Verbatim parallel to Newmark 2017 `disclosure.total_expenditures` and Newmark 2005 `disc_total_expenditures`. Reuses the row Newmark 2017 mapping introduced. This row is now 3-rubric-confirmed (Newmark 2017 + Newmark 2005 + Opheim).

#### opheim_1991.disclosure.spending_by_category — Spending by category

- **Compendium rows:** `lobbyist_spending_report_categorizes_expenses_by_type` (binary; legal)
  [cross-rubric: Sunlight #2 categorized-tier; Newmark 2017 `disclosure.categories_of_expenditures`; Newmark 2005 `disc_categories_of_expenditures`; HG Q14 ("summaries (totals) of spending classified by category types — gifts, entertainment, postage"); FOCAL `financials.*` battery (FOCAL atomizes the categories themselves)]
  Already in Sunlight mapping; pre-existing.
- **Cell type:** binary.
- **Axis:** `legal_availability`.
- **Scoring rule:** `cell == TRUE → 1; else → 0`.
- **Source quote:** "spending by category" (Opheim 1991 paper line 129–130).
- **Note:** Opheim doesn't enumerate the categories (per `items_Opheim.md` row 13 note). Same row as Newmark 2017/2005 and Sunlight #2; the row design is binary "categorized or not" — finer category-level granularity (e.g., the gift/entertainment/postage split FOCAL captures) is downstream of this row, in separate per-category cells.

#### opheim_1991.disclosure.expenditures_benefitting_public_employees — Expenditures benefitting public employees, including gifts

- **Compendium rows:** `lobbyist_report_includes_gifts_entertainment_transport_lodging` (binary; legal) AND/OR `principal_report_includes_gifts_entertainment_transport_lodging` (binary; legal)
  [cross-rubric: PRI E1f_iii (principal-side); PRI E2f_iii (lobbyist-side); Newmark 2017 `disclosure.expenditures_benefiting_officials`; Newmark 2005 `disc_expenditures_benefiting_officials`; FOCAL `financials.10` (verbatim parallel); HG Q14 / Q17 / Q23 (partial reads at finer gift granularity)]
  Already in PRI mapping; pre-existing pair of rows.
- **Cell type:** binary per row.
- **Axis:** `legal_availability`.
- **Scoring rule:** `(lobbyist_report_includes_gifts_entertainment_transport_lodging OR principal_report_includes_gifts_entertainment_transport_lodging) → 1; else → 0`. Opheim's framing is actor-agnostic; OR over the two actor-side rows is the coarsest correct reading. Same projection convention as Newmark 2017's `disclosure.expenditures_benefiting_officials` and Newmark 2005's `disc_expenditures_benefiting_officials`.
- **Source quote:** "expenditures benefitting public employees including gifts" (Opheim 1991 paper line 130). Note: Opheim's "benefitting" (double t) and "public employees" (vs Newmark's "public officials or employees") preserved verbatim.
- **Note on "including gifts" framing:** `items_Opheim.md` §4 explicitly notes "the 'including gifts' appears to be a clarifying clause within one disclosure category in the source data, and Opheim uses singular grammar." Kept as one item rather than split; HG Q23's finer gift granularity remains a separate compendium-2.0 freeze question (per Newmark 2017 mapping note).

#### opheim_1991.disclosure.legislation_supported_or_opposed — Legislation approved or opposed by the lobbyist (β AND-projection)

- **Compendium rows:** `lobbyist_spending_report_includes_bill_or_action_identifier` (binary; legal) AND `lobbyist_spending_report_includes_position_on_bill` (binary; legal)
  [cross-rubric, bill_id row: HG Q20 bill-tier (3-pt tier in a 3-tier categorical); FOCAL `contact_log.11` ("bill numbers/measures"); PRI E2g_ii ("specific bill number or legislation ID"); Sunlight #1 tier 1+ (bill/action discussed)]
  [cross-rubric, position row: FOCAL `contact_log.10` ("Outcomes sought (eg, legislation/policies supported/opposed)"); Sunlight #1 tier 2 (position taken)]
  Both rows already in Sunlight mapping (introduced via the α form-type split); pre-existing.
- **Cell type:** projection only — reads 2 binary cells, AND-aggregated.
- **Axis:** `legal_availability`.
- **Scoring rule:** `(bill_or_action_identifier == TRUE) AND (position_on_bill == TRUE) → 1; else → 0`.
- **Source quote:** "legislation approved or opposed by the lobbyist" (Opheim 1991 paper line 130–131). Note: Opheim's source phrase bundles bill-identifier ("legislation") AND position ("approved or opposed") into a single binary.
- **Note on β convention (locked 2026-05-11 Sunlight session):** Opheim's TSV is not edited — the conjunction lives in the projection, not in the source. Same convention as documented in the Sunlight mapping doc and the handoff. This is the second confirmed application of β after Sunlight's locked decision; the projection AND-projection pattern is now exemplified, not just hypothesized.
- **Note on coarser-rubric reuse:** Newmark 2017 / Newmark 2005's `disclosure.influence_legislation_or_admin` (or `disc_legislative_admin_action_to_influence` in 2005) reads the COARSER `lobbyist_spending_report_includes_general_subject_matter` row, NOT the bill_id+position bundle. Opheim is the only contributing rubric (in current set, besides Sunlight #1 tier 2) that reads BOTH bill_id AND position at the strict level. Confirms the granularity-bias α split is paying off — Opheim's 1-binary observable maps cleanly to two compendium cells via AND.
- **Note on registration form vs spending report side:** Opheim doesn't disambiguate which form the disclosure happens on. Per the convention in Newmark 2017's mapping (and the prior Sunlight session), Opheim's "disclosure" frame is post-registration; reads only the spending-report-side bill_id and position rows. If a state requires bill_id + position on the reg form but not the spending report, Opheim would code 0 (since the actual ongoing-disclosure requirement isn't met). Verifiable cross-state if needed; treat as Phase C edge case.

#### opheim_1991.disclosure.sources_of_income — Sources of income

- **Compendium rows:** `lobbyist_spending_report_includes_compensation_broken_down_by_client` (binary; legal)
  [cross-rubric: Sunlight #5 (the broken-down-by-client row); Newmark 2017 `disclosure.compensation_by_employer`; Newmark 2005 `disc_compensation_by_employer`; HG Q13 footnote ("Full points if information is on registration form instead") at coarser granularity; CPI #201 (compound — compensation-included is one of three reads)]
  Already in Sunlight mapping; pre-existing.
- **Cell type:** binary.
- **Axis:** `legal_availability`.
- **Scoring rule:** `cell == TRUE → 1; else → 0`.
- **Source quote:** "sources of income" (Opheim 1991 paper line 131).
- **Note on the "sources of income" → compensation-broken-down-by-client mapping:** Opheim is BoS-defined (the CSG Blue Book 1988-89 table is the operational source; Opheim doesn't elaborate). The structural parallel with Opheim's adjacent `disclosure.total_income` item — i.e., "sources of income" + "total income" — mirrors Newmark 2005/2017's `disc_compensation_by_employer` + `disc_total_compensation` pair. The conservative reading: "sources of income" means lobbyist compensation broken down by paying entity (client/employer/principal), parallel to Newmark's framing. Alternative reading (rejected as less likely): "sources of income" could include third-party contributions earmarked for lobbying (parallel to Newmark 2017's `disc.contributions_from_others`), but a 1988-89 BoS table is unlikely to have framed it this way — third-party-contributions disclosure is a more modern reform concern. **Watchpoint 4 resolved against this alternative reading:** Newmark 2017's `lobbyist_or_principal_report_includes_contributions_received_for_lobbying` row remains single-rubric.
- **Note on "employer" vs "client" vs "source" naming:** Opheim's "source" wording is yet a third synonym alongside Sunlight's "client" and Newmark's "employer." Same observable: which *paying entity* the lobbyist's compensation is itemized against. Open Issue 2 from Newmark 2017 mapping carries forward — compendium 2.0 should rename to a neutral phrasing like `_by_paying_entity` or `_by_source_of_funding`.

#### opheim_1991.disclosure.total_income — Total income

- **Compendium rows:** `lobbyist_spending_report_includes_total_compensation` (binary; legal)
  [cross-rubric: Sunlight #5 (total-compensation-on-spending-report row); Newmark 2017 `disclosure.total_compensation`; Newmark 2005 `disc_total_compensation`; HG Q13 (binary lobbyist-side compensation on spending report); HG Q27 (mirror on principal/employer side — distinct cell, parallel); CPI #201 (compound); PRI E2f_i ("Direct lobbying costs (compensation)")]
  Already in Sunlight mapping; pre-existing.
- **Cell type:** binary.
- **Axis:** `legal_availability`.
- **Scoring rule:** `cell == TRUE → 1; else → 0`.
- **Source quote:** "total income" (Opheim 1991 paper line 131–132).
- **Note:** Same row as Newmark 2017's `disclosure.total_compensation` and Newmark 2005's `disc_total_compensation`. The row is now 3-rubric-confirmed (Newmark 2017 + Newmark 2005 + Opheim + Sunlight #5 = 4-rubric-confirmed counting Sunlight; one of the most-validated rows in compendium 2.0).

#### opheim_1991.disclosure.other_influence_peddling_or_conflict_of_interest — Other activities (catch-all; UN-PROJECTABLE)

- **Compendium rows:** **None — operationally undefined.**
  [cross-rubric: no clean parallel in any other contributing rubric; the closest concept-adjacent rows are `lobbyist_or_principal_report_includes_contributions_received_for_lobbying` (Newmark 2017-distinctive) and assorted gift / contribution sub-cells, but none deterministically maps.]
- **Cell type:** n/a — no row read.
- **Axis:** n/a.
- **Scoring rule:** `unable_to_evaluate`. The item is excluded from the projected partial (not zeroed).
- **Source quote:** "other activities that might constitute influence peddling or conflict of interest" (Opheim 1991 paper line 132–133).
- **Note on un-projectability:** Per `items_Opheim.md` §7 ("the single most under-defined item in the index") and §4 ("Catch-all category - operational definition fully implicit; Opheim does not enumerate what activities qualify"), Opheim's catch-all has no operational definition in the paper. The underlying CSG Blue Book 1988-89 source table presumably had a column titled something like "other," and Opheim coded 1/0 based on whatever the BoS coders had marked. Without the BoS source, we cannot determine which compendium cell(s) to read. **Honest projection: this item is excluded from the partial.** When the deferred enforce.* round adds the 7 OOS enforcement items, the catch-all should be revisited with a richer compendium row set (post-Phase B compendium 2.0); it may then admit a multi-cell OR projection capturing several "influence peddling" observables, or it may stay un-projectable.
- **Note on what we DON'T do:** We do NOT default to 0, do NOT collapse to the contributions row (the most concept-adjacent candidate), and do NOT make up a row. The honest reading is: 1 of Opheim's 8 disclosure items has no deterministic projection through the current compendium row set. Phase C tooling should treat this as `unable_to_evaluate`, same convention as other un-extractable observables.

### Enforcement battery (7 items, ALL OUT of scope)

Opheim's "oversight and enforcement of regulations" sub-aggregate. All 7 items are agency authority observables, not disclosure requirements. Excluded per the disclosure-only Phase B qualifier.

| Excluded item | Source quote (Opheim) | Re-entry scope |
|---|---|---|
| `enforce.thoroughness_of_reviews` | "the thoroughness of reviews was coded (1 for review of all reports, 0 for less extensive review)" (line 140–142) | Enforcement round (deferred). Categorical-collapsed-to-binary per Opheim's note at line 152–154; finer granularity available in CSG source. |
| `enforce.subpoena_witnesses` | "whether the agency may subpoena witnesses" (line 146–147) | Enforcement round (deferred). |
| `enforce.subpoena_records` | "subpoena records" (line 147) | Enforcement round (deferred). |
| `enforce.conduct_administrative_hearings` | "conduct administrative hearings" (line 147–148) | Enforcement round (deferred). |
| `enforce.impose_administrative_fines` | "impose administrative fines" (line 148) | Enforcement round (deferred). Distinct from `enforce.impose_administrative_penalties` per Opheim's enumeration (paper line 148) — distinction unexplained, flagged in `items_Opheim.tsv` notes. |
| `enforce.impose_administrative_penalties` | "impose administrative penalties" (line 148) | Enforcement round (deferred). |
| `enforce.file_independent_court_actions` | "file independent court actions" (line 148–149) | Enforcement round (deferred). |

These 7 items × 47 states × 1 vintage (1988–89) = up to 329 ground-truth cells parked for later, not lost.

---

## Summary of compendium rows touched

| Row id (working name) | Cell type | Axis | Opheim items reading | Cross-rubric readers (dedupe candidates) | Status |
|---|---|---|---|---|---|
| `def_target_legislative_branch` | binary | legal | `def.legislative_lobbying` | CPI #196, HG Q1, FOCAL scope.3, Newmark 2017, Newmark 2005, PRI A7 (actor-side parallel) | existing (CPI mapping) |
| `def_target_executive_agency` | binary | legal | `def.administrative_lobbying` | CPI #196, HG Q1, FOCAL scope.3, Newmark 2017, Newmark 2005 | existing (CPI mapping) |
| `def_actor_class_elected_officials` | binary | legal | `def.elective_officials` | Newmark 2017, Newmark 2005 (3-rubric-confirmed with Opheim) | existing (Newmark 2017 mapping) |
| `def_actor_class_public_employees` | binary | legal | `def.public_employees` | Newmark 2017, Newmark 2005 (3-rubric-confirmed with Opheim) | existing (Newmark 2017 mapping) |
| `compensation_threshold_for_lobbyist_registration` | typed `Optional[Decimal]` | legal | `def.compensation_standard` (via `IS NOT NULL`) | CPI #197, HG Q2, FOCAL scope.2, Newmark 2017, Newmark 2005 | existing (CPI mapping) |
| `expenditure_threshold_for_lobbyist_registration` | typed `Optional[Decimal]` | legal | `def.expenditure_standard` (via `IS NOT NULL`) | Newmark 2017, Newmark 2005, FOCAL scope.2 (partial) (3-rubric-confirmed with Opheim) | existing (Newmark 2017 mapping) |
| `time_threshold_for_lobbyist_registration` | typed `Optional[TimeThreshold]` | legal | `def.time_standard` (via `IS NOT NULL`) | Newmark 2017, Newmark 2005, FOCAL scope.2 (partial), Federal LDA 20% rule (3-rubric-confirmed with Opheim) | existing (Newmark 2017 mapping) |
| `lobbyist_report_cadence_includes_monthly` + `principal_report_cadence_includes_monthly` (2 cells, OR-projection; subset of the 8-cell PRI cadence family) | binary × 2 | legal | `disclosure.frequency` (via OR over 2 cells; monthly-only cut) | PRI E1h_i + E2h_i (canonical atomization); Newmark 2005 `freq_reporting_more_than_annual` reads the same family at coarser cut; CPI #202 (enum-derived); FOCAL `timeliness.*`; HG Q11 (gateway) | existing (PRI mapping) |
| `lobbyist_spending_report_includes_total_expenditures` | binary | legal | `disclosure.total_spending` | Newmark 2017, Newmark 2005, HG Q11 (gateway), CPI #201 (compound) (3-rubric-confirmed with Opheim) | existing (Newmark 2017 mapping) |
| `lobbyist_spending_report_categorizes_expenses_by_type` | binary | legal | `disclosure.spending_by_category` | Sunlight #2, HG Q14, Newmark 2017, Newmark 2005, FOCAL financials.* | existing (Sunlight mapping) |
| `lobbyist_report_includes_gifts_entertainment_transport_lodging` | binary | legal | `disclosure.expenditures_benefitting_public_employees` (via OR with principal-side) | PRI E2f_iii, FOCAL financials.10, Newmark 2017, Newmark 2005 | existing (PRI mapping) |
| `principal_report_includes_gifts_entertainment_transport_lodging` | binary | legal | `disclosure.expenditures_benefitting_public_employees` (via OR with lobbyist-side) | PRI E1f_iii, FOCAL financials.10 (combined), Newmark 2017, Newmark 2005 | existing (PRI mapping) |
| `lobbyist_spending_report_includes_bill_or_action_identifier` | binary | legal | `disclosure.legislation_supported_or_opposed` (via β AND with position) | Sunlight #1, HG Q20 bill-tier, FOCAL contact_log.11, PRI E2g_ii | existing (Sunlight mapping) |
| `lobbyist_spending_report_includes_position_on_bill` | binary | legal | `disclosure.legislation_supported_or_opposed` (via β AND with bill_id) | Sunlight #1 tier 2, FOCAL contact_log.10 | existing (Sunlight mapping) |
| `lobbyist_spending_report_includes_compensation_broken_down_by_client` | binary | legal | `disclosure.sources_of_income` | Sunlight #5, Newmark 2017, Newmark 2005, HG Q13 footnote, CPI #201 | existing (Sunlight mapping) |
| `lobbyist_spending_report_includes_total_compensation` | binary | legal | `disclosure.total_income` | Sunlight #5, Newmark 2017, Newmark 2005, HG Q13, CPI #201, PRI E2f_i (4-rubric-confirmed with Opheim) | existing (Sunlight mapping) |

**14 distinct compendium row families touched by 14 of 15 in-scope Opheim atomic items** (the 15th in-scope item, `disclosure.other_influence_peddling_or_conflict_of_interest`, is un-projectable; counting it as 0 rows touched). **All 14 row families are pre-existing**: 4 from the CPI mapping, 4 from the Sunlight mapping, 2 from the PRI mapping (gifts/entertainment principal-and-lobbyist pair), 1 from the PRI mapping (cadence family — 2 cells read of the 8-cell family), 3 from the Newmark 2017 mapping (the two `def_actor_class_*` rows + `expenditure_threshold_*` + `time_threshold_*` + `lobbyist_spending_report_includes_total_expenditures`; net 3 distinct row IDs after de-duping against CPI).

**Bill_id + position pair** (`lobbyist_spending_report_includes_bill_or_action_identifier`, `lobbyist_spending_report_includes_position_on_bill`) come from the Sunlight mapping's α form-type split. The β AND-projection on these two cells is the second exemplification of β after the Sunlight mapping locked the convention.

Reuse rate: **14/14 row families = 100%.** Same headline as Newmark 2005. Consistent with Opheim being the explicit predecessor of Newmark 2005 (whose paper line 117 cites Opheim verbatim).

Items per row-family promotion-status update (after this mapping):
- `def_actor_class_elected_officials`, `def_actor_class_public_employees` → **3-rubric-confirmed** (Newmark 2017 + Newmark 2005 + Opheim). **Open Issue 1 should be resolved at compendium 2.0 freeze**, not deferred.
- `expenditure_threshold_for_lobbyist_registration`, `time_threshold_for_lobbyist_registration` → **3-rubric-confirmed** (Newmark 2017 + Newmark 2005 + Opheim).
- `lobbyist_spending_report_includes_total_expenditures` → **3-rubric-confirmed** (Newmark 2017 + Newmark 2005 + Opheim).
- `lobbyist_spending_report_includes_total_compensation` → **4-rubric-confirmed** (Sunlight + Newmark 2017 + Newmark 2005 + Opheim).
- `lobbyist_spending_report_includes_compensation_broken_down_by_client` → **4-rubric-confirmed** (Sunlight + Newmark 2017 + Newmark 2005 + Opheim).
- `lobbyist_report_includes_gifts_entertainment_transport_lodging` / `principal_report_includes_gifts_entertainment_transport_lodging` → **3-rubric-confirmed** on PRI principal/lobbyist split (PRI + Newmark 2017 + Newmark 2005 + Opheim — actually 4-rubric-confirmed; plus FOCAL `financials.10` as a 5th reader at combined granularity).

---

## Corrections to predecessor mappings

### Correction 1 — Newmark 2017 mapping speculation on Open Issue 1 row family

The Newmark 2017 mapping documented Open Issue 1 ("`def_actor_class_*` row family — separate from `def_target_*` or merged into `actor_*`?") as deferred to compendium 2.0 freeze with the caveat:

> "PRI A-family content not directly walked this session — Newmark 2005 mapping or PRI re-walk should confirm whether `def_actor_class_*` overlaps PRI A6 or similar."

Newmark 2005 mapping walked the PRI A-family check (Watchpoint 1) and confirmed no overlap. Opheim adds the third reader. **The row family is no longer fragile; it's load-bearing in 3 rubric mappings.** Open Issue 1 should be resolved at compendium 2.0 freeze planning — explicitly elevate `def_actor_class_*` from "fragile candidate row family" to "locked row family with 3-rubric validation" status. The handoff's explicit guidance ("three rubrics reading the same row family is high enough confidence to lock its design") is now operative.

### Correction 2 — Newmark 2005 mapping watchpoint on `contributions_from_others` (no change, just confirmation)

Newmark 2005 falsified the Newmark 2017 mapping's speculation that Newmark 2005 would confirm `lobbyist_or_principal_report_includes_contributions_received_for_lobbying` as a cross-rubric row. **Opheim's Watchpoint 4 walk confirms** the row remains single-rubric (Newmark 2017-only) in the current contributing set. No further correction to predecessors — both Newmark mappings' notes are now consistent with Opheim's findings. The next chance to promote this row from single-rubric to 2-rubric-confirmed is HG 2007 (next mapping); failing that, FOCAL `financials.*` battery or LobbyView schema fields.

### Correction 3 — Phase B mapping count

The 2026-05-13 handoff references "5 mappings done" once Newmark 2005 ships; Opheim is the 6th. The handoff's row count and remaining-rubrics count should be updated:
- Mappings done: 5 → **6** (add Opheim row; 14 rows touched, 0 new)
- Remaining rubrics: 4 → **3** (HG, FOCAL, LobbyView)

---

## Open issues surfaced by Opheim (for compendium-2.0 freeze)

Opheim introduces no new compendium rows, so no new row-design issues. It contributes one new row-design observation and one new vintage-scope observation:

1. **Cadence granularity — session-bounded vs always-monthly.** Opheim distinguishes "monthly during the session" from "monthly in-and-out-of-session" in the source quote (paper line 116–117), but Opheim's binary cut collapses both to the same 1-bucket. PRI's atomization captures only "Monthly" without distinguishing session-bounded vs always. If compendium 2.0 wants to support a future rubric that distinguishes session-bounded from always-monthly, the PRI cadence row family would need to split `lobbyist_report_cadence_includes_monthly` into two cells. **Flagged as a compendium 2.0 freeze question** — not load-bearing for current contributing rubrics (PRI, CPI, Newmark, Opheim all read the coarser cell), but extensible if FOCAL `timeliness.*` or LobbyView federal LDA-coverage cells need it. Not creating the split now (YAGNI); flagged for revisit when FOCAL mapping or LobbyView schema-coverage check surfaces the distinction.

2. **The catch-all `other_influence_peddling_or_conflict_of_interest` item.** This is the first contributing-rubric item that is **operationally undefined** at the source level. Phase C tooling should support `unable_to_evaluate` as a deterministic projection outcome for items whose underlying cells aren't determinable. Opheim's catch-all is the canonical example. When the deferred enforce.* round expands compendium 2.0 to cover prohibitions / enforcement / personnel, the catch-all may admit a multi-cell OR projection (capturing "influence peddling" observables like contingent-compensation prohibitions, post-employment cooling-off requirements, or gift-prohibition tiers), or it may stay un-projectable. Not in scope for Phase B; flagged for Phase C harness design and for the deferred-items round.

3. **Temporal-depth validation observation.** Opheim's 1988-89 vintage extends the contributing-rubric ground-truth coverage to ~28 years (1988-89 through 2015), going through Opheim → Newmark 2005 (1990-91 + 1994-95 + 1996-97 + 2000-01 + 2002 + 2003) → PRI 2010 → Sunlight 2015 + CPI 2015 + Newmark 2017. Phase C "multi-year reliability" success criterion (STATUS.md line 12) is strongly testable on rows Opheim + Newmark + PRI + Sunlight + CPI all read. Specific candidate row families for cross-vintage tolerance checking (all 3+ rubric-confirmed, multiple vintages, BoS-sourced):
   - `lobbyist_spending_report_includes_total_compensation` (Opheim 1988-89 + Newmark 2005 ×6 panels + Newmark 2017 2015 + Sunlight 2015 = 9 vintage-cells)
   - `lobbyist_spending_report_includes_compensation_broken_down_by_client` (Opheim 1988-89 + Newmark 2005 ×6 + Newmark 2017 2015 + Sunlight 2015 = 9 vintage-cells)
   - `lobbyist_spending_report_includes_total_expenditures` (Opheim 1988-89 + Newmark 2005 ×6 + Newmark 2017 2015 = 8 vintage-cells)
   - `def_target_legislative_branch` / `def_target_executive_agency` (5+ vintages each)
   - `def_actor_class_elected_officials` / `def_actor_class_public_employees` (Opheim + Newmark 2005 ×6 + Newmark 2017 = 8 vintage-cells each)
   - Cadence row family — same 8 vintage-cells, but multi-rubric reading at varying binary cuts (each rubric extracts a different projection from the underlying cells)

The Newmark 2017 mapping's other 4 open issues all carry forward unchanged. Open Issue 1 (`def_actor_class_*` row family) is now **strongly load-bearing** at 3 rubrics; per the handoff's explicit guidance, it merits explicit resolution at compendium 2.0 freeze.

---

## What Opheim doesn't ask that other rubrics will

Opheim reads no registration form content beyond the lobbyist definition (Sunlight reg-form territory; HG Q3–Q10 territory), no portal-accessibility cells (CPI #205-206, FOCAL openness.*, HG Q28-Q34, PRI Q1-Q6 + Q7a-Q7o; this is unsurprising for 1988-89 vintage — no portals existed), no audit / enforcement cells from the disclosure side (HG Q39-Q47 in the enforcement-side OOS bucket; Opheim's own 7 enforcement items are also OOS), no itemization-de-minimis threshold (Sunlight #3, HG Q15), no filing-de-minimis threshold (PRI D1), no per-meeting contact log granularity (FOCAL contact_log battery), no specific bill-number-only disclosure (Opheim reads bill_id ONLY in conjunction with position via β AND; FOCAL contact_log.11 + PRI E2g_ii read bill_id alone), no third-party-contributions-received observable (Newmark-2017-distinctive). It also lacks Newmark 2017's `disc.contributions_from_others` (per Watchpoint 4) and lacks any of the 5 `prohib.*` items Newmark 2017 added in revision (Opheim has no prohibitions section).

Opheim's role within the contributing-rubric set is **temporal-depth validation of the definitional-and-disclosure backbone of BoS-derived items, plus β-pattern exemplification on `legislation_supported_or_opposed`** — 14 of 14 row families it touches are pre-existing, the 1988-89 vintage is the earliest cross-rubric ground truth available, and the β AND-projection convention (locked 2026-05-11) now has its second concrete application. Once Phase C extraction is validated against the 2015 vintage via CPI 2015 C11 + Newmark 2017 sub-aggregates + PRI 2010 per-item data + Sunlight 2015 per-item data, Opheim provides the earliest-vintage stability check.
