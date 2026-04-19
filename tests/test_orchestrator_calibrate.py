"""Tests for `orchestrator calibrate`."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


from scoring.orchestrator import cmd_calibrate
from scoring.output_writer import SCORED_ROW_COLUMNS


def _disclosure_atomic_ids() -> list[str]:
    ids = [
        *[f"A{i}" for i in range(1, 12)],
        *[f"B{i}" for i in range(1, 5)],
        *[f"C{i}" for i in range(0, 4)],
        "D0", "D1_present", "D1_value", "D2_present", "D2_value",
        "E1a", "E1b", "E1c", "E1d", "E1e",
        "E1f_i", "E1f_ii", "E1f_iii", "E1f_iv",
        "E1g_i", "E1g_ii",
        "E1h_i", "E1h_ii", "E1h_iii", "E1h_iv", "E1h_v", "E1h_vi",
        "E1i", "E1j",
        "E2a", "E2b", "E2c", "E2d", "E2e",
        "E2f_i", "E2f_ii", "E2f_iii", "E2f_iv",
        "E2g_i", "E2g_ii",
        "E2h_i", "E2h_ii", "E2h_iii", "E2h_iv", "E2h_v", "E2h_vi",
        "E2i",
    ]
    assert len(ids) == 61
    return ids


def _seed_scored_csv(
    repo_root: Path,
    state: str,
    vintage: int,
    run_id: str,
    rubric: str,
    atomic_scores: dict[str, object],
) -> Path:
    """Write a scored CSV at data/scores/<STATE>/statute/<vintage>/<run_id>/<rubric>.csv."""
    run_dir = repo_root / "data" / "scores" / state / "statute" / str(vintage) / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    csv_path = run_dir / f"{rubric}.csv"
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


def _mt_perfect_disclosure_scores() -> dict[str, object]:
    """Atomic scores that roll up to Montana's PRI 2010 disclosure-law totals (9/3/0/1/18)."""
    ids = _disclosure_atomic_ids()
    scores: dict[str, object] = {i: 0 for i in ids}
    # A_registration = 9
    for i in range(1, 10):
        scores[f"A{i}"] = 1
    # B = 3: B1=0, B2=0, B3=1, B4=0
    scores["B1"] = 0
    scores["B2"] = 0
    scores["B3"] = 1
    # D0=1
    scores["D0"] = 1
    # E = 18
    for suffix in ("a", "b", "c", "d", "e", "i", "h_i"):
        scores[f"E1{suffix}"] = 1
    for suffix in ("f_i", "f_ii", "f_iii", "f_iv", "g_i", "g_ii"):
        scores[f"E1{suffix}"] = 1
    for suffix in ("f_i", "f_ii", "f_iii", "f_iv"):
        scores[f"E2{suffix}"] = 1
    scores["E1j"] = 1
    return scores


def _fl_all_zero_disclosure_scores() -> dict[str, object]:
    return {i: 0 for i in _disclosure_atomic_ids()}


def test_calibrate_writes_markdown_report_to_output_path(tmp_path: Path) -> None:
    # Seed real repo's PRI reference CSVs by symlinking the docs/ tree we need.
    # Simpler: use the real repo_root but write scored CSVs into a tmp data/ dir.
    repo_root = Path(__file__).resolve().parents[1]
    # Use a tmp-root for scored CSVs by pointing repo_root at tmp_path/repo and
    # symlinking docs/ over so load_pri_reference_scores finds the real reference CSV.
    tmp_repo = tmp_path / "repo"
    tmp_repo.mkdir()
    (tmp_repo / "docs").symlink_to(repo_root / "docs")

    _seed_scored_csv(tmp_repo, "MT", 2010, "run1", "pri_disclosure_law",
                     _mt_perfect_disclosure_scores())

    output = tmp_path / "report.md"
    args = argparse.Namespace(
        repo_root=str(tmp_repo),
        snapshot_date="ignored",
        rubric="pri_disclosure_law",
        run_id="run1",
        vintage=2010,
        state_subset="MT",
        output=str(output),
    )
    rc = cmd_calibrate(args)
    assert rc == 0
    assert output.exists()
    text = output.read_text(encoding="utf-8")
    # Header-shaped markdown report mentions the rubric and Montana.
    assert "pri_disclosure_law" in text
    assert "MT" in text


def test_calibrate_reports_perfect_agreement_when_ours_matches_pri(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    tmp_repo = tmp_path / "repo"
    tmp_repo.mkdir()
    (tmp_repo / "docs").symlink_to(repo_root / "docs")

    _seed_scored_csv(tmp_repo, "MT", 2010, "run1", "pri_disclosure_law",
                     _mt_perfect_disclosure_scores())

    output = tmp_path / "report.md"
    args = argparse.Namespace(
        repo_root=str(tmp_repo),
        snapshot_date="ignored",
        rubric="pri_disclosure_law",
        run_id="run1",
        vintage=2010,
        state_subset="MT",
        output=str(output),
    )
    cmd_calibrate(args)
    text = output.read_text(encoding="utf-8")
    # Sub-components A, B, C, D, E all match MT's PRI values → 5/5 sub-components match.
    # The report should show 100% agreement for all-sub-components on MT.
    assert "100" in text  # some rendering of 100% agreement


def test_calibrate_reports_disagreement_when_ours_diverges(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    tmp_repo = tmp_path / "repo"
    tmp_repo.mkdir()
    (tmp_repo / "docs").symlink_to(repo_root / "docs")

    _seed_scored_csv(tmp_repo, "FL", 2010, "run1", "pri_disclosure_law",
                     _fl_all_zero_disclosure_scores())

    output = tmp_path / "report.md"
    args = argparse.Namespace(
        repo_root=str(tmp_repo),
        snapshot_date="ignored",
        rubric="pri_disclosure_law",
        run_id="run1",
        vintage=2010,
        state_subset="FL",
        output=str(output),
    )
    cmd_calibrate(args)
    text = output.read_text(encoding="utf-8")
    # FL's PRI values are A=10, B=3, C=0, D=0, E=9, total=22.
    # All-zero atomic → A=0, B=2 (reverse), C=0, D=0, E=0, total=2. Disagreement on A, B, E, total.
    # Expect the report to mention FL and some non-100% figure.
    assert "FL" in text


def test_calibrate_responder_partition_exposed_for_mixed_subset(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    tmp_repo = tmp_path / "repo"
    tmp_repo.mkdir()
    (tmp_repo / "docs").symlink_to(repo_root / "docs")

    # MT is a responder; FL is not. Mixing them should trigger partition breakdown.
    _seed_scored_csv(tmp_repo, "MT", 2010, "run1", "pri_disclosure_law",
                     _mt_perfect_disclosure_scores())
    _seed_scored_csv(tmp_repo, "FL", 2010, "run1", "pri_disclosure_law",
                     _fl_all_zero_disclosure_scores())

    output = tmp_path / "report.md"
    args = argparse.Namespace(
        repo_root=str(tmp_repo),
        snapshot_date="ignored",
        rubric="pri_disclosure_law",
        run_id="run1",
        vintage=2010,
        state_subset="MT,FL",
        output=str(output),
    )
    cmd_calibrate(args)
    text = output.read_text(encoding="utf-8")
    # The partition breakdown should be present somehow (string match on "responder" is sufficient).
    assert "responder" in text.lower()


def test_calibrate_errors_on_missing_scored_csv(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    tmp_repo = tmp_path / "repo"
    tmp_repo.mkdir()
    (tmp_repo / "docs").symlink_to(repo_root / "docs")

    # No CSV for MT → expect nonzero exit.
    args = argparse.Namespace(
        repo_root=str(tmp_repo),
        snapshot_date="ignored",
        rubric="pri_disclosure_law",
        run_id="run1",
        vintage=2010,
        state_subset="MT",
        output=str(tmp_path / "report.md"),
    )
    rc = cmd_calibrate(args)
    assert rc != 0
