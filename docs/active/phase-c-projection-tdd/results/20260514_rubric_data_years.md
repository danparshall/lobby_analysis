<!-- Generated during: convos/20260514_rubric_plans_drafting.md (sub-session 0 of 5) -->

# Rubric data years vs publication years

**Date:** 2026-05-14
**Convo:** [`../convos/20260514_rubric_plans_drafting.md`](../convos/20260514_rubric_plans_drafting.md)
**Purpose:** Each rubric's *publication year* is not its *data year*. For the extraction pipeline to fetch the right statute vintage from Justia (or other archived-statute sources), we need to know which year's statutes each published rubric actually scored. This table is the working answer; gaps marked LOW confidence need direct user confirmation or deeper paper-methodology re-read.

## Why this matters

Each per-rubric projection function operates on `compendium_cells_for_state_year`. The "year" parameter must match the year the rubric's scoring reflected. If Sunlight published a "2015 Scorecard" but actually reviewed statutes in late 2014 / early 2015, then validating our extracted-from-Justia compendium cells against Sunlight requires we fetch the **2014-2015 statute snapshots**, not the 2015-as-of-December snapshots. Misaligned vintages cause "the extraction doesn't match Sunlight's scoring" failures that are vintage-mismatch artifacts, not extraction errors.

## Summary table

| Rubric | Publication year | Data year (statutes reviewed) | Source for data year | Confidence | Extraction-vintage implication |
|---|---|---|---|---|---|
| **Opheim 1991** | 1991 (received Dec 1989; accepted Apr 1990) | **1988-89** | Paper line 121-124: "from the Council of State Government's Blue Book 1988-89" + "Council of State Governments, The Book of the States, 1988-89" + "data are gathered from Council of State Governments, 1988, pp. 97-99" | **HIGH** — paper-explicit | Fetch 1988-89 statute snapshots for 47 in-scope states (MT, SD, VA excluded by Opheim). |
| **Newmark 2005** | 2005 | **6 panels: 1990-91, 1994-95, 1996-97, 2000-01, 2002, 2003** | Paper line 110-115 + endnote 2 (line 840-841: "The Book of the States had biennial editions until recently. Accordingly, data are biennial except for 2002 and 2003, which are annual") | **HIGH** — paper-explicit | Fetch 6 statute snapshots per state (one per panel). |
| **PRI 2010** | Nov 2010 | **~2009-2010 statutes** (cites 2008 lobbying-spending data as *context*, not the rubric's statute-review year) | Paper publishes Nov 2010; rubric scores disclosure laws as they were when the survey was conducted (late 2009 / early 2010) | **MEDIUM-LOW** — implicit; needs user/paper-methodology confirmation | Fetch statute snapshots dated **late 2009 / early 2010**. Already implemented (rubric #2 shipped 2026-05-14). |
| **CPI 2015 C11** (State Integrity Investigation) | Nov 9, 2015 | **~2014-2015 statutes** | Article cites Nov 2014 Arkansas reforms ("ballot measure that... barred"), and 2015 events like the $100 gift cap. SII pub Nov 9, 2015. | **MEDIUM** — implicit but well-bounded | Statute snapshots ~mid-2015 (during the SII review window). Already implemented (rubric #1). |
| **Sunlight 2015** | Aug 12, 2015 | **~2014-2015 statutes** (likely as of mid-2015) | Sunlight blog publication date: Aug 12, 2015 (per Newmark 2017 paper line 195-196 citing the Sunlight URL with that date) | **MEDIUM-LOW** — implicit; Sunlight blog dated mid-2015 | Statute snapshots **as of mid-2015** (matching SII period). User's framing — "wasn't actually checking the 2015 statutes" — is on point: it was mid-2015 statutes at best, not end-of-year 2015. Worth a Sub-1 paper re-read to firm up. |
| **Newmark 2017** | 2017 (Macmillan) | **~2015-2016 statutes** (BoS 2015 or 2016 edition) | Paper footnotes show URLs accessed May 25, 2016 (lines 152-153, 155); cites Newmark 2005's BoS 2005 errata work. BoS 2015 or 2016 edition is the upstream. | **MEDIUM** — implicit via accessed-dates | Statute snapshots ~2015 to early 2016 (BoS edition cutoff). |
| **HG 2007** (CPI 2007 Hired Guns) | 2007 | **~2006-2007 statutes for Q1-Q34, Q38**; **2002 reference year for Q35-Q37** | CPI methodology: "Center researchers developed 48 questions, and sought answers... by studying statutes and interviewing officials." Spec doc `items_HiredGuns.md` §6 notes Q35-Q37 reference year is 2002. Main items implicit. | **MEDIUM** (Q35-Q37 explicit; main items implicit) | Statute snapshots ~2006-2007 for the 34 main items; **2002 statute snapshot for Q35-Q37 aggregate-publication items**. Two distinct vintages within one rubric. |
| **FOCAL 2024** (Lacy-Nichols framework paper) | 2024 (Int. J. Health Policy & Mgmt.) | **N/A — framework synthesis, no data collection** | FOCAL 2024 paper itself is a framework; the 50 indicators are derived from synthesizing 15 predecessor rubrics, not from coding any jurisdictions. | **HIGH** — framework paper, no data | No statute extraction needed for FOCAL framework. Data year applies to the *applied* version (L-N 2025). |
| **L-N 2025** (FOCAL applied to 28 countries + US federal LDA) | 2025 (Milbank Quarterly) | **2019-2023 for 27 countries; 2025 for Israel** | Paper line 180-181 (verbatim): "Data for these sources were collected between 2019 and 2023 (Israel's data were collected in 2025, as the website was inaccessible prior to that)" | **HIGH** — paper-explicit | For US federal LDA validation row (81/182): statute snapshots in the 2019-2023 window. Most likely **circa 2020-2022** based on the mid-range of L-N's collection period, but the exact US-data-collection date within 2019-2023 may be in L-N's supplementary materials — flag for Sub-3 plan-drafting. |

## Inferred extraction-vintage requirements

If projection functions are validated against published per-state scores, the per-rubric extraction-vintage requirements are:

| Year | Rubrics requiring statute snapshots at this vintage |
|---|---|
| 1988-89 | Opheim 1991 (47 states) |
| 1990-91 | Newmark 2005 panel 1 (50 states) |
| 1994-95 | Newmark 2005 panel 2 |
| 1996-97 | Newmark 2005 panel 3 |
| 2000-01 | Newmark 2005 panel 4 |
| 2002 | Newmark 2005 panel 5; **HG 2007 Q35-Q37** (3 items) |
| 2003 | Newmark 2005 panel 6 |
| 2006-2007 | HG 2007 main items (Q1-Q34, Q38) |
| 2009-2010 | PRI 2010 |
| 2014-2015 | CPI 2015 C11; Sunlight 2015 |
| 2015-2016 | Newmark 2017 (BoS 2015 or 2016 edition cutoff) |
| 2019-2023 | L-N 2025 / FOCAL 2024-applied (US federal LDA only; no US state ground truth) |

**Total distinct vintages: 12**, ranging 1988-89 → 2025.

## Implications for Justia (or other archived-statute source) retrieval

- **Multi-vintage extraction is real.** A single state's projection across all 8 rubrics requires up to ~12 distinct statute snapshots over a 37-year span. Most rubrics cluster in 2-4 distinct years, but Newmark 2005 alone needs 6 panels.
- **HG 2007's split vintage** (2006-2007 for main items + 2002 for Q35-Q37) is a per-item-level vintage. Plan must specify per-item statute-year, not per-rubric.
- **FOCAL state projections are vintage-flexible.** Because FOCAL has no US-state ground truth, the "year" parameter for state-level FOCAL projections is a user choice. Recommended: align with the L-N 2025 collection window (2019-2023) so the projected-state-scores are comparable to the published-federal-LDA score.
- **`oh-statute-retrieval` (Track A) vintage scope** is currently OH 2007 + OH 2010 + OH 2015 + OH 2025. For multi-rubric validation across the full 8 rubrics, the OH bundle would need to expand to: OH 1988-89, 1990-91, 1994-95, 1996-97, 2000-01, 2002, 2003, 2006-2007, 2009-2010, 2014-2015, 2015-2016, 2019-2023. **The current 4-vintage OH bundle is a subset.**

## Confidence-improving next steps

Three rubrics have MEDIUM-or-lower data-year confidence (Sunlight 2015, CPI 2015, PRI 2010, Newmark 2017). Sub-1 / Sub-2 / Sub-3 plan-drafting agents should:

1. **Sunlight 2015**: read paper methodology section (`Sunlight_2015__state_lobbying_disclosure_scorecard.txt`) end-to-end during Sunlight plan drafting; flag exact research period.
2. **CPI 2015 C11**: re-read the CPI methodology pages (`papers/CPI_2015__sii_methodology.txt` if available) for the statute-review cutoff date.
3. **Newmark 2017**: confirm whether BoS 2015 or BoS 2016 was the edition used (paper line 149 cites BoS but specific edition not surfaced in this audit's grep).
4. **PRI 2010**: cross-reference with the PRI 2010 rubric's existing module to see if the PRI implementation already assumed a specific data year; reconcile if needed.

These are NOT blockers for plan drafting — plans can specify "vintage: per the rubric paper's methodology section, to be confirmed at implementation time" — but knowing the answer up-front avoids late-stage extraction-vintage churn.

## Provenance

This table is derived from grepping `papers/text/` for each rubric and cross-referencing with spec doc statements about "vintage." Specific paper-line citations are above. Where confidence is MEDIUM-or-lower, the data year is *inferred* (e.g., from publication date + research-period heuristics + URL-accessed-dates in footnotes), not paper-stated.
