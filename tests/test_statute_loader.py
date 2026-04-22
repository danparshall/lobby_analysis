"""Tests for statute_loader.load_statute_bundle."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from scoring.models import StatuteBundle
from scoring.statute_loader import load_statute_bundle


def _build_bundle(
    repo_root: Path,
    state: str = "CA",
    vintage: int = 2010,
    section_text: str = "Section 86100. Lobbyist.",
) -> Path:
    """Create a minimal valid statute bundle under repo_root/data/statutes/<STATE>/<VINTAGE>/."""
    bundle_dir = repo_root / "data" / "statutes" / state / str(vintage)
    sections = bundle_dir / "sections"
    sections.mkdir(parents=True)
    section_file = sections / "gov-86100-86118.txt"
    section_file.write_text(section_text, encoding="utf-8")
    raw = section_file.read_bytes()
    manifest = {
        "state_abbr": state,
        "vintage_year": vintage,
        "year_delta": 0,
        "direction": "exact",
        "pri_state_reviewed": True,
        "retrieved_at": "2026-04-18T18:00:00+00:00",
        "artifacts": [
            {
                "url": f"https://law.justia.com/codes/{state.lower()}/{vintage}/gov/86100-86118.html",
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
    return bundle_dir


def test_load_statute_bundle_happy_path(tmp_path: Path) -> None:
    bundle_dir = _build_bundle(tmp_path)
    bundle = load_statute_bundle(bundle_dir, tmp_path)
    assert isinstance(bundle, StatuteBundle)
    assert bundle.state_abbr == "CA"
    assert bundle.vintage_year == 2010
    assert bundle.direction == "exact"
    assert bundle.pri_state_reviewed is True
    assert len(bundle.artifacts) == 1
    assert bundle.artifacts[0].role == "statute"


def test_load_statute_bundle_normalizes_local_path_to_repo_root(tmp_path: Path) -> None:
    """Artifact local_path must be repo-root-relative after load, so that
    downstream consumers (subagent briefs) can prepend repo_root and get a
    resolvable path. Mirrors how SnapshotArtifact.local_path already works."""
    bundle_dir = _build_bundle(tmp_path)
    bundle = load_statute_bundle(bundle_dir, tmp_path)
    [artifact] = bundle.artifacts
    assert artifact.local_path == "data/statutes/CA/2010/sections/gov-86100-86118.txt"
    assert (tmp_path / artifact.local_path).exists()


def test_load_statute_bundle_populates_manifest_sha(tmp_path: Path) -> None:
    bundle_dir = _build_bundle(tmp_path)
    bundle = load_statute_bundle(bundle_dir, tmp_path)
    # manifest_sha should be the sha256 of the manifest.json bytes.
    expected = hashlib.sha256(
        (bundle_dir / "manifest.json").read_bytes()
    ).hexdigest()
    assert bundle.manifest_sha == expected


def test_load_statute_bundle_missing_manifest_raises(tmp_path: Path) -> None:
    empty_bundle = tmp_path / "data" / "statutes" / "CA" / "2010"
    (empty_bundle / "sections").mkdir(parents=True)  # sections dir exists but no manifest
    with pytest.raises(FileNotFoundError):
        load_statute_bundle(empty_bundle, tmp_path)


def test_load_statute_bundle_sha_mismatch_raises(tmp_path: Path) -> None:
    bundle_dir = _build_bundle(tmp_path)
    # Tamper with the section file — its bytes now differ from the manifest sha.
    section_file = bundle_dir / "sections" / "gov-86100-86118.txt"
    section_file.write_text("tampered content", encoding="utf-8")
    with pytest.raises(ValueError, match="sha256 mismatch"):
        load_statute_bundle(bundle_dir, tmp_path)


def test_load_statute_bundle_missing_section_file_raises(tmp_path: Path) -> None:
    bundle_dir = _build_bundle(tmp_path)
    # Delete the referenced section file.
    (bundle_dir / "sections" / "gov-86100-86118.txt").unlink()
    with pytest.raises(FileNotFoundError):
        load_statute_bundle(bundle_dir, tmp_path)
