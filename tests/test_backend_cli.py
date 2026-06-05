"""Behavior tests for src/lobby_analysis/backend/cli.py.

The CLI reads `DATABASE_URL` (or `--db-url`) for the connection URL; tests
pass the `lobby_test` URL via `--db-url` explicitly so they don't depend on
environment leakage from the host shell.
"""

import json
from pathlib import Path

from lobby_analysis.backend.cli import main
from lobby_analysis.backend.storage import get_filing
from lobby_analysis.models.entities import Person
from lobby_analysis.models.filings import LobbyingFiling


def _write_sample_json(path: Path, id: str = "cli-1") -> str:
    filing = LobbyingFiling(
        id=id,
        state="OH",
        filing_type="activity_report",
        filer_role="lobbyist",
        filer_person=Person(id=f"p-{id}", name="Nathan Aichele", source_state="OH"),
    )
    path.write_text(filing.model_dump_json())
    return filing.id


def test_ingest_loads_filing_into_db(tmp_path, engine, db_url):
    json_path = tmp_path / "sample.json"
    filing_id = _write_sample_json(json_path)

    rc = main(["--db-url", db_url, "ingest", str(json_path)])
    assert rc == 0

    retrieved = get_filing(engine, filing_id)
    assert retrieved is not None
    assert retrieved.id == filing_id


def test_get_subcommand_prints_filing_json(tmp_path, engine, db_url, capsys):
    json_path = tmp_path / "sample.json"
    filing_id = _write_sample_json(json_path)
    main(["--db-url", db_url, "ingest", str(json_path)])
    capsys.readouterr()  # discard ingest's stdout

    rc = main(["--db-url", db_url, "get", filing_id])
    assert rc == 0

    captured = capsys.readouterr()
    parsed = json.loads(captured.out)
    assert parsed["id"] == filing_id
    assert parsed["state"] == "OH"


def test_get_returns_nonzero_for_unknown_id(engine, db_url):
    rc = main(["--db-url", db_url, "get", "no-such-id"])
    assert rc != 0


def test_list_subcommand_shows_ingested_filings(tmp_path, engine, db_url, capsys):
    json_path = tmp_path / "sample.json"
    _write_sample_json(json_path)
    main(["--db-url", db_url, "ingest", str(json_path)])
    capsys.readouterr()

    rc = main(["--db-url", db_url, "list"])
    assert rc == 0

    captured = capsys.readouterr()
    assert "cli-1" in captured.out
