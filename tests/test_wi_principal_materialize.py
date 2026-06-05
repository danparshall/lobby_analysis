"""Behavior tests for materializing the principal-side authorization
table from on-disk checkpoint files.

Mirror of ``test_wi_authorization_materialize`` for the principal
side. Checkpoint shape is the same except for the ID field name
(``principal_id`` instead of ``lobbyist_id``).

The materialize layer re-parses HTML at materialize-time (rather
than parsing eagerly during the scrape) so a parser fix doesn't
require re-scraping — just re-materialize.
"""

from __future__ import annotations

import csv
import json
from datetime import date
from pathlib import Path

from lobby_analysis.io.wi.authorization_parser import Authorization
from lobby_analysis.io.wi.principal_materialize import (
    iter_authorizations_from_principal_checkpoints,
    write_authorizations_tsv,  # re-exported from authorization_materialize
)

WCTA_FIXTURE = Path(__file__).parent / "fixtures" / "wi" / "principal_12997.html"
LEXIA_FIXTURE = Path(__file__).parent / "fixtures" / "wi" / "principal_11348.html"


def _write_checkpoint(
    checkpoint_dir: Path, principal_id: int, html: str | None, status: int
) -> None:
    (checkpoint_dir / f"{principal_id}.json").write_text(
        json.dumps(
            {
                "principal_id": principal_id,
                "html": html,
                "fetched_at": "2026-05-26T00:00:00Z",
                "status_code": status,
            }
        ),
        encoding="utf-8",
    )


def test_iterates_authorizations_from_a_real_principal_checkpoint(
    tmp_path: Path,
):
    """A checkpoint holding WCTA's real HTML (principal 12997) must
    produce its one known authorization — lobbyist 12694 (Schlaak),
    authorized 1/8/2026, no withdrawal. This is the load-bearing case
    for the Schlaak-class enumeration."""
    _write_checkpoint(
        tmp_path,
        principal_id=12997,
        html=WCTA_FIXTURE.read_text(encoding="utf-8"),
        status=200,
    )

    rows = list(iter_authorizations_from_principal_checkpoints(tmp_path))

    assert rows == [
        Authorization(
            lobbyist_id=12694,
            principal_id=12997,
            authorized_on=date(2026, 1, 8),
            withdrawn_on=None,
        )
    ]


def test_skips_404_principal_checkpoints_silently(tmp_path: Path):
    """``html: null`` (404 / soft-404) checkpoints emit nothing — a
    principal page that doesn't resolve can't contribute any
    authorizations."""
    _write_checkpoint(tmp_path, principal_id=99999, html=None, status=404)
    _write_checkpoint(
        tmp_path,
        principal_id=12997,
        html=WCTA_FIXTURE.read_text(encoding="utf-8"),
        status=200,
    )

    rows = list(iter_authorizations_from_principal_checkpoints(tmp_path))

    assert len(rows) == 1  # only WCTA's; 99999 contributes 0
    assert rows[0].principal_id == 12997


def test_iterates_multi_principal_directory(tmp_path: Path):
    """Two principal checkpoints (WCTA + Lexia) must produce 1 + 4 = 5
    total authorizations, with the principal_id correctly stamped on
    each row from its own checkpoint (not cross-contaminated)."""
    _write_checkpoint(
        tmp_path,
        principal_id=12997,
        html=WCTA_FIXTURE.read_text(encoding="utf-8"),
        status=200,
    )
    _write_checkpoint(
        tmp_path,
        principal_id=11348,
        html=LEXIA_FIXTURE.read_text(encoding="utf-8"),
        status=200,
    )

    rows = list(iter_authorizations_from_principal_checkpoints(tmp_path))

    assert len(rows) == 5
    by_principal = {p: [r for r in rows if r.principal_id == p] for p in {12997, 11348}}
    assert len(by_principal[12997]) == 1
    assert len(by_principal[11348]) == 4
    # Schlaak is in WCTA's rows, not in Lexia's
    assert 12694 in {r.lobbyist_id for r in by_principal[12997]}
    assert 12694 not in {r.lobbyist_id for r in by_principal[11348]}


def test_iter_handles_empty_principal_checkpoint_dir(tmp_path: Path):
    assert list(iter_authorizations_from_principal_checkpoints(tmp_path)) == []


def test_write_principal_tsv_uses_same_schema_as_lobbyist_side(tmp_path: Path):
    """The principal-side TSV has the same 4-column schema as the
    lobbyist-side TSV (lobbyist_id, principal_id, authorized_on,
    withdrawn_on) because they're tables of the same bipartite edges
    — only the discovery path differs. Unification compares row-by-row
    across both, so the schemas must match exactly.

    Verifies via re-export: write a principal-side row, re-read with
    csv.DictReader, confirm the field names are identical to the
    lobbyist side's."""
    rows = [
        Authorization(12694, 12997, date(2026, 1, 8), None),
    ]
    out = tmp_path / "principal_side.tsv"

    n = write_authorizations_tsv(rows, out)

    assert n == 1
    with out.open("r", encoding="utf-8") as fh:
        reader = csv.DictReader(fh, delimiter="\t")
        assert reader.fieldnames == [
            "lobbyist_id", "principal_id", "authorized_on", "withdrawn_on",
        ]
        data = list(reader)
    assert data[0]["lobbyist_id"] == "12694"
    assert data[0]["principal_id"] == "12997"
    assert data[0]["authorized_on"] == "2026-01-08"
    assert data[0]["withdrawn_on"] == ""
