"""Loaders for the WI 2025-2026 release.

Four entry points, each parametrized by ``(release_dir, semester)`` where
semester is a string in ``{"2025-H1", "2025-H2", "2026-H1", "2026-H2"}``:

- :func:`load_principal_totals` — per-principal (hours_comm, hours_other)
  for the named semester, read from ``WI_principal_filings.tsv``.
- :func:`load_lobbyist_totals` — per-lobbyist (hours_comm, hours_other),
  read from ``WI_lobbyist_filings.tsv``.
- :func:`load_active_edges` — the set of ``(lobbyist_id, principal_id)``
  authorizations active in the named semester, read from
  ``WI_lobbyist_principal_authorizations_unified.tsv``.
- :func:`load_bill_effort_percents` — per-principal list of
  ``(item_id, item_name, percent_float)`` bill-effort allocations, read
  from ``WI_principal_bill_efforts.tsv``.

The release TSVs are the contract — these loaders do not modify them.
``"%"`` strings parse to floats in ``[0, 1]``. Embedded newlines in
``item_description`` are handled by pandas' CSV-quoting (NEVER use
``wc -l`` on bill_efforts).

Phase 0 audit findings the loaders bake in:

- Lobbyist filings are semester-granular natively (no quarterly
  aggregation). See ``20260530_phase_0_data_audit.md`` TL;DR #1.
- 4 of 2,254 authorization rows have null ``authorized_on``. These are
  excluded from the active-edge set (cannot reason about period
  membership without an auth date).
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

__all__ = [
    "load_principal_totals",
    "load_lobbyist_totals",
    "load_active_edges",
    "load_bill_effort_percents",
]


# Semester → (period_start_iso, period_end_iso, bill_effort_label)
_SEMESTER_BOUNDS: dict[str, tuple[str, str, str]] = {
    "2025-H1": ("2025-01-01", "2025-06-30", "2025 January - June"),
    "2025-H2": ("2025-07-01", "2025-12-31", "2025 July - December"),
    "2026-H1": ("2026-01-01", "2026-06-30", "2026 January - June"),
    "2026-H2": ("2026-07-01", "2026-12-31", "2026 July - December"),
}


def _semester_bounds(semester: str) -> tuple[str, str, str]:
    try:
        return _SEMESTER_BOUNDS[semester]
    except KeyError as exc:
        raise ValueError(
            f"unknown semester {semester!r}; expected one of "
            f"{sorted(_SEMESTER_BOUNDS)}"
        ) from exc


def load_principal_totals(
    release_dir: Path, semester: str
) -> dict[int, tuple[float, float]]:
    """Per-principal (hours_communicating, hours_other) for the named
    semester."""
    period_start, _, _ = _semester_bounds(semester)
    df = pd.read_csv(
        Path(release_dir) / "WI_principal_filings.tsv",
        sep="\t",
        dtype={"principal_id": "Int64"},
    )
    rows = df[df["reporting_period_start"] == period_start]
    return {
        int(pid): (float(comm), float(other))
        for pid, comm, other in zip(
            rows["principal_id"],
            rows["total_hours_communicating"],
            rows["total_hours_other"],
        )
    }


def load_lobbyist_totals(
    release_dir: Path, semester: str
) -> dict[int, tuple[float, float]]:
    """Per-lobbyist (hours_communicating, hours_other) for the named
    semester. The WI portal zero-fills, so every registered lobbyist
    has a cell."""
    period_start, _, _ = _semester_bounds(semester)
    df = pd.read_csv(
        Path(release_dir) / "WI_lobbyist_filings.tsv",
        sep="\t",
        dtype={"lobbyist_id": "Int64"},
    )
    rows = df[df["reporting_period_start"] == period_start]
    return {
        int(lid): (float(comm), float(other))
        for lid, comm, other in zip(
            rows["lobbyist_id"],
            rows["total_hours_communicating"],
            rows["total_hours_other"],
        )
    }


def load_active_edges(release_dir: Path, semester: str) -> set[tuple[int, int]]:
    """Authorizations active in the named semester.

    Filter: ``auth_dt <= period_end AND (wd_dt null OR wd_dt >= period_start)``.
    Edges with null ``authorized_on`` (4 in this release) are excluded —
    no period-membership inference is possible without an auth date.
    """
    period_start, period_end, _ = _semester_bounds(semester)
    df = pd.read_csv(
        Path(release_dir) / "WI_lobbyist_principal_authorizations_unified.tsv",
        sep="\t",
        dtype={"lobbyist_id": "Int64", "principal_id": "Int64"},
        keep_default_na=False,
        na_values=[""],
    )
    df["auth_dt"] = pd.to_datetime(df["authorized_on"], errors="coerce")
    df["wd_dt"] = pd.to_datetime(df["withdrawn_on"], errors="coerce")
    active = df[
        df["auth_dt"].notna()
        & (df["auth_dt"] <= period_end)
        & (df["wd_dt"].isna() | (df["wd_dt"] >= period_start))
    ]
    return {
        (int(lid), int(pid))
        for lid, pid in zip(active["lobbyist_id"], active["principal_id"])
    }


def load_bill_effort_percents(
    release_dir: Path, semester: str
) -> dict[int, list[tuple[int, str, float]]]:
    """Per-principal bill-effort allocations for the named semester.

    Returns ``{principal_id: [(item_id, item_name, percent_float), ...]}``.
    Percent strings like ``"1%"`` / ``"54%"`` parse to floats in ``[0, 1]``.
    """
    _, _, label = _semester_bounds(semester)
    df = pd.read_csv(
        Path(release_dir) / "WI_principal_bill_efforts.tsv",
        sep="\t",
        dtype={"principal_id": "Int64", "item_id": "Int64"},
    )
    rows = df[df["period_label"] == label]
    out: dict[int, list[tuple[int, str, float]]] = {}
    for pid, iid, name, pct_str in zip(
        rows["principal_id"], rows["item_id"], rows["item_name"], rows["percent"]
    ):
        pct = float(str(pct_str).rstrip("%")) / 100.0
        out.setdefault(int(pid), []).append((int(iid), str(name), pct))
    return out
