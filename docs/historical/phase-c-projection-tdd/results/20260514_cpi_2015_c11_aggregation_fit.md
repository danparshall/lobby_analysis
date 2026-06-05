<!-- Generated during: convos/20260514_cpi_2015_c11_tdd.md -->
# CPI 2015 C11 aggregation-rule empirical fit

**Date:** 2026-05-14
**Convo:** [`../convos/20260514_cpi_2015_c11_tdd.md`](../convos/20260514_cpi_2015_c11_tdd.md)
**Script:** [`../../../../scripts/fit_cpi_2015_c11_aggregation.py`](../../../../scripts/fit_cpi_2015_c11_aggregation.py)

## Question

CPI's methodology archive does not document how the 14 per-item
Lobbying Disclosure scores are aggregated into the category score.
The spec doc enumerated four candidate formulas; this fit identifies
which one CPI actually used.

## Method

For each candidate aggregator, compute the projected category score
for all 50 states from the per-state per-item ground truth, compare
against the published per-state aggregate in
`papers/CPI_2015__sii_scores.csv` (column `categories/10/score`,
Lobbying Disclosure), and report the absolute residual distribution.
Tolerance per the spec: ±1 on >48 of 50 states.

The CPI sub-category structure (counts 2/4/3/2/3) was extracted from
`papers/CPI_2015__sii_criteria.xlsx`, sheet 11, column A (each
indicator's row carries its sub-category label `11.1` through `11.5`).

## Results

| Candidate | Max abs residual | Mean abs residual | States off by >1.0 |
|---|---|---|---|
| simple mean (14 items) | 6.20 | 2.05 | 36 / 50 |
| de jure half + de facto half / 2 | 7.24 | 1.92 | 38 / 50 |
| sequential sub-cats 2/4/3/2/3 (a priori guess) | 2.52 | 0.91 | 18 / 50 |
| **CPI sub-cats from criteria.xlsx** | **0.05** | **0.03** | **0 / 50** |

CPI sub-category structure:

| Sub-cat | Question | Indicators | n |
|---|---|---|---|
| 11.1 | Is there a clear definition of a lobbyist? | IND_196, IND_197 | 2 |
| 11.2 | Are lobbyist registration processes effective? | IND_198, IND_200, IND_202, IND_204 | 4 |
| 11.3 | Are there detailed registration requirements? | IND_199, IND_201, IND_203 | 3 |
| 11.4 | Can citizens access the information reported by lobbyists? | IND_205, IND_206 | 2 |
| 11.5 | Is there effective monitoring of lobbying disclosure requirements? | IND_207, IND_208, IND_209 | 3 |

## Verdict

`category_score = mean(sub_cat_means)` where each sub-cat mean is the
unweighted average of its indicators. Max residual 0.05 across all 50
states (one-decimal rounding artifact of the published score).

## Side findings

- **Two data-quality glitches** force a normalization decision. Texas
  IND_199 and Massachusetts IND_203 carry the literal string `"100"`
  in a YES/MOD/NO column. The fit chooses between two interpretations:

    | Interpretation | Texas residual | Massachusetts residual |
    |---|---|---|
    | `"100"` -> YES (100) | +6.67 | +6.67 |
    | `"100"` -> NO (0) (invalid -> default fallback) | 0.00 | -0.05 |

  The NO-fallback interpretation is consistent with CPI's published
  aggregate. Codified in `_DE_JURE_TIER_TO_SCORE` (case-insensitive
  YES/MODERATE/NO match; anything else -> 0).

- **Competition ranking** (1224 style) is required to reproduce CPI's
  published per-category rank column. Sequential ranking with
  alphabetical tie-break (a-priori choice) was off-by-1 to off-by-2
  on 11 of 50 states.

## Implication for other rubrics

If other CPI-style scorecards in the Phase C rubric list (PRI 2010,
Sunlight 2015, Newmark 2017, Newmark 2005, Opheim 1991, HG 2007,
FOCAL 2024) use the same unweighted-mean-of-sub-category-means pattern,
the analogous fit procedure (try 3-4 closed-form candidates, pick the
one with the smallest max residual) should land each aggregation rule
in a single pass. PRI 2010's rollup rule is already paper-derived from
the archived `pri-calibration` work — start there, since the empirical
fit will confirm or falsify a known candidate.
