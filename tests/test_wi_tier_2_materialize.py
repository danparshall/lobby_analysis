"""TDD tests for the WI Tier-2 materializer.

Phase 4 of plans/wi_tier_2_parser.md. These tests are expected to fail
until ``src/lobby_analysis/io/wi/tier_2_materialize.py`` exists and exposes
the iterator + writer + orchestrator surface below.

The materializer reads checkpoint JSONs from disk, calls the two Tier-2
parsers (principal_meta_parser + lobbyist_time_report_parser), and emits
5 TSVs plus a parse-failures warnings file::

    WI_principals.tsv              — one row per principal (Organization)
    WI_lobbyists.tsv               — one row per lobbyist (Person)
    WI_principal_filings.tsv       — one row per (principal, semester)
    WI_lobbyist_filings.tsv        — one row per (lobbyist, semester)
    WI_principal_bill_efforts.tsv  — one row per Percent Allocation item × period
    _tier_2_parse_failures.tsv     — ParseError rows (soft-404, etc.) — warnings, not crashes

Idempotency contract (load-bearing): the parsers stamp
``datetime.now(timezone.utc)`` into ``provenance.extracted_at``. The TSV
writers MUST NOT serialize that field, so byte-identical re-runs are
possible. ``source_url`` (stable from URL template) IS serialized.

Fixtures exercised:
- principal_11590_populated.html (Dairy — populated)
- principal_11348.html (Lexia — topics-only at 100%)
- principal_12997.html (WCTA — zero-spend low-spend exempt)
- lobbyist_11052_populated.html (Brooks — fully populated)
- lobbyist_11042.html (Pfaff — populated)
- Plus a synthetic soft-404 lobbyist HTML to drive the ParseError → warnings path.
"""

from __future__ import annotations

import csv
import json
from datetime import date, datetime, timezone
from pathlib import Path

from lobby_analysis.io.wi.tier_2_materialize import (  # noqa: F401 — drives RED
    ParseFailure,
    iter_lobbyist_records,
    iter_principal_records,
    materialize_tier_2,
    write_lobbyist_filings_tsv,
    write_lobbyists_tsv,
    write_parse_failures_tsv,
    write_principal_bill_efforts_tsv,
    write_principal_filings_tsv,
    write_principals_tsv,
)
from lobby_analysis.models import (
    ContactDetail,
    LobbyingFiling,
    Organization,
    Person,
)
from lobby_analysis.models.provenance import Provenance

FIXTURES = Path(__file__).parent / "fixtures" / "wi"


def _load(name: str) -> str:
    return (FIXTURES / name).read_text()


# Soft-404 stub: has <h2 class="display-4"> but no Time Report Summary.
# Mirrors the Neumann-Ortiz 12717 case the prior scrape session caught.
_SOFT_404_LOBBYIST_HTML = (
    '<html><body><h2 class="display-4">Stub Lobbyist</h2></body></html>'
)


def _write_principal_checkpoint(
    checkpoint_dir: Path,
    principal_id: int,
    html: str | None,
    status: int = 200,
    fetched_at: str = "2026-05-26T00:00:00Z",
) -> None:
    (checkpoint_dir / f"{principal_id}.json").write_text(
        json.dumps(
            {
                "principal_id": principal_id,
                "html": html,
                "fetched_at": fetched_at,
                "status_code": status,
            }
        ),
        encoding="utf-8",
    )


def _write_lobbyist_checkpoint(
    checkpoint_dir: Path,
    lobbyist_id: int,
    html: str | None,
    status: int = 200,
    fetched_at: str = "2026-05-26T00:00:00Z",
) -> None:
    (checkpoint_dir / f"{lobbyist_id}.json").write_text(
        json.dumps(
            {
                "lobbyist_id": lobbyist_id,
                "html": html,
                "fetched_at": fetched_at,
                "status_code": status,
            }
        ),
        encoding="utf-8",
    )


# ---------------------------------------------------------------------------
# ParseFailure value object
# ---------------------------------------------------------------------------


class TestParseFailureValueObject:
    """``ParseFailure`` is the tagged-union companion type that iterators yield
    alongside successful parser tuples. It carries everything the
    parse-failures TSV needs."""

    def test_parse_failure_has_entity_type_id_and_reason(self):
        f = ParseFailure(entity_type="lobbyist", entity_id=12717, reason="soft_404")
        assert f.entity_type == "lobbyist"
        assert f.entity_id == 12717
        assert f.reason == "soft_404"

    def test_parse_failure_is_hashable(self):
        """Frozen so it can sit in sets and dicts (downstream dedup)."""
        f1 = ParseFailure(entity_type="lobbyist", entity_id=12717, reason="x")
        f2 = ParseFailure(entity_type="lobbyist", entity_id=12717, reason="x")
        assert {f1, f2} == {f1}


# ---------------------------------------------------------------------------
# iter_principal_records
# ---------------------------------------------------------------------------


class TestIterPrincipalRecords:
    """Yields one ``(Organization, extras_dict, list[LobbyingFiling], list[item_dict])``
    per successfully-parsed principal checkpoint, or a ``ParseFailure`` per
    page that raises ParseError. Null-html checkpoints (404 / soft-404 at
    fetch time) are skipped silently — they contributed nothing at fetch
    time and contribute nothing here."""

    def test_yields_parsed_tuple_for_dairy_checkpoint(self, tmp_path: Path):
        _write_principal_checkpoint(
            tmp_path, 11590, _load("principal_11590_populated.html")
        )

        records = list(iter_principal_records(tmp_path))

        assert len(records) == 1
        rec = records[0]
        # Successful records are tuples of (Organization, dict, list, list).
        assert not isinstance(rec, ParseFailure)
        org, extras, filings, items = rec
        assert isinstance(org, Organization)
        assert org.id == "WI-principal-11590"
        assert isinstance(extras, dict)
        assert "ceo_name" in extras
        assert isinstance(filings, list)
        assert all(isinstance(f, LobbyingFiling) for f in filings)
        assert isinstance(items, list)
        assert all(isinstance(d, dict) for d in items)

    def test_skips_null_html_checkpoints_silently(self, tmp_path: Path):
        """A checkpoint with ``html: null`` (a 404 captured at fetch time)
        contributes nothing — not a record, not a failure. Matches the
        existing ``iter_authorizations_from_principal_checkpoints`` precedent."""
        _write_principal_checkpoint(tmp_path, 99999, html=None, status=404)
        _write_principal_checkpoint(
            tmp_path, 11590, _load("principal_11590_populated.html")
        )

        records = list(iter_principal_records(tmp_path))

        assert len(records) == 1
        assert not isinstance(records[0], ParseFailure)

    def test_yields_parse_failure_when_parser_raises(self, tmp_path: Path):
        """A page that ParseError'd in the parser is captured as a
        ParseFailure, not allowed to crash the run."""
        # Bare empty page — no <h2 class="display-4">, no privacy-redacted
        # whitelist entry → principal_meta_parser raises ParseError.
        bogus_html = "<html><body><p>not a principal page</p></body></html>"
        _write_principal_checkpoint(tmp_path, 99998, html=bogus_html)

        records = list(iter_principal_records(tmp_path))

        assert len(records) == 1
        rec = records[0]
        assert isinstance(rec, ParseFailure)
        assert rec.entity_type == "principal"
        assert rec.entity_id == 99998
        assert rec.reason  # non-empty

    def test_iterates_in_principal_id_order(self, tmp_path: Path):
        """Multi-checkpoint dir yields records in ascending principal_id
        order — load-bearing for idempotent TSV output."""
        _write_principal_checkpoint(
            tmp_path, 12997, _load("principal_12997.html")
        )
        _write_principal_checkpoint(
            tmp_path, 11348, _load("principal_11348.html")
        )
        _write_principal_checkpoint(
            tmp_path, 11590, _load("principal_11590_populated.html")
        )

        records = list(iter_principal_records(tmp_path))

        ids = [rec[0].id for rec in records if not isinstance(rec, ParseFailure)]
        assert ids == ["WI-principal-11348", "WI-principal-11590", "WI-principal-12997"]

    def test_handles_empty_dir(self, tmp_path: Path):
        assert list(iter_principal_records(tmp_path)) == []

    def test_skips_non_numeric_filenames(self, tmp_path: Path):
        """Stray non-{id}.json files (e.g., logs or partial captures with
        suffixes) don't break iteration — same defense as the existing
        materializer."""
        (tmp_path / "README.json").write_text("{}", encoding="utf-8")
        _write_principal_checkpoint(
            tmp_path, 11590, _load("principal_11590_populated.html")
        )

        records = list(iter_principal_records(tmp_path))
        assert len(records) == 1


# ---------------------------------------------------------------------------
# iter_lobbyist_records
# ---------------------------------------------------------------------------


class TestIterLobbyistRecords:
    """Mirrors iter_principal_records on the lobbyist side. The key extra
    case is the ParseError → ParseFailure routing for soft-404 stub pages
    (e.g., Neumann-Ortiz 12717 on the 2026-05-26 snapshot)."""

    def test_yields_parsed_tuple_for_brooks_checkpoint(self, tmp_path: Path):
        _write_lobbyist_checkpoint(
            tmp_path, 11052, _load("lobbyist_11052_populated.html")
        )

        records = list(iter_lobbyist_records(tmp_path))

        assert len(records) == 1
        rec = records[0]
        assert not isinstance(rec, ParseFailure)
        person, filings = rec
        assert isinstance(person, Person)
        assert person.id == "WI-lobbyist-11052"
        assert len(filings) == 4  # 4 period columns always

    def test_soft_404_routes_to_parse_failure(self, tmp_path: Path):
        """A lobbyist page lacking the Time Report Summary section
        (soft-404 stub) raises ParseError in the parser; the iterator
        captures it as a ParseFailure with entity_type='lobbyist'."""
        _write_lobbyist_checkpoint(tmp_path, 12717, _SOFT_404_LOBBYIST_HTML)

        records = list(iter_lobbyist_records(tmp_path))

        assert len(records) == 1
        rec = records[0]
        assert isinstance(rec, ParseFailure)
        assert rec.entity_type == "lobbyist"
        assert rec.entity_id == 12717

    def test_skips_null_html_checkpoints_silently(self, tmp_path: Path):
        _write_lobbyist_checkpoint(tmp_path, 99999, html=None, status=404)
        _write_lobbyist_checkpoint(
            tmp_path, 11042, _load("lobbyist_11042.html")
        )

        records = list(iter_lobbyist_records(tmp_path))

        assert len(records) == 1
        assert not isinstance(records[0], ParseFailure)

    def test_iterates_in_lobbyist_id_order(self, tmp_path: Path):
        _write_lobbyist_checkpoint(
            tmp_path, 11052, _load("lobbyist_11052_populated.html")
        )
        _write_lobbyist_checkpoint(
            tmp_path, 11042, _load("lobbyist_11042.html")
        )

        records = list(iter_lobbyist_records(tmp_path))

        ids = [rec[0].id for rec in records if not isinstance(rec, ParseFailure)]
        assert ids == ["WI-lobbyist-11042", "WI-lobbyist-11052"]


# ---------------------------------------------------------------------------
# write_principals_tsv
# ---------------------------------------------------------------------------


_DAIRY_ORG = Organization(
    id="WI-principal-11590",
    name="Dairy Business Association",
    source_state="WI",
    contact_details=[
        ContactDetail(type="email", value="dairy@example.com"),
        ContactDetail(type="phone", value="608-555-0001"),
    ],
)


_WCTA_ORG = Organization(
    id="WI-principal-12997",
    name="Wisconsin County Treasurers Association",
    source_state="WI",
    contact_details=[],
)


def _dairy_extras() -> dict:
    return {
        "ceo_name": "Jane Doe",
        "business_or_interest": "Dairy community",
        "lobbying_interests_prose": "Dairy policy and farm regulations.",
    }


def _wcta_extras() -> dict:
    return {
        "ceo_name": None,
        "business_or_interest": "County treasurer affairs",
        "lobbying_interests_prose": "County treasurer policy advocacy.",
    }


class TestWritePrincipalsTsv:
    """Each row carries the Organization fields plus the side-channel
    extras (ceo_name / business_or_interest / lobbying_interests_prose).
    ``contact_details`` is JSON-serialized for round-trippable storage —
    a flat TSV column can't hold the list[ContactDetail] shape."""

    def test_schema(self, tmp_path: Path):
        rows = [(_DAIRY_ORG, _dairy_extras())]
        out = tmp_path / "principals.tsv"

        n = write_principals_tsv(rows, out)

        assert n == 1
        with out.open("r", encoding="utf-8", newline="") as fh:
            reader = csv.DictReader(fh, delimiter="\t")
            assert reader.fieldnames == [
                "principal_id",
                "id",
                "name",
                "source_state",
                "classification",
                "legal_form",
                "sector",
                "contact_details_json",
                "ceo_name",
                "business_or_interest",
                "lobbying_interests_prose",
            ]
            data = list(reader)
        assert data[0]["principal_id"] == "11590"
        assert data[0]["id"] == "WI-principal-11590"
        assert data[0]["name"] == "Dairy Business Association"
        assert data[0]["source_state"] == "WI"
        assert data[0]["ceo_name"] == "Jane Doe"

    def test_contact_details_serialized_as_json(self, tmp_path: Path):
        rows = [(_DAIRY_ORG, _dairy_extras())]
        out = tmp_path / "principals.tsv"

        write_principals_tsv(rows, out)

        with out.open("r", encoding="utf-8", newline="") as fh:
            reader = csv.DictReader(fh, delimiter="\t")
            row = next(reader)
        parsed = json.loads(row["contact_details_json"])
        assert isinstance(parsed, list)
        assert len(parsed) == 2
        # Order preserved from the Organization's contact_details list.
        assert parsed[0]["type"] == "email"
        assert parsed[0]["value"] == "dairy@example.com"
        assert parsed[1]["type"] == "phone"

    def test_empty_extras_serialize_as_empty_strings(self, tmp_path: Path):
        """None values in the extras dict (e.g., redacted or low-spend
        partial-disclosure principals) serialize as empty TSV cells, not
        the literal string 'None'."""
        extras = {
            "ceo_name": None,
            "business_or_interest": None,
            "lobbying_interests_prose": None,
        }
        rows = [(_WCTA_ORG, extras)]
        out = tmp_path / "principals.tsv"

        write_principals_tsv(rows, out)

        with out.open("r", encoding="utf-8", newline="") as fh:
            reader = csv.DictReader(fh, delimiter="\t")
            row = next(reader)
        assert row["ceo_name"] == ""
        assert row["business_or_interest"] == ""
        assert row["lobbying_interests_prose"] == ""

    def test_sorted_by_principal_id(self, tmp_path: Path):
        rows = [
            (_WCTA_ORG, _wcta_extras()),
            (_DAIRY_ORG, _dairy_extras()),
        ]
        out = tmp_path / "principals.tsv"

        write_principals_tsv(rows, out)

        with out.open("r", encoding="utf-8", newline="") as fh:
            reader = csv.DictReader(fh, delimiter="\t")
            data = list(reader)
        assert [r["principal_id"] for r in data] == ["11590", "12997"]


# ---------------------------------------------------------------------------
# write_lobbyists_tsv
# ---------------------------------------------------------------------------


_BROOKS_PERSON = Person(
    id="WI-lobbyist-11052",
    name="Bryan Brooks",
    source_state="WI",
    contact_details=[
        ContactDetail(type="email", value="bryan@example.com"),
    ],
)


_PFAFF_PERSON = Person(
    id="WI-lobbyist-11042",
    name="Shawn Pfaff",
    source_state="WI",
    contact_details=[],
)


class TestWriteLobbyistsTsv:
    def test_schema(self, tmp_path: Path):
        rows = [_BROOKS_PERSON]
        out = tmp_path / "lobbyists.tsv"

        n = write_lobbyists_tsv(rows, out)

        assert n == 1
        with out.open("r", encoding="utf-8", newline="") as fh:
            reader = csv.DictReader(fh, delimiter="\t")
            assert reader.fieldnames == [
                "lobbyist_id",
                "id",
                "name",
                "source_state",
                "contact_details_json",
            ]
            data = list(reader)
        assert data[0]["lobbyist_id"] == "11052"
        assert data[0]["id"] == "WI-lobbyist-11052"
        assert data[0]["name"] == "Bryan Brooks"

    def test_sorted_by_lobbyist_id(self, tmp_path: Path):
        rows = [_BROOKS_PERSON, _PFAFF_PERSON]  # input order: 11052, 11042
        out = tmp_path / "lobbyists.tsv"

        write_lobbyists_tsv(rows, out)

        with out.open("r", encoding="utf-8", newline="") as fh:
            reader = csv.DictReader(fh, delimiter="\t")
            data = list(reader)
        assert [r["lobbyist_id"] for r in data] == ["11042", "11052"]


# ---------------------------------------------------------------------------
# write_principal_filings_tsv
# ---------------------------------------------------------------------------


def _make_principal_filing(
    principal_id: int,
    year: int,
    half: str,
    expenditure: float | None = 100.0,
    hrs_comm: float | None = 10.0,
    hrs_other: float | None = 20.0,
) -> LobbyingFiling:
    if half == "H1":
        start = date(year, 1, 1)
        end = date(year, 6, 30)
    else:
        start = date(year, 7, 1)
        end = date(year, 12, 31)
    return LobbyingFiling(
        id=f"WI-principal-{principal_id}-expenditure-{year}-{half}",
        state="WI",
        filing_type="expenditure_report",
        filer_organization=Organization(
            id=f"WI-principal-{principal_id}",
            name=f"Principal {principal_id}",
            source_state="WI",
        ),
        filer_role="client",
        reporting_period_start=start,
        reporting_period_end=end,
        total_expenditure=expenditure,
        total_hours_communicating=hrs_comm,
        total_hours_other=hrs_other,
        provenance=Provenance(
            source_url=(
                "https://lobbying.wi.gov/Who/PrincipalInformation/2025REG/Information/"
                f"{principal_id}"
            ),
            extracted_at=datetime(2026, 5, 26, 12, 0, tzinfo=timezone.utc),
            extraction_method="direct_copy",
        ),
    )


class TestWritePrincipalFilingsTsv:
    def test_schema(self, tmp_path: Path):
        rows = [_make_principal_filing(11590, 2025, "H1")]
        out = tmp_path / "principal_filings.tsv"

        n = write_principal_filings_tsv(rows, out)

        assert n == 1
        with out.open("r", encoding="utf-8", newline="") as fh:
            reader = csv.DictReader(fh, delimiter="\t")
            assert reader.fieldnames == [
                "filing_id",
                "principal_id",
                "state",
                "filing_type",
                "filer_role",
                "reporting_period_start",
                "reporting_period_end",
                "total_expenditure",
                "total_hours_communicating",
                "total_hours_other",
                "source_url",
            ]
            data = list(reader)
        row = data[0]
        assert row["filing_id"] == "WI-principal-11590-expenditure-2025-H1"
        assert row["principal_id"] == "11590"
        assert row["state"] == "WI"
        assert row["filing_type"] == "expenditure_report"
        assert row["filer_role"] == "client"
        assert row["reporting_period_start"] == "2025-01-01"
        assert row["reporting_period_end"] == "2025-06-30"
        assert row["total_expenditure"] == "100.0"
        assert row["total_hours_communicating"] == "10.0"
        assert row["total_hours_other"] == "20.0"
        assert "PrincipalInformation" in row["source_url"]
        assert "11590" in row["source_url"]

    def test_none_values_serialize_as_empty(self, tmp_path: Path):
        rows = [
            _make_principal_filing(
                11590, 2025, "H1",
                expenditure=None, hrs_comm=None, hrs_other=None,
            )
        ]
        out = tmp_path / "principal_filings.tsv"

        write_principal_filings_tsv(rows, out)

        with out.open("r", encoding="utf-8", newline="") as fh:
            row = next(csv.DictReader(fh, delimiter="\t"))
        assert row["total_expenditure"] == ""
        assert row["total_hours_communicating"] == ""
        assert row["total_hours_other"] == ""

    def test_zero_values_serialize_as_zero_not_empty(self, tmp_path: Path):
        """WCTA-style low-spend exempt filings file 0.00 explicitly — zero
        is real data, distinct from missing."""
        rows = [
            _make_principal_filing(
                12997, 2025, "H1",
                expenditure=0.0, hrs_comm=0.0, hrs_other=0.0,
            )
        ]
        out = tmp_path / "principal_filings.tsv"

        write_principal_filings_tsv(rows, out)

        with out.open("r", encoding="utf-8", newline="") as fh:
            row = next(csv.DictReader(fh, delimiter="\t"))
        assert row["total_expenditure"] == "0.0"
        assert row["total_hours_communicating"] == "0.0"
        assert row["total_hours_other"] == "0.0"

    def test_sorted_by_principal_id_then_period(self, tmp_path: Path):
        rows = [
            _make_principal_filing(12997, 2025, "H2"),
            _make_principal_filing(11590, 2025, "H2"),
            _make_principal_filing(11590, 2025, "H1"),
            _make_principal_filing(12997, 2025, "H1"),
        ]
        out = tmp_path / "principal_filings.tsv"

        write_principal_filings_tsv(rows, out)

        with out.open("r", encoding="utf-8", newline="") as fh:
            data = list(csv.DictReader(fh, delimiter="\t"))
        # (principal_id, reporting_period_start) ascending.
        assert [(r["principal_id"], r["reporting_period_start"]) for r in data] == [
            ("11590", "2025-01-01"),
            ("11590", "2025-07-01"),
            ("12997", "2025-01-01"),
            ("12997", "2025-07-01"),
        ]


# ---------------------------------------------------------------------------
# write_lobbyist_filings_tsv
# ---------------------------------------------------------------------------


def _make_lobbyist_filing(
    lobbyist_id: int,
    year: int,
    half: str,
    hrs_comm: float | None = 10.0,
    hrs_other: float | None = 20.0,
) -> LobbyingFiling:
    if half == "H1":
        start = date(year, 1, 1)
        end = date(year, 6, 30)
    else:
        start = date(year, 7, 1)
        end = date(year, 12, 31)
    return LobbyingFiling(
        id=f"WI-lobbyist-{lobbyist_id}-activity-{year}-{half}",
        state="WI",
        filing_type="activity_report",
        filer_person=Person(
            id=f"WI-lobbyist-{lobbyist_id}",
            name=f"Lobbyist {lobbyist_id}",
            source_state="WI",
        ),
        filer_role="lobbyist",
        reporting_period_start=start,
        reporting_period_end=end,
        total_hours_communicating=hrs_comm,
        total_hours_other=hrs_other,
        provenance=Provenance(
            source_url=(
                "https://lobbying.wi.gov/Who/LobbyistInformation/2025REG/Information/"
                f"{lobbyist_id}"
            ),
            extracted_at=datetime(2026, 5, 26, 12, 0, tzinfo=timezone.utc),
            extraction_method="direct_copy",
        ),
    )


class TestWriteLobbyistFilingsTsv:
    def test_schema(self, tmp_path: Path):
        rows = [_make_lobbyist_filing(11052, 2025, "H1")]
        out = tmp_path / "lobbyist_filings.tsv"

        n = write_lobbyist_filings_tsv(rows, out)

        assert n == 1
        with out.open("r", encoding="utf-8", newline="") as fh:
            reader = csv.DictReader(fh, delimiter="\t")
            assert reader.fieldnames == [
                "filing_id",
                "lobbyist_id",
                "state",
                "filing_type",
                "filer_role",
                "reporting_period_start",
                "reporting_period_end",
                "total_hours_communicating",
                "total_hours_other",
                "source_url",
            ]
            data = list(reader)
        row = data[0]
        assert row["filing_id"] == "WI-lobbyist-11052-activity-2025-H1"
        assert row["lobbyist_id"] == "11052"
        assert row["filing_type"] == "activity_report"
        assert row["filer_role"] == "lobbyist"
        assert "LobbyistInformation" in row["source_url"]
        assert "11052" in row["source_url"]

    def test_sorted_by_lobbyist_id_then_period(self, tmp_path: Path):
        rows = [
            _make_lobbyist_filing(11052, 2026, "H1"),
            _make_lobbyist_filing(11042, 2025, "H2"),
            _make_lobbyist_filing(11052, 2025, "H1"),
            _make_lobbyist_filing(11042, 2025, "H1"),
        ]
        out = tmp_path / "lobbyist_filings.tsv"

        write_lobbyist_filings_tsv(rows, out)

        with out.open("r", encoding="utf-8", newline="") as fh:
            data = list(csv.DictReader(fh, delimiter="\t"))
        assert [(r["lobbyist_id"], r["reporting_period_start"]) for r in data] == [
            ("11042", "2025-01-01"),
            ("11042", "2025-07-01"),
            ("11052", "2025-01-01"),
            ("11052", "2026-01-01"),
        ]


# ---------------------------------------------------------------------------
# write_principal_bill_efforts_tsv
# ---------------------------------------------------------------------------


_AB30_2025H1 = {
    "principal_id": 11590,
    "bucket": "Legislative Bills/Resolutions",
    "item_id": "24598",
    "item_name": "Assembly Bill 30",
    "item_description": "Relating to: licensing of dairy farms.",
    "period_label": "2025 January - June",
    "percent": "2%",
}


_AB30_2025H2 = {
    "principal_id": 11590,
    "bucket": "Legislative Bills/Resolutions",
    "item_id": "24598",
    "item_name": "Assembly Bill 30",
    "item_description": "Relating to: licensing of dairy farms.",
    "period_label": "2025 July - December",
    "percent": "5%",
}


_TOPIC_LEXIA = {
    "principal_id": 11348,
    "bucket": "Topics Not Yet Assigned A Bill Or Rule Number",
    "item_id": "9999",
    "item_name": "Generic topic",
    "item_description": None,
    "period_label": "2025 January - June",
    "percent": "100%",
}


class TestWritePrincipalBillEffortsTsv:
    def test_schema(self, tmp_path: Path):
        rows = [_AB30_2025H1]
        out = tmp_path / "bill_efforts.tsv"

        n = write_principal_bill_efforts_tsv(rows, out)

        assert n == 1
        with out.open("r", encoding="utf-8", newline="") as fh:
            reader = csv.DictReader(fh, delimiter="\t")
            assert reader.fieldnames == [
                "principal_id",
                "bucket",
                "item_id",
                "item_name",
                "item_description",
                "period_label",
                "percent",
            ]
            data = list(reader)
        row = data[0]
        assert row["principal_id"] == "11590"
        assert row["bucket"] == "Legislative Bills/Resolutions"
        assert row["item_id"] == "24598"
        assert row["item_name"] == "Assembly Bill 30"
        assert row["item_description"] == "Relating to: licensing of dairy farms."
        assert row["period_label"] == "2025 January - June"
        assert row["percent"] == "2%"

    def test_none_item_description_serializes_as_empty(self, tmp_path: Path):
        """Topics-Not-Yet-Assigned items have no 'Relating to:' prose →
        ``item_description=None`` per the parser. Serializes as empty
        cell, not 'None'."""
        out = tmp_path / "bill_efforts.tsv"
        write_principal_bill_efforts_tsv([_TOPIC_LEXIA], out)

        with out.open("r", encoding="utf-8", newline="") as fh:
            row = next(csv.DictReader(fh, delimiter="\t"))
        assert row["item_description"] == ""

    def test_sorted_for_determinism(self, tmp_path: Path):
        """Sorted by (principal_id, bucket, item_id, period_label)."""
        rows = [_AB30_2025H2, _TOPIC_LEXIA, _AB30_2025H1]
        out = tmp_path / "bill_efforts.tsv"

        write_principal_bill_efforts_tsv(rows, out)

        with out.open("r", encoding="utf-8", newline="") as fh:
            data = list(csv.DictReader(fh, delimiter="\t"))
        keys = [(r["principal_id"], r["item_id"], r["period_label"]) for r in data]
        # Lexia 11348 < Dairy 11590; within Dairy, H1 < H2 by period_label.
        assert keys == [
            ("11348", "9999", "2025 January - June"),
            ("11590", "24598", "2025 January - June"),
            ("11590", "24598", "2025 July - December"),
        ]


# ---------------------------------------------------------------------------
# write_parse_failures_tsv
# ---------------------------------------------------------------------------


class TestWriteParseFailuresTsv:
    """The parse-failures TSV is the warnings channel: parser raised
    ParseError on a specific entity, materializer kept going, and the row
    is recorded here so a downstream consumer can see how many pages
    didn't parse and why."""

    def test_schema(self, tmp_path: Path):
        failures = [
            ParseFailure(entity_type="lobbyist", entity_id=12717, reason="soft_404"),
        ]
        out = tmp_path / "_tier_2_parse_failures.tsv"

        n = write_parse_failures_tsv(failures, out)

        assert n == 1
        with out.open("r", encoding="utf-8", newline="") as fh:
            reader = csv.DictReader(fh, delimiter="\t")
            assert reader.fieldnames == ["entity_type", "entity_id", "reason"]
            data = list(reader)
        row = data[0]
        assert row["entity_type"] == "lobbyist"
        assert row["entity_id"] == "12717"
        assert row["reason"] == "soft_404"

    def test_writes_empty_file_with_header_when_no_failures(self, tmp_path: Path):
        """Zero failures still writes the file with the header row — so a
        downstream consumer can ``ls _tier_2_parse_failures.tsv`` and know
        the materializer ran (vs. crashed before writing)."""
        out = tmp_path / "_tier_2_parse_failures.tsv"

        n = write_parse_failures_tsv([], out)

        assert n == 0
        assert out.exists()
        with out.open("r", encoding="utf-8", newline="") as fh:
            reader = csv.DictReader(fh, delimiter="\t")
            assert reader.fieldnames == ["entity_type", "entity_id", "reason"]
            assert list(reader) == []

    def test_sorted_by_entity_type_then_id(self, tmp_path: Path):
        failures = [
            ParseFailure(entity_type="principal", entity_id=99998, reason="x"),
            ParseFailure(entity_type="lobbyist", entity_id=12717, reason="y"),
            ParseFailure(entity_type="lobbyist", entity_id=11000, reason="z"),
        ]
        out = tmp_path / "_tier_2_parse_failures.tsv"

        write_parse_failures_tsv(failures, out)

        with out.open("r", encoding="utf-8", newline="") as fh:
            data = list(csv.DictReader(fh, delimiter="\t"))
        assert [(r["entity_type"], r["entity_id"]) for r in data] == [
            ("lobbyist", "11000"),
            ("lobbyist", "12717"),
            ("principal", "99998"),
        ]


# ---------------------------------------------------------------------------
# materialize_tier_2 — end-to-end orchestrator
# ---------------------------------------------------------------------------


class TestMaterializeTier2EndToEnd:
    """Walks both checkpoint dirs, calls the parsers, writes all 6 output
    files. Returns a dict of row counts per file."""

    def test_emits_all_six_output_files(self, tmp_path: Path):
        principal_dir = tmp_path / "principals_in"
        lobbyist_dir = tmp_path / "lobbyists_in"
        output_dir = tmp_path / "out"
        principal_dir.mkdir()
        lobbyist_dir.mkdir()
        output_dir.mkdir()

        _write_principal_checkpoint(
            principal_dir, 11590, _load("principal_11590_populated.html")
        )
        _write_principal_checkpoint(
            principal_dir, 12997, _load("principal_12997.html")
        )
        _write_lobbyist_checkpoint(
            lobbyist_dir, 11052, _load("lobbyist_11052_populated.html")
        )

        counts = materialize_tier_2(principal_dir, lobbyist_dir, output_dir)

        assert (output_dir / "WI_principals.tsv").exists()
        assert (output_dir / "WI_lobbyists.tsv").exists()
        assert (output_dir / "WI_principal_filings.tsv").exists()
        assert (output_dir / "WI_lobbyist_filings.tsv").exists()
        assert (output_dir / "WI_principal_bill_efforts.tsv").exists()
        assert (output_dir / "_tier_2_parse_failures.tsv").exists()

        # Counts dict carries one key per output file.
        assert set(counts.keys()) == {
            "WI_principals.tsv",
            "WI_lobbyists.tsv",
            "WI_principal_filings.tsv",
            "WI_lobbyist_filings.tsv",
            "WI_principal_bill_efforts.tsv",
            "_tier_2_parse_failures.tsv",
        }
        assert counts["WI_principals.tsv"] == 2  # Dairy + WCTA
        assert counts["WI_lobbyists.tsv"] == 1   # Brooks
        assert counts["WI_principal_filings.tsv"] >= 3  # Dairy 2 + WCTA 2 → ≥3
        assert counts["WI_lobbyist_filings.tsv"] == 4   # Brooks: 4 periods
        # Dairy has populated bill-effort items; WCTA contributes none.
        assert counts["WI_principal_bill_efforts.tsv"] > 0
        assert counts["_tier_2_parse_failures.tsv"] == 0

    def test_dairy_known_values_round_trip_through_materializer(self, tmp_path: Path):
        """The plan's spot-check anchors (Dairy P1 = $37,840 / 158.50 / 307.00)
        must survive the materialize step intact."""
        principal_dir = tmp_path / "principals_in"
        lobbyist_dir = tmp_path / "lobbyists_in"
        output_dir = tmp_path / "out"
        principal_dir.mkdir()
        lobbyist_dir.mkdir()
        output_dir.mkdir()

        _write_principal_checkpoint(
            principal_dir, 11590, _load("principal_11590_populated.html")
        )

        materialize_tier_2(principal_dir, lobbyist_dir, output_dir)

        with (output_dir / "WI_principal_filings.tsv").open(
            "r", encoding="utf-8", newline=""
        ) as fh:
            rows = list(csv.DictReader(fh, delimiter="\t"))
        dairy_p1 = next(
            r for r in rows
            if r["principal_id"] == "11590" and r["reporting_period_start"] == "2025-01-01"
        )
        assert dairy_p1["total_expenditure"] == "37840.0"
        assert dairy_p1["total_hours_communicating"] == "158.5"
        assert dairy_p1["total_hours_other"] == "307.0"

    def test_parse_failures_routed_to_failures_tsv_not_crash(self, tmp_path: Path):
        """A soft-404 lobbyist page does NOT crash the run; the failure
        appears in _tier_2_parse_failures.tsv and other rows still flow
        through normally."""
        principal_dir = tmp_path / "principals_in"
        lobbyist_dir = tmp_path / "lobbyists_in"
        output_dir = tmp_path / "out"
        principal_dir.mkdir()
        lobbyist_dir.mkdir()
        output_dir.mkdir()

        _write_lobbyist_checkpoint(lobbyist_dir, 12717, _SOFT_404_LOBBYIST_HTML)
        _write_lobbyist_checkpoint(
            lobbyist_dir, 11052, _load("lobbyist_11052_populated.html")
        )

        counts = materialize_tier_2(principal_dir, lobbyist_dir, output_dir)

        assert counts["_tier_2_parse_failures.tsv"] == 1
        assert counts["WI_lobbyists.tsv"] == 1  # Brooks still landed
        with (output_dir / "_tier_2_parse_failures.tsv").open(
            "r", encoding="utf-8", newline=""
        ) as fh:
            failures = list(csv.DictReader(fh, delimiter="\t"))
        assert failures[0]["entity_type"] == "lobbyist"
        assert failures[0]["entity_id"] == "12717"

    def test_id_scheme_follows_wi_role_id_convention(self, tmp_path: Path):
        """``Organization.id`` is ``WI-principal-{id}`` and ``Person.id``
        is ``WI-lobbyist-{id}`` in the TSV output, matching the
        plan-locked entity-ID convention."""
        principal_dir = tmp_path / "principals_in"
        lobbyist_dir = tmp_path / "lobbyists_in"
        output_dir = tmp_path / "out"
        principal_dir.mkdir()
        lobbyist_dir.mkdir()
        output_dir.mkdir()

        _write_principal_checkpoint(
            principal_dir, 11590, _load("principal_11590_populated.html")
        )
        _write_lobbyist_checkpoint(
            lobbyist_dir, 11052, _load("lobbyist_11052_populated.html")
        )

        materialize_tier_2(principal_dir, lobbyist_dir, output_dir)

        with (output_dir / "WI_principals.tsv").open(
            "r", encoding="utf-8", newline=""
        ) as fh:
            principals = list(csv.DictReader(fh, delimiter="\t"))
        with (output_dir / "WI_lobbyists.tsv").open(
            "r", encoding="utf-8", newline=""
        ) as fh:
            lobbyists = list(csv.DictReader(fh, delimiter="\t"))
        assert principals[0]["id"] == "WI-principal-11590"
        assert lobbyists[0]["id"] == "WI-lobbyist-11052"

    def test_principal_id_column_joins_with_authorizations_tsv(
        self, tmp_path: Path
    ):
        """Materialize output joins with the existing
        WI_lobbyist_principal_authorizations.tsv on ``principal_id``
        (bare int) and ``lobbyist_id`` (bare int). The integer columns
        must be there and parsable as ints — load-bearing for downstream
        graph analysis joining authorizations to per-period totals."""
        principal_dir = tmp_path / "principals_in"
        lobbyist_dir = tmp_path / "lobbyists_in"
        output_dir = tmp_path / "out"
        principal_dir.mkdir()
        lobbyist_dir.mkdir()
        output_dir.mkdir()

        _write_principal_checkpoint(
            principal_dir, 11590, _load("principal_11590_populated.html")
        )
        _write_lobbyist_checkpoint(
            lobbyist_dir, 11052, _load("lobbyist_11052_populated.html")
        )

        materialize_tier_2(principal_dir, lobbyist_dir, output_dir)

        with (output_dir / "WI_principal_filings.tsv").open(
            "r", encoding="utf-8", newline=""
        ) as fh:
            principal_filings = list(csv.DictReader(fh, delimiter="\t"))
        with (output_dir / "WI_lobbyist_filings.tsv").open(
            "r", encoding="utf-8", newline=""
        ) as fh:
            lobbyist_filings = list(csv.DictReader(fh, delimiter="\t"))
        # principal_id / lobbyist_id columns parse cleanly as ints.
        assert all(int(r["principal_id"]) for r in principal_filings)
        assert all(int(r["lobbyist_id"]) for r in lobbyist_filings)


# ---------------------------------------------------------------------------
# Idempotency
# ---------------------------------------------------------------------------


class TestIdempotency:
    """Re-running the materializer against the same checkpoint dir produces
    byte-identical TSVs. This is load-bearing: the parsers stamp
    ``datetime.now(timezone.utc)`` into provenance, so anything that
    survives into the TSV breaks byte-identity. The TSV schemas omit
    extracted_at for this reason."""

    def test_repeated_runs_produce_byte_identical_output(self, tmp_path: Path):
        principal_dir = tmp_path / "principals_in"
        lobbyist_dir = tmp_path / "lobbyists_in"
        output_a = tmp_path / "out_a"
        output_b = tmp_path / "out_b"
        for d in (principal_dir, lobbyist_dir, output_a, output_b):
            d.mkdir()

        _write_principal_checkpoint(
            principal_dir, 11590, _load("principal_11590_populated.html")
        )
        _write_principal_checkpoint(
            principal_dir, 12997, _load("principal_12997.html")
        )
        _write_lobbyist_checkpoint(
            lobbyist_dir, 11052, _load("lobbyist_11052_populated.html")
        )
        _write_lobbyist_checkpoint(
            lobbyist_dir, 11042, _load("lobbyist_11042.html")
        )

        materialize_tier_2(principal_dir, lobbyist_dir, output_a)
        materialize_tier_2(principal_dir, lobbyist_dir, output_b)

        for name in (
            "WI_principals.tsv",
            "WI_lobbyists.tsv",
            "WI_principal_filings.tsv",
            "WI_lobbyist_filings.tsv",
            "WI_principal_bill_efforts.tsv",
            "_tier_2_parse_failures.tsv",
        ):
            assert (output_a / name).read_bytes() == (output_b / name).read_bytes(), (
                f"Mismatch in {name} between consecutive runs"
            )
