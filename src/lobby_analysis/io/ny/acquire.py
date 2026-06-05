"""Phase 1 acquisition for the NY Open NY (Socrata) lobbying pipeline.

Two entry points, by design:

* :func:`download_bulk_csv` — the **primary** path. NY's datasets are
  denormalized ~1,300x (``client_semiannual`` 2025 is 11.2M rows for only
  8,613 filings), so the JSON API cannot be paginated for a full pull. The
  bulk CSV export (``/api/views/<id>/rows.csv?accessType=DOWNLOAD``) is streamed
  to disk with resume-skip and an atomic temp-then-rename, so a truncated
  download is never mistaken for a complete one on the next run.

* :class:`SocrataProbeClient` — a **thin** JSON client for cheap aggregate
  probes only (``$select``/``$group``/``$where`` counts and distinct-value
  checks), never full pulls.

Both surface HTTP failures as a typed :class:`NYAcquisitionError` rather than a
silent partial file or empty list, so a failed acquisition can never be read as
valid data downstream.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Mapping, Protocol

import requests

DATA_NY_BASE = "https://data.ny.gov"
DEFAULT_TIMEOUT = 60
DEFAULT_CHUNK_SIZE = 1 << 20  # 1 MiB


class NYAcquisitionError(RuntimeError):
    """An NY Socrata acquisition request failed (HTTP error or transport)."""


class _SessionLike(Protocol):
    """Structural type for what we need from ``requests.Session`` — also
    satisfied by the test suite's fake sessions."""

    def get(self, url: str, **kwargs: Any) -> Any: ...


def bulk_csv_url(dataset_id: str, *, base_url: str = DATA_NY_BASE) -> str:
    """URL of the full-dataset CSV export for ``dataset_id``."""
    return f"{base_url}/api/views/{dataset_id}/rows.csv?accessType=DOWNLOAD"


def download_bulk_csv(
    dataset_id: str,
    dest_path: Path | str,
    session: _SessionLike,
    *,
    base_url: str = DATA_NY_BASE,
    app_token: str | None = None,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    timeout: float = DEFAULT_TIMEOUT,
    force: bool = False,
) -> Path:
    """Stream the bulk CSV export for ``dataset_id`` to ``dest_path``.

    Resume-skip: if ``dest_path`` already exists and is non-empty, returns it
    without any network traffic (unless ``force``). The download streams to a
    ``<name>.part`` temp file and is renamed onto ``dest_path`` only after the
    full body is written, so an interrupted pull leaves no file that a later
    resume check would treat as complete.

    Raises :class:`NYAcquisitionError` on HTTP failure.
    """
    dest_path = Path(dest_path)
    if not force and dest_path.exists() and dest_path.stat().st_size > 0:
        return dest_path

    headers: dict[str, str] = {}
    if app_token:
        headers["X-App-Token"] = app_token

    url = bulk_csv_url(dataset_id, base_url=base_url)
    response = session.get(url, headers=headers, stream=True, timeout=timeout)
    try:
        response.raise_for_status()
    except requests.HTTPError as exc:
        raise NYAcquisitionError(f"bulk CSV download for {dataset_id} failed: {exc}") from exc

    dest_path.parent.mkdir(parents=True, exist_ok=True)
    part_path = dest_path.parent / (dest_path.name + ".part")
    try:
        with part_path.open("wb") as fh:
            for chunk in response.iter_content(chunk_size=chunk_size):
                if chunk:
                    fh.write(chunk)
    except Exception as exc:  # noqa: BLE001 — clean up the temp, re-raise typed
        part_path.unlink(missing_ok=True)
        raise NYAcquisitionError(
            f"bulk CSV download for {dataset_id} was interrupted: {exc}"
        ) from exc

    os.replace(part_path, dest_path)
    return dest_path


class SocrataProbeClient:
    """Thin JSON client for cheap aggregate probes against ``/resource``.

    Not for full pulls — use :func:`download_bulk_csv` for those. This is for
    counts, distinct-value checks, and coverage probes via SoQL.
    """

    def __init__(
        self,
        session: _SessionLike,
        *,
        base_url: str = DATA_NY_BASE,
        app_token: str | None = None,
        timeout: float = DEFAULT_TIMEOUT,
    ):
        self.session = session
        self.base_url = base_url
        self.app_token = app_token
        self.timeout = timeout

    @classmethod
    def from_env(
        cls,
        session: _SessionLike,
        *,
        base_url: str = DATA_NY_BASE,
        env: Mapping[str, str] | None = None,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> "SocrataProbeClient":
        """Build a client whose app token is read from ``SOCRATA_APP_TOKEN``."""
        env = os.environ if env is None else env
        return cls(
            session,
            base_url=base_url,
            app_token=env.get("SOCRATA_APP_TOKEN"),
            timeout=timeout,
        )

    def query(
        self,
        dataset_id: str,
        *,
        select: str | None = None,
        where: str | None = None,
        group: str | None = None,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        """Run a SoQL query and return the decoded JSON record list.

        Raises :class:`NYAcquisitionError` on HTTP failure (never a silent
        empty list).
        """
        params: dict[str, Any] = {}
        if select is not None:
            params["$select"] = select
        if where is not None:
            params["$where"] = where
        if group is not None:
            params["$group"] = group
        if limit is not None:
            params["$limit"] = limit

        headers: dict[str, str] = {}
        if self.app_token:
            headers["X-App-Token"] = self.app_token

        url = f"{self.base_url}/resource/{dataset_id}.json"
        response = self.session.get(url, params=params, headers=headers, timeout=self.timeout)
        try:
            response.raise_for_status()
        except requests.HTTPError as exc:
            raise NYAcquisitionError(f"probe query on {dataset_id} failed: {exc}") from exc
        return response.json()
