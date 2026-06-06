# Plan — Pre-dispatch hygiene + 5-state CPI-2015 C11 extension

**Originating analysis:**
- [`../results/20260606_failure_mode_trends_and_paths_forward.md`](../results/20260606_failure_mode_trends_and_paths_forward.md) — Round 1 N=5 failure-mode trends. Path 1 = helper-side vocab fix; Path 2-modified = 5-state extension; this plan combines them.
- [`../results/20260606_cpi_2015_c11_chunk_inventory.md`](../results/20260606_cpi_2015_c11_chunk_inventory.md) — structural inventory of the 6 default chunks; identifies the 11 underspecified prompts.
- Originating convo: [`../convos/20260606_pre_dispatch_review.md`](../convos/20260606_pre_dispatch_review.md).

**Cross-branch context:**
- [`../../leave-behind-prep/convos/20260606_take_stock_and_day1_hygiene.md`](../../leave-behind-prep/convos/20260606_take_stock_and_day1_hygiene.md) — the 5-day Fellowship-end plan. This plan executes Day 2.
- [`../../../historical/wi-ralph-cpi-renewal-cadence/plans/20260605_cross_state_cpi_2015_validation.md`](../../../historical/wi-ralph-cpi-renewal-cadence/plans/20260605_cross_state_cpi_2015_validation.md) — the originating cross-state plan (5 states × default-6-chunks × per-(state, indicator) de-jure exact-match). Round 1 executed; this plan extends to N=10.

**Branch:** `cross-state-cpi-2015-validation`
**Worktree:** `/Users/dan/code/lobby_analysis/.worktrees/cross-state-cpi-2015-validation`
**Estimated total cost:** ~$15 dispatch + 0 (hygiene phases) = **~$15**
**Estimated total time:** 1 working session (the hygiene phases are <60 min each; the dispatch is async)

---

## Why this plan exists (the question it's answering)

Round 1 (5 states × 6 chunks × 2 models × 3 runs = 180 dispatches) hit 50% per-(state, indicator) match rate. The failure-mode analysis identified two surgical pre-dispatch hygiene items that could land before re-dispatching on the next 5 states:

- **(c) Helper-side vocab schism fix** — Path 1 / Step 1 from the failure-mode doc. ~30 min, $0. Mechanically collapses 9 of 15 Round 1 misses without re-dispatch; required to make the Round 1 baseline interpretable. Tracked in failure-mode doc as the "cheap bolt-on."
- **(b) Underspecified-prompt cleanup** — surfaced by the chunk inventory's prompt-audit pass. 11 prompts lack explicit response-format clarification. ~30–60 min, $0. Forward hygiene only — these prompts didn't cause documented Round 1 failures, but weaker prompts are higher risk on unfamiliar states.

Dan asked (this session) for a plan that does **(b) + (c) then dispatch**. This is a hybrid of Path 1 and Path 2-modified that addresses both leverage points before spending the $15.

The implementing agent (next session) should already have re-read the failure-mode doc and the chunk inventory before starting. The §Pre-execution checklist at the bottom of this plan gates that.

---

## Risks & open caveats (read before committing)

1. **Phase 2 changes the experimental input mid-experiment.** The 11 prompts get rewritten between Round 1 (NY/WI/OH/CA/TX) and Round 2 (CO/IL/WA/FL/NC). For the underspecified-prompt cells, Round 1 vs Round 2 will not be on identical prompts.
   - **Why we're doing it anyway:** Round 1 documented failures were YAML-correct + helper-wrong (vocab schism), not "prompt was unclear." So the new prompts shouldn't change accuracy on those cells, only σ_noise (and only on the 11 affected cells). The clarification is intended to be **semantics-preserving**, not behavior-changing.
   - **Mitigation:** Phase 2's TDD discipline requires showing test green before AND after on the cells touched. The implementing agent must confirm semantics-preservation via diff review with Dan before committing the prompt YAML.
   - **Exit ramp:** if Phase 2 review uncovers any prompt where the clarification might shift answers, skip that one prompt and document.

2. **Phase 1 helper changes mean Round 1 stored cells get re-projected.** The audit machinery (`scripts/cross_state_cpi_2015_audit.py`) reads the stored YAML extractions + re-projects via current helpers. After Phase 1, re-running the audit on Round 1 data produces a **new** Round 1 match rate — the +4 prediction in the failure-mode doc lands.
   - **This is desirable** — it disambiguates "Round 1 baseline is 50%" (pre-fix) vs "Round 1 baseline is ~63% if you fix the vocab schism" (post-fix). The implementing agent should re-run the Round 1 audit between Phase 1 and Phase 4 and record both numbers.

3. **No state-agnostic refactor.** Per the leave-behind-prep convo's Anna Karenina reframing, this plan stays inside the CPI-2015 C11 projection module + the prompt SSOT YAML. No "let's generalize the projection pattern" tangent.

4. **Provider config unchanged.** Round 1 used `claude-opus-4-7` + `gpt-5.2-2025-12-11`. Round 2 uses the same two models, same chunk shape (default 6), same 3 runs. If Dan wants to drop a provider (halves cost), surface that before Phase 4.

5. **Cost overrun guard.** Round 1 cost $14.43 of a $15 envelope. Round 2 expected $13–18. The instantiation-error pause threshold is 5%; if any state's first 2 chunks blow past that, halt and surface.

---

## Phase 1 — Helper-side vocab schism fix ($0, ~30 min)

**Goal:** make the IND_199 and IND_207 projection helpers accept the YAML-extracted vocabulary (CPI's published "YES"/"MODERATE"/"NO" + IntCell months). Removes the 9-of-15 Round 1 misses that were extraction-correct but helper-misaligned.

**Files touched:**
- `src/lobby_analysis/projections/cpi_2015_c11.py` — `project_ind_199` (lines 167–178) and `project_ind_207` (lines 275–282).
- `tests/projections/test_cpi_2015_c11_ground_truth.py` — add per-(state, indicator) regression tests against Round 1 stored extractions where the post-fix expected score is known.

### TDD sequence

1. **RED** — write a failing test against Round 1 stored extractions:
   - For each of {NY, WI, OH, CA} on IND_199 with `lobbyist_registration_renewal_cadence = 24` (months): expect `project_ind_199(cells) == 50` (MODERATE). Currently returns 0 (NO) because the helper compares the int to the string `"biennial"`.
   - For NY on IND_207 with `lobbying_disclosure_audit_required_in_law = "YES"`: expect `project_ind_207(cells) == 100`. Currently returns 0 because the helper compares `"YES"` to `"regular_third_party_audit_required"`.
   - Run pytest, confirm 2 RED.

2. **GREEN** — update the two helpers to accept the YAML vocabulary:

   **`project_ind_199`** (current code reads cadence as enum strings `"annual"`, `"more_frequent_than_annual"`, `"biennial"`, `"less_frequent_than_biennial"`):
   ```python
   def project_ind_199(cells: dict[str, Any]) -> int:
       cadence = _legal(cells, "lobbyist_registration_renewal_cadence")
       if cadence is None:
           return 0
       # YAML extracts IntCell months (statute-literal); 0 = "no renewal".
       if isinstance(cadence, int):
           if cadence == 0:
               return 0
           if cadence <= 12:
               return 100
           if cadence <= 24:
               return 50
           return 50  # biennial-or-less stays MODERATE per CPI rubric
       # Legacy string-enum path retained as a fallback for older fixtures.
       if cadence in ("annual", "more_frequent_than_annual"):
           return 100
       if cadence in ("biennial", "less_frequent_than_biennial"):
           return 50
       return 0
   ```

   **`project_ind_207`** (current code reads enum `"regular_third_party_audit_required"` / `"audit_only_when_irregularities_suspected_or_compliance_review"`):
   ```python
   def project_ind_207(cells: dict[str, Any]) -> int:
       rule = _legal(cells, "lobbying_disclosure_audit_required_in_law")
       if rule is None:
           return 0
       # YAML enum domain (CPI vocab): YES / MODERATE / NO.
       if rule in ("YES", "regular_third_party_audit_required"):
           return 100
       if rule in ("MODERATE", "audit_only_when_irregularities_suspected_or_compliance_review"):
           return 50
       return 0  # "NO" or any other string
   ```

   **Why both vocabularies retained:** existing test fixtures may carry the legacy string-enum domain. Dropping the legacy keys would break those tests without surfacing a real regression.

3. **Re-run pytest.** All `tests/projections/test_cpi_2015_c11_ground_truth.py` green; full suite (~14 tier_1 tests + projection suite) green.

4. **Re-audit Round 1 stored data.** Run `scripts/cross_state_cpi_2015_audit.py` against the existing Round 1 results dir. Expected new match rate per failure-mode doc Trend 1: `15 → 19 / 30` (50% → ~63%). Capture the new Table A in the §Phase 5 writeup.

### Acceptance gate

- Pytest fully green.
- Round 1 re-audited match rate ≥ 60% (the predicted ~63%, with 1-cell margin).
- Helper changes are diff-reviewable in <50 lines.
- Commit message: `phase 1 vocab fix: IND_199 IntCell-months + IND_207 CPI-enum domains; round 1 re-audit X/30 (was 15/30)`

---

## Phase 2 — Underspecified-prompt cleanup ($0, ~45 min)

**Goal:** add explicit response-format clarification to the 11 prompts identified in the chunk-inventory report §4. Semantics-preserving — the model's expected answer doesn't change, only the prompt's explicit-ness.

**Files touched:**
- `compendium/source_quotes.yaml` — 11 prompt entries (see chunk inventory §4 for the full list).
- `tests/<wherever the YAML-load tests live>` — add a regression that all 93 default-chunk prompts contain at least one format-clarification token from a small whitelist.

### TDD sequence

1. **RED** — write a failing test in a new file `tests/test_default_chunk_prompts_have_format_hints.py`:
   ```python
   def test_default_chunk_prompts_have_format_hints():
       """Every cell in the 6 CPI 2015 C11 default chunks must have a prompt
       that explicitly states the response format."""
       FORMAT_KEYWORDS = (...)  # exact list from the audit
       chunks = {c.chunk_id: c for c in build_chunks()}
       offenders = []
       for cid in DEFAULT_CHUNKS:
           for cs in chunks[cid].cell_specs:
               if not any(kw.lower() in (cs.prompt or "").lower() for kw in FORMAT_KEYWORDS):
                   offenders.append((cs.row_id, cs.axis))
       assert not offenders, f"{len(offenders)} prompts lack format hint: {offenders}"
   ```
   - First run: 11 offenders. Test RED.

2. **GREEN** — edit `compendium/source_quotes.yaml`. Add a single closing sentence to each of the 11 prompts that names the expected return shape. Templates:

   - **BinaryCell prompts (Group 2 partial — `lobbyist_registration_required` L):** append `Answer with the boolean value true or false.`
   - **IntCell prompts (Group 2 + Group 3, e.g. `lobbyist_registration_amendment_deadline_days`):** append `Answer with a non-negative integer number of days.` (or `months`, depending on the cell)
   - **GradedIntCell prompts (Group 2 — the 4 practical cells + 1 legal):** append `Answer with one of: 0, 25, 50, 75, 100.`
   - **FloatCell prompts (Group 1 — `lobbyist_filing_de_minimis_threshold_time_percent`):** append `Answer with a non-negative float (percent, 0 to 100). Use null if no such threshold exists in statute.`
   - **TimeThresholdCell prompts (Group 1 — `lobbyist_registration_threshold_time_percent`):** append `Answer with the time-percent as a non-negative float (0 to 100). Use null if no time-based threshold exists in statute.`
   - **FreeTextCell prompts (Group 1 — the two `_cadence_other_specification` rows):** append `If the statute specifies a non-standard cadence (i.e., not annual/semiannual/quarterly/monthly/biennial/triannual), answer with a short free-text description of that cadence. Otherwise, return null.`

3. **Diff review with Dan before commit.** Show the 11 prompt diffs. Confirm each is semantics-preserving.

4. **Re-run pytest.** Test green. Full suite still green.

### Acceptance gate

- Pytest green including the new prompt-hint test.
- Diff review with Dan complete; any contested prompt skipped + documented.
- Commit message: `phase 2 prompt hygiene: add response-format hints to 11 default-chunks prompts; new test guards against regression`

---

## Phase 3 — Round 1 re-audit checkpoint ($0, ~5 min)

**Goal:** capture the post-Phase-1 Round 1 baseline before Round 2 dispatches.

### Sequence

1. Run `python scripts/cross_state_cpi_2015_audit.py` against the Round 1 `tier_1_results_v2/` directory (or wherever Round 1 outputs live — check the trends doc).
2. Capture Table A (per-cell) + Table B (per-state) post-fix into a new section of the Round 1 results doc: `../results/20260605_cross_state_cpi_2015_validation.md` — under a new heading `## Post-Phase-1 re-audit (2026-06-06)`.
3. Confirm the new headline: predicted 19/30 (63%) per the failure-mode doc Trend 1.
4. If actual ≠ predicted within ±1 cell: pause and investigate. The plan assumed only IND_199 + IND_207 were affected; an unexpected delta would indicate other helpers also depend on the changed vocabulary.

### Acceptance gate

- Round 1 post-fix match rate captured + committed.
- Phases 1+2 commits pushed to origin.

---

## Phase 4 — 5-state Round 2 dispatch (~$13–18, async)

**Goal:** dispatch CO, IL, WA, FL, NC at vintage 2015, default-6-chunks shape, identical to Round 1 except for the Phase 1+2 hygiene deltas.

### Sequence

1. **State-bundle pre-flight.** For each of CO/IL/WA/FL/NC, confirm `data/statutes/<STATE>/2015/sections/` exists and has the expected file shape. (TX 2015's Round 1 over-projection was traced to a 1-file bundle in Trend 4 of the failure-mode doc — check whether any of the new 5 states have similarly thin bundles before dispatching, so we know what to expect.)

2. **Anchor first, then parallel.** Round 1's NY-first cost anchor worked well — NY came in at $2.83 with no instantiation errors above threshold. For Round 2, pick the state with the smallest bundle as the anchor (most likely to surface dispatch-shape issues early) and dispatch it first. If anchor stays under $4 and instantiation errors stay under 5%, dispatch the other 4 in parallel via 4 separate Bash calls.

3. **Dispatch command per state** (no `--chunks` flag — uses the 6 defaults):
   ```bash
   uv run python scripts/tier_1_direct_read_legal_axis.py --state CO --vintage 2015 --results-base docs/active/cross-state-cpi-2015-validation/results/tier_1
   ```
   Repeat per state.

4. **Mid-dispatch monitoring.** Each state writes per-dispatch checkpoint JSONs; the dispatcher prints cumulative cost + error counts. If any state exceeds:
   - Cost > $4.50 single-state, OR
   - Instantiation errors > 5% (>= 2 of 36 dispatches on a single state)
   - then **halt that state's run** and surface to Dan with the actual numbers.

5. **Cost envelope check.** Round 1 closed at $14.43 of $15. Round 2 envelope is ~$15 same. If running total approaches $18, pause before launching the last state.

### Acceptance gate

- All 5 states' dispatches complete (36 dispatches each, 180 total).
- Per-state instantiation error rate ≤ 5%.
- Total Round 2 cost ≤ $18 (any overrun documented).
- All results land in state-keyed result dirs under `docs/active/cross-state-cpi-2015-validation/results/tier_1/<STATE>_2015/`.

---

## Phase 5 — Audit + writeup ($0, ~60 min)

**Goal:** audit all 10 states post-Phase-1, write up trends at N=10, mark the failure-mode doc resolved or supersede.

### Sequence

1. Run `scripts/cross_state_cpi_2015_audit.py` against all 10 states (Round 1 + Round 2).
2. Write `results/20260607_cross_state_cpi_2015_n10_results.md` (date will adjust):
   - Headline: N=10 per-(state, indicator) match rate
   - Per-indicator (10 states each): IND_196, 197, 199, 201, 203, 207
   - Per-state (6 indicators each): all 10 states
   - σ_noise range across both providers
   - Cost ledger across both rounds
3. Update the failure-mode doc with a header banner: `## Resolved at N=10 (2026-06-XX) — see [N=10 results doc]`. Specifically, validate or refute:
   - Trend 1 (vocab schism): ~63% predicted post-fix on Round 1 → expected ≥60% Round 2 on the same cells.
   - Trend 4 (TX sparse-corpus over-projection): test by checking whether any Round 2 state with a 1-file bundle also over-projects.
   - Trend 5 (CPI more generous on audits): test against Round 2's IND_207 distribution.
   - Trend 6 (cell-type schism): test by checking whether Round 2's pattern of (helper-output ≠ rubric-tier) mismatches reproduces.
4. Update `RESEARCH_LOG.md` with the N=10 entry.
5. Update repo-root `STATUS.md` row for this branch.
6. Finish-convo with full session capture.

### Acceptance gate

- N=10 results doc landed and linked from RESEARCH_LOG.
- Failure-mode doc updated with N=10 verdicts on each trend.
- This plan moved to a "completed" section at the bottom of itself with a brief outcome note.

---

## Pre-execution checklist (gating Phase 1 start)

The implementing agent (next session) should confirm all of these before writing the first test:

- [ ] Read this plan end-to-end.
- [ ] Read [`../results/20260606_failure_mode_trends_and_paths_forward.md`](../results/20260606_failure_mode_trends_and_paths_forward.md) end-to-end.
- [ ] Read [`../results/20260606_cpi_2015_c11_chunk_inventory.md`](../results/20260606_cpi_2015_c11_chunk_inventory.md) end-to-end.
- [ ] Read `src/lobby_analysis/projections/cpi_2015_c11.py` end-to-end (372 lines).
- [ ] Run pytest baseline — confirm current suite is green before changes.
- [ ] Confirm worktree is clean + on `cross-state-cpi-2015-validation` at HEAD.
- [ ] Confirm Round 1 results dir is present at `docs/active/cross-state-cpi-2015-validation/results/tier_1/<STATE>_2015/` for all 5 Round 1 states (NY/WI/OH/CA/TX).
- [ ] Confirm `data/statutes/{CO,IL,WA,FL,NC}/2015/sections/` exists for all 5 Round 2 states.
- [ ] Confirm `.env.local` has Anthropic + OpenAI API keys (Round 1 worked, so this should be set).
- [ ] Get explicit cost authorization from Dan for Phase 4 (~$15) before starting Phase 4. Phases 1–3 are $0 and don't need re-authorization.

---

## What's explicitly NOT in this plan (deferred)

- **Vintage 2025 dispatch** (Path 2's Step 2 in the failure-mode doc). Cross-vintage stability is a separate research question; deferred per failure-mode doc §"My recommendation."
- **v2.2 schema redesign** (Trend 6 — cell-type schism). The leave-behind-prep convo's SMR-as-canonical reframing turned this from "schema redesign" into "projection-translation engineering"; needs a separate plan downstream.
- **Per-row Ralph on the remaining 6 Round 1 misses** (Path 1 Step 3). Cheap (~$1–2) but only sensible against N=10 evidence; defer to Phase 5's writeup.
- **Single-provider dispatch** (cost halving). Would break cross-model σ_noise comparability with Round 1; flagged as a decision point but not adopted unless Dan says otherwise.
- **CO/IL/WA/FL/NC pipeline-shape exploration.** This plan assumes these 5 states' statute bundles are dispatch-ready. If pre-flight reveals a bundle isn't, that becomes its own pre-Phase-4 sub-plan.

---

## Cost summary

| phase | cost | time | scope |
|---|---:|---:|---|
| 1 — helper vocab fix | $0 | ~30 min | code + tests |
| 2 — prompt hygiene | $0 | ~45 min | YAML + new test |
| 3 — Round 1 re-audit | $0 | ~5 min | audit script |
| 4 — Round 2 dispatch | ~$13–18 | async (~30 min wall) | 180 dispatches |
| 5 — N=10 writeup | $0 | ~60 min | docs |
| **total** | **~$15** | **~3 hrs working + async** | one execution session |
