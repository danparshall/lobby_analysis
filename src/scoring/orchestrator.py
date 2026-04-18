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
from scoring.consistency import (
    ConsistencyReport,
    compute_consistency,
    render_markdown,
)
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
from scoring.statute_retrieval import USPS_TO_JUSTIA_SLUG, run_audit_to_csv

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


def cmd_prepare_run(args: argparse.Namespace) -> int:
    """Prepare briefs for all 3 rubrics in one pass, sharing a run_id."""
    repo_root = Path(args.repo_root).resolve()
    state = args.state.upper()
    run_id = args.run_id or new_run_id()
    results = []
    for rubric_name in RUBRIC_NAMES:
        rubric = load_rubric(rubric_name, repo_root)
        snapshot = load_snapshot(state, repo_root, args.snapshot_date)
        rd = run_dir(repo_root, state, snapshot.snapshot_date, run_id)
        (rd / "briefs").mkdir(parents=True, exist_ok=True)
        (rd / "raw").mkdir(parents=True, exist_ok=True)
        brief = build_subagent_brief(
            state=state,
            rubric=rubric,
            snapshot=snapshot,
            repo_root=repo_root,
            scorer_prompt_path=repo_root / PROMPT_PATH,
            output_json_path=raw_output_path(rd, rubric_name),
        )
        bp = brief_path(rd, rubric_name)
        bp.write_text(brief, encoding="utf-8")
        results.append({
            "rubric": rubric_name,
            "brief_path": str(bp),
            "expected_output_path": str(raw_output_path(rd, rubric_name)),
            "item_count": len(rubric.items),
        })
    print(json.dumps({
        "run_id": run_id,
        "state": state,
        "coverage_tier": coverage_tier_for(state),
        "rubrics": results,
    }, indent=2))
    return 0


def cmd_finalize_run(args: argparse.Namespace) -> int:
    """Finalize all 3 rubrics for one (state, run_id), writing run_metadata at the end.

    Skips rubrics that already have a CSV. Errors if any required raw JSON is missing
    unless --skip-missing is set.
    """
    repo_root = Path(args.repo_root).resolve()
    state = args.state.upper()
    snapshot = load_snapshot(state, repo_root, args.snapshot_date)
    rd = run_dir(repo_root, state, snapshot.snapshot_date, args.run_id)

    tier = coverage_tier_for(state)
    psha = prompt_sha(repo_root)
    run_ts = utc_now()

    per_rubric_status: list[dict] = []
    all_rubrics_finalized = True
    for rubric_name in RUBRIC_NAMES:
        raw_path = raw_output_path(rd, rubric_name)
        out_csv = csv_output_path(rd, rubric_name)
        if out_csv.exists():
            per_rubric_status.append({"rubric": rubric_name, "status": "already"})
            continue
        if not raw_path.exists():
            all_rubrics_finalized = False
            per_rubric_status.append({"rubric": rubric_name, "status": "missing_raw"})
            if args.skip_missing:
                continue
            print(json.dumps({"error": f"missing raw JSON for {rubric_name}", "path": str(raw_path)}))
            return 2
        rubric = load_rubric(rubric_name, repo_root)
        scored_items = parse_and_validate(raw_path, rubric)
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
        write_scored_csv(rows, out_csv)
        per_rubric_status.append({
            "rubric": rubric_name,
            "status": "finalized",
            "rows": len(rows),
            "unable_to_evaluate_count": sum(1 for r in rows if r.unable_to_evaluate),
        })

    wrote_metadata = False
    if all_rubrics_finalized:
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
        wrote_metadata = True

    print(json.dumps({
        "state": state,
        "run_id": args.run_id,
        "coverage_tier": tier,
        "per_rubric": per_rubric_status,
        "wrote_metadata": wrote_metadata,
    }, indent=2))
    return 0


def cmd_analyze_consistency(args: argparse.Namespace) -> int:
    """Compute inter-run disagreement for a (state, rubric) triad, or for all three rubrics."""
    repo_root = Path(args.repo_root).resolve()
    state = args.state.upper()
    rubrics = [args.rubric] if args.rubric else RUBRIC_NAMES
    reports: list[ConsistencyReport] = []
    for rubric_name in rubrics:
        reports.append(
            compute_consistency(
                repo_root=repo_root,
                state=state,
                rubric=rubric_name,
                run_ids=list(args.run_ids),
                snapshot_date=args.snapshot_date,
            )
        )
    print(render_markdown(reports))
    if args.output:
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(render_markdown(reports))
        print(f"\nReport written: {out}", flush=True)
    return 0


def cmd_audit_statutes(args: argparse.Namespace) -> int:
    """Audit Justia year-availability for a list of states (default: all 50)."""
    from scoring.justia_client import PlaywrightClient

    states = args.states or sorted(USPS_TO_JUSTIA_SLUG.keys())
    out_path = Path(args.output_csv)
    client = PlaywrightClient(rate_limit_seconds=args.rate_limit_seconds)
    results = run_audit_to_csv(
        client=client,
        states=states,
        target_year=args.target_year,
        tolerance=args.tolerance,
        out_path=out_path,
    )
    print(json.dumps({
        "audited": len(results),
        "eligible_for_calibration": sum(1 for r in results if r.eligible_for_calibration),
        "eligible_for_2026_scoring": sum(1 for r in results if r.eligible_for_2026_scoring),
        "output_csv": str(out_path),
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

    p_fin = sub.add_parser("finalize", help="validate subagent output + write CSV (one rubric)")
    p_fin.add_argument("--state", required=True)
    p_fin.add_argument("--rubric", required=True, choices=RUBRIC_NAMES)
    p_fin.add_argument("--run-id", required=True)
    p_fin.add_argument(
        "--write-metadata",
        action="store_true",
        help="also write run_metadata.json (pass on the last rubric of the pass)",
    )
    p_fin.set_defaults(func=cmd_finalize)

    p_prep_run = sub.add_parser(
        "prepare-run", help="prepare briefs for all 3 rubrics of a (state, run_id) in one call"
    )
    p_prep_run.add_argument("--state", required=True)
    p_prep_run.add_argument("--run-id", default=None)
    p_prep_run.set_defaults(func=cmd_prepare_run)

    p_fin_run = sub.add_parser(
        "finalize-run",
        help="finalize all 3 rubrics of a (state, run_id) and write run_metadata when complete",
    )
    p_fin_run.add_argument("--state", required=True)
    p_fin_run.add_argument("--run-id", required=True)
    p_fin_run.add_argument(
        "--skip-missing",
        action="store_true",
        help="finalize whichever rubrics have raw JSON; skip the rest without erroring",
    )
    p_fin_run.set_defaults(func=cmd_finalize_run)

    p_cons = sub.add_parser(
        "analyze-consistency",
        help="compute inter-run disagreement for (state, rubric?) across N run-ids",
    )
    p_cons.add_argument("--state", required=True)
    p_cons.add_argument(
        "--rubric",
        choices=RUBRIC_NAMES,
        default=None,
        help="omit to analyze all 3 rubrics",
    )
    p_cons.add_argument("--run-ids", nargs="+", required=True)
    p_cons.add_argument("--output", default=None, help="optional markdown output path")
    p_cons.set_defaults(func=cmd_analyze_consistency)

    p_audit = sub.add_parser(
        "audit-statutes",
        help="audit Justia year-availability across states; emit eligibility CSV",
    )
    p_audit.add_argument(
        "--states",
        nargs="*",
        default=None,
        help="USPS state codes to audit (default: all 50)",
    )
    p_audit.add_argument("--target-year", type=int, default=2010)
    p_audit.add_argument("--tolerance", type=int, default=2)
    p_audit.add_argument("--output-csv", required=True)
    p_audit.add_argument(
        "--rate-limit-seconds",
        type=float,
        default=5.0,
        help="courtesy delay between state fetches",
    )
    p_audit.set_defaults(func=cmd_audit_statutes)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
