#!/usr/bin/env python3
"""Quick per-indicator score distribution for Sunlight 2015 CSV.

Strips footnote markers (*, **, ^, ^^) so distributions reflect base tiers.
"""
from collections import Counter
from pathlib import Path
import csv
import re

CSV = Path("papers/Sunlight_2015__state_lobbying_disclosure_scorecard_data.csv")


def clean(score: str) -> str:
    """Strip footnote markers; return the bare integer string."""
    return re.sub(r"[*^]+", "", score).strip()


def main() -> None:
    score_cols = [
        "Lobbyist Activity",
        "Expenditure Transparency",
        "Expenditure Reporting Thresholds",
        "Document Accessibility",
        "Lobbyist Compensation",
    ]
    counts: dict[str, Counter[str]] = {c: Counter() for c in score_cols}
    n_rows = 0
    with CSV.open() as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            n_rows += 1
            for col in score_cols:
                counts[col][clean(row[col])] += 1

    print(f"# Sunlight 2015 per-indicator distributions  (N={n_rows} states)\n")
    for col in score_cols:
        ordered = sorted(counts[col].items(), key=lambda kv: int(kv[0]))
        line = "  ".join(f"{score}={n}" for score, n in ordered)
        print(f"- **{col}**: {line}")


if __name__ == "__main__":
    main()
