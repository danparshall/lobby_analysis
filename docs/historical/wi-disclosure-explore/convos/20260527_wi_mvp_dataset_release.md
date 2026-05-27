# wi_mvp_dataset_release

**Date:** 2026-05-27
**Branch:** main (post-archive addendum — packaging task on the archived `wi-disclosure-explore` output)
**Related commit:** [`6dda3f1`](https://github.com/danparshall/lobby_analysis/commit/6dda3f1) `releases/wi: MVP snapshot of 2025-2026 WI lobbying disclosure data`

## Summary

Packaged the merged `wi-disclosure-explore` Tier-2 output as the first MVP data release for sharing with collaborators. Six canonical TSVs (944 principals / 773 lobbyists / 2,254 authorization edges / 1,706 principal filings / 3,092 lobbyist filings / 7,345 bill-effort rows; ~2.9 MB total) plus a `README.md` with provenance, schema notes, headline aggregates, and caveats. Committed to `main` under the new path `releases/wi/`.

The session was a packaging exercise, not a research session. The substantive judgment calls were (1) what counts as the "canonical" set of files (the six Tier-2 outputs from `tier_2_materialize_cli` + the unified authorization TSV — *not* the two side-only authorization TSVs subsumed by it, *not* the directory XLS inputs, *not* the smoke / sample / checkpoint dirs), (2) where in the repo a published data snapshot should live (new `releases/` convention, distinct from gitignored `data/`), and (3) whether to work on a branch or directly on `main` (user chose `main` for the small packaging task, knowing `CLAUDE.md` says otherwise — flagged once in the convo, then proceeded).

## Topics Explored

- Surveying the wi-disclosure-explore output on disk to identify the canonical set vs the intermediate artifacts (checkpoints, smoke dirs, side-only authorization TSVs, XLS directory inputs)
- Verifying the on-disk TSVs reflect the post-address-fix state (`fbd8a4c`) — spot-checked Brooks 11052 row, confirmed clean `"1 S. Pinckney Street, Suite 318\nMadison, WI 53703"` (no phone or firm-name leak)
- What goes in the release README — schema tables, headline aggregates from the results doc, the seven caveats (Pettack outlier, low-spend-exempt, 56 zero-filing principals, Neumann-Ortiz null-html silent skip, address sub-field split open follow-up, Nels Rude duplicated state-zip portal artifact, "WCTA" acronym ambiguity)
- Multi-committer-repo etiquette for the first non-gitignored data file — flagged the precedent-setting nature to the user; `releases/` naming chosen to signal "deliberately-published snapshot," distinct from any future scrape outputs that should stay under gitignored `data/`

## Provisional Findings

- **The six-TSV canonical set hangs together cleanly** as a normalized relational bundle. `principal_id` / `lobbyist_id` join across all six files; the unified authorization TSV gives the lobbyist↔principal edge graph with `discovered_via` provenance; the bill-efforts file decomposes each principal-side filing into per-bucket per-item allocations. No file is structurally redundant within the set.
- **~2.9 MB is a comfortable size for git** — well within the range git handles fine for text files, large enough that GitHub's web UI will preview rather than blame, small enough that nobody cloning the repo will notice. The bill-efforts file at 1.2 MB is the largest single file but doesn't approach concern territory.
- **The `releases/wi/README.md` is the primary contract for downstream consumers** — schema definitions, provenance pointer to the generating commit, caveats. The Pydantic models in `src/lobby_analysis/models/` are the secondary contract (linked from the README). The results doc in `docs/historical/wi-disclosure-explore/results/` is the tertiary depth-reference (also linked).

## Decisions Made

- **`releases/wi/` is the path.** New convention: deliberately-published data snapshots live under `releases/<state-or-collection>/`. Distinct from gitignored `data/` (which stays the home for scrape outputs and scratch artifacts).
- **Six TSVs included; nothing else from `data/disclosures/WI/`.** Excluded: the two side-only authorization TSVs (subsumed by the unified one), the XLS directory inputs (raw scrape, not output), the smoke / sample / checkpoint subdirectories.
- **Generating commit cited in the README as merge commit `5fcc6ac`.** The address fix `fbd8a4c` is included in that merge; user did not opt to cite the fix commit directly when offered the choice (left as default).
- **Worked directly on `main` with no branch** per user choice; documented as a deliberate exception to `CLAUDE.md`'s "no changes directly on main" rule (one-line packaging task, no risk surface).

## Results

The release itself is the result: [`releases/wi/`](../../../../releases/wi/) on `main` (commit `6dda3f1`). README: [`releases/wi/README.md`](../../../../releases/wi/README.md).

No new files under `results/` for this session — the headline aggregates already live in [`results/20260526_wi_tier_2_parser_results.md`](../results/20260526_wi_tier_2_parser_results.md) (the original run-results doc, which the release README references and summarizes).

## Open Questions

- **Should other fellows / Suhan be notified of the new `releases/` convention?** Flagged to the user at end-of-session; not actioned. A note in the next weekly Corda update would be the lightest-weight way to land it.
- **Is `releases/` the right name?** Alternatives considered: `data/published/` (would have required `.gitignore` exception), `snapshots/`, `published/`. `releases/` won on signal strength — readers know "this is intended for downstream consumption."
- **Will subsequent state pulls (NC, etc.) want a parallel `releases/nc/` structure?** Assumed yes; not yet a concrete question.
