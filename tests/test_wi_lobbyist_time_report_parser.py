"""TDD tests for the WI Tier-2 lobbyist time-report parser.

Phase 3 of plans/wi_tier_2_parser.md. These tests are expected to fail
until ``src/lobby_analysis/io/wi/lobbyist_time_report_parser.py`` exists
and exposes::

    parse_lobbyist_time_reports(html, lobbyist_id)
        -> tuple[Person, list[LobbyingFiling]]

Tier-2 contract for the lobbyist side mirrors the principal side but
with two important shape differences:

  - The Time Report Summary header is ``<h4>``, not ``<h3>``. The
    parser keys on ``<h4>Time Report Summary</h4>``.
  - In-progress 2026 columns show explicit ``0`` (not empty cells).
    Distinct from the principal-side Total Lobbying Effort table,
    which omits in-progress columns entirely. The parser emits 4
    filings per lobbyist page (one per period in the biennium),
    including zero-hours rows — zero is real data.

Fixtures exercised:
- lobbyist_11052_populated.html — Bryan Brooks (top lobbyist, 41
  principals). Communication = [102.50, 195.00, 0, 0]; Other =
  [566.00, 673.90, 0, 0]. The 2-populated/2-zero pattern is the
  realistic norm: 420 of 770 lobbyists on the 2026-05-26 snapshot match
  this shape.
- lobbyist_11042.html — Shawn Pfaff (original authorization-parser
  fixture). Communication = [125.00, 74.00, 0, 0]; Other = [259.50,
  276.00, 0, 0]. Smaller cross-check.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from lobby_analysis.io.wi.lobbyist_time_report_parser import (  # noqa: F401 — drives RED
    ParseError,
    parse_lobbyist_time_reports,
)
from lobby_analysis.models import LobbyingFiling, Person  # noqa: F401 — used in assertions

FIXTURES = Path(__file__).parent / "fixtures" / "wi"


def _load(name: str) -> str:
    return (FIXTURES / name).read_text()


# ---------------------------------------------------------------------------
# Person extraction
# ---------------------------------------------------------------------------


class TestPersonExtraction:
    """The Person carries lobbyist metadata typed under the v1.1 schema.
    Name comes from ``<h2 class="display-4">``; source_state is "WI"; id
    follows the locked ``WI-lobbyist-{id}`` convention."""

    def test_brooks_name_and_id(self):
        person, _ = parse_lobbyist_time_reports(
            _load("lobbyist_11052_populated.html"), 11052
        )
        assert isinstance(person, Person)
        assert person.id == "WI-lobbyist-11052"
        assert person.name == "Bryan Brooks"
        assert person.source_state == "WI"

    def test_pfaff_name_and_id(self):
        person, _ = parse_lobbyist_time_reports(_load("lobbyist_11042.html"), 11042)
        assert person.id == "WI-lobbyist-11042"
        assert person.name == "Shawn Pfaff"


# ---------------------------------------------------------------------------
# Person contact details
# ---------------------------------------------------------------------------


class TestPersonContactDetails:
    """The contact card sits inside the lobbyist-info section at the top of
    the page (in ``.person-info``). Email + phone are the most reliable
    fields; address is multi-line and harder to validate exactly, so the
    tests focus on the structured fields."""

    def test_brooks_email(self):
        person, _ = parse_lobbyist_time_reports(
            _load("lobbyist_11052_populated.html"), 11052
        )
        emails = [c.value for c in person.contact_details if c.type == "email"]
        assert "bbrooks@paladincg.com" in emails

    def test_brooks_phone(self):
        person, _ = parse_lobbyist_time_reports(
            _load("lobbyist_11052_populated.html"), 11052
        )
        phones = [c.value for c in person.contact_details if c.type == "phone"]
        assert "(608) 467-7933" in phones

    def test_pfaff_email(self):
        person, _ = parse_lobbyist_time_reports(_load("lobbyist_11042.html"), 11042)
        emails = [c.value for c in person.contact_details if c.type == "email"]
        assert "shawn@pfaffpublicaffairs.com" in emails

    def test_brooks_address_is_only_street_and_city_state_zip(self):
        """The address ContactDetail must contain ONLY the postal address
        (street + city/state/zip), NOT (a) the firm-name ``<div>`` that
        precedes the address row, or (b) the phone digits that follow the
        ``<i class="fa-phone">`` icon as a NavigableString sibling. Both
        currently leak in on the Brooks fixture; both belong in their own
        typed slots (the firm name has no slot at all on v1.1 ContactDetail
        and should NOT be invented as part of the address)."""
        person, _ = parse_lobbyist_time_reports(
            _load("lobbyist_11052_populated.html"), 11052
        )
        addresses = [c.value for c in person.contact_details if c.type == "address"]
        assert addresses == [
            "1 S. Pinckney Street, Suite 318\nMadison, WI 53703"
        ]

    def test_pfaff_address_is_only_street_and_city_state_zip(self):
        """Pfaff 11042: self-employed lobbyist. Address column carries the
        street + city/state/zip; the 'Self-Employed Lobbyist - No Firm or
        Org' string belongs to the firm-name slot, not the address."""
        person, _ = parse_lobbyist_time_reports(_load("lobbyist_11042.html"), 11042)
        addresses = [c.value for c in person.contact_details if c.type == "address"]
        assert addresses == ["5843 Schumann Drive\nFitchburg, WI 53711"]


# ---------------------------------------------------------------------------
# LobbyingFiling — Time Report Summary table
# ---------------------------------------------------------------------------


class TestTimeReportSummaryFilings:
    """The ``<h4>Time Report Summary</h4>`` table has 2 rows (Communication
    + Other) × 4 period columns. The parser emits one LobbyingFiling per
    period (4 total per lobbyist), with ``filer_role="lobbyist"``,
    ``filing_type="activity_report"``, ``filer_person=the lobbyist's
    Person``, populated ``total_hours_communicating`` and
    ``total_hours_other``, and a populated Provenance with source_url +
    extracted_at."""

    def test_brooks_emits_four_period_filings(self):
        """Brooks's table has all 4 columns populated (with zeros for
        in-progress 2026); 4 filings emitted."""
        _, filings = parse_lobbyist_time_reports(
            _load("lobbyist_11052_populated.html"), 11052
        )
        assert len(filings) == 4

    def test_brooks_p1_amounts(self):
        """2025 Jan-Jun (P1): 102.50 hrs communicating / 566.00 hrs other."""
        _, filings = parse_lobbyist_time_reports(
            _load("lobbyist_11052_populated.html"), 11052
        )
        p1 = next(
            f for f in filings
            if f.reporting_period_start
            and f.reporting_period_start.year == 2025
            and f.reporting_period_start.month == 1
        )
        assert p1.total_hours_communicating == 102.50
        assert p1.total_hours_other == 566.00

    def test_brooks_p2_amounts(self):
        """2025 Jul-Dec (P2): 195.00 hrs communicating / 673.90 hrs other."""
        _, filings = parse_lobbyist_time_reports(
            _load("lobbyist_11052_populated.html"), 11052
        )
        p2 = next(
            f for f in filings
            if f.reporting_period_start
            and f.reporting_period_start.year == 2025
            and f.reporting_period_start.month == 7
        )
        assert p2.total_hours_communicating == 195.00
        assert p2.total_hours_other == 673.90

    def test_brooks_in_progress_periods_emit_zero_hour_filings(self):
        """In-progress 2026 periods file with explicit ``0`` on lobbyist
        pages (NOT empty cells, as on the principal-side Total Lobbying
        Effort). The parser MUST emit filings for both — zero hours is a
        real value, not absence."""
        _, filings = parse_lobbyist_time_reports(
            _load("lobbyist_11052_populated.html"), 11052
        )
        p3 = next(
            f for f in filings
            if f.reporting_period_start
            and f.reporting_period_start.year == 2026
            and f.reporting_period_start.month == 1
        )
        p4 = next(
            f for f in filings
            if f.reporting_period_start
            and f.reporting_period_start.year == 2026
            and f.reporting_period_start.month == 7
        )
        assert p3.total_hours_communicating == 0.0
        assert p3.total_hours_other == 0.0
        # Distinct from None — the field is set with the real zero value.
        assert p3.total_hours_communicating is not None
        assert p4.total_hours_communicating == 0.0
        assert p4.total_hours_other == 0.0

    def test_filing_filer_role_and_person(self):
        """``filer_role="lobbyist"``, ``filer_person`` set (not
        ``filer_organization``)."""
        _, filings = parse_lobbyist_time_reports(
            _load("lobbyist_11052_populated.html"), 11052
        )
        f = filings[0]
        assert f.filer_role == "lobbyist"
        assert f.filer_person is not None
        assert f.filer_person.id == "WI-lobbyist-11052"
        assert f.filer_organization is None

    def test_filing_provenance_populated(self):
        """Per Dan's resolution of plan Q1 (principal-side), provenance is
        also populated on lobbyist-side filings. source_url is the
        lobbyist-info detail page; extracted_at is the parse-time
        timestamp."""
        _, filings = parse_lobbyist_time_reports(
            _load("lobbyist_11052_populated.html"), 11052
        )
        f = filings[0]
        assert f.provenance is not None
        assert f.provenance.source_url is not None
        assert "LobbyistInformation" in f.provenance.source_url
        assert "11052" in f.provenance.source_url
        assert f.provenance.extracted_at is not None

    def test_pfaff_p1_amounts(self):
        """Cross-check on the existing authorization-parser fixture.
        Pfaff 11042 P1: 125.00 hrs communicating / 259.50 hrs other."""
        _, filings = parse_lobbyist_time_reports(_load("lobbyist_11042.html"), 11042)
        p1 = next(
            f for f in filings
            if f.reporting_period_start
            and f.reporting_period_start.year == 2025
            and f.reporting_period_start.month == 1
        )
        assert p1.total_hours_communicating == 125.00
        assert p1.total_hours_other == 259.50

    def test_pfaff_emits_four_period_filings(self):
        """Pfaff also matches the 4-period (2-populated, 2-zero) norm."""
        _, filings = parse_lobbyist_time_reports(_load("lobbyist_11042.html"), 11042)
        assert len(filings) == 4


# ---------------------------------------------------------------------------
# Missing-section behavior (soft-404 case)
# ---------------------------------------------------------------------------


class TestMissingTimeReportSummary:
    """Loud-fail discipline (mirroring authorization_parser): a lobbyist
    page that lacks the expected Time Report Summary section is not
    silently treated as zero filings — it raises ParseError. Catches
    soft-404 stub pages (e.g., lobbyist 12717 Neumann-Ortiz on the
    2026-05-26 snapshot) before they slip through a materializer run."""

    def test_missing_section_raises_parse_error(self):
        html = (
            '<html><body><h2 class="display-4">Stub Lobbyist</h2></body></html>'
        )
        with pytest.raises(ParseError):
            parse_lobbyist_time_reports(html, 99999)
