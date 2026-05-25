# Sub-3 FOCAL plan-set + HG 2007 plan drafting

**Date:** 2026-05-18
**Branch:** phase-c-projection-tdd
**Predecessor convos:** [`20260514_rubric_plans_drafting.md`](20260514_rubric_plans_drafting.md) (Sub-0 — playbook gap audit + data-year audit), [`20260514_sub_1_sunlight_opheim_plans.md`](20260514_sub_1_sunlight_opheim_plans.md) (Sub-1 — Stream 1 plans), [`20260518_newmark_plans_drafting.md`](20260518_newmark_plans_drafting.md) (Sub-2 — Stream 2 plans).
**Sub-session 3 of 5** in the multi-sub-session structure laid out by Sub-0.

## Context reconstruction

This session started from a fresh-context handoff: the prior agent's last message described what Sub-3 and Sub-4 would each do, but didn't say which I was picking up. Reconstructed state from git log (`cacb65b` = Sub-2 committed and pushed), Sub-2's convo, RESEARCH_LOG, and the FOCAL + HG spec docs in `docs/historical/compendium-source-extracts/results/projections/`. User confirmed: Sub-3 (FOCAL plan-set + HG plan with retrieval gate).

## Summary

Drafted the **5 plans** that constitute Sub-3's deliverable — the 4-plan FOCAL set (per Sub-0's structural recommendation) + the standalone HG 2007 plan with retrieval-gate dual-path validation:

1. **`20260518_hg_2007_plan.md`** — HG rubric #7 (~500 lines). 38 in-scope items (Q1-Q38; 10 OUT per disclosure-only Phase B). Declarative `_ATOMIC_SPEC` dispatcher with 9 named helpers for non-passthrough items. **Dual-path validation:** Path A (Strong, 1,900-cell ground truth if CPI's 2007 scorecard retrievable) vs Path B (Weak-inequality `our_partial ≤ published_total - 17` if not). Cross-rubric overlap with 22 of 38 items reusing existing v2 rows. Q12 cadence-derived projection from PRI cadence binaries; Q15+Q16-Q19 itemization conditional cascade; Q23/Q24 partial-scope projection (under-scoring by design).
2. **`20260518_focal_2024_legal_core_plan.md`** — FOCAL plan 1 of 4 (~470 lines). Introduces the `focal_2024.py` module skeleton + score model + `_ATOMIC_SPEC` dispatcher dict. 26 in-scope legal-axis items (scope 4 + descriptors 6 + relationships 4+1 + revolving_door 1 + financials 11). 5 named helpers for compound items (scope.1, scope.2 with calibration cutoffs, scope.3 with v2 staff split, scope.4, financials.6, financials.10). **Validation regime:** Strong on Federal US LDA (81/180 = 45% exact-match target); Cross-rubric only on US states (no per-state US ground truth).
3. **`20260518_focal_2024_contact_log_plan.md`** — FOCAL plan 2 of 4 (~320 lines). 11 contact_log items (9 NEW v2 rows; FOCAL's most-distinctive battery). Mostly binary reads via the dispatcher's `is_not_null` / `or_any` generic helpers. Documented systematic over-scoring (~10 raw points on Federal US LDA contact_log subtotal from partly-tier collapse).
4. **`20260518_focal_2024_openness_timeliness_plan.md`** — FOCAL plan 3 of 4 (~390 lines). 12 items: openness battery (9) + timeliness battery (3, with 2025 merge of timeliness.1+.2). First FOCAL battery to read practical-axis cells. 4 named helpers (openness.3 4-AND, openness.8 2-AND, openness.5 typed-int 3-tier, cadence 3-tier for timeliness.1/.2/.3). One operationally-readable partly tier (openness.6 set-typed) kept at 3-tier; the rest YAGNI-collapsed to binary.
5. **`20260518_focal_2024_aggregation_plan.md`** — FOCAL plan 4 of 4 (~510 lines). Top-level `project_focal_2024(cells, jurisdiction, vintage)` + weighted-sum aggregation + Federal US LDA validation harness + ranking. Tolerance budgeting per battery (e.g., contact_log ±12 raw, openness ±4). Cross-rubric overlap harness extension for 10 shared rows across the 7 other Phase C modules.

**Total deliverable:** 5 plans, ~2,190 lines of structured plan text. All self-contained per the write-a-plan skill, all carrying STOP clauses for spec-doc-vs-v2 drift, all baking in the 7 Sub-0 conventions, all with Phase 0 cross-checks specified inline.

A Phase-0-style cross-check executed via `load_v2_compendium()` surfaced **23 spec-doc-vs-v2 row-name renames total** — 9 for HG, 17 for FOCAL (most inherit from Sub-1 and Sub-2 rename families). All resolved cleanly; rename mapping tables baked into each plan inline. Notable v2-vs-spec-doc structural deltas:

- **scope.3 staff cell SPLIT in v2** into `def_target_legislative_staff` + `def_target_executive_staff` (spec doc had single `def_target_legislative_or_executive_staff`). FOCAL legal-core plan handles via strict-AND projection (Open Q-2).
- **scope.1 + scope.4 set-typed cells** named differently in v2 (`def_lobbyist_actor_types`, `def_lobbying_activity_types`) than spec doc proposed (`lobbyist_definition_included_actor_types`).
- **`lobbyist_disclosure_includes_*` form-agnostic cells** chose reg-form-side in v2 (`lobbyist_reg_form_includes_*`). HG Q10 / Q22 form-flexibility relaxation handled via documentation in module docstring (Open Q-2 in HG plan).
- **`principal_report_includes_direct_compensation` → `principal_spending_report_includes_compensation_paid_to_lobbyists`** (semantic clarification + Sub-1 rename family).

## Topics Explored

- **Pre-flight:** Reconstructed Phase C state from `cacb65b` HEAD; confirmed Sub-2 Newmark plans (2017 + 2005) shipped; confirmed branch is clean and up-to-date with origin. Read Sub-0's playbook gap audit convo + Sub-1's convo for drafting conventions (7 baked-in conventions: scope qualifier, `unable_to_evaluate`, validation regime declaration, row-promotion delta hook, spec-doc-vs-v2 cross-check as Phase 0, per-item helper return signature, function-per-item vs declarative table per-rubric).
- **Read the rubric implementation playbook + the FOCAL (938 lines) and HG (815 lines) spec docs end-to-end** for source quotes, per-item logic, axis assignments, and Open Issues. FOCAL has 11 Open Issues (FOCAL-1 through FOCAL-11; FOCAL-1 resolved 2026-05-13 with `revolving_door.1` IN scope per user); HG has 10 Open Issues + 3 mapping corrections + the per-state scorecard retrieval gate.
- **Phase 0 cross-check executed.** Wrote a 130-line Python script (`/tmp/phase_0_focal_hg.py`) running `load_v2_compendium()` against the 59 expected FOCAL rows + 49 expected HG rows + 6 PRI cadence binaries (Q12 input). Surfaced 23 renames; resolved all via TSV verification (`grep` on `compendium/disclosure_side_compendium_items_v2.tsv`). All 23 resolved cleanly; rename tables baked inline in each plan.
- **HG retrieval-gate decision** — Sub-0 had documented that HG's per-state scorecard retrieval is **NOT a Track A task** (Track A handles OH multi-vintage statute retrieval). The HG plan specifies dual validation paths (Path A: Strong, requires retrieval; Path B: Weak-inequality, requires only per-state composite totals) with a launch-time environment variable `HG_GROUND_TRUTH_PATH` for path selection. Recommendation: attempt retrieval from Wayback Machine before starting HG implementation.
- **FOCAL plan-split decision** — followed Sub-0's recommendation of 3-4 sub-plans; chose 4. The split is by battery/concern boundary (legal core / contact log / openness+timeliness / aggregation), all converging on a SINGLE `focal_2024.py` module via additions to a shared `_ATOMIC_SPEC` dispatcher dict. **Sub-4 launcher must enforce intra-FOCAL ordering** (legal core → contact log → openness+timeliness → aggregation); each subsequent plan inherits the module skeleton + must not redefine the score model.
- **scope.2 calibration cutoff** — flagged as a Phase C decision by Sub-0; provisional defaults `LOW_DOLLAR_CUTOFF = $1000`, `LOW_TIME_CUTOFF = 5%`. Federal US LDA's threshold ($3000 + 20%) is "significant" under these cutoffs, matching published US scope.2 = 0. Plan ships with these defaults; implementing agent verifies on the Federal US LDA validation run.
- **Partly-tier collapse documentation** — FOCAL's 3-tier per-indicator scoring (0=no, 1=partly, 2=yes) has many partly-tier sub-criteria that aren't extractable from v2 binary cells (data-quality observables like "some entries incomplete", "vague or unclear", "general list not specific to the communication"). YAGNI: collapse to binary (TRUE → 2; FALSE → 0). **Federal US LDA validation tolerance accommodates the systematic over-scoring** per battery (contact_log ±12, openness ±4, descriptors ±4, etc.). Total tolerance ~±15 raw points on the 81-target.
- **2024 vs 2025 vintage handling** — L-N 2025 merged timeliness.1 + timeliness.2 into one indicator + added "Lobbyist list" to relationships. Spec encoded via `min_vintage` / `max_vintage` per `_ATOMIC_SPEC` entry; dispatcher filters items based on `current_vintage`. For 2024 vintage: 49 in-scope indicators (50 - revolving_door.2); for 2025: 50 in-scope (49 + lobbyist_list_2025).

## Provisional Findings

- **FOCAL's partly-tier sub-criteria are mostly not operationally extractable from v2 binary cells.** Of FOCAL's 49 in-scope indicators, ~20 have partly-tier sub-criteria; only 1 (openness.6 "only business IDs") reads cleanly from v2 typed cells. The remaining ~19 partly tiers collapse to binary (TRUE → 2 instead of 1; FALSE → 0). **Documented as a systematic over-scoring on Federal US LDA validation**; tolerance budgeted per battery in the aggregation plan. Compendium 2.0 freeze decision: invest in partly-tier extraction (~10 new typed cells across batteries) only if Phase D extraction surfaces meaningful state variation on partly tiers.
- **scope.3 v2 staff split is a meaningful structural change from the spec doc.** v2 split `def_target_legislative_or_executive_staff` into 2 cells (`_legislative_staff` + `_executive_staff`). FOCAL plan handles via strict-AND read (both must be TRUE for `staff_in_scope`). Federal US LDA validation will surface whether the strict reading aligns with L-N 2025's coding (Open Q-2 in legal-core plan).
- **HG retrieval gate creates a real branching workflow** for Sub-5+ implementation. Path A (per-state per-item scorecard from CPI archives) gives 1,900-cell ground truth; Path B (composite totals only) gives 50 weak-inequality checks. The plan's dual-path-aware tests share the same per-item helpers but differ in aggregation-test assertions. **Launch infrastructure (Sub-4) must run the retrieval attempt first** and pass the path selection to the implementing agent's environment.
- **Cross-rubric overlap promotion at FOCAL landing.** After FOCAL ships, the most-validated row `lobbyist_spending_report_includes_total_compensation` reaches **8-module-confirmed** at the projection layer (was 7 after HG; Opheim is blocked). This unlocks the Phase 4 cross-rubric agreement audit on a meaningful overlap sample. Three other rows reach 5+ rubric-confirmed: `_compensation_broken_down_by_payer`, the gifts bundle, `_bill_or_action_identifier` α-split pair.
- **Set-typed cells (scope.1, scope.4, financials.3, openness.6, openness.7) are the cleanest example of the "typed cell, multiple projection granularities" pattern in FOCAL.** Same v2 cell, different rubric reads: openness.6 reads at 3-tier (full set vs business-ID-only vs empty); scope.1 reads at 3-tier (full 9-actor set vs prof_consultant + others vs prof_consultant only); financials.3 reads at binary `IS NOT NULL`. The cell carries the typed value; projections apply rubric-specific reads.
- **No shared helpers between FOCAL and HG.** Unlike Stream 2 (Newmark 2017's `project_gifts_actor_agnostic_or` shared with Newmark 2005), Stream 3 has no intra-stream helper sharing. FOCAL optionally imports `project_gifts_actor_agnostic_or` from `newmark_2017` for financials.10 if Newmark 2017 has shipped; otherwise inlines the OR.

## Decisions Made

- **Sub-3's 5 plans are committed-ready as-is.** Self-contained per write-a-plan; carry the 7 Sub-0 conventions; STOP clauses for spec-doc-vs-v2 drift; Phase-0 cross-checks specified inline; rename mapping tables baked in. All open questions surfaced to the implementing agent's pre-launch decisions.
- **4-plan FOCAL split** at the battery/concern boundary (legal core / contact log / openness+timeliness / aggregation). All 4 plans converge on a SINGLE `focal_2024.py` module via additions to a shared `_ATOMIC_SPEC` dispatcher dict. **Sub-4 launcher must enforce intra-FOCAL ordering.**
- **HG dual-path validation regime** — Path A (Strong) if scorecard retrievable; Path B (Weak-inequality) if not. Launcher attempts retrieval first; passes `HG_GROUND_TRUTH_PATH=A|B` to implementing agent's environment.
- **FOCAL partly-tier YAGNI collapse** — project at binary granularity (TRUE → 2; FALSE → 0); document systematic over-scoring on Federal US LDA per battery; tolerance budget ~±15 raw points on the 81 target. Defer typed extraction of partly-tier sub-criteria to compendium 2.0 freeze.
- **scope.3 strict-AND read for v2 staff split** — `staff_in_scope = legislative_staff AND executive_staff`. Federal US LDA validation will surface whether strict reading aligns with L-N 2025.
- **scope.2 calibration cutoffs** — defaults `LOW_DOLLAR_CUTOFF = $1000`, `LOW_TIME_CUTOFF = 5%`. Module constants; pre-tested per-fixture override for calibration sensitivity. Federal US LDA's $3000 + 20% threshold is "significant" under these cutoffs (matches published scope.2 = 0).
- **2024-vs-2025 vintage handling** — single dispatcher with `min_vintage` / `max_vintage` per spec entry; `current_vintage` parameter on `project_focal_2024(cells, jurisdiction, vintage)` selects scope. `relationships.lobbyist_list_2025` and `timeliness.1_2_merged_2025` are vintage=2025-only; `timeliness.1` and `timeliness.2` are vintage<=2024.
- **Cross-rubric overlap harness extension** — Plan 4 (FOCAL aggregation) ships 10 shared-row checks via extension of `tests/projections/test_cross_rubric_overlap.py`. Phase 4 audit prototype reuses this infrastructure.

## Results

The Sub-3 deliverables are plan docs (in `plans/`), not analysis results, so no entries in `results/`. Plan paths:

- [`../plans/20260518_hg_2007_plan.md`](../plans/20260518_hg_2007_plan.md) — ~500 lines. Declarative `_ATOMIC_SPEC` dispatcher; 38 in-scope items (10 enforcement+cooling-off OUT); 9 named helpers; dual-path validation regime (Strong if scorecard retrievable; Weak-inequality if not); Q15→Q16-Q19 conditional cascade; Q23/Q24 partial-scope projection.
- [`../plans/20260518_focal_2024_legal_core_plan.md`](../plans/20260518_focal_2024_legal_core_plan.md) — ~470 lines. Module skeleton + 26 legal-axis items (scope 4 + descriptors 6 + relationships 4+1 + revolving_door 1 + financials 11); 5 named helpers; scope.2 calibration cutoffs; scope.3 v2 staff-split strict-AND projection.
- [`../plans/20260518_focal_2024_contact_log_plan.md`](../plans/20260518_focal_2024_contact_log_plan.md) — ~320 lines. 11 contact_log items (9 NEW rows); binary reads via dispatcher's `is_not_null` / `or_any` generic helpers; partly-tier collapse with documented over-scoring.
- [`../plans/20260518_focal_2024_openness_timeliness_plan.md`](../plans/20260518_focal_2024_openness_timeliness_plan.md) — ~390 lines. 12 items (openness 9 + timeliness 3 with 2025 merge); 4 named helpers; first FOCAL battery to read practical-availability axis; openness.6 partly tier kept at 3-tier (operationally readable from v2 typed cell).
- [`../plans/20260518_focal_2024_aggregation_plan.md`](../plans/20260518_focal_2024_aggregation_plan.md) — ~510 lines. Top-level `project_focal_2024` + weighted-sum aggregation + Federal US LDA validation harness (load-bearing 81-raw-points target with per-battery tolerance) + ranking + cross-rubric overlap harness extension.

## Open Questions

Surfaced across the 5 plans for the implementing agent (or pre-launch decision) to confirm before launch:

**HG plan (5 questions):**
- HG-Q1: Per-state scorecard retrieval — Path A or Path B? **Recommendation:** attempt retrieval before starting implementation.
- HG-Q2: Q10 / Q22 form-OR relaxation handling. **Recommendation:** read reg-form cell only; document in module docstring.
- HG-Q3: Q12 session-calendar metadata cell. **Recommendation:** ship YAGNI projection (monthly = year-round); flag over-counting; defer metadata cell.
- HG-Q4: Q15 / Q16-Q19 itemization-conditional cascade. **Recommendation:** projection-side conditional.
- HG-Q5: Q35-Q37 practical-axis Phase D-only ground truth. **Recommendation:** Path A tests `pytest.mark.xfail` at landing.

**FOCAL legal-core plan (5 questions):**
- FOCAL-LC-Q1: scope.2 calibration cutoffs. **Recommendation:** `LOW_DOLLAR_CUTOFF = $1000`, `LOW_TIME_CUTOFF = 5%`; verify against Federal US LDA first.
- FOCAL-LC-Q2: scope.3 staff-cell read — AND or OR? **Recommendation:** strict AND.
- FOCAL-LC-Q3: Descriptors "partly" tier. **Recommendation:** YAGNI binary.
- FOCAL-LC-Q4: relationships.4 "partly" tier on detail level. **Recommendation:** YAGNI binary.
- FOCAL-LC-Q5: Per-battery subtotal API — informational only or load-bearing? **Recommendation:** informational (mirror Newmark 2005 no-sub-aggregate-validation discipline).

**FOCAL contact-log plan (3 questions):**
- FOCAL-CL-Q1: Partly-tier over-scoring vs published L-N 2025 — accept or fix? **Recommendation:** accept; tolerance ≤12 raw points on contact_log subtotal.
- FOCAL-CL-Q2: contact_log.11 OR over reg_form + spending_report sides. **Recommendation:** OR (matches spec doc framing).
- FOCAL-CL-Q3: `is_not_null` helper — module-level or per-item lambda? **Recommendation:** module-level shared helper.

**FOCAL openness-timeliness plan (3 questions):**
- FOCAL-OT-Q1: openness.1 partly tier ("optional registration or separate websites"). **Recommendation:** YAGNI binary.
- FOCAL-OT-Q2: openness.6 partly tier — 3-tier or binary? **Recommendation:** ship 3-tier (operationally readable from v2 typed Set[enum]).
- FOCAL-OT-Q3: timeliness merge 2025 indicator handling — CSV column naming. **Recommendation:** vintage-aware loader; verify CSV header before coding.

**FOCAL aggregation plan (3 questions):**
- FOCAL-AGG-Q1: Federal US LDA aggregate tolerance — exact or ±15? **Recommendation:** ship ±15; tighten in follow-up if delta consistently smaller.
- FOCAL-AGG-Q2: Cross-rubric harness scope — full pairwise or sampled? **Recommendation:** full pairwise.
- FOCAL-AGG-Q3: 2025 vintage US LDA — does per-country CSV include `lobbyist_list` for US? **Recommendation:** verify CSV header; mark 2025 test `xfail` if absent.

## Next steps

**Stream 3's plans are ready for Sub-5+ headless implementation once Sub-4's launch infrastructure exists.** Recommended sequencing per the locked rubric order:

1. **HG 2007 implementation** (rubric #7) — independent; can launch in parallel with FOCAL implementation. Pre-launch task: scorecard retrieval attempt (Wayback Machine `publicintegrity.org/politics/state-politics/influence/hired-guns/`).
2. **FOCAL 2024 implementation** (rubric #8 — 4 sub-implementation sessions in strict order):
   - Plan 1 (legal core) — first; introduces module skeleton.
   - Plan 2 (contact log) — second.
   - Plan 3 (openness + timeliness) — third.
   - Plan 4 (aggregation + Federal US LDA harness) — fourth (last); load-bearing validation.

After Stream 3 ships, Phase C is **7 of 8 score-projection rubrics complete** (Opheim blocked on 1988-89 statute data). Phase 4 cross-rubric agreement audit becomes the natural next research line — the `lobbyist_spending_report_includes_total_compensation` row reaches 8-module-confirmed at FOCAL landing.

**Sub-4 (launch infra + Sunlight canary)** is the next session. The launch infrastructure handles:

- Path-selection step for HG (retrieval attempt + `HG_GROUND_TRUTH_PATH` env var).
- Intra-FOCAL ordering enforcement (4-step sequence).
- Stream-2 ordering enforcement (Newmark 2017 before Newmark 2005).
- API-key handoff per [`../plans/20260514_headless_api_key_handoff.md`](../plans/20260514_headless_api_key_handoff.md).
- Sunlight canary — re-run rubric #3 implementation headless to validate the launcher.

## Session token cost

This sub-session ran on `ANTHROPIC_API_KEY` (work-project budget) per the multi-sub-session structure Sub-0 designed. Verified via session-start hostname/date probe (Dans-MacBook-Pro, 2026-05-18 UTC).
