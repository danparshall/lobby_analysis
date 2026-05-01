"""TDD tests for v1.3 provenance extension.

Phase 2 of plans/20260501_statute_extraction_harness.md adds a new
`ExtractionRunMetadata` model to scoring/models.py and helpers
`compute_compendium_sha` + `compute_bundle_manifest_sha` to
scoring/provenance.py. These tests are expected to fail until the
implementation lands.

Tests target behavior — round-trip equality, sha shape, field presence
— against the real OH 2025 bundle and the real compendium CSV.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
COMPENDIUM_CSV = REPO_ROOT / "compendium" / "disclosure_items.csv"
OH_2025_BUNDLE_DIR = REPO_ROOT / "data" / "statutes" / "OH" / "2025"

_HEX64 = re.compile(r"^[0-9a-f]{64}$")


pytestmark = pytest.mark.skipif(
    not OH_2025_BUNDLE_DIR.exists() or not COMPENDIUM_CSV.exists(),
    reason="OH 2025 bundle or compendium CSV not present",
)


def _build_meta(**overrides):
    from scoring.models import ExtractionRunMetadata

    defaults = dict(
        state="OH",
        run_id="abc123def456",
        run_timestamp_utc="2026-05-01T18:30:00+00:00",
        vintage_year=2025,
        chunk="definitions",
        prompt_sha="0" * 64,
        bundle_manifest_sha="1" * 64,
        compendium_csv_sha="2" * 64,
        model_version="claude-opus-4-7",
        iteration_label="iter-1",
        prior_run_id=None,
        changes_from_prior="first iteration baseline",
    )
    return ExtractionRunMetadata(**{**defaults, **overrides})


def test_meta_json_includes_iteration_label():
    """`iteration_label`, `prior_run_id`, `changes_from_prior` all serialize."""
    meta = _build_meta(
        iteration_label="iter-1",
        prior_run_id=None,
        changes_from_prior="first iteration baseline",
    )
    payload = meta.model_dump_json()

    assert '"iteration_label":"iter-1"' in payload
    assert '"prior_run_id":null' in payload
    assert '"changes_from_prior":"first iteration baseline"' in payload


def test_meta_json_includes_provenance_shas():
    """`prompt_sha`, `bundle_manifest_sha`, `compendium_csv_sha`, `chunk` populate.

    Computed shas (from real bundle + real CSV) must validate as 64-char hex.
    """
    from scoring.provenance import (
        compute_bundle_manifest_sha,
        compute_compendium_sha,
    )

    bundle_sha = compute_bundle_manifest_sha(OH_2025_BUNDLE_DIR)
    compendium_sha = compute_compendium_sha(COMPENDIUM_CSV)

    assert _HEX64.match(bundle_sha), f"bundle sha not 64-hex: {bundle_sha!r}"
    assert _HEX64.match(compendium_sha), f"compendium sha not 64-hex: {compendium_sha!r}"

    meta = _build_meta(
        bundle_manifest_sha=bundle_sha,
        compendium_csv_sha=compendium_sha,
        chunk="definitions",
    )
    assert meta.bundle_manifest_sha == bundle_sha
    assert meta.compendium_csv_sha == compendium_sha
    assert meta.chunk == "definitions"


def test_meta_json_round_trip():
    """Serialize then deserialize → byte-identical."""
    from scoring.models import ExtractionRunMetadata

    meta = _build_meta(
        prior_run_id="prior_run_99",
        changes_from_prior="dropped Rule 7 sidecar; added per-domain notes",
    )
    payload = meta.model_dump_json()
    meta2 = ExtractionRunMetadata.model_validate_json(payload)
    assert meta2.model_dump_json() == payload
