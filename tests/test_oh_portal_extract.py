"""Tests for the OH-portal single-AER extraction assembly.

The Anthropic API call is an external boundary and is NOT exercised here. What
IS tested is the deterministic, pure assembly that surrounds it:

  - `assemble_filing` makes the persisted audit text (`raw_text`) equal to the
    source text the pipeline already computed, independent of (and overriding)
    whatever the model emitted. This is the provenance guarantee: the audit
    field is source-of-truth, not model-paraphrase.
  - `build_tool_schema` hides `raw_text` from the model so it stops
    re-transcribing text the code already has (and saves output tokens).
"""

from lobby_analysis.models.provenance import Provenance
from lobby_analysis.oh_portal.extract import assemble_filing, build_tool_schema

_MINIMAL_INPUT = {
    "id": "oh-1427844",
    "state": "OH",
    "filing_type": "activity_report",
    "filer_role": "lobbyist",
}
_PROVENANCE = Provenance(extraction_method="llm")


def test_assemble_filing_populates_raw_text_from_source_when_model_omits_it() -> None:
    # The model returned no raw_text (the common case: 64% of the slice lacked it).
    aer_text = "AGENT: Jane Doe\nEMPLOYER: ARC Gaming\nPERIOD: May-Aug25"
    filing = assemble_filing(_MINIMAL_INPUT, aer_text, _PROVENANCE)
    assert filing.raw_text == aer_text


def test_assemble_filing_overrides_model_supplied_raw_text_with_source() -> None:
    # Even when the model DID emit a raw_text, the code-computed source text wins
    # — a model that paraphrases or truncates can't corrupt the audit field.
    tool_input = {**_MINIMAL_INPUT, "raw_text": "a lossy model paraphrase"}
    aer_text = "the exact source text the pipeline fetched and cleaned"
    filing = assemble_filing(tool_input, aer_text, _PROVENANCE)
    assert filing.raw_text == aer_text


def test_assemble_filing_attaches_provenance() -> None:
    filing = assemble_filing(_MINIMAL_INPUT, "source", _PROVENANCE)
    assert filing.provenance == _PROVENANCE


def test_build_tool_schema_hides_raw_text_but_keeps_real_fields() -> None:
    props = build_tool_schema()["properties"]
    # raw_text is code-populated now, so the model must not be asked for it...
    assert "raw_text" not in props
    # ...but the rest of the schema must be intact (guards against nuking it).
    assert "positions" in props
    assert "total_expenditure" in props
