# v2.2 schema design inputs — rows where the model agrees but v2.1 can't represent the answer

**Purpose:** Structured record of cases where, on real statute extraction runs, the model(s) agree on what the statute says, but the v2.1 typed-cell schema cannot faithfully represent the answer. This is the corpus for the v2.2 schema redesign — see the 2026-05-24 gather-first pivot in repo-root `STATUS.md`.

**Scope:** This ledger is **observation-only**, not patch-driven. Each entry captures: the cell, the current v2.1 constraint, the observed model emission(s), the proposed v2.2 widening, and the source evidence. v2.1 stays locked; entries here become the design inputs when the v2.2 design pass runs.

**Cross-reference (naming):** [`compendium/NAMING_CONVENTIONS.md`](../../../../compendium/NAMING_CONVENTIONS.md) §7 (three-threshold framework, `_threshold_<measure>_<unit>` suffix). The row-ID `<unit>` suffix and the cell-class `unit` enum **content** are distinct surfaces: §7 governs the row-ID; this ledger records gaps in the enum content surface (`models_v2/cells.py`'s `TimeUnitLiteral`, etc.).

---

## Entry 1 — `TimeThresholdCell.unit` literal-enum gap (WI §13.62(11))

### Cell

| Field | Value |
|---|---|
| Cell class | `TimeThresholdCell` |
| Field | `unit: TimeUnitLiteral \| None` |
| Source: | `src/lobby_analysis/models_v2/cells.py` (line 186) |
| Reachable from row | `lobbyist_registration_threshold_time_percent` (legal axis) |

### Current v2.1 allowed values

```python
TimeUnitLiteral = Literal[
    "hours_per_quarter", "hours_per_year", "days_per_year", "percent_of_work_time"
]
```

(`src/lobby_analysis/models_v2/cells.py` line 171–173.)

### Observed model emissions

Both Claude opus-4-7 and GPT-5.2, **all 6/6 runs** on the WI 2025 statute bundle (Phase 2, 2026-06-01), emitted `unit="days_per_reporting_period"` for `lobbyist_registration_threshold_time_percent`, citing WI Stat. §13.62(11):

> An individual whose duties are not limited exclusively to lobbying is a lobbyist only if he or she makes lobbying communications on each of at least **5 days within a reporting period**.

Pydantic literal validation rejects with `literal_error`: `Input should be 'hours_per_quarter', 'hours_per_year', 'days_per_year' or 'percent_of_work_time' [type=literal_error, input_value='days_per_reporting_period', input_type=str]`.

### Proposed v2.2 additions (minimum)

- `days_per_reporting_period` — WI's structure (5 days per principal's 6-month reporting period). Generalizes to any state whose lobbyist-status definition counts qualifying days within the filing cadence.
- `days_per_6_month_reporting_period` — if a stricter encoding is wanted (when the reporting period itself is specified by statute as 6-monthly, this preserves the period length).

### Candidate additions (need more evidence before pinning)

- `days_per_quarter` — parallel to `hours_per_quarter`.
- `days_per_session` — for legislative-session-bounded thresholds (some states key on biennial session days).
- `days_unspecified_period` — escape hatch for statutes that say "N days" without naming the period; better than forcing one of the above.

### Source statute citation

WI Stat. §13.62(11) "Lobbyist" definition, paragraph beginning "If an individual's duties are not limited exclusively to lobbying…"

### Source evidence files

6 JSONs, all errored on this cell with identical mechanism:

- `docs/active/wi-tier1-direct-read/results/tier_1/WI_2025/claude-opus-4-7__registration_thresholds__run{1,2,3}.json`
- `docs/active/wi-tier1-direct-read/results/tier_1/WI_2025/gpt-5.2-2025-12-11__registration_thresholds__run{1,2,3}.json`

The `errors[0].arguments` dict in each contains the full `record_cell` arguments the model emitted, including the exact `value={"magnitude": 5, "unit": "days_per_reporting_period"}` shape.

### Open design question — single source of truth or per-cell?

`TimeUnitLiteral` is reused on both `TimeThresholdCell` and `TimeSpentCell` (same `cells.py` line 200). When v2.2 lands, the question is whether unit enums should consolidate to a single canonical enum source (e.g., a shared `UnitsRegistry` typed module) or stay per-cell. **The gather-first phase doesn't need to decide this**; record it here so the v2.2 design pass has the question pre-loaded.

### Cross-row coordination note

The row `lobbyist_registration_threshold_time_percent` has `_time_percent` in its row-ID suffix per §7 of NAMING_CONVENTIONS.md — but the WI evidence shows the actual unit isn't a percent at all; it's day-count-per-period. If v2.2 adds `days_per_reporting_period`, the row-ID's `_time_percent` suffix is misleading for statutes (like WI) that use day-count thresholds. Two options for the v2.2 design pass to weigh:

- (a) Keep the row-ID `_time_percent` and accept that the suffix names the *family of measure* (time-based threshold), with `unit` field carrying the actual unit.
- (b) Split into two rows: `_time_percent` (for percent-of-work-time states) and `_time_days_per_period` (for day-count states), with each row's `unit` enum constrained to the matching shape.

(a) is simpler; (b) is more honest. **No decision needed now** — flagging for v2.2.

### How this entry was opened

Predecessor plan: [`../plans/20260601_post_phase3_followups.md`](../plans/20260601_post_phase3_followups.md) Item 2.
Session that opened it: [`../convos/20260601_phase3_followups_execution.md`](../convos/20260601_phase3_followups_execution.md).
Companion: Item 1 (Fix A dict-shape coverage) cleared the magnitude-coercion side of this same cell's two-error stack; the enum gap is the residual.

---

## Entry 2 — Axis-mis-registration on `lobbying_violation_penalties_imposed_in_practice`

### Row

| Field | Value |
|---|---|
| Compendium row | `lobbying_violation_penalties_imposed_in_practice` |
| TSV registration | `axis = legal+practical` (line in `compendium/disclosure_side_compendium_items_v2.tsv`) |
| Originating rubric | CPI 2015 IND_209 (`first_introduced_by = cpi_2015_c11_projection_mapping.md`) |

### Current v2.1 state

The row appears on the **legal-axis roster** of the `enforcement_and_audits` chunk and is dispatched to the model under the legal-axis prompt ("DE JURE: what the statute REQUIRES, PERMITS, or DEFINES").

### Source-rubric intent

CPI 2015 IND_209's source quote (`cpi_2015_c11_projection_mapping.md` line 203):

> *"A 100 score is earned if **offenders are always sanctioned** when violations to reporting requirements are discovered. A 50 score is earned if offenders are generally sanctioned, but documented evidence show some exceptions exist. A 0 score is earned if sanctions are rarely or never imposed even though they are necessary."*

CPI explicitly assigns this row to the **practical-availability axis** (cpi_2015 mapping line 201: `practical-availability typed int ∈ {0, 25, 50, 75, 100}`). The row name embeds "in practice" because CPI's question is empirical: are penalties actually imposed when violations are found?

### Observed model behavior on WI

Both models, every run, stable within model — and disagreeing across models:

- **Claude (TRUE × 3):** reads §13.69 (the statute that authorizes monetary forfeitures, criminal fines, Class H felony liability) and scores TRUE because penalties exist in law.
- **GPT (unscoreable × 3):** *"the bundled statute text describes available penalties and enforcement mechanisms, but does not state whether penalties are imposed 'in practice', which is an empirical/practical question not answered de jure by the statute."*

**Neither model is wrong** for what each is reading. Claude treats the row as if its legal-axis sibling were `lobbying_violation_penalty_framework_exists_in_law`; GPT reads the row's actual text and correctly refuses.

### Proposed v2.2 fix

Split into two sibling rows:

- `lobbying_violation_penalties_authorized_in_statute` — legal axis only. Reads as "does the statute create a penalty framework for reporting violations?"
- `lobbying_violation_penalties_imposed_in_practice` — practical axis only. Preserves CPI IND_209's empirical question.

### Interim handling

Until the v2.2 split lands, this row's legal-axis emission should be **excluded** from σ_noise and inter-model alignment computations on legal-axis runs. The "disagreement" on this cell is an artifact of the mis-registered axis, not model behavior worth measuring.

### Source evidence files

- `docs/active/wi-tier1-direct-read/results/tier_1/WI_2025/claude-opus-4-7__enforcement_and_audits__run{1,2,3}.json`
- `docs/active/wi-tier1-direct-read/results/tier_1/WI_2025/gpt-5.2-2025-12-11__enforcement_and_audits__run{1,2,3}.json`
- `docs/historical/compendium-source-extracts/results/projections/cpi_2015_c11_projection_mapping.md` lines 197–204.

### How this entry was opened

Session: [`../convos/20260603_statute_disagreement_prior_art_review.md`](../convos/20260603_statute_disagreement_prior_art_review.md). Detailed writeup: [`20260603_prior_art_adjudication_of_18_disagreements.md`](20260603_prior_art_adjudication_of_18_disagreements.md) Pattern C.

---

## Entry 3 — `prompt_text` column gap on the compendium TSV

### Row / context

Affects every row in `compendium/disclosure_side_compendium_items_v2.tsv` (currently 181 rows). This is a **schema-level** gap, not a per-row gap.

### Current v2.1 state

The TSV columns are: `compendium_row_id / cell_type / axis / rubrics_reading / n_rubrics / first_introduced_by / status / notes`. There is **no `prompt_text`, `source_quote_verbatim`, or equivalent** column carrying the row's authored question text.

### Observed consequence

The Tier-1 dispatch script `scripts/tier_1_direct_read_legal_axis.py` (`render_legal_roster`, lines 205–223) constructs the per-row prompt from `row_id`, `axis`, and `expected_cell_class` only. For `lobbyist_spending_report_required`, the model literally sees:

```
- row_id='lobbyist_spending_report_required', axis='legal', expected_cell_class=BinaryCell
```

No question text reaches the model. The model is reverse-engineering "what is this row asking?" from the row ID alone — which works for unambiguous rows but breaks for rows where the ID is structurally ambiguous about who-the-filer-is-vs-who-the-subject-is. WI Tier-1 surfaced 17 cells (Patterns A + B in the 2026-06-03 disagreement-audit writeup) where this exact ambiguity caused inter-model disagreement.

The verbatim source-rubric questions already exist in `docs/historical/compendium-source-extracts/results/projections/*.md` under `Source quote` fields per atomic indicator. They are not currently surfaced through the compendium pipeline.

### Proposed v2.2 additions

Add two columns to the TSV:

- `prompt_text` — the question the model should answer for this row, in the source-author's voice when possible. For multi-rubric rows, prefer the originator (`first_introduced_by`) rubric's wording; if multiple rubrics phrase the question meaningfully differently, document the variance in `notes`.
- `source_quote_verbatim` — the original source-rubric quote text, copied verbatim from the projection-mapping doc, with rubric/section attribution.

Update `render_legal_roster` (and any analogous Tier-0 / Tier-2 renderers) to include `prompt_text` on each roster line.

### Why this is v2.2-prerequisite, not v2.2-future

The gather-first pivot (2026-05-24) depends on per-(state, vintage, question) answers being collected reliably. Currently, the **question** half of (question → answer) is being lossy-compressed through row IDs. The MI run is the next state in the pipeline; running MI without this fix will reproduce the WI 17-cell Pattern A/B class on whatever subset of compendium rows are sensitive to filer-vs-subject framing in MI's statute. Fixing this before MI dispatch is the minimum-cost intervention with the highest-confidence payoff.

### Suggested staging

- **Narrow.** Populate `prompt_text` for the 17 WI confirmed-disagreement rows from their `first_introduced_by` rubric's source quote. Re-dispatch the 3 affected chunks on WI (~$1, ~10 min). Validation criterion: Claude collapses onto GPT's reading on those 17 cells.
- **Wide.** If narrow validates, populate `prompt_text` for the remaining ~164 rows in a separate session (substantive — most of a session). If narrow doesn't validate, surface the deeper issue before going wider.

### Source evidence files

Dispatch script: `scripts/tier_1_direct_read_legal_axis.py` lines 205–223.
TSV header: `compendium/disclosure_side_compendium_items_v2.tsv` line 1.
Source quotes already extant: `docs/historical/compendium-source-extracts/results/projections/*.md` — `Source quote` field on each indicator entry.

### How this entry was opened

Session: [`../convos/20260603_statute_disagreement_prior_art_review.md`](../convos/20260603_statute_disagreement_prior_art_review.md). Detailed writeup: [`20260603_prior_art_adjudication_of_18_disagreements.md`](20260603_prior_art_adjudication_of_18_disagreements.md) "Structural finding" section.

---

## Entry 4 — Source-quote provenance gap (compendium ID renames hide source intent)

### Row / context

Two known cases where compendium row IDs were renamed between the projection-mapping docs and the v2.1 TSV, in ways that preserve source intent but obscure the trail back to it:

1. **PRI 2010 §III.E2 row family.** PRI's projection mapping uses `lobbyist_report_*` (e.g., `lobbyist_report_includes_lobbyist_contact_info` for E2b, `lobbyist_report_includes_principal_names` for E2c, `lobbyist_report_includes_direct_compensation` for E2f_i). The v2.1 TSV registers these as `lobbyist_spending_report_*`. The rename *adds specificity* ("spending"), which makes the row even more filer-centric than PRI's original "any kind of report" framing — source-intent-preserving but the rename should have been documented.
2. **Newmark 2017 expenditure threshold.** Newmark's mapping uses `expenditure_threshold_for_lobbyist_registration` (`newmark_2017_projection_mapping.md` line 150, "the expenditure dollar threshold above which the lobbyist-definition triggers"). The v2.1 TSV registers it as `lobbyist_registration_threshold_expenditure_dollars`. The rename reorders to put `lobbyist_` first — same intent, harder to grep for.

### Current v2.1 state

The TSV's `first_introduced_by` column points to the projection-mapping doc, but recovering the original row ID + the rationale for the rename requires opening the doc and grepping. There is no inline trace.

### Observed consequence

Auditing the 18 WI disagreements required cross-referencing each row through `first_introduced_by` → mapping doc → `Source quote` field. Two renames in this audit (one for Pattern A, one for Pattern B) had to be hand-traced. For an audit of all 181 rows, this would compound.

### Proposed v2.2 additions

Two options, not mutually exclusive:

- (a) Add a `source_quote_verbatim` column (paired with Entry 3's `prompt_text`). This makes the source intent recoverable from the TSV directly, regardless of rename history.
- (b) Add a `source_row_id_history` column carrying the original row ID(s) from the source rubric, when different from the current ID. E.g., `lobbyist_report_includes_lobbyist_contact_info (pri E2b)`. Less load-bearing than (a) but makes the rename history audit-able.

(a) is the higher-value of the two; (b) is cheaper and orthogonal.

### Source evidence files

- `docs/historical/compendium-source-extracts/results/projections/pri_2010_projection_mapping.md` lines 638, 646, 654, 670, 678 (PRI's `lobbyist_report_*` row IDs).
- `docs/historical/compendium-source-extracts/results/projections/newmark_2017_projection_mapping.md` line 150 (Newmark's `expenditure_threshold_for_lobbyist_registration`).
- `compendium/disclosure_side_compendium_items_v2.tsv` (current v2.1 IDs).

### How this entry was opened

Session: [`../convos/20260603_statute_disagreement_prior_art_review.md`](../convos/20260603_statute_disagreement_prior_art_review.md). Detailed writeup: [`20260603_prior_art_adjudication_of_18_disagreements.md`](20260603_prior_art_adjudication_of_18_disagreements.md) "Architectural side-note" (in the QQ exchange).

---

## Future entries

Add new entries below as concrete v2.1 representation gaps surface across states. Each entry should carry: the cell + field, the v2.1 constraint, the observed emission, the proposed widening, the source statute citation, the source evidence files, and any cross-row coordination notes.
