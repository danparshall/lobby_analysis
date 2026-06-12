"""Phase 3 acquisition: pull the 2025 client_semiannual subset to disk.

Pulls the SODA ``/resource/qym9-xzj6.csv`` endpoint, projecting only the columns
the Phase-2 pipeline consumes and filtering to ``reporting_year='2025'``, into the
gitignored ``data/raw/ny/2025/client_semiannual.csv``.

**Why this paginates (2026-06-06).** A single streamed request for all ~11.2M
rows with a 12M ``$limit`` SILENTLY TRUNCATES — the server closes the stream
early (observed at 7,577,810 of 11,200,080 rows, a clean connection close that
``requests`` reads as a complete body), and nothing downstream notices because
the row count was never checked. ``$order=:id`` (the usual keyset-paging cure)
forces a full-table sort that times out on this 11.2M-row view, and
``form_submission_id`` is non-unique so offset paging on it is tie-unsafe.

So we paginate by **``form_submission_id`` value-ranges**: the view has only 8,613
distinct submission ids for 2025, so we group them (cheap aggregate query) into
contiguous id-range buckets of <=~800k rows each and pull each bucket with a
``form_submission_id BETWEEN lo AND hi`` filter. A whole id is never split across
buckets, so no keyset/offset tie hazard arises. **Every bucket's on-disk row count
is verified against its expected count (from the group-by) with retry**, and the
**final concatenated file is verified against the live ``count(*)``** — a short
pull can never again masquerade as complete. Buckets are checkpointed under
``.parts/`` so an interrupted run resumes without re-pulling completed buckets.

Run:
    uv run --active python scripts/ny_pull_2025.py
"""

from __future__ import annotations

import csv
import os
import time
from pathlib import Path

import requests

BASE = "https://data.ny.gov/resource/qym9-xzj6"
DATASET = "qym9-xzj6"  # client_semiannual ("Client Semi-Annual Report Beginning 2019")
YEAR = "2025"

# Exactly the columns the Phase-2 pipeline reads (column-map + grain + bill-id),
# plus parties_lobbied (the disclosed-lawmaker edge). level_of_government is
# intentionally omitted (scoping = focus_type alone).
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
PARTS_DIR = DEST.parent / ".parts"
TARGET_ROWS = 800_000  # bucket size ceiling (well under the ~7.6M truncation point)
READ_TIMEOUT = 300
RETRIES = 5

csv.field_size_limit(10**7)


def _headers() -> dict:
    tok = os.environ.get("SOCRATA_APP_TOKEN")
    return {"X-App-Token": tok} if tok else {}


def _live_count(session: requests.Session) -> int:
    r = session.get(
        f"{BASE}.json",
        params={"$select": "count(1)", "$where": f"reporting_year='{YEAR}'"},
        headers=_headers(), timeout=120,
    )
    r.raise_for_status()
    return int(r.json()[0]["count_1"])


def _id_counts(session: requests.Session) -> list[tuple[int, int]]:
    """Sorted ``(form_submission_id, row_count)`` for the year (one aggregate query)."""
    r = session.get(
        f"{BASE}.json",
        params={
            "$select": "form_submission_id, count(1) as n",
            "$where": f"reporting_year='{YEAR}'",
            "$group": "form_submission_id",
            "$order": "form_submission_id",
            "$limit": 60000,
        },
        headers=_headers(), timeout=180,
    )
    r.raise_for_status()
    rows = [(int(x["form_submission_id"]), int(x["n"])) for x in r.json()]
    return sorted(rows)


def _bucketize(id_counts: list[tuple[int, int]]) -> list[tuple[int, int, int]]:
    """Greedily group contiguous ids into ``(lo_id, hi_id, expected_rows)`` buckets."""
    buckets: list[tuple[int, int, int]] = []
    lo = hi = None
    acc = 0
    for sid, n in id_counts:
        if lo is None:
            lo = hi = sid
            acc = n
        elif acc + n > TARGET_ROWS:
            buckets.append((lo, hi, acc))
            lo = hi = sid
            acc = n
        else:
            hi = sid
            acc += n
    if lo is not None:
        buckets.append((lo, hi, acc))
    return buckets


def _count_records(path: Path) -> int:
    with path.open(encoding="utf-8", newline="") as fh:
        reader = csv.reader(fh)
        next(reader, None)  # header
        return sum(1 for _ in reader)


def _pull_bucket(session: requests.Session, lo: int, hi: int, expected: int, part: Path) -> None:
    """Stream one id-range bucket to ``part``, retrying until its row count matches."""
    where = (
        f"reporting_year='{YEAR}' AND form_submission_id >= {lo} "
        f"AND form_submission_id <= {hi}"
    )
    params = {"$select": ",".join(COLS), "$where": where,
              "$order": "form_submission_id", "$limit": expected + 10}
    for attempt in range(1, RETRIES + 1):
        tmp = part.with_suffix(".tmp")
        try:
            resp = session.get(f"{BASE}.csv", params=params, headers=_headers(),
                               stream=True, timeout=READ_TIMEOUT)
            resp.raise_for_status()
            with tmp.open("wb") as fh:
                for chunk in resp.iter_content(chunk_size=1 << 20):
                    if chunk:
                        fh.write(chunk)
            got = _count_records(tmp)
        except (requests.RequestException, OSError) as exc:
            print(f"    attempt {attempt}: transport error {exc!r}", flush=True)
            tmp.unlink(missing_ok=True)
            continue
        if got == expected:
            os.replace(tmp, part)
            return
        print(f"    attempt {attempt}: got {got:,} != expected {expected:,}; retrying", flush=True)
        tmp.unlink(missing_ok=True)
    raise RuntimeError(f"bucket ids[{lo}..{hi}] never reached {expected} rows after {RETRIES} tries")


def _concat(parts: list[Path], dest: Path, header: str) -> None:
    """Concatenate bucket files (header once) into ``dest`` atomically."""
    tmp = dest.with_suffix(".part")
    with tmp.open("wb") as out:
        out.write(header.encode("utf-8"))
        for part in parts:
            with part.open("rb") as fh:
                fh.readline()  # drop the per-bucket header (no embedded newline)
                while True:
                    block = fh.read(1 << 20)
                    if not block:
                        break
                    out.write(block)
    os.replace(tmp, dest)


def main() -> int:
    session = requests.Session()
    print(f"[ny-pull] dataset={DATASET} year={YEAR} dest={DEST}", flush=True)
    print(f"[ny-pull] columns={COLS}", flush=True)
    t0 = time.time()

    live = _live_count(session)
    id_counts = _id_counts(session)
    summed = sum(n for _, n in id_counts)
    print(f"[ny-pull] live count(*)={live:,} | distinct ids={len(id_counts)} "
          f"| sum(id counts)={summed:,}", flush=True)
    if summed != live:
        raise RuntimeError(f"group-by sum {summed} != live count {live}; data shifting mid-pull")

    buckets = _bucketize(id_counts)
    print(f"[ny-pull] {len(buckets)} buckets (<= {TARGET_ROWS:,} rows each)", flush=True)
    PARTS_DIR.mkdir(parents=True, exist_ok=True)

    header = ",".join(f'"{c}"' for c in COLS) + "\n"
    parts: list[Path] = []
    for i, (lo, hi, expected) in enumerate(buckets):
        part = PARTS_DIR / f"bucket_{i:03d}.csv"
        parts.append(part)
        if part.exists() and _count_records(part) == expected:
            print(f"[ny-pull] bucket {i:03d} ids[{lo}..{hi}] {expected:,} rows — cached", flush=True)
            continue
        print(f"[ny-pull] bucket {i:03d} ids[{lo}..{hi}] expect {expected:,} rows...", flush=True)
        _pull_bucket(session, lo, hi, expected, part)

    _concat(parts, DEST, header)
    final = _count_records(DEST)
    dt = time.time() - t0
    size = DEST.stat().st_size
    print(f"[ny-pull] concatenated {final:,} rows | {size/1e9:.2f} GB | {dt/60:.1f} min", flush=True)
    if final != live:
        raise RuntimeError(f"FINAL row count {final:,} != live {live:,} — pull incomplete")
    print(f"[ny-pull] VERIFIED {final:,} == live count(*) -> {DEST}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
