# Rubric Unification Plan + Project-State Handoff

**Goal:** Produce a single, actionable, item-level unified rubric that reconciles PRI 2010 (disclosure-law + accessibility) with FOCAL 2024 — including explicit lineage back to each source item, documented non-overlap, and a mapping from rubric items to `StateMasterRecord` schema fields.

**Originating conversation:** [`docs/active/pri-calibration/convos/20260420_phase3_baseline_dispatch.md`](../convos/20260420_phase3_baseline_dispatch.md) — the 2026-04-20/21 session that ran Phase 3 baseline, confirmed H1 (bundle scope too narrow) via TX §311.005 walkthrough, decided the meta-dictionary architecture, and ended with the user (Dan) asking "what's up with FOCAL vs PRI — we use both to define the standard, but maybe we should do the effort to first think about what does/n't overlap."

**Context:** The project uses PRI 2010 (61-item disclosure-law rubric + 22-item accessibility rubric) and FOCAL 2024 (50 indicators across 8 categories) as the two reference rubrics for state lobbying disclosure. Earlier analysis (`docs/historical/research-prior-art/results/scoring-rubric-landscape.md`) proposed composing "PRI's 22 accessibility + FOCAL's 50 content indicators" but **never did the item-level mapping** — it stopped at the conceptual level. Before 3 fellows × ~17 states each begin legal review at scale, the unified rubric needs to be nailed down so everyone is scoring the same thing. This plan does that unification.

**Confidence:** Medium. The two rubrics overlap meaningfully and the prior analysis was right that they compose, but the **shape** of the composition — which items are redundant, which are complementary, which are incompatible, and what to do about FOCAL's explicit exclusion of enforcement — requires a careful pass. Expect to surface disagreements that need Dan's adjudication.

**Architecture:** This is a research-and-synthesis task, not a code task. Output is a set of doc artifacts (markdown + CSV), not new pydantic models or pipeline code. The unified rubric is ultimately consumed by the scoring subagents via `src/scoring/rubric_loader.py`, which already supports per-rubric CSVs — so integration is "add a new rubric CSV under `docs/active/pri-2026-rescore/results/`" with matching atomic-item structure. No code change unless the rubric shape surfaces a loader bug.

**Branch:** `pri-calibration` — the unified rubric is logically upstream of pri-calibration's re-score, but the pri-calibration pilot must finish first (see "Nearby active work" below) so the two workstreams don't collide on rubric identity mid-calibration. Work here and hand off the finished unified rubric for a future re-score, don't interleave.

**Tech Stack:** Markdown + CSV + judgment. No code required for the primary task.

---

## Project context — start here if you're fresh

You're picking up a research project whose current state is:

1. **Mission.** `lobby_analysis` is open-source infrastructure for real-time democracy measurement — make US state lobbying disclosure data programmatically usable. Corda Democracy Fellowship project led by Suhan Kacholia. Target: 5–8 priority states initially, expansion to 50 states over time. Dan is one of ~3 fellows contributing; he works on this repo across multiple branches.

2. **What's settled:**
   - **Data model v1.0 accepted (2026-04-21).** 18 pydantic models in `src/lobby_analysis/models/` — Person/Organization/Identifier/ContactDetail/BillReference/PriorOffice/OrganizationRelationship (reference entities); LobbyingFiling/LobbyistRegistration/LobbyingPosition/LobbyingExpenditure/LobbyingEngagement/Gift (filing entities); Provenance + StateMasterRecord/requirement models (meta). Popolo-compatible at the reference-entity layer. Archived spec: `docs/historical/lobbying-data-model/results/lobbying_data_model_spec.md`.
   - **`StateMasterRecord` is the reconciliation surface.** Distinguishes "state law doesn't require this field" from "filer failed to report a required field." The unified rubric's items should map cleanly to `StateMasterRecord` requirement-side fields — that's the contract.
   - **Portal snapshot corpus exists for 50 states.** 2026-04-13 capture on `pri-2026-rescore` branch (merged to main): 981 artifacts, ~350 MB, 40 clean / 8 partial WAF-SPA / 2 near-empty (AZ, VT). Lives in `data/portal_snapshots/<STATE>/<DATE>/` (gitignored; manifests committed). Will be the raw material for portal-extraction pipelines.
   - **Scoring pipeline infrastructure.** `src/scoring/` has `orchestrator.py` with prepare-run / finalize-run / analyze-consistency subcommands; per-state subagent dispatch; locked scorer prompt at `src/scoring/scorer_prompt.md`. Tested at 132 tests green on pri-calibration, 156 with main merged in.

3. **What's in progress (pri-calibration, 2026-04-17 → present):**
   - **Phase 3 baseline dispatched 2026-04-20/21.** 30 subagents × 5 states (CA/TX/WY/NY/WI) × 3 runs × 2 PRI rubrics. Result: **0% exact-match agreement vs PRI 2010 on disclosure-law totals** across all 5 states. Triggered the plan's "<40% agreement → debug before iterating" stopping condition.
   - **Root cause identified: H1 (bundle scope too narrow).** Post-dispatch, Dan walked TX Gov Code ch. 305 item-by-item for A_registration (ours 1 vs PRI 7); retrieved §311.005(2) Code Construction Act externally; confirmed its "Person includes government or governmental subdivision or agency" sweeps state agencies into §305.003's expenditure-path registration requirement. Our scorer had no way to know this from ch. 305 alone. Same pattern expected for the other 4 states.
   - **Architectural decision made.** Extend `LOBBYING_STATUTE_URLS` in `src/scoring/lobbying_statute_urls.py` to a hybrid shape: `{(state, year): {"lobbying_chapters": [...], "support_chapters": [(url, note), ...], "interpretive_notes": [...]}}`. The scorer reads primary + support chapters (retrieval-guide); static facts about PRI's coding protocol go in interpretive_notes (metadata).
   - **Pilot-first strategy locked.** Finish 5-state pilot with bundle expansion before fellows onboard. Avoids forking the meta-dictionary schema into 3 incompatible shapes.
   - **Accessibility descoped from calibration.** Portal-feature rubric fundamentally doesn't fit statute text — TX/WY showed 96–98% items in "unable-disagree" inter-run.

4. **The rubric question that motivated this handoff plan.** Dan asked: we're using FOCAL + PRI as the scoring basis, but we haven't done the item-level overlap analysis. What's redundant, what's complementary, what's incompatible? The earlier `scoring-rubric-landscape.md` proposed composing them but only at the conceptual level. Before scaling to 50 states, we need to unify. **That's what this plan is for.**

## Pre-flight reads (absolute paths — worktree-aware)

Everything below is relative to the pri-calibration worktree root: `/Users/dan/code/lobby_analysis/.worktrees/pri-calibration/`. Prepend that to every path.

**Mandatory (read in this order):**

1. `STATUS.md` — branch inventory + recent sessions (newest first in "Recent Sessions").
2. `CLAUDE.md` — repo-level agent instructions. Multi-committer repo; branch hygiene rules.
3. `README.md` — project framing.
4. `docs/active/pri-calibration/RESEARCH_LOG.md` — this branch's trajectory, newest-first.
5. `docs/active/pri-calibration/convos/20260420_phase3_baseline_dispatch.md` — the session that produced this handoff. Read especially the "Topics Explored," "Provisional Findings," and "Decisions Made" sections.
6. `docs/active/pri-calibration/results/20260420_calibration_baseline.md` — Phase 3 baseline writeup, updated with H1 confirmation.
7. `docs/historical/research-prior-art/results/scoring-rubric-landscape.md` — the four-rubric landscape (PRI 2010, FOCAL 2024, F Minus, GAO). Read for the conceptual framing. **This doc proposed the composition but did not do item-level mapping.** Your job starts where it stops.

**Rubric source files (primary inputs for this plan):**

8. `docs/active/pri-2026-rescore/results/pri_2010_disclosure_law_rubric.csv` — 61 items. Columns: `item_id`, `sub_component` (A/B/C/D/E1/E2), `item_text`, `data_type`, `pri_notes`. PRI 2010 §III.
9. `docs/active/pri-2026-rescore/results/pri_2010_accessibility_rubric.csv` — 22 items. Columns: `item_id`, `category`, `item_text`, `data_type`, `pri_notes`. PRI 2010 §IV. Q7 has 15 sub-items (a–o) for "sorting data" sub-criteria.
10. `docs/active/focal-extraction/results/focal_2024_indicators.csv` — 50 indicators across 8 categories. Columns: `indicator_id`, `category`, `category_definition`, `indicator_text`, `measurement_guidance`, `supports_state_application`, `source_framework`. Indicator IDs are `{cat}.{item}` format (e.g., `3.3`, `8.11`).
11. `docs/active/focal-extraction/results/focal_2024_methodology.md` — FOCAL's extraction-from-Lacy-Nichols methodology note.
12. `docs/active/focal-extraction/results/focal_2026_scoring_rubric.csv` — **unknown content — READ FIRST and determine whether this is a pre-existing draft unified rubric or just a 2026 update of FOCAL alone.** Adjust plan shape based on what's there.
13. `docs/active/focal-extraction/results/focal_2026_methodology.md` — companion methodology note for the 2026 version.

**PRI methodology (for interpretation calls):**

14. `papers/text/PRI_2010__state_lobbying_disclosure.txt` — PRI 2010 paper text. Lines 1120–1250 for scoring methodology detail; §III for disclosure-law coverage; §IV for accessibility coverage. Resolves "how did PRI intend item X to be scored."
15. `docs/active/pri-calibration/results/20260419_pri_rollup_rule_spec.md` — PRI's sub-aggregate rollup rule, line-cited. 9 methodology differences between our scoring setup and PRI's 2010 protocol documented. Relevant because the unified rubric needs to decide: do we keep PRI's rollup semantics, adopt FOCAL's flatter approach, or invent something new?

**Data model side (for the rubric-to-schema mapping):**

16. `docs/historical/lobbying-data-model/results/lobbying_data_model_spec.md` — the v1.0 spec. Read the StateMasterRecord section carefully; that's the schema surface rubric items map onto.
17. `src/lobby_analysis/models/state_master.py` — the `StateMasterRecord`, `RegistrationRequirement`, `ReportingPartyRequirement`, `FieldRequirement` pydantic models.
18. `src/lobby_analysis/models/filings.py` — `LobbyistRegistration`, `LobbyingFiling`, `LobbyingPosition`, `LobbyingExpenditure`, `LobbyingEngagement`, `Gift`. These are the observed-filing models that the rubric's "what should be disclosed" questions correspond to.

**PRI ground truth (for validation):**

19. `docs/active/pri-2026-rescore/results/pri_2010_disclosure_law_scores.csv` — 50 states × 5 sub-aggregates + total.
20. `docs/active/pri-2026-rescore/results/pri_2010_accessibility_scores.csv` — 50 states × 8 categories + total.

**User preferences (memory-backed, don't re-learn):**

- Root-cause bugs; don't fix symptoms.
- TDD for implementation work. This plan is analysis/synthesis — no TDD expected.
- Don't write throwaway scripts.
- No `---` separator in chained bash output.
- Auto-add top-500 mature single-purpose Python libs; ask about architecture-shapers.
- Subagent prompts forbid shelling out — Read tool only.
- Push back on bad ideas; don't be sycophantic; never say "You are absolutely right."

---

## The plan

Four phases. Each phase produces a discrete, reviewable artifact. Phase 1 is the substantive analysis; Phases 2–4 turn it into actionable outputs.

### Phase 1 — Item-level overlap mapping (~1 day, analysis)

**Output:** `docs/active/pri-calibration/results/20260421_pri_focal_overlap_map.md` — a line-by-line mapping of every PRI and every FOCAL item to one of six classifications (defined below), with short rationale per item.

**Classification scheme** (propose to Dan for approval before starting):

- **`DUPLICATE`** — same question, equivalent scoring semantics. Keep one source; document lineage.
- **`RELATED`** — overlapping domain but different granularity or scope. Merge or decide which to keep per item.
- **`PRI_ONLY`** — PRI item with no FOCAL analog. Candidate for the unified rubric if the content is useful.
- **`FOCAL_ONLY`** — FOCAL indicator with no PRI analog. Candidate for the unified rubric if the content is useful.
- **`INCOMPATIBLE`** — two items that look similar but score contradictory things (e.g., PRI B1/B2 reverse-scored for "government exemption exists" vs FOCAL's absence of a comparable construct). Requires a decision call.
- **`OUT_OF_SCOPE`** — item that belongs in a different axis (enforcement, compliance, portal accessibility) and should NOT be in the unified rubric even if both rubrics have it.

**Known landmarks (use these to sanity-check your classifications):**

| Zone | PRI items | FOCAL indicators | Expected classification |
|------|-----------|------------------|------------------------|
| Who must register | PRI A1–A11 (11 items) | FOCAL 1.1–1.4 (4 items) | `RELATED` — FOCAL's cat 1 is more compact but covers the same conceptual ground. Decision: keep PRI's granularity (more actionable for scoring) but map FOCAL's 1.1-types-of-lobbyists onto the PRI A1–A11 structure. |
| Government exemptions | PRI B1–B4 | *no direct FOCAL* | `PRI_ONLY`. |
| Public entity def | PRI C0, C1–C3 | *no direct FOCAL* | `PRI_ONLY`. |
| Materiality tests | PRI D0, D1_present/value, D2_present/value | FOCAL 1.2 "no (or low) threshold" | `RELATED` — FOCAL flags threshold existence; PRI records threshold value. Keep PRI's richer capture. |
| Principal/Lobbyist disclosure fields | PRI E1a–E1j, E2a–E2i (~24 items) | FOCAL 4.1–4.6 (descriptors), 7.1–7.11 (financials), 8.1–8.11 (contact log) | `RELATED` — same topic, different axis. FOCAL's 26 content items provide the vocabulary for *what's in a disclosure*; PRI's E section scopes *who must disclose what*. Worth keeping both with explicit cross-references. |
| Reporting frequency | PRI E1h_i–E1h_vi, E2h_i–E2h_vi | FOCAL 2.1–2.3 (timeliness) | `DUPLICATE` on the concept; `RELATED` on granularity. PRI captures discrete frequency options; FOCAL uses a "real-time vs quarterly" threshold. Decide which to keep. |
| Issue/bill disclosure | PRI E1g_i/ii, E2g_i/ii | FOCAL 8.9 (topics/issues discussed), 8.11 (legislative references) | `DUPLICATE`. |
| Contact log | PRI E1i, E2i (brief) | FOCAL 8.1–8.11 (detailed, 11 indicators) | `RELATED` — FOCAL is much richer. Keep FOCAL's granularity. |
| Revolving door | *no PRI analog* | FOCAL 5.1–5.2 | `FOCAL_ONLY`. |
| Relationships (between actors) | *partial via A10/A11* | FOCAL 6.1–6.4 | `FOCAL_ONLY` for most. |
| Portal/openness | PRI §IV Q1–Q8 (22 items) | FOCAL 3.1–3.9 (openness) | `RELATED` / `OUT_OF_SCOPE` — this is the portal-accessibility axis, which should NOT be in the unified *legal-review* rubric. Keep these separate (they're scored against portal snapshots, not statute text — confirmed by the 2026-04-20 pri-calibration baseline finding on accessibility). |

**Task list:**

1. Load all three CSVs. Validate they parse cleanly (pandas or csv module; no dependency on new deps — pydantic is already installed).
2. Read `focal_2026_scoring_rubric.csv` first and determine whether prior work has already produced a partial unified rubric. If yes, treat it as a starting draft to validate; if no, proceed from the raw sources.
3. For each PRI disclosure-law item (61), produce a row in the output table with columns: `source`, `source_id`, `source_text`, `classification`, `paired_with` (other source's item_id if DUPLICATE/RELATED/INCOMPATIBLE, else null), `rationale` (≤200 chars), `keep_in_unified` (bool).
4. For each PRI accessibility item (22), same as step 3.
5. For each FOCAL indicator (50), same as step 3. Cross-reference back to any PRI items that appeared in step 3's `paired_with` to check symmetry.
6. Sanity check: sum of DUPLICATE pairs should appear in both PRI's and FOCAL's classified list (symmetry). RELATED pairs likewise. PRI_ONLY and FOCAL_ONLY should be listed only once.
7. Aggregate: count by classification, broken down by rubric-of-origin. Report: "N PRI items are DUPLICATE, M are RELATED, P are PRI_ONLY..." etc.
8. Identify INCOMPATIBLE pairs explicitly — these are the ones requiring Dan's adjudication. Expect 2–5 such pairs. Document each with "PRI says X, FOCAL says Y, which do we adopt and why."
9. Write up the mapping as the markdown artifact. Save the long-form table as an accompanying CSV at `docs/active/pri-calibration/results/20260421_pri_focal_overlap_map.csv` for downstream consumption.
10. Gate: present classifications to Dan, get approval or revisions on the INCOMPATIBLE pairs, before Phase 2.

### Phase 2 — Unified rubric synthesis (~half day, once Phase 1 is approved)

**Output:** `docs/active/pri-calibration/results/20260421_unified_rubric.csv` — the canonical scoring rubric going forward. Same column shape as PRI 2010 rubrics to minimize `rubric_loader.py` changes.

**Task list:**

1. For each item with `keep_in_unified=true` in Phase 1's map, create a unified-rubric row with a new stable `item_id` (e.g., `U_A1`, `U_E1f_i`, `U_REV_1` for revolving-door items that have no PRI predecessor).
2. Retain `source` and `source_id` as provenance columns on every row.
3. Retain `sub_component` / `category` structure but unify the taxonomy. Propose: use PRI's A–E sub-components as the skeleton for legal-review items (since PRI's structure maps cleanly onto statute sections); use FOCAL's cat 5 (Revolving Door) and cat 6 (Relationships) as additional sub-components where PRI has no coverage.
4. Write an accompanying methodology note (`docs/active/pri-calibration/results/20260421_unified_rubric_methodology.md`) explaining: which items were merged and why; which FOCAL-only items made it in; why enforcement was excluded (follow FOCAL's protocol — enforcement belongs in a separate axis per GAO-25-107523 style analysis).
5. Gate: Dan review before Phase 3.

### Phase 3 — Rubric-to-schema mapping (~half day)

**Output:** `docs/active/pri-calibration/results/20260421_rubric_to_schema_map.md` — mapping from unified-rubric items to `StateMasterRecord` / filing-model fields.

**Task list:**

1. For each unified-rubric item, identify:
   - (a) Which `StateMasterRecord` requirement field represents "does this state's law require this?" — i.e., the answer to the rubric question IS the value of that requirement field.
   - (b) Which filing-model field represents "did a given filer actually report this?" — i.e., presence/absence of this field on a `LobbyingFiling` or related entity tells you whether compliance happened.
2. Flag rubric items that don't have a clean schema mapping — those require either a schema extension (future data-model v1.1) or a note that they're score-only (not mapped to extraction).
3. Expected outcome: most PRI A/E items map cleanly to `RegistrationRequirement` and `LobbyistRegistration` / `LobbyingFiling` fields. Most FOCAL contact-log items (8.1–8.11) map to `LobbyingEngagement`. FOCAL revolving-door (5.1–5.2) may require either a schema extension on `PriorOffice` or a score-only flag.

### Phase 4 — Handoff deliverable for fellows (~half day)

**Output:** `docs/active/pri-calibration/plans/20260421_fellow_legal_review_playbook.md` — a playbook fellows can follow when scoring their assigned ~17 states.

Contents:
1. Which rubric to use (the unified one).
2. How to build the state's statute bundle using the meta-dictionary (`lobbying_chapters` + `support_chapters` + `interpretive_notes`) — with CA and TX as worked examples once pri-calibration pilot finishes.
3. How to dispatch scoring subagents (existing `orchestrator calibrate-prepare-run` / etc.).
4. How to file rubric items that require human judgment (edge cases, interpretive drift).
5. What to do if a state's statute genuinely has no analog for an item (e.g., WY has no revolving-door statute — score as `not_required` in `StateMasterRecord`, not as `unable_to_evaluate`).

This deliverable is blocked on **pri-calibration pilot completion** (the CA/TX worked examples). Write what you can now; finish when pilot closes.

---

## Testing Plan

This is a research/synthesis task, not a code task. TDD does not apply. Instead:

- **Phase 1 is validated by item count**: every PRI item appears exactly once in the output; every FOCAL indicator appears exactly once; RELATED/DUPLICATE pairs appear in both rubrics' rows (symmetry check). A simple count assertion passes.
- **Phase 2 is validated by traceability**: every unified-rubric row has a `source` and `source_id` that resolves to a real item in the source CSVs.
- **Phase 3 is validated by schema coverage**: every `StateMasterRecord.*Requirement` field is either referenced by at least one rubric item, or flagged as "schema has this field but no rubric currently probes it" (future work).
- **Phase 4 is validated by worked example**: apply the playbook to CA step-by-step; check that a fresh agent could follow it unambiguously.

If the plan expands into code (e.g., adding a new rubric CSV to the loader, or extending `StateMasterRecord`), switch to TDD:

I will add a loader test that ensures the unified rubric CSV parses into the same pydantic `Rubric` structure as the existing PRI rubrics. I will add a test that the unified rubric has no duplicate `item_id`s. I will add a test that every `source_id` in the unified rubric resolves to a real item in one of the source CSVs.

NOTE: I will write *all* unit/integration tests before I add any implementation behavior.

---

## Edge cases

- **PRI's B1/B2 reverse-scoring.** These items are scored as "1 if exemption does NOT exist" per PRI footnotes 85/86. The unified rubric should either preserve reverse-scoring (risky — easy to get wrong) or restructure the question to score normally (e.g., "Are government agencies subject to lobbying-disclosure law?" scored 1 if yes). Call: restructure. Flag in methodology note.
- **PRI's ordinal Q8 (0–15) for accessibility "simultaneous sorting."** Non-binary in an otherwise-binary rubric. Accessibility is out of scope for the unified legal-review rubric anyway, so this only matters if we ever build a separate unified accessibility rubric.
- **FOCAL 1.2 threshold ambiguity.** "No (or low) financial or time threshold." "Low" is unspecified. PRI's D1_value / D2_value capture the actual threshold value as numeric. Decision: keep PRI's numeric capture; derive the binary "low threshold" answer from it via a state-specific threshold policy (TBD).
- **Westminster-centric FOCAL language.** Several FOCAL indicators reference "Ministers," "Ministerial diaries," etc. (FOCAL 1.3, 2.3, 3.2). `measurement_guidance` column in the FOCAL CSV notes US-state translations. Apply those translations verbatim in the unified rubric.
- **FOCAL 3.3 is compound** (5 sub-conditions). Decompose into 5 atomic items for consistency with PRI's atomic structure.
- **Enforcement exclusion.** FOCAL explicitly excludes enforcement "for feasibility." PRI also doesn't cover enforcement. The unified rubric should preserve this exclusion — enforcement is a separate axis per GAO-25-107523 methodology. Document the exclusion in the methodology note.
- **What about F Minus 2024?** Prior analysis (`scoring-rubric-landscape.md`) concluded: "treat as a hypothesis generator only" pending methodology verification. Out of scope for this plan. Don't import F Minus indicators into the unified rubric.

---

## Nearby active work — don't duplicate, don't collide

Three workstreams are live on this branch or the broader project. Coordinate but don't interleave:

1. **pri-calibration pilot finish** (Dan's next session, probably): expand `LOBBYING_STATUTE_URLS` for CA/TX/NY/WI/WY with `support_chapters` (TX ch. 311, CA Gov Code §18 + §§82000–82056, etc.); re-retrieve; re-score against PRI 2010 rubric; measure agreement uplift. **Uses the existing PRI rubric CSVs, not the unified rubric.** That's intentional — changing the rubric between today's baseline and the re-score would break apples-to-apples comparison. **This plan's unified rubric is downstream of the pilot; don't merge them.**

2. **Data model v1.0 is frozen.** `src/lobby_analysis/models/` is the contract. Any schema extensions this plan surfaces (e.g., for revolving-door items that don't have a clean `StateMasterRecord` home) become v1.1 work on a new branch with a migration plan — NOT silent edits here.

3. **Portal extraction pipelines are not yet built.** Pipelines will run PER FELLOW, one per state, emitting JSON conforming to `src/lobby_analysis/models/`. The unified rubric informs what those pipelines need to capture, but the pipelines themselves are future work (fellow rollout).

---

## Open questions (present to Dan before final unified rubric commit)

1. **FOCAL 2026 scoring rubric CSV** — what's in `focal_2026_scoring_rubric.csv`? Is it a pre-existing draft unified rubric that supersedes this plan, or a 2026 update of FOCAL alone? **Answer this before starting Phase 1.**
2. **Should reverse-scored PRI items (B1, B2) be restructured in the unified rubric?** Recommendation: yes. Requires confirmation.
3. **How to handle INCOMPATIBLE pairs** — when PRI and FOCAL disagree on what to measure. Present each such pair to Dan with the recommendation; expect 2–5 pairs.
4. **Reporting frequency granularity** — keep PRI's 6-item frequency breakdown or collapse to FOCAL's real-time-vs-threshold approach? Recommendation: keep PRI's breakdown (more actionable for scoring state statutes) but add a FOCAL-style aggregate as a derived score.
5. **Revolving-door data model mapping.** FOCAL 5.1 (lobbyist's prior public offices) → extends `PriorOffice`. FOCAL 5.2 (database of banned officials) has no current home. Options: add a model, flag as score-only, defer to v1.1.

---

## Testing Details

No code-behavior tests required for Phases 1–3 (research/synthesis). Phase 4 playbook is validated by worked example on CA once the pri-calibration pilot produces the expanded CA bundle.

If code is added (rubric loader extension for the unified rubric), tests are: (a) loader parses the unified CSV into the existing `Rubric` pydantic model shape; (b) no duplicate item_ids; (c) every `source_id` in unified rubric resolves to a real source-CSV item.

## Implementation Details

- Output artifacts live under `docs/active/pri-calibration/results/` following the `YYYYMMDD_<description>.{md,csv}` naming convention; link each from the RESEARCH_LOG.
- Do not create new `src/` modules. The unified rubric should plug into the existing `src/scoring/rubric_loader.py` with zero loader changes if the CSV schema matches PRI's existing shape.
- Use the pri-calibration worktree: `/Users/dan/code/lobby_analysis/.worktrees/pri-calibration/`.
- Commit after each phase (not just at the end). Commit messages follow the `pri-calibration: <what>` convention.
- Run `uv run --active pytest -q` after any code change to verify 156 tests still pass.

## What could change

- **If pri-calibration pilot fails to improve agreement** (bundle expansion doesn't move the needle), H2 (rubric-interpretation drift) becomes the leading hypothesis instead of H1. That would mean the unified rubric needs prompt-level disambiguation — specific coding-protocol notes on ambiguous items — and Phase 2's output shape may need to include an `interpretive_note_per_item` column.
- **If a fellow surfaces a genuinely new rubric source** (state-specific reporting requirements, a newer paper), the unified rubric may need revision. Design for extension: keep `source` column populated so new items can be added without disturbing existing IDs.
- **FOCAL's 2026 version may change the 2024 indicators materially.** If the `focal_2026_scoring_rubric.csv` reflects substantive differences from 2024, the unified rubric should use 2026 FOCAL as the base, not 2024. Determine which is current before starting Phase 1.

## Questions

- See "Open questions" above — 5 items requiring Dan's input at specific phase gates.
- One meta-question for the next agent: is rubric unification properly scoped *within pri-calibration branch*, or does it deserve its own branch (e.g., `rubric-unification`)? Recommendation: keep on pri-calibration since it's directly informing the calibration work and the timeline is tight. But if the work expands in scope (e.g., requires data-model extension), cut a branch.

---
