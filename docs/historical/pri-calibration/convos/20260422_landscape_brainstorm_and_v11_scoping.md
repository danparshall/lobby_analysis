# Landscape brainstorm + data-model v1.1 scoping

**Date:** 2026-04-22
**Branch:** pri-calibration (brainstorm); spawned data-model-v1.1 (v1.1 plan + TDD tests)
**Picking up from:** handoff from desktop session on 2026-04-21 pointing at `plans/20260421_rubric_unification_and_handoff.md`.

## Summary

The session resolved the key open question from the 2026-04-21 handoff (what's in `focal_2026_scoring_rubric.csv`), then widened into a landscape-scope brainstorm covering the five architectural pieces (Popolo, Open Civic Data, spatula, FOCAL, PRI) plus federal context (GAO, LDA, Lacy-Nichols 2025). The brainstorm surfaced three substantive reframings of the project — each moving away from "we score states" and toward "we are data infrastructure that makes existing-but-buried state lobbying disclosure usable." These reframings then fed a data-model v1.1 scoping exercise that produced a plan + TDD test suite on a new branch `data-model-v1.1`. The landscape report itself was deferred to a fresh-context session; this convo is the finish-convo checkpoint before handing off.

Pri-calibration's pilot work is **not affected** by the reframings — the calibration pipeline remains the internal QA mechanism for statute-reading LLM reliability, just stripped of any pretension that its scores will be a public output. The next pri-calibration session still picks up where 2026-04-21 left off: expand `LOBBYING_STATUTE_URLS` with `support_chapters` per H1, re-retrieve, re-score against existing PRI 2010 rubric, measure agreement uplift.

## Topics explored

- **Resolved open question #1 from 2026-04-21 plan:** `focal_2026_scoring_rubric.csv` is NOT a pre-existing draft unified rubric. It's a FOCAL-only 2026 operationalization of FOCAL 2024 (54 rows, 50 indicators − 1 compound + 5 decomposed). Dated 2026-04-14 on `focal-extraction` branch. Already handles three plan-called-out edge cases (3.3 decomposition, Westminster→US translation, FOCAL 1.2 threshold pinned to federal LDA). Original plan executes as written but using 2026 FOCAL as the FOCAL-side input.

- **Mapped the five-piece architecture** at two layers: (a) **data infrastructure** — Popolo (spec), Open Civic Data (project/governance), spatula (scraping framework) — and (b) **evaluation frameworks** — PRI 2010 (historical ground truth), FOCAL 2024/2026 (academic framework). The layers meet at `StateMasterRecord` (legal review) joined with filings (extracted data).

- **GAO-25-107523 is a compliance-axis resource, not a rubric.** The 2025 report is the 18th annual federal LDA compliance audit — it measures whether federal lobbyists comply with LDA requirements (21% miss covered-positions disclosure; 3,566 referrals to DOJ 2015-2024; 63% unresolved). It does NOT score the statute itself. This reclassifies the prior-art `scoring-rubric-landscape.md`'s framing of GAO as a "fourth rubric" — it's actually on a different axis.

- **Three-axis framing proposed then refined to four.** Initially: coverage / compliance / enforcement. Dan's refinement: split **coverage** into **Required × Available**, making it four axes. The 2×2 typology (required-available / required-not-available / not-required-available / not-required-not-available) cleanly locates the project's value: we convert "Required + Not Available" cells into "Required + Available" ones.

- **"Available" has two sub-dimensions:** legally available (is the filed data public under state law?) and practically available (is the public data usable given portal format?). Project's LLM/OCR/PDF extraction fixes practical-availability gaps; legal-availability gaps require statute reform.

- **Lacy-Nichols 2025 ("Lobbying in the Shadows", Milbank Quarterly)** applies FOCAL internationally with weighted 0/1/2 scoring (182-pt total). US federal = 45% (82/182); Canada leads at 49%. Authors explicitly call out US-state application as future work. Their weights are an input we should decide to adopt-or-not for the compendium.

- **Newmark 2017's cross-rubric correlation finding is load-bearing for project positioning.** Four state disclosure measures (CPI, PRI, Sunlight, Newmark) have near-zero correlation with each other — CPI ↔ PRI-disclosure r=0.04. Empirical proof that different rubrics measure different constructs. Justifies the compendium-first approach: we union them rather than pick one.

- **OpenSecrets 2022 is the nearest living competitor and covers only 19 states.** Verified via their API and Bulk Data sections: state lobbying data is NOT in their bulk-downloadable catalog (federal lobbying is; state campaign contributions via FollowTheMoney is). OpenSecrets' 2022 scorecard paper acknowledges they only cover states with "meaningful data available" — the other 31 are out of their operational reach. **The gap is specifically open-access + live + field-level state lobbying data.**

- **Sunlight Foundation's 2015 scorecard** was never updated; Sunlight shut down 2020. Named precedent for the sustainability problem the project claims to solve.

- **CPI "Hired Guns" 2007** is CPI's pre-PRI methodology (48 questions, 100 points, weighted by category). Same organization replaced it with PRI 2010 three years later — its evolution is informative. Enforcement (15 pts) and Revolving Door (2 pts) are categories PRI 2010 and FOCAL both exclude; Hired Guns' inclusion of them is a useful reminder that those exclusions are deliberate, not natural absences.

- **"Required" is state-specific, not measured against an external ideal.** Framework compendium tells us the universe of what various rubrics think ought to be required; the project's matrix reports what this state's statute actually requires. We catalog; we don't grade. Scholars do the grading, activists do the kvetching.

- **No Corda Rubric.** The existing rubrics remain internal scaffolding for legal review; public output is the matrix + bulk data, not a scored ranking.

- **Data model v1.0 unfrozen.** Five gaps surfaced: (1) availability axes absent, (2) framework traceability hardcoded to PRI+FOCAL, (3) no evidence-source tag, (4) no first-class CompendiumItem/MatrixCell models, (5) no per-state pipeline-capability model. Scoped as v1.1 on a new branch.

## Provisional findings

- **Project identity clarified.** Primary deliverable: live, bulk-downloadable, cross-state lobbying disclosure data (LobbyView-for-states analog filling the gap OpenSecrets' 19-state scorecard acknowledges). Companion: N × 50 × 2 matrix of Required × {Legally Available, Practically Available} derived from the compendium. Not a deliverable: rubric scores, compliance audits, enforcement work, a Corda rubric.

- **4-axis framing confirmed.** Required / Legally Available / Practically Available / (Compliance + Enforcement — out of scope but enabled by the project's data outputs for downstream consumers).

- **Pri-calibration's role stable but reframed.** Internal QA for LLM statute-reading reliability, not a public scoring output. Pilot work continues unchanged on the pri-calibration branch; the architectural reframing doesn't invalidate it.

- **Compendium is upstream of any unified rubric** and more durable as an artifact. Source-lineage columns preserve each framework's contribution; users (including us internally) can filter to whatever subset they want to score against.

- **"Real-time" framing in README.md overstates what's achievable** and should be softened to "up-to-date" (every few weeks is fine; faster has no real value given state filing cadences).

- **FOCAL + PRI cover direct-lobbying disclosure design well** but miss: FARA-style foreign lobbying, grassroots lobbying, procurement lobbying, below-threshold "shadow lobbying." The README should make the project's scope explicit to distinguish what's deliberately out-of-scope from what's overlooked.

- **PRI 2010 as "ground truth" is scoped to PRI's frame, not to "disclosure law quality" broadly.** Newmark 2017's r=0.04 vs. CPI means PRI captures one legitimate frame among several. The calibration pilot validates LLM reading-consistency-against-PRI, not "LLM reads statute correctly in some general sense." Worth stating in the README to avoid overclaiming.

## Decisions made

- **Compendium-first over unified-rubric-first.** The 20260421 rubric-unification plan is not abandoned, but its framing shifts from "produce a unified scoring instrument" to "produce a field compendium with framework-source lineage." Decision captured for the landscape report.

- **Frameworks to union in the compendium:** PRI 2010 (disclosure-law + accessibility), FOCAL 2024 verbatim, FOCAL 2026 operationalized, CPI Hired Guns 2007, Newmark 2005, Newmark 2017, Opheim 1991, Sunlight 2015, OpenSecrets 2022, federal LDA (field inventory from LD-1/LD-2/LD-203 + statute).

- **No Corda-branded rubric.** Catalog, don't grade. Scholars can grade using the matrix under their preferred rubric; we stay in the infrastructure lane.

- **Data model v1.0 unfrozen.** Five-gap v1.1 update scoped on new branch `data-model-v1.1`. Plan and TDD test suite committed; implementation deferred to next agent.

- **Framework traceability clean-break.** Drop `pri_item_id` / `focal_indicator_id` / `pri_item_ids` across `FieldRequirement`, `RegistrationRequirement`, `ReportingPartyRequirement`. Replace uniformly with `framework_references: list[FrameworkReference]`. Safe because no live v1.0 artifacts exist yet.

- **"Available" sub-dimensions co-located on `FieldRequirement`** for v1.1 pragmatism (matrix export joins them anyway). Future refactor possible if experience shows a cleaner split.

- **Landscape report deferred to fresh-context session.** Will use this convo + the 2026-04-21 handoff + the data-model-v1.1 plan as the input trio.

- **Next pri-calibration session unchanged by today's work.** Still: expand bundles per H1, re-retrieve, re-score, measure.

## Results / artifacts produced

- New branch `data-model-v1.1` cut from `main` at `2afe77f4`, three commits:
  - `5b0799f1` — `docs/active/data-model-v1.1/RESEARCH_LOG.md` seed
  - `2f9053ac` — `docs/active/data-model-v1.1/plans/20260422_v1.1_gap_closures.md` (25KB: gap analysis, code shapes, TDD handoff, migration notes)
  - `cb077a00` — `tests/test_models_v1_1.py` (25KB: ~55 tests across 8 classes, expected-red until implementation)
- This convo summary (you are reading it).
- Updated RESEARCH_LOG.md and STATUS.md entries on `pri-calibration` (separate commits).

## Open questions

**For the next pri-calibration session (unchanged from 2026-04-21):**

- `support_chapters` lists per pilot state (CA / TX / NY / WI / WY). Dan identified CA Gov Code §18 + §§82000-82056 for CA, TX Gov Code §311 for TX in prior session.
- Does `build_statute_subagent_brief` need a prompt update to flag primary vs. secondary statute roles?

**For the data-model-v1.1 implementation agent:**

- Should `RegistrationRequirement` also get an `evidence_source` field? (Plan recommends skip for v1.1.)
- Should `MatrixCell` live in `models/` or a separate `exports/` module? (Plan keeps it with `CompendiumItem` for colocation.)
- Granularity of `PortalTier` — wait for fellow-surfaced gaps before extending.

**For the landscape report's next author:**

- Report scope: fellow-facing landscape, one document, architecture + decisions log (no full literature positioning). Confirmed 2026-04-22.
- Include OpenSecrets, Sunlight, LobbyView as positioning reference points; CSG Book of the States as sustainability precedent.
- Three-axis framing → four-axis (Dan's refinement; "Available" splits into legal × practical).
- Explicit: we catalog, not grade; project is data infrastructure, not evaluator.
- "Up-to-date" not "real-time" in the README update.

**Strategic open questions (raised but not decided this session):**

- **OCDEP engagement strategy.** Is the "Campaign Finance Filings" OCDEP active, dormant, or abandoned? Our pydantic models may be the most developed draft of what that OCDEP should look like. Worth checking before engagement direction is decided. **Flagged for Dan to raise with fellows.**
- **Sustainability after the fellowship.** Options: civic-tech home (OpenStates, OpenSecrets, FollowTheMoney, Harvard Ash Center), independent open-source project, or accept 2026-snapshot-plus-code-for-revival. Left open in the plan; design for sustainability, sort out operationally later.

## Notes for the landscape report writer

Recommended structure (confirmed 2026-04-22):

1. Project identity — data infrastructure, not evaluation. LobbyView-for-states ambition. Companion: N × 50 × 2 matrix.
2. Four-axis framing — Required / Legally Available / Practically Available / (Compliance + Enforcement downstream). 2×2 typology of matrix cells and their remediation pathways.
3. Layer 1: data infrastructure — Popolo (base spec), Open Civic Data (extensions + OCDEPs; engagement strategy is an open question), spatula (scraping framework; Open States distribution channel decision is open). Our pydantic models are v1.0 accepted; v1.1 in progress on `data-model-v1.1` branch.
4. Layer 2: legal-review frameworks — PRI (ground-truth anchor despite being one frame among many; Newmark 2017 r=0.04 context); FOCAL 2024/2026 (academic modern framework, international benchmark via Lacy-Nichols 2025); CPI Hired Guns 2007; Newmark 2005/2017; Opheim 1991; Sunlight 2015; OpenSecrets 2022; LDA federal fields.
5. What we're explicitly not doing — Corda Rubric, ranking, compliance auditing, enforcement. How our output enables others to do these.
6. GAO-25-107523 as compliance-axis federal benchmark — 21% miss rate on covered-positions, 93-97% on core fields. Positioning: each jurisdiction's compliance with its own requirements, not cross-jurisdiction rubric-item comparison.
7. Positioning vs. adjacent infrastructure — OpenSecrets (19 states, federal-complete), FollowTheMoney (state campaign finance), Sunlight (shut down 2020), LobbyView (federal-only), CSG Book of the States (dropped lobbying section ~2005). Our niche: open + maintained + all-50-states + field-level.
8. Sustainability question — open.

Source material: this convo, `docs/active/pri-calibration/plans/20260421_rubric_unification_and_handoff.md` (for the prior architectural framing being superseded), `PAPER_SUMMARIES.md` entries for Hired Guns / Newmark 2005 / Newmark 2017 / Opheim / Lacy-Nichols 2025 / Sunlight / OpenSecrets / GAO / LaPira & Thomas / Bacik (LobbyView), `docs/active/data-model-v1.1/plans/20260422_v1.1_gap_closures.md`.
