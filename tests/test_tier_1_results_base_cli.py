"""CLI test for the ``--results-base`` flag on the Tier-1 dispatcher.

Plan: docs/historical/wi-ralph-cpi-renewal-cadence/plans/20260605_cross_state_cpi_2015_validation.md

The dispatcher's ``_DEFAULT_RESULTS_BASE`` is hardcoded to
``docs/active/wi-tier1-direct-read/results/tier_1/`` (now archived). For the
cross-state validation round, results need to land under
``docs/active/cross-state-cpi-2015-validation/results/tier_1/<STATE>_<VINTAGE>/``.
``resolve_results_dir`` already accepts a ``results_base=`` kwarg; this test
file pins the CLI surface for that override.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
_TIER_1_PATH = _SCRIPTS / "tier_1_direct_read_legal_axis.py"


def _load(module_name: str, path: Path):
    spec = importlib.util.spec_from_file_location(module_name, path)
    assert spec is not None and spec.loader is not None, f"could not load {path}"
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


tier1 = _load("tier_1_direct_read_legal_axis", _TIER_1_PATH)


def test_results_base_omitted_defaults_to_none():
    """No ``--results-base`` -> ``args.results_base`` is None.

    None is the sentinel ``main()`` translates to the legacy default
    (``_DEFAULT_RESULTS_BASE``), preserving backward compatibility for any
    caller still relying on the hardcoded path.
    """
    args = tier1.parse_args(["--state", "NY", "--vintage", "2015"])
    assert args.results_base is None


def test_results_base_accepts_path_override():
    """``--results-base /tmp/foo`` -> ``args.results_base == Path('/tmp/foo')``.

    The override gets forwarded to ``resolve_results_dir(..., results_base=)``,
    which already supports the kwarg (see ``test_tier_1_state_keying.py``
    ``test_resume_isolation_across_states``).
    """
    args = tier1.parse_args(
        ["--state", "NY", "--vintage", "2015", "--results-base", "/tmp/foo"]
    )
    assert args.results_base == Path("/tmp/foo")


def test_results_base_threads_into_resolve_results_dir():
    """End-to-end: parsed ``--results-base`` resolves to the right per-state dir.

    Pins the contract ``main()`` uses: take ``args.results_base``, hand it to
    ``resolve_results_dir(state, vintage, results_base=...)``, and the returned
    path is ``<results_base>/<STATE>_<VINTAGE>``.
    """
    args = tier1.parse_args(
        [
            "--state",
            "NY",
            "--vintage",
            "2015",
            "--results-base",
            "/tmp/cross_state_demo",
        ]
    )
    results_dir = tier1.resolve_results_dir(
        args.state, args.vintage, results_base=args.results_base
    )
    assert results_dir == Path("/tmp/cross_state_demo/NY_2015")
