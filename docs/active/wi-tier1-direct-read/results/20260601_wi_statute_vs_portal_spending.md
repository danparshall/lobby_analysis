# WI 2025 — Statute-required vs portal-exposed (spending reports)

**Session:** 2026-06-01
**Convo:** `convos/20260601_wi_tier1_phase2_run.md`
**Inputs:**
- Legal side: 36 Tier-1 result JSONs at `results/tier_1/WI_2025/` (consensus over 2 models × 3 runs × 6 chunks). This doc covers only the two spending-report chunks (53 cells).
- Practical side: `releases/wi/` — 6 TSVs scraped from `lobbying.wi.gov` (released to main 2026-05-27 from the archived `wi-disclosure-explore` branch).

## Headline finding — *deterministic inter-model framing disagreement on WI's spending-report architecture, settled by portal data*

> **Correction to prior framing**: an earlier draft of this doc claimed σ_noise "was masking" inter-model disagreement. That was wrong. The script's reported `pct_stable` (85.71% Claude / 84.52% GPT) is **already a per-model number** — each model's runs compared against itself. Inter-model agreement was never a component of σ_noise; it has no reported metric at all. The substantive finding (Claude over-includes; GPT reads correctly; portal data confirms GPT) is unchanged. The framing fix is just: there's a *second*, *un-reported* metric that needs surfacing alongside σ_noise.

In the `lobbyist_spending_report` chunk, every row where the WI statute requires the *data to flow through* the lobbyist (but the *report itself is filed by* the principal under §13.68(1)) splits **3 Claude TRUE / 3 GPT FALSE** with zero within-model variance:

| Row | Claude (3 runs) | GPT-5.2 (3 runs) |
|---|---|---|
| `lobbyist_spending_report_required` | TRUE × 3 | FALSE × 3 |
| `lobbyist_spending_report_includes_total_compensation` | TRUE × 3 | FALSE × 3 |
| `lobbyist_spending_report_includes_total_expenditures` | TRUE × 3 | FALSE × 3 |
| `lobbyist_spending_report_includes_general_issues` | TRUE × 3 | FALSE × 3 |
| `lobbyist_spending_report_includes_indirect_costs` | TRUE × 3 | FALSE × 3 |
| `lobbyist_spending_report_includes_gifts_entertainment_transport_lodging` | TRUE × 3 | FALSE × 3 |
| `lobbyist_spending_report_includes_principal_names` | TRUE × 3 | FALSE × 3 |
| `lobbyist_spending_report_includes_specific_bill_number` | TRUE × 3 | FALSE × 3 |
| `lobbyist_spending_report_includes_general_subject_matter` | TRUE × 3 | FALSE × 3 |
| `lobbyist_spending_report_includes_lobbyist_contact_info` | TRUE × 3 | FALSE × 3 |
| `lobbyist_spending_report_required_when_no_activity` | TRUE × 3 | FALSE × 3 |
| `lobbyist_spending_report_categorizes_expenses_by_type` | TRUE × 3 | FALSE × 3 |
| `lobbyist_spending_report_cadence_includes_semiannual` | TRUE × 3 | FALSE × 3 |

The per-model σ_noise (85.71% Claude / 84.52% GPT) reports each model's run-to-run stability. **These cells are within-model 100% stable for both models**; they just disagree with each other. The σ_noise metric as designed doesn't see this — *and there is no metric that does*. See implication 1 below.

### What the disagreement actually is

WI §13.68(1): *"Each registered principal shall file …"* (the expense statement)
WI §13.68(4): *"Each lobbyist shall, no later than 15 days after the close of each reporting period, provide the lobbyist's principal with the information required to enable the principal to comply with sub (1)."*

So: **the lobbyist provides info to the principal; the principal files.** There is no separate lobbyist-filed spending report in WI.

- **Claude reads the row functionally**: "is this information required to flow through the lobbyist?" → TRUE (per §13.68(4) the lobbyist must transmit it).
- **GPT reads the row literally**: "is the *lobbyist* the filer of a spending report?" → FALSE (the principal is).

### The portal data resolves the disagreement — GPT is right

`releases/wi/WI_lobbyist_filings.tsv` columns:
```
filing_id  lobbyist_id  state  filing_type  filer_role
reporting_period_start  reporting_period_end
total_hours_communicating  total_hours_other  source_url
```

**Zero expenditure columns. Zero compensation columns. Zero per-bill columns. Zero per-topic columns.** The lobbyist files an *activity report* (hours communicated), not a spending report. This matches GPT's reading of §13.68 exactly and falsifies Claude's overinclusive interpretation.

The practical data is **independent ground truth** on which model was right about WI's filing architecture — and on this batch of 13 cells, GPT wins 13/13.

### Implications

1. **A second, un-reported metric: inter-model alignment.** σ_noise as designed is per-model and behaves correctly. What's missing is the inter-model number. On WI: **65 of 84 cells are jointly within-model stable (both models internally agree on the 3 runs); of those 65, only 47 (72.3%) agree across models. 18 cells (27.7%) have a deterministic Claude-says-X-vs-GPT-says-Y framing disagreement.** That 27.7% is much larger than either model's individual ~14-15% run-to-run variance, and it's *signal* (deterministic), not *noise*. The two numbers should be reported alongside each other in v2.2. **Open candidate direction (Dan flagged 2026-06-01, not yet decided):** if the disagreement holds up on closer look, routing the next pipeline iteration through the Anthropic Citations API would let us recover each model's *cited statute text* for adjudication. To evaluate after a more detailed read of the 18 disagreeing cells. Captured for evaluation in `HANDOFF_followups.md` item 3.

2. **Compendium row taxonomy gap.** The `lobbyist_spending_report_*` rows assume a structure where the lobbyist files a spending report. WI doesn't have that — the lobbyist files an activity report, and the spending data is the principal's responsibility. Either: (a) the compendium needs a `lobbyist_activity_report_*` row family that distinguishes from spending, or (b) the existing row family needs a precondition cell (`lobbyist_files_spending_report_at_all`) and downstream cells become conditional on it.

3. **Cross-validation with portal data is a *general* technique.** This wasn't a fluke — comparing Tier-1 legal extraction against practical data resolved a model disagreement that pure statute-reading couldn't. **For MI (the next state), running Tier-1 *and* having portal data in parallel should be a default**, not a follow-on analysis. The gather-first pivot's intermediate JSON should include a `practical_observed: <portal column or null>` field per row.

---

## Principal-side spending report — full 23-row mapping

These are the cells where both models (mostly) agree on what WI statute requires.

| Compendium row | Statute consensus | Cited | Portal exposure | Status |
|---|---|---|---|---|
| `principal_spending_report_required` | **TRUE** | §13.68(1) | `WI_principal_filings.tsv` exists (1,706 rows) | ✅ MATCH |
| `principal_spending_report_cadence_includes_semiannual` | **TRUE** | §13.68(1) | `reporting_period_start`/`_end` show ~6-month periods | ✅ MATCH |
| `principal_spending_report_cadence_includes_annual` | FALSE | §13.68(1) | Not annual | ✅ MATCH (silent both ways) |
| `principal_spending_report_cadence_includes_quarterly` | FALSE | §13.68(1) | Not quarterly | ✅ MATCH (silent both ways) |
| `principal_spending_report_cadence_includes_monthly` | FALSE | §13.68(1) | Not monthly | ✅ MATCH (silent both ways) |
| `principal_spending_report_cadence_includes_triannual` | FALSE | §13.68(1) | Not triannual | ✅ MATCH (silent both ways) |
| `principal_spending_report_cadence_includes_other` | FALSE | §13.68(1) | n/a | ✅ MATCH |
| `principal_spending_report_cadence_other_specification` | UNSCOREABLE (conditional, parent False) | — | n/a | ✅ MATCH (correctly abstained) |
| `principal_spending_report_includes_total_expenditures` | **TRUE** | §13.68(1)(a) | `total_expenditure` (single $ aggregate) | ✅ MATCH |
| `principal_spending_report_includes_compensation_paid_to_lobbyists` | **TRUE** | §13.68(1)(a)1., (a)6. | **NO per-lobbyist compensation column** | ⛔ **GAP** |
| `principal_spending_report_includes_gifts_entertainment_transport_lodging` | **TRUE** | §13.68(1)(d) | **NO itemized gifts column** | ⛔ **GAP** |
| `principal_spending_report_includes_indirect_costs` | **TRUE** | §13.68(1)(b) | **NO indirect-cost column** | ⛔ **GAP** |
| `principal_spending_report_uses_itemized_format` | **TRUE** | §13.68(1)(c) | `total_expenditure` is a single scalar, **not itemized** | ⛔ **GAP** (largest one — statute requires itemization, portal exposes aggregate) |
| `principal_spending_report_includes_general_issues` | **TRUE** | §13.68(1)(bn) | `WI_principal_bill_efforts.tsv` has `bucket`, `item_name`, `item_description` | ✅ CROSS-FILE MATCH |
| `principal_spending_report_includes_specific_bill_number` | **TRUE** | §13.68(1)(bn) | `WI_principal_bill_efforts.tsv.item_id` | ✅ CROSS-FILE MATCH |
| `principal_spending_report_includes_lobbyist_names` | **TRUE** | §13.68(1)(a)6., (cm) | `WI_lobbyist_principal_authorizations_unified.tsv` + `WI_lobbyists.tsv.name` | ✅ CROSS-FILE MATCH |
| `principal_spending_report_includes_lobbyist_contact_info` | **TRUE** | §13.68(1)(a)6. | `WI_lobbyists.tsv.contact_details_json` | ✅ CROSS-FILE MATCH |
| `principal_spending_report_lists_lobbyists_employed` | **TRUE** | §13.68(1)(a)6. | `WI_lobbyist_principal_authorizations_unified.tsv` | ✅ CROSS-FILE MATCH |
| `principal_spending_report_includes_contacts_made` | UNSTABLE (4/6 TRUE) | §13.68(1)(c)1. | No per-contact data | ⚠ UNRESOLVED |
| `principal_spending_report_includes_business_nature` | FALSE | §13.68(1) | (In registration, not filing — `WI_principals.tsv.business_or_interest`) | ✅ MATCH on "not in spending report" |
| `principal_spending_report_includes_principal_contact_info` | FALSE | §13.68(1) | (In registration — `WI_principals.tsv.contact_details_json`) | ✅ MATCH on "not in spending report" |
| `principal_spending_report_includes_major_financial_contributors` | FALSE | §13.68(1) | Not exposed | ✅ MATCH (silent both ways) |
| `lobbyist_or_principal_reg_form_includes_member_or_sponsor_names` | UNSTABLE (4/6 TRUE; this is a *registration* row, mis-grouped in the spending chunk) | §13.64(1)(c),(d) | n/a in this comparison | (out of scope here) |

### Headline counts (principal side)

| Status | Count |
|---|---|
| ✅ MATCH (required + exposed, or not-required + not-exposed) | 12 |
| ✅ CROSS-FILE MATCH (required, exposed via linked file) | 5 |
| ⛔ **GAP** (required + not exposed) | **4** |
| ⚠ UNRESOLVED (ambiguous consensus) | 1 |
| Out of scope | 1 |

### The 4 principal-side gaps in detail

1. **`includes_compensation_paid_to_lobbyists`** — statute §13.68(1)(a)1.+(a)6. requires reporting of compensation paid to each lobbyist. Portal exposes only `total_expenditure`, no per-lobbyist breakdown. The data is collected (the principal must file it) but not published in machine-readable form. *This is the kind of finding the FOCAL/Sunlight transparency rubrics weight heavily.*
2. **`includes_gifts_entertainment_transport_lodging`** — statute §13.68(1)(d) requires reporting of these as a separate category. Portal: no itemized gifts column.
3. **`includes_indirect_costs`** — statute §13.68(1)(b) requires reporting of indirect costs (overhead). Portal: no indirect-cost column.
4. **`uses_itemized_format`** — statute §13.68(1)(c) requires the report be itemized. Portal exposes a single `total_expenditure` scalar. **Largest gap** — itemization is the structural shape of the disclosure.

All four gaps reduce to one underlying transparency problem: **WI principal expense statements *do* itemize by category in the underlying filings, but the public-facing TSV exposes only top-line aggregates.** Whether this is a portal-publication choice or a scrape-loss is the next question (the `wi-disclosure-explore` archive should know).

---

## Lobbyist-side "spending" report — what the portal *does* expose

Per the headline finding, WI doesn't have a lobbyist-side spending report at all — only the principal does. What the lobbyist files (the "activity report" in §13.68's vocabulary) is:

| Compendium row | Should this row exist for WI? | Portal | Notes |
|---|---|---|---|
| `lobbyist_activity_report_*` (doesn't exist in compendium) | **YES — this taxonomy gap is the v2.2 design input** | `WI_lobbyist_filings.tsv.total_hours_communicating`, `total_hours_other` | The compendium has no row family for the lobbyist-side activity report; it's invisible in the current 84-cell legal roster because the only spending-side row is `lobbyist_spending_report_*` (which WI's lobbyist doesn't file). |

The 30 `lobbyist_spending_report_*` cells in the chunk are almost all GPT-FALSE (correct) / Claude-TRUE (over-inclusive). When the compendium taxonomy adds a `lobbyist_activity_report_*` row family in v2.2, those should populate with `total_hours_communicating`/`total_hours_other` as the matching practical-axis observation.

---

## Cross-validation summary

This is the first WI cell where **practical data settled a Tier-1 model disagreement**. The mechanism is general: when both models converge on the same answer it's strong evidence; when they diverge cleanly along framing lines, the portal data is an independent yardstick.

The Compendium 2.0 success criterion #4 talks about per-rubric projections as redundant ground truth. **Per-state portal data is a second, orthogonal ground truth** — it tests the *legal axis* extraction by checking the *practical axis* downstream. For the priority states where we already have scrape outputs (WI from `wi-disclosure-explore`; NC from a forthcoming branch per the archived convention), this validation is essentially free.

### Suggested follow-up to add to MI handoff

Run Tier-1 against MI 2025 **and** load `releases/mi/` (assuming it exists by then) **in the same session**. Use the same comparison structure as this doc. Expected payoff: identifying MI-specific compendium taxonomy gaps + cross-validating per-cell model disagreements + building the cross-state portal-coverage matrix that the README's "Required × {Legal, Practical}" framing has been waiting for. **Open candidate:** if Dan's closer look at the 18 WI inter-model disagreements (item 3 in followups) concludes the Citations API is worth pulling in, the MI session is a natural time to route through it — but that's a decision for the evaluation, not a foregone conclusion.
