# RESEARCH_LOG — cogel-extraction

Trajectory of work on the COGEL Blue Book 1990 lobbying tables. Newest
entries on top.

## Purpose

The COGEL Blue Book 1990 is a fifth (or sixth, depending on how you count
PRI accessibility) primary source for the cross-state lobbying compendium:
50-state structured tables of lobbyist definition / registration /
reporting / report-filing / compliance authority as of 1 Jan 1990. Adding
it to the compendium gives a 20-year-prior anchor for measuring how state
disclosure law evolved (PRI is dated 2010; the 2025 OH SMR the latest
recoverable Justia vintage). It also expands rubric coverage on the
"definitions" and "compliance authority" axes that the existing 141-row
compendium covers thinly.

The branch problem is mechanical: the source pages are scanned tables
whose OCR text layer dropped the asterisk and em-dash glyphs that encode
most of the binary cell content. Without a working extractor, the source
is unusable for the compendium pipeline.

## Session: 2026-05-10 — opheim_cross_validation (kickoff)

### Topics Explored

- Worktree provisioning for cogel-extraction. Branch was previously
  checked out in the main repo; flipped main checkout to `main` and
  added `.worktrees/cogel-extraction` per the use-worktree skill.
- `data/` symlink fit for this repo. `data/compendium/` is tracked,
  so `data/` exists naturally on checkout — the skill's symlink
  advice doesn't apply. Initial `ln -s` accidentally produced a
  nested `data/data` symlink; removed.
- Test baseline on worktree: 328 passed / 5 skipped / 3 pre-existing
  failures in `tests/test_pipeline.py` (missing
  `data/portal_snapshots/`; reproduce on main; unrelated to cogel).
- Read of `plans/20260507_opheim_cross_validation.md` and pushback
  on five points before encoder code is written.

### Provisional Findings

- Worktree at `/Users/dan/code/lobby_analysis/.worktrees/cogel-extraction`
  is operational. `uv sync --extra dev` succeeded.
- Three load-bearing open questions in the plan need paper-text
  resolution: (1) "review of all reports" — ALL vs any-of;
  (2) Opheim's `disclose_sources_of_income` vs COGEL T29
  `disclose_compensation_by_employer` overlap; (3) frequency item
  is sourced by Opheim from Book of States 1988-89, not the Blue
  Book — known cross-source ambiguity.
- 47-state count and the 3-state exclusion list (plan asserts MT/
  SD/VA) need to be verified from paper text in Phase 0.

### Decisions Made

- Worktree adopted. Phase 0 of the Opheim plan (read paper text +
  lift Table 1 + settle the three open questions) is the next
  concrete step on resume.
- Pre-existing `test_pipeline.py` failures flagged but not
  addressed on this branch — they are a `main`-line infrastructure
  issue.

### Results

- None this session. Setup + pushback only; no Opheim code.

### Next Steps

- Phase 0: read Opheim paper text, lift the 47 published scores
  into `data/compendium/opheim_1991_published_scores.csv`, settle
  the three open coding-rule questions.
- Update plan doc to remove stale "no worktree" line.
- Then Phase 1 (encoder TDD).

## Session: 2026-05-07 — v2_grid_implementation

### Topics Explored

- Why tesseract reads sub-column headers as garbage despite reading
  group headers cleanly (vertical text faces opposite rotation axis
  after 90-deg-CW page rotation).
- 1-D agglomerative gap-threshold sweep on data tokens: no single
  threshold yields a clean schema-matched cluster count without
  filtering out stray clusters.
- Vertical-text bbox filter (`h > 2*max(w, 30)`) drops `SITYIY`-class
  rotated-header garbage but keeps real markers.
- Conf filter redesign: keep markers + conf ≥ 40 + digit-bearing
  tokens. Catches OCR artifact `"3-reports"` at conf=29.
- Multi-line free-text cells reconstructed via `(cy // 30, x)` sort
  ordering.
- Per-scan x-offset analysis: ±5 to ±25 px shifts across scans of the
  same table from manual page placement during HathiTrust scanning.
- Cross-validation candidate analysis: PRI 2010 vs Newmark 2005 vs
  Newmark 2017 vs Opheim 1991. Opheim wins on vintage match,
  oversight-dimension coverage, and items per dimension.

### Provisional Findings

- v2 grid pipeline shipped end-to-end: 4 per-table CSVs covering 50
  states + DC + provinces, tested via 25-test suite (all green).
- Missouri ground truth: **16/16 cells correct** (up from v1's
  15/16 via the `_` → `—` dash normalisation and the multi-line cell
  `"3 times a year"` reconstructed correctly).
- Total marker preservation across emission: 1,496 marker cells in
  the 4 v2 CSVs vs 1,495 in the v1 TSV (within 1).
- Per-scan offsets are real and varied: +8.3 to -13.4 (T29);
  +24.1 to -19.2 (T31, manual-placement drift accumulates over 6
  scans). Uniform shift fits well; no scaling needed yet.
- Hand-curated boundaries beat auto-detection on this corpus.
  Auto-clustering retained as fallback.
- Two open extraction issues: (a) Alabama-style content-width
  overflow leaks tokens into adjacent cells; (b) California and
  Florida missing from Table 30 emission despite being in v1 TSV.
- Opheim 1991 confirmed sourced from CSG Blue Book 1988-89; clean
  external ground truth at two-year vintage offset.

### Decisions Made

- Hand-curated `boundaries` field on `Table` schema is the primary
  path for boundary detection. Auto-clustering is fallback only.
- Cell reading order uses `cy`-bucket-then-x sort to handle
  multi-line free-text cells.
- Per-scan x-offset adjustment matches scan markers to reference
  column centers and applies the mean delta.
- Plan doc for Opheim 1991 cross-validation captured at
  `plans/20260507_opheim_cross_validation.md`.

### Results

- `results/cogel_1990_table28.csv` — 40 jurisdictions × 23 columns
- `results/cogel_1990_table29.csv` — 38 jurisdictions × 16 columns
- `results/cogel_1990_table30.csv` — 46 jurisdictions × 18 columns
- `results/cogel_1990_table31.csv` — 58 jurisdictions × 10 columns
- `results/cogel_1990_grid_warnings.tsv` — 475 warnings (per-scan
  offsets, unknown-marker flags, no-anchor scans).

### Next Steps

- Execute `plans/20260507_opheim_cross_validation.md`: encode
  Opheim's 22 items, score 47 states, compare to her published
  index, diagnose disagreements.
- Fix the missing CA/FL in Table 30 (filter cascading suspected).
- Address Alabama-style content-width overflow (per-row boundary
  reslicing or content-overlap detection).

## Session: 2026-05-05 — blue_book_v1_extractor

### Topics Explored

- Structural map of the 20 added PDFs across Tables 28-31, including
  which scans are data pages vs footnote-only.
- Why the HathiTrust .txt cannot drive cell recovery: asterisks /
  em-dashes are part of the scanned image, not the OCR text layer.
- pdfplumber + pytesseract pipeline at 300 DPI with a 90-deg-CW rotation.
- PSM mode comparison (3 vs 4 vs 6 vs 11 vs 12) and DPI / preprocessing
  sweep.
- Multi-word jurisdiction matching with same-row-left and stacked-above
  prefix layouts (the wrap of "New" above "Hampshire").
- Two-signal footnote-prose filter: footnote-key tokens to the left
  (`(a)`, `(jj)`, `(I)` mis-OCR'd from `(l)`, `(s}` mis-OCR'd from
  `(s)`) plus x-clustering with other anchors.
- OCR error normalisation (case, footnote suffix, glyph aliases).
- Validation against multimodal ground truth for Missouri on scan 165.

### Provisional Findings

- Tesseract `--psm 3` after a 90-deg-CW rotation at 300 DPI is sufficient
  for cell-marker recovery; no merge with the HathiTrust text layer is
  required.
- v1 recovers 7,197 tokens across the 20 pages: 59 distinct jurisdictions
  (50 states + DC + 8 Canadian provinces), 509 asterisks, 986 dashes.
  HathiTrust text layer: 0 asterisks / 0 dashes.
- Footnote-only pages correctly emit zero jurisdictions (161, 162, 168,
  171, 178). Mixed pages (167, 177) keep their real rows and reject
  footnote prose.
- Missouri row (scan 165, Table 29): 15/16 cells correctly recovered AND
  row-tagged. The single miss is character-level (`—` recognised as
  `_`), not row assignment.
- Row-band logic must extend the topmost row upward by half the median
  inter-row gap because asterisk and dash glyphs sit ~60 px above the
  letter baseline of the row label at 300 DPI.

### Results

- `results/20260505_v1_tokens.tsv` + `results/20260505_v1_tokens.md` —
  v1 token output across all 20 pages (commit `f2ba496`).

### Next Steps

- Optionally validate one or two more rows (Canadian-province row from
  scan 177 with all-`N.A.` cells; one Table 30 row with rich numerics
  like Texas's `$26,200,000`) before designing v2.
- v2: column clustering. Per-table-type column boundaries (transcribed
  once from the headers, since Tables 28-31 have different schemas), or
  auto-inferred from header tokens, or hybrid. Output: per-table CSVs
  with cells aligned to canonical column names.
- v2 should also handle the OCR character oddities in a centralised cell
  normalisation step (`_` -> `—`, `3-reports` -> `3 reports`, low-conf
  margin artifact filter).
- After v2, decide whether the COGEL pages and any derived CSVs move
  from the repo-root `COGEL_BlueBook_1990/` into `papers/` to match
  existing convention.
