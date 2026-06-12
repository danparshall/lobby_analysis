"""Phase 0 probe: quantify the bill-linkage coverage for 2025 in the two
core chain datasets, and confirm reporting_year filtering works.

Chain closes only on rows whose focus type is 'State Bill' (focus id = a
real bill number). Everything else is subject/funding free text. This
measures that share — the realistic chain-closure ceiling for NY.
"""

from __future__ import annotations

import json

import requests

BASE = "https://data.ny.gov/resource/{id}.json"


def group_count(ds_id, focus_col, where):
    params = {
        "$select": f"{focus_col}, count(1) AS n",
        "$group": focus_col,
        "$order": "n DESC",
        "$where": where,
    }
    r = requests.get(BASE.format(id=ds_id), params=params, timeout=180)
    r.raise_for_status()
    return r.json()


def main():
    out = {}
    # client semi-annual: discriminator col = type_of_lobbying_focus
    try:
        out["client_semiannual_2025_focus"] = group_count(
            "qym9-xzj6",
            "type_of_lobbying_focus",
            "reporting_year = '2025'",
        )
    except Exception as e:  # noqa: BLE001
        out["client_semiannual_2025_focus"] = {"error": repr(e)}

    # lobbyist bi-monthly: discriminator col = lobbying_focus_type
    try:
        out["lobbyist_bimonthly_2025_focus"] = group_count(
            "t9kf-dqbc",
            "lobbying_focus_type",
            "reporting_year = '2025'",
        )
    except Exception as e:  # noqa: BLE001
        out["lobbyist_bimonthly_2025_focus"] = {"error": repr(e)}

    # sanity: distinct reporting_year values present in client semiannual
    try:
        r = requests.get(
            BASE.format(id="qym9-xzj6"),
            params={
                "$select": "reporting_year, count(1) AS n",
                "$group": "reporting_year",
                "$order": "reporting_year DESC",
            },
            timeout=180,
        )
        r.raise_for_status()
        out["client_semiannual_years"] = r.json()
    except Exception as e:  # noqa: BLE001
        out["client_semiannual_years"] = {"error": repr(e)}

    with open("/tmp/ny_billshare.json", "w") as f:
        json.dump(out, f, indent=2, default=str)
    with open("/tmp/ny_billshare_done.txt", "w") as f:
        f.write("done\n")


if __name__ == "__main__":
    main()
