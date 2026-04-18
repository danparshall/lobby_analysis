"""Tests for scoring.statute_retrieval — eligibility + audit logic."""

from __future__ import annotations

from pathlib import Path

import pytest

from scoring.statute_retrieval import (
    PRI_RESPONDER_STATES,
    StateAudit,
    audit_state,
    pick_year_within_tolerance,
)

FIXTURES_DIR = Path(__file__).parent / "fixtures" / "justia"


# ---------- pick_year_within_tolerance ----------


def test_pick_year_within_tolerance_exact_match() -> None:
    got = pick_year_within_tolerance([2008, 2009, 2010, 2011, 2012], target=2010, tolerance=2)
    assert got is not None
    year, delta, direction = got
    assert year == 2010
    assert delta == 0
    assert direction == "exact"


def test_pick_year_within_tolerance_pre_preferred_on_tie() -> None:
    # |2008 - 2010| == |2012 - 2010| == 2; pre-2010 preferred because PRI scored late-2009.
    got = pick_year_within_tolerance([2008, 2012], target=2010, tolerance=2)
    assert got is not None
    year, delta, direction = got
    assert year == 2008
    assert delta == -2
    assert direction == "pre"


def test_pick_year_within_tolerance_post_only() -> None:
    got = pick_year_within_tolerance([2011, 2012], target=2010, tolerance=2)
    assert got is not None
    year, delta, direction = got
    assert year == 2011
    assert delta == 1
    assert direction == "post"


def test_pick_year_within_tolerance_closest_wins_asymmetric() -> None:
    # 2007 is 3 away, 2011 is 1 away; 2011 should win even though pre is preferred on ties.
    got = pick_year_within_tolerance([2007, 2011], target=2010, tolerance=3)
    assert got is not None
    year, delta, direction = got
    assert year == 2011
    assert delta == 1
    assert direction == "post"


def test_pick_year_within_tolerance_out_of_band() -> None:
    # Nothing within ±2 of 2010.
    got = pick_year_within_tolerance([2016, 2017, 2018], target=2010, tolerance=2)
    assert got is None


def test_pick_year_within_tolerance_empty_years() -> None:
    got = pick_year_within_tolerance([], target=2010, tolerance=2)
    assert got is None


def test_pick_year_within_tolerance_single_exact() -> None:
    got = pick_year_within_tolerance([2010], target=2010, tolerance=0)
    assert got == (2010, 0, "exact")


# ---------- PRI_RESPONDER_STATES ----------


def test_pri_responder_states_has_34_entries() -> None:
    # Paper footnote 80 lists 34 states that responded to PRI's review.
    assert len(PRI_RESPONDER_STATES) == 34


def test_pri_responder_states_uses_usps_abbreviations() -> None:
    # All entries are 2-letter USPS codes.
    assert all(len(s) == 2 and s.isupper() for s in PRI_RESPONDER_STATES)


def test_pri_responder_states_known_examples() -> None:
    # Spot-check a few known entries from footnote 80.
    assert "CA" in PRI_RESPONDER_STATES
    assert "WA" in PRI_RESPONDER_STATES
    assert "NY" in PRI_RESPONDER_STATES
    # Non-responders per paper: not in the set.
    assert "IL" not in PRI_RESPONDER_STATES  # Illinois was not in the 34


# ---------- audit_state ----------


class FakeClient:
    """Test double: returns canned HTML for specific URL patterns."""

    def __init__(self, url_to_html: dict[str, str]) -> None:
        self._pages = url_to_html

    def fetch_page(self, url: str) -> str:
        if url not in self._pages:
            raise KeyError(f"FakeClient has no canned response for {url}")
        return self._pages[url]


def _load(name: str) -> str:
    return (FIXTURES_DIR / name).read_text(encoding="utf-8")


def test_audit_state_california_has_2010() -> None:
    client = FakeClient({
        "https://law.justia.com/codes/california/": _load("california_index.html"),
    })
    result = audit_state(client, state_abbr="CA", target_year=2010, tolerance=2)
    assert isinstance(result, StateAudit)
    assert result.state_abbr == "CA"
    assert result.target_year == 2010
    assert result.available_years  # non-empty
    assert 2010 in result.available_years
    assert result.chosen_year == 2010
    assert result.year_delta == 0
    assert result.direction == "exact"
    assert result.eligible_for_calibration is True
    assert result.eligible_for_2026_scoring is True
    assert result.current_year >= 2024


def test_audit_state_colorado_out_of_tolerance() -> None:
    client = FakeClient({
        "https://law.justia.com/codes/colorado/": _load("colorado_index.html"),
    })
    result = audit_state(client, state_abbr="CO", target_year=2010, tolerance=2)
    # CO's earliest year is 2016 — 6 years out from 2010.
    assert 2010 not in result.available_years
    assert min(result.available_years) == 2016
    assert result.chosen_year is None  # no year within ±2
    assert result.direction == "none"
    assert result.eligible_for_calibration is False
    assert result.eligible_for_2026_scoring is True  # current year is recent


def test_audit_state_records_pri_responder_status() -> None:
    client = FakeClient({
        "https://law.justia.com/codes/california/": _load("california_index.html"),
    })
    result = audit_state(client, state_abbr="CA", target_year=2010, tolerance=2)
    assert result.pri_state_reviewed is True  # CA responded per footnote 80


def test_audit_state_current_year_is_max() -> None:
    client = FakeClient({
        "https://law.justia.com/codes/california/": _load("california_index.html"),
    })
    result = audit_state(client, state_abbr="CA", target_year=2010, tolerance=2)
    assert result.current_year == max(result.available_years)
