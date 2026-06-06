"""Audit script for the cross-state CPI 2015 C11 de-jure projection validation.

Plan: docs/historical/wi-ralph-cpi-renewal-cadence/plans/20260605_cross_state_cpi_2015_validation.md

For each (state, vintage=2015) results directory under results/tier_1/<STATE>_2015/:

1. Walk all dispatch result JSONs (6 chunks x 2 models x 3 runs = 36 per state).
2. Aggregate per-(row_id, axis) values across the 6 runs into a single value
   for the projection helpers to consume. Aggregation policy:
   - count distinct values seen across the 6 runs (unscoreables count as None)
   - take the MAJORITY value (>=4/6 = strong; 3/6 = weak)
   - flag stability class: stable / value_unstable / scor_unstable / incomplete
3. Apply the 6 de-jure projection helpers (project_ind_196, _197, _199, _201,
   _203, _207) from src/lobby_analysis/projections/cpi_2015_c11.py.
4. Compare against the published per-state oracle for those 6 indicators.
5. Emit a per-cell-verdict Table A (5 states x 6 indicators = 30 cells) +
   per-state-summary Table B (5 rows).

Run from the worktree root:
    uv run --env-file .env.local python scripts/cross_state_cpi_2015_audit.py
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

from lobby_analysis.projections.cpi_2015_c11 import (
    load_per_state_ground_truth,
    project_ind_196,
    project_ind_197,
    project_ind_199,
    project_ind_201,
    project_ind_203,
    project_ind_207,
)

# ----------------------------------------------------------------------------
# Config
# ----------------------------------------------------------------------------

_WORKTREE_ROOT = Path(__file__).resolve().parents[1]
_RESULTS_BASE = _WORKTREE_ROOT / "docs" / "active" / "cross-state-cpi-2015-validation" / "results" / "tier_1"

_STATES = ("NY", "WI", "OH", "CA", "TX")
_VINTAGE = 2015

# The dispatcher keys results by 2-letter state abbreviation; the CPI 2015
# oracle CSV uses full state names. Map for the 5 target states.
_STATE_ABBR_TO_NAME: dict[str, str] = {
    "NY": "New York",
    "WI": "Wisconsin",
    "OH": "Ohio",
    "CA": "California",
    "TX": "Texas",
}

_DE_JURE_INDICATORS: tuple[str, ...] = (
    "IND_196",
    "IND_197",
    "IND_199",
    "IND_201",
    "IND_203",
    "IND_207",
)

# Chunk hosting each de-jure indicator (per plan §P3 1:1 mapping).
_INDICATOR_HOSTING_CHUNK: dict[str, str] = {
    "IND_196": "lobbying_definitions",
    "IND_197": "registration_thresholds",
    "IND_199": "registration_mechanics_and_exemptions",
    "IND_201": "lobbyist_spending_report",
    "IND_203": "principal_spending_report",
    "IND_207": "enforcement_and_audits",
}

_PROJECTION_HELPER = {
    "IND_196": project_ind_196,
    "IND_197": project_ind_197,
    "IND_199": project_ind_199,
    "IND_201": project_ind_201,
    "IND_203": project_ind_203,
    "IND_207": project_ind_207,
}

# Cell IDs each de-jure projection reads (legal axis only). For diagnostic
# notes when a mismatch fires; helper functions own the actual cell reads.
_INDICATOR_INPUT_CELLS: dict[str, tuple[str, ...]] = {
    "IND_196": ("def_target_legislative_branch", "def_target_governors_office"),
    "IND_197": ("lobbyist_registration_threshold_compensation_dollars",),
    "IND_199": ("lobbyist_registration_renewal_cadence",),
    "IND_201": (
        "lobbyist_spending_report_required",
        "lobbyist_spending_report_includes_itemized_expenses",
        "lobbyist_spending_report_includes_total_compensation",
    ),
    "IND_203": (
        "principal_spending_report_required",
        "principal_spending_report_includes_compensation_paid_to_lobbyists",
    ),
    "IND_207": ("lobbying_disclosure_audit_required_in_law",),
}

# Models the dispatcher runs (so we can iterate result file names).
_MODELS: tuple[str, ...] = ("claude-opus-4-7", "gpt-5.2-2025-12-11")
_N_RUNS = 3


# ----------------------------------------------------------------------------
# Per-cell aggregation
# ----------------------------------------------------------------------------


@dataclass(frozen=True)
class AggregatedCell:
    row_id: str
    axis: str
    value: object  # the chosen value (may be None for unscoreable-majority)
    stability: str  # "stable" | "value_unstable" | "scor_unstable" | "incomplete"
    runs_total: int  # how many runs covered this cell (should be 6 if complete)
    value_counts: dict[str, int]  # repr(value) -> count, including "<unscoreable>"

    def is_unscoreable_majority(self) -> bool:
        return self.value is None and self.stability != "incomplete"


_UNSCOREABLE_SENTINEL = "<unscoreable>"


def _coerce_value(raw: object) -> object:
    """Coerce a raw dispatch value to a projection-helper-compatible form.

    DecimalCell stores values as strings ("0", "200"); projection helpers
    do `threshold == 0`, which fails string compare. Coerce numeric strings
    to int (preserving None for "no statute"). Bools and enum strings pass
    through unchanged.
    """
    if raw is None:
        return None
    if isinstance(raw, bool):
        return raw
    if isinstance(raw, (int, float)):
        return raw
    if isinstance(raw, str):
        # Try numeric coercion for DecimalCell strings.
        try:
            return int(raw)
        except ValueError:
            try:
                return float(raw)
            except ValueError:
                return raw  # enum string passthrough
    return raw


def _load_runs(state: str, vintage: int) -> dict[tuple[str, str], list[object | None]]:
    """Walk all dispatch JSONs for a state and return per-cell run lists.

    Returns ``{(row_id, axis): [value_run1, ..., value_run6]}`` where each
    list has length = n_models * n_runs (6 for the standard dispatch shape).
    A None entry means that run emitted the cell as unscoreable OR didn't
    cover the cell at all (e.g., model failure).
    """
    state_dir = _RESULTS_BASE / f"{state}_{vintage}"
    if not state_dir.exists():
        return {}

    per_cell_runs: dict[tuple[str, str], list[object | None]] = {}

    # We expect one file per (model, chunk, run). To know which cells SHOULD
    # appear per chunk, we read the legal_roster from any single file per
    # chunk (it's identical across runs). Cells not emitted by a given run
    # (instantiation errors / unscoreables) become None in that run's slot.
    for model in _MODELS:
        for chunk_id in _INDICATOR_HOSTING_CHUNK.values():
            # Read 3 runs per (model, chunk).
            for run_idx in range(1, _N_RUNS + 1):
                fname = f"{model}__{chunk_id}__run{run_idx}.json"
                fpath = state_dir / fname
                if not fpath.exists():
                    continue
                data = json.loads(fpath.read_text(encoding="utf-8"))
                roster = data.get("legal_roster", [])
                instantiated = data.get("instantiated_cells", [])

                # Build a per-cell value map for this run.
                inst_map: dict[tuple[str, str], object] = {}
                for entry in instantiated:
                    cell = entry["cell"]
                    cell_id = cell.get("cell_id")
                    if cell_id is None:
                        continue
                    row_id, axis = cell_id[0], cell_id[1]
                    raw_value = cell.get("value")
                    inst_map[(row_id, axis)] = _coerce_value(raw_value)

                # For every cell in the roster, record either the value (or
                # None if unscoreable / not emitted).
                for row_id, axis in roster:
                    key = (row_id, axis)
                    per_cell_runs.setdefault(key, []).append(inst_map.get(key))

    return per_cell_runs


def _aggregate(per_cell_runs: dict[tuple[str, str], list[object | None]]) -> dict[tuple[str, str], AggregatedCell]:
    """Reduce per-cell run lists to a single value + stability class."""
    out: dict[tuple[str, str], AggregatedCell] = {}
    for (row_id, axis), runs in per_cell_runs.items():
        runs_total = len(runs)
        # Bucket by stringified value (so unhashables like lists are fine).
        counter: Counter[str] = Counter()
        repr_to_value: dict[str, object] = {}
        for v in runs:
            key = _UNSCOREABLE_SENTINEL if v is None else repr(v)
            counter[key] += 1
            if key not in repr_to_value:
                repr_to_value[key] = v
        # Most common value (may be unscoreable sentinel).
        top_key, top_count = counter.most_common(1)[0]
        top_value = repr_to_value[top_key]

        # Stability classification.
        n_unscore = counter.get(_UNSCOREABLE_SENTINEL, 0)
        n_scoreable = runs_total - n_unscore
        if runs_total == 0:
            stability = "incomplete"
        elif len(counter) == 1 and top_key != _UNSCOREABLE_SENTINEL:
            stability = "stable"
        elif len(counter) == 1:  # all unscoreable
            stability = "stable"
        elif n_unscore > 0 and n_scoreable > 0:
            stability = "scor_unstable"
        else:
            stability = "value_unstable"

        out[(row_id, axis)] = AggregatedCell(
            row_id=row_id,
            axis=axis,
            value=top_value,
            stability=stability,
            runs_total=runs_total,
            value_counts=dict(counter),
        )
    return out


def _build_cells_dict(aggregated: dict[tuple[str, str], AggregatedCell]) -> dict[str, dict[str, object]]:
    """Materialize the {row_id: {axis_long: value}} dict the projection helpers
    consume.

    Schema bridge: the dispatcher emits the axis as the short string
    ('legal' / 'practical') on `cell_id`, but the projection helpers in
    `cpi_2015_c11.py` read `cell.get('legal_availability')` /
    `cell.get('practical_availability')` (the v1.1 MatrixCell field names).
    Rename the short form to the long form on the way out.
    """
    short_to_long = {"legal": "legal_availability", "practical": "practical_availability"}
    out: dict[str, dict[str, object]] = {}
    for (row_id, axis), agg in aggregated.items():
        long_axis = short_to_long.get(axis, axis)
        out.setdefault(row_id, {})[long_axis] = agg.value
    return out


# ----------------------------------------------------------------------------
# Per-state cost + error summary (read from dispatch JSON metadata)
# ----------------------------------------------------------------------------


@dataclass(frozen=True)
class PerStateMeta:
    state: str
    n_dispatches: int
    total_cost_usd: float
    n_instantiation_errors: int


def _state_meta(state: str, vintage: int) -> PerStateMeta:
    state_dir = _RESULTS_BASE / f"{state}_{vintage}"
    n_dispatches = 0
    total_cost = 0.0
    n_errors = 0
    for fpath in sorted(state_dir.glob("*.json")):
        data = json.loads(fpath.read_text(encoding="utf-8"))
        n_dispatches += 1
        total_cost += float(data.get("cost_usd_estimate", 0.0))
        n_errors += len(data.get("errors", []))
    return PerStateMeta(
        state=state,
        n_dispatches=n_dispatches,
        total_cost_usd=round(total_cost, 4),
        n_instantiation_errors=n_errors,
    )


# ----------------------------------------------------------------------------
# Report rendering
# ----------------------------------------------------------------------------


def _diagnose_mismatch(indicator: str, aggregated: dict[tuple[str, str], AggregatedCell], extracted_score: int, oracle_score: int) -> str:
    """One-sentence diagnosis for a (state, indicator) exact-match miss.

    Categorizes by the most common failure modes:
    - vocab-mismatch: extracted value is in a different vocabulary than the
      projection helper expects (IND_199, IND_207)
    - missing-cell: the input cell wasn't extracted (None)
    - unstable: aggregated stability != "stable"
    - genuine-disagreement: extraction looks clean but disagrees with oracle
    """
    input_cells = _INDICATOR_INPUT_CELLS.get(indicator, ())
    if not input_cells:
        return "no input cells mapped"

    notes: list[str] = []
    for row_id in input_cells:
        agg = aggregated.get((row_id, "legal"))
        if agg is None:
            notes.append(f"{row_id}: NOT-EXTRACTED")
        elif agg.stability != "stable":
            notes.append(f"{row_id}: {agg.stability} (value={agg.value!r})")
        else:
            notes.append(f"{row_id}={agg.value!r}")

    # Vocab-mismatch heuristics for IND_199 (cadence) and IND_207 (audit enum).
    if indicator == "IND_199":
        agg = aggregated.get(("lobbyist_registration_renewal_cadence", "legal"))
        if agg is not None and isinstance(agg.value, (int, float)):
            return (
                f"vocab-mismatch: extracted IntCell={agg.value} (months) but "
                f"helper expects string enum {{annual, biennial, ...}}; "
                f"oracle={oracle_score}, projected={extracted_score}"
            )
    if indicator == "IND_207":
        agg = aggregated.get(("lobbying_disclosure_audit_required_in_law", "legal"))
        if agg is not None and agg.value in ("YES", "MODERATE", "NO"):
            return (
                f"vocab-mismatch: extracted EnumCell={agg.value!r} but helper "
                f"expects {{'regular_third_party_audit_required', "
                f"'audit_only_when_irregularities_suspected_or_compliance_review'}}; "
                f"oracle={oracle_score}, projected={extracted_score}"
            )

    return f"oracle={oracle_score} projected={extracted_score}; " + "; ".join(notes)


def _render_table_a(rows: list[dict[str, object]]) -> str:
    headers = [
        "State",
        "Indicator",
        "Chunk",
        "Oracle",
        "Projected",
        "Match",
        "Notes",
    ]
    lines = ["| " + " | ".join(headers) + " |", "|" + "|".join("---" for _ in headers) + "|"]
    for r in rows:
        lines.append(
            "| "
            + " | ".join(
                str(r[h]).replace("\n", " ").replace("|", "\\|") for h in headers
            )
            + " |"
        )
    return "\n".join(lines)


def _render_table_b(rows: list[dict[str, object]]) -> str:
    headers = [
        "State",
        "Indicators matched",
        "Dispatches",
        "Instantiation errors",
        "Total cost (USD)",
        "Per-chunk diagnosis",
    ]
    lines = ["| " + " | ".join(headers) + " |", "|" + "|".join("---" for _ in headers) + "|"]
    for r in rows:
        lines.append("| " + " | ".join(str(r[h]) for h in headers) + " |")
    return "\n".join(lines)


# ----------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------


def run_audit(states: Iterable[str] = _STATES) -> str:
    oracle = load_per_state_ground_truth()
    table_a_rows: list[dict[str, object]] = []
    table_b_rows: list[dict[str, object]] = []
    per_indicator_match_counts: dict[str, int] = {ind: 0 for ind in _DE_JURE_INDICATORS}

    for state in states:
        state_dir = _RESULTS_BASE / f"{state}_{_VINTAGE}"
        if not state_dir.exists():
            print(f"SKIP {state}: results dir not found at {state_dir}", file=sys.stderr)
            continue

        meta = _state_meta(state, _VINTAGE)
        per_cell_runs = _load_runs(state, _VINTAGE)
        aggregated = _aggregate(per_cell_runs)
        cells = _build_cells_dict(aggregated)

        # Per-indicator: project, compare, record.
        state_match_count = 0
        per_chunk_diag: list[str] = []
        oracle_state_name = _STATE_ABBR_TO_NAME.get(state, state)
        for ind in _DE_JURE_INDICATORS:
            projected = _PROJECTION_HELPER[ind](cells)
            oracle_score = oracle.get((oracle_state_name, ind))
            match = projected == oracle_score
            if match:
                state_match_count += 1
                per_indicator_match_counts[ind] += 1
                notes = "match"
            else:
                notes = _diagnose_mismatch(ind, aggregated, projected, oracle_score)
            table_a_rows.append(
                {
                    "State": state,
                    "Indicator": ind,
                    "Chunk": _INDICATOR_HOSTING_CHUNK[ind],
                    "Oracle": oracle_score,
                    "Projected": projected,
                    "Match": "YES" if match else "no",
                    "Notes": notes,
                }
            )
            per_chunk_diag.append(
                f"{_INDICATOR_HOSTING_CHUNK[ind]}->{ind}: "
                + ("match" if match else f"{projected}!={oracle_score}")
            )

        table_b_rows.append(
            {
                "State": state,
                "Indicators matched": f"{state_match_count} / 6",
                "Dispatches": meta.n_dispatches,
                "Instantiation errors": meta.n_instantiation_errors,
                "Total cost (USD)": f"${meta.total_cost_usd:.4f}",
                "Per-chunk diagnosis": "; ".join(per_chunk_diag),
            }
        )

    # Per-indicator summary (across all states).
    n_states_audited = len(table_b_rows)
    total_cells = n_states_audited * 6
    total_matches = sum(per_indicator_match_counts.values())

    md = []
    md.append("# Cross-state CPI 2015 C11 de-jure projection-accuracy audit")
    md.append("")
    md.append(f"**States audited:** {', '.join(r['State'] for r in table_b_rows)} (vintage 2015)")
    md.append(f"**De-jure indicators:** {', '.join(_DE_JURE_INDICATORS)}")
    md.append(f"**Total comparison cells:** {total_cells}")
    md.append(f"**Total matches:** {total_matches} / {total_cells} ({100 * total_matches / total_cells:.1f}%)")
    md.append("")
    md.append("Per-indicator match counts (across states):")
    md.append("")
    for ind in _DE_JURE_INDICATORS:
        md.append(f"- {ind}: {per_indicator_match_counts[ind]} / {n_states_audited}")
    md.append("")
    md.append("## Table A — Per-cell comparison (state x indicator)")
    md.append("")
    md.append(_render_table_a(table_a_rows))
    md.append("")
    md.append("## Table B — Per-state summary")
    md.append("")
    md.append(_render_table_b(table_b_rows))
    md.append("")
    return "\n".join(md)


def main() -> int:
    md = run_audit()
    print(md)
    return 0


if __name__ == "__main__":
    sys.exit(main())
