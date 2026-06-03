<!-- Generated during: convos/20260603_statute_disagreement_prior_art_review.md -->

# Prior-art adjudication of the 18 WI inter-model disagreement cells

**Session:** 2026-06-03
**Convo:** [`../convos/20260603_statute_disagreement_prior_art_review.md`](../convos/20260603_statute_disagreement_prior_art_review.md)
**Predecessor results doc:** [`20260601_wi_statute_vs_portal_spending.md`](20260601_wi_statute_vs_portal_spending.md) — surfaced the 18 disagreements (27.7% of 65 jointly-stable cells).
**Predecessor plan:** [`../plans/20260601_post_phase3_followups.md`](../plans/20260601_post_phase3_followups.md) Item 3 — Citations API for adjudication, open candidate.
**Inputs analyzed:**
- 36 Tier-1 result JSONs at `results/tier_1/WI_2025/` (2 models × 3 runs × 6 chunks).
- `compendium/disclosure_side_compendium_items_v2.tsv` for per-row source-rubric provenance.
- 5 projection-mapping docs at `docs/historical/compendium-source-extracts/results/projections/` (PRI 2010, CPI 2015 C11, Sunlight 2015, Newmark 2017, HG 2007) for verbatim source-quote text.
- `scripts/tier_1_direct_read_legal_axis.py` — the dispatch script and prompt construction.
**Reproducibility scripts:** [`disagreement_audit/wi_intermodel_disagreement.py`](disagreement_audit/wi_intermodel_disagreement.py) (enumerates the 18), [`disagreement_audit/wi_disagreement_provenance.py`](disagreement_audit/wi_disagreement_provenance.py) (joins to TSV provenance).

---

## TL;DR

1. **All 18 disagreements are row-meaning problems, not statute-reading problems.** Both models converge on which sections of WI's lobbying statute apply; they diverge on what the *compendium row* is asking.
2. **Prior art adjudicates 17 of the 18 in GPT's favor.** Claude was over-charitable to the row label (treating `lobbyist_spending_report_*` as "anything in the regime touching the lobbyist"); GPT read the label literally (the lobbyist as filer). The source rubrics (CPI 2015 IND_201, PRI 2010 §III.E2, Newmark 2017, others) explicitly ask about the lobbyist as filer — they maintain `principal_*` as separately-asked sibling rows precisely because the two are not interchangeable.
3. **The 1 remaining cell is a v2.2 row-axis issue, not a model disagreement.** `lobbying_violation_penalties_imposed_in_practice` (CPI 2015 IND_209) was registered as `legal+practical` in the v2.1 TSV; the row name embeds "in practice"; CPI's source quote is unambiguously about empirical imposition. Running this on the legal axis at all is the bug.
4. **Closing Item 3 (Citations API).** Span-level citations within §13.68 wouldn't have changed the verdict — both models already cite the right sections. The disambiguation lives in the prior-art layer, not the statute layer. Item 3 is decisively out as a response to this finding.
5. **Structural finding worth its own attention: the dispatch prompt sends only row IDs, no question text.** `render_legal_roster` in `scripts/tier_1_direct_read_legal_axis.py` (line 205–223) emits `- row_id='lobbyist_spending_report_required', axis='legal', expected_cell_class=BinaryCell` — that's the entire per-row prompt. The verbatim source-rubric question text exists in the projection-mapping docs but never reaches the model. The right fix for the 17 row-meaning disagreements is to add a `prompt_text` column to the TSV, populate it from the source-rubric quotes, and have `render_legal_roster` include it on each roster line.

---

## Setup: what counted as a "disagreement"

Defined as a (chunk, row_id) where:

1. All 3 Claude `opus-4-7` runs agree on (kind, value).
2. All 3 GPT `5.2-2025-12-11` runs agree on (kind, value).
3. Claude's consensus answer ≠ GPT's consensus answer.

"Kind" is one of `scored` / `unscoreable` / `incomplete`. Two scored runs with the same value count as agreement. Two `unscoreable` runs count as agreement regardless of the reason text.

The enumeration script (`disagreement_audit/wi_intermodel_disagreement.py`) walks all 36 JSONs and produces this report. Counts replicate the predecessor doc's headline exactly:

| Metric | Count |
|---|---|
| Total unique (chunk, row_id) cells | 84 |
| Jointly within-model stable | 65 |
| Inter-model agree (of 65) | 47 (72.3%) |
| Inter-model **DISAGREE** | **18 (27.7%)** |

Distribution of the 18 across chunks:

| Chunk | Disagreements |
|---|---|
| `lobbying_definitions` | 0 |
| `registration_thresholds` | 2 |
| `registration_mechanics_and_exemptions` | 1 |
| `lobbyist_spending_report` | 14 |
| `principal_spending_report` | 0 |
| `enforcement_and_audits` | 1 |

(The predecessor doc estimated "13 explicit + ~5 other"; the actual split is 14 + 4. Headline unchanged.)

---

## Three structural patterns

### Pattern A — `lobbyist_spending_report_*` row-label ambiguity (14 cells)

Every Pattern A cell has the same shape: Claude `TRUE × 3` / GPT `FALSE × 3`, with both models citing the same or overlapping sections of WI §13.68. The disagreement is **not** about what the statute says; it's about what the row label `lobbyist_spending_report_*` is asking.

#### What each model is reading

- **Claude:** "Is this information required to flow through any disclosure mechanism that touches the lobbyist?" — TRUE, because §13.68(4) requires the lobbyist to provide the info to the principal.
- **GPT:** "Is the lobbyist the filer of a spending report containing this?" — FALSE, because §13.68(1) makes the *principal* the filer; the lobbyist files only an activity report (hours, not money).

In **9 of 14** cells, GPT's justification explicitly contains a phrase like *"this duty applies to **principals**, not lobbyists; no separate lobbyist spending report is required."* In **5 of 14** GPT's wording is *"compensation/topic/etc. is reported by the principal, but no lobbyist spending report contains it."* The framing is consistent run-over-run.

#### Source-rubric provenance for the 14 rows

| Row | First introduced by | Rubrics reading | n |
|---|---|---|---|
| `lobbyist_spending_report_required` | cpi_2015 | cpi_2015; hg_2007; pri_2010; sunlight_2015 | 4 |
| `_cadence_includes_semiannual` | pri_2010 | newmark_2005; pri_2010 | 2 |
| `_categorizes_expenses_by_type` | sunlight_2015 | hg_2007; newmark_2005; newmark_2017; opheim_1991; sunlight_2015 | 5 |
| `_includes_bill_or_action_identifier` | sunlight_2015 | focal_2024; hg_2007; opheim_1991; sunlight_2015 | 4 |
| `_includes_general_issues` | pri_2010 | pri_2010 | 1 |
| `_includes_general_subject_matter` | sunlight_2015 | hg_2007; newmark_2005; newmark_2017; sunlight_2015 | 4 |
| `_includes_gifts_entertainment_transport_lodging` | pri_2010 | focal_2024; hg_2007; newmark_2005; newmark_2017; opheim_1991; pri_2010 | 6 |
| `_includes_indirect_costs` | pri_2010 | pri_2010 | 1 |
| `_includes_lobbyist_contact_info` | pri_2010 | pri_2010 | 1 |
| `_includes_principal_names` | pri_2010 | focal_2024; pri_2010 | 2 |
| `_includes_specific_bill_number` | pri_2010 | pri_2010 | 1 |
| `_includes_total_compensation` | pri_2010 | (all 8 rubrics) | 8 |
| `_includes_total_expenditures` | newmark_2017 | focal_2024; newmark_2005; newmark_2017; opheim_1991 | 4 |
| `_required_when_no_activity` | hg_2007 | hg_2007 | 1 |

All 14 rows are `status=firm`. PRI 2010 introduces 8 of 14 and is read by 13 of 14; CPI 2015 introduces the originator row of the family. Multi-rubric reach is broad — these are not edge-case rows.

#### What the source rubrics actually ask — verbatim

**CPI 2015 IND_201** (originator of `lobbyist_spending_report_required`):

> *"A YES score is earned if **lobbyists are required to file** itemized spending reports (including name of employer, lobbied issues and bill number(s) and compensation/payments received for lobbying services)."*

(`docs/historical/compendium-source-extracts/results/projections/cpi_2015_c11_projection_mapping.md` line 131.)

CPI's language is unambiguous: "lobbyists are required to file." The structural corroboration: CPI maintains `lobbyist_spending_report_required` AND `principal_spending_report_required` as separate rows (IND_201 vs IND_203). If "lobbyist spending report" meant "any report containing lobbyist info," the two rows would be redundant.

**PRI 2010 §III.E2** ("Lobbyist Disclosure (18 items)"):

> *"Are lobbyists required to disclose?"* — E2a, source for `lobbyist_spending_report_required` (PRI maps E2a onto the same row CPI #201 introduced).
>
> *"Are lobbyists required to disclose their address and phone number?"* — E2b → `lobbyist_report_includes_lobbyist_contact_info`.
>
> *"Required component of disclosure report: Direct lobbying costs (compensation)."* — E2f_i → `lobbyist_report_includes_direct_compensation`.

(`docs/historical/compendium-source-extracts/results/projections/pri_2010_projection_mapping.md` lines 630, 642, 670.)

PRI's projection-mapping doc explicitly atomizes lobbyist-side (E2) and principal-side (E1) as structural mirrors. "Are lobbyists required to disclose…?" assumes a lobbyist-as-filer model — which is the model in most US states but not in WI.

#### Verdict: Pattern A

**All 14 Pattern A cells on WI should be FALSE (under the lobbyist-as-filer reading) or unscoreable (because WI has no lobbyist-filed spending report at all — there's no "report" to score the components of).** GPT is reading the source intent. Claude is over-projecting §13.68(4)'s "lobbyist provides info to the principal" onto a row whose source-author intent is specifically about who the *filer* is.

The portal-data 13/13 corroboration from `20260601_wi_statute_vs_portal_spending.md` is not an independent validation — it's the same finding restated. The portal exposes what the lobbyist actually files (zero spending columns; only `total_hours_communicating` and `total_hours_other`), which is exactly what the source-intent reading predicts.

#### What this is NOT

This is **not** a finding that Claude is "wrong about WI law." Claude correctly identifies §13.68(1) + §13.68(4) and reads them accurately. It's a finding that Claude is **answering a different question than the row was authored to ask** — and the row's authored question is recoverable from the source rubric.

---

### Pattern B — `lobbyist_*` registration rows, principal-side rule projected (3 cells)

Same root cause as Pattern A, different answer-shape. Claude scores by projecting a principal-side or time-exemption rule onto a row labeled `lobbyist_*`; GPT abstains because WI has no lobbyist-side analog.

| Row | Claude (scored) | GPT (unscoreable) | Source rubric | Source intent |
|---|---|---|---|---|
| `lobbyist_registration_threshold_expenditure_dollars` | `500` (cites §13.64(1), §13.621(5) — both PRINCIPAL thresholds) | "statute does not set any expenditure-dollar threshold that triggers **lobbyist** registration/licensure" | newmark_2017 (rename of newmark's `expenditure_threshold_for_lobbyist_registration`) | "the expenditure dollar threshold above which the **lobbyist-definition** triggers" (newmark_2017 mapping line 152) |
| `lobbyist_filing_de_minimis_threshold_time_percent` | `10.0` (cites §13.68(1)(bn) — principal's 10%-of-time itemized-reporting threshold) | "non-lobbyist employees devoting not more than 10 hours… but no filing/reporting de minimis threshold expressed as a percentage of time" | pri_2010 | filing de minimis for lobbyist's own filing |
| `lobbyist_registration_deadline_days_after_first_lobbying` | `10` (cites §13.64(1) — principal's 10-day deadline after exceeding $500) | "statute does not specify a numeric number of days after first lobbying in which **registration** must occur" | cpi_2015 (IND_200 — the de-jure pair of an in-practice row, defined as "lobbyists register within X days of first lobbying contact" per `cpi_2015_c11_projection_mapping.md` line 119) | lobbyist's registration timeliness, not principal's |

#### Verdict: Pattern B

**All 3 Pattern B cells on WI should be unscoreable.** GPT is source-faithful. Claude is projecting principal-side dollar/time/deadline rules onto lobbyist-side rows whose source intent is unambiguously about the lobbyist's own definitional or filing thresholds.

---

### Pattern C — mis-axed row (1 cell)

`lobbying_violation_penalties_imposed_in_practice` traces to **CPI 2015 IND_209**:

> *"A 100 score is earned if **offenders are always sanctioned** when violations to reporting requirements are discovered."* (cpi_2015 mapping line 203)

CPI explicitly assigns this row to the **practical-availability axis** (cpi_2015 mapping line 201: *"practical-availability typed `int` ∈ {0, 25, 50, 75, 100}"*). The row name embeds "in practice" precisely because CPI's question is empirical, not de jure.

The v2.1 TSV registers the row as `legal+practical`. The WI Tier-1 dispatch (which runs only the legal axis) included it on the roster. On the legal axis:

- **Claude (TRUE):** read §13.69 (the statute that authorizes penalties) as evidence; scored TRUE because penalties exist in law.
- **GPT (unscoreable):** *"the bundled statute text describes available penalties and enforcement mechanisms, but does not state whether penalties are imposed 'in practice', which is an empirical/practical question not answered de jure by the statute."*

#### Verdict: Pattern C

**Neither model is wrong.** Claude reads the row as if its legal-axis sibling were `lobbying_violation_penalty_framework_exists_in_law`; GPT reads the row's actual text and correctly refuses. The row shouldn't have been on the legal-axis roster in the first place. The v2.2 fix is to split the row into two siblings:

- `lobbying_violation_penalties_authorized_in_statute` — legal axis only.
- `lobbying_violation_penalties_imposed_in_practice` — practical axis only.

Until then, this row's legal-axis read should be excluded from σ_noise and inter-model alignment computations.

---

## Structural finding: the dispatch prompt sends no row-question text

The strongest single intervention that would address Patterns A + B is upstream of any schema change.

### What `render_legal_roster` actually sends

From `scripts/tier_1_direct_read_legal_axis.py` lines 205–223:

```python
def render_legal_roster(chunk_id: str, topic: str, legal_specs: list[Any]) -> str:
    lines = [
        f"Answer all {len(legal_specs)} DE JURE (legal-axis) cells for chunk "
        f"`{chunk_id}` ({topic}):"
    ]
    for cs in legal_specs:
        cls = cs.expected_cell_class
        lines.append(
            f"- row_id={cs.row_id!r}, axis='legal', "
            f"expected_cell_class={cls.__name__}{_value_shape_hint(cls)}"
        )
    ...
```

For `lobbyist_spending_report_required`, the model literally sees:

```
- row_id='lobbyist_spending_report_required', axis='legal', expected_cell_class=BinaryCell
```

**No question text. No source quote. No disambiguation between filer and subject.** The model is reverse-engineering "what is this row asking?" from the row ID alone — which is exactly why Pattern A happens. Row IDs are a lossy compression of the original source-rubric question; for unambiguous rows, the compression is fine; for rows where filer-vs-subject matters, the compression destroys the disambiguation.

### Where the question text already exists, unused

Every projection-mapping doc at `docs/historical/compendium-source-extracts/results/projections/` carries a verbatim `Source quote` field per atomic indicator. For example:

- CPI #201 → `lobbyist_spending_report_required` source quote: *"A YES score is earned if lobbyists are required to file itemized spending reports…"*
- PRI E2a → same row, PRI's source quote: *"Are lobbyists required to disclose?"*

The compendium TSV has `compendium_row_id / cell_type / axis / rubrics_reading / n_rubrics / first_introduced_by / status / notes` columns — **no `prompt_text` or `source_quote` column**. The verbatim source-author question text is one TSV-column-addition away from being available to the model at dispatch time.

### The fix shape

1. Add `prompt_text` (and ideally `source_quote_verbatim`) columns to `compendium/disclosure_side_compendium_items_v2.tsv`.
2. Populate `prompt_text` from the projection-mapping docs' `Source quote` fields, prioritizing the `first_introduced_by` rubric.
3. Update `render_legal_roster` to include the `prompt_text` on each roster line.
4. Re-dispatch the 3 chunks containing the 17 confirmed-disagreement rows (lobbyist_spending_report + registration_thresholds + registration_mechanics_and_exemptions) on WI, both models, 3 runs each. Validation criterion: Claude collapses onto GPT's reading on the 17 cells.

Staging:
- **Narrow first.** Populate `prompt_text` for the 17 confirmed-disagreement rows only (CPI/PRI/Newmark/HG quotes are already verbatim in the mapping docs — ~30 min). Validate via re-dispatch (~$1, ~10 min). If Claude collapses, the fix is portable to the broader 181-row pass.
- **Wide second.** Populate for all 181 rows once the narrow pass validates. This is a separate session — substantive work.

---

## Closing Item 3 (Citations API)

Item 3 of `plans/20260601_post_phase3_followups.md` proposed integrating the Anthropic Citations API to recover each model's cited statute spans, hoping to distinguish "same-span/different-interpretation" disagreements from "different-spans/retrieval-bug" disagreements.

The 18-cell prior-art audit shows:

- **Pattern A (14):** Both models cite overlapping §13.68 sections. The disagreement is on what the row asks, not on what the statute says. Citations API would confirm the same-span case for these 14, which is already visible from the `cited_section` + `justification` fields in the JSONs.
- **Pattern B (3):** Claude cites principal-side statute sections; GPT abstains (cites nothing). This isn't a same-span/different-span distinction — Claude isn't reading the wrong text, it's projecting principal-side rules onto a lobbyist-labeled row. Citations API tells us Claude cited §13.64(1); we already know that. The diagnosis is row-meaning, not retrieval.
- **Pattern C (1):** Axis-mis-registration; both models reading the statute correctly within their respective framings. No model-level disagreement to adjudicate.

**Item 3 is closed.** The disambiguation lives in the prior-art layer, not the statute layer. Span-level statute citations don't help when both models already cite the right sections — the question is what the row was authored to mean, and that answer is in the rubric papers and projection-mapping docs, not in §13.68.

This **doesn't** mean Citations API is never useful for this project. A future state (MI, NC, others) could turn up disagreements where models cite genuinely non-overlapping statute sections — that's the regime where Citations API earns its keep. The WI 18-cell batch is not that regime.

---

## v2.2 schema-inputs ledger updates

Three entries added to [`v2_2_schema_inputs.md`](v2_2_schema_inputs.md):

- **Entry 2** — Pattern C axis-mis-registration on `lobbying_violation_penalties_imposed_in_practice`. Proposed split into two sibling rows.
- **Entry 3** — `prompt_text` column gap on the compendium TSV. Structural blocker on the model-disambiguation work; ledger note flags as v2.2-prerequisite, not v2.2-future.
- **Entry 4** — Source-quote provenance gap: two known renames between projection mappings and v2.1 TSV (`lobbyist_report_*` → `lobbyist_spending_report_*`; `expenditure_threshold_for_lobbyist_registration` → `lobbyist_registration_threshold_expenditure_dollars`) obscure the trail back to source intent. Proposes a `source_quote_verbatim` column to make the audit trail short.

---

## What this changes operationally

1. **Item 3 closed.** No Citations API integration in response to the WI 18.
2. **Item 6's open question on OH cross-state baseline is recontextualized.** The Phase 2 convo's σ_noise comparison was per-model; an inter-model-alignment computation (analogous to this WI 18-cell exercise) hasn't been done for OH. The optional OH re-dispatch flagged earlier could double as a parallel inter-model-disagreement audit, but only after the prompt_text fix lands — otherwise we'd be measuring the same row-label-ambiguity problem at OH instead of measuring model behavior under a sharper prompt.
3. **MI session sequencing.** The prompt_text fix should land before the MI Tier-1 dispatch, otherwise MI will repeat WI's Pattern-A / Pattern-B class of disagreement on whatever subset of compendium rows are sensitive to filer-vs-subject framing in MI's statute. If it doesn't land first, the MI run is still informative — but interpret-with-caveats.
4. **The 17-row narrow prompt_text + re-dispatch validation** is the next concrete piece of work, scope discussed at session-end. Estimated cost: ~$1, ~10 min API + ~30 min metadata population. To be picked up by a fresh agent.

---

## Reproducibility

Both enumeration scripts are saved under [`disagreement_audit/`](disagreement_audit/):

- `wi_intermodel_disagreement.py` — walks the 36 JSONs, produces the 18-cell list with full justifications per model per cell.
- `wi_disagreement_provenance.py` — joins the 18 cells against the v2.1 TSV provenance columns.

Both are pure-stdlib `uv run python` scripts. Source projection-mapping docs are at:

- `docs/historical/compendium-source-extracts/results/projections/cpi_2015_c11_projection_mapping.md`
- `docs/historical/compendium-source-extracts/results/projections/pri_2010_projection_mapping.md`
- `docs/historical/compendium-source-extracts/results/projections/newmark_2017_projection_mapping.md`
- `docs/historical/compendium-source-extracts/results/projections/sunlight_2015_projection_mapping.md`
- `docs/historical/compendium-source-extracts/results/projections/hiredguns_2007_projection_mapping.md`
