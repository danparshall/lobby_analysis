"""Rebuild a per-pass _summary_run<N>.json from on-disk per-filing artifacts.

Needed when the dispatch is killed mid-pass — the summary is normally written
once at end-of-pass, so a SIGKILL leaves no JSON. This script walks
`data/oh_portal/extracted_openai/<report_id>/<run_label>_*/extraction_run.json`
and aggregates token / cost / wall-clock into the same schema the dispatcher
would have written.

Usage:
    python scripts/gpt5mini_oh_300slice_reconstruct_summary.py --pass 1
    python scripts/gpt5mini_oh_300slice_reconstruct_summary.py --pass 1 --out FOO.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
_SRC = _REPO_ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from lobby_analysis.oh_portal.fetch import DATA_DIR  # noqa: E402
from lobby_analysis.oh_portal.pipeline_openai import (  # noqa: E402
    EXTRACTED_OPENAI_SUBDIR,
)

# Must match the dispatcher's constants.
COST_PER_MTOK_PROMPT = 0.25
COST_PER_MTOK_COMPLETION = 2.00


def reconstruct(run_label: str, data_dir: Path) -> dict:
    mini_dir = data_dir / EXTRACTED_OPENAI_SUBDIR
    n_attempted = 0
    n_extracted = 0
    total_prompt = 0
    total_completion = 0
    total_wall = 0.0
    started_at_min: str | None = None
    finished_at_max: str | None = None

    if not mini_dir.is_dir():
        return {
            "run_label": run_label,
            "n_attempted": 0, "n_extracted": 0, "n_skipped_resume": 0,
            "n_failed": 0, "total_prompt_tokens": 0,
            "total_completion_tokens": 0, "total_cost_usd": 0.0,
            "total_wall_clock_s": 0.0,
            "avg_s_per_filing": None, "failed_report_ids": [],
            "reconstructed_from": "no extracted_openai/ dir found",
        }

    for report_dir in sorted(mini_dir.iterdir()):
        if not report_dir.is_dir():
            continue
        for run_dir in report_dir.iterdir():
            if not run_dir.is_dir() or not run_dir.name.startswith(f"{run_label}_"):
                continue
            meta_path = run_dir / "extraction_run.json"
            if not meta_path.exists():
                continue
            meta = json.loads(meta_path.read_text())
            usage = meta.get("usage") or {}
            n_attempted += 1
            if (run_dir / "filing.json").exists():
                n_extracted += 1
            total_prompt += usage.get("prompt_tokens", 0)
            total_completion += usage.get("completion_tokens", 0)
            total_wall += meta.get("duration_seconds", 0.0)
            sa = meta.get("started_at")
            fa = meta.get("finished_at")
            if sa and (started_at_min is None or sa < started_at_min):
                started_at_min = sa
            if fa and (finished_at_max is None or fa > finished_at_max):
                finished_at_max = fa

    total_cost = (
        total_prompt / 1_000_000 * COST_PER_MTOK_PROMPT
        + total_completion / 1_000_000 * COST_PER_MTOK_COMPLETION
    )
    return {
        "run_label": run_label,
        "n_attempted": n_attempted,
        "n_extracted": n_extracted,
        "n_skipped_resume": 0,
        "n_failed": n_attempted - n_extracted,
        "total_prompt_tokens": total_prompt,
        "total_completion_tokens": total_completion,
        "total_cost_usd": round(total_cost, 4),
        "total_wall_clock_s": round(total_wall, 1),
        "avg_s_per_filing": (
            round(total_wall / n_extracted, 2) if n_extracted else None
        ),
        "failed_report_ids": [],
        "started_at": started_at_min,
        "finished_at": finished_at_max,
        "reconstructed_from": "on-disk extraction_run.json files (dispatch was killed mid-pass; summary not natively written)",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pass", dest="which_pass", required=True,
                        choices=["1", "2", "3"])
    parser.add_argument("--data-dir", default=str(DATA_DIR))
    parser.add_argument("--out", default=None,
                        help="Output path; default data_dir/extracted_openai/_summary_run<N>.json")
    args = parser.parse_args()
    data_dir = Path(args.data_dir)
    run_label = f"mini_run_{args.which_pass}"
    out = Path(args.out) if args.out else (
        data_dir / EXTRACTED_OPENAI_SUBDIR
        / f"_summary_run{args.which_pass}.json"
    )

    summary = reconstruct(run_label, data_dir)
    out.write_text(json.dumps(summary, indent=2))
    print(f"[reconstruct] wrote {out}", file=sys.stderr)
    print(json.dumps(summary, indent=2), file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
