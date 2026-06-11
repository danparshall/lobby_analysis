# Pattern C row split → compendium v2.1 schema bump + parallel inverse fix + BinaryCell dispatch

**Date drafted:** 2026-06-05
**Branch:** wi-ralph-cpi-renewal-cadence
**Originating convo:** [`../convos/20260604_phase_b_silent_unit_mismatch_sweep.md`](../convos/20260604_phase_b_silent_unit_mismatch_sweep.md) §"Post-session refinement"
**Step 1 status:** ✅ DONE this session (Pattern C audit; see findings below)
**This session's convo:** [`../convos/20260605_pattern_c_audit_and_plan.md`](../convos/20260605_pattern_c_audit_and_plan.md)

---

## What's already done (this session)

**Step 1 — Pattern C audit on v2 TSV (182 rows).** No API cost. Findings:

| Row | Cell types | Severity | Disposition |
|---|---|---|---|
| `lobbying_violation_penalties_imposed_in_practice` (v2 line 72) | `binary (legal) + typed int 0-100 step 25 (practical)` | **Egregious** — practical-semantic name; legal-axis cell is a category error ("in law, are penalties imposed in practice?") | Fix this session |
| `lobbying_disclosure_audit_required_in_law` (v2 line 49) | `enum (legal) + typed int 0-100 step 25 (practical)` | **Inverse / less egregious** — legal name matches legal cell; practical cell mis-keyed by name | Fix this session (Dan's call) |

Other 3 `legal+practical` rows (`lobbyist_registration_required`, `lobbyist_spending_report_filing_cadence`, `lobbyist_registration_deadline_days_after_first_lobbying`) have neutral names — dual-axis split is semantically coherent. **Not bugs.**

## Dan's scoping decisions (2026-06-05)

1. **v2.1 schema bump.** New file `compendium/disclosure_side_compendium_items_v2.1.tsv`; v2 stays frozen as the prior reference. Cleaner historical record. wi-tier1-direct-read consumers will need a pointer update (flag in handoff).
2. **Fix the inverse `_audit_required_in_law` in parallel this session.** Net +2 rows (182 → 184).

## Next-session execution plan

### Pre-flight reads (4 docs)

1. This plan + originating convo §"Post-session refinement" (lines 102-118 of the iter-5 convo).
2. **CPI 2015 projection mapping doc** — `docs/historical/compendium-source-extracts/results/projections/cpi_2015_c11_projection_mapping.md` §IND_207 (audit_required) + §IND_209 (penalties_imposed). Confirms the de-jure pair was deferred from compendium and HG Q41/Q42 reference for `rubrics_reading`.
3. **NAMING_CONVENTIONS.md** + **README.md** in `compendium/` — confirm row-id and cell-type conventions before adding new rows.
4. **`compendium/source_quotes.yaml`** — find the existing entries for `lobbying_violation_penalties_imposed_in_practice` and `lobbying_disclosure_audit_required_in_law` to confirm axis-tagging conventions and source-quote provenance to preserve.

### Step 2a — v2.1 TSV creation (no API cost)

Copy `disclosure_side_compendium_items_v2.tsv` → `disclosure_side_compendium_items_v2.1.tsv` and apply 4 changes:

**Pattern C egregious fix** (around line 72):
- **Edit existing row** `lobbying_violation_penalties_imposed_in_practice`:
  - `cell_type`: `binary (legal) + typed int 0-100 step 25 (practical)` → `typed int 0-100 step 25 (practical)`
  - `axis`: `legal+practical` → `practical`
  - `notes`: append `; legal axis split to _defined_in_law in v2.1 (Pattern C fix)`
- **Add new row** `lobbying_violation_penalties_defined_in_law` (insert adjacent):
  - `cell_type`: `binary`
  - `axis`: `legal`
  - `rubrics_reading`: `cpi_2015;hg_2007` (per projection doc HG Q41/Q42 reference — verify in pre-flight)
  - `n_rubrics`: `2`
  - `first_introduced_by`: `cpi_2015_c11_projection_mapping.md`
  - `status`: `firm`
  - `notes`: `Pattern C split in v2.1 from _imposed_in_practice legal axis; de-jure pair the projection mapping doc explicitly said should exist`

**Inverse fix** (around line 49):
- **Edit existing row** `lobbying_disclosure_audit_required_in_law`:
  - `cell_type`: `enum (legal) + typed int 0-100 step 25 (practical)` → `enum (legal)`
  - `axis`: `legal+practical` → `legal`
  - `notes`: append `; practical axis split to _audit_conducted_in_practice in v2.1 (Pattern C inverse fix)`
- **Add new row** `lobbying_disclosure_audit_conducted_in_practice` (insert adjacent; **name TBD — confirm with Dan**, options: `_audit_conducted_in_practice` vs `_audit_required_in_practice`; the convo argued the former since it parallels `_penalties_imposed_in_practice`):
  - `cell_type`: `typed int 0-100 step 25`
  - `axis`: `practical`
  - `rubrics_reading`: `cpi_2015`
  - `n_rubrics`: `1`
  - `first_introduced_by`: `cpi_2015_c11_projection_mapping.md`
  - `status`: `firm`
  - `notes`: `Pattern C inverse split in v2.1 from _audit_required_in_law practical axis`

Net: 182 → 184 rows.

### Step 2b — YAML population for new rows

In `compendium/source_quotes.yaml`, add entries for:
- `lobbying_violation_penalties_defined_in_law` (BinaryCell, legal axis) — apply the additive BinaryCell pattern. Concrete template (per iter 5 §Decisions):
  > "Under state law, are penalties defined for lobbying disclosure violations? Answer with 'yes' or 'no'. Use 'yes' if any statute prescribes a penalty (civil fine, criminal, administrative sanction) for failure to register, failure to file, or filing a false report. Use 'no' only if no such statutory penalty exists."
  - Preserve CPI source quote at front (from existing `_imposed_in_practice` YAML entry, if axis-tagged for legal).
- `lobbying_disclosure_audit_conducted_in_practice` (practical typed int, NOT dispatched by legal-axis pipeline) — populate for completeness even though this session won't test it via dispatch. Leave a banner that the practical-axis pipeline does not exist yet.

Also **revise existing YAML entries**:
- `lobbying_violation_penalties_imposed_in_practice` — remove the legal-axis prompt (now structurally absent); keep only the practical-axis content.
- `lobbying_disclosure_audit_required_in_law` — remove the practical-axis prompt; keep only the legal-axis enum content.

### Step 2c — Pointer updates for downstream consumers

- **`scripts/tier_1_direct_read_legal_axis.py`** — find the TSV loader; update path from `_v2.tsv` to `_v2.1.tsv`. **Confirm wi-tier1-direct-read branch is on the same v2.1 pointer before dispatching**, OR scope the v2.1 pointer to this branch only and merge later.
- **`scripts/silent_unit_mismatch_sweep.py`** — same pointer update; rerun once cells re-populate (optional follow-up).
- Search for other consumers via `grep -rn "disclosure_side_compendium_items_v2" .`

### Step 3 — Dispatch BinaryCell additive pattern test

After Step 2 lands:

```
python scripts/tier_1_direct_read_legal_axis.py --state WI --vintage 2025 --chunks enforcement_and_audits
```

Expected: ~$0.30. New `_defined_in_law` row dispatches as BinaryCell legal axis; 6/6 convergence at high confidence citing WI §13.69 (penalties) and/or §13.62 violations sections.

**Audit:**
- 6/6 on `_defined_in_law` value? (expect `'yes'` per §13.69 forfeitures + §13.69(7) criminal penalty).
- Chunk-mate spillover on other `enforcement_and_audits` rows (the iter 5 spillover finding suggests we should expect some).
- Pre-existing `_imposed_in_practice` row's practical axis still NOT_EMITTED (legal-axis pipeline doesn't reach it) — verify in audit, not a regression.

**Stopping conditions:** convergence → finish-convo; non-convergence → diagnose (silent unit-mismatch? cell-type instantiation failure? something new?).

## Cost projection

- Step 2 (TSV + YAML): $0 (no API).
- Step 3 (1 chunk dispatch): ~$0.30.
- **Session total budget: $0.30.** wi-ralph cumulative after = $2.6573. Stays within the $3-5 ceiling.

## Open scoping question for implementing agent

1. **`_audit_conducted_in_practice` vs `_audit_required_in_practice`**: which name? Convo argued the former (parallels `_penalties_imposed_in_practice`); the inverse-fix could equally read "audits are required by law" / "audits are conducted in practice." Confirm with Dan before adding the row.
2. **v2.1 pointer scope**: does the v2.1 schema bump propagate to main / other branches, or stay scoped to this branch until Dan greenlights? Default: scope to this branch; surface for merge after BinaryCell test confirms the structural fix.

## Out of scope

- Phase A pre-flight YAML audit at scale (deferred — closes after 4-cell-type matrix is structurally complete).
- Chunk-mate spillover mechanism investigation (separate session candidate from iter 5).
- Value-stability test on `lobbyist_filing_itemization_de_minimis_threshold_dollars` (separate session candidate).
- Retroactive CPI 2015 errata footnote update (low-priority cleanup; 3 errata candidates queued: IND_197, IND_207, IND_209).

---

## Expanded Step 2c — discovered scope (2026-06-05, mid-session amendment)

Original Step 2c said *"tier_1_direct_read_legal_axis.py + silent_unit_mismatch_sweep.py + grep -rn sweep."* Reality is broader. The dispatcher reads via `build_cell_spec_registry()` (loader) and `build_chunks(registry, manifest)` (which enforces a hard partition invariant: every (row_id, axis) in the registry must appear in exactly one chunk; every manifest member_row_id must resolve in the registry; otherwise raises). A v2.1 row-set change therefore cascades into chunks manifest, the CPI projection function, and several tests.

### Dan's mid-session decisions (2026-06-05)

1. **Naming** (open scoping Q (a) from §"Open scoping question for implementing agent"): new practical-axis row name = **`lobbying_disclosure_audit_required_in_practice`** (mirrors `_audit_required_in_law` — the "inverse-fix symmetric" choice). *Not* `_audit_conducted_in_practice` as the original plan defaulted.
2. **v2.1 pointer scope** (open scoping Q (b)): **branch-local** (plan default). v2.1 visible only on `wi-ralph-cpi-renewal-cadence` until BinaryCell dispatch confirms the fix; propagate to main later.
3. **How to handle the expanded Step 2c scope** (new question surfaced this session): **charge through** — full v2.1 swap on this branch (DEFAULT loader path, tests, manifest, projection). Tests stay green on this branch; other branches stay on v2.

### Production-code touchpoints (5)

1. `compendium/disclosure_side_compendium_items_v2.1.tsv` — NEW file. 4 row-level edits per §"Step 2a" above. Net 181 → 183 data rows (182 → 184 incl. header). Cell-count neutral (186 cells unchanged).
2. `compendium/source_quotes.yaml` — 2 new entries: `lobbying_violation_penalties_defined_in_law` (BinaryCell, legal axis, additive prompt) + `lobbying_disclosure_audit_required_in_practice` (5-tier int passthrough, practical axis, CPI IND_208 source quote). **No edits to existing `_imposed_in_practice` / `_audit_required_in_law` entries** — current YAML content for both is already single-axis-aligned (IND_209 practical-only for one, IND_207 legal-only for the other); the plan's "strip wrong-axis content" instruction is a no-op given actual YAML state. Verified by inspection 2026-06-05.
3. `src/lobby_analysis/compendium_loader.py:30` — swap `DEFAULT_COMPENDIUM_V2_TSV` from `_v2.tsv` → `_v2.1.tsv`. Branch-local effect: all consumers on this branch now read v2.1.
4. `src/lobby_analysis/chunks_v2/manifest.py:243-254` — extend `enforcement_and_audits` `ChunkDef.member_row_ids` from `("lobbying_violation_penalties_imposed_in_practice", "lobbying_disclosure_audit_required_in_law")` to include `"lobbying_violation_penalties_defined_in_law"` and `"lobbying_disclosure_audit_required_in_practice"` (4 row_ids total). Update chunk's `notes` to reflect the new shape.
5. `src/lobby_analysis/projections/cpi_2015_c11.py:287` — `project_ind_208`: `_practical(cells, "lobbying_disclosure_audit_required_in_law")` → `_practical(cells, "lobbying_disclosure_audit_required_in_practice")`. (The Pattern C inverse fix re-routes IND_208's practical-axis read to the new row, which is where the practical content actually lives in v2.1.)

### Test-code touchpoints (7)

1. `tests/test_models_v2_cell_spec.py:66-72` — `test_registry_doubles_each_legal_plus_practical_row`: drop `_audit_required_in_law` and `_imposed_in_practice` from `combined_row_ids` set. New set has 3 rows: `_registration_required`, `_filing_cadence`, `_registration_deadline_days_after_first_lobbying`.
2. `tests/test_models_v2_cell_spec.py:118-132` — `@pytest.mark.parametrize` cases: drop the 2 parametrize entries for the un-combined rows. (Parametrize list shrinks from 5 to 3.)
3. `tests/test_chunks_build.py:17-23` — module-level `COMBINED_AXIS_ROWS` tuple feeding `test_combined_axis_rows_land_in_same_chunk`: drop the same 2 rows. (Discovery 2026-06-05 mid-execution: this was implicit under "test_chunks_build if needed" in the original §"Test-code touchpoints"; promoted to explicit.)
4. `tests/projections/test_cpi_2015_c11_per_item.py:389,428` — IND_208 test fixture row name + `_DE_FACTO_PASSTHROUGH_ITEMS["IND_208"]` tuple — both flip to `"lobbying_disclosure_audit_required_in_practice"`. (IND_209 fixture at L403 unchanged: `_imposed_in_practice` still holds the practical cell.)
5. `tests/projections/test_cpi_2015_c11_aggregation.py:261-264` — synthesizer's audit cell currently bundles legal_availability + practical_availability under `_audit_required_in_law`. After v2.1: split into two cells — `_audit_required_in_law: {legal_availability: audit_enum}` and `_audit_required_in_practice: {practical_availability: per_item["IND_208"]}`. (Discovery 2026-06-05 mid-execution: missed in the original addendum; needed for `test_cells_synthesizer_round_trips_per_item_scores` to project IND_208 from the new row.)
6. `tests/test_compendium_loader_v2.py:35-37,45-49` — `EXPECTED_V2_ROW_COUNT` constant + `test_load_v2_compendium_returns_181_rows` test: bump constant 181 → 183 and rename test to `_returns_expected_row_count`. (Discovery 2026-06-05 mid-execution from full-suite run: caught by the 1683-test sweep, not enumerated upfront.)
7. `scripts/silent_unit_mismatch_sweep.py:175,181,187,319` — DEFERRED. Sweep is a completed one-shot artifact; no re-run scheduled this session. Touch only if Dan requests a re-run.

### TDD execution order (RED → GREEN per `skills/test-driven-development/SKILL.md`)

Skill requires writing **all** test edits before moving to GREEN.

**RED batch (write tests expressing v2.1 contract):**
1. Edit test_models_v2_cell_spec.py:66-72 → 3-row combined set.
2. Edit test_models_v2_cell_spec.py:118-132 → 3-entry parametrize.
3. Edit test_cpi_2015_c11_per_item.py:389,428 → new row name.
4. Run `pytest tests/test_models_v2_cell_spec.py tests/projections/test_cpi_2015_c11_per_item.py -x` → confirm RED (current v2.0 state should fail the new contract — registry doublings show 5 rows; projection IND_208 reads old row).

**GREEN batch (production changes):**
5. Create v2.1 TSV (touchpoint 1).
6. Add 2 YAML entries (touchpoint 2).
7. Swap DEFAULT_COMPENDIUM_V2_TSV (touchpoint 3).
8. Update chunks_v2/manifest.py enforcement_and_audits (touchpoint 4).
9. Update projection L287 (touchpoint 5).
10. Run full pytest suite → confirm GREEN (or at least no regression in {test_models_v2_cell_spec, test_chunks_build, test_cpi_2015_c11_per_item, test_cpi_2015_c11_aggregation, test_compendium_loader}).

**REFACTOR:** none expected. The changes are mechanical row renames + an additive split; no logic abstraction warranted.

### Step 3 dispatch prerequisites (all from GREEN batch)

- `pytest` green across registry/chunks/projection tests.
- v2.1 TSV has both new rows.
- YAML has prompt for `_defined_in_law` (BinaryCell additive pattern).
- Manifest's `enforcement_and_audits` chunk includes the new row.

### Rollback / risk

- If dispatch fails to converge 6/6 on `_defined_in_law`, **do not revert the schema**. The schema fix is structurally correct independent of dispatch convergence (the de-jure pair belongs in compendium per CPI 2015 IND_209 projection-mapping note). A non-convergent dispatch indicates a YAML-prompt issue, not a schema issue — diagnose at YAML level (silent unit-mismatch class? cell-type instantiation failure?) per the iter-5 playbook.
- If discovery during execution reveals further code/test touchpoints not enumerated here: **stop, surface to Dan**, do not patch silently. ("Doc system is persistent memory, not patchwork" — ship-then-patch-each-gap is the broken pattern.)

### Cost projection (revised, no change to bottom line)

- Step 0 (plan addendum + TDD setup): $0.
- Step 2 + expanded Step 2c (TSV + YAML + 5 production edits + 4 test edits): $0.
- Step 3 (dispatch): ~$0.30.
- Step 4 (audit + finish-convo): $0.
- Session total: **~$0.30**. wi-ralph cumulative after = **$2.6573**. Within $3-5 ceiling.
