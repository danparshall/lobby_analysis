# PRI 2010 Ground-Truth Calibration — Implementation Plan

**Goal:** Calibrate the LLM scoring pipeline against PRI 2010's published human-rater scores (using 2010-era statutes as input), iterate the scorer prompt until our output matches PRI's inter-rater reliability window, then apply the calibrated prompt against 2026 statutes to produce defensible 2026 state scores.

**Originating conversation:** `docs/active/scoring/convos/20260417_pilot_and_calibration_pivot.md`

**Context:** The Phase 3 pilot (2026-04-17) found that PRI disclosure-law is flagged on all three pilot states (CA 37.7%, CO 11.5%, WY 11.5%) with disagreement driven not by scoring but by `unable_to_evaluate` vs `score=0` interpretation. Root cause: the snapshot corpus is same-host only, which excludes state legislative sites — we're scoring the portal's summary of the law, not the law itself. Rather than tighten the rubric against a proxy source, the project is pivoting to calibrate against a known labeled dataset (PRI 2010). See the convo for the full analysis.

**Confidence:** Exploratory. Three upstream unknowns gate this:
1. Is PRI 2010's published resolution fine enough to calibrate at? We have item-level scores for accessibility Q1-Q6 only; Q7/Q8 are sub-aggregates; disclosure-law is 5 sub-component aggregates (A/B/C/D/E). That limits per-item calibration signal — we may need to calibrate on sub-aggregates, not atomic items.
2. Can we retrieve 2010-era state statutes (50 states) reliably? Wayback Machine coverage for state legislature sites is uneven; PRI's own cited statute sections (if published) would be a cheaper anchor.
3. What is PRI 2010's internal inter-rater reliability? That's the realistic convergence target, not 100%. Pull from the methodology paper in `papers/`.

**Architecture:** Reuse the existing `src/scoring/` pipeline but swap the input from "portal snapshot bundles" to "statute text bundles." Add a `calibrate` subcommand to `scoring.orchestrator` that takes (state, rubric, LLM run_id, PRI 2010 reference scores) and reports agreement metrics. Iterate the `scorer_prompt.md` against the calibration subset; validate on a held-out set; apply to 2026 statutes at full-50-state scale.

**Branch:** Create a new worktree `pri-2010-calibration` off `main` (not off `scoring` — the calibration line is orthogonal to the in-flight scoring work; whichever converges first will inform how the other lands). Use the use-worktree skill which symlinks `data/` to the main worktree so the large data directories are shared.

**Tech Stack:** Python 3.12, `uv`, `pydantic`, existing `scoring` package. No new third-party dependencies expected. Continues the subagent-only (Agent tool, no SDK) dispatch pattern.

---

## Pre-flight reads

**On first picking up this plan, read in order:**

1. `STATUS.md` — current branch inventory, recent sessions
2. `README.md` — project scope
3. `docs/active/scoring/RESEARCH_LOG.md` — scoring-branch trajectory
4. `docs/active/scoring/convos/20260417_pilot_and_calibration_pivot.md` — the originating convo (this plan's "why")
5. `docs/active/scoring/results/20260417_{ca,co,wy}_consistency.md` — the concrete pilot disagreement that motivated the pivot
6. `docs/active/pri-2026-rescore/results/pri_2010_accessibility_rubric.csv` and `pri_2010_disclosure_law_rubric.csv` — atomic rubric structure
7. `docs/active/pri-2026-rescore/results/pri_2010_accessibility_scores.csv` and `pri_2010_disclosure_law_scores.csv` — the ground-truth per-state scores (note the resolution caveats above)
8. `docs/active/pri-2026-rescore/results/pri_2026_methodology.md` — how the 2026 rubric was constructed vs 2010
9. `src/scoring/scorer_prompt.md` — the prompt we'll iterate
10. `src/scoring/orchestrator.py` + `src/scoring/consistency.py` — reuse patterns
11. `PAPER_INDEX.md` — find the PRI 2010 paper; then `papers/text/` for the extracted methodology section

**Dan's working preferences** (memory-saved from the pilot session, worth knowing up front):
- Don't write throwaway `scripts/foo.py` with hardcoded values — extend the existing `scoring.orchestrator` CLI reusably.
- Subagent dispatch prompts must explicitly say "use Read tool only; do NOT subprocess, shell out, pdftotext, or unzip." Without this, scoring subagents try to shell out for PDF/ZIP content and trigger permission prompts Dan has to deny.
- Don't use `echo "---"` or literal `---` as a separator in chained bash output — it reliably hiccups on Dan's system.
- Rate-limit-safe subagent dispatch is ~4 concurrent. 21 concurrent triggers org-level Anthropic API throttling and silently kills ~95% of dispatches with "Server is temporarily limiting requests."

---

## Testing Plan

This plan has three modes of testing — choose per step:

**TDD (for implementation steps — new CLI subcommand, calibration harness, statute bundle loader):**

- Each new module gets pytest coverage against realistic inputs. No mocks of the scoring pipeline itself.
- The calibration harness has a pure-function `agreement_metrics(our_scores, pri_scores, level)` that takes item-level OR sub-aggregate-level scores and returns agreement dict. Test with small synthetic inputs covering: perfect agreement, full disagreement, mixed, null-handling, sub-aggregate rollup correctness.
- A statute bundle loader (analogous to `snapshot_loader.py`) validates that a statute directory contains the expected per-state files + manifest. Test against a fixture directory.
- Integration test: given a fake 2-state calibration subset with known PRI reference scores and LLM scores, `calibrate` produces the expected agreement report.

**Exploration / analysis (for calibration iteration itself — Phase 2, 3, 4):**

- Not TDD. Document what was run, what was observed, what constitutes a surprising result.
- Each prompt iteration produces a new scorer_prompt_vN.md with a tracked SHA and a results/ markdown documenting: which changes were made, which states/items improved, which regressed, whether the change helped, aggregate convergence metric.
- Track convergence in a running `results/calibration_trajectory.md` so it's clear whether we're improving or oscillating.

**Validation (for final application to 2026):**

- Spot-check 5 states by hand: read the 2026 statute bundle, read the LLM-scored CSV, disagree/agree per item.
- Compare 2026 state-level aggregate scores to 2010 state-level scores for states whose disclosure laws are known to be stable (low-change states). Dramatic 2010→2026 deltas on stable states are a red flag.

NOTE: I will write *all* unit/integration tests before I add any implementation behavior.

---

## Phase 0 — Verify ground truth is usable (1–2 hours, exploration)

**Goal:** Answer the three upstream unknowns before committing to the rest of the plan.

### Steps

- Read PRI 2010 methodology paper (find via PAPER_INDEX.md). Extract:
  - Number of human raters per state
  - Inter-rater reliability score (IRR) if reported — this is the convergence target
  - Whether per-item codings are published in an appendix, or only the sub-aggregates we have
  - Whether specific statute sections are cited per item (if so, statute retrieval becomes much cheaper — pull just those sections)
  - Scoring date range (when was the law "as of"? 2009–2010?)
- Inspect `pri_2010_accessibility_scores.csv` and `pri_2010_disclosure_law_scores.csv` in detail — confirm the coarse-resolution caveat from the plan header.
- Write `results/20260418_pri_ground_truth_audit.md` documenting:
  - What resolution we actually have
  - PRI's IRR number (or explicit note if they didn't publish one)
  - Which statute sections PRI cited (if any)
  - Go/no-go decision for the rest of the plan

### What would kill the plan at Phase 0

- If PRI 2010 used a completely different scoring scheme than what's in the paper's appendix (e.g., they scored against non-statute sources like newspaper articles), calibration doesn't make sense. STOP and surface to Dan.
- If PRI's IRR is itself <80%, the calibration target is unclear — continue only if Dan explicitly OKs a lower target.

### Edge cases

- PRI's paper may report IRR for accessibility but not disclosure-law (or vice versa). That's fine — calibrate each rubric half separately.
- If PRI used a DIFFERENT rubric atomicity than what was transcribed in `pri_2010_*_rubric.csv` (e.g., PRI scored "A. Registration" as a 10-point aggregate and our rubric has 11 A-items), we need to carefully check the transcription matches the paper's atomic structure. Don't assume.

---

## Phase 1 — Spot-check 2010 statute retrievability (half day, exploration)

**Goal:** Confirm we can actually get 2010-era state code text for a realistic subset of states.

### Steps

- Pick 5 states spanning the PRI 2010 score distribution: the top scorer, the bottom scorer, and 3 median scorers. (Use `pri_2010_disclosure_law_scores.csv` `rank_2010` column to select.)
- For each state:
  1. Locate the state's legislature / state code website. In 2026, that's typically a separate domain from the SOS portal (e.g., `leg.colorado.gov`, `leginfo.legislature.ca.gov`, `wyoleg.gov`).
  2. Query the Wayback Machine for captures of the state code landing page circa 2010-01-01 to 2011-06-30. Record coverage (how many snapshots, closest date to 2010-12-31).
  3. If PRI cited specific statute sections (per Phase 0), try to retrieve the Wayback-archived pages for those specific section URLs. Record success/failure.
  4. If no Wayback coverage, check Justia, FindLaw, state bar archives for 2010-era code copies.
- Write `results/20260418_statute_retrieval_audit.md` — per-state retrievability grade (clean / partial / unavailable), plus an overall projection for the full 50.

### Decision point after Phase 1

- **If ≥ 40 of 50 states look retrievable**: proceed. Plan a full 50-state statute capture.
- **If 20–40 retrievable**: proceed but calibrate only on retrievable states; Dan decides whether partial-state 2026 scoring is acceptable.
- **If < 20 retrievable**: STOP and re-scope with Dan. Alternatives: (a) calibrate on retrievable states only, accept coverage gap; (b) use current-2026-statute as both ground-truth proxy AND scoring input, dropping 2010 calibration; (c) abandon the statute-based approach and calibrate against portal guidance with a tightened rubric.

### Edge cases

- Some state codes are only published as PDFs, not HTML. Wayback captures may be of HTML index pages that link to PDFs; the PDFs themselves may not be archived. Check this during the spot-check.
- State code changes. "2010 statute" ideally means the law as of December 2010 — but revisions happen mid-year. Document which capture date we're using per state.
- A few states publish session laws (acts passed in 2010) separately from the codified code. PRI's methodology will say which they used.

---

## Phase 2 — Build the calibration harness (1 day, implementation)

**Goal:** Reusable CLI + library code for comparing our LLM output to PRI reference scores.

### Testing plan for this phase

Write the following tests FIRST:

- **`tests/test_calibration.py::test_agreement_metrics_identical`** — two identical score vectors → 100% agreement.
- **`::test_agreement_metrics_full_disagreement`** — disjoint scores → near-zero agreement.
- **`::test_agreement_metrics_null_handling`** — LLM `unable_to_evaluate` vs PRI numeric → counted as disagreement, not as missing data.
- **`::test_sub_aggregate_rollup_accessibility`** — 15 atomic Q7 sub-items rolled up to `Q7_raw` matches PRI's raw-count field.
- **`::test_sub_aggregate_rollup_disclosure_law`** — 61 atomic items rolled up to A/B/C/D/E sub-component totals match PRI's column structure.
- **`::test_statute_bundle_loader_validates_manifest`** — a fixture statute directory with manifest.json loads; a directory missing manifest.json raises.
- **`tests/test_orchestrator_calibrate.py::test_calibrate_subcommand`** — integration test: orchestrator reads fixture PRI reference scores and fixture LLM scores, produces a report with correct agreement rate.

Run them. Confirm they all fail. Then implement.

### Implementation

- Create `src/scoring/statute_loader.py` analogous to `src/scoring/snapshot_loader.py`. It loads a state-statute bundle: per-state directory containing `manifest.json` (listing statute section files, Wayback capture date, sha256 per file) + the statute artifact files themselves. No WAF stub flag; statute text is plain.
- Extend `src/scoring/bundle.py` to handle both snapshot bundles AND statute bundles. Brief assembly should be the same shape with role=`statute` artifacts.
- Create `src/scoring/calibration.py`:
  - `load_pri_reference_scores(rubric: str, repo_root: Path) -> dict[state, dict[item_or_subcomponent_id, score]]`
  - `rollup_our_scores_to_sub_aggregates(our_csv: Path, rubric: str) -> dict[state, dict[sub_agg_id, score]]` — aggregate atomic scores the same way PRI did.
  - `agreement_metrics(ours, pri_ref, level: Literal["item", "sub_aggregate"]) -> dict` — returns exact-match rate, per-state agreement, per-item/per-sub-aggregate agreement, a Kappa or similar, and a list of max-disagreement items.
- Add `calibrate` subcommand to `scoring.orchestrator`:
  - `uv run python -m scoring.orchestrator calibrate --rubric pri_accessibility --run-id <id> --output <path>`
  - Runs `rollup_our_scores_to_sub_aggregates` + `agreement_metrics` + writes a markdown report.
- All 9 existing pipeline tests continue to pass.

### Edge cases

- PRI 2010 scores include only 50 states + DC (check — might be 50). Our pipeline includes 50 states. Handle state-set mismatch explicitly.
- Accessibility Q7 raw count comparison: PRI's `Q7_raw` is a 0-15 integer. Our output will be 15 binary sub-item scores. `sum(binary_subitems)` should equal PRI's Q7_raw when we're scoring correctly; disagreement is an integer delta.
- Accessibility Q8 is "normalized": check PRI's methodology to understand how they normalize. Document the formula we use for rollup.
- Disclosure-law A/B/C/D/E rollup: the 2010 rubric CSV has `sub_component` column (per our earlier Read of it). Group atomic items by sub_component and sum the scores. Confirm the sums match PRI's published totals on the 50 known states before trusting the rollup.

---

## Phase 3 — Baseline run (1 day, exploration)

**Goal:** Run the CURRENT scorer prompt against 2010 statutes for the Phase-1 subset of states (5 states). Compare to PRI 2010. This is the "before" measurement.

### Steps

- Capture 2010 statute bundles for the 5 calibration states (per Phase 1 retrievability). Structure matches snapshot bundles: `data/statutes_2010/<STATE>/2010-12-31/...` with `manifest.json`.
- Dispatch 3 temp-0 runs per state per rubric (same self-consistency pattern as the pilot), using the current `scorer_prompt.md`. 5 states × 2 PRI rubrics × 3 runs = 30 subagent dispatches. **Dispatch in batches of 4 per rate-limit lessons from the pilot.**
- Finalize all 30 runs. Aggregate to sub-aggregates. Compute agreement vs PRI 2010.
- Write `results/<date>_calibration_baseline.md` with per-state + per-rubric agreement numbers. This is the baseline we're trying to improve.

### What constitutes a "surprising" baseline result

- Agreement already ≥ 90% on disclosure-law — this would contradict the pilot finding and suggest the disclosure-law disagreement was snapshot-driven rather than prompt-driven. Surface immediately.
- Agreement < 40% — something bigger is wrong (rubric misinterpretation, statute wrong vintage, rollup formula bug). Debug before iterating on prompt.

### Edge cases

- Inter-run disagreement on 2010 statutes will still exist but should be LOWER than on portal snapshots if the thesis holds (statute text is clearer than portal guidance). If 2010 inter-run disagreement ≥ 2026 portal disagreement, the calibration pivot's premise is weak — stop and surface.

---

## Phase 4 — Iterate the prompt to convergence (1–3 days, exploration)

**Goal:** Modify `scorer_prompt.md` until agreement with PRI 2010 reaches PRI's IRR window.

### Steps

- For each prompt iteration (`scorer_prompt_v2.md`, `v3.md`, …):
  - Change ONE thing at a time (e.g., "clarify unable-vs-zero rule", "tighten evidence citation requirement", "specify handling of statutes that reference but don't define a term"). Document the hypothesis.
  - Re-score all 5 calibration states × 2 rubrics × 1 run (NOT 3 — single run is fine for iteration speed; 3-run self-consistency only on final candidate).
  - Compute agreement vs PRI. Compare to prior iteration.
  - Append row to `results/calibration_trajectory.md`: iteration, change, pre→post agreement %, notes.
- Iteration stops when agreement ≥ PRI's IRR OR no single-change hypothesis improves further for 3 consecutive iterations (local minimum; time to surface).
- When converged, lock the prompt version and run the 3-run self-consistency check on the 5 calibration states to confirm it's stable.

### What could go wrong in iteration

- Overfitting: prompt changes that improve agreement on the 5 calibration states but generalize poorly. Validation on held-out states (Phase 5) catches this.
- Oscillation: changes trade off one state's agreement against another. Record trajectory to spot this.
- One rubric converges, the other doesn't. Diagnose separately; may need different prompt sections per rubric.

---

## Phase 5 — Held-out validation (half day, exploration)

**Goal:** Confirm the iterated prompt generalizes.

### Steps

- Pick 3–5 additional PRI 2010 states NOT in the calibration subset (again spanning the score distribution).
- Capture their 2010 statute bundles.
- Run the locked-version prompt against them — single run per state × 2 rubrics.
- Compute agreement vs PRI.
- If held-out agreement ≥ PRI's IRR: the prompt is calibrated. Proceed to Phase 6.
- If held-out agreement < PRI's IRR by more than 5pp: overfitting detected. Go back to Phase 4 with a smaller iteration step.

### Edge cases

- If agreement is high on calibration but held-out states have weird statutory structure (e.g., session laws referenced from outside the main code), that's a domain-knowledge gap, not overfitting. Surface and discuss with Dan.

---

## Phase 6 — Apply to 2026 statutes, full 50 states (1–2 days, exploration + scale-up)

**Goal:** Use the calibrated prompt against 2026-vintage statutes for all 50 states. This is what produces the defensible 2026 scores.

### Steps

- Capture 2026 statute bundles for all 50 states. Bundle structure matches 2010; snapshot date = current. This is a significant data-collection step on its own — plan to parallelize via subagents similar to the Phase 4 portal-snapshot capture from the pri-2026-rescore branch.
- Dispatch scoring runs: 50 states × 2 PRI rubrics × 1 run each (self-consistency already established on calibration states). 100 subagent dispatches in batches of 4. Allow ~1 day of dispatch throughput.
- Finalize all 100 runs, aggregate to sub-aggregates, produce per-state + per-rubric scores.
- Compare to 2010 baseline: which states moved most? Which items moved? Sanity-check high-change states against news-reported law changes (e.g., a state passed a major disclosure reform in 2014 → expect a substantial score move).

### Edge cases

- Some states with unretrievable 2010 statutes may have retrievable 2026 statutes (recency bias). Score them on 2026 but flag that no 2010 baseline comparison is possible.
- Some states' 2026 statutes may themselves reference other-host regulatory content (e.g., ethics commission rules). Decide whether to expand the capture or accept the statute-only scope.

---

## Phase 7 — Produce the deliverable (half day)

**Goal:** State-level aggregate 2026 scores for the PRI accessibility + disclosure-law rubrics, with transparent methodology.

### Steps

- Per-state aggregate totals for each rubric (sum of sub-aggregates, same as PRI 2010).
- Delta table: 2010 → 2026 score change per state per rubric.
- Methodology note: `results/20260XXX_pri_2026_calibrated_scores.md` covering:
  - What the calibration process was
  - Which prompt version was used (sha-stamped)
  - PRI IRR comparison (our match rate to PRI)
  - Caveats on states with incomplete coverage
  - How this relates to (and differs from) the portal-snapshot scoring on the `scoring` branch

### Then finish-convo + PR.

---

**Testing Details:**

- Unit tests cover the pure functions: `agreement_metrics`, `rollup_our_scores_to_sub_aggregates`, `load_pri_reference_scores`, `load_statute_bundle`. Each tests BEHAVIOR (does the function produce the right output for realistic input), not datastructure equality of mocks.
- Integration test covers the full `orchestrator calibrate` subcommand end-to-end against fixture data.
- Exploration phases (baseline, iteration, validation) are not unit-tested — they're observational. But each produces a written artifact under `results/` so the work is reproducible and auditable.
- Regression: all 9 existing `tests/test_pipeline.py` tests continue to pass throughout.

**Implementation Details (max 10 bullets):**

- New module: `src/scoring/calibration.py` (pure functions for agreement metrics and rollup).
- New module: `src/scoring/statute_loader.py` (parallel to `snapshot_loader.py`).
- Extend `src/scoring/bundle.py` to build briefs from statute bundles, not just snapshot bundles.
- New subcommand: `orchestrator calibrate` — takes run_id + rubric, produces agreement report vs PRI reference.
- All statute data lives under `data/statutes_{2010,2026}/<STATE>/<DATE>/` with manifest.json (same shape as snapshots).
- Prompt iterations live as `src/scoring/scorer_prompt_vN.md`; the currently-active prompt is `src/scoring/scorer_prompt.md` (symlink or overwrite — pick one, be consistent).
- Use batches of 4 concurrent Agent dispatches; subagent prompts MUST include "use Read tool only; do NOT subprocess/shell/pdftotext/unzip."
- Finish each phase with a `results/<date>_phase_N_<name>.md` document so the calibration history is legible.
- Use the existing `scoring.consistency.compute_consistency` for any in-phase 3-run self-consistency checks.
- Do NOT modify `docs/active/scoring/` results or the locked 2026-04-13 snapshot corpus — those belong to the `scoring` branch.

**What could change:**

- If PRI 2010 IRR turns out to be, say, 92%, and our baseline hits 89%, iteration may be unnecessary — we'd already be close. Scope down Phase 4 accordingly.
- If 2010 statute retrievability is bad (<20 states per Phase 1), the whole plan re-scopes. Either drop 2010 calibration entirely or accept partial coverage.
- If Dan decides the current scoring branch's approach is good enough (with a tighter prompt on the portal-only snapshot), this calibration line may run in parallel rather than as a replacement — the two produce different but comparable scores.
- Rate-limit policy from Anthropic may change; current safe concurrency is ~4.

**Questions:**

1. **Branch choice** — is `pri-2010-calibration` the right branch name? Or something shorter / clearer? Confirm with Dan.
2. **Scope of retrieval** — are 2010 and 2026 BOTH statute captures required, or can we shortcut 2026 by using a subset of already-known statutory provisions from FollowTheMoney / NIMP / etc.? Worth checking during Phase 1.
3. **Accessibility calibration** — the 2010 accessibility rubric is 22 items but the scores table only publishes Q1-Q8 (with Q7/Q8 as aggregates). This plan calibrates at the sub-aggregate level. If Dan wants per-atomic-item calibration, we need to find or reconstruct per-item PRI codings (unlikely to exist publicly).
4. **FOCAL** — this plan explicitly scopes to PRI accessibility + disclosure-law. FOCAL has no 2010 analog and cannot be calibrated this way. FOCAL scoring continues under the `scoring` branch with whatever prompt-sharpening the portal-side work settles on.
5. **Composition with the `scoring` branch** — if this calibration succeeds, do we merge the calibrated prompt back into `scoring` and re-score the 2026-04-13 snapshot corpus, or treat the 2010-calibrated pipeline as producing the canonical 2026 scores and retire the portal-based approach? Decision point for Dan once Phase 6 lands.

---
