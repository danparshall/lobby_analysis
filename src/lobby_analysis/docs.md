# Noridoc: lobby_analysis

Path: @/src/lobby_analysis

### Overview
This package contains the stable domain layer for the lobbying disclosure project. It defines the schema vocabulary for entities, filings, state disclosure requirements, extraction capability, provenance, and compendium items.

### How it fits into the larger codebase

The models in @/src/lobby_analysis/models are the target shape that scoring and extraction workflows project toward. @/src/scoring/smr_projection.py imports these models to turn PRI disclosure-law scores into State Master Records, and @/src/lobby_analysis/compendium_loader.py loads the committed compendium artifact into typed `CompendiumItem` objects. The package is deliberately independent of the scoring orchestrator so future fetch/parse/enrich/publish stages can share the same contracts.

### Core Implementation

@/src/lobby_analysis/compendium_loader.py reads @/compendium/disclosure_items.csv, parses JSON-encoded framework references, normalizes optional fields, and validates each row as a `CompendiumItem`. The package re-exports model classes from @/src/lobby_analysis/models/__init__.py so scoring and scripts can import the domain objects from one namespace. The loader treats a missing compendium CSV as a hard error because downstream matrix and State Master Record projection depend on that artifact being present.

### Things to Know

The domain package stores both normalized values and provenance-oriented context. Many fields preserve raw source structure, source-state identifiers, or framework references because the project needs replayable research evidence, not only final cleaned values. The models use Pydantic validation as the boundary between hand-curated research artifacts and executable workflows.

Created and maintained by Nori.
