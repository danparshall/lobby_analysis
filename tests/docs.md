# Noridoc: tests

Path: @/tests

### Overview
This folder contains the pytest suite for the domain models, compendium loader, scoring harness, Justia parsers, statute retrieval, calibration, consistency analysis, orchestrator commands, and State Master Record projection. The tests use local fixtures and temporary directories to exercise real file-backed behavior.

### How it fits into the larger codebase

The tests protect the interfaces used by @/src/lobby_analysis and @/src/scoring. They validate that committed rubric, compendium, snapshot, and statute conventions can be loaded and transformed without relying on live network calls. Fixture HTML under @/tests/fixtures/justia mirrors the shapes that @/src/scoring/justia_client.py and @/src/scoring/statute_retrieval.py parse.

### Core Implementation

The suite is organized around behavior rather than implementation-only units. Orchestrator tests prepare and finalize runs, retrieval tests build statute bundles from fake clients and fixture HTML, calibration tests check rollups and agreement rendering, and model tests assert Pydantic validation for the lobbying data contracts. Several tests write to pytest-managed temporary paths to verify output files and manifests without mutating committed data artifacts.

### Things to Know

Many tests depend on exact artifact schemas and item ordering because the production workflows are file-backed and order-sensitive. Network behavior is represented through fake clients and captured Justia pages, leaving live Playwright fetching outside normal test execution. The package configuration in @/pyproject.toml points pytest at this folder as the default test root.

Created and maintained by Nori.
