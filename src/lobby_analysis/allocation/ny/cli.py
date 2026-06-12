"""CLI for the NY Phase-4 chain composer.

One subcommand (NY has no allocation/IPF stage — the lobbyist->bill link is
disclosed directly, so the chain is a join):

    chain
        Compose the firm -> beneficiary -> bill -> sponsor chain. Reads the
        Phase-3 ``releases/ny/`` tables + the gitignored Open States NY bill
        bundle, and writes ``releases/ny/chain/NY_chain_<years>.tsv``.

        uv run --active python -m lobby_analysis.allocation.ny.cli chain \
            --release-dir releases/ny \
            --bill-csv-dir data/bills/NY/2025 \
            --output releases/ny/chain/NY_chain_2025.tsv
"""

from __future__ import annotations

import argparse
from pathlib import Path

from lobby_analysis.allocation.ny.chain import materialize_chain


def _cmd_chain(args: argparse.Namespace) -> int:
    print(f"release dir:  {args.release_dir.resolve()}")
    print(f"bill csv dir: {args.bill_csv_dir.resolve()}")
    print(f"output:       {args.output.resolve()}")
    n = materialize_chain(
        release_dir=args.release_dir,
        csv_dir=args.bill_csv_dir,
        output_path=args.output,
    )
    print(f"wrote {n} chain rows")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Compose the NY Phase-4 chain (firm -> beneficiary -> bill -> sponsor)."
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_chain = sub.add_parser("chain", help="Compose the chain into a single TSV.")
    p_chain.add_argument("--release-dir", type=Path, default=Path("releases/ny"))
    p_chain.add_argument("--bill-csv-dir", type=Path, default=Path("data/bills/NY/2025"))
    p_chain.add_argument(
        "--output", type=Path, default=Path("releases/ny/chain/NY_chain_2025.tsv")
    )
    p_chain.set_defaults(func=_cmd_chain)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
