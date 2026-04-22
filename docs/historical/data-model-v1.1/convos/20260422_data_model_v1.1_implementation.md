# data-model v1.1 — Implementation

**Date:** 2026-04-22
**Branch:** data-model-v1.1

## Summary

Picked up the v1.1 gap-closure work from the TDD handoff that was staged on this branch (red tests in `tests/test_models_v1_1.py`, plan in `plans/20260422_v1.1_gap_closures.md`). Implementation agent had no prior convo memory — the plan + tests were the entire contract.

Implemented all five gaps per the plan, migrated the existing v1.0 test suite to the new `framework_references` shape, and got the full suite green in one red→green iteration. No plan changes surfaced during implementation; the tests were a clean spec.

## Topics Explored

- RED confirmation: initial pytest run failed at collection on `ImportError: cannot import name 'CompendiumItem' from 'lobby_analysis.models'` — correct failure mode per plan.
- Shell-env hiccup: the session started with `VIRTUAL_ENV` inherited from another worktree (`pri-2026-rescore`). `source .venv/bin/activate` did not override it reliably; `VIRTUAL_ENV=<worktree>/.venv uv run --active pytest` was the clean form.
- Pydantic v2 behavior around unknown-field rejection: default is silent-ignore. The plan's "reject old `pri_item_id` / `focal_indicator_id` / `pri_item_ids`" requirement needed `model_config = ConfigDict(extra="forbid")` on the three migrating models — otherwise pydantic would accept the legacy kwargs silently and the red tests for those cases would pass for the wrong reason.
- Scope check: `extra="forbid"` applied only to the three migrating models (FieldRequirement, RegistrationRequirement, ReportingPartyRequirement). New models (CompendiumItem, MatrixCell, ExtractionCapability) left with pydantic default (`extra="ignore"`) — no tests require them to forbid extras, and the YAGNI principle applies.

## Provisional Findings

- The v1.1 plan was a clean TDD handoff. No ambiguity surfaced, no plan updates needed. Tests are the contract; implementation mechanical.
- Five gap closures implemented exactly as specified (Gap 1: availability axes; Gap 2: framework_references migration; Gap 3: evidence_source; Gap 4: compendium.py; Gap 5: pipeline.py).
- Existing v1.0 test migration was surgical — three `TestStateMasterRecord` tests used `pri_item_id=`; swapped for `framework_references=[FrameworkReference(framework="pri_2010_disclosure", item_id=...)]`.

## Decisions Made

- **`extra="forbid"` scope limited to the three migrating models.** New v1.1 models stay at pydantic default. Revisit in a future minor if fellows start putting typo'd fields through CompendiumItem and we want hard validation.
- **All open questions in the plan deferred to post-implementation user review** — none of them forced a divergence:
  - Q1 (RegistrationRequirement.evidence_source): skipped, per plan recommendation.
  - Q2 (MatrixCell location): kept in `compendium.py`, per plan.
  - Q3 (PortalTier granularity): six values ship as specced.
  - Q4 (list vs dict for framework_references): list, per plan.
  - Q5 (structured metadata on `"other"` framework): skipped; `item_text` remains the escape hatch.

## Results

Full suite green: **128 passed in 0.16s**. Breakdown:

- `tests/test_models.py` — 24 passed (existing v1.0 tests, three `TestStateMasterRecord` cases migrated to `framework_references`)
- `tests/test_models_v1_1.py` — 95 passed (all red tests now green)
- Other test modules — 9 passed (untouched scoring infra)

No results files produced — this session is pure code + test implementation.

## Files Touched

**Modified:**
- `src/lobby_analysis/models/state_master.py` — added `FrameworkId`, `FrameworkReference`, `LegalAvailability`, `PracticalAvailability`, `EvidenceSource` aliases; added `framework_references` + availability/evidence fields to `FieldRequirement`; added `framework_references` to `RegistrationRequirement` + `ReportingPartyRequirement`; dropped `pri_item_id` / `focal_indicator_id` / `pri_item_ids`; added `ConfigDict(extra="forbid")` to the three migrating models.
- `src/lobby_analysis/models/__init__.py` — exports for new types.
- `tests/test_models.py` — migrated three `TestStateMasterRecord` tests from `pri_item_id=` kwargs to `framework_references=[FrameworkReference(...)]`.

**Created:**
- `src/lobby_analysis/models/compendium.py` — `CompendiumItem`, `MatrixCell`, `CompendiumDomain`, `CompendiumDataType`.
- `src/lobby_analysis/models/pipeline.py` — `ExtractionCapability`, `PortalTier`, `PipelineCadence`.

**Not touched:** `entities.py`, `filings.py`, `provenance.py`, `tests/test_pipeline.py`, `src/scoring/`, `docs/historical/lobbying-data-model/` (per plan).

## Open Questions

- **STATUS.md Active Research Lines row not added on this branch.** Per plan's "Update STATUS.md on main via PR", the Active Research Lines row gets added when the branch lands. This session appended only a Recent Sessions one-liner locally; the branch row will come with the merge PR.
- **v1.1 schema change not yet broadcast to the other two fellows** doing extraction rollout. Not this branch's job — user decides when to merge + communicate.
- **No "other" framework-usage guidance** in any compendium items yet. The enum value exists; real usage will surface whether the denormalized `item_text` convention is enough.

## Next Steps

- Wait on Dan's review of the diff.
- If approved → merge to main (not done here; Dan-only action per CLAUDE.md); add Active Research Lines archive row in the merge PR.
- Post-merge, someone can start populating actual `CompendiumItem` records from the compendium sources in `PAPER_SUMMARIES.md`.
