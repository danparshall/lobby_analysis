# 20260429 — Sunlight 2015 / PRI 2010 Joint Item-Level Calibration → SMR Pivot

**Date:** 2026-04-29 (evening session, follows the morning/afternoon `20260429_retrieval_pipeline_design.md` convo)
**Branch:** statute-retrieval

## Summary

Started this session executing Phase 1 of `plans/20260429_multi_rubric_extraction_harness.md` — a Sunlight 2015 vs PRI 2010 correlation analysis on the existing opus-4-7 + files-read-enforced harness runs for CA / TX / OH. Two reframings landed mid-session that materially changed the work.

**First reframe (mid-Phase-1):** the unit of analysis isn't state-level totals or rankings, it's the disclosure *item*. The harness's job is to decide, for each of ~120 union compendium items, whether the state's law requires it. PRI and Sunlight aren't optimization targets or even ranking benchmarks — they're independent human-rater datasets used to identify real extraction errors (where multiple rubrics concur against the harness) vs judgment-call zones (where rubrics disagree with each other). The original "Spearman correlation on N=3" framing was wrong because it treated states as the unit; the joint per-item agreement structure is what actually informs whether the harness is reading statutes correctly.

**Second reframe (post-Phase-1):** the actual product is the `StateMasterRecord`, and the per-rubric score CSVs are an instrument, not the deliverable. OH calibration is "good enough" to ship — opus matches PRI within 1 point and matches Sunlight on every overlap cell — and the next priority is building a pipeline that produces SMRs so the other fellows can run it for their states. Phase 2 of the multi-rubric plan (Sunlight as a second scoring rubric) is being skipped because Sunlight's coverage of statutory disclosure-law items is too narrow (~13 of 61 PRI items) to justify duplicating the scoring infrastructure. The signal Phase 1 extracted via overlay analysis is sufficient.

## Topics Explored

- Reread Sunlight 2015 methodology (`papers/text/Sunlight_2015__state_lobbying_disclosure_scorecard.txt`) — five categories with explicit ordinal scales documented; asterisk modifiers in the per-state CSV not defined in the methodology document.
- Decomposed Sunlight categories into PRI item overlaps:
  - **Lobbyist Activity** ↔ E1g_i/ii, E2g_i/ii (4 items)
  - **Expenditure Transparency** ↔ E*f_i/ii/iii/iv (8 items)
  - **Lobbyist Compensation** ↔ E1f_i, E2f_i (2 items, subset of the above)
  - **Expenditure Reporting Thresholds** — no clean PRI mapping (Sunlight asks about expenditure-itemization threshold; PRI's D1 is a registration threshold)
  - **Document Accessibility** — out of scope (portal accessibility, not statutory disclosure)
- Computed corrected sub-aggregate baselines from the latest opus-4-7 runs using `rollup_disclosure_law` from `src/scoring/calibration.py`: CA 29/23 (+6), TX 23/29 (−6), OH 25/26 (−1). Matches the RESEARCH_LOG afternoon entry; the morning's `calibration_comparison.md` table was sonnet runs and is now superseded.
- Built the joint per-item agreement table: 12/12 activity cells match Sunlight; 6/6 expenditure-itemization cells match (binary level); 5/6 compensation cells match. The one ambiguity is TX `E1f_i` (principal-side compensation) where Sunlight has `0***` and opus has `0`.
- Read `src/lobby_analysis/models/state_master.py` to confirm the `StateMasterRecord` schema. Confirmed no populated SMR instances exist for any state; the harness's only output today is the per-item PRI score CSV.
- Discussed three implementation paths for the SMR pipeline (project-from-PRI, re-extract-from-statute, hybrid). User selected Path 1 (project-from-PRI MVP).

## Provisional Findings

- On items where Sunlight and PRI cover the same ground, the harness is reading CA/TX/OH statutes consistently with both human raters. No extraction errors are identified by the joint signal in those items.
- The headline opus-vs-PRI sub-aggregate gaps (TX A −2, CA B +2, CA C +1, E gaps for all states) all live in items Sunlight is silent on. Single-rubric (PRI-only) signal is too noisy to call those gaps extraction errors per the Newmark 2017 r=0.04 cross-rubric finding.
- OH is the cleanest of the three states: Δ=−1 vs PRI total, every Sunlight overlap cell matches, and the harness correctly identified that OH does not require lobbyist compensation disclosure (Sunlight independently confirms `Compensation = −1`).
- The OH `Threshold = −1` finding (OH lobbyists need not include expenditures under $50, per the Sunlight methodology paragraph itself) is a real disclosure feature that PRI's rubric has no slot for. The harness's `D1_present = 0` is correctly answering PRI's narrower question (no *registration* threshold) but doesn't surface the *expenditure-itemization* threshold that exists in OH law. This is a Phase-3 compendium gap, not a harness bug.
- Sunlight's narrow item coverage (13/61 PRI items, all in E-series) means that as a calibration instrument, it primarily provides redundant verification of PRI's E-series rather than independent signal in A/B/C/D zones. CPI Hired Guns 2007, Newmark, or OpenSecrets 2022 are the higher-leverage next-rubric integrations.

## Decisions Made

- **Phase 1 = done.** Result doc shipped. Decision recorded: skip Phase 2 (Sunlight as a second scoring rubric — narrow item overlap doesn't justify duplicate scoring infrastructure).
- **OH harness output is accepted as the calibration baseline** for the SMR pipeline MVP. We are not re-tuning the prompt against TX A or CA B/C without joint-rubric signal supporting those as extraction errors.
- **The other fellows are the immediate users** of the SMR pipeline. The activist/journalist consumption layer comes later, after the MVP is working for the calibrated states + ready for the Track A scale-out.

## Architectural Redesign (later in session, 2026-04-30)

The first SMR plan I drafted ("Path 1 SMR projection MVP") had PRI feeding *into* the SMR — which would make the SMR rubric-shaped and structurally locked to PRI's framing. User pushed back hard:

> "We're supposed to have a 'universe' of possible disclosure items, which is the union of ALL the scoring systems we have documented. We shouldn't extract from PRI to populate the SMR; we should use data from a populated SMR *in order* to check our SMR results against PRI, Sunshine, etc. The only thing that was special about PRI was that we happened to find it first!"

The right architecture flips the data flow: **the compendium is the universe** (union of disclosure items across all rubrics, ~140 atomic items per the 2026-04-22 landscape framing). The SMR is keyed to the compendium, not to any one rubric. PRI/Sunlight/CPI/etc. are projections you compute *from* a populated SMR for calibration purposes. The data-model-v1.1 schema (`CompendiumItem`, `MatrixCell`, generic `FrameworkReference`, `framework_references: list[...]` on `FieldRequirement`) was designed for exactly this flow but had not been used that way.

User also clarified: the compendium has two domains tracked together — **disclosure** (statute-derived) and **accessibility** (portal-derived). The schema already encodes this via the per-item `domain` literal that includes both `"accessibility"` and the disclosure-side domains (`"registration"`, `"reporting"`, etc.).

Verified during this redesign: `CompendiumItem` schema exists (`src/lobby_analysis/models/compendium.py:43`); `MatrixCell` exists (`compendium.py:76`); tests cover the schemas (`tests/test_models_v1_1.py`); but the compendium has **never been populated** — no `data/compendium/` directory, no `CompendiumItem` instances in any data file, no `MatrixCell` instances. Schema only.

## Decisions Made (continued)

- **Compendium population is the load-bearing missing piece.** Without populated compendium items, neither SMRs nor the N×50×2 matrix can exist. Stage A of the new plan does this curation work.
- **Temporary PRI-data SMR fill is OK as a stand-in** for the real (statute-extraction) data source — but only because the compendium-keyed output shape locks in the long-term architecture. The data source is replaceable; the structure isn't.
- **Plan doc (replaces the abandoned Path 1 plan):** `plans/20260430_compendium_population_and_smr_fill.md` — three stages (A: populate compendium; B: temporary SMR fill via PRI projection through compendium; C: deferred reference to MatrixCell layer + real statute-extraction harness).

## Results

- `results/20260429_sunlight_pri_item_level.md` — Phase 1 deliverable: full joint per-item table, Sunlight category decomposition, gap analysis, and recommendation to skip Phase 2.

## Open Questions

- TX `E1f_i = 0` vs Sunlight `Compensation = 0***` — worth a targeted statute re-read of TX §305.006 to see if opus is correct that principal-side compensation isn't required, or if the asterisks indicate something opus missed.
- For SMR projection: do we emit `FieldRequirement` rows with `status="not_applicable"` for PRI score=0 items, or only emit `status="required"` rows? Plan resolves this as "emit not_applicable too — Track B downstream needs the negative signal." Confirm with user when the first OH SMR JSON ships.
- Where do PRI B-series and C-series items land in the SMR? They have no direct schema slot in `StateMasterRecord`. Plan routes them to free-text `notes` for MVP. Revisit when CPI/Newmark add coverage and the schema may need a `government_exemptions` field.
- What's the sensible `version` string for the SMR? Plan proposes `"pri-2010-baseline-{run_id_short}"` for Stage B's temporary fills; revisit when Stage C statute-extraction harness ships.
- Do the other fellows need a one-command CLI or a multi-step recipe? Plan defaults to projection-only `build-smr` (assumes score CSV exists). Revisit if fellow feedback indicates a chained command is needed.
- **Curation judgment calls in the compendium 4-way union** (PRI atomic items vs FOCAL coarser indicators): does FOCAL pointing at multiple atomic items (rather than one super-item) capture the relationship correctly? Worth a second-pass review by another fellow once the curation is complete.
