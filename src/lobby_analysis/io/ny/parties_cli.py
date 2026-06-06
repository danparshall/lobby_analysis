"""CLI: materialize the NY ``parties_lobbied`` disclosed-lawmaker edge.

Wires the parties pipeline over the re-pulled ``client_semiannual`` CSV (which
must include the ``parties_lobbied`` column — see ``scripts/ny_pull_2025.py``)::

    read_csv (only the columns the edge needs)
      -> columns.normalize_columns(dataset)
      -> parties.extract_filing_parties(df, roster)
      -> parties.materialize_parties_lobbied(output_dir)

The roster is built from the Open States NY sponsorship file
(``--os-dir``). Prints a JSON summary plus the resolution metrics (total party
rows, distinct resolved ``ocd-person``s, resolution rate, top unresolved values)
so the release doc's aggregates come straight from the run. No new behavior tests
— ``parties.py``'s suite covers the steps (mirrors ``materialize_cli``'s
"no new tests" precedent).

Usage::

    uv run python -m lobby_analysis.io.ny.parties_cli \\
        --input data/raw/ny/2025/client_semiannual.csv \\
        --os-dir data/bills/NY/2025 \\
        --output-dir releases/ny

Plan: ``docs/active/ny-disclosure-explore/plans/ny_parties_lobbied_mvp.md`` (Phase 3).
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from collections import Counter
from pathlib import Path

import pandas as pd

from lobby_analysis.io.ny.columns import COLUMN_MAPS, normalize_columns
from lobby_analysis.io.ny.parties import (
    build_legislator_roster,
    extract_filing_parties,
    materialize_parties_lobbied,
)

DEFAULT_OUTPUT_DIR = Path("releases/ny")
DEFAULT_OS_DIR = Path("data/bills/NY/2025")

#: Only the columns the parties edge consumes (form_submission_id + BUSINESS_KEY +
#: parties_lobbied). Reading this subset keeps the 3+ GB CSV's memory footprint
#: down — the focus/compensation columns the bill-link pipeline needs are skipped.
_USECOLS = [
    "form_submission_id",
    "reporting_year",
    "reporting_period",
    "principal_lobbyist",
    "beneficial_client",
    "contractual_client_name",
    "parties_lobbied",
]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=(
            "Materialize the NY parties_lobbied disclosed-lawmaker edge "
            "(releases/ny/NY_filing_parties_lobbied.tsv) from a re-pulled "
            "client_semiannual CSV + the Open States NY sponsorship roster."
        )
    )
    ap.add_argument("--input", type=Path, required=True,
                    help="client_semiannual CSV (must include parties_lobbied).")
    ap.add_argument("--dataset", choices=sorted(COLUMN_MAPS), default="client_semiannual",
                    help="Which NY dataset the CSV is (selects the column map).")
    ap.add_argument("--os-dir", type=Path, default=DEFAULT_OS_DIR,
                    help="Dir holding NY_*_bill_sponsorships.csv (the OS roster source).")
    ap.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR,
                    help="Where to write NY_filing_parties_lobbied.tsv.")
    args = ap.parse_args(argv)

    print(f"[ny-parties] input:      {args.input}", flush=True)
    print(f"[ny-parties] os-dir:     {args.os_dir}", flush=True)
    print(f"[ny-parties] output-dir: {args.output_dir}", flush=True)

    t0 = time.time()
    roster = build_legislator_roster(args.os_dir)
    print(f"[ny-parties] roster legislators: {len(roster)}", flush=True)

    df = pd.read_csv(args.input, dtype=str, keep_default_na=False, usecols=_USECOLS)
    print(f"[ny-parties] raw rows: {len(df):,}", flush=True)
    df = normalize_columns(df, args.dataset)
    parties = extract_filing_parties(df, roster)
    counts = materialize_parties_lobbied(parties, output_dir=args.output_dir)
    elapsed = time.time() - t0

    # Resolution metrics for the release doc.
    total = len(parties)
    resolved_mask = parties["resolved"]
    n_resolved = int(resolved_mask.sum())
    distinct_persons = int(parties.loc[resolved_mask, "party_lobbied_person_id"].nunique())
    rate = (100 * n_resolved / total) if total else 0.0
    unresolved_top = Counter(
        parties.loc[~resolved_mask, "party_lobbied_raw"]
    ).most_common(15)

    print(
        json.dumps(
            {
                "elapsed_seconds": round(elapsed, 1),
                "row_counts": counts,
                "total_party_rows": total,
                "resolved_rows": n_resolved,
                "resolution_rate_pct": round(rate, 1),
                "distinct_resolved_persons": distinct_persons,
                "top_unresolved": [{"raw": v, "rows": c} for v, c in unresolved_top],
            },
            indent=2,
        ),
        flush=True,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
