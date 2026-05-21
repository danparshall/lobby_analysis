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

## Findings (will fill in as work proceeds)

_(Empty at session start.)_

## Decisions made

_(Empty at session start.)_

## Next steps

_(Empty at session start.)_
