"""Load the source-quotes YAML sidecar — prompt SSOT for the tier-1 dispatch.

The sidecar lives at ``compendium/source_quotes.yaml`` (repo-relative) and is
the source of truth for what the model sees per compendium row. Per-row YAML
schema is two flat fields:

- ``source_quotes`` — non-empty dict keyed by ``<rubric>_<section_ref>``,
  holding verbatim quote(s) from the source rubric(s). Immutable reference
  material; provenance lives here.
- ``prompt`` — non-empty flat string. What ``render_legal_roster`` actually
  emits to the model. Mutable; the Ralph loop edits this field. Initially
  populated as the most relevant verbatim source quote (citations stripped),
  with a clarifier appended where filer/subject ambiguity required it (the
  14 Pattern A rows + 3 Pattern B rows from convo
  ``20260603_prompt_text_fix_iterations_1_and_2``).

The TSV's old ``prompt_text`` column is dropped — the runtime reads from this
YAML at registry-build time instead. The TSV remains the contract for
row-set membership (compendium_row_id, axes, cell types, rubric attribution);
YAML is the prompt SSOT. Two different change cycles: TSV bumps the
compendium version, YAML does not.

Originating convo: docs/active/wi-tier1-direct-read/convos/
    20260604_wide_pass_yaml_sidecar_design.md
Plan: docs/active/wi-tier1-direct-read/plans/20260604_wide_prompt_text_pass.md
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SOURCE_QUOTES_YAML = REPO_ROOT / "compendium" / "source_quotes.yaml"


@dataclass(frozen=True)
class SourceQuotesEntry:
    """Per-row source quotes + model-facing prompt.

    Behavior contract (asserted by the loader): both fields are non-empty.
    Empty source_quotes or empty prompt is a YAML-authoring bug and raises
    rather than silently neutering the model prompt.
    """

    source_quotes: dict[str, str]
    prompt: str


def load_source_quotes(
    path: Path | str = DEFAULT_SOURCE_QUOTES_YAML,
) -> dict[str, SourceQuotesEntry]:
    """Load source-quote YAML and return a row_id → entry mapping.

    Args:
        path: Path to the YAML file. Defaults to
            ``compendium/source_quotes.yaml`` resolved relative to the repo
            root.

    Returns:
        A dict keyed by ``compendium_row_id``; values are
        :class:`SourceQuotesEntry` dataclass instances.

    Raises:
        FileNotFoundError: if the YAML file does not exist.
        ValueError: if any entry is malformed — missing the ``prompt`` key,
            missing the ``source_quotes`` key, has an empty ``source_quotes``
            dict, or has an empty ``prompt`` string. The error message names
            the offending ``row_id`` and the failing field so authoring
            errors are immediately localizable.
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"source-quotes YAML not found: {p}")

    with p.open(encoding="utf-8") as fh:
        raw = yaml.safe_load(fh)

    # An empty or completely-missing YAML body yields None — treat as empty.
    if raw is None:
        return {}

    if not isinstance(raw, dict):
        raise ValueError(
            f"source-quotes YAML at {p} must be a top-level mapping; got {type(raw).__name__}"
        )

    entries: dict[str, SourceQuotesEntry] = {}
    for row_id, body in raw.items():
        if not isinstance(body, dict):
            raise ValueError(
                f"row_id {row_id!r} in {p}: entry must be a mapping with "
                f"`source_quotes` and `prompt` keys; got {type(body).__name__}"
            )

        if "source_quotes" not in body:
            raise ValueError(
                f"row_id {row_id!r} in {p}: missing required key `source_quotes`"
            )
        source_quotes = body["source_quotes"]
        if not isinstance(source_quotes, dict) or not source_quotes:
            raise ValueError(
                f"row_id {row_id!r} in {p}: `source_quotes` must be a "
                f"non-empty mapping (provenance is load-bearing); got "
                f"{source_quotes!r}"
            )

        if "prompt" not in body:
            raise ValueError(
                f"row_id {row_id!r} in {p}: missing required key `prompt`"
            )
        prompt = body["prompt"]
        if not isinstance(prompt, str) or not prompt:
            raise ValueError(
                f"row_id {row_id!r} in {p}: `prompt` must be a non-empty "
                f"string; got {prompt!r}"
            )

        # Coerce values inside source_quotes to plain strings — YAML can give
        # back non-str types if the entry is e.g. an int.
        normalized_quotes = {str(k): str(v) for k, v in source_quotes.items()}

        entries[row_id] = SourceQuotesEntry(
            source_quotes=normalized_quotes,
            prompt=prompt,
        )

    return entries
