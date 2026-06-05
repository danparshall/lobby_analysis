# 2026-06-05 — Pattern C row split v2.1 execution: BinaryCell additive-pattern confirmed (6/6 on `_defined_in_law`), 4-cell-type matrix closes

**Plan:** [`../plans/20260605_pattern_c_row_split_v2_1.md`](../plans/20260605_pattern_c_row_split_v2_1.md) (incl. mid-session "Expanded Step 2c" addendum capturing the 5 production + 7 test touchpoints discovered after the original plan was written)
**Originating convo:** [`20260604_phase_b_silent_unit_mismatch_sweep.md`](20260604_phase_b_silent_unit_mismatch_sweep.md) §"Post-session refinement"

## Pre-flight

Read in order: STATUS.md, README.md, RESEARCH_LOG.md (this branch), plan doc end-to-end, iter-5 convo §"Post-session refinement", CPI 2015 projection mapping doc §IND_207/IND_208/IND_209, `compendium/NAMING_CONVENTIONS.md` end-to-end, existing `source_quotes.yaml` entries for the two target rows. Clean pre-flight: no surprises in trajectory; plan was self-contained for cold pickup; 2 open scoping questions surfaced as expected.

## Decisions confirmed with Dan

1. **Naming for the new practical-axis row** (open scoping Q (a) in the plan): **`lobbying_disclosure_audit_required_in_practice`** — the "inverse-fix symmetric" choice that mirrors `_audit_required_in_law`. *Not* `_audit_conducted_in_practice` as the plan defaulted (which would have paralleled `_penalties_imposed_in_practice`'s past-participle-action verb).
2. **v2.1 pointer scope** (open scoping Q (b)): **branch-local** (plan default). v2.1 visible only on `wi-ralph-cpi-renewal-cadence`; other branches stay on v2 until BinaryCell test confirms the structural fix.
3. **(Surfaced mid-session)** Plan's Step 2c undercounted: the dispatcher reads via `build_cell_spec_registry()` + `build_chunks()` (which enforces a hard partition invariant). v2.1 swap cascades into chunks manifest + CPI projection + 4 (later 7) tests. Surfaced 4 options to Dan; Dan picked **(1) charge through: full v2.1 swap on this branch**. Dan also asked "you ARE writing a plan and using Nori / TDD right?" — caught me about to start editing without first patching the plan to reflect expanded scope. Walked back, wrote the plan addendum, read `skills/test-driven-development/SKILL.md`, then executed RED → GREEN per skill.

## What happened (chronological)

### Phase 0 — discovery + planning

1. Pre-flight reads (per CLAUDE.md session protocol).
2. Confirmed 2 open scoping questions with Dan.
3. Started Step 2c, discovered the plan's literal "tier_1_direct_read_legal_axis.py pointer update" was underspecified for the actual code structure (dispatcher accesses via `build_cell_spec_registry()` + `build_chunks()`; manifest + CPI projection + 4 tests cascade).
4. Surfaced 4 options to Dan + recommendation; Dan picked (1) charge through.
5. Started editing TSV directly; Dan caught me skipping the plan-update step. Reverted in-progress edits.
6. Wrote a substantial plan addendum at `plans/20260605_pattern_c_row_split_v2_1.md` §"Expanded Step 2c — discovered scope" capturing Dan's 3 decisions, 5 production touchpoints, 6 test touchpoints (later patched to 7), and TDD execution order. Read TDD skill.

### Phase 1 — RED batch (test edits expressing v2.1 contract)

1. `tests/test_models_v2_cell_spec.py:66-72` — `combined_row_ids` set shrunk 5 → 3.
2. `tests/test_models_v2_cell_spec.py:118-132` — `@parametrize` cases shrunk 5 → 3.
3. `tests/test_chunks_build.py:17-23` — `COMBINED_AXIS_ROWS` tuple shrunk 5 → 3.
4. `tests/projections/test_cpi_2015_c11_per_item.py:389` — IND_208 fixture row → `_audit_required_in_practice`.
5. `tests/projections/test_cpi_2015_c11_per_item.py:428` — `_DE_FACTO_PASSTHROUGH_ITEMS["IND_208"]` row → `_audit_required_in_practice`.
6. `tests/projections/test_cpi_2015_c11_aggregation.py:261-264` — synthesizer split into `_audit_required_in_law: {legal_availability}` + `_audit_required_in_practice: {practical_availability}`.
7. **Added explicit-contract RED test** at `tests/test_models_v2_cell_spec.py::test_v2_1_pattern_c_split_rows_present_and_wrong_axes_removed` asserting the new sibling rows present at correct axes AND the wrong-axis halves removed from the old rows. Mid-step realization: the shrunken `combined_row_ids` set passed in v2.0 (less-strict subset assertion), so without this explicit-contract test the RED batch wouldn't truly test the schema contract. Added per TDD skill's "Test passes immediately = testing existing behavior, fix test."

Ran pytest on the 4 affected files: **8 IND_208-related failures** (real RED — projection still reads old row name; fixtures pass new name) **+ 1 new explicit-schema failure** (missing `_defined_in_law` row in v2.0 registry). RED verified for the right reasons.

### Phase 2 — GREEN batch (production changes)

1. `compendium/disclosure_side_compendium_items_v2.1.tsv` created — 184 lines (1 header + 183 data rows), 4 row-level edits as planned. Cell count unchanged at 186.
2. `compendium/source_quotes.yaml` — added 2 new entries: `_defined_in_law` (with HG Q41 + Q42 source quotes + initial BinaryCell prompt) and `_audit_required_in_practice` (with CPI IND_208 source quote, practical-axis-only — populated for completeness even though legal-axis pipeline won't dispatch it).
3. `src/lobby_analysis/compendium_loader.py:30` — `DEFAULT_COMPENDIUM_V2_TSV` swapped to `_v2.1.tsv`.
4. `src/lobby_analysis/chunks_v2/manifest.py:243-258` — `enforcement_and_audits` `ChunkDef.member_row_ids` extended 2 → 4 rows; `notes` updated.
5. `src/lobby_analysis/projections/cpi_2015_c11.py:285-292` — `project_ind_208` lookup flipped from `_audit_required_in_law` → `_audit_required_in_practice`.

Pytest on the 4 affected files: **95/95 green**. Full pytest suite: **1683 pass, 3 skip, 3 xfail, 1 fail** (`test_load_v2_compendium_returns_181_rows` — the 7th test touchpoint discovered by the full sweep; `EXPECTED_V2_ROW_COUNT` constant pinned 181 to v2's row count). Updated to 183 with rename to `test_load_v2_compendium_returns_expected_row_count`. Full suite: **1683/1683 green** (3 skip, 3 xfail baseline).

### Phase 3 — dispatch + audit

1. First dispatch attempt — env vars not exported. Switched to `uv run --env-file .env.local`.
2. Second dispatch attempt — `skipped(resumed)=6, session_cost=$0.0000`. Old wide-pass checkpoint JSONs from the wi-tier1 merge prevented re-dispatch. Archived 6 JSONs to `_pre_v2_1_pattern_c_enforcement/` with SUPERSEDED.md banner (per "prefer mv over rm for research artifacts" memory).
3. Third dispatch (first real run) — **6/6 errors:** `BinaryCell: cannot coerce 'yes' to bool`. Diagnosed via JSON inspection: both Claude (3/3) and GPT (3/3) correctly emitted `'yes'` for WI per §13.69, but the dispatcher's `_instantiate_cell` accepts only `'true'`/`'false'` strings for BinaryCell. **The iter-5 playbook's "cell-type instantiation failure" branch landed literally.** Cost: $0.171.
4. Archived the 6 yes/no-prompt JSONs to `_pre_v2_1_binarycell_vocab_fix/` with SUPERSEDED.md banner documenting the negative-result evidence.
5. Updated `_defined_in_law` YAML prompt: `'yes'/'no'` → `true`/`false` (cell-type-aligned vocabulary per the additive pattern).
6. Fourth dispatch — **6/6 success**, all `cells=2 errors=0`. Cost: $0.155.

**Convergence audit on `_defined_in_law` (BinaryCell, the test target):**

| Run | Claude `_defined_in_law` | GPT `_defined_in_law` |
|---|---|---|
| run1 | True (high) | True (high) |
| run2 | True (high) | True (high) |
| run3 | True (high) | True (high) |

**6/6 converge on `True` at high confidence.** Justifications cite WI §13.69 forfeitures + §13.69(7) Class H felony for false statements. The de-jure pair the projection mapping doc said should exist now reads cleanly.

**Secondary observation on `_audit_required_in_law` (EnumCell, NOT prompt-updated this session):**

| Run | Claude `_audit_required_in_law` | GPT `_audit_required_in_law` |
|---|---|---|
| run1 | MODERATE (medium) | MODERATE (high) |
| run2 | MODERATE (medium) | MODERATE (high) |
| run3 | YES (high) | MODERATE (high) |

Claude run3 flipped to YES — first observation of this row drifting. Plausibly within sampling noise on a borderline case (§13.685(3) compliance examination by the Ethics Commission can be read as either compliance-review = MODERATE or impartial-third-party-audit = YES). Row's prompt was NOT updated this session (still uses raw CPI source quote, no additive cell-type-aligned instruction). Value-stability for this row would require an additive-pattern iter; flagged as a next-session candidate.

## Findings (load-bearing)

### 1. BinaryCell additive pattern confirmed; 4-cell-type matrix closes structurally

The cell-type-aligned vocabulary for BinaryCell is `true`/`false`, NOT the rubric-conventional `yes`/`no`. Initial prompt used `'yes'/'no'` → 6/6 `instantiation_failed` with `ValueError("BinaryCell: cannot coerce 'yes' to bool")`. After flipping prompt to `true`/`false` (matching the dispatcher's coercion table at `scripts/tier_0_direct_read_smoke.py:476-482`), 6/6 convergence on `True` at high confidence. **The additive cell-type-aligned-instruction pattern is now confirmed across the 4-cell-type matrix:**

| Cell type | Iter | Convergence |
|---|---|---|
| IntCell | iter 1+2 (`renewal_cadence`) | 6/6 on 24 at high confidence |
| EnumCell | iter 3+4 (`filing_cadence`) | 6/6 on `'none'` at high confidence |
| DecimalCell-Optional | iter 5 (`compensation_threshold`) | 6/6 on `'0'` at high confidence |
| DecimalCell-non-negative | iter 5 spillover | 3/3 instantiate (value-stability not validated) |
| BinaryCell | this session (`_defined_in_law`) | 6/6 on `True` at high confidence |

This is the **Phase A pre-flight YAML audit's per-cell-type template set**. Five cell-type-aligned vocabulary templates:

- **IntCell:** `"Answer as an integer (e.g., 24 for 24 months)"`.
- **EnumCell:** `"Answer with one of: {value1}, {value2}, ..., or {valueN}"` + descriptive each-value-use guidance.
- **DecimalCell-Optional:** `"Answer with the dollar amount as a non-negative decimal (e.g., 500 for $500). Use 0 if [no threshold]. Use null if [no statute exists]."`.
- **DecimalCell-non-negative:** same as above minus the null branch.
- **BinaryCell:** `"Answer with the boolean value true or false."` — NOT 'yes'/'no'.

Phase A scope is now well-defined.

### 2. Cell-type-vocabulary mismatch is a real silent-failure class

Until this session, the silent-unit-mismatch sweep found 1 mismatch class instance (IND_197 GPT emitting CPI tier value as DecimalCell value). This session reveals a sibling class: **prompt vocabulary mismatch with the cell's instantiation coercion table.** The dispatcher's `_instantiate_cell` is permissive about JSON-shape (accepts strings for numeric fields, coerces) but strict about vocabulary (BinaryCell wants only `'true'`/`'false'`; doesn't accept `'yes'`/`'no'`/`'Yes'`/`'Y'`/etc.). The Phase A audit needs to check both: (a) silent-unit-mismatch on numeric cells, AND (b) cell-type-vocabulary mismatch on enumerable cells (BinaryCell, EnumCell).

### 3. Pattern C row split is structurally clean

v2.1 TSV: 183 data rows, 186 cells (unchanged from v2 — splits are cell-count-neutral). All 1683 tests green. `enforcement_and_audits` chunk dispatches without registry/manifest errors. Both new sibling rows (`_defined_in_law`, `_audit_required_in_practice`) parse to their intended cell classes (BinaryCell, GradedIntCell). The de-jure pair CPI 2015 IND_209's projection mapping doc said should exist now reads `True` for WI 2025 with high cross-model agreement.

### 4. `_audit_required_in_law` Claude drift to YES is the third iter-5 errata candidate's first sampling-time variation

Iter-5 sweep flagged IND_207 as CPI errata candidate (CPI says YES, 6/6 wide-pass models said MODERATE). This session, Claude flips to YES on 1 of 3 runs (justification: §13.685(3) Ethics Commission examination is impartial-third-party-audit). The row's prompt was NOT updated this session (still raw CPI source quote, no additive treatment). Value-stability for this row is a candidate next-session target.

### 5. The doc-graph discipline survived a near-miss

Dan's mid-session question caught me about to edit code before updating the plan. Per the "doc system is persistent memory, not patchwork" memory entry, end-of-session commits must land the link graph self-consistent. Walking back to update the plan first cost ~10 min and added discipline to the rest of the session — the 7th test-touchpoint discovery later in execution was also patched into the plan addendum BEFORE the code commit, not after. The graph stays coherent.

## Cost ledger

| Item | Cost |
|---|---|
| Plan addendum + TDD skill read + RED batch + GREEN batch | $0 (no API) |
| Test fixes + full pytest sweep | $0 |
| First dispatch (yes/no prompt, all errored — negative-result evidence) | $0.1710 |
| Re-dispatch (true/false prompt, 6/6 success) | $0.1554 |
| **This session subtotal** | **$0.3264** |
| **wi-ralph cumulative** | **$2.6837** (against $3-5 ceiling; $0.32-$2.32 remaining) |
| wi-tier1-direct-read cumulative | $7.2946 (unchanged) |
| **Grand total WI Phase 1/2 + Phase B** | **$9.9783** |

Slightly over original $0.30 projection by ~$0.026 due to the buggy-prompt first dispatch — well within budget tolerance.

## Artifacts produced

- **Plan addendum:** [`../plans/20260605_pattern_c_row_split_v2_1.md`](../plans/20260605_pattern_c_row_split_v2_1.md) §"Expanded Step 2c — discovered scope" (3 decisions + 5 production + 7 test touchpoints + TDD execution order + rollback policy + revised cost projection).
- **v2.1 compendium:** [`../../../../compendium/disclosure_side_compendium_items_v2.1.tsv`](../../../../compendium/disclosure_side_compendium_items_v2.1.tsv) (183 data rows, 186 cells; v2.tsv preserved unchanged as historical reference).
- **YAML additions:** [`../../../../compendium/source_quotes.yaml`](../../../../compendium/source_quotes.yaml) — 2 new entries (`_defined_in_law` with `true`/`false` BinaryCell additive prompt; `_audit_required_in_practice` with CPI IND_208 source quote).
- **Production code edits:** `src/lobby_analysis/compendium_loader.py:30`, `src/lobby_analysis/chunks_v2/manifest.py:243-258`, `src/lobby_analysis/projections/cpi_2015_c11.py:285-292`.
- **Test edits:** 7 touchpoints across `tests/test_models_v2_cell_spec.py`, `tests/test_chunks_build.py`, `tests/projections/test_cpi_2015_c11_per_item.py`, `tests/projections/test_cpi_2015_c11_aggregation.py`, `tests/test_compendium_loader_v2.py`. Plus 1 new explicit-schema-contract test (`test_v2_1_pattern_c_split_rows_present_and_wrong_axes_removed`).
- **Dispatch results (live):** `docs/active/wi-tier1-direct-read/results/tier_1/WI_2025/{claude-opus-4-7,gpt-5.2-2025-12-11}__enforcement_and_audits__run{1,2,3}.json` (6 JSONs; all cells=2 errors=0; 6/6 `_defined_in_law=True` at high confidence).
- **Archived dispatch results (negative-result evidence):**
  - `docs/active/wi-tier1-direct-read/results/tier_1/WI_2025/_pre_v2_1_pattern_c_enforcement/` (6 JSONs from wi-tier1 wide-pass + SUPERSEDED.md).
  - `docs/active/wi-tier1-direct-read/results/tier_1/WI_2025/_pre_v2_1_binarycell_vocab_fix/` (6 JSONs from yes/no-prompt dispatch + SUPERSEDED.md documenting the cell-type-vocabulary mismatch finding).

## Open questions / next-session candidates

1. **Phase A pre-flight YAML audit at scale** (candidate (iv) from iter-5 RESEARCH_LOG entry). Now well-positioned: 4-cell-type matrix structurally complete + 5 cell-type-aligned-vocabulary templates documented (incl. BinaryCell `true`/`false`) + ~21 CPI-readable rows already swept (16 cleared, 1 silent-unit-mismatch fixed, 2 CPI errata candidates queued) + chunk-mate spillover known design constraint. Phase A is the next obvious move.
2. **Value-stability test on `_audit_required_in_law`** with additive cell-type-aligned EnumCell instruction (does Claude run3 YES persist? Does GPT also drift? Does CPI errata status change from "candidate" to "documented"?). ~$0.15 if dispatched on `enforcement_and_audits` chunk alone.
3. **Value-stability test on `lobbyist_filing_itemization_de_minimis_threshold_dollars`** ($200 vs $500 ambiguity carried forward from iter-5).
4. **Propagate v2.1 to main + other branches.** Now that structural fix is dispatch-confirmed, the branch-local scope can lift. Other branches (wi-tier1-direct-read, etc.) still see v2; merging this branch to main would propagate v2.1 to them on their next merge. Dan's call on timing.
5. **Chunk-mate spillover mechanism investigation** (candidate (iii) from iter-5).

Dan's call on which to pick.

## Session meta — the discipline cost

Dan's mid-session "you ARE writing a plan and using Nori / TDD right?" question caught the protocol drift early. The plan-update + TDD-skill-read added ~15 min of overhead before any test/code edit. The discipline paid off twice:

- The added explicit-schema test (`test_v2_1_pattern_c_split_rows_present_and_wrong_axes_removed`) caught a subtle RED-batch weakness: the shrunken `combined_row_ids` set passed against v2.0 because subset-assertions of true statements stay true. Without the explicit test, the RED batch wouldn't have demonstrated the v2.1 contract.
- The 7th test-touchpoint discovery (`test_load_v2_compendium_returns_181_rows`) was caught BEFORE the commit by running the full suite, and patched into the plan addendum (raising touchpoint count 6 → 7) BEFORE the code commit. The link graph stayed self-consistent.

The TDD skill's "If you have more than one test that you need to write, you should write all of them before moving to the GREEN phase" mapped cleanly to a research-code session: batch all test edits → verify RED → batch all production edits → verify GREEN. The full-suite run after the targeted-4-file green was load-bearing — it caught the row-count test that wasn't in my enumerated list.
