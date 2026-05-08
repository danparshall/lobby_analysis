# Blue Book 1990 — v2 grid pipeline implementation

**Date:** 2026-05-07 → 2026-05-08
**Branch:** cogel-extraction

## Summary

Started as a review of the v2 column-clustering plan
(`plans/20260505_v2_column_clustering.md`); user approved going ahead
with implementation as exploratory iteration ("let's see what we get").
Built the v2 pipeline end-to-end: schemas for all four Blue Book tables,
test suite (TDD), grid module with cell normalisation + boundary
detection, and a PEP-723 CLI that consumes either the v1 token TSV
(default) or PDFs via `--from-pdfs`. Validation against the multimodal
Missouri ground truth on scan 165 lifted from v1's 15/16 cells to v2's
**16/16** (the col-16 `_` → `—` normalisation closed the last gap, and
the multi-line cell `"3 times a year"` reconstructed correctly).

Two design pivots away from the original plan emerged from inspecting
the actual TSV. (1) The plan's auto-detect-from-`_header`-tokens
approach for column boundaries was unsound: tesseract reads sub-column
header text on this corpus as letter-fragment garbage because the
headers face the opposite rotation axis from the body cells. The
hand-curated boundaries field on the schema became the primary path,
auto-clustering only the fallback. (2) Multi-line free-text cells (e.g.
`"3 times a year"` printed across two physical lines in the original
narrow column) need reading-order reconstruction by `cy`-bucket sort
followed by x within bucket — the plan implicitly assumed single-line
cells. Both pivots committed.

A second iteration added per-scan x-offset adjustment after observing
that columns shift ±5 to ±25 px between scans of the same table (manual
page placement during the HathiTrust scanning, user confirmed). The
adjustment matches scan markers to reference column centers within
tolerance and applies the mean delta to the table-default boundaries.
The conversation closed by identifying Opheim 1991 as a strong external
ground truth for cross-validation — same Blue Book series (1988-89
edition vs our 1990 edition), 22 binary items with explicit coding
rules, per-state index scores published for 47 states, and uniquely
covers the oversight dimension (Table 31) that Newmark dropped.

## Topics Explored

- Why tesseract reads scan 165's individual sub-column headers as
  garbage despite reading group headers ("Required To File Report",
  "Disclosures Required") at conf 95-96. Hypothesis: vertical column
  headers in the original PDF face the opposite rotation axis after
  90-deg-CW page rotation, making them upside-down for tesseract.
- Approach taxonomy for column-boundary detection: (a) header-token
  cluster, (b) data-token cluster all kinds, (c) marker-only cluster,
  (d) hand-curated. The TSV evidence promoted (d) to primary, (c) to
  fallback.
- 1-D agglomerative gap-threshold sweep on data-row tokens for
  scan 165: gap=20 yields 22 clusters with stray 1-row outliers,
  gap=60 yields 16 with one fake 266-margin cluster, gap=70 yields 15
  with one merged. None give a clean 16 without filtering.
- Vertical-text bbox filter (`h > 2*max(w, 30)`) drops `SITYIY`-class
  rotated-header garbage (h=134/w=33) without dropping real markers
  (`*` at h=12/w=13, `—` at h=4/w=29).
- Conf filter design: `conf < 40` drops the legitimate token
  `"3-reports"` at conf=29 (real OCR artifact for `3 reports` joined by
  hyphen). Replaced with: keep markers, keep conf ≥ 40 non-markers,
  keep digit-bearing tokens at any conf. SITYIY is then caught by the
  vertical-bbox filter, not the conf filter.
- Multi-line free-text cells: `"3 times a year"` is printed as
  `"3 times" / "a year"` across two physical lines (cy=1204 / cy=1249);
  cy-bucket-then-x sort reconstructs reading order.
- Per-scan offset analysis on Table 29 marker centroids across scans
  163-167: max scan-to-scan column shift is ~15 px, consistent across
  all 16 columns within a scan. Suggests single-offset translation
  fits each scan well.
- Cross-validation candidates: PRI 2010, Newmark 2005, Newmark 2017,
  Opheim 1991. Opheim 1991 wins on (a) vintage match, (b) coverage of
  Table 31 oversight dimension, (c) more items per dimension.

## Provisional Findings

- **Hand-curated boundaries beat auto-detection on this corpus.**
  Sub-column headers are unreadable; data-row tokens scatter due to
  free-text content variability. One canonical scan per table gives
  good initial centers; per-scan offset handles placement variance.
- **Marker recovery preserved across emission.** v1 TSV: 509 `*` +
  986 dash variants = 1,495 markers. v2 CSVs: 1,496 marker cells in
  total — within 1 of v1. The matching is robust.
- **Missouri ground truth: 16/16 cells correct.** Up from v1's 15/16
  (the dash-variant normalisation `_` → `—` closed the gap). The
  multi-line cell `"3 times a year"` reconstructs correctly via cy
  bucketing.
- **Per-scan offsets are real and varied.** Table 28: +8.3, +1.2 px;
  Table 29: -1.4 to -13.4; Table 30: +7.0, -5.1; Table 31: -19.2 to
  +24.1. Most pronounced on Table 31 (six scans, manual placement
  drift accumulates). Uniform-shift fits well; no scaling needed.
- **Content-width overflow is a separate failure mode.** Alabama's
  Table 29 freq col 5 ("Monthly during legislative session") spans
  1430-2020 px versus Missouri's "3 reports per year" at 1430-1615.
  Table-default boundaries that fit Missouri leak Alabama tokens into
  cols 6 and 7. Per-scan offset doesn't help; needs per-row width
  detection or content-aware boundary reslicing. Deferred.
- **Two rows missing from Table 30 in v2 emission**: California and
  Florida. v1 anchored them, v2 dropped them. Filter cause not yet
  traced.
- **Opheim 1991 source confirmed as CSG Blue Book 1988-89.** From the
  Opheim paper text: "All data, with the exception of frequency of
  reporting requirements, were coded from the Council of State
  Government's Blue Book 1988-89... Data indicating frequency of
  reporting requirements were taken from Council of State
  Governments, The Book of the States, 1988-89." Vintage gap to our
  Blue Book 1990 is two years; state law changes in that window
  should be small but non-zero.

## Decisions Made

- Hand-curated `boundaries` field added to `Table` dataclass; primary
  path. Auto-clustering retained as fallback when `boundaries` is
  empty.
- Conf filter for free-text cells: keep markers, keep conf ≥ 40,
  keep digit-bearing tokens regardless of conf.
- Multi-line free-text reading order: sort tokens by `(cy // 30, x)`.
- Vertical-text bbox filter applied at both boundary detection and
  cell projection.
- Per-scan x-offset adjustment between marker centroids and reference
  column centers; applied as uniform shift to table boundaries.
- Plan doc for cross-validation against Opheim 1991 captured at
  `plans/20260507_opheim_cross_validation.md`. Opheim chosen over
  Newmark because she covers the oversight dimension (Table 31) that
  Newmark dropped, and her vintage matches more closely.

## Results

- `results/cogel_1990_table28.csv` — 40 jurisdictions × 23 columns
- `results/cogel_1990_table29.csv` — 38 jurisdictions × 16 columns
- `results/cogel_1990_table30.csv` — 46 jurisdictions × 18 columns
- `results/cogel_1990_table31.csv` — 58 jurisdictions × 10 columns
- `results/cogel_1990_grid_warnings.tsv` — 475 entries (per-scan
  offsets, unknown-marker flags, no-anchor scans).

Code committed under `1a9a92f` (v2 grid pipeline) + `e17246e`
(per-scan offset).

## Open Questions

- **Content-width overflow.** Alabama-style rows where a free-text
  cell's content exceeds the canonical column width and tokens leak
  into adjacent cells. Possible fix: row-aware boundary reslicing
  using token-density gaps within each row, falling back to table
  default. Or: detect overflow by counting tokens past the boundary
  and re-attaching to the source cell if the source cell is free_text.
- **California / Florida missing from Table 30 emission.** v1 TSV has
  them; v2 drops them. Suspect: filter cascading kills all their
  data tokens. Trace pending.
- **Should boundaries scale per-scan, not just shift?** A scan that's
  rotated by 0.5 deg or scaled by 1% would have non-uniform offsets.
  Current data shows uniform shift fits well, but worth verifying on
  the +24 px outlier (Table 31 scan 175).
- **Where do the per-table CSVs ultimately live?** Currently under
  `docs/active/cogel-extraction/results/`. On merge, candidate
  destinations: `data/compendium/cogel_1990/<table>.csv` (matching
  the existing `data/compendium/disclosure_items.csv` pattern) or
  `papers/COGEL_1990__blue_book_lobbying_tables/`. Defer to merge time.
- **Does Opheim cross-val find systematic extraction errors or
  systematic 1988→1990 statutory changes?** The validation can
  surface either; per-item disagreement diagnosis distinguishes them.
