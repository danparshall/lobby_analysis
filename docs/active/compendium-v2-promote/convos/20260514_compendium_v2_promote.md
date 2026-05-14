# Compendium v2-promote: deprecate v1, promote v2 to repo-level, clear PRI banner

**Date:** 2026-05-14
**Branch:** compendium-v2-promote

## Summary

This session opened as a coordination check between the two parallel-running compendium-consumer successor branches (`extraction-harness-brainstorm` and `phase-c-projection-tdd`, both cut 2026-05-14 off main after the `compendium-source-extracts` archive). Dan's concern: would they conflict?

Analysis showed they don't conflict on their **core deliverables** — extraction-harness produces compendium cells, phase-c-projection consumes them, and the v2 TSV row-freeze is the contract between them. But they collide on **shared infrastructure** both would naturally want to touch: v1 CSV deprecation, v2 TSV path promotion, `compendium_loader.py`, the v1.1 Pydantic models, and the STATUS.md ⛔ banner wording.

Decision: cut a small `compendium-v2-promote` branch first to land the v1→v2 deprecation work in one place before either successor edits shared infrastructure. Same session also cleared the ⛔ PRI-out-of-bounds banner — Compendium 2.0 structurally treats PRI as 1 of 8 score-projection rubrics on even footing (⭐ success criterion #4); the banner was emergency posture for a failure mode that's now structurally resolved.

Process notes (raised by Dan mid-session):

- **Nori workflow:** followed substantively (pre-flight reads, convo-name proposal, use-worktree skill read before worktree creation, TodoWrite tasks) but skipped reading `using-skills/SKILL.md` at start and skipped putting the Nori checklist itself into TodoWrite. Remediated by reading `using-skills`, `test-driven-development`, `finish-convo`, and `update-docs` skills fresh during the session.
- **TDD:** initially wrote `load_v2_compendium()` before writing tests. Remediated by reverting the implementation to a stub-returning-`[]`, writing 3 failing tests, watching them fail for the right reasons (RED), restoring the implementation, watching them pass (GREEN).

## Topics Explored

- Conflict-surface analysis between `extraction-harness-brainstorm` and `phase-c-projection-tdd`: which files would both branches touch, where they're decoupled by design (cell-dict contract), where they're coupled by infrastructure (loader, paths, models).
- Sequencing options for v1→v2 deprecation work: own branch, fold into harness, fold into phase-c, or skip-and-coordinate.
- Where the v2 TSV should live (kept the `_v2` suffix on the filename for explicit versioning; promoted from `docs/historical/...` to `compendium/`).
- How aggressive the v2 loader should be (raw `list[dict[str, str]]` returned — typed models deferred to harness branch's surgery, since model shape = extraction output shape).
- Forwarding stub for old historical TSV path (`.MOVED.md` markdown file with update instructions and a warning, rather than symlink or silent move).
- PRI banner removal: the substantive "no rubric privileged" content survives as ⭐ success criterion #4; the banner was emergency posture for the bootstrapping-from-PRI failure mode. Phase C #2 (PRI 2010 projection) literally requires reading PRI methodology — banner rule 1 was rule-blocking that work.

## Provisional Findings

- The two parallel compendium-consumer branches have natural separation (produce vs. consume) with the v2 TSV as the explicit contract — confirms the Option B sequencing decision (locked 2026-05-13) was sound at the architectural level.
- Compendium 1's structural PRI-shape is documented and recoverable — moving v1 CSVs to `_deprecated/v1/` with a README explaining why preserves it as evidence-for-rebuild, not just clutter.
- The 5 path constants flagged in STATUS.md's 2026-05-14 session entry needed updates again (4 of the same files plus the loader itself) — repeated path migrations within a week are a smell; Pydantic v2 models will trigger a third migration when harness branch lands.
- Pre-existing test failure in `test_pipeline.py` (3 tests, portal snapshot fixture data not bundled) is identical on main — not introduced by this branch, but worth flagging since it means the full pytest run isn't currently clean on main either.

## Decisions Made

- **Q1 (sequencing):** Own branch `compendium-v2-promote` cut off main; lands first; successors rebase against new main after merge.
- **Q2 (model rewrite owner):** `extraction-harness-brainstorm` owns v2 Pydantic model rewrite. Phase C consumes models as a downstream.
- **Q3 (v2 loader return):** Raw `list[dict[str, str]]`. No TypedDict, no Pydantic model. Harness branch defines typed model later.
- **Q4 (forwarding stub):** `.MOVED.md` markdown file at old historical path with new-path + update instructions + warning header.
- **PRI banner removal:** authorized; entire `## ⛔ AGENT-CRITICAL` section deleted from STATUS.md; recorded in 2026-05-14 Current Focus paragraph with reasoning.

## Concrete changes

### File moves (`git mv` — history preserved)

- `compendium/disclosure_items.csv` → `compendium/_deprecated/v1/disclosure_items.csv`
- `compendium/framework_dedup_map.csv` → `compendium/_deprecated/v1/framework_dedup_map.csv`
- `docs/historical/compendium-source-extracts/results/projections/disclosure_side_compendium_items_v2.tsv` → `compendium/disclosure_side_compendium_items_v2.tsv`

### New files

- `docs/historical/compendium-source-extracts/results/projections/disclosure_side_compendium_items_v2.MOVED.md` — forwarding stub
- `compendium/README.md` — v2 source-of-truth declaration
- `compendium/_deprecated/v1/README.md` — v1 deprecation context (cites 2026-05-02 v3 audit: 186 concerns / 109 of 141 rows flagged / 24.2% inter-auditor agreement)
- `tests/test_compendium_loader_v2.py` — 3 smoke tests (row count == 181, expected columns, canonical 8-rubric anchor row present)

### Edited code

- `src/lobby_analysis/compendium_loader.py` — renamed `load_compendium` → `load_v1_compendium_deprecated`; added `load_v2_compendium`; updated `DEFAULT_COMPENDIUM_V1_CSV` path constant + added `DEFAULT_COMPENDIUM_V2_TSV`
- `scripts/build_compendium.py` — docstring + `OUT_DIR` constant updated to point at `_deprecated/v1/`
- `src/scoring/orchestrator.py` — import alias + path constant updated
- `tests/test_compendium_loader.py` — docstring + import alias + path constants updated (`compendium/_deprecated/v1/`)
- `tests/test_smr_projection.py` — same shape of updates

### Docs

- `STATUS.md` — removed `⛔ AGENT-CRITICAL: PRI 2010 IS OUT OF BOUNDS` section wholesale (lines 7-26); added v2-promote update to 2026-05-14 Current Focus paragraph; added `compendium-v2-promote` row to Active Research Lines; updated row-freeze contract path references in `oh-statute-retrieval` / `extraction-harness-brainstorm` / `phase-c-projection-tdd` rows
- `README.md` — Project state section updated to reflect Compendium 2.0 as landed (not "in progress"); Repo layout section adds `compendium/` directory description

### Tests

- 297 baseline pass / 5 skip pre-change (excluding `test_pipeline.py`'s 3 pre-existing portal-snapshot failures)
- 300 pass / 5 skip post-change (3 new v2-loader smoke tests added)
- v1-loader regression (`test_compendium_loader.py` + `test_smr_projection.py`): 34 pass / 5 skip — same as before the rename

## Out of scope (handed to successors)

- v2-shaped Pydantic models in `src/lobby_analysis/models/` → `extraction-harness-brainstorm`
- v2-shaped extraction prompts → `extraction-harness-brainstorm`
- Retiring `cmd_build_smr` / `smr_projection` PRI-MVP code → `phase-c-projection-tdd`
- Per-rubric projection function implementations → `phase-c-projection-tdd`

## Open Questions / post-merge actions

- **Successor RESEARCH_LOG path updates** — the row-freeze-contract links inside `docs/active/extraction-harness-brainstorm/RESEARCH_LOG.md` and `docs/active/phase-c-projection-tdd/RESEARCH_LOG.md` still point at the old historical path. Those files exist only on their respective branches, so I couldn't edit them from this branch. **Action for each successor's kickoff agent:** after rebasing against the new main (post-`compendium-v2-promote` merge), update the Row-freeze contract link to `compendium/disclosure_side_compendium_items_v2.tsv` and update the carry-forward path under "Out of scope for this branch" if needed.
- **`oh-statute-retrieval`** also benefits from this v2-promotion (it'll feed extracted statute text into the v2 row contract). Same RESEARCH_LOG-link update applies.
- **Pre-existing 3 test_pipeline.py failures** are not addressed here — they require either bundling portal snapshot fixture data or restructuring those tests. Out of scope; flagged.

## Results

No analytical results produced this session — code + docs only. The new v2 smoke tests (`tests/test_compendium_loader_v2.py`) serve as the executable specification for the v2 loader contract.
