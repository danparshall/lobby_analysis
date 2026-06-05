"""v2 retrieval agent — Anthropic Citations API + tool use over the v2 compendium.

Builds a ``messages.create()`` brief, parses the response back into typed
output. Does NOT call the SDK itself — the caller (orchestrator or
integration test) dispatches the brief and feeds the response into the parser.
"""

from lobby_analysis.retrieval_v2.brief_writer import build_retrieval_brief
from lobby_analysis.retrieval_v2.models import (
    CrossReference,
    EvidenceSpan,
    RetrievalOutput,
    UnresolvableReference,
)
from lobby_analysis.retrieval_v2.parser import parse_retrieval_response
from lobby_analysis.retrieval_v2.tools import (
    ALL_TOOLS,
    CROSS_REFERENCE_TOOL,
    UNRESOLVABLE_REFERENCE_TOOL,
)

__all__ = [
    "ALL_TOOLS",
    "CROSS_REFERENCE_TOOL",
    "CrossReference",
    "EvidenceSpan",
    "RetrievalOutput",
    "UNRESOLVABLE_REFERENCE_TOOL",
    "UnresolvableReference",
    "build_retrieval_brief",
    "parse_retrieval_response",
]
