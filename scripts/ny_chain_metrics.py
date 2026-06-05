"""Ad-hoc chain metrics for the &amp;-decode regeneration sanity check.

Reports row count, distinct-cell compensation total (the conservation invariant),
distinct beneficiary count, and any residual HTML-entity fragments in the
beneficiary column. Run before and after regeneration to confirm the decode
removed phantom beneficiaries without moving dollars.

    uv run --active python scripts/ny_chain_metrics.py releases/ny/chain/NY_chain_2025.tsv
"""

from __future__ import annotations

import csv
import sys
from decimal import Decimal
from pathlib import Path

csv.field_size_limit(10_000_000)


def main(path_str: str) -> int:
    path = Path(path_str)
    rows = 0
    cell_comp: dict[tuple, Decimal] = {}
    beneficiaries: set[str] = set()
    amp_fragments = 0
    frag_examples: set[str] = set()
    with path.open(encoding="utf-8") as fh:
        for row in csv.DictReader(fh, delimiter="\t"):
            rows += 1
            key = (
                row["filing_id"],
                row["lobbyist_id"],
                row["beneficiary_id"],
                row["bill_id"],
            )
            # comp_per_cell is replicated across sponsor rows of one cell -> keep one.
            comp = row["comp_per_cell"]
            if comp:
                cell_comp[key] = Decimal(comp)
            bn = row["beneficiary_name"]
            beneficiaries.add(bn)
            if "&amp" in bn:
                amp_fragments += 1
                if len(frag_examples) < 15:
                    frag_examples.add(bn)
    total = sum(cell_comp.values(), Decimal(0))
    print(f"file:                 {path}")
    print(f"rows:                 {rows:,}")
    print(f"distinct cells:       {len(cell_comp):,}")
    print(f"distinct-cell total:  ${total:,.2f}")
    print(f"distinct beneficiary: {len(beneficiaries):,}")
    print(f"amp-fragment rows:    {amp_fragments:,}")
    if frag_examples:
        print("fragment examples:")
        for ex in sorted(frag_examples):
            print(f"    {ex!r}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1]))
