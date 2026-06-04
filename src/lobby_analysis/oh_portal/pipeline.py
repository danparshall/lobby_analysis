"""Single-filing pipeline: fetch one OLAC AER, extract it, write artifacts.

Factored out of __main__ so both the single-filing CLI and the (B') batch
runner share one code path. Returns the written `filing.json` path and, as a
side effect, writes the `extraction_run.json` sidecar next to it.
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from typing import Callable

from lobby_analysis.oh_portal.extract import (
    MODEL_ID,
    TOOL_NAME,
    extract_oh_legislative_filing,
)
from lobby_analysis.oh_portal.extraction_brief import build_oh_legislative_brief
from lobby_analysis.oh_portal.fetch import DATA_DIR, fetch_olac_aer, parse_report_id
from lobby_analysis.oh_portal.provenance import build_provenance

EXTRACTOR_IDENTITY = "oh-portal-extraction/v0.1"
# This brief is OH legislative-regime-specific, so regime is a constant property
# of the run (caller-stamped), not something the model extracts. Recorded in run
# metadata; a first-class regime axis is deferred to the v2.2 schema pivot.
REGIME = "legislative"


def _noop(_msg: str) -> None:
    pass


def extract_one_filing(
    url: str,
    data_dir: Path = DATA_DIR,
    *,
    log: Callable[[str], None] = _noop,
) -> Path:
    """Fetch + extract + persist one OLAC AER. Return the `filing.json` path.

    Writes `data_dir/extracted/<report_id>/<run_id>/{filing.json,extraction_run.json}`.
    Raises on fetch failure, missing tool call, or Pydantic validation failure
    (fail-loud — the caller decides whether to isolate the failure).
    """
    report_id = parse_report_id(url)
    run_id = uuid.uuid4().hex[:8]
    started_at = datetime.now(timezone.utc)

    log(f"[oh_portal] fetching {url}")
    html_path = fetch_olac_aer(url)
    log(f"[oh_portal] saved {html_path}")

    brief = build_oh_legislative_brief()
    prompt_sha = sha256(brief.encode()).hexdigest()[:16]
    prompt_version = f"{EXTRACTOR_IDENTITY}:{prompt_sha}"

    provenance = build_provenance(
        source_url=url,
        model_version=MODEL_ID,
        prompt_version=prompt_version,
    )

    log(f"[oh_portal] extracting via {MODEL_ID} tool={TOOL_NAME}")
    filing = extract_oh_legislative_filing(html_path, brief, provenance)
    finished_at = datetime.now(timezone.utc)

    out_dir = data_dir / "extracted" / report_id / run_id
    out_dir.mkdir(parents=True, exist_ok=True)
    filing_path = out_dir / "filing.json"
    filing_path.write_text(filing.model_dump_json(indent=2))

    run_meta = {
        "run_id": run_id,
        "report_id": report_id,
        "source_url": url,
        "raw_html_path": str(html_path),
        "regime": REGIME,
        "model_id": MODEL_ID,
        "tool_name": TOOL_NAME,
        "prompt_version": prompt_version,
        "extractor_identity": EXTRACTOR_IDENTITY,
        "started_at": started_at.isoformat(),
        "finished_at": finished_at.isoformat(),
        "duration_seconds": (finished_at - started_at).total_seconds(),
    }
    (out_dir / "extraction_run.json").write_text(json.dumps(run_meta, indent=2))

    return filing_path
