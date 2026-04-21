"""Load a retrieved statute bundle from data/statutes/<STATE>/<YEAR>/.

Mirrors `snapshot_loader.load_snapshot` in shape: read manifest.json, verify
each artifact's sha256 against the file bytes, return a validated pydantic
StatuteBundle.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from scoring.models import StatuteArtifact, StatuteBundle


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_statute_bundle(bundle_dir: Path, repo_root: Path) -> StatuteBundle:
    """Load manifest.json from `bundle_dir` and return a StatuteBundle.

    Artifact `local_path` values in the manifest are stored relative to
    `bundle_dir` (e.g. `sections/gov-86100-86118.txt`). On load, they are
    normalized to be relative to `repo_root` (e.g.
    `data/statutes/CA/2010/sections/gov-86100-86118.txt`) so that downstream
    consumers (scoring subagent briefs, in particular) can prepend
    `repo_root` and get a path that resolves — mirroring how
    `SnapshotArtifact.local_path` is already stored repo-root-relative.

    Verifies each artifact's sha256 matches the bytes of
    `<bundle_dir>/<manifest local_path>`. Raises FileNotFoundError if
    manifest or an artifact file is missing. Raises ValueError if any
    sha256 doesn't match.
    """
    manifest_path = bundle_dir / "manifest.json"
    if not manifest_path.exists():
        raise FileNotFoundError(manifest_path)

    manifest_sha = _sha256(manifest_path)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    artifacts: list[StatuteArtifact] = []
    for art in manifest.get("artifacts", []):
        file_path = bundle_dir / art["local_path"]
        if not file_path.exists():
            raise FileNotFoundError(file_path)
        actual_sha = _sha256(file_path)
        if actual_sha != art["sha256"]:
            raise ValueError(
                f"sha256 mismatch for {file_path}: "
                f"manifest says {art['sha256']}, file is {actual_sha}"
            )
        artifacts.append(
            StatuteArtifact(
                url=art["url"],
                sha256=art["sha256"],
                bytes=int(art["bytes"]),
                local_path=str(file_path.relative_to(repo_root)),
            )
        )

    return StatuteBundle(
        state_abbr=manifest["state_abbr"],
        vintage_year=int(manifest["vintage_year"]),
        year_delta=int(manifest["year_delta"]),
        direction=manifest["direction"],
        pri_state_reviewed=bool(manifest["pri_state_reviewed"]),
        retrieved_at=manifest["retrieved_at"],
        artifacts=artifacts,
        manifest_sha=manifest_sha,
    )
