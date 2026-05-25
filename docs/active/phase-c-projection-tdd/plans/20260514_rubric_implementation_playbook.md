# Per-rubric implementation playbook

**Purpose:** Reusable kickoff brief for the remaining Phase C rubrics. Two rubrics have landed (CPI 2015 C11, PRI 2010); patterns and gotchas from those sessions are baked into the steps below. 6 rubrics remain.

**Originating convos:**

- [`../convos/20260514_cpi_2015_c11_tdd.md`](../convos/20260514_cpi_2015_c11_tdd.md) — function-per-item pattern; empirical aggregation-rule fit.
- [`../convos/20260514_pri_2010_tdd.md`](../convos/20260514_pri_2010_tdd.md) — declarative table pattern; paper-derived rollup reuse; spec-doc-to-v2 row-name drift surfaced.

**Source spec docs (one per rubric):** all under [`../../../historical/compendium-source-extracts/results/projections/`](../../../historical/compendium-source-extracts/results/projections/). One `<rubric>_projection_mapping.md` per rubric. Read it end-to-end before fixture authoring.

**Status of remaining rubrics (locked order from `RESEARCH_LOG.md`):**

| # | Rubric | Rows in v2 | Notes |
|---|--------|----------|-------|
| 3 | Sunlight 2015 | 13 (11 cross-rubric) | α form-type split, β Opheim AND-projection, "collect once, map many" annotation. |
| 4 | Newmark 2017 | 14 (8 reused, 6 new) | Load-bearing r=0.04 CPI↔PRI-disclosure correlation; index-based (sum of 19 binaries with reverse-scoring). |
| 5 | Newmark 2005 | 14 (100% reuse of 2017) | 2005 mapping falsified 2017's `contributions_from_others` parallel speculation. |
| 6 | Opheim 1991 | 14 row families / 15 in-scope items (100% reuse) | β AND-projection 2nd concrete use; 1 catch-all un-projectable. |
| 7 | HG 2007 | 38 (16 reused, 22 new — 42% reuse) | Ground-truth retrieval is `oh-statute-retrieval` sub-task — depend on Track A. |
| 8 | FOCAL 2024 | 58 (22 reused, 36 new — 37.9% reuse) | L-N 2025 Suppl File 1 weights, 1,372-cell ground truth. Lowest reuse rate. |

LobbyView 2018/2025 is NOT in this list — it's schema-coverage, not score-projection (Federal LDA only).

---

## Pre-flight (every rubric, ~30 min)

The Nori session-start workflow is already documented in `CLAUDE.md`. The rubric-specific pre-flight on top of that:

1. **Read the spec doc** [`../../../historical/compendium-source-extracts/results/projections/<rubric>_projection_mapping.md`](../../../historical/compendium-source-extracts/results/projections/). Goal: understand the rubric's per-item logic, axis assignments, and any "Open Issues" the spec author flagged.
2. **Locate the ground truth CSV(s).** Most rubrics' per-state ground truth lives under `papers/` or `docs/historical/<predecessor-branch>/results/`. PRI 2010's lives at `docs/historical/pri-2026-rescore/results/`; CPI 2015's at `docs/historical/compendium-source-extracts/results/cpi_2015_c11_per_state_scores.csv` + `papers/CPI_2015__sii_scores.csv`. Find yours via `find papers docs/historical -iname "*<rubric>*.csv"`.
3. **Cross-check spec-doc row names against the v2 TSV.** **THIS IS LOAD-BEARING** — PRI 2010's spec used `principal_report_*` / `lobbyist_report_*` while v2 has `*_spending_report_*`. Each pre-`compendium-v2-promote` spec doc may have similar drift. The check:

   ```python
   uv run python <<'PY'
   from lobby_analysis.compendium_loader import load_v2_compendium
   ids = {r['compendium_row_id'] for r in load_v2_compendium()}
   # Paste the expected row names from your rubric's spec doc here
   expected = ["row_name_1", "row_name_2", ...]
   missing = [e for e in expected if e not in ids]
   print(f"Missing: {missing}")
   PY
   ```

   If any are missing, search v2 for likely renames (`grep`, pattern-match) before writing fixtures. Document the spec-doc-to-v2 mapping in your module as a comment.
4. **Check for a surviving paper-derived rollup helper.** Look in `src/scoring/calibration.py` and the matching `docs/historical/<rubric>-calibration/` (e.g., `pri-calibration/`) for a previously-derived rollup. If the rubric had a calibration branch, the rollup helper likely survived. Port if found; rebuild from the spec doc only if not.
5. **Confirm the rubric's published columns.** Open the ground-truth CSV header. Check for: per-state score, percent, rank, letter grade, sub-aggregates if any. **PRI 2010 and CPI 2015 do NOT publish per-category letter grades** — handoff's "confirm rubric-by-rubric" pattern continues to land negative. Document if your rubric breaks the pattern.

## Architectural decision: declarative table vs function-per-item

The two completed rubrics demonstrate both patterns. Decision rule based on rubric shape:

| Rubric shape | Pattern | Why |
|---|---|---|
| Most items are pure binary cell → 0/1 passthroughs (PRI 2010: 75 of 76) | **Declarative `_ATOMIC_SPEC` table** | One `dict[item_id, (row_id, axis)]` + one dispatching helper. Adding an item is one row, no new function. See `src/lobby_analysis/projections/pri_2010.py`. |
| Items have bespoke compound logic (CPI 2015's 14 items mix Boolean, threshold, enum, compound multi-cell reads) | **Function-per-item** | Each helper carries its own logic in clear prose. See `src/lobby_analysis/projections/cpi_2015_c11.py`. |
| **Mixed** | **Hybrid** | Declarative table for the passthrough majority; named helpers for the bespoke few. Single dispatching function checks the table first, falls back to bespoke. |

Sunlight 2015's α form-type split likely needs an extra dimension on the spec table (`(item_id → row_id, axis, form_type)`) or a hybrid; commit only after reading the spec doc end-to-end.

Newmark 2017 + Newmark 2005 + Opheim 1991: high reuse (100% for the latter two), index-based (sum of binaries). Declarative table likely fits. Watch for reverse-scoring (Newmark may follow PRI's B1/B2 pattern).

HG 2007 + FOCAL 2024: larger rubrics (38 + 58 rows). Inspect the spec doc for compound logic before deciding.

## Validation-strategy decision

The validation depth ceiling is set by what ground truth is published. Three regimes seen so far:

1. **Per-state per-atomic-item published** (CPI 2015 C11: 50 × 14 = 700 cells): use it as a data-driven test parameterized over all states. Validate per-item helpers directly against truth. End-to-end aggregation tested against published per-state score within tolerance.
2. **Per-state per-sub-aggregate only** (PRI 2010: 50 × 5 disclosure-law + 50 × 8 accessibility): per-atomic-item validation is fixture-based. End-to-end is feasible at the sub-aggregate layer for axes where the sub-component-to-atomic mapping is recoverable (PRI accessibility's Q1..Q6 are atomic; Q7_raw + Q8_normalized are recoverable up to ~0.05 round-trip error). Disclosure-law side is blocked on the extraction harness until per-state cells exist; rule-based tests in `src/scoring/calibration.py` carry the validation load.
3. **No per-state ground truth** (only published as aggregate methodology): fixture-only. Rare; flag to user if you hit one.

Decide on (1), (2), or (3) for your rubric **before writing tests** so the test file's structure matches the regime.

## Standard module structure

Modules and tests follow this layout:

```
src/lobby_analysis/projections/<rubric>.py       # the projection module
tests/projections/test_<rubric>_per_item.py      # per-atomic-item tests (fixture or data-driven per regime)
tests/projections/test_<rubric>_ground_truth.py  # ground-truth CSV loader tests
tests/projections/test_<rubric>_aggregation.py   # aggregation + end-to-end + rank
```

Module shape (mirror PRI 2010 if declarative, CPI 2015 if function-per-item):

- Module docstring naming spec doc + ground truth paths.
- Constants: list of atomic IDs, axis-name constants if needed.
- Score model(s): frozen Pydantic `BaseModel` with `state`, `atomic_scores: dict[str, int]`, sub-aggregates if any, `total`, `percent`, and per-component fields. **No letter grade unless the rubric publishes per-category grades** — CPI and PRI don't.
- Per-item layer: declarative spec table OR named helpers.
- Aggregation: import from `src/scoring/calibration.py` if it has a paper-derived rollup; else implement with provenance comment pointing at the spec doc / fit script.
- Top-level: `project_<rubric>(cells, state)` returning the score model. If the rubric publishes multiple independent axes (PRI: disclosure + accessibility), use multiple top-level functions.
- Ranking: `rank_<rubric>_states(scores)` with the rubric's tie-break convention. **Default to competition (1224) ranking** — CPI and PRI both use it.
- Ground-truth loaders: `load_<rubric>_reference(repo_root)` returning USPS-keyed dict of typed sub-aggregate models. Reuse `STATE_NAME_TO_USPS` from `scoring.calibration`.

## Test structure

Per the test-driven-development skill: write all tests first, watch them fail, write minimal code to pass, refactor, re-verify.

**Per-item tests** (cardinality varies by rubric):
- Parameterize over every atomic item × {True, False, missing} for binary items.
- Q8-style typed items: parameterize over every tier.
- Items with compound logic: hand-crafted fixtures covering each branch.

**Ground-truth loader tests**: 50-state count, spot-check 2-3 specific states against the published CSV (top, bottom, middle), check sub-aggregate types.

**Aggregation tests**:
- Validation-regime 1: parameterize over all 50 states, project, compare to published with `abs(diff) <= 1.0`.
- Validation-regime 2: 50-state round-trip for the axes where it's feasible (recover atomic from sub-aggregate); wiring tests on hand-crafted fixtures exercising every code path; **document the validation gap** for axes without per-atomic-item truth.
- Validation-regime 3: fixture-only end-to-end tests; document why.
- Rank test: project 50-state ranks, compare to published rank column.

## Common rubric patterns (cheat sheet)

Patterns seen across CPI + PRI; expect to encounter most of these in the remaining 6 rubrics:

- **Binary cell → 0/1.** `bool(cell.get(axis))`. Most common.
- **5-tier cell → 0/25/50/75/100 passthrough.** `int(cell.get(axis) or 0)`. Common in de facto items.
- **3-tier cell → 0/50/100 enum.** Dict-lookup `{YES: 100, MODERATE: 50, NO: 0}` with case-insensitive match; map anything else to 0 (the CPI fallback convention).
- **Typed cell → integer passthrough.** PRI Q8 (0..15); rollup divides at sub-aggregate layer.
- **Compound 3-tier.** Multi-cell read with branching (CPI IND_201: required + itemized + compensation → 100/50/0). Each branch deserves a fixture test.
- **Threshold-based 3-tier.** CPI IND_197: `threshold == 0 → 100`, `threshold > 0 → 50`, `None → 0`.
- **Reverse-scoring at the rollup layer** (PRI B1/B2). Per-item helper returns literal 0/1; rollup applies `(1 - x)`. **Do not reverse in the per-item helper** — it muddles the rubric's semantics.
- **AND-projection over multiple cells.** Sunlight 2015's β convention with Opheim 1991. Helper reads N cells, returns 1 only if all are True. Common shape: per-item helper returns `1 if all(cell[i] for i in cells_to_AND) else 0`.
- **Form-type partition.** Sunlight 2015's α convention. Different rules apply to different form types (registration vs activity report); spec table needs an extra dimension or per-form-type sub-spec.
- **"Collect once, map many".** Sunlight 2015's γ convention. One compendium cell serves multiple rubric items; per-item helpers can share a cell-read.
- **Catch-all un-projectable** (Opheim 1991). Rubric carries items that don't map cleanly to compendium cells; document and skip in projection. Note the rubric's published score may still be reachable from the projectable subset.

## Per-rubric specifics

Detail beyond the table at the top:

### Sunlight 2015 (rubric #3, next)

- 13 rows in v2; 11 cross-rubric (the most cross-rubric overlap of any single rubric).
- Three locked conventions to internalize before coding:
  - **α form-type split.** Sunlight scores per form type (e.g., registration vs expenditure report) separately. The compendium row is one cell; the rubric reads it under different form-type contexts. Likely needs `(item_id → row, axis, form_type)` spec dimension.
  - **β Opheim AND-projection.** Some Sunlight items collapse multiple compendium cells via AND. Per-item helper returns 1 only if every named cell is True.
  - **"Collect once, map many".** A single compendium cell may serve multiple Sunlight items (cross-rubric reuse is high). Per-item helpers can share cell-reads; no duplication of cell extraction needed.
- Spec doc: `docs/historical/compendium-source-extracts/results/projections/sunlight_2015_projection_mapping.md`.
- Ground truth: search `papers/` for a Sunlight 2015 CSV; if not directly published, the spec doc should name the source.
- Letter grade: confirm from CSV header. Probable: no.

### Newmark 2017 (rubric #4)

- 14 rows in v2; 8 reused, 6 new (vs CPI/PRI mappings).
- Index-based: sum of 19 binary items per state, range 7-19, mean 12.96, SD 2.63, alpha 0.67.
- **Reverse-scoring possible** (Newmark may follow PRI's B1/B2 pattern for exemptions; check the spec doc).
- Load-bearing role: this is the rubric carrying the **r=0.04 CPI↔PRI-disclosure correlation** that anchors the project's "no single rubric privileged" thesis. The correlation itself is between **published rubric scores**, not between projections — so the projection just needs to reproduce Newmark's published score within ±1; the correlation is downstream.
- Spec doc + paper text: `docs/historical/.../newmark_2017_projection_mapping.md` + `papers/text/Newmark_2017__lobbying_regulation_index.txt`.
- Newmark 2017 sourcing nit per pre-merge audit: the parenthetical "0.71" comparator in the paper is sourced from Newmark 2005, not 2017 — irrelevant to the projection but note it if cited.

### Newmark 2005 (rubric #5)

- 14 rows; **100% reuse of Newmark 2017 mappings** per the 2026-05-13 row-freeze decisions.
- The 2005 mapping falsified the 2017 mapping's `contributions_from_others` parallel speculation; the merged v2 row reflects 2005's narrower reading.
- Likely a near-clone of Newmark 2017's projection module — consider extracting a shared helper.

### Opheim 1991 (rubric #6)

- 14 row families / 15 in-scope items; **100% reuse** of cross-rubric rows.
- **β AND-projection's 2nd concrete use** (after Sunlight 2015's first). If the projection pattern is general (per-rubric helper takes a list of cells to AND), the Sunlight 2015 implementation should produce a reusable shape.
- **1 catch-all un-projectable item** — Opheim has an aggregate "does the state's lobbying regime function well" judgment that doesn't map to a single compendium cell. Document and skip.
- **Weak-inequality tolerance**: Opheim's published per-state scores may be slightly out of range from projection (the rubric is old and the underlying compendium has evolved); use a `<=` tolerance check.

### HG 2007 (rubric #7)

- 38 rows; 16 reused, 22 new (42% reuse).
- **Ground-truth retrieval depends on `oh-statute-retrieval` (Track A).** Check that branch's status before starting; if Track A's HG sub-task isn't complete, the per-state ground truth may not exist locally. Surface this to user before fixture authoring.
- HG ground-truth retrieval was identified as Track A's sub-task in the row-freeze handoff because HG's published data is on physical-page-only state-by-state, requires extraction from scanned PDF — a separate retrieval pipeline.

### FOCAL 2024 (rubric #8, last)

- 58 rows post-FOCAL-1 expansion; 22 reused, 36 new (37.9% reuse — lowest of any rubric).
- **L-N 2025 Suppl File 1 weights** are 1,372-cell ground truth at compendium-cell granularity. This is the highest-density per-rubric ground truth in Phase C.
- US LDA score is 81/182 = 45% per the L-N 2025 supplement; mirror that for Federal coverage if relevant.
- Likely needs its own per-state ground truth processing because L-N 2025 publishes weighted scores rather than raw 0/1 per item.

## Phase 3 retirements

Each rubric session may surface PRI-MVP-style code that's now superseded. The pattern (from PRI 2010's session):

1. `git mv <stale_file>.py <parent_dir>/_deprecated/<stale_file>.py` — **mv, not rm**, per the research-artifacts memory note.
2. Add a SUPERSEDED banner to the module's docstring (date + reason + pointer to the new code).
3. If the stale file has tests, move them too. Update import paths.
4. Ensure pytest excludes `_deprecated/` from default collection (already configured in `pyproject.toml` post-PRI session: `norecursedirs = ["_deprecated"]`).
5. Remove the stale entry-point from any CLI / orchestrator wiring.
6. Run the full test suite to confirm no regressions.

## Phase 4 cross-rubric agreement audit

Deferred until ≥3 projection modules exist. With CPI 2015 + PRI 2010 + (e.g.) Sunlight 2015, the audit shape is:

- For each compendium row that's read by ≥2 rubric projections, project a sample of states' cells through all consuming rubrics.
- Verify the per-rubric atomic-item answers agree (e.g., if CPI's IND_201 and PRI's E1f_iv both read `principal_spending_report_uses_itemized_format`, they should both produce 1 when the cell is True).
- Where they disagree by design (e.g., CPI uses tier-based; PRI uses binary), document the projection-layer transformation that resolves the disagreement.

Output: `tests/projections/test_cross_rubric_agreement.py` + a results doc in `results/`.

## Open questions across the remaining rubrics

- **Cross-rubric typed-cell representation.** PRI 2010 surfaced one cross-rubric typed-cell row (`lobbyist_spending_report_includes_total_compensation` — 8 rubrics read it). The compendium currently carries it as binary; PRI / CPI / Sunlight / HG / FOCAL all read it as binary. If any future rubric needs a typed (numeric / enum) read on the same row, the compendium contract may need a typed-cell upgrade — surface to user before introducing a parallel row.
- **Reverse-scoring conventions across rubrics.** PRI reverse-scores B1/B2 at the rollup layer. Newmark / Opheim may have analogous patterns. Establish a convention: reverse-score lives in the rollup, NOT in the per-item helper, so the per-item helper preserves the rubric's literal semantics.
- **Aggregation-rule fitting.** CPI 2015 required empirical aggregation-rule fit (4 candidates evaluated; sub-cat means won). PRI 2010 had a paper-derived rule. Future rubrics may need fitting if their published methodology is silent. Reuse the CPI fit-script pattern (closed-form candidate aggregators + 50-state residual table) when needed.
- **Letter-grade pattern.** CPI 2015 and PRI 2010 do not publish per-category letter grades. The kickoff plan's per-category letter-grade scope was wrong for those two. Continue confirming per rubric; flag if any rubric breaks the pattern.

## When to depart from this playbook

These cases are real reasons to deviate; surface to user before doing so:

- The rubric's spec doc has unresolved Open Issues that block fixture authoring (e.g., undefined aggregation rule, missing per-item ground truth, ambiguous reverse-scoring direction).
- The compendium contract changes mid-session (extraction-harness-brainstorm ships v2 Pydantic models that supersede the raw-dict cells shape).
- A pre-flight cross-check reveals >10% of expected v2 rows are missing or significantly renamed — this is a Phase B spec-doc-vs-v2 issue that needs resolution before projection work.
- The validation regime is (3) "no per-state ground truth" — fixture-only validation is weak; surface and let user decide whether to proceed.

## Closing the loop on each rubric

End-of-session checklist (per finish-convo + update-docs skills):

1. Convo file at `convos/YYYYMMDD_<rubric>_tdd.md` — Summary, Topics, Findings, Decisions, Results, Open Questions, Next Session.
2. Results doc at `results/YYYYMMDD_<rubric>_projection.md` — what landed, validation outcome, naming-drift corrections, items skipped per YAGNI.
3. RESEARCH_LOG.md entry (newest first) — links to convo + results, topics, findings, decisions, next steps.
4. STATUS.md — append one-liner to "Recent Sessions"; update the phase-c-projection-tdd row in the active table to reflect rubric #N complete.
5. README.md — only update if the session retired code visible at the README level (e.g., PRI 2010 session updated the smr_projection retirement line).
6. Commit + push. Commit message format: `convo: <convo-name> — <rubric>: <one-line summary>`.
