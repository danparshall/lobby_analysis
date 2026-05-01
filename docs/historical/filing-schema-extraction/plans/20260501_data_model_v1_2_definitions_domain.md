# Data Model v1.2 — `domain="definitions"` + symmetry-gap fixup

**Status:** Implement-ready. Originated from end-of-audit review (2026-05-01) in convo `20260430_compendium_audit_v2_execution`. Greenlit by user as option (A): promote 5 rows + add 2 symmetry rows.

**Originating convo:** [`convos/20260430_compendium_audit_v2_execution.md`](../convos/20260430_compendium_audit_v2_execution.md) — closing discussion of the 7 notes-flagged rows.

**Branch:** `filing-schema-extraction` (this worktree).

---

## What this changes

1. Add `"definitions"` as the 11th allowed value in `CompendiumDomain` Literal in `src/lobby_analysis/models/compendium.py`.
2. Migrate 5 existing compendium rows from `domain="registration"` to `domain="definitions"`:
   - `THRESHOLD_LOBBYING_MATERIALITY_GATE` (PRI D0; the qualitative-materiality umbrella)
   - `DEF_ADMIN_AGENCY_LOBBYING_TRIGGER`
   - `DEF_ELECTED_OFFICIAL_AS_LOBBYIST`
   - `DEF_PUBLIC_EMPLOYEE_AS_LOBBYIST`
   - `DEF_COMPENSATION_STANDARD`
3. Drop the notes flag from those 5 (they're now self-documenting via `domain="definitions"`).
4. Drop the notes flag from the 3 rows that **stay in `registration`**:
   - `REG_LOBBYIST` — flag was defensive; on review it doesn't capture a definition.
   - `THRESHOLD_LOBBYING_EXPENDITURE_PRESENT` — exemption-framed; properly a registration gate.
   - `THRESHOLD_LOBBYING_TIME_PRESENT` — exemption-framed; properly a registration gate.
5. **Symmetry-gap fix:** add 2 NEW rows for inclusion-framed expenditure/time standards (paralleling `DEF_COMPENSATION_STANDARD`):
   - `DEF_EXPENDITURE_STANDARD` (`domain="definitions"`, inclusion-framed: "spend > $X on lobbying = you ARE a lobbyist")
   - `DEF_TIME_STANDARD` (`domain="definitions"`, inclusion-framed: "spend > X% of compensated time lobbying = you ARE a lobbyist")
6. **Curation-gap fix:** add `newmark_*` / `opheim_*` framework_references to `THRESHOLD_LOBBYING_MATERIALITY_GATE` (D0). The audit caught this — D0 is the umbrella concept that subsumes Newmark/Opheim's compensation/expenditure/time standards (each implies the existence of a materiality test); the original audit only put PRI D0 framework_references on it.
7. Move dedup-map entries for Newmark/Opheim `def_expenditure_standard` and `def_time_standard` from EXISTS-on-`THRESHOLD_LOBBYING_*` to MERGE-or-NEW-on-`DEF_*_STANDARD` so the inclusion-framed dispositions are honestly captured.
8. Update tests:
   - `tests/test_compendium_loader.py::test_loader_raises_on_invalid_domain` — already covers schema rejection of unknown values.
   - Per-rubric counts unchanged (still 19/18/22/48/7); dispositions just move between rows.
   - Add a sanity test: `domain="definitions"` rows have at least one Newmark/Opheim/CPI/PRI-D0 framework_reference.

## Conceptual line (the meaning of the new domain)

- `domain="definitions"` = **statutory criteria for whether a person IS a lobbyist** (predicate on the agent: who counts).
- `domain="registration"` = **filing requirements once a person is a lobbyist** (gates, exemptions, registration-form contents).

Test for any borderline future row: "Does this answer 'who is a lobbyist?' or 'what does a lobbyist file?'" If the former, `definitions`. If the latter, `registration` (or `reporting`/etc. as appropriate).

OpenSecrets's `REG_SEPARATE_LOBBYIST_CLIENT_FILINGS` stays in `registration` under this rule — it's a filing-architecture feature, not a definitional criterion.

## Implementation steps

1. **Schema bump** — edit `src/lobby_analysis/models/compendium.py`: add `"definitions"` to `CompendiumDomain` Literal.
2. **Write a small migration script** (`/tmp/v1_2_definitions_migration.py`, one-shot) that:
   - Reads `data/compendium/disclosure_items.csv`.
   - Migrates the 5 rows: `domain` → `"definitions"`, clear notes flag.
   - Adds the 2 new symmetry rows.
   - Drops the notes flag from the 3 stay-in-`registration` rows.
   - Adds Newmark/Opheim/CPI framework_references to `THRESHOLD_LOBBYING_MATERIALITY_GATE`.
   - Writes back the CSV.
3. **Update `framework_dedup_map.csv`**: dedup-map entries for Newmark/Opheim `def_expenditure_standard` and `def_time_standard` re-target to the new `DEF_EXPENDITURE_STANDARD` / `DEF_TIME_STANDARD` rows (NEW disposition); CPI Q2 expenditure portion stays multi-row (D1_present + DEF_EXPENDITURE_STANDARD).
4. **Update `scripts/build_compendium.py`** D0/D1/D2 entries — D0's domain becomes `definitions`; D1/D2 stay `registration`. (D1/D2 row IDs already neutral from D9 rename.)
5. **Update audit doc** `results/20260430_compendium_audit.md`:
   - Decision Log D11 entry: "v1.2 schema bump landed; 5 rows migrated; 2 symmetry rows added; D0 framework_references gap closed."
   - Update per-rubric tables: dispositions for `def_expenditure_standard`/`def_time_standard` change from EXISTS-on-PRI-row to NEW-row.
   - Update notes-flagged-rows review table: all 7 flags resolved.
6. **Tests:**
   - Existing 17 should still pass.
   - Add `test_definitions_domain_rows_have_definitional_framework_refs` — every row with `domain="definitions"` has at least one Newmark/Opheim/CPI/PRI(D0) framework_reference.
   - Per-rubric counts for newmark_2017 (19), newmark_2005 (18), opheim_1991 (22), hired_guns_2007 (48), opensecrets_2022 (7) all unchanged.

## Out of scope (deliberate)

- **Renaming any row IDs.** This plan only changes domains and dedup-map targets; row IDs stay stable.
- **Re-walking other rubrics for definition concepts.** Only the rows already flagged or symmetry-gapped move. F Minus / Common Cause still excluded per the v2 audit.
- **Coverage matrix generation.** Still queued from the audit.

## Risk assessment

- **Low** schema-change risk. `domain` is read by tests (`test_loader_raises_on_invalid_domain`) and the loader. Adding a new Literal value is backward-compatible for any code that reads existing values.
- **Low** data-migration risk. CSVs are idempotent and tests catch curation drops.
- **Medium** for the dedup-map re-targeting — Newmark/Opheim entries that currently EXISTS-on-D1_present need to flip to NEW-on-DEF_EXPENDITURE_STANDARD. Small bookkeeping; verify by running the dedup-map sanity test post-migration.
- **None** for downstream code: harness reads `id`/`description`/`framework_references`, not `domain`.
