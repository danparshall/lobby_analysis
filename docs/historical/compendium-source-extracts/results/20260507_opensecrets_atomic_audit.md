# OpenSecrets 2022 atomic-item audit (Phase A1)

**Plan:** [`plans/20260507_atomic_items_and_projections.md`](../plans/20260507_atomic_items_and_projections.md), Phase A1.
**Date:** 2026-05-07.
**Verdict:** **DROP from contributing-rubric set** (CASE B, with nuance — see below).
**Reversibility:** drop is reversible. If OpenSecrets publishes a v2 scorecard with sub-anchors per category, the rubric can be re-added without invalidating any other rubric's projection work.

## TL;DR

The existing 7-row extraction in `items_OpenSecrets.tsv` already captures the **maximally-atomic decomposition the published methodology supports**. There is no further decomposition to find. Categories 1, 2, and 3 are each scored as a single 0–5 ordinal where the rubric author exercises holistic judgment; the article does not publish per-cell sub-anchors that an extraction-based projection function could read deterministically. Category 4 IS decomposed into three sub-facets (already captured), but those three sub-facets are themselves "more subjective and can have gray areas" by OpenSecrets' own admission (line 211 of the source text).

OpenSecrets 2022 therefore cannot serve as a Phase-C per-row sanity check on extracted compendium cells in the way the plan's success criterion requires — its scoring is not reproducibly decomposable from atomic cell values.

The 7-row TSV stays in place (per the plan's "do not delete" instruction). It remains useful as a coarse cross-check at the per-state aggregate level (the published per-state 0–20 totals can be compared to projections from other rubrics that share the same underlying compendium rows) but it does not contribute new atomic items to the compendium row set.

## What I searched

1. **Full read of the source article text** — `papers/text/OpenSecrets_2022__state_lobbying_disclosure_scorecard.txt` (325 lines, the complete 11-page article). The methodology section is lines 196–216.
2. **Existing extraction artifacts** — `results/items_OpenSecrets.tsv` (7 rows) and `results/items_OpenSecrets.md` (companion methodology note). Both already document the score-anchor structure exhaustively.
3. **Web searches** —
   - "OpenSecrets state lobbying disclosure scorecard 2022 methodology atomic indicators"
   - "opensecrets.org state lobbying scorecard methodology sub-questions"

   Both searches returned the scorecard URL (`opensecrets.org/news/reports/layers-of-lobbying/lobbying-scorecard`), the news-release URL (`opensecrets.org/news/2022/06/opensecrets-releases-new-state-lobbying-disclosure-scorecard/`), and the federal-lobbying methodology page (`opensecrets.org/federal-lobbying/methodology`). The first two URLs return HTTP 403 to non-browser fetches, but the rendered article text is already in `papers/text/`. The third URL (federal methodology) is for federal LDA data-processing pipelines, not the state scorecard.
4. **Web-search snippets explicitly confirmed no further decomposition exists.** Quoting the search-tool's summary: "The results provide details on the four main scoring categories but not on the detailed granular metrics (atomic indicators)... You may need to access the full scorecard report directly for information on that specific aspect" — and the full scorecard report IS what `papers/text/` contains.

## What the published methodology actually exposes

Quoting verbatim from `papers/text/OpenSecrets_2022__state_lobbying_disclosure_scorecard.txt`:

**Category 1 — lobbyist/client disclosure (lines 196–199):**
> "Each of the four key areas discussed above was graded on a five-point scale. For lobbying/client disclosure, the baseline score was three and states that require separate registrations for the lobbyists and clients were assigned a four."

This is a **single 0–5 ordinal** with two named anchors (3 = baseline; 4 = separate registrations) and no sub-question decomposition. The score-5 anchor is not even defined in the text — flagged as a gap in `items_OpenSecrets.md` §7.

**Category 2 — compensation (lines 199–209):**
> "For compensation and timely reporting, a score of four was assigned to those states that are at least requiring the baseline practices discussed above and a score of five for those that are exceeding the baseline. States with scores that fall below the baseline receive a score between zero and three, depending on the individual circumstances. For instance, states that do not require disclosure of compensation received a score of zero for that category. As detailed earlier, several states have partial compensation disclosure. Those received scores of between one and three in relation to the level of compensation disclosed."

Single 0–5 ordinal. The 0 and 4/5 anchors are explicit (no disclosure / baseline / exceeds baseline). Scores 1–3 are explicitly "depending on the individual circumstances" — i.e., scored by analyst judgment, not by atomic-question yes/no answers. There are no published sub-questions.

**Category 3 — timely disclosure (lines 199–209, same passage as category 2 + lines 98–101):**
> "In our scoring system, the baseline for timely disclosure is set to monthly reporting when the legislature is in session, and quarterly otherwise."

Single 0–5 ordinal. Anchors: 4 = baseline (monthly in-session, quarterly otherwise); 5 = monthly year-round; 0–3 = "depending on the individual circumstances" (e.g., once-yearly = bottom). Same pattern as category 2: holistic judgment for sub-baseline scores.

**Category 4 — public availability (lines 210–216):**
> "The categories related to public availability of the disclosed data are more subjective and can have gray areas. Within the five points allocated to this category, one point is dedicated to the availability of lobbyist and client lists. Partial points were assigned based on lists that are available, but not as easily accessed. Two points each were assigned to user-friendly search and availability of downloadable data."

This IS decomposed: 3 named sub-facets with explicit point weights (search=2, downloads=2, lists=1). Already captured in the existing TSV as `public_avail_search`, `public_avail_downloads`, `public_avail_lists`. But OpenSecrets explicitly acknowledges the sub-facets are "more subjective" — partial points are assigned by analyst judgment without per-state-per-sub-facet anchors.

## Why "no atomic items" (in the plan's sense) — even though the existing TSV has 7 rows

The plan's atomic-item criterion is implicitly: **does the rubric publish sub-questions whose answers can be computed from atomic compendium-cell values via a documented scoring rule?** That's what makes a rubric a Phase-C sanity check. Under this criterion:

- **HiredGuns 2007** publishes 47 yes/no sub-questions, each scored 0/3 with explicit point weights. Phase C can mechanically project compendium cells → HiredGuns score.
- **Newmark 2017** publishes 19 binary indicators with explicit 1/0 scoring. Same.
- **PRI 2010** publishes 83 sub-questions with detailed scoring rubrics. Same.
- **CPI 2015 C11** publishes 14 indicators with 100/50/0 scoring rules. Same.
- **OpenSecrets 2022** publishes 4 ordinal categories where 3 of the 4 are scored holistically (one anchor at 4, one at 5, "depending on circumstances" for 0–3). The 4th category has 3 sub-facets but they are "more subjective" and partial-pointed by analyst judgment.

In other words: OpenSecrets's "atomic items" already exist in the TSV, but they are **not deterministically computable from atomic compendium cells**. Categories 1, 2, 3 each compress an unspecified set of statute-reading judgments into a single 0–5 ordinal. A Phase-C projection function `project_OpenSecrets(compendium_cells, vintage) → 0–20 score` cannot be written, because the function from atomic cells to per-category scores is not published — the rubric author's analyst judgment is doing the work.

This is the structural reason for the drop. It is not "no atomic items exist in the methodology"; it is "the atomic items the methodology publishes are not the kind of atomic items the success criterion needs."

## What would change the verdict

Drop is reversible. Any of the following would re-qualify OpenSecrets as a contributing rubric:

1. **OpenSecrets publishes a v2 scorecard with explicit per-category sub-anchors.** E.g., for category 2: "score 1 = compensation in ranges with no per-lobbyist linkage, score 2 = ranges with per-lobbyist linkage, score 3 = exact dollar amounts not per-lobbyist, score 4 = exact per-lobbyist (baseline), score 5 = exact per-lobbyist + lobbyist-direction reporting (exceeds)." With anchors like that, a deterministic projection becomes writable.
2. **Per-state per-sub-question data is released.** OpenSecrets references a "complete list" of per-state scores (line 195) but only the 0–20 total per state and per-category 0–5 breakdowns are published — not per-sub-question. If they release the underlying per-judgment-call data (e.g., "for category 1, state X earned points because: lobbyist identified=yes, client identified=yes, separate registrations=no"), the rubric becomes decomposable.
3. **A third party (e.g., FOCAL 2024 or a successor scorecard) reverse-engineers the OpenSecrets scoring into yes/no sub-questions and publishes it as a derived rubric.** That would be a different rubric, not OpenSecrets, but would cover the same conceptual ground.

## What the existing 7-row extraction is still good for

Even though OpenSecrets is dropped from the **contributing-rubric set** for compendium row construction (Phase B), the 7 rows in `items_OpenSecrets.tsv` retain three uses:

1. **Coarse cross-check on per-state aggregate scores.** Once Phase C projections produce per-state HiredGuns / Newmark / PRI / CPI scores from a populated compendium, the OpenSecrets per-state 0–20 totals can be plotted against those — disagreements are diagnostic at the state level, not the row level.
2. **Conceptual coverage map.** OpenSecrets's 4 categories articulate what an end-user-facing scorecard cares about (who, how much, when, accessibility). When the compendium row set is finalized, a coverage check can confirm that every OpenSecrets category has at least one compendium row populating it — even if OpenSecrets itself can't be projected.
3. **Future re-add candidate.** If items 1–3 above resolve, the 7 rows are already in the schema and can be re-attached as a contributing rubric without re-extraction.

The existing files (`items_OpenSecrets.tsv` and `items_OpenSecrets.md`) are **not modified or moved** by this audit, per the plan's instruction.

## Flag for user review

The plan's expectation was that atomic items would exist for OpenSecrets. The honest answer after a careful read of the published article + targeted web search is that they do, but only at the level of the existing 7 rows — and 3 of those 7 rows are scored by holistic analyst judgment that a Phase-C projection function cannot replicate from atomic compendium cells. That makes OpenSecrets a coarser instrument than HiredGuns / Newmark / PRI / CPI for the success criterion's purpose.

If the user disagrees with this drop call — for example, if there is an OpenSecrets per-state per-judgment-call dataset I have not found, or if the user wants OpenSecrets retained as a coarse 4-category cross-check despite the lack of per-row projectability — please flag and the verdict can be revised.
