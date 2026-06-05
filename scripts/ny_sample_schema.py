"""Phase 0: pull tiny samples from the 6 NY 'Beginning 2019' lobbying datasets
and print their columns + one example row, so we can verify the real schema
(bill-number field? transactional dollars? stance?).
"""

from __future__ import annotations

import json

import requests

BASE = "https://data.ny.gov/resource/{id}.json"

DATASETS = {
    "lobbyist_registration": "se5j-cmbb",
    "lobbyist_bimonthly": "t9kf-dqbc",
    "client_semiannual": "qym9-xzj6",
    "disbursement_public_monies": "i574-v3dp",
    "public_corp_registration": "2pde-cfs9",
    "public_corp_bimonthly": "ffd8-nyat",
}


def fetch(ds_id: str, limit: int = 3, where: str | None = None) -> list[dict]:
    params = {"$limit": limit}
    if where:
        params["$where"] = where
    r = requests.get(BASE.format(id=ds_id), params=params, timeout=60)
    r.raise_for_status()
    return r.json()


def main() -> None:
    out: dict[str, dict] = {}
    for label, ds_id in DATASETS.items():
        entry: dict = {"id": ds_id}
        try:
            rows = fetch(ds_id, limit=3)
            entry["columns"] = sorted({k for row in rows for k in row})
            entry["example"] = rows[0] if rows else None
            entry["n_sampled"] = len(rows)
        except Exception as e:  # noqa: BLE001
            entry["error"] = repr(e)
        out[label] = entry
    dest = "/tmp/ny_schema.json"
    with open(dest, "w") as f:
        json.dump(out, f, indent=2, default=str)
    # also write a flag file proving completion
    with open("/tmp/ny_schema_done.txt", "w") as f:
        f.write(f"datasets: {list(out)}\n")


if __name__ == "__main__":
    main()
