"""Phase 3.5 — OH filings-level composer (Q6 → include, minimal v0 version).

Produces a per-filing TSV at ``releases/oh/filings/OH_filings_2025_2026.tsv``
that hosts two findings-doc normalizations that have no home in the
position-grain chain TSV or the per-event gifts TSV:

1. **Stated-zero normalization.** ``(total_expenditure is None AND
   len(expenditures) == 0) → 0.0``. Nil filings (no expenditures, no total)
   sum correctly downstream; analysts don't have to coalesce null. Only
   the (None, empty) pair normalizes: ``(None, non-empty)`` stays null
   so the upstream extraction inconsistency surfaces, not hides.

2. **is_current default-forcing.** ``(filing_action == 'original' AND
   supersedes is None) → is_current = True``. The "original + no supersedes"
   pair structurally implies "this is the latest version"; the AER
   extraction sometimes leaves ``is_current`` default-unset. Per Phase 0
   audit, 316/316 cached filings already carry ``is_current == True``,
   so this forcing is currently a no-op invariant guard rather than a
   correcting transform — kept against future cache drift.

Plan reference: ``docs/active/oh-portal-extraction/plans/20260611_oh_chain_composer_design.md`` §5 Phase 3.5
+ ``docs/active/leave-behind-prep/results/20260613_mini_swap_quality_gate_findings.md``.

Schema (14 columns), one row per canonical filing:

- ``filing_id``, ``report_period``
- ``principal_name``, ``principal_id``, ``lobbyist_name``, ``lobbyist_id``
- ``total_expenditure`` (post-normalize: never null when expenditures==[])
- ``is_current`` (post-force: True for original+no-supersedes)
- ``filing_action``, ``supersedes``
- ``n_positions``, ``n_gifts``, ``n_expenditures``
- ``extraction_warnings``
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from lobby_analysis.allocation.oh.chain import derive_org_id, derive_person_id
from lobby_analysis.allocation.oh.load import load_filings, select_canonical_extraction
from lobby_analysis.models.filings import LobbyingFiling

__all__ = ["FILINGS_COLUMNS", "compose_filings"]


FILINGS_COLUMNS: tuple[str, ...] = (
    "filing_id",
    "report_period",
    "principal_name",
    "principal_id",
    "lobbyist_name",
    "lobbyist_id",
    "total_expenditure",
    "is_current",
    "filing_action",
    "supersedes",
    "n_positions",
    "n_gifts",
    "n_expenditures",
    "extraction_warnings",
)


def _report_period(filing: LobbyingFiling) -> str:
    if filing.reporting_period_start and filing.reporting_period_end:
        return f"{filing.reporting_period_start}..{filing.reporting_period_end}"
    if filing.reporting_period_start:
        return str(filing.reporting_period_start)
    if filing.reporting_period_end:
        return str(filing.reporting_period_end)
    return ""


def _normalize_stated_zero(filing: LobbyingFiling) -> float | None:
    """Stated-zero rule: (total_expenditure is None AND expenditures==[]) → 0.0."""
    if filing.total_expenditure is None and len(filing.expenditures) == 0:
        return 0.0
    return filing.total_expenditure


def _force_is_current(filing: LobbyingFiling) -> bool:
    """is_current rule: original+no-supersedes → True. Else carry-through."""
    if filing.filing_action == "original" and filing.supersedes is None:
        return True
    return filing.is_current


def compose_filings(extractions_dir: Path) -> pd.DataFrame:
    """One row per canonical filing, with the two normalizations applied."""
    filings = select_canonical_extraction(load_filings(extractions_dir))

    rows: list[dict[str, object]] = []
    for _, frow in filings.iterrows():
        filing: LobbyingFiling = frow["filing_obj"]
        principal_name = filing.employer.name if filing.employer else None
        lobbyist_name = filing.filer_person.name if filing.filer_person else None
        rows.append(
            {
                "filing_id": filing.filing_id,
                "report_period": _report_period(filing),
                "principal_name": principal_name,
                # Derive principal_id / lobbyist_id from name (mirror of
                # the chain composer's Step-1 normalization — keeps the
                # filings TSV's ID columns join-consistent with the chain
                # TSV. Plan §"Step 1" lives on leave-behind-prep.)
                "principal_id": derive_org_id(principal_name),
                "lobbyist_name": lobbyist_name,
                "lobbyist_id": derive_person_id(lobbyist_name),
                "total_expenditure": _normalize_stated_zero(filing),
                "is_current": _force_is_current(filing),
                "filing_action": filing.filing_action,
                "supersedes": filing.supersedes,
                "n_positions": len(filing.positions),
                "n_gifts": len(filing.gifts),
                "n_expenditures": len(filing.expenditures),
                "extraction_warnings": list(filing.extraction_warnings),
            }
        )

    if not rows:
        return pd.DataFrame({c: [] for c in FILINGS_COLUMNS})
    return pd.DataFrame(rows, columns=list(FILINGS_COLUMNS))
