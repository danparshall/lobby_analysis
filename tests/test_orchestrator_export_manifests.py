"""Tests for `orchestrator export-statute-manifests`."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


from scoring.orchestrator import cmd_export_statute_manifests


def _seed_bundle(root: Path, state: str, year: int) -> Path:
    """Create a minimal data/statutes/<STATE>/<YEAR>/ with manifest + dummy section."""
    bundle_dir = root / state / str(year)
    sections = bundle_dir / "sections"
    sections.mkdir(parents=True)
    section_file = sections / "fake.txt"
    section_file.write_text(f"{state} {year} statute", encoding="utf-8")
    manifest = {
        "state_abbr": state,
        "vintage_year": year,
        "year_delta": 0,
        "direction": "exact",
        "pri_state_reviewed": True,
        "retrieved_at": "2026-04-18T21:00:00+00:00",
        "artifacts": [
            {
                "url": f"https://law.justia.com/codes/{state.lower()}/{year}/fake.html",
                "role": "statute",
                "sha256": hashlib.sha256(section_file.read_bytes()).hexdigest(),
                "bytes": section_file.stat().st_size,
                "local_path": "sections/fake.txt",
            }
        ],
    }
    (bundle_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8"
    )
    return bundle_dir


def test_export_copies_manifest_preserving_state_year_layout(tmp_path: Path) -> None:
    source = tmp_path / "data" / "statutes"
    _seed_bundle(source, "CA", 2010)
    _seed_bundle(source, "TX", 2009)
    dest = tmp_path / "results" / "statute_manifests"

    args = argparse.Namespace(
        repo_root=str(tmp_path), source=str(source), dest=str(dest)
    )
    rc = cmd_export_statute_manifests(args)
    assert rc == 0
    assert (dest / "CA" / "2010" / "manifest.json").exists()
    assert (dest / "TX" / "2009" / "manifest.json").exists()


def test_export_does_not_copy_section_text(tmp_path: Path) -> None:
    source = tmp_path / "data" / "statutes"
    _seed_bundle(source, "CA", 2010)
    dest = tmp_path / "results" / "statute_manifests"

    args = argparse.Namespace(
        repo_root=str(tmp_path), source=str(source), dest=str(dest)
    )
    cmd_export_statute_manifests(args)
    # Only manifest.json should have been copied — no sections/ dir.
    assert (dest / "CA" / "2010" / "manifest.json").exists()
    assert not (dest / "CA" / "2010" / "sections").exists()


def test_export_preserves_manifest_bytes(tmp_path: Path) -> None:
    source = tmp_path / "data" / "statutes"
    _seed_bundle(source, "WY", 2010)
    dest = tmp_path / "results" / "statute_manifests"

    args = argparse.Namespace(
        repo_root=str(tmp_path), source=str(source), dest=str(dest)
    )
    cmd_export_statute_manifests(args)
    src_bytes = (source / "WY" / "2010" / "manifest.json").read_bytes()
    dst_bytes = (dest / "WY" / "2010" / "manifest.json").read_bytes()
    assert src_bytes == dst_bytes


def test_export_returns_nonzero_on_missing_source(tmp_path: Path) -> None:
    args = argparse.Namespace(
        repo_root=str(tmp_path),
        source=str(tmp_path / "does_not_exist"),
        dest=str(tmp_path / "dest"),
    )
    rc = cmd_export_statute_manifests(args)
    assert rc == 2
