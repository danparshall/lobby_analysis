"""CLI for the WI allocation matrix.

Usage:

    uv run --active python -m lobby_analysis.allocation.wi.cli \
        --release-dir releases/wi \
        --output-dir data/allocations/WI

Produces ``WI_lobbyist_principal_hours_h{1,2}_2025.tsv`` in the output
directory.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from lobby_analysis.allocation.wi.materialize import materialize_allocation_matrix


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Materialize the WI allocation matrix to TSV (per semester)."
    )
    parser.add_argument(
        "--release-dir",
        type=Path,
        default=Path("releases/wi"),
        help="Path to the WI release directory (default: releases/wi)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("data/allocations/WI"),
        help="Output dir for the per-semester TSVs "
        "(default: data/allocations/WI)",
    )
    args = parser.parse_args(argv)

    print(f"reading release: {args.release_dir.resolve()}")
    print(f"writing output:  {args.output_dir.resolve()}")
    materialize_allocation_matrix(args.release_dir, args.output_dir)
    print("done")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
