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


# --- Fix A (dict-shape extension): inner-Decimal-field coercion -----------
# Regression evidence: WI 2025 §13.62(11) emitted
#   {"magnitude": 5, "unit": "..."}
# all 6/6 runs and failed instantiation with "Input should be an instance of
# Decimal" on the `magnitude` field. Fix A originally covered the outer scalar
# `DecimalCell.value` path; the dict-shape branch in `_instantiate_cell`
# (TimeThresholdCell / TimeSpentCell / EnumSetWithAmountsCell / CountWithFTECell)
# unpacks `raw_value` directly into the constructor and never runs any per-field
# coercion, so a bare int `magnitude` reaches Pydantic strict mode unchanged and
# fails. Plan: docs/active/wi-tier1-direct-read/plans/
#   20260601_post_phase3_followups.md, Item 1.
#
# Tests use unit="days_per_year" (a valid TimeUnitLiteral) to isolate the
# magnitude coercion from item 2's enum-gap on "days_per_reporting_period".


def test_coerce_int_magnitude_to_decimal_for_timethresholdcell():
    """A bare JSON int magnitude (5) inside a TimeThresholdCell dict-shape
    value coerces to Decimal — same Fix A semantics that already cover scalar
    DecimalCell, now extended to inner Decimal fields on dict-shape cells."""
    spec = _spec("lobbyist_registration_threshold_time_percent", "legal")
    assert spec.expected_cell_class.__name__ == "TimeThresholdCell"
    args = _record_cell_args({"magnitude": 5, "unit": "days_per_year"})
    result = tier0._instantiate_cell(spec, args)
    # model_dump(mode="json") serializes Decimal to a string.
    assert result["cell"]["magnitude"] == "5"
    assert result["cell"]["unit"] == "days_per_year"


def test_coerce_float_magnitude_to_decimal_for_timethresholdcell():
    """A bare JSON float magnitude (5.5) coerces to an exact Decimal (via str(),
    so no binary-float artifact: Decimal(0.1) is wrong, Decimal('0.1') is right)
    on a TimeThresholdCell."""
    spec = _spec("lobbyist_registration_threshold_time_percent", "legal")
    args = _record_cell_args({"magnitude": 5.5, "unit": "days_per_year"})
    result = tier0._instantiate_cell(spec, args)
    assert result["cell"]["magnitude"] == "5.5"


def test_bool_magnitude_not_coerced_to_decimal_for_timethresholdcell():
    """bool is an int subclass but never a valid magnitude — strict-mode must
    reject it loudly (parallel to the scalar bool-uncoerced test)."""
    spec = _spec("lobbyist_registration_threshold_time_percent", "legal")
    args = _record_cell_args({"magnitude": True, "unit": "days_per_year"})
    with pytest.raises((ValueError, TypeError)):
        tier0._instantiate_cell(spec, args)


# --- Fix B: dict-shape value prompt hint ----------------------------------


def test_legal_roster_names_dict_keys_for_dict_shape_cell():
    """A TimeThresholdCell roster line names its JSON-object keys (magnitude,
    unit) so the model emits a dict, not a bare scalar (error class B).

    Renderer return is ``(message, handle_to_row_id_map)`` per the wide-pass
    refactor; the message string is the first element of the tuple."""
    spec = _spec("lobbyist_registration_threshold_time_percent", "legal")
    assert spec.expected_cell_class.__name__ == "TimeThresholdCell"
    message, _handles = tier1.render_legal_roster(
        "registration_thresholds", "thresholds", [spec]
    )
    assert "magnitude" in message
    assert "unit" in message
    assert "JSON object" in message


def test_legal_roster_adds_no_shape_hint_for_scalar_cell():
    """A scalar cell (BinaryCell) gets no dict-shape hint — the hint must not
    push a scalar cell toward fabricating an object."""
    spec = _spec("actor_executive_agency_registration_required", "legal")
    assert spec.expected_cell_class.__name__ == "BinaryCell"
    message, _handles = tier1.render_legal_roster("registration", "reg", [spec])
    assert "JSON object" not in message
    assert "magnitude" not in message


# --- Fix C: null-valued FreeTextCell routed to abstention -----------------


def _record_cell_response(handle: str, axis: str, value, *, tool_name: str = "record_cell"):
    """An Anthropic-shaped response dict carrying one tool call.

    Wire-format slot is ``handle`` (renamed from ``row_id`` in the wide-pass
    refactor — tier-1 owns its own tool schemas with opaque handles instead
    of leaking compendium row_ids to the model).

    parse_anthropic_response reads dicts via _attr_or_key, so a plain dict in
    the wire shape exercises _parse_and_instantiate with no SDK object and no
    API call."""
    return {
        "content": [
            {
                "type": "tool_use",
                "name": tool_name,
                "input": {
                    "handle": handle,
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


def _record_unscoreable_response(handle: str, axis: str, reason: str):
    """Anthropic-shaped response dict carrying one record_unscoreable_cell."""
    return {
        "content": [
            {
                "type": "tool_use",
                "name": "record_unscoreable_cell",
                "input": {
                    "handle": handle,
                    "axis": axis,
                    "reason": reason,
                },
            }
        ]
    }


def test_null_freetext_record_cell_routed_to_abstention():
    """A record_cell with value:null for a FreeTextCell row is routed to the
    unscoreable list as an abstention — not the errors list. The conditional
    *_other_specification rows correctly emit null; the schema cannot hold it.

    Parser signature now accepts a handle→row_id map; the test fixture maps
    one synthetic handle to the target row_id."""
    from lobby_analysis.models_v2 import build_cell_spec_registry

    registry = build_cell_spec_registry()
    target_row_id = "lobbyist_spending_report_cadence_other_specification"
    handle_map = {"row_001": target_row_id}
    response = _record_cell_response("row_001", "legal", None)
    instantiated, unscoreable, errors = tier1._parse_and_instantiate(
        response, "anthropic", registry, handle_map
    )
    assert errors == []
    assert instantiated == []
    assert len(unscoreable) == 1
    abstained = unscoreable[0]
    assert abstained["row_id"] == target_row_id
    assert abstained["axis"] == "legal"
    assert "reason" in abstained


def test_nonnull_freetext_record_cell_still_instantiates():
    """A FreeTextCell record_cell with a real string value instantiates
    normally — the null sentinel must not intercept genuine values."""
    from lobby_analysis.models_v2 import build_cell_spec_registry

    registry = build_cell_spec_registry()
    target_row_id = "lobbyist_spending_report_cadence_other_specification"
    handle_map = {"row_001": target_row_id}
    response = _record_cell_response("row_001", "legal", "biennial")
    instantiated, unscoreable, errors = tier1._parse_and_instantiate(
        response, "anthropic", registry, handle_map
    )
    assert errors == []
    assert unscoreable == []
    assert len(instantiated) == 1


def test_null_decimalcell_record_cell_not_routed_to_abstention():
    """The null sentinel is FreeTextCell-specific: a DecimalCell genuinely
    accepts value:null (Decimal | None), so it instantiates, not abstains."""
    from lobby_analysis.models_v2 import build_cell_spec_registry

    registry = build_cell_spec_registry()
    target_row_id = "lobbyist_registration_threshold_compensation_dollars"
    handle_map = {"row_001": target_row_id}
    response = _record_cell_response("row_001", "legal", None)
    instantiated, unscoreable, errors = tier1._parse_and_instantiate(
        response, "anthropic", registry, handle_map
    )
    assert errors == []
    assert unscoreable == []
    assert len(instantiated) == 1


# ---------------------------------------------------------------------------
# Group 6 — Wide-pass renderer: opaque handles instead of row_ids
# (plan: docs/active/wi-tier1-direct-read/plans/
#         20260604_wide_prompt_text_pass.md, Commit 1)
# ---------------------------------------------------------------------------


def _narrow_pass_anchor_spec():
    """Pattern A anchor row — has a populated ``prompt`` after Commit 1's
    YAML migration. Used by renderer tests that need a spec with a prompt."""
    return _spec("lobbyist_spending_report_required", "legal")


def test_render_legal_roster_returns_tuple_of_message_and_handle_map():
    """``render_legal_roster`` returns ``(message, handle_to_row_id_map)`` —
    the dispatch handler consumes both halves: the message goes to the model,
    the map decodes the model's handle-keyed responses back to row_ids."""
    spec = _narrow_pass_anchor_spec()
    result = tier1.render_legal_roster("lobbyist_spending_report", "topic", [spec])
    assert isinstance(result, tuple)
    assert len(result) == 2
    message, handle_map = result
    assert isinstance(message, str)
    assert isinstance(handle_map, dict)


def test_render_legal_roster_uses_opaque_handles_not_row_ids():
    """LOAD-BEARING: the rendered string sends opaque handles (``row_001``,
    ``row_002``, …) and does NOT contain the row's ``compendium_row_id``.
    The row name is the Pattern A bug surface; suppressing it from the
    model's view is the wide-pass forcing function for prompt quality."""
    rows = [
        "lobbyist_spending_report_required",
        "lobbyist_spending_report_includes_total_compensation",
        "lobbyist_spending_report_includes_principal_names",
    ]
    specs = [_spec(rid, "legal") for rid in rows]
    message, _handle_map = tier1.render_legal_roster(
        "lobbyist_spending_report", "topic", specs
    )
    # Handles present
    assert "row_001" in message
    assert "row_002" in message
    assert "row_003" in message
    # Compendium row_ids absent — this is the forcing-function assertion.
    for row_id in rows:
        assert row_id not in message, (
            f"row_id {row_id!r} leaked into rendered message — opaque-handle "
            f"contract violated.\nmessage=\n{message}"
        )


def test_render_legal_roster_emits_substantive_prompt_per_row():
    """Each row in the chunk gets its YAML-sourced ``prompt`` emitted in the
    rendered message. Asserted on the Pattern A anchor (populated in
    Commit 1)."""
    spec = _narrow_pass_anchor_spec()
    assert spec.prompt, "test precondition: anchor spec must carry a prompt"
    message, _ = tier1.render_legal_roster(
        "lobbyist_spending_report", "topic", [spec]
    )
    # A distinctive verbatim phrase from the anchor's source quote.
    assert "itemized spending reports" in message, (
        f"renderer did not emit substantive prompt content for "
        f"{spec.row_id!r}; message=\n{message}"
    )


def test_render_legal_roster_handles_are_zero_padded_three_digits():
    """Handles use ``row_NNN`` with three-digit zero padding so lexical sort
    matches numeric sort and the format scales to 999 rows per chunk
    (current max chunk ≈ 24)."""
    specs = [_narrow_pass_anchor_spec() for _ in range(3)]
    _msg, handle_map = tier1.render_legal_roster("topic_id", "topic", specs)
    handles = sorted(handle_map.keys())
    assert handles == ["row_001", "row_002", "row_003"], (
        f"handles not zero-padded three-digit: {handles}"
    )


def test_handle_to_row_id_map_is_deterministic_per_chunk():
    """Two independent renders of the same chunk produce the same handle map.
    Necessary so resume-skip + replay produce consistent decoding."""
    rows = [
        "lobbyist_spending_report_required",
        "lobbyist_spending_report_includes_total_compensation",
        "lobbyist_spending_report_includes_principal_names",
    ]
    specs = [_spec(rid, "legal") for rid in rows]
    _, map1 = tier1.render_legal_roster("topic", "topic", specs)
    _, map2 = tier1.render_legal_roster("topic", "topic", specs)
    assert map1 == map2


def test_handle_to_row_id_map_covers_every_spec_in_chunk():
    """Every spec in the input list has exactly one handle entry in the
    returned map, and the values are the specs' row_ids in order."""
    rows = [
        "lobbyist_spending_report_required",
        "lobbyist_spending_report_includes_total_compensation",
        "lobbyist_spending_report_includes_principal_names",
    ]
    specs = [_spec(rid, "legal") for rid in rows]
    _msg, handle_map = tier1.render_legal_roster("topic", "topic", specs)
    assert list(handle_map.values()) == rows


# ---------------------------------------------------------------------------
# Group 7 — Wide-pass parser: handle decoding + handle/row_id validation
# ---------------------------------------------------------------------------


def test_result_parser_maps_handle_to_row_id_via_handle_map():
    """A record_cell emission keyed by ``handle="row_001"`` produces an
    instantiated cell whose ``cell_id`` first element is the original
    ``compendium_row_id`` (decoded via the handle map)."""
    from lobby_analysis.models_v2 import build_cell_spec_registry

    registry = build_cell_spec_registry()
    target_row_id = "actor_executive_agency_registration_required"
    handle_map = {"row_001": target_row_id}
    response = _record_cell_response("row_001", "legal", True)
    instantiated, unscoreable, errors = tier1._parse_and_instantiate(
        response, "anthropic", registry, handle_map
    )
    assert errors == []
    assert unscoreable == []
    assert len(instantiated) == 1
    wrapped = instantiated[0]
    cell_id = list(wrapped["cell"]["cell_id"])
    assert cell_id[0] == target_row_id


def test_result_parser_rejects_handle_not_in_map():
    """An unknown handle (``row_999`` not in the chunk's handle set) is a
    parser-level error — not a silent drop. Catches the case where the model
    emits something we did not render."""
    from lobby_analysis.models_v2 import build_cell_spec_registry

    registry = build_cell_spec_registry()
    handle_map = {"row_001": "actor_executive_agency_registration_required"}
    response = _record_cell_response("row_999", "legal", True)
    instantiated, unscoreable, errors = tier1._parse_and_instantiate(
        response, "anthropic", registry, handle_map
    )
    assert instantiated == []
    assert unscoreable == []
    assert len(errors) == 1
    assert "unknown_handle" in errors[0].get("reason", "")


def test_result_parser_rejects_row_id_emission_by_model():
    """If the model emits the actual compendium row_id as the ``handle``
    value (a regression where row-IDs leak back at us), the parser errors —
    the contract is opaque handles only."""
    from lobby_analysis.models_v2 import build_cell_spec_registry

    registry = build_cell_spec_registry()
    # Map has a handle, but the model emits the real row_id instead.
    target_row_id = "actor_executive_agency_registration_required"
    handle_map = {"row_001": target_row_id}
    response = _record_cell_response(target_row_id, "legal", True)
    instantiated, unscoreable, errors = tier1._parse_and_instantiate(
        response, "anthropic", registry, handle_map
    )
    assert instantiated == []
    assert unscoreable == []
    assert len(errors) == 1
    # The error must identify the failure as a row-id-leakage / unknown-handle
    # event — not a successful instantiation under the legacy contract.
    assert "unknown_handle" in errors[0].get("reason", "")


def test_result_parser_decodes_unscoreable_emission_via_handle_map():
    """A record_unscoreable_cell emission keyed by handle decodes to the
    original row_id in the abstention record so downstream agreement metrics
    keep working unchanged."""
    from lobby_analysis.models_v2 import build_cell_spec_registry

    registry = build_cell_spec_registry()
    target_row_id = "actor_executive_agency_registration_required"
    handle_map = {"row_001": target_row_id}
    response = _record_unscoreable_response(
        "row_001", "legal", "statute references out-of-bundle chapter"
    )
    instantiated, unscoreable, errors = tier1._parse_and_instantiate(
        response, "anthropic", registry, handle_map
    )
    assert errors == []
    assert instantiated == []
    assert len(unscoreable) == 1
    abstained = unscoreable[0]
    assert abstained.get("row_id") == target_row_id


def test_render_then_parse_roundtrip_preserves_row_ids():
    """Integration: render a chunk → mock a response that uses the rendered
    handles → parse → recover the original row_ids. No row-IDs visible in the
    rendered message; all row-IDs recoverable from the parsed results."""
    from lobby_analysis.models_v2 import build_cell_spec_registry

    registry = build_cell_spec_registry()
    rows = [
        # Two narrow-pass rows (have prompts) plus one scalar BinaryCell that
        # the test fixture can emit a true/false answer for. The narrow-pass
        # anchor rows are BinaryCells so the value=True emission instantiates.
        "lobbyist_spending_report_required",
        "lobbyist_spending_report_includes_principal_names",
        "actor_executive_agency_registration_required",
    ]
    specs = [_spec(rid, "legal") for rid in rows]
    message, handle_map = tier1.render_legal_roster(
        "lobbyist_spending_report", "topic", specs
    )

    # Sanity: no row_ids in message; every spec has an entry in the handle map.
    for rid in rows:
        assert rid not in message
    assert set(handle_map.values()) == set(rows)

    # Construct three record_cell emissions, one per rendered handle.
    response_calls = []
    for handle in sorted(handle_map):
        response_calls.append(
            {
                "type": "tool_use",
                "name": "record_cell",
                "input": {
                    "handle": handle,
                    "axis": "legal",
                    "value": True,
                    "condition_text": None,
                    "confidence": "high",
                    "cited_section": "§101.70",
                    "justification": "test fixture justification.",
                },
            }
        )
    response = {"content": response_calls}

    instantiated, unscoreable, errors = tier1._parse_and_instantiate(
        response, "anthropic", registry, handle_map
    )
    assert errors == []
    assert unscoreable == []
    assert len(instantiated) == 3
    recovered_row_ids = sorted(
        list(wrapped["cell"]["cell_id"])[0] for wrapped in instantiated
    )
    assert recovered_row_ids == sorted(rows)
