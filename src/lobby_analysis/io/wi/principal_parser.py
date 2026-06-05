"""Parse the "Authorized Lobbyists" section of a lobbying.wi.gov
principal-information page into structured Authorization records.

Mirror of ``authorization_parser.parse_lobbyist_authorizations`` for
the other side of the bipartite (lobbyist, principal) graph. Same
``Authorization`` schema, same ``ParseError`` semantics; only the
HTML heading text, the href pattern, and which endpoint is stamped
on every record differ.

Source HTML shape (verified against principal 12997 / WCTA, principal
11348 / Lexia, principal 11530 / privacy-redacted, principal 10949 /
Apex Clean Energy ceased — all 2026-05-26 captures):

    <h3>Authorized Lobbyists</h3>
    <div class="card bg-light mb-4"><div class="card-body">
      <table class="table table-striped table-hover table-responsive-stack">
        <thead><tr>
          <th>Lobbyist Name</th><th>Exclusive Duties</th>
          <th>Authorized On</th><th>Withdrawn On</th>
        </tr></thead>
        <tbody>
          <tr>
            <td class="label">
              <a href="/Who/LobbyistInformation/2025REG/Information/{lobbyist_id}">
                {lobbyist_name}
              </a>
            </td>
            <td><span class="table-responsive-stack-thead">Exclusive Duties</span> {Yes|No}</td>
            <td><span class="table-responsive-stack-thead">Authorized On</span> {M/D/YYYY}</td>
            <td><span class="table-responsive-stack-thead">Withdrawn On</span> {M/D/YYYY|N/A}</td>
          </tr>
          ...
        </tbody>
      </table>
    </div></div>

The lobbyist-side parser's column header reads ``Exclusive?``; the
principal-side reads ``Exclusive Duties``. Otherwise the table layout
is symmetric.

Privacy-redacted principals (e.g., 11530, 13137 — "low-spend pledge"
entities under the <$500/yr Ethics Commission exemption): the page
title and principal-info section are suppressed but the
"Authorized Lobbyists" heading IS present and the rows ARE
populated. The parser keys on the heading, not on the principal-info
section, so redacted pages parse cleanly.
"""

from __future__ import annotations

import re
from datetime import date, datetime

from bs4 import BeautifulSoup

from lobby_analysis.io.wi.authorization_parser import Authorization, ParseError

_LOBBYIST_HREF_RE = re.compile(
    r"/Who/LobbyistInformation/\d+REG/Information/(?P<id>\d+)"
)


def parse_principal_authorizations(
    html: str, principal_id: int
) -> list[Authorization]:
    """Extract every (lobbyist, authorized_on, withdrawn_on) edge from
    a principal's "Authorized Lobbyists" table on lobbying.wi.gov.

    ``principal_id`` is stamped on every returned ``Authorization``;
    the parser does not try to discover it from the HTML (the
    redacted-principal case suppresses the principal-info section, so
    the principal name/ID would not be derivable from the page).
    """
    soup = BeautifulSoup(html, "lxml")

    heading = soup.find(
        "h3", string=lambda s: s and s.strip() == "Authorized Lobbyists"
    )
    if heading is None:
        raise ParseError(
            "Could not find '<h3>Authorized Lobbyists</h3>' section on "
            f"the principal page (principal_id={principal_id}). The portal "
            "DOM may have changed."
        )

    table = heading.find_next("table")
    if table is None:
        raise ParseError(
            f"Found 'Authorized Lobbyists' heading but no following "
            f"<table> (principal_id={principal_id})."
        )

    tbody = table.find("tbody")
    if tbody is None:
        # Empty / malformed table — treat as no rows rather than a
        # parse error, since the heading is still present.
        return []

    authorizations: list[Authorization] = []
    for row in tbody.find_all("tr"):
        cells = row.find_all("td")
        if len(cells) < 4:
            # Skip rows that don't have the expected 4-column layout.
            continue

        lobbyist_cell, _exclusive_cell, authorized_cell, withdrawn_cell = cells[:4]

        lobbyist_id = _extract_lobbyist_id(lobbyist_cell, principal_id)
        authorized_on = _extract_optional_date(
            authorized_cell, "Authorized On", principal_id
        )
        withdrawn_on = _extract_optional_date(
            withdrawn_cell, "Withdrawn On", principal_id
        )

        authorizations.append(
            Authorization(
                lobbyist_id=lobbyist_id,
                principal_id=principal_id,
                authorized_on=authorized_on,
                withdrawn_on=withdrawn_on,
            )
        )

    return authorizations


def _extract_lobbyist_id(cell, principal_id: int) -> int:
    link = cell.find("a", href=_LOBBYIST_HREF_RE)
    if link is None:
        raise ParseError(
            "Could not find lobbyist link in 'Authorized Lobbyists' row "
            f"for principal_id={principal_id}."
        )
    match = _LOBBYIST_HREF_RE.search(link["href"])
    assert match is not None
    return int(match.group("id"))


def _cell_value_text(cell, label: str) -> str:
    """Return the cell text with the responsive-table label stripped.

    Portal markup is:

        <td><span class="table-responsive-stack-thead">{label}</span> {value}</td>

    We want only ``{value}``.
    """
    label_span = cell.find("span", class_="table-responsive-stack-thead")
    if label_span is not None:
        label_span.extract()
    return cell.get_text(strip=True)


def _extract_optional_date(cell, label: str, principal_id: int) -> date | None:
    text = _cell_value_text(cell, label)
    if text.upper() == "N/A" or text == "":
        return None
    try:
        return datetime.strptime(text, "%m/%d/%Y").date()
    except ValueError as exc:
        raise ParseError(
            f"Could not parse optional '{label}' date '{text}' for "
            f"principal_id={principal_id}."
        ) from exc
