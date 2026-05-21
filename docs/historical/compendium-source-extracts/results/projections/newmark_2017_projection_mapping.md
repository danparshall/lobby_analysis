# Newmark 2017 — projection mapping

**Plan:** [`../../plans/20260507_atomic_items_and_projections.md`](../../plans/20260507_atomic_items_and_projections.md) Phase B (fourth rubric to ship, after CPI 2015 C11, PRI 2010, and Sunlight 2015; OpenSecrets 2022 was tabled 2026-05-13).
**Handoff (most recent):** [`../../plans/_handoffs/20260511_phase_b_continued_remaining_7.md`](../../plans/_handoffs/20260511_phase_b_continued_remaining_7.md). Watchpoints for Newmark 2017 are in the per-rubric section there.
**Prior handoff:** [`../../plans/_handoffs/20260507_phase_b_handoff.md`](../../plans/_handoffs/20260507_phase_b_handoff.md).
**Atomic items source:** [`../items_Newmark2017.tsv`](../items_Newmark2017.tsv) (23 rows total: 19 atomic items + 3 sub-aggregate composites + 1 index composite; **the 5 `prohib.*` items are OUT of scope** per the disclosure-only Phase B qualifier).
**Predecessor mappings (for conventions):** [`cpi_2015_c11_projection_mapping.md`](cpi_2015_c11_projection_mapping.md), [`pri_2010_projection_mapping.md`](pri_2010_projection_mapping.md), [`sunlight_2015_projection_mapping.md`](sunlight_2015_projection_mapping.md).

---

## Doc conventions

All five conventions from the CPI/PRI/Sunlight mapping docs apply verbatim:

- Compendium row IDs are working names, not cluster-derived.
- Typed cells live on `MatrixCell.value` (v2.0 schema bump assumed).
- Granularity bias: split on every distinguishing case.
- Axis is `legal_availability` for de jure observables; Newmark 2017 reads no de facto observables (no `practical_availability` rows).
- **"Collect once, map to many."** Each row entry carries a `[cross-rubric: …]` annotation listing every other rubric that reads the same observable. This is the seed for compendium-2.0 dedup.

**Newmark 2017 is a shallow but heavily redundant rubric.** Nearly every row Newmark touches is already in another rubric's mapping. Newmark's contribution to compendium 2.0 is cross-rubric validation depth, not novel observables — same role Sunlight plays. The only Newmark-distinctive observable surfaced this session is `lobbyist_or_principal_report_includes_contributions_received_for_lobbying` (Newmark `disclosure.contributions_from_others`; not directly read by any other rubric in our contributing set).

## Scope qualifier — 5 `prohib.*` items OUT

Per the plan's disclosure-only Phase B qualifier, the 5 `prohib.*` atomic items are **excluded from this projection** without further analysis:

| Excluded item | Why excluded |
|---|---|
| `prohib.contributions_anytime` | Prohibition (no campaign contributions). Restriction, not disclosure. |
| `prohib.contributions_during_session` | Prohibition (session-time campaign contributions). |
| `prohib.solicitation_by_officials` | Prohibition (officials soliciting gifts/contributions). |
| `prohib.contingent_compensation` | Prohibition (contingent-fee lobbying). |
| `prohib.revolving_door` | Cooling-off period — restriction on post-office employment. |

These items measure what state regimes **prohibit**, not what they **require be disclosed**. They re-enter scope in a later round (per `STATUS.md` Current Focus: "Once disclosure-side prototype is solid, expand to prohibitions / enforcement / personnel / itemization-granularity"). Five `prohib.*` items × 50 states = 250 ground-truth cells parked for later, not lost.

**Implication:** With `prohib.*` excluded, this projection **cannot reproduce `index.total`** (Newmark's headline 0–19 measure, published per state in Table 2). It CAN reproduce `def.section_total` (0–7) and `disclosure.section_total` (0–7), which are 100 per-state sub-aggregate ground-truth cells for Phase C validation.

## Aggregation rule

Newmark's published structure (paper lines 539–558 + Table 2):

- `index.total = def.section_total + prohib.section_total + disclosure.section_total` (0–19; sub-aggregate sum)
- Each section_total is the unweighted sum of its 1/0 atomic items
- Each atomic item: 1 if the state's statute includes the provision, 0 if not (per the verbatim `scoring_rule` columns in `items_Newmark2017.tsv`)

Phase C `project_newmark_2017_disclosure_side(state, 2015)` produces:

```
def.section_total_partial    = sum of 7 def.* atomic projections  ∈ [0, 7]
disclosure.section_total     = sum of 7 disclosure.* atomic projections  ∈ [0, 7]
```

The `prohib.*` portion of `index.total` is not produced (`prohib.section_total` is undefined for this projection). **Phase C validation:** 50 states × 2 sub-aggregate ground-truth cells (`def.section_total` and `disclosure.section_total`) for tolerance check.

## Per-state per-indicator data

**Newmark 2017 does NOT publish per-state per-atomic-item data.** Table 2 publishes per-state sub-aggregate totals (`def.section_total`, `prohib.section_total`, `disclosure.section_total`, `index.total`) for 2015. The underlying per-state per-item data is Book of States-derived (BoS 2015/2016 vintage, looked up by Newmark from state statutes via the BoS abstraction). The BoS source isn't in this project's archive.

**Practical consequence for Phase C:** Per-atomic-item validation against Newmark's published data is impossible — Newmark only publishes sub-aggregates. Per-atomic-item validation has to come from cross-rubric overlap with rubrics that DO publish per-item per-state data (PRI 2010, CPI 2015 C11 — and the BoS-derived items are correct-by-construction when fed by those rubrics' published cells, since both Newmark 2017 and Newmark 2005 use BoS as the upstream source).

**Distribution context (from paper Table 2 / abstract):**

| Sub-aggregate | Range across 50 states | Mean |
|---|---|---|
| `def.section_total` (max 7) | 1 – 7 | (paper notes range; mean not given for sub-aggregate alone) |
| `prohib.section_total` (max 5) | 0 – 5 | (excluded from this projection) |
| `disclosure.section_total` (max 7) | 2 – 7 | 15 states score the max of 7 |
| `index.total` (max 19) | 7 – 19 | 12.96 (SD 2.63); Cronbach's α = 0.67 |

**Items with no variation across 50 states** (per Newmark's Table 3 factor-analysis footnote):
- `def.legislative_lobbying` — all 50 states require registration for lobbying the legislature. Cell value is uniformly TRUE.
- `disclosure.expenditures_benefiting_officials` — "no variation" per Table 3 footnote (excluded from factor analysis). Direction not stated; likely uniformly TRUE (universal disclosure requirement in 2015).

For Phase C: these two items don't actually discriminate across states, but the cells they read are still extracted (the cells carry observable values; the lack of variation is a 2015-vintage empirical fact, not a definition).

## Validation jurisdictions

50 US states × 2015 vintage × **2 sub-aggregates** = **100 per-cell sub-aggregate ground-truth values** for Phase C. Per-item validation impossible directly against Newmark; available via cross-rubric overlap.

Federal LDA out of scope (Newmark is state-only). Newmark 2005 is the explicit predecessor (18 items vs 17 with prohib excluded ≈ subset of 2017) and will produce a parallel ground-truth set for the 2003 vintage when mapped next.

---

## Per-item mappings

### Definitions battery (7 items, all in scope)

Newmark's "Definitions of lobbyists and registration requirements" sub-aggregate. Decomposes into:
- 2 **activity-type** observables (legislative / administrative-agency lobbying triggers registration): `def_target_*` rows on the existing CPI-mapping target-type family.
- 2 **actor-class** observables (elected officials / public employees as lobbyists): NEW `def_actor_class_*` rows.
- 3 **lobbyist-status threshold** observables (compensation / expenditure / time standards): typed cells with `IS NOT NULL` projection.

#### newmark_2017.def.legislative_lobbying — Legislative lobbying necessitates registering as a lobbyist

- **Compendium rows:** `def_target_legislative_branch` (binary; legal)
  [cross-rubric: CPI #196 (one of three target-type reads in IND_196's compound); HG Q1 (inverse-framed — Q1 asks if executive lobbying is ALSO recognized, presupposing legislative is universal); FOCAL `scope.3` (legislative branches as targets); Newmark 2005 `def_legislative_lobbying` (verbatim predecessor); Opheim `def.legislative_lobbying`; PRI A7 actor-side (`actor_legislative_branch_registration_required`, parallel-but-not-identical observable)]
  Already in CPI mapping; pre-existing.
- **Cell type:** binary.
- **Axis:** `legal_availability`.
- **Scoring rule:** `cell == TRUE → 1; else → 0`.
- **Source quote:** "Definitions include whether the following necessitate registering as a lobbyist: legislative lobbying, administrative agency lobbying" (Newmark 2017 paper line 515–516).
- **Note on no-variation:** Newmark notes "All 50 states require registration for lobbying the legislature" (paper line 518). Newmark excludes this item from factor analysis (Table 3 footnote). The cell should still be extracted (state-by-state) — the empirical no-variation in 2015 doesn't make the observable any less load-bearing for compendium 2.0.
- **Note on PRI A7 vs CPI #196:** PRI A is **actor-side** ("legislative branch is required to register") whereas CPI #196 / Newmark `def.legislative_lobbying` is **target-side** ("lobbying targets include legislative branch"). Per the PRI mapping convention, two row families exist (`actor_*` vs `def_target_*`). Newmark `def.legislative_lobbying` is target-side per its source quote ("legislative lobbying" = the activity of lobbying *of* the legislature triggers registration). Reads the target-side row.

#### newmark_2017.def.administrative_agency_lobbying — Administrative-agency lobbying necessitates registering

- **Compendium rows:** `def_target_executive_agency` (binary; legal)
  [cross-rubric: CPI #196 (compound second arm — "executive officials"); HG Q1 ("does the deﬁnition recognize executive branch lobbyists?"); FOCAL `scope.3` (executive branch officials, administrative branch/bureaucracy); Newmark 2005 `def_administrative_agency_lobbying`; PRI A (actor-side, parallel)]
  Already in CPI mapping; pre-existing.
- **Cell type:** binary.
- **Axis:** `legal_availability`.
- **Scoring rule:** `cell == TRUE → 1; else → 0`.
- **Source quote:** "administrative agency lobbying, elective officials as lobbyists" (Newmark 2017 paper line 516–517).
- **Note on row choice:** CPI's #196 source quote requires *executive officials including the governor*; the target-type split is `def_target_governors_office AND def_target_executive_agency`. Newmark's `def.administrative_agency_lobbying` reads only the administrative-agency arm — not the governor's-office arm. Single-row projection on `def_target_executive_agency` is the conservative reading. Newmark provides no specific definition of "administrative agency" beyond the BoS source; the cell stays at the executive-agency-coverage granularity.

#### newmark_2017.def.elective_officials_as_lobbyists — Elected officials are defined as lobbyists if engaged in lobbying-related behaviors

- **Compendium rows:** `def_actor_class_elected_officials` (binary; legal) **NEW**
  [cross-rubric: Newmark 2005 `def_elected_officials_as_lobbyists`; Opheim `def.elective_officials`; potential FOCAL relationships.4 partial reading (which captures business associations *of* officials, not officials-as-lobbyists, so loose at best); PRI A actor-side may have a parallel actor-class concept — unverified in current mapping]
- **Cell type:** binary.
- **Axis:** `legal_availability`.
- **Scoring rule:** `cell == TRUE → 1; else → 0`.
- **Source quote:** "Some states require elected officials and public appointees to register if they engage in certain lobbying-related behaviors." (Newmark 2017 paper line 519–521).
- **Note on row design — actor-class vs actor-side:** The `actor_*` row family from the PRI mapping captures "the state requires registration *when X is the entity lobbying*" — e.g., `actor_legislative_branch_registration_required` covers the case where the legislative branch itself is lobbying another branch. That's a structural-actor classification. `def_actor_class_elected_officials` is a different observable: "do *individual* elected officials, when engaged in lobbying behaviors as individuals, fall under the lobbyist definition." Newmark and Opheim treat this as a definitional inclusion criterion (does the lobbyist definition include elected officials when they themselves lobby). I'm proposing a **separate row family `def_actor_class_*`** to capture this. Could alternatively be merged into `actor_*` rows; flagged as Open Issue 1.

#### newmark_2017.def.public_employees_as_lobbyists — Public employees are defined as lobbyists if engaged in lobbying-related behaviors

- **Compendium rows:** `def_actor_class_public_employees` (binary; legal) **NEW**
  [cross-rubric: Newmark 2005 `def_public_employees_as_lobbyists`; Opheim `def.public_employees`; PRI A actor-side may have a parallel concept]
- **Cell type:** binary.
- **Axis:** `legal_availability`.
- **Scoring rule:** `cell == TRUE → 1; else → 0`.
- **Source quote:** "public employees as lobbyists, and whether there are compensation, expenditure, and time standards" (Newmark 2017 paper line 517–518).
- **Note:** Parallel to elected-officials; same row-design Open Issue 1 applies.

#### newmark_2017.def.compensation_standard — Compensation standard for lobbyist status

- **Compendium rows:** `compensation_threshold_for_lobbyist_registration` (typed `Optional[Decimal]`; legal)
  [cross-rubric: CPI #197 (reads the dollar value at 3-tier — present/some-threshold/none); HG Q2 (reads as 5-tier ordinal); FOCAL `scope.2` (combined with filing-de-minimis per handoff threshold table); Newmark 2005 `def_compensation_standard` (binary; reads same cell `IS NOT NULL`); Opheim `def.compensation_standard` (binary; reads same cell `IS NOT NULL`)]
  Already in CPI mapping; pre-existing typed cell.
- **Cell type:** `Optional[Decimal]` representing the compensation dollar threshold above which the lobbyist-definition triggers.
- **Axis:** `legal_availability`.
- **Scoring rule:** `cell IS NOT NULL → 1; else → 0`. (Newmark reads only the presence of a standard, not the value. CPI #197 reads the value to discriminate `==0` (anyone paid) vs `>0` (some threshold).)
- **Source quote:** "persons are defined as lobbyists if they receive a certain amount of money in exchange for lobbying (compensation standards)" (Newmark 2017 paper line 521–523).
- **Note on threshold-concept distinction:** This is the **lobbyist-status threshold** (one of three threshold concepts in compendium 2.0 — see CRITICAL distinction in the Sunlight mapping doc). Not to be confused with the filing-de-minimis (PRI D1) or itemization-de-minimis (Sunlight #3 / HG Q15) thresholds.

#### newmark_2017.def.expenditure_standard — Expenditure standard for lobbyist status

- **Compendium rows:** `expenditure_threshold_for_lobbyist_registration` (typed `Optional[Decimal]`; legal) **NEW**
  [cross-rubric: Newmark 2005 `def_expenditure_standard`; Opheim `def.expenditure_standard`; potential FOCAL `scope.2` partial read (FOCAL bundles all three thresholds at finer granularity)]
- **Cell type:** `Optional[Decimal]` representing the expenditure dollar threshold above which the lobbyist-definition triggers. Distinct cell from the compensation-threshold row above — a state could define lobbyists by compensation OR expenditure OR both OR neither.
- **Axis:** `legal_availability`.
- **Scoring rule:** `cell IS NOT NULL → 1; else → 0`.
- **Source quote:** "if they spend a certain amount of money in lobbying (expenditure standards)" (Newmark 2017 paper line 523–524).
- **Note:** The 2026-05-11 handoff says these three def.*_standard items "Should read the existing CPI #197 cell ... as `cell IS NOT NULL`. Don't propose new binary rows." Charitable reading: the watchpoint is shorthand for "follow the CPI #197 typed-cell pattern" — i.e., propose a typed cell with `IS NOT NULL` projection, not a separate binary row. The three Newmark standards are conceptually distinct (compensation ≠ expenditure ≠ time as definitional axes); they cannot all read the same cell because a state could have a compensation standard without an expenditure standard. Three typed cells, each read by the corresponding Newmark binary via `IS NOT NULL`. If the handoff intended literal "all three read CPI #197," that reading is internally inconsistent and I'm proposing this correction explicitly.

#### newmark_2017.def.time_standard — Time standard for lobbyist status

- **Compendium rows:** `time_threshold_for_lobbyist_registration` (typed `Optional[<TimeThreshold>]`; legal) **NEW**
  [cross-rubric: Newmark 2005 `def_time_standard`; Opheim `def.time_standard`; potential FOCAL `scope.2` partial read; Federal LDA uses a 20%-of-work-time threshold which would populate this cell for the Federal_US jurisdiction]
- **Cell type:** `Optional[<TimeThreshold>]` where `TimeThreshold = {magnitude: Decimal, unit: enum{hours_per_quarter, hours_per_year, days_per_year, percent_of_work_time, ...}}`. Three real-world variants commonly observed: hours-per-time-period, days-per-period, percent-of-work-time. The structured-value type accommodates all three.
- **Axis:** `legal_availability`.
- **Scoring rule:** `cell IS NOT NULL → 1; else → 0`. Newmark reads only presence/absence; the magnitude and unit are extracted for downstream consumers and finer-grained rubrics (none in current contributing set, but a future LDA-specific rubric might read the 20% threshold).
- **Source quote:** "if they devote a certain amount of time in their lobbying efforts (time standards). Each of these is coded 1 if the state includes the provision in its definition of a lobbyist and 0 otherwise." (Newmark 2017 paper line 524–526).
- **Note:** The structured cell type is finer than `Optional[Decimal]` because time thresholds are unit-bearing (the federal LDA's "20% of work time" doesn't reduce to a dollar amount). Alternative: a free-text `Optional[str]` cell with parsed structured features. Decision deferred to compendium 2.0 freeze.

### Disclosure battery (7 items, all in scope)

Newmark's "Registration and reporting/disclosure requirements" sub-aggregate. Decomposes into:
- 1 **subject-matter** observable: maps to existing Sunlight/HG/PRI subject-matter row.
- 1 **expenditures-benefiting-officials** observable: maps to existing PRI gifts/entertainment row, projected as OR over actors.
- 2 **compensation** observables: map to existing Sunlight compensation rows.
- 2 **expenditure summary** observables: 1 reuses Sunlight categories row; 1 is NEW (totals).
- 1 **contributions-received** observable: NEW; Newmark-distinctive within the current contributing set.

#### newmark_2017.disclosure.influence_legislation_or_admin — Disclosure: seeking to influence legislation or admin action

- **Compendium rows:** `lobbyist_spending_report_includes_general_subject_matter` (binary; legal)
  [cross-rubric: Sunlight #1 (one of 6 rows, the spending-report-side general-subject-matter row); HG Q20 subject-tier (read on spending reports); Newmark 2005 `disc_legislative_admin_action_to_influence`; PRI E2g_i (lobbyist-side subject disclosure); Opheim `disclosure.legislation_supported_or_opposed` (loose reading, via β AND-projection); FOCAL `contact_log.11` (broad reading on subject coverage)]
  Already in Sunlight mapping; pre-existing.
- **Cell type:** binary.
- **Axis:** `legal_availability`.
- **Scoring rule:** `cell == TRUE → 1; else → 0`.
- **Source quote:** "seeking to influence legislation or administrative action" (Newmark 2017 paper line 540–541).
- **Note on form-type split (α convention):** Sunlight mapping introduced 6 rows from 3 disclosure-detail levels × 2 form types (reg form / spending report). Newmark's `disclosure.influence_legislation_or_admin` is on the disclosure-report side per the source quote "seeking to influence" being a *required disclosure*. Reads only the spending-report-side row. (If a state requires the subject on the reg form but not the spending report, Newmark would code 0 for this item — Newmark's "disclosure" frame is explicit about post-registration spending disclosure. Verifiable cross-state if needed via BoS; treat as a Phase C edge case rather than a Phase B row-design decision.)

#### newmark_2017.disclosure.expenditures_benefiting_officials — Disclosure: expenditures benefiting public officials or employees

- **Compendium rows:** `lobbyist_report_includes_gifts_entertainment_transport_lodging` (binary; legal) AND/OR `principal_report_includes_gifts_entertainment_transport_lodging` (binary; legal)
  [cross-rubric: PRI E1f_iii (principal-side; loose-c_030); PRI E2f_iii (lobbyist-side; loose-c_030); Newmark 2005 `disc_expenditures_benefiting_officials`; Opheim `disclosure.expenditures_benefitting_public_employees` ("including gifts"); FOCAL `financials.10` ("Expenditures benefitting public officials or employees including financial/non-financial gifts and support, employer/principal on whose behalf expenses were made" — verbatim parallel); HG Q14 (categorized totals "i.e., gifts, entertainment, postage" — partial); HG Q17 (recipient of itemized expenditure — partial); HG Q23 (gifts statutory provision, 4-tier ordinal including prohibition tier — partial, prohibition portion is out-of-scope)]
  Already in PRI mapping; pre-existing pair of rows.
- **Cell type:** binary per row.
- **Axis:** `legal_availability`.
- **Scoring rule:** `(lobbyist_report_includes_gifts_entertainment_transport_lodging OR principal_report_includes_gifts_entertainment_transport_lodging) → 1; else → 0`. Newmark's framing is actor-agnostic ("expenditures benefitting officials" — somewhere in the disclosure regime); OR over the two actor-side rows is the coarsest correct reading.
- **Source quote:** "expenditures benefitting public officials or employees" (Newmark 2017 paper line 541–542). Note the source's "benefitting" (double t) spelling; preserved verbatim.
- **Note on no-variation:** Newmark Table 3 footnote (paper line 1162–1163): "Excluded from factor analysis ... no variation in this category" — Newmark observed no cross-state variation on this item in 2015. Likely cell value uniformly TRUE for the 2015 vintage (universal disclosure requirement for gift-like benefits). Phase C: project this item as TRUE for all states; verify against Newmark's sub-aggregate published values (every state should add 1 here to its disclosure sub-aggregate). If a state's `disclosure.section_total` is 6 and the other 6 disclosure items sum to 5, this item must be the missing 1.
- **Note on row design (handoff watchpoint):** The handoff flagged: "Important row for the FOCAL/Newmark cross-rubric stack. Check whether this should be one row or split by what counts as a benefit (gift, meal, etc.)." Resolution: keep the existing PRI bundled rows (gifts ∪ entertainment ∪ transport ∪ lodging × principal/lobbyist) — most rubrics (Newmark, FOCAL, Opheim) read the bundle at coarse granularity. **HG Q23 specifically reads gifts at finer granularity** (gift-prohibition tier), but Q23's finer granularity is a 4-tier ordinal that mixes disclosure and prohibition tiers; for disclosure-only scope, Q23 reads `gifts_reported` ∈ {required, not required} — same observable as the existing bundle. Splitting `gifts` out as its own row would only matter if a state required reporting of gifts but NOT entertainment/transport/lodging — empirically unusual. Recommendation: keep bundle; revisit at compendium 2.0 freeze if HG mapping or extraction pipeline surfaces a state where the granularity-bias argument actually changes a projection score.

#### newmark_2017.disclosure.compensation_by_employer — Disclosure: compensation broken down by employer

- **Compendium rows:** `lobbyist_spending_report_includes_compensation_broken_down_by_client` (binary; legal)
  [cross-rubric: Sunlight #5 (the broken-down-by-client row); Newmark 2005 `disc_compensation_by_employer` (verbatim predecessor); HG Q13 footnote ("Full points if information is on registration form instead") at coarser granularity; CPI #201 (compound — compensation-included is one of three reads)]
  Already in Sunlight mapping; pre-existing.
- **Cell type:** binary.
- **Axis:** `legal_availability`.
- **Scoring rule:** `cell == TRUE → 1; else → 0`.
- **Source quote:** "compensation received (broken down by employer)" (Newmark 2017 paper line 542–543).
- **Note on "employer" vs "client":** Newmark uses "employer"; Sunlight uses "client". Same observable: which *paying entity* the lobbyist's compensation is itemized against. The cell name uses "client" (Sunlight convention) for consistency with the existing row; could be renamed to "employer_or_client" if compendium 2.0 prefers neutral phrasing — flagged as Open Issue 2.

#### newmark_2017.disclosure.total_compensation — Disclosure: total compensation received

- **Compendium rows:** `lobbyist_spending_report_includes_total_compensation` (binary; legal)
  [cross-rubric: Sunlight #5 (total-compensation-on-spending-report row); Newmark 2005 `disc_total_compensation`; HG Q13 (binary lobbyist-side compensation on spending report — same observable); HG Q27 (mirror on principal/employer side — distinct cell, parallel); CPI #201 (compound); PRI E2f_i ("Direct lobbying costs (compensation)")]
  Already in Sunlight mapping; pre-existing.
- **Cell type:** binary.
- **Axis:** `legal_availability`.
- **Scoring rule:** `cell == TRUE → 1; else → 0`.
- **Source quote:** "total compensations received" (Newmark 2017 paper line 543).
- **Note on plural typo:** Newmark's source uses plural "compensations" — same concept as singular "total compensation" used in Table 3. Preserved verbatim above.

#### newmark_2017.disclosure.categories_of_expenditures — Disclosure: categories of expenditures

- **Compendium rows:** `lobbyist_spending_report_categorizes_expenses_by_type` (binary; legal)
  [cross-rubric: Sunlight #2 categorized-tier (item-2 tier 1 reads this row); Newmark 2005 `disc_categories_of_expenditures`; HG Q14 ("summaries (totals) of spending classified by category types — gifts, entertainment, postage"); Opheim `disclosure.spending_by_category`; FOCAL `financials.*` battery (FOCAL atomizes the categories themselves rather than asking the binary "are categories required" — but the underlying observable for the binary is the same)]
  Already in Sunlight mapping; pre-existing.
- **Cell type:** binary.
- **Axis:** `legal_availability`.
- **Scoring rule:** `cell == TRUE → 1; else → 0`.
- **Source quote:** "categories of expenditures" (Newmark 2017 paper line 543).

#### newmark_2017.disclosure.total_expenditures — Disclosure: total expenditures toward lobbying

- **Compendium rows:** `lobbyist_spending_report_includes_total_expenditures` (binary; legal) **NEW**
  [cross-rubric: Newmark 2005 `disc_total_expenditures`; Opheim `disclosure.total_spending` ("lobbyist's total spending"); HG Q11 (gateway: spending report required — implies total reported); HG Q36 (state agency provides overall lobbying spending total — different observable, public-access side); CPI #201 (compound — total spending implicit in "detailed spending reports"); Sunlight #2 tier 0+ (implicit: "lobbyists report lump total of expenditures")]
- **Cell type:** binary.
- **Axis:** `legal_availability`.
- **Scoring rule:** `cell == TRUE → 1; else → 0`.
- **Source quote:** "total expenditures toward lobbying" (Newmark 2017 paper line 543–544).
- **Note on row design — separate from `lobbyist_spending_report_required`:** Granularity-bias says split. The existence of a spending report (`lobbyist_spending_report_required`) is logically distinct from whether the report includes a total expenditures line item. Empirically the two almost always co-occur — if a state requires a spending report, it requires a total. But a state could require itemized expenditures only (no aggregate total) or categorized expenditures only. The cell is separate; in practice it will be TRUE whenever `lobbyist_spending_report_required` is TRUE. Cross-rubric readers (Newmark 2017, Newmark 2005, Opheim) treat "total expenditures" as a distinct disclosure observable.

#### newmark_2017.disclosure.contributions_from_others — Disclosure: contributions received from others for lobbying purposes

- **Compendium rows:** `lobbyist_or_principal_report_includes_contributions_received_for_lobbying` (binary; legal) **NEW**
  [cross-rubric: Newmark 2005 *contributions* parallel item (likely; not directly verified in cross-rubric grep but predecessor structure suggests parallel inclusion in the 2005 disclosure-of-6 battery); HG, CPI, PRI, FOCAL, Opheim, Sunlight, OpenSecrets, LobbyView — **no direct match in any other contributing rubric**]
- **Cell type:** binary.
- **Axis:** `legal_availability`.
- **Scoring rule:** `cell == TRUE → 1; else → 0`.
- **Source quote:** "contributions received from others for lobbying purposes" (Newmark 2017 paper line 547).
- **Note — Newmark-distinctive observable:** This is the only Newmark 2017 disclosure item that doesn't already have a row from another rubric mapping. The observable: does the state require a lobbyist (or their principal/employer) to disclose any **third-party contributions** received for lobbying purposes? E.g., a non-profit principal might receive earmarked donations from members for the purpose of funding lobbying activities; some states require these to be disclosed. Distinct from `lobbyist_spending_report_includes_total_compensation` (which is what the lobbyist is *paid by* the principal) and from `lobbyist_spending_report_includes_compensation_broken_down_by_client` (which is per-client allocation of the lobbyist's pay). This row is about funds flowing TO the lobbyist/principal FROM third parties EARMARKED for lobbying. **Real-world example:** a trade-association lobbyist whose dues income includes earmarked lobbying-fund contributions from member companies — some states require those member contributions to be itemized in the principal's spending report.
- **Note on actor split:** The row is currently framed as `lobbyist_or_principal_*` because Newmark's source quote doesn't specify actor side. Could be split into `lobbyist_report_includes_contributions_received_for_lobbying` + `principal_report_includes_contributions_received_for_lobbying` per the granularity-bias convention (consistent with the principal-vs-lobbyist split throughout PRI mapping). Flagging as Open Issue 3 — defer to compendium 2.0 freeze; the projection logic is identical (OR over the two actor-side rows if split).

---

## Summary of compendium rows touched

| Row id (working name) | Cell type | Axis | Newmark 2017 items reading | Cross-rubric readers (dedupe candidates) | Status |
|---|---|---|---|---|---|
| `def_target_legislative_branch` | binary | legal | `def.legislative_lobbying` | CPI #196, HG Q1, FOCAL scope.3, Newmark 2005, Opheim, PRI A7 (actor-side parallel) | existing (CPI mapping) |
| `def_target_executive_agency` | binary | legal | `def.administrative_agency_lobbying` | CPI #196, HG Q1, FOCAL scope.3, Newmark 2005 | existing (CPI mapping) |
| `def_actor_class_elected_officials` | binary | legal | `def.elective_officials_as_lobbyists` | Newmark 2005, Opheim | **NEW** |
| `def_actor_class_public_employees` | binary | legal | `def.public_employees_as_lobbyists` | Newmark 2005, Opheim | **NEW** |
| `compensation_threshold_for_lobbyist_registration` | typed `Optional[Decimal]` | legal | `def.compensation_standard` (via `IS NOT NULL`) | CPI #197, HG Q2, FOCAL scope.2, Newmark 2005, Opheim | existing (CPI mapping) |
| `expenditure_threshold_for_lobbyist_registration` | typed `Optional[Decimal]` | legal | `def.expenditure_standard` (via `IS NOT NULL`) | Newmark 2005, Opheim, FOCAL scope.2 (partial) | **NEW** |
| `time_threshold_for_lobbyist_registration` | typed `Optional[<TimeThreshold>]` | legal | `def.time_standard` (via `IS NOT NULL`) | Newmark 2005, Opheim, FOCAL scope.2 (partial), Federal LDA 20% rule | **NEW** |
| `lobbyist_spending_report_includes_general_subject_matter` | binary | legal | `disclosure.influence_legislation_or_admin` | Sunlight #1, HG Q20, Newmark 2005, PRI E2g_i, Opheim (β AND-projection), FOCAL contact_log.11 | existing (Sunlight mapping) |
| `lobbyist_report_includes_gifts_entertainment_transport_lodging` | binary | legal | `disclosure.expenditures_benefiting_officials` (via OR with principal-side) | PRI E2f_iii, FOCAL financials.10, Newmark 2005, Opheim | existing (PRI mapping) |
| `principal_report_includes_gifts_entertainment_transport_lodging` | binary | legal | `disclosure.expenditures_benefiting_officials` (via OR with lobbyist-side) | PRI E1f_iii, FOCAL financials.10 (combined), Newmark 2005, Opheim | existing (PRI mapping) |
| `lobbyist_spending_report_includes_compensation_broken_down_by_client` | binary | legal | `disclosure.compensation_by_employer` | Sunlight #5, Newmark 2005, HG Q13 footnote, CPI #201 | existing (Sunlight mapping) |
| `lobbyist_spending_report_includes_total_compensation` | binary | legal | `disclosure.total_compensation` | Sunlight #5, Newmark 2005, HG Q13, CPI #201, PRI E2f_i | existing (Sunlight mapping) |
| `lobbyist_spending_report_categorizes_expenses_by_type` | binary | legal | `disclosure.categories_of_expenditures` | Sunlight #2, HG Q14, Newmark 2005, Opheim, FOCAL financials.* | existing (Sunlight mapping) |
| `lobbyist_spending_report_includes_total_expenditures` | binary | legal | `disclosure.total_expenditures` | Newmark 2005, Opheim, HG Q11 (gateway), CPI #201 (compound) | **NEW** |
| `lobbyist_or_principal_report_includes_contributions_received_for_lobbying` | binary | legal | `disclosure.contributions_from_others` | Newmark 2005 (likely parallel; unverified) — Newmark-distinctive in current set | **NEW** |

**14 distinct compendium rows touched by 14 Newmark 2017 atomic items in scope.** **8 of 14 are pre-existing** (reused from CPI / PRI / Sunlight mappings); **6 of 14 are NEW** (proposed in this mapping). Of the 6 new, 5 are reasonably anticipated by the predecessor handoff (`def_actor_class_*` × 2, `expenditure_threshold_*`, `time_threshold_*`, `lobbyist_spending_report_includes_total_expenditures`); 1 is a Newmark-distinctive observable (`lobbyist_or_principal_report_includes_contributions_received_for_lobbying`).

Each new row's reuse expectation: every new row is also read by Newmark 2005's parallel item (Newmark 2005 will be the next mapping). After Newmark 2005 mapping, expect at most 1 row remains single-rubric (`contributions_received_for_lobbying`) until Newmark 2005 explicitly confirms its parallel.

---

## Open issues surfaced by Newmark 2017 (for compendium-2.0 freeze)

1. **`def_actor_class_*` row family — separate from `def_target_*` or merged into `actor_*`?** Newmark and Opheim treat "elected officials as lobbyists" / "public employees as lobbyists" as definitional inclusion criteria of the lobbyist concept (does the statutory definition cover these actor classes when they engage in lobbying behaviors). This is a third row family alongside CPI's `def_target_*` (who can be lobbied) and PRI's `actor_*` (who's required to register *as* a lobbying entity). The three families are real and distinct:
   - **`def_target_*`** — entities that can be the target of lobbying (whose communication triggers lobbyist status of the communicator). Reads: CPI #196, FOCAL scope.3, HG Q1.
   - **`actor_*`** — entities required to register *as* a lobbying entity (CSPI: "the legislative branch lobbying the executive" — a structural-actor row). Reads: PRI A1–A11.
   - **`def_actor_class_*`** (proposed) — individual-actor classifications that affect lobbyist-definition coverage when those individuals engage in lobbying behaviors as individuals (does an elected official, when personally lobbying, fall under the lobbyist definition?). Reads: Newmark 2017/2005, Opheim.
   The three families are conceptually distinct but the third is fragile — could be folded into one of the other two with care. Defer to compendium 2.0 freeze. (PRI A-family content not directly walked this session — Newmark 2005 mapping or PRI re-walk should confirm whether `def_actor_class_*` overlaps PRI A6 or similar.)

2. **`lobbyist_spending_report_includes_compensation_broken_down_by_client` — "client" vs "employer" naming.** Newmark uses "employer"; Sunlight uses "client". Same observable. Compendium 2.0 should rename to either `_by_paying_entity` or `_by_employer_or_client`. Functional rename; flagged.

3. **`lobbyist_or_principal_report_includes_contributions_received_for_lobbying` — actor split.** Currently bundled. Granularity-bias says split into `lobbyist_*` + `principal_*` parallel rows (consistent with the principal-vs-lobbyist pattern throughout PRI mapping). Newmark doesn't distinguish. Defer to compendium 2.0 freeze; the projection is identical (OR over two actor-side rows if split).

4. **Handoff watchpoint correction — the three def.*_standard items read THREE typed cells, not one.** The 2026-05-11 handoff suggested "Should read the existing CPI #197 cell ... as `cell IS NOT NULL`" for all three Newmark def.*_standard items. Charitable reading: the watchpoint is shorthand for "follow the CPI #197 typed-cell pattern" — not a literal claim that all three Newmark items read the same cell. The compensation / expenditure / time threshold concepts are independently extant in state regimes (a state can have a compensation standard but no expenditure or time standard, etc.). Three separate typed cells. Documenting the correction here for visibility to subsequent mapping agents — the handoff threshold table's "Newmark/Opheim def.*_standard" entry collapses the family to one line for brevity but doesn't mean one cell.

5. **No per-state per-atomic-item ground truth from Newmark 2017.** Newmark publishes only sub-aggregate per-state totals (Table 2). Phase C validation against Newmark directly is sub-aggregate-only: 50 states × 2 sub-aggregates (`def.section_total`, `disclosure.section_total`) = 100 cells. Per-item validation has to come from cross-rubric overlap with PRI (per-item per-state available in `docs/historical/pri-2026-rescore/`) and CPI 2015 C11 (700-cell ground truth available in `results/cpi_2015_c11_per_state_scores.csv`). The BoS-derived items in particular are correct-by-construction when fed from PRI's or CPI's published cells (both rubrics use BoS or state statute as upstream source).

6. **Two no-variation items — `def.legislative_lobbying` and `disclosure.expenditures_benefiting_officials`.** Cells are extracted normally (compendium 2.0 doesn't elide rows based on observed 2015 variation); Newmark's factor-analysis exclusion is a statistical artifact, not a definitional claim. Phase C: project these as TRUE for all 50 states; `def.section_total` validation must account for the constant +1 contribution from `def.legislative_lobbying`; `disclosure.section_total` similarly has a constant +1 from `disclosure.expenditures_benefiting_officials`.

## What Newmark 2017 doesn't ask that other rubrics will

For continuity with other rubric mappings: Newmark does not read any registration form content beyond the lobbyist definition (Sunlight #1 reg-form rows territory; HG Q3-Q10 territory), any timeliness of disclosure (PRI E1h/E2h cadence, CPI #199/#202), any itemization-de-minimis threshold (Sunlight #3, HG Q15), any filing-de-minimis threshold (PRI D1), any per-meeting contact log granularity (FOCAL contact_log.* battery), any specific bill-number disclosure (FOCAL contact_log.11, PRI E1g_ii/E2g_ii — although Newmark's `disclosure.influence_legislation_or_admin` is the coarse cousin), any portal-accessibility / search / filter cells (CPI #205-206, FOCAL openness.*, HG Q28-Q34, PRI Q1-Q6 + Q7a-Q7o), any reporting-frequency enum or cadence cells (PRI E1h/E2h, CPI #202), any audit / enforcement cells (CPI #207-209, HG Q39-Q47 — enforcement-side, also out of disclosure-only scope).

All of these enter compendium 2.0 from other rubric mappings, not Newmark's. Newmark's role within the contributing-rubric set is **cross-rubric redundancy on the definitional-and-disclosure backbone of BoS-derived items** — 8 of 14 rows it touches are already established; the 6 new rows largely overlap with Newmark 2005 (next-up mapping) and Opheim (later).
