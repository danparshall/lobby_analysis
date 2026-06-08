"""Run one LLM extraction call against a fetched OLAC AER, using OpenAI.

Mirror of `extract.py` (Anthropic Sonnet path) for cross-provider cost-floor
validation. See `docs/active/leave-behind-prep/plans/20260608_gpt5mini_on_oh_300slice.md`.

Calls the OpenAI SDK (model set by MODEL_ID) with structured outputs enforcing
the LobbyingFiling Pydantic schema. Fail-loud at every layer: HTTP error,
refusal, parse failure, Pydantic validation failure all raise.

Design intent:
- Same public function signature as `extract.extract_oh_legislative_filing`
  so a dispatcher can swap providers by import-line.
- Same `assemble_filing` post-processing (raw_text from source-of-truth, not
  model output) — reuses the function from `extract.py` rather than redefining
  it, to guarantee identical assembly semantics across providers.
- Same brief content (`build_oh_legislative_brief`). The point of this
  experiment is to test model-difference at constant prompt, not the reverse.

Schema-translation note: as of openai==2.41.0, `chat.completions.parse(
response_format=LobbyingFiling)` auto-converts the Pydantic schema to OpenAI's
strict-mode JSON schema (nullable required fields, additionalProperties=false,
flattened $refs). LobbyingFiling produces ~109 object properties total; this
fits well within OpenAI's structured-outputs ceiling of 5000 (raised from 100
in July 2025). No manual flattening required.
"""

from __future__ import annotations

import json
from pathlib import Path

from openai import OpenAI

from lobby_analysis.models.filings import LobbyingFiling
from lobby_analysis.models.provenance import Provenance
from lobby_analysis.oh_portal.extract import assemble_filing, html_to_aer_text

MODEL_ID = "gpt-5-mini"
# Phase 0 step 3 of the plan: pin the dated model version after the first
# `client.models.list()` call to ensure reproducibility across the 3 runs.
# Pinned 2026-06-08 — only one dated mini variant was visible on the account
# at that time (`gpt-5-mini-2025-08-07`), and the undated alias rotates under
# the hood, which would confound the 3x self-consistency measurement.
MODEL_ID_DATED: str | None = "gpt-5-mini-2025-08-07"


def resolved_model_id() -> str:
    """Return MODEL_ID_DATED if pinned, else MODEL_ID."""
    return MODEL_ID_DATED or MODEL_ID


def extract_oh_legislative_filing(
    html_path: Path,
    brief: str,
    provenance: Provenance,
) -> tuple[LobbyingFiling, dict]:
    """Extract one OH legislative AER's HTML into a populated LobbyingFiling.

    Differs from the Anthropic signature by also returning the response usage
    dict (`prompt_tokens`, `completion_tokens`, etc.) so the dispatcher can
    track per-filing cost without re-issuing the call. The plan requires
    per-run cost tracking (step 10) and this is the cheapest way to surface it.

    Raises:
        RuntimeError: if the model refuses to respond or returns no parsed
            content.
        pydantic.ValidationError: if the model emits a structurally invalid
            LobbyingFiling.
    """
    aer_text = html_to_aer_text(html_path)
    client = OpenAI()

    completion = client.chat.completions.parse(
        model=resolved_model_id(),
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
        response_format=LobbyingFiling,
    )

    choice = completion.choices[0]
    if choice.message.refusal:
        # OpenAI structured outputs returns a refusal field rather than a
        # parsed object when the model declines. Surface this distinctly from
        # a parse failure.
        raise RuntimeError(
            f"OpenAI model refused to respond: {choice.message.refusal!r}"
        )
    filing = choice.message.parsed
    if filing is None:
        # Parse failure: model produced output that couldn't be validated
        # against the schema. The SDK normally raises before we get here,
        # but defend against the edge case.
        raise RuntimeError(
            f"OpenAI returned no parsed LobbyingFiling. "
            f"finish_reason={choice.finish_reason!r} "
            f"content={choice.message.content!r}"
        )

    # The model populated `raw_text` (the schema can't hide it without a
    # separate target class — see schema-translation note above). Overwrite
    # with source-of-truth before assembly, matching the Anthropic path's
    # provenance guarantee.
    filing_dict = filing.model_dump()
    filing_dict.pop("raw_text", None)

    usage = {
        "prompt_tokens": completion.usage.prompt_tokens,
        "completion_tokens": completion.usage.completion_tokens,
        "total_tokens": completion.usage.total_tokens,
        "model": completion.model,
    }
    return assemble_filing(filing_dict, aer_text, provenance), usage


def dump_error(out_dir: Path, exc: Exception, raw_response: str | None = None) -> Path:
    """Persist a failed extraction's exception + raw response for inspection.

    Mirrors `extract.dump_error` but adapted to OpenAI's response shape
    (string content rather than a structured response object — we capture the
    raw JSON string the model emitted, when available).
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    err_path = out_dir / "error.json"
    err_path.write_text(
        json.dumps(
            {
                "exception_type": type(exc).__name__,
                "exception_repr": repr(exc),
                "raw_response": raw_response,
            },
            indent=2,
        )
    )
    return err_path
