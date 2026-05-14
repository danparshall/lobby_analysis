# Phase B close + post-Phase-B forward plan — handoff

**Originating plan:** [`../20260507_atomic_items_and_projections.md`](../20260507_atomic_items_and_projections.md) (Phase B is now complete; Phase C unstarted)
**Predecessor handoff (now stale):** [`20260511_phase_b_continued_remaining_7.md`](20260511_phase_b_continued_remaining_7.md) — covers the in-progress Phase B work that has since closed.
**Originating convo (this handoff):** [`../../convos/20260513_lobbyview_phase_b_final_and_focal1_resolution.md`](../../convos/20260513_lobbyview_phase_b_final_and_focal1_resolution.md)
**Date drafted:** 2026-05-13 (late-late eve)
**Audience:** the next-session agent picking up after Phase B close. Fresh-context-safe.

---

## Why this handoff exists

The 2026-05-11 handoff covered the in-progress Phase B work (7 rubrics remaining). All 9 Phase B mappings have now shipped (the last two, FOCAL 2024 and LobbyView 2018/2025, landed 2026-05-13 late eve and late-late eve respectively; FOCAL-1 was resolved by user decision the same session). The original Phase B plan called for a union step + Phase C kickoff after Phase B close. The 2026-05-13 follow-up planning conversation locked a richer forward plan that this handoff captures.

**Read order for the next-session agent:**
1. This handoff
2. The locked plan: [`../20260507_atomic_items_and_projections.md`](../20260507_atomic_items_and_projections.md) — for Phase B done-condition definition and Phase C order
3. The most recent convo summary: [`../../convos/20260513_lobbyview_phase_b_final_and_focal1_resolution.md`](../../convos/20260513_lobbyview_phase_b_final_and_focal1_resolution.md)
4. The 9 mapping docs in `../../results/projections/` (skim Summary tables; deep-read on demand)

---

## What's locked since the 2026-05-11 handoff

### Phase B is complete

All 9 mappings shipped:

| # | Rubric | Rows touched | Reuse / new | Date |
|---|---|---|---|---|
| 1 | CPI 2015 C11 | 21 | breakthrough | 2026-05-07 eve |
| 2 | PRI 2010 | 69 | ~52 new | 2026-05-07 late eve |
| 3 | Sunlight 2015 (4-of-5 scope) | 13 | 11 cross-rubric | 2026-05-11 |
| 4 | Newmark 2017 | 14 | 8 reused + 6 new | 2026-05-13 |
| 5 | Newmark 2005 | 14 | 100% reuse | 2026-05-13 pm |
| 6 | Opheim 1991 | 14 (15 items; 1 un-projectable) | 100% reuse | 2026-05-13 pm late |
| 7 | HiredGuns 2007 | 38 | 16 reused + 22 new (42%, lowest) | 2026-05-13 eve |
| 8 | FOCAL 2024 | 58 (post-FOCAL-1) | 22 reused + 36 new (37.9%) | 2026-05-13 late eve |
| 9 | LobbyView 2018/2025 | schema-coverage (46 fields) | 14/18 = 78% Federal_US coverage | 2026-05-13 late-late eve |

OpenSecrets 2022 structured-tabled 2026-05-13 (reversible) — 3 OS-distinctive row candidates also tabled.

### FOCAL-1 resolved

`revolving_door.1` pulled IN scope (against the strict-plan reading). NEW row `lobbyist_reg_form_includes_lobbyist_prior_public_offices_held` (binary; legal). `revolving_door.2` stays deferred (enforcement-adjacent meta-publication).

**Validation within session:** LobbyView's `covered_official_position` (LDA §18; the canonical federal disclosure observable for revolving-door research used by Kim 2025's GNN) maps directly onto the just-added row. Row is now **2-rubric-confirmed (FOCAL + LobbyView)** within hours of being introduced.

US LDA Phase C tolerance closes from +6pt to 0pt on raw points (≤1pp residual percentage delta is denominator-shift only).

### Three watchpoints from the 2026-05-11 handoff are resolved

1. **`contributions_from_others` final promotion check** → NO PARALLEL in LobbyView. Row is now single-rubric across the entire 9-rubric contributing set. **Compendium 2.0 freeze recommendation: KEEP** per Newmark-distinctive-observable rationale (real but unusual; MA principal reports list earmarked dues).
2. **`def_target_*` 4-cell extension validation** → CONFIRMED via LDA §17 + 2 USC §1602(4) "covered legislative branch official" definition. All 4 cells `TRUE` for federal jurisdiction.
3. **FOCAL-1 row validation** → CONFIRMED via LDA §18 (see above).

### Compendium 2.0 row inventory standing

**~111 disclosure-side rows** (110 pre-FOCAL-1 + 1 from FOCAL-1 + 0 from LobbyView's freeze-deferred candidates). If row-freeze pulls in LV-1..LV-4 + other freeze-deferred candidates, the count may grow to ~115-120.

### Decided: Option B for the row-freeze sequencing

User decision 2026-05-13: row-freeze brainstorm is a **small standalone session BEFORE merging this branch to main.** Rationale: "freeze" should actually mean frozen at merge so the 3 parallel successor tracks (OH retrieval, harness brainstorm, projection TDD) have a stable row-set contract. The ~5-10 candidate row deltas are small but real — they affect harness chunking, projection scoping, and OH extraction targets.

---

## Next-session scope (the agent picking up this handoff)

The next session should do all of the following, in order. None of it requires deep research — this is the Phase B-done plumbing + post-B forward planning that sets up parallel work.

### 1. Union step (mechanical; ½ session at most)

Per the locked plan's Phase B done condition:

> Union all 9 score-projection mapping docs' `compendium_rows` lists; de-dupe; save as `results/projections/disclosure_side_compendium_items_v1.tsv`.

(Note: 8 score-projection mapping docs + 1 schema-coverage mapping doc. LobbyView's schema-coverage mapping doesn't introduce rows to the union directly — its 4 candidate NEW rows are freeze-deferred — but it should be referenced for the candidate-NEW-rows column.)

**Suggested TSV columns:**
- `compendium_row_id` (working name from mapping docs)
- `cell_type` (binary / typed_decimal / typed_enum / set_typed / structured)
- `axis` (legal_availability / practical_availability)
- `rubrics_reading` (semicolon-separated rubric refs — e.g., `cpi_2015:#197;newmark_2017:def.compensation_standard;hg_2007:Q2`)
- `n_rubrics` (count)
- `source_mapping_doc` (which mapping doc first introduced the row)
- `status` (firm / freeze-candidate / freeze-deferred)
- `notes` (cross-rubric, Open Issue refs, granularity warnings)

**Tool suggestion:** small Python script `tools/union_projection_rows.py` reading each of the 8 score-projection mapping docs' Summary tables (markdown-parseable) plus the LobbyView coverage doc's candidate-NEW-rows section. Use `pandas` for the dedup join. Write the script to `tools/` (project root) so it's reusable for future audits.

**Stop condition:** `results/projections/disclosure_side_compendium_items_v1.tsv` exists with ~111 firm rows + flagged freeze candidates listed separately or in a `status` column. Spot-check 5-10 rows against the source mappings to confirm the rubric-reads column resolves correctly.

### 2. Pre-merge audit + sanity checks (½ session)

Per CLAUDE.md "branch history becomes main's history" — the branch has been long-lived (2026-05-02 → 2026-05-13, ~11 days, many sessions). Cheap insurance before merge.

- **Run `audit-docs` skill** on `docs/active/compendium-source-extracts/` — verifies every convo is indexed in RESEARCH_LOG, every plan links to its convo, no orphans.
- **`git log --stat` glance** — confirm no large data blobs snuck in. The branch has been mapping-doc heavy; surprises unlikely but verify.
- **PAPER_INDEX.md / PAPER_SUMMARIES.md sanity check** — 26 papers were extracted on this branch (vs the 7 originally scoped). Confirm the new papers are indexed + summarized. If not, run `auditing-paper-summaries` skill.

If any of these surface real gaps, fix in place before drafting the 3 plan docs.

### 3. Draft 3 plan docs for the parallel successor tracks (1-1.5 sessions)

Each plan follows the `write-a-plan` skill — self-contained, references originating convo, assumes fresh-context implementing agent. All 3 land at `docs/active/compendium-source-extracts/plans/`.

#### 3a. OH statute retrieval pipeline

**Filename:** `plans/20260514_oh_statute_retrieval_pipeline.md` (adjust date as needed)

**Scope:**
- Add OH 2007 + OH 2015 URLs to `LOBBYING_STATUTE_URLS` (in `src/lobby_analysis/scoring/statute_retrieval/` or wherever the curated dict lives on the archived `statute-retrieval` branch — verify path after merge)
- Run `justia_client` probe to confirm OH coverage at 2007 (the 2026-04-18 audit showed CO earliest = 2016; OH may be earlier — probe will confirm)
- Retrieve OH 2007 + OH 2015 bundles (existing 2010 + 2025 bundles already in repo from statute-retrieval branch)
- **Parallel sub-task: HiredGuns 2007 per-state per-question ground truth retrieval.** Per the HG mapping, the methodology TSV is in repo but per-state per-question scorecard pages once hosted at `publicintegrity.org/politics/state-politics/influence/hired-guns/`. **Likely need Wayback Machine.** If the pages are gone, HG validation degrades from per-item to sub-aggregate-only.

**Inherits from archived branches:**
- `statute-retrieval` (already merged to main 2026-04-30): `justia_client`, `LOBBYING_STATUTE_URLS`, `retrieve-statutes` + `expand-bundle` + `ingest-crossrefs` orchestrator subcommands. The pipeline is operational — this plan adds 2 (state, vintage) entries + runs retrieval.

**Out of scope:** scaling to non-OH states (that's after the OH end-to-end validation works).

**Stop condition:** OH 2007 + OH 2015 bundles in the repo (or documented unavailability for 2007); HG 2007 per-state scorecard CSV retrieved or documented as unavailable.

#### 3b. Extraction harness brainstorm

**Filename:** `plans/20260514_extraction_harness_brainstorm.md`

This is a brainstorm-then-plan, not direct implementation. Use the `brainstorming` skill explicitly per CLAUDE.md. Output is a follow-on plan doc; this plan is for the brainstorm session itself.

**Brainstorm dimensions** (from the 2026-05-13 follow-up convo):

- **Chunking strategy.** 111 rows in one prompt? Per-`domain` chunks (definitions / scope / itemization / cadence / contact_log / portal / etc.)? Per-rubric? The archived `statute-extraction` branch (paused) shipped `chunk_frames/definitions.md` at 7-row scope with a frame preamble — scaling that pattern is one option. 111 rows is ~15× the iter-1 scope; need a chunking design.
- **Artifacts to inherit from `statute-extraction` iter-2** (paused branch; archived):
  - v2 scorer prompt
  - files-read enforcement (`files_read.json` sidecar + locked-prompt Rule 7 + orchestrator fail-closed)
  - Tightened axis-explicit row descriptions (was applied to 7-row definitions chunk)
  - `chunk_frames/definitions.md` per-chunk preamble pattern
  - `ExtractionRunMetadata` model + `extract-prepare` / `extract-finalize` orchestrator subcommands
- **Typed-cell handling.** Decimal thresholds, enum cadence, structured `TimeThreshold {magnitude, unit}`, set-typed cells (`lobbyist_definition_included_actor_types`, `lobbying_definition_included_activity_types`). Prompt must produce typed values, not yes/no.
- **`unable_to_evaluate` vs `not_addressed` vs `required_conditional`.** iter-1 landed these patterns; need consistent grammar across 111 rows.
- **Resume/checkpoint** per CLAUDE.md experiment-data-integrity rules.
- **Practical-availability scope boundary:** harness extracts from statute text → **legal_availability only**. Practical cells stay null; Track B portal pipeline (other fellow's `oh-portal-extraction`) populates them.
- **Cost/wall-clock budget per (state, vintage)** — informs chunking + parallelism.
- **Multi-run / consensus pattern** — earlier statute-retrieval / statute-extraction work ran 3 concurrent opus runs and measured inter-run agreement. Keep or change?

**Anti-pattern to avoid:** the archived `statute-retrieval` branch's `cmd_build_smr` + `smr_projection` modules are the **wrong shape** for compendium 2.0 (they're PRI-rubric-shaped, compendium-1.x-keyed). The locked plan explicitly says "do NOT use as a template." Inherit only the prompt-architecture pieces.

**Stop condition:** Brainstorm doc → follow-on implementation plan that another agent can execute. Brainstorm doc should clearly answer the dimensions above. Implementation plan should be TDD-shaped where it's code.

#### 3c. Phase C projection TDD — 8 rubrics

**Filename:** `plans/20260514_phase_c_projection_tdd.md`

Per the locked plan, Phase C order is:

1. CPI 2015 C11 (smallest target — 14 items × 5 sub-categories × 50-state ground truth)
2. PRI 2010 (largest item set — 83 items × full per-state per-item ground truth)
3. Sunlight 2015 (4-of-5 scope; 5 items; 50-state per-category data)
4. Newmark 2017 (14 rows; per-state sub-aggregates only — direct tolerance check is weaker)
5. Newmark 2005 (14 rows; 100% reuse from 2017; per-state main-index only)
6. Opheim 1991 (14 row families + 1 un-projectable; 47-state index totals only)
7. HiredGuns 2007 (38 rows; per-state per-question if HG ground-truth retrieval succeeds; otherwise sub-aggregate-only)
8. FOCAL 2024 (58 rows post-FOCAL-1; federal-LDA-only per-indicator ground truth from L-N 2025 Suppl File 1)

**LobbyView is NOT a Phase C target** (schema-coverage, no score to project). 8 rubrics total.

**Per-rubric Phase C work** (from the locked plan §Phase C):
1. Implement `project_<rubric>(compendium_cells, vintage) → RubricScore` in `src/lobby_analysis/projections/<rubric>.py` (verify path against existing `src/lobby_analysis/` layout post-merge).
2. **Unit tests** with synthetic cell values exercising each per-item scoring branch + the aggregation rule. Tests verify projection LOGIC, not extraction. Per testing-anti-patterns skill: tests test behavior (does the projection produce the right rubric score given the right cells), not mocks/implementation.
3. **Integration test fixture**: hand-populate compendium cells for ONE state in the rubric's vintage. Hand-populated cells are correct-by-construction relative to the source rubric being tested (e.g., populate OH 2010 cells from PRI 2010 OH per-item answers).
4. Run projection on hand-populated cells; compare to published per-state aggregate; match within rubric-specific tolerance.
5. **Cross-rubric validation**: same hand-populated cells; run a *different* rubric's projection; compare to that other rubric's published score. Cross-validates that the cells are consistent across rubrics' interpretations.

**Out of scope:** real extraction (that's the harness's job). Hand-populated cells are test scaffolding only.

**Inputs the implementing agent needs:**
- Union TSV from §1 above (the row-set contract)
- 8 mapping docs in `../../results/projections/` (per-rubric scoring + aggregation rules)
- Ground-truth files:
  - PRI 2010 → `docs/historical/pri-2026-rescore/results/pri_2010_disclosure_law_rubric.csv` + `pri_2010_accessibility_rubric.csv`
  - CPI 2015 → `results/cpi_2015_c11_per_state_scores.csv`
  - Sunlight 2015 → `papers/Sunlight_2015__state_lobbying_disclosure_scorecard_data.csv`
  - FOCAL 2024 → `results/focal_2025_lacy_nichols_per_country_scores.csv`
  - Newmark 2017 → Table 2 in `papers/Newmark_2017_*.pdf` (transcribe if not already)
  - Newmark 2005 → Table 1 in `papers/Newmark_2005_*.pdf` (transcribe if not already)
  - Opheim 1991 → Table 1 in `papers/Opheim_1991_*.pdf` (transcribe if not already)
  - HG 2007 → depends on retrieval (§3a sub-task)

**Stop condition:** 8 projection functions implemented + unit-tested + integration-tested for at least one (state, vintage) per rubric. Cross-rubric validation passes for at least one shared row (e.g., `lobbyist_spending_report_includes_total_compensation` is read by 7 rubrics; populate the cell once, verify all 7 projections produce their respective correct outputs).

### 4. Hand off to row-freeze brainstorm session (next-next session)

Per Option B (decided 2026-05-13), a separate small brainstorm session resolves freeze decisions on:

- 4 LobbyView candidate NEW rows (LV-1 in-house-vs-contract; LV-2 amendment flag; LV-3 standardized issue-code taxonomy; LV-4 full-text-search-index split). LV-5 (bill_client_link) recommended OUT.
- 3 OpenSecrets-distinctive tabled rows (separate-registrations; lobbyist-compensation-as-exact-vs-ranges; lobbyist-compensation-per-individual-vs-aggregate)
- FOCAL Open Issues 2-11 (set-typed-vs-binary atomization on scope.1/scope.4; partly-tier mechanics on openness.1/4 + relationships.4; α form-pair on descriptors.1-5)
- HG Open Issues 1-7 (gift-granularity split; household-member scope; business-association split; etc.)
- Newmark Open Issue 1 (`def_actor_class_*` family, 3-rubric-confirmed; freeze design)
- Final disposition of `lobbyist_or_principal_report_includes_contributions_received_for_lobbying` (current recommendation: KEEP per Newmark-distinctive-observable rationale; single-rubric across full 9-rubric set per LobbyView Watchpoint 1)

After freeze: regenerate `disclosure_side_compendium_items_v1.tsv` → `_v2.tsv` (or update in place). Then merge `compendium-source-extracts` → main. Then cut 3 successor branches:
- `oh-statute-retrieval` (or extend the operational `oh-portal-extraction` if owner agrees)
- `extraction-harness-design`
- `phase-c-projections`

Each successor branch creates its own `docs/active/<branch-name>/` scaffolding with the relevant plan as the kickoff doc.

---

## Standing watchpoints (carry forward)

1. **`lobbyist_or_principal_report_includes_contributions_received_for_lobbying`** is single-rubric across the full 9-rubric contributing set. Freeze recommendation: KEEP. Single-rubric ≠ deletion criterion when the underlying observable is real (MA principal reports list earmarked dues; some states explicitly require disclosure of restricted contributions received).

2. **`def_actor_class_*` family is 3-rubric-confirmed** (Newmark 2017 + Newmark 2005 + Opheim). HG / FOCAL / LobbyView are NOT readers (HG Q1-Q4 read target/threshold/gateway/deadline, not actor-class definitional inclusion; FOCAL scope reads target side; LobbyView §17 reads gov_entity contacted, not the lobbyist-side definition). Open Issue 1 from Newmark 2017 mapping is **resolved-in-principle** for freeze planning.

3. **Three lobbyist-status threshold cells** (compensation / expenditure / time) are 3-rubric-confirmed (Newmark 2017 + Newmark 2005 + Opheim; CPI #197 reads the compensation cell at coarser granularity). Federal LDA reads compensation + time but not expenditure threshold. Lock at compendium 2.0.

4. **Gifts/entertainment/transport/lodging bundle** is 5-rubric-confirmed at combined granularity (PRI + Newmark 2017 + Newmark 2005 + Opheim + HG + FOCAL `financials.10`). HG Q23 gifts-specific granularity is a separate freeze question (split bundle by benefit type, or keep combined?).

5. **`lobbyist_spending_report_includes_total_compensation`** is 7-rubric-confirmed — the most-validated row in the compendium. Lock at compendium 2.0.

6. **Practical-availability cells** (~⅓ of the ~111 rows) require portal observation, not statute extraction. Track A (statute extraction) populates only legal_availability cells; Track B (portal pipeline; other fellow's `oh-portal-extraction`) populates practical_availability. The harness brainstorm plan should make this scope boundary explicit.

7. **Newmark 2005 / Opheim 1991 / Newmark 2017 publish per-state aggregates only** (no per-item). Direct Phase C tolerance check for these rubrics reduces to a weak inequality (`projected_partial ≤ paper_total`). Per-item validation only via cross-rubric overlap with PRI 2010 + CPI 2015 (the per-item rubrics). Phase C plan should accept this.

8. **FOCAL 2024 has no per-state US ground truth** — only federal LDA. State-level Phase C validation for FOCAL = cross-rubric overlap with PRI/CPI/Sunlight/HG only. Federal LDA validation anchor: 81/182 = 45% (and now exactly 81 raw points / 180 in-scope max = 45.0% projected after FOCAL-1).

9. **`statute-retrieval` branch's `cmd_build_smr` / `smr_projection`** is the WRONG shape for compendium 2.0 — compendium-1.x-keyed + PRI-only. Locked plan explicitly says "do NOT use as a template." Inherit only the prompt-architecture pieces from `statute-extraction` iter-2.

---

## Files this handoff is the index for

- Convo summary (Phase B close session): [`../../convos/20260513_lobbyview_phase_b_final_and_focal1_resolution.md`](../../convos/20260513_lobbyview_phase_b_final_and_focal1_resolution.md)
- FOCAL mapping (updated for FOCAL-1): [`../../results/projections/focal_2024_projection_mapping.md`](../../results/projections/focal_2024_projection_mapping.md)
- LobbyView schema-coverage mapping: [`../../results/projections/lobbyview_schema_coverage.md`](../../results/projections/lobbyview_schema_coverage.md)
- Predecessor handoff (now stale, kept for audit trail): [`20260511_phase_b_continued_remaining_7.md`](20260511_phase_b_continued_remaining_7.md)
