"""TDD tests for the WI allocation-matrix IPF fit (Phase 2.2 of
plans/wi_allocation_matrix.md).

Design decisions locked at the Phase 2 boundary (see
convos/20260531_phase_2_ipf_design.md, anticipated):

- ``fit_component(component, hours_type) -> ComponentFit`` runs ipfn on
  ONE FreeComponent for one of {"hours_comm", "hours_other"}. The seed
  matrix is 1.0 on edges, 0.0 elsewhere — the bipartite support pattern
  is preserved through every iteration (empirically verified: zero seed
  cells stay at exactly 0.0).
- Marginals are taken as-is. No Pettack-style marginal surgery: Pettack
  sits in her own 6x6 CC where the marginals balance natively (730.2
  hrs comm both sides; 3454.5 vs 3466.8 other), and ipfn converges
  cleanly. Cells in flagged-lobbyist rows are labeled with
  confidence='aggregation_flagged' at materialize time, not by altering
  the fit.
- Zero-marginal lobbyists/principals stay in the fit (their rows/cols
  go to 0 by IPF construction). Within-CC aggregate row residual ~1.3%
  comm / 2.8% other is accepted as a data-quality fixture, not a fit
  failure. Per-row residual is reported in the writeup, not asserted.

Reference: ipfn library, https://pypi.org/project/ipfn/. The API is
``ipfn.ipfn(seed, [row_targets, col_targets], [[0], [1]],
convergence_rate=1e-6, max_iteration=500).iteration()`` returning the
fit matrix in place (or (matrix, converged_flag) if verbose=1).
"""

from __future__ import annotations

from pathlib import Path

import numpy as np

from lobby_analysis.allocation.wi.graph import (
    FreeComponent,
    build_bipartite_graph,
    classify_components,
    connected_components,
)
from lobby_analysis.allocation.wi.ipf import (  # noqa: F401 — drives RED
    AllocationMatrix,
    ComponentFit,
    fit_all,
    fit_component,
)
from lobby_analysis.allocation.wi.load import (
    load_active_edges,
    load_lobbyist_totals,
    load_principal_totals,
)

_REPO_ROOT = Path(__file__).resolve().parents[1]
RELEASE_DIR = _REPO_ROOT / "releases" / "wi"


# ---------------------------------------------------------------------------
# Toy graphs — IPF convergence on hand-constructed marginals
# ---------------------------------------------------------------------------


def test_fit_component_2x2_full_support():
    """Toy 2x2 with full support and balanced marginals — IPF converges
    to the unique max-entropy solution.

        cols:     P100  P200
        L1  (10)   x     y    → x + y = 10
        L2  (20)   z     w    → z + w = 20

        col sums: 12    18    → x + z = 12, y + w = 18

    Closed-form max-entropy (full support, balanced): the IPF starting
    from uniform seed converges to the outer product (l*p)/total.
        x = 10 * 12 / 30 = 4
        y = 10 * 18 / 30 = 6
        z = 20 * 12 / 30 = 8
        w = 20 * 18 / 30 = 12
    """
    fc = FreeComponent(
        edges=frozenset({(1, 100), (1, 200), (2, 100), (2, 200)}),
        principal_totals={100: (12.0, 0.0), 200: (18.0, 0.0)},
        lobbyist_totals={1: (10.0, 0.0), 2: (20.0, 0.0)},
    )
    fit = fit_component(fc, hours_type="hours_comm")
    # The output should be addressable as fit.cells[(lobbyist_id, principal_id)]
    assert abs(fit.cells[(1, 100)] - 4.0) < 1e-4
    assert abs(fit.cells[(1, 200)] - 6.0) < 1e-4
    assert abs(fit.cells[(2, 100)] - 8.0) < 1e-4
    assert abs(fit.cells[(2, 200)] - 12.0) < 1e-4


def test_fit_component_sparse_zero_stays_zero():
    """Toy 3x3 with one missing edge — that cell stays at exactly 0.

        cols:     P100  P200  P300
        L1  (10)   x     y     0    (no edge L1-P300)
        L2  (20)   0     z     w    (no edge L2-P100)
        L3  (15)   0     0     v    (no edge L3-P100, L3-P200)

        col sums: 5     18    22

    The support-pattern encoding (zero seed → zero fit) is the
    mechanism by which the bipartite edge structure carries through
    the IPF without explicit constraint handling.
    """
    fc = FreeComponent(
        edges=frozenset({(1, 100), (1, 200), (2, 200), (2, 300), (3, 300)}),
        principal_totals={100: (5.0, 0.0), 200: (18.0, 0.0), 300: (22.0, 0.0)},
        lobbyist_totals={1: (10.0, 0.0), 2: (20.0, 0.0), 3: (15.0, 0.0)},
    )
    fit = fit_component(fc, hours_type="hours_comm")
    # No edge → cell must NOT be in the output (or must be exactly 0).
    assert (1, 300) not in fit.cells or fit.cells[(1, 300)] == 0.0
    assert (2, 100) not in fit.cells or fit.cells[(2, 100)] == 0.0
    assert (3, 100) not in fit.cells or fit.cells[(3, 100)] == 0.0
    assert (3, 200) not in fit.cells or fit.cells[(3, 200)] == 0.0


def test_fit_component_residuals_under_tolerance_when_balanced():
    """When marginals balance, per-row and per-col residuals are both
    tight (< 1e-4 relative)."""
    fc = FreeComponent(
        edges=frozenset({(1, 100), (1, 200), (2, 100), (2, 200)}),
        principal_totals={100: (12.0, 0.0), 200: (18.0, 0.0)},
        lobbyist_totals={1: (10.0, 0.0), 2: (20.0, 0.0)},
    )
    fit = fit_component(fc, hours_type="hours_comm")
    # Lobbyist row sums
    assert abs(fit.cells[(1, 100)] + fit.cells[(1, 200)] - 10.0) < 1e-4
    assert abs(fit.cells[(2, 100)] + fit.cells[(2, 200)] - 20.0) < 1e-4
    # Principal col sums
    assert abs(fit.cells[(1, 100)] + fit.cells[(2, 100)] - 12.0) < 1e-4
    assert abs(fit.cells[(1, 200)] + fit.cells[(2, 200)] - 18.0) < 1e-4


def test_fit_component_zero_marginal_row_yields_zero_cells():
    """If lobbyist 2 has 0 hours_comm marginal, all of her cells must
    be 0 in the fit — IPF constructively zeros the row."""
    fc = FreeComponent(
        edges=frozenset({(1, 100), (1, 200), (2, 100), (2, 200)}),
        principal_totals={100: (5.0, 0.0), 200: (5.0, 0.0)},
        lobbyist_totals={1: (10.0, 0.0), 2: (0.0, 0.0)},
    )
    fit = fit_component(fc, hours_type="hours_comm")
    assert fit.cells.get((2, 100), 0.0) == 0.0
    assert fit.cells.get((2, 200), 0.0) == 0.0


def test_fit_component_nonneg_cells():
    """All output cells are nonneg."""
    fc = FreeComponent(
        edges=frozenset({(1, 100), (1, 200), (2, 100), (2, 200), (2, 300)}),
        principal_totals={100: (12.0, 0.0), 200: (18.0, 0.0), 300: (5.0, 0.0)},
        lobbyist_totals={1: (10.0, 0.0), 2: (25.0, 0.0)},
    )
    fit = fit_component(fc, hours_type="hours_comm")
    for v in fit.cells.values():
        assert v >= 0.0


def test_fit_component_hours_type_axis():
    """``hours_type='hours_other'`` reads the second element of the
    marginal tuples instead of the first."""
    fc = FreeComponent(
        edges=frozenset({(1, 100), (1, 200), (2, 100), (2, 200)}),
        principal_totals={100: (1.0, 12.0), 200: (1.0, 18.0)},
        lobbyist_totals={1: (1.0, 10.0), 2: (1.0, 20.0)},
    )
    fit = fit_component(fc, hours_type="hours_other")
    # Same arithmetic as the comm test, just sourced from the other axis
    assert abs(fit.cells[(1, 100)] - 4.0) < 1e-4
    assert abs(fit.cells[(2, 200)] - 12.0) < 1e-4


def test_fit_component_reports_iterations_and_converged():
    """ComponentFit exposes ``iterations`` and ``converged`` so the
    writeup can report convergence behavior."""
    fc = FreeComponent(
        edges=frozenset({(1, 100), (1, 200), (2, 100), (2, 200)}),
        principal_totals={100: (12.0, 0.0), 200: (18.0, 0.0)},
        lobbyist_totals={1: (10.0, 0.0), 2: (20.0, 0.0)},
    )
    fit = fit_component(fc, hours_type="hours_comm")
    assert fit.iterations >= 1
    assert fit.converged is True


# ---------------------------------------------------------------------------
# Real-data: giant CC and Pettack CC
# ---------------------------------------------------------------------------


def _load_h1_2025_graph():
    edges = load_active_edges(RELEASE_DIR, "2025-H1")
    p_totals = load_principal_totals(RELEASE_DIR, "2025-H1")
    l_totals = load_lobbyist_totals(RELEASE_DIR, "2025-H1")
    return build_bipartite_graph(
        edges=edges, principal_totals=p_totals, lobbyist_totals=l_totals
    )


def test_fit_giant_cc_converges_under_iteration_budget():
    """The H1 2025 giant CC (312 lobbyists x 523 principals, 1441
    edges) converges within the 500-iteration budget."""
    graph = _load_h1_2025_graph()
    _, free = classify_components(connected_components(graph))
    giant = max(free, key=lambda c: len(c.edges))
    fit = fit_component(giant, hours_type="hours_comm")
    assert fit.converged is True
    assert fit.iterations <= 500


def test_fit_giant_cc_col_residual_tight():
    """Per-column residual is tight (< 1e-3 relative) on the giant CC —
    ipfn's last sweep is the col sweep, so column constraints are
    satisfied exactly modulo float precision."""
    graph = _load_h1_2025_graph()
    _, free = classify_components(connected_components(graph))
    giant = max(free, key=lambda c: len(c.edges))
    fit = fit_component(giant, hours_type="hours_comm")
    col_sums: dict[int, float] = {}
    for (lid, pid), v in fit.cells.items():
        col_sums[pid] = col_sums.get(pid, 0.0) + v
    for pid, target in giant.principal_totals.items():
        if target[0] > 0:
            assert abs(col_sums.get(pid, 0.0) / target[0] - 1) < 1e-3


def test_fit_giant_cc_aggregate_row_residual_under_5pct():
    """Aggregate row residual is small: total of fit row sums vs total
    of row targets within 5% — empirical reality is 1.3% comm / 2.8%
    other on the giant CC, both well inside."""
    graph = _load_h1_2025_graph()
    _, free = classify_components(connected_components(graph))
    giant = max(free, key=lambda c: len(c.edges))
    fit_comm = fit_component(giant, hours_type="hours_comm")
    fit_other = fit_component(giant, hours_type="hours_other")

    def _row_residual(fit, totals, axis):
        fit_total = sum(fit.cells.values())
        target_total = sum(t[axis] for t in totals.values())
        return abs(fit_total / target_total - 1) if target_total > 0 else 0.0

    assert _row_residual(fit_comm, giant.lobbyist_totals, 0) < 0.05
    assert _row_residual(fit_other, giant.lobbyist_totals, 1) < 0.05


def test_fit_giant_cc_zero_marginal_rows_fit_zero():
    """Lobbyists in the giant CC with zero hours_comm marginal have
    fit_sum exactly 0 — IPF clamps them at 0 by construction."""
    graph = _load_h1_2025_graph()
    _, free = classify_components(connected_components(graph))
    giant = max(free, key=lambda c: len(c.edges))
    fit = fit_component(giant, hours_type="hours_comm")
    row_sums: dict[int, float] = {}
    for (lid, pid), v in fit.cells.items():
        row_sums[lid] = row_sums.get(lid, 0.0) + v
    zero_lobs = [
        lid for lid, t in giant.lobbyist_totals.items() if t[0] == 0.0
    ]
    assert len(zero_lobs) > 0  # sanity — there are 40 in H1 2025
    for lid in zero_lobs:
        assert row_sums.get(lid, 0.0) == 0.0


def test_fit_giant_cc_seed_pattern_preserved():
    """No fit cell exists for a non-edge pair in the giant CC — the
    bipartite support pattern is enforced by the zero seed encoding."""
    graph = _load_h1_2025_graph()
    _, free = classify_components(connected_components(graph))
    giant = max(free, key=lambda c: len(c.edges))
    fit = fit_component(giant, hours_type="hours_comm")
    # Every fit cell's key must correspond to a real edge.
    for (lid, pid) in fit.cells:
        assert (lid, pid) in giant.edges


def test_fit_pettack_cc_converges_with_marginals_as_is():
    """Pettack's 6x6 CC has internally-balanced marginals (730.2 comm
    both sides). The fit converges without any marginal surgery."""
    graph = _load_h1_2025_graph()
    _, free = classify_components(connected_components(graph))
    pettack_cc = next(
        c for c in free if 11072 in {lid for (lid, _) in c.edges}
    )
    fit = fit_component(pettack_cc, hours_type="hours_comm")
    assert fit.converged is True


def test_fit_pettack_cc_assigns_most_hours_to_pettack():
    """Pettack's row sum in the fit reflects her dominant marginal
    contribution: her 651 H1 hours_comm out of the CC's 730.2 total
    means her fit-row-sum is ~651 (~89% of the CC's total cells)."""
    graph = _load_h1_2025_graph()
    _, free = classify_components(connected_components(graph))
    pettack_cc = next(
        c for c in free if 11072 in {lid for (lid, _) in c.edges}
    )
    fit = fit_component(pettack_cc, hours_type="hours_comm")
    pettack_row_sum = sum(v for (lid, _), v in fit.cells.items() if lid == 11072)
    # Within 1% of her reported marginal
    assert abs(pettack_row_sum - 651.0) < 7.0


# ---------------------------------------------------------------------------
# fit_all — orchestration over all components × hours-types
# ---------------------------------------------------------------------------


def test_fit_all_returns_allocation_matrix_for_h1_2025():
    """fit_all consumes the H1 2025 graph and returns an
    AllocationMatrix covering every edge with a confidence label."""
    graph = _load_h1_2025_graph()
    matrix = fit_all(graph)
    # Every edge in the graph has a cell in the output.
    for edge in graph.edges:
        assert edge in matrix.cells


def test_fit_all_exact_cells_match_marginals():
    """Edges in singleton (exactly-pinned) CCs round-trip exactly: the
    cell value equals the lobbyist's reported marginal."""
    graph = _load_h1_2025_graph()
    matrix = fit_all(graph)
    pinned, _ = classify_components(connected_components(graph))
    for ep in pinned:
        cell = matrix.cells[(ep.lobbyist_id, ep.principal_id)]
        assert cell.hours_comm == ep.hours_comm
        assert cell.hours_other == ep.hours_other
        assert cell.confidence == "exact"


def test_fit_all_zero_marginal_lobbyists_get_zero_filed_label():
    """Cells in the rows of zero-marginal lobbyists (in free CCs)
    materialize as (0.0, 0.0, 'zero_filed') — Dan's call: preserve
    them in the output so downstream comparisons can surface 'principal
    paid but lobbyist didn't file' patterns."""
    graph = _load_h1_2025_graph()
    matrix = fit_all(graph)
    _, free = classify_components(connected_components(graph))
    # Find a free CC with at least one zero-comm-and-other-marginal lobbyist
    for fc in free:
        zero_lobs = [
            lid for lid, t in fc.lobbyist_totals.items()
            if t[0] == 0.0 and t[1] == 0.0
        ]
        if not zero_lobs:
            continue
        zlob = zero_lobs[0]
        # Find an edge for this lobbyist
        cell_keys = [(l, p) for (l, p) in fc.edges if l == zlob]
        if not cell_keys:
            continue
        cell = matrix.cells[cell_keys[0]]
        assert cell.hours_comm == 0.0
        assert cell.hours_other == 0.0
        assert cell.confidence == "zero_filed"
        return
    raise AssertionError("expected at least one zero-marginal lobbyist in free CCs")


def test_fit_all_pettack_cells_labeled_aggregation_flagged():
    """Cells in Pettack's row materialize with
    confidence='aggregation_flagged' (per the flag_outliers list)."""
    graph = _load_h1_2025_graph()
    matrix = fit_all(graph)
    pettack_cells = [
        cell for (lid, _), cell in matrix.cells.items() if lid == 11072
    ]
    assert len(pettack_cells) > 0
    for cell in pettack_cells:
        assert cell.confidence == "aggregation_flagged"


def test_fit_all_emits_ipf_fit_confidence_for_free_nonzero():
    """Cells in free CCs with nonzero lobbyist marginals get
    confidence='ipf_fit' (unless overridden by aggregation_flagged or
    zero_filed)."""
    graph = _load_h1_2025_graph()
    matrix = fit_all(graph)
    # Spot-check: there must be at least some 'ipf_fit' cells
    n_ipf_fit = sum(
        1 for cell in matrix.cells.values() if cell.confidence == "ipf_fit"
    )
    assert n_ipf_fit > 100  # giant CC alone has > 1000 such cells


def test_fit_all_confidence_distribution_covers_all_labels():
    """Every materialized cell has one of the four documented
    confidence labels."""
    graph = _load_h1_2025_graph()
    matrix = fit_all(graph)
    valid = {"exact", "ipf_fit", "zero_filed", "aggregation_flagged"}
    for cell in matrix.cells.values():
        assert cell.confidence in valid
