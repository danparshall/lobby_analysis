# Sub-1 Stream 1 plans: Sunlight 2015 + Opheim 1991

**Date:** 2026-05-14
**Branch:** phase-c-projection-tdd
**Predecessor convo:** [`20260514_rubric_plans_drafting.md`](20260514_rubric_plans_drafting.md) (Sub-0 of 5 — playbook gap audit + data-year audit)
**Sub-session 1 of 5** in the multi-sub-session structure laid out by Sub-0.

## Summary

Drafted the two Stream 1 plans (Sunlight 2015 rubric #3, Opheim 1991 rubric #6) per the Sub-0 charter, in the locked intra-stream order (Sunlight first because its α form-type split introduces the 6 bill_id/position cells that Opheim's β AND-projection reads). Both plans are self-contained per the write-a-plan skill, carry STOP clauses for spec-doc-vs-v2 drift, and bake in the 7 conventions Sub-0's gap audit surfaced (scope qualifier, validation regime, data year section, `unable_to_evaluate` discipline, row-promotion delta hook, spec-doc-vs-v2 cross-check as Phase 0, helper return-signature contract).

A Phase-0-style cross-check run against `load_v2_compendium()` surfaced **5 spec-doc-vs-v2 row-name renames** total — 1 in Sunlight's row set (`_by_client` → `_by_payer`) and 4 in Opheim's (`*_report_*` → `*_spending_report_*` for the cadence + gifts pairs, the same family PRI 2010 caught). All under the 10% STOP threshold; both plans carry rename mapping tables inline so the implementing agent doesn't rediscover them. The cross-check also confirmed the rest of the expected rows (12 for Sunlight, 13 for Opheim) exist in v2 exactly as the spec docs name them.

A user-raised question about whether the broader naming taxonomy was documented led to the discovery that the **specific** renames are documented (`20260513_row_freeze_decisions.md` D3 is canonical), but the **broader prefix-family taxonomy** (`def_target_*`, `def_actor_class_*`, `actor_*`, `lobbyist_reg_form_*`, `lobbyist_spending_report_*`, etc.) is **not** — it lives implicitly across multiple docs. Captured as **GH issue #9** for a dedicated docs-overhaul branch; user's intent is to run that off main first, merge to main, then pull main into the consumer branches so Stream 2/3/4 plans can reference the taxonomy doc instead of inlining their own rename tables. Confirmed via `git diff --stat origin/main -- compendium/` that `phase-c-projection-tdd` has NOT touched `compendium/` (empty diff), so off-main → merge-back → merge-forward works cleanly.

## Topics Explored

- **Pre-flight reads:** STATUS.md, README.md, RESEARCH_LOG.md, Sub-0's three artifacts (rubric_plans_drafting convo, playbook gap audit, rubric data years), the rubric implementation playbook, the headless-API-key handoff doc, and both target rubrics' projection mapping docs (Sunlight 2015 spec at 217 lines, Opheim 1991 spec at 424 lines).
- **API-key billing confirmation.** User on Dans-MacBook-Pro (desktop), `/status` confirmed API-key billing. The handoff doc's "Where the key lives on the user's machines" section was complete and accurate.
- **Phase-0 cross-check executed.** Ran `load_v2_compendium()` against the 13 expected Sunlight rows + 17 expected Opheim rows. Surfaced 5 renames (all v1-style `_report_*` or `_by_client` carry-overs); each is below the 10% STOP threshold; both plans bake the rename tables inline.
- **Plan drafting — Sunlight 2015** (rubric #3). Scope qualifier: item 4 EXCLUDED per 2026-05-07 audit (`Total` and `Grade` unreproducible — per-item validation only). Validation regime: Strong (50 × 4 = 200 ground-truth cells in `papers/Sunlight_2015__...csv`). Architecture: function-per-item dispatcher (all 4 in-scope items have bespoke compound logic — nested-tier tables, OR projections, signed-tier typed-cell read). API contract bakes in no-`Total`/no-`Grade` regression-guard tests. Data year: MEDIUM-LOW; Phase-0 paper methodology re-read flagged.
- **Plan drafting — Opheim 1991** (rubric #6). Scope qualifier: 7 `enforce.*` items OUT + 1 catch-all un-projectable = max reproducible partial 14/22. Validation regime: Weak-inequality only (Opheim publishes per-state TOTALS only — no sub-aggregates, no per-item). 47-state sample (MT/SD/VA missing) enforced via `ValueError`. Architecture: declarative `_ATOMIC_SPEC` table mirroring PRI 2010 + 3 named helpers (cadence-OR, gifts-OR, β AND). Cross-rubric continuity test pins the bill_id+position row-name invariant between Stream 1's two plans. Data year: HIGH (paper-explicit 1988-89). No CSV exists for Opheim Table 1 — Phase-0 task extracts to a paper-derived CSV.
- **Token-prefix conventions audit.** User question prompted a search across `compendium/README.md`, `20260513_row_freeze_decisions.md`, the row-freeze brainstorm convo, the playbook, and per-rubric mapping docs. Found D3 (and D1, D2, D6) but no canonical taxonomy reference. Surfaced gap; user proposed docs-overhaul on its own branch off main.
- **Branching analysis for the docs overhaul.** Verified `phase-c-projection-tdd` is read-only on `compendium/` via `git diff --stat origin/main -- compendium/` (empty). Concluded: docs-overhaul can land cleanly off main; both compendium-consumer branches (`phase-c-projection-tdd`, `extraction-harness-brainstorm`) pull main forward afterward. Flagged that `extraction-harness-brainstorm` should be checked for compendium-contract edits before the overhaul launches (it owns v2 Pydantic model rewrite).

## Provisional Findings

- **Spec-doc-vs-v2 drift is a recurring failure mode for Phase B → Phase C handoff.** PRI 2010 caught it; Sunlight + Opheim caught it again (in the same `*_report_*` family); Stream 2/3/4 will likely catch it too. The systemic fix is GH #9 (per-row provenance + prefix taxonomy doc). The per-plan workaround (rename mapping table inline) is sufficient but adds friction per plan.
- **Both Stream 1 plans are self-contained but Stream-1-internally coupled.** Sunlight must land before Opheim's implementation runs (else Opheim's cross-rubric continuity test fails at import). Sub-4's headless launch script needs to enforce this. Flagged as Open Question in the Opheim plan.
- **The `unable_to_evaluate` convention is now exercised concretely across both Sub-1 plans** — Sunlight uses it for missing input cells; Opheim uses it for both missing cells and the operationally-undefined catch-all. Per Sub-0 gap audit Pattern 3, this is the canonical disclosure-only-Phase-B treatment; future rubric plans should adopt verbatim.
- **β AND-projection now has its second exemplification.** First was Sunlight item 1's bill_id+position row-introduction (locked 2026-05-11 in archived `compendium-source-extracts`). Second is Opheim's `disclosure.legislation_supported_or_opposed` reading those same cells via AND. Pattern is now empirically demonstrated, not just hypothesized.
- **The `*_spending_report_*` rename family is documented at D3 in the row-freeze decisions doc** but the broader prefix taxonomy (what `def_target_*`, `def_actor_class_*`, `actor_*`, `lobbyist_reg_form_*`, `lobbyist_spending_report_*`, `principal_spending_report_*` each mean as families) is NOT. GH #9 will fix this.
- **`phase-c-projection-tdd` is read-only on `compendium/`.** This is structurally true (Phase C consumes the v2 contract; doesn't modify it) and was empirically verified by `git diff --stat origin/main -- compendium/`. Implication: the docs-overhaul branch can land off main without conflict; Phase C pulls forward when convenient.

## Decisions Made

- **Sub-1's two plan deliverables are committed-ready.** Both follow the write-a-plan skill conventions, both reference their originating Sub-0 convo, both carry the 7 Sub-0 conventions, both have Phase-0 cross-checks specified inline.
- **GH #9 ("Document compendium row-naming taxonomy; trace every name to source")** is opened with the `task` label. Issue body recommends a fresh branch off main, points to D1-D3 + Sections 1, 5-6 of `20260513_row_freeze_decisions.md` as starting material, flags `extraction-harness-brainstorm` for a pre-launch overlap check.
- **Sub-2 (Newmark 2017 + Newmark 2005) should wait on GH #9 to merge.** Newmark 2017 introduces 6 new rows; their naming would benefit from the taxonomy doc landing first. Sub-1's plans are self-contained and don't need to wait. Surfaced for the user to decide when to launch Sub-2.
- **Back-link on this convo** captures GH #9 via the `## Captured Tasks` section at the end of Sub-0's convo file (since this convo file is being created later in finish-convo; the back-link lives on Sub-0's file per the capture-task skill's "most recent convo" detection at the moment of capture). The link's intent is preserved.

## Results

The Sub-1 deliverables are plan docs (in `plans/`), not analysis results, so no entries in `results/`. Plan paths:

- [`../plans/20260514_sunlight_2015_plan.md`](../plans/20260514_sunlight_2015_plan.md) — 399 lines. Function-per-item dispatcher; 4 in-scope items; Strong validation regime; no-Total/no-Grade regression-guard tests; data-year confidence-lift task in Phase 0.
- [`../plans/20260514_opheim_1991_plan.md`](../plans/20260514_opheim_1991_plan.md) — 491 lines. Declarative `_ATOMIC_SPEC` table + 3 named helpers; 14 effective in-scope items + 1 un-projectable catch-all; Weak-inequality validation regime; 47-state sample enforced via `ValueError`; β AND-projection cross-rubric continuity test imports `project_sunlight_item1`.

GitHub issue:

- [danparshall/lobby_analysis#9](https://github.com/danparshall/lobby_analysis/issues/9) — Document compendium row-naming taxonomy; trace every name to source.

## Open Questions

- **Sunlight oddity-flag return shape** (Question 2 in Sunlight plan): `(int, oddity_flag)` tuple from each helper vs. bucketing oddities into `unable_to_evaluate`. Open for the implementing agent to pick after one truth-table iteration; documented in module docstring either way.
- **Opheim Table 1 CSV destination** (Question 1 in Opheim plan): `papers/Opheim_1991__state_lobby_regulation_table1.csv` (tracked, recommended) vs `data/opheim_1991_index_totals.csv` (untracked). Confirm before implementation.
- **MT/SD/VA refusal vs sentinel** (Question 4 in Opheim plan): plan picks `ValueError`. Confirm before implementation.
- **Sub-4 launch-ordering enforcement.** Sub-1 plans require Sunlight to land before Opheim; Sub-4's headless launch script needs to encode this. Surfaced for Sub-4 drafting.
- **`_is_not_null` helper survival** (Question 3 in Opheim plan): did PRI 2010's session leave a reusable helper, or does the implementing agent need to write one?
- **`TimeThreshold` cell access pattern.** v2 loader returns raw strings; `lobbyist_registration_threshold_time_percent` carries a structured value. Opheim only needs `IS NOT NULL` so non-empty-string check works; if Track B (`extraction-harness-brainstorm`) ships typed models, the helper migrates without logic change. Documented in plan.
- **Sub-2 launch timing.** Recommended to wait on GH #9 to merge. User's call.

## Captured Tasks

- [#9: Document compendium row-naming taxonomy; trace every name to source](https://github.com/danparshall/lobby_analysis/issues/9) — captured 2026-05-14 during this session (cross-listed on Sub-0's convo file per capture-task's at-capture detection of most-recent convo).

## Session token cost

This sub-session ran on `ANTHROPIC_API_KEY` (work-project budget) per the multi-sub-session structure Sub-0 designed. Verified via `/status` at session start.

## Next steps

**Sub-2 (Stream 2 plans — Newmark 2017 + Newmark 2005)** is next in the structure. Recommendation: defer until GH #9 merges so the naming taxonomy doc is available; Newmark 2017 introduces 6 new rows that would benefit from prefix-choice guidance. User's call on timing.

**Sub-1's deliverables** are ready for the headless implementation runs (Sub-5+), but the launch infrastructure itself is Sub-4's job. The plans note Sub-4 dependencies inline (launch-ordering enforcement; oddity-flag policy confirmation; `_is_not_null` helper status; CSV destination confirmation).

If a parallel `compendium-naming-docs` branch is launched (per the user's plan for GH #9), `phase-c-projection-tdd` will need to pull main forward after that branch merges. The merge is expected to be clean (this branch is read-only on `compendium/`).
