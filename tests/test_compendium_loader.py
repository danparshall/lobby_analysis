"""Tests for the compendium loader.

Stage A of plans/20260430_compendium_population_and_smr_fill.md.

Unit tests use synthetic CSVs in tmp_path. Integration tests load the real
data/compendium/disclosure_items.csv and verify curation completeness against
the four source rubric CSVs.
"""

from __future__ import annotations

import csv
import json
import re
from pathlib import Path

import pytest
from pydantic import ValidationError

from lobby_analysis.compendium_loader import load_compendium
from lobby_analysis.models import CompendiumItem


REPO_ROOT = Path(__file__).resolve().parents[1]
REAL_COMPENDIUM = REPO_ROOT / "data" / "compendium" / "disclosure_items.csv"
DEDUP_MAP = REPO_ROOT / "data" / "compendium" / "framework_dedup_map.csv"

PRI_DISCLOSURE_RUBRIC = (
    REPO_ROOT
    / "docs"
    / "historical"
    / "pri-2026-rescore"
    / "results"
    / "pri_2010_disclosure_law_rubric.csv"
)
PRI_ACCESSIBILITY_RUBRIC = (
    REPO_ROOT
    / "docs"
    / "historical"
    / "pri-2026-rescore"
    / "results"
    / "pri_2010_accessibility_rubric.csv"
)
FOCAL_RUBRIC = (
    REPO_ROOT
    / "docs"
    / "historical"
    / "focal-extraction"
    / "results"
    / "focal_2024_indicators.csv"
)


COMPENDIUM_FIELDNAMES = [
    "id",
    "name",
    "description",
    "domain",
    "data_type",
    "framework_references_json",
    "maps_to_state_master_field",
    "maps_to_filing_field",
    "observable_from_database",
    "notes",
]


def _write_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=COMPENDIUM_FIELDNAMES)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)


def _row(**overrides) -> dict:
    """Build a synthetic compendium row with sensible defaults."""
    base = {
        "id": "REG_LOBBYIST",
        "name": "Lobbyist registration",
        "description": "Whether a lobbyist must register.",
        "domain": "registration",
        "data_type": "boolean",
        "framework_references_json": json.dumps(
            [{"framework": "pri_2010_disclosure", "item_id": "A1"}]
        ),
        "maps_to_state_master_field": "",
        "maps_to_filing_field": "",
        "observable_from_database": "False",
        "notes": "",
    }
    base.update(overrides)
    return base


# -----------------------------------------------------------------------------
# A.5 unit tests (synthetic CSVs in tmp_path)
# -----------------------------------------------------------------------------


def test_loader_reads_well_formed_compendium_csv(tmp_path: Path) -> None:
    """Three synthetic rows round-trip into three valid CompendiumItem objects."""
    csv_path = tmp_path / "compendium.csv"
    _write_csv(
        csv_path,
        [
            _row(id="REG_LOBBYIST"),
            _row(
                id="RPT_LOBBYIST_COMPENSATION",
                name="Lobbyist compensation reported",
                description="Whether the report includes lobbyist compensation.",
                domain="financial",
                framework_references_json=json.dumps(
                    [{"framework": "pri_2010_disclosure", "item_id": "E2f_i"}]
                ),
            ),
            _row(
                id="ACC_PORTAL_DOWNLOAD_BULK",
                name="Bulk download available",
                description="Whether the portal offers bulk download.",
                domain="accessibility",
                framework_references_json=json.dumps(
                    [{"framework": "pri_2010_accessibility", "item_id": "Q6"}]
                ),
            ),
        ],
    )

    items = load_compendium(csv_path)

    assert len(items) == 3
    assert all(isinstance(i, CompendiumItem) for i in items)
    assert {i.id for i in items} == {
        "REG_LOBBYIST",
        "RPT_LOBBYIST_COMPENSATION",
        "ACC_PORTAL_DOWNLOAD_BULK",
    }


def test_loader_parses_framework_references_json_column(tmp_path: Path) -> None:
    """A row with two framework refs in JSON parses into both refs with full fields."""
    csv_path = tmp_path / "compendium.csv"
    _write_csv(
        csv_path,
        [
            _row(
                framework_references_json=json.dumps(
                    [
                        {
                            "framework": "pri_2010_disclosure",
                            "item_id": "E2f_i",
                            "item_text": "Direct lobbying costs (compensation).",
                        },
                        {
                            "framework": "sunlight_2015",
                            "item_id": "compensation",
                            "item_text": "Lobbyist compensation disclosed.",
                        },
                    ]
                )
            )
        ],
    )

    items = load_compendium(csv_path)

    assert len(items) == 1
    refs = items[0].framework_references
    assert len(refs) == 2
    assert refs[0].framework == "pri_2010_disclosure"
    assert refs[0].item_id == "E2f_i"
    assert refs[0].item_text == "Direct lobbying costs (compensation)."
    assert refs[1].framework == "sunlight_2015"
    assert refs[1].item_id == "compensation"


def test_loader_raises_on_invalid_domain(tmp_path: Path) -> None:
    csv_path = tmp_path / "compendium.csv"
    _write_csv(csv_path, [_row(domain="vibes")])

    with pytest.raises(ValidationError):
        load_compendium(csv_path)


def test_loader_raises_on_invalid_data_type(tmp_path: Path) -> None:
    csv_path = tmp_path / "compendium.csv"
    _write_csv(csv_path, [_row(data_type="quaternion")])

    with pytest.raises(ValidationError):
        load_compendium(csv_path)


def test_loader_raises_on_missing_file(tmp_path: Path) -> None:
    """compendium is required infrastructure — missing file is a hard error."""
    nonexistent = tmp_path / "does_not_exist.csv"

    with pytest.raises(FileNotFoundError):
        load_compendium(nonexistent)


# -----------------------------------------------------------------------------
# A.5 real-artifact integration tests
#
# These use the curated `data/compendium/disclosure_items.csv`. They are
# expected to fail until Stage A curation lands; once it does, they enforce
# that no source-rubric items were dropped during curation.
# -----------------------------------------------------------------------------


def _real_compendium_or_skip() -> list[CompendiumItem]:
    if not REAL_COMPENDIUM.exists():
        pytest.fail(
            f"real compendium CSV missing at {REAL_COMPENDIUM} — "
            "Stage A curation must populate this artifact"
        )
    return load_compendium(REAL_COMPENDIUM)


def _read_rubric_ids(path: Path, id_column: str = "item_id") -> set[str]:
    with path.open() as f:
        return {row[id_column] for row in csv.DictReader(f)}


def _refs_by_framework(
    items: list[CompendiumItem], framework: str
) -> set[str]:
    out: set[str] = set()
    for item in items:
        for ref in item.framework_references:
            if ref.framework == framework:
                out.add(ref.item_id)
    return out


def test_loaded_real_compendium_has_no_duplicate_ids() -> None:
    items = _real_compendium_or_skip()
    ids = [i.id for i in items]
    assert len(ids) == len(set(ids)), "duplicate compendium IDs detected"


def test_loaded_real_compendium_every_row_has_at_least_one_framework_reference() -> None:
    items = _real_compendium_or_skip()
    orphans = [i.id for i in items if not i.framework_references]
    assert orphans == [], (
        f"compendium rows with no framework reference (curation bug): {orphans}"
    )


def test_loaded_real_compendium_includes_all_pri_2010_disclosure_items() -> None:
    items = _real_compendium_or_skip()
    pri_disclosure = _read_rubric_ids(PRI_DISCLOSURE_RUBRIC)
    referenced = _refs_by_framework(items, "pri_2010_disclosure")
    missing = pri_disclosure - referenced
    assert not missing, f"PRI 2010 disclosure items missing from compendium: {sorted(missing)}"


def test_loaded_real_compendium_includes_all_pri_2010_accessibility_items() -> None:
    items = _real_compendium_or_skip()
    pri_accessibility = _read_rubric_ids(PRI_ACCESSIBILITY_RUBRIC)
    referenced = _refs_by_framework(items, "pri_2010_accessibility")
    missing = pri_accessibility - referenced
    assert not missing, (
        f"PRI 2010 accessibility items missing from compendium: {sorted(missing)}"
    )


def test_loaded_real_compendium_includes_all_focal_2024_indicators() -> None:
    items = _real_compendium_or_skip()
    focal_ids = _read_rubric_ids(FOCAL_RUBRIC, id_column="indicator_id")
    referenced = _refs_by_framework(items, "focal_2024")
    missing = focal_ids - referenced
    assert not missing, f"FOCAL 2024 indicators missing from compendium: {sorted(missing)}"


def test_loaded_real_compendium_includes_sunlight_2015_unique_items() -> None:
    """Sunlight contributes a small number of unique atomic items.

    Per docs/active/statute-retrieval/results/20260429_sunlight_pri_item_level.md,
    Sunlight adds at minimum:
      - position taken on legislation (Sunlight Activity = 2)
      - expenditure-itemization threshold (Sunlight Threshold)
      - expenditure format granularity (broad-categories vs itemized-w/-dates)
    """
    items = _real_compendium_or_skip()
    sunlight_refs = _refs_by_framework(items, "sunlight_2015")
    assert sunlight_refs, "no Sunlight 2015 framework references found in compendium"


# -----------------------------------------------------------------------------
# Dedup-map sanity (the curation-time audit trail)
# -----------------------------------------------------------------------------


_TOKEN_RE = re.compile(r"([a-z_0-9]+):([A-Za-z0-9_.\-]+)")


def test_dedup_map_target_expressions_reference_real_compendium_items() -> None:
    """Every framework:item_id token in target_expression must appear as a
    framework_reference somewhere in the curated compendium.

    NEW is allowed (means a Sunlight/FOCAL-only concept becoming its own row).
    """
    if not DEDUP_MAP.exists():
        pytest.fail(
            f"dedup map missing at {DEDUP_MAP} — Stage A curation must produce it"
        )
    items = _real_compendium_or_skip()
    referenced_pairs: set[tuple[str, str]] = set()
    for item in items:
        for ref in item.framework_references:
            referenced_pairs.add((ref.framework, ref.item_id))

    bad: list[tuple[str, str, str]] = []
    with DEDUP_MAP.open() as f:
        for row in csv.DictReader(f):
            expr = row["target_expression"].strip()
            if expr == "NEW" or not expr:
                continue
            for fw, item_id in _TOKEN_RE.findall(expr):
                if (fw, item_id) not in referenced_pairs:
                    bad.append((row["source_framework"], row["source_item_id"], expr))
                    break
    assert not bad, (
        f"dedup map references items not present in compendium: {bad[:5]}"
        + ("..." if len(bad) > 5 else "")
    )
