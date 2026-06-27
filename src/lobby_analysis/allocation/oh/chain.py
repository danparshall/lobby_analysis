"""Phase 2 — bill-side chain composer for OH.

Composes the ``releases/oh/chain/`` artifact from OH AER extractions joined
to the Plural Policy 136th GA bill bundle.

Plan reference: ``docs/active/oh-portal-extraction/plans/20260611_oh_chain_composer_design.md`` §4 (schema), §4a
(position-shape normalization), §5 Phase 2 (this module), §6 (OAC routing).

Composition shape:

- For each canonical extraction (deduped via
  :func:`load.select_canonical_extraction`) and each ``LobbyingPosition``:

  - Classify the position shape (Step A) and label class (Step B).
  - If ``bill_class == "bill"`` AND the label joins to Plural's
    ``OH_136_bills.csv``: cross-product with primary sponsorships,
    emitting one row per (filing, position, sponsor). For the rare case
    of a bill with no primary sponsorships (defensive), emit one row
    with null sponsor fields rather than zero rows (silent drop).
  - If the label looks like a bill but doesn't join to Plural: emit one
    row with ``bill_class="unmatched"``, ``bill_id=null``,
    ``confidence="unmatched"``.
  - For non-bill classes (jcarr / oac_rule / subject / subject from
    hoisted description): emit ONE row with null sponsor fields per §4a
    conservation implication. JCARR + OAC → ``confidence="oac_dropped"``;
    subject → ``confidence="subject_only"``.
  - If the position is structurally empty (Step A raises): catch
    ValueError and emit a sentinel row with
    ``confidence="null_extraction"``. One defective position must not
    kill the whole composer run.

Per Q2, sponsorships are filtered to ``classification == "primary"`` at
load time. The v1.1 cosponsor extension is a classification-filter flip
plus a chain README revision.

Per Phase 0 audit + Phase 1 smoke test, conservation invariant:

    len(output_df) == sum over canonical filings of:
        sum over positions of:
            max(1, num_primary_sponsors) if bill else 1

Every position routes to ≥1 chain row. No position is silently dropped.
"""

from __future__ import annotations

import re
import unicodedata
from pathlib import Path

import pandas as pd

from lobby_analysis.allocation.oh.classify import (
    BILL_CLASS_BILL,
    BILL_CLASS_JCARR,
    BILL_CLASS_OAC_RULE,
    BILL_CLASS_SUBJECT,
    BILL_CLASS_UNMATCHED,
    POSITION_KIND_BILL_REFERENCED,
    POSITION_KIND_SUBJECT_GENERAL,
    POSITION_KIND_SUBJECT_HOISTED,
    classify_bill_label,
    classify_position_shape,
    extract_position_label,
)
from lobby_analysis.allocation.oh.load import (
    load_filings,
    load_plural_bills,
    load_plural_sponsorships,
    select_canonical_extraction,
)
from lobby_analysis.models.filings import LobbyingFiling, LobbyingPosition

__all__ = [
    "CHAIN_COLUMNS",
    "compose_bill_chain",
    "derive_org_id",
    "derive_person_id",
]


# ---------------------------------------------------------------------------
# Deterministic entity-ID derivation (composer-side normalization)
# ---------------------------------------------------------------------------
#
# Plan: docs/active/leave-behind-prep/plans/20260615_composer_side_mini_swap_normalizations.md
# §"Step 1 — Entity-ID derivation from name"
#
# The 2026-06-15 chain-level mini-swap experiment measured 97-98% per-row
# disagreement on principal_id/lobbyist_id between sonnet- and mini-sourced
# chains — driven entirely by inconsistent model formatting of the
# Organization.id/Person.id schema fields, with identical names underneath.
# Composer-time derivation from name collapses that noise to zero.


def _slugify(s: str) -> str:
    """Reduce a free-text name to a stable kebab-case ASCII slug.

    NFKD-normalize, drop non-ASCII (so accented characters fold to their
    base letters), lowercase, replace any run of non-alphanumerics with a
    single hyphen, strip leading/trailing hyphens. Empty input → empty
    string; the public ``derive_*`` helpers turn that into ``None``.
    """
    nfkd = unicodedata.normalize("NFKD", s)
    ascii_only = nfkd.encode("ascii", "ignore").decode("ascii")
    lower = ascii_only.lower()
    hyphenated = re.sub(r"[^a-z0-9]+", "-", lower)
    return hyphenated.strip("-")


def derive_org_id(name: str | None) -> str | None:
    """Derive a deterministic chain-time organization ID from a name.

    Returns ``None`` for None / empty / whitespace-only input (we don't
    attach an ``"org-"`` prefix to nothing). Otherwise returns
    ``f"org-{slug}"``.
    """
    if name is None or not name.strip():
        return None
    slug = _slugify(name)
    if not slug:
        return None
    return f"org-{slug}"


def derive_person_id(name: str | None) -> str | None:
    """Derive a deterministic chain-time person ID from a name.

    Returns ``None`` for None / empty / whitespace-only input. Otherwise
    returns ``f"person-{slug}"``.
    """
    if name is None or not name.strip():
        return None
    slug = _slugify(name)
    if not slug:
        return None
    return f"person-{slug}"


# ---------------------------------------------------------------------------
# Schema — plan §4 schema sketch
# ---------------------------------------------------------------------------

CHAIN_COLUMNS: tuple[str, ...] = (
    "report_period",
    "filing_id",
    "principal_name",
    "principal_id",
    "lobbyist_name",
    "lobbyist_id",
    "position_kind",
    "bill_label_raw",
    "bill_label_normalized",
    "bill_class",
    "bill_id",
    "bill_title",
    "position_description",
    "num_primary_sponsors",
    "sponsor_lawmaker_id",
    "sponsor_lawmaker_name",
    "sponsor_role",
    "confidence",
)


# Confidence tokens (plan §4 schema sketch row)
_CONFIDENCE_DIRECT = "direct"
_CONFIDENCE_OAC_DROPPED = "oac_dropped"
_CONFIDENCE_UNMATCHED = "unmatched"
_CONFIDENCE_NULL_EXTRACTION = "null_extraction"
_CONFIDENCE_SUBJECT_ONLY = "subject_only"


_NON_BILL_CONFIDENCE: dict[str, str] = {
    BILL_CLASS_JCARR: _CONFIDENCE_OAC_DROPPED,
    BILL_CLASS_OAC_RULE: _CONFIDENCE_OAC_DROPPED,
    BILL_CLASS_SUBJECT: _CONFIDENCE_SUBJECT_ONLY,
    BILL_CLASS_UNMATCHED: _CONFIDENCE_UNMATCHED,
}


def _normalize_identifier(s: str) -> str:
    """Mirror of :func:`load._normalize_identifier`. Kept private here to
    avoid a brittle cross-module import; tested via load's tests + the
    chain composer's join correctness."""
    if not s:
        return ""
    s = re.sub(r"\s+", " ", s.strip().upper())
    s = s.replace(".", "")
    return re.sub(r"\s+", " ", s).strip()


# ---------------------------------------------------------------------------
# Row factories
# ---------------------------------------------------------------------------


def _filing_base(filing: LobbyingFiling) -> dict[str, object]:
    """Filing-level scalars common to every chain row from a given filing."""
    period_start = filing.reporting_period_start
    period_end = filing.reporting_period_end
    if period_start is not None and period_end is not None:
        report_period = f"{period_start}..{period_end}"
    elif period_start is not None:
        report_period = str(period_start)
    elif period_end is not None:
        report_period = str(period_end)
    else:
        report_period = ""

    principal_name = filing.employer.name if filing.employer is not None else None
    # Derive principal_id from the *name* rather than the model-emitted
    # employer.id. See plan §"Step 1" for the 97-98% inter-model
    # disagreement that this collapses.
    principal_id = derive_org_id(principal_name)
    lobbyist_name = filing.filer_person.name if filing.filer_person is not None else None
    lobbyist_id = derive_person_id(lobbyist_name)

    return {
        "report_period": report_period,
        "filing_id": filing.filing_id,
        "principal_name": principal_name,
        "principal_id": principal_id,
        "lobbyist_name": lobbyist_name,
        "lobbyist_id": lobbyist_id,
    }


def _row(
    base: dict[str, object],
    *,
    position_kind: str | None,
    bill_label_raw: str | None,
    bill_label_normalized: str | None,
    bill_class: str | None,
    bill_id: str | None,
    bill_title: str | None,
    position_description: str | None,
    num_primary_sponsors: int,
    sponsor_lawmaker_id: str | None,
    sponsor_lawmaker_name: str | None,
    sponsor_role: str | None,
    confidence: str,
) -> dict[str, object]:
    """Assemble one chain row dict with full schema."""
    return {
        **base,
        "position_kind": position_kind,
        "bill_label_raw": bill_label_raw,
        "bill_label_normalized": bill_label_normalized,
        "bill_class": bill_class,
        "bill_id": bill_id,
        "bill_title": bill_title,
        "position_description": position_description,
        "num_primary_sponsors": num_primary_sponsors,
        "sponsor_lawmaker_id": sponsor_lawmaker_id,
        "sponsor_lawmaker_name": sponsor_lawmaker_name,
        "sponsor_role": sponsor_role,
        "confidence": confidence,
    }


def _position_description_for(position: LobbyingPosition, kind: str) -> str | None:
    """The ``position_description`` column carries the position's ``description``
    field — except for the subject_hoisted_from_description case, where the
    description was hoisted into ``bill_label_raw`` and emitting it again
    in this column would just duplicate that text."""
    if kind == POSITION_KIND_SUBJECT_HOISTED:
        return None
    return position.description


# ---------------------------------------------------------------------------
# Per-position emission
# ---------------------------------------------------------------------------


def _emit_position_rows(
    base: dict[str, object],
    position: LobbyingPosition,
    bills_by_norm: dict[str, dict[str, str]],
    spons_by_bill_id: dict[str, list[dict[str, str]]],
) -> list[dict[str, object]]:
    """Return one or more chain rows for a single position."""
    try:
        kind = classify_position_shape(position)
        raw_label = extract_position_label(position)
    except ValueError:
        # Empty position — emit a sentinel so the run continues.
        return [
            _row(
                base,
                position_kind=None,
                bill_label_raw=None,
                bill_label_normalized=None,
                bill_class=None,
                bill_id=None,
                bill_title=None,
                position_description=None,
                num_primary_sponsors=0,
                sponsor_lawmaker_id=None,
                sponsor_lawmaker_name=None,
                sponsor_role=None,
                confidence=_CONFIDENCE_NULL_EXTRACTION,
            )
        ]

    bill_class = classify_bill_label(raw_label, kind)

    # Composer-side rescue (plan §"Step 2"): mini routes regulatory /
    # policy subjects into the bill_reference slot, where they correctly
    # classify as unmatched (no HB/SB/JC/OAC pattern). A no-digit label
    # is structurally incapable of being a bill / JCARR / OAC citation
    # (all of those require digits), so demote it to subject_general +
    # subject. Digit-containing unmatched rows stay as-is so the
    # genuinely-malformed-bill audit signal survives.
    if (
        kind == POSITION_KIND_BILL_REFERENCED
        and bill_class == BILL_CLASS_UNMATCHED
        and not re.search(r"\d", raw_label)
    ):
        kind = POSITION_KIND_SUBJECT_GENERAL
        bill_class = BILL_CLASS_SUBJECT

    norm_label = _normalize_identifier(raw_label) if kind == POSITION_KIND_BILL_REFERENCED else raw_label.strip()
    desc = _position_description_for(position, kind)

    if bill_class != BILL_CLASS_BILL:
        # Single-row emission for non-bill rows (jcarr / oac_rule / subject /
        # unmatched). Sponsor fields are null. Plan §4a "Conservation
        # implication" — these rows skip the cross-product entirely.
        return [
            _row(
                base,
                position_kind=kind,
                bill_label_raw=raw_label,
                bill_label_normalized=norm_label,
                bill_class=bill_class,
                bill_id=None,
                bill_title=None,
                position_description=desc,
                num_primary_sponsors=0,
                sponsor_lawmaker_id=None,
                sponsor_lawmaker_name=None,
                sponsor_role=None,
                confidence=_NON_BILL_CONFIDENCE[bill_class],
            )
        ]

    # bill_class == "bill". Try to join.
    bill_row = bills_by_norm.get(norm_label)
    if bill_row is None:
        # Bill-shaped label that doesn't join to Plural — downgrade to unmatched.
        return [
            _row(
                base,
                position_kind=kind,
                bill_label_raw=raw_label,
                bill_label_normalized=norm_label,
                bill_class=BILL_CLASS_UNMATCHED,
                bill_id=None,
                bill_title=None,
                position_description=desc,
                num_primary_sponsors=0,
                sponsor_lawmaker_id=None,
                sponsor_lawmaker_name=None,
                sponsor_role=None,
                confidence=_CONFIDENCE_UNMATCHED,
            )
        ]

    bill_id = bill_row["bill_id"]
    bill_title = bill_row.get("title")
    primaries = spons_by_bill_id.get(bill_id, [])
    n_primary = len(primaries)

    if n_primary == 0:
        # Defensive: bill exists in Plural but has no primary sponsorships.
        # Emit one row with null sponsor rather than silently dropping.
        return [
            _row(
                base,
                position_kind=kind,
                bill_label_raw=raw_label,
                bill_label_normalized=norm_label,
                bill_class=BILL_CLASS_BILL,
                bill_id=bill_id,
                bill_title=bill_title,
                position_description=desc,
                num_primary_sponsors=0,
                sponsor_lawmaker_id=None,
                sponsor_lawmaker_name=None,
                sponsor_role=None,
                confidence=_CONFIDENCE_DIRECT,
            )
        ]

    return [
        _row(
            base,
            position_kind=kind,
            bill_label_raw=raw_label,
            bill_label_normalized=norm_label,
            bill_class=BILL_CLASS_BILL,
            bill_id=bill_id,
            bill_title=bill_title,
            position_description=desc,
            num_primary_sponsors=n_primary,
            sponsor_lawmaker_id=p.get("person_id") or None,
            sponsor_lawmaker_name=p.get("name") or None,
            sponsor_role="primary",
            confidence=_CONFIDENCE_DIRECT,
        )
        for p in primaries
    ]


# ---------------------------------------------------------------------------
# Public entrypoint
# ---------------------------------------------------------------------------


def compose_bill_chain(
    extractions_dir: Path, plural_dir: Path
) -> pd.DataFrame:
    """Compose the OH bill-side chain DataFrame.

    Loads (extractions, plural bills, plural primary sponsorships), dedupes
    extractions to canonical, and walks every (filing, position) producing
    chain rows per the §4/§4a/§6 plan contracts.

    Output column shape is :data:`CHAIN_COLUMNS` regardless of input — an
    empty input still returns an empty DataFrame with the full schema.
    """
    filings_df = select_canonical_extraction(load_filings(extractions_dir))
    bills_df = load_plural_bills(plural_dir)
    spons_df = load_plural_sponsorships(plural_dir, classification="primary")

    # Index bills by normalized identifier for O(1) join.
    bills_by_norm: dict[str, dict[str, str]] = {
        row["identifier_norm"]: row.to_dict() for _, row in bills_df.iterrows()
    }

    # Group sponsorships by bill_id for O(1) cross-product fan-out.
    spons_by_bill_id: dict[str, list[dict[str, str]]] = {}
    for _, row in spons_df.iterrows():
        spons_by_bill_id.setdefault(row["bill_id"], []).append(row.to_dict())

    rows: list[dict[str, object]] = []
    for _, frow in filings_df.iterrows():
        filing: LobbyingFiling = frow["filing_obj"]
        base = _filing_base(filing)
        for position in filing.positions:
            rows.extend(_emit_position_rows(base, position, bills_by_norm, spons_by_bill_id))

    if not rows:
        return pd.DataFrame({c: [] for c in CHAIN_COLUMNS})

    df = pd.DataFrame(rows, columns=list(CHAIN_COLUMNS))
    # Numeric column dtype hygiene: num_primary_sponsors is int, not object.
    df["num_primary_sponsors"] = df["num_primary_sponsors"].astype("int64")
    return df
