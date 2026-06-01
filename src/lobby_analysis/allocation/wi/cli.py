"""CLI for the WI allocation matrix + chain.

Two subcommands:

    allocation
        Phase 2: build the per-semester allocation matrix.

        uv run --active python -m lobby_analysis.allocation.wi.cli allocation \
            --release-dir releases/wi \
            --output-dir data/allocations/WI

    chain
        Phase 3: compose the end-to-end principal → lobbyist → bill → sponsor
        chain. Reads the Phase 2 output + bulk OpenStates CSV bundle.

        uv run --active python -m lobby_analysis.allocation.wi.cli chain \
            --allocation-dir data/allocations/WI \
            --release-dir releases/wi \
            --bill-csv-dir data/bills/WI/2025 \
            --legislators-csv data/bills/wi.csv \
            --output data/allocations/WI/WI_chain_2025.tsv
"""

from __future__ import annotations

import argparse
from pathlib import Path

from lobby_analysis.allocation.wi.materialize import (
    materialize_allocation_matrix,
    materialize_chain,
)


def _cmd_allocation(args: argparse.Namespace) -> int:
    print(f"reading release: {args.release_dir.resolve()}")
    print(f"writing output:  {args.output_dir.resolve()}")
    materialize_allocation_matrix(args.release_dir, args.output_dir)
    print("done")
    return 0


def _cmd_chain(args: argparse.Namespace) -> int:
    print(f"allocation dir:  {args.allocation_dir.resolve()}")
    print(f"release dir:     {args.release_dir.resolve()}")
    print(f"bill csv dir:    {args.bill_csv_dir.resolve()}")
    print(f"legislators csv: {args.legislators_csv.resolve()}")
    print(f"output:          {args.output.resolve()}")
    materialize_chain(
        allocation_dir=args.allocation_dir,
        release_dir=args.release_dir,
        bill_csv_dir=args.bill_csv_dir,
        legislators_csv=args.legislators_csv,
        output_path=args.output,
    )
    print("done")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Materialize the WI allocation matrix and Phase 3 chain."
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_alloc = sub.add_parser(
        "allocation", help="Materialize the Phase 2 allocation matrix per semester."
    )
    p_alloc.add_argument(
        "--release-dir", type=Path, default=Path("releases/wi"),
    )
    p_alloc.add_argument(
        "--output-dir", type=Path, default=Path("data/allocations/WI"),
    )
    p_alloc.set_defaults(func=_cmd_allocation)

    p_chain = sub.add_parser(
        "chain", help="Compose the Phase 3 chain into a single TSV."
    )
    p_chain.add_argument(
        "--allocation-dir", type=Path, default=Path("data/allocations/WI"),
    )
    p_chain.add_argument(
        "--release-dir", type=Path, default=Path("releases/wi"),
    )
    p_chain.add_argument(
        "--bill-csv-dir", type=Path, default=Path("data/bills/WI/2025"),
    )
    p_chain.add_argument(
        "--legislators-csv", type=Path, default=Path("data/bills/wi.csv"),
    )
    p_chain.add_argument(
        "--output", type=Path, default=Path("data/allocations/WI/WI_chain_2025.tsv"),
    )
    p_chain.set_defaults(func=_cmd_chain)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
