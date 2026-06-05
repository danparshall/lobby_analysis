# 2026-06-05 (latest) — Cross-state expansion planning: 10-state target locked (NY/CO/WI/CA/TX/IL/WA/FL/NC/OH); vintage 2015; CPI 2015 C11 projection-accuracy as primary success metric; v2.1-to-main merge gates dispatch; fresh $10 envelope

**Plan:** [`../plans/20260605_cross_state_cpi_2015_validation.md`](../plans/20260605_cross_state_cpi_2015_validation.md)
**Predecessor:** [`20260605_phase_a_execution.md`](20260605_phase_a_execution.md) (Phase A done-criteria 5/6 met on WI; cross-state expansion is the natural next research line)
**Execution session:** TBD on a successor branch (`cross-state-cpi-2015-validation` or similar) cut off main AFTER v2.1 + Phase A YAML merge from this branch

## Pre-flight

Read STATUS.md (Compendium 2.0 success criterion ⭐ + Current Focus), README.md (research question + project state), this branch's RESEARCH_LOG.md end-to-end (all 9 prior session entries, oldest of which is the 2026-06-04 Phase B kickoff). Then read the handoff-named docs: `convos/20260605_phase_a_execution.md` + `convos/20260605_phase_a_kickoff.md` + `plans/20260605_phase_a_yaml_audit_at_scale.md` end-to-end. Confirmed Phase A landed structurally; cross-state expansion is the obvious continuation.

This session is **planning + finish-convo only** per the Nori flow plan-then-fresh-session memory (load-bearing for the last 3 sessions in a row). No API spend, no YAML/code edits — only doc-graph and plan-doc work.

## Empirical findings produced this session (before questions)

1. **Statute bundle availability check** via `/tmp/check_statute_bundles.py`: all originally-named 15 states (AK, AR, CA, CO, FL, IL, MA, MI, NC, OH, PA, TX, WA, WI, WV) × 2015 + 2025 have `data/statutes/<STATE>/<VINTAGE>/sections/` populated. **NY ALSO has 2015 + 2025 bundles** — contradicting the handoff's "NY+WY 2010-only" claim. WY remains 2010-only.
2. **Cost math against $5 wi-ralph ceiling** — the A2.b WI baseline ($0.83 for 3 chunks / 21 cells) extrapolates to $75-90 for 6-default-chunks × 30 SVs ($-90 for 7 chunks); structurally an order of magnitude over the wi-ralph $1.49 remaining. New envelope is the load-bearing input.
3. **CPI 2015 C11 projection operational on main** — confirmed `src/lobby_analysis/projections/cpi_2015_c11.py` + 3 test files (`tests/projections/test_cpi_2015_c11_{aggregation,ground_truth,per_item}.py`) + oracle CSV at `docs/historical/compendium-source-extracts/results/cpi_2015_c11_per_state_scores.csv` + projection mapping doc. All 50 states + DC in oracle, so all 10 target states covered.
4. **Coverage gap surfaced** in the 3-chunk validation subset relative to CPI 2015 C11: `actor_registration_required` (~48% of per-state spend) does NOT feed any CPI 2015 C11 indicator — it's PRI/FOCAL-anchored. The chunks that DO feed CPI projection are `registration_thresholds` + `enforcement_and_audits` (~52% of subset spend) plus `registration_mechanics_and_exemptions` + `lobbyist_spending_report` (not in subset). Flagged as Open Question #1 in the new plan — the highest-leverage swap consideration for the execution session.

## Decisions confirmed with Dan mid-session

**Dan course-corrected my initial framing in two important ways:**

1. **State scope.** I had carried the handoff's 15-state framing into my first set of questions. Dan replied: *"after researching data availability, our top-ten states are: NY CO WI CA TX IL WA FL NC OH. Let's be sure to update our docs, and make that the target for Ralph."* This drops 5 states (AK, AR, MA, MI, PA, WV) and adds NY (whose 2015/2025 bundles do exist contrary to handoff). Order preserved as Dan listed (likely priority/data-quality-ordered, not alphabetical).

2. **Vintage.** I had defaulted to 2025 (more current) in the breadth-first scope-shape option. Dan answered the success-metric question with *"do vintage 2015 and apply the CPI"* — overriding my 2025 default. This is internally coherent: CPI 2015 is the published rubric oracle, so to use it as ground truth for projection accuracy, we extract at the 2015 vintage CPI scored. Sharpens the plan substantially.

**Locked via AskUserQuestion (4 questions):**

1. **Budget:** Fresh $10 envelope for cross-state work, atop wi-ralph's $3.51. (NOT a raised cumulative wi-ralph ceiling.)
2. **Scope shape:** Breadth-first — 1 vintage × all 10 states, 3-chunk validation subset (matching Phase A's A2.b touched chunks).
3. **v2.1 propagation:** Merge v2.1 TSV + YAML additives to main BEFORE cross-state dispatch. Successor branch cut off main for execution.
4. **Success metric:** Apply CPI 2015 C11 projection per state; compare to published oracle. Secondary metrics (per-state instantiation rate + cross-state value-stability matrix) computed as free byproducts.

## What happened (chronological)

1. **Pre-flight reads** — STATUS, README, RESEARCH_LOG, handoff-named docs (Phase A kickoff + execution convos + plan), chunks_v2 manifest, dispatcher script `_DEFAULT_CHUNKS` + `_RESOLVED_CHUNKS` definitions.
2. **Statute bundle availability check** via `/tmp/check_statute_bundles.py` (Write-then-run pattern, no chains). Surfaced NY 2015/2025 availability — handoff was incorrect.
3. **Cost math projection** from existing A2.b per-chunk cost data: 6 default × 30 SVs = ~$75-90, 7 chunks = ~$90-105, validation-subset 3 chunks × 30 SVs = ~$25. New envelope required.
4. **First AskUserQuestion** (4 questions: chunk set, cost ceiling, v2.1 propagation, success metric) — surfaced findings + math up front.
5. **Dan interrupted with the 10-state correction + $10 ceiling.** Re-cast question framing with the corrected state set + $10 budget tension (3 × 20 SVs = $16.6, doesn't fit).
6. **Second AskUserQuestion** (4 questions: budget interpretation, scope shape, v2.1 propagation, success metric). Dan picked fresh $10 + breadth-first + merge v2.1 + CPI projection metric. Also override-pinned vintage 2015.
7. **CPI 2015 projection coverage check** on main: confirmed projection module + oracle CSV both ship. Two of three validation-subset chunks feed CPI projection; flagged the actor_registration_required → registration_mechanics_and_exemptions swap as the execution-session's highest-leverage open question.
8. **Wrote the plan** at `plans/20260605_cross_state_cpi_2015_validation.md`: 10-state × vintage 2015 × 3-chunk validation subset × CPI 2015 projection metric; v2.1 promotion to main as prerequisite P1; successor-branch cut off main for execution; Open Question #1 documents the chunk-vs-projection-coverage tension for the implementing agent.

## Findings (load-bearing)

### 1. The $10 envelope + 20-SV target leaves $1.70 headroom — tight but feasible
At ~$0.83 per state-vintage for the 3-chunk validation subset, 10 states × 1 vintage = ~$8.30 dispatched + $1.70 headroom for re-runs / single-row Ralph follow-ups on any outlier state. Vintage 2025 deferred to a follow-up run with a separate budget.

### 2. Open Question #1 (the chunk swap) is genuinely consequential
If kept as-is, ~48% of the dispatch budget ($0.40/state × 10 = $4) goes to a chunk that contributes 0 to the primary success metric. Swapping `actor_registration_required` → `registration_mechanics_and_exemptions` shifts to ~95% of the budget feeding CPI projection at lower total cost ($0.73/state × 10 = $7.30, $2.70 headroom). Loss: the BinaryCell cross-state template test gets deferred. Plan flags this as the execution session's first decision to surface to Dan, with corrected per-chunk projection-coverage counts.

### 3. NY scope correction is a substantive data-availability finding
The handoff said NY was 2010-only; the `/tmp/check_statute_bundles.py` run showed NY has 2010 + 2015 + 2025 bundles all with `sections/` populated. Dan's top-10 list includes NY, so this aligns; but the handoff's claim was empirically wrong. Worth noting if a future agent reads the handoff and treats NY's exclusion as authoritative.

### 4. The Nori-flow boundary held cleanly for a third consecutive session
This session was planning + finish-convo only. No code, no YAML, no API spend. The slide-into-execution pattern that caught me in the prior two sessions (and that Dan caught the second time) didn't fire here — the planning artifacts (statute bundle check, CPI projection module existence verification, cost math) stayed within "evidence to support the plan" and did not creep into execution-prep. Memory entry `[[nori-flow-plan-then-fresh-session]]` continues to be load-bearing.

## Cost ledger

| Item | Cost |
|---|---|
| Pre-flight reads | $0 |
| `/tmp/check_statute_bundles.py` (statute bundle availability check) | $0 |
| CPI 2015 C11 projection module + oracle existence verification (git ls-tree) | $0 |
| Plan write + 2 AskUserQuestion rounds + this convo | $0 |
| **This session subtotal** | **$0** |
| **wi-ralph cumulative** | **$3.5127** (unchanged; against $3-5 → revised-to-$10 ceiling per cross-state envelope being SEPARATE; this branch's ceiling unchanged) |
| **Cross-state envelope (fresh)** | **$0 of $10** (this is the new budget tag for the successor branch) |
| wi-tier1-direct-read cumulative | $7.2946 (unchanged) |
| **Grand total WI Phase 1/2 + Phase B + Phase A** | **$10.8073** (unchanged) |

## Artifacts produced

- **New plan:** [`../plans/20260605_cross_state_cpi_2015_validation.md`](../plans/20260605_cross_state_cpi_2015_validation.md) (self-contained for cold pickup on the successor branch; locks 6 decisions; documents 4 prerequisites; surfaces 4 open questions for execution session)
- **This convo:** [`20260605_cross_state_planning.md`](20260605_cross_state_planning.md) ← here
- **Session artifact (preserved in /tmp):** `/tmp/check_statute_bundles.py` — re-runnable; produces per-state vintage availability table including the `sections/` directory presence flag.
- **No code, no YAML, no API spend.**

## Decisions locked

(All 6 documented in the plan's §"Decisions locked this session." Compressed here for the convo record:)

1. **D1 Target state list:** NY, CO, WI, CA, TX, IL, WA, FL, NC, OH (10 states; Dan's order; supersedes handoff's 15-state list).
2. **D2 Vintage:** 2015 single-vintage this round. Vintage 2025 deferred to a follow-up.
3. **D3 Chunk set:** Phase A validation subset (actor_registration_required + registration_thresholds + enforcement_and_audits) — see Open Question #1 in plan for the chunk-vs-projection-coverage tension.
4. **D4 Primary success metric:** CPI 2015 C11 projection accuracy per state.
5. **D5 v2.1 promotion to main:** BEFORE cross-state dispatch. Successor branch cut off main.
6. **D6 Budget envelope:** Fresh $10 for cross-state, atop wi-ralph $3.51.

## Open questions surfaced this session

(All 4 documented in the plan's §"Open questions for execution session." Compressed here:)

- **#1 (highest-leverage):** Should the chunk set swap `actor_registration_required` → `registration_mechanics_and_exemptions`? Surface to Dan at execution time with corrected per-chunk CPI 2015 projection-coverage counts (per `cpi_2015_c11_projection_mapping.md`). Difference: ~52% vs ~95% of dispatch budget feeding the primary metric.
- **#2:** Tolerance convention for "projected score matches published CPI 2015." Read existing test fixtures; if no convention, propose ±10 points.
- **#3:** What does the implementing agent do if any state's instantiation error rate exceeds Phase A's 0% baseline? Default in plan: pause + surface to Dan at >5% per state. Implementing agent may push back.
- **#4:** Should NY 2010 also be in scope? Skip unless Dan explicitly wants it — CPI 2015 oracle measures against the 2015 statute.

## Session meta — Dan's two course-corrections held the design together

The first AskUserQuestion presupposed the handoff's 15-state framing. Dan immediately replied with the corrected 10-state list + the $10 ceiling — both substantively different from the handoff's assumptions. The second AskUserQuestion absorbed the corrections cleanly and let the design land in 4 locked decisions + 4 open questions for execution. The vintage-2015 override on the success-metric question was a separate sharpening — coherent with applying CPI 2015 as the primary metric. Without those two corrections the plan would have shipped wrong (wrong states + insufficient budget for the original 30-SV target + wrong vintage for the CPI oracle).

## Next-session handoff sentence

*"Pick up the successor branch (`cross-state-cpi-2015-validation` or similar) AFTER v2.1 + Phase A YAML merge from wi-ralph-cpi-renewal-cadence to main. Read `docs/historical/wi-ralph-cpi-renewal-cadence/plans/20260605_cross_state_cpi_2015_validation.md` end-to-end (plan will live in historical once wi-ralph archives) + this convo + the Phase A execution convo for full context. Cross-state CPI 2015 C11 projection-accuracy validation: 10 states (NY/CO/WI/CA/TX/IL/WA/FL/NC/OH) × vintage 2015 × Phase A validation subset (PENDING Open Q #1 — surface the chunk swap to Dan with corrected projection-coverage counts BEFORE any dispatch). Fresh $10 cross-state envelope; ~$8.30 dispatched + $1.70 headroom; primary success metric = CPI 2015 C11 projection accuracy per state (oracle CSV at `docs/historical/compendium-source-extracts/results/cpi_2015_c11_per_state_scores.csv`); secondary = instantiation rate + cross-state value-stability matrix. v2.1 promotion to main is prerequisite P1 — pause if not yet merged."*

---

## Appendix — Finish-branch skill (PR to main)

Dan asked to run `skills/finishing-a-development-branch/SKILL.md` after the planning + finish-convo landed. Walking through the 11 steps captured the wi-ralph → main PR work as part of this session.

### What this PR contains

- **wi-tier1-direct-read** (absorbed via merge `b4cc986` earlier; never PR'd separately) — WI 2025 paid run + YAML SSOT + opaque-handle renderer.
- **v2.1 compendium schema bump** (Pattern C row split, 183 rows).
- **Phase A YAML audit at scale** (163 additives + dispatcher refactor + 167 new tests).
- **Cross-state expansion plan** (this session's planning artifact).

PR diff: 239 files / +89k / −279. ~80k of insertions are dispatch result JSONs (per-cell API outputs), not code.

### Skill-step results

1. **Tests:** `uv run pytest -q` → 1851 passed, 3 skipped, 3 xfailed. Matches Phase A execution baseline.
2-4. **Ruff format/lint:**
   - `ruff format --check .` would reformat **112 files**, but only ~12 are in this branch's diff. The remaining ~100 are pre-existing format issues on main.
   - `ruff check .` reports 28 lint errors on main; 6 of them in `scripts/tier_0_direct_read_smoke.py` lines 286-291 (deliberate "single-file by design" pattern per the file's own comment).
   - **Decision:** Don't auto-fix. Touching 100+ shared files outside this branch's scope violates the multi-committer norm and bloats an already-huge PR. Surfaced in PR description as pre-existing-not-regressed state.
5. **Type checking:** No mypy/pyright/ty configured in `pyproject.toml`. Skipped.
6. **nori-code-reviewer self-review:** 4 findings; 3 fixed pre-PR (commit `9a22232`):
   - **#1 ✅** Misleading "Filtered to N of M chunks" log line in default dispatch (compared against `_RESOLVED_CHUNKS` instead of "did user pass --chunks?"). Cosmetic UX fix; logic unchanged.
   - **#2 ⏭️** 50/151 BinaryCell prompts have grammar awkwardness from bulk-script concatenation (rubric source quotes lack terminal punctuation). Deferred to follow-up Ralph pass per reviewer's own recommendation. The LLMs grok it (Phase A A2.b: 66/66 BinaryCell cell-instantiations on `actor_registration_required`).
   - **#3 ✅** Stale docstrings/prose in `compendium_loader.py`, `models_v2/cell_spec.py`, `tests/test_models_v2_cell_spec.py` referencing v2 (181 rows) — updated to v2.1 (183 rows) with Pattern C context.
   - **#4 ✅** "5 known combined-axis rows" prose with 3-element set fixed to "3 known combined-axis rows (down from 5 in v2)". Assertion was already correct.
7. **Not on main:** Confirmed on `wi-ralph-cpi-renewal-cadence`.
8. **Push + PR:** in progress.
9-11. **Merge main, CI, review comments:** TBD post-PR-creation.

### Why the PR is so large (and what to do about it next time)

239 files is a single-PR scope problem. The root cause is that `wi-tier1-direct-read` was merged INTO wi-ralph (via `b4cc986`) but never PR'd to main first — wi-tier1's work then rode along with wi-ralph's Phase B + Pattern C + Phase A work. By the time finish-branch ran, the combined scope was unwieldy.

**Lesson for future branches:** if a research line absorbs another via merge, PR the absorbed line to main BEFORE adding more layered work, so the eventual final PR has a clean scope. This pattern isn't pervasive — most prior branches merged to main in their own time — but the wi-tier1 case slipped through.

Not retroactively splittable here (history is what it is), but worth noting for the cross-state successor branch: PR each meaningful scope-unit separately, don't let absorbed-branch debt accumulate.
