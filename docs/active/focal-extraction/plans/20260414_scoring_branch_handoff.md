# Scoring Branch — Handoff

**Date:** 2026-04-14
**Source branches (being wrapped):** `focal-extraction`, `pri-2026-rescore`
**Destination branch:** `scoring` (to be cut from main after `focal-extraction` merges)

---

## Why this doc exists

Both rubric branches (`pri-2026-rescore` and `focal-extraction`) have completed their rubric-prep phases. PRI is through Phase 4 (rubrics locked + portal snapshots captured for 50/50 states). FOCAL is through Phase 1 operationalization as of today — the locked scoring rubric lands in this commit. The unified-pipeline architecture decision was made on 2026-04-14 (see `docs/active/pri-2026-rescore/plans/20260414_pri_focal_unified_scoring_handoff.md`). All remaining work is the **scoring pipeline itself**, which belongs on a dedicated branch.

This doc is the handoff brief the `scoring` branch picks up.

---

## State of play

### Rubrics (ready to consume)

| File | Items | Status |
|---|---|---|
| `docs/active/pri-2026-rescore/results/pri_2026_accessibility_rubric.csv` | 59 | Locked, user-approved |
| `docs/active/pri-2026-rescore/results/pri_2026_disclosure_law_rubric.csv` | 61 | Locked, user-approved |
| `docs/active/focal-extraction/results/focal_2026_scoring_rubric.csv` | 54 | Locked today (2026-04-14); methodology in `focal_2026_methodology.md` |

All three CSVs share the same column schema (`*_id, category, *_text, data_type, source, scoring_direction, scoring_guidance, notes`) — the scorer can iterate all of them through one generic row-by-row loop.

### Snapshot corpus (ready to score against)

- `data/portal_snapshots/<STATE>/2026-04-13/` — 50/50 states
- `data/portal_snapshots/<STATE>/2026-04-13/manifest.json` — per-fetch sha256, http_status, content_type, bytes, role, source, `suspicious_challenge_stub` flag
- Aggregate: 981 artifacts, ~350 MB
- `data/` is symlinked across worktrees; the `scoring` branch will see the same snapshots

Coverage tiers per `docs/active/pri-2026-rescore/results/20260413_stage1_stage2_collection_summary.md` and cross-audited in `docs/active/focal-extraction/results/20260413_snapshot_sufficiency_audit.md`:

- **~40 states clean-capture** — score now on both rubrics.
- **~8 states partial-WAF** (MA, NH, MI, CT, DE, KS, CA, NC, IL) — score what's captured; inaccessible items score low (rubric signal, not pipeline defect).
- **~12 states SPA-shell-only** (GA, ID, ND, SC, NM, ME, MI, AR, IN, PA) — static captures cover statutes/FAQ/guides; UX-dependent items need Playwright supplementation (parallel workstream).
- **2 states near-empty** (AZ, VT) — score from statute text only with explicit nulls on portal-derived items.

---

## Unified pipeline architecture (decided 2026-04-14)

Per `20260414_pri_focal_unified_scoring_handoff.md`: one scoring pass per state, all three rubrics evaluated against the same snapshot corpus in a single chained pipeline. Rationale:

1. Evidence corpus is shared (both rubrics cite the same files).
2. Cross-rubric consistency is auditable within the same output row group.
3. Token cost halved vs. two independent passes.
4. Composite is a post-data collaborator decision — aligned outputs support this.

### Per-state output

```
data/scores/<STATE>/<RUN_DATE>/pri_accessibility.csv
data/scores/<STATE>/<RUN_DATE>/pri_disclosure_law.csv
data/scores/<STATE>/<RUN_DATE>/focal_indicators.csv
data/scores/<STATE>/<RUN_DATE>/run_metadata.json
```

### Output row schema (all three CSVs)

`indicator_id, score, evidence_quote_or_url, source_artifact, confidence, unable_to_evaluate, notes, model_version, prompt_sha, rubric_sha, snapshot_manifest_sha`

Provenance columns stamp each row; allow audit replay without guessing which model/prompt/rubric produced which row.

---

## Reproducibility commitments (inherited from unified handoff)

1. **Version the scorer prompt** (commit as file; any change bumps the version).
2. **Stamp every row with provenance** (`model_version, prompt_sha, rubric_sha, snapshot_manifest_sha`).
3. **Three independent runs per state at temperature 0** (self-consistency check; >10% inter-run disagreement triggers rubric-sharpening, not per-score adjudication).
4. **Retain raw model outputs alongside adjudicated scores** (no overwriting; both disagreeing raw outputs and final adjudicated score are kept).

### Honest reproducibility caveat

Stages 1–2 (URL discovery + snapshot selection) are **not** reproducible — Sonnet chose search terms and linked pages to follow, so re-runs would produce overlapping but different outputs. The evidence base **is** frozen: bytes-on-disk with sha256s in manifests are the reproducibility anchor, not the pipeline that assembled them. Scoring is reproducible within LLM drift (typical temp-0 drift: ~1–5% of scores shift by ±1; the 3× self-consistency check quantifies this).

---

## Recommended phase plan for `scoring` branch

### Phase 1 — Pipeline build (estimate: 1–2 sessions)

1. Cut `scoring` branch from `main` (after `focal-extraction` merges with the locked FOCAL rubric).
2. Create `src/scoring/` Python package with `uv`-managed deps: `anthropic`, `pydantic`.
3. Write the locked scoring prompt (`src/scoring/scorer_prompt.md`):
   - Per-item evaluation, evidence-citation required for every score.
   - Handle SPA-shell / WAF stubs: when a file in `suspicious_challenge_stub` is the only evidence for an item, score `unable_to_evaluate: true` rather than guessing.
   - Structured output schema via pydantic (scorer must match or the call fails).
   - Inject `model_version, prompt_sha, rubric_sha, snapshot_manifest_sha` into every row at orchestrator level, not by asking the model.
4. Write snapshot loader: read `manifest.json`, index artifacts by role, expose as a typed structure.
5. Write rubric loader: read one of the three rubric CSVs; pydantic-validated.
6. Write scoring function: `(state, rubric, snapshot_bundle) → list[ScoredRow]`. One indicator at a time, temperature 0.
7. Write orchestrator: per-state subagent dispatch (Agent tool, not SDK — per auto-memory `feedback_prefer_subagents_over_sdk.md` and the PRI handoff's Q3 resolution).

### Phase 2 — Dry run on CA (estimate: same session as Phase 1)

8. Run one state (CA — biggest portal, known Imperva issues, stress-tests inaccessibility handling) with all three rubrics.
9. Validate output CSV shape; confirm every row has evidence field populated or `unable_to_evaluate: true`; confirm provenance fields stamped.
10. Commit pipeline + CA dry-run output.

### Phase 3 — Pilot on CA/CO/WY (estimate: 1 session)

11. Run CA, CO, WY with 3 independent temp-0 runs each, all three rubrics per run.
12. Compute inter-run disagreement rate per rubric.
13. If disagreement >10% of items: pause, sharpen the ambiguous rubric items, re-pilot.
14. User reviews pilot scores against snapshots; defects resolve as rubric-sharpening passes, not per-score adjudication.
15. Commit pilot scores (raw + adjudicated).

### Phase 4 — Full 50-state run (estimate: 1 wall-clock session, hours of model time)

16. Launch subagents across remaining 47 states; pilot states stay fixed.
17. Orchestrator must checkpoint per-state completion so rate-limit failures don't force re-runs.
18. Self-consistency check on all 50.
19. Items with inter-run disagreement → `human_review_queue.csv` for adjudication with raw outputs preserved.
20. Commit final outputs.

### Phase 5 — Deliverable synthesis (estimate: 1 session)

21. Produce three summary docs (one per rubric): per-state totals, per-category sub-totals, `coverage_tier` annotations so collaborators can distinguish "low-scoring because of weak portal" from "low-scoring because snapshot was incomplete."
22. Update `STATUS.md` and `RESEARCH_LOG.md` on `scoring` branch.
23. Push. Notify collaborators that all three 50-state scorings are ready for review.

### Not in scope

- **PRI-FOCAL composite rubric design.** Collaborator decision, downstream.
- **Playwright supplementation.** Parallel workstream on a separate branch; when Playwright-captured snapshots land for a state, the scorer re-runs that state with the same pipeline. Output format unchanged; new `run_metadata.json` reflects the updated snapshot manifest.
- **Evidence verification layer** (checking that fields on forms are actually populated in sample records). Post-first-pass enhancement.

---

## Open questions carried forward

1. **Subagent vs. SDK.** Default is Agent-tool subagents per state. Confirmed in PRI handoff; honor unless user overrides.
2. **Self-consistency disagreement threshold.** 10% from original plans; calibrate empirically on pilot if needed.
3. **Coverage-tier labeling in output.** Recommend a `coverage_tier` column on the output CSV (clean / partial_waf / spa_pending_playwright / inaccessible) so summary synthesis can filter or annotate without re-deriving the tier.
4. **AZ / VT treatment.** Score from statute text with heavy null expectation, or defer until Playwright lands. Recommend: score now, flag prominently; Playwright re-run when available overwrites with new `run_metadata.json`.
5. **SPA-state Playwright supplementation.** Out of scope for `scoring` branch code itself, but the pipeline must be structured so that a Playwright re-capture of a state's snapshot triggers a clean re-score without touching other states' outputs.
6. **Rubric-sharpening during pilot.** If pilot reveals ambiguity in a FOCAL indicator, who owns the sharpening? Default: operationalization doc on `focal-extraction` gets updated and re-merged to main; scoring branch pulls the revision. Same for PRI.

---

## Files the next agent needs

### Rubrics (inputs to the pipeline)
- `docs/active/pri-2026-rescore/results/pri_2026_accessibility_rubric.csv`
- `docs/active/pri-2026-rescore/results/pri_2026_disclosure_law_rubric.csv`
- `docs/active/focal-extraction/results/focal_2026_scoring_rubric.csv`

### Methodology (context for scoring decisions)
- `docs/active/pri-2026-rescore/results/pri_2026_methodology.md`
- `docs/active/focal-extraction/results/focal_2026_methodology.md`

### Evidence corpus
- `data/portal_snapshots/<STATE>/2026-04-13/` + `manifest.json` per state
- `data/portal_urls/<ABBR>.json` (reference for state-level context)
- `data/portal_urls/_flagged.md` (states with non-200 seed URLs)

### Upstream context docs
- This handoff
- `docs/active/pri-2026-rescore/plans/20260414_pri_focal_unified_scoring_handoff.md` (unified-pipeline architecture decision)
- `docs/active/pri-2026-rescore/results/20260413_stage1_stage2_collection_summary.md` (snapshot coverage)
- `docs/active/focal-extraction/results/20260413_snapshot_sufficiency_audit.md` (cross-rubric sufficiency assessment)
- `docs/historical/research-prior-art/plans/20260412_pri_2026_accessibility_rescore.md` (original PRI 7-phase plan; Phases 5–7 still load-bearing)

### Do not modify

- Existing committed rubrics (any sharpening during pilot lands via the rubric's source branch, not in-place on `scoring`).
- Snapshots (frozen at 2026-04-13; Playwright supplements write new date dirs, they do not overwrite).
- PRI's uncommitted branch state (if `pri-2026-rescore` has in-flight work, stay out of it).

---

**Branch lifecycle:** `scoring` is code + data. When Phase 5 deliverable ships, `scoring` merges to main and the three source branches (`pri-2026-rescore`, `focal-extraction`, `scoring`) all archive to `docs/historical/` as part of a single "Phase 5 complete" checkpoint.
