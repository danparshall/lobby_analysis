# T28/T29 Coverage Gap — Diagnosis & Fix Plan

**Goal:** Close the 12-state coverage gap in v2 CSVs for COGEL Blue Book
Tables 28 and 29, so that the Opheim cross-validation can run
authoritatively over all 47 in-scope states.

**Originating conversation:** `docs/active/cogel-extraction/convos/20260512_opheim_phase1_encoders_and_tdd.md`

**Context:** Phase 1 of the Opheim plan
(`plans/20260507_opheim_cross_validation.md`) shipped the 22 encoders +
60-case TDD suite. The 47-state coverage test is currently
`xfail(strict=False)` because 12 Opheim states have **zero rows** in
one or more of our four v2 CSVs:

| State group | Missing from | Count |
|-------------|--------------|-------|
| AZ, CO, GA, IL, KY, NM, OH, PA | T28 + T29 | 8 |
| DE | T28 + T29 + T31 | 1 |
| RI, SC | T28 + T29 + T30 | 2 |
| IA | T29 only | 1 |
| **Total** | | **12** |

This blocks `score_state()` for those states because the encoders read
from all four tables. Phase 2 of the Opheim plan therefore inherits a
12-state hole; the bidirectional error pattern on the 35 scoreable
states (high-Opheim under, low-Opheim over) suggests extraction errors
dominate over encoder mismatches, so closing this gap is the
highest-leverage next move before chasing per-state Phase 3 diagnosis.

**Confidence:**

- Phase 0 (diagnose mechanism): **High** — concrete diagnostic
  questions with multimodal-PDF answer paths.
- Phase 1 (fix): **Low until Phase 0 resolves**. The fix architecture
  depends on which of Hypotheses A/E/F (below) the source-page layout
  actually exhibits. Do not pre-commit to a fix until Phase 0 closes.
- Phase 2 (verify XPASS on coverage test): **High** — the test
  already exists; it tells us pass/fail mechanically.
- Phase 3 (re-run Phase 2 preview to assess delta-pattern shift):
  **Medium** — closing the coverage gap may or may not soften the
  bidirectional error pattern; the residual after the fix is itself
  diagnostic.

**Architecture:** Diagnose first. Phase 0 is multimodal inspection of
3-4 source PDFs (no code) plus targeted token-distribution diagnostics
on the v1 TSV. Phase 1 designs the fix to match whichever mechanism
Phase 0 identifies. The v1 extractor (`scripts/cogel_1990_extract.py`)
and the cogel module (`src/lobby_analysis/cogel/{grid,ocr_merge}.py`)
are the candidate touch points; tests live in `tests/test_cogel_*.py`.

**Branch:** `cogel-extraction` (worktree at
`/Users/dan/code/lobby_analysis/.worktrees/cogel-extraction/`).

**Tech Stack:** Python 3.12, pdfplumber, pytesseract, PIL, stdlib csv.
No new dependencies anticipated.

---

## Diagnostic anchors from the originating session

These findings frame Phase 0:

1. **State coverage by scan from the post-dual-PSM v1 TSV** (which is
   the regenerated `results/20260505_v1_tokens.tsv`, 8,442 tokens):

   | Scan | Table | States captured | Expected ~30 (US) |
   |------|-------|-----------------|--------------------|
   | 159 | T28 | 23 — Alabama → New Hampshire | missing AZ, CO, DE, GA, IL, KY |
   | 160 | T28 | 17 — incl. DC, NJ → WY | missing NM, OH, PA, RI, SC |
   | 163 | T29 | 9 — Alabama → Indiana | missing AZ, CO, DE, GA, IL |
   | 164 | T29 | 8 — Kansas → Mississippi | missing KY, IA |
   | 165 | T29 | 9 — Missouri → North Dakota | missing NM |
   | 166 | T29 | 9 — Oklahoma → Washington | missing OH, PA, RI, SC |
   | 167 | T29 | 3 — West Virginia, Wisconsin, Wyoming | (end) |

2. **Text-token search for missing state names on T28/T29 scans
   returns zero hits.** "Arizona", "Colorado", "Delaware", "Georgia",
   "Illinois", "Kentucky", "Ohio", "Pennsylvania" do not appear as text
   tokens (any row label) on scans 159, 160, 163-167. So the issue is
   not row-mis-attribution to neighbor rows — the state names are not
   in the OCR output at all on those scans, regardless of which PSM
   mode produced them.

3. **Same states are recovered fine on T30 and T31 scans** (169, 170,
   172-175), so the v1 anchor-matching logic is sound when the state
   names exist in the OCR output. The pathology is specific to the
   T28/T29 scans, not the row labeler.

4. **Opheim's published scores rule out source omission for at least
   four of these states:** AZ=11, IL=15, PA=14, OH had positive
   Phase-2-preview oversight scores (so OH must have a compliance
   authority in COGEL T31, which it does). States with non-zero Opheim
   scores must have lobbyist definitions and disclosure laws — so they
   must appear in the COGEL Blue Book tables that catalog those.
   Hypothesis A (source omission) is partially falsified.

5. **The arithmetic structure is suggestive of a 2-column page
   layout.** Each missing state on scan 159 has an alphabetical
   neighbor that IS captured: AZ between Alaska/Arkansas; CO between
   CT-or-CA/Connecticut; DE between Connecticut/Florida; GA between
   Florida/Hawaii; IL between Idaho/Indiana; KY between Kansas/
   Louisiana. The captured states could form a left column while the
   missing states form a right column on a 2-column table.

---

## Hypotheses

The diagnostic anchors above narrow the cause to one of:

- **Hypothesis A (Source omission):** COGEL Blue Book legitimately
  excludes these states from T28/T29 (and DE from T31, RI/SC from
  T30). Partially falsified by Opheim non-zero scores for AZ/IL/PA/OH.
  Mostly ruled out, but not 100% — the source could exclude a state
  from T28 (definitions) yet include it in T29 (disclosure) or vice
  versa. Phase 0 must check each table separately.

- **Hypothesis E (Two-column page layout):** T28 / T29 in COGEL Blue
  Book put state rows in TWO columns side-by-side (left half of page
  + right half of page), and the v1 row labeler — designed for
  single-column-state tables (the assumption matches T30/T31) —
  catches only the left column. **Most likely.**

- **Hypothesis F (OCR PSM blind spot on T28/T29 anchor regions):**
  The dual-PSM merge (PSM 3 + PSM 6) doesn't cover the layout
  variant that puts state names in T28/T29. A third PSM mode might
  recover them. Plausible but less likely given that PSM 6 recovered
  CA/FL on T30; if these scans had a similar pathology PSM 6 should
  have caught it.

Phase 0 distinguishes between these.

---

## Testing Plan

The existing `tests/test_cogel_opheim.py::test_all_47_opheim_states_present_in_all_four_csvs`
test is currently `xfail(strict=False)`. **The plan's principal
success criterion is that this test XPASSes after the fix.**

Additional tests added per phase:

- **Phase 0 (diagnostic):** No new tests — pure exploration. Visual
  inspection of PDFs + token-distribution queries against the v1 TSV.
  Phase 0 outputs a results-doc, not code.

- **Phase 1 (fix):** Tests depend on Phase 0 mechanism. If Hypothesis E
  (two-column layout) holds: add a new test in
  `tests/test_cogel_grid.py` (or a new `tests/test_cogel_extract.py`
  if the fix lives at the v1 extractor) that asserts the extractor /
  grid recovers the missing states' rows on at least one synthetic or
  fixture page in the two-column layout. The test should be
  independent of the full 20-page corpus — small fixture or synthetic
  token list with a known two-column structure.

- **Phase 2 (verify):** Run the existing Opheim coverage test, expect
  XPASS. Then full pytest suite for no-regression. Existing
  `tests/test_cogel_grid.py` (25 tests) and
  `tests/test_cogel_ocr_merge.py` (11 tests) must still pass.

- **Phase 3 (Phase 2 preview re-run):** No new tests — exploration.
  Re-run the inline rollup against the new v2 CSVs, compare delta
  stats and the bidirectional pattern against
  `results/20260512_opheim_phase2_preview.md`.

NOTE: I will write *all* tests before I add any implementation
behavior in Phase 1.

---

## Phase 0 — Diagnose the mechanism

**Goal:** Decide between Hypotheses A, E, and F for each missing
state × missing-table cell. Output is a results-doc, not code.

Steps:

1. **Multimodal-read scan 159 PDF** at
   `COGEL_BlueBook_1990/mdp-39015077214750-159-1777852418.pdf`. Look
   at the actual page layout. Count physical state-name columns
   (1 or 2). Confirm whether AZ/CO/DE/GA/IL/KY are visually present
   on the page.
2. **Multimodal-read scan 163 PDF** at
   `COGEL_BlueBook_1990/mdp-39015077214750-163-1777852444.pdf` —
   same check for T29.
3. **Multimodal-read scan 170 PDF** at
   `COGEL_BlueBook_1990/mdp-39015077214750-170-1777852495.pdf` — to
   compare T30's known-working layout against T28/T29's failing
   layout.
4. **Multimodal-read scan 169 PDF** for completeness — to confirm
   the CA/FL fix from 2026-05-11 was actually a PSM issue and not a
   layout issue.
5. **Tabulate per-state × per-table conclusion** in a results doc
   `results/20260513_t28_t29_coverage_gap_diagnosis.md`. Columns:
   state | T28 verdict | T29 verdict | source-page evidence | hypothesis.
   Verdict ∈ {present-extractable, present-needs-fix, absent-source}.
6. **If Hypothesis E holds**: also confirm whether T28 and T29 use
   the SAME layout or different ones. The number of states per scan
   suggests T28 may be 2-column (40 jurisdictions across 2 scans =
   20/scan; we recovered 23 + 17 = 40) and T29 may also be 2-column
   (~9-10 states per scan × 5 data scans = ~45-50, we recovered 38
   total). Re-check arithmetic against the Blue Book's actual layout.
7. **Commit the diagnosis doc.** Phase 1 design is gated on this
   doc.

**Output:**
- `results/20260513_t28_t29_coverage_gap_diagnosis.md` (per-state
  verdict table + page-layout finding)
- A definitive call on which hypothesis (or combination) the fix
  must address.

**What if Phase 0 reveals Hypothesis A** (some states truly absent
from source)? Then the Opheim cross-val itself needs revision:
those states' Opheim "scores" can't be reproduced from T28/T29
because the source data doesn't exist. Update the encoders to
return `None` (or 0 with a `na_count` flag per the original plan's
"Implementation Details" §5) when source row is missing. Test
expectation updates accordingly.

---

## Phase 1 — Implement the fix

Steps depend on Phase 0 outcome. Two main branches:

### Branch 1.A — Hypothesis E (two-column layout)

If T28/T29 use a 2-column-state layout where v1 catches only the
left column:

1. **Inspect v1 token positions** on scan 159 for the right column.
   The right-column state-name tokens DID get OCR'd somewhere —
   they just weren't recognized as row anchors. Check whether
   tokens with x-positions in the right half of the page have
   plausible state-name text (e.g., scan 159 page width ~2667 px;
   right column starts ~x=1300 or wherever the page break is).
2. **If right-column tokens are in the TSV but mislabeled**
   (e.g., row=`_header` because anchor-matching failed): write a
   failing test in `tests/test_cogel_extract.py` (new file) that
   exercises a synthetic 2-column token layout and asserts both
   columns' state rows are recovered. Watch it fail.
3. **Modify the v1 extractor** to detect two-column layouts and
   anchor-match in both halves. Likely: split scans by mid-x,
   run anchor-matching on each half independently, merge the
   resulting row labels. Minimal code per TDD GREEN.
4. **Re-run v1 extraction** on scans 159-167 to regenerate the
   v1 TSV.
5. **Re-run v2 grid** to regenerate the four v2 CSVs.
6. **Run the existing Opheim coverage test.** Expect XPASS.

### Branch 1.B — Hypothesis F (PSM blind spot)

If the state-name tokens themselves aren't OCR'd by either PSM 3
or PSM 6 on T28/T29 scans:

1. **Probe additional PSM modes** (4 = single column of text;
   1 = automatic page segmentation with OSD; etc.) on scan 159
   crop covering one missing state's expected y-band. Find a
   PSM that recovers "Arizona" etc.
2. **Extend `ocr_merge.py`** with a third PSM pass on T28/T29
   scans only (or all scans, if regression-safe).
3. **Write a failing test** in `tests/test_cogel_ocr_merge.py`
   covering a 3-PSM-pass merge with appropriate dedup behavior.
   Watch fail, GREEN.
4. **Re-run v1 extraction + v2 grid.**

### Branch 1.C — Hypothesis A (source omission for some cells)

If Phase 0 confirms some states are genuinely absent from T28 or
T29 in the source:

1. **Update the encoders** to handle missing-source-row gracefully.
   `score_state(t28, t29, t30, t31)` already accepts dict args;
   when a row is `None`, it should compute partial-dimension scores
   and flag which dimensions are unscored.
2. **Update the coverage test** to exclude documented-absent states
   with a citation to the Phase 0 diagnosis. Test still XPASSes
   for present states.

---

## Phase 2 — Verify

Steps:

1. **Run** `uv run pytest tests/test_cogel_opheim.py::test_all_47_opheim_states_present_in_all_four_csvs`.
   Expect XPASS (or, under Branch 1.C, expect pass on the
   reduced state set).
2. **Run** `uv run pytest` (full suite). Expect 398 → 398+N where
   N is the new test count from Phase 1. Pre-existing failures
   in `tests/test_pipeline.py` remain unchanged.
3. **Run** the inline Phase 2 preview rollup from the originating
   convo (same Python snippet emitting
   `results/<date>_opheim_phase2_preview.csv`), now covering all
   47 (or revised) states.
4. **Drop the xfail marker** on
   `tests/test_cogel_opheim.py::test_all_47_opheim_states_present_in_all_four_csvs`
   once it consistently XPASSes. Commit the marker removal as a
   separate small commit so the XPASS → PASS transition is
   visible in git history.

---

## Phase 3 — Re-run Opheim Phase 2 preview, assess delta-pattern shift

Steps:

1. **Re-run the rollup script** from the convo's snippet (or
   bake it into a committed `scripts/opheim_phase2_preview.py`
   if the Phase 2 driver from the original Opheim plan hasn't
   landed yet).
2. **Compare summary stats** vs `results/20260512_opheim_phase2_preview.md`:
   exact / ±1 / ±2 counts, mean Δ, stddev.
3. **Inspect the bidirectional pattern.** If the high-Opheim
   under-scoring softens substantially (e.g., NJ Δ moves from
   −10 toward 0), the coverage gap was the dominant cause and
   we're now in mid-agreement territory. If the pattern persists,
   the residual error is per-cell extraction (asterisk-→-em-dash
   misreads on rich rows, AR-style row-band contamination on
   sparse rows) and Phase 3 of the Opheim plan handles it.
4. **Write a results doc**
   `results/<date>_opheim_phase2_post_gap_fix.md` mirroring the
   prior preview doc structure: stats, per-state table, top
   outliers, mechanism residuals.

---

**Testing Details:** The principal test is the existing 47-state
coverage test moving from xfail to XPASS — a behavior verification
that doesn't depend on the extraction internals. Phase 1's new
tests target the specific mechanism Phase 0 identifies; they use
synthetic token layouts or small fixture pages so they exercise
the fix's *behavior* (does the extractor recover both columns? does
the third PSM pass produce additional state-name tokens?) without
testing the v2 grid's internal data structures. No mock-only
tests; all assert on the row dicts the pipeline produces from
real or synthetic OCR token streams.

**Implementation Details**

- Phase 0 produces a results-doc only — no code commits in Phase 0.
- The v1 extractor (`scripts/cogel_1990_extract.py`) is the most
  likely touch point under Hypothesis E. The v1 module wraps the
  raw `pytesseract.image_to_data` output with anchor-matching, OCR
  normalisation, and row labeling.
- The dual-PSM merge in `src/lobby_analysis/cogel/ocr_merge.py` is
  the likely touch point under Hypothesis F.
- The v2 grid (`src/lobby_analysis/cogel/grid.py`) is unlikely to
  need changes — the gap is upstream of the v2 grid.
- Test corpus / fixtures should NOT be the full 20-page COGEL
  corpus. Use small synthetic token layouts to test the column-
  splitting or third-PSM logic in isolation.
- Don't delete the existing `results/20260505_v1_tokens.tsv` when
  regenerating — copy to a dated archive before overwriting (e.g.,
  `results/20260513_v1_tokens_pre_t28_t29_fix.tsv.gz`) so the
  before-state remains reproducible. Per the repo's Experiment
  Data Integrity rule.
- The XPASS-then-drop-marker flow keeps git history clean: Phase 2
  step 4 commits "drop xfail marker" as a one-line change visible
  to future readers.

**What could change:**

- **Hypothesis A confirmation** on any state changes the
  acceptance criterion. The coverage test gets adjusted, not all
  12 states recovered.
- **Mixed mechanism**: if some states fail under E and others
  under F, Phase 1 needs both fixes. Plan currently scopes Phase 1
  to one branch; expanding to multi-branch is straightforward.
- **Iowa is a special case** (missing from T29 only). The
  mechanism for IA may differ from the 9-state group — could be
  a single-state OCR pathology on scan 164 specifically. Phase 0
  should treat IA as its own diagnostic case.
- **DE / RI / SC also miss from T30 or T31.** This suggests
  multi-table OCR / layout pathology. Phase 0 should check those
  tables too if convenient (same scan inspection).
- **Alabama T29 content-width overflow** (deferred from
  2026-05-11) is a separate extraction-pipeline bug. If Phase 0
  reveals it shares a mechanism with T28/T29 gap, fold them; if
  not, AL stays a separate session.
- **The Opheim Phase 2 driver script** (`scripts/cogel_1990_opheim_score.py`)
  from `plans/20260507_opheim_cross_validation.md` Phase 2 hasn't
  been written yet. If it lands between this plan being created
  and Phase 3 being executed, use it instead of the inline
  preview snippet.

**Questions**

- Should Phase 0 also examine scan 168 / 171 / 178 (the documented
  footnote-only pages)? Probably not — those don't contain
  jurisdictional data. But confirming no missing states are buried
  there is a 5-minute check.
- After this fix lands, does the 12-state gap have any implications
  for the OTHER active research line (`compendium-source-extracts`)?
  That branch consumes COGEL items for cross-rubric clustering;
  the per-state cells may flow through if compendium 2.0 pulls
  cell-level evidence rather than row-level. Out of scope for
  this plan; flag for cross-branch coordination if confirmed.
- Is there a risk that whichever fix lands breaks the Missouri
  16/16 multimodal ground truth (the v2 extraction's main
  regression anchor)? Phase 2 step 2 catches this — the existing
  `test_cogel_grid.py` suite includes Missouri-specific assertions.
  But a manual re-verification of Missouri T29 cells against the
  scan is cheap insurance.

---
