# Research Log: compendium-v2-promote

Created: 2026-05-14
Purpose: **Single-session infrastructure branch.** Promote Compendium 2.0 to the repo-level source of truth and deprecate Compendium 1, before either of the two parallel-running successor branches (`extraction-harness-brainstorm`, `phase-c-projection-tdd`) lands real code on the shared infrastructure surface. Also: remove the now-superseded ⛔ PRI-out-of-bounds banner from STATUS.md.

> **Predecessor:** Cut off `main` at `0b8bf71` (post-`compendium-source-extracts` archive `cac1469` → `7a107ea` rename → `8bfc225` archive → `0b8bf71` noridocs init).
>
> **Originating coordination convo:** [`convos/20260514_compendium_v2_promote.md`](convos/20260514_compendium_v2_promote.md) — analysis of conflict surfaces between `extraction-harness-brainstorm` (Track B) and `phase-c-projection-tdd` (Phase C) successor branches, leading to the decision to do v2-promotion as own branch first.

## Why this branch exists

Both `extraction-harness-brainstorm` and `phase-c-projection-tdd` were cut off main 2026-05-14 as parallel successor branches to the archived `compendium-source-extracts`. Their core deliverables are decoupled (one **produces** compendium cells, the other **consumes** them; the v2 TSV row-freeze is the contract). But they collide on **shared infrastructure** that both would naturally want to touch:

- `compendium/disclosure_items.csv` + `compendium/framework_dedup_map.csv` (v1 / v1.2 PRI-shaped) — both would deprecate
- `docs/historical/compendium-source-extracts/results/projections/disclosure_side_compendium_items_v2.tsv` — v2 TSV in awkward historical path despite being a live contract
- `src/lobby_analysis/compendium_loader.py` — both would update to load v2
- `STATUS.md` ⛔ rule 2 wording — both would flip from "frozen pending rebuild" to "deprecated, use v2"

Doing this infrastructure work as a separate small branch first lets both successors `git pull --rebase origin main` and start with a clean v2 contract at a stable repo path. Eliminates the merge-conflict surface.

## Scope

**In scope (this branch):**

1. File moves: v1 CSVs → `compendium/_deprecated/v1/`; v2 TSV → `compendium/disclosure_side_compendium_items_v2.tsv`
2. Forwarding `.MOVED.md` stub at old historical v2 TSV path
3. New READMEs: `compendium/README.md` (v2 source-of-truth declaration) + `compendium/_deprecated/v1/README.md` (v1 deprecation context)
4. `src/lobby_analysis/compendium_loader.py`: rename existing v1 loader to `load_v1_compendium_deprecated()`; add minimal `load_v2_compendium() → list[dict[str, str]]`; update path constants to new `_deprecated/v1/` location so existing v1-shape tests stay green
5. Path-constant updates in 4 dependent files: `scripts/build_compendium.py`, `src/scoring/orchestrator.py`, `tests/test_compendium_loader.py`, `tests/test_smr_projection.py`
6. 1-2 smoke tests for `load_v2_compendium()` (row count, columns, canonical-row presence)
7. Remove ⛔ PRI-out-of-bounds banner from STATUS.md; record removal in 2026-05-14 Current Focus paragraph
8. Update Active Research Lines table (add this branch's row); minor README.md updates (Project state + Repo layout)
9. Update both successor branches' RESEARCH_LOG row-freeze-contract links to point at the new repo-level path

**Explicitly out of scope (handed to successors):**

- v2-shaped Pydantic models in `src/lobby_analysis/models/` → `extraction-harness-brainstorm` (per user decision: model shape = extraction output shape)
- v2-shaped extraction prompts → `extraction-harness-brainstorm`
- Retiring `cmd_build_smr` / `smr_projection` PRI-MVP code → `phase-c-projection-tdd` when ready (left functional with deprecation docstring for now)
- Per-rubric projection function implementations → `phase-c-projection-tdd`

## Acceptance criteria

- 297 baseline tests + 1-2 new v2-loader smoke tests pass (test_pipeline.py's 3 pre-existing failures are out-of-scope — portal snapshot fixture data not bundled in repo; identical failure mode on main)
- `git grep "compendium/disclosure_items.csv"` returns hits only in `compendium/_deprecated/v1/README.md` + archived `docs/historical/` content
- STATUS.md ⛔ section is gone; ⭐ Compendium 2.0 success criterion is now the top section after title + date
- Both successor RESEARCH_LOG row-freeze-contract links resolve to the new `compendium/` path

## Data symlink note

`data/` does not exist in main worktree (per `ls /Users/dan/code/lobby_analysis/data` at branch creation); no symlink needed per `skills/use-worktree/SKILL.md` quick-reference.

---

## Sessions

(Newest first.)

### 2026-05-14 — Compendium v2-promote: deprecate v1, promote v2 to repo-level, clear PRI banner

Convo: [`convos/20260514_compendium_v2_promote.md`](convos/20260514_compendium_v2_promote.md)

**Topics explored.** Conflict-surface analysis between `extraction-harness-brainstorm` and `phase-c-projection-tdd`; sequencing options for v1→v2 deprecation; v2 TSV's new home; v2 loader return shape (raw dicts vs. typed model); PRI ⛔ banner removal vs. retention.

**Provisional findings.** Successor branches are decoupled on core deliverables (produce-vs-consume; v2 TSV row-freeze is the contract) but coupled on shared infrastructure (loader, paths, models, STATUS.md wording). Own-branch deprecation work eliminates the merge-conflict surface. PRI ⛔ banner's substantive content ("no rubric privileged") survives as ⭐ success criterion #4; banner was emergency posture for a structurally-resolved failure mode.

**Concrete changes.** v1 CSVs moved to `compendium/_deprecated/v1/`; v2 TSV promoted from `docs/historical/...` to `compendium/disclosure_side_compendium_items_v2.tsv` (181 rows × 8 columns); `.MOVED.md` forwarding stub left at old historical path; new `compendium/README.md` + `compendium/_deprecated/v1/README.md`; `load_compendium` renamed to `load_v1_compendium_deprecated` with deprecation docstring; new minimal `load_v2_compendium() → list[dict[str, str]]` (3 smoke tests via real RED-GREEN TDD cycle); 4 dependent path-constant files updated; STATUS.md ⛔ banner removed and v2-promote added to Active Research Lines; README.md Project state + Repo layout sections updated.

**Process notes (raised by user mid-session).** Initially skipped reading `using-skills/SKILL.md` at session start and skipped putting the Nori checklist itself into TodoWrite — remediated by reading 4 skills fresh during the session. Initially wrote `load_v2_compendium` implementation before tests — remediated with a real RED-GREEN cycle (stub → 3 failing tests → restored implementation → 3 passing tests).

**Test status.** 300 pass / 5 skip (3 new v2 smoke tests above the 297 baseline); v1-loader regression suite 34 pass / 5 skip (same as pre-rename). 3 pre-existing failures in `test_pipeline.py` (portal-snapshot fixture data not bundled) confirmed identical on main — not introduced here.

**Next steps / post-merge actions.**
- Both successor branches (`extraction-harness-brainstorm`, `phase-c-projection-tdd`) need their RESEARCH_LOG row-freeze-contract links updated to the new `compendium/disclosure_side_compendium_items_v2.tsv` path after rebasing against post-merge main. Documented in this branch's convo summary; flagged as kickoff-agent action.
- Same for `oh-statute-retrieval` (third successor, not in original conflict-check scope but inherits the same path migration).
- `extraction-harness-brainstorm` owns the v2 Pydantic model rewrite (per same-session decision).

