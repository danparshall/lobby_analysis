# 2026-05-01 — Harness Brainstorm Kickoff

**Branch:** `statute-extraction` (worktree: `.worktrees/statute-extraction/`)
**Status:** in progress (live convo summary)
**Predecessor branch:** `filing-schema-extraction` (merged 2026-05-01 via PR #5, archived to `docs/historical/`; v2 audit + v1.2 schema bump landed there)

## Framing (corrected mid-session 2026-05-01)

The compendium is the universe; the SMR is keyed to the compendium; rubrics are projections of the SMR, not data sources for it. **All nine past rubric scorings (PRI 2010 disclosure, PRI 2010 accessibility, FOCAL 2024, Sunlight 2015, Newmark 2005/2017, Opheim 1991, CPI Hired Guns 2007, OpenSecrets 2022) are validation signals** — none privileged. The harness's job is to populate the 108-row statute-side compendium for OH from statute text; multi-rubric agreement is a sanity check.

Two artifacts exist as diff inputs (not gates): the OH 2010 + OH 2025 PRI-projection SMR shipped on `statute-retrieval` (PR-merged 2026-04-30, archived). They illustrate the SMR shape that is correct, but their PRI-only data source is what the new harness replaces.

## Goal of this session

Resolve the seven open design questions from the kickoff plan (Q1–Q7 in the handoff) and produce a concrete OH-first MVP target before any harness code is written.

## Pre-work done before brainstorm

- Pre-flight reads: STATUS.md, README.md, docs/COMPENDIUM_AUDIT.md, kickoff plan, OH 2025/2010 diff.
- Confirmed the 141-row compendium = 108 statute-side + 33 accessibility-side from disk.
- Identified the carry-forward infrastructure: `src/scoring/{justia_client, bundle, statute_retrieval, calibration, consistency, orchestrator, smr_projection, scorer_prompt.md}` + `src/lobby_analysis/models/` (v1.2 schema with `definitions` domain).

## Skeleton refactor (commit 5537c92)

Moved `data/compendium/` → `compendium/` at repo root. The compendium is the locked contract for the harness, not gitignored runtime data. Path constants updated in `compendium_loader.py`, `build_compendium.py`, `test_compendium_loader.py`; `.gitignore` re-include removed; audit-doc references updated. 24/24 compendium tests pass.

## Open design questions (to brainstorm)

### Q1 — Subagent architecture / extraction prompt shape
Per-row, per-section, or per-bundle? The harness extracts against compendium rows that are filing-shape-distinct (not yes/no), so prior per-rubric-item subagent shapes don't transfer cleanly.

### Q2 — Qualitative materiality
§101.70(F)-type "main purposes" tests are real legal gates that are easy to silently drop. How does the harness flag and capture qualitative gates? (boolean? structured boolean+text? `requires_human_review`?)

### Q3 — Conjunctive vs disjunctive drift
Multi-field requirements ("address AND phone") need to be extracted atomically; prior runs collapsed these disjunctively under prompt drift. Atomic per-row extraction may help; verify in pilot.

### Q4 — Multi-regime parallel chapters
Some states have parallel disclosure regimes for different branches (legislative + executive). Data model already supports `ReportingPartyRequirement`; the prompt needs to enumerate them.

### Q5 — MVP gate
What's the green-light bar for the OH MVP? Anchored against the compendium directly, not against any prior rubric-projection artifact. Coverage-only? Coverage + qualitative-materiality capture? Coverage + multi-run agreement threshold? Coverage + audit-trail/citation chain?

### Q6 — Multi-run agreement
Prior runs hit 21.3% inter-run disagreement at temp-0 with files-read enforcement. What's an acceptable level for the new harness, and how do we collapse runs (majority vote, flag-for-review, scorer-of-scorers)?

### Q7 — Scaling shape
OH first → which states next, in what order, on what schedule. The 5–8 priority-state target lives in README.md scope but specific states aren't picked.

## Brainstorm transcript

(To be filled in as the brainstorming skill walks Q1–Q7.)
