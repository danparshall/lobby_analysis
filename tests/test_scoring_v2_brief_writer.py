"""Tests for scoring_v2 brief_writer.

Phase 1 (RED): all tests fail with ImportError because build_scoring_brief
doesn't yet exist in lobby_analysis.scoring_v2.brief_writer.
"""

from pathlib import Path

import pytest

from lobby_analysis.retrieval_v2 import (
    CrossReference,
    EvidenceSpan,
    RetrievalOutput,
)
from lobby_analysis.scoring_v2.brief_writer import build_scoring_brief


def _bundle() -> list[dict]:
    return [
        {
            "path": "ch99.txt",
            "content": "Section 1. The commission shall audit each lobbyist annually.",
            "title": "OH ch.99",
        }
    ]


def _retrieval_output() -> RetrievalOutput:
    span = EvidenceSpan(
        citation_type="char_location",
        document_index=0,
        document_title="ch99.txt",
        cited_text="audit each lobbyist annually",
        start_char_index=20,
        end_char_index=48,
    )
    xref = CrossReference(
        section_reference="§99.005",
        chunk_ids_affected=("enforcement_and_audits",),
        relevance="defines audit waiver criteria",
        justia_url="https://example.com/99_005.html",
        url_confidence="medium",
        url_confidence_reason="title inferred",
        evidence_spans=(span,),
    )
    return RetrievalOutput(
        state_abbr="OH",
        vintage_year=2015,
        hop=1,
        cross_references=(xref,),
        unresolvable_references=(),
    )


def _build(chunks: list[str] | None = None) -> dict:
    return build_scoring_brief(
        state="OH",
        vintage=2015,
        chunks=chunks if chunks is not None else ["enforcement_and_audits"],
        retrieval_output=_retrieval_output(),
        statute_bundle=_bundle(),
        url_pattern="https://example.com/99_005.html",
    )


def _user_text_concat(brief: dict) -> str:
    blocks = brief["messages"][0]["content"]
    text_blocks = [b for b in blocks if b.get("type") == "text"]
    return "\n".join(b["text"] for b in text_blocks)


def _document_blocks(brief: dict) -> list[dict]:
    return [b for b in brief["messages"][0]["content"] if b.get("type") == "document"]


def test_brief_writer_returns_messages_create_kwargs():
    brief = _build()
    for key in (
        "model",
        "max_tokens",
        "thinking",
        "output_config",
        "system",
        "messages",
        "tools",
    ):
        assert key in brief, f"missing key: {key}"


def test_brief_writer_uses_claude_opus_4_7():
    assert _build()["model"] == "claude-opus-4-7"


def test_brief_writer_uses_adaptive_thinking():
    assert _build()["thinking"] == {"type": "adaptive"}


def test_brief_writer_uses_effort_high():
    assert _build()["output_config"] == {"effort": "high"}


def test_brief_writer_omits_sampling_params():
    brief = _build()
    assert "temperature" not in brief
    assert "top_p" not in brief
    assert "top_k" not in brief


def test_brief_writer_max_tokens_is_16000():
    assert _build()["max_tokens"] == 16000


def test_brief_writer_attaches_both_tools():
    tools = _build()["tools"]
    names = {t["name"] for t in tools}
    assert names == {"record_cell", "record_unscoreable_cell"}


def test_brief_writer_system_block_loads_scorer_prompt_v2():
    system = _build()["system"]
    assert isinstance(system, list)
    assert system[0].get("cache_control") == {"type": "ephemeral"}
    text = system[0]["text"]
    # Distinctive phrase from v2 prompt Rule 3 ("cite ... before each tool call").
    assert "cite" in text.lower()
    assert "tool call" in text.lower()


def test_brief_writer_packages_statute_files_as_documents_with_citations():
    docs = _document_blocks(_build())
    assert len(docs) == 1
    for doc in docs:
        assert doc["citations"]["enabled"] is True
        assert doc["cache_control"] == {"type": "ephemeral"}
        assert doc["source"]["type"] == "text"


def test_brief_writer_user_text_includes_state_and_vintage():
    combined = _user_text_concat(_build())
    assert "OH" in combined
    assert "2015" in combined


def test_brief_writer_user_text_includes_cell_roster_for_legal_axis_only():
    """enforcement_and_audits is a mixed chunk; legal half scores, practical half excluded.

    The roster should list each row_id once with axis=legal — but row_ids appear in
    both halves. The verifiable invariant is that the user text contains a marker
    showing the axis label per cell (e.g. "(legal)") and DOES NOT instruct on practical
    GradedIntCell shape (e.g. no GradedIntCell mention).
    """
    combined = _user_text_concat(_build())
    # Legal cells (BinaryCell + EnumCell shapes) should appear:
    assert "BinaryCell" in combined or "EnumCell" in combined
    # GradedIntCell is the practical-half shape for this chunk — it must NOT appear
    # in the brief, because we filter to legal cells only.
    assert "GradedIntCell" not in combined


def test_brief_writer_user_text_includes_retrieval_annotations():
    combined = _user_text_concat(_build())
    assert "§99.005" in combined
    # relevance text should be excerpted
    assert "audit" in combined.lower()


def test_brief_writer_unknown_chunk_raises_value_error():
    with pytest.raises(ValueError) as exc_info:
        _build(chunks=["nonexistent_chunk"])
    assert "nonexistent_chunk" in str(exc_info.value)


def test_brief_writer_practical_only_chunk_raises_value_error():
    """search_portal_capabilities is practical-only — must be rejected."""
    with pytest.raises(ValueError) as exc_info:
        _build(chunks=["search_portal_capabilities"])
    msg = str(exc_info.value).lower()
    assert "legal" in msg or "practical" in msg


def test_brief_writer_loads_preamble_if_present(monkeypatch, tmp_path):
    """When src/scoring/chunk_frames_v2/<chunk_id>.md exists, brief inserts its content."""
    import lobby_analysis.scoring_v2.brief_writer as bw

    preamble_text = "PREAMBLE-SENTINEL-7c5e: focus on whether audits are unconditional."
    (tmp_path / "enforcement_and_audits.md").write_text(preamble_text)
    monkeypatch.setattr(bw, "_PREAMBLE_DIR", tmp_path)

    combined = _user_text_concat(_build())
    assert "PREAMBLE-SENTINEL-7c5e" in combined


def test_brief_writer_skips_silently_if_preamble_absent(monkeypatch, tmp_path):
    """Default state (no preamble file) — brief assembles cleanly without sentinel."""
    import lobby_analysis.scoring_v2.brief_writer as bw

    # Empty dir → no preamble found.
    monkeypatch.setattr(bw, "_PREAMBLE_DIR", tmp_path)
    combined = _user_text_concat(_build())
    assert "PREAMBLE-SENTINEL" not in combined
    # Brief still builds without error.
    assert "OH" in combined
