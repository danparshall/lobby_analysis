"""Discover the universe of principal IDs to scrape for the
2025-2026 WI legislative session.

The principal universe is the **union** of two sources:

* ``WI_directory_principals.xls`` — the Ethics Commission's official
  roster (~904 entries; empirically filters on ``cessation_date IS
  NULL`` per the 2026-05-26 gap investigation).
* The auth-graph TSV produced by the lobbyist-side scrape — 942
  distinct principal IDs reached via the lobbyist→principal back-link
  on each lobbyist's "Principals Represented" page.

Their union is 944 IDs: 902 intersection, 40 auth-only (ceased
principals filtered out of the directory or privacy-redacted
low-spend-pledge entities), 2 dir-only (downstream consequences of
the Schlaak case + the soft-404 from the lobbyist-side scrape).

We deliberately do NOT enumerate the 10000-13500 range as a third
source — that's ~3500 extra polite requests and a one-hour wall
that the plan flags as out of scope.

The directory ``.xls`` has FIVE pre-data rows (not three as the
kickoff convo recorded): a title row, the session row, a "Printed
{date}" row, a blank row, then the column headers at index 4.
``header=4`` puts pandas in the right place. The Principal ID
column comes back as float64 because the file has trailing-NaN
columns; we ``dropna()`` then cast to int.
"""

from __future__ import annotations

import csv
from pathlib import Path

import pandas as pd


def _ids_from_xls(xls_path: Path) -> set[int]:
    """Read the directory ``.xls`` and return the set of distinct
    Principal ID integers.

    Drops NaN (trailing blank rows) and casts to int. Pandas reads the
    column as float64 when any NaN is present in the column.
    """
    df = pd.read_excel(xls_path, header=4)
    column = df["Principal ID"].dropna()
    return {int(v) for v in column}


def _ids_from_tsv(tsv_path: Path) -> set[int]:
    """Read the lobbyist-side auth-graph TSV and return the set of
    distinct ``principal_id`` integers.

    One principal can appear in many rows (one per authorizing
    lobbyist); this deduplicates.
    """
    with Path(tsv_path).open("r", encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh, delimiter="\t")
        return {int(row["principal_id"]) for row in reader}


def discover_principal_ids(
    directory_xls_path: Path,
    auth_graph_tsv_path: Path,
) -> set[int]:
    """Union of the directory ``.xls`` principal IDs and the existing
    auth-graph TSV principal IDs.

    Returns a set of ints; the caller is responsible for ordering
    (the scrape loop sorts ascending for deterministic checkpoint
    filenames).
    """
    xls_ids = _ids_from_xls(directory_xls_path)
    tsv_ids = _ids_from_tsv(auth_graph_tsv_path)
    return xls_ids | tsv_ids
