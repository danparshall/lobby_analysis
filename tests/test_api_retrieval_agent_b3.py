"""Tests for the B3 two-pass discovery orchestrator.

Plan: docs/active/api-multi-vintage-retrieval/plans/20260514_b3_two_pass_discovery_plan_playwright.md

Mocks two boundaries:
- `client.messages.create` (Anthropic) via `FakeAsyncClient` — same shape as
  the B2 tests but with a `pass_marker` parameter on the responder so a
  single fake can return pass-1 and pass-2 responses for the same pair.
- `justia_client.Client` (HTTP fetcher) via `FakeJustiaClient` — satisfies
  the `fetch_page(url) -> str` protocol with a URL → HTML mapping plus an
  optional URL → Exception mapping for failure-isolation tests.

Everything past those two boundaries is real code under test.
"""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
from types import SimpleNamespace

import pytest


# ---------------------------------------------------------------------------
# Fake Anthropic client (carry-forward from B2 with pass-marker dispatch)
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
    """Duck-typed `anthropic.AsyncAnthropic`.

    The responder receives `(state, vintage, pass_marker)` where `pass_marker`
    is "PASS_1" or "PASS_2" — detected by a literal marker line in the
    outgoing prompt. Returns either response text or an exception to raise.
    """

    def __init__(self, responder) -> None:
        self.responder = responder
        self.calls: list[dict] = []
        self.messages = self

    async def create(self, **kwargs):
        self.calls.append(kwargs)
        prompt_text = kwargs["messages"][0]["content"]
        state, vintage = _pair_from_prompt(prompt_text)
        pass_marker = _pass_marker_from_prompt(prompt_text)
        result = self.responder(state, vintage, pass_marker)
        if isinstance(result, BaseException):
            raise result
        await asyncio.sleep(0)
        return _fake_message(result)


def _pair_from_prompt(prompt_text: str) -> tuple[str, int]:
    state: str | None = None
    vintage: int | None = None
    for line in prompt_text.splitlines():
        stripped = line.strip()
        if stripped.startswith("STATE:"):
            state = stripped.split(":", 1)[1].strip()
        elif stripped.startswith("VINTAGE:"):
            vintage = int(stripped.split(":", 1)[1].strip())
    assert state is not None and vintage is not None, (
        f"Prompt missing STATE/VINTAGE markers: {prompt_text!r}"
    )
    return state, vintage


def _pass_marker_from_prompt(prompt_text: str) -> str:
    if "PASS_1" in prompt_text:
        return "PASS_1"
    if "PASS_2" in prompt_text:
        return "PASS_2"
    raise AssertionError(
        f"Prompt did not contain PASS_1 or PASS_2 marker: {prompt_text!r}"
    )


# ---------------------------------------------------------------------------
# Fake Justia client (Client protocol — fetch_page(url) -> str)
# ---------------------------------------------------------------------------


class FakeJustiaClient:
    """Stand-in for `justia_client.PlaywrightClient`.

    Returns HTML from `html_map` for matching URLs; raises from `error_map`
    when a URL is configured to fail. Records every call for assertions.
    """

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
# Minimal prompt templates (real prompts live in src/scoring/*.md)
# ---------------------------------------------------------------------------


MINIMAL_PASS1_TEMPLATE = (
    "PASS_1 title-picker.\n"
    "STATE: {state}\n"
    "VINTAGE: {vintage}\n"
    "Index:\n{state_index}\n"
    "Return JSON: chosen_titles[]/justia_unavailable/alternative_year/notes.\n"
)

MINIMAL_PASS2_TEMPLATE = (
    "PASS_2 URL-proposer.\n"
    "STATE: {state}\n"
    "VINTAGE: {vintage}\n"
    "Chosen-title rationale: {chosen_title_rationale}\n"
    "Title index:\n{state_index}\n"
    'Return JSON: {{"urls": [...]}}\n'
)


# ---------------------------------------------------------------------------
# Shared HTML fixtures (small, hand-rolled — not real Justia HTML)
# ---------------------------------------------------------------------------


WY_STATE_INDEX_URL = "https://law.justia.com/codes/wyoming/2010/"
WY_TITLE28_URL = "https://law.justia.com/codes/wyoming/2010/Title28.html"
WY_TITLE1_URL = "https://law.justia.com/codes/wyoming/2010/Title1.html"
WY_CHAPTER7_URL = "https://law.justia.com/codes/wyoming/2010/Title28/chapter7.html"
WY_CHAPTER1_URL = "https://law.justia.com/codes/wyoming/2010/Title28/chapter1.html"


WY_STATE_INDEX_HTML = f"""
<html><body>
<a href="/codes/wyoming/2010/Title1.html">Title 1 - General Provisions</a>
<a href="/codes/wyoming/2010/Title28.html">Title 28 - Public Officers and Employees</a>
<a href="https://en.wikipedia.org/wiki/Wyoming">Out-of-namespace link</a>
</body></html>
"""

WY_TITLE28_PAGE_HTML = f"""
<html><body>
<a href="/codes/wyoming/2010/Title28/chapter1.html">Chapter 1 - General</a>
<a href="/codes/wyoming/2010/Title28/chapter7.html">Chapter 7 - Lobbyists</a>
<a href="https://accounts.justia.com/signin">Log In</a>
</body></html>
"""

WY_TITLE1_PAGE_HTML = f"""
<html><body>
<a href="/codes/wyoming/2010/Title1/chapter3.html">Chapter 3 - Misc</a>
</body></html>
"""


def _pass1_payload(
    chosen: list[tuple[str, str]],
    *,
    justia_unavailable: bool = False,
    alternative_year: int | None = None,
    notes: str = "",
) -> str:
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


def _pass2_payload(
    urls: list[tuple[str, str, str]],
    *,
    justia_unavailable: bool = False,
    notes: str = "",
) -> str:
    return json.dumps(
        {
            "urls": [
                {"url": url, "role": role, "rationale": rationale}
                for url, role, rationale in urls
            ],
            "justia_unavailable": justia_unavailable,
            "alternative_year": None,
            "notes": notes,
        }
    )


# ===========================================================================
# Helper test — _build_justia_link_tsv handles the Foo/Foo.html pattern
# under a directory parent (WY state-year-index links go 2 segments deep)
# ===========================================================================


def test_build_justia_link_tsv_uses_parent_row_text_when_anchor_is_terse() -> None:
    """When the anchor text alone is uninformative (just `TITLE III`), the
    TSV must enrich it with the parent <tr>'s full text — picking up the
    subject name from the sibling <td>. This is the FL 2010 state-year
    index shape; without the fix pass-1 can't disambiguate Roman-numeral
    titles by topic.
    """
    from scoring.api_retrieval_agent import _build_justia_link_tsv

    parent = "https://law.justia.com/codes/florida/2010/"
    html = """
    <html><body><table>
    <tr><td><strong><a href="/codes/florida/2010/TitleII/TitleII.html">TITLE II</a></strong></td>
        <td>STATE ORGANIZATION</td></tr>
    <tr><td><strong><a href="/codes/florida/2010/TitleIII/TitleIII.html">TITLE III</a></strong></td>
        <td>LEGISLATIVE BRANCH; COMMISSIONS</td></tr>
    </table></body></html>
    """
    tsv = _build_justia_link_tsv(html, parent)
    lines = tsv.splitlines()
    # Find the TitleIII line; description must include the sibling-td subject.
    title3_line = next(l for l in lines if "TitleIII/TitleIII.html" in l)
    assert "LEGISLATIVE BRANCH" in title3_line, (
        f"Expected sibling-td subject in TSV; got line: {title3_line!r}"
    )
    title2_line = next(l for l in lines if "TitleII/TitleII.html" in l)
    assert "STATE ORGANIZATION" in title2_line


def test_build_justia_link_tsv_directory_parent_with_foo_foo_html_children() -> None:
    """When a directory parent (e.g., /codes/wyoming/2010/) links to entries
    of the form `TitleN/TitleN.html`, the helper must include them in the TSV.

    This is the empirically-observed shape of WY 2010's state-year-index
    page: 43 anchors, all of form `/codes/wyoming/2010/TitleN/TitleN.html`.
    The earlier "one-segment-deeper" check rejected them as too deep, which
    starved pass-1's prompt of any usable links.
    """
    from scoring.api_retrieval_agent import _build_justia_link_tsv

    parent = "https://law.justia.com/codes/wyoming/2010/"
    html = """
    <html><body>
    <a href="/codes/wyoming/2010/Title1/Title1.html">Title 1 - General Provisions</a>
    <a href="/codes/wyoming/2010/Title28/Title28.html">Title 28 - Public Officers and Employees</a>
    <a href="/codes/wyoming/2010/Title28/Title28/Title28.html">Grandchild (should be rejected)</a>
    <a href="/codes/wyoming/2010/Title28/chapter7.html">Chapter-level link (should be rejected)</a>
    <a href="https://en.wikipedia.org/wiki/Wyoming">External (should be rejected)</a>
    </body></html>
    """

    tsv = _build_justia_link_tsv(html, parent)
    lines = tsv.splitlines()
    urls = [line.split("\t", 1)[0] for line in lines]

    assert "https://law.justia.com/codes/wyoming/2010/Title1/Title1.html" in urls
    assert "https://law.justia.com/codes/wyoming/2010/Title28/Title28.html" in urls
    # The Foo/Foo.html exception is narrow — only ``X/X.html`` is accepted.
    # A bare `Title28/chapter7.html` (different segments) must NOT slip in
    # at the directory-parent level — that would let chapter URLs masquerade
    # as title URLs in pass-1.
    assert "https://law.justia.com/codes/wyoming/2010/Title28/chapter7.html" not in urls
    # A genuine grandchild (Title28/Title28/Title28.html) is also rejected.
    assert "https://law.justia.com/codes/wyoming/2010/Title28/Title28/Title28.html" not in urls
    # External links rejected.
    assert not any("wikipedia" in u for u in urls)

    # Anchor text preserved, tab-delimited.
    title28_line = next(l for l in lines if "Title28.html\t" in l)
    assert "Public Officers" in title28_line


# ===========================================================================
# Test 1 — single-title two-pass returns pass-2 URLs
# ===========================================================================


@pytest.mark.asyncio
async def test_two_pass_returns_pass2_urls_for_single_title(tmp_path: Path) -> None:
    """Pass-1 picks one title; orchestrator fetches it; pass-2 picks one
    chapter URL; final parsed_urls contains exactly that chapter URL."""
    from scoring.api_retrieval_agent import discover_urls_for_pair_two_pass

    def responder(state: str, vintage: int, pass_marker: str) -> str:
        if pass_marker == "PASS_1":
            return _pass1_payload([(WY_TITLE28_URL, "Title 28 is Public Officers — contains lobbyist registration ch. 7.")])
        return _pass2_payload([(WY_CHAPTER7_URL, "core_chapter", "Ch. 7 Lobbyists.")])

    anthropic_client = FakeAsyncClient(responder)
    justia_client = FakeJustiaClient(
        html_map={
            WY_STATE_INDEX_URL: WY_STATE_INDEX_HTML,
            WY_TITLE28_URL: WY_TITLE28_PAGE_HTML,
        }
    )

    result = await discover_urls_for_pair_two_pass(
        anthropic_client,
        justia_client,
        state="WY",
        vintage=2010,
        slug="wyoming",
        pass1_template=MINIMAL_PASS1_TEMPLATE,
        pass2_template=MINIMAL_PASS2_TEMPLATE,
    )

    assert [u.url for u in result.parsed_urls] == [WY_CHAPTER7_URL]
    assert result.parsed_urls[0].role == "core_chapter"
    # Both passes were exercised.
    assert len(anthropic_client.calls) == 2
    # Two Justia fetches: state-year index + Title28 page.
    assert justia_client.calls == [WY_STATE_INDEX_URL, WY_TITLE28_URL]


# ===========================================================================
# Test 2 — fans out across multiple chosen titles, dedups on URL
# ===========================================================================


@pytest.mark.asyncio
async def test_two_pass_fans_out_to_multiple_titles(tmp_path: Path) -> None:
    """Pass-1 picks two titles; orchestrator fetches both; pass-2 runs
    once per title; parsed_urls is the dedup'd union."""
    from scoring.api_retrieval_agent import discover_urls_for_pair_two_pass

    duplicate_url = WY_CHAPTER7_URL  # appears under both titles to test dedup

    def responder(state: str, vintage: int, pass_marker: str) -> str:
        if pass_marker == "PASS_1":
            return _pass1_payload(
                [
                    (WY_TITLE1_URL, "Title 1 might contain general provisions about lobbying."),
                    (WY_TITLE28_URL, "Title 28 is Public Officers — contains lobbyist registration ch. 7."),
                ]
            )
        # Pass-2 returns different URLs depending on which title page was
        # snapshot'd — distinguish by chosen_title_rationale carried in the
        # prompt.
        # Inspect the prompt to figure out which title we're on.
        # Easier: just return the same shared URL twice, plus one unique each.
        return _pass2_payload(
            [
                (duplicate_url, "core_chapter", "Ch. 7"),
                (WY_CHAPTER1_URL, "support_chapter", "Ch. 1"),
            ]
        )

    anthropic_client = FakeAsyncClient(responder)
    justia_client = FakeJustiaClient(
        html_map={
            WY_STATE_INDEX_URL: WY_STATE_INDEX_HTML,
            WY_TITLE1_URL: WY_TITLE1_PAGE_HTML,
            WY_TITLE28_URL: WY_TITLE28_PAGE_HTML,
        }
    )

    result = await discover_urls_for_pair_two_pass(
        anthropic_client,
        justia_client,
        state="WY",
        vintage=2010,
        slug="wyoming",
        pass1_template=MINIMAL_PASS1_TEMPLATE,
        pass2_template=MINIMAL_PASS2_TEMPLATE,
    )

    # Three Anthropic calls (1 pass-1 + 2 pass-2).
    assert len(anthropic_client.calls) == 3
    # Three Justia fetches (state index + 2 title pages).
    assert set(justia_client.calls) == {WY_STATE_INDEX_URL, WY_TITLE1_URL, WY_TITLE28_URL}
    assert len(justia_client.calls) == 3
    # Two unique URLs (dedup on the duplicate chapter7 URL).
    urls = sorted(u.url for u in result.parsed_urls)
    assert urls == sorted({WY_CHAPTER7_URL, WY_CHAPTER1_URL})


# ===========================================================================
# Test 3 — non-Justia / out-of-namespace pass-1 picks are rejected
# ===========================================================================


@pytest.mark.asyncio
async def test_two_pass_rejects_non_state_year_titles_from_pass1(tmp_path: Path) -> None:
    """Pass-1 returns one valid + one out-of-namespace URL. Orchestrator drops
    the bad one into pass1_schema_violations and proceeds with the valid one."""
    from scoring.api_retrieval_agent import discover_urls_for_pair_two_pass

    bad_url = "https://en.wikipedia.org/wiki/Wyoming_lobbying_law"

    def responder(state: str, vintage: int, pass_marker: str) -> str:
        if pass_marker == "PASS_1":
            return _pass1_payload(
                [
                    (WY_TITLE28_URL, "Real title."),
                    (bad_url, "Out-of-namespace link."),
                ]
            )
        return _pass2_payload([(WY_CHAPTER7_URL, "core_chapter", "Ch. 7")])

    anthropic_client = FakeAsyncClient(responder)
    justia_client = FakeJustiaClient(
        html_map={
            WY_STATE_INDEX_URL: WY_STATE_INDEX_HTML,
            WY_TITLE28_URL: WY_TITLE28_PAGE_HTML,
        }
    )

    result = await discover_urls_for_pair_two_pass(
        anthropic_client,
        justia_client,
        state="WY",
        vintage=2010,
        slug="wyoming",
        pass1_template=MINIMAL_PASS1_TEMPLATE,
        pass2_template=MINIMAL_PASS2_TEMPLATE,
    )

    # Pass-1 schema violation recorded.
    assert any(
        v.get("url") == bad_url for v in result.pass1_schema_violations
    ), f"Expected {bad_url} in violations, got {result.pass1_schema_violations}"
    # Only the valid title was fetched (no wikipedia fetch attempted).
    assert justia_client.calls == [WY_STATE_INDEX_URL, WY_TITLE28_URL]
    # Pass-2 still ran on the surviving valid title.
    assert [u.url for u in result.parsed_urls] == [WY_CHAPTER7_URL]


# ===========================================================================
# Test 4 — pass-1 justia_unavailable=true short-circuits the orchestrator
# ===========================================================================


@pytest.mark.asyncio
async def test_two_pass_propagates_justia_unavailable_from_pass1(tmp_path: Path) -> None:
    """Pass-1 reports justia_unavailable=true with empty chosen_titles.
    Orchestrator does NOT call pass-2, does NOT fetch any title page,
    and reports the availability signal up."""
    from scoring.api_retrieval_agent import discover_urls_for_pair_two_pass

    def responder(state: str, vintage: int, pass_marker: str) -> str:
        if pass_marker == "PASS_1":
            return _pass1_payload(
                [],
                justia_unavailable=True,
                notes="Justia hosts no WY statutes pre-2009.",
            )
        # Should never be called.
        raise AssertionError("Pass-2 must not run when pass-1 reports unavailable")

    anthropic_client = FakeAsyncClient(responder)
    justia_client = FakeJustiaClient(
        html_map={WY_STATE_INDEX_URL: WY_STATE_INDEX_HTML}
    )

    result = await discover_urls_for_pair_two_pass(
        anthropic_client,
        justia_client,
        state="WY",
        vintage=2010,
        slug="wyoming",
        pass1_template=MINIMAL_PASS1_TEMPLATE,
        pass2_template=MINIMAL_PASS2_TEMPLATE,
    )

    # Exactly one Anthropic call (pass-1).
    assert len(anthropic_client.calls) == 1
    # Exactly one Justia fetch (state-year index).
    assert justia_client.calls == [WY_STATE_INDEX_URL]
    # Empty parsed_urls; availability propagated.
    assert result.parsed_urls == []
    assert result.pass1_availability["justia_unavailable"] is True
    assert "no WY statutes" in result.pass1_availability["notes"]


# ===========================================================================
# Test 5 — one title-page fetch fails; the other completes; failure logged
# ===========================================================================


@pytest.mark.asyncio
async def test_two_pass_isolates_title_fetch_failure(tmp_path: Path) -> None:
    """Pass-1 picks two titles; Justia fetch raises on one of them and
    succeeds on the other. Pass-2 runs once (on the surviving title);
    the failed title is recorded in title_fetch_failures with the error;
    parsed_urls contains only the surviving title's pass-2 output."""
    from scoring.api_retrieval_agent import discover_urls_for_pair_two_pass

    def responder(state: str, vintage: int, pass_marker: str) -> str:
        if pass_marker == "PASS_1":
            return _pass1_payload(
                [
                    (WY_TITLE1_URL, "Title 1 maybe."),
                    (WY_TITLE28_URL, "Title 28 definitely."),
                ]
            )
        return _pass2_payload([(WY_CHAPTER7_URL, "core_chapter", "Ch. 7")])

    anthropic_client = FakeAsyncClient(responder)
    justia_client = FakeJustiaClient(
        html_map={
            WY_STATE_INDEX_URL: WY_STATE_INDEX_HTML,
            WY_TITLE28_URL: WY_TITLE28_PAGE_HTML,
        },
        error_map={WY_TITLE1_URL: RuntimeError("simulated outage on Title 1")},
    )

    result = await discover_urls_for_pair_two_pass(
        anthropic_client,
        justia_client,
        state="WY",
        vintage=2010,
        slug="wyoming",
        pass1_template=MINIMAL_PASS1_TEMPLATE,
        pass2_template=MINIMAL_PASS2_TEMPLATE,
    )

    # Failed title is recorded with its error.
    failures = result.title_fetch_failures
    assert len(failures) == 1, f"Expected 1 failure, got {failures}"
    assert failures[0]["url"] == WY_TITLE1_URL
    assert "simulated outage" in failures[0]["error"]

    # Pass-2 ran exactly once (for the surviving Title 28).
    pass2_calls = [c for c in anthropic_client.calls
                   if "PASS_2" in c["messages"][0]["content"]]
    assert len(pass2_calls) == 1

    # parsed_urls contains only Title 28's chapter URL.
    assert [u.url for u in result.parsed_urls] == [WY_CHAPTER7_URL]


# ===========================================================================
# Test 6 — _parse_pass1_response unit test (markdown fences + violations)
# ===========================================================================


def test_pass1_response_schema_records_chosen_titles() -> None:
    """`_parse_pass1_response` returns (chosen_titles, availability, schema_violations).
    Tolerates ```json``` fences identically to `_parse_response_text`; rejects
    non-Justia URLs to the violations list with a reason."""
    from scoring.api_retrieval_agent import _parse_pass1_response

    bad_url = "https://en.wikipedia.org/wiki/X"
    raw_json = json.dumps(
        {
            "chosen_titles": [
                {"url": WY_TITLE28_URL, "rationale": "real title"},
                {"url": bad_url, "rationale": "non-Justia"},
            ],
            "justia_unavailable": False,
            "alternative_year": None,
            "notes": "ok",
        }
    )

    # Variant 1: ```json fenced
    fenced = f"```json\n{raw_json}\n```"
    chosen, avail, violations = _parse_pass1_response(fenced)
    assert [c.url for c in chosen] == [WY_TITLE28_URL]
    assert chosen[0].rationale == "real title"
    assert avail["justia_unavailable"] is False
    assert any(v.get("url") == bad_url for v in violations)

    # Variant 2: raw JSON (no fence) parses identically
    chosen2, avail2, violations2 = _parse_pass1_response(raw_json)
    assert [c.url for c in chosen2] == [WY_TITLE28_URL]
    assert any(v.get("url") == bad_url for v in violations2)

    # Variant 3: leading preamble + fence
    with_preamble = f"Sure:\n```json\n{raw_json}\n```"
    chosen3, _avail3, _violations3 = _parse_pass1_response(with_preamble)
    assert [c.url for c in chosen3] == [WY_TITLE28_URL]


# ===========================================================================
# Test 7 — per-pair checkpoint round-trips both passes
# ===========================================================================


@pytest.mark.asyncio
async def test_two_pass_pair_checkpoint_records_both_passes(tmp_path: Path) -> None:
    """Serialize the Pass1Pass2Result to a per-pair checkpoint JSON;
    deserialize; assert all fields round-trip — pass1_prompt, pass1_response,
    pass2_prompts (list with per-title {url, prompt, response}), chosen_titles,
    parsed_urls, pass1_availability, pass1_schema_violations,
    title_fetch_failures."""
    from scoring.api_retrieval_agent import (
        discover_urls_for_pair_two_pass,
        serialize_pass1_pass2_result,
        deserialize_pass1_pass2_result,
    )

    def responder(state: str, vintage: int, pass_marker: str) -> str:
        if pass_marker == "PASS_1":
            return _pass1_payload([(WY_TITLE28_URL, "Title 28.")])
        return _pass2_payload([(WY_CHAPTER7_URL, "core_chapter", "Ch. 7")])

    anthropic_client = FakeAsyncClient(responder)
    justia_client = FakeJustiaClient(
        html_map={
            WY_STATE_INDEX_URL: WY_STATE_INDEX_HTML,
            WY_TITLE28_URL: WY_TITLE28_PAGE_HTML,
        }
    )

    result = await discover_urls_for_pair_two_pass(
        anthropic_client,
        justia_client,
        state="WY",
        vintage=2010,
        slug="wyoming",
        pass1_template=MINIMAL_PASS1_TEMPLATE,
        pass2_template=MINIMAL_PASS2_TEMPLATE,
    )

    # Serialize → write → read → deserialize.
    checkpoint_path = tmp_path / "WY" / "2010" / "discovered_urls.json"
    checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
    checkpoint_path.write_text(
        json.dumps(serialize_pass1_pass2_result(result), indent=2),
        encoding="utf-8",
    )

    on_disk = json.loads(checkpoint_path.read_text(encoding="utf-8"))

    # Required fields exist and are non-empty where expected.
    assert "STATE: WY" in on_disk["pass1_prompt"]
    assert "PASS_1" in on_disk["pass1_prompt"]
    assert WY_TITLE28_URL in on_disk["pass1_response"]
    assert len(on_disk["pass2_prompts"]) == 1
    p2 = on_disk["pass2_prompts"][0]
    assert p2["url"] == WY_TITLE28_URL
    assert "PASS_2" in p2["prompt"]
    assert WY_CHAPTER7_URL in p2["response"]
    assert on_disk["chosen_titles"][0]["url"] == WY_TITLE28_URL
    assert on_disk["parsed_urls"][0]["url"] == WY_CHAPTER7_URL
    assert on_disk["pass1_availability"]["justia_unavailable"] is False
    assert on_disk["pass1_schema_violations"] == []
    assert on_disk["title_fetch_failures"] == []

    # Round-trip back to a Pass1Pass2Result and compare structurally.
    rehydrated = deserialize_pass1_pass2_result(on_disk)
    assert [u.url for u in rehydrated.parsed_urls] == [WY_CHAPTER7_URL]
    assert [c.url for c in rehydrated.chosen_titles] == [WY_TITLE28_URL]
    assert rehydrated.pass1_availability == result.pass1_availability
