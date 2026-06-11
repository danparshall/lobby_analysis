# Cross-state CPI 2015 projection-accuracy validation — 5 states × vintage 2015 × de-jure indicators

**Date:** 2026-06-05 (original) · **Amended:** 2026-06-05 (pressure-test refinement)
**Branch:** `wi-ralph-cpi-renewal-cadence` (this plan); execution session runs on a successor branch cut off main AFTER v2.1 merges
**Originating convo:** [`convos/20260605_cross_state_planning.md`](../convos/20260605_cross_state_planning.md) (original — written at finish-convo)
**Amendment convo:** [`convos/20260605_pr40_pressure_test.md`](../convos/20260605_pr40_pressure_test.md) (pressure-test refinement — written at finish-convo)
**Predecessors:**
- [`plans/20260605_phase_a_yaml_audit_at_scale.md`](20260605_phase_a_yaml_audit_at_scale.md) — Phase A pre-flight YAML audit (163 additives landed; BinaryCell + EnumCell templates confirmed at scale on WI)
- [`convos/20260605_phase_a_execution.md`](../convos/20260605_phase_a_execution.md) — A2.b dispatch baseline ($0.83 / 3 chunks / 21 cells / 0 errors on the 4-cell-type templates)
**Status:** APPROVED 2026-06-05 (amended same day) — Dan locked: fresh $10 envelope; 5-state × default-6-chunk × vintage **2015** scope; **per-(state, indicator) exact-match on the 6 de-jure CPI 2015 C11 indicators** as primary success metric; v2.1 merges to main BEFORE dispatch.

---

## Amendment 2026-06-05 — pressure-test refinement (PR 40 review)

The original plan locked a 10-state × 3-chunk scope (D1, D3, D4 below, kept inline as superseded). A pressure-test session 2026-06-05 (PR 40 review — full convo write-up at finish-convo) surfaced two refinements that Dan locked:

1. **De-jure-only success metric is more operational than the original "category-score within tolerance" framing.** CPI 2015 publishes per-(state, indicator) ground truth in a 700-cell CSV (`docs/historical/compendium-source-extracts/results/cpi_2015_c11_per_state_scores.csv`). Comparison is **per-cell exact-match on the 3-tier {0, 50, 100} de-jure scale** for the 6 de-jure indicators (IND_196, IND_197, IND_199, IND_201, IND_203, IND_207). Tier-1 (legal-axis-only) dispatch can be cleanly evaluated against this subset *without* the parallel research-agent practical-axis pipeline needing to have run — practical-axis cells aren't extracted from statutes and are explicitly out of scope this round (see updated §Out of scope).
2. **The 6 de-jure CPI indicators map 1:1 onto the dispatcher's 6 default chunks** (the `_DEFAULT_CHUNKS` tuple in `scripts/tier_1_direct_read_legal_axis.py`). Dropping the `--chunks` flag (default dispatch) gives full de-jure coverage; each chunk's extraction-quality lands a single indicator's match rate as its primary diagnostic. See updated §P3 for the mapping.

Trade-off Dan locked: full de-jure indicator coverage at the cost of cross-state breadth. **States cut from 10 to 5: NY, WI, OH, CA, TX** (drops CO, IL, WA, FL, NC — deferred to a follow-up round, not retired).

Sections affected: title; §Scope locked (D1, D3, D4 rows); §P3 (rewritten with 1:1 chunk↔indicator table); §Stage X1 (drop `--chunks` from example, refresh per-state cost); §Stage X2 (per-cell comparison spec replaces ±10-point category tolerance); §Cost projection (refreshed); §Done criteria (#1 / #3 reworded); §Decisions (D1/D3/D4 marked SUPERSEDED inline + new D7/D8/D9 added); §Out of scope (8 practical-axis indicators + 5 deferred states named); §Open Q #1/#2 (resolved); §Next-session handoff (rewritten); §Pre-execution checklist (Open Q #1 step dropped).

---

## Why this plan exists

Phase A (this branch) shipped 163 YAML additives across the v2.1 compendium and confirmed the BinaryCell + EnumCell additive templates at scale on **WI 2025 only**. The natural next question is the one the Compendium 2.0 success criterion (STATUS.md ⭐) is built around:

> **Falsifiable test:** populate compendium for state S in vintage Y via the single extraction pipeline → apply each rubric's projection → compare each projected per-state score to the rubric's published score for (S, Y). Match within tolerance ⇒ extraction is sound on the rows that rubric reads, in vintage Y.

We test that here at the smallest scope that exercises the falsifiability mechanism end-to-end: **5 states × 1 vintage × 6 de-jure CPI 2015 C11 indicators**. Pass ⇒ extraction pipeline + v2.1 YAML templates are sound on the de-jure rows CPI 2015 reads, in vintage 2015. Fail (per-(state, indicator)) ⇒ we have a localized debug signal — the failing chunk is identified by the 1:1 chunk↔indicator mapping (see §P3), and the diagnosis branches to either a row-level Ralph follow-up on the failing chunk or a projection-mapping footnote (cf. the iter-5 WI errata candidates IND_197 + IND_207).

---

## Scope locked

| Axis | Value | Source |
|---|---|---|
| States (5, in Dan's order) | **NY, WI, OH, CA, TX** | Dan 2026-06-05 (amendment lock — drops CO/IL/WA/FL/NC from the original 10-state list to fit a 6-chunk dispatch in the $10 envelope) |
| Vintage | **2015** (single vintage this round) | Dan 2026-06-05 ("do vintage 2015 and apply the CPI") |
| Chunk set | **Default 6 chunks** (omit `--chunks` flag) — `lobbying_definitions`, `registration_thresholds`, `registration_mechanics_and_exemptions`, `lobbyist_spending_report`, `principal_spending_report`, `enforcement_and_audits` | Dan 2026-06-05 (amendment lock — covers all 6 de-jure CPI 2015 C11 indicators 1:1; see §P3) |
| Primary success metric | **Per-(state, indicator) exact-match on the 6 de-jure CPI 2015 C11 indicators** (IND_196, IND_197, IND_199, IND_201, IND_203, IND_207); 3-tier scale {0, 50, 100} — exact-match, not ±10 tolerance. 30 comparison cells (5 states × 6 indicators) | Dan 2026-06-05 (amendment lock) |
| Secondary metrics (free byproducts) | Per-state instantiation rate; cross-state value-stability matrix per row | Plan default |
| Budget envelope | **Fresh $10** (atop wi-ralph's $3.51; wi-ralph cumulative lands at ~$13.51 max) | Dan 2026-06-05 |

**Statute bundle availability verified** for all 5 target states × 2015 vintage via `/tmp/check_statute_bundles.py` (2026-06-05 — originally verified for the 10-state list; the 5-state set is a subset, all bundles present). All `data/statutes/<STATE>/2015/sections/` directories present for NY, WI, OH, CA, TX.

---

## Prerequisites (must land before any cross-state dispatch)

These are **not** part of this plan's execution but are pre-execution preconditions. The implementing session (post-v2.1-merge) confirms each before dispatch.

### P1 — v2.1 promotion to main

Currently branch-local. Phase A's done-criteria are met on `wi-ralph-cpi-renewal-cadence`:
- v2.1 TSV (`compendium/disclosure_side_compendium_items_v2.1.tsv`, 183 rows)
- v2.1 YAML additives (163 prompts in `compendium/source_quotes.yaml`)
- Pattern C row split (`enforcement_and_audits` 2→4 rows, IND_208 axis fix)
- Dispatcher `_RESOLVED_CHUNKS` extension (`actor_registration_required` added)
- Phase A test suite (167 tests in `tests/test_phase_a_yaml_additives.py`)
- 12 archived stale JSONs under `_pre_phase_a_<chunk>/` with SUPERSEDED.md banners

**P1 path:** PR `wi-ralph-cpi-renewal-cadence` → `main`. Multi-committer norm: pull before push; if conflicts on shared files (`STATUS.md`, `compendium/disclosure_side_compendium_items_v2.tsv`, `source_quotes.yaml`), surface to Dan rather than auto-resolve. After merge, `wi-ralph-cpi-renewal-cadence` moves to `docs/historical/` per the active → historical lifecycle.

### P2 — Successor branch cut off main

Cut a new branch off main for cross-state execution. Suggested name: `cross-state-cpi-2015-validation` (kebab-case, semantic, no temporal suffix). Worktree convention per CLAUDE.md: `.worktrees/<branch>/` with `data → main/data` symlink + `.env.local → main/.env.local` symlink (mandatory for this repo per personal-info block).

Seed the successor branch's `docs/active/<branch>/` with `RESEARCH_LOG.md`, empty `convos/` `plans/` `results/` dirs. Copy this plan over (or just reference it from main's `docs/historical/wi-ralph-cpi-renewal-cadence/plans/` once wi-ralph archives).

### P3 — Default-6-chunks map 1:1 onto the 6 de-jure CPI 2015 C11 indicators

The dispatcher's `_DEFAULT_CHUNKS` tuple — `lobbying_definitions`, `registration_thresholds`, `registration_mechanics_and_exemptions`, `lobbyist_spending_report`, `principal_spending_report`, `enforcement_and_audits` — hosts the 6 de-jure CPI 2015 C11 indicators as a clean 1:1 correspondence (almost certainly by design — the chunk decomposition was informed by the CPI indicator structure when originally cut):

| Default chunk | De-jure CPI indicator | Cells the projection reads (legal axis) |
|---|---|---|
| `lobbying_definitions` (15 rows) | IND_196 (definition recognizes executive-branch lobbyists) | `def_target_legislative_branch`, `def_target_governors_office` |
| `registration_thresholds` (6 rows) | IND_197 (anyone paid is defined as a lobbyist) | `lobbyist_registration_threshold_compensation_dollars` |
| `registration_mechanics_and_exemptions` (8 rows) | IND_199 (registration form filed at least annually in law) | `lobbyist_registration_renewal_cadence` |
| `lobbyist_spending_report` (34 rows) | IND_201 (itemized lobbyist spending reports including compensation) | `lobbyist_spending_report_required`, `..._includes_itemized_expenses`, `..._includes_total_compensation` |
| `principal_spending_report` (23 rows) | IND_203 (principal/employer spending reports including compensation) | `principal_spending_report_required`, `principal_spending_report_includes_compensation_paid_to_lobbyists` |
| `enforcement_and_audits` (4 rows, post-v2.1) | IND_207 (regular auditing of disclosure records in law) | `lobbying_disclosure_audit_required_in_law` |

**Diagnostic structure that falls out:** each chunk's extraction-quality lands a single de-jure indicator's match rate. If a state's IND_201 mismatches, the failing chunk (`lobbyist_spending_report`) is identified without further triangulation — no need to disambiguate which chunk's prompts to scrutinize.

**Practical-axis indicators (IND_198, 200, 202, 204, 205, 206, 208, 209) are out of scope this round** — they require the research-agent practical-axis pipeline, not statute-parsing. Tier-1 is legal-axis only. See §Out of scope.

**Implementing agent: re-read `docs/historical/compendium-source-extracts/results/projections/cpi_2015_c11_projection_mapping.md` end-to-end at execution time** to verify these cells. The legal-axis cell IDs above are read from `src/lobby_analysis/projections/cpi_2015_c11.py`'s `project_ind_*` helpers (the `_legal(cells, "...")` calls inside the 6 de-jure helper functions). If the projection mapping doc disagrees with what the helpers actually read, **the helpers are the source of truth** for this validation round — surface the discrepancy to Dan in the audit results, don't silently re-key.

### P4 — Oracle data per state

CPI 2015 C11 published per-state scores: `docs/historical/compendium-source-extracts/results/cpi_2015_c11_per_state_scores.csv` (all 50 states + DC). All 10 target states have ground truth.

---

## Stages

### Stage X1 — Dispatch loop (default 6 chunks × 5 states ≈ $8 expected, with non-trivial variance)

Sequential dispatch per state-vintage. Per state:

```
uv run python scripts/tier_1_direct_read_legal_axis.py \
    --state <STATE> \
    --vintage 2015
```

(No `--chunks` flag — the dispatcher's default is the 6-chunk set that maps 1:1 onto the 6 de-jure CPI 2015 C11 indicators per §P3.)

Per Dan's "batch-dispatch-per-loop, want the overall effect not per-state optimization" framing (kickoff convo §Decisions): the loop is the unit of analysis, not any individual state's dispatch result. We're testing whether the pipeline writes coherent multi-state CPI-projection-comparable data on the de-jure indicators, not whether NY's IND_201 individually matches.

Results land under `docs/active/cross-state-cpi-2015-validation/results/tier_1/<STATE>_2015/` (or wherever the successor branch's results-base resolves to).

**Dispatch order (cost-calibration anchor first):** **NY, WI, OH, CA, TX**. NY is the first execution because it's the largest unknown for cost variance (statute corpus may differ substantially from WI's); WI is second because it's the known-good baseline from Phase A — together they pin down per-state cost on two ends of expected variance before committing to the remaining 3 states.

**Cost budget:** ~$8 expected dispatched + ~$2 headroom for re-runs / one-off Ralph follow-ups on outlier states ≈ $10 envelope. **Important caveat:** the $8 figure extrapolates from Phase A's $0.83/state-for-3-chunks (21 cells) to 6 chunks ≈ 2× per-state cost ≈ $1.6/state × 5 states. But the 6 default chunks contain ~90 rows total vs Phase A's 21 — chunk-size variance is large (`lobbyist_spending_report` is 34 rows, `enforcement_and_audits` is 4). If NY's actual cost exceeds $2.50 (1.5× the extrapolation), **pause after NY and surface to Dan** — the remaining 4 states would bust the envelope at that rate.

**Instantiation-error pause threshold:** unchanged from original — if any state's dispatch shows instantiation errors >5% on the 4-cell-type-template rows, **pause and surface to Dan** before continuing.

### Stage X2 — Per-(state, indicator) projection audit ($0)

For each state's results JSONs, run **only the 6 de-jure projection helpers** (`project_ind_196`, `_197`, `_199`, `_201`, `_203`, `_207`) from `src/lobby_analysis/projections/cpi_2015_c11.py` over the extracted cell values. The 8 practical-axis helpers are out of scope this round — do not call them; their `_practical()` lookups would return `None` and default to 0, which would be a measurement artifact, not a real result.

**Oracle slice:** load `load_per_state_ground_truth()` from `cpi_2015_c11.py`, then slice to the 30 comparison cells: `{(state, ind): score for state in {"NY","WI","OH","CA","TX"} for ind in ("IND_196","IND_197","IND_199","IND_201","IND_203","IND_207")}`. De-jure scores are already normalized to {0, 50, 100} via the loader's `_DE_JURE_TIER_TO_SCORE` map.

**Comparison rule:** **exact-match** on the 3-tier {0, 50, 100} scale. No ±10 tolerance — de-jure is categorical, not continuous. Per-cell verdict is binary (match / mismatch); per-(state, indicator) is the unit of analysis.

**Output:** `results/20260605_cross_state_cpi_2015_validation.md` — two tables:

*Table A — Per-cell comparison (30 rows):*
- State
- Indicator (IND_xxx)
- Chunk (the §P3 chunk that hosts this indicator)
- Published CPI 2015 score ({0, 50, 100})
- Projected score from extracted cells ({0, 50, 100})
- Match? (yes/no)
- Notes (e.g., "matches WI iter-5 IND_207 errata pattern" / "novel mismatch — Ralph candidate")

*Table B — Per-(state) summary:*
- State
- De-jure indicators matched (count / 6)
- Instantiation errors across all 6 chunks (count)
- Total dispatch cost ($)
- Per-chunk diagnosis (which chunks' indicators matched vs mismatched)

### Stage X3 — Documentation + commit

- Convo summary at `convos/20260605_cross_state_cpi_2015_validation_execution.md` (on successor branch)
- Update successor branch's `RESEARCH_LOG.md`
- Update `STATUS.md` (the successor branch's row; do NOT rewrite wi-ralph's row — multi-committer norm)
- Walk doc link graph (per persistent-memory feedback memo): convo back-references plan; plan back-references convo; RESEARCH_LOG indexes both
- Commit + push

---

## Cost projection (amended 2026-06-05)

| Stage | Cost | Cumulative (cross-state envelope) |
|---|---:|---:|
| X1 — Dispatch (6 default chunks × 5 states × 1 vintage) | ~$8 expected (high variance — see caveat) | $8 |
| X2 — Per-(state, indicator) audit | $0 | $8 |
| X3 — Documentation | $0 | $8 |
| **Total this dispatch round** | **~$8 expected** | **$8 of $10 expected** |
| Headroom for one-off follow-ups (single-row Ralph on a failing state, re-dispatch after YAML hotfix) | up to $2 | up to $10 |

**Cost extrapolation caveat:** Phase A's $0.83/state was on a 21-cell 3-chunk subset. The default 6-chunk dispatch is ~90 rows total (chunks: 15/6/8/34/23/4). Per-chunk cost scales sub-linearly with cell count (statute-text input dominates), so $8 is the working estimate — but expect variance of ±$2 depending on per-chunk output volume. **NY dispatched first as cost anchor**; pause-and-surface threshold at NY > $2.50 per §Stage X1.

---

## Done criteria (for "cross-state CPI 2015 validation is complete")

Landing this work checks all of:

1. **Dispatch complete** — 5 state-vintages × 6 default chunks dispatched; all JSONs present in `results/tier_1/<STATE>_2015/`.
2. **Per-state instantiation rate computed** — % cells coerced cleanly per state-vintage; documented in the audit results.
3. **Per-(state, indicator) de-jure exact-match computed** — Table A (30 cells: 5 states × 6 de-jure indicators) populated; Table B per-state summary; documented in the audit results.
4. **Mismatches diagnosed** — for each (state, indicator) failing exact-match, a 1-sentence diagnosis (e.g., "matches WI iter-5 IND_207 errata pattern" vs "novel template failure mode — Ralph candidate").
5. **Budget within $10** — cross-state envelope respected; if exceeded, surface to Dan before continuing.
6. **Doc graph self-consistent** at commit — plan back-referenced from convo, convo from RESEARCH_LOG, RESEARCH_LOG from STATUS.

---

## Decisions locked this session

### ~~D1 — Target state list: NY, CO, WI, CA, TX, IL, WA, FL, NC, OH (order preserved)~~ **SUPERSEDED by D7 (2026-06-05 amendment)**
Dan's research-driven update; supersedes the original handoff's 15-state list. NY's 2015/2025 statute bundles exist (handoff was incorrect to mark NY 2010-only). WY remains out of scope (2010-only). *Superseded: amended to 5 states (NY, WI, OH, CA, TX) to fit a full 6-chunk de-jure dispatch in the $10 envelope. CO/IL/WA/FL/NC deferred to a follow-up round.*

### D2 — Vintage: 2015 (single vintage this round)
Dan picked 2015 specifically to match CPI 2015 oracle's measurement period. Vintage 2025 deferred — future work could re-run on 2025 for cross-vintage stability signal.

### ~~D3 — Chunk set: Phase A validation subset~~ **SUPERSEDED by D8 (2026-06-05 amendment)**
`actor_registration_required` + `registration_thresholds` + `enforcement_and_audits`. Matches Phase A's A2.b touched chunks. See Open Question #1 for the chunk-vs-projection-coverage tension. *Superseded: amended to default-6-chunks (omit `--chunks` flag) to cover all 6 de-jure CPI 2015 C11 indicators 1:1.*

### ~~D4 — Success metric: CPI 2015 C11 projection accuracy per state~~ **SUPERSEDED by D9 (2026-06-05 amendment)**
Primary metric. Secondary metrics (instantiation rate, value-stability matrix) computed as free byproducts. *Superseded: amended to per-(state, indicator) exact-match on the 6 de-jure CPI indicators; 30 comparison cells total. Per-cell categorical comparison replaces per-state continuous-tolerance comparison.*

### D5 — v2.1 promotion to main BEFORE cross-state dispatch
PR `wi-ralph-cpi-renewal-cadence` → main first. Successor branch cut off main for cross-state execution. Clean inheritance.

### D6 — Budget envelope: fresh $10 (atop wi-ralph $3.51)
Cumulative wi-ralph after cross-state lands at ~$13.51 max.

### D7 — Target state list (amended): NY, WI, OH, CA, TX (5 states, dispatch order preserved)
Dan 2026-06-05 (PR 40 pressure-test). Selected to span Northeast (NY), Midwest (WI, OH), West (CA), South (TX) with WI as the Phase A known-good anchor. NY dispatched first as cost-calibration anchor for variance estimation against WI's known baseline. **Deferred to follow-up round (not retired): CO, IL, WA, FL, NC.**

### D8 — Chunk set (amended): default 6 chunks via dispatcher default
Dan 2026-06-05 (PR 40 pressure-test). Omit `--chunks` flag entirely; dispatcher's `_DEFAULT_CHUNKS` tuple covers the 6 chunks hosting the 6 de-jure CPI 2015 C11 indicators 1:1. This drops the `actor_registration_required` chunk (BinaryCell cross-state template test) entirely from this round — the test is deferred to a follow-up, justified by Phase A's 11/11 BinaryCell verification on WI 2025 already establishing the template at scale on the matter that mattered for Phase A.

### D9 — Success metric (amended): per-(state, indicator) exact-match on 6 de-jure CPI indicators
Dan 2026-06-05 (PR 40 pressure-test). 6 indicators: IND_196 (def_target legislative + governors_office), IND_197 (registration threshold), IND_199 (renewal cadence), IND_201 (lobbyist spending report compound), IND_203 (principal spending report compound), IND_207 (audit required in law). 5 states × 6 indicators = 30 comparison cells. Exact-match on the 3-tier {0, 50, 100} scale — no ±10 continuous tolerance. The 8 practical-axis indicators (IND_198, 200, 202, 204, 205, 206, 208, 209) are explicitly out of scope this round — those require the research-agent practical-axis pipeline, not statute-parsing.

---

## Out of scope (explicitly)

- **Practical-axis CPI 2015 C11 indicators.** IND_198, IND_200, IND_202, IND_204, IND_205, IND_206, IND_208, IND_209 — all 8 de-facto indicators that the CPI projection helpers read via `_practical()`. Practical-axis cells come from a separate research-agent pipeline, not statute-parsing; Tier-1 is legal-axis only. The cross-state validation this round computes the 6 de-jure projections only.
- **The 5 deferred states.** CO, IL, WA, FL, NC. Statute bundles exist for all of them at vintage 2015 (verified in §Scope locked); they're cut for envelope reasons, not data availability. A follow-up dispatch can pick them up after this round establishes the dispatch+audit pattern on the 5-state anchor set.
- **`actor_registration_required` chunk.** Phase A's BinaryCell template was verified at scale on WI 2025 (11/11 cells); cross-state BinaryCell template verification is deferred to a follow-up dispatch (not retired).
- **Vintage 2025 cross-state dispatch.** Deferred to a follow-up. Vintage-stability per state (2015 ↔ 2025) is the natural next research line after this lands.
- **Other rubric projections** (PRI 2010, FOCAL 2024, Sunlight 2015, Newmark 2005/2017, etc.). CPI 2015 C11 only, this round.
- **Row-level Ralph on mismatching (state, indicator) cells.** If a (state, indicator) fails exact-match, the diagnostic is captured in audit Table A; Ralph itself is a separate session per the Phase B pattern.
- **Long-tail typed singletons** (TimeThresholdCell, count_with_FTE, SectorClassification, etc.). These remain DEFERRED per Phase A plan §"Out of scope."
- **Retroactive edits to wi-ralph's prior convos/plans.** The "15 states" references in handoff + "10 states" references in kickoff convo + Phase A plan are historical records of what was known at write time; this plan (as amended) supersedes them going forward. Doc-link-graph integrity preserved via forward references, not back-rewrites.

---

## Open questions for execution session

### ~~#1 — Should the chunk set swap `actor_registration_required` → `registration_mechanics_and_exemptions`?~~ **RESOLVED 2026-06-05 (amendment)**
Resolved by D8: drop `--chunks` entirely → default-6-chunks dispatch. Covers all 6 de-jure indicators 1:1; `actor_registration_required` drops out of this round (deferred follow-up). Both originally-considered alternatives (Phase A subset / Open Q #1 swap) are superseded.

### ~~#2 — Tolerance for "projected score matches published CPI 2015"~~ **RESOLVED 2026-06-05 (amendment)**
Resolved by D9: per-(state, indicator) **exact-match on the 3-tier {0, 50, 100} de-jure scale**. No continuous tolerance needed — de-jure is categorical. The implementing agent does NOT need to invent or read a ±N convention from the projection test files; the comparison rule is exact-match on the de-jure subset, period.

### #3 — What does the implementing agent do if any state's instantiation error rate exceeds Phase A's 0% baseline?

Phase A WI achieved 0 errors on the 4-cell-type templates. If e.g. NY hits 6/6 errors on `enforcement_and_audits` due to NY-specific statute idioms, that's signal — but is it Ralph-it-now (additional spend), document-and-continue (skip NY in the projection table), or stop-everything (pause for redesign)? **Default in plan: pause + surface to Dan at >5% error rate per state**. Implementing agent may push back if Dan articulates a different threshold. (Unchanged from original.)

### ~~#4 — Should NY 2010 also be in scope (for completeness on the 10-state list)?~~ **OBSOLETE 2026-06-05 (amendment)**
Original question presumed the 10-state scope. Under D7's 5-state amendment, NY is still in scope at vintage 2015 (the CPI 2015 measurement vintage); 2010 remains skip. No change to substance — just notes the question's framing dissolved with the state-list amendment.

---

## Linked artifacts

- **Predecessor plan:** [`20260605_phase_a_yaml_audit_at_scale.md`](20260605_phase_a_yaml_audit_at_scale.md)
- **Predecessor convo (Phase A execution):** [`../convos/20260605_phase_a_execution.md`](../convos/20260605_phase_a_execution.md)
- **CPI 2015 projection module:** `src/lobby_analysis/projections/cpi_2015_c11.py`
- **CPI 2015 projection tests:** `tests/projections/test_cpi_2015_c11_{aggregation,ground_truth,per_item}.py`
- **CPI 2015 projection mapping doc:** `docs/historical/compendium-source-extracts/results/projections/cpi_2015_c11_projection_mapping.md`
- **CPI 2015 oracle data:** `docs/historical/compendium-source-extracts/results/cpi_2015_c11_per_state_scores.csv`
- **v2.1 TSV (branch-local until P1 merges):** `compendium/disclosure_side_compendium_items_v2.1.tsv`
- **YAML SSOT (branch-local until P1 merges):** `compendium/source_quotes.yaml`
- **Dispatcher:** `scripts/tier_1_direct_read_legal_axis.py`
- **Chunks manifest:** `src/lobby_analysis/chunks_v2/manifest.py`
- **Statute bundle availability script (session artifact):** `/tmp/check_statute_bundles.py`

---

## Pre-execution checklist (implementing agent)

**This is a fresh-session-TDD task.** This plan was written one session; the execution session follows after v2.1 merges to main and a successor branch is cut.

1. Read this plan end-to-end **including the §Amendment 2026-06-05 banner at top**.
2. Read [`convos/20260605_phase_a_execution.md`](../convos/20260605_phase_a_execution.md) end-to-end (immediate Phase A baseline; A2.b dispatch shape; TDD discipline; the dispatcher `_RESOLVED_CHUNKS` extension).
3. Read [`convos/20260605_cross_state_planning.md`](../convos/20260605_cross_state_planning.md) (this plan's originating convo — captures the original 10-state framing) **AND** [`convos/20260605_pr40_pressure_test.md`](../convos/20260605_pr40_pressure_test.md) (the amendment convo — captures the 5-state × default-6-chunks × de-jure-exact-match refinement Dan locked).
4. Read `docs/historical/compendium-source-extracts/results/projections/cpi_2015_c11_projection_mapping.md` end-to-end — confirms the per-indicator projection scoring rules. **Reminder per §P3**: if this doc disagrees with what the `project_ind_*` helpers actually read, the helpers are the source of truth for this validation round.
5. Read `src/lobby_analysis/projections/cpi_2015_c11.py` end-to-end — confirm the 6 de-jure helper APIs (`project_ind_196`, `_197`, `_199`, `_201`, `_203`, `_207`) and `load_per_state_ground_truth()` signature.
6. Verify P1, P2, P3, P4 above. If any prereq is unmet (most likely P1: v2.1 not yet merged to main), **stop and surface to Dan**.
7. Begin TDD per `skills/test-driven-development/SKILL.md`:
   - RED batch: tests asserting results JSONs exist per (state, vintage); zero unhandled errors; per-(state, indicator) de-jure exact-match table A populated (30 cells). No state-count threshold for "pass" — document the result; this round is a measurement, not a gate.
   - GREEN batch: dispatch loop + audit script.
8. Dispatch order: **NY first** (cost-calibration anchor — see §Stage X1 caveat); **WI second** (Phase A known-good baseline); then OH, CA, TX. After NY, check actual dispatch cost; if > $2.50, **pause and surface to Dan** before continuing.
9. After X1 dispatch lands: run X2 audit; populate Table A (30 per-cell verdicts) and Table B (5 per-state summaries); for each mismatch, write a 1-sentence diagnosis. If any (state, indicator) shows a novel template-failure mode (not matching WI iter-5 errata patterns), surface to Dan before X3.
10. Finish-convo: walk the doc-link-graph before commit.

---

## Next-session handoff sentence

*"Pick up the successor branch cut off main (`cross-state-cpi-2015-validation` or similar) after v2.1 + Phase A YAML merge from wi-ralph-cpi-renewal-cadence. Read this plan end-to-end **including the §Amendment 2026-06-05 banner at top** (now living on main at `docs/historical/wi-ralph-cpi-renewal-cadence/plans/20260605_cross_state_cpi_2015_validation.md`), plus both the Phase A execution convo and the PR 40 pressure-test convo (the amendment's originating convo). Cross-state CPI 2015 C11 de-jure projection validation: **5 states (NY, WI, OH, CA, TX in dispatch order) × vintage 2015 × default 6 chunks (no `--chunks` flag)**. Fresh $10 envelope; ~$8 expected dispatched + $2 headroom; NY dispatched first as cost-calibration anchor (pause-and-surface threshold at NY > $2.50). Primary metric: **per-(state, indicator) exact-match on the 6 de-jure CPI 2015 C11 indicators** (IND_196, IND_197, IND_199, IND_201, IND_203, IND_207); 3-tier {0, 50, 100} categorical comparison; no ±10 continuous tolerance. The 8 practical-axis indicators are out of scope this round (research-agent pipeline, not statute-parsing). Secondary: instantiation rate + cross-state value-stability matrix. No remaining pre-dispatch blocking open questions — the original Open Q #1 (chunk-set swap) and #2 (tolerance) were resolved by the 2026-06-05 amendment."*
