"""Spot-check total_expenditure emission asymmetry: who is null, and is the
emitted value verbatim-on-form or derived?

Session: docs/active/leave-behind-prep/convos/20260612_gpt5mini_quality_gap_checks.md

The briefv3 cross-arm table shows total_expenditure at 28 both_null /
63 one_null / 9 both-emit-agree (n=100). The 3-arm dispatch convo establishes
the direction qualitatively ("mini doesn't fill ... total_expenditure as
often as Sonnet does") but not whether mini's nulls are WRONG (the source
carries a total mini missed) or whether Sonnet is DERIVING a total the form
doesn't state. That distinction decides whether mini is shippable: wrong
nulls on a money field disqualify it regardless of cost; conservative
abstention on a derived field does not.

For each one-null rid this script prints:

  - which side emitted, and the value
  - VERBATIM_IN_HTML / NOT_IN_HTML — whether the emitted amount appears as a
    money string in the raw HTML (formats: 1,234.56 | 1234.56 | $-prefixed;
    integer dollars also matched without cents)
  - EQUALS_ITEMIZED_SUM / NOT_SUM — whether the emitted total equals the sum
    of that arm's itemized expenditures[].amount (a derived-value hint)
  - len(expenditures) per side, raw.html path

Reading the two flags together:
  VERBATIM_IN_HTML + sonnet-only  -> form states a total; mini under-extracts
                                     (the disqualifying case if common)
  NOT_IN_HTML + EQUALS_ITEMIZED_SUM -> sonnet derived it; abstention defensible
  NOT_IN_HTML + NOT_SUM           -> eyeball the HTML; heuristic insufficient

The flags are heuristics, not verdicts — money can be rendered in ways the
regexes miss (e.g., split across table cells). Treat NOT_IN_HTML as "open the
file," not "proven derived."

Run (from repo root, on the machine with data/oh_portal/)
---
    uv run python scripts/gpt5mini_oh_300slice_total_expenditure_spotcheck.py

    # Different mini arm, or also check is_itemized-style fields:
    uv run python scripts/gpt5mini_oh_300slice_total_expenditure_spotcheck.py \\
        --arm medium_briefv2 --field total_other_costs
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
_SRC = _REPO_ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from lobby_analysis.oh_portal.fetch import DATA_DIR  # noqa: E402
from lobby_analysis.oh_portal.pipeline_openai import (  # noqa: E402
    EXTRACTED_OPENAI_SUBDIR,
)


def _latest_filing_json(report_dir: Path, prefix: str | None = None) -> Path | None:
    if not report_dir.is_dir():
        return None
    candidates: list[Path] = []
    for d in report_dir.iterdir():
        if not d.is_dir():
            continue
        if prefix is not None and not d.name.startswith(prefix):
            continue
        fj = d / "filing.json"
        if fj.exists():
            candidates.append(fj)
    if not candidates:
        return None
    return max(candidates, key=lambda p: p.stat().st_mtime)


def load_arm(rid: str, data_dir: Path, arm: str) -> dict | None:
    if arm == "sonnet":
        path = _latest_filing_json(data_dir / "extracted" / rid)
    else:
        prefix = f"mini_{arm}_run_1_"
        path = _latest_filing_json(data_dir / EXTRACTED_OPENAI_SUBDIR / rid, prefix=prefix)
    if path is None:
        return None
    return json.loads(path.read_text())


def _raw_html_path(rid: str, data_dir: Path) -> Path | None:
    raw_root = data_dir / "raw" / rid
    if not raw_root.is_dir():
        return None
    candidates = sorted(raw_root.glob("*/raw.html"))
    return candidates[-1] if candidates else None


def find_intersection_rids(data_dir: Path, arms: list[str]) -> list[str]:
    sonnet_root = data_dir / "extracted"
    intersection: list[str] = []
    for rid in sorted(p.name for p in sonnet_root.iterdir() if p.is_dir()):
        if load_arm(rid, data_dir, "sonnet") is None:
            continue
        if all(load_arm(rid, data_dir, a) is not None for a in arms):
            intersection.append(rid)
    return intersection


def money_variants(amount: float) -> list[str]:
    """Render an amount in the string forms an HTML page plausibly uses."""
    variants: list[str] = []
    cents = f"{amount:,.2f}"  # 1,234.56
    variants.append(cents)
    variants.append(cents.replace(",", ""))  # 1234.56
    if amount == int(amount):
        whole = f"{int(amount):,}"  # 1,234
        variants.append(whole)
        variants.append(whole.replace(",", ""))  # 1234
    return variants


def amount_in_html(amount: float, html: str) -> bool:
    for v in money_variants(amount):
        # Guard against substring hits inside longer numbers: no digit /
        # decimal continuation on either side ("1234" must not match inside
        # "12345"; "234.56" must not match inside "1,234.56").
        pat = r"(?<![\d.,])" + re.escape(v) + r"(?!\d|[.,]\d)"
        if re.search(pat, html):
            return True
    return False


def itemized_sum(filing: dict) -> float | None:
    exps = filing.get("expenditures") or []
    amounts = [e.get("amount") for e in exps if e.get("amount") is not None]
    if not amounts:
        return None
    return round(sum(amounts), 2)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", default=str(DATA_DIR))
    parser.add_argument("--arm", default="medium_briefv3")
    parser.add_argument("--field", default="total_expenditure")
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Cap the per-rid detail listing (buckets always computed in full).",
    )
    args = parser.parse_args()

    data_dir = Path(args.data_dir)
    rids = find_intersection_rids(data_dir, [args.arm])
    print(f"Comparison set: {len(rids)} report_ids in (sonnet ∩ {args.arm}); field={args.field}\n")

    buckets: dict[str, list[dict]] = {
        "both_null": [],
        "both_emit_agree": [],
        "both_emit_disagree": [],
        "sonnet_only": [],
        "mini_only": [],
    }
    for rid in rids:
        sonnet = load_arm(rid, data_dir, "sonnet")
        mini = load_arm(rid, data_dir, args.arm)
        assert sonnet is not None and mini is not None
        sv = sonnet.get(args.field)
        mv = mini.get(args.field)
        row = {"rid": rid, "sonnet": sv, "mini": mv, "sonnet_filing": sonnet, "mini_filing": mini}
        if sv is None and mv is None:
            buckets["both_null"].append(row)
        elif sv is not None and mv is not None:
            key = "both_emit_agree" if sv == mv else "both_emit_disagree"
            buckets[key].append(row)
        elif sv is not None:
            buckets["sonnet_only"].append(row)
        else:
            buckets["mini_only"].append(row)

    print("Direction census:")
    for k, v in buckets.items():
        print(f"  {k:18s} {len(v):3d}")
    print()

    for bucket_name in ("sonnet_only", "mini_only", "both_emit_disagree"):
        rows = buckets[bucket_name]
        if not rows:
            continue
        shown = rows if args.limit is None else rows[: args.limit]
        print(
            f"━━━ {bucket_name} ({len(rows)} rids"
            f"{'' if shown is rows else f', showing {len(shown)}'}) ━━━"
        )
        verdict_census: dict[str, int] = {}
        for row in shown:
            emitter = "sonnet" if row["sonnet"] is not None else "mini"
            if bucket_name == "both_emit_disagree":
                emitter = "sonnet"  # check sonnet's value; print both
            value = row[emitter]
            filing = row[f"{emitter}_filing"]
            html_path = _raw_html_path(row["rid"], data_dir)
            in_html = None
            if html_path is not None and value is not None:
                in_html = amount_in_html(float(value), html_path.read_text(errors="replace"))
            isum = itemized_sum(filing)
            equals_sum = isum is not None and value is not None and abs(float(value) - isum) < 0.005
            flag_html = (
                "VERBATIM_IN_HTML"
                if in_html
                else ("NOT_IN_HTML" if in_html is not None else "NO_RAW_HTML")
            )
            flag_sum = "EQUALS_ITEMIZED_SUM" if equals_sum else "NOT_SUM"
            verdict = f"{flag_html}+{flag_sum}"
            verdict_census[verdict] = verdict_census.get(verdict, 0) + 1
            n_exp_s = len(row["sonnet_filing"].get("expenditures") or [])
            n_exp_m = len(row["mini_filing"].get("expenditures") or [])
            print(
                f"  {row['rid']}  sonnet={row['sonnet']} mini={row['mini']}  "
                f"{flag_html} {flag_sum}  "
                f"itemized_sum={isum}  len(exp) s/m={n_exp_s}/{n_exp_m}"
            )
            if html_path is not None:
                print(f"      raw: {html_path}")
        print("\n  verdict census:")
        for v, n in sorted(verdict_census.items(), key=lambda x: -x[1]):
            print(f"    {n:3d}  {v}")
        print()

    print(
        "Decision guide: a large VERBATIM_IN_HTML count under sonnet_only means"
        "\nthe form states a total mini is missing -> disqualifying for mini."
        "\nNOT_IN_HTML+EQUALS_ITEMIZED_SUM means sonnet derived -> abstention"
        "\ndefensible; pick the convention and encode it in the brief either way."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
