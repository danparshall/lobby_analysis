"""Behavior tests for Tier-1 state/vintage parameterization + output isolation.

Plan: docs/active/wi-tier1-direct-read/plans/20260530_wi_2025_tier1_direct_read.md

The Tier-1 script originally hardcoded `_STATE_ABBR = "OH"` / `_VINTAGE_YEAR =
2025` and an un-state-keyed results directory. Both states therefore shared
`results/tier_1/`, so a second state's run would resume-skip every dispatch
against the first state's result files and silently emit the wrong state's
answers. These tests pin the behavior that prevents that:

1. **Collision isolation** — (WI, 2025) and (OH, 2025) resolve to *different*
   results directories, so a WI run can never write into or read from the OH
   pilot's files.
2. **Resume isolation** — `is_dispatch_done(...)` is False for a (WI, 2025)
   triple when only the corresponding (OH, 2025) file exists on disk.
3. **Argument threading** — `--state WI --vintage 2025` resolves the bundle to
   `data/statutes/WI/2025/sections` and the results dir to the WI-keyed path,
   with no API dispatch.
4. **Required args** — `--state`/`--vintage` are required (no default), so a
   bare invocation cannot accidentally re-run OH.
5. **OH still resolves the original-style bundle path** — passing OH/2025
   resolves `data/statutes/OH/2025/sections`, so the existing OH pilot's
   statute bundle is read from the same place as before.

Real path-resolution and resume logic; no network, no model mocking.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

_SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
_TIER_0_PATH = _SCRIPTS / "tier_0_direct_read_smoke.py"
_TIER_1_PATH = _SCRIPTS / "tier_1_direct_read_legal_axis.py"


def _load(module_name: str, path: Path):
    spec = importlib.util.spec_from_file_location(module_name, path)
    assert spec is not None and spec.loader is not None, f"could not load {path}"
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


tier0 = _load("tier_0_direct_read_smoke", _TIER_0_PATH)
tier1 = _load("tier_1_direct_read_legal_axis", _TIER_1_PATH)


# ---------------------------------------------------------------------------
# 1 — collision isolation: WI and OH resolve to different results dirs
# ---------------------------------------------------------------------------


def test_results_dir_is_state_vintage_keyed():
    wi = tier1.resolve_results_dir("WI", 2025)
    oh = tier1.resolve_results_dir("OH", 2025)
    assert wi != oh
    assert wi.name == "WI_2025"
    assert oh.name == "OH_2025"


def test_results_dir_keyed_by_vintage_too():
    """Same state, different vintages must not collide either."""
    assert tier1.resolve_results_dir("OH", 2025) != tier1.resolve_results_dir("OH", 2010)


# ---------------------------------------------------------------------------
# 2 — resume isolation: only-OH-files-on-disk must not mark WI dispatch done
# ---------------------------------------------------------------------------


def test_resume_isolation_across_states(tmp_path):
    model, chunk_id, run_idx = "claude-opus-4-7", "registration_thresholds", 1
    oh_dir = tier1.resolve_results_dir("OH", 2025, results_base=tmp_path)
    wi_dir = tier1.resolve_results_dir("WI", 2025, results_base=tmp_path)

    # Place an OH result file only.
    oh_path = tier1.dispatch_result_path(oh_dir, model, chunk_id, run_idx)
    oh_path.parent.mkdir(parents=True, exist_ok=True)
    oh_path.write_text(json.dumps({"provenance": {"state_abbr": "OH"}}), encoding="utf-8")

    # OH sees it done; WI must not — the bug this change exists to prevent.
    assert tier1.is_dispatch_done(oh_dir, model, chunk_id, run_idx) is True
    assert tier1.is_dispatch_done(wi_dir, model, chunk_id, run_idx) is False


# ---------------------------------------------------------------------------
# 3 — CLI args thread into the resolved bundle + results paths
# ---------------------------------------------------------------------------


def test_cli_args_set_bundle_and_results_paths():
    args = tier1.parse_args(["--state", "WI", "--vintage", "2025"])
    assert args.state == "WI"
    assert args.vintage == 2025

    bundle = tier1.resolve_bundle_dir(args.state, args.vintage)
    assert bundle.parts[-3:] == ("WI", "2025", "sections")

    results = tier1.resolve_results_dir(args.state, args.vintage)
    assert results.name == "WI_2025"


# ---------------------------------------------------------------------------
# 4 — required args: no default, bare invocation cannot re-run OH
# ---------------------------------------------------------------------------


def test_state_and_vintage_are_required():
    with pytest.raises(SystemExit):
        tier1.parse_args([])
    with pytest.raises(SystemExit):
        tier1.parse_args(["--state", "WI"])
    with pytest.raises(SystemExit):
        tier1.parse_args(["--vintage", "2025"])


# ---------------------------------------------------------------------------
# 5 — OH still resolves the original-style bundle path
# ---------------------------------------------------------------------------


def test_oh_resolves_original_style_bundle_path():
    bundle = tier1.resolve_bundle_dir("OH", 2025)
    assert bundle.parts[-3:] == ("OH", "2025", "sections")
    assert bundle.parts[-4] == "statutes"
