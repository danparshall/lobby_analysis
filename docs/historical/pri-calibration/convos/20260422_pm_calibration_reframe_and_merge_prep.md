# Calibration reframe + merge-to-main prep

**Date:** 2026-04-22 (pm)
**Branch:** pri-calibration (updating in place ahead of merge to main)
**Picking up from:** 2026-04-22 (am) landscape brainstorm (`convos/20260422_landscape_brainstorm_and_v11_scoping.md`) + data-model-v1.1 implementation session (other branch, now merged to main as of `5c7c02c`).

## Summary

Three things happened this session, in order:

1. **Archival sweep on main.** After merging `data-model-v1.1`, cleaned up `docs/active/` on main by moving `scoring`, `pri-2026-rescore`, and `focal-extraction` to `docs/historical/` — all three had been merged but never archived per the lifecycle. `docs/active/` on main is now empty; all research lines are either merged-and-archived or live on unmerged branches.

2. **Reflection on pri-calibration's role.** After the 2026-04-22 (am) reframe from "we score states" → "we catalog the universe of required-vs-available", pri-calibration's original charter (PRI-only calibration → produce defensible 2026 state scores) is dead as a public-output path. Its stable role going forward is **LLM statute-reading QA harness** — does the LLM read statutes well enough that its extracted `StateMasterRecord` fields agree with independent human-rater datasets? PRI 2010 is one such dataset; Newmark 2017's r=0.04 cross-rubric correlation finding means single-rubric agreement isn't enough — our LLM could overfit PRI's frame. Broadening to CPI Hired Guns 2007 + Sunlight 2015 + Newmark 2005/2017 (+ OpenSecrets 2022 for the 19 covered states) tests whether our extraction is *frame-robust* rather than PRI-specific. This is a stronger form of the same mission, aligned with v1.1's compendium-first data model.

3. **Merge-to-main decision.** With the reframe articulated and data-model-v1.1 already on main, pri-calibration's infrastructure (Justia retrieval, bundle construction, scorer dispatch, consistency measurement — all framework-agnostic) is ready to land. Fellow onboarding needs this tooling on main before work can split between the two tracks. Updating docs on pri-calibration, merging, archiving to `docs/historical/pri-calibration/`, then letting new fellow-owned branches carry the work forward.

## Topics explored

- **What's pri-calibration actually serving for?** Read the branch's own `RESEARCH_LOG.md` + the 2026-04-22 (am) landscape convo. The RESEARCH_LOG already says "internal QA for LLM statute-reading reliability, not a public scoring output" — the reframe was articulated by the brainstorm, not invented today. What today's session added was the multi-rubric extension.

- **Sequence concern.** H1 (bundle scope missing cross-referenced support chapters) is confirmed but not fixed; the PRI-only baseline is still at 0% exact-match agreement. Broadening to multi-rubric calibration before PRI agreement lifts off the floor would dilute signal — if the LLM can't hit any ground truth, the problem is retrieval (upstream) not ground-truth coverage (downstream). Sequence locked: finish H1 → land a credible PRI single-rubric pilot → *then* broaden to CPI/Sunlight/Newmark. This affects plan-phase ordering but not the data-model or infrastructure.

- **Which prior datasets actually have per-state human-rater scores?** Verified against `PAPER_SUMMARIES.md`:
  - **PRI 2010** — 50 states × disclosure-law + accessibility rubrics. Transcribed to CSV already (`docs/historical/pri-2026-rescore/results/pri_2010_*_scores.csv`).
  - **Sunlight 2015** — "Explicit per-state category scores in machine-readable CSV — directly usable for calibration" (per paper summary). Needs to be located/added to the repo if not already.
  - **CPI Hired Guns 2007** — 48-question rubric, 100-point scale, all 50 states. Rubric + scores need transcription from the CPI site/archive.
  - **Newmark 2005** — "Measuring State Legislative Lobbying Regulation, 1990–2003" — time-series per-state index. Needs verification.
  - **Newmark 2017** — "Lobbying Regulation in the States Revisited" — comparison of 4 rubrics on 50 states. The r=0.04 finding lives here.
  - **Opheim 1991** — Early per-state study; lower priority given age.
  - **OpenSecrets 2022** — 19 states with "meaningful data available" scored. Subset-only but high-signal.

- **Newmark 2017 r=0.04 as a hypothesis test.** Not just an empirical justification for multi-rubric coverage — it's a *predicted outcome* our calibration can measure. If our LLM reads statutes "normally" (same as human experts do), its cross-rubric variance on 50 states should approximately match Newmark's r=0.04 floor. Much higher cross-rubric correlation (e.g., r=0.9) would suggest the LLM collapsed distinct rubric frames into one, overfitting whichever we calibrated first. Cross-rubric variance becomes a first-class calibration metric, not an afterthought.

- **Fellow-task split decision.** Per Dan: two sides to the project deliverable.
  - **Track A — Verify lobbying laws.** Populate `StateMasterRecord.field_requirements[]` via statute reading: for each state × each compendium item, is it Required / Optional / Not Applicable / Unknown? Legal citations, framework_references, evidence_source. This is where pri-calibration's infrastructure lives.
  - **Track B — Pull disclosure data.** Populate `LobbyingFiling` records via extraction pipeline (scrapers + LLM-based field extraction from portal snapshots + PDFs). Where `ExtractionCapability` gets populated. The pipeline side.
  - The matrix (N × 50 × 2) is produced by joining Track A's SMRs with Track B's `ExtractionCapability` (for Practically Available) + spot-checks against actual filings.
  - Fellow assignments: Dan-decided, not agent-decided. This session only surfaces the split; fellow-to-track mapping happens in a later session.

## Provisional findings

- **pri-calibration's role is now clearly scoped:** internal LLM-reading QA across multiple ground-truth rubrics, feeding Track A (statute verification).

- **The infrastructure is framework-agnostic already.** Justia retrieval retrieves law regardless of rubric; orchestrator subcommands are rubric-parameterized; consistency code refactored last session to support arbitrary rubric paths. Broadening to additional rubrics is additive (scorer prompt variants, rubric CSVs, human-score CSVs), not a rewrite.

- **Data-model v1.1 supports this natively.** `FrameworkReference` + `framework_references: list[...]` already name all the target rubrics as first-class citation targets. `EvidenceSource = Literal["statute_verified", ...]` carries the reliability tag for Track A outputs. No data-model changes needed to support multi-rubric calibration.

- **Sustainability-adjacent observation:** the compendium + matrix + bulk data is the publishable artifact; multi-rubric calibration is internal QA. We do not ship "states ranked by rubric X." That framing stays stable post-fellowship.

## Decisions made

- **Multi-rubric calibration adopted** as pri-calibration's forward direction. New plan doc `plans/20260422_multi_rubric_calibration.md` captures the extension (Phases 6–10 added on top of the existing PRI-only charter). Old charter (`plans/20260417_pri_ground_truth_calibration.md`) remains as history of how we got here; superseded-not-deleted.

- **Sequence:** H1 bundle expansion → PRI single-rubric agreement uplift → then broaden. Locked until PRI baseline moves off 0%.

- **Merge pri-calibration to main this session.** Rationale: the infrastructure is stable, the reframe is articulated in docs, fellow onboarding needs the tooling on main. Merge includes all 34 commits + the updated docs from this session.

- **Archive pri-calibration docs on merge.** `git mv docs/active/pri-calibration → docs/historical/pri-calibration` as part of the main commit. Continuing the lifecycle pattern we just reinforced with the 3-branch sweep; the statute-verification track continues on a *new* branch cut by whichever fellow owns it.

- **Fellow-task split framing captured for Dan.** Track A (statute verification) vs. Track B (extraction pipeline). Assignment decision deferred to Dan; this session only articulates the split. Neither track starts on pri-calibration — both get fresh branches off main post-merge.

## Results / artifacts produced

- `convos/20260422_pm_calibration_reframe_and_merge_prep.md` — this file.
- `plans/20260422_multi_rubric_calibration.md` — the multi-rubric extension plan.
- `RESEARCH_LOG.md` trajectory entry for this session.
- Merge commit on `main`: pri-calibration infrastructure landed + docs archived.
- (Before this session) `data-model-v1.1` shipped on main (`5c7c02c`); `scoring`/`pri-2026-rescore`/`focal-extraction` archived on main (`4d59d8b`).

## Open questions

**For Dan:**

- **Fellow-task assignment.** Which fellow takes Track A (statute verification / multi-rubric calibration)? Which takes Track B (extraction pipeline)? What's the state-partition (5–8 priority states each, or split by axis with all states)?
- **CPI Hired Guns transcription scope.** The 48-question rubric + 50-state scores need transcription before Phase 6 can run. Agent or fellow task? Plan defaults to "next agent picks this up" but Dan may have preferences.
- **Sunlight 2015 CSV location.** `PAPER_SUMMARIES.md` says the CSV exists and is machine-readable. Is it in the repo already under `papers/` or does someone need to recover it?
- **Sustainability decision still open.** Per 2026-04-22 (am): civic-tech home / independent project / 2026-snapshot-plus-code. Not urgent, flagged again for future consideration.

**For the next pri-calibration-successor-branch agent (Track A):**

- Bundle-expansion curation: hand-curate `support_chapters` for CA/TX/NY/WI/WY per H1. Pilot states already have primary `lobbying_chapters`.
- Does `build_statute_subagent_brief` need a prompt update distinguishing primary vs. secondary statute roles? (Carried-over from 2026-04-21.)

**For the Track B (extraction pipeline) starter branch:**

- Decide seed-state (CA is typical — highest-quality portal + already has snapshot corpus).
- Decide pipeline architecture: reuse scoring branch's subagent-dispatch pattern, or fresh design per Bacik/Kim 2025 prior art?
- Integration point: `LobbyingFiling` models are in place (v1.1 shipped); `ExtractionCapability` model exists and is waiting for population.

## Next steps

1. Write the new multi-rubric plan (`plans/20260422_multi_rubric_calibration.md`).
2. Update `RESEARCH_LOG.md` with this session's trajectory entry.
3. Commit + push on pri-calibration.
4. Switch to main; merge pri-calibration (resolve STATUS.md + pyproject.toml conflicts); run full test suite.
5. Archive: `git mv docs/active/pri-calibration docs/historical/pri-calibration`.
6. Update STATUS.md on main (archive row, empty Active Research Lines table, Current Focus reflecting post-merge state).
7. Commit + push main.
8. Hand back to Dan for fellow-split decisions.
