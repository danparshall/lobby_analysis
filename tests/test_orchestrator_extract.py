"""TDD tests for `orchestrator extract-prepare-run` and `extract-finalize-run`.

These are the v2 statute-extraction counterparts of the calibrate-* commands.
They read the locked compendium + a state's statute bundle, build a v2
extraction brief (no rubric_shas, no rubric files), and write a per-run dir
under `data/extractions/<STATE>/<VINTAGE>/<CHUNK>/<RUN_ID>/`.

Phase 3 of plans/20260501_statute_extraction_harness.md. Tests target
behavior — files written, content validates, drift caught — using a
tmp_repo seeded with a real compendium symlink + a synthetic OH 2025
bundle.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]


def _tmp_repo_root(tmp_path: Path) -> Path:
    """Create a tmp repo with src/, docs/, and compendium/ symlinked from real repo."""
    tmp_repo = tmp_path / "repo"
    tmp_repo.mkdir()
    (tmp_repo / "src").symlink_to(REPO_ROOT / "src")
    (tmp_repo / "docs").symlink_to(REPO_ROOT / "docs")
    (tmp_repo / "compendium").symlink_to(REPO_ROOT / "compendium")
    return tmp_repo


def _seed_definitions_bundle(tmp_repo: Path, state: str = "OH", vintage: int = 2025) -> Path:
    """Write a tiny statute bundle with valid manifest + sha256 under tmp_repo."""
    bundle_dir = tmp_repo / "data" / "statutes" / state / str(vintage)
    sections = bundle_dir / "sections"
    sections.mkdir(parents=True)
    section_file = sections / "title1-chapter101-101_70.txt"
    section_text = (
        "Section 101.70 Definitions.\n"
        "(F) 'Lobbyist' means any person engaged, for compensation, to influence "
        "legislative action by direct communication with members of the general "
        "assembly, when the activity is one of the individual's main purposes."
    )
    section_file.write_text(section_text, encoding="utf-8")
    raw = section_file.read_bytes()
    manifest = {
        "state_abbr": state,
        "vintage_year": vintage,
        "year_delta": 15,
        "direction": "post",
        "pri_state_reviewed": True,
        "retrieved_at": "2026-04-30T18:17:37+00:00",
        "artifacts": [
            {
                "url": (
                    f"https://law.justia.com/codes/{state.lower()}/{vintage}/"
                    "title1/chapter101/101_70.html"
                ),
                "role": "core_chapter",
                "sha256": hashlib.sha256(raw).hexdigest(),
                "bytes": len(raw),
                "local_path": "sections/title1-chapter101-101_70.txt",
                "retrieved_because": "curated core lobbying chapter",
                "hop": 0,
                "referenced_from": "",
            }
        ],
    }
    (bundle_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8"
    )
    return bundle_dir


def _prepare_run(tmp_repo: Path, run_id: str = "iter1run01") -> Path:
    from scoring.orchestrator import cmd_extract_prepare_run, extract_run_dir

    args = argparse.Namespace(
        repo_root=str(tmp_repo),
        snapshot_date="ignored",
        state="OH",
        vintage=2025,
        chunk="definitions",
        iteration_label="iter-1",
        prior_run_id=None,
        changes_from_prior="first iteration baseline",
        run_id=run_id,
    )
    rc = cmd_extract_prepare_run(args)
    assert rc == 0
    return extract_run_dir(tmp_repo, "OH", 2025, "definitions", run_id)


# ---------------------------------------------------------------------------
# extract-prepare-run
# ---------------------------------------------------------------------------


def test_extract_prepare_run_writes_brief_and_meta(tmp_path: Path) -> None:
    tmp_repo = _tmp_repo_root(tmp_path)
    _seed_definitions_bundle(tmp_repo)

    run_dir = _prepare_run(tmp_repo)

    suffix_path = run_dir / "brief_suffix.md"
    meta_path = run_dir / "meta.json"

    assert suffix_path.exists(), f"brief_suffix.md missing at {suffix_path}"
    assert meta_path.exists(), f"meta.json missing at {meta_path}"

    suffix = suffix_path.read_text()
    assert "definitions" in suffix
    assert "scorer_prompt_v2.md" in suffix
    assert "THRESHOLD_LOBBYING_MATERIALITY_GATE" in suffix

    meta = json.loads(meta_path.read_text())
    assert meta["state"] == "OH"
    assert meta["vintage_year"] == 2025
    assert meta["chunk"] == "definitions"
    assert meta["iteration_label"] == "iter-1"
    assert meta["prior_run_id"] is None
    assert meta["changes_from_prior"] == "first iteration baseline"
    assert len(meta["bundle_manifest_sha"]) == 64
    assert len(meta["compendium_csv_sha"]) == 64
    assert len(meta["prompt_sha"]) == 64
    # run_timestamp_utc must NOT be stamped at prepare-time; finalize stamps it.
    assert meta.get("run_timestamp_utc") in (None, "", "PENDING")


# ---------------------------------------------------------------------------
# extract-finalize-run
# ---------------------------------------------------------------------------


def _write_raw_output(run_dir: Path, records: list[dict]) -> None:
    (run_dir / "raw_output.json").write_text(json.dumps(records, indent=2))


def _valid_record(**overrides) -> dict:
    base = {
        "compendium_row_id": "THRESHOLD_LOBBYING_MATERIALITY_GATE",
        "field_path": "lobbyist_threshold",
        "reporting_party": "lobbyist",
        "status": "required_conditional",
        "condition_text": "as one of the individual's main purposes",
        "regime": None,
        "registrant_role": None,
        "legal_citation": "ORC §101.70(F)",
        "evidence_notes": "verbatim quote from statute",
        "notes": "",
    }
    return {**base, **overrides}


def test_extract_finalize_run_validates_raw_output(tmp_path: Path) -> None:
    from scoring.orchestrator import cmd_extract_finalize_run

    tmp_repo = _tmp_repo_root(tmp_path)
    _seed_definitions_bundle(tmp_repo)
    run_dir = _prepare_run(tmp_repo)

    # Happy path: a single valid record.
    _write_raw_output(run_dir, [_valid_record()])

    args = argparse.Namespace(
        repo_root=str(tmp_repo),
        snapshot_date="ignored",
        state="OH",
        vintage=2025,
        chunk="definitions",
        run_id="iter1run01",
    )
    rc = cmd_extract_finalize_run(args)
    assert rc == 0, "happy-path finalize must succeed"

    fr_path = run_dir / "field_requirements.json"
    assert fr_path.exists()
    fr_records = json.loads(fr_path.read_text())
    assert len(fr_records) == 1
    assert fr_records[0]["compendium_row_id"] == "THRESHOLD_LOBBYING_MATERIALITY_GATE"
    assert fr_records[0]["status"] == "required_conditional"

    meta_after = json.loads((run_dir / "meta.json").read_text())
    assert meta_after.get("run_timestamp_utc"), (
        "finalize must stamp run_timestamp_utc into meta.json"
    )

    # Sad path: missing legal_citation must be rejected.
    run_dir_2 = _prepare_run(tmp_repo, run_id="iter1run02")
    bad_record = _valid_record(legal_citation=None)
    _write_raw_output(run_dir_2, [bad_record])
    args.run_id = "iter1run02"
    rc_bad = cmd_extract_finalize_run(args)
    assert rc_bad != 0, "finalize must fail when legal_citation is null"


def test_extract_finalize_run_rejects_unknown_compendium_id(tmp_path: Path) -> None:
    from scoring.orchestrator import cmd_extract_finalize_run

    tmp_repo = _tmp_repo_root(tmp_path)
    _seed_definitions_bundle(tmp_repo)
    run_dir = _prepare_run(tmp_repo)

    # Record references an id that exists in the compendium but NOT in the
    # definitions chunk (e.g., a registration row). Drift-catching guard.
    drifted = _valid_record(
        compendium_row_id="REG_LOBBYIST",
        status="required",
        condition_text=None,
    )
    _write_raw_output(run_dir, [drifted])

    args = argparse.Namespace(
        repo_root=str(tmp_repo),
        snapshot_date="ignored",
        state="OH",
        vintage=2025,
        chunk="definitions",
        run_id="iter1run01",
    )
    rc = cmd_extract_finalize_run(args)
    assert rc != 0, "finalize must reject compendium_row_ids outside the chunk"
    # field_requirements.json must NOT have been written.
    assert not (run_dir / "field_requirements.json").exists()
