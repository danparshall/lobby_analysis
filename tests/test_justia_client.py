"""Parser tests for scoring.justia_client.

Fixtures live in tests/fixtures/justia/ (real Justia HTML pages captured via
Playwright). Tests never hit the live network.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from scoring.justia_client import (
    TitleEntry,
    parse_children_list,
    parse_state_year_index,
    parse_statute_text,
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


# ---------- parse_statute_text ----------
#
# Works on any Justia statute-leaf page — CA section-range leaves, TX full-chapter
# leaves, NY single-page acts, WY chapter-leaves. Extracts main-content statute
# text and strips Justia navigation chrome. Returns a single string.


def test_parse_statute_text_ca_section_range_contains_definitions() -> None:
    # CA Gov §§ 86100-86118 is the Political Reform Act definitions article.
    # §86100 defines "Lobbying firm"; §86115 defines "Lobbyist" — at least one
    # definitional phrase must survive the strip.
    html = _fixture("california_2010_gov_sections_86100_86118.html")
    text = parse_statute_text(html)
    assert "86100" in text  # section number preserved
    # Canonical definitional phrasing found verbatim in the PRA.
    low = text.lower()
    assert "lobbyist" in low or "lobbying firm" in low


def test_parse_statute_text_tx_chapter_contains_registrant_definition() -> None:
    # TX Gov Code Ch. 305 §305.002 defines "Registrant" (among others).
    html = _fixture("texas_2009_gov_title3_chapter305.html")
    text = parse_statute_text(html)
    assert "305" in text
    low = text.lower()
    assert "registrant" in low
    assert "lobbyist" in low or "lobbying" in low


def test_parse_statute_text_ny_rla_contains_legislative_declaration() -> None:
    # NY Regulation of Lobbying Act §1 opens with "Section 1. Legislative
    # declaration. The legislature hereby declares that the operation of
    # responsible democratic government..."
    html = _fixture("new_york_2010_rla.html")
    text = parse_statute_text(html)
    low = text.lower()
    assert "legislative declaration" in low
    assert "lobbying" in low


def test_parse_statute_text_wy_chapter_contains_lobbyist_term() -> None:
    # WY Title 28 Ch. 7 is titled "Lobbyists" — text must mention the word.
    html = _fixture("wyoming_2010_title28_chapter7.html")
    text = parse_statute_text(html)
    assert "lobbyist" in text.lower()


def test_parse_statute_text_strips_justia_chrome() -> None:
    # Output must not contain Justia navigation/footer chrome. "Find a Lawyer"
    # is a prominent sidebar CTA; "Ask a Lawyer" is another. Neither belongs
    # in the statute text.
    html = _fixture("california_2010_gov_sections_86100_86118.html")
    text = parse_statute_text(html)
    assert "Find a Lawyer" not in text
    assert "Ask a Lawyer" not in text
    # The "Justia Legal Resources" footer section should not appear either.
    assert "Justia Legal Resources" not in text


def test_parse_statute_text_returns_substantial_text() -> None:
    # Sanity: a chapter-leaf with known statute content shouldn't come back
    # near-empty after chrome stripping. Covers the regression where a too-
    # aggressive stripper might delete the statute body itself.
    html = _fixture("texas_2009_gov_title3_chapter305.html")
    text = parse_statute_text(html)
    # TX Ch. 305 main-content is ~66KB. After stripping we should still have
    # tens of KB of statute text.
    assert len(text) > 30_000


# ---------- parse_children_list ----------
#
# Discovery helper used during curation: given a Justia listing page and its
# URL, return the list of one-level-deeper child URLs (absolute). Not used by
# scheduled retrieval (which relies on lobbying_statute_urls.LOBBYING_STATUTE_URLS).


def test_parse_children_list_ca_gov_title_returns_section_ranges() -> None:
    parent = "https://law.justia.com/codes/california/2010/gov.html"
    html = _fixture("california_2010_gov_title.html")
    children = parse_children_list(html, parent)
    # CA Gov title lists 1000+ section-range leaves. All children should be
    # /codes/california/2010/gov/...html URLs.
    assert len(children) > 500
    for c in children:
        assert c.startswith("https://law.justia.com/codes/california/2010/gov/")
        assert c.endswith(".html")
    # Spot-check a known range.
    assert "https://law.justia.com/codes/california/2010/gov/86100-86118.html" in children


def test_parse_children_list_tx_gov_code_returns_title_dirs() -> None:
    parent = "https://law.justia.com/codes/texas/2009/government-code/"
    html = _fixture("texas_2009_government_code_title.html")
    children = parse_children_list(html, parent)
    # TX Gov Code has 11 titles.
    assert len(children) == 11
    for c in children:
        assert c.startswith(
            "https://law.justia.com/codes/texas/2009/government-code/"
        )
        # TX uses trailing-slash directory URLs, not .html.
        assert c.endswith("/")
    # Spot-check Title 3 (contains Ch. 305 Lobbyists).
    assert any("title-3-legislative-branch" in c for c in children)


def test_parse_children_list_wi_chapter_returns_sections() -> None:
    parent = "https://law.justia.com/codes/wisconsin/2010/13/13.html"
    html = _fixture("wisconsin_2010_chapter13.html")
    children = parse_children_list(html, parent)
    # WI Ch. 13 has ~100 sections (§13.01 through §13.83-ish).
    assert len(children) > 50
    for c in children:
        assert c.startswith("https://law.justia.com/codes/wisconsin/2010/13/")
        assert c.endswith(".html")
    # Spot-check a lobbying section.
    assert "https://law.justia.com/codes/wisconsin/2010/13/13.61.html" in children


def test_parse_children_list_only_direct_children_not_grandchildren() -> None:
    # CA gov.html title page → children are section-range leaves. It should
    # NOT return hrefs from deeper in the hierarchy (e.g., /gov/foo/bar.html)
    # even if the HTML happens to contain them somewhere.
    parent = "https://law.justia.com/codes/california/2010/gov.html"
    html = _fixture("california_2010_gov_title.html")
    children = parse_children_list(html, parent)
    for c in children:
        # Strip the parent prefix; what remains should be a single segment
        # (no additional slashes in the relative path beyond the leaf).
        rest = c.replace("https://law.justia.com/codes/california/2010/gov/", "")
        # The leaf is one segment — "NNNN-MMMM.html". Grandchildren would be
        # "subcategory/NNNN.html" and would fail this.
        assert "/" not in rest, f"grandchild leaked through: {c}"


def test_parse_children_list_normalizes_to_absolute_urls() -> None:
    # Justia hrefs are typically relative (/codes/...). parse_children_list
    # must normalize to https://law.justia.com/... so downstream callers
    # don't have to.
    parent = "https://law.justia.com/codes/texas/2009/government-code/"
    html = _fixture("texas_2009_government_code_title.html")
    children = parse_children_list(html, parent)
    for c in children:
        assert c.startswith("https://"), f"relative URL leaked: {c}"


def test_parse_children_list_excludes_signin_and_self_parent() -> None:
    # Justia pages typically have a "Log In" link to accounts.justia.com/signin
    # which technically shares the parent URL as a destination query param.
    # parse_children_list must exclude: (a) the parent URL itself, (b) external
    # accounts.justia.com links, (c) anchors that don't descend.
    parent = "https://law.justia.com/codes/texas/2009/government-code/"
    html = _fixture("texas_2009_government_code_title.html")
    children = parse_children_list(html, parent)
    for c in children:
        assert "accounts.justia.com" not in c
        assert c != parent
        assert c.rstrip("/") != parent.rstrip("/")
