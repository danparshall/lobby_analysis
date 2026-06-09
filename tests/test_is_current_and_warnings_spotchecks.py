"""Tests for is_current_spotcheck + extraction_warnings_inspect.

Both are enumeration scripts that walk on-disk filings. The testable surface
is the bucketing/loading logic — exercised against a synthetic on-disk
layout so we don't need the real OH dataset.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
_IS_CURRENT_PATH = _REPO_ROOT / "scripts" / "gpt5mini_oh_300slice_is_current_spotcheck.py"
_WARNINGS_PATH = _REPO_ROOT / "scripts" / "gpt5mini_oh_300slice_extraction_warnings_inspect.py"


def _load(path: Path, modname: str):
    spec = importlib.util.spec_from_file_location(modname, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[modname] = module
    spec.loader.exec_module(module)
    return module


def _write_filing(
    data_dir: Path, *, arm: str, rid: str, payload: dict
) -> None:
    """Write a filing.json into the on-disk layout the scripts expect."""
    if arm == "sonnet":
        d = data_dir / "extracted" / rid / "sonnet_run_abcd1234"
    else:
        d = data_dir / "extracted_openai" / rid / f"mini_{arm}_run_1_20260609T120000_aabb1122"
    d.mkdir(parents=True, exist_ok=True)
    (d / "filing.json").write_text(json.dumps(payload))


# ─── is_current_spotcheck ────────────────────────────────────────────────


def test_is_current_no_disagreement_returns_empty(tmp_path: Path) -> None:
    mod = _load(_IS_CURRENT_PATH, "is_current_spotcheck")
    rid = "9000001"
    _write_filing(tmp_path, arm="sonnet", rid=rid, payload={"is_current": True})
    _write_filing(tmp_path, arm="medium_briefv2", rid=rid, payload={"is_current": True})
    disagreements = mod.find_disagreements([rid], tmp_path, "medium_briefv2")
    assert disagreements == []


def test_is_current_disagreement_records_both_values(tmp_path: Path) -> None:
    mod = _load(_IS_CURRENT_PATH, "is_current_spotcheck")
    rid = "9000002"
    _write_filing(
        tmp_path, arm="sonnet", rid=rid,
        payload={"is_current": True, "filing_action": "original", "supersedes": None},
    )
    _write_filing(
        tmp_path, arm="medium_briefv2", rid=rid,
        payload={"is_current": False, "filing_action": "amendment", "supersedes": "f-prev"},
    )
    disagreements = mod.find_disagreements([rid], tmp_path, "medium_briefv2")
    assert len(disagreements) == 1
    d = disagreements[0]
    assert d["report_id"] == rid
    assert d["sonnet"] is True
    assert d["mini"] is False
    # Adjacent-field context is captured for diagnosis
    assert d["sonnet_filing_action"] == "original"
    assert d["mini_filing_action"] == "amendment"
    assert d["sonnet_supersedes"] is None
    assert d["mini_supersedes"] == "f-prev"


def test_is_current_skips_missing_arm_output(tmp_path: Path) -> None:
    """If an arm has no output for a rid, the rid is silently skipped."""
    mod = _load(_IS_CURRENT_PATH, "is_current_spotcheck")
    rid = "9000003"
    _write_filing(tmp_path, arm="sonnet", rid=rid, payload={"is_current": True})
    # No medium_briefv2 output written
    disagreements = mod.find_disagreements([rid], tmp_path, "medium_briefv2")
    assert disagreements == []


# ─── extraction_warnings_inspect ────────────────────────────────────────


def test_extraction_warnings_find_briefv2_rids(tmp_path: Path) -> None:
    mod = _load(_WARNINGS_PATH, "extraction_warnings_inspect")
    # Rid with briefv2 output: should be discovered
    _write_filing(
        tmp_path, arm="medium_briefv2", rid="8000001",
        payload={"extraction_warnings": ["foo"]},
    )
    # Rid with only original medium output: should NOT be discovered
    _write_filing(
        tmp_path, arm="medium", rid="8000002",
        payload={"extraction_warnings": []},
    )
    rids = mod.find_briefv2_rids(tmp_path)
    assert rids == ["8000001"]


def test_extraction_warnings_format_handles_three_states(tmp_path: Path) -> None:
    """_format_warnings handles None (field absent), [] (empty), and populated."""
    mod = _load(_WARNINGS_PATH, "extraction_warnings_inspect")
    assert mod._format_warnings(None) == "(field absent)"
    assert mod._format_warnings([]) == "(empty list)"
    out = mod._format_warnings(["first warning", "second warning"])
    assert "first warning" in out
    assert "second warning" in out
    # Each on its own line with bullet prefix
    assert out.count("\n") == 1
