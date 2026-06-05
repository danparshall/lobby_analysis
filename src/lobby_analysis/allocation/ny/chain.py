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

import re

__all__ = ["split_beneficiaries"]


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
