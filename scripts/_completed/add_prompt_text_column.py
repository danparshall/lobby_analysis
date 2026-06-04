"""Add the `prompt_text` column to the v2 compendium TSV.

Narrow fix per convo 20260603_statute_disagreement_prior_art_review:
populate prompt_text for the 17 confirmed WI inter-model disagreement rows
(14 Pattern A + 3 Pattern B). Pattern C is excluded — it's a v2.2 axis-split
issue (ledger Entry 2), not a prompt fix.

Source-quote provenance: each row's prompt_text is the verbatim `Source quote`
field from its first_introduced_by rubric's projection-mapping doc under
`docs/historical/compendium-source-extracts/results/projections/`. Citations
embedded in each value name the doc + author so the audit trail back to the
source author's intent is short. (v2.2 ledger Entry 4 motivates eventually
adding a `source_quote_verbatim` column too; for the narrow fix we land just
the one column.)

2026-06-03 iteration 2 — append a uniform LOBBYIST-vs-PRINCIPAL clarifier to
all 14 Pattern A rows. Iteration 1's verbatim CPI/PRI/Sunlight/Newmark/HG
source quotes collapsed Pattern B (3/3) but only 2/14 of Pattern A — Claude
was reading "lobbyists are required to file ... (including ... compensation
received)" as "is information about the lobbyist's compensation required to
be disclosed anywhere in the regime" → TRUE for WI (via the principal's
report). The clarifier makes the filer-identity question explicit, mirroring
the Pattern B clarifier shape that already worked.

Usage: `uv run python scripts/add_prompt_text_column.py` (idempotent —
overwrites the 17 values each run; leaves all other rows' prompt_text empty).
"""

from __future__ import annotations

import csv
from pathlib import Path


TSV_PATH = (
    Path(__file__).resolve().parents[1]
    / "compendium"
    / "disclosure_side_compendium_items_v2.tsv"
)


# 2026-06-03 iteration-2 clarifier appended to every Pattern A row's
# verbatim source quote. Mirrors the Pattern B clarifier shape (which
# resolved 3/3 Pattern B disagreements in iteration 1).
PATTERN_A_CLARIFIER: str = (
    " Asks whether the LOBBYIST is the named filer of a separate spending "
    "report — NOT whether the principal's expense statement contains "
    "lobbyist info (e.g., the lobbyist's signature on the principal's form, "
    "the lobbyist's name/address listed by the principal, or compensation "
    "paid to lobbyists itemized within the principal's aggregate). FALSE in "
    "regimes where the statute mandates the PRINCIPAL as the filer of the "
    "spending report, even if the principal's report references the lobbyist."
)

# The 14 Pattern A row IDs (lobbyist_spending_report_* family). Each row's
# final prompt_text = source_quote + PATTERN_A_CLARIFIER.
_PATTERN_A_ROWS: frozenset[str] = frozenset(
    {
        "lobbyist_spending_report_required",
        "lobbyist_spending_report_cadence_includes_semiannual",
        "lobbyist_spending_report_categorizes_expenses_by_type",
        "lobbyist_spending_report_includes_bill_or_action_identifier",
        "lobbyist_spending_report_includes_general_issues",
        "lobbyist_spending_report_includes_general_subject_matter",
        "lobbyist_spending_report_includes_gifts_entertainment_transport_lodging",
        "lobbyist_spending_report_includes_indirect_costs",
        "lobbyist_spending_report_includes_lobbyist_contact_info",
        "lobbyist_spending_report_includes_principal_names",
        "lobbyist_spending_report_includes_specific_bill_number",
        "lobbyist_spending_report_includes_total_compensation",
        "lobbyist_spending_report_includes_total_expenditures",
        "lobbyist_spending_report_required_when_no_activity",
    }
)


# Verbatim source-rubric quotes for the 17 confirmed WI inter-model disagreement
# rows. Each value is the `Source quote` field from the row's introducing
# rubric's projection-mapping doc — with the doc-file citation appended so the
# audit trail back to the source author is on the prompt line.
# Source: results/20260603_prior_art_adjudication_of_18_disagreements.md
_SOURCE_QUOTES: dict[str, str] = {
    # === Pattern A — lobbyist_spending_report_* row-label ambiguity (14) ===
    "lobbyist_spending_report_required": (
        '"A YES score is earned if lobbyists are required to file itemized '
        "spending reports (including name of employer, lobbied issues and bill "
        "number(s) and compensation/payments received for lobbying services). "
        "A MODERATE score is earned if lobbyists are required to file itemized "
        "spending reports or compensation/payments received, but not both. "
        'A NO score is earned if no such law exists." '
        "(CPI 2015 IND_201; cpi_2015_c11_projection_mapping.md.)"
    ),
    "lobbyist_spending_report_cadence_includes_semiannual": (
        '"Reporting frequency option: Semi-annually." '
        "(PRI 2010 §III.E2.h.iv; pri_2010_projection_mapping.md.)"
    ),
    "lobbyist_spending_report_categorizes_expenses_by_type": (
        '"Expenditure Transparency: Are lobbyists required to itemize all the '
        "expenses associated with their work, such as travel, holding an event, "
        "or buying gifts for lawmakers? Tier 2: Lobbyists report itemized list "
        "of expenses with dates and description of direct expenditure; Tier 1: "
        "Lobbyists report list of expenses categorized under broad descriptions, "
        "e.g. food, travel, meetings, media, etc.; Tier 0: Lobbyists report "
        "lump total of expenditures; Tier -1: Lobbyists do not report total "
        'expenditures." '
        "(Sunlight 2015 #2 Expenditure Transparency, tier-1 reading; "
        "sunlight_2015_projection_mapping.md.)"
    ),
    "lobbyist_spending_report_includes_bill_or_action_identifier": (
        '"Lobbyist Activity: Do lobbyists have to reveal which pieces of '
        "legislation or executive actions they are seeking to influence? "
        "Tier 2: Lobbyists report the bill/action discussed and position "
        "taken; Tier 1: Lobbyists report the bill/action discussed; Tier 0: "
        "Lobbyists report the general subjects of lobbying; Tier -1: "
        'Lobbyists do not report activity." '
        "(Sunlight 2015 #1 Lobbyist Activity, tier-1/2 reading; "
        "sunlight_2015_projection_mapping.md.)"
    ),
    "lobbyist_spending_report_includes_general_issues": (
        '"Are lobbyists required to disclose information on the issue lobbied '
        'by the general issues lobbied?" '
        "(PRI 2010 §III.E2.g.i; pri_2010_projection_mapping.md.)"
    ),
    "lobbyist_spending_report_includes_general_subject_matter": (
        '"Lobbyist Activity: Do lobbyists have to reveal which pieces of '
        "legislation or executive actions they are seeking to influence? "
        "... Tier 0: Lobbyists report the general subjects of lobbying; "
        'Tier -1: Lobbyists do not report activity." '
        "(Sunlight 2015 #1 Lobbyist Activity, tier-0 reading; "
        "sunlight_2015_projection_mapping.md.)"
    ),
    "lobbyist_spending_report_includes_gifts_entertainment_transport_lodging": (
        '"Required component of disclosure report: Other costs such as gifts, '
        'entertainment, transportation, and lodging." '
        "(PRI 2010 §III.E2.f.iii; pri_2010_projection_mapping.md.)"
    ),
    "lobbyist_spending_report_includes_indirect_costs": (
        '"Required component of disclosure report: Indirect lobbying costs '
        '(non-compensation)." '
        "(PRI 2010 §III.E2.f.ii; pri_2010_projection_mapping.md.)"
    ),
    "lobbyist_spending_report_includes_lobbyist_contact_info": (
        '"Are lobbyists required to disclose their address and phone number?" '
        "(PRI 2010 §III.E2.b; pri_2010_projection_mapping.md.)"
    ),
    "lobbyist_spending_report_includes_principal_names": (
        '"Are lobbyists required to disclose the names of all the principals '
        'represented?" '
        "(PRI 2010 §III.E2.c; pri_2010_projection_mapping.md.)"
    ),
    "lobbyist_spending_report_includes_specific_bill_number": (
        '"Are lobbyists required to disclose information on the issue lobbied '
        'by the specific bill number or legislation ID?" '
        "(PRI 2010 §III.E2.g.ii; pri_2010_projection_mapping.md.)"
    ),
    "lobbyist_spending_report_includes_total_compensation": (
        '"Required component of disclosure report: Direct lobbying costs '
        '(compensation)." '
        "(PRI 2010 §III.E2.f.i; pri_2010_projection_mapping.md. "
        "Cross-rubric: read by 8 of 8 rubrics in the v2 compendium.)"
    ),
    "lobbyist_spending_report_includes_total_expenditures": (
        '"total expenditures toward lobbying" '
        "(Newmark 2017 paper line 543-544; "
        "newmark_2017_projection_mapping.md, disclosure.total_expenditures.)"
    ),
    "lobbyist_spending_report_required_when_no_activity": (
        '"Is a lobbyist who has done no spending during a filing period '
        'required to make a report of no activity?" '
        "(Hired Guns / CPI 2007 Q25; hiredguns_2007_projection_mapping.md.)"
    ),
    # === Pattern B — lobbyist_* registration rows where Claude projected ===
    # ===              principal-side rule, GPT abstained (3 rows) ===
    "lobbyist_registration_threshold_expenditure_dollars": (
        '"if they spend a certain amount of money in lobbying (expenditure '
        'standards)" '
        "(Newmark 2017 paper line 523-524; "
        "newmark_2017_projection_mapping.md, def.expenditure_standard. "
        "Asks about the LOBBYIST-DEFINITION expenditure threshold — i.e., the "
        "dollar amount the LOBBYIST spends in lobbying that triggers their "
        "registration as a lobbyist, not a principal-side filing trigger.)"
    ),
    "lobbyist_filing_de_minimis_threshold_time_percent": (
        '"Time threshold exists: if amount of time devoted to lobbying is less '
        "than a threshold percentage of an individual's compensated time the "
        'individual or entity is exempted from filing disclosure." '
        "(PRI 2010 §III.D, D2_present; pri_2010_projection_mapping.md. "
        "Asks about the LOBBYIST's own filing-de-minimis time-percent exemption, "
        "not a principal-side itemized-reporting threshold.)"
    ),
    "lobbyist_registration_deadline_days_after_first_lobbying": (
        '"A 100 score is earned if lobbyists register before or within five '
        "days of initial lobbying activity. ... A 50 score is earned if "
        "lobbyists register about 10 days after initial lobbying activity ... "
        "A 0 score is earned if lobbyists register 20 or more days after "
        'initial lobbying activity ..." '
        "(CPI 2015 IND_200; cpi_2015_c11_projection_mapping.md. "
        "Asks about the LOBBYIST's own statutory registration deadline — i.e., "
        "the number of days after first lobbying within which the LOBBYIST "
        "must register, not a principal-side filing trigger.)"
    ),
}


def _assemble_prompt_text(row_id: str) -> str:
    """Compose final prompt_text = source quote, with Pattern A clarifier
    appended for the 14 Pattern A rows. Pattern B rows already carry a
    row-specific clarifier inline in `_SOURCE_QUOTES`."""
    quote = _SOURCE_QUOTES[row_id]
    if row_id in _PATTERN_A_ROWS:
        return quote + PATTERN_A_CLARIFIER
    return quote


# Public mapping consumers (the script and tests) read.
PROMPT_TEXTS: dict[str, str] = {
    row_id: _assemble_prompt_text(row_id) for row_id in _SOURCE_QUOTES
}


def main() -> None:
    if not TSV_PATH.exists():
        raise FileNotFoundError(TSV_PATH)

    with TSV_PATH.open() as fh:
        reader = csv.DictReader(fh, delimiter="\t")
        fieldnames = list(reader.fieldnames or [])
        rows = list(reader)

    if "prompt_text" not in fieldnames:
        fieldnames.append("prompt_text")

    populated = 0
    updated_existing: list[str] = []
    missing_targets: list[str] = []
    seen_target_row_ids: set[str] = set()

    for row in rows:
        row_id = row["compendium_row_id"]
        # Default empty string in every row — keeps the TSV rectangular.
        row.setdefault("prompt_text", "")
        if row_id in PROMPT_TEXTS:
            seen_target_row_ids.add(row_id)
            target = PROMPT_TEXTS[row_id]
            current = row.get("prompt_text") or ""
            if current == target:
                continue
            if current:
                updated_existing.append(row_id)
            else:
                populated += 1
            row["prompt_text"] = target

    missing_targets = [rid for rid in PROMPT_TEXTS if rid not in seen_target_row_ids]

    # Write back. csv.DictWriter handles embedded quotes/whitespace correctly
    # using csv.QUOTE_MINIMAL — only fields containing the delimiter or the
    # quote char get quoted. Tab is the delimiter so this is safe.
    # Use lineterminator='\n' to preserve the file's existing Unix line endings
    # (csv default is '\r\n' — which would balloon the diff with CRLF noise).
    with TSV_PATH.open("w", newline="") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=fieldnames,
            delimiter="\t",
            quoting=csv.QUOTE_MINIMAL,
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {TSV_PATH}")
    print(f"  Newly populated prompt_text for {populated} rows.")
    print(
        f"  Updated existing prompt_text for {len(updated_existing)} rows "
        f"(target total when stable: 17)."
    )
    if updated_existing:
        for rid in updated_existing:
            print(f"    - {rid}")
    if missing_targets:
        print(f"  WARNING — {len(missing_targets)} target rows not found in TSV:")
        for rid in missing_targets:
            print(f"    - {rid}")


if __name__ == "__main__":
    main()
