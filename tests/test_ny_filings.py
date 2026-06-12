"""Behavior tests for NY money coercion + filing parsing (``io/ny/parse``).

Phase 0 flagged that NY money is dirty: it mixes ``"$1000"`` (registration),
bare ``"17160"`` / ``"6000"`` (reports), and a literal ``"$"`` (an empty
``total_contribution_amount``). The coercer must turn real amounts into
``Decimal`` (the plan: *Decimal for money, not float*) and treat ``"$"`` / ``""``
/ NaN as absent (None), never as 0 — a missing contribution is not a $0
contribution.

The filing parser maps one collapsed grain row (a filing's ``filing_compensation``
+ identity) to a ``LobbyingFiling`` with the firm as ``filer_organization`` and
``filer_role='firm'`` (NY client-semiannual is the firm's report of comp it
received from the client). Compensation is filing-level; the parser carries the
already-de-duplicated value, it does not re-sum.

Tests assert coerced/parsed *values* against the real Phase-0 amounts.
"""

from __future__ import annotations

from decimal import Decimal

from lobby_analysis.io.ny.parse import coerce_money, parse_filing
from lobby_analysis.models.filings import LobbyingFiling


def test_coerce_money_parses_bare_and_dollar_prefixed_amounts():
    """Both report-style bare numbers and registration-style '$'-prefixed
    strings parse to the same Decimal."""
    assert coerce_money("17160") == Decimal("17160")
    assert coerce_money("6000") == Decimal("6000")
    assert coerce_money("$1000") == Decimal("1000")
    assert coerce_money("$24,000") == Decimal("24000")


def test_coerce_money_treats_empty_dollar_sign_as_absent_not_zero():
    """The literal '$' (NY's empty ``total_contribution_amount``), the empty
    string, whitespace, and None all mean 'not reported' -> None. NOT 0, which
    would fabricate a reported-zero where the filer reported nothing."""
    assert coerce_money("$") is None
    assert coerce_money("") is None
    assert coerce_money("   ") is None
    assert coerce_money(None) is None


def test_coerce_money_preserves_explicit_zero():
    """An explicit '0' is a real reported value (the bimonthly rows report
    ``reimbursed_expenses = '0'``) and must round-trip as Decimal('0'), distinct
    from the absent case above."""
    assert coerce_money("0") == Decimal("0")
    assert coerce_money("0.00") == Decimal("0.00")


def test_coerce_money_returns_decimal_not_float():
    """Decimal, not float — the plan's explicit money rule; float would lose
    exactness across the even-split conservation invariant downstream."""
    assert isinstance(coerce_money("24000"), Decimal)


def test_parse_filing_maps_grain_row_to_lobbying_filing():
    """A collapsed grain row -> a LobbyingFiling: NY native filing id, the firm
    as the organizational filer, role 'firm', the filing-level compensation as
    ``total_compensation`` (carried, not summed), and the NY state stamp."""
    row = {
        "reporting_year": "2025",
        "reporting_period": "July/Dec",
        "form_submission_id": "793896",
        "principal_lobbyist": "THE PARKSIDE GROUP LLC",
        "beneficial_client": "GRAHAM WINDHAM;",
        "contractual_client_name": "GRAHAM WINDHAM",
        "filing_compensation": "24000",
        "n_bills_in_filing": 2,
    }

    filing = parse_filing(row)

    assert isinstance(filing, LobbyingFiling)
    assert filing.state == "NY"
    assert filing.filing_id == "793896"
    assert filing.filer_role == "firm"
    # NY client_semiannual is a compensation report -> expenditure_report,
    # matching WI's convention (spend report = expenditure_report).
    assert filing.filing_type == "expenditure_report"
    assert filing.filer_organization is not None
    assert filing.filer_organization.name == "THE PARKSIDE GROUP LLC"
    assert filing.total_compensation == Decimal("24000")


def test_parse_filing_with_absent_compensation_yields_none_total():
    """A grain row whose compensation coerces to absent (e.g. '$') must produce
    a filing with ``total_compensation=None`` — not 0, not a crash."""
    row = {
        "reporting_year": "2025",
        "reporting_period": "Jan/June",
        "form_submission_id": "500",
        "principal_lobbyist": "SOME FIRM LLC",
        "beneficial_client": "SOME CLIENT;",
        "contractual_client_name": "SOME CLIENT",
        "filing_compensation": "$",
        "n_bills_in_filing": 0,
    }

    filing = parse_filing(row)

    assert filing.total_compensation is None
    assert filing.filing_id == "500"


def test_parse_filing_id_is_unique_per_submission_and_role_pair():
    """The LobbyingFiling.id must distinguish the (submission, firm, client)
    tuple so two clients under one firm's submission don't collide. Built from
    NY identifiers, deterministic."""
    row_a = {
        "reporting_year": "2025", "reporting_period": "July/Dec",
        "form_submission_id": "793896",
        "principal_lobbyist": "THE PARKSIDE GROUP LLC",
        "beneficial_client": "GRAHAM WINDHAM;",
        "contractual_client_name": "GRAHAM WINDHAM",
        "filing_compensation": "24000", "n_bills_in_filing": 2,
    }
    row_b = dict(row_a, beneficial_client="OTHER CLIENT;", contractual_client_name="OTHER CLIENT")

    fa = parse_filing(row_a)
    fb = parse_filing(row_b)

    assert fa.id != fb.id
