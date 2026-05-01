"""Unit tests for the deterministic Stage 2 portal-snapshot helpers.

The actual fetch loop is exercised by running `cmd_capture_snapshots` against a
real Stage 1 JSON; this file just covers the pure helpers (stub detection,
filename derivation) so they're fixed regardless of network conditions.
"""

from __future__ import annotations

from scoring.portal_snapshot import artifact_filename, detect_stub


def test_detect_stub_small_html_body() -> None:
    assert detect_stub("text/html; charset=utf-8", b"<html></html>") is True


def test_detect_stub_large_html_is_not_stub() -> None:
    body = b"<html>" + b"x" * 5000 + b"</html>"
    assert detect_stub("text/html", body) is False


def test_detect_stub_incapsula_marker_in_body() -> None:
    body = b"<html><body>Request unsuccessful. Incapsula incident ID: 1-...</body></html>" + b"x" * 5000
    assert detect_stub("text/html", body) is True


def test_detect_stub_marker_in_notes() -> None:
    body = b"<html>" + b"x" * 5000 + b"</html>"
    assert detect_stub("text/html", body, notes="Cloudflare challenge stub") is True


def test_detect_stub_zip_is_not_stub() -> None:
    assert detect_stub("application/zip", b"\x50\x4b\x03\x04") is False


def test_artifact_filename_html() -> None:
    name = artifact_filename(
        role="search",
        index=3,
        url="https://cal-access.sos.ca.gov/Lobbying/Lobbyists/",
        content_type="text/html; charset=utf-8",
    )
    assert name == "search_03_lobbyists.html"


def test_artifact_filename_zip() -> None:
    name = artifact_filename(
        role="bulk_download",
        index=8,
        url="https://campaignfinance.cdn.sos.ca.gov/dbwebexport.zip",
        content_type="application/zip",
    )
    assert name == "bulk_download_08_dbwebexport.zip"


def test_artifact_filename_strips_unsafe_chars() -> None:
    name = artifact_filename(
        role="statute",
        index=1,
        url="https://leginfo.legislature.ca.gov/faces/codes_displayexpandedbranch.xhtml?tocCode=GOV",
        content_type="text/html",
    )
    assert "?" not in name
    assert name.endswith(".html")
    assert name.startswith("statute_01_")
