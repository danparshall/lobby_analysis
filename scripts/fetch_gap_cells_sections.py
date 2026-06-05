"""Section-body fetch for the 5 top-10 gap cells (pass 1, 2026-06-05).

Consumes the discovery bundles produced this session and downloads statute
section bodies to data/statutes/<STATE>/<VINTAGE>/sections/ via the rate-limited
PlaywrightClient. Idempotent at the cell level; re-run is safe (overwrites).

Cells: FL 2010, NC 2010, NY 2010, NY 2015, NY 2025.
Skips NY's `rla/` monolith (support-only; the leg/article-1-a section leaves are
the canonical bodies).
"""

import json
from pathlib import Path

from scoring.justia_client import PlaywrightClient
from scoring.statute_retrieval import retrieve_statute_bundle

BASE = Path("data/statutes")
CANARY = Path("docs/active/api-multi-vintage-retrieval/results/subagent_canaries")
CELLS = [("FL", 2010), ("NC", 2010), ("NY", 2010), ("NY", 2015), ("NY", 2025)]


def main() -> None:
    client = PlaywrightClient(rate_limit_seconds=2.5)
    for state, vintage in CELLS:
        rj = json.loads((CANARY / f"{state}_{vintage}" / "result.json").read_text())
        urls = [
            u["url"]
            for u in rj["proposed_urls"]
            if not u["url"].rstrip("/").endswith("/rla")
        ]
        dest = BASE / state / str(vintage)
        print(f"[{state} {vintage}] fetching {len(urls)} sections -> {dest}", flush=True)
        mp = retrieve_statute_bundle(
            client,
            state_abbr=state,
            vintage_year=vintage,
            urls=urls,
            dest_dir=dest,
        )
        print(f"[{state} {vintage}] manifest: {mp}", flush=True)

    print("\n=== SIZE SANITY (flag <500B = possible CF stub / parse miss) ===", flush=True)
    for state, vintage in CELLS:
        sdir = BASE / state / str(vintage) / "sections"
        files = sorted(sdir.glob("*.txt"))
        small = [f.name for f in files if f.stat().st_size < 500]
        sizes = [f.stat().st_size for f in files]
        med = sorted(sizes)[len(sizes) // 2] if sizes else 0
        print(
            f"[{state} {vintage}] {len(files)} files, median {med}B"
            + (f"  ⚠ SMALL: {small}" if small else ""),
            flush=True,
        )
    print("DONE", flush=True)


if __name__ == "__main__":
    main()
