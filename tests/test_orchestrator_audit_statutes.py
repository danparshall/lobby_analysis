"""Integration tests for the `orchestrator audit-statutes` subcommand."""

from __future__ import annotations

import csv
from pathlib import Path

import pytest

from scoring.statute_retrieval import run_audit_to_csv

FIXTURES_DIR = Path(__file__).parent / "fixtures" / "justia"


class FakeClient:
    def __init__(self, url_to_html: dict[str, str]) -> None:
        self._pages = url_to_html

    def fetch_page(self, url: str) -> str:
        if url not in self._pages:
            raise KeyError(f"FakeClient has no response for {url}")
        return self._pages[url]


def _load(name: str) -> str:
    return (FIXTURES_DIR / name).read_text(encoding="utf-8")


def test_run_audit_to_csv_produces_expected_rows(tmp_path: Path) -> None:
    # 2-state audit: CA (has 2010) and CO (doesn't).
    client = FakeClient({
        "https://law.justia.com/codes/california/": _load("california_index.html"),
        "https://law.justia.com/codes/colorado/": _load("colorado_index.html"),
    })
    out_csv = tmp_path / "audit.csv"
    run_audit_to_csv(
        client=client,
        states=["CA", "CO"],
        target_year=2010,
        tolerance=2,
        out_path=out_csv,
    )
    assert out_csv.exists()
    with out_csv.open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 2

    ca = next(r for r in rows if r["state_abbr"] == "CA")
    assert ca["chosen_year"] == "2010"
    assert ca["year_delta"] == "0"
    assert ca["direction"] == "exact"
    assert ca["eligible_for_calibration"] == "True"
    assert ca["eligible_for_2026_scoring"] == "True"
    assert ca["pri_state_reviewed"] == "True"

    co = next(r for r in rows if r["state_abbr"] == "CO")
    assert co["chosen_year"] == ""  # None → empty cell
    assert co["direction"] == "none"
    assert co["eligible_for_calibration"] == "False"
    assert co["eligible_for_2026_scoring"] == "True"
    assert co["pri_state_reviewed"] == "True"  # CO responded to PRI


def test_run_audit_to_csv_headers_match_contract(tmp_path: Path) -> None:
    client = FakeClient({
        "https://law.justia.com/codes/california/": _load("california_index.html"),
    })
    out_csv = tmp_path / "audit.csv"
    run_audit_to_csv(
        client=client,
        states=["CA"],
        target_year=2010,
        tolerance=2,
        out_path=out_csv,
    )
    with out_csv.open(encoding="utf-8") as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames
    expected = [
        "state_abbr",
        "target_year",
        "chosen_year",
        "year_delta",
        "direction",
        "current_year",
        "eligible_for_calibration",
        "eligible_for_2026_scoring",
        "pri_state_reviewed",
        "n_available_years",
        "min_available_year",
        "max_available_year",
    ]
    assert headers == expected


def test_run_audit_to_csv_logs_progress(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    client = FakeClient({
        "https://law.justia.com/codes/california/": _load("california_index.html"),
    })
    out_csv = tmp_path / "audit.csv"
    run_audit_to_csv(
        client=client,
        states=["CA"],
        target_year=2010,
        tolerance=2,
        out_path=out_csv,
    )
    captured = capsys.readouterr()
    # Progress output includes the state abbr.
    assert "CA" in captured.out
