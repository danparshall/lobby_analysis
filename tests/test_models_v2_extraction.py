"""Tests for `lobby_analysis.models_v2.extraction.StateVintageExtraction`
and `ExtractionRun` (Phase 6).
"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest
from pydantic import ValidationError


def test_state_vintage_extraction_validates_with_empty_cells():
    """A blank container is valid (extraction not started yet)."""
    from lobby_analysis.models_v2.extraction import StateVintageExtraction

    ext = StateVintageExtraction(
        state="OH",
        vintage=2025,
        run_id="test_run_001",
        cells={},
    )
    assert ext.state == "OH"
    assert ext.vintage == 2025
    assert ext.run_id == "test_run_001"
    assert ext.cells == {}


def test_state_vintage_extraction_round_trips_a_populated_cell():
    """A cell stored under (row_id, axis) round-trips with its value intact."""
    from lobby_analysis.models_v2.cells import BinaryCell
    from lobby_analysis.models_v2.extraction import StateVintageExtraction

    key = ("lobbyist_spending_report_includes_total_compensation", "legal")
    cell = BinaryCell(cell_id=key, value=True)
    ext = StateVintageExtraction(
        state="OH",
        vintage=2025,
        run_id="r1",
        cells={key: cell},
    )
    assert ext.cells[key].value is True


def test_state_vintage_extraction_rejects_mismatched_cell_id_key():
    """OUR rule: each cell's cell_id MUST match the dict key it's stored under.
    Drift between key and cell_id is a serious extraction bug; surface it as a
    validation error at construction time.
    """
    from lobby_analysis.models_v2.cells import BinaryCell
    from lobby_analysis.models_v2.extraction import StateVintageExtraction

    key = ("row_a", "legal")
    cell = BinaryCell(cell_id=("row_B_different", "legal"), value=True)
    with pytest.raises(ValidationError):
        StateVintageExtraction(state="OH", vintage=2025, run_id="r1", cells={key: cell})


# ---------------------------------------------------------------------------
# ExtractionRun
# ---------------------------------------------------------------------------


def test_extraction_run_validates_with_required_fields():
    from lobby_analysis.models_v2.extraction import ExtractionRun

    run = ExtractionRun(
        run_id="r1",
        model_version="claude-opus-4-7",
        prompt_sha="abc123",
        started_at=datetime(2026, 5, 14, 9, 0, 0, tzinfo=timezone.utc),
    )
    assert run.run_id == "r1"
    assert run.completed_at is None


def test_extraction_run_serializes_and_deserializes_via_json():
    """OUR rule: ExtractionRun must round-trip JSON so it can be persisted with
    extraction outputs. Datetime + sha hash + model_version must all survive."""
    from lobby_analysis.models_v2.extraction import ExtractionRun

    original = ExtractionRun(
        run_id="r1",
        model_version="claude-opus-4-7",
        prompt_sha="abc123def456",
        started_at=datetime(2026, 5, 14, 9, 0, 0, tzinfo=timezone.utc),
        completed_at=datetime(2026, 5, 14, 9, 5, 0, tzinfo=timezone.utc),
    )
    payload = original.model_dump_json()
    restored = ExtractionRun.model_validate_json(payload)
    assert restored == original
