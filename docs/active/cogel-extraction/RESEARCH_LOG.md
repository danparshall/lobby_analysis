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

## Session: 2026-05-12 → 2026-05-13 — opheim_phase1_encoders_and_tdd

### Topics Explored

- Phase 1 implementation per the plan: write tests-first, then
  encoders. 22-item encoder list bound to actual CSV column names
  (which diverge from the plan's encoder IDs on def_legislative_*
  and def_administrative_* — handled by binding to columns, not by
  renaming).
- Four mid-implementation design calls: (a) freq encoder uses
  lowercase-substring match on "monthly" / "in and out" rather than
  an enumerated string-set; (b) penalties encoder accepts `*` OR any
  digit (T31 column is amount-bearing); (c)
  `disclose_other_influence_activities` uses any-of
  (`disclose_contributions_for_lobbying`, `disclose_other`);
  (d) `disclose_sources_of_income` keeps the Phase-0 provisional
  best-fit to `disclose_compensation_by_employer` despite a WA
  disconfirmation surfaced during this session.
- Non-committed Phase 2 preview rollup across the 35 of 47 states
  scoreable from the current v2 CSVs, to get a directional read on
  agreement before designing the Phase 2 driver.

### Provisional Findings

- Phase 1 ships: `src/lobby_analysis/cogel/opheim.py` (267 lines,
  22 entries) + `tests/test_cogel_opheim.py` (60 cases).
- Full suite: **398 passed, 5 skipped, 1 xfailed (the 47-state
  coverage test), 3 pre-existing failures** in
  `tests/test_pipeline.py` unrelated to cogel.
- Missouri smoke: ours=7, opheim=5, Δ=+2 — passes ±2 boundary.
- Phase 2 preview over 35 scoreable states: mean Δ = −2.11,
  stddev 3.96. Only 4/35 exact, 11/35 within ±1, 14/35 within ±2.
  **Below plan's mid-agreement (60-90% within ±2) band** but
  premature to declare low-agreement: the bidirectional error
  pattern strongly implicates extraction, not encoder design.
- **Strong directional pattern** — high-Opheim states under-score
  (NJ −10, WI −8, MA −7, WA −7, IN −6); low-Opheim states
  over-score (AR +8, WY +6, NH +5, WV +3). Hypotheses: missing-marker
  OCR misreads on rich rows + row-band contamination on sparse rows.
  Arkansas's garbled `freq_lobbyist` value is the smoking gun for
  the latter.
- 12-state coverage gap (T28/T29 dominant): AZ, CO, DE, GA, IL, IA,
  KY, NM, OH, PA, RI, SC. Same conceptual bucket as the 2026-05-11
  CA/FL fix but mechanically separate.

### Decisions Made

- Encoders bind to actual CSV column names. The plan's encoder ID
  names for def_legislative_* / def_administrative_* are
  Opheim-aligned but don't match the CSV headers; the dataclass
  carries both for auditability.
- 47-state coverage test marked `xfail(strict=False)` rather than
  failing CI. Will XPASS automatically when v2 extraction closes
  the gap. Documented in the test's reason string + this entry +
  the convo summary.
- `disclose_sources_of_income` mapping kept provisional. NJ/WI
  confirm; WA disconfirms (Opheim 18 perfect, but our CSV has the
  column blank). Either the mapping is wrong OR WA's row is
  mis-extracted (under the dominant Phase-2-preview hypothesis,
  the latter).
- Phase 2 driver script deferred. User chose "checkpoint + push"
  over "build Phase 2 driver next" or "close the 12-state gap first."
- Plan doc NOT updated. Encoder-design provenance lives in the
  encoder `description` strings and this convo; plan stays as the
  high-level brief.

### Results

- `src/lobby_analysis/cogel/opheim.py` — 22 encoders + state_score rollup
- `tests/test_cogel_opheim.py` — 60-case TDD suite (59 pass, 1 xfail)
- `results/20260512_opheim_phase2_preview.csv` — per-state preview (47 rows)
- `results/20260512_opheim_phase2_preview.md` — preview narrative + diagnosis hypotheses
- `plans/20260513_t28_t29_coverage_gap.md` — diagnosis-and-fix plan for the 12-state T28/T29 gap (Phase 0 multimodal inspection → Phase 1 fix conditional on Hypothesis A/E/F → Phase 2 verify XPASS → Phase 3 re-preview)

### Post-checkpoint plan creation

After running finish-convo, user asked for a plan on the T28/T29
gap before ending the session. Targeted diagnostic against the
post-dual-PSM v1 TSV revealed:

- **All 12 missing states have ZERO state-name text tokens on
  T28/T29 scans** (not even mis-attributed to neighbor rows).
- **Same states recover fine on T30/T31 scans** — so the v1 row
  labeler is sound when state-name OCR succeeds; pathology is
  specific to T28/T29 scans.
- **Opheim non-zero scores for AZ=11, IL=15, PA=14, OH+** rule out
  source omission for those states.
- **Alphabetical alternation pattern** on scans 159-167 (every
  other state captured) strongly suggests **two-column-state page
  layout** in the COGEL Blue Book T28/T29 that the v1 single-
  column anchor logic doesn't handle.

Plan committed at `plans/20260513_t28_t29_coverage_gap.md` —
Phase-0-gated, three conditional fix branches (A: source omission,
E: two-column layout, F: PSM blind spot), success criterion =
existing xfail coverage test transitioning to XPASS.

## Session: 2026-05-11 → 2026-05-12 — opheim_phase0_and_dual_psm_recovery

### Topics Explored

- Opheim Phase 0 execution: located Table 1 in PDF (page 5 is a
  scanned bitmap; pdfplumber's text layer skipped the body); OCR'd
  the page with tesseract `--psm 6` at 300 DPI; parsed rank/state/
  score triplets with predictable artifact normalisation (`i0`→`10`,
  `il`→`11`, `Towa`→`Iowa`, `[Illinois`→`Illinois`).
- Settled the three open coding-rule questions from
  `plans/20260507_opheim_cross_validation.md` by reading the
  methodology section: "review of all reports" is any-of mechanism
  with scope=all; `disclose_sources_of_income` has no exact COGEL
  T29 column, best-fit `disclose_compensation_by_employer`; the
  frequency item is sourced by Opheim from Book of States 1988-89
  (not Blue Book) — irreducible cross-source artifact.
- Investigated CA/FL absence from v2 T30. Confirmed CA had 2 tokens
  in v1 TSV (label + rotated-header garbage), FL had 1 (label only).
  Bug is in v1 OCR, not v2 grid filtering.
- Cropped scan 169 around the CA/FL y-bands and re-OCR'd with PSMs
  3/6/11/12. PSM 6 cleanly recovers CA's full data row (~17 tokens)
  and FL's row partially (~7 tokens). PSM 3 misses both. The v1
  probe at branch start compared PSM 3 vs 11/12 only; PSM 6 was
  not evaluated.
- Designed `merge_token_passes` for spatial-proximity dedup between
  two OCR passes; 15-px Chebyshev radius is set just above the
  half-width of the smallest in-corpus marker glyph.

### Provisional Findings

- Opheim's 47 published scores: range 0-18, total 454, mean 9.66.
  Top: NJ/WA/WI=18. Bottom: AR=0. Missouri=5 (Phase 2 smoke-test
  anchor in the plan).
- Dual-PSM merge outcomes (regenerated v1 TSV + all 4 v2 CSVs):
  v1 TSV 7,198 → 8,443 tokens; T30 jurisdictions 46 → **48** (+CA
  +FL); marker cells 1,523 → 1,648. ~80% of the +125 marker gain
  is PSM 6 filling in missed markers across many state rows beyond
  CA/FL alone.
- Missouri T29 row unchanged before/after dual-PSM fix — no
  regression. Test suite: 339 passed (+11 new merge tests), 5
  skipped, 3 pre-existing failures unrelated to cogel.
- Alabama overflow is a different mechanism (cell-boundary
  collision on AL's wide "Monthly during legislative session" T29
  freq col 5) — not affected by the dual-PSM fix; deferred.

### Decisions Made

- Opheim Phase 0 complete; the curated CSV
  `data/compendium/opheim_1991_published_scores.csv` is the
  authoritative published-score reference for the Phase 2 driver.
- Worktree provisioned at `.worktrees/cogel-extraction`; plan doc's
  stale "no worktree" line corrected during this checkpoint.
- Diagnostic scripts kept committed: `scripts/inspect_scan169_ca_fl.py`,
  `scripts/diagnose_v1_token_gaps.py`. Investigation reproducible.
- AL overflow scoped to a separate session — fix design is open.
- Pre-existing 3 failures in `tests/test_pipeline.py` (missing
  portal-snapshot data) remain flag-only; not addressed on this
  branch.

### Results

- `data/compendium/opheim_1991_published_scores.csv` — Opheim Table 1
- `results/20260511_opheim_table1_ocr.txt` — raw OCR provenance
- `results/20260511_dual_psm_ca_fl_recovery.md` — CA/FL fix report

Commits: `db4a1d1` (Opheim Phase 0), `c3ec36f` (dual-PSM recovery).

### Next Steps

- Alabama overflow fix on T29 (per-row content-width detection
  / boundary reslicing) — OR Opheim Phase 1 encoders (22-item
  encoder set + TDD suite). User's call.
- Two-state spot-check on `disclose_compensation_by_employer` vs
  Opheim's "sources of income" during Phase 1 encoder dev.
- Trivial: add `=` to grid marker-normalisation aliases (FL T30
  col-1 cell).

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
