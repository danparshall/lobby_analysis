"""Tests for retrieve_statute_bundle.

Uses a FakeClient with canned HTML rather than real Playwright fetches.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from scoring.statute_retrieval import retrieve_statute_bundle


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


CA_URL_1 = "https://law.justia.com/codes/california/2010/gov/86100-86118.html"
CA_URL_2 = "https://law.justia.com/codes/california/2010/gov/86201-86206.html"
TX_URL = (
    "https://law.justia.com/codes/texas/2009/government-code/"
    "title-3-legislative-branch/chapter-305-registration-of-lobbyists/"
)


def test_retrieve_statute_bundle_writes_manifest_and_sections(tmp_path: Path) -> None:
    urls = [CA_URL_1, CA_URL_2]
    client = FakeClient(
        {
            CA_URL_1: _statute_html("Section 86100. Lobbyist means any individual."),
            CA_URL_2: _statute_html("Section 86201. No lobbyist shall ..."),
        }
    )
    manifest_path = retrieve_statute_bundle(
        client,
        state_abbr="CA",
        vintage_year=2010,
        urls=urls,
        dest_dir=tmp_path,
        year_delta=0,
        direction="exact",
        pri_state_reviewed=True,
    )
    assert manifest_path == tmp_path / "manifest.json"
    assert manifest_path.exists()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["state_abbr"] == "CA"
    assert manifest["vintage_year"] == 2010
    assert manifest["year_delta"] == 0
    assert manifest["direction"] == "exact"
    assert manifest["pri_state_reviewed"] is True
    assert len(manifest["artifacts"]) == 2
    # Both section .txt files exist under sections/.
    sections = tmp_path / "sections"
    assert (sections / "gov-86100-86118.txt").exists()
    assert (sections / "gov-86201-86206.txt").exists()


def test_retrieve_statute_bundle_stores_parsed_text_not_raw_html(tmp_path: Path) -> None:
    # The section file should hold statute text, chrome stripped. Raw HTML tags
    # and the "Find a Lawyer" chrome must not leak through.
    client = FakeClient(
        {CA_URL_1: _statute_html("Section 86100. Lobbyist means any individual.")}
    )
    retrieve_statute_bundle(
        client,
        state_abbr="CA",
        vintage_year=2010,
        urls=[CA_URL_1],
        dest_dir=tmp_path,
    )
    text = (tmp_path / "sections" / "gov-86100-86118.txt").read_text(encoding="utf-8")
    assert "<div" not in text
    assert "<p>" not in text
    assert "Find a Lawyer" not in text
    assert "Lobbyist means any individual" in text


def test_retrieve_statute_bundle_sha256_matches_contents(tmp_path: Path) -> None:
    client = FakeClient(
        {CA_URL_1: _statute_html("Section 86100. Lobbyist means any individual.")}
    )
    retrieve_statute_bundle(
        client,
        state_abbr="CA",
        vintage_year=2010,
        urls=[CA_URL_1],
        dest_dir=tmp_path,
    )
    manifest = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
    artifact = manifest["artifacts"][0]
    section_bytes = (tmp_path / artifact["local_path"]).read_bytes()
    expected_sha = hashlib.sha256(section_bytes).hexdigest()
    assert artifact["sha256"] == expected_sha
    assert artifact["bytes"] == len(section_bytes)


def test_retrieve_statute_bundle_raises_on_empty_urls(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="empty"):
        retrieve_statute_bundle(
            FakeClient({}),
            state_abbr="CA",
            vintage_year=2010,
            urls=[],
            dest_dir=tmp_path,
        )


def test_retrieve_statute_bundle_filename_for_trailing_slash_url(tmp_path: Path) -> None:
    # TX uses trailing-slash URLs. Filename should derive sensibly from the
    # last non-empty path segment, not produce an empty-extension file.
    client = FakeClient({TX_URL: _statute_html("Sec. 305.001. Registrant means...")})
    retrieve_statute_bundle(
        client,
        state_abbr="TX",
        vintage_year=2009,
        urls=[TX_URL],
        dest_dir=tmp_path,
        year_delta=-1,
        direction="pre",
    )
    sections = tmp_path / "sections"
    txts = list(sections.glob("*.txt"))
    assert len(txts) == 1
    # Name should reference the chapter slug, not be empty or collide.
    name = txts[0].name
    assert "chapter-305" in name
    assert name.endswith(".txt")


def test_retrieve_statute_bundle_fetch_order_matches_urls(tmp_path: Path) -> None:
    # FakeClient.fetched records order; retrieval should hit URLs in input order.
    urls = [CA_URL_1, CA_URL_2]
    client = FakeClient(
        {CA_URL_1: _statute_html("one"), CA_URL_2: _statute_html("two")}
    )
    retrieve_statute_bundle(
        client,
        state_abbr="CA",
        vintage_year=2010,
        urls=urls,
        dest_dir=tmp_path,
    )
    assert client.fetched == urls
