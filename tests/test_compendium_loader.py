"""Tests for the compendium loader.

Stage A of plans/20260430_compendium_population_and_smr_fill.md.

Unit tests use synthetic CSVs in tmp_path. Integration tests load the real
compendium/disclosure_items.csv and verify curation completeness against
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
REAL_COMPENDIUM = REPO_ROOT / "compendium" / "disclosure_items.csv"
DEDUP_MAP = REPO_ROOT / "compendium" / "framework_dedup_map.csv"

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
# These use the curated `compendium/disclosure_items.csv`. They are
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


# -----------------------------------------------------------------------------
# Compendium expansion v2 — curation-drop tests for the 5 newly walked rubrics.
#
# Source-of-truth for "items walked" is `framework_dedup_map.csv`: the per-
# rubric audit walkthrough lands every atomic rubric item there with a
# disposition (EXISTS via framework:item_id reference, MERGE via boolean
# expression, NEW via UPPERCASE compendium row id, or OUT_OF_SCOPE).
#
# Audit document: docs/active/filing-schema-extraction/results/20260430_compendium_audit.md
# Originating plan: docs/active/filing-schema-extraction/plans/20260430_compendium_expansion_v2.md
#
# Atomic item counts per rubric come from the audit's per-rubric tables.
# -----------------------------------------------------------------------------


_NEWLY_WALKED_RUBRICS = {
    "newmark_2017": 19,       # 7 def + 5 prohib + 7 disc
    "newmark_2005": 18,       # 7 def + 1 freq + 4 prohib + 6 disc
    "opheim_1991": 22,        # 7 def + 8 freq-and-quality + 7 enforcement
    "hired_guns_2007": 48,    # CPI: 2 def + 8 reg + 15 ind-spending + 2 emp + 3 efile + 8 access + 9 enforce + 1 revolving
    "opensecrets_2022": 7,    # 4 main scoring areas + 3 public-availability sub-items
}


_UPPERCASE_ROW_RE = re.compile(r"^[A-Z][A-Z0-9_]+$")


def _walked_items_for(framework: str) -> list[dict]:
    """Return all dedup-map rows for a given source framework."""
    if not DEDUP_MAP.exists():
        pytest.fail(f"dedup map missing at {DEDUP_MAP}")
    with DEDUP_MAP.open() as f:
        return [r for r in csv.DictReader(f) if r["source_framework"] == framework]


def _assert_rubric_walked(framework: str, expected_count: int) -> None:
    """Per-rubric curation-drop assertion.

    Asserts: (a) the expected number of atomic items appear in the dedup map
    for this framework, AND (b) every non-OUT_OF_SCOPE entry resolves either
    to a real framework:item_id reference (EXISTS/MERGE) or to a real
    UPPERCASE compendium row id (NEW).

    Catches future drops: if a fellow removes a compendium row or fails to
    re-curate after a paper update, the corresponding rubric item resolution
    will break and this test will fire with a precise diff.
    """
    items = _real_compendium_or_skip()
    by_id = {i.id for i in items}
    referenced_pairs: set[tuple[str, str]] = {
        (ref.framework, ref.item_id) for i in items for ref in i.framework_references
    }

    walked = _walked_items_for(framework)
    assert len(walked) == expected_count, (
        f"{framework}: expected {expected_count} atomic items walked into dedup map, "
        f"found {len(walked)}. The audit doc "
        f"(results/20260430_compendium_audit.md) is the source of truth for the count."
    )

    unresolved: list[str] = []
    for entry in walked:
        expr = entry["target_expression"].strip()
        if expr.startswith("OUT_OF_SCOPE"):
            continue
        # Check uppercase row-id tokens (NEW dispositions)
        for token in re.split(r"[\s|&()]+", expr):
            token = token.strip()
            if not token or token == "NEW" or token.startswith("OUT_OF_SCOPE"):
                continue
            if ":" in token:
                fw, item_id = token.split(":", 1)
                if (fw, item_id) not in referenced_pairs:
                    unresolved.append(
                        f"{framework}/{entry['source_item_id']}: framework_ref "
                        f"{fw}:{item_id} missing from compendium"
                    )
            elif _UPPERCASE_ROW_RE.match(token):
                if token not in by_id:
                    unresolved.append(
                        f"{framework}/{entry['source_item_id']}: NEW row id "
                        f"{token} missing from compendium"
                    )
    assert not unresolved, (
        f"{framework}: {len(unresolved)} dedup-map entries fail to resolve "
        f"against the curated compendium (curation drop?):\n  "
        + "\n  ".join(unresolved[:10])
        + ("\n  ..." if len(unresolved) > 10 else "")
    )


def test_loaded_real_compendium_includes_all_newmark_2017_items() -> None:
    _assert_rubric_walked("newmark_2017", _NEWLY_WALKED_RUBRICS["newmark_2017"])


def test_loaded_real_compendium_includes_all_newmark_2005_items() -> None:
    _assert_rubric_walked("newmark_2005", _NEWLY_WALKED_RUBRICS["newmark_2005"])


def test_loaded_real_compendium_includes_all_opheim_1991_items() -> None:
    _assert_rubric_walked("opheim_1991", _NEWLY_WALKED_RUBRICS["opheim_1991"])


def test_loaded_real_compendium_includes_all_hired_guns_2007_items() -> None:
    _assert_rubric_walked("hired_guns_2007", _NEWLY_WALKED_RUBRICS["hired_guns_2007"])


def test_loaded_real_compendium_includes_all_opensecrets_2022_items() -> None:
    _assert_rubric_walked("opensecrets_2022", _NEWLY_WALKED_RUBRICS["opensecrets_2022"])


# -----------------------------------------------------------------------------
# Data model v1.2: domain="definitions" + 7 notes-flagged row resolution
#
# Plan: docs/active/filing-schema-extraction/plans/20260501_data_model_v1_2_definitions_domain.md
#
# These tests assert the v1.2 migration is complete:
#   - Schema accepts "definitions" as a valid CompendiumDomain value.
#   - 5 rows are migrated to domain="definitions".
#   - 2 new symmetry rows exist (DEF_EXPENDITURE_STANDARD, DEF_TIME_STANDARD)
#     in domain="definitions".
#   - All 7 notes-flagged rows have their flag dropped.
#   - Every domain="definitions" row has at least one definitional
#     framework_reference (Newmark, Opheim, CPI, or PRI D0).
# -----------------------------------------------------------------------------


_DEFINITIONS_ROW_IDS = {
    "THRESHOLD_LOBBYING_MATERIALITY_GATE",
    "DEF_ADMIN_AGENCY_LOBBYING_TRIGGER",
    "DEF_ELECTED_OFFICIAL_AS_LOBBYIST",
    "DEF_PUBLIC_EMPLOYEE_AS_LOBBYIST",
    "DEF_COMPENSATION_STANDARD",
    "DEF_EXPENDITURE_STANDARD",
    "DEF_TIME_STANDARD",
}

_NOTES_FLAG_FRAGMENT = "definition-trigger criterion"

_PREVIOUSLY_FLAGGED_ROWS = _DEFINITIONS_ROW_IDS - {
    "DEF_EXPENDITURE_STANDARD",
    "DEF_TIME_STANDARD",
} | {
    # Rows that were notes-flagged but stay in registration (flag must drop).
    "REG_LOBBYIST",
    "THRESHOLD_LOBBYING_EXPENDITURE_PRESENT",
    "THRESHOLD_LOBBYING_TIME_PRESENT",
}


def test_compendium_domain_literal_accepts_definitions_value(tmp_path: Path) -> None:
    """v1.2: 'definitions' is a valid CompendiumDomain Literal value."""
    csv_path = tmp_path / "compendium.csv"
    _write_csv(csv_path, [_row(domain="definitions")])

    items = load_compendium(csv_path)

    assert len(items) == 1
    assert items[0].domain == "definitions"


def test_real_compendium_has_definitions_domain_rows() -> None:
    """v1.2: the 7 expected row IDs all have domain='definitions' post-migration."""
    items = _real_compendium_or_skip()
    by_id = {i.id: i for i in items}

    missing = _DEFINITIONS_ROW_IDS - by_id.keys()
    assert not missing, f"v1.2 row IDs missing from compendium: {sorted(missing)}"

    wrong_domain = {
        rid: by_id[rid].domain for rid in _DEFINITIONS_ROW_IDS if by_id[rid].domain != "definitions"
    }
    assert not wrong_domain, (
        f"v1.2 rows have wrong domain (expected 'definitions'): {wrong_domain}"
    )


def test_real_compendium_has_no_lingering_definition_trigger_notes_flags() -> None:
    """v1.2: every previously notes-flagged row must have its flag dropped."""
    items = _real_compendium_or_skip()
    by_id = {i.id: i for i in items}

    still_flagged: list[str] = []
    for rid in _PREVIOUSLY_FLAGGED_ROWS:
        if rid not in by_id:
            continue
        if _NOTES_FLAG_FRAGMENT in by_id[rid].notes:
            still_flagged.append(rid)
    assert not still_flagged, (
        f"rows still carry the v1.1 notes flag (should be dropped post-v1.2): {still_flagged}"
    )


def test_definitions_domain_rows_have_definitional_framework_refs() -> None:
    """v1.2: every domain='definitions' row references at least one of
    Newmark/Opheim/CPI Hired Guns, OR PRI D0 (the materiality umbrella).

    This catches an orphan 'definitions' row that has no definitional rubric
    behind it. PRI D0 is the only PRI item that captures the qualitative
    materiality concept; PRI A/B/C/D1/D2/E items are not definitional in this
    sense.
    """
    items = _real_compendium_or_skip()
    definitional_frameworks = {"newmark_2017", "newmark_2005", "opheim_1991", "hired_guns_2007"}

    orphans: list[str] = []
    for item in items:
        if item.domain != "definitions":
            continue
        has_definitional = any(
            ref.framework in definitional_frameworks
            or (ref.framework == "pri_2010_disclosure" and ref.item_id == "D0")
            for ref in item.framework_references
        )
        if not has_definitional:
            orphans.append(item.id)
    assert not orphans, (
        f"domain='definitions' rows missing a definitional framework_reference: {orphans}"
    )


def test_materiality_gate_row_has_newmark_opheim_cross_refs() -> None:
    """v1.2 curation-gap fix: D0 (the qualitative-materiality umbrella) gains
    Newmark/Opheim framework_references.

    Each Newmark/Opheim 'standard' (compensation/expenditure/time) implies the
    existence of a materiality test; the D0 row should reflect that.
    """
    items = _real_compendium_or_skip()
    by_id = {i.id: i for i in items}
    row = by_id.get("THRESHOLD_LOBBYING_MATERIALITY_GATE")
    assert row is not None, "THRESHOLD_LOBBYING_MATERIALITY_GATE missing"
    frameworks = {ref.framework for ref in row.framework_references}
    expected_extra = {"newmark_2017", "newmark_2005", "opheim_1991"}
    missing = expected_extra - frameworks
    assert not missing, (
        f"THRESHOLD_LOBBYING_MATERIALITY_GATE missing definitional cross-refs: {sorted(missing)}"
    )


def test_inclusion_framed_expenditure_standard_is_separate_row() -> None:
    """v1.2 symmetry-gap fix: DEF_EXPENDITURE_STANDARD exists as a separate
    inclusion-framed row, paralleling DEF_COMPENSATION_STANDARD.

    Newmark/Opheim's def_expenditure_standard re-targets here (was previously
    folded into the exemption-framed THRESHOLD_LOBBYING_EXPENDITURE_PRESENT).
    """
    items = _real_compendium_or_skip()
    by_id = {i.id: i for i in items}
    row = by_id.get("DEF_EXPENDITURE_STANDARD")
    assert row is not None, "DEF_EXPENDITURE_STANDARD missing"
    assert row.domain == "definitions"

    # Newmark/Opheim def_expenditure_standard now targets this row in dedup map.
    with DEDUP_MAP.open() as f:
        for r in csv.DictReader(f):
            if r["source_framework"] in {"newmark_2017", "newmark_2005", "opheim_1991"} and (
                r["source_item_id"] == "def_expenditure_standard"
            ):
                assert "DEF_EXPENDITURE_STANDARD" in r["target_expression"], (
                    f"{r['source_framework']}/def_expenditure_standard should target "
                    f"DEF_EXPENDITURE_STANDARD; got {r['target_expression']!r}"
                )


def test_inclusion_framed_time_standard_is_separate_row() -> None:
    """v1.2 symmetry-gap fix: DEF_TIME_STANDARD exists as a separate
    inclusion-framed row, paralleling DEF_COMPENSATION_STANDARD."""
    items = _real_compendium_or_skip()
    by_id = {i.id: i for i in items}
    row = by_id.get("DEF_TIME_STANDARD")
    assert row is not None, "DEF_TIME_STANDARD missing"
    assert row.domain == "definitions"

    with DEDUP_MAP.open() as f:
        for r in csv.DictReader(f):
            if r["source_framework"] in {"newmark_2017", "newmark_2005", "opheim_1991"} and (
                r["source_item_id"] == "def_time_standard"
            ):
                assert "DEF_TIME_STANDARD" in r["target_expression"], (
                    f"{r['source_framework']}/def_time_standard should target "
                    f"DEF_TIME_STANDARD; got {r['target_expression']!r}"
                )
