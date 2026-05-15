"""Behavior tests for tools.v2_update_names — the find-and-replace tool that
applies the 15 compendium v2 row-ID renames (accepted in audit branch
`compendium-naming-docs`, plan: docs/active/compendium-naming-docs/plans/20260515_rename_execution_plan.md
now on main) plus 1 README typo fix.

Run with:  uv run pytest tests/test_v2_update_names.py
"""

from __future__ import annotations

import csv
import shutil
from pathlib import Path

import pytest

from lobby_analysis.row_id_renamer import (
    RENAMES,
    apply_renames_to_text,
    should_skip_path,
    walk_and_apply,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
V2_TSV = REPO_ROOT / "compendium" / "disclosure_side_compendium_items_v2.tsv"


# ---------------------------------------------------------------------------
# Mapping integrity
# ---------------------------------------------------------------------------


def test_renames_has_16_entries():
    """15 row-ID renames (Candidates 1–7) + 1 filename typo fix (Candidate 8)."""
    assert len(RENAMES) == 16


def test_renames_keys_all_unique():
    # dict construction would dedupe; this guards against a mistyped duplicate
    # being silently dropped during a future edit.
    assert len(set(RENAMES.keys())) == len(RENAMES)


def test_renames_values_all_unique():
    assert len(set(RENAMES.values())) == len(RENAMES)


def test_renames_no_old_name_equals_new_name():
    for old, new in RENAMES.items():
        assert old != new, f"identity rename for {old}"


def test_lv1_renames_to_filing_not_spending_report():
    """The LV-1 categorical exception. The other 5 Candidate-2 rows go to
    `_spending_report_*`; this one goes to `_filing_*` because it's a
    LobbyView schema-coverage observable, not a report-content row.
    See plan §1 Candidate 2 and NAMING_CONVENTIONS.md §5 / §11."""
    assert (
        RENAMES["lobbyist_report_distinguishes_in_house_vs_contract_filer"]
        == "lobbyist_filing_distinguishes_in_house_vs_contract_filer"
    )


def test_candidate_3_unit_suffixes():
    """compensation & expenditure get `_dollars`; time gets `_percent`.
    Plan §1 Candidate 3."""
    assert (
        RENAMES["compensation_threshold_for_lobbyist_registration"]
        == "lobbyist_registration_threshold_compensation_dollars"
    )
    assert (
        RENAMES["expenditure_threshold_for_lobbyist_registration"]
        == "lobbyist_registration_threshold_expenditure_dollars"
    )
    assert (
        RENAMES["time_threshold_for_lobbyist_registration"]
        == "lobbyist_registration_threshold_time_percent"
    )


# ---------------------------------------------------------------------------
# Pure transform: apply_renames_to_text
# ---------------------------------------------------------------------------


def test_apply_renames_replaces_a_known_old_id():
    text = "row: lobbyist_report_includes_campaign_contributions, axis: legal"
    new_text, count = apply_renames_to_text(text, RENAMES)
    assert "lobbyist_report_includes_campaign_contributions" not in new_text
    assert "lobbyist_spending_report_includes_campaign_contributions" in new_text
    assert count == 1


def test_apply_renames_no_op_when_no_old_names():
    text = "nothing here matches the mapping"
    new_text, count = apply_renames_to_text(text, RENAMES)
    assert new_text == text
    assert count == 0


def test_apply_renames_idempotent_on_new_names():
    """Running the script twice must not double-rename. This is the
    Candidate-5 substring risk: old name `registration_deadline_days_after_first_lobbying`
    is a substring of the new name `lobbyist_registration_deadline_days_after_first_lobbying`,
    so a naive find-and-replace would produce
    `lobbyist_lobbyist_registration_deadline_days_after_first_lobbying`
    on the second run. Word-boundary matching prevents this.
    """
    text = "row: lobbyist_registration_deadline_days_after_first_lobbying"
    once, _ = apply_renames_to_text(text, RENAMES)
    twice, count2 = apply_renames_to_text(once, RENAMES)
    assert once == twice
    assert count2 == 0


def test_apply_renames_handles_all_15_old_row_ids():
    """All 15 old row IDs must be replaceable in a single pass."""
    # Build a text containing every old row ID once
    old_ids = [k for k in RENAMES if not k.endswith("_projection_mapping")]
    text = "\n".join(old_ids)
    new_text, count = apply_renames_to_text(text, RENAMES)
    assert count == 15
    for old in old_ids:
        # Old name should be gone from the text (modulo substring-of-new-name,
        # but we constructed the text to only contain old names on their own lines)
        new = RENAMES[old]
        # If new contains old as substring (Candidate 5), the line is just the new name now
        if old in new:
            assert new in new_text
        else:
            assert old not in new_text


def test_apply_renames_word_boundary_does_not_match_substring():
    """`registration_deadline_days_after_first_lobbying` inside the longer
    `lobbyist_registration_deadline_days_after_first_lobbying` must not match.
    """
    text = "lobbyist_registration_deadline_days_after_first_lobbying"  # the NEW name
    new_text, count = apply_renames_to_text(text, RENAMES)
    assert new_text == text
    assert count == 0


def test_apply_renames_candidate_8_readme_typo():
    text = "see cpi_2015_projection_mapping.md for details"
    new_text, count = apply_renames_to_text(text, RENAMES)
    assert "cpi_2015_c11_projection_mapping.md" in new_text
    assert count == 1


# ---------------------------------------------------------------------------
# Path-skip logic
# ---------------------------------------------------------------------------


def test_should_skip_historical():
    root = Path("/repo")
    assert should_skip_path(root / "docs" / "historical" / "something.md", root)


def test_should_skip_deprecated():
    root = Path("/repo")
    assert should_skip_path(root / "compendium" / "_deprecated" / "v1" / "x.tsv", root)


def test_should_skip_dot_git():
    root = Path("/repo")
    assert should_skip_path(root / ".git" / "HEAD", root)


def test_should_skip_worktrees():
    root = Path("/repo")
    assert should_skip_path(root / ".worktrees" / "other" / "file.py", root)


def test_should_skip_venv():
    root = Path("/repo")
    assert should_skip_path(root / ".venv" / "lib" / "site.py", root)


def test_should_not_skip_compendium_tsv():
    root = Path("/repo")
    assert not should_skip_path(
        root / "compendium" / "disclosure_side_compendium_items_v2.tsv", root
    )


def test_should_not_skip_active_docs():
    root = Path("/repo")
    assert not should_skip_path(
        root / "docs" / "active" / "some-branch" / "convos" / "x.md", root
    )


def test_should_not_skip_src():
    root = Path("/repo")
    assert not should_skip_path(root / "src" / "lobby_analysis" / "loader.py", root)


def test_should_skip_renamer_module(tmp_path: Path):
    """The renamer module itself contains all 16 old→new strings in its
    RENAMES dict. Walking it would rewrite the dict keys (old names) to
    the values (new names), producing self-referential no-op entries."""
    target = tmp_path / "src" / "lobby_analysis" / "row_id_renamer.py"
    target.parent.mkdir(parents=True)
    target.touch()
    assert should_skip_path(target, tmp_path)


def test_should_skip_renamer_test_module(tmp_path: Path):
    """This test file references old names as test inputs; rewriting them
    would destroy the test semantics."""
    target = tmp_path / "tests" / "test_v2_update_names.py"
    target.parent.mkdir(parents=True)
    target.touch()
    assert should_skip_path(target, tmp_path)


def test_should_skip_naming_conventions(tmp_path: Path):
    """NAMING_CONVENTIONS.md needs surgical hand-edit (mark §10 DONE, add
    §10.1 resolver table) — auto-rename corrupts the candidate list semantics."""
    target = tmp_path / "compendium" / "NAMING_CONVENTIONS.md"
    target.parent.mkdir(parents=True)
    target.touch()
    assert should_skip_path(target, tmp_path)


def test_should_skip_status(tmp_path: Path):
    """STATUS.md session-log entries reference old row IDs as historical
    narrative ("we renamed X to Y"). Auto-rename collapses that to "Y to Y"
    and erases the rename's audit trail. Active-table rows and new session
    entries reference new names; the skip means we hand-edit STATUS.md only
    for rows we own (per multi-committer rule)."""
    target = tmp_path / "STATUS.md"
    target.touch()
    assert should_skip_path(target, tmp_path)


# ---------------------------------------------------------------------------
# Integration: walk_and_apply on a fixture tree
# ---------------------------------------------------------------------------


def test_walk_applies_to_tsv_in_fixture(tmp_path: Path):
    """A TSV with an old row ID gets rewritten; row count unchanged."""
    tsv = tmp_path / "compendium" / "disclosure_side_compendium_items_v2.tsv"
    tsv.parent.mkdir(parents=True)
    tsv.write_text(
        "compendium_row_id\tcell_type\n"
        "lobbyist_report_includes_campaign_contributions\tbinary\n"
        "actor_executive_agency_registration_required\tbinary\n"
    )
    result = walk_and_apply(tmp_path, RENAMES, dry_run=False)
    text = tsv.read_text()
    assert "lobbyist_report_includes_campaign_contributions" not in text
    assert "lobbyist_spending_report_includes_campaign_contributions" in text
    assert "actor_executive_agency_registration_required" in text  # untouched
    assert result[tsv] == 1
    # Row count unchanged
    assert len(text.strip().splitlines()) == 3


def test_walk_applies_to_python_file(tmp_path: Path):
    py = tmp_path / "src" / "x.py"
    py.parent.mkdir(parents=True)
    py.write_text('ROW = "lobbying_definition_included_activity_types"\n')
    walk_and_apply(tmp_path, RENAMES, dry_run=False)
    assert "def_lobbying_activity_types" in py.read_text()
    assert "lobbying_definition_included_activity_types" not in py.read_text()


def test_walk_applies_to_markdown(tmp_path: Path):
    md = tmp_path / "docs" / "active" / "x.md"
    md.parent.mkdir(parents=True)
    md.write_text("See `compensation_threshold_for_lobbyist_registration` for D22.\n")
    walk_and_apply(tmp_path, RENAMES, dry_run=False)
    assert "lobbyist_registration_threshold_compensation_dollars" in md.read_text()


def test_walk_skips_historical(tmp_path: Path):
    """Historical archives are immutable per plan §5 E4."""
    hist = tmp_path / "docs" / "historical" / "old-branch" / "x.md"
    hist.parent.mkdir(parents=True)
    original = "old `compensation_threshold_for_lobbyist_registration` reference\n"
    hist.write_text(original)
    walk_and_apply(tmp_path, RENAMES, dry_run=False)
    assert hist.read_text() == original


def test_walk_skips_deprecated(tmp_path: Path):
    """v1 archive is immutable."""
    dep = tmp_path / "compendium" / "_deprecated" / "v1" / "items.tsv"
    dep.parent.mkdir(parents=True)
    original = "compendium_row_id\nlobbyist_report_includes_campaign_contributions\n"
    dep.write_text(original)
    walk_and_apply(tmp_path, RENAMES, dry_run=False)
    assert dep.read_text() == original


def test_walk_dry_run_does_not_mutate(tmp_path: Path):
    tsv = tmp_path / "compendium" / "items.tsv"
    tsv.parent.mkdir(parents=True)
    original = "compendium_row_id\nlobbyist_report_includes_campaign_contributions\n"
    tsv.write_text(original)
    result = walk_and_apply(tmp_path, RENAMES, dry_run=True)
    assert tsv.read_text() == original
    assert result[tsv] == 1  # dry-run still reports what WOULD change


def test_walk_idempotent_on_already_renamed_tree(tmp_path: Path):
    tsv = tmp_path / "compendium" / "items.tsv"
    tsv.parent.mkdir(parents=True)
    tsv.write_text(
        "compendium_row_id\nlobbyist_spending_report_includes_campaign_contributions\n"
    )
    result = walk_and_apply(tmp_path, RENAMES, dry_run=False)
    # No changes on a tree that already has new names
    assert all(count == 0 for count in result.values())


def test_walk_skips_binary_files(tmp_path: Path):
    """Binary files (PDFs, images) must not be opened as text."""
    pdf = tmp_path / "papers" / "x.pdf"
    pdf.parent.mkdir(parents=True)
    pdf.write_bytes(b"\x89PNG\r\n\x1a\nbinary data")
    # Should not raise
    walk_and_apply(tmp_path, RENAMES, dry_run=False)
    assert pdf.read_bytes() == b"\x89PNG\r\n\x1a\nbinary data"


# ---------------------------------------------------------------------------
# Real-TSV invariants: row count and non-ID column stability
# ---------------------------------------------------------------------------


def test_real_tsv_181_rows_invariant(tmp_path: Path):
    """Apply the renames to a copy of the real v2 TSV. Row count must
    stay at 181 (plus header)."""
    target = tmp_path / "compendium" / V2_TSV.name
    target.parent.mkdir(parents=True)
    shutil.copy(V2_TSV, target)
    walk_and_apply(tmp_path, RENAMES, dry_run=False)
    with target.open() as f:
        rows = list(csv.reader(f, delimiter="\t"))
    assert len(rows) == 182  # 1 header + 181 data
    # Header is unchanged
    assert rows[0][0] == "compendium_row_id"


def test_real_tsv_all_15_old_ids_disappear(tmp_path: Path):
    target = tmp_path / "compendium" / V2_TSV.name
    target.parent.mkdir(parents=True)
    shutil.copy(V2_TSV, target)
    walk_and_apply(tmp_path, RENAMES, dry_run=False)
    text = target.read_text()
    old_row_ids = [k for k in RENAMES if not k.endswith("_projection_mapping")]
    for old in old_row_ids:
        # Substring containment is sufficient because compendium_row_id is column 1;
        # if "old\t" or "old\n" pattern is gone, the row ID is gone.
        # Use word-boundary-aware containment check.
        import re

        assert not re.search(rf"\b{re.escape(old)}\b", text), (
            f"old row ID {old!r} still present in TSV after rename"
        )


def test_real_tsv_all_15_new_ids_present(tmp_path: Path):
    target = tmp_path / "compendium" / V2_TSV.name
    target.parent.mkdir(parents=True)
    shutil.copy(V2_TSV, target)
    walk_and_apply(tmp_path, RENAMES, dry_run=False)
    text = target.read_text()
    new_row_ids = [v for k, v in RENAMES.items() if not k.endswith("_projection_mapping")]
    for new in new_row_ids:
        assert new in text, f"new row ID {new!r} missing from TSV after rename"


def test_real_tsv_non_id_columns_unchanged_for_renamed_rows(tmp_path: Path):
    """The rename touches column 1 only. Columns 2–8 for renamed rows
    must be byte-identical to wherever the row appears in the source TSV.

    This test is idempotency-aware: it works whether the live TSV is in
    pre-apply state (has old IDs) or post-apply state (has new IDs),
    mirroring the renamer's own idempotency property."""
    target = tmp_path / "compendium" / V2_TSV.name
    target.parent.mkdir(parents=True)
    shutil.copy(V2_TSV, target)

    with V2_TSV.open() as f:
        src_rows = list(csv.reader(f, delimiter="\t"))
    src_by_id = {row[0]: row[1:] for row in src_rows[1:]}

    walk_and_apply(tmp_path, RENAMES, dry_run=False)

    with target.open() as f:
        new_rows = list(csv.reader(f, delimiter="\t"))
    new_by_id = {row[0]: row[1:] for row in new_rows[1:]}

    # For each renamed row, look up by either old or new ID in the source
    # (depending on whether the live TSV is pre- or post-apply). Verify the
    # target has the new ID with byte-identical non-ID columns.
    row_renames = {k: v for k, v in RENAMES.items() if not k.endswith("_projection_mapping")}
    for old, new in row_renames.items():
        src_cols = src_by_id.get(old) or src_by_id.get(new)
        assert src_cols is not None, f"neither {old!r} nor {new!r} in source TSV"
        assert new in new_by_id, f"new row {new!r} not in target TSV after apply"
        assert new_by_id[new] == src_cols, (
            f"non-ID columns drifted for {new}"
        )
