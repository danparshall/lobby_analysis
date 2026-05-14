# Compendium v2 Row-ID Rename Execution Plan

**Goal:** Apply 15 accepted row-ID renames (plus 1 README typo fix) from §10 of `compendium/NAMING_CONVENTIONS.md` to the compendium v2 contract, producing a v3 TSV with consistent prefix families and a clean cross-reference path from old names to new.

**Originating conversation:** [`docs/active/compendium-naming-docs/convos/20260514_rename_review_and_plan.md`](../convos/20260514_rename_review_and_plan.md) (this session — walkthrough of all 8 candidates, all accepted). See also the kickoff convo [`20260514_naming_taxonomy_kickoff.md`](../convos/20260514_naming_taxonomy_kickoff.md) for the audit that produced the §10 candidate list.

**Context:** The kickoff audit on `compendium-naming-docs` surfaced 8 rename candidates in §10 of `compendium/NAMING_CONVENTIONS.md` and locked scope to **audit + flag, defer renames** to keep sister-branch merges (`phase-c-projection-tdd`, `extraction-harness-brainstorm`, `oh-statute-retrieval`) clean during their active lifecycles. The 2026-05-14 walkthrough session reviewed each candidate one-at-a-time with downstream-consumer fan-out; all 8 were accepted. This plan is the execution brief for the future rename branch, to be cut once sister-branch lifecycles settle.

**Confidence:** High on the rename targets themselves (Dan reviewed all 8 with full downstream-consumer cost visible). Medium on execution timing — depends on `extraction-harness-brainstorm` Pydantic-model state at execution time. Low risk of needing to revisit any individual rename target.

**Architecture:** Extend `tools/freeze_canonicalize_rows.py` with a new `V2_TO_V3_RENAMES` rename dict (same shape as the existing v1→v2 rename machinery) and a `--target-version=v3` flag. Output `compendium/disclosure_side_compendium_items_v3.tsv`, then immediately deprecate v2 to `compendium/_deprecated/v2/` (mirroring the v1 deprecation pattern from `compendium-v2-promote`). No transition window — sister branches absorb on their next merge, which is the coordination model Phase 0's pre-execution grep validates. Update `compendium/NAMING_CONVENTIONS.md` §10 in place to mark each candidate **DONE** (the §10 Issue 2 header "5 rows" → "6 rows" was already patched in the audit branch alongside this plan). Update `compendium/README.md` to fix the `cpi_2015_c11_projection_mapping.md` filename typo. Regenerate the prefix-survey and provenance-table artifacts from the new TSV (their scripts are already re-runnable).

**Branch:** New branch `compendium-row-renames-v3` (or similar) cut off `main` at the time of execution — NOT cut off `compendium-naming-docs`. The audit branch is plan-only; execution happens on a fresh branch when sister-branch timing allows.

**Tech Stack:** Python (csv, pathlib stdlib only — same as existing `freeze_canonicalize_rows.py`). pytest for the rename-validity checks.

---

## 1. The accepted rename set (15 row renames + 1 README fix)

### Candidate 1 — Joint-actor ordering fix (1 row)

| Old row_id | New row_id |
|---|---|
| `principal_or_lobbyist_reg_form_includes_member_or_sponsor_names` | `lobbyist_or_principal_reg_form_includes_member_or_sponsor_names` |

Source rubric: FOCAL. Single-rubric. Aligns with all 5 other joint-actor rows.

### Candidate 2 — D3 rename gaps (6 rows)

| Old row_id | New row_id | Source |
|---|---|---|
| `lobbyist_report_distinguishes_in_house_vs_contract_filer` | `lobbyist_filing_distinguishes_in_house_vs_contract_filer` | LV-1 (D12 promotion) |
| `lobbyist_report_includes_campaign_contributions` | `lobbyist_spending_report_includes_campaign_contributions` | Newmark 2017 |
| `lobbyist_or_principal_report_includes_lobbyist_count_total_and_FTE` | `lobbyist_or_principal_spending_report_includes_lobbyist_count_total_and_FTE` | FOCAL |
| `lobbyist_or_principal_report_includes_time_spent_on_lobbying` | `lobbyist_or_principal_spending_report_includes_time_spent_on_lobbying` | FOCAL |
| `lobbyist_or_principal_report_includes_trade_association_dues_or_sponsorship` | `lobbyist_or_principal_spending_report_includes_trade_association_dues_or_sponsorship` | FOCAL |
| `principal_report_lists_lobbyists_employed` | `principal_spending_report_lists_lobbyists_employed` | FOCAL |

> **LV-1 is the categorical exception.** It goes to `lobbyist_filing_*` (schema-coverage observable, joining `lobbyist_filing_de_minimis_threshold_*`), not `_spending_report_*`. The other 5 go to `_spending_report_*`. This was a deliberate decision in the 2026-05-14 walkthrough — LobbyView coverage rows are meta-observables about the filing apparatus, semantically different from report-content rows. Do not "unify" LV-1 to `_spending_report_*` during execution without re-opening the convo.

**§10 Issue 2 header inconsistency:** the audit-branch session that produced this plan fixed the header from "(5 rows)" to "(6 rows)" in `compendium/NAMING_CONVENTIONS.md` before merge. No action needed on the rename-execution branch.

### Candidate 3 — Registration-threshold trio (3 rows, high-traffic)

| Old row_id | New row_id |
|---|---|
| `compensation_threshold_for_lobbyist_registration` | `lobbyist_registration_threshold_compensation_dollars` |
| `expenditure_threshold_for_lobbyist_registration` | `lobbyist_registration_threshold_expenditure_dollars` |
| `time_threshold_for_lobbyist_registration` | `lobbyist_registration_threshold_time_percent` |

**This is the highest-traffic rename in the batch.** `compensation_threshold` is 6-rubric; `expenditure_threshold` and `time_threshold` are 4-rubric. Load-bearing for HG Q2 (D22) and for D4's three-threshold framework.

### Candidate 4 — Itemization de-minimis family fit (1 row)

| Old row_id | New row_id |
|---|---|
| `expenditure_itemization_de_minimis_threshold_dollars` | `lobbyist_filing_itemization_de_minimis_threshold_dollars` |

Source: Newmark + Sunlight. Pairs structurally with `lobbyist_filing_de_minimis_threshold_dollars` (D4's second concept), so both de-minimis concepts share the `lobbyist_filing_*` family.

### Candidate 5 — Registration deadline family fit (1 row)

| Old row_id | New row_id |
|---|---|
| `registration_deadline_days_after_first_lobbying` | `lobbyist_registration_deadline_days_after_first_lobbying` |

Source: CPI 2015. 2-rubric. Two-axis (D11).

### Candidate 6 — Ministerial-diary plural drift (1 row)

| Old row_id | New row_id |
|---|---|
| `ministerial_diaries_available_online` | `ministerial_diary_available_online` |

Source: FOCAL. Standardize on singular across the 2-row family (`ministerial_diary_disclosure_cadence` already singular).

### Candidate 7 — Definitional-row family fit (2 rows)

| Old row_id | New row_id |
|---|---|
| `lobbying_definition_included_activity_types` | `def_lobbying_activity_types` |
| `lobbyist_definition_included_actor_types` | `def_lobbyist_actor_types` |

Source: FOCAL. Joins the `def_*` family with `def_target_*`, `def_actor_class_*`, etc.

### Candidate 8 — README typo (not a row rename)

In `compendium/README.md` §"How Compendium 2.0 was built", update the listed projection-mapping doc filename from `cpi_2015_projection_mapping.md` to `cpi_2015_c11_projection_mapping.md` (matching the actual filename in `docs/historical/compendium-source-extracts/results/projections/`).

### Rename totals

- **15 row renames** across 8 candidate clusters
- **1 README typo fix** (Candidate 8)
- **1 doc-header fix** (§10 Issue 2: "5 rows" → "6 rows")

---

## 2. Downstream-consumer fan-out per rename cluster

The cost surface for any rename is the union of:

| Consumer | Action |
|---|---|
| `compendium/disclosure_side_compendium_items_v2.tsv` → v3 | Regenerate via extended `freeze_canonicalize_rows.py` |
| `compendium/NAMING_CONVENTIONS.md` | Update §10 entries to **DONE**, update body cross-refs, fix §10 Issue 2 header |
| `compendium/README.md` | Fix the projection-mapping doc filename typo (Candidate 8) |
| `docs/historical/compendium-source-extracts/results/projections/*.md` | **Immutable archives — do not edit.** The rename table in this plan IS the old→new resolver for archive readers. |
| `tools/freeze_canonicalize_rows.py` | Extend with `V2_TO_V3_RENAMES` dict |
| `src/lobby_analysis/models/*.py` (v1.1 Pydantic) | **No action.** Pre-scanned: row-ID-agnostic, no candidate row IDs hard-coded. |
| `src/lobby_analysis/compendium_loader.py` | **No action.** Pre-scanned: row-ID-agnostic. |
| `extraction-harness-brainstorm` Pydantic models (chunks_v2, future row-ID enums) | **Sister-branch coordination.** Check at execution time whether any model enumerates candidate row IDs. If yes, coordinate with branch owner before execution. |
| `phase-c-projection-tdd` projection functions | **Sister-branch coordination.** Projection code likely references high-traffic rows from Candidates 3 and 4. Check at execution time. |
| `oh-statute-retrieval` | Lower probability of row-ID references; verify at execution time. |
| Prompt strings (future, for extraction) | List the 15 old→new mappings in the prompt-string update PR when extraction work hardens. |
| `STATUS.md`, branch RESEARCH_LOGs | Narrative updates as part of finish-convo on the rename-execution branch. |

### Per-candidate consumer hotspots (use as a coordination checklist at execution time)

**Candidate 2 LV-1** (`lobbyist_filing_distinguishes_in_house_vs_contract_filer`):
- `docs/historical/compendium-source-extracts/results/projections/lobbyview_schema_coverage.md` — references the old name in narrative; do not edit (archive) but be aware
- Future Pydantic: this is one of the LV-1 schema-coverage rows; any LobbyView-side extraction model will reference it

**Candidate 3** (registration threshold trio — **the riskiest cluster**):
- `docs/historical/compendium-source-extracts/results/projections/hiredguns_2007_projection_mapping.md` — D22 references `compensation_threshold` directly
- `docs/historical/compendium-source-extracts/results/projections/pri_2010_projection_mapping.md`, `cpi_2015_c11_projection_mapping.md`, `sunlight_2015_projection_mapping.md`, `newmark_2005_projection_mapping.md`, `newmark_2017_projection_mapping.md`, `opheim_1991_projection_mapping.md`, `focal_2024_projection_mapping.md` — all reference one or more of the trio (6-rubric and 4-rubric)
- Future Pydantic and prompt strings: this is the most-likely-to-be-enumerated cluster
- **Pre-execution check:** before cutting the rename branch, grep `extraction-harness-brainstorm` and `phase-c-projection-tdd` worktrees for the three old names. If found, brief the branch owners.

**Candidate 4** (`lobbyist_filing_itemization_de_minimis_threshold_dollars`):
- `docs/historical/compendium-source-extracts/results/projections/sunlight_2015_projection_mapping.md`, `newmark_2017_projection_mapping.md` — historical, no edit
- Future: pairs with `lobbyist_filing_de_minimis_threshold_dollars`; downstream extraction models will likely treat both as a pair

**Candidates 1, 5, 6, 7** (lower-cost: 1-2 rows, single-rubric, lower traffic):
- Mostly FOCAL-introduced (1-rubric); historical projection-mapping doc references are isolated to `focal_2024_projection_mapping.md`
- Future Pydantic absorption is mechanical

**Candidate 8** (README typo): self-contained in `compendium/README.md`.

---

## 3. Testing plan

I will add behavior tests for the rename machinery before extending `freeze_canonicalize_rows.py`. The tests live alongside the tool (suggested: `tools/test_freeze_canonicalize_rows.py` or `tests/test_rename_v2_to_v3.py` — match existing repo convention; check `tests/` layout at execution time).

**Behavior tests for `V2_TO_V3_RENAMES` (the new rename machinery):**

- Test that running the v2→v3 transformation on the current `compendium/disclosure_side_compendium_items_v2.tsv` produces a TSV with exactly 181 rows (no rows added, no rows dropped).
- Test that for each of the 15 (old, new) pairs, the old name does **not** appear in any `compendium_row_id` column of the regenerated v3 TSV and the new name **does**.
- Test that for each renamed row, all non-`compendium_row_id` columns (source rubrics, cell_type, axis, `first_introduced_by`, provenance) are byte-identical between v2 and v3. The rename is a pure ID swap; nothing else changes.
- Test that the LV-1 row `lobbyist_report_distinguishes_in_house_vs_contract_filer` renames to `lobbyist_filing_distinguishes_in_house_vs_contract_filer` (NOT `lobbyist_spending_report_distinguishes_in_house_vs_contract_filer`). This is the categorical-exception case and deserves an explicit test so future agents can't quietly "unify" the cluster.
- Test that the three Candidate-3 rows all land at `lobbyist_registration_threshold_<measure>_<unit>` with the correct unit suffix per row (`_dollars` for compensation and expenditure, `_percent` for time).
- Test that the rename dict contains exactly 15 entries (no accidental additions or duplicates).
- Test that re-running the prefix-survey script (`docs/active/compendium-naming-docs/results/20260514_prefix_survey.py` or its post-execution successor on the rename branch) against the v3 TSV produces NO singleton-prefix rows that match any of the pre-rename singletons (Candidates 4, 5 should no longer be singleton-prefixed).

**Behavior tests for the doc updates:**

- Test (or grep-check in CI) that `compendium/NAMING_CONVENTIONS.md` §10 marks each accepted candidate as **DONE** and that the body cross-refs use the new names.
- Test that the §10 Issue 2 header reads "(6 rows)" not "(5 rows)".
- Test that `compendium/README.md` references `cpi_2015_c11_projection_mapping.md` and does NOT reference `cpi_2015_projection_mapping.md`.

NOTE: I will write *all* tests before I add any implementation behavior.

---

## 4. Execution steps (bite-sized, sequenced)

This is a small but high-coordination change. The sequence prioritizes (a) verifying sister-branch state before cutting the branch, (b) test-first inside the rename branch, (c) one atomic commit for the rename itself, (d) regen the audit artifacts as a separate commit.

### Phase 0 — Pre-execution coordination check

0.1. Verify sister-branch state. From the main worktree:
   ```
   git -C <repo> fetch origin
   git -C <repo> log --oneline origin/extraction-harness-brainstorm -10
   git -C <repo> log --oneline origin/phase-c-projection-tdd -10
   git -C <repo> log --oneline origin/oh-statute-retrieval -10
   ```
0.2. Grep the three sister branches for any of the 15 old row IDs. Use:
   ```
   git -C <repo> grep -l '<old_row_id>' origin/extraction-harness-brainstorm
   ```
   for each of the 15 old names, against each of the 3 sister branches. Tabulate any hits.
0.3. If any sister branch references an old row ID in code (`*.py`) or prompt strings — pause. Brief the branch owner. Do not proceed until coordination is resolved.
0.4. If sister branches only reference old names in markdown narrative — proceed; markdown can be patched in a follow-up PR.

### Phase 1 — Cut the rename branch

1.1. From main, cut a new branch `compendium-row-renames-v3` (or per-convention name). Use the `use-worktree` skill — include the `data/` symlink.
1.2. Seed `docs/active/compendium-row-renames-v3/` with `RESEARCH_LOG.md`, `convos/`, `plans/`, `results/`. The originating convo for the new branch is this plan plus the convo it references; mirror those into `RESEARCH_LOG.md` as predecessor pointers.

### Phase 2 — Write tests (test-first)

2.1. Locate the test layout for `tools/` — check whether `tools/test_*.py` is the convention or whether tests live elsewhere. Match existing convention.
2.2. Write all behavior tests from §3 against the **unchanged** `tools/freeze_canonicalize_rows.py`. Tests should FAIL initially since the rename dict doesn't exist yet.
2.3. Run the test suite. Verify the tests fail for the right reason (V2_TO_V3_RENAMES doesn't exist / produces empty mapping / etc.).
2.4. Commit: "tests: v2→v3 row-ID rename behavior tests (initially failing)".

### Phase 3 — Implement the rename machinery

3.1. Extend `tools/freeze_canonicalize_rows.py` with `V2_TO_V3_RENAMES = {...}` — a dict of 15 (old, new) pairs in the order they appear in §1 of this plan. Include a short header comment naming the originating decisions (D-style: D31 = Candidate 1, D32 = Candidate 2 cluster, etc., or use a flat list with this plan as the reference).
3.2. Add a `--target-version=v3` flag (or per-existing-convention) that:
   - Reads `compendium/disclosure_side_compendium_items_v2.tsv`
   - Applies `V2_TO_V3_RENAMES` to `compendium_row_id` only
   - Writes `compendium/disclosure_side_compendium_items_v3.tsv`
3.3. Run the test suite. All tests should now PASS.
3.4. Commit: "compendium: v2→v3 row-ID rename — 15 renames across 8 §10 candidates".

### Phase 4 — Doc updates

4.1. Update `compendium/NAMING_CONVENTIONS.md`:
   - Mark each §10 Issue (1–7) as **DONE — applied YYYY-MM-DD in branch `compendium-row-renames-v3`** (use actual branch name and date)
   - Update §10 Issue 8 to mark the README typo fix as **DONE**
   - Update body cross-references in §§2, 3, 4, 5, 7 (prefix family listings) to use the new names — re-running the prefix-survey script will tell you which sections need updates
   - Add a §10.1 "Resolver table for archive readers" that lists the 15 old→new pairs verbatim, so anyone reading `docs/historical/compendium-source-extracts/results/projections/*.md` can resolve old names to new
   - (Note: §10 Issue 2 header "5 rows" → "6 rows" was already fixed in the audit branch — no action.)
4.2. Update `compendium/README.md`: fix the `cpi_2015_projection_mapping.md` filename to `cpi_2015_c11_projection_mapping.md`.
4.3. Commit: "compendium: doc updates for v3 rename — §10 marked DONE, resolver table added, README typo fixed".

### Phase 5 — Regen the audit artifacts

5.1. Copy or re-locate the prefix-survey and provenance-table scripts. Either:
   - Reference the existing scripts at `docs/active/compendium-naming-docs/results/20260514_prefix_survey.py` and `20260514_provenance_table.py` and run them against the v3 TSV, OR
   - Copy them into `docs/active/compendium-row-renames-v3/results/` with a new date prefix and run there
5.2. Diff the regenerated `.md` outputs against the existing 2026-05-14 outputs. The expected delta: Candidates 4 and 5 no longer singleton-prefixed; Candidates 6 and 7 now joining their target families; Candidates 1, 2, and 3 showing new family memberships.
5.3. Commit: "results: prefix-survey + provenance-table regen against v3 TSV".

### Phase 6 — Canonical swap (immediate, no transition window)

6.1. **Swap is immediate.** Once Phase 5 lands, v3 replaces v2 as canonical in the same execution branch. Sister branches absorb on their next merge — that's the explicit coordination model and Phase 0 has already verified they can.
6.2. Move the v2 TSV to `compendium/_deprecated/v2/disclosure_side_compendium_items_v2.tsv` (mirroring the v1 deprecation pattern from `compendium-v2-promote`'s merge commit `0a6804f`).
6.3. Rename `compendium/disclosure_side_compendium_items_v3.tsv` → `compendium/disclosure_side_compendium_items_v2.tsv` if we want the filename stable across versions, OR keep `_v3` in the filename if we want the version visible at the path level. **Recommended:** keep `_v3` in the filename — the version-in-path convention is already established by `_v2.tsv` and the v1 deprecation. Update `compendium/README.md` and `compendium/_deprecated/README.md` (if it exists) to reflect.
6.4. Update tooling that reads the v2 TSV to point at v3. Pre-scan: `src/lobby_analysis/compendium_loader.py` is the obvious consumer; grep for `disclosure_side_compendium_items_v2` repo-wide and update each hit. Add a behavior test that confirms `compendium_loader.py` reads the v3 TSV without error and returns the expected row count (181).
6.5. Commit: "compendium: swap v3 to canonical, deprecate v2 to `_deprecated/v2/`".

### Phase 7 — Finish-convo, push, brief sister branches

7.1. Run the finish-convo skill for the rename branch.
7.2. Push to origin.
7.3. Brief sister-branch owners (`extraction-harness-brainstorm`, `phase-c-projection-tdd`, `oh-statute-retrieval`) about the rename and link this plan + the resolver table.

---

## 5. Edge cases and risk surface

**E1. A sister branch silently absorbs an old row ID before execution.** If `extraction-harness-brainstorm`'s Pydantic models or `phase-c-projection-tdd`'s projection functions hard-code an old name and the branch owner doesn't know about this plan, the rename will look like a breaking change after the fact. Mitigation: Phase 0 grep across sister branches before cutting. If hits found, brief owners.

**E2. The `_threshold_<measure>_<unit>` suffix shape (C3) is canonical, not drift.** Resolution (sub-3, 2026-05-14): the rule is "include the unit suffix when `cell_type` is a typed numeric; include the measure word when the row family contains multiple measures, omit it when there's only one." `lobbyist_filing_de_minimis_threshold_dollars` (single-measure case) follows `_threshold_<unit>`. C3's `lobbyist_registration_threshold_compensation_dollars` etc. (three-measure case) follows `_threshold_<measure>_<unit>`. Both are consistent with the `_threshold_*_dollars` / `_threshold_time_percent` rows in NAMING_CONVENTIONS.md §9. The earlier "drift" framing was wrong: C3 *fixes* drift in the current names (`compensation_threshold_for_lobbyist_registration` doesn't follow the §9 shape); it does not introduce new drift. NAMING_CONVENTIONS.md §7 was updated in sub-3 to encode this rule explicitly. Execute as specified in §1 Candidate 3 — no execution-time re-litigation.

**E3. The §10 Issue 2 header inconsistency (5 vs 6 rows) was fixed in the audit branch alongside this plan.** No action required on the rename-execution branch.

**E4. Historical projection-mapping docs reference old names.** They are immutable archives. The resolver table in §10.1 (new) is the contract for archive readers. Do not edit the archives even if a stray `lobbyist_report_includes_*` reference is jarring.

**E5. The audit results files (`20260514_prefix_survey.md`, `20260514_provenance_table.md`) were generated against v2.** They stay as-is (provenance). Regen against v3 produces new files with new dates in the rename branch, not overwrites.

**E6. Row count drift.** The plan asserts 181 rows in / 181 rows out. Any row count change is a bug, not a feature. The test in §3 enforces this.

**E7. The provenance column inside the TSV may reference old row IDs in narrative text.** Check at execution: if a row's `provenance` cell mentions an old row ID (e.g., "merged from lobbyist_report_includes_x" referencing a Candidate 2 row), update those narrative strings too. The behavior test in §3 should be tightened to check `compendium_row_id` *and* `provenance` columns for old-name appearances.

---

## 6. What could change

- **Sister-branch timing.** If `extraction-harness-brainstorm` adopts old row IDs in Pydantic enums before execution, the rename branch needs a coordinated dual-update. Worst case: defer execution further.
- **Candidate 2 LV-1.** If during execution we discover that LV-1 is heavily referenced in `extraction-harness-brainstorm`'s schema-coverage Pydantic work, the `lobbyist_filing_*` decision might trigger a small re-litigation. The walkthrough decision stands; just flag if friction appears.
- **Candidate 3 high-traffic concern.** If the trio rename produces an outsized merge cost on a sister branch, partial accept (defer `compensation_threshold` only) is the documented fallback from the walkthrough.
- **Resolver-table format.** §10.1 might prefer to be a separate file (`compendium/V2_TO_V3_RENAME_TABLE.md`) rather than a NAMING_CONVENTIONS subsection if it grows or if other readers want to import it. Decide at execution.

---

## 7. Questions for execution-time

- Is `compendium-row-renames-v3` the right branch name, or does Dan prefer a different convention? (Default: ask at branch-cut time.)
- Should D-numbering continue (D31, D32, ...) for the renames, or is the §10 candidate numbering sufficient as the reference?
- Where is the test layout for `tools/`? (Check `tests/` at execution; match existing convention.)
- Are there prompt strings already in flight (`extraction-harness-brainstorm` or elsewhere) that need a coordinated update PR alongside the rename branch?
- For Phase 6.3: keep `_v3` visible in the canonical filename, or drop the version suffix and let `_deprecated/v2/` carry the history? (Plan recommends keeping `_v3`; flag at execution if filename-stability matters more than version-visibility.)

---

**Testing Details:** Pure data-transformation tests against `tools/freeze_canonicalize_rows.py`'s extended rename machinery. Tests verify (a) row count invariance (181 in, 181 out), (b) every old name absent from v3, (c) every new name present in v3, (d) non-ID columns byte-identical, (e) LV-1 categorical exception preserved, (f) Candidate 3 unit suffixes correct, (g) §10 doc-state assertions. No mocks. Tests act on real TSV reads/writes.

**Implementation Details:**
- Single Python module change: `tools/freeze_canonicalize_rows.py` gains `V2_TO_V3_RENAMES` dict and a `--target-version=v3` code path
- Same csv/pathlib stdlib stack as the existing v1→v2 machinery — no new deps
- Doc updates in `compendium/NAMING_CONVENTIONS.md`, `compendium/README.md`
- Audit-artifact regen via existing re-runnable scripts under `docs/active/compendium-naming-docs/results/`
- Resolver table at §10.1 of NAMING_CONVENTIONS (or sibling file if it grows)
- Historical projection-mapping docs in `docs/historical/compendium-source-extracts/results/projections/` are NOT edited
- Phase-0 sister-branch grep is non-negotiable — it's the difference between a clean rename and a coordination headache after the fact

**What could change:** see §6.

**Questions:** see §7.

---
