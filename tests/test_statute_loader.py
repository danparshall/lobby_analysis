"""Tests for statute_loader.load_statute_bundle."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from scoring.models import StatuteBundle
from scoring.statute_loader import load_statute_bundle


def _build_bundle(tmp_path: Path, section_text: str = "Section 86100. Lobbyist.") -> Path:
    """Create a minimal valid statute bundle at tmp_path."""
    sections = tmp_path / "sections"
    sections.mkdir()
    section_file = sections / "gov-86100-86118.txt"
    section_file.write_text(section_text, encoding="utf-8")
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
    (tmp_path / "manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8"
    )
    return tmp_path


def test_load_statute_bundle_happy_path(tmp_path: Path) -> None:
    bundle_dir = _build_bundle(tmp_path)
    bundle = load_statute_bundle(bundle_dir)
    assert isinstance(bundle, StatuteBundle)
    assert bundle.state_abbr == "CA"
    assert bundle.vintage_year == 2010
    assert bundle.direction == "exact"
    assert bundle.pri_state_reviewed is True
    assert len(bundle.artifacts) == 1
    assert bundle.artifacts[0].role == "statute"


def test_load_statute_bundle_populates_manifest_sha(tmp_path: Path) -> None:
    bundle_dir = _build_bundle(tmp_path)
    bundle = load_statute_bundle(bundle_dir)
    # manifest_sha should be the sha256 of the manifest.json bytes.
    expected = hashlib.sha256(
        (bundle_dir / "manifest.json").read_bytes()
    ).hexdigest()
    assert bundle.manifest_sha == expected


def test_load_statute_bundle_missing_manifest_raises(tmp_path: Path) -> None:
    (tmp_path / "sections").mkdir()  # sections dir exists but no manifest
    with pytest.raises(FileNotFoundError):
        load_statute_bundle(tmp_path)


def test_load_statute_bundle_sha_mismatch_raises(tmp_path: Path) -> None:
    bundle_dir = _build_bundle(tmp_path)
    # Tamper with the section file — its bytes now differ from the manifest sha.
    section_file = bundle_dir / "sections" / "gov-86100-86118.txt"
    section_file.write_text("tampered content", encoding="utf-8")
    with pytest.raises(ValueError, match="sha256 mismatch"):
        load_statute_bundle(bundle_dir)


def test_load_statute_bundle_missing_section_file_raises(tmp_path: Path) -> None:
    bundle_dir = _build_bundle(tmp_path)
    # Delete the referenced section file.
    (bundle_dir / "sections" / "gov-86100-86118.txt").unlink()
    with pytest.raises(FileNotFoundError):
        load_statute_bundle(bundle_dir)
