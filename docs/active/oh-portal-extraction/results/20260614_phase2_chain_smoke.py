"""Smoke test for the OH chain composer against the real 316-filing cache."""
from collections import Counter
from pathlib import Path

import pandas as pd

from lobby_analysis.allocation.oh.chain import compose_bill_chain

WORKTREE = Path("/Users/dan/code/lobby_analysis/.worktrees/oh-chain-composer")
EXTRACT = WORKTREE / "data" / "oh_portal" / "extracted"
BILLS = WORKTREE / "data" / "bills" / "OH" / "136"


def main() -> None:
    pd.set_option("display.max_columns", 20)
    pd.set_option("display.width", 240)

    print("Composing OH bill chain against the 316-filing cache...")
    df = compose_bill_chain(EXTRACT, BILLS)
    print(f"\nChain rows: {len(df):,}")
    print(f"Columns: {list(df.columns)}")

    print("\nbill_class distribution:")
    for cls, n in df["bill_class"].value_counts().items():
        print(f"  {cls!r:14} {n:>5}")
    print(f"  TOTAL          {len(df):>5}")

    print("\nposition_kind distribution:")
    for k, n in df["position_kind"].value_counts(dropna=False).items():
        print(f"  {str(k)!r:38} {n:>5}")

    print("\nconfidence distribution:")
    for c, n in df["confidence"].value_counts(dropna=False).items():
        print(f"  {c!r:18} {n:>5}")

    print("\nnum_primary_sponsors distribution (top 10):")
    for n_primary, count in df["num_primary_sponsors"].value_counts().head(10).items():
        print(f"  primary_count={n_primary:3d}: {count:>5} chain rows")

    print("\nTop 5 most-lobbied bills (by chain rows):")
    bill_rows = df[df["bill_class"] == "bill"]
    top_bills = (
        bill_rows.groupby(["bill_label_normalized", "bill_title"])
        .size()
        .sort_values(ascending=False)
        .head(5)
    )
    for (label, title), n in top_bills.items():
        print(f"  {n:>4}× {label:8} — {str(title)[:75]}")

    print("\nConservation check:")
    print(f"  Total positions input (1,177 from Phase 1 smoke): expecting equal coverage")
    # bill rows might be > positions (cross-product) so this is rows-from-N-positions
    # Empty-position sentinels would show as confidence=null_extraction
    print(f"  null_extraction sentinels: {(df['confidence'] == 'null_extraction').sum()}")
    print(f"  Unique filing_ids in output: {df['filing_id'].nunique()} (canonical extraction count)")

    # By-filing position count check: each filing's contribution to chain row count
    # should be sum over its positions of N_sponsors (>=1)
    per_filing = df.groupby("filing_id").size().describe()
    print(f"\nChain rows per filing: {per_filing.to_dict()}")


if __name__ == "__main__":
    main()
