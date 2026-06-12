"""Phase 0 discovery: enumerate NY lobbying datasets on data.ny.gov.

Hits the Socrata catalog API (no auth needed) and prints candidate
lobbying datasets with their 4x4 id, name, row count, and updated date.
"""

from __future__ import annotations

import json

import requests

CATALOG = "https://api.us.socrata.com/api/catalog/v1"


def discover(query: str) -> list[dict]:
    params = {
        "domains": "data.ny.gov",
        "q": query,
        "only": "dataset",
        "limit": 100,
    }
    r = requests.get(CATALOG, params=params, timeout=60)
    r.raise_for_status()
    return r.json().get("results", [])


def main() -> None:
    seen: dict[str, dict] = {}
    for q in ("lobby", "lobbying", "lobbyist", "ethics lobby"):
        for res in discover(q):
            resource = res.get("resource", {})
            ds_id = resource.get("id")
            if not ds_id or ds_id in seen:
                continue
            seen[ds_id] = {
                "id": ds_id,
                "name": resource.get("name"),
                "rows": resource.get("rows_size"),
                "updated": resource.get("updatedAt"),
                "type": resource.get("type"),
                "domain_category": res.get("classification", {}).get(
                    "domain_category"
                ),
                "page": res.get("permalink"),
            }
    rows = sorted(seen.values(), key=lambda d: (d["name"] or "").lower())
    print(f"# {len(rows)} candidate datasets on data.ny.gov\n")
    for d in rows:
        print(json.dumps(d, default=str))


if __name__ == "__main__":
    main()
