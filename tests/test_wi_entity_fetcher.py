"""Behavior tests for the generic ``entity_fetcher`` extracted from
``authorization_fetcher.py``.

The extraction is motivated by adding a principal-side scrape that
hits a different URL template (``/Who/PrincipalInformation/...``) but
needs the same politeness floor, retry-on-5xx, soft-404 detection,
and checkpoint/resume contract. The generic core takes a URL template
plus the kwarg name that the template's ``{}`` placeholder uses
(``lobbyist_id`` / ``principal_id``) and the checkpoint payload's ID
field name.

These tests verify the parameterization works for both bindings.
The full set of behavior tests (retries, soft-404, cache hit/miss)
already lives in ``test_wi_authorization_fetcher.py`` and acts as the
regression suite for the refactor — those exercise the same generic
core via the lobbyist wrapper.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
import requests

from lobby_analysis.io.wi.entity_fetcher import (
    fetch_entity_page,
    fetch_or_load_entity,
)


LOBBYIST_URL_TEMPLATE = (
    "https://lobbying.wi.gov/Who/LobbyistInformation/{session_id}"
    "/Information/{lobbyist_id}?tab=Profile"
)
PRINCIPAL_URL_TEMPLATE = (
    "https://lobbying.wi.gov/Who/PrincipalInformation/{session_id}"
    "/Information/{principal_id}"
)


class _FakeResponse:
    def __init__(self, status_code: int, text: str = ""):
        self.status_code = status_code
        self.text = text

    def raise_for_status(self) -> None:
        if 400 <= self.status_code < 600:
            raise requests.HTTPError(f"status {self.status_code}", response=self)  # type: ignore[arg-type]


class _RecordingFakeSession:
    """Captures the URL passed to ``.get`` so URL-template tests can
    assert the parameterized template produced the right URL.

    Returns canned responses in order. Asserting on the URL is the
    *point* of these tests — we're verifying that the generic
    ``fetch_entity_page`` substitutes the right kwarg into the right
    placeholder. Existing fetcher tests (which don't assert on URLs)
    cover everything else.
    """

    def __init__(self, responses: list[_FakeResponse]):
        self._responses = list(responses)
        self.urls_called: list[str] = []

    def get(self, url: str, **kwargs: Any):  # noqa: ARG002
        self.urls_called.append(url)
        if not self._responses:
            raise AssertionError(
                f"Unexpected network call to {url} — fake session ran out "
                "of canned responses (tripwire)."
            )
        return self._responses.pop(0)


def test_fetch_entity_page_lobbyist_url_template_substitutes_lobbyist_id():
    """The lobbyist binding must produce the exact same URL that
    ``LOBBYIST_PAGE_URL_TEMPLATE`` produced before the refactor.

    This is the regression guard for the lobbyist code path — the
    existing 851-second authorization scrape that landed this morning
    hit URLs of this exact shape, and any drift would silently break
    resumed scrapes."""
    fake = _RecordingFakeSession([_FakeResponse(200, "<html>ok</html>")])

    html = fetch_entity_page(
        11042,
        session=fake,
        url_template=LOBBYIST_URL_TEMPLATE,
        url_kwarg_name="lobbyist_id",
        delay=0.0,
    )

    assert html == "<html>ok</html>"
    assert fake.urls_called == [
        "https://lobbying.wi.gov/Who/LobbyistInformation/2025REG/Information/11042?tab=Profile"
    ]


def test_fetch_entity_page_principal_url_template_substitutes_principal_id():
    """The principal binding must produce the principal-detail URL the
    plan keys on — same path shape as the gap-investigation captures
    (e.g., principal_12997.html = WCTA, the load-bearing Schlaak case)."""
    fake = _RecordingFakeSession([_FakeResponse(200, "<html>ok</html>")])

    html = fetch_entity_page(
        12997,
        session=fake,
        url_template=PRINCIPAL_URL_TEMPLATE,
        url_kwarg_name="principal_id",
        delay=0.0,
    )

    assert html == "<html>ok</html>"
    assert fake.urls_called == [
        "https://lobbying.wi.gov/Who/PrincipalInformation/2025REG/Information/12997"
    ]


def test_fetch_entity_page_honors_session_id_override():
    """A non-2025 session_id must substitute correctly — needed for the
    eventual cross-biennium investigation flagged in the auth-scrape
    session's Next Steps (``principal_id`` stability across sessions)."""
    fake = _RecordingFakeSession([_FakeResponse(200, "<html>ok</html>")])

    fetch_entity_page(
        12997,
        session=fake,
        url_template=PRINCIPAL_URL_TEMPLATE,
        url_kwarg_name="principal_id",
        session_id="2023REG",
        delay=0.0,
    )

    assert fake.urls_called == [
        "https://lobbying.wi.gov/Who/PrincipalInformation/2023REG/Information/12997"
    ]


def test_fetch_or_load_entity_writes_principal_id_field_in_checkpoint(
    tmp_path: Path,
):
    """The checkpoint payload's ID field name is parameterized — a
    principal scrape's checkpoints must say ``"principal_id": 12997``,
    not ``"lobbyist_id": 12997``, so downstream materialize code can
    distinguish the two sides without inferring from path conventions."""
    fake = _RecordingFakeSession([_FakeResponse(200, "<html>fresh</html>")])

    result = fetch_or_load_entity(
        entity_id=12997,
        checkpoint_dir=tmp_path,
        session=fake,
        url_template=PRINCIPAL_URL_TEMPLATE,
        url_kwarg_name="principal_id",
        id_field_name="principal_id",
        delay=0.0,
    )

    assert result["principal_id"] == 12997
    assert "lobbyist_id" not in result
    on_disk = json.loads((tmp_path / "12997.json").read_text(encoding="utf-8"))
    assert on_disk["principal_id"] == 12997
    assert on_disk["html"] == "<html>fresh</html>"


def test_fetch_or_load_entity_writes_lobbyist_id_field_in_checkpoint(
    tmp_path: Path,
):
    """Same parameterization, opposite binding — verifies the lobbyist
    side still produces the ``lobbyist_id``-keyed payload that the
    existing materialize code reads."""
    fake = _RecordingFakeSession([_FakeResponse(200, "<html>fresh</html>")])

    result = fetch_or_load_entity(
        entity_id=11042,
        checkpoint_dir=tmp_path,
        session=fake,
        url_template=LOBBYIST_URL_TEMPLATE,
        url_kwarg_name="lobbyist_id",
        id_field_name="lobbyist_id",
        delay=0.0,
    )

    assert result["lobbyist_id"] == 11042
    assert "principal_id" not in result
    on_disk = json.loads((tmp_path / "11042.json").read_text(encoding="utf-8"))
    assert on_disk["lobbyist_id"] == 11042


def test_fetch_entity_page_soft_404_detection_still_fires():
    """Soft-404 detection is a property of the WI portal, not of any
    particular entity type — the principal side is expected to have the
    same failure mode (unverified at refactor time; the prior session
    only observed soft-404s on lobbyist pages). The generic core must
    still short-circuit on the body marker so the principal scrape
    doesn't feed Page-Not-Found HTML into the principal parser."""
    soft_404_body = """<!DOCTYPE html><html><head>
        <title>Page Not Found -  Lobbying in Wisconsin</title>
        </head><body><h1 class="display-4">Page Not Found</h1>
        </body></html>"""
    fake = _RecordingFakeSession([_FakeResponse(200, soft_404_body)])

    html = fetch_entity_page(
        99999,
        session=fake,
        url_template=PRINCIPAL_URL_TEMPLATE,
        url_kwarg_name="principal_id",
        delay=0.0,
    )

    assert html is None
