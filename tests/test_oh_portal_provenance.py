"""Tests for OH-portal extraction provenance builder.

Tests that we *populate* a valid Provenance from the inputs we'll have at
extraction time (source URL, model identity, prompt identity), not that
the Pydantic class itself works. The class is already covered by
tests/test_models.py.
"""

from lobby_analysis.models.provenance import Provenance
from lobby_analysis.oh_portal.provenance import build_provenance

SAMPLE_URL = "https://www2.jlec-olig.state.oh.us/olac/AERs/1427844/View"
SAMPLE_MODEL = "claude-opus-4-7"
SAMPLE_PROMPT_SHA = "a1b2c3d4e5f6"


def test_build_provenance_populates_required_fields() -> None:
    """All five fields (A') needs from a Provenance — source URL, extraction
    method, model version, prompt version, extracted-at timestamp — must be
    populated by the builder. extraction_method is the only Pydantic-required
    one, but the others are non-optional from a *behavior* standpoint: a
    Provenance with null model_version is useless for re-running extractions."""
    p = build_provenance(
        source_url=SAMPLE_URL,
        model_version=SAMPLE_MODEL,
        prompt_version=SAMPLE_PROMPT_SHA,
    )
    assert p.source_url == SAMPLE_URL
    assert p.extraction_method == "llm"
    assert p.model_version == SAMPLE_MODEL
    assert p.prompt_version == SAMPLE_PROMPT_SHA
    assert p.extracted_at is not None


def test_build_provenance_round_trips_through_json() -> None:
    """The output Provenance must serialize to JSON and deserialize back
    cleanly — this is what gets emitted as part of LobbyingFiling.
    model_dump_json() to disk and read by Track A tools / Gowrav's front
    end. A round-trip mismatch here breaks the inter-track contract."""
    original = build_provenance(
        source_url=SAMPLE_URL,
        model_version=SAMPLE_MODEL,
        prompt_version=SAMPLE_PROMPT_SHA,
    )
    serialized = original.model_dump_json()
    restored = Provenance.model_validate_json(serialized)
    assert restored == original
