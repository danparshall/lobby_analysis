"""Builds Provenance records for OH-portal LLM extractions.

extraction_method is hard-coded to "llm" because (A') only does LLM
extraction. If (B') needs regex/direct_copy variants, parameterize then.
"""

from datetime import datetime, timezone

from lobby_analysis.models.provenance import Provenance


def build_provenance(
    source_url: str,
    model_version: str,
    prompt_version: str,
) -> Provenance:
    """Build a Provenance for one LLM extraction call.

    extracted_at is set to UTC now() at call time. The fetched-bytes sha256
    lives in the fetch sidecar (meta.json), not in Provenance — Provenance
    tracks the *extraction* event, not the *fetch* event.
    """
    return Provenance(
        source_url=source_url,
        extraction_method="llm",
        model_version=model_version,
        prompt_version=prompt_version,
        extracted_at=datetime.now(timezone.utc),
    )
