"""Phase 3 — OH gifts edge composer.

Composes the ``releases/oh/gifts/`` artifact from OH AER Section II.A (gifts)
+ Section II.B (meals) extractions.

Per plan §3 (OH structural delta) and STATE_COVERAGE.md OH section, this is
OH's **distinctive native edge**: a per-event ``(lobbyist → lawmaker)``
transactional layer that WI and NY don't disclose. We expose it as a
sibling artifact (`releases/oh/gifts/`), not as a sub-column on the chain.

Plan reference: ``docs/active/oh-portal-extraction/plans/20260611_oh_chain_composer_design.md`` §5 Phase 3.

Schema (10 columns):

- ``report_period`` (str): same convention as chain
- ``filing_id`` (str): the AER report ID
- ``principal_name`` (str): the lobbyist's employer for the period
- ``lobbyist_name`` (str): filer of the AER
- ``lawmaker_name_raw`` (str): from ``Gift.recipient_name``
- ``lawmaker_id`` (str|null): resolved via ``oh.csv`` matcher if file present;
  null if file absent, or if the recipient name doesn't disambiguate
- ``event_type`` (str): ``"meal"`` for Section II.B (``gift_type == "meal"``);
  ``"gift"`` for everything else (Section II.A)
- ``description`` (str|null): from ``Gift.description``
- ``amount_dollars`` (float|null): from ``Gift.value``
- ``gift_date`` (date|null): from ``Gift.gift_date``

The ``oh.csv`` resolver does prefix-strip ("Sen.", "Sen", "Senator", "Rep.",
"Rep", "Representative") + exact full-name lookup. Ambiguous matches (multiple
oh.csv entries with the same surname when the recipient gives only a surname)
resolve to null rather than picking arbitrarily.
"""

from __future__ import annotations

import re
from collections import Counter
from pathlib import Path

import pandas as pd

from lobby_analysis.allocation.oh.load import load_filings, select_canonical_extraction
from lobby_analysis.models.filings import Gift, LobbyingFiling

__all__ = ["GIFTS_COLUMNS", "compose_gifts"]


GIFTS_COLUMNS: tuple[str, ...] = (
    "report_period",
    "filing_id",
    "principal_name",
    "lobbyist_name",
    "lawmaker_name_raw",
    "lawmaker_id",
    "event_type",
    "description",
    "amount_dollars",
    "gift_date",
)


# ---------------------------------------------------------------------------
# oh.csv lawmaker resolver
# ---------------------------------------------------------------------------

_TITLE_PREFIX_RE = re.compile(
    r"^(?:Senator|Sen\.?|Representative|Rep\.?)\s+",
    re.IGNORECASE,
)


def _strip_title_prefix(name: str) -> str:
    """Strip a leading 'Sen.'/'Rep.'/'Senator'/'Representative' from a name."""
    return _TITLE_PREFIX_RE.sub("", name).strip()


def _build_lawmaker_index(
    oh_csv_path: Path,
) -> tuple[dict[str, str], dict[str, str | None]]:
    """Read oh.csv and return two lookup tables:

    - full-name (case-folded, whitespace-collapsed) → ocd-person id
    - surname (case-folded) → ocd-person id, or None when ambiguous

    The surname table maps ambiguous surnames to ``None`` so the resolver
    can detect ambiguity and decline rather than pick arbitrarily.
    """
    df = pd.read_csv(oh_csv_path, dtype=str).fillna("")
    full_name_index: dict[str, str] = {}
    surname_counter: Counter = Counter()
    surname_first: dict[str, str] = {}
    for _, row in df.iterrows():
        ocd_id = row["id"]
        full = _normalize_for_lookup(row["name"])
        surname = _normalize_for_lookup(row.get("family_name", ""))
        if full:
            full_name_index[full] = ocd_id
        if surname:
            surname_counter[surname] += 1
            surname_first.setdefault(surname, ocd_id)
    surname_index: dict[str, str | None] = {
        s: (surname_first[s] if n == 1 else None) for s, n in surname_counter.items()
    }
    return full_name_index, surname_index


def _normalize_for_lookup(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").strip().lower())


def _resolve_lawmaker(
    raw_name: str,
    full_index: dict[str, str],
    surname_index: dict[str, str | None],
) -> str | None:
    """Return the ocd-person id matching ``raw_name``, or None."""
    if not raw_name:
        return None
    stripped = _strip_title_prefix(raw_name)
    normalized = _normalize_for_lookup(stripped)
    if not normalized:
        return None
    # Try full-name match first.
    hit = full_index.get(normalized)
    if hit:
        return hit
    # Try surname-only fallback if recipient gave just one token.
    tokens = normalized.split()
    if len(tokens) == 1:
        surname_hit = surname_index.get(tokens[0])
        if surname_hit:  # None if ambiguous
            return surname_hit
    return None


# ---------------------------------------------------------------------------
# Composer
# ---------------------------------------------------------------------------


def _report_period(filing: LobbyingFiling) -> str:
    if filing.reporting_period_start and filing.reporting_period_end:
        return f"{filing.reporting_period_start}..{filing.reporting_period_end}"
    if filing.reporting_period_start:
        return str(filing.reporting_period_start)
    if filing.reporting_period_end:
        return str(filing.reporting_period_end)
    return ""


def _event_type_for(gift: Gift) -> str:
    """Section II.A ("gifts") vs II.B ("meals") routing.

    Per plan §3 / §4 schema sketch, OH AER splits the disclosure into:
      Section II.A — gifts (anything not a meal)
      Section II.B — meals
    The Gift model's ``gift_type`` enum has 'meal' as one value alongside
    travel/lodging/entertainment/event_ticket/other. Anything tagged 'meal'
    goes to II.B (event_type='meal'); everything else to II.A (event_type='gift').
    """
    if gift.gift_type == "meal":
        return "meal"
    return "gift"


def compose_gifts(
    extractions_dir: Path, oh_csv_path: Path | None = None
) -> pd.DataFrame:
    """Compose the OH gifts DataFrame.

    Walks canonical extractions (deduped) and emits one row per
    ``(filing, gift)``. If ``oh_csv_path`` is provided, resolves
    ``lawmaker_id`` via prefix-stripped exact name match (full-name
    preferred; unambiguous surname-only as fallback). If ``oh_csv_path``
    is None, ``lawmaker_id`` is always null.
    """
    if oh_csv_path is not None:
        full_index, surname_index = _build_lawmaker_index(oh_csv_path)
    else:
        full_index, surname_index = {}, {}

    filings = select_canonical_extraction(load_filings(extractions_dir))

    rows: list[dict[str, object]] = []
    for _, frow in filings.iterrows():
        filing: LobbyingFiling = frow["filing_obj"]
        report_period = _report_period(filing)
        principal_name = filing.employer.name if filing.employer else None
        lobbyist_name = filing.filer_person.name if filing.filer_person else None
        for gift in filing.gifts:
            lawmaker_id = (
                _resolve_lawmaker(gift.recipient_name, full_index, surname_index)
                if oh_csv_path is not None
                else None
            )
            rows.append(
                {
                    "report_period": report_period,
                    "filing_id": filing.filing_id,
                    "principal_name": principal_name,
                    "lobbyist_name": lobbyist_name,
                    "lawmaker_name_raw": gift.recipient_name,
                    "lawmaker_id": lawmaker_id,
                    "event_type": _event_type_for(gift),
                    "description": gift.description,
                    "amount_dollars": gift.value,
                    "gift_date": gift.gift_date,
                }
            )

    if not rows:
        return pd.DataFrame({c: [] for c in GIFTS_COLUMNS})
    return pd.DataFrame(rows, columns=list(GIFTS_COLUMNS))
