# Newmark 2005 Phase B projection mapping (5th rubric)

**Date:** 2026-05-13
**Branch:** compendium-source-extracts

## Summary

Continued Phase B per the locked plan and the 2026-05-13 (afternoon) handoff. Newmark 2005 was the next rubric after Newmark 2017 shipped earlier the same day, with the user expecting ≥90% row reuse off the 2017 mapping. Actual reuse landed at 100% (14/14 in-scope rows reused, zero new rows introduced) — exceeding the handoff's expectation. The session walked all three watchpoints called out for Newmark 2005 in the handoff (PRI A-family overlap check on `def_actor_class_*`, three-threshold-cell verification against the 2005 paper text, `penalty_stringency_2003` exclusion).

The principal structural finding was the 6-vs-7 disclosure-item delta between Newmark 2005 and Newmark 2017: the 2017 paper adds a `disc.contributions_from_others` item that 2005 doesn't have. The Newmark 2017 mapping had speculated a 2005 parallel would confirm `lobbyist_or_principal_report_includes_contributions_received_for_lobbying` as a cross-rubric row — this is falsified. The row remains Newmark-2017-distinctive within the current contributing-rubric set. The 2005-vs-2017 also has a 2005-distinctive structural delta: 2005 has a standalone `freq_reporting_more_than_annual` item that 2017 omits, which projects from the existing PRI E1h/E2h cadence row family via an 8-cell OR-projection (no new rows needed). The user noted in mid-session that PRI's institutional-actor tracking (`actor_*` family from A1–A11) is itself valuable for the SMR regardless of overlap with Newmark's `def_actor_class_*` — this is consistent with the mapping's existing treatment (both row families remain distinct and both are already in the compendium plan).

A secondary discussion landed on Newmark 2005's Phase C utility being structurally weaker than Newmark 2017's: the 2005 paper publishes only per-state main-index totals in Table 1, not sub-aggregate breakdowns. With prohibitions + penalty out of scope under the disclosure-only Phase B qualifier, direct tolerance validation against Newmark 2005's published numbers reduces to a weak inequality (`our_projected_partial ≤ paper_total`). The actual quality signal from Newmark 2005 is temporal-coverage validation across six panels (1990–91, 1994–95, 1996–97, 2000–01, 2002, 2003) — the only multi-vintage ground truth in the current contributing-rubric set, useful for confirming that BoS-sourced cells are extracted consistently across vintages.

## Topics Explored

- All 14 in-scope Newmark 2005 atomic items mapped: 7 def + 1 freq + 6 disclosure (4 `prohib.*` + 1 `penalty_stringency_2003` excluded per disclosure-only Phase B qualifier).
- Watchpoint 1: PRI A-family overlap check on `def_actor_class_elected_officials` / `def_actor_class_public_employees`. Resolved negatively — PRI A1–A11 are structural/institutional-actor observables, distinct from Newmark's individual-actor-class observable.
- Watchpoint 2: three-threshold-cell verification against 2005 paper text (lines 120–121). Confirmed — 2005 enumerates compensation + expenditure + time as three separate definitional components, identical to 2017.
- Watchpoint 3: `penalty_stringency_2003` exclusion. Documented in the mapping doc's "Scope qualifier — 5 items OUT" table.
- 6-vs-7 disclosure-item delta between Newmark 2005 and Newmark 2017 surfaced. 2005 doesn't have `disc.contributions_from_others`; 2005 does have a standalone `freq_reporting_more_than_annual` item that 2017 omits.
- Per-state per-indicator data inventory for Newmark 2005. Paper Table 1 publishes per-state main-index totals across 6 panels (1990–91, 1994–95, 1996–97, 2000–01, 2002, 2003). Sub-aggregate breakdowns NOT published — weaker than Newmark 2017's Table 2.
- Cross-rubric annotation discipline applied to all 14 in-scope rows.
- User confirmation that PRI A-family institutional-actor tracking is itself valuable for the SMR. Already operationalized in the compendium via the PRI mapping's 11 `actor_*` rows.

## Provisional Findings

- **Row reuse rate: 14/14 = 100%.** Zero new compendium rows introduced. Exceeds the handoff's ≥90% expectation. Breakdown: 4 rows from CPI mapping (`def_target_*`, `compensation_threshold_*`), 4 from Sunlight mapping (subject-matter + compensation pair + categorization), 2 from PRI mapping (gifts/entertainment principal+lobbyist pair) + 1 from PRI cadence family (8-cell OR-projection), 4 from Newmark 2017 mapping (`def_actor_class_*` × 2 + `expenditure_threshold_*` + `time_threshold_*` + `lobbyist_spending_report_includes_total_expenditures`). NOTE: counting the cadence family as one family read here; the 8 cells underneath are themselves pre-existing.
- **The Newmark 2017 mapping's `disc.contributions_from_others` parallel speculation is falsified.** Newmark 2005 has only 6 disclosure items, not 7. The row `lobbyist_or_principal_report_includes_contributions_received_for_lobbying` remains Newmark-2017-distinctive within the current contributing-rubric set. Confirmed pending against HG, FOCAL, OpenSecrets (tabled), LobbyView.
- **Newmark 2005's Phase C validation utility is structurally weaker than Newmark 2017's.** Paper publishes per-state totals only, no sub-aggregate breakdown. With disclosure-only scope (`prohib.*` + penalty excluded), direct tolerance validation reduces to a weak inequality. Cross-rubric validation via PRI 2010 per-item + CPI 2015 C11 per-item remains the actual quality signal.
- **Multi-vintage stability is real but bounded.** Newmark's own 1990–91 vs 2003 correlation = 0.46 (p < 0.01). The BoS-sourced observables are non-stationary over a 13-year window — meaningful drift, not regime change. Confirms the project's "multi-year reliability" success criterion is the right framing.
- **The `def_actor_class_*` row family is now 3-rubric-confirmed** (Newmark 2005 + Newmark 2017 + Opheim, pending Opheim mapping). Open Issue 1 from the Newmark 2017 mapping is increasingly load-bearing; merits explicit resolution at compendium 2.0 freeze.

## Decisions

| topic | decision |
|---|---|
| Fifth Phase B target | Newmark 2005, completed (14 atomic items in scope; 5 items out of scope) |
| Row reuse | 14 of 14 = 100% (zero new rows) |
| Watchpoint 1 (PRI A-family overlap) | NO OVERLAP — institutional-actor vs individual-actor-class are distinct observables |
| Watchpoint 2 (three thresholds) | CONFIRMED in 2005 paper text lines 120–121; reuses Newmark 2017's three typed cells via IS NOT NULL |
| Watchpoint 3 (penalty_stringency_2003) | EXCLUDED per disclosure-only Phase B qualifier (enforcement-side, opaque rubric, 2003-only, 3 states missing) |
| `freq_reporting_more_than_annual` projection | OR over 8 PRI cadence cells (lobbyist + principal × {monthly, quarterly, triannual, semiannual}); no new compendium rows |
| Newmark 2017 speculation on 2005 contributions parallel | FALSIFIED — 2005 has 6 disclosure items, no contributions item |
| Phase C utility of Newmark 2005 | Temporal-coverage validation (6 panels, 1990–2003) rather than direct tolerance check; weak inequality only against published totals |
| Open Issue 1 status | Now load-bearing — explicit resolution required at compendium 2.0 freeze |
| PRI A-family value | Confirmed (user note) — institutional-actor tracking belongs in the compendium regardless of overlap with `def_actor_class_*`; already done via the PRI projection mapping |
| Next target | Opheim 1991 (next in Phase B order after Newmark 2005) |

## Mistakes recorded

- Initially named the convo file `_projection_mapping` in the mapping doc's link before the docs checkpoint surfaced the established `_phase_b_mapping` convention from prior sessions. Caught at docs-update time and corrected.

## Results

- [`results/projections/newmark_2005_projection_mapping.md`](../results/projections/newmark_2005_projection_mapping.md) — Newmark 2005 projection mapping doc (14 atomic items × 14 distinct compendium row families; all reused, zero new; all rows annotated with `[cross-rubric: …]`; includes "Corrections to predecessor mappings" section flagging the Newmark 2017 speculation falsification and the handoff remaining-rubric count decrement).

## Open Questions

- When (if ever) should `lobbyist_or_principal_report_includes_contributions_received_for_lobbying` split into `lobbyist_*` + `principal_*` parallel rows per the granularity-bias convention? Currently bundled; same Open Issue 3 from Newmark 2017 mapping.
- Should the `def_actor_class_*` row family resolution be deferred until Opheim 1991 mapping ships (which will be the third confirmed reader), or pulled forward to compendium 2.0 freeze planning? The Newmark 2005 mapping argues for the latter — the family is now 3-rubric-load-bearing if Opheim confirms, which is high enough confidence to lock its design.
- Newmark 2005 endnote 5 anomaly: which of the seven definition components was "constant across states" in 2003? Most likely candidate is `def_legislative_lobbying` (consistent with Newmark 2017 paper line 518 explicitly noting universal coverage), but unverifiable from the 2005 paper alone. Doesn't affect projection design — cell is extracted normally — but may matter for Phase C reproducibility of the Cronbach's α diagnostic.
- Once Opheim 1991 mapping ships, can the user authorize a compendium-2.0 row-freeze brainstorm? Phase B was scoped to deliver the union of mapping docs as input to that freeze; with 5 of 6 Phase B mappings done, the freeze planning is starting to be unblocked.
