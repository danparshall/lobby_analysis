"""Phase A pre-flight YAML audit — cell-type-aligned vocabulary additives.

Plan: docs/active/wi-ralph-cpi-renewal-cadence/plans/20260605_phase_a_yaml_audit_at_scale.md

After Phase A lands, every row whose cell_type matches one of the 3 in-scope
template buckets carries the cell-type-aligned vocabulary additive in its
YAML prompt:

- BinaryCell (cell_type == "binary"): "Answer with the boolean value true or false."
- DecimalCell-Optional (cell_type == "typed Optional[Decimal]"): "non-negative decimal"
- EnumCell-family (9 hand-curated rows, 7 distinct cell_types): "Answer with one of:"
  OR "Answer with one or more of:" (Set[enum] variants take the plural form)

Out of scope for Phase A (and therefore for these tests):
- 11 long-tail typed singletons (e.g. UpdateCadenceCell, TimeThresholdCell,
  count_with_FTE, free-text) — each needs Phase-B-style hand iteration.
  Plan §"Out of scope" line item.
- 3 practical-axis-only `typed int 0-100 step 25 (practical)` rows — dispatcher
  does not extract these.
- Combined-axis rows (e.g. `lobbyist_registration_required` with
  `binary (legal) + typed int 0-100 step 25 (practical)`) — deferred to Phase B.
  Filters here use exact-match on the canonical single-axis cell_type strings.

Why these tests test real behavior: a cell-type-vocabulary mismatch makes the
dispatcher's `_instantiate_cell` raise ValueError at coercion (BinaryCell
accepts only `true`/`false`, not `yes`/`no` — observed empirically on
`_defined_in_law` Pattern C, 6/6 errored). Asserting the YAML prompt carries
the cell-type-aligned marker is the cheapest layer at which to catch the
regression class.
"""

from __future__ import annotations

import csv
from pathlib import Path

import pytest

_WORKTREE = Path(__file__).resolve().parents[1]
_TSV = _WORKTREE / "compendium" / "disclosure_side_compendium_items_v2.1.tsv"


def _rows_with_cell_type(target_cell_type: str) -> list[str]:
    """Return compendium row IDs whose `cell_type` is exactly `target_cell_type`.

    Exact-match is deliberate: combined-axis cell_types like
    `binary (legal) + typed int 0-100 step 25 (practical)` are out of scope
    for Phase A (deferred to Phase B per plan §"Out of scope").
    """
    rows: list[str] = []
    with _TSV.open() as f:
        reader = csv.DictReader(f, delimiter="\t")
        for r in reader:
            if r["cell_type"] == target_cell_type:
                rows.append(r["compendium_row_id"])
    return rows


# Collected at module load — pytest parametrize takes the snapshot.
_BINARY_ROWS = _rows_with_cell_type("binary")
_DECIMAL_OPTIONAL_ROWS = _rows_with_cell_type("typed Optional[Decimal]")


# 9 hand-curated enum-family targets (per plan §"Why this plan exists" + the
# `/tmp/phase_a_list_targets.py` enumeration). Mix of cell_types:
#   - typed Optional[enum]  (2 rows)
#   - typed Set[enum]       (2 rows)
#   - typed Set[enum] (8 types) (1 row)
#   - typed Set[enum] (9 types) (1 row)
#   - typed Set[enum] + amounts (1 row)
#   - enum (legal)          (1 row — `lobbying_disclosure_audit_required_in_law`)
#   - typed enum            (1 row — `ministerial_diary_disclosure_cadence`)
_ENUM_TARGET_ROWS: frozenset[str] = frozenset(
    {
        "consultant_lobbyist_report_includes_income_by_source_type",
        "lobbying_contact_log_includes_communication_form",
        "def_lobbying_activity_types",
        "lobbying_disclosure_audit_required_in_law",
        "lobbying_disclosure_data_includes_unique_identifiers",
        "lobbying_disclosure_data_linked_to_other_datasets",
        "def_lobbyist_actor_types",
        "lobbyist_reg_form_includes_lobbyist_legal_form",
        "ministerial_diary_disclosure_cadence",
    }
)


# ---------------------------------------------------------------------------
# Sanity: did module-load collection actually find rows?
# ---------------------------------------------------------------------------


def test_phase_a_binary_target_count_matches_plan():
    """Plan §"Current YAML state" expects 151 rows with exact cell_type == 'binary'.

    Anchors the collection step: if a future TSV edit changes the cell_type
    vocabulary, this catches the drift before parametrize silently expands or
    shrinks the test set.
    """
    assert len(_BINARY_ROWS) == 151, (
        f"Expected 151 binary rows (plan §'Current YAML state'); "
        f"found {len(_BINARY_ROWS)}. TSV may have shifted."
    )


def test_phase_a_decimal_optional_target_count_matches_plan():
    """Plan §"Current YAML state" expects 5 rows with cell_type == 'typed Optional[Decimal]'."""
    assert len(_DECIMAL_OPTIONAL_ROWS) == 5, (
        f"Expected 5 typed-Optional-Decimal rows (plan §'Current YAML state'); "
        f"found {len(_DECIMAL_OPTIONAL_ROWS)}. TSV may have shifted."
    )


# ---------------------------------------------------------------------------
# BinaryCell additive — 151 rows post-Phase-A
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("row_id", _BINARY_ROWS)
def test_phase_a_binary_row_carries_boolean_additive(row_id):
    """Every BinaryCell row's YAML prompt must contain the boolean-vocabulary
    instruction so the LLM emits `true`/`false` (not `yes`/`no`) and the
    dispatcher's `BinaryCell` coercion succeeds.

    Failure mode this prevents: Pattern C iter `_defined_in_law` 6/6 errored
    because the prompt asked a natural-English yes/no question; models
    correctly emit `'yes'`; BinaryCell coercion raises ValueError.
    """
    from lobby_analysis.source_quotes_loader import load_source_quotes

    entries = load_source_quotes()
    assert row_id in entries, f"{row_id!r} missing from source_quotes.yaml"
    prompt = entries[row_id].prompt
    assert "Answer with the boolean value true or false." in prompt, (
        f"BinaryCell row {row_id!r} is missing the Phase A BinaryCell "
        f"additive ('Answer with the boolean value true or false.') from its "
        f"prompt.\nprompt={prompt!r}"
    )


# ---------------------------------------------------------------------------
# DecimalCell-Optional additive — 5 rows post-Phase-A
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("row_id", _DECIMAL_OPTIONAL_ROWS)
def test_phase_a_decimal_optional_row_carries_decimal_additive(row_id):
    """Every typed-Optional-Decimal row's YAML prompt must contain the
    non-negative-decimal vocabulary instruction so the LLM emits a Decimal
    (not a tier-score, not a yes/no, not a string).

    Failure mode this prevents: iter 5 silent unit-mismatch (GPT emitted
    `'0.5'` — the CPI tier score 50/100 normalized — when DecimalCell wanted
    the actual dollar amount).
    """
    from lobby_analysis.source_quotes_loader import load_source_quotes

    entries = load_source_quotes()
    assert row_id in entries, f"{row_id!r} missing from source_quotes.yaml"
    prompt = entries[row_id].prompt
    assert "non-negative decimal" in prompt, (
        f"DecimalCell-Optional row {row_id!r} is missing the Phase A "
        f"DecimalCell-Optional additive ('non-negative decimal') from its "
        f"prompt.\nprompt={prompt!r}"
    )


# ---------------------------------------------------------------------------
# EnumCell-family additive — 9 hand-curated rows post-Phase-A
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("row_id", sorted(_ENUM_TARGET_ROWS))
def test_phase_a_enum_row_carries_enum_domain_additive(row_id):
    """Each of the 9 enum-family target rows must carry an additive that
    explicitly enumerates the row's per-row enum domain.

    Single-valued EnumCell rows use 'Answer with one of:'; set-valued
    EnumSetCell rows use 'Answer with one or more of:'. The test accepts
    either marker (the row-specific cell-type dictates which is correct).
    """
    from lobby_analysis.source_quotes_loader import load_source_quotes

    entries = load_source_quotes()
    assert row_id in entries, f"{row_id!r} missing from source_quotes.yaml"
    prompt = entries[row_id].prompt
    has_single = "Answer with one of:" in prompt
    has_set = "Answer with one or more of:" in prompt
    assert has_single or has_set, (
        f"EnumCell-family row {row_id!r} is missing the Phase A enum-domain "
        f"additive ('Answer with one of:' or 'Answer with one or more of:') "
        f"from its prompt.\nprompt={prompt!r}"
    )
