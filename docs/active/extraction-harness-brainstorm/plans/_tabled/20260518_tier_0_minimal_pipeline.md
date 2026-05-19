# Tier 0 — Minimal end-to-end pipeline (smoke test)

> **🟥 SUPERSEDED 2026-05-18 — DO NOT EXECUTE.** This plan was attempted on 2026-05-18 and failed four preconditions at execution time: (1) wrong data paths (corrected in the in-session RETARGET banner below, but discovery cost real time); (2) no Anthropic API key on the implementing machine — and `retrieval_v2/docs.md` already noted the laptop is keyless, so this was a self-contradiction the plan didn't catch; (3) `scoring_v2/` module specified-but-not-built — the "thin wiring script" framing understates the work ~10× because the scorer prompt + tool schemas + parser have to be inlined from the 1380-line `20260514_brief_writer_implementation_plan.md`; (4) a circular import `chunks_v2 → models_v2 → retrieval_v2 → chunks_v2` surfaced under cold-load that the test suite missed because tests import lazily inside test functions. Architecture also reframed in the same session: retrieval+score is now the *escape-hatch* path; direct-read with cross-model verify (Claude + GPT side-by-side) is the YAGNI primary. **See [`../20260518_tier_0_direct_read_smoke_test.md`](../20260518_tier_0_direct_read_smoke_test.md)** for the replacement plan. Pivot reasoning in [`../../convos/20260518_tier_0_execution_pivot_to_direct_read.md`](../../convos/20260518_tier_0_execution_pivot_to_direct_read.md). This file is retained for provenance (the `2b9528c` retarget commit lives on top of it as a record of what was tried); the **Tier-1 forward-pointer section near the bottom (CPI 2015 / 6 de-jure items / σ_noise / projection function) remains valid input for Tier-1 planning** even though the Tier-0 portion is dead.

> **RETARGET 2026-05-18 (in-session, pre-supersession):** Tier-0 vintage swapped from **OH 2015 → OH 2025** because the OH 2015 statute bundle was not on the implementing machine (Dans-MacBook-Air) — only OH 2010 and OH 2025 were present in the canonical location. Approved by Dan in-session. All vintage-2025 references below were originally 2015. The Tier-1 forward-pointer section retains 2015 — that's Tier 1's bundle-availability problem to resolve. Convenient side-effect: OH 2025 was the v2 scorer prompt's original tuning vintage (`statute-extraction` iter-1), so this is closer to known territory than the original scope.
>
> **Path correction (same commit):** Canonical statutes path is `~/data/lobby_analysis/statutes/<STATE>/<VINTAGE>/`, NOT `~/data/statutes/<STATE>/<VINTAGE>/` as originally written. Pre-existing data/ dir in the worktree (containing gitignored `data/retrieval_v2/.gitkeep` placeholder) made `ln -s ~/data data` infeasible; replaced with sibling symlink `data/statutes -> /Users/dan/data/lobby_analysis/statutes`. Symlink lives inside gitignored `data/` so Step 1's commit is empty / skipped.

**Goal:** Run the extraction pipeline end-to-end for **one chunk on one state-vintage** (OH 2025, `enforcement_and_audits` chunk) and produce a partial `StateVintageExtraction` containing the 2 legal cells. Verify the wiring works; no projection comparison, no σ_noise re-runs, no other chunks.

**Originating conversation:** [`../../convos/20260518_synopsis_walkthrough_and_tier_0_scoping.md`](../../convos/20260518_synopsis_walkthrough_and_tier_0_scoping.md)

**Context:** The post-framing review synopsis ([`../../results/20260516_review_synopsis.md`](../../results/20260516_review_synopsis.md)) flagged H-F2: "the Ralph loop has no home in the four-component architecture; no orchestrator dispatches the pipeline." The 2026-05-18 session reframed this — the Ralph loop *is* the orchestrator, and the load-bearing next move is building the smallest version of it that runs end-to-end. Plans A/B/C from the synopsis are downstream of that; the EvidenceSpan and axis_coverage forks resolve empirically once a real run produces something to look at.

**Confidence:** Exploratory. Tier 0's purpose is to test whether the 4 v2 modules (`models_v2`, `chunks_v2`, `retrieval_v2`, the WIP brief-writer in `retrieval_v2/brief_writer.py`) wire into a runnable end-to-end pipeline. Surprises are expected and informative; the value is what they teach about Tier 1.

**Architecture:** A thin wiring script at `scripts/tier_0_smoke_test.py` that invokes (1) the retrieval agent against the OH 2025 statute bundle, (2) the brief-writer for the `enforcement_and_audits` chunk using retrieval output, (3) `anthropic.messages.create()` to dispatch the scorer call, (4) the parser to convert response into cells, (5) assemble a partial `StateVintageExtraction`, (6) save artifacts to `results/` with provenance headers. No new packaged module. The dispatch logic is the kernel of what the orchestrator will become; YAGNI says don't package it yet.

**Branch:** `extraction-harness-brainstorm` (worktree at `/Users/dan/code/lobby_analysis/.worktrees/extraction-harness-brainstorm/`)

**Tech Stack:** Python 3.12, Anthropic SDK (Citations API + tool use), Pydantic v2, `uv` for dep management.

---

## Pre-flight reads (mandatory before touching code)

The implementing agent has zero context. Read these first, in order:

1. `/Users/dan/code/lobby_analysis/.worktrees/extraction-harness-brainstorm/STATUS.md` — current focus, branch inventory, ⭐ Compendium 2.0 success criterion.
2. `docs/active/extraction-harness-brainstorm/RESEARCH_LOG.md` — full session trajectory for this branch.
3. **This plan's originating convo:** `docs/active/extraction-harness-brainstorm/convos/20260518_synopsis_walkthrough_and_tier_0_scoping.md` — the substantive reasoning behind Tier 0 scoping, including the EvidenceSpan resolution that Step 2 below operationalizes.
4. `docs/RESEARCH_ARC.md` (repo root) — three-prong arc, Phase C eval framing, Ralph loop concretization.
5. `src/lobby_analysis/retrieval_v2/docs.md`, `src/lobby_analysis/chunks_v2/docs.md`, `src/lobby_analysis/models_v2/` — the 4 v2 modules being wired together.
6. Brainstorm convos that produced the current shapes:
   - `docs/active/extraction-harness-brainstorm/convos/20260514_retrieval_brainstorm.md`
   - `docs/active/extraction-harness-brainstorm/convos/20260514_chunks_brainstorm.md`
   - `docs/active/extraction-harness-brainstorm/convos/20260514_brief_writer_brainstorm.md` (contains the Q8 `provenance` decision)

## Prerequisites

- **OH 2025 statute bundle** (retargeted from 2015 — see banner). Canonical path: `~/data/lobby_analysis/statutes/OH/2025/`. Symlinked into worktree at `data/statutes/OH/2025/` in Step 1. (Original prereq language read: "User maintains canonical data at `~/data/statutes/OH/2015/`... If `~/data/statutes/OH/` doesn't exist on this machine, **stop and ask the user** — do not proceed against OH 2010 or OH 2025 as a substitute. Vintage mismatch with CPI 2015 ground truth makes the eventual Tier 1 comparison meaningless, and Tier 0 is the predecessor of Tier 1." That stop fired on 2026-05-18; resolution was the blessed retarget.)
- **`ANTHROPIC_API_KEY`** in env. Tier 0 dispatches real API calls (~$1–2 budget per smoke-test run).
- **Model:** `claude-opus-4-7` to match the prior `statute-extraction` iter-1 baseline (93.3% inter-run agreement on the v1.2 definitions chunk). Override only if there's a documented reason.

## Why this is an exploration task, not strict TDD

Per the write-a-plan skill: "Pure analysis or exploration tasks ... do not need TDD." Tier 0 fits — the pipeline either wires up or it doesn't, and either outcome is informative. The "test" is the end-to-end run itself.

Unit-level TDD **is** in scope for the small wiring helpers introduced in Steps 3–5 (retrieval invocation wrapper, brief-writer dispatch, scorer dispatch, parser-output assembly). Those should be written test-first using frozen fixtures captured from real runs — never mocks of behavior.

## Success criteria

Tier 0 passes if all of:

1. The script runs to completion (no uncaught exceptions).
2. It produces a `StateVintageExtraction` with `state_abbr="OH"`, `vintage_year=2025`.
3. The extraction's `cells` field contains exactly 2 entries: legal halves of `lobbying_violation_penalties_imposed_in_practice` and `lobbying_disclosure_audit_required_in_law`.
4. Each cell's `provenance` is a non-empty `tuple[retrieval_v2.EvidenceSpan, ...]`.
5. The cell values type-check against their `CompendiumCellSpec.expected_cell_class`.
6. A hand-eyeball read of the cell values is plausible against OH 2025 statute text (does OH 2025 require audits? Are penalties statutorily defined? — quick sanity check, ~10 minutes, not a formal projection).

If any of (1)–(5) fail, **stop and report rather than patching**. The failure mode is the deliverable.

---

## Implementation steps

### Step 1 — Set up the OH 2025 data symlink

- Verify `~/data/lobby_analysis/statutes/OH/2025/` exists. (Original plan path `~/data/statutes/OH/2015/` was wrong on both vintage and parent dir; see banner.)
- Worktree has a pre-existing gitignored `data/` directory containing only `data/retrieval_v2/.gitkeep` placeholder. Create sibling symlink: `ln -s /Users/dan/data/lobby_analysis/statutes /Users/dan/code/lobby_analysis/.worktrees/extraction-harness-brainstorm/data/statutes`.
- Verify the bundle is readable from `data/statutes/OH/2025/` within the worktree.
- No commit (symlink lives under gitignored `data/`).

### Step 2 — Verify the EvidenceSpan migration is already in place

**Already done 2026-05-18 in commit `0979779`** (`models_v2: retire EvidenceSpan; migrate CompendiumCell.provenance to tuple[retrieval_v2.EvidenceSpan, ...]`). The Fork 1 resolution from the synopsis was applied as a single tight commit: deleted `src/lobby_analysis/models_v2/provenance.py` + its test file, dropped `EvidenceSpan` from `models_v2.__init__` exports, swapped the import in `cells.py`, and changed the annotation to `provenance: tuple[EvidenceSpan, ...] = ()`. The original plan's "deletion requires a full import-graph audit; defer" assertion was overcautious — the actual surface was 6 files / 5 edit sites / 130 line-diff.

- Verify on this branch: `git -C /Users/dan/code/lobby_analysis/.worktrees/extraction-harness-brainstorm log --oneline 0979779 -- src/lobby_analysis/models_v2/cells.py` should return commit `0979779` with the schema change. `ls src/lobby_analysis/models_v2/provenance.py` should fail (file deleted).
- If both verify: **skip to Step 3**. No commit, no test re-run (commit `0979779` ran `uv run pytest`: 480 pass / 8 skip / 3 pre-existing `test_pipeline.py` failures unchanged from baseline).
- If either does NOT verify (branch state surprise — e.g., a rebase dropped the commit): **stop and surface to user**. Do NOT re-execute the migration blindly — coordinate first.

### Step 3 — Verify the retrieval agent runs against OH 2025

- Identify the current entry point for invoking retrieval (likely in `src/lobby_analysis/retrieval_v2/`; check `__init__.py` exports).
- Construct the call inputs targeting OH 2025's statute bundle. Use `hop=2` — matches what Tier 1 will use; cost delta over hop=1 is small and parity matters for the Tier-0 → Tier-1 lift.
- Invoke. Verify it returns a `RetrievalOutput` with at least one `CrossReference`.
- Hand-eyeball: do the returned `section_reference` strings look like real OH lobbying-statute sections (Ohio Revised Code §101.70 onward)?
- Save the `RetrievalOutput` to `results/20260518_tier_0_retrieval_oh_2025.json` (or `.md` if formatted for human reading) with a provenance header:
  ```
  <!-- Generated during: convos/20260518_synopsis_walkthrough_and_tier_0_scoping.md -->
  ```
- Commit: `tier-0: retrieval against OH 2025 produces N CrossReferences`

If retrieval returns zero `CrossReference`s or fails: **stop**. The retrieval prompt was tuned against OH 2025 (per `statute-extraction` iter-1), so zero results would point to a wiring regression rather than vintage tuning. Either way, that's the finding for this session; report and stop.

### Step 4 — Brief-writer for `enforcement_and_audits`

- Build the chunk: `chunks = build_chunks(); chunk = next(c for c in chunks if c.chunk_id == "enforcement_and_audits")`.
- Sanity-check: chunk has exactly 2 cells (legal halves of `lobbying_violation_penalties_imposed_in_practice` and `lobbying_disclosure_audit_required_in_law`) once filtered to legal axis. (Note: `enforcement_and_audits` has 4 cells total per the manifest — 2 rows × 2 axes. Practical halves are out of scope for Tier 0; filter or let the brief-writer's legal-axis-only mode handle it.)
- Invoke the brief-writer with `(chunk, retrieval_output)`. Verify the return is a dict suitable for `anthropic.Anthropic().messages.create(**kwargs)`.
- Sanity-check the kwargs:
  - System prompt mentions the 2 row IDs and their cell types.
  - User message includes the retrieved sections as `document` content blocks with `cite_documents=true`.
  - Tools list includes `record_cell` and `record_unscoreable_cell` (per the brief-writer brainstorm).
- Save the kwargs to `results/20260518_tier_0_brief_kwargs.json` with a provenance header (document content can be elided to a length sentinel for size).
- Commit: `tier-0: brief-writer produces messages.create kwargs for enforcement_and_audits`

### Step 5 — Dispatch the scorer call + parse

- Instantiate `anthropic.Anthropic()` and call `messages.create(**kwargs)`. Capture the full response object.
- **Capture the prompt-sha before dispatch.** Compute `prompt_sha = hashlib.sha256(scorer_prompt_v2_text.encode()).hexdigest()` (using the same prompt content the brief-writer loaded). Persist it in the results JSON alongside the response — Tier 1's σ_noise loop requires fixed prompt-sha pinning, and bisecting smoke-test outputs against future prompt revisions needs this fingerprint captured from the first run.
- Pass the response to the parser entry point (per the brief-writer brainstorm: `parse_scoring_response(message, state_abbr="OH", vintage_year=2025, chunk_id="enforcement_and_audits") -> ScoringOutput`).
- Inspect the parsed `ScoringOutput`. Confirm it has exactly 2 cells, each with non-empty `provenance`.
- Save the raw response (with sensitive fields redacted if any), the parsed `ScoringOutput`, and the `prompt_sha` to `results/20260518_tier_0_scoring_output.json` with a provenance header.
- Commit: `tier-0: scorer call dispatched + parsed`

### Step 6 — Assemble the partial SMR + unit tests for the wiring

- Construct a partial `StateVintageExtraction(state_abbr="OH", vintage_year=2025, cells=<from parser>)`. Verify Pydantic validation passes.
- Write unit tests for the small helper functions introduced in Steps 3–5:
  - Retrieval invocation wrapper (input → kwargs).
  - Brief-writer dispatch wrapper (chunk + retrieval_output → kwargs).
  - Scorer dispatch wrapper (kwargs → raw response → parsed `ScoringOutput`).
  - Cell-to-SMR assembly.
- Use **frozen fixtures** captured from Steps 3 and 5 — real RetrievalOutput, real API response. NOT mocks of behavior. Per `skills/testing-anti-patterns/SKILL.md`: tests must verify actual behavior.
- Run tests; confirm green.
- Save the assembled SMR to `results/20260518_tier_0_smr_oh_2025.json` with provenance header.
- Commit: `tier-0: assemble partial SMR + wiring unit tests`

### Step 7 — Hand-eyeball + writeup

- Compare cell values against the OH 2025 statute text. Do they read as plausible? (~10 minutes.)
- Write `results/20260518_tier_0_writeup.md` (with provenance header) containing:
  - What the script does.
  - Cell values produced (the 2 legal cells, with their provenance).
  - Wall-clock time and API cost.
  - `prompt_sha` (the scorer prompt fingerprint captured in Step 5) — anchors this Tier-0 run for future bisects.
  - Surprises encountered during Steps 1–6 (especially anywhere the wiring didn't behave as the brainstorm convos predicted).
  - Recommendation: ready for Tier 1, or another Tier 0 iteration needed?
- Commit: `tier-0: smoke-test writeup`

### Step 8 — Finish-convo

- Edit the originating convo file (`docs/active/extraction-harness-brainstorm/convos/20260518_synopsis_walkthrough_and_tier_0_scoping.md`) to add a back-link to the writeup and a one-paragraph executive summary of the smoke-test outcome.
- Prepend a Tier-0-execution session entry to `RESEARCH_LOG.md` (newest first per the doc convention).
- Append one line to `STATUS.md` under "Recent Sessions" (do not rewrite other content).
- Commit + push. Don't merge to main — Tier 0 is a checkpoint, not a research-line completion.

---

## Edge cases to anticipate

- **Retrieval emits 0 `CrossReference`s.** Either OH 2025 has no enforcement/audit language (very unlikely — Ohio Revised Code Chapter 101 covers this and the retrieval prompt was tuned on this exact vintage) or there's a wiring regression. Report and stop; don't try to patch the prompt mid-session.
- **Scorer emits cells the parser rejects** (e.g., unknown tool names, malformed payloads). Per the brainstorm: "unknown tool names reset the citation buffer." Surface the rejection in the writeup; don't silently drop cells.
- **Cell value out of range for its `CompendiumCellSpec`.** Pydantic should catch this. If it does, that's a finding about the scorer prompt → row description mismatch, not a bug to patch in Tier 0.
- **`models_v2.EvidenceSpan` import surface larger than expected.** Step 2's audit may surface importers across fixtures, tests, possibly `compendium_loader.py`. Update them in this commit; defer the deletion of the class itself.
- **Data symlink already exists with a conflicting target.** Don't overwrite blindly; ask user.
- **Cost overrun.** If retrieval + scoring runs >$5 for the chunk, stop and investigate before iterating.

## Confidence checkpoints (don't barrel through)

| Checkpoint | If it fails... |
|---|---|
| Retrieval returns ≥1 CrossReference | Stop; report whether the issue is vintage-mismatch or prompt-tuning |
| Brief-writer produces valid kwargs | Stop; the chunk → kwargs path may have a regression vs the brainstorm spec |
| Scorer call returns parseable response | Stop; either the prompt or the tool schemas need adjustment |
| Parser produces exactly 2 cells | Stop; either the scorer emitted other tool calls or the parser logic mis-clusters citations |

---

## After Tier 0 — Tier 1 scope (forward-pointer)

When Tier 0 lands clean, **Tier 1 is the 6 chunks and deeper comparison.** A separate plan should be written for it; do not fold Tier 1 into Tier 0.

Tier 1 scope:

- **6 chunks** covering all 6 de-jure CPI 2015 items:
  - `lobbying_definitions` (IND_196 — target definitions)
  - `registration_thresholds` (IND_197 — compensation threshold)
  - `registration_mechanics_and_exemptions` (IND_199 — renewal cadence)
  - `lobbyist_spending_report` (IND_201 — spending report mandate + itemization + compensation rollup)
  - `principal_spending_report` (IND_203 — principal-side spending report)
  - `enforcement_and_audits` (IND_207 — audit requirement in law)
- **σ_noise estimation** via N=3 re-runs at fixed prompt-sha (per RESEARCH_ARC's Ralph-loop concretization). Pre-requisite for any loss-function comparison.
- **CPI 2015 projection function** consumed from the sister branch `phase-c-projection-tdd` (Dan's parallel work). Tier 1 imports `f_cpi2015_dejure(SMR) → projected_score` — don't stub locally.
- **Δ vs published CPI 2015 OH scores** computed per item and aggregated. First real Ralph-loop data point.
- **Same chunk-set + same prompt-sha against OH 2010 and OH 2025** if `oh-statute-retrieval` has produced those bundles by Tier 1 time. Track A's across-vintage stability check is the only Ralph-loop signal that doesn't go through a rubric and is load-bearing for Goodhart defense per RESEARCH_ARC.
- **De-facto half (IND_198, 200, 202, 204, 205, 206, 208, 209)** stays out of scope — those require Track B's portal-observation pipeline, not this branch.

Tier 1's plan should also propose whether the orchestrator graduates from a `scripts/` script to a packaged module — by Tier 1, the dispatch logic will have iterated enough to know what shape it wants.

---

## Testing Details

Tier 0 is primarily an exploration task — the end-to-end run is the deliverable, not a unit-testable invariant. Unit-level TDD covers the small wiring helpers introduced in Steps 3–5 (retrieval invocation wrapper, brief-writer dispatch, scorer dispatch + parsing, SMR assembly). These tests:

- Use **frozen fixtures** from Steps 3 and 5 — real `RetrievalOutput` and real Anthropic API response objects, captured to disk during initial runs. Not mocks of behavior.
- Verify **wiring behavior** — does the helper construct correct `messages.create()` kwargs from a chunk + retrieval_output? Does the parser correctly cluster citations onto tool_use blocks per the "citations accumulate, flush on tool_use, reset on unknown tool" rule?
- Do **not** verify Pydantic type semantics — those are validated by Pydantic itself; testing them in our test suite is testing-anti-pattern (testing the library).
- Run fast (no live API calls in tests; live calls only in `scripts/tier_0_smoke_test.py`).

NOTE: I will write *all* tests before I add any implementation behavior.

## Implementation Details

- Tier 0 script lives at `scripts/tier_0_smoke_test.py` — single file. No new `orchestrator_v2/` module. The dispatch logic is the kernel of the future orchestrator but shouldn't be packaged as such yet (YAGNI).
- Pre-locked decisions from the originating convo: (a) `CompendiumCell.provenance: tuple[retrieval_v2.EvidenceSpan, ...]` — Step 2 implements this; (b) Tier 0 scope is one chunk × one state-vintage × no projection; (c) success/failure is empirical, not unit-test-encoded.
- Cost budget: ~$1–2 per Tier 0 run. Cache the `RetrievalOutput` to disk after the first successful Step 3 run so Steps 4–7 can iterate against the cached copy without re-billing retrieval.
- Every results file gets the provenance header: `<!-- Generated during: convos/20260518_synopsis_walkthrough_and_tier_0_scoping.md -->`.
- Worktree absolute path: `/Users/dan/code/lobby_analysis/.worktrees/extraction-harness-brainstorm/`. All paths in this plan are relative to that unless prefixed `/Users/...`.
- The Phase C projection for CPI 2015 lives on `phase-c-projection-tdd` (Dan's parallel work). Tier 0 does NOT touch that branch; Tier 1 will import its output as a dependency.
- Per the multi-committer rules: `phase-c-projection-tdd` and `oh-statute-retrieval` are sister branches with active work. Do NOT modify them. If Tier 0 surfaces a need for changes to shared infrastructure (e.g., `compendium/`), stop and surface to the user rather than editing across branches.
- Step 2's audit may reveal that the `_handoffs/` brief-writer impl plan references the old `provenance` shape. If so, update those references in the same commit, but mark them as plan-time references (the plan is what the impl agent reads — keep it consistent).
- The retrieval brainstorm landed on 2-hop as default. Tier 0 may use `hop=1` to keep costs minimal; this is the Question 2 below.

## What could change

- **Retrieval prompt may not generalize across vintages.** The v2 scorer prompt was tuned against OH 2025 definitions (per iter-1 in the now-paused `statute-extraction`). Tier 0 (post-retarget) runs against the prompt's own tuning vintage, so this risk doesn't bear on this run — but it remains a Tier 1 concern: enforcement language in OH 2015 may use older phrasings the prompt doesn't anticipate. If Tier 1 retrieval against OH 2015 returns weak `CrossReference`s, the finding may be "the retrieval prompt needs vintage-aware tuning" — that's a Tier 1 prerequisite, not a Tier 0 bug.
- **The 5-tier de facto scoring** in CPI 2015 (25/75 intermediate values undocumented in the published criteria) is a Tier 1 problem the de-jure-only Tier 0 sidesteps entirely.
- **`models_v2.EvidenceSpan` deletion** is deferred to a follow-on plan. Tier 0 deprecates the class; deletion requires a full import-graph audit.
- **The orchestrator's packaged shape.** Tier 0's script is a prototype. Tier 1 may decide the orchestrator wants its own module with batching, σ_noise re-run scaffolding, prompt-sha pinning. Don't pre-design that here.

## Questions

1. **Hand-eyeball pass criterion strictness.** Is "the 2 cell values look plausible against statute text" sufficient for Tier 0 to declare success, or must the values be confirmed correct? My read: plausible is sufficient — correctness is Tier 1's job once we have a projection function and ground truth to compare against.
2. **Cost overrun threshold.** $5 is my proposed stop-and-investigate threshold. Is that the right number, or higher / lower?

(Q1 from prior draft — hop count — locked at `hop=2` per user 2026-05-18; baked into Step 3. Q4 from prior draft — Step 2 ordering — was moot since the plan already locks first; removed.)

---
