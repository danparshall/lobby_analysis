"""Materialize the WI Tier-2 disclosure-data layer from on-disk checkpoint
JSONs.

Walks both the principal-side checkpoint directory and the lobbyist-side
checkpoint directory, calls the two Tier-2 parsers
(``principal_meta_parser`` + ``lobbyist_time_report_parser``), and emits 5
TSVs plus a parse-failures warnings file under ``output_dir``::

    WI_principals.tsv              — one row per principal (Organization)
    WI_lobbyists.tsv               — one row per lobbyist (Person)
    WI_principal_filings.tsv       — one row per (principal, semester)
    WI_lobbyist_filings.tsv        — one row per (lobbyist, semester)
    WI_principal_bill_efforts.tsv  — one row per Percent Allocation item × period
    _tier_2_parse_failures.tsv     — ParseError rows (soft-404, etc.)

Idempotency contract (load-bearing): the parsers stamp
``datetime.now(timezone.utc)`` into ``provenance.extracted_at``. The TSV
schemas here intentionally omit that field so byte-identical re-runs are
possible. ``source_url`` (stable from URL template) IS serialized; the
extracted_at timestamp stays in-memory only.

Discovery follows the existing ``principal_materialize`` /
``authorization_materialize`` precedent: scan checkpoint dir for
``{int_id}.json`` files in sorted order, parse each, route ParseError
into the warnings TSV instead of crashing. ``html: null`` checkpoints
(404 captured at fetch time) are skipped silently — they contributed
nothing at fetch time and contribute nothing here.

Plan: ``docs/active/wi-disclosure-explore/plans/wi_tier_2_parser.md``
(Phase 4, steps 26-31). Originating convo:
``convos/20260526_wi_tier_2_phases_2_3_green.md``.
"""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Iterator, Sequence

from lobby_analysis.io.wi.lobbyist_time_report_parser import (
    ParseError as LobbyistParseError,
    parse_lobbyist_time_reports,
)
from lobby_analysis.io.wi.principal_meta_parser import (
    ParseError as PrincipalParseError,
    parse_principal_meta,
)
from lobby_analysis.models import LobbyingFiling, Organization, Person


# Sentinel used when sorting filings by reporting_period_start — None
# values sort first.
_MIN_DATE = date.min


__all__ = [
    "ParseFailure",
    "iter_principal_records",
    "iter_lobbyist_records",
    "write_principals_tsv",
    "write_lobbyists_tsv",
    "write_principal_filings_tsv",
    "write_lobbyist_filings_tsv",
    "write_principal_bill_efforts_tsv",
    "write_parse_failures_tsv",
    "materialize_tier_2",
]


PrincipalRecord = tuple[Organization, dict, list[LobbyingFiling], list[dict]]
LobbyistRecord = tuple[Person, list[LobbyingFiling]]


@dataclass(frozen=True)
class ParseFailure:
    """A parser raised ParseError on a specific entity. The materializer
    captured it as a warning row rather than letting the run crash."""

    entity_type: str  # "principal" or "lobbyist"
    entity_id: int
    reason: str


# ---------------------------------------------------------------------------
# Checkpoint iterators
# ---------------------------------------------------------------------------


def _iter_int_checkpoints(checkpoint_dir: Path) -> Iterator[Path]:
    """Yield ``{int_id}.json`` checkpoint files in ascending id order.

    Mirrors the existing ``principal_materialize`` iteration discipline:
    skip directories that don't exist, skip non-numeric filenames, sort
    by integer id for deterministic output.
    """
    checkpoint_dir = Path(checkpoint_dir)
    if not checkpoint_dir.exists():
        return
    files = sorted(
        (p for p in checkpoint_dir.glob("*.json") if p.stem.isdigit()),
        key=lambda p: int(p.stem),
    )
    for path in files:
        yield path


def iter_principal_records(
    checkpoint_dir: Path,
) -> Iterator[PrincipalRecord | ParseFailure]:
    """Yield one parsed-tuple per successful principal checkpoint, or a
    ParseFailure per page that raises ParseError.

    ``html: null`` checkpoints (404 captured at fetch time) are skipped
    silently. Non-numeric filenames are ignored.
    """
    for path in _iter_int_checkpoints(checkpoint_dir):
        with path.open("r", encoding="utf-8") as fh:
            payload = json.load(fh)
        html = payload.get("html")
        if html is None:
            continue
        principal_id = int(payload["principal_id"])
        try:
            yield parse_principal_meta(html, principal_id=principal_id)
        except PrincipalParseError as exc:
            yield ParseFailure(
                entity_type="principal",
                entity_id=principal_id,
                reason=str(exc),
            )


def iter_lobbyist_records(
    checkpoint_dir: Path,
) -> Iterator[LobbyistRecord | ParseFailure]:
    """Yield one parsed-tuple per successful lobbyist checkpoint, or a
    ParseFailure per page that raises ParseError (e.g., soft-404 stub
    pages like Neumann-Ortiz 12717)."""
    for path in _iter_int_checkpoints(checkpoint_dir):
        with path.open("r", encoding="utf-8") as fh:
            payload = json.load(fh)
        html = payload.get("html")
        if html is None:
            continue
        lobbyist_id = int(payload["lobbyist_id"])
        try:
            yield parse_lobbyist_time_reports(html, lobbyist_id=lobbyist_id)
        except LobbyistParseError as exc:
            yield ParseFailure(
                entity_type="lobbyist",
                entity_id=lobbyist_id,
                reason=str(exc),
            )


# ---------------------------------------------------------------------------
# TSV helpers
# ---------------------------------------------------------------------------


def _open_writer(path: Path, fieldnames: Sequence[str]) -> tuple:
    """Open a TSV file and return (file_handle, DictWriter). Uses ``\\n``
    lineterminator so re-runs produce byte-identical output on every
    platform."""
    fh = path.open("w", encoding="utf-8", newline="")
    writer = csv.DictWriter(
        fh, fieldnames=list(fieldnames), delimiter="\t", lineterminator="\n"
    )
    writer.writeheader()
    return fh, writer


def _maybe_str(value) -> str:
    """``None`` → empty cell; everything else → ``str(value)``. Booleans
    become ``True``/``False`` strings (no callers pass booleans here)."""
    if value is None:
        return ""
    return str(value)


def _contact_details_to_json(details) -> str:
    """Serialize a list[ContactDetail] (or list[dict]) into a deterministic
    JSON string for a TSV cell. ``sort_keys=False`` because the list order
    carries meaning (preferred contact method first); within each dict the
    keys come from the model and are stable."""
    items = []
    for d in details:
        if hasattr(d, "model_dump"):
            items.append(d.model_dump())
        else:
            items.append(dict(d))
    return json.dumps(items, separators=(",", ":"), ensure_ascii=False)


# ---------------------------------------------------------------------------
# write_principals_tsv
# ---------------------------------------------------------------------------


_PRINCIPALS_FIELDS = [
    "principal_id",
    "id",
    "name",
    "source_state",
    "classification",
    "legal_form",
    "sector",
    "contact_details_json",
    "ceo_name",
    "business_or_interest",
    "lobbying_interests_prose",
]


def write_principals_tsv(
    rows: Sequence[tuple[Organization, dict]], path: Path
) -> int:
    """Write the principals TSV. Sorted by ``principal_id`` (the suffix of
    ``Organization.id``)."""
    fh, writer = _open_writer(path, _PRINCIPALS_FIELDS)
    try:
        ordered = sorted(rows, key=lambda r: _id_suffix(r[0].id))
        for org, extras in ordered:
            writer.writerow(
                {
                    "principal_id": _id_suffix(org.id),
                    "id": org.id,
                    "name": org.name,
                    "source_state": org.source_state,
                    "classification": _maybe_str(org.classification),
                    "legal_form": _maybe_str(org.legal_form),
                    "sector": _maybe_str(org.sector),
                    "contact_details_json": _contact_details_to_json(
                        org.contact_details
                    ),
                    "ceo_name": _maybe_str(extras.get("ceo_name")),
                    "business_or_interest": _maybe_str(
                        extras.get("business_or_interest")
                    ),
                    "lobbying_interests_prose": _maybe_str(
                        extras.get("lobbying_interests_prose")
                    ),
                }
            )
        return len(ordered)
    finally:
        fh.close()


# ---------------------------------------------------------------------------
# write_lobbyists_tsv
# ---------------------------------------------------------------------------


_LOBBYISTS_FIELDS = [
    "lobbyist_id",
    "id",
    "name",
    "source_state",
    "contact_details_json",
]


def write_lobbyists_tsv(rows: Sequence[Person], path: Path) -> int:
    """Write the lobbyists TSV. Sorted by ``lobbyist_id`` (the suffix of
    ``Person.id``)."""
    fh, writer = _open_writer(path, _LOBBYISTS_FIELDS)
    try:
        ordered = sorted(rows, key=lambda p: _id_suffix(p.id))
        for person in ordered:
            writer.writerow(
                {
                    "lobbyist_id": _id_suffix(person.id),
                    "id": person.id,
                    "name": person.name,
                    "source_state": person.source_state,
                    "contact_details_json": _contact_details_to_json(
                        person.contact_details
                    ),
                }
            )
        return len(ordered)
    finally:
        fh.close()


# ---------------------------------------------------------------------------
# write_principal_filings_tsv
# ---------------------------------------------------------------------------


_PRINCIPAL_FILINGS_FIELDS = [
    "filing_id",
    "principal_id",
    "state",
    "filing_type",
    "filer_role",
    "reporting_period_start",
    "reporting_period_end",
    "total_expenditure",
    "total_hours_communicating",
    "total_hours_other",
    "source_url",
]


def write_principal_filings_tsv(
    rows: Sequence[LobbyingFiling], path: Path
) -> int:
    """Write the principal-filings TSV. Sorted by ``(principal_id,
    reporting_period_start)``. ``extracted_at`` is intentionally omitted
    so byte-identical re-runs are possible."""
    fh, writer = _open_writer(path, _PRINCIPAL_FILINGS_FIELDS)
    try:
        ordered = sorted(
            rows,
            key=lambda f: (
                _principal_id_from_filing(f),
                f.reporting_period_start or _MIN_DATE,
            ),
        )
        for filing in ordered:
            writer.writerow(
                {
                    "filing_id": filing.id,
                    "principal_id": _principal_id_from_filing(filing),
                    "state": filing.state,
                    "filing_type": filing.filing_type,
                    "filer_role": filing.filer_role,
                    "reporting_period_start": _maybe_str(
                        filing.reporting_period_start
                    ),
                    "reporting_period_end": _maybe_str(filing.reporting_period_end),
                    "total_expenditure": _maybe_str(filing.total_expenditure),
                    "total_hours_communicating": _maybe_str(
                        filing.total_hours_communicating
                    ),
                    "total_hours_other": _maybe_str(filing.total_hours_other),
                    "source_url": _maybe_str(
                        filing.provenance.source_url if filing.provenance else None
                    ),
                }
            )
        return len(ordered)
    finally:
        fh.close()


# ---------------------------------------------------------------------------
# write_lobbyist_filings_tsv
# ---------------------------------------------------------------------------


_LOBBYIST_FILINGS_FIELDS = [
    "filing_id",
    "lobbyist_id",
    "state",
    "filing_type",
    "filer_role",
    "reporting_period_start",
    "reporting_period_end",
    "total_hours_communicating",
    "total_hours_other",
    "source_url",
]


def write_lobbyist_filings_tsv(
    rows: Sequence[LobbyingFiling], path: Path
) -> int:
    """Write the lobbyist-filings TSV. Sorted by ``(lobbyist_id,
    reporting_period_start)``."""
    fh, writer = _open_writer(path, _LOBBYIST_FILINGS_FIELDS)
    try:
        ordered = sorted(
            rows,
            key=lambda f: (
                _lobbyist_id_from_filing(f),
                f.reporting_period_start or _MIN_DATE,
            ),
        )
        for filing in ordered:
            writer.writerow(
                {
                    "filing_id": filing.id,
                    "lobbyist_id": _lobbyist_id_from_filing(filing),
                    "state": filing.state,
                    "filing_type": filing.filing_type,
                    "filer_role": filing.filer_role,
                    "reporting_period_start": _maybe_str(
                        filing.reporting_period_start
                    ),
                    "reporting_period_end": _maybe_str(filing.reporting_period_end),
                    "total_hours_communicating": _maybe_str(
                        filing.total_hours_communicating
                    ),
                    "total_hours_other": _maybe_str(filing.total_hours_other),
                    "source_url": _maybe_str(
                        filing.provenance.source_url if filing.provenance else None
                    ),
                }
            )
        return len(ordered)
    finally:
        fh.close()


# ---------------------------------------------------------------------------
# write_principal_bill_efforts_tsv
# ---------------------------------------------------------------------------


_BILL_EFFORTS_FIELDS = [
    "principal_id",
    "bucket",
    "item_id",
    "item_name",
    "item_description",
    "period_label",
    "percent",
]


def write_principal_bill_efforts_tsv(
    rows: Sequence[dict], path: Path
) -> int:
    """Write the per-(principal, bucket, item, period) percent allocation
    TSV. Sorted by ``(principal_id, bucket, item_id, period_label)``."""
    fh, writer = _open_writer(path, _BILL_EFFORTS_FIELDS)
    try:
        ordered = sorted(
            rows,
            key=lambda r: (
                int(r["principal_id"]),
                r.get("bucket", ""),
                r.get("item_id", ""),
                r.get("period_label", ""),
            ),
        )
        for row in ordered:
            writer.writerow(
                {
                    "principal_id": row["principal_id"],
                    "bucket": row.get("bucket", ""),
                    "item_id": row.get("item_id", ""),
                    "item_name": row.get("item_name", ""),
                    "item_description": _maybe_str(row.get("item_description")),
                    "period_label": row.get("period_label", ""),
                    "percent": row.get("percent", ""),
                }
            )
        return len(ordered)
    finally:
        fh.close()


# ---------------------------------------------------------------------------
# write_parse_failures_tsv
# ---------------------------------------------------------------------------


_PARSE_FAILURES_FIELDS = ["entity_type", "entity_id", "reason"]


def write_parse_failures_tsv(
    failures: Sequence[ParseFailure], path: Path
) -> int:
    """Write the warnings TSV. Always writes the header row even when
    there are zero failures so a downstream consumer can confirm the
    materializer ran. Sorted by ``(entity_type, entity_id)``."""
    fh, writer = _open_writer(path, _PARSE_FAILURES_FIELDS)
    try:
        ordered = sorted(failures, key=lambda f: (f.entity_type, f.entity_id))
        for f in ordered:
            writer.writerow(
                {
                    "entity_type": f.entity_type,
                    "entity_id": f.entity_id,
                    "reason": f.reason,
                }
            )
        return len(ordered)
    finally:
        fh.close()


# ---------------------------------------------------------------------------
# materialize_tier_2 — end-to-end orchestrator
# ---------------------------------------------------------------------------


def materialize_tier_2(
    principal_checkpoints_dir: Path,
    lobbyist_checkpoints_dir: Path,
    output_dir: Path,
) -> dict[str, int]:
    """Walk both checkpoint dirs, run the parsers, write 5 TSVs + the
    parse-failures TSV under ``output_dir``. Returns a dict mapping each
    output filename to its row count (excluding the header).
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    principal_orgs: list[tuple[Organization, dict]] = []
    principal_filings: list[LobbyingFiling] = []
    bill_efforts: list[dict] = []
    lobbyist_persons: list[Person] = []
    lobbyist_filings: list[LobbyingFiling] = []
    failures: list[ParseFailure] = []

    for record in iter_principal_records(Path(principal_checkpoints_dir)):
        if isinstance(record, ParseFailure):
            failures.append(record)
            continue
        org, extras, filings, items = record
        principal_orgs.append((org, extras))
        principal_filings.extend(filings)
        bill_efforts.extend(items)

    for record in iter_lobbyist_records(Path(lobbyist_checkpoints_dir)):
        if isinstance(record, ParseFailure):
            failures.append(record)
            continue
        person, filings = record
        lobbyist_persons.append(person)
        lobbyist_filings.extend(filings)

    n_principals = write_principals_tsv(
        principal_orgs, output_dir / "WI_principals.tsv"
    )
    n_lobbyists = write_lobbyists_tsv(
        lobbyist_persons, output_dir / "WI_lobbyists.tsv"
    )
    n_principal_filings = write_principal_filings_tsv(
        principal_filings, output_dir / "WI_principal_filings.tsv"
    )
    n_lobbyist_filings = write_lobbyist_filings_tsv(
        lobbyist_filings, output_dir / "WI_lobbyist_filings.tsv"
    )
    n_bill_efforts = write_principal_bill_efforts_tsv(
        bill_efforts, output_dir / "WI_principal_bill_efforts.tsv"
    )
    n_failures = write_parse_failures_tsv(
        failures, output_dir / "_tier_2_parse_failures.tsv"
    )

    return {
        "WI_principals.tsv": n_principals,
        "WI_lobbyists.tsv": n_lobbyists,
        "WI_principal_filings.tsv": n_principal_filings,
        "WI_lobbyist_filings.tsv": n_lobbyist_filings,
        "WI_principal_bill_efforts.tsv": n_bill_efforts,
        "_tier_2_parse_failures.tsv": n_failures,
    }


# ---------------------------------------------------------------------------
# Helpers — ID suffix extraction
# ---------------------------------------------------------------------------


def _id_suffix(model_id: str) -> int:
    """Extract the integer suffix from a ``WI-{role}-{int_id}`` model id.

    Used for sorting Organization / Person rows by their underlying
    integer state-portal id (not by the full string id, which would sort
    ``WI-principal-10000`` before ``WI-principal-9999``).
    """
    parts = model_id.rsplit("-", 1)
    return int(parts[-1])


def _principal_id_from_filing(filing: LobbyingFiling) -> int:
    org = filing.filer_organization
    if org is None:
        raise ValueError(
            f"Principal filing {filing.id} has no filer_organization — cannot "
            "extract principal_id for the materialized TSV."
        )
    return _id_suffix(org.id)


def _lobbyist_id_from_filing(filing: LobbyingFiling) -> int:
    person = filing.filer_person
    if person is None:
        raise ValueError(
            f"Lobbyist filing {filing.id} has no filer_person — cannot extract "
            "lobbyist_id for the materialized TSV."
        )
    return _id_suffix(person.id)
