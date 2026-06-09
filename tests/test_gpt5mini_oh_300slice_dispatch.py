"""Tests for scripts/gpt5mini_oh_300slice_dispatch.py — the 2026-06-09 changes.

What is tested
--------------
1. `_process_one_filing` correctly threads `reasoning_effort` to
   `extract_one_filing_from_cache`.
2. `run_one_pass(max_concurrent=1)` (serial path) preserves byte-identical
   semantics for legacy callers — no executor, single-threaded, ordered
   results.
3. `run_one_pass(max_concurrent>1)` (parallel path) produces the same SET of
   results as serial on the same input (order is not promised under
   concurrency).
4. Both paths invoke `extract_one_filing_from_cache` with the supplied
   `reasoning_effort`.
5. Resume skip-check is concurrency-safe (multiple parallel workers reading
   the same already_extracted dir don't double-count or duplicate work).
6. `post_run1_sanity_diff` honors the parameterized run_label_prefix —
   passes filter to the right effort-coupled label, not the legacy hardcoded
   one.
7. Per-filing exceptions in the parallel path are isolated; one failure
   doesn't abort siblings.

What is NOT tested
------------------
- Network calls. We mock `extract_one_filing_from_cache` at the boundary.
- The wall-clock semantics under parallelism in detail (the "stop
  submitting new work" path). The implementation pre-checks the cap before
  each submit; a focused test would need controllable per-task sleep, which
  is brittle.
- argparse CLI plumbing (it's straightforward and exercised by the operator
  runbook).
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest


# Load the dispatch module by file path, since `scripts/` isn't a proper
# package on the Python path. This mirrors how the script's __main__ block
# expects to be invoked.
_REPO_ROOT = Path(__file__).resolve().parents[1]
_DISPATCH_PATH = _REPO_ROOT / "scripts" / "gpt5mini_oh_300slice_dispatch.py"


def _load_dispatch_module():
    """Import the dispatch script as a module, regardless of CWD."""
    spec = importlib.util.spec_from_file_location(
        "gpt5mini_oh_300slice_dispatch", _DISPATCH_PATH
    )
    assert spec and spec.loader, f"Cannot load {_DISPATCH_PATH}"
    module = importlib.util.module_from_spec(spec)
    sys.modules["gpt5mini_oh_300slice_dispatch"] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def dispatch_mod():
    return _load_dispatch_module()


def _make_extract_stub(
    *,
    usage_completion_tokens: int = 1000,
    usage_prompt_tokens: int = 4500,
) -> Any:
    """Build a stub for extract_one_filing_from_cache.

    The stub returns a (filing_path, usage) pair shaped like the real
    function would, and records the kwargs it was called with so tests can
    assert on threading.
    """
    calls: list[dict[str, Any]] = []

    def stub(report_id: str, **kwargs):
        calls.append({"report_id": report_id, **kwargs})
        # The dispatcher only uses the path for logging; any string works.
        fake_path = Path(f"/fake/{report_id}/filing.json")
        usage = {
            "prompt_tokens": usage_prompt_tokens,
            "completion_tokens": usage_completion_tokens,
            "total_tokens": usage_prompt_tokens + usage_completion_tokens,
            "reasoning_tokens": None,
            "reasoning_effort": kwargs.get("reasoning_effort"),
            "model": "gpt-5-mini-2025-08-07",
        }
        return fake_path, usage

    stub.calls = calls  # type: ignore[attr-defined]
    return stub


def test_process_one_filing_threads_reasoning_effort(
    dispatch_mod, tmp_path: Path
) -> None:
    """_process_one_filing forwards reasoning_effort to the extractor."""
    stub = _make_extract_stub()
    with patch.object(
        dispatch_mod, "extract_one_filing_from_cache", side_effect=stub
    ):
        result = dispatch_mod._process_one_filing(
            "1234567",
            run_label="mini_minimal_run_1",
            data_dir=tmp_path,
            resume=False,
            reasoning_effort="minimal",
            log=lambda _m: None,
        )
    assert result.status == "extracted"
    assert len(stub.calls) == 1
    assert stub.calls[0]["reasoning_effort"] == "minimal"
    assert stub.calls[0]["run_label"] == "mini_minimal_run_1"


def test_process_one_filing_resume_skip_short_circuits_extractor(
    dispatch_mod, tmp_path: Path
) -> None:
    """If already_extracted finds output, the extractor must not be called."""
    # Set up a fake already-extracted output
    report_id = "1234567"
    run_label = "mini_medium_run_1"
    run_dir = (
        tmp_path / "extracted_openai" / report_id /
        f"{run_label}_20260609T100000_abcdef01"
    )
    run_dir.mkdir(parents=True)
    (run_dir / "filing.json").write_text("{}")

    stub = _make_extract_stub()
    with patch.object(
        dispatch_mod, "extract_one_filing_from_cache", side_effect=stub
    ):
        result = dispatch_mod._process_one_filing(
            report_id,
            run_label=run_label,
            data_dir=tmp_path,
            resume=True,
            reasoning_effort="medium",
            log=lambda _m: None,
        )
    assert result.status == "skipped"
    assert len(stub.calls) == 0, "Extractor was called despite resume hit"


def test_run_one_pass_serial_preserves_order(
    dispatch_mod, tmp_path: Path
) -> None:
    """max_concurrent=1 dispatches in the input order, ordered results."""
    rids = ["1000001", "1000002", "1000003"]
    stub = _make_extract_stub()
    with patch.object(
        dispatch_mod, "extract_one_filing_from_cache", side_effect=stub
    ):
        results = dispatch_mod.run_one_pass(
            rids,
            run_label="mini_medium_run_1",
            data_dir=tmp_path,
            wall_clock_cap_s=3600,
            resume=False,
            log=lambda _m: None,
            reasoning_effort="medium",
            max_concurrent=1,
        )
    assert [r.report_id for r in results] == rids
    assert all(r.status == "extracted" for r in results)
    # Every extractor call carried the same reasoning_effort
    assert {c["reasoning_effort"] for c in stub.calls} == {"medium"}


def test_run_one_pass_parallel_processes_all_filings(
    dispatch_mod, tmp_path: Path
) -> None:
    """max_concurrent=5 produces the same SET of results as serial.

    Result order under concurrency is not promised, but every input report_id
    must appear exactly once in the output, and every output must be
    extracted (since our stub doesn't fail).
    """
    rids = [f"100000{i}" for i in range(10)]
    stub = _make_extract_stub()
    with patch.object(
        dispatch_mod, "extract_one_filing_from_cache", side_effect=stub
    ):
        results = dispatch_mod.run_one_pass(
            rids,
            run_label="mini_minimal_run_1",
            data_dir=tmp_path,
            wall_clock_cap_s=3600,
            resume=False,
            log=lambda _m: None,
            reasoning_effort="minimal",
            max_concurrent=5,
        )
    assert {r.report_id for r in results} == set(rids)
    assert len(results) == len(rids)
    assert all(r.status == "extracted" for r in results)
    assert {c["reasoning_effort"] for c in stub.calls} == {"minimal"}


def test_run_one_pass_parallel_isolates_per_filing_failures(
    dispatch_mod, tmp_path: Path
) -> None:
    """One filing failing under parallelism doesn't abort the others."""
    rids = ["good_1", "BAD", "good_2", "good_3"]

    def selective_failure(report_id: str, **kwargs):
        if report_id == "BAD":
            raise RuntimeError("simulated extractor failure")
        return _make_extract_stub()(report_id, **kwargs)

    with patch.object(
        dispatch_mod,
        "extract_one_filing_from_cache",
        side_effect=selective_failure,
    ):
        results = dispatch_mod.run_one_pass(
            rids,
            run_label="mini_low_run_1",
            data_dir=tmp_path,
            wall_clock_cap_s=3600,
            resume=False,
            log=lambda _m: None,
            reasoning_effort="low",
            max_concurrent=4,
        )
    by_rid = {r.report_id: r for r in results}
    assert by_rid["BAD"].status == "failed"
    assert "simulated extractor failure" in by_rid["BAD"].error
    for good_rid in ("good_1", "good_2", "good_3"):
        assert by_rid[good_rid].status == "extracted", (
            f"sibling {good_rid} was not extracted after BAD's failure"
        )


def test_run_one_pass_parallel_concurrency_safe_resume(
    dispatch_mod, tmp_path: Path
) -> None:
    """Resume skip-check works correctly across parallel workers.

    Pre-populate output for half the inputs; dispatch the full set under
    resume=True with concurrency > 1. The extractor stub must be called
    exactly once for each un-extracted report_id, and zero times for any
    pre-populated report_id.
    """
    rids = [f"200000{i}" for i in range(10)]
    run_label = "mini_medium_run_1"
    # Pre-populate evens
    pre_populated = {rids[i] for i in range(0, 10, 2)}
    for rid in pre_populated:
        d = (
            tmp_path / "extracted_openai" / rid /
            f"{run_label}_20260609T100000_deadbeef"
        )
        d.mkdir(parents=True)
        (d / "filing.json").write_text("{}")

    stub = _make_extract_stub()
    with patch.object(
        dispatch_mod, "extract_one_filing_from_cache", side_effect=stub
    ):
        results = dispatch_mod.run_one_pass(
            rids,
            run_label=run_label,
            data_dir=tmp_path,
            wall_clock_cap_s=3600,
            resume=True,
            log=lambda _m: None,
            reasoning_effort="medium",
            max_concurrent=5,
        )

    by_rid = {r.report_id: r for r in results}
    for rid in pre_populated:
        assert by_rid[rid].status == "skipped", (
            f"{rid} was re-extracted under resume"
        )
    for rid in set(rids) - pre_populated:
        assert by_rid[rid].status == "extracted"

    # Stub was called only for the un-extracted set
    called_rids = {c["report_id"] for c in stub.calls}
    assert called_rids == set(rids) - pre_populated


def test_post_run1_sanity_diff_honors_run_label_prefix(
    dispatch_mod, tmp_path: Path
) -> None:
    """Sanity diff finds outputs under the supplied prefix, not the legacy."""
    import json

    rid = "9000001"
    # Sonnet baseline
    sonnet = (
        tmp_path / "extracted" / rid / "sonnet_run_1_20260605T010000_baseline"
    )
    sonnet.mkdir(parents=True)
    (sonnet / "filing.json").write_text(json.dumps({
        "filer_name": "X", "filer_organization": None,
    }))
    # Effort-coupled mini output (no legacy mini_run_1_*)
    mini = (
        tmp_path / "extracted_openai" / rid /
        "mini_minimal_run_1_20260609T123000_abcdef01"
    )
    mini.mkdir(parents=True)
    (mini / "filing.json").write_text(json.dumps({
        "filer_name": "X", "filer_organization": "Y",
    }))

    # With the legacy default prefix → finds no mini output → 0 compared
    legacy = dispatch_mod.post_run1_sanity_diff([rid], tmp_path)
    assert legacy["n_compared"] == 0

    # With the new prefix → finds the output → 1 compared
    new = dispatch_mod.post_run1_sanity_diff(
        [rid], tmp_path, run_label_prefix="mini_minimal_run_1_"
    )
    assert new["n_compared"] == 1
