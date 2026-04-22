"""Parse subagent JSON output, validate against pydantic, write stamped CSVs."""

from __future__ import annotations

import csv
import json
from pathlib import Path

from pydantic import ValidationError

from scoring.models import Rubric, ScoredItem, ScoredRow

SCORED_ROW_COLUMNS = [
    "state",
    "rubric_name",
    "item_id",
    "score",
    "evidence_quote_or_url",
    "source_artifact",
    "confidence",
    "unable_to_evaluate",
    "notes",
    "coverage_tier",
    "model_version",
    "prompt_sha",
    "rubric_sha",
    "snapshot_manifest_sha",
    "run_id",
    "run_timestamp",
]


class OutputSchemaError(ValueError):
    """Raised when the subagent output doesn't match the locked schema."""


def parse_and_validate(
    output_json_path: Path,
    rubric: Rubric,
) -> list[ScoredItem]:
    if not output_json_path.exists():
        raise OutputSchemaError(f"subagent did not produce {output_json_path}")
    try:
        raw = json.loads(output_json_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise OutputSchemaError(f"{output_json_path} is not valid JSON: {e}") from e
    if not isinstance(raw, list):
        raise OutputSchemaError(f"{output_json_path} must be a JSON array")

    expected_ids = [ri.item_id for ri in rubric.items]
    if len(raw) != len(expected_ids):
        raise OutputSchemaError(
            f"expected {len(expected_ids)} items, got {len(raw)} in {output_json_path}"
        )

    items: list[ScoredItem] = []
    for i, row in enumerate(raw):
        try:
            items.append(ScoredItem(**row))
        except ValidationError as e:
            raise OutputSchemaError(f"row {i} (expected id {expected_ids[i]}): {e}") from e

    got_ids = [si.item_id for si in items]
    if got_ids != expected_ids:
        mismatch = [(i, g, e) for i, (g, e) in enumerate(zip(got_ids, expected_ids)) if g != e]
        raise OutputSchemaError(f"item_id order mismatch vs rubric: {mismatch[:5]} ...")

    return items


def write_scored_csv(rows: list[ScoredRow], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=SCORED_ROW_COLUMNS)
        writer.writeheader()
        for r in rows:
            d = r.model_dump()
            d["unable_to_evaluate"] = "true" if d["unable_to_evaluate"] else "false"
            writer.writerow(d)
