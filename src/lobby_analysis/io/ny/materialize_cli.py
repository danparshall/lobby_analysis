"""CLI: materialize the NY ``releases/ny/`` disclosure TSVs from a raw Open NY
bulk CSV.

Thin wrapper that wires the full Phase-2 pipeline over one dataset's bulk CSV::

    read_csv
      -> columns.normalize_columns(dataset)
      -> parse.add_bill_id_column
      -> grain.collapse_to_filing_grain
      -> materialize.materialize_ny(output_dir)

then prints a JSON summary of per-file row counts. No new behavior tests — the
materializer's and the upstream steps' suites cover everything this CLI does
(mirrors WI's ``tier_2_materialize_cli`` "no new tests" precedent).

The acquisition layer (``io/ny/acquire.download_bulk_csv``) writes the input CSV
to ``data/raw/ny/<year>/<dataset>.csv``; this CLI reads from there by default.

Usage::

    uv run python -m lobby_analysis.io.ny.materialize_cli \\
        --input data/raw/ny/2025/client_semiannual.csv \\
        --dataset client_semiannual \\
        --output-dir releases/ny

Plan: ``docs/active/ny-disclosure-explore/plans/ny_disclosure_pipeline.md``
(Phase 2 / Phase 3).
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import pandas as pd

from lobby_analysis.io.ny.columns import COLUMN_MAPS, normalize_columns
from lobby_analysis.io.ny.grain import collapse_to_filing_grain
from lobby_analysis.io.ny.materialize import materialize_ny
from lobby_analysis.io.ny.parse import add_bill_id_column

DEFAULT_OUTPUT_DIR = Path("releases/ny")


def _build_grain(input_csv: Path, dataset: str) -> pd.DataFrame:
    """Read the raw bulk CSV and run it through the Phase-2 pipeline to grain.

    Reads as ``dtype=str`` so the dirty NY money/id strings survive intact for
    the typed coercers downstream (pandas would otherwise infer floats and lose
    the ``"$"`` / leading-zero / exact-cents signal). ``keep_default_na=False``
    keeps empty cells as ``""`` rather than NaN, matching the coercers' contract.
    """
    df = pd.read_csv(input_csv, dtype=str, keep_default_na=False)
    df = normalize_columns(df, dataset)
    df = add_bill_id_column(df)
    return collapse_to_filing_grain(df)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=(
            "Materialize the NY releases/ny disclosure TSVs (clients / "
            "lobbyists / filings / filing-bill links) from a raw Open NY bulk "
            "CSV, running the full Phase-2 pipeline (column-normalize -> "
            "bill_id -> grain collapse -> materialize)."
        )
    )
    ap.add_argument(
        "--input",
        type=Path,
        required=True,
        help="Raw Open NY bulk CSV (e.g. data/raw/ny/2025/client_semiannual.csv).",
    )
    ap.add_argument(
        "--dataset",
        choices=sorted(COLUMN_MAPS),
        default="client_semiannual",
        help="Which NY dataset the CSV is (selects the column map).",
    )
    ap.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Where to write the NY release TSVs.",
    )
    args = ap.parse_args(argv)

    print(f"[ny-materialize] input:      {args.input}", flush=True)
    print(f"[ny-materialize] dataset:    {args.dataset}", flush=True)
    print(f"[ny-materialize] output-dir: {args.output_dir}", flush=True)

    t0 = time.time()
    grain = _build_grain(args.input, args.dataset)
    print(f"[ny-materialize] grain rows: {len(grain)}", flush=True)
    counts = materialize_ny(grain, output_dir=args.output_dir)
    elapsed = time.time() - t0

    print(
        json.dumps(
            {"elapsed_seconds": round(elapsed, 1), "row_counts": counts}, indent=2
        ),
        flush=True,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
