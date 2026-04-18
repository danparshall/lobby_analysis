"""Audit + eligibility logic for Justia statute retrieval.

Phase 1 scope: year-availability audit across 50 states; pick closest year to
a target vintage within a ±N year tolerance; report eligibility for calibration
(2010-anchored) and for 2026-scoring.

Per-state chapter-level availability and full statute-text retrieval belong to
Phase 2 and are out of scope here.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Literal

from scoring.justia_client import Client, parse_state_year_index

# Footnote 80 of Clemens et al. (PRI 2010): the 34 states that responded to
# PRI's review email (31 with confirmations/corrections, 3 declined-for-time).
# These are higher-trust ground truth than the 16 non-responders.
PRI_RESPONDER_STATES: set[str] = {
    "WA", "RI", "SD", "NV", "KS", "AL", "ME", "MN", "AK", "DE",
    "CA", "OR", "VT", "HI", "IN", "LA", "NE", "CO", "SC", "MT",
    "WI", "TX", "NM", "NJ", "OH", "NY", "CT", "MD", "KY", "WY",
    "NH", "AZ", "WV", "VA",
}


# USPS → Justia slug. Justia uses lowercase hyphen-separated state names in URLs.
USPS_TO_JUSTIA_SLUG: dict[str, str] = {
    "AL": "alabama", "AK": "alaska", "AZ": "arizona", "AR": "arkansas",
    "CA": "california", "CO": "colorado", "CT": "connecticut", "DE": "delaware",
    "FL": "florida", "GA": "georgia", "HI": "hawaii", "ID": "idaho",
    "IL": "illinois", "IN": "indiana", "IA": "iowa", "KS": "kansas",
    "KY": "kentucky", "LA": "louisiana", "ME": "maine", "MD": "maryland",
    "MA": "massachusetts", "MI": "michigan", "MN": "minnesota", "MS": "mississippi",
    "MO": "missouri", "MT": "montana", "NE": "nebraska", "NV": "nevada",
    "NH": "new-hampshire", "NJ": "new-jersey", "NM": "new-mexico", "NY": "new-york",
    "NC": "north-carolina", "ND": "north-dakota", "OH": "ohio", "OK": "oklahoma",
    "OR": "oregon", "PA": "pennsylvania", "RI": "rhode-island", "SC": "south-carolina",
    "SD": "south-dakota", "TN": "tennessee", "TX": "texas", "UT": "utah",
    "VT": "vermont", "VA": "virginia", "WA": "washington", "WV": "west-virginia",
    "WI": "wisconsin", "WY": "wyoming",
}


Direction = Literal["exact", "pre", "post", "none"]


@dataclass(frozen=True)
class StateAudit:
    state_abbr: str
    target_year: int
    available_years: list[int]
    chosen_year: int | None
    year_delta: int | None
    direction: Direction
    current_year: int
    eligible_for_calibration: bool
    eligible_for_2026_scoring: bool
    pri_state_reviewed: bool


def pick_year_within_tolerance(
    years: list[int],
    target: int,
    tolerance: int,
) -> tuple[int, int, Direction] | None:
    """Pick the best year within ±tolerance of target.

    Tie-break rule: if two years are equidistant, prefer the pre-target year
    (direction="pre") because PRI scored late-2009 law — a pre-2010 vintage
    may miss late-2009 changes but a post-2010 vintage may include reforms
    PRI never saw.

    Returns (chosen_year, year_delta, direction) or None if no candidate
    within tolerance. Direction is "exact" (delta=0), "pre" (delta<0), or
    "post" (delta>0).
    """
    candidates = [y for y in years if abs(y - target) <= tolerance]
    if not candidates:
        return None
    # Sort key: (distance, direction_priority) — closer first, pre preferred.
    def _key(y: int) -> tuple[int, int]:
        dist = abs(y - target)
        direction_priority = 0 if y <= target else 1
        return (dist, direction_priority)

    chosen = min(candidates, key=_key)
    delta = chosen - target
    if delta == 0:
        direction: Direction = "exact"
    elif delta < 0:
        direction = "pre"
    else:
        direction = "post"
    return chosen, delta, direction


def _state_index_url(state_abbr: str) -> str:
    slug = USPS_TO_JUSTIA_SLUG[state_abbr]
    return f"https://law.justia.com/codes/{slug}/"


def audit_state(
    client: Client,
    state_abbr: str,
    target_year: int = 2010,
    tolerance: int = 2,
) -> StateAudit:
    """Audit a single state's Justia coverage.

    Fetches the state's year-index page, determines calibration + 2026-scoring
    eligibility by year availability. Does NOT verify chapter-level content
    (deferred to Phase 2 retrieval).
    """
    url = _state_index_url(state_abbr)
    html = client.fetch_page(url)
    years = parse_state_year_index(html)

    picked = pick_year_within_tolerance(years, target_year, tolerance) if years else None
    if picked is None:
        chosen_year: int | None = None
        year_delta: int | None = None
        direction: Direction = "none"
    else:
        chosen_year, year_delta, direction = picked

    current_year = max(years) if years else 0
    eligible_for_calibration = chosen_year is not None
    eligible_for_2026_scoring = current_year > 0

    return StateAudit(
        state_abbr=state_abbr,
        target_year=target_year,
        available_years=years,
        chosen_year=chosen_year,
        year_delta=year_delta,
        direction=direction,
        current_year=current_year,
        eligible_for_calibration=eligible_for_calibration,
        eligible_for_2026_scoring=eligible_for_2026_scoring,
        pri_state_reviewed=state_abbr in PRI_RESPONDER_STATES,
    )


CSV_HEADERS = [
    "state_abbr",
    "target_year",
    "chosen_year",
    "year_delta",
    "direction",
    "current_year",
    "eligible_for_calibration",
    "eligible_for_2026_scoring",
    "pri_state_reviewed",
    "n_available_years",
    "min_available_year",
    "max_available_year",
]


def run_audit_to_csv(
    client: Client,
    states: Iterable[str],
    target_year: int,
    tolerance: int,
    out_path: Path,
) -> list[StateAudit]:
    """Run `audit_state` for each state, write one row per state to out_path.

    Returns the list of StateAudit results for in-memory analysis.
    """
    out_path.parent.mkdir(parents=True, exist_ok=True)
    results: list[StateAudit] = []
    with out_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
        writer.writeheader()
        for state_abbr in states:
            print(f"auditing {state_abbr} ...")
            try:
                audit = audit_state(client, state_abbr, target_year, tolerance)
            except Exception as e:
                print(f"  !! {state_abbr} failed: {type(e).__name__}: {e}")
                continue
            writer.writerow(_audit_to_row(audit))
            results.append(audit)
    return results


def _audit_to_row(audit: StateAudit) -> dict[str, str]:
    return {
        "state_abbr": audit.state_abbr,
        "target_year": str(audit.target_year),
        "chosen_year": "" if audit.chosen_year is None else str(audit.chosen_year),
        "year_delta": "" if audit.year_delta is None else str(audit.year_delta),
        "direction": audit.direction,
        "current_year": str(audit.current_year),
        "eligible_for_calibration": str(audit.eligible_for_calibration),
        "eligible_for_2026_scoring": str(audit.eligible_for_2026_scoring),
        "pri_state_reviewed": str(audit.pri_state_reviewed),
        "n_available_years": str(len(audit.available_years)),
        "min_available_year": (
            str(min(audit.available_years)) if audit.available_years else ""
        ),
        "max_available_year": (
            str(max(audit.available_years)) if audit.available_years else ""
        ),
    }
