"""CLI entrypoint: python -m lobby_analysis.oh_portal <OLAC_AER_URL>

Drives the (A') round-trip for a single filing — fetch HTML, extract via LLM,
write LobbyingFiling JSON + ExtractionRun sidecar. Prints the output path.
The actual work lives in pipeline.extract_one_filing (shared with the batch
runner); this module is just argv + logging glue.
"""

from __future__ import annotations

import sys

from lobby_analysis.oh_portal.pipeline import extract_one_filing


def main() -> int:
    if len(sys.argv) != 2:
        print(f"usage: {sys.argv[0]} <OLAC_AER_URL>", file=sys.stderr)
        return 2

    url = sys.argv[1]
    filing_path = extract_one_filing(url, log=lambda msg: print(msg, file=sys.stderr))
    print(filing_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
