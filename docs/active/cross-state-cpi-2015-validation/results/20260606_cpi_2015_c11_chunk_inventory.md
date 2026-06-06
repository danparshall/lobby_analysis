<!-- Generated during: convos/20260606_pre_dispatch_review.md -->

# CPI-2015 C11 default-6-chunks inventory

**Purpose:** structural breakdown of what we'd be re-dispatching in the 5-state extension (CO/IL/WA/FL/NC). Counts cells by axis (de-jure vs de-facto), cell-type, and chunk; surfaces combined-axis rows; audits prompt-presence and response-format clarification.

**Companion to:**
- [`20260605_cross_state_cpi_2015_validation.md`](20260605_cross_state_cpi_2015_validation.md) — N=5 audit data (Table A + Table B)
- [`20260606_failure_mode_trends_and_paths_forward.md`](20260606_failure_mode_trends_and_paths_forward.md) — N=5 failure-mode trends
- Companion plan: [`../plans/20260606_pre_dispatch_hygiene.md`](../plans/20260606_pre_dispatch_hygiene.md)

**Code referenced:**
- Chunk manifest: `src/lobby_analysis/chunks_v2/manifest.py`
- Cell-type parser: `src/lobby_analysis/models_v2/cell_spec.py`
- Prompt SSOT: `compendium/source_quotes.yaml`
- Dispatcher default chunks: `scripts/tier_1_direct_read_legal_axis.py` (`_DEFAULT_CHUNKS`)

---

## Headline numbers

The 6 default chunks contain **93 cells** total:

| dimension | count | % |
|---|---:|---:|
| **de-jure (legal axis)** | **84** | **90.3%** |
| de-facto (practical axis) | 9 | 9.7% |
| BinaryCell | 73 | 78.5% |
| structured types (Int/Float/Decimal/Graded/Enum/Set/FreeText/TimeThreshold) | 20 | 21.5% |
| prompts present | 93 | 100% |
| prompts with explicit response-format hint | 82 | 88.2% |
| prompts lacking response-format hint | **11** | **11.8%** |

The "structured 20" is where Round 1's vocab-mismatch failures lived. The "underspecified 11" is a partially-overlapping hygiene problem (4 of the 11 are also in the structured-20).

---

## Section 1 — de-jure vs de-facto

CPI-2015 C11 scores **state lobbying disclosure law** (de jure), so the rubric is overwhelmingly legal. The 6 default chunks reflect that — 90.3% de-jure cells. The de-facto cells appear only where a row is **combined-axis**: the same row_id has both a legal-half cell (e.g., "does law require X?") and a practical-half cell (e.g., "does it actually happen, on a 0/25/50/75/100 graded scale?"). The two halves co-locate in the same chunk per Q3 of the chunks brainstorm — see `src/lobby_analysis/chunks_v2/chunks.py` lines 108–113.

**Combined-axis rows present in the 6 default chunks (3 rows, 6 cells):**
- `lobbyist_registration_required` — in `registration_mechanics_and_exemptions`
- `lobbyist_registration_deadline_days_after_first_lobbying` — in `registration_mechanics_and_exemptions`
- `lobbyist_spending_report_filing_cadence` — in `lobbyist_spending_report`

**De-facto cells (9 total) by chunk:**

| chunk | de-facto cells | provenance |
|---|---:|---|
| `registration_mechanics_and_exemptions` | 2 | combined-axis rows ↑ |
| `lobbyist_spending_report` | 5 | 1 combined-axis row + 4 single-axis practical rows (the "report available as ..." accessibility flags) |
| `enforcement_and_audits` | 2 | post-v2.1 Pattern C row split: `lobbying_violation_penalties_imposed_in_practice`, `lobbying_disclosure_audit_required_in_practice` |
| **other 3 chunks** | **0** | pure legal |

**Why this matters for the dispatch:** the de-facto cells use rubric-graded language ("A 100 score is earned if all who are paid to lobby register as such…"). They can't be answered from statute alone — they require either empirical observation or scoring against an external practical-state assessment. In Round 1 these are sources of σ_noise more than projection error, because the model knows the rubric tiers and just has to commit. They're also 4 of the 11 underspecified-prompt cells (Section 4).

---

## Section 2 — cell-type histogram

The cells are typed via `_CELL_TYPE_PARSER` in `src/lobby_analysis/models_v2/cell_spec.py`. Each type carries a different return-shape contract.

| Type | n | % | What the model returns | Where the projection helper consumes it |
|---|--:|--:|---|---|
| **BinaryCell** | 73 | 78.5% | `True` / `False` / `null` | `bool(...)` checks |
| **GradedIntCell** | 5 | 5.4% | int ∈ {0, 25, 50, 75, 100} | passed through to CPI score |
| **DecimalCell** | 4 | 4.3% | non-negative `Decimal` (e.g., `500` for $500) | thresholded vs `0` for YES/MODERATE/NO |
| **IntCell** | 3 | 3.2% | non-negative int (months or days) | thresholded vs cadence/deadline tiers |
| **EnumCell** | 2 | 2.2% | one of a named domain | `==` against helper-expected strings |
| **EnumSetCell** | 2 | 2.2% | a set of named domain values | membership checks |
| **FreeTextCell** | 2 | 2.2% | string | typically passthrough |
| **FloatCell** | 1 | 1.1% | non-negative float (percent 0–100) | thresholded |
| **TimeThresholdCell** | 1 | 1.1% | composite (time + unit) | typed accessor |

### Where Round 1 failures lived, by cell-type

The trends doc puts 9 of 15 misses (60%) on vocab schism in:
- **IND_199** (`lobbyist_registration_renewal_cadence`, **IntCell**) — YAML returns months (`12`/`24`); helper expects `"annual"`/`"biennial"` strings. 4 of 5 states miss.
- **IND_207** (`lobbying_disclosure_audit_required_in_law`, **EnumCell**) — YAML returns `"YES"`/`"MODERATE"`/`"NO"`; helper expects `"regular_third_party_audit_required"`/`"audit_only_when_irregularities_suspected_or_compliance_review"`. All 5 states miss.

Both are in the structured-20 (~22% of cells), not in the BinaryCell majority. IND_196 (5/5 perfect) is BinaryCell-compound and rides on the clean 78.5%.

### Full row list per cell-type

<details>
<summary><strong>BinaryCell (73 — too long to inline; see appendix at end</strong></summary>

See appendix A.
</details>

**GradedIntCell (5)** — all de-facto, all CPI-rubric-graded:
- `lobbyist_registration_required` (P, `registration_mechanics_and_exemptions`)
- `lobbyist_registration_deadline_days_after_first_lobbying` (P, `registration_mechanics_and_exemptions`)
- `lobbyist_spending_report_filing_cadence` (P, `lobbyist_spending_report`)
- `lobbying_violation_penalties_imposed_in_practice` (P, `enforcement_and_audits`)
- `lobbying_disclosure_audit_required_in_practice` (P, `enforcement_and_audits`)

**DecimalCell (4)** — all in `registration_thresholds`:
- `lobbyist_registration_threshold_compensation_dollars`
- `lobbyist_registration_threshold_expenditure_dollars`
- `lobbyist_filing_itemization_de_minimis_threshold_dollars`
- `lobbyist_filing_de_minimis_threshold_dollars`

These are the cells where the "$0 threshold" extraction-vs-MODERATE-grader disagreement landed in Round 1 (WI + OH IND_197 — Trend 3 in the failure-mode doc).

**IntCell (3)** — all in `registration_mechanics_and_exemptions`:
- `lobbyist_registration_renewal_cadence` ← the IND_199 vocab schism cell
- `lobbyist_registration_amendment_deadline_days`
- `lobbyist_registration_deadline_days_after_first_lobbying` (legal half; practical half is GradedIntCell)

**EnumCell (2)**:
- `lobbyist_spending_report_filing_cadence` (L, `lobbyist_spending_report`) — domain: cadence enum
- `lobbying_disclosure_audit_required_in_law` (L, `enforcement_and_audits`) ← the IND_207 vocab schism cell

**EnumSetCell (2)** — both in `lobbying_definitions`:
- `def_lobbying_activity_types` — domain: {oral, written, electronic, virtual, organising_meetings, events, phone_calls, emails}
- `def_lobbyist_actor_types` — domain: {professional_lobbyist, in_house_company, in_house_organisation, professional_consultancy, law_firm, think_tank, research_institution, public_entity, government_…}

**FreeTextCell (2)**:
- `lobbyist_spending_report_cadence_other_specification` (L, `lobbyist_spending_report`)
- `principal_spending_report_cadence_other_specification` (L, `principal_spending_report`)

Both are "if cadence is `other`, specify" — short-text completion of an enum's escape hatch.

**FloatCell (1)**:
- `lobbyist_filing_de_minimis_threshold_time_percent` (L, `registration_thresholds`)

**TimeThresholdCell (1)**:
- `lobbyist_registration_threshold_time_percent` (L, `registration_thresholds`) — composite carrying time + unit

---

## Section 3 — 6 chunks with themes + size

The 6 chunks were chosen as the de-jure subset that maps onto CPI-2015 C11's 6 published indicators (IND_196, 197, 199, 201, 203, 207). The chunk boundaries are topic-coherent, not indicator-aligned — one chunk can contribute to multiple indicators and vice versa. Each chunk has hand-curated `notes` in the manifest that record design intent.

### 3.1 `lobbying_definitions` — 15 cells (15L / 0P, axis=legal)

**Topic:** What counts as lobbying or a lobbyist — definitional rows.

**Manifest notes:** Spiritual successor to iter-1's 7-row `definitions` chunk. Three sub-axes (TARGET / ACTOR / THRESHOLD-qualitative); preamble will teach the disambiguation.

**Cell-type breakdown:** 13 BinaryCell + 2 EnumSetCell.

**Rows:** `def_lobbying_activity_types`, `def_lobbyist_actor_types`, `law_defines_public_entity`, `law_includes_materiality_test`, `def_target_executive_agency`, `def_target_executive_staff`, `def_target_governors_office`, `def_target_independent_agency`, `def_target_legislative_branch`, `def_target_legislative_staff`, `def_actor_class_elected_officials`, `def_actor_class_public_employees`, `public_entity_def_relies_on_charter`, `public_entity_def_relies_on_ownership`, `public_entity_def_relies_on_revenue_structure`.

**Round 1 performance:** clean. IND_196 (which reads `def_target_legislative_branch` + `def_target_governors_office`) hit 5/5 across all states. The chunk's "structurally Boolean + statutorily unambiguous" character is what made the indicator robust.

### 3.2 `registration_thresholds` — 6 cells (6L / 0P, axis=legal)

**Topic:** Quantitative gates for lobbyist registration and disclosure.

**Manifest notes:** The quantitative thresholds. Qualitative `law_includes_materiality_test` lives in `lobbying_definitions` since it functions definitionally, not as a numeric gate.

**Cell-type breakdown:** 4 DecimalCell + 1 TimeThresholdCell + 1 FloatCell — the most-typed-rich chunk in the round.

**Rows:** `lobbyist_registration_threshold_compensation_dollars`, `lobbyist_registration_threshold_expenditure_dollars`, `lobbyist_registration_threshold_time_percent`, `lobbyist_filing_itemization_de_minimis_threshold_dollars`, `lobbyist_filing_de_minimis_threshold_dollars`, `lobbyist_filing_de_minimis_threshold_time_percent`.

**Round 1 performance:** mostly clean on the BinaryCell-adjacent threshold reads (DecimalCells extracted $0 cleanly). The CPI-grader-vs-statute-literal disagreement on "any economic consideration" (WI + OH IND_197, Trend 3) lives here. 2 of the 6 cells are in the underspecified-prompt list (Section 4).

### 3.3 `registration_mechanics_and_exemptions` — 10 cells (8L / 2P, axis=mixed)

**Topic:** Registration process: when, how, who's exempt.

**Manifest notes:** Contains 2 of the 5 combined-axis rows (`lobbyist_registration_required`, `lobbyist_registration_deadline_days_after_first_lobbying`). Mixed axis_summary expected.

**Cell-type breakdown:** 5 BinaryCell + 3 IntCell + 2 GradedIntCell.

**Rows:** `lobbyist_registration_required` (both axes), `lobbyist_registration_renewal_cadence`, `lobbyist_registration_amendment_deadline_days`, `lobbyist_registration_deadline_days_after_first_lobbying` (both axes), `separate_registrations_for_lobbyists_and_clients`, `lobbyist_required_to_submit_photograph_with_registration`, `exemption_for_govt_official_capacity_exists`, `exemption_partial_for_govt_agencies`.

**Round 1 performance:** **mixed — the IND_199 vocab schism lives here.** `lobbyist_registration_renewal_cadence` is the IntCell whose months-extraction the helper expects as `"annual"`/`"biennial"`. Also home to 5 of the 11 underspecified prompts (Section 4).

### 3.4 `lobbyist_spending_report` — 35 cells (30L / 5P, axis=mixed) — **the big one**

**Topic:** Lobbyist's periodic spending report — cadence, content, format.

**Manifest notes:** 34 rows. Single chunk per user approval — the cluster is one coherent topic (the report). Contains 1 combined-axis row (`lobbyist_spending_report_filing_cadence`).

**Cell-type breakdown:** 32 BinaryCell + 1 EnumCell (combined-axis legal) + 1 GradedIntCell (combined-axis practical) + 1 FreeTextCell.

**Rows:** 30+ "report includes X / report available as Y / cadence Z" rows; see `src/lobby_analysis/chunks_v2/manifest.py` for full list.

**Round 1 performance:** the BinaryCell majority dispatches cleanly (this is the σ_noise floor — Claude consistently 85–93% on this chunk). 2 of the 11 underspecified prompts live here (the `_filing_cadence` combined-axis row + `_cadence_other_specification` FreeTextCell).

**Engineering note:** at 35 cells in one chunk, this is also the chunk most exposed to output-token-budget pressure. `_MAX_OUTPUT_TOKENS = 16384` in the dispatcher should handle it; verified in Round 1.

### 3.5 `principal_spending_report` — 23 cells (23L / 0P, axis=legal)

**Topic:** Principal's (employer's) periodic spending report.

**Manifest notes:** 21 `principal_spending_*` rows + 2 adjacent principal-side rows that don't fit elsewhere.

**Cell-type breakdown:** 22 BinaryCell + 1 FreeTextCell.

**Rows:** 21 `principal_spending_report_*` (cadence flags, content fields, format, requirement, itemized format) + `lobbyist_or_principal_reg_form_includes_member_or_sponsor_names` + `principal_spending_report_lists_lobbyists_employed`.

**Round 1 performance:** clean structurally; not directly read by any of the 6 CPI 2015 C11 indicators we audited, so doesn't appear in Trends 1–6 but is part of the dispatched corpus.

### 3.6 `enforcement_and_audits` — 4 cells (2L / 2P, axis=mixed) — **smallest, most CPI-load-bearing per cell**

**Topic:** Does the regime have teeth — penalties and audits.

**Manifest notes:** 4 rows, all single-axis (4 cells total) after v2.1 Pattern C row split (2026-06-05): the two CPI legal+practical rows were each un-combined into a de-jure + de-facto pair. `_defined_in_law` and `_audit_required_in_law` carry the legal half; `_imposed_in_practice` and `_audit_required_in_practice` carry the practical half. If merging feels desirable, `oversight_and_government_subjects` is the topical neighbor.

**Cell-type breakdown:** 1 BinaryCell + 2 GradedIntCell + 1 EnumCell.

**Rows:** `lobbying_violation_penalties_defined_in_law` (L), `lobbying_violation_penalties_imposed_in_practice` (P), `lobbying_disclosure_audit_required_in_law` (L), `lobbying_disclosure_audit_required_in_practice` (P).

**Round 1 performance:** **worst per-cell rate.** IND_207 reads `lobbying_disclosure_audit_required_in_law` and missed on all 5 states — the vocab schism cell. 2 of the 11 underspecified prompts live here (both GradedIntCells).

---

## Section 4 — underspecified prompts (the 11)

These prompts are present in `compendium/source_quotes.yaml` (Phase A wide-pass completed 2026-06-05) but lack heuristic keyword match for response-format clarification. They fall into three groups:

### Group 1 — terse / fragmentary (4)

These read as YAML-author shorthand, not model-facing prompts:

| row_id | axis | type | chunk | prompt |
|---|---|---|---|---|
| `lobbyist_registration_threshold_time_percent` | L | TimeThreshold | `registration_thresholds` | `"if they devote a certain amount of time in their lobbying efforts (time standards). Each of these is coded 1 if the state includes the provision in its definition of a lobbyist and 0 otherwise."` |
| `lobbyist_filing_de_minimis_threshold_time_percent` | L | Float | `registration_thresholds` | `"Time threshold exists: if amount of time devoted to lobbying is less than a threshold percentage of an individual's compensated time the individual or entity is exempted from filing disclosure." Asks about the LOBBYIST's own filing-de-minimis time-percent exemption, not a principal-side itemized-reporting threshold.` |
| `lobbyist_spending_report_cadence_other_specification` | L | FreeText | `lobbyist_spending_report` | `"Reporting frequency option: Other (free-text)."` |
| `principal_spending_report_cadence_other_specification` | L | FreeText | `principal_spending_report` | `"Reporting frequency option: Other (free-text)."` |

### Group 2 — CPI rubric language, no extraction instruction (6)

These carry CPI's "A 100 / 50 / 0 score is earned if…" rubric copy verbatim, with no explicit "Answer with one of: 0, 25, 50, 75, 100." instruction. Model has to infer the return shape from the cell-type contract:

| row_id | axis | type | chunk |
|---|---|---|---|
| `lobbyist_registration_required` | L | Binary | `registration_mechanics_and_exemptions` |
| `lobbyist_registration_required` | P | GradedInt | `registration_mechanics_and_exemptions` |
| `lobbyist_registration_deadline_days_after_first_lobbying` | L | Int | `registration_mechanics_and_exemptions` |
| `lobbyist_registration_deadline_days_after_first_lobbying` | P | GradedInt | `registration_mechanics_and_exemptions` |
| `lobbying_violation_penalties_imposed_in_practice` | P | GradedInt | `enforcement_and_audits` |
| `lobbying_disclosure_audit_required_in_practice` | P | GradedInt | `enforcement_and_audits` |

(Total: Group 1 (4) + Group 2 (6) + Group 3 (1) = 11 cell-axis-pairs. Some rows contribute two cells via combined-axis. See appendix B.)

### Group 3 — instruction-shaped but no enum / unit specified (1)

| row_id | axis | type | chunk | prompt |
|---|---|---|---|---|
| `lobbyist_registration_amendment_deadline_days` | L | Int | `registration_mechanics_and_exemptions` | `"7. Within how many days must a lobbyist notify the oversight agency of changes in registration?"` |

The "Within how many days" implies integer-days; just missing the explicit "Answer with an integer number of days" closing.

**The structural pattern across all 11:** they're prompts where the YAML author treated the *cell-type contract* as carrying the return-shape information, and only wrote the *content* question. The 82 well-specified prompts redundantly state the contract ("Answer with one of: …", "Answer with the dollar amount as a non-negative decimal"). This is exactly the hygiene gap Dan flagged.

---

## Section 5 — what this implies for the 5-state extension

Two findings from this inventory shape the Phase 0 hygiene work that should ideally land before the $15 dispatch:

1. **The vocab schism (Round 1's 9 of 15 misses, Trend 1 in the failure-mode doc) is concentrated in the structured-20.** Specifically: IND_199's IntCell ↔ helper-enum mismatch, IND_207's EnumCell-domain-mismatch. Both are helper-side, surgical, $0 fix. See [`../plans/20260606_pre_dispatch_hygiene.md`](../plans/20260606_pre_dispatch_hygiene.md) §Phase 1.

2. **The 11 underspecified prompts are forward hygiene, not Round 1 debt.** Round 1's documented failure mechanism was YAML-correct + helper-wrong; the under-specified prompts didn't cause Round 1's documented misses. But weaker prompts could cause more instantiation errors or σ_noise on the new 5 states — particularly because CO/IL/WA/FL/NC have less Round 1 trace evidence. See [`../plans/20260606_pre_dispatch_hygiene.md`](../plans/20260606_pre_dispatch_hygiene.md) §Phase 2 and §Risks.

If both phases land cleanly, the N=10 picture should be:
- IND_207: helper fix → all 5 Round 1 states flip MODERATE→YES match. New 5 states match-rate predicted ~85% on this indicator (subject to Trend 5's "CPI is more generous than our extraction" caveat for 1 of 5 expected misses).
- IND_199: helper fix → 4 of 5 Round 1 states flip; TX (Round 1 over-projection, Trend 4) was already accidentally-matching on the broken helper. Net change for Round 1: +3 cells. Round 2 prediction: ~80% match on this indicator.
- Underspecified-prompt fixes: cleaner σ_noise on the affected cells; same projected accuracy (these weren't accuracy failures in Round 1).

These are predictions, not promises — N=10 evidence will tell.

---

## Appendix A — full BinaryCell row list (73)

Omitted for inline brevity; full list is at `/tmp/inventory_v2_out.txt` lines 157–230, generated by `/tmp/chunk_inventory_v2.py`.

## Appendix B — exact prompt-audit counts

From `/tmp/prompt_audit.py`:
- 93 cells across 6 default chunks
- 93 with prompts (0 missing)
- 82 with format-clarification keyword match
- 11 without — listed in full in Section 4 (Groups 1+2+3 sum to 4+6+1=11 cell-axis-pairs)

Generated 2026-06-06 against the cross-state-cpi-2015-validation worktree at commit `b41a8c6`.
