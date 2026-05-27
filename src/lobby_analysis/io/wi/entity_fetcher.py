"""Generic polite fetcher + on-disk checkpoint layer for per-entity
detail pages on ``lobbying.wi.gov``.

This module factors out the entity-agnostic core of the lobbyist
authorization scrape (``authorization_fetcher.py``) so the same retry,
soft-404 detection, politeness floor, and checkpoint/resume contract
can serve both the lobbyist side and the principal side of the
bipartite authorization graph.

Two functions:

* ``fetch_entity_page(entity_id, session, *, url_template,
  url_kwarg_name, ...)`` — HTTP GET with retry on 5xx and ``None``
  return on hard or soft 404. Sleeps for ``delay`` seconds AFTER each
  request (politeness floor).

* ``fetch_or_load_entity(entity_id, checkpoint_dir, session, *,
  url_template, url_kwarg_name, id_field_name, ...)`` — resume-friendly
  wrapper. If ``{entity_id}.json`` already exists in
  ``checkpoint_dir``, returns the cached payload without touching the
  network. Otherwise fetches, writes the checkpoint (including 404s as
  ``html: null``), and returns the payload. The ``id_field_name``
  parameter controls the key under which the entity ID appears in the
  payload — ``"lobbyist_id"`` for lobbyist-side scrapes,
  ``"principal_id"`` for principal-side scrapes.

The lobbyist-side and principal-side fetchers (``authorization_fetcher``
and any future ``principal_fetcher``) are thin wrappers around these
generics that bind a URL template + the appropriate kwarg/field names.
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


class _SessionLike(Protocol):
    """Structural type for what we need from ``requests.Session`` — also
    satisfied by the test suite's ``_FakeSession``."""

    def get(self, url: str, **kwargs: Any) -> Any: ...


def _is_soft_404(html: str) -> bool:
    """The WI portal returns HTTP 200 with a "Page Not Found" body for
    nonexistent entity IDs. Distinguishable by the page title and an
    ``<h1>Page Not Found</h1>`` heading — neither marker appears on a
    real entity detail page.

    Lobbyist-side soft-404 observed on ID 12717 in the 2026-05-26
    scrape; principal-side has the same body markers (verified during
    the SAL-table investigation that returned this exact body for an
    invalid endpoint).
    """
    return (
        "<title>Page Not Found" in html
        or "Page Not Found</h1>" in html
    )


def fetch_entity_page(
    entity_id: int,
    session: _SessionLike,
    *,
    url_template: str,
    url_kwarg_name: str,
    delay: float = 1.0,
    max_retries: int = 3,
    session_id: str = "2025REG",
    user_agent: str = DEFAULT_USER_AGENT,
) -> str | None:
    """GET the entity's detail page; return its HTML, or ``None`` on
    hard or soft 404.

    ``url_template`` must contain ``{session_id}`` and
    ``{<url_kwarg_name>}`` placeholders — e.g. for the lobbyist side,
    ``url_kwarg_name="lobbyist_id"`` and the template contains
    ``{lobbyist_id}``; for the principal side, ``url_kwarg_name=
    "principal_id"`` and the template contains ``{principal_id}``.

    Retries on 5xx up to ``max_retries`` times (4 attempts total).
    Sleeps for ``delay`` seconds AFTER each request, including on
    retry, to enforce the politeness floor against the live portal.
    Pass ``delay=0.0`` in unit tests.
    """
    url = url_template.format(session_id=session_id, **{url_kwarg_name: entity_id})
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


def fetch_or_load_entity(
    entity_id: int,
    checkpoint_dir: Path,
    session: _SessionLike,
    *,
    url_template: str,
    url_kwarg_name: str,
    id_field_name: str,
    delay: float = 1.0,
    max_retries: int = 3,
    session_id: str = "2025REG",
    user_agent: str = DEFAULT_USER_AGENT,
) -> dict[str, Any]:
    """Return the (cached or freshly-fetched) checkpoint payload for
    ``entity_id``.

    Resume contract: if ``{entity_id}.json`` exists in
    ``checkpoint_dir``, returns it as-is without any HTTP traffic.
    Otherwise fetches, writes the checkpoint, and returns the same
    structure.

    The payload uses ``id_field_name`` as the key for the entity ID
    (e.g. ``"lobbyist_id"`` or ``"principal_id"``) so downstream
    consumers can identify which side of the bipartite graph the
    checkpoint came from.
    """
    checkpoint_dir = Path(checkpoint_dir)
    checkpoint_file = checkpoint_dir / f"{entity_id}.json"

    if checkpoint_file.exists():
        with checkpoint_file.open("r", encoding="utf-8") as fh:
            return json.load(fh)

    html = fetch_entity_page(
        entity_id,
        session,
        url_template=url_template,
        url_kwarg_name=url_kwarg_name,
        delay=delay,
        max_retries=max_retries,
        session_id=session_id,
        user_agent=user_agent,
    )
    payload: dict[str, Any] = {
        id_field_name: entity_id,
        "html": html,
        "fetched_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "status_code": 404 if html is None else 200,
    }

    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    with checkpoint_file.open("w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False)

    return payload
