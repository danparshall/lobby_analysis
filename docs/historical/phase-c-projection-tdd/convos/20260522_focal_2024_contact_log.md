# 20260522 — FOCAL 2024 contact_log TDD

**Branch:** `phase-c-projection-tdd`
**Plan:** [`../plans/20260518_focal_2024_contact_log_plan.md`](../plans/20260518_focal_2024_contact_log_plan.md)
**Predecessor convo:** [`20260522_focal_2024_legal_core_continued.md`](20260522_focal_2024_legal_core_continued.md)
**Spec doc:** [`docs/historical/compendium-source-extracts/results/projections/focal_2024_projection_mapping.md`](../../../historical/compendium-source-extracts/results/projections/focal_2024_projection_mapping.md) — contact_log section (lines 653–764)

## Goal

Plan 2 of the FOCAL 4-plan set — extend `focal_2024.py` with the 11 contact_log
atomic items (9 NEW v2 rows + 2 reused Sunlight rows). All 11 are
`legal_availability` axis reads. Contact log is FOCAL's most-distinctive
battery: 9 of 11 items are read at per-meeting granularity that no other
contributing rubric exercises.

## Pre-flight outcomes

- ✅ Plan-vs-shipped **architecture mismatch verified superficial only.**
  Plan called for `_ATOMIC_SPEC.update({...})` with `Spec(rows, axis, weight,
  helper, min_vintage)` named-tuples and helper-name strings
  (`"is_not_null"`, `"or_any"`). Legal-core actually shipped with
  `_SINGLE_ROW_SPEC → _SPEC_BY_ITEM` (single-row dict, kind ∈ {"binary",
  "typed_is_not_null"}) + `_COMPOUND_DISPATCH` (dict of lambdas / named
  callables). Every Plan 2 element maps cleanly to the shipped shape — no
  architectural decision required.
- ✅ **Phase 0 cross-check clean.** All 12 v2 rows (11 items, +1 for
  contact_log.11's OR α-pair) present in `compendium/disclosure_side_compendium_items_v2.tsv`
  with **0 renames needed** (plan's claim verified — no late-discovered
  rename like `relationships.0` was in legal-core).
- ✅ **contact_log.6 cell type confirmed** as `typed Optional[enum]` →
  `_TYPED_NOT_NULL` kind (existing `_project_typed_is_not_null_2tier`
  helper handles it; no new helper needed).
- ✅ **Federal US LDA validation values cross-checked from CSV.** Per-item
  raw values for the 11 contact_log indicators: `[1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1]`
  (raw sum 4 / weighted 10). Resolves the plan's Open Issue FOCAL-5
  (audit-doc-vs-CSV ordering ambiguity for contact_log.1) — the CSV is
  unambiguous; plan's per-item discussion was tracking the weighted
  contribution (1×2=2 for partly-tier indicators), not the raw value
  itself.

## Session work landed

Plan 2 shipped in one session, ~150 LOC:

| Commit | Battery / piece | Items added | Tests added |
|---|---|---|---|
| (this session) | Contact log (11 items: 9 binary + 1 typed_is_not_null + 1 OR-pair) + `FOCAL_2024_CONTACT_LOG_INDICATORS` frozenset + ground-truth loader test extension | 11 | 40 per-item + 18 ground-truth = 58 |

Full projections suite: **888 pass + 3 xfailed** (was 830 + 3 xfailed at
session start). Ruff clean throughout.

## Topics explored

- **Architecture-translation sanity check before writing tests.** The plan
  was drafted before legal-core implementation, so it described an
  `_ATOMIC_SPEC.update(...)` with helper-name strings that doesn't exist in
  the shipped module. Mapping checked: 10 binary/typed items → 10 rows in
  `_SINGLE_ROW_SPEC`; contact_log.11 OR pair → one lambda in
  `_COMPOUND_DISPATCH` using existing `_project_binary_or_2tier` (already
  used by `relationships.1`). No new helpers; no weights in the spec
  table (Plan 4 owns weights via the per-indicator CSV); no `_MIN_VINTAGE`
  entries (all 11 are non-vintage-gated).
- **All 3 plan Open Questions resolve trivially to shipped patterns.**
  OQ-1 (partly-tier over-scoring on .1, .3, .9, .11): accept binary
  projection, document in docstring, Plan 4 absorbs via tolerance. OQ-2
  (contact_log.11 OR over reg_form + spending_report): use existing
  `_project_binary_or_2tier` helper. OQ-3 (`is_not_null` helper
  placement): no decision needed — `_TYPED_NOT_NULL` kind already wires
  the existing `_project_typed_is_not_null_2tier` helper via the
  dispatcher.
- **Convo-name date discipline.** Handoff sentence proposed
  `20260523_focal_2024_contact_log.md`; actual UTC date is 2026-05-22.
  Settled on `20260522_focal_2024_contact_log.md` for date-precedent
  consistency with the prior session
  (`20260522_focal_2024_legal_core_continued.md`).
- **OR-helper test parity with relationships.1.** Contact_log.11 tests
  mirror `relationships.1` coverage (7 cases: 4 truth-table TT/TF/FT/FF +
  3 partial-missing cases) rather than just the 4-case grid the plan
  listed. The partial-missing semantics (T+missing → 2; F+missing → UNABLE;
  missing+missing → UNABLE) are load-bearing for downstream extraction
  reliability and matched the shipped helper exactly.

## Provisional findings

- **Federal US LDA contact_log per-item raw values = `[1,0,1,0,0,0,0,0,1,0,1]`,
  raw sum 4, weighted 10** — verified verbatim against L-N 2025
  per-country CSV via 11 parameterized per-indicator tests.
- **Partly-tier over-scoring quantified.** Four indicators publish raw=1
  ("partly" tier): contact_log.1, .3, .9, .11. Binary projection
  over-scores each by 1 raw point if the underlying v2 cell extracts as
  TRUE (which it does for all four on US LDA). Cumulative US LDA
  over-scoring on contact_log subtotal: **+4 raw / +10 weighted**
  (projected 20 weighted vs published 10). Documented in module docstring
  and ground-truth test docstrings.
- **`_project_binary_or_2tier` reuse confirmed as the FOCAL OR convention.**
  Now used by relationships.1 + contact_log.11; same UNABLE-on-partial-
  missing semantics enforced by both. Future α form-type splits in
  openness or timeliness can adopt the same shape.
- **No spec-doc-vs-v2 renames discovered.** All 12 row IDs (11 items + the
  α-pair second row for contact_log.11) present in TSV at session start
  with verbatim names. Plan's Phase 0 cross-check claim verified.

## Decisions made

- **All 3 plan Open Questions defaulted** to the recommended resolutions
  (accept partly-tier over-scoring, OR for contact_log.11, no new helper
  for contact_log.6).
- **`FOCAL_2024_CONTACT_LOG_INDICATORS`** exported as a public frozenset
  alongside the legal-core one, for Plan 3/4 introspection. Two indicator
  sets are disjoint (regression-guarded by
  `test_legal_core_and_contact_log_are_disjoint`).
- **Section-header cleanup in ground-truth test file.** Renamed the
  pre-existing "27 reference countries: presence smoke test + xfail
  aggregates" header to "presence smoke test (legal-core slice)" and gave
  the xfails their own header ("per-country aggregate xfails (Plan 4
  territory)"), reflecting the new structural reality with contact_log
  sandwiched between.

## Next steps

- **Plan 3 (FOCAL openness + timeliness):** 12 items. Practical-axis read
  pattern enters this plan (openness items are typically practical-axis,
  not legal-axis — first FOCAL plan to read `practical_availability`).
  Loader already loads these indicator rows; `FOCAL_2024_CONTACT_LOG_INDICATORS`
  and `FOCAL_2024_LEGAL_CORE_INDICATORS` together cover 38 of 50 indicators;
  openness+timeliness adds the final 12. Read
  [`plans/20260518_focal_2024_openness_timeliness_plan.md`](../plans/20260518_focal_2024_openness_timeliness_plan.md)
  at next session start.
- **Plan 4 (FOCAL aggregation):** top-level projector + US LDA federal-
  validation harness with the **±15 raw tolerance** budget that absorbs
  contact_log's +10 weighted partly-tier over-scoring (plus
  openness/timeliness contributions surfacing at Plan 3 landing).
  Closing plan for FOCAL.

Convo for the next session (per-sub-plan granularity per the legal-core
plan's "Closing the loop"): `<YYYYMMDD>_focal_2024_openness_timeliness.md`.
