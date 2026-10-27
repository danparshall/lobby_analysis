"""Shared pytest fixtures for the backend test suite.

A session-scoped engine connects to the `lobby_test` postgres database
(spun up by `docker compose up -d postgres`). The `filings` table is
created once at session start and dropped at the end. Each test that
uses `engine` is isolated via a `TRUNCATE` after the test function;
tests that don't use the database don't need postgres at all. If
postgres is unreachable, the tests that need it are skipped.
"""

from __future__ import annotations

import os

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import OperationalError

from lobby_analysis.backend.storage import Base

TEST_DATABASE_URL = os.environ.get(
    "TEST_DATABASE_URL",
    "postgresql+psycopg://lobby:lobby@localhost:5432/lobby_test",
)


@pytest.fixture(scope="session")
def engine() -> Engine:
    """Skips every test that needs the database when postgres is unreachable."""
    eng = create_engine(TEST_DATABASE_URL)
    try:
        with eng.connect():
            pass
    except OperationalError as exc:
        eng.dispose()
        pytest.skip(
            f"postgres not reachable at {eng.url.render_as_string(hide_password=True)} "
            f"— run `docker compose up -d postgres` ({type(exc.orig).__name__})"
        )
    Base.metadata.create_all(eng)
    yield eng
    Base.metadata.drop_all(eng)
    eng.dispose()


@pytest.fixture(scope="session")
def db_url(engine: Engine) -> str:
    """Depends on `engine` so a test using only `db_url` still gets the
    tables created, the per-test TRUNCATE, and the unreachable-postgres skip."""
    return TEST_DATABASE_URL


@pytest.fixture(autouse=True)
def _truncate_filings(request: pytest.FixtureRequest):
    """TRUNCATE `filings` after each test that uses the database.

    Tests that never request `engine` (directly or via another fixture)
    don't touch postgres, so they neither need a connection nor pay for
    a TRUNCATE.
    """
    if "engine" not in request.fixturenames:
        yield
        return
    engine: Engine = request.getfixturevalue("engine")
    yield
    with engine.begin() as conn:
        conn.execute(text("TRUNCATE TABLE filings"))
