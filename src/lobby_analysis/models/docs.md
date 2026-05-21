# Noridoc: models

Path: @/src/lobby_analysis/models

### Overview
This folder defines the Pydantic data contracts for the lobbying analysis domain. The models cover reference entities, filings and nested filing sections, State Master Records, compendium items, extraction capability, and field-level provenance.

### How it fits into the larger codebase

These models are the shared vocabulary between research scoring and future data ingestion. @/src/scoring/smr_projection.py builds `StateMasterRecord`, `RegistrationRequirement`, `ReportingPartyRequirement`, and `FieldRequirement` instances from scored PRI rows and compendium references. @/src/lobby_analysis/compendium_loader.py builds `CompendiumItem` instances from committed CSV rows. Filing and entity models provide the field paths referenced by compendium rows and State Master Record requirements.

### Core Implementation

@/src/lobby_analysis/models/state_master.py captures what each state's law requires, including registration roles, reporting parties, field requirements, availability status, evidence source, and legal citations. @/src/lobby_analysis/models/filings.py follows a Filing -> Sections -> Transactions shape: `LobbyistRegistration` establishes registration, while `LobbyingFiling` contains nested positions, expenditures, engagements, and gifts. @/src/lobby_analysis/models/entities.py follows a Popolo-style person and organization structure and adds bill references plus organization relationships. @/src/lobby_analysis/models/compendium.py ties external rubric items to universal compendium items and matrix cells.

### Things to Know

Dot-paths in `FieldRequirement.field_path` intentionally point into `LobbyingFiling` or registration-related structures, so scoring outputs can be projected into concrete schema expectations. Literal types encode controlled vocabularies for statuses, roles, domains, availability tiers, and framework IDs. The models preserve framework references and provenance directly on the data objects so downstream exports can explain where each requirement or value came from.

Created and maintained by Nori.
