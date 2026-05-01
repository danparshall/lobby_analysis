# 2026-05-01 — Harness Brainstorm Kickoff

**Branch:** `statute-extraction` (worktree: `.worktrees/statute-extraction/`)
**Status:** in progress (live convo summary)
**Predecessor branch:** `filing-schema-extraction` (merged 2026-05-01 via PR #5, archived to `docs/historical/`; v2 audit + v1.2 schema bump landed there)

## Framing (corrected mid-session 2026-05-01)

The compendium is the universe; the SMR is keyed to the compendium; rubrics are projections of the SMR, not data sources for it. **All nine past rubric scorings (PRI 2010 disclosure, PRI 2010 accessibility, FOCAL 2024, Sunlight 2015, Newmark 2005/2017, Opheim 1991, CPI Hired Guns 2007, OpenSecrets 2022) are validation signals** — none privileged. The harness's job is to populate the 108-row statute-side compendium for OH from statute text; multi-rubric agreement is a sanity check.

Two artifacts exist as diff inputs (not gates): the OH 2010 + OH 2025 PRI-projection SMR shipped on `statute-retrieval` (PR-merged 2026-04-30, archived). They illustrate the SMR shape that is correct, but their PRI-only data source is what the new harness replaces.

## Goal of this session

Resolve the seven open design questions from the kickoff plan (Q1–Q7 in the handoff) and produce a concrete OH-first MVP target before any harness code is written.

## Pre-work done before brainstorm

- Pre-flight reads: STATUS.md, README.md, docs/COMPENDIUM_AUDIT.md, kickoff plan, OH 2025/2010 diff.
- Confirmed the 141-row compendium = 108 statute-side + 33 accessibility-side from disk.
- Identified the carry-forward infrastructure: `src/scoring/{justia_client, bundle, statute_retrieval, calibration, consistency, orchestrator, smr_projection, scorer_prompt.md}` + `src/lobby_analysis/models/` (v1.2 schema with `definitions` domain).

## Skeleton refactor (commit 5537c92)

Moved `data/compendium/` → `compendium/` at repo root. The compendium is the locked contract for the harness, not gitignored runtime data. Path constants updated in `compendium_loader.py`, `build_compendium.py`, `test_compendium_loader.py`; `.gitignore` re-include removed; audit-doc references updated. 24/24 compendium tests pass.

## Open design questions (to brainstorm)

### Q1 — Subagent architecture / extraction prompt shape
Per-row, per-section, or per-bundle? The harness extracts against compendium rows that are filing-shape-distinct (not yes/no), so prior per-rubric-item subagent shapes don't transfer cleanly.

### Q2 — Qualitative materiality
§101.70(F)-type "main purposes" tests are real legal gates that are easy to silently drop. How does the harness flag and capture qualitative gates? (boolean? structured boolean+text? `requires_human_review`?)

### Q3 — Conjunctive vs disjunctive drift
Multi-field requirements ("address AND phone") need to be extracted atomically; prior runs collapsed these disjunctively under prompt drift. Atomic per-row extraction may help; verify in pilot.

### Q4 — Multi-regime parallel chapters
Some states have parallel disclosure regimes for different branches (legislative + executive). Data model already supports `ReportingPartyRequirement`; the prompt needs to enumerate them.

### Q5 — MVP gate
What's the green-light bar for the OH MVP? Anchored against the compendium directly, not against any prior rubric-projection artifact. Coverage-only? Coverage + qualitative-materiality capture? Coverage + multi-run agreement threshold? Coverage + audit-trail/citation chain?

### Q6 — Multi-run agreement
Prior runs hit 21.3% inter-run disagreement at temp-0 with files-read enforcement. What's an acceptable level for the new harness, and how do we collapse runs (majority vote, flag-for-review, scorer-of-scorers)?

### Q7 — Scaling shape
OH first → which states next, in what order, on what schedule. The 5–8 priority-state target lives in README.md scope but specific states aren't picked.

## Brainstorm transcript

### Two-script structure (resolved)

The branch produces two scripts, not one:

1. **Harness.** Parses OH 2025 statute from Justia → answers the compendium questions → emits an SMR. Runs on the current vintage; this is the production artifact.
2. **Validation tool.** Runs the same harness on past Justia vintages where human-graded rubric scores exist, projects the resulting SMR through each rubric's dedup map (`compendium/framework_dedup_map.csv`) to per-rubric scores, and compares to the published human-coded scores. Output: a multi-rubric agreement table per (state, vintage). This measures how well the harness is working — it is not a gate.

Iteration is the unit of work: harness runs → validation table → identify weak rows → improve prompt/scaffolding → re-run. Multiple rounds expected before the harness is trusted enough to scale beyond OH.

### Q1 — Subagent architecture / chunking (resolved)

**Decision:** chunk the 108 statute-side compendium rows by `domain` into **4 prompts**:

| chunk | rows | row-brief tokens |
|---|---|---|
| reporting | 47 | 1,938 |
| registration | 31 | 1,401 |
| contact_log | 14 | 487 |
| other (definitions + financial + revolving_door + relationship) | 16 | 967 |
| **total** | **108** | **4,793** |

**Rationale:** measured single-prompt input is ~43–46K tokens (~5% of Opus 4.7's 1M window). Size is not the bottleneck; attention dilution across 108 simultaneous extraction goals is — that's what produced the prior MVP's conjunctive→disjunctive collapse, qualitative-materiality drops, and 21% inter-run disagreement. Smaller chunks help quality, not capacity. By-domain chunking is semantically meaningful, aligns with how statute chapters are organized, and lets us iterate one domain at a time.

**Caching architecture:** the OH 2025 statute bundle (~36K tokens, identical across chunks) is the cached system-prompt prefix. The per-chunk row briefs + extraction instructions are the variable suffix. Anthropic prompt caching's 5-minute TTL covers running all 4 chunks back-to-back.

**Expected refinement (deferred until pilot data):** `reporting` at 47 rows may need to be sub-split (likely along `RPT_LOBBYIST_*` vs `RPT_PRINCIPAL_*` vs `RPT_ITEMIZED_*` vs `FREQ_*` lines). `registration` at 31 should hold. `contact_log` and `other` are small enough that splits aren't expected to matter.

### Bundle inlining (resolved)

**Decision:** the OH 2025 statute bundle (~36K tokens, 30 sections) is inlined directly in the cached system-prompt prefix — not referenced via Read tool calls.

**Rationale:** the prior architecture's failure modes (4–43 tool-call variance, exemption-layer under-reading, conjunctive collapse) all trace back to subagents choosing what to read. Inlining makes reading structural — the text is unconditionally in attention; there's nothing to skip to. This obsoletes the "did you read?" scaffolding (Rule 7's `files_read.json` sidecar, Rule 5's imperative to read everything). Cost: ~36K cached tokens + ~5K per-chunk suffix; cache hit on chunks 2–4 within the 5-min TTL.

**What we keep from the old scaffolding:** citation discipline. Every populated compendium row must carry `legal_citation` + a short verbatim quote. That's not "did you read?" — that's "show which clause you used."

**Code impact:** delete the `files_read.json` writing logic in `bundle.py:build_statute_subagent_brief`; the v2 brief-builder doesn't need it.

### Existing harness review (informational)

Before designing more, reviewed `src/scoring/`:

**Carry-forward unchanged:** `justia_client.py`, `statute_retrieval.py`, `lobbying_statute_urls.py`, `cmd_retrieve_statutes`, `cmd_audit_statutes`, `cmd_expand_bundle`, `cmd_ingest_crossrefs`, `statute_loader.py`, `bundle.py`'s artifact-index logic, `provenance.py`, `output_writer.py` (pattern), `consistency.py`, `compendium_loader.py`, `smr_projection.py` (the compendium↔rubric direction inverts cleanly for the validation tool).

**Carry-forward with v2 rewrite:**
- `scorer_prompt.md` v1 → v2 (rubric-shape → compendium-shape; clean slate cherry-picking lessons listed below).
- `bundle.py:build_statute_subagent_brief()` — currently takes a `Rubric`, emits rubric-items JSON; v2 takes a domain chunk + filtered `CompendiumItem`s, emits compendium-row briefs, inlines the bundle text.
- `cmd_calibrate_prepare_run` / `cmd_calibrate_finalize_run` → fork into `cmd_extract_prepare_run` / `cmd_extract_finalize_run` (same scaffolding; different brief + output schema).
- `cmd_build_smr` — currently consumes per-rubric-item score CSV; v2 consumes the harness's 4-chunk compendium-row outputs and assembles a single SMR.

**Genuinely new:**
- `FieldRequirement.condition_text: str | None` — v1.3 schema bump.
- v2 `scorer_prompt.md`.
- The validation tool — new orchestrator subcommand `cmd_validate_smr` that takes a populated SMR + `framework_dedup_map.csv`, projects compendium→rubric via `target_expression` evaluation, compares to published human-graded scores for the (state, vintage, rubric), emits agreement tables.

### v2 scorer-prompt lessons preserved (resolved)

Concrete lessons from `scorer_prompt.md` v1 that carry into v2:
- **Citation mandatory.** Every populated row: `legal_citation` + ≤30-word verbatim quote.
- **Layered-reading awareness.** Statutes are general rule → exemption → carve-out → re-inclusion. Before committing to `not_required`, check for separate triggers in adjacent sections that catch the entity by activity rather than category.
- **Honest `not_addressed`.** Statute silence → `not_addressed` + citation of the sections searched. No guesses.
- **Confidence self-assessment.** `confidence: high|medium|low` per row.
- **Atomic per-row.** Each compendium row is answered on its own; multi-field requirements have separate rows by curation. Do not merge.

Lessons that change shape:
- Output schema: rubric-item-shape → `FieldRequirement`-shape with `condition_text` (Q2).
- Status enumeration: `0/1 + unable_to_evaluate` → `required / not_required / not_addressed / required_conditional`.
- Rule 6 (PRI-specific A5–A11 / C0 reading guidance) → per-domain extraction notes (registration / reporting / contact_log / other).
- Files-read sidecar: gone (bundle inlined).

### Q5 — MVP shape & iteration loop (resolved)

The MVP isn't a fixed gate; it's an iteration loop where the validation tool measures harness quality between rounds.

**Q5a — First-iteration scope (resolved):** start with the **`definitions` chunk only** (7 rows). Smallest non-trivial chunk; exercises the trickiest output shape (`required_conditional` + `condition_text`); §101.70(F)'s "main purposes" test is the known canary failure case. If the harness gets `THRESHOLD_LOBBYING_MATERIALITY_GATE` right on §101.70(F), we have evidence the architecture works on the hard case before fanning out to 108 rows.

**Q5b — Per-iteration artifacts (resolved as option (3), pending template iteration):**
1. Populated SMR JSON (or chunk-level partial SMR for early iterations).
2. Raw subagent outputs per chunk + per run.
3. Validation agreement table (multi-rubric projection through `framework_dedup_map.csv` vs published human-graded scores, where data exists).
4. Per-iteration analysis doc — I write it; lists weak rows, likely causes, proposed prompt/scaffolding change for the next iteration.

**Iterate the analysis-doc template with the user before producing the first real one** — the user wants to see the structure before I generate it for OH iteration 1.

**Q5c — Convergence signal (resolved):** **user OK is required** to call OH MVP done. Multi-rubric agreement (the validation table) is one factor in that judgment, not a hard threshold. After OH ships, future-state gates may quantify based on OH's observed distribution.

### Provenance / reproducibility (resolved — first-class requirement)

**Decision:** every output must be paired with the prompt that produced it, plus timestamp, plus a per-subfolder meta file. Iteration without provenance is "a nightmare to figure out if we're improving."

**Per-run output layout** (extends existing `data/scores/<STATE>/...` convention):

```
data/extractions/<STATE>/<VINTAGE>/<CHUNK>/<RUN_ID>/
  brief.md                        # the literal prompt (system + user message) sent to the subagent
  raw_output.json                 # the subagent's response
  field_requirements.json         # validated, schema-conformant rows (post output_writer)
  meta.json                       # the run-metadata sidecar (see below)
```

**`meta.json` schema (extends existing `StatuteRunMetadata`):**
- `run_id` — short hash, cross-references with run dir name.
- `run_timestamp_utc` — ISO-8601.
- `model_version` — e.g., `claude-opus-4-7`.
- `state`, `vintage_year`, `chunk` (e.g., `"definitions"`).
- `prompt_sha` — sha256 of `brief.md`.
- `bundle_manifest_sha` — sha256 of the inlined statute bundle (so we can detect bundle drift).
- `compendium_csv_sha` — sha256 of `compendium/disclosure_items.csv` at run time (compendium is locked but defensive).
- `iteration_label` — free-text human label (e.g., `"iter-1"`, `"iter-2-after-D0-fix"`).
- `prior_run_id` — the run this iterates from, if any.
- `changes_from_prior` — free-text 1–3 sentence summary of what changed in this iteration vs prior.

**Per-iteration parent dir:** `data/extractions/<STATE>/<VINTAGE>/_iterations/<ITERATION_LABEL>/` carries the analysis doc + a top-level meta.json that links to all chunk run_ids in that iteration.

**Code impact:**
- Extend `provenance.py` with the new fields (`chunk`, `iteration_label`, `prior_run_id`, `changes_from_prior`, `bundle_manifest_sha`, `compendium_csv_sha`).
- The harness CLI must take `--iteration-label` and `--prior-run-id` as args, write the meta sidecar on each run.
- The existing `MODEL_VERSION`, `prompt_sha`, `new_run_id`, `utc_now` helpers carry forward.

### Q3 — Conjunctive vs disjunctive (resolved structurally)

**Answered by prior decisions, not a new design call:**
- Compendium curation already split conjunctive multi-field requirements into atomic rows (e.g., `E1b` principal-address and `E1d` principal-phone are separate compendium rows, not a single "address+phone" row).
- Bundle inlining + per-row briefs mean the model answers one row at a time. The v2 prompt's "atomic per-row" rule names this explicitly.

**Verify in pilot** — should be a non-issue but observe the OH output for any residual collapse on multi-clause statutory language.

### Q4 — Multi-regime parallel chapters (provisionally resolved; final pending external survey)

**Provisional decision:** flat representation for OH MVP (option (a)). Each compendium row populates once; per-regime variation is captured in `notes`. Matches the existing PRI-projection SMR shape and minimizes schema change.

**Reopened mid-session:** the user asked how many states have parallel-regime structures. Rough estimate: of the 5–8 priority states the README scopes to, ~25–40% (likely 2–3 of 8: OH confirmed, IL likely, MA possibly) have meaningful multi-regime structure. That's at the boundary of "more than a handful." If empirical survey confirms ≥3 of 8 priority states have parallel regimes, lock in regime-aware representation (option (b)) from day one as part of the v1.3 schema bump rather than deferring to v1.4.

**External agent dispatched (web-UX, special research skill, 2026-05-01)** to survey regime structure across priority states. Output expected as a per-state structured table. **Q4 final decision blocks on that survey returning** — the harness plan will cover both branches:
- if survey shows ≤2 of 8 multi-regime → ship flat for OH MVP, target regime-aware in v1.4 as data accumulates.
- if survey shows ≥3 of 8 multi-regime → ship regime-aware in v1.3 alongside `condition_text`. The schema cost is one additional field; the rework cost of building flat then refactoring is much higher.

**Either way, OH iteration 1 (definitions chunk) can proceed** — the `definitions` rows do not vary by regime in OH (definitions cross-apply within Ch. 101's two regimes via shared §101.70 vocabulary; Ch. 121 has parallel definitions in §121.60 that we'd extract whether the schema is flat or regime-aware). Iter 1 is unblocked by the regime decision.

### Q6 — Multi-run agreement (resolved provisionally)

**Decision:** start with 3 temp-0 runs per chunk. Measure observed inter-run disagreement; pick a threshold from the actual distribution rather than guessing.

**Collapse strategy:** TBD after first measurement. The user has used a **3-model consensus oracle** in other projects (third-party adjudicator across model outputs); flagged as a candidate if simple majority-vote on 3 same-model runs proves insufficient. Decide after seeing OH variance.

**Comparator:** prior architecture under PRI-projection at temp-0 with files-read enforcement hit 21.3% inter-run disagreement on OH 2025. Inlining the bundle should drop that materially (eliminates the Read-tool dispatch variance that was the dominant noise source) — but the new architecture has its own variance shape (e.g., model commitment to `not_addressed` vs `not_required` on edge cases). Measure first.

### Q7 — Scaling (deferred)

Defer state-selection and ordering until OH iteration converges. Re-open as a separate brainstorm at that point.

### Q2 — Qualitative materiality (resolved)

**Decision:** option (ii). When a qualitative gate exists in statute (e.g., OH §101.70(F) "as one of the individual's main purposes"), the relevant compendium row (e.g., `THRESHOLD_LOBBYING_MATERIALITY_GATE`) populates as:
- `status="required_conditional"`
- `legal_citation` = section reference
- new field `condition_text: str | None` on `FieldRequirement` carrying the verbatim qualifying clause
- `evidence_source` filled per existing schema

**Rationale:** the structured `condition_text` field makes the gate queryable downstream (the disclosure-data pipeline can enumerate states with primary-purpose-style tests and handle them at portal level). Boolean-only would force the condition into free-text `notes`, defeating the SMR-as-contract role.

**Schema implication:** additive v1.3 schema bump — `FieldRequirement.condition_text: str | None` (default None). No breaking changes; existing populated SMRs without conditions are valid as-is. Plan for v1.3 to be its own small commit before harness implementation.

**Deferred:** LLM-flagged-for-human-review (option iii) is premature; observe the harness's actual failure modes first, then add review-flagging if needed.
