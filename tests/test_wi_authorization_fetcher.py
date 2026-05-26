"""Behavior tests for the polite fetcher + checkpoint/resume layer that
backs the WI authorization scrape.

We don't pull in a network-mocking library (``requests_mock`` /
``responses``); instead the tests use a small in-test ``FakeSession``
that delivers canned responses on ``.get``. That keeps test code
explicit — no "assert the mock was called with X" assertions — and
avoids a dev-deps addition for something we use in one test file.

Live-portal behavior (real UA acceptance, real-time politeness) is
exercised by Step 9's small-batch sanity check, not by these unit
tests.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import requests

from lobby_analysis.io.wi.authorization_fetcher import (
    fetch_lobbyist_page,
    fetch_or_load,
)


class _FakeResponse:
    """Minimal ``requests.Response`` stand-in."""

    def __init__(self, status_code: int, text: str = ""):
        self.status_code = status_code
        self.text = text

    def raise_for_status(self) -> None:
        if 400 <= self.status_code < 600:
            raise requests.HTTPError(f"status {self.status_code}", response=self)  # type: ignore[arg-type]


class _FakeSession:
    """Returns canned responses on successive ``.get`` calls and counts
    how many times it was called.

    Test code asserts on *outcomes* (returned HTML, raised exception,
    on-disk checkpoint contents) — never on ``session.call_count`` as
    an end in itself. The counter exists so a "tripwire" fake (with
    zero responses queued) can fail loudly if the code under test
    decides to hit the network when it shouldn't.
    """

    def __init__(self, responses: list[_FakeResponse]):
        self._responses = list(responses)
        self.call_count = 0

    def get(self, url: str, **kwargs):  # noqa: ARG002 — kwargs ignored, mirroring requests.Session
        self.call_count += 1
        if not self._responses:
            raise AssertionError(
                f"Unexpected network call to {url} — fake session ran out "
                "of canned responses (tripwire)."
            )
        return self._responses.pop(0)


def test_fetcher_returns_html_on_200_response():
    fake = _FakeSession([_FakeResponse(200, "<html>ok</html>")])

    html = fetch_lobbyist_page(11042, session=fake, delay=0.0)

    assert html == "<html>ok</html>"


def test_fetcher_retries_on_5xx_then_succeeds():
    """A transient 5xx should not kill the scrape; the fetcher should
    retry and surface the eventual 200 body."""
    fake = _FakeSession(
        [
            _FakeResponse(503, ""),
            _FakeResponse(502, ""),
            _FakeResponse(200, "<html>recovered</html>"),
        ]
    )

    html = fetch_lobbyist_page(11042, session=fake, delay=0.0, max_retries=3)

    assert html == "<html>recovered</html>"
    assert fake.call_count == 3


def test_fetcher_raises_after_max_retries_on_persistent_5xx():
    """If the server stays broken across all retries, we surface the
    failure — silently dropping the lobbyist would corrupt the join
    table without anyone noticing."""
    fake = _FakeSession([_FakeResponse(500, "") for _ in range(4)])

    with pytest.raises(requests.HTTPError):
        fetch_lobbyist_page(11042, session=fake, delay=0.0, max_retries=3)


def test_fetcher_returns_none_on_404_without_raising():
    """Not every lobbyist ID may have a public detail page (withdrawn
    lobbyists, edge cases). 404 is expected-data, not an error — the
    caller should still get a clean ``None`` and continue."""
    fake = _FakeSession([_FakeResponse(404, "")])

    html = fetch_lobbyist_page(11042, session=fake, delay=0.0)

    assert html is None


def test_fetch_or_load_returns_cached_payload_when_checkpoint_exists(
    tmp_path: Path,
):
    """If ``{lobbyist_id}.json`` is already on disk, the fetcher must
    NOT hit the network. Verified by passing a fake session with zero
    responses queued — if the network is touched, the tripwire fires."""
    checkpoint = tmp_path / "11042.json"
    payload = {
        "lobbyist_id": 11042,
        "html": "<html>from cache</html>",
        "fetched_at": "2026-05-26T12:00:00Z",
    }
    checkpoint.write_text(json.dumps(payload), encoding="utf-8")
    tripwire_session = _FakeSession([])  # no responses — raises if .get is called

    result = fetch_or_load(
        lobbyist_id=11042,
        checkpoint_dir=tmp_path,
        session=tripwire_session,
        delay=0.0,
    )

    assert result["html"] == "<html>from cache</html>"
    assert result["lobbyist_id"] == 11042
    assert tripwire_session.call_count == 0


def test_fetch_or_load_writes_checkpoint_when_no_cache(tmp_path: Path):
    """First-time fetch must persist the HTML + lobbyist_id to disk so
    a resumed run skips the network call."""
    fake = _FakeSession([_FakeResponse(200, "<html>fresh</html>")])

    result = fetch_or_load(
        lobbyist_id=11042,
        checkpoint_dir=tmp_path,
        session=fake,
        delay=0.0,
    )

    assert result["html"] == "<html>fresh</html>"
    checkpoint_file = tmp_path / "11042.json"
    assert checkpoint_file.exists()
    on_disk = json.loads(checkpoint_file.read_text(encoding="utf-8"))
    assert on_disk["html"] == "<html>fresh</html>"
    assert on_disk["lobbyist_id"] == 11042
    assert "fetched_at" in on_disk


def test_fetch_or_load_writes_404_marker_so_resumed_runs_dont_retry(
    tmp_path: Path,
):
    """A 404 must also be persisted (with ``html=None``) — otherwise a
    resumed run hits the network again for the same not-found page."""
    fake = _FakeSession([_FakeResponse(404, "")])

    result = fetch_or_load(
        lobbyist_id=99999,
        checkpoint_dir=tmp_path,
        session=fake,
        delay=0.0,
    )

    assert result["html"] is None
    checkpoint_file = tmp_path / "99999.json"
    assert checkpoint_file.exists()
    on_disk = json.loads(checkpoint_file.read_text(encoding="utf-8"))
    assert on_disk["html"] is None
