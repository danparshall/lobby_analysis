"""TDD tests for the WI allocation-matrix bipartite graph + connected
components.

Phase 1.3 of plans/wi_allocation_matrix.md. The graph layer consumes
loader output ((edges, principal_totals, lobbyist_totals)) and exposes:

    build_bipartite_graph(edges, principal_totals, lobbyist_totals)
        -> BipartiteGraph
    connected_components(graph)
        -> list[Component]                   (each Component holds its
                                              sub-edges + sub-marginals)
    classify_components(components)
        -> tuple[list[ExactlyPinned],        (singleton-edge: one edge,
                 list[FreeComponent]]         one lobbyist, one principal —
                                              cell value is structurally
                                              determined by the marginals;
                                              IPF not needed)
                                             (everything else: free, IPF
                                              will fit max-entropy)
    flag_outliers(graph)
        -> list[OutlierFlag]                 (lobbyists whose marginal
                                              hours implausibly exceed
                                              the sum of attributable
                                              principal hours — Pettack-
                                              class data-entry pattern)

Tests include hand-constructed toy graphs (no I/O) AND real-data
spot-checks against the H1 2025 release. Expected counts come from
the Phase 0 audit doc.
"""

from __future__ import annotations

from pathlib import Path

from lobby_analysis.allocation.wi.graph import (  # noqa: F401 — drives RED
    BipartiteGraph,
    build_bipartite_graph,
    classify_components,
    connected_components,
    flag_outliers,
)
from lobby_analysis.allocation.wi.load import (
    load_active_edges,
    load_lobbyist_totals,
    load_principal_totals,
)

_REPO_ROOT = Path(__file__).resolve().parents[1]
RELEASE_DIR = _REPO_ROOT / "releases" / "wi"


# ---------------------------------------------------------------------------
# Toy graphs — no I/O, deterministic
# ---------------------------------------------------------------------------


def test_empty_graph_has_no_components():
    g = build_bipartite_graph(edges=set(), principal_totals={}, lobbyist_totals={})
    assert connected_components(g) == []


def test_single_edge_is_one_component():
    """One lobbyist authorized by one principal → one connected
    component of size 2 (one lobbyist node + one principal node)."""
    g = build_bipartite_graph(
        edges={(1, 100)},
        principal_totals={100: (10.0, 20.0)},
        lobbyist_totals={1: (10.0, 20.0)},
    )
    components = connected_components(g)
    assert len(components) == 1


def test_two_isolated_edges_are_two_components():
    """Two lobbyist-principal pairs with no shared node → two
    components, each of size 2."""
    g = build_bipartite_graph(
        edges={(1, 100), (2, 200)},
        principal_totals={100: (10.0, 20.0), 200: (5.0, 7.0)},
        lobbyist_totals={1: (10.0, 20.0), 2: (5.0, 7.0)},
    )
    components = connected_components(g)
    assert len(components) == 2


def test_shared_principal_merges_components():
    """Two lobbyists authorized by the same principal → one component
    of size 3 (two lobbyists + one principal)."""
    g = build_bipartite_graph(
        edges={(1, 100), (2, 100)},
        principal_totals={100: (15.0, 27.0)},
        lobbyist_totals={1: (10.0, 20.0), 2: (5.0, 7.0)},
    )
    components = connected_components(g)
    assert len(components) == 1


def test_shared_lobbyist_merges_components():
    """One lobbyist authorized by two principals → one component."""
    g = build_bipartite_graph(
        edges={(1, 100), (1, 200)},
        principal_totals={100: (3.0, 5.0), 200: (7.0, 15.0)},
        lobbyist_totals={1: (10.0, 20.0)},
    )
    components = connected_components(g)
    assert len(components) == 1


def test_components_cover_all_nodes_and_edges():
    """Decomposition preserves: total node count + total edge count."""
    g = build_bipartite_graph(
        edges={(1, 100), (2, 100), (3, 200), (4, 300), (4, 400)},
        principal_totals={
            100: (15.0, 27.0),
            200: (5.0, 7.0),
            300: (1.0, 1.0),
            400: (2.0, 2.0),
        },
        lobbyist_totals={
            1: (10.0, 20.0),
            2: (5.0, 7.0),
            3: (5.0, 7.0),
            4: (3.0, 3.0),
        },
    )
    components = connected_components(g)
    # 3 components: {1,2,100}, {3,200}, {4,300,400}
    assert len(components) == 3
    total_edges = sum(len(c.edges) for c in components)
    assert total_edges == 5


# ---------------------------------------------------------------------------
# classify_components
# ---------------------------------------------------------------------------


def test_classify_singleton_edge_as_exactly_pinned():
    """A component with exactly 1 edge (1 lobbyist + 1 principal) is
    structurally pinned — the only cell value consistent with both
    marginals is the marginal itself."""
    g = build_bipartite_graph(
        edges={(1, 100)},
        principal_totals={100: (10.0, 20.0)},
        lobbyist_totals={1: (10.0, 20.0)},
    )
    components = connected_components(g)
    pinned, free = classify_components(components)
    assert len(pinned) == 1
    assert len(free) == 0


def test_classify_two_edge_component_as_free():
    """A component with 2 edges (e.g., 1 principal + 2 lobbyists) has
    > 1 free cell — IPF must fit it."""
    g = build_bipartite_graph(
        edges={(1, 100), (2, 100)},
        principal_totals={100: (15.0, 27.0)},
        lobbyist_totals={1: (10.0, 20.0), 2: (5.0, 7.0)},
    )
    components = connected_components(g)
    pinned, free = classify_components(components)
    assert len(pinned) == 0
    assert len(free) == 1


def test_classify_mixed_returns_both_lists():
    """Mixed component sizes split into the two output lists."""
    g = build_bipartite_graph(
        edges={(1, 100), (2, 200), (3, 200)},
        principal_totals={100: (10.0, 20.0), 200: (15.0, 27.0)},
        lobbyist_totals={1: (10.0, 20.0), 2: (5.0, 7.0), 3: (10.0, 20.0)},
    )
    components = connected_components(g)
    pinned, free = classify_components(components)
    assert len(pinned) == 1  # {1, 100}
    assert len(free) == 1    # {2, 3, 200}


def test_exactly_pinned_carries_cell_values():
    """An ExactlyPinned record exposes the cell's lobbyist_id,
    principal_id, and the pinned hours (comm + other) — these come
    from the lobbyist marginal (canonical choice; could equally come
    from the principal marginal, identical for a true singleton)."""
    g = build_bipartite_graph(
        edges={(7, 700)},
        principal_totals={700: (42.5, 100.0)},
        lobbyist_totals={7: (42.5, 100.0)},
    )
    pinned, _ = classify_components(connected_components(g))
    assert len(pinned) == 1
    p = pinned[0]
    assert p.lobbyist_id == 7
    assert p.principal_id == 700
    assert p.hours_comm == 42.5
    assert p.hours_other == 100.0


# ---------------------------------------------------------------------------
# Real H1 2025 data — node/edge counts
# ---------------------------------------------------------------------------


def test_h1_2025_graph_node_and_edge_counts():
    """Built from real H1 2025 loader output:
       - 1,912 edges
       - 632 distinct lobbyists
       - 823 distinct principals
       - 1,455 total bipartite nodes
    """
    edges = load_active_edges(RELEASE_DIR, "2025-H1")
    p_totals = load_principal_totals(RELEASE_DIR, "2025-H1")
    l_totals = load_lobbyist_totals(RELEASE_DIR, "2025-H1")
    g = build_bipartite_graph(
        edges=edges, principal_totals=p_totals, lobbyist_totals=l_totals
    )
    assert len(g.edges) == 1912
    edge_lobbyists = {l for (l, _) in g.edges}
    edge_principals = {p for (_, p) in g.edges}
    assert len(edge_lobbyists) == 632
    assert len(edge_principals) == 823


def test_h1_2025_decomposes_into_192_components():
    """H1 2025 bipartite graph decomposes into 192 components
    (Phase 0 audit)."""
    edges = load_active_edges(RELEASE_DIR, "2025-H1")
    p_totals = load_principal_totals(RELEASE_DIR, "2025-H1")
    l_totals = load_lobbyist_totals(RELEASE_DIR, "2025-H1")
    g = build_bipartite_graph(
        edges=edges, principal_totals=p_totals, lobbyist_totals=l_totals
    )
    components = connected_components(g)
    assert len(components) == 192


def test_h1_2025_giant_component_dominates():
    """The largest H1 2025 component has 835 nodes (Phase 0 audit) —
    far larger than any other (next: 33, 21, 16). The 'one giant CC'
    scenario the plan anticipated."""
    edges = load_active_edges(RELEASE_DIR, "2025-H1")
    p_totals = load_principal_totals(RELEASE_DIR, "2025-H1")
    l_totals = load_lobbyist_totals(RELEASE_DIR, "2025-H1")
    g = build_bipartite_graph(
        edges=edges, principal_totals=p_totals, lobbyist_totals=l_totals
    )
    components = connected_components(g)
    sizes = sorted(
        (len(c.lobbyist_ids) + len(c.principal_ids) for c in components),
        reverse=True,
    )
    assert sizes[0] == 835
    assert sizes[1] <= 35  # next is 33; leave a little slack


def test_h1_2025_has_122_singleton_edge_components():
    """122 components have exactly one edge — the exactly-pinned cells.
    ~6.4% of edges (122 / 1,912)."""
    edges = load_active_edges(RELEASE_DIR, "2025-H1")
    p_totals = load_principal_totals(RELEASE_DIR, "2025-H1")
    l_totals = load_lobbyist_totals(RELEASE_DIR, "2025-H1")
    g = build_bipartite_graph(
        edges=edges, principal_totals=p_totals, lobbyist_totals=l_totals
    )
    pinned, _ = classify_components(connected_components(g))
    assert len(pinned) == 122


# ---------------------------------------------------------------------------
# Outlier flagging
# ---------------------------------------------------------------------------


def test_flag_outliers_pettack_h1_2025():
    """Pettack (11072) has 4,007.5 H1 hours total (651 comm + 3,356.5
    other), implausibly high vs. the sum of her attributable principal
    hours. She must appear in the outlier-flag list."""
    edges = load_active_edges(RELEASE_DIR, "2025-H1")
    p_totals = load_principal_totals(RELEASE_DIR, "2025-H1")
    l_totals = load_lobbyist_totals(RELEASE_DIR, "2025-H1")
    g = build_bipartite_graph(
        edges=edges, principal_totals=p_totals, lobbyist_totals=l_totals
    )
    outliers = flag_outliers(g)
    flagged_lobbyists = {o.lobbyist_id for o in outliers}
    assert 11072 in flagged_lobbyists


def test_flag_outliers_handles_empty_graph():
    """No edges → no outliers."""
    g = build_bipartite_graph(edges=set(), principal_totals={}, lobbyist_totals={})
    assert flag_outliers(g) == []


def test_flag_outliers_skips_well_behaved_lobbyist():
    """A lobbyist whose marginal is plausibly explained by her
    principals' marginals is NOT flagged. Toy: lobbyist 1 works for
    principals 100+200; her 10-hr marginal fits within their 50-hr
    combined principal-side marginal."""
    g = build_bipartite_graph(
        edges={(1, 100), (1, 200)},
        principal_totals={100: (20.0, 30.0), 200: (30.0, 20.0)},
        lobbyist_totals={1: (10.0, 5.0)},
    )
    outliers = flag_outliers(g)
    assert 1 not in {o.lobbyist_id for o in outliers}


# ---------------------------------------------------------------------------
# Outlier flagging — min_hours_for_ratio_flag parameter
# ---------------------------------------------------------------------------
#
# Phase 1 surfaced 4 H1/H2 "false positive" ratio-flags: lobbyists with
# very small hours (0.2-6.0) authorized for principals whose marginals
# are 0 (low-spend-exempt). The ratio check trips trivially because the
# denominator is 0. ``min_hours_for_ratio_flag`` is a Phase 2-added knob
# that suppresses the ratio check below the threshold (default 0 = no
# suppression, preserves Phase 1 behavior; recommended 10 hrs).


def test_min_hours_default_zero_preserves_phase_1_behavior():
    """Default ``min_hours_for_ratio_flag=0`` must reproduce the Phase 1
    ratio-flag behavior exactly: lobbyist with 0.2 hrs against a
    zero-marginal principal trips the ratio check."""
    g = build_bipartite_graph(
        edges={(1, 100)},
        principal_totals={100: (0.0, 0.0)},
        lobbyist_totals={1: (0.2, 0.0)},
    )
    outliers = flag_outliers(g)
    assert 1 in {o.lobbyist_id for o in outliers}


def test_min_hours_suppresses_low_hours_ratio_flag():
    """Setting ``min_hours_for_ratio_flag=10`` suppresses the 0.2-hr
    ratio-flag false positive — the per-day absolute check is still
    in effect but doesn't trip on 0.2 hrs."""
    g = build_bipartite_graph(
        edges={(1, 100)},
        principal_totals={100: (0.0, 0.0)},
        lobbyist_totals={1: (0.2, 0.0)},
    )
    outliers = flag_outliers(g, min_hours_for_ratio_flag=10.0)
    assert 1 not in {o.lobbyist_id for o in outliers}


def test_min_hours_does_not_suppress_absolute_check():
    """``min_hours_for_ratio_flag`` only gates the ratio check.
    A lobbyist over the per-semester absolute ceiling is still flagged
    regardless of where the threshold is set, because the absolute
    check is a separate axis (per-day arithmetic)."""
    g = build_bipartite_graph(
        edges={(1, 100)},
        principal_totals={100: (1500.0, 1500.0)},
        lobbyist_totals={1: (1200.0, 1200.0)},  # 2400 > 2000 absolute ceiling
    )
    # min_hours_for_ratio_flag=10000 silences the ratio check entirely,
    # but the absolute check still trips at 2400 > 2000.
    outliers = flag_outliers(g, min_hours_for_ratio_flag=10000.0)
    assert 1 in {o.lobbyist_id for o in outliers}


def test_min_hours_does_not_suppress_above_threshold_ratio_trip():
    """A lobbyist whose hours exceed ``min_hours_for_ratio_flag`` AND
    trip the ratio check is still flagged. Toy: 50 hrs total against
    zero attributable, threshold 10 → still flagged."""
    g = build_bipartite_graph(
        edges={(1, 100)},
        principal_totals={100: (0.0, 0.0)},
        lobbyist_totals={1: (50.0, 0.0)},
    )
    outliers = flag_outliers(g, min_hours_for_ratio_flag=10.0)
    assert 1 in {o.lobbyist_id for o in outliers}


def test_min_hours_h1_2025_suppresses_known_false_positives():
    """Phase 1 results §"False-positive ratio flags": H1 ratio-trip on
    lobbyist 11065 (0.2 hrs, max-attributable 0.0). Setting threshold
    to 10 hrs must suppress 11065 without affecting Pettack 11072 (who
    trips the per-semester absolute check at 4,007.5 hrs, independent
    of the ratio threshold)."""
    edges = load_active_edges(RELEASE_DIR, "2025-H1")
    p_totals = load_principal_totals(RELEASE_DIR, "2025-H1")
    l_totals = load_lobbyist_totals(RELEASE_DIR, "2025-H1")
    g = build_bipartite_graph(
        edges=edges, principal_totals=p_totals, lobbyist_totals=l_totals
    )
    flagged_default = {o.lobbyist_id for o in flag_outliers(g)}
    flagged_threshold = {
        o.lobbyist_id for o in flag_outliers(g, min_hours_for_ratio_flag=10.0)
    }
    assert 11065 in flagged_default
    assert 11065 not in flagged_threshold
    assert 11072 in flagged_threshold  # Pettack still caught via absolute
