# Sunlight 2015 projection: TDD session

**Date:** 2026-05-18
**Branch:** phase-c-projection-tdd

## Summary

Implemented rubric #3 in the Phase C locked order: Sunlight 2015. The
session followed the kickoff plan
[`plans/20260514_sunlight_2015_plan.md`](../plans/20260514_sunlight_2015_plan.md)
end-to-end. All 4 in-scope items (1, 2, 3, 5) are shipped with TDD'd
helpers, a frozen `Sunlight2015Score` model, a ground-truth loader that
strips footnote markers and preserves provenance, and a 50-state × 4-item
parameterized round-trip test (200 cells) validating against the published
CSV. Item 4 (`document_accessibility`) is regression-guarded as excluded
per the 2026-05-07 audit. The module exposes NO aggregation API
(`project_sunlight_2015_total` / `_grade` / `rank_*`) — also
regression-guarded.

Sunlight is a **shallow rubric** whose value is cross-rubric redundancy on
heavily-shared rows (11 of 13 v2 rows touched are read by ≥1 other rubric);
no novel observables. Its α form-type split introduces 3 spending-report-
side cells that Opheim 1991 will reuse via β AND-projection — those row
IDs are stable.

The session also surfaced a pre-existing **silent-drift bug in CPI 2015
C11**: `project_ind_201` reads `lobbyist_spending_report_includes_compensation`,
which doesn't exist in v2 (merged into the 8-rubric mega-row
`_includes_total_compensation` by D1/D2 of the row-freeze). CPI tests pass
only because fixtures use the same wrong name; the bug will surface
silently when extraction-harness ships v2-keyed cells. Filed as task #12;
not fixed in this session (out of scope).

## Topics Explored

- **Phase 0 pre-flight.** v2 cross-check on the 13 expected rows
  (all present, 1 rename `_by_client` → `_by_payer` already in plan's
  expected list). Ground-truth CSV smoke (50 rows, 10 cols, footnote
  markers observed). Data-year paper re-read: methodology section
  (lines 128–156) doesn't name a research period explicitly; line 242
  ("Kansas chooses not to hold any lobbying data before 2015") is only
  sensible from inside-2015 → lifted confidence MEDIUM-LOW → MEDIUM.
- **Item 1 TDD (3 stages).** unable_to_evaluate → 4 valid truth-table tiers
  with form-agnostic OR → 4 statutorily-implausible oddity combinations
  with `cascading-downward` semantics (lowest failing predicate sets
  tier).
- **Item 2 TDD.** Truth table uses explicit wildcards from the spec doc;
  `(T, F, T)` → tier 2 (per wildcard rule) plus non-None oddity flag.
- **Item 3 TDD.** Typed `Optional[Decimal]` cell. Per spec,
  `threshold IS NULL → 0` (no threshold defined ⇒ all expenditures
  itemized); `threshold > 0 → -1`. The `unable_to_evaluate` sentinel is
  reserved for "row not a key in cells" — distinct from "row present,
  value None."
- **Item 5 TDD.** Form-agnostic OR over 3 binary cells. Tier 0 for any
  disclosure mode; tier -1 only when all 3 modes False. No oddity flags
  (no statutory implausibility among the three modes).
- **Item 4 regression-guard.** No helper defined; `EXCLUDED_ITEMS`
  contains the item; `IN_SCOPE_ITEMS` does not.
- **Ground-truth loader.** Strips trailing markers (`*`/`**`/`***`/`^^`)
  via a single regex; preserves marker provenance in a sibling dict.
  Phase 0 inventory confirmed 36 marker-carrying cells (28 `*`, 2 `**`,
  5 `***`, 1 `^^`).
- **50-state × 4-item parameterized round-trip.** Reverse-projection
  cells builder (test-only fixture) constructs minimal cells dict whose
  projection should yield the published tier; runs `project_sunlight_2015`;
  asserts equality. 200 cells, all pass.
- **Pre-existing CPI drift.** Surfaced during Sunlight Phase 0 — see task
  #12.

## Provisional Findings

- **Sunlight's per-item logic is straightforward but heterogeneous.**
  Item 1 needs a 6-cell form-agnostic OR + nested-tier table; item 2 has
  wildcard tiers; item 3 is a single typed read; item 5 is a 3-cell OR.
  Function-per-item dispatcher fits cleanly; a declarative table would
  not compress them.
- **Cascading-downward vs highest-tier-wins semantics is a real
  asymmetry.** Item 1's spec table is monotonic (no wildcards); item 2's
  spec table uses an explicit `(T, *, T) → 2` wildcard. I implemented
  item 1 with cascading-downward (lowest failing predicate sets tier)
  and item 2 with the wildcard. Both options exist for rubrics with
  nested predicates; future rubrics should pick deliberately.
- **The `unable_to_evaluate` convention works.** Helper signature
  `tuple[int | Literal["unable_to_evaluate"], str | None]` cleanly
  separates "couldn't determine" from "determined a tier (possibly with
  oddity)." Threading into `Sunlight2015Score.per_item_scores` as
  `dict[str, int | str]` keeps the score model frozen and downstream-
  consumable.
- **The 200-cell round-trip is a weak validation.** It exercises
  reverse-projection-to-projection consistency, not statute-extraction-
  to-projection consistency. The real validation comes when
  `extraction-harness-brainstorm` ships and we run the projection on
  actual extracted cells. For now: it confirms wiring + the canonical
  truth-table rows reach the right tier.
- **Sunlight cross-rubric reuse is high.** 11 of 13 v2 rows feed other
  rubrics. The Phase 4 cross-rubric agreement audit (deferred until
  ≥3 modules exist; we now have CPI + PRI + Sunlight) becomes well-
  defined.

## Decisions Made

- **Helper return shape:**
  `tuple[int | Literal["unable_to_evaluate"], str | None]`. Score is
  either the tier (signed int) or the sentinel; oddity is None for
  clean inputs or a description string for statutorily-implausible
  inputs. Threaded into the score model as a `dict[str, int | str]`
  for scores and `dict[str, list[str]]` for oddity flags (list to
  accommodate multiple flags per item, though Sunlight items currently
  emit at most one).
- **Item 1 implausible-combo semantics: cascading-downward.** Spec is
  silent on the 4 non-monotonic rows; I picked the rule "tier = lowest
  failing predicate's tier." This treats nesting as strict; the
  alternative (highest-tier-wins) would produce different tiers for the
  same oddity cases. Documented in module + convo for future revisit.
- **No aggregation API.** Confirmed firm via user disambiguation:
  module exposes no `project_sunlight_2015_total` / `_grade` /
  `rank_sunlight_2015_states`. Regression-guarded.
- **Data-year confidence lifted MEDIUM-LOW → MEDIUM.** Sub-1 follow-up
  task in `results/20260514_rubric_data_years.md` marked done.
- **CPI 2015 drift not fixed in this session.** Filed as task #12 to
  preserve session focus; out of scope for Sunlight TDD.

## Results

- [`results/20260518_sunlight_2015_projection.md`](../results/20260518_sunlight_2015_projection.md)
  — what landed, validation outcome, row-promotion delta, naming-drift
  corrections, items skipped per YAGNI.

## Open Questions

- **Item 1 semantics: cascading-downward vs highest-tier-wins.** The
  current implementation defaults to cascading-downward. The user may
  prefer "highest-tier-wins" for symmetry with item 2's wildcard table.
  No real data exists yet to discriminate (extraction harness pending);
  the choice can be revisited in Phase 4.
- **Oddity flags as list[str].** Score model carries
  `oddity_flags: dict[str, list[str]]` for forward compatibility, but
  Sunlight items emit at most one flag each (always length 0 or 1).
  Newmark / HG / FOCAL may need multiple flags per item; the list shape
  is ready.
- **Marker semantics still uninterpretable.** Sunlight's published
  scorecard uses footnote markers (`*`, `**`, `***`, `^^`) without
  documenting their meaning. Provenance is preserved for audit-traceable
  validation; the markers don't currently affect projection logic.
- **Reverse-projection canonical-row choice.** For tiers that admit
  multiple input combinations (item 1 tier 2; item 5 tier 0), the
  reverse-projection picks a canonical row. Tests are deterministic but
  not exhaustive over the input domain. A separate test could exercise
  all valid input combinations producing a given tier.
- **CPI #201 drift fix (task #12).** When and how to land — same session,
  next session, or batched with a v2-row-reference audit test (e.g.,
  `tests/test_v2_row_references_exist.py` checking every row name
  referenced in projections code/tests exists in the live v2 TSV).

## Next steps

Phase C rubric #4: **Newmark 2017**. Per the rubric implementation
playbook: 14 v2 rows, 8 reused + 6 new, sum-of-19-binaries index, load-
bearing r=0.04 CPI↔PRI-disclosure correlation. Sub-1's recommendation
was to defer Newmark plans until GH #9 (row-ID renames) merged — that
landed 2026-05-14, so Newmark 2017 plan drafting is now unblocked.

Alternatives:
- (b) Implement Opheim 1991 (rubric #6) since its plan is also ready
  (drafted Sub-1 along with Sunlight). Opheim's β AND-projection
  imports `project_sunlight_item1` for the cross-rubric continuity
  test — that import now resolves.
- (c) Prototype the Phase 4 cross-rubric agreement audit on the
  3-module overlap (CPI + PRI + Sunlight). Most-validated row
  `lobbyist_spending_report_includes_total_compensation` is the
  natural starting point, but the CPI drift surfaced this session
  means an audit prototype would fail on that row until task #12 lands.
- (d) Fix CPI drift (task #12) — small, surgical, unblocks (c).

Recommendation: **(d) first, then (a) or (b).** The CPI drift is a small
yak-shave that unblocks Phase 4 prototyping and removes a load-bearing
silent failure mode before extraction harness lands. (a) and (b) are
equally good after that; either advances the locked rubric order.
