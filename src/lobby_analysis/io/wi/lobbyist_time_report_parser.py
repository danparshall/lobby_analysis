"""Parse the Time Report Summary section of a lobbying.wi.gov
lobbyist-information page into structured Tier-2 records.

Companion to ``authorization_parser.parse_lobbyist_authorizations`` (the
authorization-edge parser at the top of the same page). This module
parses the ``<h4>Time Report Summary</h4>`` table — the lobbyist-side
analogue to the principal-side ``<h3>Total Lobbying Effort</h3>`` table
parsed by ``principal_meta_parser``.

Public surface
==============

``ParseError``
    Raised when the page lacks the expected Time Report Summary section.
    Catches soft-404 stub pages (e.g., lobbyist 12717 Neumann-Ortiz on
    the 2026-05-26 snapshot) before they slip through a materializer
    run. Mirrors the loud-fail discipline of
    ``authorization_parser.ParseError``.

``parse_lobbyist_time_reports(html, lobbyist_id)``
    Returns a two-element tuple::

        (Person, list[LobbyingFiling])

    The contract was locked in
    ``docs/active/wi-disclosure-explore/plans/wi_tier_2_parser.md`` Phase 3:

    1. ``Person`` — typed v1.1 + ``source_state="WI"`` + ``contact_details``
       (email / phone / address from the lobbyist-info ``.person-info`` card).
       Name from ``<h2 class="display-4">``. ``id`` follows the locked
       ``WI-lobbyist-{id}`` convention.

    2. ``list[LobbyingFiling]`` — one per period column in the Time Report
       Summary table. ``filer_role="lobbyist"``,
       ``filing_type="activity_report"``, ``filer_person=person``,
       populated ``total_hours_communicating`` + ``total_hours_other``
       (v1.2 fields) + ``provenance``. Zero-hours reports (in-progress
       biennium halves on the snapshot date) ARE emitted — zero is real
       data, distinct from ``None``.

Shape differences from the principal side
==========================================

- The Time Report Summary header is ``<h4>``, not ``<h3>``.
- Period column headers read ``January 2025 to June 2025`` (not
  ``2025<br />January - June`` as on the principal-side Total Lobbying
  Effort table). The regex below pins both halves of the period name.
- The table has 2 data rows (Communication + Other), no Total summary
  column, and FOUR period columns — all 4 biennium halves always
  shown, with explicit ``0`` for in-progress halves. So the parser
  always emits exactly 4 filings per lobbyist page (matching the
  table width), unlike the principal-side parser's 2 (Total Lobbying
  Effort only shows completed semesters).
"""

from __future__ import annotations

import re
from datetime import date, datetime, timezone

from bs4 import BeautifulSoup, NavigableString, Tag

from lobby_analysis.models import (
    ContactDetail,
    LobbyingFiling,
    Person,
)
from lobby_analysis.models.provenance import Provenance


class ParseError(ValueError):
    """Raised when the lobbyist-page HTML does not contain the expected
    Time Report Summary section.

    Loud-fail discipline: a silent ``[]`` on a soft-404 / page-shape change
    would let an entire Tier-2 run produce broken output without anyone
    noticing. ``authorization_parser.ParseError`` is the precedent.
    """


_SOURCE_URL_TEMPLATE = (
    "https://lobbying.wi.gov/Who/LobbyistInformation/2025REG/Information/"
    "{lobbyist_id}"
)

# Time Report Summary period header form: "January 2025 to June 2025",
# "July 2025 to December 2025", "January 2026 to June 2026", etc.
_PERIOD_HEADER_RE = re.compile(
    r"^(?P<start_month>January|July)\s+(?P<start_year>\d{4})\s+to\s+"
    r"(?P<end_month>June|December)\s+(?P<end_year>\d{4})$"
)


_TRS_LABEL_COMMUNICATION = "Communication"
_TRS_LABEL_OTHER = "Other"


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------


def parse_lobbyist_time_reports(
    html: str, lobbyist_id: int
) -> tuple[Person, list[LobbyingFiling]]:
    """Parse a lobbying.wi.gov lobbyist-information page into a Person
    plus one LobbyingFiling per period column in the Time Report Summary
    table.

    Raises ``ParseError`` when the Time Report Summary section is absent
    (soft-404 case).
    """
    soup = BeautifulSoup(html, "lxml")

    heading = soup.find(
        "h4", string=lambda s: s is not None and s.strip() == "Time Report Summary"
    )
    if heading is None:
        raise ParseError(
            "Could not find '<h4>Time Report Summary</h4>' section on the "
            f"lobbyist page (lobbyist_id={lobbyist_id}). The portal DOM may "
            "have changed, or the page is a soft-404 stub (compare with "
            "lobbyist 12717 Neumann-Ortiz on the 2026-05-26 snapshot)."
        )

    person = _extract_person(soup, lobbyist_id)
    filings = _extract_time_report_filings(heading, person, lobbyist_id)
    return person, filings


# ---------------------------------------------------------------------------
# Person
# ---------------------------------------------------------------------------


def _extract_person(soup: BeautifulSoup, lobbyist_id: int) -> Person:
    h2 = soup.find("h2", class_="display-4")
    if h2 is None:
        raise ParseError(
            "Could not find '<h2 class=\"display-4\">' on the lobbyist page "
            f"(lobbyist_id={lobbyist_id}). The portal DOM may have changed."
        )
    name = h2.get_text(strip=True)
    if not name:
        raise ParseError(
            f"Empty '<h2 class=\"display-4\">' on the lobbyist page "
            f"(lobbyist_id={lobbyist_id}). Unlike the principal side, no "
            "known privacy-redaction class exists for lobbyists; an empty "
            "name indicates a portal-shape change."
        )

    return Person(
        id=f"WI-lobbyist-{lobbyist_id}",
        name=name,
        source_state="WI",
        contact_details=_extract_contact_details(soup),
    )


def _extract_contact_details(soup: BeautifulSoup) -> list[ContactDetail]:
    person_info = soup.find("div", class_="person-info")
    if person_info is None:
        return []

    details: list[ContactDetail] = []
    phone = _extract_phone(person_info)
    if phone:
        details.append(ContactDetail(type="phone", value=phone))
    email = _extract_email(person_info)
    if email:
        details.append(ContactDetail(type="email", value=email))
    address = _extract_address(person_info)
    if address:
        details.append(ContactDetail(type="address", value=address))
    return details


def _extract_phone(person_info: Tag) -> str | None:
    phone_icon = person_info.find("i", class_="fa-phone")
    if phone_icon is None:
        return None
    sibling = phone_icon.next_sibling
    while sibling is not None and isinstance(sibling, NavigableString) and not str(sibling).strip():
        sibling = sibling.next_sibling
    if isinstance(sibling, NavigableString):
        return str(sibling).strip()
    return None


def _extract_email(person_info: Tag) -> str | None:
    mailto = person_info.find("a", href=lambda h: h is not None and h.startswith("mailto:"))
    if mailto is None:
        return None
    return mailto["href"][len("mailto:"):]


def _extract_address(person_info: Tag) -> str | None:
    """Multi-line postal address: the loose text + ``<br/>`` nodes sitting
    inside the address column of the lobbyist's person-info card (e.g.,
    ``"1 S. Pinckney Street, Suite 318\\nMadison, WI 53703"``).

    The lobbyist-side person-info card lays out:

    .. code-block:: html

        <div class="person-info">
          <div class="font-weight-bold">{name}</div>
          <div>{firm name}</div>           <!-- not part of the address -->
          <div class="row">
            <div class="col-lg-6">          <!-- address column -->
              {street}<br/>
              {city, state, zip}<br/>
            </div>
            <div class="col-lg-6">          <!-- contact column -->
              <i class="fa fa-phone"></i> {phone}<br/>
              <a href="mailto:..."><i class="fa fa-envelope"></i> {email}</a><br/>
              ...
            </div>
          </div>
        </div>

    The address column is the ``col-lg-6`` that contains no ``<i>`` icon
    children. We target it directly rather than walking every descendant
    of person-info (which would pull in the firm-name div and the icon-
    sibling NavigableStrings that hold phone/email/website text).
    """
    # Find the col-lg-6 div(s) that hold the address (no icon prefixes —
    # those mark the contact column).
    address_cols = [
        div
        for div in person_info.find_all("div", class_="col-lg-6")
        if div.find("i") is None
    ]
    if not address_cols:
        return None
    parts: list[str] = []
    for col in address_cols:
        for node in col.children:
            if not isinstance(node, NavigableString):
                continue
            text = str(node).strip()
            if text:
                parts.append(text)
    if not parts:
        return None
    return "\n".join(parts)


# ---------------------------------------------------------------------------
# LobbyingFiling — Time Report Summary
# ---------------------------------------------------------------------------


def _extract_time_report_filings(
    heading: Tag, person: Person, lobbyist_id: int
) -> list[LobbyingFiling]:
    table = heading.find_next("table")
    if table is None:
        raise ParseError(
            f"Found '<h4>Time Report Summary</h4>' heading but no following "
            f"<table> (lobbyist_id={lobbyist_id})."
        )
    head_row = table.find("thead")
    body = table.find("tbody")
    if head_row is None or body is None:
        raise ParseError(
            "Time Report Summary table missing thead or tbody "
            f"(lobbyist_id={lobbyist_id})."
        )

    headers = head_row.find_all("th")
    # First <th> is the row-label column ("Category"); remaining headers
    # are the four period columns.
    period_headers = headers[1:]
    period_periods: list[tuple[date, date] | None] = []
    for th in period_headers:
        label = th.get_text(strip=True)
        period_periods.append(_parse_period_header(label))

    rows = body.find_all("tr")
    by_label: dict[str, list[Tag]] = {}
    for row in rows:
        cells = row.find_all("td")
        if not cells:
            continue
        row_label = cells[0].get_text(strip=True)
        by_label[row_label] = cells[1:]  # match period_headers offset

    comm_cells = by_label.get(_TRS_LABEL_COMMUNICATION, [])
    other_cells = by_label.get(_TRS_LABEL_OTHER, [])

    extracted_at = datetime.now(timezone.utc)
    source_url = _SOURCE_URL_TEMPLATE.format(lobbyist_id=lobbyist_id)

    filings: list[LobbyingFiling] = []
    for idx, period in enumerate(period_periods):
        if period is None:
            # Unrecognised header — skip rather than crash the page.
            continue
        start, end = period
        hrs_comm = _safe_hours(_cell_value(comm_cells, idx))
        hrs_other = _safe_hours(_cell_value(other_cells, idx))

        half = "H1" if start.month == 1 else "H2"
        filing_id = f"WI-lobbyist-{lobbyist_id}-activity-{start.year}-{half}"
        filings.append(
            LobbyingFiling(
                id=filing_id,
                state="WI",
                filing_type="activity_report",
                filer_person=person,
                filer_role="lobbyist",
                reporting_period_start=start,
                reporting_period_end=end,
                total_hours_communicating=hrs_comm,
                total_hours_other=hrs_other,
                provenance=Provenance(
                    source_url=source_url,
                    extracted_at=extracted_at,
                    extraction_method="direct_copy",
                ),
            )
        )

    return filings


def _cell_value(cells: list[Tag], idx: int) -> str:
    if idx >= len(cells):
        return ""
    cell = cells[idx]
    label_span = cell.find("span", class_="table-responsive-stack-thead")
    if label_span is not None:
        label_span.extract()
    return cell.get_text(strip=True)


def _parse_period_header(label: str) -> tuple[date, date] | None:
    match = _PERIOD_HEADER_RE.match(label)
    if match is None:
        return None
    start_year = int(match.group("start_year"))
    end_year = int(match.group("end_year"))
    if match.group("start_month") == "January":
        return date(start_year, 1, 1), date(end_year, 6, 30)
    # Only other allowed start month per the regex is July.
    return date(start_year, 7, 1), date(end_year, 12, 31)


def _safe_hours(text: str) -> float | None:
    """Parse ``X.XX`` / ``0`` / ``0.00`` into a float. Empty → None.

    Zero is a real value: in-progress biennium halves file with explicit
    ``0`` on lobbyist pages."""
    text = text.strip().replace(",", "")
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return None
