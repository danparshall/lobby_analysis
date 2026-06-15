# 2026-06-14 — OH chain composer Phase 1 (loaders) findings

**Branch:** `oh-chain-composer` (continuing from `51a3e1e` — Phase 0 audit clean).
**Trigger:** Plan §5 Phase 1 Step C — typed DataFrame loaders for extractions + Plural Policy CSVs (the classifier Steps A+B shipped at `f59a7f9`).
**Smoke scripts:** `20260614_phase1_loaders_smoke.py` and `20260614_phase1_loaders_diags.py` (sibling files).

## What shipped

Module: `src/lobby_analysis/allocation/oh/load.py` (240 lines).
Tests: `tests/allocation/oh/test_load.py` (37 tests, all passing — full OH suite now **85/85** green).

Six public functions, all TDD-developed:

| Function | Output | Purpose |
|---|---|---|
| `load_filings(extractions_dir)` | DataFrame, one row per `LobbyingFiling` | Filing-grain view; carries `filing_obj` (typed Pydantic) for downstream typed access |
| `load_positions(extractions_dir)` | DataFrame, one row per (filing, position) | Position-grain view; carries `position_obj` (typed `LobbyingPosition`) for classifier calls |
| `load_gifts(extractions_dir)` | DataFrame, one row per (filing, gift) | Phase 3 input; carries `gift_obj` (typed `Gift`) |
| `load_plural_bills(plural_dir)` | DataFrame, one row per Plural Policy bill | Adds `identifier_norm` (uppercase, dot-stripped, whitespace-collapsed) for join with extraction labels |
| `load_plural_sponsorships(plural_dir, classification="primary")` | DataFrame, filtered sponsorships | Q2-locked default: primary-only; pass `classification=None` for all rows or `"cosponsor"` for v1.1 prep |
| `select_canonical_extraction(filings)` | DataFrame, one row per `filing_id` | Dedupes extraction-cache duplicates (most-recent mtime wins; lex `source_path` tie-break) |

**Design principle.** The model-bearing columns (`filing_obj`, `position_obj`, `gift_obj`) preserve the full Pydantic typing for downstream classifier and composer calls without re-parsing. The flat scalar columns (e.g., `principal_name`, `reporting_period_start`) are convenience views for analytics.

**Empty-input contract.** All three extraction loaders return empty DataFrames with the full column set when handed an empty directory — downstream code can depend on column shape without a "but only if non-empty" guard.

**Defective-position contract.** `load_positions` does NOT pre-filter empty positions. The classifier raises `ValueError` on empty positions (existing contract from `f59a7f9`); the loader surfaces the row and lets the classifier raise at composition time, so upstream extraction defects are visible at the right seam.

## Real-data smoke test against the 316-filing cache

| Metric | Value |
|---|---:|
| Filings loaded | **316** |
| Unique `filing_id`s | 305 |
| Duplicate-`filing_id` cases | 5 (one filing has 8 cached extractions) |
| Unique principals (`employer.name`) | 284 |
| Unique lobbyists (`filer_person.name`) | 231 |
| Total positions (sum of `n_positions`) | **1,177** |
| Total gifts (sum of `n_gifts`) | **0** |
| Total expenditures (sum of `n_expenditures`) | 0 in the slice |
| `total_expenditure is None` | 97 (30.7%) — Phase 3.5 stated-zero candidates |
| `is_current == True` | 316 (100%) |
| `filing_action` distribution | `original`: 316 (100%) |
| Plural Policy bills loaded | 2,317 |
| Plural Policy primary-only sponsorships | 4,029 (1.74 primaries / bill on average) |

Position-side classifier integration smoke (chain-composer dress rehearsal — applies `classify_position_shape` + `classify_bill_label` to each loaded position):

| `position_kind` distribution | Count | % |
|---|---:|---:|
| `bill_referenced` | 1,027 | 87.3% |
| `subject_general` | 149 | 12.7% |
| `subject_hoisted_from_description` | **1** | 0.08% |

| `bill_class` distribution | Count | % | Note |
|---|---:|---:|---|
| `bill` | 887 | 75.4% | **matches the 86.4% row-weighted smoke-test match from 06-11** (887 / 1027 bill-referenced rows) |
| `subject` | 150 | 12.7% | covers both subject_general (149) and subject_hoisted (1) |
| `jcarr` | 88 | 7.5% | OAC admin rule under JCARR review |
| `oac_rule` | 34 | 2.9% | bare OAC citations |
| `unmatched` | 18 | 1.5% | extraction-side defects (see below) |

**Conservation check.** 887 + 150 + 88 + 34 + 18 = 1,177 = total positions ✓. Every position routes to exactly one class.

**Three structural findings from the smoke test:**

### Finding 1 — 5 filing_ids have multiple cached extractions (1 has 8)

The extraction cache has duplicate extractions for 5 filing_ids: 4 with 2 each, 1 (`20250903LUPA1427844`) with **8**. Different hash subdirs under the same numeric ID:

```
data/oh_portal/extracted/1427844/{16054ea8,4766491e,6206dbc9,6a9bb30a,
                                   969b0b8a,a4aa988c,bd540187,ed3b5310}/filing.json
```

Likely a debug/test re-extraction artifact. The loader emits all 316 rows truthfully; the new `select_canonical_extraction` helper picks the most-recent `filing.json` mtime per filing_id (lex `source_path` tie-break for determinism). **Phase 2's chain composer must call `select_canonical_extraction` before composing** or it will triple-count positions for those 5 filings.

This is mechanically related to (but not the same as) issue [#36](https://github.com/danparshall/lobby_analysis/issues/36) — "doubled `_discover_dir` cache path"; that fix lives in `oh_portal/discover.py`, this dedup is downstream of any cache topology.

### Finding 2 — 0 gifts across 316 filings; Phase 3 still scoped

OH's distinctive native edge (AER Section II.A gifts + II.B meals) returned **0 rows** across the slice. Three plausible causes:

1. **Sampling artifact.** The 316-filing slice was drawn from agents-with-recent-activity per the 06-05 validation doc; nothing constrained those agents to have gifted lawmakers in the slice's reporting window.
2. **53% nil rate.** The 06-11 result doc noted 53% of cached filings are nil — half the population is structurally empty. If a typical lobbyist files quarterly with no activity, both positions and gifts will be empty.
3. **Extraction prompt scope.** The portal extraction may not actually be wired to read Section II.A/B yet. STATE_COVERAGE.md OH section confirms it IS — but the prompt brief at `src/lobby_analysis/oh_portal/extraction_brief.py` would need to be inspected to verify.

(3) is the riskiest possibility. The Phase 3 composer (`compose_gifts`) ships either way — the smoke at 0 just means the preview release's `releases/oh/gifts/` artifact is empty (release README will note this honestly). **Verification of cause (3) is a separate concern**, not blocking; if confirmed, that's a portal-extraction issue tracked separately (likely a follow-up to PR #33).

### Finding 3 — 18 unmatched bill_referenced positions are extraction-side defects

All 18 distinct unmatched labels (each appears once in the slice):

- **OAC variants the regex doesn't cover** (8 cases): labels with colons (`5180:4-5-09.1`), multi-rule strings (`5180:2-5-07, 5180:2-5-28`), "Chapter" prefix (`Chapter 5160-35`), wildcards (`5123-2-XX`).
- **Subject text wrongly placed in `bill_reference`** (8 cases): `Early Intervention`, `Accessible Housing`, `Waiver Modernization`, etc. These should have been `general_issue_area`; the extraction model conflated subject and bill-reference fields.
- **Strange identifiers** (2 cases): `CB 7/21/2025`, `CB DOH0105168`.

The classifier correctly flags all 18 as `unmatched` rather than silently joining them as bills. The chain composer should emit them as chain rows with `bill_class = "unmatched"`, `bill_id = null` — a quality-canary signal for the release README ("the 1.5% unmatched class indicates extraction quality issues we surface rather than hide").

The OAC-variant ones (those with colons + multi-rule + Chapter prefix) are a defensible regex widening for v0.1 — defer.

## What this unblocks

Phase 2 (chain composer) — has typed input DataFrames, normalized join keys, and the dedup helper. Per Q1+Q2 locks, the composer cross-products bill-referenced positions × primary-only sponsorships and emits subject/jcarr/oac_rule/unmatched rows with null sponsor fields.

Phase 3.5 (filings composer) — the 97 `total_expenditure is None` rows confirm the stated-zero normalization is load-bearing; the 316/316 `is_current==True` confirms the `is_current` forcing is consistent with the current cache.

Phase 3 (gifts composer) — runnable but its preview output is empty until extraction-side investigation resolves Finding 2.

## What stays open

- **Finding 2 (0 gifts):** report to portal-extraction track for triage. Not Phase-2-blocking; flag in the gifts README.
- **OAC regex widening (Finding 3, v0.1):** add support for `:`-subdivided rules and multi-rule strings. Pure-logic change to `classify.py`; small scope.
- **Issue #36** (`_discover_dir` doubled cache path) — orthogonal to Phase 1, but `select_canonical_extraction` is a downstream guard regardless.
