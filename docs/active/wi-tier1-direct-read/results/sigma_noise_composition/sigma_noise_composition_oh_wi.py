"""Decompose σ_noise = pct_stable into its stability-class components for
both OH (extraction-harness-brainstorm archive) and WI (this branch), so the
2 → 7 GPT scoreability-unstable jump in WI can be seen against the broader
component shifts.

Plan: docs/active/wi-tier1-direct-read/plans/20260601_post_phase3_followups.md
Item 6.

The Tier-1 classifier already emits four components per (model, state):
  n_stable, n_value_unstable, n_scoreability_unstable, n_incomplete
plus the aggregate pct_stable = n_stable / n_cells. The headline σ_noise reads
only pct_stable; this script re-reads the saved Tier-1 result JSONs, re-runs
the classifier (no API calls), and prints the full 4-component breakdown.
"""

from __future__ import annotations

import importlib.util
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

REPO = Path("/Users/dan/code/lobby_analysis/.worktrees/wi-tier1-direct-read")
TIER_1_SCRIPT = REPO / "scripts" / "tier_1_direct_read_legal_axis.py"
TIER_0_SCRIPT = REPO / "scripts" / "tier_0_direct_read_smoke.py"

# Load the Tier-1 module via importlib (matches the test pattern).
sys.path.insert(0, str(REPO / "src"))


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


tier0 = _load("tier_0_direct_read_smoke", TIER_0_SCRIPT)
tier1 = _load("tier_1_direct_read_legal_axis", TIER_1_SCRIPT)

# Filename pattern: <model>__<chunk_id>__run<N>.json
_FNAME_RE = re.compile(r"^(?P<model>[^_]+(?:-[^_]+)*)__(?P<chunk>[^_]+(?:_[^_]+)*)__run(?P<run>\d+)\.json$")


def _parse_fname(fname: str) -> dict | None:
    m = _FNAME_RE.match(fname)
    if not m:
        return None
    return m.groupdict()


def _extract_outcome_from_payload(payload: dict, row_id: str, axis: str):
    """Build a CellOutcome by walking the saved result JSON.

    Mirrors the runner's `extract_cell_outcome` semantics but reads from disk:
      - if (row_id, axis) is in errors[*].key → errored
      - if in unscoreable_emissions[*].(row_id, axis) → abstained
      - if in instantiated_cells[*].cell.cell_id → scored, value = cell.value
      - else absent.
    """
    key = [row_id, axis]
    for err in payload.get("errors", []):
        if err.get("key") == key:
            return tier1.CellOutcome(status="errored", value=None)
    for ab in payload.get("unscoreable_emissions", []):
        if ab.get("row_id") == row_id and ab.get("axis") == axis:
            return tier1.CellOutcome(status="abstained", value=None)
    for inst in payload.get("instantiated_cells", []):
        cell_id = inst.get("cell", {}).get("cell_id")
        if cell_id == key:
            value = inst.get("cell", {}).get("value")
            return tier1.CellOutcome(status="scored", value=value)
    return tier1.CellOutcome(status="absent", value=None)


def _analyze(state_label: str, results_dir: Path):
    """Group result JSONs by (model, chunk, row_id, axis), classify, summarize."""
    # First pass: load every payload, indexed by (model, chunk_id, run_index).
    by_dispatch: dict[tuple[str, str, int], dict] = {}
    legal_rosters_by_chunk: dict[str, list[tuple[str, str]]] = {}
    for path in sorted(results_dir.glob("*.json")):
        parts = _parse_fname(path.name)
        if parts is None:
            continue
        with path.open() as f:
            payload = json.load(f)
        model = parts["model"]
        chunk = parts["chunk"]
        run = int(parts["run"])
        by_dispatch[(model, chunk, run)] = payload
        # Record the chunk's legal roster (every run for a given chunk uses
        # the same roster — verified by the runner's deterministic dispatch).
        roster = [tuple(r) for r in payload.get("legal_roster", [])]
        legal_rosters_by_chunk.setdefault(chunk, roster)

    # Second pass: per (model, chunk), gather the N runs, then per cell on
    # that chunk's roster, build a CellOutcome list across runs.
    models = sorted({k[0] for k in by_dispatch})
    chunks = sorted({k[1] for k in by_dispatch})

    per_model_summary: dict[str, dict] = {}
    per_model_chunk_breakdown: dict[str, dict[str, dict]] = defaultdict(dict)

    for model in models:
        all_cell_classifications: dict = {}
        for chunk in chunks:
            roster = legal_rosters_by_chunk.get(chunk, [])
            chunk_cells: dict = {}
            runs = sorted({k[2] for k in by_dispatch if k[0] == model and k[1] == chunk})
            for row_id, axis in roster:
                outcomes = []
                for run in runs:
                    payload = by_dispatch.get((model, chunk, run))
                    if payload is None:
                        outcomes.append(tier1.CellOutcome(status="absent"))
                        continue
                    outcomes.append(_extract_outcome_from_payload(payload, row_id, axis))
                cls = tier1.classify_cell_runs(outcomes)
                chunk_cells[(row_id, axis)] = cls
                all_cell_classifications[(chunk, row_id, axis)] = cls
            per_model_chunk_breakdown[model][chunk] = tier1.summarize_sigma_noise(chunk_cells)
        per_model_summary[model] = tier1.summarize_sigma_noise(all_cell_classifications)

    return per_model_summary, per_model_chunk_breakdown


def _print_summary(state_label: str, summary: dict):
    print(f"\n=== {state_label} — σ_noise composition (all chunks, N=3 runs) ===")
    print(f"{'model':<32} {'n_cells':>8} {'stable':>7} {'val_un':>7} {'scor_un':>8} {'incomp':>7} {'pct_st':>7}")
    for model, s in sorted(summary.items()):
        print(
            f"{model:<32} {s['n_cells']:>8} {s['n_stable']:>7} "
            f"{s['n_value_unstable']:>7} {s['n_scoreability_unstable']:>8} "
            f"{s['n_incomplete']:>7} {s['pct_stable']:>6.2f}%"
        )


def _print_chunk_breakdown(state_label: str, per_model_chunk: dict):
    print(f"\n--- {state_label} — per-chunk breakdown (scoreability-unstable focus) ---")
    print(f"{'model':<32} {'chunk':<40} {'n':>4} {'stab':>5} {'val':>4} {'scor':>5} {'inc':>4}")
    for model in sorted(per_model_chunk):
        for chunk in sorted(per_model_chunk[model]):
            s = per_model_chunk[model][chunk]
            print(
                f"{model:<32} {chunk:<40} {s['n_cells']:>4} {s['n_stable']:>5} "
                f"{s['n_value_unstable']:>4} {s['n_scoreability_unstable']:>5} "
                f"{s['n_incomplete']:>4}"
            )


def main():
    oh_dir = REPO / "docs" / "historical" / "extraction-harness-brainstorm" / "results" / "tier_1"
    wi_dir = REPO / "docs" / "active" / "wi-tier1-direct-read" / "results" / "tier_1" / "WI_2025"

    oh_summary, oh_chunk = _analyze("OH 2025", oh_dir)
    wi_summary, wi_chunk = _analyze("WI 2025", wi_dir)

    _print_summary("OH 2025", oh_summary)
    _print_summary("WI 2025", wi_summary)
    _print_chunk_breakdown("OH 2025", oh_chunk)
    _print_chunk_breakdown("WI 2025", wi_chunk)

    print("\n=== Δ (WI − OH) — per model ===")
    print(f"{'model':<32} {'Δstable':>8} {'Δval_un':>8} {'Δscor_un':>9} {'Δincomp':>8} {'Δpct_st':>8}")
    for model in sorted(set(oh_summary) | set(wi_summary)):
        oh = oh_summary.get(model, {})
        wi = wi_summary.get(model, {})
        if not oh or not wi:
            continue
        dstable = wi["n_stable"] - oh["n_stable"]
        dval = wi["n_value_unstable"] - oh["n_value_unstable"]
        dscor = wi["n_scoreability_unstable"] - oh["n_scoreability_unstable"]
        dinc = wi["n_incomplete"] - oh["n_incomplete"]
        dpct = wi["pct_stable"] - oh["pct_stable"]
        print(
            f"{model:<32} {dstable:>+8d} {dval:>+8d} {dscor:>+9d} "
            f"{dinc:>+8d} {dpct:>+7.2f}%"
        )


if __name__ == "__main__":
    main()
