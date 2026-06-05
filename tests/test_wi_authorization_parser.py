"""Behavior tests for the WI lobbyist-page authorization parser.

The parser turns a per-lobbyist HTML detail page from lobbying.wi.gov
into a list of (lobbyist_id, principal_id, authorized_on, withdrawn_on)
records — one per row of the "Principals Represented" table.

Ground truth comes from a real portal snapshot of lobbyist 11042
(fixture: ``tests/fixtures/wi/lobbyist_11042.html``). The 9 rows in that
snapshot were captured 2026-05-26; principal IDs and authorized-on dates
are verifiable by visiting the live page until the WI Ethics Commission
re-renders it.

See the originating convo for context:
``docs/active/wi-disclosure-explore/convos/20260526_wi_data_ingest_and_join_key_investigation.md``
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from lobby_analysis.io.wi.authorization_parser import (
    Authorization,
    ParseError,
    parse_lobbyist_authorizations,
)

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "wi"


def _load_fixture(name: str) -> str:
    return (FIXTURE_DIR / name).read_text(encoding="utf-8")


def test_parses_full_lobbyist_11042_ground_truth():
    """Lobbyist 11042's page yields exactly the 9 authorizations observed in
    the snapshot, with correct principal IDs, parsed dates, and
    ``withdrawn_on=None`` for every "N/A" cell."""
    html = _load_fixture("lobbyist_11042.html")

    result = parse_lobbyist_authorizations(html, lobbyist_id=11042)

    expected = {
        Authorization(11042, 11158, date(2024, 12, 17), None),  # Wisconsin Agri-Business Association
        Authorization(11042, 11590, date(2025, 1, 3), None),    # Dairy Business Association
        Authorization(11042, 11300, date(2024, 12, 20), None),  # Data Recognition Corporation
        Authorization(11042, 11110, date(2024, 12, 13), None),  # One City Schools, Inc.
        Authorization(11042, 13214, date(2026, 2, 17), None),   # Pivot Bio
        Authorization(11042, 11102, date(2025, 1, 3), None),    # Stride, Inc.
        Authorization(11042, 11004, date(2024, 12, 10), None),  # Wisconsin Counties Utility Tax Association
        Authorization(11042, 10937, date(2024, 12, 3), None),   # Wisconsin County Forests Association
        Authorization(11042, 11678, date(2025, 1, 7), None),    # Wisconsin Land and Water Conservation Association, Inc.
    }
    assert set(result) == expected


def test_lobbyist_id_is_propagated_from_argument():
    """The parser does not try to extract the lobbyist's own ID from the
    HTML — it stamps every Authorization with the lobbyist_id the caller
    passed in. Verified by asking for a different ID than the page's
    actual one and checking it propagates."""
    html = _load_fixture("lobbyist_11042.html")

    result = parse_lobbyist_authorizations(html, lobbyist_id=99999)

    assert result, "expected at least one record from the real fixture"
    assert {row.lobbyist_id for row in result} == {99999}


def test_empty_principals_section_returns_empty_list():
    """A lobbyist with the section present but zero rows yields ``[]`` —
    not an exception."""
    html = """
    <html><body>
      <div class="row"><div class="col-lg-12">
        <h3>Principals Represented</h3>
        <div class="card bg-light mb-4"><div class="card-body">
          <table class="table">
            <thead><tr><th>Principal Name</th><th>Exclusive?</th>
              <th>Authorized On</th><th>Withdrawn On</th></tr></thead>
            <tbody></tbody>
          </table>
        </div></div>
      </div></div>
    </body></html>
    """

    result = parse_lobbyist_authorizations(html, lobbyist_id=12345)

    assert result == []


def test_authorized_on_can_be_none_when_value_is_na():
    """The live portal sometimes shows ``Authorized On = N/A`` (a small
    number of rows where the relationship is in the database but no
    dates have been finalized — pending, or a data-entry artifact). The
    parser must represent these as ``authorized_on=None`` rather than
    raising — losing the row entirely would silently drop edges from
    the join table.

    Surfaced 2026-05-26 by the full live scrape: 4 of 2251 rows across
    the 774 lobbyists had this shape (lobbyists 11112, 12666, 12748,
    13865 — Wisconsin Reading Corps shows up in two of the four)."""
    html = """
    <html><body>
      <h3>Principals Represented</h3>
      <table><thead><tr><th>Principal Name</th><th>Exclusive?</th>
        <th>Authorized On</th><th>Withdrawn On</th></tr></thead>
      <tbody>
        <tr>
          <td class="label"><a href="/Who/PrincipalInformation/2025REG/Information/11415?tab=Lobbyists">Wisconsin Reading Corps</a></td>
          <td><span class="table-responsive-stack-thead">Exclusive?</span> No</td>
          <td><span class="table-responsive-stack-thead">Authorized On</span> N/A</td>
          <td><span class="table-responsive-stack-thead">Withdrawn On</span> N/A</td>
        </tr>
      </tbody></table>
    </body></html>
    """

    result = parse_lobbyist_authorizations(html, lobbyist_id=11112)

    assert len(result) == 1
    assert result[0].lobbyist_id == 11112
    assert result[0].principal_id == 11415
    assert result[0].authorized_on is None
    assert result[0].withdrawn_on is None


def test_missing_section_raises_parse_error_not_silent_empty():
    """If the page structure no longer carries the "Principals Represented"
    section at all, the parser must FAIL LOUDLY (raise ParseError) — not
    silently return []. Silently returning [] would let a portal redesign
    blow up the whole scrape into a join table of nothing without anyone
    noticing."""
    html = "<html><body><p>portal redesigned, no Principals heading anywhere</p></body></html>"

    with pytest.raises(ParseError):
        parse_lobbyist_authorizations(html, lobbyist_id=12345)
