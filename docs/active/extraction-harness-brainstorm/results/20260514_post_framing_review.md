# extraction-harness-brainstorm post-framing review

**Date:** 2026-05-14
**Framing reference:** `docs/RESEARCH_ARC.md` (main `86dc02e`)
**Originating handoff:** `docs/active/extraction-harness-brainstorm/plans/_handoffs/20260514_post_framing_harness_review_handoff.md`

## Top findings that should change what we work on next

1. **[SHOULD-FIX] `EvidenceSpan` is two incompatible types in the public API.** `lobby_analysis.models_v2.EvidenceSpan` (`section_reference`, `quoted_span` ≤ 200 chars, `artifact_path`, `url`) and `lobby_analysis.retrieval_v2.EvidenceSpan` (`citation_type`, `document_index`, `cited_text`, `start_char_index`/`end_char_index` etc.) are two different Pydantic classes both exported as public names of their packages. The scoring_v2 brainstorm Q8 locked `CompendiumCell.provenance: tuple[EvidenceSpan, ...]` — but the field today imports from `.provenance`, while the natural producer of those spans is the Citations API path, which builds the retrieval-shaped one. The scoring_v2 brainstorm convo does not name which class wins, and the handoff just refers to "EvidenceSpan" by short name in the `ScoringOutput.UnscoreableCell` sketch (handoff lines 154–156). The two shapes cannot be unified by aliasing: the section-reference-with-quoted-text shape is statute-axis semantics; the Citations API shape is API-level provenance with char indices. Scoring_v2 needs to either (a) pick one for `CompendiumCell.provenance` and write an adapter, or (b) carry both — a Citations-API `EvidenceSpan` for the raw machine-verified span, and a semantic `EvidenceSpan` (section_reference, quoted_span) derived from it. This decision is downstream of nothing else and should be made explicit before the scoring_v2 impl plan is written; the brainstorm convo's "Locked package" sketch elided it.

2. **[SHOULD-FIX] The Ralph loop has no home in the four-component architecture.** Phase C is now reframed as the eval function `f_rubric(SMR) → score`, the loss is `Σ |f_rubric − published|` over (state, vintage, rubric), and `σ_noise` requires N independent re-runs at a fixed `(prompt, state, vintage)`. None of `models_v2` / `chunks_v2` / `retrieval_v2` / `scoring_v2` (as scoped) is positioned to: (a) invoke extraction with a fixed prompt N times for a noise-floor estimate; (b) batch invoke across (state, vintage, rubric); (c) sum the per-rubric losses into a scalar; (d) diff across prompt versions. "The orchestrator" is named as out-of-scope in every brainstorm convo (chunks line 147; retrieval line 130; brief-writer line 86, 185) but is the thing the Ralph loop actually requires. The four-component branch will deliver an *extraction-complete* harness but not a *Ralph-loop-ready* harness. This was already surfaced in the research-arc convo as a cross-track milestone, but the implication for `scoring_v2`'s scope was not — `scoring_v2` as currently scoped is one `messages.create()` call per `(state, vintage, chunk_id)`, and the harness-of-harnesses that bundles N runs into a `σ_noise` measurement is nowhere in the queue. Either the scoring_v2 impl plan should explicitly carry "expose a programmatic single-call entry point that the future orchestrator can wrap" (a low-cost add) or the Ralph-loop glue should be its own next-after-scoring component, named and scheduled. Recommendation: name it as the next component after scoring_v2 ships, and add to STATUS.md so the orchestrator gap doesn't get rediscovered post-merge.

3. **[OBSERVATION] Practical-axis cells in mixed chunks are an unresolved seam in the typed-cell schema, even though the scope is "legal only".** The brainstorm Q6 lock defers practical-axis brief-writer, and `build_scoring_brief()` is supposed to filter mixed chunks to `axis == "legal"`. But the cell-spec registry, the chunks manifest, and `StateVintageExtraction.cells` all treat the 186-cell space as flat. The legal-only `ScoringOutput` for a mixed chunk like `lobbying_definitions` (15 rows mixed) returns a partial chunk-extraction; the orchestrator (out of scope, see Finding 2) is presumed to merge this with practical-axis output later. Until the practical-axis sibling ships, `StateVintageExtraction.cells` will be missing the practical halves of 5 dual-axis rows + all 50 practical-only cells. This is correct behavior — Prong 2 fills those — but the legal-axis-only validator should not accept a `StateVintageExtraction` as "complete" prematurely. Worth a sentinel/typed-state distinction (`partial=True` flag, or separate `LegalAxisExtraction` / `PracticalAxisExtraction` types that merge into `StateVintageExtraction`) so Phase C consumers don't silently project from half-filled SMRs.

## Q1. Phase C ergonomics of StateVintageExtraction

The `cells: dict[(row_id, axis), CompendiumCell]` access pattern is a natural fit for projection code, based on the projection mappings at `docs/historical/compendium-source-extracts/results/projections/`. The CPI 2015 doc's per-item entries name rows like `def_target_executive_agency` (legal), `lobbyist_registration_required` (practical for #198), and consistently read `cell.value` against typed predicates (`threshold == 0`, `5-tier int in {0,25,50,75,100}`). Projection functions will key by `(row_id, axis)`, look up the cell, branch on the cell subclass, and read `value` (or struct fields for the specialized types). This matches the current shape exactly.

One frictio point worth naming: many projection mappings reason about combinations of cells (CPI #196 reads 5 different `def_target_*` rows; HG 2007 reads ~38 rows). Phase C will want `cells.get((row_id, "legal"))` access with sensible behavior when a cell is missing (None, raise, sentinel). Today the dict is plain `dict[tuple, CompendiumCell]`; recommend either a helper method on `StateVintageExtraction` (`smr.get_cell(row_id, axis)`) or a wrapping accessor type, so Phase C doesn't reimplement defensive lookups in 8 different projection modules. Not a blocker, but the first projection (CPI 2015 C11) will surface this immediately and the pattern that gets set there will propagate.

The `cell_id` post-validator (`cell.cell_id == key`) is sound; Phase C reading from the dict can trust the key. The frozen-Pydantic discipline is sound; Phase C cannot accidentally mutate cells mid-projection.

## Q2. Ralph-loop glue location

See Finding 2 above. No part of the four-component architecture is positioned to drive the Ralph loop. The retrieval and scoring brief-writers return `messages.create()` kwargs; the parsers consume single responses; there's no `n_runs`, no fixed-seed-or-prompt-batch primitive, no per-rubric loss aggregator. The "orchestrator" is uniformly named as out-of-scope but is the missing component.

Concrete gap for `scoring_v2`'s impl plan: the brief-writer signature `build_scoring_brief(state, vintage, chunks, retrieval_output, statute_bundle, url_pattern)` is per-call. For Ralph, the natural primitive is "run this brief N times with a fixed prompt-sha, return N `ScoringOutput`s." If `scoring_v2` exposes the brief-as-kwargs cleanly (which it does, mirroring retrieval), the Ralph harness can wrap it. The risk is not that scoring_v2 designs poorly — it's that the seam between "one brief per call" and "N briefs at fixed prompt-sha for noise floor" never gets named, and a future agent reinvents.

Suggested concrete adds (low-cost, do not re-open the brainstorm lock):

- `scoring_v2.brief_writer` documents the `prompt_sha` is the hash of `scorer_prompt_v2.md` content + any chunk preamble + the cell roster. (Already partially the case in `ExtractionRun.prompt_sha` — but ensure scoring_v2 surfaces it.)
- `ScoringOutput.run_id: str` echoed in the output, sourced from the caller, so N runs at the same prompt-sha can be tagged for noise-floor analysis.
- One paragraph in the scoring_v2 impl plan's "Things this plan does not ship" naming the Ralph-loop harness as the next-component-after.

## Q3. Practical-axis reuse budget

Reuse from `retrieval_v2` to a portal-extraction equivalent is **structurally low** and the brainstorm has correctly deferred it. Concretely:

- **Document blocks shape:** `retrieval_v2.brief_writer` builds `{"type": "document", "source": {"type": "text", "media_type": "text/plain", ...}}` blocks with `citations.enabled=True`. Citations API support for plain text yields `char_location` citations. Portal artifacts are HTML/PDF/XLSX/ZIP/CSV per v1's `bundle.py` history. PDF → `page_location` citations (different EvidenceSpan branch — already supported in the polymorphic model). HTML/XLSX/ZIP/CSV: not supported as document blocks at all; would need either (a) text-extraction preprocessing (loses structure) or (b) `custom_content` blocks with `content_block_location` citations.
- **Tool surface:** `record_cross_reference` is statute-text-shaped (`section_reference` is a statutory-section pattern like §101.70). Portal extraction needs different tools (`record_filing`, `record_portal_observation`, etc.) — the abstraction "tool that records something with Citations provenance" carries forward, but the schemas don't.
- **Brief-writer pattern:** the kwargs-returning pattern is reusable. The user-text formatting (`_format_cell_roster`) is reusable. The polymorphic parser (`_get` attr-or-dict-access helper) is fully reusable.
- **Cell-class dispatch by `(row_id, axis)`:** fully reusable — the same registry serves both axes.

Specific call-outs:

- The `EvidenceSpan` (retrieval_v2) shape covers all three Citations document types. Portal-side reuse just needs to populate the right branch fields. (Modulo Finding 1 — the EvidenceSpan duplication.)
- v1's `build_subagent_brief` (portal) vs `build_statute_subagent_brief` (statute) split (`bundle.py`) is precedent for not jamming both axes into one brief-writer. Q6's defer is the right call.
- `lobbying_data_open_data_quality` (GradedIntCell, 0/25/50/75/100) is a portal observation; FOCAL 2024 mapping shows the practical axis routinely uses 5-tier scoring. The cell-class layer handles this; the question is purely how the brief-writer produces the value.

Budget: maybe 30–40% of `retrieval_v2`'s line-count carries forward as pattern (brief-writer skeleton, parser shape, models template). The substantive content (prompt, tools, document handling) is portal-specific.

## Q4. Scale-failure diagnostics

**Will not fail silently in T0/T1 but may fail noisily-but-uninformatively at T2+.** The diagnostic surface today:

- `retrieval_v2.parser` raises on unknown citation types (`ValueError(f"Unknown citation type: {cite_type!r}")`) — good.
- Unknown tool names are silently skipped with citation-buffer reset. The comment says this prevents stale citations bleeding, which is sound, but means a model hallucination of a tool name produces no error trace, just a missing tool call. At T2+ with longer chains, this could mask real bugs (the model emits `record_cross_ref` instead of `record_cross_reference`).
- `RetrievalOutput.cross_references` is just a tuple — there's no validation that "this chunk's brief expected references and got zero" is informative. T2 single-OH-chunk validation could pass with zero references on a chunk that actually has them, and the failure would show up downstream as missing cells, not as "retrieval returned empty."
- The Citations-API `cache_control` interaction with citations was flagged as unverified in the retrieval brainstorm. T1 cleared on tiny statute. T2 on real-OH-chunk-sized inputs has not run.
- Tool-use composition under longer chains (>5 tool calls per response) is documented behavior but empirically unmeasured (RESEARCH_ARC.md "Open empirical questions"). The parser's pairing rule assumes "citation precedes tool call" — at long chains this could fail in ways the unit tests don't cover.

Recommend the scoring_v2 impl plan inherit retrieval's Phase-7 "pause-and-surface" directive (which it does — see Q6 below), AND add a minimum-emit-count diagnostic: "if scoring a 10-row chunk returns 0 `record_cell` calls, log/raise — don't silently produce an empty `ScoringOutput`."

`UnresolvableReference` / `UnscoreableCell` are the right shape for explicit failures; the gap is implicit failures (zero output, no tool calls fired).

## Q5. Scoring_v2 brainstorm decisions to reopen

Reviewed the 10 locked Q's + 2 pushbacks against the corrected framing. **One should be reconsidered, one is borderline:**

- **Q8 `provenance: tuple[EvidenceSpan, ...]` — reopen for type clarification.** As Finding 1: the brainstorm lock named the shape but not which `EvidenceSpan` class. This needs to be a decision, not an assumption. Cheap to clarify; expensive to retrofit.
- **Q3 "all statutes + retrieval annotations as user text" — borderline.** Putting retrieval annotations in user-text body means they're part of the prompt content but not part of the prompt-sha (which is just `scorer_prompt_v2.md` per the plan-sketch). For Ralph-loop reproducibility, two runs with different retrieval outputs but same prompt-sha will produce different scoring outputs that look like "same prompt, different result" — which is exactly the noise the noise-floor measurement is trying to separate from real prompt-effect signal. Suggest the scoring_v2 impl plan name what counts as the run-identity: just prompt-sha, or `(prompt_sha, retrieval_output_sha)`? Not a re-litigation of Q3; just a Ralph-loop-aware clarification of `ExtractionRun.prompt_sha` semantics.

The other 8 locked Q's hold under the corrected framing:

- Q1 (parameterized chunks list, per-chunk default): unchanged.
- Q2 (single polymorphic `record_cell`): unchanged.
- Q4 (optional disk-loaded preambles, ship 0): unchanged.
- Q6 (defer practical-axis): correct — Finding 3 notes the typed-state seam but doesn't undermine the lock.
- Q7-sub (`UnscoreableCell` parallel to `UnresolvableReference`): unchanged.
- Q7-rules (v1 rule disposition): unchanged.
- Q9 (`ScoringOutput` mirrors `RetrievalOutput`): unchanged.
- Q10 (file location): unchanged.

The Pushback 1 (combine brief-writer + scorer-prompt) is unchanged. The Pushback 2 (direct SDK pattern) is reaffirmed by the corrected framing — Citations API is the load-bearing provenance mechanism for Phase C's `EvidenceSpan` reads.

No new framing reason was found to re-open the locks beyond what's named above.

## Q6. Pause-and-surface directive for scoring_v2

**The brief-writer impl plan handoff explicitly carries the directive forward.** Handoff line 72 names the "Things that may go wrong" section as a required part of the scoring_v2 impl plan. Line 210 instructs the impl-plan-writer to inherit retrieval's pause-and-surface posture for the integration test phase and references retrieval's "Plan deviations surfaced and resolved" pattern. Line 192 instructs the plan-writer to surface holes to user rather than unilaterally re-decide. The directive is present.

What is **not** yet in place because the scoring_v2 impl plan itself has not been written: the actual concrete bullet list of T1-failure modes for scoring (analogous to retrieval impl plan lines 1020–1028). The handoff names the inputs; the impl-plan-writer produces the bullets. The retrieval plan's bullets covered (a) citations don't attach to text blocks, (b) tool calls fire without preceding cited text, (c) citations attach after tool calls instead of before, (d) `record_cross_reference` not called at all, (e) schema validation errors on enum fields, (f) `cache_control` doesn't work with citations. Scoring's analogs would be: (a) cells emitted without preceding citations, (b) value-type mismatches (model passes `"true"` string for BinaryCell), (c) `record_unscoreable_cell` not called when it should be (model fabricates instead of escaping), (d) longer-tool-chain pairing-rule failures (per RESEARCH_ARC.md open question), (e) practical-axis cell tool calls leaking from mixed-chunk briefs.

Verdict: the directive flow is wired in via the handoff; the concrete realization is the next agent's deliverable. Worth re-emphasizing in the impl plan that the diagnostic surface for scoring_v2 is MORE important than retrieval's because (a) it produces the typed cells that feed Ralph's loss, and (b) it's the place where prompt iteration will actually happen.

## Out of scope / not checked

- Did not re-read v1 `scorer_prompt.md` — relied on brief-writer brainstorm's Q7-rules table.
- Did not audit existing tests for `provenance=` usages (handoff says the impl-plan-writer does this).
- Did not check the compendium-v2-promote branch's audit trail for the 5 combined-axis rows beyond what's in the brainstorm convo.
- Did not check `phase-c-projection-tdd` branch state — Finding 2's claim about Phase C consumer-side relies on the RESEARCH_LOG note that "Phase C consumer-side not yet ramped" + the brainstorm convo confirming low blast radius.
- Did not check the `oh-statute-retrieval` branch state.
- Did not deeply read all 8 projection mapping docs — read CPI 2015 C11 + verified the access pattern matches.
- Did not check whether iter-1's 93.3% agreement number generalizes to the v2 schema (acknowledged open in the brainstorm).
- Did not propose new lock decisions; only surfaced open questions for user input.
