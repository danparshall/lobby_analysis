"""CLI: unify the lobbyist-side and principal-side authorization
tables into one provenance-annotated edge table.

Usage::

    uv run python -m lobby_analysis.io.wi.unify_authorizations_cli \\
        [--lobbyist-side-tsv PATH] \\
        [--principal-side-tsv PATH] \\
        [--grid-html PATH] \\
        [--output PATH]

The grid HTML is needed to compute the ``lobbyist_in_grid`` flag —
True if the lobbyist_id appeared in the LobbyistList grid AJAX
response when the lobbyist-side scrape ran, False otherwise (the
Schlaak-class indicator).

Output: TSV with the 4-column authorization edge schema plus
``discovered_via`` (``lobbyist``/``principal``/``both``) and
``lobbyist_in_grid`` (``true``/``false``). The Schlaak-class
population is the count of distinct ``lobbyist_id`` values where
``discovered_via='principal'`` and ``lobbyist_in_grid='false'``.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

from lobby_analysis.io.wi.lobbyist_id_discovery import parse_lobbyist_ids
from lobby_analysis.io.wi.unify_authorizations import (
    UNIFIED_FIELDNAMES,
    unify_authorization_tables,
)

DEFAULT_LOBBYIST_TSV = Path(
    "/Users/dan/data/lobby_analysis/disclosures/WI/"
    "WI_lobbyist_principal_authorizations.tsv"
)
DEFAULT_PRINCIPAL_TSV = Path(
    "/Users/dan/data/lobby_analysis/disclosures/WI/"
    "WI_lobbyist_principal_authorizations_principal_side.tsv"
)
DEFAULT_GRID_HTML = Path(
    "/Users/dan/data/lobby_analysis/disclosures/WI/"
    "_authorization_scrape_checkpoints/_lobbyist_grid_2025REG.html"
)
DEFAULT_OUTPUT_TSV = Path(
    "/Users/dan/data/lobby_analysis/disclosures/WI/"
    "WI_lobbyist_principal_authorizations_unified.tsv"
)


def _load_rows(tsv_path: Path) -> list[dict]:
    with tsv_path.open("r", encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def _write_unified_tsv(rows: list[dict], output_path: Path) -> int:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=UNIFIED_FIELDNAMES, delimiter="\t")
        writer.writeheader()
        for row in rows:
            writer.writerow({
                **row,
                # Bool → "true"/"false" for TSV portability.
                "lobbyist_in_grid": "true" if row["lobbyist_in_grid"] else "false",
            })
    return len(rows)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Unify lobbyist-side + principal-side WI authorization tables."
    )
    ap.add_argument("--lobbyist-side-tsv", type=Path, default=DEFAULT_LOBBYIST_TSV)
    ap.add_argument("--principal-side-tsv", type=Path, default=DEFAULT_PRINCIPAL_TSV)
    ap.add_argument("--grid-html", type=Path, default=DEFAULT_GRID_HTML,
                    help="Cached LobbyistList grid HTML (used to compute "
                         "the lobbyist_in_grid flag).")
    ap.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_TSV)
    args = ap.parse_args(argv)

    print(f"[load] lobbyist-side: {args.lobbyist_side_tsv}", flush=True)
    lobbyist_side = _load_rows(args.lobbyist_side_tsv)
    print(f"[load]   {len(lobbyist_side)} rows", flush=True)

    print(f"[load] principal-side: {args.principal_side_tsv}", flush=True)
    principal_side = _load_rows(args.principal_side_tsv)
    print(f"[load]   {len(principal_side)} rows", flush=True)

    print(f"[load] grid html: {args.grid_html}", flush=True)
    grid_html = args.grid_html.read_text(encoding="utf-8")
    grid_ids = set(parse_lobbyist_ids(grid_html))
    print(f"[load]   {len(grid_ids)} lobbyist IDs in grid", flush=True)

    print("[unify] computing union with provenance...", flush=True)
    unified = unify_authorization_tables(
        lobbyist_side_rows=lobbyist_side,
        principal_side_rows=principal_side,
        lobbyist_grid_ids=grid_ids,
    )

    n = _write_unified_tsv(unified, args.output)
    print(f"[unify] wrote {n} rows to {args.output}", flush=True)

    # Headline stats.
    by_via = {via: 0 for via in ("lobbyist", "principal", "both")}
    for row in unified:
        by_via[row["discovered_via"]] += 1

    schlaak_class_rows = [
        r for r in unified
        if r["discovered_via"] == "principal" and not r["lobbyist_in_grid"]
    ]
    schlaak_class_lobbyists = sorted({r["lobbyist_id"] for r in schlaak_class_rows})

    print(json.dumps({
        "total_rows": n,
        "by_discovered_via": by_via,
        "distinct_lobbyists": len({r["lobbyist_id"] for r in unified}),
        "distinct_principals": len({r["principal_id"] for r in unified}),
        "schlaak_class_rows": len(schlaak_class_rows),
        "schlaak_class_lobbyist_count": len(schlaak_class_lobbyists),
        "schlaak_class_lobbyist_ids": schlaak_class_lobbyists,
    }, indent=2), flush=True)

    return 0


if __name__ == "__main__":
    sys.exit(main())
