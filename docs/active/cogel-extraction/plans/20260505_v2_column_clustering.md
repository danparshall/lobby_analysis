# COGEL Blue Book v2 — Column Clustering Implementation Plan

**Goal:** Turn the v1 per-token TSV into per-table CSVs (one row per
jurisdiction, one column per Blue Book table column) by clustering tokens
into cell positions and normalising cell values.

**Originating conversation:** `docs/active/cogel-extraction/convos/20260505_blue_book_v1_extractor.md`

**Context:** v1 (commits `29457c6`, `f2ba496`) produces a token-level TSV
where each token is bbox-located and tagged with the nearest jurisdiction
by y. Validation against multimodal ground truth for Missouri on scan 165
showed 15/16 cells correctly recovered AND row-tagged. The remaining work
is *column* assignment: project the row-tagged tokens onto canonical
table columns and emit one CSV per table type. This is the artifact
downstream compendium code (and any future fellow's analysis) actually
consumes — the TSV is an intermediate.

**Confidence:** Medium. Token recall and row tagging are validated;
column-boundary detection is novel and needs its own validation pass
before scaling to all four tables. The biggest unknowns are (a) whether
auto-detected column boundaries from header tokens are stable enough
across pages within a single table, and (b) how to handle Table 30's
twelve sub-columns under "Nature of review" (the densest schema).

**Architecture:** A second script `scripts/cogel_1990_grid.py` consumes
the v1 TSV and emits per-table CSVs. Column schemas are hard-coded as
constants per table (column names are a fixed schema in the source).
For each (page, table), header tokens above the topmost data row are
clustered by x to produce candidate column boundaries; canonical column
names are matched against header strings; cell tokens are projected onto
boundaries; cell values are normalised (`-`/`--`/`—`/`_` → `—`; multi-
token text joined with whitespace cleanup).

**Branch:** `cogel-extraction` (no worktree — implement directly in
`/Users/dan/code/lobby_analysis/`).

**Tech Stack:** Python 3.12, stdlib `csv` + `dataclasses`, no new
dependencies. v1's PEP 723 metadata covers v2 too if v2 reads PDFs; if
v2 reads only the v1 TSV (preferred), it's pure stdlib.

---

## Testing Plan

I will add a unit test module `tests/test_cogel_grid.py` covering the
behaviours that determine cell content correctness. Tests use a small
fixture TSV (5–10 rows hand-built) so the assertions are deterministic
and don't require a running tesseract.

Behavioural tests (each tests *behaviour*, not data structure shape):

1. **Cell-marker normalisation:** given a row with tokens `*` at x=600
   and `—` at x=750, verify the emitted cell at column-x-bucket-1 is `*`
   and at bucket-2 is `—`. Repeat with token texts `-`, `--`, `_` (the
   OCR variants observed in v1) — all should normalise to `—`.
2. **Multi-token free-text cell:** given tokens `3`, `reports`, `per`,
   `year` at consecutive x positions inside a single column bucket,
   verify the emitted cell is `"3 reports per year"` (single space joins,
   no leading/trailing whitespace).
3. **Joined-with-hyphen OCR fix:** given a single token `3-reports` at
   the start of a free-text cell with `per` and `year` adjacent, verify
   the emitted cell is `"3 reports per year"` (the hyphen-join is
   undone).
4. **Empty cell:** given a row with no tokens in a column's x-range,
   verify the emitted cell is the empty string.
5. **Low-confidence margin artifact filtered:** given a row where the
   leftmost token is `SITYIY` at conf=31 (the kind of garbage that v1
   emits at the page-margin), verify it doesn't end up in cell 1.
   Threshold: drop tokens with conf < 40 unless the token text is `*` or
   a dash-variant (since marker glyphs often OCR at low confidence).
6. **Header → canonical column-name match:** given header tokens `Total`
   and `Expenditures` clustered at one x-bucket, verify the matcher
   returns the canonical column name `disclose_total_expenditures`
   (Table 29). Repeat for a misspelled / partial header (`Total`,
   `Expenditure`) — fuzzy match should still succeed at threshold.
7. **Column-boundary derivation:** given header-token x-clusters at
   x={600, 750, 900, 1100}, verify the derived cell boundaries are
   midpoints {675, 825, 1000} with outer edges at the page bounds.
8. **Footnote-suffix on cell text:** given a token `Annually(k)` in a
   period-covered column, verify the emitted cell text is `Annually`
   and the footnote letter is captured in a parallel `_footnotes`
   column for that row (so the information isn't lost).

Integration test (one per table, kept small):

9. **End-to-end one row, scan 165 Missouri:** load the v1 TSV
   (committed at `docs/active/cogel-extraction/results/20260505_v1_tokens.tsv`),
   run the grid pipeline for Table 29, and verify Missouri's emitted CSV
   row matches the multimodal ground truth captured in the convo (15/16
   cells; the col-16 dash mis-OCR'd as `_` should still emit `—` after
   normalisation, lifting recall to 16/16).
10. **Footnote-only-page no-op:** run the grid pipeline on the v1 TSV
    rows for scan 161 (Table 28 footnotes; no jurisdictions). Verify the
    output for Table 28 has no rows for scan 161 jurisdictions and the
    footnote text is captured separately (per Phase 4 below).

NOTE: I will write *all* tests before I add any implementation behavior.

---

## Phase 0 — Set up the schema constants

Each Blue Book table has a fixed column schema we transcribe once. The
schemas come from the column-header strip on the data pages, verified
against the multimodal read of scan 165 (Table 29) and the visual layout
of scans 159 (Table 28), 169 (Table 30), 172 (Table 31).

Steps:

1. Create a new module `src/lobby_analysis/cogel/schemas.py` with one
   `Table` dataclass per table type (`TABLE_28`, `TABLE_29`, `TABLE_30`,
   `TABLE_31`).
2. Each `Table` carries: `name` (e.g. `"Lobbyists: Definition,
   Registration, and Prohibited Activities"`), `scan_pages` (list of
   scan numbers that contribute), `columns` (list of `Column` records).
3. Each `Column` carries: `key` (snake_case canonical name used in CSV
   header), `header_text` (the printed column-header phrase, for header
   matching), `value_kind` (`"marker" | "free_text" | "currency" |
   "frequency"` — drives cell normalisation), and optional `header_aliases`
   for headers we expect tesseract to misread.
4. Hand-transcribe column headers for all four tables using the
   multimodal reads we already have for scans 165 (Table 29) and 159
   (Table 28); for Tables 30 and 31, do a fresh multimodal read of one
   data page each (scans 169 and 172) before writing the schema.
5. Commit the schemas as a standalone change before any clustering code
   lands. They're a curation artifact in their own right.

## Phase 1 — Column-boundary detection

For each PDF page, derive cell-boundary x-positions from the header
tokens in v1's TSV (rows where `row == "_header"`).

Steps:

1. Filter `_header` tokens to those whose y is just above the topmost
   data row (avoid title-block tokens at the very top of the page).
2. Cluster filtered header tokens by x using a 1-D agglomerative pass
   with a fixed gap threshold (~30 px at 300 DPI). Each cluster
   represents one column header (the column-header strings span
   several tokens — "Total", "Compensation", "Received").
3. For each cluster, build a `header_phrase` by sorting tokens by y
   (column headers are vertical text; sorting by y after the 90° CW
   rotation yields normal reading order) and joining with single spaces.
4. Match each `header_phrase` against the schema's column `header_text`
   plus aliases using normalised string distance (lowercase, alnum-only,
   accept ≥ 0.7 ratio). Unmatched clusters are flagged for review.
5. Cell boundaries are midpoints between adjacent cluster centroids;
   outer edges of the leftmost and rightmost clusters extend to the
   page margins.
6. Sanity check: the number of detected columns should equal the schema
   length within ±1. Larger drift → flag the page in a `_grid_warnings`
   sidecar so the operator can review without the run failing.

## Phase 2 — Cell normalisation

A small pure function maps a list of tokens (already bucketed into one
cell) plus the column's `value_kind` to a single cell value.

Rules per `value_kind`:

- **marker:** if any token text is in `{*}` → `*`. Else if any token
  text is in `{-, --, —, _}` → `—`. Else if no tokens → `""`. Else
  flag as `<unknown>` and dump tokens to a sidecar.
- **free_text:** filter tokens to conf ≥ 40 (markers exempt — they OCR
  at low conf often). Sort by x, join with single space. Apply a
  hyphen-fix pass: `\b(\d+)-(\w)` → `\1 \2` (handles "3-reports" →
  "3 reports"). Strip trailing `[footnote_letter]` suffix into a
  parallel `_footnotes` column.
- **currency:** extract the first token matching `\$?[\d,]+` (e.g.
  `$26,200,000`); strip commas and `$` to a numeric column
  `<col>_dollars`, retain the original text in `<col>`.
- **frequency:** match against an enum `{Annual, Biennial, Quarterly,
  Semiannual, Monthly, Annually, Permanent, "3 times a year", ...}`
  with normalisation (lowercase, alpha-only). Unmatched → free_text
  fallback.

## Phase 3 — Per-table CSV emission

Steps:

1. For each table type, gather all jurisdictions from all relevant scan
   pages (e.g., Table 28 = scans 159 + 160).
2. For each (table, jurisdiction), assemble a row dict keyed by column
   `key`s. Empty cells stay empty.
3. Write `docs/active/cogel-extraction/results/cogel_1990_table28.csv`
   (and 29, 30, 31). Once stable, copy/move to `data/compendium/cogel_1990/`
   in a follow-up task; for now keep them under `results/` so they're
   committed alongside the convo as research artifacts.
4. Write a sidecar `docs/active/cogel-extraction/results/cogel_1990_grid_warnings.tsv`
   capturing every cell where Phase 2 flagged ambiguity.

## Phase 4 — Validation

Steps:

1. Diff Missouri's emitted Table 29 row against the multimodal ground
   truth in the convo. Target: 16/16 cells correct after dash-variant
   normalisation lifts the col-16 `_` → `—`.
2. Read 2–3 additional pages multimodally to capture ground truth for:
   - one row in Table 30 with non-trivial currency (e.g., New York's
     `$26,200,000` from scan 170)
   - one Canadian-province row from scan 177 with all-`N.A.` cells
   - one Table 31 row that mentions agency name (e.g., "AL Ethics
     Commission" under Alabama) to test the agency-name sub-row case
3. Compute per-table totals: count emitted asterisks + dashes per page,
   compare against v1 TSV totals (509 / 986). Difference = tokens lost
   in clustering, should be near-zero.
4. Eyeball `cogel_1990_grid_warnings.tsv` and resolve any non-trivial
   ambiguities by hand or by tightening Phase 2 rules.

---

**Testing Details:** Tests target behaviour, not data shape. The
fixture-TSV unit tests cover the cell-normalisation rules in isolation
(no tesseract, no PDFs). The integration test loads the committed v1
TSV (so it's reproducible from the repo without re-running OCR) and
verifies one specific row's emitted CSV matches a hand-curated truth
table. The grid_warnings sidecar gives the operator a manifest of cells
the pipeline wasn't sure about — that's where unanticipated OCR
weirdness shows up.

**Implementation Details**

- Module layout: `src/lobby_analysis/cogel/{__init__.py, schemas.py, grid.py}`
  for the library; `scripts/cogel_1990_grid.py` for the CLI driver.
- v2 reads the v1 TSV by default; a `--from-pdfs` flag reroutes through
  `cogel_1990_extract` to regenerate tokens on the fly (useful when
  iterating on tesseract settings).
- Schema constants are typed and validated at import time (each
  `Column.value_kind` ∈ a fixed Literal).
- Column-key naming matches the existing compendium snake_case
  convention (e.g., `definition_legislative_lobbying`).
- The hyphen-fix and dash-normalisation rules live in one place
  (`grid.normalise_cell`), tested in isolation, called by the emission
  step.
- Schemas should NOT include columns we can't reliably extract (e.g.,
  if Table 30's nine "Nature of review" sub-columns prove unrecoverable,
  drop them from the schema with a NOTE, don't pretend to extract them).
- No new third-party dependencies (stdlib `csv`, `dataclasses`, `re`,
  `difflib` for fuzzy header match).
- Tests run under the project's existing pytest config; add a
  `tests/test_cogel_grid.py` and a fixture TSV under `tests/fixtures/`.
- After v2 lands and passes validation, draft a small follow-up task to
  move the CSVs from `docs/active/.../results/` to
  `data/compendium/cogel_1990/` as a curated artifact, mirroring the
  pattern in `data/compendium/disclosure_items.csv`.

**What could change**

- If header-token clustering produces unstable boundaries across pages
  within a table (e.g., scan 159 vs scan 160 disagree on column count),
  fall back to fixed per-(table, scan) hardcoded boundaries — manual
  but reliable. We'll know after Phase 1 spot-check on Table 29.
- If Table 30's "Nature of review" sub-grid is too dense to OCR
  reliably, drop it from the schema and flag it as a known
  not-extracted region. We'll know after multimodal review of scan 169.
- Cell normalisation rules will accrete as we see real OCR oddities;
  the rules above cover what v1 surfaced on Missouri but the integration
  test on three more rows will surface more.
- If downstream compendium consumers want a long-form CSV (one row per
  cell with table/jurisdiction/column/value) rather than wide per-table
  CSVs, add a long-form emitter alongside the wide ones. Cheap.

**Questions**

- Should Table 31's agency-name sub-row become its own column
  (`agency_name`), a row property, or get dropped? My guess: a column.
  Decide after the multimodal read of scan 172.
- Cell value for `N.A.` (Not Available) cells in Table 30 / 31 vs
  truly empty cells: are these the same downstream, or do we need to
  preserve the distinction? My guess: preserve as `N.A.` literal so
  downstream can decide.
- Where should the per-table CSVs ultimately live? Options:
  `data/compendium/cogel_1990/<table>.csv` (alongside other compendium
  artifacts; gitignored exception via `!data/compendium/`),
  `papers/COGEL_1990__blue_book_lobbying_tables/` (alongside the source
  PDFs, but `papers/` typically holds raw sources not derived data),
  or stay under `docs/active/` until the branch merges. My recommendation
  is `docs/active/` for now and `data/compendium/cogel_1990/` on merge,
  but Dan should confirm before the move.

---
