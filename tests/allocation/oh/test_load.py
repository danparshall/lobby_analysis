"""Phase 1 Step C — typed loader tests for the OH chain composer.

Tests are fixture-only (pure-logic; no real-cache dependency). The local
``conftest.py`` overrides the repo's autouse Postgres-dependent
``_truncate_filings`` fixture to a no-op.

Plan reference: ``docs/active/oh-portal-extraction/plans/20260611_oh_chain_composer_design.md`` §5 Phase 1.

Covers five loaders:

- :func:`load_filings` — one row per ``LobbyingFiling``
- :func:`load_positions` — one row per ``(filing, position)``; carries the
  ``LobbyingPosition`` model object for downstream classifier calls
- :func:`load_gifts` — one row per ``(filing, gift)`` (Phase 3 input)
- :func:`load_plural_bills` — one row per Plural Policy bill
- :func:`load_plural_sponsorships`(classification="primary" by default per Q2)
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

import pandas as pd
import pytest

from lobby_analysis.allocation.oh.load import (
    load_filings,
    load_gifts,
    load_plural_bills,
    load_plural_sponsorships,
    load_positions,
    select_canonical_extraction,
)
from lobby_analysis.models.entities import BillReference
from lobby_analysis.models.filings import Gift, LobbyingFiling, LobbyingPosition


# ---------------------------------------------------------------------------
# Fixtures — hand-crafted extractions and Plural Policy CSVs
# ---------------------------------------------------------------------------


def _write_filing(extractions_dir: Path, dir_id: str, hash_: str, payload: dict) -> Path:
    """Write a filing.json under extractions_dir/<dir_id>/<hash>/."""
    subdir = extractions_dir / dir_id / hash_
    subdir.mkdir(parents=True, exist_ok=True)
    fp = subdir / "filing.json"
    fp.write_text(json.dumps(payload))
    return fp


def _filing_dict(
    filing_id: str,
    *,
    principal_name: str = "Acme Corp",
    lobbyist_name: str = "Jane Doe",
    period_start: str = "2025-01-01",
    period_end: str = "2025-04-30",
    filing_action: str = "original",
    is_current: bool = True,
    supersedes: str | None = None,
    total_expenditure: float | None = None,
    positions: list[dict] | None = None,
    expenditures: list[dict] | None = None,
    gifts: list[dict] | None = None,
) -> dict:
    """Build a minimal LobbyingFiling JSON payload."""
    return {
        "id": f"filing-{filing_id}",
        "state": "OH",
        "filing_id": filing_id,
        "filing_type": "activity_report",
        "filer_person": {
            "id": f"person-{lobbyist_name.lower().replace(' ', '-')}",
            "name": lobbyist_name,
            "source_state": "OH",
        },
        "filer_role": "lobbyist",
        "employer": {
            "id": f"org-{principal_name.lower().replace(' ', '-')}",
            "name": principal_name,
            "source_state": "OH",
        },
        "reporting_period_start": period_start,
        "reporting_period_end": period_end,
        "filing_action": filing_action,
        "is_current": is_current,
        "supersedes": supersedes,
        "total_expenditure": total_expenditure,
        "positions": positions or [],
        "expenditures": expenditures or [],
        "gifts": gifts or [],
        "engagements": [],
    }


def _bill_ref_position(bill_text: str) -> dict:
    """Position carrying a bill_reference (Step A → bill_referenced)."""
    return {
        "bill_reference": {
            "original_text": bill_text,
            "bill_number": bill_text,
            "reference_type": "bill",
            "is_resolved": False,
        },
        "position": "support",
        "general_issue_area": None,
        "description": None,
    }


def _subject_general_position(issue_area: str) -> dict:
    """Position carrying only general_issue_area (Step A → subject_general)."""
    return {
        "bill_reference": None,
        "general_issue_area": issue_area,
        "description": None,
    }


def _subject_hoisted_position(description: str) -> dict:
    """Position with description only (Step A → subject_hoisted_from_description)."""
    return {
        "bill_reference": None,
        "general_issue_area": None,
        "description": description,
    }


def _gift_dict(recipient: str, amount: float, gift_type: str = "meal") -> dict:
    return {
        "recipient_name": recipient,
        "value": amount,
        "gift_type": gift_type,
    }


@pytest.fixture
def extractions_dir(tmp_path: Path) -> Path:
    """Hand-crafted extractions directory with 4 filings covering the §4a cases.

    Filing A — bill_referenced + subject_general (2 positions, 1 gift)
    Filing B — subject_hoisted_from_description only (1 position)
    Filing C — empty positions (stated-zero candidate; total_expenditure=None, no expenditures)
    Filing D — bill_referenced (1 position) + 2 gifts (Phase 3 coverage)
    """
    root = tmp_path / "extractions"

    # Filing A: 2 positions (1 bill_referenced, 1 subject_general), 1 gift
    _write_filing(
        root,
        "1000001",
        "hashA",
        _filing_dict(
            "20250314AAA1000001",
            principal_name="Acme Corp",
            lobbyist_name="Alice Anderson",
            positions=[
                _bill_ref_position("HB 96"),
                _subject_general_position("Public Safety"),
            ],
            gifts=[_gift_dict("Sen. Smith", 25.0, "meal")],
        ),
    )

    # Filing B: 1 subject_hoisted position (mini-quirk)
    _write_filing(
        root,
        "1000002",
        "hashB",
        _filing_dict(
            "20250314BBB1000002",
            principal_name="Beacon LLC",
            lobbyist_name="Bob Baker",
            positions=[_subject_hoisted_position("Education Policy")],
        ),
    )

    # Filing C: nil-zero expenditure (Phase 3.5 stated-zero case)
    _write_filing(
        root,
        "1000003",
        "hashC",
        _filing_dict(
            "20250314CCC1000003",
            principal_name="Civic Group",
            lobbyist_name="Carol Carter",
            total_expenditure=None,
            positions=[],
            expenditures=[],
        ),
    )

    # Filing D: 1 bill_referenced position + 2 gifts
    _write_filing(
        root,
        "1000004",
        "hashD",
        _filing_dict(
            "20250314DDD1000004",
            principal_name="Delta Inc",
            lobbyist_name="Dan Davis",
            positions=[_bill_ref_position("SB 2")],
            gifts=[
                _gift_dict("Rep. Jones", 12.50, "meal"),
                _gift_dict("Rep. Wilson", 50.0, "event_ticket"),
            ],
        ),
    )

    return root


@pytest.fixture
def plural_dir(tmp_path: Path) -> Path:
    """Hand-crafted Plural Policy directory with bills + sponsorships CSVs."""
    root = tmp_path / "plural" / "136"
    root.mkdir(parents=True)

    # OH_136_bills.csv — 3 bills
    with (root / "OH_136_bills.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(
            [
                "id",
                "identifier",
                "title",
                "classification",
                "subject",
                "session_identifier",
                "jurisdiction",
                "organization_classification",
            ]
        )
        w.writerow(
            [
                "ocd-bill/aaa-hb-96",
                "HB 96",
                "FY 2026-27 state operating budget.",
                "['bill']",
                "['Budget']",
                "136",
                "ocd-jurisdiction/country:us/state:oh/government",
                "lower",
            ]
        )
        w.writerow(
            [
                "ocd-bill/bbb-sb-2",
                "SB 2",
                "Energy generation.",
                "['bill']",
                "['Energy']",
                "136",
                "ocd-jurisdiction/country:us/state:oh/government",
                "upper",
            ]
        )
        w.writerow(
            [
                "ocd-bill/ccc-hr-369",
                "HR 369",
                "In memory of L. Helen Rankin.",
                "['resolution']",
                "['Memorial']",
                "136",
                "ocd-jurisdiction/country:us/state:oh/government",
                "lower",
            ]
        )

    # OH_136_bill_sponsorships.csv — 6 rows
    #   HB 96: 2 primaries (multi-primary), 1 cosponsor
    #   SB 2:  1 primary
    #   HR 369: 1 primary (truncated; real bill has 99)
    #   one extra cosponsor on SB 2
    with (root / "OH_136_bill_sponsorships.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(
            [
                "id",
                "name",
                "entity_type",
                "organization_id",
                "person_id",
                "bill_id",
                "primary",
                "classification",
            ]
        )
        w.writerow(["sp1", "Rep. Adam Bird", "person", "", "ocd-person/aaa-bird", "ocd-bill/aaa-hb-96", "True", "primary"])
        w.writerow(["sp2", "Rep. Bea Cox", "person", "", "ocd-person/bbb-cox", "ocd-bill/aaa-hb-96", "True", "primary"])
        w.writerow(["sp3", "Rep. Cy Dane", "person", "", "ocd-person/ccc-dane", "ocd-bill/aaa-hb-96", "False", "cosponsor"])
        w.writerow(["sp4", "Sen. Don Earl", "person", "", "ocd-person/ddd-earl", "ocd-bill/bbb-sb-2", "True", "primary"])
        w.writerow(["sp5", "Sen. Eve Frey", "person", "", "ocd-person/eee-frey", "ocd-bill/bbb-sb-2", "False", "cosponsor"])
        w.writerow(["sp6", "Rep. Faye Gore", "person", "", "ocd-person/fff-gore", "ocd-bill/ccc-hr-369", "True", "primary"])

    return root


# ---------------------------------------------------------------------------
# TestLoadFilings
# ---------------------------------------------------------------------------


class TestLoadFilings:
    def test_returns_dataframe(self, extractions_dir: Path) -> None:
        df = load_filings(extractions_dir)
        assert isinstance(df, pd.DataFrame)

    def test_row_per_filing(self, extractions_dir: Path) -> None:
        df = load_filings(extractions_dir)
        # 4 filings in the fixture
        assert len(df) == 4

    def test_expected_columns_present(self, extractions_dir: Path) -> None:
        df = load_filings(extractions_dir)
        expected = {
            "filing_id",
            "source_path",
            "state",
            "filer_role",
            "lobbyist_name",
            "principal_name",
            "reporting_period_start",
            "reporting_period_end",
            "filed_date",
            "filing_action",
            "supersedes",
            "is_current",
            "total_expenditure",
            "total_compensation",
            "n_expenditures",
            "n_positions",
            "n_gifts",
            "n_engagements",
            "filing_obj",
        }
        assert expected.issubset(set(df.columns)), (
            f"missing columns: {expected - set(df.columns)}"
        )

    def test_filing_id_populated_for_all_rows(self, extractions_dir: Path) -> None:
        df = load_filings(extractions_dir)
        assert df["filing_id"].notna().all()
        # Every fixture filing carries a 20250314XXX1000xxx pattern
        assert all(s.startswith("20250314") for s in df["filing_id"])

    def test_lobbyist_and_principal_names_populated(self, extractions_dir: Path) -> None:
        df = load_filings(extractions_dir)
        # Indexed by filing_id for clarity
        by_id = df.set_index("filing_id")
        assert by_id.loc["20250314AAA1000001", "lobbyist_name"] == "Alice Anderson"
        assert by_id.loc["20250314AAA1000001", "principal_name"] == "Acme Corp"
        assert by_id.loc["20250314DDD1000004", "lobbyist_name"] == "Dan Davis"
        assert by_id.loc["20250314DDD1000004", "principal_name"] == "Delta Inc"

    def test_filing_obj_column_is_lobbying_filing(self, extractions_dir: Path) -> None:
        df = load_filings(extractions_dir)
        for obj in df["filing_obj"]:
            assert isinstance(obj, LobbyingFiling)

    def test_n_position_and_n_gift_counts_correct(self, extractions_dir: Path) -> None:
        df = load_filings(extractions_dir)
        by_id = df.set_index("filing_id")
        assert by_id.loc["20250314AAA1000001", "n_positions"] == 2
        assert by_id.loc["20250314AAA1000001", "n_gifts"] == 1
        assert by_id.loc["20250314BBB1000002", "n_positions"] == 1
        assert by_id.loc["20250314BBB1000002", "n_gifts"] == 0
        assert by_id.loc["20250314CCC1000003", "n_positions"] == 0
        assert by_id.loc["20250314CCC1000003", "n_gifts"] == 0
        assert by_id.loc["20250314DDD1000004", "n_positions"] == 1
        assert by_id.loc["20250314DDD1000004", "n_gifts"] == 2

    def test_source_path_points_at_filing_json(self, extractions_dir: Path) -> None:
        df = load_filings(extractions_dir)
        for p in df["source_path"]:
            assert Path(p).name == "filing.json"
            assert Path(p).exists()

    def test_empty_extractions_dir_returns_empty_df_with_columns(
        self, tmp_path: Path
    ) -> None:
        """Empty dir is a valid input (zero filings). Loader returns an
        empty DataFrame, not a crash; columns are still present so
        downstream code that depends on column shape doesn't break."""
        empty = tmp_path / "no-extractions"
        empty.mkdir()
        df = load_filings(empty)
        assert len(df) == 0
        # Column shape must still match
        assert "filing_id" in df.columns


# ---------------------------------------------------------------------------
# TestLoadPositions
# ---------------------------------------------------------------------------


class TestLoadPositions:
    def test_one_row_per_position(self, extractions_dir: Path) -> None:
        df = load_positions(extractions_dir)
        # Fixture: 2 (A) + 1 (B) + 0 (C) + 1 (D) = 4 positions
        assert len(df) == 4

    def test_expected_columns_present(self, extractions_dir: Path) -> None:
        df = load_positions(extractions_dir)
        expected = {
            "filing_id",
            "position_index",
            "position_obj",
            "principal_name",
            "lobbyist_name",
            "reporting_period_start",
            "reporting_period_end",
            "filing_action",
            "is_current",
        }
        assert expected.issubset(set(df.columns))

    def test_position_obj_column_is_lobbying_position(self, extractions_dir: Path) -> None:
        df = load_positions(extractions_dir)
        for obj in df["position_obj"]:
            assert isinstance(obj, LobbyingPosition)

    def test_filing_metadata_propagated(self, extractions_dir: Path) -> None:
        """Every position row of a filing carries that filing's principal +
        lobbyist names (so a downstream chain composer doesn't have to re-join)."""
        df = load_positions(extractions_dir)
        a_rows = df[df["filing_id"] == "20250314AAA1000001"]
        assert len(a_rows) == 2
        assert (a_rows["principal_name"] == "Acme Corp").all()
        assert (a_rows["lobbyist_name"] == "Alice Anderson").all()

    def test_position_index_is_zero_based_per_filing(self, extractions_dir: Path) -> None:
        df = load_positions(extractions_dir)
        a_rows = df[df["filing_id"] == "20250314AAA1000001"].sort_values("position_index")
        assert list(a_rows["position_index"]) == [0, 1]

    def test_filings_with_no_positions_produce_no_rows(
        self, extractions_dir: Path
    ) -> None:
        df = load_positions(extractions_dir)
        # Filing C has no positions → no rows
        assert (df["filing_id"] == "20250314CCC1000003").sum() == 0

    def test_position_carrying_bill_reference_round_trips(
        self, extractions_dir: Path
    ) -> None:
        """The bill_reference must survive load — chain composer downstream
        depends on accessing position_obj.bill_reference.original_text."""
        df = load_positions(extractions_dir)
        a_rows = df[df["filing_id"] == "20250314AAA1000001"].sort_values("position_index")
        first_position = a_rows.iloc[0]["position_obj"]
        assert isinstance(first_position.bill_reference, BillReference)
        assert first_position.bill_reference.original_text == "HB 96"

    def test_subject_general_position_round_trips(self, extractions_dir: Path) -> None:
        df = load_positions(extractions_dir)
        a_rows = df[df["filing_id"] == "20250314AAA1000001"].sort_values("position_index")
        second_position = a_rows.iloc[1]["position_obj"]
        assert second_position.bill_reference is None
        assert second_position.general_issue_area == "Public Safety"

    def test_subject_hoisted_position_round_trips(self, extractions_dir: Path) -> None:
        df = load_positions(extractions_dir)
        b_rows = df[df["filing_id"] == "20250314BBB1000002"]
        assert len(b_rows) == 1
        pos = b_rows.iloc[0]["position_obj"]
        assert pos.bill_reference is None
        assert pos.general_issue_area is None
        assert pos.description == "Education Policy"


# ---------------------------------------------------------------------------
# TestLoadGifts
# ---------------------------------------------------------------------------


class TestLoadGifts:
    def test_one_row_per_gift(self, extractions_dir: Path) -> None:
        df = load_gifts(extractions_dir)
        # Fixture: 1 (A) + 0 (B) + 0 (C) + 2 (D) = 3 gifts
        assert len(df) == 3

    def test_expected_columns_present(self, extractions_dir: Path) -> None:
        df = load_gifts(extractions_dir)
        expected = {
            "filing_id",
            "gift_index",
            "gift_obj",
            "principal_name",
            "lobbyist_name",
            "reporting_period_start",
            "reporting_period_end",
        }
        assert expected.issubset(set(df.columns))

    def test_gift_obj_column_is_gift_model(self, extractions_dir: Path) -> None:
        df = load_gifts(extractions_dir)
        for obj in df["gift_obj"]:
            assert isinstance(obj, Gift)

    def test_filings_with_no_gifts_produce_no_rows(self, extractions_dir: Path) -> None:
        df = load_gifts(extractions_dir)
        assert (df["filing_id"] == "20250314BBB1000002").sum() == 0
        assert (df["filing_id"] == "20250314CCC1000003").sum() == 0

    def test_filing_d_gifts_round_trip(self, extractions_dir: Path) -> None:
        df = load_gifts(extractions_dir)
        d_rows = df[df["filing_id"] == "20250314DDD1000004"].sort_values("gift_index")
        assert len(d_rows) == 2
        first = d_rows.iloc[0]["gift_obj"]
        assert first.recipient_name == "Rep. Jones"
        assert first.value == 12.50
        second = d_rows.iloc[1]["gift_obj"]
        assert second.recipient_name == "Rep. Wilson"
        assert second.gift_type == "event_ticket"


# ---------------------------------------------------------------------------
# TestLoadPluralBills
# ---------------------------------------------------------------------------


class TestLoadPluralBills:
    def test_columns_present(self, plural_dir: Path) -> None:
        df = load_plural_bills(plural_dir)
        expected = {"bill_id", "identifier", "identifier_norm", "title", "classification"}
        assert expected.issubset(set(df.columns))

    def test_row_per_bill(self, plural_dir: Path) -> None:
        df = load_plural_bills(plural_dir)
        # 3 bills in the fixture
        assert len(df) == 3

    def test_identifier_norm_uppercase_no_dots_collapsed_whitespace(
        self, tmp_path: Path
    ) -> None:
        """Loader applies the smoke-test normalization so identifier_norm is
        directly joinable to the extraction-side normalized labels."""
        root = tmp_path / "plural" / "136"
        root.mkdir(parents=True)
        with (root / "OH_136_bills.csv").open("w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["id", "identifier", "title", "classification", "subject", "session_identifier", "jurisdiction", "organization_classification"])
            # Lowercase with extra space and dots
            w.writerow(["ocd-bill/xxx", "  h.b. 96  ", "x", "['bill']", "[]", "136", "j", "lower"])
            w.writerow(["ocd-bill/yyy", "s.b.  2", "y", "['bill']", "[]", "136", "j", "upper"])
        # Need a sponsorships CSV too even if empty — bills loader shouldn't
        # require it, but plural_dir convention expects both. Keep this test
        # bills-only: pass the dir directly without requiring sponsorships.
        df = load_plural_bills(root)
        norms = sorted(df["identifier_norm"])
        assert norms == ["HB 96", "SB 2"]

    def test_bill_id_preserved_from_csv(self, plural_dir: Path) -> None:
        df = load_plural_bills(plural_dir)
        by_norm = df.set_index("identifier_norm")
        assert by_norm.loc["HB 96", "bill_id"] == "ocd-bill/aaa-hb-96"
        assert by_norm.loc["SB 2", "bill_id"] == "ocd-bill/bbb-sb-2"
        assert by_norm.loc["HR 369", "bill_id"] == "ocd-bill/ccc-hr-369"


# ---------------------------------------------------------------------------
# TestLoadPluralSponsorships
# ---------------------------------------------------------------------------


class TestLoadPluralSponsorships:
    def test_default_filters_to_primary(self, plural_dir: Path) -> None:
        """Per Q2 — v1 ships primary-only. Default is "primary"."""
        df = load_plural_sponsorships(plural_dir)
        # Fixture has 4 primaries (HB96×2, SB2×1, HR369×1), 2 cosponsors
        assert len(df) == 4
        assert (df["classification"] == "primary").all()

    def test_classification_filter_can_be_overridden(self, plural_dir: Path) -> None:
        df = load_plural_sponsorships(plural_dir, classification="cosponsor")
        assert len(df) == 2
        assert (df["classification"] == "cosponsor").all()

    def test_classification_none_loads_all(self, plural_dir: Path) -> None:
        df = load_plural_sponsorships(plural_dir, classification=None)
        # 4 primaries + 2 cosponsors = 6
        assert len(df) == 6

    def test_expected_columns_present(self, plural_dir: Path) -> None:
        df = load_plural_sponsorships(plural_dir)
        expected = {
            "id",
            "name",
            "entity_type",
            "organization_id",
            "person_id",
            "bill_id",
            "primary",
            "classification",
        }
        assert expected.issubset(set(df.columns))

    def test_multi_primary_bill_emits_multiple_rows(self, plural_dir: Path) -> None:
        """HB 96 in the fixture has 2 primary sponsors (matches the real
        40.8% multi-primary OH structural finding from Phase 0)."""
        df = load_plural_sponsorships(plural_dir)
        hb96 = df[df["bill_id"] == "ocd-bill/aaa-hb-96"]
        assert len(hb96) == 2
        names = set(hb96["name"])
        assert names == {"Rep. Adam Bird", "Rep. Bea Cox"}


# ---------------------------------------------------------------------------
# TestSelectCanonicalExtraction
# ---------------------------------------------------------------------------


class TestSelectCanonicalExtraction:
    """Dedupe a filings DataFrame to one row per filing_id.

    Surfaced by the 2026-06-14 real-data smoke test: 5 filing_ids in the
    316-filing cache have multiple cached extractions (one filing has 8).
    Phase 2's chain composer must dedupe before composing or it will
    triple-count positions for those 5 filings.

    Strategy: most-recent by ``filing.json`` mtime wins; lexicographic
    ``source_path`` is the deterministic tie-breaker.
    """

    def test_no_duplicates_pass_through_unchanged(self, extractions_dir: Path) -> None:
        """If filing_ids are already unique, the dedup is a no-op."""
        df = load_filings(extractions_dir)
        canonical = select_canonical_extraction(df)
        assert len(canonical) == len(df)
        assert set(canonical["filing_id"]) == set(df["filing_id"])

    def test_picks_most_recent_extraction_by_mtime(self, tmp_path: Path) -> None:
        """When the same filing_id has two extractions, the most-recent
        ``filing.json`` mtime wins."""
        import os

        root = tmp_path / "extractions"
        # Two extractions of the same filing_id, different hashes.
        old_path = _write_filing(
            root, "999", "olderhash", _filing_dict("DUPED999", lobbyist_name="Old Run")
        )
        new_path = _write_filing(
            root, "999", "newerhash", _filing_dict("DUPED999", lobbyist_name="New Run")
        )
        # Force the old one to have an older mtime so the test is deterministic.
        old_mtime = new_path.stat().st_mtime - 100
        os.utime(old_path, (old_mtime, old_mtime))

        df = load_filings(root)
        assert len(df) == 2  # loader does not pre-dedupe — confirms the contract
        canonical = select_canonical_extraction(df)
        assert len(canonical) == 1
        assert canonical.iloc[0]["lobbyist_name"] == "New Run"
        assert canonical.iloc[0]["source_path"] == str(new_path)

    def test_lex_path_breaks_ties_when_mtimes_equal(self, tmp_path: Path) -> None:
        """If two extractions have identical mtime, the lexicographically
        larger source_path wins (deterministic fallback)."""
        import os

        root = tmp_path / "extractions"
        a_path = _write_filing(
            root, "888", "aaaaaaaa", _filing_dict("TIEDFID888", lobbyist_name="A run")
        )
        b_path = _write_filing(
            root, "888", "zzzzzzzz", _filing_dict("TIEDFID888", lobbyist_name="Z run")
        )
        # Force identical mtimes.
        shared = a_path.stat().st_mtime
        os.utime(a_path, (shared, shared))
        os.utime(b_path, (shared, shared))

        df = load_filings(root)
        canonical = select_canonical_extraction(df)
        assert len(canonical) == 1
        # Lexicographically-larger path (zzzzzzzz > aaaaaaaa) wins.
        assert canonical.iloc[0]["lobbyist_name"] == "Z run"

    def test_returns_input_when_already_empty(self) -> None:
        """Empty input → empty output, no crash."""
        empty = pd.DataFrame(
            {"filing_id": [], "source_path": []},
        )
        canonical = select_canonical_extraction(empty)
        assert len(canonical) == 0
        assert "filing_id" in canonical.columns

    def test_preserves_all_columns(self, extractions_dir: Path) -> None:
        df = load_filings(extractions_dir)
        canonical = select_canonical_extraction(df)
        assert set(canonical.columns) == set(df.columns)
