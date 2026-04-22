"""Tests for build_statute_subagent_brief."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from scoring.bundle import build_statute_subagent_brief
from scoring.models import StatuteArtifact, StatuteBundle
from scoring.provenance import PROMPT_PATH
from scoring.rubric_loader import load_rubric
from scoring.statute_loader import load_statute_bundle

REPO_ROOT = Path(__file__).resolve().parents[1]


def _mini_statute_bundle() -> StatuteBundle:
    return StatuteBundle(
        state_abbr="CA",
        vintage_year=2010,
        year_delta=0,
        direction="exact",
        pri_state_reviewed=True,
        retrieved_at="2026-04-18T18:00:00+00:00",
        artifacts=[
            StatuteArtifact(
                url="https://law.justia.com/codes/california/2010/gov/86100-86118.html",
                sha256="abc123",
                bytes=5000,
                local_path="sections/gov-86100-86118.txt",
            ),
            StatuteArtifact(
                url="https://law.justia.com/codes/california/2010/gov/86201-86206.html",
                sha256="def456",
                bytes=3000,
                local_path="sections/gov-86201-86206.txt",
            ),
        ],
        manifest_sha="m1m2m3",
    )


def test_statute_brief_labels_source_as_statute_text() -> None:
    rubric = load_rubric("pri_disclosure_law", REPO_ROOT)
    statute = _mini_statute_bundle()
    out_path = REPO_ROOT / "data/scores/CA/2010/TEST/raw/pri_disclosure_law.json"
    brief = build_statute_subagent_brief(
        state="CA",
        rubric=rubric,
        statute=statute,
        repo_root=REPO_ROOT,
        scorer_prompt_path=REPO_ROOT / PROMPT_PATH,
        output_json_path=out_path,
    )
    # Must explicitly tell the scorer the source is statute text, not portal content.
    assert "statute text" in brief
    assert "not portal content" in brief


def test_statute_brief_includes_vintage_and_retrieved_at() -> None:
    rubric = load_rubric("pri_disclosure_law", REPO_ROOT)
    statute = _mini_statute_bundle()
    brief = build_statute_subagent_brief(
        state="CA",
        rubric=rubric,
        statute=statute,
        repo_root=REPO_ROOT,
        scorer_prompt_path=REPO_ROOT / PROMPT_PATH,
        output_json_path=REPO_ROOT / "data/scores/x.json",
    )
    assert "2010" in brief
    assert "exact" in brief
    assert statute.retrieved_at in brief


def test_statute_brief_lists_all_artifacts() -> None:
    rubric = load_rubric("pri_disclosure_law", REPO_ROOT)
    statute = _mini_statute_bundle()
    brief = build_statute_subagent_brief(
        state="CA",
        rubric=rubric,
        statute=statute,
        repo_root=REPO_ROOT,
        scorer_prompt_path=REPO_ROOT / PROMPT_PATH,
        output_json_path=REPO_ROOT / "data/scores/x.json",
    )
    for a in statute.artifacts:
        assert a.local_path in brief
        assert a.url in brief


def test_statute_brief_contains_all_rubric_items() -> None:
    rubric = load_rubric("pri_disclosure_law", REPO_ROOT)
    statute = _mini_statute_bundle()
    brief = build_statute_subagent_brief(
        state="CA",
        rubric=rubric,
        statute=statute,
        repo_root=REPO_ROOT,
        scorer_prompt_path=REPO_ROOT / PROMPT_PATH,
        output_json_path=REPO_ROOT / "data/scores/x.json",
    )
    for item in rubric.items:
        assert item.item_id in brief, f"brief missing {item.item_id}"


def test_statute_brief_references_locked_prompt_and_output_path() -> None:
    rubric = load_rubric("pri_disclosure_law", REPO_ROOT)
    statute = _mini_statute_bundle()
    out_path = REPO_ROOT / "data/scores/CA/2010/RUN1/raw/pri_disclosure_law.json"
    brief = build_statute_subagent_brief(
        state="CA",
        rubric=rubric,
        statute=statute,
        repo_root=REPO_ROOT,
        scorer_prompt_path=REPO_ROOT / PROMPT_PATH,
        output_json_path=out_path,
    )
    assert str(PROMPT_PATH) in brief or "scorer_prompt.md" in brief
    assert str(out_path) in brief


def test_statute_brief_paths_resolve_against_repo_root(tmp_path: Path) -> None:
    """Dispatch contract: prepending repo_root to each artifact's local_path
    must yield an existing readable file. This is the contract the brief
    instructs the subagent to follow — if it's not true, every Read in the
    subagent will fail."""
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    (repo_root / "docs").symlink_to(REPO_ROOT / "docs", target_is_directory=True)

    bundle_dir = repo_root / "data" / "statutes" / "CA" / "2010"
    sections = bundle_dir / "sections"
    sections.mkdir(parents=True)
    section_file = sections / "gov-86100-86118.txt"
    section_file.write_text("§86100. Definitions. As used in this chapter…", encoding="utf-8")
    raw = section_file.read_bytes()
    manifest = {
        "state_abbr": "CA",
        "vintage_year": 2010,
        "year_delta": 0,
        "direction": "exact",
        "pri_state_reviewed": True,
        "retrieved_at": "2026-04-18T18:00:00+00:00",
        "artifacts": [
            {
                "url": "https://law.justia.com/codes/california/2010/gov/86100-86118.html",
                "role": "statute",
                "sha256": hashlib.sha256(raw).hexdigest(),
                "bytes": len(raw),
                "local_path": "sections/gov-86100-86118.txt",
            }
        ],
    }
    (bundle_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8"
    )

    statute = load_statute_bundle(bundle_dir, repo_root=repo_root)
    rubric = load_rubric("pri_disclosure_law", repo_root)
    build_statute_subagent_brief(
        state="CA",
        rubric=rubric,
        statute=statute,
        repo_root=repo_root,
        scorer_prompt_path=repo_root / PROMPT_PATH,
        output_json_path=repo_root / "data/scores/CA/statute/2010/r1/raw/pri_disclosure_law.json",
    )
    for artifact in statute.artifacts:
        resolved = repo_root / artifact.local_path
        assert resolved.exists(), (
            f"brief contract broken: repo_root / {artifact.local_path!r} "
            f"should resolve to an existing file, but {resolved} does not exist"
        )
        assert resolved.read_bytes(), f"{resolved} is empty"
