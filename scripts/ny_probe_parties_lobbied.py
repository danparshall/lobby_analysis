"""Reconnaissance probe for the NY ``parties_lobbied`` disclosed-lawmaker edge.

NOT a pull and NOT a resolver. Characterizes the free-text shape of
``client_semiannual.parties_lobbied`` so the eventual ocd-person resolution
approach can be designed against real data:

  * what fraction of 2025 rows populate the field (row-grain, denormalized);
  * the distribution of value *kinds* (named legislator vs executive office vs
    agency vs committee vs multi-name cell), via cheap surface heuristics;
  * a saved raw sample for provenance.

One aggregate count query + one bounded sample request against the SODA JSON
endpoint (``qym9-xzj6``). Writes the raw sample + a categorized summary under
``docs/active/ny-disclosure-explore/results/``.

    uv run --active python scripts/ny_probe_parties_lobbied.py
"""

from __future__ import annotations

import json
import os
import re
from collections import Counter
from pathlib import Path

import requests

BASE = "https://data.ny.gov/resource/qym9-xzj6.json"
YEAR = "2025"
SAMPLE_LIMIT = 5000
OUT_DIR = Path(
    "docs/active/ny-disclosure-explore/results"
)
RAW_OUT = OUT_DIR / "20260605_ny_parties_lobbied_sample.json"
GROUP_OUT = OUT_DIR / "20260605_ny_parties_lobbied_top_distinct.json"
GROUP_TOP = 400

# Surface heuristics for value *kind*. Deliberately coarse -- the point is to
# size the resolution problem, not to be the resolver.
LEGISLATOR_TITLE = re.compile(
    r"\b(senator|assembly\s*member|assemblyman|assemblywoman|assembly\s*man|"
    r"assembly\s*woman|sen\.|asm\.|am\b|legislator)\b",
    re.IGNORECASE,
)
OFFICE = re.compile(
    r"\b(governor|executive chamber|lieutenant|comptroller|attorney general|"
    r"mayor|commissioner|secretary|office of|department|division|authority|"
    r"agency|board|council|administration)\b",
    re.IGNORECASE,
)
COMMITTEE = re.compile(r"\b(committee|caucus|conference|majority|minority|staff)\b", re.IGNORECASE)
MULTI = re.compile(r"[;,/&]| and ", re.IGNORECASE)


def _headers() -> dict:
    tok = os.environ.get("SOCRATA_APP_TOKEN")
    return {"X-App-Token": tok} if tok else {}


def _get(params: dict) -> object:
    resp = requests.get(BASE, params=params, headers=_headers(), timeout=120)
    resp.raise_for_status()
    return resp.json()


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    sess_note = "with app-token" if os.environ.get("SOCRATA_APP_TOKEN") else "no app-token"
    print(f"[probe] {BASE} year={YEAR} ({sess_note})", flush=True)

    total = _get({"$select": "count(1)", "$where": f"reporting_year='{YEAR}'"})
    populated = _get(
        {
            "$select": "count(1)",
            "$where": f"reporting_year='{YEAR}' AND parties_lobbied IS NOT NULL",
        }
    )
    total_n = int(total[0]["count_1"])
    pop_n = int(populated[0]["count_1"])
    print(f"[probe] 2025 rows total={total_n:,} populated={pop_n:,} "
          f"({100*pop_n/total_n:.1f}% row-grain)", flush=True)

    # 99.9% of rows populate the field, so skip the (unindexed, slow) IS NOT NULL
    # filter + sort and just page the front of the year, filtering populated
    # rows client-side. Cheap and representative for shape characterization.
    sample = _get(
        {
            "$select": "form_submission_id,reporting_period,parties_lobbied",
            "$where": f"reporting_year='{YEAR}'",
            "$limit": str(SAMPLE_LIMIT),
        }
    )
    RAW_OUT.write_text(json.dumps(sample, indent=2))
    print(f"[probe] saved {len(sample)} sample rows -> {RAW_OUT}", flush=True)

    values = [str(r.get("parties_lobbied", "")).strip() for r in sample]
    values = [v for v in values if v]
    distinct = sorted(set(values))

    kinds: Counter = Counter()
    for v in values:
        if MULTI.search(v):
            kinds["multi/compound"] += 1
        if LEGISLATOR_TITLE.search(v):
            kinds["named-legislator-title"] += 1
        elif COMMITTEE.search(v):
            kinds["committee/caucus/staff"] += 1
        elif OFFICE.search(v):
            kinds["executive-office/agency"] += 1
        else:
            kinds["uncategorized"] += 1

    print(f"[probe] sample values={len(values)} distinct={len(distinct)}")
    print("[probe] kind histogram (heuristic, non-exclusive for multi):")
    for k, c in kinds.most_common():
        print(f"    {c:5d}  {k}")

    print("[probe] 30 distinct examples:")
    for v in distinct[:30]:
        print(f"    {v!r}")

    # The row sample is clustered (denormalized front-of-year) -> only a narrow
    # slice of distinct values. A GROUP BY over the whole year gives the
    # representative distinct-value frequency distribution, which is what the
    # resolution design actually needs.
    print(f"[probe] GROUP BY parties_lobbied over all {YEAR} rows (top {GROUP_TOP})...",
          flush=True)
    try:
        grouped = _get(
            {
                "$select": "parties_lobbied, count(1) as n",
                "$where": f"reporting_year='{YEAR}'",
                "$group": "parties_lobbied",
                "$order": "n DESC",
                "$limit": str(GROUP_TOP),
            }
        )
        GROUP_OUT.write_text(json.dumps(grouped, indent=2))
        print(f"[probe] saved {len(grouped)} top distinct values -> {GROUP_OUT}", flush=True)
        gkinds: Counter = Counter()
        for r in grouped:
            v = str(r.get("parties_lobbied", "")).strip()
            n = int(r.get("n", 0))
            if LEGISLATOR_TITLE.search(v):
                gkinds["named-legislator-title"] += n
            elif COMMITTEE.search(v):
                gkinds["committee/caucus/staff"] += n
            elif OFFICE.search(v):
                gkinds["executive-office/agency"] += n
            else:
                gkinds["uncategorized"] += n
        gtot = sum(gkinds.values()) or 1
        print(f"[probe] top-{GROUP_TOP} distinct-value kind histogram (row-weighted):")
        for k, c in gkinds.most_common():
            print(f"    {c:9,d}  ({100*c/gtot:4.1f}%)  {k}")
        print("[probe] top 25 distinct values by row frequency:")
        for r in grouped[:25]:
            print(f"    {int(r['n']):8,d}  {str(r['parties_lobbied'])!r}")
    except requests.RequestException as exc:
        print(f"[probe] GROUP BY failed ({exc!r}); row-sample shape stands.", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
