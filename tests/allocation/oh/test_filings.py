"""Phase 3.5 — filings-level composer tests for OH.

Plan reference: ``docs/active/oh-portal-extraction/plans/20260611_oh_chain_composer_design.md`` §5 Phase 3.5.

Covers the two findings-doc normalizations:

1. **Stated-zero:** ``(total_expenditure is None AND len(expenditures) == 0)``
   normalizes ``total_expenditure → 0.0`` so nil filings aggregate
   correctly downstream.
2. **is_current default-forcing:** ``(filing_action == 'original' AND
   supersedes is None)`` forces ``is_current → True``. The original/no-
   supersedes pair structurally implies "this is the latest version";
   the AER extraction sometimes leaves the field default-unset.

Conservation: one row per canonical extraction (so the row count equals
the number of canonical filings, not the cache size).
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest

from lobby_analysis.allocation.oh.filings import (
    FILINGS_COLUMNS,
    compose_filings,
)


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
    filing_action: str = "original",
    is_current: bool = True,
    supersedes: str | None = None,
    total_expenditure: float | None = None,
    expenditures: list[dict] | None = None,
    extraction_warnings: list[str] | None = None,
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
        "filing_action": filing_action,
        "is_current": is_current,
        "supersedes": supersedes,
        "total_expenditure": total_expenditure,
        "positions": [],
        "expenditures": expenditures or [],
        "engagements": [],
        "gifts": [],
        "extraction_warnings": extraction_warnings or [],
    }


@pytest.fixture
def three_filing_fixture(tmp_path: Path) -> Path:
    """3 filings exercising the two normalizations + one populated control:

    Filing A — nil/zero: total_expenditure=None + expenditures=[] →
               after normalize, total_expenditure=0.0
    Filing B — populated: total_expenditure=1234.56 + expenditures=[...] →
               no normalize, total_expenditure unchanged
    Filing C — supersession-shaped: filing_action='amendment',
               supersedes='OLD_FID' → is_current must NOT be forced
               (only original+no-supersedes gets forced True)
    """
    root = tmp_path / "extractions"

    _write_filing(
        root,
        "A",
        "ha",
        _make_filing(
            "FID_A",
            principal_name="Acme",
            total_expenditure=None,
            expenditures=[],
        ),
    )

    _write_filing(
        root,
        "B",
        "hb",
        _make_filing(
            "FID_B",
            principal_name="Beacon",
            total_expenditure=1234.56,
            expenditures=[
                {"category": "compensation", "amount": 1234.56, "currency": "USD"}
            ],
        ),
    )

    _write_filing(
        root,
        "C",
        "hc",
        _make_filing(
            "FID_C",
            principal_name="Civic",
            filing_action="amendment",
            is_current=False,
            supersedes="FID_C_PRIOR",
            total_expenditure=500.0,
        ),
    )

    return root


# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------


class TestSchema:
    def test_filings_columns_constant_present(self) -> None:
        for col in (
            "filing_id",
            "report_period",
            "principal_name",
            "principal_id",
            "lobbyist_name",
            "lobbyist_id",
            "total_expenditure",
            "is_current",
            "filing_action",
            "supersedes",
            "n_positions",
            "n_gifts",
            "n_expenditures",
            "extraction_warnings",
        ):
            assert col in FILINGS_COLUMNS

    def test_output_columns_match_constant(self, three_filing_fixture: Path) -> None:
        df = compose_filings(three_filing_fixture)
        assert list(df.columns) == list(FILINGS_COLUMNS)

    def test_empty_input_returns_empty_with_full_columns(self, tmp_path: Path) -> None:
        ext = tmp_path / "empty"
        ext.mkdir()
        df = compose_filings(ext)
        assert len(df) == 0
        assert list(df.columns) == list(FILINGS_COLUMNS)


# ---------------------------------------------------------------------------
# Row count = canonical filings
# ---------------------------------------------------------------------------


class TestRowCount:
    def test_one_row_per_filing(self, three_filing_fixture: Path) -> None:
        df = compose_filings(three_filing_fixture)
        assert len(df) == 3
        assert set(df["filing_id"]) == {"FID_A", "FID_B", "FID_C"}


# ---------------------------------------------------------------------------
# Stated-zero normalization
# ---------------------------------------------------------------------------


class TestStatedZeroNormalization:
    def test_nil_filing_total_expenditure_normalizes_to_zero(
        self, three_filing_fixture: Path
    ) -> None:
        df = compose_filings(three_filing_fixture)
        row = df[df["filing_id"] == "FID_A"].iloc[0]
        assert row["total_expenditure"] == 0.0

    def test_populated_filing_total_expenditure_unchanged(
        self, three_filing_fixture: Path
    ) -> None:
        df = compose_filings(three_filing_fixture)
        row = df[df["filing_id"] == "FID_B"].iloc[0]
        assert row["total_expenditure"] == 1234.56

    def test_no_row_has_null_total_expenditure_after_normalize(
        self, three_filing_fixture: Path
    ) -> None:
        """The post-normalize invariant: every filing has a numeric
        total_expenditure (never null). Downstream SUM aggregations are
        safe without coalescing."""
        df = compose_filings(three_filing_fixture)
        assert df["total_expenditure"].notna().all()

    def test_none_with_non_empty_expenditures_NOT_normalized(
        self, tmp_path: Path
    ) -> None:
        """Only the (None, empty) pair normalizes. If total_expenditure is
        None but expenditures are NON-empty, that's an upstream extraction
        inconsistency — don't silently coerce to 0.0; leave as null so
        analysts see the defect."""
        root = tmp_path / "extractions"
        _write_filing(
            root,
            "X",
            "hx",
            _make_filing(
                "FID_X",
                total_expenditure=None,
                expenditures=[
                    {"category": "compensation", "amount": 999.0, "currency": "USD"}
                ],
            ),
        )
        df = compose_filings(root)
        row = df.iloc[0]
        # NOT normalized to 0.0 — the (None, non-empty) pair is a defect.
        assert pd.isna(row["total_expenditure"])


# ---------------------------------------------------------------------------
# is_current forcing
# ---------------------------------------------------------------------------


class TestIsCurrentForcing:
    def test_original_no_supersedes_forces_is_current_true(
        self, tmp_path: Path
    ) -> None:
        """Filing structurally is the latest version (no supersession);
        is_current is forced True even if the extraction left it
        default-unset (False)."""
        root = tmp_path / "extractions"
        _write_filing(
            root,
            "Y",
            "hy",
            _make_filing(
                "FID_Y",
                filing_action="original",
                is_current=False,
                supersedes=None,
            ),
        )
        df = compose_filings(root)
        row = df.iloc[0]
        assert row["is_current"] is True or row["is_current"] == True  # noqa

    def test_supersession_shaped_filing_is_current_NOT_forced(
        self, three_filing_fixture: Path
    ) -> None:
        """Filing C has filing_action='amendment' AND supersedes='FID_C_PRIOR'.
        The forcing rule does NOT apply. is_current stays as extracted
        (False in the fixture)."""
        df = compose_filings(three_filing_fixture)
        row = df[df["filing_id"] == "FID_C"].iloc[0]
        assert row["is_current"] is False or row["is_current"] == False  # noqa

    def test_original_with_supersedes_NOT_forced(self, tmp_path: Path) -> None:
        """filing_action='original' AND supersedes='something' is a
        suspicious combination (typically supersedes is null for originals),
        but the forcing rule has both conjuncts — both must hold. If only
        one holds, don't force."""
        root = tmp_path / "extractions"
        _write_filing(
            root,
            "Z",
            "hz",
            _make_filing(
                "FID_Z",
                filing_action="original",
                is_current=False,
                supersedes="SOMETHING",
            ),
        )
        df = compose_filings(root)
        row = df.iloc[0]
        # NOT forced — supersedes is non-null
        assert row["is_current"] is False or row["is_current"] == False  # noqa


# ---------------------------------------------------------------------------
# Filing-grain summary stats
# ---------------------------------------------------------------------------


class TestSummaryStats:
    def test_n_expenditures_correct(self, three_filing_fixture: Path) -> None:
        df = compose_filings(three_filing_fixture)
        by_id = df.set_index("filing_id")
        assert by_id.loc["FID_A", "n_expenditures"] == 0
        assert by_id.loc["FID_B", "n_expenditures"] == 1
        assert by_id.loc["FID_C", "n_expenditures"] == 0

    def test_report_period_format(self, three_filing_fixture: Path) -> None:
        df = compose_filings(three_filing_fixture)
        assert (df["report_period"] == "2025-01-01..2025-04-30").all()

    def test_extraction_warnings_carried_through(self, tmp_path: Path) -> None:
        root = tmp_path / "extractions"
        _write_filing(
            root,
            "W",
            "hw",
            _make_filing(
                "FID_W",
                extraction_warnings=["odd_value_in_section_iv", "ambiguous_recipient"],
            ),
        )
        df = compose_filings(root)
        # Stored as a list or joined string — accept either as long as the
        # info is preserved.
        wrn = df.iloc[0]["extraction_warnings"]
        s = str(wrn)
        assert "odd_value_in_section_iv" in s
        assert "ambiguous_recipient" in s
