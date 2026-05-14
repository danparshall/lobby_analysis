"""Tests for `lobby_analysis.models_v2.cell_spec.CompendiumCellSpec` + the
186-cell registry built from the real `compendium/disclosure_side_compendium_items_v2.tsv`.

These tests run against the REAL TSV, not a fixture — a TSV change must
propagate as a test failure (per the plan's "no mocks of load_v2_compendium").
"""

from __future__ import annotations

import pytest


# ---------------------------------------------------------------------------
# Registry size + axis-expansion semantics
# ---------------------------------------------------------------------------


def test_build_cell_spec_registry_has_186_entries():
    """The v2 TSV's 181 rows expand to 186 registry entries: 126 legal-only +
    50 practical-only + 5 legal+practical (each doubled to one legal + one
    practical entry) = 181 + 5 = 186 entries.
    """
    from lobby_analysis.models_v2.cell_spec import build_cell_spec_registry

    registry = build_cell_spec_registry()
    assert len(registry) == 186, (
        f"Expected 186 registry entries (181 TSV rows + 5 legal+practical "
        f"doublings); got {len(registry)}."
    )


def test_registry_keys_are_row_id_axis_tuples():
    """Each registry key is (row_id: str, axis: 'legal'|'practical')."""
    from lobby_analysis.models_v2.cell_spec import build_cell_spec_registry

    registry = build_cell_spec_registry()
    for key in registry:
        assert isinstance(key, tuple) and len(key) == 2
        row_id, axis = key
        assert isinstance(row_id, str) and row_id  # non-empty
        assert axis in ("legal", "practical"), (
            f"Registry has axis={axis!r} for row {row_id!r}; expected legal or practical."
        )


def test_registry_legal_practical_split_matches_tsv_distribution():
    """The TSV has 126 legal-only + 50 practical-only + 5 legal+practical.
    After expansion: 131 legal entries + 55 practical entries = 186.
    """
    from lobby_analysis.models_v2.cell_spec import build_cell_spec_registry

    registry = build_cell_spec_registry()
    legal_count = sum(1 for (_, axis) in registry if axis == "legal")
    practical_count = sum(1 for (_, axis) in registry if axis == "practical")
    assert legal_count == 131
    assert practical_count == 55


def test_registry_doubles_each_legal_plus_practical_row():
    """The 5 known combined-axis rows must each have BOTH (row_id, 'legal') AND
    (row_id, 'practical') in the registry.
    """
    from lobby_analysis.models_v2.cell_spec import build_cell_spec_registry

    registry = build_cell_spec_registry()
    combined_row_ids = {
        "lobbying_disclosure_audit_required_in_law",
        "lobbying_violation_penalties_imposed_in_practice",
        "lobbyist_registration_required",
        "lobbyist_spending_report_filing_cadence",
        "registration_deadline_days_after_first_lobbying",
    }
    for row_id in combined_row_ids:
        assert (row_id, "legal") in registry, f"Missing ({row_id}, 'legal') in registry."
        assert (row_id, "practical") in registry, f"Missing ({row_id}, 'practical') in registry."


# ---------------------------------------------------------------------------
# Spec class
# ---------------------------------------------------------------------------


def test_cell_spec_carries_row_id_axis_and_expected_class():
    """CompendiumCellSpec is a frozen record: row_id, axis, expected_cell_class."""
    from lobby_analysis.models_v2.cell_spec import build_cell_spec_registry
    from lobby_analysis.models_v2.cells import CompendiumCell

    registry = build_cell_spec_registry()
    spec = next(iter(registry.values()))
    assert isinstance(spec.row_id, str)
    assert spec.axis in ("legal", "practical")
    assert issubclass(spec.expected_cell_class, CompendiumCell)


# ---------------------------------------------------------------------------
# Anchor row mapping (most-validated row across rubrics)
# ---------------------------------------------------------------------------


def test_anchor_row_maps_to_binary_cell_at_legal():
    """`lobbyist_spending_report_includes_total_compensation` is the 8-rubric
    most-validated row in the v2 TSV (only one of its tier). cell_type=binary,
    axis=legal. If this anchor's mapping breaks, the parser is broken.
    """
    from lobby_analysis.models_v2.cell_spec import build_cell_spec_registry
    from lobby_analysis.models_v2.cells import BinaryCell

    registry = build_cell_spec_registry()
    spec = registry[("lobbyist_spending_report_includes_total_compensation", "legal")]
    assert spec.expected_cell_class is BinaryCell


# ---------------------------------------------------------------------------
# Combined-axis parsing — explicit per-row checks for all 5 combined rows
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "row_id, legal_class_name, practical_class_name",
    [
        # cell_type: 'enum (legal) + typed int 0-100 step 25 (practical)'
        (
            "lobbying_disclosure_audit_required_in_law",
            "EnumCell",
            "GradedIntCell",
        ),
        # cell_type: 'binary (legal) + typed int 0-100 step 25 (practical)'
        (
            "lobbying_violation_penalties_imposed_in_practice",
            "BinaryCell",
            "GradedIntCell",
        ),
        (
            "lobbyist_registration_required",
            "BinaryCell",
            "GradedIntCell",
        ),
        # cell_type: 'enum (legal) + typed int 0-100 step 25 (practical)'
        (
            "lobbyist_spending_report_filing_cadence",
            "EnumCell",
            "GradedIntCell",
        ),
        # cell_type: 'typed int (legal) + typed int 0-100 step 25 (practical)'
        (
            "registration_deadline_days_after_first_lobbying",
            "IntCell",
            "GradedIntCell",
        ),
    ],
)
def test_combined_axis_rows_parse_to_correct_per_axis_classes(
    row_id: str, legal_class_name: str, practical_class_name: str
):
    """The cell_type parser must split combined-axis rows into two specs
    with the correct per-axis cell class. Generalizes — not hard-coded per
    row, so adding a future combined row only requires this list to grow.
    """
    from lobby_analysis.models_v2.cell_spec import build_cell_spec_registry

    registry = build_cell_spec_registry()
    legal_spec = registry[(row_id, "legal")]
    practical_spec = registry[(row_id, "practical")]
    assert legal_spec.expected_cell_class.__name__ == legal_class_name
    assert practical_spec.expected_cell_class.__name__ == practical_class_name


# ---------------------------------------------------------------------------
# No orphan cell_types — every distinct TSV cell_type must have a parser
# ---------------------------------------------------------------------------


def test_no_orphan_cell_types_in_tsv():
    """If a new cell_type appears in the TSV without a parser, the registry
    build must fail loudly. Calling build_cell_spec_registry() against the
    real TSV exercises this — if the build returns 186 entries, every row's
    cell_type was successfully parsed.
    """
    from lobby_analysis.compendium_loader import load_v2_compendium
    from lobby_analysis.models_v2.cell_spec import build_cell_spec_registry

    raw_rows = load_v2_compendium()
    registry = build_cell_spec_registry()

    # Sanity: every row in the TSV produces at least one registry entry.
    expected_min = len(raw_rows)
    expected_max = len(raw_rows) + sum(1 for r in raw_rows if r["axis"] == "legal+practical")
    assert expected_min <= len(registry) <= expected_max


# ---------------------------------------------------------------------------
# Parametrized sweep — every registry entry can construct a valid cell
# ---------------------------------------------------------------------------


# These are the "valid value" templates each cell class accepts.
# Used to parametrize-construct one instance per registry entry as a
# round-trip check that the registry's class mapping is actually usable.
_VALID_VALUE_TEMPLATES = {
    "BinaryCell": {"value": True},
    "DecimalCell": {"value": None},
    "IntCell": {"value": None},
    "FloatCell": {"value": None},
    "GradedIntCell": {"value": 0},
    "BoundedIntCell": {"value": 0},
    "EnumCell": {"value": "any"},
    "EnumSetCell": {"value": frozenset({"any"})},
    "FreeTextCell": {"value": "any"},
    "UpdateCadenceCell": {"value": None},
    "TimeThresholdCell": {"magnitude": None, "unit": None},
    "TimeSpentCell": {"magnitude": None, "unit": None},
    "SectorClassificationCell": {"value": None},
    "CountWithFTECell": {"count": None, "fte": None},
    "EnumSetWithAmountsCell": {"value": frozenset(), "amounts": {}},
}


def test_every_registry_entry_can_construct_a_valid_cell():
    """Sweep: for each (row_id, axis, expected_class), construct an instance
    with a known-valid value template and assert it validates. Catches
    parser errors where a row gets mapped to the wrong class.
    """
    from lobby_analysis.models_v2.cell_spec import build_cell_spec_registry

    registry = build_cell_spec_registry()
    missing_templates: list[str] = []
    for (row_id, axis), spec in registry.items():
        cls = spec.expected_cell_class
        template = _VALID_VALUE_TEMPLATES.get(cls.__name__)
        if template is None:
            missing_templates.append(cls.__name__)
            continue
        cls(cell_id=(row_id, axis), **template)
    assert not missing_templates, (
        f"Missing valid-value templates for: {sorted(set(missing_templates))}"
    )
