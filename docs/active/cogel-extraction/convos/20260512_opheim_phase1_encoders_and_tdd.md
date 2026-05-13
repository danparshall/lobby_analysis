# Opheim Phase 1 — 22 encoders + TDD suite

**Date:** 2026-05-12 → 2026-05-13
**Branch:** cogel-extraction
**Plan:** `plans/20260507_opheim_cross_validation.md` (Phase 1)
**Prior convo:** `convos/20260511_opheim_phase0_and_dual_psm_recovery.md`

## Summary

Shipped Phase 1 of the Opheim cross-validation plan: the 22-item
encoder list (`src/lobby_analysis/cogel/opheim.py`) and a 60-test TDD
suite (`tests/test_cogel_opheim.py`). Encoders run cleanly on real
data — 35 of 47 Opheim states scoreable from the current v2 CSVs;
Missouri smoke-test passes within ±2. The remaining 12 states are
absent from one or more of T28/T29/T30/T31 due to v2-extraction
problems separate from the encoder design — same bucket as the
2026-05-11 CA/FL dual-PSM fix, mechanically distinct.

A non-committed quick rollup over the 35 scoreable states gave a
preview of agreement: mean Δ = −2.11, stddev 3.96, only 4/35 exact
matches, 11/35 within ±1, 14/35 within ±2. **Below the plan's
mid-agreement band**, but it is premature to declare "low-agreement"
(rethink boundary curation) because the bidirectional error pattern
strongly implicates extraction, not encoder design: high-Opheim
states under-score (NJ −10, WI −8, MA −7, WA −7, IN −6); low-Opheim
states over-score (AR +8, WY +6, NH +5, WV +3). Preview artifacts
committed at `results/20260512_opheim_phase2_preview.{csv,md}`.

The 47-state coverage test is `xfail(strict=False)` until v2
extraction is fixed — it will start passing automatically when the
12-state gap closes.

## Topics Explored

- Opheim §III paragraph-by-paragraph mapping of the 22 items to T28/
  T29/T30/T31 columns. All 7 definition items map directly to T28
  cols 0-6 (positional). 8 disclosure items map to T29 with two
  exceptions discussed below. 7 oversight items split: 1 review item
  on T30 (any-of three review_*_all columns per Phase 0 settlement),
  6 authority items on T31 with one (penalties) special-cased
  because the COGEL column is amount-bearing not marker-bearing.
- Spot-check on `disclose_compensation_by_employer ↔ sources_of_income`
  (deferred from Phase 0). NJ/WI score 18 in Opheim AND have `*` in
  this column → consistent with the mapping. WA scores 18 in Opheim
  but the column is BLANK → either the mapping is wrong OR WA's row
  is mis-extracted (the WA `disclose_other` cell shows `(il)`
  footnote, suggesting decoration). Mapping kept provisional.
- Resolution of `disclose_other_influence_activities` ambiguity. T29
  has two catch-all columns (`disclose_contributions_for_lobbying`
  for peddling-side, `disclose_other` for the bucket). Opheim's
  wording — "other activities that might constitute influence
  peddling or conflict of interest" — covers both, so encoder uses
  any-of. Flagged for reconsideration if Phase 3 surfaces
  systematic over-scoring at this item.
- T31 `auth_impose_administrative_penalties_amount` is an AMOUNT
  column, not a marker — cells hold numeric dollar amounts (e.g.
  `1,000`), asterisks, or absence indicators (N.A./em-dash/
  underscore/empty). Encoder: 1 if cell contains `*` OR any digit.
- Plan's "All seven directly mappable" line in the disclosure
  section is a typo — there are 8 disclosure items. The 7+8+7=22
  count is consistent everywhere else.
- Frequency encoder rule: simpler than a known-string set. The plan
  suggested enumerating monthly variants. Better: lowercase
  substring match on "monthly" OR "in and out" / "in-and-out". This
  handles the OCR-garbled T29 strings without an explicit deny-list.

## Provisional Findings

### Phase 1 deliverables

- `src/lobby_analysis/cogel/opheim.py` (267 lines): `OpheimItem`
  dataclass with `item_id` / `dimension` / `description` /
  `cogel_table` / `cogel_column_keys` / `encoder`; 22 entries; four
  encoder factories (`_marker`, `_any_marker`, `_freq_monthly`,
  `_penalties`); `score_state(t28, t29, t30, t31) -> int` rollup.
- `tests/test_cogel_opheim.py` (60 test cases): 18 simple-marker
  items × 2 polarities (parametrized = 36 cases); 5 freq cases;
  3 other-influence-activities cases; 4 review-thoroughness cases;
  5 penalties cases; 3 structural invariants; 2 score_state rollup
  cases; Missouri ±2 smoke test; 47-state coverage test
  (`xfail(strict=False)`).
- Full suite: **398 passed, 5 skipped, 1 xfailed, 3 pre-existing
  failures** in `tests/test_pipeline.py` (missing
  `data/portal_snapshots/`, documented main-line issue carried from
  the 2026-05-10 baseline).

### Phase 2 preview (non-authoritative rollup over 35 scoreable states)

| Metric | Value |
|--------|-------|
| Exact (Δ=0) | 4/35 (11%) |
| Within ±1 | 11/35 (31%) |
| Within ±2 | 14/35 (40%) |
| Mean Δ | −2.11 |
| Stddev | 3.96 |
| Missouri Δ | +2 (ours=7, opheim=5) |

The directional pattern is the load-bearing signal: high-Opheim
states under-score; low-Opheim states over-score. See
`results/20260512_opheim_phase2_preview.md` for the mechanistic
hypotheses and full per-state table.

### Coverage gap

12 of 47 Opheim states absent from one or more v2 CSVs: AZ, CO, DE,
GA, IL, KY, NM, OH, PA, RI, SC missing from T28+T29 (DE/RI/SC also
missing from T30, DE from T31); IA missing from T29. This is the
v2-extraction-pipeline gap anticipated by plan §"What could change"
§1; same conceptual bucket as the 2026-05-11 CA/FL fix.

## Decisions Made

- Phase 1 shipped. The 22 encoders are the auditable artifact for
  the cross-validation comparison; they bind explicitly to CSV
  column names and document Opheim's coding rule in each entry's
  `description` field.
- `disclose_compensation_by_employer ↔ sources_of_income` mapping
  kept (provisional, weakly supported by WA disconfirmation).
  Encoder documents this in its description.
- `disclose_other_influence_activities` resolved to any-of
  (`disclose_contributions_for_lobbying`, `disclose_other`). Encoder
  documents this in its description.
- 47-state coverage test marked `xfail(strict=False)` rather than
  failing CI. The known 12-state gap is tracked in the test reason
  string + this convo + the Phase 2 preview MD; the test will XPASS
  automatically when v2 extraction closes the gap.
- The plan doc is NOT updated. The plan's Phase 1 steps were
  followed as written; the four encoder-design decisions above are
  documented here (per the plan's intent that encoder bodies carry
  the per-item provenance, not the plan itself).
- Phase 2 driver script deferred — three reasonable next moves
  flagged for user choice: checkpoint here, build Phase 2 driver
  next, or close the 12-state gap first. User chose checkpoint.

## Results

- `src/lobby_analysis/cogel/opheim.py` — 22-encoder module
- `tests/test_cogel_opheim.py` — 60-case TDD suite
- `docs/active/cogel-extraction/results/20260512_opheim_phase2_preview.csv` — per-state preview (47 rows, 35 with derived scores, 12 with `missing_in` flag)
- `docs/active/cogel-extraction/results/20260512_opheim_phase2_preview.md` — preview narrative + diagnosis hypotheses

## Open Questions

- **12-state extraction gap** (AZ, CO, DE, GA, IL, IA, KY, NM, OH,
  PA, RI, SC). T28/T29 dominate the gap, T30/T31 less so. Mechanism
  unknown — could be y-band detection failure (like CA/FL on T30) or
  a different pathology since multiple scans are involved. Next-
  session investigation candidate.
- **NJ/WA `disclose_compensation_by_employer` divergence.** WA scores
  18 in Opheim but has blank value. Spot-check NJ T29 row
  multimodally against scan to test the asterisk-→-em-dash misread
  hypothesis. If real, this is the dominant under-scoring cause.
- **Arkansas over-scoring.** Opheim AR=0, ours=8. The garbled
  `freq_lobbyist` value strongly suggests adjacent-row contamination
  on the AR y-band. If confirmed, an "AR-class" extraction error
  may affect WY/NH/WV too.
- **Provisional `sources_of_income` mapping.** Phase 0 spot-check
  was inconclusive (NJ/WI confirm, WA disconfirms); Phase 1
  development didn't strengthen it. Resolves only via per-row
  multimodal verification of WA, or a deeper read of Opheim's
  source documents.
- **47-state coverage test xfail.** Will automatically XPASS when
  the gap closes. Watch for this signal — it's the clean indicator
  that Phase 2 can run authoritatively.

## Next Steps

(Per the user's choice of "checkpoint + push," next session will
pick one of these three paths.)

- **Phase 2 driver script** — `scripts/cogel_1990_opheim_score.py`
  emitting the authoritative `results/<date>_opheim_validation.csv`
  across all 47 states, with `_missing_in:` field for the 12 gap
  states. Caveat: results inherit the extraction gap; useful as a
  before/after baseline for the gap fix.
- **Close the 12-state T28/T29 gap** — investigate why those states
  drop out, fix the extraction, regenerate the 4 CSVs, watch the
  coverage test XPASS. Higher value but unscoped — needs its own
  diagnosis session like the 2026-05-11 CA/FL session.
- **Alabama overflow fix on T29** — deferred from 2026-05-11. The
  cell-boundary collision pathology is structurally similar to the
  AR over-scoring hypothesis here, so resolving AL may shed light
  on AR/WY/NH simultaneously.
