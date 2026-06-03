"""Tests for the `prompt_text` column on the v2 compendium TSV + plumbing
into `CompendiumCellSpec` + `render_legal_roster`.

Background: convo 20260603_statute_disagreement_prior_art_review found that
`render_legal_roster` sends only `row_id`/`axis`/`expected_cell_class` to the
model — no row-question text at all. Verbatim source-rubric quotes exist in
the projection-mapping docs but never reach the model. The narrow fix
populates a new `prompt_text` column on the TSV for the 17 confirmed
inter-model disagreement rows and plumbs that column through the cell-spec
registry into the dispatch prompt.

These tests run against the REAL TSV (mirroring `test_models_v2_cell_spec.py`
convention) — a TSV change must propagate as a test signal.
"""

from __future__ import annotations

import importlib.util as _ilu
import sys as _sys
from pathlib import Path as _Path


_SCRIPTS = _Path(__file__).resolve().parents[1] / "scripts"


def _load(module_name: str, path: _Path):
    spec = _ilu.spec_from_file_location(module_name, path)
    assert spec is not None and spec.loader is not None, f"could not load {path}"
    module = _ilu.module_from_spec(spec)
    _sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


_tier0 = _load("tier_0_direct_read_smoke", _SCRIPTS / "tier_0_direct_read_smoke.py")
_tier1 = _load("tier_1_direct_read_legal_axis", _SCRIPTS / "tier_1_direct_read_legal_axis.py")


# ---------------------------------------------------------------------------
# CompendiumCellSpec carries an optional `prompt_text` field
# ---------------------------------------------------------------------------


def test_cell_spec_has_optional_prompt_text_field():
    """`CompendiumCellSpec` exposes a `prompt_text: str | None` attribute.
    Default is `None` so untouched rows (the 164 not in the 17-row fix) don't
    require the column to be populated."""
    from lobby_analysis.models_v2.cell_spec import CompendiumCellSpec
    from lobby_analysis.models_v2.cells import BinaryCell

    spec = CompendiumCellSpec(
        row_id="x", axis="legal", expected_cell_class=BinaryCell
    )
    assert spec.prompt_text is None


# ---------------------------------------------------------------------------
# Registry loads `prompt_text` from the TSV column
# ---------------------------------------------------------------------------


def test_registry_populates_prompt_text_for_pattern_a_anchor_row():
    """`lobbyist_spending_report_required` is the originator of Pattern A (the
    14-cell `lobbyist_spending_report_*` family) and is the most-cited row for
    the filer-vs-subject disambiguation. Its `prompt_text` must be the
    verbatim CPI 2015 IND_201 source quote (the row's first_introduced_by
    rubric)."""
    from lobby_analysis.models_v2.cell_spec import build_cell_spec_registry

    registry = build_cell_spec_registry()
    spec = registry[("lobbyist_spending_report_required", "legal")]
    assert spec.prompt_text is not None
    # Must contain the unambiguous "lobbyists are required to file" phrase
    # that anchors filer-vs-subject — this is the load-bearing distinction
    # the WI 18-cell adjudication identified.
    assert "lobbyists are required to file" in spec.prompt_text


def test_registry_populates_prompt_text_for_all_17_disagreement_rows():
    """All 17 confirmed-disagreement rows (14 Pattern A + 3 Pattern B per
    `results/20260603_prior_art_adjudication_of_18_disagreements.md`) must
    have non-empty `prompt_text`. Pattern C is excluded — it's a v2.2
    axis-split issue, not a prompt fix."""
    from lobby_analysis.models_v2.cell_spec import build_cell_spec_registry

    seventeen_rows = {
        # Pattern A (14)
        "lobbyist_spending_report_required",
        "lobbyist_spending_report_cadence_includes_semiannual",
        "lobbyist_spending_report_categorizes_expenses_by_type",
        "lobbyist_spending_report_includes_bill_or_action_identifier",
        "lobbyist_spending_report_includes_general_issues",
        "lobbyist_spending_report_includes_general_subject_matter",
        "lobbyist_spending_report_includes_gifts_entertainment_transport_lodging",
        "lobbyist_spending_report_includes_indirect_costs",
        "lobbyist_spending_report_includes_lobbyist_contact_info",
        "lobbyist_spending_report_includes_principal_names",
        "lobbyist_spending_report_includes_specific_bill_number",
        "lobbyist_spending_report_includes_total_compensation",
        "lobbyist_spending_report_includes_total_expenditures",
        "lobbyist_spending_report_required_when_no_activity",
        # Pattern B (3)
        "lobbyist_registration_threshold_expenditure_dollars",
        "lobbyist_filing_de_minimis_threshold_time_percent",
        "lobbyist_registration_deadline_days_after_first_lobbying",
    }
    registry = build_cell_spec_registry()
    missing: list[str] = []
    for row_id in seventeen_rows:
        spec = registry[(row_id, "legal")]
        if not spec.prompt_text:
            missing.append(row_id)
    assert not missing, (
        f"{len(missing)} of 17 disagreement rows missing prompt_text: {sorted(missing)}"
    )


def test_registry_leaves_prompt_text_none_for_untouched_rows():
    """Rows not in the narrow 17-row fix must have `prompt_text is None`. The
    wide 181-row pass is a separate session per the handoff."""
    from lobby_analysis.models_v2.cell_spec import build_cell_spec_registry

    registry = build_cell_spec_registry()
    # Pick a row that is NOT in the 17 — `principal_spending_report_required`
    # is structurally analogous to but distinct from the 14 Pattern A rows.
    spec = registry[("principal_spending_report_required", "legal")]
    assert spec.prompt_text is None


# ---------------------------------------------------------------------------
# render_legal_roster includes prompt_text when present, omits when None
# ---------------------------------------------------------------------------


def _spec(row_id: str, axis: str):
    """Resolve one (row_id, axis) cell spec from the real registry."""
    from lobby_analysis.models_v2.cell_spec import build_cell_spec_registry

    return build_cell_spec_registry()[(row_id, axis)]


def test_legal_roster_emits_prompt_text_when_present():
    """When a spec carries `prompt_text`, `render_legal_roster` must include
    it on the roster line. Otherwise the model still sees only the row_id,
    which is exactly the structural problem this fix addresses."""
    spec = _spec("lobbyist_spending_report_required", "legal")
    assert spec.prompt_text  # precondition
    roster = _tier1.render_legal_roster(
        "lobbyist_spending_report", "lobbyist spending report", [spec]
    )
    # The exact prompt_text must appear verbatim in the roster.
    assert spec.prompt_text in roster, (
        f"render_legal_roster did not emit prompt_text for "
        f"{spec.row_id!r}: roster=\n{roster}"
    )


def test_legal_roster_omits_prompt_text_for_specs_without_one():
    """Specs with `prompt_text is None` get the original row_id-only line
    (no spurious 'source-rubric question:' label, no empty-quote artifacts)."""
    spec = _spec("principal_spending_report_required", "legal")
    assert spec.prompt_text is None  # precondition
    roster = _tier1.render_legal_roster(
        "principal_spending_report", "principal spending report", [spec]
    )
    assert "source-rubric question:" not in roster
    assert "''" not in roster
    assert '""' not in roster
