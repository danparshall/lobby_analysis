# 20260521 — FOCAL 2024 legal_core TDD

**Branch:** `phase-c-projection-tdd`
**Plan:** [`../plans/20260518_focal_2024_legal_core_plan.md`](../plans/20260518_focal_2024_legal_core_plan.md)
**Predecessor convo:** [`20260521_hg_vintage_finding_and_deferral.md`](20260521_hg_vintage_finding_and_deferral.md) (HG deferred; FOCAL is next)
**Spec doc:** [`docs/historical/compendium-source-extracts/results/projections/focal_2024_projection_mapping.md`](../../../historical/compendium-source-extracts/results/projections/focal_2024_projection_mapping.md)

## Goal

Ship the `focal_2024.py` module skeleton + 26 in-scope legal-axis items (scope 4 + descriptors 6 + relationships 4+1 + revolving_door 1 + financials 11). This is sub-1 of 4 FOCAL sub-plans that all converge on a single `focal_2024.py`. Aggregation lives in Plan 4 — this plan ships only the per-item dispatcher + ground-truth loader stub.

## Pre-flight outcomes

- ✅ **Phase-0 row cross-check**: all 35 v2 row IDs the plan names are present in the live TSV (`compendium/disclosure_side_compendium_items_v2.tsv`). No further spec-doc-vs-v2 renames needed.
- ⚠️ **17th rename discovered**: the plan's working name `relationships.lobbyist_list_2025` (for the 2025-only "lobbyist list" indicator) doesn't match L-N 2025's actual indicator ID. The published CSV uses `relationships.0` with `focal_2024_indicator_id_map = "(new in 2025)"`. **Adopt `relationships.0` in the module spec table.**
- ✅ **Federal US LDA published aggregate confirmed**: weighted sum 81, max sum 182, raw sum 42 (from CSV). Excluding revolving_door.2 per FOCAL-1: max → 180, US weighted stays 81 (US scored 0 on r.d.2). Target: 81/180 = 45.0%.
- ✅ **Cell-type metadata verified** for all 11 non-binary cells: typed-Decimal × 2, typed-TimeThreshold × 1, typed-Set[enum] × 3, typed-Optional[enum/SectorClassification] × 2, typed-structured (count_with_FTE, TimeSpent) × 2, plus binary descriptors.6.
- ✅ **Template chosen**: `newmark_2017.py` is the closest analog — single-row binary dispatcher + typed-IS-NOT-NULL helper + named compound helpers (gifts-OR) + Pydantic frozen score model + `UNABLE_TO_EVALUATE` sentinel.

## OQ defaults adopted (per plan recommendations + user confirmation)

| # | Question | Default |
|---|---|---|
| OQ1 | scope.2 cutoffs | `LOW_DOLLAR_CUTOFF=Decimal("1000")`, `LOW_TIME_CUTOFF=Decimal("5")` (percent), module constants, fixture-overridable |
| OQ2 | scope.3 staff cells | **AND (strict)** — both `def_target_legislative_staff` AND `def_target_executive_staff` must be True for `staff_in_scope=True` |
| OQ3 | descriptors "partly" tier | **YAGNI binary** (TRUE → 2, FALSE/missing → 0). Documented in module docstring as known over/under-scoring channel |
| OQ4 | relationships.4 "partly" tier | **YAGNI binary**. Same justification |
| OQ5 | per-battery subtotals | **Informational only** — score model exposes them but tests don't assert vs L-N Table 5 sub-totals |

## Sentinel semantics (decision)

- `UNABLE_TO_EVALUATE` sentinel for missing cells (match Sunlight/Newmark recent convention; honest about extraction holes; PRI's silent-0 hides data-completeness failures).
- Per-item dispatcher returns `int | Literal["unable_to_evaluate"]` where `int ∈ {0, 1, 2}`.

## TDD sequence (smallest-to-largest dispatcher complexity)

1. **Descriptors** (6 items, simplest single-cell binary reads). Tests + minimal module shape.
2. **Revolving door** (1 item, single binary read).
3. **Relationships** (4 binary + 1 vintage-gated `relationships.0` — first vintage-gate exercise).
4. **Financials** (11 items: 8 single binary or typed; financials.7 reuses descriptors.6's cell; financials.6 = AND-helper; financials.10 = OR-helper imported from newmark_2017).
5. **Scope** (4 items, all named helpers; needs `def_lobbyist_actor_types` + `def_lobbying_activity_types` enum lookups).
6. **Ground-truth loader stub** (`load_focal_2024_per_country_reference(repo_root)`).

Each step: tests first (RED) → minimal code (GREEN) → commit.

## Session work landed

12 of 26 legal-core items shipped (descriptors 6 + revolving_door 1 + relationships 4 binary + 1 vintage-gated):

| Commit | Battery | Items | Tests added |
|---|---|---|---|
| `6a482ec` | Descriptors (skeleton + 6 items) | 6 | 20 truth-table + 3 regression guards |
| `57f1b17` | Revolving door + relationships | 6 | 19 (3 + 16) |

Full projections suite: 718 pass (was 676 → 699 after descriptors → 718). Ruff clean. 42 FOCAL per-item tests.

## Findings

- **Phase-0 cross-check passes**: all 35 v2 row IDs the plan names are present in the live TSV. No new spec-doc-vs-v2 renames needed for the legal-core scope (the 16 renames listed in the plan still hold).
- **17th rename discovered (relationships.0)**: the plan's working name `relationships.lobbyist_list_2025` does not appear in the L-N CSV. The CSV uses `relationships.0` with `focal_2024_indicator_id_map = "(new in 2025)"`. Adopted `relationships.0` as the canonical FOCAL indicator id. Module docstring lists this as rename #17.
- **Federal US LDA aggregate verified** from the CSV's US row: weighted sum 81, raw sum 42, max sum 182. Excluding revolving_door.2 (weight 1 × max 2): max → 180, US weighted stays 81 (US scored 0 on r.d.2). Plan target 81/180 = 45.0% holds.
- **FOCAL is a cross-national framework, not a US-state framework.** L-N 2025 applied FOCAL to 28 jurisdictions at national-level only. The "United States" row in the CSV is the **federal LDA**, not any US state. No per-state FOCAL ground truth exists. State-level validation runs via cross-rubric agreement (Plan 4 owns the harness). Other 27 countries are `xfail`-marked reference data.
- **Cell-type metadata confirmed** for 11 non-binary legal-core cells: typed Decimal × 2 (compensation/expenditure thresholds), typed TimeThreshold × 1 (time percent), typed Set[enum] × 3 (actor types, activity types, income-source types), typed Optional[enum/SectorClassification] × 2 (legal_form, sector), typed structured × 2 (count_with_FTE, TimeSpent), binary descriptors.6.

## Decisions made

- **Sentinel = `UNABLE_TO_EVALUATE`** for missing cells (matches Sunlight + Newmark recent convention; surfaces extraction holes as test failures rather than hiding them as silent score-0 readings).
- **Binary cells return 2/0** (not 1/0) — FOCAL per-item granularity is 0/1/2; partly-tier collapses to binary per OQ3/OQ4 YAGNI. Documented in module docstring as a known over/under-scoring channel.
- **Vintage gate via `_MIN_VINTAGE` dict + KeyError on mismatch.** `relationships.0` is registered with `min_vintage=2025`; a 2024-vintage caller dispatching it raises KeyError (programming-error tripwire vs silent UNABLE — UNABLE is reserved for data-missing semantics, not scope-mismatch).
- **OR-helper `_project_binary_or_2tier(cells, row_ids)` is module-internal.** Reusable for relationships.1 (and the upcoming financials.10 — though the plan's recommended pattern there is to import newmark_2017's `project_gifts_actor_agnostic_or` and rescale 0/1→0/2, which gives a coupling test against newmark_2017's stability).
- **All 5 OQ defaults from the plan are in force** for the next session's continuation (scope.2 cutoffs $1000/5%, scope.3 staff AND-strict, descriptors/relationships.4 partly-tier YAGNI, per-battery subtotals informational only).

## Permission-rule note

The MEMORY-noted footgun (`uv run pytest` resolves to main's editable install in a worktree) forces `.venv/bin/python -m pytest ...`. The `Bash(python *)` pre-approval doesn't cover this prefix, so every pytest invocation triggered a prompt mid-session. Dan added `Bash(.venv/bin/python *)` to the permission list. Subsequent FOCAL sessions on this branch (and any other worktree-isolated TDD) will run without prompts.

## Next steps (handoff for next session on this branch)

Continue FOCAL legal-core implementation. Remaining work:

1. **Financials battery** (11 items, mixed shapes) — biggest remaining battery. financials.7 reuses descriptors.6's cell; financials.6 = AND-helper over 2 binary rows; financials.10 = OR-helper (import `project_gifts_actor_agnostic_or` from `newmark_2017` per plan's reuse recommendation, rescale 0/1 → 0/2). The 5 typed-IS-NOT-NULL items (financials.3 set, financials.4 count_with_FTE, financials.5 TimeSpent) need the existing `_project_typed_is_not_null_2tier` helper.
2. **Scope battery** (4 items, all named helpers): scope.1/scope.4 set-membership 3-tier (need the enum definitions from `lobby_analysis.models` or the items_FOCAL doc for "full set" and "partly" predicate); scope.2 calibrated 3-tier (dollar/time cutoffs as module constants); scope.3 AND-projection over 5 binary cells (uses v2 staff-split).
3. **Ground-truth loader stub** (`load_focal_2024_per_country_reference(repo_root)`) reading `docs/historical/compendium-source-extracts/results/focal_2025_lacy_nichols_per_country_scores.csv`. Returns `dict[country_code, dict[indicator_id, int]]`. Per-item subset for the 26 legal-core indicators; companion plans expand.
4. **Closing**: After scope + financials + loader land, this sub-plan is done. Plan 2 (contact_log, 11 items) is the next sub-plan in the FOCAL ordering.

Convo for next session should be `20260522_focal_2024_legal_core_continued.md` (or similar) — same per-sub-plan granularity. The overarching `focal_2024_tdd.md` convo lands at Plan 4 completion per the plan's "Closing the loop" section.
