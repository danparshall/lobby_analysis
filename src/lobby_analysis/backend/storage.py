"""SQLite-backed storage for LobbyingFiling records.

Single table `filings` holds the full pydantic-serialized JSON in a `payload`
column plus a handful of denormalized columns for index-backed filtering and
LIKE-based filer-name search. The serialized JSON is the source of truth;
the indexed columns are derived at insert time and exist only to make
queries fast at SQLite scale.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import DateTime, String, Text, create_engine, select
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column
from sqlalchemy.pool import StaticPool

from lobby_analysis.models.filings import LobbyingFiling


class Base(DeclarativeBase):
    pass


class FilingRow(Base):
    __tablename__ = "filings"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    state: Mapped[str] = mapped_column(String, nullable=False, index=True)
    filing_id: Mapped[str | None] = mapped_column(String, nullable=True)
    filing_type: Mapped[str] = mapped_column(String, nullable=False)
    filer_role: Mapped[str] = mapped_column(String, nullable=False, index=True)
    filer_name: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    filed_date: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    payload: Mapped[str] = mapped_column(Text, nullable=False)
    ingested_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)


def init_engine(db_path: str = ":memory:") -> Engine:
    """Create a SQLite engine and ensure the schema exists.

    `db_path=":memory:"` (default) uses an in-memory database — convenient for
    tests. For a file-backed DB pass an absolute or relative path; the parent
    directory is created if missing.
    """
    if db_path == ":memory:":
        # StaticPool + check_same_thread=False makes all connections share one
        # in-memory DB — without it, a new SQLAlchemy connection gets its own
        # empty DB, which breaks tests where the API endpoint runs on a
        # different connection than the one that created the schema.
        engine = create_engine(
            "sqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
            echo=False,
        )
    else:
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        engine = create_engine(f"sqlite:///{db_path}", echo=False)
    Base.metadata.create_all(engine)
    return engine


def _filer_name(filing: LobbyingFiling) -> str | None:
    if filing.filer_person is not None:
        return filing.filer_person.name
    if filing.filer_organization is not None:
        return filing.filer_organization.name
    return None


def insert_filing(engine: Engine, filing: LobbyingFiling) -> str:
    """Persist one filing; returns its id."""
    row = FilingRow(
        id=filing.id,
        state=filing.state,
        filing_id=filing.filing_id,
        filing_type=filing.filing_type,
        filer_role=filing.filer_role,
        filer_name=_filer_name(filing),
        filed_date=filing.filed_date.isoformat() if filing.filed_date else None,
        payload=filing.model_dump_json(),
        ingested_at=datetime.now(timezone.utc),
    )
    with Session(engine) as session:
        session.add(row)
        session.commit()
    return filing.id


def get_filing(engine: Engine, id: str) -> LobbyingFiling | None:
    """Fetch one filing by id, or None if no such id exists."""
    with Session(engine) as session:
        row = session.get(FilingRow, id)
        if row is None:
            return None
        return LobbyingFiling.model_validate_json(row.payload)


def list_filings(
    engine: Engine,
    state: str | None = None,
    filer_role: str | None = None,
    limit: int = 100,
) -> list[LobbyingFiling]:
    """List filings, optionally filtered by state and/or filer_role.

    Ordered by ingested_at descending so newest-first is the default view.
    """
    stmt = select(FilingRow)
    if state is not None:
        stmt = stmt.where(FilingRow.state == state)
    if filer_role is not None:
        stmt = stmt.where(FilingRow.filer_role == filer_role)
    stmt = stmt.order_by(FilingRow.ingested_at.desc()).limit(limit)
    with Session(engine) as session:
        rows = session.scalars(stmt).all()
        return [LobbyingFiling.model_validate_json(r.payload) for r in rows]


def search_filings(engine: Engine, q: str, limit: int = 100) -> list[LobbyingFiling]:
    """Search filings by filer_name (case-insensitive substring match)."""
    stmt = (
        select(FilingRow)
        .where(FilingRow.filer_name.ilike(f"%{q}%"))
        .order_by(FilingRow.ingested_at.desc())
        .limit(limit)
    )
    with Session(engine) as session:
        rows = session.scalars(stmt).all()
        return [LobbyingFiling.model_validate_json(r.payload) for r in rows]
