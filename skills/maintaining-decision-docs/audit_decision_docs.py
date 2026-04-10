#!/usr/bin/env python3
"""
Audit decision docs coverage and consistency.

Compares docs on disk against DOCS_INDEX.md and DOCS_SUMMARY.md to find:
- Docs missing from indexes
- Orphaned index entries (referencing deleted docs)
- Broken Related: links
- ADR format compliance gaps

Usage:
    python3 audit_decision_docs.py [repo_root]

If repo_root is omitted, uses the current directory.
"""

import re
import sys
from pathlib import Path
from typing import Optional


def find_docs_dir(repo_root: Path) -> Optional[Path]:
    """Find the docs/ directory relative to repo root."""
    docs_dir = repo_root / "docs"
    if docs_dir.is_dir():
        return docs_dir
    return None


def list_decision_docs(docs_dir: Path) -> list[str]:
    """List all YYYYMMDD-prefixed .md files in docs/."""
    pattern = re.compile(r"^2\d{7}.*\.md$")
    return sorted(
        f.name for f in docs_dir.iterdir()
        if f.is_file() and pattern.match(f.name)
    )


def parse_index_entries(docs_dir: Path) -> list[str]:
    """Extract filenames referenced in DOCS_INDEX.md."""
    index_file = docs_dir / "DOCS_INDEX.md"
    if not index_file.exists():
        return []

    content = index_file.read_text()
    # Match backtick-quoted filenames like `20260305_foo.md`
    return re.findall(r"`(2\d{7}[^`]*\.md)`", content)


def parse_summary_entries(docs_dir: Path) -> list[str]:
    """Extract filenames from ## headers in DOCS_SUMMARY.md."""
    summary_file = docs_dir / "DOCS_SUMMARY.md"
    if not summary_file.exists():
        return []

    content = summary_file.read_text()
    # Match ## headers like ## 20260305_foo.md
    return re.findall(r"^## (2\d{7}[^\n]*\.md)", content, re.MULTILINE)


def check_adr_compliance(docs_dir: Path, doc_name: str) -> dict:
    """Check if a doc has basic ADR structure."""
    doc_path = docs_dir / doc_name
    if not doc_path.exists():
        return {"exists": False}

    content = doc_path.read_text()
    content_lower = content.lower()

    return {
        "exists": True,
        "has_date": bool(re.search(r"\*\*date\b", content_lower) or re.search(r"^date:", content_lower, re.MULTILINE)),
        "has_status": bool(re.search(r"\*\*status\b", content_lower) or re.search(r"^status:", content_lower, re.MULTILINE)),
        "has_context": bool(re.search(r"^#{1,3}\s*(context|background)", content_lower, re.MULTILINE)),
        "has_decision": bool(re.search(r"^#{1,3}\s*(decision|key decisions)", content_lower, re.MULTILINE)),
        "has_rationale": bool(re.search(r"^#{1,3}\s*(rationale|why|decision rationale)", content_lower, re.MULTILINE)),
    }


def find_related_links(docs_dir: Path, doc_name: str) -> list[str]:
    """Extract Related: document references from a doc, skipping code blocks."""
    doc_path = docs_dir / doc_name
    if not doc_path.exists():
        return []

    content = doc_path.read_text()
    # Strip fenced code blocks to avoid matching example filenames
    content_no_codeblocks = re.sub(r"```.*?```", "", content, flags=re.DOTALL)
    # Match filenames in Related: lines or frontmatter related: blocks
    refs = re.findall(r"(2\d{7}[^\s,)]*\.md)", content_no_codeblocks)
    # Deduplicate
    return list(dict.fromkeys(refs))


def check_broken_links(docs_dir: Path, all_docs: list[str]) -> dict[str, list[str]]:
    """Find broken Related: links across all docs."""
    doc_set = set(all_docs)
    broken = {}

    for doc_name in all_docs:
        links = find_related_links(docs_dir, doc_name)
        bad_links = [link for link in links if link not in doc_set]
        if bad_links:
            broken[doc_name] = bad_links

    return broken


def main():
    repo_root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    repo_root = repo_root.resolve()

    docs_dir = find_docs_dir(repo_root)
    if not docs_dir:
        print(f"No docs/ directory found in {repo_root}")
        sys.exit(1)

    # Discover
    on_disk = list_decision_docs(docs_dir)
    in_index = parse_index_entries(docs_dir)
    in_summary = parse_summary_entries(docs_dir)

    on_disk_set = set(on_disk)
    in_index_set = set(in_index)
    in_summary_set = set(in_summary)

    # Coverage
    missing_from_index = sorted(on_disk_set - in_index_set)
    missing_from_summary = sorted(on_disk_set - in_summary_set)
    orphaned_index = sorted(in_index_set - on_disk_set)
    orphaned_summary = sorted(in_summary_set - on_disk_set)

    # Broken links
    broken_links = check_broken_links(docs_dir, on_disk)

    # ADR compliance
    compliance = {}
    for doc in on_disk:
        compliance[doc] = check_adr_compliance(docs_dir, doc)

    non_compliant = [
        doc for doc, checks in compliance.items()
        if checks["exists"] and not (checks["has_date"] and checks["has_context"])
    ]

    # Report
    print("=" * 60)
    print("DECISION DOCS AUDIT REPORT")
    print("=" * 60)
    print(f"\nRepo: {repo_root}")
    print(f"Docs directory: {docs_dir}")
    print()

    print(f"## Coverage")
    print(f"  Docs on disk:        {len(on_disk)}")
    print(f"  In DOCS_INDEX:       {len(in_index_set & on_disk_set)}/{len(on_disk)} ", end="")
    has_index = (docs_dir / "DOCS_INDEX.md").exists()
    has_summary = (docs_dir / "DOCS_SUMMARY.md").exists()
    if not has_index:
        print("(DOCS_INDEX.md does not exist)")
    else:
        print()
    print(f"  In DOCS_SUMMARY:     {len(in_summary_set & on_disk_set)}/{len(on_disk)} ", end="")
    if not has_summary:
        print("(DOCS_SUMMARY.md does not exist)")
    else:
        print()

    if missing_from_index:
        print(f"\n  Missing from DOCS_INDEX ({len(missing_from_index)}):")
        for doc in missing_from_index:
            print(f"    - {doc}")

    if missing_from_summary:
        print(f"\n  Missing from DOCS_SUMMARY ({len(missing_from_summary)}):")
        for doc in missing_from_summary:
            print(f"    - {doc}")

    if orphaned_index:
        print(f"\n  Orphaned DOCS_INDEX entries ({len(orphaned_index)}):")
        for doc in orphaned_index:
            print(f"    - {doc}")

    if orphaned_summary:
        print(f"\n  Orphaned DOCS_SUMMARY entries ({len(orphaned_summary)}):")
        for doc in orphaned_summary:
            print(f"    - {doc}")

    # ADR compliance
    print(f"\n## ADR Format Compliance")
    fully_compliant = [
        doc for doc, checks in compliance.items()
        if checks["exists"]
        and checks["has_date"]
        and checks["has_status"]
        and checks["has_context"]
        and checks["has_decision"]
    ]
    print(f"  Fully compliant:     {len(fully_compliant)}/{len(on_disk)}")

    if non_compliant:
        print(f"\n  Missing basic fields ({len(non_compliant)}):")
        for doc in non_compliant:
            checks = compliance[doc]
            missing = []
            if not checks["has_date"]:
                missing.append("date")
            if not checks["has_status"]:
                missing.append("status")
            if not checks["has_context"]:
                missing.append("context section")
            if not checks["has_decision"]:
                missing.append("decision section")
            if not checks["has_rationale"]:
                missing.append("rationale section")
            print(f"    - {doc}: missing {', '.join(missing)}")

    # Broken links
    print(f"\n## Related Links")
    if broken_links:
        print(f"  Broken links found ({sum(len(v) for v in broken_links.values())}):")
        for doc, links in broken_links.items():
            for link in links:
                print(f"    - {doc} -> {link} (NOT FOUND)")
    else:
        print("  No broken links found.")

    print()

    # Exit code
    has_issues = missing_from_index or missing_from_summary or orphaned_index or orphaned_summary or broken_links
    sys.exit(1 if has_issues else 0)


if __name__ == "__main__":
    main()
