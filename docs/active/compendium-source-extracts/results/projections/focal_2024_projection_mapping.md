# FOCAL 2024 — projection mapping

**Plan:** [`../../plans/20260507_atomic_items_and_projections.md`](../../plans/20260507_atomic_items_and_projections.md) Phase B (eighth rubric to ship, after CPI 2015 C11, PRI 2010, Sunlight 2015, Newmark 2017, Newmark 2005, Opheim 1991, and HiredGuns 2007; OpenSecrets 2022 was tabled 2026-05-13).
**Handoff (most recent):** [`../../plans/_handoffs/20260511_phase_b_continued_remaining_7.md`](../../plans/_handoffs/20260511_phase_b_continued_remaining_7.md). Watchpoints for FOCAL 2024 are in the per-rubric section there.
**Prior handoff:** [`../../plans/_handoffs/20260507_phase_b_handoff.md`](../../plans/_handoffs/20260507_phase_b_handoff.md).
**Atomic items source:** [`../items_FOCAL.tsv`](../items_FOCAL.tsv) (50 atomic indicators, 2024 numbering).
**Phase A4 audit (ground truth provenance):** [`../20260507_focal_a4_audit.md`](../20260507_focal_a4_audit.md).
**Phase A4 ground truth:**
- [`../focal_2025_lacy_nichols_per_country_scores.csv`](../focal_2025_lacy_nichols_per_country_scores.csv) — 1,372 cells (28 countries × 49 merged 2025 indicators; 50 with one merge -1 + one addition +1).
- [`../focal_2025_lacy_nichols_prior_framework_mapping.csv`](../focal_2025_lacy_nichols_prior_framework_mapping.csv) — verbatim Suppl File 1 Table 4 weights per indicator (20×W1 + 19×W2 + 11×W3 = 182 max).
**Predecessor mappings (for conventions and row reuse):** [`cpi_2015_c11_projection_mapping.md`](cpi_2015_c11_projection_mapping.md), [`pri_2010_projection_mapping.md`](pri_2010_projection_mapping.md), [`sunlight_2015_projection_mapping.md`](sunlight_2015_projection_mapping.md), [`newmark_2017_projection_mapping.md`](newmark_2017_projection_mapping.md), [`newmark_2005_projection_mapping.md`](newmark_2005_projection_mapping.md), [`opheim_1991_projection_mapping.md`](opheim_1991_projection_mapping.md), [`hiredguns_2007_projection_mapping.md`](hiredguns_2007_projection_mapping.md).

---

## Doc conventions

All six conventions from the prior mapping docs apply verbatim:

- Compendium row IDs are working names, not cluster-derived.
- Typed cells live on `MatrixCell.value` (v2.0 schema bump assumed).
- Granularity bias: split on every distinguishing case.
- Axis is `legal_availability` for de jure observables, `practical_availability` for de facto (portal-observable) observables. FOCAL is the first contributing rubric whose indicators are roughly evenly split between the two axes (legal-side: scope.*, descriptors.*, relationships.*, financials.*, contact_log.*, partial timeliness.*; practical-side: openness.*, timeliness.* in part).
- **"Collect once, map to many."** Each row entry carries a `[cross-rubric: …]` annotation listing every other rubric that reads the same observable.
- α form-type split applies where FOCAL's "register / reg form vs spending report" distinction is statutorily meaningful (FOCAL itself reads "the register" — typically the lobbyist directory deriving from the registration form, so FOCAL reads the reg-form-side or directory-side cells where the α split applies).

**FOCAL 2024 is structurally the broadest and most internationally-shaped contributing rubric.** It synthesises 15 predecessor frameworks (incl. all 6 other contributing-set rubrics with US scope plus 9 international/EU frameworks) and was designed for global comparison. Its 50 indicators atomize **contact_log per-meeting granularity** (11 sub-fields) and **descriptors lobbyist-identifying-content granularity** (6 sub-fields) finer than any contributing rubric. FOCAL therefore introduces a substantial batch of contact_log + descriptors row families that PRI's binary `_includes_contacts_made` and Sunlight's coarser disclosure rows subsume.

**Expected reuse rate:** ~45% (not the ≥70% prediction from the HG mapping). The HG mapping anticipated FOCAL would "confirm rather than expand," but the per-meeting contact_log atomization (9 new rows) and per-lobbyist descriptors atomization (5 new rows) push the new-row count up. The remaining batteries (scope, openness, financials, relationships, timeliness) DO confirm at high reuse — only contact_log + descriptors expand the row set substantially.

## Scope qualifier — 2 items OUT

Per the plan's disclosure-only Phase B qualifier ("FOCAL all `financials.*` / `descriptors.*` / `contact_log.*` / `openness.*` / `relationships.*` / `scope.*` / `timeliness.*`"), the plan enumerates 7 batteries and is **silent on `revolving_door.*`**. Strict reading: both revolving_door items are out, parallel to:
- HG Q48 cooling-off → DEFERRED (HiredGuns mapping)
- Newmark 2017 `prohib.revolving_door` → DEFERRED (Newmark 2017 mapping)
- Newmark 2005 `prohib.*` battery → DEFERRED

| Excluded item | Why excluded |
|---|---|
| `revolving_door.1` (list of prior public offices that lobbyists have held) | Borderline. Statutorily this IS a disclosure-side observable (a state can require the lobbyist to disclose prior public service on the reg form, analogous to `descriptors.*`). But the plan groups it under "revolving_door" — the cooling-off / prohibition battery — which is deferred. Strict reading: DEFERRED, **flag as Open Issue FOCAL-1** for compendium 2.0 freeze reconsideration. |
| `revolving_door.2` (database of officials in cooling-off period) | State-side meta-publication of an enforcement mechanism (which officials are currently restricted from lobbying). Enforcement-adjacent; not disclosure-side. Cleanly DEFERRED. |

**Implication for US federal LDA ground truth:** Federal LDA scored 6/6 = 3×2 on revolving_door.1 (yes; weight 3) and 0 on revolving_door.2 (no; weight 1). With both deferred, the projected partial reaches 75/182 = 41% (max) against published 81/182 = 45% — a known **6-point under-scoring tolerance** in Phase C validation, fully attributable to the scope deviation. Documenting tolerance now so Phase C doesn't surprise.

If at end-of-session review the scope-qualifier deviation is rejected and `revolving_door.1` is brought in scope: the row `lobbyist_reg_form_includes_lobbyist_prior_public_offices_held` (NEW) reads the disclosure; projection is `cell == TRUE → 1 (partly) | only_one_listed → 1 (partly) | all_listed → 2 (yes)`. Adding this row reaches projected 81/182 for US.

## Aggregation rule

FOCAL's published structure (Lacy-Nichols 2025 main paper + Suppl File 1 Tables 3, 4, 5):

```
per_indicator_score(i) = base(i) × weight(i)
  base(i)   ∈ {0=no, 1=partly, 2=yes}
  weight(i) ∈ {1, 2, 3}            (verbatim per Suppl File 1 Table 4 "Our weights")

per_country_score = Σ per_indicator_score(i) over all 50 indicators
                  ∈ [0, 182]
per_country_pct   = per_country_score / 182
```

**Weight distribution:** 20 × weight-1 + 19 × weight-2 + 11 × weight-3 = 91, sum × 2 = **182 maximum**.

**Phase C `project_focal_2024_disclosure_side(state_or_federal, vintage)` produces:**

```
focal_partial_score    = Σ per_indicator_score(i) for i in 48 in-scope indicators
                       ∈ [0, 175]    (since revolving_door.1 weight 3 yes=6 + revolving_door.2 weight 1 yes=2 = 8 max excluded;
                                      but ground-truth tolerance applies as +0..+8 for the excluded battery — typically +6 for jurisdictions like US that score revolving_door.1=yes)
focal_partial_pct      = focal_partial_score / 175
```

The 2 `revolving_door.*` items are **not projected**. Phase C validation tolerance against published FOCAL scores must add back the published revolving_door per-country values (or accept the systematic under-scoring on a published-vs-projected delta with known sign).

## Per-state / per-country per-indicator data

**FOCAL 2024 itself publishes no scores.** FOCAL is a framework paper (Lacy-Nichols 2024, IJHPM); no jurisdictions are scored in it. **Lacy-Nichols 2025 (Milbank Quarterly) APPLIES FOCAL to 28 countries' national lobbyist registers** — providing the **per-country per-indicator ground truth** at `../focal_2025_lacy_nichols_per_country_scores.csv` (1,372 cells: 28 countries × 49 merged 2025 indicators).

**Project-relevant validation anchor: US federal LDA = 81/182 = 45%** — the primary federal-jurisdiction validation row across the contributing rubric set. Per the audit doc:

```
Scope:          4 + 0 + 0 + 2  =  6
Timeliness:     0 + 0          =  0
Openness:       4 + 0 + 6 + 3 + 6 + 2 + 2 + 2 + 2  =  27
Descriptors:    4 + 2 + 0 + 0 + 2 + 0  =  8
Revolving_door: 6 + 0          =  6      (DEFERRED in this projection)
Relationships:  6 + 2 + 0 + 0 + 0  =  8
Financials:     4 + 4 + 0 + 0 + 0 + 4 + 0 + 0 + 0 + 0 + 4  =  16
Contact_log:    2 + 0 + 2 + 0 + 0 + 0 + 0 + 0 + 3 + 0 + 3  =  10
TOTAL:          81 / 182 = 45%           (projected: 75 / 175 = 43% after revolving_door deferral)
```

**Other validation jurisdictions** (28 total, US row most relevant): Canada 49%, Chile 48%, Ireland 43%, France 43%, Scotland 40%, ... down to Netherlands 9%. The non-US rows are reference; the project's extraction pipeline is US-focused (50 states + Federal_US per the 2026-05-07 jurisdiction-scope landing).

**Per-state US ground truth:** NONE. FOCAL has not been applied to US states (only Federal_US). Phase C state-level projections run the same logic on state cells but cannot be validated directly — cross-rubric validation against PRI/CPI/Sunlight/HG state-level scores is the only check. This is the **opposite** of HG/CPI/Newmark, where per-state ground truth exists but federal does not.

## Phase C validation

**Federal_US LDA:** 1 jurisdiction × 1 vintage (2024) × 49 merged 2025 indicators (after timeliness.1+.2 merge) = **49 per-cell ground-truth values**, plus aggregate 81/182 (45%).

**Other countries:** 27 jurisdictions × 1 vintage × 49 indicators = 1,323 more cells if non-US validation is in scope (it's secondary; the pipeline is US-focused).

**US states:** 50 jurisdictions × 1 vintage × 48 in-scope indicators = 2,400 projected cells, **NONE with FOCAL-published ground truth.** Cross-rubric is the only check: every shared row (e.g., `lobbyist_spending_report_includes_total_compensation` is read by FOCAL `financials.1` + Sunlight #5 + Newmark 2017/2005 + HG Q13 + CPI #201 + PRI E2f_i) lets us check that FOCAL's projection on a state cell matches the other rubrics' projections on the same cell.

## Structural notes — Lacy-Nichols 2024 → 2025

Two adjustments in the 2025 application (per audit doc):

1. **`timeliness.1` + `timeliness.2` MERGED into one 2025 indicator.** Lacy-Nichols 2025 main text line 202-204: "we combined two of the timeliness indicators (around updating changes in general versus activities), as the answers were the same across all registers." Net: -1 indicator. The merged 2025 indicator uses the same weight (3) and same scoring rule.
   - **Projection implication:** Both 2024 rows map to the same compendium cell `lobbyist_directory_update_cadence` (HG Q38 NEW). The merged 2025 ground-truth cell in the per-country CSV is `timeliness.1` (2025 numbering); `timeliness.2` (2024 numbering) is null/merged in 2025. Phase C projection treats them as one merged indicator.

2. **NEW indicator "Lobbyist list" added to Relationships category in 2025.** Lacy-Nichols 2025 main text line 213: "We created an additional indicator for listing the lobbyists employed by a company or lobby firm, as we found this was inconsistently disclosed." Net: +1 indicator. This 2025-only indicator is NOT in `items_FOCAL.tsv` (which captures 2024 items only).
   - **Projection implication:** This 2025-only indicator reads `principal_report_lists_lobbyists_employed` (NEW, parallel to HG Q9 `lobbyist_reg_form_lists_each_employer_or_principal` but on the principal/employer side — "the company discloses which lobbyists it has retained"). Documenting now but not formally in the per-item mappings below (since the source TSV is 2024 numbering). Phase C tooling should support reading this 2025-only indicator from the per-country CSV.

Net: 50 (2024) → 49 (merged) + 1 (added) = 50 (2025) indicators with verbatim ground-truth in `focal_2025_lacy_nichols_per_country_scores.csv`.

---

## Per-item mappings

### Scope battery (4 items, all in scope)

FOCAL's "scope of what is included and excluded from the register" — definitions of lobbyists / activities / targets / thresholds.

#### focal_2024.scope.1 — Lobbyist definition includes 9 actor types (weight 2)

- **Compendium rows:** `lobbyist_definition_included_actor_types` (typed `Set[enum{prof_consultant, inhouse_company, inhouse_org, prof_consultancy, law_firm, think_tank, research_institution, public_entity, govt_agency_employee}]`; legal) **NEW**
  [cross-rubric: Newmark 2017/2005 `def_actor_class_*` (individual elected officials / public employees — DIFFERENT axis; FOCAL scope.1 is ORGANIZATIONAL actor types); HG Q1 (target-side recognition, not actor-side breadth); CPI #196 (target-side); PRI A1-A11 (institutional-actor side — closer concept but at structural-actor not actor-type granularity)]
  **Distinct from `def_actor_class_*`** (Newmark/Opheim individual-actor family) and from `actor_*` (PRI institutional-actor family). FOCAL scope.1 is a third actor axis: organizational actor TYPES.
- **Cell type:** `Set[enum]` over the 9 FOCAL-enumerated organizational types.
- **Axis:** `legal_availability`.
- **Scoring rule:**
  ```
  cell == {all 9 types}  → 2 (yes)
  cell ⊃ {prof_consultant} AND cell ≠ {all}  → 1 (partly) — "other exclusions"
  cell == {prof_consultant} ONLY  → 0 (no) — "only consultant lobbyists"
  ```
- **Source quote:** "The following types of lobbyists are included in the register: professional lobbyists/consultants, in-house company lobbyists, in-house organisation lobbyists, professional consultancies, law firms, think tanks, research institutions, public entities, government agencies/employees" (FOCAL Table 3); P/N from Suppl Table 3: "N=only consultant lobbyists; P=other exclusions" (Suppl File 1 line 158ff).
- **Note on row design — atomization deferred:** Granularity bias would suggest 9 binary cells, one per actor type. **Deferred**: extraction would have to enumerate 9 binary cells from statute, which is heavier than reading the set membership directly. The set-typed cell is YAGNI-cleaner; atomization into 9 binary cells flagged as Open Issue FOCAL-2 for compendium 2.0 freeze.
- **Note on US federal LDA scoring:** Federal LDA scored 4 (raw 2 × weight 2 = yes). LDA's "lobbyist" definition covers all 9 types via the broad "any individual who is employed or retained ... for compensation to ... lobby" language. Cell value for Federal_US = full set.

#### focal_2024.scope.2 — No/low financial or time threshold for registration (weight 3)

- **Compendium rows:** `compensation_threshold_for_lobbyist_registration` (typed `Optional[Decimal]`; legal) AND `expenditure_threshold_for_lobbyist_registration` (typed `Optional[Decimal]`; legal) AND `time_threshold_for_lobbyist_registration` (typed `Optional[<TimeThreshold>]`; legal)
  [cross-rubric: CPI #197 (compensation cell — 3-tier read); HG Q2 (compensation cell — 5-tier read); Newmark 2017/2005 `def.*_standard` (binary `IS NOT NULL` × 3 cells); Opheim `def.*_standard` (binary `IS NOT NULL` × 3 cells)]
  All three rows pre-existing (CPI for compensation; Newmark 2017 introduced expenditure + time).
- **Cell type:** existing typed cells (`Optional[Decimal]` × 2 + `Optional[<TimeThreshold>]` × 1).
- **Axis:** `legal_availability`.
- **Scoring rule:**
  ```
  Let any_threshold = (compensation_threshold IS NOT NULL) OR (expenditure_threshold IS NOT NULL) OR (time_threshold IS NOT NULL)
  Let significant_threshold = (compensation_threshold > LOW_DOLLAR_CUTOFF) OR (expenditure_threshold > LOW_DOLLAR_CUTOFF) OR (time_threshold > LOW_TIME_CUTOFF)

  significant_threshold == TRUE   → 0 (no — "significant financial or time thresholds")
  any_threshold == TRUE AND NOT significant_threshold AND only_remunerated_lobbying_included → 1 (partly — "only remunerated lobbying included")
  any_threshold == FALSE   → 2 (yes — "no thresholds, anyone who lobbies must register")
  ```
  `LOW_DOLLAR_CUTOFF` and `LOW_TIME_CUTOFF` are scorer-judgment; FOCAL's 2024 paper acknowledges the subjectivity (paper lines 1206-1208: "what is a 'low' financial or time threshold? This is a question we will consider in the next stage"). **Phase C must pick a calibrated cutoff** — candidate: $1000 / 8 hours / 5% time. Document in Phase C plan; this is the only FOCAL indicator where the cutoff is scorer-judgment rather than mechanically derivable from the cell value.
- **Source quote:** "There is no (or low) financial or time threshold to qualify/exempt lobbyists from registration" (FOCAL Table 3); P/N: "P=only remunerated lobbying included; N=significant financial or time thresholds" (Suppl Table 3).
- **Note on cross-rubric reads at varying granularities on the same cells:** This is the canonical 5-rubric-confirmed threshold-cell family in compendium 2.0. CPI/HG/Newmark/Opheim/FOCAL all read these three typed cells at different granularities (3-tier, 5-tier, binary `IS NOT NULL`, combined "any threshold" reads). The cells carry the typed value; projections apply rubric-specific reads. **No new rows.**
- **Note on US federal LDA scoring:** Federal LDA scored 0 (no). LDA has compensation threshold ($3000) + time threshold (20%) — counted as "significant" by L-N 2025.

#### focal_2024.scope.3 — 8 target types included (weight 3)

- **Compendium rows:** `def_target_legislative_branch` (binary; legal) AND `def_target_executive_agency` (binary; legal) AND `def_target_governors_office` (binary; legal) AND `def_target_legislative_or_executive_staff` (binary; legal) **NEW (staff row)**
  [cross-rubric: CPI #196 (compound — reads legislative + executive + governor); HG Q1 (target-side reading of executive recognition); Newmark 2017/2005 `def.legislative_lobbying` + `def.administrative_agency_lobbying`; Opheim `def.legislative_lobbying` + `def.administrative_lobbying`; PRI A7 (actor-side parallel for legislative branch)]
  3 existing rows + 1 NEW (`def_target_legislative_or_executive_staff`).
- **Cell type:** binary per row.
- **Axis:** `legal_availability`.
- **Scoring rule:**
  ```
  legislative_branch == TRUE AND executive_agency == TRUE AND governors_office == TRUE AND staff == TRUE  → 2 (yes — all targets)
  legislative_branch == TRUE AND executive_agency == TRUE AND governors_office == TRUE AND staff == FALSE  → 1 (partly — "staff excluded")
  one or more major branches missing  → 0 (no — "major branches excluded")
  ```
- **Source quote:** "The following are included as targets of lobbying: legislative branches, executive branch officials, Ministers, Deputy Ministers, members of parliament, Director-Generals and senior officials, staff, administrative branch/bureaucracy" (FOCAL Table 3); P/N: "P=staff excluded; N=major branches excluded" (Suppl Table 3).
- **Note on staff-row design:** FOCAL explicitly enumerates "staff" as a separate target type alongside major branches. The compendium currently has no cell for whether staff (legislative aides, executive-branch employees below senior level) are recognized as targets. PROPOSE NEW `def_target_legislative_or_executive_staff` (binary; legal). HG Q22 reads "household members of officials" (different observable, finer). Phase C: project staff cell separately from major-branch cells per FOCAL's 3-tier scoring.
- **Note on parliamentary target mapping:** FOCAL's "Ministers, Deputy Ministers, members of parliament, Director-Generals and senior officials" map to US state equivalents: Governor's Office (Ministers/Deputy Ministers), Legislature (members of parliament), executive-agency leadership (Director-Generals/senior officials). The 4-cell read above is the US-state-mapped equivalent of FOCAL's broader parliamentary enumeration.
- **Note on US federal LDA scoring:** Federal LDA scored 0 (no). LDA's "covered legislative branch official" + "covered executive branch official" cover legislators + president + VP + cabinet + EOP — major branches all covered. But L-N 2025 scored 0; likely because LDA excludes congressional STAFF (covered staff is narrow), staff exclusion drives the 0. Worth double-checking against the L-N coding notes if available in Phase C — could indicate a stricter staff-coverage interpretation than US legal scholars would give LDA.

#### focal_2024.scope.4 — Activity breadth (weight 1)

- **Compendium rows:** `lobbying_definition_included_activity_types` (typed `Set[enum{oral, written, electronic, virtual, meeting_organizing, events, phone_calls, emails}]`; legal) **NEW**
  [cross-rubric: HG Q1-Q3 read "what counts as lobbying" at coarser registration-trigger granularity, not activity breadth per se; PRI definitions reference but don't atomize activity types; **FOCAL-distinctive at this granularity in current contributing set**]
- **Cell type:** `Set[enum]` over the 8 FOCAL-enumerated activity types.
- **Axis:** `legal_availability`.
- **Scoring rule:**
  ```
  cell ⊇ {oral, written, electronic, virtual, meeting_organizing, events}  → 2 (yes — wide breadth)
  cell limited to influencing legislative changes only  → 1 (partly — "limited to influencing legislative changes")
  cell == {face_to_face} ONLY  → 0 (no — "face-to-face only")
  ```
- **Source quote:** "A wide breadth of activities are included, eg, oral, written, electronic, virtual communications; organising meetings for others; events; phone calls and emails" (FOCAL Table 3); P/N: "P=limited to influencing legislative changes; N=face-to-face only" (Suppl Table 3).
- **Note:** Same row-design trade-off as scope.1 — set-typed cell vs 8 binary cells. Deferring atomization, same Open Issue FOCAL-2.
- **Note on US federal LDA scoring:** Federal LDA scored 2 (raw 2 × weight 1 = yes). LDA's broad "lobbying contact" + "lobbying activities" cover all 8 FOCAL activity types.

### Timeliness battery (3 items; 1+2 merged in 2025)

#### focal_2024.timeliness.1 + timeliness.2 (MERGED in 2025; weight 3 each → merged weight 3)

- **Compendium rows:** `lobbyist_directory_update_cadence` (typed enum `{daily, weekly, monthly, semiannual_or_less_often, none}`; practical) — HG Q38 NEW; reused here
  [cross-rubric: HG Q38 (4-tier ordinal read); PRI Q4 (binary "current data present"); FOCAL timeliness.1 + .2 (merged 2025, this projection)]
  Pre-existing (HG mapping); FOCAL is the 2nd reader.
- **Cell type:** existing enum.
- **Axis:** `practical_availability`.
- **Scoring rule (merged 2025 weight 3):**
  ```
  cell == daily  → 2 (yes — "real time")
  cell ∈ {weekly, monthly within two weeks}  → 1 (partly — "within two weeks")
  cell ∈ {semiannual_or_less_often, none}  → 0 (no)
  ```
- **Source quote:** "Changes (eg, registering/deregistering lobbyists, new clients) are updated close to real time (eg, daily)" + "Lobbying activities are disclosed close to real time (eg, daily)" (FOCAL Table 3); P/N: "P=within two weeks" (Suppl Table 3 merged note).
- **Note on merge:** L-N 2025 merged these two 2024 indicators (line 202-204). Both 2024 rows read the same compendium cell; the merge applies the projection once with weight 3.
- **Note on US federal LDA scoring:** Federal LDA scored 0 + 0 = 0 (no). LDA's lobbyist registration data is updated quarterly (semi-annually for some employer reports); not "close to real time" at any cadence.

#### focal_2024.timeliness.3 — Ministerial diaries disclosed monthly (weight 1)

- **Compendium rows:** `ministerial_diary_disclosure_cadence` (typed enum `{monthly_or_more, quarterly, less_than_quarterly, no_diary_published, none_required}`; practical OR legal) **NEW**
  [cross-rubric: FOCAL-distinctive (no other contributing rubric reads ministerial diaries); parliamentary-system observable]
- **Cell type:** typed enum.
- **Axis:** `practical_availability` (whether the state actually publishes) — or legal if state law explicitly mandates publication cadence.
- **Scoring rule:**
  ```
  cell == monthly_or_more  → 2 (yes)
  cell == quarterly  → 1 (partly)
  cell ∈ {less_than_quarterly, no_diary_published, none_required}  → 0 (no)
  ```
- **Source quote:** "Ministerial diaries are disclosed monthly (or more frequently)" (FOCAL Table 3); no P/N notes (Suppl Table 3).
- **Note on US applicability:** **Ministerial diaries are a parliamentary-system feature.** US federal and state governments do not have formal "ministerial diary" publication requirements. Some agencies (e.g., White House visitor logs at the federal level) publish meeting logs, but inconsistently and not statute-mandated. For US jurisdictions, the cell is typically `no_diary_published` (= score 0). **Phase C: extract the cell as `no_diary_published` for all US states + Federal_US absent evidence of a state-specific equivalent (e.g., NY's executive transparency portals).** Federal LDA scored 0 (no diary).
- **Note on row utility:** The row exists for cross-jurisdictional comparison (parliamentary systems would populate it differently). For US-focused extraction, the row provides systematic-zero-evidence rather than data signal, but the cell is included for compendium completeness and federal-LDA-parallel scoring (since FOCAL is published for 28 countries, not US-only).

### Openness battery (9 items, all in scope)

FOCAL's "how easy it is to find and use information in the register" — practical-availability portal observables. Strong overlap with CPI #205-206, PRI Q1-Q8, HG Q28-Q38.

#### focal_2024.openness.1 — Lobbyist register is online (weight 2)

- **Compendium rows:** `state_has_dedicated_lobbying_website` (binary; practical)
  [cross-rubric: PRI Q2 (binary read on this cell); HG Q31 (4-tier ordinal on adjacent cell — Q31 reads the spending-report side at finer "photocopies / pdf / searchable / downloadable" granularity, but the binary "exists at all" is the same observable); FOCAL openness.1 reads the binary]
  Pre-existing (PRI mapping; loose-c_009 cluster).
- **Cell type:** binary.
- **Axis:** `practical_availability`.
- **Scoring rule:**
  ```
  cell == TRUE  → 2 (yes — register online)
  cell == FALSE AND optional_registration OR separate_websites  → 1 (partly — "optional registration or separate websites")
  cell == FALSE  → 0 (no)
  ```
- **Source quote:** "Lobbyist register is online" (FOCAL Table 3); P/N: "P=optional registration or separate websites" (Suppl Table 3).
- **Note on partly-tier:** FOCAL's "partly" tier reads a derived condition (optional registration OR separate websites for different lobbyist types). Either condition requires checking the registration-form structure (separate cells), not just the binary. **Phase C**: partly-tier projection may need to OR over `lobbyist_registration_optional_for_some_actor_types` (NEW? or derive from scope.1 cell) AND `lobbyist_registration_split_across_websites_by_actor_type` (NEW?). Flagging as Open Issue FOCAL-3 for the partly-tier mechanics.
- **Note on US federal LDA scoring:** Federal LDA scored 4 (raw 2 × weight 2 = yes). LDA filings are on the Senate LDA site + House LDA site (technically split sites but lobbyists file in both — counts as one logical register).

#### focal_2024.openness.2 — Diaries available online (weight 1)

- **Compendium rows:** `ministerial_diaries_available_online` (binary; practical) **NEW**
  [cross-rubric: FOCAL-distinctive; same parliamentary-system N/A note as timeliness.3]
- **Cell type:** binary.
- **Axis:** `practical_availability`.
- **Scoring rule:** `cell == TRUE → 2; cell == FALSE → 0` (no partly tier in Suppl Table 3).
- **Source quote:** "Diaries available online (eg, lobbyists, ministers, ministerial staff)" (FOCAL Table 3); no P/N (Suppl Table 3).
- **Note on US applicability:** Same N/A note as timeliness.3 — US has no formal ministerial diaries. Cell defaults to FALSE for US jurisdictions absent state-specific transparency portal. Federal LDA scored 0 (no).

#### focal_2024.openness.3 — Available without registration, free, open license, non-proprietary, machine readable (weight 3)

- **Compendium rows:** `lobbying_data_downloadable_in_analytical_format` (binary; practical) AND `lobbying_disclosure_documents_free_to_access` (binary; practical) AND `lobbying_data_no_user_registration_required` (binary; practical) **NEW (no-registration row)** AND `lobbying_data_open_license` (binary; practical) **NEW (license row)**
  [cross-rubric: PRI Q6 + FOCAL openness.3 + FOCAL openness.4 + OpenSecrets `public_avail_downloads` — 4-rubric loose cluster (loose-c_002); CPI #206 reads the 4-feature bundle as a 5-tier practical cell]
  2 existing rows (PRI Q6, CPI #205 derivative) + 2 NEW.
- **Cell type:** 4 binary cells (or one structured cell with 4 sub-fields if compendium prefers a single typed cell — flag for freeze).
- **Axis:** `practical_availability`.
- **Scoring rule:**
  ```
  ALL 4 cells (no_registration AND free AND open_license AND machine_readable AND non_proprietary) → 2 (yes)
  cell.machine_readable AND cell.proprietary_format (eg excel) → 1 (partly — "proprietary format (e.g. excel)")
  NOT cell.machine_readable → 0 (no — "not machine readable")
  ```
- **Source quote:** "Available without registration, free to access, open license (eg, no limits to reuse), non-proprietary format (eg, CSV, not Excel), machine readable" (FOCAL Table 3); P/N: "P=proprietary format (e.g. excel); N=not machine readable" (Suppl Table 3).
- **Note on row count:** FOCAL bundles 5 sub-criteria. Granularity bias splits. PROPOSE 4 cells (the proprietary-vs-non-proprietary distinction is binary on `machine_readable`'s level). Two of the 4 are NEW.
- **Note on US federal LDA scoring:** Federal LDA scored 6 (raw 2 × weight 3 = yes). LDA bulk data downloads are free, no registration required, XML/CSV format, no license restrictions, machine-readable.

#### focal_2024.openness.4 — Downloadable as files/database (weight 3)

- **Compendium rows:** `lobbying_data_downloadable_in_analytical_format` (binary; practical)
  [cross-rubric: PRI Q6, CPI #206, OpenSecrets `public_avail_downloads`, FOCAL openness.3 (reads same cell as one of 4 features); openness.4 reads the binary downloadable-at-all]
  Pre-existing (PRI mapping); FOCAL openness.4 is the 4th reader of this cell.
- **Cell type:** existing binary.
- **Axis:** `practical_availability`.
- **Scoring rule:**
  ```
  cell == TRUE AND complete_data → 2 (yes)
  cell == TRUE AND some_data_not_captured → 1 (partly — "some data not captured")
  cell == FALSE → 0 (no)
  ```
- **Source quote:** "Downloadable (eg, as files, database)" (FOCAL Table 3); P/N: "P=some data not captured" (Suppl Table 3).
- **Note on partly-tier:** "Some data not captured" reads a derived condition over the data-completeness story, not the downloadability binary. **Phase C**: partly-tier likely requires checking against `lobbying_data_completeness_score` (NEW? practical-availability indicator). Flagging as Open Issue FOCAL-4 — may collapse to the binary at coarse projection if "complete data" can't be operationalized.
- **Note on US federal LDA scoring:** Federal LDA scored 3 (raw 1 × weight 3 = partly). LDA bulk downloads exist; some data not captured per L-N 2025 (likely "principal" and "client" data partially).

#### focal_2024.openness.5 — Searchable, simultaneous multi-criteria sorting (weight 3)

- **Compendium rows:** `lobbying_search_simultaneous_multicriteria_capability` (typed `int` ∈ 0..15; practical)
  [cross-rubric: PRI Q8 (binary reading on this cell); OpenSecrets `public_avail_search` ("user-friendly search feature"); FOCAL openness.5 — strict-c_003 + loose-c_010 3-rubric strict cluster]
  Pre-existing (PRI mapping).
- **Cell type:** existing typed int (capacity count, 0-15 search-criteria flags).
- **Axis:** `practical_availability`.
- **Scoring rule:**
  ```
  cell >= 4 (multi-criteria, simultaneous)  → 2 (yes)
  cell ∈ {1, 2, 3} (single-criterion or non-simultaneous)  → 1 (partly — "no simultaneous sorting")
  cell == 0 (no search)  → 0 (no)
  ```
- **Source quote:** "Searchable, simultaneous sorting with multiple criteria" (FOCAL Table 3); P/N: "P=no simultaneous sorting" (Suppl Table 3).
- **Note on US federal LDA scoring:** Federal LDA scored 6 (raw 2 × weight 3 = yes). LDA's online search supports multi-criteria simultaneous (lobbyist name + client name + filing date + topic etc.).

#### focal_2024.openness.6 — Unique identifiers (weight 1)

- **Compendium rows:** `lobbying_disclosure_data_includes_unique_identifiers` (typed `Set[enum{lobbyist_id, individual_id, organization_id, business_registration_id}]`; practical) **NEW**
  [cross-rubric: FOCAL openness.6 + LobbyView `lobbyist_id` schema field (Kim 2018; though Kim 2025 demos identifiers in network analysis, lobbyview.org API exposes them) — 2-rubric where LobbyView's schema-coverage check reads this cell]
- **Cell type:** typed set.
- **Axis:** `practical_availability` (whether published data includes IDs).
- **Scoring rule:**
  ```
  cell ⊇ {lobbyist_id, organization_id}  → 2 (yes)
  cell == {business_registration_id} ONLY → 1 (partly — "only business IDs")
  cell == ∅  → 0 (no)
  ```
- **Source quote:** "Unique identifiers (eg, for lobbyists, individuals, organisations)" (FOCAL Table 3); P/N: "P=only business IDs" (Suppl Table 3).
- **Note on US federal LDA scoring:** Federal LDA scored 2 (raw 2 × weight 1 = yes). LDA assigns lobbyist registration numbers + client identifiers.

#### focal_2024.openness.7 — Linked or interconnected data (weight 1)

- **Compendium rows:** `lobbying_disclosure_data_linked_to_other_datasets` (typed `Set[enum{campaign_finance, voting_records, contract_awards, none}]`; practical) **NEW**
  [cross-rubric: FOCAL-distinctive; LobbyView (Kim 2025) builds these linkages externally rather than via state-portal native support]
- **Cell type:** typed set over datasets the lobbying portal links to.
- **Axis:** `practical_availability`.
- **Scoring rule:** `cell ⊇ {campaign_finance} → 2 (yes); cell == ∅ → 0 (no)` (no partly per Suppl Table 3).
- **Source quote:** "Linked or interconnected data (to other datasets, eg, campaign financing)" (FOCAL Table 3); no P/N (Suppl Table 3).
- **Note on US federal LDA scoring:** Federal LDA scored 2 (raw 2 × weight 1 = yes). LDA's FEC linkages exist (campaign contributions cross-reference).

#### focal_2024.openness.8 — Historical archive published and downloadable (weight 1)

- **Compendium rows:** `lobbying_data_historical_archive_present` (binary; practical)
  [cross-rubric: PRI Q5 (binary reading); FOCAL openness.8 — strict-c_015 + loose-c_019 2-rubric strict cluster]
  Pre-existing (PRI mapping).
- **Cell type:** existing binary.
- **Axis:** `practical_availability`.
- **Scoring rule:**
  ```
  cell == TRUE AND downloadable → 2 (yes)
  cell == TRUE AND viewable_only_not_downloadable → 1 (partly — "not downloadable at once")
  cell == FALSE → 0 (no)
  ```
- **Source quote:** "Historical data in lobbyist register is archived and published; downloadable" (FOCAL Table 3); P/N: "P=not downloadable at once" (Suppl Table 3).
- **Note on partly-tier:** Reads the AND of `historical_archive_present == TRUE` and `lobbying_data_downloadable_in_analytical_format == TRUE` (openness.4 cell). If historical archive viewable but not bulk-downloadable → 1.
- **Note on US federal LDA scoring:** Federal LDA scored 2 (raw 2 × weight 1 = yes). LDA archive is fully downloadable back to 1999.

#### focal_2024.openness.9 — Changes/updates flagged with versioning (weight 1)

- **Compendium rows:** `lobbying_data_changes_flagged_with_versioning` (binary; practical) **NEW**
  [cross-rubric: FOCAL-distinctive; LobbyView captures version info but not as a publicly-flagged update]
- **Cell type:** binary.
- **Axis:** `practical_availability`.
- **Scoring rule:** `cell == TRUE → 2; cell == FALSE → 0`.
- **Source quote:** "Changes or updates documented with a flagging system" (FOCAL Table 3); no P/N (Suppl Table 3).
- **Note on US federal LDA scoring:** Federal LDA scored 2 (raw 2 × weight 1 = yes). LDA filings include amendment-flagging versioning.

### Descriptors battery (6 items, all in scope)

FOCAL's "descriptions and identifying elements of individuals/organisations involved in lobbying" — registration-form content per lobbyist/principal entity.

#### focal_2024.descriptors.1 — Full names (weight 2)

- **Compendium rows:** `lobbyist_reg_form_includes_lobbyist_full_name` (binary; legal) **NEW**
  [cross-rubric: FOCAL-distinctive at reg-form-side granularity; PRI E2b reads `lobbyist_report_includes_lobbyist_contact_info` (spending-report side; α form-type pair candidate)]
- **Cell type:** binary.
- **Axis:** `legal_availability`.
- **Scoring rule:** `cell == TRUE AND not_abbreviated → 2 (yes); cell == TRUE AND incomplete → 1 (partly — "some entries incomplete"); cell == FALSE → 0 (no)`.
- **Source quote:** "Full names of lobbyists/organisations, (not abbreviations or ambiguous names)" (FOCAL Table 3); P/N: "P=some entries incomplete" (Suppl Table 3).
- **Note on near-universal cell value:** US state statutes almost universally require the lobbyist's full name on the reg form. This cell is empirically near-constant TRUE across US states. Same status as Newmark's `def.legislative_lobbying` (no-variation row); kept in compendium per granularity-bias / completeness.
- **Note on US federal LDA scoring:** Federal LDA scored 4 (raw 2 × weight 2 = yes). LDA requires full lobbyist name (employee or individual) on LD-1 / LD-2.

#### focal_2024.descriptors.2 — Contact details (weight 1)

- **Compendium rows:** `lobbyist_reg_form_includes_lobbyist_contact_details` (binary; legal) **NEW**
  [cross-rubric: PRI E2b `lobbyist_report_includes_lobbyist_contact_info` (spending-report side; α form-type pair); FOCAL descriptors.2 is the reg-form side]
- **Cell type:** binary.
- **Axis:** `legal_availability`.
- **Scoring rule:** `TRUE AND complete → 2; TRUE AND incomplete → 1; FALSE → 0`.
- **Source quote:** "Contact details provided (eg, Address, telephone and/or website)" (FOCAL Table 3); P/N: "P=some entries incomplete" (Suppl Table 3).
- **Note on US federal LDA scoring:** Federal LDA scored 2 (raw 2 × weight 1 = yes).

#### focal_2024.descriptors.3 — Legal form (weight 1)

- **Compendium rows:** `lobbyist_reg_form_includes_lobbyist_legal_form` (typed `Optional[enum{public, private, nonprofit, ngo, government, other}]`; legal) **NEW**
  [cross-rubric: FOCAL-distinctive at this granularity]
- **Cell type:** typed enum (or binary "is legal-form disclosed at all" if extraction is harder than enum-typed).
- **Axis:** `legal_availability`.
- **Scoring rule:** `cell IS NOT NULL AND value_provided → 2; cell IS NOT NULL AND incomplete → 1; cell IS NULL → 0`.
- **Source quote:** "Legal form (eg, public, private, not-for-profit, NGO, government)" (FOCAL Table 3); P/N: "P=some entries incomplete" (Suppl Table 3).
- **Note on US federal LDA scoring:** Federal LDA scored 0 (no). LD-1 does not require explicit legal-form classification. (Lobbyists may identify employer type via free-text but no standardized field.)

#### focal_2024.descriptors.4 — Company registration number (weight 1)

- **Compendium rows:** `lobbyist_reg_form_includes_lobbyist_business_id` (binary; legal) **NEW**
  [cross-rubric: FOCAL-distinctive; overlaps openness.6 conceptually (FOCAL reads "are IDs published" practical; descriptors.4 reads "is biz ID required on reg form" legal — distinct observables)]
- **Cell type:** binary.
- **Axis:** `legal_availability`.
- **Scoring rule:** `TRUE AND complete → 2; TRUE AND incomplete → 1; FALSE → 0`.
- **Source quote:** "Company registration number" (FOCAL Table 3); P/N: "P=some entries incomplete" (Suppl Table 3).
- **Note on US federal LDA scoring:** Federal LDA scored 0 (no). LD-1 does not require EIN or other business registration number.

#### focal_2024.descriptors.5 — Sector / sub-sector (weight 1)

- **Compendium rows:** `lobbyist_reg_form_includes_lobbyist_sector` (typed `Optional[<SectorClassification>]`; legal) **NEW**
  [cross-rubric: PRI Q7n / Q7o (search-side reads of sector / subsector — `lobbying_search_filter_by_sector` + `lobbying_search_filter_by_subsector`); FOCAL descriptors.5 is the reg-form-side / register-content side of the same observable family (PRI reads "can users filter by sector"; FOCAL reads "is sector captured on the reg form" — the predicate that makes filtering possible)]
- **Cell type:** typed enum or free-text classification.
- **Axis:** `legal_availability`.
- **Scoring rule:** `cell IS NOT NULL AND complete → 2; partial → 1; null → 0`.
- **Source quote:** "Sector (eg, transport, energy), sub sector" (FOCAL Table 3); P/N: "P=some entries incomplete" (Suppl Table 3).
- **Note on US federal LDA scoring:** Federal LDA scored 2 (raw 2 × weight 1 = yes). LD-2 requires the "general issue area" code (75 categories, e.g., TAX, AGR, HCR), which serves as the sector classification.

#### focal_2024.descriptors.6 — Type of lobbyist contract (weight 1)

- **Compendium rows:** `lobbyist_disclosure_includes_employment_type` (binary; legal)
  [cross-rubric: HG Q10 ("Reg form includes lobbying-work type — compensated/non-compensated/contract/salaried"); FOCAL descriptors.6 (verbatim parallel observable)]
  Pre-existing (HG mapping; HG Q10 introduced as form-agnostic per the locked α decision).
- **Cell type:** existing binary.
- **Axis:** `legal_availability`.
- **Scoring rule:** `TRUE AND complete → 2; TRUE AND incomplete → 1; FALSE → 0`.
- **Source quote:** "Type of lobbyist contract (eg, salaried staff, contracted)" (FOCAL Table 3); P/N: "P=some entries incomplete" (Suppl Table 3).
- **Note:** **2-rubric-confirmed after FOCAL** (HG + FOCAL). HG-4 Open Issue (form-agnostic vs α split into reg/spending pair) — FOCAL also reads form-agnostically, so the form-agnostic cell stays. Decision affirmed by FOCAL's reading.
- **Note on US federal LDA scoring:** Federal LDA scored 0 (no). LD-1 does not require contract-type classification (LDA captures lobbyist names but not whether they're salaried-staff vs contract).

### Relationships battery (4 items, all in scope; 2025 added a 5th item "Lobbyist list" documented below)

#### focal_2024.relationships.1 — Client list (weight 2)

- **Compendium rows:** `lobbyist_report_includes_principal_names` (binary; legal) OR `lobbyist_reg_form_lists_each_employer_or_principal` (binary; legal)
  [cross-rubric: PRI E2c (lobbyist spending-report side); HG Q9 (reg-form side); FOCAL relationships.1 (reads either side)]
  Both pre-existing.
- **Cell type:** binary per row.
- **Axis:** `legal_availability`.
- **Scoring rule:**
  ```
  (lobbyist_report_includes_principal_names == TRUE OR lobbyist_reg_form_lists_each_employer_or_principal == TRUE) AND names_clear_not_abbreviated → 2 (yes)
  abbreviated OR not_listed_together → 1 (partly — "names are abbreviated or unclear; not listed together")
  neither → 0 (no)
  ```
- **Source quote:** "Client list (for all consultant lobbyists and firms)" (FOCAL Table 3); P/N: "P=names are abbreviated or unclear; not listed together" (Suppl Table 3).
- **Note:** OR over reg-form-side + spending-report-side cells (α form-type both readable for this observable). **3-rubric-confirmed** (PRI + HG + FOCAL).
- **Note on US federal LDA scoring:** Federal LDA scored 6 (raw 2 × weight 3 = yes). Wait — Suppl Table 4 says weight 2 for relationships.1; the US row in audit doc says 6 which would be weight 3. Let me re-check the audit: "Relationships: 6 + 2 + 0 + 0 + 0 = 8" — Relationships values 6, 2, 0, 0, 0 = 8 total. Per `relationships.1` weight 2: raw=2 × weight 2 = 4, not 6. **Discrepancy with audit doc** — likely the 6 corresponds to the LATER "Lobbyist list" indicator (2025 addition, weight 3, raw=2) rather than relationships.1. Flagging as Open Issue FOCAL-5 for verification against Suppl Table 5 row-ordering.

  Actually re-examining the audit doc: "Relationships: 6 + 2 + 0 + 0 + 0 = 8" — 5 entries, not 4. The 5th is the 2025 "Lobbyist list" addition. With weights {relationships.1=2, relationships.2=1, relationships.3=1, relationships.4=2, lobbyist_list=3}: scores [4, 2, 0, 0, 0] = 6. But audit shows [6, 2, 0, 0, 0] = 8. Possible: lobbyist_list at weight 3 raw 2 → 6 in position 1 of the audit's calculation (different ordering). Per Suppl Table 5 verbatim (which I haven't seen directly), the actual ordering may differ.

  **For Phase C: read the per-country CSV directly rather than the audit-doc summary** — the CSV has indicator_id keys that resolve the ordering ambiguity. US row contributions resolve there.

#### focal_2024.relationships.2 — Names of sponsors/members (weight 1)

- **Compendium rows:** `principal_or_lobbyist_reg_form_includes_member_or_sponsor_names` (binary; legal) **NEW**
  [cross-rubric: FOCAL-distinctive; structurally similar to "compensation broken by client" (Sunlight #5) but on the membership-source side]
- **Cell type:** binary.
- **Axis:** `legal_availability`.
- **Scoring rule:** `TRUE AND associations_disclose_members → 2 (yes); TRUE AND companies_disclose_memberships_but_associations_not_members → 1 (partly — "companies disclose memberships but associations not their members"); FALSE → 0 (no)`.
- **Source quote:** "Names of all sponsors or members (for associations and representative groups)" (FOCAL Table 3); P/N as above (Suppl Table 3).
- **Note on US federal LDA scoring:** Federal LDA scored 2 (raw 2 × weight 1 = yes). LDA's LD-1 / LD-2 requires "client" disclosure, which for trade associations means the association name itself but not the underlying members. So this should be PARTLY (1) not YES (2). Possible audit-doc discrepancy. Phase C: verify against Suppl Table 5 directly.

#### focal_2024.relationships.3 — Board seats (weight 1)

- **Compendium rows:** `lobbyist_or_principal_reg_form_includes_lobbyist_board_memberships` (binary; legal) **NEW**
  [cross-rubric: FOCAL-distinctive]
- **Cell type:** binary.
- **Axis:** `legal_availability`.
- **Scoring rule:** `TRUE AND clear → 2; TRUE AND abbreviated → 1; FALSE → 0`.
- **Source quote:** "List of board seats held (eg, in associations, companies)" (FOCAL Table 3); P/N: "P=names are abbreviated or unclear" (Suppl Table 3).
- **Note on US federal LDA scoring:** Federal LDA scored 0 (no). LD-1 / LD-2 does not require disclosure of lobbyist board memberships.

#### focal_2024.relationships.4 — Direct business associations with officials (weight 2)

- **Compendium rows:** `lobbyist_disclosure_includes_business_associations_with_officials` (binary; legal)
  [cross-rubric: HG Q22 (introduced this row); FOCAL relationships.4 — **2-rubric-confirmed after FOCAL**, as predicted by the HG mapping]
  Pre-existing (HG mapping).
- **Cell type:** existing binary.
- **Axis:** `legal_availability`.
- **Scoring rule:** `TRUE AND full_relationship_info → 2 (yes); TRUE AND only_yn_no_relationship_details → 1 (partly — "limited to Y/N and no information about nature of relationship"); FALSE → 0 (no)`.
- **Source quote:** "Direct business associations with public officials, candidates or members of their households" (FOCAL Table 3); P/N: "P=limited to Y/N and no information about nature of relationship" (Suppl Table 3).
- **Note on partly-tier:** FOCAL distinguishes between a binary disclosure (yes/no — Q22 reads this) and detailed disclosure (nature of the relationship). Phase C may need a typed cell `business_association_disclosure_detail_level` ∈ {binary_yn, detailed} to support the FOCAL partly-tier; alternatively HG Q22's binary AND a new detail-level cell. Flagging as Open Issue FOCAL-6.
- **Note on US federal LDA scoring:** Federal LDA scored 0 (no). LD-1 / LD-2 does not require disclosure of lobbyist-official relationships.

#### 2025-only addition: "Lobbyist list" (Relationships, weight 3) — NOT in 2024 items_FOCAL.tsv

- **Compendium rows:** `principal_report_lists_lobbyists_employed` (binary; legal) **NEW**
  [cross-rubric: HG Q9 (lobbyist-side parallel `lobbyist_reg_form_lists_each_employer_or_principal`); the 2025 FOCAL addition is the principal-side mirror]
- **Cell type:** binary.
- **Axis:** `legal_availability`.
- **Scoring rule:** `TRUE → 2; partly → 1; FALSE → 0`.
- **Source quote:** "We created an additional indicator for listing the lobbyists employed by a company or lobby firm, as we found this was inconsistently disclosed" (Lacy-Nichols 2025 main text line 213).
- **Note:** Captured here for compendium 2.0 completeness. Phase C extracts this cell + projects via the 2025-only weight-3 reading; Phase C ground-truth uses per-country CSV cell `lobbyist_list` (2025 numbering — exact CSV column name TBD; verify in Phase C).

### Financials battery (11 items, all in scope)

FOCAL's "flow of money spent and earned" — strong overlap with HG / Sunlight / PRI / Newmark / CPI expenditure batteries. **The most US-centric FOCAL category** (paper line 1059-1062).

#### focal_2024.financials.1 — Total lobbying income for consultants (weight 2)

- **Compendium rows:** `lobbyist_spending_report_includes_total_compensation` (binary; legal)  *(scope-restricted to consultant lobbyists by FOCAL framing)*
  [cross-rubric: Sunlight #5 (total compensation row); Newmark 2017/2005 `disc_total_compensation`; HG Q13 (binary lobbyist-side); CPI #201 (compound); PRI E2f_i; Opheim `disclosure.total_income`; FOCAL financials.1 — the **7-rubric-confirmed most-validated row** in the compendium]
  Pre-existing (Sunlight mapping; HG mapping confirmed 7-rubric-status).
- **Cell type:** existing binary.
- **Axis:** `legal_availability`.
- **Scoring rule:** `cell == TRUE → 2 (yes); cell == FALSE → 0 (no)` (no partly tier in Suppl Table 3).
- **Source quote:** "Total lobbying income (for consultant lobbyists/lobby firms)" (FOCAL Table 3); no P/N (Suppl Table 3).
- **Note on FOCAL scope:** FOCAL Table 3 sub-header "For consultant lobbyists & lobby firms" scopes financials.1-3 to consultant lobbyists only. The compendium cell is universal (applies to any lobbyist); FOCAL's projection reads the cell where the lobbyist is a consultant. Practically, the cell value applies uniformly (states don't typically distinguish consultant lobbyists from in-house in disclosure requirements).
- **Note on US federal LDA scoring:** Federal LDA scored 4 (raw 2 × weight 2 = yes). LD-2 requires "Income relating to lobbying activities" disclosure by registrants.

#### focal_2024.financials.2 — Lobbying income per client (weight 2)

- **Compendium rows:** `lobbyist_spending_report_includes_compensation_broken_down_by_client` (binary; legal)  *(scope-restricted to consultant lobbyists)*
  [cross-rubric: Sunlight #5 (broken-down-by-client row); Newmark 2017/2005 `disc_compensation_by_employer`; HG Q13 footnote; CPI #201 (compound); FOCAL financials.2 — **5-rubric-confirmed**]
  Pre-existing (Sunlight mapping).
- **Cell type:** existing binary.
- **Axis:** `legal_availability`.
- **Scoring rule:** `TRUE → 2; FALSE → 0`.
- **Source quote:** "Lobbying income per client" (FOCAL Table 3); no P/N (Suppl Table 3).
- **Note on US federal LDA scoring:** Federal LDA scored 4 (raw 2 × weight 2 = yes). LD-2 requires per-client income reporting.

#### focal_2024.financials.3 — Income sources and amounts (weight 2)

- **Compendium rows:** `consultant_lobbyist_report_includes_income_by_source_type` (typed `Set[enum{government_agency, foundation, company, individual, other}]`; legal) **NEW**
  [cross-rubric: FOCAL-distinctive at the source-type level]
- **Cell type:** typed set with per-source-type amount.
- **Axis:** `legal_availability`.
- **Scoring rule:** `cell complete (sources and amounts) → 2 (yes); cell incomplete (sources or amounts in bandwidths) → 1 (partly — "amounts or sources are not specified or in bandwidths"); cell null → 0 (no)`.
- **Source quote:** "Income sources (eg, including government agencies, grant-making foundations, companies) and amount received" (FOCAL Table 3); P/N: "P=amounts or sources are not specified or in bandwidths" (Suppl Table 3).
- **Note on relationship to financials.2:** financials.2 = compensation broken by client (per-paying-entity, identifiable clients). financials.3 = income by source TYPE (which categories of payer). The two are conceptually distinct: a state can require per-client (FOCAL .2) without requiring source-type categorization (FOCAL .3) and vice versa.
- **Note on US federal LDA scoring:** Federal LDA scored 0 (no). LDA's per-client reporting (financials.2) does not categorize source TYPE; it lists specific clients.

#### focal_2024.financials.4 — Number of lobbyists employed/contracted (total + FTE) (weight 1)

- **Compendium rows:** `lobbyist_or_principal_report_includes_lobbyist_count_total_and_FTE` (typed `Optional[{count: int, fte: Optional[Decimal]}]`; legal) **NEW**
  [cross-rubric: FOCAL-distinctive]
- **Cell type:** typed structured value.
- **Axis:** `legal_availability`.
- **Scoring rule:** `cell with both count and FTE → 2 (yes); cell with count only (no FTE) → 1 (partly — "FTE is not specified"); cell null → 0 (no)`.
- **Source quote:** "Number of lobbyists employed/contracted (total and full-time equivalent)" (FOCAL Table 3); P/N: "P=FTE is not specified" (Suppl Table 3).
- **Note on US federal LDA scoring:** Federal LDA scored 0 (no). LDA's LD-1 lists lobbyists by name on registration but does not require FTE counts; LD-2 is per-client not per-lobbyist count.

#### focal_2024.financials.5 — Amount of time on lobbying (weight 2)

- **Compendium rows:** `lobbyist_or_principal_report_includes_time_spent_on_lobbying` (typed `Optional[<TimeSpent>]`; legal) **NEW**
  [cross-rubric: FOCAL-distinctive at the disclosure-side level; Federal LDA's 20%-of-time DEFINITIONAL threshold (`time_threshold_for_lobbyist_registration` row) is a different observable — registration trigger, not reporting content]
- **Cell type:** typed structured value (hours, days, or % of work time).
- **Axis:** `legal_availability`.
- **Scoring rule:** `cell IS NOT NULL → 2 (yes); cell IS NULL → 0 (no)` (no partly per Suppl Table 3).
- **Source quote:** "Amount of time spent on lobbying" (FOCAL Table 3); no P/N (Suppl Table 3).
- **Note on relationship to scope.2 (and time threshold cell):** scope.2 reads the DEFINITIONAL threshold (does the state's lobbyist definition trigger based on time spent? — cell value is the threshold itself). financials.5 reads the REPORTING content (does the lobbyist's filing disclose the time spent? — cell value is the disclosed time amount). Distinct cells, distinct readings.
- **Note on US federal LDA scoring:** Federal LDA scored 0 (no). LDA does not require reporting of time spent on lobbying per filing period (only the 20% definitional trigger at registration).

#### focal_2024.financials.6 — Total lobbying expenditure (both in-house and consulting) (weight 2)

- **Compendium rows:** `lobbyist_spending_report_includes_total_expenditures` (binary; legal) AND `principal_report_includes_total_expenditures` (binary; legal) **NEW (principal-side)**
  [cross-rubric: Newmark 2017 `disclosure.total_expenditures` (introduced the lobbyist-side row); Newmark 2005 `disc_total_expenditures`; Opheim `disclosure.total_spending`; HG Q11 gateway (implicit); CPI #201 compound (implicit); FOCAL financials.6 reads BOTH actor sides AND-projected ("both in-house and consulting")]
  Lobbyist-side pre-existing (Newmark 2017 mapping); principal-side NEW.
- **Cell type:** binary per row.
- **Axis:** `legal_availability`.
- **Scoring rule:**
  ```
  (lobbyist_report_total_expenditures == TRUE AND principal_report_total_expenditures == TRUE) → 2 (yes)
  one of two TRUE  → 1 (partly — "general bandwidth")
  both FALSE  → 0 (no)
  ```
- **Source quote:** "Total lobbying expenditure (both in-house and consulting)" (FOCAL Table 3); P/N: "P=general bandwidth" (Suppl Table 3).
- **Note on principal-side parallel:** FOCAL's "both in-house and consulting" framing means in-house lobbying (typically reported on the PRINCIPAL'S report) is included alongside consulting (typically on the LOBBYIST'S report). PROPOSE NEW `principal_report_includes_total_expenditures` parallel to existing lobbyist-side row.
- **Note on US federal LDA scoring:** Federal LDA scored 4 (raw 2 × weight 2 = yes). LD-2 requires expenditure totals from both lobbyist registrants and (per-client) for registrants representing clients.

#### focal_2024.financials.7 — Compensated / uncompensated activities (weight 2)

- **Compendium rows:** `lobbyist_reg_form_or_report_includes_compensation_status_flag` (binary; legal) **NEW**
  [cross-rubric: HG Q10 (Reg form: lobbying-work type includes compensated/non-compensated/contract/salaried — covers compensation status partially); FOCAL financials.7 — 2-rubric-confirmed if HG Q10's enum cell value covers FOCAL's binary read]
- **Cell type:** binary (or derived from HG Q10's enum cell).
- **Axis:** `legal_availability`.
- **Scoring rule:** `TRUE → 2; FALSE → 0`.
- **Source quote:** "Compensated/uncompensated lobbying activities" (FOCAL Table 3); no P/N (Suppl Table 3).
- **Note on cross-rubric reuse:** HG Q10's cell `lobbyist_disclosure_includes_employment_type` (enum {compensated, non-compensated, contract, salaried}) covers FOCAL's binary "is compensation status disclosed" via `cell IS NOT NULL`. **Likely reuse:** read existing HG cell as `cell IS NOT NULL → 2; cell IS NULL → 0`. **DECISION: reuse `lobbyist_disclosure_includes_employment_type` (HG Q10) via `IS NOT NULL` projection.** No new row.
- **Note on US federal LDA scoring:** Federal LDA scored 0 (no). LDA's LD-1 employee disclosure does not formally distinguish compensated vs uncompensated (all lobbyists are presumed compensated under the 20% threshold definition).

#### focal_2024.financials.8 — Expenditure per issue (weight 2)

- **Compendium rows:** `lobbyist_spending_report_includes_expenditure_per_issue` (binary; legal) **NEW**
  [cross-rubric: FOCAL-distinctive in current set; HG Q15-Q19 itemize expenditures per-transaction not per-issue; PRI E1g_ii/E2g_ii read bill_id but not expenditure-allocation; FOCAL financials.8 is the only contributing-set reader of "spending broken by lobbying issue"]
- **Cell type:** binary.
- **Axis:** `legal_availability`.
- **Scoring rule:** `TRUE → 2; FALSE → 0`.
- **Source quote:** "Expenditure per issue" (FOCAL Table 3); no P/N (Suppl Table 3).
- **Note on US federal LDA scoring:** Federal LDA scored 0 (no). LD-2 does not require expenditure allocation per specific issue / bill; quarterly totals are aggregate.

#### focal_2024.financials.9 — Expenditure on membership/sponsorship (weight 1)

- **Compendium rows:** `lobbyist_or_principal_report_includes_trade_association_dues_or_sponsorship` (binary; legal) **NEW**
  [cross-rubric: FOCAL-distinctive]
- **Cell type:** binary.
- **Axis:** `legal_availability`.
- **Scoring rule:** `TRUE → 2; FALSE → 0`.
- **Source quote:** "Expenditure on membership/sponsorship of organisations that lobby (eg, trade associations)" (FOCAL Table 3); no P/N (Suppl Table 3).
- **Note on US federal LDA scoring:** Federal LDA scored 0 (no). LD-2 does not require disclosure of trade association dues paid by registrant principals.

#### focal_2024.financials.10 — Expenditures benefitting officials (weight 2)

- **Compendium rows:** `lobbyist_report_includes_gifts_entertainment_transport_lodging` (binary; legal) OR `principal_report_includes_gifts_entertainment_transport_lodging` (binary; legal)
  [cross-rubric: PRI E1f_iii (principal-side; loose-c_030); PRI E2f_iii (lobbyist-side); Newmark 2017/2005 `disc.expenditures_benefiting_officials`; Opheim `disclosure.expenditures_benefitting_public_employees`; HG Q14 (categorized totals — partial); HG Q23 (gifts statutory provision — disclosure portion partial); FOCAL financials.10 — **5-rubric-confirmed at combined granularity, the most-validated bundle in the compendium**]
  Pre-existing (PRI mapping; 5+ readers in the contributing set).
- **Cell type:** binary per row.
- **Axis:** `legal_availability`.
- **Scoring rule:** `(lobbyist_side OR principal_side) AND complete → 2; partial → 1; FALSE → 0`.
- **Source quote:** "Expenditures benefitting public officials or employees including financial/non-financial gifts and support, employer/principal on whose behalf expenses were made" (FOCAL Table 3); no P/N (Suppl Table 3).
- **Note:** **Most-validated row family across the contributing set.** No new rows.
- **Note on US federal LDA scoring:** Federal LDA scored 0 (no). LDA does not require gift/expenditure disclosure (the Honest Leadership and Open Government Act of 2007 added some semi-annual contribution disclosures but not the broad gift-and-benefit reporting FOCAL expects).

#### focal_2024.financials.11 — Campaign/political contributions including in-kind (weight 2)

- **Compendium rows:** `lobbyist_report_includes_campaign_contributions` (binary; legal)
  [cross-rubric: HG Q24 (disclosure-side read of campaign contributions on lobbyist spending report); FOCAL financials.11 — **2-rubric-confirmed after FOCAL** (HG + FOCAL)]
  Pre-existing (HG mapping).
- **Cell type:** existing binary.
- **Axis:** `legal_availability`.
- **Scoring rule:** `TRUE → 2; FALSE → 0`.
- **Source quote:** "Campaign/political contributions, including in-kind" (FOCAL Table 3); no P/N (Suppl Table 3).
- **Note on US federal LDA scoring:** Federal LDA scored 4 (raw 2 × weight 2 = yes). LD-203 (semi-annual contribution report under HLOGA) requires disclosure of political contributions by lobbyists and PACs they control.

### Contact log battery (11 items, all in scope) — FOCAL's most-distinctive battery

FOCAL's "activities of lobbyists" — per-meeting / per-contact granularity. Strongest atomization in current contributing set; PRI's `_includes_contacts_made` (E1i/E2i) is the coarse parent binary that FOCAL atomizes into 11 sub-fields. **9 of 11 contact_log items are NEW rows.**

#### focal_2024.contact_log.1 — Organisation/interest represented (weight 2)

- **Compendium rows:** `lobbying_contact_log_includes_beneficiary_organization` (binary; legal) **NEW**
  [cross-rubric: PRI E1i / E2i (coarse-parent binary, "are contacts disclosed at all"); FOCAL contact_log.1 (finer-grained read of the parent binary's sub-content)]
- **Cell type:** binary.
- **Axis:** `legal_availability`.
- **Scoring rule:** `TRUE AND complete → 2; partly → 1 (P=some entries incomplete); FALSE → 0`.
- **Source quote:** "Organisation/interest(s) represented (beneficiary)" (FOCAL Table 3); P/N: "P=some entries incomplete" (Suppl Table 3).
- **Note on US federal LDA scoring:** Federal LDA scored 2 (raw 1 × weight 2 = partly). LD-2 requires the "client" — the beneficiary organization — to be identified on lobbying reports, but the granularity of identification is incomplete for some entries.

#### focal_2024.contact_log.2 — Names of persons contacted (weight 2)

- **Compendium rows:** `lobbying_contact_log_includes_official_contacted_name` (binary; legal) **NEW**
  [cross-rubric: PRI E1i / E2i (coarse parent)]
- **Cell type:** binary.
- **Axis:** `legal_availability`.
- **Scoring rule:** `TRUE AND complete → 2; partly → 1; FALSE → 0`.
- **Source quote:** "Names of persons contacted and their position/role" (FOCAL Table 3); P/N: "P=some entries incomplete" (Suppl Table 3).
- **Note on US federal LDA scoring:** Federal LDA scored 0 (no). LD-2 lists the "chambers and Federal agencies contacted" but not specific persons (individual officials).

#### focal_2024.contact_log.3 — Institution/department contacted (weight 2)

- **Compendium rows:** `lobbying_contact_log_includes_institution_or_department` (binary; legal) **NEW**
  [cross-rubric: PRI E1i / E2i (coarse parent); HG Q1 target-side recognition is a definitional precursor, not a per-meeting reading]
- **Cell type:** binary.
- **Axis:** `legal_availability`.
- **Scoring rule:** `TRUE AND complete → 2; partly → 1; FALSE → 0`.
- **Source quote:** "Institution/department contacted" (FOCAL Table 3); P/N: "P=some entries incomplete" (Suppl Table 3).
- **Note on US federal LDA scoring:** Federal LDA scored 2 (raw 1 × weight 2 = partly). LD-2 requires "Specific houses of Congress and Federal agencies contacted" — the institution but not necessarily the department/sub-unit.

#### focal_2024.contact_log.4 — Meeting attendees (weight 1)

- **Compendium rows:** `lobbying_contact_log_includes_meeting_attendees` (binary; legal) **NEW**
- **Cell type:** binary.
- **Axis:** `legal_availability`.
- **Scoring rule:** `TRUE → 2; partly → 1; FALSE → 0`.
- **Source quote:** "If a meeting, names of all attendees" (FOCAL Table 3); P/N: "P=some entries incomplete" (Suppl Table 3).
- **Note on US federal LDA scoring:** Federal LDA scored 0 (no). Per-meeting attendee disclosure not required by LDA.

#### focal_2024.contact_log.5 — Date (weight 2)

- **Compendium rows:** `lobbying_contact_log_includes_date` (binary; legal) **NEW**
- **Cell type:** binary.
- **Axis:** `legal_availability`.
- **Scoring rule:** `TRUE AND specific_date → 2; date_range_only → 1 (P=date range provided); FALSE → 0`.
- **Source quote:** "Date" (FOCAL Table 3); P/N: "P=date range provided" (Suppl Table 3).
- **Note on US federal LDA scoring:** Federal LDA scored 0 (no). LD-2 reports quarterly aggregate, not per-meeting dates.

#### focal_2024.contact_log.6 — Form (in person / video / phone) (weight 2)

- **Compendium rows:** `lobbying_contact_log_includes_communication_form` (typed `Optional[enum{in_person, video, phone, written, electronic}]`; legal) **NEW**
- **Cell type:** typed enum.
- **Axis:** `legal_availability`.
- **Scoring rule:** `TRUE → 2; FALSE → 0`.
- **Source quote:** "Form (eg, in person meeting, video conference, phone call)" (FOCAL Table 3); no P/N (Suppl Table 3).
- **Note on US federal LDA scoring:** Federal LDA scored 0 (no).

#### focal_2024.contact_log.7 — Location (weight 1)

- **Compendium rows:** `lobbying_contact_log_includes_location` (binary; legal) **NEW**
- **Cell type:** binary.
- **Axis:** `legal_availability`.
- **Scoring rule:** `TRUE → 2; FALSE → 0`.
- **Source quote:** "Location" (FOCAL Table 3); no P/N (Suppl Table 3).
- **Note on US federal LDA scoring:** Federal LDA scored 0 (no).

#### focal_2024.contact_log.8 — Materials shared (weight 1)

- **Compendium rows:** `lobbying_contact_log_includes_materials_shared` (binary; legal) **NEW**
- **Cell type:** binary.
- **Axis:** `legal_availability`.
- **Scoring rule:** `TRUE → 2; FALSE → 0`.
- **Source quote:** "Any materials that were shared, excluding commercially sensitive materials (before, during and after the meeting)" (FOCAL Table 3); no P/N (Suppl Table 3).
- **Note on US federal LDA scoring:** Federal LDA scored 0 (no).

#### focal_2024.contact_log.9 — Topics/issues discussed (weight 3)

- **Compendium rows:** `lobbying_contact_log_includes_topics_discussed` (binary; legal) **NEW**
  [cross-rubric: PRI E2g_i / E1g_i (general-subject-matter rows — coarser parent of FOCAL contact_log.9's per-meeting read); HG Q5/Q20 subject-tier (reg-form / spending-report side — coarser granularity than per-meeting)]
- **Cell type:** binary.
- **Axis:** `legal_availability`.
- **Scoring rule:** `TRUE AND specific → 2; vague_or_unclear → 1 (P); FALSE → 0`.
- **Source quote:** "Topics/issues discussed" (FOCAL Table 3); P/N: "P=description is vague or unclear" (Suppl Table 3).
- **Note on relationship to subject_matter row:** The compendium has `lobbyist_spending_report_includes_general_subject_matter` (Sunlight + HG + Newmark + PRI + Opheim). That's the AGGREGATE-period read (what topics did the lobbyist work on this quarter). FOCAL contact_log.9 is the PER-MEETING read. Different granularity; PROPOSE NEW row for per-meeting topics rather than reusing the aggregate-period row.
- **Note on US federal LDA scoring:** Federal LDA scored 3 (raw 1 × weight 3 = partly). LD-2 "Specific lobbying issues" requires topic disclosure but at aggregate (quarterly), not per-meeting; FOCAL scores this as partly because the disclosure exists but is not at the per-meeting granularity FOCAL expects.

#### focal_2024.contact_log.10 — Outcomes / position on bill (weight 3)

- **Compendium rows:** `lobbyist_spending_report_includes_position_on_bill` (binary; legal)
  [cross-rubric: Sunlight #1 (β AND pair with bill_id); Opheim `disclosure.legislation_supported_or_opposed` (β AND); FOCAL contact_log.10 — **3-rubric-confirmed**]
  Pre-existing (Sunlight mapping; β AND-projection family).
- **Cell type:** existing binary.
- **Axis:** `legal_availability`.
- **Scoring rule:** `TRUE AND specific → 2; vague → 1; FALSE → 0`.
- **Source quote:** "Outcomes sought (eg, legislation/policies supported/opposed)" (FOCAL Table 3); P/N: "P=description is vague or unclear" (Suppl Table 3).
- **Note on US federal LDA scoring:** Federal LDA scored 0 (no). LD-2 does not require disclosure of position taken on bills (only that the lobbyist worked on them).

#### focal_2024.contact_log.11 — Bill numbers / legislation (weight 3)

- **Compendium rows:** `lobbyist_spending_report_includes_bill_or_action_identifier` (binary; legal) OR `lobbyist_reg_form_includes_bill_or_action_identifier` (binary; legal)
  [cross-rubric: Sunlight #1 (α form-type split — both sides); HG Q20 bill-tier (spending-report side); HG Q5 bill-tier (reg-form side); PRI E2g_ii / E1g_ii (lobbyist + principal spending-report sides); FOCAL contact_log.11 — **4-rubric-confirmed (Sunlight + HG + PRI + FOCAL)**]
  Pre-existing (Sunlight mapping + HG α split).
- **Cell type:** binary per row.
- **Axis:** `legal_availability`.
- **Scoring rule:** `(reg_form OR spending_report) AND specific_to_communication → 2; general_list → 1 (P="if general list not specific to the communication"); FALSE → 0`.
- **Source quote:** "Targeted areas of public policy or legislation, including a list of official legislative references/bill numbers/measures etc" (FOCAL Table 3); P/N: "P=if general list not specific to the communication" (Suppl Table 3).
- **Note on US federal LDA scoring:** Federal LDA scored 3 (raw 1 × weight 3 = partly). LD-2 requires "Specific bills" be listed but at aggregate (quarterly), not per-meeting communication-specific — partly per FOCAL.

---

## Summary of compendium rows touched

| Row id (working name) | Cell type | Axis | FOCAL items reading | Cross-rubric readers (dedupe candidates) | Status |
|---|---|---|---|---|---|
| `lobbyist_definition_included_actor_types` | typed Set[enum] (9 types) | legal | scope.1 | FOCAL-distinctive at organizational-actor-type level | **NEW** |
| `compensation_threshold_for_lobbyist_registration` | typed Optional[Decimal] | legal | scope.2 | CPI #197 (3-tier), HG Q2 (5-tier), Newmark 2017/2005/Opheim IS NOT NULL | existing (CPI mapping) |
| `expenditure_threshold_for_lobbyist_registration` | typed Optional[Decimal] | legal | scope.2 | Newmark 2017/2005/Opheim IS NOT NULL | existing (Newmark 2017 mapping) |
| `time_threshold_for_lobbyist_registration` | typed Optional[TimeThreshold] | legal | scope.2 | Newmark 2017/2005/Opheim IS NOT NULL, Federal LDA 20% rule | existing (Newmark 2017 mapping) |
| `def_target_legislative_branch` | binary | legal | scope.3 | CPI #196, HG Q1, Newmark 2017/2005, Opheim, PRI A7 (actor-side parallel) | existing (CPI mapping) |
| `def_target_executive_agency` | binary | legal | scope.3 | CPI #196, HG Q1, Newmark 2017/2005, Opheim | existing (CPI mapping) |
| `def_target_governors_office` | binary | legal | scope.3 | CPI #196, HG Q1 | existing (CPI mapping) |
| `def_target_legislative_or_executive_staff` | binary | legal | scope.3 | FOCAL-distinctive | **NEW** |
| `lobbying_definition_included_activity_types` | typed Set[enum] (8 types) | legal | scope.4 | FOCAL-distinctive at activity-type level | **NEW** |
| `lobbyist_directory_update_cadence` | typed enum | practical | timeliness.1 + .2 (merged) | HG Q38, PRI Q4 (coarser) | existing (HG mapping) |
| `ministerial_diary_disclosure_cadence` | typed enum | practical | timeliness.3 | FOCAL-distinctive (parliamentary-system observable) | **NEW** |
| `state_has_dedicated_lobbying_website` | binary | practical | openness.1 | PRI Q2, HG Q31, loose-c_009 | existing (PRI mapping) |
| `ministerial_diaries_available_online` | binary | practical | openness.2 | FOCAL-distinctive | **NEW** |
| `lobbying_data_downloadable_in_analytical_format` | binary | practical | openness.3, openness.4 | PRI Q6, CPI #206, OpenSecrets (tabled), loose-c_002 | existing (PRI mapping) |
| `lobbying_disclosure_documents_free_to_access` | binary | practical | openness.3 | CPI #205 (derivative) | existing (CPI mapping) |
| `lobbying_data_no_user_registration_required` | binary | practical | openness.3 | FOCAL-distinctive | **NEW** |
| `lobbying_data_open_license` | binary | practical | openness.3 | FOCAL-distinctive | **NEW** |
| `lobbying_search_simultaneous_multicriteria_capability` | typed int 0..15 | practical | openness.5 | PRI Q8, OpenSecrets (tabled), strict-c_003 | existing (PRI mapping) |
| `lobbying_disclosure_data_includes_unique_identifiers` | typed Set[enum] | practical | openness.6 | LobbyView schema-coverage check | **NEW** |
| `lobbying_disclosure_data_linked_to_other_datasets` | typed Set[enum] | practical | openness.7 | FOCAL-distinctive | **NEW** |
| `lobbying_data_historical_archive_present` | binary | practical | openness.8 | PRI Q5, strict-c_015 | existing (PRI mapping) |
| `lobbying_data_changes_flagged_with_versioning` | binary | practical | openness.9 | FOCAL-distinctive | **NEW** |
| `lobbyist_reg_form_includes_lobbyist_full_name` | binary | legal | descriptors.1 | FOCAL-distinctive at reg-form-side granularity | **NEW** |
| `lobbyist_reg_form_includes_lobbyist_contact_details` | binary | legal | descriptors.2 | PRI E2b α-form-pair (spending-report side exists) | **NEW** |
| `lobbyist_reg_form_includes_lobbyist_legal_form` | typed Optional[enum] | legal | descriptors.3 | FOCAL-distinctive | **NEW** |
| `lobbyist_reg_form_includes_lobbyist_business_id` | binary | legal | descriptors.4 | FOCAL-distinctive | **NEW** |
| `lobbyist_reg_form_includes_lobbyist_sector` | typed Optional[<SectorClassification>] | legal | descriptors.5 | PRI Q7n/Q7o (search-filter side reads sector data — different observable axis) | **NEW** |
| `lobbyist_disclosure_includes_employment_type` | binary | legal | descriptors.6 | HG Q10, FOCAL descriptors.6 — 2-rubric-confirmed | existing (HG mapping) |
| `lobbyist_report_includes_principal_names` | binary | legal | relationships.1 | PRI E2c, FOCAL relationships.1, strict-c_016 | existing (PRI mapping) |
| `lobbyist_reg_form_lists_each_employer_or_principal` | binary | legal | relationships.1 | HG Q9, FOCAL relationships.1 (α form-pair) | existing (HG mapping) |
| `principal_or_lobbyist_reg_form_includes_member_or_sponsor_names` | binary | legal | relationships.2 | FOCAL-distinctive | **NEW** |
| `lobbyist_or_principal_reg_form_includes_lobbyist_board_memberships` | binary | legal | relationships.3 | FOCAL-distinctive | **NEW** |
| `lobbyist_disclosure_includes_business_associations_with_officials` | binary | legal | relationships.4 | HG Q22, FOCAL relationships.4 — 2-rubric-confirmed | existing (HG mapping) |
| `lobbyist_spending_report_includes_total_compensation` | binary | legal | financials.1 | Sunlight #5, Newmark 2017/2005, HG Q13, CPI #201, PRI E2f_i, Opheim, FOCAL — **7-rubric-confirmed; most-validated row in compendium** | existing (Sunlight mapping) |
| `lobbyist_spending_report_includes_compensation_broken_down_by_client` | binary | legal | financials.2 | Sunlight #5, Newmark 2017/2005, HG Q13 footnote, CPI #201, FOCAL — **5-rubric-confirmed** | existing (Sunlight mapping) |
| `consultant_lobbyist_report_includes_income_by_source_type` | typed Set[enum] + amounts | legal | financials.3 | FOCAL-distinctive at source-type granularity | **NEW** |
| `lobbyist_or_principal_report_includes_lobbyist_count_total_and_FTE` | typed Optional[<count + FTE>] | legal | financials.4 | FOCAL-distinctive | **NEW** |
| `lobbyist_or_principal_report_includes_time_spent_on_lobbying` | typed Optional[<TimeSpent>] | legal | financials.5 | FOCAL-distinctive (distinct from time_threshold cell which is definitional) | **NEW** |
| `lobbyist_spending_report_includes_total_expenditures` | binary | legal | financials.6 (lobbyist side) | Newmark 2017/2005, Opheim, HG Q11 gateway, CPI #201 compound, FOCAL | existing (Newmark 2017 mapping) |
| `principal_report_includes_total_expenditures` | binary | legal | financials.6 (principal side) | FOCAL-distinctive at principal-side | **NEW** |
| `lobbyist_spending_report_includes_expenditure_per_issue` | binary | legal | financials.8 | FOCAL-distinctive | **NEW** |
| `lobbyist_or_principal_report_includes_trade_association_dues_or_sponsorship` | binary | legal | financials.9 | FOCAL-distinctive | **NEW** |
| `lobbyist_report_includes_gifts_entertainment_transport_lodging` | binary | legal | financials.10 (via OR with principal side) | PRI E2f_iii, Newmark 2017/2005, Opheim, HG Q23/14, FOCAL — 5-rubric-confirmed | existing (PRI mapping) |
| `principal_report_includes_gifts_entertainment_transport_lodging` | binary | legal | financials.10 (via OR with lobbyist side) | PRI E1f_iii, Newmark 2017/2005, Opheim, HG Q23/14, FOCAL — 5-rubric-confirmed | existing (PRI mapping) |
| `lobbyist_report_includes_campaign_contributions` | binary | legal | financials.11 | HG Q24, FOCAL — 2-rubric-confirmed | existing (HG mapping) |
| `lobbying_contact_log_includes_beneficiary_organization` | binary | legal | contact_log.1 | PRI E1i/E2i coarse parent | **NEW** |
| `lobbying_contact_log_includes_official_contacted_name` | binary | legal | contact_log.2 | PRI E1i/E2i coarse parent | **NEW** |
| `lobbying_contact_log_includes_institution_or_department` | binary | legal | contact_log.3 | PRI E1i/E2i coarse parent | **NEW** |
| `lobbying_contact_log_includes_meeting_attendees` | binary | legal | contact_log.4 | FOCAL-distinctive | **NEW** |
| `lobbying_contact_log_includes_date` | binary | legal | contact_log.5 | FOCAL-distinctive | **NEW** |
| `lobbying_contact_log_includes_communication_form` | typed Optional[enum] | legal | contact_log.6 | FOCAL-distinctive | **NEW** |
| `lobbying_contact_log_includes_location` | binary | legal | contact_log.7 | FOCAL-distinctive | **NEW** |
| `lobbying_contact_log_includes_materials_shared` | binary | legal | contact_log.8 | FOCAL-distinctive | **NEW** |
| `lobbying_contact_log_includes_topics_discussed` | binary | legal | contact_log.9 | FOCAL-distinctive at per-meeting granularity; PRI/Sunlight/HG read aggregate-period subject | **NEW** |
| `lobbyist_spending_report_includes_position_on_bill` | binary | legal | contact_log.10 | Sunlight #1, Opheim (β AND), FOCAL — 3-rubric-confirmed | existing (Sunlight mapping) |
| `lobbyist_spending_report_includes_bill_or_action_identifier` | binary | legal | contact_log.11 (spending-report side) | Sunlight #1, HG Q20, PRI E2g_ii, Opheim, FOCAL — 5-rubric-confirmed | existing (Sunlight mapping) |
| `lobbyist_reg_form_includes_bill_or_action_identifier` | binary | legal | contact_log.11 (reg-form side) | Sunlight #1, HG Q5, FOCAL — 3-rubric-confirmed | existing (Sunlight mapping) |
| `principal_report_lists_lobbyists_employed` | binary | legal | 2025-only "Lobbyist list" | HG Q9 (principal-side mirror) | **NEW (documented; not in 2024 TSV)** |

**Total distinct compendium rows touched: 57** across 48 in-scope 2024 indicators (some indicators read multiple rows; some rows are read by multiple indicators).

**Reuse breakdown:**
- **Existing rows reused: 22** (38.5%)
- **NEW rows added by this mapping: 35** (including 1 row for the 2025 "Lobbyist list" 2025-only addition)

**Per-battery reuse rates:**
- scope: 3/8 reused (37.5%; 3 threshold cells + 3 target cells reused, 4 new: 1 set-typed actor-types, 1 staff target, 1 set-typed activity-types, plus this is at row level not item level)
- timeliness: 1/2 reused (50%)
- openness: 5/10 reused (50%)
- descriptors: 1/6 reused (16.7%) — FOCAL-distinctive battery
- relationships: 3/5 reused (60%; including 2025 lobbyist_list)
- financials: 6/11 reused (54.5%)
- contact_log: 3/12 reused (25%) — FOCAL-distinctive battery (9 NEW contact_log cells)

**Cross-rubric promotion levels after FOCAL mapping:**
- `lobbyist_spending_report_includes_total_compensation` → **7-rubric-confirmed** (FOCAL is the 7th reader; same status as after HG)
- `lobbyist_spending_report_includes_compensation_broken_down_by_client` → **5-rubric-confirmed**
- Gifts/entertainment/transport/lodging bundle (`lobbyist_report_includes_*` + `principal_report_includes_*`) → **5-rubric-confirmed at combined granularity** (PRI + Newmark 2017/2005 + Opheim + HG + FOCAL — counting PRI's pair as one rubric-read this is 5; counting separately this is 5+)
- `lobbyist_spending_report_includes_bill_or_action_identifier` → **5-rubric-confirmed** (Sunlight + HG + PRI + Opheim + FOCAL)
- `lobbyist_spending_report_includes_position_on_bill` → **3-rubric-confirmed** (Sunlight + Opheim + FOCAL)
- `lobbyist_report_includes_campaign_contributions` → **2-rubric-confirmed** (HG + FOCAL)
- `lobbyist_disclosure_includes_business_associations_with_officials` → **2-rubric-confirmed** (HG + FOCAL)
- `lobbyist_disclosure_includes_employment_type` → **2-rubric-confirmed** (HG + FOCAL)

---

## Promotions for compendium 2.0 freeze planning

After FOCAL mapping (8 of 9 score-projection rubrics done), the following row-family observations feed into the compendium 2.0 freeze brainstorm:

1. **The `lobbyist_or_principal_report_includes_contributions_received_for_lobbying` row remains single-rubric across 8 of 9 contributing rubrics** (Newmark 2017 only).
   - **FOCAL `financials.*` battery WAS the strongest remaining promotion candidate per the 2026-05-11 handoff, BUT walking FOCAL's 11 financials items confirms NO PARALLEL.**
   - FOCAL financials.1 = total income (own pay, not third-party-contributions); .2 = income per client (per-client breakdown, not third-party); .3 = income source types (which categories of payer — closest candidate, but reads sources of OWN income not third-party-contributions earmarked for lobbying); .4 = lobbyist count; .5 = time spent; .6 = total expenditure; .7 = compensated/uncompensated status; .8 = expenditure per issue; .9 = trade association dues (closest candidate — money OUT to third-party orgs that lobby, not money IN from third parties for own lobbying); .10 = gifts to officials; .11 = campaign contributions outgoing.
   - **None of FOCAL's 11 financials items reads the "third-party contributions received earmarked for lobbying" observable that Newmark 2017's `disc.contributions_from_others` reads.**
   - **LobbyView is the last remaining check.** If LobbyView's federal LDA schema does NOT include a third-party-contributions-received field (which seems likely — LDA's contribution reporting is OUTGOING under LD-203, not INCOMING), then this row is single-rubric across the entire contributing set.
   - **Compendium 2.0 freeze question:** is `lobbyist_or_principal_report_includes_contributions_received_for_lobbying` a genuine Newmark-distinctive observable that the other 8 rubrics overlook, or is it Newmark over-atomization? Suggestive evidence: Newmark 2017 added this in revision from Newmark 2005 (which doesn't have it); the observable is real (some states do require this, e.g., MA principal reports list dues earmarked for lobbying) but rare. Recommendation: **KEEP** the row in compendium 2.0; flag as "Newmark-2017-distinctive but real" with concrete state examples surfaced during Phase D extraction.

2. **Three FOCAL-distinctive batteries that DON'T fold elsewhere:**
   - **Contact log per-meeting granularity (9 NEW rows).** No other contributing rubric reads per-meeting per-contact disclosure. PRI's coarse `_includes_contacts_made` (E1i/E2i) is the only parent. **Compendium 2.0 freeze decision:** keep all 9 cells; they are real observables (Canada, Chile, Ireland require some/all; US states largely don't). The cells discriminate well across jurisdictions and are extraction-tractable.
   - **Descriptors per-lobbyist registration content (5 NEW rows).** PRI E2b reads lobbyist contact info on the SPENDING report; FOCAL's descriptors.* reads on the REGISTRATION FORM. Different α-form-pair. **Compendium 2.0 freeze decision:** keep both α sides; the reg-form-side cells (FOCAL) and spending-report-side cells (PRI) are valid separate observables.
   - **Openness new cells (5 NEW: ministerial_diaries_available_online, no_user_registration_required, open_license, unique_identifiers, linked_to_other_datasets, changes_flagged_with_versioning).** Mix of universal-portal-features (search, downloadability — existing) and FOCAL-distinctive transparency-quality features. **Compendium 2.0 freeze decision:** keep all; LobbyView's federal API schema-coverage check will validate the unique_identifiers and linked_to_other_datasets cells against the actual LDA API capabilities.

3. **Three row family promotions to compendium 2.0 lock-in confidence:**
   - `lobbyist_spending_report_includes_total_compensation` — **7-rubric-confirmed, most-validated row in compendium.** Lock.
   - Gifts/entertainment/transport/lodging bundle — **5-rubric-confirmed at combined granularity.** Lock. HG Q23 finer gift-granularity remains a compendium 2.0 freeze question (separate gift cell vs bundle); not blocking.
   - Bill/action identifier rows (α form-pair) — **5-rubric-confirmed.** Lock.

4. **The 2025-only "Lobbyist list" indicator** belongs in compendium 2.0 even though it's not in the 2024 `items_FOCAL.tsv`. The principal-side `principal_report_lists_lobbyists_employed` mirror to HG Q9 is documented above. Phase C ground truth uses 2025 numbering from the per-country CSV.

---

## Corrections to predecessor mappings

### Correction 1 — `def_target_*` family expanded to include `def_target_legislative_or_executive_staff`

The CPI mapping introduced `def_target_legislative_branch`, `def_target_executive_agency`, `def_target_governors_office`. FOCAL scope.3 explicitly enumerates "staff" as a separate target type. PROPOSE adding `def_target_legislative_or_executive_staff` (binary; legal) as the 4th cell in the `def_target_*` family. This row is read by FOCAL scope.3's partly-tier (P=staff excluded). The HG / Newmark / Opheim mappings don't read this 4th cell explicitly — but the 3-cell `def_target_*` set they collectively read corresponds to FOCAL's "major branches" (yes/partly = all major branches covered); the staff cell discriminates between FOCAL yes (all-incl-staff) and partly (major-branches-but-not-staff).

### Correction 2 — `lobbyist_disclosure_includes_employment_type` (HG Q10) is now 2-rubric-confirmed (HG + FOCAL)

The HG mapping introduced this row as form-agnostic (cell name pattern `lobbyist_disclosure_*` rather than `lobbyist_reg_form_*` or `lobbyist_spending_report_*`). HG Open Issue HG-4 flagged the form-agnostic vs α-split decision for compendium 2.0 freeze. **FOCAL descriptors.6 reads form-agnostically** — agreeing with HG's reading. The form-agnostic cell is now 2-rubric-confirmed; Open Issue HG-4 resolution leans toward "keep form-agnostic" given 2-rubric agreement.

### Correction 3 — Phase B mapping count

The plan and `STATUS.md` Active Research Lines table both reference "Phase B: 9 rubrics" — after OpenSecrets tabling (2026-05-13) and the OS-Distinctive 3 rows also tabled, the actual Phase B count is **8 rubrics done + 1 (LobbyView) remaining** = 9 mappings total but with OpenSecrets being a structured-tabling rather than a delivered mapping. After FOCAL ships this session, **Phase B is 8 of 9 complete; LobbyView is the final mapping** (a schema-coverage check rather than score-projection — different shape per plan).

---

## Open issues surfaced by FOCAL 2024 (for compendium-2.0 freeze)

1. **FOCAL-1 — `revolving_door.1` scope decision.** Plan defers all revolving_door items; this mapping follows strict plan reading. But `revolving_door.1` (lobbyist's prior public offices disclosed on reg form) is statutorily a disclosure observable. **Decision deferred to user.** If brought in scope, propose row `lobbyist_reg_form_includes_lobbyist_prior_public_offices_held` (binary; legal) with FOCAL projection partly/yes based on completeness.

2. **FOCAL-2 — set-typed cells vs atomized binary cells.** `lobbyist_definition_included_actor_types` (scope.1) and `lobbying_definition_included_activity_types` (scope.4) are proposed as set-typed cells. Granularity bias suggests 9 + 8 = 17 binary cells. **Tradeoff:** set-typed is YAGNI-cleaner for FOCAL's projection but doesn't atomize for downstream rubrics or future granularity. Decision deferred; the set-typed form is FOCAL-projection-sufficient.

3. **FOCAL-3 — openness.1 partly-tier mechanics.** "Optional registration OR separate websites" is a derived condition needing additional cells (`lobbyist_registration_optional_for_some_actor_types`, `lobbyist_registration_split_across_websites_by_actor_type`) to operationalize. Phase C: collapse to binary for projection unless concrete state cases require finer resolution.

4. **FOCAL-4 — openness.4 partly-tier mechanics.** "Some data not captured" needs a `lobbying_data_completeness_score` cell to be operationally read. Phase C: collapse to binary for projection unless completeness concrete-state-grounded.

5. **FOCAL-5 — audit-doc score breakdown ordering ambiguity for Relationships.** The audit doc's "Relationships: 6 + 2 + 0 + 0 + 0 = 8" 5-item summation needs ordering verification against verbatim Suppl Table 5 row order. Suspects: the "6" entry is the 2025-only `lobbyist_list` indicator (weight 3 × yes 2 = 6); positional ordering in the audit doc may differ from `relationships.1-4` enumeration. **Phase C: verify against per-country CSV directly (which uses indicator_id keys).**

6. **FOCAL-6 — relationships.4 partly-tier cell.** FOCAL's "limited to Y/N and no information about nature of relationship" partly-tier needs a `business_association_disclosure_detail_level` cell to operationalize. HG Q22's binary suffices for HG's projection but not for FOCAL's 3-tier read. Phase C may need a typed cell with enum {binary_yn, detailed}.

7. **FOCAL-7 — 2025 application differences encoded in projection logic, not source TSV.** The 2024 → 2025 application differences (timeliness.1+.2 merged, "Lobbyist list" added) are encoded in the projection logic via the per-country CSV's 2025 numbering. Phase C tooling must support this 2024-source-with-2025-application asymmetry. Alternative: re-extract `items_FOCAL.tsv` with 2025 numbering (50 items: 49 merged + 1 added). Decision deferred; current approach (2024 numbering with 2025 projection logic) is straightforward.

8. **FOCAL-8 — Ministerial diary rows are US-N/A but useful for compendium completeness.** `ministerial_diary_disclosure_cadence` + `ministerial_diaries_available_online` are population-zero observables for US jurisdictions. Phase C extracts them as `no_diary_published`. Compendium 2.0 freeze decision: keep the rows for cross-jurisdictional comparison value (28 countries vs 50 US states) even though US extraction is uniform-zero.

9. **FOCAL-9 — financials.5 (time spent on lobbying) is REPORTING-side, distinct from scope.2 (time threshold DEFINITIONAL).** Two cells, same row name `time_*` but different observables. Phase C must distinguish; `time_threshold_for_lobbyist_registration` (legal; definitional trigger) ≠ `lobbyist_or_principal_report_includes_time_spent_on_lobbying` (legal; reporting content).

10. **FOCAL-10 — Federal LDA scoring quirks deserve cross-checking against Phase A4 audit conclusions.** Several FOCAL items where US LDA scored UNEXPECTEDLY 0 (e.g., scope.3 = 0 despite broad target coverage; relationships.2 = 2 despite trade-association coverage being narrow) warrant re-examination against the audit doc's verbatim Suppl Table 5 values. Phase C: validate projection against per-country CSV verbatim, not audit-doc summary.

11. **FOCAL-11 — α form-type split candidates from FOCAL descriptors / relationships.** Descriptors.* read reg-form-side; PRI E2b reads spending-report-side `lobbyist_report_includes_lobbyist_contact_info`. Compendium 2.0 freeze: explicitly add the spending-report-side parallels for the 5 NEW reg-form-side rows (descriptors.1-5 → `lobbyist_spending_report_includes_lobbyist_*`)? Or accept that the FOCAL-distinctive reg-form-side cells stand alone? Decision deferred. PRI's `lobbyist_report_includes_lobbyist_contact_info` is one already-existing α pair; the others may follow.

---

## What FOCAL doesn't ask that other rubrics will

For continuity with other rubric mappings: FOCAL does not read any registration form content beyond actor types, activity types, and the 6 descriptors observables (Sunlight #1 reg-form territory beyond subject-matter is broader than FOCAL); any registration deadline (HG Q4, CPI #200); any registration cadence (HG Q6, CPI #199); any reporting cadence enum or filing-frequency-per-cycle (HG Q12, CPI #202, PRI E1h/E2h); any prohibition observable (Newmark 2017/2005 `prohib.*`); any itemization-de-minimis threshold (Sunlight #3, HG Q15); any filing-de-minimis threshold (PRI D1); any null/no-activity report (HG Q25); any photograph requirement (HG Q8); any registration-amendment deadline (HG Q7); any actor-class definitional inclusion at the individual level (Newmark `def.elective_officials` / `def.public_employees`; FOCAL's scope.1 covers organizational types not individual roles); any audit / enforcement cells (CPI #207-209, HG Q39-Q47); any third-party-contributions-received-for-lobbying observable (Newmark-2017-distinctive); any aggregate-lobbying-spending publication (HG Q35-Q37).

FOCAL's role within the contributing-rubric set is **per-meeting contact-log atomization + portal-quality cells + cross-jurisdictional (28-country) calibration anchor for the US federal LDA jurisdiction.** Together with HG's portal-access ordinals and PRI's actor-and-target taxonomy, FOCAL completes the disclosure-side compendium row backbone with the contact-log per-meeting granularity that completes the spectrum from "coarse aggregate-period subject" (PRI/Sunlight/HG) to "per-meeting per-contact granularity" (FOCAL).

After FOCAL, **LobbyView (federal LDA schema-coverage check) is the last remaining Phase B mapping** — different shape (schema-coverage instead of score-projection), shorter, and likely confirms 90%+ of LobbyView's 46 schema fields against the now-rich 110+ compendium row set. After Phase B closes, the compendium 2.0 row freeze brainstorm starts.
