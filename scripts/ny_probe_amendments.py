"""Phase 2 pre-flight probe: resolve amendment-dedup semantics for
client_semiannual (qym9-xzj6).

The plan says "keep latest filing_type per form_submission_id". That is only
correct if an amendment RE-USES the original's form_submission_id (so one id
carries both Original and Amendment rows). If instead an amendment is a NEW
form submission with a NEW form_submission_id, then:
  - dedup must be on a business key, not form_submission_id, and
  - summing current_period_compensation over distinct form_submission_id
    DOUBLE-COUNTS the original + the amendment.

This is the load-bearing dollar-conservation question. Resolve it with data.

Probes (read-only, no auth):
  A. filing_type distribution for 2025.
  B. any single form_submission_id carrying >1 distinct filing_type?
  C. for one concrete business key (PARKSIDE / GRAHAM WINDHAM, 2025 July/Dec),
     how many form_submission_ids exist and what are their filing_types?
"""

from __future__ import annotations

import json

import requests

BASE = "https://data.ny.gov/resource/qym9-xzj6.json"
OUT = "/tmp/ny_amendments_probe.json"


def q(params, timeout=90):
    last = None
    for _ in range(3):
        try:
            r = requests.get(BASE, params=params, timeout=timeout)
            r.raise_for_status()
            return r.json()
        except Exception as e:  # noqa: BLE001
            last = e
    return {"error": repr(last)}


def main():
    out = {}

    # A. filing_type distribution 2025
    out["A_filing_type_dist_2025"] = q(
        {
            "$select": "filing_type, count(1) as n",
            "$where": "reporting_year='2025'",
            "$group": "filing_type",
        }
    )

    # B. any form_submission_id with >1 distinct filing_type?
    # min<>max over filing_type within a submission proves co-residence.
    out["B_submissions_with_mixed_filing_type"] = q(
        {
            "$select": "form_submission_id, min(filing_type) as lo, max(filing_type) as hi, count(1) as n",
            "$where": "reporting_year='2025'",
            "$group": "form_submission_id",
            "$having": "lo <> hi",
            "$limit": "10",
        }
    )

    # C. concrete business key: does an amended report have its own id?
    bizkey = (
        "reporting_year='2025' "
        "AND principal_lobbyist='THE PARKSIDE GROUP LLC' "
        "AND beneficial_client='GRAHAM WINDHAM;'"
    )
    out["C_parkside_grahamwindham_by_submission"] = q(
        {
            "$select": "form_submission_id, reporting_period, filing_type, "
            "current_period_compensation, count(1) as n",
            "$where": bizkey,
            "$group": "form_submission_id, reporting_period, filing_type, "
            "current_period_compensation",
            "$order": "form_submission_id",
        }
    )

    # D. broader: distinct (form_submission_id) count vs distinct business keys,
    # restricted to a small slice to see if ids >> business keys (amendments add ids).
    out["D_id_vs_bizkey_counts_2025"] = {
        "distinct_form_submission_ids": q(
            {
                "$select": "count(distinct form_submission_id) as n",
                "$where": "reporting_year='2025'",
            }
        ),
    }

    with open(OUT, "w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
