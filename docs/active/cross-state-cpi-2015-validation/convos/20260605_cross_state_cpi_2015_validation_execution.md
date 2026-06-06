# 2026-06-05 — Cross-state CPI 2015 C11 de-jure validation execution: 5 states × default-6-chunks × per-(state, indicator) exact-match; 15/30 match (50%); 60% of misses are systematic vocab-mismatches (projection-helper-vs-YAML divergence), not extraction failures

**Plan:** [`../../../historical/wi-ralph-cpi-renewal-cadence/plans/20260605_cross_state_cpi_2015_validation.md`](../../../historical/wi-ralph-cpi-renewal-cadence/plans/20260605_cross_state_cpi_2015_validation.md) (amended 2026-06-05)
**Originating convos (on wi-ralph):**
- [`../../../historical/wi-ralph-cpi-renewal-cadence/convos/20260605_cross_state_planning.md`](../../../historical/wi-ralph-cpi-renewal-cadence/convos/20260605_cross_state_planning.md) — original 10-state planning
- [`../../../historical/wi-ralph-cpi-renewal-cadence/convos/20260605_pr40_pressure_test.md`](../../../historical/wi-ralph-cpi-renewal-cadence/convos/20260605_pr40_pressure_test.md) — amendment to 5-state × default-6 × per-cell-exact-match
- [`../../../historical/wi-ralph-cpi-renewal-cadence/convos/20260605_phase_a_execution.md`](../../../historical/wi-ralph-cpi-renewal-cadence/convos/20260605_phase_a_execution.md) — Phase A execution baseline
**Audit results (data):** [`../results/20260605_cross_state_cpi_2015_validation.md`](../results/20260605_cross_state_cpi_2015_validation.md)
**Failure-mode trends + paths forward (analysis):** [`../results/20260606_failure_mode_trends_and_paths_forward.md`](../results/20260606_failure_mode_trends_and_paths_forward.md) — six trends synthesized from the audit; two contrasting paths forward (remediate first vs broaden first); my recommendation is Path 2 modified (dispatch the 5 deferred states at vintage 2015 before remediating).
**Audit script:** [`/scripts/cross_state_cpi_2015_audit.py`](../../../../scripts/cross_state_cpi_2015_audit.py)

## Pre-flight

This was a fresh execution session per the Nori plan-then-fresh-session pattern. Branch `cross-state-cpi-2015-validation` cut off main at `f97c73d` (PR 40 merge — v2.1 + Phase A YAML additives + cross-state plan landed). Pre-execution checklist steps 1-6 verified before any TDD or dispatch: read plan + amendment, both planning convos, Phase A execution convo, CPI 2015 projection mapping doc, `src/lobby_analysis/projections/cpi_2015_c11.py`; verified P1 (v2.1 on main), P2 (worktree + symlinks), P3 (`_DEFAULT_CHUNKS` 1:1 with de-jure indicators), P4 (oracle CSV present).

## What happened (chronological)

1. **Branch skeleton + dispatcher TDD (commit `169c553`, `6a5da30`).** Cut worktree off main with `data → /Users/dan/data/lobby_analysis` + `.env.local` symlinks. Seeded `docs/active/cross-state-cpi-2015-validation/` (RESEARCH_LOG + convos/plans/results dirs). Added `--results-base` CLI flag to `scripts/tier_1_direct_read_legal_axis.py` under TDD (RED: 3 failed on unrecognized arg → GREEN: 14/14 pass on tier_1 tests, no regression). The dispatcher's `_DEFAULT_RESULTS_BASE` was hardcoded to the now-archived `wi-tier1-direct-read` results path; the flag lets cross-state results land under the new branch's `docs/active/` cleanly.

2. **NY dispatch as cost anchor (commit `280be17`).** Dispatched NY 2015 default-6-chunks with `--results-base docs/active/cross-state-cpi-2015-validation/results/tier_1` and `--env-file .env.local`. **36/36 dispatched / $2.8289 / σ_noise Claude 90.48% / GPT 88.10%.** Cost EXCEEDED the $2.50 pause-and-surface threshold by $0.33 (13%). Per plan §Stage X1 caveat, paused and surfaced to Dan.

3. **Budget decision (Dan, via AskUserQuestion).** Surfaced 4 options (expand envelope / drop a state / drop a model / stop at NY). Dan picked **expand envelope to ~$15 to finish all 5** — preserves the amendment design intent (full 5-state cross-state validation).

4. **Parallel dispatch of WI/OH/CA/TX (commits `282097b`, `ccf2cc3`, `6e0cbab`).** 4 background subprocesses in parallel — each writes to its own state-keyed dir, no collision risk. All 4 landed cleanly:

   | State | $ | σ Claude | σ GPT | inst. errors |
   |---|---:|---:|---:|---:|
   | NY  | $2.8289 | 90.48% | 88.10% | 2 |
   | WI  | $2.4825 | 84.52% | 88.10% | 6 |
   | OH  | $3.7894 | 92.86% | 86.90% | 0 |
   | CA  | $2.8428 | 78.57% | 86.90% | 1 |
   | TX  | $2.4835 | 73.81% | 60.71% | 3 |
   | **Total** | **$14.4271** | | | **12** |

   Total fit within the $15 expanded envelope by $0.57. TX's low σ_noise (Claude 73.8% / GPT 60.7%) is correlated with TX having only 1 statute file in the bundle (`government-code-title-3-subtitle-a-chapter-305.txt`) — sparse corpus pushes models toward "unscoreable" more often (TX's GPT has 27 scor_unstable cells vs e.g. NY's 4).

5. **Audit script (commit `7578c89`).** `scripts/cross_state_cpi_2015_audit.py`: walks results/tier_1/<STATE>_2015/, aggregates per-cell across 6 runs (2 models × 3 runs) with stability classification (stable / value_unstable / scor_unstable / incomplete) → majority value, builds `cells: dict[row_id, dict["legal_availability", value]]` for projection-helper consumption, applies the 6 de-jure helpers, compares per-(state, indicator) to the published oracle (loaded via `cpi_2015_c11.load_per_state_ground_truth()`), emits markdown with Table A (30 verdicts + 1-sentence diagnosis on each miss) + Table B (5 per-state summaries).

   **Two schema bridges across the dispatch→projection boundary:**
   - **Axis name short→long:** dispatcher emits `axis="legal"` on `cell_id`; projection helpers read `cells[row_id]["legal_availability"]` (v1.1 MatrixCell field). Rename in `_build_cells_dict`.
   - **State name abbrev→full:** dispatcher keys results by 2-letter abbrev (`NY`); oracle CSV uses full names (`New York`). Map via `_STATE_ABBR_TO_NAME`.

   Both bridges surfaced as bugs during the NY-only smoke run; fixed before the final 5-state audit.

6. **Final audit at `results/20260605_cross_state_cpi_2015_validation.md`.** 15/30 match across 5 states × 6 indicators.

## Findings (load-bearing)

### 1. Headline: 15/30 (50%) match — 60% of misses are projection-side vocabulary mismatches, not extraction failures

| Indicator | Match / 5 | Failure mode |
|---|---:|---|
| IND_196 (def recognizes exec branch) | **5 / 5** | clean cross-state — best signal |
| IND_197 (anyone paid is lobbyist) | 3 / 5 | WI + OH project YES from $0 threshold; oracle MODERATE (known IND_197 errata candidate per wi-tier1 Phase 2) |
| IND_199 (annual registration) | 1 / 5 | systematic vocab-mismatch: extracted IntCell(months) vs helper string enum (TX matches only because TX=0 → NO works by coincidence) |
| IND_201 (lobbyist spending report compound) | 2 / 5 | mix of value_unstable cells (OH, CA) + TX over-projection |
| IND_203 (principal spending report compound) | 4 / 5 | strong; only OH misses |
| IND_207 (audit in law) | **0 / 5** | systematic vocab-mismatch: extracted `YES`/`MODERATE`/`NO` vs helper structural enum |

**Vocab-mismatch misses: 9 of 15 (60%).** Concretely:
- `IND_199`: extracted as `IntCell` (months: NY=24, WI=24, OH=24, CA=24, TX=12); helper `project_ind_199` expects string enum (`"annual"`, `"biennial"`, etc.).
- `IND_207`: extracted as `EnumCell` with values from the CPI rubric's own vocabulary (`YES`/`MODERATE`/`NO`, as set up by Phase A's hand-craft for `_audit_required_in_law`); helper `project_ind_207` expects internal structural names (`"regular_third_party_audit_required"`, etc.).

The extraction is **factually correct** in both cases (e.g., TX's 12-month renewal cadence is materially correct; NY's "YES" on audits captures the third-party audit requirement). The mismatch is between the YAML's chosen extraction vocabulary and the projection helper's expected vocabulary.

Per plan §P3: *"if the projection mapping doc disagrees with what the helpers actually read, the helpers are the source of truth for this validation round — surface the discrepancy to Dan, don't silently re-key."* Surfacing here.

### 2. IND_196 is the cleanest cross-state signal — 5/5 across the heterogeneous state set

NY, WI, OH, CA, TX all extracted `def_target_legislative_branch=True` AND `def_target_governors_office=True`, projecting cleanly to 100 (YES) and matching oracle. Across 5 statute corpora ranging from TX's 1-file sparse bundle to NY's multi-file ample bundle, this 2-row Boolean composition is robust.

### 3. WI IND_197 reproduces the wi-tier1 Phase 2 errata candidate

WI extracted `lobbyist_registration_threshold_compensation_dollars=0` (matching WI §13.62(11)'s "any economic consideration" language). Helper logic: `threshold == 0 → 100 (YES)`. Oracle: MODERATE (50). **This is the same IND_197 errata candidate documented in the wi-tier1 Phase 2 findings** — CPI scored WI as MODERATE despite WI's statute having no compensation minimum. The extraction is structurally correct; CPI may have applied a non-statutory MODERATE.

OH shows the same pattern: extracted threshold=0 (scor_unstable; models flip between 0 and unscoreable), projected 100, oracle 50. Either the same statutory pattern as WI, or extraction over-projection on a scor_unstable cell.

### 4. OH is the worst state at 1/6 — but most OH misses are vocab-mismatch + value_unstable, not extraction failure

OH instantiation errors: 0 (perfect). σ_noise Claude 92.86% (highest of the 5 states). But OH IND_201 (lobbyist spending report compound) has 2 of 3 input cells value_unstable, and IND_203 (principal spending report) extracted as `principal_spending_report_required=False` — OH may genuinely have a different statutory regime that the helper's compound logic mishandles. The OH 2015 statute corpus is the largest of the 5 and the highest-cost ($3.79); the model is confident but the projection compounding doesn't capture OH's statutory shape.

### 5. TX low σ_noise correlates with sparse statute corpus

TX 2015 has only 1 statute file (`government-code-title-3-subtitle-a-chapter-305.txt`); other states have multi-file bundles. TX σ_noise: Claude 73.81% (15 scor_unstable cells), GPT 60.71% (27 scor_unstable cells). Models are flipping between "scoreable" and "unscoreable" on cells where the statute text simply doesn't cover the question. **The dispatch IS detecting the corpus sparseness correctly.** Despite this, TX matches 4 of 6 indicators — the sparse corpus answers the de-jure questions where it does cover them.

### 6. Cost extrapolation caveat from the plan was right to flag variance

Plan §Cost projection: *"$8 expected... expect variance of ±$2."* Actual: $14.43 (~80% over the $8 expected). NY+CA+OH each landed at $2.8–$3.8; WI+TX at $2.5. The variance is per-chunk-volume driven (statute text input dominates cost; large-corpus states cost ~50% more than small-corpus states). The $10 envelope was structurally tight; the $15 expanded envelope was the right call.

### 7. Architecture validated end-to-end

- **Dispatcher generalizes cross-state** with the `--results-base` CLI override + the existing `--state` / `--vintage` parameterization. 5 parallel state dispatches landed cleanly with no collision (state-keyed result dirs).
- **`resolve_results_dir(results_base=)` kwarg pre-existing from wi-tier1** is what made the cross-state extension a 2-line GREEN change after 1 RED test — that's the value of carrying through clean abstractions across branches.
- **Audit machinery (single audit script + projection helpers + oracle CSV)** runs in <1s, with provenance for every projected value. The per-cell diagnosis catches vocab-mismatches and value_unstable separately, so debugging signals point to the right layer (projection vs extraction vs sigma).

## Decisions confirmed mid-session

1. **Budget expansion to ~$15 (Dan, via AskUserQuestion).** NY's $2.83 vs $2.50 threshold projection meant the $10 envelope would bust by $3-4. Dan chose "expand to ~$15, finish all 5" — preserves the amendment design intent (full cross-state signal). Actual landed at $14.43, fitting the expanded envelope.

## Open questions surfaced this session

### #1 — How to remediate the vocab-mismatch on IND_199 + IND_207 (9 of 15 misses)

Two options:
- **(a) Update projection helpers to read CPI's published vocabulary (`YES`/`MODERATE`/`NO`).** Small change in `cpi_2015_c11.py`: helpers consume the strings the YAML extraction emits. Cleaner if all 9-rubric projections converge on CPI's vocab; otherwise multiplies into per-rubric helper changes.
- **(b) Update YAML enum/cell-type domains to use the helpers' structural names** (`"annual"`, `"biennial"`, `"regular_third_party_audit_required"`, etc.). Larger change — touches the YAML source-quote design and the cell-type schema (`renewal_cadence` is currently IntCell, would need to become EnumCell with months-to-tier mapping).

Recommendation: **(a) is the smaller surgical change** that lets this validation round close. (b) is a longer-term v2.2 schema design question that should accompany the broader compendium 2.0 typed-cell migration.

### #2 — Is OH IND_203's `principal_spending_report_required=False` a real OH-specific statutory pattern, or a missed extraction?

OH oracle = 50 (MODERATE); extraction = principal_required=False → projection = 0. OH 2015 may genuinely not require principal-side spending reports as the rubric reads them. Needs row-level Ralph on OH to disambiguate, OR cross-check against OH portal data (Track B).

### #3 — Is TX IND_201's over-projection (YES vs MODERATE) extraction or oracle?

TX extracted all 3 lobbyist_spending_report cells as True → 100. Oracle 50. TX has only 1 statute file; the model may have generalized incorrectly. Needs row-level Ralph OR cross-check against TX's CPI 2015 published criteria.

### #4 — WI IND_197 (and OH IND_197) errata candidate confirmation

WI extracted threshold=0 → 100; oracle 50. Same as the wi-tier1 Phase 2 errata candidate. OH similar (scor_unstable on threshold=0). If CPI 2015 systematically scored "no compensation minimum" states as MODERATE rather than YES, that's a documentable CPI inconsistency with their own published rubric ("anyone paid any amount → YES"). Worth a footnote in the projection mapping doc.

## Cost ledger

| State | Cost | σ Claude | σ GPT | Instantiation errors |
|---|---:|---:|---:|---:|
| NY | $2.8289 | 90.48% | 88.10% | 2 |
| WI | $2.4825 | 84.52% | 88.10% | 6 |
| OH | $3.7894 | 92.86% | 86.90% | 0 |
| CA | $2.8428 | 78.57% | 86.90% | 1 |
| TX | $2.4835 | 73.81% | 60.71% | 3 |
| **Cross-state envelope used** | **$14.4271 of $15** | | | **12 of 420 (2.9%)** |

Cross-state envelope vs the original $10 plan: +$4.43 over the original; +$0.57 under the expanded $15 ceiling.

## Artifacts produced

- **Audit results:** `docs/active/cross-state-cpi-2015-validation/results/20260605_cross_state_cpi_2015_validation.md` (Table A: 30 per-cell verdicts; Table B: 5 per-state summaries).
- **Audit script:** `scripts/cross_state_cpi_2015_audit.py` (reusable for future cross-state rounds; runs end-to-end in <1s).
- **Dispatcher extension:** `scripts/tier_1_direct_read_legal_axis.py` (`--results-base` CLI flag + plumbing) + `tests/test_tier_1_results_base_cli.py` (3 new tests).
- **180 dispatch result JSONs:** 5 states × 6 chunks × 2 models × 3 runs = 180. Committed under `docs/active/cross-state-cpi-2015-validation/results/tier_1/<STATE>_2015/`.
- **Branch skeleton:** `docs/active/cross-state-cpi-2015-validation/` (RESEARCH_LOG + convos/plans/results) + STATUS.md row.

## Done criteria status (per plan)

1. ✅ Dispatch complete (5 states × 6 default chunks = 180 result JSONs).
2. ✅ Per-state instantiation rate computed (Table B; range 0-6 errors per state, 12 / 420 total = 2.9%).
3. ✅ Per-(state, indicator) de-jure exact-match computed (Table A; 30 cells / 15 matches / 50%).
4. ✅ Mismatches diagnosed (1-sentence diagnosis per miss; vocab-mismatch vs value_unstable vs not-extracted vs over-projection).
5. ⚠️ Budget within $10 — **OVERRUN to $14.43**; expanded envelope to $15 with Dan's mid-session authorization. Documented as cost extrapolation lesson.
6. ✅ Doc graph self-consistent at commit (this convo + RESEARCH_LOG + STATUS + audit results all linked).

## Next-session candidates

Dan's call. In rough priority order:

1. **Remediate IND_199 + IND_207 vocab-mismatch (Open Q #1).** Highest-leverage fix — 9 of 15 misses collapse if helpers read CPI's published vocabulary. ~30 min of work; raises match rate from 50% → ~80% with no additional dispatch spend. Recommend option (a).
2. **Row-level Ralph on OH IND_201 + OH IND_203 (Open Q #2).** Disambiguate OH-specific statutory pattern from extraction error. Maybe 1-2 single-row dispatches (~$0.20).
3. **Footnote the WI + OH IND_197 errata candidate (Open Q #4).** Doc-only update to projection mapping doc.
4. **Cross-state vintage 2025 round** (deferred per plan §Out of scope). Apply the same dispatch + audit pattern to 2025 to test cross-vintage stability of extraction quality.
5. **5 deferred states (CO, IL, WA, FL, NC) at vintage 2015** (deferred per plan §Out of scope). Extends the 5-state validation to the full 10-state target list.

## Session meta

- Nori plan-then-fresh-session boundary held cleanly: planning happened on wi-ralph (the 2 originating convos); execution happened on this fresh branch off main.
- Cost discipline held: Dan-authorized envelope expansion mid-session before the 4 remaining dispatches kicked off; landed under the expanded ceiling.
- Doc graph walked at finish-convo (this convo + RESEARCH_LOG + STATUS update + audit results + plan back-reference all linked).
- 12 instantiation errors over 420 cell-dispatches (2.9%) — well under the plan's 5% pause threshold; no need to surface intra-dispatch.

## Next-session handoff sentence

*"Pick up branch `cross-state-cpi-2015-validation` (worktree at `.worktrees/cross-state-cpi-2015-validation`). Cross-state dispatch + audit complete: 5 states (NY/WI/OH/CA/TX × vintage 2015 × default-6-chunks) / 180 result JSONs / $14.4271 / 50% per-(state, indicator) match rate / 15 of 30 cells. **60% of the 15 misses are systematic projection-helper-vs-YAML-extraction vocabulary mismatches** on IND_199 (IntCell months vs string enum) + IND_207 (CPI's YES/MODERATE/NO vs internal structural enum). Highest-leverage next move: remediate the vocab-mismatch by updating the helpers in `src/lobby_analysis/projections/cpi_2015_c11.py` to read CPI's published vocabulary (Open Question #1, option a) — ~30 min, raises match rate to ~80%, $0 spend. See audit results at `docs/active/cross-state-cpi-2015-validation/results/20260605_cross_state_cpi_2015_validation.md` for Table A (30 per-cell verdicts) + Table B (5 per-state summaries with per-chunk diagnosis)."*
