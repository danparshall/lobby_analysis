# 2026-05-13 — Phase B continued: Newmark 2017 projection mapping (4th rubric to ship)

**Date:** 2026-05-13
**Branch:** compendium-source-extracts
**Plan executed:** [`../plans/20260507_atomic_items_and_projections.md`](../plans/20260507_atomic_items_and_projections.md) Phase B (Newmark 2017 — fourth rubric to ship after CPI 2015 C11, PRI 2010, Sunlight 2015; OpenSecrets 2022 was tabled 2026-05-13).
**Handoff (most recent, with this rubric's watchpoints):** [`../plans/_handoffs/20260511_phase_b_continued_remaining_7.md`](../plans/_handoffs/20260511_phase_b_continued_remaining_7.md).
**Prior handoff:** [`../plans/_handoffs/20260507_phase_b_handoff.md`](../plans/_handoffs/20260507_phase_b_handoff.md).

## Summary

Drafted the Newmark 2017 projection mapping at [`../results/projections/newmark_2017_projection_mapping.md`](../results/projections/newmark_2017_projection_mapping.md). 14 atomic items in scope (7 def + 7 disclosure); 5 `prohib.*` items explicitly excluded per the disclosure-only Phase B qualifier. Mandatory cross-rubric grep run BEFORE drafting (8 grep calls in parallel across the 10 contributing-rubric files + 3 existing projection mapping docs); locked conventions from CPI/PRI/Sunlight (granularity bias, typed cells on `MatrixCell.value`, `[cross-rubric: …]` annotations, three-distinct-threshold-concepts discipline) applied verbatim.

**Headline result: 8 of 14 rows are reuse, 6 are new.** Reuse rate matches Sunlight's (11 of 13 cross-rubric overlapped). The single Newmark-distinctive observable surfaced this session is `lobbyist_or_principal_report_includes_contributions_received_for_lobbying` — Newmark 2017's `disclosure.contributions_from_others` doesn't have a direct cross-rubric reader in the current contributing set, though Newmark 2005's parallel item (next-up mapping) likely picks it up.

Per the locked Phase B per-item template, no surprises in the structural shape of the work. The substantive design pushback this session was on the 2026-05-11 handoff's per-rubric watchpoint for the three `def.*_standard` items (compensation / expenditure / time) — see Decisions § "Pushback on handoff watchpoint #4" below.

## Topics Explored

- All 14 in-scope Newmark 2017 atomic items mapped to compendium rows per the locked Phase B template: 2 activity-type defs (`def_target_legislative_branch`, `def_target_executive_agency` — reused from CPI mapping) + 2 actor-class defs (new row family `def_actor_class_*`) + 3 lobbyist-status threshold typed cells (compensation existing from CPI; expenditure + time NEW) + 7 disclosure items (1 reused from Sunlight subject-matter; 2 reused from Sunlight compensation; 1 reused from Sunlight categorized; 1 reused from PRI gifts-bundle as OR-projection across actor sides; 1 NEW total-expenditures; 1 NEW contributions-received).
- Cross-rubric grep across 8 concept clusters in parallel, covering all 10 contributing-rubric files (`items_*.tsv`) + historical PRI 2010 disclosure-law CSV + 3 existing projection mapping docs. The grep workflow was the procedural fix locked in the 2026-05-11 Sunlight session — applied here mandatorily before drafting any row.
- Three threshold concepts kept distinct per the locked discipline: lobbyist-status (compensation/expenditure/time → typed cells via `IS NOT NULL` projection), filing-de-minimis (PRI D1 territory; not read by Newmark 2017), itemization-de-minimis (Sunlight #3 / HG Q15 territory; not read by Newmark 2017).
- Row design question on `disclosure.expenditures_benefiting_officials` (the handoff flagged this explicitly as "important row for the FOCAL/Newmark cross-rubric stack; check whether this should be one row or split by benefit type"): resolved to keep the existing PRI bundle (gifts ∪ entertainment ∪ transport ∪ lodging × lobbyist/principal), projected as OR over the two actor-side rows. HG Q23's gifts-specific granularity flagged as a candidate split-row at compendium 2.0 freeze if HG mapping or extraction surfaces a real per-state distinguishing case.
- Two no-variation items (`def.legislative_lobbying`, `disclosure.expenditures_benefiting_officials`) — Newmark's factor-analysis exclusion is a statistical artifact, not a definitional claim. Compendium 2.0 doesn't elide rows based on observed 2015 variation; cells extracted normally; Phase C accounts for constant +2 contribution to `def.section_total` + `disclosure.section_total`.
- Validation-scope honest-framing: Newmark 2017 publishes only sub-aggregate per-state data (Table 2), not per-atomic-item per-state. Phase C against Newmark directly is 50 states × 2 sub-aggregates = 100 ground-truth cells. Per-item validation has to come from cross-rubric overlap with PRI 2010 (per-item per-state via `docs/historical/pri-2026-rescore/`) and CPI 2015 C11 (700-cell `results/cpi_2015_c11_per_state_scores.csv`). Both rubrics use BoS or direct statute as upstream, so BoS-derived Newmark items are correct-by-construction when fed from PRI/CPI cells.

## Provisional Findings

- **Reuse rate stays high (8 of 14 = 57%).** Cumulative across 4 mappings (CPI 21 rows + PRI ~52 new + Sunlight 11 cross-rubric reused / 13 total + Newmark 8 reused / 14 total), compendium-row growth is slowing as expected — first rubric (CPI) was almost entirely new rows; last 3 mappings have been increasingly reuse-dominated. This validates the projection-driven row-design approach.
- **Newmark 2017's role within the contributing set mirrors Sunlight's:** cross-rubric redundancy on the definitional-and-disclosure backbone of BoS-derived items, not novel observables. Single Newmark-distinctive row (`lobbyist_or_principal_report_includes_contributions_received_for_lobbying`) is the only candidate from this rubric for the "no other rubric reads this" category — and Newmark 2005 likely picks it up via its parallel disclosure item.
- **The `def_actor_class_*` row family is a genuinely new third row family** alongside CPI's `def_target_*` (who can be lobbied) and PRI's `actor_*` (who's required to register as a lobbying entity). Newmark and Opheim treat "elected officials as lobbyists" / "public employees as lobbyists" as definitional inclusion criteria of the lobbyist concept (do these actor classes fall under the lobbyist definition when they personally lobby). Conceptually distinct from both other families. Fragile — could be folded into one of the other two at compendium 2.0 freeze if PRI A-family content overlaps; not directly walked this session.
- **The handoff's threshold-table line "Newmark/Opheim def.*_standard" collapses three typed cells into one row entry for brevity.** Literal reading (all three Newmark items read CPI #197) is internally inconsistent: compensation / expenditure / time thresholds are independently extant in state statutes. Federal LDA itself has compensation + time thresholds but no expenditure threshold, so even one well-known regime contradicts the literal reading. Charitable reading is "follow the CPI #197 typed-cell pattern" — three separate typed cells, each read by the corresponding Newmark binary via `IS NOT NULL`.
- **Phase C validation scope for Newmark is sub-aggregate-only against Newmark's own published data.** Per-atomic-item validation requires cross-rubric overlap. Documented honestly in the mapping doc rather than smuggling per-item ground truth from indirect sources.

## Decisions

| Topic | Decision |
|---|---|
| Fourth Phase B target | Newmark 2017, completed (14 atomic items in scope; 5 prohib.* excluded) |
| Row reuse rate | 8 of 14 = 57% (5 from CPI + 2 from PRI + 1 from Sunlight at row level; doc also lists 4 additional pre-existing rows touched at compound granularity) |
| New row family `def_actor_class_*` | PROPOSED for elected-officials-as-lobbyists and public-employees-as-lobbyists. Distinct from `def_target_*` (CPI) and `actor_*` (PRI). Open Issue 1 at compendium 2.0 freeze: keep as third family, fold into actor_*, or fold into def_target_* |
| `expenditure_threshold_for_lobbyist_registration` (typed Optional[Decimal]) | PROPOSED as new typed cell parallel to CPI #197's compensation cell |
| `time_threshold_for_lobbyist_registration` (typed Optional[<TimeThreshold>]) | PROPOSED with structured value type (magnitude + unit enum) to accommodate hours-per-period / days-per-period / percent-of-work-time variants (federal LDA's 20% rule) |
| `lobbyist_spending_report_includes_total_expenditures` (binary) | PROPOSED as separate from `lobbyist_spending_report_required` per granularity bias. Empirically co-occurs with the existence-of-report cell but conceptually distinct (state could require categorized-only reporting without a total) |
| `lobbyist_or_principal_report_includes_contributions_received_for_lobbying` (binary) | PROPOSED. Newmark-distinctive observable; will be confirmed/refined by Newmark 2005 mapping. Open Issue 3: actor-split (lobbyist vs principal) deferred to compendium 2.0 freeze |
| `disclosure.expenditures_benefiting_officials` row design | RESOLVED: keep existing PRI bundle (gifts ∪ entertainment ∪ transport ∪ lodging × lobbyist/principal), projected as OR over actor sides. HG Q23 gifts-specific granularity flagged for compendium 2.0 freeze; not split now |
| Pushback on handoff watchpoint #4 | Three def.*_standard items read THREE typed cells (compensation/expenditure/time), not one. The 2026-05-11 handoff's wording "Should read the existing CPI #197 cell ... as `cell IS NOT NULL`" is shorthand for "follow the CPI #197 typed-cell pattern" — not a literal claim that all three Newmark items read the same cell. Documented as Open Issue 4 in the mapping doc |
| Phase C validation scope for Newmark | Sub-aggregate-only against Newmark's published data (50 states × `def.section_total` + 50 states × `disclosure.section_total` = 100 cells). Per-item validation via cross-rubric overlap with PRI 2010 + CPI 2015 C11. Documented honestly in mapping doc |
| Two no-variation items | Cells still extracted; Phase C accounts for constant +1 contribution from `def.legislative_lobbying` and constant +1 from `disclosure.expenditures_benefiting_officials` (likely; direction of no-variation not explicitly stated in Newmark) |
| Next Phase B target | Newmark 2005 (predecessor; 18 items; expect heavy overlap with Newmark 2017's row set) |

## Mistakes recorded

None significant. Cross-rubric grep workflow (locked 2026-05-11) ran cleanly on the first attempt; no rework cycles. One minor friction: PRI projection mapping doc exceeded the 25k-token Read limit; I switched to grep-based interrogation of the existing PRI rows rather than reading the full doc. This is the predictable consequence of PRI being the largest mapping (~860 lines per the file structure) and is independent of any process discipline.

## Results

- [`../results/projections/newmark_2017_projection_mapping.md`](../results/projections/newmark_2017_projection_mapping.md) — Newmark 2017 projection mapping doc (14 atomic items × 14 distinct compendium rows; 6 new, 8 reused; all rows annotated with `[cross-rubric: …]` overlap).

## Next Steps

1. **Newmark 2005 projection mapping** (18 items; predecessor of 2017; expect very heavy overlap with Newmark 2017's row set — Newmark 2005's 4 def items + 5 prohib + 7 disc + 1 penalty = 17 atomic items + 1 standards composite; subset/predecessor of Newmark 2017). Should be fast given Newmark 2017 is now mapped and most rows are pre-existing. Verify which Newmark 2017 row is NOT in Newmark 2005 (likely fewer threshold concepts — paper 2005 enumerated only "compensation standard"; 2017 explicitly enumerates compensation + expenditure + time).
2. **Opheim 1991 mapping** (22 items disclosure-side only; applies β AND-projection for `disclosure.legislation_supported_or_opposed`; introduces in-session/out-of-session cadence row family per the OpenSecrets-tabling note in `_tabled/opensecrets_2022_tabled.md`).
3. **HiredGuns 2007 mapping** (47 items, the largest remaining; applies α form-type split heavily; reads CPI #197 / Sunlight #3 / Newmark threshold cells at finer ordinal granularities).
4. **FOCAL 2024 mapping** (50 items; weighted aggregation, US federal LDA validation anchor at 81/182 = 45%).
5. **LobbyView schema-coverage check** (different shape; tackled last; produces `lobbyview_schema_coverage.md` rather than a score-projection).
6. After Phase B completes for all 6 remaining rubrics: union of compendium rows across all 9 mappings → `results/projections/disclosure_side_compendium_items_v1.tsv` → compendium 2.0 row-freeze brainstorm (separate plan; resolves the 4 Open Issues from this session + open issues from prior mappings).
7. **Open Issue 4 (handoff threshold pushback) needs design-team disposition.** Either (a) the handoff is corrected to explicitly call out three separate typed cells per the cross-rubric grep evidence, or (b) my reading is wrong and there's a structural argument I'm missing for collapsing the three threshold concepts onto one cell. Worth a 5-minute check at the next session start; current mapping doc assumes (a).

## Open Questions

- Does PRI A6 or another PRI A-family item overlap with the proposed `def_actor_class_elected_officials` row? Not walked directly this session — would tighten Open Issue 1.
- Does Newmark 2005 enumerate all three threshold concepts (compensation + expenditure + time) or only compensation? Paper-line evidence in the items_Newmark2005.tsv extract is ambiguous; will resolve during Newmark 2005 mapping.
- Is the actor-split for `lobbyist_or_principal_report_includes_contributions_received_for_lobbying` needed? Newmark doesn't specify actor side; granularity-bias says split; no other rubric currently reads this row at any granularity. Defer to compendium 2.0 freeze.
