"""Postgres-backed storage for LobbyingFiling records.

Single table `filings` holds the full pydantic-serialized JSON in a `payload`
column plus a handful of denormalized columns for index-backed filtering and
ILIKE-based filer-name search. The serialized JSON is the source of truth;
the indexed columns are derived at insert time and exist only to make
queries fast.
"""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import DateTime, Numeric, String, Text, cast, create_engine, func, select
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

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


def init_engine(url: str) -> Engine:
    """Create a postgres engine and ensure the schema exists.

    `url` is a SQLAlchemy URL like
    `postgresql+psycopg://lobby:lobby@localhost:5432/lobby_dev`.
    """
    engine = create_engine(url)
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


def _apply_filters(stmt, state: str | None, filer_role: str | None):
    if state is not None:
        stmt = stmt.where(FilingRow.state == state)
    if filer_role is not None:
        stmt = stmt.where(FilingRow.filer_role == filer_role)
    return stmt


def count_filings(
    engine: Engine,
    state: str | None = None,
    filer_role: str | None = None,
) -> int:
    """Count filings matching the optional state / filer_role filters."""
    stmt = _apply_filters(select(func.count()).select_from(FilingRow), state, filer_role)
    with Session(engine) as session:
        return session.scalar(stmt) or 0


def list_filings(
    engine: Engine,
    state: str | None = None,
    filer_role: str | None = None,
    limit: int = 100,
    offset: int = 0,
) -> list[LobbyingFiling]:
    """List filings, optionally filtered by state and/or filer_role.

    Ordered by ingested_at descending so newest-first is the default view.
    `offset` supports pagination alongside `limit`.
    """
    stmt = _apply_filters(select(FilingRow), state, filer_role)
    stmt = stmt.order_by(FilingRow.ingested_at.desc()).limit(limit).offset(offset)
    with Session(engine) as session:
        rows = session.scalars(stmt).all()
        return [LobbyingFiling.model_validate_json(r.payload) for r in rows]


def search_filings(
    engine: Engine, q: str, limit: int = 100, offset: int = 0
) -> list[LobbyingFiling]:
    """Search filings by filer_name (case-insensitive substring match)."""
    stmt = (
        select(FilingRow)
        .where(FilingRow.filer_name.ilike(f"%{q}%"))
        .order_by(FilingRow.ingested_at.desc())
        .limit(limit)
        .offset(offset)
    )
    with Session(engine) as session:
        rows = session.scalars(stmt).all()
        return [LobbyingFiling.model_validate_json(r.payload) for r in rows]


# Numeric value of payload->>'total_expenditure', for SQL-side aggregation.
_TOTAL_EXPENDITURE = cast(
    cast(FilingRow.payload, JSONB)["total_expenditure"].astext, Numeric
)


def stats(engine: Engine, top_n: int = 10) -> dict:
    """Aggregate dashboard stats: totals, breakdowns, and top spenders.

    Returns a dict with `total`, `by_state`, `by_filer_role`, and
    `top_spenders` (filers ranked by summed total_expenditure).
    """
    with Session(engine) as session:
        total = session.scalar(select(func.count()).select_from(FilingRow)) or 0
        by_state = dict(
            session.execute(
                select(FilingRow.state, func.count()).group_by(FilingRow.state)
            ).all()
        )
        by_filer_role = dict(
            session.execute(
                select(FilingRow.filer_role, func.count()).group_by(FilingRow.filer_role)
            ).all()
        )
        spend = func.sum(_TOTAL_EXPENDITURE).label("spend")
        spender_rows = session.execute(
            select(FilingRow.filer_name, spend)
            .where(FilingRow.filer_name.isnot(None))
            .group_by(FilingRow.filer_name)
            .having(spend > 0)
            .order_by(spend.desc())
            .limit(top_n)
        ).all()
        top_spenders = [
            {"name": name, "total_expenditure": float(amount)}
            for name, amount in spender_rows
        ]
    return {
        "total": total,
        "by_state": by_state,
        "by_filer_role": by_filer_role,
        "top_spenders": top_spenders,
    }
