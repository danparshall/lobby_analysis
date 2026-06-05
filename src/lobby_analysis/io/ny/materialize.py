"""Phase 2 materialize step for the NY Open NY (Socrata) lobbying pipeline.

The end of the Phase-2 pipeline. Takes the output of::

    columns.normalize_columns
        -> parse.add_bill_id_column
        -> grain.collapse_to_filing_grain

(a column-normalized, ``bill_id``-derived, grain-collapsed frame) and writes the
``releases/ny/`` TSVs, mirroring WI's ``tier_2_materialize`` conventions.

The 2025 build draws from ``client_semiannual`` (the chain spine), so four files
are emitted (shape-compatible with ``releases/wi/``):

  * ``NY_clients.tsv``           — one row per distinct beneficial client (``Organization``)
  * ``NY_lobbyists.tsv``         — one row per distinct principal-lobbyist firm (``Organization``)
  * ``NY_filings.tsv``           — one row per distinct (submission, client) filing,
                                   carrying the de-duplicated filing-level compensation
  * ``NY_filing_bill_links.tsv`` — one row per (filing, real bill) with the even-split
                                   ``comp_per_bill = filing_compensation / n_bills_in_filing``
                                   alongside ``filing_compensation``, ``n_bills_in_filing``,
                                   and ``bill_print_version`` (the suffixed canonical id,
                                   preserved for the Phase-4 chain normalizer)

Conventions carried from WI's materializer (load-bearing for idempotency):

  * ``csv.DictWriter`` with ``delimiter="\\t"`` + ``lineterminator="\\n"`` so re-runs
    are byte-identical across platforms;
  * ``None`` -> empty cell (never the string ``"None"`` or a fabricated ``0``);
  * JSON columns serialized compactly + deterministically;
  * every table sorted on a stable key before writing.

Money discipline: compensation is read from the grain's ``filing_compensation``
via :func:`parse.coerce_money` (Decimal, with ``"$"``/``""``/None -> absent, not
0). The even-split is computed in ``Decimal`` so the per-filing conservation
invariant (``SUM(comp_per_bill) == filing_compensation``) holds exactly when the
bill count divides evenly; when it does not, the remainder is distributed across
the first bills so the sum is still exact (no rounding loss).

This step does **not** re-derive grain or re-sum compensation — those guards live
upstream in :mod:`grain`. It only projects the collapsed grain into the release
TSVs.

Plan: ``docs/active/ny-disclosure-explore/plans/ny_disclosure_pipeline.md`` (Phase 2).
"""

from __future__ import annotations

import csv
import json
from decimal import Decimal
from pathlib import Path
from typing import Sequence

import pandas as pd

from lobby_analysis.io.ny.parse import (
    STATE,
    coerce_money,
    parse_client,
    parse_principal_lobbyist,
)
from lobby_analysis.models.entities import Organization

__all__ = ["materialize_ny"]

_CLIENTS_FIELDS = (
    "id",
    "name",
    "source_state",
    "classification",
    "legal_form",
    "sector",
    "contact_details_json",
)
_LOBBYISTS_FIELDS = _CLIENTS_FIELDS
_FILINGS_FIELDS = (
    "filing_id",
    "id",
    "state",
    "filing_type",
    "filer_role",
    "reporting_year",
    "reporting_period",
    "lobbyist_id",
    "client_id",
    "total_compensation",
)
_BILL_LINKS_FIELDS = (
    "filing_id",
    "lobbyist_id",
    "client_id",
    "bill_id",
    "bill_print_version",
    "comp_per_bill",
    "filing_compensation",
    "n_bills_in_filing",
    "reporting_year",
    "reporting_period",
)


# ---------------------------------------------------------------------------
# TSV helpers (mirror io/wi/tier_2_materialize)
# ---------------------------------------------------------------------------


def _write_tsv(path: Path, fieldnames: Sequence[str], rows: list[dict]) -> int:
    """Write ``rows`` to ``path`` as a TSV with a single header row.

    ``\\n`` lineterminator gives byte-identical output across platforms.
    Returns the number of data rows written.
    """
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(
            fh, fieldnames=list(fieldnames), delimiter="\t", lineterminator="\n"
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    return len(rows)


def _cell(value) -> str:
    """``None`` -> empty cell; everything else -> ``str(value)``."""
    return "" if value is None else str(value)


def _contact_details_json(org: Organization) -> str:
    """Serialize an Organization's contact_details to a compact JSON cell."""
    return json.dumps(
        [d.model_dump() for d in org.contact_details],
        separators=(",", ":"),
        ensure_ascii=False,
    )


def _org_row(org: Organization) -> dict:
    return {
        "id": org.id,
        "name": org.name,
        "source_state": org.source_state,
        "classification": _cell(org.classification),
        "legal_form": _cell(org.legal_form),
        "sector": _cell(org.sector),
        "contact_details_json": _contact_details_json(org),
    }


def _even_split(total: Decimal, n: int) -> list[Decimal]:
    """Split ``total`` into ``n`` parts summing exactly to ``total``.

    Uses integer-cent arithmetic so the parts sum to the original with no
    rounding loss: the first ``remainder`` parts get one extra cent. For totals
    that divide evenly this is just ``total / n`` repeated ``n`` times.
    """
    if n <= 0:
        return []
    cents = int((total * 100).to_integral_value())
    base, rem = divmod(cents, n)
    parts = []
    for i in range(n):
        c = base + (1 if i < rem else 0)
        parts.append(Decimal(c) / Decimal(100))
    return parts


# ---------------------------------------------------------------------------
# materialize
# ---------------------------------------------------------------------------


def materialize_ny(grain: pd.DataFrame, *, output_dir: Path) -> dict[str, int]:
    """Write the ``releases/ny/`` TSVs from a collapsed filing-grain frame.

    ``grain`` is the output of ``collapse_to_filing_grain`` (one row per
    ``(reporting_year, reporting_period, form_submission_id, principal_lobbyist,
    beneficial_client, bill_id)``, with ``filing_compensation`` and
    ``n_bills_in_filing`` carried). Returns a dict of row counts per file.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    clients: dict[str, dict] = {}
    lobbyists: dict[str, dict] = {}
    filings: dict[str, dict] = {}
    bill_links: list[dict] = []

    for record in grain.to_dict(orient="records"):
        firm = parse_principal_lobbyist(record["principal_lobbyist"])
        client = parse_client(record["beneficial_client"])
        submission = str(record["form_submission_id"])

        clients.setdefault(client.id, _org_row(client))
        lobbyists.setdefault(firm.id, _org_row(firm))

        comp = coerce_money(record.get("filing_compensation"))
        n_bills = int(record.get("n_bills_in_filing") or 0)
        # A filing is one FIRM's report-of-work for one client in one period. The
        # key MUST include the firm: ``form_submission_id`` is the *client's*
        # report id, shared across every firm the client retains (26% of live
        # 2025 submissions list >1 firm), so keying on (submission, client) alone
        # collapses co-retained firms onto one row and drops their dollars.
        firm_suffix = firm.id.split("NY-lobbyist-", 1)[-1]
        client_suffix = client.id.split("NY-client-", 1)[-1]
        filing_uid = f"NY-filing-{submission}-{firm_suffix}-{client_suffix}"
        filings.setdefault(
            (record.get("reporting_year"), record.get("reporting_period"),
             submission, firm.id, client.id),
            {
                "filing_id": submission,
                "id": filing_uid,
                "state": STATE,
                "filing_type": "expenditure_report",
                "filer_role": "firm",
                "reporting_year": _cell(record.get("reporting_year")),
                "reporting_period": _cell(record.get("reporting_period")),
                "lobbyist_id": firm.id,
                "client_id": client.id,
                "total_compensation": _cell(comp),
            },
        )

        bill_id = record.get("bill_id")
        # pandas may carry NaN/None for non-bill focus rows; only real bills
        # become chain-eligible bill links.
        if bill_id is None or (isinstance(bill_id, float) and pd.isna(bill_id)):
            continue
        bill_links.append(
            {
                "filing_id": submission,
                "lobbyist_id": firm.id,
                "client_id": client.id,
                "bill_id": str(bill_id),
                "bill_print_version": str(bill_id),
                # comp_per_bill filled after we know each filing's split below
                "_comp": comp,
                "filing_compensation": _cell(comp),
                "n_bills_in_filing": _cell(n_bills),
                "reporting_year": _cell(record.get("reporting_year")),
                "reporting_period": _cell(record.get("reporting_period")),
            }
        )

    # Even-split per filing so SUM(comp_per_bill) == filing_compensation exactly.
    # Group by (submission, lobbyist, client) — the firm is load-bearing: a shared
    # client submission carries several firms' bills, and splitting on
    # (submission, client) alone would pool them and mis-divide each firm's comp.
    by_filing: dict[tuple, list[dict]] = {}
    for link in bill_links:
        by_filing.setdefault(
            (link["filing_id"], link["lobbyist_id"], link["client_id"]), []
        ).append(link)
    for group in by_filing.values():
        comp = group[0]["_comp"]
        if comp is None:
            for link in group:
                link["comp_per_bill"] = ""
        else:
            parts = _even_split(comp, len(group))
            for link, part in zip(group, parts):
                link["comp_per_bill"] = str(part)
    for link in bill_links:
        link.pop("_comp", None)

    client_rows = sorted(clients.values(), key=lambda r: r["id"])
    lobbyist_rows = sorted(lobbyists.values(), key=lambda r: r["id"])
    filing_rows = sorted(
        filings.values(),
        key=lambda r: (r["filing_id"], r["lobbyist_id"], r["client_id"]),
    )
    link_rows = sorted(
        bill_links,
        key=lambda r: (r["filing_id"], r["lobbyist_id"], r["client_id"], r["bill_id"]),
    )

    counts = {
        "clients": _write_tsv(
            output_dir / "NY_clients.tsv", _CLIENTS_FIELDS, client_rows
        ),
        "lobbyists": _write_tsv(
            output_dir / "NY_lobbyists.tsv", _LOBBYISTS_FIELDS, lobbyist_rows
        ),
        "filings": _write_tsv(
            output_dir / "NY_filings.tsv", _FILINGS_FIELDS, filing_rows
        ),
        "filing_bill_links": _write_tsv(
            output_dir / "NY_filing_bill_links.tsv", _BILL_LINKS_FIELDS, link_rows
        ),
    }
    return counts
