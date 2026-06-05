"""Materialize the principal-side authorization table from the on-disk
principal checkpoint files.

Mirror of ``authorization_materialize`` for the other endpoint of the
bipartite graph. Same edge schema, same TSV writer; only the
checkpoint key is ``principal_id`` instead of ``lobbyist_id``, and the
HTML is re-parsed via ``parse_principal_authorizations`` instead of
``parse_lobbyist_authorizations``.

The TSV writer (``write_authorizations_tsv``) is re-exported from
``authorization_materialize`` so the principal-side table shares an
exact schema with the lobbyist-side table — a hard requirement for
the unification step that compares rows from both sides.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterator

from lobby_analysis.io.wi.authorization_materialize import (
    write_authorizations_tsv,  # noqa: F401  (re-exported)
)
from lobby_analysis.io.wi.authorization_parser import Authorization
from lobby_analysis.io.wi.principal_parser import parse_principal_authorizations


def iter_authorizations_from_principal_checkpoints(
    checkpoint_dir: Path,
) -> Iterator[Authorization]:
    """Yield every ``Authorization`` parsed out of every ``{id}.json``
    principal-side checkpoint in ``checkpoint_dir`` (sorted by
    principal_id for deterministic output)."""
    checkpoint_dir = Path(checkpoint_dir)
    if not checkpoint_dir.exists():
        return

    checkpoint_files = sorted(
        checkpoint_dir.glob("*.json"),
        key=lambda p: int(p.stem) if p.stem.isdigit() else 10**9,
    )
    for path in checkpoint_files:
        if not path.stem.isdigit():
            continue
        with path.open("r", encoding="utf-8") as fh:
            payload = json.load(fh)
        html = payload.get("html")
        if html is None:
            continue
        principal_id = int(payload["principal_id"])
        yield from parse_principal_authorizations(html, principal_id=principal_id)
