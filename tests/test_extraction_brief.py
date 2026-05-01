"""TDD tests for the v2 extraction-brief builder.

The brief builder inlines the OH 2025 statute bundle into a single string
that subagents read end-to-end (no Read tool, no files-read sidecar). Tests
target behavior against the real compendium CSV + the real OH 2025 bundle —
no mocks, no synthetic fixtures.

These tests are expected to fail until Phase 1 of
docs/active/statute-extraction/plans/20260501_statute_extraction_harness.md
lands the implementation.
"""

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
COMPENDIUM_CSV = REPO_ROOT / "compendium" / "disclosure_items.csv"
OH_2025_BUNDLE_DIR = REPO_ROOT / "data" / "statutes" / "OH" / "2025"
OH_2025_SECTIONS_DIR = OH_2025_BUNDLE_DIR / "sections"
SCORER_PROMPT_V2_PATH = REPO_ROOT / "src" / "scoring" / "scorer_prompt_v2.md"


pytestmark = pytest.mark.skipif(
    not OH_2025_SECTIONS_DIR.exists(),
    reason="OH 2025 statute bundle not present (data/ symlink missing or bundle removed)",
)


def _import_brief_module():
    from scoring import extraction_brief

    return extraction_brief


def test_extraction_brief_inlines_full_bundle():
    """Every section's text content appears verbatim in the rendered brief.

    No Read-tool reference, no truncation. The bundle must be in the model's
    attention unconditionally.
    """
    brief_module = _import_brief_module()
    full_brief, _suffix = brief_module.build_extraction_brief(
        state="OH",
        vintage_year=2025,
        chunk="definitions",
        bundle_dir=OH_2025_BUNDLE_DIR,
        compendium_csv=COMPENDIUM_CSV,
        scorer_prompt_path=SCORER_PROMPT_V2_PATH,
        repo_root=REPO_ROOT,
    )

    section_files = sorted(OH_2025_SECTIONS_DIR.glob("*.txt"))
    assert section_files, "OH 2025 bundle should contain section files"
    for section_path in section_files:
        body = section_path.read_text()
        # Every section's full body must be present in the brief.
        assert body in full_brief, f"section {section_path.name} not inlined verbatim"


def test_extraction_brief_lists_only_chunk_rows():
    """The row-briefs section names exactly the 7 `definitions`-domain row IDs."""
    brief_module = _import_brief_module()
    full_brief, _suffix = brief_module.build_extraction_brief(
        state="OH",
        vintage_year=2025,
        chunk="definitions",
        bundle_dir=OH_2025_BUNDLE_DIR,
        compendium_csv=COMPENDIUM_CSV,
        scorer_prompt_path=SCORER_PROMPT_V2_PATH,
        repo_root=REPO_ROOT,
    )

    expected_definitions_ids = {
        "THRESHOLD_LOBBYING_MATERIALITY_GATE",
        "DEF_ADMIN_AGENCY_LOBBYING_TRIGGER",
        "DEF_ELECTED_OFFICIAL_AS_LOBBYIST",
        "DEF_PUBLIC_EMPLOYEE_AS_LOBBYIST",
        "DEF_COMPENSATION_STANDARD",
        "DEF_EXPENDITURE_STANDARD",
        "DEF_TIME_STANDARD",
    }
    for row_id in expected_definitions_ids:
        assert row_id in full_brief, f"definitions row {row_id} missing from brief"

    # Sanity-check non-definitions rows are NOT pulled into the definitions chunk.
    out_of_chunk_samples = [
        "REG_LOBBYIST",
        "RPT_LOBBYIST_COMPENSATION",
        "CONTACT_LOG_OFFICIAL",
    ]
    for row_id in out_of_chunk_samples:
        assert row_id not in full_brief, (
            f"non-definitions row {row_id} leaked into definitions chunk"
        )


def test_extraction_brief_includes_v2_scorer_prompt_path():
    """The brief points at scorer_prompt_v2.md, not v1's scorer_prompt.md."""
    brief_module = _import_brief_module()
    full_brief, suffix = brief_module.build_extraction_brief(
        state="OH",
        vintage_year=2025,
        chunk="definitions",
        bundle_dir=OH_2025_BUNDLE_DIR,
        compendium_csv=COMPENDIUM_CSV,
        scorer_prompt_path=SCORER_PROMPT_V2_PATH,
        repo_root=REPO_ROOT,
    )

    assert "scorer_prompt_v2.md" in full_brief
    assert "scorer_prompt_v2.md" in suffix
    # The v1 prompt name must not appear (would indicate a leftover reference).
    assert "scorer_prompt.md" not in full_brief.replace("scorer_prompt_v2.md", "")


def test_reconstruct_brief_round_trip(tmp_path):
    """suffix + bundle_manifest_sha → byte-identical reconstruction of the full brief."""
    brief_module = _import_brief_module()
    full_brief, suffix = brief_module.build_extraction_brief(
        state="OH",
        vintage_year=2025,
        chunk="definitions",
        bundle_dir=OH_2025_BUNDLE_DIR,
        compendium_csv=COMPENDIUM_CSV,
        scorer_prompt_path=SCORER_PROMPT_V2_PATH,
        repo_root=REPO_ROOT,
    )

    suffix_path = tmp_path / "brief_suffix.md"
    suffix_path.write_text(suffix)

    bundle_manifest_sha = brief_module.compute_bundle_manifest_sha(OH_2025_BUNDLE_DIR)

    reconstructed = brief_module.reconstruct_brief(
        suffix_path=suffix_path,
        bundle_dir=OH_2025_BUNDLE_DIR,
        bundle_manifest_sha=bundle_manifest_sha,
        scorer_prompt_path=SCORER_PROMPT_V2_PATH,
        repo_root=REPO_ROOT,
    )

    assert reconstructed == full_brief, "reconstruct_brief round-trip mismatch"


def test_extraction_brief_includes_chunk_frame_when_present():
    """When src/scoring/chunk_frames/<chunk>.md exists, the brief inlines it
    ahead of the row briefs so the agent gets a conceptual map of the chunk's
    axes before answering individual rows."""
    brief_module = _import_brief_module()
    full_brief, suffix = brief_module.build_extraction_brief(
        state="OH",
        vintage_year=2025,
        chunk="definitions",
        bundle_dir=OH_2025_BUNDLE_DIR,
        compendium_csv=COMPENDIUM_CSV,
        scorer_prompt_path=SCORER_PROMPT_V2_PATH,
        repo_root=REPO_ROOT,
    )
    chunk_frame_path = REPO_ROOT / "src" / "scoring" / "chunk_frames" / "definitions.md"
    assert chunk_frame_path.exists(), "definitions chunk frame must be present"
    frame_content = chunk_frame_path.read_text()

    # The frame's distinguishing prose appears in the suffix and the full brief.
    assert "Chunk frame: `definitions`" in frame_content
    assert "TARGET axis" in suffix
    assert "ACTOR axis" in suffix
    assert "THRESHOLD axis" in suffix
    # The frame appears before the row-briefs section (orientation precedes detail).
    frame_pos = suffix.find("TARGET axis")
    rows_pos = suffix.find("Compendium rows to extract")
    assert frame_pos < rows_pos, "chunk frame must precede the row briefs"


def test_extraction_brief_includes_v1_3_output_schema():
    """The brief's output-schema section names the v1.3 fields by name."""
    brief_module = _import_brief_module()
    full_brief, _suffix = brief_module.build_extraction_brief(
        state="OH",
        vintage_year=2025,
        chunk="definitions",
        bundle_dir=OH_2025_BUNDLE_DIR,
        compendium_csv=COMPENDIUM_CSV,
        scorer_prompt_path=SCORER_PROMPT_V2_PATH,
        repo_root=REPO_ROOT,
    )

    for v1_3_field in ("condition_text", "regime", "registrant_role"):
        assert v1_3_field in full_brief, (
            f"v1.3 schema field {v1_3_field} not surfaced in brief"
        )

    # The four v2 status values must appear (rule 5 of scorer_prompt_v2).
    for status_value in ("required_conditional", "not_required", "not_addressed"):
        assert status_value in full_brief, (
            f"v2 status value {status_value} not surfaced in brief"
        )
