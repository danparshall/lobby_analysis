# 2026-04-17 — pri-calibration branch kickoff + retrieval architecture

**Date:** 2026-04-17
**Branch:** pri-calibration (newly cut from `scoring`)
**Parent plan:** `docs/active/pri-calibration/plans/20260417_pri_ground_truth_calibration.md` (authored on `scoring` and carried here with amendments)
**Sub-plan:** `docs/active/pri-calibration/plans/20260417_statute_retrieval_module.md`

## Summary

Picked up the PRI 2010 ground-truth calibration plan authored on the `scoring` branch after the pilot's same-host snapshot limitation was surfaced. Did the Phase 0 methodology audit (read the PRI 2010 paper in detail) and hashed out the retrieval architecture with Dan. Three material updates to the original plan:

1. **PRI 2010 did NOT publish an IRR.** The methodology was single-coder preliminary analysis + state-official review (34/50 responded). This kills the plan's original "match PRI IRR" convergence target. New target-setting approach: defer to after a baseline measurement (Phase 3), then set by discussion (fiat target, or bootstrapped via pilot hand-scoring). Add trust-weighting: the 31 responder states that confirmed/corrected are higher-trust ground truth than the 16 non-responders.
2. **Justia serves both 2010 AND current statutes** via stable URLs (`law.justia.com/codes/<state>/<year>/`). Replaces the original Wayback-primary retrieval architecture with a unified Justia-only retrieval module. Coverage is per-state uneven (e.g., CO only goes back to 2016, confirmed by Dan's Wayback check to reflect actual 2010 availability, not a Justia gap). Eligibility rule: ±2 year tolerance, prefer pre-2010 on ties (since PRI scored late-2009 law).
3. **Branch cut from `scoring`, not `main`** (contrary to the original plan's instruction). The calibration line continues the scoring work — the pilot's statute-vs-portal gap motivated this pivot, and we need `src/scoring/`'s orchestrator + pipeline scaffolding. "Orthogonality" is preserved: independent research conclusions, shared code.

## Topics Explored

- Phase 0 ground-truth audit: read paper methodology section. Confirmed binary yes/no rubric, no weighting, B1/B2 reverse-scored, scoring vintage late-2009 law, single-coder + state-official-review validation (no IRR), per-item codings not published (Dan messaged original authors; pending).
- IRR explanation to Dan: what it measures, why we can't hit PRI's (it doesn't exist), alternative target-setting approaches.
- Retrieval architecture options: Westlaw/Lexis (overkill, expensive), HeinOnline (good for historical, mid-cost), Justia (free, unified, the winner), Wayback (fallback for states Justia doesn't cover).
- Verified Justia has historical state codes at stable URLs (Dan's TN 2010 example). Discovered Justia's curl-block (Cloudflare) — use realistic UA or WebFetch.
- Decided on ±2 year tolerance with asymmetric direction logging (pre/exact/post, prefer pre on ties).
- Chapter-level availability check: Justia sometimes hosts a year with only a subset of titles. Eligibility requires the lobbying/ethics title to actually be present in the chosen year.
- Branch strategy: cut from `scoring` (not `main` per original plan), because the Python package we build on lives there and sharing scaffolding doesn't compromise research orthogonality.
- Implementation approach: extend the existing `scoring.orchestrator` CLI with new subcommands (`audit-statutes`, `retrieve-statutes`) rather than throwaway scripts. Aligns with Dan's feedback memory and keeps retrieval reusable.

## Provisional Findings

- **PRI 2010's 31 responder states are higher-trust ground truth.** Non-responder disagreements may reflect PRI error, not LLM error. Calibration metrics should partition on this.
- **Scoring atomically, comparing at sub-aggregate level** is the right data-collection strategy (Dan's call). If per-item codings arrive from the original authors, we can re-run the comparison without re-scoring.
- **Justia coverage is the gating constraint** for calibration-pool size. If < 20 states have a ±2-year match, we re-scope.
- **Per-state vintage variance will create noise in 2010 calibration.** A state using 2012 Justia to compare against PRI's late-2009 scoring will show "disagreement" even with a perfect LLM if the law changed 2010–2012. Trust-weighting + direction logging is how we distinguish real LLM error from vintage drift.

## Decisions Made

- **Branch name:** `pri-calibration` (not `pri-2010-calibration` — shorter, since the work isn't strictly about 2010 alone; we're producing both 2010 calibration AND 2026 scoring).
- **Branch base:** `scoring`, not `main`. Plan doc amended to reflect this.
- **Convergence target:** deferred to post-baseline. No hardcoded target. Candidates: 90% exact agreement on responder-subset, or bootstrapped via pilot hand-scoring.
- **Retrieval source:** Justia for both vintages. Wayback and HeinOnline are fallbacks only if Phase 1 eligibility is low.
- **Score atomically, compare at sub-aggregate level.**
- **±2 year tolerance, pre-preferred on ties.**
- **Phase 1 is a single script** (one CLI subcommand), not 50 dispatches, per Dan's batch-scripts feedback memory.
- **Implementation via TDD** per Nori workflow.

## Results

None yet in `results/`. First artifact is the 50-state Justia audit CSV produced by running the `audit-statutes` subcommand at the end of Phase 1 implementation.

## Open Questions

- **Convergence target value** — to be set after Phase 3 baseline numbers are in. Could be 90% exact agreement, or a hand-score-bootstrap target.
- **Per-item PRI codings** — Dan has messaged authors. If they arrive, we can calibrate per-item instead of at sub-aggregate level. Either way, the atomic data collection covers the case.
- **Composition with `scoring` branch** — if this calibration succeeds, do we merge the calibrated prompt back into `scoring` and re-score the 2026-04-13 portal snapshot corpus, or treat the statute-based pipeline as producing the canonical 2026 scores? Decision after Phase 6.
- **FOCAL** — no 2010 analog, can't be calibrated this way. Stays on the `scoring` branch with whatever prompt-sharpening the portal side settles on.

## Next Steps

1. Read the test-driven-development skill.
2. TDD-implement `justia_client.py`, `statute_retrieval.py`, `statute_loader.py`, and the two orchestrator subcommands per the sub-plan. Write tests first, capture Justia HTML fixtures, implement until green.
3. Run `audit-statutes` across all 50 states; commit CSV + methodology note.
4. Decision point: is the eligible calibration pool big enough to proceed?
