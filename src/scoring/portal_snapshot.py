"""Stage 2 portal snapshot capture.

Reads a Stage 1 URL-discovery JSON (`compendium/portal_urls/<ABBR>.json`),
fetches each seed URL with a realistic browser UA, saves raw bytes, computes
sha256, and emits a `manifest.json` in the shape `snapshot_loader.load_snapshot`
expects.

The historical Stage 2 was subagent-driven and hit permission/rate issues;
this is the deterministic Python replacement. No LLM in the loop.
"""

from __future__ import annotations

import hashlib
import json
import re
from datetime import date
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import requests

CHROME_UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)

STUB_MARKERS = ("incapsula", "_incapsula_resource", "imperva", "waf", "challenge stub", "cloudflare")
STUB_BYTE_THRESHOLD = 2048
DEFAULT_TIMEOUT_S = 30
DEFAULT_RETRIES = 2
DEFAULT_MAX_BYTES = 100 * 1024 * 1024  # 100 MB cap per artifact


def detect_stub(content_type: str, body: bytes, notes: str = "") -> bool:
    """Return True if the response looks like a WAF challenge stub.

    Mirrors `snapshot_loader._looks_like_stub` semantics so the captured
    manifest pre-flags what the loader would otherwise fall back on.
    """
    if "text/html" in content_type and len(body) < STUB_BYTE_THRESHOLD:
        return True
    blob = (body[:4096].decode("utf-8", errors="ignore") + " " + notes).lower()
    return any(tok in blob for tok in STUB_MARKERS)


_FILENAME_SAFE = re.compile(r"[^a-z0-9._-]+")


def artifact_filename(role: str, index: int, url: str, content_type: str) -> str:
    """Pick a filesystem-safe filename for a fetched artifact.

    Pattern: `<role>_<index>_<urlslug>.<ext>` — preserves provenance back to
    the URL while staying readable.
    """
    parsed = urlparse(url)
    slug = (parsed.path.rstrip("/").split("/")[-1] or parsed.netloc).lower()
    slug = _FILENAME_SAFE.sub("-", slug).strip("-")[:60] or "index"
    if "zip" in content_type:
        ext = "zip"
    elif "pdf" in content_type:
        ext = "pdf"
    elif "json" in content_type:
        ext = "json"
    elif "xml" in content_type:
        ext = "xml"
    elif "csv" in content_type:
        ext = "csv"
    else:
        ext = "html"
    if slug.endswith("." + ext):
        slug = slug[: -(len(ext) + 1)]
    return f"{role}_{index:02d}_{slug}.{ext}"


def fetch_one(
    url: str,
    *,
    timeout_s: int = DEFAULT_TIMEOUT_S,
    retries: int = DEFAULT_RETRIES,
    max_bytes: int = DEFAULT_MAX_BYTES,
) -> tuple[int, str, bytes, str]:
    """Fetch one URL with retries; return (http_status, content_type, body, error_note).

    Streams the body and stops at `max_bytes` (note recorded in error_note).
    Network errors are caught and reported via a non-empty error_note + status=0.
    """
    headers = {"User-Agent": CHROME_UA, "Accept": "*/*"}
    last_exc: Exception | None = None
    for _ in range(retries + 1):
        try:
            with requests.get(url, headers=headers, timeout=timeout_s, stream=True) as resp:
                ct = resp.headers.get("content-type", "")
                buf = bytearray()
                truncated = False
                for chunk in resp.iter_content(chunk_size=64 * 1024):
                    if not chunk:
                        continue
                    if len(buf) + len(chunk) > max_bytes:
                        buf.extend(chunk[: max_bytes - len(buf)])
                        truncated = True
                        break
                    buf.extend(chunk)
                note = f"truncated at max_bytes={max_bytes}" if truncated else ""
                return resp.status_code, ct, bytes(buf), note
        except requests.RequestException as exc:
            last_exc = exc
    return 0, "", b"", f"{type(last_exc).__name__}: {last_exc}"


def capture_state(
    stage1_json: Path,
    output_root: Path,
    snapshot_date: str | None = None,
    repo_root: Path | None = None,
) -> Path:
    """Capture all seed URLs for one state. Returns the path to manifest.json.

    Args:
        stage1_json: Path to `compendium/portal_urls/<ABBR>.json`.
        output_root: Path to `data/portal_snapshots/`.
        snapshot_date: YYYY-MM-DD; defaults to today.
        repo_root: For computing repo-root-relative `local_path` strings in the
            manifest. Defaults to `output_root.parents[1]` (i.e. assumes
            `output_root == <repo>/data/portal_snapshots`).

    Side effect: writes one file per seed URL plus `manifest.json` under
    `output_root/<STATE>/<DATE>/`.
    """
    spec = json.loads(stage1_json.read_text(encoding="utf-8"))
    state = spec["state_abbr"]
    snap_date = snapshot_date or date.today().isoformat()
    if repo_root is None:
        repo_root = output_root.parents[1]

    state_dir = output_root / state / snap_date
    state_dir.mkdir(parents=True, exist_ok=True)

    fetches: list[dict[str, Any]] = []
    for i, seed in enumerate(spec.get("seed_urls", []), start=1):
        url = seed["url"]
        role = seed.get("role", "unknown")
        status, ct, body, err = fetch_one(url)
        is_stub = bool(body) and detect_stub(ct, body, seed.get("notes", ""))
        fname = artifact_filename(role, i, url, ct)
        local_abs = state_dir / fname
        if body:
            local_abs.write_bytes(body)
        sha = hashlib.sha256(body).hexdigest() if body else ""
        local_rel = str(local_abs.relative_to(repo_root))
        fetches.append({
            "url": url,
            "role": role,
            "source": "seed",
            "http_status": status,
            "content_type": ct,
            "bytes": len(body),
            "sha256": sha,
            "local_path": local_rel,
            "suspicious_challenge_stub": is_stub,
            "notes": err or seed.get("notes", ""),
        })

    skipped = [
        {
            "url": entry["url"],
            "role": entry.get("role", "unknown"),
            "reason": entry.get("reason", "flagged at Stage 1"),
            "notes": entry.get("notes", ""),
        }
        for entry in spec.get("flagged", [])
    ]

    summary = (
        f"{state} {snap_date}: {len(fetches)} fetched "
        f"({sum(1 for f in fetches if f['http_status'] == 200)} ok, "
        f"{sum(1 for f in fetches if f['suspicious_challenge_stub'])} stubs), "
        f"{len(skipped)} skipped"
    )

    manifest = {
        "state_abbr": state,
        "snapshot_date": snap_date,
        "portal_system": spec.get("portal_system", ""),
        "regulator": spec.get("regulator", ""),
        "summary": summary,
        "skipped": skipped,
        "fetches": fetches,
    }
    manifest_path = state_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest_path
