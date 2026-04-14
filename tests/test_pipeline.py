"""End-to-end tests for the scoring pipeline plumbing.

These tests exercise real rubric CSVs and a real CA snapshot manifest so we catch
schema drift against source data — NOT mocked behavior.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from scoring.bundle import build_subagent_brief
from scoring.coverage import coverage_tier_for
from scoring.models import ScoredItem
from scoring.orchestrator import raw_output_path, run_dir
from scoring.output_writer import OutputSchemaError, parse_and_validate
from scoring.provenance import PROMPT_PATH, prompt_sha, stamp_rows
from scoring.rubric_loader import RUBRIC_PATHS, load_all_rubrics, load_rubric
from scoring.snapshot_loader import load_snapshot

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_all_three_rubrics_load_cleanly() -> None:
    rubrics = load_all_rubrics(REPO_ROOT)
    assert set(rubrics) == set(RUBRIC_PATHS)
    expected_counts = {
        "pri_accessibility": 59,
        "pri_disclosure_law": 61,
        "focal_indicators": 54,
    }
    for name, count in expected_counts.items():
        assert len(rubrics[name].items) == count, f"{name}: expected {count}, got {len(rubrics[name].items)}"
        assert rubrics[name].sha, f"{name} missing sha"
        # No empty item_id, item_text, or scoring_guidance — these are load-bearing for the scorer.
        for it in rubrics[name].items:
            assert it.item_id, f"{name} has item with empty item_id"
            assert it.item_text, f"{name}:{it.item_id} has empty item_text"
            assert it.scoring_guidance, f"{name}:{it.item_id} has empty scoring_guidance"


def test_ca_snapshot_loads_and_flags_incapsula_stubs() -> None:
    bundle = load_snapshot("CA", REPO_ROOT)
    assert bundle.state_abbr == "CA"
    assert bundle.manifest_sha
    # CA's manifest documents at least two Incapsula stubs (/Lobbying/ and /Payments/).
    stub_count = sum(1 for a in bundle.artifacts if a.suspicious_challenge_stub)
    assert stub_count >= 2, f"expected ≥2 stubs in CA, got {stub_count}"


def test_coverage_tier_assignments() -> None:
    assert coverage_tier_for("CA") == "partial_waf"
    assert coverage_tier_for("CO") == "clean"
    assert coverage_tier_for("WY") == "clean"
    assert coverage_tier_for("AZ") == "inaccessible"
    assert coverage_tier_for("VT") == "inaccessible"
    assert coverage_tier_for("GA") == "spa_pending_playwright"


def test_brief_contains_all_rubric_items_and_instructs_subagent() -> None:
    rubric = load_rubric("focal_indicators", REPO_ROOT)
    snapshot = load_snapshot("CA", REPO_ROOT)
    out_path = REPO_ROOT / "data/scores/CA/2026-04-13/TEST/raw/focal_indicators.json"
    brief = build_subagent_brief(
        state="CA",
        rubric=rubric,
        snapshot=snapshot,
        repo_root=REPO_ROOT,
        scorer_prompt_path=REPO_ROOT / PROMPT_PATH,
        output_json_path=out_path,
    )
    # Brief must instruct subagent to read the locked prompt and write to the expected path.
    assert str(PROMPT_PATH) in brief or "scorer_prompt.md" in brief
    assert str(out_path) in brief
    # Every rubric item_id must appear in the brief (guard against truncation).
    for it in rubric.items:
        assert it.item_id in brief, f"brief missing {it.item_id}"


def test_parse_and_validate_rejects_missing_items(tmp_path: Path) -> None:
    rubric = load_rubric("pri_accessibility", REPO_ROOT)
    bad = tmp_path / "bad.json"
    bad.write_text(json.dumps([]), encoding="utf-8")
    with pytest.raises(OutputSchemaError):
        parse_and_validate(bad, rubric)


def test_parse_and_validate_rejects_score_when_unable(tmp_path: Path) -> None:
    rubric = load_rubric("pri_accessibility", REPO_ROOT)
    # Build a full-length array but with one malformed row.
    rows = []
    for ri in rubric.items:
        rows.append({
            "item_id": ri.item_id,
            "score": 1,
            "evidence_quote_or_url": "x",
            "source_artifact": "landing_01.html",
            "confidence": "high",
            "unable_to_evaluate": False,
            "notes": "",
        })
    rows[0]["unable_to_evaluate"] = True  # score=1 + unable=true → invalid
    bad = tmp_path / "bad.json"
    bad.write_text(json.dumps(rows), encoding="utf-8")
    with pytest.raises(OutputSchemaError):
        parse_and_validate(bad, rubric)


def test_parse_and_validate_rejects_item_id_reorder(tmp_path: Path) -> None:
    rubric = load_rubric("pri_accessibility", REPO_ROOT)
    rows = [
        {
            "item_id": ri.item_id,
            "score": 1,
            "evidence_quote_or_url": "x",
            "source_artifact": "landing_01.html",
            "confidence": "high",
            "unable_to_evaluate": False,
            "notes": "",
        }
        for ri in rubric.items
    ]
    rows[0], rows[1] = rows[1], rows[0]
    bad = tmp_path / "bad.json"
    bad.write_text(json.dumps(rows), encoding="utf-8")
    with pytest.raises(OutputSchemaError):
        parse_and_validate(bad, rubric)


def test_stamp_rows_adds_provenance() -> None:
    rubric = load_rubric("pri_accessibility", REPO_ROOT)
    snapshot = load_snapshot("CA", REPO_ROOT)
    items = [
        ScoredItem(
            item_id=ri.item_id,
            score=1,
            evidence_quote_or_url="q",
            source_artifact="landing_01.html",
            confidence="high",
            unable_to_evaluate=False,
            notes="",
        )
        for ri in rubric.items
    ]
    rows = stamp_rows(
        items,
        state="CA",
        rubric=rubric,
        coverage_tier="partial_waf",
        prompt_sha_hex=prompt_sha(REPO_ROOT),
        snapshot_manifest_sha=snapshot.manifest_sha,
        run_id="abcdef123456",
        run_timestamp="2026-04-14T00:00:00+00:00",
    )
    assert len(rows) == len(rubric.items)
    for r in rows:
        assert r.model_version
        assert r.prompt_sha
        assert r.rubric_sha == rubric.sha
        assert r.snapshot_manifest_sha == snapshot.manifest_sha
        assert r.coverage_tier == "partial_waf"
        assert r.state == "CA"


def test_run_dir_layout_is_state_date_runid() -> None:
    rd = run_dir(REPO_ROOT, "CA", "2026-04-13", "deadbeef1234")
    assert rd == REPO_ROOT / "data/scores/CA/2026-04-13/deadbeef1234"
    assert raw_output_path(rd, "pri_accessibility").name == "pri_accessibility.json"
