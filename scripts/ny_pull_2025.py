"""Phase 3 acquisition: pull the 2025 client_semiannual subset to disk.

Drives ``io.ny.acquire.download_resource_csv`` against the SODA
``/resource/qym9-xzj6.csv`` endpoint, projecting only the columns the Phase-2
pipeline consumes and filtering to ``reporting_year='2025'``. Writes to the
gitignored ``data/raw/ny/2025/client_semiannual.csv`` with resume-skip + atomic
temp-then-rename, so a re-run never re-hits the API.

The whole-view bulk export (``download_bulk_csv``) is NOT used here: it dumps all
66.9M rows (2019-present) with human-readable display headers the column-map
can't consume. This filtered pull is ~3.17 GB / 11.2M rows with field-name
headers.

Run:
    uv run --active python scripts/ny_pull_2025.py
"""

from __future__ import annotations

import time
from pathlib import Path

import requests

from lobby_analysis.io.ny.acquire import download_resource_csv

DATASET = "qym9-xzj6"  # client_semiannual ("Client Semi-Annual Report Beginning 2019")
YEAR = "2025"

# Exactly the columns the Phase-2 pipeline reads (column-map + grain + bill-id):
#   business key + grain, money, and the two bill-id derivation columns.
# level_of_government is intentionally omitted (scoping = focus_type alone).
COLS = [
    "form_submission_id",
    "reporting_year",
    "reporting_period",
    "principal_lobbyist",
    "beneficial_client",
    "contractual_client_name",
    "current_period_compensation",
    "type_of_lobbying_focus",
    "focus_identifying_number",
    "parties_lobbied",
]

DEST = Path("data/raw/ny") / YEAR / "client_semiannual.csv"


def main() -> int:
    print(f"[ny-pull] dataset={DATASET} year={YEAR}", flush=True)
    print(f"[ny-pull] dest={DEST}", flush=True)
    print(f"[ny-pull] columns={COLS}", flush=True)
    t0 = time.time()
    path = download_resource_csv(
        DATASET,
        DEST,
        requests.Session(),
        select=",".join(COLS),
        where=f"reporting_year='{YEAR}'",
        order_by="form_submission_id",
        limit=12_000_000,  # above the known 11,200,080 row count -> full single-request stream
        timeout=600,  # generous per-read timeout for a multi-GB stream
    )
    dt = time.time() - t0
    size = path.stat().st_size
    print(f"[ny-pull] DONE in {dt/60:.1f} min | {size/1e9:.2f} GB -> {path}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
