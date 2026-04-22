"""Load a per-state snapshot bundle from data/portal_snapshots/<STATE>/<DATE>/."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from scoring.models import SnapshotArtifact, SnapshotBundle

SNAPSHOT_DATE_DEFAULT = "2026-04-13"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_snapshot(
    state_abbr: str,
    repo_root: Path,
    snapshot_date: str = SNAPSHOT_DATE_DEFAULT,
) -> SnapshotBundle:
    """Load the manifest.json for one state and return a validated SnapshotBundle.

    Paths in the manifest are repo-root-relative (e.g. `data/portal_snapshots/CA/...`).
    """
    state_dir = repo_root / "data" / "portal_snapshots" / state_abbr / snapshot_date
    manifest_path = state_dir / "manifest.json"
    if not manifest_path.exists():
        raise FileNotFoundError(manifest_path)

    manifest_sha = _sha256(manifest_path)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    artifacts: list[SnapshotArtifact] = []
    for fetch in manifest.get("fetches", []):
        stub = bool(fetch.get("suspicious_challenge_stub", False)) or _looks_like_stub(fetch)
        artifacts.append(
            SnapshotArtifact(
                url=fetch["url"],
                role=fetch.get("role", "unknown"),
                source=fetch.get("source", "seed"),
                http_status=int(fetch.get("http_status", 0)),
                content_type=fetch.get("content_type", ""),
                bytes=int(fetch.get("bytes", 0)),
                sha256=fetch.get("sha256", ""),
                local_path=fetch["local_path"],
                suspicious_challenge_stub=stub,
                notes=fetch.get("notes", ""),
            )
        )

    return SnapshotBundle(
        state_abbr=manifest.get("state_abbr", state_abbr),
        snapshot_date=manifest.get("snapshot_date", snapshot_date),
        artifacts=artifacts,
        manifest_sha=manifest_sha,
        summary=manifest.get("summary", ""),
        skipped=manifest.get("skipped", []),
    )


def _looks_like_stub(fetch: dict) -> bool:
    """Secondary stub heuristic when the manifest hasn't pre-flagged an artifact.

    The Stage-2 snapshot collector pre-populates `suspicious_challenge_stub` on many
    WAF stubs, but not all. Conservative fallback: tiny HTML bodies with an Incapsula
    marker in the note.
    """
    if fetch.get("bytes", 0) < 2048 and "text/html" in fetch.get("content_type", ""):
        return True
    note = (fetch.get("notes") or "").lower()
    if any(tok in note for tok in ("incapsula", "waf", "challenge stub", "cloudflare")):
        return True
    return False
