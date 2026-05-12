"""Tests for the OCR dual-pass token merger.

The v1 extractor uses tesseract PSM 3 by default. On scan 169 PSM 3 drops
the California and Florida row bands; PSM 6 (uniform-block) reads them.
The fix runs both PSMs and merges via spatial proximity: any PSM-6 token
not co-located with an existing PSM-3 token is added. See investigation
in convos/20260511_opheim_phase0_table1_lift.md.
"""
from __future__ import annotations

from dataclasses import dataclass

import pytest

from lobby_analysis.cogel.ocr_merge import DEFAULT_MERGE_RADIUS, merge_token_passes


@dataclass(frozen=True)
class T:
    """Minimal token stand-in matching the TokenLike protocol."""

    x: int
    y: int
    w: int
    h: int
    conf: int = 90
    text: str = "*"


# ----- baseline merge semantics -----------------------------------------


def test_empty_secondary_returns_primary_verbatim():
    primary = [T(100, 200, 10, 10), T(500, 800, 30, 5)]
    assert merge_token_passes(primary, []) == primary


def test_empty_primary_returns_secondary_verbatim():
    secondary = [T(100, 200, 10, 10)]
    assert merge_token_passes([], secondary) == secondary


def test_two_empty_inputs_returns_empty():
    assert merge_token_passes([], []) == []


# ----- spatial dedup ----------------------------------------------------


def test_colocated_tokens_keep_primary_drop_secondary():
    """Same-position tokens: primary wins, secondary dropped."""
    p = T(100, 200, 10, 10, conf=50, text="*")
    s = T(102, 201, 10, 10, conf=95, text="*")  # ~2 px away, same glyph
    result = merge_token_passes([p], [s])
    assert result == [p]


def test_far_apart_tokens_both_retained():
    p = T(100, 200, 10, 10)
    s = T(500, 800, 10, 10)
    result = merge_token_passes([p], [s])
    assert len(result) == 2
    assert p in result
    assert s in result


def test_secondary_only_token_at_new_position_is_added():
    """Realistic case: PSM 3 finds A, PSM 6 finds both A and B; merger keeps A and B."""
    primary = [T(100, 200, 10, 10, text="A")]
    secondary = [
        T(100, 200, 10, 10, text="A"),   # duplicate of primary
        T(300, 500, 30, 5, text="B"),    # new — PSM 3 missed
    ]
    result = merge_token_passes(primary, secondary)
    assert len(result) == 2
    assert primary[0] in result
    assert secondary[1] in result


# ----- radius parameter -------------------------------------------------


def test_default_radius_is_15px_chebyshev():
    """Verify the documented default. Primary center (105, 205); a
    secondary token at center (120, 220) is exactly 15 px away in both
    axes (dedup'd); at (121, 205) it's 16 px (kept)."""
    p = T(100, 200, 10, 10)  # center (105, 205)
    s_inside = T(115, 215, 10, 10)  # center (120, 220); dx=15, dy=15
    s_outside = T(116, 200, 10, 10)  # center (121, 205); dx=16
    result = merge_token_passes([p], [s_inside, s_outside])
    assert s_inside not in result
    assert s_outside in result
    assert DEFAULT_MERGE_RADIUS == 15


def test_custom_radius_widens_dedup_window():
    p = T(100, 200, 10, 10)
    s = T(130, 200, 10, 10)  # 30 px center-to-center along x
    assert len(merge_token_passes([p], [s], radius=15)) == 2
    assert len(merge_token_passes([p], [s], radius=30)) == 1


# ----- ordering --------------------------------------------------------


def test_primary_order_preserved_then_secondary_appended():
    p1 = T(100, 200, 10, 10, text="p1")
    p2 = T(500, 600, 10, 10, text="p2")
    s_new = T(800, 900, 10, 10, text="s_new")
    result = merge_token_passes([p1, p2], [s_new])
    assert result == [p1, p2, s_new]


# ----- realistic California/Florida scenario ---------------------------


def test_realistic_scan169_dual_psm_merge_adds_missing_row():
    """Simulate the CA scan-169 scenario at a small scale.

    PSM 3 (primary) finds: row label only ("California" at y=1196).
    PSM 6 (secondary) finds: label + 5 markers across the row.
    Merger should keep the label once and add the 5 marker tokens.
    """
    psm3 = [T(316, 1196, 163, 30, conf=96, text="California")]
    psm6 = [
        T(317, 1197, 162, 29, conf=95, text="California"),  # dup
        T(680, 1210, 13, 13, conf=85, text="*"),
        T(820, 1212, 29, 5, conf=70, text="—"),
        T(970, 1213, 29, 4, conf=65, text="—"),
        T(1120, 1212, 29, 5, conf=70, text="—"),
        T(2772, 1215, 12, 13, conf=85, text="*"),
    ]
    result = merge_token_passes(psm3, psm6)
    assert len(result) == 6
    assert psm3[0] in result  # original label preserved
    assert all(s in result for s in psm6[1:])  # all 5 markers added


# ----- input immutability ----------------------------------------------


def test_inputs_not_mutated():
    p = [T(100, 200, 10, 10)]
    s = [T(100, 200, 10, 10), T(500, 600, 10, 10)]
    p_snapshot = list(p)
    s_snapshot = list(s)
    merge_token_passes(p, s)
    assert p == p_snapshot
    assert s == s_snapshot
