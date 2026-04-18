# PRI 2010 Ground-Truth Calibration — Implementation Plan

**Goal:** Calibrate the LLM scoring pipeline against PRI 2010's published human-rater scores (using 2010-era statutes as input), iterate the scorer prompt until our output reaches a **discussion-set agreement target** (see "Calibration target" below — PRI didn't publish an IRR), then apply the calibrated prompt against 2026 statutes to produce defensible 2026 state scores.

**Originating conversation:** `docs/active/scoring/convos/20260417_pilot_and_calibration_pivot.md`

**Branch kickoff convo (amendments to this plan):** `docs/active/pri-calibration/convos/20260417_calibration_kickoff.md`

**Context:** The Phase 3 pilot (2026-04-17) found that PRI disclosure-law is flagged on all three pilot states (CA 37.7%, CO 11.5%, WY 11.5%) with disagreement driven not by scoring but by `unable_to_evaluate` vs `score=0` interpretation. Root cause: the snapshot corpus is same-host only, which excludes state legislative sites — we're scoring the portal's summary of the law, not the law itself. Rather than tighten the rubric against a proxy source, the project is pivoting to calibrate against a known labeled dataset (PRI 2010).

**Confidence:** Exploratory. Two upstream unknowns gate this (down from three — see Phase 0 below for what was answered):

1. Is PRI 2010's published resolution fine enough to calibrate at? We have item-level scores for accessibility Q1-Q6 only; Q7/Q8 are sub-aggregates; disclosure-law is 5 sub-component aggregates (A/B/C/D/E). Calibration happens at sub-aggregate level for comparison, but per Dan's direction we score **atomically** during data collection so per-item reconstruction is available if PRI per-item codings ever surface (Dan has messaged the original authors).
2. Can we retrieve 2010-era state statutes (50 states) reliably via Justia? Justia hosts historical code at stable URLs (`/codes/<state>/<year>/`), but coverage is uneven per state (e.g., CO only starts 2016). Phase 1 audit tells us the calibration-eligible pool size.

**Calibration target** (replaces the original "match PRI IRR" target, which doesn't exist — see Phase 0 findings):

PRI 2010 did not use multiple independent human raters and did not publish an IRR. Their methodology was: single-coder preliminary analysis (Nov 2009) → state-official review/confirmation (34/50 responded; 31 confirmed or corrected; 16 never externally validated). Implications for our target:

- Treat the **31 state-reviewed states** as higher-trust ground truth; treat the **16 non-responders** as lower-trust (disagreements there may reflect PRI error rather than LLM error).
- Target to be set by discussion once we have a baseline measurement. Candidates:
  (a) **Fiat target**: e.g., 90% exact item agreement on the 31 reviewed states.
  (b) **Bootstrap with a pilot hand-score**: hand-score 3 states against 2010 statutes, use our own PRI-agreement as the realistic target.
- Defer final target-setting to after Phase 3 (baseline) produces empirical numbers.

**Architecture:** Reuse the existing `src/scoring/` pipeline but swap the input from "portal snapshot bundles" to "statute text bundles." Add a `calibrate` subcommand to `scoring.orchestrator` that takes (state, rubric, LLM run_id, PRI 2010 reference scores) and reports agreement metrics. Iterate the `scorer_prompt.md` against the calibration subset; validate on a held-out set; apply to 2026 statutes at full-50-state scale.

**Retrieval architecture (Justia-unified):** Use Justia's historical and current state code as the single retrieval source for both 2010 and 2026 statute bundles. Stable URLs (`law.justia.com/codes/<state>/<year>/`) mean one retrieval module, one parser, uniform provenance. Per-state vintage coverage is uneven; eligibility rule is ±2 years of 2010 (symmetric tolerance) with **direction logged** (pre-2010 Justia may miss late-2009 changes; post-2010 Justia may include post-PRI reforms). States without any Justia year within ±2 are excluded from the calibration subset. For 2026 scoring, accept Justia's latest year per state (typically 1–2 years behind actual law) and log the vintage in the manifest.

**Branch:** Cut from `scoring` (not `main`) because this work continues the scoring line — the pilot surfaced the statute vs. portal gap, and the calibration approach is the response. Sharing the Python package scaffolding doesn't compromise intellectual orthogonality.

**Tech Stack:** Python 3.12, `uv`, `pydantic`, existing `scoring` package. Add `requests` + `beautifulsoup4` for Justia retrieval (pending user approval in Phase 1 implementation). Continues the subagent-only (Agent tool, no SDK) dispatch pattern for scoring; retrieval is standalone.

---

## Pre-flight reads

**On first picking up this plan, read in order:**

1. `STATUS.md` — current branch inventory, recent sessions
2. `README.md` — project scope
3. `docs/active/pri-calibration/RESEARCH_LOG.md` — this branch's trajectory
4. `docs/active/pri-calibration/convos/20260417_calibration_kickoff.md` — amendments to this plan (no-IRR finding, Justia-unified architecture, branch-from-scoring decision)
5. `docs/active/scoring/convos/20260417_pilot_and_calibration_pivot.md` — originating convo on the scoring branch
6. `docs/active/scoring/results/20260417_{ca,co,wy}_consistency.md` — concrete pilot disagreement
7. `docs/active/pri-2026-rescore/results/pri_2010_accessibility_rubric.csv` and `pri_2010_disclosure_law_rubric.csv` — atomic rubric structure
8. `docs/active/pri-2026-rescore/results/pri_2010_accessibility_scores.csv` and `pri_2010_disclosure_law_scores.csv` — ground-truth per-state scores
9. `docs/active/pri-2026-rescore/results/pri_2026_methodology.md` — 2026 vs 2010 rubric construction
10. `src/scoring/scorer_prompt.md` — the prompt we'll iterate
11. `src/scoring/orchestrator.py` + `src/scoring/consistency.py` — reuse patterns
12. `papers/text/PRI_2010__state_lobbying_disclosure.txt` — methodology section at lines 1120–1144 (no published IRR; state-official-review validation)

**Dan's working preferences:**
- Don't write throwaway `scripts/foo.py` with hardcoded values — extend the existing `scoring.orchestrator` CLI reusably.
- Subagent dispatch prompts must explicitly say "use Read tool only; do NOT subprocess, shell out, pdftotext, or unzip."
- Don't use `echo "---"` or literal `---` as a separator in chained bash output.
- Rate-limit-safe subagent dispatch is ~4 concurrent.

---

## Testing Plan

Three modes — choose per step:

**TDD (for implementation steps — Justia client, statute retrieval, calibration harness, orchestrator subcommands):**
- Each new module gets pytest coverage against realistic inputs. No mocks of the scoring pipeline itself.
- HTML parsing tested against captured fixture pages (never against live Justia in unit tests).
- Integration tests exercise the full CLI end-to-end against fixture data.

**Exploration / analysis (for calibration iteration — Phases 3, 4, 5):**
- Not TDD. Document what was run, what was observed, what constitutes a surprising result.
- Each prompt iteration produces a new `scorer_prompt_vN.md` with a tracked SHA and a results/ markdown.
- Track convergence in `results/calibration_trajectory.md`.

**Validation (for final 2026 application):**
- Spot-check 5 states by hand.
- Compare 2026 state-level aggregates to 2010 for known-stable states. Dramatic deltas on stable states are a red flag.

NOTE: Write all unit/integration tests before implementation behavior.

---

## Phase 0 — Verify ground truth is usable (COMPLETE, 2026-04-17)

**Goal:** Answer the upstream unknowns before committing to the rest of the plan.

### Findings

- **PRI IRR does not exist.** PRI 2010 methodology (paper pp.34–35, extract at `papers/text/PRI_2010__state_lobbying_disclosure.txt` lines 1120–1144): single-coder preliminary analysis + state-official review; 34/50 responded; 31 confirmed or corrected; 16 never externally validated. No multi-rater agreement step. The plan's original "match PRI IRR" target has been replaced (see "Calibration target" above).
- **Scoring scheme matches our rubric.** Binary yes/no, unweighted, with B1/B2 reverse-scored (line 1150–1154, 1977–1978 footnotes). No scheme mismatch risk.
- **Scoring vintage is early 2010.** PRI analysis Nov 2009; state reviews through Jan 2010. So "2010 statutes" effectively means late-2009 law.
- **Per-item codings not published in the paper.** Table 5 contains sub-component totals (A/B/C/D/E) by state; Appendix A has principal-vs-lobbyist split for E-component. Dan has messaged original authors for per-item codings; pending response. For now, calibrate at sub-aggregate level but **score atomically** so per-item reconstruction is available later.
- **Cited statute sections: not per-item.** PRI referenced state websites + NCSL broadly but didn't publish per-question statute citations. So no "cheap anchor" — full lobbying-chapter retrieval is needed per state.

### Go/no-go: GO

With the understanding that the convergence target will be set post-baseline rather than inherited from PRI.

---

## Phase 1 — 50-state Justia retrievability audit (half day, implementation + exploration)

**Goal:** Build the Justia retrieval module and audit all 50 states for 2010 + current (2026) statute availability. Output: per-state eligibility table.

### Module boundaries

Defined in detail in: `plans/20260417_statute_retrieval_module.md` (the focused sub-plan for this phase).

Short version:
- `src/scoring/justia_client.py` — HTTP client + HTML parsing for Justia codes pages (year listing, title/chapter structure).
- `src/scoring/statute_retrieval.py` — per-state audit logic (eligibility rules, ±2 year tolerance, chapter detection).
- `scoring.orchestrator audit-statutes` subcommand — runs the audit across all 50 states, emits CSV.
- `scoring.orchestrator retrieve-statutes` subcommand — retrieves full statute-chapter text for eligible states, builds statute bundles in `data/statutes_<vintage>/<STATE>/<date>/` with manifest.

### Eligibility rules

Per state:
1. **2010 available on Justia?** → use it (`year_delta=0`, `direction=exact`).
2. Else, find nearest year within ±2 (2008, 2009, 2011, 2012). Log delta + direction.
3. Else, mark as ineligible for calibration. Log why.
4. Separately check 2026-scoring eligibility: latest Justia year per state. Record vintage.
5. Second-level check: does the chosen year contain the lobbying/ethics title? (Empty year-pages exist; chapter-level presence is the real gate.)

### Output

`docs/active/pri-calibration/results/20260418_justia_retrieval_audit.csv`:
- `state, pri_2010_disclosure_rank, pri_2010_accessibility_rank`
- `justia_2010_available, justia_2010_has_lobbying_chapter`
- `justia_nearest_year_to_2010, year_delta, direction, nearest_has_lobbying_chapter`
- `justia_current_year, current_has_lobbying_chapter`
- `eligible_for_calibration, eligible_for_2026_scoring, notes`

And `docs/active/pri-calibration/results/20260418_justia_retrieval_audit.md` — methodology note + summary statistics.

### Decision point after Phase 1

- **≥ 40 of 50 states eligible for calibration**: proceed. Plan full calibration subset selection + scale-up.
- **20–39 eligible**: proceed with eligible pool only; discuss coverage gap.
- **< 20 eligible**: STOP and re-scope. Justia-unified may not be viable; consider Wayback of state-leg sites or a paid source (HeinOnline) for the gap.

### Edge cases

- Some states publish only certain titles at certain years on Justia. Chapter-level check catches this.
- Lobbying-chapter detection: titles vary by state ("Lobbyists and Lobbying," "Regulation of Legislative Agents," "Government Ethics"). Use a keyword-match heuristic, verify manually during audit.
- Justia's Cloudflare blocks bare-curl user agents; use a realistic browser UA, respect robots.txt, rate-limit the audit.

---

## Phase 2 — Build the calibration harness (1 day, implementation)

**Goal:** Reusable CLI + library code for comparing our LLM output to PRI reference scores.

### Testing plan

Write these tests FIRST:

- `tests/test_calibration.py::test_agreement_metrics_identical` — identical score vectors → 100% agreement.
- `::test_agreement_metrics_full_disagreement` — disjoint scores → near-zero agreement.
- `::test_agreement_metrics_null_handling` — LLM `unable_to_evaluate` vs PRI numeric → counted as disagreement, not missing data.
- `::test_sub_aggregate_rollup_accessibility` — 15 atomic Q7 sub-items rolled up to `Q7_raw` matches PRI's raw-count field.
- `::test_sub_aggregate_rollup_disclosure_law` — 61 atomic items rolled up to A/B/C/D/E totals match PRI column structure.
- `::test_statute_bundle_loader_validates_manifest` — fixture statute directory with manifest.json loads; missing manifest raises.
- `::test_agreement_metrics_trust_weighting` — responder-state agreement and non-responder-state agreement are separately computable.
- `tests/test_orchestrator_calibrate.py::test_calibrate_subcommand` — integration test: orchestrator reads fixture PRI refs + fixture LLM scores, produces report.

Run them. Confirm all fail. Then implement.

### Implementation

- `src/scoring/statute_loader.py` analogous to `snapshot_loader.py`. Loads statute bundle: per-state directory with `manifest.json` (listing statute section files, Justia vintage year, sha256 per file) + artifact files. Bundle manifest includes `vintage_year`, `vintage_delta_from_target`, `direction` (pre/exact/post), `pri_state_reviewed` (from the 34/50 list).
- Extend `src/scoring/bundle.py` to handle statute bundles alongside snapshot bundles. Brief assembly uses `role=statute` artifacts.
- `src/scoring/calibration.py`:
  - `load_pri_reference_scores(rubric, repo_root) -> dict[state, dict[id, score]]`
  - `rollup_our_scores_to_sub_aggregates(our_csv, rubric) -> dict[state, dict[sub_agg_id, score]]`
  - `agreement_metrics(ours, pri_ref, level, trust_partition=None) -> dict` — exact-match rate, per-state agreement, per-item/per-sub-aggregate agreement, max-disagreement items. When `trust_partition` is supplied, reports reviewed-vs-non-responder agreement separately.
  - Responder-state list hard-coded from paper footnote 80 (34 states); documented in code comments.
- Add `calibrate` subcommand to `scoring.orchestrator`:
  - `uv run python -m scoring.orchestrator calibrate --rubric pri_accessibility --run-id <id> --output <path>`
- All existing pipeline tests continue to pass.

### Edge cases

- PRI 2010 scores include 50 states (not DC). Our pipeline = 50 states. No mismatch expected but assert explicitly.
- Accessibility Q7 raw count: PRI's `Q7_raw` is 0–15 integer. Our output = 15 binary sub-items. `sum(binary)` should equal PRI's Q7_raw. Disagreement is an integer delta.
- Accessibility Q8 "normalized": check paper for formula; document the rollup formula in code.
- Disclosure-law A/B/C/D/E rollup: group atomic items by `sub_component` column in the rubric CSV. Confirm sums match published PRI totals across all 50 states before trusting the rollup (reconciliation test).

---

## Phase 3 — Baseline run (1 day, exploration)

**Goal:** Run the CURRENT scorer prompt against 2010 statutes for a Phase-1-selected subset. Compare to PRI 2010. This is the "before" measurement.

### Steps

- Pick 5 calibration states spanning the PRI 2010 score distribution AND weighted toward responder states (higher-trust ground truth). Use the Phase 1 eligibility table to pick.
- Retrieve 2010 statute bundles via `orchestrator retrieve-statutes` (from Phase 1 machinery).
- Dispatch 3 temp-0 runs per state per rubric (self-consistency pattern from the pilot). 5 × 2 × 3 = 30 dispatches. Batches of 4.
- Finalize all 30 runs. Aggregate to sub-aggregates. Compute agreement vs PRI 2010.
- Write `results/<date>_calibration_baseline.md` with per-state + per-rubric agreement, broken out responder vs non-responder.

### What constitutes a "surprising" baseline

- Agreement already ≥ 90% on disclosure-law — would suggest pilot disagreement was entirely snapshot-driven, not prompt-driven. Surface and re-think.
- Agreement < 40% — something bigger is wrong (rubric misinterpretation, statute wrong vintage, rollup bug). Debug before iterating.
- Responder-state agreement is sharply lower than non-responder-state agreement — suspicious; should be the opposite. Surface.

### Edge cases

- Inter-run disagreement on 2010 statutes should be lower than on portal snapshots if the thesis holds. If not, the calibration pivot's premise is weak — stop and surface.

---

## Phase 4 — Iterate the prompt to convergence (1–3 days, exploration)

**Goal:** Modify `scorer_prompt.md` until agreement with PRI 2010 reaches the target set post-baseline.

### Steps

- For each prompt iteration (`scorer_prompt_v2.md`, `v3.md`, …):
  - Change ONE thing at a time. Document the hypothesis.
  - Re-score all calibration states × 2 rubrics × 1 run (NOT 3).
  - Compute agreement vs PRI. Compare to prior iteration.
  - Append row to `results/calibration_trajectory.md`: iteration, change, pre→post agreement %, notes, responder-vs-non-responder split.
- Iteration stops when agreement ≥ target OR no single-change hypothesis improves further for 3 consecutive iterations (local minimum).
- When converged, lock the prompt and run the 3-run self-consistency check to confirm stability.

### What could go wrong

- Overfitting: improvements on calibration states that don't generalize. Phase 5 catches this.
- Oscillation: changes trade one state's agreement against another. Trajectory log spots this.
- One rubric converges, the other doesn't. Diagnose separately.

---

## Phase 5 — Held-out validation (half day, exploration)

**Goal:** Confirm the iterated prompt generalizes.

### Steps

- Pick 3–5 additional PRI 2010 states NOT in the calibration subset, again favoring responder states.
- Retrieve their 2010 statute bundles.
- Run locked prompt, single run per state × 2 rubrics.
- Compute agreement vs PRI.
- If held-out agreement ≥ target: proceed to Phase 6.
- If held-out agreement < target by > 5pp: overfitting. Back to Phase 4 with smaller iteration step.

---

## Phase 6 — Apply to 2026 statutes, full 50 states (1–2 days)

**Goal:** Use calibrated prompt against 2026-vintage statutes for all 50 states.

### Steps

- Retrieve 2026 statute bundles via `orchestrator retrieve-statutes --vintage latest`. Manifest logs each state's actual Justia year (latest available, not literally 2026).
- Dispatch scoring: 50 × 2 × 1 = 100 dispatches. Batches of 4. ~1 day of throughput.
- Finalize. Aggregate to sub-aggregates. Produce per-state scores.
- Compare to 2010 baseline. Flag high-delta states. Sanity-check against known reform events (e.g., post-2010 state disclosure reform → expect movement).

### Edge cases

- States ineligible for 2010 calibration but eligible for 2026 scoring: score them on 2026, flag that no 2010 baseline comparison is possible.
- States' 2026 statutes referencing off-host regulatory content (ethics commission rules): decide per state whether to expand capture or accept statute-only scope.

---

## Phase 7 — Produce the deliverable (half day)

**Goal:** State-level aggregate 2026 scores for PRI accessibility + disclosure-law, with transparent methodology.

### Steps

- Per-state aggregate totals per rubric (same rollup as PRI 2010).
- Delta table: 2010 → 2026 score change per state per rubric.
- Methodology note: `results/<date>_pri_2026_calibrated_scores.md` covering:
  - Calibration process + convergence target chosen + why
  - Prompt version SHA used
  - Responder-vs-non-responder agreement breakdown
  - Per-state Justia vintages used (2010 and current)
  - Caveats on states with ineligible vintage
  - Relation to (and divergence from) portal-snapshot scoring on `scoring` branch

### Then finish-convo + PR.

---

**Testing Details:**

- Unit tests: pure functions in `justia_client`, `statute_retrieval`, `calibration`. Each tests behavior, not mock equality.
- Integration tests: `orchestrator audit-statutes`, `orchestrator retrieve-statutes`, `orchestrator calibrate` end-to-end against fixture data.
- Exploration phases (baseline, iteration, validation): not unit-tested; produce written artifacts under `results/`.
- Regression: all existing `tests/test_pipeline.py` tests continue to pass.

**Implementation Details:**

- New modules: `src/scoring/justia_client.py`, `src/scoring/statute_retrieval.py`, `src/scoring/statute_loader.py`, `src/scoring/calibration.py`.
- Extend `src/scoring/bundle.py` for statute bundles.
- New subcommands: `audit-statutes`, `retrieve-statutes`, `calibrate`.
- Statute data: `data/statutes/<STATE>/<YEAR>/` with manifest.json (vintage, delta, direction, sha256).
- Prompt iterations: `src/scoring/scorer_prompt_vN.md`; active is `src/scoring/scorer_prompt.md` (overwrite on lock).
- Subagent batches of 4; prompts include "Read tool only; no subprocess/shell/pdftotext/unzip."
- Each phase closes with `results/<date>_phase_N_<name>.md`.
- Do NOT modify `docs/active/scoring/` results or the locked 2026-04-13 snapshot corpus.

**What could change:**

- If the baseline (Phase 3) already shows high agreement, Phase 4 may scope down.
- If Phase 1 eligibility is low (< 20 states), re-scope to Wayback-supplemented or paid-source retrieval.
- If the portal-snapshot approach converges independently on the `scoring` branch with a tightened prompt, this calibration may be an independent validation rather than a replacement.
- Rate-limit policy from Anthropic may change; current safe concurrency is ~4.

**Questions — closed:**

1. ~~Branch choice~~ — `pri-calibration` (confirmed Dan 2026-04-17).
2. ~~Scope of retrieval~~ — Justia-unified: both 2010 and 2026 via one module; FollowTheMoney shortcut not needed.
3. ~~Accessibility calibration~~ — Score atomically (per Dan 2026-04-17) so per-item reconstruction is always available; compare at whatever resolution PRI provides. If per-item codings arrive from the authors, reuse the atomic data without re-scoring.

**Questions — still open:**

4. **FOCAL** — this plan scopes to PRI only. FOCAL has no 2010 analog. FOCAL scoring continues under the `scoring` branch with whatever prompt-sharpening the portal side settles on.
5. **Composition with `scoring` branch** — if this calibration succeeds, do we merge the calibrated prompt back into `scoring` and re-score the 2026-04-13 portal snapshots, or treat the statute-based pipeline as producing the canonical 2026 scores and retire the portal approach? Decision for Dan once Phase 6 lands.
6. **Convergence target value** — set after Phase 3 baseline numbers are in.

---
