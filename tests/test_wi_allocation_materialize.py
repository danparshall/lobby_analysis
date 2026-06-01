"""TDD tests for the WI allocation-matrix materialize step (Phase 2.3
of plans/wi_allocation_matrix.md).

The materialize step takes the AllocationMatrix from ``fit_all`` and
writes a TSV with one row per (lobbyist_id, principal_id) edge:

    lobbyist_id  principal_id  hours_comm  hours_other  confidence

One file per semester. Used downstream as the contract for the chain
composition in Phase 3.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from lobby_analysis.allocation.wi.graph import (
    build_bipartite_graph,
    classify_components,
    connected_components,
)
from lobby_analysis.allocation.wi.ipf import fit_all
from lobby_analysis.allocation.wi.load import (
    load_active_edges,
    load_lobbyist_totals,
    load_principal_totals,
)
from lobby_analysis.allocation.wi.materialize import (  # noqa: F401 — drives RED
    materialize_allocation_matrix,
)

_REPO_ROOT = Path(__file__).resolve().parents[1]
RELEASE_DIR = _REPO_ROOT / "releases" / "wi"


def test_materialize_writes_one_file_per_semester(tmp_path: Path):
    """``materialize_allocation_matrix(release_dir, output_dir)``
    produces ``WI_lobbyist_principal_hours_h1_2025.tsv`` and
    ``WI_lobbyist_principal_hours_h2_2025.tsv`` in the output dir."""
    materialize_allocation_matrix(RELEASE_DIR, tmp_path)
    assert (tmp_path / "WI_lobbyist_principal_hours_h1_2025.tsv").exists()
    assert (tmp_path / "WI_lobbyist_principal_hours_h2_2025.tsv").exists()


def test_materialize_schema_correct(tmp_path: Path):
    """The output TSV has exactly the documented columns in the
    documented order."""
    materialize_allocation_matrix(RELEASE_DIR, tmp_path)
    df = pd.read_csv(
        tmp_path / "WI_lobbyist_principal_hours_h1_2025.tsv", sep="\t"
    )
    assert list(df.columns) == [
        "lobbyist_id",
        "principal_id",
        "hours_comm",
        "hours_other",
        "confidence",
    ]


def test_materialize_row_count_matches_edge_count_h1_2025(tmp_path: Path):
    """Every active edge in H1 2025 produces exactly one row in the
    H1 file (no duplicates, no missing edges)."""
    edges = load_active_edges(RELEASE_DIR, "2025-H1")
    materialize_allocation_matrix(RELEASE_DIR, tmp_path)
    df = pd.read_csv(
        tmp_path / "WI_lobbyist_principal_hours_h1_2025.tsv", sep="\t"
    )
    assert len(df) == len(edges)
    # No duplicates: every (lobbyist_id, principal_id) pair is unique
    assert df[["lobbyist_id", "principal_id"]].duplicated().sum() == 0


def test_materialize_pinned_cells_round_trip_h1_2025(tmp_path: Path):
    """Exactly-pinned cells in the output match the lobbyist marginals
    that produced them — sanity check that the materialize step doesn't
    distort what the graph layer reported."""
    edges = load_active_edges(RELEASE_DIR, "2025-H1")
    p_totals = load_principal_totals(RELEASE_DIR, "2025-H1")
    l_totals = load_lobbyist_totals(RELEASE_DIR, "2025-H1")
    g = build_bipartite_graph(
        edges=edges, principal_totals=p_totals, lobbyist_totals=l_totals
    )
    pinned, _ = classify_components(connected_components(g))
    materialize_allocation_matrix(RELEASE_DIR, tmp_path)
    df = pd.read_csv(
        tmp_path / "WI_lobbyist_principal_hours_h1_2025.tsv", sep="\t"
    )
    # Spot-check 3 pinned cells
    for ep in pinned[:3]:
        row = df[
            (df["lobbyist_id"] == ep.lobbyist_id)
            & (df["principal_id"] == ep.principal_id)
        ]
        assert len(row) == 1
        assert row.iloc[0]["confidence"] == "exact"
        assert abs(row.iloc[0]["hours_comm"] - ep.hours_comm) < 1e-6
        assert abs(row.iloc[0]["hours_other"] - ep.hours_other) < 1e-6


def test_materialize_confidence_distribution_h1_2025(tmp_path: Path):
    """All 4 confidence labels appear in the H1 2025 output (the data
    is rich enough that every category is populated)."""
    materialize_allocation_matrix(RELEASE_DIR, tmp_path)
    df = pd.read_csv(
        tmp_path / "WI_lobbyist_principal_hours_h1_2025.tsv", sep="\t"
    )
    labels = set(df["confidence"].unique())
    assert "exact" in labels
    assert "ipf_fit" in labels
    assert "zero_filed" in labels
    assert "aggregation_flagged" in labels


def test_materialize_pettack_cells_aggregation_flagged(tmp_path: Path):
    """Every cell in Pettack's row (lobbyist 11072) carries the
    ``aggregation_flagged`` label in both semesters."""
    materialize_allocation_matrix(RELEASE_DIR, tmp_path)
    for semester_file in (
        "WI_lobbyist_principal_hours_h1_2025.tsv",
        "WI_lobbyist_principal_hours_h2_2025.tsv",
    ):
        df = pd.read_csv(tmp_path / semester_file, sep="\t")
        pet = df[df["lobbyist_id"] == 11072]
        assert len(pet) > 0
        assert (pet["confidence"] == "aggregation_flagged").all()


def test_materialize_nonneg_hours(tmp_path: Path):
    """No negative hour values in the output."""
    materialize_allocation_matrix(RELEASE_DIR, tmp_path)
    df = pd.read_csv(
        tmp_path / "WI_lobbyist_principal_hours_h1_2025.tsv", sep="\t"
    )
    assert (df["hours_comm"] >= 0).all()
    assert (df["hours_other"] >= 0).all()
