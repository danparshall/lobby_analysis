# Noridoc: fixtures

Path: @/tests/fixtures

### Overview
This folder holds local test fixtures used to exercise parsing and retrieval without live external requests. The fixture tree currently focuses on Justia statute pages and index pages.

### How it fits into the larger codebase

Fixtures under this folder provide stable inputs for @/tests and stand in for external web pages consumed by @/src/scoring/justia_client.py and @/src/scoring/statute_retrieval.py. Keeping captured HTML in version control lets parser behavior evolve against known page structures from multiple states and URL conventions.

### Core Implementation

The fixture files are read directly by tests or by fake client implementations that satisfy the `Client` protocol in @/src/scoring/justia_client.py. Parent folders provide grouping context, while leaf fixture files preserve the raw HTML surface that parser functions operate on. The capture helper under @/tests/fixtures/justia can refresh or add pages when parser coverage needs to reflect a new Justia layout.

### Things to Know

Fixtures are intentionally raw enough to catch parser assumptions about navigation chrome, URL namespaces, title indexes, and statute-leaf text extraction. They should not be over-normalized into minimal snippets unless a test is specifically narrowing behavior, because the parser code needs realistic page noise to stay honest.

Created and maintained by Nori.
