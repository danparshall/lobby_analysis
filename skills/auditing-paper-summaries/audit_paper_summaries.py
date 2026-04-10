#!/usr/bin/env python3
"""
Audit PAPER_SUMMARIES.md for formatting conventions and completeness.

Checks each entry for:
- Required metadata fields (arXiv, Authors, Date, File)
- Presence of Summary section
- Presence of numerical findings / key results
- Presence of Relevance section
- Consistency of formatting
- Whether referenced PDF/text files exist on disk

Usage:
    python3 audit_paper_summaries.py [repo_root]

If repo_root is omitted, uses the current directory.
"""

import re
import sys
from pathlib import Path
from typing import Optional


def find_summaries_file(repo_root: Path) -> Optional[Path]:
    """Find PAPER_SUMMARIES.md in repo root."""
    f = repo_root / "PAPER_SUMMARIES.md"
    return f if f.exists() else None


def parse_entries(content: str) -> list:
    """Parse PAPER_SUMMARIES.md into individual entries."""
    entries = []
    # Split on ### headings (level 3)
    parts = re.split(r"^### ", content, flags=re.MULTILINE)

    for part in parts[1:]:  # skip preamble before first ###
        lines = part.strip().split("\n")
        title = lines[0].strip()
        body = "\n".join(lines[1:])
        entries.append({"title": title, "body": body, "raw": "### " + part})

    return entries


def check_entry(entry: dict, repo_root: Path) -> dict:
    """Check a single entry for format compliance."""
    body = entry["body"]
    body_lower = body.lower()
    issues = []
    warnings = []

    # Required metadata fields
    has_arxiv = bool(re.search(r"\*\*arXiv:\*\*", body))
    has_authors = bool(re.search(r"\*\*Authors:\*\*", body))
    has_date = bool(re.search(r"\*\*Date:\*\*", body))
    has_file = bool(re.search(r"\*\*File:\*\*", body))

    if not has_arxiv:
        issues.append("missing arXiv field")
    if not has_authors:
        issues.append("missing Authors field")
    if not has_date:
        issues.append("missing Date field")
    if not has_file:
        warnings.append("missing File field (reference-only entry?)")

    # Check if referenced file exists
    file_match = re.search(r"\*\*File:\*\*\s*`([^`]+)`", body)
    if file_match:
        filename = file_match.group(1)
        pdf_path = repo_root / "papers" / filename
        text_stem = Path(filename).stem
        text_path = repo_root / "papers" / "text" / (text_stem + ".txt")

        if not pdf_path.exists():
            warnings.append(f"PDF not found: papers/{filename}")
        if not text_path.exists():
            warnings.append(f"text extraction not found: papers/text/{text_stem}.txt")

    # Summary section
    has_summary = bool(re.search(r"\*\*Summary:\*\*", body))
    if not has_summary:
        issues.append("missing Summary section")

    # Key findings
    has_key_findings = bool(re.search(r"\*\*key findings", body_lower))
    if not has_key_findings:
        warnings.append("no Key findings section")

    # Numerical results
    # Look for percentages, numbers with units, ratios, fractions, ranges, etc.
    has_numbers = bool(re.search(
        r"\d+\.?\d*\s*(%|pp|percentage|percent|points?|×|x\s|improvement|reduction|increase|decrease|accuracy|score)"
        r"|\d+\.?\d*/\w+"  # ratios like 0.21/yr
        r"|\d+\.?\d*\s*[-–]\s*\d"  # ranges like 0.5-0.77
        r"|\d+k\b"  # counts like 18k
        r"|\d+\.?\d*\s*(billion|million|thousand|trillion)",
        body_lower
    ))
    if not has_numbers:
        issues.append("no numerical findings/results detected")

    # Relevance section
    has_relevance = bool(re.search(r"\*\*Relevance:\*\*", body))
    if not has_relevance:
        warnings.append("no Relevance section")

    # Separator
    has_separator = body.rstrip().endswith("---") or "---" in body.split("\n")[-3:]
    if not has_separator:
        warnings.append("missing --- separator after entry")

    return {
        "title": entry["title"],
        "issues": issues,
        "warnings": warnings,
        "has_arxiv": has_arxiv,
        "has_summary": has_summary,
        "has_key_findings": has_key_findings,
        "has_numbers": has_numbers,
        "has_relevance": has_relevance,
    }


def main():
    repo_root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    repo_root = repo_root.resolve()

    summaries_file = find_summaries_file(repo_root)
    if not summaries_file:
        print(f"No PAPER_SUMMARIES.md found in {repo_root}")
        sys.exit(1)

    content = summaries_file.read_text()
    entries = parse_entries(content)

    results = []
    for entry in entries:
        result = check_entry(entry, repo_root)
        results.append(result)

    # Categorize
    with_issues = [r for r in results if r["issues"]]
    with_warnings_only = [r for r in results if r["warnings"] and not r["issues"]]
    clean = [r for r in results if not r["issues"] and not r["warnings"]]

    # Stats
    total = len(results)
    with_summary = sum(1 for r in results if r["has_summary"])
    with_findings = sum(1 for r in results if r["has_key_findings"])
    with_numbers = sum(1 for r in results if r["has_numbers"])
    with_relevance = sum(1 for r in results if r["has_relevance"])

    print("=" * 60)
    print("PAPER SUMMARIES AUDIT REPORT")
    print("=" * 60)
    print(f"\nFile: {summaries_file}")
    print(f"Total entries: {total}")
    print()

    print("## Coverage")
    print(f"  Has Summary section:      {with_summary}/{total}")
    print(f"  Has Key findings section:  {with_findings}/{total}")
    print(f"  Has numerical results:    {with_numbers}/{total}")
    print(f"  Has Relevance section:    {with_relevance}/{total}")
    print()

    if with_issues:
        print(f"## Issues ({len(with_issues)} entries)")
        for r in with_issues:
            print(f"\n  {r['title']}")
            for issue in r["issues"]:
                print(f"    ERROR: {issue}")
            for warning in r["warnings"]:
                print(f"    WARN:  {warning}")

    if with_warnings_only:
        print(f"\n## Warnings Only ({len(with_warnings_only)} entries)")
        for r in with_warnings_only:
            print(f"\n  {r['title']}")
            for warning in r["warnings"]:
                print(f"    WARN:  {warning}")

    print(f"\n## Clean ({len(clean)} entries)")
    if clean:
        for r in clean:
            print(f"  - {r['title']}")

    # Priority list for factual review
    missing_numbers = [r for r in results if not r["has_numbers"]]
    if missing_numbers:
        print(f"\n## Priority for Factual Review ({len(missing_numbers)} entries lacking numerical findings)")
        for r in missing_numbers:
            print(f"  - {r['title']}")

    print()
    has_issues = bool(with_issues)
    sys.exit(1 if has_issues else 0)


if __name__ == "__main__":
    main()
