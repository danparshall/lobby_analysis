"""Coverage-tier mapping per the 2026-04-13 snapshot sufficiency audit.

Sources:
- docs/historical/pri-2026-rescore/results/20260413_stage1_stage2_collection_summary.md
- docs/historical/focal-extraction/results/20260413_snapshot_sufficiency_audit.md
"""

from __future__ import annotations

from scoring.models import CoverageTier

PARTIAL_WAF: set[str] = {"MA", "NH", "MI", "CT", "DE", "KS", "CA", "NC", "IL"}
SPA_PENDING_PLAYWRIGHT: set[str] = {"GA", "ID", "ND", "SC", "NM", "ME", "AR", "IN", "PA"}
INACCESSIBLE: set[str] = {"AZ", "VT"}


def coverage_tier_for(state_abbr: str) -> CoverageTier:
    abbr = state_abbr.upper()
    if abbr in INACCESSIBLE:
        return "inaccessible"
    if abbr in PARTIAL_WAF:
        # MI appears in both partial-WAF and SPA lists in the source docs; partial-WAF is the
        # more informative label for scoring (WAF-blocked evidence, not just SPA shells).
        return "partial_waf"
    if abbr in SPA_PENDING_PLAYWRIGHT:
        return "spa_pending_playwright"
    return "clean"
