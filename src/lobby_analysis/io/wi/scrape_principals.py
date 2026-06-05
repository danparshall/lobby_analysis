"""CLI: scrape the principal-side authorization graph for the
2025-2026 Wisconsin legislative session.

Mirror of ``scrape_authorizations`` for the other endpoint of the
bipartite graph. Discovers the 944-ID principal universe via the
union of ``WI_directory_principals.xls`` and the existing lobbyist-side
auth-graph TSV, then politely fetches each principal's detail page
with checkpoint/resume.

Usage::

    uv run python -m lobby_analysis.io.wi.scrape_principals \\
        [--limit N] \\
        [--delay SECONDS] \\
        [--checkpoint-dir PATH] \\
        [--directory-xls PATH] \\
        [--auth-graph-tsv PATH] \\
        [--session-id 2025REG] \\
        [--output PATH] \\
        [--skip-materialize | --skip-fetch]

Default checkpoint dir:
``/Users/dan/data/lobby_analysis/disclosures/WI/_principal_scrape_checkpoints/``

Resume contract: every per-principal fetch is checkpointed to
``{principal_id}.json`` immediately. Re-running with the same
checkpoint dir picks up where the previous run left off.

Live-portal etiquette: identical to the lobbyist-side scrape — 1.0 s
polite delay, browser-realistic UA, no ``robots.txt`` restrictions
on ``lobbying.wi.gov``.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import requests

from lobby_analysis.io.wi.entity_fetcher import DEFAULT_USER_AGENT
from lobby_analysis.io.wi.principal_fetcher import fetch_or_load_principal
from lobby_analysis.io.wi.principal_id_discovery import discover_principal_ids
from lobby_analysis.io.wi.principal_materialize import (
    iter_authorizations_from_principal_checkpoints,
    write_authorizations_tsv,
)

DEFAULT_CHECKPOINT_DIR = Path(
    "/Users/dan/data/lobby_analysis/disclosures/WI/_principal_scrape_checkpoints"
)
DEFAULT_DIRECTORY_XLS = Path(
    "/Users/dan/data/lobby_analysis/disclosures/WI/WI_directory_principals.xls"
)
DEFAULT_AUTH_GRAPH_TSV = Path(
    "/Users/dan/data/lobby_analysis/disclosures/WI/WI_lobbyist_principal_authorizations.tsv"
)
DEFAULT_OUTPUT_TSV = Path(
    "/Users/dan/data/lobby_analysis/disclosures/WI/"
    "WI_lobbyist_principal_authorizations_principal_side.tsv"
)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Scrape WI principal-side authorization graph."
    )
    ap.add_argument("--limit", type=int, default=None,
                    help="If set, stop after this many principals (sanity check).")
    ap.add_argument("--delay", type=float, default=1.0,
                    help="Polite-sleep seconds between requests (default 1.0).")
    ap.add_argument("--checkpoint-dir", type=Path, default=DEFAULT_CHECKPOINT_DIR)
    ap.add_argument("--directory-xls", type=Path, default=DEFAULT_DIRECTORY_XLS)
    ap.add_argument("--auth-graph-tsv", type=Path, default=DEFAULT_AUTH_GRAPH_TSV)
    ap.add_argument("--session-id", default="2025REG")
    ap.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_TSV,
                    help="Path for the materialized TSV.")
    ap.add_argument("--user-agent", default=DEFAULT_USER_AGENT)
    ap.add_argument("--skip-materialize", action="store_true",
                    help="Skip the post-scrape TSV materialize step.")
    ap.add_argument("--skip-fetch", action="store_true",
                    help="Only materialize from existing checkpoints; no HTTP.")
    ap.add_argument("--prepend-ids", type=int, nargs="*", default=[],
                    help="Principal IDs to scrape FIRST (useful for sanity "
                         "checks — e.g., --prepend-ids 12997 to ensure WCTA "
                         "is in a --limit 10 run).")
    args = ap.parse_args(argv)

    checkpoint_dir: Path = args.checkpoint_dir
    checkpoint_dir.mkdir(parents=True, exist_ok=True)

    session = requests.Session()
    session.headers["User-Agent"] = args.user_agent

    if not args.skip_fetch:
        # Warm cookies with one GET to /Home/Welcome before per-page fetches.
        session.get("https://lobbying.wi.gov/Home/Welcome", timeout=30)

        print("[discover] composing principal universe...", flush=True)
        ids = sorted(discover_principal_ids(
            directory_xls_path=args.directory_xls,
            auth_graph_tsv_path=args.auth_graph_tsv,
        ))
        print(f"[discover] {len(ids)} principal IDs", flush=True)

        # Move --prepend-ids to the front so --limit N is guaranteed to
        # include them. Useful for sanity checks targeting known cases
        # (e.g., the Schlaak / WCTA load-bearing principal 12997).
        if args.prepend_ids:
            prepend = [i for i in args.prepend_ids if i in ids]
            rest = [i for i in ids if i not in args.prepend_ids]
            ids = prepend + rest
            print(f"[discover] {len(prepend)} ID(s) prepended: {prepend}",
                  flush=True)

        if args.limit is not None:
            ids = ids[: args.limit]
            print(f"[scrape] --limit {args.limit} applied; "
                  f"scraping {len(ids)} principals", flush=True)

        t0 = time.monotonic()
        skipped = 0
        fetched = 0
        not_found = 0
        for n, pid in enumerate(ids, start=1):
            checkpoint_file = checkpoint_dir / f"{pid}.json"
            existed_before = checkpoint_file.exists()
            payload = fetch_or_load_principal(
                principal_id=pid,
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
        rows = list(iter_authorizations_from_principal_checkpoints(checkpoint_dir))
        n = write_authorizations_tsv(rows, args.output)
        print(f"[materialize] {n} authorizations written", flush=True)

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
