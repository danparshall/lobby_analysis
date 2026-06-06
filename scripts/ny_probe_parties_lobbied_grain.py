"""Phase-0 GATING probe for the NY ``parties_lobbied`` MVP.

Answers the two facts that gate the table design (plan
``plans/ny_parties_lobbied_mvp.md`` Phase 0), against real data, before any
schema is frozen:

  A. **Grain.** Does ``parties_lobbied`` vary *within* one filing
     (``FILING_KEY`` = year + period + principal_lobbyist + beneficial_client +
     contractual_client_name)? And does it correlate with
     ``focus_identifying_number`` (reported per-bill/focus, or once per filing)?
     -> pulls every row for a handful of worst-case (highest-row-count)
     ``form_submission_id``s, with ``parties_lobbied`` + the focus columns, and
     measures distinct-party counts per FILING_KEY and per (FILING_KEY, focus).

  B. **Name format.** Can the disclosure free text be reconciled to the Open
     States ``ocd-person`` roster by *exact normalized match* (title/​suffix/​
     parenthetical strip), or is fuzzy matching required (which would expand MVP
     scope -> STOP and surface to Dan)?  -> builds the OS roster from
     ``NY_*_bill_sponsorships.csv`` and replays the recon top-400 distinct values
     through a candidate normalizer, reporting the row-weighted resolution rate
     and the unresolved head.

Also checks Q1 (multi-party delimited cells) on both the API sample and the
top-400 distinct values.

Pure analysis, no TDD, writes nothing to ``releases/``. Raw API sample saved for
provenance under ``results/``.

    uv run --active python scripts/ny_probe_parties_lobbied_grain.py
"""

from __future__ import annotations

import csv
import html
import json
import os
import re
from collections import Counter, defaultdict
from pathlib import Path

import requests

BASE = "https://data.ny.gov/resource/qym9-xzj6.json"
YEAR = "2025"
N_SUBMISSIONS = 5  # worst-case multi-row submissions to fully pull

RESULTS = Path("docs/active/ny-disclosure-explore/results")
RAW_OUT = RESULTS / "20260606_ny_parties_grain_sample.json"
RECON_TOP = RESULTS / "20260605_ny_parties_lobbied_top_distinct.json"

OS_DIR = Path("data/bills/NY/2025")

# FILING_KEY (mirrors io.ny.grain.FILING_KEY business identity, plus the firm).
FILING_KEY = (
    "reporting_year",
    "reporting_period",
    "principal_lobbyist",
    "beneficial_client",
    "contractual_client_name",
)

PULL_COLS = [
    "form_submission_id",
    "reporting_year",
    "reporting_period",
    "principal_lobbyist",
    "beneficial_client",
    "contractual_client_name",
    "type_of_lobbying_focus",
    "focus_identifying_number",
    "parties_lobbied",
]

# Candidate resolver normalization (exact-match MVP; see plan Phase 2).
TITLES = [
    "assembly member",
    "assemblywoman",
    "assemblyman",
    "assembly woman",
    "assembly man",
    "senator",
    "lieutenant governor",
    "governor",
    "comptroller",
    "attorney general",
]
_STAFF_SUFFIX = re.compile(r",\s*staff member\s*$", re.IGNORECASE)
_PAREN = re.compile(r"\s*\([^)]*\)")
_WS = re.compile(r"\s+")
_DELIM = re.compile(r";| and |&amp;|&| / ", re.IGNORECASE)
# Surface heuristic: does the value name an individual legislator?
_LEG_TITLE = re.compile(r"^\s*(senator|assembly\s*member|assemblyman|assemblywoman)\b", re.IGNORECASE)


def _headers() -> dict:
    tok = os.environ.get("SOCRATA_APP_TOKEN")
    return {"X-App-Token": tok} if tok else {}


def _get(params: dict) -> list:
    resp = requests.get(BASE, params=params, headers=_headers(), timeout=180)
    resp.raise_for_status()
    return resp.json()


def normalize_disclosure(raw: str) -> str:
    """Candidate exact-match normalizer for a disclosure ``parties_lobbied`` value."""
    s = html.unescape(str(raw)).strip().rstrip(";").strip()
    s = _STAFF_SUFFIX.sub("", s)
    s = _PAREN.sub("", s)
    low = s.lower()
    for t in TITLES:  # already longest-first where it matters
        if low.startswith(t + " "):
            s = s[len(t):].strip()
            break
    return _WS.sub(" ", s).strip().casefold()


def normalize_roster(name: str) -> str:
    """Normalize an OS roster name the SAME way, minus the title strip (OS has none)."""
    s = html.unescape(str(name)).strip()
    return _WS.sub(" ", s).strip().casefold()


# ---------------------------------------------------------------------------
# Part A — grain
# ---------------------------------------------------------------------------


def probe_grain() -> None:
    print("\n=== PART A: grain (per-filing vs per-focus) ===", flush=True)
    top = _get(
        {
            "$select": "form_submission_id, count(1) as n",
            "$where": f"reporting_year='{YEAR}'",
            "$group": "form_submission_id",
            "$order": "n DESC",
            "$limit": "15",
        }
    )
    ids = [str(r["form_submission_id"]) for r in top[:N_SUBMISSIONS]]
    print(f"[grain] worst-case submissions (id, rows): "
          f"{[(r['form_submission_id'], r['n']) for r in top[:N_SUBMISSIONS]]}", flush=True)

    in_clause = ",".join(ids)  # form_submission_id is numeric in SoQL
    rows = _get(
        {
            "$select": ",".join(PULL_COLS),
            "$where": f"reporting_year='{YEAR}' AND form_submission_id IN ({in_clause})",
            "$limit": "1000000",
        }
    )
    RAW_OUT.write_text(json.dumps(rows, indent=2))
    print(f"[grain] pulled {len(rows):,} rows for {len(ids)} submissions -> {RAW_OUT}", flush=True)

    # distinct parties per FILING_KEY, and per (FILING_KEY, focus_identifying_number)
    by_filing: dict[tuple, set] = defaultdict(set)
    by_filing_focus: dict[tuple, set] = defaultdict(set)
    filing_rows: Counter = Counter()
    for r in rows:
        fk = tuple(str(r.get(c, "")) for c in FILING_KEY)
        party = str(r.get("parties_lobbied", "")).strip()
        focus = str(r.get("focus_identifying_number", "")).strip()
        filing_rows[fk] += 1
        by_filing[fk].add(party)
        by_filing_focus[(fk, focus)].add(party)

    print(f"[grain] distinct FILING_KEYs in sample: {len(by_filing)}", flush=True)
    multi_party_filings = sum(1 for v in by_filing.values() if len(v) > 1)
    print(f"[grain] FILING_KEYs whose parties_lobbied VARIES (>1 distinct): "
          f"{multi_party_filings}/{len(by_filing)}", flush=True)
    # is the variation explained by focus? (i.e. constant within (filing, focus))
    focus_varies = sum(1 for v in by_filing_focus.values() if len(v) > 1)
    print(f"[grain] (FILING_KEY, focus) pairs whose parties_lobbied varies: "
          f"{focus_varies}/{len(by_filing_focus)}", flush=True)

    # show a representative filing's structure
    for fk, n in filing_rows.most_common(3):
        parties = sorted(by_filing[fk])
        print(f"\n[grain] filing {fk[:2]}... lobbyist={fk[2]!r} client={fk[3]!r}")
        print(f"        rows={n} distinct_parties={len(parties)}")
        for p in parties[:12]:
            print(f"          - {p!r}")
        if len(parties) > 12:
            print(f"          ... (+{len(parties) - 12} more)")

    # Q1: multi-party delimited cells in the API sample
    delim_cells = Counter()
    for r in rows:
        v = str(r.get("parties_lobbied", "")).strip()
        if v and _DELIM.search(v):
            delim_cells[v] += 1
    print(f"\n[grain] Q1 — sample cells containing a delimiter (;/and/&//): "
          f"{len(delim_cells)} distinct")
    for v, c in delim_cells.most_common(10):
        print(f"          {c:5d}  {v!r}")


# ---------------------------------------------------------------------------
# Part B — OS name-format reconciliation
# ---------------------------------------------------------------------------


def _os_sponsorships_csv() -> Path:
    matches = list(OS_DIR.glob("NY_*_bill_sponsorships.csv"))
    if not matches:
        raise FileNotFoundError(f"no NY_*_bill_sponsorships.csv under {OS_DIR}")
    return min(matches, key=lambda p: len(p.name))


def build_roster() -> dict[str, set]:
    """normalized name -> set of ocd-person ids (set surfaces collisions)."""
    roster: dict[str, set] = defaultdict(set)
    raw_names: dict[str, str] = {}
    path = _os_sponsorships_csv()
    csv.field_size_limit(10**7)
    with path.open(encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            if row.get("entity_type") != "person":
                continue
            pid = (row.get("person_id") or "").strip()
            name = (row.get("name") or "").strip()
            if not pid or not name:
                continue
            key = normalize_roster(name)
            roster[key].add(pid)
            raw_names[key] = name
    print(f"[roster] OS person-sponsors: {sum(len(v) for v in roster.values())} "
          f"(distinct normalized names: {len(roster)})", flush=True)
    collisions = {k: v for k, v in roster.items() if len(v) > 1}
    if collisions:
        print(f"[roster] WARNING: {len(collisions)} normalized names map to >1 ocd-person:")
        for k, v in list(collisions.items())[:10]:
            print(f"          {raw_names[k]!r} -> {sorted(v)}")
    return roster


def probe_name_format(roster: dict[str, set]) -> None:
    print("\n=== PART B: OS name-format reconciliation (exact-match feasibility) ===", flush=True)
    if not RECON_TOP.exists():
        print(f"[names] recon top-distinct file missing: {RECON_TOP}; run ny_probe_parties_lobbied.py")
        return
    grouped = json.loads(RECON_TOP.read_text())

    leg_rows = leg_hits = 0
    total_rows = 0
    misses: list[tuple[int, str, str]] = []
    delim_in_top = []
    for r in grouped:
        v = str(r.get("parties_lobbied", "")).strip()
        n = int(r.get("n", 0))
        total_rows += n
        if not v:
            continue
        if _DELIM.search(v):
            delim_in_top.append((n, v))
        if not _LEG_TITLE.search(v):
            continue  # only legislator-titled values are MVP-resolvable
        leg_rows += n
        norm = normalize_disclosure(v)
        if norm in roster:
            leg_hits += n
        else:
            misses.append((n, v, norm))

    print(f"[names] top-400 covers {total_rows:,} rows", flush=True)
    print(f"[names] legislator-titled rows: {leg_rows:,} "
          f"({100*leg_rows/total_rows:.1f}% of covered rows)")
    if leg_rows:
        print(f"[names] EXACT-MATCH resolved: {leg_hits:,}/{leg_rows:,} "
              f"= {100*leg_hits/leg_rows:.1f}% of legislator-titled rows")
    print(f"[names] unresolved legislator-titled values: {len(misses)} distinct "
          f"(row-weighted {sum(m[0] for m in misses):,})")
    for n, v, norm in sorted(misses, reverse=True)[:25]:
        print(f"          {n:7,d}  raw={v!r}  norm={norm!r}")

    print(f"\n[names] Q1 — top-400 values containing a delimiter: {len(delim_in_top)}")
    for n, v in sorted(delim_in_top, reverse=True)[:10]:
        print(f"          {n:7,d}  {v!r}")


def main() -> int:
    RESULTS.mkdir(parents=True, exist_ok=True)
    sess = "with app-token" if os.environ.get("SOCRATA_APP_TOKEN") else "no app-token"
    print(f"[probe] {BASE} year={YEAR} ({sess})", flush=True)
    probe_grain()
    roster = build_roster()
    probe_name_format(roster)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
