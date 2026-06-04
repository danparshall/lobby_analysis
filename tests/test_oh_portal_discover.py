"""Tests for the OH-portal agent-axis filing discovery parsers.

The HTTP fetching is an external boundary and is not exercised here. What IS
tested is the parsing/filtering of the portal's real response shapes (markup +
CSV captured live from OLAC on 2026-06-04), which is where the bugs live:
column-order assumptions, AER-vs-registration discrimination, year filtering.
"""

from lobby_analysis.oh_portal.discover import (
    parse_agent_roster,
    parse_forms_filed,
    parse_search_agent_ids,
    recent_aers,
)

# Real OLAC roster CSV shape (Agents/List). Note the trailing space in a real
# first name — the parser must strip it.
ROSTER_CSV = (
    '"Last Name","First Name","Address","Address 2","City","State","Zipcode","Phone"\n'
    '"Aichele","Nathan","4580 Helston Court","","Columbus","OH","43220","614-204-4909"\n'
    '"Akwakoku","Belawoe ","900 Cottage Grove Road","","Bloomfield","CT","06002","240-561-2888"\n'
)

# Real FormsFiledSearch result shape: anchors to per-agent FormsFiled pages.
SEARCH_HTML = (
    '<div><a href="/olac/Reports/Agents/5272/FormsFiled">Nathan Aichele</a></div>'
    '<div><a href="/olac/Reports/Agents/7140/FormsFiled">Nathan Aichele</a></div>'
)

# Real Agents/{id}/FormsFiled table shape (8 columns; View path differs by type).
FORMS_FILED_HTML = """
<table class="table table-striped">
<thead><tr>
  <th>Year</th><th>Employer Name</th><th>Type</th><th>Termination Date</th>
  <th>Amended</th><th>Category</th><th>Reporting Period</th><th></th>
</tr></thead>
<tbody>
<tr><td>2026</td><td>ALPS Services Inc. </td><td>Initial</td><td></td><td></td>
    <td>E</td><td></td>
    <td class="text-end"><a href="/olac/Initials/487198/View">View</a></td></tr>
<tr><td>2026</td><td>ALPS Services Inc. </td><td>AER</td><td></td><td></td>
    <td>L</td><td>Jan-Apr26</td>
    <td class="text-end"><a href="/olac/AERs/1492518/View">View</a></td></tr>
<tr><td>2025</td><td>ARC Gaming &amp;. Technologies</td><td>AER</td><td></td><td></td>
    <td>E</td><td>May-Aug25</td>
    <td class="text-end"><a href="/olac/AERs/1427844/View">View</a></td></tr>
<tr><td>2019</td><td>Old Employer LLC</td><td>AER</td><td></td><td></td>
    <td>E</td><td>Jan-Apr19</td>
    <td class="text-end"><a href="/olac/AERs/1001692/View">View</a></td></tr>
</tbody>
</table>
"""


def test_parse_agent_roster_extracts_names_and_strips_whitespace() -> None:
    agents = parse_agent_roster(ROSTER_CSV)
    pairs = [(a.last_name, a.first_name) for a in agents]
    assert pairs == [("Aichele", "Nathan"), ("Akwakoku", "Belawoe")]


def test_parse_search_agent_ids_returns_all_matches() -> None:
    # A surname can map to multiple agent records (two Aicheles in OH).
    assert parse_search_agent_ids(SEARCH_HTML) == ["5272", "7140"]


def test_parse_forms_filed_reads_all_rows_with_fields() -> None:
    forms = parse_forms_filed(FORMS_FILED_HTML)
    assert len(forms) == 4
    aer = next(f for f in forms if f.report_id == "1427844")
    assert aer.year == 2025
    assert aer.form_type == "AER"
    assert aer.employer == "ARC Gaming &. Technologies"  # html-unescaped
    assert aer.reporting_period == "May-Aug25"
    assert aer.view_url == "/olac/AERs/1427844/View"


def test_parse_forms_filed_keeps_registration_distinguishable() -> None:
    forms = parse_forms_filed(FORMS_FILED_HTML)
    initial = next(f for f in forms if f.report_id == "487198")
    assert initial.form_type == "Initial"
    assert "/olac/Initials/" in initial.view_url


def test_recent_aers_filters_by_type_and_year() -> None:
    forms = parse_forms_filed(FORMS_FILED_HTML)
    kept = recent_aers(forms, years={2025, 2026})
    ids = sorted(f.report_id for f in kept)
    # Drops the 2026 Initial (not an AER) and the 2019 AER (too old).
    assert ids == ["1427844", "1492518"]
    assert all(f.form_type == "AER" for f in kept)
