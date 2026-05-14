# Opheim 1991 Phase B projection mapping (6th rubric)

**Date:** 2026-05-13 (pm late)
**Branch:** compendium-source-extracts

## Summary

Continued Phase B per the locked plan and the 2026-05-13 (pm) handoff. Opheim 1991 was the next rubric after Newmark 2005 shipped earlier the same afternoon. Opheim is the **earliest contributing rubric** (1988-89 vintage, published 1991) and the explicit predecessor cited by Newmark 2005 ("Similar to Opheim's (1991) measure" — Newmark 2005 paper line 117). The session walked all four watchpoints called out for Opheim in the handoff, and the mapping landed at the same 100% reuse rate as Newmark 2005: 14 of 14 distinct compendium row families touched are pre-existing, zero new rows introduced. One of Opheim's 15 in-scope atomic items (the catch-all `disclosure.other_influence_peddling_or_conflict_of_interest`) is operationally undefined in the paper and therefore un-projectable — flagged as `unable_to_evaluate` rather than zeroed.

Three structural promotions landed for the compendium 2.0 freeze planning. First, the `def_actor_class_elected_officials` / `def_actor_class_public_employees` row family is now 3-rubric-confirmed (Newmark 2017 + Newmark 2005 + Opheim). Per the handoff's explicit guidance ("three rubrics reading the same row family is high enough confidence to lock its design"), Open Issue 1 from the Newmark 2017 mapping should be pulled forward to compendium 2.0 freeze rather than indefinitely deferred. Second, the three lobbyist-status threshold cells (`compensation_threshold_*`, `expenditure_threshold_*`, `time_threshold_*`) are similarly 3-rubric-confirmed. Third, the β AND-projection pattern locked during the 2026-05-11 Sunlight session now has its second concrete application: `disclosure.legislation_supported_or_opposed` reads `lobbyist_spending_report_includes_bill_or_action_identifier AND lobbyist_spending_report_includes_position_on_bill`. Pattern is no longer "locked but applied once" — it's an established projection convention.

Two cross-rubric searches resolved against potential promotions. The Watchpoint-4 check for a `contributions_from_others` parallel in Opheim's 7-item information-category battery resolved as NO PARALLEL — Opheim's "sources of income" and "total income" structurally parallel Newmark's compensation pair, not third-party-contributions. Newmark 2017's `lobbyist_or_principal_report_includes_contributions_received_for_lobbying` row remains single-rubric within the current contributing set (CPI, PRI, Sunlight, Newmark 2005, Opheim — none confirmed parallel). The 7th category (the "other influence peddling or conflict of interest" catch-all) could plausibly cover that observable but is operationally undefined and rejected as non-deterministic. Remaining promotion checks: HG 2007, FOCAL 2024, LobbyView.

A secondary discussion landed on Opheim's Phase C utility profile. Opheim publishes per-state INDEX TOTALS only (Table 1, 47 states; MT/SD/VA missing). No sub-aggregate breakdown. With all 7 `enforce.*` items OOS plus the catch-all un-projectable, the projected partial maxes at 14/22 and the only available validation against Opheim's published numbers is a weak inequality (`our_projected_partial ≤ paper_total`). The actual quality signal is **temporal-depth validation** — Opheim's 1988-89 vintage is the earliest cross-rubric ground truth available, extending the contributing-rubric coverage to ~28 years end-to-end (1988-89 through 2015). For rows that several rubrics read across multiple vintages, this gives Phase C a strong cross-vintage stability check.

## Topics Explored

- All 15 in-scope Opheim atomic items mapped: 7 def + 1 freq + 6 information-category (1 catch-all un-projectable); 7 `enforce.*` items excluded per disclosure-only Phase B qualifier.
- Watchpoint 1: β AND-projection on `disclosure.legislation_supported_or_opposed`. Applied — reads `lobbyist_spending_report_includes_bill_or_action_identifier AND lobbyist_spending_report_includes_position_on_bill` (both pre-existing from Sunlight's α form-type split). Second concrete application of the β convention after its 2026-05-11 Sunlight locking.
- Watchpoint 2: `def_actor_class_*` row family — confirmed 3-rubric-load-bearing with Opheim added as third reader. Open Issue 1 promoted to compendium 2.0 freeze planning per handoff's explicit guidance.
- Watchpoint 3: `disclosure.frequency` reads PRI E1h/E2h cadence at finer binary cut (monthly-only). Source quote confirms: "monthly during the session or both in and out of session were coded 1; quarterly/semi-annually/annually were coded 0" (Opheim paper line 115–118). Projection reads only the 2 monthly cells of the 8-cell PRI cadence family (lobbyist + principal); tri-annual is omitted from Opheim's prose and interpreted strictly as 0. Newmark 2005 reads the same row family at the coarser >annual cut.
- Watchpoint 4: 7-item information-category battery checked for `contributions_from_others` parallel. NO PARALLEL — "sources of income" + "total income" structurally parallel Newmark's compensation pair (broken-down + total), not third-party-contributions. Catch-all (item 7) is operationally undefined and rejected as non-deterministic. Newmark 2017's distinctive row stays single-rubric in current set.
- The catch-all item `disclosure.other_influence_peddling_or_conflict_of_interest` operationally undefined per `items_Opheim.md` §7. Treated as `unable_to_evaluate`, excluded from projected partial. First contributing-rubric item with that disposition — Phase C tooling needs to support this outcome.
- Cross-rubric grep across all 10 source TSVs + historical PRI 2010 CSV BEFORE drafting per the locked 2026-05-11 workflow. Confirmed bill_id and position rows already in compendium (from Sunlight mapping's α split), confirmed no `contributions_from_others` parallel in Opheim, confirmed cadence row family is the right target for `disclosure.frequency` projection.
- Structural delta from Newmark 2005 enumerated: Opheim's enforcement section (7 items, all OOS in Phase B) is absent from Newmark 2005; Newmark 2005 adds prohibitions (4 items, also OOS) that Opheim doesn't have; Opheim has the catch-all that Newmark 2005 drops; Opheim splits bill_id+position via the `legislation_supported_or_opposed` item where Newmark 2005 reads only the coarser subject-matter row.
- Three row-family promotions identified for the compendium 2.0 freeze: (a) `def_actor_class_*` 3-rubric-confirmed → resolve Open Issue 1 at freeze; (b) the three lobbyist-status threshold cells 3-rubric-confirmed; (c) the gifts/entertainment/transport/lodging bundle now 4-rubric-confirmed (PRI + Newmark 2017 + Newmark 2005 + Opheim, plus FOCAL `financials.10` at combined granularity).

## Provisional Findings

- **Row reuse rate: 14/14 distinct row families = 100%.** Zero new compendium rows introduced. Matches Newmark 2005's headline reuse, consistent with Opheim being the explicit predecessor Newmark 2005 cites. Breakdown: 4 from CPI mapping (def_target_* + comp threshold), 4 from Sunlight mapping (subject-matter side + comp pair + categorization + bill_id + position; the bill_id/position pair was introduced by Sunlight's α split and the β AND-projection on these two cells is the second confirmed use of β), 2 from PRI mapping (gifts/entertainment principal+lobbyist pair) + 2 cells of the PRI cadence family, 3 from Newmark 2017 mapping (`def_actor_class_*` × 2 + `expenditure_threshold_*` + `time_threshold_*` + `total_expenditures`).
- **One item un-projectable.** Opheim's `disclosure.other_influence_peddling_or_conflict_of_interest` has no operational definition in the paper. First contributing-rubric item with `unable_to_evaluate` projection. Phase C harness must support this outcome (cannot default to 0; cannot project to a specific cell; explicitly excluded from partial).
- **Three row-family promotions** for compendium 2.0 freeze: `def_actor_class_*` 3-rubric-confirmed → resolve Open Issue 1 now (handoff explicit guidance); three lobbyist-status threshold cells 3-rubric-confirmed; gifts bundle 4-rubric-confirmed at combined granularity.
- **Newmark 2017's `lobbyist_or_principal_report_includes_contributions_received_for_lobbying` stays single-rubric.** No parallel found in Opheim's 7-item info-category battery. Open watchpoints: HG 2007, FOCAL 2024, LobbyView. If all three fail to confirm, the row is single-rubric in the entire contributing set and should be re-examined at compendium 2.0 freeze (is it a real observable other rubrics happened to miss, or is it Newmark-2017-specific over-atomization?).
- **β AND-projection convention is now established, not just locked.** Second concrete application after the 2026-05-11 Sunlight session. Pattern: when a source paper bundles N conceptually-distinct observables into one item, encode the bundling in the projection logic (AND/OR/derived expression) rather than re-atomizing the source. Source TSV stays unedited.
- **Opheim's Phase C utility is temporal-depth validation.** 1988-89 vintage extends contributing-rubric coverage to ~28 years (1988-89 through 2015). For BoS-sourced rows multiple rubrics read across multiple vintages, this gives Phase C a multi-decade cross-vintage stability check. Direct tolerance validation against Opheim's published totals reduces to weak inequality.

## Decisions

| topic | decision |
|---|---|
| Sixth Phase B target | Opheim 1991, completed (15 atomic items in scope; 7 OOS enforce.* items; 14 of 15 projectable) |
| Row reuse | 14 of 14 distinct row families = 100% (zero new rows) |
| Watchpoint 1 (β AND-projection on `legislation_supported_or_opposed`) | APPLIED — reads `bill_id AND position`; second confirmed use of β |
| Watchpoint 2 (`def_actor_class_*` 3rd reader) | CONFIRMED — row family now 3-rubric-load-bearing |
| Watchpoint 3 (`disclosure.frequency` finer cadence cut) | CONFIRMED — reads only PRI monthly cells (lobbyist + principal); tri-annual → 0 |
| Watchpoint 4 (`contributions_from_others` parallel) | NO PARALLEL — Newmark 2017 row stays single-rubric in current set |
| Catch-all `disclosure.other_influence_peddling_or_conflict_of_interest` | UN-PROJECTABLE; `unable_to_evaluate`; excluded from projected partial (not zeroed) |
| Open Issue 1 (`def_actor_class_*` row family) | RESOLVED — pull forward to compendium 2.0 freeze (3-rubric-confirmed; handoff guidance operative) |
| Three lobbyist-status threshold cells | 3-rubric-confirmed (compensation + expenditure + time) |
| Gifts bundle row pair | 4-rubric-confirmed at combined granularity (PRI + Newmark 2017 + Newmark 2005 + Opheim) |
| `lobbyist_spending_report_includes_total_compensation` | 4-rubric-confirmed (Sunlight + Newmark 2017 + Newmark 2005 + Opheim) — one of the most-validated rows in the compendium |
| Phase C utility of Opheim | Temporal-depth validation; weak inequality only against published totals; cross-vintage stability check on BoS-derived rows the strongest signal |
| Next target | HiredGuns 2007 (47 items, disclosure-side only; largest single remaining mapping) |

## Mistakes recorded

None significant in this session. Followed locked conventions (cross-rubric grep before drafting; α form-type split via Sunlight rows; β AND-projection on bundled items; `unable_to_evaluate` for un-projectable items).

## Results

- [`results/projections/opheim_1991_projection_mapping.md`](../results/projections/opheim_1991_projection_mapping.md) — Opheim 1991 projection mapping doc (15 atomic items in scope × 14 distinct compendium row families; 100% reuse; 1 item un-projectable; includes "Corrections to predecessor mappings" section flagging Open Issue 1 resolution + handoff remaining-rubric count decrement 4 → 3).

## Open Questions

- Should `lobbyist_or_principal_report_includes_contributions_received_for_lobbying` survive compendium 2.0 freeze if HG 2007 + FOCAL 2024 + LobbyView all also fail to confirm a parallel? The row is currently single-rubric in 5 contributing rubrics (CPI, PRI, Sunlight, Newmark 2005, Opheim); if it's still single-rubric after all 9 ship, that's evidence either of a real Newmark-2017-discovered observable other rubrics miss, or of Newmark over-atomization. Either reading is honest; user decision pending at compendium 2.0 freeze.
- Should the catch-all `disclosure.other_influence_peddling_or_conflict_of_interest` admit a multi-cell OR projection when the deferred prohibitions / enforcement round expands compendium 2.0? Specific candidate cells: contingent-compensation prohibition, cooling-off-period requirement, gift-prohibition tier, third-party-contributions disclosure. Not in scope for Phase B; flagged for the deferred-items round.
- Should the cadence row family `lobbyist_report_cadence_includes_monthly` (and the 7 other cells under it) split into session-bounded vs always-monthly cells? Opheim's source distinguishes them but collapses to one binary; PRI atomization doesn't split them; FOCAL `timeliness.*` and LobbyView may surface the need. Flagged for compendium 2.0 freeze.
- With 6 of 9 Phase B mappings done (Newmark 2017, Newmark 2005, CPI, PRI, Sunlight, Opheim) and OpenSecrets tabled, can the user authorize a parallel compendium-2.0 row-freeze brainstorm to run alongside HG/FOCAL/LobbyView mapping? Phase B's done-condition is the union of all 9 mapping docs feeding the freeze; ~67% complete is a reasonable point to start scoping the freeze plan.
