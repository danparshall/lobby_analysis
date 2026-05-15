"""Tests for the B4 three-pass discovery orchestrator.

Plan: docs/active/api-multi-vintage-retrieval/plans/20260515_b4_three_pass_discovery_plan.md

Builds on the B3PW two-pass orchestrator. Adds an adaptive third pass:
after pass-2 picks a chapter URL, probe its HTML for section children. If
present, pass-3 picks the in-scope sections from a chapter-page snapshot.
If absent (chapter IS the leaf), pass-2's URL becomes the final answer.

Mocks two boundaries (same shape as B3PW):
- FakeAsyncClient: discriminates pass-1 / pass-2 / pass-3 by a marker line
  in the rendered prompt. The orchestrator accepts a distinct pass3_template
  kwarg so tests can mark pass-3 calls without polluting production prompts.
- FakeJustiaClient: URL → HTML map + optional URL → Exception map.
"""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
from types import SimpleNamespace

import pytest


# ---------------------------------------------------------------------------
# Fake clients — pass marker recognition extended to PASS_3
# ---------------------------------------------------------------------------


def _fake_message(text: str) -> SimpleNamespace:
    return SimpleNamespace(
        content=[SimpleNamespace(type="text", text=text)],
        usage=SimpleNamespace(input_tokens=120, output_tokens=80),
        model="claude-sonnet-4-6",
        role="assistant",
        stop_reason="end_turn",
    )


class FakeAsyncClient:
    def __init__(self, responder) -> None:
        self.responder = responder
        self.calls: list[dict] = []
        self.messages = self

    async def create(self, **kwargs):
        self.calls.append(kwargs)
        prompt_text = kwargs["messages"][0]["content"]
        state, vintage = _pair_from_prompt(prompt_text)
        pass_marker = _pass_marker_from_prompt(prompt_text)
        result = self.responder(state, vintage, pass_marker, prompt_text)
        if isinstance(result, BaseException):
            raise result
        await asyncio.sleep(0)
        return _fake_message(result)


def _pair_from_prompt(prompt_text: str) -> tuple[str, int]:
    state = vintage = None
    for line in prompt_text.splitlines():
        s = line.strip()
        if s.startswith("STATE:"):
            state = s.split(":", 1)[1].strip()
        elif s.startswith("VINTAGE:"):
            vintage = int(s.split(":", 1)[1].strip())
    assert state is not None and vintage is not None
    return state, vintage


def _pass_marker_from_prompt(prompt_text: str) -> str:
    # PASS_3 must be checked before PASS_2 because tests may have both
    # markers present in a templated prompt that copies pass-2's structure.
    if "PASS_3" in prompt_text:
        return "PASS_3"
    if "PASS_2" in prompt_text:
        return "PASS_2"
    if "PASS_1" in prompt_text:
        return "PASS_1"
    raise AssertionError(f"No pass marker in prompt: {prompt_text!r}")


class FakeJustiaClient:
    def __init__(
        self,
        html_map: dict[str, str],
        error_map: dict[str, Exception] | None = None,
    ) -> None:
        self.html_map = html_map
        self.error_map = error_map or {}
        self.calls: list[str] = []

    def fetch_page(self, url: str) -> str:
        self.calls.append(url)
        if url in self.error_map:
            raise self.error_map[url]
        if url not in self.html_map:
            raise KeyError(f"FakeJustiaClient has no fixture for {url}")
        return self.html_map[url]


# ---------------------------------------------------------------------------
# Minimal templates — each carries a distinct PASS marker
# ---------------------------------------------------------------------------


MINIMAL_PASS1_TEMPLATE = (
    "PASS_1 title-picker.\n"
    "STATE: {state}\n"
    "VINTAGE: {vintage}\n"
    "Index:\n{state_index}\n"
)

MINIMAL_PASS2_TEMPLATE = (
    "PASS_2 chapter-picker.\n"
    "STATE: {state}\n"
    "VINTAGE: {vintage}\n"
    "Chosen-title rationale: {chosen_title_rationale}\n"
    "Title index:\n{state_index}\n"
)

MINIMAL_PASS3_TEMPLATE = (
    "PASS_3 section-picker.\n"
    "STATE: {state}\n"
    "VINTAGE: {vintage}\n"
    "Chosen-chapter rationale: {chosen_title_rationale}\n"
    "Chapter index:\n{state_index}\n"
)


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------


WY_STATE_INDEX_URL = "https://law.justia.com/codes/wyoming/2010/"
WY_TITLE28_URL = "https://law.justia.com/codes/wyoming/2010/Title28.html"
WY_CHAPTER7_URL = "https://law.justia.com/codes/wyoming/2010/Title28/chapter7.html"

WY_STATE_INDEX_HTML = """
<html><body>
<a href="/codes/wyoming/2010/Title28.html">Title 28 - Legislature</a>
</body></html>
"""

WY_TITLE28_PAGE_HTML = """
<html><body>
<a href="/codes/wyoming/2010/Title28/chapter7.html">Chapter 7 - Lobbyists</a>
</body></html>
"""

# Chapter 7 is the leaf — full statute text, no deeper child links.
WY_CHAPTER7_PAGE_HTML = """
<html><body>
<p>The full text of Wyoming lobbyist registration statute lives here, with
no further internal links to deeper section pages.</p>
<a href="/codes/wyoming/2010/">Up to year index</a>
</body></html>
"""


FL_STATE_INDEX_URL = "https://law.justia.com/codes/florida/2010/"
FL_TITLE3_URL = "https://law.justia.com/codes/florida/2010/TitleIII/TitleIII.html"
FL_TITLE10_URL = "https://law.justia.com/codes/florida/2010/TitleX/TitleX.html"
FL_CHAPTER11_URL = (
    "https://law.justia.com/codes/florida/2010/TitleIII/chapter11/chapter11.html"
)
FL_CHAPTER112_URL = (
    "https://law.justia.com/codes/florida/2010/TitleX/chapter112/chapter112.html"
)
FL_11_045_URL = (
    "https://law.justia.com/codes/florida/2010/TitleIII/chapter11/11_045.html"
)
FL_11_062_URL = (
    "https://law.justia.com/codes/florida/2010/TitleIII/chapter11/11_062.html"
)
FL_11_011_URL = (
    "https://law.justia.com/codes/florida/2010/TitleIII/chapter11/11_011.html"
)
FL_112_3215_URL = (
    "https://law.justia.com/codes/florida/2010/TitleX/chapter112/112_3215.html"
)
FL_112_001_URL = (
    "https://law.justia.com/codes/florida/2010/TitleX/chapter112/112_001.html"
)


FL_STATE_INDEX_HTML = """
<html><body><table>
<tr><td><a href="/codes/florida/2010/TitleIII/TitleIII.html">TITLE III</a></td>
    <td>LEGISLATIVE BRANCH; COMMISSIONS</td></tr>
<tr><td><a href="/codes/florida/2010/TitleX/TitleX.html">TITLE X</a></td>
    <td>PUBLIC OFFICERS, EMPLOYEES, AND RECORDS</td></tr>
</table></body></html>
"""

FL_TITLE3_PAGE_HTML = """
<html><body>
<a href="/codes/florida/2010/TitleIII/chapter11/chapter11.html">Chapter 11 - Legislative Organization</a>
</body></html>
"""

FL_TITLE10_PAGE_HTML = """
<html><body>
<a href="/codes/florida/2010/TitleX/chapter112/chapter112.html">Chapter 112 - Public Officers</a>
</body></html>
"""

FL_CHAPTER11_PAGE_HTML = """
<html><body>
<a href="/codes/florida/2010/TitleIII/chapter11/11_011.html">11.011 Special session</a>
<a href="/codes/florida/2010/TitleIII/chapter11/11_045.html">11.045 Lobbying before the Legislature</a>
<a href="/codes/florida/2010/TitleIII/chapter11/11_062.html">11.062 Use of state funds for lobbying</a>
</body></html>
"""

FL_CHAPTER112_PAGE_HTML = """
<html><body>
<a href="/codes/florida/2010/TitleX/chapter112/112_001.html">112.001 General provisions</a>
<a href="/codes/florida/2010/TitleX/chapter112/112_3215.html">112.3215 Lobbying before the Executive</a>
</body></html>
"""


def _pass1_payload(chosen, *, justia_unavailable=False, alternative_year=None, notes=""):
    return json.dumps(
        {
            "chosen_titles": [
                {"url": url, "rationale": rationale} for url, rationale in chosen
            ],
            "justia_unavailable": justia_unavailable,
            "alternative_year": alternative_year,
            "notes": notes,
        }
    )


def _urls_payload(urls):
    return json.dumps(
        {
            "urls": [
                {"url": url, "role": role, "rationale": rationale}
                for url, role, rationale in urls
            ],
            "justia_unavailable": False,
            "alternative_year": None,
            "notes": "",
        }
    )


# ===========================================================================
# Test 1 — pass-3 is skipped when chapter has no children (WY shape)
# ===========================================================================


@pytest.mark.asyncio
async def test_three_pass_skips_pass3_when_chapter_has_no_children() -> None:
    """WY 2010 chapter7.html is itself the statute leaf — no section children
    underneath. The orchestrator must detect this (empty children-TSV) and
    skip pass-3; the chapter URL becomes the final parsed_urls entry."""
    from scoring.api_retrieval_agent import discover_urls_for_pair_three_pass

    def responder(state, vintage, pass_marker, prompt_text):
        if pass_marker == "PASS_1":
            return _pass1_payload([(WY_TITLE28_URL, "Title 28 is the Legislature.")])
        if pass_marker == "PASS_2":
            return _urls_payload([(WY_CHAPTER7_URL, "core_chapter", "Ch. 7 Lobbyists.")])
        raise AssertionError(f"Pass-3 should not run for WY; got {pass_marker}")

    anthropic_client = FakeAsyncClient(responder)
    justia_client = FakeJustiaClient(
        html_map={
            WY_STATE_INDEX_URL: WY_STATE_INDEX_HTML,
            WY_TITLE28_URL: WY_TITLE28_PAGE_HTML,
            WY_CHAPTER7_URL: WY_CHAPTER7_PAGE_HTML,
        }
    )

    result = await discover_urls_for_pair_three_pass(
        anthropic_client,
        justia_client,
        state="WY",
        vintage=2010,
        slug="wyoming",
        pass1_template=MINIMAL_PASS1_TEMPLATE,
        pass2_template=MINIMAL_PASS2_TEMPLATE,
        pass3_template=MINIMAL_PASS3_TEMPLATE,
    )

    # Exactly 2 Anthropic calls (pass-1 + pass-2; pass-3 skipped).
    assert len(anthropic_client.calls) == 2
    # Chapter7 page was fetched (for the children-probe) but no pass-3 ran.
    assert WY_CHAPTER7_URL in justia_client.calls
    assert result.pass3_prompts == []
    # parsed_urls contains the chapter URL.
    assert [u.url for u in result.parsed_urls] == [WY_CHAPTER7_URL]
    # The chapter was recorded in chosen_chapters.
    assert [c.url for c in result.chosen_chapters] == [WY_CHAPTER7_URL]


# ===========================================================================
# Test 2 — pass-3 runs when chapter has children, filters to in-scope (FL shape)
# ===========================================================================


@pytest.mark.asyncio
async def test_three_pass_runs_pass3_when_chapter_has_children() -> None:
    """FL 2010 chapter11.html has section children — 11.011 (non-lobbying),
    11.045 (lobbying), 11.062 (lobbying). Pass-3 must pick the two lobbying
    sections and drop the non-lobbying one."""
    from scoring.api_retrieval_agent import discover_urls_for_pair_three_pass

    def responder(state, vintage, pass_marker, prompt_text):
        if pass_marker == "PASS_1":
            return _pass1_payload([(FL_TITLE3_URL, "Title III is the Legislative Branch.")])
        if pass_marker == "PASS_2":
            return _urls_payload([(FL_CHAPTER11_URL, "core_chapter", "Ch. 11 Legislative org.")])
        if pass_marker == "PASS_3":
            return _urls_payload(
                [
                    (FL_11_045_URL, "core_chapter", "11.045 Lobbying before the Legislature."),
                    (FL_11_062_URL, "core_chapter", "11.062 Use of state funds for lobbying."),
                ]
            )
        raise AssertionError(f"unknown pass {pass_marker}")

    anthropic_client = FakeAsyncClient(responder)
    justia_client = FakeJustiaClient(
        html_map={
            FL_STATE_INDEX_URL: FL_STATE_INDEX_HTML,
            FL_TITLE3_URL: FL_TITLE3_PAGE_HTML,
            FL_CHAPTER11_URL: FL_CHAPTER11_PAGE_HTML,
        }
    )

    result = await discover_urls_for_pair_three_pass(
        anthropic_client,
        justia_client,
        state="FL",
        vintage=2010,
        slug="florida",
        pass1_template=MINIMAL_PASS1_TEMPLATE,
        pass2_template=MINIMAL_PASS2_TEMPLATE,
        pass3_template=MINIMAL_PASS3_TEMPLATE,
    )

    # 3 Anthropic calls (pass-1, pass-2, pass-3).
    assert len(anthropic_client.calls) == 3
    # parsed_urls has exactly the two lobbying sections (not 11.011).
    urls = sorted(u.url for u in result.parsed_urls)
    assert urls == sorted([FL_11_045_URL, FL_11_062_URL])
    # pass3_prompts has one entry, for chapter11.
    assert len(result.pass3_prompts) == 1
    assert result.pass3_prompts[0]["url"] == FL_CHAPTER11_URL


# ===========================================================================
# Test 3 — fans out across multiple chapters (split-regime FL)
# ===========================================================================


@pytest.mark.asyncio
async def test_three_pass_fans_out_across_multiple_chapters() -> None:
    """Pass-1 picks Title III + Title X. Pass-2 picks one chapter per title.
    Both chapters have section children. Pass-3 runs twice. parsed_urls
    is the dedup'd union of in-scope sections from both chapters."""
    from scoring.api_retrieval_agent import discover_urls_for_pair_three_pass

    def responder(state, vintage, pass_marker, prompt_text):
        if pass_marker == "PASS_1":
            return _pass1_payload(
                [
                    (FL_TITLE3_URL, "Title III Ch.11 legislative-branch lobbying."),
                    (FL_TITLE10_URL, "Title X Ch.112 executive-branch lobbying."),
                ]
            )
        if pass_marker == "PASS_2":
            # The chapter pick differs by title — disambiguate by content of prompt.
            if "TitleIII" in prompt_text:
                return _urls_payload([(FL_CHAPTER11_URL, "core_chapter", "Ch. 11.")])
            if "TitleX" in prompt_text:
                return _urls_payload([(FL_CHAPTER112_URL, "core_chapter", "Ch. 112.")])
            raise AssertionError("pass-2 prompt didn't reference a known title")
        if pass_marker == "PASS_3":
            if "chapter11" in prompt_text and "chapter112" not in prompt_text:
                return _urls_payload(
                    [(FL_11_045_URL, "core_chapter", "11.045"), (FL_11_062_URL, "core_chapter", "11.062")]
                )
            if "chapter112" in prompt_text:
                return _urls_payload([(FL_112_3215_URL, "core_chapter", "112.3215 Exec lobbying.")])
            raise AssertionError("pass-3 prompt didn't reference a known chapter")
        raise AssertionError(f"unknown pass {pass_marker}")

    anthropic_client = FakeAsyncClient(responder)
    justia_client = FakeJustiaClient(
        html_map={
            FL_STATE_INDEX_URL: FL_STATE_INDEX_HTML,
            FL_TITLE3_URL: FL_TITLE3_PAGE_HTML,
            FL_TITLE10_URL: FL_TITLE10_PAGE_HTML,
            FL_CHAPTER11_URL: FL_CHAPTER11_PAGE_HTML,
            FL_CHAPTER112_URL: FL_CHAPTER112_PAGE_HTML,
        }
    )

    result = await discover_urls_for_pair_three_pass(
        anthropic_client,
        justia_client,
        state="FL",
        vintage=2010,
        slug="florida",
        pass1_template=MINIMAL_PASS1_TEMPLATE,
        pass2_template=MINIMAL_PASS2_TEMPLATE,
        pass3_template=MINIMAL_PASS3_TEMPLATE,
    )

    # 5 Anthropic calls: 1 pass-1 + 2 pass-2 + 2 pass-3.
    assert len(anthropic_client.calls) == 5
    urls = sorted(u.url for u in result.parsed_urls)
    assert urls == sorted([FL_11_045_URL, FL_11_062_URL, FL_112_3215_URL])
    assert len(result.pass3_prompts) == 2


# ===========================================================================
# Test 4 — one chapter-fetch failure is isolated; other chapter completes
# ===========================================================================


@pytest.mark.asyncio
async def test_three_pass_isolates_chapter_fetch_failure() -> None:
    """Pass-2 picks two chapter URLs; one chapter-page fetch raises; the
    other completes; pass-3 runs once (on the surviving chapter); failure
    is logged in chapter_fetch_failures."""
    from scoring.api_retrieval_agent import discover_urls_for_pair_three_pass

    def responder(state, vintage, pass_marker, prompt_text):
        if pass_marker == "PASS_1":
            return _pass1_payload(
                [
                    (FL_TITLE3_URL, "Title III."),
                    (FL_TITLE10_URL, "Title X."),
                ]
            )
        if pass_marker == "PASS_2":
            if "TitleIII" in prompt_text:
                return _urls_payload([(FL_CHAPTER11_URL, "core_chapter", "Ch. 11.")])
            return _urls_payload([(FL_CHAPTER112_URL, "core_chapter", "Ch. 112.")])
        if pass_marker == "PASS_3":
            # Only Ch. 11 should reach pass-3 (Ch. 112 fetch raises).
            assert "chapter11" in prompt_text and "chapter112" not in prompt_text, (
                f"pass-3 should only run on the surviving chapter; got {prompt_text!r}"
            )
            return _urls_payload([(FL_11_045_URL, "core_chapter", "11.045")])
        raise AssertionError(f"unknown pass {pass_marker}")

    anthropic_client = FakeAsyncClient(responder)
    justia_client = FakeJustiaClient(
        html_map={
            FL_STATE_INDEX_URL: FL_STATE_INDEX_HTML,
            FL_TITLE3_URL: FL_TITLE3_PAGE_HTML,
            FL_TITLE10_URL: FL_TITLE10_PAGE_HTML,
            FL_CHAPTER11_URL: FL_CHAPTER11_PAGE_HTML,
        },
        error_map={FL_CHAPTER112_URL: RuntimeError("simulated outage on Ch. 112")},
    )

    result = await discover_urls_for_pair_three_pass(
        anthropic_client,
        justia_client,
        state="FL",
        vintage=2010,
        slug="florida",
        pass1_template=MINIMAL_PASS1_TEMPLATE,
        pass2_template=MINIMAL_PASS2_TEMPLATE,
        pass3_template=MINIMAL_PASS3_TEMPLATE,
    )

    failures = result.chapter_fetch_failures
    assert len(failures) == 1
    assert failures[0]["url"] == FL_CHAPTER112_URL
    assert "simulated outage" in failures[0]["error"]
    assert [u.url for u in result.parsed_urls] == [FL_11_045_URL]


# ===========================================================================
# Test 5 — three-pass checkpoint round-trips
# ===========================================================================


@pytest.mark.asyncio
async def test_three_pass_pair_checkpoint_records_all_three_passes(tmp_path: Path) -> None:
    """Serialize → write → read → deserialize. All B4-specific fields
    round-trip: chosen_chapters, pass3_prompts, chapter_fetch_failures,
    plus everything inherited from B3PW."""
    from scoring.api_retrieval_agent import (
        discover_urls_for_pair_three_pass,
        serialize_pass1_pass2_pass3_result,
        deserialize_pass1_pass2_pass3_result,
    )

    def responder(state, vintage, pass_marker, prompt_text):
        if pass_marker == "PASS_1":
            return _pass1_payload([(FL_TITLE3_URL, "Title III.")])
        if pass_marker == "PASS_2":
            return _urls_payload([(FL_CHAPTER11_URL, "core_chapter", "Ch. 11.")])
        if pass_marker == "PASS_3":
            return _urls_payload([(FL_11_045_URL, "core_chapter", "11.045")])
        raise AssertionError(f"unknown pass {pass_marker}")

    anthropic_client = FakeAsyncClient(responder)
    justia_client = FakeJustiaClient(
        html_map={
            FL_STATE_INDEX_URL: FL_STATE_INDEX_HTML,
            FL_TITLE3_URL: FL_TITLE3_PAGE_HTML,
            FL_CHAPTER11_URL: FL_CHAPTER11_PAGE_HTML,
        }
    )

    result = await discover_urls_for_pair_three_pass(
        anthropic_client,
        justia_client,
        state="FL",
        vintage=2010,
        slug="florida",
        pass1_template=MINIMAL_PASS1_TEMPLATE,
        pass2_template=MINIMAL_PASS2_TEMPLATE,
        pass3_template=MINIMAL_PASS3_TEMPLATE,
    )

    checkpoint_path = tmp_path / "FL" / "2010" / "discovered_urls.json"
    checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
    checkpoint_path.write_text(
        json.dumps(serialize_pass1_pass2_pass3_result(result), indent=2),
        encoding="utf-8",
    )

    on_disk = json.loads(checkpoint_path.read_text(encoding="utf-8"))
    assert "PASS_1" in on_disk["pass1_prompt"]
    assert on_disk["chosen_titles"][0]["url"] == FL_TITLE3_URL
    assert on_disk["chosen_chapters"][0]["url"] == FL_CHAPTER11_URL
    assert len(on_disk["pass2_prompts"]) == 1
    assert len(on_disk["pass3_prompts"]) == 1
    assert on_disk["pass3_prompts"][0]["url"] == FL_CHAPTER11_URL
    assert "PASS_3" in on_disk["pass3_prompts"][0]["prompt"]
    assert on_disk["parsed_urls"][0]["url"] == FL_11_045_URL
    assert on_disk["chapter_fetch_failures"] == []

    rehydrated = deserialize_pass1_pass2_pass3_result(on_disk)
    assert [u.url for u in rehydrated.parsed_urls] == [FL_11_045_URL]
    assert [c.url for c in rehydrated.chosen_chapters] == [FL_CHAPTER11_URL]
