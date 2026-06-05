"""Phase 2 parser step for the NY Open NY (Socrata) lobbying pipeline.

Sits between :func:`columns.normalize_columns` (raw -> canonical column names)
and :func:`grain.collapse_to_filing_grain` (which requires a canonical
``bill_id`` column to already exist). Three concerns:

1. **Canonical ``bill_id`` derivation** — the State-Bill scoping decision. A
   real, Open-States-joinable bill number lives in ``focus_identifying_number``
   only when ``focus_type == "State Bill"``. Scope is the focus type **alone**
   (not ``level_of_government``): a ``State Bill`` filed at ``Both (State and
   Municipal)`` level is still a state bill (``S550-A`` in the Phase-0 fixture),
   and the ``level`` clause Phase 0 first tried drops ~25% of State-Bill rows.
   ``Municipal Bill`` is a distinct ``focus_type`` value, excluded by the
   focus-type test without consulting ``level``. The amendment print suffix
   (``-A``/``-B``) is preserved here; stripping it to hit the Open States key is
   the separate Phase-4 chain normalizer's job.

2. **Entity parsing** — name-keyed Popolo ``Organization`` / ``Person`` (NY has
   no stable numeric entity id), under the ``NY-{role}-{slug}`` id convention
   (parallel to WI's ``WI-principal-{id}``). Role prefix keeps a firm and a
   client that share a name distinct.

3. **Filing parsing + money coercion** — one collapsed grain row -> a
   ``LobbyingFiling`` (firm as organizational filer, role ``firm``). NY money is
   dirty (``"$1000"`` / bare ``"17160"`` / literal ``"$"``); the coercer yields
   ``Decimal`` for real amounts and ``None`` (not 0) for the absent cases.
"""

from __future__ import annotations

import re
from decimal import Decimal, InvalidOperation

import pandas as pd

from lobby_analysis.models.entities import Organization, Person
from lobby_analysis.models.filings import LobbyingFiling

STATE = "NY"

#: ``S550``, ``A10003``, ``S550-A`` — chamber letter + digits + optional print
#: suffix. Anchored so free text ("various", "see attached") never matches.
_BILL_RE = re.compile(r"^([SA])\s*(\d+)(?:-([A-Z]+))?$", re.IGNORECASE)


# ---------------------------------------------------------------------------
# bill_id derivation (the State-Bill scoping decision)
# ---------------------------------------------------------------------------


def derive_bill_id(focus_type, focus_identifying_number) -> str | None:
    """Return the canonical NY ``bill_id`` for a row, or ``None``.

    A bill_id is produced only when ``focus_type`` is exactly ``"State Bill"``
    and ``focus_identifying_number`` parses as a NY bill identifier
    (``S###`` / ``A###``, optionally ``-A``/``-B`` suffixed). The print suffix
    is preserved (it records which print was lobbied). Whitespace is trimmed and
    the key is uppercased so the same bill doesn't fork into variants.

    Deliberately takes no ``level_of_government`` argument: bill identity depends
    on the focus type only, never on the engagement's jurisdictional scope.
    """
    if focus_type != "State Bill":
        return None
    if focus_identifying_number is None:
        return None
    text = str(focus_identifying_number).strip()
    if not text:
        return None
    m = _BILL_RE.match(text)
    if m is None:
        return None
    chamber, number, suffix = m.group(1).upper(), m.group(2), m.group(3)
    base = f"{chamber}{number}"
    return f"{base}-{suffix.upper()}" if suffix else base


def add_bill_id_column(df: pd.DataFrame) -> pd.DataFrame:
    """Add a canonical ``bill_id`` column to a column-normalized frame.

    Applies :func:`derive_bill_id` rowwise over ``focus_type`` +
    ``focus_identifying_number``. This interposes between
    :func:`columns.normalize_columns` and :func:`grain.collapse_to_filing_grain`,
    which requires ``bill_id`` to exist. Original columns are left intact.
    """
    out = df.copy()
    out["bill_id"] = pd.Series(
        [
            derive_bill_id(ft, fin)
            for ft, fin in zip(out["focus_type"], out["focus_identifying_number"])
        ],
        index=out.index,
        dtype=object,
    )
    return out


# ---------------------------------------------------------------------------
# entity parsing
# ---------------------------------------------------------------------------


def _clean_name(raw) -> str:
    """Strip a trailing ``;`` delimiter and collapse stray whitespace."""
    text = "" if raw is None else str(raw)
    return text.strip().rstrip(";").strip()


def _slug(name: str) -> str:
    """A stable, case-insensitive slug from a name for use in entity ids."""
    s = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return s


def parse_principal_lobbyist(raw_name) -> Organization:
    """The lobbying firm (``principal_lobbyist``) -> Organization."""
    name = _clean_name(raw_name)
    return Organization(id=f"NY-lobbyist-{_slug(name)}", name=name, source_state=STATE)


def parse_client(raw_name) -> Organization:
    """The client (``beneficial_client``) -> Organization."""
    name = _clean_name(raw_name)
    return Organization(id=f"NY-client-{_slug(name)}", name=name, source_state=STATE)


def parse_individual_lobbyists(raw) -> list[Person]:
    """Split the semicolon-delimited ``individual_lobbyist_name`` into People.

    Trims stray internal/trailing whitespace, drops empty tokens (e.g. from a
    trailing delimiter), and de-dupes repeated names within the one field.
    """
    if raw is None:
        return []
    people: list[Person] = []
    seen: set[str] = set()
    for token in str(raw).split(";"):
        name = token.strip()
        if not name:
            continue
        pid = f"NY-person-{_slug(name)}"
        if pid in seen:
            continue
        seen.add(pid)
        people.append(Person(id=pid, name=name, source_state=STATE))
    return people


# ---------------------------------------------------------------------------
# money coercion + filing parsing
# ---------------------------------------------------------------------------


def coerce_money(raw) -> Decimal | None:
    """Coerce a NY money string to ``Decimal``, or ``None`` if not reported.

    Handles ``"$1000"`` / ``"$24,000"`` / bare ``"17160"``; treats the literal
    ``"$"``, empty string, whitespace, and ``None`` as absent (``None``, not 0).
    An explicit ``"0"`` is a reported value and round-trips as ``Decimal('0')``.
    """
    if raw is None:
        return None
    text = str(raw).replace("$", "").replace(",", "").strip()
    if not text:
        return None
    try:
        return Decimal(text)
    except InvalidOperation:
        return None


def parse_filing(row: dict) -> LobbyingFiling:
    """Map one collapsed grain row to a ``LobbyingFiling``.

    The firm (``principal_lobbyist``) is the organizational filer; ``filer_role``
    is ``firm`` (NY client-semiannual is the firm's compensation report, mapped
    to ``filing_type='expenditure_report'`` per WI's spend-report convention).
    Compensation is filing-level and already de-duplicated upstream, so it is
    carried, not summed. The filing id distinguishes the (submission, client)
    tuple so two clients under one submission don't collide.
    """
    firm = parse_principal_lobbyist(row["principal_lobbyist"])
    client = parse_client(row["beneficial_client"])
    submission = str(row["form_submission_id"])
    filing_id = f"NY-filing-{submission}-{_slug(client.name)}"
    return LobbyingFiling(
        id=filing_id,
        state=STATE,
        filing_id=submission,
        filing_type="expenditure_report",
        filer_organization=firm,
        filer_role="firm",
        total_compensation=coerce_money(row.get("filing_compensation")),
    )
