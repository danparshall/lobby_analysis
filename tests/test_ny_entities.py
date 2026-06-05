"""Behavior tests for NY entity parsing (``io/ny/parse``): raw rows -> Popolo
``Organization`` / ``Person`` models, reusing ``src/lobby_analysis/models/``.

NY has no stable numeric entity id in the bulk data (WI had ``11590``-style ids;
NY keys everything by *name string*). So entity identity is derived from a
normalized name, under the project's ``NY-{role}-{slug}`` id convention
(parallel to WI's ``WI-principal-{id}`` / ``WI-lobbyist-{id}``). Names arrive
dirty: clients carry a trailing ``;`` (``"GRAHAM WINDHAM;"``), and the
individual-lobbyist field is a single semicolon-delimited string with stray
internal whitespace and a trailing delimiter
(``"Post, Naomi; Chin, Kimberley; Genadri, Melissa ;"``).

Tests assert on the parsed model *values* (names cleaned, ids stable, people
split out correctly), driven by the real Phase-0 fixture rows.
"""

from __future__ import annotations

import json
from pathlib import Path

from lobby_analysis.io.ny.parse import (
    parse_client,
    parse_individual_lobbyists,
    parse_principal_lobbyist,
)
from lobby_analysis.models.entities import Organization, Person

FIXTURE = Path(__file__).parent / "fixtures" / "ny" / "sample_schema_core2_datasets.json"


def _examples(dataset: str) -> list[dict]:
    return json.loads(FIXTURE.read_text())[dataset]["examples"]


def test_principal_lobbyist_parses_to_organization():
    """The ``principal_lobbyist`` (the lobbying firm) becomes an Organization
    with a NY firm id and the cleaned name. From the real client_semiannual
    row: firm = 'THE PARKSIDE GROUP LLC'."""
    org = parse_principal_lobbyist("THE PARKSIDE GROUP LLC")

    assert isinstance(org, Organization)
    assert org.name == "THE PARKSIDE GROUP LLC"
    assert org.source_state == "NY"
    assert org.id.startswith("NY-lobbyist-")


def test_client_parses_to_organization_with_trailing_semicolon_stripped():
    """``beneficial_client`` arrives as 'GRAHAM WINDHAM;' (trailing delimiter).
    The Organization name must be the clean 'GRAHAM WINDHAM'."""
    org = parse_client("GRAHAM WINDHAM;")

    assert isinstance(org, Organization)
    assert org.name == "GRAHAM WINDHAM"
    assert org.source_state == "NY"
    assert org.id.startswith("NY-client-")


def test_same_client_name_yields_the_same_id():
    """Entity identity is name-derived and stable: the same client name (modulo
    trailing-semicolon / case / whitespace noise) must map to one id, so the
    client doesn't fork into duplicate entities across filings."""
    a = parse_client("GRAHAM WINDHAM;")
    b = parse_client("graham windham")
    c = parse_client("  GRAHAM WINDHAM ")

    assert a.id == b.id == c.id


def test_principal_and_client_with_same_name_get_distinct_ids():
    """A firm and a client can share a name (self-filing orgs do). The role
    prefix keeps them distinct so the chain doesn't conflate the two roles —
    seen in the real data: 'Children's Defense Fund' is both."""
    firm = parse_principal_lobbyist("Children's Defense Fund")
    client = parse_client("Children's Defense Fund")

    assert firm.id != client.id
    assert firm.id.startswith("NY-lobbyist-")
    assert client.id.startswith("NY-client-")


def test_individual_lobbyists_split_on_semicolons():
    """The ``individual_lobbyist_name`` field is one semicolon-delimited string.
    Parse it into one Person per name, trimming stray whitespace and dropping
    the empty tail from the trailing delimiter. From the real bimonthly row."""
    raw = "Post, Naomi; Chin, Kimberley; Genadri, Melissa ; Aung, Khin Mai;"

    people = parse_individual_lobbyists(raw)

    names = [p.name for p in people]
    assert names == ["Post, Naomi", "Chin, Kimberley", "Genadri, Melissa", "Aung, Khin Mai"]
    assert all(isinstance(p, Person) for p in people)
    assert all(p.source_state == "NY" for p in people)
    assert all(p.id.startswith("NY-person-") for p in people)


def test_individual_lobbyists_empty_or_none_yields_no_people():
    """A filing with no named individuals (empty string / None) yields an empty
    list, not a Person with a blank name."""
    assert parse_individual_lobbyists("") == []
    assert parse_individual_lobbyists(None) == []
    assert parse_individual_lobbyists("  ;  ;") == []


def test_individual_lobbyists_dedupe_within_one_field():
    """If the same name appears twice in one semicolon list, it yields one
    Person (same derived id), not duplicates."""
    people = parse_individual_lobbyists("Levy, Scott; Levy, Scott;")

    assert len(people) == 1
    assert people[0].name == "Levy, Scott"
