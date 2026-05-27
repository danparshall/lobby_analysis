"""Polite fetcher + on-disk checkpoint layer for the per-principal
detail pages on ``lobbying.wi.gov``.

Thin wrapper around the generic ``entity_fetcher`` module. Binds the
principal URL template and the ``"principal_id"`` kwarg/field names.

Parallel to ``authorization_fetcher.py`` (which binds the lobbyist
side). The two wrappers exist so callers can import a function with
a domain-meaningful name (``fetch_principal_page``,
``fetch_or_load_principal``) rather than passing URL templates
explicitly at every call site.

Checkpoint shape::

    {
      "principal_id": 12997,
      "html": "<html>...</html>"  | null  (null for 404),
      "fetched_at": "2026-05-26T12:34:56Z",
      "status_code": 200 | 404
    }
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

PRINCIPAL_PAGE_URL_TEMPLATE = (
    "https://lobbying.wi.gov/Who/PrincipalInformation/{session_id}"
    "/Information/{principal_id}"
)


def fetch_principal_page(
    principal_id: int,
    session: _SessionLike,
    *,
    delay: float = 1.0,
    max_retries: int = 3,
    session_id: str = "2025REG",
    user_agent: str = DEFAULT_USER_AGENT,
) -> str | None:
    """GET the principal's detail page; return its HTML, or ``None`` on
    404 (hard or soft)."""
    return fetch_entity_page(
        principal_id,
        session,
        url_template=PRINCIPAL_PAGE_URL_TEMPLATE,
        url_kwarg_name="principal_id",
        delay=delay,
        max_retries=max_retries,
        session_id=session_id,
        user_agent=user_agent,
    )


def fetch_or_load_principal(
    principal_id: int,
    checkpoint_dir: Path,
    session: _SessionLike,
    *,
    delay: float = 1.0,
    max_retries: int = 3,
    session_id: str = "2025REG",
    user_agent: str = DEFAULT_USER_AGENT,
) -> dict[str, Any]:
    """Return the (cached or freshly-fetched) checkpoint payload for
    ``principal_id``.

    Resume contract: if ``{principal_id}.json`` exists in
    ``checkpoint_dir``, returns it as-is without any HTTP traffic.
    Otherwise fetches, writes the checkpoint, and returns the same
    structure.
    """
    return fetch_or_load_entity(
        principal_id,
        checkpoint_dir,
        session,
        url_template=PRINCIPAL_PAGE_URL_TEMPLATE,
        url_kwarg_name="principal_id",
        id_field_name="principal_id",
        delay=delay,
        max_retries=max_retries,
        session_id=session_id,
        user_agent=user_agent,
    )
