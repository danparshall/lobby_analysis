"""NY ``parties_lobbied`` disclosed-lawmaker edge (the MVP resolver + extraction).

NY discloses, per filing, the free-text "who was lobbied" field
``parties_lobbied``. Unlike the chain's lawmaker edge (the bill *primary sponsor*,
*inferred* via Open States), this is the genuinely **disclosed** contact. Phase 0
(``docs/active/ny-disclosure-explore/results/20260606_ny_parties_lobbied_grain.md``)
characterized it:

  * **Grain** — ``parties_lobbied`` is a per-filing SET (its own denormalization
    axis: it varies within a filing and even within one ``focus_identifying_number``).
    The edge is therefore ``FILING_KEY -> {distinct resolved parties}`` — there is
    no faithful per-bill association to recover.
  * **Matching** — the disclosure text is ``"<Title> First [M.] Last[, staff
    member]"``. Exact full-name match on the OS bill-sponsorship roster resolves
    only 63% (leadership rarely sponsors, so they are absent from that roster); a
    deterministic **first-name + last-name key** (drop the middle initial)
    resolves 93.7% with ZERO collisions on the real NY roster. That is the MVP key.
  * **Scope** — only legislator-titled values (``Senator`` / ``Assembly member`` /
    ``Assemblyman`` / ``Assemblywoman``) are resolved to an ``ocd-person``.
    Executive offices, agencies, committee/program staff, and "entire legislature"
    broadcasts are kept with ``resolved=False`` and the raw string preserved — no
    ``target_kind`` taxonomy yet (post-MVP). No row is dropped.

The edge is **unweighted** — a contact edge, not a dollar allocation — so there is
no conservation invariant; the metric is the resolution rate.
"""

from __future__ import annotations

import csv
import re
from pathlib import Path

import pandas as pd

from lobby_analysis.io.ny.grain import resolve_superseded
from lobby_analysis.io.ny.materialize import _cell, _write_tsv
from lobby_analysis.io.ny.parse import _clean_name, parse_client, parse_principal_lobbyist

__all__ = [
    "build_legislator_roster",
    "resolve_party_lobbied",
    "extract_filing_parties",
    "materialize_parties_lobbied",
]

#: Legislator titles that gate resolution. Executive titles (Governor,
#: Comptroller, Attorney General) are deliberately EXCLUDED — they name an
#: official who is not a legislator and must not resolve to an ``ocd-person`` in
#: the legislative roster. Space-anchored, so order is irrelevant.
_LEG_TITLES = (
    "assembly member",
    "assemblywoman",
    "assemblyman",
    "assembly woman",
    "assembly man",
    "senator",
)
#: ``, staff member`` / ``staff member`` trailing tag (the comma is sometimes
#: absent in the source) — a named legislator's office, still that legislator.
_STAFF = re.compile(r",?\s*staff member\s*$", re.IGNORECASE)
#: parenthetical noise: ``(effective 8/24/21)``, ``(NYSED)``.
_PAREN = re.compile(r"\s*\([^)]*\)")
#: name suffix dropped before the first+last key.
_SUFFIX = re.compile(r",?\s*(jr|sr|ii|iii|iv)\.?\s*$", re.IGNORECASE)
_WS = re.compile(r"\s+")

_FIELDS = (
    "reporting_year",
    "reporting_period",
    "filing_id",
    "lobbyist_id",
    "client_id",
    "party_lobbied_raw",
    "party_lobbied_name",
    "party_lobbied_person_id",
    "resolved",
)


# ---------------------------------------------------------------------------
# normalization + resolution
# ---------------------------------------------------------------------------


def _strip_legislator_title(text: str) -> str | None:
    """Return ``text`` minus a leading legislator title, or ``None`` if it has none."""
    low = text.lower()
    for title in _LEG_TITLES:
        if low.startswith(title + " "):
            return text[len(title):].strip()
    return None


def _strip_noise(name: str) -> str:
    """Drop the ``staff member`` tag and parentheticals; collapse whitespace."""
    name = _STAFF.sub("", name)
    name = _PAREN.sub("", name)
    return _WS.sub(" ", name).strip()


def _first_last_key(name: str) -> str:
    """The Phase-0 match key: first token + last token, casefolded.

    Drops the middle initial (the disclosure carries it, many roster names do
    not) and any Jr/Sr/III suffix. Phase 0 verified ZERO first+last collisions on
    the real NY legislator roster, so this permissive key adds no ambiguity.
    """
    name = _SUFFIX.sub("", name).strip()
    tokens = name.split()
    if len(tokens) < 2:
        return name.casefold()
    return f"{tokens[0]} {tokens[-1]}".casefold()


def resolve_party_lobbied(raw, roster: dict[str, str]) -> tuple[str, str, str | None, bool]:
    """Resolve one ``parties_lobbied`` value against the legislator roster.

    Returns ``(party_raw, party_name, person_id, resolved)``:

      * ``party_raw`` — the HTML-decoded, cleaned disclosure string (preserved
        verbatim for every value, resolved or not);
      * ``party_name`` — the title/noise-stripped legislator name when resolved,
        else ``""``;
      * ``person_id`` — the OS ``ocd-person`` id when resolved, else ``None``;
      * ``resolved`` — ``True`` only when the value carries a *legislator* title
        and its first+last key hits the roster.

    A value without a legislator title (an executive office, agency, committee, or
    "entire legislature" broadcast) is never resolved — it is kept unresolved with
    the raw preserved, so the disclosed edge is never over-claimed as a specific
    legislator.
    """
    cleaned = _clean_name(raw)
    if not cleaned:
        return ("", "", None, False)
    residual = _strip_legislator_title(cleaned)
    if residual is None:
        return (cleaned, "", None, False)
    name = _strip_noise(residual)
    person_id = roster.get(_first_last_key(name))
    if person_id:
        return (cleaned, name, person_id, True)
    return (cleaned, "", None, False)


# ---------------------------------------------------------------------------
# roster
# ---------------------------------------------------------------------------


def _os_sponsorships_csv(csv_dir: Path) -> Path:
    """Locate ``NY_*_bill_sponsorships.csv`` (shortest match avoids sibling files).

    Mirrors the shortest-match glob discipline of
    ``allocation.ny.chain._os_sponsorships_csv``; kept local to avoid an
    io -> allocation layer dependency.
    """
    matches = list(Path(csv_dir).glob("NY_*_bill_sponsorships.csv"))
    if not matches:
        raise FileNotFoundError(f"no NY_*_bill_sponsorships.csv under {csv_dir}")
    return min(matches, key=lambda p: len(p.name))


def build_legislator_roster(csv_dir: Path) -> dict[str, str]:
    """Build a ``first+last -> ocd-person`` roster from the OS sponsorship file.

    Reads every ``entity_type == 'person'`` sponsorship row with a non-empty
    ``person_id`` (primary AND cosponsor — the goal is the widest legislator name
    set, not the bill linkage) and keys it by :func:`_first_last_key`. First write
    wins on a key; Phase 0 verified there are no first+last collisions on the real
    roster, so the choice is moot in practice.
    """
    csv.field_size_limit(10**7)
    roster: dict[str, str] = {}
    with _os_sponsorships_csv(csv_dir).open(encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            if row.get("entity_type") != "person":
                continue
            person_id = (row.get("person_id") or "").strip()
            name = (row.get("name") or "").strip()
            if not person_id or not name:
                continue
            roster.setdefault(_first_last_key(_clean_name(name)), person_id)
    return roster


# ---------------------------------------------------------------------------
# extraction
# ---------------------------------------------------------------------------


def extract_filing_parties(df: pd.DataFrame, roster: dict[str, str]) -> pd.DataFrame:
    """Extract the ``FILING_KEY -> {distinct resolved parties}`` edge.

    ``df`` is a column-normalized ``client_semiannual`` frame (the output of
    :func:`columns.normalize_columns`; ``parties_lobbied`` passes through unchanged
    as it is already canonical). Superseded submissions are dropped first (the same
    guard the dollar pipeline applies, via :func:`grain.resolve_superseded`), so an
    amended-away contact list never leaks in. Surviving rows are exploded to one
    output row per ``(filing_id, lobbyist_id, client_id, distinct party)``:

      * resolved parties dedupe by ``person_id`` (so ``"Senator X"`` and
        ``"Senator X, staff member"`` collapse to one legislator edge);
      * unresolved parties dedupe by the cleaned raw string (so distinct offices /
        broadcasts stay distinct), keeping the lexicographically smallest raw form.

    Returns a deterministically sorted frame with :data:`_FIELDS` columns.
    """
    if df.empty:
        return pd.DataFrame(columns=list(_FIELDS))

    survivors = resolve_superseded(df)

    # Memoize the expensive per-value work (regex resolution + entity-id slugging)
    # over the DISTINCT values — the source is denormalized ~1,300x, so the same
    # party / firm / client string recurs across millions of rows. This turns
    # ~11M regex+slug calls into a few tens of thousands.
    party_cache: dict[object, tuple[str, str, str | None, bool]] = {}
    firm_cache: dict[object, str] = {}
    client_cache: dict[object, str] = {}

    seen: dict[tuple, dict] = {}
    cols = (
        survivors["parties_lobbied"],
        survivors["principal_lobbyist"],
        survivors["beneficial_client"],
        survivors["form_submission_id"],
        survivors["reporting_year"],
        survivors["reporting_period"],
    )
    for raw_party, firm_raw, client_raw, sub, year, period in zip(*cols):
        cached = party_cache.get(raw_party)
        if cached is None:
            cached = resolve_party_lobbied(raw_party, roster)
            party_cache[raw_party] = cached
        party_raw, party_name, person_id, resolved = cached
        if not party_raw:
            continue

        lobbyist_id = firm_cache.get(firm_raw)
        if lobbyist_id is None:
            lobbyist_id = parse_principal_lobbyist(firm_raw).id
            firm_cache[firm_raw] = lobbyist_id
        client_id = client_cache.get(client_raw)
        if client_id is None:
            client_id = parse_client(client_raw).id
            client_cache[client_raw] = client_id

        filing_id = str(sub)
        dedup = person_id if resolved else party_raw.casefold()
        key = (filing_id, lobbyist_id, client_id, dedup)
        if key in seen:
            if party_raw < seen[key]["party_lobbied_raw"]:
                seen[key]["party_lobbied_raw"] = party_raw
            continue
        seen[key] = {
            "reporting_year": str(year),
            "reporting_period": str(period),
            "filing_id": filing_id,
            "lobbyist_id": lobbyist_id,
            "client_id": client_id,
            "party_lobbied_raw": party_raw,
            "party_lobbied_name": party_name,
            "party_lobbied_person_id": person_id or "",
            "resolved": resolved,
        }

    out = pd.DataFrame(list(seen.values()), columns=list(_FIELDS))
    out["resolved"] = out["resolved"].astype(bool)
    out = out.sort_values(
        by=[
            "filing_id",
            "lobbyist_id",
            "client_id",
            "party_lobbied_person_id",
            "party_lobbied_raw",
        ],
        kind="stable",
    ).reset_index(drop=True)
    return out


# ---------------------------------------------------------------------------
# materialize
# ---------------------------------------------------------------------------


def materialize_parties_lobbied(parties: pd.DataFrame, *, output_dir: Path) -> dict[str, int]:
    """Write ``releases/ny/NY_filing_parties_lobbied.tsv`` from an extracted frame.

    Mirrors :mod:`io.ny.materialize` determinism conventions (``csv.DictWriter``,
    ``\\t`` + ``\\n``, ``None`` -> empty cell, deterministic sort, byte-identical
    re-runs). ``resolved`` is serialized as ``"True"`` / ``"False"``. Returns a
    one-key row-count dict.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    rows = [
        {
            "reporting_year": _cell(rec.get("reporting_year")),
            "reporting_period": _cell(rec.get("reporting_period")),
            "filing_id": _cell(rec.get("filing_id")),
            "lobbyist_id": _cell(rec.get("lobbyist_id")),
            "client_id": _cell(rec.get("client_id")),
            "party_lobbied_raw": _cell(rec.get("party_lobbied_raw")),
            "party_lobbied_name": _cell(rec.get("party_lobbied_name")),
            "party_lobbied_person_id": _cell(rec.get("party_lobbied_person_id")),
            "resolved": _cell(bool(rec.get("resolved"))),
        }
        for rec in parties.to_dict(orient="records")
    ]
    rows.sort(
        key=lambda r: (
            r["filing_id"],
            r["lobbyist_id"],
            r["client_id"],
            r["party_lobbied_person_id"],
            r["party_lobbied_raw"],
        )
    )
    n = _write_tsv(output_dir / "NY_filing_parties_lobbied.tsv", _FIELDS, rows)
    return {"filing_parties_lobbied": n}
