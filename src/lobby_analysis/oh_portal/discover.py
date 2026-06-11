"""Agent-axis discovery of recent OH AER filings — the (B') enumeration step.

Maps the OLAC report_id universe so the batch runner has an input list. The
portal partitions filings per filer; the agent-axis chain is:

    Agents/List (CSV roster)            -> agent surnames
    Agents/FormsFiledSearch?LastName=X  -> agent IDs (a surname can have several)
    Agents/{id}/FormsFiled              -> every form that agent filed, as a table
                                           (Year | Employer | Type | ... | Period | View)

Filtering rows to Type=="AER" and a recent year-set yields the AER universe.
Each kept row is written to a TSV whose `report_id` -> /olac/AERs/{id}/View URL
feeds `batch.run_batch`. The `employer` column captures the (agent, employer)
tuple straight from the index — independent of the detail-page extraction.

Raw responses (roster CSV, search HTML, per-agent FormsFiled HTML) are cached
under data/oh_portal/discover/ so the crawl is resumable and auditable.
"""

from __future__ import annotations

import csv
import html as html_lib
import io
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable

import requests

from lobby_analysis.oh_portal.fetch import DATA_DIR, USER_AGENT, throttle

BASE = "https://www2.jlec-olig.state.oh.us"

_AGENT_FORMS_RE = re.compile(r"/olac/Reports/Agents/(\d+)/FormsFiled")
_VIEW_RE = re.compile(r'href="(/olac/\w+/(\d+)/View)"')
_ROW_RE = re.compile(r"<tr[^>]*>(.*?)</tr>", re.IGNORECASE | re.DOTALL)
_TD_RE = re.compile(r"<td[^>]*>(.*?)</td>", re.IGNORECASE | re.DOTALL)
_HEADING_RE = re.compile(r"<h\d[^>]*>(.*?)\s*Forms Filed", re.IGNORECASE | re.DOTALL)


@dataclass(frozen=True)
class RosterAgent:
    last_name: str
    first_name: str


@dataclass(frozen=True)
class FiledForm:
    report_id: str
    year: int
    employer: str
    form_type: str
    category: str
    reporting_period: str
    view_url: str


# OLAC's "Category" column encodes the disclosure regime the form belongs to.
# Confirmed empirically against 364,351 cached AER rows (2026-06-05): the column
# takes exactly L / E / R, no blanks. Anything else is treated as unknown (None),
# never silently defaulted to legislative.
_CATEGORY_TO_REGIME = {
    "L": "legislative",
    "E": "executive",
    "R": "retirement_system",
}


def category_to_regime(category: str) -> str | None:
    """Map an OLAC Category letter to a disclosure regime, or None if unknown."""
    return _CATEGORY_TO_REGIME.get((category or "").strip())


# --------------------------------------------------------------------------- #
# Parsers (pure — unit tested against real captured shapes)
# --------------------------------------------------------------------------- #


def _clean(cell_html: str) -> str:
    return html_lib.unescape(re.sub(r"<[^>]+>", "", cell_html)).strip()


def parse_agent_roster(csv_text: str) -> list[RosterAgent]:
    """Parse the Agents/List CSV into (last, first) records."""
    reader = csv.DictReader(io.StringIO(csv_text))
    out: list[RosterAgent] = []
    for row in reader:
        last = (row.get("Last Name") or "").strip()
        first = (row.get("First Name") or "").strip()
        if last:
            out.append(RosterAgent(last_name=last, first_name=first))
    return out


def parse_search_agent_ids(search_html: str) -> list[str]:
    """Extract agent IDs (order-preserving, deduped) from a FormsFiledSearch
    result. A surname can map to several agent records."""
    seen: list[str] = []
    for m in _AGENT_FORMS_RE.finditer(search_html):
        if m.group(1) not in seen:
            seen.append(m.group(1))
    return seen


def parse_forms_filed(forms_html: str) -> list[FiledForm]:
    """Parse an Agents/{id}/FormsFiled table into FiledForm rows.

    Only data rows (those with a /View link) are returned; the header row and
    any chrome are skipped. Columns are positional per the portal's 8-column
    table: 0=Year, 1=Employer, 2=Type, 5=Category, 6=Reporting Period, and the
    trailing cell's anchor carries the view URL + report_id (path segment
    differs by form type: /olac/AERs/ vs /olac/Initials/)."""
    forms: list[FiledForm] = []
    for rowm in _ROW_RE.finditer(forms_html):
        row = rowm.group(1)
        view = _VIEW_RE.search(row)
        if not view:
            continue
        cells = [_clean(c) for c in _TD_RE.findall(row)]
        if len(cells) < 7:
            continue
        try:
            year = int(cells[0])
        except ValueError:
            continue
        forms.append(
            FiledForm(
                report_id=view.group(2),
                year=year,
                employer=cells[1],
                form_type=cells[2],
                category=cells[5],
                reporting_period=cells[6],
                view_url=view.group(1),
            )
        )
    return forms


def parse_agent_name(forms_html: str) -> str:
    """Pull the agent's display name from the '<X> Forms Filed' heading."""
    m = _HEADING_RE.search(forms_html)
    return _clean(m.group(1)) if m else ""


def recent_aers(forms: Iterable[FiledForm], years: set[int]) -> list[FiledForm]:
    """Keep only Type==AER rows filed in one of `years`."""
    return [f for f in forms if f.form_type == "AER" and f.year in years]


# --------------------------------------------------------------------------- #
# Fetch layer (thin network shell; validated live, not unit-tested)
# --------------------------------------------------------------------------- #


def _discover_dir(data_dir: Path) -> Path:
    # `data_dir` is already the oh_portal-rooted data dir (see fetch.DATA_DIR),
    # so we append only "discover" — appending "oh_portal" here would double
    # the segment and orphan caches one level too deep (#36).
    d = data_dir / "discover"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _get(session: requests.Session, path: str) -> str:
    throttle()
    r = session.get(BASE + path, timeout=60)
    r.raise_for_status()
    return r.text


def _cached_get(session: requests.Session, path: str, cache_file: Path) -> str:
    if cache_file.exists():
        return cache_file.read_text()
    text = _get(session, path)
    cache_file.parent.mkdir(parents=True, exist_ok=True)
    cache_file.write_text(text)
    return text


def fetch_roster(session: requests.Session, data_dir: Path = DATA_DIR) -> list[RosterAgent]:
    csv_text = _cached_get(
        session, "/olac/Reports/Agents/List", _discover_dir(data_dir) / "roster.csv"
    )
    return parse_agent_roster(csv_text)


def fetch_agent_ids_for_surname(
    session: requests.Session, last_name: str, data_dir: Path = DATA_DIR
) -> list[str]:
    safe = re.sub(r"[^A-Za-z0-9_-]", "_", last_name) or "_"
    html = _cached_get(
        session,
        f"/olac/Reports/Agents/FormsFiledSearch?LastName={requests.utils.quote(last_name)}",
        _discover_dir(data_dir) / "search" / f"{safe}.html",
    )
    return parse_search_agent_ids(html)


def fetch_agent_forms(
    session: requests.Session, agent_id: str, data_dir: Path = DATA_DIR
) -> tuple[str, list[FiledForm]]:
    html = _cached_get(
        session,
        f"/olac/Reports/Agents/{agent_id}/FormsFiled",
        _discover_dir(data_dir) / "agents" / f"{agent_id}.html",
    )
    return parse_agent_name(html), parse_forms_filed(html)


# --------------------------------------------------------------------------- #
# Orchestration
# --------------------------------------------------------------------------- #

TSV_HEADER = ["report_id", "agent", "agent_id", "employer", "year", "reporting_period", "form_type", "regime", "aer_url"]


def discover_for_agent_ids(
    agent_ids: Iterable[str],
    years: set[int],
    *,
    data_dir: Path = DATA_DIR,
    session: requests.Session | None = None,
    log: Callable[[str], None] = lambda _m: None,
) -> list[dict]:
    """Fetch FormsFiled for each agent_id, keep recent AERs, return enriched rows."""
    own = session is None
    session = session or requests.Session()
    if own:
        session.headers.update({"User-Agent": USER_AGENT})
    rows: list[dict] = []
    for aid in agent_ids:
        name, forms = fetch_agent_forms(session, aid, data_dir)
        kept = recent_aers(forms, years)
        log(f"[discover] agent {aid} ({name}): {len(kept)} recent AERs of {len(forms)} forms")
        for f in kept:
            rows.append(
                {
                    "report_id": f.report_id,
                    "agent": name,
                    "agent_id": aid,
                    "employer": f.employer,
                    "year": f.year,
                    "reporting_period": f.reporting_period,
                    "form_type": f.form_type,
                    "regime": category_to_regime(f.category),
                    "aer_url": BASE + f.view_url,
                }
            )
    return rows


def discover_all(
    years: set[int],
    *,
    data_dir: Path = DATA_DIR,
    limit_agents: int | None = None,
    log: Callable[[str], None] = lambda _m: None,
) -> list[dict]:
    """Full agent-axis crawl: roster -> surname search -> per-agent FormsFiled."""
    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})
    roster = fetch_roster(session, data_dir)
    surnames = sorted({a.last_name for a in roster})
    log(f"[discover] roster: {len(roster)} agents, {len(surnames)} unique surnames")
    agent_ids: list[str] = []
    seen: set[str] = set()
    for surname in surnames:
        for aid in fetch_agent_ids_for_surname(session, surname, data_dir):
            if aid not in seen:
                seen.add(aid)
                agent_ids.append(aid)
    log(f"[discover] resolved {len(agent_ids)} distinct agent IDs")
    if limit_agents is not None:
        agent_ids = agent_ids[:limit_agents]
        log(f"[discover] limited to first {len(agent_ids)} agents")
    return discover_for_agent_ids(
        agent_ids, years, data_dir=data_dir, session=session, log=log
    )


def write_tsv(rows: list[dict], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=TSV_HEADER, delimiter="\t")
        w.writeheader()
        for r in rows:
            w.writerow(r)


def cli_main() -> int:
    """`python -m lobby_analysis.oh_portal.discover --years 2025,2026 --out PATH
    [--all | --agent-ids 5272,7140] [--limit-agents N]`"""
    import argparse
    import sys

    p = argparse.ArgumentParser(description="Discover recent OH AER report_ids (agent axis).")
    p.add_argument("--years", default="2025,2026", help="comma-separated years to keep")
    p.add_argument("--out", required=True, help="output TSV path")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--all", action="store_true", help="full roster crawl")
    g.add_argument("--agent-ids", help="comma-separated agent IDs (targeted/validation)")
    p.add_argument("--limit-agents", type=int, default=None, help="cap agents (with --all)")
    args = p.parse_args()

    years = {int(y) for y in args.years.split(",") if y.strip()}

    def log(m: str) -> None:
        print(m, file=sys.stderr)

    if args.all:
        rows = discover_all(years, limit_agents=args.limit_agents, log=log)
    else:
        ids = [a.strip() for a in args.agent_ids.split(",") if a.strip()]
        rows = discover_for_agent_ids(ids, years, log=log)

    out_path = Path(args.out)
    write_tsv(rows, out_path)
    print(f"[discover] wrote {len(rows)} AER rows -> {out_path}", file=sys.stderr)
    print(out_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(cli_main())
