# PRI + FOCAL Unified Scoring — Phase 5 Handoff

**Date:** 2026-04-14
**Branch context:** written from `pri-2026-rescore`; applies to both `pri-2026-rescore` and `focal-extraction` work, which will be unified into a single scoring chain going forward.
**Originating convo:** `docs/active/pri-2026-rescore/convos/20260413_pri_phase4_data_collection_prep.md`
**Upstream plans:**
- PRI plan: `docs/historical/research-prior-art/plans/20260412_pri_2026_accessibility_rescore.md`
- FOCAL plan: (in `focal-extraction` branch — consult FOCAL RESEARCH_LOG)

---

## Why this doc exists

Data collection (Stage 1 + Stage 2) is complete under the PRI branch. Next phase is LLM-assisted scoring. **Project decision (2026-04-14):** rather than run two independent scoring passes (one per rubric), score both PRI and FOCAL rubrics against the same snapshot corpus in a single chained pipeline per state.

This doc is the handoff brief for whichever agent/session picks up Phase 5. It captures current state, reproducibility commitments, and the unified-chain architecture.

---

## Current State (end of 2026-04-13 session)

### Data collected (lives in `data/`, not committed)

- `data/portal_urls/<ABBR>.json` — 50 seed URL JSONs (one per state), role-labeled, WebFetch-verified at discovery time.
- `data/portal_urls/_flagged.md` — 15 states with non-200 seed URLs (WAF/DNS/auth) catalogued for collaborator manual re-verification.
- `data/portal_snapshots/<STATE>/2026-04-13/` — 50 per-state snapshot directories with raw HTML/PDF/XLSX/ZIP/CSV artifacts + a `manifest.json` per state with per-fetch sha256, http_status, content_type, bytes, source (`seed` or `linked`), and `suspicious_challenge_stub` flag.
- Aggregate: 981 artifacts, ~350 MB on disk.

### Rubrics (committed, in `docs/active/pri-2026-rescore/results/`)

- `pri_2026_accessibility_rubric.csv` — 59 items
- `pri_2026_disclosure_law_rubric.csv` — 61 items
- `pri_2026_methodology.md` — modernization rationale
- `focal_2024_indicators.csv` — 50 indicators (lives on `focal-extraction` branch until merged)

### What's blocking

Nothing hard. Ready to start Phase 5. Known soft issues catalogued in previous convo's "Open Questions" section — most are collaborator follow-up tasks (fix AL seed URLs, re-verify HI Salesforce status, supplement AZ/VT via playwright) that don't block the scoring pass for the other 40+ states.

### Coverage tiers for scoring

- **40 states cleanly captured:** full rubric scoring feasible.
- **8 states partial capture** (MA, NH, MI, CT, DE, KS, CA, NC, IL — WAF/SPA on subset of URLs): score what we have; items that depend on inaccessible portal content correctly score low (that's the rubric signal, not a pipeline bug).
- **2 states near-empty** (AZ, VT — 100% WAF-blocked): document the gap, score from statute + observations field only, flag for playwright follow-up.
- **~12 states are SPA-shell-only on the public portal** (GA, ID, ND, SC, NM, ME, MI, AR, IN, PA, etc.): static captures still give statutes + user guides + FAQs + bulk-download artifacts; UX-dependent rubric items score low.

---

## Architectural decision: unified scoring chain

### Decision

Score both rubrics against each state's snapshot corpus in **one scoring pass per state**, not two independent passes.

### Rationale

1. **Snapshot corpus is shared.** Both PRI and FOCAL score against the same evidence (the state's portal + statute + data artifacts). Running twice re-reads the same files and doubles token cost for no marginal signal.
2. **Evidence citations transfer.** A rubric item in PRI ("bulk download available") and a rubric item in FOCAL (the analogous openness indicator) cite the same evidence file — the scorer can be more consistent with itself if it evaluates both in one pass.
3. **Rubric overlap is two-dimensional** (per the 2026-04-13 focal-extraction session): PRI and FOCAL each span statutory-content and portal-accessibility dimensions. Scoring in one chain makes cross-rubric consistency auditable in the same output row group.
4. **Composite decision is deferred to post-data.** Project-level decision (from STATUS.md) is that the composite-rubric choice happens as a collaborator review after both 50-state scorings complete. Unified scoring supports this by producing aligned per-state outputs with shared evidence.

### Architecture

Per state, one subagent (or SDK call) dispatched with:
- The state's snapshot directory path + manifest.json
- Both rubrics (PRI accessibility + PRI disclosure-law + FOCAL indicators) as CSV attachments
- A locked scoring prompt that instructs item-by-item evaluation with required evidence citation
- Temperature 0
- Pinned model version (stamped into output metadata)

Output per state:
- `data/scores/<STATE>/<RUN_DATE>/pri_accessibility.csv`
- `data/scores/<STATE>/<RUN_DATE>/pri_disclosure_law.csv`
- `data/scores/<STATE>/<RUN_DATE>/focal_indicators.csv`
- `data/scores/<STATE>/<RUN_DATE>/run_metadata.json` with `(model_version, prompt_sha, rubric_shas, snapshot_manifest_sha, run_timestamp)`

---

## Reproducibility commitments

Score outputs must be replayable by anyone with the frozen snapshots + the scorer prompt + a valid Anthropic key. Four commitments:

1. **Version the scorer prompt.** Commit the locked prompt as a file (e.g., `src/pri_scoring/scorer_prompt.md` or similar), treat as code. Any change to the prompt bumps the version.
2. **Stamp every score row with provenance:** `(model_version, prompt_sha, rubric_sha, snapshot_manifest_sha)`. Allows a future auditor to verify what produced what without guessing.
3. **Three independent runs per state at temperature 0.** Per the original plan's self-consistency check. Items where 3 runs disagree flag rubric ambiguity (not noise) — these go to a human-review queue and drive rubric-sharpening, not per-score adjudication.
4. **Keep raw model outputs alongside adjudicated scores.** If a rubric-ambiguity item is adjudicated during the full-50 run, both the raw disagreeing outputs and the final score are retained. No overwriting.

### Honest note on "reproducibility"

- **Stages 1 and 2 are NOT reproducible.** URL discovery involved Sonnet choosing search terms and interpreting results; linked-page selection during snapshotting involved Sonnet picking which same-host links to follow. Re-running would produce different (overlapping) outputs.
- **The evidence base IS frozen.** Snapshots have sha256s in manifests; the bytes-on-disk are the reproducibility anchor, not the pipeline that assembled them.
- **Scoring is reproducible within LLM drift.** Temperature-0 LLMs have residual non-determinism from batching/tokenization/floating-point. Typical drift is ~1–5% of scores shifting by ±1. The 3× self-consistency check quantifies this; publish the disagreement rate alongside scores in the deliverable methodology section.
- **Pinning the model version is load-bearing.** `claude-sonnet-4-6` ≠ `claude-sonnet-4-7`. Stamp the full version string in every output row.

---

## Recommended next steps

1. **Merge `focal-extraction` branch into `pri-2026-rescore`** (or vice versa, or into a new `scoring` branch) so both rubrics are available in a single working directory. Discuss with user before choosing branch strategy.
2. **Write the locked scoring prompt** — per-item evaluation, evidence-citation requirement, handling of inaccessible URLs (score 0 or null with explicit `unable_to_evaluate: true` rather than guessing), structured output schema.
3. **Dry-run on one state** (recommend CA — biggest portal, known Imperva issues, will stress-test the inaccessibility handling). Validate output schema and evidence quality before proceeding.
4. **Pilot on CA, CO, WY** at temp 0 with 3 independent runs each. Compute inter-run disagreement rate. If >10% of items disagree, pause and sharpen rubric before the full run.
5. **Full 50-state run** with orchestrator that checkpoints per-state completion (so partial failures don't force re-runs).
6. **Deliverable synthesis** — both scorings land as CSVs; composite choice is a later collaborator decision.

---

## Known issues / open questions carried forward

1. **Seed-JSON refinements for the ~4 states flagged mid-snapshot:** AL (add ethics-form.alabama.gov), HI (update Salesforce status 403→200), MS (prefer lobbying.sos.ms.gov over Akamai'd hosts), CA (manually verify fppc.ca.gov). Collaborator task. Non-blocking for scoring the other 40+ states.
2. **Playwright supplement for AZ, VT, plus ~10 SPA-shell states.** Either score with degraded evidence and flag, or defer those states until playwright captures land. Project-level call.
3. **Stub-detection heuristic is crude.** The 2KB-HTML rule caught some challenge stubs but missed a 3.3KB LA error page and several 5-20KB SPA shells. Consider refining to (size threshold + sha-duplication + content-sniffing) during scoring, or trust the `suspicious_challenge_stub` flags already in manifests.
4. **AZ snapshot is empty.** Pre-Phase-5 decision: either re-attempt AZ discovery with a different stack (playwright at the URL-discovery stage too), or accept and score from statute + FOIA observations.
5. **Self-consistency disagreement threshold.** Original plan set 10% of items. May need empirical recalibration after pilot — CA + CO + WY are heterogeneous enough to inform the threshold honestly.

---

## Files / paths the next agent will need

- Rubrics: `docs/active/pri-2026-rescore/results/pri_2026_*.csv` (and once merged) `focal_2024_indicators.csv`
- Snapshots: `data/portal_snapshots/<STATE>/2026-04-13/` + `manifest.json`
- Seed URLs (for reference): `data/portal_urls/<ABBR>.json`
- Flagged gaps: `data/portal_urls/_flagged.md`
- This handoff: the file you're reading
- Original PRI plan (still load-bearing for Phase 5–7 methodology): `docs/historical/research-prior-art/plans/20260412_pri_2026_accessibility_rescore.md`
