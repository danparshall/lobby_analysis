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

from scoring.bundle import build_statute_subagent_brief, build_subagent_brief
from scoring.calibration import (
    compute_agreement,
    load_atomic_scores_from_csv,
    load_pri_reference_scores,
    render_agreement_markdown,
    render_multi_run_agreement_markdown,
)
from scoring.consistency import (
    ConsistencyReport,
    compute_consistency,
    csv_path as portal_csv_path,
    render_markdown,
    statute_csv_path,
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
from scoring.models import StatuteRunMetadata
from scoring.rubric_loader import load_all_rubrics, load_rubric
from scoring.snapshot_loader import SNAPSHOT_DATE_DEFAULT, load_snapshot
from scoring.statute_loader import load_statute_bundle
from scoring.statute_retrieval import (
    PRI_RESPONDER_STATES,
    USPS_TO_JUSTIA_SLUG,
    retrieve_bundles_for_states,
    run_audit_to_csv,
)

RUBRIC_NAMES = ["pri_accessibility", "pri_disclosure_law", "focal_indicators"]

# Calibration runs score only the two PRI rubrics (no 2010 FOCAL reference exists).
CALIBRATION_RUBRIC_NAMES = ["pri_accessibility", "pri_disclosure_law"]


def run_dir(repo_root: Path, state: str, snapshot_date: str, run_id: str) -> Path:
    return repo_root / "data" / "scores" / state / snapshot_date / run_id


def statute_run_dir(
    repo_root: Path, state: str, vintage_year: int, run_id: str
) -> Path:
    return repo_root / "data" / "scores" / state / "statute" / str(vintage_year) / run_id


def statute_bundle_dir(repo_root: Path, state: str, vintage_year: int) -> Path:
    return repo_root / "data" / "statutes" / state / str(vintage_year)


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
        paths = {
            rid: portal_csv_path(repo_root, state, args.snapshot_date, rid, rubric_name)
            for rid in args.run_ids
        }
        reports.append(
            compute_consistency(state=state, rubric=rubric_name, csv_paths_by_run_id=paths)
        )
    print(render_markdown(reports))
    if args.output:
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(render_markdown(reports))
        print(f"\nReport written: {out}", flush=True)
    return 0


def cmd_calibrate_analyze_consistency(args: argparse.Namespace) -> int:
    """Compute inter-run disagreement for a statute-based calibration (state, rubric[s])."""
    repo_root = Path(args.repo_root).resolve()
    state = args.state.upper()
    vintage = int(args.vintage)
    rubrics = [args.rubric] if args.rubric else CALIBRATION_RUBRIC_NAMES
    reports: list[ConsistencyReport] = []
    for rubric_name in rubrics:
        paths = {
            rid: statute_csv_path(repo_root, state, vintage, rid, rubric_name)
            for rid in args.run_ids
        }
        reports.append(
            compute_consistency(state=state, rubric=rubric_name, csv_paths_by_run_id=paths)
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


def cmd_export_statute_manifests(args: argparse.Namespace) -> int:
    """Copy statute-bundle manifests from data/statutes/ to a committable path.

    data/ is gitignored across the project (it's a symlink in worktrees). For
    git-tracked provenance, small manifest files belong under docs/active/<branch>/results/.
    This subcommand mirrors `data/statutes/<STATE>/<YEAR>/manifest.json` to
    `<dest>/<STATE>/<YEAR>/manifest.json` without touching the bulk section text.
    """
    from shutil import copy2

    repo_root = Path(args.repo_root).resolve()
    source_root = Path(args.source) if args.source else repo_root / "data" / "statutes"
    dest_root = Path(args.dest).resolve()

    if not source_root.exists():
        print(json.dumps({"error": f"source not found: {source_root}"}))
        return 2

    copied: list[str] = []
    for manifest in sorted(source_root.glob("*/*/manifest.json")):
        state = manifest.parent.parent.name
        year = manifest.parent.name
        target = dest_root / state / year / "manifest.json"
        target.parent.mkdir(parents=True, exist_ok=True)
        copy2(manifest, target)
        try:
            rel = target.relative_to(repo_root)
        except ValueError:
            rel = target
        copied.append(str(rel))
    print(json.dumps(
        {"copied": len(copied), "targets": copied, "dest": str(dest_root)}, indent=2
    ))
    return 0


def cmd_calibrate_prepare_run(args: argparse.Namespace) -> int:
    """Prepare subagent briefs for a statute-based calibration run.

    Two rubrics: pri_accessibility + pri_disclosure_law. focal_indicators is
    skipped (no 2010 FOCAL reference). Briefs land at
    data/scores/<STATE>/statute/<vintage>/<run_id>/briefs/<rubric>.brief.md.
    """
    repo_root = Path(args.repo_root).resolve()
    state = args.state.upper()
    vintage = int(args.vintage)
    bundle_dir = statute_bundle_dir(repo_root, state, vintage)
    if not (bundle_dir / "manifest.json").exists():
        print(json.dumps({
            "error": "statute bundle not found",
            "state": state,
            "vintage": vintage,
            "expected_path": str(bundle_dir / "manifest.json"),
        }))
        return 2

    statute = load_statute_bundle(bundle_dir, repo_root)
    run_id = args.run_id or new_run_id()
    rd = statute_run_dir(repo_root, state, vintage, run_id)
    (rd / "briefs").mkdir(parents=True, exist_ok=True)
    (rd / "raw").mkdir(parents=True, exist_ok=True)

    results = []
    for rubric_name in CALIBRATION_RUBRIC_NAMES:
        rubric = load_rubric(rubric_name, repo_root)
        brief = build_statute_subagent_brief(
            state=state,
            rubric=rubric,
            statute=statute,
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
        "vintage_year": vintage,
        "year_delta": statute.year_delta,
        "direction": statute.direction,
        "rubrics": results,
    }, indent=2))
    return 0


def cmd_calibrate_finalize_run(args: argparse.Namespace) -> int:
    """Finalize a statute-based calibration run: validate raw JSON, write CSVs + metadata.

    Writes a StatuteRunMetadata (not RunMetadata) to run_metadata.json so downstream
    analysis can cleanly distinguish statute vs snapshot runs.
    """
    repo_root = Path(args.repo_root).resolve()
    state = args.state.upper()
    vintage = int(args.vintage)

    bundle_dir = statute_bundle_dir(repo_root, state, vintage)
    if not (bundle_dir / "manifest.json").exists():
        print(json.dumps({
            "error": "statute bundle not found",
            "state": state,
            "vintage": vintage,
            "expected_path": str(bundle_dir / "manifest.json"),
        }))
        return 2
    statute = load_statute_bundle(bundle_dir, repo_root)
    rd = statute_run_dir(repo_root, state, vintage, args.run_id)

    psha = prompt_sha(repo_root)
    run_ts = utc_now()
    rubrics_loaded = {n: load_rubric(n, repo_root) for n in CALIBRATION_RUBRIC_NAMES}

    per_rubric_status: list[dict] = []
    all_finalized = True
    for rubric_name in CALIBRATION_RUBRIC_NAMES:
        raw_path = raw_output_path(rd, rubric_name)
        out_csv = csv_output_path(rd, rubric_name)
        if out_csv.exists():
            per_rubric_status.append({"rubric": rubric_name, "status": "already"})
            continue
        if not raw_path.exists():
            all_finalized = False
            per_rubric_status.append({"rubric": rubric_name, "status": "missing_raw"})
            if args.skip_missing:
                continue
            print(json.dumps({"error": f"missing raw JSON for {rubric_name}", "path": str(raw_path)}))
            return 2
        rubric = rubrics_loaded[rubric_name]
        scored_items = parse_and_validate(raw_path, rubric)
        rows = stamp_rows(
            scored_items,
            state=state,
            rubric=rubric,
            coverage_tier="clean",  # statute runs have no WAF/SPA semantics
            prompt_sha_hex=psha,
            snapshot_manifest_sha=statute.manifest_sha,  # re-used column for corpus sha
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
    if all_finalized:
        meta = StatuteRunMetadata(
            state=state,
            run_id=args.run_id,
            run_timestamp=run_ts,
            vintage_year=statute.vintage_year,
            year_delta=statute.year_delta,
            direction=statute.direction,
            pri_state_reviewed=statute.pri_state_reviewed,
            statute_manifest_sha=statute.manifest_sha,
            prompt_sha=psha,
            prompt_path=str(PROMPT_PATH),
            model_version="claude-sonnet-4-6",
            rubric_shas={n: r.sha for n, r in rubrics_loaded.items()},
        )
        (rd / "run_metadata.json").write_text(
            meta.model_dump_json(indent=2), encoding="utf-8"
        )
        wrote_metadata = True

    print(json.dumps({
        "state": state,
        "run_id": args.run_id,
        "vintage_year": vintage,
        "per_rubric": per_rubric_status,
        "wrote_metadata": wrote_metadata,
    }, indent=2))
    return 0


def cmd_calibrate(args: argparse.Namespace) -> int:
    """Compute agreement between N LLM-scored statute runs and PRI 2010 reference scores.

    Reads scored CSVs from data/scores/<STATE>/statute/<vintage>/<run_id>/<rubric>.csv
    for every (state, run_id) in the subset × --run-id list, applies the rollup
    spec'd in docs/historical/pri-calibration/results/20260419_pri_rollup_rule_spec.md,
    and emits a markdown report. For N>1 runs, the report includes per-run
    agreement sections plus a cross-run variance table so reviewers can tell
    stable-disagreement (rubric/prompt issue) from scorer-noise (self-consistency).
    """
    repo_root = Path(args.repo_root).resolve()
    states = [s.strip().upper() for s in args.state_subset.split(",") if s.strip()]
    if not states:
        print(json.dumps({"error": "--state-subset must list at least one USPS code"}))
        return 2

    run_ids: list[str] = list(args.run_ids)
    if not run_ids:
        print(json.dumps({"error": "--run-id must list at least one run_id"}))
        return 2

    pri_by_state = load_pri_reference_scores(args.rubric, repo_root)
    missing_from_pri = set(states) - set(pri_by_state)
    if missing_from_pri:
        print(json.dumps({
            "error": "state(s) have no PRI 2010 reference",
            "states": sorted(missing_from_pri),
        }))
        return 2

    reports: list = []
    for run_id in run_ids:
        ours_atomic_by_state: dict[str, dict[str, object]] = {}
        for state in states:
            csv_path = (
                repo_root / "data" / "scores" / state / "statute" / str(args.vintage)
                / run_id / f"{args.rubric}.csv"
            )
            if not csv_path.exists():
                print(json.dumps({
                    "error": "scored CSV not found",
                    "state": state,
                    "run_id": run_id,
                    "expected_path": str(csv_path),
                }))
                return 2
            ours_atomic_by_state[state] = load_atomic_scores_from_csv(csv_path)
        reports.append(compute_agreement(
            ours_atomic_by_state=ours_atomic_by_state,
            pri_by_state={s: pri_by_state[s] for s in states},
            rubric=args.rubric,
            trust_partition=PRI_RESPONDER_STATES,
            trust_partition_label="PRI 2010 responders",
        ))

    if len(reports) == 1:
        markdown = render_agreement_markdown(reports[0])
    else:
        markdown = render_multi_run_agreement_markdown(reports, run_ids=run_ids)

    if args.output:
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(markdown, encoding="utf-8")
        print(json.dumps({
            "rubric": args.rubric,
            "run_ids": run_ids,
            "vintage": args.vintage,
            "states": states,
            "output": str(out),
        }, indent=2))
    else:
        print(markdown)
    return 0


def cmd_retrieve_statutes(args: argparse.Namespace) -> int:
    """Retrieve statute bundles from Justia for (state, vintage) targets.

    Three invocation modes:
      --state CA --vintage 2010       one pair
      --calibration-subset            all 5 pairs in CALIBRATION_SUBSET
      (otherwise error)
    """
    from scoring.justia_client import PlaywrightClient
    from scoring.lobbying_statute_urls import (
        CALIBRATION_SUBSET,
        LOBBYING_STATUTE_URLS,
    )

    repo_root = Path(args.repo_root).resolve()
    dest_root = Path(args.output_dir) if args.output_dir else repo_root / "data" / "statutes"

    if args.calibration_subset:
        targets = list(CALIBRATION_SUBSET)
    elif args.state and args.vintage is not None:
        state = args.state.upper()
        if (state, args.vintage) not in LOBBYING_STATUTE_URLS:
            print(json.dumps({
                "error": f"no curated URLs for ({state}, {args.vintage})",
                "available": sorted(str(k) for k in LOBBYING_STATUTE_URLS),
            }))
            return 2
        targets = [(state, args.vintage)]
    else:
        print(json.dumps({
            "error": "must supply --calibration-subset or both --state and --vintage",
        }))
        return 2

    client = PlaywrightClient(rate_limit_seconds=args.rate_limit_seconds)
    manifest_paths = retrieve_bundles_for_states(
        client=client,
        targets=targets,
        dest_root=dest_root,
        target_year=args.target_year,
    )
    print(json.dumps({
        "retrieved": len(manifest_paths),
        "manifests": [str(p) for p in manifest_paths],
        "dest_root": str(dest_root),
    }, indent=2))
    return 0


def cmd_expand_bundle(args: argparse.Namespace) -> int:
    """Generate a retrieval-agent brief for cross-reference discovery.

    Loads the existing statute bundle and the PRI disclosure-law rubric,
    builds a retrieval-agent brief, and writes it to the bundle directory.
    A human or orchestrating agent then dispatches a subagent with this brief.
    """
    from scoring.bundle import build_retrieval_subagent_brief
    from scoring.rubric_loader import load_rubric
    from scoring.statute_loader import load_statute_bundle

    repo_root = Path(args.repo_root).resolve()
    state = args.state.upper()
    bundle_dir = repo_root / "data" / "statutes" / state / str(args.vintage)
    statute = load_statute_bundle(bundle_dir, repo_root)
    rubric = load_rubric("pri_disclosure_law", repo_root)

    hop = args.hop
    output_json_path = bundle_dir / f"crossrefs_hop{hop}.json"
    brief = build_retrieval_subagent_brief(
        state=state,
        rubric=rubric,
        statute=statute,
        repo_root=repo_root,
        retrieval_prompt_path=repo_root / "src/scoring/retrieval_agent_prompt.md",
        output_json_path=output_json_path,
        hop=hop,
    )
    brief_path = bundle_dir / f"retrieval_brief_hop{hop}.md"
    brief_path.write_text(brief, encoding="utf-8")
    print(json.dumps({
        "brief_path": str(brief_path),
        "output_json_path": str(output_json_path),
        "state": state,
        "vintage": args.vintage,
        "hop": hop,
        "artifact_count": len(statute.artifacts),
    }, indent=2))
    return 0


def cmd_ingest_crossrefs(args: argparse.Namespace) -> int:
    """Fetch cross-referenced support chapters and update the manifest.

    Reads the retrieval agent's output JSON, fetches each URL not already
    in the bundle, and appends support_chapter artifacts to the manifest.
    """
    from scoring.justia_client import PlaywrightClient
    from scoring.statute_retrieval import ingest_crossrefs

    repo_root = Path(args.repo_root).resolve()
    state = args.state.upper()
    bundle_dir = repo_root / "data" / "statutes" / state / str(args.vintage)
    crossrefs_path = Path(args.crossrefs) if args.crossrefs else bundle_dir / f"crossrefs_hop{args.hop}.json"

    if not crossrefs_path.exists():
        print(json.dumps({"error": f"crossrefs file not found: {crossrefs_path}"}))
        return 2

    client = PlaywrightClient(rate_limit_seconds=args.rate_limit_seconds)
    new_files = ingest_crossrefs(
        client=client,
        bundle_dir=bundle_dir,
        crossrefs_path=crossrefs_path,
    )
    print(json.dumps({
        "ingested": len(new_files),
        "new_sections": [f.name for f in new_files],
        "bundle_dir": str(bundle_dir),
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

    p_retrieve = sub.add_parser(
        "retrieve-statutes",
        help="retrieve curated lobby-statute URL lists from Justia per state/vintage",
    )
    p_retrieve.add_argument("--state", default=None, help="USPS state code (e.g. CA)")
    p_retrieve.add_argument(
        "--vintage", type=int, default=None, help="vintage year (e.g. 2010)"
    )
    p_retrieve.add_argument(
        "--calibration-subset",
        action="store_true",
        help="retrieve all 5 (state, vintage) pairs in CALIBRATION_SUBSET",
    )
    p_retrieve.add_argument(
        "--output-dir",
        default=None,
        help="destination root (default: <repo_root>/data/statutes)",
    )
    p_retrieve.add_argument(
        "--target-year",
        type=int,
        default=2010,
        help="for year_delta/direction computation; default 2010 (calibration)",
    )
    p_retrieve.add_argument(
        "--rate-limit-seconds",
        type=float,
        default=2.0,
        help="courtesy delay between Justia fetches (see Phase 2 A4 decision)",
    )
    p_retrieve.set_defaults(func=cmd_retrieve_statutes)

    p_expand = sub.add_parser(
        "expand-bundle",
        help="generate a retrieval-agent brief for cross-reference discovery",
    )
    p_expand.add_argument("--state", required=True, help="USPS state code (e.g. OH)")
    p_expand.add_argument("--vintage", type=int, required=True, help="vintage year (e.g. 2010)")
    p_expand.add_argument("--hop", type=int, default=1, help="hop number (default 1)")
    p_expand.set_defaults(func=cmd_expand_bundle)

    p_ingest = sub.add_parser(
        "ingest-crossrefs",
        help="fetch cross-referenced support chapters and update the manifest",
    )
    p_ingest.add_argument("--state", required=True, help="USPS state code (e.g. OH)")
    p_ingest.add_argument("--vintage", type=int, required=True, help="vintage year (e.g. 2010)")
    p_ingest.add_argument("--hop", type=int, default=1, help="hop number (default 1)")
    p_ingest.add_argument("--crossrefs", default=None, help="path to crossrefs JSON (default: bundle_dir/crossrefs_hopN.json)")
    p_ingest.add_argument(
        "--rate-limit-seconds",
        type=float,
        default=2.0,
        help="courtesy delay between Justia fetches",
    )
    p_ingest.set_defaults(func=cmd_ingest_crossrefs)

    p_cal_prep = sub.add_parser(
        "calibrate-prepare-run",
        help="prepare briefs for 2 PRI rubrics against a statute bundle (calibration run)",
    )
    p_cal_prep.add_argument("--state", required=True)
    p_cal_prep.add_argument("--vintage", type=int, required=True)
    p_cal_prep.add_argument("--run-id", default=None)
    p_cal_prep.set_defaults(func=cmd_calibrate_prepare_run)

    p_cal_fin = sub.add_parser(
        "calibrate-finalize-run",
        help="finalize a statute calibration run: validate raw JSON, write CSVs + metadata",
    )
    p_cal_fin.add_argument("--state", required=True)
    p_cal_fin.add_argument("--vintage", type=int, required=True)
    p_cal_fin.add_argument("--run-id", required=True)
    p_cal_fin.add_argument(
        "--skip-missing",
        action="store_true",
        help="finalize whichever rubrics have raw JSON; skip the rest without erroring",
    )
    p_cal_fin.set_defaults(func=cmd_calibrate_finalize_run)

    p_cal_cons = sub.add_parser(
        "calibrate-analyze-consistency",
        help="inter-run disagreement across statute-based calibration runs",
    )
    p_cal_cons.add_argument("--state", required=True)
    p_cal_cons.add_argument("--vintage", type=int, required=True)
    p_cal_cons.add_argument(
        "--rubric",
        choices=CALIBRATION_RUBRIC_NAMES,
        default=None,
        help="omit to analyze both PRI rubrics",
    )
    p_cal_cons.add_argument("--run-ids", nargs="+", required=True)
    p_cal_cons.add_argument("--output", default=None)
    p_cal_cons.set_defaults(func=cmd_calibrate_analyze_consistency)

    p_cal = sub.add_parser(
        "calibrate",
        help="compare LLM scored statute run against PRI 2010 published sub-aggregates",
    )
    p_cal.add_argument(
        "--rubric", required=True, choices=["pri_disclosure_law", "pri_accessibility"]
    )
    p_cal.add_argument(
        "--run-id",
        dest="run_ids",
        nargs="+",
        required=True,
        help="one or more run_ids; with N>1, report includes cross-run variance",
    )
    p_cal.add_argument(
        "--vintage",
        type=int,
        default=2010,
        help="statute vintage year (selects subdir under data/scores/<STATE>/statute/)",
    )
    p_cal.add_argument(
        "--state-subset",
        required=True,
        help="comma-separated USPS codes (e.g. CA,TX,WY,NY,WI)",
    )
    p_cal.add_argument(
        "--output",
        default=None,
        help="markdown output path; stdout if omitted",
    )
    p_cal.set_defaults(func=cmd_calibrate)

    p_export = sub.add_parser(
        "export-statute-manifests",
        help="copy statute-bundle manifests from data/statutes/ to a committable path",
    )
    p_export.add_argument(
        "--source",
        default=None,
        help="source root (default: <repo_root>/data/statutes)",
    )
    p_export.add_argument(
        "--dest",
        required=True,
        help="destination root, typically docs/active/<branch>/results/statute_manifests",
    )
    p_export.set_defaults(func=cmd_export_statute_manifests)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
