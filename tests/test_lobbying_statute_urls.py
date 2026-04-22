"""Sanity tests for the curated lobby-statute URL config."""

from __future__ import annotations

from scoring.lobbying_statute_urls import CALIBRATION_SUBSET, LOBBYING_STATUTE_URLS


def test_all_calibration_subset_keys_present() -> None:
    for key in CALIBRATION_SUBSET:
        assert key in LOBBYING_STATUTE_URLS, f"missing URL list for {key}"
        assert LOBBYING_STATUTE_URLS[key], f"empty URL list for {key}"


def test_all_urls_are_justia_https() -> None:
    for key, urls in LOBBYING_STATUTE_URLS.items():
        for u in urls:
            assert u.startswith("https://law.justia.com/codes/"), (
                f"{key}: non-Justia URL {u}"
            )


def test_tx_uses_2009_vintage_not_2010() -> None:
    # Justia doesn't host TX 2010; Phase 1 audit chose 2009 as nearest within
    # ±2 tolerance. Regression check so nobody silently adds ("TX", 2010).
    assert ("TX", 2009) in LOBBYING_STATUTE_URLS
    assert ("TX", 2010) not in LOBBYING_STATUTE_URLS


def test_subset_keys_match_audit_chosen_years() -> None:
    # CA/NY/WI/WY at 2010 (exact), TX at 2009 (pre-preferred). Matches the
    # Phase 1 Justia retrieval audit's chosen_year column.
    expected = {("CA", 2010), ("TX", 2009), ("NY", 2010), ("WI", 2010), ("WY", 2010)}
    assert set(CALIBRATION_SUBSET) == expected
