# OH lobbying gifts edge — 2025-2026 (preview, currently empty)

`OH_gifts_2025_2026_preview.tsv` — per-event `(lobbyist → lawmaker)` table covering AER **Section II.A (gifts)** and **Section II.B (meals)**. This is OH's distinctive native edge — WI and NY do not disclose per-pair lobbyist↔lawmaker $ flows.

> **EMPTY IN THIS PREVIEW — and that's an empirical finding, not a defect.** Zero gift events were extracted from the 305-filing slice. Header row only. **See "Why is this empty?" below.** A 2026-06-15 spot-check (`docs/active/oh-portal-extraction/results/20260615_gifts_spotcheck_findings.md`) ruled out the extraction-prompt-scope hypothesis: across all 305 cached filings, **zero** have any itemized content in Section II.A (Gifts) or Section II.B (Itemized Meals). All disclosed expenditure activity in this window concentrates in the non-itemized sub-$50 meal aggregate (Section II.D-Legislative / II.C-Executive). Itemized gifts appear to be essentially absent from OH 2025 lobbying disclosure. The `compose_gifts` composer is tested at 14/14 green and correctly emits rows when input filings carry gift records — the source data just doesn't have any.

---

## TL;DR

| | |
|---|---|
| **Rows** | 0 (empty body) |
| **Columns** | 10 (see Schema) |
| **File size** | 131 bytes (header only) |
| **Source: gifts** | OH AER Section II.A — gifts (`gift_type` ∈ {travel, lodging, entertainment, event_ticket, other}) |
| **Source: meals** | OH AER Section II.B — meals (`gift_type == "meal"`) |
| **Lawmaker resolution** | Open States `oh.csv` at `data/bills/OH/oh.csv` (132 legislators) |

---

## Schema

| Column | Type | Notes |
|---|---|---|
| `report_period` | str | Same convention as chain: `YYYY-MM-DD..YYYY-MM-DD` |
| `filing_id` | str | OH AER report ID |
| `principal_name` | str | The lobbyist's employer for the period |
| `lobbyist_name` | str | The filer of the AER |
| `lawmaker_name_raw` | str | Verbatim from `Gift.recipient_name` (may carry `Sen.` / `Rep.` prefix) |
| `lawmaker_id` | str \| null | Resolved to `ocd-person/...` via `oh.csv` matcher (see below); null if no match |
| `event_type` | enum | `"meal"` (Section II.B; `gift_type == "meal"`) / `"gift"` (Section II.A; anything else) |
| `description` | str \| null | From `Gift.description` |
| `amount_dollars` | float \| null | From `Gift.value` |
| `gift_date` | date \| null | From `Gift.gift_date` |

---

## Lawmaker resolution methodology

Recipient names on OH AERs typically arrive as `"Sen. John Smith"` / `"Rep. Jane Doe"` / `"John Smith"`. The resolver:

1. Strips a leading prefix matching `(Sen\.?|Rep\.?|Senator|Representative)\s+` (case-insensitive).
2. Normalizes (lowercase, collapse whitespace).
3. Looks up the result in two indexes built from `oh.csv`:
   - **Full-name index** (`oh.csv.name` lowercased): direct hit → return the `ocd-person/...` id.
   - **Surname-only index** (`oh.csv.family_name` lowercased): if the recipient gave only a single token AND that surname is **unambiguous** in oh.csv, return the id.
4. Otherwise → null.

**Ambiguous surnames return null** rather than picking arbitrarily. If `oh.csv` has both "John Smith" and "Adam Smith" and a gift recipient is `"Sen. Smith"`, the resolver declines.

If `--oh-csv` is omitted from the CLI, all `lawmaker_id` cells are null and the resolver code is skipped entirely.

---

## Why is this empty? An empirical base-rate finding

A 2026-06-15 spot-check (`docs/active/oh-portal-extraction/results/20260615_gifts_spotcheck_findings.md`) systematically scanned all 305 cached `raw.html` files and cross-referenced extraction outcomes. The result is decisive:

| Status | Count | % |
|--------|-------|----|
| Source says "No expenditures" (empty Section II) | 286 | 93.8% |
| Source has Section II content | 19 | 6.2% |
| Of those 19: any **itemized** content in II.A (Gifts) | **0** | **0%** |
| Of those 19: any **itemized** content in II.B (Itemized Meals) | **0** | **0%** |
| Of those 19: content only in the non-itemized sub-$50 aggregate | 19 | 100% |

**The extraction-prompt-scope hypothesis is ruled out.** Rule 2 of the brief at `src/lobby_analysis/oh_portal/extraction_brief.py` explicitly enumerates Section II.A (Gifts), II.B (Itemized Meals), and II.C (Dinner/Party/Function); Rule 3 covers the Section II.D non-itemized aggregate (mapped to `category="entertainment"`). The brief is correctly scoped — the source data is empty.

**This is consistent with OH lobbying disclosure behavior.** The AER form's $50 threshold for itemization captures only one specific kind of activity (named individual gift/meal recipients). Almost all disclosed activity in the 2025 window falls below that threshold and aggregates to the non-itemized sum. The 17 with-content Legislative filings + 2 with-content Executive filings all correctly extracted to `category="entertainment"` (Section II.D-Legislative / II.C-Executive aggregate) and appear in `releases/oh/filings/` via the `total_expenditure` column — not in `gifts/`, which is specifically for itemized Section II.A/B events.

**Caveat — form-type mismatch surfaced as orthogonal finding.** The spot-check also confirmed that the brief, titled "OH legislative-agent AER," is applied uniformly to all 305 filings, including 140 Executive AERs (46%) which use a 3-subsection (A/B/C) structure, not 4 (A/B/C/D). The model recovers gracefully on the current sample (zero itemized content either way), but the brief should be parameterized by form type before the full-corpus run if Executive AERs are intentionally in scope. Tracked separately; does not affect the gifts result.

**Expected at full corpus** (issue #35): given 0/305 itemized gifts in the 2025-window sample, the full-corpus rate will likely remain zero or very low single digits in absolute count. The empty-gifts release is honest output, not a provisional placeholder.

**What the gifts TSV will look like when populated** (verified via TDD fixtures in `tests/allocation/oh/test_gifts.py`):

```
report_period         | filing_id            | principal_name | lobbyist_name | lawmaker_name_raw    | lawmaker_id              | event_type | description       | amount_dollars | gift_date
2025-01-01..2025-04-30| 20250314ABC123456    | Acme Corp     | Jane Doe      | Sen. Adam Bird       | ocd-person/bird-id       | meal       | dinner            | 20.00          | 2025-02-15
2025-01-01..2025-04-30| 20250314ABC123456    | Acme Corp     | Jane Doe      | Rep. Bea Cox         | ocd-person/cox-id        | gift       | ballet ticket     | 75.00          | 2025-03-08
```

When the full-corpus run (issue #35) lands, the gifts TSV will be re-materialized and this README will be updated with real row counts.

---

## Conservation rules

1. **One row per `(filing, gift event)`.** No fan-out, no cross-product. The gifts TSV is the simplest of the three release TSVs.
2. **`event_type` is derived from `gift_type`**, not from a separate AER field. The OH AER form splits II.A/II.B by visual section; we infer the section via the `gift_type` enum — meals to II.B, everything else to II.A. Consumers wanting strict section-fidelity should join back to the source `filing.json` via `filing_id`.
3. **Null `amount_dollars` is honest, not a defect.** Some OH disclosures report description-only ("dinner at the Capitol") without a dollar value — the AER form allows this for de minimis events. Filter `WHERE amount_dollars IS NOT NULL` only when explicitly computing dollar totals.

---

## Provenance

| | |
|---|---|
| **Source** | OH AER extractions at `data/oh_portal/extracted/*/*/filing.json` (`LobbyingFiling.gifts[]`) |
| **Lawmaker roster** | `data/bills/OH/oh.csv` (Open States, 132 legislators; downloaded 2026-06-14 per Phase 0 audit) |
| **Generating code** | [`src/lobby_analysis/allocation/oh/gifts.py`](../../../src/lobby_analysis/allocation/oh/gifts.py) |
| **Tests** | `tests/allocation/oh/test_gifts.py` — 14 tests covering schema, row shape, event-type derivation, resolver hit/miss/ambiguity cases |
