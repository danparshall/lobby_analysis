# Research Log: statute-retrieval
Created: 2026-04-29
Purpose: Build a scalable two-pass statute retrieval pipeline (retrieval agent → scoring agent) that can run annually on all 50 states without manual per-state URL curation

## Conversations

(newest first)

## Session: 2026-04-29 — 20260429_retrieval_pipeline_design

### Topics Explored
- Cleaned up merged worktrees/branches, verified data safety before removal
- Designed two-pass retrieval architecture (LLM-driven cross-reference discovery, 2-hop limit, enriched manifests)
- TDD implementation: Phase 1 (enriched StatuteArtifact model), Phase 2 (retrieval agent prompt, brief builder, ingest_crossrefs, orchestrator subcommands)
- Ran retrieval agents on CA (5 cross-refs), TX (7), OH (9) — all successfully identified relevant support chapters
- Discovered Justia 404 gap for CA 2010 definitions; used 2007 fallback
- Multiple scorer prompt iterations across 4 OH runs, 4 TX runs, 3 CA runs

### Provisional Findings
- Retrieval infrastructure works well — LLM-driven cross-reference discovery is reliable
- C_public_entity_def matches 3/3 states with functional-definition guidance
- D_materiality matches 2/3 states (OH regressed on latest prompt)
- CA and OH A-series within ±1 of PRI; TX A-series is -5 (different mechanism — narrow "person" def + entity-agnostic trigger)
- TX E-series has cascade bug: E1a=0 zeros all 15 E1 items. Single biggest scoring error.
- Scorer reads exemptions as broader than PRI does — the central prompt engineering challenge

### Results
- `results/20260429_calibration_comparison.md` — full cross-state calibration table with run histories

### Next Steps
- Fix TX E1 cascade (scorer must distinguish partial vs blanket principal exemption)
- Investigate TX A-series: scorer needs to reason about interaction between expenditure-based triggers and entity definitions
- Add Justia 404 detection + adjacent-vintage fallback to ingest_crossrefs
- Re-run OH with prompt that doesn't regress D
- Consider running all 3 states with the same prompt version for a clean comparison

## Plans

(newest first)

- **20260429_two_pass_retrieval_agent** — Two-pass pipeline: retrieval agent follows cross-references (2-hop, LLM-driven), enriched manifests, PRI 2010 as test suite. OH first. Originated from `convos/20260429_retrieval_pipeline_design.md`.
