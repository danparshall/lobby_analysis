# Research Log: extraction-harness-brainstorm

Created: 2026-05-14
Purpose: Track B successor branch (per Option B locked 2026-05-13). Brainstorm-then-plan: design the **single** extraction harness / prompt architecture per the Compendium 2.0 success criterion #2 ("ONE extraction pipeline — same prompt structure, same model, same retrieval approach, applied uniformly across rows, states, and years"). The v2 row set (181 rows) is the input contract. Goal of this branch's kickoff session: a written plan (`docs/active/extraction-harness-brainstorm/plans/`) ready for the first TDD implementation session.

> **Predecessor:** Cut off `main` at `8bfc225` post-archive of `compendium-source-extracts` (merged 2026-05-14 as `cac1469`; archived to `docs/historical/compendium-source-extracts/`).
>
> **Row-freeze contract:** [`compendium/disclosure_side_compendium_items_v2.tsv`](../../../compendium/disclosure_side_compendium_items_v2.tsv) — 181 rows. Promoted from `docs/historical/...` to repo-level `compendium/` on 2026-05-14 by the `compendium-v2-promote` branch (live contract for the two parallel-running successors; v1 artifacts retained at `compendium/_deprecated/v1/`). Decision log at [`20260513_row_freeze_decisions.md`](../../historical/compendium-source-extracts/results/projections/20260513_row_freeze_decisions.md). Idempotent regen via `tools/freeze_canonicalize_rows.py`. (Path is live on main after `compendium-v2-promote` merges; until then read via the worktree-local view.)
>
> **Compendium 2.0 success criterion:** see the ⭐ section in [`../../../STATUS.md`](../../../STATUS.md). This branch is direct work on criterion #2 (ONE extraction pipeline).
>
> **Carry-forward prompt architecture (from now-dead `statute-extraction` iter-2):** the v2 scorer prompt + chunk-frame preamble (`src/scoring/chunk_frames/definitions.md`) + tightened row-description axis labels. Iter-1 dispatched against OH 2025 `definitions` chunk achieved 93.3% inter-run agreement (3 temp-0 claude-opus-4-7 runs); the materiality-gate canary captured `required_conditional` + verbatim `condition_text` across all three regimes. **Note:** iter-2's tightened row descriptions targeted the v1.2 (141-row) compendium and may need redoing against the v2 (181-row) compendium.

## Out of scope for this branch

- Multi-vintage OH statute retrieval — that lives on `oh-statute-retrieval` (Track A).
- Per-rubric projection function implementations — that lives on `phase-c-projection-tdd`.
- Full 50-state rollout — this branch's deliverable is a *single-state pilot-ready* plan + harness, not 50-state production scale.

## Data symlink note

The `data/` symlink convention from `skills/use-worktree/SKILL.md` was **skipped at branch creation** because (a) `data/` is now fully gitignored post-2026-05-14 rename (`data/compendium/` → repo-root `compendium/`) so the prior conflict is resolved but (b) on this machine no gitignored data under `data/` actually exists yet to share. When this branch's first kickoff session generates gitignored data (e.g., extraction runs, scoring results), the kickoff agent should decide its own symlink approach at that point.

---

## Sessions

(Newest first.)

### 2026-05-14 (research arc doc) — three-prong arc + Prong 1 internals + Ralph loop doc landed on main

Convo: [`convos/20260514_research_arc_doc.md`](convos/20260514_research_arc_doc.md)
Doc: [`docs/RESEARCH_ARC.md`](../../../RESEARCH_ARC.md) (repo-level; main `86dc02e`, this branch `ee75e3a`)

**Started as a branch-status query, evolved into a research-arc review with three user-initiated reframes of the agent's mental model, and produced one repo-level doc landed on main via cherry-pick.** No code changes; no extraction-harness component movement; no plan revisions. Pure framing work that hardens the project's link graph for future agents (and other fellows).

**The three reframes** (corrections to agent framing, all from user):

1. **Phase C is the Ralph-loop evaluation function, not a downstream sanity-check.** No 50-state typed-cell ground truth exists — that's the gap this project fills — so projecting our extracted cells back into each rubric's published scoring rule and comparing to published per-state scores is the only tractable accuracy signal for Prong 1. The Ralph loop closes via that signal.
2. **Prong 2 + Prong 3 is the product; Prong 1 is upstream scaffolding.** The SMR encodes what each state's regime *legally requires*; the gap vs. what portals *actually expose* is itself a research artifact. Prong 1 also makes Prong 2 dramatically cheaper (shared typed-cell schema across 50 state pipelines instead of 50 bespoke extractors). "Stairs of leverage" pattern: prior-art rubrics → Prong 1 (via Phase C eval); Prong 1 → Prong 2.
3. **Locked rubric order is mostly convenience, not a rigid signal-strength gradient.** Order respects dependencies (Newmark 2005 → Newmark 2017; HG 2007 → Track A's HG retrieval sub-task) and starts where ground truth is strongest, but reordering on empirical results is fine.

**Ralph-loop concretization** (added to the doc after user provided the loop shape): objective `loss(prompt) = Σ over (state, vintage, rubric) |f_rubric(SMR) − published_score|`; single scalar. Noise floor `σ_noise` from independent re-runs is a prerequisite (otherwise the loop chases 1σ flukes). Three risks named up front: implicit weighting in `Σ |diff|` across unequal-size rubrics; Goodhart on projection-distance (rubrics have degenerate solutions); cost asymmetry (single-state OH-only ≈ $4/iter vs 50-state ≈ $150/iter under ARCHITECTURE.md's $50–500/mo budget). Track A's across-vintage stability check is the only signal that *doesn't* go through a rubric — load-bearing for Goodhart defense.

**Cross-track milestone surfaced:** the first Ralph-loop iteration end-to-end needs three things landed across three branches simultaneously — `scoring_v2` (this branch) + CPI 2015 C11 projection (`phase-c-projection-tdd`) + OH 2015 statute bundle (`oh-statute-retrieval`). Named in the doc. This walks back an earlier agent overclaim that "harness feature-complete for a single-state pilot after scoring_v2 ships" — that's *extraction-complete*, not *quality-validated*.

**Mid-session fast-forward:** integrated 2 unseen commits on `origin/extraction-harness-brainstorm` (`5f262e9` fixture decouple + `7d6f20d` desktop T1 convo) before the new doc commit. No conflicts; no file overlap with `docs/RESEARCH_ARC.md`. Doc's `retrieval_v2` status line ("T1 smoke validated on desktop") happened to land consistent with the just-pulled RESEARCH_LOG state.

**Cherry-pick path executed cleanly:** `git pull --ff-only` on this branch → commit doc (`ee75e3a`) → switch to main worktree (already at `f6cf909` from session-start fetch, fast-forwarded by `compendium-naming-docs` PR #10 merge during the session) → `git cherry-pick ee75e3a` (clean; lands as `86dc02e`) → push both branches. Multi-committer rules respected throughout.

**Discoverability follow-up deferred per user.** `README.md`'s repo-layout section doesn't reference `docs/RESEARCH_ARC.md`. Easy one-line edit when desired.

**Next session.** Brief-writer/scorer-v2 implementation plan per the prior session's outstanding handoff at [`plans/_handoffs/20260514_brief_writer_impl_plan_write_handoff.md`](plans/_handoffs/20260514_brief_writer_impl_plan_write_handoff.md). That's the actual next work session; the research-arc doc was a sidebar that happened to fit cleanly here.

### 2026-05-14 (retrieval impl T1 + fixture decouple) — desktop T1 cleared; parser fixture decoupled from integration write path

Convo: [`convos/20260514_retrieval_v2_t1_and_fixture_decouple.md`](convos/20260514_retrieval_v2_t1_and_fixture_decouple.md)
Predecessor: [`convos/20260514_retrieval_implementation.md`](convos/20260514_retrieval_implementation.md) (laptop shipped retrieval_v2 at T0 with T1 deferred)
Concurrent: [`convos/20260514_brief_writer_brainstorm.md`](convos/20260514_brief_writer_brainstorm.md) (parallel session; clean fast-forward, no file overlap)

**Cleared the T1 smoke gate on the desktop machine.** Ran `uv run pytest tests/test_retrieval_v2_integration.py` against the real Anthropic Citations API: **3/3 passed in ~21s, ~$0.06** (three separate `messages.create` calls). Real API attaches citations to text blocks, fires `record_cross_reference` tool calls on the tiny statute fixture, and parser yields valid `RetrievalOutput` with non-empty `evidence_spans`. T1 cleared on first try; no SDK auth/schema/400 issues; Opus 4.7's adaptive `thinking` block confirmed present in real responses (parser passes through, matches plan's documented behavior).

**Then 3 parser unit tests went red** — exactly the failure mode the laptop convo's "Open Questions" section pre-flagged. Diagnosis: NOT a parser bug; **test design coupling**. The integration test's side-effect-write to `sample_response.json` (same file parser unit tests consume) caused hand-crafted-shape-specific assertions to break against the new real-shape data: (1) hardcoded `§311.005` literal in pairing test where real fixture has `§99.005`; (2,3) two tests asserting on `unresolvable_references[0]` / `len == 1` where real fixture has zero unresolvable refs (agent didn't emit any — the tiny 2-sentence statute has no unresolvable cross-refs to emit).

**Per Phase 7 of the retrieval impl plan ("pause-and-surface, don't silently patch"), surfaced to user with full diagnosis and 3 options.** User locked **Option A: split fixture paths**:

- `tests/fixtures/retrieval_v2/sample_response_handcrafted.json` (committed, md5 `d2e3fe0a…` — pristine from laptop session) → parser unit tests pin here; exercises edge cases real API may not naturally produce on a tiny fixture (mixed tool types, multi-tool buffer reset invariant).
- `tests/fixtures/retrieval_v2/sample_response_real.json` (gitignored) → T1 writes here as ad-hoc local-inspection aid; no test consumes it.

**Did NOT silently patch the parser or dumb-down the unit tests to match the new fixture shape** — both would have lost real coverage signal. The optional shape-tolerant-against-real-fixture test was punted under YAGNI (T1 itself tests parser-against-real on every desktop run).

**One commit** (`5f262e9`): rename `sample_response.json` → `sample_response_handcrafted.json` (100% similarity preserved in git), gitignore rule for `sample_response_real.json`, 2 test-file path edits + docstring cleanup, ruff clean. Post-fix state: parser unit suite 8/8, full retrieval_v2 unit suite 48/48, T1 re-run against new path 3/3 (verified the rename works end-to-end against real API; second ~$0.06 spent).

**Surfaced for future work (NOT done this session):**

- **`thinking` block in parser docs.** Now empirically confirmed in Opus 4.7 real responses; parser handles transparently but `parser.py` docstring may not mention this as a tested path. Quick fix when scoring_v2 next touches the parser.
- **Unresolvable-reference live-test.** Currently un-exercised against real API; tiny_statute.txt is too clean. Would need a deliberately-messy fixture (phantom section reference, ambiguous "the act"). Worth raising in scoring impl, where `record_unscoreable_cell` has an analogous untested path.
- **Permissions/uv-resolution finding.** `uv run pytest` from inside the worktree resolves to the worktree's `.venv` correctly (despite parent shell's `VIRTUAL_ENV` pointing at main) — uv emits a diagnostic warning then ignores the env var. Updated the prior memory note (`feedback_pytest_in_worktree.md`) with an addendum: the safe sequence is `uv sync --extra dev` from inside the worktree first, then `uv run pytest …`. Also matches the pre-approved `Bash(uv *)` rule, avoiding permission prompts that `.venv/bin/pytest` triggers.

**Sequencing unchanged:** cells ✓ → chunks ✓ → **retrieval ✓ (T0 + T1)** → brief-writer (brainstorm done concurrently, impl plan write next per its handoff) → practical-axis sibling brainstorm.

### 2026-05-14 (brief-writer brainstorm) — all 10 Q's + 2 pushbacks locked; impl-plan-write handed off

Plan sketch: [`plans/20260514_brief_writer_plan_sketch.md`](plans/20260514_brief_writer_plan_sketch.md)
Convo: [`convos/20260514_brief_writer_brainstorm.md`](convos/20260514_brief_writer_brainstorm.md)
Outgoing handoff: [`plans/_handoffs/20260514_brief_writer_impl_plan_write_handoff.md`](plans/_handoffs/20260514_brief_writer_impl_plan_write_handoff.md)

**Brainstormed the v2 scoring harness (legal-axis path) end-to-end with user-in-loop; all architectural Q's locked.** Two pushbacks against the prior session strategy accepted in the opening exchange before any plan-sketch was written:

1. **Combine brief-writer + scorer-prompt-rewrite into ONE component.** Kickoff handoff split them; retrieval's experience (prompt and brief-writer ship in one session, tightly coupled — brief-writer reads prompt at call time, prompt assumes brief-writer's tool definitions) said split was wrong. User agreed.
2. **Follow retrieval's SDK + Citations + tool use pattern.** Effectively makes the deferred-SDK-adoption decision a settled question — retrieval already added `anthropic>=0.102` to `pyproject.toml`. "ONE pipeline" criterion consistency. User agreed.

**Locked package (full audit trail in convo's "Decisions made" table + "Locked package (synthesis)" section):**

- **Q6: Practical-axis cells → DEFER to sibling brainstorm.** Second pushback against the user's "combine" decision: combine was about prompt+brief-writer *for legal scoring*, not legal+practical. v1 had 2 brief-writers (`build_subagent_brief` portal, `build_statute_subagent_brief` statute) for exactly this reason. Citations API behavior on portal HTML/PDF empirically unmeasured. This component's scope is legal-axis only; mixed chunks score only their legal cells; practical-axis (50 cells + practical halves of 5 dual-axis rows) becomes the next sibling brainstorm.
- **Q4: Optional disk-loaded preambles, ship 0.** `src/scoring/chunk_frames_v2/<chunk_id>.md` if present, else skip silently. The scholarly v2 rewrite of v1 Rule 6 (PRI A5-A11 + C0 functional-public-entity substantive guidance) lands in preambles when authored — empirical-informed by T1+ evidence of where the model under-grounds. Impl plan ships 0 preambles.
- **Q1: Parameterized `chunks: list[str]`, default per-chunk.** Mirrors retrieval; accuracy-first; iter-1's 7-row baseline is the comparison point.
- **Q2: Single polymorphic `record_cell` + `record_unscoreable_cell`.** 2 tools total, mirrors retrieval's surface. Parser dispatches by `row_id` → `CompendiumCellSpec.expected_cell_class`. Per-cell-type (15) tools deferred until T2+ evidence shows the model mis-types values.
- **Q3: All statutes + retrieval annotations as user text.** Same statute set retrieval consumed — cache-friendly cross-call sharing. RetrievalOutput's cross_references summarized in user text (relevance + chunk_ids_affected + key evidence_spans).
- **Q7-sub: Separate `UnscoreableCell` + `record_unscoreable_cell` tool.** Direct parallel to retrieval's `UnresolvableReference` / `record_unresolvable_reference`. No `CompendiumCell` wrapper field churn. Symmetric `ScoringOutput.cells` + `ScoringOutput.unscoreable_cells`.
- **Q7-rules: v1 rule-by-rule disposition.** Drop 1, 7 (Citations + tool-use enforce); replace 6 (preambles), 8 (tool-use); morph 3 (parser validates per-cell-type); keep 2 (escape valve = Q7-sub), 4 (confidence), 5 (read full statute layered — promoted load-bearing).
- **Q8: `CompendiumCell.provenance` → `tuple[EvidenceSpan, ...]`.** Mirror retrieval; Citations returns multiple spans per claim; low blast radius (Phase C consumer-side not yet ramped); impl-plan-writer audits existing fixture usages.
- **Q9: `ScoringOutput` Pydantic model mirroring `RetrievalOutput`.** Scoped to one call: `(state_abbr, vintage_year, chunk_id)` + `cells` + `unscoreable_cells` tuples.
- **Q10: `src/lobby_analysis/scoring_v2/` + `src/scoring/scorer_prompt_v2.md`.** Boring; mirrors retrieval naming; no broader reorg.

**Six locked Q's mirror retrieval directly** (Q1, Q2, Q3, Q7-sub, Q8, Q9, Q10). Symmetry is intentional — process inertia at the architectural-pattern layer reduces review surface and gives a code-reviewable parallel structure across the two LLM-calling modules.

**Things this brainstorm is locking blind on** (3, flagged in convo + handoff): Citations API + tool use composition under longer statutes + more tool calls per response (retrieval's T1 smoke is the canary); `CompendiumCell.provenance` schema change tolerance (Phase C consumer-side); practical-axis brief-writer feasibility (entirely deferred).

**Session strategy: hand off to impl-plan-write session.** User chose the handoff option over writing the impl plan in this session. Outgoing handoff specifies: write `plans/20260514_brief_writer_implementation_plan.md` — TDD-shaped, API-launchable, mirror retrieval impl plan structure (inline the full v2 prompt + tool schemas; list 30+ test signatures by name; phase-by-phase commit boundary). The impl-plan-writer does NOT re-litigate locked decisions; it translates them. Cycle continuation: brainstorm done → impl-plan-write next → impl session in API-launched sub-branch after.

**Process notes.** (1) Agent pushed back on the kickoff handoff's 4-component framing **before** writing the plan-sketch — the sketch reflects the consolidated framing rather than re-litigating the handoff's split mid-document. (2) Two architectural pushbacks batched into a single AskUserQuestion call; both accepted; saved a round-trip. (3) Per the user memory note about doc system being persistent memory, not patchwork: drafted plan-sketch + brainstorm convo before any Phase-2 Q calls so the link graph was consistent at every commit boundary. Plan-sketch carries a "Brainstorm outcome" back-link at the top to the convo's locked decisions; convo carries forward-links to plan-sketch + handoff; handoff carries back-links to convo + plan-sketch + retrieval impl plan + retrieval impl convo. (4) Second pushback (Q6 = defer practical) was a deliberate re-fork of the kickoff "combine" decision on a different seam — surfaced explicitly. (5) Six of 10 Q's locked on agent's "mirror retrieval" hunches; one Q4 deferred scholarly work (v1 Rule 6 content not rewritten this session — lands in preambles when authored, downstream).

**Next session.** Impl-plan-write per the outgoing handoff. After impl-plan ships, two paths in parallel: (a) implementation session in API-launched sub-branch executing the plan under strict TDD; (b) **practical-axis brief-writer brainstorm** as sibling component — covers the 4 practical-only chunks + practical halves of 5 dual-axis chunks; depends on cells + chunks + this session's `scoring_v2` model bindings.

### 2026-05-14 (retrieval impl) — retrieval_v2 module landed under strict TDD; T1 smoke deferred to desktop

Convo: [`convos/20260514_retrieval_implementation.md`](convos/20260514_retrieval_implementation.md)
Plan executed: [`plans/20260514_retrieval_implementation_plan.md`](plans/20260514_retrieval_implementation_plan.md)
Originating brainstorm: [`convos/20260514_retrieval_brainstorm.md`](convos/20260514_retrieval_brainstorm.md)

**Executed the retrieval implementation plan end-to-end under strict TDD on the laptop (Dans-MacBook-Air).** 51 RED tests written first (commit `a5d05c5`), then five GREEN commits each turning one test file green in sequence. **T0 unit gate is fully green** (full suite 400 → **448 pass** = +48 retrieval_v2 tests); 3 pre-existing `test_pipeline.py` FileNotFoundErrors unchanged from baseline. **T1 smoke (integration test against the real Anthropic Citations API) is deferred to a desktop run** — laptop has no `ANTHROPIC_API_KEY`; user flagged this mid-session and asked to defer T1 explicitly. Integration test machinery is in place: `tiny_statute.txt` fixture committed; `tests/test_retrieval_v2_integration.py` skips cleanly without the key (verified `3 skipped in 0.01s`). Desktop run = `uv run pytest tests/test_retrieval_v2_integration.py` with key in env.

**The deliverable: `src/lobby_analysis/retrieval_v2/`.** Five thin modules:

- `tools.py` — `CROSS_REFERENCE_TOOL` + `UNRESOLVABLE_REFERENCE_TOOL` JSON-schema definitions. `chunk_ids_affected.enum` sourced from `build_chunks()`; **coupling test** (`test_cross_reference_tool_chunk_ids_enum_matches_chunks_manifest`) enforces no drift between this tool schema and the chunks manifest.
- `models.py` — frozen Pydantic models. `EvidenceSpan` (polymorphic over the 3 documented Citations API citation types); `CrossReference` / `UnresolvableReference` (`evidence_spans: tuple[EvidenceSpan, ...]` from preceding text blocks); `RetrievalOutput` (scoped to `(state_abbr, vintage_year, hop)` with hop ∈ [1, 2]).
- `brief_writer.py` — `build_retrieval_brief(state, vintage, statute_bundle, chunks, url_pattern="")` returns the `messages.create()` kwargs dict. Does **not** call the SDK; the orchestrator dispatches. Model `claude-opus-4-7`, `thinking={"type": "adaptive"}`, `output_config={"effort": "high"}`, no sampling params (would 400 on Opus 4.7). System block + document blocks both ephemeral-cached.
- `parser.py` — `parse_retrieval_response(message, state_abbr, vintage_year, hop)`. Polymorphic over SDK `Message` objects (attr access) and JSON dicts (key access) — same path works for fixtures + real responses. Pairing rule: citations on text blocks accumulate; on `tool_use` block, buffer flushes onto that tool's `evidence_spans` and resets. Unknown tool names still reset (prevents stale spans bleeding into next valid call). Other block types (`thinking`, `server_tool_use`) pass through.
- `__init__.py` + `docs.md` — 9 public names; module-level docs matching `chunks_v2`/`models_v2` pattern.

Plus `src/scoring/retrieval_agent_prompt_v2.md` — the v2 prompt (chunk-anchored, zero PRI rubric leakage, Rule 5 instructs "cite before each tool call" making the parser's pairing rule non-vacuous).

**Plan deviations surfaced and resolved (2, both flagged in convo).**

1. **Phase ordering (P6 → P4 → P5).** The brief_writer reads the prompt file at call time (`_PROMPT_PATH.read_text()` inside `build_retrieval_brief`), so Phase 6 (write `retrieval_agent_prompt_v2.md`) had to land before Phase 4 (brief_writer) for tests to clear. Commit messages preserve plan-numbered phase names ("Phase 6 of plan", "Phase 4 of plan") so the audit trail stays intact.
2. **Cell roster format.** Plan's `_format_cell_roster` used `spec.description[:120]`, but `CompendiumCellSpec` has only `(row_id, axis, expected_cell_class)` — no description. The underlying compendium TSV also has no description column (only provenance fields: `rubrics_reading`, `n_rubrics`, `notes`). Adapted format to `- {row_id} ({axis}) [{cell_class}]` per cell; row_ids are self-describing in this codebase.

**Surfaced for user / next agent: side-effect in `test_parser_handles_real_api_response`.** Plan design has the integration test write the real API response to `tests/fixtures/retrieval_v2/sample_response.json` on every successful run (overwriting the hand-crafted fixture from Phase 5). Functionally that means parser unit-test fixture churns across runs; pro/con argument in the convo. Plan author chose pro; if fixture-churn-induced parser flakes show up at T2+, gate the write with `if not SAMPLE_RESPONSE_PATH.exists():`. Not changing until the user weighs in or T2-T4 show real noise.

**Commits this session (8):** `a5d05c5` RED tests → `191873b` tools.py (P2) → `16beb1d` models.py (P3) → `1686474` prompt.md (P6, executed early) → `97a3fee` brief_writer.py (P4) → `aab535f` parser.py + fixture (P5) → `22703fa` tiny_statute.txt (P7 prep) → `d1fa512` exports + docs.md + ruff (P8).

**Next session.** Either: (a) **desktop T1 run** — Dan runs `uv run pytest tests/test_retrieval_v2_integration.py` on Dans-MacBook-Pro with `ANTHROPIC_API_KEY`; on success the test side-effects `sample_response.json` with the real shape; if parser unit tests then go red, pause-and-surface (per plan Phase 7 'Things that may go wrong'). Or (b) **brief-writer brainstorm** — the cleaner next downstream component (orthogonal to retrieval; depends only on cells + chunks, both shipped). Plan-sketch → brainstorm → impl-plan cycle, same convention as chunks and retrieval. Scorer-prompt rewrite is the fourth component; depends on retrieval bundle shape (now known: `RetrievalOutput.cross_references[*].evidence_spans` carries cited statute support).

### 2026-05-14 (chunks impl) — chunks_v2 module landed under strict TDD (Phases 0-7)

Convo: [`convos/20260514_chunks_implementation.md`](convos/20260514_chunks_implementation.md)
Plan executed: [`plans/20260514_chunks_implementation_plan.md`](plans/20260514_chunks_implementation_plan.md)
Handoff consumed: [`plans/_handoffs/20260514_chunks_implementation_handoff.md`](plans/_handoffs/20260514_chunks_implementation_handoff.md)

**Executed the chunks implementation plan end-to-end under strict TDD.** 24 tests written first (RED, commit `8450bd6`), then five GREEN commits in sequence — each turned exactly its target test file green. Full repo suite went **374 → 400 pass** (+26 chunks tests), 5 skip, 3 pre-existing `test_pipeline.py` `FileNotFoundError`s unchanged (user-approved baseline carried from the cell-models session).

**The deliverable: `src/lobby_analysis/chunks_v2/`.** A pure-data partition layer parallel to `models_v2/`:

- `chunks.py` — `Chunk` and `ChunkDef` frozen dataclasses (both validated by `__post_init__`: snake_case `chunk_id`, non-empty tuple `cell_specs` / `member_row_ids`, `axis_summary ∈ {legal, practical, mixed}`) + `build_chunks(registry=None, manifest=None) -> list[Chunk]`.
- `manifest.py` — `CHUNKS_V2: tuple[ChunkDef, ...]` — the hand-curated 15-chunk manifest covering 181 TSV rows = 186 cells, verified against the real registry both at plan-write time and in Phase 0 of this session.
- `__init__.py` — public exports: `Chunk`, `ChunkDef`, `build_chunks`, `CHUNKS_V2`.
- `docs.md` — module-level documentation with the 15-chunk table + invariant summary + downstream-consumer pointers.

**Plan deviations surfaced and resolved (3, all minor):**

1. **Architecture-diagram vs Phase-2-wording inconsistency.** The plan placed `ChunkDef` in `manifest.py` per the diagram, but Phase 2 said to implement both `Chunk` and `ChunkDef` in `chunks.py`. Went with Phase 2 wording — splitting `ChunkDef` into `manifest.py` would have induced a circular import once `build_chunks()` lands (chunks.py needs `CHUNKS_V2`; manifest.py would need `ChunkDef`). Recorded in convo + commit `487e713`.
2. **`build_chunks(manifest=CHUNKS_V2)` default-arg circular import.** Rewrote as `manifest: tuple[ChunkDef, ...] | None = None` with a lazy `from .manifest import CHUNKS_V2` inside the function body. Same caller behavior; eliminates the module-load cycle. Commit `c98ebd0`.
3. **`ChunkDef.__post_init__` snake_case regex fix.** Plan's draft used `chunk_id.replace("_", "").isalnum() and chunk_id[0].isalpha()` which lets `"BadCaps"` through. Replaced with `re.fullmatch(r"^[a-z][a-z0-9_]*$", chunk_id)` to match the plan's test #4 explicitly. Commit `487e713`.

**No manifest refinements applied this session.** The plan flagged 3 potential refinement targets (the 2-row `enforcement_and_audits` chunk, the `other_lobbyist_filings` catch-all assignment of `lobbyist_or_principal_spending_report_includes_contributions_received_for_lobbying`, the legal/practical mix in `oversight_and_government_subjects`). All hold under the partition invariant; brief-writer brainstorm can revisit if a real reason surfaces.

**Phase-by-phase invariant: each phase's commit turns its target test file green.** Pre-flight reads + handoff verification confirmed working tree clean, `4c49888 retrieval_v2: scaffolding` from the prior killed session on HEAD (left untouched per handoff), and `src/lobby_analysis/chunks_v2/` non-existent on any branch. Phase 0's one-off coverage script (`/tmp/verify_chunks_coverage.py`) confirmed 186/186 cell coverage against the real registry — no TSV drift since plan-write time.

**Commits this session (7):** `087edb6` scaffolding → `8450bd6` RED tests → `487e713` Chunk+ChunkDef → `b9731ee` CHUNKS_V2 manifest → `c98ebd0` build_chunks → `54949c4` __init__ exports → `65fa872` ruff format pass.

**Next session.** Retrieval implementation sub-branch is unblocked — Phase 1 onward of [`plans/20260514_retrieval_implementation_plan.md`](plans/20260514_retrieval_implementation_plan.md) can now run (Phase 0 already shipped at `4c49888` from the killed parallel session; this session deliberately did not touch `retrieval_v2/`). After retrieval lands, brief-writer is the cleaner next brainstorm (orthogonal to retrieval; depends only on cells + chunks, both shipped); scorer-prompt rewrite waits on retrieval bundle shape.

### 2026-05-14 (pickup) — Retrieval brainstorm completed; Citations API pivot; impl plan written

Convo: [`convos/20260514_retrieval_brainstorm.md`](convos/20260514_retrieval_brainstorm.md) (Phase 2 added — locked Q's + audit table)
Plan: [`plans/20260514_retrieval_implementation_plan.md`](plans/20260514_retrieval_implementation_plan.md) — TDD-shaped, API-launchable
Handoff consumed: [`plans/_handoffs/20260514_retrieval_brainstorm_handoff.md`](plans/_handoffs/20260514_retrieval_brainstorm_handoff.md)

**Resumed retrieval brainstorm at Phase 2** per handoff. Re-engaged with the aggregate-cost lens explicitly surfaced (~8,000 calls per design cycle for per-chunk dispatch vs ~800 for per-(state, vintage); 10× delta). Initial agent recommendation was per-(state, vintage) on cost grounds — **user pushed back**: "If it's dirt cheap but only 50% accuracy, that's not actually a win." Re-anchored on **accuracy gate before cost optimization**. Q1 lock: parameterized `chunks: list[str]` dispatch unit, default per-chunk for experiments; iter-1's 93.3% baseline is the per-chunk-against-7-cells comparison point. Batches up empirically (tiny fixture → 1 chunk → N chunks → 50 states × 4 vintages) — never commit to full rollout without intermediate accuracy data.

**Citations API pivot.** Mid-Phase-2, user surfaced the Anthropic **Citations API** as a feature the prior session hadn't considered. This is load-bearing: Citations structurally enforces provenance grounding (every cited claim has a verbatim span pointing back to a source document). Verified the current API surface via WebFetch of [`platform.claude.com/docs/en/build-with-claude/citations.md`](https://platform.claude.com/docs/en/build-with-claude/citations.md): GA, no beta header, works on `claude-opus-4-7`. Three document types supported (plain text → char-level citations, PDF → page-level, custom content → block-level); we use plain text since we have `papers/text/` extractions. **Hard incompatibility:** Citations + Structured Outputs (`output_config.format`) → 400 error — so v1's strict JSON output schema can't be enforced via structured outputs. **Solution:** tool use. Define `record_cross_reference` and `record_unresolvable_reference` tools; agent calls one per finding; citations attach to text blocks preceding each tool call as machine-verified provenance. Tool use **is** compatible with citations.

**Locked package** (full rationale in convo Phase 2):

- Q1: parameterized dispatch unit (`chunks: list[str]`), default per-chunk
- Q2: tool use (α) replacing JSON output schema; `chunk_ids_affected` is a tool input field
- Q3: chunk-name + count + descriptive anchors (not cell-row-id enumeration; not chunk-name-only)
- Q4: cell-aware at input, chunk-coarse at output
- Q6: prompt markdown + Python brief-writer + tool definitions + parser + Pydantic models (full Python module — brief-writer no longer YAGNI)
- Q7: `src/scoring/retrieval_agent_prompt_v2.md` + `src/lobby_analysis/retrieval_v2/`
- SDK: `anthropic>=0.102` added to `pyproject.toml` (closes deferred kickoff Q; current version verified via PyPI WebFetch 2026-05-14)
- Model/thinking/effort: `claude-opus-4-7`, `thinking={"type": "adaptive"}`, `output_config={"effort": "high"}`; no sampling params (would 400 on Opus 4.7)
- Data dir: `data/retrieval_v2/{state}_{vintage}/` local-only in worktree

**Implementation plan: 10 phases (0-9), 1 commit per phase.** Full v2 prompt markdown inlined in Phase 6 (chunks-plan precedent: load-bearing artifacts are plan-anchored). Full tool schemas inlined in Phase 2 with `chunk_ids_affected.enum` sourced from `build_chunks()` (coupling test catches drift). 30+ test signatures listed by name across 6 test files (tools, models, brief-writer, parser, prompt invariants, integration). **Integration test runs automatically on every `uv run pytest`** when `ANTHROPIC_API_KEY` is set (skipif gate); 2-sentence statute fixture + `max_tokens=2000` keeps cost ≈ $0.02 per run. Empirical validation gates T0-T4 — this plan implements through T1 (smoke test); T2-T4 (single-OH-chunk → multi-chunk → 50-state) are downstream.

**Things this brainstorm + plan is locking blind on** (both author and implementer first-time Citations users; flagged in convo + Phase 7 of plan): citation-to-tool-call attribution behavior (does Claude actually emit cited reasoning before each tool call, or sometimes consolidate at end?); cache_control on document blocks (does it work alongside citations?); tool-use + citations composition; plain-text char-level citation accuracy on `papers/text/` extractions (PDF→text may have non-standard whitespace affecting sentence chunking). **Phase 7 integration test is designed to surface these — instructs implementer to pause and surface to user rather than silently patch the parser if real-API behavior diverges from documented behavior.**

**Process notes.** (1) The pickup session almost locked Q1 on the per-(state, vintage) framing the cost lens favors before catching that the empirical accuracy floor was undefined — user correction in real time reframed the package around accuracy first, cost second. (2) Citations API pivot was substantial: the entire output-schema decision (Q2) and deliverable-shape decision (Q6) had to be rewritten mid-brainstorm. The plan-sketch's `cell_ids_affected: list[tuple[str, str]]` field is gone; the brief-writer that was YAGNI in the pre-pivot package is now load-bearing. Documented the pre-pivot answers in the convo's "Decisions made (audit trail)" table so future readers can see why the lock changed. (3) Saved a real-API-call decision for the implementer (the integration test is the first time Citations API is exercised in this codebase) — explicitly built-in pause-and-surface instructions in Phase 7 of the plan, rather than expecting silent patching.

**Process note 2: user mid-session correction on the cost framing.** When I led with the cost lens for per-(state, vintage) in the AskUserQuestion, the user pushed back with the accuracy floor argument — and I rolled the cost framing back into "secondary to accuracy gate" in the locked package. The aggregate-cost analysis is still in the convo Phase 2 as decision context (it's a real argument that should inform later batch-size scaling), but it doesn't drive Q1's default.

**Next session.** Implementer (separate API-launched sub-branch per user's session strategy) executes the impl plan. After implementation lands, **brief-writer brainstorm** is the cleaner next component (orthogonal to retrieval; depends on chunks + cells which both exist). **Scorer-prompt rewrite** is the fourth component, depends on retrieval bundle shape (which will be known once retrieval lands).

### Addendum (same day, post-finish-convo)

User caught a real defect in the retrieval impl plan: **chunks_v2 was treated as if it had shipped, but the chunks impl has not been executed yet.** Three places in the retrieval plan import from `lobby_analysis.chunks_v2` (tools.py, brief_writer.py, coupling test), so the retrieval implementation hard-blocks on chunks shipping. State of play confirmed:

- `src/lobby_analysis/chunks_v2/` does not exist on any branch (`git log --all -- src/lobby_analysis/chunks_v2/` returns zero commits)
- `src/lobby_analysis/models_v2/` exists and is shipped (cell models complete)
- A parallel agent session had picked up the retrieval impl plan and executed Phase 0 (local commit `4c49888 retrieval_v2: scaffolding (empty module + anthropic SDK dependency)`) before hitting the same dependency wall and stopping; user killed that session
- The 4c49888 commit is a clean Phase 0 execution: adds `anthropic>=0.102` to pyproject.toml + uv.lock, creates empty placeholder files in `src/lobby_analysis/retrieval_v2/` + `tests/fixtures/retrieval_v2/.gitkeep`. Safe to keep; the chunks impl session does not touch retrieval_v2/.

**Remediation:**

- Wrote [`_handoffs/20260514_chunks_implementation_handoff.md`](plans/_handoffs/20260514_chunks_implementation_handoff.md) — chunks impl session handoff for fresh agent. Explains state of play, points at the chunks impl plan, names what NOT to touch (retrieval_v2/ scaffolding from the killed session).
- Added a Prerequisite section + Phase-0-already-done note at the top of [`20260514_retrieval_implementation_plan.md`](plans/20260514_retrieval_implementation_plan.md). Future retrieval impl sessions verify chunks has shipped before proceeding past Phase 0, and skip re-running Phase 0 if the 4c49888 commit is already on HEAD.
- Sequencing for the user's 4-component strategy: cells ✓ done; chunks → retrieval → brief-writer → scorer-prompt is the now-locked implementation order. Chunks unblocks retrieval; retrieval unblocks scorer-prompt (since scorer-prompt benefits from knowing retrieval's bundle shape); brief-writer is parallelizable with retrieval but cleanest to do after chunks.



Plan sketches: [`plans/20260514_chunks_plan_sketch.md`](plans/20260514_chunks_plan_sketch.md) + [`plans/20260514_retrieval_plan_sketch.md`](plans/20260514_retrieval_plan_sketch.md)
Brainstorm convos: [`convos/20260514_chunks_brainstorm.md`](convos/20260514_chunks_brainstorm.md) + [`convos/20260514_retrieval_brainstorm.md`](convos/20260514_retrieval_brainstorm.md) (retrieval in progress)
Implementation plan: [`plans/20260514_chunks_implementation_plan.md`](plans/20260514_chunks_implementation_plan.md)
Handoff: [`plans/_handoffs/20260514_retrieval_brainstorm_handoff.md`](plans/_handoffs/20260514_retrieval_brainstorm_handoff.md)

**Session strategy locked by user: brainstorm-and-plan all 4 downstream components in this branch with user-in-loop, then launch implementations as parallel API sub-branches that merge back.** This session covered component 1 (chunks) end-to-end and component 2 (retrieval) plan-sketch + Phase-1-brainstorm only. Two remain after retrieval (brief-writer, scorer-prompt rewrite).

**Chunks (complete).** Brainstorm resolved 7 Q's. **Critical revision** to the prior brainstorm's Q1 (5-12 rows/chunk): user surfaced prompt-caching architecture (statute in cached `system` block, chunk content in uncached `user`), which makes per-chunk cost largely chunk-size-independent. Revised lock: **~30 row soft cap, 34 hard cap** (for the natural `lobbyist_spending_report` single-chunk cluster). Iter-1's 7-row anchor remains an empirical reference point but is no longer a constraint. **Q3:** same chunk for both halves of all 5 combined-axis rows. **Q4:** `list[Chunk]` frozen dataclass (`chunk_id`, `topic`, `cell_specs: tuple[CompendiumCellSpec, ...]`, `axis_summary`, `notes`). **Q6:** `src/lobby_analysis/chunks_v2/` parallel to `models_v2/`. All locked via AskUserQuestion. Sub-Q's (size bounds Q2, stability mechanism Q5, function signature Q7, manifest storage sub-Q) proposed-and-locked: hand-curated `tuple[ChunkDef, ...]` constant in `manifest.py`; coverage test enforces partition invariant at `build_chunks()` call time; `build_chunks(registry=None) -> list[Chunk]` mirrors cell-models' default-param pattern. **Implementation plan inlines a complete 15-chunk manifest** covering 181/181 rows = 186/186 cells, no duplicates, no typos — verified by plan-author against the real TSV at this branch's HEAD. Chunk sizes range 2 rows (`enforcement_and_audits`, 4 cells via 2 combined-axis rows) to 34 rows (`lobbyist_spending_report`). Spiritual successor to iter-1's 7-row `definitions` chunk is `lobbying_definitions` (15 rows: 6 `def_target_*` + 2 `def_actor_class_*` + 3 `public_entity_def_*` + 4 singletons including `law_includes_materiality_test`).

**Retrieval (in progress).** Plan-sketch enumerates 7 Q's around scope (per-chunk vs per-state-vintage), output schema replacement for `rubric_items_affected`, substantive guidance translation, cell-aware vs cell-agnostic dispatch, deliverable shape (markdown only vs prompt + brief-writer vs prompt + brief-writer + parser), file location. Brainstorm convo's Phase 1 reading complete: identified the v1 prompt's two rubric-coupling sites (Rule 2 "person definition controls A5-A11/C0-C3" substantive anchor; output schema's `rubric_items_affected` field) and computed legal-vs-practical cell breakdown per chunk (5 fully-practical chunks don't need statute retrieval at all). Phase 2 stopped at Q1/Q3/Q6 ask — user wanted to clarify before locking. Four hunches floated in the final exchange (per-chunk retrieval may be cheap under prompt caching; v1 is identify-only not fetch-and-bundle; chunk-level anchors may simplify Q3; per-chunk dispatch may collapse the cell-level output schema in Q2). **User surfaced a load-bearing addendum after the AskUserQuestion:** even if per-chunk dispatch is cheap *per call* under caching, the **aggregate cost** (50 states × ~4 vintages × ~3-5 prompt-tuning iterations × ~10 legal-axis chunks if per-chunk = 6,000-10,000 calls per design cycle, vs ~600-1,000 if per-(state, vintage)) is an order-of-magnitude argument against per-chunk dispatch. This reweights Q1 hunch (i) — the per-call efficiency framing obscured the aggregate-rollout cost. **Next agent finishes this brainstorm + writes the TDD-shaped implementation plan + runs finish-convo;** see [`plans/_handoffs/20260514_retrieval_brainstorm_handoff.md`](plans/_handoffs/20260514_retrieval_brainstorm_handoff.md) for full pickup, including the aggregate-cost lens.

**No code written this session.** Docs only: 6 new files in `docs/active/extraction-harness-brainstorm/` (2 plan sketches, 2 brainstorm convos, 1 implementation plan, 1 handoff). Session is the model for the remaining 2 downstream components (brief-writer, scorer-prompt rewrite) — each follows the same plan-sketch → brainstorm → impl-plan cycle.

**Process notes.** (1) Initial chunks Q1 framing batched 4 options without the "hand-curated manifest" option that ultimately landed — user pushed back on the prompt-caching grounds and asked how many chunks pure first-2-token splitting would produce (53, mostly singletons); revised options exposed the manifest path. (2) Two AskUserQuestion calls hit a UI bug where the user couldn't answer all 4 batched Q's; second call (3 Q's instead of 4) worked cleanly. (3) Initial manifest draft had ~30 row_id typos (missing `_registration_required` suffixes etc.); rebuilt with a coverage-verification script that the implementer should re-run at Phase 0.

**Next session.** Next agent picks up retrieval per handoff. After retrieval lands, components 3 (brief-writer — consumes chunks + cells; orthogonal to retrieval; the cleaner next pick) and 4 (scorer-prompt rewrite — informed by retrieval bundle shape) remain.

### 2026-05-14 — v2 Pydantic cell models implementation (Phases 0-9 under strict TDD)

Convo: [`convos/20260514_v2_pydantic_cell_models_implementation.md`](convos/20260514_v2_pydantic_cell_models_implementation.md)
Plan: [`plans/20260514_v2_pydantic_cell_models_implementation_plan.md`](plans/20260514_v2_pydantic_cell_models_implementation_plan.md)

**Executed the implementation plan end-to-end under strict TDD.** All 68 tests written first (RED, commit `44eee71`), then implementation phases 1-7 turned each phase's tests green in sequence. Phase 8 ran the full suite (374 pass / 5 skip / 3 pre-existing test_pipeline.py failures unchanged from baseline — user-approved). Phase 9 is this entry + STATUS update + finish-convo.

**The deliverable: `src/lobby_analysis/models_v2/` module.** A pure-data typed cell model layer parallel to v1.1 at `src/lobby_analysis/models/` (v1.1 untouched per Q4 decision):

- `cells.py` — `CompendiumCell` ABC (`frozen=True`, wrapper fields: `cell_id`, `conditional`, `condition_text`, `confidence`, `provenance`) + 15 concrete subclasses (BinaryCell, DecimalCell, IntCell, FloatCell, GradedIntCell, BoundedIntCell, EnumCell, EnumSetCell, FreeTextCell + 6 specialized: UpdateCadenceCell, TimeThresholdCell, TimeSpentCell, SectorClassificationCell, CountWithFTECell, EnumSetWithAmountsCell).
- `cell_spec.py` — `CompendiumCellSpec` (frozen dataclass) + `build_cell_spec_registry()` returning the canonical 186-entry `dict[tuple[row_id, axis], CompendiumCellSpec]` (181 TSV rows + 5 legal+practical doublings). Uses a `_CELL_TYPE_PARSER` table + a generic combined-axis splitter — no per-row hard-coding.
- `extraction.py` — `StateVintageExtraction(state, vintage, run_id, cells)` with post-validator enforcing `cell.cell_id` matches its dict key; `ExtractionRun(run_id, model_version, prompt_sha, started_at, completed_at)`.
- `provenance.py` — `EvidenceSpan(section_reference, artifact_path, quoted_span, url)` with 200-char `quoted_span` cap.
- `__init__.py` — public surface: 21 names re-exported.

**Phase 7 cross-module edit:** added `load_v2_compendium_typed() -> list[CompendiumCellSpec]` to `src/lobby_analysis/compendium_loader.py` as the typed wrapper around the registry. Phase C adopts at its own pace; the raw-dict `load_v2_compendium()` is unchanged.

**Specialized cell struct-shape resolution.** The handoff's instruction to read each specialized row's `notes` column turned out to be a partial map of the territory: `notes` carries provenance only (`'single-rubric (focal_2024)'`) or is empty (`UpdateCadenceCell`, `TimeThresholdCell`). Struct shapes live in the source-rubric projection mappings at `docs/historical/compendium-source-extracts/results/projections/{focal_2024,hiredguns_2007,newmark_2017,newmark_2005}_projection_mapping.md`. Surfaced all 6 to user with proposed shapes (anchored to the mappings); user approved all 6. Documented under "Decisions Made" in the convo.

**Unanticipated 7th cell_type.** The TSV has `typed Optional[int_months] (or enum)` for `lobbyist_registration_renewal_cadence` — not catalogued in the plan. User-approved YAGNI mapping to existing `IntCell` (the "months" semantic is documentation; the type stays `int | None`). The "(or enum)" suffix remains in the parser table as documentation.

**Plan's 29-distinct-cell_types claim was off.** Actual: 23 distinct values. Data-driven parser handles this without code change; flagged in convo's Topics Explored.

**Pre-existing CI failures unchanged.** 3 `test_pipeline.py` failures (portal-snapshot fixture data missing — same as on main, same as the previous v2-promote session). User approved leaving them.

**Commits this session (10):** `62daee7` scaffolding → `44eee71` RED tests → `de507f3` EvidenceSpan → `e3de953` ABC+BinaryCell → `5cac6bc` numerics → `ea6faf5` enum/freetext/specialized → `0e1ed2a` registry → `7c882b1` extraction container → `368cc21` exports+typed loader → `c66d808` ruff format pass.

**Next session.** The cell model layer unblocks 4 downstream components (chunk-grouping function, brief-writer module, retrieval-agent v2 generalization, scorer prompt rewrite). Each is its own brainstorm + TDD plan + implementation cycle. Pick one and start with a brainstorm session. SDK-vs-subagent-dispatch decision deferred until the first LLM-calling component lands. Dedicated handoff at [`plans/_handoffs/20260514_next_session_kickoff.md`](plans/_handoffs/20260514_next_session_kickoff.md) — dependency graph, recommendation (chunk-grouping first), cycle convention, and the two deferred decisions (data/ symlink, Anthropic SDK).

### 2026-05-14 — Extraction harness brainstorm (Phase 1 reading + Phase 2 architectural decisions) + first TDD plan

Convo: [`convos/20260514_extraction_harness_brainstorm.md`](convos/20260514_extraction_harness_brainstorm.md)
Plan: [`plans/20260514_v2_pydantic_cell_models_implementation_plan.md`](plans/20260514_v2_pydantic_cell_models_implementation_plan.md)
Antecedent agenda: [`plans/20260514_kickoff_plan_sketch.md`](plans/20260514_kickoff_plan_sketch.md)

**The "real" brainstorm session.** Executed the plan-sketch's Phases 1-3 agenda: read 7 carry-forward artifacts, resolved 6 architectural questions + 1 new one (legal/practical axis split surfaced by Phase 1 reading), wrote the first TDD-able implementation plan.

**Mid-session merge.** `compendium-v2-promote` merged to main as `0a6804f` while this session was running (flagged finding #1: v2 TSV path wasn't actually on main at session start; user merged it mid-session). This branch was then `git merge main`'d to bring the canonical `compendium/disclosure_side_compendium_items_v2.tsv` path live on the worktree before the plan was written, matching `phase-c-projection-tdd`'s pattern (merge, not rebase).

**Phase 2 locked decisions (full rationale in convo).**

- **Q0 (new) — Cell ID space:** `(compendium_row_id, axis_str)` flat 186-key space (181 rows: 126 legal-only + 50 practical-only get one entry; 5 legal+practical get two). User-confirmed via AskUserQuestion. Supersedes `compendium/README.md`'s `{row_id: typed_value}` phrasing for the 5 combined-axis rows.
- **Q1 — Prompt granularity:** Hybrid — chunked-by-domain (5-12 rows) with chunk-frame preambles + per-row instructions, same template across all chunks. Preserves iter-1's empirical 93.3% on the 7-row `definitions` chunk.
- **Q2 — Retrieval approach:** Two-pass (cross-ref walking → bundle scoring), carry forward from `src/scoring/retrieval_agent_prompt.md`. Empirical bundle-size measurement added as downstream task.
- **Q3 — Iteration unit:** Per-(state, vintage) as deliverable unit; per-(state, vintage, chunk) as execution unit. Multi-year reliability tested by running same pipeline against `oh-statute-retrieval`'s 4-vintage OH set.
- **Q4 — v2 Pydantic model shape:** New module `src/lobby_analysis/models_v2/` (user-confirmed); per-cell-type subclasses of `CompendiumCell` ABC; `StateVintageExtraction` container keyed by `(row_id, axis)`; `ExtractionRun` provenance wrapper.
- **Q5 — Conditional / materiality-gate:** Wrapper fields (`conditional: bool`, `condition_text: str | None`), not a cell-type variant. Orthogonal to value type.
- **Q6 — Provenance per cell:** Inside the wrapper (`provenance: EvidenceSpan | None`), not parallel. Matches v1.1 `EvidenceSource`-inside-`FieldRequirement` precedent.

**Findings from Phase 1 reading flagged in convo:**

1. `compendium-v2-promote` was unmerged at session start (resolved mid-session by user merge).
2. **Anthropic SDK is NOT in `pyproject.toml`.** Iter-1 worked via Claude Code subagent dispatch. The v2 harness inherits this pattern; SDK is not added by the first implementation plan.
3. The v2 TSV's 5 `legal+practical` rows carry axis-conditional `cell_type` strings (e.g., `"binary (legal) + typed int 0-100 step 25 (practical)"`), surfacing Q0. Not in plan-sketch's Open Questions; surfaced explicitly to user.

**First implementation plan: v2 Pydantic cell models** (plan-sketch's recommendation, reaffirmed). 9 phases: scaffolding → `EvidenceSpan` → `CompendiumCell` ABC + `BinaryCell` → numeric subclasses → enum/specialized subclasses → `CompendiumCellSpec` registry (186-cell roster) → `StateVintageExtraction` + `ExtractionRun` → `__init__.py` + `load_v2_compendium_typed()` → suite-wide green + lint → RESEARCH_LOG + finish-convo. Pure-data; no LLM calls; unblocks Phase C.

**No code written this session** — docs only: brainstorm convo, implementation plan, this log entry, back-reference annotation in the plan sketch. Implementation work begins in the next session.

### 2026-05-14 — Kickoff orientation + plan sketch (NOT the real brainstorm)

Convo: [`convos/20260514_kickoff_orientation.md`](convos/20260514_kickoff_orientation.md)
Plan: [`plans/20260514_kickoff_plan_sketch.md`](plans/20260514_kickoff_plan_sketch.md)

**Originating context.** This branch was assigned plan-sketch work as a side-effect of the 2026-05-14 coordination session on `compendium-v2-promote` (see [`../../compendium-v2-promote/convos/20260514_compendium_v2_promote.md`](../../compendium-v2-promote/convos/20260514_compendium_v2_promote.md), available post-merge). User wanted a "solidly sketched" plan in `plans/` so the kickoff agent isn't reading skeleton stubs cold.

**Locked decisions carried forward.** This branch owns the v2 Pydantic model rewrite (model shape = extraction output shape; Phase C consumes as a downstream contract). The v2 row contract is at `compendium/disclosure_side_compendium_items_v2.tsv` (181 rows × 8 columns). The ⛔ PRI-out-of-bounds banner is gone — PRI is 1 of 8 rubrics on even footing.

**Sketch contents.** Three-phase agenda for the first real brainstorm session: (1) read carry-forward material (existing `src/scoring/scorer_prompt.md` + `retrieval_agent_prompt.md` on main; `chunk_frames/definitions.md` on `origin/statute-extraction`; predecessor harness plan in historical); (2) resolve 6 architectural questions (prompt granularity, retrieval approach, iteration unit, Pydantic model shape, conditional/materiality cell values, provenance per cell); (3) capture decisions in a follow-up implementation plan with a single TDD-able first component picked. **Recommended first component:** v2 Pydantic cell models — pure-data, easy to TDD, unblocks both this branch and Phase C.

**Open questions flagged for the real kickoff.** Does `oh-statute-retrieval` block first end-to-end test? Phase C's preferred input shape (Pydantic models vs raw dicts)? Where does the v2 model module live (in-place at `src/lobby_analysis/models/` vs new `models_v2/`)?

**Not implementation work.** No code, no tests written; only docs (the convo + plan sketch + this RESEARCH_LOG update + the Row-freeze contract path migration).

