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

import csv
import io
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


def read_url_regimes(args: Sequence[str]) -> list[tuple[str, Optional[str]]]:
    """Read AER URLs paired with their OLAC regime, from `--file <path>` or args.

    A discover TSV carries `aer_url` + `regime` columns; each row yields
    `(url, regime)`. A plain one-URL-per-line list (or a TSV predating the
    `regime` column) yields `(url, None)` — an unknown regime is surfaced as
    None, never silently treated as legislative. This is what lets
    `discover --out x.tsv` pipe straight into `batch --file x.tsv`."""
    if len(args) >= 2 and args[0] == "--file":
        return _read_file_url_regimes(Path(args[1]))
    return [(u, None) for u in args]


def _read_file_url_regimes(path: Path) -> list[tuple[str, Optional[str]]]:
    text = path.read_text()
    lines = [
        ln for ln in text.splitlines()
        if ln.strip() and not ln.lstrip().startswith("#")
    ]
    # discover TSV: a tab-delimited header naming aer_url. Pull the URL and the
    # (optional) regime column by name so column order can't silently mismatch.
    if lines and "\t" in lines[0] and "aer_url" in lines[0]:
        out: list[tuple[str, Optional[str]]] = []
        for row in csv.DictReader(io.StringIO(text), delimiter="\t"):
            url = (row.get("aer_url") or "").strip()
            if not url:
                continue
            regime = (row.get("regime") or "").strip() or None
            out.append((url, regime))
        return out
    # plain one-URL-per-line list — scan each line, no regime available.
    out = []
    for ln in lines:
        m = _AER_URL_RE.search(ln)
        if m:
            out.append((m.group(0), None))
    return out


def _read_urls(args: Sequence[str]) -> list[str]:
    """URLs only (regime dropped) — back-compat wrapper over read_url_regimes."""
    return [u for u, _ in read_url_regimes(args)]


def select_legislative(
    pairs: Sequence[tuple[str, Optional[str]]],
    include_nonlegislative: bool,
) -> tuple[list[tuple[str, Optional[str]]], int]:
    """Partition (url, regime) pairs by the skip policy.

    Only the legislative extraction brief exists, so by default non-legislative
    (and unknown-regime) filings are skipped to keep the corpus trustworthy.
    Returns (kept_pairs, skipped_count). With `include_nonlegislative=True`,
    nothing is skipped (those filings run through the legislative brief and get
    an extraction warning in `extract_one_filing`)."""
    if include_nonlegislative:
        return list(pairs), 0
    kept = [(u, r) for (u, r) in pairs if r == "legislative"]
    return kept, len(pairs) - len(kept)


def cli_main() -> int:
    """`python -m lobby_analysis.oh_portal.batch <url>... | --file <path>`."""
    import sys

    from lobby_analysis.oh_portal.env_local import load_env_local
    from lobby_analysis.oh_portal.fetch import DATA_DIR
    from lobby_analysis.oh_portal.pipeline import extract_one_filing

    load_env_local()
    argv = list(sys.argv[1:])
    include_nonlegislative = False
    if "--include-nonlegislative" in argv:
        argv.remove("--include-nonlegislative")
        include_nonlegislative = True

    pairs = read_url_regimes(argv)
    if not pairs:
        print(
            "usage: python -m lobby_analysis.oh_portal.batch <OLAC_AER_URL>... "
            "| --file <path> [--include-nonlegislative]",
            file=sys.stderr,
        )
        return 2

    kept, skipped = select_legislative(pairs, include_nonlegislative)
    if skipped:
        print(
            f"[oh_portal.batch] skipping {skipped} non-legislative/unknown-regime "
            "filing(s); pass --include-nonlegislative to extract them with the "
            "legislative brief (flagged via extraction_warnings)",
            file=sys.stderr,
        )
    regime_by_url = dict(kept)
    urls = [u for u, _ in kept]

    def process_one(url: str) -> Path:
        return extract_one_filing(
            url,
            regime=regime_by_url.get(url),
            log=lambda m: print(m, file=sys.stderr),
        )

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
