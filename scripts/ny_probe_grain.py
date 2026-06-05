"""Phase 0 probe: true grain of client_semiannual 2025 — distinct filings,
lobbyists, clients, and the State-Bill+State-level working set — vs the
exploded row count (11.2M). Informs the dollar-conservation rule and
whether to pull via API or bulk CSV.
"""

from __future__ import annotations

import json

import requests

BASE = "https://data.ny.gov/resource/qym9-xzj6.json"


def scalar(select, where):
    r = requests.get(
        BASE, params={"$select": select, "$where": where}, timeout=180
    )
    r.raise_for_status()
    return r.json()


def main():
    out = {}
    where_2025 = "reporting_year = '2025'"
    probes = {
        "distinct_filings_2025": "count(distinct form_submission_id) AS n",
        "distinct_principal_lobbyists_2025": "count(distinct principal_lobbyist) AS n",
        "distinct_beneficial_clients_2025": "count(distinct beneficial_client) AS n",
        "total_rows_2025": "count(1) AS n",
    }
    for key, sel in probes.items():
        try:
            out[key] = scalar(sel, where_2025)
        except Exception as e:  # noqa: BLE001
            out[key] = {"error": repr(e)}

    # State-Bill + State-level working set (rows + distinct filings)
    where_sb = (
        "reporting_year = '2025' AND type_of_lobbying_focus = 'State Bill' "
        "AND starts_with(level_of_government, 'State') "
    )
    try:
        out["statebill_statelevel_rows_2025"] = scalar("count(1) AS n", where_sb)
    except Exception as e:  # noqa: BLE001
        out["statebill_statelevel_rows_2025"] = {"error": repr(e)}
    # distinct bill numbers in that working set
    try:
        out["distinct_state_bills_2025"] = scalar(
            "count(distinct focus_identifying_number) AS n", where_sb
        )
    except Exception as e:  # noqa: BLE001
        out["distinct_state_bills_2025"] = {"error": repr(e)}

    with open("/tmp/ny_grain.json", "w") as f:
        json.dump(out, f, indent=2, default=str)
    with open("/tmp/ny_grain_done.txt", "w") as f:
        f.write("done\n")


if __name__ == "__main__":
    main()
