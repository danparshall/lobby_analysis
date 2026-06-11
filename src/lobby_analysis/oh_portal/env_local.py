"""Minimal .env.local loader (no third-party dependency).

The extraction CLIs need ANTHROPIC_API_KEY in the environment. Rather than
require a wrapper that sources .env.local, the CLIs call load_env_local() so
the committed pipeline runs reproducibly from a clean shell. Only keys NOT
already set in the environment are populated (an explicit `export FOO=...`
wins over the file).
"""

from __future__ import annotations

import os
from pathlib import Path

# repo root: .../src/lobby_analysis/oh_portal/env_local.py -> parents[3]
REPO_ROOT = Path(__file__).resolve().parents[3]


def load_env_local(path: Path | None = None) -> bool:
    """Load KEY=VALUE lines from .env.local into os.environ. Returns True if the
    file was found. Existing env vars are not overwritten."""
    p = path or (REPO_ROOT / ".env.local")
    if not p.exists():
        return False
    for line in p.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export "):]
        if "=" not in line:
            continue
        key, _, val = line.partition("=")
        key = key.strip()
        val = val.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = val
    return True
