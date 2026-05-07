"""Project PRI 2010 disclosure-law per-item scores into a StateMasterRecord.

Stage B of `docs/active/statute-retrieval/plans/20260430_compendium_population_and_smr_fill.md`.

The SMR's *output shape* is the long-term shape (compendium-keyed); only the
upstream data source is temporary. When the statute-extraction harness ships
in a later branch (Stage C.2), it emits the same FieldRequirement shape but
populates `framework_references` based on which rubrics independently flag
the item.
"""

from __future__ import annotations

from datetime import date
from typing import Iterable

from lobby_analysis.models import (
    CompendiumItem,
    FieldRequirement,
    FrameworkReference,
    RegistrationRequirement,
    ReportingPartyRequirement,
    StateMasterRecord,
)


# A-series role mapping (per plan B.4 + state_master.RegistrationRequirement.role literal)
_A_TO_ROLE: dict[str, str] = {
    "A1": "lobbyist",
    "A2": "volunteer_lobbyist",
    "A3": "principal",
    "A4": "lobbying_firm",
    "A5": "governors_office",
    "A6": "executive_agency",
    "A7": "legislative_branch",
    "A8": "independent_agency",
    "A9": "local_government",
    "A10": "government_lobbying_government",
    "A11": "other_public_entity",
}


# Frequency option mapping (E1h_*/E2h_*)
_H_TO_FREQUENCY: dict[str, str] = {
    "i": "monthly",
    "ii": "quarterly",
    "iii": "tri_annually",
    "iv": "semi_annually",
    "v": "annually",
    "vi": "other",
}


# Field-level PRI items that map to FieldRequirement (per plan B.4)
_FIELD_REQUIREMENT_PRI_IDS: set[str] = {
    "E1b", "E1c", "E1d", "E1e",
    "E1f_i", "E1f_ii", "E1f_iii", "E1f_iv",
    "E1g_i", "E1g_ii",
    "E1i", "E1j",
    "E2b", "E2c", "E2d", "E2e",
    "E2f_i", "E2f_ii", "E2f_iii", "E2f_iv",
    "E2g_i", "E2g_ii",
    "E2i",
}


def _index_compendium_by_pri(compendium: Iterable[CompendiumItem]) -> dict[str, CompendiumItem]:
    out: dict[str, CompendiumItem] = {}
    for item in compendium:
        for ref in item.framework_references:
            if ref.framework == "pri_2010_disclosure":
                out[ref.item_id] = item
    return out


def _to_int(value: str) -> int:
    """Parse the PRI score column. Empty / non-numeric → 0."""
    s = (value or "").strip()
    if not s:
        return 0
    try:
        return int(float(s))
    except ValueError:
        return 0


def _to_float(value: str) -> float | None:
    s = (value or "").strip()
    if not s:
        return None
    try:
        return float(s)
    except ValueError:
        return None


def _legal_citation(row: dict) -> str | None:
    quote = (row.get("evidence_quote_or_url") or "").strip()
    return quote or None


def _project_registration_requirements(
    by_item: dict[str, dict],
    pri_index: dict[str, CompendiumItem],
) -> list[RegistrationRequirement]:
    reqs: list[RegistrationRequirement] = []
    for a_id, role in _A_TO_ROLE.items():
        row = by_item.get(a_id)
        if row is None:
            continue
        comp = pri_index.get(a_id)
        framework_references = list(comp.framework_references) if comp else [
            FrameworkReference(framework="pri_2010_disclosure", item_id=a_id)
        ]
        reqs.append(
            RegistrationRequirement(
                role=role,  # type: ignore[arg-type]
                required=bool(_to_int(row["score"])),
                framework_references=framework_references,
                legal_citation=_legal_citation(row),
                notes=(row.get("notes") or ""),
            )
        )
    return reqs


def _project_de_minimis(
    by_item: dict[str, dict],
) -> tuple[float | None, str | None, float | None, str | None]:
    """Return (financial_threshold, financial_citation, time_threshold, time_citation).

    Per plan B.4: D0 is the gate; if 0, all de_minimis_* fields stay None.
    """
    d0 = _to_int((by_item.get("D0") or {}).get("score", "0"))
    if d0 == 0:
        return (None, None, None, None)

    financial_threshold: float | None = None
    financial_citation: str | None = None
    if _to_int((by_item.get("D1_present") or {}).get("score", "0")):
        d1v = by_item.get("D1_value", {})
        financial_threshold = _to_float(d1v.get("score", ""))
        financial_citation = _legal_citation(d1v)

    time_threshold: float | None = None
    time_citation: str | None = None
    if _to_int((by_item.get("D2_present") or {}).get("score", "0")):
        d2v = by_item.get("D2_value", {})
        time_threshold = _to_float(d2v.get("score", ""))
        time_citation = _legal_citation(d2v)

    return (financial_threshold, financial_citation, time_threshold, time_citation)


def _resolve_frequency(
    by_item: dict[str, dict], h_prefix: str
) -> tuple[str | None, str]:
    """Return (reporting_frequency, frequency_notes).

    Plan B.4: first true frequency wins; multiple → "other" + free-text notes.
    Plan B.5 STOP-AND-NOTIFY clause is enforced at the CLI level (build-smr
    subcommand), not here — this helper preserves the data so the caller can
    detect the multi-set case via the notes field.
    """
    set_freqs: list[str] = []
    for suffix, freq in _H_TO_FREQUENCY.items():
        row = by_item.get(f"{h_prefix}_{suffix}")
        if row is not None and _to_int(row["score"]):
            set_freqs.append(freq)
    if not set_freqs:
        return (None, "")
    if len(set_freqs) == 1:
        return (set_freqs[0], "")
    return (
        "other",
        f"PRI flagged multiple reporting frequencies: {', '.join(set_freqs)}",
    )


def _project_reporting_parties(
    by_item: dict[str, dict],
    pri_index: dict[str, CompendiumItem],
) -> list[ReportingPartyRequirement]:
    out: list[ReportingPartyRequirement] = []
    for gate_id, entity_role in (("E1a", "client"), ("E2a", "lobbyist")):
        row = by_item.get(gate_id)
        if row is None:
            continue
        score = _to_int(row["score"])
        comp = pri_index.get(gate_id)
        framework_references = list(comp.framework_references) if comp else [
            FrameworkReference(framework="pri_2010_disclosure", item_id=gate_id)
        ]
        h_prefix = "E1h" if gate_id == "E1a" else "E2h"
        frequency, freq_notes = _resolve_frequency(by_item, h_prefix)
        out.append(
            ReportingPartyRequirement(
                entity_role=entity_role,  # type: ignore[arg-type]
                report_type="activity_report",
                filing_status="required" if score else "not_required",
                reporting_frequency=frequency,  # type: ignore[arg-type]
                framework_references=framework_references,
                notes=freq_notes,
            )
        )
    return out


def _reporting_party_for_pri(pri_id: str) -> str:
    if pri_id.startswith("E1"):
        return "client"
    if pri_id.startswith("E2"):
        return "lobbyist"
    return "all"


def _project_field_requirements(
    by_item: dict[str, dict],
    pri_index: dict[str, CompendiumItem],
) -> list[FieldRequirement]:
    out: list[FieldRequirement] = []
    for pri_id in _FIELD_REQUIREMENT_PRI_IDS:
        row = by_item.get(pri_id)
        if row is None:
            continue
        comp = pri_index.get(pri_id)
        if comp is None or comp.maps_to_state_master_field in (None, ""):
            continue
        score = _to_int(row["score"])
        out.append(
            FieldRequirement(
                field_path=comp.maps_to_state_master_field,  # type: ignore[arg-type]
                reporting_party=_reporting_party_for_pri(pri_id),  # type: ignore[arg-type]
                status="required" if score else "not_applicable",
                evidence_source="statute_verified",
                evidence_notes=(row.get("notes") or ""),
                framework_references=list(comp.framework_references),
                legal_citation=_legal_citation(row),
            )
        )
    return out


def _build_notes(by_item: dict[str, dict]) -> str:
    """Free-text paragraph capturing items that don't have structured slots:
    B-series govt exemptions, C-series public-entity definition.

    Per plan B.4 these route to StateMasterRecord.notes.
    """
    paragraphs: list[str] = []

    b_items = [(b, by_item.get(b)) for b in ("B1", "B2", "B3", "B4")]
    if any(row is not None for _, row in b_items):
        lines = ["Government exemptions (PRI B-series):"]
        for b_id, row in b_items:
            if row is None:
                continue
            score = _to_int(row["score"])
            citation = _legal_citation(row) or ""
            lines.append(f"  {b_id}={score}" + (f" — {citation}" if citation else ""))
        paragraphs.append("\n".join(lines))

    c_items = [(c, by_item.get(c)) for c in ("C0", "C1", "C2", "C3")]
    if any(row is not None for _, row in c_items):
        lines = ["Public-entity definition (PRI C-series):"]
        for c_id, row in c_items:
            if row is None:
                continue
            score = _to_int(row["score"])
            citation = _legal_citation(row) or ""
            lines.append(f"  {c_id}={score}" + (f" — {citation}" if citation else ""))
        paragraphs.append("\n".join(lines))

    return "\n\n".join(paragraphs)


def project_pri_scores_to_smr(
    pri_score_rows: list[dict],
    compendium: list[CompendiumItem],
    state: str,
    state_name: str,
    vintage: int,
    run_id: str,
) -> StateMasterRecord:
    """Project PRI 2010 disclosure-law per-item scores into a StateMasterRecord.

    The output shape is forward-compatible with the eventual statute-extraction
    harness (Stage C.2): same FieldRequirement / ReportingPartyRequirement /
    RegistrationRequirement structure, with framework_references carrying the
    full compendium union (not just PRI). Only the upstream data source —
    PRI per-item scores — is temporary.
    """
    by_item: dict[str, dict] = {row["item_id"]: row for row in pri_score_rows}
    pri_index = _index_compendium_by_pri(compendium)

    reg_reqs = _project_registration_requirements(by_item, pri_index)
    fin_thr, fin_cit, time_thr, time_cit = _project_de_minimis(by_item)
    reporting_parties = _project_reporting_parties(by_item, pri_index)
    field_reqs = _project_field_requirements(by_item, pri_index)
    notes = _build_notes(by_item)

    return StateMasterRecord(
        state=state,
        state_name=state_name,
        version=f"pri-2010-baseline-{run_id[:8]}",
        effective_start=date(vintage, 1, 1),
        effective_end=None,
        last_updated=date.today(),
        legal_citations=[],
        registration_requirements=reg_reqs,
        de_minimis_financial_threshold=fin_thr,
        de_minimis_financial_citation=fin_cit,
        de_minimis_time_threshold=time_thr,
        de_minimis_time_citation=time_cit,
        reporting_parties=reporting_parties,
        field_requirements=field_reqs,
        notes=notes,
    )
