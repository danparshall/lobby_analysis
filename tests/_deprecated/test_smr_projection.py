"""SUPERSEDED — tests for the v1 PRI-MVP SMR projection (retired 2026-05-14).

Status: retired by ``phase-c-projection-tdd`` Phase 3 alongside the source
module at ``src/scoring/_deprecated/smr_projection.py``. Kept here for
recoverability of the v1 PRI-MVP pipeline; excluded from default pytest
collection via ``pyproject.toml`` ``collect_ignore``-equivalent (testpaths
scope is just ``tests/`` at the top level; this subdir is no longer auto-
discovered).

To re-run these tests, point pytest at the file directly:

    uv run pytest tests/_deprecated/test_smr_projection.py

The successor projection lives at
``src/lobby_analysis/projections/pri_2010.py`` (tested in
``tests/projections/test_pri_2010_*.py``).

----- Original docstring -----

Tests for the PRI-data → StateMasterRecord projection (Stage B).

Plan: docs/active/statute-retrieval/plans/20260430_compendium_population_and_smr_fill.md

Synthetic-row unit tests cover each helper. Real-artifact integration tests
project the on-disk CA/TX/OH PRI score CSVs and validate the resulting SMR
against the pydantic schema.
"""

from __future__ import annotations

import csv
from pathlib import Path

import pytest

from lobby_analysis.compendium_loader import load_v1_compendium_deprecated as load_compendium
from lobby_analysis.models import (
    CompendiumItem,
    FrameworkReference,
    StateMasterRecord,
)
from scoring._deprecated.smr_projection import project_pri_scores_to_smr


REPO_ROOT = Path(__file__).resolve().parents[1]
COMPENDIUM_CSV = REPO_ROOT / "compendium" / "_deprecated" / "v1" / "disclosure_items.csv"

REAL_RUNS = {
    "CA": (2010, "590e9123a624", "California"),
    "TX": (2009, "4fe9774234f3", "Texas"),
    "OH": (2010, "38803d49e32f", "Ohio"),
}


def _real_pri_csv_path(state: str) -> Path:
    vintage, run_id, _ = REAL_RUNS[state]
    return REPO_ROOT / "data" / "scores" / state / "statute" / str(vintage) / run_id / "pri_disclosure_law.csv"


def _read_real_pri_rows(state: str) -> list[dict]:
    path = _real_pri_csv_path(state)
    if not path.exists():
        pytest.skip(f"PRI score CSV missing for {state}: {path}")
    with path.open() as f:
        return list(csv.DictReader(f))


def _synthetic_compendium() -> list[CompendiumItem]:
    """Tiny compendium with the rows the unit tests need.

    Mirrors the real compendium's structure (PRI ref carried in
    framework_references, field_path on E-series rows) without
    requiring the full 118-row CSV to be loaded.
    """
    return [
        CompendiumItem(
            id="REG_LOBBYIST",
            name="Lobbyist must register",
            description="Lobbyists.",
            domain="registration",
            data_type="boolean",
            framework_references=[
                FrameworkReference(framework="pri_2010_disclosure", item_id="A1")
            ],
            observable_from_database=False,
        ),
        CompendiumItem(
            id="REG_VOLUNTEER_LOBBYIST",
            name="Volunteer lobbyist must register",
            description="Volunteer lobbyists.",
            domain="registration",
            data_type="boolean",
            framework_references=[
                FrameworkReference(framework="pri_2010_disclosure", item_id="A2")
            ],
            observable_from_database=False,
        ),
        CompendiumItem(
            id="RPT_LOBBYIST_COMPENSATION",
            name="Lobbyist compensation",
            description="Direct lobbying costs.",
            domain="reporting",
            data_type="boolean",
            framework_references=[
                FrameworkReference(framework="pri_2010_disclosure", item_id="E2f_i"),
                FrameworkReference(framework="focal_2024", item_id="7.1"),
                FrameworkReference(framework="sunlight_2015", item_id="compensation"),
            ],
            maps_to_state_master_field="total_compensation",
            maps_to_filing_field="total_compensation",
            observable_from_database=True,
        ),
    ]


def _row(item_id: str, score: int = 0, **overrides) -> dict:
    """Build a synthetic PRI score CSV row."""
    base = {
        "state": "ZZ",
        "rubric_name": "pri_disclosure_law",
        "item_id": item_id,
        "score": str(score),
        "evidence_quote_or_url": "",
        "source_artifact": "",
        "confidence": "high",
        "unable_to_evaluate": "false",
        "notes": "",
        "coverage_tier": "clean",
        "model_version": "claude-opus-4-7",
        "prompt_sha": "x",
        "rubric_sha": "x",
        "snapshot_manifest_sha": "x",
        "run_id": "test",
        "run_timestamp": "2026-04-30T00:00:00+00:00",
    }
    base.update({k: str(v) for k, v in overrides.items()})
    return base


def _project(rows: list[dict], compendium: list[CompendiumItem] | None = None) -> StateMasterRecord:
    return project_pri_scores_to_smr(
        pri_score_rows=rows,
        compendium=compendium if compendium is not None else _synthetic_compendium(),
        state="ZZ",
        state_name="Testland",
        vintage=2010,
        run_id="test",
    )


# -----------------------------------------------------------------------------
# Registration requirements (A-series)
# -----------------------------------------------------------------------------


def test_project_a1_lobbyist_required_yields_registration_requirement() -> None:
    smr = _project([_row("A1", score=1)])
    matches = [r for r in smr.registration_requirements if r.role == "lobbyist"]
    assert len(matches) == 1
    assert matches[0].required is True


def test_project_a2_volunteer_not_required_yields_registration_requirement_required_false() -> None:
    """Negative signal preserved (Track B needs to know 'state explicitly does not require X')."""
    smr = _project([_row("A2", score=0)])
    matches = [r for r in smr.registration_requirements if r.role == "volunteer_lobbyist"]
    assert len(matches) == 1
    assert matches[0].required is False


# -----------------------------------------------------------------------------
# De-minimis (D-series)
# -----------------------------------------------------------------------------


def test_project_d_with_threshold_present() -> None:
    smr = _project(
        [
            _row("D0", score=1),
            _row("D1_present", score=1),
            _row("D1_value", score=200, evidence_quote_or_url="§305.001"),
        ]
    )
    assert smr.de_minimis_financial_threshold == 200.0


def test_project_d_with_no_threshold() -> None:
    smr = _project(
        [
            _row("D0", score=0),
            _row("D1_present", score=0),
            _row("D1_value", score=0),
        ]
    )
    assert smr.de_minimis_financial_threshold is None


# -----------------------------------------------------------------------------
# Reporting party (E1a / E2a) and frequency (E1h_*)
# -----------------------------------------------------------------------------


def test_project_e1a_creates_client_activity_reporting_party() -> None:
    smr = _project([_row("E1a", score=1)])
    matches = [
        r for r in smr.reporting_parties
        if r.entity_role == "client" and r.report_type == "activity_report"
    ]
    assert len(matches) == 1
    assert matches[0].filing_status == "required"


def test_project_eh_frequency_picks_quarterly() -> None:
    smr = _project(
        [
            _row("E1a", score=1),
            _row("E1h_i", score=0),
            _row("E1h_ii", score=1),
            _row("E1h_iii", score=0),
            _row("E1h_iv", score=0),
            _row("E1h_v", score=0),
        ]
    )
    matches = [r for r in smr.reporting_parties if r.entity_role == "client"]
    assert len(matches) == 1
    assert matches[0].reporting_frequency == "quarterly"


def test_project_eh_frequency_multiple_yields_other_with_notes() -> None:
    """Per plan B.5 STOP-AND-NOTIFY clause.

    On synthetic input the projection does not pause (it can't); it should
    emit `reporting_frequency='other'` with a notes field annotating which
    frequencies were set. The pause-and-surface is for the build-smr CLI
    when run on real data — tested separately.
    """
    smr = _project(
        [
            _row("E1a", score=1),
            _row("E1h_i", score=1),
            _row("E1h_ii", score=1),
            _row("E1h_iii", score=0),
            _row("E1h_iv", score=0),
            _row("E1h_v", score=0),
        ]
    )
    matches = [r for r in smr.reporting_parties if r.entity_role == "client"]
    assert len(matches) == 1
    rp = matches[0]
    assert rp.reporting_frequency == "other"
    assert "monthly" in rp.notes.lower() and "quarterly" in rp.notes.lower()


# -----------------------------------------------------------------------------
# Field requirements (E1b–E1g, E1i, E1j, and E2 counterparts)
# -----------------------------------------------------------------------------


def test_project_field_requirement_carries_compendium_framework_references() -> None:
    """Compendium union is preserved on the SMR row.

    Compendium item RPT_LOBBYIST_COMPENSATION refs PRI E2f_i + FOCAL 7.1 +
    Sunlight compensation. The projected FieldRequirement must carry all three.
    """
    smr = _project(
        [_row("E2f_i", score=1, evidence_quote_or_url="some quote")],
        compendium=_synthetic_compendium(),
    )
    matches = [r for r in smr.field_requirements if r.field_path == "total_compensation"]
    assert len(matches) == 1
    fw_set = {(ref.framework, ref.item_id) for ref in matches[0].framework_references}
    assert ("pri_2010_disclosure", "E2f_i") in fw_set
    assert ("focal_2024", "7.1") in fw_set
    assert ("sunlight_2015", "compensation") in fw_set


def test_project_field_requirement_score_zero_yields_not_applicable() -> None:
    smr = _project(
        [_row("E2f_i", score=0)],
        compendium=_synthetic_compendium(),
    )
    matches = [r for r in smr.field_requirements if r.field_path == "total_compensation"]
    assert len(matches) == 1
    assert matches[0].status == "not_applicable"


def test_project_field_requirement_carries_legal_citation() -> None:
    smr = _project(
        [_row("E2f_i", score=1, evidence_quote_or_url="§305.006(a)(1)")],
        compendium=_synthetic_compendium(),
    )
    matches = [r for r in smr.field_requirements if r.field_path == "total_compensation"]
    assert len(matches) == 1
    assert matches[0].legal_citation is not None
    assert "305.006" in matches[0].legal_citation


# -----------------------------------------------------------------------------
# Real-artifact integration tests (CA / TX / OH)
# -----------------------------------------------------------------------------


@pytest.mark.parametrize("state", ["CA", "TX", "OH"])
def test_project_full_smr_validates_against_schema(state: str) -> None:
    rows = _read_real_pri_rows(state)
    if not COMPENDIUM_CSV.exists():
        pytest.skip(f"compendium missing at {COMPENDIUM_CSV}")
    compendium = load_compendium(COMPENDIUM_CSV)
    vintage, run_id, state_name = REAL_RUNS[state]

    smr = project_pri_scores_to_smr(
        pri_score_rows=rows,
        compendium=compendium,
        state=state,
        state_name=state_name,
        vintage=vintage,
        run_id=run_id,
    )

    assert isinstance(smr, StateMasterRecord)
    assert smr.state == state
    assert smr.state_name == state_name
    assert len(smr.registration_requirements) > 0, "expected non-empty registration_requirements"
    assert len(smr.reporting_parties) > 0, "expected non-empty reporting_parties"
    assert len(smr.field_requirements) > 0, "expected non-empty field_requirements"


def test_project_full_smr_round_trips_through_json() -> None:
    rows = _read_real_pri_rows("OH")
    if not COMPENDIUM_CSV.exists():
        pytest.skip(f"compendium missing at {COMPENDIUM_CSV}")
    compendium = load_compendium(COMPENDIUM_CSV)
    vintage, run_id, state_name = REAL_RUNS["OH"]

    smr = project_pri_scores_to_smr(
        pri_score_rows=rows,
        compendium=compendium,
        state="OH",
        state_name=state_name,
        vintage=vintage,
        run_id=run_id,
    )

    blob = smr.model_dump_json()
    parsed = StateMasterRecord.model_validate_json(blob)

    assert parsed.state == smr.state
    assert parsed.state_name == smr.state_name
    assert len(parsed.registration_requirements) == len(smr.registration_requirements)
    assert len(parsed.reporting_parties) == len(smr.reporting_parties)
    assert len(parsed.field_requirements) == len(smr.field_requirements)


def test_project_oh_field_requirements_carry_sunlight_refs_for_compensation() -> None:
    """Plan B.6.9 spot-check: lobbyist-compensation FieldRequirement should
    carry both PRI and Sunlight references via the compendium union.

    OH's per-item PRI says E2f_i is required; the compendium row for
    RPT_LOBBYIST_COMPENSATION references PRI + FOCAL 7.1 + Sunlight, so the
    projected FieldRequirement carries all three.
    """
    rows = _read_real_pri_rows("OH")
    if not COMPENDIUM_CSV.exists():
        pytest.skip(f"compendium missing at {COMPENDIUM_CSV}")
    compendium = load_compendium(COMPENDIUM_CSV)
    smr = project_pri_scores_to_smr(
        pri_score_rows=rows,
        compendium=compendium,
        state="OH",
        state_name="Ohio",
        vintage=2010,
        run_id="38803d49e32f",
    )

    comp_rows = [
        r for r in smr.field_requirements
        if r.field_path == "total_compensation" and r.reporting_party == "lobbyist"
    ]
    assert len(comp_rows) == 1
    fw_names = {ref.framework for ref in comp_rows[0].framework_references}
    assert "pri_2010_disclosure" in fw_names
    assert "sunlight_2015" in fw_names
