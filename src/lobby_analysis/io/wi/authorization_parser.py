"""Parse the "Principals Represented" section of a lobbying.wi.gov
lobbyist-information page into structured Authorization records.

Source HTML shape (verified against lobbyist 11042 snapshot, 2026-05-26):

    <h3>Principals Represented</h3>
    <div class="card bg-light mb-4"><div class="card-body">
      <table class="table table-striped table-hover table-responsive-stack">
        <thead><tr>
          <th>Principal Name</th><th>Exclusive?</th>
          <th>Authorized On</th><th>Withdrawn On</th>
        </tr></thead>
        <tbody>
          <tr>
            <td class="label">
              <a href="/Who/PrincipalInformation/2025REG/Information/{principal_id}?tab=Lobbyists">
                {principal_name}
              </a>
            </td>
            <td><span class="table-responsive-stack-thead">Exclusive?</span> {Yes|No}</td>
            <td><span class="table-responsive-stack-thead">Authorized On</span> {M/D/YYYY}</td>
            <td><span class="table-responsive-stack-thead">Withdrawn On</span> {M/D/YYYY|N/A}</td>
          </tr>
          ...
        </tbody>
      </table>
    </div></div>

Date format is ``M/D/YYYY`` with no zero-padding (e.g., ``1/3/2025``,
``12/17/2024``). ``Withdrawn On`` is ``N/A`` for active authorizations.

Companion to the bulk ``.xls`` directory exports at
``data/disclosures/WI/``; building the lobbyist↔principal join table
this parser feeds is the goal of the
``wi-disclosure-explore`` branch.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date, datetime

from bs4 import BeautifulSoup

_PRINCIPAL_HREF_RE = re.compile(
    r"/Who/PrincipalInformation/\d+REG/Information/(?P<id>\d+)"
)


class ParseError(ValueError):
    """Raised when the lobbyist-page HTML does not contain the expected
    "Principals Represented" structure.

    Surfacing this loudly is intentional: a silent ``[]`` on a page-shape
    change would let an entire scrape run produce an empty join table
    without anyone noticing.
    """


@dataclass(frozen=True)
class Authorization:
    """A single (lobbyist, principal) authorization edge for one
    legislative session."""

    lobbyist_id: int
    principal_id: int
    authorized_on: date
    withdrawn_on: date | None


def parse_lobbyist_authorizations(
    html: str, lobbyist_id: int
) -> list[Authorization]:
    """Extract every (principal, authorized_on, withdrawn_on) edge from a
    lobbyist's "Principals Represented" table on lobbying.wi.gov.

    ``lobbyist_id`` is stamped on every returned ``Authorization``; the
    parser does not try to discover it from the HTML.
    """
    soup = BeautifulSoup(html, "lxml")

    heading = soup.find("h3", string=lambda s: s and s.strip() == "Principals Represented")
    if heading is None:
        raise ParseError(
            "Could not find '<h3>Principals Represented</h3>' section on "
            f"the lobbyist page (lobbyist_id={lobbyist_id}). The portal "
            "DOM may have changed."
        )

    table = heading.find_next("table")
    if table is None:
        raise ParseError(
            f"Found 'Principals Represented' heading but no following "
            f"<table> (lobbyist_id={lobbyist_id})."
        )

    tbody = table.find("tbody")
    if tbody is None:
        # Empty / malformed table — treat as no rows rather than a parse
        # error, since the heading is still present.
        return []

    authorizations: list[Authorization] = []
    for row in tbody.find_all("tr"):
        cells = row.find_all("td")
        if len(cells) < 4:
            # Skip rows that don't have the expected 4-column layout.
            # Could tighten to raise instead, but a stray malformed row
            # shouldn't kill the whole page.
            continue

        principal_cell, _exclusive_cell, authorized_cell, withdrawn_cell = cells[:4]

        principal_id = _extract_principal_id(principal_cell, lobbyist_id)
        authorized_on = _extract_date(authorized_cell, "Authorized On", lobbyist_id)
        withdrawn_on = _extract_optional_date(withdrawn_cell, "Withdrawn On", lobbyist_id)

        authorizations.append(
            Authorization(
                lobbyist_id=lobbyist_id,
                principal_id=principal_id,
                authorized_on=authorized_on,
                withdrawn_on=withdrawn_on,
            )
        )

    return authorizations


def _extract_principal_id(cell, lobbyist_id: int) -> int:
    link = cell.find("a", href=_PRINCIPAL_HREF_RE)
    if link is None:
        raise ParseError(
            "Could not find principal link in 'Principals Represented' row "
            f"for lobbyist_id={lobbyist_id}."
        )
    match = _PRINCIPAL_HREF_RE.search(link["href"])
    # Match is guaranteed since find() matched the same regex, but mypy
    # doesn't know that.
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


def _extract_date(cell, label: str, lobbyist_id: int) -> date:
    text = _cell_value_text(cell, label)
    try:
        return datetime.strptime(text, "%m/%d/%Y").date()
    except ValueError as exc:
        raise ParseError(
            f"Could not parse '{label}' date '{text}' for "
            f"lobbyist_id={lobbyist_id}."
        ) from exc


def _extract_optional_date(cell, label: str, lobbyist_id: int) -> date | None:
    text = _cell_value_text(cell, label)
    if text.upper() == "N/A" or text == "":
        return None
    try:
        return datetime.strptime(text, "%m/%d/%Y").date()
    except ValueError as exc:
        raise ParseError(
            f"Could not parse optional '{label}' date '{text}' for "
            f"lobbyist_id={lobbyist_id}."
        ) from exc
