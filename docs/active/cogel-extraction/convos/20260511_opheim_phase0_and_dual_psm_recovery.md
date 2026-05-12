# Opheim Phase 0 — Table 1 lifted + dual-PSM CA/FL recovery

**Date:** 2026-05-11 → 2026-05-12
**Branch:** cogel-extraction

## Summary

Three deliverables landed: (1) Phase 0 of the Opheim cross-validation
plan — `data/compendium/opheim_1991_published_scores.csv` (47 states,
0-18 score range, mean 9.66, total 454); (2) the three open
coding-rule questions from `plans/20260507_opheim_cross_validation.md`
all settled from the paper methodology text; (3) root-cause fix for
the CA/FL absence from Table 30. The CA/FL fix turned out not to be a
v2-grid filter cascade but a v1-extractor segmentation pathology —
tesseract PSM 3 (the v1 default) drops the California and Florida row
bands of scan 169. PSM 6 reads them. The fix is a dual-PSM token-merge
in the v1 extractor.

Alabama-style content-width overflow remains open — different failure
mode (cell-boundary collision, not OCR segmentation). User chose to
checkpoint here rather than push into AL in this session.

## Topics Explored

- Why pdfplumber's `extract_text` and `extract_tables` both return
  nothing for Opheim's Table 1 page. The page is a single 1774×2667
  CCITTFaxDecode bitmap; the OCR text overlay built into the PDF has
  the header tokens and the footnote but skipped the 47-row body.
- Tesseract PSM choice. The v1 probe selected PSM 3 over PSM 11/12
  (both sparse, collapsed) but did NOT evaluate PSM 6. On scan 169,
  PSM 3 misses the CA and FL row bands entirely; PSM 6 (uniform-block
  assumption) reads them cleanly.
- Extent inventory across all 20 scans (`scripts/diagnose_v1_token_gaps.py`):
  2 anchors with 0 data tokens (CA scan 169, FL scan 169), 2 anchors
  with 3-5 tokens (Hawaii scan 163, Georgia scan 169) — both of the
  borderline cases already emit rows.
- Worktree provisioning subtleties. `use-worktree` skill's `data/`
  symlink advice doesn't apply here because `data/compendium/` is
  tracked content; `ln -s data` into an existing `data/` directory
  creates a nested broken symlink. Resolved by removing the symlink
  and letting `data/` exist naturally on the branch.
- Reproducibility constraints raised mid-session: scripts must live
  on disk (not `python3 -c "..."` inline), so they don't trigger
  permission prompts and remain auditable for future runs.

## Provisional Findings

### Opheim Phase 0

- All 47 states in Opheim's Table 1 transcribed; assertions confirm
  ranks 1..47 contiguous, states exactly = {50 US states} − {MT, SD, VA}
  matching the paper footnote, all scores in [0, 18].
- Predictable OCR artifacts on the Opheim bitmap: `i0` → `10` (Texas,
  Michigan), `il` → `11` (Arizona, Kansas), `Towa` → `Iowa`,
  `[Illinois` → `Illinois`, rank-comma → rank-period. All handled
  in `scripts/opheim_1991_extract.py` with explicit fixup tables.
- Published-mean reconciliation deferred: paper doesn't report mean(Y)
  in narrative text; it's in Tables 2/3 (also bitmaps, separate OCR
  needed). Not pursued — internal validation (state-set match,
  monotonic ranks, in-range scores) is already strong evidence.

### Three open coding-rule questions settled from methodology

1. **"Review of all reports" — any-of vs ALL.** Paper §III line
   141-142: "1 for review of all reports, 0 for less extensive
   review." COGEL T30 `review_*_all` columns differ on *mechanism*
   (desk / field / either); all three measure *scope=all*. Encoder:
   `1 if any(review_desk_all, review_field_all,
   review_desk_or_field_all) == "*" else 0`. Plan author's any-of
   read was correct.
2. **Opheim's "sources of income" ↔ COGEL T29 column.** No exact
   match. Best-fit `disclose_compensation_by_employer`: Opheim's
   "sources of income" = lobbyist reports payers; COGEL column =
   compensation broken down by payer. Adjacent but not identical.
   Flagged for two-state spot-check during Phase 1 encoder dev.
3. **Frequency item source-doc.** Paper footnote 1 explicitly:
   21/22 items sourced from CSG Blue Book 1988-89; ONLY frequency
   from Book of States 1988-89. We use Blue Book 1990 for all 22 →
   irreducible cross-source artifact on frequency. Accept and
   document in the Phase 4 report.

### CA/FL recovery

- Root cause: v1 extractor uses `--psm 3`; PSM 3 segments scan 169
  in a way that drops the CA and FL row bands. Two tokens for CA
  in pre-fix TSV (label + 1 rotated-header garbage), 1 for FL
  (label only).
- Fix: `merge_token_passes` in `src/lobby_analysis/cogel/ocr_merge.py`
  — keep all primary (PSM 3) tokens, append PSM 6 tokens not
  co-located within 15 px (Chebyshev) of a primary center.
- Outcome (regenerated v1 TSV + all 4 v2 CSVs):

  | Metric | Before | After |
  |--------|--------|-------|
  | v1 TSV tokens | 7,198 | 8,443 |
  | T30 jurisdictions | 46 | **48** (+CA +FL) |
  | Marker cells (4 tables) | 1,523 | 1,648 |
  | Missouri T29 | 16/16 | 16/16 |

- The +125-marker gain is wider than CA + FL alone (~20). The
  remaining +105 is PSM 6 filling in dashes and asterisks that PSM 3
  missed across other state rows. No regression: merge is monotonic.

## Decisions Made

- Phase 0 of Opheim plan committed as `db4a1d1`. Three open
  coding-rule questions resolved; Phase 1 encoders can proceed.
- Dual-PSM fix landed as `c3ec36f`: 1 new module, 11 new tests, 1
  modified script, all 4 v2 CSVs regenerated.
- Diagnostic scripts retained as committed artifacts per "fully
  reproducible" — `scripts/inspect_scan169_ca_fl.py` and
  `scripts/diagnose_v1_token_gaps.py`.
- Worktree at `.worktrees/cogel-extraction` (mid-session note: plan
  doc's "no worktree" line is stale; fixed during this checkpoint).
- AL overflow scoped to a separate future session — same conceptual
  bucket as CA/FL ("fix v2 extraction errors") but mechanically
  unrelated (cell-boundary collision, not OCR segmentation).

## Results

- `data/compendium/opheim_1991_published_scores.csv` — 47 rows of
  curated published scores
- `docs/active/cogel-extraction/results/20260511_opheim_table1_ocr.txt`
  — raw tesseract OCR provenance for the Table 1 page
- `docs/active/cogel-extraction/results/20260511_dual_psm_ca_fl_recovery.md`
  — full recovery report with before/after counts and known
  follow-ups

## Open Questions

- **Alabama-style content-width overflow** on T29 (and possibly other
  tables). AL's freq col 5 ("Monthly during legislative session")
  spans 1430-2020 px, but the table-default col 5|6 boundary is at
  1650 — tokens past 1650 leak into col 6 and 7. Needs per-row
  width detection or content-aware boundary reslicing. Next session.
- **FL row col-1 cell value `=`** — OCR misread that the grid's
  marker normalisation doesn't currently cover. Trivial fix; not
  done in this session.
- **CA row col-13 `-`** — single hyphen in a free-text column. Likely
  the OCR's best read of a missing-data marker on that cell. Not
  normalised because col 13 is free_text, not marker.
- **`disclose_compensation_by_employer` ↔ Opheim's "sources of
  income"** still needs two-state spot-check during Phase 1 encoder
  dev. The best-fit mapping is provisional.
- **Opheim Table 2/3 OCR** for published mean(Y) reconciliation —
  not pursued; flag if Phase 3 diagnosis suggests we need it.

## Next Steps

1. Either Alabama overflow fix (Phase 1 root-cause investigation
   on AL's token positions vs T29 boundaries → fix design →
   implement) — OR proceed to Opheim Phase 1 (the 22 encoders +
   TDD test suite, leaving AL for later).
2. The two-state spot-check on `disclose_compensation_by_employer`
   vs Opheim's "sources of income" should happen during Phase 1
   encoder dev.
3. Continue updating the plan doc as decisions land — the "no
   worktree" line was fixed in this checkpoint; the three
   coding-rule resolutions documented above.
