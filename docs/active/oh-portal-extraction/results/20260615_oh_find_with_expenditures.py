"""Find OH AERs that don't say 'No expenditures' — the ones where Section II
should have actual content.

For each such filing:
  - Form type (Legislative / Executive / Retirement)
  - Whether the source contains $ amounts in Section II
  - Whether the extracted JSON has any expenditures
"""
from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path("/Users/dan/code/lobby_analysis/.worktrees/oh-chain-composer")
RAW = ROOT / "data/oh_portal/raw"
EXTRACTED = ROOT / "data/oh_portal/extracted"

NO_EXP_PATTERN = re.compile(r"No expenditures", re.IGNORECASE)
TITLE_PATTERN = re.compile(r"<title>([^<]*)</title>", re.IGNORECASE)
DOLLAR_PATTERN = re.compile(r"\$\s*([\d,]+(?:\.\d{2})?)")


def newest_filing_json(filing_id: str) -> Path | None:
    candidates = list((EXTRACTED / filing_id).glob("*/filing.json"))
    if not candidates:
        return None
    return max(candidates, key=lambda p: p.stat().st_mtime)


def main():
    filing_ids = sorted(p.name for p in RAW.iterdir() if p.is_dir())
    print(f"Total filings: {len(filing_ids)}")

    by_form = Counter()
    with_expenditures = []   # raw.html does NOT contain "No expenditures"
    no_exp = Counter()

    for fid in filing_ids:
        subdirs = list((RAW / fid).iterdir())
        if not subdirs:
            continue
        latest = max(subdirs, key=lambda p: p.name)
        html = (latest / "raw.html").read_text(errors="replace")
        t = TITLE_PATTERN.search(html)
        title = t.group(1).strip() if t else "(none)"
        form = "Legislative" if "Legislative" in title else "Executive" if "Executive" in title else "Retirement" if "Retirement" in title else "Other"
        by_form[form] += 1

        if NO_EXP_PATTERN.search(html):
            no_exp[form] += 1
        else:
            # Has expenditures — check the JSON
            jp = newest_filing_json(fid)
            n_extracted = 0
            cats = Counter()
            if jp:
                data = json.loads(jp.read_text())
                exps = data.get("expenditures", [])
                n_extracted = len(exps)
                for e in exps:
                    cats[e.get("category") or "(null)"] += 1
            # Find dollar amounts
            dollars = DOLLAR_PATTERN.findall(html)
            with_expenditures.append({
                "filing_id": fid,
                "form": form,
                "n_extracted": n_extracted,
                "categories": dict(cats),
                "n_dollar_matches": len(dollars),
                "sample_dollars": dollars[:5],
                "html_path": str(latest / "raw.html"),
                "json_path": str(jp) if jp else None,
            })

    print()
    print("=" * 70)
    print("Per-form filing counts")
    print("=" * 70)
    for k, v in by_form.most_common():
        no_exp_n = no_exp[k]
        with_exp_n = v - no_exp_n
        print(f"  {k:12s}: {v:4d} total | {no_exp_n:3d} say 'No expenditures' | {with_exp_n:3d} have expenditure content")
    print()
    print(f"Total filings WITH expenditure content: {len(with_expenditures)}")
    print()
    if with_expenditures:
        print("=" * 70)
        print("Filings WITH expenditure content — extraction outcome")
        print("=" * 70)
        for e in with_expenditures:
            print(f"\n  filing_id={e['filing_id']} ({e['form']}) "
                  f"-- dollars_in_html={e['n_dollar_matches']} | extracted_exps={e['n_extracted']} | cats={e['categories']}")
            print(f"      sample_dollars: {e['sample_dollars']}")
            print(f"      html: {e['html_path']}")


if __name__ == "__main__":
    main()
