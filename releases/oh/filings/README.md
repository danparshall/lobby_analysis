# OH lobbying filings table — 2025-2026 (preview)

`OH_filings_2025_2026_preview.tsv` — one row per canonical OH AER filing, hosting the two filing-grain normalizations that have no home in the position-grain chain TSV or the per-event gifts TSV.

**Audience:** analysts wanting per-filing summary stats (total_expenditure, action, super­session) plus the two normalizations applied so downstream aggregations are safe.

---

## TL;DR

| | |
|---|---|
| **Rows** | 305 (one per canonical AER extraction; 11 dupe-cached extractions for 5 filing_ids deduped via `select_canonical_extraction`) |
| **Columns** | 14 (see Schema) |
| **File size** | ~220 KB |
| **Stated-zero normalizations applied** | 97 of 305 filings (`total_expenditure: None + expenditures==[]` → `0.0`) |
| **is_current forcings applied** | 0 in this slice (all 305 filings already carry `is_current=True`; rule is a no-op invariant guard) |

---

## Schema

| Column | Type | Notes |
|---|---|---|
| `filing_id` | str | OH AER report ID |
| `report_period` | str | Same `start..end` format as chain + gifts |
| `principal_name` | str | `LobbyingFiling.employer.name` |
| `principal_id` | str | Derived deterministically from `principal_name` (`org-{slug}`). Mirrors the chain TSV's convention for join consistency — see `chain/README.md` §"Entity-ID derivation". |
| `lobbyist_name` | str | `LobbyingFiling.filer_person.name` |
| `lobbyist_id` | str | Derived from `lobbyist_name` (`person-{slug}`). Same convention as chain TSV. |
| `total_expenditure` | float | **Post-stated-zero-normalize.** See Normalization 1 below. Never null when `expenditures` is empty. |
| `is_current` | bool | **Post-force.** See Normalization 2 below. |
| `filing_action` | enum | `original` / `amendment` / `termination` / `withdrawal` |
| `supersedes` | str \| null | `filing_id` of the prior version (Epton-pattern amendment chain) |
| `n_positions` | int | Length of `positions[]` on the canonical extraction |
| `n_gifts` | int | Length of `gifts[]` |
| `n_expenditures` | int | Length of `expenditures[]` |
| `extraction_warnings` | str | JSON-serialized list of `LobbyingFiling.extraction_warnings` — free-text notes from the extractor for un-schema-able source content. Inspect for cases the chain composer can't represent. |

---

## Normalization 1 — stated-zero

```
IF total_expenditure IS NULL AND len(expenditures) == 0:
    total_expenditure = 0.0
```

Rationale: a nil OH AER (no expenditures filed) sets `total_expenditure` to None by default, which is semantically *"no value disclosed"*. But structurally, "no expenditures filed" IS the value — it's zero. Downstream `SUM(total_expenditure)` should treat these filings as $0, not null. The normalization makes that safe without consumers having to write `COALESCE(total_expenditure, 0.0)`.

**Strict guard.** The normalization fires **only** on the `(None, empty)` pair. `(None, non-empty)` is an upstream extraction inconsistency (total missing but line items present) — that case stays null so analysts see the defect. The strict guard is tested at `tests/allocation/oh/test_filings.py::TestStatedZeroNormalization::test_none_with_non_empty_expenditures_NOT_normalized`.

In this preview slice: **97 of 305 canonical filings** are nil-zero — without the normalization, downstream sums on `total_expenditure` would coerce-or-null those out incorrectly.

---

## Normalization 2 — is_current default-forcing

```
IF filing_action == 'original' AND supersedes IS NULL:
    is_current = True
```

Rationale: a filing that is `original` AND has no supersession link is structurally the latest version of itself. The AER extraction occasionally leaves `is_current` default-unset (False) on this combination; the forcing rule enforces the structural invariant.

**Strict guard.** Both conjuncts are required. `filing_action == 'amendment'` (regardless of supersedes) does NOT trigger forcing — those filings legitimately have their own `is_current` semantics depending on which amendment in the chain is "latest." Likewise `original` with a non-null `supersedes` is suspicious and we don't force.

In this preview slice: **0 forcings applied.** All 305 canonical filings already carry `is_current=True`. The rule is a no-op invariant guard against future extraction drift.

---

## Conservation rules

1. **One row per `filing_id`.** Duplicate cached extractions are deduped by `select_canonical_extraction` (most-recent mtime wins; lex `source_path` tiebreaker). 11 non-canonical extractions across 5 filing_ids were dropped from this slice — see `docs/active/oh-portal-extraction/results/20260614_phase1_loaders_findings.md` Finding 1.

2. **`total_expenditure` is the post-normalize value.** If you want the raw extracted value (including nulls), read the source `filing.json` via `filing_id`.

3. **`extraction_warnings` is verbatim from the extractor.** It carries content that has no schema slot — usually free-text notes about format anomalies, period-label inference, or executive-agency vs legislative AER distinctions. Useful for triage; not load-bearing for the chain.

---

## Provenance

| | |
|---|---|
| **Source** | OH AER extractions at `data/oh_portal/extracted/*/*/filing.json` |
| **Originating findings** | [`docs/active/leave-behind-prep/results/20260613_mini_swap_quality_gate_findings.md`](../../../docs/active/leave-behind-prep/results/20260613_mini_swap_quality_gate_findings.md) — the 2026-06-13 mini-swap session that surfaced both normalizations |
| **Generating code** | [`src/lobby_analysis/allocation/oh/filings.py`](../../../src/lobby_analysis/allocation/oh/filings.py) |
| **Tests** | `tests/allocation/oh/test_filings.py` — 14 tests covering both normalizations + strict-guard cases + summary stats |
