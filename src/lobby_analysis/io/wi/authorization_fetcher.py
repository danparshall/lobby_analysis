"""Polite fetcher + on-disk checkpoint layer for the per-lobbyist
detail pages on ``lobbying.wi.gov``.

Two functions:

* ``fetch_lobbyist_page(lobbyist_id, session, *, delay, max_retries)`` —
  HTTP GET with retry on 5xx and ``None`` return on 404. Sleeps for
  ``delay`` seconds AFTER each request (politeness floor). Returns the
  page HTML or ``None``.

* ``fetch_or_load(lobbyist_id, checkpoint_dir, session, *, delay, ...)`` —
  resume-friendly wrapper. If ``{lobbyist_id}.json`` already exists in
  ``checkpoint_dir``, returns the cached payload without touching the
  network. Otherwise fetches, writes the checkpoint (including 404s as
  ``html: null``), and returns the payload.

Checkpoint shape::

    {
      "lobbyist_id": 11042,
      "html": "<html>...</html>"  | null  (null for 404),
      "fetched_at": "2026-05-26T12:34:56Z",
      "status_code": 200 | 404
    }

Storing the full HTML lets us re-parse without re-scraping (the parser
in ``authorization_parser.py`` may change but the page snapshot is
fixed). Per Dan's experiment-data-integrity rules in CLAUDE.md.
"""

from __future__ import annotations

import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Protocol

import requests

DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_5) "
    "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15"
)

LOBBYIST_PAGE_URL_TEMPLATE = (
    "https://lobbying.wi.gov/Who/LobbyistInformation/{session_id}"
    "/Information/{lobbyist_id}?tab=Profile"
)


class _SessionLike(Protocol):
    """Structural type for what we need from ``requests.Session`` — also
    satisfied by the test suite's ``_FakeSession``."""

    def get(self, url: str, **kwargs: Any) -> Any: ...


def _is_soft_404(html: str) -> bool:
    """The WI portal returns HTTP 200 with a "Page Not Found" body for
    nonexistent lobbyist IDs. Distinguishable by the page title and an
    ``<h1>Page Not Found</h1>`` heading — neither marker appears on a
    real lobbyist detail page.
    """
    return (
        "<title>Page Not Found" in html
        or "Page Not Found</h1>" in html
    )


def fetch_lobbyist_page(
    lobbyist_id: int,
    session: _SessionLike,
    *,
    delay: float = 1.0,
    max_retries: int = 3,
    session_id: str = "2025REG",
    user_agent: str = DEFAULT_USER_AGENT,
) -> str | None:
    """GET the lobbyist's detail page; return its HTML, or ``None`` on
    404.

    Retries on 5xx up to ``max_retries`` times (4 attempts total).
    Sleeps for ``delay`` seconds AFTER each request, including on
    retry, to enforce the politeness floor against the live portal.
    Pass ``delay=0.0`` in unit tests.
    """
    url = LOBBYIST_PAGE_URL_TEMPLATE.format(
        session_id=session_id, lobbyist_id=lobbyist_id
    )
    headers = {"User-Agent": user_agent}

    last_error: requests.HTTPError | None = None
    for _attempt in range(max_retries + 1):
        response = session.get(url, headers=headers, timeout=30)
        if delay > 0:
            time.sleep(delay)

        if response.status_code == 404:
            return None
        if 500 <= response.status_code < 600:
            try:
                response.raise_for_status()
            except requests.HTTPError as exc:
                last_error = exc
            continue

        response.raise_for_status()
        if _is_soft_404(response.text):
            return None
        return response.text

    # Exhausted retries on 5xx — re-raise the last error.
    assert last_error is not None
    raise last_error


def fetch_or_load(
    lobbyist_id: int,
    checkpoint_dir: Path,
    session: _SessionLike,
    *,
    delay: float = 1.0,
    max_retries: int = 3,
    session_id: str = "2025REG",
    user_agent: str = DEFAULT_USER_AGENT,
) -> dict[str, Any]:
    """Return the (cached or freshly-fetched) checkpoint payload for
    ``lobbyist_id``.

    Resume contract: if ``{lobbyist_id}.json`` exists in
    ``checkpoint_dir``, returns it as-is without any HTTP traffic.
    Otherwise fetches, writes the checkpoint, and returns the same
    structure.
    """
    checkpoint_dir = Path(checkpoint_dir)
    checkpoint_file = checkpoint_dir / f"{lobbyist_id}.json"

    if checkpoint_file.exists():
        with checkpoint_file.open("r", encoding="utf-8") as fh:
            return json.load(fh)

    html = fetch_lobbyist_page(
        lobbyist_id,
        session,
        delay=delay,
        max_retries=max_retries,
        session_id=session_id,
        user_agent=user_agent,
    )
    payload: dict[str, Any] = {
        "lobbyist_id": lobbyist_id,
        "html": html,
        "fetched_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "status_code": 404 if html is None else 200,
    }

    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    with checkpoint_file.open("w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False)

    return payload
