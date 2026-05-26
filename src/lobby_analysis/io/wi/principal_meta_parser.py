"""Parse the non-edge sections of a lobbying.wi.gov principal-info page
into structured Tier-2 records.

Companion to ``principal_parser.parse_principal_authorizations`` (the
authorization-edge parser at the bottom of the same page). This module
parses everything ELSE on a principal-information page: the Organization
metadata block (name + contact card), the free-text Business-Or-Interest
/ Lobbying-Interests / CEO-Name strongs, the Total Lobbying Effort table
(per-semester $ + hours totals), and the bill-itemized Percent Allocation
of Lobbying Effort cross-tab.

Public surface
==============

``REDACTED_PRINCIPAL_IDS``
    ``frozenset[int]`` of principal IDs whose ``<h2 class="display-4">``
    is suppressed under the WI Ethics Commission's <$500/yr "low-spend
    pledge" privacy exemption (verified at 11530, 13137 on the 2026-05-26
    snapshot). An empty ``<h2>`` on any OTHER principal raises
    ``ParseError`` — a portal-shape change rather than a known data class
    deserves loud surfacing.

``ParseError``
    Raised when the page does not match the expected Tier-2 shape and the
    principal isn't a known-redacted whitelist entry. The lobbyist-side
    parser at ``authorization_parser`` sets this loud-fail-don't-silently-
    empty-out precedent.

``parse_principal_meta(html, principal_id)``
    Returns a four-element tuple::

        (Organization, extras_dict, list[LobbyingFiling], list[item_dict])

    The contract was locked with Dan in
    ``docs/active/wi-disclosure-explore/convos/20260526_wi_tier_2_parser_implementation.md``:

    1. ``Organization`` — typed v1.1 + ``source_state="WI"`` +
       ``contact_details``. Redacted principals get
       ``name=f"[redacted principal {id}]"`` so downstream consumers can
       still join on principal_id.

    2. ``extras`` — dict with keys ``ceo_name``,
       ``business_or_interest``, ``lobbying_interests_prose``. All keys
       ALWAYS present; values are ``None`` when the corresponding
       ``<strong>X:</strong>`` is absent from the page (redacted
       principals; also partial-disclosure principals like the low-spend-
       exempt WCTA which has Business + Lobbying-Interests but no CEO
       Name). This is the v1.1 ``Organization`` model's free-text shim;
       long-term v1.3 lifts the dict into typed Organization fields.

    3. ``list[LobbyingFiling]`` — one per non-summary period column in
       the "Total Lobbying Effort" table. ``filer_role="client"``,
       ``filing_type="expenditure_report"``, ``filer_organization=org``,
       populated ``total_expenditure`` + ``total_hours_communicating`` +
       ``total_hours_other`` (v1.2 fields) + ``provenance``. Zero-spend
       reports (low-spend exempt: $0 / 0.00 / 0.00) ARE emitted — zero
       is real data, not absence.

    4. ``list[dict]`` — per-(bucket, item, period) percent rows from the
       "Percent Allocation of Lobbying Effort" section. Per-item, not
       bucket-totaled (Dan's call: "ship the data shape first, design the
       schema once we've seen it"). Keys:
       ``principal_id``, ``bucket``, ``item_id``, ``item_name``,
       ``item_description``, ``period_label``, ``percent``. Empty period
       cells (in-progress biennium halves on snapshot date) are SKIPPED,
       not emitted with ``percent=None``. Long-term v1.3 lifts this into
       typed ``LobbyingEffortAllocation`` sub-entity records.

Same-text-different-section gotchas
====================================

- ``<h4 class="card-title">Legislative Bills/Resolutions</h4>`` appears
  TWICE on populated pages: once inside ``<h3>Lobbying Interests</h3>``
  (the bill-by-bill registration list, no %s), once inside
  ``<h3>Percent Allocation of Lobbying Effort</h3>`` (the per-bill
  % cross-tab). The parser scopes the bucket-walk to the Percent
  Allocation section's ``<div class="row">`` subtree, so the
  Lobbying-Interests h4s never match.

- Panel IDs have different prefixes per section: ``panel-bill-{id}``,
  ``panel-topic-{id}``, ``panel-rule-{id}`` etc. under Lobbying
  Interests; ``panel-billeffort-{id}``,
  ``panel-budgetbillsubjecteffort-{id}``, ``panel-administrativeruleeffort-{id}``
  etc. under Percent Allocation. The integer suffix IS the item ID in
  both sections; the prefix varies by bucket but isn't needed for the
  Tier-2 contract.
"""

from __future__ import annotations

import re
from datetime import date, datetime, timezone

from bs4 import BeautifulSoup, NavigableString, Tag

from lobby_analysis.models import (
    ContactDetail,
    LobbyingFiling,
    Organization,
)
from lobby_analysis.models.provenance import Provenance


class ParseError(ValueError):
    """Raised when the principal-page HTML does not contain the expected
    Tier-2 sections in the expected shape and the page is not a known
    privacy-redacted-low-spend-pledge exemption.

    Surfacing this loudly is intentional: a silent placeholder on a
    page-shape change would let an entire Tier-2 run produce structurally
    broken output without anyone noticing. The lobbyist-side
    ``authorization_parser.ParseError`` is the precedent.
    """


REDACTED_PRINCIPAL_IDS: frozenset[int] = frozenset({11530, 13137})


_BUCKET_HEADERS: tuple[str, ...] = (
    "Legislative Bills/Resolutions",
    "Budget Bill Subjects",
    "Administrative Rulemaking Proceedings",
    "Topics Not Yet Assigned A Bill Or Rule Number",
    "Minor Efforts",
    "Other Matters",
)


_SOURCE_URL_TEMPLATE = (
    "https://lobbying.wi.gov/Who/PrincipalInformation/2025REG/Information/"
    "{principal_id}"
)

# Total Lobbying Effort + Percent Allocation table header form:
#   "2025 January - June" / "2025 July - December" / "2026 January - June" / "2026 July - December"
_PERIOD_HEADER_RE = re.compile(
    r"^(?P<year>\d{4})\s+(?P<start_month>January|July)\s*-\s*(?P<end_month>June|December)$"
)

# Panel HTML IDs in the Percent Allocation section: panel-{prefix}-{int_id}.
_PANEL_ID_RE = re.compile(r"^panel-[A-Za-z]+-(?P<item_id>\d+)$")

# Labels for the three Total Lobbying Effort table rows.
_TLE_LABEL_EXPENDITURE = "Total Lobbying Expenditures"
_TLE_LABEL_HRS_COMM = "Total Hours Communicating"
_TLE_LABEL_HRS_OTHER = "Total Hours Other"


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------


def parse_principal_meta(
    html: str, principal_id: int
) -> tuple[Organization, dict, list[LobbyingFiling], list[dict]]:
    """Parse a lobbying.wi.gov principal-information page into Tier-2 records.

    See module docstring for the four-element tuple contract.
    """
    soup = BeautifulSoup(html, "lxml")

    org = _extract_organization(soup, principal_id)
    extras = _extract_principal_extras(soup)
    filings = _extract_total_lobbying_effort_filings(soup, org, principal_id)
    items = _extract_percent_allocation_items(soup, principal_id)

    return org, extras, filings, items


# ---------------------------------------------------------------------------
# Organization
# ---------------------------------------------------------------------------


def _extract_organization(soup: BeautifulSoup, principal_id: int) -> Organization:
    h2 = soup.find("h2", class_="display-4")
    if h2 is None:
        raise ParseError(
            "Could not find '<h2 class=\"display-4\">' on the principal page "
            f"(principal_id={principal_id}). The portal DOM may have changed."
        )

    name = h2.get_text(strip=True)
    if not name:
        if principal_id in REDACTED_PRINCIPAL_IDS:
            name = f"[redacted principal {principal_id}]"
        else:
            raise ParseError(
                f"Empty <h2 class=\"display-4\"> on a non-redacted principal "
                f"(principal_id={principal_id}). Whitelist the id in "
                "REDACTED_PRINCIPAL_IDS if this is a genuine privacy-redacted "
                "low-spend-pledge page; otherwise the portal DOM has changed."
            )

    return Organization(
        id=f"WI-principal-{principal_id}",
        name=name,
        source_state="WI",
        contact_details=_extract_contact_details(soup),
    )


def _extract_contact_details(soup: BeautifulSoup) -> list[ContactDetail]:
    """Pull the address / phone / email / website rows from the Contact card.

    Returns an empty list when the page has no Contact card (e.g., redacted
    principals).
    """
    label = soup.find("strong", string=lambda s: s is not None and s.strip() == "Contact")
    if label is None:
        return []
    person_info = label.find_next("div", class_="person-info")
    if person_info is None:
        return []

    details: list[ContactDetail] = []
    address = _extract_address(person_info)
    if address:
        details.append(ContactDetail(type="address", value=address))
    phone = _extract_phone(person_info)
    if phone:
        details.append(ContactDetail(type="phone", value=phone))
    email = _extract_email(person_info)
    if email:
        details.append(ContactDetail(type="email", value=email))
    website = _extract_website(person_info)
    if website:
        details.append(ContactDetail(type="website", value=website))
    return details


def _extract_address(person_info: Tag) -> str | None:
    """Multi-line postal address; everything in person-info that isn't the
    person name, phone, email, or website."""
    parts: list[str] = []
    for child in person_info.children:
        if isinstance(child, NavigableString):
            text = str(child).strip()
            if text:
                parts.append(text)
            continue
        if not isinstance(child, Tag):
            continue
        if child.name in ("strong", "br"):
            # The person name <strong> isn't part of the address; <br/> is a
            # separator only.
            continue
        if child.name == "i":
            # Phone is rendered as `<i class="fa fa-phone"></i> 608-...` —
            # the text directly follows the <i> as a NavigableString, so we
            # treat that NavigableString as phone (handled in
            # _extract_phone) and skip the <i> here.
            continue
        if child.name == "a":
            # email / website anchors are handled separately
            continue
    if not parts:
        return None
    return "\n".join(parts)


def _extract_phone(person_info: Tag) -> str | None:
    phone_icon = person_info.find("i", class_="fa-phone")
    if phone_icon is None:
        return None
    # The phone number is the NavigableString immediately following the icon.
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


def _extract_website(person_info: Tag) -> str | None:
    site = person_info.find(
        "a",
        href=lambda h: h is not None and (h.startswith("http://") or h.startswith("https://")),
    )
    if site is None:
        return None
    return site["href"]


# ---------------------------------------------------------------------------
# Extras dict (CEO + Business + Lobbying-Interests prose)
# ---------------------------------------------------------------------------


def _extract_principal_extras(soup: BeautifulSoup) -> dict[str, str | None]:
    """Pull the three free-text strongs into the side-channel dict.

    All three keys are ALWAYS present; values are None when the strong is
    absent from the page (redacted; partial-disclosure low-spend exempt).
    """
    return {
        "ceo_name": _extract_strong_value(soup, "CEO Name:"),
        "business_or_interest": _extract_strong_value(soup, "Business Or Interest:"),
        "lobbying_interests_prose": _extract_strong_value(soup, "Lobbying Interests:"),
    }


def _extract_strong_value(soup: BeautifulSoup, label: str) -> str | None:
    """Find ``<strong>{label}</strong>`` and return the text that follows it
    on the page, stripped of surrounding whitespace.

    Portal markup is::

        <strong>Business Or Interest:</strong><br />
        Dairy community<br /><br />

    BeautifulSoup parses the value as a NavigableString sibling of the
    ``<strong>`` (between two ``<br />`` self-closing tags). We walk forward
    from the strong, skipping ``<br />`` tags, and return the first non-empty
    text node we hit.
    """
    strong = soup.find("strong", string=lambda s: s is not None and s.strip() == label)
    if strong is None:
        return None
    for sibling in strong.next_siblings:
        if isinstance(sibling, NavigableString):
            text = str(sibling).strip()
            if text:
                return text
            continue
        if isinstance(sibling, Tag):
            if sibling.name == "br":
                continue
            # Any other tag (next <strong>, etc.) terminates the value.
            return None
    return None


# ---------------------------------------------------------------------------
# LobbyingFiling — Total Lobbying Effort
# ---------------------------------------------------------------------------


def _extract_total_lobbying_effort_filings(
    soup: BeautifulSoup, org: Organization, principal_id: int
) -> list[LobbyingFiling]:
    heading = soup.find(
        "h3", string=lambda s: s is not None and s.strip() == "Total Lobbying Effort"
    )
    if heading is None:
        # Pages with no "Total Lobbying Effort" section have nothing to
        # emit. Not a ParseError — some classes of principal page may
        # legitimately lack the section (none observed on the 2026-05-26
        # snapshot, but the parser shouldn't presume).
        return []

    table = heading.find_next("table")
    if table is None:
        return []
    head_row = table.find("thead")
    body = table.find("tbody")
    if head_row is None or body is None:
        return []

    headers = head_row.find_all("th")
    if not headers:
        return []
    # First <th> is the row-label column (empty / aria-label only).
    # Remaining headers are the period columns plus a final "Total" summary.
    period_headers = headers[1:]
    period_specs: list[tuple[int, str, date, date] | None] = []
    for idx, th in enumerate(period_headers):
        label = th.get_text(separator=" ", strip=True)
        period = _parse_period_header(label)
        if period is None:
            # Either the Total summary column or an unrecognized header.
            period_specs.append(None)
            continue
        start, end = period
        period_specs.append((idx, label, start, end))

    rows = body.find_all("tr")
    by_label: dict[str, list[Tag]] = {}
    for row in rows:
        cells = row.find_all("td")
        if not cells:
            continue
        row_label = cells[0].get_text(strip=True)
        by_label[row_label] = cells[1:]  # match the period_headers offset

    expenditure_cells = by_label.get(_TLE_LABEL_EXPENDITURE, [])
    hrs_comm_cells = by_label.get(_TLE_LABEL_HRS_COMM, [])
    hrs_other_cells = by_label.get(_TLE_LABEL_HRS_OTHER, [])

    filings: list[LobbyingFiling] = []
    for spec_idx, spec in enumerate(period_specs):
        if spec is None:
            continue
        _, _label, start, end = spec
        expenditure = _safe_dollar(_cell_value(expenditure_cells, spec_idx))
        hrs_comm = _safe_hours(_cell_value(hrs_comm_cells, spec_idx))
        hrs_other = _safe_hours(_cell_value(hrs_other_cells, spec_idx))

        half = "H1" if start.month == 1 else "H2"
        filing_id = f"WI-principal-{principal_id}-expenditure-{start.year}-{half}"
        filings.append(
            LobbyingFiling(
                id=filing_id,
                state="WI",
                filing_type="expenditure_report",
                filer_organization=org,
                filer_role="client",
                reporting_period_start=start,
                reporting_period_end=end,
                total_expenditure=expenditure,
                total_hours_communicating=hrs_comm,
                total_hours_other=hrs_other,
                provenance=Provenance(
                    source_url=_SOURCE_URL_TEMPLATE.format(principal_id=principal_id),
                    extracted_at=datetime.now(timezone.utc),
                    extraction_method="direct_copy",
                ),
            )
        )

    return filings


def _cell_value(cells: list[Tag], idx: int) -> str:
    if idx >= len(cells):
        return ""
    cell = cells[idx]
    # Strip the responsive-table label span (mirrors authorization_parser's
    # `_cell_value_text`).
    label_span = cell.find("span", class_="table-responsive-stack-thead")
    if label_span is not None:
        label_span = label_span.extract()  # noqa: F841 — discard
    return cell.get_text(strip=True)


def _parse_period_header(label: str) -> tuple[date, date] | None:
    match = _PERIOD_HEADER_RE.match(label)
    if match is None:
        return None
    year = int(match.group("year"))
    if match.group("start_month") == "January":
        return date(year, 1, 1), date(year, 6, 30)
    # Only other allowed start_month in the regex is July.
    return date(year, 7, 1), date(year, 12, 31)


def _safe_dollar(text: str) -> float | None:
    """Parse ``$X.XX`` / ``$X,XXX.XX`` into a float. Empty/missing → None.

    Zero (``$0.00``) is a real value, not None — low-spend-exempt principals
    file with literal zeros."""
    text = text.strip()
    if not text:
        return None
    cleaned = text.replace("$", "").replace(",", "").strip()
    if not cleaned:
        return None
    try:
        return float(cleaned)
    except ValueError:
        return None


def _safe_hours(text: str) -> float | None:
    """Parse ``X.XX`` / ``0`` / ``0.00`` into a float. Empty/missing → None."""
    text = text.strip().replace(",", "")
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return None


# ---------------------------------------------------------------------------
# Percent Allocation items
# ---------------------------------------------------------------------------


def _extract_percent_allocation_items(
    soup: BeautifulSoup, principal_id: int
) -> list[dict]:
    heading = soup.find(
        "h3",
        string=lambda s: s is not None
        and s.strip() == "Percent Allocation of Lobbying Effort",
    )
    if heading is None:
        return []
    section_row = heading.find_parent("div", class_="row")
    if section_row is None:
        return []

    items: list[dict] = []
    for panel in section_row.find_all("div", id=_PANEL_ID_RE):
        match = _PANEL_ID_RE.match(panel["id"])
        if match is None:
            continue
        item_id = match.group("item_id")

        bucket = _find_bucket_for_panel(panel, section_row)
        if bucket is None:
            continue

        card_title = panel.find("div", class_="card-title")
        if card_title is None:
            continue
        item_name = _extract_item_name(card_title)

        collapse_panel = panel.find("div", class_="component-collapse-panel")
        if collapse_panel is None:
            continue
        description = _extract_item_description(collapse_panel)
        table = collapse_panel.find("table")
        if table is None:
            continue

        head = table.find("thead")
        body = table.find("tbody")
        if head is None or body is None:
            continue

        period_labels = [th.get_text(separator=" ", strip=True) for th in head.find_all("th")]
        data_row = body.find("tr")
        if data_row is None:
            continue
        data_cells = data_row.find_all("td")

        for col_idx, label in enumerate(period_labels):
            if label == "Total":
                continue
            if _parse_period_header(label) is None:
                # Skip any header that isn't a recognised period column —
                # the percent-allocation tables share the same period
                # vocabulary as Total Lobbying Effort but with the full
                # 4-half biennium grid.
                continue
            if col_idx >= len(data_cells):
                continue
            value = _cell_value(data_cells, col_idx)
            if not value:
                # Empty / whitespace cell — in-progress biennium half on
                # the snapshot date. Skip (don't emit percent=None).
                continue
            items.append(
                {
                    "principal_id": principal_id,
                    "bucket": bucket,
                    "item_id": item_id,
                    "item_name": item_name,
                    "item_description": description,
                    "period_label": label,
                    "percent": value,
                }
            )

    return items


def _find_bucket_for_panel(panel: Tag, section_row: Tag) -> str | None:
    """Walk backward in document order from the panel to find the closest
    preceding ``<h4 class="card-title">`` whose text matches one of the 6
    known bucket headers, stopping if we leave the Percent Allocation
    section row.
    """
    for h4 in panel.find_all_previous("h4", class_="card-title"):
        if section_row not in h4.parents:
            return None
        text = h4.get_text(strip=True)
        if text in _BUCKET_HEADERS:
            return text
    return None


def _extract_item_name(card_title: Tag) -> str:
    """The first non-collapse-toggle ``<a>`` in a panel's card-title carries
    the item name (bill / topic / rule label). The second ``<a>`` is the
    collapse-toggle (``href`` starts with ``#``).
    """
    link = card_title.find(
        "a", href=lambda h: h is not None and not h.startswith("#")
    )
    if link is None:
        return ""
    return link.get_text(strip=True)


def _extract_item_description(collapse_panel: Tag) -> str | None:
    """The optional ``Relating to: ...`` text that sits between the collapse-
    panel open and the per-period table. None when the panel jumps straight
    into the table (e.g., topics-not-yet-assigned items)."""
    parts: list[str] = []
    for child in collapse_panel.children:
        if isinstance(child, Tag) and child.name == "table":
            break
        if isinstance(child, NavigableString):
            text = str(child).strip()
            if text:
                parts.append(text)
        elif isinstance(child, Tag):
            text = child.get_text(strip=True)
            if text:
                parts.append(text)
    if not parts:
        return None
    return " ".join(parts)
