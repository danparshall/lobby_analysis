"""Tests for enriched statute manifest format.

Covers:
- StatuteArtifact model accepts expanded role, retrieval reasoning fields
- statute_loader handles old-format and new-format manifests
- retrieve_statute_bundle writes enriched fields for core chapters
- Scorer brief includes role information in artifact index
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from scoring.models import StatuteArtifact
from scoring.statute_loader import load_statute_bundle
from scoring.statute_retrieval import retrieve_statute_bundle


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _section_bytes(text: str = "Section 101.70. Definitions.") -> tuple[bytes, str]:
    """Return (raw_bytes, sha256_hex) for a section file."""
    raw = text.encode("utf-8")
    return raw, hashlib.sha256(raw).hexdigest()


def _write_manifest(bundle_dir: Path, artifacts: list[dict], **kwargs) -> Path:
    """Write a manifest.json with given artifacts and optional top-level overrides."""
    defaults = {
        "state_abbr": "OH",
        "vintage_year": 2010,
        "year_delta": 0,
        "direction": "exact",
        "pri_state_reviewed": True,
        "retrieved_at": "2026-04-29T12:00:00+00:00",
    }
    defaults.update(kwargs)
    defaults["artifacts"] = artifacts
    manifest_path = bundle_dir / "manifest.json"
    manifest_path.write_text(json.dumps(defaults, indent=2), encoding="utf-8")
    return manifest_path


def _statute_html(body_text: str) -> str:
    return f"""<html>
<head><title>Test</title></head>
<body>
<div id="main-content">
<p>Find a Lawyer</p>
<p>{body_text}</p>
</div>
</body>
</html>"""


class FakeClient:
    def __init__(self, responses: dict[str, str]) -> None:
        self.responses = responses
        self.fetched: list[str] = []

    def fetch_page(self, url: str) -> str:
        self.fetched.append(url)
        if url not in self.responses:
            raise KeyError(f"FakeClient has no response for {url}")
        return self.responses[url]


# ---------------------------------------------------------------------------
# StatuteArtifact model: enriched fields
# ---------------------------------------------------------------------------

class TestStatuteArtifactEnrichedFields:
    """StatuteArtifact should accept core_chapter/support_chapter roles
    and the new retrieval-reasoning fields."""

    def test_accepts_core_chapter_role(self) -> None:
        a = StatuteArtifact(
            url="https://law.justia.com/codes/ohio/2010/title1/chapter101/101_70.html",
            role="core_chapter",
            sha256="abc123",
            bytes=5000,
            local_path="sections/101_70.txt",
        )
        assert a.role == "core_chapter"

    def test_accepts_support_chapter_role(self) -> None:
        a = StatuteArtifact(
            url="https://law.justia.com/codes/ohio/2010/title1/chapter311/311_005.html",
            role="support_chapter",
            sha256="abc123",
            bytes=3000,
            local_path="sections/311_005.txt",
            retrieved_because="§101.70 references §311.005 for 'person' definition",
            hop=1,
            referenced_from="sections/101_70.txt",
        )
        assert a.role == "support_chapter"
        assert a.hop == 1
        assert "person" in a.retrieved_because
        assert a.referenced_from == "sections/101_70.txt"

    def test_defaults_for_new_fields(self) -> None:
        """New fields should have sensible defaults so old code paths still work."""
        a = StatuteArtifact(
            url="https://example.com/statute.html",
            role="core_chapter",
            sha256="abc",
            bytes=100,
            local_path="sections/foo.txt",
        )
        assert a.hop == 0
        assert a.retrieved_because == ""
        assert a.referenced_from == ""

    def test_rejects_invalid_role(self) -> None:
        """Only core_chapter and support_chapter should be accepted."""
        with pytest.raises(Exception):
            StatuteArtifact(
                url="https://example.com/statute.html",
                role="unknown_role",
                sha256="abc",
                bytes=100,
                local_path="sections/foo.txt",
            )


# ---------------------------------------------------------------------------
# statute_loader: old-format manifest backward compat
# ---------------------------------------------------------------------------

class TestLoaderOldFormatManifest:
    """load_statute_bundle should handle manifests with role: 'statute'
    by mapping to 'core_chapter'."""

    def test_old_role_statute_maps_to_core_chapter(self, tmp_path: Path) -> None:
        bundle_dir = tmp_path / "data" / "statutes" / "OH" / "2010"
        sections = bundle_dir / "sections"
        sections.mkdir(parents=True)
        raw, sha = _section_bytes()
        (sections / "101_70.txt").write_bytes(raw)

        _write_manifest(bundle_dir, [{
            "url": "https://law.justia.com/codes/ohio/2010/title1/chapter101/101_70.html",
            "role": "statute",
            "sha256": sha,
            "bytes": len(raw),
            "local_path": "sections/101_70.txt",
        }])

        bundle = load_statute_bundle(bundle_dir, tmp_path)
        assert bundle.artifacts[0].role == "core_chapter"


class TestLoaderNewFormatManifest:
    """load_statute_bundle should pass through all enriched fields."""

    def test_loads_enriched_fields(self, tmp_path: Path) -> None:
        bundle_dir = tmp_path / "data" / "statutes" / "OH" / "2010"
        sections = bundle_dir / "sections"
        sections.mkdir(parents=True)
        raw, sha = _section_bytes()
        (sections / "311_005.txt").write_bytes(raw)

        _write_manifest(bundle_dir, [{
            "url": "https://law.justia.com/codes/ohio/2010/title1/chapter311/311_005.html",
            "role": "support_chapter",
            "sha256": sha,
            "bytes": len(raw),
            "local_path": "sections/311_005.txt",
            "retrieved_because": "§101.70 references §311.005 for definition of person",
            "hop": 1,
            "referenced_from": "sections/101_70.txt",
        }])

        bundle = load_statute_bundle(bundle_dir, tmp_path)
        a = bundle.artifacts[0]
        assert a.role == "support_chapter"
        assert a.hop == 1
        assert "person" in a.retrieved_because
        assert a.referenced_from == "sections/101_70.txt"

    def test_mixed_core_and_support_artifacts(self, tmp_path: Path) -> None:
        bundle_dir = tmp_path / "data" / "statutes" / "OH" / "2010"
        sections = bundle_dir / "sections"
        sections.mkdir(parents=True)

        raw_core, sha_core = _section_bytes("Section 101.70. Definitions.")
        (sections / "101_70.txt").write_bytes(raw_core)

        raw_support, sha_support = _section_bytes("Section 311.005. Person defined.")
        (sections / "311_005.txt").write_bytes(raw_support)

        _write_manifest(bundle_dir, [
            {
                "url": "https://law.justia.com/codes/ohio/2010/title1/chapter101/101_70.html",
                "role": "core_chapter",
                "sha256": sha_core,
                "bytes": len(raw_core),
                "local_path": "sections/101_70.txt",
                "hop": 0,
                "retrieved_because": "curated core lobbying chapter",
                "referenced_from": "",
            },
            {
                "url": "https://law.justia.com/codes/ohio/2010/title1/chapter311/311_005.html",
                "role": "support_chapter",
                "sha256": sha_support,
                "bytes": len(raw_support),
                "local_path": "sections/311_005.txt",
                "hop": 1,
                "retrieved_because": "§101.70 references §311.005",
                "referenced_from": "sections/101_70.txt",
            },
        ])

        bundle = load_statute_bundle(bundle_dir, tmp_path)
        assert len(bundle.artifacts) == 2
        roles = [a.role for a in bundle.artifacts]
        assert roles == ["core_chapter", "support_chapter"]


# ---------------------------------------------------------------------------
# retrieve_statute_bundle: writes enriched manifest for core chapters
# ---------------------------------------------------------------------------

OH_URL = "https://law.justia.com/codes/ohio/2010/title1/chapter101/101_70.html"


class TestRetrieveWritesEnrichedManifest:
    """retrieve_statute_bundle should write role: core_chapter and hop: 0."""

    def test_manifest_has_core_chapter_role(self, tmp_path: Path) -> None:
        client = FakeClient({OH_URL: _statute_html("Section 101.70. Definitions.")})
        retrieve_statute_bundle(
            client,
            state_abbr="OH",
            vintage_year=2010,
            urls=[OH_URL],
            dest_dir=tmp_path,
        )
        manifest = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
        assert manifest["artifacts"][0]["role"] == "core_chapter"

    def test_manifest_has_hop_zero(self, tmp_path: Path) -> None:
        client = FakeClient({OH_URL: _statute_html("Section 101.70. Definitions.")})
        retrieve_statute_bundle(
            client,
            state_abbr="OH",
            vintage_year=2010,
            urls=[OH_URL],
            dest_dir=tmp_path,
        )
        manifest = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
        assert manifest["artifacts"][0]["hop"] == 0

    def test_manifest_has_retrieval_reasoning(self, tmp_path: Path) -> None:
        client = FakeClient({OH_URL: _statute_html("Section 101.70. Definitions.")})
        retrieve_statute_bundle(
            client,
            state_abbr="OH",
            vintage_year=2010,
            urls=[OH_URL],
            dest_dir=tmp_path,
        )
        manifest = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
        art = manifest["artifacts"][0]
        assert "retrieved_because" in art
        assert "referenced_from" in art
