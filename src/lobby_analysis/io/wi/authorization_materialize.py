"""Materialize the lobbyist↔principal authorization join table from
the on-disk checkpoint files.

Decoupled from the fetcher so a parser fix triggers re-materialization,
not re-scraping. The checkpoints store full page HTML; the parser
runs at materialize-time.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Iterable, Iterator

from lobby_analysis.io.wi.authorization_parser import (
    Authorization,
    parse_lobbyist_authorizations,
)

TSV_FIELDNAMES = ["lobbyist_id", "principal_id", "authorized_on", "withdrawn_on"]


def iter_authorizations_from_checkpoints(
    checkpoint_dir: Path,
) -> Iterator[Authorization]:
    """Yield every ``Authorization`` parsed out of every ``{id}.json``
    checkpoint in ``checkpoint_dir`` (sorted by lobbyist_id for
    deterministic output)."""
    checkpoint_dir = Path(checkpoint_dir)
    if not checkpoint_dir.exists():
        return

    checkpoint_files = sorted(
        checkpoint_dir.glob("*.json"),
        key=lambda p: int(p.stem) if p.stem.isdigit() else 10**9,
    )
    for path in checkpoint_files:
        if not path.stem.isdigit():
            continue
        with path.open("r", encoding="utf-8") as fh:
            payload = json.load(fh)
        html = payload.get("html")
        if html is None:
            continue
        lobbyist_id = int(payload["lobbyist_id"])
        yield from parse_lobbyist_authorizations(html, lobbyist_id=lobbyist_id)


def write_authorizations_tsv(
    rows: Iterable[Authorization], output_path: Path
) -> int:
    """Write ``rows`` to ``output_path`` as a tab-separated table with
    ISO-format dates (``YYYY-MM-DD``) and blank ``withdrawn_on`` when
    ``None``. Returns the number of data rows written.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with output_path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=TSV_FIELDNAMES, delimiter="\t")
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    "lobbyist_id": row.lobbyist_id,
                    "principal_id": row.principal_id,
                    "authorized_on": row.authorized_on.isoformat(),
                    "withdrawn_on": row.withdrawn_on.isoformat() if row.withdrawn_on else "",
                }
            )
            count += 1
    return count
