"""Load and normalize the three locked rubrics into a shared schema."""

from __future__ import annotations

import csv
import hashlib
from pathlib import Path

from pydantic import ValidationError

from scoring.models import Rubric, RubricItem

# Rubric registry: logical name -> (path, column rename map to normalize into RubricItem fields)
RUBRIC_PATHS: dict[str, tuple[Path, dict[str, str]]] = {
    "pri_accessibility": (
        Path("docs/historical/pri-2026-rescore/results/pri_2026_accessibility_rubric.csv"),
        {"category": "category", "item_text": "item_text"},
    ),
    "pri_disclosure_law": (
        Path("docs/historical/pri-2026-rescore/results/pri_2026_disclosure_law_rubric.csv"),
        # disclosure-law uses "sub_component" where accessibility uses "category"
        {"category": "sub_component", "item_text": "item_text"},
    ),
    "focal_indicators": (
        Path("docs/historical/focal-extraction/results/focal_2026_scoring_rubric.csv"),
        # FOCAL uses indicator_id / indicator_text
        {"category": "category", "item_text": "indicator_text", "item_id": "indicator_id"},
    ),
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_rubric(name: str, repo_root: Path) -> Rubric:
    """Load a rubric by logical name, normalizing columns into the shared RubricItem schema."""
    if name not in RUBRIC_PATHS:
        raise ValueError(f"unknown rubric {name!r}; valid: {list(RUBRIC_PATHS)}")

    rel_path, rename_map = RUBRIC_PATHS[name]
    csv_path = repo_root / rel_path
    if not csv_path.exists():
        raise FileNotFoundError(csv_path)

    sha = _sha256(csv_path)

    with csv_path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        raw_rows = list(reader)

    items: list[RubricItem] = []
    for row in raw_rows:
        normalized = {
            "item_id": row.get(rename_map.get("item_id", "item_id"), row.get("item_id", "")),
            "category": row.get(rename_map["category"], ""),
            "item_text": row.get(rename_map["item_text"], ""),
            "data_type": row.get("data_type", "binary"),
            "source": row.get("source", ""),
            "scoring_direction": row.get("scoring_direction", "normal"),
            "scoring_guidance": row.get("scoring_guidance", ""),
            "notes": row.get("notes", ""),
        }
        try:
            items.append(RubricItem(**normalized))
        except ValidationError as e:
            raise ValueError(f"{name} row {normalized.get('item_id')!r} failed validation: {e}") from e

    return Rubric(name=name, items=items, sha=sha)  # type: ignore[arg-type]


def load_all_rubrics(repo_root: Path) -> dict[str, Rubric]:
    return {name: load_rubric(name, repo_root) for name in RUBRIC_PATHS}
