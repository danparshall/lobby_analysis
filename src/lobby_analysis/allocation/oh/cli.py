"""Phase 4 — OH allocation CLI.

One subcommand:

    materialize
        Runs the three composers (chain, gifts, filings) against the
        extraction cache + Plural Policy bundle (and oh.csv if provided)
        and writes three TSVs under the chosen output directory.

Usage:

    uv run --active python -m lobby_analysis.allocation.oh.cli materialize \\
        --extractions data/oh_portal/extracted \\
        --bills       data/bills/OH/136 \\
        --oh-csv      data/bills/OH/oh.csv \\
        --out         releases/oh

Output (per Q1 — preview release):

    <out>/chain/OH_chain_2025_2026_preview.tsv
    <out>/gifts/OH_gifts_2025_2026_preview.tsv
    <out>/filings/OH_filings_2025_2026_preview.tsv

The ``_preview`` suffix is hard-coded in v0: per Q1, the 316-filing slice
is non-representative and the released artifact must be honestly labeled.
The full-corpus run after issue #35 lands removes the suffix.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from lobby_analysis.allocation.oh.chain import compose_bill_chain
from lobby_analysis.allocation.oh.filings import compose_filings
from lobby_analysis.allocation.oh.gifts import compose_gifts

_PREVIEW_SUFFIX = "_preview"


def _write_tsv(df, path: Path) -> None:
    """Write a TSV; lossless against embedded tabs/newlines via pandas default."""
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, sep="\t", index=False)


def _cmd_materialize(args: argparse.Namespace) -> int:
    extractions = args.extractions
    bills = args.bills
    oh_csv = args.oh_csv
    out_root = args.out

    print(f"extractions: {extractions.resolve()}")
    print(f"bills:       {bills.resolve()}")
    print(f"oh_csv:      {oh_csv.resolve() if oh_csv else '<not provided>'}")
    print(f"out:         {out_root.resolve()}")

    chain_path = out_root / "chain" / f"OH_chain_2025_2026{_PREVIEW_SUFFIX}.tsv"
    gifts_path = out_root / "gifts" / f"OH_gifts_2025_2026{_PREVIEW_SUFFIX}.tsv"
    filings_path = out_root / "filings" / f"OH_filings_2025_2026{_PREVIEW_SUFFIX}.tsv"

    print("\n[1/3] compose_bill_chain...")
    chain_df = compose_bill_chain(extractions, bills)
    print(f"      chain rows: {len(chain_df)}")
    _write_tsv(chain_df, chain_path)
    print(f"      → {chain_path}")

    print("\n[2/3] compose_gifts...")
    gifts_df = compose_gifts(extractions, oh_csv)
    print(f"      gifts rows: {len(gifts_df)}")
    _write_tsv(gifts_df, gifts_path)
    print(f"      → {gifts_path}")

    print("\n[3/3] compose_filings...")
    filings_df = compose_filings(extractions)
    print(f"      filings rows: {len(filings_df)}")
    _write_tsv(filings_df, filings_path)
    print(f"      → {filings_path}")

    print("\ndone")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="lobby_analysis.allocation.oh.cli",
        description="Materialize the OH chain + gifts + filings release artifacts.",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_mat = sub.add_parser(
        "materialize",
        help="Compose chain + gifts + filings and write the three release TSVs.",
    )
    p_mat.add_argument(
        "--extractions",
        type=Path,
        required=True,
        help="Directory of OH AER extractions (data/oh_portal/extracted).",
    )
    p_mat.add_argument(
        "--bills",
        type=Path,
        required=True,
        help="Plural Policy 136th GA bundle directory (data/bills/OH/136).",
    )
    p_mat.add_argument(
        "--oh-csv",
        type=Path,
        default=None,
        help="Optional Open States oh.csv legislator roster for gift lawmaker resolution.",
    )
    p_mat.add_argument(
        "--out",
        type=Path,
        default=Path("releases/oh"),
        help="Output release directory root (default: releases/oh).",
    )
    p_mat.set_defaults(func=_cmd_materialize)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
