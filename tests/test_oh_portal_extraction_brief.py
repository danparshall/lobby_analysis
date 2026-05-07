"""Tests for OH legislative-agent extraction brief builder.

Tests *what the LLM sees* — substring presence in the rendered brief —
not data structure shape. Per the (A') plan, this brief is the prompt
that gets passed alongside the OLAC AER text to claude-opus-4-7.
"""

from lobby_analysis.oh_portal.extraction_brief import build_oh_legislative_brief


def test_brief_cites_oh_legislative_statute() -> None:
    """The brief must name the controlling Ohio statute so the LLM has the
    regime grounding. ORC §§101.70-101.79 governs OH legislative-agent
    disclosure (per Dan's regime survey on origin/statute-extraction)."""
    brief = build_oh_legislative_brief()
    assert "ORC" in brief, "brief must cite Ohio Revised Code"


def test_brief_mentions_lobbying_position_field() -> None:
    """The brief must surface at least one LobbyingFiling sub-entity field
    name so the LLM knows what target structure to populate. 'position' is
    a Literal-valued field on LobbyingPosition — its presence in the brief
    is the canonical proxy for 'the brief documents the target schema'."""
    brief = build_oh_legislative_brief()
    assert "position" in brief, "brief must reference the 'position' field"


def test_brief_instructs_no_guessing() -> None:
    """The brief must explicitly tell the model to leave fields null when
    not stated in the source — preventing hallucinated values is a hard
    constraint at (A') scale, where one wrong field skews the validation
    log's CORRECT/WRONG/MISSING/SCHEMA-GAP tallies."""
    brief = build_oh_legislative_brief()
    assert "null when not stated" in brief, (
        "brief must explicitly instruct the model to leave fields null "
        "rather than guess values"
    )
