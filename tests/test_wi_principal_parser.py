"""Behavior tests for ``parse_principal_authorizations`` — the
principal-side mirror of ``parse_lobbyist_authorizations``.

The parser is a pure function; tests run against committed HTML
fixtures captured from the live portal during the 2026-05-26
principal-gap investigation. They verify that specific known
authorizations on specific known pages are correctly extracted.

The principal page exposes the same (lobbyist, principal,
authorized_on, withdrawn_on) edges as the lobbyist-side page, just
keyed on the other endpoint of the bipartite graph. The schema of
the returned ``Authorization`` is identical — only the page that
publishes the edge differs.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from lobby_analysis.io.wi.authorization_parser import Authorization, ParseError
from lobby_analysis.io.wi.principal_parser import parse_principal_authorizations


FIXTURE_DIR = Path(__file__).parent / "fixtures" / "wi"


def _load(name: str) -> str:
    return (FIXTURE_DIR / name).read_text(encoding="utf-8")


def test_parses_single_lobbyist_principal():
    """Load-bearing case for the whole plan: WCTA (principal 12997) has
    exactly one authorized lobbyist — Michael Schlaak (12694) —
    authorized 1/8/2026, no withdrawal. Schlaak is silently omitted
    from the LobbyistList grid AJAX and the directory .xls, so this
    edge is reachable ONLY via the principal-side back-link. If the
    parser misses this row, the Schlaak-class population enumeration
    is broken at the source."""
    html = _load("principal_12997.html")

    auths = parse_principal_authorizations(html, principal_id=12997)

    assert auths == [
        Authorization(
            lobbyist_id=12694,
            principal_id=12997,
            authorized_on=date(2026, 1, 8),
            withdrawn_on=None,
        )
    ]


def test_parses_multi_lobbyist_principal():
    """Lexia Learning (principal 11348) has 4 authorized lobbyists, all
    withdrawn on the same date — verifies that the parser handles
    multi-row sections AND that the Withdrawn On column is parsed as
    a real date, not coerced to None."""
    html = _load("principal_11348.html")

    auths = parse_principal_authorizations(html, principal_id=11348)

    expected = {
        Authorization(11137, 11348, date(2024, 12, 30), date(2026, 2, 2)),  # Adam Barr
        Authorization(11119, 11348, date(2024, 12, 30), date(2026, 2, 2)),  # McCoshen
        Authorization(11403, 11348, date(2024, 12, 30), date(2026, 2, 2)),  # Liedl
        Authorization(11113, 11348, date(2024, 12, 30), date(2026, 2, 2)),  # Stengl
    }
    assert set(auths) == expected
    assert len(auths) == 4
    assert all(a.principal_id == 11348 for a in auths)


def test_parses_privacy_redacted_principal():
    """Principal 11530 is privacy-redacted under the WI Ethics
    Commission's <$500/year "low-spend pledge" exemption: the
    principal-info section is suppressed (page title is the generic
    "Lobbying in Wisconsin", not the principal's name) BUT the
    Authorized Lobbyists section IS published.

    The parser must not gate extraction on principal-info presence —
    if it does, the redacted principals' edges drop out of the
    principal-side scrape and the bipartite graph loses 2+ known
    principals from the gap-investigation classification."""
    html = _load("principal_11530.html")

    auths = parse_principal_authorizations(html, principal_id=11530)

    expected = {
        Authorization(11147, 11530, date(2025, 1, 2), None),  # Hubbard
        Authorization(11216, 11530, date(2025, 1, 2), None),  # White
        Authorization(11082, 11530, date(2025, 1, 2), None),  # Wilson
    }
    assert set(auths) == expected
    assert len(auths) == 3


def test_parses_ceased_principal_with_historical_authorizations():
    """Apex Clean Energy (principal 10949) ceased 1/22/2025; its one
    historical lobbyist authorization (Chris Kunkle, 11061, authorized
    12/9/2024, withdrawn 1/23/2025) is still published on the
    principal page. The parser must extract historical authorizations
    on ceased principals — they ARE part of the bipartite graph for
    the 2025REG session even if the principal is no longer active."""
    html = _load("principal_10949.html")

    auths = parse_principal_authorizations(html, principal_id=10949)

    assert auths == [
        Authorization(
            lobbyist_id=11061,
            principal_id=10949,
            authorized_on=date(2024, 12, 9),
            withdrawn_on=date(2025, 1, 23),
        )
    ]


def test_unparseable_authorized_lobbyists_section_raises_parse_error():
    """If the portal changes its DOM and the "<h3>Authorized Lobbyists</h3>"
    heading is missing, the parser must raise loudly. A silent ``[]``
    on a structural change would let an entire 944-principal scrape
    produce an empty join table without anyone noticing — exactly the
    failure mode the existing lobbyist parser already guards against.
    """
    html = _load("principal_12997.html").replace(
        ">Authorized Lobbyists<", ">Some Other Heading<"
    )

    with pytest.raises(ParseError):
        parse_principal_authorizations(html, principal_id=12997)


def test_empty_authorized_lobbyists_section_returns_empty_list():
    """A principal with no authorized lobbyists (e.g., registered but
    no one filed an authorization, or all withdrawn before our
    snapshot) should return an empty list — not raise. The
    distinguishing feature from the parse-error case above is that
    the heading IS present; only the rows are missing."""
    html = """<!DOCTYPE html><html><body>
        <h3>Authorized Lobbyists</h3>
        <div class="card bg-light mb-4"><div class="card-body">
          <table class="table">
            <thead><tr>
              <th>Lobbyist Name</th><th>Exclusive Duties</th>
              <th>Authorized On</th><th>Withdrawn On</th>
            </tr></thead>
            <tbody></tbody>
          </table>
        </div></div>
        </body></html>"""

    auths = parse_principal_authorizations(html, principal_id=99999)

    assert auths == []
