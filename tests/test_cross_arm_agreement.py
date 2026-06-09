"""Tests for scripts/gpt5mini_oh_300slice_cross_arm_agreement.py.

Verifies:
1. The both-null / one-null / agree / disagree bucketing matches the
   2026-06-09 design call (both-null is NOT agreement).
2. Named-object fields compare by name, not full object.
3. List-valued fields compare by length.
4. The intersection scan finds report_ids present in all four arms.
5. The arm-pair loader uses the right run_label prefix.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
_SCRIPT_PATH = (
    _REPO_ROOT / "scripts" / "gpt5mini_oh_300slice_cross_arm_agreement.py"
)


def _load_script():
    spec = importlib.util.spec_from_file_location(
        "cross_arm_agreement", _SCRIPT_PATH
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["cross_arm_agreement"] = module
    spec.loader.exec_module(module)
    return module


def _write_filing(
    data_dir: Path, *, arm: str, rid: str, payload: dict
) -> None:
    """Write a fake filing.json into the on-disk layout the script expects."""
    if arm == "sonnet":
        d = data_dir / "extracted" / rid / "sonnet_run_abcd1234"
    else:
        prefix = f"mini_{arm}_run_1"
        d = data_dir / "extracted_openai" / rid / f"{prefix}_20260609T120000_aabb1122"
    d.mkdir(parents=True)
    (d / "filing.json").write_text(json.dumps(payload))


def _make_payload(**overrides):
    """Minimum-viable filing.json payload — only the fields the script reads."""
    base = {
        "id": "f-x",
        "state": "OH",
        "filing_type": "activity_report",
        "filer_role": "lobbyist",
        "reporting_period_start": "2025-01-01",
        "reporting_period_end": "2025-06-30",
        "total_compensation": "1000.00",
        "is_itemized": False,
        "positions": [{"a": 1}, {"a": 2}],
        "filer_organization": {"id": "o-1", "name": "Acme Lobbying LLC"},
        "extraction_warnings": [],
    }
    base.update(overrides)
    return base


def test_both_null_is_not_agreement(tmp_path: Path) -> None:
    """Bucketing: both arms null on a field → both_null, NOT both_emitted_agree."""
    mod = _load_script()
    rid = "9000001"
    _write_filing(
        tmp_path, arm="sonnet", rid=rid,
        payload=_make_payload(total_compensation=None),
    )
    _write_filing(
        tmp_path, arm="medium", rid=rid,
        payload=_make_payload(total_compensation=None),
    )
    _write_filing(
        tmp_path, arm="low", rid=rid,
        payload=_make_payload(total_compensation=None),
    )
    _write_filing(
        tmp_path, arm="minimal", rid=rid,
        payload=_make_payload(total_compensation=None),
    )

    stats, n = mod.compare_pair([rid], "sonnet", "medium", tmp_path)
    s = stats["total_compensation"]
    assert s["both_null"] == 1
    assert s["both_emitted_agree"] == 0
    assert s["both_emitted_disagree"] == 0
    assert s["one_null"] == 0
    assert n == 1


def test_one_null_counts_as_disagreement_via_one_null_bucket(
    tmp_path: Path,
) -> None:
    """One arm null + the other emits → one_null bucket (NOT counted as agree)."""
    mod = _load_script()
    rid = "9000002"
    _write_filing(tmp_path, arm="sonnet", rid=rid, payload=_make_payload())
    _write_filing(
        tmp_path, arm="medium", rid=rid,
        payload=_make_payload(reporting_period_start=None),
    )
    _write_filing(tmp_path, arm="low", rid=rid, payload=_make_payload())
    _write_filing(tmp_path, arm="minimal", rid=rid, payload=_make_payload())

    stats, _ = mod.compare_pair([rid], "sonnet", "medium", tmp_path)
    s = stats["reporting_period_start"]
    assert s["one_null"] == 1
    assert s["both_emitted_agree"] == 0
    assert s["both_emitted_disagree"] == 0


def test_both_emitted_agree_when_values_equal(tmp_path: Path) -> None:
    mod = _load_script()
    rid = "9000003"
    payload = _make_payload(reporting_period_start="2025-01-01")
    for arm in ("sonnet", "medium", "low", "minimal"):
        _write_filing(tmp_path, arm=arm, rid=rid, payload=payload)

    stats, _ = mod.compare_pair([rid], "sonnet", "medium", tmp_path)
    s = stats["reporting_period_start"]
    assert s["both_emitted_agree"] == 1
    assert s["both_emitted_disagree"] == 0
    assert s["both_null"] == 0


def test_both_emitted_disagree_when_values_differ(tmp_path: Path) -> None:
    mod = _load_script()
    rid = "9000004"
    _write_filing(
        tmp_path, arm="sonnet", rid=rid,
        payload=_make_payload(total_compensation="1000.00"),
    )
    _write_filing(
        tmp_path, arm="medium", rid=rid,
        payload=_make_payload(total_compensation="999.00"),
    )
    _write_filing(tmp_path, arm="low", rid=rid, payload=_make_payload())
    _write_filing(tmp_path, arm="minimal", rid=rid, payload=_make_payload())

    stats, _ = mod.compare_pair([rid], "sonnet", "medium", tmp_path)
    s = stats["total_compensation"]
    assert s["both_emitted_disagree"] == 1
    assert s["both_emitted_agree"] == 0


def test_named_object_fields_compare_by_name(tmp_path: Path) -> None:
    """filer_organization.name match → agreement, even if other fields differ."""
    mod = _load_script()
    rid = "9000005"
    _write_filing(
        tmp_path, arm="sonnet", rid=rid,
        payload=_make_payload(
            filer_organization={"id": "o-1", "name": "Acme", "address": "x"},
        ),
    )
    _write_filing(
        tmp_path, arm="medium", rid=rid,
        payload=_make_payload(
            filer_organization={"id": "o-2", "name": "Acme", "address": "y"},
        ),
    )
    _write_filing(tmp_path, arm="low", rid=rid, payload=_make_payload())
    _write_filing(tmp_path, arm="minimal", rid=rid, payload=_make_payload())

    stats, _ = mod.compare_pair([rid], "sonnet", "medium", tmp_path)
    s = stats["filer_organization"]
    assert s["both_emitted_agree"] == 1, (
        "Same name across differing object detail should count as agreement"
    )


def test_list_fields_compare_by_length(tmp_path: Path) -> None:
    """Lists with same length but different content → agreement (by design)."""
    mod = _load_script()
    rid = "9000006"
    _write_filing(
        tmp_path, arm="sonnet", rid=rid,
        payload=_make_payload(positions=[{"a": 1}, {"a": 2}]),
    )
    _write_filing(
        tmp_path, arm="medium", rid=rid,
        payload=_make_payload(positions=[{"b": 99}, {"b": 100}]),
    )
    _write_filing(tmp_path, arm="low", rid=rid, payload=_make_payload())
    _write_filing(tmp_path, arm="minimal", rid=rid, payload=_make_payload())

    stats, _ = mod.compare_pair([rid], "sonnet", "medium", tmp_path)
    assert stats["positions"]["both_emitted_agree"] == 1

    # And a counter-example: different lengths → disagreement
    rid2 = "9000007"
    _write_filing(
        tmp_path, arm="sonnet", rid=rid2,
        payload=_make_payload(positions=[{"a": 1}]),
    )
    _write_filing(
        tmp_path, arm="medium", rid=rid2,
        payload=_make_payload(positions=[{"a": 1}, {"a": 2}, {"a": 3}]),
    )
    _write_filing(tmp_path, arm="low", rid=rid2, payload=_make_payload())
    _write_filing(tmp_path, arm="minimal", rid=rid2, payload=_make_payload())
    stats2, _ = mod.compare_pair([rid2], "sonnet", "medium", tmp_path)
    assert stats2["positions"]["both_emitted_disagree"] == 1


def test_intersection_finds_only_rids_in_all_four_arms(tmp_path: Path) -> None:
    """find_intersection_rids: rid missing in any arm is dropped."""
    mod = _load_script()
    # rid_all: present in all four arms → included
    rid_all = "8000001"
    for arm in ("sonnet", "medium", "low", "minimal"):
        _write_filing(tmp_path, arm=arm, rid=rid_all, payload=_make_payload())
    # rid_minimal_missing: present everywhere except minimal → dropped
    rid_partial = "8000002"
    for arm in ("sonnet", "medium", "low"):
        _write_filing(tmp_path, arm=arm, rid=rid_partial, payload=_make_payload())

    intersection, skipped = mod.find_intersection_rids(tmp_path)
    assert rid_all in intersection
    assert rid_partial not in intersection
    assert skipped["minimal"] >= 1
