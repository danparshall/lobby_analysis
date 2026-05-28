"""Backend CLI: python -m lobby_analysis.backend <subcommand>.

Subcommands:
    ingest <json>           Load one LobbyingFiling JSON file into the DB.
    get <id>                Print one filing as indented JSON.
    list [--state OH] [--filer-role lobbyist]
                            Print one TSV line per filing in the DB.

All subcommands take `--db <path>` (default: data/backend/prototype.db).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from lobby_analysis.backend.storage import (
    get_filing,
    init_engine,
    insert_filing,
    list_filings,
)
from lobby_analysis.models.filings import LobbyingFiling

DEFAULT_DB = "data/backend/prototype.db"


def _cmd_ingest(engine, args) -> int:
    payload = Path(args.path).read_text()
    filing = LobbyingFiling.model_validate_json(payload)
    insert_filing(engine, filing)
    print(filing.id)
    return 0


def _cmd_get(engine, args) -> int:
    filing = get_filing(engine, args.id)
    if filing is None:
        print(f"no filing with id {args.id!r}", file=sys.stderr)
        return 1
    print(filing.model_dump_json(indent=2))
    return 0


def _cmd_list(engine, args) -> int:
    filings = list_filings(engine, state=args.state, filer_role=args.filer_role)
    for f in filings:
        filer_name = (
            f.filer_person.name
            if f.filer_person is not None
            else (f.filer_organization.name if f.filer_organization is not None else "")
        )
        print(f"{f.id}\t{f.state}\t{f.filing_type}\t{f.filer_role}\t{filer_name}")
    return 0


_DISPATCH = {
    "ingest": _cmd_ingest,
    "get": _cmd_get,
    "list": _cmd_list,
}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="lobby_analysis.backend")
    parser.add_argument("--db", default=DEFAULT_DB, help="SQLite DB path")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_ingest = sub.add_parser("ingest", help="Load a LobbyingFiling JSON file")
    p_ingest.add_argument("path")

    p_get = sub.add_parser("get", help="Print one filing as JSON")
    p_get.add_argument("id")

    p_list = sub.add_parser("list", help="List filings")
    p_list.add_argument("--state")
    p_list.add_argument("--filer-role", dest="filer_role")

    args = parser.parse_args(argv)
    engine = init_engine(args.db)
    return _DISPATCH[args.cmd](engine, args)


if __name__ == "__main__":
    sys.exit(main())
