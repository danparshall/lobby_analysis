"""Reconnaissance probe for the NY ``lobbyist_bimonthly`` ``party_name`` field.

Sister to ``ny_probe_parties_lobbied_grain.py``. Decides whether the bimonthly
dataset (Socrata id ``t9kf-dqbc``) can supply per-bill disclosed-contact tuples
that the semiannual's ``parties_lobbied`` structurally cannot — Phase-0 of the
semiannual gating settled that ``parties_lobbied`` is a SET per filing-focus
(cartesian, not a mapping). The bimonthly carries the contact in a singular
``party_name`` column instead; this probe tests whether that singularity
extends down to ``(filing, focus)`` grain.

Four parts:

  A. **Grain (LOAD-BEARING).** For 2025 ``State Bill`` rows, does any
     ``(form_submission_id, focus_identifying_number)`` pair carry >1 distinct
     ``party_name``? If 0 → bimonthly maps focus → party at the row level and
     can recover (lawmaker, bill) tuples the semiannual loses. If >0 → still
     cartesian, just one-party-per-row instead of one-set-per-filing.

  B. **Worst-case zoom-in.** Pull all rows of a handful of highest-row-count
     submissions and characterize the shape: rows vs distinct (focus, party)
     triples vs expense-row denormalization, ``individual_lobbyist_name``
     list shape.

  C. **Name format.** Replay the top-400 distinct ``party_name`` values
     through the *existing* ``io.ny.parties.resolve_party_lobbied`` resolver
     against the OS sponsorship roster — measures whether the shipped resolver
     drops in without modification (predict ≥98% given identical name format
     to semiannual).

  D. **Delim check.** Does ``party_name`` ever contain ``;`` / ``&`` / `` and ``
     suggesting it's sometimes a list?

Pure analysis, no TDD, writes nothing to ``releases/``. Raw sample saved for
provenance under ``results/``.

    uv run --active python scripts/ny_probe_bimonthly_party_grain.py
"""

from __future__ import annotations

import json
import os
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

import requests

BASE = "https://data.ny.gov/resource/t9kf-dqbc.json"
YEAR = "2025"
N_SUBMISSIONS = 5  # worst-case multi-row submissions to fully pull
TOP_K_NAMES = 400  # distinct party_name values to test resolution on

RESULTS = Path("docs/active/ny-disclosure-explore/results")
RAW_SAMPLE = RESULTS / "20260607_ny_bimonthly_party_sample.json"
TOP_NAMES = RESULTS / "20260607_ny_bimonthly_party_top_distinct.json"

OS_DIR = Path("data/bills/NY/2025")

# bimonthly business-key for cross-dataset filing identity check.
# Note: form_submission_id is the bimonthly's own report id and will NOT match
# semiannual ids (different filing types). The semantic FILING_KEY (year +
# period + firm + client) is the only cross-dataset handle.
FILING_KEY = (
    "reporting_year",
    "reporting_period",
    "principal_lobbyist_name",
    "beneficial_client_name",
    "contractual_client_name",
)

PULL_COLS = [
    "form_submission_id",
    "reporting_year",
    "reporting_period",
    "principal_lobbyist_name",
    "beneficial_client_name",
    "contractual_client_name",
    "lobbying_focus_type",
    "focus_identifying_number",
    "party_name",
    "individual_lobbyist_name",
    "compensation",
    "expense_type",
    "expense_paid_to",
]

_DELIM = re.compile(r";| and |&amp;|&| / ", re.IGNORECASE)
_LEG_TITLE = re.compile(
    r"^\s*(senator|assembly\s*member|assemblyman|assemblywoman)\b", re.IGNORECASE
)


def _headers() -> dict:
    tok = os.environ.get("SOCRATA_APP_TOKEN")
    return {"X-App-Token": tok} if tok else {}


def _get(params: dict, *, timeout: int = 300) -> list:
    resp = requests.get(BASE, params=params, headers=_headers(), timeout=timeout)
    resp.raise_for_status()
    return resp.json()


# Server-side aggregates we tried and dropped:
#   - count(*) by reporting_year (~2s when warm, but 60M total + 57.9M State-Bill
#     are known from Phase-0 schema verification — no decision rides on
#     re-confirming them, so the query is decorative).
#   - count(distinct party_name) GROUP BY (form_submission_id, focus) over the
#     full 2025 State-Bill subset (~58M rows): times out at 600s anonymously.
#     Narrowing to one reporting period (Jan/Feb, ~10M rows) still timed out at
#     600s.
# The load-bearing grain test now lives in probe_worstcase_zoom — pull all rows
# for the densest filings and compute the per-(filing, focus) distinct party
# count directly on the pulled rows.


# ---------------------------------------------------------------------------
# Part B — worst-case zoom-in
# ---------------------------------------------------------------------------


def probe_worstcase_zoom() -> None:
    print("\n=== PART B: dense-filing zoom-in (mid-size; absolute top-5 are 6-9M rows each) ===", flush=True)
    top = _get(
        {
            "$select": "form_submission_id, count(1) as n",
            "$where": f"reporting_year='{YEAR}' AND lobbying_focus_type='State Bill'",
            "$group": "form_submission_id",
            "$order": "n DESC",
            "$limit": "200",
        },
        timeout=120,
    )
    # Pick filings with row counts in a pullable mid-range — dense enough to
    # exercise denormalization, small enough to JSON-stream in one request.
    MIN_ROWS, MAX_ROWS = 1_000, 8_000
    selected = []
    for r in top:
        n = int(r["n"])
        if MIN_ROWS <= n <= MAX_ROWS:
            selected.append((str(r["form_submission_id"]), n))
            if len(selected) >= N_SUBMISSIONS:
                break
    if not selected:
        # fall back to smaller filings outside the top-200 if needed
        print(f"[zoom] no mid-size filings in top 200; expanding search...")
        # take the smallest top-200 entries
        selected = [(str(r["form_submission_id"]), int(r["n"]))
                    for r in sorted(top, key=lambda r: int(r["n"]))[:N_SUBMISSIONS]]
    print(f"[zoom] absolute-top-5 row counts: "
          f"{[(r['form_submission_id'], r['n']) for r in top[:5]]}", flush=True)
    print(f"[zoom] selected mid-size filings ({MIN_ROWS:,} <= n <= {MAX_ROWS:,}): "
          f"{selected}", flush=True)

    ids = [s[0] for s in selected]
    in_clause = ",".join(ids)
    rows = _get(
        {
            "$select": ",".join(PULL_COLS),
            "$where": (
                f"reporting_year='{YEAR}' AND lobbying_focus_type='State Bill' "
                f"AND form_submission_id IN ({in_clause})"
            ),
            "$limit": "100000",
        },
        timeout=120,
    )
    RAW_SAMPLE.write_text(json.dumps(rows, indent=2))
    print(f"[zoom] pulled {len(rows):,} rows -> {RAW_SAMPLE}", flush=True)

    # Per-submission shape
    by_sub: dict[str, list] = defaultdict(list)
    for r in rows:
        by_sub[str(r.get("form_submission_id", ""))].append(r)

    # GLOBAL load-bearing test across the pulled sample:
    # for each (form_submission_id, focus_identifying_number), how many distinct
    # party_name values do we see?  If max == 1 across all pairs, then bimonthly
    # maps focus -> party at the (filing, focus) grain — and we can recover the
    # (lawmaker, bill) tuples the semiannual structurally cannot.  If max > 1,
    # bimonthly is also cartesian, just one-party-per-row instead of one-set-
    # per-filing.
    pair_parties: dict[tuple[str, str], set] = defaultdict(set)
    for r in rows:
        key = (str(r.get("form_submission_id", "")), str(r.get("focus_identifying_number", "")))
        pair_parties[key].add(str(r.get("party_name", "")))
    np_counter = Counter(len(v) for v in pair_parties.values())
    print(
        f"\n[zoom-grain] {sum(np_counter.values()):,} distinct (filing, focus) "
        f"pairs across all pulled rows"
    )
    print(f"[zoom-grain] np (distinct party_name per pair) distribution:")
    for np_val, c in sorted(np_counter.items()):
        marker = "  <-- focus -> party IS NOT a function" if np_val > 1 else ""
        print(f"          np={np_val}: {c:,} pairs{marker}")
    violations = sum(c for np_val, c in np_counter.items() if np_val > 1)
    if violations == 0:
        print("\n[zoom-grain] *** VERDICT (worst-case sample): "
              "(filing, focus) -> party IS a function. ***")
        print("[zoom-grain] Bimonthly CAN supply per-bill lawmaker tuples the semiannual cannot.")
    else:
        print(f"\n[zoom-grain] *** VERDICT (worst-case sample): {violations:,} pairs "
              f"have multiple distinct party_name values. ***")
        print("[zoom-grain] Bimonthly is also cartesian — singular per row, not per-bill.")
        # show a few violation examples
        for key, parties in list(pair_parties.items())[:5]:
            if len(parties) > 1:
                print(f"          sub={key[0]!r:>10s} focus={key[1]!r:>40s} "
                      f"parties={sorted(parties)[:5]}")

    for sub_id, sub_rows in sorted(by_sub.items(), key=lambda kv: -len(kv[1]))[
        :N_SUBMISSIONS
    ]:
        print(f"\n[zoom] submission {sub_id}: {len(sub_rows):,} rows")
        # Distinct shapes
        focus_party_pairs = {
            (r.get("focus_identifying_number", ""), r.get("party_name", ""))
            for r in sub_rows
        }
        focus_set = {r.get("focus_identifying_number", "") for r in sub_rows}
        party_set = {r.get("party_name", "") for r in sub_rows}
        # rows with expense_type populated (the suspected denormalization axis)
        with_expense = sum(1 for r in sub_rows if (r.get("expense_type") or "").strip())
        # individual_lobbyist_name shape (list vs single?)
        ind_lists = Counter()
        for r in sub_rows:
            ind = (r.get("individual_lobbyist_name") or "").strip()
            if ind:
                ind_lists[ind.count(";") + 1 if ind else 0] += 1
        print(f"        distinct focus values: {len(focus_set):,}")
        print(f"        distinct party_name values: {len(party_set):,}")
        print(f"        distinct (focus, party) pairs: {len(focus_party_pairs):,}")
        print(
            f"        rows with expense_type populated: {with_expense:,} "
            f"({100*with_expense/len(sub_rows):.1f}%)"
        )
        print(f"        individual_lobbyist_name size distribution (top 5):")
        for size, c in ind_lists.most_common(5):
            print(f"          {size}-person list: {c:,} rows")

        # Show first 5 representative rows
        print(f"        sample rows:")
        for r in sub_rows[:5]:
            focus = (r.get("focus_identifying_number") or "")[:60]
            party = (r.get("party_name") or "")[:60]
            expense_type = (r.get("expense_type") or "")[:25]
            ind = (r.get("individual_lobbyist_name") or "")[:60]
            print(
                f"          period={r.get('reporting_period')!r:>11s}  "
                f"focus={focus!r:>62s}  "
                f"party={party!r:>62s}  "
                f"expense={expense_type!r:>27s}  "
                f"ind={ind!r}"
            )


# ---------------------------------------------------------------------------
# Part C — name-format reconciliation against the SHIPPED resolver
# ---------------------------------------------------------------------------


def probe_name_format() -> None:
    print(
        "\n=== PART C: name-format reconciliation against io.ny.parties resolver ===",
        flush=True,
    )

    # Pull top-K distinct party_name values by row weight (2025 State Bill)
    grouped = _get(
        {
            "$select": "party_name, count(1) as n",
            "$where": f"reporting_year='{YEAR}' AND lobbying_focus_type='State Bill'",
            "$group": "party_name",
            "$order": "n DESC",
            "$limit": str(TOP_K_NAMES),
        }
    )
    TOP_NAMES.write_text(json.dumps(grouped, indent=2))
    total_rows = sum(int(r.get("n", 0)) for r in grouped)
    print(
        f"[names] top-{TOP_K_NAMES} distinct party_name values cover {total_rows:,} rows -> "
        f"{TOP_NAMES}",
        flush=True,
    )

    # Import the shipped resolver + roster builder. This is the GOLD path —
    # what we'd actually use if we fold bimonthly in.
    try:
        from lobby_analysis.io.ny.parties import (  # type: ignore
            build_legislator_roster,
            build_nickname_index,
            resolve_party_lobbied,
        )
    except ImportError as exc:
        print(f"[names] cannot import io.ny.parties ({exc}); aborting Part C")
        print("[names] try: uv sync && uv run --active python scripts/...")
        return

    # Build roster from the OS sponsorships CSV (same as the materializer does).
    # NOTE: shipped builders take the *directory*, not the CSV path — they
    # internally glob NY_*_bill_sponsorships.csv and pick the shortest match.
    print(f"[names] roster from {OS_DIR}", flush=True)
    roster = build_legislator_roster(OS_DIR)
    nick_index = build_nickname_index(OS_DIR)
    print(
        f"[names] roster: {len(roster):,} first+last keys; "
        f"nickname index: {len(nick_index):,} (last, canonical-root) keys",
        flush=True,
    )

    leg_rows = leg_hits = 0
    delim_in_top = []
    misses: list[tuple[int, str]] = []
    for r in grouped:
        raw = str(r.get("party_name") or "").strip()
        n = int(r.get("n", 0))
        if not raw:
            continue
        if _DELIM.search(raw):
            delim_in_top.append((n, raw))
        if not _LEG_TITLE.search(raw):
            continue
        leg_rows += n
        pid = resolve_party_lobbied(raw, roster, nick_index)
        if pid:
            leg_hits += n
        else:
            misses.append((n, raw))

    print(f"[names] legislator-titled top-{TOP_K_NAMES} rows: {leg_rows:,}")
    if leg_rows:
        print(
            f"[names] RESOLVED via shipped resolver: {leg_hits:,}/{leg_rows:,} "
            f"= {100*leg_hits/leg_rows:.1f}% of legislator-titled rows"
        )
    print(f"[names] unresolved legislator-titled raws: {len(misses)} distinct "
          f"(row-weighted {sum(m[0] for m in misses):,})")
    for n, raw in sorted(misses, reverse=True)[:25]:
        print(f"          {n:7,d}  {raw!r}")

    print(f"\n[names] Part D — top-{TOP_K_NAMES} values containing a delimiter: "
          f"{len(delim_in_top)}")
    for n, v in sorted(delim_in_top, reverse=True)[:10]:
        print(f"          {n:7,d}  {v!r}")


def _os_sponsorships_csv() -> Path:
    matches = list(OS_DIR.glob("NY_*_bill_sponsorships.csv"))
    if not matches:
        raise FileNotFoundError(f"no NY_*_bill_sponsorships.csv under {OS_DIR}")
    return min(matches, key=lambda p: len(p.name))


def main() -> int:
    RESULTS.mkdir(parents=True, exist_ok=True)
    # Add src to path so 'lobby_analysis' imports work if .venv isn't active
    repo_src = Path(__file__).resolve().parents[1] / "src"
    if str(repo_src) not in sys.path:
        sys.path.insert(0, str(repo_src))

    sess = "with app-token" if os.environ.get("SOCRATA_APP_TOKEN") else "no app-token"
    print(f"[probe] {BASE} year={YEAR} ({sess})", flush=True)
    probe_worstcase_zoom()
    probe_name_format()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
