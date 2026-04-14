"""Per-state scoring orchestrator.

Architectural note: the LLM is invoked via the Claude Code Agent tool (subagent-only,
no anthropic SDK). This module therefore has two CLI subcommands:

  1. `prepare` — load snapshot + rubric, assemble subagent brief, write it to disk,
     print the path. The orchestrating agent then dispatches an Agent subagent using
     that brief and instructs the subagent to write its JSON output to the paired
     output path.

  2. `finalize` — read the subagent's JSON output, validate against pydantic,
     stamp provenance columns, write the final CSV and (on the last rubric of a run)
     the run_metadata.json.

Layout under `data/scores/<STATE>/<RUN_DATE>/<RUN_ID>/`:

    briefs/pri_accessibility.brief.md           (prepare)
    briefs/pri_disclosure_law.brief.md          (prepare)
    briefs/focal_indicators.brief.md            (prepare)
    raw/pri_accessibility.json                  (subagent writes)
    raw/pri_disclosure_law.json                 (subagent writes)
    raw/focal_indicators.json                   (subagent writes)
    pri_accessibility.csv                       (finalize)
    pri_disclosure_law.csv                      (finalize)
    focal_indicators.csv                        (finalize)
    run_metadata.json                           (finalize --write-metadata)

The `<RUN_ID>` dir preserves raw subagent outputs so Phase-3 self-consistency can keep
all three temp-0 runs alongside any adjudicated rows without overwriting.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from scoring.bundle import build_subagent_brief
from scoring.coverage import coverage_tier_for
from scoring.output_writer import parse_and_validate, write_scored_csv
from scoring.provenance import (
    PROMPT_PATH,
    build_run_metadata,
    new_run_id,
    prompt_sha,
    stamp_rows,
    utc_now,
)
from scoring.rubric_loader import load_all_rubrics, load_rubric
from scoring.snapshot_loader import SNAPSHOT_DATE_DEFAULT, load_snapshot

RUBRIC_NAMES = ["pri_accessibility", "pri_disclosure_law", "focal_indicators"]


def run_dir(repo_root: Path, state: str, snapshot_date: str, run_id: str) -> Path:
    return repo_root / "data" / "scores" / state / snapshot_date / run_id


def brief_path(run_dir_: Path, rubric: str) -> Path:
    return run_dir_ / "briefs" / f"{rubric}.brief.md"


def raw_output_path(run_dir_: Path, rubric: str) -> Path:
    return run_dir_ / "raw" / f"{rubric}.json"


def csv_output_path(run_dir_: Path, rubric: str) -> Path:
    return run_dir_ / f"{rubric}.csv"


def cmd_prepare(args: argparse.Namespace) -> int:
    repo_root = Path(args.repo_root).resolve()
    state = args.state.upper()
    rubric = load_rubric(args.rubric, repo_root)
    snapshot = load_snapshot(state, repo_root, args.snapshot_date)
    run_id = args.run_id or new_run_id()
    rd = run_dir(repo_root, state, snapshot.snapshot_date, run_id)
    (rd / "briefs").mkdir(parents=True, exist_ok=True)
    (rd / "raw").mkdir(parents=True, exist_ok=True)

    brief = build_subagent_brief(
        state=state,
        rubric=rubric,
        snapshot=snapshot,
        repo_root=repo_root,
        scorer_prompt_path=repo_root / PROMPT_PATH,
        output_json_path=raw_output_path(rd, args.rubric),
    )
    bp = brief_path(rd, args.rubric)
    bp.write_text(brief, encoding="utf-8")
    print(json.dumps({
        "run_id": run_id,
        "state": state,
        "rubric": args.rubric,
        "brief_path": str(bp),
        "expected_output_path": str(raw_output_path(rd, args.rubric)),
        "coverage_tier": coverage_tier_for(state),
        "item_count": len(rubric.items),
    }, indent=2))
    return 0


def cmd_finalize(args: argparse.Namespace) -> int:
    repo_root = Path(args.repo_root).resolve()
    state = args.state.upper()
    rubric = load_rubric(args.rubric, repo_root)
    snapshot = load_snapshot(state, repo_root, args.snapshot_date)
    rd = run_dir(repo_root, state, snapshot.snapshot_date, args.run_id)

    scored_items = parse_and_validate(raw_output_path(rd, args.rubric), rubric)
    tier = coverage_tier_for(state)
    psha = prompt_sha(repo_root)
    run_ts = utc_now()
    rows = stamp_rows(
        scored_items,
        state=state,
        rubric=rubric,
        coverage_tier=tier,
        prompt_sha_hex=psha,
        snapshot_manifest_sha=snapshot.manifest_sha,
        run_id=args.run_id,
        run_timestamp=run_ts,
    )
    out_csv = csv_output_path(rd, args.rubric)
    write_scored_csv(rows, out_csv)

    if args.write_metadata:
        rubrics = load_all_rubrics(repo_root)
        meta = build_run_metadata(
            state=state,
            run_id=args.run_id,
            run_timestamp=run_ts,
            snapshot_date=snapshot.snapshot_date,
            snapshot_manifest_sha=snapshot.manifest_sha,
            prompt_sha_hex=psha,
            rubrics=rubrics,
            coverage_tier=tier,
        )
        (rd / "run_metadata.json").write_text(
            meta.model_dump_json(indent=2), encoding="utf-8"
        )

    print(json.dumps({
        "csv": str(out_csv),
        "rows": len(rows),
        "unable_to_evaluate_count": sum(1 for r in rows if r.unable_to_evaluate),
        "coverage_tier": tier,
        "wrote_metadata": bool(args.write_metadata),
    }, indent=2))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(prog="scoring-orchestrator")
    parser.add_argument("--repo-root", default=".", help="repo root (worktree path)")
    parser.add_argument("--snapshot-date", default=SNAPSHOT_DATE_DEFAULT)
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_prep = sub.add_parser("prepare", help="write subagent brief for one (state, rubric)")
    p_prep.add_argument("--state", required=True)
    p_prep.add_argument("--rubric", required=True, choices=RUBRIC_NAMES)
    p_prep.add_argument("--run-id", default=None, help="reuse across rubrics in one pass")
    p_prep.set_defaults(func=cmd_prepare)

    p_fin = sub.add_parser("finalize", help="validate subagent output + write CSV")
    p_fin.add_argument("--state", required=True)
    p_fin.add_argument("--rubric", required=True, choices=RUBRIC_NAMES)
    p_fin.add_argument("--run-id", required=True)
    p_fin.add_argument(
        "--write-metadata",
        action="store_true",
        help="also write run_metadata.json (pass on the last rubric of the pass)",
    )
    p_fin.set_defaults(func=cmd_finalize)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
