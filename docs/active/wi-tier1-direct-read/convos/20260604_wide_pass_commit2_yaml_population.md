# Wide-pass Commit 2 — YAML population for 164 remaining rows (TDD execution)

**Date:** 2026-06-04 (afternoon, immediately following Commit 1)
**Branch:** wi-tier1-direct-read
**Predecessor convo:** [`20260604_wide_pass_commit1_renderer_yaml_scaffold.md`](20260604_wide_pass_commit1_renderer_yaml_scaffold.md)
**Plan executed:** [`../plans/20260604_wide_prompt_text_pass.md`](../plans/20260604_wide_prompt_text_pass.md) (steps 18-23)
**Commits landed:** `aa58042` (RED) + `13ae80a` (GREEN)

## Summary

Picked up Commit 1's handoff and executed Commit 2 of the wide-pass plan — populate `compendium/source_quotes.yaml` for the remaining 164 v2 compendium rows that the narrow pass didn't cover. RED → GREEN sequence: 3 new failing wide-pass coverage tests committed, then a one-shot extractor script walks the 9 projection-mapping docs under `docs/historical/compendium-source-extracts/results/projections/`, lifts each row's `**Source quote**` field, and merges into the existing 17-row YAML.

End state: **181 / 181 rows populated** in `compendium/source_quotes.yaml`. Full suite 1585 pass / 0 fail / 3 skip / 3 xfail (baseline 1581 pass → +4 net new). Ruff clean. Smoke probe confirms WI Tier-1 chunks render to 6 chunks / 84 legal cells / 36 planned dispatches (matches Phase 2 baseline) with **zero row_id leakage** and **zero rows missing prompt**.

The session is mostly mechanical against a fully-specified plan. The one substantive surface was a v1-→-v2 rename-map gap: 9 v2 row_ids whose pre-freeze names the projection docs use weren't covered by the plan's D3/D4/D5/D6/D8 mechanical rules. All 9 were clean renames (not lacking-Source-quote cases) and were added as explicit `_EXPLICIT_RENAMES` entries to close the gap. None of the 164 unpopulated rows lacked a clean Source quote — the surfacing-to-Dan path in plan step 20 was unused.

## Topics Explored

- **TDD sequencing.** Wrote 5 new wide-pass coverage tests in `tests/test_source_quotes_yaml.py` and removed the Commit-1 stub `test_registry_leaves_prompt_none_for_rows_not_in_yaml` (whose contract — "rows in the wide-pass pool keep `spec.prompt is None`" — is invalidated by the wide-pass population). 3 were immediately RED (181-row coverage, 2 outlier rows); 2 were dormant guards that iterate `entries.items()` (currently 17, becomes 181 after GREEN; activate as regression guards post-Commit-2).

- **Projection-doc parser design.** Each projection-mapping doc carries atomic-indicator blocks delimited by `^#+ ` heading lines. Per block: 0-1 `**Source quote:**` line, 1+ `**Compendium rows:**` (or `**Compendium rows (sub-group):**`) markers. The parser walks lines, splits on any header level, then within each block (a) extracts backticked tokens from the Compendium-rows sub-list region, (b) extracts the FIRST `"…"` from the Source quote line plus the FIRST `(…)` parenthetical that follows. Heading levels are not respected for block boundaries — splitting on every header gives the right granularity for both PRI's `#####` atomic items and CPI/Sunlight/FOCAL's `###`/`####` blocks. Tested across all 9 docs; resolved 155 / 164 rows on the first dry-run before the explicit-rename layer was added.

- **v1 → v2 row-id rename map.** The projection docs were authored on the `compendium-source-extracts` branch BEFORE the 2026-05-13 row-freeze (`20260513_row_freeze_decisions.md` D1-D8). The v2 TSV uses post-freeze canonical row_ids. Reading source quotes for v2 rows requires resolving them back to v1 row_ids in the projection docs.

  The plan's design enumerated D3/D4/D5/D6/D8 rules; I encoded them as mechanical string substitutions plus a `_EXPLICIT_RENAMES` dict for D1/D2 hand-merges. The dry-run surfaced 9 unresolved rows — all of which turned out to be clean renames not covered by the mechanical rules:

  | v2 row_id | v1 row_id (in projection doc) | Source rubric |
  |---|---|---|
  | `lobbyist_registration_threshold_compensation_dollars` | `compensation_threshold_for_lobbyist_registration` | CPI #197 |
  | `lobbyist_registration_threshold_time_percent` | `time_threshold_for_lobbyist_registration` | Newmark def.time_standard |
  | `lobbyist_filing_itemization_de_minimis_threshold_dollars` | `expenditure_itemization_de_minimis_threshold_dollars` | Sunlight #3 |
  | `def_lobbying_activity_types` | `lobbying_definition_included_activity_types` | FOCAL scope.4 |
  | `def_lobbyist_actor_types` | `lobbyist_definition_included_actor_types` | FOCAL scope.1 |
  | `ministerial_diary_available_online` | `ministerial_diaries_available_online` (plural) | FOCAL openness.2 |
  | `lobbyist_or_principal_reg_form_includes_member_or_sponsor_names` | `principal_or_lobbyist_reg_form_includes_member_or_sponsor_names` (word-order swap) | FOCAL relationships.2 |
  | `lobbyist_filing_de_minimis_threshold_dollars` | `materiality_threshold_financial_value` | PRI D1_present / D1_value |
  | `principal_spending_report_includes_compensation_paid_to_lobbyists` | `principal_report_includes_direct_compensation` | PRI E1f_i (D2) |

  After adding these to `_EXPLICIT_RENAMES`, the dry-run resolved all 164 rows.

- **YAML key derivation.** Heading-derived slug + rubric-vintage prefix: e.g., `pri_2010_E2f_i`, `cpi_2015_IND_196`, `focal_2024_scope_3`, `hiredguns_2007_Q3`, `newmark_2017_def_legislative_lobbying`, `sunlight_2015_lobbyist_activity`. Strips the rubric prefix when the heading already includes it (e.g., FOCAL/HG/Newmark/Sunlight headings have `focal_2024.X` / `hg_2007.X` / `newmark_2017.X` / `sunlight_2015.X` patterns; the slug normalizes `.` → `_` and emits `<rubric>_<vintage>_<slug>`). The narrow-pass uses citation-paren-derived keys (e.g., `pri_2010_§III.E2.f.i`); the wide-pass uses heading-derived keys. Both conventions co-exist in the YAML — no key collision because every row's `source_quotes` dict is independent.

- **Outlier handling.** 2 rows hand-encoded per plan step 19:
  - `lobbyist_filing_distinguishes_in_house_vs_contract_filer` (LobbyView D12 LV-1 IN) — no quotable question in source; synthesized prompt with `lobbyview_2018_schema_field_is_client_self_filer` as the provenance key.
  - `separate_registrations_for_lobbyists_and_clients` (D16 OS-1 path-b unvalidated) — quote from `_tabled/opensecrets_2022_tabled.md` candidate 1; synthesized prompt with `opensecrets_2022_tabled_candidate_1` as the provenance key.

## Provisional Findings

- **End-to-end smoke probe confirms zero row_id leakage and full prompt coverage.** Built a programmatic probe (`/tmp/smoke_wide_pass.py`) that imports `tier1.build_legal_roster` + `tier1.render_legal_roster` and walks all 6 WI chunks. Asserts: rendered messages contain no v2 row_ids verbatim (0 leaks across 84 cells × 6 chunks); every spec has a non-empty `prompt`; chunk + cell + dispatch counts match Phase 2 baseline (6 / 84 / 36). All assertions pass.
- **Short source quotes for PRI section-A atomic items.** PRI's A1-A11 atomic items have terse source quotes like `"Legislative branch."`, `"Lobbyists."`, `"Volunteer lobbyists."` — that's how PRI's paper §III.A structures the actor-side list. Initially-populated prompts inherit these terse quotes. The Ralph loop or future sessions are expected to enrich these for model clarity (plan step 18: "Initial `prompt:` value is the verbatim quote — the Ralph loop or future sessions evolve it from there"). No fix needed in this commit.
- **The 5 new wide-pass tests + the 17 narrow-pass tests are now mutually reinforcing.** Narrow-pass tests pin the migration-correctness contract for the 17 specific rows (Pattern A clarifier preservation, no citation leakage on those rows, source_quotes provenance). Wide-pass tests pin the all-181-row coverage contract (every row has a non-empty prompt + source_quotes; no citation leakage across the full set; the 2 outliers carry their hand-keyed entries). After Commit 2 GREEN, both layers hold simultaneously.
- **Registry is 186 entries for 181 rows.** Two-axis rows (`lobbyist_registration_required` per D10, `registration_deadline_days_after_first_lobbying` per D11) produce separate `(row_id, axis)` entries in the registry. Both legal- and practical-axis specs share the same `prompt` from the row's YAML entry. Not a regression.

## Decisions Made

- **Heading-derived YAML keys for wide-pass entries.** Consistent across rubrics: `<rubric>_<vintage>_<heading_slug>` with `.` → `_` normalization. The narrow-pass citation-derived keys (e.g., `pri_2010_§III.E2.f.i`) stay as-is; no retroactive rename. Mixed-style keys are fine because each row's `source_quotes` dict is independent — no key collisions across rows.
- **Citation parens stripped from `prompt`.** The model-facing string is the verbatim quote alone. Citations live only in YAML keys (provenance). Matches the narrow-pass convention.
- **Initial `prompt` = verbatim quote alone (no decoration).** Per plan step 18 and 19's outlier exception. The 2 outlier rows get synthesized prompts (no verbatim source available); all other 162 wide-pass rows get verbatim-as-prompt.
- **`_EXPLICIT_RENAMES` covers the 10 v1-→-v2 rename gaps.** Each entry documented in the script's comment with the specific rubric+section the v1 name comes from. Mechanical D3 (`_spending_report_` ↔ `_report_`) + D4 (`lobbyist_filing_de_minimis_threshold_` ↔ `materiality_threshold_`) + D5/D6/D8 rules cover the majority; explicit entries close the gaps the mechanical rules miss.
- **Removed Commit-1 stub `test_registry_leaves_prompt_none_for_rows_not_in_yaml`.** Its assertion (`spec.prompt is None` for `principal_spending_report_required`) is the inverse of what the wide pass establishes. Replaced by `test_all_181_rows_have_nonempty_prompt`, which pins the broader contract.
- **Migration script preserved at `scripts/_completed/populate_source_quotes_wide_pass.py`.** Per CLAUDE.md Experiment Data Integrity policy and the pattern from Commit 1's `migrate_prompts_to_yaml.py`.

## Results

No standalone analytical results files this session (code + tests + YAML data only). Verifiable artifacts:

- `compendium/source_quotes.yaml` — 181 rows (was 17), all with non-empty `prompt` + non-empty `source_quotes` dicts.
- `scripts/_completed/populate_source_quotes_wide_pass.py` — one-shot extractor (idempotent; re-running preserves existing rows and only adds missing ones).
- `tests/test_source_quotes_yaml.py` — 20 tests (was 17), all GREEN. Net +4 (5 new wide-pass + 1 stub removed).

## Open Questions

- **Commit 3 spend authorization.** Plan step 24 says "Confirm with Dan that the spend (~$2.50) is OK to fire". Not asked this session; landing Commit 2 stands on its own (it's the YAML SSOT contract; doesn't require the re-dispatch to be value-positive). When Dan is ready to validate the wide pass against WI's prior baseline, the next step is: archive existing result JSONs to `_pre_wide_pass/`, dispatch, and re-run the σ_noise / inter-model audit. Baseline: 65/66 agreement (98.5%); regression watch is for any previously-passing row that flips under the new substantive-prompt renderer.
- **Prompt-quality on terse-quote rows.** ~30 of the PRI A-, B-, C-, D-section rows have very short source quotes (e.g., `"Legislative branch."`). For model legibility, the Ralph loop will likely need to expand these. Not in scope for this commit; flag for future prompt-evolution session.
- **No backward-compat for narrow-pass key convention.** The 17 narrow-pass rows continue to use citation-derived keys like `pri_2010_§III.E2.f.i`; the 164 wide-pass rows use heading-derived keys like `pri_2010_E2f_i`. Both correct, both serve the provenance role. If consistency is wanted as a future polish, an optional Commit-4-style stylistic commit could renormalize. Not blocking.
- **The 7 newly-discovered renames (CPI/Newmark/Sunlight/FOCAL gap) are documented in the script comment but not in `20260513_row_freeze_decisions.md`.** They're not new freeze decisions — they're cases where the freeze decisions doc doesn't enumerate every v1→v2 rename (the doc focused on canonicalization decisions, not the full rename map). Worth flagging for the v2.2 design pass: if a future row-set bump needs a complete rename catalog, this script's `_EXPLICIT_RENAMES` is the load-bearing reference.

## Session meta — execution against the well-specified plan

Same pattern as Commit 1: 200+-line plan with full Testing Plan + Edge Cases + Implementation Details + Pointers. Execution was mechanical against it. The single substantive surface (the rename-map gap) was caught by the script's dry-run mode (`--dry-run` flag I added during construction) and resolved in-session without surfacing to Dan — the 9 unresolved rows were all clean renames, not the plan-step-20 "lacks clean Source quote" case. Surfaced renames in this convo for traceability instead.

Deviations from a literal plan reading:
1. Added `--dry-run` flag to the migration script (not specified in plan). Allowed iterating on the rename map without writing YAML on each pass.
2. Removed the Commit-1 stub `test_registry_leaves_prompt_none_for_rows_not_in_yaml` rather than rewriting it. The plan didn't explicitly address this; deletion vs. inversion is a stylistic choice and matches the wide-pass's "all rows have prompts" contract more cleanly.
3. Wrote a one-off smoke probe at `/tmp/smoke_wide_pass.py` rather than relying on the dispatch script's `--dry-run` flag (which doesn't exist — verified plan step 22's hedge "verify the exact flag name in the script"). Same end goal: assert 6 / 84 / 36 + no row_id leakage + all prompts populated. The temp script is gone after this session; if persistent verification is wanted, the assertions could move into a pytest test that imports the renderer + builds a chunk manually.

No API spend this session (TDD implementation + smoke probe only). Cumulative WI Tier-1 ledger unchanged at $4.7504.
