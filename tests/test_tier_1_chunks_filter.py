"""Behavior tests for the ``--chunks`` filter flag on the Tier-1 dispatcher.

Plan: docs/active/wi-ralph-cpi-renewal-cadence/plans/20260604_phase_b_ralph_renewal_cadence.md

The Phase B Ralph loop wants to dispatch ONE chunk at a time per iteration
(~$0.05-0.10 per round), not all six (~$2.50). The ``--chunks`` flag accepts
one or more chunk_ids from the ``_RESOLVED_CHUNKS`` list and restricts the
dispatch to just those chunks. When omitted, the dispatcher runs all six
chunks (current behavior; backward-compatible).

Tests below pin the behavior:

1. **Omitting --chunks preserves the all-six default.** A bare invocation
   resolves to the full ``_RESOLVED_CHUNKS`` tuple.
2. **--chunks <chunk_id> filters to one chunk.** Passing one chunk_id
   resolves to a tuple containing only that chunk_id.
3. **--chunks accepts multiple chunk_ids.** Passing two valid chunk_ids
   resolves to both.
4. **--chunks rejects unknown chunk_ids cleanly.** Passing an invalid
   chunk_id raises SystemExit with a message that names the bad chunk
   AND lists the valid options. No silent fall-through to "all chunks".

Real parse_args + resolve_active_chunks; no network, no model mocking.
"""

from __future__ import annotations

import importlib.util
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
# 1 — omitting --chunks preserves the all-six default
# ---------------------------------------------------------------------------


def test_omitting_chunks_resolves_to_all_six():
    args = tier1.parse_args(["--state", "WI", "--vintage", "2025"])
    resolved = tier1.resolve_active_chunks(args.chunks)
    assert resolved == tier1._RESOLVED_CHUNKS
    assert len(resolved) == 6


# ---------------------------------------------------------------------------
# 2 — --chunks <chunk_id> filters to one chunk
# ---------------------------------------------------------------------------


def test_single_chunk_arg_filters_to_one_chunk():
    args = tier1.parse_args(
        [
            "--state", "WI", "--vintage", "2025",
            "--chunks", "registration_mechanics_and_exemptions",
        ]
    )
    resolved = tier1.resolve_active_chunks(args.chunks)
    assert resolved == ("registration_mechanics_and_exemptions",)


# ---------------------------------------------------------------------------
# 3 — --chunks accepts multiple chunk_ids
# ---------------------------------------------------------------------------


def test_multiple_chunks_arg_filters_to_those_chunks():
    args = tier1.parse_args(
        [
            "--state", "WI", "--vintage", "2025",
            "--chunks",
            "registration_mechanics_and_exemptions",
            "lobbying_definitions",
        ]
    )
    resolved = tier1.resolve_active_chunks(args.chunks)
    assert set(resolved) == {
        "registration_mechanics_and_exemptions",
        "lobbying_definitions",
    }


# ---------------------------------------------------------------------------
# 4 — --chunks rejects unknown chunk_ids cleanly
# ---------------------------------------------------------------------------


def test_unknown_chunk_id_raises_with_valid_list_in_message():
    args = tier1.parse_args(
        [
            "--state", "WI", "--vintage", "2025",
            "--chunks", "nonexistent_chunk",
        ]
    )
    with pytest.raises(SystemExit) as exc_info:
        tier1.resolve_active_chunks(args.chunks)

    # Error message must (a) name the bad chunk, (b) list valid chunks —
    # silent fall-through to "all chunks" is the regression to prevent.
    msg = str(exc_info.value)
    assert "nonexistent_chunk" in msg
    for valid_chunk in tier1._RESOLVED_CHUNKS:
        assert valid_chunk in msg
