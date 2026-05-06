# Blue Book 1990 — v1 token extractor

**Date:** 2026-05-05
**Branch:** cogel-extraction

## Summary

Dan added 20 pages of the COGEL Blue Book 1990 to the repo (HathiTrust scans
159–178; book pp. 149–168) covering Tables 28–31 — lobbyist
definition/registration, reporting requirements, report filing, and
compliance authority. Each page is a wide table printed in landscape on a
portrait page, with HathiTrust's OCR text layer overlaid. The .txt files
preserve footnote prose cleanly but flatten the table structure: column
headers appear in scrambled order, jurisdiction (row) labels are stripped
on most data pages, and — load-bearingly — the asterisk and em-dash glyphs
that encode most binary cell content are absent from the text layer
entirely. The session's goal evolved from "let's read these tables together"
to "build a reproducible Python script that maps PDF pages to structured
token data."

The architecture explored: pdfplumber for rendering and rotation, plus
tesseract `--psm 3` (after a 90 deg CW rotation) for OCR. A probe
established that HathiTrust's text layer contains 1 asterisk and 3 dashes
across a representative page where the visual table has dozens; a fresh
tesseract pass on the same page recovers 46 asterisks and 66 dash-tokens.
The script therefore drops the HathiTrust text layer entirely and works
from a fresh tesseract pass.

Validation against multimodal ground truth for Missouri on scan 165
recovered 15/16 cells correctly. The single miss is character-level
(tesseract reads one em-dash as `_`), not a row-tagging error. A bug in
the row-band logic was caught and fixed during validation.

## Topics Explored

- Structural map of the 20 pages (Table 28: scans 159-162; Table 29:
  163-168; Table 30: 169-171; Table 31: 172-178), including which scans
  are data pages vs footnote-only.
- Why the HathiTrust .txt is structurally unusable for cell recovery:
  asterisks/em-dashes are part of the scanned image, not the OCR text.
- pdfplumber probe: page has 4 images (scanned tile) and zero vector
  primitives; chars in the text layer carry an `upright` flag and bbox
  metadata; some text runs are rotated 90 deg on the page.
- Rotation handling: a 90 deg CW PIL rotation puts the table into natural
  reading orientation for tesseract.
- Tesseract PSM mode comparison: `--psm 3` gave the highest asterisk
  recall (46 asterisks at default DPI). PSMs 11 and 12 (sparse) collapsed
  to 5–6.
- DPI / preprocessing sweep: 300 DPI base render is as good as any
  combination of 450 DPI / grayscale / autocontrast / threshold for
  state-name recall on Table 28 page 1 (21/28 either way; the unmatched
  states turned out to be genuinely absent from this table).
- Multi-word jurisdiction matching: 14 multi-word names (New Hampshire,
  District of Columbia, etc.) are matched ahead of single-word states
  with a prefix-walking helper that handles both same-row-left and
  stacked-above prefix layouts (the "New" of "New Hampshire" sometimes
  wraps to its own line above the tail).
- Footnote-prose false-positive filtering: candidate jurisdiction tokens
  with a footnote-key token (e.g., `(a)`, `(jj)`, `(I)` mis-OCR'd from
  `(l)`) anywhere to their left in the same row are rejected; an
  x-clustering check requires anchors to share a row-label column with
  at least one other anchor.
- OCR error normalisation: case (alaska -> Alaska), trailing footnote
  suffix (Louisiana(i) -> Louisiana), known glyph-confusion aliases
  (lowa -> Iowa).
- Validation: Missouri's 16-cell row on scan 165 (Table 29) compared
  against multimodal ground truth, surfacing a row-band bug where
  asterisks above the letter baseline of the row label were
  misclassified as `_header`.

## Provisional Findings

- **Tesseract `--psm 3` on a 90-deg-CW-rotated 300 DPI render is
  sufficient for cell-marker recovery.** No second OCR pass and no
  pdfplumber/tesseract merge proved necessary. Re-OCR alone outperforms
  the HathiTrust text layer for our use (markers + free-text cells +
  jurisdiction labels).
- **The script is OCR-recall limited, not structure-limited.** Where
  cells are missed, it's because tesseract didn't transcribe the glyph,
  not because the row/column logic dropped a real token.
- **Footnote-prose filter is robust.** Five footnote-only pages (161,
  162, 168, 171, 178) correctly emit zero jurisdictions; data pages with
  trailing footnote text on the same page (167, 177) keep their real
  jurisdictions and reject the footnote mentions.
- **Cell-level recall is high but not perfect.** Missouri row: 15/16
  cells correctly recovered. The one miss was a `—` recognised as `_`,
  recoverable downstream by treating any short horizontal-only glyph
  inside a cell as a dash regardless of OCR's character label.
- **Row-band logic must extend the topmost row upward by half the median
  inter-row gap** (and symmetrically for the bottom row), because
  asterisk and dash glyphs sit ~60 px above the letter baseline of the
  row label at 300 DPI. The original fixed 50 px upper margin
  misclassified two real cell asterisks as `_header` for the topmost
  jurisdiction on every page.
- **Page totals (no asterisks/dashes survived the HathiTrust text layer
  vs 509 / 986 recovered by the script):**

  | Page set | Jurisdictions | Asterisks | Dashes |
  |----------|---------------|-----------|--------|
  | All 20 PDFs | 59 distinct (50 states + DC + 8 Canadian provinces) | 509 | 986 |

## Decisions Made

- Branch `cogel-extraction` cut from main; v1 script + 20 PDFs committed
  as `29457c6`; row-band fix as `f2ba496`.
- Architecture: tesseract-only OCR pipeline (HathiTrust text layer is not
  used by the script).
- Reproducibility via PEP 723 inline metadata so `uv run scripts/cogel_1990_extract.py`
  works without modifying `pyproject.toml`.
- Column clustering deferred to v2; v1 emits a per-token TSV with row
  labels only.
- COGEL pages live at the repo-root `COGEL_BlueBook_1990/` directory for
  now; reorganisation under `papers/` deferred.

## Results

- `results/20260505_v1_tokens.tsv` — full v1 token output across all 20
  PDFs (7,197 rows; 59 jurisdictions; 509 asterisks; 986 dashes).

## Open Questions

- One more validation row (e.g., a Canadian-province row with all-`N.A.`
  cells from scan 177) before committing to a column-clustering design —
  Dan's call on whether to spot-check more before v2 starts.
- Column clustering strategy for v2: per-table-type fixed column
  boundaries (transcribed once from the headers) vs auto-inference from
  header tokens vs hybrid. Tables 28-31 each have a different schema.
- Downstream normalisation rules for OCR oddities: `_` -> `—`,
  `3-reports` -> `3 reports`, low-confidence margin artifacts (e.g.,
  `SITYIY@244` at conf 31) — these belong in a v2 cell-emission step,
  not in v1.
- Whether the HathiTrust .txt has any role at all going forward, or
  whether v2 can drop it entirely.
