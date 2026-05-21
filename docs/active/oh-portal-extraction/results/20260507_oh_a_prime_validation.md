<!-- Generated during: convos/20260522_phase_3_handoff_prep.md (skeleton) -->
<!-- Originating plan: plans/20260507_oh_a_prime_implementation.md Phase 3 step 18 -->

# (A') Hand-Validation: OH Legislative Agent AER 1427844

**Status:** Skeleton — pre-filled with ground truth from the source HTML. Awaiting `filing.json` from a Phase 3 extraction run (blocked locally on Anthropic workspace quota until 2026-06-01).

**Source HTML:** `data/oh_portal/raw/1427844/2026-05-21T18-52-26+00-00/raw.html`
(Browser-saved via VPN on 2026-05-21; sha256 + meta recorded in sidecar `meta.json`.)

**Source URL:** https://www2.jlec-olig.state.oh.us/olac/AERs/1427844/View

**Extraction run:** TBD — populate `data/oh_portal/extracted/1427844/<run_id>/filing.json` first, then this doc.

---

## How to use this doc

1. Run the extraction (full CLI from a US-network machine with a working API key, OR the local-HTML one-off from `convos/20260522_phase_3_handoff_prep.md`).
2. Open `filing.json` next to this doc.
3. For each row in the **Field-level tagging** section below, fill the **Emitted Value** column from the JSON, compare to **Expected Value**, and set the **Tag** column.
4. Compute summary stats at the bottom.
5. If `% CORRECT < 80%`, write a sentence in the convo summary on whether the issue is prompt-fixable or model-limited.

**Tag legend:**

| Tag | Meaning |
|---|---|
| **CORRECT** | Emitted value matches the source. |
| **WRONG** | Emitted value is populated but doesn't match the source (hallucination, mis-parsing, wrong cell). |
| **MISSING** | Source has a value but emitted JSON is null/empty/missing. |
| **SCHEMA-GAP** | Source has a value the schema cannot represent. Pre-flagged rows below; new ones surfaced during tagging go in the schema-gap section. |

---

## Ground truth (from source HTML)

Filing header:

| Source field | Value |
|---|---|
| Agent | Nathan Aichele |
| Employer | ARC Gaming &. Technologies *(note the typo "&." in the source — keep verbatim)* |
| Reporting Period | May–Aug 25 |
| Date Filed | 9/3/2025 |
| Confirmation | 20250903LUPA1427844 |

Section I (Legislative Agent Activity) — 4 bills:

| Bill | Title (verbatim) |
|---|---|
| HB 96 | Make state operating appropriations for FY 2026-27 |
| HB 298 | Legalize, tax internet gambling; make other Gambling Law changes |
| HB 344 | Regards electronic instant bingo, lottery terminals; levy a tax |
| SB 197 | Legalize, tax internet gambling; make other Gambling Law changes |

Section II (Expenditure Statement):

| Sub-section | Content |
|---|---|
| A. Gifts | empty |
| B. Itemized Meals and Beverages | empty |
| C. Dinner/Party/Functions (all members invited) | empty |
| D. Non-Itemized Meals and Beverages | Meals Under $50: **$20.00** / Speaking Engagements: $0.00 / National Conference Meals: $0.00 |
| Total Aggregate (A+B+C+D) | $20.00 |

---

## Field-level tagging

### Filing-level fields

| Field | Expected Value | Emitted Value | Tag | Notes |
|---|---|---|---|---|
| `state` | `"OH"` | | | |
| `filing_id` | `"20250903LUPA1427844"` (confirmation number) | | | |
| `filing_type` | `"activity_report"` | | | |
| `filer_person` | Person record for Nathan Aichele | | | |
| `filer_organization` | (see note ↓) | | | **Possible SCHEMA-GAP** — OH AERs are filed per (agent, employer) tuple but `LobbyingFiling` has no top-level "employer of the lobbyist for this filing" field. ARC Gaming might land in `filer_organization` (semantically wrong — filer is Aichele the person), or in `positions[].provenance.notes`, or be dropped. Tag whatever the model does. |
| `filer_role` | `"lobbyist"` | | | |
| `reporting_period_start` | `2025-05-01` (May 25, tri-annual window) — confirm convention | | | OH form uses "May–Aug 25" not explicit dates. Model may emit a different convention. |
| `reporting_period_end` | `2025-08-31` (Aug 25, tri-annual window) | | | Same caveat. |
| `filed_date` | `2025-09-03` | | | |
| `is_current` | `true` | | | |
| `filing_action` | `"original"` | | | |
| `total_compensation` | `null` (not on OH form) | | | |
| `total_reimbursements` | `null` (not on OH form) | | | |
| `total_other_costs` | `null` or `20.00` (interpretation) | | | OH Total Aggregate D = $20 maps to "other_costs" *if* the model reads it as gifts/entertainment/travel/lodging totals. Acceptable either way; note interpretation. |
| `total_expenditure` | `20.00` | | | |
| `total_income` | `null` | | | |
| `income_per_client` | `null` | | | |
| `is_itemized` | `false` (Section D is non-itemized aggregate) | | | |
| `raw_text` | full AER text or null | | | Brief doesn't request this. Either is fine; tag CORRECT either way. |

### `positions[]` (expected: 4 rows, one per bill)

| Bill | Expected `bill_reference` | Expected `description` | Expected `position` | Emitted? | Tag |
|---|---|---|---|---|---|
| HB 96 | bill_id="HB 96" | "Make state operating appropriations for FY 2026-27" | `null` (OH form doesn't collect stance) | | |
| HB 298 | bill_id="HB 298" | "Legalize, tax internet gambling; make other Gambling Law changes" | `null` | | |
| HB 344 | bill_id="HB 344" | "Regards electronic instant bingo, lottery terminals; levy a tax" | `null` | | |
| SB 197 | bill_id="SB 197" | "Legalize, tax internet gambling; make other Gambling Law changes" | `null` | | |

**Brief-compliance checks for each position row:**
- `position` field should be `null` (brief rule 1 — don't invent stance)
- No fabricated `outcomes_sought`, `general_issue_area` unless source states it

### `expenditures[]` (expected: 1 row — Section D collapse per brief rule 3)

| Expected field | Expected value | Emitted value | Tag |
|---|---|---|---|
| `category` | `"entertainment"` | | |
| `amount` | `20.00` | | |
| `currency` | `"USD"` | | |
| `recipient_name` | `null` (brief rule 3 — don't invent) | | |
| `expenditure_date` | `null` (not stated) | | |
| `purpose` | `null` or "non-itemized meals under $50" | | |

**WRONG-flag triggers:**
- Model emits 3 separate rows for Section D's sub-categories → violates brief rule 3 → tag WRONG (the schema gap is real, but the brief said collapse)
- Model emits expenditure rows for empty Sections A/B/C → tag WRONG (hallucinated)
- Model invents a recipient name → tag WRONG

### `engagements[]` and `gifts[]`

| List | Expected | Emitted | Tag |
|---|---|---|---|
| `engagements` | `[]` (OH form doesn't collect contact-level data) | | |
| `gifts` | `[]` (Section A is empty for this filing) | | |

---

## Pre-flagged schema gaps

These were identified pre-extraction and recorded in `results/20260507_a_prime_sample_selection.md`. List again here for the v1.4 conversation; expect the extraction to surface them implicitly.

1. **Section II.D three-sub-row structure.** OH's non-itemized aggregate splits across Meals Under $50 / Speaking Engagements / National Conference Meals. `LobbyingExpenditure.category` is a flat Literal — can't represent the sub-breakdown. The brief collapses to one `entertainment` row with the total. **Common shape for real filings, not edge case.**
2. **`(agent, employer)` filing tuple.** OH AERs are filed per (agent, employer) engagement. `LobbyingFiling` has no top-level "employer for this filing" field — only `filer_person` xor `filer_organization`. May need a `filer_employer` field or to model the engagement as a separate entity. **Open until the colleague's extraction lands and we see where the model puts ARC Gaming.**

(Append new gaps surfaced during tagging here.)

---

## Summary stats (fill after tagging)

| Tag | Count | % of populated rows |
|---|---|---|
| CORRECT | | |
| WRONG | | |
| MISSING | | |
| SCHEMA-GAP | | |
| **Total populated rows** | | 100% |

**Decision gate:** % CORRECT ≥ 80% → graduate to (B'). % CORRECT < 80% → write one paragraph in the convo summary on prompt-fixable vs model-limited; do not graduate.

---

## What changes go where

- New schema gaps → append above; surface as v1.4 proposal text in the convo summary (NOT the schema, NOT a unilateral bump).
- Brief-violation patterns (model ignored a rule) → list in the convo summary's "iteration notes" section.
- One-off model errors (transcription typos, formatting) → tag WRONG, no further action; opus-4-7 doesn't need prompt tuning for stochastic errors at n=1.
