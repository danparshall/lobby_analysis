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
from decimal import Decimal
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
    assert (
        tier1.is_dispatch_done(tmp_path, "gpt-5.2-2025-12-11", "registration_thresholds", 2)
        is False
    )


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


# ---------------------------------------------------------------------------
# Group 5 — Tier-2 schema/adapter fixes
# (plan: docs/active/extraction-harness-brainstorm/plans/
#         20260521_tier_2_schema_adapter_fixes.md)
# ---------------------------------------------------------------------------


# --- Fix A: int / float -> Decimal coercion -------------------------------


def test_coerce_int_to_decimal_for_decimalcell():
    """A bare JSON int (50) for a DecimalCell coerces to Decimal.

    The Tier-1 'emit numbers as JSON numbers' nudge made GPT emit a bare
    int; CompendiumCell strict mode rejects an int for a Decimal field."""
    spec = _spec("lobbyist_registration_threshold_compensation_dollars", "legal")
    assert spec.expected_cell_class.__name__ == "DecimalCell"
    result = tier0._instantiate_cell(spec, _record_cell_args(50))
    # model_dump(mode="json") serializes Decimal to a string.
    assert result["cell"]["value"] == "50"


def test_coerce_float_to_decimal_for_decimalcell():
    """A bare JSON float (50.5) coerces to an exact Decimal (via str(), so no
    binary-float artifact: Decimal(0.1) is wrong, Decimal('0.1') is right)."""
    spec = _spec("lobbyist_registration_threshold_compensation_dollars", "legal")
    result = tier0._instantiate_cell(spec, _record_cell_args(50.5))
    assert result["cell"]["value"] == "50.5"


def test_bool_value_not_coerced_to_decimal():
    """bool is an int subclass but never a valid threshold — it must not be
    coerced; strict-mode validation rejects it loudly instead."""
    spec = _spec("lobbyist_registration_threshold_compensation_dollars", "legal")
    with pytest.raises((ValueError, TypeError)):
        tier0._instantiate_cell(spec, _record_cell_args(True))


def test_coerce_scalar_value_int_and_float_directly():
    """_coerce_scalar_value returns an exact Decimal for a non-string int /
    float passed for a DecimalCell."""
    from lobby_analysis.models_v2 import DecimalCell

    int_result = tier0._coerce_scalar_value(DecimalCell, 50)
    assert isinstance(int_result, Decimal)
    assert int_result == Decimal("50")

    float_result = tier0._coerce_scalar_value(DecimalCell, 50.5)
    assert isinstance(float_result, Decimal)
    assert float_result == Decimal("50.5")
    assert str(float_result) == "50.5"


def test_coerce_scalar_value_leaves_bool_uncoerced():
    """A bool passed for a DecimalCell is returned untouched (not a Decimal),
    so strict-mode validation can reject it downstream."""
    from lobby_analysis.models_v2 import DecimalCell

    assert tier0._coerce_scalar_value(DecimalCell, True) is True


# --- Fix B: dict-shape value prompt hint ----------------------------------


def test_legal_roster_names_dict_keys_for_dict_shape_cell():
    """A TimeThresholdCell roster line names its JSON-object keys (magnitude,
    unit) so the model emits a dict, not a bare scalar (error class B)."""
    spec = _spec("lobbyist_registration_threshold_time_percent", "legal")
    assert spec.expected_cell_class.__name__ == "TimeThresholdCell"
    roster = tier1.render_legal_roster("registration_thresholds", "thresholds", [spec])
    assert "magnitude" in roster
    assert "unit" in roster
    assert "JSON object" in roster


def test_legal_roster_adds_no_shape_hint_for_scalar_cell():
    """A scalar cell (BinaryCell) gets no dict-shape hint — the hint must not
    push a scalar cell toward fabricating an object."""
    spec = _spec("actor_executive_agency_registration_required", "legal")
    assert spec.expected_cell_class.__name__ == "BinaryCell"
    roster = tier1.render_legal_roster("registration", "reg", [spec])
    assert "JSON object" not in roster
    assert "magnitude" not in roster


# --- Fix C: null-valued FreeTextCell routed to abstention -----------------


def _record_cell_response(row_id: str, axis: str, value):
    """An Anthropic-shaped response dict carrying one record_cell tool call.

    parse_anthropic_response reads dicts via _attr_or_key, so a plain dict in
    the wire shape exercises _parse_and_instantiate with no SDK object and no
    API call."""
    return {
        "content": [
            {
                "type": "tool_use",
                "name": "record_cell",
                "input": {
                    "row_id": row_id,
                    "axis": axis,
                    "value": value,
                    "condition_text": None,
                    "confidence": "high",
                    "cited_section": "§101.70",
                    "justification": "test fixture justification.",
                },
            }
        ]
    }


def test_null_freetext_record_cell_routed_to_abstention():
    """A record_cell with value:null for a FreeTextCell row is routed to the
    unscoreable list as an abstention — not the errors list. The conditional
    *_other_specification rows correctly emit null; the schema cannot hold it."""
    from lobby_analysis.models_v2 import build_cell_spec_registry

    registry = build_cell_spec_registry()
    response = _record_cell_response(
        "lobbyist_spending_report_cadence_other_specification", "legal", None
    )
    instantiated, unscoreable, errors = tier1._parse_and_instantiate(
        response, "anthropic", registry
    )
    assert errors == []
    assert instantiated == []
    assert len(unscoreable) == 1
    abstained = unscoreable[0]
    assert abstained["row_id"] == "lobbyist_spending_report_cadence_other_specification"
    assert abstained["axis"] == "legal"
    assert "reason" in abstained


def test_nonnull_freetext_record_cell_still_instantiates():
    """A FreeTextCell record_cell with a real string value instantiates
    normally — the null sentinel must not intercept genuine values."""
    from lobby_analysis.models_v2 import build_cell_spec_registry

    registry = build_cell_spec_registry()
    response = _record_cell_response(
        "lobbyist_spending_report_cadence_other_specification", "legal", "biennial"
    )
    instantiated, unscoreable, errors = tier1._parse_and_instantiate(
        response, "anthropic", registry
    )
    assert errors == []
    assert unscoreable == []
    assert len(instantiated) == 1


def test_null_decimalcell_record_cell_not_routed_to_abstention():
    """The null sentinel is FreeTextCell-specific: a DecimalCell genuinely
    accepts value:null (Decimal | None), so it instantiates, not abstains."""
    from lobby_analysis.models_v2 import build_cell_spec_registry

    registry = build_cell_spec_registry()
    response = _record_cell_response(
        "lobbyist_registration_threshold_compensation_dollars", "legal", None
    )
    instantiated, unscoreable, errors = tier1._parse_and_instantiate(
        response, "anthropic", registry
    )
    assert errors == []
    assert unscoreable == []
    assert len(instantiated) == 1
