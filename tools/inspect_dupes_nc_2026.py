"""Look at the 59 duplicate (Lobbyist, Principal) pairs in NC_2026.xlsx.

Are they amendment-style duplicates (same content), or do something differ
between the rows (e.g., firm switches, address updates)?

Run from worktree root:
    .venv/bin/python tools/inspect_dupes_nc_2026.py
"""

from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path

import openpyxl


def main() -> None:
    path = Path("data/disclosures/NC_2026.xlsx")
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    ws = wb["Sheet1"]
    rows_iter = ws.iter_rows(values_only=True)
    header = list(next(rows_iter))
    n_cols = len(header)
    data = [r + (None,) * (n_cols - len(r)) if len(r) < n_cols else r for r in rows_iter]

    # Bucket rows by (LobbyName, Principal)
    by_pair = defaultdict(list)
    for r in data:
        by_pair[(r[1], r[13])].append(r)

    dup_groups = {k: v for k, v in by_pair.items() if len(v) > 1}
    print(f"== Duplicate (Lobbyist, Principal) pairs ==")
    print(f"  groups: {len(dup_groups)}")
    print(f"  total rows in dup groups: {sum(len(v) for v in dup_groups.values()):,}")
    print(f"  group size distribution: {Counter(len(v) for v in dup_groups.values())}")

    print(f"\n== Are dup rows byte-identical? ==")
    identical_count = 0
    differ_count = 0
    for k, v in dup_groups.items():
        if len({tuple(r) for r in v}) == 1:
            identical_count += 1
        else:
            differ_count += 1
    print(f"  identical: {identical_count}")
    print(f"  differ:    {differ_count}")

    print(f"\n== First 5 differing dup groups: which columns differ? ==")
    shown = 0
    for k, v in dup_groups.items():
        if len({tuple(r) for r in v}) == 1:
            continue
        shown += 1
        if shown > 5:
            break
        print(f"\n  --- ({k[0]!r}, {k[1]!r}) -- {len(v)} rows")
        # find columns that differ
        for i, col in enumerate(header):
            vals = {r[i] for r in v}
            if len(vals) > 1:
                print(f"    col [{i}] {col}: {vals}")

    print(f"\n== First 3 identical dup groups (sanity) ==")
    shown = 0
    for k, v in dup_groups.items():
        if len({tuple(r) for r in v}) > 1:
            continue
        shown += 1
        if shown > 3:
            break
        print(f"  ({k[0]!r}, {k[1]!r}) -- {len(v)} identical rows")


if __name__ == "__main__":
    main()
