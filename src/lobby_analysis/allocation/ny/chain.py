"""NY Phase-4 chain composer: company -> lobbyist -> bill -> lawmaker.

Unlike WI (whose lobbyist<->bill link had to be *modeled* via IPF, because WI
lobbyists file only aggregate hours), NY discloses the lobbyist->bill link
directly in ``client_semiannual``. So the NY chain is a **join**, not an
allocation: there is no ``graph.py`` / ``ipf.py`` here.

Two transforms make this module more than a plain join:

1. **Coalition beneficiary split (Decision 7).** Some NY ``beneficial_client``
   cells pack several beneficiaries into one semicolon-delimited string. The
   chain splits each into its own beneficiary and allocates credit evenly.
   :func:`split_beneficiaries` is the splitter (mirrors
   ``io.ny.parse.parse_individual_lobbyists``); the Phase-3 ``releases/ny/``
   entity tables keep the raw disclosed string for source fidelity — the split
   is a chain-layer transform only.

2. **No-loss conservation.** A filing with compensation ``C``, ``M``
   beneficiaries, and ``N`` bills emits ``M*N`` cells each carrying
   ``comp_per_cell``; the cells sum to ``C`` exactly. The split is a single
   :func:`io.ny.parse.even_split` over the cell count (``even_split(C, M*N)``),
   so the integer-cent remainder never compounds across the two axes. Sponsor
   fan-out replicates ``comp_per_cell`` across a bill's sponsors WITHOUT
   re-dividing it (the dollars attach to the bill, not to each lawmaker) — so a
   consumer must not sum ``comp_per_cell`` across sponsors of one bill.

The Open-States-dependent half (bill-id normalization to the OS ``identifier``
key, and the bill->sponsor join) lands once the gated OS NY bundle is staged
under ``data/bills/NY/2025/``.

Plan: ``docs/active/ny-disclosure-explore/plans/ny_disclosure_pipeline.md`` (Phase 4).
"""

from __future__ import annotations

import csv
import re
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from lobby_analysis.io.ny.parse import coerce_money, even_split

__all__ = [
    "NYSponsor",
    "NYBillMeta",
    "normalize_bill_id_to_os",
    "split_beneficiaries",
    "load_os_bills",
    "compose_chain",
    "materialize_chain",
]

# Allow the large OS CSVs (e.g. an 82MB vote_people file is sibling to the ones
# we read) to be parsed without a field-size ceiling surprise.
csv.field_size_limit(10**7)


#: NY lobbying ``bill_id`` shape: chamber letter + digits + optional ``-A``/``-B``
#: print suffix, optionally already space-separated. Calibrated to the OS NY
#: 2025-2026 bills.csv, whose ``identifier`` is ``<LETTER> <UNPADDED-DIGITS>``.
_OS_BILL_RE = re.compile(r"^\s*([A-Za-z])\s*0*(\d+)(?:-[A-Za-z]+)?\s*$")


def normalize_bill_id_to_os(bill_id) -> str | None:
    """Canonicalize a NY lobbying ``bill_id`` to the Open States ``identifier``.

    OS NY identifiers are ``<LETTER><SPACE><UNPADDED-DIGITS>`` (``A 1668``,
    ``S 550``) — a single space, no zero-padding, no print suffix. This maps the
    lobbying-side id (``A1668``, ``A00804``, ``S550-A``) onto that exact form so
    the bill->sponsor join hits:

    - strip the ``-A``/``-B`` amendment print suffix (OS keys the base bill);
    - drop leading zeros (the NY source is inconsistently padded — ``A00804`` vs
      ``A804`` — but OS is unpadded, so both collapse to ``A 804``);
    - insert the single space and uppercase the chamber letter.

    Returns ``None`` for anything that doesn't parse as a chamber-prefixed bill
    number (free text, empty, ``None``) — such rows are flagged as not
    OS-resolvable, never coerced into a fabricated key.
    """
    if bill_id is None:
        return None
    m = _OS_BILL_RE.match(str(bill_id))
    if m is None:
        return None
    chamber, digits = m.group(1).upper(), m.group(2)
    return f"{chamber} {int(digits)}"


def _slug(name: str) -> str:
    """Stable, case-insensitive slug from a name (matches ``io.ny.parse._slug``)."""
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def split_beneficiaries(raw) -> list[str]:
    """Split a (possibly coalition) ``beneficial_client`` cell into beneficiaries.

    A non-coalition client returns a single-element list (M=1, the per-cell
    split is then a no-op). A semicolon-delimited coalition cell returns one
    cleaned beneficiary per element. Each element is whitespace-trimmed; empty
    tokens (e.g. from a trailing ``;``) are dropped; duplicates within the one
    cell are de-duped by slug, order-preserving, keeping the first display form
    (mirrors ``parse.parse_individual_lobbyists``). An empty / whitespace /
    ``None`` cell yields ``[]``.
    """
    if raw is None:
        return []
    beneficiaries: list[str] = []
    seen: set[str] = set()
    for token in str(raw).split(";"):
        name = token.strip()
        if not name:
            continue
        slug = _slug(name)
        if not slug or slug in seen:
            continue
        seen.add(slug)
        beneficiaries.append(name)
    return beneficiaries


# ---------------------------------------------------------------------------
# OS bill metadata (the lawmaker spine)
# ---------------------------------------------------------------------------


@dataclass
class NYSponsor:
    """One primary sponsor of a NY bill.

    For individual legislators ``person_id`` is the OpenStates ``ocd-person/...``
    id and ``is_collective`` is False. For committee ("organization") sponsors
    ``person_id`` is None and ``is_collective`` is True.
    """

    name: str
    person_id: str | None
    is_collective: bool


@dataclass
class NYBillMeta:
    """Per-bill OS metadata keyed by the OS ``identifier`` (e.g. ``A 1668``)."""

    identifier: str
    ocd_bill_id: str
    title: str
    chamber: str
    primary_sponsors: list[NYSponsor]


def _os_bills_csv(csv_dir: Path) -> Path:
    """Locate the OS bills CSV in ``csv_dir`` (``NY_<session>_bills.csv``).

    The glob ``NY_*_bills.csv`` also matches the sibling
    ``NY_<session>_bill_related_bills.csv`` (a different schema), so pick the
    SHORTEST match: the related-bills filename is the canonical stem with
    ``_bill_related`` inserted, hence always strictly longer.
    """
    matches = list(csv_dir.glob("NY_*_bills.csv"))
    if not matches:
        raise FileNotFoundError(f"no NY_*_bills.csv under {csv_dir}")
    return min(matches, key=lambda p: len(p.name))


def _os_sponsorships_csv(csv_dir: Path) -> Path:
    matches = list(csv_dir.glob("NY_*_bill_sponsorships.csv"))
    if not matches:
        raise FileNotFoundError(f"no NY_*_bill_sponsorships.csv under {csv_dir}")
    return min(matches, key=lambda p: len(p.name))


def load_os_bills(csv_dir: Path) -> dict[str, NYBillMeta]:
    """Load OS NY bill metadata + **primary** sponsors, keyed by OS ``identifier``.

    Reads ``NY_<session>_bills.csv`` (one row per bill: ``id`` is the
    ``ocd-bill`` uuid, ``identifier`` the join key) and
    ``NY_<session>_bill_sponsorships.csv`` (``bill_id`` = the ocd-bill uuid).
    Only ``classification == 'primary'`` rows attach (cosponsors are deferred to
    a later refinement — they live in the same file but are out of v1 scope).
    Committee ("organization") primaries are kept as collective sponsors with
    ``person_id=None``, not dropped.
    """
    csv_dir = Path(csv_dir)

    # ocd-bill uuid -> list[NYSponsor] (primary only)
    sponsors_by_bill: dict[str, list[NYSponsor]] = {}
    with _os_sponsorships_csv(csv_dir).open(encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            if row.get("classification") != "primary":
                continue
            pid = (row.get("person_id") or "").strip() or None
            sponsors_by_bill.setdefault(row["bill_id"], []).append(
                NYSponsor(
                    name=(row.get("name") or "").strip(),
                    person_id=pid,
                    is_collective=pid is None,
                )
            )

    bills: dict[str, NYBillMeta] = {}
    with _os_bills_csv(csv_dir).open(encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            identifier = (row.get("identifier") or "").strip()
            if not identifier:
                continue
            bills[identifier] = NYBillMeta(
                identifier=identifier,
                ocd_bill_id=row["id"],
                title=(row.get("title") or "").strip(),
                chamber=(row.get("organization_classification") or "").strip(),
                primary_sponsors=sponsors_by_bill.get(row["id"], []),
            )
    return bills


# ---------------------------------------------------------------------------
# chain composer
# ---------------------------------------------------------------------------


_CHAIN_COLUMNS = [
    "reporting_year",
    "reporting_period",
    "filing_id",
    "lobbyist_id",
    "lobbyist_name",
    "client_id",
    "beneficiary_id",
    "beneficiary_name",
    "bill_id",
    "bill_print_version",
    "os_bill_identifier",
    "bill_title",
    "sponsor_lawmaker_id",
    "sponsor_lawmaker_name",
    "comp_per_cell",
    "filing_compensation",
    "n_beneficiaries_in_filing",
    "n_bills_in_filing",
    "os_matched",
    # ---- Disclosed-lawmaker enrichment (chain-completion plan, Phase 1+2) ----
    # ``disclosed_lawmakers`` is the set of resolved ``ocd-person`` IDs from
    # ``parties_lobbied`` for this row's ``(filing_id, lobbyist_id)``, sorted
    # alphabetically and semicolon-joined (empty string when no disclosed
    # contacts resolve). It is METADATA at the filing/lobbyist grain — it is
    # NOT a per-(bill, lawmaker) claim. ``parties_lobbied``'s grain is
    # per-filing SET (cartesian over the filing's bills), so the set attaches
    # to the *filing*, not to any specific bill.
    "disclosed_lawmakers",
    # ``sponsor_in_disclosed_set`` is True iff this row's
    # ``sponsor_lawmaker_id`` is in the (filing, lobbyist)'s disclosed set.
    # **CAVEAT**: with a typical fan-out of 36+ disclosed legislators per
    # (filing, lobbyist) in 2025, this is True often by base-rate, not by
    # specific intent — do NOT read True as "this filer lobbied this sponsor
    # about this bill". Read it as "this filer disclosed contact with this
    # sponsor on *something* in this filing."
    "sponsor_in_disclosed_set",
    # ``disclosed_only_lawmaker_count`` is, per (filing, lobbyist), the count
    # of resolved disclosed lawmakers who are NOT primary sponsors of any
    # MATCHED bill in the filing — the leadership / committee-chair signal.
    # The same int is replicated to every chain row of the group.
    "disclosed_only_lawmaker_count",
]


def _name_lookup(path: Path) -> dict[str, str]:
    """id -> name from a release entity TSV (clients/lobbyists)."""
    out: dict[str, str] = {}
    with path.open(encoding="utf-8") as fh:
        for row in csv.DictReader(fh, delimiter="\t"):
            out[row["id"]] = row["name"]
    return out


def _load_disclosed_contacts(release_dir: Path) -> dict[tuple[str, str], set[str]]:
    """Load ``NY_filing_parties_lobbied.tsv`` into ``(filing_id, lobbyist_id) ->
    set(ocd-person)``.

    Only rows with ``resolved=True`` AND a non-empty ``party_lobbied_person_id``
    contribute — unresolved rows (NYC municipal officials, executive offices,
    agencies, broadcasts; ~42% of edges in 2025) MUST NOT leak into the
    legislator set. The empty-id-but-resolved=True case (a fixture hostility,
    not seen in real data) is also dropped.

    The Phase-0 grain check (2026-06-08, plans/ny_chain_completion_sketch.md)
    confirmed ``(filing_id, lobbyist_id)`` is the correct join key under this
    branch's release schema — A and B (``+ client_id``) gave identical coverage
    of 97.63% (every (filing, lobbyist) group has exactly one client_id).

    Returns an empty dict if the file is absent — keeps the column additive
    rather than mandatory, so existing tests / consumers that pass a
    parties-less ``release_dir`` continue to work.
    """
    path = release_dir / "NY_filing_parties_lobbied.tsv"
    out: dict[tuple[str, str], set[str]] = {}
    if not path.exists():
        return out
    with path.open(encoding="utf-8") as fh:
        for row in csv.DictReader(fh, delimiter="\t"):
            if (row.get("resolved") or "").strip().lower() != "true":
                continue
            pid = (row.get("party_lobbied_person_id") or "").strip()
            if not pid:
                continue
            key = (row["filing_id"], row["lobbyist_id"])
            out.setdefault(key, set()).add(pid)
    return out


def compose_chain(release_dir: Path, os_bills: dict[str, NYBillMeta]) -> pd.DataFrame:
    """Compose the NY firm -> beneficiary -> bill -> sponsor chain.

    Reads ``NY_filing_bill_links.tsv`` + the entity tables from ``release_dir``,
    splits each coalition ``beneficial_client`` into beneficiaries (Decision 7),
    normalizes each ``bill_id`` to the OS key (Decision 8), and joins the OS
    primary sponsor(s). Emits one row per
    ``(period, lobbyist, beneficiary, bill, sponsor)``.

    Conservation (Decision 7): per filing — keyed
    ``(filing_id, lobbyist_id, client_id)`` — the compensation ``C`` is split
    evenly across the ``M`` beneficiaries x ``N`` bills via a single
    :func:`even_split` over the ``M*N`` distinct cells, so the cells sum to ``C``
    exactly. Sponsor fan-out replicates ``comp_per_cell`` across a bill's
    primary sponsors **without** re-dividing it, so ``comp_per_cell`` must not be
    summed across sponsor rows of one cell.

    Unmatched bills (no OS identifier match, or matched with zero structured
    sponsors) are FLAGGED (``os_matched=False``, empty sponsor) — never dropped —
    so dollars stay conserved.

    **Disclosed-lawmaker enrichment** (chain-completion plan, Phases 1+2). If
    ``release_dir/NY_filing_parties_lobbied.tsv`` exists, three extra columns
    are populated: ``disclosed_lawmakers`` (the sorted, ``;``-joined set of
    resolved ``ocd-person`` IDs for this row's ``(filing_id, lobbyist_id)``;
    empty string when none), ``sponsor_in_disclosed_set`` (True iff this row's
    ``sponsor_lawmaker_id`` is in the disclosed set — empty-id never qualifies),
    and ``disclosed_only_lawmaker_count`` (per ``(filing, lobbyist)``, the count
    of disclosed lawmakers NOT primary-sponsoring any MATCHED bill — the
    leadership / committee-chair signal; same int on every row of the group).
    The enrichment is purely additive — it never changes row count, money, or
    sponsor attachment. If the file is absent the three columns are still
    present with empty/False/0 defaults (back-compat).

    **Reading caveat (do not silently re-derive).** ``parties_lobbied``'s grain
    is per-filing SET (Phase-0 finding: cartesian, not mapping). So
    ``disclosed_lawmakers`` attaches at the filing/lobbyist level, NOT per bill,
    and ``sponsor_in_disclosed_set=True`` is NOT specific evidence that this
    filer lobbied this sponsor about this bill — with typical fan-outs of 36+
    legislators per (filing, lobbyist), inclusion is consistent with base-rate
    matching. The observed in-set rate (~56% on the 2026-06-08 build) is well
    short of fan-out saturation, so the negative case (False) carries some
    real signal (44% of matched rows have a sponsor the filer did NOT
    disclose). The interesting per-row signal is the conjunction of high
    ``sponsor_in_disclosed_set`` with low ``disclosed_only_lawmaker_count`` —
    the filer's disclosed contacts ARE the sponsors of the engaged bills.
    """
    release_dir = Path(release_dir)
    client_names = _name_lookup(release_dir / "NY_clients.tsv")
    lobbyist_names = _name_lookup(release_dir / "NY_lobbyists.tsv")
    # ``(filing_id, lobbyist_id) -> set(ocd-person)`` — resolved disclosed
    # lawmakers from ``NY_filing_parties_lobbied.tsv``. Empty dict if absent
    # (back-compat: callers without the parties release still get an empty
    # ``disclosed_lawmakers`` column rather than an error).
    disclosed = _load_disclosed_contacts(release_dir)

    # Group link rows by filing so M*N is known per filing.
    by_filing: dict[tuple, list[dict]] = {}
    with (release_dir / "NY_filing_bill_links.tsv").open(encoding="utf-8") as fh:
        for row in csv.DictReader(fh, delimiter="\t"):
            by_filing.setdefault(
                (row["filing_id"], row["lobbyist_id"], row["client_id"]), []
            ).append(row)

    rows: list[dict] = []
    # Precompute the joined string per ``(filing_id, lobbyist_id)`` so we
    # don't sort/join inside the inner loop (medians of 36+ IDs per group).
    disclosed_str = {key: ";".join(sorted(s)) for key, s in disclosed.items()}
    for (filing_id, lobbyist_id, client_id), links in by_filing.items():
        client_raw = client_names.get(client_id, "")
        beneficiaries = split_beneficiaries(client_raw)
        if not beneficiaries:
            # No usable beneficiary name — fall back to the raw client cell so the
            # filing's dollars are not silently dropped.
            beneficiaries = [client_raw] if client_raw else [client_id]
        m = len(beneficiaries)
        n = len(links)

        comp = coerce_money(links[0].get("filing_compensation"))
        parts = even_split(comp, m * n) if comp is not None else [None] * (m * n)

        # Cells in deterministic order: beneficiary-major, bill-minor.
        cell_idx = 0
        for beneficiary in beneficiaries:
            beneficiary_id = f"NY-client-{_slug(beneficiary)}"
            for link in links:
                part = parts[cell_idx]
                cell_idx += 1
                bill_id = link["bill_id"]
                os_key = normalize_bill_id_to_os(bill_id)
                bill_meta = os_bills.get(os_key) if os_key else None
                sponsors = bill_meta.primary_sponsors if bill_meta else []
                pl_key = (filing_id, lobbyist_id)
                disclosed_set = disclosed.get(pl_key, set())
                base = {
                    "reporting_year": link.get("reporting_year", ""),
                    "reporting_period": link.get("reporting_period", ""),
                    "filing_id": filing_id,
                    "lobbyist_id": lobbyist_id,
                    "lobbyist_name": lobbyist_names.get(lobbyist_id, ""),
                    "client_id": client_id,
                    "beneficiary_id": beneficiary_id,
                    "beneficiary_name": beneficiary,
                    "bill_id": bill_id,
                    "bill_print_version": link.get("bill_print_version", ""),
                    "os_bill_identifier": bill_meta.identifier if bill_meta else "",
                    "bill_title": bill_meta.title if bill_meta else "",
                    "comp_per_cell": "" if part is None else str(part),
                    "filing_compensation": link.get("filing_compensation", ""),
                    "n_beneficiaries_in_filing": m,
                    "n_bills_in_filing": n,
                    "os_matched": bool(sponsors),
                    "disclosed_lawmakers": disclosed_str.get(pl_key, ""),
                    # ``disclosed_only_lawmaker_count`` is filled in a second
                    # pass below (it needs the union of sponsor IDs across all
                    # chain rows for this ``(filing, lobbyist)``).
                    "disclosed_only_lawmaker_count": 0,
                }
                if sponsors:
                    for sp in sponsors:
                        sid = sp.person_id or ""
                        rows.append(
                            {
                                **base,
                                "sponsor_lawmaker_id": sid,
                                "sponsor_lawmaker_name": sp.name,
                                "sponsor_in_disclosed_set": bool(sid) and sid in disclosed_set,
                            }
                        )
                else:
                    rows.append(
                        {
                            **base,
                            "sponsor_lawmaker_id": "",
                            "sponsor_lawmaker_name": "",
                            "sponsor_in_disclosed_set": False,
                        }
                    )

    # ---- Second pass: ``disclosed_only_lawmaker_count`` per (filing, lobbyist).
    # For each (filing, lobbyist), this is |disclosed_set \ matched_sponsors|:
    # the count of resolved disclosed lawmakers who are NOT primary sponsors of
    # any MATCHED bill in the filing (the leadership / committee-chair signal).
    # Unmatched bills contribute no sponsor IDs — see the docstring's caveat.
    matched_sponsors_per_group: dict[tuple[str, str], set[str]] = {}
    for r in rows:
        if not r["os_matched"]:
            continue
        sid = r["sponsor_lawmaker_id"]
        if not sid:
            continue
        key = (r["filing_id"], r["lobbyist_id"])
        matched_sponsors_per_group.setdefault(key, set()).add(sid)
    only_count: dict[tuple[str, str], int] = {
        key: len(disclosed.get(key, set()) - matched_sponsors_per_group.get(key, set()))
        for key in disclosed
    }
    for r in rows:
        key = (r["filing_id"], r["lobbyist_id"])
        r["disclosed_only_lawmaker_count"] = only_count.get(key, 0)

    chain = pd.DataFrame(rows, columns=_CHAIN_COLUMNS)
    chain = chain.sort_values(
        by=[
            "reporting_year",
            "reporting_period",
            "filing_id",
            "lobbyist_id",
            "beneficiary_id",
            "bill_id",
            "sponsor_lawmaker_id",
        ],
        kind="stable",
    ).reset_index(drop=True)
    return chain


def materialize_chain(
    release_dir: Path, csv_dir: Path, output_path: Path
) -> int:
    """Compose the chain and write it to ``output_path`` as a deterministic TSV.

    Loads the OS bill spine from ``csv_dir`` (the gitignored OS bundle), composes
    the chain over ``release_dir``'s ``releases/ny/`` tables, and writes a
    tab-separated file (``\\n`` line terminator for byte-identical reruns).
    Returns the number of chain rows written.
    """
    output_path = Path(output_path)
    os_bills = load_os_bills(csv_dir)
    chain = compose_chain(release_dir, os_bills)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    chain.to_csv(output_path, sep="\t", index=False, lineterminator="\n")
    return len(chain)
