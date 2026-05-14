# Noridoc: src

Path: @/src

### Overview
This folder contains the installable Python packages for the project. @/src/lobby_analysis holds the domain model and compendium loading code, while @/src/scoring holds the statute and portal-snapshot scoring harness.

### How it fits into the larger codebase

The packages under this folder are the bridge between research artifacts and executable workflows. @/src/lobby_analysis supplies Pydantic contracts that describe the long-term lobbying data model, and @/src/scoring consumes historical rubrics, portal snapshots, statute bundles, and scorer outputs to produce scored CSVs and State Master Records. @/pyproject.toml maps both packages into the built distribution, including the explicit source mapping that exposes @/src/scoring as the `scoring` package.

### Core Implementation

The code in @/src is intentionally file-backed. Loaders such as @/src/lobby_analysis/compendium_loader.py, @/src/scoring/rubric_loader.py, @/src/scoring/snapshot_loader.py, and @/src/scoring/statute_loader.py validate committed artifacts and return typed objects from @/src/lobby_analysis/models and @/src/scoring/models.py. The scoring orchestrator then composes those typed objects into command-line workflows.

### Things to Know

The packages assume repo-root-relative artifact locations for many workflows, so callers typically pass or derive a repository root rather than relying on a service container. Validation errors are part of the contract: missing files, malformed JSON, rubric mismatch, or invalid Pydantic rows fail loudly instead of being silently treated as empty data.

Created and maintained by Nori.
