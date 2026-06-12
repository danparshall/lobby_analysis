"""Phase 0 retry: the two large datasets that timed out, plus probe the
bill-number field on the retained-lobbyist bi-monthly report (the core
chain dataset). Writes JSON to /tmp for inspection.
"""

from __future__ import annotations

import json

import requests

BASE = "https://data.ny.gov/resource/{id}.json"


def fetch(ds_id, limit=3, where=None, order=None, timeout=180):
    params = {"$limit": limit}
    if where:
        params["$where"] = where
    if order:
        params["$order"] = order
    r = requests.get(BASE.format(id=ds_id), params=params, timeout=timeout)
    r.raise_for_status()
    return r.json()


def summarize(ds_id, rows):
    return {
        "id": ds_id,
        "columns": sorted({k for row in rows for k in row}) if rows else [],
        "examples": rows[:3],
        "n_sampled": len(rows),
    }


def main():
    out = {}
    # 1) retained lobbyist bi-monthly — core spend+bill dataset
    try:
        rows = fetch("t9kf-dqbc", limit=5, order="form_submission_id DESC")
        out["lobbyist_bimonthly"] = summarize("t9kf-dqbc", rows)
    except Exception as e:  # noqa: BLE001
        out["lobbyist_bimonthly"] = {"id": "t9kf-dqbc", "error": repr(e)}

    # 2) client semi-annual
    try:
        rows = fetch("qym9-xzj6", limit=5, order="form_submission_id DESC")
        out["client_semiannual"] = summarize("qym9-xzj6", rows)
    except Exception as e:  # noqa: BLE001
        out["client_semiannual"] = {"id": "qym9-xzj6", "error": repr(e)}

    # 3) probe: how many lobbyist_bimonthly rows have a State Bill focus?
    try:
        r = requests.get(
            BASE.format(id="t9kf-dqbc"),
            params={
                "$select": "type_of_lobbying_focus, count(1)",
                "$group": "type_of_lobbying_focus",
            },
            timeout=180,
        )
        r.raise_for_status()
        out["bimonthly_focus_breakdown"] = r.json()
    except Exception as e:  # noqa: BLE001
        out["bimonthly_focus_breakdown"] = {"error": repr(e)}

    with open("/tmp/ny_retry.json", "w") as f:
        json.dump(out, f, indent=2, default=str)
    with open("/tmp/ny_retry_done.txt", "w") as f:
        f.write(f"keys: {list(out)}\n")


if __name__ == "__main__":
    main()
