# OH lobbying chain — 2025-2026 (preview)

`OH_chain_2025_2026_preview.tsv` — a per-`(filing, position, sponsor)` chain joining the OH AER extractions (`positions[].bill_reference`) to Plural Policy's 136th GA bill sponsorships, with **§4a position-shape normalization** so subject-only positions are preserved rather than silently dropped.

**Audience:** colleagues who want OH's influence graph "principal → lobbyist → bill → sponsor" without writing the join themselves. **Preview scope** — see the parent [`releases/oh/README.md`](../README.md) for the 316-filing slice caveat and the issue #35 path to full-corpus.

---

## TL;DR

| | |
|---|---|
| **Rows** | 1,589 |
| **Columns** | 18 (see Schema) |
| **File size** | ~600 KB |
| **Distinct canonical filings contributing rows** | 140 (of 305 canonical filings; 54% of filings are position-empty in this slice) |
| **bill_class distribution** | 1,299 `bill` / 150 `subject` / 88 `jcarr` / 34 `oac_rule` / 18 `unmatched` |
| **Cross-product math** | 855 unique bill-position joins × avg 1.52 primary sponsors → 1,299 bill chain rows |
| **Most-lobbied bill** | HB 96 (FY 2026-27 budget — 73 chain rows) |

---

## Schema

18 columns, tab-separated.

| Column | Type | Example | Notes |
|---|---|---|---|
| `report_period` | str | `2025-01-01..2025-04-30` | OH AER reporting period; 3 windows/year |
| `filing_id` | str | `20250314EUPA1394434` | OH AER report ID — joins back to source provenance |
| `principal_name` | str | `Ohio Poverty Law Center` | From `LobbyingFiling.employer.name` |
| `principal_id` | str | `org-ohio-poverty-law-center` | From `LobbyingFiling.employer.id` (extraction slug; no canonical OH employer ID yet) |
| `lobbyist_name` | str | `Susan M Jagers` | From `LobbyingFiling.filer_person.name` |
| `lobbyist_id` | str | `person-susan-m-jagers` | From `LobbyingFiling.filer_person.id` (extraction slug) |
| `position_kind` | enum | `bill_referenced` / `subject_general` / `subject_hoisted_from_description` | §4a Step A: which of the three `LobbyingPosition` fields carries the subject |
| `bill_label_raw` | str | `HB 96` | The display label — `bill_reference.original_text` for bill-referenced positions; the subject text otherwise |
| `bill_label_normalized` | str | `HB 96` | Normalized form (uppercase + dot-stripped + ws-collapsed) used as the join key for `bill_class == "bill"` rows |
| `bill_class` | enum | `bill` / `subject` / `jcarr` / `oac_rule` / `unmatched` | §6 OAC table + §4a subject row (Step B classification) |
| `bill_id` | str \| null | `ocd-bill/ocd-jurisdiction/country:us/state:oh/government/sessions/136/bills/...` | Plural Policy bill ID when `bill_class == "bill"`; null otherwise |
| `bill_title` | str \| null | `Make state operating appropriations for FY 2026-27` | From `OH_136_bills.csv.title`; null for non-bill rows |
| `position_description` | str \| null | `support the appropriations` | From `LobbyingPosition.description`; null for `subject_hoisted_from_description` rows (description was hoisted into `bill_label_raw`, see §4a) |
| `num_primary_sponsors` | int | `2` | Count of primary sponsors on the bill (0 for non-bill rows) |
| `sponsor_lawmaker_id` | str \| null | `ocd-person/aaa-bird-id` | From `OH_136_bill_sponsorships.person_id` (one row per primary); null for non-bill rows |
| `sponsor_lawmaker_name` | str \| null | `Rep. Adam Bird` | From `OH_136_bill_sponsorships.name`; null for non-bill rows |
| `sponsor_role` | str \| null | `primary` | Always `primary` in v1; null for non-bill rows. v1.1 cosponsor follow-up will add `cosponsor` rows. |
| `confidence` | enum | `direct` | One of: `direct` (bill class, joined to Plural), `oac_dropped` (jcarr/oac_rule), `subject_only` (subject_general / subject_hoisted), `unmatched` (classifier flagged or join failed), `null_extraction` (empty position sentinel) |

---

## Per-row routing — what each class means

Per the §4a "Conservation implication" and §6 OAC routing tables:

| Source position | bill_class | Sponsor fields | confidence | Row count contribution |
|---|---|---|---|---|
| `bill_reference` set, label matches Plural | `bill` | populated (cross-product over primaries) | `direct` | N (one per primary) |
| `bill_reference` set, label matches Plural, bill has 0 primaries (defensive) | `bill` | null | `direct` (with `num_primary_sponsors=0`) | 1 |
| `bill_reference` set, label looks like bill (HB/SB/HR/SR/...) but doesn't join Plural | `unmatched` | null | `unmatched` | 1 |
| `bill_reference` set, label = `JC \d...` | `jcarr` | null | `oac_dropped` | 1 |
| `bill_reference` set, label = `\d+-\d+-\d+` | `oac_rule` | null | `oac_dropped` | 1 |
| `bill_reference` set, label is neither bill nor admin-rule shape | `unmatched` | null | `unmatched` | 1 |
| `bill_reference` null, `general_issue_area` set | `subject` | null | `subject_only` | 1 |
| `bill_reference` null, `general_issue_area` null, `description` set | `subject` | null | `subject_only` (with `position_kind = subject_hoisted_from_description`) | 1 |
| All three fields null (defect) | `null` (sentinel) | null | `null_extraction` | 1 |

---

## Conservation rules (read before quantitative use)

1. **Multi-primary cross-product.** A single position on a multi-primary bill emits N rows. OH allows multi-primary sponsorship on 40.8% of bills (one ceremonial House Resolution has 99 primaries). **`SUM(num_primary_sponsors)` is not a sponsor count** — it overcounts by the multiplier. Aggregate by `(filing_id, position_index)` or by `bill_label_normalized` per filing to deduplicate.

   - Example: a lobbyist files a position on `HB 96` (1 primary) and `HB 1` (2 primaries) → emits 1 + 2 = 3 chain rows. The lobbyist tracked 2 bills, not 3.

2. **`bill_class != 'bill'` rows do not join to Plural.** Subject / JCARR / OAC / unmatched rows have null `bill_id`. **Do not** `INNER JOIN OH_chain ... ON bill_id = ...` — that silently drops 290 rows (18% of the chain). Use `LEFT JOIN` or filter `WHERE bill_class = 'bill'` explicitly.

3. **Subject-only rows are real lobbying activity**, not nulls. They represent advocacy on a topic (e.g., "Public Safety", "Aging") that the lobbyist did not pin to a specific bill — common for executive-agency advocacy and ongoing-issue coalitions. **Do not filter them out** without a deliberate reason.

4. **The 18 unmatched rows are an extraction-quality canary.** Inspect with `WHERE confidence = 'unmatched'` to see the patterns. As of 2026-06-14: 8 are OAC variants the regex doesn't cover (e.g., `5180:4-5-09.1` with a colon), 8 are subject text wrongly placed in `bill_reference` (e.g., `Early Intervention`), 2 are malformed identifiers (`CB ...`).

5. **Stance not disclosed.** OH AER carries no support/oppose/monitor signal at the position level. Same as WI. The chain says "the lobbyist tracked this bill," not "for or against." (The `position_description` column sometimes hints at stance — `"support the appropriations"`, `"strike section 1"` — but is not structured.)

6. **`extract_position_label` uses `original_text` not `bill_number`** (open follow-up). If a position's `bill_reference.original_text` carries extra text (e.g., `"HB 96 BUDGET BILL"`), the join may fail and the row downgrades to `unmatched`. In the current 316-filing slice no such labels appear, so the practical impact is zero. The full-corpus run after #35 may surface a few; tracked at Phase 2 findings doc.

---

## Provenance

| | |
|---|---|
| **Source disclosure data** | OH AER extractions at `data/oh_portal/extracted/*/*/filing.json` (316 cached; gitignored — generated via `oh_portal/` per PR #33) |
| **Source bill metadata** | `data/bills/OH/136/OH_136_bills.csv` + `OH_136_bill_sponsorships.csv` (Plural Policy 136th GA export, 2026-06-07) |
| **Generating code** | [`src/lobby_analysis/allocation/oh/chain.py`](../../../src/lobby_analysis/allocation/oh/chain.py) (composer); [`classify.py`](../../../src/lobby_analysis/allocation/oh/classify.py) (Steps A+B); [`load.py`](../../../src/lobby_analysis/allocation/oh/load.py) (typed loaders + dedup helper) |
| **CLI** | `uv run python -m lobby_analysis.allocation.oh.cli materialize --extractions ... --bills ... --out releases/oh` |
| **Tests** | `tests/allocation/oh/` — 139 tests, no DB / network / real-data required |
| **Methodology** | Plan at [`docs/active/oh-portal-extraction/plans/20260611_oh_chain_composer_design.md`](../../../docs/active/oh-portal-extraction/plans/20260611_oh_chain_composer_design.md) §4 (schema), §4a (position-shape normalization, added 2026-06-14), §6 (OAC routing); per-phase findings under `results/` |
