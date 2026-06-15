# OH extraction provenance fixes — TDD implementation

**Date:** 2026-06-05
**Branch:** oh-portal-aprime-batch

## Summary

Implemented the do-first task from the prior session's plan
(`plans/20260605_extraction_provenance_fixes.md`): the two provenance defects
the 300-filing slice surfaced. Part 1 makes `raw_text` (the `LobbyingFiling`
audit field) code-populated from the fetched source text instead of
model-emitted; Part 2 captures the true OLAC disclosure regime per filing
instead of hardcoding `legislative`. Both done test-first.

Before touching Part 2's parser, the planned Medium-confidence flag on the
`R`→retirement mapping was resolved empirically: a scan of all 2,684 cached
agent FormsFiled pages (364,351 AER rows) showed the OLAC "Category" column
(index 5) takes exactly `L`/`E`/`R` with no blanks — confirming
L→legislative, E→executive, R→retirement_system without a live page fetch.

A `nori-code-reviewer` pass on the finished diff caught one real defect: the
non-legislative warning keyed on the CLI-default constant (`DEFAULT_REGIME`)
rather than the brief's regime, so an unknown-regime (`None`) filing run under
`--include-nonlegislative` emitted the nonsense text "None brief not yet
implemented." Fixed at the root (compare against the literal brief regime; a
distinct branch for `regime is None`) and added the missing test for that path.
The two new commits were pushed (PR #33). The doubled discover cache-path bug
(plan step 21) was deferred to issue #36 rather than fixed, because the fix
isn't authoritative until the branch merges to main — stale-code crawls from
other worktrees would re-create the doubled path.

## Topics Explored

- Empirical OLAC Category→regime confirmation across 364,351 cached AER rows
- Part 1: `raw_text` code-population + schema hiding (TDD)
- Part 2: regime capture in discover → batch → pipeline (TDD)
- Skip-by-default policy for non-legislative AERs (`--include-nonlegislative`)
- Code review + root-cause fix of the unknown-regime warning text
- Branch-cleanliness checks (tests, lint, format, CI, mergeability)
- Why step 21 (cache-path fix) belongs post-merge, not on this branch

## Provisional Findings

- **OLAC Category column is clean and 3-valued.** Across 364,351 cached AER
  rows: `L` 52.3% / `E` 46.9% / `R` 0.8%, zero blanks/unknowns. (This is
  all-years; the 2025–26 slice was ~86/13/1 — different denominators.) So the
  ~14% non-legislative share of the 45,605-filing universe is what
  skip-by-default removes.
- **`raw_text` is exactly recoverable in code.** Confirmed in the prior session
  as byte-identical to `html_to_aer_text(source)`; this session makes the code
  value authoritative (overrides any model value) and removes `raw_text` from
  the model-visible tool schema (also trims output tokens per call).
- **Repo has no CI and is not maintained under `ruff format`.** `.github/`
  absent; PR #33 `statusCheckRollup` empty; pre-existing code fails
  `ruff format --check`. So lint (`ruff check`) is the only style gate.
- **3 `test_pipeline.py` failures are local-data-only** (gitignored `data/`,
  untracked CA `2026-04-13` snapshot) — not a regression, no CI impact.

## Decisions Made

- **Skip non-legislative AERs by default**, behind `--include-nonlegislative`;
  any non-legislative filing actually run gets an `extraction_warnings` entry.
- **`raw_text` stays inline in `filing.json`** (self-contained records).
- **Step 21 (doubled cache path) deferred to issue
  [#36](https://github.com/danparshall/lobby_analysis/issues/36)** — do
  post-merge so stale-code worktrees can't re-double the path; includes the
  cache-migration step.
- Two commits per the plan (`9b0fd7d` Part 1, `629ce28` Part 2), pushed.

## Results

- `results/20260605_olac_category_regime_distribution.md` — the L/E/R Category
  tabulation across all cached agent pages.

## Open Questions

- Executive/retirement extraction briefs don't exist yet; until they do, those
  ~14% of filings are skipped by default. When are those briefs worth building
  vs. just cataloguing the legislative regime first?
- Issue #36 (cache-path migration) — sequence relative to the eventual
  branch→main merge.
- Unchanged from prior session: full-universe extraction via Batches API
  (issue #35).

## Captured Tasks

- [#36: oh_portal discover cache path is doubled](https://github.com/danparshall/lobby_analysis/issues/36) — captured 2026-06-05
