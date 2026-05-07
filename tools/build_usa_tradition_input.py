#!/usr/bin/env python3
"""Build the 9-rubric USA-tradition input for the 3-way consensus run.

Reads:
  results/cross_rubric_items_clustered.csv  (8 non-PRI rubrics, atomic)
  results/items_PRI_2010.tsv                (PRI 83 atomic items)

Filters CPI_2015 to lobbying-disclosure rows only (C11) per the
plan's CPI scoping decision; the other 12 categories + 3 sub-questions
are out of project scope.

Writes:
  results/3way_consensus/usa_tradition_items.csv
  Columns: paper, indicator_id, indicator_text, section
"""
from pathlib import Path

import pandas as pd

ROOT = Path("docs/active/compendium-source-extracts/results")
USA_NON_PRI = [
    "HiredGuns",
    "FOCAL",
    "Newmark2017",
    "Newmark2005",
    "Opheim",
    "OpenSecrets",
    "Sunlight",
    "CPI_2015",
]
CPI_IN_SCOPE_IDS = ["C11"]


def main() -> None:
    df = pd.read_csv(ROOT / "cross_rubric_items_clustered.csv")
    df = df[df["paper"].isin(USA_NON_PRI)].copy()

    cpi_mask = df["paper"] == "CPI_2015"
    df = df[~cpi_mask | df["indicator_id"].isin(CPI_IN_SCOPE_IDS)].copy()

    df_min = df[["paper", "indicator_id", "indicator_text", "section"]].copy()

    pri = pd.read_csv(ROOT / "items_PRI_2010.tsv", sep="\t")
    pri = pri.rename(columns={"paper_id": "paper", "section_or_category": "section"})
    pri_min = pri[["paper", "indicator_id", "indicator_text", "section"]].copy()

    out = pd.concat([df_min, pri_min], ignore_index=True)

    print("Counts by paper:")
    print(out["paper"].value_counts().sort_index())
    print(f"\nTotal: {len(out)} items")

    dup_mask = out.duplicated(subset=["paper", "indicator_id"], keep=False)
    if dup_mask.any():
        print("\nDUPLICATE (paper, indicator_id) pairs found:")
        print(out[dup_mask].to_string())
        raise SystemExit("duplicate (paper, indicator_id)")

    out_path = ROOT / "3way_consensus" / "usa_tradition_items.csv"
    out_path.parent.mkdir(exist_ok=True)
    out.to_csv(out_path, index=False)
    print(f"\nWrote {out_path}")


if __name__ == "__main__":
    main()
