# HiredGuns 2007 — projection mapping

**Plan:** [`../../plans/20260507_atomic_items_and_projections.md`](../../plans/20260507_atomic_items_and_projections.md) Phase B (seventh rubric to ship, after CPI 2015 C11, PRI 2010, Sunlight 2015, Newmark 2017, Newmark 2005, and Opheim 1991; OpenSecrets 2022 was tabled 2026-05-13).
**Handoff (most recent):** [`../../plans/_handoffs/20260511_phase_b_continued_remaining_7.md`](../../plans/_handoffs/20260511_phase_b_continued_remaining_7.md). Watchpoints for HG are in the per-rubric section there.
**Prior handoff:** [`../../plans/_handoffs/20260507_phase_b_handoff.md`](../../plans/_handoffs/20260507_phase_b_handoff.md).
**Atomic items source:** [`../items_HiredGuns.tsv`](../items_HiredGuns.tsv) (48 rows total: Q1–Q48 atomic, all CPI question numbering; **Q39–Q47 enforcement and Q48 cooling-off are OUT** per the disclosure-only Phase B qualifier).
**Atomic items audit:** [`../items_HiredGuns.md`](../items_HiredGuns.md) — documents the 8-category atomization, the conditional cascade on Q15, and the Q24 composite quirk (5 labels / 3 point values).
**Predecessor mappings (for conventions):** all six prior mappings — `cpi_2015_c11_projection_mapping.md`, `pri_2010_projection_mapping.md`, `sunlight_2015_projection_mapping.md`, `newmark_2017_projection_mapping.md`, `newmark_2005_projection_mapping.md`, `opheim_1991_projection_mapping.md`.

---

## Doc conventions

All five conventions from the predecessor mappings apply verbatim:

- Compendium row IDs are working names, not cluster-derived.
- Typed cells live on `MatrixCell.value` (v2.0 schema bump assumed).
- Granularity bias: split on every distinguishing case.
- Axes: `legal_availability` for de jure observables (statute-readable); `practical_availability` for de facto observables (observed agency / portal behavior). HG has many of each — Q1–Q27 are mostly legal; Q28–Q38 are mostly practical.
- **"Collect once, map to many."** Each row entry carries a `[cross-rubric: …]` annotation listing every other rubric that reads the same observable. HG is the seventh Phase B mapping; most annotated readers are well-established by now.

**HG 2007 is the LARGEST contributing rubric by item count (38 items in scope after enforcement and cooling-off exclusions; 47 items if those were included).** It is CPI's own predecessor — the 2007 Hired Guns scoring methodology produced the per-state rubric that the 2015 CPI SII C11 sub-category compresses to 14 questions. Many HG observables show up in CPI 2015 C11 at coarser granularity (e.g., HG Q11 + Q14 + Q15 fold into CPI IND_201's "detailed spending reports including itemized expenses"). HG's contribution to compendium 2.0 is therefore twofold:

1. **Fine-grained granularity on existing rows** — HG atomizes itemization detail (Q16–Q19), online-filing facets (Q28–Q30), and access-tier ordinals (Q31, Q32, Q38) finer than any other rubric in the contributing set. The cell types those rows carry must be rich enough for HG's projections.
2. **Genuinely HG-distinctive observables** — household-members coverage (Q21), business-associations disclosure (Q22), campaign-contribution disclosure (Q24, disclosure-side), null/no-activity report requirement (Q25), photograph-with-registration (Q8), aggregate-totals provision by agency (Q35–Q37). None of these are read by another rubric in the contributing set; they enter compendium 2.0 as HG-introduced rows.

**Net reuse: 16/38 in-scope items reuse pre-existing rows (~42%); 22 new rows proposed.** Lowest reuse rate of any Phase B mapping so far — predictable given HG's size and granularity advantage over later (shorter) rubrics.

## Watchpoint resolutions (per [handoff](../../plans/_handoffs/20260511_phase_b_continued_remaining_7.md) HG section)

1. **Q5 (reg form) vs Q20 (spending report) — canonical α split case.** APPLIED. Both items read the 6-row Sunlight α split (3 disclosure-detail levels × 2 form types). Q5 reads the reg-form-side rows at 3-tier (none / subject only / bill number); Q20 reads the spending-report-side rows at the same 3-tier. No new rows; reuses Sunlight's `lobbyist_reg_form_includes_*` × 3 and `lobbyist_spending_report_includes_*` × 3.

2. **Q11 (gateway) / Q14 (categorized) / Q15 (itemized + threshold magnitude) — canonical item-2 stack.** RESOLVED. Q15 reads two cells: the binary `lobbyist_spending_report_includes_itemized_expenses` AND the typed `expenditure_itemization_de_minimis_threshold_dollars` (Sunlight #3, finer at HG Q15's 5-tier ordinal on threshold magnitude).

3. **Q13 (lobbyist compensation) / Q27 (principal compensation).** APPLIED. Q13 reuses Sunlight #5's `lobbyist_spending_report_includes_total_compensation` (+ footnote: also reads `lobbyist_reg_form_includes_compensation` via OR). Q27 reuses PRI E1f_i's `principal_report_includes_direct_compensation`. CPI #201 reads these at compound granularity.

4. **Q2 (5-tier ordinal on lobbyist-status threshold).** APPLIED. Reads CPI #197's typed cell `compensation_threshold_for_lobbyist_registration` at finer granularity than Newmark/Opheim's binary `IS NOT NULL` reads. The 5-tier projection is a function of the threshold dollar value.

5. **Q39–Q47 (enforcement) and Q48 (cooling-off) OUT.** EXCLUDED per disclosure-only Phase B qualifier (10 items × 50 states = 500 ground-truth cells parked for later). See scope qualifier table below.

6. **`contributions_from_others` parallel in HG.** WALKED. HG has no item parallel to Newmark 2017's `lobbyist_or_principal_report_includes_contributions_received_for_lobbying`. The closest concept-adjacent items are Q13 (lobbyist compensation — what the lobbyist is *paid by* the principal/client) and Q24 (campaign contributions *to officials* — disclosure of contributions flowing OUT FROM lobbyist, not INTO lobbyist/principal). HG Q24 is the *outgoing* mirror, not the third-party-contributions-IN observable Newmark 2017 reads. **Result: `lobbyist_or_principal_report_includes_contributions_received_for_lobbying` remains single-rubric across 7 of 9 contributing rubrics now (CPI, PRI, Sunlight, Newmark 2005, Newmark 2017, Opheim, HG; OpenSecrets tabled).** Remaining promotion checks: FOCAL `financials.*` battery and LobbyView schema fields. If both fail, the row is single-rubric across the entire contributing set — that becomes a compendium 2.0 freeze question (real Newmark-distinctive observable, or over-atomization?).

7. **`def_actor_class_*` row family.** Per the handoff: "no longer in question — row family is 3-rubric-confirmed and Open Issue 1 is resolved-in-principle." HG Q3 ("Is a lobbyist required to file a registration form?") is a registration-gateway question, not an actor-class question; HG does not have items reading `def_actor_class_elected_officials` or `def_actor_class_public_employees` as distinct observables. **HG is not a 4th reader.** Confirmed by walking Q1–Q10 — none asks whether elected officials or public employees fall under the lobbyist definition; HG's Q1–Q2 atomize *target* coverage (executive branch lobbying) and the lobbyist-status threshold, not actor-class membership.

## Scope qualifier — 10 items OUT

Per the plan's disclosure-only Phase B qualifier:

| Excluded items | Reason | Re-entry scope |
|---|---|---|
| Q39 (statutory auditing authority) | Enforcement — agency authority observable | Enforcement round (deferred) |
| Q40 (mandatory reviews/audits) | Enforcement — agency-action observable | Enforcement round (deferred) |
| Q41 (penalty for late reg form) | Enforcement — statutory-penalty observable | Enforcement round (deferred) |
| Q42 (penalty for late spending report) | Enforcement | Enforcement round (deferred) |
| Q43 (when penalty last levied — late) | Enforcement; agency-self-report-only data | Enforcement round (deferred) |
| Q44 (penalty for incomplete reg form) | Enforcement | Enforcement round (deferred) |
| Q45 (penalty for incomplete spending report) | Enforcement | Enforcement round (deferred) |
| Q46 (when penalty last levied — incomplete) | Enforcement; agency-self-report-only data | Enforcement round (deferred) |
| Q47 (list of delinquent filers published) | Enforcement / public-shaming | Enforcement round (deferred) |
| Q48 (cooling-off period for legislators-to-lobbyists) | Revolving-door prohibition | Prohibitions round (deferred) |

10 items × 50 states × 1 vintage (2007, reference year 2002 for some Q35–Q37 trio sub-items) = up to 500 ground-truth cells parked for later, not lost.

**Implication for index reproducibility:** With 10 items × ~20 points (per category totals: Enforcement = 15, Revolving Door = 2 — total 17 of HG's 100) excluded, this projection **cannot reproduce HG's published 100-point composite**. It CAN reproduce the 83-point disclosure-side portion (Definition of Lobbyist 7 + Individual Registration 19 + Individual Spending Disclosure 29 + Employer Spending Disclosure 5 + Electronic Filing 3 + Public Access 20 = 83). Phase C validation can use the 83-point disclosure-side partial against CPI's published per-state HG totals (subtract the published per-state enforcement+revolving-door points if those are separately reported; otherwise validate the partial as `our_disclosure_partial ≤ published_total` weak inequality).

## Aggregation rule

HG's published structure (`items_HiredGuns.md` §2 + CPI methodology lines 17–18):

- `index.total = sum of 48 atomic items` (0–100; raw sum, no weighting beyond the per-item point values declared in `scoring_rule` columns)
- Per-category maxima sum to 100 exactly: Def 7 + IndReg 19 + IndSpending 29 + EmpSpending 5 + EFiling 3 + PubAccess 20 + Enforcement 15 + RevolvingDoor 2 = 100
- Bands: ≥70 "satisfactory", 60–69 "marginal", <60 "failing" (CPI does not use letter grades)

Phase C `project_hired_guns_2007_disclosure_side(state, 2007)` produces:

```
def.section_total          = sum of Q1..Q2  per-item projections  ∈ [0, 7]
ind_reg.section_total      = sum of Q3..Q10 per-item projections  ∈ [0, 19]
ind_spending.section_total = sum of Q11..Q25 per-item projections ∈ [0, 29]
emp_spending.section_total = sum of Q26..Q27 per-item projections ∈ [0, 5]
e_filing.section_total     = sum of Q28..Q30 per-item projections ∈ [0, 3]
pub_access.section_total   = sum of Q31..Q38 per-item projections ∈ [0, 20]

disclosure_partial         = def + ind_reg + ind_spending + emp_spending + e_filing + pub_access
                                                                          ∈ [0, 83]
```

The 10 OOS items (`enforce.*` 9 + `revolving_door.*` 1) are **not produced** (treated as `unable_to_evaluate`, same convention as Opheim's catch-all). Maximum reproducible partial = **83/100**.

## Per-state per-indicator data

**HG 2007 publishes per-state per-question data** in the original CPI report and methodology (per `items_HiredGuns.md` §6: "Center researchers developed 48 questions, and sought answers for them by studying statutes and interviewing officials in charge of lobbying agencies in each state"). The per-state per-question data was historically available on CPI's website; current availability depends on whether the 2007 scorecard pages are still hosted at publicintegrity.org/politics/state-politics/influence/hired-guns/. **Per-state per-question data has NOT been retrieved into this branch's data archive** — only the methodology TSV (48 atomic items in `items_HiredGuns.tsv`) is in the corpus.

**Practical consequence for Phase C:**

- Per-atomic-item validation against HG's published data requires a separate retrieval step to pull the per-state per-question scorecard. If retrievable: 50 states × 38 in-scope items = **1,900 per-cell ground-truth values** for Phase C — the second-largest ground-truth set in the contributing-rubric set, behind PRI 2010 (50 × 83 = 4,150 cells).
- Per-section-total validation: 50 states × 6 in-scope sub-aggregates = 300 cells (if scorecard publishes sub-aggregates; methodology doc doesn't confirm).
- Per-state overall total validation: 50 states × 1 total = 50 cells; weak inequality `our_disclosure_partial ≤ published_total - 17` (where 17 = max enforcement + revolving-door contribution).
- **Cross-rubric validation remains the dominant check.** HG's BoS-and-statute-sourced atomic items overlap heavily with PRI 2010 per-item per-state data, CPI 2015 C11 per-state data (compressed CPI 2015 is HG's successor at coarser granularity — direct cross-rubric stability check on rows both read), Newmark/Sunlight per-item data.

**HG-distinctive caveat:** Q40, Q43, Q46 (all enforcement, all OOS), Q35–Q37 (aggregate-totals provision), and Q30 (e-filing training) are statutorily-informed-but-agency-self-report-derived per `items_HiredGuns.md` §6 ("Items whose operational definition relies primarily on the fallback (interview) source"). These are intrinsically practical-availability cells; statute-extraction alone won't populate them.

**Distribution context** (from `items_HiredGuns.md` §2 + CPI methodology line 28):

| Vintage | Headline observation |
|---|---|
| 2007 (reference year 2002 for Q35-Q37) | "Only one state scored an 80 or above" (line 28). Most states clustered in the marginal-to-failing range (60s and below). |

## Phase C validation

50 states × 1 vintage (2007) × 38 in-scope items = up to **1,900 per-cell ground-truth values** for Phase C, contingent on retrieving CPI's per-state per-question scorecard (not currently in branch archive — see "Per-state per-indicator data" above).

Federal LDA out of scope (HG is state-only). HG predates the federal HLOGA-2007 amendments to LDA but the federal LDA itself is older than HG; HG simply doesn't extend to federal jurisdiction.

---

## Structural delta from CPI 2015 C11 (HG is CPI's direct predecessor)

CPI's 2015 SII C11 sub-category (14 atomic items) is the explicit compression of HG's 48-item 2007 scorecard. The compression rules:

| HG 2007 (atomized) | CPI 2015 C11 (compressed) | Net effect on compendium rows |
|---|---|---|
| Q1 (executive-branch recognized) + Q2 (compensation threshold 5-tier) | IND_196 (def includes executive officials + governor's office) + IND_197 (compensation threshold ≥0) | Same row family; CPI atomizes the target side (governor's office vs executive agency) finer; HG atomizes the threshold magnitude finer. |
| Q3 (lobbyist reg required) + Q6 (cadence) + Q11 (spending report required) + Q14 (categorized) + Q15 (itemized + threshold) + Q13 (compensation) | IND_198 (lobbyist actually registers) + IND_199 (annual reg cadence) + IND_201 (detailed spending reports incl compensation, itemized) + IND_202 (detailed spending reports filed with reasonable frequency) | CPI compresses 6 HG items to 4 CPI items by bundling "detailed spending reports" as one compound observable (HG separates the components). |
| Q5 + Q20 (subject/bill on reg form / spending report) | (no direct CPI 2015 read at this granularity) | HG-distinctive granularity preserved via Sunlight's α form-type split; the underlying cells are read by Sunlight #1, HG Q5/Q20, FOCAL contact_log.11, PRI E1g_ii/E2g_ii. |
| Q26–Q27 (principal/employer spending report) | IND_203 (principal spending report required) + IND_204 (principal spending report includes compensation) | Direct parallel; same row family. |
| Q28–Q38 (electronic filing + public access) | IND_205 (citizens access disclosure documents) + IND_206 (open data format) | CPI compresses 11 HG items into 2 CPI items (both practical-availability). HG's 4-tier ordinals (Q31, Q32, Q38) and binary facets (Q28–Q30, Q33–Q37) provide the finer underlying cells; CPI 2015 reads them at compound granularity. |
| Q39–Q47 (enforcement) | IND_207–IND_209 (audit + penalty) | Both rubrics' enforcement batteries are OOS for disclosure-only Phase B. |
| Q48 (cooling-off) | (CPI 2015 C11 has no cooling-off item) | OOS for disclosure-only Phase B. |

**Net for Phase B:** HG provides the cell-level granularity the CPI 2015 C11 compound items implicitly aggregate. Where CPI 2015 reads "detailed spending reports including compensation/salary, employer name, lobbied issues, bill numbers" as ONE compound observable (IND_201), HG reads the same observables across 5 separate atomic items (Q11 + Q13 + Q14 + Q15 + Q20 + Q9). Compendium 2.0 should preserve HG's finer atomization — CPI 2015's compound reads can roll up via AND-projection over the underlying cells.

---

## Per-item mappings

### Definition of Lobbyist (Q1–Q2; max 7 points)

#### hg_2007.Q1 — Executive-branch lobbyists recognized in lobbyist definition (3 pts)

- **Compendium rows:** `def_target_executive_agency` (binary; legal) AND `def_target_governors_office` (binary; legal)
  [cross-rubric: CPI #196 (compound — both target rows are reads of IND_196); Newmark 2017 `def.administrative_agency_lobbying`; Newmark 2005 `def_administrative_agency_lobbying`; Opheim `def.administrative_lobbying`; FOCAL `scope.3`]
  Already in CPI mapping; pre-existing rows.
- **Cell type:** binary per row.
- **Axis:** `legal_availability`.
- **Scoring rule:** `(def_target_executive_agency OR def_target_governors_office) AND NOT legislative_only_carve_out → 3; else → 0`.
- **Source quote:** "1. In addition to legislative lobbyists, does the deﬁnition recognize executive branch lobbyists? No – 0 points Yes – 3 points" (CPI_2007__hired_guns_methodology.txt:32).
- **Note on the "legislative-only carve-out" caveat:** Per the HG notes column: "States did not receive points for including executive communication in the deﬁnition only when it directly related to legislative action." Recognition must be standalone, not derivative of legislative-action recognition. This is a HG-specific scoring nuance that the existing CPI `def_target_executive_agency` row carries: if the cell is TRUE based on a "lobbying executive officials counts when discussing pending legislation" clause, HG would code 0 even though CPI #196 might code YES. **Granularity-bias question for compendium 2.0 freeze:** should `def_target_executive_agency` be split into `def_target_executive_agency_standalone` vs `def_target_executive_agency_only_re_pending_legislation`? Flagging as Open Issue HG-1.

#### hg_2007.Q2 — Compensation threshold for lobbyist registration (5-tier ordinal; max 4 pts)

- **Compendium rows:** `compensation_threshold_for_lobbyist_registration` (typed `Optional[Decimal]`; legal)
  [cross-rubric: CPI #197 (3-tier read: none/threshold/zero); Newmark 2017 `def.compensation_standard` (binary `IS NOT NULL`); Newmark 2005 `def_compensation_standard`; Opheim `def.compensation_standard`; FOCAL `scope.2`]
  Already in CPI mapping; pre-existing typed cell.
- **Cell type:** `Optional[Decimal]` representing the compensation dollar threshold above which the lobbyist-definition triggers.
- **Axis:** `legal_availability`.
- **Scoring rule:**
  ```
  threshold == NULL  (no threshold; any compensation triggers registration)  → 4
  threshold ≤ 50                                                              → 3
  50 < threshold ≤ 100                                                        → 2
  100 < threshold ≤ 500                                                       → 1
  threshold > 500                                                             → 0
  ```
  HG's 5-tier ordinal is the finest reading of this cell in the contributing-rubric set. CPI #197 reads at 3-tier; Newmark/Opheim read at binary `IS NOT NULL`. Same cell, three different projection granularities — exactly the typed-cell pattern locked in CPI mapping.
- **Source quote:** "2. How much does an individual have to make/spend to qualify as a lobbyist or to prompt registration as a lobbyist, according to the deﬁnition? Qualiﬁcation threshold: More than $500 made/spent – 0 points; More than $100 made/spent – 1 point; More than $50 made/spent – 2 points; $50 or less made/spent – 3 points; Lobbyists qualify and must register no matter how much money made/spent – 4 points" (CPI_2007__hired_guns_methodology.txt:44).
- **Note on threshold-concept distinction:** This is the lobbyist-status threshold (one of five distinct threshold concepts per the handoff). Not to be confused with filing-de-minimis (PRI D1), itemization-de-minimis (Sunlight #3 / HG Q15), expenditure-threshold-for-lobbyist-status (Newmark `def.expenditure_standard` — a *separate* typed cell), or time-threshold-for-lobbyist-status (Newmark `def.time_standard`).
- **Note on "make/spend" phrasing:** HG's source wording is "make/spend", suggesting the threshold may be on either compensation received OR expenditures made. The strict reading: `compensation_threshold_for_lobbyist_registration` reads the *compensation* arm; if a state uses an *expenditure* threshold instead, that's `expenditure_threshold_for_lobbyist_registration` (Newmark 2017 row). HG's Q2 is ambiguous between the two — practical interpretation: read `compensation_threshold OR expenditure_threshold` (treat as OR over the two typed cells, with the 5-tier projection applied to whichever is non-null; if both, take the smaller). Flagging as Open Issue HG-2 for compendium 2.0 freeze if this affects projection-vs-published-data results.

### Individual Registration (Q3–Q10; max 19 points)

#### hg_2007.Q3 — Lobbyist required to file registration form (3 pts)

- **Compendium rows:** `lobbyist_registration_required` (binary; legal)
  [cross-rubric: CPI #198 (compound — legal axis read of "lobbyists are required to file registration forms"; CPI's #198 also adds a practical-axis "all paid lobbyists actually register"); PRI A actor-side (parallel-but-not-identical observable — PRI A is institutional-actor-class; this row is the meta-gate "do any lobbyists need to register")]
  Already in CPI mapping; pre-existing.
- **Cell type:** binary.
- **Axis:** `legal_availability`.
- **Scoring rule:** `cell == TRUE → 3; else → 0`.
- **Source quote:** "3. Is a lobbyist required to ﬁle a registration form? No – 0 points Yes – 3 points" (CPI_2007__hired_guns_methodology.txt:64).
- **Note:** Empirically TRUE for all 50 states by 2007 (no state in the HG cycle lacked any registration requirement). Like Newmark 2017's no-variation items, the cell is still extracted state-by-state — the saturation is a vintage-empirical observation, not a design claim.

#### hg_2007.Q4 — Registration deadline: days lobbying may take place before registration required (5-tier; max 4 pts)

- **Compendium rows:** `registration_deadline_days_after_first_lobbying` (typed `int`; legal)
  [cross-rubric: CPI #200 (de-jure pair carrying the day-count; CPI also reads the practical-availability axis); FOCAL `scope.4` partial reading (FOCAL bundles many activity scope criteria); HG Q7 reads the *amendment* deadline, NOT this one (Q4 is initial registration; Q7 is post-registration changes)]
  Already in CPI mapping; pre-existing typed cell.
- **Cell type:** typed `Optional[int]` representing days after first lobbying activity by which registration must be filed. `None` = no registration requirement (effectively infinite); `0` = same day / before lobbying begins.
- **Axis:** `legal_availability`.
- **Scoring rule:**
  ```
  days == 0   → 4
  1 ≤ days ≤ 5   → 3
  6 ≤ days ≤ 10  → 2
  11 ≤ days ≤ 15 → 1
  days ≥ 16 OR days IS NULL → 0
  ```
- **Source quote:** "4. How many days can lobbying take place before registration is required? 16 or more days – 0 points; 11 to 15 days – 1 point; 6 to 10 days – 2 points; 1 to 5 days – 3 points; 0 days – 4 points" (CPI_2007__hired_guns_methodology.txt:68).

#### hg_2007.Q5 — Subject matter or bill number on registration forms (3-tier categorical; max 3 pts)

- **Compendium rows:**
  - `lobbyist_reg_form_includes_general_subject_matter` (binary; legal)
  - `lobbyist_reg_form_includes_bill_or_action_identifier` (binary; legal)

  [cross-rubric: Sunlight #1 (α form-type split — the reg-form-side trio of rows); FOCAL `contact_log.11` (when statute requires bill numbers on reg form — uncommon; usually FOCAL reads the spending-report side); HG Q20 mirror (spending-report side)]
  Already in Sunlight mapping; pre-existing pair of rows.
- **Cell type:** binary per row.
- **Axis:** `legal_availability`.
- **Scoring rule:**
  ```
  bill_or_action_identifier == TRUE  → 3
  general_subject_matter == TRUE AND bill_or_action_identifier == FALSE  → 1
  general_subject_matter == FALSE AND bill_or_action_identifier == FALSE  → 0
  ```
- **Source quote:** "5. Is subject matter or bill number to be addressed by a lobbyist required on registration forms? No bill number/subject matter required – 0 points; Subject matter only required – 1 point; Bill number required – 3 points" (CPI_2007__hired_guns_methodology.txt:75).
- **Note on the canonical α split case:** Q5/Q20 are the original motivating case for the form-type split (a state can require bill number on the spending report but not the reg form — empirically extant across states). Reuses Sunlight's split exactly; no new rows.

#### hg_2007.Q6 — Lobbyist registration cadence (3-tier ordinal; max 2 pts)

- **Compendium rows:** `lobbyist_registration_renewal_cadence` (typed `Optional[int_months]` or enum; legal)
  [cross-rubric: CPI #199 (reads `annual_or_more_frequent` as YES, biennial as MODERATE, no-registration as NO); FOCAL `timeliness.1` (related but reads update cadence of the register, not lobbyist-renewal cadence); HG Q4 (registration deadline, distinct from cadence)]
  Already in CPI mapping; pre-existing typed cell.
- **Cell type:** `Optional[int_months]` representing renewal period in months. Common values: 12 (annual), 24 (biennial), `None` (no renewal required or one-time registration).
- **Axis:** `legal_availability`.
- **Scoring rule:**
  ```
  cadence IS NULL  (registration is once only, never renewed) → 0
  cadence == 24  (biennial)                                    → 1
  cadence ≤ 12  (annual or more frequent)                      → 2
  ```
- **Source quote:** "6. How often is registration by a lobbyist required? Once only – 0 points; Every two years – 1 point; Annually or more often – 2 points" (CPI_2007__hired_guns_methodology.txt:84).
- **Note on "includes regular supplements/refilings":** HG notes column says "Includes regular supplements/refilings." If a state has a one-time registration plus mandatory supplements every N months, treat supplements as renewals for projection purposes (cadence = N).

#### hg_2007.Q7 — Registration-amendment deadline: days to notify of changes (5-tier; max 4 pts)

- **Compendium rows:** `lobbyist_registration_amendment_deadline_days` (typed `Optional[int]`; legal) **NEW**
  [cross-rubric: no current reader. Probably future-FOCAL read at finer granularity; HG-distinctive in the current contributing set.]
- **Cell type:** typed `Optional[int]` representing days after a change in registration information by which the amendment must be filed. `None` = no amendment requirement.
- **Axis:** `legal_availability`.
- **Scoring rule:**
  ```
  days == 0   → 4
  1 ≤ days ≤ 5   → 3
  6 ≤ days ≤ 10  → 2
  11 ≤ days ≤ 15 → 1
  days ≥ 16 OR days IS NULL → 0
  ```
  Same 5-tier shape as Q4 — but distinct cell (Q4 is INITIAL registration deadline; Q7 is amendment-after-change deadline).
- **Source quote:** "7. Within how many days must a lobbyist notify the oversight agency of changes in registration?" (CPI_2007__hired_guns_methodology.txt:94).
- **Note on row design — separate from Q4:** Granularity bias says split. A state could require initial registration within 5 days (Q4 = 3 pts) but allow 30 days for amendments (Q7 = 0 pts). Empirically these tend to diverge — initial registration deadlines tend to be stricter than amendment deadlines.

#### hg_2007.Q8 — Photograph required with registration (1 pt)

- **Compendium rows:** `lobbyist_required_to_submit_photograph_with_registration` (binary; legal) **NEW**
  [cross-rubric: no current reader. HG-distinctive in the contributing set. Practical-availability axis would be "does the state actually produce identification badges from these photos" (HG notes: "Pertains to identification badges").]
- **Cell type:** binary.
- **Axis:** `legal_availability`.
- **Scoring rule:** `cell == TRUE → 1; else → 0`.
- **Source quote:** "8. Is a lobbyist required to submit a photograph with registration? No – 0 points Yes – 1 point" (CPI_2007__hired_guns_methodology.txt:101).
- **Note:** Empirically a minority observable in 2007 — most states don't require photos. Real (some states do produce lobbyist ID badges with photo). This row is one of the cleanest HG-distinctive observables.

#### hg_2007.Q9 — Reg form identifies each employer/principal by name (1 pt)

- **Compendium rows:** `lobbyist_reg_form_lists_each_employer_or_principal` (binary; legal) **NEW**
  [cross-rubric: PRI E2c (`lobbyist_report_includes_principal_names` — but that's on the SPENDING REPORT side, not reg form); FOCAL `relationships.1` ("Client list for all consultant lobbyists and firms" — captures the same observable but doesn't restrict to which form); HG Q9 is reg-form-side specifically]
- **Cell type:** binary.
- **Axis:** `legal_availability`.
- **Scoring rule:** `cell == TRUE → 1; else → 0`.
- **Source quote:** "9. Is a lobbyist required to identify by name each employer on the registration form? No – 0 points Yes – 1point" (CPI_2007__hired_guns_methodology.txt:108).
- **Note on row design — form-side α split repeats here:** HG's notes say "Either single-form-multi-employer or per-employer-registration counts as full points." This means HG accepts either (a) one reg form listing all employers OR (b) separate reg forms per employer. Both indicate the same cell value (employers are listed on the reg). The α split principle says we should also have a parallel row `lobbyist_spending_report_includes_principal_names` (PRI E2c, already exists). Q9 reads the reg-form-side row only. Open Issue HG-3: should HG's Q9 OR-project over reg-form + spending-report cells per the footnote's location flexibility? Strict reading is reg-form-only.

#### hg_2007.Q10 — Reg form includes lobbying-work type (compensated/non-compensated/contract/salaried) (1 pt)

- **Compendium rows:** `lobbyist_disclosure_includes_employment_type` (binary; legal) **NEW**
  [cross-rubric: FOCAL `descriptors.6` ("Type of lobbyist contract (eg, salaried staff, contracted)" — verbatim parallel); LobbyView (Federal LDA distinguishes lobbying firms vs in-house filers — analogous schema field)]
- **Cell type:** binary.
- **Axis:** `legal_availability`.
- **Scoring rule:** `cell == TRUE → 1; else → 0`.
- **Source quote:** "10. Is a lobbyist required to include on the registration form any additional information about the type of lobbying work he or she does (i.e., compensated or non-compensated/contract or salaried)?" (CPI_2007__hired_guns_methodology.txt:120).
- **Note on form-location flexibility:** HG notes "Full points if info appears on spending reports rather than registration; CPI relaxes the location." So the projection is OR over reg-form + spending-report cells. Per the locked α convention, this could be split into `lobbyist_reg_form_includes_employment_type` + `lobbyist_spending_report_includes_employment_type` (two cells); HG reads the OR. **Cell-naming convention here:** since HG's Q10 explicitly accepts either form, and the cross-rubric reader (FOCAL `descriptors.6`) is also form-agnostic, I'm proposing a SINGLE form-agnostic cell `lobbyist_disclosure_includes_employment_type` to match the consensus reading. Splitting into reg/spending pair is not necessary unless a future rubric reads location-specifically — flagging as Open Issue HG-4.

### Individual Spending Disclosure (Q11–Q25; max 29 points)

#### hg_2007.Q11 — Lobbyist spending report required (gateway; 3 pts)

- **Compendium rows:** `lobbyist_spending_report_required` (binary; legal)
  [cross-rubric: Sunlight #2 tier 0+ (gateway); CPI #201 (compound); Newmark 2017 `disclosure.total_expenditures` (gateway implicit); PRI E2-family entire principal-side battery (gateway implicit); Opheim `disclosure.total_spending` (gateway implicit)]
  Already in Sunlight mapping; pre-existing.
- **Cell type:** binary.
- **Axis:** `legal_availability`.
- **Scoring rule:** `cell == TRUE → 3; else → 0`.
- **Source quote:** "11. Is a lobbyist required to ﬁle a spending report? No – 0 points Yes – 3 points" (CPI_2007__hired_guns_methodology.txt:131).
- **Note:** Empirically TRUE for all states by 2007. Gateway question — `cell == FALSE` should imply Q12–Q25 all score 0 (HG doesn't say this explicitly but it's implied — a state with no spending-report requirement can't have a categorized / itemized / threshold / etc. spending report).

#### hg_2007.Q12 — Filings per 2-year cycle (4-tier ordinal derived from cadence; max 3 pts)

- **Compendium rows:** derived from `lobbyist_report_cadence_includes_monthly` + `_quarterly` + `_triannual` + `_semiannual` + `_annual` + `_other` (binary × 6; legal) AND `state_legislative_session_calendar` (typed metadata; legal)
  [cross-rubric: PRI E2h_* (6-binary canonical cadence atomization); Newmark 2005 `freq_reporting_more_than_annual` (8-cell OR over the 6-binary lobbyist-side + 2-binary principal-side); Opheim `disclosure.frequency` (2-cell OR — monthly only); CPI #202 (enum derived); FOCAL `timeliness.*`]
  Cadence binaries already in PRI mapping; pre-existing. **State legislative session calendar is a NEW metadata cell** — see note below.
- **Cell type:** projection only — derived from the 6 cadence binaries + session-calendar metadata.
- **Axis:** `legal_availability`.
- **Scoring rule:**
  ```
  filings_per_2yr_cycle = max_implied_filings_per_2yr(cadence_binaries, session_calendar)

  filings_per_2yr_cycle ≥ 10  → 3
  7 ≤ filings_per_2yr_cycle ≤ 9   → 2
  4 ≤ filings_per_2yr_cycle ≤ 6   → 1
  0 ≤ filings_per_2yr_cycle ≤ 3   → 0
  ```
  Where `max_implied_filings_per_2yr` maps cadence flags to a count:
  - `monthly` (year-round) → 24
  - `monthly during session` (e.g., 4-month session) → 8 (4 mo × 2 sessions)
  - `quarterly` → 8
  - `triannual` → 6 (3× per year × 2)
  - `semiannual` → 4
  - `annual` → 2
  - `other` → free-text inspection required

  If multiple cadence binaries are TRUE, take the largest implied count (HG's projection wants "how often might the state require filings").
- **Source quote:** "12. How often during each two-year cycle is a lobbyist required to report spending? 0 – 3 ﬁlings – 0 points; 4 – 6 ﬁlings – 1 point; 7 – 9 ﬁlings – 2 points; 10 – or more ﬁlings – 3 points" (CPI_2007__hired_guns_methodology.txt:136).
- **Note on the worked example (HG notes column):** "Two-year cycle accommodates biennial legislatures; CPI gives a worked example for a 4-month-session state." A 4-month-session state with monthly-during-session filing = 4 mo × 2 sessions = 8 filings = 2 points. The session-length information IS NECESSARY to make Q12 deterministic from the cadence binaries alone — proposing a new metadata cell `state_legislative_session_calendar` typed as `{session_length_months: int, sessions_per_two_years: int, in_session_filing_cadence: enum, out_of_session_filing_cadence: enum}`. Alternative: a single derived cell `lobbyist_spending_reports_implied_per_2yr_cycle: int` that statute-extraction populates directly from the statutory text. The latter is YAGNI-cleaner; the former is more reusable. **Flagging as Open Issue HG-5** — the cleanest YAGNI cell for compendium 2.0 is a typed-int `lobbyist_spending_reports_implied_per_2yr_cycle` populated by extraction, which the HG Q12 projection then bucket-maps to the 4-tier ordinal.
- **Note on alternative — direct typed cell:** Could short-circuit by having compendium carry `lobbyist_spending_reports_per_two_year_cycle: int` directly. Newmark 2005's `freq_reporting_more_than_annual` and Opheim's `disclosure.frequency` are already derived from the binaries; adding HG Q12 as a third derivative is consistent. Decision deferred to compendium 2.0 freeze; for projection-mapping purposes here, treat HG Q12 as derived from the existing PRI cadence family with session-calendar metadata.

#### hg_2007.Q13 — Lobbyist compensation on spending report (2 pts)

- **Compendium rows:** `lobbyist_spending_report_includes_total_compensation` (binary; legal) AND/OR `lobbyist_reg_form_includes_compensation` (binary; legal)
  [cross-rubric (spending-report side): Sunlight #5 (total-compensation row); Newmark 2017 `disclosure.total_compensation`; Newmark 2005 `disc_total_compensation`; CPI #201 (compound); PRI E2f_i; Opheim `disclosure.total_income`]
  [cross-rubric (reg-form-side fallback): Sunlight #5 (`lobbyist_reg_form_includes_compensation`)]
  Already in Sunlight mapping; pre-existing pair.
- **Cell type:** binary per row.
- **Axis:** `legal_availability`.
- **Scoring rule:** `(lobbyist_spending_report_includes_total_compensation OR lobbyist_reg_form_includes_compensation) → 2; else → 0`.
- **Source quote:** "13. Is compensation/salary required to be reported by a lobbyist on spending reports? No – 0 points Yes – 2 points" (CPI_2007__hired_guns_methodology.txt:151).
- **Note on location flexibility:** HG notes "Full points if information is on registration form instead." OR-projection across the two form-locations matches HG's intent. Same form-location flexibility as Q10. This row is now 5-rubric-confirmed (Sunlight + Newmark 2017 + Newmark 2005 + Opheim + HG; plus PRI E2f_i, CPI #201 — 7 readers in total) — second-most-validated row in the compendium going into FOCAL mapping after `lobbyist_spending_report_includes_total_compensation` itself.

#### hg_2007.Q14 — Categorized totals of spending (gifts/entertainment/postage/etc.) (2 pts)

- **Compendium rows:** `lobbyist_spending_report_categorizes_expenses_by_type` (binary; legal)
  [cross-rubric: Sunlight #2 categorized-tier; Newmark 2017 `disclosure.categories_of_expenditures`; Newmark 2005 `disc_categories_of_expenditures`; Opheim `disclosure.spending_by_category`; FOCAL `financials.*` battery]
  Already in Sunlight mapping; pre-existing.
- **Cell type:** binary.
- **Axis:** `legal_availability`.
- **Scoring rule:** `cell == TRUE → 2; else → 0`.
- **Source quote:** "14. Are summaries (totals) of spending classiﬁed by category types (i.e., gifts, entertainment, postage, etc.)? No – 0 points Yes – 2 points" (CPI_2007__hired_guns_methodology.txt:158).
- **Note:** "Single aggregate total without category breakdown = 0 points" per HG notes. Row is now 5-rubric-confirmed (Sunlight + Newmark 2017 + Newmark 2005 + Opheim + HG; plus FOCAL implicit).

#### hg_2007.Q15 — What spending must be itemized? (5-tier ordinal on threshold magnitude; max 4 pts)

- **Compendium rows:**
  - `lobbyist_spending_report_includes_itemized_expenses` (binary; legal)
  - `expenditure_itemization_de_minimis_threshold_dollars` (typed `Optional[Decimal]`; legal)

  [cross-rubric: Sunlight #2 tier 2 (`includes_itemized_expenses`); Sunlight #3 (`expenditure_itemization_de_minimis_threshold_dollars` at 2-tier ordinal); CPI #201 (compound); PRI E1f_iv / E2f_iv (`uses_itemized_format`); Newmark 2017 implicit; FOCAL `financials.6` ("individual entries")]
  Both already in CPI/Sunlight mappings; pre-existing.
- **Cell type:** binary + typed `Optional[Decimal]`.
- **Axis:** `legal_availability`.
- **Scoring rule:**
  ```
  itemized == FALSE OR threshold > 500           → 0   (no itemization OR threshold above $500)
  itemized == TRUE AND 100 < threshold ≤ 500    → 1
  itemized == TRUE AND 25 < threshold ≤ 100     → 2
  itemized == TRUE AND 0 < threshold ≤ 25       → 3
  itemized == TRUE AND threshold IS NULL OR == 0 → 4   (all spending itemized regardless of amount)
  ```
  HG's 5-tier ordinal is the FINEST reading of the itemization-de-minimis threshold in the contributing set. Sunlight #3 reads it at 2-tier (presence/absence); HG reads at 5-tier.
- **Source quote:** "15. What spending must be itemized? No spending required to be itemized – 0 points; Itemization threshold: More than $100 – 1 point; Itemization threshold: More than $25 – 2 points; Itemization threshold: $25 and below – 3 points; All spending required to be itemized – 4 points" (CPI_2007__hired_guns_methodology.txt:165).
- **Note on threshold-concept distinction:** This is the **itemization-de-minimis threshold** (one of five distinct threshold concepts; see Sunlight mapping CRITICAL distinction block). Not the lobbyist-status threshold (Q2 / CPI #197) or the filing-de-minimis threshold (PRI D1).

#### hg_2007.Q16 — Itemized expenditure identifies employer/principal (conditional on Q15; 1 pt)

- **Compendium rows:** `lobbyist_itemized_expenditure_identifies_employer_or_principal` (binary; legal) **NEW**
  [cross-rubric: no current reader. HG-distinctive at this itemized-detail granularity.]
- **Cell type:** binary.
- **Axis:** `legal_availability`.
- **Scoring rule:** `(lobbyist_spending_report_includes_itemized_expenses == TRUE) AND (cell == TRUE) → 1; else → 0`. Conditional on Q15 — "If spending is not required to be itemized, a state received no points" (HG notes).
- **Source quote:** "16. Is the lobbyist employer/principal on whose behalf the itemized expenditure was made required to be identiﬁed? No – 0 points Yes – 1 point" (CPI_2007__hired_guns_methodology.txt:180).
- **Note on row design:** HG atomizes per-line-item disclosure detail finer than any other rubric. The 4 cells (Q16–Q19) are about which fields each itemized line must include — distinct from "are itemized line items required at all" (Q15). Conditional-on-Q15 logic lives in the projection, not in the cell (cells carry the statutory state regardless of whether itemization is required).

#### hg_2007.Q17 — Itemized expenditure identifies recipient (conditional on Q15; 1 pt)

- **Compendium rows:** `lobbyist_itemized_expenditure_identifies_recipient` (binary; legal) **NEW**
  [cross-rubric: PRI E1f_iii / E2f_iii loose reading (the gifts/entertainment bundle implicitly identifies recipients in its column structure — but PRI atomizes at "is the bundle on the report?" granularity, not "is the recipient required to be itemized?"); HG-distinctive at this granularity]
- **Cell type:** binary.
- **Axis:** `legal_availability`.
- **Scoring rule:** Conditional on Q15 (same as Q16). `(itemized == TRUE) AND (cell == TRUE) → 1; else → 0`.
- **Source quote:** "17. Is the recipient of the itemized expenditure required to be identiﬁed? No – 0 points Yes – 1 point" (CPI_2007__hired_guns_methodology.txt:189).
- **Note on recipient scope (HG notes):** "Recipient = legislator/staff/family." This is the statutory definition the cell carries — which person(s) the itemized line must name. Distinct from Q21 (household members SCOPE — does the state require reporting of spending on household members at all). Q17 says "if you itemize, you must name the recipient"; Q21 says "spending on household members of officials is in-scope for reporting."

#### hg_2007.Q18 — Itemized expenditure includes date (conditional on Q15; 1 pt)

- **Compendium rows:** `lobbyist_itemized_expenditure_includes_date` (binary; legal) **NEW**
  [cross-rubric: FOCAL `timeliness.*` partial reading (FOCAL captures timing at the meta-level but not the per-line-item date); HG-distinctive at this granularity]
- **Cell type:** binary.
- **Axis:** `legal_availability`.
- **Scoring rule:** Conditional on Q15. `(itemized == TRUE) AND (cell == TRUE) → 1; else → 0`.
- **Source quote:** "18. Is the date of the itemized expenditure required to be reported? No – 0 points Yes – 1 point" (CPI_2007__hired_guns_methodology.txt:196).

#### hg_2007.Q19 — Itemized expenditure includes description (conditional on Q15; 1 pt)

- **Compendium rows:** `lobbyist_itemized_expenditure_includes_description` (binary; legal) **NEW**
  [cross-rubric: FOCAL `financials.6` ("individual entries") partial reading (FOCAL's financials.6 asks for itemized line items but doesn't atomize description as a separate field); HG-distinctive at this granularity]
- **Cell type:** binary.
- **Axis:** `legal_availability`.
- **Scoring rule:** Conditional on Q15. `(itemized == TRUE) AND (cell == TRUE) → 1; else → 0`.
- **Source quote:** "19. Is a description of the itemized expenditure required to be reported? No – 0 points Yes – 1 point" (CPI_2007__hired_guns_methodology.txt:202).
- **Note:** "Description or category (e.g., food/postage) qualifies" per HG notes. The cell reading captures whether the statute requires a free-text description OR a category code (either qualifies as YES). The FOCAL `financials.6` reader may want finer granularity; flagging as Open Issue HG-6 for compendium 2.0 freeze.

#### hg_2007.Q20 — Subject matter or bill number on spending reports (3-tier categorical; max 3 pts)

- **Compendium rows:**
  - `lobbyist_spending_report_includes_general_subject_matter` (binary; legal)
  - `lobbyist_spending_report_includes_bill_or_action_identifier` (binary; legal)

  [cross-rubric: Sunlight #1 spending-report-side rows; FOCAL `contact_log.11`; PRI E2g_i / E2g_ii; Newmark 2017 `disclosure.influence_legislation_or_admin` (reads only the general-subject-matter row); Newmark 2005 `disc_legislative_admin_action_to_influence`; Opheim `disclosure.legislation_supported_or_opposed` (reads the bill_id row via β AND with position)]
  Already in Sunlight mapping; pre-existing pair.
- **Cell type:** binary per row.
- **Axis:** `legal_availability`.
- **Scoring rule:**
  ```
  bill_or_action_identifier == TRUE  → 3
  general_subject_matter == TRUE AND bill_or_action_identifier == FALSE  → 1
  general_subject_matter == FALSE AND bill_or_action_identifier == FALSE  → 0
  ```
  Mirrors Q5 exactly but on the spending-report side. The α form-type split makes this distinct from Q5 — a state can require bill_id on spending reports without requiring it on the reg form.
- **Source quote:** "20. Is subject matter or bill number to be addressed by a lobbyist required on spending reports? No bill number/subject matter required – 0 points; Subject matter only required – 1 point; Bill number required – 3 points" (CPI_2007__hired_guns_methodology.txt:213).

#### hg_2007.Q21 — Spending on household members of officials required to be reported (1 pt)

- **Compendium rows:** `lobbyist_spending_report_scope_includes_household_members_of_officials` (binary; legal) **NEW**
  [cross-rubric: no current reader. HG-distinctive. Closest concept-adjacent: Newmark 2005 `prohib_solicitation_by_officials` (the inverse direction — officials soliciting from lobbyists, not lobbyists spending on officials' families); FOCAL `relationships.4` partial (captures business associations of officials but not family-side spending scope)]
- **Cell type:** binary.
- **Axis:** `legal_availability`.
- **Scoring rule:** `cell == TRUE → 1; else → 0`.
- **Source quote:** "21. Is spending on household members of public ofﬁcials by a lobbyist required to be reported? No – 0 points Yes – 1 point" (CPI_2007__hired_guns_methodology.txt:222).
- **Note on state-specific scope (HG notes):** "Implicit scope: depends on state's definition of household member." The cell reading is whether the statute *includes household-member spending in the reporting scope*; the underlying definition of "household member" varies (some states limit to spouse + minor children; some include domestic partners + adult dependents; etc.). Compendium 2.0 may want a companion `state_definition_of_household_member` free-text cell to capture variation; YAGNI says no until a rubric reads it.

#### hg_2007.Q22 — Direct business associations with officials/candidates/household members (1 pt)

- **Compendium rows:** `lobbyist_disclosure_includes_business_associations_with_officials` (binary; legal) **NEW**
  [cross-rubric: FOCAL `relationships.4` ("Personal or professional relationships of lobbyists/officials/etc with politicians or officials" — verbatim adjacent, possibly the same observable at FOCAL granularity); LobbyView lobbyist_demographics (Kim 2025 enrichment — federal-side network analysis of revolving-door connections, related but not the same observable as state disclosure)]
- **Cell type:** binary.
- **Axis:** `legal_availability`.
- **Scoring rule:** `cell == TRUE → 1; else → 0`.
- **Source quote:** "22. Is a lobbyist required to disclose direct business associations with public ofﬁcials, candidates or members of their households? No – 0 points Yes – 1 point" (CPI_2007__hired_guns_methodology.txt:227).
- **Note on state-specific scope (HG notes):** "State-specific definitions of business association; implicit scope variation." Same pattern as Q21 — cell reading is whether the statute includes business-association disclosure; what counts as a "business association" varies (some states require disclosure of partnerships > $X; others require any joint board membership; etc.). Open Issue HG-7: should this be split into separate disclosure-scope cells per relationship type (partnership vs board membership vs employment vs household)? YAGNI says no for now.

#### hg_2007.Q23 — Gifts statutory provision (4-tier ordinal; disclosure-side read = 1 pt)

- **Compendium rows:** `lobbyist_report_includes_gifts_entertainment_transport_lodging` (binary; legal) AND/OR `principal_report_includes_gifts_entertainment_transport_lodging` (binary; legal)
  [cross-rubric: PRI E2f_iii / E1f_iii; Newmark 2017 `disclosure.expenditures_benefiting_officials`; Newmark 2005 `disc_expenditures_benefiting_officials`; Opheim `disclosure.expenditures_benefitting_public_employees`; FOCAL `financials.10`]
  Already in PRI mapping; pre-existing pair.
- **Cell type:** binary per row.
- **Axis:** `legal_availability`.
- **Scoring rule (disclosure-only portion of HG's 4-tier):**
  ```
  HG 4-tier: 0 = not reported; 1 = reported; 2 = limited and reported; 3 = prohibited
  Disclosure-side projection: cell == TRUE → 1; cell == FALSE → 0
  ```
  The 2-pt "limited and reported" tier requires reading TWO cells: (a) reported (this row) AND (b) `lobbyist_gift_dollar_limit_dollars` (typed `Optional[Decimal]`, NEW for the gift-limit prohibition tier) — but the limit tier is partially out of scope (limits are prohibitions). The 3-pt "prohibited" tier is fully out of scope (prohibition; Newmark 2017 `prohib.*` battery territory).
  **For disclosure-only Phase B, project the binary "gifts reported" mapping (0/1).** Full 4-tier projection requires the prohibition round. Maximum disclosure-side projection score for Q23 = 1 pt out of 3 max.
- **Source quote:** "23. What is the statutory provision for a lobbyist giving and reporting gifts? Gifts are not reported – 0 points; Gifts are reported – 1 point; Gifts are limited and reported – 2 points; Gifts are prohibited – 3 points" (CPI_2007__hired_guns_methodology.txt:234).
- **Note on partial-scope projection:** Q23 is the cleanest example of a contributing-rubric item with **partial disclosure-side projection**: 1 of 3 max points is reachable from disclosure cells; 2 points require prohibition cells. **The Phase C validation tolerance for HG Q23 disclosure-side projection should be loose (we'll under-score states with gift limits or prohibitions by 1–2 pts).** This is similar to Newmark's `prohib.*` battery exclusion — Newmark gets fully zero points on those; HG gets up to 1/3 here.
- **Note on row granularity (Newmark 2017 watchpoint resolution):** Newmark 2017 mapping flagged: keep the PRI gifts bundle (gifts ∪ entertainment ∪ transport ∪ lodging), don't split. HG Q23 is gifts-specific — would justify a split. **Resolution:** keep bundle. Per Newmark 2017's note, splitting only matters if a state requires reporting of gifts but NOT entertainment/transport/lodging (empirically unusual). Compendium 2.0 freeze may revisit if extraction surfaces such states.

#### hg_2007.Q24 — Campaign contributions statutory provision (5 labels / 3 distinct point values; disclosure-side read = up to 1 pt)

- **Compendium rows:** `lobbyist_report_includes_campaign_contributions` (binary; legal) **NEW**
  [cross-rubric: Newmark 2005 `prohib_campaign_contrib_any_time` (the PROHIBITION axis, OOS); Newmark 2005 `prohib_campaign_contrib_during_session` (also OOS); Newmark 2017 has the parallel prohibitions; HG Q24 disclosure-side is the only contributing-rubric read of the DISCLOSURE axis (whether campaign contributions are DISCLOSED on lobbyist spending reports — not prohibited). HG-distinctive on the disclosure side; consistent with `lobbyist_or_principal_report_includes_contributions_received_for_lobbying` being the only contributing-rubric read of OTHER-side contributions disclosure.]
- **Cell type:** binary.
- **Axis:** `legal_availability`.
- **Scoring rule (disclosure-only portion of HG's 5-label composite):**
  ```
  HG 5-label / 3-value scoring:
   - "Campaign contributions allowed, not disclosed, prohibited during session"   → 0
   - "Campaign contributions allowed, not disclosed, allowed during session"      → 0
   - "Campaign contributions allowed, disclosed on spending report, prohibited during session" → 1
   - "Campaign contributions allowed, disclosed on spending report, allowed during session"   → 1
   - "Campaign contributions prohibited"                                          → 2

  Disclosure-side projection: cell == TRUE → 1; cell == FALSE → 0
  ```
  The 2-pt "prohibited" tier requires reading the Newmark `prohib_campaign_contrib_any_time` cell (OOS for disclosure-only). The session-timing distinction (allowed-during-session-or-not) doesn't change the point value per HG's own scoring — so the cell reading is just "are campaign contributions disclosed on spending reports."
  **For disclosure-only Phase B, max projection score for Q24 = 1 pt out of 2 max.** Loose tolerance, same as Q23.
- **Source quote:** "24. What is the statutory provision for a lobbyist giving and reporting campaign contributions? Campaign contributions allowed and not required to be disclosed on spending report/prohibited during session – 0 points; Campaign contributions allowed and not required to be disclosed on spending report/allowed during session – 0 points; Campaign contributions allowed and required to be disclosed on spending report/prohibited during session – 1 point; Campaign contributions allowed and required to be disclosed on spending report/allowed during session – 1point; Campaign contributions prohibited – 2 points" (CPI_2007__hired_guns_methodology.txt:248).
- **Note on the composite quirk:** Per `items_HiredGuns.md` §7: "5 labeled levels but only 3 distinct point values. The 'during session' / 'allowed' distinction inside the 'disclosed' branch does not change the point value. The labels carry information that the score does not — a quirk worth flagging if downstream consumers expect category labels and points to be biject." For projection-mapping purposes, this means the *projection function* uses only the disclosure binary; the labeled levels' session-timing distinction is informational, not score-affecting.
- **Note on outgoing vs incoming contributions:** Q24 is about contributions FROM lobbyist TO public officials (outgoing). Newmark 2017's `lobbyist_or_principal_report_includes_contributions_received_for_lobbying` is about contributions TO lobbyist/principal FROM third parties (incoming). Distinct observables; both belong in compendium 2.0.

#### hg_2007.Q25 — Null/no-activity report required (1 pt)

- **Compendium rows:** `lobbyist_spending_report_required_when_no_activity` (binary; legal) **NEW**
  [cross-rubric: no current reader. HG-distinctive observable. Practical effect: a state requiring null filings exposes lobbying-activity gaps as observable cells (zero-filings are themselves a data point), whereas a state without null-filing requirements has gaps that are ambiguous between "no activity" and "filing forgotten."]
- **Cell type:** binary.
- **Axis:** `legal_availability`.
- **Scoring rule:** `cell == TRUE → 1; else → 0`.
- **Source quote:** "25. Is a lobbyist who has done no spending during a ﬁling period required to make a report of no activity? No – 0 points Yes – 1 point" (CPI_2007__hired_guns_methodology.txt:265).
- **Note on data-pipeline implications:** This cell's value affects the downstream LobbyView-style data layer's interpretability — states with `cell == TRUE` produce a complete time series of lobbyist activity (including explicit zeros); states with `cell == FALSE` produce a censored time series where absence-of-filing is ambiguous. Flagged for the LobbyView schema-coverage mapping (last Phase B target).

### Employer Spending Disclosure (Q26–Q27; max 5 points)

#### hg_2007.Q26 — Principal/employer required to file spending report (gateway; 3 pts)

- **Compendium rows:** `principal_spending_report_required` (binary; legal)
  [cross-rubric: PRI E1a (canonical atomization); CPI #203 (compound)]
  Already in PRI mapping; pre-existing.
- **Cell type:** binary.
- **Axis:** `legal_availability`.
- **Scoring rule:** `cell == TRUE → 3; else → 0`.
- **Source quote:** "26. Is an employer or principal of a lobbyist required to ﬁle a spending report? No – 0 point Yes – 3 points" (CPI_2007__hired_guns_methodology.txt:275).

#### hg_2007.Q27 — Principal compensation/salary required on principal spending report (2 pts)

- **Compendium rows:** `principal_report_includes_direct_compensation` (binary; legal)
  [cross-rubric: PRI E1f_i (canonical atomization); CPI #203 / CPI #204 (compound — CPI reads both axes); Newmark 2017 `disclosure.total_compensation` partial (Newmark is lobbyist-side, but the principal-side mirror is implicit in the compendium row family)]
  Already in PRI mapping; pre-existing.
- **Cell type:** binary.
- **Axis:** `legal_availability`.
- **Scoring rule:** `cell == TRUE → 2; else → 0`.
- **Source quote:** "27. Is compensation/salary required to be reported on employer/principal spending reports? No – 0 points Yes – 2 points" (CPI_2007__hired_guns_methodology.txt:281).
- **Note (HG notes column):** "Mirrors Q13 from the employer side." Confirms the lobbyist-side / principal-side parallelism that PRI's atomization preserves explicitly (E1 / E2 mirror tables).

### Electronic Filing (Q28–Q30; max 3 points)

#### hg_2007.Q28 — Online registration available (1 pt)

- **Compendium rows:** `online_lobbyist_registration_filing_available` (binary; practical) **NEW**
  [cross-rubric: FOCAL `openness.1` ("Lobbyist register is online" — closest concept-adjacent, but FOCAL reads availability of the SEARCHABLE REGISTER, not the LOBBYIST-side FILING ability); CPI #205/#206 (de facto access to disclosure documents at compound granularity; CPI doesn't atomize the file-vs-view distinction); HG Q28-Q30 atomize the lobbyist-side filing capability, which FOCAL/CPI compress into "is the register online"]
- **Cell type:** binary.
- **Axis:** `practical_availability`.
- **Scoring rule:** `cell == TRUE → 1; else → 0`.
- **Source quote:** "28. Does the oversight agency provide lobbyists/employers with online registration? No – 0 points Yes – 1 point" (CPI_2007__hired_guns_methodology.txt:287).
- **Note (HG notes column):** "CPI links this to ensuring electronic format and searchable database availability." The cell reads whether the oversight agency PROVIDES an online registration filing portal — distinct from whether the resulting data is online-accessible by the public (that's Q31). Compendium 2.0 may want to consolidate Q28+Q29 into a single `online_lobbyist_filing_available` cell or keep them split; granularity bias says split (a state could offer online registration but require paper-only spending reports — empirically rare but extant in early adoption).

#### hg_2007.Q29 — Online spending reporting available (1 pt)

- **Compendium rows:** `online_lobbyist_spending_report_filing_available` (binary; practical) **NEW**
  [cross-rubric: FOCAL `openness.1` partial (analogous to Q28); CPI #205/#206 compound]
- **Cell type:** binary.
- **Axis:** `practical_availability`.
- **Scoring rule:** `cell == TRUE → 1; else → 0`.
- **Source quote:** "29. Does the oversight agency provide lobbyists/employers with online spending reporting? No – 0 points Yes – 1 point" (CPI_2007__hired_guns_methodology.txt:295).

#### hg_2007.Q30 — Training on electronic filing (1 pt)

- **Compendium rows:** `oversight_agency_provides_efile_training` (binary; practical) **NEW**
  [cross-rubric: no current reader. HG-distinctive. Cell-content scope: any conveyance of e-filing instruction (informational packet, training session, video tutorial, etc.) qualifies per HG notes.]
- **Cell type:** binary.
- **Axis:** `practical_availability`.
- **Scoring rule:** `cell == TRUE → 1; else → 0`.
- **Source quote:** "30. Does the oversight agency provide training about how to ﬁle registrations/spending reports electronically? No – 0 points Yes – 1 point" (CPI_2007__hired_guns_methodology.txt:307).

### Public Access (Q31–Q38; max 20 points)

#### hg_2007.Q31 — Location/format of registrations or active lobbyist directory (4-tier ordinal; max 4 pts)

- **Compendium rows:** four binary cells encoding the access-tier ladder:
  - `lobbyist_directory_available_as_photocopies_from_office_only` (binary; practical) **NEW**
  - `lobbyist_directory_available_as_pdf_or_image_on_web` (binary; practical) **NEW**
  - `lobbyist_directory_available_as_searchable_database_on_web` (binary; practical) **NEW**
  - `lobbyist_directory_available_as_downloadable_database` (binary; practical) **NEW**

  [cross-rubric: FOCAL `openness.1` (online register — overlaps `lobbyist_directory_available_as_pdf_or_image_on_web` + the searchable variant); FOCAL `openness.4` (downloadable — overlaps `lobbyist_directory_available_as_downloadable_database`); FOCAL `openness.5` (searchable with simultaneous sorting — overlaps `lobbyist_directory_available_as_searchable_database_on_web`); CPI #205 (citizens access disclosure documents — compound across all four cells); PRI accessibility Q1–Q6 (compound access cells)]
- **Cell type:** binary per row.
- **Axis:** `practical_availability`.
- **Scoring rule (highest-applies per HG):**
  ```
  4 if downloadable_database == TRUE
  3 if NOT downloadable AND searchable_database == TRUE
  2 if NOT (downloadable OR searchable) AND pdf_or_image_on_web == TRUE
  1 if NOT (downloadable OR searchable OR pdf_or_image) AND photocopies_from_office_only == TRUE
  0 otherwise (no access)
  ```
- **Source quote:** "31. Location/format of registrations or active lobbyist directory: Photocopies from ofﬁce only – 1 point; PDF or image ﬁles on the Web – 2 points; Searchable database on the Web – 3 points; Downloadable ﬁles/database – 4 points" (CPI_2007__hired_guns_methodology.txt:314).
- **Note on "highest-applies" rule:** HG explicitly notes that this question is answered by choosing the item with the highest point value that applies. Translated to compendium cells, this means the cells are NOT mutually exclusive (a state can have BOTH a searchable database AND downloadable files); the projection takes the max. Each cell reads independently from the portal observation.
- **Note on row design — 4 cells vs 1 enum cell:** Granularity bias prefers 4 cells (each access tier is an independently observable portal feature; a state can add downloadable bulk access without rebuilding the searchable interface, etc.). Alternative: a single typed-enum cell `lobbyist_directory_access_tier ∈ {none, photocopies_only, pdf, searchable, downloadable}` with `none < photocopies_only < pdf < searchable < downloadable` ordering. The 4-cell decomposition is more LobbyView-friendly (each cell is a portal feature); the enum is more HG/CPI-friendly (each rubric reads the same ordinal). **Decision:** propose 4 cells now; flag the enum-derivation as a Phase C convenience.
- **Note on overlap with Sunlight item-4 underlying observables:** The Sunlight mapping noted that Sunlight item 4 (Document Accessibility) was excluded from projection, but the underlying observables (digital filing, registration form online, expenditure form online, blank forms online) "are still in compendium 2.0 — they're read by other rubrics." HG Q31 IS the cleanest projection-friendly read of those underlying observables. The 4 cells here cover Sunlight item 4's tiers 0–2; the 5-tier ordinal Sunlight uses (and its near-typo -1/-2 distinction) is what made Sunlight item 4 un-projectable. HG's clean 4-tier ladder makes these cells projectable.

#### hg_2007.Q32 — Location/format of spending reports (4-tier ordinal; max 4 pts)

- **Compendium rows:** four binary cells, exact parallel of Q31 on the spending-report side:
  - `lobbyist_spending_report_available_as_photocopies_from_office_only` (binary; practical) **NEW**
  - `lobbyist_spending_report_available_as_pdf_or_image_on_web` (binary; practical) **NEW**
  - `lobbyist_spending_report_available_as_searchable_database_on_web` (binary; practical) **NEW**
  - `lobbyist_spending_report_available_as_downloadable_database` (binary; practical) **NEW**

  [cross-rubric: same as Q31 — FOCAL openness.1/4/5, CPI #205/#206, PRI accessibility Q1–Q6]
- **Cell type:** binary per row.
- **Axis:** `practical_availability`.
- **Scoring rule:** Same highest-applies ladder as Q31 but on the spending-report side.
- **Source quote:** "32. Location/format of spending reports: Photocopies from ofﬁce only – 1 point; PDF or image ﬁles on the Web – 2 points; Searchable database on the Web – 3 points; Downloadable ﬁles/database – 4 points" (CPI_2007__hired_guns_methodology.txt:336).
- **Note on Q31/Q32 mirror parallel:** Same α form-type split convention applied at the practical-availability axis: directory of lobbyists vs spending reports are distinct portal capabilities. A state might have a downloadable directory but only PDF spending reports — empirically observable across portals. Granularity bias says split into 8 cells (4 directory + 4 spending-report); HG's projection takes the max per side.

#### hg_2007.Q33 — Cost of copies (binary; <25¢/page = 1 pt)

- **Compendium rows:** `lobbying_records_copy_cost_per_page_dollars` (typed `Optional[Decimal]`; practical) **NEW**
  [cross-rubric: CPI #205 partial ("at no cost, can be obtained electronically within a week, or in paper for no more than the cost of photocopies" — CPI's de facto reading bundles cost with timeliness)]
- **Cell type:** `Optional[Decimal]` representing cost per page in dollars. `None` = no per-page fee (e.g., online-only or free copies); `0` = free copies via in-office request.
- **Axis:** `practical_availability`.
- **Scoring rule:**
  ```
  cost IS NULL OR cost < 0.25 → 1
  cost ≥ 0.25 → 0
  ```
- **Source quote:** "33. Cost of copies: 25 cents or more per page – 0 points; Less than 25 cents per page – 1 point" (CPI_2007__hired_guns_methodology.txt:354).
- **Note (HG notes column):** "Tiered fee schedules: take rate appropriate for the first price quantity. Differential in/out-of-state pricing: use in-state price." The cell value should be the per-page rate for in-state requesters at the first tier (i.e., the price for a single page).

#### hg_2007.Q34 — Sample registration/spending forms available on web (1 pt)

- **Compendium rows:** `sample_lobbying_forms_available_on_web` (binary; practical) **NEW**
  [cross-rubric: FOCAL `openness.3` partial (the broader "online availability" battery — FOCAL doesn't atomize blank-vs-filled forms); Sunlight item 4 tier 0 ("Public can access blank forms online" — same observable; Sunlight item 4 excluded from projection but the cells stay in compendium 2.0)]
- **Cell type:** binary.
- **Axis:** `practical_availability`.
- **Scoring rule:** `cell == TRUE → 1; else → 0`.
- **Source quote:** "34. Are sample registration forms/spending reports available the Web? No – 0 points Yes – 1 point" (CPI_2007__hired_guns_methodology.txt:369).
- **Note on HG source typo (HG notes column):** "Note typo in CPI source ('available the Web' missing 'on'). Captured verbatim." Cell content matches the intended meaning regardless of the typo.

#### hg_2007.Q35 — State agency provides aggregate lobbying spending total by year (2 pts)

- **Compendium rows:** `oversight_agency_publishes_aggregate_lobbying_spending_by_year` (binary; practical) **NEW**
  [cross-rubric: FOCAL `financials.*` battery partial (FOCAL atomizes financial-content of lobbying reports; HG Q35 atomizes the AGGREGATE-PROVISION axis — different observable); HG-distinctive at this aggregate-axis granularity]
- **Cell type:** binary.
- **Axis:** `practical_availability`.
- **Scoring rule:** `cell == TRUE → 2; else → 0`.
- **Source quote:** "35. Does the state agency provide an overall lobbying spending total by year? No – 0 points Yes – 2 points" (CPI_2007__hired_guns_methodology.txt:374).
- **Note (HG notes column):** "2002 reference year for the data; provision via Web OR upon request both qualify." The cell reads whether the oversight agency PROVIDES an aggregate yearly total (regardless of channel: web, paper-on-request, FOIA-able). Agency-self-report-derived per `items_HiredGuns.md` §6 — statute-extraction alone won't reliably populate.

#### hg_2007.Q36 — Aggregate spending total by filing-period deadline (2 pts)

- **Compendium rows:** `oversight_agency_publishes_aggregate_lobbying_spending_by_filing_deadline` (binary; practical) **NEW**
  [cross-rubric: parallel to Q35 but at the filing-deadline rollup granularity]
- **Cell type:** binary.
- **Axis:** `practical_availability`.
- **Scoring rule:** `cell == TRUE → 2; else → 0`.
- **Source quote:** "36. Does the state agency provide an overall lobbying spending total by spending-report deadlines? No – 0 points Yes – 2 points" (CPI_2007__hired_guns_methodology.txt:380).

#### hg_2007.Q37 — Aggregate spending total by industry (2 pts)

- **Compendium rows:** `oversight_agency_publishes_aggregate_lobbying_spending_by_industry` (binary; practical) **NEW**
  [cross-rubric: parallel to Q35; industry-classification axis]
- **Cell type:** binary.
- **Axis:** `practical_availability`.
- **Scoring rule:** `cell == TRUE → 2; else → 0`.
- **Source quote:** "37. Does the state agency provide an overall lobbying spending total by industries lobbyists represent? No – 0 points Yes – 2 points" (CPI_2007__hired_guns_methodology.txt:386).
- **Note (HG notes column):** "Lobby spending is not commonly organized in this fashion." Empirically a minority observable in 2007. Web or upon request both qualify.

#### hg_2007.Q38 — Lobby list update frequency (4-tier ordinal; max 4 pts)

- **Compendium rows:** `lobbyist_directory_update_cadence` (typed `Optional[<UpdateCadence>]`; practical) **NEW**
  [cross-rubric: FOCAL `timeliness.1` ("Changes (eg, registering/deregistering lobbyists, new clients) are updated close to real time (eg, daily)" — verbatim parallel observable; FOCAL's 2025 application merged timeliness.1 + timeliness.2 into a single indicator)]
- **Cell type:** typed `Optional[<UpdateCadence>]` where `UpdateCadence` is a structured value `{magnitude: int, unit: enum{day, week, month, semiannual}}` or `enum{daily, weekly, monthly, semiannual_or_less_often, none}`. Two equivalent representations; latter is simpler.
- **Axis:** `practical_availability`.
- **Scoring rule:**
  ```
  cadence == daily             → 4
  cadence == weekly            → 3
  cadence == monthly           → 2
  cadence == semiannual_or_less_often → 1
  cadence IS NULL OR no_updates → 0
  ```
  HG's source has no explicit 0-point option per `items_HiredGuns.md` §7 ("Either CPI assumes every state updates at least semi-annually, or a state with no updates at all gets an unspecified 0. Source is silent on the floor case.") — assuming 0 for no-updates as the conservative reading.
- **Source quote:** "38. How often are lobby lists updated? Semi-annually or less often – 1 point; Monthly – 2 points; Weekly – 3 points; Daily – 4 points" (CPI_2007__hired_guns_methodology.txt:398).

---

## Summary of compendium rows touched

| Row id (working name) | Cell type | Axis | HG items reading | Cross-rubric readers (dedupe candidates) | Status |
|---|---|---|---|---|---|
| `def_target_executive_agency` | binary | legal | Q1 (with `def_target_governors_office`) | CPI #196, Newmark 2017, Newmark 2005, Opheim, FOCAL scope.3 | existing (CPI mapping) |
| `def_target_governors_office` | binary | legal | Q1 (with `def_target_executive_agency`) | CPI #196, FOCAL scope.3 | existing (CPI mapping) |
| `compensation_threshold_for_lobbyist_registration` | typed `Optional[Decimal]` | legal | Q2 (5-tier ordinal magnitude) | CPI #197 (3-tier), Newmark 2017 (binary `IS NOT NULL`), Newmark 2005, Opheim, FOCAL scope.2 | existing (CPI mapping) |
| `lobbyist_registration_required` | binary | legal | Q3 | CPI #198 | existing (CPI mapping) |
| `registration_deadline_days_after_first_lobbying` | typed `Optional[int]` | legal | Q4 (5-tier ordinal) | CPI #200 (de jure pair), FOCAL scope.4 partial | existing (CPI mapping) |
| `lobbyist_reg_form_includes_general_subject_matter` | binary | legal | Q5 (3-tier with bill_id) | Sunlight #1, FOCAL contact_log.11 (broad reading) | existing (Sunlight mapping) |
| `lobbyist_reg_form_includes_bill_or_action_identifier` | binary | legal | Q5 (3-tier with subject) | Sunlight #1, FOCAL contact_log.11 (narrow reading) | existing (Sunlight mapping) |
| `lobbyist_registration_renewal_cadence` | typed `Optional[int_months]` | legal | Q6 (3-tier ordinal) | CPI #199 | existing (CPI mapping) |
| `lobbyist_registration_amendment_deadline_days` | typed `Optional[int]` | legal | Q7 (5-tier ordinal) | (HG-distinctive in current set) | **NEW** |
| `lobbyist_required_to_submit_photograph_with_registration` | binary | legal | Q8 | (HG-distinctive) | **NEW** |
| `lobbyist_reg_form_lists_each_employer_or_principal` | binary | legal | Q9 | (HG-distinctive at reg-form-side granularity; PRI E2c / FOCAL relationships.1 read parallel observables at different scope) | **NEW** |
| `lobbyist_disclosure_includes_employment_type` | binary | legal | Q10 | FOCAL `descriptors.6` (verbatim parallel) | **NEW** |
| `lobbyist_spending_report_required` | binary | legal | Q11 (gateway) | Sunlight #2 tier 0+, CPI #201, Newmark 2017/2005/Opheim gateway implicit | existing (Sunlight mapping) |
| (derived projection from PRI cadence family + session-calendar metadata) | derived | legal | Q12 (4-tier ordinal) | PRI E2h_* binaries, Newmark 2005 `freq_reporting_more_than_annual`, Opheim `disclosure.frequency`, CPI #202, FOCAL timeliness | existing rows; **session-calendar metadata cell is NEW** |
| `lobbyist_spending_report_includes_total_compensation` | binary | legal | Q13 (with reg-form fallback) | Sunlight #5, Newmark 2017/2005, CPI #201, PRI E2f_i, Opheim `disclosure.total_income` | existing (Sunlight mapping) |
| `lobbyist_reg_form_includes_compensation` | binary | legal | Q13 footnote | Sunlight #5 | existing (Sunlight mapping) |
| `lobbyist_spending_report_categorizes_expenses_by_type` | binary | legal | Q14 | Sunlight #2, Newmark 2017/2005, Opheim, FOCAL financials.* | existing (Sunlight mapping) |
| `lobbyist_spending_report_includes_itemized_expenses` | binary | legal | Q15 (with threshold magnitude) | Sunlight #2 tier 2, CPI #201, PRI E1f_iv / E2f_iv, FOCAL financials.6 | existing (Sunlight mapping) |
| `expenditure_itemization_de_minimis_threshold_dollars` | typed `Optional[Decimal]` | legal | Q15 (5-tier ordinal magnitude) | Sunlight #3 (2-tier) | existing (Sunlight mapping) |
| `lobbyist_itemized_expenditure_identifies_employer_or_principal` | binary | legal | Q16 (conditional on Q15) | (HG-distinctive at itemized-detail granularity) | **NEW** |
| `lobbyist_itemized_expenditure_identifies_recipient` | binary | legal | Q17 (conditional on Q15) | (HG-distinctive at itemized-detail granularity; loose adjacency to PRI gifts bundle which implicitly captures recipients but at coarser axis) | **NEW** |
| `lobbyist_itemized_expenditure_includes_date` | binary | legal | Q18 (conditional on Q15) | (HG-distinctive at itemized-detail granularity; FOCAL timeliness.* partial) | **NEW** |
| `lobbyist_itemized_expenditure_includes_description` | binary | legal | Q19 (conditional on Q15) | (HG-distinctive at itemized-detail granularity; FOCAL financials.6 partial) | **NEW** |
| `lobbyist_spending_report_includes_general_subject_matter` | binary | legal | Q20 (3-tier with bill_id) | Sunlight #1, Newmark 2017/2005, PRI E2g_i, Opheim (loose), FOCAL contact_log.11 | existing (Sunlight mapping) |
| `lobbyist_spending_report_includes_bill_or_action_identifier` | binary | legal | Q20 (3-tier with subject) | Sunlight #1, FOCAL contact_log.11, PRI E2g_ii, Opheim (β AND with position) | existing (Sunlight mapping) |
| `lobbyist_spending_report_scope_includes_household_members_of_officials` | binary | legal | Q21 | (HG-distinctive) | **NEW** |
| `lobbyist_disclosure_includes_business_associations_with_officials` | binary | legal | Q22 | FOCAL `relationships.4` (concept-adjacent at FOCAL granularity); LobbyView (Kim 2025 network analysis adjacent) | **NEW** |
| `lobbyist_report_includes_gifts_entertainment_transport_lodging` | binary | legal | Q23 (disclosure-side; max 1 pt of 3) | PRI E2f_iii, FOCAL financials.10, Newmark 2017/2005, Opheim | existing (PRI mapping) |
| `principal_report_includes_gifts_entertainment_transport_lodging` | binary | legal | Q23 (via OR with lobbyist-side) | PRI E1f_iii, FOCAL financials.10, Newmark 2017/2005, Opheim | existing (PRI mapping) |
| `lobbyist_report_includes_campaign_contributions` | binary | legal | Q24 (disclosure-side; max 1 pt of 2) | (HG-distinctive on the DISCLOSURE axis; Newmark prohib_campaign_contrib_* reads the prohibition axis, OOS) | **NEW** |
| `lobbyist_spending_report_required_when_no_activity` | binary | legal | Q25 | (HG-distinctive) | **NEW** |
| `principal_spending_report_required` | binary | legal | Q26 (gateway) | PRI E1a, CPI #203 | existing (PRI mapping) |
| `principal_report_includes_direct_compensation` | binary | legal | Q27 | PRI E1f_i, CPI #203 / #204, Newmark 2017 partial | existing (PRI mapping) |
| `online_lobbyist_registration_filing_available` | binary | practical | Q28 | FOCAL `openness.1` partial, CPI #205/#206 compound | **NEW** |
| `online_lobbyist_spending_report_filing_available` | binary | practical | Q29 | FOCAL `openness.1` partial, CPI #205/#206 compound | **NEW** |
| `oversight_agency_provides_efile_training` | binary | practical | Q30 | (HG-distinctive) | **NEW** |
| `lobbyist_directory_available_as_photocopies_from_office_only` | binary | practical | Q31 (tier 1) | (HG-distinctive at this tier) | **NEW** |
| `lobbyist_directory_available_as_pdf_or_image_on_web` | binary | practical | Q31 (tier 2) | FOCAL `openness.1` | **NEW** |
| `lobbyist_directory_available_as_searchable_database_on_web` | binary | practical | Q31 (tier 3) | FOCAL `openness.5` | **NEW** |
| `lobbyist_directory_available_as_downloadable_database` | binary | practical | Q31 (tier 4) | FOCAL `openness.4`, PRI accessibility.Q6 | **NEW** |
| `lobbyist_spending_report_available_as_photocopies_from_office_only` | binary | practical | Q32 (tier 1) | (HG-distinctive) | **NEW** |
| `lobbyist_spending_report_available_as_pdf_or_image_on_web` | binary | practical | Q32 (tier 2) | FOCAL `openness.1` partial | **NEW** |
| `lobbyist_spending_report_available_as_searchable_database_on_web` | binary | practical | Q32 (tier 3) | FOCAL `openness.5` partial | **NEW** |
| `lobbyist_spending_report_available_as_downloadable_database` | binary | practical | Q32 (tier 4) | FOCAL `openness.4`, PRI accessibility.Q6, CPI #206 | **NEW** |
| `lobbying_records_copy_cost_per_page_dollars` | typed `Optional[Decimal]` | practical | Q33 | CPI #205 partial | **NEW** |
| `sample_lobbying_forms_available_on_web` | binary | practical | Q34 | Sunlight item 4 tier 0 (underlying cell, since Sunlight #4 excluded), FOCAL openness.3 partial | **NEW** |
| `oversight_agency_publishes_aggregate_lobbying_spending_by_year` | binary | practical | Q35 | (HG-distinctive at aggregate-provision axis) | **NEW** |
| `oversight_agency_publishes_aggregate_lobbying_spending_by_filing_deadline` | binary | practical | Q36 | (HG-distinctive) | **NEW** |
| `oversight_agency_publishes_aggregate_lobbying_spending_by_industry` | binary | practical | Q37 | (HG-distinctive) | **NEW** |
| `lobbyist_directory_update_cadence` | typed `<UpdateCadence>` | practical | Q38 (4-tier ordinal) | FOCAL `timeliness.1` (verbatim parallel) | **NEW** |

**Totals:** 38 in-scope items × ~38 distinct compendium rows touched (Q31/Q32 split into 4 cells each — 8 NEW practical-access cells; Q12 derived from cadence family + session-calendar metadata).

- **Reuse rate by item:** 16 of 38 in-scope items map entirely to pre-existing rows (Q1, Q2, Q3, Q4, Q5, Q6, Q11, Q13, Q14, Q15, Q20, Q23, Q26, Q27 — plus Q12 reads existing cadence rows; Q13 reads existing reg-form fallback). **42% reuse rate by item.**
- **New rows introduced:** **22 distinct new compendium rows** (the largest count from any single mapping so far). 14 are NEW legal-availability rows (Q7, Q8, Q9, Q10, Q16, Q17, Q18, Q19, Q21, Q22, Q24, Q25 + the session-calendar metadata cell). 8 are NEW practical-availability rows for Q28–Q30 + the Q31/Q32 underlying cell family + Q33–Q38 access-tier cells. **Net practical-availability rows added: 13** (8 from Q31/Q32 + 5 from Q28/Q29/Q30/Q33/Q34/Q35/Q36/Q37/Q38 — minus 2 cells that share with Q31/Q32 family).

**Reuse pattern compared to prior mappings:**
- CPI 2015 C11 mapping: ~21 rows touched (CPI is the smallest, first mapping).
- PRI 2010 mapping: ~69 rows touched (PRI is the largest by-item count; 83 in scope).
- Sunlight 2015 mapping: 13 rows touched (11 cross-rubric); 4-of-5 items in scope.
- Newmark 2017 mapping: 14 rows touched (8 reused + 6 new); 14 items in scope.
- Newmark 2005 mapping: 14 rows touched (100% reuse); 14 items in scope.
- Opheim 1991 mapping: 14 rows touched (100% reuse); 15 items in scope.
- **HG 2007 mapping (this one):** **38 rows touched (16 reused + 22 new); 38 items in scope.**

HG is the second-largest by row-touch count (after PRI). It introduces the most new rows of any single mapping because (a) it's the largest by item count after PRI, (b) it atomizes practical-availability finer than any other rubric (Q28–Q38 covers 11 portal observables; no other rubric covers more than 4 — FOCAL openness has 9 but those mostly read into HG's cells at finer FOCAL granularity).

---

## Promotions for compendium 2.0 freeze planning

After HG, several row families' cross-rubric confirmation levels shift upward:

- `lobbyist_spending_report_includes_total_compensation` → **7-rubric-confirmed** (Sunlight + Newmark 2017 + Newmark 2005 + Opheim + HG Q13 + CPI #201 + PRI E2f_i). **Single most-validated row in the compendium.**
- `lobbyist_spending_report_categorizes_expenses_by_type` → **6-rubric-confirmed** (Sunlight + Newmark 2017 + Newmark 2005 + Opheim + HG Q14 + FOCAL implicit).
- `lobbyist_spending_report_includes_itemized_expenses` → **6-rubric-confirmed** (Sunlight + CPI + HG Q15 + PRI E1f_iv/E2f_iv + Newmark 2017 implicit + FOCAL financials.6).
- `compensation_threshold_for_lobbyist_registration` → **5-rubric-confirmed at varying granularities** (CPI #197 3-tier + HG Q2 5-tier + Newmark 2017 / 2005 / Opheim `IS NOT NULL` + FOCAL scope.2). The 5-tier read (HG) and 3-tier read (CPI) at the same typed cell is the cleanest example of "typed cell, multiple projection granularities" in the compendium.
- Gifts/entertainment/transport/lodging bundle (lobbyist + principal sides) → **5-rubric-confirmed** at combined granularity (PRI + Newmark 2017 + Newmark 2005 + Opheim + HG Q23 disclosure-side; plus FOCAL `financials.10`).
- `lobbyist_reg_form_includes_bill_or_action_identifier` / `_includes_general_subject_matter` → **3-rubric-confirmed** (Sunlight + HG Q5 + FOCAL contact_log.11 narrow/broad). The α form-type split (locked in Sunlight 2026-05-11) is now empirically necessary: HG Q5 vs Q20 was the canonical motivating case and HG's actual mapping reads BOTH sides distinctly.
- `lobbyist_spending_report_includes_bill_or_action_identifier` / `_includes_general_subject_matter` → **4-rubric-confirmed** (Sunlight + HG Q20 + Newmark 2017/2005 + PRI E2g_i/ii + Opheim β AND).

The 22 new rows introduced this mapping are mostly **single-rubric** (HG-distinctive) in the current contributing set. The exceptions:

- `lobbyist_disclosure_includes_employment_type` (Q10) — 2-rubric-confirmed with FOCAL `descriptors.6` verbatim parallel.
- `lobbyist_disclosure_includes_business_associations_with_officials` (Q22) — concept-adjacent to FOCAL `relationships.4`; likely 2-rubric-confirmed once FOCAL mapping lands.
- `lobbyist_directory_update_cadence` (Q38) — verbatim parallel to FOCAL `timeliness.1`; 2-rubric-confirmed after FOCAL mapping.
- `lobbyist_directory_available_as_*` × 4 cells (Q31) — overlap with FOCAL `openness.1/4/5`; partial confirmation.
- `lobbyist_spending_report_available_as_*` × 4 cells (Q32) — same FOCAL overlap.

**FOCAL mapping is the next chance to promote ~10 HG-introduced rows from single-rubric to 2-rubric-confirmed.** LobbyView schema-coverage check is the last; it may confirm some practical-availability cells against federal LDA portal facets.

---

## Corrections to predecessor mappings

### Correction 1 — HG total-item count in plan and handoffs

The locked plan ([`../../plans/20260507_atomic_items_and_projections.md`](../../plans/20260507_atomic_items_and_projections.md)) and the 2026-05-11 handoff both reference HG as a **47-item rubric**, with the plan adding "Q1-Q38 + accessibility-related Q49-Q56" as disclosure scope. **Both numbers are incorrect on the HG source:**

- `items_HiredGuns.tsv` contains **48 atomic items** (Q1 through Q48), confirmed by `items_HiredGuns.md` §4: "Total rows in TSV: 48." The CPI 2007 methodology source itself enumerates Q1 through Q48 with category maxima summing to 100 exactly. There is no Q49 or beyond.
- Disclosure-side scope per the plan's stated exclusions (Q39–Q47 enforcement + Q48 cooling-off OOS) = **Q1–Q38 = 38 items in scope**, not 47.
- The handoff's "47 items, disclosure-side only" was a propagated typo from the plan's 47-item summary table; the plan's "Q49–Q56" sub-list is likely a paste-error from another rubric's structure (Opheim has 22 items / Q1–Q22; Newmark 2017 has 19 items / `def.*` + `prohib.*` + `disc.*` — neither matches Q49–Q56 either).

**Implication for Phase C:** the 50 × 38 = 1,900 per-cell ground-truth count (vs. the earlier 50 × 47 = 2,350 estimate) is the correct figure if CPI's per-state per-question scorecard is retrievable.

### Correction 2 — `def_actor_class_*` is NOT 4-rubric-confirmed after HG

The 2026-05-11 handoff anticipated HG might be a 4th reader of the `def_actor_class_elected_officials` / `def_actor_class_public_employees` row family ("HG mapping need not re-examine the row family's existence; just check if any HG question reads it (likely Q3 / Q4 area on individual lobbyist definition — could be a 4th reader but immaterial to row design)"). **Walked: HG is NOT a 4th reader.** HG Q3 ("Is a lobbyist required to file a registration form?") is a registration-gateway question; HG Q4 is the registration deadline. Neither reads whether elected officials or public employees fall under the lobbyist definition as an actor-class observable. HG's `Def of Lobbyist` category (Q1, Q2) atomizes target-coverage (executive branch) and the lobbyist-status threshold, not actor-class definitional inclusion.

**Status:** `def_actor_class_*` remains 3-rubric-confirmed (Newmark 2017 + Newmark 2005 + Opheim). Open Issue 1 (Newmark 2017 mapping) remains resolved-in-principle at 3 rubrics per the Opheim mapping's elevation.

### Correction 3 — Phase B mapping count

The 2026-05-13 (Opheim) mapping noted "6 mappings done, 3 remaining (HG, FOCAL, LobbyView)." HG is now the 7th mapping. Remaining: FOCAL, LobbyView.

---

## Open issues surfaced by HG (for compendium-2.0 freeze)

1. **`def_target_executive_agency` row design — split for "legislative-action-only carve-out"?** (HG-1) HG Q1 explicitly does NOT award points if a state recognizes executive-branch lobbying *only when it directly relates to legislative action*. The existing CPI `def_target_executive_agency` cell may be TRUE under that condition (CPI #196's coding is more permissive). Compendium 2.0 should consider splitting into `def_target_executive_agency_standalone` vs `def_target_executive_agency_only_re_pending_legislation` so HG and CPI can each read the cell that matches their own coding rule. Not load-bearing for current Phase C validation (CPI 2015 doesn't preserve the 2007 distinction); flagged for future-rubric mapping.

2. **Q2 "make/spend" ambiguity — does it read `compensation_threshold` OR `expenditure_threshold`?** (HG-2) HG's source wording bundles compensation and expenditure into one 5-tier threshold question. Newmark 2017 / 2005 / Opheim split them into separate definitional standards (now 3-rubric-confirmed as distinct cells). HG's Q2 projection should be `min(compensation_threshold, expenditure_threshold)` if both are non-null; or read whichever is non-null; or read whichever the state's definition uses. Phase C validation may surface states where the HG projection diverges from the published HG score depending on this resolution. Flagged for compendium 2.0 freeze.

3. **Q9 reg-form-specific vs form-flexible scope.** (HG-3) HG Q9 reads `lobbyist_reg_form_lists_each_employer_or_principal` strictly (reg form only), but HG's footnote-like note ("Either single-form-multi-employer or per-employer-registration counts as full points") is ambiguous about whether a state requiring employer lists ONLY on spending reports gets points. Strict reading: reg-form-only. Open Issue HG-3 in the per-item entry; defer to compendium 2.0 freeze.

4. **Q10 form-location flexibility — split or merge cell?** (HG-4) Q10 explicitly accepts the disclosure on either reg form OR spending report. FOCAL `descriptors.6` is form-agnostic. The proposed cell `lobbyist_disclosure_includes_employment_type` is also form-agnostic. Alternative: split into `lobbyist_reg_form_includes_employment_type` + `lobbyist_spending_report_includes_employment_type` per the α convention. Defer to compendium 2.0 freeze.

5. **Q12 derived projection — need a session-calendar metadata cell, or a direct typed-int cell?** (HG-5) Q12's projection from cadence binaries requires session-length information to disambiguate "monthly during session" vs "monthly year-round." Cleanest options: (a) add a `state_legislative_session_calendar` metadata cell typed as a structured value; or (b) carry `lobbyist_spending_reports_implied_per_2yr_cycle: int` as a derived-by-extraction cell directly. Option (b) is YAGNI-cleaner; option (a) is more reusable across future rubrics. Defer to compendium 2.0 freeze.

6. **Q19 description scope — granularity of "description or category" coding.** (HG-6) HG accepts either a free-text description or a category code as YES on `lobbyist_itemized_expenditure_includes_description`. FOCAL `financials.6` may want finer granularity (free-text vs categorical). Defer.

7. **Q22 business-association scope — split by relationship type?** (HG-7) HG accepts a single binary across partnership / board / employment / household-business relationships. FOCAL `relationships.4` is also a single composite. Empirically these tend to be regulated together (a state either covers all of them or none). Defer.

8. **Q23 / Q24 partial-scope projection — Phase C tolerance.** Items with disclosure-side reads that are 1/3 or 1/2 of the published max points will systematically under-score states with prohibition/limit structures. The disclosure-only Phase B accepts this; Phase C validation tolerance must accommodate. **Quantified: across 50 states, Q23 + Q24 contribute up to 5 pts of HG's 100-point total (3 + 2 = 5); the disclosure-side projection captures up to 2 pts (1 + 1). Maximum systematic under-scoring per state = 3 pts on the 100-point scale.** This is well within typical inter-coder reliability range; not a Phase C blocker but should be documented in validation outputs.

9. **Practical-availability cells (Q28–Q38) — Phase C population strategy.** 13 NEW practical-availability cells are HG-distinctive (Q28–Q38; excludes Q31/Q32 which have FOCAL partial overlap). These cells require portal observation, not statute extraction. Phase C validation against HG's published per-state scores requires populating them from a 2007-vintage portal observation that's no longer recoverable. Phase C strategy: validate the 22 legal-axis HG items against published per-state data (if scorecard retrievable); leave the 13+ practical-axis items as Phase D (operational extraction pipeline) validation targets, with Track B portal-extraction work as the upstream source.

10. **The contributing-rubric set has converged on HG's atomization granularity for spending-disclosure observables.** Cumulative across 7 mappings (CPI, PRI, Sunlight, Newmark 2017/2005, Opheim, HG), HG introduces the LAST significant batch of new disclosure-side observables. FOCAL (next mapping) is expected to confirm rather than expand (FOCAL `financials.*` largely overlaps HG / Sunlight / PRI; FOCAL `contact_log.*` overlaps Sunlight α + HG Q5/Q20). **Prediction:** FOCAL mapping will be ≥70% reuse rate; LobbyView schema-coverage will be ~100% coverage check against the now-rich compendium row set.

---

## What HG doesn't ask that other rubrics will

For continuity with other rubric mappings: HG does not read any specific bill-position observable beyond the bill_id read (Sunlight #1 tier 2 / FOCAL contact_log.10 / Opheim β position — HG Q5/Q20 stop at bill number; the position-on-bill cell is not HG-read), any FOCAL-style contact-log per-meeting granularity (FOCAL contact_log battery — HG only goes as far as Q9 listing employers, not per-meeting contacts), any cooling-off-duration-as-ordinal beyond the binary existence (Q48 cooling-off only scores existence; FOCAL `revolving_door.*` and Newmark 2017 `prohib.revolving_door` read at finer granularity), any historical-data archive cell (PRI accessibility.Q5 + FOCAL openness.8 — HG portal-access ladder Q31/Q32 reads current-data access, not historical), any audit / enforcement statutory provisions beyond the OOS Q39-Q47 battery (CPI #207/208/209 reads these at compound granularity), any third-party-contributions-received-for-lobbying observable (Newmark 2017's `lobbyist_or_principal_report_includes_contributions_received_for_lobbying` — HG Q24 is outgoing contributions, not incoming). HG also does not split principal-side observables as finely as PRI (PRI E1f_* has 4 sub-rows; HG Q27 reads only the compensation sub-row).

HG's role within the contributing-rubric set is **finest-grained atomization of the registration + spending-disclosure + portal-access backbone** — 22 of 38 rows it touches are new and largely HG-distinctive, the cell-granularity it introduces (5-tier ordinal on threshold magnitudes, 4-tier ordinal on access ladders, conditional-cascade on itemization detail) is the most diverse in the contributing-rubric set. Together with PRI's actor-and-target taxonomy and FOCAL's contact-log + financials atomization (next mapping), HG completes the disclosure-side row backbone that compendium 2.0 will freeze. After HG, the FOCAL mapping is expected to confirm rather than expand.
