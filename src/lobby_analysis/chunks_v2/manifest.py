"""The hand-curated `CHUNKS_V2` manifest.

Partitions the 181 v2 TSV rows (= 186 cells) into 15 topic-coherent chunks.
Verified at plan-write time (2026-05-14) against `compendium/disclosure_side_compendium_items_v2.tsv`
at the `extraction-harness-brainstorm` HEAD: every row appears in exactly one
chunk; no chunk_id collisions; no typos.

Both halves of all 5 combined-axis rows ride in the same chunk per Q3 of the
chunks brainstorm — when `build_chunks()` resolves a `ChunkDef`, every entry
in `member_row_ids` that the registry treats as combined-axis contributes both
its legal-half and its practical-half cells to the resulting `Chunk`.
"""

from __future__ import annotations

from .chunks import ChunkDef


CHUNKS_V2: tuple[ChunkDef, ...] = (
    ChunkDef(
        chunk_id="lobbying_definitions",
        topic="What counts as lobbying or a lobbyist — definitional rows",
        member_row_ids=(
            "def_lobbying_activity_types",
            "def_lobbyist_actor_types",
            "law_defines_public_entity",
            "law_includes_materiality_test",
            "def_target_executive_agency",
            "def_target_executive_staff",
            "def_target_governors_office",
            "def_target_independent_agency",
            "def_target_legislative_branch",
            "def_target_legislative_staff",
            "def_actor_class_elected_officials",
            "def_actor_class_public_employees",
            "public_entity_def_relies_on_charter",
            "public_entity_def_relies_on_ownership",
            "public_entity_def_relies_on_revenue_structure",
        ),
        notes=(
            "Spiritual successor to iter-1's 7-row `definitions` chunk. Three "
            "sub-axes (TARGET / ACTOR / THRESHOLD-qualitative); preamble will "
            "teach the disambiguation."
        ),
    ),
    ChunkDef(
        chunk_id="actor_registration_required",
        topic="Which entity types must register as lobbyists",
        member_row_ids=(
            "actor_executive_agency_registration_required",
            "actor_governors_office_registration_required",
            "actor_independent_agency_registration_required",
            "actor_intergov_agency_lobbying_registration_required",
            "actor_legislative_branch_registration_required",
            "actor_lobbying_firm_registration_required",
            "actor_local_government_registration_required",
            "actor_paid_lobbyist_registration_required",
            "actor_principal_registration_required",
            "actor_public_entity_other_registration_required",
            "actor_volunteer_lobbyist_registration_required",
        ),
        notes=(
            "All 11 `actor_*_registration_required` rows. Mechanically uniform: "
            "'is X-type entity required to register?'"
        ),
    ),
    ChunkDef(
        chunk_id="registration_thresholds",
        topic="Quantitative gates for lobbyist registration and disclosure",
        member_row_ids=(
            "lobbyist_registration_threshold_compensation_dollars",
            "lobbyist_registration_threshold_expenditure_dollars",
            "lobbyist_registration_threshold_time_percent",
            "lobbyist_filing_itemization_de_minimis_threshold_dollars",
            "lobbyist_filing_de_minimis_threshold_dollars",
            "lobbyist_filing_de_minimis_threshold_time_percent",
        ),
        notes=(
            "The quantitative thresholds. Qualitative `law_includes_materiality_test` "
            "lives in `lobbying_definitions` since it functions definitionally, "
            "not as a numeric gate."
        ),
    ),
    ChunkDef(
        chunk_id="registration_mechanics_and_exemptions",
        topic="Registration process: when, how, who's exempt",
        member_row_ids=(
            "lobbyist_registration_required",
            "lobbyist_registration_renewal_cadence",
            "lobbyist_registration_amendment_deadline_days",
            "lobbyist_registration_deadline_days_after_first_lobbying",
            "separate_registrations_for_lobbyists_and_clients",
            "lobbyist_required_to_submit_photograph_with_registration",
            "exemption_for_govt_official_capacity_exists",
            "exemption_partial_for_govt_agencies",
        ),
        notes=(
            "Contains 2 of the 5 combined-axis rows (`lobbyist_registration_required`, "
            "`lobbyist_registration_deadline_days_after_first_lobbying`). Mixed axis_summary "
            "expected."
        ),
    ),
    ChunkDef(
        chunk_id="lobbyist_registration_form_contents",
        topic="What fields appear on the lobbyist registration form",
        member_row_ids=(
            "lobbyist_reg_form_includes_bill_or_action_identifier",
            "lobbyist_reg_form_includes_business_associations_with_officials",
            "lobbyist_reg_form_includes_compensation",
            "lobbyist_reg_form_includes_employment_type",
            "lobbyist_reg_form_includes_general_subject_matter",
            "lobbyist_reg_form_includes_lobbyist_business_id",
            "lobbyist_reg_form_includes_lobbyist_contact_details",
            "lobbyist_reg_form_includes_lobbyist_full_name",
            "lobbyist_reg_form_includes_lobbyist_legal_form",
            "lobbyist_reg_form_includes_lobbyist_prior_public_offices_held",
            "lobbyist_reg_form_includes_lobbyist_sector",
            "lobbyist_reg_form_includes_position_on_bill",
            "lobbyist_reg_form_lists_each_employer_or_principal",
        ),
        notes="All 13 `lobbyist_reg_form_includes_*` rows. Tight cluster.",
    ),
    ChunkDef(
        chunk_id="lobbyist_spending_report",
        topic="Lobbyist's periodic spending report — cadence, content, format",
        member_row_ids=(
            "lobbyist_spending_report_available_as_downloadable_database",
            "lobbyist_spending_report_available_as_pdf_or_image_on_web",
            "lobbyist_spending_report_available_as_photocopies_from_office_only",
            "lobbyist_spending_report_available_as_searchable_database_on_web",
            "lobbyist_spending_report_cadence_includes_annual",
            "lobbyist_spending_report_cadence_includes_monthly",
            "lobbyist_spending_report_cadence_includes_other",
            "lobbyist_spending_report_cadence_includes_quarterly",
            "lobbyist_spending_report_cadence_includes_semiannual",
            "lobbyist_spending_report_cadence_includes_triannual",
            "lobbyist_spending_report_cadence_other_specification",
            "lobbyist_spending_report_categorizes_expenses_by_type",
            "lobbyist_spending_report_filing_cadence",
            "lobbyist_spending_report_includes_bill_or_action_identifier",
            "lobbyist_spending_report_includes_compensation_broken_down_by_payer",
            "lobbyist_spending_report_includes_contacts_made",
            "lobbyist_spending_report_includes_expenditure_per_issue",
            "lobbyist_spending_report_includes_general_issues",
            "lobbyist_spending_report_includes_general_subject_matter",
            "lobbyist_spending_report_includes_gifts_entertainment_transport_lodging",
            "lobbyist_spending_report_includes_indirect_costs",
            "lobbyist_spending_report_includes_itemized_expenses",
            "lobbyist_spending_report_includes_lobbyist_contact_info",
            "lobbyist_spending_report_includes_position_on_bill",
            "lobbyist_spending_report_includes_principal_business_nature",
            "lobbyist_spending_report_includes_principal_contact_info",
            "lobbyist_spending_report_includes_principal_names",
            "lobbyist_spending_report_includes_specific_bill_number",
            "lobbyist_spending_report_includes_total_compensation",
            "lobbyist_spending_report_includes_total_expenditures",
            "lobbyist_spending_report_required",
            "lobbyist_spending_report_required_when_no_activity",
            "lobbyist_spending_report_scope_includes_household_members_of_officials",
            "lobbyist_spending_report_uses_itemized_format",
        ),
        notes=(
            "34 rows. Single chunk per user approval — the cluster is one "
            "coherent topic (the report). Contains 1 combined-axis row "
            "(`lobbyist_spending_report_filing_cadence`)."
        ),
    ),
    ChunkDef(
        chunk_id="principal_spending_report",
        topic="Principal's (employer's) periodic spending report",
        member_row_ids=(
            "principal_spending_report_cadence_includes_annual",
            "principal_spending_report_cadence_includes_monthly",
            "principal_spending_report_cadence_includes_other",
            "principal_spending_report_cadence_includes_quarterly",
            "principal_spending_report_cadence_includes_semiannual",
            "principal_spending_report_cadence_includes_triannual",
            "principal_spending_report_cadence_other_specification",
            "principal_spending_report_includes_business_nature",
            "principal_spending_report_includes_compensation_paid_to_lobbyists",
            "principal_spending_report_includes_contacts_made",
            "principal_spending_report_includes_general_issues",
            "principal_spending_report_includes_gifts_entertainment_transport_lodging",
            "principal_spending_report_includes_indirect_costs",
            "principal_spending_report_includes_lobbyist_contact_info",
            "principal_spending_report_includes_lobbyist_names",
            "principal_spending_report_includes_major_financial_contributors",
            "principal_spending_report_includes_principal_contact_info",
            "principal_spending_report_includes_specific_bill_number",
            "principal_spending_report_includes_total_expenditures",
            "principal_spending_report_required",
            "principal_spending_report_uses_itemized_format",
            "lobbyist_or_principal_reg_form_includes_member_or_sponsor_names",
            "principal_spending_report_lists_lobbyists_employed",
        ),
        notes=(
            "21 `principal_spending_*` rows + 2 adjacent principal-side rows "
            "that don't fit elsewhere."
        ),
    ),
    ChunkDef(
        chunk_id="lobbying_contact_log",
        topic="Contact-log disclosure: per-meeting records",
        member_row_ids=(
            "lobbying_contact_log_includes_beneficiary_organization",
            "lobbying_contact_log_includes_communication_form",
            "lobbying_contact_log_includes_date",
            "lobbying_contact_log_includes_institution_or_department",
            "lobbying_contact_log_includes_location",
            "lobbying_contact_log_includes_materials_shared",
            "lobbying_contact_log_includes_meeting_attendees",
            "lobbying_contact_log_includes_official_contacted_name",
            "lobbying_contact_log_includes_topics_discussed",
        ),
        notes="All 9 `lobbying_contact_log_*` rows.",
    ),
    ChunkDef(
        chunk_id="other_lobbyist_filings",
        topic="Other lobbyist/principal filings — itemized expenditures, special reports",
        member_row_ids=(
            "lobbyist_or_principal_reg_form_includes_lobbyist_board_memberships",
            "lobbyist_or_principal_spending_report_includes_lobbyist_count_total_and_FTE",
            "lobbyist_or_principal_spending_report_includes_time_spent_on_lobbying",
            "lobbyist_or_principal_spending_report_includes_trade_association_dues_or_sponsorship",
            "lobbyist_or_principal_spending_report_includes_contributions_received_for_lobbying",
            "lobbyist_itemized_expenditure_identifies_employer_or_principal",
            "lobbyist_itemized_expenditure_identifies_recipient",
            "lobbyist_itemized_expenditure_includes_date",
            "lobbyist_itemized_expenditure_includes_description",
            "lobbyist_filing_distinguishes_in_house_vs_contract_filer",
            "lobbyist_spending_report_includes_campaign_contributions",
            "consultant_lobbyist_report_includes_income_by_source_type",
        ),
        notes=(
            "Catch-all for lobbyist/principal filing rows not in the two big "
            "spending-report chunks. The "
            "`lobbyist_or_principal_spending_report_includes_contributions_received_for_lobbying` "
            "row may fit better in `principal_spending_report` or "
            "`lobbyist_spending_report`; flagged as a coherence judgment call."
        ),
    ),
    ChunkDef(
        chunk_id="enforcement_and_audits",
        topic="Does the regime have teeth — penalties and audits",
        member_row_ids=(
            "lobbying_violation_penalties_imposed_in_practice",
            "lobbying_disclosure_audit_required_in_law",
        ),
        notes=(
            "Only 2 rows but topically distinct. Both rows are combined-axis "
            "(4 cells total). If 2-row chunks feel too granular, merging into "
            "`oversight_and_government_subjects` is reasonable."
        ),
    ),
    ChunkDef(
        chunk_id="search_portal_capabilities",
        topic="Search & filter capabilities of the state's lobbying portal",
        member_row_ids=(
            "lobbying_search_filter_by_assigned_entity",
            "lobbying_search_filter_by_compensation",
            "lobbying_search_filter_by_funding_source",
            "lobbying_search_filter_by_lobbyist_location",
            "lobbying_search_filter_by_lobbyist_name",
            "lobbying_search_filter_by_misc_expenses",
            "lobbying_search_filter_by_principal",
            "lobbying_search_filter_by_principal_legal_status",
            "lobbying_search_filter_by_principal_location",
            "lobbying_search_filter_by_sector",
            "lobbying_search_filter_by_specific_date",
            "lobbying_search_filter_by_subject",
            "lobbying_search_filter_by_subsector",
            "lobbying_search_filter_by_time_period",
            "lobbying_search_filter_by_total_expenditures",
            "lobbying_search_simultaneous_multicriteria_capability",
        ),
        notes="All 16 `lobbying_search_*` rows. All practical-axis.",
    ),
    ChunkDef(
        chunk_id="data_quality_and_access",
        topic="Portal data quality, format, and downloadability",
        member_row_ids=(
            "lobbying_data_changes_flagged_with_versioning",
            "lobbying_data_current_year_present_on_website",
            "lobbying_data_downloadable_in_analytical_format",
            "lobbying_data_historical_archive_present",
            "lobbying_data_minimally_available",
            "lobbying_data_no_user_registration_required",
            "lobbying_data_open_data_quality",
            "lobbying_data_open_license",
            "lobbying_records_copy_cost_per_page_dollars",
            "sample_lobbying_forms_available_on_web",
        ),
        notes=(
            "All practical-axis. The `lobbying_data_open_data_quality` row is a "
            "`typed int 0-100 step 25 (practical)` GradedIntCell."
        ),
    ),
    ChunkDef(
        chunk_id="disclosure_documents_online",
        topic="Online accessibility of the disclosure documents themselves",
        member_row_ids=(
            "lobbying_disclosure_data_includes_unique_identifiers",
            "lobbying_disclosure_data_linked_to_other_datasets",
            "lobbying_disclosure_documents_free_to_access",
            "lobbying_disclosure_documents_online",
            "lobbying_disclosure_offline_request_response_time_days",
        ),
        notes=(
            "All 5 practical `lobbying_disclosure_*` rows (excluding "
            "`lobbying_disclosure_audit_required_in_law` which is in "
            "`enforcement_and_audits`)."
        ),
    ),
    ChunkDef(
        chunk_id="lobbyist_directory_and_website",
        topic="Lobbyist directory format and the state's lobbying website itself",
        member_row_ids=(
            "lobbyist_directory_available_as_downloadable_database",
            "lobbyist_directory_available_as_pdf_or_image_on_web",
            "lobbyist_directory_available_as_photocopies_from_office_only",
            "lobbyist_directory_available_as_searchable_database_on_web",
            "lobbyist_directory_update_cadence",
            "online_lobbyist_registration_filing_available",
            "online_lobbyist_spending_report_filing_available",
            "lobbying_website_easily_findable",
            "state_has_dedicated_lobbying_website",
        ),
        notes=("All practical-axis. Combines directory format with parent-website-existence rows."),
    ),
    ChunkDef(
        chunk_id="oversight_and_government_subjects",
        topic="Oversight agency activities and government-entity disclosure subjects",
        member_row_ids=(
            "oversight_agency_provides_efile_training",
            "oversight_agency_publishes_aggregate_lobbying_spending_by_filing_deadline",
            "oversight_agency_publishes_aggregate_lobbying_spending_by_industry",
            "oversight_agency_publishes_aggregate_lobbying_spending_by_year",
            "ministerial_diary_available_online",
            "ministerial_diary_disclosure_cadence",
            "govt_agencies_subject_to_lobbyist_disclosure_requirements",
            "govt_agencies_subject_to_principal_disclosure_requirements",
        ),
        notes=(
            "Mixed axis: 6 practical (oversight + ministerial) + 2 legal "
            "(govt_agencies_*). The chunk most likely to want refinement; if "
            "the legal vs practical mix is unwieldy, split `govt_agencies_*` "
            "into their own chunk and merge `enforcement_and_audits` into "
            "oversight here."
        ),
    ),
)
