"""Fetch a Justia page via Playwright, save raw HTML + cleaned TSV, print TSV.

Usage: subagent_fetch_save.py <out_dir> <pass_label> <url>

Where pass_label is "pass1", "pass2", or "pass3". The filename stem is derived
from the URL: pass1 → "pass1_state_index"; pass2/pass3 → "<label>_<last-segment>".

Used by the subagent canary dispatch when the Anthropic workspace API cap is
hit (see docs/active/api-multi-vintage-retrieval/results/subagent_canaries/
README.md). Saves both the raw HTML and the cleaned TSV so a future direct-API
run can replay the exact prompt over the exact input.

Machine-local; not gitignored but not committed either (same pattern as
scripts/canary_discovery.py).
"""

import sys
from pathlib import Path
from urllib.parse import urlparse

from scoring.api_retrieval_agent import _build_justia_link_tsv
from scoring.justia_client import PlaywrightClient


def main() -> int:
    if len(sys.argv) != 4:
        print(__doc__, file=sys.stderr)
        return 2

    out_dir = Path(sys.argv[1])
    label = sys.argv[2]
    url = sys.argv[3]

    if label not in {"pass1", "pass2", "pass3"}:
        print(f"unknown pass_label: {label!r}", file=sys.stderr)
        return 2

    parsed = urlparse(url)
    path_parts = [p for p in parsed.path.strip("/").split("/") if p]
    if label == "pass1":
        slug = "state_index"
    elif path_parts:
        slug = path_parts[-1].replace(".html", "")
    else:
        slug = "root"
    stem = f"{label}_{slug}"

    out_dir.mkdir(parents=True, exist_ok=True)
    html = PlaywrightClient().fetch_page(url)
    (out_dir / f"{stem}.html").write_text(html)
    tsv = _build_justia_link_tsv(html, url)
    (out_dir / f"{stem}.tsv").write_text(tsv)
    print(tsv)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
