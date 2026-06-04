"""(B') batch runner over OLAC AER URLs.

Loops the proven (A') single-filing pipeline over a list of URLs with two
operational guarantees the volume work needs:

  - **Resume / idempotency.** A report_id that already has a written
    extraction is skipped, so an interrupted batch can be re-run safely
    without duplicate LLM calls or clobbered artifacts.
  - **Failure isolation.** One filing's fetch/extraction error is captured
    as a per-filing `failed` result; the batch continues to the rest.

Discovery of the report_id universe (enumerating OLAC) is a SEPARATE,
unsolved problem — this runner consumes a caller-supplied URL list.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Literal, Optional, Sequence

from lobby_analysis.oh_portal.fetch import parse_report_id

_AER_URL_RE = re.compile(r"https?://\S*?/olac/AERs/\d+/View")

BatchStatus = Literal["extracted", "skipped", "failed"]


@dataclass(frozen=True)
class BatchResult:
    report_id: str
    url: str
    status: BatchStatus
    filing_path: Optional[Path]
    error: Optional[str]


def find_existing_extraction(report_id: str, data_dir: Path) -> Optional[Path]:
    """Return the path to a prior `filing.json` for this report_id, or None.

    A bare `extracted/<report_id>/` directory with no run that produced a
    `filing.json` does NOT count as extracted — the resume guard keys on the
    written filing, not on a directory having been created.
    """
    report_dir = data_dir / "extracted" / report_id
    if not report_dir.is_dir():
        return None
    for run_dir in sorted(report_dir.iterdir()):
        candidate = run_dir / "filing.json"
        if candidate.exists():
            return candidate
    return None


def run_batch(
    urls: Sequence[str],
    data_dir: Path,
    process_one: Callable[[str], Path],
    *,
    resume: bool = True,
) -> list[BatchResult]:
    """Run `process_one` over each URL, skipping already-extracted report_ids
    and isolating per-filing failures.

    `process_one(url)` performs the expensive fetch + LLM extraction + write
    for a single filing and returns the written `filing.json` path.
    """
    results: list[BatchResult] = []
    for url in urls:
        report_id = parse_report_id(url)
        if resume:
            existing = find_existing_extraction(report_id, data_dir)
            if existing is not None:
                results.append(
                    BatchResult(report_id, url, "skipped", existing, None)
                )
                continue
        try:
            filing_path = process_one(url)
            results.append(
                BatchResult(report_id, url, "extracted", filing_path, None)
            )
        except Exception as exc:  # noqa: BLE001 — isolate one filing's failure
            results.append(BatchResult(report_id, url, "failed", None, repr(exc)))
    return results


def _read_urls(args: Sequence[str]) -> list[str]:
    """URLs come either as positional args, or via `--file <path>`.

    A `--file` may be a plain one-URL-per-line list OR the discover step's rich
    TSV — each non-comment line is scanned for an `/olac/AERs/{id}/View` URL and
    that token is taken (so the header and any extra columns are ignored). This
    is what lets `discover --out x.tsv` pipe straight into `batch --file x.tsv`."""
    if len(args) >= 2 and args[0] == "--file":
        urls: list[str] = []
        for ln in Path(args[1]).read_text().splitlines():
            ln = ln.strip()
            if not ln or ln.startswith("#"):
                continue
            m = _AER_URL_RE.search(ln)
            if m:
                urls.append(m.group(0))
        return urls
    return list(args)


def cli_main() -> int:
    """`python -m lobby_analysis.oh_portal.batch <url>... | --file <path>`."""
    import sys

    from lobby_analysis.oh_portal.env_local import load_env_local
    from lobby_analysis.oh_portal.fetch import DATA_DIR
    from lobby_analysis.oh_portal.pipeline import extract_one_filing

    load_env_local()
    urls = _read_urls(sys.argv[1:])
    if not urls:
        print(
            "usage: python -m lobby_analysis.oh_portal.batch <OLAC_AER_URL>... "
            "| --file <path>",
            file=sys.stderr,
        )
        return 2

    def process_one(url: str) -> Path:
        return extract_one_filing(url, log=lambda m: print(m, file=sys.stderr))

    results = run_batch(urls, DATA_DIR, process_one)

    counts = {"extracted": 0, "skipped": 0, "failed": 0}
    for r in results:
        counts[r.status] += 1
        line = f"[{r.status:9}] {r.report_id}"
        if r.status == "extracted":
            line += f" -> {r.filing_path}"
        elif r.status == "skipped":
            line += f" (already at {r.filing_path})"
        elif r.status == "failed":
            line += f" :: {r.error}"
        print(line, file=sys.stderr)

    print(
        f"[oh_portal.batch] {len(results)} filings: "
        f"{counts['extracted']} extracted, {counts['skipped']} skipped, "
        f"{counts['failed']} failed",
        file=sys.stderr,
    )
    return 1 if counts["failed"] else 0


if __name__ == "__main__":
    raise SystemExit(cli_main())
