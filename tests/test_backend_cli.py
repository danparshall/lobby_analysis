"""Behavior tests for src/lobby_analysis/backend/cli.py.

Each test creates a tmp JSON sample + tmp DB and invokes `main(argv)`
in-process. Side effects observed via the storage layer or captured stdout.
"""

import json
from pathlib import Path

from lobby_analysis.backend.cli import main
from lobby_analysis.backend.storage import get_filing, init_engine
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


def test_ingest_loads_filing_into_db(tmp_path):
    json_path = tmp_path / "sample.json"
    db_path = tmp_path / "test.db"
    filing_id = _write_sample_json(json_path)

    rc = main(["--db", str(db_path), "ingest", str(json_path)])
    assert rc == 0

    engine = init_engine(str(db_path))
    retrieved = get_filing(engine, filing_id)
    assert retrieved is not None
    assert retrieved.id == filing_id


def test_get_subcommand_prints_filing_json(tmp_path, capsys):
    json_path = tmp_path / "sample.json"
    db_path = tmp_path / "test.db"
    filing_id = _write_sample_json(json_path)
    main(["--db", str(db_path), "ingest", str(json_path)])
    capsys.readouterr()  # discard ingest's stdout

    rc = main(["--db", str(db_path), "get", filing_id])
    assert rc == 0

    captured = capsys.readouterr()
    parsed = json.loads(captured.out)
    assert parsed["id"] == filing_id
    assert parsed["state"] == "OH"


def test_get_returns_nonzero_for_unknown_id(tmp_path):
    db_path = tmp_path / "test.db"
    rc = main(["--db", str(db_path), "get", "no-such-id"])
    assert rc != 0


def test_list_subcommand_shows_ingested_filings(tmp_path, capsys):
    json_path = tmp_path / "sample.json"
    db_path = tmp_path / "test.db"
    _write_sample_json(json_path)
    main(["--db", str(db_path), "ingest", str(json_path)])
    capsys.readouterr()

    rc = main(["--db", str(db_path), "list"])
    assert rc == 0

    captured = capsys.readouterr()
    assert "cli-1" in captured.out
