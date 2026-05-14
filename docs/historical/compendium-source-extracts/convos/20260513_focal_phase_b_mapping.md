# 20260513 — FOCAL 2024 projection mapping (8th Phase B rubric)

**Date:** 2026-05-13 (evening, immediately after HiredGuns shipped)
**Branch:** compendium-source-extracts

## Summary

Executed Phase B FOCAL 2024 projection mapping per the locked plan (`plans/20260507_atomic_items_and_projections.md`) and the 2026-05-11 handoff's per-rubric FOCAL watchpoint section. FOCAL 2024 is the eighth rubric to ship in Phase B (after CPI 2015 C11, PRI 2010, Sunlight 2015, Newmark 2017, Newmark 2005, Opheim 1991, HiredGuns 2007; OpenSecrets 2022 was tabled 2026-05-13). LobbyView (federal LDA schema-coverage check — different shape) is the final remaining Phase B mapping.

The session followed the locked 2026-05-11 workflow: cross-rubric grep BEFORE drafting each compendium row, leveraging the 7 predecessor mapping docs which pre-annotated many FOCAL→compendium-row mappings as forward references. The grep surfaced ~22 reusable rows out of 48 in-scope items + 35 NEW rows (a 38.5% row-reuse rate — substantially lower than HG's prediction of ≥70%, driven mostly by FOCAL's distinctive per-meeting contact_log atomization (9 new rows) and per-lobbyist descriptors atomization (5 new rows) that no other contributing rubric reads).

Mapping doc shipped at `results/projections/focal_2024_projection_mapping.md` (957 lines; longest single mapping after PRI). All 48 in-scope items mapped per the locked Phase B per-item template; 2 `revolving_door.*` items deferred per strict plan reading with `revolving_door.1` flagged as Open Issue FOCAL-1 for compendium 2.0 freeze reconsideration. The 2025-only "Lobbyist list" indicator (added in Lacy-Nichols 2025 application to Relationships category) is documented as `principal_report_lists_lobbyists_employed` (1 additional NEW row not in 2024 source TSV).

## Topics Explored

- All 48 in-scope FOCAL atomic items mapped per the locked Phase B per-item template:
  - **Scope (4 items):** 2 set-typed cells NEW (actor-types, activity-types) + 3 existing threshold cells reused + 3 existing target cells reused + 1 NEW staff target cell.
  - **Timeliness (3 items, with 2025 merge of .1+.2):** HG Q38 cadence cell reused (2-rubric-confirmed) + 1 NEW ministerial-diary cadence (US-N/A).
  - **Openness (9 items):** 4 existing cells reused (`state_has_dedicated_lobbying_website`, `lobbying_data_downloadable_in_analytical_format`, `lobbying_search_simultaneous_multicriteria_capability`, `lobbying_data_historical_archive_present`, `lobbying_disclosure_documents_free_to_access`) + 5 NEW (ministerial-diaries-online, no-user-registration, open-license, unique-identifiers, linked-data, changes-flagged).
  - **Descriptors (6 items):** HG Q10 `lobbyist_disclosure_includes_employment_type` reused for descriptors.6 (2-rubric-confirmed) + 5 NEW reg-form-side cells (full-name, contact-details, legal-form, business-id, sector) — FOCAL atomizes per-lobbyist registration content finer than any contributing rubric.
  - **Relationships (4 items + 1 2025 addition):** 2 existing cells reused (`lobbyist_report_includes_principal_names` PRI E2c, `lobbyist_reg_form_lists_each_employer_or_principal` HG Q9, `lobbyist_disclosure_includes_business_associations_with_officials` HG Q22) + 2 NEW (member/sponsor-names, board-seats) + 1 NEW for 2025-only Lobbyist-list.
  - **Financials (11 items):** 6 existing rows reused (`lobbyist_spending_report_includes_total_compensation` 7-rubric-confirmed, `_compensation_broken_down_by_client` 5-rubric, `_total_expenditures`, gifts bundle 5-rubric, `_campaign_contributions` HG Q24) + 5 NEW (income-by-source-type, FTE-count, time-spent-reporting, principal-side-total-expenditures, expenditure-per-issue, trade-association-dues, compensated-status flag — though compensated-status reads via HG Q10 IS NOT NULL).
  - **Contact log (11 items):** 9 NEW rows (beneficiary-org, official-name, institution/dept, attendees, date, communication-form, location, materials-shared, topics-discussed) + 2 existing β-AND rows reused (`lobbyist_spending_report_includes_bill_or_action_identifier`, `lobbyist_spending_report_includes_position_on_bill`) — FOCAL's most-distinctive battery; PRI's coarse `_includes_contacts_made` (E1i/E2i) is the only parent.
- **Cross-rubric grep BEFORE drafting** per the locked 2026-05-11 workflow. Three parallel greps across the 7 existing mapping docs + targeted greps for FOCAL contact_log / descriptors / financials concepts. Surfaced ~22 reusable rows pre-annotated by predecessor mappings; minimal rework cycles.
- **Scope-qualifier decision logged: revolving_door.* DEFERRED per strict plan reading.** Plan enumerates 7 in-scope batteries and is silent on revolving_door (parallel to HG Q48 cooling-off and Newmark `prohib.revolving_door`). `revolving_door.1` (lobbyist's prior public offices disclosed on reg form) is statutorily disclosure-shaped but flagged as Open Issue FOCAL-1 for user reconsideration. Known Phase C validation tolerance: US federal LDA projects to 75/175 = 43% (max) vs published 81/182 = 45% — a 6-point known under-scoring fully attributable to revolving_door.1 deferral.
- **Watchpoint walked — `contributions_from_others` parallel in FOCAL financials.* battery: NO PARALLEL.** The 2026-05-11 handoff flagged FOCAL `financials.*` as the strongest remaining promotion candidate for Newmark 2017's `lobbyist_or_principal_report_includes_contributions_received_for_lobbying` row. Walking all 11 financials items confirms NO MATCH:
  - financials.1 = own total income (consultant lobbyist's compensation); .2 = income per client (per-paying-entity); .3 = income source types (closest candidate but reads sources of OWN income — government agencies / foundations / companies as payers, NOT third-party-contributions earmarked-for-lobbying); .4 = lobbyist count; .5 = time spent; .6 = total expenditure; .7 = compensated-status flag; .8 = expenditure per issue; .9 = trade-association dues (closest candidate — money OUT to third-party organizations that lobby, NOT money IN from third parties for own lobbying); .10 = gifts to officials; .11 = OUTGOING campaign contributions.
  - **Newmark 2017's row remains single-rubric across 8 of 9 contributing rubrics. LobbyView is the last remaining promotion check.**
- **2024 → 2025 application differences encoded in projection logic:** timeliness.1+.2 merged in 2025 (reads same compendium cell, applies projection once with weight 3); "Lobbyist list" indicator added to Relationships in 2025 (weight 3, new row `principal_report_lists_lobbyists_employed`). Source TSV stays 2024; projection logic handles the asymmetry; per-country CSV uses 2025 numbering.
- **Federal LDA scoring walks** for each indicator. Most US LDA scores align with audit-doc verbatim; surfaced one ordering ambiguity on Relationships (audit's "6 + 2 + 0 + 0 + 0 = 8" 5-entry sum vs 4 indicators in 2024 — the "6" likely corresponds to 2025-only Lobbyist-list at weight 3 raw 2). Flagged as FOCAL-5 for Phase C verification against per-country CSV directly.

## Provisional Findings

- **Row reuse rate by item: 22/57 = 38.5%.** Lowest reuse rate of any Phase B mapping. Below HG's ≥70% prediction because FOCAL's per-meeting contact_log atomization (9 NEW rows) and per-lobbyist descriptors atomization (5 NEW rows) introduce row families that no other contributing rubric reads. The remaining batteries (scope, openness, financials, relationships, timeliness) DO confirm at high reuse — only contact_log + descriptors expand the row set substantially.
- **35 NEW compendium rows introduced** — surpasses HG's 22 new rows, becoming the largest new-row contribution of any single Phase B mapping. Concentration: 9 contact_log + 5 descriptors + 5 openness + 5 financials + 1 staff target + 1 actor-types set + 1 activity-types set + 1 timeliness ministerial diary + 1 openness ministerial diary + 1 2025-only Lobbyist list + 5 misc.
- **`lobbyist_spending_report_includes_total_compensation` stays at 7-rubric-confirmed** (FOCAL is the 7th reader; the most-validated row in the compendium). Other promotions: gifts bundle remains 5-rubric-confirmed; bill_or_action_identifier α split rows hit 5-rubric-confirmed (Sunlight + HG + PRI + Opheim + FOCAL); position_on_bill at 3-rubric-confirmed (Sunlight + Opheim + FOCAL); business_associations_with_officials (HG Q22) at 2-rubric-confirmed; campaign_contributions (HG Q24) at 2-rubric-confirmed; employment_type (HG Q10) at 2-rubric-confirmed.
- **The `contributions_from_others` row is now single-rubric across 8 of 9 contributing rubrics** (Newmark 2017 only). FOCAL was the strongest remaining promotion candidate per the 2026-05-11 handoff; walking all 11 financials items falsified the promotion. Only LobbyView remaining as final check. **Compendium 2.0 freeze recommendation: KEEP the row** — observable is real (Newmark documents the cross-state variation; MA principal reports list earmarked dues; some states explicitly require it) but unusual; the row may be 1-rubric-confirmed in the contributing set but should not be discarded on cross-rubric-frequency grounds alone.
- **FOCAL is the first contributing rubric where the projection's max for US federal LDA is structurally < the published score.** Strict-plan-reading deferral of revolving_door.* costs 6 points (revolving_door.1 yes × weight 3 = 6 for US). Other contributing rubrics either had no federal data (Newmark, Opheim — state-only) or aligned naturally with the 50-state vs 51-jurisdiction extraction scope. FOCAL's federal-LDA-as-validation-anchor creates the first Phase C tolerance with a known signed delta.
- **9 NEW contact_log rows enable LobbyView schema-coverage at finer granularity.** LobbyView's Kim 2018/2025 schema captures per-filing fields (organization, agencies-contacted, issues, bill-numbers) but at LDA's quarterly aggregate granularity. FOCAL's per-meeting cells provide compendium structure that LobbyView API fields can be checked against; LobbyView fields are expected to populate the FOCAL contact_log.1/3/9/11 cells for federal jurisdiction (the 4 cells where US LDA scored partly>0).
- **`def_target_*` family expands to 4 cells with new `def_target_legislative_or_executive_staff`.** FOCAL scope.3's partly-tier (P=staff excluded) requires distinguishing staff coverage from major-branch coverage. Other contributing rubrics' 3-cell reads correspond to FOCAL "yes/partly major branches"; the staff cell discriminates "yes (incl staff)" from "partly (major branches but not staff)".
- **α form-type split is now established for descriptors.** FOCAL reads reg-form-side; PRI E2b reads spending-report-side `lobbyist_report_includes_lobbyist_contact_info`. 5 NEW reg-form-side rows (descriptors.1-5) introduce the α form-pair for descriptive content; the spending-report-side parallels may follow at compendium 2.0 freeze if a future rubric reads them.

## Decisions

| topic | decision |
|---|---|
| Eighth Phase B target | FOCAL 2024, completed (48 atomic items in scope; 2 deferred = revolving_door.*) |
| Row reuse | 22 of 57 distinct rows = 38.5% reuse (lowest single-mapping rate; below HG ≥70% prediction) |
| New rows introduced | 35 distinct new rows (most of any single Phase B mapping) |
| Scope-qualifier — revolving_door deferral | DEFERRED per strict plan reading; revolving_door.1 flagged Open Issue FOCAL-1 |
| Phase C validation tolerance | Known +6 under-scoring on US federal LDA (revolving_door.1 deferral); other tolerances minor |
| Watchpoint — `contributions_from_others` in FOCAL financials.* battery | NO PARALLEL; row stays single-rubric across 8 of 9 contributing rubrics |
| α form-type split for descriptors | APPLIED (5 NEW reg-form-side cells; α-pair on spending-report side deferred to compendium 2.0 freeze) |
| `def_target_*` family expansion | EXTENDED with `def_target_legislative_or_executive_staff` (4th cell) per FOCAL scope.3 partly-tier |
| 2024 → 2025 application differences | Encoded in projection logic; timeliness.1+.2 merged; 2025-only `principal_report_lists_lobbyists_employed` added |
| Per-meeting contact_log atomization | 9 NEW rows; FOCAL-distinctive at per-meeting granularity; PRI E1i/E2i are coarse parents |
| Phase C utility of FOCAL | Federal LDA per-indicator + per-jurisdiction (28 countries) ground truth in `focal_2025_lacy_nichols_per_country_scores.csv`; US states have NO FOCAL ground truth (state-level cross-rubric validation only) |
| Next target | LobbyView 2018/2025 (46 schema fields, schema-coverage check — different shape from score-projection) |

## Open Issues surfaced (for compendium 2.0 freeze)

11 Open Issues documented in the mapping doc:
1. **FOCAL-1**: `revolving_door.1` scope decision (user-deferred to scope-qualifier review).
2. **FOCAL-2**: Set-typed cells vs atomized binary cells (scope.1 = 9 actor types; scope.4 = 8 activity types).
3. **FOCAL-3**: openness.1 partly-tier mechanics (optional-registration / split-websites derived condition).
4. **FOCAL-4**: openness.4 partly-tier mechanics (data-completeness cell).
5. **FOCAL-5**: Audit-doc Relationships score-breakdown ordering ambiguity (verify per-country CSV directly).
6. **FOCAL-6**: relationships.4 partly-tier cell (`business_association_disclosure_detail_level` enum).
7. **FOCAL-7**: 2024→2025 application differences in projection logic vs source TSV (encoded in logic; consider re-extracting source for 2025 numbering).
8. **FOCAL-8**: Ministerial diary rows are US-N/A but kept for compendium completeness.
9. **FOCAL-9**: financials.5 (REPORTING-side time-spent) is distinct from scope.2 (DEFINITIONAL time-threshold).
10. **FOCAL-10**: Federal LDA scoring quirks (some indicators with surprising 0 scores) warrant cross-checking against Phase A4 audit conclusions and per-country CSV directly.
11. **FOCAL-11**: α form-type split candidates from FOCAL descriptors / relationships (5 reg-form-side cells now exist; spending-report-side parallels may follow).

## Mistakes recorded

None significant. The cross-rubric grep workflow ran cleanly with 3 parallel greps (FOCAL refs across mapping docs, contact_log concepts, financials concepts). FOCAL scoring rules were already on-disk from the Phase A4 audit (no re-extraction needed). Followed locked conventions throughout (α split applied for reg/spending pair where statutorily extant; β AND-projection applied for bill_id+position contact_log.10 reuse; `unable_to_evaluate` not needed — no FOCAL item is operationally undefined unlike Opheim's catch-all).

One reasonable counter-argument I want to flag: 35 NEW rows is the most of any single mapping (HG = 22) — at risk of over-atomizing FOCAL's contact_log and descriptors batteries. The granularity-bias rule supports atomization; LobbyView's schema-coverage will validate the choices by checking if the federal LDA schema populates the FOCAL-distinctive cells. If LobbyView's schema cleanly populates the contact_log per-meeting cells (it won't — LDA is quarterly aggregate), the atomization is over-aggressive and the per-meeting cells will be uniformly NULL for US jurisdictions. But that's a known characteristic of LDA, not a flaw in the compendium row design — the cells discriminate well across the 28 FOCAL-applied countries and Phase D international extraction.

## Results

- [`results/projections/focal_2024_projection_mapping.md`](../results/projections/focal_2024_projection_mapping.md) — FOCAL 2024 projection mapping doc (957 lines; 48 atomic items × 57 distinct compendium row families; 22 reused / 35 new; 38.5% reuse — lowest single-mapping rate; includes 11 Open Issues + 3 Corrections to predecessor mappings + Promotions section for compendium 2.0 freeze planning + 2025-only Lobbyist-list documentation).

## Next Steps

1. **LobbyView 2018/2025 schema-coverage check** — final Phase B mapping. Different shape (schema-coverage, not score-projection). 46 schema fields per Kim 2018 + Kim 2025; output as `results/projections/lobbyview_schema_coverage.md`. Validation criterion: for the federal LDA jurisdiction, what fraction of LobbyView API fields can be populated from the compendium cells now in place? Target: ~100% coverage.
2. **`contributions_from_others` final promotion check.** LobbyView is the last contributing rubric. If LobbyView's federal LDA schema does NOT include third-party-contributions-received (likely — LDA contribution reporting is LD-203 OUTGOING under HLOGA), the row is single-rubric across the entire contributing set. Compendium 2.0 freeze: KEEP per Newmark-distinctive-observable rationale.
3. **After Phase B closes** (FOCAL done; LobbyView next): union of 8 score-projection mapping docs + 1 schema-coverage doc → `results/projections/disclosure_side_compendium_items_v1.tsv`. Compendium 2.0 row-freeze brainstorm (separate plan; the dedup pass uses `[cross-rubric: …]` annotations across all mappings).
4. **Phase C: code projections under TDD.** Order locked: CPI 2015 C11 first (smallest, simplest), PRI 2010 second (largest, most-studied per-item ground truth), remaining 7 in mapping order, FOCAL last (after federal-LDA jurisdiction extraction is in place).
5. **Resolve Open Issue FOCAL-1** (revolving_door.1 scope decision) at end-of-session or next-session review.
