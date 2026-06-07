# Plan — Audit of all prompts in `compendium/source_quotes.yaml`

> ## ⚠️ HANDOFF UPDATE (2026-06-06, post-plan-draft) — READ FIRST
>
> Dan has ruled: **combined-axis rows are verboten henceforth.** This research line is **DE JURE ONLY** — reading statutes can tell us what the law says, not what actually happens. The *de facto* question requires entirely different data sources (empirical observation, court records, FOIA) and is a separate research line.
>
> **Implications the auditing agent must apply by editing this plan BEFORE executing the audit:**
>
> 1. **Reduce audit scope to `axis == "legal"` cells only.** Practical-axis prompts are permanently out of scope for this research line (not "deferred until Prong 2" — out entirely). Strike the "Phase 2 — chunk-by-chunk audit" guidance to iterate practical-axis prompts; replace with explicit legal-axis filter at every level (per-row, per-chunk, headline counts).
>
> 2. **Drop audit dimension #6 (axis disambiguation).** With combined-axis rows abolished, every (row_id, axis) pair has exactly one prompt and one cell type — no shared-prompt ambiguity to audit. Renumber the remaining 7 dimensions.
>
> 3. **Drop the SCHEMA-BLOCKED escalation path "needs per-axis prompts."** That entire failure mode disappears with the policy change. The YAML schema does NOT need `prompt_legal` / `prompt_practical` keys.
>
> 4. **Add a new sibling plan (or escalation note in §SCHEMA-BLOCKED summary)** for the **Pattern-C split of the 3 remaining combined-axis rows**, following the v2.1 precedent. The 3 rows currently `axis = "legal+practical"`:
>    - `lobbyist_registration_required` (BinaryCell legal + GradedIntCell practical)
>    - `lobbyist_registration_deadline_days_after_first_lobbying` (IntCell legal + GradedIntCell practical)
>    - `lobbyist_spending_report_filing_cadence` (EnumCell legal + GradedIntCell practical)
>
>    Each becomes two rows with new row_ids — likely `<base>_in_law` (legal) + `<base>_in_practice` (practical), per the v2.1 Pattern-C naming convention already used for `lobbying_violation_penalties_defined_in_law` / `_imposed_in_practice` and `lobbying_disclosure_audit_required_in_law` / `_in_practice`. The practical-axis halves still get created (compendium completeness; another research line will dispatch them), but this audit does not cover their prompts.
>
> 5. **The companion Phase 2 plan** ([`./20260606_phase_2_schema_aware_prompt_hygiene.md`](./20260606_phase_2_schema_aware_prompt_hygiene.md)) needs a one-paragraph patch in its §Risks section to reflect the policy: the "4 practical-axis cells deferred from this plan" are now permanently out of scope, not "deferred until Prong 2." Make that edit alongside the audit-plan revision.
>
> 6. **Re-estimate time and scope.** With practical-axis cells removed, the audit covers ~128 legal-only rows + the legal halves of the 3 (soon-to-be-split) combined-axis rows ≈ 131 prompts, not ~183.
>
> 7. The term "combined-axis" itself becomes historical vocabulary post-Pattern-C-finish — note in the findings doc that the term is no longer current usage.
>
> After applying these edits to this plan, the auditing agent proceeds with Phase 1 source familiarization as updated.
>
> **Sequencing prerequisite:** Phase 2A schema work (in [`./20260606_phase_2_schema_aware_prompt_hygiene.md`](./20260606_phase_2_schema_aware_prompt_hygiene.md) §Phase A — TimeThresholdCell `other_specification` + row #5 FloatCell→TimeThresholdCell promotion) should land BEFORE this audit runs, so the audit can review row #5's prompt normally instead of escalating it as SCHEMA-BLOCKED. If Phase 2A has not yet landed when this audit starts, escalate row #5 with a pointer to Phase 2A rather than auditing against the old FloatCell schema.

---

**Originating analysis:**
- [`./20260606_phase_2_schema_aware_prompt_hygiene.md`](./20260606_phase_2_schema_aware_prompt_hygiene.md) — the Phase 2 plan that established the per-prompt revision pattern this audit generalizes to all rows. The 7 prompts revised there are the worked example; this audit applies the same discipline to the remaining ~175.
- Originating convo: [`../convos/20260606_phase_1_exec_and_de_jure_pivot.md`](../convos/20260606_phase_1_exec_and_de_jure_pivot.md). The convo established three principles the audit will apply:
  1. **Extraction-vs-projection separation.** The YAML prompt asks the actual question; the model returns the raw observable. Cross-rubric synthesis (OR-projection, AND-compounds, tier collapses) lives in projection helpers, not in the prompt.
  2. **Lean question.** The model doesn't need historical rubric framing. Strip "A 100 score is earned if..." preambles where the underlying question is clear without them.
  3. **Schema-aware return-shape spec.** Every prompt explicitly states the response format, matched to the cell type the dispatcher will instantiate.
- Failure-mode trail behind those principles: [`../results/20260606_failure_mode_trends_and_paths_forward.md`](../results/20260606_failure_mode_trends_and_paths_forward.md) (Trend 6 — cell-type schism) and [`../results/20260606_cpi_2015_c11_chunk_inventory.md`](../results/20260606_cpi_2015_c11_chunk_inventory.md) (the 11 underspecified prompts that surfaced the audit need).

**Cross-branch context:**
- [`../../leave-behind-prep/convos/20260606_take_stock_and_day1_hygiene.md`](../../leave-behind-prep/convos/20260606_take_stock_and_day1_hygiene.md) — Fellowship-end framing.

**Branch:** `cross-state-cpi-2015-validation`
**Worktree:** `/Users/dan/code/lobby_analysis/.worktrees/cross-state-cpi-2015-validation`
**Estimated total cost:** $0 (read-only analysis; no model dispatches, no YAML edits)
**Estimated total time:** 2–4 hours of audit agent execution + Dan review of findings

---

## Why this plan exists (the question it's answering)

In the Phase 2 design session we discovered that the existing prompts in `compendium/source_quotes.yaml` carry three structural problems:

- **Bloat:** most existing prompts lead with a rubric-quote preamble (e.g., "A 100 score is earned if..."), then add a question, then add a format spec. The preamble is for human auditors, not the model. The model just needs the actual friggin' question.
- **Extraction-vs-projection conflation:** some prompts bake cross-rubric synthesis into the model-facing question (e.g., HG Q13's OR-projection across registration-form-comp ∨ spending-report-comp), which forces the model to do work that belongs in projection helpers.
- **Cell-type schism (Trend 6):** some prompts assume one return shape (e.g., percent) while the cell type can't carry that shape (e.g., FloatCell with no unit slot), forcing the model to do math-on-the-fly or lose information.

Phase 2 fixed 7 prompts. The remaining ~175 likely have similar issues. We want a systematic audit before the next round of dispatches, so the model gets laser-focused questions everywhere — not just on the cells we already inspected.

**Separation of concerns this plan enforces:**
- This audit agent **identifies** problems and **drafts** revisions.
- A future set of execution agents (probably one per chunk) **applies** the revisions.
- The handoff is a single findings doc that catalogs every prompt + verdict + suggested revision, structured chunk-by-chunk so execution agents can pick up a coherent slice without reading the whole thing.

**What this agent does NOT do:**
- Does NOT edit `compendium/source_quotes.yaml`.
- Does NOT edit any source code.
- Does NOT change cell-type schemas (escalates schema-blocked cases to a separate plan).
- Does NOT dispatch any model calls.

---

## The audit dimensions (8 checks per prompt)

For each (row_id, axis) with a non-null prompt, check:

| # | Dimension | Pass condition |
|---|---|---|
| 1 | **Extraction-vs-projection** | Prompt asks the raw observable. Does NOT bake OR/AND/tier-collapse logic across other rows. |
| 2 | **Lean question** | Prompt's first substantive sentence is the actual question. Rubric-quote preamble is either absent or strictly necessary for disambiguation (the auditor must justify any retained preamble). |
| 3 | **Return-shape spec** | Prompt explicitly names the expected return format, matching the cell type's `value` (or `magnitude` + `unit` for composite cells). |
| 4 | **Cell-type alignment** | The return-shape spec's named format is achievable in the cell type (e.g., a prompt asking for "an integer number of days" against an IntCell — pass; asking for "a percent" against a FloatCell with no unit slot when statutes use mixed units — fail, schema-blocked). |
| 5 | **Null semantics** | Prompt names when to return null vs zero vs an empty/default value. Especially load-bearing for IntCell (0 days vs no deadline) and DecimalCell (0 dollars vs no threshold). |
| 6 | **Axis disambiguation** | For combined-axis rows (one YAML prompt shared between legal + practical CellSpecs with different cell types): the prompt must either (a) be unambiguously interpretable for both axes, or (b) flag as needing a per-axis prompt split (which is a schema change). |
| 7 | **Scope clarity (lobbyist vs principal)** | Where the same observable could be asked on either side (e.g., "does the spending report include X"), the prompt names which side. Default-7 already includes scope notes for most; this check confirms coverage. |
| 8 | **Schema mismatch** | The prompt does NOT implicitly assume a structure the cell type can't carry (the row #5 FloatCell-vs-statute-units case is the worked example). When this fails, the row is **SCHEMA-BLOCKED**, escalated for cell-type change before prompt revision. |

A prompt passing all 8 → `PASS`.
A prompt failing 1–7 but the fix is a prompt rewrite → `NEEDS-REVISION` with a draft revision.
A prompt failing #4 or #8 (cell-type schema can't carry what the prompt needs) → `SCHEMA-BLOCKED` with an escalation note.

---

## Phase 1 — Source familiarization (~30 min)

**Goal:** the audit agent reads the foundational context.

### Sequence

1. Read this plan end-to-end.
2. Read [`./20260606_phase_2_schema_aware_prompt_hygiene.md`](./20260606_phase_2_schema_aware_prompt_hygiene.md) end-to-end — the worked example, including the 7 revised prompts (these are the audit's gold standard for "laser-focused").
3. Read [`../results/20260606_failure_mode_trends_and_paths_forward.md`](../results/20260606_failure_mode_trends_and_paths_forward.md) — Trends 1, 3, 5, 6 are the failure modes the audit will likely re-surface.
4. Read [`../results/20260606_cpi_2015_c11_chunk_inventory.md`](../results/20260606_cpi_2015_c11_chunk_inventory.md) — chunk structure, cell-type histogram, the original "underspecified 11" analysis.
5. Read `compendium/source_quotes.yaml` (754 lines). Understand the YAML structure: one row per `row_id`, with `source_quotes:` dict (pedigree) and `prompt:` (the model-facing text).
6. Read `compendium/disclosure_side_compendium_items_v2.1.tsv`. Understand the per-row contract: `compendium_row_id`, `cell_type`, `axis`, `rubrics_reading` (paper-level pedigree), `n_rubrics`.
7. Read `src/lobby_analysis/models_v2/cells.py`. Understand each cell type's schema (the `value` or `magnitude`+`unit` contract).
8. Read `src/lobby_analysis/chunks_v2/manifest.py`. Understand how rows are grouped into chunks. ~20 chunks expected.
9. Read `src/lobby_analysis/models_v2/cell_spec.py`. Understand how `(row_id, axis)` maps to a CellSpec at registry-build time, including the combined-axis branch (lines ~213–226).

### Acceptance gate

- Audit agent can name (without re-reading) at least 5 cell types and their `value` shape.
- Audit agent can name the 6 CPI-2015 default chunks and the actor_registration_required Phase A extra chunk.
- Audit agent understands the extraction-vs-projection separation (can articulate why HG Q13's OR-projection belongs in a helper, not a prompt).

---

## Phase 2 — Chunk-by-chunk audit (~2–3 hours)

**Goal:** for each chunk, audit every prompt against the 8 dimensions and produce a per-chunk section of the findings doc.

**File produced:**
- `docs/active/cross-state-cpi-2015-validation/results/20260606_prompt_audit_findings.md` (new).

### Sequence

For each chunk, in this order (small chunks first, so context warm-up has fast feedback):

1. `enforcement_and_audits` (4 cells)
2. `registration_thresholds` (6 cells)
3. `actor_registration_required` (11 cells — Phase A extra chunk)
4. `registration_mechanics_and_exemptions` (10 cells)
5. `lobbying_definitions` (15 cells)
6. `principal_spending_report` (23 cells)
7. `lobbyist_spending_report` (35 cells)
8. All remaining chunks not in `_DEFAULT_CHUNKS + _PHASE_A_EXTRA_CHUNKS` (likely ~13 more, ~80 cells). Audit these even though they're not currently dispatched — the lean-prompt discipline applies to all of them, and Prong 2 (practical-axis dispatch) + later rubrics will surface them eventually.

For each chunk, iterate through its `cell_specs` (combined-axis rows produce one entry per axis but share the YAML prompt; audit per-row, with both axes' cell-type contracts considered in the verdict).

### Per-prompt audit output template

Append to the findings doc, one per (row_id, primary_axis):

```markdown
### `<row_id>` (axes: <legal/practical/both>, cell types: <list>, chunk: `<chunk_id>`)

**Source quotes (pedigree from YAML):**
- `<provenance_key>`: "<verbatim quote>"
(plus any others — usually 1; flag if >1)

**TSV pedigree (paper-level, may be richer than YAML):**
- `rubrics_reading`: <semicolon-list>
- `n_rubrics`: <int>
- `first_introduced_by`: <projection mapping doc>

**Current prompt:**
> "<verbatim from YAML>"

**Audit (8 dimensions):**
1. Extraction-vs-projection: ✓ / ✗ — <one-line reason>
2. Lean question: ✓ / ✗ — <one-line reason>
3. Return-shape spec: ✓ / ✗ — <one-line reason>
4. Cell-type alignment: ✓ / ✗ — <one-line reason>
5. Null semantics: ✓ / ✗ — <one-line reason>
6. Axis disambiguation (combined-axis only): ✓ / ✗ / N/A — <one-line reason>
7. Scope clarity (lobbyist vs principal): ✓ / ✗ / N/A — <one-line reason>
8. Schema mismatch: ✓ / ✗ — <one-line reason>

**Verdict:** PASS | NEEDS-REVISION | SCHEMA-BLOCKED

**Suggested revision** (NEEDS-REVISION only):
> "<draft lean prompt — full proposed YAML value>"

**Schema escalation** (SCHEMA-BLOCKED only):
- Issue: <what the cell type can't carry>
- Required schema change: <field add, cell-type promotion, axis split, etc.>
- Related affected rows: <list of others with the same gap, if any>
- Suggested separate plan: <yes/no — if yes, name it>

---
```

### Findings doc structure

Top-of-doc:

```markdown
# Prompt audit findings — `compendium/source_quotes.yaml` (all rows, 2026-06-06)

**Originating plan:** [`../plans/20260606_prompt_audit_all_questions.md`](../plans/20260606_prompt_audit_all_questions.md)
**Audit performed by:** <agent identifier + commit SHA>
**YAML audited at commit:** <SHA>

## Headline counts

| verdict | count | % |
|---|---:|---:|
| PASS | TBD | TBD |
| NEEDS-REVISION | TBD | TBD |
| SCHEMA-BLOCKED | TBD | TBD |
| **total** | **TBD** | **100%** |

## Schema-blocked rows (escalation summary)

(Per-issue summary table — the same gap may affect multiple rows; group them.)

| Issue | Affected rows | Proposed schema change | Separate plan? |
|---|---|---|---|
| ... | ... | ... | ... |

## Chunks audited

- [enforcement_and_audits](#chunk-enforcement_and_audits) (4 cells)
- [registration_thresholds](#chunk-registration_thresholds) (6 cells)
- ... etc.

---

## Chunk: `enforcement_and_audits`

(per-prompt blocks, as above)

---

## Chunk: `registration_thresholds`

(per-prompt blocks)

(...etc...)
```

### Acceptance gate (Phase 2)

- Findings doc has all ~183 rows audited.
- Each prompt has a verdict + (for NEEDS-REVISION) a draft revision + (for SCHEMA-BLOCKED) an escalation note.
- Headline counts table populated.
- Schema-blocked rows grouped by issue, with suggested separate plans named.
- Chunks ordered with TOC links to each chunk section.

---

## Phase 3 — Dan review of findings (~30 min Dan time)

**Goal:** Dan reviews the headline counts + schema escalations + spot-checks a sample of revisions.

### Sequence

1. Audit agent surfaces the findings doc location.
2. Dan reviews:
   - The headline counts (sanity check: are most prompts PASS, or did the audit grade too harshly?)
   - The schema-blocked escalations (these are the highest-leverage findings; each is a candidate separate plan)
   - A spot-check of ~5 randomly-picked NEEDS-REVISION drafts (validate the rewrite quality)
3. Dan feedback fed back into the findings doc; audit agent revises if needed.
4. Findings doc is then **frozen** as the handoff artifact for execution agents.

### Acceptance gate (Phase 3)

- Dan sign-off on findings doc.
- Frozen version committed.
- Schema-blocked escalations have a `next-step` line each.

---

## Phase 4 — Execution agents (separate, future, NOT this plan's scope)

**Goal:** apply the NEEDS-REVISION drafts to `compendium/source_quotes.yaml`. Excluded from this plan because:
- Each chunk's execution is independent and parallelizable.
- Different execution agents may benefit from different context windows (one per chunk).
- The audit agent's deliverable is the findings doc; execution is a separate plan.

A starter plan for the execution phase:
- One agent per chunk (or one agent for all chunks if the findings are small enough).
- Each execution agent: re-runs the Phase 2 plan's format-hint regression test, makes YAML edits matching the findings doc's drafts, confirms test passes, commits.
- Schema-blocked rows are NOT touched until their separate schema plans land.

---

## Risks & open caveats (read before audit start)

1. **The audit agent may grade too harshly.** The lean-prompt principle is a discipline, not an absolute. Some prompts NEED disambiguation preamble (e.g., the long lobbyist/principal scope-notes on combined-axis rows are load-bearing where a model could confidently extract the wrong side's observable). Auditor must justify any preamble it WOULD strip, and retain it if the justification doesn't hold up. Borderline cases → flag for Dan review, don't auto-fail.

2. **The TSV pedigree (`rubrics_reading`) is RICHER than the YAML's `source_quotes`.** 49 multi-rubric TSV rows have only 1 source quote in the YAML. The audit should:
   - Note the gap (display TSV `rubrics_reading` next to YAML `source_quotes` in each per-prompt block).
   - NOT attempt to recover the dropped source quotes from paper text — that's a separate Phase A pedigree-completeness pass.
   - For NEEDS-REVISION drafts on multi-rubric rows: draft from the YAML's single retained quote + the TSV's paper list (not from the dropped quotes themselves). This may produce a less-ideal revision than a full pedigree-aware rewrite, but it's honest about what the agent had access to.

3. **Combined-axis rows share one prompt across two cells with different return shapes.** The audit must produce one verdict per row (since one YAML edit affects both axes), but the verdict logic must consider both axes' cell types. If a single prompt can satisfy both (e.g., scope-note disambiguation + a return-shape line that names both shapes), draft accordingly. If not, the row is SCHEMA-BLOCKED on "needs per-axis prompts" (separate plan: extend the YAML schema to support `prompt_legal` + `prompt_practical` keys).

4. **The audit covers ALL chunks, not just dispatched ones.** Rationale: the lean-prompt discipline applies to every prompt, and Prong 2 + other rubric pipelines will eventually exercise them. But not-currently-dispatched rows are lower-priority for execution; the findings doc should mark them as such so execution agents can prioritize the actively-dispatched ones.

5. **The audit does NOT touch projection helpers, the TSV, the cell-type schemas, or any source code.** Read-only audit. Execution agents may edit YAML; schema agents (separate plans) edit cells.py / TSV / parser. Strict separation prevents the audit from sliding into execution.

6. **The audit produces only one new file: the findings doc.** No edits to existing docs, no commits to source code. The plan's Phase 3 freezes the findings doc with a Dan-reviewed commit.

7. **Context window pressure.** ~183 rows × 8 dimensions × per-prompt output is a lot of text. Use `handle-large-tasks` skill if context becomes an issue: split the audit across multiple agent invocations, each handling N chunks, with the findings doc grown incrementally. Each invocation reads the current findings doc state, audits its assigned chunks, appends. Headline counts populated at the end by the last agent.

---

## Pre-execution checklist (gating Phase 1 start)

The audit agent should confirm before reading the first source file:

- [ ] Read this plan end-to-end.
- [ ] Confirm worktree is clean + on `cross-state-cpi-2015-validation` at HEAD `cbcd3e2` or later.
- [ ] Confirm `compendium/source_quotes.yaml` exists and has ~183 entries (sanity: `yq '. | length' < compendium/source_quotes.yaml` or equivalent).
- [ ] Confirm `compendium/disclosure_side_compendium_items_v2.1.tsv` exists and has the `rubrics_reading` + `n_rubrics` columns.
- [ ] Confirm the Phase 2 plan ([`./20260606_phase_2_schema_aware_prompt_hygiene.md`](./20260606_phase_2_schema_aware_prompt_hygiene.md)) is on disk in the same plans directory.
- [ ] Confirm `src/lobby_analysis/chunks_v2/manifest.py` lists ~20 chunks.
- [ ] Audit agent has acknowledged in its own words: "I am NOT editing the YAML or source code. I am producing a single new file: `docs/active/cross-state-cpi-2015-validation/results/20260606_prompt_audit_findings.md`."

---

## What's explicitly NOT in this plan (deferred)

- **Editing `compendium/source_quotes.yaml`.** Execution agents do this in a separate plan, reading the findings doc as their spec.
- **Cell-type schema changes.** SCHEMA-BLOCKED rows escalate to separate plans (one per distinct schema issue).
- **YAML pedigree-completeness pass** (recovering the dropped source quotes for the 49 multi-rubric rows). Separate plan.
- **Projection helper updates** triggered by any audit findings. Each helper change is its own concern.
- **Audit of `source_quotes.yaml` rows for OTHER rubrics' rows** that aren't yet in the compendium TSV. Out of scope — audit is bounded to the existing TSV roster.
- **Re-running any dispatch.** The audit is paper-only; no API spend.

---

## Cost summary

| phase | cost | time | scope |
|---|---:|---:|---|
| 1 — source familiarization | $0 | ~30 min | reading |
| 2 — chunk-by-chunk audit | $0 | ~2–3 hr | findings doc creation |
| 3 — Dan review + freeze | $0 | ~30 min Dan + ~30 min agent (revise) | findings doc edits |
| **total** | **$0** | **~3.5–4.5 hr execution + Dan review** | one or more audit sessions |

After Phase 3 lands, the findings doc is the handoff to execution agents in a separate plan (out of scope for this one).
