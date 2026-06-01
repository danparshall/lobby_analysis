"""WI end-to-end chain composer (Phase 3 step 38).

Stitches Phase 2's allocation matrix together with bill-effort filings and the
legislature bill metadata into one row per
(semester, principal, lobbyist, bill, sponsor) tuple — the chain Suhan asked
for: company → lobbyist → bill → lawmaker.

Inputs:

- ``allocation_dir`` — directory containing
  ``WI_lobbyist_principal_hours_h{1,2}_2025.tsv`` (Phase 2 output).
- ``release_dir`` — directory containing ``WI_principals.tsv``,
  ``WI_lobbyists.tsv``, and ``WI_principal_bill_efforts.tsv`` (Phase 0 release).
- ``bill_metadata`` — dict produced by
  :func:`lobby_analysis.allocation.wi.legislature.load_bill_sponsorships`.

Phase 3 v1 scope:

- Bucket filter: only ``Legislative Bills/Resolutions`` rows from bill_efforts
  produce chain rows. The other three buckets (Topics Not Yet Assigned, Budget
  Bill Subjects, Administrative Rulemaking) are deferred to Phase 3+ refinement.
- Unmatched bills (no entry in ``bill_metadata`` or zero structured primary
  sponsors) are silently skipped — they're diagnostic, not chain-emit-worthy.
- Granularity: one row per (semester, principal, lobbyist, bill, sponsor).
- ``modeled_hours = (hours_comm + hours_other) × (filed_percent / 100)``.
- ``attribution_confidence`` is the allocation matrix's confidence value,
  passed through unchanged.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from lobby_analysis.allocation.wi.legislature import BillMetadata, normalize_bill_id

__all__ = ["compose_chain"]


_PERIOD_TO_SEMESTER: dict[str, str] = {
    "2025 January - June": "2025-H1",
    "2025 July - December": "2025-H2",
    "2026 January - June": "2026-H1",
    "2026 July - December": "2026-H2",
}


def _parse_percent(raw: object) -> float | None:
    """Parse a 'percent' field from bill_efforts into a [0, 1] float.

    Accepts either '21%' (string) or 21.0 (numeric). Returns None if input is NaN.
    """
    if raw is None or (isinstance(raw, float) and pd.isna(raw)):
        return None
    if isinstance(raw, str):
        s = raw.strip().rstrip("%").strip()
        if not s:
            return None
        return float(s) / 100.0
    return float(raw) / 100.0


def compose_chain(
    allocation_dir: Path,
    release_dir: Path,
    bill_metadata: dict[str, BillMetadata],
) -> pd.DataFrame:
    """Compose the principal → lobbyist → bill → sponsor chain table."""
    principals = pd.read_csv(release_dir / "WI_principals.tsv", sep="\t")[
        ["principal_id", "name"]
    ].rename(columns={"name": "principal_name"})
    lobbyists = pd.read_csv(release_dir / "WI_lobbyists.tsv", sep="\t")[
        ["lobbyist_id", "name"]
    ].rename(columns={"name": "lobbyist_name"})
    efforts = pd.read_csv(release_dir / "WI_principal_bill_efforts.tsv", sep="\t")

    alloc_h1 = pd.read_csv(
        allocation_dir / "WI_lobbyist_principal_hours_h1_2025.tsv", sep="\t"
    )
    alloc_h2 = pd.read_csv(
        allocation_dir / "WI_lobbyist_principal_hours_h2_2025.tsv", sep="\t"
    )
    alloc_by_semester: dict[str, pd.DataFrame] = {
        "2025-H1": alloc_h1,
        "2025-H2": alloc_h2,
    }

    # Legislative bucket only; map period to semester; drop other periods
    legislative = efforts[efforts["bucket"] == "Legislative Bills/Resolutions"].copy()
    legislative["semester"] = legislative["period_label"].map(_PERIOD_TO_SEMESTER)
    legislative = legislative.dropna(subset=["semester"])

    rows: list[dict[str, object]] = []
    for eff in legislative.itertuples(index=False):
        semester: str = eff.semester
        if semester not in alloc_by_semester:
            continue

        canonical = normalize_bill_id(eff.item_name)
        bm = bill_metadata.get(canonical)
        if bm is None or not bm.primary_sponsors:
            continue

        pct = _parse_percent(eff.percent)
        if pct is None:
            continue

        alloc_for_principal = alloc_by_semester[semester][
            alloc_by_semester[semester]["principal_id"] == eff.principal_id
        ]
        if len(alloc_for_principal) == 0:
            continue

        for alloc_row in alloc_for_principal.itertuples(index=False):
            total_hours = float(alloc_row.hours_comm) + float(alloc_row.hours_other)
            modeled = total_hours * pct
            for sp in bm.primary_sponsors:
                sponsor_lawmaker_id = sp.person_id if sp.person_id else sp.name
                rows.append(
                    {
                        "semester": semester,
                        "principal_id": eff.principal_id,
                        "lobbyist_id": alloc_row.lobbyist_id,
                        "bill_id": canonical,
                        "bill_title": bm.title,
                        "modeled_hours": modeled,
                        "principal_filed_percent": pct,
                        "sponsor_lawmaker_id": sponsor_lawmaker_id,
                        "sponsor_lawmaker_name": sp.name,
                        "attribution_confidence": alloc_row.confidence,
                    }
                )

    chain = pd.DataFrame(rows)
    chain = chain.merge(principals, on="principal_id", how="left")
    chain = chain.merge(lobbyists, on="lobbyist_id", how="left")

    # Column order: keep schema readable + match plan literal order
    column_order = [
        "semester",
        "principal_id",
        "principal_name",
        "lobbyist_id",
        "lobbyist_name",
        "bill_id",
        "bill_title",
        "modeled_hours",
        "principal_filed_percent",
        "sponsor_lawmaker_id",
        "sponsor_lawmaker_name",
        "attribution_confidence",
    ]
    return chain[column_order]
