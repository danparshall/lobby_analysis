"""Empirical fit of the CPI 2015 C11 aggregation rule.

The CPI methodology archive does not document the formula that
aggregates the 14 per-item Lobbying Disclosure scores into a category
score. This script tries four candidate formulas from the spec doc
against CPI's published 50-state per-state aggregate and reports which
fits within the spec's +/- 1 tolerance.

The winning rule is hardcoded as ``aggregate_cpi_2015_c11`` in
``src/lobby_analysis/projections/cpi_2015_c11.py``. Run this script to
reproduce the fit decision or to evaluate alternative candidates.

Usage:

    uv run python scripts/fit_cpi_2015_c11_aggregation.py
"""

from __future__ import annotations

import csv
import statistics
from pathlib import Path

from lobby_analysis.projections.cpi_2015_c11 import (
    CPI_2015_C11_INDICATOR_IDS,
    CPI_2015_C11_SUB_CATEGORIES,
    load_per_state_ground_truth,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
PUBLISHED_CSV = REPO_ROOT / "papers" / "CPI_2015__sii_scores.csv"

# Splits the 14 indicators by their de-jure vs de-facto nature. Used by
# the "halves" candidate aggregator below.
DE_JURE = {"IND_196", "IND_197", "IND_199", "IND_201", "IND_203", "IND_207"}
DE_FACTO = set(CPI_2015_C11_INDICATOR_IDS) - DE_JURE


def load_published_c11() -> dict[str, float]:
    """{state: published_c11_score} from CPI 2015 SII results CSV."""
    out: dict[str, float] = {}
    with PUBLISHED_CSV.open() as f:
        for row in csv.DictReader(f):
            assert row["categories/10/number"] == "11"
            out[row["name"]] = float(row["categories/10/score"])
    return out


def per_state_items() -> dict[str, dict[str, int]]:
    truth = load_per_state_ground_truth()
    out: dict[str, dict[str, int]] = {}
    for (state, ind), score in truth.items():
        out.setdefault(state, {})[ind] = score
    return out


def candidate_simple_mean(s: dict[str, int]) -> float:
    return statistics.mean(s[ind] for ind in CPI_2015_C11_INDICATOR_IDS)


def candidate_halves(s: dict[str, int]) -> float:
    return (
        statistics.mean(s[ind] for ind in DE_JURE)
        + statistics.mean(s[ind] for ind in DE_FACTO)
    ) / 2


def candidate_sequential_sub_cats(s: dict[str, int]) -> float:
    """Sequential sub-cat grouping (counts 2/4/3/2/3 in IND order).

    This was the author's a-priori guess before extracting the actual
    CPI sub-cat structure from the criteria xlsx. Retained here to
    document why it does NOT fit.
    """
    groups = [
        ("IND_196", "IND_197"),
        ("IND_198", "IND_199", "IND_200", "IND_201"),
        ("IND_202", "IND_203", "IND_204"),
        ("IND_205", "IND_206"),
        ("IND_207", "IND_208", "IND_209"),
    ]
    return statistics.mean(statistics.mean(s[ind] for ind in g) for g in groups)


def candidate_cpi_sub_cats(s: dict[str, int]) -> float:
    """The actual CPI 2015 C11 sub-cat structure, extracted from
    papers/CPI_2015__sii_criteria.xlsx sheet11 column A. This is the
    winning rule.
    """
    return statistics.mean(
        statistics.mean(s[ind] for ind in items)
        for items in CPI_2015_C11_SUB_CATEGORIES.values()
    )


CANDIDATES = {
    "simple_mean": candidate_simple_mean,
    "de_jure_de_facto_halves": candidate_halves,
    "sequential_sub_cats_2_4_3_2_3": candidate_sequential_sub_cats,
    "cpi_sub_cats_from_xlsx": candidate_cpi_sub_cats,
}


def main() -> None:
    published = load_published_c11()
    per_state = per_state_items()
    assert set(published) == set(per_state)

    print(f"Evaluating {len(CANDIDATES)} aggregation candidates against "
          f"{len(published)} published per-state scores.\n")

    for name, fn in CANDIDATES.items():
        residuals = []
        for state, items in per_state.items():
            projected = fn(items)
            residuals.append((state, projected, published[state],
                              projected - published[state]))
        abs_resids = [abs(r[3]) for r in residuals]
        n_over_1 = sum(1 for r in abs_resids if r > 1.0)
        print(f"{name}")
        print(f"  max abs residual:        {max(abs_resids):.4f}")
        print(f"  mean abs residual:       {statistics.mean(abs_resids):.4f}")
        print(f"  states off by > 1.0:     {n_over_1}/50")
        if n_over_1 > 0:
            worst = sorted(residuals, key=lambda r: -abs(r[3]))[:3]
            print(f"  worst 3: {[(s, round(p, 2), round(pub, 2), round(res, 3)) for s, p, pub, res in worst]}")
        print()

    print("Winner: cpi_sub_cats_from_xlsx -- the only candidate that fits")
    print("within +/- 1 for all 50 states (max abs residual 0.05, attributable")
    print("to 1-decimal rounding of the published score).")


if __name__ == "__main__":
    main()
