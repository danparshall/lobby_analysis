"""Behavior tests for the NY Phase-4 chain composer's OS-independent core.

Two concerns are tested here (the parts that do **not** depend on the Open
States bill bundle, so they can be built before that gated download lands):

1. **Coalition beneficiary split (Decision 7).** Some NY ``beneficial_client``
   cells pack many beneficiaries into one semicolon-delimited string (346 such
   client rows in the live 2025 release). The chain layer splits them into one
   beneficiary per entity and allocates credit evenly. ``split_beneficiaries``
   is the splitter; it mirrors ``parse.parse_individual_lobbyists`` (trim, drop
   empties from trailing delimiters, de-dupe by slug, preserve order).

2. **No-loss conservation under the multiplicative split.** A filing with
   compensation ``C``, ``M`` beneficiaries, and ``N`` bills emits ``M·N`` cells
   each carrying ``comp_per_cell``; the cells must sum to ``C`` exactly (no cent
   lost or duplicated). The conservation primitive is ``parse.even_split`` (the
   integer-cent splitter relocated from ``materialize`` so both the Phase-3
   per-bill split and the Phase-4 per-cell split share one implementation). The
   multiplicative case is just ``even_split(C, M*N)``.

These assert real allocated values, not call-shape. The full composer test
(sponsor attachment, unmatched-bill flagging) lands with the OS bundle.
"""

from __future__ import annotations

from decimal import Decimal

from lobby_analysis.allocation.ny.chain import split_beneficiaries
from lobby_analysis.io.ny.parse import even_split


# ---------------------------------------------------------------------------
# split_beneficiaries (Decision 7)
# ---------------------------------------------------------------------------


def test_single_client_is_a_one_element_list():
    """A non-coalition ``beneficial_client`` is one beneficiary; the splitter
    returns a single-element list so M=1 and the per-cell split is a no-op."""
    assert split_beneficiaries("Suffolk County Court Employees Association Inc") == [
        "Suffolk County Court Employees Association Inc"
    ]


def test_semicolon_list_splits_into_separate_beneficiaries():
    """The canonical coalition cell: a semicolon-delimited list becomes one
    cleaned beneficiary per element, order preserved."""
    raw = "239 Entertainment LLC; AoK Maintenance Supply"
    assert split_beneficiaries(raw) == ["239 Entertainment LLC", "AoK Maintenance Supply"]


def test_each_beneficiary_is_whitespace_trimmed():
    """Stray internal/leading/trailing whitespace around each element is
    trimmed so the same beneficiary doesn't fork on spacing."""
    assert split_beneficiaries("  ACME LLC ;   Beta Corp  ") == ["ACME LLC", "Beta Corp"]


def test_trailing_delimiter_does_not_emit_empty_beneficiary():
    """A trailing ``;`` (common in NY data) must not produce an empty
    beneficiary token."""
    assert split_beneficiaries("ACME LLC; Beta Corp;") == ["ACME LLC", "Beta Corp"]


def test_duplicate_beneficiaries_are_deduped_by_slug_order_preserving():
    """A beneficiary repeated within one cell collapses to a single entry
    (deduped by slug, like ``parse_individual_lobbyists``), keeping the first
    display form and original order."""
    assert split_beneficiaries("ACME LLC; acme llc; Beta Corp") == ["ACME LLC", "Beta Corp"]


def test_empty_or_missing_cell_yields_empty_list():
    """An empty / whitespace / None cell has no beneficiaries — return []
    (not [""]), so a filing with no usable client contributes no cells."""
    assert split_beneficiaries("") == []
    assert split_beneficiaries("   ") == []
    assert split_beneficiaries(None) == []
    assert split_beneficiaries(";") == []


# ---------------------------------------------------------------------------
# even_split conservation under the multiplicative (M·N) split
# ---------------------------------------------------------------------------


def test_even_split_divides_evenly_when_it_can():
    """C / n with no remainder: each part is exactly C/n and the parts sum to C."""
    parts = even_split(Decimal("100.00"), 4)
    assert parts == [Decimal("25.00")] * 4
    assert sum(parts) == Decimal("100.00")


def test_even_split_distributes_the_remainder_to_the_first_parts():
    """Odd division: the leftover cents go to the first parts so the sum is
    still exactly C (no rounding loss). 100/3 -> 33.34 + 33.33 + 33.33."""
    parts = even_split(Decimal("100.00"), 3)
    assert parts == [Decimal("33.34"), Decimal("33.33"), Decimal("33.33")]
    assert sum(parts) == Decimal("100.00")


def test_multiplicative_split_conserves_C_across_M_times_N_cells():
    """The Decision-7 invariant the plan calls out: a filing with comp C, M
    beneficiaries, and N bills splits into M*N cells summing exactly to C. This
    is just even_split(C, M*N) — the multiplicative split is a single even-split
    over the cell count, so remainders never compound across the two axes."""
    C = Decimal("345762.46")
    M, N = 3, 7  # multi-beneficiary x multi-bill
    cells = even_split(C, M * N)
    assert len(cells) == M * N
    assert sum(cells) == C


def test_even_split_of_zero_parts_is_empty():
    """Degenerate guard: no cells requested -> no parts (a filing with no bills
    or no beneficiaries emits nothing, rather than raising)."""
    assert even_split(Decimal("100.00"), 0) == []
