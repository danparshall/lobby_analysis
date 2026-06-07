"""Tests for the OH-portal agent-axis filing discovery parsers.

The HTTP fetching is an external boundary and is not exercised here. What IS
tested is the parsing/filtering of the portal's real response shapes (markup +
CSV captured live from OLAC on 2026-06-04), which is where the bugs live:
column-order assumptions, AER-vs-registration discrimination, year filtering.
"""

from pathlib import Path

from lobby_analysis.oh_portal.discover import (
    _discover_dir,
    category_to_regime,
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


def test_parse_forms_filed_captures_category() -> None:
    # The Category column (L/E/R) is what distinguishes the OLAC disclosure
    # regime; without it the agent-axis crawl can't tell a legislative AER from
    # an executive one. Index 5 in the real 8-column table.
    forms = parse_forms_filed(FORMS_FILED_HTML)
    cats = {f.report_id: f.category for f in forms}
    assert cats["1492518"] == "L"  # legislative AER
    assert cats["1427844"] == "E"  # executive AER


def test_category_to_regime_maps_known_letters() -> None:
    assert category_to_regime("L") == "legislative"
    assert category_to_regime("E") == "executive"
    assert category_to_regime("R") == "retirement_system"


def test_category_to_regime_unknown_is_none_not_legislative() -> None:
    # The bug being removed is defaulting unknowns to "legislative". An
    # unrecognized or blank category must surface as None, not a silent default.
    assert category_to_regime("") is None
    assert category_to_regime("X") is None


def test_recent_aers_filters_by_type_and_year() -> None:
    forms = parse_forms_filed(FORMS_FILED_HTML)
    kept = recent_aers(forms, years={2025, 2026})
    ids = sorted(f.report_id for f in kept)
    # Drops the 2026 Initial (not an AER) and the 2019 AER (too old).
    assert ids == ["1427844", "1492518"]
    assert all(f.form_type == "AER" for f in kept)


# --- Issue #36: cache path was doubled (data/oh_portal/oh_portal/discover/). -- #
# DATA_DIR (from fetch.py) is already .../data/oh_portal, so _discover_dir
# must NOT prepend "oh_portal" a second time. Contract: result is data_dir
# joined with "discover" only, regardless of what data_dir is. -------------- #


def test_discover_dir_returns_discover_subdir_of_data_dir(tmp_path: Path) -> None:
    # The caller's data_dir is treated as the oh_portal-rooted dir; _discover_dir
    # appends only "discover". This mirrors how fetch.DATA_DIR is structured.
    data_dir = tmp_path / "data" / "oh_portal"
    assert _discover_dir(data_dir) == data_dir / "discover"


def test_discover_dir_does_not_double_oh_portal_segment(tmp_path: Path) -> None:
    # Regression guard against the doubled-path bug — even if data_dir
    # itself happens to end in "oh_portal", the function must not append a
    # second "oh_portal" segment.
    data_dir = tmp_path / "data" / "oh_portal"
    result = _discover_dir(data_dir)
    parts = result.parts
    # exactly one "oh_portal" between "data" and "discover"
    assert parts.count("oh_portal") == 1, f"doubled oh_portal in {result}"
    assert "discover" in parts
    assert parts[-1] == "discover"


def test_discover_dir_creates_directory(tmp_path: Path) -> None:
    data_dir = tmp_path / "data" / "oh_portal"
    assert not (data_dir / "discover").exists()
    result = _discover_dir(data_dir)
    assert result.is_dir(), "discover dir should be created on call"
