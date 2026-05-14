"""CPI 2015 C11 (Lobbying Disclosure) projection.

Implements per-item projections for the 14 CPI 2015 C11 indicators
(IND_196 through IND_209) plus an aggregation rule that reproduces the
published per-state Lobbying Disclosure score within +/- 1 across all
50 states.

Spec doc:
``docs/historical/compendium-source-extracts/results/projections/cpi_2015_c11_projection_mapping.md``

Ground-truth files (700-cell per-item + 50-cell category aggregate):

* ``docs/historical/compendium-source-extracts/results/cpi_2015_c11_per_state_scores.csv``
* ``papers/CPI_2015__sii_scores.csv``

The aggregation rule is fitted empirically (CPI's methodology archive
does not document the formula). See
``scripts/fit_cpi_2015_c11_aggregation.py`` for the fit procedure.
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

CPI_2015_C11_INDICATOR_IDS: tuple[str, ...] = tuple(f"IND_{n}" for n in range(196, 210))

_REPO_ROOT = Path(__file__).resolve().parents[3]
_PER_STATE_CSV = (
    _REPO_ROOT
    / "docs"
    / "historical"
    / "compendium-source-extracts"
    / "results"
    / "cpi_2015_c11_per_state_scores.csv"
)


# De jure 3-tier indicators record each cell as YES / MODERATE / NO.
# Six Colorado cells were typed in title case (Yes/No); case-insensitive
# matching handles them. Two cells (Texas IND_199, Massachusetts IND_203)
# carry the literal string "100" -- an Excel transcription artifact. CPI's
# published per-state aggregate is consistent with treating these invalid
# cells as NO (0): empirical fit of the sub-cat-mean aggregation rule
# matches the published C11 score within +/- 0.05 for both states only
# when they are zeroed. See scripts/fit_cpi_2015_c11_aggregation.py for
# the derivation.
_DE_JURE_TIER_TO_SCORE: dict[str, int] = {
    "YES": 100,
    "MODERATE": 50,
    "NO": 0,
}

_DE_JURE_INDICATORS: frozenset[str] = frozenset(
    {"IND_196", "IND_197", "IND_199", "IND_201", "IND_203", "IND_207"}
)


# ---------------------------------------------------------------------------
# Pydantic score model
# ---------------------------------------------------------------------------


class CPI2015C11Score(BaseModel):
    """A CPI 2015 Lobbying Disclosure (C11) score for one state.

    Carries the 14 per-item scores plus the aggregated category score.
    Letter grade is not modeled: CPI 2015 publishes letter grades at
    the overall state level only, not per category.
    """

    model_config = ConfigDict(frozen=True)

    state: str
    per_item_scores: dict[str, int]
    category_score: float


# ---------------------------------------------------------------------------
# Ground-truth loader (700-cell per-state per-item CSV)
# ---------------------------------------------------------------------------


def load_per_state_ground_truth() -> dict[tuple[str, str], int]:
    """Load and normalize the 50-state x 14-item ground-truth CSV.

    Returns a flat ``{(state, indicator_id): score}`` mapping where each
    score is an int in ``{0, 25, 50, 75, 100}``. De jure tiers
    (YES/MODERATE/NO) are mapped to 100/50/0; de facto 5-tier values
    pass through unchanged. Known data-quality glitches (case-mismatched
    Yes/No, numeric strings in de jure columns) are normalized via the
    ``_DE_JURE_TIER_TO_SCORE`` map.
    """
    out: dict[tuple[str, str], int] = {}
    with _PER_STATE_CSV.open() as f:
        for row in csv.DictReader(f):
            ind = row["indicator_id"]
            state = row["state"]
            raw = row["score"].strip()
            if ind in _DE_JURE_INDICATORS:
                # Case-insensitive YES/MODERATE/NO match. Anything else
                # (e.g. the "100" transcription artifact in Texas IND_199
                # and Massachusetts IND_203) is treated as an invalid
                # cell -> NO (0). See _DE_JURE_TIER_TO_SCORE comment.
                score = _DE_JURE_TIER_TO_SCORE.get(raw.upper(), 0)
            else:
                score = int(raw)
            out[(state, ind)] = score
    return out


# ---------------------------------------------------------------------------
# Per-item projections
# ---------------------------------------------------------------------------


def _legal(cells: dict[str, Any], row_id: str) -> Any:
    """Read the legal_availability value of a compendium cell, or None
    if the cell or axis is missing."""
    cell = cells.get(row_id) or {}
    return cell.get("legal_availability")


def _practical(cells: dict[str, Any], row_id: str) -> Any:
    """Read the practical_availability value of a compendium cell, or
    None if the cell or axis is missing."""
    cell = cells.get(row_id) or {}
    return cell.get("practical_availability")


def project_ind_196(cells: dict[str, Any]) -> int:
    """IND_196: definition recognizes executive-branch lobbyists.

    Source quote requires coverage of *both* state legislators *and*
    executive officials (specifically including the governor). 2-tier.
    """
    leg = bool(_legal(cells, "def_target_legislative_branch"))
    gov = bool(_legal(cells, "def_target_governors_office"))
    return 100 if (leg and gov) else 0


def project_ind_197(cells: dict[str, Any]) -> int:
    """IND_197: anyone paid is defined as a lobbyist.

    threshold == 0 -> YES; threshold > 0 -> MODERATE; no statute -> NO.
    """
    threshold = _legal(cells, "compensation_threshold_for_lobbyist_registration")
    if threshold is None:
        return 0
    if threshold == 0:
        return 100
    return 50


def project_ind_198(cells: dict[str, Any]) -> int:
    """IND_198: all paid lobbyists register in practice. 5-tier passthrough."""
    return int(_practical(cells, "lobbyist_registration_required") or 0)


def project_ind_199(cells: dict[str, Any]) -> int:
    """IND_199: registration form filed at least annually in law. 3-tier enum.

    annual (or more frequent) -> YES; biennial / less_frequent -> MODERATE;
    no registration required -> NO.
    """
    cadence = _legal(cells, "lobbyist_registration_renewal_cadence")
    if cadence in ("annual", "more_frequent_than_annual"):
        return 100
    if cadence in ("biennial", "less_frequent_than_biennial"):
        return 50
    return 0


def project_ind_200(cells: dict[str, Any]) -> int:
    """IND_200: registration filed within days of first lobbying. 5-tier passthrough."""
    return int(
        _practical(cells, "registration_timeliness_after_first_lobbying_activity") or 0
    )


def project_ind_201(cells: dict[str, Any]) -> int:
    """IND_201: itemized lobbyist spending reports including compensation.

    Compound de jure 3-tier:
    * report_required AND itemized AND includes_compensation -> 100
    * report_required AND (itemized XOR includes_compensation) -> 50
    * else -> 0
    """
    required = bool(_legal(cells, "lobbyist_spending_report_required"))
    if not required:
        return 0
    itemized = bool(_legal(cells, "lobbyist_spending_report_includes_itemized_expenses"))
    compensation = bool(_legal(cells, "lobbyist_spending_report_includes_compensation"))
    if itemized and compensation:
        return 100
    if itemized or compensation:
        return 50
    return 0


def project_ind_202(cells: dict[str, Any]) -> int:
    """IND_202: filing cadence of lobbyist spending reports. 5-tier passthrough."""
    return int(_practical(cells, "lobbyist_spending_report_filing_cadence") or 0)


def project_ind_203(cells: dict[str, Any]) -> int:
    """IND_203: principal/employer spending reports including compensation.

    Compound de jure 3-tier:
    * principal_report_required AND includes_compensation -> 100
    * principal_report_required AND NOT includes_compensation -> 50
    * NOT principal_report_required -> 0
    """
    required = bool(_legal(cells, "principal_spending_report_required"))
    if not required:
        return 0
    comp = bool(
        _legal(
            cells,
            "principal_spending_report_includes_compensation_paid_to_lobbyists",
        )
    )
    return 100 if comp else 50


def project_ind_204(cells: dict[str, Any]) -> int:
    """IND_204: principals list lobbyist compensation in practice. Passthrough."""
    return int(
        _practical(
            cells,
            "principal_spending_report_includes_compensation_paid_to_lobbyists",
        )
        or 0
    )


def project_ind_205(cells: dict[str, Any]) -> int:
    """IND_205: citizens access disclosure documents within a reasonable time at no cost.

    Compound de facto. Published anchors:
    * online AND free OR offline obtainable within 7 days -> 100
    * offline 2-week request with visit or fee -> 50
    * offline > a month or prohibitive or unobtainable -> 0
    * 25 / 75 are scorer-judgment partial credit; carried on the
      ``__ind_205_partial_credit_passthrough`` key for round-trip.
    """
    partial = _practical(cells, "__ind_205_partial_credit_passthrough")
    if partial in (25, 75):
        return int(partial)
    online = bool(_practical(cells, "lobbying_disclosure_documents_online"))
    free = bool(_practical(cells, "lobbying_disclosure_documents_free_to_access"))
    days_raw = _practical(cells, "lobbying_disclosure_offline_request_response_time_days")
    days = int(days_raw) if days_raw is not None else None
    if online and free:
        return 100
    if days is not None and days <= 7:
        return 100
    if days is not None and days <= 14:
        return 50
    return 0


def project_ind_206(cells: dict[str, Any]) -> int:
    """IND_206: open data format quality. 5-tier passthrough."""
    return int(_practical(cells, "lobbying_data_open_data_quality") or 0)


def project_ind_207(cells: dict[str, Any]) -> int:
    """IND_207: regular auditing of lobbying disclosure records in law. 3-tier enum."""
    rule = _legal(cells, "lobbying_disclosure_audit_required_in_law")
    if rule == "regular_third_party_audit_required":
        return 100
    if rule == "audit_only_when_irregularities_suspected_or_compliance_review":
        return 50
    return 0


def project_ind_208(cells: dict[str, Any]) -> int:
    """IND_208: lobbying disclosures actually audited. 5-tier passthrough."""
    return int(_practical(cells, "lobbying_disclosure_audit_required_in_law") or 0)


def project_ind_209(cells: dict[str, Any]) -> int:
    """IND_209: penalties imposed for reporting violations. 5-tier passthrough."""
    return int(
        _practical(cells, "lobbying_violation_penalties_imposed_in_practice") or 0
    )


_PER_ITEM_HELPERS = {
    "IND_196": project_ind_196,
    "IND_197": project_ind_197,
    "IND_198": project_ind_198,
    "IND_199": project_ind_199,
    "IND_200": project_ind_200,
    "IND_201": project_ind_201,
    "IND_202": project_ind_202,
    "IND_203": project_ind_203,
    "IND_204": project_ind_204,
    "IND_205": project_ind_205,
    "IND_206": project_ind_206,
    "IND_207": project_ind_207,
    "IND_208": project_ind_208,
    "IND_209": project_ind_209,
}


# ---------------------------------------------------------------------------
# Aggregation
# ---------------------------------------------------------------------------


# CPI 2015 C11 sub-category structure, extracted from
# ``papers/CPI_2015__sii_criteria.xlsx`` sheet11 column A. The 14
# indicators group into 5 sub-categories with counts 2/4/3/2/3:
#
# * 11.1 Is there a clear definition of a lobbyist?
# * 11.2 Are lobbyist registration processes effective?
# * 11.3 Are there detailed registration requirements?
# * 11.4 Can citizens access the information reported by lobbyists?
# * 11.5 Is there effective monitoring of lobbying disclosure requirements?
CPI_2015_C11_SUB_CATEGORIES: dict[str, tuple[str, ...]] = {
    "11_1": ("IND_196", "IND_197"),
    "11_2": ("IND_198", "IND_200", "IND_202", "IND_204"),
    "11_3": ("IND_199", "IND_201", "IND_203"),
    "11_4": ("IND_205", "IND_206"),
    "11_5": ("IND_207", "IND_208", "IND_209"),
}


def aggregate_cpi_2015_c11(per_item: dict[str, int]) -> float:
    """Aggregate 14 per-item integer scores to a category score in [0, 100].

    The aggregation rule is the unweighted mean of the 5 sub-category
    means. Fitted empirically against CPI's published 50-state Lobbying
    Disclosure scores; max abs residual is 0.05 across all 50 states
    (1-decimal rounding artifact), well inside the spec's +/- 1
    tolerance. Counts 2/4/3/2/3 across the sub-categories give de jure
    items implicit higher per-item weight than a flat mean would.
    """
    missing = [ind for ind in CPI_2015_C11_INDICATOR_IDS if ind not in per_item]
    if missing:
        raise ValueError(f"missing per-item scores: {missing}")
    sub_cat_means = [
        sum(per_item[ind] for ind in items) / len(items)
        for items in CPI_2015_C11_SUB_CATEGORIES.values()
    ]
    return sum(sub_cat_means) / len(sub_cat_means)


def project_cpi_2015_c11(cells: dict[str, Any], state: str) -> CPI2015C11Score:
    """Top-level projection: cells -> per-item tiers -> aggregated C11 score."""
    per_item = {ind: helper(cells) for ind, helper in _PER_ITEM_HELPERS.items()}
    return CPI2015C11Score(
        state=state,
        per_item_scores=per_item,
        category_score=aggregate_cpi_2015_c11(per_item),
    )


def rank_states_by_category_score(scores: dict[str, float]) -> dict[str, int]:
    """Return a {state: rank} mapping where higher score -> lower rank.

    Uses competition ranking (1224 style): tied states share the same
    rank and the next rank skips the corresponding count, matching CPI
    2015's published per-category rank column. Within a tie, all
    members get the rank of the highest position in the tie group.
    """
    # Round to one decimal: CPI publishes scores to 1 dp, and ties are
    # defined at that precision. Floating-point quirks (e.g.
    # 58.333... vs 58.4) would otherwise miscount ties.
    ordered = sorted(scores.items(), key=lambda kv: -round(kv[1], 1))
    out: dict[str, int] = {}
    prev_rounded: float | None = None
    prev_rank = 0
    for i, (state, score) in enumerate(ordered, start=1):
        rounded = round(score, 1)
        if prev_rounded is None or rounded != prev_rounded:
            prev_rank = i
            prev_rounded = rounded
        out[state] = prev_rank
    return out
