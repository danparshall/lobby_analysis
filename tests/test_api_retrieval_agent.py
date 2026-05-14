"""Tests for src/scoring/api_retrieval_agent.py.

Phase 0–1 of the api-multi-vintage-retrieval plan (tests 1–6): single-pair
discovery, fan-out concurrency cap, per-pair checkpoint, resume from
checkpoint, batch-level failure isolation, Justia-hostname schema enforcement.

All tests use a duck-typed fake stand-in for `anthropic.AsyncAnthropic` so
no network or API key is required. The fake mimics the `client.messages.create`
boundary exactly — anything past that boundary is real code.
"""

from __future__ import annotations

import asyncio
import json
import time
from pathlib import Path
from types import SimpleNamespace

import pytest


# ---------------------------------------------------------------------------
# Fake anthropic client
# ---------------------------------------------------------------------------


def _fake_message(text: str) -> SimpleNamespace:
    """Build a duck-typed Message response object."""
    return SimpleNamespace(
        content=[SimpleNamespace(type="text", text=text)],
        usage=SimpleNamespace(input_tokens=100, output_tokens=50),
        model="claude-sonnet-4-6",
        role="assistant",
        stop_reason="end_turn",
    )


def _urls_payload(*entries: dict) -> str:
    """Wrap entries in the schema the agent expects from the LLM."""
    return json.dumps({"urls": list(entries)})


class FakeAsyncClient:
    """Duck-typed stand-in for `anthropic.AsyncAnthropic`.

    The agent code under test calls ``client.messages.create(...)``. This
    fake exposes that surface and routes each call through ``responder``,
    a callable the test supplies that takes the (state, vintage) extracted
    from the outgoing prompt and returns either the response text or
    raises an exception.

    Concurrency is recorded on every call so Test 2 can assert the cap.
    """

    def __init__(self, responder) -> None:
        self.responder = responder
        self.calls: list[dict] = []
        self.in_flight = 0
        self.peak_in_flight = 0
        self._lock = asyncio.Lock()
        # client.messages.create dispatches to this same object's `create`
        self.messages = self

    async def create(self, **kwargs):
        async with self._lock:
            self.in_flight += 1
            self.peak_in_flight = max(self.peak_in_flight, self.in_flight)
        try:
            self.calls.append(kwargs)
            pair = _pair_from_prompt(kwargs["messages"][0]["content"])
            result = self.responder(pair)
            # Allow the responder to either return a string or raise
            if isinstance(result, BaseException):
                raise result
            # Tiny await to let other coroutines run — exposes concurrency-cap
            # violations in Test 2 even on fast hardware.
            await asyncio.sleep(0.02)
            return _fake_message(result)
        finally:
            async with self._lock:
                self.in_flight -= 1


def _pair_from_prompt(prompt_text: str) -> tuple[str, int]:
    """Extract (state, vintage) from the prompt.

    Contract: the agent's prompt formatter MUST include lines
    ``STATE: <abbr>`` and ``VINTAGE: <year>`` so the LLM (and this fake)
    can identify the target pair. This is a behaviour requirement, not
    an implementation detail — without it, the LLM has no idea what
    pair to research.
    """
    state: str | None = None
    vintage: int | None = None
    for line in prompt_text.splitlines():
        stripped = line.strip()
        if stripped.startswith("STATE:"):
            state = stripped.split(":", 1)[1].strip()
        elif stripped.startswith("VINTAGE:"):
            vintage = int(stripped.split(":", 1)[1].strip())
    assert state is not None and vintage is not None, (
        f"Prompt did not contain STATE/VINTAGE markers: {prompt_text!r}"
    )
    return state, vintage


# A minimal prompt template the agent can substitute into. Tests pass
# this as `prompt_template`; the real seed-discovery prompt is written
# in Phase 4 and lives at `src/scoring/api_seed_discovery_prompt.md`.
MINIMAL_TEMPLATE = (
    "You are a legal-research agent. Discover Justia URLs for the "
    "lobbying-disclosure statutes of this state and vintage.\n"
    "STATE: {state}\n"
    "VINTAGE: {vintage}\n"
    'Respond with JSON: {{"urls": [{{"url": "...", "role": "core_chapter|support_chapter", "rationale": "..."}}]}}\n'
)


# ---------------------------------------------------------------------------
# Test 1 — single-pair discovery returns the expected URL list
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_discover_urls_for_pair_returns_proposed_urls() -> None:
    """The function returns ProposedURL objects whose URLs match the LLM payload."""
    from scoring.api_retrieval_agent import discover_urls_for_pair

    expected_urls = [
        "https://law.justia.com/codes/california/2015/gov/86100-86118.html",
        "https://law.justia.com/codes/california/2015/gov/86201-86206.html",
    ]
    payload = _urls_payload(
        {"url": expected_urls[0], "role": "core_chapter",
         "rationale": "Article 1: definitions and registration."},
        {"url": expected_urls[1], "role": "core_chapter",
         "rationale": "Article 2: prohibitions and reports."},
    )
    client = FakeAsyncClient(responder=lambda pair: payload)

    result = await discover_urls_for_pair(
        client,
        state="CA",
        vintage=2015,
        prompt_template=MINIMAL_TEMPLATE,
    )

    assert [r.url for r in result] == expected_urls
    # And the role/rationale survive the round-trip.
    assert result[0].role == "core_chapter"
    assert "Article 1" in result[0].rationale


# ---------------------------------------------------------------------------
# Test 2 — fan-out respects max_concurrent cap
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_discover_urls_for_pairs_respects_max_concurrent(tmp_path: Path) -> None:
    """With 20 pairs and max_concurrent=4, peak in-flight calls is ≤ 4."""
    from scoring.api_retrieval_agent import discover_urls_for_pairs

    pairs = [(s, v) for s in ["CA", "TX", "NY", "WI", "WY", "OH", "CO", "FL", "AZ", "OR"]
             for v in [2015, 2010]]
    assert len(pairs) == 20

    # Empty-URL response is fine — this test is about concurrency, not parsing.
    client = FakeAsyncClient(responder=lambda pair: _urls_payload())

    results = await discover_urls_for_pairs(
        client,
        pairs=pairs,
        max_concurrent=4,
        checkpoint_root=tmp_path,
        prompt_template=MINIMAL_TEMPLATE,
    )

    assert client.peak_in_flight <= 4, (
        f"peak in-flight was {client.peak_in_flight}, expected ≤ 4"
    )
    # All 20 pairs accounted for in the returned mapping.
    assert set(results.keys()) == set(pairs)


# ---------------------------------------------------------------------------
# Test 3 — checkpoint is written per pair with full prompt + response
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_checkpoint_records_prompt_response_and_timestamp(tmp_path: Path) -> None:
    """Per-pair checkpoint contains exact prompt, model, response text,
    retrieved_at timestamp, and parsed URL list — full reproducibility."""
    from scoring.api_retrieval_agent import discover_urls_for_pairs

    url = "https://law.justia.com/codes/california/2015/gov/86100-86118.html"
    payload = _urls_payload(
        {"url": url, "role": "core_chapter", "rationale": "Art 1."},
    )
    client = FakeAsyncClient(responder=lambda pair: payload)

    started_at = time.time()
    await discover_urls_for_pairs(
        client,
        pairs=[("CA", 2015)],
        max_concurrent=1,
        checkpoint_root=tmp_path,
        prompt_template=MINIMAL_TEMPLATE,
        model="claude-sonnet-4-6",
    )
    finished_at = time.time()

    checkpoint_path = tmp_path / "CA" / "2015" / "discovered_urls.json"
    assert checkpoint_path.exists()
    data = json.loads(checkpoint_path.read_text(encoding="utf-8"))

    # Prompt: exact text sent to the API (state + vintage substituted in).
    assert "STATE: CA" in data["prompt"]
    assert "VINTAGE: 2015" in data["prompt"]
    # Model: the model parameter we asked for.
    assert data["model"] == "claude-sonnet-4-6"
    # Response: the raw response text (so we can reparse if schema changes).
    assert url in data["response"]
    # Timestamp: ISO-8601 or epoch; either way, parseable + in the right window.
    retrieved_at_iso = data["retrieved_at"]
    # Permissive parse — accept ISO-8601.
    from datetime import datetime
    ts = datetime.fromisoformat(retrieved_at_iso.replace("Z", "+00:00"))
    assert started_at - 1 <= ts.timestamp() <= finished_at + 1
    # Parsed URLs: the structured list, ready for downstream consumption.
    assert data["parsed_urls"][0]["url"] == url


# ---------------------------------------------------------------------------
# Test 4 — resume skips pairs that already have a checkpoint
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_resume_skips_existing_checkpoint(tmp_path: Path) -> None:
    """A pre-existing checkpoint must not be re-queried; the API call count is
    exactly one (for the un-checkpointed pair), and the loaded checkpoint is
    returned unchanged."""
    from scoring.api_retrieval_agent import discover_urls_for_pairs

    # Pre-seed CA checkpoint with a sentinel payload.
    sentinel_url = "https://law.justia.com/codes/california/2015/MARKER.html"
    ca_dir = tmp_path / "CA" / "2015"
    ca_dir.mkdir(parents=True)
    sentinel_checkpoint = {
        "prompt": "MARKER_PROMPT",
        "model": "claude-sonnet-4-6",
        "response": '{"urls": [{"url": "' + sentinel_url + '", "role": "core_chapter", "rationale": "marker"}]}',
        "retrieved_at": "2026-05-13T12:00:00+00:00",
        "parsed_urls": [
            {"url": sentinel_url, "role": "core_chapter", "rationale": "marker"},
        ],
    }
    (ca_dir / "discovered_urls.json").write_text(
        json.dumps(sentinel_checkpoint), encoding="utf-8"
    )

    # Fake responds to TX with a fresh payload; raises if asked for CA.
    tx_url = "https://law.justia.com/codes/texas/2015/government-code/chapter-305/"
    def responder(pair):
        state, _ = pair
        if state == "CA":
            return RuntimeError("CA should have been loaded from checkpoint, not re-fetched")
        return _urls_payload(
            {"url": tx_url, "role": "core_chapter", "rationale": "Ch 305."},
        )
    client = FakeAsyncClient(responder=responder)

    results = await discover_urls_for_pairs(
        client,
        pairs=[("CA", 2015), ("TX", 2015)],
        max_concurrent=2,
        checkpoint_root=tmp_path,
        prompt_template=MINIMAL_TEMPLATE,
    )

    assert len(client.calls) == 1, (
        f"Expected exactly one API call (for TX), got {len(client.calls)}"
    )
    # The one call must be for TX, not CA.
    only_call_prompt = client.calls[0]["messages"][0]["content"]
    assert "STATE: TX" in only_call_prompt

    # CA checkpoint on disk is untouched.
    on_disk = json.loads((ca_dir / "discovered_urls.json").read_text(encoding="utf-8"))
    assert on_disk == sentinel_checkpoint

    # The returned mapping covers both pairs, with CA loaded from disk.
    assert set(results.keys()) == {("CA", 2015), ("TX", 2015)}
    assert results[("CA", 2015)][0].url == sentinel_url
    assert results[("TX", 2015)][0].url == tx_url


# ---------------------------------------------------------------------------
# Test 5 — API failure for one pair produces failures.jsonl, does not crash batch
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_batch_isolates_per_pair_api_failure(tmp_path: Path) -> None:
    """One pair's exception must not crash the batch; it's logged to
    failures.jsonl, and the other pairs complete normally."""
    from scoring.api_retrieval_agent import discover_urls_for_pairs

    ca_url = "https://law.justia.com/codes/california/2015/gov/86100-86118.html"
    tx_url = "https://law.justia.com/codes/texas/2015/government-code/chapter-305/"

    def responder(pair):
        state, _ = pair
        if state == "WY":
            return RuntimeError("simulated API failure for WY")
        if state == "CA":
            return _urls_payload({"url": ca_url, "role": "core_chapter", "rationale": ""})
        if state == "TX":
            return _urls_payload({"url": tx_url, "role": "core_chapter", "rationale": ""})
        raise AssertionError(f"unexpected pair {pair}")

    client = FakeAsyncClient(responder=responder)

    # Must not raise.
    results = await discover_urls_for_pairs(
        client,
        pairs=[("CA", 2015), ("WY", 2015), ("TX", 2015)],
        max_concurrent=2,
        checkpoint_root=tmp_path,
        prompt_template=MINIMAL_TEMPLATE,
    )

    # CA + TX got checkpoints; WY did not.
    assert (tmp_path / "CA" / "2015" / "discovered_urls.json").exists()
    assert (tmp_path / "TX" / "2015" / "discovered_urls.json").exists()
    assert not (tmp_path / "WY" / "2015" / "discovered_urls.json").exists()

    # failures.jsonl has exactly one entry, naming WY.
    failures_path = tmp_path / "failures.jsonl"
    assert failures_path.exists()
    failure_lines = [line for line in failures_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert len(failure_lines) == 1
    failure = json.loads(failure_lines[0])
    assert failure["state"] == "WY"
    assert failure["vintage"] == 2015
    assert "error" in failure and "WY" in failure["error"]

    # results contains the successes; WY is either absent or marked failed.
    assert ("CA", 2015) in results
    assert ("TX", 2015) in results
    assert results[("CA", 2015)][0].url == ca_url
    assert results[("TX", 2015)][0].url == tx_url
    # WY is either missing from results, or present with an empty list — both are
    # acceptable; what matters is the batch didn't crash and WY is recorded as failed.
    assert ("WY", 2015) not in results or results[("WY", 2015)] == []


# ---------------------------------------------------------------------------
# Test 6 — output schema rejects non-Justia hostnames
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_non_justia_hostnames_are_rejected(tmp_path: Path) -> None:
    """If the LLM proposes a non-Justia URL, the parser must drop it from the
    returned list. The bad URL is recorded in the checkpoint's schema_violations
    field so downstream code can see what was filtered."""
    from scoring.api_retrieval_agent import discover_urls_for_pairs

    good_url = "https://law.justia.com/codes/california/2015/gov/86100-86118.html"
    bad_url = "https://wikipedia.org/wiki/California_lobbying_law"

    payload = _urls_payload(
        {"url": good_url, "role": "core_chapter", "rationale": "real statute"},
        {"url": bad_url, "role": "core_chapter", "rationale": "hallucinated wiki link"},
    )
    client = FakeAsyncClient(responder=lambda pair: payload)

    results = await discover_urls_for_pairs(
        client,
        pairs=[("CA", 2015)],
        max_concurrent=1,
        checkpoint_root=tmp_path,
        prompt_template=MINIMAL_TEMPLATE,
    )

    # Returned list contains only the Justia URL.
    urls = [r.url for r in results[("CA", 2015)]]
    assert urls == [good_url], f"Expected only Justia URL, got {urls}"

    # Checkpoint records the dropped URL so it's auditable.
    checkpoint = json.loads(
        (tmp_path / "CA" / "2015" / "discovered_urls.json").read_text(encoding="utf-8")
    )
    violations = checkpoint.get("schema_violations", [])
    assert any(v.get("url") == bad_url for v in violations), (
        f"schema_violations should record dropped {bad_url}, got {violations}"
    )


# ---------------------------------------------------------------------------
# Test 7 — parser tolerates ```json markdown fences
# ---------------------------------------------------------------------------


def test_parser_strips_markdown_fences() -> None:
    """Models sometimes wrap JSON in ```json fences despite the prompt asking
    for raw JSON. The parser must tolerate this rather than raising — fence
    discipline is hard for LLMs and shouldn't be a hard failure mode."""
    from scoring.api_retrieval_agent import _parse_response_text

    url = "https://law.justia.com/codes/california/2015/gov/86100-86118.html"
    raw_json = json.dumps({"urls": [
        {"url": url, "role": "core_chapter", "rationale": "Art 1."},
    ]})

    # Variant 1: ```json ... ``` (most common)
    fenced_json = f"```json\n{raw_json}\n```"
    parsed, _violations, _avail = _parse_response_text(fenced_json)
    assert [p.url for p in parsed] == [url], (
        f"fenced JSON should parse cleanly, got {parsed}"
    )

    # Variant 2: ``` (no language tag)
    fenced_bare = f"```\n{raw_json}\n```"
    parsed, _violations, _avail = _parse_response_text(fenced_bare)
    assert [p.url for p in parsed] == [url], "bare-fence JSON should parse cleanly"

    # Variant 3: leading prose + fenced JSON
    with_preamble = f"Sure, here's the JSON:\n```json\n{raw_json}\n```"
    parsed, _violations, _avail = _parse_response_text(with_preamble)
    assert [p.url for p in parsed] == [url], (
        "JSON with preamble + fence should parse cleanly"
    )


# ---------------------------------------------------------------------------
# Test 8 — parser surfaces justia_unavailable / alternative_year metadata
# ---------------------------------------------------------------------------


def test_parser_extracts_availability_metadata() -> None:
    """The parser must distinguish three cases:
      (a) urls present, justia_unavailable=false  → normal
      (b) urls present, alternative_year set      → year substitution
      (c) urls empty, justia_unavailable=true     → no Justia coverage at all
    Case (c) cannot be confused with a model that just returned [] because
    it had no answer — the metadata is the signal."""
    from scoring.api_retrieval_agent import _parse_response_text

    # Case (a): normal response, defaults
    raw_a = json.dumps({
        "urls": [{"url": "https://law.justia.com/codes/ca/2015/gov/86100-86118.html",
                  "role": "core_chapter", "rationale": "r"}],
    })
    _, _, avail_a = _parse_response_text(raw_a)
    assert avail_a["justia_unavailable"] is False
    assert avail_a["alternative_year"] is None

    # Case (b): year substitution
    raw_b = json.dumps({
        "urls": [{"url": "https://law.justia.com/codes/texas/2009/government-code/",
                  "role": "core_chapter", "rationale": "r"}],
        "alternative_year": 2009,
        "notes": "TX 2010 not on Justia",
    })
    _, _, avail_b = _parse_response_text(raw_b)
    assert avail_b["justia_unavailable"] is False
    assert avail_b["alternative_year"] == 2009
    assert "TX 2010" in avail_b["notes"]

    # Case (c): justia_unavailable true, empty url list
    raw_c = json.dumps({
        "urls": [],
        "justia_unavailable": True,
        "alternative_year": None,
        "notes": "Justia hosts no CO statutes before 2016.",
    })
    parsed_c, _, avail_c = _parse_response_text(raw_c)
    assert parsed_c == []
    assert avail_c["justia_unavailable"] is True
    assert "no CO statutes" in avail_c["notes"]


# ---------------------------------------------------------------------------
# Test 9 — batch writes availability.jsonl line when justia_unavailable=true
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_batch_records_unavailable_pairs_in_availability_log(tmp_path: Path) -> None:
    """When the model reports justia_unavailable=true, the batch must record
    this distinctly from successful empty-result calls. The mechanism: a
    line in `<root>/availability.jsonl` with state, vintage, alternative_year,
    notes, and a timestamp. The per-pair checkpoint is still written (so the
    full response is preserved per experiment-data-integrity)."""
    from scoring.api_retrieval_agent import discover_urls_for_pairs

    co_url = "https://law.justia.com/codes/colorado/2016/title-24/article-6/"

    def responder(pair):
        state, vintage = pair
        if state == "CO" and vintage == 2010:
            # CO pre-2016 has no Justia coverage.
            return json.dumps({
                "urls": [],
                "justia_unavailable": True,
                "alternative_year": None,
                "notes": "Justia hosts no CO statutes before 2016.",
            })
        if state == "CO" and vintage == 2016:
            return json.dumps({
                "urls": [{"url": co_url, "role": "core_chapter",
                          "rationale": "Title 24 Art 6 (Lobbyist Reg)."}],
                "justia_unavailable": False,
                "alternative_year": None,
                "notes": "",
            })
        raise AssertionError(f"unexpected pair {pair}")

    client = FakeAsyncClient(responder=responder)

    results = await discover_urls_for_pairs(
        client,
        pairs=[("CO", 2010), ("CO", 2016)],
        max_concurrent=2,
        checkpoint_root=tmp_path,
        prompt_template=MINIMAL_TEMPLATE,
    )

    # availability.jsonl exists with exactly one line — for CO 2010.
    availability_path = tmp_path / "availability.jsonl"
    assert availability_path.exists(), (
        "availability.jsonl must be written when any pair reports unavailable"
    )
    lines = [line for line in availability_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert len(lines) == 1, f"Expected 1 availability entry, got {len(lines)}: {lines}"
    entry = json.loads(lines[0])
    assert entry["state"] == "CO"
    assert entry["vintage"] == 2010
    assert entry["justia_unavailable"] is True
    assert "no CO statutes" in entry["notes"]
    assert "retrieved_at" in entry

    # The per-pair checkpoint for CO 2010 still exists and preserves the full response.
    co_2010_checkpoint = tmp_path / "CO" / "2010" / "discovered_urls.json"
    assert co_2010_checkpoint.exists(), (
        "checkpoint should still be written even for unavailable pairs"
    )
    cp = json.loads(co_2010_checkpoint.read_text(encoding="utf-8"))
    assert cp["parsed_urls"] == []
    assert "no CO statutes" in cp["response"]

    # CO 2016 was a normal success — no availability entry, normal checkpoint.
    assert results[("CO", 2016)][0].url == co_url
    co_2016_checkpoint = tmp_path / "CO" / "2016" / "discovered_urls.json"
    assert co_2016_checkpoint.exists()
