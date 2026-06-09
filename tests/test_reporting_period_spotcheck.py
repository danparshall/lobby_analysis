"""Tests for scripts/gpt5mini_oh_300slice_reporting_period_spotcheck.py.

The script's job is enumeration + classification, and the classification
is heuristic — the only thing worth testing rigorously is the classifier
itself (the enumeration walks the filesystem and is exercised by hand).
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
_SCRIPT_PATH = (
    _REPO_ROOT / "scripts" / "gpt5mini_oh_300slice_reporting_period_spotcheck.py"
)


def _load_script():
    spec = importlib.util.spec_from_file_location("rp_spotcheck", _SCRIPT_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["rp_spotcheck"] = module
    spec.loader.exec_module(module)
    return module


def test_format_only_iso_vs_slash() -> None:
    mod = _load_script()
    assert mod.classify("2025-01-01", "01/01/2025") == "format_only"


def test_format_only_iso_vs_dash_us() -> None:
    mod = _load_script()
    assert mod.classify("2025-06-30", "06-30-2025") == "format_only"


def test_one_day_off_plus() -> None:
    mod = _load_script()
    c = mod.classify("2025-01-01", "2025-01-02")
    assert "one_day_off" in c and "+1" in c


def test_one_day_off_minus() -> None:
    mod = _load_script()
    c = mod.classify("2025-01-01", "2024-12-31")
    assert "one_day_off" in c and "-1" in c


def test_semester_boundary() -> None:
    mod = _load_script()
    # June 30 vs August 31 - 62 days
    c = mod.classify("2025-06-30", "2025-08-31")
    assert "semester_or_quarter_boundary" in c


def test_large_delta() -> None:
    mod = _load_script()
    # Year apart
    c = mod.classify("2024-01-01", "2025-01-01")
    assert "large_delta" in c


def test_unparseable_gibberish() -> None:
    mod = _load_script()
    # Both unparseable → unparseable category
    assert mod.classify("xyz", "abc") == "unparseable"


def test_week_off() -> None:
    mod = _load_script()
    c = mod.classify("2025-01-01", "2025-01-05")
    assert "week_off" in c


def test_month_off() -> None:
    mod = _load_script()
    # Within 35 days but >7 days → month_off
    c = mod.classify("2025-01-01", "2025-01-20")
    assert "month_off" in c
