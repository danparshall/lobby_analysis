"""Tests for the retrieval agent brief builder and ingest-crossrefs pipeline."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from scoring.models import StatuteArtifact, StatuteBundle


REPO_ROOT = Path(__file__).resolve().parents[1]


def _mini_oh_statute_bundle() -> StatuteBundle:
    return StatuteBundle(
        state_abbr="OH",
        vintage_year=2010,
        year_delta=0,
        direction="exact",
        pri_state_reviewed=True,
        retrieved_at="2026-04-29T12:00:00+00:00",
        artifacts=[
            StatuteArtifact(
                url="https://law.justia.com/codes/ohio/2010/title1/chapter101/101_70.html",
                role="core_chapter",
                sha256="abc123",
                bytes=5000,
                local_path="data/statutes/OH/2010/sections/title1-chapter101-101_70.txt",
                hop=0,
                retrieved_because="curated core lobbying chapter",
            ),
            StatuteArtifact(
                url="https://law.justia.com/codes/ohio/2010/title1/chapter101/101_72.html",
                role="core_chapter",
                sha256="def456",
                bytes=3000,
                local_path="data/statutes/OH/2010/sections/title1-chapter101-101_72.txt",
                hop=0,
                retrieved_because="curated core lobbying chapter",
            ),
        ],
        manifest_sha="m1m2m3",
    )


# ---------------------------------------------------------------------------
# build_retrieval_subagent_brief
# ---------------------------------------------------------------------------

class TestBuildRetrievalSubagentBrief:
    """The retrieval brief must give the agent everything it needs to
    identify and locate cross-references."""

    def test_brief_includes_rubric_items(self) -> None:
        from scoring.bundle import build_retrieval_subagent_brief
        from scoring.rubric_loader import load_rubric

        rubric = load_rubric("pri_disclosure_law", REPO_ROOT)
        statute = _mini_oh_statute_bundle()
        brief = build_retrieval_subagent_brief(
            state="OH",
            rubric=rubric,
            statute=statute,
            repo_root=REPO_ROOT,
            retrieval_prompt_path=REPO_ROOT / "src/scoring/retrieval_agent_prompt.md",
            output_json_path=REPO_ROOT / "data/statutes/OH/2010/crossrefs_hop1.json",
        )
        # Rubric items should be in the brief so the agent knows what's relevant
        for item in rubric.items:
            assert item.item_id in brief, f"brief missing rubric item {item.item_id}"

    def test_brief_includes_artifact_index(self) -> None:
        from scoring.bundle import build_retrieval_subagent_brief
        from scoring.rubric_loader import load_rubric

        rubric = load_rubric("pri_disclosure_law", REPO_ROOT)
        statute = _mini_oh_statute_bundle()
        brief = build_retrieval_subagent_brief(
            state="OH",
            rubric=rubric,
            statute=statute,
            repo_root=REPO_ROOT,
            retrieval_prompt_path=REPO_ROOT / "src/scoring/retrieval_agent_prompt.md",
            output_json_path=REPO_ROOT / "data/statutes/OH/2010/crossrefs_hop1.json",
        )
        for a in statute.artifacts:
            assert a.local_path in brief
            assert a.url in brief

    def test_brief_includes_url_pattern_examples(self) -> None:
        from scoring.bundle import build_retrieval_subagent_brief
        from scoring.rubric_loader import load_rubric

        rubric = load_rubric("pri_disclosure_law", REPO_ROOT)
        statute = _mini_oh_statute_bundle()
        brief = build_retrieval_subagent_brief(
            state="OH",
            rubric=rubric,
            statute=statute,
            repo_root=REPO_ROOT,
            retrieval_prompt_path=REPO_ROOT / "src/scoring/retrieval_agent_prompt.md",
            output_json_path=REPO_ROOT / "data/statutes/OH/2010/crossrefs_hop1.json",
        )
        # The brief should show the URL pattern so the agent can construct
        # new URLs for cross-referenced sections
        assert "law.justia.com/codes/ohio/2010" in brief

    def test_brief_specifies_two_hop_limit(self) -> None:
        from scoring.bundle import build_retrieval_subagent_brief
        from scoring.rubric_loader import load_rubric

        rubric = load_rubric("pri_disclosure_law", REPO_ROOT)
        statute = _mini_oh_statute_bundle()
        brief = build_retrieval_subagent_brief(
            state="OH",
            rubric=rubric,
            statute=statute,
            repo_root=REPO_ROOT,
            retrieval_prompt_path=REPO_ROOT / "src/scoring/retrieval_agent_prompt.md",
            output_json_path=REPO_ROOT / "data/statutes/OH/2010/crossrefs_hop1.json",
        )
        assert "hop" in brief.lower()

    def test_brief_references_locked_prompt_and_output_path(self) -> None:
        from scoring.bundle import build_retrieval_subagent_brief
        from scoring.rubric_loader import load_rubric

        rubric = load_rubric("pri_disclosure_law", REPO_ROOT)
        statute = _mini_oh_statute_bundle()
        prompt_path = REPO_ROOT / "src/scoring/retrieval_agent_prompt.md"
        output_path = REPO_ROOT / "data/statutes/OH/2010/crossrefs_hop1.json"
        brief = build_retrieval_subagent_brief(
            state="OH",
            rubric=rubric,
            statute=statute,
            repo_root=REPO_ROOT,
            retrieval_prompt_path=prompt_path,
            output_json_path=output_path,
        )
        assert str(prompt_path) in brief
        assert str(output_path) in brief

    def test_brief_includes_artifact_roles(self) -> None:
        from scoring.bundle import build_retrieval_subagent_brief
        from scoring.rubric_loader import load_rubric

        rubric = load_rubric("pri_disclosure_law", REPO_ROOT)
        statute = _mini_oh_statute_bundle()
        brief = build_retrieval_subagent_brief(
            state="OH",
            rubric=rubric,
            statute=statute,
            repo_root=REPO_ROOT,
            retrieval_prompt_path=REPO_ROOT / "src/scoring/retrieval_agent_prompt.md",
            output_json_path=REPO_ROOT / "data/statutes/OH/2010/crossrefs_hop1.json",
        )
        assert "core_chapter" in brief


# ---------------------------------------------------------------------------
# ingest_crossrefs: deterministic fetch + manifest update
# ---------------------------------------------------------------------------

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


def _build_core_bundle(tmp_path: Path) -> Path:
    """Create a minimal core-only OH bundle on disk."""
    bundle_dir = tmp_path / "data" / "statutes" / "OH" / "2010"
    sections = bundle_dir / "sections"
    sections.mkdir(parents=True)
    text = "Section 101.70. As used in sections 101.70 to 101.79 of the Revised Code..."
    section_file = sections / "title1-chapter101-101_70.txt"
    section_file.write_text(text, encoding="utf-8")
    raw = section_file.read_bytes()
    manifest = {
        "state_abbr": "OH",
        "vintage_year": 2010,
        "year_delta": 0,
        "direction": "exact",
        "pri_state_reviewed": True,
        "retrieved_at": "2026-04-29T12:00:00+00:00",
        "artifacts": [{
            "url": "https://law.justia.com/codes/ohio/2010/title1/chapter101/101_70.html",
            "role": "core_chapter",
            "sha256": hashlib.sha256(raw).hexdigest(),
            "bytes": len(raw),
            "local_path": "sections/title1-chapter101-101_70.txt",
            "hop": 0,
            "retrieved_because": "curated core lobbying chapter",
            "referenced_from": "",
        }],
    }
    (bundle_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return bundle_dir


class TestIngestCrossrefs:
    """ingest_crossrefs reads agent output JSON, fetches URLs, and
    appends support_chapter artifacts to the manifest."""

    def test_appends_support_chapter_to_manifest(self, tmp_path: Path) -> None:
        from scoring.statute_retrieval import ingest_crossrefs

        bundle_dir = _build_core_bundle(tmp_path)
        support_url = "https://law.justia.com/codes/ohio/2010/title1/chapter102/102_01.html"
        client = FakeClient({support_url: _statute_html("Section 102.01. Definitions.")})

        agent_output = {
            "state_abbr": "OH",
            "vintage_year": 2010,
            "hop": 1,
            "cross_references": [{
                "section_reference": "§102.01",
                "referenced_from": "sections/title1-chapter101-101_70.txt",
                "relevance": "Defines 'expenditure' by reference to §101.70",
                "rubric_items_affected": ["E1a", "E1b"],
                "justia_url": support_url,
                "url_confidence": "high",
                "url_confidence_reason": "Same title as core chapters",
            }],
            "unresolvable_references": [],
        }
        crossrefs_path = bundle_dir / "crossrefs_hop1.json"
        crossrefs_path.write_text(json.dumps(agent_output), encoding="utf-8")

        ingest_crossrefs(
            client=client,
            bundle_dir=bundle_dir,
            crossrefs_path=crossrefs_path,
        )

        manifest = json.loads((bundle_dir / "manifest.json").read_text(encoding="utf-8"))
        assert len(manifest["artifacts"]) == 2
        support = manifest["artifacts"][1]
        assert support["role"] == "support_chapter"
        assert support["hop"] == 1
        assert "102.01" in support["retrieved_because"]
        assert support["referenced_from"] == "sections/title1-chapter101-101_70.txt"

    def test_fetches_correct_url(self, tmp_path: Path) -> None:
        from scoring.statute_retrieval import ingest_crossrefs

        bundle_dir = _build_core_bundle(tmp_path)
        support_url = "https://law.justia.com/codes/ohio/2010/title1/chapter102/102_01.html"
        client = FakeClient({support_url: _statute_html("Section 102.01.")})

        agent_output = {
            "state_abbr": "OH",
            "vintage_year": 2010,
            "hop": 1,
            "cross_references": [{
                "section_reference": "§102.01",
                "referenced_from": "sections/title1-chapter101-101_70.txt",
                "relevance": "Defines expenditure",
                "rubric_items_affected": ["E1a"],
                "justia_url": support_url,
                "url_confidence": "high",
                "url_confidence_reason": "",
            }],
            "unresolvable_references": [],
        }
        crossrefs_path = bundle_dir / "crossrefs_hop1.json"
        crossrefs_path.write_text(json.dumps(agent_output), encoding="utf-8")

        ingest_crossrefs(client=client, bundle_dir=bundle_dir, crossrefs_path=crossrefs_path)
        assert client.fetched == [support_url]

    def test_writes_section_file(self, tmp_path: Path) -> None:
        from scoring.statute_retrieval import ingest_crossrefs

        bundle_dir = _build_core_bundle(tmp_path)
        support_url = "https://law.justia.com/codes/ohio/2010/title1/chapter102/102_01.html"
        client = FakeClient({support_url: _statute_html("Section 102.01. Important definition.")})

        agent_output = {
            "state_abbr": "OH",
            "vintage_year": 2010,
            "hop": 1,
            "cross_references": [{
                "section_reference": "§102.01",
                "referenced_from": "sections/title1-chapter101-101_70.txt",
                "relevance": "Defines expenditure",
                "rubric_items_affected": ["E1a"],
                "justia_url": support_url,
                "url_confidence": "high",
                "url_confidence_reason": "",
            }],
            "unresolvable_references": [],
        }
        crossrefs_path = bundle_dir / "crossrefs_hop1.json"
        crossrefs_path.write_text(json.dumps(agent_output), encoding="utf-8")

        ingest_crossrefs(client=client, bundle_dir=bundle_dir, crossrefs_path=crossrefs_path)

        # Support chapter text file should exist in sections/
        sections = list((bundle_dir / "sections").glob("*102*"))
        assert len(sections) == 1
        text = sections[0].read_text(encoding="utf-8")
        assert "Important definition" in text

    def test_skips_duplicate_urls(self, tmp_path: Path) -> None:
        from scoring.statute_retrieval import ingest_crossrefs

        bundle_dir = _build_core_bundle(tmp_path)
        # The core bundle already has 101_70 — agent should not re-fetch it
        already_in_bundle_url = "https://law.justia.com/codes/ohio/2010/title1/chapter101/101_70.html"
        client = FakeClient({})  # no responses needed — should not be called

        agent_output = {
            "state_abbr": "OH",
            "vintage_year": 2010,
            "hop": 1,
            "cross_references": [{
                "section_reference": "§101.70",
                "referenced_from": "sections/title1-chapter101-101_70.txt",
                "relevance": "Already in bundle",
                "rubric_items_affected": [],
                "justia_url": already_in_bundle_url,
                "url_confidence": "high",
                "url_confidence_reason": "",
            }],
            "unresolvable_references": [],
        }
        crossrefs_path = bundle_dir / "crossrefs_hop1.json"
        crossrefs_path.write_text(json.dumps(agent_output), encoding="utf-8")

        ingest_crossrefs(client=client, bundle_dir=bundle_dir, crossrefs_path=crossrefs_path)

        # Should not have fetched anything
        assert client.fetched == []
        # Manifest should still have only 1 artifact
        manifest = json.loads((bundle_dir / "manifest.json").read_text(encoding="utf-8"))
        assert len(manifest["artifacts"]) == 1

    def test_preserves_existing_artifacts(self, tmp_path: Path) -> None:
        from scoring.statute_retrieval import ingest_crossrefs

        bundle_dir = _build_core_bundle(tmp_path)
        support_url = "https://law.justia.com/codes/ohio/2010/title1/chapter102/102_01.html"
        client = FakeClient({support_url: _statute_html("Section 102.01.")})

        agent_output = {
            "state_abbr": "OH",
            "vintage_year": 2010,
            "hop": 1,
            "cross_references": [{
                "section_reference": "§102.01",
                "referenced_from": "sections/title1-chapter101-101_70.txt",
                "relevance": "Defines expenditure",
                "rubric_items_affected": ["E1a"],
                "justia_url": support_url,
                "url_confidence": "high",
                "url_confidence_reason": "",
            }],
            "unresolvable_references": [],
        }
        crossrefs_path = bundle_dir / "crossrefs_hop1.json"
        crossrefs_path.write_text(json.dumps(agent_output), encoding="utf-8")

        ingest_crossrefs(client=client, bundle_dir=bundle_dir, crossrefs_path=crossrefs_path)

        manifest = json.loads((bundle_dir / "manifest.json").read_text(encoding="utf-8"))
        # Original core chapter is still there
        assert manifest["artifacts"][0]["role"] == "core_chapter"
        assert manifest["artifacts"][0]["url"].endswith("101_70.html")
