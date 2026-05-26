"""CLI: scrape the lobbyist↔principal authorization graph for the
2025-2026 Wisconsin legislative session.

Usage::

    uv run python -m lobby_analysis.io.wi.scrape_authorizations \\
        [--limit N] \\
        [--delay SECONDS] \\
        [--checkpoint-dir PATH] \\
        [--session-id 2025REG] \\
        [--output PATH] \\
        [--skip-materialize]

Default checkpoint dir:
``/Users/dan/data/lobby_analysis/disclosures/WI/_authorization_scrape_checkpoints/``

Resume contract: every per-lobbyist fetch is checkpointed to
``{lobbyist_id}.json`` immediately. Re-running with the same
checkpoint dir picks up where the previous run left off.

Discovery is also checkpointed: the LobbyistList grid HTML is saved
to ``_lobbyist_grid_{session_id}.html`` in the checkpoint dir on the
first run. Subsequent runs reuse it. Delete that file to force
re-discovery.

Live-portal etiquette:
* ``--delay`` defaults to 1.0 s between requests (politeness floor).
* Browser-realistic User-Agent (verified working in the originating
  convo's curl probes).
* No ``robots.txt`` at ``lobbying.wi.gov`` (server returns 404 HTML)
  — confirmed 2026-05-26, no machine-readable restriction.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import requests

from lobby_analysis.io.wi.authorization_fetcher import (
    DEFAULT_USER_AGENT,
    fetch_or_load,
)
from lobby_analysis.io.wi.authorization_materialize import (
    iter_authorizations_from_checkpoints,
    write_authorizations_tsv,
)
from lobby_analysis.io.wi.lobbyist_id_discovery import (
    fetch_lobbyist_grid_html,
    parse_lobbyist_ids,
)

DEFAULT_CHECKPOINT_DIR = Path(
    "/Users/dan/data/lobby_analysis/disclosures/WI/_authorization_scrape_checkpoints"
)
DEFAULT_OUTPUT_TSV = Path(
    "/Users/dan/data/lobby_analysis/disclosures/WI/WI_lobbyist_principal_authorizations.tsv"
)


def _discover_or_load_grid(
    session: requests.Session,
    checkpoint_dir: Path,
    session_id: str,
    user_agent: str,
) -> list[int]:
    grid_cache = checkpoint_dir / f"_lobbyist_grid_{session_id}.html"
    if grid_cache.exists():
        html = grid_cache.read_text(encoding="utf-8")
    else:
        html = fetch_lobbyist_grid_html(
            session, session_id=session_id, user_agent=user_agent
        )
        checkpoint_dir.mkdir(parents=True, exist_ok=True)
        grid_cache.write_text(html, encoding="utf-8")
    return parse_lobbyist_ids(html)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Scrape WI lobbyist↔principal authorization graph."
    )
    ap.add_argument("--limit", type=int, default=None,
                    help="If set, stop after this many lobbyists (sanity check).")
    ap.add_argument("--delay", type=float, default=1.0,
                    help="Polite-sleep seconds between requests (default 1.0).")
    ap.add_argument("--checkpoint-dir", type=Path, default=DEFAULT_CHECKPOINT_DIR)
    ap.add_argument("--session-id", default="2025REG")
    ap.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_TSV,
                    help="Path for the materialized TSV.")
    ap.add_argument("--user-agent", default=DEFAULT_USER_AGENT)
    ap.add_argument("--skip-materialize", action="store_true",
                    help="Skip the post-scrape TSV materialize step.")
    ap.add_argument("--skip-fetch", action="store_true",
                    help="Only materialize from existing checkpoints; no HTTP.")
    args = ap.parse_args(argv)

    checkpoint_dir: Path = args.checkpoint_dir
    checkpoint_dir.mkdir(parents=True, exist_ok=True)

    session = requests.Session()
    session.headers["User-Agent"] = args.user_agent

    if not args.skip_fetch:
        # Warm cookies with one GET to /Home/Welcome before AJAX POST.
        session.get("https://lobbying.wi.gov/Home/Welcome", timeout=30)

        print("[discover] resolving lobbyist IDs...", flush=True)
        ids = _discover_or_load_grid(
            session, checkpoint_dir, args.session_id, args.user_agent
        )
        print(f"[discover] {len(ids)} lobbyist IDs", flush=True)

        if args.limit is not None:
            ids = ids[: args.limit]
            print(f"[scrape] --limit {args.limit} applied; "
                  f"scraping {len(ids)} lobbyists", flush=True)

        t0 = time.monotonic()
        skipped = 0
        fetched = 0
        not_found = 0
        for n, lid in enumerate(ids, start=1):
            checkpoint_file = checkpoint_dir / f"{lid}.json"
            existed_before = checkpoint_file.exists()
            payload = fetch_or_load(
                lobbyist_id=lid,
                checkpoint_dir=checkpoint_dir,
                session=session,
                delay=args.delay,
                session_id=args.session_id,
                user_agent=args.user_agent,
            )
            if existed_before:
                skipped += 1
            else:
                fetched += 1
                if payload.get("status_code") == 404:
                    not_found += 1
            if n % 25 == 0 or n == len(ids):
                elapsed = time.monotonic() - t0
                print(f"[scrape] {n}/{len(ids)} "
                      f"(fetched={fetched} skipped={skipped} 404={not_found}) "
                      f"elapsed={elapsed:.1f}s",
                      flush=True)

    if not args.skip_materialize:
        print(f"[materialize] writing TSV to {args.output}", flush=True)
        rows = list(iter_authorizations_from_checkpoints(checkpoint_dir))
        n = write_authorizations_tsv(rows, args.output)
        print(f"[materialize] {n} authorizations written", flush=True)

        # Quick stats for the operator.
        unique_lobbyists = len({r.lobbyist_id for r in rows})
        unique_principals = len({r.principal_id for r in rows})
        print(json.dumps({
            "rows": n,
            "unique_lobbyists": unique_lobbyists,
            "unique_principals": unique_principals,
        }), flush=True)

    return 0


if __name__ == "__main__":
    sys.exit(main())
