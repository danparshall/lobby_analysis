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
