# `compendium/` — Row-naming conventions

> **Status:** 2026-05-14. Audit produced on the `compendium-naming-docs` branch (GH issue [#9](https://github.com/danparshall/lobby_analysis/issues/9), merged to main as PR [#10](https://github.com/danparshall/lobby_analysis/pull/10)). The 8 rename candidates surfaced in [§10](#naming-issues--rename-candidates) were ratified across 3 sessions and applied on `compendium-row-id-renames`: 15 row-ID renames + 1 README typo fix. The renames are part of v2's contract (no v2→v3 generation bump — Dan's "retroactively re-finalize v2" framing). The [§10.1 resolver table](#101-resolver-table-for-archive-readers) preserves old→new pairs verbatim for readers of archived material. Sister branches absorb the renames by merging main and running `tools/v2_update_names.py` against their working tree.

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

16 distinct 1-token prefixes. The first six account for 164 of 181 rows.

| Prefix | Count | Role |
|---|---:|---|
| `lobbyist_*` | 75 | Lobbyist-side observables (the natural person or firm registered to lobby): registration forms, spending reports, directory listings, filing requirements |
| `lobbying_*` | 42 | Process / portal observables (the *activity* of lobbying, the *data system* exposing it): search filters, contact logs, data quality, disclosure-documents access |
| `principal_*` | 22 | Principal-side observables (the entity employing or paying the lobbyist): spending reports, listings |
| `actor_*` | 11 | Institutional-actor registration requirements (PRI A1–A11): one row per actor type (`actor_executive_agency_*`, `actor_volunteer_lobbyist_*`, etc.) |
| `def_*` | 10 | Definitional rows (legal definitions): `def_target_*`, `def_actor_class_*`, `def_lobbying_*`, `def_lobbyist_*` |
| `oversight_*` | 4 | Oversight-agency publishing behavior (HG practical-axis: aggregate spending publications, e-file training) |
| `public_*` | 3 | Public-entity definition criteria |
| `exemption_*` | 2 | Exemption-from-disclosure provisions |
| `govt_*` | 2 | Government-agency disclosure-subject status |
| `law_*` | 2 | Statutory-content properties (definitions and materiality tests) |
| `ministerial_*` | 2 | Ministerial-diary practical observables (FOCAL) |
| `online_*` | 2 | Online-filing portal availability (HG practical-axis) |
| `consultant_*` | 1 | Singleton — consultant-lobbyist sub-type income disclosure (FOCAL) |
| `sample_*` | 1 | Singleton — HG: sample filing forms available online |
| `separate_*` | 1 | Singleton — OS-1 path-b unvalidated row |
| `state_*` | 1 | Singleton — HG: state has dedicated lobbying website |

(`compensation_*`, `expenditure_*`, `registration_*`, `time_*` are empty after the §10 renames — their rows joined `lobbyist_registration_*` and `lobbyist_filing_*`. `lobbyist_definition_*` and `lobbying_definition_*` collapsed into `def_*`.)

The keying choice between `lobbyist_*` and `lobbying_*` tracks **whose observable it is**: a `lobbyist_*` row is a property of the lobbyist's filings or the lobbyist as an entity; a `lobbying_*` row is a property of the lobbying activity or the data system that exposes it. This split was not a single explicit decision — it emerged from the nine per-rubric extraction passes — but it holds consistently across the 181 rows.

---

## 3. Strong 3-token families

The empirically tightest families. These are the "real" structural anchors for new rows: if a proposed row fits one of these families, it should use the family prefix.

| Family prefix | Count | Meaning |
|---|---:|---|
| `lobbyist_spending_report_*` | 35 | Content / structure / cadence / scope of the lobbyist-side spending report (PRI E2 + cross-rubric companions). The α form-type split target — see [§5 below](#5-the-α-form-type-split-d3) |
| `principal_spending_report_*` | 22 | Content / structure / cadence of the principal-side spending report (PRI E1 + CPI-distinctive content) |
| `lobbying_search_filter_*` | 15 | Per-criterion search-filter capabilities on the portal (PRI Q7a-o atomized, +1 multicriteria capability) |
| `lobbyist_reg_form_*` | 13 | Content fields on the lobbyist's registration form (HG Q22 + FOCAL `descriptors.*`) |
| `lobbying_contact_log_*` | 9 | Per-field content of the contact log (FOCAL `contact_log` atomized) |
| `lobbying_data_*` | 8 | Data-system / portal-data quality observables (FOCAL openness + PRI Q3/Q11) |
| `lobbyist_registration_*` | 7 | Registration administration + lobbyist-status threshold trio + registration deadline (CPI/HG/PRI; expanded by Issue 3 + Issue 5 renames) |
| `def_target_*` | 6 | Target classes of lobbying (legislative/executive/independent/governor's office/legislative-staff/executive-staff) |
| `lobbying_disclosure_*` | 6 | Disclosure-documents access (online, free, audited, unique-IDs, linked, response-time) |
| `lobbyist_or_principal_*` | 6 | Joint-actor rows: same observable applies to either side (see [§6 below](#6-joint-actor-rows-d7); expanded by Issue 1 + Issue 2 renames) |
| `lobbyist_directory_*` | 5 | Directory of registered lobbyists, availability format + update cadence (HG Q31/Q32) |
| `lobbyist_filing_*` | 4 | Filing-de-minimis thresholds + itemization-de-minimis threshold + LV-1 in-house/contract distinction (D4 — see [§7 below](#7-the-three-threshold-framework-d4); expanded by Issue 2 LV-1 + Issue 4 renames) |
| `lobbyist_itemized_expenditure_*` | 4 | Per-item content of itemized expenditures (HG) |
| `oversight_agency_*` | 4 | Oversight agency publishing + training behavior (HG practical-axis) |
| `public_entity_def_*` | 3 | Criteria the public-entity definition relies on (charter / ownership / revenue structure) |
| `def_actor_class_*` | 2 | Individual-actor classes (elected officials / public employees) |
| `govt_agencies_subject_*` | 2 | Whether government agencies are themselves subject to lobbyist / principal disclosure |
| `online_lobbyist_*` | 2 | Online-filing portal availability (HG practical-axis) |

Two new `def_*` 3-token singletons from Issue 7: `def_lobbying_activity_types`, `def_lobbyist_actor_types`. The `lobbyist_report_*` family is now empty (both leftover D3 rows from Issue 2 moved to `lobbyist_spending_report_*` or `lobbyist_filing_*`).

Plus 34 singleton families (one row each) — see the [prefix survey](../docs/historical/compendium-naming-docs/results/20260514_prefix_survey.md) for the full listing.

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

**LobbyView schema-coverage exception (categorical).** Rows that describe whether a filing has a given column or distinguishes between filing types *at the data-system level* (rather than what content is *in* a single report) belong in `lobbyist_filing_*`, **not** `lobbyist_spending_report_*`. The canonical case is the LV-1 row `lobbyist_filing_distinguishes_in_house_vs_contract_filer` (D12 promotion of a LobbyView schema-coverage column): it captures whether the filing apparatus exposes the in-house-vs-contract distinction at all, not what either category's report contents include. This is a categorical rule, not a per-row judgment call — any future LobbyView-style schema-coverage row goes in `lobbyist_filing_*`. See [Issue 2](#issue-2--d3-rename-gaps-leftover-_report_-rows-that-should-be-_spending_report_-6-rows) for the cluster of D3 rename gaps where this exception lives.

---

## 6. Joint-actor rows (D7)

The `lobbyist_or_principal_*` prefix (5 rows) marks observables that **apply to either side** — the underlying disclosure exists, but the rubrics cited it without specifying actor side. D7 of the row-freeze log made the explicit decision to keep these combined rather than splitting each into lobbyist + principal variants (YAGNI vs granularity-bias: split if a real rubric reads the distinction).

Members:

- `lobbyist_or_principal_reg_form_includes_lobbyist_board_memberships`
- `lobbyist_or_principal_spending_report_includes_lobbyist_count_total_and_FTE`
- `lobbyist_or_principal_spending_report_includes_time_spent_on_lobbying`
- `lobbyist_or_principal_spending_report_includes_trade_association_dues_or_sponsorship`
- `lobbyist_or_principal_spending_report_includes_contributions_received_for_lobbying`

**Ordering convention: `lobbyist_or_principal_*` (alphabetical-by-actor-prominence, not alphabetical-by-string).** All 5 rows now follow this convention — the prior `principal_or_lobbyist_*` outlier was renamed per [Issue 1, DONE 2026-05-14](#issue-1--principal_or_lobbyist_-reversed-ordering-1-row).

**Form-type consistency:** all 5 rows now use either `_reg_form_*` or `_spending_report_*` (none use the legacy ambiguous `_report_*`). D3's original rename rule was scoped to PRI E1/E2; [Issue 2, DONE 2026-05-14](#issue-2--d3-rename-gaps-leftover-_report_-rows-that-should-be-_spending_report_-6-rows) closed the gap for the 5 non-PRI rows that were also spending-report observables (plus 1 row that became `lobbyist_filing_*` — the LV-1 schema-coverage exception, §5).

---

## 7. The three-threshold framework (D4)

Disclosure law uses *three distinct* dollar/time thresholds, and the compendium uses three distinct prefix conventions to keep them apart (per Sunlight 2015 mapping's Decision Rule 6, made canonical at D4 of the row-freeze):

| Threshold concept | Prefix shape | Members |
|---|---|---|
| **Lobbyist-status threshold** — triggers the obligation to register as a lobbyist at all | `lobbyist_registration_threshold_<measure>_<unit>` | `lobbyist_registration_threshold_compensation_dollars`, `lobbyist_registration_threshold_expenditure_dollars`, `lobbyist_registration_threshold_time_percent` |
| **Filing-de-minimis threshold** — once registered, triggers the obligation to file spending reports | `lobbyist_filing_de_minimis_threshold_*` | `lobbyist_filing_de_minimis_threshold_dollars`, `lobbyist_filing_de_minimis_threshold_time_percent` |
| **Itemization-de-minimis threshold** — once filing, triggers per-line itemization within a report | `*_itemization_de_minimis_threshold_*` (singleton) | `lobbyist_filing_itemization_de_minimis_threshold_dollars` |

The three-threshold framework is load-bearing for HG Q2's projection (D22: `min(compensation_threshold, expenditure_threshold)` reads the binding-threshold concept).

The lobbyist-status threshold family now joins the `lobbyist_registration_*` family with consistent `_threshold_<measure>_<unit>` suffix shape, per [Issue 3, DONE 2026-05-14](#issue-3--registration-threshold-family-lives-outside-the-registration-family-3-rows). Prior names were `<measure>_threshold_for_lobbyist_registration` singletons — see §10.1 for the resolver table.

**Threshold-suffix convention** (sub-3 resolution, 2026-05-14). The canonical shape for a threshold row is `_threshold_<unit>` for single-measure threshold families and `_threshold_<measure>_<unit>` for multi-measure families. The unit token (`_dollars` / `_percent` / `_hours`) is repeated in the suffix even though `cell_type` carries it — this is intentional redundancy so readers of the row_id alone know the unit without consulting `cell_type`.

- **Single-measure:** `lobbyist_filing_de_minimis_threshold_dollars` and its sibling `lobbyist_filing_de_minimis_threshold_time_percent` — the filing-de-minimis concept is one threshold cell with two measures (dollar amount, time percent). Each measure is its own row and the row id ends in `_threshold_<unit>`. The measure word is omitted because the threshold concept itself has one name (`de_minimis`).
- **Multi-measure:** the lobbyist-status threshold family has three *distinct measure concepts* (compensation, expenditure, time spent) all triggering the same status threshold, so each row needs an explicit measure word. Issue 3's applied renames `lobbyist_registration_threshold_compensation_dollars` / `_expenditure_dollars` / `_time_percent` follow this shape.

When introducing a new threshold row, decide which case applies: is this a new measure on an existing single-concept threshold (use `_threshold_<unit>` if the family is currently single-measure; rename the existing row to add `<measure>` only if the family is acquiring a second concept), or a new concept-level threshold (use `_threshold_<measure>_<unit>` from the start if you expect multiple measures).

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
| `_threshold_*_dollars` | `typed Optional[Decimal]` | `lobbyist_filing_de_minimis_threshold_dollars`, `lobbyist_registration_threshold_compensation_dollars` |
| `_threshold_time_percent` | `typed Optional[TimeThreshold]` | `lobbyist_filing_de_minimis_threshold_time_percent`, `lobbyist_registration_threshold_time_percent` |
| `_cadence_*` | `binary` (PRI atomized as 6-binary set) or `typed UpdateCadence` (HG) | `lobbyist_spending_report_cadence_includes_quarterly`, `lobbyist_directory_update_cadence` |
| `_def_*` / `_definition_*` | `typed Set[enum]` | `def_lobbying_activity_types`, `def_lobbyist_actor_types` |
| `_filter_by_*` | `binary` | the `lobbying_search_filter_*` family |
| `_required_in_law` / `_available_*` | `binary` | self-explanatory practical-availability rows |

These are conventions, not rules — the `cell_type` column is authoritative. If you're adding a row, write a suffix that hints at the cell_type, but **don't infer cell_type from suffix alone**.

---

## 10. Naming issues / rename candidates

**Status:** All 8 candidates surfaced in this audit were ratified and applied on `compendium-row-id-renames` (PR pending; merged 2026-05-14). The §10.1 resolver table below preserves the 15 row-ID renames + 1 doc-filename typo fix verbatim — readers of archived material (e.g., `docs/historical/compendium-naming-docs/`, `docs/historical/compendium-source-extracts/results/projections/*.md`) can resolve old names to new here.

The renames are part of v2's contract, not a v2→v3 generation bump: `compendium/disclosure_side_compendium_items_v2.tsv` was finalized 2026-05-13 on `compendium-v2-promote` and re-finalized 2026-05-14 with the renamed row IDs on `compendium-row-id-renames`. Sister branches absorb the renames by merging main and running `tools/v2_update_names.py` against their working tree (the script's mapping dict at `src/lobby_analysis/row_id_renamer.py` is the executable form of §10.1 below).

### Issue 1 — `principal_or_lobbyist_*` reversed ordering (1 row) — **DONE 2026-05-14**

**Row:** `principal_or_lobbyist_reg_form_includes_member_or_sponsor_names`
**Issue:** Joint-actor rows use `lobbyist_or_principal_*` ordering (5 of 5 other rows). This one row reverses it. Same convention, opposite alphabetic order.
**Applied rename:** → `lobbyist_or_principal_reg_form_includes_member_or_sponsor_names`
**Cost:** 1 row; FOCAL-introduced; single-rubric.

### Issue 2 — D3 rename gaps: leftover `_report_*` rows that should be `_spending_report_*` (6 rows) — **DONE 2026-05-14**

D3 enacted the α form-type split (`*_report_includes_*` → `*_spending_report_includes_*`) but keyed the rename rule on `_includes_*` and `_cadence_*` patterns inside PRI E1/E2 only. Six non-PRI rows that are spending-report observables (or, in the LV-1 case, a schema-coverage observable on the filing apparatus) retained the legacy ambiguous `_report_*` prefix:

| Old row_id | Source rubric | Applied rename |
|---|---|---|
| `lobbyist_report_distinguishes_in_house_vs_contract_filer` | LV-1 (LobbyView, D12 promotion) | `lobbyist_filing_distinguishes_in_house_vs_contract_filer` |
| `lobbyist_report_includes_campaign_contributions` | Newmark 2017 | `lobbyist_spending_report_includes_campaign_contributions` |
| `lobbyist_or_principal_report_includes_lobbyist_count_total_and_FTE` | FOCAL | `lobbyist_or_principal_spending_report_includes_lobbyist_count_total_and_FTE` |
| `lobbyist_or_principal_report_includes_time_spent_on_lobbying` | FOCAL | `lobbyist_or_principal_spending_report_includes_time_spent_on_lobbying` |
| `lobbyist_or_principal_report_includes_trade_association_dues_or_sponsorship` | FOCAL | `lobbyist_or_principal_spending_report_includes_trade_association_dues_or_sponsorship` |
| `principal_report_lists_lobbyists_employed` | FOCAL | `principal_spending_report_lists_lobbyists_employed` |

**LV-1 is the categorical exception.** It goes to `lobbyist_filing_*` (schema-coverage observable, joining `lobbyist_filing_de_minimis_threshold_*`), not `_spending_report_*`. See §5 and §11 for the decision-tree branch that captures this categorical rule (the other 5 are report-content observables; LV-1 is a schema-coverage meta-observable about the filing apparatus).

### Issue 3 — Registration-threshold family lives outside the registration family (3 rows) — **DONE 2026-05-14**

Three rows capture the **lobbyist-status threshold** (D4's first concept in the three-threshold framework). They previously used a `<measure>_threshold_for_lobbyist_registration` shape that joined no family. Applied renames join `lobbyist_registration_*` with the `_threshold_<measure>_<unit>` shape (§7):

- `compensation_threshold_for_lobbyist_registration` → `lobbyist_registration_threshold_compensation_dollars`
- `expenditure_threshold_for_lobbyist_registration` → `lobbyist_registration_threshold_expenditure_dollars`
- `time_threshold_for_lobbyist_registration` → `lobbyist_registration_threshold_time_percent`

(`compensation_threshold` is 6-rubric and `expenditure_threshold` + `time_threshold` are 4-rubric — these are high-traffic rows. The rename improves family coherence at three of the most-read rows in the compendium and is load-bearing for HG Q2's projection [D22].)

### Issue 4 — `expenditure_itemization_de_minimis_threshold_dollars` family fit (1 row) — **DONE 2026-05-14**

**Old row_id:** `expenditure_itemization_de_minimis_threshold_dollars`
**Issue:** D4's third concept (itemization-de-minimis threshold) lived as a singleton `expenditure_*` prefix.
**Applied rename:** → `lobbyist_filing_itemization_de_minimis_threshold_dollars` (mirroring `lobbyist_filing_de_minimis_threshold_dollars`).
**Cost:** 1 row; Newmark+Sunlight-introduced.

### Issue 5 — `registration_deadline_days_after_first_lobbying` family fit (1 row) — **DONE 2026-05-14**

**Old row_id:** `registration_deadline_days_after_first_lobbying`
**Issue:** Singleton `registration_*` prefix; didn't join the `lobbyist_registration_*` family despite being a registration-administration observable.
**Applied rename:** → `lobbyist_registration_deadline_days_after_first_lobbying`
**Cost:** 1 row; CPI-introduced; 2-rubric. (The old name is a substring of the new — word-boundary regex in the renamer prevents the double-rename trap on idempotent re-runs.)

### Issue 6 — `ministerial_diaries_*` vs `ministerial_diary_*` plural drift (1 row renamed) — **DONE 2026-05-14**

**Old row_id:** `ministerial_diaries_available_online`
**Issue:** Plural vs singular within a 2-row family (`ministerial_diary_disclosure_cadence` already singular).
**Applied rename:** → `ministerial_diary_available_online`. Family now consistently singular.
**Cost:** 1 row; FOCAL-introduced.

### Issue 7 — `lobbying_definition_*` and `lobbyist_definition_*` outside the `def_*` family (2 rows) — **DONE 2026-05-14**

**Applied renames:**
- `lobbying_definition_included_activity_types` → `def_lobbying_activity_types`
- `lobbyist_definition_included_actor_types` → `def_lobbyist_actor_types`

These join the `def_*` family with `def_target_*`, `def_actor_class_*`, etc.

### Issue 8 — README filename inconsistency (not a row-ID issue) — **DONE 2026-05-14**

`compendium/README.md` referenced `cpi_2015_projection_mapping.md` (the actual file is `cpi_2015_c11_projection_mapping.md`). Applied rename: `cpi_2015_projection_mapping` → `cpi_2015_c11_projection_mapping` (string-level, not a row rename).

---

## 10.1. Resolver table for archive readers

Verbatim old → new mapping for the 15 row-ID renames + 1 documentation-filename typo fix landed 2026-05-14. Anyone reading archived material that references an old row ID can resolve it here.

The executable form of this table is the `RENAMES` dict at the top of `src/lobby_analysis/row_id_renamer.py`; the find-and-replace tool that applies it is `tools/v2_update_names.py`. Sister branches absorb the rename by merging main and running the tool on their own tree.

| Old name | New name | Candidate |
|---|---|---|
| `principal_or_lobbyist_reg_form_includes_member_or_sponsor_names` | `lobbyist_or_principal_reg_form_includes_member_or_sponsor_names` | 1 |
| `lobbyist_report_distinguishes_in_house_vs_contract_filer` | `lobbyist_filing_distinguishes_in_house_vs_contract_filer` | 2 (LV-1 exception) |
| `lobbyist_report_includes_campaign_contributions` | `lobbyist_spending_report_includes_campaign_contributions` | 2 |
| `lobbyist_or_principal_report_includes_lobbyist_count_total_and_FTE` | `lobbyist_or_principal_spending_report_includes_lobbyist_count_total_and_FTE` | 2 |
| `lobbyist_or_principal_report_includes_time_spent_on_lobbying` | `lobbyist_or_principal_spending_report_includes_time_spent_on_lobbying` | 2 |
| `lobbyist_or_principal_report_includes_trade_association_dues_or_sponsorship` | `lobbyist_or_principal_spending_report_includes_trade_association_dues_or_sponsorship` | 2 |
| `principal_report_lists_lobbyists_employed` | `principal_spending_report_lists_lobbyists_employed` | 2 |
| `compensation_threshold_for_lobbyist_registration` | `lobbyist_registration_threshold_compensation_dollars` | 3 |
| `expenditure_threshold_for_lobbyist_registration` | `lobbyist_registration_threshold_expenditure_dollars` | 3 |
| `time_threshold_for_lobbyist_registration` | `lobbyist_registration_threshold_time_percent` | 3 |
| `expenditure_itemization_de_minimis_threshold_dollars` | `lobbyist_filing_itemization_de_minimis_threshold_dollars` | 4 |
| `registration_deadline_days_after_first_lobbying` | `lobbyist_registration_deadline_days_after_first_lobbying` | 5 |
| `ministerial_diaries_available_online` | `ministerial_diary_available_online` | 6 |
| `lobbying_definition_included_activity_types` | `def_lobbying_activity_types` | 7 |
| `lobbyist_definition_included_actor_types` | `def_lobbyist_actor_types` | 7 |
| `cpi_2015_projection_mapping` (doc filename ref) | `cpi_2015_c11_projection_mapping` | 8 |

## 11. Prefix-choice guidance (for new rows)

When introducing a new row, work through this decision tree:

1. **What kind of observable is it?**
   - Statutory **definition** → `def_*` family. `def_target_*` if it's about who/what gets lobbied; `def_actor_class_*` if it's about which individuals count as actors.
   - Whether a specific institutional actor type must **register as a lobbyist** → `actor_<type>_registration_required` (PRI A1–A11 shape).
   - Content of a **registration form** → `lobbyist_reg_form_includes_*` or `principal_reg_form_includes_*` (or `lobbyist_or_principal_reg_form_*` if the rubric source doesn't specify side).
   - Content / structure / cadence of a **spending report** → `lobbyist_spending_report_*` or `principal_spending_report_*` (or `lobbyist_or_principal_spending_report_*`). **Always use the explicit `_spending_report_*` prefix, not bare `_report_*` (per D3).**
   - **Schema-coverage observable about the filing apparatus** (e.g., "does the system distinguish between two filing types," "is there a column for X at all") → `lobbyist_filing_*`, **NOT** `lobbyist_spending_report_*`. Distinction: report-content rows describe what's *in* a single filing; schema-coverage rows describe what *kinds* of filings exist or what fields the system tracks at all. Canonical case: the LV-1 row in [Issue 2](#issue-2--d3-rename-gaps-leftover-_report_-rows-that-should-be-_spending_report_-6-rows) and the §5 categorical-exception note.
   - **Search-filter capability** on the portal → `lobbying_search_filter_*`.
   - **Contact-log content** → `lobbying_contact_log_*`.
   - **Data-system quality** (downloadable, versioned, open license, identifiers) → `lobbying_data_*`.
   - **Disclosure-document access** (online, free, audited) → `lobbying_disclosure_*`.
   - **Directory of lobbyists** (availability, cadence) → `lobbyist_directory_*`.
   - **Oversight-agency behavior** (publishing aggregates, training) → `oversight_agency_*`.
   - **Threshold** for something:
     - Lobbyist-status threshold (when must one register at all)? → `lobbyist_registration_threshold_<measure>_<unit>` (per [Issue 3, DONE 2026-05-14](#issue-3--registration-threshold-family-lives-outside-the-registration-family-3-rows)).
     - Filing-de-minimis (when must a registered lobbyist file)? → `lobbyist_filing_de_minimis_threshold_*`.
     - Itemization-de-minimis (when must a line item be itemized)? → `lobbyist_filing_itemization_de_minimis_threshold_*` (per [Issue 4, DONE 2026-05-14](#issue-4--lobbyist_filing_itemization_de_minimis_threshold_dollars-family-fit-1-row)).

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

The per-row provenance table is machine-generated from the v2 TSV's `first_introduced_by` and `notes` columns plus the D1–D30 freeze decisions, by [`docs/historical/compendium-naming-docs/results/20260514_provenance_table.py`](../docs/historical/compendium-naming-docs/results/20260514_provenance_table.py). Output: [`docs/historical/compendium-naming-docs/results/20260514_provenance_table.md`](../docs/historical/compendium-naming-docs/results/20260514_provenance_table.md) — one row per `compendium_row_id` with:

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
