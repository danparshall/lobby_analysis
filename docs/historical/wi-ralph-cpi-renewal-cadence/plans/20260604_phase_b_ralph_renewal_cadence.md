# Phase B Ralph — Single-Row Iteration on `lobbyist_registration_renewal_cadence` (CPI 2015 IND_199) Implementation Plan

**Goal:** Run a first-row-by-hand Ralph iteration loop on a single CPI 2015 C11–readable compendium row, with the row's published per-state score as the external oracle, to surface what is and isn't tractable about Phase B before designing any automation.

**Originating conversation:** [`../convos/20260604_phase_b_kickoff.md`](../convos/20260604_phase_b_kickoff.md) (to be written when this branch's kickoff convo is finished). **Upstream lineage (this plan exists because of):** [`../../wi-tier1-direct-read/convos/20260604_wide_pass_commit3_redispatch_and_audit.md`](https://github.com/danparshall/lobby_analysis/blob/wi-tier1-direct-read/docs/active/wi-tier1-direct-read/convos/20260604_wide_pass_commit3_redispatch_and_audit.md) (Ralph brainstorm seeded) and [`../../wi-tier1-direct-read/convos/20260604_oracle_granularity_audit.md`](https://github.com/danparshall/lobby_analysis/blob/wi-tier1-direct-read/docs/active/wi-tier1-direct-read/convos/20260604_oracle_granularity_audit.md) (oracle confirmed = CPI 2015 C11, not PRI 2010). **Audit deliverable:** [`../../wi-tier1-direct-read/results/20260604_oracle_granularity_audit.md`](https://github.com/danparshall/lobby_analysis/blob/wi-tier1-direct-read/docs/active/wi-tier1-direct-read/results/20260604_oracle_granularity_audit.md).

**Context:** The wide-pass Commit 3 dispatch (2026-06-04 afternoon, on `wi-tier1-direct-read`) populated YAML prompts mechanically by lifting source-rubric scoring vocabulary verbatim. For 4 rows this created a vocabulary-vs-cell-type mismatch (CPI's `YES/MODERATE/NO` landed for IntCell rows; CPI's `100/50/0` landed for BinaryCell rows), causing 11 NEW instantiation failures vs the narrow-pass baseline. The Commit 3 brainstorm proposed a per-row Ralph loop **anchored to the introducing rubric author's published score as the external oracle**, rather than to inter-model agreement. The 9-rubric oracle-granularity audit (deferred from Commit 3, executed 2026-06-04 evening) then confirmed that **CPI 2015 C11 is the cleanest per-item × per-state oracle in the archive** (700 cells: 14 indicators × 50 states), and that `lobbyist_registration_renewal_cadence` is the right first row — clean failure mode, clean CPI oracle (IND_199, Wisconsin = MODERATE), and informative for the deferred Phase A pre-flight YAML audit because every fix Ralph requires on this row's YAML prompt is a fix Phase A will need to make on every other CPI-readable row with the same YES/MODERATE/NO ↔ IntCell mismatch.

**Confidence:** **Exploratory.** This is the first time we are running a Ralph-style row-level iteration anchored to a rubric oracle. Dan's framing for the session: *"even if we don't get it perfect, we might be able to learn a lot about what is/n't hiccuping by inference."* The deliverable is not converged extraction; the deliverable is empirical signal about (a) what the per-iteration human-in-the-loop step looks like in practice, (b) what kinds of prompt changes the model responds to, (c) whether convergence is achievable at all for this row with this oracle. Outcomes feed the automation-level decision and the Phase A pre-flight scope.

**Architecture:** Human-in-the-loop iteration. Each round = (1) inspect current YAML prompt for the target row; (2) inspect prior dispatch's result JSONs (claude + GPT, 3 runs each, single chunk `registration_mechanics_and_exemptions`); (3) decide what to change about the prompt (or whether to stop); (4) edit `compendium/source_quotes.yaml` in place; (5) re-dispatch just that one chunk via the existing `scripts/tier_1_direct_read_legal_axis.py`; (6) audit new results against the CPI IND_199 WI=MODERATE oracle; (7) log the iteration in a single results doc. No new dispatcher infrastructure built in this session; uses existing chunk-level dispatch.

**Branch:** `wi-ralph-cpi-renewal-cadence` (this worktree).

**Tech Stack:** Existing — Python 3.12 + uv, pytest + ruff for whatever code touch is required (probably none), YAML edits via direct file edit, dispatch via `uv run --env-file .env.local python scripts/tier_1_direct_read_legal_axis.py --state WI --vintage 2025 --models claude-opus-4-7 gpt-5.2 --runs 3`. API keys + dotenv via the symlinked `.env.local`.

---

## Pre-flight reads (for the implementing agent)

1. **This plan** — read end to end.
2. **The kickoff convo** at `docs/active/wi-ralph-cpi-renewal-cadence/convos/20260604_phase_b_kickoff.md` — sets the empirical priors and the budget conversation.
3. **The 9-rubric audit** at `docs/active/wi-tier1-direct-read/results/20260604_oracle_granularity_audit.md` (cross-branch reference via the wi-tier1-direct-read worktree at `/Users/dan/code/lobby_analysis/.worktrees/wi-tier1-direct-read/`, or via `git show wi-tier1-direct-read:docs/active/wi-tier1-direct-read/results/20260604_oracle_granularity_audit.md` from this worktree). **Especially the appendix** with WI's full 14-cell CPI oracle row.
4. **The Commit 3 audit at** `docs/active/wi-tier1-direct-read/results/20260604_wi_wide_pass_audit.md` — the instantiation-failure survey and the `lobbyist_registration_renewal_cadence` failure detail.
5. **The CPI 2015 C11 projection mapping** at `docs/historical/compendium-source-extracts/results/projections/cpi_2015_c11_projection_mapping.md`, specifically the IND_199 entry (line ~104) — what CPI's scoring rule actually means, and what the row's v2 cell type should accept as input.
6. **Current YAML state** at `compendium/source_quotes.yaml`, specifically the `lobbyist_registration_renewal_cadence` entry (verbatim CPI vocabulary, currently mis-landed against IntCell expectation).

---

## Target row, oracle, and starting state

- **Compendium row:** `lobbyist_registration_renewal_cadence`
- **Cell type:** `typed Optional[int_months] (or enum)` (from `compendium/disclosure_side_compendium_items_v2.tsv` line 105)
- **First-introduced-by:** CPI 2015 C11 (`cpi_2015_c11_projection_mapping.md`)
- **Rubrics reading the row:** `cpi_2015;hg_2007` (n_rubrics=2)
- **Oracle source:** CPI 2015 IND_199 ("In law, lobbyists are required to file a registration form on an annual basis")
- **Per-state oracle file:** `docs/historical/compendium-source-extracts/results/cpi_2015_c11_per_state_scores.csv` (cross-branch via wi-tier1-direct-read worktree)
- **Wisconsin's published value:** **MODERATE** (lobbyists must file but with less frequency than annual; WI §13.62 requires biennial renewal → CPI MODERATE)
- **Expected v2 cell value:** `magnitude=24, unit=months` (24 months = biennial, projects to CPI MODERATE under the scoring rule)
- **Current YAML prompt** (verbatim, as of commit `b73915e` on `wi-tier1-direct-read`):
  > *"A YES score is earned if lobbyists must fill out and file a registration form with the state government at least once a year. A MODERATE score is earned where lobbyists must fill out and file a registration form, but with less frequency. A NO score is earned if no such law exists."*
- **Known failure mode** (wide-pass Commit 3): Claude 3/3 instantiation failures — emits a `value` string like "MODERATE" or "YES" which IntCell rejects. GPT-5.2 emits a value but on the unit axis changed from `months` to `years` (24 months → 2 years; semantically equivalent biennial; cell-type may or may not accept).

---

## Operational mechanics

### Chunk identification

The target row lives in the **`registration_mechanics_and_exemptions`** chunk (verified by `grep -l "renewal_cadence" docs/active/wi-tier1-direct-read/results/tier_1/WI_2025/claude-opus-4-7__*__run1.json`). The chunk has ~12 legal cells (registration-mechanics rows). When dispatching, this is the only chunk we re-dispatch per iteration.

### Dispatch command (per iteration)

The existing dispatcher dispatches **all 6 chunks** by default. We need to limit it to one chunk. Inspect `scripts/tier_1_direct_read_legal_axis.py` for an existing `--chunks` flag or equivalent; if absent, two acceptable options:

- **Option A (cheapest, ~$0.05-0.10/iter):** add a `--chunks <chunk_id>` filter argument as a small 10-minute change. Single chunk × 2 models × 3 runs = 6 dispatches. ~$0.05-0.10 per iteration.
- **Option B (no code change, ~$0.30-0.40/iter):** dispatch all 6 chunks every iteration; only inspect the target chunk's outputs. Wastes 5 chunks' worth of compute (~$2/iter) but requires no script change. Acceptable for this exploratory session if Dan wants zero-code-touch.
- **Option C (manual single-row dispatch):** write a one-off `/tmp/single_row_dispatch.py` that loads just the target row + renders + calls one model + parses. Cleanest empirical signal but defers code work to a script-vs-not decision Dan hasn't made.

**Recommendation:** ask Dan to choose Option A or B at the start of the first iteration. The plan-level recommendation is **Option A** (small dispatcher tweak; per-iteration cost stays under $0.10), per Dan's $3-5 budget allowing ~10-30 iterations under A vs only 2-3 under B.

> **NOTE on the original brainstorm cost figure.** The Commit 3 convo cited "$0.05-0.07 × 2 models × 3 runs = ~$0.30-0.40 per iteration of a single row." That figure assumed Option C / single-row mechanism. Under Option B (full-chunk dispatch), each chunk averages ~$0.40-0.45 (per Phase 2 data: $2.5708 / 6 chunks). Total session cost under B = ~$2.50 × N iterations, very expensive.

### Iteration loop (manual, human-in-the-loop)

For each iteration `i = 0, 1, 2, ..., N`:

0. **(i = 0 only)** Inspect the current YAML prompt for the target row + the current cell type spec. Confirm the mismatch live (paste prompt + cell type + current Claude/GPT outputs from `_pre_wide_pass`/post-wide-pass JSONs to your scratchpad).

1. **Read state.** For iteration `i ≥ 1`, inspect the 6 result JSONs from iteration `i-1` for the target row only:
   - `results/tier_1/WI_2025/claude-opus-4-7__registration_mechanics_and_exemptions__run{1,2,3}.json`
   - `results/tier_1/WI_2025/gpt-5.2__registration_mechanics_and_exemptions__run{1,2,3}.json`
   - Look at the `cells` array entry where `row_id == "lobbyist_registration_renewal_cadence"`; record `value`, `errors`, `notes`.

2. **Compare against oracle.** Did the model emit a value the cell type accepted? If yes: does it project to CPI MODERATE? (i.e., `magnitude == 24` or any value in (12, 24] — see CPI's scoring rule: less-than-annual but ≥ once per N years for some N). If no: what specifically rejected it?

3. **Decide the change.** Three rough categories of fix:
   - **Vocab-strip:** delete the YES/MODERATE/NO language; replace with neutral cell-type-aligned question ("How many months between mandatory lobbyist re-registrations under WI law? Answer with an integer.").
   - **Vocab-bridge:** keep CPI's vocab as reference context but add explicit cell-type instruction ("CPI 2015 scored states YES/MODERATE/NO. Read WI's statute and answer in months: YES → 12, MODERATE → > 12, NO → null. Return an integer or null.").
   - **Citation-anchor:** add an explicit statute pointer ("WI §13.62 sets the renewal cadence; identify it and answer in months.").

4. **Edit the YAML.** Open `compendium/source_quotes.yaml`, find the `lobbyist_registration_renewal_cadence` entry, edit only the `prompt:` field (NOT `source_quotes` — that's the immutable reference material). Save.

5. **Re-dispatch.** Run the chunk dispatch (per Option A or B chosen above). Wait ~2-3 minutes for chunk completion.

6. **Audit + log.** Append a row to `results/20260604_renewal_cadence_iterations.md` (format below). Capture: iteration number, prompt-change summary, Claude 3-run outputs, GPT 3-run outputs, instantiation-pass count, oracle-match count, cost, qualitative notes.

7. **Stopping condition.** Stop if any of the following:
   - **(a) Convergence:** both models produce instantiation-passing values across all 3 runs, and the values project to CPI MODERATE on all 6 runs.
   - **(b) Budget hit:** cumulative this-session dispatch cost reaches $3-5 (per Dan's ceiling).
   - **(c) Dan calls it.** This is the default termination — first-row-by-hand means human judgment ends the loop.
   - **(d) Non-convergence pattern surfaced:** if after ~5 iterations the models are still rejecting the cell-type alignment for structural reasons (e.g., the cell type itself can't represent WI's renewal cadence, putting this in v2.2 schema fix territory), stop and document the structural finding.

### Results-logging format

Create `docs/active/wi-ralph-cpi-renewal-cadence/results/20260604_renewal_cadence_iterations.md` on the first iteration with a provenance header pointing to this plan + the kickoff convo. Per-iteration row schema:

```markdown
## Iteration N — YYYY-MM-DD HH:MM

**Prompt change from N-1:** [summary in 1-2 sentences]

**YAML prompt (verbatim):**
> [paste full prompt]

**Results (target row only):**
| Model | Run | value emitted | instantiation | projects to CPI? |
|---|---|---|---|---|
| claude-opus-4-7 | 1 | ... | pass/fail (reason) | MODERATE / mismatch / n/a |
| claude-opus-4-7 | 2 | ... | ... | ... |
| ... | ... | ... | ... | ... |

**Cost:** $X.XX (cumulative: $Y.YY)

**Notes:** [what we learned this iteration]
```

End the doc with a **session summary** when stopping — what converged, what didn't, what the experience taught us about Phase B Ralph mechanics.

---

## Edge cases to think about

- **Cell-type mismatch is structural, not just vocab.** If the CPI scoring rule (YES = annual, MODERATE = less frequent, NO = no requirement) genuinely can't be encoded as `Optional[int_months]` because some states require sub-annual renewal (e.g., per-session), `int_months` can't capture that distinction either way. Phase B may surface this as a v2.2 schema input. Document if it appears.

- **GPT vs Claude on the unit axis.** GPT-5.2 in Commit 3 changed unit (months → years) while preserving semantic correctness. If the cell schema accepts either `unit=months magnitude=24` or `unit=years magnitude=2` as both projecting to CPI MODERATE, that's a design choice (probably the schema should reject one to force normalization). If it accepts both, the projection function needs to handle both. Plan does not commit to a normalization; iteration will surface what the schema actually does.

- **Cross-vintage drift.** CPI 2015 data reflects 2014-15 statutes. WI's renewal cadence in 2025 may have changed since 2015. Verify before treating CPI MODERATE as ground truth for the 2025 extraction: check WI's current §13.62 against the 2015 version (the OH bundle methodology has examples of this; Wayback or Justia for 2015-vintage WI statutes would be the check). If WI's cadence has changed, the oracle isn't valid and we should swap to a row whose statute hasn't changed.

- **The 2nd rubric (HG 2007) reads this row too.** HG 2007 = CPI 2003 vintage data, per the vintage-correction doc. HG's per-state per-question scorecard is NOT in the archive. Cross-rubric overlap can't be validated empirically this session.

- **The CPI 2015 extract has 6 data-quality glitches** (per `cpi_2015_c11_projection_mapping.md` §"data-quality glitches"). 4 mixed-case typos + 2 numeric-where-categorical entries. WI IND_199 is `MODERATE` (clean), so this row is unaffected.

- **Other rows in the chunk may regress.** When we re-dispatch `registration_mechanics_and_exemptions` after a YAML edit, we change the prompt only for `renewal_cadence` — but the model sees the chunk as a whole. Adjacent rows' answers may shift even with no prompt change for them. Log if observed; do not over-interpret as Ralph-causation without evidence.

- **The wi-tier1-direct-read branch's `compendium/source_quotes.yaml` is the source of truth.** This new branch is forked from `main` (commit `28f3e47`), which does NOT yet contain the wide-pass YAML changes (those live on `wi-tier1-direct-read`). The implementing agent's first action should be to confirm the YAML state matches what they expect — likely **the agent should `git merge wi-tier1-direct-read` into this branch first** so the starting state includes the wide-pass YAML. Otherwise the YAML is still in its narrow-17-row state and the renewal_cadence prompt isn't present. **This is a real branch-state question; flag for Dan.**

---

## Questions for Dan (pre-execution)

1. **Branch starting state.** Should the implementing agent `git merge wi-tier1-direct-read` into `wi-ralph-cpi-renewal-cadence` before iteration 0, so the wide-pass YAML is present? Or branch off a different commit? (Plan default if no answer: merge wi-tier1-direct-read, since the failure mode being iterated on only exists in the post-wide-pass YAML.)

2. **Dispatch mechanism.** Option A (add `--chunks` flag, ~$0.05-0.10/iter), B (no code change, ~$0.30-0.40/iter), or C (single-row script, deferred)? Recommendation: A, but Dan may want B (zero code touch) given the exploratory framing.

3. **Vintage check first?** Should iteration 0 include a manual check that WI's current §13.62 renewal cadence matches the 2015 version CPI scored? ~5-10 min web research. If WI's law has changed, swap to a row with stable vintage.

4. **What does "stop" look like?** The plan defaults to Dan-calls-it (stopping condition c). Dan may want a more concrete metric — e.g., "stop when 4/6 runs project to MODERATE" or "stop after exactly 5 iterations." Plan defers; first-row-by-hand suggests human judgment.

---

## What could change (provisional findings dependencies)

- **If the audit's "CPI 2015 C11 is the row-level oracle" claim is later revised** (e.g., new vintage mismatch surfaces, or new ground-truth data shows per-state cells don't match published category aggregates), the oracle for this row would shift and the iteration premise would need re-baselining.

- **If Phase A pre-flight is executed first** (the deferred wide-pass Commit 4), the starting YAML would be different (vocab-patched globally) and this row's iteration would start from a cleaner baseline. Currently we deliberately iterate against the unpatched YAML — but if Phase A lands first, replace iteration-0's "current state" with the post-Phase-A state.

- **If the cell type for this row changes** (e.g., v2.2 swaps `Optional[int_months]` for an enum like `{annual, biennial, none, sub_annual}` to match CPI's scoring), the convergence target changes and iteration outputs need re-mapping.

- **If we learn the row isn't Ralph-tractable** (cell type can't represent the answer; model can't reliably produce the answer; oracle is too coarse to validate), document the finding and move to a different first row — `lobbyist_spending_report_filing_cadence` (CPI IND_201, WI=NO, similar failure shape) is the audit's #2 candidate.

- **If the iteration converges in 1-2 rounds**, the convergence is informative but probably an artifact of how clean this specific row's vocab/cell-type mismatch is. Don't generalize; pick a harder row for round 2.

---

## What is NOT in scope for this plan

- **Ralph automation.** This plan is explicitly first-row-by-hand. Automation level is decided AFTER iteration ends, based on what we learned.
- **Phase A pre-flight YAML audit.** Deferred until Phase B teaches us what kinds of fixes the audit needs to know how to make.
- **Other CPI-readable rows.** 21 rows are CPI-readable; only this one is iterated on. Other rows wait for Phase A or subsequent Phase B sessions.
- **Multi-state Ralph.** WI only. Cross-state validation comes after the per-row mechanism is understood.
- **Cross-vintage Ralph.** Only WI 2025 here. Cross-vintage validation per the ⭐ success criterion #3 needs more statute bundles.
- **HG 2007 retrieval.** Per the audit, HG per-state-per-question could add ~1,900 oracle cells but requires its own research line. Deferred to a future task.
- **Schema fixes.** Anything that surfaces as a v2.2 schema input gets recorded to the v2.2 ledger (`docs/active/wi-tier1-direct-read/results/v2_2_schema_inputs.md`) but NOT fixed in this branch.

---

## Testing details

This is an **exploration** task, not a code-change task — per write-a-plan's exception, no formal TDD test plan is required. The "test" is observational: does Ralph iteration produce a convergent answer? What patterns emerge?

If the implementing agent chooses Option A (small dispatcher tweak to add `--chunks` flag), that code change DOES need test coverage:

- Add 1 unit test: `--chunks registration_mechanics_and_exemptions` filters the dispatch to that chunk only; other chunks not dispatched.
- Add 1 integration-style test: dispatcher run with `--chunks foo` (nonexistent) errors cleanly with a clear message listing valid chunk names.
- No mocks-only tests; mock only the actual model API call.

If Option B is chosen, no code is touched and no tests needed.

NOTE: I will write *all* tests before I add any implementation behavior (for the Option A code path only).

---

## Implementation details

- The `compendium/source_quotes.yaml` file is the prompt SSOT — edit in place, never via a generator script.
- The `compendium/disclosure_side_compendium_items_v2.tsv` row contract is NOT touched by this plan (cell type is not changing).
- Dispatcher invocation pattern (whichever option): `uv run --env-file .env.local python scripts/tier_1_direct_read_legal_axis.py --state WI --vintage 2025 --models claude-opus-4-7 gpt-5.2 --runs 3 [--chunks registration_mechanics_and_exemptions]`.
- Result JSON paths: `docs/active/wi-ralph-cpi-renewal-cadence/results/tier_1/WI_2025/<model>__<chunk>__run<N>.json` (note: NEW results dir under this branch; existing wi-tier1 result JSONs are NOT touched, and the dispatcher's state-keyed `--state WI --vintage 2025` plus this branch's CWD will produce a clean new dir).
- **Archive every iteration's prior JSONs** before re-dispatch — move to `_pre_iter<N>/` subdir per the wide-pass + narrow-pass precedent (CLAUDE.md Experiment Data Integrity). Never delete.
- **Per-iteration cost telemetry:** the dispatcher writes per-file `cost_usd_estimate`; sum and reconcile against the log's `session_cost` after each dispatch. Add cumulative cost to the iterations log.
- **Spend hard ceiling: $5.** If reached, stop regardless of convergence state.
- Cumulative WI cost ledger across both branches: wi-tier1-direct-read = $7.2946 → this branch adds Phase B spend. Track separately in this branch's docs.
- Do NOT push to `main`. Do NOT merge to `wi-tier1-direct-read`. Stays on `wi-ralph-cpi-renewal-cadence`.
- Per Dan's "do NOT implement without discussion" pattern: **before iteration 0**, confirm Dan's answers to the 4 questions above. Iteration 0 itself is the first cost-bearing step.

---

**Plan length sanity check:** This plan is long because the cross-branch context is non-trivial (Phase A vs B, oracle audit's role, branch-state question, the YAML/cell-type mismatch backstory). The implementing agent reads it once, does the work in a small fraction of the time. If the agent is repeating from a prior session: skip to "Operational mechanics" + iteration log.

---
