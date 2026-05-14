# Noridoc: lobby_analysis

Path: @/

### Overview
This repository is a research-first codebase for modeling, scoring, and eventually operationalizing U.S. state lobbying disclosure data. The active Python implementation is split between the long-term data model in @/src/lobby_analysis and the statute/snapshot scoring harness in @/src/scoring, with @/scripts and @/tools used for reproducible artifact generation and @/tests preserving the calibration and retrieval behavior.

### How it fits into the larger codebase

The repo combines prose research artifacts and executable code. @/README.md and @/CLAUDE.md define the project framing and collaboration workflow, while @/docs/active and @/docs/historical preserve branch-level research decisions that the Python modules implement. Runtime code reads committed rubric, compendium, statute, and fixture artifacts from @/docs, @/data, @/papers, and @/tests/fixtures rather than hiding those inputs behind external services. The package configuration in @/pyproject.toml exposes both @/src/lobby_analysis and @/src/scoring as installable Python packages.

### Core Implementation

The long-term domain layer in @/src/lobby_analysis defines Pydantic schemas for filings, entities, provenance, extraction capability, compendium items, and State Master Records. The scoring layer in @/src/scoring loads frozen snapshots or statute bundles, builds subagent briefs, validates scorer outputs, stamps provenance, analyzes calibration/consistency, and exports projected State Master Records. @/scripts/build_compendium.py is an idempotent artifact builder that turns historical rubric results into the committed compendium CSVs consumed by the package code, while @/tools contains research-line utilities for assembling and analyzing compendium source material.

### Things to Know

The codebase treats raw research artifacts as part of the system boundary: CSV rubrics, snapshot manifests, Justia fixtures, and compendium outputs are source material for tests and CLI commands. State heterogeneity is handled by common models and retrieval/scoring harnesses rather than per-state application code. LLM scoring is orchestrated through generated briefs and validated JSON files, not direct SDK calls inside the Python modules.

Created and maintained by Nori.
