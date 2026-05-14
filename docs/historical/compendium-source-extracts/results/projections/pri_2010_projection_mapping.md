# PRI 2010 (Disclosure Law + Accessibility) — projection mapping

**Plan:** [`../../plans/20260507_atomic_items_and_projections.md`](../../plans/20260507_atomic_items_and_projections.md) Phase B.
**Handoff:** [`../../plans/_handoffs/20260507_phase_b_handoff.md`](../../plans/_handoffs/20260507_phase_b_handoff.md).
**Atomic items source:** [`../items_PRI_2010.tsv`](../items_PRI_2010.tsv) (83 items: 22 accessibility + 61 disclosure-law).
**Predecessor mapping:** [`cpi_2015_c11_projection_mapping.md`](cpi_2015_c11_projection_mapping.md). The Doc Conventions block below is the same set of rules locked in the CPI mapping; restated here for self-containment, not re-derived.
**Per-item per-state ground truth:**
- Accessibility: [`docs/historical/pri-2026-rescore/results/pri_2010_accessibility_scores.csv`](../../../../historical/pri-2026-rescore/results/pri_2010_accessibility_scores.csv) (50 states × 8 sub-component cells; Q7 is `Q7_raw 0-15`, Q8 is `Q8_normalized 0-1`; per-Q7-sub-criterion scores not published) and [`pri_2010_accessibility_rubric.csv`](../../../../historical/pri-2026-rescore/results/pri_2010_accessibility_rubric.csv) (rubric text).
- Disclosure law: [`pri_2010_disclosure_law_scores.csv`](../../../../historical/pri-2026-rescore/results/pri_2010_disclosure_law_scores.csv) (50 states × 5 sub-aggregate cells: `A_registration / B_gov_exemptions / C_public_entity_def / D_materiality / E_info_disclosed`; per-atomic-item scores not in this file but the rubric CSV holds the per-item structure).

---

## Doc conventions

These are identical to the CPI mapping's locked Doc Conventions block (granularity-bias, typed cells on `MatrixCell.value`, strict-c_NNN / loose-c_NNN notation, clusters as provenance-hints-not-row-identities). Restated here in compressed form:

- **Compendium row IDs** are projection-meaningful working names. Cluster references (`cf. strict-c_NNN` / `cf. loose-c_NNN`) are provenance hints, not authoritative identifiers. Strict ≥8/9 method-runs, loose ≥6/9; the two files use independent cluster numbering.
- **Cell type** is the type the compendium cell carries. Projection logic maps cell value → rubric score.
- **Axis:** `legal_availability` for de jure items (statutory provisions); `practical_availability` for de facto items (observed portal/regime behavior). PRI 2010 has both axes (disclosure-law is mostly legal; accessibility is mostly practical).
- **Granularity bias: split on every distinguishing case.** Multi-binary cells per case; projections combine via Boolean expressions. PRI 2010 already atomizes most concepts at fine granularity (the explicit reason this rubric was extracted into 83 items rather than ~30) — the convention's job here is mostly to *preserve* PRI's atomization in the compendium row set, not to expand it further.
- **Typed cells live on `MatrixCell.value`.** v2.0 schema bump assumed (still pending; tracked separately). Until v2.0 lands, this projection mapping assumes the typed-cell pattern is available.

## Aggregation rule (Phase C empirical, structure documented)

PRI 2010 publishes **two separate per-state scores** (each on a 0-100% scale):

1. **Accessibility** — published in `pri_2010_accessibility_scores.csv`. Max raw = 22 (six sub-components: Q1+Q2 each 1pt, Q3 1pt, Q4+Q5 each 1pt, Q6 1pt, Q7 0-15 raw, Q8 0-1 normalized — paper-derived breakdown gives max around 22 if you sum the per-sub-component maxima the way the published data shows). Empirically: `total_2010 = Q1+Q2+Q3+Q4+Q5+Q6+Q7_raw+Q8_normalized`, with `percent_2010 = total_2010 / 22 * 100`. Spot-check Alabama: 1+1+1+1+0+0+3+0.1 = 7.1, ×100/22 ≈ 32.3 vs published 32.4 ✓; Alaska: 1+1+1+1+1+0+7+0.1 = 12.1, ×100/22 ≈ 55.0 vs published 55.2 ✓. Aggregation rule for accessibility is therefore: simple sum of 6 sub-component scores, divided by 22. Within sub-component, the per-atomic-item rollup matters most for Q7 (Q7_raw = sum of Q7a-Q7o binary truths, max 15) and Q8 (the 0-15 ordinal normalized to 0-1; partition unknown — see Open Issue 1).

2. **Disclosure law** — published in `pri_2010_disclosure_law_scores.csv`. Max raw appears to be 37 (Alabama 19/0.514 ≈ 37; Alaska 26/0.703 ≈ 37). Sub-aggregates: A_registration (max ≈ 11), B_gov_exemptions (max ≈ 4), C_public_entity_def (max 1, gate-only — see C0), D_materiality (max 1, gate-only — see D0), E_info_disclosed (max ≈ 20). Spot-check Alabama: 7+3+0+1+8=19 ✓; Alaska: 5+2+0+1+18=26 ✓. The within-E1/E2 atomic-item-to-sub-aggregate rule is **not specified at atomic granularity** in the paper — paper §III.E describes "components" at the E1f / E1g / E1h / E1i level (one point per component if statute requires it) without specifying the sub-component handling for E1f_i-iv (4 binaries → 1 point or 4 points?), E1g_i-ii (2 binaries → 1 or 2 points?), E1h_i-vi (6 cadence options → counts how?), and similarly for E2. PRI's published per-state data is at the sub-aggregate level only, not per-atomic-item. **Phase C will need to fit the within-E1/E2 rollup empirically** against the per-state E_info_disclosed values, with the historical methodology doc at [`docs/historical/pri-calibration/`](../../../../historical/pri-calibration/) flagging "9 methodology differences" — at least some of which involve E-series rollup choices. Phase B doesn't need to resolve this.

The 9 methodology-difference flags from the historical pri-calibration work are **inputs** to Phase C, not Phase B's responsibility. Phase B's job: write down what each atomic item asks of the compendium cells. Phase C's job: figure out how the atomic-item scores combine to produce the published sub-aggregates.

## Per-state ground truth data

Available granularity:
- **Accessibility:** per-Q1..Q6 binary + Q7_raw (0-15) + Q8_normalized (0-1) per state — 8 cells × 50 states = 400 ground-truth values. Per-Q7-sub-criterion data NOT published; only the Q7_raw aggregate is available, so projection validation for Q7a-Q7o has to use the aggregate (sum check) rather than per-atomic-item.
- **Disclosure law:** per-sub-aggregate (A/B/C/D/E_info_disclosed) per state — 5 cells × 50 states = 250 ground-truth values. Per-atomic-item data NOT published in this file. The atomic-item structure exists in the rubric CSV; per-state per-item answers are NOT available from PRI 2010 publication.

This is **less granular** than CPI 2015's 700-cell per-state per-indicator ground truth. PRI compensates with item count (83 vs CPI's 14) and a longer trail of subsequent academic use. For the purposes of Phase C validation, PRI provides sub-aggregate-level fitting only; per-atomic-item validation is impossible against PRI's published data.

## Validation jurisdictions

50 US states × 2010 vintage × 8 accessibility sub-components + 5 disclosure-law sub-aggregates = **650 ground-truth values**. Federal LDA out of scope (PRI 2010 is state-only).

---

## Per-item mappings

### Accessibility section (22 items)

PRI 2010 §IV. All accessibility items measure **practical availability** of the state's lobbying-data web presence. The de-jure pair (e.g., is there a *statutory mandate* for the state to publish lobbying data online?) generally does not exist in US state law and is rarely populated; practical availability is the only meaningful axis for most accessibility items.

#### Q1: At least some lobbying data available (in any format) either by request (email, telephone, fax, etc.) or anonymously (web-based)

- **Compendium rows:** `lobbying_data_minimally_available` (NEW; not in consensus output as a strict or loose cluster — PRI Q1 is a low-bar gate that no other rubric replicates at this granularity).
- **Cell type:** binary.
- **Axis:** `practical_availability`.
- **Scoring rule:** `cell_value → 1 if True else 0`.
- **Source quote:** "At least some lobbying data available (in any format) either by request (email, telephone, fax, etc.) or anonymously (web-based)." (PRI 2010 §IV Q1.)

#### Q2: The state has a dedicated website for lobbying information

- **Compendium rows:** `state_has_dedicated_lobbying_website` (cf. loose-c_009: PRI Q2 + FOCAL openness.1 "Lobbyist register is online" + HiredGuns Q31 "Location/format of registrations or active lobbyist directory" — 3-rubric cluster on "lobbying data lives at a known web location").
- **Cell type:** binary.
- **Axis:** `practical_availability`.
- **Scoring rule:** `cell_value → 1 if True else 0`.
- **Source quote:** "The state has a dedicated website for lobbying information." (PRI 2010 §IV Q2.)
- **Note:** PRI source TSV flags "likely obsolete for 2026" — by 2026 nearly all states have at least *some* online presence for lobbying data, so the row's discriminative power is greater in 2010 than in modern vintages. Compendium row remains valid; the rubric's *binary threshold* is what's becoming obsolete, not the underlying observable.

#### Q3: How easily a state's lobbying website can be found

- **Compendium rows:** `lobbying_website_easily_findable` (NEW; no consensus cluster).
- **Cell type:** binary (with the caveat that PRI does not define "easily" — see Open Issue 2).
- **Axis:** `practical_availability`.
- **Scoring rule:** `cell_value → 1 if True else 0`.
- **Source quote:** "How easily a state's lobbying website can be found." (PRI 2010 §IV Q3, footnote 92 in source.)
- **Note:** PRI source TSV flags "PRI does not define 'easily' — flag for Phase 3." Phase C will need a deterministic operationalization (Google-rank-of-lobbying-data-on-search-for-"<state> lobbying disclosure"? site-prominence-on-state-government-homepage?) since the rubric leaves it open.

#### Q4: At least some current lobbying data/information available on the website for the most recent year

- **Compendium rows:** `lobbying_data_current_year_present_on_website` (NEW; no consensus cluster).
- **Cell type:** binary.
- **Axis:** `practical_availability`.
- **Scoring rule:** `cell_value → 1 if True else 0`.
- **Source quote:** "At least some current lobbying data/information available on the website for the most recent year." (PRI 2010 §IV Q4.)
- **Note:** Closely related to FOCAL `timeliness.1` (frequency of website updates) but reads a coarser binary; FOCAL's projection will read a richer typed cell on the same row family.

#### Q5: Historical lobbying information is available, downloadable, or at least viewable on the state's website

- **Compendium rows:** `lobbying_data_historical_archive_present` (cf. strict-c_015 / loose-c_019: PRI Q5 + FOCAL openness.8 "Historical data in lobbyist register is archived and published; downloadable" — 2-rubric strict cluster).
- **Cell type:** binary.
- **Axis:** `practical_availability`.
- **Scoring rule:** `cell_value → 1 if True else 0`.
- **Source quote:** "Historical lobbying information is available, downloadable, or at least viewable on the state's website." (PRI 2010 §IV Q5.)
- **Note:** PRI source TSV flags "Historical horizon not specified — flag for Phase 3." FOCAL openness.8 implies a cleaner "archived and published" reading. The compendium cell can carry the binary; Phase C decides where the threshold sits (one year of history? five? all-vintages?).

#### Q6: How easily users can download lobbying data and information and analyze it, and specifically, whether users are able to download information in an electronic format that is immediately useable for analysis, such as Excel or SPSS

- **Compendium rows:** `lobbying_data_downloadable_in_analytical_format` (cf. loose-c_002: PRI Q6 + FOCAL openness.3 "Available without registration, free to access, open license, non-proprietary format, machine readable" + FOCAL openness.4 "Downloadable" + OpenSecrets `public_avail_downloads` — 4-rubric loose cluster). This row is the same one CPI #206 reads (`lobbying_data_open_data_quality`, 5-tier practical) but PRI reads a coarser binary.
- **Cell type:** binary, derivable from the richer 4-feature cell already proposed by CPI #206 (`(online: bool, easy_access: bool, bulk_download: bool, machine_readable: bool)`). PRI Q6 binary projection: `online AND easy_access AND machine_readable`.
- **Axis:** `practical_availability`.
- **Scoring rule:** `cell_value → 1 if True else 0`. Composition over the 4-feature cell from CPI #206: `1 if (online AND easy_access AND machine_readable) else 0`.
- **Source quote:** "How easily users can download lobbying data and information and analyze it, and specifically, whether users are able to download information in an electronic format that is immediately useable for analysis, such as Excel or SPSS." (PRI 2010 §IV Q6.)
- **Note:** PRI source TSV flags "2010 treated CSV/Excel as gold standard; 2026 should reward bulk download / API access — flag for Phase 3." Compendium 2.0 row already accommodates this — the underlying cell is multi-feature; rubric vintages choose their own binary threshold over those features.

#### Q7a: Can users specify data searches on the website by Principal (city; authority hiring; employer; corporation; etc.)

- **Compendium rows:** `lobbying_search_filter_by_principal` (NEW; no consensus cluster — PRI's Q7 atomization is finer than any other rubric).
- **Cell type:** binary.
- **Axis:** `practical_availability`.
- **Scoring rule:** `cell_value → 1 if True else 0`.
- **Source quote:** "Can users specify data searches on the website by Principal (city; authority hiring; employer; corporation; etc.)." (PRI 2010 §IV Q7.)

#### Q7b: Can users specify data searches on the website by Principal's location (specific address; city)

- **Compendium rows:** `lobbying_search_filter_by_principal_location` (NEW).
- **Cell type:** binary.
- **Axis:** `practical_availability`.
- **Scoring rule:** `cell_value → 1 if True else 0`.
- **Source quote:** "Can users specify data searches on the website by Principal's location (specific address; city)." (PRI 2010 §IV Q7.)

#### Q7c: Can users specify data searches on the website by Lobbyist name

- **Compendium rows:** `lobbying_search_filter_by_lobbyist_name` (NEW).
- **Cell type:** binary.
- **Axis:** `practical_availability`.
- **Scoring rule:** `cell_value → 1 if True else 0`.
- **Source quote:** "Can users specify data searches on the website by Lobbyist name." (PRI 2010 §IV Q7.)

#### Q7d: Can users specify data searches on the website by Lobbyist location (specific address; city)

- **Compendium rows:** `lobbying_search_filter_by_lobbyist_location` (NEW).
- **Cell type:** binary.
- **Axis:** `practical_availability`.
- **Scoring rule:** `cell_value → 1 if True else 0`.
- **Source quote:** "Can users specify data searches on the website by Lobbyist location (specific address; city)." (PRI 2010 §IV Q7.)

#### Q7e: Can users specify data searches on the website by Specific date

- **Compendium rows:** `lobbying_search_filter_by_specific_date` (NEW).
- **Cell type:** binary.
- **Axis:** `practical_availability`.
- **Scoring rule:** `cell_value → 1 if True else 0`.
- **Source quote:** "Can users specify data searches on the website by Specific date." (PRI 2010 §IV Q7.)

#### Q7f: Can users specify data searches on the website by Specific time period (normally quarter but it depends on how often the law requires data to be disclosed)

- **Compendium rows:** `lobbying_search_filter_by_time_period` (NEW).
- **Cell type:** binary.
- **Axis:** `practical_availability`.
- **Scoring rule:** `cell_value → 1 if True else 0`.
- **Source quote:** "Can users specify data searches on the website by Specific time period (normally quarter but it depends on how often the law requires data to be disclosed)." (PRI 2010 §IV Q7.)

#### Q7g: Can users specify data searches on the website by Total expenditures

- **Compendium rows:** `lobbying_search_filter_by_total_expenditures` (NEW).
- **Cell type:** binary.
- **Axis:** `practical_availability`.
- **Scoring rule:** `cell_value → 1 if True else 0`.
- **Source quote:** "Can users specify data searches on the website by Total expenditures." (PRI 2010 §IV Q7.)

#### Q7h: Can users specify data searches on the website by Compensation spending (portion of total expenditures for which the lobbyist is paid back)

- **Compendium rows:** `lobbying_search_filter_by_compensation` (NEW).
- **Cell type:** binary.
- **Axis:** `practical_availability`.
- **Scoring rule:** `cell_value → 1 if True else 0`.
- **Source quote:** "Can users specify data searches on the website by Compensation spending (portion of total expenditures for which the lobbyist is paid back)." (PRI 2010 §IV Q7.)

#### Q7i: Can users specify data searches on the website by Miscellaneous expenses (non-compensation)

- **Compendium rows:** `lobbying_search_filter_by_misc_expenses` (NEW).
- **Cell type:** binary.
- **Axis:** `practical_availability`.
- **Scoring rule:** `cell_value → 1 if True else 0`.
- **Source quote:** "Can users specify data searches on the website by Miscellaneous expenses (non-compensation)." (PRI 2010 §IV Q7.)

#### Q7j: Can users specify data searches on the website by Sources of funding (emphasis on public/taxpayer-funded)

- **Compendium rows:** `lobbying_search_filter_by_funding_source` (NEW).
- **Cell type:** binary.
- **Axis:** `practical_availability`.
- **Scoring rule:** `cell_value → 1 if True else 0`.
- **Source quote:** "Can users specify data searches on the website by Sources of funding (emphasis on public/taxpayer-funded)." (PRI 2010 §IV Q7.)

#### Q7k: Can users specify data searches on the website by Subject of lobbying (or item of legislation)

- **Compendium rows:** `lobbying_search_filter_by_subject` (NEW). Probable intersection with FOCAL `contact_log.11` (bill numbers / legislation) at the cell-content level — the search-filter row reads "is filtering by subject possible," and the underlying data being filterable depends on whether the subject is captured per-filing (FOCAL `contact_log.11`).
- **Cell type:** binary.
- **Axis:** `practical_availability`.
- **Scoring rule:** `cell_value → 1 if True else 0`.
- **Source quote:** "Can users specify data searches on the website by Subject of lobbying (or item of legislation)." (PRI 2010 §IV Q7.)

#### Q7l: Can users specify data searches on the website by Designated entities assigned to lobbyist (group/congressman the lobbyist is working for)

- **Compendium rows:** `lobbying_search_filter_by_assigned_entity` (NEW). Likely reads cell content captured per-filing (which official/group is the lobbyist contacting, akin to FOCAL `contact_log` family).
- **Cell type:** binary.
- **Axis:** `practical_availability`.
- **Scoring rule:** `cell_value → 1 if True else 0`.
- **Source quote:** "Can users specify data searches on the website by Designated entities assigned to lobbyist (group/congressman the lobbyist is working for)." (PRI 2010 §IV Q7.)

#### Q7m: Can users specify data searches on the website by Legal status of the principal (government; non-profit; for-profit; etc.)

- **Compendium rows:** `lobbying_search_filter_by_principal_legal_status` (NEW).
- **Cell type:** binary.
- **Axis:** `practical_availability`.
- **Scoring rule:** `cell_value → 1 if True else 0`.
- **Source quote:** "Can users specify data searches on the website by Legal status of the principal (government; non-profit; for-profit; etc.)." (PRI 2010 §IV Q7.)

#### Q7n: Can users specify data searches on the website by Sector (transport; energy; banking; education; social services; etc.)

- **Compendium rows:** `lobbying_search_filter_by_sector` (NEW).
- **Cell type:** binary.
- **Axis:** `practical_availability`.
- **Scoring rule:** `cell_value → 1 if True else 0`.
- **Source quote:** "Can users specify data searches on the website by Sector (transport; energy; banking; education; social services; etc.)." (PRI 2010 §IV Q7.)

#### Q7o: Can users specify data searches on the website by Sub-sector (K–12; secondary; vocational; etc.)

- **Compendium rows:** `lobbying_search_filter_by_subsector` (NEW).
- **Cell type:** binary.
- **Axis:** `practical_availability`.
- **Scoring rule:** `cell_value → 1 if True else 0`.
- **Source quote:** "Can users specify data searches on the website by Sub-sector (K–12; secondary; vocational; etc.)." (PRI 2010 §IV Q7.)

#### Q8: Users can simultaneously sort lobbying data by multiple criteria

- **Compendium rows:** `lobbying_search_simultaneous_multicriteria_capability` (cf. strict-c_003 + loose-c_010: PRI Q8 + FOCAL openness.5 "Searchable, simultaneous sorting with multiple criteria" + OpenSecrets `public_avail_search` "User-friendly search feature on state lobbying disclosure website" — 3-rubric strict cluster, exact concept overlap).
- **Cell type:** typed `int` ∈ {0, 1, …, 15} (PRI's published 0-15 ordinal). Underlying observable: count of distinct criteria the search UI permits to be combined simultaneously, OR a quality-tier judgment on a 0-15 scale. **Scoring partition is undocumented in the paper** — see Open Issue 1.
- **Axis:** `practical_availability`.
- **Scoring rule:** Cell-value passthrough divided by 15 to yield Q8_normalized (0-1 scale per the published data column). Phase C decides whether the cell carries the raw ordinal directly (passthrough) or is computed from underlying observables via a deterministic mapping (analogous to the CPI 25/75 boundary-semantics decision per Open Issue 2 in the CPI mapping).
- **Source quote:** "Users can simultaneously sort lobbying data by multiple criteria." (PRI 2010 §IV Q8; published as `Q8_normalized` in scores file with values like 0.1.)
- **Note:** Direct analogue to CPI's 5-tier 25/75 partial-credit issue. PRI's published per-state values cluster heavily at 0.1 (and a few states higher), suggesting the scorer awarded mostly low partial-credit values — fitting any partition function from underlying observables to the 0-15 range will require the per-state observed values as ground truth. Treated here as an Open Issue for Phase C, in line with user direction (a2, 2026-05-07).

---

### Disclosure law section (61 items)

PRI 2010 §III. All disclosure-law items measure **legal availability** (statutory provisions); none read practical_availability.

#### A. Who is required to register (11 items)

PRI atomizes "registrant taxonomy" into 11 binary items asking: for each potential lobbying-actor class (paid lobbyists, volunteers, principals, firms, government bodies of various flavors, public entities), is that class statutorily required to register?

**Conceptual note: actor-side, not target-side.** PRI A is the *who-must-register* axis (an entity's statutory obligation as a registering actor). This is structurally distinct from CPI #196's *def_target_** rows, which are the *who-counts-as-being-lobbied* axis (a state body whose contact triggers lobbying status for the actor). For example: "Does state law require Governor's Office staff to register *as a lobbyist* when they advocate to the Legislature on behalf of the executive branch?" (PRI A5) is a different question from "Does state law include communications *to* the Governor in the definition of lobbying?" (CPI #196 component). Both are real, distinct, separately observable. The compendium splits accordingly.

##### A1: Lobbyists

- **Compendium rows:** `actor_paid_lobbyist_registration_required` (NEW; no consensus cluster — most rubrics treat this as the gate question implicitly without atomizing it). Distinct from CPI #198's `lobbyist_registration_required` (which is the *de facto* "do they actually register" axis); A1 is the *de jure* mandate.
- **Cell type:** binary.
- **Axis:** `legal_availability`.
- **Scoring rule:** `cell_value → 1 if True else 0`.
- **Source quote:** "Lobbyists." (PRI 2010 §III.A.)
- **Note:** Per paper: all 50 states require lobbyists to register, so this cell is True for all 50 states in 2010 vintage. Limited discriminative power but kept in compendium as the fundamental gate.

##### A2: Volunteer lobbyists

- **Compendium rows:** `actor_volunteer_lobbyist_registration_required` (NEW).
- **Cell type:** binary.
- **Axis:** `legal_availability`.
- **Scoring rule:** `cell_value → 1 if True else 0`.
- **Source quote:** "Volunteer lobbyists." (PRI 2010 §III.A.)
- **Note:** Per paper: 17 states required as of 2010.

##### A3: Principals who employ a lobbyist

- **Compendium rows:** `actor_principal_registration_required` (NEW; closely related but DIFFERENT from `principal_spending_report_required` from CPI #203 — registration is a one-time/renewal act of identification; spending reports are periodic disclosures).
- **Cell type:** binary.
- **Axis:** `legal_availability`.
- **Scoring rule:** `cell_value → 1 if True else 0`.
- **Source quote:** "Principals who employ a lobbyist." (PRI 2010 §III.A.)
- **Note:** Per paper: 24 states required as of 2010.

##### A4: Lobbying firms

- **Compendium rows:** `actor_lobbying_firm_registration_required` (NEW).
- **Cell type:** binary.
- **Axis:** `legal_availability`.
- **Scoring rule:** `cell_value → 1 if True else 0`.
- **Source quote:** "Lobbying firms." (PRI 2010 §III.A.)
- **Note:** Per paper: 17 states required as of 2010.

##### A5: Governor's office

- **Compendium rows:** `actor_governors_office_registration_required` (NEW; actor-side analogue of the target-side `def_target_governors_office` from CPI #196).
- **Cell type:** binary.
- **Axis:** `legal_availability`.
- **Scoring rule:** `cell_value → 1 if True else 0`.
- **Source quote:** "Governor's office." (PRI 2010 §III.A.)

##### A6: Executive branch agencies

- **Compendium rows:** `actor_executive_agency_registration_required` (NEW; actor-side analogue of `def_target_executive_agency` from CPI #196). Likely overlaps content-wise with Newmark `def_administrative_agency_lobbying` (cf. loose-c_006) but on the actor axis rather than target axis.
- **Cell type:** binary.
- **Axis:** `legal_availability`.
- **Scoring rule:** `cell_value → 1 if True else 0`.
- **Source quote:** "Executive branch agencies." (PRI 2010 §III.A.)

##### A7: Legislative branch

- **Compendium rows:** `actor_legislative_branch_registration_required` (NEW; actor-side analogue of `def_target_legislative_branch`).
- **Cell type:** binary.
- **Axis:** `legal_availability`.
- **Scoring rule:** `cell_value → 1 if True else 0`.
- **Source quote:** "Legislative branch." (PRI 2010 §III.A.)

##### A8: Independent agencies

- **Compendium rows:** `actor_independent_agency_registration_required` (NEW; actor-side analogue of `def_target_independent_agency`).
- **Cell type:** binary.
- **Axis:** `legal_availability`.
- **Scoring rule:** `cell_value → 1 if True else 0`.
- **Source quote:** "Independent agencies." (PRI 2010 §III.A.)

##### A9: Local governments

- **Compendium rows:** `actor_local_government_registration_required` (NEW). v1.1 schema's `RegistrationRequirement.role` Literal already enumerates `local_government` as a role; this row reads the actor-side mandate on the same role taxonomy.
- **Cell type:** binary.
- **Axis:** `legal_availability`.
- **Scoring rule:** `cell_value → 1 if True else 0`.
- **Source quote:** "Local governments." (PRI 2010 §III.A.)

##### A10: Government agencies who lobby other agencies

- **Compendium rows:** `actor_intergov_agency_lobbying_registration_required` (NEW). Distinct from A6/A7/A8 in that A10 specifies the *intergovernmental* lobbying activity (agency lobbying agency) rather than agency-as-actor in general. Often regulated separately from private-sector lobbying.
- **Cell type:** binary.
- **Axis:** `legal_availability`.
- **Scoring rule:** `cell_value → 1 if True else 0`.
- **Source quote:** "Government agencies who lobby other agencies." (PRI 2010 §III.A.)

##### A11: Public entities, other than government agencies

- **Compendium rows:** `actor_public_entity_other_registration_required` (NEW). Reads in conjunction with the C-series public-entity-definition rows (which determine the cell value for "what counts as a public entity").
- **Cell type:** binary.
- **Axis:** `legal_availability`.
- **Scoring rule:** `cell_value → 1 if True else 0`.
- **Source quote:** "Public entities, other than government agencies." (PRI 2010 §III.A.)

#### B. Government exemptions (4 items)

PRI atomizes whether/how state law exempts government bodies from the disclosure regime that applies to private lobbyists. Source TSV note flags an unresolved scoring direction (Open Issue 3): "exemption exists" structurally reduces transparency, but PRI's published score may treat it as +1 for legal completeness rather than -1 for transparency loss.

##### B1: Is there an exemption for government agencies and/or public officials acting within their official capacity?

- **Compendium rows:** `exemption_for_govt_official_capacity_exists` (NEW).
- **Cell type:** binary.
- **Axis:** `legal_availability`.
- **Scoring rule:** `cell_value → 1 if True else 0`. Direction note: PRI may reverse-score this; Phase C empirical fit against per-state B_gov_exemptions sub-aggregate will reveal direction. See Open Issue 3.
- **Source quote:** "Is there an exemption for government agencies and/or public officials acting within their official capacity?" (PRI 2010 §III.B, footnote 85.)

##### B2: Are government agencies relieved and/or exempted (partially) from the regulations imposed on non-government organizations and individuals?

- **Compendium rows:** `exemption_partial_for_govt_agencies` (NEW).
- **Cell type:** binary.
- **Axis:** `legal_availability`.
- **Scoring rule:** `cell_value → 1 if True else 0`. Same direction-uncertainty caveat as B1.
- **Source quote:** "Are government agencies relieved and/or exempted (partially) from the regulations imposed on non-government organizations and individuals?" (PRI 2010 §III.B, footnote 86.)

##### B3: Are government agencies subject to the same disclosure requirements as lobbyists?

- **Compendium rows:** `govt_agencies_subject_to_lobbyist_disclosure_requirements` (NEW; conceptually inverse of B1 and partial inverse of B2).
- **Cell type:** binary.
- **Axis:** `legal_availability`.
- **Scoring rule:** `cell_value → 1 if True else 0`.
- **Source quote:** "Are government agencies subject to the same disclosure requirements as lobbyists?" (PRI 2010 §III.B.)
- **Note:** PRI scores B as 4 atomic items but they're not independent — B1=True usually implies B3=False. Compendium 2.0 keeps them as separate rows because edge cases (partial exemptions, asymmetric treatment) violate strict implication, and the granularity-bias convention prefers explicit storage over derivation.

##### B4: Are government agencies subject to the same disclosure requirements as principals?

- **Compendium rows:** `govt_agencies_subject_to_principal_disclosure_requirements` (NEW).
- **Cell type:** binary.
- **Axis:** `legal_availability`.
- **Scoring rule:** `cell_value → 1 if True else 0`.
- **Source quote:** "Are government agencies subject to the same disclosure requirements as principals?" (PRI 2010 §III.B.)

#### C. Definition of public entity (4 items)

PRI atomizes whether/how state law defines "public entity." Per source TSV: "Table 5 reports C as 0/1 only, suggesting the published score reflected only this question [C0]. Sub-criteria C1-C3 below are described in the paper but their scoring contribution is not specified — flag for Phase 3."

This means C0 is the published-score gate, and C1-C3 are atomically extracted but **not read by the PRI projection**. They remain in compendium 2.0 because they are real distinguishing cases (different states define "public entity" using different criteria, which downstream extraction needs to capture); the PRI projection just doesn't read them. Other rubrics (potentially) might.

##### C0: Does the law include a definition of "public entity"?

- **Compendium rows:** `law_defines_public_entity` (NEW).
- **Cell type:** binary.
- **Axis:** `legal_availability`.
- **Scoring rule:** `cell_value → 1 if True else 0`. PRI's published C sub-aggregate reads only this gate.
- **Source quote:** "Does the law include a definition of 'public entity'?" (PRI 2010 §III.C.)

##### C1: Definition relies on Ownership

- **Compendium rows:** `public_entity_def_relies_on_ownership` (NEW; sub-criterion of C0, only meaningful if C0=True).
- **Cell type:** binary.
- **Axis:** `legal_availability`.
- **Scoring rule:** Not read by PRI 2010 projection (paper does not specify a scoring contribution for C1-C3). Compendium row exists for cross-rubric availability.
- **Source quote:** "Definition relies on Ownership." (PRI 2010 §III.C, sub-criterion of C0.)

##### C2: Definition relies on Structure or composition of revenue

- **Compendium rows:** `public_entity_def_relies_on_revenue_structure` (NEW; sub-criterion of C0, only meaningful if C0=True).
- **Cell type:** binary.
- **Axis:** `legal_availability`.
- **Scoring rule:** Not read by PRI 2010 projection.
- **Source quote:** "Definition relies on Structure or composition of revenue." (PRI 2010 §III.C, sub-criterion of C0.)

##### C3: Definition relies on Public charter or special government protection

- **Compendium rows:** `public_entity_def_relies_on_charter` (NEW; sub-criterion of C0, only meaningful if C0=True).
- **Cell type:** binary.
- **Axis:** `legal_availability`.
- **Scoring rule:** Not read by PRI 2010 projection.
- **Source quote:** "Definition relies on Public charter or special government protection." (PRI 2010 §III.C, sub-criterion of C0.)

#### D. Materiality test (5 items)

PRI atomizes the materiality-test concept (statutory thresholds below which lobbying activity is exempt from disclosure). Two sub-types: financial threshold (D1) and time threshold (D2). Each is structured as `_present` (binary) + `_value` (typed). Per source TSV: "Table 5 reports D as 0/1 only" (gate D0). The `_present` and `_value` items are atomically extracted but not separately scored in PRI's published per-state aggregate.

**Single-row typed-cell pattern preferred (consistent with CPI #197):** D1_present + D1_value can be encoded as ONE compendium row carrying a typed `Optional[Decimal]` cell, where `cell IS NULL` means "no financial threshold defined" and any non-null value means "threshold exists with that dollar value." D1_present is then derived as `cell IS NOT NULL`. Same pattern for D2 with `Optional[float]`. The PRI projection reads `value IS NOT NULL` for the present-flag; CPI #197 reads the threshold value directly.

##### D0: Does the law include a materiality test (ability to exempt) for coverage in disclosure regulations?

- **Compendium rows:** `law_includes_materiality_test` (NEW; gate question, distinct from D1/D2 because PRI's published C/D sub-aggregates score gate-only).
- **Cell type:** binary. **Derivation note:** D0 = `(D1 IS NOT NULL) OR (D2 IS NOT NULL)` — i.e., "law includes a materiality test" if either threshold is defined. This makes D0 a derived Boolean over the two underlying typed cells. Compendium 2.0 may store D0 as a separate cell (explicit) or derive it (implicit); flagged as a v2.0 schema question.
- **Axis:** `legal_availability`.
- **Scoring rule:** `cell_value → 1 if True else 0`. PRI's published D sub-aggregate reads only this gate.
- **Source quote:** "Does the law include a materiality test (ability to exempt) for coverage in disclosure regulations?" (PRI 2010 §III.D.)

##### D1_present: Financial threshold exists: if expenses are less than some dollar threshold the entity is exempted from filing disclosure

- **Compendium rows:** `materiality_threshold_financial_value` — typed `Optional[Decimal]` (USD). The `_present` reading is `cell IS NOT NULL`. This is the same row that CPI's `compensation_threshold_for_lobbyist_registration` family covers conceptually — but with one important distinction: CPI #197's threshold is on *compensation paid to* the lobbyist (registration trigger); D1's threshold is on *expenses* by the entity (disclosure-filing exemption). These are different statutory thresholds in the same family but logically distinct cells. Compendium row name reflects D1's specific scope.
- **Cell type:** binary projection over a typed `Optional[Decimal]` underlying cell — projection reads `cell IS NOT NULL`.
- **Axis:** `legal_availability`.
- **Scoring rule:** `cell IS NOT NULL → 1 else 0`.
- **Source quote:** "Financial threshold exists: if expenses are less than some dollar threshold the entity is exempted from filing disclosure." (PRI 2010 §III.D, sub-criterion of D0.)

##### D1_value: Dollar threshold value (USD) for financial-threshold exemption

- **Compendium rows:** `materiality_threshold_financial_value` (same row as D1_present — D1_present and D1_value are two PRI atomic items reading the same compendium cell at different granularities).
- **Cell type:** typed `Optional[Decimal]` (USD).
- **Axis:** `legal_availability`.
- **Scoring rule:** Not read by PRI 2010 published projection (paper scores D as 0/1 gate only). Cell value is captured for cross-rubric availability and Phase C empirical fitting.
- **Source quote:** "Dollar threshold value (USD) for financial-threshold exemption." (PRI 2010 §III.D — capture raw value; null if no threshold.)
- **Note:** Canonical example of the typed-cell pattern: ONE compendium cell, TWO PRI atomic items reading it at different granularities. CPI #197 reads similar threshold-cells directly for its 100/50/0 mapping; PRI 2010 reads only the presence flag. This is exactly the typed-cell-on-MatrixCell.value design from the CPI Doc Conventions.

##### D2_present: Time threshold exists: if amount of time devoted to lobbying is less than a threshold percentage of an individual's compensated time the individual or entity is exempted from filing disclosure

- **Compendium rows:** `materiality_threshold_time_percent` — typed `Optional[float]` (percentage). Same row as D2_value.
- **Cell type:** binary projection over a typed `Optional[float]` underlying cell — projection reads `cell IS NOT NULL`.
- **Axis:** `legal_availability`.
- **Scoring rule:** `cell IS NOT NULL → 1 else 0`.
- **Source quote:** "Time threshold exists: if amount of time devoted to lobbying is less than a threshold percentage of an individual's compensated time the individual or entity is exempted from filing disclosure." (PRI 2010 §III.D, sub-criterion of D0.)

##### D2_value: Percentage threshold value for time-threshold exemption

- **Compendium rows:** `materiality_threshold_time_percent` (same row as D2_present).
- **Cell type:** typed `Optional[float]` (percentage).
- **Axis:** `legal_availability`.
- **Scoring rule:** Not read by PRI 2010 published projection.
- **Source quote:** "Percentage threshold value for time-threshold exemption." (PRI 2010 §III.D — capture raw value; null if no threshold.)
- **Note:** OH 2025's §101.70(F) materiality test ("primary purpose" qualitative) is the kind of regime that doesn't fit a numeric threshold and may need a separate `materiality_threshold_qualitative_present` companion row. Flagged for awareness; not added in this round.

#### E1. Principal Reports (19 items)

PRI atomizes principal-side disclosure-report content. E1a is the gate; E1b-e cover identifiers; E1f_i-iv cover financial content; E1g_i-ii cover issue scope; E1h_i-vi cover reporting cadence options; E1i covers contacts; E1j is a stand-alone "major financial contributors" item.

**Conceptual note on parallelism with E2.** PRI's E1 (principals) and E2 (lobbyists) are deliberately parallel — many atomic items have the same indicator text (just with "principal" / "lobbyist" swapped). The consensus method captured this parallelism as paired loose clusters (loose-c_028 for E1f_i + E2f_i, etc.). Per granularity-bias, compendium 2.0 keeps these as **separate rows** (`principal_*` and `lobbyist_*`) because some states regulate principal-side and lobbyist-side disclosures asymmetrically (e.g., requiring lobbyist compensation disclosure but not principal compensation disclosure, or vice versa). The two parallel row-families ARE the right shape.

##### E1a: Are principals required to disclose?

- **Compendium rows:** `principal_spending_report_required` (cf. CPI #203's `principal_spending_report_required` — same row).
- **Cell type:** binary.
- **Axis:** `legal_availability`.
- **Scoring rule:** `cell_value → 1 if True else 0`. Gate for the rest of E1.
- **Source quote:** "Are principals required to disclose?" (PRI 2010 §III.E1.)

##### E1b: Are principals required to disclose their address and phone number?

- **Compendium rows:** `principal_report_includes_principal_contact_info` (NEW; no consensus cluster).
- **Cell type:** binary.
- **Axis:** `legal_availability`.
- **Scoring rule:** `cell_value → 1 if True else 0`.
- **Source quote:** "Are principals required to disclose their address and phone number?" (PRI 2010 §III.E1.)

##### E1c: Are principals required to disclose the names of all the lobbyists representing them?

- **Compendium rows:** `principal_report_includes_lobbyist_names` (NEW). Inverse-direction analogue of E2c (lobbyist-side discloses principal names).
- **Cell type:** binary.
- **Axis:** `legal_availability`.
- **Scoring rule:** `cell_value → 1 if True else 0`.
- **Source quote:** "Are principals required to disclose the names of all the lobbyists representing them?" (PRI 2010 §III.E1.)

##### E1d: Are principals required to disclose the address and phone number of contracted lobbyists?

- **Compendium rows:** `principal_report_includes_lobbyist_contact_info` (NEW).
- **Cell type:** binary.
- **Axis:** `legal_availability`.
- **Scoring rule:** `cell_value → 1 if True else 0`.
- **Source quote:** "Are principals required to disclose the address and phone number of contracted lobbyists?" (PRI 2010 §III.E1.)

##### E1e: Are principals required to disclose the nature of the business (public or private)?

- **Compendium rows:** `principal_report_includes_business_nature` (NEW).
- **Cell type:** binary.
- **Axis:** `legal_availability`.
- **Scoring rule:** `cell_value → 1 if True else 0`.
- **Source quote:** "Are principals required to disclose the nature of the business (public or private)?" (PRI 2010 §III.E1.)

##### E1f_i: Required component of disclosure report: Direct lobbying costs (compensation)

- **Compendium rows:** `principal_report_includes_direct_compensation` (cf. loose-c_028: PRI E1f_i + E2f_i — 2-rubric loose cluster, both PRI internal).
- **Cell type:** binary.
- **Axis:** `legal_availability`.
- **Scoring rule:** `cell_value → 1 if True else 0`.
- **Source quote:** "Required component of disclosure report: Direct lobbying costs (compensation)." (PRI 2010 §III.E1.f.)
- **Note:** Conceptually the principal-side companion of CPI #201's `lobbyist_spending_report_includes_compensation`. CPI #203 reads this row's principal-side equivalent at compound granularity (`principal_spending_report_includes_compensation_paid_to_lobbyists`). The atomic-item granularity here is compensation-component-of-report-content, finer than CPI's compound read.

##### E1f_ii: Required component of disclosure report: Indirect lobbying costs (non-compensation)

- **Compendium rows:** `principal_report_includes_indirect_costs` (cf. loose-c_029: PRI E1f_ii + E2f_ii).
- **Cell type:** binary.
- **Axis:** `legal_availability`.
- **Scoring rule:** `cell_value → 1 if True else 0`.
- **Source quote:** "Required component of disclosure report: Indirect lobbying costs (non-compensation)." (PRI 2010 §III.E1.f.)

##### E1f_iii: Required component of disclosure report: Other costs such as gifts, entertainment, transportation, and lodging

- **Compendium rows:** `principal_report_includes_gifts_entertainment_transport_lodging` (cf. loose-c_030: PRI E1f_iii + E2f_iii). Likely also overlaps Newmark/FOCAL "expenditures benefitting officials" content (cf. strict-c_001 family); but PRI's atomization is at "report-component" granularity, not "what-the-expenditure-is" granularity. Same conceptual cell; different axes-of-atomization.
- **Cell type:** binary.
- **Axis:** `legal_availability`.
- **Scoring rule:** `cell_value → 1 if True else 0`.
- **Source quote:** "Required component of disclosure report: Other costs such as gifts, entertainment, transportation, and lodging." (PRI 2010 §III.E1.f.)

##### E1f_iv: Is the information disclosed in an itemized format (as opposed to an aggregated or lump-sum amount)?

- **Compendium rows:** `principal_report_uses_itemized_format` (cf. loose-c_031: PRI E1f_iv + E2f_iv). Closely related to CPI #201's `lobbyist_spending_report_includes_itemized_expenses` (which is the lobbyist-side analogue per CPI's compound-read structure).
- **Cell type:** binary.
- **Axis:** `legal_availability`.
- **Scoring rule:** `cell_value → 1 if True else 0`.
- **Source quote:** "Is the information disclosed in an itemized format (as opposed to an aggregated or lump-sum amount)?" (PRI 2010 §III.E1.f.)

##### E1g_i: Are principals required to disclose information on the issue lobbied by the general issues lobbied?

- **Compendium rows:** `principal_report_includes_general_issues` (cf. loose-c_032: PRI E1g_i + E2g_i).
- **Cell type:** binary.
- **Axis:** `legal_availability`.
- **Scoring rule:** `cell_value → 1 if True else 0`.
- **Source quote:** "Are principals required to disclose information on the issue lobbied by the general issues lobbied?" (PRI 2010 §III.E1.g.)

##### E1g_ii: Are principals required to disclose information on the issue lobbied by the specific bill number or legislation ID?

- **Compendium rows:** `principal_report_includes_specific_bill_number` (cf. loose-c_012: PRI E1g_ii + E2g_ii + FOCAL `contact_log.11` "Targeted areas of public policy or legislation, including a list of official legislative references/bill numbers/measures etc" — 3-rubric loose cluster).
- **Cell type:** binary.
- **Axis:** `legal_availability`.
- **Scoring rule:** `cell_value → 1 if True else 0`.
- **Source quote:** "Are principals required to disclose information on the issue lobbied by the specific bill number or legislation ID?" (PRI 2010 §III.E1.g.)

##### E1h_i: Reporting frequency option: Monthly

- **Compendium rows:** `principal_report_cadence_includes_monthly` (cf. loose-c_033: PRI E1h_i + E2h_i — both PRI internal). Per PRI's own atomization: 6 binary rows for E1h_i-vi each asking "is X an allowed reporting frequency option?"
- **Cell type:** binary.
- **Axis:** `legal_availability`.
- **Scoring rule:** `cell_value → 1 if True else 0`.
- **Source quote:** "Reporting frequency option: Monthly." (PRI 2010 §III.E1.h.)
- **Note:** Tension with CPI #202's `lobbyist_spending_report_filing_cadence` enum representation — see Open Issue 4. PRI's atomization permits multiple cadences-allowed-simultaneously regimes, which the enum-cell representation handles via a Set type, but PRI's binary atomization is more direct. Adopting PRI's 6-binary representation as the canonical compendium rows; CPI's enum read becomes a derived projection from the 6 binaries.

##### E1h_ii: Reporting frequency option: Quarterly

- **Compendium rows:** `principal_report_cadence_includes_quarterly` (cf. loose-c_034).
- **Cell type:** binary.
- **Axis:** `legal_availability`.
- **Scoring rule:** `cell_value → 1 if True else 0`.
- **Source quote:** "Reporting frequency option: Quarterly." (PRI 2010 §III.E1.h.)

##### E1h_iii: Reporting frequency option: Tri-annually (linked with legislative calendar)

- **Compendium rows:** `principal_report_cadence_includes_triannual` (cf. loose-c_035).
- **Cell type:** binary.
- **Axis:** `legal_availability`.
- **Scoring rule:** `cell_value → 1 if True else 0`.
- **Source quote:** "Reporting frequency option: Tri-annually (linked with legislative calendar)." (PRI 2010 §III.E1.h.)

##### E1h_iv: Reporting frequency option: Semi-annually

- **Compendium rows:** `principal_report_cadence_includes_semiannual` (cf. loose-c_036).
- **Cell type:** binary.
- **Axis:** `legal_availability`.
- **Scoring rule:** `cell_value → 1 if True else 0`.
- **Source quote:** "Reporting frequency option: Semi-annually." (PRI 2010 §III.E1.h.)

##### E1h_v: Reporting frequency option: Annually

- **Compendium rows:** `principal_report_cadence_includes_annual` (cf. loose-c_037).
- **Cell type:** binary.
- **Axis:** `legal_availability`.
- **Scoring rule:** `cell_value → 1 if True else 0`.
- **Source quote:** "Reporting frequency option: Annually." (PRI 2010 §III.E1.h.)

##### E1h_vi: Reporting frequency option: Other (free-text)

- **Compendium rows:** `principal_report_cadence_includes_other` + `principal_report_cadence_other_specification` (free-text companion cell carrying the "other" specification). 2-row pair: a binary indicator + a free-text spec.
- **Cell type:** binary (on the indicator row) + free-text (on the specification row).
- **Axis:** `legal_availability` for both.
- **Scoring rule:** `indicator_cell → 1 if True else 0`; specification cell not scored, captured for downstream consumers.
- **Source quote:** "Reporting frequency option: Other (free-text)." (PRI 2010 §III.E1.h.)

##### E1i: Are principals required to disclose contacts?

- **Compendium rows:** `principal_report_includes_contacts_made` (cf. loose-c_039: PRI E1i + E2i — 2-rubric loose cluster, PRI internal). Captures contact-log content specifically — "did principal X make contact with official Y on date Z?" — distinct from financial reporting.
- **Cell type:** binary.
- **Axis:** `legal_availability`.
- **Scoring rule:** `cell_value → 1 if True else 0`.
- **Source quote:** "Are principals required to disclose contacts?" (PRI 2010 §III.E1.i, footnote 90.)
- **Note:** "Contacts" here aligns with FOCAL's `contact_log.*` indicator family (contact_log.1 through .11). FOCAL's projection mapping will read the same row at finer granularity (each contact-log field as a separate cell). The PRI-coarser binary reads "any contacts disclosure exists at all."

##### E1j: Are principals required to disclose major financial contributors?

- **Compendium rows:** `principal_report_includes_major_financial_contributors` (NEW; no consensus cluster). Per paper §III.E intro: "scored independently of the rest of E (this is 'question J' referenced in the text)" — meaning E1j contributes to a separate sub-aggregate slot, not the E_info_disclosed bucket.
- **Cell type:** binary.
- **Axis:** `legal_availability`.
- **Scoring rule:** `cell_value → 1 if True else 0`. Aggregation note: PRI scores this independently of E1a-i (paper §III.E intro). Phase C aggregation must respect the carve-out.
- **Source quote:** "Are principals required to disclose major financial contributors?" (PRI 2010 §III.E1.j.)
- **Note:** Where E1j folds into the published E_info_disclosed sub-aggregate vs a separate slot is a Phase C question — see Open Issue 5.

#### E2. Lobbyist Disclosure (18 items)

PRI atomizes lobbyist-side disclosure-report content. Structurally parallel to E1 (principal-side) but with a few differences: E2 has no equivalent of E1j (major financial contributors); E2c reads the lobbyist→principals link (which pairs with FOCAL relationships.1). Where an E2 item is the structural mirror of an E1 item, the per-item analysis below references the E1 entry and only flags differences.

##### E2a: Are lobbyists required to disclose?

- **Compendium rows:** `lobbyist_spending_report_required` (cf. CPI #201's `lobbyist_spending_report_required` — same row).
- **Cell type:** binary.
- **Axis:** `legal_availability`.
- **Scoring rule:** `cell_value → 1 if True else 0`. Gate for the rest of E2.
- **Source quote:** "Are lobbyists required to disclose?" (PRI 2010 §III.E2.)

##### E2b: Are lobbyists required to disclose their address and phone number?

- **Compendium rows:** `lobbyist_report_includes_lobbyist_contact_info` (NEW; structural mirror of E1b but lobbyist-side).
- **Cell type:** binary.
- **Axis:** `legal_availability`.
- **Scoring rule:** `cell_value → 1 if True else 0`.
- **Source quote:** "Are lobbyists required to disclose their address and phone number?" (PRI 2010 §III.E2.)

##### E2c: Are lobbyists required to disclose the names of all the principals represented?

- **Compendium rows:** `lobbyist_report_includes_principal_names` (cf. strict-c_016 + loose-c_020: PRI E2c + FOCAL `relationships.1` "Client list (for all consultant lobbyists and firms)" — 2-rubric strict cluster). High-confidence canonical row.
- **Cell type:** binary.
- **Axis:** `legal_availability`.
- **Scoring rule:** `cell_value → 1 if True else 0`.
- **Source quote:** "Are lobbyists required to disclose the names of all the principals represented?" (PRI 2010 §III.E2.)

##### E2d: Are lobbyists required to disclose the address and phone number of the principals represented?

- **Compendium rows:** `lobbyist_report_includes_principal_contact_info` (NEW; structural mirror of E1d but lobbyist-side).
- **Cell type:** binary.
- **Axis:** `legal_availability`.
- **Scoring rule:** `cell_value → 1 if True else 0`.
- **Source quote:** "Are lobbyists required to disclose the address and phone number of the principals represented?" (PRI 2010 §III.E2.)

##### E2e: Are lobbyists required to disclose the nature of the principal's business (public or private)?

- **Compendium rows:** `lobbyist_report_includes_principal_business_nature` (NEW; structural mirror of E1e but lobbyist-side).
- **Cell type:** binary.
- **Axis:** `legal_availability`.
- **Scoring rule:** `cell_value → 1 if True else 0`.
- **Source quote:** "Are lobbyists required to disclose the nature of the principal's business (public or private)?" (PRI 2010 §III.E2.)

##### E2f_i: Required component of disclosure report: Direct lobbying costs (compensation)

- **Compendium rows:** `lobbyist_report_includes_direct_compensation` (cf. loose-c_028: PRI E1f_i + E2f_i, plus likely overlap with strict-c_018: HG Q13 + Sunlight `lobbyist_compensation` — see CPI #201's reading of the same concept). This row is one of the most-cross-rubric-read in compendium 2.0.
- **Cell type:** binary.
- **Axis:** `legal_availability`.
- **Scoring rule:** `cell_value → 1 if True else 0`.
- **Source quote:** "Required component of disclosure report: Direct lobbying costs (compensation)." (PRI 2010 §III.E2.f.)

##### E2f_ii: Required component of disclosure report: Indirect lobbying costs (non-compensation)

- **Compendium rows:** `lobbyist_report_includes_indirect_costs` (cf. loose-c_029).
- **Cell type:** binary.
- **Axis:** `legal_availability`.
- **Scoring rule:** `cell_value → 1 if True else 0`.
- **Source quote:** "Required component of disclosure report: Indirect lobbying costs (non-compensation)." (PRI 2010 §III.E2.f.)

##### E2f_iii: Required component of disclosure report: Other costs such as gifts, entertainment, transportation, and lodging

- **Compendium rows:** `lobbyist_report_includes_gifts_entertainment_transport_lodging` (cf. loose-c_030).
- **Cell type:** binary.
- **Axis:** `legal_availability`.
- **Scoring rule:** `cell_value → 1 if True else 0`.
- **Source quote:** "Required component of disclosure report: Other costs such as gifts, entertainment, transportation, and lodging." (PRI 2010 §III.E2.f.)

##### E2f_iv: Is the information disclosed in an itemized format (as opposed to an aggregated or lump-sum amount)?

- **Compendium rows:** `lobbyist_report_uses_itemized_format` (cf. loose-c_031). Same row as CPI #201's `lobbyist_spending_report_includes_itemized_expenses` — confirmed cross-rubric overlap.
- **Cell type:** binary.
- **Axis:** `legal_availability`.
- **Scoring rule:** `cell_value → 1 if True else 0`.
- **Source quote:** "Is the information disclosed in an itemized format (as opposed to an aggregated or lump-sum amount)?" (PRI 2010 §III.E2.f.)

##### E2g_i: Are lobbyists required to disclose information on the issue lobbied by the general issues lobbied?

- **Compendium rows:** `lobbyist_report_includes_general_issues` (cf. loose-c_032).
- **Cell type:** binary.
- **Axis:** `legal_availability`.
- **Scoring rule:** `cell_value → 1 if True else 0`.
- **Source quote:** "Are lobbyists required to disclose information on the issue lobbied by the general issues lobbied?" (PRI 2010 §III.E2.g.)

##### E2g_ii: Are lobbyists required to disclose information on the issue lobbied by the specific bill number or legislation ID?

- **Compendium rows:** `lobbyist_report_includes_specific_bill_number` (cf. loose-c_012: PRI E1g_ii + E2g_ii + FOCAL `contact_log.11`).
- **Cell type:** binary.
- **Axis:** `legal_availability`.
- **Scoring rule:** `cell_value → 1 if True else 0`.
- **Source quote:** "Are lobbyists required to disclose information on the issue lobbied by the specific bill number or legislation ID?" (PRI 2010 §III.E2.g.)

##### E2h_i: Reporting frequency option: Monthly

- **Compendium rows:** `lobbyist_report_cadence_includes_monthly` (cf. loose-c_033).
- **Cell type:** binary.
- **Axis:** `legal_availability`.
- **Scoring rule:** `cell_value → 1 if True else 0`.
- **Source quote:** "Reporting frequency option: Monthly." (PRI 2010 §III.E2.h.)
- **Note:** Same enum-vs-binary tension as E1h family — see Open Issue 4. CPI #202's enum row `lobbyist_spending_report_filing_cadence` becomes a derived projection from these 6 binaries.

##### E2h_ii: Reporting frequency option: Quarterly

- **Compendium rows:** `lobbyist_report_cadence_includes_quarterly` (cf. loose-c_034).
- **Cell type:** binary.
- **Axis:** `legal_availability`.
- **Scoring rule:** `cell_value → 1 if True else 0`.
- **Source quote:** "Reporting frequency option: Quarterly." (PRI 2010 §III.E2.h.)

##### E2h_iii: Reporting frequency option: Tri-annually (linked with legislative calendar)

- **Compendium rows:** `lobbyist_report_cadence_includes_triannual` (cf. loose-c_035).
- **Cell type:** binary.
- **Axis:** `legal_availability`.
- **Scoring rule:** `cell_value → 1 if True else 0`.
- **Source quote:** "Reporting frequency option: Tri-annually (linked with legislative calendar)." (PRI 2010 §III.E2.h.)

##### E2h_iv: Reporting frequency option: Semi-annually

- **Compendium rows:** `lobbyist_report_cadence_includes_semiannual` (cf. loose-c_036).
- **Cell type:** binary.
- **Axis:** `legal_availability`.
- **Scoring rule:** `cell_value → 1 if True else 0`.
- **Source quote:** "Reporting frequency option: Semi-annually." (PRI 2010 §III.E2.h.)

##### E2h_v: Reporting frequency option: Annually

- **Compendium rows:** `lobbyist_report_cadence_includes_annual` (cf. loose-c_037).
- **Cell type:** binary.
- **Axis:** `legal_availability`.
- **Scoring rule:** `cell_value → 1 if True else 0`.
- **Source quote:** "Reporting frequency option: Annually." (PRI 2010 §III.E2.h.)

##### E2h_vi: Reporting frequency option: Other (free-text)

- **Compendium rows:** `lobbyist_report_cadence_includes_other` + `lobbyist_report_cadence_other_specification` (2-row pair: binary indicator + free-text spec, mirroring E1h_vi).
- **Cell type:** binary (indicator) + free-text (specification).
- **Axis:** `legal_availability`.
- **Scoring rule:** `indicator_cell → 1 if True else 0`; specification cell not scored.
- **Source quote:** "Reporting frequency option: Other (free-text)." (PRI 2010 §III.E2.h.)

##### E2i: Are lobbyists required to disclose contacts?

- **Compendium rows:** `lobbyist_report_includes_contacts_made` (cf. loose-c_039). Same FOCAL `contact_log.*` overlap as E1i.
- **Cell type:** binary.
- **Axis:** `legal_availability`.
- **Scoring rule:** `cell_value → 1 if True else 0`.
- **Source quote:** "Are lobbyists required to disclose contacts?" (PRI 2010 §III.E2.i, footnote 91.)

---

## Summary of compendium rows touched

For convenience; the union of these rows across all rubric mappings (CPI 2015 + this one + the remaining 8) becomes `disclosure_side_compendium_items_v1.tsv` after Phase B completes.

### Accessibility-side rows (22 PRI items → 22 distinct rows, all on practical_availability)

| Row id (working name) | Cell type | PRI items reading | Provenance hint | Other rubrics likely to read |
|---|---|---|---|---|
| `lobbying_data_minimally_available` | binary | Q1 | NEW | (PRI-only at this granularity) |
| `state_has_dedicated_lobbying_website` | binary | Q2 | loose-c_009 | FOCAL openness.1, HG Q31 |
| `lobbying_website_easily_findable` | binary | Q3 | NEW | (PRI-only) |
| `lobbying_data_current_year_present_on_website` | binary | Q4 | NEW | FOCAL timeliness.1 (richer cell) |
| `lobbying_data_historical_archive_present` | binary | Q5 | strict-c_015, loose-c_019 | FOCAL openness.8 |
| `lobbying_data_downloadable_in_analytical_format` | binary derived from CPI #206's 4-feature cell | Q6 | loose-c_002 | FOCAL openness.3, openness.4, OpenSecrets `public_avail_downloads`, CPI #206 |
| `lobbying_search_filter_by_principal` | binary | Q7a | NEW | (PRI-only at this granularity; may overlap FOCAL relationships) |
| `lobbying_search_filter_by_principal_location` | binary | Q7b | NEW | (PRI-only) |
| `lobbying_search_filter_by_lobbyist_name` | binary | Q7c | NEW | (PRI-only) |
| `lobbying_search_filter_by_lobbyist_location` | binary | Q7d | NEW | (PRI-only) |
| `lobbying_search_filter_by_specific_date` | binary | Q7e | NEW | (PRI-only) |
| `lobbying_search_filter_by_time_period` | binary | Q7f | NEW | (PRI-only) |
| `lobbying_search_filter_by_total_expenditures` | binary | Q7g | NEW | (PRI-only) |
| `lobbying_search_filter_by_compensation` | binary | Q7h | NEW | (PRI-only) |
| `lobbying_search_filter_by_misc_expenses` | binary | Q7i | NEW | (PRI-only) |
| `lobbying_search_filter_by_funding_source` | binary | Q7j | NEW | (PRI-only) |
| `lobbying_search_filter_by_subject` | binary | Q7k | NEW | FOCAL contact_log.11 (cell content) |
| `lobbying_search_filter_by_assigned_entity` | binary | Q7l | NEW | FOCAL contact_log family |
| `lobbying_search_filter_by_principal_legal_status` | binary | Q7m | NEW | (PRI-only) |
| `lobbying_search_filter_by_sector` | binary | Q7n | NEW | (PRI-only) |
| `lobbying_search_filter_by_subsector` | binary | Q7o | NEW | (PRI-only) |
| `lobbying_search_simultaneous_multicriteria_capability` | typed `int` ∈ 0..15 | Q8 | strict-c_003, loose-c_010 | FOCAL openness.5, OpenSecrets `public_avail_search` |

### Disclosure-law-side rows (61 PRI items → 47 distinct rows, all on legal_availability)

| Row id (working name) | Cell type | PRI items reading | Provenance hint | Other rubrics likely to read |
|---|---|---|---|---|
| `actor_paid_lobbyist_registration_required` | binary | A1 | NEW | (gate; most rubrics assume this) |
| `actor_volunteer_lobbyist_registration_required` | binary | A2 | NEW | (PRI-only at this granularity) |
| `actor_principal_registration_required` | binary | A3 | NEW | (distinct from CPI #203 `principal_spending_report_required`) |
| `actor_lobbying_firm_registration_required` | binary | A4 | NEW | (PRI-only) |
| `actor_governors_office_registration_required` | binary | A5 | NEW | (actor-side; CPI's def_target is target-side) |
| `actor_executive_agency_registration_required` | binary | A6 | (overlaps loose-c_006 content-wise on actor axis) | Newmark `def_administrative_agency_lobbying` |
| `actor_legislative_branch_registration_required` | binary | A7 | NEW | (actor-side mirror) |
| `actor_independent_agency_registration_required` | binary | A8 | NEW | (actor-side mirror) |
| `actor_local_government_registration_required` | binary | A9 | NEW | v1.1 schema role enumeration |
| `actor_intergov_agency_lobbying_registration_required` | binary | A10 | NEW | (PRI-only at this granularity) |
| `actor_public_entity_other_registration_required` | binary | A11 | NEW | (PRI-only; depends on C-series public-entity-def cells) |
| `exemption_for_govt_official_capacity_exists` | binary | B1 | NEW | (PRI-only at this granularity; direction-of-scoring open) |
| `exemption_partial_for_govt_agencies` | binary | B2 | NEW | (PRI-only) |
| `govt_agencies_subject_to_lobbyist_disclosure_requirements` | binary | B3 | NEW | (PRI-only) |
| `govt_agencies_subject_to_principal_disclosure_requirements` | binary | B4 | NEW | (PRI-only) |
| `law_defines_public_entity` | binary | C0 | NEW | (PRI's gate; sub-criteria captured but unscored) |
| `public_entity_def_relies_on_ownership` | binary | C1 | NEW | (PRI-extracted; not read by PRI projection) |
| `public_entity_def_relies_on_revenue_structure` | binary | C2 | NEW | (PRI-extracted; not read by PRI projection) |
| `public_entity_def_relies_on_charter` | binary | C3 | NEW | (PRI-extracted; not read by PRI projection) |
| `law_includes_materiality_test` | binary (derived) | D0 | NEW | (gate, derivable from D1+D2 typed cells) |
| `materiality_threshold_financial_value` | typed `Optional[Decimal]` | D1_present, D1_value | (refines strict-c_009 / loose-c_016) | CPI #197 (different scope: registration vs filing-exemption); FOCAL TBD |
| `materiality_threshold_time_percent` | typed `Optional[float]` | D2_present, D2_value | NEW | (PRI-only at this granularity) |
| `principal_spending_report_required` | binary | E1a | (CPI #203) | CPI #203, FOCAL TBD |
| `principal_report_includes_principal_contact_info` | binary | E1b | NEW | (PRI-only) |
| `principal_report_includes_lobbyist_names` | binary | E1c | NEW | (inverse-direction of E2c) |
| `principal_report_includes_lobbyist_contact_info` | binary | E1d | NEW | (PRI-only) |
| `principal_report_includes_business_nature` | binary | E1e | NEW | (PRI-only) |
| `principal_report_includes_direct_compensation` | binary | E1f_i | loose-c_028 | (CPI #203's compound read; HG Q13; Sunlight) |
| `principal_report_includes_indirect_costs` | binary | E1f_ii | loose-c_029 | (PRI-only at this granularity) |
| `principal_report_includes_gifts_entertainment_transport_lodging` | binary | E1f_iii | loose-c_030 | Newmark/FOCAL "expenditures benefitting officials" family |
| `principal_report_uses_itemized_format` | binary | E1f_iv | loose-c_031 | CPI #201 (lobbyist-side) |
| `principal_report_includes_general_issues` | binary | E1g_i | loose-c_032 | FOCAL contact_log family |
| `principal_report_includes_specific_bill_number` | binary | E1g_ii | loose-c_012 | FOCAL contact_log.11 |
| `principal_report_cadence_includes_monthly` | binary | E1h_i | loose-c_033 | (CPI #202 enum derives from these 6 binaries) |
| `principal_report_cadence_includes_quarterly` | binary | E1h_ii | loose-c_034 | (CPI #202 enum) |
| `principal_report_cadence_includes_triannual` | binary | E1h_iii | loose-c_035 | (CPI #202 enum) |
| `principal_report_cadence_includes_semiannual` | binary | E1h_iv | loose-c_036 | (CPI #202 enum) |
| `principal_report_cadence_includes_annual` | binary | E1h_v | loose-c_037 | (CPI #202 enum) |
| `principal_report_cadence_includes_other` | binary | E1h_vi | loose-c_038 | (CPI #202 enum) |
| `principal_report_cadence_other_specification` | free-text | E1h_vi (companion) | NEW | (free-text spec) |
| `principal_report_includes_contacts_made` | binary | E1i | loose-c_039 | FOCAL contact_log.* |
| `principal_report_includes_major_financial_contributors` | binary | E1j | NEW | (PRI scores independently per paper) |
| `lobbyist_spending_report_required` | binary | E2a | (CPI #201) | CPI #201, HG Q*, Sunlight, Newmark |
| `lobbyist_report_includes_lobbyist_contact_info` | binary | E2b | NEW | (PRI-only) |
| `lobbyist_report_includes_principal_names` | binary | E2c | strict-c_016, loose-c_020 | FOCAL relationships.1 |
| `lobbyist_report_includes_principal_contact_info` | binary | E2d | NEW | (PRI-only) |
| `lobbyist_report_includes_principal_business_nature` | binary | E2e | NEW | (PRI-only) |
| `lobbyist_report_includes_direct_compensation` | binary | E2f_i | loose-c_028 (paired with E1f_i) | strict-c_018 (HG Q13 + Sunlight `lobbyist_compensation`); CPI #201 |
| `lobbyist_report_includes_indirect_costs` | binary | E2f_ii | loose-c_029 | (PRI-only at this granularity) |
| `lobbyist_report_includes_gifts_entertainment_transport_lodging` | binary | E2f_iii | loose-c_030 | Newmark/FOCAL "expenditures benefitting officials" |
| `lobbyist_report_uses_itemized_format` | binary | E2f_iv | loose-c_031 | CPI #201 — same row |
| `lobbyist_report_includes_general_issues` | binary | E2g_i | loose-c_032 | FOCAL contact_log |
| `lobbyist_report_includes_specific_bill_number` | binary | E2g_ii | loose-c_012 | FOCAL contact_log.11 |
| `lobbyist_report_cadence_includes_monthly` | binary | E2h_i | loose-c_033 | (CPI #202 enum) |
| `lobbyist_report_cadence_includes_quarterly` | binary | E2h_ii | loose-c_034 | (CPI #202 enum) |
| `lobbyist_report_cadence_includes_triannual` | binary | E2h_iii | loose-c_035 | (CPI #202 enum) |
| `lobbyist_report_cadence_includes_semiannual` | binary | E2h_iv | loose-c_036 | (CPI #202 enum) |
| `lobbyist_report_cadence_includes_annual` | binary | E2h_v | loose-c_037 | (CPI #202 enum) |
| `lobbyist_report_cadence_includes_other` | binary | E2h_vi | loose-c_038 | (CPI #202 enum) |
| `lobbyist_report_cadence_other_specification` | free-text | E2h_vi (companion) | NEW | (free-text spec) |
| `lobbyist_report_includes_contacts_made` | binary | E2i | loose-c_039 | FOCAL contact_log.* |

### Row-count rollup

- Accessibility-side: **22 rows** (all NEW or sparsely cross-rubric except Q2/Q5/Q6/Q8 which cluster with FOCAL/HG/OpenSecrets).
- Disclosure-law-side: **47 rows** — 11 actor-side (A-series), 4 govt-exemption (B-series), 4 public-entity-def (C-series), 3 materiality-test (D-series, condensed via typed-cell pattern from 5 PRI items), 19 principal-side (E1-series, with E1h yielding 6 binary + 1 free-text companion), 18 lobbyist-side (E2-series, structurally parallel to E1 minus E1j). Plus 2 free-text specification companions on E1h_vi/E2h_vi (counted within the 47).
- **Total: 69 distinct compendium rows touched by 83 PRI atomic items.**
- **NEW rows (not previously surfaced by CPI mapping):** ~52 (PRI's atomization is much finer than CPI's, especially in Q7a-o, A1-A11, B1-4, C0-3, D, E1h/E2h cadence, and E2 lobbyist-side identifiers). This matches the handoff's prediction ("30-50 new compendium rows").

---

## Open issues surfaced by PRI for design-team review

1. **Q8's 0-15 ordinal partition is undocumented.** The published per-state Q8_normalized values (mostly 0.1) suggest scorer-judgment partial credit on a 0-15 raw scale that the paper does not partition into anchors. Direct analogue to CPI's 25/75 partial-credit issue — see CPI mapping Open Issue 2. Phase C decides whether the cell carries the raw 0-15 ordinal directly (passthrough) or computes from underlying observables via a deterministic mapping. Per user direction (a2, 2026-05-07): treat as Open Issue, pass cell value through, defer partition decision to Phase C. (For comparison: CPI 2015 has 8 items with this shape; PRI 2010 has 1 — but the published per-state values cluster heavily at 0.1, making 0-15-tier-distinction less load-bearing for PRI than 25/75-distinction was for CPI.)

2. **Several PRI items have undefined operationalizations** (PRI source TSV pre-flagged these as "flag for Phase 3"):
   - Q3 "easily found" not defined
   - Q5 "historical" horizon not defined
   - Q6 "immediately useable" format not defined (2010 Excel/SPSS gold standard now obsolete)
   These are not Phase B blockers — the compendium row carries the binary cell; Phase C operationalizes the threshold for projection. But all three need explicit operationalizations for any deterministic projection.

3. **B1/B2 scoring direction ambiguous.** "Government exemption exists" (B1=True) structurally reduces transparency, but PRI's published B sub-aggregate may treat it as +1 for legal completeness rather than -1 for transparency loss. Source TSV note flags this for Phase 3. Phase C empirical fit against the per-state B_gov_exemptions sub-aggregate (max 4) will reveal the direction. Provisional projection rule above assumes +1 for True; flip to −1 if Phase C fitting demands.

4. **E1h/E2h enum-vs-binary representation tension with CPI #202.** PRI atomizes reporting-cadence options as 6 binary items (E1h_i-vi, E2h_i-vi) where each asks "is X an allowed cadence?" CPI #202 reads cadence as an enum cell with one most-frequent value. Compendium 2.0 design choice: use PRI's binary representation as canonical (allows multi-cadence regimes naturally), and let CPI's enum read derive as `min(allowed cadences, ordered by frequency)`. This is an explicit retroactive modification of the CPI mapping's enum row — flag for design-team review. The retroactive change is small (one cell representation in compendium 2.0; CPI's projection logic reads the same observable just differently). Adopting PRI's representation also lets E1h_vi / E2h_vi "Other" capture as a free-text companion cell — which CPI's enum representation didn't accommodate.

5. **E1j's independent-of-E aggregation.** PRI paper §III.E intro states E1j (major financial contributors) is scored independently of the rest of E. Phase C's E1+E2-rollup-fitting must respect this carve-out. If empirical fitting against E_info_disclosed treats E1j as part of the bucket, the rollup will be miscalibrated. Phase B doesn't resolve this; Phase C consumption layer needs to either (a) treat E1j as a separate sub-aggregate slot in the projection output, or (b) document that the published E_info_disclosed includes E1j and fold accordingly.

6. **C1-C3 in compendium but unread by PRI projection.** PRI 2010 §III.C has 4 items (C0 + C1+C2+C3) but per source TSV "Table 5 reports C as 0/1 only" — only the gate enters the published score. C1-C3 are real distinguishing cases (states define "public entity" using different criteria) and belong in compendium 2.0 for cross-rubric and downstream-consumer use, but the PRI projection function reads only C0. This is a clean example of the success-criterion's expected behavior: rows in compendium that some projections don't read (kept until *no* projection reads them, then candidates for deletion). Same pattern for D1_value/D2_value — values captured in cells but not read by PRI projection (which scores D as 0/1 gate-only).

7. **De-jure / de-facto staging recommendation carries forward from CPI.** The CPI mapping flagged that 2015-vintage de-facto items face evidence-circularity if populated from CPI's own scores. PRI 2010 has the same shape on its 22 accessibility items (all practical_availability) — populating cells from PRI's published per-state scores and projecting PRI back validates against itself. **Recommendation:** Phase C validation for PRI on 2010 vintage stages de-jure half first (61 disclosure-law items → cells populated from statute, no circularity), de-facto half (22 accessibility items) held until practical-availability extraction (Track B) can populate cells from primary observation (portal scrape, Wayback Machine archive of 2010-era state lobbying portals if available). User decision pending whether to stage. Same staging decision as CPI; resolves once for both.

8. **Per-atomic-item ground truth not published.** Unlike CPI 2015 (which has 50×14=700 per-state per-indicator scores in the criteria xlsx), PRI 2010 publishes only sub-aggregate-level per-state data (5 disclosure-law sub-aggregates + 8 accessibility sub-components). Per-atomic-item validation is therefore impossible against PRI's published data. Phase C validation tolerance for PRI must be at sub-aggregate granularity, not per-item. This is fine — the cross-rubric validation from CPI's per-item ground truth still validates PRI rows that overlap, and the sub-aggregate fit is sufficient to validate the within-rubric aggregation rule.

9. **Same-text PRI atomic items in different sections (paired E1/E2 entries).** The consensus method correctly identified PRI's E1/E2 parallel pairs (loose-c_028 through c_039 are mostly E1f_*/E2f_* and E1h_*/E2h_* and E1i/E2i) — each cluster contains exactly two PRI items differing only in actor (principal vs lobbyist). Per the granularity-bias convention, these collapse into TWO compendium rows (`principal_*` and `lobbyist_*`), not one — because regimes can regulate the two actors asymmetrically. Open question: is the two-row split the right call, or are there cases where a single row with an "actor" enum cell would be more general? The two-row split is more direct and matches the granular regulatory reality; sticking with it. Flagged for review.

---

## What PRI doesn't ask that other rubrics will (Phase B for those rubrics)

For continuity with the CPI mapping doc's reverse-coverage section. PRI 2010 already touches 69 distinct compendium rows (vs CPI's 21), so the unique-to-other-rubrics list is shorter:

- **Audits / penalties** (CPI #207-209, HG Q40-42 enforcement battery): PRI has no audit or penalty items. Compendium rows already in CPI mapping.
- **Cooling-off / revolving door** (HG Q48, Newmark2017 personnel battery): PRI has no cooling-off items. Out of scope per disclosure-first qualifier; will enter compendium when prohibitions/personnel rounds run.
- **Specific gift bans / contingent-fee bans** (Newmark prohib battery): not in PRI; deferred per disclosure-first qualifier.
- **Per-meeting contact-log granularity beyond "are contacts disclosed"** (FOCAL contact_log.1 through .11 in detail): PRI's E1i/E2i is a coarse binary; FOCAL atomizes 11 sub-fields of the contact log. FOCAL projection mapping will add ~11 finer-grained rows on the contact_log family that PRI's binary subsumes.
- **Search/filter on de-jure axis** (e.g., "is the state required by law to publish in machine-readable format"): PRI Q6 / Q7-family read practical-availability only; the de-jure pair may not exist statutorily in most US states (most lobbying disclosure laws don't mandate a portal format).
- **Frequency-of-website-updates** (FOCAL timeliness.1, HG Q38): PRI Q4 reads a coarser binary "current data present"; FOCAL/HG read finer cadence.
- **Open-data licensing / API access** (FOCAL openness.* battery): PRI Q6 collapses these into a single binary; FOCAL atomizes license, format, downloadability, machine-readability separately.

These rows enter compendium 2.0 from the other rubrics' projection mappings, not PRI's.
