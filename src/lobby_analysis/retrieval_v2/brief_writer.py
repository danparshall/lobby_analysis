"""Build a retrieval brief — i.e. the ``messages.create()`` kwargs dict.

The brief writer does **not** call the Anthropic SDK. It returns a kwargs
dict that the orchestrator (or an integration test) hands to
``client.messages.create(**brief)``. This keeps the assembly path testable
without an API key.

Inputs:

- ``state`` / ``vintage`` — interpolated into the user message text so the
  agent has scope context.
- ``statute_bundle`` — list of dicts ``{"path", "content", "title"}``,
  one per statute file. Each becomes a ``type: "document"`` content block
  with citations enabled and ``cache_control`` set to ephemeral (so the
  bundle is cached on first call and read-cached on retries within the
  cache TTL).
- ``chunks`` — list of chunk ids to scope retrieval. Validated against
  :func:`lobby_analysis.chunks_v2.build_chunks` (unknown chunk ids raise
  :class:`ValueError`).
- ``url_pattern`` — an example Justia URL from the core chapters that the
  agent uses to infer the URL pattern for referenced sections.

Outputs the kwargs dict with: ``model``, ``max_tokens``, ``thinking``,
``output_config``, ``system``, ``messages``, ``tools``. No sampling
parameters — Opus 4.7 returns 400 if any are supplied.
"""

from pathlib import Path

from lobby_analysis.chunks_v2 import build_chunks
from lobby_analysis.retrieval_v2.tools import ALL_TOOLS

# src/lobby_analysis/retrieval_v2/brief_writer.py → repo root → src/scoring/...
_PROMPT_PATH = (
    Path(__file__).parent.parent.parent.parent / "src" / "scoring" / "retrieval_agent_prompt_v2.md"
)

_MODEL = "claude-opus-4-7"
_MAX_TOKENS = 16000


def build_retrieval_brief(
    state: str,
    vintage: int,
    statute_bundle: list[dict],
    chunks: list[str],
    url_pattern: str = "",
) -> dict:
    """Assemble ``messages.create()`` kwargs for a retrieval call.

    Args:
        state: Two-letter state abbreviation (e.g., ``"OH"``).
        vintage: Vintage year (e.g., ``2010``).
        statute_bundle: List of statute file dicts; each requires ``path``
            and ``content`` keys, and may supply ``title`` (falls back to
            ``path``).
        chunks: Chunk ids in scope for this call. Each must exist in
            :func:`lobby_analysis.chunks_v2.build_chunks`; unknown ids raise.
        url_pattern: Example Justia URL from the core chapters; the agent
            infers the pattern for constructing URLs to referenced sections.

    Returns:
        Dict suitable for ``client.messages.create(**brief)``.

    Raises:
        ValueError: If ``chunks`` contains any chunk id not in the manifest.
    """
    all_chunks_by_id = {c.chunk_id: c for c in build_chunks()}
    unknown = set(chunks) - set(all_chunks_by_id)
    if unknown:
        raise ValueError(f"Unknown chunks: {sorted(unknown)}")

    requested_chunks = [all_chunks_by_id[cid] for cid in chunks]
    cell_roster_text = _format_cell_roster(requested_chunks)
    prompt_template = _PROMPT_PATH.read_text()

    document_blocks = [
        {
            "type": "document",
            "source": {
                "type": "text",
                "media_type": "text/plain",
                "data": doc["content"],
            },
            "title": doc.get("title") or doc["path"],
            "citations": {"enabled": True},
            "cache_control": {"type": "ephemeral"},
        }
        for doc in statute_bundle
    ]

    user_text = _build_user_text(state, vintage, cell_roster_text, url_pattern)

    return {
        "model": _MODEL,
        "max_tokens": _MAX_TOKENS,
        "thinking": {"type": "adaptive"},
        "output_config": {"effort": "high"},
        "system": [
            {
                "type": "text",
                "text": prompt_template,
                "cache_control": {"type": "ephemeral"},
            }
        ],
        "messages": [
            {
                "role": "user",
                "content": [
                    *document_blocks,
                    {"type": "text", "text": user_text},
                ],
            }
        ],
        "tools": ALL_TOOLS,
    }


def _format_cell_roster(chunks: list) -> str:
    """Render the cell roster text the agent reads in the user message.

    Per-chunk format:

        ### Chunk: <chunk_id> (<n> cells, <axis_summary>)
        Topic: <topic>
        - <row_id> (<axis>) [<expected_cell_class>]
        ...

    NB: ``CompendiumCellSpec`` carries no free-form description (the plan
    draft assumed ``spec.description`` which doesn't exist). The row_id is
    self-describing in this codebase, and ``expected_cell_class.__name__``
    tells the agent the value shape it should ground.
    """
    lines: list[str] = []
    for chunk in chunks:
        lines.append("")
        lines.append(
            f"### Chunk: {chunk.chunk_id} ({len(chunk.cell_specs)} cells, {chunk.axis_summary})"
        )
        lines.append(f"Topic: {chunk.topic}")
        for spec in chunk.cell_specs:
            cell_class = spec.expected_cell_class.__name__
            lines.append(f"- {spec.row_id} ({spec.axis}) [{cell_class}]")
    return "\n".join(lines)


def _build_user_text(state: str, vintage: int, cell_roster: str, url_pattern: str) -> str:
    """Build the user-message text following the statute documents."""
    return (
        f"State: {state}\n"
        f"Vintage: {vintage}\n\n"
        f"Example URL pattern: {url_pattern}\n\n"
        f"## Compendium cells in scope for this call:\n{cell_roster}\n\n"
        f"Identify cross-references in the statute documents above. For each, "
        f"call `record_cross_reference` with the supporting statute span cited "
        f"in the preceding text. For references you cannot resolve to a section "
        f"number, call `record_unresolvable_reference`."
    )
