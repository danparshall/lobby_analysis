"""Run one LLM extraction call against a fetched OLAC AER.

Calls the Anthropic SDK (model set by MODEL_ID) with tool-use enforcing the
LobbyingFiling Pydantic schema. Fail-loud at every layer: HTTP error,
missing tool call, Pydantic validation failure all raise.
"""

from __future__ import annotations

import json
from pathlib import Path

import anthropic
from bs4 import BeautifulSoup

from lobby_analysis.models.filings import LobbyingFiling
from lobby_analysis.models.provenance import Provenance

MODEL_ID = "claude-sonnet-4-6"
TOOL_NAME = "emit_lobbying_filing"
MAX_TOKENS = 8192


def build_tool_schema() -> dict:
    """The LobbyingFiling JSON schema with `raw_text` removed.

    `raw_text` is the full source-text audit field; the pipeline populates it
    deterministically from the fetched source (see `assemble_filing`), so the
    model must not be asked to re-transcribe it. Dropping it also trims output
    tokens on every call. It is optional on the model, so removing it from
    `properties` leaves a valid schema with no `required` cleanup needed."""
    schema = LobbyingFiling.model_json_schema()
    schema.get("properties", {}).pop("raw_text", None)
    return schema


def assemble_filing(
    tool_input: dict,
    aer_text: str,
    provenance: Provenance,
) -> LobbyingFiling:
    """Validate a model tool_input into a LobbyingFiling, then stamp the
    code-authoritative `raw_text` (= the fetched source text) and provenance.

    `raw_text` is always set to `aer_text` regardless of any value the model
    emitted — the persisted audit text is source-of-truth, not model output."""
    filing = LobbyingFiling.model_validate(tool_input)
    filing.raw_text = aer_text
    filing.provenance = provenance
    return filing


def html_to_aer_text(html_path: Path) -> str:
    """Strip nav/footer/script/style chrome from an OLAC view page and return
    the visible text content. Keeps line breaks so the LLM sees structure."""
    soup = BeautifulSoup(html_path.read_bytes(), "html.parser")
    for tag in soup(["script", "style", "nav", "header", "footer", "noscript"]):
        tag.decompose()
    text = soup.get_text(separator="\n", strip=True)
    return "\n".join(line for line in text.splitlines() if line.strip())


def extract_oh_legislative_filing(
    html_path: Path,
    brief: str,
    provenance: Provenance,
) -> LobbyingFiling:
    """Extract one OH legislative AER's HTML into a populated LobbyingFiling.

    Raises:
        RuntimeError: if the API call doesn't include a tool_use block
            for emit_lobbying_filing.
        pydantic.ValidationError: if the model emits a structurally invalid
            LobbyingFiling.
    """
    aer_text = html_to_aer_text(html_path)

    client = anthropic.Anthropic()

    response = client.messages.create(
        model=MODEL_ID,
        max_tokens=MAX_TOKENS,
        tools=[
            {
                "name": TOOL_NAME,
                "description": (
                    "Emit a populated LobbyingFiling record matching the "
                    "supplied AER source text per the extraction brief."
                ),
                "input_schema": build_tool_schema(),
            }
        ],
        tool_choice={"type": "tool", "name": TOOL_NAME},
        messages=[
            {
                "role": "user",
                "content": (
                    brief
                    + "\n\n--- AER SOURCE TEXT ---\n\n"
                    + aer_text
                ),
            }
        ],
    )

    tool_blocks = [b for b in response.content if b.type == "tool_use"]
    if not tool_blocks or tool_blocks[0].name != TOOL_NAME:
        raise RuntimeError(
            f"Expected tool_use block named {TOOL_NAME!r}, got: "
            f"{[(b.type, getattr(b, 'name', None)) for b in response.content]}"
        )

    tool_input = tool_blocks[0].input
    return assemble_filing(tool_input, aer_text, provenance)


def dump_error(out_dir: Path, response: object, exc: Exception) -> Path:
    """Persist a failed extraction's response + exception for later inspection.
    Used by __main__ when extract_oh_legislative_filing raises."""
    out_dir.mkdir(parents=True, exist_ok=True)
    err_path = out_dir / "error.json"
    err_path.write_text(
        json.dumps(
            {
                "exception_type": type(exc).__name__,
                "exception_repr": repr(exc),
                "response_repr": repr(response),
            },
            indent=2,
        )
    )
    return err_path
