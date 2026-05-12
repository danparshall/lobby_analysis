<!-- Generated during: convos/20260511_opheim_phase0_table1_lift.md -->

# Dual-PSM v1 extractor: CA/FL recovery on Table 30

Date: 2026-05-11
Originating convo: `convos/20260511_opheim_phase0_table1_lift.md`

## Problem

End-of-session 2026-05-08 flagged two states (California, Florida) as
absent from the v2 Table 30 emission despite being in the v1 token TSV.
The 2026-05-08 RESEARCH_LOG noted "filter cascading suspected" but the
root cause had not been traced.

## Investigation summary

The v2 grid was not the failure point. The v1 token TSV had CA and FL
*labels* but **zero data tokens** tagged to those rows. A targeted re-OCR
of scan 169 with tesseract PSM 6 (uniform-block) recovered the missing
rows that tesseract PSM 3 (auto-layout, the v1 default) had segmented
out. The v1's original PSM choice was empirical from a probe that
compared PSM 3 vs PSM 11/12 (both sparse) but did not evaluate PSM 6.

Extent inventory across all 20 scans:

| Scan | Anchor | Tokens before | Tokens after |
|------|--------|---------------|--------------|
| 169  | California | 2 | 14 |
| 169  | Florida    | 1 | 13 |
| 163  | Hawaii     | 4 | (unchanged in this scope) |
| 169  | Georgia    | 4 | (unchanged in this scope) |

Only CA + FL on scan 169 emit *no* T30 row pre-fix. Hawaii (T29) and
Georgia (T30) were already present in the CSVs but borderline-thin.

## Fix

`src/lobby_analysis/cogel/ocr_merge.py` adds `merge_token_passes(primary,
secondary, radius)` that keeps all primary-pass tokens and appends any
secondary-pass tokens not co-located within a 15-px Chebyshev radius of
a primary center. `scripts/cogel_1990_extract.py` now runs tesseract
twice (PSM 3 primary, PSM 6 secondary) and merges the results. Unit
tests in `tests/test_cogel_ocr_merge.py` cover empty inputs, dedup
semantics, the radius parameter, ordering, and a realistic CA-scan-169
scenario (11 tests, all green).

## Outcome

Re-running the v1 extractor on all 20 PDFs and projecting through the v2
grid (no changes to grid or schemas):

| Metric | Before | After | Delta |
|--------|--------|-------|-------|
| v1 TSV total tokens | 7,198 | 8,443 | +1,245 |
| Table 28 jurisdictions | 40 | 40 | 0 |
| Table 29 jurisdictions | 38 | 38 | 0 |
| Table 30 jurisdictions | 46 | **48** | **+2 (CA, FL)** |
| Table 31 jurisdictions | 58 | 58 | 0 |
| Marker cells (sum over 4 tables) | 1,523 | 1,648 | +125 |
| Missouri T29 row | 16/16 | 16/16 | unchanged |

The +125 markers are wider than the CA + FL recovery alone (~20 marker
cells across the two new rows). The bulk (~105 markers) is PSM 6 filling
in dashes and asterisks that PSM 3 read past on other states. No
regression: every token PSM 3 emitted is preserved by the merge.

## Known follow-ups not addressed by this fix

- **Alabama-style content-width overflow.** A separate failure mode
  where a free-text cell's content (e.g., "Monthly during legislative
  session") overflows the canonical column width and leaks tokens into
  adjacent cells. Not in scope here; needs per-row width detection or
  content-aware boundary reslicing.
- **FL row col-1 cell value `=`.** The FL row's first cell reads `=`
  which is an OCR misread that the grid's marker normalisation doesn't
  cover. Trivial to fix by adding `=` to the dash-variant aliases; not
  done in this fix.
- **CA row col-13 cell value `-`.** A single hyphen in a free-text
  column. Probably the OCR's best read of a missing-data marker on
  that cell. Not normalised to `—` because col 13 is free_text, not
  marker.

## Reproducibility

End-to-end:

```
uv run scripts/cogel_1990_extract.py COGEL_BlueBook_1990/*.pdf \
  -o docs/active/cogel-extraction/results/20260505_v1_tokens.tsv

uv run scripts/cogel_1990_grid.py
```

Investigation scripts retained for future audits:

- `scripts/inspect_scan169_ca_fl.py` — crops + re-OCRs the CA and FL
  bands on scan 169 with multiple PSMs (this is the script that
  surfaced PSM 6 as the recovery mode).
- `scripts/diagnose_v1_token_gaps.py` — inventories anchors with very
  few tokens across all scans; would have flagged CA/FL/Hawaii/Georgia
  directly had it existed at the time.
