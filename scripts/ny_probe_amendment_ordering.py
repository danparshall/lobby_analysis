"""Phase 2 pre-flight probe #2: verify the supersede-ordering assumption for
client_semiannual (qym9-xzj6) before building the grain-collapse guard.

Probe #1 (ny_probe_amendments.py) established that an amendment is a NEW
form_submission_id that supersedes a prior submission for the same business
key. To dedup correctly we need a reliable "latest" rule. There is no
filed-date column, so the recommendation leans on form_submission_id being
monotonic with submission time. This probe tests that and checks for
re-amendment.

Business key under test:
    (reporting_year, reporting_period, principal_lobbyist,
     beneficial_client, contractual_client_name)

Probes (read-only):
  E1. Business keys in 2025 with >1 distinct form_submission_id, worst first.
      Quantifies how common multi-submission is and surfaces re-amendment.
  E2. For the top-N offender keys, enumerate every submission
      (form_submission_id, filing_type, comp). Python then checks:
        - is every Amendment id > every Original id for that key?  (monotonic)
        - how many Amendments exist per key?                       (re-amend)
"""

from __future__ import annotations

import json

import requests

BASE = "https://data.ny.gov/resource/qym9-xzj6.json"
OUT = "/tmp/ny_amendment_ordering_probe.json"

KEY_COLS = [
    "reporting_period",
    "principal_lobbyist",
    "beneficial_client",
    "contractual_client_name",
]


def q(params, timeout=120):
    last = None
    for _ in range(3):
        try:
            r = requests.get(BASE, params=params, timeout=timeout)
            r.raise_for_status()
            return r.json()
        except Exception as e:  # noqa: BLE001
            last = e
    return {"error": repr(last)}


def soql_str(v: str) -> str:
    return "'" + v.replace("'", "''") + "'"


def main():
    out = {}

    # E1: multi-submission business keys, 2025, worst first.
    group = ", ".join(KEY_COLS)
    e1 = q(
        {
            "$select": f"{group}, count(distinct form_submission_id) as n_subs",
            "$where": "reporting_year='2025'",
            "$group": group,
            "$having": "n_subs > 1",
            "$order": "n_subs DESC",
            "$limit": "40",
        }
    )
    out["E1_multi_submission_keys"] = e1

    # E2: enumerate submissions for the top offender keys; analyze ordering.
    analyses = []
    if isinstance(e1, list):
        for key in e1[:5]:
            where = " AND ".join(
                ["reporting_year='2025'"]
                + [f"{c}={soql_str(key[c])}" for c in KEY_COLS if key.get(c) is not None]
            )
            subs = q(
                {
                    "$select": "form_submission_id, filing_type, "
                    "current_period_compensation, count(1) as n_rows",
                    "$where": where,
                    "$group": "form_submission_id, filing_type, current_period_compensation",
                    "$order": "form_submission_id",
                }
            )
            analysis = {"key": {c: key.get(c) for c in KEY_COLS}, "submissions": subs}
            if isinstance(subs, list):
                def _id(s):
                    try:
                        return int(s["form_submission_id"])
                    except (KeyError, ValueError, TypeError):
                        return None

                orig_ids = [_id(s) for s in subs if s.get("filing_type") == "Original"]
                amend_ids = [_id(s) for s in subs if s.get("filing_type") == "Amendment"]
                orig_ids = [i for i in orig_ids if i is not None]
                amend_ids = [i for i in amend_ids if i is not None]
                analysis["n_originals"] = len(orig_ids)
                analysis["n_amendments"] = len(amend_ids)
                analysis["monotonic_amend_gt_orig"] = (
                    bool(orig_ids) and bool(amend_ids) and min(amend_ids) > max(orig_ids)
                )
            analyses.append(analysis)
    out["E2_submission_orderings"] = analyses

    with open(OUT, "w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
