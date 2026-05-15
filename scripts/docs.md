# Noridoc: scripts

Path: @/scripts

### Overview
This folder contains repo-level executable maintenance scripts that generate committed research artifacts. The current implementation builds the disclosure compendium and framework deduplication map from historical rubric data.

### How it fits into the larger codebase

@/scripts/build_compendium.py is the source of truth for the curation judgments that produce @/compendium/disclosure_items.csv and @/compendium/framework_dedup_map.csv. @/src/lobby_analysis/compendium_loader.py loads the generated compendium CSV into typed domain objects, and @/src/scoring/smr_projection.py uses those objects when projecting scored PRI rows into State Master Records. The script's inputs live in @/docs/historical and @/papers, keeping research provenance visible in version control.

### Core Implementation

The script defines in-memory compendium rows, indexes framework references, reads PRI accessibility, PRI disclosure-law, FOCAL, and Sunlight source artifacts, applies curated mapping judgments, and writes deterministic CSV outputs. Its helper functions convert source-specific data types and observable-status rules into the normalized compendium schema. The output step is idempotent so reviewers can diff both the mapping code and the regenerated artifacts.

### Things to Know

Curation choices are encoded directly in Python structures instead of a separate hidden spreadsheet. The generated CSVs are committed artifacts, so a correct update generally changes both @/scripts/build_compendium.py and files under @/compendium. The script is not a general ETL framework; it captures the current research synthesis for disclosure-item unification.

Created and maintained by Nori.
