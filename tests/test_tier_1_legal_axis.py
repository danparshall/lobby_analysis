"""Behavior tests for the Tier-1 direct-read legal-axis run.

Plan: docs/active/extraction-harness-brainstorm/plans/20260520_tier_1_direct_read_legal_axis.md

Four behavior-focused groups (no datastructure tests, no mocks):

1. ``_instantiate_cell`` value coercion — JSON-string scalars coerce to the
   target Python type of the real ``models_v2`` cell class; uncoercible
   strings raise (so the runner records them as errors, never silently).
2. ``build_legal_roster`` — a mixed chunk yields only its ``axis=='legal'``
   cells; zero practical cells leak through.
3. ``classify_cell_runs`` / ``summarize_sigma_noise`` — the inter-run
   agreement metric classifies stable / value-unstable /
   scoreability-unstable, and reports numeric spread.
4. ``is_dispatch_done`` — the resume-skip predicate detects an
   already-written dispatch result and does not re-dispatch it.

Both scripts are single-file (YAGNI); this module loads them via
``importlib.util.spec_from_file_location``.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

_SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
_TIER_0_PATH = _SCRIPTS / "tier_0_direct_read_smoke.py"
_TIER_1_PATH = _SCRIPTS / "tier_1_direct_read_legal_axis.py"


def _load(module_name: str, path: Path):
    spec = importlib.util.spec_from_file_location(module_name, path)
    assert spec is not None and spec.loader is not None, f"could not load {path}"
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


tier0 = _load("tier_0_direct_read_smoke", _TIER_0_PATH)
tier1 = _load("tier_1_direct_read_legal_axis", _TIER_1_PATH)


# ---------------------------------------------------------------------------
# Group 1 — _instantiate_cell value coercion (Step 2)
# ---------------------------------------------------------------------------


def _spec(row_id: str, axis: str):
    """Fetch a real CompendiumCellSpec from the live v2 registry."""
    from lobby_analysis.models_v2 import build_cell_spec_registry

    registry = build_cell_spec_registry()
    spec = registry.get((row_id, axis))
    assert spec is not None, f"({row_id!r}, {axis!r}) not in registry"
    return spec


def _record_cell_args(value, **overrides):
    args = {
        "value": value,
        "condition_text": None,
        "confidence": "high",
        "cited_section": "§101.70",
        "justification": "test fixture justification.",
    }
    args.update(overrides)
    return args


def test_coerce_string_to_int_for_gradedintcell():
    """A JSON-string '50' for a GradedIntCell coerces to int 50.

    (Plan Step 6 names value='2'; GradedIntCell's grid validator rejects 2
    regardless of coercion, so an on-grid value is used — see plan note.)
    """
    spec = _spec("lobbying_data_open_data_quality", "practical")
    assert spec.expected_cell_class.__name__ == "GradedIntCell"
    result = tier0._instantiate_cell(spec, _record_cell_args("50"))
    assert result["cell"]["value"] == 50
    assert isinstance(result["cell"]["value"], int)


def test_coerce_string_to_int_for_intcell():
    """A JSON-string '2' for a plain IntCell coerces to int 2."""
    spec = _spec("lobbying_disclosure_offline_request_response_time_days", "practical")
    assert spec.expected_cell_class.__name__ == "IntCell"
    result = tier0._instantiate_cell(spec, _record_cell_args("2"))
    assert result["cell"]["value"] == 2
    assert isinstance(result["cell"]["value"], int)


def test_coerce_string_to_float_for_floatcell():
    """A JSON-string '3.5' for a FloatCell coerces to float 3.5."""
    spec = _spec("lobbyist_filing_de_minimis_threshold_time_percent", "legal")
    assert spec.expected_cell_class.__name__ == "FloatCell"
    result = tier0._instantiate_cell(spec, _record_cell_args("3.5"))
    assert result["cell"]["value"] == 3.5
    assert isinstance(result["cell"]["value"], float)


def test_coerce_string_to_decimal_for_decimalcell():
    """A JSON-string '500' for a DecimalCell coerces to a non-negative Decimal.

    DecimalCell.value is ``Decimal | None`` under strict mode — a float would
    fail validation, so coercion targets Decimal (deviates from the plan's
    'float' prose; see plan note)."""
    spec = _spec("lobbyist_registration_threshold_compensation_dollars", "legal")
    assert spec.expected_cell_class.__name__ == "DecimalCell"
    result = tier0._instantiate_cell(spec, _record_cell_args("500"))
    # model_dump(mode="json") serializes Decimal to a string.
    assert result["cell"]["value"] == "500"


def test_coerce_string_to_bool_for_binarycell():
    """JSON-strings 'true' / 'false' for a BinaryCell coerce to bool."""
    spec = _spec("actor_executive_agency_registration_required", "legal")
    assert spec.expected_cell_class.__name__ == "BinaryCell"
    assert tier0._instantiate_cell(spec, _record_cell_args("true"))["cell"]["value"] is True
    assert tier0._instantiate_cell(spec, _record_cell_args("false"))["cell"]["value"] is False


def test_correct_type_value_passes_through_unchanged():
    """An already-typed value is not mangled by the coercion step."""
    spec = _spec("lobbying_data_open_data_quality", "practical")
    result = tier0._instantiate_cell(spec, _record_cell_args(50))
    assert result["cell"]["value"] == 50


def test_uncoercible_string_raises_rather_than_swallows():
    """'banana' for an int cell must raise — the runner records it as an
    error; coercion never silently passes a bad value."""
    spec = _spec("lobbying_disclosure_offline_request_response_time_days", "practical")
    with pytest.raises((ValueError, TypeError)):
        tier0._instantiate_cell(spec, _record_cell_args("banana"))


# ---------------------------------------------------------------------------
# Group 2 — legal-axis roster filter (Step 3)
# ---------------------------------------------------------------------------


def _chunk(chunk_id: str):
    from lobby_analysis.chunks_v2 import build_chunks

    chunks = {c.chunk_id: c for c in build_chunks()}
    assert chunk_id in chunks, f"chunk {chunk_id!r} not in manifest"
    return chunks[chunk_id]


def test_legal_roster_drops_practical_cells_from_mixed_chunk():
    """enforcement_and_audits is a mixed chunk (2 legal + 2 practical).
    The legal roster contains exactly the 2 legal cells, zero practical."""
    chunk = _chunk("enforcement_and_audits")
    roster = tier1.build_legal_roster(chunk)
    assert len(roster) == 2
    assert all(spec.axis == "legal" for spec in roster)
    assert not any(spec.axis == "practical" for spec in roster)


def test_legal_roster_keeps_all_cells_of_a_pure_legal_chunk():
    """registration_thresholds is pure-legal (6 cells); none are dropped."""
    chunk = _chunk("registration_thresholds")
    roster = tier1.build_legal_roster(chunk)
    assert len(roster) == len(chunk.cell_specs) == 6
    assert all(spec.axis == "legal" for spec in roster)


# ---------------------------------------------------------------------------
# Group 3 — inter-run agreement / sigma_noise metric (Step 5)
# ---------------------------------------------------------------------------


def _scored(value):
    return tier1.CellOutcome(status="scored", value=value)


_ABSTAINED = None  # set in module init below


def test_agreement_three_equal_values_is_stable():
    runs = [_scored(2), _scored(2), _scored(2)]
    result = tier1.classify_cell_runs(runs)
    assert result["stability"] == "stable"


def test_agreement_differing_values_is_value_unstable_with_spread():
    runs = [_scored(2), _scored(2), _scored(3)]
    result = tier1.classify_cell_runs(runs)
    assert result["stability"] == "value-unstable"
    spread = result["numeric_spread"]
    assert spread["min"] == 2
    assert spread["max"] == 3
    assert spread["stdev"] == pytest.approx(0.5773, abs=1e-3)


def test_agreement_score_then_abstain_is_scoreability_unstable():
    runs = [_scored(2), _scored(2), tier1.CellOutcome(status="abstained")]
    result = tier1.classify_cell_runs(runs)
    assert result["stability"] == "scoreability-unstable"


def test_agreement_all_abstained_is_stable():
    runs = [tier1.CellOutcome(status="abstained")] * 3
    result = tier1.classify_cell_runs(runs)
    assert result["stability"] == "stable"


def test_agreement_errored_run_is_incomplete():
    runs = [_scored(2), _scored(2), tier1.CellOutcome(status="errored")]
    result = tier1.classify_cell_runs(runs)
    assert result["stability"] == "incomplete"


def test_summarize_sigma_noise_reports_pct_stable():
    """3 of 4 cells stable → 75% stable."""
    classifications = {
        ("a", "legal"): {"stability": "stable", "numeric_spread": None},
        ("b", "legal"): {"stability": "stable", "numeric_spread": None},
        ("c", "legal"): {"stability": "stable", "numeric_spread": None},
        ("d", "legal"): {"stability": "value-unstable", "numeric_spread": None},
    }
    summary = tier1.summarize_sigma_noise(classifications)
    assert summary["n_cells"] == 4
    assert summary["n_stable"] == 3
    assert summary["pct_stable"] == pytest.approx(75.0)


# ---------------------------------------------------------------------------
# Group 4 — resume-skip predicate (Step 4)
# ---------------------------------------------------------------------------


def test_is_dispatch_done_true_when_result_file_present(tmp_path):
    """A pre-placed result file makes is_dispatch_done report True for that
    triple — the runner skips it instead of re-dispatching."""
    model, chunk_id, run_idx = "claude-opus-4-7", "registration_thresholds", 1
    path = tier1.dispatch_result_path(tmp_path, model, chunk_id, run_idx)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"provenance": {}}), encoding="utf-8")
    assert tier1.is_dispatch_done(tmp_path, model, chunk_id, run_idx) is True


def test_is_dispatch_done_false_for_undispatched_triple(tmp_path):
    """A triple with no result file is reported not-done — it gets dispatched."""
    assert tier1.is_dispatch_done(tmp_path, "gpt-5.2-2025-12-11", "registration_thresholds", 2) is False


def test_dispatch_result_path_is_unique_per_triple(tmp_path):
    """Each (model, chunk, run) maps to a distinct path so dispatches never
    overwrite each other."""
    paths = {
        tier1.dispatch_result_path(tmp_path, model, chunk, run)
        for model in ("claude-opus-4-7", "gpt-5.2-2025-12-11")
        for chunk in ("registration_thresholds", "enforcement_and_audits")
        for run in (1, 2, 3)
    }
    assert len(paths) == 12
