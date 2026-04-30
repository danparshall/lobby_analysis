# Research Log: statute-retrieval
Created: 2026-04-29
Purpose: Build a harness that reads state lobbying law and produces correct, auditable disclosure-requirement extractions for the StateMasterRecord. The harness must scale to all 50 states annually without per-state hand-curation, and its outputs must be inspectable enough that activists and journalists can verify which disclosure obligations the law actually imposes.

PRI 2010 and Sunlight 2015 (and eventually CPI Hired Guns 2007, Newmark 2005/2017) serve as **multi-rubric calibration signals**, not optimization targets. We don't tune the harness to match any one rubric — single-rubric matching can mask a scorer that is overfit to one rater's quirks (Newmark 2017: PRI vs CPI cross-rater r = 0.04). Instead: where multiple independent rubrics concur and the harness disagrees, that is a real extraction error worth fixing; where rubrics disagree with each other (judgment-call zones), the harness's reading of the statute is the load-bearing artifact, and we don't chase any single rubric's score.

## Conversations

(newest first)

## Session: 2026-04-30 — 20260430_oh_2025_baseline_smr

### Topics Explored
- Executed `plans/20260430_oh_2026_baseline_smr.md` end-to-end. Source vintage was 2025 not 2026 — Justia tops out at 2025 for Ohio; user confirmed `(OH, 2025)` was fine for an April-2026 calibration baseline.
- Phase 1: live Justia probe via `PlaywrightClient` confirmed URL convention identical to 2010 (Justia redirects newer slug-based forms to legacy underscore form), section list intact 2010 → 2025. Added `("OH", 2025)` entry to `LOBBYING_STATUTE_URLS` (30 URLs, commit `ee4ffdd`). Retrieved 30 sections (~143 KB) — apples-to-apples with the OH 2010 core (140,828 B) confirms the corpus is essentially unchanged in size.
- Phase 2: 3 concurrent opus-4-7 scorer subagents per user request ("3 times for debugging"). All three scored 61 items, read all 30 statute files. Inter-run disagreement: 13 items, 21.3% (flagged at 11.5% threshold).
- Mid-session reframe (which interpretation is correct?): read §101.72 + §101.70(F) directly and reasoned through the disputed items. **No 2025 run is fully correct.** r1 reads qualitative materiality test correctly (§101.70(F) "main purposes") but over-scores conjunctive E-series; r2/r3 read E-series correctly but miss qualitative materiality. The 2010 baseline got both right. Picked r2 (`e7846593ebb5`) for SMR projection because it best matches 2010 conventions on disputed binary items (8/9 vs 2/9 for r1, 5/9 for r3) — for continuity, not legal correctness.
- Second reframe: **the rubric isn't the right product.** PRI asks diagnostic yes/no questions for cross-state comparison; an extraction pipeline needs a filing-field schema (filing types × required fields × cadence × triggers × cross-references). The compendium-keyed `field_requirements` row IS the right shape; the 22 fields populated by PRI projection are a thin slice of what OH's statute actually requires. User decision: don't pivot in this session — push the OH 2025 PRI-projection through as a parking-orbit MVP, then split future work into (1) filing-schema extraction harness, (2) parallel branch for pulling actual disclosure data.
- Phase 3: built SMR from r2. Phase 4: diffed vs OH 2010 SMR.

### Provisional Findings
- **OH disclosure law is structurally near-unchanged 2010 → 2025** as PRI projection sees it. Only one structured-data flip (`governors_office.required: False → True`); all 22 field_requirements identical, both reporting_parties identical, both de_minimis nulls (wrong in both years — known scorer blind spot on qualitative materiality).
- **Real text-level changes exist but don't move the rubric needle:** Ohio casino control commission added to "person"/"legislative agent" definitions in §101.70 (likely 2012). 8 procedural sections grew 15–60% (additions, not replacements). 12 sections ≥90% similar (housekeeping only).
- **Section-level apparent shrinkage in §101.70 / §121.60 (~45%) is a Justia hosting artifact** — 2010 page contained both pre-9/10/2010 and post-9/10/2010 versions of those definitions inline ("set out twice"); 2025 shows only current version.
- **OH was "the cleanest" state in the original 5-state calibration but inter-run rate jumped to 21% on 2025.** The disagreement is concentrated in known-broken zones (qualitative materiality, conjunctive E-series, C-series public-entity boundary) rather than spread evenly.

### Decisions Made
- **Source vintage = 2025** (Justia constraint, user confirmed for April-2026 calibration).
- **3 concurrent runs** at safe-batch-size of 4 (10 min wall-clock vs 5 min for single run; worth it for inter-run signal).
- **r2 (`e7846593ebb5`) for SMR projection** — 2010-convention continuity, not legal correctness. Diff doc explicitly flags this.
- **No more polishing on this branch.** PRI-projection MVP shipped; future work splits into two parallel branches.

### Results
- `results/20260430_oh_2025_vs_2010_diff.md` — first multi-vintage-same-state SMR comparison; structural-diff finding + scorer-drift signals + statute-text change summary (commit `ce10674`).

### Next Steps (forward signals, not acted on this session)
- Extraction-harness branch: filing-schema-first design. The qualitative materiality gate must be handled. r2's E-series accuracy and r1's D0 accuracy are signals for what each prompt iteration got right — preserve both behaviors in a unified scorer or schema-extractor.
- Disclosure-data branch: unblocked by the OH 2025 SMR existing as a downstream contract.
- Open question on `governors_office.required: False → True` flip — could be a real Ch. 121 legal change since 2010 OR scorer judgment drift; not investigated this pass.
- CA 2025 / TX 2025 baselines extend the same template; out of scope until extraction-harness branch is further along.

## Session: 2026-04-29 / 30 — 20260429_sunlight_pri_item_level_calibration

### Topics Explored
- Phase 1 of the multi-rubric extraction harness plan: Sunlight 2015 ↔ PRI 2010 calibration on the existing opus-4-7 + files-read-enforced harness runs (CA / TX / OH).
- Reframe mid-Phase-1: unit of analysis is the disclosure item, not state-level totals or rankings. PRI/Sunlight are independent human-rater datasets used to identify real extraction errors vs judgment-call zones.
- Sub-aggregate baseline recompiled with `rollup_disclosure_law`: CA 29/23 (+6), TX 23/29 (−6), OH 25/26 (−1). Replaces the morning's sonnet-run table.
- Sunlight category → PRI item decomposition (Activity ↔ E*g; ExpTrans ↔ E*f; Compensation ↔ E*f_i; Threshold = no clean PRI map; DocAccess = portal accessibility, out of scope).
- Joint per-item agreement table: 12/12 activity cells, 6/6 expenditure-itemization cells, 5/6 compensation cells match Sunlight across CA/TX/OH.
- Second reframe (post-Phase-1): the actual product is the `StateMasterRecord`, not per-rubric scores. OH calibration is "good enough" to ship; build a pipeline that produces SMRs so other fellows can use it on their states.
- Architectural redesign (2026-04-30, mid-session): user pushback on PRI-feeding-into-SMR direction. Correct architecture flips data flow — compendium is the universe; SMR is keyed to the compendium; PRI/Sunlight/etc. are *projections from* the SMR for calibration.
- Verified `CompendiumItem` and `MatrixCell` schemas exist (data-model-v1.1, 2026-04-22) but compendium has **never been populated**. No `data/compendium/` dir; no `CompendiumItem` instances anywhere.

### Provisional Findings
- On items where Sunlight and PRI cover the same ground (~13 of 61 PRI items), the harness reads CA/TX/OH consistently with both human raters. No extraction errors identified by joint signal.
- The headline opus-vs-PRI sub-aggregate gaps (TX A −2, CA B +2, CA C +1, E gaps) all live in items Sunlight is silent on. Single-rubric (PRI-only) signal too noisy to call those gaps extraction errors per Newmark r=0.04.
- OH is the cleanest of the three: Δ=−1 vs PRI total; every Sunlight overlap cell matches; harness correctly identified that OH does not require lobbyist compensation disclosure (Sunlight independently confirms).
- The OH `Threshold = −1` finding (under-$50 expenditures don't need itemization, per Sunlight methodology paragraph itself) is a real disclosure feature PRI's rubric has no slot for. Phase-3 compendium gap, not a harness bug.
- Sunlight's narrow item coverage (~13/61 PRI items, all in E-series) means it primarily provides redundant verification of PRI's E-series rather than independent signal in A/B/C/D zones. CPI Hired Guns 2007 / Newmark / OpenSecrets 2022 are the higher-leverage next-rubric integrations.
- Compendium population is the actually-load-bearing missing piece: schema is done; data isn't.

### Decisions Made
- **Skip Phase 2** of `plans/20260429_multi_rubric_extraction_harness.md` (Sunlight as a second scoring rubric — narrow item overlap doesn't justify duplicate scoring infrastructure).
- **OH harness output accepted as the calibration baseline.** Stop iterating prompt against TX A or CA B/C without joint-rubric signal supporting them as extraction errors.
- **Compendium is the universe.** SMR is keyed to compendium, not to any single rubric. PRI/Sunlight/etc. are projections from a populated SMR.
- **Plan doc:** `plans/20260430_compendium_population_and_smr_fill.md` — Stage A (populate compendium CSV from PRI disclosure-law + PRI accessibility + FOCAL + Sunlight unique items, ~140 atomic items after dedup); Stage B (temporary OH/CA/TX SMR fill via PRI-data projection through populated compendium); Stage C reference (MatrixCell projection layer + real statute-extraction harness, deferred to separate branches).
- **Earlier "Path 1 SMR projection MVP" plan abandoned** — rubric-shaped SMR was the wrong architecture per the user's correction.

### Results
- `results/20260429_sunlight_pri_item_level.md` — Phase 1 deliverable: full joint per-item table, Sunlight category decomposition, gap analysis, recommendation to skip Phase 2.

### Next Steps
- Stage A.1: pre-flight verify all 4 source CSV paths (especially `docs/historical/focal-extraction/results/focal_2024_indicators.csv`).
- Stage A: write compendium loader (TDD), then curate `data/compendium/disclosure_items.csv` — PRI disclosure-law spine first, then accessibility, then FOCAL refs, then Sunlight unique items.
- Stage B: populate `maps_to_state_master_field` on E-series compendium items, then TDD the `smr_projection` module + `cmd_build_smr` CLI.
- Targeted re-read of TX §305.006 to resolve the `E1f_i` / Sunlight `Compensation = 0***` ambiguity (background; doesn't block Stage A).

## Session: 2026-04-29 — 20260429_retrieval_pipeline_design

### Topics Explored
- Cleaned up merged worktrees/branches, verified data safety before removal
- Designed two-pass retrieval architecture (LLM-driven cross-reference discovery, 2-hop limit, enriched manifests)
- TDD implementation: Phase 1 (enriched StatuteArtifact model), Phase 2 (retrieval agent prompt, brief builder, ingest_crossrefs, orchestrator subcommands)
- Ran retrieval agents on CA (5 cross-refs), TX (7), OH (9) — all successfully identified relevant support chapters
- Discovered Justia 404 gap for CA 2010 definitions; used 2007 fallback
- Multiple scorer prompt iterations across 4 OH runs, 4 TX runs, 3 CA runs

### Provisional Findings
- Retrieval infrastructure works well — LLM-driven cross-reference discovery is reliable
- C_public_entity_def matches 3/3 states with functional-definition guidance
- D_materiality matches 2/3 states (OH regressed on latest prompt)
- CA and OH A-series within ±1 of PRI; TX A-series is -5 (different mechanism — narrow "person" def + entity-agnostic trigger)
- TX E-series has cascade bug: E1a=0 zeros all 15 E1 items. Single biggest scoring error.
- Scorer reads exemptions as broader than PRI does — the central prompt engineering challenge

### Results
- `results/20260429_calibration_comparison.md` — full cross-state calibration table with run histories

### Next Steps (morning, superseded by afternoon continuation)
- Fix TX E1 cascade (scorer must distinguish partial vs blanket principal exemption)
- Investigate TX A-series: scorer needs to reason about interaction between expenditure-based triggers and entity definitions
- Add Justia 404 detection + adjacent-vintage fallback to ingest_crossrefs
- Re-run OH with prompt that doesn't regress D
- Consider running all 3 states with the same prompt version for a clean comparison

### Continuation, same day (afternoon) — appended to same convo doc

- Bumped scorer to **claude-opus-4-7** (`provenance.py`); fixed duplicated literal in `orchestrator.py`.
- Diagnosed dispatch variance (opus subagent uses 4–43 tool calls per dispatch on the same statute) as the dominant noise source. Added **files-read enforcement**: brief requires sidecar `files_read.json`; locked prompt adds Rule 7; orchestrator fails closed if any bundle file is unread without explanation. Variance collapsed from ±7 to ±1 on TX total.
- **Narrowed Rule 6's C0 sub-rule**: public-entity definitions count only when they bring entities INTO the disclosure obligation, not when they appear in exemption or fund-use clauses. Fixed TX C0 over-score; CA C0 still 1/0 (open question).
- **Three-state apples-to-apples (opus + enforcement)**: TX 22–23/29 (−7/−6), CA 29/23 (+6), OH 25/26 (−1). Gap structure asymmetric — chasing TX agreement would worsen CA/OH.
- **Surfaced Sunlight 2015 as second ground-truth dataset** (`papers/Sunlight_2015__state_lobbying_disclosure_scorecard_data.csv`). PRI and Sunlight independently rank TX > OH; opus ranks OH > TX. Two unrelated human raters concurring is a real signal.
- **Goal reframe**: harness produces `StateMasterRecord` disclosure-requirement extractions; PRI/Sunlight are calibration signals, not optimization targets. Updated four docs (RESEARCH_LOG Purpose, plan Goal/Architecture, calibration_comparison header, STATUS Track A line + branch row). Justification: Newmark 2017 PRI vs CPI cross-rater r = 0.04.
- **Withdrew the proposed "within-the-regime's-reach" A-series rule** after user pushback. PRI item text reads institutionally; the proposed rule would have inflated scores on weakly-grounded reasoning.
- **Commits**: `fc644b5` (scorer changes + doc reframe), `904b110` (multi-rubric-extraction-harness plan).

### Carried-forward open questions
1. CA C0 = 1/0 over-score — coverage-side definition or another exemption-side one to narrow Rule 6 against?
2. Sunlight correlation analysis (Phase 1 of new plan) — does opus track Sunlight in the same band as PRI does?
3. Phase 3 extraction-first refactor needs a brainstorm before coding.
4. Justia 404 detection + adjacent-vintage fallback (still unaddressed).
5. OH C0 = 1/1 ✓ — confirm genuinely correct vs lucky dispatch variance.

## Plans

(newest first)

- **20260430_oh_2026_baseline_smr** — Re-run the Stage B SMR pipeline (URL list → retrieval → calibrate → build-smr) against the 2026-vintage OH lobbying statute. Executed end-to-end 2026-04-30 against actual Justia source vintage 2025 (no 2026 hosted yet). Diff vs OH 2010 baseline produced as `results/20260430_oh_2025_vs_2010_diff.md`. Originated from `convos/20260429_sunlight_pri_item_level_calibration.md` end-of-session.
- **20260430_compendium_population_and_smr_fill** — Stage A populated the compendium (118 rows from PRI disclosure ∪ PRI accessibility ∪ FOCAL ∪ Sunlight unique). Stage B added `compendium_loader`, `smr_projection`, `cmd_build_smr`. Executed for OH 2010 baseline and OH 2025 baseline. Stage C (MatrixCell projection + statute-extraction harness) deferred to separate branches.
- **20260429_multi_rubric_extraction_harness** — Reframe of harness goal: produce `StateMasterRecord` disclosure-requirement extractions, calibrated multi-rubric (PRI 2010 + Sunlight 2015 + planned CPI/Newmark). Phase 1: Sunlight correlation analysis (no new infra). Phase 2: Sunlight as second scoring rubric (skipped). Phase 3: extraction-first refactor (brainstorm-needed). Phase 4: scale to README's 5–8 priority states. Originated from the 2026-04-29 prompt-iteration thread that surfaced the goal-vs-instrument confusion.
- **20260429_two_pass_retrieval_agent** — Two-pass pipeline: retrieval agent follows cross-references (2-hop, LLM-driven), enriched manifests, PRI 2010 as test suite. OH first. Originated from `convos/20260429_retrieval_pipeline_design.md`.
