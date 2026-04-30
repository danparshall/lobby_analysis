# 2026-04-29: Retrieval Pipeline Design & Calibration

**Date:** 2026-04-29
**Branch:** statute-retrieval

## Summary

Long session covering the full arc from design through implementation through calibration. Built a two-pass statute retrieval pipeline (retrieval agent identifies cross-references in core lobbying chapters → orchestrator fetches support chapters → scoring agent scores the expanded bundle against PRI 2010 rubric). Ran multiple calibration rounds on OH, CA, and TX, iterating on the scorer prompt to improve agreement with PRI 2010 ground-truth disclosure-law scores.

The retrieval infrastructure works well — the retrieval agent reliably finds cross-references, the enriched manifest provides an audit trail, and the ingest pipeline deduplicates and fetches correctly. The remaining gaps are in scorer interpretation, particularly around how to read exemption clauses and how entity-type coverage interacts with activity-based registration triggers.

## Topics Explored
- Cleaned up merged worktrees (lobbying-data-model, scoring) and verified data safety
- Redesigned calibration subset: CA, TX, OH (dropped WY, kept WI URLs)
- Designed two-pass retrieval architecture (LLM-driven cross-reference discovery, 2-hop limit, enriched manifests)
- TDD implementation: Phase 1 (enriched StatuteArtifact model + loader + retriever), Phase 2 (retrieval agent prompt + brief builder + ingest_crossrefs + orchestrator subcommands)
- Ran retrieval agents on all 3 states: OH found 9 cross-refs, CA found 5, TX found 7
- Discovered Justia 404 gap for CA 2010 definitions chapter (§§82000-82054); used 2007 vintage as fallback
- Multiple scorer prompt iterations targeting A-series (registration coverage), C-series (public entity definition), and E-series (disclosure cascade)

## Provisional Findings

### Retrieval pipeline
- LLM-driven cross-reference discovery (approach C) works well. The retrieval agent consistently identifies relevant cross-references and constructs valid Justia URLs.
- OH: 9 cross-refs found (all URLs valid), 4 unresolvable (federal/constitutional — correct)
- CA: 5 cross-refs found, but 3 URLs returned 404s due to Justia vintage gap. Fallback to 2007 vintage resolved it.
- TX: 7 cross-refs found including the critical §311.005 "person" definition

### Scorer calibration (best results per state)

| Sub-aggregate | CA (run 3) | TX (run 4) | OH (run 4) |
|---|---|---|---|
| A_registration | 7/6 (+1) | 2/7 (-5) | 8/7 (+1) |
| B_gov_exemptions | 3/2 (+1) | 2/3 (-1) | 2/2 match |
| C_public_entity_def | 0/0 match | 0/0 match | 1/1 match |
| D_materiality | 1/1 match | 1/1 match | 0/1 (-1) |
| E_info_disclosed | 17/14 (+3) | 11/18 (-7) | 17/15 (+2) |

- **D matches 2/3 states** (was 3/3 before last prompt change — OH regressed)
- **C matches 3/3 states** — functional definition guidance works
- **CA and OH A-series within ±1** of PRI; TX A-series is -5, a harder problem
- **TX E-series has a cascade bug**: scorer reads §305.004(4) principal exemption as blanket, scores E1a=0, which zeros all 15 E1 items. PRI says TX E=18.

### Key scorer prompt insights
- "Read the full statute before scoring" is necessary but not sufficient for TX
- Exemption-narrowness guidance helps CA/OH but doesn't fix TX's interaction between two registration triggers (expenditure-based vs compensation-based)
- The scorer reads bottom-up (definition → who's included) but PRI reads top-down (trigger → who's exempt from the trigger). TX exposes this because its §305.003(a)(1) expenditure trigger is entity-agnostic even though its "person" definition is narrow.

## Decisions Made
- Two-pass architecture with enriched manifests (see plan doc)
- `expand-bundle` and `ingest-crossrefs` as separate orchestrator subcommands
- PRI 2010 scores as TDD-equivalent test suite
- Scorer prompt iterates on scorer interpretation, not retrieval (retrieval is working)
- Plan doc: `plans/20260429_two_pass_retrieval_agent.md`

## Results
- `results/20260429_calibration_comparison.md` — cross-state calibration results table

## Open Questions
1. **TX A-series**: How did PRI score A=7 when §305.002(8) "person" doesn't include government entities? Likely PRI read the expenditure trigger (§305.003(a)(1)) as entity-agnostic, covering government entities despite the narrow "person" definition. Scorer needs to reason about trigger-vs-entity interaction.
2. **TX E1 cascade**: §305.004(4) exempts principals whose *only* activity is compensating a lobbyist, but non-exempt principals must register under §305.005 and disclose under §305.006. Scorer treats the partial exemption as blanket. Multiple prompt fixes haven't resolved this.
3. **E over-scoring on CA/OH**: Consistently +2-3 on E across CA and OH. Without item-level PRI truth, can't pinpoint which items. May be PRI under-counting rather than pipeline error.
4. **Justia 404 handling**: CA 2010 definitions chapter not on Justia; used 2007 fallback. Pipeline needs systematic 404 detection and adjacent-vintage fallback logic.
5. **OH D regressed**: Was matching, now 0/1 after last prompt change. The "unable_to_evaluate" items may be related.

---

## Continuation, same day (afternoon): scorer model bump + reframe

### Topics explored

- **Identified scorer-model lever.** The cascade error and shallow statute reading were diagnosed as sonnet-4-6 prompt-following limits, not raw reasoning limits. Bumped `MODEL_VERSION` in `src/scoring/provenance.py` from `claude-sonnet-4-6` to `claude-opus-4-7`; also fixed a duplicated literal at `orchestrator.py:539` to reference the constant.
- **First opus run on TX disclosure-law (`529c711c1b4b`):** total 23/29 vs PRI's 29 — gap closed from sonnet's −13 to −6 in a single dispatch. Most consequential: A_registration jumped from 2/7 → 6/7 (opus reasoned about the §305.003(a)(1) entity-agnostic trigger × §305.002(8) narrow "person" definition interaction); E_info_disclosed went from 11/18 → 13/18 (E1 cascade no longer absolute). One regression: C_public_entity_def went 0/0 ✓ → 1/0 because opus correctly applied Rule 6's functional-definition guidance to TX's §305.003(b-1) "quasi-governmental agency" and §305.026(b) "political subdivision" definitions.
- **Narrowed Rule 6's C0 sub-rule.** TX's quasi-gov and political-subdivision definitions appear only in *exemption* and *fund-use* clauses, not in clauses scoping the disclosure obligation itself. Updated the locked prompt to count C0 = 1 only when the public-entity definition brings public entities INTO the disclosure obligation. Re-ran TX (`03db461b99e1`): C0 fixed (0/0 ✓), but A and E regressed sharply (16/29 total) — opus run 2 used 4 tool calls in 3 minutes vs run 1's 12 tool calls in 5.5 minutes, and explicitly invoked "E1 cascade is null/0" reasoning the locked prompt forbids. Diagnosis: dispatch variance. The locked-prompt rules can't enforce thorough reading; agent thoroughness is variable per dispatch.
- **Diagnosed why subagent thoroughness varies despite both being opus-4-7.** I (the orchestrating agent) read the statute carefully because of accumulated conversation context, direct stakes from the user, an interactive system prompt, and per-item dialogue. The dispatched subagent gets a one-shot brief + cold start, runs under a "general-purpose" system prompt optimized for tool economy, has no feedback loop, and is asked for all 61 items in one Write call. Same model, materially different operating conditions.
- **Added forcing function for thoroughness.** Modified `build_statute_subagent_brief` to require a sidecar `files_read.json` enumerating every statute file the subagent Read; added Rule 7 to the locked scorer prompt; modified `cmd_calibrate_finalize_run` to fail closed if `files_read.json` is missing or any bundle file is unread without explanation in the `notes` field. Updated `tests/test_orchestrator_calibrate_run.py` fixtures (one-line addition); 4 previously-failing tests went green.
- **Run 3 with enforcement (`1b5f1a140d47`):** 16 tool calls, 22/29 total (A=4, B=2, C=0✓, D=1✓, E=15). Files-read manifest enumerated 8 statute files with detailed notes for each (Education Code 61 for §61.003 institution-of-higher-ed, Election Code 251 for §251.001 political contribution, Penal Code 36 for §305.0021 cross-refs, Business & Commerce Code 3 for §305.024(a)(1)(B) negotiable-instrument, Government Code 572 for state-officer references, etc.).
- **Three more enforced runs in parallel:** TX run 2 (`4fe9774234f3`, 12 tool calls, 23/29), CA (`590e9123a624`, 9 tool calls, 29/23 — over PRI by 6), OH (`38803d49e32f`, 43 tool calls, 25/26 — matched within 1).
- **A-series gap analysis.** Per-item inspection of TX run 3 vs run 1 showed the 2-point variance collapsed to two specific items (A2 volunteer lobbyists, A3 principals who employ lobbyist) where opus made opposite calls about partial exemptions. Drafted a proposed prompt rule to codify run 1's looser reading ("the A-series question is whether the entity type is within the regime's reach, not whether every pathway leads to mandatory registration") — user pushed back. PRI item text is plain: "Governor's office." under "Who is required to register." The natural reading is institutional ("does the office have a registration obligation?"), not "could some pathway reach an individual." Withdrew the proposed rule; if anything Rule 6 may already be too permissive.
- **Surfaced Sunlight 2015 as second ground-truth dataset.** User pointed out we have an additional reference set we hadn't been using. Found `papers/Sunlight_2015__state_lobbying_disclosure_scorecard_data.csv` — 50 states × 5 categories + total + grade. Per-state ordering across rubrics: PRI and Sunlight independently rank TX > OH on lobbying disclosure substance (TX=29 PRI / 3 Sunlight; OH=26 PRI / −1 Sunlight). Opus ranks OH > TX (TX=22-23 / OH=25). Two unrelated human raters agreeing where our LLM disagrees is a real signal worth taking seriously.
- **Goal reframe.** User clarified: the project's real goal is "create a harness that can read state law and understand which disclosure requirements should be included" — feeding correct values into `StateMasterRecord` and providing inspectable extractions for activists/journalists. PRI and Sunlight are *calibration tools*, not output targets. Confirmed the docs were framing PRI as the optimization target (RESEARCH_LOG Purpose, plan Goal/Architecture, calibration_comparison title, STATUS Track A line). Updated all four to reflect: harness produces extractions; per-rubric scores are diagnostic; single-rubric matching is empirically weak validation (Newmark 2017 PRI vs CPI cross-rater r = 0.04).

### Provisional findings

**Scorer model + enforcement results (TX disclosure-law, opus-4-7 + files-read enforced, current calibration baseline):**

| Sub-aggregate | Sonnet best | Opus run 1 (no enforce) | Opus run 2 (no enforce) | Opus run 3 (enforced) | Opus run 4 (enforced) | PRI 2010 |
|---|---|---|---|---|---|---|
| A_registration | 2/7 | 6/7 | 3/7 | **4/7** | **5/7** | 7 |
| B_gov_exemptions | 2/3 | 2/3 | 2/3 | **2/3** | **2/3** | 3 |
| C_public_entity_def | 0/0 ✓ | 1/0 ✗ | 0/0 ✓ | **0/0 ✓** | **0/0 ✓** | 0 |
| D_materiality | 1/1 ✓ | 1/1 ✓ | 1/1 ✓ | **1/1 ✓** | **1/1 ✓** | 1 |
| E_info_disclosed | 11/18 | 13/18 | 10/18 | **15/18** | **15/18** | 18 |
| **Total** | **16/29** | **23/29** | **16/29** | **22/29** | **23/29** | **29** |
| tool_uses | — | 12 | 4 | 16 | 12 | — |

**Three-state apples-to-apples (opus-4-7 + enforcement, single run each, except TX which has two):**

| State | A | B | C | D | E | Total | vs PRI |
|---|---|---|---|---|---|---|---|
| TX run 1 | 4/7 | 2/3 | 0/0 ✓ | 1/1 ✓ | 15/18 | **22/29** | −7 |
| TX run 2 | 5/7 | 2/3 | 0/0 ✓ | 1/1 ✓ | 15/18 | **23/29** | −6 |
| CA | 6/6 ✓ | 4/2 | 1/0 | 1/1 ✓ | 17/14 | **29/23** | **+6** |
| OH | 8/7 | 2/2 ✓ | 1/1 ✓ | 1/1 ✓ | 13/15 | **25/26** | −1 |

Key observations:
- **Files-read enforcement collapsed dispatch variance** from ±7 points (TX runs 1 vs 2 unenforced) to ±1 point (TX runs 3 and 4 enforced). The forcing function changed agent behavior even before the orchestrator-side guard had to fire.
- **Gap structure is asymmetric across states.** TX is under PRI; CA is over PRI by the same magnitude; OH is matched. A "fix" tuned for TX would push CA and OH further off PRI. This is the signature of judgment-call-zone disagreements rather than systematic scorer error.
- **CA's C0 = 1/0 survived the Rule-6 narrowing** that fixed TX's C0. CA may have a coverage-side public-entity definition that legitimately scores 1, OR opus is finding another exemption-side definition the narrowed rule doesn't catch. Worth inspecting per-item.
- **PRI 2010 reviewer noted as load-bearing.** TX is a PRI 2010 responder; the published TX = 29 went through state review. The C0 = 0 from PRI represents TX's own reviewer agreeing with PRI's reading. We're not just contradicting PRI in the abstract; we're contradicting state review. (Same logic applies in reverse for the A=7 gap — PRI's 7 went through TX state review.)

### Decisions made

- **Pin scorer to opus-4-7** as the new baseline model. Stamp via `MODEL_VERSION` constant from `provenance.py`; never duplicate the literal.
- **Files-read enforcement is mandatory** for statute calibration runs. Brief writes the requirement, locked prompt explains it (Rule 7), orchestrator validates.
- **Narrow C0 (Rule 6) to coverage-side definitions only.** Definitions appearing only in exemption clauses or fund-use clauses score 0 even if functional.
- **Do not add the proposed "within-the-regime's-reach" A-series rule.** It would chase one specific PRI judgment at the cost of likely worsening CA/OH.
- **Reframe project docs**: harness produces `StateMasterRecord` extractions; PRI 2010 + Sunlight 2015 are multi-rubric calibration signals; single-rubric agreement is insufficient validation. Updated `RESEARCH_LOG.md` Purpose, `plans/20260429_two_pass_retrieval_agent.md` Goal+Architecture, `results/20260429_calibration_comparison.md` header, `STATUS.md` Track A line + branch row.
- **Preserve all existing scored runs as historical baselines.** New runs go in new run-id directories per the experiment-data-integrity rule. Opus runs are stamped `model_version="claude-opus-4-7"`; sonnet runs remain stamped `claude-sonnet-4-6`. Both sets are recoverable.

### Commits this session
- `fc644b5` — opus-4-7 bump + files-read enforcement + C0 narrowing + four-doc reframe
- `904b110` — new plan doc `20260429_multi_rubric_extraction_harness.md` with 4 phases

### Open questions (carried forward)

1. **CA C0 = 1/0 over-score.** Does CA have a coverage-side public-entity definition (rule working as intended), or is opus finding another exemption-side definition the narrowed rule doesn't catch? Inspect per-item before any further C0-rule changes.
2. **Sunlight correlation analysis (Phase 1 of the new plan doc).** Compute Spearman correlation between {opus PRI totals} and {Sunlight totals} across the 3 calibrated states; compare to the human PRI×Sunlight correlation. If opus tracks Sunlight in the same band as PRI does, the residual TX A-gap is unjustified to chase. N=3 is too small for robust inference but is a directional sanity check.
3. **Whether to do Phase 2 (Sunlight as second scoring rubric).** Conditional on Phase 1's signal. The rubric transcription + scorer-prompt parameterization is ~1-2 sessions of work; only justified if Phase 1 shows opus and Sunlight materially diverge.
4. **Phase 3 extraction-first refactor needs a brainstorm before coding.** The output schema (FieldRequirement-shaped? coarser intermediate "statute fact" model?) is an unsolved design question; should not pick in haste.
5. **Justia 404 detection** still unaddressed (carried from morning session). CA 2010 definitions returned 404; we used 2007 fallback manually. Should add adjacent-vintage fallback logic to `ingest_crossrefs`.
6. **OH C0 = 1/1 ✓** is correct under the narrowed rule, but worth one inspection to confirm OH genuinely has a coverage-side definition rather than just dispatch variance landing on the right answer for the wrong reason.

### Why this matters

The afternoon work changed the operating frame more than it changed the scorer. The scorer changes (opus + enforcement + narrowed C0) are real and load-bearing — they collapsed dispatch variance and produced a stable calibration baseline across three states. But the larger shift is recognizing that the harness's job is **producing extractions**, not matching any one rubric's scores. The prior session's iteration loop was shaped by the implicit assumption that closer PRI agreement = better scorer; that assumption is empirically broken (Newmark 2017's r=0.04 finding) and the doc reframe locks in the corrected framing for future fellows working this branch.
