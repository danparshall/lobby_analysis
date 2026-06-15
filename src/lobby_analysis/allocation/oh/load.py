"""Phase 1 Step C — typed DataFrame loaders for the OH chain composer.

Loads the two raw inputs the chain composer joins against:

1. **OH AER extractions** under ``data/oh_portal/extracted/*/*/filing.json``
   (one ``LobbyingFiling`` per file). Three loaders project the nested
   filing structure into flat per-grain DataFrames:

   - :func:`load_filings` — one row per filing
   - :func:`load_positions` — one row per (filing, position)
   - :func:`load_gifts` — one row per (filing, gift)

   Each DataFrame carries the original Pydantic model in an ``*_obj`` column
   so downstream composers can call typed accessors (notably the Phase-1
   classifiers in :mod:`.classify`) without re-parsing.

2. **Plural Policy 136th GA bundle** under ``data/bills/OH/136/*.csv``:

   - :func:`load_plural_bills` — bills table, with a ``identifier_norm``
     column applying the smoke-test normalization (uppercase + dot-strip +
     whitespace-collapse) for direct join against extraction labels.
   - :func:`load_plural_sponsorships` — sponsorships table, filtered by
     classification (default ``"primary"`` per Q2 v1 scope).

Plan reference: ``docs/active/oh-portal-extraction/plans/20260611_oh_chain_composer_design.md`` §5 Phase 1.

Per Phase 0 audit (``results/20260614_phase0_preflight_audit.md``):

- ``bill_actions.description`` does NOT carry cosponsor names — Q2 v1.1
  cosponsor extension is just a classification-filter flip in this loader.
- 40.8% of OH bills have ≥2 primary sponsors — ``load_plural_sponsorships``
  with the default filter preserves that signal (one row per primary).

Empty/defective positions are NOT pre-filtered. The :mod:`.classify`
contract is to raise on empty positions; the loader keeps them in the
DataFrame so the chain composer surfaces the upstream extraction defect
rather than silently dropping rows.
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from lobby_analysis.models.filings import LobbyingFiling

__all__ = [
    "load_filings",
    "load_positions",
    "load_gifts",
    "load_plural_bills",
    "load_plural_sponsorships",
    "select_canonical_extraction",
]


# ---------------------------------------------------------------------------
# Column manifests (so empty-input cases still emit correct shape)
# ---------------------------------------------------------------------------

_FILINGS_COLUMNS = (
    "filing_id",
    "source_path",
    "state",
    "filer_role",
    "lobbyist_name",
    "principal_name",
    "reporting_period_start",
    "reporting_period_end",
    "filed_date",
    "filing_action",
    "supersedes",
    "is_current",
    "total_expenditure",
    "total_compensation",
    "n_expenditures",
    "n_positions",
    "n_gifts",
    "n_engagements",
    "filing_obj",
)

_POSITIONS_COLUMNS = (
    "filing_id",
    "position_index",
    "position_obj",
    "principal_name",
    "lobbyist_name",
    "reporting_period_start",
    "reporting_period_end",
    "filing_action",
    "is_current",
)

_GIFTS_COLUMNS = (
    "filing_id",
    "gift_index",
    "gift_obj",
    "principal_name",
    "lobbyist_name",
    "reporting_period_start",
    "reporting_period_end",
)


def _empty_df(columns: tuple[str, ...]) -> pd.DataFrame:
    return pd.DataFrame({c: [] for c in columns})


# ---------------------------------------------------------------------------
# Extraction-side loaders
# ---------------------------------------------------------------------------


def _iter_filing_paths(extractions_dir: Path) -> list[Path]:
    """Walk ``extractions_dir/*/*/filing.json`` deterministically (sorted)."""
    return sorted(extractions_dir.glob("*/*/filing.json"))


def _load_filing_obj(fp: Path) -> LobbyingFiling:
    """Parse one filing.json into a ``LobbyingFiling`` Pydantic model."""
    return LobbyingFiling.model_validate(json.loads(fp.read_text()))


def _filer_lobbyist_name(filing: LobbyingFiling) -> str | None:
    """Resolve the lobbyist display name from filer_person."""
    if filing.filer_person is not None:
        return filing.filer_person.name
    return None


def _principal_name(filing: LobbyingFiling) -> str | None:
    """Resolve the principal display name from employer."""
    if filing.employer is not None:
        return filing.employer.name
    return None


def load_filings(extractions_dir: Path) -> pd.DataFrame:
    """Load one row per ``LobbyingFiling`` under ``extractions_dir``.

    Walks ``<extractions_dir>/<dir>/<hash>/filing.json``. Each row carries
    filing-level scalars (period, action, totals, sub-entity counts) plus
    the typed ``LobbyingFiling`` Pydantic model in ``filing_obj``.

    Empty input directories return an empty DataFrame with the full column
    set — downstream code can depend on column shape without a "but only
    if non-empty" caveat.
    """
    paths = _iter_filing_paths(extractions_dir)
    if not paths:
        return _empty_df(_FILINGS_COLUMNS)

    rows: list[dict[str, object]] = []
    for fp in paths:
        filing = _load_filing_obj(fp)
        rows.append(
            {
                "filing_id": filing.filing_id,
                "source_path": str(fp),
                "state": filing.state,
                "filer_role": filing.filer_role,
                "lobbyist_name": _filer_lobbyist_name(filing),
                "principal_name": _principal_name(filing),
                "reporting_period_start": filing.reporting_period_start,
                "reporting_period_end": filing.reporting_period_end,
                "filed_date": filing.filed_date,
                "filing_action": filing.filing_action,
                "supersedes": filing.supersedes,
                "is_current": filing.is_current,
                "total_expenditure": filing.total_expenditure,
                "total_compensation": filing.total_compensation,
                "n_expenditures": len(filing.expenditures),
                "n_positions": len(filing.positions),
                "n_gifts": len(filing.gifts),
                "n_engagements": len(filing.engagements),
                "filing_obj": filing,
            }
        )
    return pd.DataFrame(rows, columns=list(_FILINGS_COLUMNS))


def load_positions(extractions_dir: Path) -> pd.DataFrame:
    """Load one row per (filing, position) across ``extractions_dir``.

    ``position_obj`` is the typed ``LobbyingPosition`` so downstream
    composers can call the Phase-1 classifiers without re-parsing.
    Filings with empty ``positions`` produce zero rows.

    Position rows are NOT pre-filtered for emptiness — the classifier
    contract is to raise on empty positions, surfacing the upstream
    extraction defect at the composition seam rather than here.
    """
    paths = _iter_filing_paths(extractions_dir)
    if not paths:
        return _empty_df(_POSITIONS_COLUMNS)

    rows: list[dict[str, object]] = []
    for fp in paths:
        filing = _load_filing_obj(fp)
        lobbyist = _filer_lobbyist_name(filing)
        principal = _principal_name(filing)
        for idx, position in enumerate(filing.positions):
            rows.append(
                {
                    "filing_id": filing.filing_id,
                    "position_index": idx,
                    "position_obj": position,
                    "principal_name": principal,
                    "lobbyist_name": lobbyist,
                    "reporting_period_start": filing.reporting_period_start,
                    "reporting_period_end": filing.reporting_period_end,
                    "filing_action": filing.filing_action,
                    "is_current": filing.is_current,
                }
            )
    if not rows:
        return _empty_df(_POSITIONS_COLUMNS)
    return pd.DataFrame(rows, columns=list(_POSITIONS_COLUMNS))


def load_gifts(extractions_dir: Path) -> pd.DataFrame:
    """Load one row per (filing, gift) across ``extractions_dir``.

    Inputs are AER Section II.A (gifts) + II.B (meals), parsed into the
    typed ``Gift`` model on each filing. Phase 3 (gifts edge composer)
    consumes this DataFrame.
    """
    paths = _iter_filing_paths(extractions_dir)
    if not paths:
        return _empty_df(_GIFTS_COLUMNS)

    rows: list[dict[str, object]] = []
    for fp in paths:
        filing = _load_filing_obj(fp)
        lobbyist = _filer_lobbyist_name(filing)
        principal = _principal_name(filing)
        for idx, gift in enumerate(filing.gifts):
            rows.append(
                {
                    "filing_id": filing.filing_id,
                    "gift_index": idx,
                    "gift_obj": gift,
                    "principal_name": principal,
                    "lobbyist_name": lobbyist,
                    "reporting_period_start": filing.reporting_period_start,
                    "reporting_period_end": filing.reporting_period_end,
                }
            )
    if not rows:
        return _empty_df(_GIFTS_COLUMNS)
    return pd.DataFrame(rows, columns=list(_GIFTS_COLUMNS))


# ---------------------------------------------------------------------------
# Plural Policy CSV loaders
# ---------------------------------------------------------------------------


def _normalize_identifier(s: str) -> str:
    """Smoke-test identifier normalization for direct join.

    Mirrors the normalization in ``results/20260611_plural_policy_join_smoke.py``:
    upper-case, drop dots, collapse internal whitespace.
    """
    import re

    if s is None:
        return ""
    s = re.sub(r"\s+", " ", s.strip().upper())
    s = s.replace(".", "")
    s = re.sub(r"\s+", " ", s).strip()
    return s


def load_plural_bills(plural_dir: Path) -> pd.DataFrame:
    """Load ``OH_136_bills.csv`` with a derived ``identifier_norm`` column.

    The ``identifier_norm`` column is the join key against extraction-side
    normalized bill labels (see :func:`_normalize_identifier`). All other
    columns are passed through from the CSV.
    """
    fp = plural_dir / "OH_136_bills.csv"
    df = pd.read_csv(fp, dtype=str).fillna("")
    df["identifier_norm"] = df["identifier"].map(_normalize_identifier)
    # bill_id is the canonical OCD ID; the CSV column is named "id"
    df = df.rename(columns={"id": "bill_id"})
    return df


def select_canonical_extraction(filings: pd.DataFrame) -> pd.DataFrame:
    """Pick one row per ``filing_id`` — the canonical extraction.

    The 2026-06-14 real-data smoke test surfaced that 5 filing_ids in the
    316-filing OH AER cache have multiple cached extractions (one filing
    has 8). The loaders deliberately do NOT pre-filter — they emit every
    extraction so the dedup choice lives at one obvious seam. The chain
    composer (Phase 2) is the consumer that needs canonical rows; this
    helper is the seam.

    Strategy: most-recent ``filing.json`` mtime wins; lexicographically
    larger ``source_path`` is the deterministic tie-breaker when mtimes
    are identical. Most-recent is the right semantic for the chain
    preview release — an updated extraction supersedes a prior one.

    Empty input yields empty output (no-op).
    """
    if len(filings) == 0:
        return filings.copy()

    paths_by_idx = {idx: Path(p) for idx, p in zip(filings.index, filings["source_path"])}
    mtimes = filings.index.to_series().map(
        lambda idx: paths_by_idx[idx].stat().st_mtime if paths_by_idx[idx].exists() else 0.0
    )
    # Sort by (mtime, source_path), descending; first row per filing_id wins.
    ordered = filings.assign(_mtime=mtimes.values).sort_values(
        ["filing_id", "_mtime", "source_path"],
        ascending=[True, False, False],
    )
    canonical = ordered.drop_duplicates(subset="filing_id", keep="first")
    return canonical.drop(columns="_mtime").reset_index(drop=True)


def load_plural_sponsorships(
    plural_dir: Path, classification: str | None = "primary"
) -> pd.DataFrame:
    """Load ``OH_136_bill_sponsorships.csv``, optionally filtered.

    Per Q2, the default filter is ``classification == "primary"``: v1 ships
    primary-only sponsorship edges to halve the cross-product. Pass
    ``classification=None`` to load all rows (for cosponsor v1.1 follow-up
    or analytical purposes); pass another string (e.g. ``"cosponsor"``) to
    load only that class.

    Per Phase 0 audit: this filter is structurally clean — the CSV's
    ``classification`` column has just two values, ``"primary"`` and
    ``"cosponsor"``, with no edge cases.
    """
    fp = plural_dir / "OH_136_bill_sponsorships.csv"
    df = pd.read_csv(fp, dtype=str).fillna("")
    if classification is not None:
        df = df[df["classification"] == classification].reset_index(drop=True)
    return df
