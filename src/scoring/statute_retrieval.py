"""Audit + eligibility logic for Justia statute retrieval.

Phase 1 scope: year-availability audit across 50 states; pick closest year to
a target vintage within a ±N year tolerance; report eligibility for calibration
(2010-anchored) and for 2026-scoring.

Per-state chapter-level availability and full statute-text retrieval belong to
Phase 2 and are out of scope here.
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Literal

from scoring.justia_client import Client, parse_state_year_index, parse_statute_text

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


_JUSTIA_CODES_URL_RE = re.compile(
    r"^https?://law\.justia\.com/codes/[a-z-]+/\d{4}/(.+)$"
)


def _direction_from_delta(delta: int) -> Literal["exact", "pre", "post"]:
    if delta == 0:
        return "exact"
    return "pre" if delta < 0 else "post"


def retrieve_bundles_for_states(
    client: Client,
    *,
    targets: list[tuple[str, int]],
    dest_root: Path,
    target_year: int = 2010,
) -> list[Path]:
    """Retrieve statute bundles for each (state_abbr, vintage_year) pair in targets.

    Looks up URLs in `lobbying_statute_urls.LOBBYING_STATUTE_URLS`, derives
    direction/year_delta from `vintage_year - target_year`, and writes each
    bundle to `dest_root/<STATE>/<YEAR>/`. Returns the list of manifest paths.

    Raises KeyError if no URLs are curated for a requested (state, vintage) pair.
    """
    from scoring.lobbying_statute_urls import LOBBYING_STATUTE_URLS

    manifest_paths: list[Path] = []
    for state_abbr, vintage_year in targets:
        urls = LOBBYING_STATUTE_URLS.get((state_abbr, vintage_year))
        if not urls:
            raise KeyError(
                f"no curated lobby-statute URLs for ({state_abbr}, {vintage_year})"
            )
        delta = vintage_year - target_year
        bundle_dir = dest_root / state_abbr / str(vintage_year)
        manifest_path = retrieve_statute_bundle(
            client,
            state_abbr=state_abbr,
            vintage_year=vintage_year,
            urls=urls,
            dest_dir=bundle_dir,
            year_delta=delta,
            direction=_direction_from_delta(delta),
            pri_state_reviewed=state_abbr in PRI_RESPONDER_STATES,
        )
        manifest_paths.append(manifest_path)
    return manifest_paths


def _filename_from_url(url: str) -> str:
    """Derive a sections/*.txt filename from a Justia statute URL.

    Strategy: take the path segments after `/codes/STATE/YEAR/`, strip trailing
    `/` and `.html`, flatten remaining `/` into `-`, append `.txt`. Produces
    collision-free filenames across all 4 Justia URL conventions in the
    calibration subset.
    """
    m = _JUSTIA_CODES_URL_RE.match(url)
    if not m:
        raise ValueError(f"URL not in /codes/STATE/YEAR/ namespace: {url}")
    tail = m.group(1).rstrip("/").removesuffix(".html")
    return tail.replace("/", "-") + ".txt"


def retrieve_statute_bundle(
    client: Client,
    *,
    state_abbr: str,
    vintage_year: int,
    urls: list[str],
    dest_dir: Path,
    year_delta: int = 0,
    direction: Literal["exact", "pre", "post"] = "exact",
    pri_state_reviewed: bool = False,
) -> Path:
    """Fetch each URL, parse statute text, write section files + manifest.

    Writes:
      - `<dest_dir>/sections/<filename>.txt` per URL
      - `<dest_dir>/manifest.json` describing the bundle

    Returns the path to the manifest. Raises ValueError on an empty `urls` list
    so we fail loudly rather than produce an empty bundle that quietly
    mis-represents a state's statute corpus.
    """
    if not urls:
        raise ValueError("urls list is empty — cannot retrieve an empty bundle")

    sections_dir = dest_dir / "sections"
    sections_dir.mkdir(parents=True, exist_ok=True)

    artifacts: list[dict] = []
    for url in urls:
        html = client.fetch_page(url)
        text = parse_statute_text(html)
        filename = _filename_from_url(url)
        path = sections_dir / filename
        path.write_text(text, encoding="utf-8")
        raw = path.read_bytes()
        artifacts.append(
            {
                "url": url,
                "role": "core_chapter",
                "sha256": hashlib.sha256(raw).hexdigest(),
                "bytes": len(raw),
                "local_path": f"sections/{filename}",
                "retrieved_because": "curated core lobbying chapter",
                "hop": 0,
                "referenced_from": "",
            }
        )

    manifest = {
        "state_abbr": state_abbr,
        "vintage_year": vintage_year,
        "year_delta": year_delta,
        "direction": direction,
        "pri_state_reviewed": pri_state_reviewed,
        "retrieved_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "artifacts": artifacts,
    }
    manifest_path = dest_dir / "manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    return manifest_path


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
