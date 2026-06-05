"""Behavior tests for the NY Phase 1 acquisition layer (``io/ny/acquire``).

NY's Open NY (Socrata) datasets are denormalized ~1,300x — ``client_semiannual``
2025 alone is 11.2M rows / 8,613 filings — so the JSON API cannot be paginated
for a full pull. The primary acquisition path is therefore the bulk CSV export
(``/api/views/<id>/rows.csv?accessType=DOWNLOAD``), streamed to disk with
resume-skip and an atomic temp-then-rename so a truncated download is never
mistaken for a complete one. A thin JSON probe client is kept only for cheap
aggregate checks ($select/$group/$where), never full pulls.

These tests mock ``requests`` at the transport boundary (the fake session) and
assert on *behavior*: the bytes that land on disk, that a present file short-
circuits the network, that an HTTP error surfaces as a typed exception and
leaves no file behind, and that SoQL params/app-token headers pass through
verbatim. No test asserts merely "the mock was called".
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
import requests

from lobby_analysis.io.ny.acquire import (
    NYAcquisitionError,
    SocrataProbeClient,
    bulk_csv_url,
    download_bulk_csv,
)


# --------------------------------------------------------------------------- #
# Fakes at the requests transport boundary
# --------------------------------------------------------------------------- #
class _FakeResponse:
    """Stands in for a ``requests.Response``.

    Supports both the streaming path (``iter_content``) used by the bulk CSV
    downloader and the JSON path (``json``) used by the probe client.
    """

    def __init__(
        self,
        status_code: int = 200,
        *,
        chunks: list[bytes] | None = None,
        json_body: Any = None,
    ):
        self.status_code = status_code
        self._chunks = chunks or []
        self._json_body = json_body

    def raise_for_status(self) -> None:
        if 400 <= self.status_code < 600:
            raise requests.HTTPError(f"status {self.status_code}", response=self)  # type: ignore[arg-type]

    def iter_content(self, chunk_size: int = 1):  # noqa: ARG002
        yield from self._chunks

    def json(self) -> Any:
        return self._json_body


class _FakeSession:
    """Returns canned responses in order and records each call's url / params /
    headers so passthrough behavior can be asserted."""

    def __init__(self, responses: list[_FakeResponse]):
        self._responses = list(responses)
        self.calls: list[dict[str, Any]] = []

    def get(self, url: str, **kwargs: Any):
        self.calls.append({"url": url, **kwargs})
        if not self._responses:
            raise AssertionError(
                f"Unexpected network call to {url} — fake session ran out of "
                "canned responses (tripwire)."
            )
        return self._responses.pop(0)


class _NoNetworkSession:
    """Any network call is a test failure — used to prove the resume-skip path
    never touches the network when the file already exists."""

    def get(self, url: str, **kwargs: Any):  # noqa: ARG002
        raise AssertionError(
            f"Network was hit for {url} but the file already existed on disk "
            "(resume-skip should have short-circuited)."
        )


# --------------------------------------------------------------------------- #
# bulk_csv_url
# --------------------------------------------------------------------------- #
def test_bulk_csv_url_targets_socrata_download_export():
    """The bulk path must hit the ``/api/views/<id>/rows.csv`` export endpoint
    with ``accessType=DOWNLOAD`` — the full-dataset export, distinct from the
    paginated ``/resource/<id>.json`` API the probe client uses."""
    url = bulk_csv_url("qym9-xzj6")

    assert url == ("https://data.ny.gov/api/views/qym9-xzj6/rows.csv?accessType=DOWNLOAD")


# --------------------------------------------------------------------------- #
# download_bulk_csv
# --------------------------------------------------------------------------- #
def test_download_bulk_csv_streams_full_body_to_dest(tmp_path: Path):
    """A multi-chunk streamed response must be reassembled byte-for-byte on
    disk — this is the core acquisition behavior, not an implementation
    detail."""
    dest = tmp_path / "2025" / "client_semiannual.csv"
    session = _FakeSession([_FakeResponse(200, chunks=[b"col_a,col_b\n", b"1,2\n", b"3,4\n"])])

    result = download_bulk_csv("qym9-xzj6", dest, session)

    assert result == dest
    assert dest.read_bytes() == b"col_a,col_b\n1,2\n3,4\n"


def test_download_bulk_csv_skips_when_file_already_present(tmp_path: Path):
    """Resume discipline: a non-empty file on disk short-circuits with zero
    network traffic, so a re-run never re-pulls an 11M-row dataset."""
    dest = tmp_path / "client_semiannual.csv"
    dest.write_bytes(b"already,here\n9,9\n")

    result = download_bulk_csv("qym9-xzj6", dest, _NoNetworkSession())

    assert result == dest
    assert dest.read_bytes() == b"already,here\n9,9\n"


def test_download_bulk_csv_force_redownloads_existing_file(tmp_path: Path):
    """``force=True`` overrides resume-skip and re-pulls, so a known-stale
    file can be deliberately refreshed."""
    dest = tmp_path / "client_semiannual.csv"
    dest.write_bytes(b"stale,row\n0,0\n")
    session = _FakeSession([_FakeResponse(200, chunks=[b"fresh,row\n1,1\n"])])

    download_bulk_csv("qym9-xzj6", dest, session, force=True)

    assert dest.read_bytes() == b"fresh,row\n1,1\n"


def test_download_bulk_csv_http_error_is_typed_and_leaves_no_file(tmp_path: Path):
    """An HTTP error must surface as ``NYAcquisitionError`` (never a silent
    partial file), and the atomic temp-then-rename must leave neither the
    final file nor the ``.part`` temp behind — so a failed pull can never be
    mistaken for a complete one on the next resume check."""
    dest = tmp_path / "client_semiannual.csv"
    session = _FakeSession([_FakeResponse(500)])

    with pytest.raises(NYAcquisitionError):
        download_bulk_csv("qym9-xzj6", dest, session)

    assert not dest.exists()
    assert not (tmp_path / "client_semiannual.csv.part").exists()


def test_download_bulk_csv_sends_app_token_header(tmp_path: Path):
    """When an app token is configured it must ride on the export request as
    ``X-App-Token`` (Socrata raises the throttle ceiling for tokened
    requests)."""
    dest = tmp_path / "client_semiannual.csv"
    session = _FakeSession([_FakeResponse(200, chunks=[b"a\n1\n"])])

    download_bulk_csv("qym9-xzj6", dest, session, app_token="tok-123")

    assert session.calls[0]["headers"]["X-App-Token"] == "tok-123"


# --------------------------------------------------------------------------- #
# SocrataProbeClient
# --------------------------------------------------------------------------- #
def test_probe_client_passes_soql_params_verbatim():
    """The probe client must forward ``$select``/``$where``/``$group``/``$limit``
    exactly as given — Phase 0's grain + bill-share probes depend on the SoQL
    reaching Socrata unmodified."""
    session = _FakeSession([_FakeResponse(200, json_body=[{"n": "8613"}])])
    client = SocrataProbeClient(session)

    client.query(
        "qym9-xzj6",
        select="count(distinct form_submission_id) as n",
        where="reporting_year='2025'",
        group="reporting_period",
        limit=5,
    )

    params = session.calls[0]["params"]
    assert params["$select"] == "count(distinct form_submission_id) as n"
    assert params["$where"] == "reporting_year='2025'"
    assert params["$group"] == "reporting_period"
    assert params["$limit"] == 5


def test_probe_client_returns_parsed_records():
    """A successful probe returns the decoded JSON record list — the caller
    works with parsed rows, not a raw response object."""
    session = _FakeSession([_FakeResponse(200, json_body=[{"n": "8613"}, {"n": "4376"}])])
    client = SocrataProbeClient(session)

    rows = client.query("qym9-xzj6", select="count(*) as n")

    assert rows == [{"n": "8613"}, {"n": "4376"}]


def test_probe_client_http_error_is_typed_not_silent_empty():
    """An HTTP failure must raise ``NYAcquisitionError``, never degrade to an
    empty list — a silent empty result would be read as 'zero rows' and
    corrupt a grain/coverage probe."""
    session = _FakeSession([_FakeResponse(503)])
    client = SocrataProbeClient(session)

    with pytest.raises(NYAcquisitionError):
        client.query("qym9-xzj6", select="count(*) as n")


def test_probe_client_from_env_reads_socrata_app_token():
    """``from_env`` reads ``SOCRATA_APP_TOKEN`` and the resulting client sends
    it as ``X-App-Token`` — so credentials come from the environment, not
    hardcoded call sites."""
    session = _FakeSession([_FakeResponse(200, json_body=[])])
    client = SocrataProbeClient.from_env(session, env={"SOCRATA_APP_TOKEN": "env-tok-xyz"})

    client.query("qym9-xzj6", select="count(*) as n")

    assert session.calls[0]["headers"]["X-App-Token"] == "env-tok-xyz"
