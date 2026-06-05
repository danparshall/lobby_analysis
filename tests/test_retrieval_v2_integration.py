"""T1 integration smoke test for retrieval_v2 — first real Citations API exercise.

Auto-runs on every `uv run pytest` when ANTHROPIC_API_KEY is set; otherwise
skipped (so no-key dev environments still get green from the other test files).

Cost discipline (per plan Phase 7):
- 2-sentence statute fixture (~3 sentences, 2 obvious cross-refs)
- max_tokens=2000 override (production default is 16000)
- single chunk in scope (actor_registration_required)
- pricing estimate: ~$0.02 per run

Imports for retrieval_v2 happen inside test functions so Phase 1 RED
collection on a key-less machine produces clean skips, not ImportError noise.
"""

import json
import os
from pathlib import Path

import pytest

pytestmark = pytest.mark.skipif(
    not os.environ.get("ANTHROPIC_API_KEY"),
    reason="Integration test requires ANTHROPIC_API_KEY",
)

TINY_STATUTE_PATH = Path(__file__).parent / "fixtures" / "retrieval_v2" / "tiny_statute.txt"
# Real-API response is written here as a local-inspection aid (gitignored).
# Distinct from sample_response_handcrafted.json, which parser unit tests pin
# against and which exercises edge cases (mixed tool types, multi-tool reset)
# that a single live API call may not naturally produce.
SAMPLE_RESPONSE_PATH = (
    Path(__file__).parent / "fixtures" / "retrieval_v2" / "sample_response_real.json"
)


def _tiny_bundle() -> list[dict]:
    return [
        {
            "path": "tiny_statute.txt",
            "content": TINY_STATUTE_PATH.read_text(),
            "title": "Tiny statute",
        }
    ]


def _tiny_brief() -> dict:
    from lobby_analysis.retrieval_v2.brief_writer import build_retrieval_brief

    brief = build_retrieval_brief(
        state="ZZ",
        vintage=2026,
        statute_bundle=_tiny_bundle(),
        chunks=["actor_registration_required"],
        url_pattern="https://law.justia.com/codes/example/2026/title99/chapter99/99_005.html",
    )
    # Cost discipline: override production default
    brief["max_tokens"] = 2000
    return brief


def test_real_api_call_returns_citations():
    """At least one content block has a non-empty citations list."""
    import anthropic

    client = anthropic.Anthropic()
    response = client.messages.create(**_tiny_brief())
    has_cite = any(getattr(block, "citations", None) for block in response.content)
    assert has_cite, "no text block had any citations attached"


def test_real_api_call_produces_at_least_one_cross_reference():
    """At least one tool_use block calling record_cross_reference fires."""
    import anthropic

    client = anthropic.Anthropic()
    response = client.messages.create(**_tiny_brief())
    cross_refs = [
        b
        for b in response.content
        if getattr(b, "type", None) == "tool_use"
        and getattr(b, "name", None) == "record_cross_reference"
    ]
    assert cross_refs, "no record_cross_reference tool calls emitted"


def test_parser_handles_real_api_response():
    """Parser yields non-empty cross_references with attached evidence_spans.

    Side effect: writes the real API response to sample_response_real.json
    (gitignored, local-inspection aid). Decoupled from sample_response_handcrafted.json,
    which parser unit tests pin against.
    """
    import anthropic

    from lobby_analysis.retrieval_v2.parser import parse_retrieval_response

    client = anthropic.Anthropic()
    response = client.messages.create(**_tiny_brief())
    out = parse_retrieval_response(response, state_abbr="ZZ", vintage_year=2026, hop=1)
    assert len(out.cross_references) >= 1
    for xref in out.cross_references:
        assert len(xref.evidence_spans) >= 1, (
            f"cross_reference {xref.section_reference} has no evidence_spans"
        )
    # Persist real response for parser unit tests
    serialized = response.model_dump() if hasattr(response, "model_dump") else dict(response)
    SAMPLE_RESPONSE_PATH.write_text(json.dumps(serialized, indent=2, default=str))
