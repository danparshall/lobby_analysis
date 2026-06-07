"""Phase 1 acquisition for the NY Open NY (Socrata) lobbying pipeline.

Two CSV download paths and a probe client, by design:

* :func:`download_resource_csv` — the **primary path for pipeline pulls**. Hits
  the SODA ``/resource/<id>.csv`` endpoint, accepts SoQL
  ``$select``/``$where``/``$order``/``$limit``, and returns *field-name* headers
  (``form_submission_id``) — the headers ``columns.COLUMN_MAPS`` and
  ``grain.collapse_to_filing_grain`` actually expect. Streams to disk with the
  same resume-skip + atomic temp-then-rename guarantees as
  :func:`download_bulk_csv`.

* :func:`download_bulk_csv` — **whole-view archival dump only, not pipeline
  input**. Hits ``/api/views/<id>/rows.csv?accessType=DOWNLOAD`` which has no
  ``$where`` and returns *display-name* headers (``Form Submission ID``). For
  a multi-year denormalized view like ``qym9-xzj6`` (66.9M rows, ~55 GB), it's
  also operationally infeasible — kept here because the streaming /
  resume-skip / atomic-rename machinery is sound for any future whole-view
  archival use, but never feed its output to the pipeline (#39).

* :class:`SocrataProbeClient` — a **thin** JSON client for cheap aggregate
  probes only (``$select``/``$group``/``$where`` counts and distinct-value
  checks), never full pulls.

All three surface HTTP failures as a typed :class:`NYAcquisitionError` rather
than a silent partial file or empty list, so a failed acquisition can never be
read as valid data downstream.
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
    """URL of the full-dataset CSV export for ``dataset_id``.

    WARNING: this whole-view export returns *every* row and column with
    *human-readable display headers* (``Form Submission ID``), not the SODA
    field names (``form_submission_id``) the column-map and grain steps expect.
    For a year-scoped, column-projected pull whose headers feed the pipeline,
    use :func:`download_resource_csv` against :func:`resource_csv_url` instead.
    """
    return f"{base_url}/api/views/{dataset_id}/rows.csv?accessType=DOWNLOAD"


def resource_csv_url(dataset_id: str, *, base_url: str = DATA_NY_BASE) -> str:
    """URL of the SODA ``/resource/<id>.csv`` endpoint for ``dataset_id``.

    Unlike :func:`bulk_csv_url` (the whole-view export), this endpoint accepts
    SoQL ``$select``/``$where``/``$order``/``$limit`` and returns SODA
    *field-name* headers — so a filtered, column-projected pull lands on disk
    with the exact column names the downstream column-map expects.
    """
    return f"{base_url}/resource/{dataset_id}.csv"


def _stream_to_dest(
    url: str,
    dest_path: Path,
    session: _SessionLike,
    *,
    params: Mapping[str, Any] | None,
    app_token: str | None,
    chunk_size: int,
    timeout: float,
    what: str,
) -> Path:
    """Stream a GET body to ``dest_path`` atomically.

    Writes to ``<name>.part`` and renames onto ``dest_path`` only after the full
    body is written, so an interrupted pull never leaves a file a later
    resume-skip check would treat as complete. HTTP/transport failures surface
    as :class:`NYAcquisitionError`.
    """
    headers: dict[str, str] = {}
    if app_token:
        headers["X-App-Token"] = app_token

    get_kwargs: dict[str, Any] = {"headers": headers, "stream": True, "timeout": timeout}
    if params is not None:
        get_kwargs["params"] = params

    response = session.get(url, **get_kwargs)
    try:
        response.raise_for_status()
    except requests.HTTPError as exc:
        raise NYAcquisitionError(f"{what} failed: {exc}") from exc

    dest_path.parent.mkdir(parents=True, exist_ok=True)
    part_path = dest_path.parent / (dest_path.name + ".part")
    try:
        with part_path.open("wb") as fh:
            for chunk in response.iter_content(chunk_size=chunk_size):
                if chunk:
                    fh.write(chunk)
    except Exception as exc:  # noqa: BLE001 — clean up the temp, re-raise typed
        part_path.unlink(missing_ok=True)
        raise NYAcquisitionError(f"{what} was interrupted: {exc}") from exc

    os.replace(part_path, dest_path)
    return dest_path


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
    """Stream the whole-view CSV export for ``dataset_id`` to ``dest_path``.

    **Archival use only — not a pipeline input.** The bulk export emits
    *display-name* headers (``Form Submission ID``), not the SODA field names
    (``form_submission_id``) the column-map / grain steps require. It also has
    no ``$where``, so a year-scoped pull through this endpoint is impossible —
    operationally infeasible for the denormalized multi-year views NY ships
    (#39). For pipeline pulls, use :func:`download_resource_csv` against
    :func:`resource_csv_url`.

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

    return _stream_to_dest(
        bulk_csv_url(dataset_id, base_url=base_url),
        dest_path,
        session,
        params=None,
        app_token=app_token,
        chunk_size=chunk_size,
        timeout=timeout,
        what=f"bulk CSV download for {dataset_id}",
    )


def download_resource_csv(
    dataset_id: str,
    dest_path: Path | str,
    session: _SessionLike,
    *,
    select: str,
    where: str | None = None,
    order_by: str | None = None,
    limit: int | None = None,
    base_url: str = DATA_NY_BASE,
    app_token: str | None = None,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    timeout: float = DEFAULT_TIMEOUT,
    force: bool = False,
) -> Path:
    """Stream a filtered/projected SODA ``/resource/<id>.csv`` pull to ``dest_path``.

    **The primary path for pipeline pulls.** Returns pipeline-compatible
    field-name headers (``form_submission_id``) and accepts ``$where`` for
    year-scoping (essential — the bulk-view path covers all years at once and
    is infeasible at NY's denormalization, see :func:`download_bulk_csv`).
    ``select`` is required (always project columns explicitly so the on-disk
    schema is intentional, not whatever the view happens to expose);
    ``where``/``order_by``/``limit`` map to ``$where`` / ``$order`` /
    ``$limit`` and are sent only when set.

    Resume-skip, atomic temp-then-rename, and typed :class:`NYAcquisitionError`
    behave exactly as :func:`download_bulk_csv`. Set ``limit`` above the known
    row count for a full single-request stream; verify the on-disk row count
    against a cheap ``count(*)`` probe afterward, since a silent server-side cap
    would otherwise look like a complete pull.
    """
    dest_path = Path(dest_path)
    if not force and dest_path.exists() and dest_path.stat().st_size > 0:
        return dest_path

    params: dict[str, Any] = {"$select": select}
    if where is not None:
        params["$where"] = where
    if order_by is not None:
        params["$order"] = order_by
    if limit is not None:
        params["$limit"] = limit

    return _stream_to_dest(
        resource_csv_url(dataset_id, base_url=base_url),
        dest_path,
        session,
        params=params,
        app_token=app_token,
        chunk_size=chunk_size,
        timeout=timeout,
        what=f"resource CSV download for {dataset_id}",
    )


class SocrataProbeClient:
    """Thin JSON client for cheap aggregate probes against ``/resource``.

    Not for full pulls — use :func:`download_resource_csv` for those. This is
    for counts, distinct-value checks, and coverage probes via SoQL.
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
