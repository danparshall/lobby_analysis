"""Bipartite graph + connected-component decomposition for the WI
allocation-matrix problem.

The graph is bipartite: lobbyists on one side, principals on the other,
with edges drawn from ``load_active_edges``. ``connected_components``
decomposes it into independent sub-problems. ``classify_components``
splits them into:

- :class:`ExactlyPinned` — singleton-edge components (one lobbyist, one
  principal, one edge). The cell value is structurally determined: the
  lobbyist's marginal must equal the principal's marginal, both equal
  the cell. No IPF needed.
- :class:`FreeComponent` — everything else. Phase 2 IPF will fit these
  via max-entropy.

:func:`flag_outliers` surfaces lobbyists whose marginal hours
implausibly exceed the sum of attributable principal hours (the
Pettack-class organization-aggregates-under-one-lobbyist pattern). The
default threshold ratio is 2× — Pettack reports ~4,000 H1 hours
against principal marginals that can't possibly sum to 2,000.

Orphan handling: if an edge references a lobbyist or principal that
lacks a marginal in the input, the edge is still kept in the graph
(it shows up in the CC decomposition). Classify_components falls back
to the available marginal for singleton orphans. The IPF stage (Phase
2) will need to decide whether to drop or impute orphan-side cells.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import networkx as nx

__all__ = [
    "BipartiteGraph",
    "Component",
    "ExactlyPinned",
    "FreeComponent",
    "OutlierFlag",
    "build_bipartite_graph",
    "connected_components",
    "classify_components",
    "flag_outliers",
]


@dataclass(frozen=True)
class BipartiteGraph:
    """A lobbyist↔principal bipartite graph with per-node marginals.

    ``edges`` is the support pattern. ``*_totals`` are the IPF marginal
    constraints (hours_comm, hours_other).
    """

    edges: frozenset[tuple[int, int]]
    principal_totals: dict[int, tuple[float, float]]
    lobbyist_totals: dict[int, tuple[float, float]]


@dataclass(frozen=True)
class Component:
    """A connected sub-graph of the bipartite graph + its marginals."""

    edges: frozenset[tuple[int, int]]
    lobbyist_ids: frozenset[int]
    principal_ids: frozenset[int]
    principal_totals: dict[int, tuple[float, float]]
    lobbyist_totals: dict[int, tuple[float, float]]


@dataclass(frozen=True)
class ExactlyPinned:
    """A singleton-edge component — cell value is structurally pinned.

    ``hours_comm`` / ``hours_other`` are taken from the lobbyist's
    marginal where available, falling back to the principal's marginal
    for orphan-lobbyist singletons (a handful in the WI release).
    """

    lobbyist_id: int
    principal_id: int
    hours_comm: float
    hours_other: float


@dataclass(frozen=True)
class FreeComponent:
    """A multi-edge component that requires IPF to fit."""

    edges: frozenset[tuple[int, int]]
    principal_totals: dict[int, tuple[float, float]]
    lobbyist_totals: dict[int, tuple[float, float]]


@dataclass(frozen=True)
class OutlierFlag:
    """A lobbyist whose marginal hours implausibly exceed the
    aggregate principal-side ceiling."""

    lobbyist_id: int
    hours_total: float
    max_attributable_total: float
    reason: str


def build_bipartite_graph(
    edges: Iterable[tuple[int, int]],
    principal_totals: dict[int, tuple[float, float]],
    lobbyist_totals: dict[int, tuple[float, float]],
) -> BipartiteGraph:
    return BipartiteGraph(
        edges=frozenset(edges),
        principal_totals=dict(principal_totals),
        lobbyist_totals=dict(lobbyist_totals),
    )


def connected_components(graph: BipartiteGraph) -> list[Component]:
    """Decompose the bipartite graph into connected components.

    Returns ``[]`` for an empty graph. Each Component carries its own
    sub-edges + the marginals for the nodes in that component (filtered
    from the parent graph's totals).
    """
    if not graph.edges:
        return []
    G = nx.Graph()
    for (l, p) in graph.edges:
        # Prefix node ids with L/P to keep the two sides disjoint.
        G.add_edge(("L", l), ("P", p))

    components: list[Component] = []
    for cc_nodes in nx.connected_components(G):
        lob_ids = frozenset(n[1] for n in cc_nodes if n[0] == "L")
        prin_ids = frozenset(n[1] for n in cc_nodes if n[0] == "P")
        sub_edges = frozenset(
            (l, p) for (l, p) in graph.edges if l in lob_ids and p in prin_ids
        )
        components.append(
            Component(
                edges=sub_edges,
                lobbyist_ids=lob_ids,
                principal_ids=prin_ids,
                principal_totals={
                    p: graph.principal_totals[p]
                    for p in prin_ids
                    if p in graph.principal_totals
                },
                lobbyist_totals={
                    l: graph.lobbyist_totals[l]
                    for l in lob_ids
                    if l in graph.lobbyist_totals
                },
            )
        )
    return components


def classify_components(
    components: Iterable[Component],
) -> tuple[list[ExactlyPinned], list[FreeComponent]]:
    """Split components into exactly-pinned (singleton-edge) vs free."""
    pinned: list[ExactlyPinned] = []
    free: list[FreeComponent] = []
    for c in components:
        if len(c.edges) == 1:
            (lid, pid) = next(iter(c.edges))
            # Prefer lobbyist marginal; fall back to principal marginal
            # for orphan-lobbyist singletons.
            if lid in c.lobbyist_totals:
                comm, other = c.lobbyist_totals[lid]
            elif pid in c.principal_totals:
                comm, other = c.principal_totals[pid]
            else:
                comm, other = 0.0, 0.0
            pinned.append(
                ExactlyPinned(
                    lobbyist_id=lid,
                    principal_id=pid,
                    hours_comm=comm,
                    hours_other=other,
                )
            )
        else:
            free.append(
                FreeComponent(
                    edges=c.edges,
                    principal_totals=c.principal_totals,
                    lobbyist_totals=c.lobbyist_totals,
                )
            )
    return pinned, free


def flag_outliers(
    graph: BipartiteGraph,
    threshold_ratio: float = 2.0,
    max_hours_per_semester: float = 2000.0,
) -> list[OutlierFlag]:
    """Lobbyists whose marginal hours are implausible. Two checks:

    1. **Marginal-ratio check**: lobbyist's hours > ``threshold_ratio``
       × sum of their attributable principals' marginal hours. Catches
       cases where the lobbyist claims more than her principals
       collectively reported (would require attribution arithmetic to
       go negative on at least one other lobbyist).
    2. **Per-semester absolute check**: lobbyist's hours >
       ``max_hours_per_semester``. Catches the Pettack-class
       organization-aggregates-under-one-lobbyist pattern, where the
       marginal-ratio check is silent because the org family registers
       enough principals to make the sum plausible — but the per-day
       arithmetic is non-human (2000 hrs/semester ≈ 16 hrs/day across
       125 working days).

    A lobbyist may be flagged for one or both reasons; only one
    OutlierFlag is emitted per lobbyist, listing every triggered check.
    Lobbyists without a marginal (orphans) are skipped.
    """
    if not graph.edges:
        return []

    lob_principals: dict[int, list[int]] = {}
    for (lid, pid) in graph.edges:
        lob_principals.setdefault(lid, []).append(pid)

    flagged: list[OutlierFlag] = []
    for lid, principals in lob_principals.items():
        if lid not in graph.lobbyist_totals:
            continue
        l_comm, l_other = graph.lobbyist_totals[lid]
        l_total = l_comm + l_other
        max_attrib_total = sum(
            graph.principal_totals[pid][0] + graph.principal_totals[pid][1]
            for pid in principals
            if pid in graph.principal_totals
        )

        reasons: list[str] = []
        if l_total > threshold_ratio * max_attrib_total:
            reasons.append(
                f"hours {l_total:.1f} > {threshold_ratio}x max attributable "
                f"{max_attrib_total:.1f}"
            )
        if l_total > max_hours_per_semester:
            reasons.append(
                f"hours {l_total:.1f} > per-semester ceiling "
                f"{max_hours_per_semester:.1f} (~16 hrs/day non-human)"
            )

        if reasons:
            flagged.append(
                OutlierFlag(
                    lobbyist_id=lid,
                    hours_total=l_total,
                    max_attributable_total=max_attrib_total,
                    reason="; ".join(reasons),
                )
            )
    return flagged
