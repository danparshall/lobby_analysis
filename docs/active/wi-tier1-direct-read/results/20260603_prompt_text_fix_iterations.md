<!-- Generated during: convos/20260603_prompt_text_fix_iterations_1_and_2.md -->

# WI prompt_text fix — iterations 1 and 2

**Session:** 2026-06-03 (evening)
**Convo:** [`../convos/20260603_prompt_text_fix_iterations_1_and_2.md`](../convos/20260603_prompt_text_fix_iterations_1_and_2.md)
**Predecessor convo (handoff):** [`../convos/20260603_statute_disagreement_prior_art_review.md`](../convos/20260603_statute_disagreement_prior_art_review.md)
**Predecessor adjudication:** [`20260603_prior_art_adjudication_of_18_disagreements.md`](20260603_prior_art_adjudication_of_18_disagreements.md)
**v2.2 ledger entry resolved:** [`v2_2_schema_inputs.md`](v2_2_schema_inputs.md) Entry 3 (narrow 17-row pass landed + validated)

---

## TL;DR

The handoff from the morning's prior-art adjudication identified that the dispatch prompt sent only `row_id`/`axis`/`expected_cell_class` to the model — no row-question text at all — and proposed a narrow fix: populate a `prompt_text` column on the v2 compendium TSV for the 17 confirmed inter-model disagreement rows (14 Pattern A + 3 Pattern B), update `render_legal_roster` to emit it, and re-dispatch the 3 affected chunks on WI to test whether Claude collapses onto GPT's reading.

Two iterations were needed:

- **Iter-1** (verbatim source quotes alone): collapsed Pattern B 3/3, Pattern A only 2/14. Claude was still reading "lobbyists are required to file ... compensation/payments received" as "is information about the lobbyist's compensation required to be disclosed *anywhere* in the regime" → TRUE for WI (via the principal's report).
- **Iter-2** (added uniform LOBBYIST-vs-PRINCIPAL filer-clarifier to all 14 Pattern A rows): collapsed Pattern A 14/14. Claude's new justifications mirror the clarifier's language ("the lobbyist is not the named filer of a separate spending report", "there is no separate lobbyist-filed spending report").

**Final outcome:** 17 of 17 confirmed disagreement cells collapsed. Inter-model agreement on the 84-cell WI Tier-1 roster went from 47/65 (72.3%) → 65/66 (98.5%) jointly-stable cells. The 1 remaining disagreement is the known Pattern C mis-axed row (`lobbying_violation_penalties_imposed_in_practice`), which is a v2.2 axis-split, not a prompt fix.

Cumulative API spend on the fix: **$2.18** ($1.41 iter-1 + $0.77 iter-2), well under the ~$4 ceiling discussed in the handoff.

---

## Iter-1 — verbatim source quotes

### Change shape

| Surface | Change |
|---|---|
| `compendium/disclosure_side_compendium_items_v2.tsv` | Added `prompt_text` column. Populated for the 17 disagreement rows using verbatim `Source quote` field from each row's `first_introduced_by` rubric's projection-mapping doc, with citation appended. |
| `src/lobby_analysis/models_v2/cell_spec.py` | Added `prompt_text: str \| None = None` field to `CompendiumCellSpec`. Registry builder loads from new TSV column; absent column tolerated for older TSV vintages. |
| `scripts/tier_1_direct_read_legal_axis.py` | `render_legal_roster` emits `  source-rubric question: <verbatim>` as continuation line below each row metadata line when `prompt_text` is present; omitted otherwise. |
| `scripts/add_prompt_text_column.py` (NEW) | Idempotent populate script. Re-runs overwrite, so iterating on prompt wording is one-edit-and-rerun. |
| `tests/test_prompt_text_column.py` (NEW) | 6 tests: field exists with `None` default, registry populates 17 rows, leaves the other 164 as `None`, render emits when present, omits when absent. |
| `tests/test_compendium_loader_v2.py` | Updated `EXPECTED_V2_COLUMNS` to include `prompt_text`. |

Tests after iter-1: **1559 pass / 3 skip / 3 xfail** (baseline 1553 + 6 new). Ruff clean.

### Pattern A vs Pattern B source-quote shape

Pattern B's source quotes already had inline filer/subject clarifiers (composed during the population pass since the Newmark/PRI/CPI quotes were short and the clarifier was per-row natural):

> *"if they spend a certain amount of money in lobbying (expenditure standards)" (Newmark 2017 paper line 523-524; newmark_2017_projection_mapping.md, def.expenditure_standard. **Asks about the LOBBYIST-DEFINITION expenditure threshold — i.e., the dollar amount the LOBBYIST spends in lobbying that triggers their registration as a lobbyist, not a principal-side filing trigger.**)*

Pattern A in iter-1 was the verbatim source quote only — no per-row clarifier:

> *"A YES score is earned if lobbyists are required to file itemized spending reports (including name of employer, lobbied issues and bill number(s) and compensation/payments received for lobbying services). A MODERATE score is earned if lobbyists are required to file itemized spending reports or compensation/payments received, but not both. A NO score is earned if no such law exists." (CPI 2015 IND_201; cpi_2015_c11_projection_mapping.md.)*

### Re-dispatch mechanics

- Created archive dir `docs/active/wi-tier1-direct-read/results/tier_1/WI_2025/_pre_prompt_text_fix/`
- Moved the 18 result JSONs from the 3 affected chunks (`lobbyist_spending_report`, `registration_thresholds`, `registration_mechanics_and_exemptions`) into archive
- Ran `scripts/tier_1_direct_read_legal_axis.py --state WI --vintage 2025`
- Resume-skip preserved the 18 unaffected JSONs; re-dispatched the 18 affected
- Wall: ~6.5 min, cost: $1.4080

### Iter-1 audit numbers

| Metric | Pre-fix (Phase 2, 2026-06-01) | After iter-1 |
|---|---|---|
| Jointly within-model stable | 65 / 84 | 63 / 84 |
| Inter-model agree | 47 (72.3%) | 50 (79.4%) |
| Inter-model DISAGREE | 18 (27.7%) | 13 (20.6%) |
| Pattern A disagreements (`lobbyist_spending_report` chunk) | 14 | 12 |
| Pattern B disagreements (registration chunks) | 3 | **0 ✓** |
| Pattern C disagreements (mis-axed) | 1 | 1 (expected) |
| Claude `σ_noise` (pct_stable) | 85.71 % | 83.33 % |
| GPT-5.2 `σ_noise` | 84.52 % | 82.14 % |

Pattern B fully resolved. Pattern A mostly not — Claude began constructing more specific statutory arguments for TRUE rather than abandoning the position:

- `_required`: cites §13.68(4) requiring the lobbyist to **sign** the principal's expense statement → "lobbyist files it"
- `_includes_lobbyist_contact_info`: cites §13.68(1)(a)6 listing lobbyist name/address in the principal's report → "lobbyist info is in the spending report"
- `_includes_total_compensation`: cites §13.68(1)(a)1 requiring compensation-to-lobbyists in the principal's aggregate → "lobbyist comp is in the spending report"

The verbatim CPI quote — without an explicit "FALSE if the statute mandates the PRINCIPAL as filer" clarifier — didn't push Claude across.

---

## Iter-2 — uniform Pattern A filer-clarifier

### Change shape

Single addition to `scripts/add_prompt_text_column.py` — a `PATTERN_A_CLARIFIER` constant appended to all 14 Pattern A rows' source quotes via an `_assemble_prompt_text(row_id)` helper. Pattern B rows kept their row-specific inline clarifiers. Population pass overwrites in place; one TSV diff, no other code surface touched.

### The clarifier text

> *"Asks whether the LOBBYIST is the named filer of a separate spending report — NOT whether the principal's expense statement contains lobbyist info (e.g., the lobbyist's signature on the principal's form, the lobbyist's name/address listed by the principal, or compensation paid to lobbyists itemized within the principal's aggregate). FALSE in regimes where the statute mandates the PRINCIPAL as the filer of the spending report, even if the principal's report references the lobbyist."*

Designed to pre-empt the three exact arguments Claude had been making in iter-1: signature-on-principal-form, name-listed-by-principal, compensation-in-principal-aggregate. Each named explicitly as NOT counting.

### Re-dispatch mechanics

- Created archive dir `docs/active/wi-tier1-direct-read/results/tier_1/WI_2025/_pre_pattern_a_clarifier/`
- Moved the 6 result JSONs from `lobbyist_spending_report` only (since iter-2 only touched Pattern A rows, which all live in that chunk)
- Ran the dispatch script — resume-skipped 30, re-dispatched 6
- Wall: ~4.7 min, cost: $0.7716

### Iter-2 audit numbers

| Metric | Pre-fix | Iter-1 | **Iter-2** |
|---|---|---|---|
| Jointly within-model stable | 65 | 63 | **66** |
| Inter-model agree | 47 (72.3%) | 50 (79.4%) | **65 (98.5%)** |
| Inter-model DISAGREE | 18 (27.7%) | 13 (20.6%) | **1 (1.5%)** |
| Pattern A disagreements | 14 | 12 | **0 ✓** |
| Pattern B disagreements | 3 | 0 | 0 ✓ |
| Pattern C disagreements | 1 | 1 | 1 (expected) |
| Claude `σ_noise` | 85.71 % | 83.33 % | **86.90 %** |
| GPT-5.2 `σ_noise` | 84.52 % | 82.14 % | 82.14 % |

### Direct evidence of clarifier landing

Claude's new justifications on the Pattern A anchor row (`lobbyist_spending_report_required`) across 3 runs:

- Run 1: *"Wisconsin's statute requires 'Every principal which is registered under s. 13.64' to file the expense statement; the lobbyist is not the named filer of a separate spending report."*
- Run 2: *"Wisconsin mandates that the principal (not the lobbyist) files the expense statement; §13.68(4) only requires lobbyists to provide information to the principal, who then files."*
- Run 3: *"Wisconsin requires the PRINCIPAL (not the lobbyist) to file the expense statement; §13.68(4) only requires the lobbyist to supply information to the principal, who then files, so there is no separate lobbyist-filed spending report."*

Claude is now using GPT's framing — and specifically the clarifier's vocabulary (*"named filer of a separate spending report"*, *"no separate lobbyist-filed spending report"*). The fix isn't lucky model variance; Claude updated its interpretive frame to match the source-rubric intent once that intent was made unambiguous.

Claude `σ_noise` improved over even the pre-fix baseline (85.71 → 86.90), suggesting the longer, more directive prompt made Claude *more* stable run-to-run, not less.

---

## What this validates (and what it doesn't)

### Validates

1. **The structural finding from the prior-art adjudication.** Row IDs alone *are* a lossy compression of source-author intent for filer-vs-subject-ambiguous rows.
2. **The narrow fix shape.** Adding a `prompt_text` column to the TSV + emitting it in the dispatch roster is the minimum-cost intervention that resolves the disambiguation problem.
3. **The verbatim source quote is necessary but not always sufficient.** Pattern B's source quotes happened to embed clarifying context naturally; Pattern A's CPI/PRI quotes did not, and required a separate explicit clarifier.

### Does NOT validate

1. **That all 181 rows need clarifiers of the Pattern A shape.** Most rows are not filer-vs-subject-ambiguous — verbatim source quotes likely suffice. The wide pass should populate from verbatim source quotes first; only rows that show inter-model disagreement after that pass warrant per-row clarifiers.
2. **That this fix is sufficient for MI.** MI's statute structure differs from WI; new filer-vs-subject ambiguities may surface elsewhere. The pattern (verbatim quote + targeted clarifier when needed) ports; the specific row coverage doesn't.
3. **That `σ_noise` improvements are durable.** Three runs at n=3 is thin; the cross-state generalization will be the real test.

---

## State of the WI 2025 results corpus

```
docs/active/wi-tier1-direct-read/results/tier_1/WI_2025/
├── claude-opus-4-7__{6 chunks}__run{1,2,3}.json     (18 files — top level, current)
├── gpt-5.2-2025-12-11__{6 chunks}__run{1,2,3}.json  (18 files — top level, current)
├── _pre_prompt_text_fix/
│   ├── claude-opus-4-7__{lobbyist_spending_report, registration_thresholds, registration_mechanics_and_exemptions}__run{1,2,3}.json
│   └── gpt-5.2-2025-12-11__{same 3 chunks}__run{1,2,3}.json
│   (18 files — Phase 2 baseline, 2026-06-01, no prompt_text)
└── _pre_pattern_a_clarifier/
    ├── claude-opus-4-7__lobbyist_spending_report__run{1,2,3}.json
    └── gpt-5.2-2025-12-11__lobbyist_spending_report__run{1,2,3}.json
    (6 files — iter-1, 2026-06-03, prompt_text without Pattern A clarifier)
```

Per CLAUDE.md Experiment Data Integrity policy, no JSONs were deleted at any iteration boundary.

Top-level corpus is the mix: `lobbyist_spending_report` = iter-2 (prompt_text + Pattern A clarifier); `registration_thresholds` + `registration_mechanics_and_exemptions` = iter-1 (prompt_text only, no Pattern A clarifier — these don't have Pattern A rows); the other 3 chunks (`lobbying_definitions`, `principal_spending_report`, `enforcement_and_audits`) = Phase 2 baseline JSONs (no prompt_text — none of these chunks have any of the 17 disagreement rows).

To reproduce earlier-iteration audits: temporarily swap archive directories' contents to the top level and re-run `docs/active/wi-tier1-direct-read/results/disagreement_audit/wi_intermodel_disagreement.py`.

The current iter-2 audit output is saved at [`20260603_wi_intermodel_disagreement_iter2.txt`](20260603_wi_intermodel_disagreement_iter2.txt).
