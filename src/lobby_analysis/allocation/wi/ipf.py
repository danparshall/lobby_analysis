"""Iterative Proportional Fitting (IPF) for the WI allocation matrix.

Run per connected component, per hours-type, against the bipartite
support pattern from the graph layer. The seed matrix is 1.0 on edges,
0.0 elsewhere — ipfn preserves zero cells through every iteration, so
the bipartite edge structure carries through without explicit
constraint handling.

Marginals are taken as-is from the loader output. Phase 2 design call
(see ``convos/20260531_phase_2_ipf_design.md``):

- **No marginal surgery for Pettack.** Pettack 11072 sits in her own
  6x6 CC where the marginals balance natively (730.2 hrs comm both
  sides, 3454.5 vs 3466.8 other). The IPF converges cleanly. Her
  cells are labeled ``confidence='aggregation_flagged'`` at materialize
  time, not by altering the fit.
- **Zero-marginal lobbyists/principals stay in the fit.** Their rows or
  cols go to 0 by IPF construction (zero target × current row sum = 0).
  Within-CC aggregate row residual ~1.3-2.8% is accepted as a
  data-quality fixture, not a fit failure.
- **Cells in zero-marginal-lobbyist rows materialize as
  ``zero_filed``.** Preserves the cell so downstream comparisons can
  surface ``principal paid but lobbyist filed 0 hrs`` patterns.

API:

    fit_component(component, hours_type) -> ComponentFit
        Run IPF on one FreeComponent for one of {"hours_comm",
        "hours_other"}. Returns the cell value dict + diagnostics.

    fit_all(graph) -> AllocationMatrix
        Orchestrate over every component × {hours_comm, hours_other},
        applying the confidence label per the Phase 2 categorization.
"""

from __future__ import annotations

import contextlib
import io
import warnings
from dataclasses import dataclass, field
from typing import Literal

import numpy as np
from ipfn import ipfn as _ipfn_module

from lobby_analysis.allocation.wi.graph import (
    BipartiteGraph,
    FreeComponent,
    classify_components,
    connected_components,
    flag_outliers,
)

__all__ = [
    "AllocationCell",
    "AllocationMatrix",
    "ComponentFit",
    "fit_all",
    "fit_component",
]


# Empirical Phase 1 finding: 10-hour floor suppresses 4 tiny-hours
# ratio-flag false positives without affecting Pettack-class (caught
# by the per-semester absolute check at >2000 hrs).
_DEFAULT_MIN_HOURS_FOR_RATIO_FLAG = 10.0

HoursType = Literal["hours_comm", "hours_other"]
ConfidenceLabel = Literal["exact", "ipf_fit", "zero_filed", "aggregation_flagged"]


@dataclass(frozen=True)
class ComponentFit:
    """The IPF fit for one FreeComponent + one hours-type."""

    cells: dict[tuple[int, int], float]
    iterations: int
    converged: bool
    hours_type: HoursType


@dataclass(frozen=True)
class AllocationCell:
    """One materialized cell of the allocation matrix."""

    hours_comm: float
    hours_other: float
    confidence: ConfidenceLabel


@dataclass(frozen=True)
class AllocationMatrix:
    """All cells across all CCs for one semester."""

    cells: dict[tuple[int, int], AllocationCell] = field(default_factory=dict)


def fit_component(
    component: FreeComponent,
    hours_type: HoursType,
    convergence_rate: float = 1e-6,
    max_iteration: int = 500,
) -> ComponentFit:
    """Run IPF on one FreeComponent for one hours-type.

    Returns a ComponentFit with per-(lobbyist_id, principal_id) cell
    values. Cells for non-edge pairs are NOT included in the output.
    """
    axis = 0 if hours_type == "hours_comm" else 1

    # Build the index mapping. Sorted for determinism.
    lob_list = sorted({lid for (lid, _) in component.edges})
    prin_list = sorted({pid for (_, pid) in component.edges})
    lob_idx = {lid: i for i, lid in enumerate(lob_list)}
    prin_idx = {pid: j for j, pid in enumerate(prin_list)}

    # Seed: 1.0 on edges, 0.0 elsewhere. The ipfn algorithm preserves
    # the zero cells through every iteration (verified empirically).
    seed = np.zeros((len(lob_list), len(prin_list)), dtype=np.float64)
    for (lid, pid) in component.edges:
        seed[lob_idx[lid], prin_idx[pid]] = 1.0

    # Marginals taken as-is. Missing entries default to 0.0 (orphans).
    row_targets = np.array(
        [component.lobbyist_totals.get(lid, (0.0, 0.0))[axis] for lid in lob_list],
        dtype=np.float64,
    )
    col_targets = np.array(
        [component.principal_totals.get(pid, (0.0, 0.0))[axis] for pid in prin_list],
        dtype=np.float64,
    )

    # ipfn emits a RuntimeWarning for zero-target axes ("invalid value
    # encountered in scalar divide" at line 146 — the convergence check
    # divides fit_sum / target). Suppress it: the zero-target rows/cols
    # are clamped to 0 by construction and don't contribute to the
    # convergence rate calc meaningfully.
    #
    # ipfn also unconditionally prints "ipfn converged: ..." to stdout
    # at the end of iteration() regardless of verbose level. Capture
    # stdout to keep our CLI output clean — the convergence info is
    # already exposed via the returned ``converged`` flag.
    with warnings.catch_warnings(), contextlib.redirect_stdout(io.StringIO()):
        warnings.simplefilter("ignore", category=RuntimeWarning)
        fit_array, converged, conv_df = _ipfn_module.ipfn(
            seed,
            [row_targets, col_targets],
            [[0], [1]],
            convergence_rate=convergence_rate,
            max_iteration=max_iteration,
            verbose=2,
        ).iteration()
    iterations = len(conv_df)

    cells: dict[tuple[int, int], float] = {}
    for (lid, pid) in component.edges:
        cells[(lid, pid)] = float(fit_array[lob_idx[lid], prin_idx[pid]])

    return ComponentFit(
        cells=cells,
        iterations=iterations,
        converged=bool(converged),
        hours_type=hours_type,
    )


def fit_all(
    graph: BipartiteGraph,
    *,
    min_hours_for_ratio_flag: float = _DEFAULT_MIN_HOURS_FOR_RATIO_FLAG,
) -> AllocationMatrix:
    """Run the per-CC IPF for every edge in the graph, label each
    resulting cell with a confidence value, and return the merged
    AllocationMatrix.

    The four confidence labels follow the Phase 2 categorization:

    - ``exact`` — singleton CC: cell value is structurally determined
      (one lobbyist + one principal + one edge → marginals must equal
      the cell).
    - ``ipf_fit`` — free CC, nonzero-marginal lobbyist, not flagged.
      Cell value is the max-entropy IPF fit.
    - ``zero_filed`` — free CC, lobbyist with zero hours_comm AND zero
      hours_other marginal. IPF outputs 0 by construction; the label
      preserves the cell so downstream comparisons can surface
      ``principal paid but lobbyist filed 0 hrs`` patterns.
    - ``aggregation_flagged`` — cell in a row of a lobbyist returned by
      ``flag_outliers``. Indicates the lobbyist's marginal is
      consistent with the org-aggregates-under-one-lobbyist pattern
      (Pettack-class). The IPF fit is unchanged; only the label
      changes.
    """
    components = connected_components(graph)
    pinned, free = classify_components(components)

    flagged_ids = {
        f.lobbyist_id
        for f in flag_outliers(
            graph, min_hours_for_ratio_flag=min_hours_for_ratio_flag
        )
    }

    cells: dict[tuple[int, int], AllocationCell] = {}

    # Singleton CCs — exactly pinned.
    for ep in pinned:
        cells[(ep.lobbyist_id, ep.principal_id)] = AllocationCell(
            hours_comm=ep.hours_comm,
            hours_other=ep.hours_other,
            confidence="exact",
        )

    # Free CCs — run IPF on each, twice (comm + other).
    for fc in free:
        fit_comm = fit_component(fc, hours_type="hours_comm")
        fit_other = fit_component(fc, hours_type="hours_other")
        for (lid, pid) in fc.edges:
            hc = fit_comm.cells.get((lid, pid), 0.0)
            ho = fit_other.cells.get((lid, pid), 0.0)
            label = _confidence_for_free_cell(
                lid=lid,
                fc=fc,
                flagged_ids=flagged_ids,
            )
            cells[(lid, pid)] = AllocationCell(
                hours_comm=hc,
                hours_other=ho,
                confidence=label,
            )

    return AllocationMatrix(cells=cells)


def _confidence_for_free_cell(
    *,
    lid: int,
    fc: FreeComponent,
    flagged_ids: set[int],
) -> ConfidenceLabel:
    """Pick the confidence label for a cell in a free CC.

    Precedence: ``aggregation_flagged`` > ``zero_filed`` > ``ipf_fit``.
    A flagged lobbyist with zero hours is unusual but possible; we
    still label flagged because it carries more downstream caution.
    """
    if lid in flagged_ids:
        return "aggregation_flagged"
    marg = fc.lobbyist_totals.get(lid, (0.0, 0.0))
    if marg[0] == 0.0 and marg[1] == 0.0:
        return "zero_filed"
    return "ipf_fit"
