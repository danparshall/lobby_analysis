# Lobbying Data Model Specification

**Version:** 1.0
**Date:** 2026-04-17 (v0.1 draft); accepted 2026-04-21 (v1.0)
**Branch:** `lobbying-data-model` (archived to `docs/historical/` on acceptance)
**Status:** **Accepted.** v0.1 circulated for feedback; no changes requested. This is the schema contract for state extraction pipelines — fellows writing per-state pipelines emit JSON conforming to these pydantic models. Future changes should go through a new branch with a migration plan, not silent edits.

---

## Purpose

This document defines the **universal output data model** for the lobby_analysis project. Every fellow's state pipeline — regardless of how different the source portal is — must produce JSON that conforms to this schema. The model is the contract that lets 50 independent pipelines interoperate.

The model also defines a **State Master Record** per state that captures what that state's law requires, so we can programmatically distinguish "this state doesn't require this field" from "this filer failed to report a required field." This enables the compliance monitoring use case.

## Design Principles

1. **Store source faithfully, transform later.** Pipelines write what the state discloses. Normalization, cross-state entity resolution, and analytics are separate layers.
2. **Union schema with nullable fields.** The schema includes every field any state could populate. `null` means "not present in this record." The State Master Record tells you whether it *should* have been present.
3. **Hierarchies where they naturally exist.** A filing contains positions, expenditures, engagements, and gifts. We preserve that nesting. A fellow with graph DB experience will handle cross-entity linking downstream.
4. **Field-level provenance** on anything extracted by LLM or regex. Direct-copy structured fields use filing-level provenance.
5. **Amendment chain, not overwrites.** Each amendment is a new filing record with a `supersedes` link. `is_current` flag for easy filtering.

## Entity Overview

```
┌─────────────────────────────────────────────────────────┐
│                    Reference Entities                    │
│                                                         │
│  Person ──── ContactDetail, Identifier                  │
│  Organization ──── ContactDetail, Identifier            │
│  OrganizationRelationship (subsidiary_of, member_of...) │
│  BillReference (Open States ID or unresolved text)      │
└─────────────────────────────────────────────────────────┘
         │                          │
         ▼                          ▼
┌─────────────────────────────────────────────────────────┐
│                   Filing Entities                        │
│                                                         │
│  LobbyistRegistration                                   │
│    who (lobbyist, employer, clients)                    │
│    status, effective period, thresholds                 │
│                                                         │
│  LobbyingFiling (the main document)                    │
│    ├── financial totals                                 │
│    ├── positions: list[LobbyingPosition]               │
│    ├── expenditures: list[LobbyingExpenditure]         │
│    ├── engagements: list[LobbyingEngagement]           │
│    └── gifts: list[Gift]                               │
│                                                         │
│  FilingAction (amendment chain: supersedes/amends/...)  │
└─────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────┐
│                    Meta Entities                         │
│                                                         │
│  Provenance (per-field extraction metadata)             │
│  StateMasterRecord (per-state field requirements)       │
│    ├── registration_requirements                        │
│    ├── reporting_parties (who files what)               │
│    └── field_requirements (required/optional/n.a.)      │
└─────────────────────────────────────────────────────────┘
```

---

## Entity Details

### Person

Follows Popolo (OCDEP 5). Single display name — no first/middle/last segmentation.

**Name convention:** `name` is always a display-ready string (e.g., "Jane Q. Doe"). When a state portal provides name components separately (first, middle, last), assemble them into `name` and preserve the original components in `name_components` as a labeled dict. This avoids re-splitting from first principles when the source already gave us the parts.

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| id | str | yes | Pipeline-assigned UUID |
| name | str | yes | Display-ready name (e.g., "Jane Q. Doe") |
| name_components | dict[str, str] | no | Original components if source provided them separately (e.g., `{"first": "Jane", "middle": "Q.", "last": "Doe"}`). Null if source gave a single string. |
| contact_details | list[ContactDetail] | no | Phone, email, address |
| identifiers | list[Identifier] | no | Open States ID, LobbyView ID, etc. |
| prior_public_offices | list[PriorOffice] | no | Revolving door (FOCAL 5.1) |
| source_state | str | yes | State where this person record originates |

**ContactDetail:** `{ type: "address"|"phone"|"email"|"website", value: str, note: str }`
**Identifier:** `{ scheme: str, identifier: str }` — scheme examples: `"open_states"`, `"lobbyview"`, `"state_registration"`
**PriorOffice:** `{ office: str, institution: str, start_date: date|None, end_date: date|None }`

### Organization

Also Popolo-based.

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| id | str | yes | Pipeline-assigned UUID |
| name | str | yes | Legal name as filed |
| classification | str | no | `company`, `nonprofit`, `trade_association`, `lobbying_firm`, `government_agency`, `other` |
| contact_details | list[ContactDetail] | no | |
| identifiers | list[Identifier] | no | SoS entity ID, EIN, OpenCorporates, SEC CIK |
| sector | str | no | Industry sector (FOCAL 4.5) |
| legal_form | str | no | Public/private/nonprofit/NGO (FOCAL 4.3) |
| source_state | str | yes | |

### OrganizationRelationship

Handles corporate hierarchies that Popolo can't represent (no org-org memberships in OCDEP 5).

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| subject_org_id | str | yes | The child/member org |
| object_org_id | str | yes | The parent/association org |
| relationship_type | str | yes | `subsidiary_of`, `member_of`, `subcontracts_to`, `affiliate_of` |
| start_date | date | no | |
| end_date | date | no | |
| source | str | no | Where this relationship was disclosed |

### BillReference

Links lobbying activity to legislation.

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| open_states_id | str | no | Canonical ID, null if unresolved |
| original_text | str | yes | Bill reference as written in the filing |
| session | str | no | Legislative session |
| chamber | str | no | |
| bill_number | str | no | Parsed bill number |
| reference_type | str | yes | `bill`, `resolution`, `regulation`, `executive_order`, `budget`, `other` |
| is_resolved | bool | yes | Whether we matched to Open States |
| inferred_from_range_expansion | bool | no | True if expanded from "HB 101–105" |

---

### LobbyistRegistration

The legal predicate — "I am registered to lobby in state X." Separate from periodic activity reports.

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| id | str | yes | Pipeline-assigned UUID |
| state | str | yes | Two-letter abbreviation |
| registration_id | str | no | State's native registration ID |
| lobbyist | Person | yes | The registered lobbyist |
| employer | Organization | no | Firm or in-house employer |
| clients | list[Organization] | no | Principals/clients represented (FOCAL 6.1) |
| lobbyist_type | str | no | `professional`, `in_house_company`, `in_house_org`, `volunteer` (FOCAL 1.1) |
| contract_type | str | no | `salaried`, `contracted` (FOCAL 4.6) |
| compensation_type | str | no | `compensated`, `uncompensated` (FOCAL 7.7) |
| registration_date | date | no | |
| termination_date | date | no | |
| effective_period_start | date | no | |
| effective_period_end | date | no | |
| status | str | yes | `active`, `terminated`, `suspended`, `expired` |
| general_issue_areas | list[str] | no | Broad subject areas registered to lobby on |
| source_url | str | no | URL of the registration record |
| source_document | str | no | Path to raw source file |
| provenance | Provenance | no | Filing-level provenance |

---

### LobbyingFiling

The main document — a periodic activity report filed by a lobbyist, principal, or firm.

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| id | str | yes | Pipeline-assigned UUID |
| state | str | yes | Two-letter abbreviation |
| filing_id | str | no | State's native filing ID |
| filing_type | str | yes | `activity_report`, `expenditure_report`, `gift_disclosure`, `supplemental`, `other` |
| filer | Person or Organization | yes | Who filed this |
| filer_role | str | yes | `lobbyist`, `client`, `firm` — which reporting party |
| reporting_period_start | date | no | |
| reporting_period_end | date | no | |
| filed_date | date | no | |
| **Amendment handling** | | | |
| is_current | bool | yes | True if this is the latest version |
| supersedes | str | no | filing_id of the prior version |
| filing_action | str | yes | `original`, `amendment`, `termination`, `withdrawal` |
| **Financial totals** | | | |
| total_compensation | float | no | Direct lobbying costs (PRI E1f_i/E2f_i) |
| total_reimbursements | float | no | Indirect costs (PRI E1f_ii/E2f_ii) |
| total_other_costs | float | no | Gifts/entertainment/travel/lodging (PRI E1f_iii/E2f_iii) |
| total_expenditure | float | no | Aggregate (FOCAL 7.6) |
| total_income | float | no | For consultant lobbyists/firms (FOCAL 7.1) |
| income_per_client | dict[str, float] | no | Client ID → amount (FOCAL 7.2) |
| is_itemized | bool | no | Whether financials are itemized vs. lump-sum (PRI E1f_iv) |
| **Nested sub-entities** | | | |
| positions | list[LobbyingPosition] | no | Positions on bills |
| expenditures | list[LobbyingExpenditure] | no | Itemized expenditures |
| engagements | list[LobbyingEngagement] | no | Contact log entries |
| gifts | list[Gift] | no | Gifts to officials |
| **Source** | | | |
| source_url | str | no | URL of the filing |
| source_document | str | no | Path to raw source file |
| provenance | Provenance | no | Filing-level provenance |
| raw_text | str | no | Full text of the filing (for auditability) |

---

### LobbyingPosition

A filer's stated position on a specific bill or issue during a reporting period.

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| bill_reference | BillReference | no | Specific bill (PRI E1g_ii/E2g_ii) |
| position | str | no | `support`, `oppose`, `amend`, `monitor`, `engage`, `mention` |
| general_issue_area | str | no | Broad topic (PRI E1g_i/E2g_i; FOCAL 8.9) |
| description | str | no | Free-text description of lobbying activity |
| outcomes_sought | str | no | What the filer wants (FOCAL 8.10) |
| provenance | Provenance | no | |

### LobbyingExpenditure

An itemized expenditure line.

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| category | str | yes | `compensation`, `reimbursement`, `entertainment`, `travel`, `lodging`, `gift`, `campaign_contribution`, `membership_sponsorship`, `other` |
| amount | float | no | |
| currency | str | no | Default `USD` |
| recipient_name | str | no | Name of person/org receiving payment |
| recipient_role | str | no | `official`, `agency`, `vendor`, `lobbyist`, `other` |
| purpose | str | no | |
| expenditure_date | date | no | |
| issue_area | str | no | Expenditure per issue (FOCAL 7.8) |
| provenance | Provenance | no | |

### LobbyingEngagement

A specific act of lobbying — meeting, call, written communication. Most states do NOT require contact-level logging; this entity is relevant only for the subset that do (FOCAL category 8).

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| official_contacted | str | no | Name (FOCAL 8.2) |
| official_role | str | no | Position/title |
| institution | str | no | Agency/department (FOCAL 8.3) |
| contact_date | date | no | FOCAL 8.5 |
| form_of_contact | str | no | `in_person`, `phone`, `email`, `video`, `written`, `event`, `other` (FOCAL 8.6) |
| location | str | no | FOCAL 8.7 |
| attendees | list[str] | no | Names of all attendees (FOCAL 8.4) |
| topics | list[str] | no | FOCAL 8.9 |
| materials_shared | list[str] | no | FOCAL 8.8 |
| outcomes_sought | list[str] | no | FOCAL 8.10 |
| bill_references | list[BillReference] | no | FOCAL 8.11 |
| beneficiary_org | str | no | Organization/interest represented (FOCAL 8.1) |
| provenance | Provenance | no | |

### Gift

Gifts, meals, travel, entertainment provided to public officials.

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| recipient_name | str | yes | The official |
| recipient_role | str | no | |
| recipient_institution | str | no | |
| donor_name | str | no | The lobbyist/client who gave it |
| value | float | no | Dollar value |
| description | str | no | |
| gift_date | date | no | |
| gift_type | str | no | `meal`, `travel`, `lodging`, `entertainment`, `event_ticket`, `other` |
| provenance | Provenance | no | |

---

### Provenance

Attached to any field or sub-entity populated by LLM extraction, regex, or inference. Direct-copy structured fields use filing-level provenance only.

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| source_url | str | no | URL of the raw source |
| source_document | str | no | Path to the raw file on disk |
| extraction_method | str | yes | `direct_copy`, `regex`, `llm`, `inferred`, `human_corrected` |
| confidence | float | no | [0, 1] for non-direct extractions; null for direct_copy |
| model_version | str | no | For LLM extractions |
| prompt_version | str | no | For LLM extractions |
| extracted_at | datetime | no | |
| text_span | str | no | Source text used as basis (for LLM/regex auditability) |

---

## State Master Record

One per state. Captures what the state's disclosure law requires, derived from PRI disclosure-law + FOCAL scoring results. This is what makes compliance monitoring possible.

### Structure

```
StateMasterRecord
├── state: "CA"
├── state_name: "California"
├── version: "2026-Q1"
├── effective_start: date  (when these requirements took effect)
├── effective_end: date | null  (null if current)
├── last_updated: date
├── legal_citations: list[str]
│
├── registration_requirements
│   ├── who_must_register: list[RegistrationRequirement]
│   │     role: "lobbyist"|"volunteer"|"principal"|"firm"|...
│   │     required: bool
│   │     pri_item_id: "A1"  (traceability to rubric)
│   │
│   ├── de_minimis_financial_threshold: float | null
│   ├── de_minimis_financial_citation: str | null
│   ├── de_minimis_time_threshold: float | null  (percentage)
│   └── de_minimis_time_citation: str | null
│
├── reporting_parties: list[ReportingPartyRequirement]
│   ├── entity_role: "lobbyist"|"client"|"firm"|"official"
│   ├── report_type: "activity_report"|"expenditure_report"|"gift_disclosure"
│   ├── filing_status: "required"|"optional"|"not_required"
│   └── reporting_frequency: "monthly"|"quarterly"|"semi_annually"|"annually"|...
│
├── field_requirements: list[FieldRequirement]
│   ├── field_path: "expenditures[].amount"
│   ├── reporting_party: "lobbyist"|"client"|"firm"
│   ├── status: "required"|"optional"|"not_applicable"|"unknown"
│   ├── legal_citation: str | null
│   ├── pri_item_id: str | null    (traceability)
│   ├── focal_indicator_id: str | null
│   └── notes: str
│
└── notes: str  (free-text for anything that doesn't fit)
```

### Compliance Check Logic

State Master Records are versioned with `effective_start` / `effective_end` dates. When checking compliance for a filing, use the version whose effective period contains the filing's `reporting_period_start`. This way, if Texas raises its de minimis threshold in 2027, filings from 2026 are still checked against the 2026 rules.

Given a `LobbyingFiling` and the `StateMasterRecord` for its state:

```python
for req in state_master.field_requirements:
    if req.reporting_party == filing.filer_role and req.status == "required":
        value = get_field(filing, req.field_path)
        if value is None:
            flag_compliance_gap(filing, req)
```

### Cross-Reporting Consistency

The `reporting_parties` list enables a powerful check: if a state requires both lobbyists and clients to file activity reports, and only the lobbyist filed, the missing client report is detectable even before examining field-level completeness.

For states where multiple parties report overlapping data (e.g., both lobbyist and client report expenditure totals), the amounts should be reconcilable. Discrepancies are a compliance signal — analogous to third-party reporting in tax enforcement.

---

## Pipeline Output Format

Each fellow's pipeline produces one JSON file per filing, validated against the pydantic models.

### Directory structure

```
data/extracted/<STATE>/
├── registrations/
│   └── <registration_id>.json    → LobbyistRegistration
├── filings/
│   └── <filing_id>.json          → LobbyingFiling
├── persons/
│   └── <person_id>.json          → Person (deduplicated within state)
├── organizations/
│   └── <org_id>.json             → Organization (deduplicated within state)
└── state_master.json             → StateMasterRecord
```

### Validation

Every JSON file must deserialize cleanly into its pydantic model. Pipelines should validate before writing:

```python
from lobby_analysis.models import LobbyingFiling

filing = LobbyingFiling(**extracted_data)
filing.model_validate(filing)  # pydantic validation
path.write_text(filing.model_dump_json(indent=2))
```

---

## What This Model Does NOT Cover (Yet)

These are explicitly deferred to later phases:

1. **Cross-state entity resolution.** The `CrossStateOrgIdentifier` that links "Pfizer Inc." across states. Separate enrichment layer, biggest open methodological question.
2. **Compliance layer entities.** `Violation`, `Referral`, `Penalty` — first-class entities in the design, but not part of the extraction pipeline output. Built from State Master Record + filing data + external enforcement records.
3. **Analytics/aggregation views.** Per-state totals, time series, network graphs. Downstream of this model.
4. **External ID linkage.** Open States, OpenCorporates, SEC CIK, LobbyView. Separate enrichment layer.

---

## Open Questions for Fellow Review

1. **Is the entity list complete?** Does any fellow's assigned state have a disclosure type not covered by these entities?
2. **Field granularity.** Are there fields that should be split finer or merged? (e.g., should `total_compensation` and `total_reimbursements` be a single `total_costs` field?)
3. **Engagement entity.** Only ~8 states require contact-level logging. Is it worth the complexity in the universal model, or should it be a state-specific extension?
4. **Gift vs. Expenditure.** Some states report gifts as a subcategory of expenditures, not separately. Should `Gift` remain a separate entity, or become an expenditure category?
5. **State Master Record population.** The scoring branch will produce PRI/FOCAL scores per state. Should we auto-generate State Master Records from those scores, or should each fellow manually verify their states' requirements?
6. **De minimis thresholds.** The PRI rubric captures whether a threshold exists and its value. Should the State Master Record also capture the *conditions* under which the threshold applies (e.g., "compensation threshold applies only to in-house lobbyists")?

---

## Rubric Traceability

Every field in this model traces back to a PRI or FOCAL rubric item. This is intentional — the rubrics were designed by researchers who surveyed the full landscape of lobbying disclosure requirements. If a state requires something not in the rubrics, we add a field and note the gap.

| Model Field | PRI Item(s) | FOCAL Indicator(s) |
|-------------|-------------|---------------------|
| Person.contact_details | E1b, E1d, E2b, E2d | 4.2 |
| Person.prior_public_offices | — | 5.1, 5.2 |
| Organization.sector | — | 4.5 |
| Organization.legal_form | — | 4.3 |
| LobbyistRegistration.lobbyist_type | A1–A4 | 1.1 |
| LobbyistRegistration.clients | — | 6.1 |
| LobbyingFiling.total_compensation | E1f_i, E2f_i | 7.6 |
| LobbyingFiling.total_reimbursements | E1f_ii, E2f_ii | — |
| LobbyingFiling.total_other_costs | E1f_iii, E2f_iii | — |
| LobbyingFiling.total_income | — | 7.1 |
| LobbyingFiling.income_per_client | — | 7.2 |
| LobbyingFiling.is_itemized | E1f_iv, E2f_iv | — |
| LobbyingPosition.bill_reference | E1g_ii, E2g_ii | 8.11 |
| LobbyingPosition.general_issue_area | E1g_i, E2g_i | 8.9 |
| LobbyingPosition.position | — | 8.10 |
| LobbyingExpenditure.amount | E1f_i–iii, E2f_i–iii | 7.6, 7.8 |
| LobbyingExpenditure.category | E1f_iii, E2f_iii | 7.9, 7.10 |
| LobbyingEngagement.* | E1i, E2i | 8.1–8.11 |
| Gift.* | E1f_iii, E2f_iii | 7.10 |
| Filing frequency | E1h_*, E2h_* | 2.1, 2.2 |
