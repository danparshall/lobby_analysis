# Sunlight Foundation 2015 — atomic-item audit

**Date:** 2026-05-07
**Plan reference:** [Phase A3 — Sunlight Foundation 2015 atomic-item audit](../plans/20260507_atomic_items_and_projections.md)
**Verdict:** **CASE B framing per the plan letter, with a substantive nuance — see "Recommendation" below.** No deeper sub-question decomposition exists in either the per-state CSV or the article methodology; the existing 5 items in `items_Sunlight.tsv` are simultaneously Sunlight's *headline categories* and its *atomic scoring units* (Sunlight does not score below this granularity).

## What was searched

### 1. Per-state data CSV (`papers/Sunlight_2015__state_lobbying_disclosure_scorecard_data.csv`)

50 state rows. Columns:

```
State, Grade, Total, Lobbyist Activity, Expenditure Transparency,
Expenditure Reporting Thresholds, Document Accessibility,
Lobbyist Compensation, State Lobbying Law, State Disclosure Portal
```

That is **exactly** 5 score columns (mapping 1:1 to the 5 criteria in the article methodology) plus aggregate columns (Grade, Total) and reference URL columns. There are **no** sub-question columns inside any category — each category has a single integer score per state, drawn from the per-criterion ordinal rubric.

Footnote markers appear on individual cells (`*`, `**`, `***`, `^`, `^^`) but the article text does not define them; these are state-specific qualifications, not additional indicators (already documented in `items_Sunlight.md` §7).

### 2. Article methodology (`papers/text/Sunlight_2015__state_lobbying_disclosure_scorecard.txt`)

Lines 137-192 enumerate the methodology completely. Five criteria, each defined by:
- One question prompt (e.g., "Lobbyist Activity: Do lobbyists have to reveal which pieces of legislation or executive actions they are seeking to influence?")
- One ordinal rubric tier list (the per-criterion scale already captured in `items_Sunlight.tsv` `scoring_rule` column)

**Verbatim source quote (article methodology preamble, lines 137-156):**

> "We evaluated every state according to the following criteria:
> 1. Lobbyist Activity: Do lobbyists have to reveal which pieces of legislation or executive actions they are seeking to influence?
> 2. Expenditure Transparency: Are lobbyists required to itemize all the expenses associated with their work, such as travel, holding an event, or buying gifts for lawmakers?
> 3. Expenditure Reporting Thresholds: Does the state require lobbyists to include all expenses in reports, or only those above a certain amount?
> 4. Document Accessibility: ... Can the public access lobbyist registration and expenditure forms?
> 5. Lobbyist Compensation: Does the state mandate that lobbyists disclose how much they receive from a client?"

The methodology has narrative observation sections ("Registering a problem", "An expenditure issue", "Miscellaneous observations") that discuss qualitative findings — but Sunlight explicitly does not score on those observations. They are commentary, not scoring criteria. (Already flagged in `items_Sunlight.md` §3 and §4.)

### 3. Web fetch step (skipped)

The article URL hint (`sunlightfoundation.com/2015/08/12/how-transparent-is-your-states-lobbying-disclosure/`) was not fetched because the local extracted text already contains the full methodology section verbatim and the per-state CSV is also local. There is no plausible additional source of sub-questions.

## What the verdict means

The plan's Phase A3 framing offered two outcomes:
- **CASE A:** atomic items found beneath the 5 headline categories
- **CASE B:** only the 5 headline categories — drop Sunlight 2015 from the contributing-rubric set

The literal answer is CASE B: there are no sub-questions decomposing any of the 5 categories.

However, the framing in the plan presupposes the 5 items in `items_Sunlight.tsv` are *headline categories* with deeper atomic items waiting to be found. The audit shows that's not Sunlight's structure — Sunlight's rubric is *intentionally shallow*, with each category being a single ordinal indicator scored on its own per-criterion tier scale (4-tier / 4-tier / 2-tier / 5-tier / 2-tier). The 5 items in `items_Sunlight.tsv` already are the atomic scoring units. There is nothing more granular to extract.

## Per-item scoring scales (for reference; verbatim from article)

| # | Criterion | Tier count | Scale |
|---|-----------|------------|-------|
| 1 | Lobbyist Activity | 4-tier | -1, 0, 1, 2 |
| 2 | Expenditure Transparency | 4-tier | -1, 0, 1, 2 |
| 3 | Expenditure Reporting Thresholds | 2-tier | -1, 0 |
| 4 | Document Accessibility (= "Form Accessibility") | 5-tier | -2, -1, 0, 1, 2 |
| 5 | Lobbyist Compensation | 2-tier | -1, 0 |

Theoretical total range = sum-of-maxes 6 to sum-of-mins -6. Letter-grade cutoffs reverse-engineered from CSV: A ≥ 4; B 2-3; C 0-1; D -2 to -1; F ≤ -3 (`items_Sunlight.md` §2).

## Recommendation: keep Sunlight 2015, do not drop

The plan's drop rule is "any rubric where atomic items don't exist after a reasonable effort is excluded." The intent of that rule is to exclude rubrics whose published per-state scores cannot be reproduced from a known set of cell values — i.e., rubrics where the projection function `f_rubric(compendium_cells, vintage) → rubric_score` is impossible to define because the scoring rule is opaque or only defined at headline-aggregate level.

That is **not** Sunlight's situation. Sunlight's per-criterion scoring rules are fully specified (per-tier descriptors, verbatim in `items_Sunlight.tsv`), and the per-state per-criterion scores are published in the CSV. A projection function `f_sunlight(compendium_cells, 2015) → (5 per-criterion ordinal scores) → total → letter grade` is straightforwardly implementable from the existing 5 atomic items. The aggregation rule is "sum the 5 ordinal scores, apply the empirically-derived letter-grade cutoffs."

What Sunlight 2015 *cannot* offer is **breadth** — only 5 atomic items, where rubrics like HiredGuns 2007 (47 items) or PRI 2010 (83 items) provide many more cells of validation per state. So Sunlight is a *low-information* contributing rubric. But low information is not zero information — the 5 cells × 50 states = 250 published score values are a valid sanity-check signal for the extraction prompt's coverage of:

- Lobbyist activity reporting (bill/action + position) — a row that also appears in HiredGuns Q5/Q20, Newmark, Opheim
- Expenditure itemization granularity — overlaps HiredGuns Q14/Q15
- Expenditure reporting threshold (existence of any threshold) — overlaps HiredGuns Q15 (which scores threshold magnitude on an ordinal scale)
- Form/document accessibility (digital filing + public access) — overlaps HiredGuns Q28-Q34, CPI 2015 C11
- Lobbyist compensation disclosure — overlaps HiredGuns Q13/Q27, Newmark `disc_*` items

Each of these maps to compendium rows that other rubrics also read — so Sunlight contributes *cross-rubric redundancy* on those rows even though its own item count is small.

**Suggested action:** Treat the existing `items_Sunlight.tsv` as the atomic-item set (no `_atomic.tsv` variant needed; no edits required). In Phase B, build the projection mapping for 5 items as documented. In Phase C, validate against the published 50-state CSV. The work is small enough that the cost of including Sunlight is low even if the validation signal is also low.

## What would change the verdict

The audit would be re-opened (and the recommendation reversed toward dropping) if any of the following surfaced:

1. A separate Sunlight Foundation 2015 *methodology supplement* exposing per-category sub-questions that the article body omits. None was referenced in the article text, and the only forward-pointer is to a "forthcoming" Open Data Policy Guidelines analysis (line 33) that would be a different scorecard entirely.
2. The Sunlight 2011 predecessor work (Schuman, Buck, Dunn) having published per-state per-sub-question data that the 2015 update suppressed. The 2015 article describes itself as "an update of that database with an emphasis on lobbyist disclosure requirements" (lines 20-21), which suggests the 5-criterion structure is new to 2015; the 2011 predecessor may have had a different (possibly finer-grained) structure. Worth a Phase A footnote if the 2011 dataset is locatable, but not load-bearing — Sunlight 2015 stands or falls on its own atomic-item set, not the 2011 predecessor's.
3. The footnote markers (`*`, `**`, `***`, `^`, `^^`) on individual CSV cells turning out to encode systematic per-state qualifications that effectively constitute sub-question scoring (e.g., `1*` means "tier 1 with caveat X"). Without a published key, this remains uninterpretable, and sub-question extraction is not possible from footnote markers alone.

## Files touched / not touched

- **Created:** this audit note at `docs/active/compendium-source-extracts/results/20260507_sunlight_atomic_audit.md`
- **Not modified:** `docs/active/compendium-source-extracts/results/items_Sunlight.tsv` (existing 5 items already at atomic level; no change required)
- **Not modified:** `docs/active/compendium-source-extracts/results/items_Sunlight.md` (existing methodology note already accurate)

## Decision needed from user

The plan's literal CASE A / CASE B dichotomy assumed a "sub-questions found ⇒ extract" / "no sub-questions ⇒ drop" choice. The audit's actual finding sits between those: no sub-questions exist *because Sunlight's rubric is shallow by design*, but the existing 5 items are still atomic in Sunlight's own scoring sense and projection-implementable.

User chooses one:

- **(a) Keep Sunlight 2015 in the contributing-rubric set** with the existing 5 items. Phase B builds a 5-item projection mapping; Phase C validates against the published 50-state CSV. (Recommended.)
- **(b) Drop Sunlight 2015 per the plan letter.** The 5-item rubric is judged too shallow to contribute meaningfully; the validation set shrinks by 1 rubric. Defensible if the user prioritizes breadth-of-atomic-items as a strict membership criterion.

The audit makes the recommendation but leaves the decision with the user.

## User decision (2026-05-07 pm)

**Per-item rule applied:** "If we can cleanly map our compendium items onto the rubric, then fine. Drop anything we can't."

Per-item adjudication:

| # | Indicator | Underlying cells | Verdict |
|---|---|---|---|
| 1 | Lobbyist Activity (4-tier) | 2 binaries: `bill_or_action_disclosed`, `position_disclosed`. Tiers 2/1/0/-1 are a deterministic function of the joint state (both / first only / general subjects only / neither). | **KEEP** |
| 2 | Expenditure Transparency (4-tier) | 1 enum cell: itemization-level ∈ {not_reported, lump, categorized, itemized}. | **KEEP** |
| 3 | Expenditure Reporting Thresholds (2-tier) | 1 binary cell: any-threshold-exemption-exists. | **KEEP** |
| 4 | Document Accessibility (5-tier) | 3-4 conflated sub-features (digital filing, registration form online, expenditure form online, blank forms online) collapsed into one ordinal whose -1/-2 distinction is a documented near-typo (audit §"Per-item scoring scales" + verbatim notes column). Tier-from-cells function not well-defined. | **DROP** |
| 5 | Lobbyist Compensation (2-tier) | 1 binary cell: lobbyist-earnings-disclosed. | **KEEP** |

**Final scope for Phase B:** Sunlight items 1, 2, 3, 5 (4 of 5) enter the contributing-rubric set. Item 4 is excluded from projection mapping.

**Note on existing TSV/CSV artifacts:** `items_Sunlight.tsv` is left unedited (it remains a verbatim per-paper extraction; item 4 still belongs in it as published). The exclusion is at the *projection-mapping layer*, not the source-extract layer. Phase B's `sunlight_projection_mapping.md` will document item 4 as deliberately excluded, with this audit note as the reason.
