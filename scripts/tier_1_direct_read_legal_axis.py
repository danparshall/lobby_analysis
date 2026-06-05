"""Tier-1 direct-read legal-axis run over the 6 CPI-2015 C11 de-jure chunks.

See `docs/active/extraction-harness-brainstorm/plans/20260520_tier_1_direct_read_legal_axis.md`
for the full plan and `convos/20260520_tier_0_direct_read_execution.md` for the
Tier-0 findings this scales up.

Scales the Tier-0 direct-read smoke into a legal-axis-only run:

- Reuses Tier-0's schemas, SDK tool wrappers, response parser, statute loader,
  `_instantiate_cell`, and cost/usage helpers (imported, not duplicated).
- Filters every chunk's cell roster to ``axis == 'legal'`` before dispatch —
  the practical (de facto) axis is Prong 2's job.
- Dispatches `[claude-opus-4-7, gpt-5.2] x 6 chunks x 3 runs` = 36 calls, with
  per-dispatch checkpoint + resume so a crash never redoes completed work.
- Computes an inter-run agreement metric (sigma_noise = % cells stable across
  the N=3 re-runs) per model.

Deviations from a literal Tier-0 reuse, documented for the writeup:
- Tier-1 owns its dispatch wrappers (Tier-0's hardcoded ``max_tokens=4096``
  was sized for a 4-cell chunk; Tier-1's largest chunk has 30 legal cells, so
  the cap is raised to 16384). Tools/model constants are still reused.
- Tier-1 owns its system prompt (adds the de-jure-only framing + the
  "numeric answers as JSON numbers" nudge from plan Step 2).

Single-file by design (YAGNI), consistent with Tier-0.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import statistics
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Reuse Tier-0 — load the sibling script as a module (it is script-shaped, not
# a package). Imports its schemas / tools / parser / _instantiate_cell /
# statute loader / cost helpers so none of that is duplicated here.
# ---------------------------------------------------------------------------

_WORKTREE_ROOT = Path(__file__).resolve().parents[1]
_TIER_0_PATH = _WORKTREE_ROOT / "scripts" / "tier_0_direct_read_smoke.py"


def _load_tier_0():
    """Load tier_0_direct_read_smoke.py as an importable module (no main())."""
    if "tier_0_direct_read_smoke" in sys.modules:
        return sys.modules["tier_0_direct_read_smoke"]
    spec = importlib.util.spec_from_file_location("tier_0_direct_read_smoke", _TIER_0_PATH)
    assert spec is not None and spec.loader is not None, f"could not load {_TIER_0_PATH}"
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


tier0 = _load_tier_0()


# ---------------------------------------------------------------------------
# Constants — Tier-1 scope.
# ---------------------------------------------------------------------------

# The 6 default chunks dispatched when --chunks is omitted: the CPI-2015 C11
# de-jure items (IND_196/197/199/201/203/207). Resolved in Step 1 of the plan;
# recorded in the writeup.
_DEFAULT_CHUNKS: tuple[str, ...] = (
    "lobbying_definitions",
    "registration_thresholds",
    "registration_mechanics_and_exemptions",
    "lobbyist_spending_report",
    "principal_spending_report",
    "enforcement_and_audits",
)

# Additional chunk_ids accepted as --chunks values (but NOT in the default
# dispatch set). Phase A A2.b (2026-06-05) adds `actor_registration_required`
# — 11 pure-binary rows — as the BinaryCell template verification chunk.
_PHASE_A_EXTRA_CHUNKS: tuple[str, ...] = (
    "actor_registration_required",
)

# Full set of valid --chunks values: defaults + Phase A additions.
_RESOLVED_CHUNKS: tuple[str, ...] = _DEFAULT_CHUNKS + _PHASE_A_EXTRA_CHUNKS

_N_RUNS = 3
_MODELS: tuple[str, ...] = (tier0._ANTHROPIC_MODEL, tier0._OPENAI_MODEL)
_ORIGINATING_CONVO = "convos/20260520_tier_0_direct_read_execution.md"

# Raised from Tier-0's 4096: the 30-cell chunk needs ~10k output tokens at
# Tier-0's observed Claude rate (~335 tok/cell).
_MAX_OUTPUT_TOKENS = 16384

# Results/checkpoint base. The per-run directory is keyed by <STATE>_<VINTAGE>
# under this base (see resolve_results_dir) so no two state-vintages share a
# checkpoint directory.
_DEFAULT_RESULTS_BASE = (
    _WORKTREE_ROOT / "docs" / "active" / "wi-tier1-direct-read" / "results" / "tier_1"
)


def resolve_bundle_dir(state: str, vintage: int) -> Path:
    """The statute bundle directory for one (state, vintage)."""
    return _WORKTREE_ROOT / "data" / "statutes" / state / str(vintage) / "sections"


def resolve_results_dir(
    state: str, vintage: int, results_base: Path | None = None
) -> Path:
    """The state-keyed results/checkpoint directory for one (state, vintage).

    Keying by ``<STATE>_<VINTAGE>`` is the correctness-critical fix: a run for
    one state can never write into, or resume-skip against, another state's
    result files. The previously un-keyed shared directory let a second
    state's run skip every dispatch on the first state's checkpoints and emit
    the wrong state's answers under the new label.
    """
    base = Path(results_base) if results_base is not None else _DEFAULT_RESULTS_BASE
    return base / f"{state}_{vintage}"


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse --state/--vintage. Both required — no default OH re-run by accident."""
    parser = argparse.ArgumentParser(
        description=(
            "Tier-1 direct-read legal-axis extraction for one (state, vintage). "
            "Dispatches both models x 6 chunks x N runs with per-dispatch "
            "checkpoint/resume into a state-keyed results directory."
        )
    )
    parser.add_argument(
        "--state",
        required=True,
        help="Two-letter state abbreviation, e.g. WI (matches data/statutes/<STATE>/).",
    )
    parser.add_argument(
        "--vintage",
        required=True,
        type=int,
        help="Statute vintage year, e.g. 2025 (matches data/statutes/<STATE>/<VINTAGE>/).",
    )
    parser.add_argument(
        "--chunks",
        nargs="+",
        default=None,
        help=(
            "Optional subset of chunk_ids to dispatch (one or more). When "
            "omitted, all 6 chunks dispatch (current behavior). Use for "
            "Phase B Ralph per-iteration single-chunk dispatches. Valid "
            f"chunk_ids: {', '.join(_RESOLVED_CHUNKS)}."
        ),
    )
    return parser.parse_args(argv)


def resolve_active_chunks(chunks_arg: list[str] | None) -> tuple[str, ...]:
    """Resolve the --chunks argument to a tuple of chunk_ids to dispatch.

    If ``chunks_arg`` is ``None`` (flag omitted), returns ``_DEFAULT_CHUNKS``
    (the original 6 CPI-2015 C11 chunks) — backward-compatible with the
    pre-Phase-B behavior. If ``chunks_arg`` is provided, validates each
    entry against ``_RESOLVED_CHUNKS`` (defaults + Phase A extras) and
    returns only those, preserving caller-specified order. An unknown
    chunk_id raises ``SystemExit`` with a message naming the bad chunk AND
    the full valid list — silent fall-through to "all chunks" is the
    regression to prevent.
    """
    if not chunks_arg:
        return _DEFAULT_CHUNKS
    valid = set(_RESOLVED_CHUNKS)
    unknown = [c for c in chunks_arg if c not in valid]
    if unknown:
        raise SystemExit(
            f"ERROR: unknown chunk_id(s): {', '.join(unknown)}. "
            f"Valid chunk_ids: {', '.join(_RESOLVED_CHUNKS)}."
        )
    return tuple(chunks_arg)

# Per-call abort retained from Tier-0; session ceiling raised to $10 for 36
# calls (~$2-4 expected). Both confirmed with the user 2026-05-20.
_PER_CALL_COST_CEILING_USD = 1.00
_SESSION_COST_CEILING_USD = 10.00


_SYSTEM_PROMPT_TEMPLATE = """\
You are a legal analyst extracting structured answers from US state lobbying \
disclosure law. You will be shown the full statute text for one state-vintage \
and asked to answer specific compendium questions about that law.

Every question in this task is a DE JURE question: it asks what the statute \
REQUIRES, PERMITS, or DEFINES — never what the state does in practice. Answer \
strictly from the statute text; do not infer real-world behavior.

For each question, emit `record_cell` with the typed answer, the specific \
section that supports it, and a one-sentence justification. Emit numeric \
answers as JSON numbers, not quoted strings (e.g. 50, not "50"); emit boolean \
answers as JSON true / false.

If a question's answer requires information not present in the bundled statute \
text (e.g. the law references a schedule in a chapter that isn't shown), emit \
`record_unscoreable_cell` with a brief reason. Do not guess.

Your response will be independently verified by another model reading the \
cited section. Cite precisely.

=== STATUTE TEXT FOLLOWS ===

{statute_text}
"""


# ---------------------------------------------------------------------------
# Tool schemas — tier-1 owns its own variants of record_cell and
# record_unscoreable_cell with the parameter `handle` in place of `row_id`.
# Per the 2026-06-04 wide-pass design (convo
# `20260604_wide_pass_yaml_sidecar_design`), opaque per-chunk handles
# replace any leakage of compendium row_ids into the model's view; tier-0's
# row-id-keyed tool schemas stay untouched (they belong to the archived
# smoke pipeline). The tool *names* (`record_cell`,
# `record_unscoreable_cell`) are deliberately the same as tier-0's so the
# shared `parse_response` / `_instantiate_cell` helpers keep working.
# ---------------------------------------------------------------------------


RECORD_CELL_INPUT_SCHEMA_HANDLE: dict[str, Any] = {
    "type": "object",
    "properties": {
        "handle": {
            "type": "string",
            "description": (
                "Opaque per-chunk row handle (e.g., 'row_001'). Use exactly "
                "the handle string listed for the row you are answering — "
                "the runtime maps the handle back to a compendium row "
                "internally."
            ),
        },
        "axis": {
            "type": "string",
            "enum": ["legal", "practical"],
        },
        "value": {
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
                "Free-text statute section reference, e.g. '§101.85(B)(2)'. "
                "The downstream verifier reads this section and rules on "
                "whether it actually supports the value."
            ),
        },
        "justification": {
            "type": "string",
            "description": (
                "One sentence explaining how the cited section supports the "
                "value. Used by the downstream verifier."
            ),
        },
    },
    "required": [
        "handle",
        "axis",
        "value",
        "confidence",
        "cited_section",
        "justification",
    ],
}


RECORD_UNSCOREABLE_INPUT_SCHEMA_HANDLE: dict[str, Any] = {
    "type": "object",
    "properties": {
        "handle": {"type": "string"},
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
    "required": ["handle", "axis", "reason"],
}


_RECORD_CELL_DESCRIPTION_HANDLE = (
    "Record a typed answer for one compendium cell. Call this once per "
    "(handle, axis) you can answer. Cite the specific statute section that "
    "supports the value; a one-sentence justification will be checked by a "
    "downstream verifier reading that section."
)


_RECORD_UNSCOREABLE_DESCRIPTION_HANDLE = (
    "Record that a compendium cell cannot be answered from the bundled "
    "statute text (e.g., the law references a penalty schedule in a "
    "different chapter that isn't shown). Provide a brief reason. "
    "Do not guess."
)


ANTHROPIC_TOOLS_HANDLE: list[dict[str, Any]] = [
    {
        "name": "record_cell",
        "description": _RECORD_CELL_DESCRIPTION_HANDLE,
        "input_schema": RECORD_CELL_INPUT_SCHEMA_HANDLE,
    },
    {
        "name": "record_unscoreable_cell",
        "description": _RECORD_UNSCOREABLE_DESCRIPTION_HANDLE,
        "input_schema": RECORD_UNSCOREABLE_INPUT_SCHEMA_HANDLE,
    },
]


OPENAI_TOOLS_HANDLE: list[dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "record_cell",
            "description": _RECORD_CELL_DESCRIPTION_HANDLE,
            "parameters": RECORD_CELL_INPUT_SCHEMA_HANDLE,
        },
    },
    {
        "type": "function",
        "function": {
            "name": "record_unscoreable_cell",
            "description": _RECORD_UNSCOREABLE_DESCRIPTION_HANDLE,
            "parameters": RECORD_UNSCOREABLE_INPUT_SCHEMA_HANDLE,
        },
    },
]


# ---------------------------------------------------------------------------
# Step 3 — legal-axis roster filter.
# ---------------------------------------------------------------------------


def build_legal_roster(chunk: Any) -> list[Any]:
    """Return only the ``axis == 'legal'`` cell specs of ``chunk``.

    Mixed chunks contribute only their legal cells; practical (de facto) cells
    belong to Prong 2 and must never be dispatched by this de-jure pipeline.
    Order is preserved.
    """
    return [spec for spec in chunk.cell_specs if spec.axis == "legal"]


def _value_shape_hint(cls: Any) -> str:
    """Roster-line hint naming the JSON-object keys a dict-shape cell expects.

    Empty string for scalar cells. The Tier-1 run surfaced a model emitting a
    bare string for the one dict-shape cell in the legal roster
    (``TimeThresholdCell`` — error class B); naming the keys steers it toward
    a JSON object. Keys are derived from ``model_fields`` minus the common
    ``CompendiumCell`` fields, so the helper generalizes to every dict-shape
    class without a per-class table.
    """
    non_common = [f for f in cls.model_fields if f not in _COMMON_CELL_FIELDS]
    if non_common == ["value"]:
        return ""
    return f" — emit `value` as a JSON object with keys: {', '.join(non_common)}"


def render_legal_roster(
    chunk_id: str, topic: str, legal_specs: list[Any]
) -> tuple[str, dict[str, str]]:
    """Render a legal-only roster as the per-chunk user message.

    Returns ``(message, handle_to_row_id_map)``. The message uses opaque
    per-chunk handles (``row_001``, ``row_002``, …) instead of leaking the
    compendium ``row_id`` into the model's view. The map decodes the
    model's handle-keyed response back to the original row_ids.

    Per convo `20260604_wide_pass_yaml_sidecar_design`: row IDs are
    structurally a lossy compression of the source-author intent and were
    the Pattern A bug surface in the WI dispatch. Suppressing them from the
    model's view is the wide-pass forcing-function for prompt quality —
    prompts cannot lean on row-name semantic content. Each spec's `prompt`
    field (from `compendium/source_quotes.yaml` via the registry) is
    emitted on the continuation line beneath the handle's metadata.
    """
    handle_to_row_id: dict[str, str] = {}
    lines = [
        f"Answer all {len(legal_specs)} DE JURE (legal-axis) cells for chunk "
        f"`{chunk_id}` ({topic}):"
    ]
    for idx, cs in enumerate(legal_specs):
        handle = f"row_{idx + 1:03d}"
        handle_to_row_id[handle] = cs.row_id
        cls = cs.expected_cell_class
        lines.append(
            f"- handle={handle!r}, axis='legal', "
            f"expected_cell_class={cls.__name__}{_value_shape_hint(cls)}"
        )
        prompt = getattr(cs, "prompt", None)
        if prompt:
            lines.append(f"  {prompt}")
    lines.append("")
    lines.append(
        "Emit one `record_cell` call per (handle, axis) you can answer from "
        "the statute text alone. Emit `record_unscoreable_cell` if the answer "
        "needs out-of-bundle cross-references. Every axis here is 'legal'."
    )
    return "\n".join(lines), handle_to_row_id


# ---------------------------------------------------------------------------
# Step 5 — inter-run agreement / sigma_noise.
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class CellOutcome:
    """One run's result for one (row_id, axis) cell.

    ``status`` is one of: ``scored`` (the model emitted record_cell and the
    value instantiated), ``abstained`` (record_unscoreable_cell), ``errored``
    (record_cell emitted but instantiation failed), ``absent`` (no emission).
    ``value`` carries the instantiated value for ``scored`` outcomes only.
    """

    status: str
    value: Any = None


def classify_cell_runs(outcomes: list[CellOutcome]) -> dict[str, Any]:
    """Classify a single cell's N runs into a stability category.

    Returns ``{"stability": str, "n_runs": int, "numeric_spread": dict|None}``.

    - ``stable`` — every run scored the same value, or every run abstained.
    - ``value-unstable`` — every run scored, but the values differ.
    - ``scoreability-unstable`` — some runs scored, some abstained (the
      Tier-0 Claude/GPT divergence, surfaced *within* a single model).
    - ``incomplete`` — at least one run errored or produced no emission;
      not counted toward the sigma_noise stable fraction.
    """
    statuses = [o.status for o in outcomes]
    numeric_spread: dict[str, Any] | None = None

    if any(s in ("errored", "absent") for s in statuses):
        stability = "incomplete"
    elif statuses and all(s == "abstained" for s in statuses):
        stability = "stable"
    elif statuses and all(s == "scored" for s in statuses):
        values = [o.value for o in outcomes]
        first = values[0]
        stability = "stable" if all(v == first for v in values) else "value-unstable"
        numeric = [
            v for v in values if isinstance(v, (int, float)) and not isinstance(v, bool)
        ]
        if len(numeric) == len(values):
            numeric_spread = {
                "min": min(numeric),
                "max": max(numeric),
                "stdev": statistics.stdev(numeric) if len(numeric) > 1 else 0.0,
            }
    else:
        stability = "scoreability-unstable"

    return {
        "stability": stability,
        "n_runs": len(outcomes),
        "numeric_spread": numeric_spread,
    }


def summarize_sigma_noise(
    classifications: dict[Any, dict[str, Any]],
) -> dict[str, Any]:
    """Aggregate per-cell classifications into a model's sigma_noise figure.

    ``sigma_noise`` proxy = ``pct_stable`` = % of cells whose N runs were
    stable. The Ralph loop must not chase differences smaller than this floor.
    """
    n_cells = len(classifications)
    counts: dict[str, int] = {}
    for c in classifications.values():
        counts[c["stability"]] = counts.get(c["stability"], 0) + 1
    n_stable = counts.get("stable", 0)
    return {
        "n_cells": n_cells,
        "n_stable": n_stable,
        "n_value_unstable": counts.get("value-unstable", 0),
        "n_scoreability_unstable": counts.get("scoreability-unstable", 0),
        "n_incomplete": counts.get("incomplete", 0),
        "pct_stable": (100.0 * n_stable / n_cells) if n_cells else 0.0,
    }


_COMMON_CELL_FIELDS = frozenset(
    {"cell_id", "conditional", "condition_text", "confidence", "provenance"}
)


def extract_cell_outcome(
    parsed_result: dict[str, Any], row_id: str, axis: str
) -> CellOutcome:
    """Build a CellOutcome for one (row_id, axis) from one run's saved JSON."""
    for wrapped in parsed_result.get("instantiated_cells", []):
        cell = wrapped.get("cell", {})
        cell_id = list(cell.get("cell_id", []))
        if cell_id[:2] == [row_id, axis]:
            if "value" in cell:
                value: Any = cell["value"]
            else:
                # dict-shape cell (e.g. TimeThresholdCell): the comparable
                # value is the non-common fields.
                value = {
                    k: v for k, v in cell.items() if k not in _COMMON_CELL_FIELDS
                }
            return CellOutcome(status="scored", value=value)
    for emission in parsed_result.get("unscoreable_emissions", []):
        if emission.get("row_id") == row_id and emission.get("axis") == axis:
            return CellOutcome(status="abstained")
    for err in parsed_result.get("errors", []):
        key = list(err.get("key") or [])
        if key[:2] == [row_id, axis]:
            return CellOutcome(status="errored")
    return CellOutcome(status="absent")


# ---------------------------------------------------------------------------
# Step 4 — checkpoint / resume.
# ---------------------------------------------------------------------------


def dispatch_result_path(
    results_dir: Path, model: str, chunk_id: str, run_idx: int
) -> Path:
    """The canonical result-file path for one (model, chunk, run) triple."""
    return Path(results_dir) / f"{model}__{chunk_id}__run{run_idx}.json"


def is_dispatch_done(
    results_dir: Path, model: str, chunk_id: str, run_idx: int
) -> bool:
    """True iff this (model, chunk, run) triple already has a result file."""
    return dispatch_result_path(results_dir, model, chunk_id, run_idx).exists()


# ---------------------------------------------------------------------------
# Step 4 — dispatch wrappers (Tier-1 owns these — see module docstring).
# ---------------------------------------------------------------------------


def _dispatch_anthropic(system_prompt: str, user_message: str) -> tuple[Any, float]:
    """Anthropic dispatch with a cache-controlled statute system block."""
    import anthropic

    client = anthropic.Anthropic()
    started = time.monotonic()
    response = client.messages.create(
        model=tier0._ANTHROPIC_MODEL,
        max_tokens=_MAX_OUTPUT_TOKENS,
        system=[
            {
                "type": "text",
                "text": system_prompt,
                "cache_control": {"type": "ephemeral"},
            }
        ],
        tools=ANTHROPIC_TOOLS_HANDLE,
        messages=[{"role": "user", "content": user_message}],
    )
    return response, time.monotonic() - started


def _dispatch_openai(system_prompt: str, user_message: str) -> tuple[Any, float]:
    """OpenAI dispatch (prompt auto-cached for prompts >= 1024 tokens)."""
    import openai

    client = openai.OpenAI()
    started = time.monotonic()
    response = client.chat.completions.create(
        model=tier0._OPENAI_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        tools=OPENAI_TOOLS_HANDLE,
        max_completion_tokens=_MAX_OUTPUT_TOKENS,
    )
    return response, time.monotonic() - started


_DISPATCHERS: dict[str, tuple[str, Any]] = {
    tier0._ANTHROPIC_MODEL: ("anthropic", _dispatch_anthropic),
    tier0._OPENAI_MODEL: ("openai", _dispatch_openai),
}


# ---------------------------------------------------------------------------
# Step 4 — runner.
# ---------------------------------------------------------------------------


def _preflight(bundle_dir: Path) -> None:
    """Fail fast before any API spend if keys or the statute bundle are absent."""
    missing = [v for v in ("ANTHROPIC_API_KEY", "OPENAI_API_KEY") if not os.environ.get(v)]
    if missing:
        print(
            f"ERROR: required env vars unset: {', '.join(missing)}. "
            "Tier-1 dispatches both models; export both keys. Aborting before "
            "any API call.",
            file=sys.stderr,
        )
        sys.exit(2)
    if not bundle_dir.exists():
        print(
            f"ERROR: statute bundle directory not found: {bundle_dir}. "
            "Stop and surface — do not substitute another vintage.",
            file=sys.stderr,
        )
        sys.exit(2)


def _is_null_freetext_abstention(spec: Any, arguments: dict[str, Any]) -> bool:
    """True for a record_cell whose target is a FreeTextCell and value is null.

    The conditional ``*_other_specification`` rows correctly emit
    ``value: null`` when their cadence condition does not hold, but
    ``FreeTextCell.value`` is a non-optional ``str`` — strict validation
    rejects null. This is error class C: the model is right and the schema
    cannot represent "not applicable." Such a call is routed to an abstention
    rather than recorded as an instantiation error.
    """
    from lobby_analysis.models_v2 import FreeTextCell

    return (
        spec.expected_cell_class is FreeTextCell
        and arguments.get("value") is None
    )


def _parse_and_instantiate(
    response: Any,
    sdk: str,
    registry: dict[Any, Any],
    handle_to_row_id: dict[str, str],
) -> tuple[list[dict], list[dict], list[dict]]:
    """Parse a response into (instantiated_cells, unscoreable, errors).

    The model emits ``record_cell`` / ``record_unscoreable_cell`` calls with
    an opaque per-chunk ``handle`` in place of the (legacy) ``row_id``.
    ``handle_to_row_id`` is the chunk-local map produced by
    ``render_legal_roster``. An emission whose ``handle`` is not in the map
    (unknown handle, missing handle, or model leaking back the actual
    compendium row_id) routes to ``errors`` — never to ``instantiated`` —
    so contract violations are loud.
    """
    instantiated: list[dict] = []
    unscoreable: list[dict] = []
    errors: list[dict] = []
    for call in tier0.parse_response(response, sdk):
        if call.tool_name == "record_cell":
            handle = call.arguments.get("handle")
            axis = call.arguments.get("axis")
            if handle is None or handle not in handle_to_row_id:
                errors.append(
                    {
                        "reason": "unknown_handle",
                        "handle": handle,
                        "arguments": call.arguments,
                    }
                )
                continue
            row_id = handle_to_row_id[handle]
            key = (row_id, axis)
            spec = registry.get(key)
            if spec is None:
                errors.append(
                    {"reason": "unknown_row_axis", "key": list(key), "arguments": call.arguments}
                )
                continue
            if _is_null_freetext_abstention(spec, call.arguments):
                unscoreable.append(
                    {
                        **call.arguments,
                        "row_id": row_id,
                        "axis": axis,
                        "reason": "conditional cell not applicable (value null)",
                    }
                )
                continue
            try:
                instantiated.append(tier0._instantiate_cell(spec, call.arguments))
            except Exception as exc:  # noqa: BLE001 — capture-and-continue per plan
                errors.append(
                    {
                        "reason": "instantiation_failed",
                        "key": list(key),
                        "error": repr(exc),
                        "arguments": call.arguments,
                    }
                )
        elif call.tool_name == "record_unscoreable_cell":
            handle = call.arguments.get("handle")
            axis = call.arguments.get("axis")
            if handle is None or handle not in handle_to_row_id:
                errors.append(
                    {
                        "reason": "unknown_handle",
                        "handle": handle,
                        "arguments": call.arguments,
                    }
                )
                continue
            row_id = handle_to_row_id[handle]
            unscoreable.append(
                {
                    **call.arguments,
                    "row_id": row_id,
                    "axis": axis,
                }
            )
        else:
            errors.append(
                {
                    "reason": "unknown_tool_name",
                    "tool_name": call.tool_name,
                    "arguments": call.arguments,
                }
            )
    return instantiated, unscoreable, errors


def _compute_and_print_agreement(
    rosters: dict[str, tuple[Any, list[Any]]], results_dir: Path
) -> dict[str, Any]:
    """Read every saved dispatch, classify each cell's N runs, print sigma_noise."""
    print("\n=== inter-run agreement / sigma_noise (N=3) ===")
    report: dict[str, Any] = {}
    for model in _MODELS:
        per_cell: dict[Any, dict[str, Any]] = {}
        for chunk_id, (_chunk, legal) in rosters.items():
            run_results = []
            for run_idx in range(1, _N_RUNS + 1):
                path = dispatch_result_path(results_dir, model, chunk_id, run_idx)
                if path.exists():
                    run_results.append(json.loads(path.read_text(encoding="utf-8")))
            if len(run_results) < _N_RUNS:
                print(f"  {model}/{chunk_id}: only {len(run_results)}/{_N_RUNS} runs — skipped")
                continue
            for spec in legal:
                outcomes = [
                    extract_cell_outcome(rr, spec.row_id, spec.axis) for rr in run_results
                ]
                per_cell[(spec.row_id, spec.axis)] = classify_cell_runs(outcomes)
        summary = summarize_sigma_noise(per_cell)
        report[model] = summary
        print(f"  {model}: {summary}")
    return report


def main(argv: list[str] | None = None) -> int:
    """Run the 36-dispatch Tier-1 legal-axis sweep end-to-end. Resumable."""
    args = parse_args(argv)
    state = args.state
    vintage = args.vintage
    bundle_dir = resolve_bundle_dir(state, vintage)
    results_dir = resolve_results_dir(state, vintage)

    _preflight(bundle_dir)

    from lobby_analysis.chunks_v2 import build_chunks
    from lobby_analysis.models_v2 import build_cell_spec_registry

    chunks = {c.chunk_id: c for c in build_chunks()}
    registry = build_cell_spec_registry()

    statute_text, statute_filenames = tier0.load_statute_bundle(bundle_dir)
    system_prompt = _SYSTEM_PROMPT_TEMPLATE.format(statute_text=statute_text)
    prompt_sha256 = hashlib.sha256(system_prompt.encode("utf-8")).hexdigest()
    results_dir.mkdir(parents=True, exist_ok=True)
    print(f"State/vintage: {state} {vintage}")
    print(f"Bundle dir: {bundle_dir}")
    print(f"Results dir: {results_dir}")

    active_chunks = resolve_active_chunks(args.chunks)
    if active_chunks != _RESOLVED_CHUNKS:
        print(f"Filtered to {len(active_chunks)} of {len(_RESOLVED_CHUNKS)} chunks: {', '.join(active_chunks)}")

    # Build the legal-only rosters once.
    rosters: dict[str, tuple[Any, list[Any]]] = {}
    for chunk_id in active_chunks:
        if chunk_id not in chunks:
            print(f"ERROR: chunk {chunk_id!r} not in CHUNKS_V2 manifest.", file=sys.stderr)
            return 2
        chunk = chunks[chunk_id]
        legal = build_legal_roster(chunk)
        if not legal:
            print(f"WARN: chunk {chunk_id!r} has no legal cells after filter — skipping.")
            continue
        rosters[chunk_id] = (chunk, legal)

    total_legal = sum(len(legal) for _c, legal in rosters.values())
    print(f"Statute files: {len(statute_filenames)}  (~{len(system_prompt) // 4} prompt tokens)")
    print(f"Prompt sha256: {prompt_sha256}")
    print(f"Chunks: {len(rosters)}  legal cells: {total_legal}")
    print(f"Dispatches planned: {len(_MODELS)} models x {len(rosters)} chunks x {_N_RUNS} runs")

    session_cost = 0.0
    n_dispatched = 0
    n_skipped = 0

    for model in _MODELS:
        sdk, dispatcher = _DISPATCHERS[model]
        for chunk_id, (chunk, legal) in rosters.items():
            user_message, handle_to_row_id = render_legal_roster(
                chunk_id, chunk.topic, legal
            )
            for run_idx in range(1, _N_RUNS + 1):
                if is_dispatch_done(results_dir, model, chunk_id, run_idx):
                    n_skipped += 1
                    continue
                print(f"\ndispatch {sdk}/{model} chunk={chunk_id} run={run_idx} ...")
                try:
                    response, elapsed = dispatcher(system_prompt, user_message)
                except Exception as exc:  # noqa: BLE001
                    print(f"ERROR: dispatch failed: {exc!r}", file=sys.stderr)
                    return 4

                usage = tier0._serialize_usage(getattr(response, "usage", None))
                cost = tier0._estimate_cost_usd(model, usage)
                if cost > _PER_CALL_COST_CEILING_USD:
                    print(
                        f"ABORT: per-call cost ${cost:.4f} exceeded ceiling "
                        f"${_PER_CALL_COST_CEILING_USD}. Stop and investigate.",
                        file=sys.stderr,
                    )
                    return 3
                session_cost += cost
                if session_cost > _SESSION_COST_CEILING_USD:
                    print(
                        f"ABORT: session cost ${session_cost:.4f} exceeded ceiling "
                        f"${_SESSION_COST_CEILING_USD}. Re-run to resume from checkpoint.",
                        file=sys.stderr,
                    )
                    return 3

                instantiated, unscoreable, errors = _parse_and_instantiate(
                    response, sdk, registry, handle_to_row_id
                )
                provenance = {
                    "originating_convo": _ORIGINATING_CONVO,
                    "script": "scripts/tier_1_direct_read_legal_axis.py",
                    "model": model,
                    "sdk": sdk,
                    "chunk_id": chunk_id,
                    "run_index": run_idx,
                    "state_abbr": state,
                    "vintage_year": vintage,
                    "prompt_sha256": prompt_sha256,
                    "timestamp_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                }
                path = dispatch_result_path(results_dir, model, chunk_id, run_idx)
                tier0._save_json(
                    path,
                    {
                        "provenance": provenance,
                        "wall_clock_seconds": elapsed,
                        "usage": usage,
                        "cost_usd_estimate": cost,
                        "legal_roster": [[s.row_id, s.axis] for s in legal],
                        "instantiated_cells": instantiated,
                        "unscoreable_emissions": unscoreable,
                        "errors": errors,
                        "response": tier0._serialize_response(response),
                    },
                )
                n_dispatched += 1
                print(
                    f"  saved {path.name}  cells={len(instantiated)} "
                    f"unscoreable={len(unscoreable)} errors={len(errors)}  "
                    f"${cost:.4f} ({elapsed:.1f}s)"
                )

    print(
        f"\ndispatched={n_dispatched}  skipped(resumed)={n_skipped}  "
        f"session_cost=${session_cost:.4f}"
    )
    _compute_and_print_agreement(rosters, results_dir)
    return 0


if __name__ == "__main__":
    sys.exit(main())
