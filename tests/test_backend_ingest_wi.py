"""Behavior tests for src/lobby_analysis/backend/ingest_wi.py.

A tiny inline fixture WI release (2 principals, 2 lobbyists, 2 principal
filings, 1 lobbyist filing) drives all tests. Real-data ingest is verified
out-of-band against `releases/wi/` by the end-to-end script in Phase 4.
"""

import pytest

from lobby_analysis.backend.ingest_wi import (
    ingest_release_dir,
    iter_lobbyist_filings,
    iter_principal_filings,
    load_organizations,
    load_persons,
)
from lobby_analysis.backend.storage import init_engine, list_filings
from lobby_analysis.models.entities import Organization, Person
from lobby_analysis.models.filings import LobbyingFiling


@pytest.fixture
def wi_mini(tmp_path):
    d = tmp_path / "wi_mini"
    d.mkdir()
    (d / "WI_principals.tsv").write_text(
        "principal_id\tid\tname\tsource_state\tclassification\tlegal_form\tsector\tcontact_details_json\tceo_name\tbusiness_or_interest\tlobbying_interests_prose\n"
        "10936\tWI-principal-10936\tWEC Energy Group, Inc.\tWI\tcompany\t\tenergy\t[]\t\t\t\n"
        "10937\tWI-principal-10937\tAcme Corp\tWI\tcompany\t\t\t[]\t\t\t\n"
    )
    (d / "WI_lobbyists.tsv").write_text(
        "lobbyist_id\tid\tname\tsource_state\tcontact_details_json\n"
        '11040\tWI-lobbyist-11040\tTia Cannon\tWI\t[{"type":"email","value":"foo@bar.com","note":""}]\n'
        "11041\tWI-lobbyist-11041\tBrian Dake\tWI\t[]\n"
    )
    (d / "WI_principal_filings.tsv").write_text(
        "filing_id\tprincipal_id\tstate\tfiling_type\tfiler_role\treporting_period_start\treporting_period_end\ttotal_expenditure\ttotal_hours_communicating\ttotal_hours_other\tsource_url\n"
        "WI-principal-10936-expenditure-2025-H1\t10936\tWI\texpenditure_report\tclient\t2025-01-01\t2025-06-30\t127867.9\t200.75\t247.25\thttps://example.com/10936\n"
        "WI-principal-10937-expenditure-2025-H1\t10937\tWI\texpenditure_report\tclient\t2025-01-01\t2025-06-30\t10000.0\t10.0\t0.0\thttps://example.com/10937\n"
    )
    (d / "WI_lobbyist_filings.tsv").write_text(
        "filing_id\tlobbyist_id\tstate\tfiling_type\tfiler_role\treporting_period_start\treporting_period_end\ttotal_hours_communicating\ttotal_hours_other\tsource_url\n"
        "WI-lobbyist-11040-activity-2025-H1\t11040\tWI\tactivity_report\tlobbyist\t2025-01-01\t2025-06-30\t0.0\t0.0\thttps://example.com/11040\n"
    )
    return d


def test_load_organizations(wi_mini):
    orgs = load_organizations(wi_mini / "WI_principals.tsv")
    assert len(orgs) == 2
    wec = orgs["10936"]
    assert isinstance(wec, Organization)
    assert wec.id == "WI-principal-10936"
    assert wec.name == "WEC Energy Group, Inc."
    assert wec.source_state == "WI"
    assert wec.classification == "company"


def test_load_persons_parses_contact_details(wi_mini):
    persons = load_persons(wi_mini / "WI_lobbyists.tsv")
    assert len(persons) == 2
    tia = persons["11040"]
    assert isinstance(tia, Person)
    assert tia.id == "WI-lobbyist-11040"
    assert tia.name == "Tia Cannon"
    assert len(tia.contact_details) == 1
    assert tia.contact_details[0].type == "email"
    assert tia.contact_details[0].value == "foo@bar.com"


def test_iter_principal_filings_yields_correct_records(wi_mini):
    orgs = load_organizations(wi_mini / "WI_principals.tsv")
    filings = list(iter_principal_filings(wi_mini / "WI_principal_filings.tsv", orgs))
    assert len(filings) == 2

    f = filings[0]
    assert isinstance(f, LobbyingFiling)
    assert f.id == "WI-principal-10936-expenditure-2025-H1"
    assert f.state == "WI"
    assert f.filing_type == "expenditure_report"
    assert f.filer_role == "client"
    assert f.filer_organization is not None
    assert f.filer_organization.name == "WEC Energy Group, Inc."
    assert f.filer_person is None
    assert f.total_expenditure == 127867.9
    assert str(f.reporting_period_start) == "2025-01-01"
    assert str(f.reporting_period_end) == "2025-06-30"
    assert f.source_url == "https://example.com/10936"


def test_iter_lobbyist_filings_yields_correct_records(wi_mini):
    persons = load_persons(wi_mini / "WI_lobbyists.tsv")
    filings = list(iter_lobbyist_filings(wi_mini / "WI_lobbyist_filings.tsv", persons))
    assert len(filings) == 1

    f = filings[0]
    assert f.id == "WI-lobbyist-11040-activity-2025-H1"
    assert f.filing_type == "activity_report"
    assert f.filer_role == "lobbyist"
    assert f.filer_person is not None
    assert f.filer_person.name == "Tia Cannon"
    assert f.filer_organization is None


def test_ingest_release_dir_persists_all_filings(wi_mini):
    engine = init_engine()
    counts = ingest_release_dir(wi_mini, engine)
    assert counts["principal_filings"] == 2
    assert counts["lobbyist_filings"] == 1

    all_filings = list_filings(engine, limit=10)
    assert len(all_filings) == 3
    ids = {f.id for f in all_filings}
    assert "WI-principal-10936-expenditure-2025-H1" in ids
    assert "WI-lobbyist-11040-activity-2025-H1" in ids
