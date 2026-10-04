"""T1 integration smoke test for scoring_v2 — first real Citations + tool use exercise.

Auto-runs on every `uv run pytest` when ANTHROPIC_API_KEY is set; otherwise
skipped (so no-key dev environments still get green from the other test files).

Cost discipline (per plan Phase 8):
- 3-sentence statute fixture (tests/fixtures/scoring_v2/tiny_statute.txt)
- max_tokens=2000 override (production default is 16000)
- single chunk in scope (enforcement_and_audits — 2 legal cells, smallest meaningful chunk)
- empty RetrievalOutput (no cross_references) is fine
- pricing estimate: ~$0.04 per run

Imports for scoring_v2 happen inside test functions so Phase 1 RED collection
on a key-less machine produces clean skips, not ImportError noise.
"""

import json
import os
from pathlib import Path

import pytest

pytestmark = pytest.mark.skipif(
    not os.environ.get("ANTHROPIC_API_KEY"),
    reason="Integration test requires ANTHROPIC_API_KEY",
)

TINY_STATUTE_PATH = Path(__file__).parent / "fixtures" / "scoring_v2" / "tiny_statute.txt"
# Real-API response written here as a local-inspection aid (gitignored).
SAMPLE_RESPONSE_REAL_PATH = (
    Path(__file__).parent / "fixtures" / "scoring_v2" / "sample_response_real.json"
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
    from lobby_analysis.retrieval_v2 import RetrievalOutput
    from lobby_analysis.scoring_v2.brief_writer import build_scoring_brief

    empty_retrieval = RetrievalOutput(
        state_abbr="ZZ",
        vintage_year=2026,
        hop=1,
        cross_references=(),
        unresolvable_references=(),
    )
    brief = build_scoring_brief(
        state="ZZ",
        vintage=2026,
        chunks=["enforcement_and_audits"],
        retrieval_output=empty_retrieval,
        statute_bundle=_tiny_bundle(),
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


def test_real_api_call_produces_at_least_one_record_cell():
    """At least one tool_use block calling record_cell fires."""
    import anthropic

    client = anthropic.Anthropic()
    response = client.messages.create(**_tiny_brief())
    record_cells = [
        b
        for b in response.content
        if getattr(b, "type", None) == "tool_use"
        and getattr(b, "name", None) == "record_cell"
    ]
    assert record_cells, "no record_cell tool calls emitted"


def test_parser_handles_real_scoring_response():
    """Parser yields non-empty cells with attached provenance.

    Side effect: writes the real API response to sample_response_real.json
    (gitignored, local-inspection aid).
    """
    import anthropic

    from lobby_analysis.scoring_v2.parser import parse_scoring_response

    client = anthropic.Anthropic()
    response = client.messages.create(**_tiny_brief())
    out = parse_scoring_response(
        response,
        state_abbr="ZZ",
        vintage_year=2026,
        chunk_id="enforcement_and_audits",
    )
    assert len(out.cells) >= 1
    assert any(len(c.provenance) >= 1 for c in out.cells), (
        "no cell had non-empty provenance"
    )
    # Persist real response for inspection.
    serialized = response.model_dump() if hasattr(response, "model_dump") else dict(response)
    SAMPLE_RESPONSE_REAL_PATH.write_text(json.dumps(serialized, indent=2, default=str))
