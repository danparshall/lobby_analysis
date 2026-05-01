"""Load the compendium artifact (`compendium/disclosure_items.csv`).

The compendium is the union of field-level questions across rubric frameworks
(PRI, FOCAL, Sunlight, ...). Each row maps to one ``CompendiumItem``; the
``framework_references_json`` column carries a JSON-encoded list of
``FrameworkReference`` dicts so the union is preserved.

Required infrastructure: a missing file is a hard error, not an empty list.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

from lobby_analysis.models import CompendiumItem, FrameworkReference


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_COMPENDIUM_CSV = REPO_ROOT / "compendium" / "disclosure_items.csv"


_TRUE = {"true", "1", "yes", "y", "t"}
_FALSE = {"false", "0", "no", "n", "f", ""}


def _parse_bool(value: str) -> bool:
    v = (value or "").strip().lower()
    if v in _TRUE:
        return True
    if v in _FALSE:
        return False
    raise ValueError(f"unparseable boolean: {value!r}")


def _row_to_item(row: dict[str, str]) -> CompendiumItem:
    refs_raw = row.get("framework_references_json", "").strip()
    refs_data = json.loads(refs_raw) if refs_raw else []
    framework_references = [FrameworkReference(**r) for r in refs_data]

    def _opt(key: str) -> str | None:
        v = row.get(key, "")
        return v if v not in (None, "") else None

    return CompendiumItem(
        id=row["id"],
        name=row["name"],
        description=row["description"],
        domain=row["domain"],
        data_type=row["data_type"],
        framework_references=framework_references,
        maps_to_state_master_field=_opt("maps_to_state_master_field"),
        maps_to_filing_field=_opt("maps_to_filing_field"),
        observable_from_database=_parse_bool(row.get("observable_from_database", "")),
        notes=row.get("notes", "") or "",
    )


def load_compendium(path: Path | str = DEFAULT_COMPENDIUM_CSV) -> list[CompendiumItem]:
    """Read the compendium CSV and return parsed CompendiumItem instances.

    Args:
        path: Path to the compendium CSV. Defaults to the repo's
            ``compendium/disclosure_items.csv``.

    Returns:
        A list of validated CompendiumItem objects in CSV order.

    Raises:
        FileNotFoundError: if the CSV does not exist.
        pydantic.ValidationError: if any row violates the schema.
        json.JSONDecodeError: if framework_references_json is malformed.
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"compendium CSV not found: {p}")
    with p.open() as f:
        reader = csv.DictReader(f)
        return [_row_to_item(row) for row in reader]
