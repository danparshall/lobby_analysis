"""Empirical reconciliation probe: client_semiannual vs lobbyist_bimonthly comp.

Resolves the precise reconciliation rule between the two NY datasets that both
carry ``filing_compensation`` for the retained-lobbyist universe (#37). For a
given ``(principal_lobbyist, beneficial_client, half-year)``:

    SUM(canonical bimonthly compensation for periods in H)
       == canonical semiannual compensation for H

where "canonical" means amendment-supersede applied (keep the highest
``form_submission_id`` per business key).

Empirically verified on 5 firms × 12 ``(firm, client, half-year)`` cells in
2025 (firms chosen from the 2026-06-07 bimonthly probe sample): every cell
matches to the cent, including a case where a semiannual amendment corrected
$47,000 → $45,823 and the bimonthly side ALSO reports $45,823.

This means a future build that materializes BOTH datasets and naively
concatenates their ``filing_compensation`` columns would **exactly
double-count** the retained-lobbyist universe (not a precaution — a literal 2×
error). See ``releases/ny/README.md`` Caveat 11 for the operational rule.

How to run::

    uv run python scripts/ny_probe_bi_semi_reconciliation.py

Writes raw evidence to::

    docs/active/ny-disclosure-explore/results/20260610_ny_bi_full_pull.json
"""

from __future__ import annotations

import json
import os
import sys
import time
from collections import defaultdict
from decimal import Decimal
from pathlib import Path

import pandas as pd
import requests

BIMONTHLY_BASE = "https://data.ny.gov/resource/t9kf-dqbc.json"
SEMIANNUAL_CSV = Path("data/raw/ny/2025/client_semiannual.csv")
RESULTS = Path("docs/active/ny-disclosure-explore/results")
RAW_BI_OUT = RESULTS / "20260610_ny_bi_full_pull.json"

YEAR = "2025"

# Firms drawn from the 2026-06-07 bimonthly party-grain probe sample —
# small enough that one Socrata $group query returns all their distinct
# (sub, year, period, firm, b_client, c_client, comp) tuples in <30s.
FIRMS = [
    "NEW YORK STATE ECONOMIC DEVELOPMENT COUNCIL, INC.",
    "PLANNED PARENTHOOD OF GREATER NEW YORK, INC.",
    "CIVIL SERVICE EMPLOYEES ASSOCIATION, INC.",
    "SURVEILLANCE TECHNOLOGY OVERSIGHT PROJECT, INC.",
    "CLEAN AND HEALTHY NEW YORK, INC.",
]

BUSINESS_KEY = (
    "reporting_year",
    "reporting_period",
    "principal_lobbyist",
    "beneficial_client",
    "contractual_client_name",
)

H1_PERIODS = {"Jan/Feb", "Mar/Apr", "May/June"}
H2_PERIODS = {"July/Aug", "Sep/Oct", "Nov/Dec"}
SEMI_PERIOD_TO_H = {"Jan/June": "H1", "July/Dec": "H2"}


def _headers() -> dict:
    tok = os.environ.get("SOCRATA_APP_TOKEN")
    return {"X-App-Token": tok} if tok else {}


def coerce_money(raw) -> Decimal | None:
    """Mirror io/ny/parse.coerce_money — strip ``$``/``,``; ``""``/None → None."""
    if raw is None:
        return None
    s = str(raw).strip().replace("$", "").replace(",", "")
    if not s:
        return None
    try:
        return Decimal(s)
    except Exception:
        return None


def _quote_in_clause(values: list[str]) -> str:
    return "(" + ",".join(f"'{v}'" for v in values) + ")"


def fetch_bimonthly_distinct_filings() -> list[dict]:
    """Pull distinct (sub, year, period, firm, clients, comp) tuples via $group."""
    cols = (
        "form_submission_id, reporting_year, reporting_period, "
        "principal_lobbyist_name, beneficial_client_name, "
        "contractual_client_name, compensation"
    )
    params = {
        "$select": cols + ", count(1) as n",
        "$where": (
            f"reporting_year='{YEAR}' "
            f"AND principal_lobbyist_name IN {_quote_in_clause(FIRMS)}"
        ),
        "$group": cols,
        "$limit": "50000",
    }
    print(f"[bi] socrata $group for {len(FIRMS)} firms...", flush=True)
    t0 = time.time()
    resp = requests.get(
        BIMONTHLY_BASE, params=params, headers=_headers(), timeout=300
    )
    resp.raise_for_status()
    rows = resp.json()
    print(
        f"[bi] {len(rows):,} distinct filing rows in {time.time()-t0:.1f}s; "
        f"saving raw evidence to {RAW_BI_OUT}",
        flush=True,
    )
    RAW_BI_OUT.parent.mkdir(parents=True, exist_ok=True)
    RAW_BI_OUT.write_text(json.dumps(rows, indent=2))
    return rows


def load_semiannual_for_firms(firms: set[str]) -> pd.DataFrame:
    """Stream the local client_semiannual CSV; keep rows whose firm is in ``firms``.

    Uses the canonical semi column names (``principal_lobbyist``, not
    ``principal_lobbyist_name`` — the semi has different raw column names than
    the bimonthly; ``io/ny/columns.py`` normalizes both downstream).
    """
    semi_cols = [
        "form_submission_id",
        "reporting_year",
        "reporting_period",
        "principal_lobbyist",
        "beneficial_client",
        "contractual_client_name",
        "current_period_compensation",
    ]
    matched = []
    total = 0
    for chunk in pd.read_csv(
        SEMIANNUAL_CSV, usecols=semi_cols, dtype=str, chunksize=500_000
    ):
        total += len(chunk)
        m = chunk["principal_lobbyist"].isin(firms)
        if m.any():
            matched.append(chunk.loc[m])
    print(
        f"[semi] scanned {total:,} rows; matched {sum(len(c) for c in matched):,}",
        flush=True,
    )
    return pd.concat(matched) if matched else pd.DataFrame(columns=semi_cols)


def supersede_bi(rows: list[dict]) -> list[dict]:
    """Keep max(form_submission_id) per BUSINESS_KEY (bimonthly side)."""
    keys_bi = (
        "reporting_year",
        "reporting_period",
        "principal_lobbyist_name",
        "beneficial_client_name",
        "contractual_client_name",
    )
    by_key: dict[tuple, dict] = {}
    for r in rows:
        k = tuple(r.get(c, "") for c in keys_bi)
        sub_id = int(r.get("form_submission_id", "0") or "0")
        cur = by_key.get(k)
        if cur is None or sub_id > int(cur.get("form_submission_id", "0") or "0"):
            by_key[k] = r
    return list(by_key.values())


def supersede_semi(df: pd.DataFrame) -> pd.DataFrame:
    """Keep max(form_submission_id) per BUSINESS_KEY (semi side)."""
    if df.empty:
        return df
    df = df.copy()
    df["__sub_int"] = df["form_submission_id"].astype(int)
    keys = list(BUSINESS_KEY)
    idx = df.groupby(keys, dropna=False)["__sub_int"].idxmax()
    out = df.loc[idx].drop(columns=["__sub_int"]).reset_index(drop=True)
    return out


def reconcile() -> int:
    bi_rows = fetch_bimonthly_distinct_filings()
    bi_canonical = supersede_bi(bi_rows)
    print(
        f"[bi] {len(bi_rows)} raw → {len(bi_canonical)} canonical (post-supersede)",
        flush=True,
    )

    semi_df = load_semiannual_for_firms(set(FIRMS))
    semi_canonical = supersede_semi(semi_df)
    print(
        f"[semi] {len(semi_df)} raw → {len(semi_canonical)} canonical (post-supersede)",
        flush=True,
    )

    # Sum bi per (firm, b_client, c_client, half-year)
    bi_sums: dict[tuple, dict[str, Decimal]] = defaultdict(
        lambda: {"H1": Decimal("0"), "H2": Decimal("0")}
    )
    bi_periods: dict[tuple, dict[str, list[str]]] = defaultdict(
        lambda: {"H1": [], "H2": []}
    )
    for r in bi_canonical:
        key = (
            r.get("principal_lobbyist_name", ""),
            r.get("beneficial_client_name", ""),
            r.get("contractual_client_name", ""),
        )
        p = r.get("reporting_period", "")
        c = coerce_money(r.get("compensation")) or Decimal("0")
        if p in H1_PERIODS:
            bi_sums[key]["H1"] += c
            bi_periods[key]["H1"].append(p)
        elif p in H2_PERIODS:
            bi_sums[key]["H2"] += c
            bi_periods[key]["H2"].append(p)

    # Index semi by (firm, b_client, c_client, H)
    semi_by_key: dict[tuple, dict[str, Decimal]] = defaultdict(dict)
    for _, r in semi_canonical.iterrows():
        key = (
            r["principal_lobbyist"],
            r["beneficial_client"],
            r.get("contractual_client_name", ""),
        )
        h = SEMI_PERIOD_TO_H.get(r["reporting_period"])
        if h is None:
            continue
        comp = coerce_money(r["current_period_compensation"]) or Decimal("0")
        semi_by_key[key][h] = comp

    # Union of keys
    all_keys = sorted(set(bi_sums) | set(semi_by_key))
    print("\n=== reconciliation table: SUM(bi) ?= semi per (firm, client, half) ===")
    header = (
        f"{'firm':45s}  {'b_client':35s}  {'H':2s}  "
        f"{'bi_sum':>13s}  {'semi':>13s}  {'delta':>10s}  bi periods present"
    )
    print(header)
    print("-" * len(header))
    matched = mismatched = 0
    for key in all_keys:
        firm, bclient, cclient = key
        for h in ("H1", "H2"):
            bi_sum = bi_sums.get(key, {}).get(h, Decimal("0"))
            semi_val = semi_by_key.get(key, {}).get(h, None)
            bi_present = bi_periods.get(key, {}).get(h, [])
            if semi_val is None and bi_sum == 0:
                continue  # no data either side
            semi_str = f"${semi_val:,.2f}" if semi_val is not None else "(no semi)"
            bi_str = f"${bi_sum:,.2f}" if bi_present else "(no bi)"
            if semi_val is not None and bi_present:
                delta = bi_sum - semi_val
                delta_str = f"${delta:,.2f}"
                if delta == 0:
                    matched += 1
                else:
                    mismatched += 1
            else:
                delta_str = "(partial)"
            print(
                f"{firm[:45]:45s}  {bclient[:35]:35s}  {h}  "
                f"{bi_str:>13s}  {semi_str:>13s}  {delta_str:>10s}  "
                f"{sorted(bi_present)}"
            )

    print(
        f"\n=== verdict: {matched} cells match exactly, "
        f"{mismatched} cells mismatch ==="
    )
    if mismatched == 0:
        print(
            "*** SUM(canonical bimonthly periods of half H) "
            "== canonical semiannual H for every cell tested. ***"
        )
        print(
            "Naively concatenating bimonthly + semiannual filing_compensation "
            "would EXACTLY double-count the retained-lobbyist universe."
        )
    else:
        print(
            "*** RULE FAILS — at least one cell has SUM(bi) != semi. "
            "Stop and surface to Dan before any cross-dataset build. ***"
        )
    return 0 if mismatched == 0 else 1


def main() -> int:
    if not SEMIANNUAL_CSV.exists():
        print(
            f"ERROR: local semiannual CSV not found at {SEMIANNUAL_CSV}; "
            f"run scripts/ny_pull_2025.py first.",
            file=sys.stderr,
        )
        return 2
    return reconcile()


if __name__ == "__main__":
    raise SystemExit(main())
