# FOCAL 2024 — Legal-side Core Projection Implementation Plan

**Goal:** Ship the `focal_2024` module skeleton + 26 in-scope legal-axis atomic items (scope battery 4, descriptors battery 6, relationships battery 4+1 2025-only, revolving_door battery 1, financials battery 11). Aggregation logic, openness/timeliness/contact_log batteries, and US LDA federal validation harness ship in the 3 companion plans drafted this session — this plan owns the legal-axis core that all others extend.

**Originating conversation:** [`../convos/20260518_focal_hg_plans_drafting.md`](../convos/20260518_focal_hg_plans_drafting.md) (Sub-3 of Phase C — FOCAL plan-set + HG plan with retrieval gate). Pairs with:

- [`20260518_focal_2024_contact_log_plan.md`](20260518_focal_2024_contact_log_plan.md) — same session, contact_log battery (11 items)
- [`20260518_focal_2024_openness_timeliness_plan.md`](20260518_focal_2024_openness_timeliness_plan.md) — same session, openness + timeliness batteries (12 items)
- [`20260518_focal_2024_aggregation_plan.md`](20260518_focal_2024_aggregation_plan.md) — same session, weighted aggregation + US LDA federal validation + ranking

The 4 plans collectively cover FOCAL's 49 in-scope 2024 indicators + the 2025-only "Lobbyist list" indicator. Per Sub-0's structural recommendation, FOCAL was split into 3-4 sub-plans because the 49 indicators × 36 NEW rows × scorer-judgment items × 2024-with-2025 asymmetry exceeded single-plan context-window budget.

**Spec doc:** [`../../../historical/compendium-source-extracts/results/projections/focal_2024_projection_mapping.md`](../../../historical/compendium-source-extracts/results/projections/focal_2024_projection_mapping.md). The plan below is **derivative** — read the spec end-to-end for source quotes, cross-rubric annotations, and Open-Issue resolutions (FOCAL-1 through FOCAL-11).

**Context:** Rubric #8 in Phase C's locked rubric order — the **last contributing rubric** in the Phase B set. FOCAL 2024 is the **broadest contributing rubric** (49 in-scope 2024 indicators + 1 2025-only addition; synthesises 15 predecessor frameworks). Its load-bearing role in the project: **cross-jurisdictional (28-country) calibration anchor for the US federal LDA jurisdiction** (US LDA = 81/182 = 45% — primary federal-jurisdiction validation row across the contributing rubric set). For US states, FOCAL has **no per-state ground truth**; cross-rubric is the only check.

**Confidence:** High on per-item legal-axis mappings; spec doc factually-audited 2026-05-13 (contact-log count restored 13/15 + openness 11/15 clarity tightening). Medium on the set-typed cells (scope.1 actor types, scope.4 activity types, financials.3 income source types) — the v2 freeze split these into different shapes than the spec doc proposed (see rename table). Medium on the scope.2 calibration cutoff (`LOW_DOLLAR_CUTOFF` / `LOW_TIME_CUTOFF`) — Sub-0 flagged this as a Phase C decision (Open Q-1 below).

**Architecture:** Single `focal_2024.py` module with a declarative `_ATOMIC_SPEC` table dispatcher mirroring `pri_2010.py`'s pattern. **This plan introduces the module skeleton** (constants, score model, dispatcher, ground-truth loader stub); the 3 companion plans add their own batteries' specs to the same dispatcher dict. 26 legal-axis items in this plan; 23 more items (contact_log 11 + openness 9 + timeliness 3 effective; some merged) land via companion plans. Named helpers for the 5 compound items (scope.1, scope.2, scope.3, scope.4, financials.10).

**Branch:** `phase-c-projection-tdd` (worktree at `.worktrees/phase-c-projection-tdd`).

**Tech Stack:** Python 3.12, Pydantic v2, pytest, `uv` for env management. `load_v2_compendium()` from `lobby_analysis.compendium_loader` for cell access. `STATE_NAME_TO_USPS` from `scoring.calibration`.

---

## Cross-plan ordering — Legal core lands first

The 4 FOCAL plans converge on **one** `focal_2024.py` module. Landing order:

1. **Legal core (this plan)** — introduces module skeleton, score model, `_ATOMIC_SPEC` dispatcher dict, ground-truth loader stub. 26 items added.
2. **Contact log** — adds 11 items to `_ATOMIC_SPEC` + 9 NEW v2 rows fully consumed. No helper exports.
3. **Openness + timeliness** — adds 12 items + practical-axis read pattern.
4. **Aggregation** — adds `project_focal_2024(cells, jurisdiction)` top-level + weighted sum + US LDA federal validation harness + cross-rubric harness + ranking.

**Headless launcher (Sub-4) must enforce this 4-step intra-FOCAL ordering.** Each subsequent plan inherits the module skeleton + must not redefine the score model or `_ATOMIC_SPEC` dict (only extend).

---

## Scope qualifier — 1 item OUT (FOCAL-1 resolved 2026-05-13)

Per the FOCAL-1 user-decision 2026-05-13: pull `revolving_door.1` IN; keep `revolving_door.2` OUT.

| FOCAL item | Disposition | Reason |
|---|---|---|
| `revolving_door.1` (list of prior public offices that lobbyists have held) | **IN** | Registration-form disclosure observable. v2 row: `lobbyist_reg_form_includes_lobbyist_prior_public_offices_held`. |
| `revolving_door.2` (database of officials in cooling-off period) | OUT | State-side meta-publication of an enforcement mechanism. Enforcement-adjacent. |

**Max reproducible:** 182 (full max) − 2 (revolving_door.2 weight 1 × max raw 2) = **180**. Federal US LDA in-scope total: 81 (unchanged; US scored 0 on revolving_door.2 anyway).

**Implication for percentage tolerance:** projected percentage 81/180 = 45.0% vs published 81/182 = 44.5%. **Raw points match exactly (81 published == 81 projected); ≤1pp residual on percentage from the denominator shift only.** The previously-documented +6pt under-scoring tolerance is **closed**.

**STOP clause:** If a borderline `prohib`-like item surfaces (analogous to the FOCAL-1 resolution itself), **STOP and ask the user before pulling it IN.** Disclosure-only Phase B scope decisions are locked per Sub-0; do not relitigate without user direction.

---

## Validation regime — Weak/Cross-rubric only (US states); Strong (US LDA federal)

**Tier (US states):** No per-state US ground truth. FOCAL has not been applied to US states (only Federal_US LDA per Lacy-Nichols 2025). **Cross-rubric validation is the only check** for state-level projections — for every shared compendium row read by FOCAL + another Phase C-shipped module, project a state's cell through both and assert per-item agreement.

**Tier (Federal_US LDA):** Strong — 1 jurisdiction × 1 vintage (2024 application) × 49 in-scope 2024 indicators = **49 per-cell ground-truth values + aggregate 81/180 (45%)** per the L-N 2025 Suppl File 1 Table 5 / per-country CSV. The Federal US LDA validation harness lives in the aggregation plan (Plan 4), but the legal core (this plan) ships the per-item ground-truth loader that the harness consumes.

**Ground truth source:** [`docs/historical/compendium-source-extracts/results/focal_2025_lacy_nichols_per_country_scores.csv`](../../../historical/compendium-source-extracts/results/focal_2025_lacy_nichols_per_country_scores.csv) — 1,372 cells (28 countries × 49 merged 2025 indicators). For Phase C, the US row is the load-bearing validation anchor; the other 27 countries are reference data.

**Tier (other countries):** Reference / secondary. 27 jurisdictions × 1 vintage × 49 indicators = 1,323 more cells if non-US validation is added. The pipeline is US-focused per the 2026-05-07 jurisdiction-scope landing; non-US tests are `pytest.mark.xfail` at landing with reason="non-US jurisdiction; reference data not in primary validation scope".

**Validation tolerance:**

- **Federal US LDA per-item:** `==` exact match on per-indicator raw score (0/1/2) for each of the 49 in-scope indicators.
- **Federal US LDA aggregate:** `==` exact match on raw points (81 ± 0). Percentage tolerance ≤1pp from denominator shift (180 vs 182).
- **US states per-item:** no validation possible against FOCAL directly; cross-rubric agreement is the proxy (per Plan 4's cross-rubric harness).

### Vintage discipline

**Same-vintage anchor (Federal US LDA):** the L-N 2025 application uses 2019-2023 data collection window (Israel outlier 2025) per paper line 180-181. **For US LDA validation, this is "data current to 2019-2023"** — Phase D extraction of FOCAL cells for Federal_US LDA must use statute snapshots from that window or accept vintage drift.

**Same-vintage anchor (US states):** FOCAL has no per-state US ground truth, so vintage discipline applies only at the cross-rubric check — FOCAL state-level projections inherit whatever vintage the state's cells were extracted at. Recommended: align with HG 2007 vintage if HG ships first, or Newmark 2017's 2015 vintage if not, or modern 2024-vintage for whatever extraction batch FOCAL runs against in Phase D.

---

## Data year — 2024 framework, 2019-2023 data window for US LDA validation (HIGH confidence)

| Source | Year | Note |
|---|---|---|
| FOCAL framework (Lacy-Nichols 2024, IJHPM) | 2024 (framework paper) | 50 indicators in scope |
| L-N 2025 (Milbank Quarterly) application | 2025 (publication) | 49 merged indicators + 1 new = 50 (2025 numbering) |
| L-N 2025 data collection window | 2019-2023 (Israel outlier 2025) | per paper line 180-181 |

**Per-item vintage:** uniform 2019-2023 for the L-N 2025 application; for US-state projections, Phase D extraction window applies (TBD).

**Cross-confirmation:** [`../results/20260514_rubric_data_years.md`](../results/20260514_rubric_data_years.md) FOCAL 2024 row (HIGH confidence; explicit paper line citations).

---

## Per-item mappings (legal-axis core — this plan)

### Spec-doc → v2 row-name rename mapping

Phase 0 cross-check from this session (2026-05-18) surfaced 17 spec-doc-vs-v2 renames across FOCAL's full 58-row set; **15 affect this plan's legal-axis core** (the other 2 affect the openness battery, addressed in Plan 3). Most renames inherit from Sub-1 and Sub-2 families; FOCAL adds a few of its own.

| Spec doc working name | v2 compendium row id | Rename family |
|---|---|---|
| `compensation_threshold_for_lobbyist_registration` | `lobbyist_registration_threshold_compensation_dollars` | Sub-2 long-form rename |
| `expenditure_threshold_for_lobbyist_registration` | `lobbyist_registration_threshold_expenditure_dollars` | Sub-2 long-form rename |
| `time_threshold_for_lobbyist_registration` | `lobbyist_registration_threshold_time_percent` | Sub-2 long-form rename |
| `lobbyist_definition_included_actor_types` | `def_lobbyist_actor_types` | FOCAL-distinctive set-typed cell; v2 chose `def_*` prefix |
| `lobbying_definition_included_activity_types` | `def_lobbying_activity_types` | FOCAL-distinctive set-typed cell; v2 chose `def_*` prefix |
| `def_target_legislative_or_executive_staff` | **`def_target_legislative_staff` + `def_target_executive_staff` (SPLIT)** | v2 split staff into 2 cells (Open Q-2 below) |
| `lobbyist_disclosure_includes_employment_type` | `lobbyist_reg_form_includes_employment_type` | form-agnostic → reg-form (v2 freeze) |
| `lobbyist_report_includes_principal_names` | `lobbyist_spending_report_includes_principal_names` | Sub-1 `_report_` → `_spending_report_` |
| `principal_or_lobbyist_reg_form_includes_member_or_sponsor_names` | `lobbyist_or_principal_reg_form_includes_member_or_sponsor_names` | argument order normalization (lobbyist first) |
| `lobbyist_disclosure_includes_business_associations_with_officials` | `lobbyist_reg_form_includes_business_associations_with_officials` | form-agnostic → reg-form (v2 freeze; matches HG Q22 plan) |
| `lobbyist_spending_report_includes_compensation_broken_down_by_client` | `lobbyist_spending_report_includes_compensation_broken_down_by_payer` | Sub-1 `_by_client` → `_by_payer` |
| `lobbyist_report_includes_gifts_entertainment_transport_lodging` | `lobbyist_spending_report_includes_gifts_entertainment_transport_lodging` | Sub-1 `_report_` → `_spending_report_` |
| `principal_report_includes_gifts_entertainment_transport_lodging` | `principal_spending_report_includes_gifts_entertainment_transport_lodging` | Sub-1 `_report_` → `_spending_report_` |
| `lobbyist_report_includes_campaign_contributions` | `lobbyist_spending_report_includes_campaign_contributions` | Sub-1 `_report_` → `_spending_report_` |
| `principal_report_includes_total_expenditures` | `principal_spending_report_includes_total_expenditures` | Sub-1 `_report_` → `_spending_report_` |
| `lobbyist_or_principal_report_includes_lobbyist_count_total_and_FTE` | `lobbyist_or_principal_spending_report_includes_lobbyist_count_total_and_FTE` | Sub-1 `_report_` → `_spending_report_` |
| `lobbyist_or_principal_report_includes_time_spent_on_lobbying` | `lobbyist_or_principal_spending_report_includes_time_spent_on_lobbying` | Sub-1 `_report_` → `_spending_report_` |
| `lobbyist_or_principal_report_includes_trade_association_dues_or_sponsorship` | `lobbyist_or_principal_spending_report_includes_trade_association_dues_or_sponsorship` | Sub-1 `_report_` → `_spending_report_` |
| `principal_report_lists_lobbyists_employed` | `principal_spending_report_lists_lobbyists_employed` | Sub-1 `_report_` → `_spending_report_` |

(The spec doc proposed `principal_report_includes_direct_compensation` for FOCAL — but this row landed in v2 as `principal_spending_report_includes_compensation_paid_to_lobbyists`; FOCAL doesn't read it directly in any legal-core item, but it's reused via the financials.1-3 consultant-side mappings. See HG plan for the same rename.)

Carry the rename mapping in a module-level comment block in `focal_2024.py`.

### Scope battery (4 items in scope; weights 2+3+3+1)

| FOCAL item | Wt | v2 row(s) | Read shape |
|---|---|---|---|
| `scope.1` (lobbyist actor types) | 2 | `def_lobbyist_actor_types` (typed Set[enum]) | named helper — set-membership 3-tier |
| `scope.2` (no/low threshold for registration) | 3 | `lobbyist_registration_threshold_{compensation_dollars,expenditure_dollars,time_percent}` (3 typed cells) | named helper — calibrated 3-tier (see Open Q-1) |
| `scope.3` (8 target types included) | 3 | `def_target_{legislative_branch,executive_agency,governors_office,legislative_staff,executive_staff}` (5 binary cells) | named helper — AND-projection 3-tier |
| `scope.4` (activity breadth) | 1 | `def_lobbying_activity_types` (typed Set[enum]) | named helper — set-membership 3-tier |

**Named helpers** (per "scope.1" and "scope.4" set-membership patterns):

```python
def _project_focal_scope_set_membership(cell_set: frozenset, full_set: frozenset, partly_predicate: Callable) -> int:
    """Generic 3-tier set-membership: full → 2, partly → 1, narrow → 0."""
    if cell_set == full_set:
        return 2
    if partly_predicate(cell_set):
        return 1
    return 0
```

**scope.2 — calibrated 3-tier** (see Open Q-1 for cutoff calibration):

```python
def _project_focal_scope_2(cells, low_dollar_cutoff: Decimal, low_time_cutoff: Decimal) -> int:
    comp = cells.get("lobbyist_registration_threshold_compensation_dollars", {}).get("legal_availability")
    exp = cells.get("lobbyist_registration_threshold_expenditure_dollars", {}).get("legal_availability")
    time = cells.get("lobbyist_registration_threshold_time_percent", {}).get("legal_availability")
    any_threshold = (comp is not None) or (exp is not None) or (time is not None)
    significant = ((comp is not None and Decimal(comp) > low_dollar_cutoff)
                   or (exp is not None and Decimal(exp) > low_dollar_cutoff)
                   or (time is not None and Decimal(time) > low_time_cutoff))
    if significant:
        return 0
    if any_threshold:  # any threshold exists but none significant
        return 1
    return 2
```

**scope.3 — AND-projection 3-tier with v2 staff split:**

```python
def _project_focal_scope_3(cells) -> int:
    leg = bool(cells.get("def_target_legislative_branch", {}).get("legal_availability"))
    exec_ = bool(cells.get("def_target_executive_agency", {}).get("legal_availability"))
    gov = bool(cells.get("def_target_governors_office", {}).get("legal_availability"))
    # v2 splits FOCAL's "staff" into two cells; treat staff_in_scope as AND (strict reading per Open Q-2)
    leg_staff = bool(cells.get("def_target_legislative_staff", {}).get("legal_availability"))
    exec_staff = bool(cells.get("def_target_executive_staff", {}).get("legal_availability"))
    staff_in_scope = leg_staff and exec_staff
    major_branches = leg and exec_ and gov
    if major_branches and staff_in_scope:
        return 2
    if major_branches and not staff_in_scope:
        return 1
    return 0
```

### Descriptors battery (6 items, all in scope; weights 2+1+1+1+1+1)

All 6 items are single-cell `IS NOT NULL` / binary reads on `legal_availability` axis. Spec-table entries:

| FOCAL item | Wt | v2 row | Read rule |
|---|---|---|---|
| `descriptors.1` (full names) | 2 | `lobbyist_reg_form_includes_lobbyist_full_name` | `cell == TRUE → 2; FALSE → 0` (no partly tier projectable; "incomplete" sub-tier deferred — see Open Q-3) |
| `descriptors.2` (contact details) | 1 | `lobbyist_reg_form_includes_lobbyist_contact_details` | binary → 2 (same as .1) |
| `descriptors.3` (legal form) | 1 | `lobbyist_reg_form_includes_lobbyist_legal_form` | typed `IS NOT NULL → 2` (binary projection) |
| `descriptors.4` (business id) | 1 | `lobbyist_reg_form_includes_lobbyist_business_id` | binary → 2 |
| `descriptors.5` (sector) | 1 | `lobbyist_reg_form_includes_lobbyist_sector` | typed `IS NOT NULL → 2` |
| `descriptors.6` (contract type) | 1 | `lobbyist_reg_form_includes_employment_type` | binary → 2 |

**Note on "partly" tier:** FOCAL Suppl Table 3 declares "P=some entries incomplete" for descriptors.1, .2, .4 — but this is a data-quality observable not extractable from the v2 binary cells. **YAGNI: project at binary granularity (full → 2, missing → 0); skip partly tier.** Open Q-3 below documents the choice.

### Relationships battery (4 items + 1 2025-only addition; weights 2+1+1+2+3)

| FOCAL item | Wt | v2 row(s) | Read shape |
|---|---|---|---|
| `relationships.1` (client list) | 2 | `lobbyist_spending_report_includes_principal_names` OR `lobbyist_reg_form_lists_each_employer_or_principal` | OR binary → 2 |
| `relationships.2` (member/sponsor names) | 1 | `lobbyist_or_principal_reg_form_includes_member_or_sponsor_names` | binary → 2 |
| `relationships.3` (board seats) | 1 | `lobbyist_or_principal_reg_form_includes_lobbyist_board_memberships` | binary → 2 |
| `relationships.4` (business associations with officials) | 2 | `lobbyist_reg_form_includes_business_associations_with_officials` | binary → 2 (FOCAL "partly" tier on detail-level deferred — see Open Q-4) |
| `relationships.lobbyist_list_2025` (2025-only) | 3 | `principal_spending_report_lists_lobbyists_employed` | binary → 2 |

**2025-only indicator:** added to relationships battery per Lacy-Nichols 2025 line 213. Projects only when `vintage == 2025`. The spec table carries a `min_vintage` annotation:

```python
_ATOMIC_SPEC["relationships.lobbyist_list_2025"] = (
    "principal_spending_report_lists_lobbyists_employed",
    _LEGAL,
    weight=3,
    min_vintage=2025,
)
```

The dispatcher skips items with `min_vintage > current_vintage`. For 2024-vintage projections, this item is **not** scored; for 2025-vintage projections, it adds up to 6 raw points (weight 3 × max 2).

### Revolving door battery (1 item in scope; weight 3)

| FOCAL item | Wt | v2 row | Read rule |
|---|---|---|---|
| `revolving_door.1` | 3 | `lobbyist_reg_form_includes_lobbyist_prior_public_offices_held` | binary → 2 |

`revolving_door.2` is OUT (FOCAL-1 user-decision); the dispatcher's `_OOS_ITEMS` set includes it.

### Financials battery (11 items, all in scope; weights 2+2+2+1+2+2+2+2+1+2+2)

| FOCAL item | Wt | v2 row(s) | Read shape |
|---|---|---|---|
| `financials.1` (total income) | 2 | `lobbyist_spending_report_includes_total_compensation` | binary → 2 |
| `financials.2` (income per client) | 2 | `lobbyist_spending_report_includes_compensation_broken_down_by_payer` | binary → 2 |
| `financials.3` (income source types) | 2 | `consultant_lobbyist_report_includes_income_by_source_type` (typed Set[enum]) | typed `IS NOT NULL → 2` (partly tier deferred) |
| `financials.4` (lobbyist count + FTE) | 1 | `lobbyist_or_principal_spending_report_includes_lobbyist_count_total_and_FTE` (typed structured) | typed `IS NOT NULL → 2` (partly tier reads FTE sub-field — deferred) |
| `financials.5` (time on lobbying) | 2 | `lobbyist_or_principal_spending_report_includes_time_spent_on_lobbying` (typed structured) | typed `IS NOT NULL → 2` |
| `financials.6` (total expenditure both in-house + consulting) | 2 | `lobbyist_spending_report_includes_total_expenditures` AND `principal_spending_report_includes_total_expenditures` | named helper — AND 3-tier |
| `financials.7` (compensated/uncompensated) | 2 | `lobbyist_reg_form_includes_employment_type` (reuse Q10/descriptors.6) | `IS NOT NULL → 2` |
| `financials.8` (expenditure per issue) | 2 | `lobbyist_spending_report_includes_expenditure_per_issue` | binary → 2 |
| `financials.9` (membership/sponsorship spending) | 1 | `lobbyist_or_principal_spending_report_includes_trade_association_dues_or_sponsorship` | binary → 2 |
| `financials.10` (expenditures benefiting officials) | 2 | `lobbyist_spending_report_includes_gifts_entertainment_transport_lodging` OR `principal_spending_report_includes_gifts_entertainment_transport_lodging` | named helper — OR binary → 2 (reuse `project_gifts_actor_agnostic_or` from `newmark_2017` if available) |
| `financials.11` (campaign contributions) | 2 | `lobbyist_spending_report_includes_campaign_contributions` | binary → 2 |

**Note on `financials.7` cell reuse:** spec doc proposed a new cell `lobbyist_reg_form_or_report_includes_compensation_status_flag`; **the FOCAL author then revised the recommendation** (spec line 607) to reuse HG Q10's `lobbyist_reg_form_includes_employment_type` via `IS NOT NULL → 2`. v2 carries the HG cell; no new row needed. Module reads the same v2 cell as `descriptors.6` and `financials.7`.

**Note on `financials.6` helper:** AND-projection over lobbyist-side + principal-side total-expenditures cells. The FOCAL spec's "partly" tier ("general bandwidth") is not operationally readable — collapse to AND-binary 3-tier:

```python
def _project_focal_financials_6(cells) -> int:
    lob = bool(cells.get("lobbyist_spending_report_includes_total_expenditures", {}).get("legal_availability"))
    prin = bool(cells.get("principal_spending_report_includes_total_expenditures", {}).get("legal_availability"))
    if lob and prin:
        return 2
    if lob or prin:
        return 1
    return 0
```

**Note on `financials.10` helper sharing:** if Newmark 2017 has shipped, import `project_gifts_actor_agnostic_or` from `lobby_analysis.projections.newmark_2017`. Otherwise inline the OR. The helper returns binary 0/1 (not 0/2); FOCAL's projection then multiplies by 2 to reach the FOCAL raw score (FOCAL is per-indicator 0/1/2 with weight-multiplier later, so binary → 2 if TRUE).

---

## Standard module structure

```
src/lobby_analysis/projections/focal_2024.py        # the projection module (this plan + 3 companion plans contribute)
tests/projections/test_focal_2024_per_item.py       # per-atomic-item tests (this plan owns the legal-core subset)
tests/projections/test_focal_2024_ground_truth.py   # ground-truth loader tests (Federal US LDA + spot-check countries)
tests/projections/test_focal_2024_aggregation.py    # aggregation + Federal US LDA end-to-end + rank (Plan 4 owns)
```

Module shape (this plan introduces; companion plans extend):

- Module docstring naming spec doc + ground-truth path + dual-validation-regime explanation (Federal US LDA = Strong; US states = Cross-rubric only).
- Constants: `_ATOMIC_ITEMS_LEGAL_CORE: tuple[str, ...] = (...)` (26 IDs); `_ATOMIC_ITEMS_CONTACT_LOG`, `_ATOMIC_ITEMS_OPENNESS_TIMELINESS` reserved for companion plans; `_OOS_ITEMS: frozenset[str] = frozenset({"revolving_door.2"})`; `_LEGAL = "legal_availability"`, `_PRACTICAL = "practical_availability"`.
- Score model (Pydantic `BaseModel`, frozen): `Focal2024Score` with `jurisdiction` (USPS code or `"Federal_US"`), `vintage` (int), `atomic_scores: dict[str, int]` (raw 0/1/2 per indicator), `per_battery_subtotals: dict[str, int]` (8 batteries — for diagnostics, NOT used for FOCAL's published score per Open Q-5), `total_raw` (sum of weighted raw scores, ∈ [0, 180] for 2024 vintage or ∈ [0, 186] for 2025 vintage), `pct` (total_raw / max).
- Spec table: `_ATOMIC_SPEC: dict[str, Spec]` where `Spec = NamedTuple("Spec", [("row_ids", tuple[str, ...]), ("axis", str), ("weight", int), ("helper", Optional[Callable]), ("min_vintage", Optional[int])])`. This plan adds 26 entries.
- Per-item dispatcher: `_project_atomic(item_id, cells, vintage, calibration) -> int` reads spec, calls helper if specified or applies binary/`IS NOT NULL` default, returns raw 0/1/2.
- Per-item layer: 5 named helpers (scope.1, .2, .3, .4, financials.6, financials.10).
- Top-level: `project_focal_2024(cells, jurisdiction, vintage)` — **lives in Plan 4** (aggregation). This plan ships only the per-item dispatcher.
- Ground-truth loader stub: `load_focal_2024_per_country_reference(repo_root)` — reads `focal_2025_lacy_nichols_per_country_scores.csv`, returns dict[country_code, dict[indicator_id, int]]. Per-item subset for the 26 legal-core indicators; companion plans expand.

---

## Test structure

Per the test-driven-development skill: write all tests first, watch them fail, write minimal code to pass.

### Per-item tests (`test_focal_2024_per_item.py` — legal-core subset)

- **Scope battery** (4 items): 
  - scope.1: 3 fixture cases (full set → 2; {prof_consultant + other types} → 1; {prof_consultant} only → 0).
  - scope.2: parameterize over (`{comp, exp, time}` ∈ {None, low, high}^3) with default calibration cutoffs from Open Q-1. Truth table: 27 cases per default; spot-check 5.
  - scope.3: 2^5 = 32 truth-table cases over 5 binary cells; assert scoring rule.
  - scope.4: 3 fixture cases parallel to scope.1.
- **Descriptors battery** (6 items): parameterize each over {TRUE, FALSE, missing} cell → expected {2, 0, 0}. 18 cells.
- **Relationships battery** (4 + 1 items): parameterize each binary read; relationships.1 OR-projection over 2 cells × 4 truth-table cases. 2025-only item: 2 vintage cases (`vintage=2024` → not scored; `vintage=2025` → scored).
- **Revolving door** (1 item): 3 cases (TRUE → 2; FALSE → 0; missing → 0).
- **Financials battery** (11 items): per-item truth-table; financials.6 AND-projection 4 cases; financials.10 OR-projection 4 cases.

**Estimated per-item test cells:** ~80 truth-table cells for legal-core subset.

### Ground-truth loader tests (`test_focal_2024_ground_truth.py` — extends in companion plans)

- Federal US LDA row exists in CSV with the 26 legal-core indicators populated.
- Per-indicator value-range bounds (every legal-core indicator ∈ {0, 1, 2}).
- Spot-check 3 non-US countries against the published L-N 2025 Suppl File 1 Table 5: Canada (49%), Chile (48%), Netherlands (9%). Indicator-level reads.
- **Aggregation harness lives in Plan 4** — this plan only seeds the loader.

### Cross-rubric overlap tests (extension)

For each row FOCAL shares with another Phase C-shipped module (CPI/PRI/Sunlight/Newmark/Opheim/HG), project a synthetic state's cell through both modules; assert per-item agreement on the binary contributing value. Specifically:

- `lobbyist_spending_report_includes_total_compensation` (financials.1) — 7+ readers; the cross-rubric agreement on this one row is the foundation for Phase 4 audit.
- `lobbyist_spending_report_includes_compensation_broken_down_by_payer` (financials.2) — 5-rubric-confirmed.
- `lobbyist_spending_report_includes_gifts_entertainment_transport_lodging` (financials.10) + principal-side — 5-rubric-confirmed bundle.
- `lobbyist_registration_threshold_compensation_dollars` (scope.2 input) — 5-rubric-confirmed at varying granularities.
- 5 `def_target_*` cells (scope.3 inputs) — 4-rubric-confirmed.
- `lobbyist_reg_form_includes_employment_type` (descriptors.6 / financials.7) — 2-rubric-confirmed with HG Q10 once HG ships.

---

## Open questions for the implementing agent

5 questions surfaced during this plan's drafting; confirm before launch:

1. **scope.2 calibration cutoffs (`LOW_DOLLAR_CUTOFF` / `LOW_TIME_CUTOFF`).** Sub-0 flagged this as a Phase C decision; FOCAL 2024 paper line 1206-1208 acknowledges scorer-judgment. **Candidate defaults:** $1000 / 8 hours / 5% time (the spec doc's suggestion). 
   - **Recommendation:** ship with `LOW_DOLLAR_CUTOFF = Decimal("1000")` and `LOW_TIME_CUTOFF = Decimal("5")` (percent) as module constants; allow per-test override via fixture for calibration sensitivity analysis.
   - **Empirical-fit alternative:** if Federal US LDA validation fails with these defaults (US scored 0 = significant threshold; LDA's threshold is $3000 compensation per quarter + 20% time), fit cutoffs to maximize Federal US LDA's projected scope.2 = published scope.2 (= 0). With $3000 compensation threshold, US scope.2 = 0 holds for any cutoff < $3000. **Defaults likely safe.**
   - Flag for the implementing agent to validate against the Federal US LDA row before sweeping to states.

2. **scope.3 staff-cell read — AND or OR of legislative_staff + executive_staff?** v2 split FOCAL's single `def_target_legislative_or_executive_staff` into 2 cells; FOCAL's "partly" tier says "P=staff excluded" — but at what aggregation? Strict reading: BOTH must be in scope for `staff_in_scope = TRUE`. Loose reading: EITHER.
   - **Recommendation:** AND (strict). Federal US LDA scored 0 on scope.3 (per L-N 2025), likely because LDA's "covered staff" definition is narrow (only some staff); the strict AND reading aligns with that interpretation.
   - **Validation tolerance:** if Federal US LDA projects scope.3 = 1 (partly) under AND-read but published is 0 (no), revisit. **Flag for the implementing agent.**

3. **Descriptors "partly" tier (FOCAL Suppl Table 3 "P=some entries incomplete").** This is a data-quality observable not extractable from v2 binary cells. Spec proposed `TRUE AND complete → 2; TRUE AND incomplete → 1; FALSE → 0`; YAGNI says collapse to binary `TRUE → 2; FALSE → 0`.
   - **Recommendation:** YAGNI — project at binary granularity. Document in module docstring that the FOCAL "partly" sub-tier is structurally invisible to this projection (extraction-completeness sub-observable not in v2 freeze). Phase C tolerance: states where FOCAL would score 1 on descriptors.* are projected as 0 (under-scoring) or 2 (over-scoring) depending on the underlying portal observation. **Quantified:** descriptors weights sum 7 max; max systematic under-scoring per state from descriptors-partly-tier ~3-4 raw points. Within typical inter-coder reliability.

4. **relationships.4 "partly" tier on business-association detail.** FOCAL distinguishes binary disclosure (Y/N — HG Q22 reads this) from detailed disclosure (nature of relationship). v2 has the binary cell only.
   - **Recommendation:** YAGNI — project at binary granularity (TRUE → 2; FALSE → 0). The FOCAL "partly" tier (`TRUE AND only_yn_no_relationship_details → 1`) is not operationally readable from v2.
   - **STOP clause:** if Federal US LDA's relationships.4 published value is 1 (partly) and projection produces 0 (no — LDA doesn't require this disclosure), the binary read is correct; if projection produces 2 (yes) but published is 1, flag for the user — may need a detail-level cell upgrade.

5. **Per-battery subtotal API — informational only or load-bearing?** The FOCAL paper publishes per-country per-battery subtotals (e.g., Federal US LDA: Scope 6 / Timeliness 0 / Openness 27 / Descriptors 8 / Revolving_door 6 / Relationships 8 / Financials 16 / Contact_log 10 = total 81). The score model exposes `per_battery_subtotals: dict[str, int]` for diagnostics.
   - **Recommendation:** expose as informational (mirror Newmark 2005's `no-sub-aggregate-validation` discipline — sub-aggregates available for diagnostics but tests do NOT assert equality against published values, because L-N 2025's per-battery breakdown may have FOCAL-5 ordering ambiguity per spec doc).
   - **Phase 4 audit prototype** may want to assert per-battery agreement against L-N 2025 Table 5 verbatim; that's Plan 4's call.

---

## Stream-3 / no-blocking-dependency note

FOCAL has no blocking dependencies on other Stream-3 rubrics for landing.

**Optional helper imports** (improve cross-rubric reuse if available):

- `project_gifts_actor_agnostic_or` from `lobby_analysis.projections.newmark_2017` (used in financials.10). If Newmark 2017 has shipped, import; otherwise inline OR. Module docstring notes the conditional reuse.
- No other helpers shared.

---

## Phase 4 cross-rubric agreement audit feed

After FOCAL ships (all 4 plans landed), the following rows reach milestone confirmation levels:

- `lobbyist_spending_report_includes_total_compensation` → **8-rubric-confirmed** (CPI + PRI + Sunlight + Newmark 2017 + Newmark 2005 + Opheim + HG + FOCAL). Single most-validated row in compendium.
- `lobbyist_spending_report_includes_compensation_broken_down_by_payer` → **6-rubric-confirmed**.
- Gifts/entertainment/transport/lodging bundle → **6-rubric-confirmed at combined granularity**.
- 36 NEW FOCAL rows become single-rubric-confirmed (FOCAL-distinctive). LobbyView schema-coverage check may promote ~5 of them (descriptors + relationships + openness) to 2-rubric.

---

## Closing the loop

This plan is part of a 4-plan FOCAL set; the closing checklist runs **once** at FOCAL completion (Plan 4):

1. Convo file at `convos/YYYYMMDD_focal_2024_tdd.md` — covers all 4 plans' implementation sessions.
2. Results doc at `results/YYYYMMDD_focal_2024_projection.md` — what landed, validation outcome (Federal US LDA 81/180 exact match expected), naming-drift corrections, items skipped per YAGNI.
3. RESEARCH_LOG.md entry — links to convo + results, topics, findings, decisions, next steps.
4. STATUS.md — append one-liner; update `phase-c-projection-tdd` row to reflect rubric #8 complete; Phase C complete (all 8 rubrics shipped).
5. Commit + push per plan. Final aggregation commit message: `convo: <convo-name> — focal_2024: rubric #8 (last) shipped`.
