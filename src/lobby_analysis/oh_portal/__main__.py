"""CLI entrypoint: python -m lobby_analysis.oh_portal <OLAC_AER_URL>

Drives the (A') round-trip — fetch HTML, extract via LLM, write
LobbyingFiling JSON + ExtractionRun sidecar. Prints the output path.
"""

from __future__ import annotations

import json
import sys
import uuid
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path

from lobby_analysis.oh_portal.extract import (
    MODEL_ID,
    TOOL_NAME,
    extract_oh_legislative_filing,
)
from lobby_analysis.oh_portal.extraction_brief import build_oh_legislative_brief
from lobby_analysis.oh_portal.fetch import DATA_DIR, fetch_olac_aer, parse_report_id
from lobby_analysis.oh_portal.provenance import build_provenance

EXTRACTOR_IDENTITY = "oh-portal-extraction/v0.1"


def main() -> int:
    if len(sys.argv) != 2:
        print(f"usage: {sys.argv[0]} <OLAC_AER_URL>", file=sys.stderr)
        return 2

    url = sys.argv[1]
    report_id = parse_report_id(url)
    run_id = uuid.uuid4().hex[:8]
    started_at = datetime.now(timezone.utc)

    print(f"[oh_portal] fetching {url}", file=sys.stderr)
    html_path = fetch_olac_aer(url)
    print(f"[oh_portal] saved {html_path}", file=sys.stderr)

    brief = build_oh_legislative_brief()
    prompt_sha = sha256(brief.encode()).hexdigest()[:16]
    prompt_version = f"{EXTRACTOR_IDENTITY}:{prompt_sha}"

    provenance = build_provenance(
        source_url=url,
        model_version=MODEL_ID,
        prompt_version=prompt_version,
    )

    print(f"[oh_portal] extracting via {MODEL_ID} tool={TOOL_NAME}", file=sys.stderr)
    filing = extract_oh_legislative_filing(html_path, brief, provenance)
    finished_at = datetime.now(timezone.utc)

    out_dir = DATA_DIR / "extracted" / report_id / run_id
    out_dir.mkdir(parents=True, exist_ok=True)
    filing_path = out_dir / "filing.json"
    filing_path.write_text(filing.model_dump_json(indent=2))

    run_meta = {
        "run_id": run_id,
        "report_id": report_id,
        "source_url": url,
        "raw_html_path": str(html_path),
        "model_id": MODEL_ID,
        "tool_name": TOOL_NAME,
        "prompt_version": prompt_version,
        "extractor_identity": EXTRACTOR_IDENTITY,
        "started_at": started_at.isoformat(),
        "finished_at": finished_at.isoformat(),
        "duration_seconds": (finished_at - started_at).total_seconds(),
    }
    (out_dir / "extraction_run.json").write_text(json.dumps(run_meta, indent=2))

    print(filing_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
