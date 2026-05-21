# Noridoc: justia

Path: @/tests/fixtures/justia

### Overview
This folder contains captured Justia HTML pages used by the statute retrieval and parsing tests. It covers state indexes, year indexes, title/chapter pages, and statute leaves from several state-specific URL layouts.

### How it fits into the larger codebase

@/src/scoring/justia_client.py parses these pages to extract hosted years, title links, child statute URLs, and statute text with Justia navigation chrome removed. @/src/scoring/statute_retrieval.py uses the same parser behavior when building statute bundles from curated URLs. The tests use these fixtures to keep retrieval logic deterministic and disconnected from live Justia availability.

### Core Implementation

The HTML files preserve representative Justia structures for states such as California, Texas, New York, Wisconsin, Wyoming, and Colorado. @/tests/fixtures/justia/_capture.py uses Playwright to fetch pages and save them by fixture name, which gives maintainers a repeatable path for expanding fixture coverage when a parser needs another real-world shape. Tests can load a fixture directly or route it through a fake client that returns fixture HTML for known URLs.

### Things to Know

Justia uses different URL and page conventions across states and years, so these fixtures are part of the parser contract. Captured pages include page chrome and unrelated links by design; the parser code is responsible for selecting statute-relevant content and rejecting sign-in or navigation URLs. The capture helper is a maintenance tool, not part of the package runtime.

Created and maintained by Nori.
