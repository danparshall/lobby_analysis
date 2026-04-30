"""Tests for `orchestrator calibrate-prepare-run` and `calibrate-finalize-run`.

These are the statute-pipeline counterparts of `prepare-run`/`finalize-run` (which
run against portal snapshots). They:
  - Use `load_statute_bundle` in place of `load_snapshot`.
  - Use `build_statute_subagent_brief` in place of `build_subagent_brief`.
  - Score only the two PRI rubrics (pri_accessibility + pri_disclosure_law);
    focal_indicators is skipped because no 2010 FOCAL reference exists.
  - Output to `data/scores/<STATE>/statute/<vintage>/<run_id>/` to disambiguate
    from portal runs.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from scoring.orchestrator import (
    CALIBRATION_RUBRIC_NAMES,
    cmd_calibrate_finalize_run,
    cmd_calibrate_prepare_run,
    statute_run_dir,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


# ---------------------------------------------------------------------------
# Fixtures: seed a minimal real StatuteBundle directory that load_statute_bundle
# can validate (correct sha256 + manifest shape) under a tmp repo_root.
# ---------------------------------------------------------------------------


def _seed_statute_bundle(repo_root: Path, state: str, vintage: int) -> Path:
    bundle_dir = repo_root / "data" / "statutes" / state / str(vintage)
    sections = bundle_dir / "sections"
    sections.mkdir(parents=True)
    section_file = sections / "fake-305.txt"
    section_file.write_text(
        "Chapter 305. Registration of Lobbyists.\nA person who engages in lobbying...",
        encoding="utf-8",
    )
    raw = section_file.read_bytes()
    manifest = {
        "state_abbr": state,
        "vintage_year": vintage,
        "year_delta": 0,
        "direction": "exact",
        "pri_state_reviewed": True,
        "retrieved_at": "2026-04-18T21:00:00+00:00",
        "artifacts": [
            {
                "url": f"https://law.justia.com/codes/{state.lower()}/{vintage}/fake-305.html",
                "role": "statute",
                "sha256": hashlib.sha256(raw).hexdigest(),
                "bytes": len(raw),
                "local_path": "sections/fake-305.txt",
            }
        ],
    }
    (bundle_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8"
    )
    return bundle_dir


def _tmp_repo_root(tmp_path: Path) -> Path:
    """Build a tmp repo root that symlinks docs/ and src/ from the real repo.

    Symlinking docs/ lets load_rubric find the 2026 rubric CSVs; symlinking
    src/ lets prompt_sha compute against the real scorer_prompt.md. We only
    write under <tmp_repo>/data/.
    """
    tmp_repo = tmp_path / "repo"
    tmp_repo.mkdir()
    (tmp_repo / "docs").symlink_to(REPO_ROOT / "docs")
    (tmp_repo / "src").symlink_to(REPO_ROOT / "src")
    return tmp_repo


# ---------------------------------------------------------------------------
# calibrate-prepare-run
# ---------------------------------------------------------------------------


def test_calibrate_prepare_run_writes_two_pri_briefs(tmp_path: Path) -> None:
    tmp_repo = _tmp_repo_root(tmp_path)
    _seed_statute_bundle(tmp_repo, "TX", 2009)

    args = argparse.Namespace(
        repo_root=str(tmp_repo),
        snapshot_date="ignored",
        state="TX",
        vintage=2009,
        run_id="runA",
    )
    rc = cmd_calibrate_prepare_run(args)
    assert rc == 0

    run_dir = statute_run_dir(tmp_repo, "TX", 2009, "runA")
    assert (run_dir / "briefs" / "pri_accessibility.brief.md").exists()
    assert (run_dir / "briefs" / "pri_disclosure_law.brief.md").exists()
    # focal_indicators is NOT a calibration rubric.
    assert not (run_dir / "briefs" / "focal_indicators.brief.md").exists()


def test_calibrate_prepare_run_briefs_mention_statute_source(tmp_path: Path) -> None:
    tmp_repo = _tmp_repo_root(tmp_path)
    _seed_statute_bundle(tmp_repo, "TX", 2009)
    args = argparse.Namespace(
        repo_root=str(tmp_repo),
        snapshot_date="ignored",
        state="TX",
        vintage=2009,
        run_id="runA",
    )
    cmd_calibrate_prepare_run(args)
    brief = (statute_run_dir(tmp_repo, "TX", 2009, "runA") / "briefs"
             / "pri_disclosure_law.brief.md").read_text(encoding="utf-8")
    # The calibrate brief uses build_statute_subagent_brief which prepends a
    # statute-source-clarification line.
    assert "state statute text" in brief
    # And the brief lists the statute's vintage + delta.
    assert "2009" in brief


def test_calibrate_prepare_run_generates_run_id_if_absent(tmp_path: Path) -> None:
    tmp_repo = _tmp_repo_root(tmp_path)
    _seed_statute_bundle(tmp_repo, "WY", 2010)
    args = argparse.Namespace(
        repo_root=str(tmp_repo),
        snapshot_date="ignored",
        state="WY",
        vintage=2010,
        run_id=None,
    )
    rc = cmd_calibrate_prepare_run(args)
    assert rc == 0
    # Exactly one run directory created under data/scores/WY/statute/2010/.
    parent = tmp_repo / "data" / "scores" / "WY" / "statute" / "2010"
    run_dirs = [p for p in parent.iterdir() if p.is_dir()]
    assert len(run_dirs) == 1


def test_calibrate_prepare_run_errors_when_statute_bundle_missing(tmp_path: Path) -> None:
    tmp_repo = _tmp_repo_root(tmp_path)
    # no bundle seeded
    args = argparse.Namespace(
        repo_root=str(tmp_repo),
        snapshot_date="ignored",
        state="CA",
        vintage=2010,
        run_id="runA",
    )
    rc = cmd_calibrate_prepare_run(args)
    assert rc != 0


# ---------------------------------------------------------------------------
# calibrate-finalize-run
# ---------------------------------------------------------------------------


def _valid_json_payload(rubric_items: list[dict]) -> list[dict]:
    """Build a minimal valid subagent JSON output matching the rubric row-for-row."""
    return [
        {
            "item_id": ri["item_id"],
            "score": 0,
            "evidence_quote_or_url": "fixture",
            "source_artifact": "fixture",
            "confidence": "high",
            "unable_to_evaluate": False,
            "notes": "",
        }
        for ri in rubric_items
    ]


def _seed_raw_json_for_calibration_run(
    tmp_repo: Path, state: str, vintage: int, run_id: str
) -> Path:
    """Write raw JSON for both PRI rubrics in the run directory."""
    from scoring.rubric_loader import load_rubric

    run_dir = statute_run_dir(tmp_repo, state, vintage, run_id)
    (run_dir / "briefs").mkdir(parents=True, exist_ok=True)
    (run_dir / "raw").mkdir(parents=True, exist_ok=True)
    for rubric_name in CALIBRATION_RUBRIC_NAMES:
        rubric = load_rubric(rubric_name, tmp_repo)
        raw = _valid_json_payload([ri.model_dump() for ri in rubric.items])
        (run_dir / "raw" / f"{rubric_name}.json").write_text(
            json.dumps(raw), encoding="utf-8"
        )
        (run_dir / "raw" / "files_read.json").write_text(
            json.dumps({"statute_files_read": ["sections/fake-305.txt"], "notes": ""}),
            encoding="utf-8",
        )
    return run_dir


def test_calibrate_finalize_run_writes_csvs_for_both_rubrics(tmp_path: Path) -> None:
    tmp_repo = _tmp_repo_root(tmp_path)
    _seed_statute_bundle(tmp_repo, "TX", 2009)
    _seed_raw_json_for_calibration_run(tmp_repo, "TX", 2009, "runA")

    args = argparse.Namespace(
        repo_root=str(tmp_repo),
        snapshot_date="ignored",
        state="TX",
        vintage=2009,
        run_id="runA",
        skip_missing=False,
    )
    rc = cmd_calibrate_finalize_run(args)
    assert rc == 0
    run_dir = statute_run_dir(tmp_repo, "TX", 2009, "runA")
    assert (run_dir / "pri_accessibility.csv").exists()
    assert (run_dir / "pri_disclosure_law.csv").exists()


def test_calibrate_finalize_run_writes_statute_run_metadata(tmp_path: Path) -> None:
    tmp_repo = _tmp_repo_root(tmp_path)
    _seed_statute_bundle(tmp_repo, "TX", 2009)
    _seed_raw_json_for_calibration_run(tmp_repo, "TX", 2009, "runA")

    args = argparse.Namespace(
        repo_root=str(tmp_repo),
        snapshot_date="ignored",
        state="TX",
        vintage=2009,
        run_id="runA",
        skip_missing=False,
    )
    cmd_calibrate_finalize_run(args)
    meta_path = statute_run_dir(tmp_repo, "TX", 2009, "runA") / "run_metadata.json"
    assert meta_path.exists()
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    assert meta["state"] == "TX"
    assert meta["run_id"] == "runA"
    assert meta["vintage_year"] == 2009
    assert meta["year_delta"] == 0
    assert meta["direction"] == "exact"
    assert meta["pri_state_reviewed"] is True
    assert meta["statute_manifest_sha"]  # non-empty
    # Should NOT have snapshot-specific fields.
    assert "snapshot_date" not in meta
    assert "snapshot_manifest_sha" not in meta
    # rubric_shas should list both PRI rubrics and exclude focal.
    assert set(meta["rubric_shas"].keys()) == set(CALIBRATION_RUBRIC_NAMES)


def test_calibrate_finalize_run_skip_missing(tmp_path: Path) -> None:
    """If one rubric's raw JSON is missing, --skip-missing finalizes the other."""
    tmp_repo = _tmp_repo_root(tmp_path)
    _seed_statute_bundle(tmp_repo, "TX", 2009)
    _seed_raw_json_for_calibration_run(tmp_repo, "TX", 2009, "runA")
    # Delete one rubric's raw JSON.
    run_dir = statute_run_dir(tmp_repo, "TX", 2009, "runA")
    (run_dir / "raw" / "pri_disclosure_law.json").unlink()

    args = argparse.Namespace(
        repo_root=str(tmp_repo),
        snapshot_date="ignored",
        state="TX",
        vintage=2009,
        run_id="runA",
        skip_missing=True,
    )
    rc = cmd_calibrate_finalize_run(args)
    assert rc == 0
    # The one with raw JSON got finalized.
    assert (run_dir / "pri_accessibility.csv").exists()
    assert not (run_dir / "pri_disclosure_law.csv").exists()
    # Metadata NOT written (run not yet complete).
    assert not (run_dir / "run_metadata.json").exists()


def test_calibrate_finalize_run_errors_on_missing_without_skip(tmp_path: Path) -> None:
    tmp_repo = _tmp_repo_root(tmp_path)
    _seed_statute_bundle(tmp_repo, "TX", 2009)
    _seed_raw_json_for_calibration_run(tmp_repo, "TX", 2009, "runA")
    run_dir = statute_run_dir(tmp_repo, "TX", 2009, "runA")
    (run_dir / "raw" / "pri_disclosure_law.json").unlink()

    args = argparse.Namespace(
        repo_root=str(tmp_repo),
        snapshot_date="ignored",
        state="TX",
        vintage=2009,
        run_id="runA",
        skip_missing=False,
    )
    rc = cmd_calibrate_finalize_run(args)
    assert rc != 0


def test_calibrate_finalize_run_stamps_statute_manifest_sha_in_csv(tmp_path: Path) -> None:
    """ScoredRow's snapshot_manifest_sha column should carry the statute manifest sha."""
    import csv as csv_mod

    tmp_repo = _tmp_repo_root(tmp_path)
    bundle_dir = _seed_statute_bundle(tmp_repo, "WY", 2010)
    _seed_raw_json_for_calibration_run(tmp_repo, "WY", 2010, "runA")

    args = argparse.Namespace(
        repo_root=str(tmp_repo),
        snapshot_date="ignored",
        state="WY",
        vintage=2010,
        run_id="runA",
        skip_missing=False,
    )
    cmd_calibrate_finalize_run(args)

    expected_sha = hashlib.sha256((bundle_dir / "manifest.json").read_bytes()).hexdigest()
    run_dir = statute_run_dir(tmp_repo, "WY", 2010, "runA")
    with (run_dir / "pri_accessibility.csv").open(encoding="utf-8") as f:
        reader = csv_mod.DictReader(f)
        first = next(reader)
    assert first["snapshot_manifest_sha"] == expected_sha
    assert first["coverage_tier"] == "clean"  # hard-coded for statute runs
