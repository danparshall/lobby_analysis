# Research Log: statute-retrieval
Created: 2026-04-29
Purpose: Build a harness that reads state lobbying law and produces correct, auditable disclosure-requirement extractions for the StateMasterRecord. The harness must scale to all 50 states annually without per-state hand-curation, and its outputs must be inspectable enough that activists and journalists can verify which disclosure obligations the law actually imposes.

PRI 2010 and Sunlight 2015 (and eventually CPI Hired Guns 2007, Newmark 2005/2017) serve as **multi-rubric calibration signals**, not optimization targets. We don't tune the harness to match any one rubric — single-rubric matching can mask a scorer that is overfit to one rater's quirks (Newmark 2017: PRI vs CPI cross-rater r = 0.04). Instead: where multiple independent rubrics concur and the harness disagrees, that is a real extraction error worth fixing; where rubrics disagree with each other (judgment-call zones), the harness's reading of the statute is the load-bearing artifact, and we don't chase any single rubric's score.

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

### Next Steps (morning, superseded by afternoon continuation)
- Fix TX E1 cascade (scorer must distinguish partial vs blanket principal exemption)
- Investigate TX A-series: scorer needs to reason about interaction between expenditure-based triggers and entity definitions
- Add Justia 404 detection + adjacent-vintage fallback to ingest_crossrefs
- Re-run OH with prompt that doesn't regress D
- Consider running all 3 states with the same prompt version for a clean comparison

### Continuation, same day (afternoon) — appended to same convo doc

- Bumped scorer to **claude-opus-4-7** (`provenance.py`); fixed duplicated literal in `orchestrator.py`.
- Diagnosed dispatch variance (opus subagent uses 4–43 tool calls per dispatch on the same statute) as the dominant noise source. Added **files-read enforcement**: brief requires sidecar `files_read.json`; locked prompt adds Rule 7; orchestrator fails closed if any bundle file is unread without explanation. Variance collapsed from ±7 to ±1 on TX total.
- **Narrowed Rule 6's C0 sub-rule**: public-entity definitions count only when they bring entities INTO the disclosure obligation, not when they appear in exemption or fund-use clauses. Fixed TX C0 over-score; CA C0 still 1/0 (open question).
- **Three-state apples-to-apples (opus + enforcement)**: TX 22–23/29 (−7/−6), CA 29/23 (+6), OH 25/26 (−1). Gap structure asymmetric — chasing TX agreement would worsen CA/OH.
- **Surfaced Sunlight 2015 as second ground-truth dataset** (`papers/Sunlight_2015__state_lobbying_disclosure_scorecard_data.csv`). PRI and Sunlight independently rank TX > OH; opus ranks OH > TX. Two unrelated human raters concurring is a real signal.
- **Goal reframe**: harness produces `StateMasterRecord` disclosure-requirement extractions; PRI/Sunlight are calibration signals, not optimization targets. Updated four docs (RESEARCH_LOG Purpose, plan Goal/Architecture, calibration_comparison header, STATUS Track A line + branch row). Justification: Newmark 2017 PRI vs CPI cross-rater r = 0.04.
- **Withdrew the proposed "within-the-regime's-reach" A-series rule** after user pushback. PRI item text reads institutionally; the proposed rule would have inflated scores on weakly-grounded reasoning.
- **Commits**: `fc644b5` (scorer changes + doc reframe), `904b110` (multi-rubric-extraction-harness plan).

### Carried-forward open questions
1. CA C0 = 1/0 over-score — coverage-side definition or another exemption-side one to narrow Rule 6 against?
2. Sunlight correlation analysis (Phase 1 of new plan) — does opus track Sunlight in the same band as PRI does?
3. Phase 3 extraction-first refactor needs a brainstorm before coding.
4. Justia 404 detection + adjacent-vintage fallback (still unaddressed).
5. OH C0 = 1/1 ✓ — confirm genuinely correct vs lucky dispatch variance.

## Plans

(newest first)

- **20260429_multi_rubric_extraction_harness** — Reframe of harness goal: produce `StateMasterRecord` disclosure-requirement extractions, calibrated multi-rubric (PRI 2010 + Sunlight 2015 + planned CPI/Newmark). Phase 1: Sunlight correlation analysis (no new infra). Phase 2: Sunlight as second scoring rubric. Phase 3: extraction-first refactor (brainstorm-needed). Phase 4: scale to README's 5–8 priority states. Originated from the 2026-04-29 prompt-iteration thread that surfaced the goal-vs-instrument confusion.
- **20260429_two_pass_retrieval_agent** — Two-pass pipeline: retrieval agent follows cross-references (2-hop, LLM-driven), enriched manifests, PRI 2010 as test suite. OH first. Originated from `convos/20260429_retrieval_pipeline_design.md`.
