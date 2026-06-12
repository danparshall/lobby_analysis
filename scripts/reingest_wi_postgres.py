"""One-shot re-ingest of releases/wi/ into postgres lobby_dev for the 2026-06 swap.

Usage:
    PYTHONPATH=src .venv/bin/python scripts/reingest_wi_postgres.py
"""

from __future__ import annotations

import time
from decimal import Decimal
from pathlib import Path

from sqlalchemy import text

from lobby_analysis.backend.ingest_wi import ingest_release_dir
from lobby_analysis.backend.storage import Base, init_engine, search_filings

URL = "postgresql+psycopg://lobby:lobby@localhost:5432/lobby_dev"


def main() -> None:
    engine = init_engine(URL)

    # Wipe filings table to start clean.
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    print("Ingesting releases/wi/ ...")
    t0 = time.perf_counter()
    counts = ingest_release_dir(Path("releases/wi"), engine)
    elapsed = time.perf_counter() - t0
    print(f"counts: {counts}")
    print(f"elapsed: {elapsed:.2f}s")

    hits = search_filings(engine, "DoorDash", limit=10000)
    print(f"\nDoorDash filing hits: {len(hits)}")
    doordash_total = Decimal("0")
    for f in hits:
        if f.filer_organization is not None and f.total_expenditure is not None:
            doordash_total += Decimal(str(f.total_expenditure))
    print(f"DoorDash YTD aggregate: ${doordash_total:,.2f}")

    with engine.connect() as conn:
        total = conn.execute(text("SELECT COUNT(*) FROM filings")).scalar_one()
        by_role = conn.execute(
            text("SELECT filer_role, COUNT(*) FROM filings GROUP BY filer_role ORDER BY filer_role")
        ).all()
    print(f"\nTotal rows in filings: {total}")
    print(f"By filer_role: {by_role}")


if __name__ == "__main__":
    main()
