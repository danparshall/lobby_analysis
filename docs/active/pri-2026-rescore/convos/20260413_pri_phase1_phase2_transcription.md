# PRI Phase 1 + Phase 2 Transcription

**Date:** 2026-04-13
**Branch:** pri-2026-rescore

## Summary

Executed Phases 1 and 2 of the PRI 2026 accessibility re-score plan. Phase 1 transcribed PRI 2010's two rubrics from the paper into structured CSVs with a consistent atomic-item schema (every sub-item captured as its own row; scoring deferred). Phase 2 transcribed PRI's published 2010 per-state scores at the sub-component level (the only granularity the paper publishes) into two score CSVs and validated them programmatically against published totals across all 50 states.

The main finding during transcription: the "22-item" and "37-item" framings used in the plan and the scoring-rubric-landscape doc are slightly misleading about the rubrics' structure. PRI's accessibility rubric is really **8 questions** (Q1–Q8) where Q7 contributes 15 sortable-field sub-criteria (a–o) and Q8 contributes a 0–15 raw score normalized to 0–1 — summing to 22 max points across 22 atomic scorable rows. PRI's disclosure-law rubric is **5 sub-components** (A:11, B:4, C:1, D:1, E:20 → 37), where C and D are published as single 0/1 scores even though the paper describes sub-criteria (3 and 2 respectively), and E's 20-point max is not decomposed item-level in the paper body — scoring uses "higher of E1/E2 + double-count when both principal and lobbyist report F/G + separate J." This means Phase 3 modernization for E is effectively re-specifying scoring from scratch rather than preserving PRI weights.

Per user direction, the CSVs capture every sub-item atomically with a `data_type` column (mostly `binary`, plus `numeric_usd_or_null`, `numeric_percent_or_null`, `text`, `ordinal_0_to_15`) and no scoring/weighting assignments — those get assigned later in Phase 3.

## Topics Explored

- Location of PRI's two rubrics in the source paper (Section III for disclosure law, Section IV for accessibility)
- Item-level vs sub-component-level granularity available in the paper
- How PRI's E-score aggregation works and where item-level detail is underspecified
- OCR fidelity of Table 5 and Table 6 (clean; all 50 states reconcile)

## Provisional Findings

- Rubric CSVs written: 22 accessibility atomic items, 61 disclosure-law atomic items (A:11, B:4, C:4, D:5, E1:19, E2:18). Every item's text is verbatim from the PRI paper.
- 2010 score CSVs written: 50 states × Q1-Q8 for accessibility; 50 states × A/B/C/D/E for disclosure-law. Both include published total, percent, rank.
- Validation spot-check #1: 3 random items per rubric matched PDF text verbatim (accessibility Q3/Q7e/Q7l; disclosure A2/B3/E1f_iii).
- Validation spot-check #2: sub-component sums reconcile to published totals for **all 50 states** (plan asked for 5 — exceeded at no extra cost). Zero mismatches on either rubric.
- Accessibility Q8 column in Table 6 has OCR-dropped decimals on ~30 rows (shows "0" when percent column implies 0.1–0.3). Doesn't affect reconciliation because published total is also rounded consistently, but flagged in the data for awareness.

## Decisions Made

- CSV schema: `item_id`, `category`/`sub_component`, `item_text` (verbatim), `data_type`, `pri_notes`. No `max_points` or `scoring_scale` columns — scoring is Phase 3's job.
- Plan Q4 (self-consistency abort threshold): deferred, will decide after seeing pilot data.
- Plan Q2 (snapshot publication) and Q3 (subagents vs. SDK): deferred until Phase 4/7.
- Output directory: `docs/active/pri-2026-rescore/results/` (plan's hardcoded path was stale — branch is no longer `research-prior-art`).
- Phase 2 validation granularity: plan asked for item-level 2010 reconciliation; only sub-component-level is possible from the paper. Accepted substitution.

## Results

- `results/pri_2010_accessibility_rubric.csv` — 22 atomic items
- `results/pri_2010_disclosure_law_rubric.csv` — 61 atomic items
- `results/pri_2010_accessibility_scores.csv` — 50 states × Q1–Q8 + total
- `results/pri_2010_disclosure_law_scores.csv` — 50 states × A/B/C/D/E + total

## Open Questions

- **Phase 3 scope for E**: is it acceptable to re-specify E's 20-point aggregation from scratch, or should we preserve PRI's "higher of E1/E2 + F/G double-count + J separate" structure even though it's not clean at item level?
- **B1 polarity**: PRI doesn't state whether "gov exemption exists" hurts or helps the score. B2/B3/B4 seem designed to penalize weaker treatment of gov lobbying, so B1 likely negative — needs Phase 3 call.
- **Q8 raw 0–15 rubric**: never specified by PRI. 2026 rubric either drops Q8, redefines it, or inherits the ambiguity. Phase 3 call.
- **"Reporting frequency option" scoring (E1h/E2h)**: PRI footnote 89 is worded ambiguously ("1 point for reporting … less than three times a year"). Likely means "awards 1 if frequency ≥ quarterly" but unconfirmed.
