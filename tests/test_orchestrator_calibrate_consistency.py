"""Tests for `orchestrator calibrate-analyze-consistency`.

Statute-path counterpart of `analyze-consistency`. Reads scored CSVs from
data/scores/<STATE>/statute/<vintage>/<run_id>/<rubric>.csv and reports
inter-run disagreement exactly as the portal-pipeline version does.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

from scoring.orchestrator import cmd_calibrate_analyze_consistency, statute_run_dir
from scoring.output_writer import SCORED_ROW_COLUMNS


def _seed_statute_scored_csv(
    repo_root: Path,
    state: str,
    vintage: int,
    run_id: str,
    rubric: str,
    atomic_scores: dict[str, object],
) -> Path:
    rd = statute_run_dir(repo_root, state, vintage, run_id)
    rd.mkdir(parents=True, exist_ok=True)
    csv_path = rd / f"{rubric}.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=SCORED_ROW_COLUMNS)
        writer.writeheader()
        for item_id, score in atomic_scores.items():
            writer.writerow({
                "state": state,
                "rubric_name": rubric,
                "item_id": item_id,
                "score": "" if score is None else score,
                "evidence_quote_or_url": "fixture",
                "source_artifact": "fixture",
                "confidence": "high",
                "unable_to_evaluate": "true" if score is None else "false",
                "notes": "",
                "coverage_tier": "clean",
                "model_version": "fixture",
                "prompt_sha": "0" * 64,
                "rubric_sha": "0" * 64,
                "snapshot_manifest_sha": "0" * 64,
                "run_id": run_id,
                "run_timestamp": "2026-04-19T00:00:00+00:00",
            })
    return csv_path


def _two_item_fixture(a1: int, a2: int) -> dict[str, object]:
    return {"A1": a1, "A2": a2}


def test_calibrate_analyze_consistency_reports_unanimous_when_runs_agree(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()

    _seed_statute_scored_csv(repo, "TX", 2009, "r1", "pri_disclosure_law",
                             _two_item_fixture(1, 0))
    _seed_statute_scored_csv(repo, "TX", 2009, "r2", "pri_disclosure_law",
                             _two_item_fixture(1, 0))
    _seed_statute_scored_csv(repo, "TX", 2009, "r3", "pri_disclosure_law",
                             _two_item_fixture(1, 0))

    output = tmp_path / "report.md"
    args = argparse.Namespace(
        repo_root=str(repo),
        snapshot_date="ignored",
        state="TX",
        vintage=2009,
        rubric="pri_disclosure_law",
        run_ids=["r1", "r2", "r3"],
        output=str(output),
    )
    rc = cmd_calibrate_analyze_consistency(args)
    assert rc == 0
    text = output.read_text(encoding="utf-8")
    assert "TX" in text
    # 100% unanimous → 0% disagreement rate.
    assert "0.00%" in text or "0%" in text


def test_calibrate_analyze_consistency_surfaces_disagreement(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()

    _seed_statute_scored_csv(repo, "TX", 2009, "r1", "pri_disclosure_law",
                             _two_item_fixture(1, 0))
    _seed_statute_scored_csv(repo, "TX", 2009, "r2", "pri_disclosure_law",
                             _two_item_fixture(0, 1))  # flipped both
    _seed_statute_scored_csv(repo, "TX", 2009, "r3", "pri_disclosure_law",
                             _two_item_fixture(1, 0))

    output = tmp_path / "report.md"
    args = argparse.Namespace(
        repo_root=str(repo),
        snapshot_date="ignored",
        state="TX",
        vintage=2009,
        rubric="pri_disclosure_law",
        run_ids=["r1", "r2", "r3"],
        output=str(output),
    )
    cmd_calibrate_analyze_consistency(args)
    text = output.read_text(encoding="utf-8")
    # Both items disagree across runs → 100% disagreement.
    assert "100.00%" in text
    # Flagged-items section should mention A1 and A2.
    assert "A1" in text
    assert "A2" in text


def test_calibrate_analyze_consistency_runs_both_rubrics_when_rubric_omitted(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()

    # Seed both PRI rubrics with 2 agreeing runs each.
    for rubric in ("pri_disclosure_law", "pri_accessibility"):
        for rid in ("r1", "r2"):
            _seed_statute_scored_csv(repo, "WY", 2010, rid, rubric,
                                     _two_item_fixture(1, 0))

    output = tmp_path / "report.md"
    args = argparse.Namespace(
        repo_root=str(repo),
        snapshot_date="ignored",
        state="WY",
        vintage=2010,
        rubric=None,  # omitted = all calibration rubrics
        run_ids=["r1", "r2"],
        output=str(output),
    )
    rc = cmd_calibrate_analyze_consistency(args)
    assert rc == 0
    text = output.read_text(encoding="utf-8")
    assert "pri_disclosure_law" in text
    assert "pri_accessibility" in text
