# 2026-06-05 — Top-10 priority states: 3-vintage statute gap-fill

**Branch:** `api-multi-vintage-retrieval` (worktree `.worktrees/api-vintage`)
**Machine:** Dans-MacBook-Pro
**Result doc:** [`results/20260605_top10_statute_coverage.md`](../results/20260605_top10_statute_coverage.md)

## Ask

Priority-state list updated. New top-10: **NY, CO, WI, CA, TX, IL, WA, FL, NC, OH** (chosen *because of* the `state_bulk_data_availability` chain-closure research). User: "make sure we have data for 3 vintages — 2010, 2015, 2025 — for all of those." Expected "several passes to get all 30 items," asked to start a new branch.

## Two clarifications resolved up front

1. **"Data" = statute / legal text** (the source material for extraction + rubric validation), not bulk filing records. Confirmed via AskUserQuestion. 2010/2015/2025 align with rubric vintages.
2. **Branch:** discovered an *active* branch already doing exactly this — `api-multi-vintage-retrieval` (the Justia multi-vintage pipeline, ~26/30 cells already gathered). Surfaced the collision rather than cutting a duplicate. User chose **resume the existing branch**. No new branch created.

## Scope correction (the main early finding)

Reconciled the new top-10 against the branch's 2026-05-27 inventory. "30 items / several passes" was really **5 gap cells**, not 30 — the other 25 were already complete. The thin cells that looked like stubs (TX 2010/2015 = 1 file, IL 2010 = 3) are **legitimate inline single-page codifications**, confirmed via the branch's own notes — not incomplete fetches. Genuine gaps: **NY 2010 (lossy stub), NY 2015, NY 2025, FL 2010, NC 2010** — 4 of 5 in the top-priority states. No ready-to-fetch URL bundles existed for any of them.

## Execution (one pass, CF clear on Pro)

- **CF probe first** (user-chosen): ran one direct `subagent_fetch_save.py pass1` on FL 2010 — clean 48-title index, no challenge. CF open on Pro.
- **Discovery fan-out** in 2 batches (3-concurrent CF ceiling): FL 2010, NC 2010, NY 2010 → then NY 2015, NY 2025. All 5 via Method-B general-purpose subagents following `plans/_handoffs/20260519_subagent_dispatch_prompt.md`, seeded with per-state regime priors. All CF-clean.
- **Section-fetch:** `scripts/fetch_gap_cells_sections.py` consumed the 5 bundles → 111 section bodies into `data/statutes/<S>/<V>/sections/` via `retrieve_statute_bundle` (PlaywrightClient, 2.5s). CF held through all 111. Size sanity: medians 2.7–4.3 KB, zero <500B.

**Outcome: 30/30 top-10 × 3-vintage cells now have statute text.**

## Findings

- **NY Lobbying Act (Leg. Law Art. 1-A §§1-A…1-V) structurally stable 2010→2025** — same 22 leaves all 3 vintages; JCOPE→COELIG (2022) changed substance, not section structure.
- **NC 2010 = NC 2015** (32-section Ch.120C; the 2 removed sections go by 2025).
- **FL 2010 Method-A helper gap:** flat-sibling Part-page convention not in `_build_justia_link_tsv`'s 4 patterns — empty TSV on `PARTIII.html`, recovered from saved HTML. Needs a 5th pattern. (Discovery only; section bodies fetched fine.)

## Decisions

- Resume existing branch, not new branch (user).
- CF probe-one-then-fan-out (user), taken to its cheapest form (direct pass1 by me before any subagent spend).
- Left NY 2010's pre-existing lossy stub file in place (data-integrity: don't delete experiment data without permission) — flagged in inventory.
- Committed the 5 canary bundles + the fetch driver (matches the branch's reproducibility-bundle norm); did **not** touch the other session's untracked `scripts/canary_discovery.py`.

## Open / next

- **CO substitution validity** (esp. 2010→2016, outside ±5) still needs human review before CO is used as a calibration anchor.
- **OH 52→30 (2015→2025) delta** uninvestigated.
- **Cross-machine sync** of the 5 new cells to Air/tarragon.
- **FL 2010 5th helper pattern** for Method-A automation (today's bundle was Method-B + manual recovery).
- CF stealth-Playwright recommendation **not** retired by today's clean window.
