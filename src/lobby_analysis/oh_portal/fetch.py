"""Fetch one OLAC AER as HTML and write a versioned raw artifact + sidecar.

OLAC AERs are public, server-rendered HTML at /olac/AERs/{report_id}/View.
No PDF endpoint exists. (A')-scale: one URL → one file pair, fail loudly on
non-200, no retry. Versioning by fetched_at_iso so re-runs accumulate
rather than overwrite.
"""

import json
import re
import time
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path

import requests

USER_AGENT = "lobby_analysis-research/1.0 (+https://canaryinstitute.ai)"

# Spacing between *live* network requests to OLAC. Cache hits don't fetch, so
# they aren't throttled — only real server requests are. The runbook's full
# --all crawl is thousands of GETs against a state ethics server; this keeps the
# request rate polite. Tunable.
REQUEST_DELAY_SECONDS = 0.5


def throttle() -> None:
    """Sleep one polite interval before a live network request."""
    time.sleep(REQUEST_DELAY_SECONDS)

DATA_DIR = Path(__file__).resolve().parents[3] / "data" / "oh_portal"

OLAC_AER_URL_RE = re.compile(r"/olac/AERs/(\d+)/View", re.IGNORECASE)


def parse_report_id(url: str) -> str:
    """Pull the OLAC report ID out of a /olac/AERs/{id}/View URL.

    Raises ValueError if the URL doesn't match the expected pattern — better
    to fail at fetch start than to write artifacts under a wrong key.
    """
    m = OLAC_AER_URL_RE.search(url)
    if not m:
        raise ValueError(f"URL does not match /olac/AERs/<id>/View pattern: {url}")
    return m.group(1)


def fetch_olac_aer(url: str) -> Path:
    """Fetch one OLAC AER and persist raw.html + meta.json. Return raw.html path.

    Layout: data/oh_portal/raw/<report_id>/<fetched_at_iso>/{raw.html,meta.json}
    """
    report_id = parse_report_id(url)
    fetched_at = datetime.now(timezone.utc).replace(microsecond=0)
    fetched_at_iso = fetched_at.isoformat().replace(":", "-")

    out_dir = DATA_DIR / "raw" / report_id / fetched_at_iso
    out_dir.mkdir(parents=True, exist_ok=True)

    throttle()
    resp = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=30)
    if resp.status_code != 200:
        raise RuntimeError(
            f"OLAC fetch failed: {resp.status_code} for {url} "
            f"(content-type={resp.headers.get('content-type')!r})"
        )

    raw_path = out_dir / "raw.html"
    raw_path.write_bytes(resp.content)

    meta = {
        "url": url,
        "report_id": report_id,
        "sha256": sha256(resp.content).hexdigest(),
        "fetched_at": fetched_at.isoformat(),
        "content_type": resp.headers.get("content-type"),
        "http_status": resp.status_code,
        "byte_count": len(resp.content),
    }
    (out_dir / "meta.json").write_text(json.dumps(meta, indent=2))

    return raw_path
