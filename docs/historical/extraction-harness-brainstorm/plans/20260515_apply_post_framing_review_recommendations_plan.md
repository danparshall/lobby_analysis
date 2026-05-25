# Apply Post-Framing Review Recommendations Implementation Plan

**Goal:** Apply the actionable findings from the two 2026-05-14 post-framing reviews — the compendium-side audit (commit `770f866`, report at `docs/historical/compendium-source-extracts/results/20260514_post_framing_review.md`) and the harness-side audit (commit `0ccbb86`, report at `docs/active/extraction-harness-brainstorm/results/20260514_post_framing_review.md`) — to this branch, and propagate the deferred findings to their proper branches without re-opening frozen Compendium 2.0 decisions.

**Originating conversation:** [`docs/active/extraction-harness-brainstorm/convos/20260514_post_framing_compendium_review_dispatch.md`](../convos/20260514_post_framing_compendium_review_dispatch.md) (dispatcher session that surfaced both reviews into the link graph; the sibling harness-review's own convo file `20260514_post_framing_harness_review.md` is uncommitted in the worktree pending its parent session's finish-convo)

**Context:** On 2026-05-14 the project framing was sharpened in `docs/RESEARCH_ARC.md` (Prong 2 + Prong 3 is the product; Prong 1 is upstream scaffolding; Phase C is the Ralph-loop eval function). Two parallel review sessions audited the work-to-date against the corrected framing — one for the Compendium 2.0 schema/docs, one for the four harness components (`models_v2`, `chunks_v2`, `retrieval_v2`, `scoring_v2`-as-brainstormed). The two reviews concur thematically on the Ralph loop being undersupported, and surface complementary findings across their respective surfaces.

**Confidence:** Medium-high on findings *as described* (both reviewers worked from the same RESEARCH_ARC framing; findings were checked against the v2 TSV + brainstorm convos + impl plans; this plan re-verified one of them directly — TSV `status` column is 181/181 `firm`, not 180+1 as README claims). Medium on the *design decisions* embedded in Phases 3 and 4 — those are genuine forks that should be brainstormed with the user before implementation rather than pre-locked here.

**Architecture:** Five phases, ordered by independence-then-risk. Phases 1, 2, 5 are mechanical (doc fixes, a new tooling script, and handoff notes for other branches). Phases 3 and 4 each open a brainstorm before code — both involve typed-state design decisions that the implementing agent must NOT silently lock unilaterally.

**Branch:** `extraction-harness-brainstorm` (worktree at `/Users/dan/code/lobby_analysis/.worktrees/extraction-harness-brainstorm`). All implementation lands here; Phase 5 writes notes that propagate to other branches.

**Tech Stack:** Python 3.12, uv, pytest, ruff. Pydantic v2 frozen models (`models_v2/`, `retrieval_v2/`). No new dependencies expected.

---

## Operating environment

- All paths in this plan are **relative to the repo root**. The fresh agent operates inside the worktree at `/Users/dan/code/lobby_analysis/.worktrees/extraction-harness-brainstorm` — use `git -C /Users/dan/code/lobby_analysis/.worktrees/extraction-harness-brainstorm <subcmd>` for git (the repo's permission rules hard-deny `cd <path> && git ...`).
- The branch is shared (multi-committer repo). `git fetch` at session start; verify clean working tree; do not touch other branches.
- The reviewer's reports are local-history-present and remote-pushed as of `58a8222`. Read them first.

## Scope and non-scope

### In scope (this plan, this branch)

| # | Phase | Finding(s) | Type |
|---|---|---|---|
| 1 | Quick doc fixes | C-F2 (status drift), H-F2 (orchestrator gap) | Docs only |
| 2 | Row-ID consistency tool | C-F4 | New code + tests (TDD) |
| 3 | EvidenceSpan consolidation | H-F1 | Brainstorm → code |
| 4 | SMR partiality marker | H-F3 | Brainstorm → code |
| 5 | Handoffs for deferred findings | C-F1, C-F3, Q5 OS-1 | Doc notes only |

### Out of scope (other branches / future work)

- **C-F1 (BLOCKER for Phase C) — Ralph-loop per-rubric normalization.** This is a Phase C kickoff decision; it does not land on this branch. Phase 5 of this plan writes a handoff note in `docs/active/phase-c-projection-tdd/plans/_handoffs/` so the next agent on that branch sees it before writing any projection code.
- **C-F3 — Legal-vs-practical content-field gap (35 + 13 + 9 legal-only `*_includes_*` rows with no practical sibling).** This is a Prong-2 brief-writer design decision and belongs in the still-future practical-axis sibling brainstorm. Phase 5 writes a forward-pointer note in `docs/active/extraction-harness-brainstorm/plans/` (this branch — that's where the practical-axis brainstorm will spin up).
- **Q5 (OS-1 P1-product residue candidate).** Per the handoff, flagged but not proposed for removal. Phase 5 records the watchpoint for `phase-c-projection-tdd` to revisit if/when extraction reveals OS scoring would benefit.
- **The four-component harness's "orchestrator" component itself.** H-F2's recommendation is to name and schedule the orchestrator — Phase 1.2 does the naming + scheduling. Actually building the orchestrator is the next-component-after-`scoring_v2`, not part of this plan.

---

## Phase 0: Read and orient (≈30 min)

The fresh agent has zero codebase context. Before any work:

1. Read `STATUS.md` (top sections + relevant Recent Sessions entries; skim, don't deep-read).
2. Read `docs/RESEARCH_ARC.md` (213 lines, authoritative framing).
3. Read both reports in full:
   - `docs/historical/compendium-source-extracts/results/20260514_post_framing_review.md` (compendium-side, 98 lines)
   - `docs/active/extraction-harness-brainstorm/results/20260514_post_framing_review.md` (harness-side, 105 lines)
4. Read this plan's originating convo (above) and `docs/active/extraction-harness-brainstorm/RESEARCH_LOG.md` (top 3 entries).
5. `git -C <worktree> fetch origin extraction-harness-brainstorm && git -C <worktree> status` — verify clean tree, up-to-date with origin.
6. Announce to user: "Read the two reviews and this plan. Ready to start Phase 1 unless you want to revise scope."

---

## Phase 1: Quick doc fixes (≈30 min, doc-only)

Two unrelated doc fixes, batched because both are surgical and don't need design decisions.

### 1.1 — C-F2: status-column doc/data drift

**Finding:** TSV column 7 (`status`) has 181/181 rows = `firm` (verified). `compendium/README.md` line 47 claims `firm (180 rows) or path_b_unvalidated (1 row — OS-1)`. `compendium/NAMING_CONVENTIONS.md` makes the same claim. OS-1's unvalidated status is actually encoded in the `n_rubrics=0` + the literal string `(unvalidated; path-b)` in the `rubrics_reading` column.

**Decision required from user before edit:** which side moves?
- **Option A:** Update the TSV to make OS-1 status = `path_b_unvalidated` (matches the docs; regenerate via `tools/freeze_canonicalize_rows.py`; downstream consumers reading `status` get a real value to branch on).
- **Option B:** Update the two docs to describe how unvalidated status is *actually* encoded (via `n_rubrics=0` + `rubrics_reading` string convention; the TSV stays as-is).

**Implementing agent: ask the user via AskUserQuestion before any edit.** Default recommendation (mention but don't pre-decide): Option A is cheaper to maintain — a real status value is more discoverable than a magic-string convention in another column. Option B is cheaper to ship — no TSV regeneration.

**Steps (Option A path):**
1. Inspect `tools/freeze_canonicalize_rows.py` for how `status` is set; add `path_b_unvalidated` as the value for OS-1.
2. Run the script; verify TSV regenerates with exactly 1 row at `path_b_unvalidated` (OS-1).
3. Confirm no other row's checksum changed (`git diff` on the TSV — should be a single-cell edit).
4. Commit: `fix(compendium): encode OS-1 status as path_b_unvalidated to match documented contract`.

**Steps (Option B path):**
1. Edit `compendium/README.md` line 47 to describe the encoding: `firm (181 rows). OS-1 (the lone path-b unvalidated row) is identified by n_rubrics=0 + the literal "(unvalidated; path-b)" prefix in rubrics_reading.`
2. Edit `compendium/NAMING_CONVENTIONS.md` analogously (find the parallel claim and rewrite).
3. Commit: `docs(compendium): correct OS-1 unvalidated-status encoding description`.

**Test:** `awk -F'\t' 'NR>1{print $7}' compendium/disclosure_side_compendium_items_v2.tsv | sort | uniq -c` should return either `181 firm` (Option B) or `180 firm / 1 path_b_unvalidated` (Option A). No tests added; this is a doc/data integrity claim.

### 1.2 — H-F2: name and schedule the orchestrator gap

**Finding:** No component in the four-module architecture (`models_v2`, `chunks_v2`, `retrieval_v2`, `scoring_v2`) is positioned to drive the Ralph loop — there's no n_runs primitive, no batch invocation, no per-rubric loss aggregator. "The orchestrator" is uniformly out-of-scope across all four brainstorm convos.

**This phase does NOT build the orchestrator.** It surfaces the gap into the persistent doc layer so it doesn't get rediscovered post-merge.

**Steps:**
1. Add a new bullet to `docs/RESEARCH_ARC.md` under the "Open empirical questions" or "Cross-track milestones" section (whichever fits the existing structure) — read the doc first to pick the right anchor. Bullet content:
   > **Ralph-loop orchestrator (named gap, not yet scheduled).** None of `models_v2` / `chunks_v2` / `retrieval_v2` / `scoring_v2` is positioned to invoke extraction with fixed prompt-sha across N runs (σ_noise estimation), batch across `(state, vintage, rubric)`, sum per-rubric losses to scalar, or diff across prompt versions. This is the next component after `scoring_v2` ships. Surfaced 2026-05-14 by [`docs/active/extraction-harness-brainstorm/results/20260514_post_framing_review.md`](../docs/active/extraction-harness-brainstorm/results/20260514_post_framing_review.md) Finding 2.
2. Add a one-line entry to `STATUS.md` under the "Active Research Lines" or equivalent table — branch `tbd-orchestrator` or similar placeholder, status `not yet scheduled`, brief = "Ralph-loop driver: n_runs, batch invocation, per-rubric loss aggregator. Surfaced 2026-05-14."
3. Add a placeholder file `docs/active/extraction-harness-brainstorm/plans/_handoffs/20260515_orchestrator_followup_note.md` — short note (≈40 lines) referencing both reviews + RESEARCH_ARC bullet + this plan, ready to be picked up after `scoring_v2` ships. **This is not an impl plan; it's a placeholder so a future search hits it.**
4. Commit: `docs: name Ralph-loop orchestrator gap; placeholder followup for post-scoring_v2`.

**Test:** None (doc-only).

---

## Phase 2: Row-ID consistency tool — C-F4 (≈2 hours, TDD)

**Finding:** The 9 per-rubric projection mapping docs at `docs/historical/compendium-source-extracts/results/projections/*_projection_mapping.md` use **pre-rename** row IDs throughout (247 occurrences across the 9 docs, by `§10.1` design — archived material is not rewritten). When `phase-c-projection-tdd` writes projection functions reading these docs, every row_id lookup must route through `§10.1`'s resolver table or `src/lobby_analysis/row_id_renamer.py:RENAMES`. Easy to skip silently.

**Deliverable:** A new script `tools/check_mapping_doc_row_ids.py` that asserts every row_id mentioned in a mapping doc either (a) exists in `compendium/disclosure_side_compendium_items_v2.tsv` or (b) is a key in `RENAMES`. Designed to be run as a pre-merge guard on projection PRs.

### 2.1 Read the surface area first

1. Read `src/lobby_analysis/row_id_renamer.py` — find `RENAMES` dict structure, understand how the existing renamer detects row IDs in text (likely a word-boundary regex with a known prefix set).
2. Read `compendium/NAMING_CONVENTIONS.md` §10.1 — understand the resolver table format and what counts as a row_id.
3. Read 2 of the 9 mapping docs to confirm the row_id reference shape (likely backticks-wrapped: `` `compensation_threshold_for_lobbyist_registration` ``).

### 2.2 Testing plan (write all tests before implementation)

I will add unit tests in `tests/test_check_mapping_doc_row_ids.py` covering:

- **`test_passes_when_all_row_ids_resolve`** — synthetic mapping-doc string containing only row_ids that are in the v2 TSV → tool returns exit 0, no findings.
- **`test_passes_when_only_pre_rename_ids_present`** — synthetic doc containing only row_ids that are keys in `RENAMES` (i.e., old names that resolve via the table) → tool returns exit 0.
- **`test_fails_when_unknown_row_id_present`** — synthetic doc containing a row_id that is neither in v2 TSV nor in `RENAMES` → tool returns nonzero, prints the offending row_id + filename + line number.
- **`test_handles_multiple_files`** — two synthetic mapping docs, one clean, one with a typo → tool reports only the dirty one.
- **`test_ignores_code_fences`** — a synthetic doc with a fenced code block containing strings that look like row_ids but are inside a fenced block clearly not meant as a row_id reference. **Decision required:** is the right behavior "scan everything" (no false-negatives) or "scan only backtick-wrapped tokens" (no false-positives)? Recommend the latter (backtick-wrapped only) — matches the actual mapping-doc convention. Test should pin whichever the implementing agent chooses with user approval.
- **`test_handles_renames_with_substring_overlap`** — `RENAMES` has at least one rename where the old name is a substring of another row_id (per the renamer's word-boundary handling). Synthetic doc tests both; tool must not false-positive on the substring.
- **`test_real_mapping_docs_pass`** — integration test: run the tool against the 9 real mapping docs at `docs/historical/compendium-source-extracts/results/projections/*_projection_mapping.md`. **Expected:** exit 0 (all 247 occurrences resolve cleanly through `RENAMES`). If this test FAILS, it's not a tool bug — it's a real drift finding that the agent must surface to the user.

NOTE: I will write *all* tests before I add any implementation behavior.

### 2.3 Implement

1. Write the tests above; run them; verify they all fail with the right shape (`ImportError`, then `NameError`, then `AssertionError`).
2. Implement `tools/check_mapping_doc_row_ids.py`:
   - CLI: `python tools/check_mapping_doc_row_ids.py <file> [<file> ...]` — accepts a list of mapping doc paths.
   - Loads v2 TSV row_ids into a set; loads `RENAMES` keys into a second set; the union is the resolvable set.
   - For each file, scans backtick-wrapped tokens matching the row_id shape (snake_case, starts with a known prefix family or matches the regex `^[a-z][a-z0-9_]*$` — match the renamer's existing regex for consistency).
   - For each token that is neither resolvable, prints `<file>:<line> <token>` to stderr.
   - Exits 0 if all clean; exits 1 otherwise.
3. Run unit tests; turn green one-by-one.
4. Run the integration test; it must pass (the §10.1 design intent says all 247 occurrences resolve).
5. Ruff format; full repo test suite must still pass (no regressions on the existing 448-test baseline).
6. Commit: `tools: add row_id consistency check for projection mapping docs (C-F4)`.

### 2.4 Document where this gets called

1. Add a one-line note to `compendium/NAMING_CONVENTIONS.md` §10.1 (or wherever fits): "Run `tools/check_mapping_doc_row_ids.py` as a pre-merge guard on projection PRs."
2. (Optional, surface to user) Should this be wired into a CI workflow? Out of scope for this plan unless user asks.
3. Commit (with the script if not already): `docs: point at row_id consistency check from naming conventions`.

---

## Phase 3: EvidenceSpan consolidation — H-F1 (brainstorm → code, ≈2-3 hours)

**Finding:** Two incompatible `EvidenceSpan` Pydantic classes are both public:
- `src/lobby_analysis/models_v2/provenance.py:13` — `(section_reference: str, quoted_span: str ≤ 200 chars, artifact_path: str, url: str | None)` — semantic statute-axis provenance.
- `src/lobby_analysis/retrieval_v2/models.py:29` — `(citation_type, document_index, cited_text, start_char_index, end_char_index, ...)` — Citations-API machine-level provenance.

The `scoring_v2` brainstorm Q8 locked `CompendiumCell.provenance: tuple[EvidenceSpan, ...]` but did not specify *which* `EvidenceSpan`. The harness reviewer recommends either (a) pick one for `provenance` + write an adapter, or (b) carry both — Citations span for raw machine-verified, semantic span derived.

### 3.1 Brainstorm first (no code)

**Do NOT skip this step.** Pre-locking by the fresh agent is exactly the failure mode the harness reviewer flagged.

1. Read both class definitions in full + their tests (`tests/test_provenance.py`, `tests/test_retrieval_v2_models.py` or equivalent).
2. Grep for all current usages: `git -C <worktree> grep -n "EvidenceSpan"` — list everywhere they're imported/instantiated/typed.
3. Read the `scoring_v2` brainstorm convo's Q8 lock + the brief-writer impl-plan-write handoff's reference (handoff lines ~154-156) to confirm what was intended.
4. Open an AskUserQuestion with three options:
   - **Option A — pick the semantic shape for `CompendiumCell.provenance`.** Scoring_v2 derives a `models_v2.EvidenceSpan` from each `retrieval_v2.EvidenceSpan` at brief-write time. Need to write the adapter. Phase C reads semantic directly. Loses raw char-index provenance unless explicitly preserved elsewhere.
   - **Option B — pick the Citations-API shape for `CompendiumCell.provenance`.** Phase C consumers must do their own section_reference + quoted_span parsing. Closer to ground truth (no derivation step) but more downstream work.
   - **Option C — carry both.** Define `CompendiumCellProvenance` (new) as a small record holding `(machine_span: retrieval_v2.EvidenceSpan, semantic_span: models_v2.EvidenceSpan)`; `CompendiumCell.provenance: tuple[CompendiumCellProvenance, ...]`. Richer; doubles the field count.
5. **Surface a recommendation but do not pre-lock.** Suggested framing: Option A is simpler and matches Phase C's natural read pattern (the projection mappings reason in terms of statute sections, not citation char indices); Option C is more correct under the framing where the legal-vs-practical gap is itself a research artifact (machine spans support cross-state replicability checks). Option B is the path of least scoring_v2 work but the path of most Phase C work.
6. **Lock with the user.** Record the decision in the convo file for this session (Phase 0 instructs the agent to write one as it goes).

### 3.2 Testing plan

I will add or extend tests in `tests/test_compendium_cell.py` (or wherever `CompendiumCell.provenance` is currently typed) covering:

- **`test_compendium_cell_provenance_type`** — pinning that `CompendiumCell.provenance`'s element type is the chosen class (whichever the user locks). This is a behavior test in the sense that it pins the public contract that Phase C will consume.
- **`test_provenance_adapter_round_trips_required_fields`** (Option A only) — if an adapter is written, test that constructing a `retrieval_v2.EvidenceSpan` with realistic Citations-API output, then running the adapter, produces a semantic `models_v2.EvidenceSpan` with `section_reference` and `quoted_span` populated correctly. Use a small realistic fixture (e.g., reuse the parser's existing fixture or build a 2-statute-section synthetic).
- **`test_provenance_carries_both_shapes`** (Option C only) — test that `CompendiumCellProvenance` instances carry both the machine and semantic spans, and that the semantic span is consistent with the machine span (`semantic.quoted_span` is a substring of the source statute around `machine.start_char_index`–`machine.end_char_index`).
- **`test_no_duplicate_public_export`** — assert that exactly one `EvidenceSpan` symbol (or the chosen wrapper) is exported from `lobby_analysis` top-level / is the type of `CompendiumCell.provenance`. Pins that the duplication is gone post-fix.

NOTE: I will write *all* tests before I add any implementation behavior.

### 3.3 Implement

(Steps depend on locked option — agent fills in based on Phase 3.1's decision.)

**For Option A (semantic-wins, adapter):**
1. Write the adapter function in `src/lobby_analysis/scoring_v2/` or a shared location — TBD by user during the brainstorm; the natural home is wherever it consumes retrieval output and produces `CompendiumCell` instances.
2. Update any existing `CompendiumCell.provenance` type annotation if it currently imports from `retrieval_v2` (or vice versa).
3. Run all tests; ensure no regression.

**For Option B (machine-wins):**
1. Update `CompendiumCell.provenance` type to import from `retrieval_v2`.
2. Delete or deprecate `models_v2/provenance.py` `EvidenceSpan` (or keep it and rename to avoid the dual-export — `SemanticEvidenceSpan` — and remove from `__init__.py` if not used).
3. Run all tests.

**For Option C (both, wrapper):**
1. Create `CompendiumCellProvenance` in `models_v2/provenance.py` (or new file) with both fields.
2. Update `CompendiumCell.provenance` type annotation.
3. Add the adapter for `retrieval_v2.EvidenceSpan → models_v2.EvidenceSpan` derivation (needed to populate the semantic half of `CompendiumCellProvenance`).
4. Run all tests.

In all cases:
- Ruff format.
- Run full repo test suite — no regressions on baseline.
- Commit: `models_v2: resolve EvidenceSpan duplication (Option <X> — see convo)`.

---

## Phase 4: SMR partiality marker — H-F3 (brainstorm → code, ≈1-2 hours)

**Finding:** `StateVintageExtraction.cells: dict[(row_id, axis), CompendiumCell]` is a flat 186-cell space, but the legal-only extraction harness (this branch's scope) produces only the 131 legal cells + the legal halves of the 5 dual-axis rows = 136 cells. Practical halves (50 practical-only + 5 dual-axis practical halves = 55 cells) are populated later by the Prong-2 sibling that hasn't been built yet.

Today `StateVintageExtraction` cannot tell a half-filled SMR (legal-only) from a fully-populated one. A Phase C consumer projecting from a half-filled SMR will silently miscompute any projection that reads practical cells.

### 4.1 Brainstorm first

1. Read `src/lobby_analysis/models_v2/extraction.py` — `StateVintageExtraction` definition + any existing validators.
2. Read the `models_v2` tests covering `StateVintageExtraction` to understand current invariants.
3. Open an AskUserQuestion with two options:
   - **Option A — `axis_coverage: frozenset[Literal["legal", "practical"]]` field.** Single new field on `StateVintageExtraction`. Validator: every `cell.cell_id`'s axis must be in `axis_coverage`. Consumers branch on `axis_coverage` to know what's safe to project from. Cheap; one field.
   - **Option B — type split.** New types `LegalAxisExtraction` and `PracticalAxisExtraction` (both subclasses of a common base or distinct types); `StateVintageExtraction` becomes a merge result. More wiring, more explicit, more code change downstream — every existing instantiation site has to choose which type.
4. **Recommendation (mention but don't pre-lock):** Option A. Reasons: (1) the partiality is a *coverage* property, not a *type* property — the cells themselves are typed correctly; (2) future axis values (`mixed`? per-chunk-axis?) are easier to add as set membership than as new types; (3) the change is one new field and one validator vs. a type-system rewrite. Option B is more correct if axis-mixing across axes is structurally forbidden later — but the brainstorm's Q6 lock (defer practical-axis) suggests the merge case is real and Option B forces a wrapper either way.
5. Lock with user.

### 4.2 Testing plan

I will add tests to `tests/test_extraction.py` (or wherever `StateVintageExtraction` lives) covering:

- **`test_legal_only_extraction_marked_partial`** — construct a `StateVintageExtraction` with only legal cells; assert it carries the partial marker (`axis_coverage == {"legal"}` for Option A, or assert it's a `LegalAxisExtraction` for Option B).
- **`test_full_coverage_extraction_marked_complete`** — construct one with both legal and practical cells; assert the marker reflects both axes.
- **`test_cell_axis_consistent_with_coverage`** (Option A) — adding a cell whose axis is not in `axis_coverage` should raise.
- **`test_merge_of_legal_and_practical_yields_complete`** (Option B) — combining a `LegalAxisExtraction` and `PracticalAxisExtraction` yields a complete `StateVintageExtraction`.
- **`test_extraction_existing_invariants_preserved`** — the post-validator (`cell.cell_id == key`) and the frozen-Pydantic discipline are unchanged.

NOTE: I will write *all* tests before I add any implementation behavior.

### 4.3 Implement

Per the locked option. Steps:
1. Edit `src/lobby_analysis/models_v2/extraction.py` to add the field or split the type.
2. Update `__init__.py` exports if needed.
3. Update any current callsite (e.g., `load_v2_compendium_typed`-adjacent code, the brief-writer/parser tests if they construct `StateVintageExtraction` directly).
4. Run unit suite; turn tests green.
5. Run full repo test suite — no regressions on baseline.
6. Ruff format.
7. Commit: `models_v2: mark axis coverage on StateVintageExtraction (Option <X>)`.

### 4.4 Update RESEARCH_ARC and STATUS

The Phase C consumers need to know to check the partiality marker. Add a one-paragraph note to `docs/RESEARCH_ARC.md` (under "Phase C reads") and a one-line entry to STATUS.md. Commit separately: `docs: surface axis-coverage marker for Phase C consumers`.

---

## Phase 5: Handoffs for deferred findings (≈45 min, doc-only)

Three findings explicitly belong on other branches. Write notes that the next agent on each will see.

### 5.1 C-F1 → `phase-c-projection-tdd`

Create `docs/active/phase-c-projection-tdd/plans/_handoffs/20260515_ralph_loop_per_rubric_normalization_note.md`. Content: short note (≈80 lines) summarizing the BLOCKER finding from the compendium review — uneven per-state per-atomic-item ground truth granularity across the 8 rubrics, the per-rubric validation regime table, and the specific recommendation that `phase-c-projection-tdd`'s kickoff must pick an explicit per-rubric normalization (uniform / by-summands / inverse-variance-weighted / etc.) before any projection code is written. **Link to:** the compendium review, RESEARCH_ARC, this plan, and the dispatcher convo.

**Edge case:** the `phase-c-projection-tdd` worktree may not be created yet on this machine, but the branch should exist on origin. If the docs directory `docs/active/phase-c-projection-tdd/` doesn't exist locally, write the file in the main worktree (or in the existing worktree if there is one) at the correct path; commit; let the `phase-c-projection-tdd` kickoff agent pick it up when they pull.

### 5.2 C-F3 → practical-axis sibling brainstorm (future this branch)

Create `docs/active/extraction-harness-brainstorm/plans/_handoffs/20260515_practical_axis_content_field_gap_note.md`. Content: short note (≈40 lines) flagging that 35 + 13 + 9 legal-only `*_includes_*` rows have no practical sibling, two routes (per-content-field practical cells vs. a single `practical_axis_observed_fields: Set[row_id]` envelope), and the decision point ("this is a Prong-2 brief-writer design decision, not v2 row-set re-opening"). **Link to:** the compendium review, this plan.

### 5.3 Q5 OS-1 → `phase-c-projection-tdd` watchpoint

Add OS-1 watchpoint to the C-F1 handoff (Phase 5.1) — same file, separate section. Note: OS-1's D16 disposition explicitly says "if extraction reveals OS scoring would benefit from inclusion, OS-tabling reverses." Phase C should flag if any rubric (especially OpenSecrets-adjacent rows) finds OS-1 read material during projection.

### 5.4 Commit

Single commit covering Phase 5: `handoff: surface deferred post-framing-review findings to other branches`.

---

## Phase 6: Finish-convo

Run `/Users/dan/.claude/skills/finish-convo/SKILL.md`. Write a convo summary referencing this plan + the locked decisions from Phases 3 and 4 + the per-phase commit SHAs. Update RESEARCH_LOG.md (top entry) + STATUS.md (one-liner). Push.

---

## Testing Details

This plan's tests cover behavior, not data structures:

- **Phase 2** tests pin the *behavior* that `tools/check_mapping_doc_row_ids.py` correctly identifies unresolvable row_ids in mapping docs. The "real mapping docs pass" integration test validates against ground truth (the §10.1 design intent).
- **Phase 3** tests pin the *behavior* that `CompendiumCell.provenance` exposes a single coherent provenance shape that Phase C can consume. The adapter test (Option A) and the round-trip test (Option C) exercise real Citations-API-shaped input.
- **Phase 4** tests pin the *behavior* that `StateVintageExtraction` cannot misrepresent its coverage — a legal-only extraction is detectable as such, and downstream code can branch on it.

No tests are added for pure data-structure shape (Pydantic frozenness, field name presence) — those are not behavior. The `test_no_duplicate_public_export` in Phase 3 tests the public surface, not field shape.

## Implementation Details

- The fresh agent should follow strict TDD on Phases 2, 3, 4 — write all tests before any implementation, in the RED phase commit.
- Brainstorm gates in Phases 3 and 4 are **mandatory** — do not pre-lock unilaterally. The harness reviewer's Finding 1 was precisely about this kind of silent lock.
- All paths in this plan are repo-root-relative. The fresh agent's working directory is the worktree at `/Users/dan/code/lobby_analysis/.worktrees/extraction-harness-brainstorm`.
- Multi-committer caution: do **not** touch `phase-c-projection-tdd` or `oh-statute-retrieval` branches/worktrees. Phase 5.1 writes a file at a path that *will be* under `phase-c-projection-tdd`'s control after merge — if a local worktree for that branch exists, ask the user before writing into it.
- Commit boundary: one logical change per commit. Phases 3 and 4 each have a brainstorm step that produces no commit, then a RED test commit, then an implementation commit.
- Per-phase commit message prefix: `fix(compendium):`, `docs:`, `tools:`, `models_v2:`, `handoff:` per the conventional style on this branch.
- The `0ccbb86` parallel-harness-review convo file (`docs/active/extraction-harness-brainstorm/convos/20260514_post_framing_harness_review.md`) is currently uncommitted in the worktree; **do not absorb it** into any commit in this plan — its parent session on `main` hasn't finished its own finish-convo yet. Leave it untracked for that session to pick up.
- This plan does **not** rebuild the v2 TSV from scratch; Phase 1.1 Option A regenerates only OS-1's status cell via the existing canonicalize script. Verify byte-identity on the other 180 rows.

## What could change

- **Phase 1.1 (status drift):** if the user is mid-flight on a separate rename/freeze branch that will touch the TSV anyway, defer Phase 1.1 to that branch.
- **Phase 2 (row_id tool):** if the existing CI workflows already have a row_id consistency gate (unlikely but worth grepping), this phase is redundant.
- **Phase 3 (EvidenceSpan):** if the user wants the brainstorm done in a fresh research session rather than inline in the implementation flow, Phase 3 becomes "brainstorm-only, defer implementation." Easy to split.
- **Phase 4 (axis_coverage):** same — could be split into brainstorm-only-now, implement-later.
- **Phase 5 (handoffs):** if the user wants to also write the orchestrator full impl plan (rather than just the placeholder note in Phase 1.2), that's a substantial scope expansion (probably a separate plan).

## Questions

Each is for the user to answer before or during execution. Some are decision-points the fresh agent should surface via AskUserQuestion at the right phase.

1. **Phase 1.1 — Option A (regen TSV) or Option B (doc fix)?** Recommendation in plan: Option A is more discoverable; Option B is cheaper. Default: ask.
2. **Phase 2 — Does this tool's CI integration go in scope or stay manual?** Plan defaults to manual (pre-merge invocation by humans). Auto-CI is a separate (small) plan.
3. **Phase 3 — Option A / B / C for `EvidenceSpan`?** Plan strongly leans Option A; Option C is the richest; Option B is the path-of-least-scoring-v2-work. The fresh agent must surface this and not pre-lock.
4. **Phase 4 — Option A (`axis_coverage` field) or Option B (type split)?** Plan recommends Option A. Surface to user; do not pre-lock.
5. **Phase 5.1 — Where does the C-F1 handoff file live if the `phase-c-projection-tdd` worktree isn't on this machine?** Plan suggests writing to the path on whichever worktree exists; the file's pull-through to the right branch happens on merge.
6. **Scope question for the user up-front:** is this plan the right shape, or do you want it split into 2-3 smaller plans (one per finding category)? Doing it as one plan keeps the framing coherent; splitting it makes parallel execution possible.
7. **Should the parallel harness review's convo file (`20260514_post_framing_harness_review.md` — currently untracked in the worktree) be finished out as part of this plan, or do you want to finish-convo it from its parent `main` session separately?** Plan defaults to "leave it alone for the parent session" per multi-committer rules; user can override.

---
