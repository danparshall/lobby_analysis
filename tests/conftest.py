"""Shared pytest fixtures for the backend test suite.

A session-scoped engine connects to the `lobby_test` postgres database
(spun up by `docker compose up -d postgres`). The `filings` table is
created once at session start and dropped at the end. Each test is
isolated via an autouse `TRUNCATE` after every test function.
"""

from __future__ import annotations

import os

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from lobby_analysis.backend.storage import Base

TEST_DATABASE_URL = os.environ.get(
    "TEST_DATABASE_URL",
    "postgresql+psycopg://lobby:lobby@localhost:5432/lobby_test",
)


@pytest.fixture(scope="session")
def engine() -> Engine:
    eng = create_engine(TEST_DATABASE_URL)
    Base.metadata.create_all(eng)
    yield eng
    Base.metadata.drop_all(eng)
    eng.dispose()


@pytest.fixture(scope="session")
def db_url() -> str:
    return TEST_DATABASE_URL


@pytest.fixture(autouse=True)
def _truncate_filings(engine: Engine):
    yield
    with engine.begin() as conn:
        conn.execute(text("TRUNCATE TABLE filings"))
