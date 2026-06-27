"""Phase 2 — bill-side chain composer tests for OH.

Tests are fixture-only (pure-logic; no real-cache dependency). The local
``conftest.py`` overrides the repo's autouse Postgres-dependent
``_truncate_filings`` fixture to a no-op.

Plan reference: ``docs/active/oh-portal-extraction/plans/20260611_oh_chain_composer_design.md`` §5 Phase 2.

Covers:

- The §5 Phase 2 plan fixture: 1 filing × 2 bill-positions × 1 bill × 2 primaries
  + 1 subject-only position → 5 rows.
- Conservation: every position produces ≥1 chain row.
- Cross-product math: bill-referenced × N primaries emits N rows.
- Subject-only rows have null sponsor fields and skip the cross-product (§4a).
- JCARR / OAC / unmatched / null-extraction routing produces single rows
  with null sponsor fields and the correct ``confidence`` token.
- Multi-primary bill exercises the OH-distinctive 40.8% multi-primary case
  surfaced in Phase 0.
- Extraction-cache duplicates do NOT inflate row count (dedup is invoked).
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

import pandas as pd
import pytest

from lobby_analysis.allocation.oh.chain import (
    CHAIN_COLUMNS,
    compose_bill_chain,
)


# ---------------------------------------------------------------------------
# Helpers — write a filing.json + Plural CSVs into tmp_path
# ---------------------------------------------------------------------------


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
    principal_id: str = "org-acme-corp",
    lobbyist_name: str = "Jane Doe",
    lobbyist_id: str = "person-jane-doe",
    period_start: str = "2025-01-01",
    period_end: str = "2025-04-30",
    positions: list[dict] | None = None,
) -> dict:
    return {
        "id": f"filing-{filing_id}",
        "state": "OH",
        "filing_id": filing_id,
        "filing_type": "activity_report",
        "filer_person": {"id": lobbyist_id, "name": lobbyist_name, "source_state": "OH"},
        "filer_role": "lobbyist",
        "employer": {"id": principal_id, "name": principal_name, "source_state": "OH"},
        "reporting_period_start": period_start,
        "reporting_period_end": period_end,
        "filing_action": "original",
        "is_current": True,
        "positions": positions or [],
        "expenditures": [],
        "engagements": [],
        "gifts": [],
    }


def _bill_pos(text: str, description: str | None = None) -> dict:
    return {
        "bill_reference": {
            "original_text": text,
            "bill_number": text,
            "reference_type": "bill",
            "is_resolved": False,
        },
        "general_issue_area": None,
        "description": description,
    }


def _subject_pos(issue_area: str) -> dict:
    return {
        "bill_reference": None,
        "general_issue_area": issue_area,
        "description": None,
    }


def _hoisted_pos(description: str) -> dict:
    return {
        "bill_reference": None,
        "general_issue_area": None,
        "description": description,
    }


def _empty_pos() -> dict:
    """A position with all three subject-carrying fields empty. The classifier
    raises ValueError on this; the composer should catch and emit a sentinel
    row with confidence='null_extraction' (defect surfaced, not silently
    dropped)."""
    return {"bill_reference": None, "general_issue_area": None, "description": None}


def _write_plural(
    plural_dir: Path,
    bills: list[tuple[str, str, str, str]],  # (bill_id, identifier, title, classification)
    sponsorships: list[tuple[str, str, str, str, str]],  # (id, name, person_id, bill_id, classification)
) -> Path:
    plural_dir.mkdir(parents=True, exist_ok=True)
    with (plural_dir / "OH_136_bills.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(
            ["id", "identifier", "title", "classification", "subject", "session_identifier", "jurisdiction", "organization_classification"]
        )
        for bill_id, ident, title, cls in bills:
            w.writerow([bill_id, ident, title, cls, "", "136", "j", "lower"])
    with (plural_dir / "OH_136_bill_sponsorships.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(
            ["id", "name", "entity_type", "organization_id", "person_id", "bill_id", "primary", "classification"]
        )
        for sid, name, person_id, bill_id, cls in sponsorships:
            primary_flag = "True" if cls == "primary" else "False"
            w.writerow([sid, name, "person", "", person_id, bill_id, primary_flag, cls])
    return plural_dir


# ---------------------------------------------------------------------------
# Fixtures: the §5 Phase 2 canonical scenario
# ---------------------------------------------------------------------------


@pytest.fixture
def plan_phase2_dirs(tmp_path: Path) -> tuple[Path, Path]:
    """Plan §5 Phase 2 fixture:
    1 filing × 2 bill-positions × 1 bill × 2 sponsors + 1 subject-only position.
    Expected: 5 chain rows (2 + 2 + 1)."""
    extractions = tmp_path / "extractions"
    plural = tmp_path / "plural" / "136"

    _write_filing(
        extractions,
        "100",
        "h1",
        _make_filing(
            "FID100",
            positions=[
                _bill_pos("HB 96", description="support the appropriations"),
                _bill_pos("HB 96", description="strike section 1"),
                _subject_pos("Public Safety"),
            ],
        ),
    )

    _write_plural(
        plural,
        bills=[("ocd-bill/hb-96", "HB 96", "Operating budget FY 2026-27", "['bill']")],
        sponsorships=[
            ("sp1", "Rep. Adam Bird", "ocd-person/bird", "ocd-bill/hb-96", "primary"),
            ("sp2", "Rep. Bea Cox", "ocd-person/cox", "ocd-bill/hb-96", "primary"),
        ],
    )

    return extractions, plural


@pytest.fixture
def mixed_class_dirs(tmp_path: Path) -> tuple[Path, Path]:
    """Filing with one of each bill_class to verify routing:
    - bill (joinable) — 1 primary
    - jcarr
    - oac_rule
    - unmatched (bill_referenced with digit-containing malformed label —
      a label that *contains a digit* so the 2026-06-15 composer-side
      demotion rule does NOT demote it to subject. This preserves the
      malformed-bill audit signal that the unmatched class exists to
      carry.)
    - subject_general
    - subject_hoisted (mini quirk)
    """
    extractions = tmp_path / "extractions"
    plural = tmp_path / "plural" / "136"

    _write_filing(
        extractions,
        "200",
        "h2",
        _make_filing(
            "FID200",
            positions=[
                _bill_pos("SB 2"),  # bill, joinable
                _bill_pos("JC 4731-9-01"),  # jcarr
                _bill_pos("5160-32-02"),  # oac_rule
                _bill_pos("HJ Res 5"),  # unmatched (digit-containing malformed bill — exempt from no-digit demotion)
                _subject_pos("Education Policy"),  # subject_general
                _hoisted_pos("Mini-quirk subject"),  # subject_hoisted
            ],
        ),
    )

    _write_plural(
        plural,
        bills=[("ocd-bill/sb-2", "SB 2", "Energy generation", "['bill']")],
        sponsorships=[
            ("sp10", "Sen. Don Earl", "ocd-person/earl", "ocd-bill/sb-2", "primary"),
        ],
    )

    return extractions, plural


# ---------------------------------------------------------------------------
# Tests: schema + plan §5 Phase 2 canonical scenario
# ---------------------------------------------------------------------------


class TestSchema:
    def test_chain_columns_constant_present(self) -> None:
        assert isinstance(CHAIN_COLUMNS, tuple)
        for col in (
            "report_period",
            "filing_id",
            "principal_name",
            "principal_id",
            "lobbyist_name",
            "lobbyist_id",
            "position_kind",
            "bill_label_raw",
            "bill_label_normalized",
            "bill_class",
            "bill_id",
            "bill_title",
            "position_description",
            "num_primary_sponsors",
            "sponsor_lawmaker_id",
            "sponsor_lawmaker_name",
            "sponsor_role",
            "confidence",
        ):
            assert col in CHAIN_COLUMNS

    def test_output_dataframe_has_chain_columns(
        self, plan_phase2_dirs: tuple[Path, Path]
    ) -> None:
        ext, pl = plan_phase2_dirs
        df = compose_bill_chain(ext, pl)
        assert list(df.columns) == list(CHAIN_COLUMNS)


class TestPlanPhase2Fixture:
    def test_five_rows(self, plan_phase2_dirs: tuple[Path, Path]) -> None:
        """Plan §5 Phase 2 contract: 1 filing × 2 bill-positions × 1 bill ×
        2 sponsors + 1 subject-only position → exactly 5 rows."""
        ext, pl = plan_phase2_dirs
        df = compose_bill_chain(ext, pl)
        assert len(df) == 5

    def test_bill_rows_have_sponsor_data(self, plan_phase2_dirs: tuple[Path, Path]) -> None:
        ext, pl = plan_phase2_dirs
        df = compose_bill_chain(ext, pl)
        bill_rows = df[df["bill_class"] == "bill"]
        assert len(bill_rows) == 4  # 2 positions × 2 sponsors
        assert bill_rows["sponsor_lawmaker_id"].notna().all()
        assert bill_rows["sponsor_lawmaker_name"].notna().all()
        assert (bill_rows["sponsor_role"] == "primary").all()
        # Both sponsors appear (across the 4 rows: 2× each)
        sponsor_counts = bill_rows["sponsor_lawmaker_name"].value_counts().to_dict()
        assert sponsor_counts == {"Rep. Adam Bird": 2, "Rep. Bea Cox": 2}

    def test_bill_rows_carry_bill_metadata(
        self, plan_phase2_dirs: tuple[Path, Path]
    ) -> None:
        ext, pl = plan_phase2_dirs
        df = compose_bill_chain(ext, pl)
        bill_rows = df[df["bill_class"] == "bill"]
        assert (bill_rows["bill_id"] == "ocd-bill/hb-96").all()
        assert (bill_rows["bill_title"] == "Operating budget FY 2026-27").all()
        assert (bill_rows["bill_label_normalized"] == "HB 96").all()
        assert (bill_rows["num_primary_sponsors"] == 2).all()

    def test_subject_row_has_null_sponsor(
        self, plan_phase2_dirs: tuple[Path, Path]
    ) -> None:
        ext, pl = plan_phase2_dirs
        df = compose_bill_chain(ext, pl)
        subject_rows = df[df["bill_class"] == "subject"]
        assert len(subject_rows) == 1
        row = subject_rows.iloc[0]
        assert pd.isna(row["sponsor_lawmaker_id"])
        assert pd.isna(row["sponsor_lawmaker_name"])
        assert pd.isna(row["sponsor_role"])
        assert pd.isna(row["bill_id"])
        assert row["bill_label_raw"] == "Public Safety"
        assert row["position_kind"] == "subject_general"
        assert row["confidence"] == "subject_only"
        assert row["num_primary_sponsors"] == 0

    def test_position_description_carries_through_on_bill_rows(
        self, plan_phase2_dirs: tuple[Path, Path]
    ) -> None:
        """Per plan §4 schema sketch: position_description column carries
        the position's description for analyst use."""
        ext, pl = plan_phase2_dirs
        df = compose_bill_chain(ext, pl)
        bill_rows = df[df["bill_class"] == "bill"]
        descs = set(bill_rows["position_description"])
        assert descs == {"support the appropriations", "strike section 1"}

    def test_filing_level_fields_populated(
        self, plan_phase2_dirs: tuple[Path, Path]
    ) -> None:
        ext, pl = plan_phase2_dirs
        df = compose_bill_chain(ext, pl)
        assert (df["filing_id"] == "FID100").all()
        assert (df["principal_name"] == "Acme Corp").all()
        assert (df["principal_id"] == "org-acme-corp").all()
        assert (df["lobbyist_name"] == "Jane Doe").all()
        assert (df["lobbyist_id"] == "person-jane-doe").all()
        assert (df["report_period"] == "2025-01-01..2025-04-30").all()


# ---------------------------------------------------------------------------
# Tests: routing per bill_class
# ---------------------------------------------------------------------------


class TestBillClassRouting:
    def test_one_row_per_class(self, mixed_class_dirs: tuple[Path, Path]) -> None:
        """6 positions: 1 bill (× 1 primary), 1 jcarr, 1 oac_rule, 1 unmatched,
        1 subject_general, 1 subject_hoisted → 6 chain rows."""
        ext, pl = mixed_class_dirs
        df = compose_bill_chain(ext, pl)
        assert len(df) == 6

    def test_bill_class_distribution(self, mixed_class_dirs: tuple[Path, Path]) -> None:
        ext, pl = mixed_class_dirs
        df = compose_bill_chain(ext, pl)
        counts = df["bill_class"].value_counts().to_dict()
        assert counts == {
            "bill": 1,
            "jcarr": 1,
            "oac_rule": 1,
            "unmatched": 1,
            "subject": 2,
        }

    @pytest.mark.parametrize(
        "bill_class,expected_confidence",
        [
            ("bill", "direct"),
            ("jcarr", "oac_dropped"),
            ("oac_rule", "oac_dropped"),
            ("unmatched", "unmatched"),
            ("subject", "subject_only"),
        ],
    )
    def test_confidence_token_per_class(
        self,
        mixed_class_dirs: tuple[Path, Path],
        bill_class: str,
        expected_confidence: str,
    ) -> None:
        ext, pl = mixed_class_dirs
        df = compose_bill_chain(ext, pl)
        rows = df[df["bill_class"] == bill_class]
        assert (rows["confidence"] == expected_confidence).all()

    def test_non_bill_rows_have_null_sponsor_fields(
        self, mixed_class_dirs: tuple[Path, Path]
    ) -> None:
        ext, pl = mixed_class_dirs
        df = compose_bill_chain(ext, pl)
        non_bill = df[df["bill_class"] != "bill"]
        # 5 non-bill rows (jcarr, oac_rule, unmatched, subject_general, subject_hoisted)
        assert len(non_bill) == 5
        assert non_bill["sponsor_lawmaker_id"].isna().all()
        assert non_bill["sponsor_lawmaker_name"].isna().all()
        assert non_bill["sponsor_role"].isna().all()
        assert non_bill["bill_id"].isna().all()
        assert (non_bill["num_primary_sponsors"] == 0).all()

    def test_subject_hoisted_row_carries_description_in_label(
        self, mixed_class_dirs: tuple[Path, Path]
    ) -> None:
        """§4a: subject_hoisted_from_description case — bill_label_raw is
        the description text. position_description column is null (not
        duplicating the hoisted text)."""
        ext, pl = mixed_class_dirs
        df = compose_bill_chain(ext, pl)
        hoisted = df[df["position_kind"] == "subject_hoisted_from_description"]
        assert len(hoisted) == 1
        row = hoisted.iloc[0]
        assert row["bill_label_raw"] == "Mini-quirk subject"
        assert pd.isna(row["position_description"])


# ---------------------------------------------------------------------------
# Tests: empty-position handling
# ---------------------------------------------------------------------------


class TestEmptyPositionRobustness:
    def test_empty_position_emits_sentinel_row(self, tmp_path: Path) -> None:
        """A position with all three subject-carrying fields null/whitespace
        is a defect (classifier raises). The composer catches and emits a
        sentinel row so one defective position does not kill the whole
        composer run."""
        ext = tmp_path / "extractions"
        pl = tmp_path / "plural" / "136"
        _write_filing(
            ext,
            "300",
            "h3",
            _make_filing(
                "FID300",
                positions=[
                    _bill_pos("HB 1"),  # valid bill
                    _empty_pos(),  # defect
                ],
            ),
        )
        _write_plural(
            pl,
            bills=[("ocd-bill/hb-1", "HB 1", "Some bill", "['bill']")],
            sponsorships=[
                ("sp20", "Rep. X", "ocd-person/x", "ocd-bill/hb-1", "primary"),
            ],
        )
        df = compose_bill_chain(ext, pl)
        # 1 bill row + 1 sentinel = 2 rows
        assert len(df) == 2
        sentinel = df[df["confidence"] == "null_extraction"]
        assert len(sentinel) == 1
        srow = sentinel.iloc[0]
        assert pd.isna(srow["bill_label_raw"])
        assert pd.isna(srow["bill_id"])
        assert pd.isna(srow["sponsor_lawmaker_id"])


# ---------------------------------------------------------------------------
# Tests: dedup invoked
# ---------------------------------------------------------------------------


class TestDeduplicationInvoked:
    def test_duplicate_extractions_do_not_inflate_row_count(self, tmp_path: Path) -> None:
        """If the same filing_id has multiple cached extractions, the composer
        must dedupe (select_canonical_extraction). With 2 extractions of
        1 filing × 1 bill position × 1 bill × 1 primary, the output is
        1 row, not 2."""
        import os

        ext = tmp_path / "extractions"
        pl = tmp_path / "plural" / "136"

        # Two extractions of the same filing_id with the same content
        old = _write_filing(
            ext, "400", "olderh", _make_filing("FID400", positions=[_bill_pos("HB 99")])
        )
        new = _write_filing(
            ext, "400", "newerh", _make_filing("FID400", positions=[_bill_pos("HB 99")])
        )
        # Make 'old' actually older for determinism
        old_mtime = new.stat().st_mtime - 100
        os.utime(old, (old_mtime, old_mtime))

        _write_plural(
            pl,
            bills=[("ocd-bill/hb-99", "HB 99", "x", "['bill']")],
            sponsorships=[("sp30", "Rep. Y", "ocd-person/y", "ocd-bill/hb-99", "primary")],
        )

        df = compose_bill_chain(ext, pl)
        # Without dedup, this would be 2 rows (positions × sponsors × 2 extractions);
        # with dedup, it's 1 row.
        assert len(df) == 1


# ---------------------------------------------------------------------------
# Tests: bill that matches Plural but has no primary sponsor (defensive)
# ---------------------------------------------------------------------------


class TestBillNoPrimaryDefensive:
    def test_bill_with_no_primary_emits_single_row_with_null_sponsor(
        self, tmp_path: Path
    ) -> None:
        """A bill class joins to Plural but the bill row has no primary
        sponsors (edge case). Defensive logic emits ONE row with null
        sponsor fields — not zero rows (silent drop) and not crash."""
        ext = tmp_path / "extractions"
        pl = tmp_path / "plural" / "136"

        _write_filing(
            ext, "500", "h5", _make_filing("FID500", positions=[_bill_pos("HB 50")])
        )
        # Bill in Plural with NO sponsorships
        _write_plural(
            pl,
            bills=[("ocd-bill/hb-50", "HB 50", "Lonely bill", "['bill']")],
            sponsorships=[],
        )

        df = compose_bill_chain(ext, pl)
        assert len(df) == 1
        row = df.iloc[0]
        assert row["bill_class"] == "bill"
        assert row["bill_id"] == "ocd-bill/hb-50"
        assert pd.isna(row["sponsor_lawmaker_id"])
        assert row["num_primary_sponsors"] == 0


# ---------------------------------------------------------------------------
# Tests: bill_referenced position whose label doesn't match Plural
# ---------------------------------------------------------------------------


class TestBillNotInPlural:
    def test_bill_label_not_in_plural_emits_unmatched_row(self, tmp_path: Path) -> None:
        """A position carries bill_reference with a valid bill-shape label,
        but the label isn't in OH_136_bills.csv (e.g., a bill from a prior
        GA, or a typo, or 2026 bill numbering that landed after the cache).
        Emit a single row with bill_class='unmatched' (downgraded from 'bill'
        because the join failed) and confidence='unmatched'."""
        ext = tmp_path / "extractions"
        pl = tmp_path / "plural" / "136"

        _write_filing(
            ext, "600", "h6", _make_filing("FID600", positions=[_bill_pos("HB 999")])
        )
        # Plural has different bills, no HB 999
        _write_plural(
            pl,
            bills=[("ocd-bill/hb-1", "HB 1", "x", "['bill']")],
            sponsorships=[("sp40", "Rep. Z", "ocd-person/z", "ocd-bill/hb-1", "primary")],
        )

        df = compose_bill_chain(ext, pl)
        assert len(df) == 1
        row = df.iloc[0]
        assert row["bill_class"] == "unmatched"
        assert row["confidence"] == "unmatched"
        assert pd.isna(row["bill_id"])
        assert row["bill_label_raw"] == "HB 999"
        # num_primary_sponsors is 0 for non-bill rows per the schema
        assert row["num_primary_sponsors"] == 0


# ---------------------------------------------------------------------------
# Tests: Step 1 — deterministic entity-ID derivation at composer time
# ---------------------------------------------------------------------------
#
# Plan: docs/active/leave-behind-prep/plans/20260615_composer_side_mini_swap_normalizations.md
#
# These are the composer-level integration tests for Step 1. The pure
# derivation helpers are exercised in test_entity_id_derivation.py; the
# tests below prove the composer reads the derived ID, not the model-
# emitted .id field.


class TestEntityIdDerivationComposerIntegration:
    def test_composer_ignores_model_emitted_id_and_derives_principal_id(
        self, tmp_path: Path
    ) -> None:
        """The model-emitted ``employer.id`` may be inconsistent across
        models (sonnet vs mini). The composer must derive ``principal_id``
        from ``employer.name`` and ignore whatever the model put in
        ``employer.id``. This is the chain-level mini-swap fix."""
        ext = tmp_path / "extractions"
        pl = tmp_path / "plural" / "136"

        _write_filing(
            ext,
            "700",
            "h7",
            _make_filing(
                "FID700",
                principal_name="AAA Club Alliance Inc",
                principal_id="garbage-model-emitted-id",  # must be ignored
                lobbyist_name="Jane Doe",
                lobbyist_id="another-garbage-id",  # must be ignored
                positions=[_bill_pos("HB 7")],
            ),
        )
        _write_plural(
            pl,
            bills=[("ocd-bill/hb-7", "HB 7", "x", "['bill']")],
            sponsorships=[("sp70", "Rep. P", "ocd-person/p", "ocd-bill/hb-7", "primary")],
        )

        df = compose_bill_chain(ext, pl)
        assert len(df) == 1
        row = df.iloc[0]
        # Derived from the *name*, not the model-emitted .id
        assert row["principal_id"] == "org-aaa-club-alliance-inc"
        assert row["lobbyist_id"] == "person-jane-doe"
        # Names pass through untouched
        assert row["principal_name"] == "AAA Club Alliance Inc"
        assert row["lobbyist_name"] == "Jane Doe"

    def test_two_filings_with_inconsistent_model_ids_but_same_name_collapse(
        self, tmp_path: Path
    ) -> None:
        """Two filings from the same principal, but the model emits
        different ``.id`` strings for each (the canonical mini-swap
        failure mode). Derivation collapses them to one
        ``principal_id`` — the whole point of the fix."""
        ext = tmp_path / "extractions"
        pl = tmp_path / "plural" / "136"

        _write_filing(
            ext,
            "800",
            "h8",
            _make_filing(
                "FID800",
                principal_name="Cleveland Browns",
                principal_id="cleveland-browns-llc",  # sonnet-ish
                positions=[_bill_pos("HB 8")],
            ),
        )
        _write_filing(
            ext,
            "801",
            "h8b",
            _make_filing(
                "FID801",
                principal_name="Cleveland Browns",
                principal_id="org_cleveland_browns_id_42",  # mini-ish
                positions=[_bill_pos("HB 8")],
            ),
        )
        _write_plural(
            pl,
            bills=[("ocd-bill/hb-8", "HB 8", "x", "['bill']")],
            sponsorships=[("sp80", "Rep. Q", "ocd-person/q", "ocd-bill/hb-8", "primary")],
        )

        df = compose_bill_chain(ext, pl)
        assert (df["principal_id"] == "org-cleveland-browns").all()

    def test_missing_name_yields_null_id(self, tmp_path: Path) -> None:
        """If the filing has no employer.name (defensive — the model
        could emit a null), principal_id is None. The derivation does
        NOT attach an ``org-`` prefix to nothing."""
        # We use _make_filing with empty principal_name and a non-empty
        # principal_id (would-be model garbage). The composer must still
        # null-out principal_id.
        ext = tmp_path / "extractions"
        pl = tmp_path / "plural" / "136"

        _write_filing(
            ext,
            "900",
            "h9",
            _make_filing(
                "FID900",
                principal_name="",  # blank name
                principal_id="garbage",
                positions=[_bill_pos("HB 9")],
            ),
        )
        _write_plural(
            pl,
            bills=[("ocd-bill/hb-9", "HB 9", "x", "['bill']")],
            sponsorships=[("sp90", "Rep. R", "ocd-person/r", "ocd-bill/hb-9", "primary")],
        )

        df = compose_bill_chain(ext, pl)
        row = df.iloc[0]
        assert pd.isna(row["principal_id"])


# ---------------------------------------------------------------------------
# Tests: Step 2 — no-digit demotion of unmatched bill_referenced rows
# ---------------------------------------------------------------------------
#
# Plan: docs/active/leave-behind-prep/plans/20260615_composer_side_mini_swap_normalizations.md
#
# Mini routes regulatory/policy subjects ("Medicaid Reform", "Competency
# Restoration") into the bill_reference slot — composer correctly flags
# them as unmatched (no HB/SB pattern), but they really are subjects in
# disguise. Rule: if a bill_referenced position classifies as unmatched
# AND its label contains no digits, demote it to subject_general+subject.
# A label without digits is structurally incapable of being a bill/rule/
# JCARR citation (all of those require digits), so the demotion is safe.
# Digit-containing unmatched rows (e.g., 'HJ Res 5') are preserved as
# unmatched so the genuinely-malformed-bill audit signal survives.


class TestUnmatchedDemotion:
    def test_no_digit_unmatched_demoted_to_subject(self, tmp_path: Path) -> None:
        """bill_reference.original_text contains no digits → demoted.
        The row's position_kind becomes subject_general, bill_class
        becomes subject, confidence becomes subject_only."""
        ext = tmp_path / "extractions"
        pl = tmp_path / "plural" / "136"

        _write_filing(
            ext,
            "1000",
            "ha",
            _make_filing(
                "FID1000",
                positions=[_bill_pos("Competency Restoration")],
            ),
        )
        _write_plural(pl, bills=[], sponsorships=[])

        df = compose_bill_chain(ext, pl)
        assert len(df) == 1
        row = df.iloc[0]
        assert row["position_kind"] == "subject_general"
        assert row["bill_class"] == "subject"
        assert row["confidence"] == "subject_only"
        # The original label text is preserved as the row's subject content
        assert row["bill_label_raw"] == "Competency Restoration"
        # Demoted rows behave like subject rows: no sponsor cross-product
        assert pd.isna(row["bill_id"])
        assert pd.isna(row["sponsor_lawmaker_id"])

    @pytest.mark.parametrize(
        "label",
        [
            "Healthcare Policy",
            "Medicaid Reform",
            "Public Safety",
            "Issue advocacy and outreach",
        ],
    )
    def test_no_digit_labels_all_demote(self, tmp_path: Path, label: str) -> None:
        """A handful of mini's observed no-digit unmatched leak patterns —
        all demote to subject."""
        ext = tmp_path / "extractions"
        pl = tmp_path / "plural" / "136"

        _write_filing(
            ext, "1100", "hb", _make_filing("FID1100", positions=[_bill_pos(label)])
        )
        _write_plural(pl, bills=[], sponsorships=[])

        df = compose_bill_chain(ext, pl)
        row = df.iloc[0]
        assert row["bill_class"] == "subject", (
            f"{label!r} (no digits) should demote to subject"
        )

    def test_digit_containing_unmatched_preserved(self, tmp_path: Path) -> None:
        """bill_reference label contains a digit but doesn't match any
        bill / OAC / JCARR pattern (e.g., 'HJ Res 5'). Stays unmatched —
        the audit signal that 'this *looked* like a bill citation but
        didn't join' is exactly what the unmatched class exists for."""
        ext = tmp_path / "extractions"
        pl = tmp_path / "plural" / "136"

        _write_filing(
            ext,
            "1200",
            "hc",
            _make_filing("FID1200", positions=[_bill_pos("HJ Res 5")]),
        )
        _write_plural(pl, bills=[], sponsorships=[])

        df = compose_bill_chain(ext, pl)
        row = df.iloc[0]
        assert row["position_kind"] == "bill_referenced"
        assert row["bill_class"] == "unmatched"
        assert row["confidence"] == "unmatched"
        assert row["bill_label_raw"] == "HJ Res 5"

    @pytest.mark.parametrize(
        "label",
        [
            "Title IV-D",  # contains '4' as Roman numeral text? No — actually 'IV' is letters; this label has no digits → would demote. Skip.
            "Chapter 4",  # digit; stays unmatched
            "Issue 3",  # digit; stays unmatched
            "Section 230",  # digit; stays unmatched
            "5 USC 552",  # digit; stays unmatched
        ],
    )
    def test_digit_containing_labels_stay_unmatched(
        self, tmp_path: Path, label: str
    ) -> None:
        """Several digit-containing-but-not-bill-shape labels — all stay
        unmatched per the plan's audit-signal preservation goal."""
        if "IV-D" in label:
            pytest.skip("Roman numerals don't count as digits; this would demote")
        ext = tmp_path / "extractions"
        pl = tmp_path / "plural" / "136"

        _write_filing(
            ext, "1300", "hd", _make_filing("FID1300", positions=[_bill_pos(label)])
        )
        _write_plural(pl, bills=[], sponsorships=[])

        df = compose_bill_chain(ext, pl)
        row = df.iloc[0]
        assert row["bill_class"] == "unmatched", (
            f"{label!r} (digit-containing) should stay unmatched"
        )

    def test_real_bill_unaffected(self, tmp_path: Path) -> None:
        """The demotion rule must not fire on rows that classify as 'bill'
        (joinable) — only on 'unmatched'. Regression guard."""
        ext = tmp_path / "extractions"
        pl = tmp_path / "plural" / "136"

        _write_filing(
            ext,
            "1400",
            "he",
            _make_filing("FID1400", positions=[_bill_pos("HB 96")]),
        )
        _write_plural(
            pl,
            bills=[("ocd-bill/hb-96", "HB 96", "x", "['bill']")],
            sponsorships=[
                ("sp01", "Rep. A", "ocd-person/a", "ocd-bill/hb-96", "primary"),
            ],
        )

        df = compose_bill_chain(ext, pl)
        # 1 primary sponsor → 1 row, class='bill', not demoted
        assert len(df) == 1
        assert df.iloc[0]["bill_class"] == "bill"

    def test_real_oac_rule_unaffected(self, tmp_path: Path) -> None:
        """OAC rule labels (e.g., '5160-46-01') contain digits AND match
        the OAC pattern — classify as oac_rule, not unmatched. The
        demotion rule must not fire."""
        ext = tmp_path / "extractions"
        pl = tmp_path / "plural" / "136"

        _write_filing(
            ext,
            "1500",
            "hf",
            _make_filing("FID1500", positions=[_bill_pos("5160-46-01")]),
        )
        _write_plural(pl, bills=[], sponsorships=[])

        df = compose_bill_chain(ext, pl)
        row = df.iloc[0]
        assert row["bill_class"] == "oac_rule"
        assert row["confidence"] == "oac_dropped"

    def test_subject_general_unaffected(self, tmp_path: Path) -> None:
        """subject_general positions (no bill_reference) bypass the
        demotion path entirely — they're already subject. The rule
        targets the bill_referenced+unmatched intersection only."""
        ext = tmp_path / "extractions"
        pl = tmp_path / "plural" / "136"

        _write_filing(
            ext,
            "1600",
            "hg",
            _make_filing(
                "FID1600",
                positions=[_subject_pos("Education Policy")],
            ),
        )
        _write_plural(pl, bills=[], sponsorships=[])

        df = compose_bill_chain(ext, pl)
        row = df.iloc[0]
        assert row["position_kind"] == "subject_general"
        assert row["bill_class"] == "subject"
