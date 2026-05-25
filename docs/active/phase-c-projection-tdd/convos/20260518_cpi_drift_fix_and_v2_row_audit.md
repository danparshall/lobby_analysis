# 20260518 — CPI 2015 drift fix + v2 row-reference audit

**Date:** 2026-05-18
**Branch:** `phase-c-projection-tdd`
**Closes:** [GH #17](https://github.com/danparshall/lobby_analysis/issues/17)
**Predecessor convo:** [`20260518_sunlight_2015_projection_tdd.md`](20260518_sunlight_2015_projection_tdd.md) — the Sunlight TDD session that surfaced the IND_201 drift and filed it as #17.

## Summary

Picked up the recommended next-step from the Sunlight session ("(d) fix CPI drift first — small, surgical, unblocks Phase 4 prototyping"). Issue #17 named one row reference to fix at CPI 2015 IND_201; the audit test the issue *also* proposed found a second instance at IND_200. Both fixed in this session along with a syntactic AST-based audit (`tests/test_v2_row_references_exist.py`) that's now load-bearing against the class of bug.

Sequence:
1. Verified issue #17's claims against the live v2 TSV — 6 reference sites for IND_201's bad name, all matching the issue exactly; `lobbyist_spending_report_includes_total_compensation` confirmed at line 138.
2. Applied the surgical IND_201 rename (1 prod + 5 test sites).
3. Wrote a first-pass audit (shape-based detection of row-name-shaped string literals). It correctly flagged IND_200's reference to a merged-away row + 4 false-positive matches on enum values (`cadence in (...)` and `rule == "..."` comparisons).
4. User locked: fix IND_200 here too, **and** rewrite audit with syntactic detection.
5. First IND_200 rename used the wrong v2 row name (`registration_deadline_days_after_first_lobbying` — from the historical mapping doc); the audit caught it and surfaced that the actual v2 row is `lobbyist_registration_deadline_days_after_first_lobbying` (line 178 of v2 TSV). Corrected.
6. Rewrote audit with syntactic AST detection (call sites + subscripts + tuple-register patterns + module-level `_FOO_ROW`/`_FOO_ROWS` constants). Plus a sentinel-name exclusion (`__`-prefixed) for the IND_205 round-trip escape hatch (`__ind_205_partial_credit_passthrough` — deliberate test-only key, never a v2 row).

End state: 73/73 CPI projection tests pass, 1/1 audit test passes, 927/930 full-suite pass (3 pre-existing `test_pipeline.py` FileNotFoundError failures on the gitignored `data/portal_snapshots/CA/2026-04-13/manifest.json` — identical to main; this worktree has no `data/` symlink at all).

## Topics Explored

- **Verification before code change.** Confirmed issue #17's claims with both `grep` and the loader: bad name absent from v2 TSV, good name present at line 138 (the 8-rubric mega-row used by cpi/pri/sunlight/newmark×2/opheim/hg/focal). 6 reference sites match the issue exactly.
- **Audit design forks.**
  - First pass: **shape-based** — collect every string literal in projection modules whose regex matches a row-name shape (`^[a-z][a-z0-9_]+$`, len≥20, ≥2 underscores). Simple; admits enum values as false positives.
  - Second pass: **syntactic** — only flag strings in row-name-consuming AST positions (`_legal(cells, X)`, `_practical(cells, X)`, `cells[X]`, tuple-register `("ID", X, _LEGAL|_PRACTICAL)`). Plus module-level constants whose name ends in `_ROW`/`_ROWS`. ~50 LOC more; zero false positives.
- **Second instance of the same drift class at IND_200.** The shape-based first pass surfaced this immediately. `project_ind_200` was reading `registration_timeliness_after_first_lobbying_activity` (the historical practical-axis row name) — but the row-freeze's Decision D11 merged the legal + practical axes into a single two-axis row `lobbyist_registration_deadline_days_after_first_lobbying`. Same fixture-drift pattern as IND_201: the tests passed because the test fixtures also used the stale name. Verified against the historical mapping doc at `docs/historical/compendium-source-extracts/results/projections/cpi_2015_c11_projection_mapping.md:115` + Decision D11 at `20260513_row_freeze_decisions.md:183`.
- **My own first-pass error on IND_200's correct v2 name.** Trusted the historical mapping doc, which used the unprefixed `registration_deadline_days_after_first_lobbying`. The actual v2 row carries the `lobbyist_` prefix. The audit caught it on the next run — exactly the failure mode the audit is built to surface, and the cycle (original buggy → wrong fix → audit catches → correct fix → green) is good evidence the audit works end-to-end.
- **Synthetic sentinel keys.** IND_205 reads `_practical(cells, "__ind_205_partial_credit_passthrough")` as a deliberate round-trip escape hatch (documented in the projection's docstring as "carried on the `__ind_205_partial_credit_passthrough` key for round-trip"). The `__`-prefix convention marks it as intentionally non-canonical; no v2 row name starts with `__`. Excluded in the audit via `_is_synthetic_sentinel(name)`.
- **3 pre-existing pipeline failures.** Confirmed by stash-and-retest: `git stash` (reverting my changes) → `test_pipeline.py` still fails 3/9 with the same FileNotFoundError on `data/portal_snapshots/CA/2026-04-13/manifest.json`. The worktree has no `data/` symlink at all (per `docs/active/phase-c-projection-tdd/RESEARCH_LOG.md:33-35` — "skipped at branch creation because projections are pure code"). Out of scope for #17; not introduced here.

## Provisional Findings

- **Audit is load-bearing.** It already paid for itself before commit: caught a second drift instance the issue didn't name, then caught my own wrong-rename. Both surfaced from end-state-detection (not from prior knowledge), which is the right test of whether the audit replaces the load-bearing review.
- **Syntactic detection is the right model for this audit.** Shape-based has irreducible false positives because v2 row names and v2 enum values share lexical shape (lowercase snake_case strings of similar length). Syntactic detection by AST position cleanly separates them and is robust to new accessors as long as they follow the `(cells, row_id, ...)` convention.
- **The audit's scope (projection-side only) is appropriate.** Test-side fixture drift surfaced here was caught only because the projection-side fix forced the test fixtures to be updated in lockstep; otherwise tests would have started failing. A test-side audit would need a stricter detection (e.g., only `cells[...]` subscripts in test files), since tests have many legitimate non-row strings. Punted to follow-up if more surface.
- **Row-freeze decisions D1–D30 are the canonical reference, not the per-rubric mapping docs.** The historical mapping docs predate the freeze and use earlier candidate row names. When checking what a current v2 row name is, the v2 TSV is the source of truth; mapping docs are background. Burnt-finger lesson from the IND_200 wrong-rename above.

## Decisions Made

- **Fix both IND_200 and IND_201 in this PR.** Issue #17 named IND_201; the audit surfaced IND_200 as the same drift class. Per user direction, both fixed here rather than split into a follow-up. Issue #17 will be updated/closed with both fixes noted.
- **Audit uses syntactic AST detection** with sentinel-prefix exclusion. Detection patterns:
  - Call-site: `_legal(cells, X)`, `_practical(cells, X)` — X is a `Constant[str]` or a `Name` resolving to a module-level row constant.
  - Subscript: `cells[X]` — same.
  - Tuple-register: `("ID", X, _LEGAL|_PRACTICAL)` — middle string when third element is a `Name` from `_ROW_AXIS_CONSTS`.
  - Module-level constants: `_FOO_ROW: Final[str] = "..."` and `_FOO_ROWS: Final[tuple[str, ...]] = (...)` harvested directly; catches the for-loop iteration pattern in `sunlight_2015.py`.
  - Sentinel exclusion: names starting with `__` are deliberate non-canonical test-only keys (current sole instance: `__ind_205_partial_credit_passthrough`).
- **Did NOT touch test-side audit scope.** Per user's chosen scope ("src-only"). If a future test-side bug surfaces, expand then.
- **Did NOT fix the 3 pre-existing `test_pipeline.py` failures.** Out of scope; require `data/` symlink + snapshot file plumbing that's a different problem class.

## Results

No standalone results files. The audit itself + the convo are the artifacts.

## Code changes (this session)

| File | Change |
|---|---|
| `src/lobby_analysis/projections/cpi_2015_c11.py` | IND_201 row name fix (line 200): `lobbyist_spending_report_includes_compensation` → `lobbyist_spending_report_includes_total_compensation`. IND_200 row name fix (line 184): `registration_timeliness_after_first_lobbying_activity` → `lobbyist_registration_deadline_days_after_first_lobbying`. |
| `tests/projections/test_cpi_2015_c11_per_item.py` | 4 IND_201 fixture sites + 3 IND_200 fixture sites (3-tuple value, parametrized fixture, row-name register, header comment). |
| `tests/projections/test_cpi_2015_c11_aggregation.py` | 1 IND_201 + 1 IND_200 round-trip-builder site. |
| `tests/test_v2_row_references_exist.py` | **NEW** — syntactic AST audit (~170 LOC including module docstring). Asserts every row name referenced in `src/lobby_analysis/projections/*.py` exists in the live v2 TSV. |

## Tests state

- `tests/projections/test_cpi_2015_c11_per_item.py`: 73/73 pass (no count change).
- `tests/projections/test_cpi_2015_c11_aggregation.py`: included in 73 above.
- `tests/test_v2_row_references_exist.py`: 1/1 pass (NEW).
- Full pytest: 927/930 pass; 3 pre-existing failures unrelated (FileNotFoundError on missing portal snapshot data in `data/` — no `data/` symlink in this worktree, identical to main per `STATUS.md` line 91 history entry).

## Open Questions

- **Should the audit also cover the `tests/` tree?** A future test-side audit would catch fixture drift directly, rather than waiting for it to surface via a projection-side bug. Detection needs to be stricter than projection-side (tests have many legitimate non-row snake_case strings, e.g., parametrize IDs); probably restrict to `cells[...]` subscript keys. Punted under YAGNI; revisit if more drift surfaces.
- **Should the row-freeze decision log be machine-readable?** The freeze's 30 decisions (D1–D30) carry the rename/merge map that the renamer can't infer. A structured representation would let the audit display "row X was merged away by Dn" rather than just "absent from v2." Out of scope for #17.
- **`data/` symlink for this worktree.** The branch was created without one (per RESEARCH_LOG line 33–35 — "skipped at branch creation"). Three `test_pipeline.py` tests need it. The user note there is "likely no gitignored data needed at all for this branch" — but those 3 tests now require it. Not a session-blocker; surfacing here so the user can decide.

## Captured Tasks

(No new tasks captured this session.)

## Commits this session

| Commit | What |
|---|---|
| (pending) | CPI 2015: rename IND_200 + IND_201 row references to v2 names; add tests/test_v2_row_references_exist.py syntactic audit. Closes #17. |
