# Newmark 2005 — projection mapping

**Plan:** [`../../plans/20260507_atomic_items_and_projections.md`](../../plans/20260507_atomic_items_and_projections.md) Phase B (fifth rubric to ship, after CPI 2015 C11, PRI 2010, Sunlight 2015, and Newmark 2017; OpenSecrets 2022 was tabled 2026-05-13).
**Handoff (most recent):** [`../../plans/_handoffs/20260511_phase_b_continued_remaining_7.md`](../../plans/_handoffs/20260511_phase_b_continued_remaining_7.md). Watchpoints for Newmark 2005 are in the per-rubric section there.
**Prior handoff:** [`../../plans/_handoffs/20260507_phase_b_handoff.md`](../../plans/_handoffs/20260507_phase_b_handoff.md).
**Atomic items source:** [`../items_Newmark2005.tsv`](../items_Newmark2005.tsv) (19 rows total: 18 atomic items in the main 0–18 index + 1 penalty composite add-on; **the 4 `prohib.*` items + the `penalty_stringency_2003` item are OUT of scope** per the disclosure-only Phase B qualifier).
**Predecessor mappings (for conventions):** [`cpi_2015_c11_projection_mapping.md`](cpi_2015_c11_projection_mapping.md), [`pri_2010_projection_mapping.md`](pri_2010_projection_mapping.md), [`sunlight_2015_projection_mapping.md`](sunlight_2015_projection_mapping.md), [`newmark_2017_projection_mapping.md`](newmark_2017_projection_mapping.md).
**Originating convo:** [`../../convos/20260513_newmark_2005_phase_b_mapping.md`](../../convos/20260513_newmark_2005_phase_b_mapping.md).

---

## Doc conventions

All five conventions from the predecessor mappings apply verbatim:

- Compendium row IDs are working names, not cluster-derived.
- Typed cells live on `MatrixCell.value` (v2.0 schema bump assumed).
- Granularity bias: split on every distinguishing case.
- Axis is `legal_availability` for de jure observables; Newmark 2005 reads no de facto observables (no `practical_availability` rows).
- **"Collect once, map to many."** Each row entry carries a `[cross-rubric: …]` annotation listing every other rubric that reads the same observable. Newmark 2005 is the fifth Phase B mapping, so most of the annotated readers are now well-established.

**Newmark 2005 is essentially Newmark 2017's predecessor — heavy reuse, no new rows.** Every in-scope row Newmark 2005 touches is already in another rubric's mapping. The 2005-vs-2017 structural delta is small but real (see §"Structural delta from Newmark 2017" below). Newmark 2005's contribution to compendium 2.0 is **vintage depth** (six time panels 1990–2003 covering the same BoS-derived observables Newmark 2017 covers in a single 2015 vintage) — not novel observables.

**Net reuse rate: 14/14 = 100% of in-scope rows reused. Zero new rows introduced.** This exceeds the handoff's ≥90% reuse expectation. Verified Watchpoints 1–3 below.

## Watchpoint resolutions (per [handoff](../../plans/_handoffs/20260511_phase_b_continued_remaining_7.md) Newmark 2005 section)

1. **Watchpoint 1 — PRI A-family overlap on `def_actor_class_*`: NO OVERLAP.** Grepped `items_PRI_2010.tsv` for "elected" / "public employee" / "officials" / A1–A11. PRI A1–A11 are **structural-actor / institutional-entity** observables: A1 (lobbyists as individuals), A2 (volunteer lobbyists), A3 (principals), A4 (lobbying firms), A5 (governor's office), A6 (executive branch agencies), A7 (legislative branch), A8 (independent agencies), A9 (local governments), A10 (government agencies who lobby other agencies), A11 (public entities other than government agencies). PRI B1 mentions "public officials acting within their official capacity" but only as an **exemption** framing of A5–A7 / A10 — not the individual-actor-class observable Newmark and Opheim capture. The Newmark observable is: when an individual elected official (e.g., a state senator) personally engages in lobbying, does the statutory lobbyist definition cover them? That's a different observable from "the Governor's office as an institution must register when it lobbies the legislature." **Conclusion:** `def_actor_class_elected_officials` and `def_actor_class_public_employees` (from the Newmark 2017 mapping) stand as a distinct row family. Newmark 2005 reuses both rows without restructure.

2. **Watchpoint 2 — three-threshold-cell verification against 2005 paper text: CONFIRMED.** Paper lines 120–121 (verbatim): "whether there is a compensation standard, expenditure standard, and time standard in the deﬁnition of lobbying." All three thresholds are independently enumerated as separate definitional components in Newmark 2005, identical to Newmark 2017. Newmark 2005 reuses the three typed cells the Newmark 2017 mapping introduced: `compensation_threshold_for_lobbyist_registration` (Optional[Decimal]), `expenditure_threshold_for_lobbyist_registration` (Optional[Decimal]), `time_threshold_for_lobbyist_registration` (Optional[TimeThreshold]) — each read via `IS NOT NULL`. Endnote 5 (paper line 847) notes one of the seven definition components was "constant across states" in 2003 and removed for the Cronbach's α calc; the paper does not say which. Likely `def_legislative_lobbying` (parallel to the no-variation note in Newmark 2017 paper line 518) but unverifiable from the 2005 paper alone. Per `items_Newmark2005.md` §7 the ambiguity is flagged on `def_expenditure_standard` arbitrarily — the no-variation observation is an empirical artifact of the 2003 vintage, not a definitional claim, so all seven cells are still extracted normally.

3. **Watchpoint 3 — `penalty_stringency_2003` exclusion: DOCUMENTED.** The penalty composite is a 2003-only ordinal 1–4 add-on (paper lines 740–765), not part of the 0–18 main index. Even on its own terms it is enforcement-side ("fines or harsher prison sentences for violations" — paper line 753–759) and explicitly OUT of disclosure-only Phase B scope. Excluded without further analysis. Mirrors the way the Newmark 2017 mapping handled its 5 `prohib.*` exclusions; see §"Scope qualifier — 5 items OUT" below for the full excluded-item table.

## Scope qualifier — 5 items OUT

Per the plan's disclosure-only Phase B qualifier, **4 `prohib.*` items + 1 `penalty_stringency_2003` item are excluded from this projection** without further analysis:

| Excluded item | Why excluded |
|---|---|
| `prohib_campaign_contrib_any_time` | Prohibition (no campaign contributions at any time). Restriction, not disclosure. |
| `prohib_campaign_contrib_during_session` | Prohibition (campaign contributions during the legislative session). |
| `prohib_expenditures_over_threshold` | Prohibition (expenditures over a dollar threshold per year — note: this is a *prohibition* on excessive spending, not the lobbyist-status `expenditure_threshold` definitional cell; distinct concepts). |
| `prohib_solicitation_by_officials` | Prohibition (officials soliciting gifts/contributions). |
| `penalty_stringency_2003` | Penalty add-on (1–4 ordinal, 2003-only). Enforcement-side. Paper-sourced from direct statute reading rather than BoS; rubric lacks a transparent sub-rubric mapping fines/sentences to scores (see `items_Newmark2005.md` §7 "Penalty composite is opaque"); CO, TN, WV missing data. |

These items re-enter scope in a later round (per `STATUS.md` Current Focus: "Once disclosure-side prototype is solid, expand to prohibitions / enforcement / personnel / itemization-granularity"). Five items × 50 states × 6 panels = up to 1,500 ground-truth cells parked for later, not lost.

**Implication for index reproducibility:** With 4 `prohib.*` + 1 penalty excluded, this projection **cannot reproduce `index.total` (Newmark 2005's headline 0–18 score)** for any panel. Unlike Newmark 2017 — which publishes per-state sub-aggregate totals (`def.section_total`, `prohib.section_total`, `disclosure.section_total`) in Table 2 — **Newmark 2005 publishes only per-state main-index totals in Table 1**, with no sub-aggregate breakdown. This makes Newmark 2005's Phase C validation utility **structurally weaker than Newmark 2017's** (detail in §"Phase C validation" below).

## Aggregation rule

Newmark 2005's published structure (paper lines 110–151, endnote 1, endnote 5):

- `index.total = def.section_total + freq.section_total + prohib.section_total + disclosure.section_total` (0–18; sub-aggregate sum)
- Section maxima: definitions = 7, frequency = 1, prohibitions = 4, disclosure = 6
- Each section's contribution is the unweighted sum of its 1/0 atomic items
- Each atomic item: 1 if the state's BoS-recorded statute includes the provision, 0 otherwise (per `items_Newmark2005.tsv` `scoring_rule` columns: paper line 122–123 for definitions, line 125–127 for frequency, line 148 for prohibitions and disclosure)

Phase C `project_newmark_2005_disclosure_side(state, panel)` produces:

```
def.section_total_partial    = sum of 7 def.* atomic projections  ∈ [0, 7]
freq.section_total           = freq_reporting_more_than_annual projection  ∈ [0, 1]
disclosure.section_total     = sum of 6 disclosure.* atomic projections  ∈ [0, 6]
```

The `prohib.*` portion of `index.total` (0–4) and the `penalty_stringency_2003` add-on (1–4, 2003 only) are **not produced** (`prohib.section_total` is undefined for this projection). Maximum reproducible partial score = 7 + 1 + 6 = **14/18** (excluding penalty).

## Per-state per-indicator data

**Newmark 2005 publishes per-state TOTAL scores only.** Table 1 (paper lines 182–686) publishes `index.total` for each of 50 states across six panels (1990–91, 1994–95, 1996–97, 2000–01, 2002, 2003) plus the 2003 total-plus-penalty column. **Sub-aggregate totals are NOT published per state.** This is a published-data shape weaker than Newmark 2017's Table 2 (which publishes `def.section_total`, `prohib.section_total`, `disclosure.section_total`, and `index.total` per state).

**Practical consequence for Phase C:**

- Per-atomic-item validation against Newmark 2005's published data is impossible (paper publishes only totals).
- **Per-section-total validation is also impossible** (Newmark 2005 paper doesn't publish section sub-aggregates).
- The only Newmark 2005-direct Phase C check is: `our_projected_partial + extracted_prohib + extracted_penalty ≈ Newmark_published_total` — which requires extracting `prohib.*` and `penalty` items we are deferring. Without that, Phase C can only assert: `our_projected_partial ≤ Newmark_published_total` (a weak inequality, since `prohib.section_total + penalty ∈ [0, 4+penalty]` is positive).
- **Cross-rubric validation remains the actual quality check.** Newmark 2005's BoS-sourced atomic items are correct-by-construction when our compendium extraction is validated against PRI 2010 per-state per-item (available in `docs/historical/pri-2026-rescore/`) and CPI 2015 C11 per-state (`results/cpi_2015_c11_per_state_scores.csv`) — both of which use the same upstream statutory observables.

**Distribution context (from paper Table 1 + lines 168–177):**

| Panel | `index.total` range (observed) | Mean | SD |
|---|---|---|---|
| 1990–91 | 1 – 14 | 6.54 | (paper does not give SD for 1990–91 explicitly; range from line 169) |
| 2003 | 1 – 17 | (paper notes range; mean/SD not given in body) | — |

No state hits 18, no state hits 0. The endnote 5 "constant across states" definition component (one of the seven) explains the guaranteed-positive floor and the unreached ceiling.

## Phase C validation

50 US states × **6 panels** = 300 per-state `index.total` ground-truth values. Of these:

- **0 are directly usable for sub-aggregate tolerance check** (paper doesn't publish sub-aggregates).
- **300 are usable for a weak inequality check** (`our_projected_partial ≤ paper_total` always must hold).
- **300 become usable for full tolerance check IF the deferred `prohib.*` and `penalty_stringency_2003` items are extracted** in a later round.

This is a meaningful regression in Phase C utility relative to Newmark 2017 (which contributes 100 sub-aggregate cells of full-tolerance ground truth from a single 2015 vintage). Newmark 2005's contribution to Phase C is **temporal-coverage validation** — the 1990–2003 panels are the only multi-vintage ground truth in the current contributing-rubric set, and confirm that the BoS-sourced observables remained reasonably stable over the period (Newmark's own 1990–91 vs 2003 correlation = 0.46, p < 0.01 per paper line 158).

Federal LDA out of scope (Newmark 2005 is state-only). Predecessor mappings noted that Newmark 2017 is the explicit successor to Newmark 2005 (paper line 117: "Similar to Opheim's (1991) measure"); Newmark 2005's actual predecessor is Opheim 1991, which is the next mapping in the Phase B order.

---

## Structural delta from Newmark 2017

Two delta items between 2005 and 2017 — both noted briefly here, fully analyzed below.

| Item | Newmark 2005 | Newmark 2017 | Net effect on row family |
|---|---|---|---|
| `freq_reporting_more_than_annual` | **Present** (its own 1-item category) | **Absent** (2017 paper omits cadence) | 2005 reuses existing PRI E1h/E2h cadence row family — adds a new cross-rubric reader, but no new compendium row. |
| `disc.contributions_from_others` | **Absent** (2005 has 6 disclosure items, not 7) | **Present** (`disclosure.contributions_from_others` → `lobbyist_or_principal_report_includes_contributions_received_for_lobbying`) | The Newmark 2017 mapping speculated "Newmark 2005 *contributions* parallel item (likely; not directly verified)" for this row's cross-rubric annotation. **Falsified by this mapping** — Newmark 2005 does NOT have a parallel. The row remains Newmark-2017-distinctive within the current contributing rubric set. |

The 2017 mapping's cross-rubric annotations need a small correction noted in §"Corrections to predecessor mappings" below.

---

## Per-item mappings

### Definitions battery (7 items, all in scope; all reused from Newmark 2017 mapping)

Newmark 2005's "statutory definitions" sub-aggregate. The seven items decompose into:
- 2 **activity-type** observables (legislative / administrative-agency lobbying triggers registration)
- 2 **actor-class** observables (elected officials / public employees as lobbyists)
- 3 **lobbyist-status threshold** observables (compensation / expenditure / time standards)

All 7 rows pre-exist in the compendium (4 from the Newmark 2017 mapping introducing new rows, 3 from earlier mappings).

#### newmark_2005.def_legislative_lobbying — Legislative lobbying

- **Compendium rows:** `def_target_legislative_branch` (binary; legal)
  [cross-rubric: CPI #196 (one of three target-type reads in IND_196's compound); HG Q1 (inverse-framed); FOCAL `scope.3` (legislative branches as targets); **Newmark 2017 `def.legislative_lobbying` (successor)**; Opheim `def.legislative_lobbying`; PRI A7 actor-side (`actor_legislative_branch_registration_required`, parallel-but-not-identical observable)]
  Already in CPI mapping; pre-existing.
- **Cell type:** binary.
- **Axis:** `legal_availability`.
- **Scoring rule:** `cell == TRUE → 1; else → 0`.
- **Source quote:** "legislative lobbying, administrative agency lobbying" (Newmark 2005 paper line 118–119).
- **Note on endnote 5 constant-across-states:** Per paper endnote 5 (line 847–848) one of the seven definition components was constant across all 50 states in 2003 and removed for the Cronbach's α calc (yielding 17, not 18). Paper does not say which. Most likely candidate is this item — Newmark 2017 explicitly says "All 50 states require registration for lobbying the legislature" (2017 paper line 518). Cell still extracted normally; the no-variation status is a 2003-vintage empirical fact, not a definitional claim.

#### newmark_2005.def_administrative_agency_lobbying — Administrative agency lobbying

- **Compendium rows:** `def_target_executive_agency` (binary; legal)
  [cross-rubric: CPI #196 (compound second arm — "executive officials"); HG Q1; FOCAL `scope.3`; **Newmark 2017 `def.administrative_agency_lobbying` (successor)**; Opheim `def.administrative_agency_lobbying`; PRI A actor-side (parallel)]
  Already in CPI mapping; pre-existing.
- **Cell type:** binary.
- **Axis:** `legal_availability`.
- **Scoring rule:** `cell == TRUE → 1; else → 0`.
- **Source quote:** "administrative agency lobbying, elected officials as lobbyists" (Newmark 2005 paper line 119).

#### newmark_2005.def_elected_officials_as_lobbyists — Elected officials as lobbyists

- **Compendium rows:** `def_actor_class_elected_officials` (binary; legal)
  [cross-rubric: **Newmark 2017 `def.elective_officials_as_lobbyists` (successor)**; Opheim `def.elective_officials`]
  Already in Newmark 2017 mapping; pre-existing.
- **Cell type:** binary.
- **Axis:** `legal_availability`.
- **Scoring rule:** `cell == TRUE → 1; else → 0`.
- **Source quote:** "elected officials as lobbyists, public employees as lobbyists" (Newmark 2005 paper line 119–120).
- **Note on row family:** This is the new `def_actor_class_*` row family the Newmark 2017 mapping introduced as Open Issue 1. Watchpoint 1 (PRI A-family overlap check) resolved negatively this session — PRI A1–A11 are structural/institutional-actor observables, not individual-actor-class. The `def_actor_class_*` family stands as a third row family distinct from CPI's `def_target_*` and PRI's `actor_*`. Reused unchanged from Newmark 2017 mapping.

#### newmark_2005.def_public_employees_as_lobbyists — Public employees as lobbyists

- **Compendium rows:** `def_actor_class_public_employees` (binary; legal)
  [cross-rubric: **Newmark 2017 `def.public_employees_as_lobbyists` (successor)**; Opheim `def.public_employees`]
  Already in Newmark 2017 mapping; pre-existing.
- **Cell type:** binary.
- **Axis:** `legal_availability`.
- **Scoring rule:** `cell == TRUE → 1; else → 0`.
- **Source quote:** "public employees as lobbyists, and whether there is a compensation standard" (Newmark 2005 paper line 120).
- **Note:** Same `def_actor_class_*` row family; same Watchpoint 1 resolution applies.

#### newmark_2005.def_compensation_standard — Compensation standard

- **Compendium rows:** `compensation_threshold_for_lobbyist_registration` (typed `Optional[Decimal]`; legal)
  [cross-rubric: CPI #197 (reads the dollar value at 3-tier); HG Q2 (reads as 5-tier ordinal); FOCAL `scope.2` (combined with filing-de-minimis per handoff threshold table); **Newmark 2017 `def.compensation_standard` (successor)**; Opheim `def.compensation_standard`]
  Already in CPI mapping; pre-existing typed cell.
- **Cell type:** `Optional[Decimal]` representing the compensation dollar threshold above which the lobbyist-definition triggers.
- **Axis:** `legal_availability`.
- **Scoring rule:** `cell IS NOT NULL → 1; else → 0`. Newmark 2005 reads only the presence of a standard, not the value (paper line 121–123: "Each of these components is coded 1 if the state considers a given behavior as lobbying and 0 otherwise.").
- **Source quote:** "whether there is a compensation standard, expenditure standard, and time standard in the deﬁnition of lobbying" (Newmark 2005 paper line 120–121).
- **Note on threshold-concept distinction:** This is the **lobbyist-status threshold** (one of five distinct threshold concepts surfaced by the Sunlight mapping). Not to be confused with the filing-de-minimis (PRI D1), itemization-de-minimis (Sunlight #3 / HG Q15), or the **`prohib_expenditures_over_threshold` item** in Newmark 2005 itself (which is a prohibition on excessive spending — a fifth, separate concept). See the handoff doc's threshold-concepts table.

#### newmark_2005.def_expenditure_standard — Expenditure standard

- **Compendium rows:** `expenditure_threshold_for_lobbyist_registration` (typed `Optional[Decimal]`; legal)
  [cross-rubric: **Newmark 2017 `def.expenditure_standard` (successor)**; Opheim `def.expenditure_standard`; potential FOCAL `scope.2` partial read (FOCAL bundles all three thresholds at finer granularity)]
  Already in Newmark 2017 mapping; pre-existing typed cell.
- **Cell type:** `Optional[Decimal]` representing the expenditure dollar threshold above which the lobbyist-definition triggers. Distinct cell from the compensation-threshold row above.
- **Axis:** `legal_availability`.
- **Scoring rule:** `cell IS NOT NULL → 1; else → 0`.
- **Source quote:** "compensation standard, expenditure standard, and time standard in the deﬁnition of lobbying" (Newmark 2005 paper line 121).
- **Watchpoint 2 resolution:** Newmark 2005 enumerates this threshold as a separate definitional component, verbatim parallel to Newmark 2017. Reuses the typed cell the Newmark 2017 mapping introduced.

#### newmark_2005.def_time_standard — Time standard

- **Compendium rows:** `time_threshold_for_lobbyist_registration` (typed `Optional[TimeThreshold]`; legal)
  [cross-rubric: **Newmark 2017 `def.time_standard` (successor)**; Opheim `def.time_standard`; potential FOCAL `scope.2` partial read; Federal LDA 20%-of-work-time rule]
  Already in Newmark 2017 mapping; pre-existing typed cell.
- **Cell type:** `Optional[TimeThreshold]` where `TimeThreshold = {magnitude: Decimal, unit: enum{hours_per_quarter, hours_per_year, days_per_year, percent_of_work_time, ...}}`. Structured value accommodates hours-per-period, days-per-period, and percent-of-work-time variants.
- **Axis:** `legal_availability`.
- **Scoring rule:** `cell IS NOT NULL → 1; else → 0`. Newmark 2005 reads only presence/absence (paper line 122–123: "Each of these components is coded 1 ... 0 otherwise.").
- **Source quote:** "expenditure standard, and time standard in the deﬁnition of lobbying. Each of these components is coded 1 if the state considers a given behavior as lobbying and 0 otherwise." (Newmark 2005 paper line 121–123).
- **Watchpoint 2 resolution:** Same as above — Newmark 2005 enumerates all three thresholds verbatim; reuses the typed cell Newmark 2017 mapping introduced.

### Frequency battery (1 item, in scope; reused from PRI cadence row family)

Newmark 2005's "frequency of reporting" sub-aggregate is a single item with maximum value 1. Newmark 2017 does not have a parallel item — this is a 2005-distinctive observable in the Newmark tradition, but it **reuses the existing PRI cadence row family** rather than introducing new compendium rows.

#### newmark_2005.freq_reporting_more_than_annual — Frequency of reporting (more frequently than once per year)

- **Compendium rows:** OR over the existing PRI cadence row family:
  `lobbyist_report_cadence_includes_monthly` OR
  `lobbyist_report_cadence_includes_quarterly` OR
  `lobbyist_report_cadence_includes_triannual` OR
  `lobbyist_report_cadence_includes_semiannual` OR
  `principal_report_cadence_includes_monthly` OR
  `principal_report_cadence_includes_quarterly` OR
  `principal_report_cadence_includes_triannual` OR
  `principal_report_cadence_includes_semiannual`
  (8 binary cells; "annual" and "other" excluded since "annual" = annually = not more frequent than annual)
  [cross-rubric: PRI E1h_i/ii/iii/iv (principal; canonical atomization at full 6-option granularity) + PRI E2h_i/ii/iii/iv (lobbyist; canonical atomization); CPI #202 (`lobbyist_spending_report_filing_cadence` — read as enum derived from binaries); Opheim `disclosure.frequency` (binary at a *finer* cut: only "monthly during session or both in-and-out-of-session" → 1, vs Newmark 2005's broader ">annual" cut); FOCAL `timeliness.*` battery (overlap per handoff cadence-rubric notes — exact projection deferred to FOCAL mapping); HG Q11 (gateway: spending report required — implies a cadence exists) — Q11 doesn't directly read the cadence cells but presumes a cadence row family is populated]
  Pre-existing row family from PRI mapping; **no new rows introduced by this Newmark 2005 item.**
- **Cell type:** projection only — reads 8 binary cells, OR-aggregated.
- **Axis:** `legal_availability`.
- **Scoring rule:** `(any cadence binary in {monthly, quarterly, triannual, semiannual} for lobbyist OR principal == TRUE) → 1; else → 0`.
- **Source quote:** "The frequency of reporting requirements was coded 1 for those states that required registration and reporting more frequently than once per year and 0 for those states reporting once per year or less" (Newmark 2005 paper line 125–127).
- **Note on "registration and reporting" conflation:** Newmark's source quote bundles registration cadence and reporting cadence into a single binary. A state requiring annual registration but quarterly reporting (or vice versa) gets coded based on whichever cadence is observed — the paper doesn't disambiguate. **Projection convention:** read *reporting* cadence (PRI E1h/E2h rows), not registration cadence (CPI #199 `lobbyist_registration_renewal_cadence` row). Rationale: (a) Newmark's broader category is "frequency of reporting requirements" (paper line 124–126) — "reporting" framing dominates; (b) CPI #199 is a distinct row family (renewal cadence vs reporting cadence) per the CPI mapping's note that "Registration-renewal cadence is a distinct concept" from PRI E1h/E2h. If a state has annual reporting but more-frequent renewal, Newmark would code 0 here (no quarterly reporting), which matches the projection convention.
- **Note on Opheim cut vs Newmark cut:** Opheim 1991 reads the same cadence row family but at a *finer* threshold ("monthly during session or both in-and-out-of-session" → 1; quarterly/semi-annual/annual → 0; paper lines 115–118). Newmark 2005's projection includes quarterly and triannual and semi-annual in the "more frequent than annual" bucket, so a state with quarterly reporting gets Newmark = 1 / Opheim = 0. Both rubrics project from the same underlying cells — different binary cuts. (When Opheim mapping ships, its cadence-reading should reuse the same PRI row family and project at the monthly-only-during-session cut.)
- **Note on enum-vs-binary tension:** PRI's atomization permits "multiple cadences allowed simultaneously" regimes (a state could allow monthly OR quarterly filing at filer's discretion). Newmark 2005's binary OR-projection is correct for the "more frequent than annual" cut regardless of how the underlying multi-cadence regime is encoded — if any sub-annual cadence binary is TRUE, the projection is 1. PRI mapping's Open Issue 4 (enum-vs-binary tension between CPI #202 and PRI E1h/E2h) doesn't affect this projection.

### Prohibitions battery (4 items, ALL OUT of scope)

Newmark 2005's "prohibited activities" sub-aggregate. All 4 items are restrictions on conduct, not disclosure requirements. Excluded per the disclosure-only Phase B qualifier.

| Excluded item | Source quote (Newmark 2005) | Re-entry scope |
|---|---|---|
| `prohib_campaign_contrib_any_time` | "campaign contributions at any time" (line 140) | Prohibitions round (deferred) |
| `prohib_campaign_contrib_during_session` | "campaign contributions during the legislative session" (line 141) | Prohibitions round (deferred) |
| `prohib_expenditures_over_threshold` | "expenditures in excess of a certain dollar amount per year" (line 141) | Prohibitions round (deferred). **Distinct from the `expenditure_threshold_for_lobbyist_registration` definitional cell** — that cell is the dollar threshold above which the lobbyist-definition triggers (i.e., spending above $X makes you a lobbyist); this prohibition is the dollar ceiling above which spending is *forbidden* (i.e., a registered lobbyist cannot spend more than $Y on lobbying). Different concepts, both relevant, both observable in state statutes. |
| `prohib_solicitation_by_officials` | "solicitation by ofﬁcials or employees for contributions or gifts" (line 142) | Prohibitions round (deferred) |

These four × 50 states × 6 panels = up to 1,200 ground-truth cells parked.

### Disclosure battery (6 items, all in scope; all reused from Newmark 2017 mapping)

Newmark 2005's "disclosure requirements" sub-aggregate (6 types per paper lines 143–148). The six items decompose into:
- 1 **subject-matter** observable: maps to existing Sunlight/HG/PRI subject-matter row.
- 1 **expenditures-benefiting-officials** observable: maps to existing PRI gifts/entertainment row, projected as OR over actors.
- 2 **compensation** observables: map to existing Sunlight compensation rows.
- 2 **expenditure summary** observables: 1 reuses Sunlight categories row; 1 reuses the new Newmark-2017-introduced total-expenditures row.

**Note on 6-vs-7 disclosure items:** Newmark 2017 has 7 disclosure items, Newmark 2005 has 6. The Newmark 2017 7th item is `disclosure.contributions_from_others` (mapping to the new `lobbyist_or_principal_report_includes_contributions_received_for_lobbying` row); **Newmark 2005 does NOT have a parallel item**. This falsifies the Newmark 2017 mapping's cross-rubric annotation that speculated a 2005 parallel; correction noted in §"Corrections to predecessor mappings" below.

#### newmark_2005.disc_legislative_admin_action_to_influence — Legislative/administrative action seeking to influence

- **Compendium rows:** `lobbyist_spending_report_includes_general_subject_matter` (binary; legal)
  [cross-rubric: Sunlight #1 (the spending-report-side general-subject-matter row); HG Q20 subject-tier (read on spending reports); **Newmark 2017 `disclosure.influence_legislation_or_admin` (successor)**; PRI E2g_i (lobbyist-side subject disclosure); Opheim `disclosure.legislation_supported_or_opposed` (loose reading, via β AND-projection); FOCAL `contact_log.11` (broad reading on subject coverage)]
  Already in Sunlight mapping; pre-existing.
- **Cell type:** binary.
- **Axis:** `legal_availability`.
- **Scoring rule:** `cell == TRUE → 1; else → 0`.
- **Source quote:** "Disclosure requirements include the following six types: legislative/administrative action seeking to inﬂuence" (Newmark 2005 paper line 143–144).

#### newmark_2005.disc_expenditures_benefiting_officials — Expenditures benefiting public officials or employees

- **Compendium rows:** `lobbyist_report_includes_gifts_entertainment_transport_lodging` (binary; legal) AND/OR `principal_report_includes_gifts_entertainment_transport_lodging` (binary; legal)
  [cross-rubric: PRI E1f_iii (principal-side); PRI E2f_iii (lobbyist-side); **Newmark 2017 `disclosure.expenditures_benefiting_officials` (successor)**; Opheim `disclosure.expenditures_benefitting_public_employees` ("including gifts"); FOCAL `financials.10` (verbatim parallel); HG Q14 / Q17 / Q23 (partial reads at finer gift granularity — disclosure-only portion)]
  Already in PRI mapping; pre-existing pair of rows.
- **Cell type:** binary per row.
- **Axis:** `legal_availability`.
- **Scoring rule:** `(lobbyist_report_includes_gifts_entertainment_transport_lodging OR principal_report_includes_gifts_entertainment_transport_lodging) → 1; else → 0`. Newmark's framing is actor-agnostic; OR over the two actor-side rows is the coarsest correct reading. Same projection convention as Newmark 2017's `disclosure.expenditures_benefiting_officials`.
- **Source quote:** "expenditures beneﬁting public ofﬁcials or employees, compensation received broken down by employers" (Newmark 2005 paper line 145).
- **Note on row-design watchpoint (resolved upstream):** The Newmark 2017 mapping session locked the decision to keep the PRI bundled rows (gifts ∪ entertainment ∪ transport ∪ lodging × principal/lobbyist) rather than splitting `gifts` out separately. HG Q23's finer gift granularity remains flagged for compendium 2.0 freeze. No new decisions required this session.

#### newmark_2005.disc_compensation_by_employer — Compensation received broken down by employers

- **Compendium rows:** `lobbyist_spending_report_includes_compensation_broken_down_by_client` (binary; legal)
  [cross-rubric: Sunlight #5 (the broken-down-by-client row); **Newmark 2017 `disclosure.compensation_by_employer` (successor; verbatim parallel)**; HG Q13 footnote ("Full points if information is on registration form instead") at coarser granularity; CPI #201 (compound — compensation-included is one of three reads)]
  Already in Sunlight mapping; pre-existing.
- **Cell type:** binary.
- **Axis:** `legal_availability`.
- **Scoring rule:** `cell == TRUE → 1; else → 0`.
- **Source quote:** "compensation received broken down by employers, total compensation received" (Newmark 2005 paper line 145–146).
- **Note on "employer" vs "client" naming:** Newmark 2005 uses "employer", same as Newmark 2017; Sunlight uses "client". Same observable. Open Issue 2 from the Newmark 2017 mapping carries forward — compendium 2.0 should rename to `_by_paying_entity` or `_by_employer_or_client`.

#### newmark_2005.disc_total_compensation — Total compensation received

- **Compendium rows:** `lobbyist_spending_report_includes_total_compensation` (binary; legal)
  [cross-rubric: Sunlight #5 (total-compensation-on-spending-report row); **Newmark 2017 `disclosure.total_compensation` (successor)**; HG Q13 (binary lobbyist-side compensation on spending report); HG Q27 (mirror on principal/employer side — distinct cell, parallel); CPI #201 (compound); PRI E2f_i ("Direct lobbying costs (compensation)")]
  Already in Sunlight mapping; pre-existing.
- **Cell type:** binary.
- **Axis:** `legal_availability`.
- **Scoring rule:** `cell == TRUE → 1; else → 0`.
- **Source quote:** "total compensation received, categories of expenditures, and total expenditures" (Newmark 2005 paper line 146).

#### newmark_2005.disc_categories_of_expenditures — Categories of expenditures

- **Compendium rows:** `lobbyist_spending_report_categorizes_expenses_by_type` (binary; legal)
  [cross-rubric: Sunlight #2 categorized-tier; **Newmark 2017 `disclosure.categories_of_expenditures` (successor)**; HG Q14 ("summaries (totals) of spending classified by category types — gifts, entertainment, postage"); Opheim `disclosure.spending_by_category`; FOCAL `financials.*` battery]
  Already in Sunlight mapping; pre-existing.
- **Cell type:** binary.
- **Axis:** `legal_availability`.
- **Scoring rule:** `cell == TRUE → 1; else → 0`.
- **Source quote:** "categories of expenditures, and total expenditures" (Newmark 2005 paper line 146–147).

#### newmark_2005.disc_total_expenditures — Total expenditures

- **Compendium rows:** `lobbyist_spending_report_includes_total_expenditures` (binary; legal)
  [cross-rubric: **Newmark 2017 `disclosure.total_expenditures` (successor)**; Opheim `disclosure.total_spending` ("lobbyist's total spending"); HG Q11 (gateway: spending report required); HG Q36 (state agency provides overall lobbying spending total — different observable, public-access side); CPI #201 (compound); Sunlight #2 tier 0+ (implicit)]
  Already in Newmark 2017 mapping; pre-existing.
- **Cell type:** binary.
- **Axis:** `legal_availability`.
- **Scoring rule:** `cell == TRUE → 1; else → 0`.
- **Source quote:** "and total expenditures. Again, each of these categories was coded 1 or 0 depending on whether the state had such a requirement" (Newmark 2005 paper line 147–148).
- **Note:** This is the **18th and final component** of Newmark 2005's 0–18 index (per `items_Newmark2005.tsv` notes column). Reuses the row Newmark 2017 mapping introduced.

### Penalty add-on (1 item, OUT of scope)

| Excluded item | Source quote | Re-entry scope |
|---|---|---|
| `penalty_stringency_2003` | "The states were scored 1 to 4, with 1 indicating the weakest penalties and 4 the strictest" (line 763–764); "States that speciﬁed larger ﬁnes or harsher prison sentences for violations were considered to have stricter regulations than those with smaller or no ﬁnes" (line 753–759) | Enforcement round (deferred). Paper-coded directly from state codes (not BoS), 2003-only, ordinal 1–4; rubric is underspecified (Newmark provides general considerations — felony/misdemeanor classification, fine sizes, prison sentences, several failure-to-X categories — but no transparent rubric mapping to specific scores; CO/TN/WV missing per endnote 8). Per `items_Newmark2005.md` §7 "Penalty composite is opaque." |

50 states × 1 panel (2003 only) = 47 ground-truth cells (CO/TN/WV missing) parked.

---

## Summary of compendium rows touched

| Row id (working name) | Cell type | Axis | Newmark 2005 items reading | Cross-rubric readers (dedupe candidates) | Status |
|---|---|---|---|---|---|
| `def_target_legislative_branch` | binary | legal | `def_legislative_lobbying` | CPI #196, HG Q1, FOCAL scope.3, Newmark 2017, Opheim, PRI A7 (actor-side parallel) | existing (CPI mapping) |
| `def_target_executive_agency` | binary | legal | `def_administrative_agency_lobbying` | CPI #196, HG Q1, FOCAL scope.3, Newmark 2017, Opheim | existing (CPI mapping) |
| `def_actor_class_elected_officials` | binary | legal | `def_elected_officials_as_lobbyists` | Newmark 2017, Opheim | existing (Newmark 2017 mapping) |
| `def_actor_class_public_employees` | binary | legal | `def_public_employees_as_lobbyists` | Newmark 2017, Opheim | existing (Newmark 2017 mapping) |
| `compensation_threshold_for_lobbyist_registration` | typed `Optional[Decimal]` | legal | `def_compensation_standard` (via `IS NOT NULL`) | CPI #197, HG Q2, FOCAL scope.2, Newmark 2017, Opheim | existing (CPI mapping) |
| `expenditure_threshold_for_lobbyist_registration` | typed `Optional[Decimal]` | legal | `def_expenditure_standard` (via `IS NOT NULL`) | Newmark 2017, Opheim, FOCAL scope.2 (partial) | existing (Newmark 2017 mapping) |
| `time_threshold_for_lobbyist_registration` | typed `Optional[TimeThreshold]` | legal | `def_time_standard` (via `IS NOT NULL`) | Newmark 2017, Opheim, FOCAL scope.2 (partial), Federal LDA 20% rule | existing (Newmark 2017 mapping) |
| `lobbyist_report_cadence_includes_{monthly,quarterly,triannual,semiannual}` + `principal_report_cadence_includes_{monthly,quarterly,triannual,semiannual}` (8 cells, OR-projection) | binary × 8 | legal | `freq_reporting_more_than_annual` (via OR over 8 cells) | PRI E1h_i/ii/iii/iv + E2h_i/ii/iii/iv (canonical 6-option atomization, but 2 options excluded from this projection); CPI #202 (enum-derived); Opheim `disclosure.frequency` (finer-cut binary on same cells); FOCAL `timeliness.*` (overlap deferred to FOCAL mapping); HG Q11 (gateway) | existing (PRI mapping) |
| `lobbyist_spending_report_includes_general_subject_matter` | binary | legal | `disc_legislative_admin_action_to_influence` | Sunlight #1, HG Q20, Newmark 2017, PRI E2g_i, Opheim (β AND-projection), FOCAL contact_log.11 | existing (Sunlight mapping) |
| `lobbyist_report_includes_gifts_entertainment_transport_lodging` | binary | legal | `disc_expenditures_benefiting_officials` (via OR with principal-side) | PRI E2f_iii, FOCAL financials.10, Newmark 2017, Opheim | existing (PRI mapping) |
| `principal_report_includes_gifts_entertainment_transport_lodging` | binary | legal | `disc_expenditures_benefiting_officials` (via OR with lobbyist-side) | PRI E1f_iii, FOCAL financials.10 (combined), Newmark 2017, Opheim | existing (PRI mapping) |
| `lobbyist_spending_report_includes_compensation_broken_down_by_client` | binary | legal | `disc_compensation_by_employer` | Sunlight #5, Newmark 2017, HG Q13 footnote, CPI #201 | existing (Sunlight mapping) |
| `lobbyist_spending_report_includes_total_compensation` | binary | legal | `disc_total_compensation` | Sunlight #5, Newmark 2017, HG Q13, CPI #201, PRI E2f_i | existing (Sunlight mapping) |
| `lobbyist_spending_report_categorizes_expenses_by_type` | binary | legal | `disc_categories_of_expenditures` | Sunlight #2, HG Q14, Newmark 2017, Opheim, FOCAL financials.* | existing (Sunlight mapping) |
| `lobbyist_spending_report_includes_total_expenditures` | binary | legal | `disc_total_expenditures` | Newmark 2017, Opheim, HG Q11 (gateway), CPI #201 (compound) | existing (Newmark 2017 mapping) |

**14 distinct compendium row families touched by 14 Newmark 2005 atomic items in scope** (counting the 8-cell cadence OR-projection as one family read). **All 14 are pre-existing**: 4 from the CPI mapping, 4 from the Sunlight mapping, 2 from the PRI mapping (gifts/entertainment principal-and-lobbyist pair), 1 from the PRI mapping (cadence family), and 4 from the Newmark 2017 mapping (the two `def_actor_class_*` rows + `expenditure_threshold_*` + `time_threshold_*` + `lobbyist_spending_report_includes_total_expenditures`). **Zero new rows introduced.**

Reuse rate: **14/14 = 100%.** Exceeds the handoff's ≥90% reuse expectation. This is consistent with Newmark 2005 being the explicit predecessor to Newmark 2017 (paper line 117 explicitly invokes Opheim 1991 as the basis; Newmark 2017 then extends 2005 by adding `disc.contributions_from_others` and dropping the standalone frequency item, while adding 5 `prohib.*` items not in 2005's prohibitions battery).

---

## Corrections to predecessor mappings

### Correction 1 — Newmark 2017 mapping speculation on `disc.contributions_from_others`

The Newmark 2017 mapping doc speculated (in the cross-rubric annotation for `lobbyist_or_principal_report_includes_contributions_received_for_lobbying`):

> [cross-rubric: Newmark 2005 *contributions* parallel item (likely; not directly verified in cross-rubric grep but predecessor structure suggests parallel inclusion in the 2005 disclosure-of-6 battery)]

**Falsified by this mapping.** Newmark 2005 has **only 6 disclosure items**, not 7, and does not have a `contributions_from_others` parallel. Per `items_Newmark2005.tsv` rows 14–19, the six disclosure items are exactly: `disc_legislative_admin_action_to_influence`, `disc_expenditures_benefiting_officials`, `disc_compensation_by_employer`, `disc_total_compensation`, `disc_categories_of_expenditures`, `disc_total_expenditures`. No contributions-received item.

**The row `lobbyist_or_principal_report_includes_contributions_received_for_lobbying` remains Newmark-2017-distinctive in the current contributing-rubric set.** Whether Opheim 1991, HiredGuns 2007, or FOCAL 2024 reads it is unknown until their respective mappings ship. The Newmark 2017 mapping's Summary table footnote ("After Newmark 2005 mapping, expect at most 1 row remains single-rubric (`contributions_received_for_lobbying`) until Newmark 2005 explicitly confirms its parallel.") should now be updated to "**confirmed single-rubric in Newmark/Opheim/Sunlight/CPI/PRI; pending check against HG, FOCAL, OpenSecrets (tabled), LobbyView**".

### Correction 2 — Phase B mapping count

The Newmark 2017 mapping doc and the 2026-05-13 handoff both reference "5 mappings done" once this ships. The handoff's row count table will need a row appended for Newmark 2005 (14 rows touched, 0 new) and the remaining-rubrics count decremented from 6 to 5.

---

## Open issues surfaced by Newmark 2005 (for compendium-2.0 freeze)

Newmark 2005 introduces no new compendium rows, so no new row-design issues. It contributes one new vintage-scope observation:

1. **Temporal stability of BoS-derived observables (1990–2003).** Newmark's own paper-internal correlation of 1990–91 vs 2003 = 0.46 (p < 0.01; paper line 158) confirms the BoS-sourced cells are **non-stationary** over a 13-year window — meaningful drift, but not a regime change. Phase C extraction over multi-vintage BoS data should expect the same row family to extract different cell values across vintages. This argues for **vintage-aware extraction** rather than a single-vintage extraction pipeline. (Already accounted for in the project's "multi-year reliability" success criterion per STATUS.md line 12.)

The Newmark 2017 mapping's 6 open issues all carry forward unchanged. The `def_actor_class_*` row family is now **2-rubric-confirmed** (Newmark 2005 + Newmark 2017 + Opheim) so Open Issue 1 from Newmark 2017 is increasingly load-bearing; it merits explicit resolution at compendium 2.0 freeze rather than indefinite deferral.

---

## What Newmark 2005 doesn't ask that other rubrics will

Newmark 2005 reads no registration form content beyond the lobbyist definition (Sunlight reg-form territory; HG Q3–Q10 territory), no timeliness of disclosure beyond the binary >annual cadence cut, no itemization-de-minimis threshold (Sunlight #3, HG Q15), no filing-de-minimis threshold (PRI D1), no per-meeting contact log granularity (FOCAL contact_log battery), no specific bill-number disclosure (FOCAL contact_log.11, PRI E1g_ii/E2g_ii), no portal-accessibility / search / filter cells (CPI #205-206, FOCAL openness, HG Q28-Q34, PRI Q1-Q6 + Q7a-Q7o), no audit / enforcement cells (CPI #207-209, HG Q39-Q47), and no third-party-contributions-received observable (Newmark-2017-distinctive). It also lacks Newmark 2017's `disc.contributions_from_others` and lacks any of the 5 `prohib.*` items Newmark 2017 added in revision.

Newmark 2005's role within the contributing-rubric set is **temporal-coverage validation of the definitional-and-disclosure backbone of BoS-derived items** — 14 of 14 rows it touches are established, and the six time panels (1990–91 through 2003) are the project's only multi-vintage ground truth in the current contributing-rubric set. Once Phase C extraction is validated against the 2015 vintage via CPI 2015 C11 + Newmark 2017 sub-aggregates + PRI 2010 per-item data, Newmark 2005 provides the cross-vintage stability check.
