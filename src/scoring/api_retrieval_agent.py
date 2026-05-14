"""API-driven multi-vintage statute URL discovery.

Wraps `anthropic.AsyncAnthropic` for the narrow task of proposing Justia
URLs that cover a state's lobbying-disclosure statutes for a given
vintage year. Feeds the existing Playwright `retrieve-statutes` fetcher
once the proposed URLs pass HEAD verification.

Design notes:
- Checkpoint-per-pair under `<root>/<STATE>/<vintage>/discovered_urls.json`
  records the exact prompt, model, response text, timestamp, and parsed
  URLs. Re-runs are idempotent — existing checkpoints are loaded from
  disk and skipped at the SDK boundary.
- Batch-level `<root>/failures.jsonl` collects per-pair API errors so a
  failed pair doesn't sink the rest of the fan-out.
- Concurrency is bounded by an `asyncio.Semaphore`; the resume path
  runs outside the semaphore (no API call to cap).
- Non-Justia URLs in the model's response are dropped from the parsed
  list and recorded in the checkpoint's `schema_violations` field so
  downstream code (and humans) can see what was filtered.
"""

from __future__ import annotations

import asyncio
import json
import os
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Protocol
from urllib.parse import urlparse


JUSTIA_HOSTNAME = "law.justia.com"
JUSTIA_BASE = "https://law.justia.com"


class JustiaFetcher(Protocol):
    """Minimal duck-typed shape we need from a Justia HTTP client.

    Production: `scoring.justia_client.PlaywrightClient`. Tests: any object
    with `fetch_page(url) -> str`. Kept as a Protocol here so the agent
    module can be imported without pulling in `playwright`.
    """

    def fetch_page(self, url: str) -> str: ...


# Matches a fenced code block in a model response, optionally with a language
# tag (e.g. ```json). The capture group holds the inner JSON text.
_FENCED_JSON_RE = re.compile(
    r"```(?:json|JSON)?\s*\n?(.*?)\n?```",
    re.DOTALL,
)


def _default_availability() -> dict:
    """Shape returned when the LLM omits availability metadata."""
    return {
        "justia_unavailable": False,
        "alternative_year": None,
        "notes": "",
    }


class SchemaViolation(ValueError):
    """Raised when an LLM-proposed URL violates the agent's schema."""


@dataclass(frozen=True)
class ProposedURL:
    """A single statute URL proposed by the discovery agent."""

    url: str
    role: str
    rationale: str

    @classmethod
    def from_raw(cls, payload: dict) -> "ProposedURL":
        url = payload.get("url", "")
        host = (urlparse(url).hostname or "").lower()
        if host != JUSTIA_HOSTNAME:
            raise SchemaViolation(
                f"non-Justia hostname {host!r} in URL {url!r}"
            )
        return cls(
            url=url,
            role=payload.get("role", ""),
            rationale=payload.get("rationale", ""),
        )


def _format_prompt(
    state: str,
    vintage: int,
    template: str,
    *,
    state_index: str = "",
) -> str:
    """Fill `{state}`, `{vintage}`, and `{state_index}` placeholders.

    `state_index` is an optional live-snapshot of `https://law.justia.com/
    codes/<state-slug>/<year>/` to inline in the prompt. When the template
    does not reference `{state_index}`, the extra kwarg is silently ignored
    by `str.format` — backwards-compatible with index-free templates.
    """
    return template.format(
        state=state, vintage=vintage, state_index=state_index
    )


def _parse_response_text(
    text: str,
) -> tuple[list[ProposedURL], list[dict], dict]:
    """Extract `{"urls": [...]}` plus availability metadata from the LLM response.

    Returns `(parsed_urls, schema_violations, availability)`:
    - `parsed_urls`: list of `ProposedURL` objects whose hostname is Justia.
    - `schema_violations`: dicts of `{"url": ..., "reason": ...}` for entries
      the parser rejected (e.g., non-Justia hostnames).
    - `availability`: `{"justia_unavailable": bool, "alternative_year": int|None,
      "notes": str}` — the LLM's coverage signal. When the LLM omits these
      fields, the defaults from `_default_availability()` are used.

    Tolerant of markdown-fenced JSON (``` or ```json) and leading prose
    before the fence. Strict JSON without fences is also accepted.
    """
    fenced = _FENCED_JSON_RE.search(text)
    json_text = fenced.group(1) if fenced else text
    data = json.loads(json_text)

    raw_urls = data.get("urls", [])
    parsed: list[ProposedURL] = []
    violations: list[dict] = []
    for entry in raw_urls:
        try:
            parsed.append(ProposedURL.from_raw(entry))
        except SchemaViolation as e:
            violations.append({"url": entry.get("url", ""), "reason": str(e)})

    availability = _default_availability()
    if "justia_unavailable" in data:
        availability["justia_unavailable"] = bool(data["justia_unavailable"])
    if "alternative_year" in data:
        availability["alternative_year"] = data["alternative_year"]
    if "notes" in data:
        availability["notes"] = data["notes"] or ""

    return parsed, violations, availability


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


async def discover_urls_for_pair(
    client,
    *,
    state: str,
    vintage: int,
    prompt_template: str,
    state_index: str = "",
    model: str = "claude-sonnet-4-6",
    max_output_tokens: int = 4096,
) -> list[ProposedURL]:
    """Discover Justia URLs for a single (state, vintage) pair.

    `state_index`, if non-empty, is inlined into the prompt's
    `{state_index}` placeholder — a live snapshot of Justia's state-year
    index page for the pair, used to ground the model's URL casing and
    granularity choices.

    Returns the parsed `ProposedURL` list. Schema violations (non-Justia
    URLs) are silently dropped from the return value — callers that need
    to audit them should use `discover_urls_for_pairs`, which records
    them in the per-pair checkpoint.
    """
    prompt = _format_prompt(
        state, vintage, prompt_template, state_index=state_index
    )
    response = await client.messages.create(
        model=model,
        max_tokens=max_output_tokens,
        messages=[{"role": "user", "content": prompt}],
    )
    text = response.content[0].text
    parsed, _violations, _availability = _parse_response_text(text)
    return parsed


def _load_checkpoint(path: Path) -> list[ProposedURL]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return [
        ProposedURL(
            url=u["url"],
            role=u.get("role", ""),
            rationale=u.get("rationale", ""),
        )
        for u in data.get("parsed_urls", [])
    ]


async def discover_urls_for_pairs(
    client,
    *,
    pairs: Iterable[tuple[str, int]],
    max_concurrent: int = 8,
    checkpoint_root: Path,
    prompt_template: str,
    model: str = "claude-sonnet-4-6",
    max_output_tokens: int = 4096,
) -> dict[tuple[str, int], list[ProposedURL]]:
    """Discover Justia URLs for many pairs concurrently, with checkpoint resume.

    Each pair's result is written to
    `<checkpoint_root>/<STATE>/<vintage>/discovered_urls.json`. Pairs whose
    checkpoint already exists are loaded from disk and not re-queried.
    Per-pair API failures are appended to `<checkpoint_root>/failures.jsonl`
    and do not propagate.

    Returns a mapping `(state, vintage) -> list[ProposedURL]`. Failed pairs
    are absent from the mapping (see `failures.jsonl` for diagnostics).
    """
    checkpoint_root = Path(checkpoint_root)
    pairs = list(pairs)
    semaphore = asyncio.Semaphore(max_concurrent)
    failures_path = checkpoint_root / "failures.jsonl"
    availability_path = checkpoint_root / "availability.jsonl"
    failures_lock = asyncio.Lock()
    availability_lock = asyncio.Lock()
    results: dict[tuple[str, int], list[ProposedURL]] = {}

    async def process_pair(state: str, vintage: int) -> None:
        checkpoint_path = (
            checkpoint_root / state / str(vintage) / "discovered_urls.json"
        )
        if checkpoint_path.exists():
            results[(state, vintage)] = _load_checkpoint(checkpoint_path)
            return

        prompt = _format_prompt(state, vintage, prompt_template)
        async with semaphore:
            try:
                response = await client.messages.create(
                    model=model,
                    max_tokens=max_output_tokens,
                    messages=[{"role": "user", "content": prompt}],
                )
            except Exception as e:  # noqa: BLE001 — batch must not crash
                async with failures_lock:
                    failures_path.parent.mkdir(parents=True, exist_ok=True)
                    with failures_path.open("a", encoding="utf-8") as f:
                        f.write(
                            json.dumps(
                                {
                                    "state": state,
                                    "vintage": vintage,
                                    "error": f"{type(e).__name__}: {e}",
                                    "retrieved_at": _now_iso(),
                                }
                            )
                            + "\n"
                        )
                return

        text = response.content[0].text
        parsed, violations, availability = _parse_response_text(text)
        retrieved_at = _now_iso()

        checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
        checkpoint = {
            "prompt": prompt,
            "model": model,
            "response": text,
            "retrieved_at": retrieved_at,
            "parsed_urls": [
                {"url": p.url, "role": p.role, "rationale": p.rationale}
                for p in parsed
            ],
            "schema_violations": violations,
            "availability": availability,
        }
        checkpoint_path.write_text(
            json.dumps(checkpoint, indent=2), encoding="utf-8"
        )

        if availability["justia_unavailable"]:
            async with availability_lock:
                availability_path.parent.mkdir(parents=True, exist_ok=True)
                with availability_path.open("a", encoding="utf-8") as f:
                    f.write(
                        json.dumps(
                            {
                                "state": state,
                                "vintage": vintage,
                                "justia_unavailable": True,
                                "alternative_year": availability[
                                    "alternative_year"
                                ],
                                "notes": availability["notes"],
                                "retrieved_at": retrieved_at,
                            }
                        )
                        + "\n"
                    )

        results[(state, vintage)] = parsed

    await asyncio.gather(*(process_pair(s, v) for s, v in pairs))
    return results


# ===========================================================================
# B3 (two-pass discovery) — orchestrator, parser, helpers, batch
# ===========================================================================


@dataclass(frozen=True)
class ChosenTitle:
    """A title-level URL picked by pass-1 to anchor pass-2 fetch + proposal."""

    url: str
    rationale: str

    @classmethod
    def from_raw(cls, payload: dict) -> "ChosenTitle":
        url = payload.get("url", "")
        host = (urlparse(url).hostname or "").lower()
        if host != JUSTIA_HOSTNAME:
            raise SchemaViolation(
                f"non-Justia hostname {host!r} in URL {url!r}"
            )
        return cls(url=url, rationale=payload.get("rationale", ""))


@dataclass
class Pass1Pass2Result:
    """Output of `discover_urls_for_pair_two_pass`.

    Full bookkeeping for both passes — see the B3 plan's checkpoint-shape
    spec. Mutable so the orchestrator can populate fields incrementally.
    """

    state: str
    vintage: int
    slug: str
    pass1_prompt: str = ""
    pass1_response: str = ""
    pass1_availability: dict = field(default_factory=_default_availability)
    pass1_schema_violations: list[dict] = field(default_factory=list)
    chosen_titles: list[ChosenTitle] = field(default_factory=list)
    pass2_prompts: list[dict] = field(default_factory=list)
    title_fetch_failures: list[dict] = field(default_factory=list)
    parsed_urls: list[ProposedURL] = field(default_factory=list)


def _parse_pass1_response(
    text: str,
) -> tuple[list[ChosenTitle], dict, list[dict]]:
    """Parse a pass-1 ``chosen_titles[]`` response.

    Returns ``(chosen_titles, availability, schema_violations)``. Tolerates
    markdown-fenced JSON (identically to ``_parse_response_text``); rejects
    non-Justia URLs to the violations list with a reason.
    """
    fenced = _FENCED_JSON_RE.search(text)
    json_text = fenced.group(1) if fenced else text
    data = json.loads(json_text)

    raw_titles = data.get("chosen_titles", [])
    chosen: list[ChosenTitle] = []
    violations: list[dict] = []
    for entry in raw_titles:
        try:
            chosen.append(ChosenTitle.from_raw(entry))
        except SchemaViolation as e:
            violations.append({"url": entry.get("url", ""), "reason": str(e)})

    availability = _default_availability()
    if "justia_unavailable" in data:
        availability["justia_unavailable"] = bool(data["justia_unavailable"])
    if "alternative_year" in data:
        availability["alternative_year"] = data["alternative_year"]
    if "notes" in data:
        availability["notes"] = data["notes"] or ""

    return chosen, availability, violations


def _build_justia_link_tsv(html: str, parent_url: str) -> str:
    """Build a ``<absolute-url>\\t<anchor-text>`` link list for prompt inlining.

    Used by both passes to give the LLM a snapshot of Justia's exposed
    children from the parent page. Filters to one-segment-deeper URLs in
    the parent's namespace; deduplicates on URL, first-seen anchor wins.

    Handles three Justia parent-page patterns:
    1. Directory parent (``/codes/wyoming/2010/``) — children are immediate
       descendants in that path.
    2. ``Foo/Foo.html`` parent (``/Title28/Title28.html``) — children are
       siblings inside the matching ``Foo/`` directory.
    3. ``foo.html`` parent (``/gov.html``) — children are entries in the
       matching ``foo/`` subdirectory.

    Anchor text is the link's stripped text content; may be empty (trailing
    tab preserved). HTML parsing uses BeautifulSoup, the same library
    ``justia_client.parse_children_list`` uses.
    """
    from bs4 import BeautifulSoup

    parent_path = urlparse(parent_url).path
    parent_canon = parent_path.rstrip("/")

    if parent_path.endswith("/"):
        # Pattern 1: directory parent.
        namespace = parent_canon + "/"
    elif parent_canon.endswith(".html"):
        last_slash = parent_canon.rfind("/")
        directory = parent_canon[: last_slash + 1]
        filename = parent_canon[last_slash + 1:]
        basename = filename[: -len(".html")]
        dir_segments = [s for s in directory.strip("/").split("/") if s]
        if dir_segments and dir_segments[-1] == basename:
            # Pattern 2: Foo/Foo.html — children are siblings in Foo/.
            namespace = directory
        else:
            # Pattern 3: gov.html — children are in gov/.
            namespace = directory + basename + "/"
    else:
        namespace = parent_canon + "/"

    soup = BeautifulSoup(html, "html.parser")
    seen: set[str] = set()
    entries: list[tuple[str, str]] = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href.startswith("/"):
            url_path = href
            url = JUSTIA_BASE + href
        elif href.startswith(JUSTIA_BASE):
            url = href
            url_path = href[len(JUSTIA_BASE):]
        else:
            continue
        if "accounts.justia.com" in url:
            continue
        if url_path == parent_canon or url_path == parent_canon + "/":
            continue
        if not url_path.startswith(namespace):
            continue
        # One segment deeper only — tail (after stripping any trailing /)
        # must not contain a further /.
        tail = url_path[len(namespace):].rstrip("/")
        if not tail or "/" in tail:
            continue
        if url in seen:
            continue
        seen.add(url)
        anchor = a.get_text(strip=True)
        entries.append((url, anchor))
    return "\n".join(f"{url}\t{anchor}" for url, anchor in entries)


async def _fetch_via_client(client: JustiaFetcher, url: str) -> str:
    """Async/sync bridge for a Justia ``Client``.

    ``PlaywrightClient.fetch_page`` is synchronous (it spins a fresh
    browser per call). Wrapping in ``asyncio.to_thread`` lets the
    orchestrator stay async and run multiple pairs concurrently in the
    batch surface. The thread-offload is effectively a no-op for the
    fast ``FakeJustiaClient`` used in tests.
    """
    return await asyncio.to_thread(client.fetch_page, url)


# --- cost tracking (used by canaries against real Anthropic) ---------------


class CostCapExceeded(RuntimeError):
    """Raised when cumulative LLM cost would exceed the configured cap."""


class CostTracker:
    """Cumulative token-cost guard with a hard USD cap.

    Per-call pricing assumes Sonnet 4-tier ($3/M input, $15/M output) and
    does NOT account for prompt-cache discount — i.e., the reported cost
    is an upper bound, so the cap behaviour is conservative.

    Update INPUT_USD_PER_M / OUTPUT_USD_PER_M if pricing changes.
    """

    INPUT_USD_PER_M = 3.0
    OUTPUT_USD_PER_M = 15.0

    def __init__(self, *, cap_usd: float | None = None) -> None:
        self.cap_usd = cap_usd
        self.input_tokens = 0
        self.output_tokens = 0
        self._lock = asyncio.Lock()

    @property
    def cost_usd(self) -> float:
        return (
            self.input_tokens * self.INPUT_USD_PER_M / 1_000_000
            + self.output_tokens * self.OUTPUT_USD_PER_M / 1_000_000
        )

    async def record(self, input_tokens: int, output_tokens: int) -> None:
        async with self._lock:
            self.input_tokens += input_tokens
            self.output_tokens += output_tokens
            if self.cap_usd is not None and self.cost_usd > self.cap_usd:
                raise CostCapExceeded(
                    f"cumulative cost ${self.cost_usd:.4f} exceeds cap "
                    f"${self.cap_usd:.4f} after "
                    f"{self.input_tokens} in / {self.output_tokens} out tokens"
                )


async def _record_usage_if_present(
    cost_tracker: CostTracker | None, response
) -> None:
    """Best-effort usage extraction; tolerates missing fields on the response."""
    if cost_tracker is None:
        return
    usage = getattr(response, "usage", None)
    if usage is None:
        return
    input_tokens = int(getattr(usage, "input_tokens", 0) or 0)
    output_tokens = int(getattr(usage, "output_tokens", 0) or 0)
    await cost_tracker.record(input_tokens, output_tokens)


# --- orchestrator ----------------------------------------------------------


def _state_year_url(slug: str, vintage: int) -> str:
    return f"{JUSTIA_BASE}/codes/{slug}/{vintage}/"


def _escape_braces(text: str) -> str:
    """Defensive: stop ``str.format`` choking on stray ``{`` / ``}`` in
    the chosen_title_rationale or any other LLM-emitted free text.
    """
    return text.replace("{", "{{").replace("}", "}}")


async def discover_urls_for_pair_two_pass(
    anthropic_client,
    justia_client: JustiaFetcher,
    *,
    state: str,
    vintage: int,
    slug: str,
    pass1_template: str,
    pass2_template: str,
    model: str = "claude-sonnet-4-6",
    max_output_tokens: int = 4096,
    cost_tracker: CostTracker | None = None,
) -> Pass1Pass2Result:
    """Two-pass Justia URL discovery for a single (state, vintage) pair.

    Pass 1: fetch state-year index, prompt LLM to pick the lobbying title(s).
    Pass 2: fetch each chosen title page, prompt LLM to propose statute URLs.
    Returns a `Pass1Pass2Result` capturing every prompt, response, parsed
    list, and failure mode encountered along the way.
    """
    result = Pass1Pass2Result(state=state, vintage=vintage, slug=slug)

    # --- Pass 1 ------------------------------------------------------------
    state_year_url = _state_year_url(slug, vintage)
    state_year_html = await _fetch_via_client(justia_client, state_year_url)
    state_year_tsv = _build_justia_link_tsv(state_year_html, state_year_url)

    pass1_prompt = pass1_template.format(
        state=state, vintage=vintage, state_index=state_year_tsv
    )
    result.pass1_prompt = pass1_prompt

    pass1_response = await anthropic_client.messages.create(
        model=model,
        max_tokens=max_output_tokens,
        messages=[{"role": "user", "content": pass1_prompt}],
    )
    await _record_usage_if_present(cost_tracker, pass1_response)
    pass1_text = pass1_response.content[0].text
    result.pass1_response = pass1_text

    chosen, availability, violations = _parse_pass1_response(pass1_text)
    result.pass1_availability = availability
    result.pass1_schema_violations = violations
    result.chosen_titles = chosen

    if availability.get("justia_unavailable") or not chosen:
        return result

    # --- Pass 2 (per chosen title) ----------------------------------------
    for title in chosen:
        try:
            title_html = await _fetch_via_client(justia_client, title.url)
        except Exception as e:  # noqa: BLE001 — log and continue per plan
            result.title_fetch_failures.append(
                {
                    "url": title.url,
                    "error": f"{type(e).__name__}: {e}",
                    "retrieved_at": _now_iso(),
                }
            )
            continue

        title_tsv = _build_justia_link_tsv(title_html, title.url)
        pass2_prompt = pass2_template.format(
            state=state,
            vintage=vintage,
            state_index=title_tsv,
            chosen_title_rationale=_escape_braces(title.rationale),
        )
        pass2_response = await anthropic_client.messages.create(
            model=model,
            max_tokens=max_output_tokens,
            messages=[{"role": "user", "content": pass2_prompt}],
        )
        await _record_usage_if_present(cost_tracker, pass2_response)
        pass2_text = pass2_response.content[0].text

        result.pass2_prompts.append(
            {"url": title.url, "prompt": pass2_prompt, "response": pass2_text}
        )

        parsed, _vio, _avail = _parse_response_text(pass2_text)
        # Dedup on (url, role) across titles.
        seen_pairs = {(u.url, u.role) for u in result.parsed_urls}
        for p in parsed:
            key = (p.url, p.role)
            if key in seen_pairs:
                continue
            seen_pairs.add(key)
            result.parsed_urls.append(p)

    return result


# --- checkpoint serialization ---------------------------------------------


def serialize_pass1_pass2_result(result: Pass1Pass2Result) -> dict:
    """Convert a `Pass1Pass2Result` to a JSON-serializable dict.

    Shape mirrors the per-pair checkpoint format documented in the B3 plan.
    """
    return {
        "state": result.state,
        "vintage": result.vintage,
        "slug": result.slug,
        "pass1_prompt": result.pass1_prompt,
        "pass1_response": result.pass1_response,
        "pass1_availability": result.pass1_availability,
        "pass1_schema_violations": result.pass1_schema_violations,
        "chosen_titles": [
            {"url": t.url, "rationale": t.rationale} for t in result.chosen_titles
        ],
        "pass2_prompts": result.pass2_prompts,
        "title_fetch_failures": result.title_fetch_failures,
        "parsed_urls": [
            {"url": u.url, "role": u.role, "rationale": u.rationale}
            for u in result.parsed_urls
        ],
    }


def deserialize_pass1_pass2_result(data: dict) -> Pass1Pass2Result:
    """Rehydrate a `Pass1Pass2Result` from `serialize_pass1_pass2_result`'s output."""
    return Pass1Pass2Result(
        state=data["state"],
        vintage=data["vintage"],
        slug=data["slug"],
        pass1_prompt=data.get("pass1_prompt", ""),
        pass1_response=data.get("pass1_response", ""),
        pass1_availability=data.get("pass1_availability") or _default_availability(),
        pass1_schema_violations=list(data.get("pass1_schema_violations") or []),
        chosen_titles=[
            ChosenTitle(url=t["url"], rationale=t.get("rationale", ""))
            for t in data.get("chosen_titles", [])
        ],
        pass2_prompts=list(data.get("pass2_prompts") or []),
        title_fetch_failures=list(data.get("title_fetch_failures") or []),
        parsed_urls=[
            ProposedURL(
                url=u["url"],
                role=u.get("role", ""),
                rationale=u.get("rationale", ""),
            )
            for u in data.get("parsed_urls", [])
        ],
    )


# --- batch orchestrator ---------------------------------------------------


async def discover_urls_for_pairs_two_pass(
    anthropic_client,
    justia_client: JustiaFetcher,
    *,
    pairs: Iterable[tuple[str, int, str]],
    pass1_template: str,
    pass2_template: str,
    checkpoint_root: Path,
    max_concurrent: int = 4,
    model: str = "claude-sonnet-4-6",
    max_output_tokens: int = 4096,
    cost_tracker: CostTracker | None = None,
) -> dict[tuple[str, int], Pass1Pass2Result]:
    """Concurrent two-pass discovery across many (state, vintage, slug) triples.

    Resume semantics identical to ``discover_urls_for_pairs``: pairs with an
    existing ``<checkpoint_root>/<STATE>/<vintage>/discovered_urls.json``
    are loaded from disk and skipped at both the Anthropic and Justia
    boundaries. Per-pair API/fetch failures land in
    ``<checkpoint_root>/failures.jsonl``; ``justia_unavailable=true`` pairs
    additionally append a row to ``<checkpoint_root>/availability.jsonl``.

    The default concurrency cap is 4 — lower than B2's 8 because Playwright
    is heavier than httpx and we want to be conservative under Justia's
    anti-bot fingerprinting at sustained pressure.
    """
    checkpoint_root = Path(checkpoint_root)
    triples = list(pairs)
    semaphore = asyncio.Semaphore(max_concurrent)
    failures_path = checkpoint_root / "failures.jsonl"
    availability_path = checkpoint_root / "availability.jsonl"
    failures_lock = asyncio.Lock()
    availability_lock = asyncio.Lock()
    results: dict[tuple[str, int], Pass1Pass2Result] = {}

    async def process(state: str, vintage: int, slug: str) -> None:
        checkpoint_path = (
            checkpoint_root / state / str(vintage) / "discovered_urls.json"
        )
        if checkpoint_path.exists():
            data = json.loads(checkpoint_path.read_text(encoding="utf-8"))
            results[(state, vintage)] = deserialize_pass1_pass2_result(data)
            return

        async with semaphore:
            try:
                result = await discover_urls_for_pair_two_pass(
                    anthropic_client,
                    justia_client,
                    state=state,
                    vintage=vintage,
                    slug=slug,
                    pass1_template=pass1_template,
                    pass2_template=pass2_template,
                    model=model,
                    max_output_tokens=max_output_tokens,
                    cost_tracker=cost_tracker,
                )
            except CostCapExceeded:
                # Bubble out — the whole batch is cost-capped.
                raise
            except Exception as e:  # noqa: BLE001
                async with failures_lock:
                    failures_path.parent.mkdir(parents=True, exist_ok=True)
                    with failures_path.open("a", encoding="utf-8") as f:
                        f.write(
                            json.dumps(
                                {
                                    "state": state,
                                    "vintage": vintage,
                                    "slug": slug,
                                    "error": f"{type(e).__name__}: {e}",
                                    "retrieved_at": _now_iso(),
                                }
                            )
                            + "\n"
                        )
                return

        checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
        checkpoint_path.write_text(
            json.dumps(serialize_pass1_pass2_result(result), indent=2),
            encoding="utf-8",
        )

        if result.pass1_availability.get("justia_unavailable"):
            async with availability_lock:
                availability_path.parent.mkdir(parents=True, exist_ok=True)
                with availability_path.open("a", encoding="utf-8") as f:
                    f.write(
                        json.dumps(
                            {
                                "state": state,
                                "vintage": vintage,
                                "slug": slug,
                                "justia_unavailable": True,
                                "alternative_year": result.pass1_availability.get(
                                    "alternative_year"
                                ),
                                "notes": result.pass1_availability.get("notes", ""),
                                "retrieved_at": _now_iso(),
                            }
                        )
                        + "\n"
                    )

        results[(state, vintage)] = result

    await asyncio.gather(*(process(s, v, slug) for s, v, slug in triples))
    return results


# ===========================================================================
# End B3 block
# ===========================================================================


def load_env_local(env_path: Path) -> None:
    """Load `KEY=VALUE` lines from a `.env.local`-style file into `os.environ`.

    Pre-existing env vars are not overwritten. Comments (`#`) and blank
    lines are ignored. Surrounding single/double quotes on values are
    stripped. No new dependency — kept deliberately minimal.
    """
    env_path = Path(env_path)
    if not env_path.exists():
        return
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if (value.startswith('"') and value.endswith('"')) or (
            value.startswith("'") and value.endswith("'")
        ):
            value = value[1:-1]
        if key and key not in os.environ:
            os.environ[key] = value
