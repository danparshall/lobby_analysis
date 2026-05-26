"""Profile NC_2026.xlsx beyond first-look: counts, uniques, nulls, term values.

Run from worktree root:
    .venv/bin/python tools/profile_nc_2026.py
"""

from __future__ import annotations

from collections import Counter
from pathlib import Path

import openpyxl


def main() -> None:
    path = Path("data/disclosures/NC_2026.xlsx")
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    ws = wb["Sheet1"]
    rows_iter = ws.iter_rows(values_only=True)
    header = list(next(rows_iter))

    data = [row for row in rows_iter]

    # openpyxl read_only mode returns rows that may be shorter than the header
    # if trailing cells are empty. Pad to header width for uniform column access.
    n_cols = len(header)
    row_lens = Counter(len(r) for r in data)
    data = [r + (None,) * (n_cols - len(r)) if len(r) < n_cols else r for r in data]
    print(f"\n== Raw row-length distribution (pre-pad) ==")
    for lng, n in sorted(row_lens.items()):
        print(f"  len={lng}: {n:,} rows")
    print(f"== Row count ==")
    print(f"  data rows: {len(data):,}")

    # Term distribution
    terms = Counter(r[0] for r in data)
    print(f"\n== Term values ==")
    for t, n in terms.most_common():
        print(f"  {t!r}: {n:,}")

    # Per-column nulls + uniques
    print(f"\n== Per-column null + unique counts ==")
    print(f"  {'col':<24} {'nulls':>8} {'uniques':>8} {'first_nonnull':<30}")
    for i, col in enumerate(header):
        vals = [r[i] for r in data]
        n_null = sum(1 for v in vals if v is None or v == "")
        n_uniq = len({v for v in vals if v is not None and v != ""})
        first_nn = next((str(v) for v in vals if v is not None and v != ""), "")
        if len(first_nn) > 28:
            first_nn = first_nn[:25] + "..."
        print(f"  [{i:>2}] {col:<20} {n_null:>8,} {n_uniq:>8,} {first_nn!r}")

    # Unique lobbyists and principals
    lobbyists = {r[1] for r in data if r[1]}
    principals = {r[13] for r in data if r[13]}
    firms = {r[7] for r in data if r[7]}
    print(f"\n== Entity counts ==")
    print(f"  unique LobbyName:    {len(lobbyists):,}")
    print(f"  unique LobbyFirm:    {len(firms):,}")
    print(f"  unique Principal:    {len(principals):,}")

    # Pairs (lobbyist, principal)
    pairs = {(r[1], r[13]) for r in data if r[1] and r[13]}
    print(f"  unique (Lobbyist, Principal) pairs: {len(pairs):,}")

    # Per-lobbyist principal count distribution
    per_lob = Counter(r[1] for r in data if r[1] and r[13])
    pcounts = Counter(per_lob.values())
    print(f"\n== Distribution: principals per lobbyist ==")
    for k in sorted(pcounts):
        print(f"  {k:>3} principal(s): {pcounts[k]:,} lobbyists")
    top = per_lob.most_common(5)
    print(f"\n  top 5 lobbyists by #principals:")
    for name, n in top:
        print(f"    {n:>3}  {name}")

    # State diversity (lobbyist + principal sides)
    lob_states = Counter(r[10] for r in data if r[10])
    prin_states = Counter(r[18] for r in data if r[18])
    print(f"\n== Lobbyist state distribution (top 5) ==")
    for s, n in lob_states.most_common(5):
        print(f"  {s}: {n:,}")
    print(f"\n== Principal state distribution (top 5) ==")
    for s, n in prin_states.most_common(5):
        print(f"  {s}: {n:,}")

    # ReadOnlySearch is the last column — what values?
    ros = Counter(r[24] for r in data)
    print(f"\n== ReadOnlySearch values ==")
    for v, n in ros.most_common():
        print(f"  {v!r}: {n:,}")


if __name__ == "__main__":
    main()
