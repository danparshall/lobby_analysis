"""Parser tests for scoring.justia_client.

Fixtures live in tests/fixtures/justia/ (real Justia HTML pages captured via
Playwright). Tests never hit the live network.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from scoring.justia_client import (
    TitleEntry,
    parse_state_year_index,
    parse_year_title_index,
)

FIXTURES_DIR = Path(__file__).parent / "fixtures" / "justia"


def _fixture(name: str) -> str:
    return (FIXTURES_DIR / name).read_text(encoding="utf-8")


# ---------- parse_state_year_index ----------


def test_parse_state_year_index_california_returns_expected_years() -> None:
    html = _fixture("california_index.html")
    years = parse_state_year_index(html)
    # CA fixture has years 2005 through 2026 (inclusive-ish).
    assert 2010 in years
    assert 2009 in years
    assert 2024 in years
    assert 2005 in years
    # Sanity: monotonically sorted-ish; at least one year >= 2025 (current).
    assert any(y >= 2025 for y in years)


def test_parse_state_year_index_colorado_has_no_2010() -> None:
    html = _fixture("colorado_index.html")
    years = parse_state_year_index(html)
    # CO fixture's earliest year is 2016 — no 2010.
    assert 2010 not in years
    assert 2009 not in years
    assert 2008 not in years
    # But it does have recent years.
    assert 2024 in years
    # The earliest CO year should be 2016 (per inspection of the fixture).
    assert min(years) == 2016


def test_parse_state_year_index_returns_ints() -> None:
    html = _fixture("california_index.html")
    years = parse_state_year_index(html)
    assert all(isinstance(y, int) for y in years)


def test_parse_state_year_index_deduplicates() -> None:
    html = _fixture("california_index.html")
    years = parse_state_year_index(html)
    assert len(years) == len(set(years))


# ---------- parse_year_title_index ----------


def test_parse_year_title_index_ca_2010_has_government_code() -> None:
    html = _fixture("california_2010_index.html")
    titles = parse_year_title_index(html)
    names = [t.name for t in titles]
    assert "Government Code" in names


def test_parse_year_title_index_ca_2010_extracts_slug_from_url() -> None:
    html = _fixture("california_2010_index.html")
    titles = parse_year_title_index(html)
    gov = next(t for t in titles if t.name == "Government Code")
    assert gov.slug == "gov"
    assert gov.url.endswith("/codes/california/2010/gov.html")


def test_parse_year_title_index_ca_2010_returns_all_titles() -> None:
    html = _fixture("california_2010_index.html")
    titles = parse_year_title_index(html)
    # CA 2010 has 29 top-level codes (BPC, CIV, CCP, ... WIC).
    assert len(titles) == 29


def test_parse_year_title_index_returns_title_entry_objects() -> None:
    html = _fixture("california_2010_index.html")
    titles = parse_year_title_index(html)
    assert all(isinstance(t, TitleEntry) for t in titles)


def test_parse_year_title_index_names_are_stripped() -> None:
    html = _fixture("california_2010_index.html")
    titles = parse_year_title_index(html)
    for t in titles:
        assert t.name == t.name.strip()
        assert not t.name.startswith(" ")
