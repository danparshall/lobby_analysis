"""Load compendium artifacts.

Two compendium versions coexist during the v1 → v2 deprecation window:

- **v2 (active)** — ``compendium/disclosure_side_compendium_items_v2.tsv``. 181 rows.
  Cell-typed observables across legal/practical axes. Read via
  ``load_v2_compendium``. The minimal raw-dict return shape is intentional:
  typed Pydantic models for v2 belong to the ``extraction-harness-brainstorm``
  branch's surgery (model shape = extraction output shape).
- **v1 (deprecated)** — ``compendium/_deprecated/v1/disclosure_items.csv``. 141
  rows. Structurally PRI-shaped. Loaded via
  ``load_v1_compendium_deprecated`` only by legacy callers (PRI-MVP
  ``cmd_build_smr`` / ``smr_projection`` path and their tests). Do not call
  from new code. See ``compendium/_deprecated/v1/README.md`` for why v1 was
  deprecated rather than patched.

Required infrastructure: a missing file is a hard error, not an empty list.
"""

from __future__ import annotations

import csv
from pathlib import Path

from lobby_analysis.models import CompendiumItem, FrameworkReference
import json


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_COMPENDIUM_V2_TSV = REPO_ROOT / "compendium" / "disclosure_side_compendium_items_v2.tsv"
DEFAULT_COMPENDIUM_V1_CSV = REPO_ROOT / "compendium" / "_deprecated" / "v1" / "disclosure_items.csv"


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


def load_v1_compendium_deprecated(
    path: Path | str = DEFAULT_COMPENDIUM_V1_CSV,
) -> list[CompendiumItem]:
    """Read the deprecated v1 compendium CSV and return parsed CompendiumItem instances.

    **DEPRECATED.** v1 (141 rows, PRI-shaped) was superseded by v2 (181 rows,
    cell-typed observables) on 2026-05-14. Use ``load_v2_compendium`` for new
    code. This function exists only so legacy callers (the PRI-projection-MVP
    ``cmd_build_smr`` subcommand, ``smr_projection`` module, and their tests)
    keep working until ``phase-c-projection-tdd`` retires them.

    Args:
        path: Path to the deprecated v1 compendium CSV. Defaults to
            ``compendium/_deprecated/v1/disclosure_items.csv``.

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


def load_v2_compendium(
    path: Path | str = DEFAULT_COMPENDIUM_V2_TSV,
) -> list[dict[str, str]]:
    """Read the v2 compendium TSV and return parsed rows as raw dicts.

    The v2 TSV has 8 columns: ``compendium_row_id``, ``cell_type``, ``axis``,
    ``rubrics_reading``, ``n_rubrics``, ``first_introduced_by``, ``status``,
    ``notes``. See ``compendium/README.md`` for the row-shape contract.

    Returns raw ``list[dict[str, str]]`` rather than a typed model on purpose
    — typed Pydantic v2 models belong to the ``extraction-harness-brainstorm``
    branch's surgery. Callers that want typing should wrap this loader after
    that work lands.

    Args:
        path: Path to the v2 compendium TSV. Defaults to
            ``compendium/disclosure_side_compendium_items_v2.tsv``.

    Returns:
        A list of row dicts in TSV order. The list has 181 entries.

    Raises:
        FileNotFoundError: if the TSV does not exist.
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"compendium TSV not found: {p}")
    with p.open() as f:
        reader = csv.DictReader(f, delimiter="\t")
        return list(reader)
