<!-- Generated during: convos/20260513_row_freeze_brainstorm.md -->

# Compendium 2.0 row-freeze decision log

**Date:** 2026-05-13 (late-late-late-late eve / 2026-05-14 UTC)
**Session convo:** [`../../convos/20260513_row_freeze_brainstorm.md`](../../convos/20260513_row_freeze_brainstorm.md)
**Originating handoff:** [`../../plans/_handoffs/20260513_row_freeze_brainstorm.md`](../../plans/_handoffs/20260513_row_freeze_brainstorm.md)
**Input TSV:** [`disclosure_side_compendium_items_v1.tsv`](disclosure_side_compendium_items_v1.tsv) (186 rows: 182 firm + 4 LV freeze-candidates)
**Output TSV:** [`disclosure_side_compendium_items_v2.tsv`](disclosure_side_compendium_items_v2.tsv) (regenerated post-freeze)

This log captures **non-trivial freeze decisions**: row renames, row merges, in/out dispositions for candidate rows, and resolutions to per-mapping-doc Open Issues. Trivial cosmetic decisions (cell_type whitespace normalization, etc.) are applied silently in the v2 TSV.

---

## Section 1 — Naming canonicalization (load-bearing)

Cross-rubric naming drift in the union step caused the mechanical TSV to *under*count cross-rubric readings on several load-bearing observables. Doc narratives consistently cite these as the same observable across multiple rubrics; the union step missed it because the first-introducing doc used a different row_id. Below are the canonicalization decisions.

### D1 — Compensation cluster: merge into `lobbyist_spending_report_includes_total_compensation`

**Decision:** Merge the following row_ids into the canonical `lobbyist_spending_report_includes_total_compensation`:

| Source row_id (v1) | Merge target (v2) | Source rubric(s) | Evidence |
|---|---|---|---|
| `lobbyist_report_includes_direct_compensation` | `lobbyist_spending_report_includes_total_compensation` | PRI E2f_i | PRI mapping line 670; FOCAL/HG/Newmark/Opheim/Sunlight docs all cite "PRI E2f_i ('Direct lobbying costs (compensation)')" as a cross-rubric reader of the canonical row |
| `lobbyist_spending_report_includes_compensation` | `lobbyist_spending_report_includes_total_compensation` | CPI #201 | CPI mapping line 225; Sunlight/FOCAL/HG/Newmark/Opheim docs all cite "CPI #201 (compound)" as a cross-rubric reader of the canonical row |

**Result:** `lobbyist_spending_report_includes_total_compensation` becomes **8-rubric-confirmed** (cpi_2015 + focal_2024 + hg_2007 + newmark_2005 + newmark_2017 + opheim_1991 + pri_2010 + sunlight_2015). Single most-validated row in the compendium.

**Why:** Doc narratives consistently cite PRI E2f_i and CPI #201 as readers of the same "lobbyist's total compensation appears on the spending report" observable. The mechanical union missed this because PRI's mapping doc used a PRI-specific row_id (`lobbyist_report_includes_direct_compensation`) and CPI's used a CPI-specific row_id (`lobbyist_spending_report_includes_compensation`), even though both reference the canonical row in their cross-rubric annotations.

### D2 — Principal-side compensation merge: `principal_spending_report_includes_compensation_paid_to_lobbyists`

**Decision:** Merge `principal_report_includes_direct_compensation` (HG Q27 + PRI E1f_i) into the canonical `principal_spending_report_includes_compensation_paid_to_lobbyists` (CPI #203/#204).

**Result:** Becomes **3-rubric-confirmed** (cpi_2015 + hg_2007 + pri_2010).

**Why:** HG mapping line 514 and PRI mapping line 510 both explicitly cite CPI #203/#204 as the compound reading of the same principal-side compensation observable. Same naming-drift pattern as D1.

### D3 — PRI E1/E2 prefix rename: `*_report_includes_*` → `*_spending_report_includes_*`

**Decision:** All PRI E1 (principal-side) and PRI E2 (lobbyist-side) atomic-item rows that currently use the `principal_report_includes_*` or `lobbyist_report_includes_*` prefix are renamed to `*_spending_report_includes_*` for consistency with the α form-type split convention (Decision Rule 4: same content cell exists separately for reg-form side vs spending-report side).

**Scope:** PRI 2010 paper section E is explicitly "Spending reports" — every E1/E2 atomic item is spending-report-content. The current generic `_report_includes_*` prefix is ambiguous and violates the α-split convention.

**Renames applied to v2 TSV** (lobbyist side, 10 rows):

| v1 row_id | v2 row_id |
|---|---|
| `lobbyist_report_includes_contacts_made` | `lobbyist_spending_report_includes_contacts_made` |
| `lobbyist_report_includes_general_issues` | `lobbyist_spending_report_includes_general_issues` |
| `lobbyist_report_includes_gifts_entertainment_transport_lodging` | `lobbyist_spending_report_includes_gifts_entertainment_transport_lodging` |
| `lobbyist_report_includes_indirect_costs` | `lobbyist_spending_report_includes_indirect_costs` |
| `lobbyist_report_includes_lobbyist_contact_info` | `lobbyist_spending_report_includes_lobbyist_contact_info` |
| `lobbyist_report_includes_principal_business_nature` | `lobbyist_spending_report_includes_principal_business_nature` |
| `lobbyist_report_includes_principal_contact_info` | `lobbyist_spending_report_includes_principal_contact_info` |
| `lobbyist_report_includes_principal_names` | `lobbyist_spending_report_includes_principal_names` |
| `lobbyist_report_includes_specific_bill_number` | `lobbyist_spending_report_includes_specific_bill_number` |
| `lobbyist_report_uses_itemized_format` | `lobbyist_spending_report_uses_itemized_format` |

(`lobbyist_report_includes_direct_compensation` was merged in D1; not in this list.)

**Renames applied to v2 TSV** (principal side, 10 rows):

| v1 row_id | v2 row_id |
|---|---|
| `principal_report_includes_business_nature` | `principal_spending_report_includes_business_nature` |
| `principal_report_includes_contacts_made` | `principal_spending_report_includes_contacts_made` |
| `principal_report_includes_general_issues` | `principal_spending_report_includes_general_issues` |
| `principal_report_includes_gifts_entertainment_transport_lodging` | `principal_spending_report_includes_gifts_entertainment_transport_lodging` |
| `principal_report_includes_indirect_costs` | `principal_spending_report_includes_indirect_costs` |
| `principal_report_includes_lobbyist_contact_info` | `principal_spending_report_includes_lobbyist_contact_info` |
| `principal_report_includes_lobbyist_names` | `principal_spending_report_includes_lobbyist_names` |
| `principal_report_includes_major_financial_contributors` | `principal_spending_report_includes_major_financial_contributors` |
| `principal_report_includes_principal_contact_info` | `principal_spending_report_includes_principal_contact_info` |
| `principal_report_includes_specific_bill_number` | `principal_spending_report_includes_specific_bill_number` |
| `principal_report_includes_total_expenditures` | `principal_spending_report_includes_total_expenditures` |
| `principal_report_uses_itemized_format` | `principal_spending_report_uses_itemized_format` |

(`principal_report_includes_direct_compensation` was merged in D2; not in this list.)

**Cadence rows also renamed** (12 rows — PRI E1h + E2h):

| v1 row_id | v2 row_id |
|---|---|
| `lobbyist_report_cadence_includes_annual` | `lobbyist_spending_report_cadence_includes_annual` |
| `lobbyist_report_cadence_includes_monthly` | `lobbyist_spending_report_cadence_includes_monthly` |
| `lobbyist_report_cadence_includes_other` | `lobbyist_spending_report_cadence_includes_other` |
| `lobbyist_report_cadence_includes_quarterly` | `lobbyist_spending_report_cadence_includes_quarterly` |
| `lobbyist_report_cadence_includes_semiannual` | `lobbyist_spending_report_cadence_includes_semiannual` |
| `lobbyist_report_cadence_includes_triannual` | `lobbyist_spending_report_cadence_includes_triannual` |
| `lobbyist_report_cadence_other_specification` | `lobbyist_spending_report_cadence_other_specification` |
| `principal_report_cadence_includes_annual` | `principal_spending_report_cadence_includes_annual` |
| `principal_report_cadence_includes_monthly` | `principal_spending_report_cadence_includes_monthly` |
| `principal_report_cadence_includes_other` | `principal_spending_report_cadence_includes_other` |
| `principal_report_cadence_includes_quarterly` | `principal_spending_report_cadence_includes_quarterly` |
| `principal_report_cadence_includes_semiannual` | `principal_spending_report_cadence_includes_semiannual` |
| `principal_report_cadence_includes_triannual` | `principal_spending_report_cadence_includes_triannual` |
| `principal_report_cadence_other_specification` | `principal_spending_report_cadence_other_specification` |

**Newmark-introduced row also renamed** (1 row):

| v1 row_id | v2 row_id |
|---|---|
| `lobbyist_or_principal_report_includes_contributions_received_for_lobbying` | `lobbyist_or_principal_spending_report_includes_contributions_received_for_lobbying` |

### D4 — Filing-de-minimis threshold rename

**Decision:** Rename `materiality_threshold_financial_value` (PRI D1) → `lobbyist_filing_de_minimis_threshold_dollars`. Rename `materiality_threshold_time_percent` (PRI D1) → `lobbyist_filing_de_minimis_threshold_time_percent`.

**Why:** Sunlight 2015 mapping introduced an explicit three-threshold-concept framework (Decision Rule 6: lobbyist-status threshold = for registration; filing-de-minimis threshold = for filing; itemization-de-minimis threshold = for itemized line items). PRI D1's `materiality_*` cells map onto the filing-de-minimis concept. The current `materiality_threshold_*` name is PRI-vocabulary; the new name aligns with the three-threshold framework that's now compendium convention.

### D5 — Compensation-broken-down row rename

**Decision:** Rename `lobbyist_spending_report_includes_compensation_broken_down_by_client` → `lobbyist_spending_report_includes_compensation_broken_down_by_payer`.

**Why:** Sunlight uses "client", Newmark uses "employer" — same observable. "Payer" is rubric-neutral and covers both (in-house lobbyists have employer-payers; contract lobbyists have client-payers). Resolves Newmark 2017 Open Issue 2.

### D6 — `def_target_*_staff` split

**Decision:** Split `def_target_legislative_or_executive_staff` into two cells:

- `def_target_legislative_staff` (existing — CPI #196)
- `def_target_executive_staff` (NEW — was implicit in FOCAL `scope.3`)

FOCAL `scope.3` projection becomes `def_target_legislative_staff OR def_target_executive_staff` (the "all staff" tier).

**Why:** Granularity-bias supports the split. Real states differ on which side (e.g., a state may include legislative aides but exclude executive-agency staff). The existing combined cell loses this distinction. Two clean cells in the family.

**Resulting `def_target_*` family (5 cells):**
1. `def_target_legislative_branch`
2. `def_target_executive_agency`
3. `def_target_governors_office`
4. `def_target_independent_agency`
5. `def_target_legislative_staff`
6. `def_target_executive_staff` **NEW from split**

### D7 — `contributions_received_for_lobbying`: keep combined

**Decision:** Keep as single combined row `lobbyist_or_principal_spending_report_includes_contributions_received_for_lobbying` (after D3 rename). Do **not** split into lobbyist-side + principal-side variants.

**Why:** Newmark's source quote doesn't specify actor side; in practice, the observable typically lives on principal-side (e.g., trade-association principal listing member-earmarked dues). Granularity-bias would split, but YAGNI argues against doubling an already-single-rubric row. Resolves Newmark 2017 Open Issue 3.

### D8 — `lobbyist_disclosure_includes_*` → `lobbyist_reg_form_includes_*`

**Decision:** Rename two rows for prefix consistency:

| v1 row_id | v2 row_id |
|---|---|
| `lobbyist_disclosure_includes_business_associations_with_officials` | `lobbyist_reg_form_includes_business_associations_with_officials` |
| `lobbyist_disclosure_includes_employment_type` | `lobbyist_reg_form_includes_employment_type` |

**Why:** HG Q22 is explicitly a reg-form question; FOCAL `descriptors.*` is also reg-form-side. The `lobbyist_disclosure_*` prefix is ambiguous; `lobbyist_reg_form_includes_*` is the family these rows belong to.

---

## Section 2 — Cell_type cosmetic normalization (auto-applied)

The following cell_type variants were normalized in v2 silently (not freeze-blockers per Watchpoint 6):

- `typed Optional[<TimeThreshold>]` → `typed Optional[TimeThreshold]`
- `binary (practical)` → `binary` (axis carries the practical/legal distinction)
- `binary (legal) + typed int 0-100 step 25 (practical)` → kept as-is (semantic two-axis declaration)
- `binary derived from CPI #206's 4-feature cell` → `binary` (the derivation provenance lives in the doc, not the cell_type)
- Multiple whitespace/backtick variants — collapsed.

## Section 3 — Cell_type semantic conflicts (resolved at freeze)

Three rows had cross-rubric cell_type disagreements that **are** real freeze decisions per Watchpoint 7:

### D9 — `lobbying_data_downloadable_in_analytical_format` cell type

**Disagreement:** PRI says "binary derived from CPI #206's 4-feature cell"; FOCAL says "binary".

**Decision:** **Single binary cell.** The CPI #206 4-feature compound is itself a derived projection over CPI's underlying typed cell (`lobbying_data_open_data_quality` row 46). Both PRI's "downloadable in analytical format" and FOCAL's analog read the same underlying binary observable (does the portal offer analytic-format download). Mark as `binary`. CPI #206's 4-feature compound is a separate row (already at row 46 as `lobbying_data_open_data_quality`).

### D10 — `lobbyist_registration_required` is two-axis

**Disagreement:** CPI says two-axis (legal binary + practical typed int 0-100 step 25); HG says legal binary only.

**Decision:** **Keep two-axis.** CPI explicitly carries a practical-availability tier (whether the registration system is actually accessible / used). HG's legal-only read is a subset projection. Cell_type: `binary (legal) + typed int 0-100 step 25 (practical)`.

### D11 — `registration_deadline_days_after_first_lobbying` is two-axis

**Disagreement:** CPI says two-axis (legal typed int + practical typed int 0-100 step 25); HG says legal binary only.

**Decision:** **Keep two-axis** with the legal-side typed as `Optional[int]` (days). HG Q4's binary "registration required within N days" is a subset projection (`legal IS NOT NULL` checks the existence). CPI's practical tier is the accessibility-of-the-deadline-process.

---

## Section 4 — Named freeze-candidate dispositions

### D12 — LV-1: `lobbyist_report_distinguishes_in_house_vs_contract_filer` — **IN**

**Decision:** PULL IN as firm row. Promoted from freeze-candidate.

**Why:** LDA explicitly distinguishes in-house from contract filer; Kim 2025 GNN uses it as a node feature. Real distinguishing observable in some states even though partially implicit in α form-split. Worth tracking for both extraction and downstream-analytics use.

**Cell type:** `binary` (axis: `legal`).
**Reading rubrics:** `lobbyview` (single-rubric — first reader; LV's `is_client_self_filer` field).

### D13 — LV-2: `lobbyist_filings_flagged_as_amendment_vs_original` — **OUT**

**Decision:** OMIT from compendium 2.0 freeze. Reversible — can re-add to a later practical-axis-only freeze if a portal pipeline shows downstream need.

**Why:** Operational metadata (filing-system behavior), not a disclosure-substance observable. Doesn't serve the projection-validation success criterion.

### D14 — LV-3: `lobbying_disclosure_uses_standardized_issue_code_taxonomy` — **OUT (reversibly tabled)**

**Decision:** DO NOT add at this freeze. Despite the LobbyView mapping doc's IN-with-typed-enum recommendation, the user's call: typed-enum complexity isn't worth it for a single-rubric LobbyView-distinctive observable that's federal-LDA-shaped (state-level pickup is weaker — most states have state-specific or free-text taxonomies that don't fit a clean enum).

**Why:** YAGNI — defer until a state-level rubric reads it or extraction surfaces need. Single-rubric LobbyView additions need a stronger affirmative case than "could be typed enum."

### D15 — LV-4: `lobbying_report_records_inferred_bill_links_to_specific_bills` — **OUT**

**Decision:** OMIT (matches LobbyView mapping recommendation).

**Why:** Operational (Kim 2018 inference pipeline output), NOT a state-disclosed observable. The disclosed observable (`lobbyist_spending_report_includes_bill_or_action_identifier`) is already covered.

### D16 — OS-1: `separate_registrations_for_lobbyists_and_clients` — **IN (path b)**

**Decision:** PULL IN as firm row. Path (b) project-internal need per the OpenSecrets-tabled doc.

**Why:** Real distinguishing statutory observable — some states require lobbyists AND clients to file independent forms; others a single combined form. Affects entity-count downstream stats. OpenSecrets Cat 1 reads it but is itself tabled (so this row enters unvalidated against any current rubric). Cost: 1 row. Benefit: data infrastructure preservation.

**Cell type:** `binary` (axis: `legal`).
**Reading rubrics:** none (path-b unvalidated). Source provenance: `_tabled/opensecrets_2022_tabled.md` Candidate 1.
**Watchpoint:** if extraction reveals OS scoring would benefit from inclusion, OS-tabling reverses.

### D17 — OS-2: `lobbyist_compensation_disclosed_as_exact_amount_vs_ranges` — **OUT (reversibly tabled)**

**Decision:** DO NOT add at this freeze. Stays in `_tabled/opensecrets_2022_tabled.md`.

**Why:** Real observable, but more downstream-utility-shaped than core-disclosure-shaped. The compensation-disclosure rows already cover existence and per-payer breakdown. The exact-vs-ranges granularity can be flagged on extracted cells (as a `disclosure_value_format` annotation or separate practical-axis row) if downstream analytics ever needs it. YAGNI defers.

### D18 — OS-3: `lobbyist_compensation_disclosed_per_individual_lobbyist_vs_aggregate` — **OUT (reversibly tabled)**

**Decision:** DO NOT add at this freeze. Stays in `_tabled/opensecrets_2022_tabled.md`.

**Why:** Real observable, but distinct from the existing `compensation_broken_down_by_payer` row in a subtle way (per-lobbyist within a firm vs per-payer across the firm's clients). Adding adds row complexity without a current rubric reading. YAGNI defers; can re-enter via path (a) if a state rubric reads the per-individual-lobbyist split.

### D19 — Open Issue: full-text vs structured search split — **DEFER**

**Decision:** Do not split `lobbyist_directory_available_as_searchable_database_on_web` into full-text vs structured-search variants.

**Why:** No current rubric reads the distinction. LobbyView's Elasticsearch-vs-Whoosh implementation difference is production-implementation-level, not statutorily disclosed. YAGNI.

---

## Section 5 — Per-mapping-doc Open Issues — dispositions

The handoff enumerated ~36 real freeze decisions across 9 mapping docs. Most are resolved by the meta-rules in Sections 1, 3, and the atomization meta-rule (D20 below). The remainder are listed here.

### D20 — Atomization meta-rule: keep current per-rubric atomization

**Decision:** No changes to atomization status. PRI E1h/E2h cadence stays atomized as 12 binary cells (6 lobbyist + 6 principal). PRI Q7a-o stays atomized as 15 binary search-filter cells. FOCAL `scope.1` stays as 1 set-typed cell (9 actor types). FOCAL `scope.4` stays as 1 set-typed cell (8 activity types). FOCAL `contact_log` stays atomized as 9 binary cells. FOCAL `descriptors` stays atomized as 5 binary cells. HG Q31/Q32 stays atomized as 4 binary access-tier cells.

**Why:** Source-rubric atomization is preserved. Projection logic is identical regardless (sum-of-binaries vs count-of-set-members). The extraction prompt accommodates both binary and set-typed cells already (set-typed cells exist for `compensation_threshold_*`, `lobbying_definition_included_*`, etc.). Changing atomization at freeze would force per-rubric re-mapping work without semantic gain.

**Resolves Open Issues:** PRI cadence atomization (PRI Open Issue 1 / handoff §pri_2010 #1), PRI Q7a-o granularity (handoff §pri_2010 #4), FOCAL set-typed cells scope.1/.4 (FOCAL Open Issue 2), FOCAL per-meeting contact_log atomization (FOCAL session decision), FOCAL descriptors atomization (FOCAL session decision), HG Q31/Q32 4-tier-vs-typed-enum (HG Open Issue handoff §hiredguns_2007 #3).

### D21 — HG-1: `def_target_executive_agency` legislative-action-only carve-out → DEFER

**Decision:** Do not split `def_target_executive_agency` into `_standalone` vs `_only_re_pending_legislation`. Single cell stays.

**Why:** HG Q1's stricter coding (no points if executive recognition is only-via-legislative-action) is a HG-projection edge case. Document the divergence in the HG mapping doc; Phase C can surface if it materially affects HG-vs-published validation. CPI 2015 doesn't preserve the 2007 distinction, so the row inflation isn't payed for by other rubrics either.

### D22 — HG-2: Q2 'make/spend' projection → `min(compensation_threshold, expenditure_threshold)` where both non-null

**Decision:** HG Q2's threshold projection reads `compensation_threshold_for_lobbyist_registration` AND `expenditure_threshold_for_lobbyist_registration` and projects against the smaller (binding) value. If only one is non-null, read that one.

**Why:** HG's wording bundles compensation and expenditure into one threshold question. The smaller of the two is the binding registration trigger in practice. No new compendium row needed; logic lives in HG's projection function.

### D23 — Opheim catch-all un-projectable item → OUT-of-scope; document in Opheim mapping

**Decision:** Opheim's 1 atomic item that doesn't project to any compendium cell stays un-projectable. Don't create a row for it.

**Why:** An unvalidated row defeats the projection-success criterion. The Opheim mapping doc's existing note explaining the un-projectability is sufficient; Phase C tolerance for Opheim accounts for the missing item.

### D24 — Sunlight item-4 underlying-cell retention, Newmark 2005 vintage-stability, Opheim cadence-monthly cell narrowing, HG Q12 session-calendar metadata, HG Q23/Q24 partial-scope, HG itemized-detail conditional-cascade, FOCAL partly-tier semantics → DEFERRED to Phase C

**Decision:** These ~7 remaining per-doc Open Issues are about projection logic (how a rubric projection function reads compendium cells), not about row identity / cell type / axis. They don't block the freeze and are deferred to Phase C projection-implementation work where each will be resolved in the rubric's projection function code under TDD.

**Why:** Freeze blocks merge to main; projection logic doesn't. Per the locked Phase C plan, projections are coded one rubric at a time after merge. Each projection function will encode the resolved interpretation in TDD-tested code.

### D25 — `actor_*` family (PRI A1-A11, 11 binary rows) → KEEP all, single-rubric per row

**Decision:** All 11 `actor_*_registration_required` rows stay as single-rubric (PRI). KEEP per Decision Rule 1 (single-rubric is NOT a deletion criterion when observable is real).

**Why:** Each represents a distinct institutional-actor type whose registration requirement varies state-by-state. The PRI A-family is structurally different from the `def_target_*` family (target of lobbying) and the `def_actor_class_*` family (individual-actor classes like elected officials / public employees). These three families are co-existing axes per established Decision Rule 3 (def_actor_class is 3-rubric-confirmed; def_target is 6-rubric; actor_ is PRI-distinctive). All three KEEP.

### D26 — PRI E1/E2 contents (after D3 rename): KEEP all atomized, single-rubric per row

**Decision:** All 21 `lobbyist_spending_report_includes_*` and `principal_spending_report_includes_*` rows that are PRI-distinctive (single-rubric after canonicalization) stay as separate rows.

**Why:** Each is a real reporting-content observable that PRI's atomic-item structure isolates. Per Decision Rule 1, single-rubric KEEP. Atomization is consistent with PRI's source structure.

### D27 — PRI exemption + govt_agencies + public_entity_def + law_* rows (single-rubric PRI): KEEP

**Decision:** All PRI single-rubric rows in these batteries (rows 23, 24, 27, 28, 29, 30, 177, 178, 179) stay.

**Why:** Each captures a real definitional / exemption observable. PRI's atomization isolates legitimately distinct observables. Per Decision Rule 1, KEEP.

### D28 — HG-distinctive practical-availability rows: KEEP

**Decision:** All HG single-rubric practical-axis rows (lobbyist_directory_*, online_lobbyist_*, oversight_agency_*, sample_lobbying_forms_available_on_web, lobbyist_required_to_submit_photograph_with_registration, lobbying_records_copy_cost_per_page_dollars, lobbyist_spending_report_required_when_no_activity, lobbyist_spending_report_scope_includes_household_members_of_officials, expenditure-itemization-detail rows) stay.

**Why:** Each captures a real observable about portal mechanics or statute provisions that HG isolated. Per Decision Rule 1, KEEP. Many are populated by Track B (portal pipeline), but the legal/practical scope distinction is preserved per Decision Rule 7.

### D29 — FOCAL-distinctive single-rubric rows: KEEP

**Decision:** All FOCAL single-rubric rows (consultant_lobbyist_report_includes_income_by_source_type; lobbying_contact_log_includes_*; lobbying_data_changes_flagged_with_versioning; lobbying_data_no_user_registration_required; lobbying_data_open_license; lobbying_definition_included_activity_types; lobbying_disclosure_data_includes_unique_identifiers; lobbying_disclosure_data_linked_to_other_datasets; lobbyist_definition_included_actor_types; lobbyist_or_principal_*reg_form_includes_lobbyist_board_memberships; lobbyist_or_principal_*report_includes_lobbyist_count_total_and_FTE; lobbyist_or_principal_*report_includes_time_spent_on_lobbying; lobbyist_or_principal_*report_includes_trade_association_dues_or_sponsorship; lobbyist_reg_form_includes_*; ministerial_diaries_*; principal_or_lobbyist_reg_form_includes_member_or_sponsor_names; principal_spending_report_includes_total_expenditures; principal_report_lists_lobbyists_employed) stay.

**Why:** FOCAL atomization at the per-meeting / per-descriptor / per-actor-type level captures real distinguishing observables not present in pre-2024 rubrics. The reuse rate (38.5%) is low because FOCAL introduces genuinely new structural detail. Per Decision Rule 1, KEEP.

### D30 — CPI-distinctive single-rubric rows: KEEP

**Decision:** All CPI single-rubric rows (def_target_independent_agency, lobbying_data_open_data_quality, lobbying_disclosure_audit_required_in_law, lobbying_disclosure_documents_online, lobbying_disclosure_offline_request_response_time_days, lobbying_violation_penalties_imposed_in_practice, lobbyist_spending_report_filing_cadence, principal_spending_report_includes_compensation_paid_to_lobbyists [now 3-rubric after D2]) stay.

**Why:** CPI's two-axis cells (legal binary + practical typed int 0-100 step 25) capture observables no other rubric reads at the same granularity. Per Decision Rule 1, KEEP.

---

## Section 6 — Single-rubric row family summary (post-freeze)

After D1-D30, the v2 TSV row tier distribution is:

| n_rubrics | row count v1 | row count v2 | notes |
|---|---:|---:|---|
| 8 | 0 | **1** | `lobbyist_spending_report_includes_total_compensation` (D1 merge: PRI + CPI added) |
| 6 | 5 | 4 | gifts_entertainment lobbyist + principal pair (renamed); def_target_executive_agency; compensation_threshold; (was 5: total_compensation moved to 8-tier) |
| 5 | 3 | 3 | def_target_legislative_branch; categorizes_expenses; compensation_broken_down_by_payer (renamed) |
| 4 | 6 | 6 | bill_or_action_identifier; expenditure_threshold; spending_report_includes_general_subject_matter; spending_report_includes_total_expenditures; spending_report_required; time_threshold |
| 3 | 9 | 10 | unchanged + principal_spending_report_includes_compensation_paid_to_lobbyists promoted to 3-rubric via D2 |
| 2 | 24 | 24 | def_target_legislative_staff promoted to 2-rubric via D6 |
| 1 | 135 | 132 | D1 removes 2 (rows 114, 132 merge into 138 → leaves 1-rubric, joins 8-rubric); D2 removes 1 (row 175 was 1-rubric, gains 2 readers from row 163, joins 3-rubric); D6 collapse removes both staff cells from 1-rubric (legislative_or_executive_staff merges into legislative_staff which becomes 2-rubric: -2); D6 split adds executive_staff at 1-rubric (+1); LV-1 promotion adds at 1-rubric (+1). Math: 135 - 2 - 1 - 2 + 1 + 1 = 132. ✓ |
| 0 | 4 | 1 | All 4 LV freeze-candidates resolved (LV-1 IN, 3 OUT); OS-1 added as path-b unvalidated (n=0). |
| **Total** | **186** | **181** | |

---

## Section 7 — Final v2 TSV summary

**File:** [`disclosure_side_compendium_items_v2.tsv`](disclosure_side_compendium_items_v2.tsv)

**Counts:**
- 181 total rows (down from 186 in v1).
- 180 firm + 1 unvalidated path-b (OS-1).
- 0 freeze-candidates (all resolved).

**Most-validated row:** `lobbyist_spending_report_includes_total_compensation` (8-rubric: cpi_2015 + pri_2010 + sunlight_2015 + newmark_2017 + newmark_2005 + opheim_1991 + hg_2007 + focal_2024). The single canonical compensation row replaces the 3 v1 variants (`_includes_compensation`, `_includes_direct_compensation`, `_includes_total_compensation`).

**Generation script:** [`tools/freeze_canonicalize_rows.py`](../../../../../tools/freeze_canonicalize_rows.py) — reads v1.tsv + the encoded D1-D19 decision data structures + applies merges/renames/promotions/additions/normalization. Re-running the script reproduces v2.tsv exactly (idempotent). Future freeze edits should be made in the script's data structures + this decision log, then the script re-run, rather than editing v2.tsv by hand.

**Merge to main:** v2 row set is the contract that successor branches reference. The 3 successor tracks (OH retrieval, harness brainstorm, Phase C projection TDD) all read this row set. Once `compendium-source-extracts` merges to main, row-set changes require a new branch.

---

## Appendix — Open Issues NOT addressed at this freeze

These are not blockers but should be tracked:

1. **v2.0 schema bump** — `MatrixCell.value: Any` constrained by `CompendiumItem.data_type`. Current schema (v1.2) has `data_type` declared on `CompendiumItem` but no carrier on `MatrixCell`. Separate plan; doesn't block freeze (compendium 2.0 row design is data_type-aware regardless of carrier shape).
2. **Practical-axis cells** stay null until Track B (portal pipeline) populates. Per Decision Rule 2: extraction harness is responsible only for legal-axis cells; practical-axis cells are flagged for Track B.
3. **PAPER_INDEX 17 vs 18 PDFs + 16+ branch-added papers** — separate `auditing-paper-summaries` pass before merge.
4. **Embedding `.npy` purge** — already executed (verified clean by 2026-05-13 union step).
5. **Provenance-header retrofit** for ~35 `results/*.md` files — low-priority, deferred (existing implicit provenance adequate per audit).

