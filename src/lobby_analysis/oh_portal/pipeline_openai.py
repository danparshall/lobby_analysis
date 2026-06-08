"""Single-filing pipeline for the OpenAI cost-floor validation run.

Mirror of `pipeline.py::extract_one_filing` but with two operational changes
for the 3x mini validation against the existing Sonnet 300-slice:

  1. **Reads cached HTML, never re-fetches OLAC.** The plan requires the mini
     runs to extract from the exact same source the Sonnet baseline saw — so
     OLAC drift between June 5 and June 8 can't masquerade as model
     disagreement. This also avoids hitting OLAC 900 more times.

  2. **Writes to a parallel namespace.** Outputs go to
     `data/oh_portal/extracted_openai/<report_id>/<run_id>/filing.json` so the
     Sonnet baseline at `extracted/` is untouched and the analysis script can
     join the two trees by report_id.

See `docs/active/leave-behind-prep/plans/20260608_gpt5mini_on_oh_300slice.md`.
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from typing import Callable

from lobby_analysis.oh_portal.extract_openai import (
    extract_oh_legislative_filing,
    resolved_model_id,
)
from lobby_analysis.oh_portal.extraction_brief import build_oh_legislative_brief
from lobby_analysis.oh_portal.fetch import DATA_DIR
from lobby_analysis.oh_portal.provenance import build_provenance

EXTRACTOR_IDENTITY = "oh-portal-extraction-openai-validation/v0.1"
EXTRACTED_OPENAI_SUBDIR = "extracted_openai"


def _noop(_msg: str) -> None:
    pass


def find_cached_html(report_id: str, data_dir: Path = DATA_DIR) -> Path:
    """Return the most recent cached raw.html for `report_id`.

    The fetcher writes one timestamped subdirectory per fetch attempt. For the
    300-slice the Sonnet run fetched each report once on 2026-06-04/05, so
    typically there is exactly one timestamp dir; pick the lexicographically
    latest (ISO timestamps sort correctly).
    """
    raw_dir = data_dir / "raw" / report_id
    if not raw_dir.is_dir():
        raise FileNotFoundError(
            f"No cached raw HTML for report_id={report_id!r} at {raw_dir}. "
            f"Run the Sonnet pipeline first to populate the cache, or remove "
            f"this report_id from the dispatch list."
        )
    timestamp_dirs = sorted(
        (d for d in raw_dir.iterdir() if d.is_dir()),
        reverse=True,
    )
    for ts_dir in timestamp_dirs:
        html_path = ts_dir / "raw.html"
        if html_path.exists():
            return html_path
    raise FileNotFoundError(
        f"Cached dir {raw_dir} exists but contains no raw.html"
    )


def extract_one_filing_from_cache(
    report_id: str,
    *,
    run_label: str,
    data_dir: Path = DATA_DIR,
    log: Callable[[str], None] = _noop,
) -> tuple[Path, dict]:
    """Extract one cached OH AER via OpenAI. Return (filing.json path, usage).

    `run_label` is the per-pass identifier — e.g., "mini_run_1" for the first
    of the three runs. Combined with a uuid suffix it becomes the per-filing
    run_id (`mini_run_1_a1b2c3d4`), so the three passes' outputs land under
    distinct directories within each report_id.

    Writes:
      data_dir/extracted_openai/<report_id>/<run_id>/filing.json
      data_dir/extracted_openai/<report_id>/<run_id>/extraction_run.json
    """
    html_path = find_cached_html(report_id, data_dir)
    log(f"[oh_portal_openai] using cached html {html_path}")

    run_uuid = uuid.uuid4().hex[:8]
    run_id = f"{run_label}_{run_uuid}"
    started_at = datetime.now(timezone.utc)

    brief = build_oh_legislative_brief()
    prompt_sha = sha256(brief.encode()).hexdigest()[:16]
    prompt_version = f"{EXTRACTOR_IDENTITY}:{prompt_sha}"

    # Reconstruct the source URL from the report_id for provenance — the
    # OLAC AER view URL is structurally `https://www4.lobbyingontario...` (OH
    # actually). We don't have the original URL here; meta.json next to
    # raw.html has it. Read it back to avoid hardcoding URL templates.
    meta_path = html_path.parent / "meta.json"
    source_url = (
        json.loads(meta_path.read_text()).get("url")
        if meta_path.exists()
        else None
    )

    provenance = build_provenance(
        source_url=source_url,
        model_version=resolved_model_id(),
        prompt_version=prompt_version,
    )

    log(f"[oh_portal_openai] extracting via {resolved_model_id()} ({run_label})")
    filing, usage = extract_oh_legislative_filing(html_path, brief, provenance)
    finished_at = datetime.now(timezone.utc)

    out_dir = data_dir / EXTRACTED_OPENAI_SUBDIR / report_id / run_id
    out_dir.mkdir(parents=True, exist_ok=True)
    filing_path = out_dir / "filing.json"
    filing_path.write_text(filing.model_dump_json(indent=2))

    run_meta = {
        "run_id": run_id,
        "run_label": run_label,
        "report_id": report_id,
        "source_url": source_url,
        "raw_html_path": str(html_path),
        "regime": "legislative",
        "model_id": resolved_model_id(),
        "provider": "openai",
        "prompt_version": prompt_version,
        "extractor_identity": EXTRACTOR_IDENTITY,
        "started_at": started_at.isoformat(),
        "finished_at": finished_at.isoformat(),
        "duration_seconds": (finished_at - started_at).total_seconds(),
        "usage": usage,
    }
    (out_dir / "extraction_run.json").write_text(json.dumps(run_meta, indent=2))

    return filing_path, usage
