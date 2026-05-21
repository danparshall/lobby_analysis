"""Tier-0 direct-read smoke test (Claude + GPT side-by-side).

See `docs/active/extraction-harness-brainstorm/plans/20260518_tier_0_direct_read_smoke_test.md`
for the full plan and the originating convo
`docs/active/extraction-harness-brainstorm/convos/20260518_tier_0_execution_pivot_to_direct_read.md`
for why this script exists in the shape it does.

Architecture: one API call per model, per chunk. The OH 2025 statute lives in
the cached system prompt; the per-chunk user message lists the questions; the
scorer emits `record_cell` (with free-text `cited_section` + 1-sentence
`justification` for downstream verifier provenance) or `record_unscoreable_cell`.

Single-file by design (YAGNI per the originating convo) — no new packaged
module. Parser tests load this file via `importlib.util` so the file stays
script-shaped while still being testable.
"""

from __future__ import annotations

import decimal
import json
from dataclasses import dataclass
from typing import Any, Literal

# ---------------------------------------------------------------------------
# Shared JSON Schemas — one source of truth, two SDK wrappers below.
# Anthropic puts schema under `input_schema`; OpenAI under `function.parameters`.
# ---------------------------------------------------------------------------

RECORD_CELL_INPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "row_id": {
            "type": "string",
            "description": "Compendium row id (one of the chunk's row_ids).",
        },
        "axis": {
            "type": "string",
            "enum": ["legal", "practical"],
        },
        "value": {
            # Loose JSON value; the script-side adapter validates per-cell-class
            # after registry lookup (some cell types take dicts, not scalars).
            "oneOf": [
                {"type": "number"},
                {"type": "integer"},
                {"type": "string"},
                {"type": "boolean"},
                {"type": "array"},
                {"type": "object"},
                {"type": "null"},
            ],
        },
        "condition_text": {"type": ["string", "null"]},
        "confidence": {
            "type": "string",
            "enum": ["high", "medium", "low"],
        },
        "cited_section": {
            "type": "string",
            "description": (
                "Free-text statute section reference, e.g. '§101.85(B)(2)' or "
                "'section 101.85 of the Revised Code'. The downstream verifier "
                "reads this section and rules on whether it actually supports the value."
            ),
        },
        "justification": {
            "type": "string",
            "description": (
                "One sentence explaining how the cited section supports the value. "
                "Used by the downstream verifier."
            ),
        },
    },
    "required": [
        "row_id",
        "axis",
        "value",
        "confidence",
        "cited_section",
        "justification",
    ],
}

RECORD_UNSCOREABLE_INPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "row_id": {"type": "string"},
        "axis": {
            "type": "string",
            "enum": ["legal", "practical"],
        },
        "reason": {
            "type": "string",
            "description": (
                "Why this cell could not be scored from the bundle "
                "(e.g., 'penalty schedule referenced but §307.99 not included')."
            ),
        },
    },
    "required": ["row_id", "axis", "reason"],
}


# ---------------------------------------------------------------------------
# SDK wrappers — same logical tool, two wire formats.
# ---------------------------------------------------------------------------

_RECORD_CELL_DESCRIPTION = (
    "Record a typed answer for one compendium cell. Call this once per "
    "(row_id, axis) you can answer. Cite the specific statute section that "
    "supports the value; a one-sentence justification will be checked by a "
    "downstream verifier reading that section."
)

_RECORD_UNSCOREABLE_DESCRIPTION = (
    "Record that a compendium cell cannot be answered from the bundled "
    "statute text (e.g., the law references a penalty schedule in a "
    "different chapter that isn't shown). Provide a brief reason. "
    "Do not guess."
)


ANTHROPIC_TOOLS: list[dict[str, Any]] = [
    {
        "name": "record_cell",
        "description": _RECORD_CELL_DESCRIPTION,
        "input_schema": RECORD_CELL_INPUT_SCHEMA,
    },
    {
        "name": "record_unscoreable_cell",
        "description": _RECORD_UNSCOREABLE_DESCRIPTION,
        "input_schema": RECORD_UNSCOREABLE_INPUT_SCHEMA,
    },
]


OPENAI_TOOLS: list[dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "record_cell",
            "description": _RECORD_CELL_DESCRIPTION,
            "parameters": RECORD_CELL_INPUT_SCHEMA,
        },
    },
    {
        "type": "function",
        "function": {
            "name": "record_unscoreable_cell",
            "description": _RECORD_UNSCOREABLE_DESCRIPTION,
            "parameters": RECORD_UNSCOREABLE_INPUT_SCHEMA,
        },
    },
]


KNOWN_TOOL_NAMES: frozenset[str] = frozenset({"record_cell", "record_unscoreable_cell"})


# ---------------------------------------------------------------------------
# Parser — returns `(tool_name, input_dict)` pairs, SDK-agnostic.
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ParsedToolCall:
    """One tool invocation pulled out of either SDK's response.

    `tool_name` is the model-emitted name (NOT yet validated against
    `KNOWN_TOOL_NAMES` — the caller decides whether to log+skip unknowns
    or treat them as fatal).

    `arguments` is the parsed argument dict — for OpenAI this means
    `json.loads`ing the wire-format string; for Anthropic the SDK already
    delivers a dict.
    """

    tool_name: str
    arguments: dict[str, Any]


def _attr_or_key(obj: Any, name: str) -> Any:
    """Read either attribute (SDK objects) or key (test fixtures / raw dicts).

    SDK responses ship Pydantic-shaped objects; tests pass plain dicts or
    SimpleNamespace. Supporting both keeps the parser usable in both worlds
    without forcing tests to construct full SDK types.
    """
    if isinstance(obj, dict):
        return obj.get(name)
    return getattr(obj, name, None)


def parse_anthropic_response(response: Any) -> list[ParsedToolCall]:
    """Extract tool calls from an Anthropic Messages API response.

    Walks `response.content` for `tool_use` blocks. Raises `ValueError` if
    a tool_use block is missing required wire fields — that's a contract
    break worth surfacing, not silently dropping.
    """
    content = _attr_or_key(response, "content")
    if content is None:
        raise ValueError("Anthropic response has no `.content`")
    calls: list[ParsedToolCall] = []
    for block in content:
        block_type = _attr_or_key(block, "type")
        if block_type != "tool_use":
            continue
        name = _attr_or_key(block, "name")
        arguments = _attr_or_key(block, "input")
        if name is None or arguments is None:
            raise ValueError(
                f"Anthropic tool_use block missing name/input: {block!r}"
            )
        if not isinstance(arguments, dict):
            raise ValueError(
                f"Anthropic tool_use `input` should be a dict, got {type(arguments).__name__}"
            )
        calls.append(ParsedToolCall(tool_name=name, arguments=dict(arguments)))
    return calls


def parse_openai_response(response: Any) -> list[ParsedToolCall]:
    """Extract tool calls from an OpenAI chat.completions API response.

    Walks `response.choices[0].message.tool_calls`. Each call has
    `.function.name` and `.function.arguments` (a JSON string). Raises
    `json.JSONDecodeError` on malformed argument JSON — silently dropping a
    malformed tool call would hide a real model failure.
    """
    choices = _attr_or_key(response, "choices")
    if not choices:
        raise ValueError("OpenAI response has no choices")
    message = _attr_or_key(choices[0], "message")
    if message is None:
        raise ValueError("OpenAI response choice missing `.message`")
    tool_calls = _attr_or_key(message, "tool_calls") or []
    calls: list[ParsedToolCall] = []
    for tc in tool_calls:
        function = _attr_or_key(tc, "function")
        if function is None:
            raise ValueError(f"OpenAI tool_call missing `.function`: {tc!r}")
        name = _attr_or_key(function, "name")
        arguments_json = _attr_or_key(function, "arguments")
        if name is None or arguments_json is None:
            raise ValueError(
                f"OpenAI tool_call missing name/arguments: {tc!r}"
            )
        # Per the OpenAI contract, `arguments` is always a JSON-encoded string.
        # Let json.loads raise on malformed — surfacing the failure beats
        # dropping the call silently.
        arguments = json.loads(arguments_json)
        if not isinstance(arguments, dict):
            raise ValueError(
                f"OpenAI tool_call arguments should decode to a dict, "
                f"got {type(arguments).__name__}"
            )
        calls.append(ParsedToolCall(tool_name=name, arguments=arguments))
    return calls


def parse_response(
    response: Any,
    sdk: Literal["anthropic", "openai"],
) -> list[ParsedToolCall]:
    """Dispatch to the per-SDK parser. Single entry point for the script."""
    if sdk == "anthropic":
        return parse_anthropic_response(response)
    if sdk == "openai":
        return parse_openai_response(response)
    raise ValueError(f"Unknown sdk: {sdk!r}")


# ---------------------------------------------------------------------------
# Step 4 — dispatch the smoke run.
#
# Below is the production path: load the OH 2025 statute bundle, build the
# system + user messages, dispatch both models, parse + instantiate cells,
# save raw + parsed outputs, print a side-by-side comparison, capture
# cost/wall-clock. Single-file by design; the parser tests above don't
# touch any of this.
# ---------------------------------------------------------------------------

import hashlib
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path


# Constants — match the plan's scope (one chunk, one state, one vintage).
_CHUNK_ID = "enforcement_and_audits"
_STATE_ABBR = "OH"
_VINTAGE_YEAR = 2025
_ANTHROPIC_MODEL = "claude-opus-4-7"
_OPENAI_MODEL = "gpt-5.2-2025-12-11"
_ORIGINATING_CONVO = "convos/20260518_tier_0_execution_pivot_to_direct_read.md"

# Paths — relative to the worktree root. The script is run from the worktree
# root via `uv run python scripts/tier_0_direct_read_smoke.py`.
_WORKTREE_ROOT = Path(__file__).resolve().parents[1]
_STATUTE_BUNDLE_DIR = _WORKTREE_ROOT / "data" / "statutes" / _STATE_ABBR / str(_VINTAGE_YEAR) / "sections"
_RESULTS_DIR = _WORKTREE_ROOT / "docs" / "active" / "extraction-harness-brainstorm" / "results"
_RESULTS_DATE_PREFIX = "20260518"  # planning date per the originating convo

# Approximate per-MTok pricing. The personal_info.md table is dated March
# 2026 and lists opus-4-6 / sonnet-4-6; opus-4-7 pricing may differ. These
# numbers are best-effort and only feed the $1/$5 ceiling check + a printed
# estimate — the writeup should re-verify if cost matters for the verdict.
_PRICING_USD_PER_MTOK: dict[str, dict[str, float]] = {
    "claude-opus-4-7": {"input": 5.00, "output": 25.00},
    "gpt-5.2-2025-12-11": {"input": 1.75, "output": 14.00},
}
_PER_CALL_COST_CEILING_USD = 1.00


@dataclass(frozen=True)
class ModelRun:
    """Bundles everything captured from one model dispatch.

    `parsed_calls` is the parser output (SDK-agnostic). `instantiated_cells`
    and `unscoreable_emissions` are the post-registry result; `errors` captures
    cells that failed to type-check.
    """

    sdk: Literal["anthropic", "openai"]
    model: str
    response_payload: dict[str, Any]  # serialized response for the raw file
    parsed_calls: list[ParsedToolCall]
    instantiated_cells: list[dict[str, Any]]  # each: cell.model_dump() + cited_section + justification
    unscoreable_emissions: list[dict[str, Any]]
    errors: list[dict[str, Any]]
    wall_clock_seconds: float
    usage: dict[str, Any]
    cost_usd_estimate: float


# ---------------------------------------------------------------------------
# Statute bundle loader
# ---------------------------------------------------------------------------


def load_statute_bundle(bundle_dir: Path) -> tuple[str, list[str]]:
    """Concatenate every ``.txt`` file under ``bundle_dir`` with header dividers.

    Returns (concatenated_text, filenames). Header divider format makes it easy
    for the model to cite a specific section by filename if it wants to.
    """
    if not bundle_dir.exists():
        raise FileNotFoundError(
            f"Statute bundle directory does not exist: {bundle_dir}. "
            f"Either the data symlink is missing or this vintage is not on this machine."
        )
    files = sorted(p for p in bundle_dir.iterdir() if p.suffix == ".txt")
    if not files:
        raise FileNotFoundError(f"No .txt files under {bundle_dir}")
    parts: list[str] = []
    for f in files:
        parts.append(f"\n\n=== {f.name} ===\n\n")
        parts.append(f.read_text(encoding="utf-8"))
    return "".join(parts), [f.name for f in files]


# ---------------------------------------------------------------------------
# Prompt assembly
# ---------------------------------------------------------------------------


_SYSTEM_PROMPT_TEMPLATE = """\
You are a legal analyst extracting structured answers from US state lobbying disclosure law. \
You will be shown the full statute text for one state-vintage and asked to answer specific \
compendium questions about that law.

For each question, emit `record_cell` with the typed answer, the specific section that supports \
it, and a one-sentence justification.

If a question's answer requires information not present in the bundled statute text (e.g., the \
law references a penalty schedule in a different chapter that isn't shown), emit \
`record_unscoreable_cell` with a brief reason. Do not guess.

Your response will be independently verified by another model reading the cited section. Cite \
precisely.

=== STATUTE TEXT FOLLOWS ===

{statute_text}
"""


def compose_system_prompt(statute_text: str) -> str:
    """Substitute the statute text into the system-prompt template."""
    return _SYSTEM_PROMPT_TEMPLATE.format(statute_text=statute_text)


def render_chunk_roster(chunk) -> str:  # type: ignore[no-untyped-def]
    """Render the chunk's cells as a bulleted roster for the user message.

    Each line names the row_id, axis, and the expected_cell_class so the model
    has the value type in front of it.
    """
    lines = [f"Answer all {len(chunk.cell_specs)} cells for chunk `{chunk.chunk_id}` ({chunk.topic}):"]
    for cs in chunk.cell_specs:
        lines.append(
            f"- row_id={cs.row_id!r}, axis={cs.axis!r}, "
            f"expected_cell_class={cs.expected_cell_class.__name__}"
        )
    lines.append("")
    lines.append(
        "Emit one `record_cell` call per (row_id, axis) you can answer with the "
        "statute text alone. Emit `record_unscoreable_cell` if the answer requires "
        "out-of-bundle cross-references."
    )
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Cell instantiation — typed values from the loose-JSON `value` field.
# ---------------------------------------------------------------------------


_INT_VALUED_CELL_NAMES: frozenset[str] = frozenset(
    {"IntCell", "GradedIntCell", "BoundedIntCell"}
)


def _coerce_scalar_value(cls: type, raw_value: Any) -> Any:
    """Coerce a JSON-string scalar to the Python type ``cls`` expects.

    Tier-0 surfaced models emitting numeric answers as quoted JSON strings
    (``"2"`` for a GradedIntCell); ``CompendiumCell`` runs Pydantic in strict
    mode, which rejects a ``str`` for an ``int`` / ``float`` / ``Decimal`` /
    ``bool`` field. This keys on the cell class and coerces a ``str`` to the
    field's target type. Non-string values pass through untouched.

    A string that cannot be cleanly coerced raises ``ValueError`` — the caller
    records it in the ``errors`` list rather than swallowing it (per plan).

    Note: ``DecimalCell.value`` is ``Decimal | None``; under strict mode a
    ``float`` would itself fail validation, so the coercion target is
    ``Decimal`` (not ``float`` as the Tier-1 plan's prose says).
    """
    if not isinstance(raw_value, str):
        return raw_value
    name = cls.__name__
    if name in _INT_VALUED_CELL_NAMES:
        try:
            return int(raw_value)
        except ValueError as exc:
            raise ValueError(f"{name}: cannot coerce {raw_value!r} to int") from exc
    if name == "FloatCell":
        try:
            return float(raw_value)
        except ValueError as exc:
            raise ValueError(f"{name}: cannot coerce {raw_value!r} to float") from exc
    if name == "DecimalCell":
        try:
            return decimal.Decimal(raw_value)
        except decimal.InvalidOperation as exc:
            raise ValueError(
                f"{name}: cannot coerce {raw_value!r} to Decimal"
            ) from exc
    if name == "BinaryCell":
        low = raw_value.strip().lower()
        if low == "true":
            return True
        if low == "false":
            return False
        raise ValueError(f"BinaryCell: cannot coerce {raw_value!r} to bool")
    # String-typed cells (EnumCell / FreeTextCell / SectorClassificationCell /
    # UpdateCadenceCell): a JSON string is already the field's target type.
    return raw_value


def _instantiate_cell(spec: Any, arguments: dict[str, Any]) -> dict[str, Any]:
    """Build a typed CompendiumCell + wrap with cited_section + justification.

    Per the plan's chosen Q3 resolution (option a), the wrapper dict is the
    least-invasive shape — leaves ``CompendiumCell`` itself unchanged.
    """
    # Local import — chunks_v2 / models_v2 are heavy and there's no need to
    # pay the cost at script-import time (the parser tests don't need them).
    from lobby_analysis.models_v2 import (
        BinaryCell,
        BoundedIntCell,
        CountWithFTECell,
        DecimalCell,
        EnumCell,
        EnumSetCell,
        EnumSetWithAmountsCell,
        FloatCell,
        FreeTextCell,
        GradedIntCell,
        IntCell,
        SectorClassificationCell,
        TimeSpentCell,
        TimeThresholdCell,
        UpdateCadenceCell,
    )

    cls = spec.expected_cell_class
    raw_value = arguments.get("value")
    common = {
        "cell_id": (spec.row_id, spec.axis),
        "conditional": arguments.get("condition_text") is not None,
        "condition_text": arguments.get("condition_text"),
        "confidence": arguments.get("confidence"),
    }

    scalar_value_cells = {
        BinaryCell,
        BoundedIntCell,
        DecimalCell,
        EnumCell,
        EnumSetCell,
        FloatCell,
        FreeTextCell,
        GradedIntCell,
        IntCell,
        SectorClassificationCell,
        UpdateCadenceCell,
    }
    dict_shape_cells = {
        CountWithFTECell,
        EnumSetWithAmountsCell,
        TimeSpentCell,
        TimeThresholdCell,
    }

    if cls in scalar_value_cells:
        # EnumSetCell takes a frozenset; the model emits a JSON array.
        if cls is EnumSetCell and isinstance(raw_value, list):
            raw_value = frozenset(raw_value)
        else:
            # Coerce JSON-string scalars to the field's target type — models
            # sometimes emit numeric/boolean answers as quoted strings, which
            # Pydantic strict mode rejects (Tier-0 criterion-5 failure).
            raw_value = _coerce_scalar_value(cls, raw_value)
        cell = cls(value=raw_value, **common)
    elif cls in dict_shape_cells:
        if not isinstance(raw_value, dict):
            raise TypeError(
                f"{cls.__name__} expects dict-shaped `value`, got "
                f"{type(raw_value).__name__}"
            )
        kwargs = dict(raw_value)
        if cls is EnumSetWithAmountsCell and isinstance(kwargs.get("value"), list):
            kwargs["value"] = frozenset(kwargs["value"])
        cell = cls(**kwargs, **common)
    else:
        raise TypeError(f"Unsupported cell class: {cls.__name__}")

    return {
        "cell": cell.model_dump(mode="json"),
        "cell_class": cls.__name__,
        "cited_section": arguments.get("cited_section"),
        "justification": arguments.get("justification"),
    }


# ---------------------------------------------------------------------------
# Dispatch — Anthropic + OpenAI.
# ---------------------------------------------------------------------------


def dispatch_anthropic(system_prompt: str, user_message: str) -> tuple[Any, float]:
    """Send the message to Anthropic and return (response, wall_clock_seconds).

    System prompt ships as a single cache-controlled block so the statute text
    is cached on the first call (cheap for the rest of Tier-1).
    """
    import anthropic

    client = anthropic.Anthropic()
    started = time.monotonic()
    response = client.messages.create(
        model=_ANTHROPIC_MODEL,
        max_tokens=4096,
        system=[
            {
                "type": "text",
                "text": system_prompt,
                "cache_control": {"type": "ephemeral"},
            }
        ],
        tools=ANTHROPIC_TOOLS,
        messages=[{"role": "user", "content": user_message}],
    )
    elapsed = time.monotonic() - started
    return response, elapsed


def dispatch_openai(system_prompt: str, user_message: str) -> tuple[Any, float]:
    """Send the message to OpenAI and return (response, wall_clock_seconds).

    OpenAI auto-caches prompts ≥1024 tokens; no explicit cache_control needed.
    """
    import openai

    client = openai.OpenAI()
    started = time.monotonic()
    response = client.chat.completions.create(
        model=_OPENAI_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        tools=OPENAI_TOOLS,
        max_completion_tokens=4096,
    )
    elapsed = time.monotonic() - started
    return response, elapsed


# ---------------------------------------------------------------------------
# Cost + usage extraction.
# ---------------------------------------------------------------------------


def _serialize_usage(usage: Any) -> dict[str, Any]:
    """Pull a JSON-serializable dict out of the SDK's usage object."""
    if usage is None:
        return {}
    if hasattr(usage, "model_dump"):
        return usage.model_dump()
    if isinstance(usage, dict):
        return dict(usage)
    # Fallback for SimpleNamespace-shaped fixtures and arbitrary attr objects.
    return {k: v for k, v in vars(usage).items() if not k.startswith("_")}


def _estimate_cost_usd(model: str, usage: dict[str, Any]) -> float:
    """Best-effort dollar estimate from usage tokens.

    Reads `input_tokens` + `output_tokens` (Anthropic shape) or
    `prompt_tokens` + `completion_tokens` (OpenAI shape). Returns 0.0 when the
    fields aren't present — surface a warning instead of failing the run.
    """
    pricing = _PRICING_USD_PER_MTOK.get(model)
    if pricing is None:
        return 0.0
    input_tokens = usage.get("input_tokens") or usage.get("prompt_tokens") or 0
    output_tokens = usage.get("output_tokens") or usage.get("completion_tokens") or 0
    return (input_tokens / 1_000_000) * pricing["input"] + (output_tokens / 1_000_000) * pricing["output"]


# ---------------------------------------------------------------------------
# Result writing.
# ---------------------------------------------------------------------------


def _save_json(path: Path, payload: dict[str, Any]) -> None:
    """Write payload to ``path`` with the structured provenance wrapper.

    JSON doesn't support markdown-style ``<!-- ... -->`` comments, so the
    provenance the plan calls for lives as a sibling ``provenance`` field on
    the top-level object.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _build_provenance(model: str, prompt_sha256: str) -> dict[str, Any]:
    """Provenance block embedded in every results JSON."""
    return {
        "originating_convo": _ORIGINATING_CONVO,
        "script": "scripts/tier_0_direct_read_smoke.py",
        "model": model,
        "chunk_id": _CHUNK_ID,
        "state_abbr": _STATE_ABBR,
        "vintage_year": _VINTAGE_YEAR,
        "prompt_sha256": prompt_sha256,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }


def _serialize_response(response: Any) -> dict[str, Any]:
    """Convert a Pydantic-shaped SDK response into a JSON-serializable dict."""
    if hasattr(response, "model_dump"):
        return response.model_dump(mode="json")
    if isinstance(response, dict):
        return response
    raise TypeError(f"Cannot serialize response of type {type(response).__name__}")


# ---------------------------------------------------------------------------
# Side-by-side comparison printer.
# ---------------------------------------------------------------------------


def _format_run_summary(run: ModelRun) -> str:
    """One-paragraph header per model run."""
    return (
        f"### {run.sdk}/{run.model}\n"
        f"- wall_clock: {run.wall_clock_seconds:.2f}s\n"
        f"- usage: {run.usage}\n"
        f"- cost_estimate_usd: ${run.cost_usd_estimate:.4f}\n"
        f"- parsed_tool_calls: {len(run.parsed_calls)}\n"
        f"- typed_cells: {len(run.instantiated_cells)}\n"
        f"- unscoreable: {len(run.unscoreable_emissions)}\n"
        f"- errors: {len(run.errors)}"
    )


def _index_cells_by_cell_id(run: ModelRun) -> dict[tuple[str, str], dict[str, Any]]:
    """Build a (row_id, axis) -> wrapped-cell-dict index for side-by-side output."""
    index: dict[tuple[str, str], dict[str, Any]] = {}
    for wrapped in run.instantiated_cells:
        cell_id = tuple(wrapped["cell"]["cell_id"])
        index[(cell_id[0], cell_id[1])] = wrapped
    return index


def print_side_by_side(runs: list[ModelRun], chunk) -> None:  # type: ignore[no-untyped-def]
    """Print a per-cell side-by-side comparison across models to stdout."""
    print("\n=== Side-by-side per-cell comparison ===\n")
    for run in runs:
        print(_format_run_summary(run))
        print()

    indices = {run.model: _index_cells_by_cell_id(run) for run in runs}
    for cs in chunk.cell_specs:
        key = (cs.row_id, cs.axis)
        print(f"\n--- ({cs.row_id}, {cs.axis})  [{cs.expected_cell_class.__name__}] ---")
        for run in runs:
            wrapped = indices[run.model].get(key)
            if wrapped is None:
                print(f"  [{run.model}] (no record_cell emitted; check unscoreable list)")
                continue
            value = wrapped["cell"].get("value")
            print(f"  [{run.model}] value={value!r}")
            print(f"  [{run.model}] cited_section={wrapped.get('cited_section')!r}")
            print(f"  [{run.model}] justification={wrapped.get('justification')!r}")


# ---------------------------------------------------------------------------
# Pre-flight + main.
# ---------------------------------------------------------------------------


def _preflight() -> dict[str, str]:
    """Verify keys + paths before any API call. Returns env keys if all good.

    Raises SystemExit (via sys.exit(2)) with a clear message if any check fails.
    Used as a fail-fast guard so a missing key never burns API spend.
    """
    missing = []
    keys = {}
    for var in ("ANTHROPIC_API_KEY", "OPENAI_API_KEY"):
        val = os.environ.get(var)
        if not val:
            missing.append(var)
        else:
            keys[var] = val
    if missing:
        print(
            "ERROR: required environment variables are unset: "
            f"{', '.join(missing)}.\n"
            "Tier-0 dispatches both Anthropic and OpenAI; both keys must be "
            "exported before running this script. Aborting before any API call.",
            file=sys.stderr,
        )
        sys.exit(2)

    if not _STATUTE_BUNDLE_DIR.exists():
        print(
            f"ERROR: statute bundle directory not found: {_STATUTE_BUNDLE_DIR}\n"
            f"Either the `data/statutes` symlink is missing in this worktree "
            f"or OH/{_VINTAGE_YEAR}/sections/ does not exist on this machine. "
            f"Per the plan, stop and surface — do not substitute another vintage.",
            file=sys.stderr,
        )
        sys.exit(2)

    return keys


def main() -> int:
    """Run the smoke test end-to-end. Returns process exit code."""
    _preflight()

    # Lazy import: chunks_v2 + registry are heavy modules; we don't want them
    # at script-import time (the parser tests load this file via importlib).
    from lobby_analysis.chunks_v2 import build_chunks
    from lobby_analysis.models_v2 import build_cell_spec_registry

    chunks = {c.chunk_id: c for c in build_chunks()}
    if _CHUNK_ID not in chunks:
        print(f"ERROR: chunk {_CHUNK_ID!r} not found in CHUNKS_V2 manifest.", file=sys.stderr)
        return 2
    chunk = chunks[_CHUNK_ID]
    registry = build_cell_spec_registry()

    statute_text, statute_filenames = load_statute_bundle(_STATUTE_BUNDLE_DIR)
    system_prompt = compose_system_prompt(statute_text)
    prompt_sha256 = hashlib.sha256(system_prompt.encode("utf-8")).hexdigest()
    user_message = render_chunk_roster(chunk)

    estimated_tokens = len(system_prompt) // 4
    print(f"Statute files: {len(statute_filenames)}")
    print(f"System prompt: {len(system_prompt)} chars, ~{estimated_tokens} tokens")
    print(f"Prompt sha256: {prompt_sha256}")
    print(f"Chunk cells: {len(chunk.cell_specs)}")

    runs: list[ModelRun] = []

    for sdk, model, dispatcher in [
        ("anthropic", _ANTHROPIC_MODEL, dispatch_anthropic),
        ("openai", _OPENAI_MODEL, dispatch_openai),
    ]:
        print(f"\nDispatching {sdk}/{model}...")
        try:
            response, elapsed = dispatcher(system_prompt, user_message)
        except Exception as exc:  # noqa: BLE001 — capture-and-continue per the plan
            print(f"ERROR: {sdk} dispatch failed: {exc!r}", file=sys.stderr)
            continue

        usage = _serialize_usage(getattr(response, "usage", None))
        cost = _estimate_cost_usd(model, usage)
        if cost > _PER_CALL_COST_CEILING_USD:
            print(
                f"ABORT: {sdk}/{model} estimated cost ${cost:.4f} exceeded ceiling "
                f"${_PER_CALL_COST_CEILING_USD}. Stop and investigate before continuing.",
                file=sys.stderr,
            )
            return 3

        parsed_calls = parse_response(response, sdk)  # type: ignore[arg-type]
        instantiated: list[dict[str, Any]] = []
        unscoreable: list[dict[str, Any]] = []
        errors: list[dict[str, Any]] = []
        for call in parsed_calls:
            if call.tool_name == "record_cell":
                key = (call.arguments.get("row_id"), call.arguments.get("axis"))
                spec = registry.get(key)
                if spec is None:
                    errors.append({"reason": "unknown_row_axis", "key": list(key), "arguments": call.arguments})
                    continue
                try:
                    wrapped = _instantiate_cell(spec, call.arguments)
                except Exception as exc:  # noqa: BLE001
                    errors.append({"reason": "instantiation_failed", "key": list(key), "error": repr(exc), "arguments": call.arguments})
                    continue
                instantiated.append(wrapped)
            elif call.tool_name == "record_unscoreable_cell":
                unscoreable.append(call.arguments)
            else:
                errors.append({"reason": "unknown_tool_name", "tool_name": call.tool_name, "arguments": call.arguments})

        run = ModelRun(
            sdk=sdk,  # type: ignore[arg-type]
            model=model,
            response_payload=_serialize_response(response),
            parsed_calls=parsed_calls,
            instantiated_cells=instantiated,
            unscoreable_emissions=unscoreable,
            errors=errors,
            wall_clock_seconds=elapsed,
            usage=usage,
            cost_usd_estimate=cost,
        )
        runs.append(run)

        # Write raw + parsed result files per the plan.
        raw_path = _RESULTS_DIR / f"{_RESULTS_DATE_PREFIX}_tier_0_raw_{sdk}_{_CHUNK_ID}.json"
        parsed_path = _RESULTS_DIR / f"{_RESULTS_DATE_PREFIX}_tier_0_parsed_{sdk}_{_CHUNK_ID}.json"
        _save_json(
            raw_path,
            {
                "provenance": _build_provenance(model, prompt_sha256),
                "wall_clock_seconds": elapsed,
                "usage": usage,
                "cost_usd_estimate": cost,
                "statute_filenames": statute_filenames,
                "response": run.response_payload,
            },
        )
        _save_json(
            parsed_path,
            {
                "provenance": _build_provenance(model, prompt_sha256),
                "instantiated_cells": instantiated,
                "unscoreable_emissions": unscoreable,
                "errors": errors,
            },
        )
        print(f"  wrote {raw_path.relative_to(_WORKTREE_ROOT)}")
        print(f"  wrote {parsed_path.relative_to(_WORKTREE_ROOT)}")

    print_side_by_side(runs, chunk)
    return 0


if __name__ == "__main__":
    sys.exit(main())
