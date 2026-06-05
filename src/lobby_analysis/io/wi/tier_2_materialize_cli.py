"""CLI: materialize the WI Tier-2 disclosure-data layer from on-disk
checkpoint JSONs.

Thin pass-through over ``materialize_tier_2``. Writes 5 TSVs + the
parse-failures warnings TSV under ``--output-dir`` and prints a JSON
summary of row counts. No new behavior tests — the materializer's
test suite covers everything this CLI does.

Usage::

    uv run python -m lobby_analysis.io.wi.tier_2_materialize_cli \\
        [--principal-checkpoints PATH] \\
        [--lobbyist-checkpoints PATH] \\
        [--output-dir PATH]

Plan: ``docs/active/wi-disclosure-explore/plans/wi_tier_2_parser.md``
(Phase 5).
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

from lobby_analysis.io.wi.tier_2_materialize import materialize_tier_2

DEFAULT_PRINCIPAL_CHECKPOINTS = Path(
    "/Users/dan/data/lobby_analysis/disclosures/WI/_principal_scrape_checkpoints"
)
DEFAULT_LOBBYIST_CHECKPOINTS = Path(
    "/Users/dan/data/lobby_analysis/disclosures/WI/_authorization_scrape_checkpoints"
)
DEFAULT_OUTPUT_DIR = Path(
    "/Users/dan/data/lobby_analysis/disclosures/WI"
)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=(
            "Materialize the WI Tier-2 disclosure layer (Organization / "
            "Person / LobbyingFiling / per-item bill efforts) from on-disk "
            "checkpoint JSONs."
        )
    )
    ap.add_argument(
        "--principal-checkpoints",
        type=Path,
        default=DEFAULT_PRINCIPAL_CHECKPOINTS,
        help="Directory of {principal_id}.json checkpoints from "
             "scrape_principals.",
    )
    ap.add_argument(
        "--lobbyist-checkpoints",
        type=Path,
        default=DEFAULT_LOBBYIST_CHECKPOINTS,
        help="Directory of {lobbyist_id}.json checkpoints from "
             "scrape_authorizations.",
    )
    ap.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Where to write the 5 TSVs and _tier_2_parse_failures.tsv.",
    )
    args = ap.parse_args(argv)

    print(f"[materialize] principal-checkpoints: {args.principal_checkpoints}", flush=True)
    print(f"[materialize] lobbyist-checkpoints:  {args.lobbyist_checkpoints}", flush=True)
    print(f"[materialize] output-dir:            {args.output_dir}", flush=True)

    t0 = time.time()
    counts = materialize_tier_2(
        principal_checkpoints_dir=args.principal_checkpoints,
        lobbyist_checkpoints_dir=args.lobbyist_checkpoints,
        output_dir=args.output_dir,
    )
    elapsed = time.time() - t0

    print(
        json.dumps(
            {
                "elapsed_seconds": round(elapsed, 1),
                "row_counts": counts,
            },
            indent=2,
        ),
        flush=True,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
