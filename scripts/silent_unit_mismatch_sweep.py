"""Silent unit-mismatch sweep on CPI-2015-readable compendium rows for WI.

Compares the actual emitted values in the wide-pass result JSONs against
WI's published CPI 2015 per-state oracle. For each (compendium row × CPI
indicator) pair, classifies the cell as MATCH / MISMATCH / INSTANTIATION_FAILED
/ NOT_EMITTED / AMBIGUOUS / COMPOUND_ROLE.

Output: a markdown table sorted by classification (mismatches first) plus
summary statistics. Pure analysis — no API spend.

Plan: docs/active/wi-ralph-cpi-renewal-cadence/plans/20260604_silent_unit_mismatch_sweep.md
Convo: docs/active/wi-ralph-cpi-renewal-cadence/convos/20260604_phase_b_silent_unit_mismatch_sweep.md
"""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# ----------------------------------------------------------------------------
# Paths and constants
# ----------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parents[1]
COMPENDIUM_TSV = REPO_ROOT / "compendium" / "disclosure_side_compendium_items_v2.tsv"
CPI_ORACLE_CSV = (
    REPO_ROOT
    / "docs"
    / "historical"
    / "compendium-source-extracts"
    / "results"
    / "cpi_2015_c11_per_state_scores.csv"
)
WIDE_PASS_JSON_DIR = (
    REPO_ROOT
    / "docs"
    / "active"
    / "wi-tier1-direct-read"
    / "results"
    / "tier_1"
    / "WI_2025"
)
RESULTS_DOC = (
    REPO_ROOT
    / "docs"
    / "active"
    / "wi-ralph-cpi-renewal-cadence"
    / "results"
    / "20260604_silent_unit_mismatch_sweep.md"
)

STATE_ABBR = "WI"
STATE_FULL = "Wisconsin"
MODELS = ["claude-opus-4-7", "gpt-5.2-2025-12-11"]
CHUNKS = [
    "enforcement_and_audits",
    "lobbying_definitions",
    "lobbyist_spending_report",
    "principal_spending_report",
    "registration_mechanics_and_exemptions",
    "registration_thresholds",
]
RUNS = (1, 2, 3)

# Projection-mapping doc uses working names; the v2 TSV canonicalizes.
WORKING_TO_TSV: dict[str, str] = {
    "compensation_threshold_for_lobbyist_registration": "lobbyist_registration_threshold_compensation_dollars",
    "lobbyist_spending_report_includes_compensation": "lobbyist_spending_report_includes_total_compensation",
    "registration_deadline_days_after_first_lobbying": "lobbyist_registration_deadline_days_after_first_lobbying",
}

# ----------------------------------------------------------------------------
# CPI indicator specs (hard-coded from cpi_2015_c11_projection_mapping.md)
# ----------------------------------------------------------------------------


@dataclass(frozen=True)
class IndicatorSpec:
    ind_id: str
    axis: str  # "legal" or "practical"
    rows: tuple[str, ...]  # working names from projection mapping doc
    description: str
    compound: bool = False


INDICATORS: list[IndicatorSpec] = [
    IndicatorSpec(
        "IND_196",
        "legal",
        ("def_target_legislative_branch", "def_target_governors_office"),
        "Definition recognizes exec-branch lobbyists alongside legislative",
        compound=True,
    ),
    IndicatorSpec(
        "IND_197",
        "legal",
        ("compensation_threshold_for_lobbyist_registration",),
        "Anyone paid is a lobbyist (compensation-threshold value)",
    ),
    IndicatorSpec(
        "IND_198",
        "practical",
        ("lobbyist_registration_required",),
        "All paid lobbyists actually register (de facto)",
    ),
    IndicatorSpec(
        "IND_199",
        "legal",
        ("lobbyist_registration_renewal_cadence",),
        "Annual registration filing required by law",
    ),
    IndicatorSpec(
        "IND_200",
        "practical",
        ("registration_deadline_days_after_first_lobbying",),
        "Lobbyists register promptly after initial activity (de facto)",
    ),
    IndicatorSpec(
        "IND_201",
        "legal",
        (
            "lobbyist_spending_report_required",
            "lobbyist_spending_report_includes_itemized_expenses",
            "lobbyist_spending_report_includes_compensation",
        ),
        "Lobbyists file detailed spending reports in law",
        compound=True,
    ),
    IndicatorSpec(
        "IND_202",
        "practical",
        ("lobbyist_spending_report_filing_cadence",),
        "Lobbyists file detailed spending reports with reasonable frequency (de facto)",
    ),
    IndicatorSpec(
        "IND_203",
        "legal",
        (
            "principal_spending_report_required",
            "principal_spending_report_includes_compensation_paid_to_lobbyists",
        ),
        "Principals required to fill out spending reports",
        compound=True,
    ),
    IndicatorSpec(
        "IND_204",
        "practical",
        ("principal_spending_report_includes_compensation_paid_to_lobbyists",),
        "Principals list lobbyist compensation in practice (de facto)",
    ),
    IndicatorSpec(
        "IND_205",
        "practical",
        (
            "lobbying_disclosure_documents_online",
            "lobbying_disclosure_documents_free_to_access",
            "lobbying_disclosure_offline_request_response_time_days",
        ),
        "Citizens can access disclosure docs reasonably (de facto)",
        compound=True,
    ),
    IndicatorSpec(
        "IND_206",
        "practical",
        ("lobbying_data_open_data_quality",),
        "Disclosure info in open data format (de facto)",
    ),
    IndicatorSpec(
        "IND_207",
        "legal",
        ("lobbying_disclosure_audit_required_in_law",),
        "Auditing required in law",
    ),
    IndicatorSpec(
        "IND_208",
        "practical",
        ("lobbying_disclosure_audit_required_in_law",),
        "Audits performed in practice (de facto)",
    ),
    IndicatorSpec(
        "IND_209",
        "practical",
        ("lobbying_violation_penalties_imposed_in_practice",),
        "Penalties imposed when violations occur (de facto)",
    ),
]


# ----------------------------------------------------------------------------
# Projection rules — per IND, project compendium row values to CPI tier
# ----------------------------------------------------------------------------


def _to_int(v: Any) -> int | None:
    if v is None:
        return None
    if isinstance(v, bool):
        return int(v)
    if isinstance(v, (int, float)):
        return int(v)
    if isinstance(v, str):
        try:
            return int(v.strip())
        except ValueError:
            return None
    return None


def _to_float(v: Any) -> float | None:
    if v is None:
        return None
    if isinstance(v, bool):
        return float(v)
    if isinstance(v, (int, float)):
        return float(v)
    if isinstance(v, str):
        try:
            return float(v.strip())
        except ValueError:
            return None
    return None


def project_to_cpi_tier(
    indicator: IndicatorSpec,
    row_values: dict[str, Any],
) -> tuple[str | None, str]:
    """Project compendium row values to a CPI tier.

    Treats numeric values per v2 convention (e.g., IND_199 cadence = months).
    Returns (projected_tier, projection_note). projected_tier is None for
    indicators we cannot project (practical-only, or rule not implemented).
    """
    # ---- IND_196 (2-tier): (legislative AND governors_office) → YES; else NO
    if indicator.ind_id == "IND_196":
        leg = row_values.get("def_target_legislative_branch")
        gov = row_values.get("def_target_governors_office")
        if leg is None or gov is None:
            return None, f"missing inputs: leg={leg!r}, gov={gov!r}"
        return ("YES" if (bool(leg) and bool(gov)) else "NO"), f"leg={leg!r} AND gov={gov!r}"

    # ---- IND_197 (3-tier): threshold == 0 → YES; > 0 → MODERATE; null → NO
    if indicator.ind_id == "IND_197":
        threshold = row_values.get("compensation_threshold_for_lobbyist_registration")
        if threshold is None:
            return "NO", "threshold == null → NO"
        t = _to_float(threshold)
        if t is None:
            return None, f"unparseable threshold: {threshold!r}"
        if t == 0:
            return "YES", "threshold == 0 → YES"
        return "MODERATE", f"threshold == {t} > 0 → MODERATE"

    # ---- IND_199 (3-tier): cadence ≤ 12 months → YES; > 12 → MODERATE;
    #      null / 'none' / 'no_registration_required' → NO
    if indicator.ind_id == "IND_199":
        cadence = row_values.get("lobbyist_registration_renewal_cadence")
        if cadence is None:
            return "NO", "cadence == null → NO"
        if isinstance(cadence, str):
            s = cadence.strip().lower()
            if s in ("none", "no_renewal_required", "no_registration_required"):
                return "NO", f"cadence == {cadence!r} → NO"
            if s == "annual":
                return "YES", "cadence == 'annual' → YES"
            if s in ("biennial", "triennial", "less_frequent_than_biennial"):
                return "MODERATE", f"cadence == {cadence!r} → MODERATE"
            # Could be a numeric string
            n = _to_int(cadence)
            if n is None:
                return None, f"unparseable cadence string: {cadence!r}"
            cadence = n
        n = _to_int(cadence)
        if n is None:
            return None, f"unparseable cadence: {cadence!r}"
        if n <= 12:
            return "YES", f"cadence == {n} months ≤ 12 → YES (v2-convention)"
        return "MODERATE", f"cadence == {n} months > 12 → MODERATE (v2-convention)"

    # ---- IND_201 (3-tier compound):
    #      (req AND itemized AND comp) → YES;
    #      (req AND (itemized XOR comp)) → MODERATE;
    #      NOT req OR (req AND no itemized AND no comp) → NO
    if indicator.ind_id == "IND_201":
        req = row_values.get("lobbyist_spending_report_required")
        item = row_values.get("lobbyist_spending_report_includes_itemized_expenses")
        comp = row_values.get("lobbyist_spending_report_includes_compensation")
        if any(v is None for v in (req, item, comp)):
            return None, f"missing inputs: req={req!r}, item={item!r}, comp={comp!r}"
        if not bool(req):
            return "NO", f"req={req!r} → NO"
        if bool(item) and bool(comp):
            return "YES", "req AND itemized AND comp → YES"
        if bool(item) or bool(comp):
            return "MODERATE", f"req AND (itemized={item!r} XOR comp={comp!r}) → MODERATE"
        return "NO", "req AND not itemized AND not comp → NO"

    # ---- IND_203 (3-tier compound):
    #      (req AND comp) → YES; (req AND NOT comp) → MODERATE; NOT req → NO
    if indicator.ind_id == "IND_203":
        req = row_values.get("principal_spending_report_required")
        comp = row_values.get(
            "principal_spending_report_includes_compensation_paid_to_lobbyists"
        )
        if any(v is None for v in (req, comp)):
            return None, f"missing inputs: req={req!r}, comp={comp!r}"
        if not bool(req):
            return "NO", f"req={req!r} → NO"
        if bool(comp):
            return "YES", "req AND comp → YES"
        return "MODERATE", "req AND NOT comp → MODERATE"

    # ---- IND_207 (3-tier): EnumCell passthrough → YES/MODERATE/NO
    if indicator.ind_id == "IND_207":
        val = row_values.get("lobbying_disclosure_audit_required_in_law")
        if val is None:
            return "NO", "value == null → NO"
        s = str(val).strip()
        val_to_tier = {
            "regular_third_party_audit_required": "YES",
            "audit_only_when_irregularities_suspected_or_compliance_review": "MODERATE",
            "no_audit_requirement": "NO",
            "YES": "YES",
            "MODERATE": "MODERATE",
            "NO": "NO",
        }
        t = val_to_tier.get(s)
        if t is None:
            t = val_to_tier.get(s.upper())
        if t is not None:
            return t, f"value == {val!r} → {t}"
        return None, f"unparseable audit value: {val!r}"

    # Practical-only indicators or unimplemented compound rules
    return None, f"projection rule for {indicator.ind_id} not implemented in this sweep"


# ----------------------------------------------------------------------------
# Loaders
# ----------------------------------------------------------------------------


def load_cpi_readable_rows() -> dict[str, dict[str, str]]:
    """Return CPI-readable rows from v2 TSV, keyed by row_id."""
    out: dict[str, dict[str, str]] = {}
    with COMPENDIUM_TSV.open() as f:
        reader = csv.DictReader(f, delimiter="\t")
        for r in reader:
            if "cpi_2015" in r["rubrics_reading"].split(";"):
                out[r["compendium_row_id"]] = r
    return out


def normalize_cpi_oracle(v: str) -> str:
    """Case-normalize YES/MODERATE/NO; pass through numeric strings."""
    s = str(v).strip()
    if s.upper() in ("YES", "MODERATE", "NO"):
        return s.upper()
    return s


def load_wi_oracle() -> dict[str, str]:
    """WI's CPI 2015 score for each IND_xxx."""
    out: dict[str, str] = {}
    with CPI_ORACLE_CSV.open() as f:
        reader = csv.DictReader(f)
        for r in reader:
            if r["state"] == STATE_FULL:
                out[r["indicator_id"]] = normalize_cpi_oracle(r["score"])
    return out


def load_wide_pass_emissions() -> dict[tuple[str, str], dict[tuple[str, int], dict[str, Any]]]:
    """Load emissions per (row_id, axis) across (model, run) tuples.

    Status values: 'instantiated', 'instantiation_failed', 'not_emitted'.
    """
    out: dict[tuple[str, str], dict[tuple[str, int], dict[str, Any]]] = defaultdict(dict)
    for model in MODELS:
        for chunk in CHUNKS:
            for run in RUNS:
                path = WIDE_PASS_JSON_DIR / f"{model}__{chunk}__run{run}.json"
                data = json.loads(path.read_text())
                emitted_per_cell: dict[tuple[str, str], dict[str, Any]] = {}
                # legal_roster: list of [row_id, axis] expected to be extracted
                legal_roster = data.get("legal_roster", [])
                # Successful emissions
                for cell_entry in data.get("instantiated_cells", []):
                    cell = cell_entry.get("cell", {})
                    cell_id = cell.get("cell_id", [None, None])
                    if not isinstance(cell_id, (list, tuple)) or len(cell_id) < 2:
                        continue
                    row_id, axis = cell_id[0], cell_id[1]
                    if row_id is None:
                        continue
                    emitted_per_cell[(row_id, axis)] = {
                        "status": "instantiated",
                        "value": cell.get("value"),
                        "confidence": cell.get("confidence"),
                        "cell_class": cell_entry.get("cell_class"),
                        "cited_section": cell_entry.get("cited_section"),
                    }
                # Errors
                for err in data.get("errors", []):
                    if err.get("reason") != "instantiation_failed":
                        continue
                    key = err.get("key", [None, None])
                    if not isinstance(key, (list, tuple)) or len(key) < 2:
                        continue
                    row_id, axis = key[0], key[1]
                    args = err.get("arguments", {})
                    emitted_per_cell[(row_id, axis)] = {
                        "status": "instantiation_failed",
                        "value": args.get("value"),
                        "error": err.get("error"),
                        "confidence": args.get("confidence"),
                        "cited_section": args.get("cited_section"),
                    }
                # not_emitted = expected but absent
                for entry in legal_roster:
                    if isinstance(entry, (list, tuple)) and len(entry) >= 2:
                        key = (entry[0], entry[1])
                    else:
                        continue
                    if key not in emitted_per_cell:
                        emitted_per_cell[key] = {"status": "not_emitted"}
                # Fold into the global structure
                for k, v in emitted_per_cell.items():
                    out[k][(model, run)] = v
    return dict(out)


# ----------------------------------------------------------------------------
# Classification
# ----------------------------------------------------------------------------


@dataclass
class CellClassification:
    indicator: IndicatorSpec
    tsv_row_id: str
    cell_type: str
    axis: str
    wi_oracle: str
    # Per (model, run) info
    emissions: dict[tuple[str, int], dict[str, Any]] = field(default_factory=dict)
    projected_tier_per_run: dict[tuple[str, int], str | None] = field(default_factory=dict)
    projection_notes: dict[tuple[str, int], str] = field(default_factory=dict)
    overall_classification: str = "PENDING"
    notes: str = ""


def classify_indicator(
    indicator: IndicatorSpec,
    cpi_rows: dict[str, dict[str, str]],
    wi_oracle: dict[str, str],
    emissions: dict[tuple[str, str], dict[tuple[str, int], dict[str, Any]]],
) -> list[CellClassification]:
    """Classify each row of an indicator. For compound indicators, returns one
    entry per contributing row, plus the composite projection in notes."""
    results: list[CellClassification] = []
    oracle = wi_oracle.get(indicator.ind_id, "UNKNOWN")

    # Resolve working names → TSV ids. Some working-name rows aren't in
    # cpi_2015's rubrics_reading set (e.g. def_target_legislative_staff is
    # focal_2024 / pri-side). The composite projection still needs those
    # values; we pull from emissions if available, regardless of TSV
    # membership.
    tsv_rows = [WORKING_TO_TSV.get(w, w) for w in indicator.rows]

    # If indicator is practical-only OR projection rule unimplemented:
    if indicator.axis == "practical":
        for w_name, tsv_id in zip(indicator.rows, tsv_rows, strict=True):
            row_meta = cpi_rows.get(tsv_id, {})
            results.append(
                CellClassification(
                    indicator=indicator,
                    tsv_row_id=tsv_id,
                    cell_type=row_meta.get("cell_type", "(not in cpi-readable TSV subset)"),
                    axis="practical",
                    wi_oracle=oracle,
                    overall_classification="NOT_EMITTED (axis=practical)",
                    notes=(
                        f"{indicator.ind_id} reads only the practical axis. "
                        f"Legal-axis dispatch did not extract this cell; cannot compare."
                    ),
                )
            )
        return results

    # Legal axis — single-row or compound
    if not indicator.compound:
        tsv_id = tsv_rows[0]
        working = indicator.rows[0]
        row_meta = cpi_rows.get(tsv_id, {})
        cls = CellClassification(
            indicator=indicator,
            tsv_row_id=tsv_id,
            cell_type=row_meta.get("cell_type", "(unknown)"),
            axis="legal",
            wi_oracle=oracle,
        )
        cell_emissions = emissions.get((tsv_id, "legal"), {})
        # Tally projected tiers per (model, run)
        match_count = 0
        mismatch_count = 0
        failed_count = 0
        not_emitted_count = 0
        for mr in [(m, r) for m in MODELS for r in RUNS]:
            em = cell_emissions.get(mr)
            cls.emissions[mr] = em or {"status": "not_emitted"}
            if em is None or em.get("status") == "not_emitted":
                cls.projected_tier_per_run[mr] = None
                cls.projection_notes[mr] = "not_emitted"
                not_emitted_count += 1
                continue
            if em.get("status") == "instantiation_failed":
                cls.projected_tier_per_run[mr] = None
                cls.projection_notes[mr] = (
                    f"instantiation_failed; attempted value={em.get('value')!r}"
                )
                failed_count += 1
                continue
            # Project the emitted value
            tier, note = project_to_cpi_tier(indicator, {working: em.get("value")})
            cls.projected_tier_per_run[mr] = tier
            cls.projection_notes[mr] = note
            if tier is None:
                # Unprojectable but instantiated; treat as MISMATCH candidate
                mismatch_count += 1
            elif tier == oracle:
                match_count += 1
            else:
                mismatch_count += 1
        # Classify overall
        cls.overall_classification = _summarize_classification(
            match_count, mismatch_count, failed_count, not_emitted_count
        )
        cls.notes = _format_notes(match_count, mismatch_count, failed_count, not_emitted_count, oracle)
        results.append(cls)
        return results

    # Compound legal-axis indicator
    # For each (model, run): collect each row's emitted value, run composite projection
    composite_per_run: dict[tuple[str, int], tuple[str | None, str]] = {}
    for mr in [(m, r) for m in MODELS for r in RUNS]:
        row_values: dict[str, Any] = {}
        any_failed = False
        any_missing = False
        for w_name, tsv_id in zip(indicator.rows, tsv_rows, strict=True):
            em = emissions.get((tsv_id, "legal"), {}).get(mr)
            if em is None or em.get("status") == "not_emitted":
                row_values[w_name] = None
                any_missing = True
            elif em.get("status") == "instantiation_failed":
                row_values[w_name] = None
                any_failed = True
            else:
                row_values[w_name] = em.get("value")
        if any_failed:
            composite_per_run[mr] = (None, "at least one row instantiation_failed")
        elif any_missing:
            composite_per_run[mr] = (None, "at least one row not_emitted")
        else:
            composite_per_run[mr] = project_to_cpi_tier(indicator, row_values)

    composite_match = sum(1 for t, _ in composite_per_run.values() if t == oracle)
    composite_mismatch = sum(
        1 for t, _ in composite_per_run.values() if t is not None and t != oracle
    )
    composite_skipped = len(composite_per_run) - composite_match - composite_mismatch
    composite_summary = (
        f"composite: match={composite_match}/6 mismatch={composite_mismatch}/6 "
        f"unprojectable={composite_skipped}/6"
    )

    # Emit one row per contributing compendium row, classified as COMPOUND_ROLE
    for w_name, tsv_id in zip(indicator.rows, tsv_rows, strict=True):
        row_meta = cpi_rows.get(tsv_id, {})
        cls = CellClassification(
            indicator=indicator,
            tsv_row_id=tsv_id,
            cell_type=row_meta.get("cell_type", "(not in cpi-readable TSV subset)"),
            axis="legal",
            wi_oracle=oracle,
        )
        cell_emissions = emissions.get((tsv_id, "legal"), {})
        match_count = mismatch_count = failed_count = not_emitted_count = 0
        for mr in [(m, r) for m in MODELS for r in RUNS]:
            em = cell_emissions.get(mr)
            cls.emissions[mr] = em or {"status": "not_emitted"}
            if em is None or em.get("status") == "not_emitted":
                cls.projected_tier_per_run[mr] = None
                cls.projection_notes[mr] = "not_emitted"
                not_emitted_count += 1
                continue
            if em.get("status") == "instantiation_failed":
                cls.projected_tier_per_run[mr] = None
                cls.projection_notes[mr] = (
                    f"instantiation_failed; attempted value={em.get('value')!r}"
                )
                failed_count += 1
                continue
            # Note: this is per-row classification; the composite is in notes
            cls.projected_tier_per_run[mr] = "(see composite)"
            cls.projection_notes[mr] = f"value={em.get('value')!r}"
            match_count += 1  # Just for completeness counting
        # Per-row classification for compound is "COMPOUND_ROLE"
        cls.overall_classification = "COMPOUND_ROLE"
        cls.notes = (
            f"{indicator.ind_id} is compound (reads {len(indicator.rows)} rows: "
            f"{', '.join(WORKING_TO_TSV.get(w, w) for w in indicator.rows)}). "
            f"{composite_summary}. WI oracle = {oracle}."
            f" Composite projections per run: "
            + ", ".join(
                f"({m[0][:8]}/r{m[1]}: {t or '∅'} — {n})"
                for m, (t, n) in composite_per_run.items()
            )
        )
        results.append(cls)
    return results


def _summarize_classification(
    match: int, mismatch: int, failed: int, not_emitted: int
) -> str:
    total = match + mismatch + failed + not_emitted
    if total == 0:
        return "EMPTY"
    if mismatch > 0:
        return f"MISMATCH ({mismatch}/{total})"
    if failed > 0 and match == 0:
        return f"INSTANTIATION_FAILED ({failed}/{total})"
    if failed > 0 and match > 0:
        return f"MIXED (match={match}, failed={failed})"
    if not_emitted == total:
        return "NOT_EMITTED"
    if match == total:
        return "MATCH"
    return f"PARTIAL (match={match}/{total})"


def _format_notes(match: int, mismatch: int, failed: int, not_emitted: int, oracle: str) -> str:
    parts = [f"WI oracle = {oracle}"]
    parts.append(
        f"match={match}/6 mismatch={mismatch}/6 failed={failed}/6 not_emitted={not_emitted}/6"
    )
    return "; ".join(parts)


# ----------------------------------------------------------------------------
# Output
# ----------------------------------------------------------------------------


CLASSIFICATION_SORT_KEY = {
    "MISMATCH": 0,
    "MIXED": 1,
    "INSTANTIATION_FAILED": 2,
    "PARTIAL": 3,
    "COMPOUND_ROLE": 4,
    "NOT_EMITTED": 5,
    "MATCH": 6,
    "EMPTY": 7,
}


def sort_key(cls: CellClassification) -> tuple[int, str, str]:
    top = cls.overall_classification.split(" ", 1)[0]
    return (CLASSIFICATION_SORT_KEY.get(top, 99), cls.indicator.ind_id, cls.tsv_row_id)


def _fmt_value(v: Any) -> str:
    if isinstance(v, str):
        return repr(v)
    return repr(v)


def render_emissions_cell(cls: CellClassification, model: str) -> str:
    parts = []
    for run in RUNS:
        em = cls.emissions.get((model, run), {"status": "not_emitted"})
        st = em.get("status")
        if st == "instantiated":
            parts.append(_fmt_value(em.get("value")))
        elif st == "instantiation_failed":
            parts.append(f"FAIL:{_fmt_value(em.get('value'))}")
        else:
            parts.append("∅")
    return " / ".join(parts)


def render_results_doc(classifications: list[CellClassification]) -> str:
    classifications_sorted = sorted(classifications, key=sort_key)
    summary = defaultdict(int)
    for cls in classifications_sorted:
        top = cls.overall_classification.split(" ", 1)[0]
        summary[top] += 1

    lines = [
        "<!-- Generated during: convos/20260604_phase_b_silent_unit_mismatch_sweep.md -->",
        "",
        "# Silent Unit-Mismatch Sweep — WI 2025 wide-pass JSONs vs CPI 2015 oracle",
        "",
        "**Plan:** [`../plans/20260604_silent_unit_mismatch_sweep.md`](../plans/20260604_silent_unit_mismatch_sweep.md)  ",
        "**Convo:** [`../convos/20260604_phase_b_silent_unit_mismatch_sweep.md`](../convos/20260604_phase_b_silent_unit_mismatch_sweep.md)  ",
        "**Script:** [`../../../scripts/silent_unit_mismatch_sweep.py`](../../../../scripts/silent_unit_mismatch_sweep.py)  ",
        "",
        "## Summary",
        "",
        f"Sweep over {len(classifications_sorted)} (compendium row × CPI indicator) pairs, "
        f"derived from 21 CPI-2015-readable rows and 14 CPI indicators (IND_196..IND_209).",
        "",
        "Classification counts (top-level):",
        "",
    ]
    for cat, n in sorted(summary.items(), key=lambda kv: CLASSIFICATION_SORT_KEY.get(kv[0], 99)):
        lines.append(f"- **{cat}** — {n}")
    lines.append("")
    lines.append("Cell emission notation: each `Claude r1/r2/r3` cell shows the emitted value "
                 "for each of the 3 runs; `∅` means not emitted, `FAIL:X` means instantiation "
                 "failed with attempted value `X`.")
    lines.append("")
    lines.append("## Full classification table")
    lines.append("")
    lines.append(
        "| Compendium row | Cell type | Axis | CPI IND | WI oracle | "
        "Claude r1/r2/r3 | GPT r1/r2/r3 | Classification | Notes |"
    )
    lines.append("|---|---|---|---|---|---|---|---|---|")
    for cls in classifications_sorted:
        claude = render_emissions_cell(cls, "claude-opus-4-7")
        gpt = render_emissions_cell(cls, "gpt-5.2-2025-12-11")
        notes = cls.notes.replace("|", "\\|")
        cell_type = cls.cell_type.replace("|", "\\|")
        lines.append(
            f"| `{cls.tsv_row_id}` | {cell_type} | {cls.axis} | {cls.indicator.ind_id} "
            f"| {cls.wi_oracle} | {claude} | {gpt} | {cls.overall_classification} | {notes} |"
        )
    lines.append("")
    return "\n".join(lines)


# ----------------------------------------------------------------------------
# Entry point
# ----------------------------------------------------------------------------


def main() -> None:
    cpi_rows = load_cpi_readable_rows()
    wi_oracle = load_wi_oracle()
    emissions = load_wide_pass_emissions()

    classifications: list[CellClassification] = []
    for indicator in INDICATORS:
        classifications.extend(classify_indicator(indicator, cpi_rows, wi_oracle, emissions))

    output = render_results_doc(classifications)
    RESULTS_DOC.parent.mkdir(parents=True, exist_ok=True)
    RESULTS_DOC.write_text(output)
    print(f"Wrote {RESULTS_DOC}")
    # Brief stdout summary
    summary: dict[str, int] = defaultdict(int)
    for cls in classifications:
        top = cls.overall_classification.split(" ", 1)[0]
        summary[top] += 1
    for cat in sorted(summary.keys(), key=lambda c: CLASSIFICATION_SORT_KEY.get(c, 99)):
        print(f"  {cat}: {summary[cat]}")


if __name__ == "__main__":
    main()
