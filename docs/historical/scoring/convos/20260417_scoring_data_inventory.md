# 2026-04-17 — Scoring data inventory

**Branch:** `scoring`
**Machine:** desktop (Dan's DC machine)
**Duration:** Brief session — inventory + logistics only

## Context

Picked up the `scoring` branch to assess what data remains to be collected for Phase 3+. Phases 1–2 (pipeline build + CA dry-run) were completed 2026-04-14 on a different machine; the branch code is on the remote at `86d1003`.

## Finding: `data/` directory is missing on this machine

The scoring pipeline and all Phase 3+ work depend on `data/`, which contains:

- **Portal snapshots** (`data/portal_snapshots/<STATE>/2026-04-13/`) — 50 states, 981 artifacts, ~350 MB. Frozen evidence corpus with per-file sha256 in `manifest.json`.
- **Seed URLs** (`data/portal_urls/<ABBR>.json`) — 50 role-labeled URL JSONs.
- **Flagged seeds** (`data/portal_urls/_flagged.md`) — 15 states with non-200 URLs needing manual re-verification.
- **CA dry-run scores** (`data/scores/CA/2026-04-13/bc11ca624efc/`) — 174 rows across 3 rubrics, provenance-stamped.

This data exists on Dan's laptop. It was never committed (gitignored by design — too large and the snapshots are the reproducibility anchor, not the pipeline). The desktop has never had a copy.

## Decision

Continue scoring work on the laptop where the data already lives, rather than re-collecting or transferring ~350 MB.

## What needs to happen next (on the laptop)

### Immediate (Phase 3 — Pilot)

1. Ensure `data/` is in place (or symlinked) in the scoring worktree on the laptop.
2. Run CA, CO, WY with 3 independent temp-0 runs each, all 3 rubrics per run.
3. Compute inter-run disagreement rate per rubric. If >10% of items disagree, pause and sharpen rubric.
4. User reviews pilot scores against snapshots.

### After pilot (Phase 4 — Full 50-state run)

5. Launch subagents across remaining 47 states; pilot states stay fixed.
6. Orchestrator checkpoints per-state; partial failures don't force re-runs.
7. Self-consistency check on all 50. Disagreements → `human_review_queue.csv`.

### Deliverable (Phase 5 — Synthesis)

8. Per-rubric summary docs: per-state totals, per-category sub-totals, `coverage_tier` annotations.
9. Update STATUS.md and RESEARCH_LOG.md.
10. Push. Notify collaborators.

### Deferred / parallel

- **Cross-machine data sync** — need a strategy for keeping `data/` available on both desktop and laptop. Not blocking scoring work but will matter for collaboration. Options to consider: rsync, rclone to cloud storage, external drive, or a shared NAS.
- **Playwright supplementation** for AZ, VT, and ~10 SPA-shell states — separate workstream, doesn't block Phase 3–4 for the other 40+ states.

## Actions taken this session

- Created `data/` in main worktree on desktop (gitignored, empty placeholder).
- Symlinked `data/` into scoring worktree.
- No code changes. Branch still at `86d1003`.
