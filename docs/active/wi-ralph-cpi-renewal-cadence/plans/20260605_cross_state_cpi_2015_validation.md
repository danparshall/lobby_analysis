# Cross-state CPI 2015 projection-accuracy validation — 10 states × vintage 2015

**Date:** 2026-06-05
**Branch:** `wi-ralph-cpi-renewal-cadence` (this plan); execution session runs on a successor branch cut off main AFTER v2.1 merges
**Originating convo:** [`convos/20260605_cross_state_planning.md`](../convos/20260605_cross_state_planning.md) (this session — written at finish-convo)
**Predecessors:**
- [`plans/20260605_phase_a_yaml_audit_at_scale.md`](20260605_phase_a_yaml_audit_at_scale.md) — Phase A pre-flight YAML audit (163 additives landed; BinaryCell + EnumCell templates confirmed at scale on WI)
- [`convos/20260605_phase_a_execution.md`](../convos/20260605_phase_a_execution.md) — A2.b dispatch baseline ($0.83 / 3 chunks / 21 cells / 0 errors on the 4-cell-type templates)
**Status:** APPROVED 2026-06-05 — Dan locked: fresh $10 envelope; breadth-first 1-vintage × 10-state scope; vintage **2015** (not 2025); CPI 2015 C11 projection-accuracy as primary success metric; v2.1 merges to main BEFORE dispatch.

---

## Why this plan exists

Phase A (this branch) shipped 163 YAML additives across the v2.1 compendium and confirmed the BinaryCell + EnumCell additive templates at scale on **WI 2025 only**. The natural next question is the one the Compendium 2.0 success criterion (STATUS.md ⭐) is built around:

> **Falsifiable test:** populate compendium for state S in vintage Y via the single extraction pipeline → apply each rubric's projection → compare each projected per-state score to the rubric's published score for (S, Y). Match within tolerance ⇒ extraction is sound on the rows that rubric reads, in vintage Y.

We test that here at the smallest scope that exercises the falsifiability mechanism end-to-end: 10 states × 1 vintage × the operational CPI 2015 C11 projection. Pass ⇒ extraction pipeline + v2.1 YAML templates are sound on CPI-readable rows for the 2015 vintage. Fail (per-state) ⇒ we have a localized debug signal — either the templates need a row-level Ralph follow-up on the failing state, or the projection mapping needs a footnote (cf. the iter-5 WI errata candidates IND_197 + IND_207).

---

## Scope locked

| Axis | Value | Source |
|---|---|---|
| States (10, in Dan's order) | **NY, CO, WI, CA, TX, IL, WA, FL, NC, OH** | Dan 2026-06-05 ("after researching data availability, our top-ten states are…") |
| Vintage | **2015** (single vintage this round) | Dan 2026-06-05 ("do vintage 2015 and apply the CPI") |
| Chunk set | **Phase A validation subset:** `actor_registration_required` + `registration_thresholds` + `enforcement_and_audits` | Dan 2026-06-05 (scope-shape Q) — but see §Open Question #1 below for the chunk-vs-projection-coverage tension |
| Primary success metric | **CPI 2015 C11 projection accuracy per state** | Dan 2026-06-05 |
| Secondary metrics (free byproducts) | Per-state instantiation rate; cross-state value-stability matrix per row | Plan default |
| Budget envelope | **Fresh $10** (atop wi-ralph's $3.51; wi-ralph cumulative lands at ~$13.51 max) | Dan 2026-06-05 |

**Statute bundle availability verified** for all 10 states × 2015 vintage via `/tmp/check_statute_bundles.py` (2026-06-05). All `data/statutes/<STATE>/2015/sections/` directories present.

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

### P3 — Verify CPI 2015 C11 projection coverage of the validation subset

The 3-chunk validation subset feeds CPI 2015 C11 indicators as follows:

| Chunk | CPI 2015 C11 indicators read | CPI projection contribution |
|---|---|---|
| `actor_registration_required` (11 binary) | **None** | 0% (per `projection_mapping.md` review) |
| `registration_thresholds` (6 cells) | IND_197 (compensation), possibly IND_198 | ~25% of CPI 2015 C11 |
| `enforcement_and_audits` (4 cells, post-v2.1) | IND_207 (audit_required), IND_208 (penalty defined), IND_209 (penalty imposed) | ~37% of CPI 2015 C11 |

**Implementing agent: re-read `docs/historical/compendium-source-extracts/results/projections/cpi_2015_c11_projection_mapping.md` end-to-end at execution time** to verify these counts. If the projection touches additional rows in the validation subset chunks (or doesn't touch some I've assumed), surface the corrected coverage table to Dan before dispatch.

### P4 — Oracle data per state

CPI 2015 C11 published per-state scores: `docs/historical/compendium-source-extracts/results/cpi_2015_c11_per_state_scores.csv` (all 50 states + DC). All 10 target states have ground truth.

---

## Stages

### Stage X1 — Dispatch loop (1 chunk × 10 states ≈ $0.83 per chunk-batch; full subset ≈ $8.30)

Sequential dispatch per state-vintage; or batched if the dispatcher supports it. Per state:

```
uv run python scripts/tier_1_direct_read_legal_axis.py \
    --state <STATE> \
    --vintage 2015 \
    --chunks actor_registration_required registration_thresholds enforcement_and_audits
```

Per Dan's "batch-dispatch-per-loop, want the overall effect not per-state optimization" framing (kickoff convo §Decisions confirmed with Dan): the loop is the unit of analysis, not any individual state's dispatch result. We're testing whether the pipeline writes coherent multi-state CPI-projection-comparable data, not whether NY's IND_207 individually matches.

Results land under `docs/active/cross-state-cpi-2015-validation/results/tier_1/<STATE>_2015/` (or wherever the successor branch's results-base resolves to).

**Cost budget:** $8.30 dispatched + ~$1.70 headroom for re-runs / one-off Ralph follow-ups on outlier states ≈ $10 envelope. If any state's dispatch shows instantiation errors >5% on the 4-cell-type-template rows, **pause and surface to Dan** before continuing — the per-state failure pattern is the diagnostic signal.

### Stage X2 — Projection audit per state ($0)

For each state's results JSONs, run the CPI 2015 C11 projection function (`src/lobby_analysis/projections/cpi_2015_c11.py`) over the extracted cell values. Compute per-state projected score; compare against the oracle CSV. Aggregate into a per-state pass/fail/within-tolerance table.

**Tolerance:** TBD by the projection function's existing test contracts (`tests/projections/test_cpi_2015_c11_ground_truth.py` — implementing agent reads to find existing tolerance). If no convention exists, propose to Dan: ±10 points (CPI 2015 C11 is on a ~50-point scale per chunk).

**Output:** `results/20260605_cross_state_cpi_2015_validation.md` — per-state table with columns:
- State
- Published CPI 2015 C11 score
- Projected score from extracted cells
- Diff (absolute, signed)
- Within tolerance? (yes/no)
- Instantiation errors (count)
- Notes (e.g., "iter-5 errata-candidate row IND_207 dragged projection low — expected")

### Stage X3 — Documentation + commit

- Convo summary at `convos/20260605_cross_state_cpi_2015_validation_execution.md` (on successor branch)
- Update successor branch's `RESEARCH_LOG.md`
- Update `STATUS.md` (the successor branch's row; do NOT rewrite wi-ralph's row — multi-committer norm)
- Walk doc link graph (per persistent-memory feedback memo): convo back-references plan; plan back-references convo; RESEARCH_LOG indexes both
- Commit + push

---

## Cost projection

| Stage | Cost | Cumulative (cross-state envelope) |
|---|---:|---:|
| X1 — Dispatch (3 chunks × 10 states × 1 vintage) | ~$8.30 | $8.30 |
| X2 — Projection audit | $0 | $8.30 |
| X3 — Documentation | $0 | $8.30 |
| **Total this dispatch round** | **~$8.30** | **$8.30 of $10** |
| Headroom for one-off follow-ups (single-row Ralph on a failing state, re-dispatch after YAML hotfix) | up to $1.70 | up to $10 |

If implementing agent picks Open Question #1 (swap `actor_registration_required` → `registration_mechanics_and_exemptions`), cost drops to ~$7.30 with $2.70 headroom.

---

## Done criteria (for "cross-state CPI 2015 validation is complete")

Landing this work checks all of:

1. **Dispatch complete** — 10 state-vintages × 3 chunks dispatched; all JSONs present in `results/tier_1/<STATE>_2015/`.
2. **Per-state instantiation rate computed** — % cells coerced cleanly per state-vintage; documented in the audit results.
3. **CPI 2015 C11 projection computed per state** — projected score vs published score with tolerance verdict, in the audit results table.
4. **Outliers diagnosed** — for each state failing tolerance, a 1-sentence diagnosis (e.g., "matches WI iter-5 IND_207 errata pattern" vs "novel template failure mode — Ralph candidate").
5. **Budget within $10** — cross-state envelope respected; if exceeded, surface to Dan before continuing.
6. **Doc graph self-consistent** at commit — plan back-referenced from convo, convo from RESEARCH_LOG, RESEARCH_LOG from STATUS.

---

## Decisions locked this session

### D1 — Target state list: NY, CO, WI, CA, TX, IL, WA, FL, NC, OH (order preserved)
Dan's research-driven update; supersedes the original handoff's 15-state list. NY's 2015/2025 statute bundles exist (handoff was incorrect to mark NY 2010-only). WY remains out of scope (2010-only).

### D2 — Vintage: 2015 (single vintage this round)
Dan picked 2015 specifically to match CPI 2015 oracle's measurement period. Vintage 2025 deferred — future work could re-run on 2025 for cross-vintage stability signal.

### D3 — Chunk set: Phase A validation subset
`actor_registration_required` + `registration_thresholds` + `enforcement_and_audits`. Matches Phase A's A2.b touched chunks. See Open Question #1 for the chunk-vs-projection-coverage tension.

### D4 — Success metric: CPI 2015 C11 projection accuracy per state
Primary metric. Secondary metrics (instantiation rate, value-stability matrix) computed as free byproducts.

### D5 — v2.1 promotion to main BEFORE cross-state dispatch
PR `wi-ralph-cpi-renewal-cadence` → main first. Successor branch cut off main for cross-state execution. Clean inheritance.

### D6 — Budget envelope: fresh $10 (atop wi-ralph $3.51)
Cumulative wi-ralph after cross-state lands at ~$13.51 max.

---

## Out of scope (explicitly)

- **Vintage 2025 cross-state dispatch.** Deferred to a follow-up. Vintage-stability per state (2015 ↔ 2025) is the natural next research line after this lands.
- **Other rubric projections** (PRI 2010, FOCAL 2024, Sunlight 2015, Newmark 2005/2017, etc.). CPI 2015 C11 only, this round.
- **Row-level Ralph on outlier states.** If a state fails CPI 2015 projection tolerance, the diagnostic is captured in audit notes; Ralph itself is a separate session per the Phase B pattern.
- **Long-tail typed singletons** (TimeThresholdCell, count_with_FTE, SectorClassification, etc.). These remain DEFERRED per Phase A plan §"Out of scope."
- **`actor_registration_required` chunk if Open Question #1 swaps it out.** In that case the BinaryCell cross-state template test is deferred to a follow-up dispatch.
- **Retroactive edits to wi-ralph's prior convos/plans.** The "15 states" references in kickoff convo + Phase A plan are historical records of what was known at write time; this plan supersedes them going forward. Doc-link-graph integrity preserved via forward references, not back-rewrites.

---

## Open questions for execution session

### #1 (highest-leverage) — Should the chunk set swap `actor_registration_required` → `registration_mechanics_and_exemptions`?

The Phase A validation subset (D3) was named for Phase A's A2.b touched chunks. Of those 3 chunks, `actor_registration_required` contributes 0% to CPI 2015 C11 projection — it's PRI/FOCAL-anchored, not CPI. So ~48% of the $8.30 per-loop spend ($4 of $8.30) goes to a chunk that doesn't feed the primary success metric (D4).

Swapping in `registration_mechanics_and_exemptions` (8 cells, ~$0.30/state):
- Cost drops: ~$0.73/state × 10 = ~$7.30 (vs $8.30); $2.70 headroom (vs $1.70)
- CPI projection coverage rises: `registration_mechanics_and_exemptions` hosts IND_196 (registration_required) + IND_199 (renewal_cadence). The renewal_cadence row is Phase B's iter 1+2 winner — already iter-tested at scale on WI.
- Cost: lose the BinaryCell template cross-state test (defer the 11-row actor coverage to a follow-up)

Implementing agent: read `cpi_2015_c11_projection_mapping.md` end-to-end to confirm coverage counts, then surface the swap option to Dan with the corrected per-chunk projection contributions. **This is the most important open question** — it's the difference between 52% and ~95% of the dispatch budget feeding the primary metric.

### #2 — Tolerance for "projected score matches published CPI 2015"

Read `tests/projections/test_cpi_2015_c11_ground_truth.py` for existing tolerance convention. If none documented, propose ±10 points (the chunk-level scale).

### #3 — What does the implementing agent do if any state's instantiation error rate exceeds Phase A's 0% baseline?

Phase A WI achieved 0 errors on the 4-cell-type templates. If e.g. NY hits 6/6 errors on `enforcement_and_audits` due to NY-specific statute idioms, that's signal — but is it Ralph-it-now (additional spend), document-and-continue (skip NY in the projection table), or stop-everything (pause for redesign)? **Default in plan: pause + surface to Dan at >5% error rate per state**. Implementing agent may push back if Dan articulates a different threshold.

### #4 — Should NY 2010 also be in scope (for completeness on the 10-state list)?

NY's 2010 bundle exists. If NY's CPI 2015 published score was measured against the 2015 statute (likely), 2010 isn't useful for this dispatch. Skip unless Dan explicitly wants it.

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

1. Read this plan end-to-end.
2. Read [`convos/20260605_phase_a_execution.md`](../convos/20260605_phase_a_execution.md) end-to-end (immediate Phase A baseline; A2.b dispatch shape; TDD discipline; the dispatcher `_RESOLVED_CHUNKS` extension).
3. Read [`convos/20260605_cross_state_planning.md`](../convos/20260605_cross_state_planning.md) (this plan's originating convo — captures Dan's 10-state pick + vintage 2015 + CPI projection metric + the $10 envelope decision).
4. Read `docs/historical/compendium-source-extracts/results/projections/cpi_2015_c11_projection_mapping.md` end-to-end — needed to resolve Open Question #1 and to confirm the per-state projection scoring rules.
5. Read `src/lobby_analysis/projections/cpi_2015_c11.py` + the 3 test files — confirm projection function's API + tolerance convention.
6. Verify P1, P2, P3, P4 above. If any prereq is unmet (most likely P1: v2.1 not yet merged to main), **stop and surface to Dan**.
7. Surface Open Question #1 to Dan with the corrected projection-coverage counts. **Wait for Dan's call on chunk set** before dispatching.
8. Begin TDD per `skills/test-driven-development/SKILL.md`:
   - RED batch: tests asserting results JSONs exist per (state, vintage); zero unhandled errors; per-state projection score within tolerance for at least N of 10 states (N = TBD with Dan — could be 7, 8, 9, etc., or "no enforced threshold; document the result").
   - GREEN batch: dispatch loop + audit script.
9. After X1 dispatch lands: run X2 audit; if any state fails tolerance, surface diagnosis to Dan before X3.
10. Finish-convo: walk the doc-link-graph before commit.

---

## Next-session handoff sentence

*"Pick up the successor branch cut off main (`cross-state-cpi-2015-validation` or similar) after v2.1 + Phase A YAML merge from wi-ralph-cpi-renewal-cadence. Read this plan end-to-end (now living on main at `docs/historical/wi-ralph-cpi-renewal-cadence/plans/20260605_cross_state_cpi_2015_validation.md`), plus the Phase A execution convo. Cross-state CPI 2015 C11 projection validation: 10 states (NY, CO, WI, CA, TX, IL, WA, FL, NC, OH) × vintage 2015 × Phase A validation subset (or swap per Open Q #1). Fresh $10 envelope; ~$8.30 dispatched + $1.70 headroom. Primary metric: CPI 2015 C11 projection accuracy per state; secondary: instantiation rate + cross-state value-stability matrix. Open Q #1 (`actor_registration_required` → `registration_mechanics_and_exemptions` swap) is the most important pre-dispatch question — surface to Dan with corrected projection-coverage counts before any spend."*
