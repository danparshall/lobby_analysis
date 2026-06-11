"""Look up source-rubric provenance for the 18 WI disagreement cells."""
from __future__ import annotations

import csv
from pathlib import Path

TSV = Path(
    "/Users/dan/code/lobby_analysis/.worktrees/wi-tier1-direct-read/"
    "compendium/disclosure_side_compendium_items_v2.tsv"
)

DISAGREEMENT_ROWS = {
    # Pattern A — lobbyist_spending_report (14 cells, all Claude TRUE / GPT FALSE)
    "lobbyist_spending_report_required": "A",
    "lobbyist_spending_report_cadence_includes_semiannual": "A",
    "lobbyist_spending_report_categorizes_expenses_by_type": "A",
    "lobbyist_spending_report_includes_bill_or_action_identifier": "A",
    "lobbyist_spending_report_includes_general_issues": "A",
    "lobbyist_spending_report_includes_general_subject_matter": "A",
    "lobbyist_spending_report_includes_gifts_entertainment_transport_lodging": "A",
    "lobbyist_spending_report_includes_indirect_costs": "A",
    "lobbyist_spending_report_includes_lobbyist_contact_info": "A",
    "lobbyist_spending_report_includes_principal_names": "A",
    "lobbyist_spending_report_includes_specific_bill_number": "A",
    "lobbyist_spending_report_includes_total_compensation": "A",
    "lobbyist_spending_report_includes_total_expenditures": "A",
    "lobbyist_spending_report_required_when_no_activity": "A",
    # Pattern B — Claude scored on principal-side rule, GPT abstained (3 cells)
    "lobbyist_registration_threshold_expenditure_dollars": "B",
    "lobbyist_filing_de_minimis_threshold_time_percent": "B",
    "lobbyist_registration_deadline_days_after_first_lobbying": "B",
    # Pattern C — "in practice" semantic disagreement (1 cell)
    "lobbying_violation_penalties_imposed_in_practice": "C",
}


def main():
    rows: dict[str, dict] = {}
    with TSV.open() as fh:
        reader = csv.DictReader(fh, delimiter="\t")
        for r in reader:
            rid = r.get("compendium_row_id", "").strip()
            if rid in DISAGREEMENT_ROWS:
                rows[rid] = r

    missing = [rid for rid in DISAGREEMENT_ROWS if rid not in rows]
    if missing:
        print(f"MISSING from TSV ({len(missing)}):")
        for m in missing:
            print(f"  - {m}")
        print()

    # Group output by pattern
    for pattern_letter in ["A", "B", "C"]:
        print(f"\n## Pattern {pattern_letter}")
        print()
        print("| row_id | rubrics_reading | n | first_introduced_by | status | notes |")
        print("|---|---|---|---|---|---|")
        for rid, p in DISAGREEMENT_ROWS.items():
            if p != pattern_letter:
                continue
            r = rows.get(rid)
            if r is None:
                print(f"| `{rid}` | (MISSING) | | | | |")
                continue
            print(
                f"| `{rid}` | {r['rubrics_reading']} | {r['n_rubrics']} "
                f"| {r['first_introduced_by']} | {r['status']} "
                f"| {(r.get('notes') or '').strip()} |"
            )

    # Summary of which rubrics are involved
    print("\n## Rubrics appearing across the 18 cells")
    rubric_counts: dict[str, int] = {}
    for r in rows.values():
        for rub in (r["rubrics_reading"] or "").split(","):
            rub = rub.strip()
            if rub:
                rubric_counts[rub] = rubric_counts.get(rub, 0) + 1
    for rub, count in sorted(rubric_counts.items(), key=lambda kv: -kv[1]):
        print(f"  - {rub}: {count}")

    # Show full notes column too — sometimes carries source context
    print("\n## Full notes column per disagreement row")
    for rid in DISAGREEMENT_ROWS:
        r = rows.get(rid)
        if r is None:
            continue
        notes = (r.get("notes") or "").strip()
        if notes:
            print(f"  - `{rid}` ({DISAGREEMENT_ROWS[rid]}): {notes}")


if __name__ == "__main__":
    main()
