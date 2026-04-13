# 20260413 — FOCAL indicator extraction

**Date:** 2026-04-13
**Branch:** `focal-extraction` (cut from main today)
**Participants:** Dan Parshall + Claude

## Summary

Single-session execution of the FOCAL extraction plan authored 2026-04-12 on the (now archived) `research-prior-art` branch. Created the `focal-extraction` worktree, transcribed Lacy-Nichols et al. 2024 Table 3 into `focal_2024_indicators.csv` (50 indicators across 8 categories, all three validation checks passed), and wrote the companion methodology note.

Mid-session, Dan flagged that the PRI–FOCAL framing in the methodology note was too clean: both rubrics span both the statutory-content and portal-accessibility dimensions, not one each. Corrected the methodology note with an explicit two-dimensional overlap table. Dan then made the meta-decision: **both rubrics will be scored in parallel, and the composite design will be a manual collaborator-review decision after data is in hand**, rather than an a-priori rubric-reconciliation pass.

Net result: FOCAL extraction deliverable complete; a FOCAL scoring plan will follow, running in parallel with the PRI 2026 re-score already underway on `pri-2026-rescore`.

## Topics Explored

- Supplementary-materials check (already resolved in 2026-04-12 planning convo): Lacy-Nichols Supplementary File 1 contains search strategies only, no indicator table — manual Table 3 transcription remains the canonical source.
- Worktree setup off main, data/ symlinked, docs seeded.
- Table 3 extraction. pdftotext output was cleaner than the plan's risk forecast; all 50 indicators on a single page with no layout breakage. PDF viewer consultation was not required.
- Validation spot-checks. All three passed: (1) 50 rows total, (2) per-category counts reconciling to Table 3 structure (Scope 4 / Timeliness 3 / Openness 9 / Descriptors 6 / Revolving door 2 / Relationships 4 / Financials 11 / Contact log 11), (3) verbatim spot-check on 5 indicators across 4 categories.
- PRI–FOCAL relationship. Corrected earlier oversimplification ("PRI = accessibility, FOCAL = content"). Actual overlap is two-dimensional: both rubrics have statutory-content halves (PRI 37 items, FOCAL 41 items across 7 categories) and portal-accessibility halves (PRI 22 items, FOCAL 9 items in Openness).
- Composition decision deferral. Dan's call: score both rubrics independently; collaborators choose composite post-data.

## Provisional Findings

1. **Table 3 is a clean source.** pdftotext preserved layout, no page-boundary ambiguity, no transcription surprises. The extraction is conservative and faithful.
2. **Indicator 3.3 is structurally compound** (available without registration / free / open license / non-proprietary format / machine readable — 5 sub-conditions). Scored as a single yes/no it will suppress cross-state variance. Recommend decomposition in the scoring plan, flagged in methodology note.
3. **Ministerial diaries (2.3, 3.2) and Westminster role names (1.3)** need US-state vocabulary translation but are not structurally inapplicable. Recommend "keep concept, normalize language" in the scoring plan rather than flagging `supports_state_application=no`. No indicator in the 50 was flagged `no`.
4. **`source_framework` column is blank throughout.** Paper's Table 2 gives framework-level not indicator-level attribution; the column is retained in CSV schema per plan but has no content.
5. **PRI + FOCAL composition is a post-scoring judgment call, not a pre-scoring rubric exercise.** Deliberate project decision — reduces the amount of analytical work required before collecting data, and grounds the eventual composite decision in actual per-state scoring output rather than framework-comparison reasoning.

## Decisions Made

- **Parallel scoring of both rubrics.** FOCAL and PRI will be scored against all 50 states independently. No pre-scoring reconciliation, no crosswalk construction, no spine choice. Composite rubric is a collaborator-review decision after both scorings produce output.
- **No `supports_state_application=no` flags.** All 50 FOCAL indicators translate to US-state scoring with operationalization work; caveats captured in `measurement_guidance` rather than exclusion flags.
- **Compound indicator 3.3 kept verbatim in extraction.** Decomposition is a scoring-plan decision, not an extraction-plan one. Lineage preserved.
- **Next branch work:** build a scoring pipeline. Open question (to resolve next session) is whether FOCAL scoring reuses the PRI pipeline infrastructure or builds in parallel. Decision carried into the next convo.

## Results Files

New this session:
- `docs/active/focal-extraction/results/focal_2024_indicators.csv` — 50 indicators, 8 categories, 7 columns including operationalization caveats.
- `docs/active/focal-extraction/results/focal_2024_methodology.md` — extraction method, validation evidence, explicit FOCAL exclusions (enforcement/sanctions/ethics/whistleblower), PRI–FOCAL two-dimensional overlap table, 7 open operationalization questions for the FOCAL scoring plan.
- `docs/active/focal-extraction/RESEARCH_LOG.md` — new branch log.
- `docs/active/focal-extraction/plans/20260412_focal_indicator_extraction.md` — copied from `docs/historical/research-prior-art/plans/` so the plan lives with its execution.

## Follow-ups

### Highest priority

- **Design the FOCAL scoring plan.** Applies the 50 indicators to US state portals. Running in parallel with the `pri-2026-rescore` branch's 7-phase plan. Key decision points: scoring granularity, 3.3 decomposition, ministerial-diary handling, Westminster role translation, 1.2 financial thresholds.
- **Decide pipeline architecture.** Do FOCAL and PRI share Sonnet-subagent scoring infrastructure, or build twice? The `pri-2026-rescore` plan already specifies a Sonnet subagent pipeline — reuse is attractive but only if the rubric-lock and scoring-prompt surfaces compose cleanly for both rubrics.

### Deferred (collaborator review)

- **PRI–FOCAL composite rubric design.** Happens after both scorings complete. Collaborator decision, not an agent task.

## Open Questions

- **FOCAL scoring scheme: binary vs. ordinal?** FOCAL itself does not prescribe. PRI used binary per-item in 2010. Consistency argument favors binary for both; richness argument favors ordinal. Unresolved.
- **Scoring pipeline reuse vs. parallel build?** To decide at start of next session.
- **Indicator 1.2 threshold.** "No (or low) financial or time threshold" is context-dependent. What concrete US-state dollar threshold counts as "low"? May need an empirical cut — e.g., median across states.
