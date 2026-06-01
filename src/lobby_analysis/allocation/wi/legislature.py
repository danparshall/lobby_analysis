"""WI legislature bill metadata loader (Phase 3 step 36 — RED stub).

Reads the Plural Policy / OpenStates bulk CSV bundle for WI 2025 and exposes a
per-bill metadata dict (keyed by canonical short identifier) for the Phase 3
chain composition.

RED STUB — definitions exist so tests collect cleanly. Implementation is in
the GREEN commit that follows.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

__all__ = [
    "Sponsor",
    "BillMetadata",
    "normalize_bill_id",
    "load_bill_sponsorships",
]


@dataclass
class Sponsor:
    """One primary sponsor of a bill. See module docstring for design notes."""

    person_id: str | None
    name: str
    party: str | None
    chamber: str | None
    district: int | None
    is_collective: bool


@dataclass
class BillMetadata:
    """Per-bill metadata returned by :func:`load_bill_sponsorships`."""

    bill_id: str
    bill_uuid: str
    title: str
    chamber: str
    primary_sponsors: list[Sponsor]
    committee_name: str | None


def normalize_bill_id(raw: str) -> str:
    """Canonicalize raw bill identifiers to the OpenStates short form."""
    raise NotImplementedError("Phase 3 step 36 GREEN")


def load_bill_sponsorships(
    csv_dir: Path,
    legislators_csv: Path,
) -> dict[str, BillMetadata]:
    """Return a per-bill metadata dict keyed by canonical short bill ID."""
    raise NotImplementedError("Phase 3 step 36 GREEN")
