"""TDD tests for the WI Tier-2 principal-meta parser.

Phase 2 of plans/wi_tier_2_parser.md. These tests are expected to fail
until `src/lobby_analysis/io/wi/principal_meta_parser.py` exists and exposes
`parse_principal_meta(html, principal_id) -> tuple[Organization, dict, list[LobbyingFiling], list[dict]]`.

Two decisions locked with Dan during this implementation session:

  1. The Percent Allocation section is emitted at the **per-item level**
     (not bucket-totaled). Parser returns a list of dicts, one per
     (bucket, item_id, period) row. Long-term this becomes a typed
     `LobbyingEffortAllocation` sub-entity (v1.3) — but ship the data
     shape first, design the schema once we've seen it.

  2. CEO Name + Business Or Interest + Lobbying Interests prose are
     emitted as a **side-channel dict** alongside the Organization
     record. The v1.1 Organization model has no free-text/notes
     catch-all, and a Tier-2 schema bump just for these three optional
     fields isn't worth it. Long-term v1.3 lifts the dict into typed
     Organization fields. Until then, the dict keys are:
       - ceo_name: str | None
       - business_or_interest: str | None
       - lobbying_interests_prose: str | None

Fixtures exercised (under tests/fixtures/wi/):
- principal_11590_populated.html (Dairy Business Association — fully
  populated, all 6 allocation buckets active, $88,568.50 total spend)
- principal_11637_populated.html (Wisconsin Manufacturers & Commerce —
  heavy Lobbying Interests, sparse Percent Allocation, $911,593.49)
- principal_11348.html (Lexia Learning — only Topics-Not-Yet-Assigned
  bucket populated at 100%)
- principal_12997.html (WCTA — low-spend exempt: $0 everywhere, all
  buckets empty, but lobbying-interests prose still parses)
- principal_11530.html (privacy-redacted: empty title/h2; no
  Business-Or-Interest / Lobbying-Interests / CEO strongs)
- principal_10949.html (Apex Clean Energy — canonical ceased principal)
"""

from __future__ import annotations

from pathlib import Path

import pytest

from lobby_analysis.io.wi.principal_meta_parser import (  # noqa: F401 — drives RED
    REDACTED_PRINCIPAL_IDS,
    ParseError,
    parse_principal_meta,
)
from lobby_analysis.models import LobbyingFiling, Organization

FIXTURES = Path(__file__).parent / "fixtures" / "wi"


def _load(name: str) -> str:
    return (FIXTURES / name).read_text()


# ---------------------------------------------------------------------------
# Module-level constants
# ---------------------------------------------------------------------------


class TestRedactedWhitelist:
    """The plan's privacy-redacted whitelist (low-spend pledge entities under
    the WI Ethics Commission's <$500/year exemption) drives a code path that
    accepts empty title/h2 fields. The whitelist is two IDs at this snapshot."""

    def test_whitelist_contains_11530_and_13137(self):
        assert 11530 in REDACTED_PRINCIPAL_IDS
        assert 13137 in REDACTED_PRINCIPAL_IDS

    def test_whitelist_does_not_include_low_spend_exempt_wcta(self):
        """WCTA 12997 is 'low-spend exempt' (different category from
        privacy-redacted) — its page DOES carry name + lobbying-interests
        prose, just with $0 / empty allocation."""
        assert 12997 not in REDACTED_PRINCIPAL_IDS


# ---------------------------------------------------------------------------
# Organization extraction
# ---------------------------------------------------------------------------


class TestOrganizationExtraction:
    """The Organization record carries principal metadata typed under the v1.1
    schema: name, source_state, contact_details. CEO / Business / Lobbying-
    Interests prose flow through a separate side-channel dict (see
    TestPrincipalExtras below)."""

    def test_dairy_business_assoc_name_and_id(self):
        org, _, _, _ = parse_principal_meta(
            _load("principal_11590_populated.html"), 11590
        )
        assert isinstance(org, Organization)
        assert org.id == "WI-principal-11590"
        assert org.name == "Dairy Business Association"
        assert org.source_state == "WI"

    def test_wcta_name_is_the_h2_acronym_not_expanded(self):
        """Principal 12997's h2 is literally 'WCTA' — the parser extracts what
        the portal page shows, NOT the expanded 'Wisconsin County Treasurers
        Association.' The expansion happens in Phase 7's separate doc-drift
        fix, not at parse time. (If the portal ever updates to show the full
        name, this test catches the regression.)"""
        org, _, _, _ = parse_principal_meta(_load("principal_12997.html"), 12997)
        assert org.name == "WCTA"

    def test_lexia_name(self):
        org, _, _, _ = parse_principal_meta(_load("principal_11348.html"), 11348)
        assert org.name == "Lexia Learning"

    def test_redacted_principal_emits_placeholder_name(self):
        """Privacy-redacted principals have empty <title> / <h2>; the parser
        substitutes a placeholder so downstream consumers can still join on
        principal_id."""
        org, _, _, _ = parse_principal_meta(_load("principal_11530.html"), 11530)
        assert org.name == "[redacted principal 11530]"
        assert org.id == "WI-principal-11530"

    def test_missing_name_raises_parse_error_when_not_redacted(self):
        """An empty <h2> on a NON-redacted principal is a portal-shape
        change, not silent data — raise ParseError rather than emit a
        placeholder for an arbitrary principal."""
        # Take the redacted fixture and pass a non-whitelist ID — the parser
        # should refuse to fall through to the placeholder branch.
        html = _load("principal_11530.html")
        with pytest.raises(ParseError):
            parse_principal_meta(html, 99999)


# ---------------------------------------------------------------------------
# Principal extras dict (CEO + business + lobbying-interests prose)
# ---------------------------------------------------------------------------


class TestPrincipalExtras:
    """The second tuple element is a dict carrying free-text fields the v1.1
    Organization model has no home for. Keys (all optional, None when the
    `<strong>X:</strong>` is absent from the page):

      - ceo_name
      - business_or_interest
      - lobbying_interests_prose
    """

    def test_dairy_ceo_name(self):
        _, extras, _, _ = parse_principal_meta(
            _load("principal_11590_populated.html"), 11590
        )
        assert extras["ceo_name"] == "Tim Trotter"

    def test_dairy_business_or_interest(self):
        _, extras, _, _ = parse_principal_meta(
            _load("principal_11590_populated.html"), 11590
        )
        assert extras["business_or_interest"] == "Dairy community"

    def test_dairy_lobbying_interests_prose(self):
        _, extras, _, _ = parse_principal_meta(
            _load("principal_11590_populated.html"), 11590
        )
        prose = extras["lobbying_interests_prose"]
        assert prose is not None
        assert "dairy community to be more successful" in prose

    def test_redacted_extras_all_none(self):
        """Privacy-redacted 11530: the Business-Or-Interest / Lobbying-
        Interests / CEO strongs are suppressed on the page. All three keys
        present in the dict but None-valued."""
        _, extras, _, _ = parse_principal_meta(_load("principal_11530.html"), 11530)
        assert extras["ceo_name"] is None
        assert extras["business_or_interest"] is None
        assert extras["lobbying_interests_prose"] is None


# ---------------------------------------------------------------------------
# Contact details (on Organization)
# ---------------------------------------------------------------------------


class TestOrganizationContactDetails:
    """The Contact card under the principal-info section emits ContactDetail
    rows on the Organization. ContactDetail.type is the v1.1 Literal
    {'address', 'phone', 'email', 'website'}."""

    def test_dairy_email(self):
        """Dairy 11590 contact: Chad L. Zuleger / czuleger@dairyforward.com /
        608-345-6906 / http://www.dairyforward.com."""
        org, _, _, _ = parse_principal_meta(
            _load("principal_11590_populated.html"), 11590
        )
        emails = [c.value for c in org.contact_details if c.type == "email"]
        assert "czuleger@dairyforward.com" in emails

    def test_dairy_phone(self):
        org, _, _, _ = parse_principal_meta(
            _load("principal_11590_populated.html"), 11590
        )
        phones = [c.value for c in org.contact_details if c.type == "phone"]
        assert "608-345-6906" in phones

    def test_dairy_website(self):
        org, _, _, _ = parse_principal_meta(
            _load("principal_11590_populated.html"), 11590
        )
        sites = [c.value for c in org.contact_details if c.type == "website"]
        assert "http://www.dairyforward.com" in sites


# ---------------------------------------------------------------------------
# LobbyingFiling — Total Lobbying Effort table
# ---------------------------------------------------------------------------


class TestTotalLobbyingEffortFilings:
    """The `<h3>Total Lobbying Effort</h3>` table has 3 rows (Expenditures,
    Hours Communicating, Hours Other) × N period columns (Jan-Jun + Jul-Dec
    per completed year + Total summary). The parser emits one LobbyingFiling
    per completed semester, mapping the row × column intersections onto
    LobbyingFiling fields. Records carry filer_role='client',
    filer_organization=the principal's Organization, and a populated
    Provenance with source_url + extracted_at."""

    def test_dairy_emits_two_completed_semester_filings(self):
        """Dairy 11590 has 2025 Jan-Jun + 2025 Jul-Dec data; the Total column
        is summary, not a filing."""
        _, _, filings, _ = parse_principal_meta(
            _load("principal_11590_populated.html"), 11590
        )
        assert len(filings) == 2

    def test_dairy_p1_amounts(self):
        """2025 Jan-Jun (P1): $37,840.00 / 158.50 hrs communicating / 307.00 hrs other."""
        _, _, filings, _ = parse_principal_meta(
            _load("principal_11590_populated.html"), 11590
        )
        p1 = next(
            f for f in filings if f.reporting_period_start
            and f.reporting_period_start.year == 2025
            and f.reporting_period_start.month == 1
        )
        assert p1.total_expenditure == 37840.00
        assert p1.total_hours_communicating == 158.50
        assert p1.total_hours_other == 307.00

    def test_dairy_p2_amounts(self):
        """2025 Jul-Dec (P2): $50,728.50 / 100.50 hrs communicating / 254.00 hrs other."""
        _, _, filings, _ = parse_principal_meta(
            _load("principal_11590_populated.html"), 11590
        )
        p2 = next(
            f for f in filings if f.reporting_period_start
            and f.reporting_period_start.year == 2025
            and f.reporting_period_start.month == 7
        )
        assert p2.total_expenditure == 50728.50
        assert p2.total_hours_communicating == 100.50
        assert p2.total_hours_other == 254.00

    def test_filing_filer_role_and_organization(self):
        _, _, filings, _ = parse_principal_meta(
            _load("principal_11590_populated.html"), 11590
        )
        f = filings[0]
        assert f.filer_role == "client"
        assert f.filer_organization is not None
        assert f.filer_organization.id == "WI-principal-11590"

    def test_filing_provenance_populated(self):
        """Per Dan's resolution of plan Q1, LobbyingFiling.provenance is
        populated with source_url and extracted_at. source_url is the
        principal-info detail page; extracted_at is the parse-time timestamp."""
        _, _, filings, _ = parse_principal_meta(
            _load("principal_11590_populated.html"), 11590
        )
        f = filings[0]
        assert f.provenance is not None
        assert f.provenance.source_url is not None
        assert "PrincipalInformation" in f.provenance.source_url
        assert "11590" in f.provenance.source_url
        assert f.provenance.extracted_at is not None

    def test_wcta_low_spend_exempt_zero_filings(self):
        """WCTA 12997 is the low-spend exempt case: $0 across all periods.
        The parser still emits LobbyingFiling records (zero-spend is real
        data, not absence) with total_expenditure=0.0 and zero hours."""
        _, _, filings, _ = parse_principal_meta(_load("principal_12997.html"), 12997)
        assert len(filings) >= 1
        for f in filings:
            assert f.total_expenditure == 0.0
            assert f.total_hours_communicating == 0.0
            assert f.total_hours_other == 0.0


# ---------------------------------------------------------------------------
# Per-item Percent Allocation rows (the third return value)
# ---------------------------------------------------------------------------


class TestPercentAllocationItemRows:
    """The third return value is a list of dicts, one per (bucket, item_id,
    period) entry from the Percent Allocation section. Keys per the
    item-level shape locked with Dan:

        {
            "principal_id": int,
            "bucket": str,
            "item_id": str,       # WI portal internal ID
            "item_name": str,     # 'Assembly Bill 30' etc.
            "item_description": str | None,  # 'Relating to: ...'
            "period_label": str,  # '2025 January - June' etc.
            "percent": str,       # '1%' / '100%' / etc. (text, not numeric)
        }

    Empty period cells are skipped (not emitted as a row with percent=None).
    Long-term this becomes a typed LobbyingEffortAllocation sub-entity (v1.3
    bump); the dict shape is the prototype.
    """

    def test_dairy_emits_per_bill_per_period_rows(self):
        """Dairy 11590 has multiple Legislative Bills, each with 2 populated
        periods → at minimum a couple-dozen item rows."""
        _, _, _, items = parse_principal_meta(
            _load("principal_11590_populated.html"), 11590
        )
        assert len(items) > 0
        # All rows carry the principal_id and a bucket.
        for row in items:
            assert row["principal_id"] == 11590
            assert row["bucket"] in {
                "Legislative Bills/Resolutions",
                "Budget Bill Subjects",
                "Administrative Rulemaking Proceedings",
                "Topics Not Yet Assigned A Bill Or Rule Number",
                "Minor Efforts",
                "Other Matters",
            }

    def test_dairy_contains_known_bill(self):
        """Assembly Bill 30 (item_id 24598) → 1% in 2025 Jan-Jun per the
        fixture's HTML."""
        _, _, _, items = parse_principal_meta(
            _load("principal_11590_populated.html"), 11590
        )
        ab30_2025_h1 = [
            row for row in items
            if row["item_id"] == "24598"
            and row["period_label"].startswith("2025") and "January" in row["period_label"]
        ]
        assert len(ab30_2025_h1) == 1
        assert ab30_2025_h1[0]["item_name"] == "Assembly Bill 30"
        assert ab30_2025_h1[0]["percent"] == "1%"

    def test_lexia_topics_not_yet_assigned_100pct(self):
        """Lexia 11348: only Topics-Not-Yet-Assigned bucket is populated;
        single item at 100% across both completed semesters."""
        _, _, _, items = parse_principal_meta(_load("principal_11348.html"), 11348)
        assert len(items) >= 2
        # All Lexia rows are in the Topics-Not-Yet-Assigned bucket.
        for row in items:
            assert row["bucket"] == "Topics Not Yet Assigned A Bill Or Rule Number"
            assert row["percent"] == "100%"

    def test_wcta_empty_allocation_yields_no_items(self):
        """WCTA 12997: all 6 allocation buckets read 'No X found.' → zero
        item rows emitted."""
        _, _, _, items = parse_principal_meta(_load("principal_12997.html"), 12997)
        assert items == []

    def test_empty_period_cells_skipped(self):
        """In-progress 2026 cells are empty (text content is whitespace, no
        % value). The parser does NOT emit a row with percent=None for those
        cells — they're absent from the output."""
        _, _, _, items = parse_principal_meta(
            _load("principal_11590_populated.html"), 11590
        )
        # 11590's bills all have empty 2026 cells; if any 2026 row exists,
        # the parser is emitting empty-cell rows it shouldn't.
        rows_2026 = [row for row in items if row["period_label"].startswith("2026")]
        assert rows_2026 == []
