"""Tests for the OH-portal OpenAI extraction wrapper.

The OpenAI API call itself is an external boundary and is NOT exercised here.
What IS tested:

  - The OpenAI extractor reuses `assemble_filing` from `extract.py`, so the
    raw_text / provenance invariants hold cross-provider. We do not redefine
    those tests — they live in test_oh_portal_extract.py and apply.
  - The schema OpenAI sees (strict-mode JSON schema generated from the
    LobbyingFiling Pydantic class) generates without error. This is a static
    structural check, not a network call.
  - `pipeline_openai.find_cached_html` correctly locates the latest cached
    raw.html for a report_id and surfaces missing-cache cases distinctly.

Phase 1 step 7 of the plan also calls for behavior tests against captured
Sonnet output for filing 1427844 (the hand-validated baseline). Those tests
require the cached HTML + Sonnet output on disk and are NOT part of this
test module — they live in the operator runbook as a manual diff check
before Phase 2 dispatch, gated on the actual extraction having been run.
"""

import json
from pathlib import Path

import pytest

from lobby_analysis.models.filings import LobbyingFiling
from lobby_analysis.oh_portal.pipeline_openai import find_cached_html


def test_strict_schema_translates_without_error() -> None:
    """LobbyingFiling produces a valid OpenAI strict-mode JSON schema.

    Regression guard: as the schema grows, the OpenAI strict-mode constraints
    (additionalProperties=false everywhere, all fields in `required`, ~5000
    property ceiling) could be silently violated. This test catches it before
    any 900-call dispatch tries to send the schema and fails uniformly.
    """
    from openai.lib._pydantic import to_strict_json_schema

    schema = to_strict_json_schema(LobbyingFiling)
    assert schema["type"] == "object"
    assert schema.get("additionalProperties") is False
    # Every nested object schema must also have additionalProperties=False
    # in strict mode; check that the generator enforced this.
    defs = schema.get("$defs", {})
    for name, sub in defs.items():
        if sub.get("type") == "object":
            assert sub.get("additionalProperties") is False, (
                f"$defs.{name} is missing additionalProperties=False; "
                f"OpenAI strict mode will reject this schema."
            )


def test_strict_schema_property_count_within_openai_ceiling() -> None:
    """Total object-property count stays under OpenAI's ~5000 ceiling.

    The limit was raised from 100 -> 5000 in July 2025. Current count is
    ~109; this test pins the order of magnitude so a future schema explosion
    (e.g., flattening BillReference inline into every position row) gets
    surfaced explicitly rather than via a runtime API rejection.
    """
    from openai.lib._pydantic import to_strict_json_schema

    schema = to_strict_json_schema(LobbyingFiling)

    def count_props(s: object) -> int:
        if isinstance(s, dict):
            n = len(s["properties"]) if (s.get("type") == "object" and "properties" in s) else 0
            return n + sum(count_props(v) for v in s.values())
        if isinstance(s, list):
            return sum(count_props(v) for v in s)
        return 0

    total = count_props(schema)
    assert total < 5000, f"schema has {total} properties; OpenAI ceiling is ~5000"
    # Sanity floor: if we accidentally drop most fields the test should fail.
    assert total > 50, f"schema has only {total} properties; suspiciously small"


def test_find_cached_html_returns_latest_timestamp(tmp_path: Path) -> None:
    """When multiple fetches cached for one report_id, pick the latest."""
    report_id = "1234567"
    raw_dir = tmp_path / "raw" / report_id
    early = raw_dir / "2026-06-04T10-00-00+00-00"
    late = raw_dir / "2026-06-05T15-30-00+00-00"
    for d in (early, late):
        d.mkdir(parents=True)
        (d / "raw.html").write_text(f"<html>from {d.name}</html>")

    got = find_cached_html(report_id, data_dir=tmp_path)
    assert got.parent == late
    assert "2026-06-05" in got.read_text()


def test_find_cached_html_raises_when_missing(tmp_path: Path) -> None:
    """Missing-cache case raises a distinguishable error (not silent re-fetch)."""
    with pytest.raises(FileNotFoundError) as exc_info:
        find_cached_html("9999999", data_dir=tmp_path)
    assert "9999999" in str(exc_info.value)


def test_find_cached_html_raises_when_dir_exists_but_no_raw_html(tmp_path: Path) -> None:
    """Half-populated cache (dir present, raw.html missing) raises clearly.

    Guards against silent fall-through to a stale or unrelated timestamp dir
    when the most recent fetch attempt crashed before writing raw.html.
    """
    report_id = "5555555"
    bad = tmp_path / "raw" / report_id / "2026-06-05T12-00-00+00-00"
    bad.mkdir(parents=True)
    # No raw.html written; only meta.json from a partial fetch.
    (bad / "meta.json").write_text(json.dumps({"url": "test"}))

    with pytest.raises(FileNotFoundError):
        find_cached_html(report_id, data_dir=tmp_path)
