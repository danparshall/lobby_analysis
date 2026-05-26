"""Behavior tests for materializing the lobbyist↔principal join table
from the on-disk checkpoint files.

Checkpoint shape (written by ``authorization_fetcher.fetch_or_load``)::

    {
      "lobbyist_id": 11042,
      "html": "<html>...</html>"  | null,
      "fetched_at": "...",
      "status_code": 200 | 404
    }

The materialize layer re-parses the HTML in each checkpoint via
``authorization_parser.parse_lobbyist_authorizations``. Storing raw
HTML in the checkpoint (rather than pre-parsed records) means a
parser fix doesn't require re-scraping — we just re-materialize.
"""

from __future__ import annotations

import csv
import json
from datetime import date
from pathlib import Path

from lobby_analysis.io.wi.authorization_materialize import (
    iter_authorizations_from_checkpoints,
    write_authorizations_tsv,
)
from lobby_analysis.io.wi.authorization_parser import Authorization

REAL_FIXTURE_PATH = Path(__file__).parent / "fixtures" / "wi" / "lobbyist_11042.html"


def _write_checkpoint(
    checkpoint_dir: Path, lobbyist_id: int, html: str | None, status: int
) -> None:
    (checkpoint_dir / f"{lobbyist_id}.json").write_text(
        json.dumps(
            {
                "lobbyist_id": lobbyist_id,
                "html": html,
                "fetched_at": "2026-05-26T00:00:00Z",
                "status_code": status,
            }
        ),
        encoding="utf-8",
    )


def test_iterates_authorizations_from_a_real_checkpoint(tmp_path: Path):
    """A checkpoint holding lobbyist 11042's real HTML must produce its 9
    known authorizations when fed through the materializer."""
    _write_checkpoint(
        tmp_path,
        lobbyist_id=11042,
        html=REAL_FIXTURE_PATH.read_text(encoding="utf-8"),
        status=200,
    )

    rows = list(iter_authorizations_from_checkpoints(tmp_path))

    assert len(rows) == 9
    assert {row.principal_id for row in rows} == {
        10937, 11004, 11102, 11110, 11158, 11300, 11590, 11678, 13214,
    }
    assert {row.lobbyist_id for row in rows} == {11042}


def test_skips_404_checkpoints_silently(tmp_path: Path):
    """``html: null`` (404) checkpoints emit nothing — a lobbyist with no
    detail page can't contribute any authorizations."""
    _write_checkpoint(tmp_path, lobbyist_id=99999, html=None, status=404)
    _write_checkpoint(
        tmp_path,
        lobbyist_id=11042,
        html=REAL_FIXTURE_PATH.read_text(encoding="utf-8"),
        status=200,
    )

    rows = list(iter_authorizations_from_checkpoints(tmp_path))

    assert len(rows) == 9  # only 11042's; 99999 contributes 0


def test_write_tsv_roundtrip(tmp_path: Path):
    """The written TSV has a header + one data row per authorization, and
    re-reading it via the stdlib ``csv`` module yields the original
    values (dates as ``M/D/YYYY``-or-iso strings, withdrawn_on blank when
    None)."""
    rows = [
        Authorization(11042, 11158, date(2024, 12, 17), None),
        Authorization(11042, 13214, date(2026, 2, 17), None),
        Authorization(11042, 11590, date(2025, 1, 3), date(2025, 6, 30)),
    ]
    out = tmp_path / "join.tsv"

    n = write_authorizations_tsv(rows, out)

    assert n == 3
    assert out.exists()
    with out.open("r", encoding="utf-8") as fh:
        reader = csv.DictReader(fh, delimiter="\t")
        data = list(reader)
    assert [r["lobbyist_id"] for r in data] == ["11042", "11042", "11042"]
    assert [r["principal_id"] for r in data] == ["11158", "13214", "11590"]
    assert data[0]["authorized_on"] == "2024-12-17"
    assert data[0]["withdrawn_on"] == ""
    assert data[2]["withdrawn_on"] == "2025-06-30"


def test_iter_handles_empty_checkpoint_dir(tmp_path: Path):
    assert list(iter_authorizations_from_checkpoints(tmp_path)) == []


def test_write_tsv_handles_none_authorized_on(tmp_path: Path):
    """A small fraction of live-portal rows show Authorized On = N/A
    (pending or data-entry artifacts), so ``authorized_on`` can be
    None on a real Authorization. The TSV writer must produce a blank
    cell for these — not raise, not write "None"."""
    rows = [
        Authorization(11112, 11415, None, None),
        Authorization(12666, 12818, None, date(2025, 7, 31)),
    ]
    out = tmp_path / "join.tsv"

    n = write_authorizations_tsv(rows, out)

    assert n == 2
    with out.open("r", encoding="utf-8") as fh:
        reader = csv.DictReader(fh, delimiter="\t")
        data = list(reader)
    assert data[0]["authorized_on"] == ""
    assert data[0]["withdrawn_on"] == ""
    assert data[1]["authorized_on"] == ""
    assert data[1]["withdrawn_on"] == "2025-07-31"
