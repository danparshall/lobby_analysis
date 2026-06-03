<!-- Generated during: convos/20260522_phase_3_handoff_prep.md (skeleton) -->
<!-- Originating plan: plans/20260507_oh_a_prime_implementation.md Phase 3 step 18 -->

# (A') Hand-Validation: OH Legislative Agent AER 1427844

**Status:** ✅ COMPLETE — validated 2026-06-03 against a real end-to-end extraction run. **93.5% CORRECT (29/31 rows), 0 WRONG → graduates to (B').**

**Source HTML:** `data/oh_portal/raw/1427844/2026-06-03T19-31-18+00-00/raw.html`
(Live-fetched from a US network on 2026-06-03 — `requests.get` succeeded directly, no VPN/browser-save needed. The earlier VPN/timeout blocker was an outside-US connectivity issue, not a portal defense. Content is byte-identical in substance to Amina's 2026-05-21 browser-save: same agent, employer, 4 bills, $20 Section II.D aggregate.)

**Source URL:** https://www2.jlec-olig.state.oh.us/olac/AERs/1427844/View

**Extraction run:** `data/oh_portal/extracted/1427844/bd540187/filing.json`
(run_id `bd540187`, model `claude-opus-4-7`, prompt `oh-portal-extraction/v0.1:fa1231278877a1d3`, 8.06s, run on branch `oh-portal-aprime-batch` off `oh-portal-extraction`.)

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
| `state` | `"OH"` | `"OH"` | **CORRECT** | |
| `filing_id` | `"20250903LUPA1427844"` (confirmation number) | `"20250903LUPA1427844"` | **CORRECT** | Also set `id="oh-aer-20250903LUPA1427844"`. |
| `filing_type` | `"activity_report"` | `"activity_report"` | **CORRECT** | |
| `filer_person` | Person record for Nathan Aichele | `{name: "Nathan Aichele", source_state: "OH", id: "oh-person-nathan-aichele"}` | **CORRECT** | |
| `filer_organization` | (see note ↓) | `null` | **SCHEMA-GAP** | Confirms pre-flagged gap #2. Model correctly declined to misfile the employer into `filer_organization` (that field denotes the *filer*; here the filer is Aichele the person). But "ARC Gaming &. Technologies" appears **nowhere** in the output — not in a notes field, not in provenance. The employer is silently dropped. Real data loss; v1.4 needs a `filer_employer`/engagement slot. |
| `filer_role` | `"lobbyist"` | `"lobbyist"` | **CORRECT** | |
| `reporting_period_start` | `2025-05-01` (May 25, tri-annual window) — confirm convention | `2025-05-01` | **CORRECT** | Model inferred the tri-annual window start from "May–Aug25" exactly as expected. |
| `reporting_period_end` | `2025-08-31` (Aug 25, tri-annual window) | `2025-08-31` | **CORRECT** | |
| `filed_date` | `2025-09-03` | `2025-09-03` | **CORRECT** | |
| `is_current` | `true` | `true` | **CORRECT** | |
| `filing_action` | `"original"` | `"original"` | **CORRECT** | |
| `total_compensation` | `null` (not on OH form) | `null` | **CORRECT** | |
| `total_reimbursements` | `null` (not on OH form) | `null` | **CORRECT** | |
| `total_other_costs` | `null` or `20.00` (interpretation) | `null` | **CORRECT** | Model routed the $20 to `total_expenditure` instead of `total_other_costs`. Acceptable per skeleton. |
| `total_expenditure` | `20.00` | `20.0` | **CORRECT** | Matches Section II.D Total Aggregate. |
| `total_income` | `null` | `null` | **CORRECT** | |
| `income_per_client` | `null` | `null` | **CORRECT** | |
| `is_itemized` | `false` (Section D is non-itemized aggregate) | `null` | **MISSING** | True value is `false` (form header reads "Non-Itemized"); model abstained rather than inferring. Defensible (no explicit itemized flag on the form) but the determinable value was left null. Low severity; candidate for a brief tweak ("set `is_itemized=false` when only the Non-Itemized aggregate is populated"). |
| `raw_text` | full AER text or null | `null` | **CORRECT** | Brief doesn't request it; null is fine. |

### `positions[]` (expected: 4 rows, one per bill)

| Bill | Expected `bill_reference` | Expected `description` | Expected `position` | Emitted? | Tag |
|---|---|---|---|---|---|
| HB 96 | bill_id="HB 96" | "Make state operating appropriations for FY 2026-27" | `null` (OH form doesn't collect stance) | `bill_number="HB 96"`, `original_text="HB 96"`, desc exact, `position=null` | **CORRECT** |
| HB 298 | bill_id="HB 298" | "Legalize, tax internet gambling; make other Gambling Law changes" | `null` | `bill_number="HB 298"`, desc exact, `position=null` | **CORRECT** |
| HB 344 | bill_id="HB 344" | "Regards electronic instant bingo, lottery terminals; levy a tax" | `null` | `bill_number="HB 344"`, desc exact, `position=null` | **CORRECT** |
| SB 197 | bill_id="SB 197" | "Legalize, tax internet gambling; make other Gambling Law changes" | `null` | `bill_number="SB 197"`, desc exact, `position=null` | **CORRECT** |

Schema note (not a defect): the skeleton's expected `bill_id="HB 96"` shorthand maps to `bill_reference.bill_number` / `original_text` in the actual `BillReference` schema. Model populated both correctly; `open_states_id`, `session`, `chamber` left null (not on the form). All four `position`, `general_issue_area`, `outcomes_sought`, `provenance` fields null — brief rule 1 honored (no invented stance).

**Brief-compliance checks for each position row:**
- `position` field should be `null` (brief rule 1 — don't invent stance)
- No fabricated `outcomes_sought`, `general_issue_area` unless source states it

### `expenditures[]` (expected: 1 row — Section D collapse per brief rule 3)

| Expected field | Expected value | Emitted value | Tag |
|---|---|---|---|
| `category` | `"entertainment"` | `"entertainment"` | **CORRECT** |
| `amount` | `20.00` | `20.0` | **CORRECT** |
| `currency` | `"USD"` | `"USD"` | **CORRECT** |
| `recipient_name` | `null` (brief rule 3 — don't invent) | `null` | **CORRECT** |
| `expenditure_date` | `null` (not stated) | `null` | **CORRECT** |
| `purpose` | `null` or "non-itemized meals under $50" | `null` | **CORRECT** |

✅ Exactly **one** expenditure row emitted — Section D collapsed per brief rule 3 (no 3-way split into Meals/Speaking/National Conference sub-rows). No hallucinated rows for the empty Sections A/B/C. No invented recipient. All WRONG-flag triggers avoided.

**WRONG-flag triggers:**
- Model emits 3 separate rows for Section D's sub-categories → violates brief rule 3 → tag WRONG (the schema gap is real, but the brief said collapse)
- Model emits expenditure rows for empty Sections A/B/C → tag WRONG (hallucinated)
- Model invents a recipient name → tag WRONG

### `engagements[]` and `gifts[]`

| List | Expected | Emitted | Tag |
|---|---|---|---|
| `engagements` | `[]` (OH form doesn't collect contact-level data) | `[]` | **CORRECT** |
| `gifts` | `[]` (Section A is empty for this filing) | `[]` | **CORRECT** |

---

## Pre-flagged schema gaps

These were identified pre-extraction and recorded in `results/20260507_a_prime_sample_selection.md`. List again here for the v1.4 conversation; expect the extraction to surface them implicitly.

1. **Section II.D three-sub-row structure.** OH's non-itemized aggregate splits across Meals Under $50 / Speaking Engagements / National Conference Meals. `LobbyingExpenditure.category` is a flat Literal — can't represent the sub-breakdown. The brief collapses to one `entertainment` row with the total. **Common shape for real filings, not edge case.** — **CONFIRMED at extraction.** Model collapsed to one $20 `entertainment` row per brief rule 3. No numeric loss *for this filing* (Speaking=$0, National Conference=$0), but the sub-category provenance is gone. A filing with non-zero Speaking/Conference amounts would lose the breakdown. Still the leading v1.4 candidate.
2. **`(agent, employer)` filing tuple.** OH AERs are filed per (agent, employer) engagement. `LobbyingFiling` has no top-level "employer for this filing" field — only `filer_person` xor `filer_organization`. May need a `filer_employer` field or to model the engagement as a separate entity. — **CONFIRMED at extraction.** With `filer_person` = Nathan Aichele, the model set `filer_organization=null` and dropped "ARC Gaming &. Technologies" entirely — it is not preserved anywhere in `filing.json`. This is the **higher-impact gap**: the employer is *the* link between a lobbyist and a client/principal, and it's silently lost on every OH filing. Recommend a dedicated `filer_employer` (or first-class engagement entity) for v1.4 review.

**No new gaps surfaced during tagging.** The two pre-flagged gaps both reproduced exactly as predicted; the model's behavior on both was the "right" behavior given the schema (collapse per brief; don't misfile employer) — the loss is structural, not a model error.

---

## Summary stats (fill after tagging)

Row accounting: 19 filing-level fields + 4 `positions` rows + 6 `expenditures` fields + 2 list fields (`engagements`, `gifts`) = **31 rows**.

| Tag | Count | % of populated rows |
|---|---|---|
| CORRECT | 29 | 93.5% |
| WRONG | 0 | 0.0% |
| MISSING | 1 | 3.2% |
| SCHEMA-GAP | 1 | 3.2% |
| **Total populated rows** | 31 | 100% |

MISSING row: `is_itemized` (expected `false`, got `null`). SCHEMA-GAP row: `filer_organization`/employer dropped.

**Decision gate:** % CORRECT ≥ 80% → graduate to (B'). **Result: 93.5% CORRECT, 0 WRONG → ✅ GRADUATE to (B').**

The two non-CORRECT rows are *not* extraction-quality failures:
- The SCHEMA-GAP is a known structural limitation (no employer slot), already flagged for v1.4. Graduating to (B') does not require fixing it — it just means every (B') OH filing inherits the same documented employer-loss until v1.4 lands.
- The MISSING `is_itemized` is the single prompt-fixable nit (one brief sentence). Not blocking.

Zero hallucinations, zero mis-parses, perfect on all 4 bills, correct Section-D collapse, correct null discipline. The pipeline is sound on OH legislative AERs. Recommend proceeding to (B') batch extraction on the pre-vetted seeds (HART 1459616, LKQ 1405684), carrying the two gaps forward as documented-known, not as blockers.

---

## What changes go where

- New schema gaps → append above; surface as v1.4 proposal text in the convo summary (NOT the schema, NOT a unilateral bump).
- Brief-violation patterns (model ignored a rule) → list in the convo summary's "iteration notes" section.
- One-off model errors (transcription typos, formatting) → tag WRONG, no further action; opus-4-7 doesn't need prompt tuning for stochastic errors at n=1.
