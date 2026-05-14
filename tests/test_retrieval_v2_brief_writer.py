"""Tests for retrieval_v2 brief_writer.

Phase 1 (RED): all tests fail with ImportError because build_retrieval_brief
doesn't yet exist in lobby_analysis.retrieval_v2.brief_writer.
"""

from lobby_analysis.retrieval_v2.brief_writer import build_retrieval_brief


def _bundle() -> list[dict]:
    return [
        {
            "path": "ch101.txt",
            "content": "Section 1. Every lobbyist must register.",
            "title": "OH ch.101",
        }
    ]


def _build() -> dict:
    return build_retrieval_brief(
        state="OH",
        vintage=2010,
        statute_bundle=_bundle(),
        chunks=["actor_registration_required"],
        url_pattern="https://law.justia.com/codes/ohio/2010/title1/chapter101/101_70.html",
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


def test_brief_writer_omits_temperature():
    assert "temperature" not in _build()


def test_brief_writer_omits_top_p():
    assert "top_p" not in _build()


def test_brief_writer_omits_top_k():
    assert "top_k" not in _build()


def test_brief_writer_attaches_both_tools():
    tools = _build()["tools"]
    names = {t["name"] for t in tools}
    assert names == {"record_cross_reference", "record_unresolvable_reference"}


def test_brief_writer_includes_state_vintage_in_user_text():
    combined = _user_text_concat(_build())
    assert "OH" in combined or "Ohio" in combined
    assert "2010" in combined


def test_brief_writer_packages_statute_files_as_documents():
    docs = _document_blocks(_build())
    assert len(docs) == 1


def test_brief_writer_enables_citations_on_all_documents():
    """All-or-nothing per Citations API."""
    for doc in _document_blocks(_build()):
        assert doc["citations"]["enabled"] is True


def test_brief_writer_applies_cache_control_to_documents():
    for doc in _document_blocks(_build()):
        assert doc["cache_control"] == {"type": "ephemeral"}


def test_brief_writer_uses_plain_text_source_type():
    for doc in _document_blocks(_build()):
        assert doc["source"]["type"] == "text"
        assert doc["source"]["media_type"] == "text/plain"


def test_brief_writer_sets_document_title():
    for doc in _document_blocks(_build()):
        assert "title" in doc and doc["title"]


def test_brief_writer_includes_only_requested_chunks_cell_roster():
    """Cell roster mentions only chunks requested in the chunks arg."""
    combined = _user_text_concat(_build())
    assert "actor_registration_required" in combined
    # not requested → must NOT appear
    assert "lobbyist_spending_report" not in combined


def test_brief_writer_caches_system_prompt():
    """System block has cache_control (frozen across calls per Q1 caching strategy)."""
    system = _build()["system"]
    assert isinstance(system, list)
    assert any(b.get("cache_control") == {"type": "ephemeral"} for b in system)


def test_brief_writer_max_tokens_is_16000():
    assert _build()["max_tokens"] == 16000
