"""Recompute the published chain aggregates from NY_chain_2025.tsv.

Mirrors the metrics in releases/ny/chain/README.md so the doc can be kept in
sync with the shipped TSV after a regeneration. Prints a markdown-ready table.

    uv run --active python scripts/ny_chain_aggregates.py releases/ny/chain/NY_chain_2025.tsv
"""

from __future__ import annotations

import csv
import sys
from collections import defaultdict
from decimal import Decimal
from pathlib import Path

csv.field_size_limit(10_000_000)


def main(path_str: str) -> int:
    path = Path(path_str)
    rows = 0
    matched_rows = 0
    firms: set[str] = set()
    beneficiaries: set[str] = set()
    src_bills: set[str] = set()
    sponsors: set[str] = set()
    unmatched_bills: set[str] = set()
    cell_comp: dict[tuple, Decimal] = {}
    # coalition = a filing (filing_id,lobbyist_id,client_id) with M>1 beneficiaries
    filing_beneficiaries: dict[tuple, set] = defaultdict(set)

    with path.open(encoding="utf-8") as fh:
        for row in csv.DictReader(fh, delimiter="\t"):
            rows += 1
            firms.add(row["lobbyist_id"])
            beneficiaries.add(row["beneficiary_id"])
            src_bills.add(row["bill_id"])
            if row["sponsor_lawmaker_id"]:
                sponsors.add(row["sponsor_lawmaker_id"])
            if row["os_matched"] == "True":
                matched_rows += 1
            else:
                unmatched_bills.add(row["bill_id"])
            cell = (
                row["filing_id"],
                row["lobbyist_id"],
                row["beneficiary_id"],
                row["bill_id"],
            )
            if row["comp_per_cell"]:
                cell_comp[cell] = Decimal(row["comp_per_cell"])
            filing_beneficiaries[
                (row["filing_id"], row["lobbyist_id"], row["client_id"])
            ].add(row["beneficiary_id"])

    n_cells = len(cell_comp)
    coalition_filings = sum(1 for s in filing_beneficiaries.values() if len(s) > 1)
    total = sum(cell_comp.values(), Decimal(0))

    print(f"file:                                   {path}")
    print(f"chain rows:                             {rows:,}")
    print(f"distinct lobbying firms:                {len(firms):,}")
    print(f"distinct beneficiaries:                 {len(beneficiaries):,}")
    print(f"distinct bills (source bill_id):        {len(src_bills):,}")
    print(f"distinct sponsoring lawmakers:          {len(sponsors):,}")
    print(f"distinct cells:                         {n_cells:,}")
    print(f"rows resolved to OS bill+sponsor:       {matched_rows:,} "
          f"({100*matched_rows/rows:.1f}%)")
    print(f"distinct bills unmatched (flagged):     {len(unmatched_bills):,}")
    print(f"coalition filings (M>1 beneficiaries):  {coalition_filings:,}")
    print(f"total comp over distinct cells:         ${total:,.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1]))
