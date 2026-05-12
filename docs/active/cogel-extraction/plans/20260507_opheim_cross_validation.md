# Opheim 1991 Cross-Validation Implementation Plan

**Goal:** Cross-validate the v2 COGEL Blue Book CSV extraction against
Opheim 1991's published 22-item / 47-state lobby-regulation index, using
her exact coding rules to score each of our extracted states and
comparing to her published per-state scores.

**Originating conversation:** `docs/active/cogel-extraction/convos/20260507_v2_grid_implementation.md`

**Context:** The v2 grid pipeline has emitted four per-table CSVs
covering 50 states + DC + Canadian provinces. Internal validation
(Missouri 16/16 multimodal) confirms a single canonical row, but we
have no held-out per-state ground truth. Opheim 1991 used the same CSG
Blue Book series (1988-89 edition; ours is 1990) for her 22-item index
across the same three structural dimensions our schemas cover
(definitions, disclosure, oversight). Her per-state scores are
published in Table 1 of the paper. If our extraction is faithful, our
re-derivation of Opheim's index from our CSVs should reproduce her
published rankings within a small per-state delta attributable to
1988→1990 statutory changes.

**Confidence:** Medium. The plan structure is straightforward, but
two unknowns: (1) Opheim's per-state scores are published as a *ranking
with summed integer scores 0-18*, not item-level — so per-item
agreement isn't directly observable; only the row-total comparison is.
(2) Frequency-of-reporting was sourced by Opheim from Book of States
1988-89, not from the Blue Book itself; that one item's ground-truth
source isn't quite the same as ours.

**Architecture:** A new module `src/lobby_analysis/cogel/opheim.py`
encodes each of Opheim's 22 binary items as a function from a
per-jurisdiction CSV row dict to a 0/1 score, with explicit reference
to the COGEL CSV column key(s) that drive the scoring. A driver
script projects all 47 in-Opheim states through these encoders,
sums to an index score per state, and emits a comparison table
(our score, Opheim published score, delta) plus a per-item-set
breakdown. The encoders are the auditable artifact — each one
documents Opheim's rule and how we mapped it.

**Branch:** `cogel-extraction` (worktree at
`/Users/dan/code/lobby_analysis/.worktrees/cogel-extraction/`).

**Tech Stack:** Python 3.12, stdlib `csv`, no new dependencies.

---

## Testing Plan

I will add a unit test module `tests/test_cogel_opheim.py` covering:

1. **Each item encoder, isolated.** For all 22 items (7 definition + 8
   disclosure + 7 oversight), the test feeds a synthetic CSV row that
   should score 1 and a synthetic row that should score 0, and
   asserts the encoder returns the expected value. The synthetic
   rows are tiny dicts, not full schema rows, so tests don't depend
   on the v2 grid output shape.

2. **State-level scoring rollup.** Given a known synthetic state
   (with known item-level 1/0 vector), the index sum equals the sum
   of the 1's. This catches encoder-name typos and double-counting.

3. **Real-data smoke test on Missouri.** Run the encoders against
   Missouri's actual CSV row from
   `docs/active/cogel-extraction/results/cogel_1990_table29.csv` (and
   table 28/30/31). Assert the resulting score is within ±2 of
   Opheim's published Missouri score. (±2 because of the 1988→1990
   vintage gap and because frequency was sourced differently by
   Opheim.)

4. **Coverage check on the 47 in-Opheim states.** Iterate over all 47
   states Opheim scored (excluding Montana, South Dakota, Virginia
   per Opheim's "data unavailable") and verify that each of our four
   CSVs contains a row for that state. Any missing state is a
   blocker — we cannot score it.

NOTE: I will write *all* tests before I add any implementation
behavior.

---

## Phase 0 — Lift Opheim's published scores

Opheim's Table 1 ranks 47 states by index score (0-18 range). We need
the per-state numerical score to compare against, not just the
ranking.

Steps:

1. Read `papers/text/Opheim_1991__state_lobby_regulation.txt` lines
   that contain Table 1.
2. Transcribe the 47-state-name + score pairs into a CSV
   `data/compendium/opheim_1991_published_scores.csv` with columns
   `state,opheim_1991_score`.
3. Reconciliation check: total scores across 47 states should match
   the sum reported in Opheim's regression analysis (mean × 47, look
   it up in the paper).
4. Commit the CSV as a curated artifact.

## Phase 1 — Encode the 22 items

Opheim's coding rules from the paper text:

- **Statutory definitions (7 items):** each coded 1 if the criterion
  is in the state's lobbyist definition, else 0.
  - `def_legislative_lobbying`
  - `def_administrative_lobbying`
  - `def_elective_officials_as_lobbyists`
  - `def_public_employees_as_lobbyists`
  - `def_compensation_standard`
  - `def_expenditure_standard`
  - `def_time_standard`
  All seven map directly to Table 28 columns 0-6.

- **Disclosure (8 items):**
  - `freq_monthly_or_in_out_session`: 1 if state requires reporting
    monthly OR in-and-out-of-session, else 0 (quarterly /
    semi-annually / annually all score 0). Maps to Table 29
    `freq_lobbyist` (and possibly `freq_lobbyist_employees`); needs
    a string-match rule against the cell value.
  - `disclose_total_spending`
  - `disclose_spending_by_category`
  - `disclose_expenditures_benefiting_employees`
  - `disclose_legislation_approved_or_opposed`
  - `disclose_sources_of_income`
  - `disclose_total_income`
  - `disclose_other_influence_activities`
  All seven directly mappable to Table 29 `disclose_*` columns.
  (`disclose_compensation_by_employer` may correspond to
  `disclose_sources_of_income`; need to verify by reading the cell
  values for two known states.)

- **Oversight (7 items):**
  - `review_thoroughness`: 1 if state reviews ALL reports, 0
    otherwise. Maps to Table 30 `review_desk_all` /
    `review_field_all` / `review_desk_or_field_all` (any one of
    them = 1).
  - `subpoena_witnesses`
  - `subpoena_records`
  - `conduct_administrative_hearings`
  - `impose_administrative_fines`
  - `impose_administrative_penalties`
  - `file_independent_court_actions`
  Six directly mappable to Table 31 `auth_*` columns.

Steps:

1. Create `src/lobby_analysis/cogel/opheim.py` with the
   `OPHEIM_ITEMS` list — 22 entries, each a small dataclass
   containing `item_id`, `dimension`, `description`,
   `cogel_table_number`, `cogel_column_keys`, `encoder` (callable).
2. Each `encoder` takes a dict (one CSV row) and returns 0 or 1.
   Encoders for marker columns: `1 if row[col] == "*" else 0`.
   Encoders for free-text columns (review thoroughness, frequency):
   string-match against known values.
3. Write the encoder tests (Phase 0 of testing plan) before adding
   any encoder bodies. Watch each fail. Add bodies one at a time;
   green per item.

## Phase 2 — Per-state scoring driver

Steps:

1. Create `scripts/cogel_1990_opheim_score.py` (PEP 723 inline
   metadata, stdlib only).
2. Load all four COGEL CSVs from
   `docs/active/cogel-extraction/results/`.
3. For each state name in `opheim_1991_published_scores.csv`:
   - Look up the row in each CSV that matches the state.
   - If any of the four CSVs lacks a row for this state, log a
     warning and skip the state (with explicit `_missing_in:` field
     in output).
   - Run the 22 encoders, summing to a state-level score.
4. Emit `docs/active/cogel-extraction/results/20260507_opheim_validation.csv`
   with columns: `state, opheim_published, ours_derived, delta,
   item_breakdown_def_disc_over, missing_in_cogel`.

## Phase 3 — Diagnosis

Steps:

1. Compute summary statistics: mean delta, stddev delta, count of
   states within ±0 / ±1 / ±2 / >±2.
2. For states with `|delta| > 2`, dump the per-item disagreement
   vector. Identify items where multiple states disagree —
   candidates for either (a) systematic extraction error (review
   the underlying COGEL cells in our CSVs) or (b) coding-rule
   mismatch (our encoder doesn't match Opheim's rule).
3. For systematic-extraction-error candidates: spot-check 2-3 cells
   multimodally against the corresponding scan PDF in
   `COGEL_BlueBook_1990/` to determine if the OCR or the boundary
   bucketing dropped a marker.
4. Write `docs/active/cogel-extraction/results/20260507_opheim_validation.md`
   summarising: overall agreement rate, per-dimension agreement
   rate (definitions / disclosure / oversight), top 5 outlier states
   with diagnostic notes, recommended fixes for the v2 pipeline.

## Phase 4 — Report and decide next steps

Steps:

1. Discuss outcome with Dan. Three cases:
   - High agreement (≥ 90% of states within ±1, mean delta ≈ 0):
     extraction is faithful; Opheim cross-val becomes evidence we
     can trust the CSVs for downstream compendium use.
   - Mid agreement (60-90%): identify systematic errors, fix the v2
     pipeline, re-emit CSVs, re-run Opheim, repeat.
   - Low agreement (< 60%): rethink the boundary curation
     assumptions; possibly per-row content-width handling becomes a
     priority.
2. If high-agreement: discuss whether to also score Newmark 2005
   for cross-validation triangulation, or move on to consuming the
   CSVs in the compendium.

---

**Testing Details:** Tests target behaviour, not data shape. Each
encoder is tested with a synthetic minimal-row dict that exercises
exactly its rule (so the test is independent of the v2 CSV column
layout — if columns change, the encoder signature changes and the
test catches it). The Missouri smoke test pins the end-to-end
behaviour against a real row whose Opheim score we can read directly
from her Table 1.

**Implementation Details**

- Module layout: `src/lobby_analysis/cogel/opheim.py` library;
  `scripts/cogel_1990_opheim_score.py` CLI.
- 22 encoders are simple functions; no classes hierarchy needed.
- Frequency-encoder rule: a known set of strings for "monthly"
  (e.g., "Monthly", "Monthly during session", "Monthly and at end of
  session", "3 reports per year" — verify Opheim's intent on
  multi-report-per-year states) maps to 1; "Annual", "Annually",
  "Biennial", "Quarterly", "Semiannually", "Permanent" all map to 0.
- Review-thoroughness encoder: `1 if any of {review_desk_all,
  review_field_all, review_desk_or_field_all} == "*" else 0`.
- Some COGEL columns may have N.A. cells (Opheim's source had the
  same issue — she dropped 3 states). Treat N.A. as score=0 for the
  dimension and tag the row with a `na_count` field.
- 47 states × 22 items = 1,034 cell lookups; runs in well under a
  second. No optimization needed.
- Output table is markdown-renderable for inclusion in
  RESEARCH_LOG when the validation completes.

**What could change**

- If our v2 CSV emission still has gaps for some Opheim states (CA,
  FL missing from Table 30 currently), Phase 2 step 3 skips them.
  We should fix the v2 pipeline to recover those states *before*
  treating Opheim cross-val as authoritative.
- The 2-year vintage gap (1988-89 vs 1990) means some real
  delta-of-2 cases will be genuine statutory changes, not extraction
  errors. Phase 3 step 2 must distinguish these via spot-check
  before declaring a v2-pipeline bug.
- If `disclose_compensation_by_employer` in Table 29 doesn't actually
  capture Opheim's "sources of income" item, we may need to redefine
  the encoder or add a new free-text matching rule. Opheim's item
  list overlaps with COGEL's columns but the labels aren't
  identical; verify with two known states (one high-disclosing, one
  low-disclosing) before scaling.
- If we discover Opheim's scoring uses tie-breaking rules or
  state-specific exceptions not described in the paper text, we may
  need to re-read the paper or accept the unexplained variance.

**Questions**

- Should we also encode Newmark 2005's 17-item index for triangulation
  on the dimensions Opheim and Newmark both cover (definitions +
  disclosure)? My recommendation: defer until after Opheim is
  green; triangulation is more useful when each individual rubric is
  validated.
- Does Opheim's "review of all reports" (her item) require ALL
  reports be reviewed, or any-of (desk OR field OR desk-or-field)?
  My read: any-of, since she scores it 1/0. Verify by reading her
  Table 1 vs our COGEL `review_*` columns for one high-review state
  (e.g., a state with `review_desk_all = "*"` only) and one low-
  review state.
- The frequency item — Opheim sourced it from Book of States 1988-89,
  not the Blue Book. Our Table 29 freq columns are from the Blue
  Book 1990. If the frequency cell on the CSV reads "Monthly during
  session" but Opheim's source reads "Annual" (1988-89 to 1990
  change), we get a delta. Are these real statutory changes or
  source-document inconsistencies? Hard to tell without consulting
  Book of States 1988-89, which we don't have.

---
