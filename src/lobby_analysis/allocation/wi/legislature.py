"""WI legislature bill metadata loader (Phase 3 step 36).

Reads the Plural Policy / OpenStates bulk CSV bundle for WI 2025 plus the
legislators roster and exposes a per-bill metadata dict (keyed by canonical
short identifier) for the Phase 3 chain composition.

Data sources (all gitignored, symlinked through ``data/``):

- ``data/bills/WI/2025/WI_2025_bills.csv`` — one row per bill
- ``data/bills/WI/2025/WI_2025_bill_sponsorships.csv`` — one row per bill-sponsor edge
- ``data/bills/WI/2025/WI_2025_bill_actions.csv`` — action history
- ``data/bills/wi.csv`` — current WI legislator roster with ocd-person/... IDs

Design decisions:

- Sponsor scope is primary-only. The sponsorships table has
  ``classification='primary'`` for ALL 28,047 rows; cosponsors live only in
  ``bill_actions.description`` text and are deferred to Phase 3+ refinement.
- 60 sponsorships have ``entity_type='organization'`` (Joint Legislative
  Council, Law Revision Committee) without a ``person_id``. These surface as
  :class:`Sponsor` with ``is_collective=True`` and ``person_id=None`` — not
  silently dropped.
- Committee name comes from regex over the first ``referral-committee``
  action's ``description`` field. The action's ``organization_id`` only
  identifies the chamber, not the receiving committee.
- The canonical bill key is the OpenStates short identifier ("SB 3", "AB 156")
  — the same string the bulk CSV exposes in the ``identifier`` column. The
  :func:`normalize_bill_id` function maps verbose WI-release forms
  ("Senate Bill 3") onto this canonical form.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

__all__ = [
    "Sponsor",
    "BillMetadata",
    "normalize_bill_id",
    "load_bill_sponsorships",
]


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass
class Sponsor:
    """One primary sponsor of a bill.

    For individual legislators, ``person_id`` is the OpenStates ``ocd-person/...``
    UUID, joined to ``wi.csv`` for ``party`` / ``chamber`` / ``district``.

    For collective entities (Joint Legislative Council, Law Revision Committee),
    ``person_id`` is ``None`` and ``is_collective=True``; ``party``, ``chamber``,
    ``district`` are also ``None``.
    """

    person_id: str | None
    name: str
    party: str | None
    chamber: str | None
    district: int | None
    is_collective: bool


@dataclass
class BillMetadata:
    """Per-bill metadata returned by :func:`load_bill_sponsorships`."""

    bill_id: str  # canonical short, e.g. "SB 3"
    bill_uuid: str  # OpenStates internal, e.g. "ocd-bill/49a..."
    title: str
    chamber: str  # "upper" / "lower"
    primary_sponsors: list[Sponsor]
    committee_name: str | None


# ---------------------------------------------------------------------------
# normalize_bill_id
# ---------------------------------------------------------------------------


_LONG_TO_SHORT: dict[str, str] = {
    "Senate Joint Resolution": "SJR",
    "Assembly Joint Resolution": "AJR",
    "Senate Resolution": "SR",
    "Assembly Resolution": "AR",
    "Senate Bill": "SB",
    "Assembly Bill": "AB",
}

_YEAR_PREFIX = re.compile(r"^\d{4}\s+")


def normalize_bill_id(raw: str) -> str:
    """Canonicalize a raw bill identifier to its OpenStates short form.

    Handles:
    - Verbose WI-release form: "Senate Bill 3" → "SB 3"
    - Already-canonical short form: "SB 3" → "SB 3"
    - Session-prefixed form: "2025 SB 3" → "SB 3", "2025 Senate Bill 3" → "SB 3"
    - Joint/standalone resolutions: "Senate Joint Resolution 1" → "SJR 1"
    """
    s = raw.strip()
    s = _YEAR_PREFIX.sub("", s)
    # Order matters: "Senate Joint Resolution" must be checked before "Senate ..."
    for long, short in _LONG_TO_SHORT.items():
        if s.startswith(long + " "):
            return short + " " + s[len(long) + 1 :]
    return s


# ---------------------------------------------------------------------------
# Committee referral parsing
# ---------------------------------------------------------------------------


_REFERRAL_RE = re.compile(r"referred to (.+?)\s*$", re.DOTALL)


def _extract_committee_name(description: str) -> str | None:
    """Pull the committee name out of a referral-committee action description.

    Example: "Read first time and referred to Committee on Utilities and Tourism"
    → "Committee on Utilities and Tourism".
    """
    m = _REFERRAL_RE.search(description.strip())
    if not m:
        return None
    name = m.group(1).strip().rstrip(".")
    return name or None


def _has_referral_classification(classification_str: str) -> bool:
    """The actions CSV stores classification as a stringified Python list,
    e.g. "['reading-1', 'referral-committee']". Substring-match is enough."""
    return "'referral-committee'" in classification_str


# ---------------------------------------------------------------------------
# load_bill_sponsorships
# ---------------------------------------------------------------------------


def load_bill_sponsorships(
    csv_dir: Path,
    legislators_csv: Path,
) -> dict[str, BillMetadata]:
    """Load WI bill metadata + primary sponsors + committee assignment.

    Returns a dict keyed by the canonical short bill identifier (e.g. ``"SB 3"``).
    """
    bills_df = pd.read_csv(csv_dir / "WI_2025_bills.csv")
    sp_df = pd.read_csv(csv_dir / "WI_2025_bill_sponsorships.csv")
    acts_df = pd.read_csv(csv_dir / "WI_2025_bill_actions.csv")
    leg_df = pd.read_csv(legislators_csv)

    # person_id -> (party, chamber, district)
    leg_lookup: dict[str, dict[str, object]] = {}
    for row in leg_df.itertuples(index=False):
        district_raw = row.current_district
        try:
            district_val: int | None = (
                int(district_raw) if pd.notna(district_raw) else None
            )
        except (ValueError, TypeError):
            district_val = None
        leg_lookup[row.id] = {
            "party": row.current_party if pd.notna(row.current_party) else None,
            "chamber": row.current_chamber if pd.notna(row.current_chamber) else None,
            "district": district_val,
        }

    # bill_uuid -> list[Sponsor]
    sponsors_by_bill: dict[str, list[Sponsor]] = {}
    for row in sp_df.itertuples(index=False):
        bill_uuid = row.bill_id
        pid = row.person_id if pd.notna(row.person_id) else None
        if pid is None:
            sponsor = Sponsor(
                person_id=None,
                name=row.name,
                party=None,
                chamber=None,
                district=None,
                is_collective=True,
            )
        else:
            info = leg_lookup.get(pid, {})
            sponsor = Sponsor(
                person_id=pid,
                name=row.name,
                party=info.get("party"),
                chamber=info.get("chamber"),
                district=info.get("district"),
                is_collective=False,
            )
        sponsors_by_bill.setdefault(bill_uuid, []).append(sponsor)

    # bill_uuid -> committee_name (first referral-committee action by order)
    committee_lookup: dict[str, str] = {}
    referral_acts = acts_df[
        acts_df["classification"].apply(_has_referral_classification)
    ].sort_values("order")
    for row in referral_acts.itertuples(index=False):
        if row.bill_id in committee_lookup:
            continue  # keep the first (earliest) referral
        name = _extract_committee_name(str(row.description))
        if name:
            committee_lookup[row.bill_id] = name

    # Assemble
    result: dict[str, BillMetadata] = {}
    for row in bills_df.itertuples(index=False):
        canonical = normalize_bill_id(row.identifier)
        result[canonical] = BillMetadata(
            bill_id=canonical,
            bill_uuid=row.id,
            title=row.title,
            chamber=row.organization_classification,
            primary_sponsors=sponsors_by_bill.get(row.id, []),
            committee_name=committee_lookup.get(row.id),
        )

    return result
