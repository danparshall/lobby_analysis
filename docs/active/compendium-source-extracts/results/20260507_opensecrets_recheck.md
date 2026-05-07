# OpenSecrets 2022 — atomic-item audit recheck

**Plan:** [`plans/20260507_atomic_items_and_projections.md`](../plans/20260507_atomic_items_and_projections.md), Phase A1.
**Date:** 2026-05-07.
**Supersedes (in part):** [`20260507_opensecrets_atomic_audit.md`](20260507_opensecrets_atomic_audit.md) — that note is preserved verbatim. This recheck does not erase it; it amends the verdict.
**Recheck verdict:** **CASE 2 — worked examples found, no formal per-tier definitions.** The drop verdict is **OVERTURNED** for categories 2, 3, and 4. Category 1 alone fails the criterion; OpenSecrets 2022 is restored to the contributing-rubric set as a **partial** rubric (3 of 4 categories projectable via few-shot calibration).

## What changed since the prior audit

The prior audit correctly characterized the methodology block (lines 196–216) as exposing only baseline anchors at score 4 and "depending on the individual circumstances" for scores 0–3 in categories 1, 2, and 3. That much stands.

What the prior audit underweighted is the **Rankings** narrative section (lines 221–245) plus scattered population-level statistical anchors. Read together, these supply enough worked examples to calibrate few-shot projection for categories 2, 3, and 4 — even though the article never publishes a formal per-tier definition.

The prior audit's framing — "the function from atomic cells to per-category scores is not published — the rubric author's analyst judgment is doing the work" — is structurally correct but operationally too strict. A few-shot projection function does not need formal definitions; it needs **named worked examples that pin score-to-statute mappings at multiple points along the ordinal**. OpenSecrets supplies those.

## Worked examples found

Captured verbatim in [`opensecrets_worked_examples_2022.csv`](opensecrets_worked_examples_2022.csv) — 18 rows, covering 5 named states (WA, ND, SD, VA, OK), 2 score-band anchors (≥16 and <10 totals), and 5 population-level statistical anchors. Highlights:

- **Category 4 (public availability), score = 5 anchored by Washington** (lines 228–230, verbatim): "Washington state's site allows easy navigation between categories, auto-populates lists which can be filtered and has a clear link to download results at any time." This single sentence pins all three sub-facets at max simultaneously and gives the projection function a positive exemplar.
- **Category 4 low-end anchored by ND, SD, VA** (lines 236–237, 239–245): explicit failure modes named — "scored poorly on ease of search, download ability and availability of lobbyist/client lists" (ND/SD); "does such a poor job of making that information available to the public" (VA).
- **Category 3 (timely), 5 anchored by top-tier subset** (lines 225–227): "perfect scores in timely disclosure, requiring monthly reports throughout the year." Plus 0–1 anchored by ND/SD: "only require reporting once a year" (lines 234–236).
- **Category 2 (compensation), 0 anchored by bottom-tier band** (lines 231–233): "nearly all of the poorest scoring states... received a zero for the fact that compensation reporting is not required." Plus full-disclosure anchored by VA being in the bottom on total but ≥4 on cat 2 (lines 238–241) — useful negative-correlation exemplar.
- **Category 1 (lobbyist/client) negative anchor by Oklahoma** (lines 60–66): the "lobbyists communicate amongst themselves" practice is explicitly described as failing best practice — places OK at most at baseline = 3, not 4.

Plus statistical anchors that constrain the population-level distribution and serve as sanity checks on any projected score:

- 17 states cat 2 = 0 (lines 78–79)
- 7 states cat 2 = 1–3 (lines 79–81)
- 26 states cat 2 = 4–5 (lines 266–267)
- 20 states cat 3 ≥ 4 (lines 100–101)
- 16 states cat 3 = 5 candidates (lines 279–280)

## Per-category projectability assessment

| Cat | What is anchored | Projectable from compendium cells? |
|-----|------------------|----------------------------------|
| 1 — lobbyist/client disclosure | Score 3 = baseline (both identified); score 4 = separate registrations. Score 5 undefined; no per-state worked examples. Only OK as a negative exemplar for "not score 4". | **NO** — too few anchors, no positive worked example for any individual state. |
| 2 — compensation | Score 0 (no disclosure), 4 (full, baseline), 5 (exceeds baseline) explicit in methodology. Worked examples: ND/SD/bottom-band = 0; VA = ≥4. Population anchors fix 17/7/26 split across 0 / 1–3 / 4–5. | **YES** — few-shot projectable to ±1 score. |
| 3 — timely disclosure | Score 4 = monthly-in-session/quarterly-otherwise (baseline); 5 = monthly year-round. Worked examples: ND/SD = once-yearly (low); top-tier subset = monthly year-round (5). Population anchors fix 20 states ≥4 and 16 states = 5. | **YES** — few-shot projectable. |
| 4 — public availability | Sub-facets explicitly weighted (search 2, downloads 2, lists 1). WA = 5 (positive exemplar); ND/SD/VA = low (negative exemplars). | **YES** — few-shot projectable per sub-facet, and the explicit weights mean the composite is a deterministic sum once the sub-facets are scored. |

**Overall:** 3 of 4 categories projectable. Category 1 contributes a maximum of 5 points to a 0–20 total — i.e., 75% of the rubric (15 / 20 points) is projectable. The remaining 5 points (cat 1) are the irreducible OpenSecrets-judgment portion.

## Implication for Phase A1

OpenSecrets 2022 is **restored to the contributing-rubric set** with the following caveat documented:

- Phase-C projection function `project_OpenSecrets(compendium_cells, vintage) → 0–20 score` is writable for cats 2, 3, 4 (15 points). For cat 1, the projection returns a fixed prior (e.g., 3 = baseline unless the compendium row "lobbyist-client separate registration = yes" supports 4).
- Calibration uses the worked examples in `opensecrets_worked_examples_2022.csv`. WA / ND / SD / VA / OK provide named per-state anchors. The 5-state, 13-state-with-bands set is small but sufficient for few-shot prompting.
- Cross-state sanity checks against OpenSecrets per-state totals remain available regardless of cat 1 ambiguity, because cat-1 contributes at most ±1 noise across states (range 3–4 with score 5 unattested in the article).

## What I did NOT find (so future agents don't redo this search)

- **No published per-tier definition table.** Categories 1, 2, 3 do not have anything resembling "score 1 = X, score 2 = Y, score 3 = Z." The text repeatedly uses "depending on the individual circumstances."
- **No published per-state per-category numerical scores in the article text.** Line 195 references a "complete list" hosted at the OpenSecrets URL, but the URL returns 403 to non-browser fetches and the rendered map widget does not surface per-category breakdowns to web-fetch tools (verified 2026-05-07). If the user has browser access to the OpenSecrets site, the per-state per-category scores are likely retrievable manually — that would convert this CASE 2 verdict into something stronger (deterministic projection benchmarkable against per-cell ground truth).
- **No inter-coder reliability / methodology supplement.** None published.

## Reversibility note

If the user pulls per-state per-category numerical scores from the OpenSecrets map widget (manually, in a browser), append them to `opensecrets_worked_examples_2022.csv` and the projection-function calibration set grows from ~5 named exemplars to all 50 states. That would make OpenSecrets a first-class Phase-C sanity check rather than a partial one. Until then, treat it as a partial rubric covering ~75% of the score-mass.
