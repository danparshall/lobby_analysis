"""Compendium v2 row-ID renamer.

Applies the 15 accepted row-ID renames (plus 1 doc-filename typo fix) from
the row-naming audit on `compendium-naming-docs` (merged to main, plan at
docs/active/compendium-naming-docs/plans/20260515_rename_execution_plan.md).

This is a find-and-replace tool, not a TSV canonicalizer: it rewrites any
text-bearing file in the repo that mentions an old row ID. Sister branches
absorb the rename by merging main and running this script on their own tree.

Word-boundary regex matching prevents the Candidate-5 substring trap
(`registration_deadline_days_after_first_lobbying` is a substring of the
new name `lobbyist_registration_deadline_days_after_first_lobbying`).
"""

from __future__ import annotations

import re
from pathlib import Path

# 15 row-ID renames + 1 doc filename typo fix (Candidate 8). Order matches
# the 8 candidate clusters in plan §1.
RENAMES: dict[str, str] = {
    # Candidate 1 — joint-actor ordering
    "principal_or_lobbyist_reg_form_includes_member_or_sponsor_names": "lobbyist_or_principal_reg_form_includes_member_or_sponsor_names",
    # Candidate 2 — D3 rename gaps (5 spending_report + 1 LV-1 filing exception)
    "lobbyist_report_distinguishes_in_house_vs_contract_filer": "lobbyist_filing_distinguishes_in_house_vs_contract_filer",
    "lobbyist_report_includes_campaign_contributions": "lobbyist_spending_report_includes_campaign_contributions",
    "lobbyist_or_principal_report_includes_lobbyist_count_total_and_FTE": "lobbyist_or_principal_spending_report_includes_lobbyist_count_total_and_FTE",
    "lobbyist_or_principal_report_includes_time_spent_on_lobbying": "lobbyist_or_principal_spending_report_includes_time_spent_on_lobbying",
    "lobbyist_or_principal_report_includes_trade_association_dues_or_sponsorship": "lobbyist_or_principal_spending_report_includes_trade_association_dues_or_sponsorship",
    "principal_report_lists_lobbyists_employed": "principal_spending_report_lists_lobbyists_employed",
    # Candidate 3 — registration threshold trio (high-traffic)
    "compensation_threshold_for_lobbyist_registration": "lobbyist_registration_threshold_compensation_dollars",
    "expenditure_threshold_for_lobbyist_registration": "lobbyist_registration_threshold_expenditure_dollars",
    "time_threshold_for_lobbyist_registration": "lobbyist_registration_threshold_time_percent",
    # Candidate 4 — itemization de-minimis family fit
    "expenditure_itemization_de_minimis_threshold_dollars": "lobbyist_filing_itemization_de_minimis_threshold_dollars",
    # Candidate 5 — registration deadline family fit (substring-of-new-name; word boundaries required)
    "registration_deadline_days_after_first_lobbying": "lobbyist_registration_deadline_days_after_first_lobbying",
    # Candidate 6 — ministerial-diary plural drift
    "ministerial_diaries_available_online": "ministerial_diary_available_online",
    # Candidate 7 — definitional-row family fit
    "lobbying_definition_included_activity_types": "def_lobbying_activity_types",
    "lobbyist_definition_included_actor_types": "def_lobbyist_actor_types",
    # Candidate 8 — README projection-mapping filename typo (not a row rename)
    "cpi_2015_projection_mapping": "cpi_2015_c11_projection_mapping",
}


_PATTERN = re.compile(r"\b(" + "|".join(re.escape(k) for k in RENAMES) + r")\b")


def apply_renames_to_text(text: str, renames: dict[str, str]) -> tuple[str, int]:
    """Apply renames to a single text string. Word-boundary-aware so a longer
    new-name that contains an old-name as a substring is not re-matched.

    Returns (new_text, count_of_substitutions).
    """
    # Build a pattern from the caller-supplied renames (so tests can pass
    # a subset if they want). For RENAMES, the module-level _PATTERN is
    # equivalent — but we re-compile here for correctness on arbitrary input.
    if not renames:
        return text, 0
    pattern = re.compile(r"\b(" + "|".join(re.escape(k) for k in renames) + r")\b")
    count = 0

    def _sub(m: re.Match[str]) -> str:
        nonlocal count
        count += 1
        return renames[m.group(1)]

    new_text = pattern.sub(_sub, text)
    return new_text, count


# Paths whose first component (relative to repo root) we never touch.
_SKIP_TOP_LEVEL = {".git", ".venv", ".worktrees", "node_modules", "__pycache__"}

# Subpaths (relative to repo root) we never touch.
_SKIP_SUBPATHS = (
    Path("docs") / "historical",
    Path("compendium") / "_deprecated",
)

# Specific files we never touch. The renamer module and its tests reference
# old names as data (mapping keys, test inputs) — rewriting them would
# destroy the rename machinery. NAMING_CONVENTIONS.md §10 needs surgical
# hand-edit (mark candidates DONE, add §10.1 resolver table); auto-rename
# would collapse the candidate list semantics.
_SKIP_FILES = (
    Path("src") / "lobby_analysis" / "row_id_renamer.py",
    Path("tests") / "test_v2_update_names.py",
    Path("compendium") / "NAMING_CONVENTIONS.md",
    Path("STATUS.md"),
)

# File extensions we treat as text. Anything else is left alone.
_TEXT_EXTENSIONS = {
    ".py",
    ".md",
    ".tsv",
    ".csv",
    ".txt",
    ".toml",
    ".yaml",
    ".yml",
    ".json",
    ".ini",
    ".cfg",
}


def should_skip_path(path: Path, root: Path) -> bool:
    """Return True if path is inside an ancestor we never modify."""
    try:
        rel = path.resolve().relative_to(root.resolve())
    except ValueError:
        # Outside the root — skip
        return True
    parts = rel.parts
    if not parts:
        return False
    if parts[0] in _SKIP_TOP_LEVEL:
        return True
    for skip in _SKIP_SUBPATHS:
        skip_parts = skip.parts
        if len(parts) >= len(skip_parts) and parts[: len(skip_parts)] == skip_parts:
            return True
    for skip in _SKIP_FILES:
        if parts == skip.parts:
            return True
    return False


def walk_and_apply(
    root: Path,
    renames: dict[str, str],
    *,
    dry_run: bool,
) -> dict[Path, int]:
    """Walk `root` recursively. For each text file outside a skip path,
    apply the renames. Returns a dict mapping changed file paths to the
    number of substitutions made.

    Files with zero substitutions are not included in the returned dict.

    When `dry_run=True`, files are not written; the returned counts are
    still accurate (what WOULD have been changed).
    """
    root = root.resolve()
    results: dict[Path, int] = {}

    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if should_skip_path(path, root):
            continue
        if path.suffix.lower() not in _TEXT_EXTENSIONS:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            # Not a readable text file; skip silently
            continue
        new_text, count = apply_renames_to_text(text, renames)
        if count == 0:
            continue
        results[path] = count
        if not dry_run:
            path.write_text(new_text, encoding="utf-8")

    return results
