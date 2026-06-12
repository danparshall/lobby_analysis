"""Phase 0: chain x parties_lobbied grain-join sanity check.

Confirms the join geometry between ``NY_chain_2025.tsv`` and
``NY_filing_parties_lobbied.tsv`` before any Phase-1 code is written.

Gating expectation (per `plans/ny_chain_completion_sketch.md`): at least 90% of
chain rows should have ≥1 resolved disclosed lawmaker in the same join group;
otherwise STOP and root-cause before Phase 1.

The plan suggested ``(filing_id, lobbyist_id)`` as the join key. We compute
coverage under **two** candidate keys and report both, because Caveat 10 of
``releases/ny/README.md`` says the disclosed party attaches at the
*client-submission* level (not per firm), so ``client_id`` might or might not
matter. The numbers will tell us:

- Key A: ``(filing_id, lobbyist_id)`` — the plan's default.
- Key B: ``(filing_id, lobbyist_id, client_id)`` — the chain's existing cell-
  identity key. If A and B give the same coverage, ``client_id`` is redundant
  for this join. If they diverge, Phase 1 must be written against B.

Outputs:

- A short summary printed to stdout (counts + coverage under both keys).
- A markdown results doc at
  ``docs/active/ny-disclosure-explore/results/<YYYYMMDD>_ny_chain_pl_grain_check.md``.

Run::

    uv run --active python scripts/ny_chain_pl_grain_check.py \\
        --chain releases/ny/chain/NY_chain_2025.tsv \\
        --parties releases/ny/NY_filing_parties_lobbied.tsv \\
        [--results-dir docs/active/ny-disclosure-explore/results]

Both inputs are gitignored release artifacts; this script does no I/O against
``data.ny.gov``. It is read-only against the release dir + write-only into the
results dir.
"""

from __future__ import annotations

import argparse
import csv
import sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path


def _load_chain_keys(path: Path) -> tuple[list[tuple[str, str]], list[tuple[str, str, str]], int]:
    """Return ``(key_A_rows, key_B_rows, total_rows)``.

    ``key_A_rows`` is one entry per chain row keyed ``(filing_id, lobbyist_id)``;
    ``key_B_rows`` the same row keyed ``(filing_id, lobbyist_id, client_id)``.
    The two lists are aligned (same length, same order).
    """
    key_a: list[tuple[str, str]] = []
    key_b: list[tuple[str, str, str]] = []
    with path.open(encoding="utf-8") as fh:
        reader = csv.DictReader(fh, delimiter="\t")
        for row in reader:
            f, lo, cl = row["filing_id"], row["lobbyist_id"], row["client_id"]
            key_a.append((f, lo))
            key_b.append((f, lo, cl))
    return key_a, key_b, len(key_a)


def _load_parties_index(
    path: Path,
) -> tuple[dict[tuple[str, str], set[str]], dict[tuple[str, str, str], set[str]], int, int]:
    """Return two indices + raw counts.

    Index A: ``(filing_id, lobbyist_id) -> set(resolved person_id)``.
    Index B: ``(filing_id, lobbyist_id, client_id) -> set(resolved person_id)``.
    Counts: ``(n_total_party_rows, n_resolved_party_rows)``.

    Unresolved rows (``resolved=False``) are intentionally NOT added to the sets,
    because Phase 1's coverage metric is specifically about *resolved* disclosed
    lawmakers (the rows that could attach an ``ocd-person`` to the chain).
    """
    a: dict[tuple[str, str], set[str]] = defaultdict(set)
    b: dict[tuple[str, str, str], set[str]] = defaultdict(set)
    n_total = 0
    n_resolved = 0
    with path.open(encoding="utf-8") as fh:
        reader = csv.DictReader(fh, delimiter="\t")
        for row in reader:
            n_total += 1
            if row.get("resolved", "").strip().lower() != "true":
                continue
            pid = (row.get("party_lobbied_person_id") or "").strip()
            if not pid:
                continue
            n_resolved += 1
            f, lo, cl = row["filing_id"], row["lobbyist_id"], row["client_id"]
            a[(f, lo)].add(pid)
            b[(f, lo, cl)].add(pid)
    return a, b, n_total, n_resolved


def _decile_table(values: list[int]) -> list[tuple[int, int]]:
    """``[(percentile, value), ...]`` at 10/25/50/75/90/95/99/100."""
    if not values:
        return []
    s = sorted(values)
    n = len(s)
    def q(p: int) -> int:
        # Lower-rank quantile, 0-indexed; clamps to last
        idx = min(n - 1, (p * n) // 100)
        return s[idx]
    return [(p, q(p)) for p in (10, 25, 50, 75, 90, 95, 99, 100)]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n", 1)[0])
    ap.add_argument("--chain", type=Path, required=True,
                    help="Path to NY_chain_2025.tsv (the gitignored chain artifact).")
    ap.add_argument("--parties", type=Path, required=True,
                    help="Path to NY_filing_parties_lobbied.tsv (the gitignored disclosed-edge artifact).")
    ap.add_argument(
        "--results-dir", type=Path,
        default=Path("docs/active/ny-disclosure-explore/results"),
        help="Where to write the markdown results doc.",
    )
    ap.add_argument("--stamp", default=date.today().strftime("%Y%m%d"),
                    help="Date stamp for the results filename (default: today).")
    args = ap.parse_args(argv)

    if not args.chain.exists():
        print(f"ERROR: chain not found at {args.chain}", file=sys.stderr)
        return 2
    if not args.parties.exists():
        print(f"ERROR: parties not found at {args.parties}", file=sys.stderr)
        return 2

    print(f"[phase0] loading chain: {args.chain}", flush=True)
    key_a, key_b, n_chain = _load_chain_keys(args.chain)
    print(f"[phase0]   chain rows: {n_chain:,}", flush=True)

    print(f"[phase0] loading parties: {args.parties}", flush=True)
    idx_a, idx_b, n_party_total, n_party_resolved = _load_parties_index(args.parties)
    print(f"[phase0]   parties rows: {n_party_total:,} ({n_party_resolved:,} resolved)", flush=True)

    # Coverage: fraction of chain rows whose join group has ≥1 resolved person.
    cov_a = sum(1 for k in key_a if idx_a.get(k))
    cov_b = sum(1 for k in key_b if idx_b.get(k))
    pct_a = 100.0 * cov_a / n_chain if n_chain else 0.0
    pct_b = 100.0 * cov_b / n_chain if n_chain else 0.0

    # Fan-out: how many distinct resolved persons per chain row's join group.
    fan_a = [len(idx_a.get(k, ())) for k in key_a]
    fan_b = [len(idx_b.get(k, ())) for k in key_b]
    fan_a_deciles = _decile_table(fan_a)
    fan_b_deciles = _decile_table(fan_b)

    # Group cardinality: how many chain rows share each join key.
    grp_a_counts = Counter(key_a)
    grp_b_counts = Counter(key_b)
    n_groups_a = len(grp_a_counts)
    n_groups_b = len(grp_b_counts)

    # Are A and B equivalent? Two ways to ask: same group count, AND no group in
    # A gets split across multiple client_ids in B (a divergence would mean
    # client_id is load-bearing for the chain side of the join).
    keys_a_per_b: dict[tuple[str, str], set[str]] = defaultdict(set)
    for (f, lo, cl) in key_b:
        keys_a_per_b[(f, lo)].add(cl)
    multi_client = sum(1 for s in keys_a_per_b.values() if len(s) > 1)

    # Print summary
    print("\n=== Phase 0 grain-check summary ===")
    print(f"chain rows                : {n_chain:,}")
    print(f"parties rows (total)      : {n_party_total:,}")
    print(f"parties rows (resolved)   : {n_party_resolved:,}")
    print(f"distinct join groups (A)  : {n_groups_a:,}  [key=(filing_id, lobbyist_id)]")
    print(f"distinct join groups (B)  : {n_groups_b:,}  [key=+ client_id]")
    print(f"  (filing_id, lobbyist_id) groups with >1 client_id: {multi_client:,}")
    print(f"coverage A (chain rows w/ ≥1 resolved person): {cov_a:,} / {n_chain:,}  =  {pct_a:.2f}%")
    print(f"coverage B (chain rows w/ ≥1 resolved person): {cov_b:,} / {n_chain:,}  =  {pct_b:.2f}%")
    print(f"\nFan-out (distinct resolved persons per chain row's join group, key A):")
    for p, v in fan_a_deciles:
        print(f"  p{p:>3}: {v}")
    print(f"\nFan-out (distinct resolved persons per chain row's join group, key B):")
    for p, v in fan_b_deciles:
        print(f"  p{p:>3}: {v}")

    # Gating verdict
    print("\n=== Gating verdict ===")
    if pct_a >= 90.0:
        print(f"  GREEN: key A coverage {pct_a:.2f}% ≥ 90%. Phase 1 may proceed under key A.")
    elif pct_b >= 90.0 and pct_b > pct_a:
        print(f"  YELLOW: key A coverage {pct_a:.2f}% < 90%, BUT key B coverage {pct_b:.2f}% ≥ 90%.")
        print(f"  Phase 1 should use ``(filing_id, lobbyist_id, client_id)`` as the join key.")
    else:
        print(f"  RED: neither key reaches 90% (A={pct_a:.2f}%, B={pct_b:.2f}%). STOP — root-cause before Phase 1.")
        print(f"  Plausible causes to investigate:")
        print(f"    - parties_lobbied resolution rate (only resolved rows count here — {n_party_resolved:,} of {n_party_total:,})")
        print(f"    - chain has rows for filings with NO populated parties_lobbied")
        print(f"    - join key mismatch (e.g. types, padding, or a different composite)")

    # Write results doc
    args.results_dir.mkdir(parents=True, exist_ok=True)
    out = args.results_dir / f"{args.stamp}_ny_chain_pl_grain_check.md"
    lines = [
        "# Phase 0: chain × parties_lobbied grain-join sanity check",
        "",
        f"_Run: {args.stamp}._  "
        f"Script: [`scripts/ny_chain_pl_grain_check.py`](../../../../scripts/ny_chain_pl_grain_check.py).  "
        f"Plan: [`plans/ny_chain_completion_sketch.md`](../plans/ny_chain_completion_sketch.md), Phase 0.",
        "",
        "## Inputs",
        "",
        f"- Chain: `{args.chain}` — **{n_chain:,} rows**",
        f"- Parties: `{args.parties}` — **{n_party_total:,} rows** ({n_party_resolved:,} resolved to `ocd-person`)",
        "",
        "## Join geometry",
        "",
        f"- Distinct `(filing_id, lobbyist_id)` groups in chain: **{n_groups_a:,}**",
        f"- Distinct `(filing_id, lobbyist_id, client_id)` groups in chain: **{n_groups_b:,}**",
        f"- `(filing_id, lobbyist_id)` groups spanning >1 `client_id`: **{multi_client:,}**",
        "",
        "## Coverage",
        "",
        "| Join key | Chain rows with ≥1 resolved disclosed person | % |",
        "|---|---:|---:|",
        f"| A: `(filing_id, lobbyist_id)`            | {cov_a:,} / {n_chain:,} | **{pct_a:.2f}%** |",
        f"| B: `(filing_id, lobbyist_id, client_id)` | {cov_b:,} / {n_chain:,} | **{pct_b:.2f}%** |",
        "",
        "## Fan-out (distinct resolved persons per chain row's join group)",
        "",
        "Percentiles — how many disclosed legislators a typical chain row will see:",
        "",
        "| pct | Key A | Key B |",
        "|---:|---:|---:|",
    ]
    a_lookup = dict(fan_a_deciles)
    b_lookup = dict(fan_b_deciles)
    for p in (10, 25, 50, 75, 90, 95, 99, 100):
        lines.append(f"| p{p} | {a_lookup.get(p, '—')} | {b_lookup.get(p, '—')} |")
    lines += [
        "",
        "## Verdict",
        "",
    ]
    if pct_a >= 90.0:
        lines.append(f"**GREEN** — key A coverage {pct_a:.2f}% ≥ 90%. Phase 1 proceeds under key A `(filing_id, lobbyist_id)`.")
    elif pct_b >= 90.0 and pct_b > pct_a:
        lines.append(
            f"**YELLOW** — key A coverage {pct_a:.2f}% < 90%, but key B coverage {pct_b:.2f}% ≥ 90%. "
            "Phase 1 uses key B `(filing_id, lobbyist_id, client_id)`."
        )
    else:
        lines.append(
            f"**RED** — neither key reaches 90% (A={pct_a:.2f}%, B={pct_b:.2f}%). "
            "STOP. Root-cause before Phase 1."
        )
    lines.append("")
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"\n[phase0] wrote results doc: {out}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
