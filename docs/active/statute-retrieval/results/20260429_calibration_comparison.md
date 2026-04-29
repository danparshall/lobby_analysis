<!-- Generated during: convos/20260429_retrieval_pipeline_design.md -->

# Calibration Comparison: CA, TX, OH vs PRI 2010

**Date:** 2026-04-29
**Rubric:** PRI disclosure-law (61 items, 5 sub-aggregates)
**Scorer prompt version:** v1 with "read full statute" + exemption-narrowness rules

## Best results per state (latest prompt)

| Sub-aggregate | CA (run 3) | TX (run 4) | OH (run 4) |
|---|---|---|---|
| A_registration | 7 / 6 (+1) | 2 / 7 (-5) | 8 / 7 (+1) |
| B_gov_exemptions | 3 / 2 (+1) | 2 / 3 (-1) | 2 / 2 **match** |
| C_public_entity_def | 0 / 0 **match** | 0 / 0 **match** | 1 / 1 **match** |
| D_materiality | 1 / 1 **match** | 1 / 1 **match** | 0 / 1 (-1) |
| E_info_disclosed | 17 / 14 (+3) | 11 / 18 (-7) | 17 / 15 (+2) |
| Total | 28 / 23 (+5) | 16 / 29 (-13) | 28 / 26 (+2) |

Format: `ours / PRI (delta)`

## Sub-aggregate match rates

| Sub-aggregate | Matches | Rate |
|---|---|---|
| C_public_entity_def | 3/3 | 100% |
| D_materiality | 2/3 | 67% |
| B_gov_exemptions | 1/3 | 33% |
| A_registration | 0/3 | 0% (but CA/OH within ±1) |
| E_info_disclosed | 0/3 | 0% |

## OH run history (prompt iteration)

| Run | Prompt change | A | B | C | D | E | Matches |
|---|---|---|---|---|---|---|---|
| Run 1 | baseline (no A/C guidance) | 2/7 | 2/2 | 0/1 | 1/1 | 17/15 | 2/5 |
| Run 2 | + coverage-by-default rule | 9/7 | 2/2 | 1/1 | 1/1 | 17/15 | 3/5 |
| Run 3 | + three-tier exemption boundary | 3/7 | 2/2 | 1/1 | 1/1 | 17/15 | 3/5 |
| Run 4 | + read-full-statute + exemption-narrowness | 8/7 | 2/2 | 1/1 | 0/1 | 17/15 | 2/5 |

## TX run history

| Run | Prompt version | A | B | C | D | E | Matches |
|---|---|---|---|---|---|---|---|
| Run 1 | three-tier | 2/7 | 2/3 | 1/0 | 1/1 | 11/18 | 1/5 |
| Run 2 | reverted to coverage-by-default | 1/7 | 2/3 | 0/0 | 1/1 | 11/18 | 2/5 |
| Run 3 | + exemption-narrowness | 1/7 | 2/3 | 0/0 | 1/1 | 11/18 | 2/5 |
| Run 4 | + read-full-statute | 2/7 | 2/3 | 0/0 | 1/1 | 11/18 | 2/5 |

## Key diagnostic: TX E1 cascade

TX E = 11 (PRI = 18) is dominated by E1a=0 cascading to all 15 E1 sub-items. The scorer reads §305.004(4) ("persons whose only lobbying activity is compensating a registered lobbyist are exempt") as a blanket principal exemption. But non-exempt principals (who also communicate directly with officials) must register under §305.005 and disclose under §305.006. Fixing this single item would recover ~7 points on E.

## Provenance

- Retrieval agent prompt: `src/scoring/retrieval_agent_prompt.md`
- Scorer prompt: `src/scoring/scorer_prompt.md`
- Statute bundles: `data/statutes/{CA,TX,OH}/` (gitignored)
- Score data: `data/scores/{CA,TX,OH}/statute/` (gitignored)
