"""Parse a ``messages.create()`` response into typed :class:`RetrievalOutput`.

**Pairing rule.** Citations from text blocks accumulate in a buffer until a
``tool_use`` block is encountered; those citations attach to that tool call's
parsed output as ``evidence_spans``. The buffer resets after each
``tool_use`` so the next tool call starts fresh — this is the load-bearing
invariant enforced by ``test_parser_resets_citation_buffer_after_each_tool_call``.

Block types other than ``text`` and ``tool_use`` (e.g. ``thinking``,
``server_tool_use``) are ignored: they pass through without disturbing the
citation buffer or producing output. Unknown tool names are silently skipped
but still cause the buffer to reset (to prevent stale citations attaching
to the next valid tool call).

The parser accepts either an Anthropic SDK ``Message`` object (attribute
access via ``getattr``) or a plain dict (dict access via ``.get``) — the
``_get`` helper handles both so the same parser path works against the
hand-crafted fixture *and* against real API responses.
"""

from typing import Any

from lobby_analysis.retrieval_v2.models import (
    CrossReference,
    EvidenceSpan,
    RetrievalOutput,
    UnresolvableReference,
)


def parse_retrieval_response(
    message: Any,
    state_abbr: str,
    vintage_year: int,
    hop: int,
) -> RetrievalOutput:
    """Parse a Citations API response into structured output.

    Args:
        message: An ``anthropic.types.Message`` instance or an equivalent
            dict (e.g., a fixture loaded from JSON).
        state_abbr: Two-letter state abbreviation (echoed into output).
        vintage_year: Vintage year (echoed into output).
        hop: 1 or 2 (echoed into output; validated by ``RetrievalOutput``).

    Returns:
        :class:`RetrievalOutput` with cross_references and
        unresolvable_references populated from tool_use blocks.
    """
    content = _get_content(message)

    cross_refs: list[CrossReference] = []
    unresolvables: list[UnresolvableReference] = []
    citation_buffer: list[EvidenceSpan] = []

    for block in content:
        block_type = _get(block, "type")

        if block_type == "text":
            for raw_cite in _get(block, "citations", default=[]) or []:
                citation_buffer.append(_parse_citation(raw_cite))

        elif block_type == "tool_use":
            tool_name = _get(block, "name")
            tool_input = _get(block, "input") or {}
            spans = tuple(citation_buffer)
            citation_buffer = []

            if tool_name == "record_cross_reference":
                cross_refs.append(
                    CrossReference(
                        section_reference=_input(tool_input, "section_reference"),
                        chunk_ids_affected=tuple(
                            _input(tool_input, "chunk_ids_affected") or ()
                        ),
                        relevance=_input(tool_input, "relevance"),
                        justia_url=_input(tool_input, "justia_url"),
                        url_confidence=_input(tool_input, "url_confidence"),
                        url_confidence_reason=_input(
                            tool_input, "url_confidence_reason", default=""
                        ),
                        evidence_spans=spans,
                    )
                )
            elif tool_name == "record_unresolvable_reference":
                unresolvables.append(
                    UnresolvableReference(
                        reference_text=_input(tool_input, "reference_text"),
                        referenced_from=_input(tool_input, "referenced_from"),
                        reason=_input(tool_input, "reason"),
                        evidence_spans=spans,
                    )
                )
            # Unknown tool names are silently skipped — citation buffer still
            # reset above to prevent stale citations attaching to the next call.

        # Other block types (thinking, server_tool_use, etc.) pass through.

    return RetrievalOutput(
        state_abbr=state_abbr,
        vintage_year=vintage_year,
        hop=hop,
        cross_references=tuple(cross_refs),
        unresolvable_references=tuple(unresolvables),
    )


def _parse_citation(raw: Any) -> EvidenceSpan:
    """Parse a single citation into an :class:`EvidenceSpan`."""
    cite_type = _get(raw, "type")
    common: dict[str, Any] = {
        "citation_type": cite_type,
        "document_index": _get(raw, "document_index"),
        "document_title": _get(raw, "document_title"),
        "cited_text": _get(raw, "cited_text"),
    }
    if cite_type == "char_location":
        return EvidenceSpan(
            **common,
            start_char_index=_get(raw, "start_char_index"),
            end_char_index=_get(raw, "end_char_index"),
        )
    if cite_type == "page_location":
        return EvidenceSpan(
            **common,
            start_page_number=_get(raw, "start_page_number"),
            end_page_number=_get(raw, "end_page_number"),
        )
    if cite_type == "content_block_location":
        return EvidenceSpan(
            **common,
            start_block_index=_get(raw, "start_block_index"),
            end_block_index=_get(raw, "end_block_index"),
        )
    raise ValueError(f"Unknown citation type: {cite_type!r}")


def _get_content(message: Any) -> list:
    """Return the ``content`` list from a Message obj or dict."""
    if hasattr(message, "content"):
        return message.content
    if isinstance(message, dict):
        return message.get("content", [])
    return []


def _get(obj: Any, key: str, default: Any = None) -> Any:
    """Attribute-or-dict access. Used for SDK objects (attrs) and fixtures (dicts)."""
    if hasattr(obj, key):
        return getattr(obj, key)
    if isinstance(obj, dict):
        return obj.get(key, default)
    return default


def _input(tool_input: Any, key: str, default: Any = None) -> Any:
    """Pull a key from a tool_use ``input`` field; supports dict-or-attr."""
    if isinstance(tool_input, dict):
        return tool_input.get(key, default)
    if hasattr(tool_input, key):
        return getattr(tool_input, key)
    return default
