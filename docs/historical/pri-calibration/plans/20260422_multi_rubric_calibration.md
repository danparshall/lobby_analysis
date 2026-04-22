# Multi-rubric calibration — extension to the pri-calibration charter

**Status:** Plan. Supersedes the narrow single-rubric framing of `plans/20260417_pri_ground_truth_calibration.md`; does not replace its Phases 1–5 (retrieval, bundles, baseline, H1-debug). Adds Phases 6–10 for cross-rubric extension.

**Originating convo:** `convos/20260422_pm_calibration_reframe_and_merge_prep.md` (this branch). Builds on the 2026-04-22 landscape brainstorm (`convos/20260422_landscape_brainstorm_and_v11_scoping.md`).

**Branch:** Not this one. After pri-calibration merges to main and its docs archive to `docs/historical/`, a *new* branch (fellow-owned) picks up this plan. Naming suggestion: `statute-verification` or `multi-rubric-calibration`. Dan to decide.

**Confidence:** High on the direction (cross-rubric is a stronger LLM-reading validation than single-rubric). Medium on ordering — Phase 6 (CPI) vs. Phase 7 (Sunlight) could swap depending on which rubric CSV surfaces first. Low-certainty on Phase 9 (OpenSecrets 2022) because the 19-state coverage is partial and may not be worth the plumbing.

## Why this exists

The 2026-04-22 (am) landscape brainstorm reframed the project's primary deliverable from "rubric scores" to "data infrastructure + compendium matrix." pri-calibration's original charter was oriented toward the dead framing — produce defensible PRI 2026 scores as a public output. Its stable, forward-compatible role is **internal LLM statute-reading QA**: does the LLM read statutes well enough that its extracted `StateMasterRecord` fields agree with independent human-rater datasets?

PRI 2010 is one such dataset and is already wired up. But single-rubric calibration is weak validation: **Newmark 2017 found r=0.04 correlation between CPI Hired Guns 2007 and PRI 2010 disclosure-law scores on the same 50 states**. Different rubrics measure different constructs of the same statute. An LLM that calibrates perfectly to PRI alone could have near-zero correlation with CPI and still be "right" — or it could be *overfitting* PRI's idiosyncrasies. We can't tell from PRI alone.

Adding independent rubrics turns the calibration into a test of **frame-robustness**: does our LLM's statute-reading produce extractions that multiple unrelated human-rater datasets cross-validate? If so, the extraction is real reading, not pattern-matching to one rubric's framing.

## What stays unchanged

Phases 1–5 of the original charter remain load-bearing and are not affected:

- **Phase 1** (Justia retrieval audit, 49/50 state eligibility) — complete.
- **Phase 2** (5-state subset curation + retrieval pipeline) — complete.
- **Phase 3** (baseline dispatch against PRI 2010, 5 states × 3 runs × 2 rubrics) — complete, 0% exact-match agreement observed.
- **Phase 4** (H1 bundle expansion with `support_chapters`) — **in progress**. Blocks Phase 5 and all subsequent phases in this plan.
- **Phase 5** (post-H1 agreement measurement on PRI) — pending Phase 4.

The framework-agnostic infrastructure also stays:

- `src/scoring/justia_client.py` (retrieval)
- `src/scoring/statute_retrieval.py` + `statute_loader.py` + `bundle.py` (bundle construction)
- `src/scoring/calibration.py` + `consistency.py` (agreement + variance metrics)
- `src/scoring/orchestrator.py` subcommands (`audit-statutes`, `retrieve-statutes`, `export-statute-manifests`, `calibrate-prepare-run`, `calibrate-finalize-run`, `calibrate-analyze-consistency`, `calibrate`)
- `StatuteRunMetadata` + related models

All of these were designed rubric-agnostic. Extension is additive.

## What gets added

### Phase 6 — CPI Hired Guns 2007 as second rubric

**Why first:** CPI is the rubric Newmark 2017 compared directly against PRI; r=0.04 is the load-bearing empirical anchor. Running CPI gives us the most direct cross-rubric signal.

**Inputs to transcribe:**

- **CPI Hired Guns rubric** — 48 questions, 100-point scale, 5 categories with weights (per `PAPER_SUMMARIES.md`). Categories include Enforcement (15 pts) and Revolving Door (2 pts) that PRI 2010 and FOCAL both exclude. Source: CPI website / archive.org.
- **CPI Hired Guns 50-state scores** — per-state per-category point totals. Same source.
- **CPI rubric CSV** — structured transcription in `src/scoring/rubrics/` (new) or `data/rubrics/`, analogous to the PRI 2010 CSVs.

**Scorer prompt variant:** The scorer prompt is currently PRI-specific. Extract the rubric-specific sections into a template; parameterize by rubric. Expected: ~1 day of prompt engineering per rubric variant.

**Agreement target:** don't set a number yet. Measure first. Expect CPI agreement to DIFFER from PRI agreement — if they're identical, the LLM is overfitting. The signal is the *pattern* of per-state residuals, not a single number.

**Pilot scope:** same 5 states as Phase 3 (CA/TX/NY/WI/WY). Per-state CPI human scores exist for all 50, so no subset-selection needed.

### Phase 7 — Sunlight 2015 as third rubric

**Why next:** per `PAPER_SUMMARIES.md`, the Sunlight 2015 per-state category scores are already in machine-readable CSV form (5 categories + state-statute + state-portal URLs). Minimal transcription cost — just locate the CSV and bring it into the repo.

**Inputs:**

- **Sunlight 2015 rubric** — 5 categories (Lobbyist Activity / Expenditure Transparency / Form Accessibility / Lobbyist Compensation / Expenditure Reporting Thresholds). Ordinal A-F letter grades per category.
- **Sunlight 2015 50-state scores** — verified CSV exists.

**Note:** Sunlight's "Expenditure Reporting Thresholds" is reverse-scored (high threshold exemption = worse). Mirrors PRI's B1/B2 reverse convention; scorer prompt needs explicit guidance (handled once per reverse-scored category).

**Overlap with FOCAL:** Paper summary maps Sunlight's categories to FOCAL subsets. That overlap isn't directly useful for calibration (FOCAL doesn't have state-level human-rater scores), but it's context for compendium mapping later.

### Phase 8 — Newmark 2005/2017 as fourth/fifth rubric

**Why:** Newmark 2017 is the paper that generated the r=0.04 cross-rubric finding. Running Newmark's own rubric on the same LLM pipeline lets us test the prediction directly.

**Inputs:**

- **Newmark 2005 index** — per-state regulation index, 1990–2003 time series. Verify from the paper whether 2010-era values are recoverable.
- **Newmark 2017 index** — updated per-state scores. Per `PAPER_INDEX.md`, this was a 4-rubric comparison; confirm whether Newmark introduced his own ratings or just compared existing ones.

**Caveat:** Newmark may already BE a composite of CPI + PRI + Sunlight (would need paper re-read to verify). If so, running it as independent ground-truth is muddled; use as a secondary cross-check rather than primary calibration.

### Phase 9 (optional) — OpenSecrets 2022 as sixth rubric

**Why optional:** OpenSecrets 2022 covers only 19 of 50 states ("states with meaningful data available"). Partial coverage is high-signal on the 19 but leaves 31 uncalibrated against this rubric. Whether worth the plumbing depends on whether the 19 include our 5 pilot states.

**Decision gate:** check OpenSecrets 2022 state list against CA/TX/NY/WI/WY. If ≥ 3 are covered, run Phase 9. Otherwise skip.

### Phase 10 — Cross-rubric variance analysis

**Hypothesis:** Our LLM's per-state cross-rubric variance should approximately match Newmark 2017's observed r=0.04 floor between human raters on CPI vs. PRI-disclosure. Concretely:

- Compute Spearman correlation between LLM's per-state total scores across each pair of rubrics (PRI-disclosure × CPI, PRI-disclosure × Sunlight, CPI × Sunlight, etc.).
- Compare to the human-rater pairwise correlations reported in Newmark 2017.

**Interpretation:**

- LLM cross-rubric correlations ≈ human cross-rubric correlations → LLM is reading statutes normally. **Calibration success.**
- LLM cross-rubric correlations >> human → LLM collapsed distinct frames; overfit. Go back to scorer prompt engineering.
- LLM cross-rubric correlations << human → LLM is reading inconsistently across rubrics; possibly a prompt-robustness issue. Investigate.

**Output artifact:** `results/<date>_cross_rubric_variance.md` with a 4-rubric (PRI-disclosure, PRI-accessibility-if-retained, CPI, Sunlight) × 5-state Spearman matrix + comparison to Newmark 2017 baseline.

## Work estimate

Rough, not committed:

- Phase 4 (H1 bundle expansion, PRI-only) — 1–2 sessions. **Prerequisite to all below.**
- Phase 5 (PRI agreement re-measurement) — 1 session.
- Phase 6 (CPI): 2–3 sessions (rubric transcription + scorer prompt variant + dispatch + analysis).
- Phase 7 (Sunlight): 1–2 sessions (CSV location + scorer prompt + dispatch).
- Phase 8 (Newmark): 1–2 sessions, pending paper re-read for independence.
- Phase 9 (optional): 1 session if pursued.
- Phase 10 (cross-rubric analysis): 1 session, runs off all prior phases' artifacts.

Total: 7–11 sessions if all phases run. Could be 2 fellows working serially on a single branch, or 1 fellow over a few weeks.

## What this plan does NOT cover

- **Track B — Extraction pipeline.** Populating `LobbyingFiling` records from portal snapshots + PDFs is a separate workstream. Not covered here.
- **Matrix export tooling.** The N × 50 × 2 matrix is a projection over `StateMasterRecord` + `ExtractionCapability`. Implementation is downstream; not blocked by multi-rubric calibration.
- **Corda Rubric.** We don't have one; we catalog, not grade. Explicitly out of scope.

## Files this plan expects the implementing agent to touch

**Create:**
- `docs/active/<new-branch>/RESEARCH_LOG.md`
- `docs/active/<new-branch>/plans/` (any sub-plans per phase)
- `src/scoring/rubrics/cpi_2007.py` + CSV transcriptions (and similar for Sunlight, Newmark)
- `results/<date>_*.md` per-phase outputs
- Rubric-specific scorer prompt modules

**Modify:**
- `src/scoring/calibration.py` — parameterize by rubric (currently hardcoded to PRI CSVs)
- `src/scoring/orchestrator.py` — `--rubric` flag on calibrate subcommands

**Don't touch:**
- `src/lobby_analysis/models/` — v1.1 shape is stable; no schema changes needed for multi-rubric calibration.
- `src/scoring/justia_client.py` / `statute_retrieval.py` / `bundle.py` — rubric-agnostic; no changes.
- `docs/historical/pri-calibration/` — archived after merge; don't modify, just reference.

## Open questions for the implementing agent

1. **Where do rubric CSVs live?** Option A: `src/scoring/rubrics/` alongside code. Option B: `data/rubrics/` adjacent to other data artifacts. Option C: `docs/historical/pri-calibration/results/` was where PRI's lived — but those are archived. Recommendation: `data/rubrics/` (new directory, gitignored data-ish but committed since these are small structured text files).

2. **Scorer-prompt template structure.** Current scorer prompt hardcodes PRI rubric items. Refactor into a template that takes rubric-items as input? Or keep one scorer prompt per rubric, duplicating statute-retrieval / bundle-loading scaffolding?

3. **Accessibility rubrics vs. disclosure-law rubrics.** CPI, Sunlight, and OpenSecrets mix accessibility items with disclosure-law items in their scoring (unlike PRI which splits them into two separate rubrics). Treat mixed rubrics as single-input, or pre-filter to disclosure-law subsets for calibration-against-statute validity? Pre-filtering avoids the "portal-feature rubric against statute text" mismatch that descoped PRI's accessibility rubric from calibration (2026-04-20 decision).

4. **PRI 2010 accessibility as a pilot for mixed rubrics?** Descoped from the original calibration because portal-feature rubric ≠ statute text. But if we can cleanly identify subsets of CPI / Sunlight / OpenSecrets that ARE statute-derived vs. portal-derived, the descoping pattern generalizes.

## Success criteria

- PRI single-rubric agreement lifts off 0% post-H1 bundle expansion (**Phase 5 gate; prerequisite**).
- CPI single-rubric agreement measurable at a level comparable to PRI's post-H1 agreement (Phase 6).
- Cross-rubric Spearman correlations across ≥ 3 rubrics on 5 pilot states fall within ±0.2 of Newmark 2017's observed human-rater cross-rubric correlations (Phase 10).

Hitting all three = calibration has validated the statute-reading pipeline. Track A (statute verification) can then scale from 5 pilot states to all 50 with confidence.

Failing any of them = diagnostic, not catastrophic — each failure mode localizes a different problem (retrieval, prompt-robustness, frame overfitting). The plan is designed to surface those distinctly.
