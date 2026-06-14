"""Local conftest for OH allocation tests.

The repo's top-level ``tests/conftest.py`` defines an autouse fixture
``_truncate_filings`` that requires a running Postgres (the backend test
suite's per-test isolation step). The OH allocation classifier is
pure-logic — no DB, no I/O — so we override that fixture to a no-op here,
letting these tests run in any environment with the source tree available.

If a future OH allocation test does need the DB (e.g., an end-to-end
materialize test reading a real Postgres-backed filings table), put it
in a separate subdirectory or remove this override.
"""

from __future__ import annotations

import pytest


@pytest.fixture(autouse=True)
def _truncate_filings():
    """No-op override; OH classifier tests don't touch Postgres."""
    yield
