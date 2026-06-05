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
    _read_urls,
    find_existing_extraction,
    read_url_regimes,
    run_batch,
    select_legislative,
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


def test_read_urls_extracts_aer_urls_from_discover_tsv(tmp_path: Path) -> None:
    # The discover step emits a rich TSV; batch --file must consume it directly
    # (pull the aer_url column, skip the header) so the two stages pipeline.
    tsv = tmp_path / "recent.tsv"
    tsv.write_text(
        "report_id\tagent\tagent_id\temployer\tyear\treporting_period\tform_type\taer_url\n"
        "1427844\tNathan Aichele\t5272\tARC Gaming\t2025\tMay-Aug25\tAER\t"
        "https://www2.jlec-olig.state.oh.us/olac/AERs/1427844/View\n"
        "1459616\tNathan Aichele\t5272\tHART\t2025\tSep-Dec25\tAER\t"
        "https://www2.jlec-olig.state.oh.us/olac/AERs/1459616/View\n"
    )
    assert _read_urls(["--file", str(tsv)]) == [
        "https://www2.jlec-olig.state.oh.us/olac/AERs/1427844/View",
        "https://www2.jlec-olig.state.oh.us/olac/AERs/1459616/View",
    ]


def test_read_urls_still_accepts_plain_url_list(tmp_path: Path) -> None:
    f = tmp_path / "urls.txt"
    f.write_text(
        "https://www2.jlec-olig.state.oh.us/olac/AERs/1427844/View\n"
        "# a comment line\n"
        "\n"
        "https://www2.jlec-olig.state.oh.us/olac/AERs/1459616/View\n"
    )
    assert _read_urls(["--file", str(f)]) == [
        "https://www2.jlec-olig.state.oh.us/olac/AERs/1427844/View",
        "https://www2.jlec-olig.state.oh.us/olac/AERs/1459616/View",
    ]


def test_read_url_regimes_pairs_each_url_with_its_regime(tmp_path: Path) -> None:
    # The discover TSV now carries a regime column; batch must pair each AER
    # URL with its regime so the right brief (and skip policy) can be applied.
    tsv = tmp_path / "recent.tsv"
    tsv.write_text(
        "report_id\tagent\tagent_id\temployer\tyear\treporting_period\t"
        "form_type\tregime\taer_url\n"
        "1427844\tJane\t5272\tARC\t2025\tMay-Aug25\tAER\texecutive\t"
        "https://www2.jlec-olig.state.oh.us/olac/AERs/1427844/View\n"
        "1492518\tJane\t5272\tALPS\t2026\tJan-Apr26\tAER\tlegislative\t"
        "https://www2.jlec-olig.state.oh.us/olac/AERs/1492518/View\n"
    )
    assert read_url_regimes(["--file", str(tsv)]) == [
        ("https://www2.jlec-olig.state.oh.us/olac/AERs/1427844/View", "executive"),
        ("https://www2.jlec-olig.state.oh.us/olac/AERs/1492518/View", "legislative"),
    ]


def test_read_url_regimes_yields_none_regime_when_column_absent(tmp_path: Path) -> None:
    # An old discover TSV (or a plain URL list) predates the regime column; the
    # regime must come back as None (unknown), never silently "legislative".
    tsv = tmp_path / "old.tsv"
    tsv.write_text(
        "report_id\tagent\tagent_id\temployer\tyear\treporting_period\t"
        "form_type\taer_url\n"
        "1427844\tJane\t5272\tARC\t2025\tMay-Aug25\tAER\t"
        "https://www2.jlec-olig.state.oh.us/olac/AERs/1427844/View\n"
    )
    assert read_url_regimes(["--file", str(tsv)]) == [
        ("https://www2.jlec-olig.state.oh.us/olac/AERs/1427844/View", None),
    ]


def test_select_legislative_drops_non_legislative_by_default() -> None:
    pairs = [
        ("u-leg", "legislative"),
        ("u-exec", "executive"),
        ("u-ret", "retirement_system"),
        ("u-unknown", None),
    ]
    kept, skipped = select_legislative(pairs, include_nonlegislative=False)
    assert kept == [("u-leg", "legislative")]
    assert skipped == 3


def test_select_legislative_keeps_everything_when_flag_set() -> None:
    pairs = [("u-leg", "legislative"), ("u-exec", "executive")]
    kept, skipped = select_legislative(pairs, include_nonlegislative=True)
    assert kept == pairs
    assert skipped == 0
