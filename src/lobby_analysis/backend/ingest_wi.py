"""WI release ingestion adapter.

Maps Dan's `releases/wi/` TSVs into `LobbyingFiling` records that the
backend storage layer can persist. The release files already mirror the
project's data model closely:

- `WI_principals.tsv`        → Organization (filer for principal filings)
- `WI_lobbyists.tsv`         → Person (filer for lobbyist filings)
- `WI_principal_filings.tsv` → LobbyingFiling (filer_role="client")
- `WI_lobbyist_filings.tsv`  → LobbyingFiling (filer_role="lobbyist")

Known schema gaps (intentionally dropped in v1, surface them upstream):
- `total_hours_communicating` and `total_hours_other` have no home on
  `LobbyingFiling`. Dropped.
- `WI_principal_bill_efforts.tsv` is keyed on (principal, bucket,
  period_label) — not directly attached to a filing. Skipped here;
  reattachment is a follow-up slice.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Iterator

from sqlalchemy.engine import Engine

from lobby_analysis.backend.storage import insert_filing
from lobby_analysis.models.entities import ContactDetail, Organization, Person
from lobby_analysis.models.filings import LobbyingFiling


def _read_tsv(path: Path) -> Iterator[dict[str, str]]:
    with open(path, newline="", encoding="utf-8") as f:
        yield from csv.DictReader(f, delimiter="\t")


def _parse_contact_details(value: str) -> list[ContactDetail]:
    if not value or value.strip() in ("", "[]"):
        return []
    raw = json.loads(value)
    return [ContactDetail(**item) for item in raw]


def _coerce_float(value: str | None) -> float | None:
    if value is None or value == "":
        return None
    return float(value)


def load_organizations(path: Path) -> dict[str, Organization]:
    """Parse WI_principals.tsv → {portal_principal_id: Organization}.

    Keyed by the portal-native integer id (`principal_id` column), so the
    filings TSV can join against it. The Popolo-style `id` (`WI-principal-...`)
    lives on the Organization record itself.
    """
    out: dict[str, Organization] = {}
    for row in _read_tsv(path):
        out[row["principal_id"]] = Organization(
            id=row["id"],
            name=row["name"],
            source_state=row["source_state"],
            classification=row["classification"] or None,
            sector=row["sector"] or None,
            legal_form=row["legal_form"] or None,
            contact_details=_parse_contact_details(row["contact_details_json"]),
        )
    return out


def load_persons(path: Path) -> dict[str, Person]:
    """Parse WI_lobbyists.tsv → {portal_lobbyist_id: Person}."""
    out: dict[str, Person] = {}
    for row in _read_tsv(path):
        out[row["lobbyist_id"]] = Person(
            id=row["id"],
            name=row["name"],
            source_state=row["source_state"],
            contact_details=_parse_contact_details(row["contact_details_json"]),
        )
    return out


def iter_principal_filings(
    path: Path, organizations: dict[str, Organization]
) -> Iterator[LobbyingFiling]:
    """Yield one LobbyingFiling per row in WI_principal_filings.tsv.

    Raises KeyError if a row references an unknown principal_id — better to
    fail at ingest time than to ship partial data with broken refs.
    """
    for row in _read_tsv(path):
        org = organizations.get(row["principal_id"])
        if org is None:
            raise KeyError(f"unknown principal_id {row['principal_id']!r}")
        yield LobbyingFiling(
            id=row["filing_id"],
            state=row["state"],
            filing_id=row["filing_id"],
            filing_type=row["filing_type"],
            filer_role=row["filer_role"],
            filer_organization=org,
            reporting_period_start=row["reporting_period_start"] or None,
            reporting_period_end=row["reporting_period_end"] or None,
            total_expenditure=_coerce_float(row.get("total_expenditure", "")),
            source_url=row["source_url"] or None,
        )


def iter_lobbyist_filings(
    path: Path, persons: dict[str, Person]
) -> Iterator[LobbyingFiling]:
    """Yield one LobbyingFiling per row in WI_lobbyist_filings.tsv."""
    for row in _read_tsv(path):
        person = persons.get(row["lobbyist_id"])
        if person is None:
            raise KeyError(f"unknown lobbyist_id {row['lobbyist_id']!r}")
        yield LobbyingFiling(
            id=row["filing_id"],
            state=row["state"],
            filing_id=row["filing_id"],
            filing_type=row["filing_type"],
            filer_role=row["filer_role"],
            filer_person=person,
            reporting_period_start=row["reporting_period_start"] or None,
            reporting_period_end=row["reporting_period_end"] or None,
            source_url=row["source_url"] or None,
        )


def ingest_release_dir(release_dir: Path, engine: Engine) -> dict[str, int]:
    """Ingest the 4 main TSVs from a `releases/wi/`-style dir. Returns counts."""
    organizations = load_organizations(release_dir / "WI_principals.tsv")
    persons = load_persons(release_dir / "WI_lobbyists.tsv")

    pf_count = 0
    for filing in iter_principal_filings(
        release_dir / "WI_principal_filings.tsv", organizations
    ):
        insert_filing(engine, filing)
        pf_count += 1

    lf_count = 0
    for filing in iter_lobbyist_filings(
        release_dir / "WI_lobbyist_filings.tsv", persons
    ):
        insert_filing(engine, filing)
        lf_count += 1

    return {
        "organizations": len(organizations),
        "persons": len(persons),
        "principal_filings": pf_count,
        "lobbyist_filings": lf_count,
    }
