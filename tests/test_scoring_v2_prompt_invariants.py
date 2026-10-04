"""Invariant tests for the v2 scorer prompt markdown.

Phase 1 (RED): all tests fail because src/scoring/scorer_prompt_v2.md does
not yet exist.

These tests catch v1-prompt leakage into the v2 rewrite — PRI rubric letter
refs (A1-A11, C0-C3), the word "rubric", the files_read.json mechanism,
the "unable_to_evaluate" sentinel — and ensure the tool-call mandates +
citation-before-tool rule are present.
"""

import re
from pathlib import Path

V2_PROMPT_PATH = (
    Path(__file__).parent.parent / "src" / "scoring" / "scorer_prompt_v2.md"
)


def _prompt() -> str:
    return V2_PROMPT_PATH.read_text()


def test_prompt_exists_and_nonempty():
    assert V2_PROMPT_PATH.exists(), f"prompt missing at {V2_PROMPT_PATH}"
    text = _prompt()
    assert text.strip(), "prompt is empty"
    assert len(text) > 1500


def test_prompt_no_pri_rubric_letter_refs():
    matches = re.findall(r"\b[AC]\d{1,2}\b", _prompt())
    assert not matches, f"PRI rubric letter leaks: {matches}"


def test_prompt_no_rubric_word():
    assert not re.search(r"\brubric\b", _prompt(), re.IGNORECASE)


def test_prompt_no_files_read_json_reference():
    text = _prompt()
    assert "files_read.json" not in text
    assert "files_read" not in text


def test_prompt_no_unable_to_evaluate_token():
    """v1 Rule 2 mechanism — replaced by record_unscoreable_cell tool."""
    assert "unable_to_evaluate" not in _prompt()


def test_prompt_mentions_record_cell_tool():
    assert "record_cell" in _prompt()


def test_prompt_mentions_record_unscoreable_cell_tool():
    assert "record_unscoreable_cell" in _prompt()


def test_prompt_instructs_citation_before_each_tool_call():
    """Loose match — the citation-before-tool rule is what makes the parser's pairing rule non-vacuous."""
    assert re.search(r"cite.{0,80}before.{0,40}tool call", _prompt(), re.IGNORECASE)
