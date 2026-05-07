# Multi-Rubric Extraction Harness — Implementation Plan

**Goal:** Evolve the statute-reading pipeline from "scorer that produces PRI sub-aggregate sums" into a **harness that produces correct, auditable disclosure-requirement extractions** for the `StateMasterRecord`. The harness's outputs are the load-bearing artifact; per-rubric scores (PRI 2010, Sunlight 2015, eventually CPI / Newmark) are calibration signals used to detect real extraction errors and to surface judgment-call zones.

**Originating conversation:** `docs/active/statute-retrieval/convos/20260429_retrieval_pipeline_design.md` (the kickoff session that built the two-pass retrieval pipeline) plus the 2026-04-29 prompt-iteration thread that:

- Bumped the scorer to opus-4-7 and added files-read enforcement (commit `fc644b5`).
- Surfaced the goal-vs-instrument confusion: "TX gap of -7 vs PRI" was being treated as an optimization target instead of a calibration signal.
- Discovered Sunlight 2015 per-state per-category scorecard data already in the repo (`papers/Sunlight_2015__state_lobbying_disclosure_scorecard_data.csv`) — a second human-rater dataset we hadn't been using.

**Confidence:** Medium. The reframe is high-confidence (the goal really is the StateMasterRecord, not PRI agreement). The implementation path is medium-confidence — three of the four phases below have well-scoped infrastructure work; phase 3 (the extraction-first refactor) is the most uncertain because it requires a new output schema that is rubric-agnostic.

**Branch:** `statute-retrieval` (continues the current work).

**What this plan supersedes:** The TX-A-series prompt-tuning question raised mid-session (whether to add a "within the regime's reach" rule to widen A-coverage). The reframe makes that question premature: we shouldn't tune for PRI agreement on one state until we know whether the gap survives multi-rubric triangulation. If PRI and Sunlight both rate TX higher than the harness reads it, the gap is real and worth investigating; if only PRI rates it higher, it's a PRI-2010 idiosyncrasy and we leave the harness alone.

---

## Why this exists

The pipeline currently produces a stamped CSV of per-rubric-item scores (PRI sub-aggregate values 0–7, etc.). This is the wrong primary output for three reasons:

1. **It's rubric-bound.** A `pri_disclosure_law/A_registration=4` value is meaningful only inside PRI's framing. Activists and journalists want to know "does TX require lobbyist phone numbers? what's the registration threshold?" — fact-level answers, not rubric-projected sums. The `StateMasterRecord` schema (built on the `data-model-v1.1` branch) explicitly carries `FieldRequirement` objects with `framework_references: list[FrameworkReference]` precisely so that the same underlying extraction can be projected onto multiple rubrics rather than being trapped in one.

2. **Single-rubric calibration is empirically weak validation.** Newmark 2017 found PRI vs CPI cross-rater r = 0.04 on the same 50 states. A scorer that calibrates perfectly to PRI alone could be overfitting PRI's idiosyncrasies — there's no way to tell from PRI agreement alone. The locked scorer prompt has been iterated 5+ times to chase PRI agreement on TX; some of those iterations may have made the scorer more accurate, others may have just made it more PRI-shaped. Without a second rubric we can't distinguish.

3. **The current calibration loop conflates two questions.** "Did the scorer correctly read the statute?" and "Did the scorer correctly project that reading onto PRI's specific framing?" are different questions. When PRI says A=7 and the scorer says A=4, we don't know whether the scorer mis-read the statute, mis-projected it onto PRI, or correctly read a statute that PRI's 2010 reviewer interpreted differently. The fix is to separate extraction from projection.

---

## Phase 1 — Sunlight 2015 correlation analysis (no new infra)

**Why first:** Lowest cost, highest information per hour. Tells us whether opus's PRI-totals already correlate with Sunlight's independent assessment at the state-aggregate level. If yes → the harness is reading the statute consistently with at least two human raters, and chasing the residual TX A-gap is unjustified. If no → we have a real diagnostic problem and Phase 2's rubric-scoring infrastructure becomes much more valuable.

**Inputs:** `papers/Sunlight_2015__state_lobbying_disclosure_scorecard_data.csv` (50 states × 5 categories + total + grade), opus-scored per-state PRI totals (currently CA/TX/OH).

**Outputs:**
- `results/20260430_sunlight_pri_correlation.md` — table of opus-PRI total vs Sunlight total for each scored state, plus Spearman rank correlation and brief interpretation.
- A documented decision: do Phase 2, or stop here.

**Steps:**

1. Read Sunlight's per-category schema and codebook (asterisks like `1*`, `-1^`, `0***` need a key). The codebook may be in `papers/text/` or referenced from the CSV; if not, read the Sunlight 2015 methodology paper (likely in `papers/`).
2. Map Sunlight's 5 categories to PRI's 5 sub-aggregates as best as the rubrics allow. Document the mapping in the results doc (some are clean — Sunlight's "Lobbyist Activity" ≈ PRI A-series; Sunlight's "Lobbyist Compensation" ≈ part of PRI E-series — others are not).
3. Compute Spearman correlation between {opus PRI total, opus PRI per-sub-aggregate} and {Sunlight total, Sunlight per-category} across the 3 calibrated states.
4. Compute the same correlation between published PRI 2010 totals and Sunlight 2015 totals across the same 3 states (the human-rater baseline).
5. Compare: if opus's correlation with Sunlight is in the same band as PRI's correlation with Sunlight, the harness is consistent with the multi-rubric human-rater landscape. If opus's correlation is dramatically lower, that's a real flag.

**Caveat:** N=3 states is too small for robust correlation inference. The result is suggestive, not statistical. To get a real correlation number we need Phase 4 (more states scored). Phase 1 is a directional sanity check.

**Done when:** Results doc shipped and a Phase-2 / stop-here decision is recorded in `RESEARCH_LOG.md`.

---

## Phase 2 — Sunlight 2015 as a second scoring rubric

**Why next (conditional on Phase 1 motivating it):** Direct Phase-7 work from the multi-rubric calibration plan in `docs/historical/pri-calibration/plans/20260422_multi_rubric_calibration.md`. Gives us a rubric the scorer can be projected onto in addition to PRI, so per-state extractions can be calibrated against two independent rater frameworks simultaneously.

**Inputs to transcribe:**

- **Sunlight rubric structure** — the 5 categories, what each measures, the −1/0/+1/+2 ordinal scale, what each asterisk modifier means. Source: Sunlight 2015 methodology document.
- **Per-state per-category scores** — already in `papers/Sunlight_2015__state_lobbying_disclosure_scorecard_data.csv`; just needs to be re-formatted into our reference-score loader's expected shape.

**Code changes:**

1. New rubric CSV at `data/rubrics/sunlight_2015_disclosure_law/items.csv` (or a similar path matching the existing rubric layout). Schema decision needed: do Sunlight categories map onto our `RubricItem` model directly, or do we need an `OrdinalRubricItem` variant for the ordinal-graded case? The existing model is binary/numeric/categorical; ordinal-with-modifiers is a new case.
2. New reference-score loader in `src/scoring/calibration.py` analogous to `load_pri_reference_scores` — reads the per-state Sunlight CSV and returns a `dict[USPS, SunlightSubAggregates]`.
3. Update `cmd_calibrate` to accept `--rubric sunlight_2015_disclosure_law` (plus any new sub-aggregate mapping for the report).
4. Scorer prompt variant: extract the rubric-specific sections of `src/scoring/scorer_prompt.md` into a parameterized template, with a Sunlight-shaped variant alongside the PRI one. This is the riskiest single piece — the current locked prompt has accumulated PRI-specific guidance (Rule 6's A-series and C-series sub-rules) and the parameterization needs to preserve the load-bearing parts while making the rubric framing swappable.
5. Tests: rubric loader, reference-score loader, calibrate command end-to-end with Sunlight rubric (mirroring the existing PRI tests).

**Calibration target:** none. The Sunlight scoring run produces a per-state Sunlight grade vector for each calibrated state; we compare to Sunlight's published per-state grades. The result is a *second* per-state agreement number. We don't tune the scorer to maximize Sunlight agreement either — we use the joint pattern (PRI agreement × Sunlight agreement) to identify real extraction errors vs judgment-call zones.

**Done when:** `calibrate --rubric sunlight_2015_disclosure_law --state-subset CA,TX,OH --run-id …` produces a report comparable in shape to the PRI calibration report, and the joint per-state PRI×Sunlight agreement table is in `results/`.

**Open question to resolve before starting:** is Sunlight's ordinal scale + asterisk-modifier structure a meaningful additional rubric, or is it too coarse / too different from PRI to give an independent signal? Phase 1 should answer this; if the correlation analysis already shows opus and Sunlight in the same band, full Phase 2 may not be worth the rubric-transcription cost.

---

## Phase 3 — Extraction-first refactor (the reframe phase)

**Why:** This is the architectural shift the doc reframe motivates. Currently the scorer's output is a list of per-rubric-item scores. The output we actually want is a list of **disclosure requirement extractions** (e.g., "TX requires registration of any person making expenditures ≥$200/quarter on direct communication; cite §305.003(a)(1)"; "TX requires lobbyists to disclose name and business address; phone optional; cite §305.005(f)(1)–(2)") that can then be *projected* onto whichever rubric is being calibrated.

**Confidence:** lower than Phases 1–2. This is a real schema design problem, not a parameter tweak. The `data-model-v1.1` `FieldRequirement` model is the candidate output shape — it carries `framework_references: list[FrameworkReference]` and availability axes — but bridging from "free-form statute reading" to "structured `FieldRequirement` instances" requires either (a) a constrained extraction prompt that emits `FieldRequirement` JSON directly, or (b) a two-pass approach where the scorer extracts facts and a second projector LLM converts facts into `FieldRequirement` plus per-rubric scores.

**Steps (sketch — refine in a brainstorm session before coding):**

1. **Spec the extraction schema.** Decide whether `FieldRequirement` from `lobby_analysis.models` is the right output shape, or whether we need a coarser intermediate "statute fact" model that `FieldRequirement` is derived from. Consider what activists/journalists would want to see (probably: a per-state YAML/JSON file with each disclosure requirement, citation, and which rubric items it would project to).
2. **Design the extraction prompt.** Take the locked scorer prompt's accumulated guidance (Rule 5 read-full-statute, Rule 6 partial-exemption-doesn't-mean-blanket) and re-express it for an extraction task rather than a scoring task. The agent's job becomes: read the statute → enumerate the disclosure requirements → cite each one → optionally tag which rubric items it satisfies.
3. **Define the projection step.** Given a list of extracted requirements + their citations, produce per-rubric scores deterministically (or via a small LLM call). This is where rubric-specific logic lives — and where rubric updates (PRI 2026, Sunlight, CPI) plug in without touching extraction.
4. **Validation:** run extraction on CA/TX/OH; project to PRI and Sunlight; compare projected scores to published. The goal is *not* better PRI agreement — it's that the same extraction produces calibrated agreement against multiple rubrics, *and* the extraction itself is human-readable.

**This phase is a brainstorm-then-plan task, not a "write the code now" task.** Before starting, run the brainstorming skill (`/Users/dan/.claude/skills/brainstorming/SKILL.md`) on the extraction schema specifically — there are several plausible shapes and we shouldn't pick one in haste.

**Done when:** there's a separate plan doc for Phase 3 (named something like `20260501_extraction_first_refactor.md`) with the schema decision, prompt approach, and integration plan with `StateMasterRecord` worked out.

---

## Phase 4 — Scale to more states

**Why last:** Until Phase 1–3 stabilize the harness, scaling to more states just produces more noise in the same pattern. Once the harness produces multi-rubric calibrated extractions, scaling is a matter of dispatching more retrieval+scoring runs and watching the calibration metrics hold.

**Inputs:** statute bundles for additional states. The `audit-statutes` subcommand already showed 49/50 states are eligible at ±2yr Justia tolerance (CO is the exclusion). The 5–8 priority states from the README scope is the natural next chunk; the ultimate goal is all 50 states annually.

**Steps:**

1. Pick the next batch (probably the rest of CPI Hired Guns 2007's responder set, or the Sunlight 2015 A/B-grade states, or a stratified sample across grades).
2. Run two-pass retrieval (`expand-bundle` → `ingest-crossrefs`) for each.
3. Run `calibrate-prepare-run` and dispatch opus-4-7 scorer subagents.
4. Project to all available rubrics (PRI, Sunlight, eventually CPI/Newmark).
5. Compute joint multi-rubric agreement; flag states where any rubric disagreement is large enough to merit per-state inspection.

**Done when:** harness produces calibrated extractions for the README's 5–8 priority states with documented multi-rubric agreement profiles.

---

## What we are NOT doing in this plan

- **Tuning the scorer prompt to chase PRI agreement on TX.** The 2026-04-29 thread iterated toward an "A-series within-the-regime's-reach" rule; we explicitly rejected that as too loose, and the reframe makes the question premature in any case. Don't reopen it without a multi-rubric signal that justifies it.
- **Building a "Corda Rubric."** STATUS.md's "Current Focus" already established the project catalogs disclosure requirements, doesn't grade. The harness produces extractions that *can be projected onto* any external rubric; it doesn't define one of its own.
- **Re-running existing scored states with new prompts.** The opus-4-7 + files-read-enforced runs at `data/scores/{CA,TX,OH}/statute/<vintage>/<run_id>/` are the current calibrated baseline; preserve them. New runs go in new run-id directories per the experiment-data-integrity rule.

## Reference

- Branch `RESEARCH_LOG.md` (Purpose) — the canonical framing this plan implements.
- `docs/historical/pri-calibration/plans/20260422_multi_rubric_calibration.md` — the original multi-rubric plan; Phases 6–9 there map roughly to Phase 2 here.
- `docs/historical/pri-calibration/results/20260419_pri_rollup_rule_spec.md` — PRI-specific sub-aggregate math; Sunlight will need its own rollup spec in Phase 2.
- `papers/Sunlight_2015__state_lobbying_disclosure_scorecard_data.csv` — the second-rubric data source.
- `src/lobby_analysis/models/state_master.py` (and the `data-model-v1.1` history) — the `FieldRequirement` shape that Phase 3's extraction step targets.
- `src/scoring/scorer_prompt.md` — the locked scorer prompt; current rules 5–7 are the hard-won guidance to preserve through any refactor.
