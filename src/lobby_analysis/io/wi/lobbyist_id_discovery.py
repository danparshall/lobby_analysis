"""Discover the 2025-2026-session lobbyist IDs on lobbying.wi.gov.

The bulk ``.xls`` directory export at
``/Who/Lobbyists/2025REG/ReportExport`` carries 12 columns of lobbyist
metadata but no Lobbyist ID column. The IDs live in the per-lobbyist
detail-page URLs (``/Who/LobbyistInformation/2025REG/Information/{id}``)
linked from the LobbyistList grid.

The grid is server-paginated 25 results at a time by default, but it
accepts an arbitrary ``pageSize`` over POST to the underlying AJAX
endpoint. ``pageSize=1000`` returns all 774 rows of the 2025-2026
session in a single 353 KB response.

How the endpoint was discovered (2026-05-26): the LobbyistList grid's
HTML carries ``data-grid-type="server"`` plus the controller path
``Who/Lobbyists/2025REG``. The shared client-side JS (``/Content/site.js``)
defines ``refreshGrid`` to POST to ``urls.view`` — constructed as
``{appPath}/{controller}/Show{type}``. Substituting gives
``/Who/Lobbyists/2025REG/ShowLobbyistList``. Form fields: ``Session``,
``SearchText`` (optional), ``pageNumber``, ``pageSize``, ``sortField``,
``isSortAscending``.
"""

from __future__ import annotations

import re

import requests

LOBBYIST_HREF_RE = re.compile(
    r"/Who/LobbyistInformation/\d+REG/Information/(?P<id>\d+)"
)

GRID_ENDPOINT_TEMPLATE = (
    "https://lobbying.wi.gov/Who/Lobbyists/{session_id}/ShowLobbyistList"
)
DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_5) "
    "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15"
)


def parse_lobbyist_ids(html: str) -> list[int]:
    """Return all distinct lobbyist IDs referenced by detail-page hrefs in
    the given grid HTML, sorted ascending.

    Pure function — the test suite exercises it against a saved fixture
    of a real LobbyistList grid response.
    """
    matches = LOBBYIST_HREF_RE.findall(html)
    return sorted({int(m) for m in matches})


def fetch_lobbyist_grid_html(
    session: requests.Session,
    session_id: str = "2025REG",
    page_size: int = 1000,
    user_agent: str = DEFAULT_USER_AGENT,
) -> str:
    """POST to the LobbyistList grid endpoint and return the HTML
    fragment that lists every lobbyist for ``session_id``.

    ``page_size=1000`` is sufficient to fit the full 2025-2026 session
    (774 rows) in one response. Bump if a future session is larger.
    """
    url = GRID_ENDPOINT_TEMPLATE.format(session_id=session_id)
    response = session.post(
        url,
        data={
            "Session": session_id,
            "SearchText": "",
            "pageNumber": "1",
            "pageSize": str(page_size),
            "sortField": "",
            "isSortAscending": "true",
        },
        headers={"User-Agent": user_agent},
        timeout=30,
    )
    response.raise_for_status()
    return response.text
