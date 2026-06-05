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
