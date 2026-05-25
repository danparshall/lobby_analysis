<!-- Generated during: convos/20260518_sunlight_2015_projection_tdd.md -->

# Sunlight 2015 projection — landed

**Date:** 2026-05-18
**Branch:** phase-c-projection-tdd
**Convo:** [`../convos/20260518_sunlight_2015_projection_tdd.md`](../convos/20260518_sunlight_2015_projection_tdd.md)
**Plan:** [`../plans/20260514_sunlight_2015_plan.md`](../plans/20260514_sunlight_2015_plan.md)
**Spec doc:** [`../../../historical/compendium-source-extracts/results/projections/sunlight_2015_projection_mapping.md`](../../../historical/compendium-source-extracts/results/projections/sunlight_2015_projection_mapping.md)

## What landed

- **Module:** `src/lobby_analysis/projections/sunlight_2015.py` —
  4 per-item helpers (item 1 nested 4-tier with α form-type split;
  item 2 4-tier with wildcard; item 3 2-tier typed; item 5 2-tier OR),
  a frozen `Sunlight2015Score` Pydantic model, top-level
  `project_sunlight_2015(cells, state)`, ground-truth loader
  (`load_sunlight_2015_reference` + `_marker_provenance`).
- **Tests (3 files, 250 tests):**
  - `tests/projections/test_sunlight_2015_per_item.py` (31 tests):
    item 1 (14 covering unable_to_evaluate + 8 valid truth-table tiers +
    4 oddity combos), item 2 (5), item 3 (5), item 5 (4 — incl. 7-combo
    parameterization), item 4 regression guards (3).
  - `tests/projections/test_sunlight_2015_ground_truth.py` (11 tests):
    50-state count, USPS keying, in-scope items, no item 4, no markers
    in numeric values, 3 spot-checks (MA top, FL bottom, KY mid),
    marker-provenance preservation (36 markers expected).
  - `tests/projections/test_sunlight_2015_aggregation.py` (208 tests):
    regression guards (no total/grade/rank function or field), reverse-
    projection cells builder, **50-state × 4-item parameterized round-
    trip (200 cells)**, top-level wiring (Score model shape,
    UNABLE_TO_EVALUATE propagation, oddity-flag threading), marker-
    carrying-cell round-trip.

## Validation outcome

- **250/250 Sunlight tests pass.**
- **Full repo:** 926 pass + 3 pre-existing failures unchanged from main
  (`tests/test_pipeline.py::test_ca_snapshot_*`,
  `test_brief_contains_*`, `test_stamp_rows_*` — all
  `FileNotFoundError` on gitignored `data/portal_snapshots/...`).
  Same failures CPI 2015 and PRI 2010 sessions flagged.
- **200-cell round-trip:** every (state, item) pair in the published
  CSV round-trips via the reverse-projection cells builder. This
  validates wiring + canonical-truth-table picks, not statute extraction.

## Phase 0 outcomes

| Task | Outcome |
|---|---|
| v2 row-name cross-check | **CLEAN.** 13/13 expected rows present after the `_by_client` → `_by_payer` rename applied in the plan's `expected` list. 0% drift. |
| Data-year paper re-read | **Confidence MEDIUM-LOW → MEDIUM.** Kansas line 242 firms lower bound at 2015; no explicit research-period sentence anywhere in methodology. Doc updated. |
| Ground-truth CSV smoke | **PASS.** 50 rows × 10 cols; 36 marker-carrying cells across in-scope columns (28 `*`, 2 `**`, 5 `***`, 1 `^^`). |
| `STATE_NAME_TO_USPS` DC coverage | **N/A.** Sunlight CSV does not include DC (50 states only). All 50 state names map cleanly. |

## Row-promotion delta

Sunlight 2015 reads 13 v2 rows; landing this projection module promotes
each row's `n_rubrics_read_by` count by 1 (when joined with the existing
rubric mappings). Most notable:

- `lobbyist_spending_report_includes_total_compensation` was already the
  **8-rubric mega-row** (anchored by D1/D2 merge during the 2026-05-13
  row-freeze). Sunlight item 5 reads it; cross-rubric agreement at this
  row across CPI + PRI + Sunlight is now well-defined (with the caveat
  that CPI's actual module reads a no-longer-existent row — see
  Naming-drift section).
- `lobbyist_spending_report_includes_compensation_broken_down_by_payer`:
  Sunlight item 5 confirms a 5th rubric reads this row (post-rename
  from `_by_client`).
- `lobbyist_filing_itemization_de_minimis_threshold_dollars`: Sunlight
  item 3 confirms the row's tier-defining role for the itemization-
  threshold concept (distinct from registration / filing-de-minimis
  thresholds).

## Naming-drift corrections

- **Sunlight spec doc `_by_client` → v2 `_by_payer`:** rename baked into
  the module docstring + the plan's expected-row list. Zero code-level
  drift after Phase 0 cross-check.
- **CPI 2015 silent drift surfaced (NOT FIXED this session):**
  `src/lobby_analysis/projections/cpi_2015_c11.py:200` reads
  `lobbyist_spending_report_includes_compensation`, which does not exist
  in v2. The row was merged with PRI E2f_i into the canonical
  `lobbyist_spending_report_includes_total_compensation` by D1/D2 of the
  2026-05-13 row-freeze. CPI tests pass only because the test fixtures
  use the same wrong name. Silent failure mode: when the extraction
  harness ships v2-keyed cells, CPI IND_201's `compensation` half will
  always read None → always score 0 → IND_201 will be capped at tier 50
  for every state. Filed as task #12. See convo "Next steps" for
  proposed sequencing.

## Items skipped per YAGNI

- **Item 4 (`document_accessibility`).** Excluded per 2026-05-07 audit;
  no helper defined; `EXCLUDED_ITEMS` carries the exclusion;
  regression-guarded against accidental re-introduction.
- **Sunlight's `Total` and `Grade`** (and `rank`). Not reproducible from
  4 items; module exports no aggregation API; regression-guarded against
  accidental implementation.
- **Reverse-projection exhaustive enumeration.** The 200-cell round-trip
  uses canonical truth-table rows; tiers admitting multiple input
  combinations (item 1 tier 2; item 5 tier 0) are exercised at one row
  each. Comprehensive enumeration is unit-test scope and would not catch
  bugs the per-item truth-table tests don't already catch.
- **`compute_partial_total` diagnostic.** User confirmed firm-no on
  any aggregation API exposure during the disambiguation question; the
  module is regression-guarded against it.

## Decisions log

1. **Helper return type unified:** `tuple[int | Literal["unable_to_evaluate"], str | None]`
   for all 4 helpers (no two-shape return-style asymmetry between
   "missing cells" vs "valid tier with oddity"). Score model carries
   `dict[str, int | str]` for per-item scores; `dict[str, list[str]]`
   for oddity flags.
2. **Item 1 implausible-combo semantics: cascading-downward.** Tier =
   lowest failing predicate's tier. Spec table is monotonic with no
   wildcards; this rule is one of two defensible defaults. Documented
   for future revisit.
3. **Item 3 `unable_to_evaluate` only when row absent.** Row present
   with `legal_availability=None` projects to tier 0 (per spec rule
   "threshold IS NULL → 0"). Asymmetric with items 1, 2, 5 — for those,
   `legal_availability=None` projects to unable_to_evaluate.
4. **`Sunlight2015Score` is frozen.** No total / grade / rank fields.
   Regression-guarded.
5. **Module structure mirrors CPI 2015 C11** (function-per-item, axis
   constants, `_legal` helper). Not the declarative-table pattern from
   PRI 2010 — Sunlight's 4 in-scope items have bespoke compound logic
   that a declarative table wouldn't compress.

## Commit cadence

The session produced 9 commits in this branch:

```
3d37cc0 docs: sunlight 2015 data-year confidence lift from paper methodology re-read
9d0f93b projections: sunlight 2015 item 1 unable_to_evaluate (stage 1)
5a5f214 projections: sunlight 2015 item 1 truth-table tiers (stage 2)
e844b4b projections: sunlight 2015 item 1 oddity flags (stage 3, item 1 complete)
5bfc370 projections: sunlight 2015 item 2 expenditure_transparency
a27151c projections: sunlight 2015 item 3 expenditure_reporting_thresholds
2544804 projections: sunlight 2015 item 5 lobbyist_compensation (4 in-scope items complete)
482c3ba projections: sunlight 2015 item 4 regression guards (excluded; no helper)
e7eb4d3 projections: sunlight 2015 ground-truth loader + marker provenance
bfb783e projections: sunlight 2015 top-level + 50-state validation
```

(Plus one finish-convo doc commit forthcoming.)
