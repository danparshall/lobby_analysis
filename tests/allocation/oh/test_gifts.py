"""Phase 3 — gifts edge composer tests for OH.

Plan reference: ``docs/active/oh-portal-extraction/plans/20260611_oh_chain_composer_design.md`` §5 Phase 3.

Covers:

- Per-event row shape (1 row per (filing, gift)).
- Event-type derivation: ``gift_type == "meal"`` → ``event_type="meal"`` (Section II.B);
  all other gift_types → ``event_type="gift"`` (Section II.A).
- ``oh.csv`` lawmaker resolution: with the file present, recipient names like
  "Sen. John Smith" or "Rep. Jane Doe" resolve to ``ocd-person/...`` IDs.
  Without the file (None), ``lawmaker_id`` is always null.
- Conservation: every gift produces exactly one row.
- Empty-input contract: 0 filings → empty DataFrame with full column set.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

import pandas as pd
import pytest

from lobby_analysis.allocation.oh.gifts import GIFTS_COLUMNS, compose_gifts


def _write_filing(extractions_dir: Path, dir_id: str, hash_: str, payload: dict) -> Path:
    subdir = extractions_dir / dir_id / hash_
    subdir.mkdir(parents=True, exist_ok=True)
    fp = subdir / "filing.json"
    fp.write_text(json.dumps(payload))
    return fp


def _make_filing(filing_id: str, *, principal_name: str = "Acme Corp", lobbyist_name: str = "Jane Doe", gifts: list[dict] | None = None) -> dict:
    return {
        "id": f"filing-{filing_id}",
        "state": "OH",
        "filing_id": filing_id,
        "filing_type": "activity_report",
        "filer_person": {"id": f"person-{lobbyist_name.lower().replace(' ', '-')}", "name": lobbyist_name, "source_state": "OH"},
        "filer_role": "lobbyist",
        "employer": {"id": f"org-{principal_name.lower().replace(' ', '-')}", "name": principal_name, "source_state": "OH"},
        "reporting_period_start": "2025-01-01",
        "reporting_period_end": "2025-04-30",
        "filing_action": "original",
        "is_current": True,
        "positions": [],
        "expenditures": [],
        "engagements": [],
        "gifts": gifts or [],
    }


def _gift(
    recipient: str,
    value: float | None = 25.0,
    gift_type: str | None = "meal",
    description: str | None = "lunch at Capitol cafeteria",
    gift_date: str | None = "2025-02-15",
) -> dict:
    return {
        "recipient_name": recipient,
        "value": value,
        "gift_type": gift_type,
        "description": description,
        "gift_date": gift_date,
    }


@pytest.fixture
def gifts_fixture(tmp_path: Path) -> Path:
    """One filing with 4 gifts:
      - meal to Sen. Adam Bird   (Section II.B; resolves via oh.csv to Bird's ocd-person id)
      - event_ticket to Rep. Bea Cox (Section II.A → 'gift'; resolves)
      - travel to "John Smith"   (no prefix; resolves)
      - meal to Sen. Unknown Person (no oh.csv hit → lawmaker_id null)
    """
    ext = tmp_path / "extractions"
    _write_filing(
        ext,
        "1",
        "h1",
        _make_filing(
            "FID1",
            principal_name="Acme Corp",
            lobbyist_name="Jane Doe",
            gifts=[
                _gift("Sen. Adam Bird", value=20.0, gift_type="meal", description="dinner"),
                _gift("Rep. Bea Cox", value=75.0, gift_type="event_ticket", description="ballet ticket"),
                _gift("John Smith", value=12.0, gift_type="travel", description="ride to airport"),
                _gift("Sen. Unknown Person", value=10.0, gift_type="meal", description="coffee"),
            ],
        ),
    )
    return ext


@pytest.fixture
def oh_csv(tmp_path: Path) -> Path:
    fp = tmp_path / "oh.csv"
    with fp.open("w", newline="") as f:
        w = csv.writer(f)
        # Minimal schema mirroring the real oh.csv (id, name, family_name, current_chamber)
        w.writerow(["id", "name", "current_party", "current_district", "current_chamber", "given_name", "family_name"])
        w.writerow(["ocd-person/bird-id", "Adam Bird", "Republican", "63", "lower", "Adam", "Bird"])
        w.writerow(["ocd-person/cox-id", "Bea Cox", "Democrat", "12", "lower", "Bea", "Cox"])
        w.writerow(["ocd-person/smith-id", "John Smith", "Republican", "5", "upper", "John", "Smith"])
        # Adam Smith — a second Smith to test ambiguity handling
        w.writerow(["ocd-person/asmith-id", "Adam Smith", "Democrat", "10", "lower", "Adam", "Smith"])
    return fp


# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------


class TestSchema:
    def test_gifts_columns_constant_present(self) -> None:
        for col in (
            "report_period",
            "filing_id",
            "principal_name",
            "lobbyist_name",
            "lawmaker_name_raw",
            "lawmaker_id",
            "event_type",
            "description",
            "amount_dollars",
            "gift_date",
        ):
            assert col in GIFTS_COLUMNS

    def test_output_has_gifts_columns(self, gifts_fixture: Path, oh_csv: Path) -> None:
        df = compose_gifts(gifts_fixture, oh_csv)
        assert list(df.columns) == list(GIFTS_COLUMNS)

    def test_empty_input_returns_empty_with_full_columns(self, tmp_path: Path) -> None:
        ext = tmp_path / "extractions-empty"
        ext.mkdir()
        df = compose_gifts(ext, None)
        assert len(df) == 0
        assert list(df.columns) == list(GIFTS_COLUMNS)


# ---------------------------------------------------------------------------
# Row shape
# ---------------------------------------------------------------------------


class TestRowShape:
    def test_one_row_per_gift(self, gifts_fixture: Path, oh_csv: Path) -> None:
        df = compose_gifts(gifts_fixture, oh_csv)
        assert len(df) == 4

    def test_event_type_meal_for_meals(self, gifts_fixture: Path, oh_csv: Path) -> None:
        df = compose_gifts(gifts_fixture, oh_csv)
        meals = df[df["lawmaker_name_raw"].str.contains("Bird") | df["lawmaker_name_raw"].str.contains("Unknown")]
        assert len(meals) == 2
        assert (meals["event_type"] == "meal").all()

    def test_event_type_gift_for_non_meals(self, gifts_fixture: Path, oh_csv: Path) -> None:
        df = compose_gifts(gifts_fixture, oh_csv)
        non_meals = df[~df["lawmaker_name_raw"].str.contains("Bird") & ~df["lawmaker_name_raw"].str.contains("Unknown")]
        assert len(non_meals) == 2
        assert (non_meals["event_type"] == "gift").all()

    def test_filing_metadata_propagated(self, gifts_fixture: Path, oh_csv: Path) -> None:
        df = compose_gifts(gifts_fixture, oh_csv)
        assert (df["filing_id"] == "FID1").all()
        assert (df["principal_name"] == "Acme Corp").all()
        assert (df["lobbyist_name"] == "Jane Doe").all()
        assert (df["report_period"] == "2025-01-01..2025-04-30").all()

    def test_gift_fields_round_trip(self, gifts_fixture: Path, oh_csv: Path) -> None:
        df = compose_gifts(gifts_fixture, oh_csv)
        bird_row = df[df["lawmaker_name_raw"].str.contains("Bird")].iloc[0]
        assert bird_row["amount_dollars"] == 20.0
        assert bird_row["description"] == "dinner"


# ---------------------------------------------------------------------------
# Lawmaker resolution via oh.csv
# ---------------------------------------------------------------------------


class TestLawmakerResolution:
    def test_resolves_with_sen_prefix(self, gifts_fixture: Path, oh_csv: Path) -> None:
        df = compose_gifts(gifts_fixture, oh_csv)
        bird_row = df[df["lawmaker_name_raw"] == "Sen. Adam Bird"].iloc[0]
        assert bird_row["lawmaker_id"] == "ocd-person/bird-id"

    def test_resolves_with_rep_prefix(self, gifts_fixture: Path, oh_csv: Path) -> None:
        df = compose_gifts(gifts_fixture, oh_csv)
        cox_row = df[df["lawmaker_name_raw"] == "Rep. Bea Cox"].iloc[0]
        assert cox_row["lawmaker_id"] == "ocd-person/cox-id"

    def test_unknown_recipient_resolves_to_null(self, gifts_fixture: Path, oh_csv: Path) -> None:
        df = compose_gifts(gifts_fixture, oh_csv)
        unk_row = df[df["lawmaker_name_raw"] == "Sen. Unknown Person"].iloc[0]
        assert pd.isna(unk_row["lawmaker_id"])

    def test_oh_csv_none_means_all_ids_null(self, gifts_fixture: Path) -> None:
        df = compose_gifts(gifts_fixture, None)
        assert df["lawmaker_id"].isna().all()
        # But the raw name still survives
        assert (df["lawmaker_name_raw"] != "").all()

    def test_ambiguous_surname_resolves_to_null(self, tmp_path: Path, oh_csv: Path) -> None:
        """If two legislators share a surname and the recipient_name carries
        only the surname or a partial form that doesn't uniquely match, the
        resolver returns null (rather than picking arbitrarily).

        oh.csv has two Smiths (John Smith + Adam Smith). A gift to "Sen. Smith"
        cannot be uniquely resolved; lawmaker_id must be null."""
        ext = tmp_path / "extractions"
        _write_filing(
            ext,
            "2",
            "h2",
            _make_filing("FID2", gifts=[_gift("Sen. Smith", gift_type="meal")]),
        )
        df = compose_gifts(ext, oh_csv)
        assert len(df) == 1
        assert pd.isna(df.iloc[0]["lawmaker_id"])

    def test_no_prefix_full_name_resolves(self, gifts_fixture: Path, oh_csv: Path) -> None:
        """Recipient name without 'Sen./Rep.' prefix — 'John Smith' should
        still resolve to ocd-person/smith-id (unambiguous full-name match)."""
        df = compose_gifts(gifts_fixture, oh_csv)
        smith_row = df[df["lawmaker_name_raw"] == "John Smith"].iloc[0]
        assert smith_row["lawmaker_id"] == "ocd-person/smith-id"
