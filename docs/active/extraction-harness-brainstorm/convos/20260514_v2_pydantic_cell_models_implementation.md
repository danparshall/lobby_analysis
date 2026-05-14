# v2 Pydantic cell models — implementation (Phases 0-9)

**Date:** 2026-05-14
**Branch:** extraction-harness-brainstorm
**Plan executed:** [`../plans/20260514_v2_pydantic_cell_models_implementation_plan.md`](../plans/20260514_v2_pydantic_cell_models_implementation_plan.md)
**Originating brainstorm:** [`20260514_extraction_harness_brainstorm.md`](20260514_extraction_harness_brainstorm.md) (Q0–Q6 architectural decisions)

## Summary

Executed Phases 0-9 of the v2 Pydantic cell models implementation plan under strict TDD. Wrote all 68 tests first (RED), watched them fail with `ModuleNotFoundError`, then implemented phase by phase (GREEN, one commit per phase) until the full test suite is green at +68 / 0 new failures (374 pass / 5 skip / 3 pre-existing failures = same baseline + new tests).

The v2 typed cell model layer (`src/lobby_analysis/models_v2/`) is now live alongside v1.1 (`src/lobby_analysis/models/`), with the canonical 186-entry `CompendiumCellSpec` registry mapped from the real `compendium/disclosure_side_compendium_items_v2.tsv`. Phase C's projection functions and this branch's downstream LLM-calling harness can both consume `dict[tuple[row_id, axis], CompendiumCell]` as the typed contract; `load_v2_compendium()` (raw dicts) remains the unchanged contract for callers that don't want types yet.

## Topics Explored

- **Pre-flight discipline:** Read the using-skills, test-driven-development, finish-convo, and update-docs skills. Spot-checked the link graph (RESEARCH_LOG ↔ convos ↔ plans ↔ STATUS) before any code; found one false-alarm "missing predecessor plan" path that turned out to be a too-narrow regex match.
- **TSV inspection** (`/tmp/inspect_v2_tsv.py`) catalogued the 181 TSV rows × 23 distinct `cell_type` values × 3 axis values (126 legal + 50 practical + 5 legal+practical). The plan's "29 distinct cell_types" claim was off; actual is 23 — doesn't change anything substantive since the parser is data-driven.
- **Specialized cell struct-shape resolution:** The handoff said to read each specialized row's `notes` column. The `notes` column turned out NOT to carry struct shape for any of the 6 specialized cells — it carries provenance only (e.g. `'single-rubric (focal_2024)'`) or is empty (`UpdateCadenceCell`, `TimeThresholdCell`). Struct shapes live instead in the source-rubric projection mappings under `docs/historical/compendium-source-extracts/results/projections/`. Surfaced all 6 to user with proposed shapes + sources; user approved all 6 as proposed.
- **Unanticipated 7th cell_type** (`typed Optional[int_months] (or enum)` for `lobbyist_registration_renewal_cadence`): not catalogued in the plan. Mapped to existing `IntCell` per user-approved YAGNI principle (the "months" semantic is documentation, the type stays `int | None`).
- **Pre-existing CI failures:** Baseline pytest had 3 failures in `tests/test_pipeline.py` (`FileNotFoundError` on portal-snapshot fixture data missing from this worktree). Identical to main and to the previous v2-promote session. User approved leaving them rather than fixing — fixing requires the gitignored `data/scores/` from the paused `statute-extraction` branch, which is out of scope here.

## Provisional Findings

- **TDD discipline yielded a clean signal at each phase.** Each phase's implementation commit turned exactly its own tests green; cumulative pass count rose monotonically (7 → 30 → 44 → 57 → 62 → 64 over phases 2-7).
- **The brainstorm convo's "Anthropic SDK not added" decision held.** The cell model layer is pure-data; no LLM-calling component touched. Phase C and the downstream harness can both consume the typed contract via Python imports — no SDK dependency surface introduced.
- **The 5 combined-axis rows parse cleanly via a generic split parser** — no per-row hard-coding. Adding a 6th combined-axis row in the future requires only its `cell_type` halves to be in `_CELL_TYPE_PARSER` and the parametrized test list to grow.
- **The 8-rubric anchor row** (`lobbyist_spending_report_includes_total_compensation`) maps correctly to `BinaryCell` at axis `legal` — the most-validated row across the rubric set is wired right.
- **The registry-build process is the orphan-check.** Calling `build_cell_spec_registry()` against the real TSV implicitly verifies every distinct `cell_type` has a parser entry — if a future TSV row adds a new `cell_type` without a parser update, the build raises `KeyError` with a precise diagnostic.

## Decisions Made

- **Specialized cell struct shapes** (user-approved 2026-05-14 from source-rubric mappings):
  - `UpdateCadenceCell.value: Literal["daily", "weekly", "monthly", "semiannual_or_less_often", "none"] | None`
  - `TimeThresholdCell.{magnitude: Decimal | None, unit: Literal["hours_per_quarter", "hours_per_year", "days_per_year", "percent_of_work_time"] | None}`
  - `TimeSpentCell.{magnitude, unit}` — same shape as `TimeThresholdCell`
  - `SectorClassificationCell.value: str | None` — open string (LDA/NAICS/ad-hoc all observed)
  - `CountWithFTECell.{count: int | None, fte: float | None}`
  - `EnumSetWithAmountsCell.{value: frozenset[Literal["government_agency", "foundation", "company", "individual", "other"]], amounts: dict[str, Decimal]}`
- **`lobbyist_registration_renewal_cadence` maps to `IntCell`** (not a new `RenewalCadenceCell`). YAGNI.
- **Pre-existing `test_pipeline.py` failures left as-is** for the second session in a row; documented in this convo's Topics Explored.
- **`frozen=True` on all cells** matches iter-1's stamped-output discipline; if iter-2-style "update confidence after second-pass review" turns out to be a real workflow, drop frozen then.

## Results

This session produced code, not analytical outputs — no files in `results/`. The deliverable is the `models_v2/` module surface itself; its contract is the public exports in `src/lobby_analysis/models_v2/__init__.py` and the 186-entry registry returned by `build_cell_spec_registry()`.

## Commits this session (oldest first)

| SHA | Message |
|-----|---------|
| `62daee7` | scaffolding: empty models_v2 module |
| `44eee71` | tests (RED): full test suite for models_v2 layer |
| `de507f3` | models_v2: EvidenceSpan provenance struct |
| `e3de953` | models_v2: CompendiumCell ABC + BinaryCell |
| `5cac6bc` | models_v2: numeric cell subclasses (Decimal, Int, Float, GradedInt, BoundedInt) |
| `ea6faf5` | models_v2: enum/free-text + 6 specialized cell subclasses |
| `0e1ed2a` | models_v2: CompendiumCellSpec + 186-cell registry |
| `7c882b1` | models_v2: StateVintageExtraction container + ExtractionRun provenance |
| `368cc21` | models_v2: __init__ exports + load_v2_compendium_typed wrapper |
| `c66d808` | models_v2: ruff format pass |

## Open Questions

- **Per-cell enum domain registries.** `enum_domains.py` was sketched in the plan but not implemented this session — no row was blocked by missing it (the bare `EnumCell(value: str)` accepts any non-empty string). When the LLM-calling harness lands and a row's enum needs validation, populate the domain at that point.
- **Whether `StateVintageExtraction` should embed `ExtractionRun` instead of running parallel.** Plan flagged as TBD; left parallel. Revisit when the harness writes its first persistence layer.
- **Whether `EvidenceSpan.section_reference` should be a structured tuple** rather than a string. Plan flagged as TBD; left as `str`. Revisit when retrieval bundle structure is known and the LLM-calling harness needs to emit citations.
- **`compendium/README.md`'s projection-input phrasing** (`{row_id: typed_value}`) is now structurally inaccurate under the Q0 `(row_id, axis)` decision. Flagged by the brainstorm convo as a coordination item; not addressed this session.

## Next session

The plan's "Out of scope" list names downstream components that now build cleanly on this session's output:

1. **Chunk-grouping function** — partitions the 186-cell roster into prompt-sized groups for the harness. Needs the `CompendiumCellSpec` registry (done).
2. **Brief-writer module** for the LLM-calling harness. Builds on cells + chunks.
3. **Cross-reference retrieval agent's v2 generalization.** Builds on `src/scoring/retrieval_agent_prompt.md` (existing v1 surface).
4. **Scorer prompt rewrite** (rubric-agnostic, v2-compendium-shaped). Builds on cells + chunks + retrieval bundle.

Each of these is its own brainstorm + TDD plan + implementation cycle. Pick one and start with a brainstorm session.

Also: when first LLM-calling work lands, decide on the Anthropic SDK dependency (currently NOT in `pyproject.toml`; iter-1 used Claude Code subagent dispatch).
