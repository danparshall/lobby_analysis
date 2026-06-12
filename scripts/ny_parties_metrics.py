"""Resolution metrics for NY_filing_parties_lobbied.tsv (before/after comparison).

Computes the same state-legislator resolution metric used across the
parties_lobbied sessions: of the edge rows that carry a legislator title
(``Senator`` / ``Assembly member`` / ``Assemblyman`` / ``Assemblywoman``),
how many resolved to an ``ocd-person``.

Usage:  PYTHONPATH=src python scripts/ny_parties_metrics.py releases/ny/NY_filing_parties_lobbied.tsv
"""

from __future__ import annotations

import csv
import sys
from collections import Counter

LEG_PREFIXES = ("senator ", "assembly member ", "assemblywoman ", "assemblyman ",
                "assembly woman ", "assembly man ")


def main(path: str) -> int:
    csv.field_size_limit(10**7)
    total = 0
    resolved = 0
    leg_titled = 0
    leg_resolved = 0
    distinct_persons: set[str] = set()
    unresolved_leg: Counter[str] = Counter()
    with open(path, encoding="utf-8", newline="") as fh:
        for row in csv.DictReader(fh, delimiter="\t"):
            total += 1
            raw = row["party_lobbied_raw"]
            is_resolved = row["resolved"] == "True"
            low = raw.lower()
            is_leg_titled = any(low.startswith(p) for p in LEG_PREFIXES)
            if is_resolved:
                resolved += 1
                distinct_persons.add(row["party_lobbied_person_id"])
            if is_leg_titled:
                leg_titled += 1
                if is_resolved:
                    leg_resolved += 1
                else:
                    unresolved_leg[raw] += 1

    print(f"file:                       {path}")
    print(f"total edge rows:            {total:,}")
    print(f"resolved rows (all):        {resolved:,} ({100*resolved/total:.2f}%)")
    print(f"distinct resolved persons:  {len(distinct_persons):,}")
    print(f"legislator-titled rows:     {leg_titled:,}")
    print(f"  of which resolved:        {leg_resolved:,} "
          f"({100*leg_resolved/leg_titled:.2f}%)")
    print(f"  still unresolved:         {leg_titled - leg_resolved:,} "
          f"({len(unresolved_leg)} distinct)")
    print("top-20 unresolved legislator-titled values:")
    for raw, n in unresolved_leg.most_common(20):
        print(f"    {n:6,}  {raw}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "releases/ny/NY_filing_parties_lobbied.tsv"))
