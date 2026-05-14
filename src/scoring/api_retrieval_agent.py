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
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable
from urllib.parse import urlparse


JUSTIA_HOSTNAME = "law.justia.com"


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


def _format_prompt(state: str, vintage: int, template: str) -> str:
    """Fill `{state}` and `{vintage}` placeholders into the prompt template."""
    return template.format(state=state, vintage=vintage)


def _parse_response_text(text: str) -> tuple[list[ProposedURL], list[dict]]:
    """Extract `{"urls": [...]}` from the LLM response text.

    Returns (parsed_urls, schema_violations). Violations are dicts of
    `{"url": ..., "reason": ...}` for entries the parser rejected.
    """
    data = json.loads(text)
    raw_urls = data.get("urls", [])
    parsed: list[ProposedURL] = []
    violations: list[dict] = []
    for entry in raw_urls:
        try:
            parsed.append(ProposedURL.from_raw(entry))
        except SchemaViolation as e:
            violations.append({"url": entry.get("url", ""), "reason": str(e)})
    return parsed, violations


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


async def discover_urls_for_pair(
    client,
    *,
    state: str,
    vintage: int,
    prompt_template: str,
    model: str = "claude-sonnet-4-7",
    max_output_tokens: int = 4096,
) -> list[ProposedURL]:
    """Discover Justia URLs for a single (state, vintage) pair.

    Returns the parsed `ProposedURL` list. Schema violations (non-Justia
    URLs) are silently dropped from the return value — callers that need
    to audit them should use `discover_urls_for_pairs`, which records
    them in the per-pair checkpoint.
    """
    prompt = _format_prompt(state, vintage, prompt_template)
    response = await client.messages.create(
        model=model,
        max_tokens=max_output_tokens,
        messages=[{"role": "user", "content": prompt}],
    )
    text = response.content[0].text
    parsed, _violations = _parse_response_text(text)
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
    model: str = "claude-sonnet-4-7",
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
    failures_lock = asyncio.Lock()
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
        parsed, violations = _parse_response_text(text)

        checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
        checkpoint = {
            "prompt": prompt,
            "model": model,
            "response": text,
            "retrieved_at": _now_iso(),
            "parsed_urls": [
                {"url": p.url, "role": p.role, "rationale": p.rationale}
                for p in parsed
            ],
            "schema_violations": violations,
        }
        checkpoint_path.write_text(
            json.dumps(checkpoint, indent=2), encoding="utf-8"
        )
        results[(state, vintage)] = parsed

    await asyncio.gather(*(process_pair(s, v) for s, v in pairs))
    return results


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
