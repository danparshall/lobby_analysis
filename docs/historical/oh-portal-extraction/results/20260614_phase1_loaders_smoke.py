"""Quick real-data smoke test for the OH Phase 1 loaders."""
from pathlib import Path

import pandas as pd

from lobby_analysis.allocation.oh.classify import (
    classify_bill_label,
    classify_position_shape,
    extract_position_label,
)
from lobby_analysis.allocation.oh.load import (
    load_filings,
    load_gifts,
    load_plural_bills,
    load_plural_sponsorships,
    load_positions,
)

WORKTREE = Path("/Users/dan/code/lobby_analysis/.worktrees/oh-chain-composer")
EXTRACT = WORKTREE / "data" / "oh_portal" / "extracted"
BILLS = WORKTREE / "data" / "bills" / "OH" / "136"


def main() -> None:
    pd.set_option("display.max_columns", 20)
    pd.set_option("display.width", 220)

    print("=" * 70, "\nload_filings\n", "=" * 70, sep="")
    filings = load_filings(EXTRACT)
    print(f"shape: {filings.shape}")
    print(f"columns: {list(filings.columns)}")
    print(f"unique filing_ids: {filings['filing_id'].nunique()}")
    print(f"unique principals: {filings['principal_name'].nunique()}")
    print(f"unique lobbyists: {filings['lobbyist_name'].nunique()}")
    print(f"n_positions sum: {filings['n_positions'].sum()}")
    print(f"n_gifts sum: {filings['n_gifts'].sum()}")
    print(f"filing_action distribution: {filings['filing_action'].value_counts().to_dict()}")
    print(f"total_expenditure NaN count: {filings['total_expenditure'].isna().sum()}")
    print(f"is_current True count: {(filings['is_current'] == True).sum()}")

    print("\n" + "=" * 70, "\nload_positions\n", "=" * 70, sep="")
    positions = load_positions(EXTRACT)
    print(f"shape: {positions.shape}")
    # Should match filings['n_positions'].sum()
    assert len(positions) == filings["n_positions"].sum(), "positions row count mismatch"
    print("✓ position row count matches filings n_positions sum")

    print("\n" + "=" * 70, "\nload_gifts\n", "=" * 70, sep="")
    gifts = load_gifts(EXTRACT)
    print(f"shape: {gifts.shape}")
    assert len(gifts) == filings["n_gifts"].sum(), "gifts row count mismatch"
    print("✓ gift row count matches filings n_gifts sum")
    if len(gifts):
        print("Sample recipient_name:")
        for g in gifts["gift_obj"].head(5):
            print(f"  {g.recipient_name!r}: {g.value} ({g.gift_type})")

    print("\n" + "=" * 70, "\nload_plural_bills\n", "=" * 70, sep="")
    bills = load_plural_bills(BILLS)
    print(f"shape: {bills.shape}")
    print(f"sample identifier_norm: {sorted(bills['identifier_norm'])[:5]}")

    print("\n" + "=" * 70, "\nload_plural_sponsorships (primary only)\n", "=" * 70, sep="")
    spons = load_plural_sponsorships(BILLS)
    print(f"shape: {spons.shape}")
    print(f"classifications: {spons['classification'].value_counts().to_dict()}")
    print(f"unique bills with primaries: {spons['bill_id'].nunique()}")

    print("\n" + "=" * 70, "\nClassifier round-trip on positions\n", "=" * 70, sep="")
    # Apply classify_position_shape + classify_bill_label to each position.
    # This exercises the classifier-loader integration we'll need in Phase 2.
    kinds = []
    classes = []
    defects = 0
    for pos in positions["position_obj"]:
        try:
            kind = classify_position_shape(pos)
            label = extract_position_label(pos)
            cls = classify_bill_label(label, kind)
            kinds.append(kind)
            classes.append(cls)
        except ValueError:
            defects += 1
    print(f"Total positions classified: {len(kinds)}")
    print(f"Extraction defects (empty positions): {defects}")
    from collections import Counter
    print(f"position_kind distribution: {Counter(kinds)}")
    print(f"bill_class distribution: {Counter(classes)}")


if __name__ == "__main__":
    main()
