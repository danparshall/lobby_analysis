"""PRI calibration harness: sub-aggregate rollups, reference-score loader, agreement metrics.

The rollup rules are specified in
`docs/active/pri-calibration/results/20260419_pri_rollup_rule_spec.md` and every
implementation choice here traces to a cited line range in PRI (2010).
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Union

from pydantic import BaseModel


# ---------------------------------------------------------------------------
# Sub-aggregate models
# ---------------------------------------------------------------------------


class DisclosureSubAggregates(BaseModel):
    A_registration: Optional[int]
    B_gov_exemptions: Optional[int]
    C_public_entity_def: Optional[int]
    D_materiality: Optional[int]
    E_info_disclosed: Optional[int]
    total: Optional[int]


class AccessibilitySubAggregates(BaseModel):
    Q1: Optional[int]
    Q2: Optional[int]
    Q3: Optional[int]
    Q4: Optional[int]
    Q5: Optional[int]
    Q6: Optional[int]
    Q7_raw: Optional[int]
    Q8_normalized: Optional[float]
    total: Optional[float]


SubAggregates = Union[DisclosureSubAggregates, AccessibilitySubAggregates]


# ---------------------------------------------------------------------------
# Rollup: disclosure law
# ---------------------------------------------------------------------------


def _ints_or_none(scores: dict[str, object], keys: list[str]) -> Optional[list[int]]:
    """Return [int(scores[k]) for k in keys], or None if any key is missing/None/non-numeric."""
    out: list[int] = []
    for k in keys:
        v = scores.get(k)
        if v is None:
            return None
        try:
            out.append(int(v))
        except (TypeError, ValueError):
            return None
    return out


def _rollup_A(scores: dict[str, object]) -> Optional[int]:
    vals = _ints_or_none(scores, [f"A{i}" for i in range(1, 12)])
    return None if vals is None else sum(vals)


def _rollup_B(scores: dict[str, object]) -> Optional[int]:
    vals = _ints_or_none(scores, ["B1", "B2", "B3", "B4"])
    if vals is None:
        return None
    b1, b2, b3, b4 = vals
    return (1 - b1) + (1 - b2) + b3 + b4


def _rollup_C(scores: dict[str, object]) -> Optional[int]:
    vals = _ints_or_none(scores, ["C0"])
    return None if vals is None else vals[0]


def _rollup_D(scores: dict[str, object]) -> Optional[int]:
    vals = _ints_or_none(scores, ["D0"])
    return None if vals is None else vals[0]


def _rollup_E(scores: dict[str, object]) -> Optional[int]:
    """PRI E rollup: max(base_E1, base_E2) + fg_E1 + fg_E2 + E1j.

    base(side)  = a + b + c + d + e + h_collapsed(side) + i
    h_collapsed = 1 if any of (h_i, h_ii, h_iii) == 1 else 0
    fg(side)    = (f_i + f_ii + f_iii + f_iv) + (g_i + g_ii)

    Null propagation: if any integer item needed for any of the above is None/missing,
    the entire E sub-aggregate is None (we cannot know whether the null would have
    changed the max-of-base or added to fg).
    """
    base_keys_per_side = ["a", "b", "c", "d", "e", "i"]
    h_keys_per_side = ["h_i", "h_ii", "h_iii"]
    fg_keys_per_side = ["f_i", "f_ii", "f_iii", "f_iv", "g_i", "g_ii"]

    def _side(prefix: str) -> Optional[tuple[int, int]]:
        base_vals = _ints_or_none(scores, [f"{prefix}{k}" for k in base_keys_per_side])
        if base_vals is None:
            return None
        h_vals = _ints_or_none(scores, [f"{prefix}{k}" for k in h_keys_per_side])
        if h_vals is None:
            return None
        h_collapsed = 1 if any(h_vals) else 0
        base = sum(base_vals) + h_collapsed
        fg_vals = _ints_or_none(scores, [f"{prefix}{k}" for k in fg_keys_per_side])
        if fg_vals is None:
            return None
        return base, sum(fg_vals)

    e1 = _side("E1")
    if e1 is None:
        return None
    e2 = _side("E2")
    if e2 is None:
        return None
    j = _ints_or_none(scores, ["E1j"])
    if j is None:
        return None
    base_e1, fg_e1 = e1
    base_e2, fg_e2 = e2
    return max(base_e1, base_e2) + fg_e1 + fg_e2 + j[0]


def rollup_disclosure_law(scores: dict[str, object]) -> DisclosureSubAggregates:
    a = _rollup_A(scores)
    b = _rollup_B(scores)
    c = _rollup_C(scores)
    d = _rollup_D(scores)
    e = _rollup_E(scores)
    parts = [a, b, c, d, e]
    total = None if any(p is None for p in parts) else sum(parts)  # type: ignore[arg-type]
    return DisclosureSubAggregates(
        A_registration=a,
        B_gov_exemptions=b,
        C_public_entity_def=c,
        D_materiality=d,
        E_info_disclosed=e,
        total=total,
    )


# ---------------------------------------------------------------------------
# Rollup: accessibility
# ---------------------------------------------------------------------------


def rollup_accessibility(scores: dict[str, object]) -> AccessibilitySubAggregates:
    q1_6 = _ints_or_none(scores, ["Q1", "Q2", "Q3", "Q4", "Q5", "Q6"])
    q7_keys = [f"Q7{ch}" for ch in "abcdefghijklmno"]
    q7_vals = _ints_or_none(scores, q7_keys)
    q7_raw = None if q7_vals is None else sum(q7_vals)

    q8_raw_raw = scores.get("Q8")
    if q8_raw_raw is None:
        q8_normalized: Optional[float] = None
    else:
        try:
            q8_normalized = float(q8_raw_raw) / 15.0
        except (TypeError, ValueError):
            q8_normalized = None

    q1, q2, q3, q4, q5, q6 = (None, None, None, None, None, None) if q1_6 is None else tuple(q1_6)

    parts: list[Optional[float]] = [q1, q2, q3, q4, q5, q6, q7_raw, q8_normalized]
    total: Optional[float]
    if any(p is None for p in parts):
        total = None
    else:
        total = float(sum(parts))  # type: ignore[arg-type]

    return AccessibilitySubAggregates(
        Q1=q1, Q2=q2, Q3=q3, Q4=q4, Q5=q5, Q6=q6,
        Q7_raw=q7_raw,
        Q8_normalized=q8_normalized,
        total=total,
    )


# ---------------------------------------------------------------------------
# PRI reference-score loader
# ---------------------------------------------------------------------------


PRI_RUBRIC_NAMES = {"pri_disclosure_law", "pri_accessibility"}


STATE_NAME_TO_USPS: dict[str, str] = {
    "Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR",
    "California": "CA", "Colorado": "CO", "Connecticut": "CT", "Delaware": "DE",
    "Florida": "FL", "Georgia": "GA", "Hawaii": "HI", "Idaho": "ID",
    "Illinois": "IL", "Indiana": "IN", "Iowa": "IA", "Kansas": "KS",
    "Kentucky": "KY", "Louisiana": "LA", "Maine": "ME", "Maryland": "MD",
    "Massachusetts": "MA", "Michigan": "MI", "Minnesota": "MN", "Mississippi": "MS",
    "Missouri": "MO", "Montana": "MT", "Nebraska": "NE", "Nevada": "NV",
    "New Hampshire": "NH", "New Jersey": "NJ", "New Mexico": "NM", "New York": "NY",
    "North Carolina": "NC", "North Dakota": "ND", "Ohio": "OH", "Oklahoma": "OK",
    "Oregon": "OR", "Pennsylvania": "PA", "Rhode Island": "RI", "South Carolina": "SC",
    "South Dakota": "SD", "Tennessee": "TN", "Texas": "TX", "Utah": "UT",
    "Vermont": "VT", "Virginia": "VA", "Washington": "WA", "West Virginia": "WV",
    "Wisconsin": "WI", "Wyoming": "WY",
}


def _disclosure_scores_path(repo_root: Path) -> Path:
    return repo_root / "docs" / "active" / "pri-2026-rescore" / "results" / "pri_2010_disclosure_law_scores.csv"


def _accessibility_scores_path(repo_root: Path) -> Path:
    return repo_root / "docs" / "active" / "pri-2026-rescore" / "results" / "pri_2010_accessibility_scores.csv"


def load_pri_reference_scores(
    rubric: str, repo_root: Path
) -> dict[str, SubAggregates]:
    """Load PRI 2010 published per-state sub-aggregate scores as a USPS-keyed dict.

    Args:
        rubric: "pri_disclosure_law" or "pri_accessibility".
        repo_root: repo root (needed to resolve the CSV path).

    Returns:
        dict mapping USPS state code to the appropriate sub-aggregate model.
    """
    if rubric not in PRI_RUBRIC_NAMES:
        raise ValueError(f"unknown PRI rubric {rubric!r}; valid: {sorted(PRI_RUBRIC_NAMES)}")

    if rubric == "pri_disclosure_law":
        return _load_disclosure_reference(_disclosure_scores_path(repo_root))
    return _load_accessibility_reference(_accessibility_scores_path(repo_root))


def _load_disclosure_reference(path: Path) -> dict[str, SubAggregates]:
    out: dict[str, SubAggregates] = {}
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["state"]
            if name not in STATE_NAME_TO_USPS:
                raise ValueError(f"unknown state name in {path}: {name!r}")
            out[STATE_NAME_TO_USPS[name]] = DisclosureSubAggregates(
                A_registration=int(row["A_registration"]),
                B_gov_exemptions=int(row["B_gov_exemptions"]),
                C_public_entity_def=int(row["C_public_entity_def"]),
                D_materiality=int(row["D_materiality"]),
                E_info_disclosed=int(row["E_info_disclosed"]),
                total=int(row["total_2010"]),
            )
    return out


def _load_accessibility_reference(path: Path) -> dict[str, SubAggregates]:
    out: dict[str, SubAggregates] = {}
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["state"]
            if name not in STATE_NAME_TO_USPS:
                raise ValueError(f"unknown state name in {path}: {name!r}")
            out[STATE_NAME_TO_USPS[name]] = AccessibilitySubAggregates(
                Q1=int(row["Q1"]),
                Q2=int(row["Q2"]),
                Q3=int(row["Q3"]),
                Q4=int(row["Q4"]),
                Q5=int(row["Q5"]),
                Q6=int(row["Q6"]),
                Q7_raw=int(float(row["Q7_raw"])),
                Q8_normalized=float(row["Q8_normalized"]),
                total=float(row["total_2010"]),
            )
    return out


# ---------------------------------------------------------------------------
# Agreement metrics
# ---------------------------------------------------------------------------


# Tolerance for float sub-aggregate comparisons. PRI publishes Q8_normalized and
# total at 1dp; our computed values can differ by up to ~0.07 on Q8 alone (e.g.,
# 5/15 = 0.333 vs PRI's 0.3). We use a slightly-larger tolerance for total to
# account for cumulative 1dp rounding in PRI's published sum.
_Q8_TOLERANCE = 0.07
_TOTAL_ACCESSIBILITY_TOLERANCE = 0.11


DISCLOSURE_SUB_COMPONENTS = (
    "A_registration", "B_gov_exemptions", "C_public_entity_def",
    "D_materiality", "E_info_disclosed",
)
ACCESSIBILITY_SUB_COMPONENTS = (
    "Q1", "Q2", "Q3", "Q4", "Q5", "Q6", "Q7_raw", "Q8_normalized",
)


def _sub_components_for(rubric: str) -> tuple[str, ...]:
    if rubric == "pri_disclosure_law":
        return DISCLOSURE_SUB_COMPONENTS
    if rubric == "pri_accessibility":
        return ACCESSIBILITY_SUB_COMPONENTS
    raise ValueError(f"unknown PRI rubric {rubric!r}")


def _match(ours: object, pri: object, sub_component: str) -> bool:
    if ours is None or pri is None:
        return False
    if sub_component == "Q8_normalized":
        return abs(float(ours) - float(pri)) < _Q8_TOLERANCE  # type: ignore[arg-type]
    return ours == pri


def _total_match(ours: SubAggregates, pri: SubAggregates, rubric: str) -> bool:
    if ours.total is None or pri.total is None:
        return False
    if rubric == "pri_accessibility":
        return abs(float(ours.total) - float(pri.total)) < _TOTAL_ACCESSIBILITY_TOLERANCE
    return ours.total == pri.total


@dataclass
class StateAgreement:
    state: str
    ours: SubAggregates
    pri: SubAggregates
    per_sub_component: dict[str, bool]
    total_match: bool


@dataclass
class PartitionAgreement:
    states: list[str]
    per_sub_component_agreement_rate: dict[str, float]
    total_agreement_rate: float


@dataclass
class OverallAgreement:
    all: PartitionAgreement
    in_partition: Optional[PartitionAgreement] = None
    out_of_partition: Optional[PartitionAgreement] = None


@dataclass
class AgreementReport:
    rubric: str
    per_state: dict[str, StateAgreement]
    overall: OverallAgreement
    trust_partition_label: Optional[str] = None


def _rollup_for(rubric: str, atomic: dict[str, object]) -> SubAggregates:
    if rubric == "pri_disclosure_law":
        return rollup_disclosure_law(atomic)
    if rubric == "pri_accessibility":
        return rollup_accessibility(atomic)
    raise ValueError(f"unknown PRI rubric {rubric!r}")


def _summarize(
    rubric: str,
    per_state: dict[str, StateAgreement],
    states: list[str],
) -> PartitionAgreement:
    if not states:
        return PartitionAgreement(
            states=states,
            per_sub_component_agreement_rate={sc: 0.0 for sc in _sub_components_for(rubric)},
            total_agreement_rate=0.0,
        )
    sub_components = _sub_components_for(rubric)
    rates: dict[str, float] = {}
    for sc in sub_components:
        matches = sum(1 for s in states if per_state[s].per_sub_component[sc])
        rates[sc] = matches / len(states)
    total_rate = sum(1 for s in states if per_state[s].total_match) / len(states)
    return PartitionAgreement(
        states=states,
        per_sub_component_agreement_rate=rates,
        total_agreement_rate=total_rate,
    )


def load_atomic_scores_from_csv(csv_path: Path) -> dict[str, object]:
    """Read a scored CSV (from the finalize step) and return {item_id → score | None}.

    A row with unable_to_evaluate=true is parsed as score=None. Otherwise the score
    column is parsed as int where possible, falling back to float, falling back to
    the raw string (for text-typed items like E1h_vi).
    """
    atomic: dict[str, object] = {}
    with csv_path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            item_id = row["item_id"]
            if row.get("unable_to_evaluate", "").lower() == "true":
                atomic[item_id] = None
                continue
            raw = row.get("score", "")
            if raw == "" or raw is None:
                atomic[item_id] = None
                continue
            try:
                atomic[item_id] = int(raw)
                continue
            except (TypeError, ValueError):
                pass
            try:
                atomic[item_id] = float(raw)
            except (TypeError, ValueError):
                atomic[item_id] = raw
    return atomic


def render_agreement_markdown(report: AgreementReport) -> str:
    """Render an AgreementReport as a human-readable markdown document."""
    lines: list[str] = []
    lines.append(f"# Calibration report — {report.rubric}")
    lines.append("")
    lines.append(f"States scored: {len(report.per_state)}")
    lines.append("")

    # Overall summary
    lines.append("## Overall")
    lines.append("")
    lines.append(_render_partition("All states", report.overall.all))

    if report.overall.in_partition is not None and report.overall.out_of_partition is not None:
        label = report.trust_partition_label or "partition"
        lines.append("")
        lines.append(f"## Partition: {label}")
        lines.append("")
        lines.append(_render_partition(f"In partition ({label})", report.overall.in_partition))
        lines.append("")
        lines.append(_render_partition("Out of partition", report.overall.out_of_partition))

    # Per-state detail
    lines.append("")
    lines.append("## Per-state detail")
    lines.append("")
    sub_components = _sub_components_for(report.rubric)
    header_cols = ["state", *sub_components, "total"]
    lines.append("| " + " | ".join(header_cols) + " |")
    lines.append("|" + "|".join(["---"] * len(header_cols)) + "|")
    for state in sorted(report.per_state):
        sa = report.per_state[state]
        cells: list[str] = [state]
        for sc in sub_components:
            ours_v = getattr(sa.ours, sc)
            pri_v = getattr(sa.pri, sc)
            matched = sa.per_sub_component[sc]
            mark = "✓" if matched else "✗"
            cells.append(f"{_fmt(ours_v)} / {_fmt(pri_v)} {mark}")
        total_mark = "✓" if sa.total_match else "✗"
        cells.append(f"{_fmt(sa.ours.total)} / {_fmt(sa.pri.total)} {total_mark}")
        lines.append("| " + " | ".join(cells) + " |")

    return "\n".join(lines) + "\n"


def _render_partition(label: str, partition: PartitionAgreement) -> str:
    if not partition.states:
        return f"**{label}:** (no states)"
    lines = [
        f"**{label}** — {len(partition.states)} states: "
        f"{', '.join(partition.states)}",
        "",
        f"- total agreement rate: {_pct(partition.total_agreement_rate)}",
    ]
    for sc, rate in partition.per_sub_component_agreement_rate.items():
        lines.append(f"- {sc}: {_pct(rate)}")
    return "\n".join(lines)


def _pct(x: float) -> str:
    return f"{x * 100:.1f}%"


def _fmt(v: object) -> str:
    if v is None:
        return "null"
    if isinstance(v, float):
        return f"{v:.2f}"
    return str(v)


def compute_agreement(
    ours_atomic_by_state: dict[str, dict[str, object]],
    pri_by_state: dict[str, SubAggregates],
    rubric: str,
    trust_partition: Optional[set[str]] = None,
    trust_partition_label: Optional[str] = None,
) -> AgreementReport:
    """Compare LLM-produced atomic scores against PRI published sub-aggregates.

    Args:
        ours_atomic_by_state: USPS → atomic item-id → numeric score (or None).
        pri_by_state: USPS → PRI sub-aggregates (loaded via load_pri_reference_scores).
        rubric: "pri_disclosure_law" or "pri_accessibility".
        trust_partition: optional set of USPS codes (e.g. PRI_RESPONDER_STATES).
            If provided, the overall summary exposes in/out partition breakdowns.
        trust_partition_label: optional label for reports (e.g. "PRI responders").

    Returns:
        AgreementReport with per-state and overall (+ optional partition) summaries.
    """
    if rubric not in PRI_RUBRIC_NAMES:
        raise ValueError(f"unknown PRI rubric {rubric!r}")

    sub_components = _sub_components_for(rubric)
    per_state: dict[str, StateAgreement] = {}
    states_in_both = sorted(set(ours_atomic_by_state) & set(pri_by_state))
    for s in states_in_both:
        ours = _rollup_for(rubric, ours_atomic_by_state[s])
        pri = pri_by_state[s]
        matches = {
            sc: _match(getattr(ours, sc), getattr(pri, sc), sc) for sc in sub_components
        }
        per_state[s] = StateAgreement(
            state=s,
            ours=ours,
            pri=pri,
            per_sub_component=matches,
            total_match=_total_match(ours, pri, rubric),
        )

    overall_all = _summarize(rubric, per_state, states_in_both)
    in_part = out_part = None
    if trust_partition is not None:
        in_states = [s for s in states_in_both if s in trust_partition]
        out_states = [s for s in states_in_both if s not in trust_partition]
        in_part = _summarize(rubric, per_state, in_states)
        out_part = _summarize(rubric, per_state, out_states)

    return AgreementReport(
        rubric=rubric,
        per_state=per_state,
        overall=OverallAgreement(all=overall_all, in_partition=in_part, out_of_partition=out_part),
        trust_partition_label=trust_partition_label,
    )
