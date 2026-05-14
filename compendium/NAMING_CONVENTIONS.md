# `compendium/` — Row-naming conventions

> **Status:** draft, 2026-05-14. Audit produced on the `compendium-naming-docs` branch (GH issue [#9](https://github.com/danparshall/lobby_analysis/issues/9)). Scope is **audit + flag**, not rename — see [Naming issues](#naming-issues--rename-candidates) for the rename candidates this audit surfaces; renames are deferred to a separately-scoped follow-up branch to avoid forcing merge churn on the parallel-running successor branches (`phase-c-projection-tdd`, `extraction-harness-brainstorm`, `oh-statute-retrieval`).

This document explains how `compendium_row_id` strings in [`disclosure_side_compendium_items_v2.tsv`](disclosure_side_compendium_items_v2.tsv) are structured, what each prefix family means, where every row's name came from, and how to choose a name for a new row.

It is the long-form companion to `compendium/README.md` (which covers the row-shape contract) and the canonical reference for the naming decisions made during the Compendium 2.0 row-freeze on 2026-05-13.

---

## 1. Row-ID shape

Every `compendium_row_id` is a single snake-case identifier built as

```
<actor_or_scope>_<artifact>_<predicate>
```

read left-to-right from the broadest scope to the most specific predicate. For example:

```
lobbyist_spending_report_includes_total_compensation
└────────┘ └──────────────┘ └────────────────────────┘
  actor      artifact                predicate
```

There is no formal grammar — the row IDs grew organically across nine source-rubric extraction passes — but the empirical structure is consistent enough to enumerate as prefix families.

**Row-ID length distribution** (181 rows, by token count after splitting on `_`):

| Tokens | Count |
|---:|---:|
| 3 | 1 |
| 4 | 19 |
| 5 | 37 |
| 6 | 64 |
| 7 | 33 |
| 8 | 13 |
| 9 | 9 |
| 10 | 5 |

Median is 6 tokens. The longest IDs are descriptive predicates inside dense families (e.g., `lobbyist_spending_report_scope_includes_household_members_of_officials`).

---

## 2. Top-level prefix families (1-token)

20 distinct 1-token prefixes. The first six account for 159 of 181 rows.

| Prefix | Count | Role |
|---|---:|---|
| `lobbyist_*` | 70 | Lobbyist-side observables (the natural person or firm registered to lobby): registration forms, spending reports, directory listings, filing requirements |
| `lobbying_*` | 43 | Process / portal observables (the *activity* of lobbying, the *data system* exposing it): search filters, contact logs, data quality, disclosure-documents access |
| `principal_*` | 23 | Principal-side observables (the entity employing or paying the lobbyist): spending reports, listings |
| `actor_*` | 11 | Institutional-actor registration requirements (PRI A1–A11): one row per actor type (`actor_executive_agency_*`, `actor_volunteer_lobbyist_*`, etc.) |
| `def_*` | 8 | Definitional rows (legal definitions): `def_target_*` (target of lobbying), `def_actor_class_*` (individual-actor classes like elected officials) |
| `oversight_*` | 4 | Oversight-agency publishing behavior (HG practical-axis: aggregate spending publications, e-file training) |
| `public_*` | 3 | Public-entity definition criteria |
| `exemption_*` | 2 | Exemption-from-disclosure provisions |
| `expenditure_*` | 2 | Expenditure observables (one rename candidate — see issues) |
| `govt_*` | 2 | Government-agency disclosure-subject status |
| `law_*` | 2 | Statutory-content properties (definitions and materiality tests) |
| `ministerial_*` | 2 | Ministerial-diary practical observables (FOCAL) |
| `online_*` | 2 | Online-filing portal availability (HG practical-axis) |
| `compensation_*` | 1 | Singleton — registration-threshold row (see [Naming issues](#naming-issues--rename-candidates)) |
| `consultant_*` | 1 | Singleton — consultant-lobbyist sub-type income disclosure (FOCAL) |
| `registration_*` | 1 | Singleton — registration-deadline row (rename candidate) |
| `sample_*` | 1 | Singleton — HG: sample filing forms available online |
| `separate_*` | 1 | Singleton — OS-1 path-b unvalidated row |
| `state_*` | 1 | Singleton — HG: state has dedicated lobbying website |
| `time_*` | 1 | Singleton — registration-threshold row (rename candidate) |

The keying choice between `lobbyist_*` and `lobbying_*` tracks **whose observable it is**: a `lobbyist_*` row is a property of the lobbyist's filings or the lobbyist as an entity; a `lobbying_*` row is a property of the lobbying activity or the data system that exposes it. This split was not a single explicit decision — it emerged from the nine per-rubric extraction passes — but it holds consistently across the 181 rows.

---

## 3. Strong 3-token families

The empirically tightest families. These are the "real" structural anchors for new rows: if a proposed row fits one of these families, it should use the family prefix.

| Family prefix | Count | Meaning |
|---|---:|---|
| `lobbyist_spending_report_*` | 34 | Content / structure / cadence / scope of the lobbyist-side spending report (PRI E2 + cross-rubric companions). The α form-type split target — see [§5 below](#5-the-α-form-type-split-d3) |
| `principal_spending_report_*` | 21 | Content / structure / cadence of the principal-side spending report (PRI E1 + CPI-distinctive content) |
| `lobbying_search_filter_*` | 15 | Per-criterion search-filter capabilities on the portal (PRI Q7a-o atomized, +1 multicriteria capability) |
| `lobbyist_reg_form_*` | 13 | Content fields on the lobbyist's registration form (HG Q22 + FOCAL `descriptors.*`) |
| `lobbying_contact_log_*` | 9 | Per-field content of the contact log (FOCAL `contact_log` atomized) |
| `lobbying_data_*` | 8 | Data-system / portal-data quality observables (FOCAL openness + PRI Q3/Q11) |
| `def_target_*` | 6 | Target classes of lobbying (legislative/executive/independent/governor's office/legislative-staff/executive-staff) |
| `lobbying_disclosure_*` | 6 | Disclosure-documents access (online, free, audited, unique-IDs, linked, response-time) |
| `lobbyist_directory_*` | 5 | Directory of registered lobbyists, availability format + update cadence (HG Q31/Q32) |
| `lobbyist_or_principal_*` | 5 | Joint-actor rows: same observable applies to either side (see [§6 below](#6-joint-actor-rows-d7)) |
| `lobbyist_itemized_expenditure_*` | 4 | Per-item content of itemized expenditures (HG) |
| `oversight_agency_*` | 4 | Oversight agency publishing + training behavior (HG practical-axis) |
| `lobbyist_registration_*` | 3 | Registration administration: amendment deadline, renewal cadence, required (CPI/HG two-axis) |
| `public_entity_def_*` | 3 | Criteria the public-entity definition relies on (charter / ownership / revenue structure) |
| `def_actor_class_*` | 2 | Individual-actor classes (elected officials / public employees) |
| `govt_agencies_subject_*` | 2 | Whether government agencies are themselves subject to lobbyist / principal disclosure |
| `lobbyist_filing_*` | 2 | Filing-de-minimis thresholds (D4 — see [§7 below](#7-the-three-threshold-framework-d4)) |
| `lobbyist_report_*` | 2 | Two leftover rows after D3 — flagged as rename candidates |
| `online_lobbyist_*` | 2 | Online-filing portal availability (HG practical-axis) |

Plus 34 singleton families (one row each) — see the [prefix survey](../docs/active/compendium-naming-docs/results/20260514_prefix_survey.md) for the full listing.

---

## 4. The `def_*` / `actor_*` triangle

The three definitional / actor-typing families capture **co-existing** axes of disclosure-law structure. They are not alternatives — a state's regime answers all three families independently.

| Family | Members | What it captures |
|---|---|---|
| `def_target_*` (6) | `legislative_branch`, `executive_agency`, `governors_office`, `independent_agency`, `legislative_staff`, `executive_staff` | **Target side.** Which institutional targets count as "lobbyable" under the statute's definition. 6-rubric confirmed on `def_target_legislative_branch`. |
| `def_actor_class_*` (2) | `elected_officials`, `public_employees` | **Lobbied-individual class.** Which individual-actor classes a target row covers. 3-rubric confirmed. |
| `actor_*_registration_required` (11) | `executive_agency`, `governors_office`, `independent_agency`, `intergov_agency_lobbying`, `legislative_branch`, `lobbying_firm`, `local_government`, `paid_lobbyist`, `principal`, `public_entity_other`, `volunteer_lobbyist` | **Lobbyist side.** Which institutional-actor types must register as lobbyists themselves. PRI A1–A11 (all 11 single-rubric per D25). |

Per D25 of the row-freeze log: all three families KEEP at this freeze. The naming separation is load-bearing — collapsing them would lose the disclosure-law structural distinction.

---

## 5. The α form-type split (D3)

For every artifact-content observable, there are potentially *two* compendium rows:

- one on the **reg-form** side: `lobbyist_reg_form_includes_*` or `principal_reg_form_includes_*`
- one on the **spending-report** side: `lobbyist_spending_report_includes_*` or `principal_spending_report_includes_*`

This is the **α form-type split** convention. The same content cell (e.g., "specific bill number") exists separately for the registration form vs the spending report, because states require it on one, the other, both, or neither — and the projection functions need to distinguish.

D3 of the row-freeze log enacted this convention by renaming **24 rows** that had used the ambiguous `lobbyist_report_includes_*` or `principal_report_includes_*` prefix (PRI E1/E2 atomic items) to use the explicit `*_spending_report_includes_*` prefix. Two leftover `lobbyist_report_*` rows survived D3's rename rule (which keyed off `_includes_*` and `_cadence_*` patterns) and are now [naming issues](#naming-issues--rename-candidates).

**Practical consequence for new rows:** if you're adding an observable about the content of a state-required artifact, ask first which artifact (reg form vs spending report); then use the matching family prefix. Generic `*_report_*` is not a current convention.

---

## 6. Joint-actor rows (D7)

The `lobbyist_or_principal_*` prefix (5 rows) marks observables that **apply to either side** — the underlying disclosure exists, but the rubrics cited it without specifying actor side. D7 of the row-freeze log made the explicit decision to keep these combined rather than splitting each into lobbyist + principal variants (YAGNI vs granularity-bias: split if a real rubric reads the distinction).

Members:

- `lobbyist_or_principal_reg_form_includes_lobbyist_board_memberships`
- `lobbyist_or_principal_report_includes_lobbyist_count_total_and_FTE`
- `lobbyist_or_principal_report_includes_time_spent_on_lobbying`
- `lobbyist_or_principal_report_includes_trade_association_dues_or_sponsorship`
- `lobbyist_or_principal_spending_report_includes_contributions_received_for_lobbying`

**Ordering convention: `lobbyist_or_principal_*` (alphabetical-by-actor-prominence, not alphabetical-by-string).** One outlier — `principal_or_lobbyist_reg_form_includes_member_or_sponsor_names` — uses the reverse order. Flagged as a [rename candidate](#naming-issues--rename-candidates).

**Mixed-form behavior:** three of the five rows use the legacy `_report_*` form-type label (not `_spending_report_*`). D3's rename rule was scoped to PRI E1/E2 rows and didn't extend to the joint-actor family — see [rename candidates](#naming-issues--rename-candidates).

---

## 7. The three-threshold framework (D4)

Disclosure law uses *three distinct* dollar/time thresholds, and the compendium uses three distinct prefix conventions to keep them apart (per Sunlight 2015 mapping's Decision Rule 6, made canonical at D4 of the row-freeze):

| Threshold concept | Prefix shape | Members |
|---|---|---|
| **Lobbyist-status threshold** — triggers the obligation to register as a lobbyist at all | `<measure>_threshold_for_lobbyist_registration` (singletons) | `compensation_threshold_for_lobbyist_registration`, `expenditure_threshold_for_lobbyist_registration`, `time_threshold_for_lobbyist_registration` |
| **Filing-de-minimis threshold** — once registered, triggers the obligation to file spending reports | `lobbyist_filing_de_minimis_threshold_*` | `lobbyist_filing_de_minimis_threshold_dollars`, `lobbyist_filing_de_minimis_threshold_time_percent` |
| **Itemization-de-minimis threshold** — once filing, triggers per-line itemization within a report | `*_itemization_de_minimis_threshold_*` (singleton) | `expenditure_itemization_de_minimis_threshold_dollars` |

The three-threshold framework is load-bearing for HG Q2's projection (D22: `min(compensation_threshold, expenditure_threshold)` reads the binding-threshold concept).

The lobbyist-status threshold family is currently three singletons with **inconsistent prefix shape** — none of them join the `lobbyist_registration_*` (3-row) family even though semantically they all gate registration. Flagged as [rename candidates](#naming-issues--rename-candidates).

---

## 8. Practical-axis vs legal-axis families

The `axis` column on each row is `legal`, `practical`, or `legal+practical`. Prefix conventions don't directly encode axis — but several families lean heavily one way:

**Predominantly legal-axis families:**
- `principal_*` (23 of 23 legal)
- `actor_*` (11 of 11 legal)
- `def_*` (8 of 8 legal)
- `public_*` (3 of 3 legal)
- `exemption_*`, `expenditure_*`, `govt_*`, `law_*` (all legal)

**Predominantly practical-axis families:**
- `oversight_*` (4 of 4 practical)
- `online_*` (2 of 2 practical) — portal-availability rows
- `ministerial_*` (2 of 2 practical)
- `lobbying_*` (31 of 43 practical) — portal/search/contact-log/data observables
- `state_*`, `sample_*` (singletons, practical)

**Mixed `lobbyist_*` family** (70 rows): 59 legal, 9 practical, 2 legal+practical. The `lobbyist_directory_*` and `lobbyist_registration_*` two-axis rows (D10, D11) are the dominant `legal+practical` cases.

When introducing a new row, **don't try to encode axis in the prefix** — it goes in the `axis` column. The `online_*` prefix is the one exception: it's a practical-axis-only family by convention because the "is there an online filing system" question only has meaning at the portal level.

---

## 9. Cell-type conventions (for context, not row-ID)

`compendium_row_id` doesn't encode `cell_type`, but the suffix often hints at it:

| Suffix shape | Typical cell_type | Examples |
|---|---|---|
| `_required` | `binary` | `lobbyist_spending_report_required`, `actor_paid_lobbyist_registration_required` |
| `_includes_*` | `binary` | most of the spending-report and reg-form content rows |
| `_threshold_*_dollars` | `typed Optional[Decimal]` | `lobbyist_filing_de_minimis_threshold_dollars`, `compensation_threshold_for_lobbyist_registration` |
| `_threshold_time_percent` | `typed Optional[TimeThreshold]` | `lobbyist_filing_de_minimis_threshold_time_percent`, `time_threshold_for_lobbyist_registration` |
| `_cadence_*` | `binary` (PRI atomized as 6-binary set) or `typed UpdateCadence` (HG) | `lobbyist_spending_report_cadence_includes_quarterly`, `lobbyist_directory_update_cadence` |
| `_def_*` / `_definition_*` | `typed Set[enum]` | `lobbying_definition_included_activity_types`, `lobbyist_definition_included_actor_types` |
| `_filter_by_*` | `binary` | the `lobbying_search_filter_*` family |
| `_required_in_law` / `_available_*` | `binary` | self-explanatory practical-availability rows |

These are conventions, not rules — the `cell_type` column is authoritative. If you're adding a row, write a suffix that hints at the cell_type, but **don't infer cell_type from suffix alone**.

---

## 10. Naming issues / rename candidates

This audit surfaces the following inconsistencies. None are blocking — the v2 TSV is the active contract and every row resolves to a single canonical name. But each is a rename candidate for a future cleanup branch, listed roughly in order of how clearly the rename is justified.

> **Coordination cost reminder:** any rename of a row that appears in a projection-mapping doc, a Pydantic model on `extraction-harness-brainstorm`, or a prompt string forces a merge update across those branches. The follow-up branch should be timed against their lifecycles.

### Issue 1 — `principal_or_lobbyist_*` reversed ordering (1 row)

**Row:** `principal_or_lobbyist_reg_form_includes_member_or_sponsor_names`
**Issue:** Joint-actor rows use `lobbyist_or_principal_*` ordering (5 of 5 other rows). This one row reverses it. Same convention, opposite alphabetic order.
**Proposed rename:** `lobbyist_or_principal_reg_form_includes_member_or_sponsor_names`
**Cost:** 1 row; FOCAL-introduced; single-rubric.

### Issue 2 — D3 rename gaps: leftover `_report_*` rows that should be `_spending_report_*` (5 rows)

D3 enacted the α form-type split (`*_report_includes_*` → `*_spending_report_includes_*`) but keyed the rename rule on `_includes_*` and `_cadence_*` patterns inside PRI E1/E2 only. Five non-PRI rows that are *also* spending-report observables retained the legacy ambiguous `_report_*` prefix:

| Current row_id | Source rubric | Proposed rename |
|---|---|---|
| `lobbyist_report_distinguishes_in_house_vs_contract_filer` | LV-1 (LobbyView, D12 promotion) | Either `lobbyist_filing_distinguishes_in_house_vs_contract_filer` (it's a filing-system property, not a single report's content) or `lobbyist_spending_report_distinguishes_in_house_vs_contract_filer` |
| `lobbyist_report_includes_campaign_contributions` | Newmark 2017 | `lobbyist_spending_report_includes_campaign_contributions` |
| `lobbyist_or_principal_report_includes_lobbyist_count_total_and_FTE` | FOCAL | `lobbyist_or_principal_spending_report_includes_lobbyist_count_total_and_FTE` |
| `lobbyist_or_principal_report_includes_time_spent_on_lobbying` | FOCAL | `lobbyist_or_principal_spending_report_includes_time_spent_on_lobbying` |
| `lobbyist_or_principal_report_includes_trade_association_dues_or_sponsorship` | FOCAL | `lobbyist_or_principal_spending_report_includes_trade_association_dues_or_sponsorship` |
| `principal_report_lists_lobbyists_employed` | FOCAL | `principal_spending_report_lists_lobbyists_employed` |

(The LV-1 row is the one with a non-trivial choice — it could reasonably belong to a `lobbyist_filing_*` family-of-meta rather than a `_spending_report_*` family-of-content. Defer the call until the rename-execution session.)

### Issue 3 — Registration-threshold family lives outside the registration family (3 rows)

Three singleton rows capture the **lobbyist-status threshold** (D4's first concept in the three-threshold framework). They use a `<measure>_threshold_for_lobbyist_registration` shape that joins no family:

- `compensation_threshold_for_lobbyist_registration`
- `expenditure_threshold_for_lobbyist_registration`
- `time_threshold_for_lobbyist_registration`

**Issue:** they share no prefix with each other (`compensation_*`, `expenditure_*`, `time_*` are three different 1-token prefix families), they don't join `lobbyist_registration_*` (3-row family for registration administration), and they don't match the `*_threshold_dollars` / `*_threshold_time_percent` suffix shape used by `lobbyist_filing_de_minimis_threshold_*` (the second concept in the same framework).

**Proposed renames** (to join `lobbyist_registration_*` and mirror the filing-de-minimis suffix shape):

- `compensation_threshold_for_lobbyist_registration` → `lobbyist_registration_threshold_compensation_dollars`
- `expenditure_threshold_for_lobbyist_registration` → `lobbyist_registration_threshold_expenditure_dollars`
- `time_threshold_for_lobbyist_registration` → `lobbyist_registration_threshold_time_percent`

(Note: `compensation_threshold` is 6-rubric and `expenditure_threshold` + `time_threshold` are 4-rubric — these are high-traffic rows. Coordination cost for rename is non-trivial. But they are *load-bearing* for HG Q2's projection [D22] and the rename improves family coherence at three of the most-read rows in the compendium.)

### Issue 4 — `expenditure_itemization_de_minimis_threshold_dollars` family fit (1 row)

**Row:** `expenditure_itemization_de_minimis_threshold_dollars`
**Issue:** This is D4's third concept (itemization-de-minimis threshold) and it lives as a singleton `expenditure_*` prefix. Could plausibly belong to `lobbyist_filing_*` (sibling to filing-de-minimis pair) or `lobbyist_spending_report_*` (it's about itemization within the report).
**Proposed rename:** `lobbyist_filing_itemization_de_minimis_threshold_dollars` (mirroring `lobbyist_filing_de_minimis_threshold_dollars`).
**Cost:** 1 row; Newmark+Sunlight-introduced.

### Issue 5 — `registration_deadline_days_after_first_lobbying` family fit (1 row)

**Row:** `registration_deadline_days_after_first_lobbying`
**Issue:** Singleton `registration_*` prefix; doesn't join the `lobbyist_registration_*` (3-row) family despite being a registration-administration observable. Two-axis (D11).
**Proposed rename:** `lobbyist_registration_deadline_days_after_first_lobbying`
**Cost:** 1 row; CPI-introduced; 2-rubric.

### Issue 6 — `ministerial_diaries_*` vs `ministerial_diary_*` plural drift (2 rows)

**Rows:**
- `ministerial_diaries_available_online`
- `ministerial_diary_disclosure_cadence`

**Issue:** Plural vs singular within a 2-row family. Defensible (the practical-availability row is about the *collection*; the cadence row is about *per-diary* disclosure), but inconsistent at the prefix level.
**Proposed rename:** standardize on singular `ministerial_diary_*` for both, or leave (low priority).
**Cost:** at most 1 row; FOCAL-introduced.

### Issue 7 — `lobbying_definition_*` and `lobbyist_definition_*` outside the `def_*` family (2 rows)

**Rows:**
- `lobbying_definition_included_activity_types` (FOCAL)
- `lobbyist_definition_included_actor_types` (FOCAL)

**Issue:** These are definitional rows (set-typed enum). Other definitional rows use the `def_*` prefix (`def_target_*`, `def_actor_class_*`). These two don't, because they read most naturally with the keyed scope first. Defensible — but it does fragment the definitional family.
**Proposed rename:** either `def_lobbying_activity_types` / `def_lobbyist_actor_types`, or leave (low priority — readability vs family coherence).
**Cost:** 2 rows; FOCAL-introduced.

### Issue 8 — README filename inconsistency (not a row-ID issue)

`compendium/README.md` §"How Compendium 2.0 was built" lists the projection-mapping doc filenames including `cpi_2015_projection_mapping.md`, but the actual file is `cpi_2015_c11_projection_mapping.md`. Minor doc-drift; flag for the rename-execution branch or fix in passing.

---

## 11. Prefix-choice guidance (for new rows)

When introducing a new row, work through this decision tree:

1. **What kind of observable is it?**
   - Statutory **definition** → `def_*` family. `def_target_*` if it's about who/what gets lobbied; `def_actor_class_*` if it's about which individuals count as actors.
   - Whether a specific institutional actor type must **register as a lobbyist** → `actor_<type>_registration_required` (PRI A1–A11 shape).
   - Content of a **registration form** → `lobbyist_reg_form_includes_*` or `principal_reg_form_includes_*` (or `lobbyist_or_principal_reg_form_*` if the rubric source doesn't specify side).
   - Content / structure / cadence of a **spending report** → `lobbyist_spending_report_*` or `principal_spending_report_*` (or `lobbyist_or_principal_spending_report_*`). **Always use the explicit `_spending_report_*` prefix, not bare `_report_*` (per D3).**
   - **Search-filter capability** on the portal → `lobbying_search_filter_*`.
   - **Contact-log content** → `lobbying_contact_log_*`.
   - **Data-system quality** (downloadable, versioned, open license, identifiers) → `lobbying_data_*`.
   - **Disclosure-document access** (online, free, audited) → `lobbying_disclosure_*`.
   - **Directory of lobbyists** (availability, cadence) → `lobbyist_directory_*`.
   - **Oversight-agency behavior** (publishing aggregates, training) → `oversight_agency_*`.
   - **Threshold** for something:
     - Lobbyist-status threshold (when must one register at all)? → currently the `<measure>_threshold_for_lobbyist_registration` shape, but [Issue 3](#issue-3--registration-threshold-family-lives-outside-the-registration-family-3-rows) flags this as a rename candidate. Use the proposed `lobbyist_registration_threshold_*` shape for new rows.
     - Filing-de-minimis (when must a registered lobbyist file)? → `lobbyist_filing_de_minimis_threshold_*`.
     - Itemization-de-minimis (when must a line item be itemized)? → currently `expenditure_itemization_de_minimis_threshold_*`, but [Issue 4](#issue-4--expenditure_itemization_de_minimis_threshold_dollars-family-fit-1-row) flags as candidate. Use the proposed `lobbyist_filing_itemization_de_minimis_threshold_*` shape for new rows.

2. **Whose observable is it?**
   - Lobbyist's filings / lobbyist as entity → `lobbyist_*`.
   - Principal's filings / principal as entity → `principal_*`.
   - Either side (rubric ambiguous on side) → `lobbyist_or_principal_*` (alphabetical-by-prominence, **not** `principal_or_lobbyist_*`).
   - The lobbying activity or the data system → `lobbying_*`.
   - Government / public entities being lobbied → `govt_*` or `public_*` (existing families; small).

3. **Which axis?**
   - Don't encode axis in the prefix. Set the `axis` column to `legal`, `practical`, or `legal+practical` and let the column carry it.
   - One exception by historical convention: `online_*_filing_available` rows are practical-axis-only by the choice to lead with `online_`.

4. **Suffix shape:** end with a predicate that hints at the cell_type:
   - Binary observables: `_required`, `_includes_*`, `_available_*`, `_filter_by_*`, `_published`, `_disclosed`.
   - Set-typed observables: `_definition_included_*_types`, `_cadence_includes_*` (when atomized as 6-binary), `_uses_itemized_format`.
   - Threshold observables: `_threshold_dollars`, `_threshold_time_percent`, `_threshold_hours`.
   - Date / deadline observables: `_deadline_days_*`, `_days_after_*`.
   - Cadence observables: `_cadence_*`, `_update_cadence`, `_renewal_cadence`.

5. **Verify against the existing 181:** before committing a new row_id, grep `compendium/disclosure_side_compendium_items_v2.tsv` for the 1-token and 2-token prefix to confirm you're joining (not duplicating) a family.

---

## 12. Per-row provenance

The per-row provenance table is machine-generated from the v2 TSV's `first_introduced_by` and `notes` columns plus the D1–D30 freeze decisions, by [`docs/active/compendium-naming-docs/results/20260514_provenance_table.py`](../docs/active/compendium-naming-docs/results/20260514_provenance_table.py). Output: [`docs/active/compendium-naming-docs/results/20260514_provenance_table.md`](../docs/active/compendium-naming-docs/results/20260514_provenance_table.md) — one row per `compendium_row_id` with:

- 2-token prefix family
- `first_introduced_by` projection-mapping doc (column from the TSV)
- D-decision references (if any of D1–D8 / D12 / D16 renamed, merged, or promoted the row)
- 1-line provenance excerpt from the TSV `notes` column

Hand-curating provenance for 181 rows would duplicate what the TSV + freeze log already encode. The generator approach keeps the per-row data live with the TSV — if the v2 TSV is regenerated by `tools/freeze_canonicalize_rows.py`, the provenance table can be regenerated in lock-step.

---

## 13. Maintenance

When `tools/freeze_canonicalize_rows.py` is updated with new canonicalization decisions (D31+), this doc should be updated in lock-step:

1. New rows or renames → §3 family counts may shift; §11 decision tree may need a new branch.
2. New naming conventions → §2 / §3 / §5 / §6 / §7 sections need amendment.
3. Resolved naming issues → strike from §10 and add a back-reference to the rename-execution branch / commit.

Cross-reference: the row-freeze decision log at [`docs/historical/compendium-source-extracts/results/projections/20260513_row_freeze_decisions.md`](../docs/historical/compendium-source-extracts/results/projections/20260513_row_freeze_decisions.md) is the canonical source for *why* each canonicalization was made. This doc is the canonical source for *what* the conventions are and *where to put a new row*.
