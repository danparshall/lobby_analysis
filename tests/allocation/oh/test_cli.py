"""Phase 4 — CLI materialize tests for OH.

Plan reference: ``docs/active/oh-portal-extraction/plans/20260611_oh_chain_composer_design.md`` §5 Phase 4.

Verifies that ``python -m lobby_analysis.allocation.oh.cli materialize`` writes
the three TSVs (chain, gifts, filings) under ``releases/oh/<grain>/`` with
the expected schema and content. Q1-locked filenames use the ``_preview``
suffix because the slice is non-representative.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

import pandas as pd
import pytest

from lobby_analysis.allocation.oh.cli import main


def _write_filing(extractions_dir: Path, dir_id: str, hash_: str, payload: dict) -> Path:
    subdir = extractions_dir / dir_id / hash_
    subdir.mkdir(parents=True, exist_ok=True)
    fp = subdir / "filing.json"
    fp.write_text(json.dumps(payload))
    return fp


def _make_filing(
    filing_id: str,
    *,
    principal_name: str = "Acme Corp",
    lobbyist_name: str = "Jane Doe",
    positions: list[dict] | None = None,
    gifts: list[dict] | None = None,
    total_expenditure: float | None = None,
) -> dict:
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
        "supersedes": None,
        "total_expenditure": total_expenditure,
        "positions": positions or [],
        "expenditures": [],
        "engagements": [],
        "gifts": gifts or [],
    }


@pytest.fixture
def cli_fixture(tmp_path: Path) -> dict[str, Path]:
    """One filing with 1 bill_referenced + 1 subject_only + 1 gift."""
    extractions = tmp_path / "extractions"
    plural = tmp_path / "plural" / "136"
    plural.mkdir(parents=True)
    out_dir = tmp_path / "releases" / "oh"
    oh_csv = tmp_path / "oh.csv"

    _write_filing(
        extractions,
        "1",
        "h1",
        _make_filing(
            "FID_CLI",
            principal_name="CLI Test",
            lobbyist_name="Test Lobbyist",
            positions=[
                {"bill_reference": {"original_text": "HB 1", "bill_number": "HB 1", "reference_type": "bill", "is_resolved": False}, "general_issue_area": None, "description": None},
                {"bill_reference": None, "general_issue_area": "Public Safety", "description": None},
            ],
            gifts=[
                {"recipient_name": "Sen. Adam Bird", "value": 15.0, "gift_type": "meal", "description": "coffee"},
            ],
            total_expenditure=None,
        ),
    )

    # Plural fixtures
    with (plural / "OH_136_bills.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["id", "identifier", "title", "classification", "subject", "session_identifier", "jurisdiction", "organization_classification"])
        w.writerow(["ocd-bill/hb-1", "HB 1", "Some bill", "['bill']", "", "136", "j", "lower"])
    with (plural / "OH_136_bill_sponsorships.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["id", "name", "entity_type", "organization_id", "person_id", "bill_id", "primary", "classification"])
        w.writerow(["sp1", "Rep. X", "person", "", "ocd-person/x", "ocd-bill/hb-1", "True", "primary"])

    # oh.csv
    with oh_csv.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["id", "name", "current_party", "current_district", "current_chamber", "given_name", "family_name"])
        w.writerow(["ocd-person/bird-id", "Adam Bird", "Republican", "63", "lower", "Adam", "Bird"])

    return {
        "extractions": extractions,
        "plural": plural,
        "oh_csv": oh_csv,
        "out_dir": out_dir,
    }


class TestMaterialize:
    def test_writes_three_tsvs(self, cli_fixture: dict[str, Path]) -> None:
        rc = main(
            [
                "materialize",
                "--extractions",
                str(cli_fixture["extractions"]),
                "--bills",
                str(cli_fixture["plural"]),
                "--oh-csv",
                str(cli_fixture["oh_csv"]),
                "--out",
                str(cli_fixture["out_dir"]),
            ]
        )
        assert rc == 0
        out = cli_fixture["out_dir"]
        assert (out / "chain" / "OH_chain_2025_2026_preview.tsv").exists()
        assert (out / "gifts" / "OH_gifts_2025_2026_preview.tsv").exists()
        assert (out / "filings" / "OH_filings_2025_2026_preview.tsv").exists()

    def test_chain_tsv_row_count_and_schema(self, cli_fixture: dict[str, Path]) -> None:
        main(
            [
                "materialize",
                "--extractions",
                str(cli_fixture["extractions"]),
                "--bills",
                str(cli_fixture["plural"]),
                "--oh-csv",
                str(cli_fixture["oh_csv"]),
                "--out",
                str(cli_fixture["out_dir"]),
            ]
        )
        chain = pd.read_csv(
            cli_fixture["out_dir"] / "chain" / "OH_chain_2025_2026_preview.tsv",
            sep="\t",
        )
        # 1 bill_referenced × 1 primary + 1 subject = 2 rows
        assert len(chain) == 2
        assert "bill_class" in chain.columns
        assert set(chain["bill_class"]) == {"bill", "subject"}

    def test_gifts_tsv_resolves_lawmaker_id(
        self, cli_fixture: dict[str, Path]
    ) -> None:
        main(
            [
                "materialize",
                "--extractions",
                str(cli_fixture["extractions"]),
                "--bills",
                str(cli_fixture["plural"]),
                "--oh-csv",
                str(cli_fixture["oh_csv"]),
                "--out",
                str(cli_fixture["out_dir"]),
            ]
        )
        gifts = pd.read_csv(
            cli_fixture["out_dir"] / "gifts" / "OH_gifts_2025_2026_preview.tsv",
            sep="\t",
        )
        assert len(gifts) == 1
        assert gifts.iloc[0]["lawmaker_id"] == "ocd-person/bird-id"
        assert gifts.iloc[0]["event_type"] == "meal"

    def test_filings_tsv_applies_normalizations(
        self, cli_fixture: dict[str, Path]
    ) -> None:
        main(
            [
                "materialize",
                "--extractions",
                str(cli_fixture["extractions"]),
                "--bills",
                str(cli_fixture["plural"]),
                "--oh-csv",
                str(cli_fixture["oh_csv"]),
                "--out",
                str(cli_fixture["out_dir"]),
            ]
        )
        filings = pd.read_csv(
            cli_fixture["out_dir"] / "filings" / "OH_filings_2025_2026_preview.tsv",
            sep="\t",
        )
        assert len(filings) == 1
        # Stated-zero normalization: total_expenditure was None, expenditures=[]
        # → normalized to 0.0
        assert filings.iloc[0]["total_expenditure"] == 0.0
        # is_current forcing: original + supersedes=null → True
        assert bool(filings.iloc[0]["is_current"]) is True

    def test_oh_csv_optional(self, cli_fixture: dict[str, Path]) -> None:
        """Omitting --oh-csv is supported; gifts then have null lawmaker_id."""
        rc = main(
            [
                "materialize",
                "--extractions",
                str(cli_fixture["extractions"]),
                "--bills",
                str(cli_fixture["plural"]),
                "--out",
                str(cli_fixture["out_dir"]),
            ]
        )
        assert rc == 0
        gifts = pd.read_csv(
            cli_fixture["out_dir"] / "gifts" / "OH_gifts_2025_2026_preview.tsv",
            sep="\t",
        )
        assert pd.isna(gifts.iloc[0]["lawmaker_id"])
