"""Integration tests for the `orchestrator retrieve-statutes` path."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from scoring.lobbying_statute_urls import CALIBRATION_SUBSET, LOBBYING_STATUTE_URLS
from scoring.statute_retrieval import retrieve_bundles_for_states


def _statute_html(body_text: str) -> str:
    return f'<html><body><div id="main-content">{body_text}</div></body></html>'


class FakeClient:
    def __init__(self, url_to_html: dict[str, str]) -> None:
        self._pages = url_to_html
        self.fetched: list[str] = []

    def fetch_page(self, url: str) -> str:
        self.fetched.append(url)
        if url not in self._pages:
            raise KeyError(f"FakeClient has no response for {url}")
        return self._pages[url]


def test_retrieve_bundles_for_ca_2010_writes_under_state_year(tmp_path: Path) -> None:
    urls = LOBBYING_STATUTE_URLS[("CA", 2010)]
    client = FakeClient({u: _statute_html(f"CA statute text {i}") for i, u in enumerate(urls)})
    paths = retrieve_bundles_for_states(
        client=client,
        targets=[("CA", 2010)],
        dest_root=tmp_path,
    )
    assert len(paths) == 1
    manifest_path = paths[0]
    assert manifest_path == tmp_path / "CA" / "2010" / "manifest.json"
    assert manifest_path.exists()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["state_abbr"] == "CA"
    assert manifest["direction"] == "exact"
    assert manifest["year_delta"] == 0
    assert manifest["pri_state_reviewed"] is True  # CA is a PRI responder
    assert len(manifest["artifacts"]) == len(urls)


def test_retrieve_bundles_tx_2009_uses_pre_direction(tmp_path: Path) -> None:
    urls = LOBBYING_STATUTE_URLS[("TX", 2009)]
    client = FakeClient({u: _statute_html("TX Ch. 305 statute text") for u in urls})
    paths = retrieve_bundles_for_states(
        client=client,
        targets=[("TX", 2009)],
        dest_root=tmp_path,
        target_year=2010,
    )
    manifest = json.loads(paths[0].read_text(encoding="utf-8"))
    assert manifest["direction"] == "pre"
    assert manifest["year_delta"] == -1


def test_retrieve_bundles_raises_on_uncurated_state(tmp_path: Path) -> None:
    with pytest.raises(KeyError, match="no curated lobby-statute URLs"):
        retrieve_bundles_for_states(
            client=FakeClient({}),
            targets=[("AK", 2010)],
            dest_root=tmp_path,
        )


def test_retrieve_bundles_all_calibration_subset(tmp_path: Path) -> None:
    # Assemble a FakeClient with canned HTML for every URL across all 5 states.
    all_urls = [u for pair in CALIBRATION_SUBSET for u in LOBBYING_STATUTE_URLS[pair]]
    client = FakeClient({u: _statute_html(f"statute at {u}") for u in all_urls})
    paths = retrieve_bundles_for_states(
        client=client,
        targets=list(CALIBRATION_SUBSET),
        dest_root=tmp_path,
    )
    assert len(paths) == 5
    # Each (state, vintage) pair got its own bundle directory.
    expected_dirs = {tmp_path / s / str(y) for s, y in CALIBRATION_SUBSET}
    got_dirs = {p.parent for p in paths}
    assert got_dirs == expected_dirs
    # Fetch order: all URLs for pair 0 before pair 1, etc.
    expected_fetch_order = all_urls
    assert client.fetched == expected_fetch_order
