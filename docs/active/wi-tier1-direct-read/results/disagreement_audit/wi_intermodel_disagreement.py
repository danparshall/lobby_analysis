"""Enumerate WI 2025 Tier-1 cells where:
  - All 3 Claude runs agree internally (within-model stable)
  - All 3 GPT runs agree internally (within-model stable)
  - Claude's consensus answer != GPT's consensus answer

Output: a markdown-ready table of the disagreement cells, per chunk,
with each model's value + cited_section + justification.
"""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

RESULTS_DIR = Path(
    "/Users/dan/code/lobby_analysis/.worktrees/wi-tier1-direct-read/"
    "docs/active/wi-tier1-direct-read/results/tier_1/WI_2025"
)

CHUNKS = [
    "lobbying_definitions",
    "registration_thresholds",
    "registration_mechanics_and_exemptions",
    "lobbyist_spending_report",
    "principal_spending_report",
    "enforcement_and_audits",
]
MODELS = ["claude-opus-4-7", "gpt-5.2-2025-12-11"]
RUNS = [1, 2, 3]


def load_run(model: str, chunk: str, run: int) -> dict:
    path = RESULTS_DIR / f"{model}__{chunk}__run{run}.json"
    return json.loads(path.read_text())


def cell_status_for_run(data: dict) -> dict[str, dict]:
    """For a single run's data, return {row_id: status_dict}.

    status_dict is one of:
      - {'kind': 'scored', 'value': X, 'cited_section': ..., 'justification': ..., 'confidence': ...}
      - {'kind': 'unscoreable', 'reason': ..., 'cited_section': ..., 'confidence': ...}
      - {'kind': 'incomplete', 'reason': error_kind}
    """
    out: dict[str, dict] = {}
    roster_ids = [row_id for row_id, _axis in data.get("legal_roster", [])]

    # Scored cells
    for entry in data.get("instantiated_cells", []):
        cell = entry["cell"]
        row_id = cell["cell_id"][0]
        out[row_id] = {
            "kind": "scored",
            "value": cell.get("value"),
            "confidence": cell.get("confidence"),
            "cited_section": entry.get("cited_section"),
            "justification": entry.get("justification"),
            "cell_class": entry.get("cell_class"),
        }

    # Unscoreable cells (different shape — flat keys row_id/axis/...)
    for entry in data.get("unscoreable_emissions", []):
        row_id = entry.get("row_id") or (entry.get("cell_id", [None])[0])
        if row_id is None:
            continue
        if row_id in out:
            # Should not happen — a row can't be both scored and unscoreable in the same run
            continue
        out[row_id] = {
            "kind": "unscoreable",
            "reason": entry.get("reason"),
            "confidence": entry.get("confidence"),
            "cited_section": entry.get("cited_section"),
            "justification": entry.get("justification"),
        }

    # Anything in roster but missing → incomplete (likely instantiation error)
    for row_id in roster_ids:
        if row_id not in out:
            out[row_id] = {"kind": "incomplete", "reason": "missing_from_output"}

    return out


def consensus_for_model(runs_status: list[dict]) -> dict | None:
    """Given 3 runs' status dicts for ONE row, return a consensus dict
    if all 3 agree on (kind, value); else None."""
    if len(runs_status) != 3:
        return None
    kinds = {s["kind"] for s in runs_status}
    if len(kinds) > 1:
        return None  # not stable on kind
    kind = next(iter(kinds))
    if kind == "scored":
        vals = {json.dumps(s["value"], sort_keys=True) for s in runs_status}
        if len(vals) > 1:
            return None  # not stable on value
        # Stable: return run 1's full record
        return runs_status[0]
    if kind == "unscoreable":
        # Treat any unscoreable as stable kind, regardless of reason
        return runs_status[0]
    if kind == "incomplete":
        return runs_status[0]
    return None


def answer_key(status: dict) -> tuple:
    """Reduce a status dict to a hashable answer key for inter-model comparison."""
    if status["kind"] == "scored":
        return ("scored", json.dumps(status["value"], sort_keys=True))
    if status["kind"] == "unscoreable":
        return ("unscoreable",)
    if status["kind"] == "incomplete":
        return ("incomplete",)
    return ("unknown",)


def main():
    # cell_data[chunk][row_id][model] = list of 3 run status dicts
    cell_data: dict[str, dict[str, dict[str, list[dict]]]] = defaultdict(
        lambda: defaultdict(lambda: defaultdict(list))
    )

    for chunk in CHUNKS:
        for model in MODELS:
            for run in RUNS:
                data = load_run(model, chunk, run)
                statuses = cell_status_for_run(data)
                for row_id, status in statuses.items():
                    cell_data[chunk][row_id][model].append(status)

    # Find inter-model disagreement cells
    disagreements: list[tuple] = []  # (chunk, row_id, claude_consensus, gpt_consensus)
    total_cells = 0
    jointly_stable = 0
    intermodel_agree = 0

    for chunk in CHUNKS:
        for row_id, model_runs in cell_data[chunk].items():
            total_cells += 1
            claude_runs = model_runs.get("claude-opus-4-7", [])
            gpt_runs = model_runs.get("gpt-5.2-2025-12-11", [])
            claude_cons = consensus_for_model(claude_runs)
            gpt_cons = consensus_for_model(gpt_runs)
            if claude_cons is None or gpt_cons is None:
                continue
            jointly_stable += 1
            if answer_key(claude_cons) == answer_key(gpt_cons):
                intermodel_agree += 1
            else:
                disagreements.append((chunk, row_id, claude_cons, gpt_cons))

    print(f"Total unique (chunk, row_id) cells: {total_cells}")
    print(f"Jointly within-model stable: {jointly_stable}")
    print(f"  Inter-model agree: {intermodel_agree}")
    print(f"  Inter-model DISAGREE: {len(disagreements)}")
    print()

    # Per-chunk breakdown of disagreements
    by_chunk: dict[str, list] = defaultdict(list)
    for chunk, row_id, c, g in disagreements:
        by_chunk[chunk].append((row_id, c, g))

    print("## Disagreements per chunk")
    for chunk in CHUNKS:
        items = by_chunk[chunk]
        print(f"  {chunk}: {len(items)}")
    print()

    # Full detail per disagreement
    for chunk in CHUNKS:
        items = by_chunk[chunk]
        if not items:
            continue
        print(f"\n=== {chunk} ({len(items)} disagreement cells) ===\n")
        for row_id, c, g in items:
            print(f"### `{row_id}`")
            print()
            print(f"**Claude** ({c['kind']}):")
            if c["kind"] == "scored":
                print(f"  - value: `{json.dumps(c['value'])}`")
                print(f"  - confidence: {c.get('confidence')}")
                print(f"  - cited: {c.get('cited_section')}")
                just = (c.get("justification") or "").strip()
                if just:
                    print(f"  - justification: {just}")
            elif c["kind"] == "unscoreable":
                print(f"  - reason: {c.get('reason')}")
                print(f"  - confidence: {c.get('confidence')}")
                print(f"  - cited: {c.get('cited_section')}")
            else:
                print(f"  - {c.get('reason', 'unknown')}")
            print()
            print(f"**GPT-5.2** ({g['kind']}):")
            if g["kind"] == "scored":
                print(f"  - value: `{json.dumps(g['value'])}`")
                print(f"  - confidence: {g.get('confidence')}")
                print(f"  - cited: {g.get('cited_section')}")
                just = (g.get("justification") or "").strip()
                if just:
                    print(f"  - justification: {just}")
            elif g["kind"] == "unscoreable":
                print(f"  - reason: {g.get('reason')}")
                print(f"  - confidence: {g.get('confidence')}")
                print(f"  - cited: {g.get('cited_section')}")
            else:
                print(f"  - {g.get('reason', 'unknown')}")
            print()


if __name__ == "__main__":
    main()
