"""Tests for retrieval_v2 prompt invariants.

Phase 1 (RED): tests fail at runtime with FileNotFoundError because
src/scoring/retrieval_agent_prompt_v2.md doesn't exist yet (Phase 6 creates it).
The read is inside a fixture so collection succeeds and each test fails
cleanly at use-time rather than at import-time.
"""

import re
from pathlib import Path

import pytest

V2_PROMPT_PATH = Path(__file__).parent.parent / "src" / "scoring" / "retrieval_agent_prompt_v2.md"


@pytest.fixture
def prompt() -> str:
    return V2_PROMPT_PATH.read_text()


def test_prompt_exists_and_nonempty(prompt: str):
    assert prompt.strip()
    assert len(prompt) > 1000


def test_prompt_no_pri_rubric_letter_refs(prompt: str):
    """No A1..A11, C0..C3 standalone tokens (PRI rubric letter leakage)."""
    matches = re.findall(r"\b[AC]\d{1,2}\b", prompt)
    assert not matches, f"PRI rubric letter leaks: {matches}"


def test_prompt_no_rubric_items_affected_string(prompt: str):
    """The v1 output field 'rubric_items_affected' must not appear."""
    assert "rubric_items_affected" not in prompt


def test_prompt_no_rubric_word(prompt: str):
    """'rubric' should not appear as a standalone word (case insensitive).

    v2 anchors on chunks + cells, not rubrics.
    """
    assert not re.search(r"\brubric\b", prompt, re.IGNORECASE)


def test_prompt_mentions_record_cross_reference_tool(prompt: str):
    assert "record_cross_reference" in prompt


def test_prompt_mentions_record_unresolvable_reference_tool(prompt: str):
    assert "record_unresolvable_reference" in prompt


def test_prompt_anchors_at_least_three_chunk_names(prompt: str):
    """Chunk-anchoring landed: at least 3 chunk_ids by name."""
    for chunk_id in (
        "actor_registration_required",
        "lobbying_definitions",
        "lobbyist_spending_report",
    ):
        assert chunk_id in prompt, f"missing chunk anchor: {chunk_id}"


def test_prompt_instructs_citation_before_tool_call(prompt: str):
    """Rule 5: loose match for 'cite before tool call' guidance."""
    lowered = prompt.lower()
    phrases = (
        "cite the supporting",
        "citing the relevant",
        "first emit a brief text passage citing",
        "before each tool call",
        "before calling",
    )
    assert any(phrase in lowered for phrase in phrases), (
        "expected citation-before-tool-call guidance in prompt"
    )
