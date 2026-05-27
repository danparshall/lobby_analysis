"""Polite fetcher + on-disk checkpoint layer for the per-lobbyist
detail pages on ``lobbying.wi.gov``.

Thin wrapper around the generic ``entity_fetcher`` module. Binds the
lobbyist URL template and the ``"lobbyist_id"`` kwarg/field names.

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

from pathlib import Path
from typing import Any

from lobby_analysis.io.wi.entity_fetcher import (
    DEFAULT_USER_AGENT,
    _SessionLike,
    fetch_entity_page,
    fetch_or_load_entity,
)

LOBBYIST_PAGE_URL_TEMPLATE = (
    "https://lobbying.wi.gov/Who/LobbyistInformation/{session_id}"
    "/Information/{lobbyist_id}?tab=Profile"
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
    404 (hard or soft).
    """
    return fetch_entity_page(
        lobbyist_id,
        session,
        url_template=LOBBYIST_PAGE_URL_TEMPLATE,
        url_kwarg_name="lobbyist_id",
        delay=delay,
        max_retries=max_retries,
        session_id=session_id,
        user_agent=user_agent,
    )


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
    return fetch_or_load_entity(
        lobbyist_id,
        checkpoint_dir,
        session,
        url_template=LOBBYIST_PAGE_URL_TEMPLATE,
        url_kwarg_name="lobbyist_id",
        id_field_name="lobbyist_id",
        delay=delay,
        max_retries=max_retries,
        session_id=session_id,
        user_agent=user_agent,
    )
