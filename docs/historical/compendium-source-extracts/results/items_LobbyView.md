# LobbyView — federal LDA data-infrastructure schema (treated as rubric items for the state-level compendium)

## 1. What this file is, and why it's not the same shape as the other rubrics

LobbyView (Kim 2018; Kim et al. 2025) is **not a scoring rubric**. It is **federal-only data infrastructure**: a database (and REST API) built on the universe of LDA reports filed under the Lobbying Disclosure Act of 1995, enriched with bill-linking, name disambiguation, NAICS / Compustat merges, full-text indices, and (in Kim 2025) LLM+GNN-derived bill-position labels.

This branch's compendium-construction project frames itself, informally, as **"LobbyView for 50 states + federal LDA"**. Under that framing, every schema field LobbyView captures becomes a question of the form: *"Does state-level disclosure data also capture this field, and if so, on what axis (legal_availability vs practical_availability)?"* The fields are the rubric items. The "scoring rule" for each item is degenerate (`N/A`) because LobbyView is not scoring states; it's storing data.

This is a deliberate repurposing — the v1.1 compendium schema's two-axis design (legal_availability / practical_availability per row) is the right shape for treating LobbyView's schema as a lens on what state-level disclosure regimes do or don't capture.

## 2. Source paper(s) and other primary sources used

| Source | Role |
|---|---|
| `papers/Kim_2018__lobbyview.pdf` (working paper, partial draft) | Original schema description, bill-detection pipeline, Herfindahl module |
| `papers/Kim_2025__ai_bill_positions_lobbying.pdf` (PNAS 2025) | Updates: bill-position dataset (Support/Oppose/Amend/Monitor → Engage), GNN graph schema with explicit entity types and node features, LDA Section 16 / 18 anchors |
| `https://github.com/lobbyview/LobbyViewPythonPackage` (README, accessed 2026-05-07) | **Production schema** — verbatim field names exposed by the public REST API, mapped to LDA form sections |
| `https://www.lobbyview.org/data-download/api` (LobbyView API documentation page) | Confirms 6 dataset families and rate limits |

The Kim 2018 paper is a **partial draft** ("This document currently contains only some technical details of the database. We will soon update this paper to provide a full description of the methods used for constructing the database", lines 23-24). Production schema details — exact field names, the relational join keys, the API rate limits — are pulled from the LobbyView Python package README and the lobbyview.org API documentation page rather than the paper, which means the production schema is more granular than what the 2018 paper enumerates.

## 3. Relationship to the existing `items_Kim2018.tsv`

The existing `items_Kim2018.tsv` (18 rows) is a **paper-shaped extraction of the Kim 2018 working paper's database section** — it captures the abstractions (`LobbyingReport`, `LobbyingSpecificIssue`, `LobbyingIssue`, `Bill`, `BillTitle`, `Term`, the bill-detection pipeline, the Herfindahl module, the API, the full-text index) in roughly the granularity the 2018 paper describes them.

This new `items_LobbyView.tsv` (46 rows) is a **production-schema extraction**, anchored to the Python package README's verbatim field names and the LDA-form sections those fields correspond to (Section 15 = General Issue Area Code; Section 16 = Specific Lobbying Issues free-text; Section 17 = government entities contacted; Section 18 = Covered Official Position / revolving-door). It also folds in the Kim 2025 additions (bill_position, lobbyist demographics, expanded Bill node features).

**Relationship:** the two files are **largely overlapping but not identical** — `items_LobbyView.tsv` is the **superset for compendium-construction purposes**:

- Every row in `items_Kim2018.tsv` has a corresponding row in `items_LobbyView.tsv` (cross-referenced in the `notes` column with the literal string "Cross-ref items_Kim2018:<row_id>")
- `items_LobbyView.tsv` adds production-schema fields that the 2018 paper draft did not enumerate at field-grain (e.g., `report_quarter_code`, `is_no_activity`, `is_client_self_filer`, `is_amendment`, `gov_entity` for Section 17, the Bioguide / GovTrack legislator IDs, the bill_state status field)
- `items_LobbyView.tsv` adds Kim 2025 enrichments not in the 2018 paper (`bill_position`, `lobbyist_demographics`, expanded `client_industry_features`, the explicit `covered_official_position` Section 18 anchor)

Both files are kept. `items_Kim2018.tsv` is preserved as the per-paper extraction (the per-paper-extraction wave deliverable); `items_LobbyView.tsv` is the rubric-item representation for compendium construction. **Neither supersedes the other** — they differ in granularity and in which "version" of LobbyView they represent (paper-of-record draft vs. production schema as of late 2024).

## 4. Field count and grouping

**Total: 46 rows** in `items_LobbyView.tsv`. Grouped by where the field originates:

| Group | Count | Examples |
|---|---:|---|
| LDA-direct fields (raw federal disclosure inputs) | 13 | `report_uuid`, `client_name`, `registrant_name`, `report_year`, `report_quarter_code`, `amount`, `is_no_activity`, `is_client_self_filer`, `is_amendment`, `issue_ordi`, `issue_code` (Section 15), `gov_entity` (Section 17), `issue_text` (Section 16) |
| LDA-direct fields with revolving-door significance | 1 | `covered_official_position` (Section 18) |
| Congressional / external bill-data fields (Congress.gov / CRS) | 8 | `congress_number`, `bill_chamber`, `bill_resolution_type`, `bill_number`, `bill_introduced_datetime`, `bill_date_updated`, `bill_state`, `bill_url`, `bill_subject`, `bill_summary`, `bill_title` |
| Legislator-identification fields (Bioguide / GovTrack) | 6 | `legislator_id`, `legislator_govtrack_id`, `legislator_first_name`, `legislator_last_name`, `legislator_full_name`, `legislator_gender`, `legislator_birthday` |
| Lobbyist-identification fields | 1 | `lobbyist_id` (implicit in Kim 2025 graph; not a public-API endpoint as of late 2024) |
| LobbyView-added enrichments — IDs and classifications | 3 | `client_uuid`, `registrant_uuid`, `primary_naics`, `naics_description` |
| LobbyView-added enrichments — derived links and aggregates | 3 | `bill_client_link`, `n_bills_sponsored`, `industry_herfindahl` |
| LobbyView-added enrichments — firm-level external merges | 1 | `firm_financials` (Compustat) |
| Kim 2025 add-ons (LLM/GNN-derived) | 3 | `bill_position`, `lobbyist_demographics`, `client_industry_features` |
| Infrastructure | 2 | `api_bulk_download`, `full_text_search_index` |

(Some examples above span multiple group counts where a single row could plausibly belong to two groups; the per-group counts sum to slightly more than 46. Total distinct rows in the TSV = 46.)

## 5. Schema-as-rubric mapping decisions

Because LobbyView is not a scorecard, the standard rubric columns are repurposed:

- `paper_id` = `lobbyview_schema` for every row (single source-of-truth identifier).
- `indicator_id` = the verbatim field name from the production REST API (where it exists), or a paper-derived field name for fields not yet in the public API (e.g., `bill_client_link`, `bill_position`, `covered_official_position`, `lobbyist_id`, `lobbyist_demographics`, `client_industry_features`).
- `indicator_text` = the field's role / what it captures.
- `section_or_category` = which LobbyView table or LDA-form section the field belongs to (e.g., `Reports table`, `Issues table`, `Bill-Client Networks table (private endpoint)`, `LDA Section 18`).
- `indicator_type` = the field's data type as a categorical (one of: `identifier_uuid`, `numeric`, `categorical`, `datetime`, `boolean`, `free_text`, `derived_link`, `derived_score`, `infrastructure`).
- `scoring_rule` = always `N/A` (these aren't scored indicators). The slot is preserved so this file can be unioned with the rubric files in downstream tooling without column-mismatch.
- `source_quote` = verbatim quote from one of: the LobbyViewPythonPackage README endpoint docstrings; the Kim 2018 paper text; the Kim 2025 paper text; the lobbyview.org API documentation page. Multi-source rows have multiple quotes joined with `; `.
- `notes` = field-of-origin context (LDA-direct vs LobbyView-added vs external) + state-level analog commentary + the cross-reference to the corresponding row in `items_Kim2018.tsv` where applicable.

## 6. The federal-vs-state gap (load-bearing for the compendium)

This is what the rubric-mapping is FOR. Each row's `notes` column flags the state-level analog where one is meaningful, but a few generalizations apply across the schema:

- **The LDA gives a single federal statute defining what gets disclosed**; there is no 50-state equivalent. State regimes vary in cadence (annual / semi-annual / quarterly / monthly-when-in-session), in itemization granularity (some report compensation; some report only registration; some require bill-level activity disclosure), and in what's mandated at all (some states require near-zero, others require fine-grained per-contact logs).
- **The LDA defines a fixed Section 15 issue-code taxonomy**; most states use free-text issue descriptions only, so the LobbyView-style `issue_code` field has weak state-level analogs.
- **`gov_entity` (Section 17)** has highly variable state coverage — some states require disclosure of which legislator / agency / branch was contacted; many do not, with no equivalent of Section 17 at all.
- **`covered_official_position` (Section 18)** is the federal revolving-door disclosure field; state-level revolving-door disclosure is uneven, and many states require nothing equivalent. This field is load-bearing for any "revolving door" empirical work and is therefore a high-value compendium row.
- **`bill_position` (Kim 2025 add-on)** has virtually no state analog — states almost never require lobbyists to disclose their position (Support/Oppose/Amend/Monitor) on a bill. **Wisconsin is the notable exception** (Wisconsin requires lobbyists to disclose support/oppose/no-position on each piece of lobbied legislation). For most states, bill-position would have to be inferred (e.g., via the Kim 2025 LLM/GNN method) rather than read directly.
- **`firm_financials` (Compustat merge)** depends on the lobbying client being a publicly traded company — federally true for a meaningful share of lobbying activity, much less true at state level where lobbying clients include far more local non-profits, municipalities, professional associations, and ad-hoc coalitions outside the SEC-traceable universe.

## 7. Open questions / known gaps

- **`lobbyist_id` and `lobbyist_demographics` are not exposed as first-class endpoints in the 2024 public-API README**, despite lobbyist nodes being central in Kim 2025's GNN (25,043 lobbyists, with ethnicity / gender / party / past-Congress-affiliation features). This means the published bill-position dataset and the public-API surface are **not 1:1**. Practical implication: a state-level analog to LobbyView's lobbyist-graph features would need to either ingest LDA Form LD-2 individual-lobbyist records directly or use an alternative source. For state lobbying, individual-lobbyist disclosure is common but inconsistent.
- **The bill-detection pipeline's accuracy was never published in Kim 2018** (no precision/recall/F1 numbers on a labeled subset; "we will conduct several descriptive and statistical analyses to demonstrate the scope and quality of the lobbying database" was forward-promised but not delivered in this draft). This means downstream users of LobbyView's `bill_client_link` field are working with an undocumented error rate.
- **The firm-disambiguation method is not described in the Kim 2018 draft** ("we will show how we disambiguate interest group names using natural language processing (NLP) as well as collaborative filtering"). For a state-level system, this method choice is load-bearing and would need its own design.
- **The 2018 draft documents Whoosh + SQLite**; the production system is PostgreSQL + Elasticsearch. The Kim 2018 draft is therefore at risk of being out-of-date relative to what researchers actually query — which is why this file uses the LobbyView Python package README (production-schema-shaped) as the primary source for field names rather than the paper.

## 8. Downstream use

The 46 rows here become inputs to **Phase B's projection-mapping work** (per the implementing plan): each LobbyView row will be evaluated against compendium 2.0's row set to determine whether the compendium covers the field, and on which axis. The expected output of that mapping is a "schema-coverage projection" rather than a score-based projection — i.e., for each LobbyView field, does the compendium have a row that captures it for `Federal_US` (LDA jurisdiction) and, where applicable, for the 50 states? Per the implementation plan §Phase C step 10, "LobbyView — schema-coverage check rather than score projection. Different shape; tackled separately."

The federal-LDA validation jurisdiction (`Federal_US`) is the natural anchor for LobbyView coverage — every LobbyView row should map cleanly to a populated `Federal_US` cell, by definition. State coverage is the empirical question the compendium exists to answer.
