# Research Log: lobbying-data-model

**Created:** 2026-04-17
**Closed:** 2026-04-21 (v1.0 accepted, branch archived)
**Purpose:** Design the normalized data model for US state lobbying disclosure records — the schema that holds registrations, expenditures, client relationships, bill positions, gifts, and other disclosure fields once extracted from heterogeneous state portals.

---

## Trajectory

Newest first.

- **2026-04-21 — v1.0 accepted.** The v0.1 draft (2026-04-17) was circulated as the proposed schema contract for per-state extraction pipelines. No objections or change requests surfaced during the 4-day review window. Declared v1.0 and archived. 18 pydantic models across 4 modules (entities, filings, provenance, state_master); 24-test validation suite under `tests/test_models.py`. Future changes go through a new branch with a migration plan, not silent edits.

- **2026-04-17 — v0.1 draft shipped.** Designed the universal output schema for the lobby_analysis project: `Person`, `Organization`, `OrganizationRelationship`, `ContactDetail`, `Identifier`, `BillReference`, `PriorOffice` (reference entities); `LobbyistRegistration`, `LobbyingFiling`, `LobbyingPosition`, `LobbyingExpenditure`, `LobbyingEngagement`, `Gift` (filing entities); `Provenance`, `StateMasterRecord` + requirement models (meta). Design principles locked: store source faithfully + normalize later; union schema with nullable fields (`null` ≠ "not required"); hierarchies preserved where they exist naturally; field-level provenance on LLM/regex extractions; amendment chain via `supersedes` links instead of overwrites; `StateMasterRecord` distinguishes "state doesn't require this field" from "filer failed to report a required field." Spec doc at `results/lobbying_data_model_spec.md`.

## Results

- 2026-04-17 / 2026-04-21 — `results/lobbying_data_model_spec.md` — v1.0 spec (accepted). Entity diagrams, field-by-field schema, design principles, integration notes for state extraction pipelines.
