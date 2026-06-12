"""Behavior tests for NY canonical ``bill_id`` derivation (``io/ny/parse``).

This is where the **State-Bill scoping decision** lives. Phase 0 found that a
real, Open-States-joinable bill number lives in ``focus_identifying_number``
only when the row's ``focus_type`` is exactly ``"State Bill"`` — the other focus
types (``State Funding``, ``Municipal Bill``, ``State Regulation/...``, etc.)
carry subject/funding free text there, which must NOT become a ``bill_id``.

The scoping question the parser resolves: Phase 0's first-pass filter combined
``focus_type == 'State Bill'`` **AND** ``level_of_government`` starts-with
``'State'``. That ``level`` clause is wrong. The committed fixture row
``S550-A`` is a genuine NY state bill filed at
``level_of_government = 'Both (State and Municipal)'`` — the ``level`` describes
the engagement's jurisdictional scope, not the bill's identity. Adding the
``level`` clause silently drops ~2.45M of ~9.82M State-Bill rows for 2025 (25%).
So the bill scope is ``focus_type == 'State Bill'`` **alone**; ``Municipal Bill``
is a distinct ``focus_type`` value and is excluded by that test without needing
``level`` at all.

``derive_bill_id`` keeps the amendment print suffix (``S550-A``) on the
``bill_id`` — that records which print was actually lobbied. Stripping the
``-A/-B`` suffix to hit the Open States key is a *separate*, later concern
(the Phase 4 chain normalizer), not this function's job.

Tests assert derived values against the real Phase-0 identifiers and the focus
taxonomy — real behavior, not call-shape.
"""

from __future__ import annotations

import pandas as pd

from lobby_analysis.io.ny.parse import add_bill_id_column, derive_bill_id


def test_state_bill_focus_yields_the_bill_number():
    """The canonical case: a ``State Bill`` focus row carries its bill number in
    ``focus_identifying_number`` and that becomes the ``bill_id`` verbatim
    (print suffix preserved)."""
    assert derive_bill_id("State Bill", "S550-A") == "S550-A"
    assert derive_bill_id("State Bill", "A10003") == "A10003"


def test_state_bill_at_both_level_is_NOT_dropped():
    """The load-bearing scoping decision. ``S550-A`` is a real state bill even
    though its engagement is filed at ``Both (State and Municipal)`` level —
    deriving ``bill_id`` must depend on ``focus_type`` only, never on
    ``level_of_government``. (derive_bill_id takes no level argument at all,
    which structurally guarantees the level can't drop it.)"""
    assert derive_bill_id("State Bill", "S550-A") == "S550-A"


def test_non_state_bill_focus_types_yield_no_bill_id():
    """Every non-``State Bill`` focus type puts free text (a subject, a funding
    description) in ``focus_identifying_number``; none of that is a bill number,
    so ``bill_id`` is None — the row is kept downstream but is not chain-eligible."""
    assert derive_bill_id("State Funding", "Discretionary Funding") is None
    assert (
        derive_bill_id(
            "State Funding",
            "Funding for Housing Access Voucher Program, Empire State Child Tax Credit",
        )
        is None
    )
    assert derive_bill_id("State Regulation/Rate-making/Rule", "Some rule text") is None
    assert derive_bill_id("State Resolution", "A resolution about things") is None


def test_municipal_bill_is_excluded_by_focus_type():
    """``Municipal Bill`` is a separate ``focus_type`` value carrying municipal
    bill numbers — out of scope (state-level only). It is excluded by the
    focus-type test, with no need to inspect ``level_of_government``."""
    assert derive_bill_id("Municipal Bill", "Int 1234-2025") is None


def test_blank_or_missing_focus_identifying_number_yields_none():
    """A ``State Bill`` row with no usable identifier (empty / NaN) cannot
    produce a bill_id — guard against emitting an empty-string bill key."""
    assert derive_bill_id("State Bill", "") is None
    assert derive_bill_id("State Bill", "   ") is None
    assert derive_bill_id("State Bill", None) is None
    assert derive_bill_id(None, "S550-A") is None


def test_bill_id_is_whitespace_trimmed_and_uppercased():
    """NY identifiers arrive with stray whitespace/case; normalize to a stable
    key (trim, uppercase) so the same bill doesn't fork into variants — but the
    amendment suffix is preserved."""
    assert derive_bill_id("State Bill", "  s550-a ") == "S550-A"
    assert derive_bill_id("State Bill", "a10003") == "A10003"


def test_state_bill_with_non_bill_text_yields_none():
    """A ``State Bill`` focus whose identifier is clearly not a bill number
    (free text rather than a chamber-prefixed number) must not be coerced into a
    bill_id — only ``S###`` / ``A###`` (optionally suffixed) parse as bills."""
    assert derive_bill_id("State Bill", "see attached list of bills") is None
    assert derive_bill_id("State Bill", "various") is None


def test_add_bill_id_column_applies_rowwise_over_a_frame():
    """The frame-level helper the grain step depends on: given a column-normalized
    frame (``focus_type`` + ``focus_identifying_number``), add a canonical
    ``bill_id`` column. State-Bill rows get their number; everything else gets
    None. This is what interposes between ``normalize_columns`` and
    ``collapse_to_filing_grain``."""
    df = pd.DataFrame(
        [
            {"focus_type": "State Bill", "focus_identifying_number": "S550-A"},
            {"focus_type": "State Funding", "focus_identifying_number": "Discretionary Funding"},
            {"focus_type": "State Bill", "focus_identifying_number": "A100"},
            {"focus_type": "Municipal Bill", "focus_identifying_number": "Int 1-2025"},
        ]
    )

    out = add_bill_id_column(df)

    assert out["bill_id"].tolist() == ["S550-A", None, "A100", None]
    # original columns are untouched
    assert out["focus_type"].tolist() == df["focus_type"].tolist()
