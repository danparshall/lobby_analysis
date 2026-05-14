# Noridoc: scoring

Path: @/src/scoring

### Overview
This package implements the scoring harness for portal snapshots and statute bundles. It loads rubrics and evidence corpora, prepares subagent briefs, validates scored JSON, stamps provenance, writes CSV outputs, retrieves Justia statute text, and analyzes calibration consistency.

### How it fits into the larger codebase

@/src/scoring/orchestrator.py is the command-line entry point that ties together the package's loaders, models, prompt bundling, output validation, calibration, consistency, retrieval, and State Master Record projection. The package reads locked research artifacts from @/docs/historical, snapshot and statute artifacts from @/data, and domain models from @/src/lobby_analysis/models. Tests in @/tests exercise the package against committed fixtures and historical calibration outputs.

### Core Implementation

The core flow is prepare/finalize. Prepare commands load a rubric with @/src/scoring/rubric_loader.py, load a portal snapshot or statute bundle with @/src/scoring/snapshot_loader.py or @/src/scoring/statute_loader.py, and use @/src/scoring/bundle.py to write a self-contained subagent brief plus expected raw-output path. Finalize commands read the raw JSON, validate it with @/src/scoring/output_writer.py and @/src/scoring/models.py, stamp run metadata with @/src/scoring/provenance.py, and write scored CSVs. Retrieval commands use @/src/scoring/justia_client.py, @/src/scoring/statute_retrieval.py, and @/src/scoring/lobbying_statute_urls.py to materialize statute bundles before scoring.

### Things to Know

The package assumes LLM scoring happens outside Python through subagent briefs; Python owns determinism, artifact paths, validation, and provenance. Rubric row order is load-bearing because @/src/scoring/output_writer.py rejects scored JSON that does not match the loaded rubric item order. Snapshot artifacts marked as suspicious challenge stubs are carried into briefs so scorers do not treat WAF pages as evidence of absence.

Created and maintained by Nori.
