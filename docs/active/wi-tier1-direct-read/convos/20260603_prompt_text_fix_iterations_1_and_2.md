# prompt_text fix — iterations 1 and 2

**Date:** 2026-06-03 (evening)
**Branch:** `wi-tier1-direct-read`
**Predecessor convo:** [`20260603_statute_disagreement_prior_art_review.md`](20260603_statute_disagreement_prior_art_review.md)
**Full writeup:** [`../results/20260603_prompt_text_fix_iterations.md`](../results/20260603_prompt_text_fix_iterations.md)
**v2.2 ledger entry resolved:** Entry 3 (narrow pass) — see [`../results/v2_2_schema_inputs.md`](../results/v2_2_schema_inputs.md)

## Summary

Picked up the handoff from the morning's prior-art adjudication. The handoff identified the structural cause of the WI 18-cell inter-model disagreement (`render_legal_roster` sent no row-question text — only `row_id` / `axis` / `expected_cell_class` — so models reverse-engineered intent from the row ID alone, and that compression destroyed the filer-vs-subject disambiguation on 17 rows) and proposed a narrow fix: add a `prompt_text` column to the v2 TSV, populate it for the 17 confirmed disagreement rows from verbatim source-rubric quotes, update the dispatch script to emit it, and re-dispatch 3 chunks (~$1, ~10 min).

Implemented test-first: 6 RED tests for the column + registry + render pathway, then GREEN with three coordinated edits (`CompendiumCellSpec` gets optional `prompt_text` field; `build_cell_spec_registry()` loads it from the new TSV column; `render_legal_roster` emits it as a continuation line below the row metadata when present). Added an idempotent populate script (`scripts/add_prompt_text_column.py`) so iterating on prompt wording is one-edit-and-rerun. Updated `tests/test_compendium_loader_v2.py`'s pinned column set to include the new column (it correctly caught the addition).

Re-dispatched twice. Iter-1 with verbatim source quotes only — collapsed Pattern B (3/3) but only 2/14 of Pattern A; Claude began constructing more specific statutory arguments for TRUE (signature-on-principal-form, name-listed-by-principal, compensation-itemized-in-principal-aggregate). Iter-2 added a uniform LOBBYIST-vs-PRINCIPAL clarifier appended to all 14 Pattern A rows' source quotes, specifically naming those three arguments as NOT counting. **Collapsed Pattern A 14/14.** Claude's new justifications mirror the clarifier's vocabulary back ("the lobbyist is not the named filer of a separate spending report"). Per-iteration costs $1.41 and $0.77 = $2.18 cumulative API spend, within the handoff's ~$4 ceiling.

## Topics Explored

- Source-quote extraction tooling — wrote a block-aware parser over the 5 projection-mapping docs (`pri_2010`, `cpi_2015_c11`, `sunlight_2015`, `newmark_2017`, `hiredguns_2007`) to pull `Source quote` fields by `Compendium rows` reference. Surfaced known row-ID renames between projection mappings and v2.1 TSV (`lobbyist_report_*` → `lobbyist_spending_report_*`; `materiality_threshold_time_percent` → `lobbyist_filing_de_minimis_threshold_time_percent`; `expenditure_threshold_for_lobbyist_registration` → `lobbyist_registration_threshold_expenditure_dollars`) — already tracked as v2.2 ledger Entry 4 (still open).
- Test-first: 6 RED tests covering CellSpec field default, registry population (17-row coverage + None for untouched), render emit/omit behavior. RED on the dataclass attribute first; GREEN after all 3 code edits + TSV population.
- TSV diff hygiene — first pass with `csv.DictWriter` default `'\r\n'` lineterminator ballooned the diff with CRLF noise; switched to `lineterminator='\n'` to preserve Unix endings. Residual 182/182 line swap is intrinsic (every row gets a new trailing column).
- Iter-2 design decision: the Pattern A clarifier is uniform across the 14 rows (they all share the same filer/subject ambiguity), while Pattern B kept its row-specific inline clarifiers. Composed via `_assemble_prompt_text(row_id)` helper that appends `PATTERN_A_CLARIFIER` only for rows in `_PATTERN_A_ROWS` set.
- Direct evidence the clarifier landed: spot-checked Claude's `instantiated_cells` justifications for `lobbyist_spending_report_required` across the 3 iter-2 runs — all three explicitly use the "named filer of a separate spending report" framing.

## Provisional Findings

- **Verbatim source quote is necessary but not always sufficient.** The same verbatim CPI 2015 IND_201 quote that the prior-art adjudication cited as the canonical disambiguator failed to push Claude across on the lobbyist_spending_report_* family; Claude read "(including ... compensation/payments received for lobbying services)" as describing the *subject* of the question rather than constraining the *filer*. The Pattern B rows happened to have source quotes that embedded clarifying context naturally (Newmark/PRI/CPI quotes about thresholds are short and unambiguous about the LOBBYIST); Pattern A's quotes were structurally ambiguous.
- **Targeted clarifier collapses Pattern A.** Naming the three exact arguments Claude was constructing for TRUE and stating each as NOT counting pushed all 14 onto FALSE. Claude's `σ_noise` improved over even the pre-fix baseline (85.71 → 86.90), so the longer prompt made it more stable, not less.
- **Pattern C is unchanged and was expected to be unchanged.** `lobbying_violation_penalties_imposed_in_practice` is a row-axis-registration issue (v2.1 TSV registers it as `legal+practical`; CPI 2015 IND_209 explicitly assigns it to practical-only), not a prompt-text issue. v2.2 ledger Entry 2 already proposes the row split.
- **No JSON deletions, two clean archive subdirs.** All 24 superseded result JSONs across iter-0/1 baselines preserved under `_pre_prompt_text_fix/` (18 from Phase 2, pre-prompt_text) and `_pre_pattern_a_clarifier/` (6 from iter-1 lobbyist_spending_report, pre-Pattern-A-clarifier).
- **Cumulative WI Tier-1 API spend ledger:** Phase 2 baseline $2.5708 (2026-06-01) + iter-1 $1.4080 + iter-2 $0.7716 = **$4.7504** total on WI. Original handoff estimate was $2-4 for Phase 2 alone, so the full validation arc came in at roughly Phase 2 + ~$2.

## Decisions Made

- Land the narrow 17-row fix. Done.
- Pattern B keeps row-specific inline clarifiers; Pattern A gets a uniform clarifier. Justified by the shape of the ambiguity (Pattern A is the same filer/subject question across 14 rows; Pattern B is 3 distinct definitional thresholds).
- Wide 181-row pass — strategy: populate from verbatim source quotes first; only add per-row clarifiers for rows that show inter-model disagreement after that pass. Don't pre-emptively add Pattern-A-style clarifiers to all 181 rows. Open for next session.
- MI dispatch is now unblocked. Pattern Pattern A + Pattern B clarifier patterns port, but specific row coverage may not — MI may surface new filer/subject ambiguities in different rows.

## Results

- [`../results/20260603_prompt_text_fix_iterations.md`](../results/20260603_prompt_text_fix_iterations.md) — full iter-0 / iter-1 / iter-2 trajectory writeup with numbers, mechanics, direct evidence, and corpus state.
- [`../results/20260603_wi_intermodel_disagreement_iter2.txt`](../results/20260603_wi_intermodel_disagreement_iter2.txt) — iter-2 audit script output, captured verbatim.
- v2.2 ledger Entry 3 updated to reflect narrow-pass landing + validation.

## Open Questions

- **Wide 181-row pass:** populate `prompt_text` from each row's `first_introduced_by` rubric's verbatim `Source quote`. Most rows are not filer/subject-ambiguous and verbatim quotes likely suffice. The block-aware parser in `/tmp/extract_source_quotes.py` (NOT checked in) is the prototype for this; it surfaced ~5 known row-ID renames in the 17-row scope, so the wide pass needs a name-rename mapping built first (v2.2 ledger Entry 4 territory).
- **MI dispatch:** does the Pattern A clarifier shape generalize? MI's statute structure differs from WI; the specific arguments Claude makes for TRUE on MI's filer-ambiguous rows (if any) may differ. The next MI session should re-audit inter-model disagreements after dispatch with the WI-tuned clarifier and look for new patterns.
- **Pattern C row-axis split (v2.2 Entry 2):** small change (split `lobbying_violation_penalties_imposed_in_practice` into `_authorized_in_statute` legal-only + `_imposed_in_practice` practical-only). Would close the final WI disagreement. Trade-off: adds 1 row to the compendium count (181 → 182); v2.1 is technically frozen.
- **Source-quote provenance column (v2.2 Entry 4):** wide pass will need a row-rename mapping; if we add a `source_quote_verbatim` column at the same time as the wide `prompt_text` pass, the rename history becomes auditable in the TSV directly.
- **Claude's interpretive frame as a research artifact:** in iter-1 Claude was making *more sophisticated* arguments than pre-fix (citing signature requirements, itemization within aggregates) — suggesting the source-quote anchor moved Claude toward more careful reading but in a direction parallel to GPT's, not the same direction. Possibly informative about how to design prompts in general: source quotes anchor *quality* of reading; clarifiers anchor *direction* of reading. Worth a future convo to test this hypothesis on a row outside the WI 17.
