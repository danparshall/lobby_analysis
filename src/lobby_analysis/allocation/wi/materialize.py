"""Materialize the WI allocation matrix to TSV.

Reads the release directly, builds the graph + runs IPF per semester,
and writes one TSV per semester with columns:

    lobbyist_id  principal_id  hours_comm  hours_other  confidence

This is the contract that Phase 3 (chain composition) consumes.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from lobby_analysis.allocation.wi.graph import build_bipartite_graph
from lobby_analysis.allocation.wi.ipf import fit_all
from lobby_analysis.allocation.wi.load import (
    load_active_edges,
    load_lobbyist_totals,
    load_principal_totals,
)

__all__ = ["materialize_allocation_matrix"]

# Only the two semesters where principal-side filings exist (lobbyist
# 2026-H1/H2 cells are zero-fill forward-look per Phase 0 audit).
_SEMESTERS: list[tuple[str, str]] = [
    ("2025-H1", "WI_lobbyist_principal_hours_h1_2025.tsv"),
    ("2025-H2", "WI_lobbyist_principal_hours_h2_2025.tsv"),
]


def materialize_allocation_matrix(
    release_dir: Path,
    output_dir: Path,
) -> None:
    """Run the per-semester graph + IPF + materialize sequence, writing
    one TSV per semester to ``output_dir``.

    Output schema (in order):
        lobbyist_id   int
        principal_id  int
        hours_comm    float
        hours_other   float
        confidence    str ∈ {exact, ipf_fit, zero_filed,
                              aggregation_flagged}
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    for semester, filename in _SEMESTERS:
        edges = load_active_edges(release_dir, semester)
        p_totals = load_principal_totals(release_dir, semester)
        l_totals = load_lobbyist_totals(release_dir, semester)
        graph = build_bipartite_graph(
            edges=edges, principal_totals=p_totals, lobbyist_totals=l_totals
        )
        matrix = fit_all(graph)

        rows: list[dict] = []
        for (lid, pid), cell in matrix.cells.items():
            rows.append(
                {
                    "lobbyist_id": int(lid),
                    "principal_id": int(pid),
                    "hours_comm": float(cell.hours_comm),
                    "hours_other": float(cell.hours_other),
                    "confidence": cell.confidence,
                }
            )
        df = pd.DataFrame(rows, columns=[
            "lobbyist_id", "principal_id",
            "hours_comm", "hours_other", "confidence",
        ])
        # Deterministic ordering: by (lobbyist_id, principal_id)
        df = df.sort_values(["lobbyist_id", "principal_id"]).reset_index(drop=True)
        df.to_csv(output_dir / filename, sep="\t", index=False)
