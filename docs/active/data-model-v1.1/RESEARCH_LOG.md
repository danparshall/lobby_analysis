# Research Log: data-model-v1.1

Created: 2026-04-22
Purpose: Close gaps in `lobbying-data-model` v1.0 (accepted 2026-04-21, archived) surfaced during the 2026-04-22 landscape brainstorm on the `pri-calibration` branch.

Cut from `main` (where v1.0 lives). v1.0 is unfrozen by Dan for this work — specifically safe because no live v1.0 artifacts exist yet (fellows haven't populated StateMasterRecords). Clean-break migration is therefore low-risk.

This branch's scope is **tests + plan only** until another agent implements. The plan is self-contained for a fresh-context agent.

## Trajectory

Newest first.

- **2026-04-22** — Branch created from main HEAD `2afe77f4`. Plan written (`plans/20260422_v1.1_gap_closures.md`) capturing five gap buckets and proposed code shapes. TDD tests written in `tests/test_models_v1_1.py` — all expected to fail until implementation. Implementation deferred to next agent; plan is a self-contained handoff. No code files (`src/`) touched on this branch yet.

## Architectural pivots that motivated v1.1

From the 2026-04-22 landscape brainstorm (convo summary to be filed on `pri-calibration` at session end):

1. **Project identity clarified** as "publish N × 50 × 2 matrix of Required × {Legally Available, Practically Available} across 50 states" — the field-level compendium is the primary artifact, not a unified scoring rubric. The compendium unions PRI 2010, FOCAL 2024/2026, CPI Hired Guns 2007, Newmark 2005/2017, Opheim 1991, Sunlight 2015, OpenSecrets 2022, and federal LDA.
2. **4-axis framing locked:** (a) Required, (b) Legally Available, (c) Practically Available, (d) [Compliance and Enforcement — out of scope for this project]. Compliance and enforcement are explicitly downstream consumer tasks enabled by our data, not done by us.
3. **Data model must be framework-agnostic** (many rubrics in the compendium), not PRI + FOCAL specific. Motivates the clean-break removal of `pri_item_id` / `focal_indicator_id` in favor of a generic `framework_references` pattern.
4. **"Up-to-date" replaces "real-time"** as cadence framing. Requires surfacing per-state pipeline capability (extractable vs. unextractable fields, cadence, parse-error rate).
5. **PRI calibration pipeline stays** — but reframed as internal QA for LLM statute-reading reliability, not as a public rubric-scoring output. Not affected by v1.1 schema changes.
6. **No Corda Rubric.** Existing rubrics live in the compendium as source references; the project catalogs, it does not grade.

## Plans

- `plans/20260422_v1.1_gap_closures.md` — full gap analysis, five proposed changes with code shapes, TDD test coverage breakdown, migration notes, files to modify during implementation.

## Convos

- Originating discussion lives on `pri-calibration` branch's 2026-04-22 landscape-brainstorm convo (to be filed at session end). Key context sources: `docs/historical/lobbying-data-model/results/lobbying_data_model_spec.md` (v1.0 spec), `PAPER_SUMMARIES.md` (compendium sources).

## Results

None yet. Results of implementation will be the passing test suite + updated `src/lobby_analysis/models/` modules.
