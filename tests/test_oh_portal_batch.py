"""Tests for the OH-portal (B') batch runner.

The network fetch + LLM extraction is an external side-effecting boundary; it
is NOT exercised here. What IS tested is the batch runner's own behavior:

  - the resume guard (real filesystem: does a prior extraction exist?)
  - orchestration: already-extracted report_ids are skipped, per-filing
    failures are isolated so the batch finishes, and each filing's outcome
    is reported.

The per-filing worker is injected as a real local function (a seam for the
expensive boundary), and assertions are on the batch's observable outcomes —
not on "the worker was called" as an end in itself.
"""

from pathlib import Path

from lobby_analysis.oh_portal.batch import (
    find_existing_extraction,
    run_batch,
)


def _seed_extraction(data_dir: Path, report_id: str, run_id: str = "run0") -> Path:
    """Create a data/oh_portal-shaped extraction artifact on disk."""
    out = data_dir / "extracted" / report_id / run_id
    out.mkdir(parents=True)
    filing = out / "filing.json"
    filing.write_text("{}")
    return filing


def test_find_existing_extraction_returns_path_when_a_filing_exists(tmp_path: Path) -> None:
    seeded = _seed_extraction(tmp_path, "1427844")
    found = find_existing_extraction("1427844", tmp_path)
    assert found == seeded


def test_find_existing_extraction_returns_none_when_no_filing(tmp_path: Path) -> None:
    # A raw fetch with no extraction must NOT count as already-extracted.
    (tmp_path / "extracted" / "1427844").mkdir(parents=True)
    assert find_existing_extraction("1427844", tmp_path) is None


def test_run_batch_skips_already_extracted_and_processes_the_rest(tmp_path: Path) -> None:
    _seed_extraction(tmp_path, "1427844")  # already done
    processed: list[str] = []

    def worker(url: str) -> Path:
        rid = url.rsplit("/", 2)[-2]
        processed.append(rid)
        return _seed_extraction(tmp_path, rid, run_id="fresh")

    urls = [
        "https://www2.jlec-olig.state.oh.us/olac/AERs/1427844/View",  # seeded -> skip
        "https://www2.jlec-olig.state.oh.us/olac/AERs/1459616/View",  # new -> extract
    ]
    results = run_batch(urls, tmp_path, worker)

    by_id = {r.report_id: r for r in results}
    assert by_id["1427844"].status == "skipped"
    assert by_id["1459616"].status == "extracted"
    # The expensive worker did not re-run on the already-extracted filing.
    assert processed == ["1459616"]


def test_run_batch_isolates_a_failing_filing(tmp_path: Path) -> None:
    def worker(url: str) -> Path:
        rid = url.rsplit("/", 2)[-2]
        if rid == "1405684":
            raise RuntimeError("boom: LLM call failed")
        return _seed_extraction(tmp_path, rid, run_id="fresh")

    urls = [
        "https://www2.jlec-olig.state.oh.us/olac/AERs/1405684/View",  # raises
        "https://www2.jlec-olig.state.oh.us/olac/AERs/1459616/View",  # still runs
    ]
    results = run_batch(urls, tmp_path, worker)

    by_id = {r.report_id: r for r in results}
    assert by_id["1405684"].status == "failed"
    assert "boom" in by_id["1405684"].error
    # A failure earlier in the list must not abort filings later in the list.
    assert by_id["1459616"].status == "extracted"
