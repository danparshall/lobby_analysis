"""Phase-0 grain confirmation on multiple mid-size filings.

The first grain probe truncated at $limit on a single 2.2M-row filing. This
selects several *mid-size* submissions (a few hundred rows each) so the whole
filing fits under the limit, and confirms across filings whether
``parties_lobbied`` is a per-filing SET (its own denormalization axis) rather
than a per-filing constant or a clean per-focus value.

    uv run --active python scripts/ny_probe_grain_confirm.py
"""

from __future__ import annotations

import json
import os
from collections import defaultdict
from pathlib import Path

import requests

BASE = "https://data.ny.gov/resource/qym9-xzj6.json"
YEAR = "2025"
RESULTS = Path("docs/active/ny-disclosure-explore/results")
RAW_OUT = RESULTS / "20260606_ny_parties_grain_confirm_sample.json"

FILING_KEY = (
    "reporting_year", "reporting_period", "principal_lobbyist",
    "beneficial_client", "contractual_client_name",
)
COLS = [
    "form_submission_id", *FILING_KEY,
    "type_of_lobbying_focus", "focus_identifying_number", "parties_lobbied",
]


def _headers() -> dict:
    tok = os.environ.get("SOCRATA_APP_TOKEN")
    return {"X-App-Token": tok} if tok else {}


def _get(params: dict) -> list:
    resp = requests.get(BASE, params=params, headers=_headers(), timeout=180)
    resp.raise_for_status()
    return resp.json()


def main() -> int:
    RESULTS.mkdir(parents=True, exist_ok=True)
    # submissions with moderate row counts: group, then take a window in the
    # middle of the distribution (skip the mega-filings, skip 1-row ones).
    grouped = _get({
        "$select": "form_submission_id, count(1) as n",
        "$where": f"reporting_year='{YEAR}'",
        "$group": "form_submission_id",
        "$order": "n DESC",
        "$limit": "4000",
    })
    mid = [r for r in grouped if 100 <= int(r["n"]) <= 800]
    picks = mid[:8]
    ids = [str(r["form_submission_id"]) for r in picks]
    print(f"[confirm] picked {len(ids)} mid-size submissions (id, rows): "
          f"{[(r['form_submission_id'], r['n']) for r in picks]}", flush=True)

    rows = _get({
        "$select": ",".join(COLS),
        "$where": f"reporting_year='{YEAR}' AND form_submission_id IN ({','.join(ids)})",
        "$limit": "100000",
    })
    RAW_OUT.write_text(json.dumps(rows, indent=2))
    print(f"[confirm] pulled {len(rows):,} rows -> {RAW_OUT}", flush=True)

    by_filing: dict[tuple, set] = defaultdict(set)
    by_filing_focus: dict[tuple, set] = defaultdict(set)
    rows_per_filing: dict[tuple, int] = defaultdict(int)
    for r in rows:
        fk = tuple(str(r.get(c, "")) for c in FILING_KEY)
        party = str(r.get("parties_lobbied", "")).strip()
        focus = str(r.get("focus_identifying_number", "")).strip()
        by_filing[fk].add(party)
        by_filing_focus[(fk, focus)].add(party)
        rows_per_filing[fk] += 1

    print(f"\n[confirm] distinct FILING_KEYs: {len(by_filing)}")
    print(f"{'rows':>6} {'distinct_parties':>16} {'lobbyist / client':<50}")
    for fk in sorted(by_filing, key=lambda k: -rows_per_filing[k]):
        print(f"{rows_per_filing[fk]:>6} {len(by_filing[fk]):>16}  "
              f"{fk[2][:24]!r} / {fk[3][:24]!r}")

    varies = sum(1 for v in by_filing.values() if len(v) > 1)
    focus_varies = sum(1 for v in by_filing_focus.values() if len(v) > 1)
    print(f"\n[confirm] filings whose parties_lobbied VARIES within the filing: "
          f"{varies}/{len(by_filing)}")
    print(f"[confirm] (filing, focus) pairs whose parties_lobbied varies: "
          f"{focus_varies}/{len(by_filing_focus)} "
          f"(>0 ⇒ NOT a clean per-focus mapping)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
