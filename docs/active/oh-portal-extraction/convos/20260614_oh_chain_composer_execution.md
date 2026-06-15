# OH chain composer — Phases 0–6 execution

**Date:** 2026-06-14
**Branch:** `oh-chain-composer`

## Summary

Picked up the `oh-chain-composer` handoff brief shipped by an earlier session at `f59a7f9` (Phase 1 *classifier* — Steps A+B — was already in; the rest of Phase 1 plus Phases 0, 2–6 were open). Surfaced Q1–Q6 from the canonical plan to Dan via `AskUserQuestion`; all six locked at the plan's recommendations (preview release against the 316-filing slice, primary-only sponsorships, download `oh.csv`, defer expenditures, branch already cut, include minimal filings TSV). One new question discovered during orientation — initial impression was "no data on this machine" because the worktree had no `data/` dir; turned out to be a false-negative read of the convention (Dan's data lake is at `~/data/lobby_analysis/`, symlinked into each worktree as `data → /Users/dan/data/lobby_analysis`).

Phases 0 through 6 then landed end-to-end in TDD: pre-flight audit clean (16/16 CSV schemas stable, 86.4% row-weighted smoke unchanged, 40.8% multi-primary structural finding empirically confirmed, cosponsor-in-actions check negative, `oh.csv` downloaded), five typed loaders + a dedup helper, the chain composer with §4a position-shape handling + §6 OAC/JCARR routing, the gifts composer with `oh.csv` lawmaker resolution, the filings composer with stated-zero + is_current normalizations, an `argparse` CLI with `materialize` subcommand, four release READMEs in the WI release-doc pattern, and the actual preview-release run materializing three TSVs in-tree at `releases/oh/`. Full OH allocation suite ended at 139/139 green.

Real-data smoke surfaced three structural findings worth flagging downstream: 11 duplicate cached extractions for 5 filing_ids (the dedup helper handles); 0 gift-event rows across 316 filings (likely sampling artifact, secondary hypothesis is extraction-prompt scope at `oh_portal/extraction_brief.py` — orthogonal to this branch); and 18 unmatched chain rows that are extraction-side defects (subject text mis-placed in `bill_reference`, OAC variants with colons/Chapter prefix the regex doesn't cover, two malformed `CB ...` identifiers). All three are surfaced honestly in the release READMEs as quality canaries rather than hidden.

## Topics Explored

- Q1–Q6 confirmation gate from the chain composer plan (six open questions the handoff explicitly required closing before Phase 1 loader work)
- Data-location convention check across worktrees (false-negative resolved via `readlink` of an existing worktree's `data/` symlink)
- Phase 0 pre-flight audit — schemas, smoke-test drift check, multi-primary empirical verification, cosponsor-location check, `oh.csv` download
- TDD design + implementation of 5 typed loaders + a canonical-extraction dedup helper
- TDD design + implementation of the bill-side chain composer with §4a position-shape branching and §6 OAC/JCARR routing
- Conservation arithmetic on the chain output (855 unique bill-position joins × avg 1.52 primaries → 1,299 bill chain rows; total 1,589 with non-bill classes)
- TDD design + implementation of the gifts composer with prefix-stripping lawmaker resolver against `oh.csv`
- TDD design + implementation of the filings composer with two strict-guarded normalizations
- CLI design (one `materialize` subcommand → three TSVs with `_preview` suffix)
- Release README authoring (top-level + per-artifact) mirroring the WI release-doc pattern
- Preview-release materialization end-to-end against the real 316-filing cache

## Provisional Findings

- **OH multi-primary sponsorship is structurally common** — 40.8% of bills (substantive HBs/SBs, not just resolutions). Cross-product expansion factor on the chain side is ~1.52 primaries per bill on average; outliers are ceremonial House Resolutions with up to 99 primaries.
- **Cosponsors live cleanly in `OH_136_bill_sponsorships.classification == "cosponsor"`** — the WI lesson (cosponsors in free-text `bill_actions.description`) does NOT apply to OH. v1.1 cosponsor extension is a classification-filter flip.
- **The extraction cache has duplicate filings.** 5 filing_ids carry multiple cached extractions (one has 8). The `select_canonical_extraction` helper (most-recent mtime wins; lex `source_path` tiebreaker) handles this at the loader seam; Phase 2 chain composer invokes it before composing.
- **0 gift-event rows extracted across 316 cached filings.** Almost certainly the 53% nil-rate × sampling-window combination; secondary hypothesis is that `oh_portal/extraction_brief.py` may not be reading AER Sections II.A/II.B fully. The composer code is tested at 14/14 green, and the release README documents the empty state honestly.
- **Classifier–loader–composer integration is consistent** with the 2026-06-11 raw smoke test: 887 `bill_class=='bill'` positions from this session's classifier-loader pass exactly match the 887 row-weighted bill matches in the standalone 06-11 smoke. The composer is faithful to the empirical baseline.
- **§4a position-shape normalization is load-bearing in practice.** The very first row of the materialized chain is Susan M Jagers (Ohio Poverty Law Center) — a `subject_general` position with `description="implementation of HB 29"`. Without §4a, this would have been silently dropped or mis-classified as bill_referenced; the kind-vs-text precedence routes it correctly to `bill_class='subject'` with `confidence='subject_only'`.

## Decisions Made

- **All six plan questions resolved** at the recommended defaults (preview slice, primary-only, download oh.csv, defer expenditures, oh-chain-composer branch was already cut, include minimal filings TSV).
- **Dedup strategy = most-recent extraction by mtime** (lex `source_path` tiebreaker). Filed in `select_canonical_extraction`.
- **`extract_position_label` uses `original_text`, NOT `bill_number`** (open follow-up — flagged in Phase 2 findings and the chain README). Practical impact in the current slice is zero. Worth swapping when the full-corpus run lands.
- **Three open follow-ups deferred** to future PRs/issues: (a) extraction-prompt scope verification for II.A/II.B gifts (separate from this branch), (b) `bill_number`-preferred join key (v0.1), (c) OAC regex widening for colon-subdivided rules / "Chapter" prefix / multi-rule strings (v0.1).

## Results

All produced this session, under `docs/active/oh-portal-extraction/results/`:

- [`20260614_phase0_preflight_audit.md`](../results/20260614_phase0_preflight_audit.md) — Phase 0 findings (schemas, smoke drift, multi-primary, cosponsor location, oh.csv download)
- [`20260614_phase0_preflight_audit.py`](../results/20260614_phase0_preflight_audit.py) — re-runnable Phase 0 audit script
- [`20260614_phase1_loaders_findings.md`](../results/20260614_phase1_loaders_findings.md) — Phase 1 loaders findings + 3 structural findings
- [`20260614_phase1_loaders_smoke.py`](../results/20260614_phase1_loaders_smoke.py) — real-data loader smoke
- [`20260614_phase1_loaders_diags.py`](../results/20260614_phase1_loaders_diags.py) — duplicate-extraction + unmatched-label diagnostic
- [`20260614_phase2_chain_findings.md`](../results/20260614_phase2_chain_findings.md) — Phase 2 chain composer findings + conservation arithmetic + per-class semantics + open follow-ups
- [`20260614_phase2_chain_smoke.py`](../results/20260614_phase2_chain_smoke.py) — real-data chain smoke

**Preview release artifacts** at `releases/oh/`:

- `chain/OH_chain_2025_2026_preview.tsv` — 1,589 rows × 18 cols (~600 KB)
- `gifts/OH_gifts_2025_2026_preview.tsv` — 0 rows, header only (honest empty)
- `filings/OH_filings_2025_2026_preview.tsv` — 305 rows × 14 cols (~220 KB)
- 4 READMEs (top-level + per-artifact)

## Open Questions

- **Are the 0 gift-event rows a sampling artifact or an extraction-prompt scope issue?** The `oh_portal/extraction_brief.py` prompt was built around bill-side positions; a spot-check against an AER PDF that's known to have Section II.A/B content would confirm or rule out. Not Phase-2-blocking, but high-leverage for the full-corpus run's gifts coverage.
- **When the full-corpus run from issue #35 lands (~$800, ~24 hr async), should it re-run this composer in place, or land on a successor branch?** The CLI is parameterized; either path works mechanically. Probably this branch merges first, then a fresh session materializes against the full corpus on main.
- **`STATE_COVERAGE.md` OH footnote 7 — should it be closed now or wait for the merge?** Both halves are now resolved (Plural Policy bundle + `oh.csv`); the footnote update is one-line and could land in this branch. Deferred this session to keep STATUS edits additive.

## Next steps for the next session

1. Review the four release READMEs at `releases/oh/{README.md, chain/, gifts/, filings/}` for tone + completeness.
2. Decide on PR timing — this branch is ready for review and merge per Q1 (preview release scope).
3. After merge: a fresh session can verify the gifts-empty hypothesis (sampling vs. extraction scope) and tee up the full-corpus run from #35.

## Provenance

- **Originating handoff:** [`../HANDOFF_oh_chain_composer.md`](../HANDOFF_oh_chain_composer.md) (shipped at `f59a7f9` by an earlier session)
- **Canonical plan:** [`../plans/20260611_oh_chain_composer_design.md`](../plans/20260611_oh_chain_composer_design.md) (last updated 2026-06-14 with §4a position-shape + Step A/B split + Q6 filings table)
- **Commits this session:** `51a3e1e` (Phase 0), `56f80ca` (Phase 1), `c30defc` (Phase 2), plus the Phases 3–6 + READMEs + preview TSVs commit landing as part of this finish-convo flow.
