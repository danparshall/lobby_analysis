"""Tests for the single-filing pipeline's regime stamping.

The two external boundaries — the HTTP fetch and the LLM extraction — are
stubbed (they are the network/API edge, not the behavior under test). What IS
tested is the pipeline's own observable output: the `extraction_run.json`
sidecar records the regime it was *given* (not a hardcoded constant), and a
filing run through the legislative brief under a non-legislative regime carries
an explicit warning rather than being silently mislabeled.
"""

import json
from pathlib import Path

import pytest

from lobby_analysis.models.filings import LobbyingFiling
from lobby_analysis.oh_portal import pipeline

_URL = "https://www2.jlec-olig.state.oh.us/olac/AERs/1427844/View"


def _fake_filing() -> LobbyingFiling:
    return LobbyingFiling(
        id="oh-1427844",
        state="OH",
        filing_type="activity_report",
        filer_role="lobbyist",
    )


@pytest.fixture
def stub_boundaries(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """Replace the fetch + LLM-extract edges with local fakes (no network)."""
    html = tmp_path / "raw.html"
    html.write_text("<html><body>AER</body></html>")
    monkeypatch.setattr(pipeline, "fetch_olac_aer", lambda url: html)
    monkeypatch.setattr(
        pipeline,
        "extract_oh_legislative_filing",
        lambda html_path, brief, provenance: _fake_filing(),
    )
    return tmp_path


def test_extract_one_filing_stamps_the_given_regime(stub_boundaries: Path) -> None:
    filing_path = pipeline.extract_one_filing(
        _URL, data_dir=stub_boundaries, regime="executive"
    )
    run_meta = json.loads((filing_path.parent / "extraction_run.json").read_text())
    assert run_meta["regime"] == "executive"


def test_extract_one_filing_defaults_regime_to_legislative(stub_boundaries: Path) -> None:
    # The single-URL CLI path passes no regime; back-compat default is legislative.
    filing_path = pipeline.extract_one_filing(_URL, data_dir=stub_boundaries)
    run_meta = json.loads((filing_path.parent / "extraction_run.json").read_text())
    assert run_meta["regime"] == "legislative"


def test_extract_one_filing_warns_when_run_through_wrong_brief(
    stub_boundaries: Path,
) -> None:
    # An executive AER extracted with the legislative brief must be flagged, not
    # silently accepted — the brief doesn't match the source's regime.
    filing_path = pipeline.extract_one_filing(
        _URL, data_dir=stub_boundaries, regime="executive"
    )
    filing = json.loads(filing_path.read_text())
    assert any("executive" in w for w in filing["extraction_warnings"])


def test_extract_one_filing_legislative_has_no_regime_warning(
    stub_boundaries: Path,
) -> None:
    filing_path = pipeline.extract_one_filing(
        _URL, data_dir=stub_boundaries, regime="legislative"
    )
    filing = json.loads(filing_path.read_text())
    assert filing["extraction_warnings"] == []


def test_extract_one_filing_unknown_regime_warns_as_unknown_not_as_a_brief(
    stub_boundaries: Path,
) -> None:
    # Reachable via --include-nonlegislative over an old/plain URL list: the
    # regime is unknown (None). The warning must say "unknown", not invent a
    # "None brief", and must not silently pass the filing off as legislative.
    filing_path = pipeline.extract_one_filing(
        _URL, data_dir=stub_boundaries, regime=None
    )
    filing = json.loads(filing_path.read_text())
    warnings = filing["extraction_warnings"]
    assert len(warnings) == 1
    assert "unknown" in warnings[0].lower()
    assert "None brief" not in warnings[0]
