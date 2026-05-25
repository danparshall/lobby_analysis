# 20260522 — FOCAL 2024 legal_core TDD (continued)

**Branch:** `phase-c-projection-tdd`
**Plan:** [`../plans/20260518_focal_2024_legal_core_plan.md`](../plans/20260518_focal_2024_legal_core_plan.md)
**Predecessor convo:** [`20260521_focal_2024_legal_core_tdd.md`](20260521_focal_2024_legal_core_tdd.md)
**Spec doc:** [`docs/historical/compendium-source-extracts/results/projections/focal_2024_projection_mapping.md`](../../../historical/compendium-source-extracts/results/projections/focal_2024_projection_mapping.md)

## Goal

Complete the FOCAL 2024 legal-core sub-plan — ship the remaining 15
items (financials 11 + scope 4) plus the ground-truth loader stub.
Predecessor convo shipped 12 of 26 (descriptors 6 + revolving_door 1 +
relationships 4 binary + 1 vintage-gated `relationships.0`); this
session shipped the remaining 15 items and the loader, closing the
legal-core sub-plan.

## Pre-flight outcomes

- ✅ All 5 OQ defaults inherited from prior session (scope.2 cutoffs
  $1000 / 5%, scope.3 staff-AND-strict, descriptors/relationships.4
  partly-tier YAGNI, per-battery subtotals informational only).
- ✅ Sentinel + 2-tier binary return + `_MIN_VINTAGE`-gated KeyError
  patterns inherited unchanged.
- ✅ All v2 row IDs for financials + scope verified present in live
  TSV at session start (no further spec-doc-vs-v2 renames needed).
- ✅ Newmark 2017's `project_gifts_actor_agnostic_or` confirmed as the
  intended import for `financials.10` (signature returns `int |
  Literal["unable_to_evaluate"]` with 0/1 granularity; FOCAL rescales
  to 0/2).

## Session work landed

15 of 26 legal-core items shipped (financials 11 + scope 4) + the
ground-truth loader stub:

| Commit | Battery / piece | Items added | Tests added |
|---|---|---|---|
| `da70480` | Financials (11 items) + Scope (4 items) + 7 compound helpers | 15 | 74 |
| `bcbff43` | Ground-truth loader stub + 27 legal-core indicator set | — | 38 + 3 xfail |

Full projections suite: 830 pass + 3 xfailed (was 718 → 792 → 830 across the two commits in this session). Ruff clean throughout.

## Topics explored

- **Financials.6 semantics judgment call.** The plan's pseudocode
  used `bool()` coercion (`bool(cells.get(row).get(axis))`), which
  silently maps `None` → `False` and would hide extraction holes.
  Shipped instead with **UNABLE-on-unknown** semantics matching the
  `relationships.1` OR-helper convention from the prior session.
  `_project_binary_and_3tier` returns UNABLE when any input cell is
  missing or has axis None; only known values determine 2/1/0.
- **Financials.10 rescale chain.** Imports
  `project_gifts_actor_agnostic_or` from `newmark_2017` (0/1 return)
  and multiplies by 2 to reach FOCAL's 0/2 per-item granularity.
  UNABLE passes through unchanged. A coupling-test
  (`test_financials_10_matches_newmark_2017_helper_rescaled`)
  surfaces drift if newmark's semantics change.
- **Financials.7 / descriptors.6 cell-share.** Both items read
  `lobbyist_reg_form_includes_employment_type` (binary). The plan
  proposed `IS NOT NULL → 2` for financials.7, but binary read on a
  binary cell collapses to the same answer; a parametrized regression
  test pins agreement across {TRUE, FALSE, None} axis values. Cleaner
  than introducing a second helper kind for the same row.
- **Scope.4 partly-tier divergence from spec doc.** The spec doc's
  P/N labels ("limited to influencing legislative changes" /
  "{face_to_face} only") don't atomize onto the 8-enum cell content
  (no `face_to_face` bit, no `legislative_changes_only` flag).
  Projected scope.4 parallel to scope.1's set-membership shape —
  full 8-set → 2, non-empty proper subset → 1, empty → 0. Documented
  as a known divergence in the module docstring + scope-4 test
  comments. US LDA scope.4 = 2 (full set) sanity-checks against the
  published anchor.
- **Scope.3 staff-AND vs major-branch precedence.** Scoring tree
  collapses to: known-FALSE major branch → 0 regardless of staff
  (UNABLE only when major branches still ambiguous between TRUE-all
  and one-FALSE); if all major branches TRUE, staff cells
  discriminate between 2 (both TRUE per OQ2 strict) and 1 (any
  FALSE). Staff-cell-missing yields UNABLE only when the answer is
  already-ambiguous between 2 and 1.
- **CSV missing-value flavors.** The L-N 2025 CSV has 40 `"NA"`
  cells ("not_assessable" — non-US scope.2/scope.3/scope.4) and 15
  empty cells (parliamentary-system `timeliness.2` for non-
  parliamentary jurisdictions). Loader collapses both to `None` in
  the returned dict; downstream aggregation excludes them from
  numerator AND denominator identically, so the L-N source
  distinction is documented but not preserved at the value level.
- **Indicator-ID convention for the loader.** Returns bare IDs
  (`"financials.1"`, not `"focal_2024.financials.1"`) verbatim from
  the CSV. Callers comparing against `_SPEC_BY_ITEM` add the prefix
  themselves; keeps the loader as a pure CSV reader and pushes
  prefix-awareness to the aggregation harness (Plan 4).

## Findings

- **US Federal LDA legal-core raw sum = 23** across the 27 legal-
  core indicators (scope 4 + descriptors 6 + revolving_door 2 +
  relationships 3 + financials 8). Verified verbatim against L-N 2025
  Suppl Table 5 via parametrized per-indicator tests.
- **US LDA scope.2 = 0 holds with the $1000 / 5% OQ1 defaults.**
  LDA has $3000 compensation + 20% time thresholds — both above the
  cutoffs, so `significant=True` → 0. The defaults don't require
  empirical refit; documented in the helper.
- **No new spec-doc-vs-v2 renames discovered.** All row IDs for the
  15 newly-implemented items were present in v2 TSV at session start;
  the 17 renames documented by the predecessor session cover the
  legal-core scope completely.
- **130 helpful per-item tests now anchor the legal-core surface**
  (42 from prior session + 74 financials/scope + 38 ground-truth + 3
  xfail = 157 FOCAL-specific). Ground-truth verbatim parametrized
  test catches indicator-ID drift, CSV reformat drift, and L-N
  publication corrections in one shot.

## Decisions made

- **`_project_binary_and_3tier` ships with UNABLE-on-unknown.**
  Diverges from plan pseudocode's `bool()`-coerce-None silently
  approach; matches project convention from `relationships.1`'s
  OR-helper. Documented in helper docstring.
- **`_COMPOUND_DISPATCH` dict replaces inline if-chain.** Consolidates
  all 7 compound items (`relationships.1`, `financials.6`,
  `financials.10`, `scope.1`-`scope.4`) into a single lookup table
  before the `_SPEC_BY_ITEM` fallthrough. Cleaner; companion plans
  extend by adding entries.
- **Scope.4 set-membership semantics deviate from spec doc P/N
  labels.** Projects parallel to scope.1's set-membership shape;
  documented in helper docstring + test comments + module docstring's
  "known systematic over/under-scoring channels" section.
- **Loader returns `int | None`.** Both NA and empty CSV cells →
  `None`; downstream aggregation treats them as `not_assessable`.
- **Loader returns bare indicator IDs.** No `focal_2024.` prefix;
  callers add for dispatcher comparison. Pushes prefix-awareness to
  Plan 4.
- **`FOCAL_2024_LEGAL_CORE_INDICATORS` exported as a public
  frozenset.** Module-public constant so companion plans + Plan 4
  can introspect the legal-core slice without re-listing the 27 IDs.

## Provisional cross-references for downstream plans

- **Plan 2 (contact_log, 11 items):** extend `_SINGLE_ROW_SPEC` with
  contact-log entries; add to `FOCAL_2024_LEGAL_CORE_INDICATORS` if
  the convention generalizes to "all in-scope indicators" — or
  introduce a parallel `FOCAL_2024_CONTACT_LOG_INDICATORS`.
- **Plan 3 (openness + timeliness, 12 items):** practical-axis read
  pattern; current helpers read `legal_availability`. Add an
  `axis` parameter or a parallel `_project_practical_*` family. The
  loader's `timeliness.2` empty cells are this plan's concern.
- **Plan 4 (aggregation):** top-level `project_focal_2024(cells,
  jurisdiction, vintage)` reads weights from L-N 2025 Suppl Table 4;
  sums weighted raw scores; compares to published per-country total.
  Cross-rubric agreement harness for US states (no per-state FOCAL
  ground truth). The `relationships.0` vintage-gate already wired;
  Plan 4 just needs to filter `IN_SCOPE_ITEMS` by `vintage` before
  dispatching.

## Open issues for future sessions

- **No new ones surfaced this session.** All 5 OQ defaults from the
  legal-core plan remained in force; no STOP-clause borderline
  `prohib`-like items emerged.
- **`relationships.4` partly-tier (binary disclosure vs detailed
  disclosure)** — projected at binary granularity per OQ4 YAGNI.
  US LDA `relationships.4` published = 0; binary projection of US
  cell value FALSE → 0 holds, so the STOP-clause check is satisfied.
  No follow-up needed unless Phase D extraction surfaces a state
  with the "Y but no detail" case.

## Next steps

- **Plan 2 (FOCAL contact_log):** 11 items. The next session should
  read `plans/20260518_focal_2024_contact_log_plan.md` (drafted same
  day as legal-core plan, per the plan-set). 9 NEW v2 rows fully
  consumed; no helper exports.
- **Plan 3 (FOCAL openness + timeliness):** 12 items.
  Practical-axis read pattern; add to the loader as needed (the
  loader already loads the openness/timeliness rows but the
  legal-core indicator set excludes them).
- **Plan 4 (FOCAL aggregation):** top-level projector + US LDA
  federal-validation harness + cross-rubric harness for US states.
  This is the closing plan; the convo for that session is the
  overarching `focal_2024_tdd.md` per the legal-core plan's "Closing
  the loop" section.

Convo for the next session: `20260523_focal_2024_contact_log.md`
(or similar — per-sub-plan granularity preserved).
