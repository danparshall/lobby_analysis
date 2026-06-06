"""Phase-0 follow-up: which OS people-source + match strategy hits ~83%?

The first probe showed exact-match against the *bill-sponsorship* roster resolves
only 63% of legislator-titled ``parties_lobbied`` rows — the misses are real
legislators (leadership: Heastie, Stewart-Cousins, Gianaris) who rarely sponsor
bills and so are absent from the sponsorship people set. This tests whether a
*complete* people roster, and/or a more permissive (first, last) match key,
closes the gap — and whether the gap can be closed by **exact** match on a fuller
roster (within MVP) or only by dropping middle initials (mild fuzzy -> flag Dan).

Roster sources:
  S  = NY_*_bill_sponsorships.csv (entity_type=person)   -- middle-initialed, incomplete
  V  = NY_*_vote_people.csv (voter_name/voter_id)         -- complete-ish, mixed format

Match keys:
  full = normalized "first [middle] last" (exact)
  fl   = (first token, last token) only  -- drops middle initial + suffix

Reports row-weighted resolution rate (over the recon top-400) for each
(source, key) combo, plus collision counts for the fl key.

    uv run --active python scripts/ny_probe_roster_strategies.py
"""

from __future__ import annotations

import csv
import html
import json
import re
from collections import defaultdict
from pathlib import Path

RESULTS = Path("docs/active/ny-disclosure-explore/results")
RECON_TOP = RESULTS / "20260605_ny_parties_lobbied_top_distinct.json"
OS_DIR = Path("data/bills/NY/2025")

TITLES = [
    "assembly member", "assemblywoman", "assemblyman", "assembly woman",
    "assembly man", "senator", "lieutenant governor", "governor",
    "comptroller", "attorney general",
]
_STAFF = re.compile(r",\s*staff member\s*$", re.IGNORECASE)
_PAREN = re.compile(r"\s*\([^)]*\)")
_WS = re.compile(r"\s+")
_LEG_TITLE = re.compile(r"^\s*(senator|assembly\s*member|assemblyman|assemblywoman)\b", re.IGNORECASE)
_SUFFIX = re.compile(r",?\s*(jr|sr|ii|iii|iv)\.?\s*$", re.IGNORECASE)


def strip_title(raw: str) -> str:
    s = html.unescape(str(raw)).strip().rstrip(";").strip()
    s = _STAFF.sub("", s)
    s = _PAREN.sub("", s)
    low = s.lower()
    for t in TITLES:
        if low.startswith(t + " "):
            s = s[len(t):].strip()
            break
    return _WS.sub(" ", s).strip()


def key_full(name_no_title: str) -> str:
    return name_no_title.casefold()


def key_fl(name_no_title: str) -> str:
    s = _SUFFIX.sub("", name_no_title).strip()
    toks = s.split()
    if len(toks) < 2:
        return s.casefold()
    return f"{toks[0]} {toks[-1]}".casefold()


def _csv(glob: str) -> Path:
    matches = list(OS_DIR.glob(glob))
    if not matches:
        raise FileNotFoundError(f"no {glob} under {OS_DIR}")
    return min(matches, key=lambda p: len(p.name))


def load_sources() -> tuple[dict, dict]:
    """Return (name->pid) raw maps from sponsorships and vote_people."""
    csv.field_size_limit(10**7)
    sp: dict[str, str] = {}
    with _csv("NY_*_bill_sponsorships.csv").open(encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            if row.get("entity_type") != "person":
                continue
            pid = (row.get("person_id") or "").strip()
            nm = (row.get("name") or "").strip()
            if pid and nm:
                sp[nm] = pid
    vp: dict[str, str] = {}
    with _csv("NY_*_vote_people.csv").open(encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            pid = (row.get("voter_id") or "").strip()
            nm = (row.get("voter_name") or "").strip()
            if pid and nm and pid.startswith("ocd-person/"):
                vp[nm] = pid
    return sp, vp


def build_roster(raw_map: dict, keyfn) -> dict[str, set]:
    roster: dict[str, set] = defaultdict(set)
    for nm, pid in raw_map.items():
        roster[keyfn(strip_title(nm))].add(pid)
    return roster


def resolve_rate(roster: dict[str, set], keyfn, grouped: list) -> tuple[int, int, int, list]:
    leg_rows = hits = ambiguous = 0
    misses: list[tuple[int, str]] = []
    for r in grouped:
        v = str(r.get("parties_lobbied", "")).strip()
        n = int(r.get("n", 0))
        if not v or not _LEG_TITLE.search(v):
            continue
        leg_rows += n
        k = keyfn(strip_title(v))
        ids = roster.get(k)
        if not ids:
            misses.append((n, v))
        elif len(ids) > 1:
            ambiguous += n
            hits += n  # counts as resolved-but-ambiguous
        else:
            hits += n
    return leg_rows, hits, ambiguous, misses


def main() -> int:
    grouped = json.loads(RECON_TOP.read_text())
    sp, vp = load_sources()
    print(f"[src] sponsorships people={len(sp)}  vote_people people={len(vp)}")
    sv = {**vp, **sp}  # union; sponsorship form wins on key collisions
    print(f"[src] union distinct raw names={len(sv)}")

    combos = [
        ("S  full", sp, key_full),
        ("S  fl  ", sp, key_fl),
        ("V  full", vp, key_full),
        ("V  fl  ", vp, key_fl),
        ("S+V full", sv, key_full),
        ("S+V fl  ", sv, key_fl),
    ]
    print(f"\n{'combo':10} {'leg_rows':>10} {'resolved':>10} {'rate':>7} {'ambig':>8}")
    results = {}
    for label, src, keyfn in combos:
        roster = build_roster(src, keyfn)
        leg, hits, amb, misses = resolve_rate(roster, keyfn, grouped)
        rate = 100 * hits / leg if leg else 0
        print(f"{label:10} {leg:>10,} {hits:>10,} {rate:>6.1f}% {amb:>8,}")
        results[label] = (leg, hits, amb, misses)

    # show residual misses for the best (S+V fl) combo
    print("\n[best=S+V fl] residual unresolved legislator-titled values (top 20):")
    for n, v in sorted(results["S+V fl  "][3], reverse=True)[:20]:
        print(f"    {n:7,d}  {v!r}")

    # collision report for fl key on the union
    roster_fl = build_roster(sv, key_fl)
    collisions = {k: v for k, v in roster_fl.items() if len(v) > 1}
    print(f"\n[collisions] (first,last) keys mapping to >1 ocd-person under S+V: {len(collisions)}")
    for k, v in list(collisions.items())[:15]:
        print(f"    {k!r} -> {sorted(v)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
