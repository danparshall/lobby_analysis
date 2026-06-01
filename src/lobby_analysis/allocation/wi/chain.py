"""WI end-to-end chain composer (Phase 3 step 38 — RED stub).

Stitches the Phase 2 allocation matrix together with the bill-effort filings
and the legislature bill metadata into one row per
(semester, principal, lobbyist, bill, sponsor) tuple — the chain Suhan asked
for: company → lobbyist → bill → lawmaker.

RED STUB — definition exists so tests collect cleanly. Implementation lands
in the GREEN commit that follows.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from lobby_analysis.allocation.wi.legislature import BillMetadata

__all__ = ["compose_chain"]


def compose_chain(
    allocation_dir: Path,
    release_dir: Path,
    bill_metadata: dict[str, BillMetadata],
) -> pd.DataFrame:
    """Compose the principal → lobbyist → bill → sponsor chain table."""
    raise NotImplementedError("Phase 3 step 40 GREEN")
