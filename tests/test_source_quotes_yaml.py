"""Tests for the source-quotes YAML SSOT + loader + registry plumbing.

Background: convo 20260604_wide_pass_yaml_sidecar_design settled on a sidecar
YAML at ``compendium/source_quotes.yaml`` as the prompt SSOT for the tier-1
dispatch. The narrow-pass ``prompt_text`` TSV column gets dropped; the
runtime reads prompts from YAML directly via the registry. Per-row YAML
schema is two flat fields:

- ``source_quotes`` — immutable dict keyed by rubric+section ref, holding
  verbatim reference material. Provenance lives here.
- ``prompt`` — mutable flat string. What the model actually sees. Initially
  populated as the most relevant verbatim source quote (with no embedded
  citation); evolved by a future Ralph loop.

Commit 1 scope (this test file):
- the YAML loader (file existence, typed return, malformed-entry rejection)
- the 17 narrow-pass rows migrated from TSV → YAML (clarifier preservation,
  no citation suffixes in the model-facing ``prompt``)
- the ``CompendiumCellSpec.prompt`` field, renamed from ``prompt_text`` and
  populated from YAML (not from the dropped TSV column)
- the renderer reading ``spec.prompt`` end-to-end via YAML

Wide-pass coverage tests (all 181 rows have nonempty prompt, etc.) belong to
Commit 2 per ``plans/20260604_wide_prompt_text_pass.md``.
"""

from __future__ import annotations

import importlib.util
import sys
import textwrap
from pathlib import Path

import pytest


_WORKTREE = Path(__file__).resolve().parents[1]
_SCRIPTS = _WORKTREE / "scripts"


def _load(module_name: str, path: Path):
    spec = importlib.util.spec_from_file_location(module_name, path)
    assert spec is not None and spec.loader is not None, f"could not load {path}"
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


# Tier-1 is loaded lazily inside individual tests that need its renderer —
# top-level load would force-evaluate the worktree-state of tier_0 and could
# couple imports in a way that hides test failures.


# The 17 confirmed-disagreement rows migrated to YAML in Commit 1 (14 Pattern
# A + 3 Pattern B per ``results/20260603_prior_art_adjudication_of_18_disagreements.md``
# and ``scripts/add_prompt_text_column.py``).
_NARROW_PASS_ROWS: frozenset[str] = frozenset(
    {
        # Pattern A (14): lobbyist_spending_report_* family, lobbyist-vs-principal
        # filer disambiguation. Each carries the Pattern A clarifier.
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
        # Pattern B (3): lobbyist-side registration rows with inline clarifiers.
        "lobbyist_registration_threshold_expenditure_dollars",
        "lobbyist_filing_de_minimis_threshold_time_percent",
        "lobbyist_registration_deadline_days_after_first_lobbying",
    }
)


_PATTERN_A_ANCHOR = "lobbyist_spending_report_required"
_PATTERN_A_CLARIFIER_FRAGMENT = (
    "Asks whether the LOBBYIST is the named filer of a separate spending report"
)


# ---------------------------------------------------------------------------
# YAML loader — file existence + typed return shape
# ---------------------------------------------------------------------------


def test_yaml_file_exists_at_canonical_path():
    """The sidecar YAML must live at ``compendium/source_quotes.yaml`` — that
    is the path the loader resolves to and the runtime reads at registry-build
    time."""
    yaml_path = _WORKTREE / "compendium" / "source_quotes.yaml"
    assert yaml_path.exists(), (
        f"source_quotes.yaml missing at canonical path: {yaml_path}. "
        "Per plan 20260604_wide_prompt_text_pass.md, Commit 1 scaffolds this "
        "file and migrates the 17 narrow-pass rows into it."
    )


def test_loader_module_importable():
    """``lobby_analysis.source_quotes_loader`` is the module name. The loader
    is a flat module alongside ``compendium_loader.py`` (matches the existing
    package layout — there is no ``compendium/`` subpackage in ``src``)."""
    from lobby_analysis.source_quotes_loader import load_source_quotes  # noqa: F401


def test_loader_returns_dict_of_entries_with_source_quotes_and_prompt():
    """``load_source_quotes()`` returns a dict keyed by ``compendium_row_id``;
    each entry exposes a non-empty ``source_quotes`` dict and a non-empty
    ``prompt`` string. Asserted against the Pattern A anchor row, which is
    populated in Commit 1."""
    from lobby_analysis.source_quotes_loader import load_source_quotes

    entries = load_source_quotes()
    assert isinstance(entries, dict)
    assert _PATTERN_A_ANCHOR in entries, (
        f"loader did not return entry for narrow-pass anchor "
        f"{_PATTERN_A_ANCHOR!r}; entries have {len(entries)} keys"
    )
    entry = entries[_PATTERN_A_ANCHOR]
    # Behavioral attributes (not type structure): the entry must carry the
    # two fields the renderer + registry will consume.
    assert isinstance(entry.source_quotes, dict)
    assert entry.source_quotes, "source_quotes dict is empty for anchor row"
    assert isinstance(entry.prompt, str)
    assert entry.prompt, "prompt string is empty for anchor row"


# ---------------------------------------------------------------------------
# YAML loader — explicit path + error handling on malformed entries
# ---------------------------------------------------------------------------


def test_loader_accepts_explicit_path_argument(tmp_path):
    """Like ``load_v2_compendium``, the loader accepts an explicit path so
    tests can point it at fixture YAML rather than the real file."""
    from lobby_analysis.source_quotes_loader import load_source_quotes

    yaml_path = tmp_path / "fixture.yaml"
    yaml_path.write_text(
        textwrap.dedent(
            """\
            example_row_id:
              source_quotes:
                example_rubric_2026_section_1: "verbatim quote here"
              prompt: |
                The model-facing prompt for example_row_id.
            """
        ),
        encoding="utf-8",
    )

    entries = load_source_quotes(yaml_path)
    assert set(entries.keys()) == {"example_row_id"}
    entry = entries["example_row_id"]
    assert entry.source_quotes == {
        "example_rubric_2026_section_1": "verbatim quote here"
    }
    assert "model-facing prompt" in entry.prompt


def test_loader_rejects_entry_missing_prompt_key(tmp_path):
    """A YAML entry without a ``prompt`` key is a contract violation — the
    loader raises a clear error naming the row_id."""
    from lobby_analysis.source_quotes_loader import load_source_quotes

    yaml_path = tmp_path / "bad.yaml"
    yaml_path.write_text(
        textwrap.dedent(
            """\
            example_row_id:
              source_quotes:
                rubric_a: "quote"
            """
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError) as excinfo:
        load_source_quotes(yaml_path)
    assert "example_row_id" in str(excinfo.value)
    assert "prompt" in str(excinfo.value)


def test_loader_rejects_entry_with_empty_source_quotes(tmp_path):
    """``source_quotes`` must be non-empty — provenance is load-bearing. An
    empty dict gets rejected with a clear, row-keyed error."""
    from lobby_analysis.source_quotes_loader import load_source_quotes

    yaml_path = tmp_path / "bad.yaml"
    yaml_path.write_text(
        textwrap.dedent(
            """\
            example_row_id:
              source_quotes: {}
              prompt: "some prompt"
            """
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError) as excinfo:
        load_source_quotes(yaml_path)
    assert "example_row_id" in str(excinfo.value)
    assert "source_quotes" in str(excinfo.value)


def test_loader_rejects_entry_with_empty_prompt(tmp_path):
    """An empty ``prompt`` value is rejected — the registry consumer expects
    a non-empty string (and an empty string would silently neuter the model
    prompt)."""
    from lobby_analysis.source_quotes_loader import load_source_quotes

    yaml_path = tmp_path / "bad.yaml"
    yaml_path.write_text(
        textwrap.dedent(
            """\
            example_row_id:
              source_quotes:
                rubric_a: "quote"
              prompt: ""
            """
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError) as excinfo:
        load_source_quotes(yaml_path)
    assert "example_row_id" in str(excinfo.value)
    assert "prompt" in str(excinfo.value)


# ---------------------------------------------------------------------------
# 17-row migration — narrow-pass behavior preserved across TSV → YAML move
# ---------------------------------------------------------------------------


def test_all_17_narrow_pass_rows_present_in_yaml():
    """Each of the 17 confirmed-disagreement rows must have a YAML entry
    after Commit 1's migration. Otherwise the narrow-pass validation
    ($4.7504 of API spend) silently regresses."""
    from lobby_analysis.source_quotes_loader import load_source_quotes

    entries = load_source_quotes()
    missing = sorted(_NARROW_PASS_ROWS - set(entries))
    assert not missing, (
        f"{len(missing)} of 17 narrow-pass rows missing from YAML: {missing}"
    )


def test_pattern_a_anchor_prompt_preserves_clarifier_after_migration():
    """The Pattern A clarifier — added to all 14 Pattern A rows in
    convo 20260603 iter-2 — must survive the YAML migration verbatim.
    Without it, Pattern A's 14/14 collapse regresses; that's the
    load-bearing migration-correctness check.

    Verified on the anchor row ``lobbyist_spending_report_required``."""
    from lobby_analysis.source_quotes_loader import load_source_quotes

    entries = load_source_quotes()
    entry = entries[_PATTERN_A_ANCHOR]
    assert _PATTERN_A_CLARIFIER_FRAGMENT in entry.prompt, (
        f"Pattern A clarifier missing from {_PATTERN_A_ANCHOR!r} prompt "
        f"after migration. prompt={entry.prompt!r}"
    )


def test_narrow_pass_prompts_have_no_embedded_citations():
    """The model-facing ``prompt`` strings must NOT contain the
    ``(<rubric> <section>; <doc>.)`` citation suffixes that the narrow-pass
    TSV embedded. Per the wide-pass design, citations live only in
    ``source_quotes`` keys; the model sees the substantive question alone.

    Patterns checked are the literal prefixes the narrow-pass script
    appended: ``(CPI 2015``, ``(PRI 2010``, ``(Sunlight 2015``, etc.
    Tested across all 17 migrated rows."""
    from lobby_analysis.source_quotes_loader import load_source_quotes

    leaked_patterns = (
        "(CPI 2015",
        "(PRI 2010",
        "(Sunlight 2015",
        "(Newmark 2017",
        "(Hired Guns",
        "projection_mapping.md",
    )

    entries = load_source_quotes()
    leaks: dict[str, list[str]] = {}
    for row_id in _NARROW_PASS_ROWS:
        prompt = entries[row_id].prompt
        hits = [pat for pat in leaked_patterns if pat in prompt]
        if hits:
            leaks[row_id] = hits

    assert not leaks, (
        "Citation leakage into model-facing prompt strings — citations should "
        f"live only in source_quotes YAML keys.\nLeaks: {leaks}"
    )


def test_narrow_pass_source_quotes_dicts_carry_provenance_keys():
    """For each of the 17 migrated rows, the ``source_quotes`` dict must have
    at least one rubric-keyed entry. The key naming convention surfaces the
    rubric + section ref; the value carries the verbatim quote (which used to
    be embedded inside ``prompt_text``)."""
    from lobby_analysis.source_quotes_loader import load_source_quotes

    entries = load_source_quotes()
    empty: list[str] = []
    for row_id in _NARROW_PASS_ROWS:
        sq = entries[row_id].source_quotes
        if not sq:
            empty.append(row_id)
    assert not empty, f"{len(empty)} narrow-pass rows have empty source_quotes: {empty}"


# ---------------------------------------------------------------------------
# Registry plumbing — ``CompendiumCellSpec.prompt`` populated from YAML
# ---------------------------------------------------------------------------


def test_cell_spec_has_prompt_field_default_none():
    """``CompendiumCellSpec`` exposes a ``prompt: str | None`` attribute.
    Rows not yet covered by YAML (pre-Commit 2: the 164 wide-pass rows) get
    ``None``."""
    from lobby_analysis.models_v2.cell_spec import CompendiumCellSpec
    from lobby_analysis.models_v2.cells import BinaryCell

    spec = CompendiumCellSpec(
        row_id="x", axis="legal", expected_cell_class=BinaryCell
    )
    assert spec.prompt is None


def test_cell_spec_does_not_expose_prompt_text_attribute():
    """The old field name is gone (rename, not alias). Any code that still
    references ``spec.prompt_text`` will raise AttributeError — that's the
    intentional callable failure that catches stragglers."""
    from lobby_analysis.models_v2.cell_spec import CompendiumCellSpec
    from lobby_analysis.models_v2.cells import BinaryCell

    spec = CompendiumCellSpec(
        row_id="x", axis="legal", expected_cell_class=BinaryCell
    )
    assert not hasattr(spec, "prompt_text"), (
        "CompendiumCellSpec still exposes the old 'prompt_text' attribute; "
        "expected rename to 'prompt' per plan 20260604_wide_prompt_text_pass.md"
    )


def test_registry_populates_prompt_from_yaml_for_pattern_a_anchor():
    """``build_cell_spec_registry()`` reads from the YAML loader, not the
    dropped TSV column. The Pattern A anchor row's ``spec.prompt`` matches
    the YAML's ``prompt`` for that row."""
    from lobby_analysis.models_v2.cell_spec import build_cell_spec_registry
    from lobby_analysis.source_quotes_loader import load_source_quotes

    registry = build_cell_spec_registry()
    entries = load_source_quotes()

    spec = registry[(_PATTERN_A_ANCHOR, "legal")]
    assert spec.prompt is not None
    assert spec.prompt == entries[_PATTERN_A_ANCHOR].prompt


def test_registry_populates_prompt_for_all_17_narrow_pass_rows():
    """All 17 narrow-pass rows have a non-empty ``spec.prompt`` after
    Commit 1's migration. Equivalent to the prior
    ``test_registry_populates_prompt_text_for_all_17_disagreement_rows`` but
    keyed on the renamed field."""
    from lobby_analysis.models_v2.cell_spec import build_cell_spec_registry

    registry = build_cell_spec_registry()
    missing: list[str] = []
    for row_id in _NARROW_PASS_ROWS:
        spec = registry[(row_id, "legal")]
        if not spec.prompt:
            missing.append(row_id)
    assert not missing, (
        f"{len(missing)} of 17 narrow-pass rows missing prompt: {sorted(missing)}"
    )


# ---------------------------------------------------------------------------
# Wide-pass coverage — Commit 2 (164-row population from projection docs)
# ---------------------------------------------------------------------------
#
# These tests assert the post-wide-pass YAML state:
#   - every v2 compendium row (181 total) has a non-empty `prompt`
#   - no citation-bake-in patterns leak into model-facing `prompt` strings
#   - the 2 outlier rows (LobbyView schema-coverage + OpenSecrets-tabled) carry
#     their hand-keyed `source_quotes` entries
#
# They INTENTIONALLY fail before Commit 2's GREEN — the Commit-1 stub
# `test_registry_leaves_prompt_none_for_rows_not_in_yaml` was the placeholder
# the wide pass invalidates by populating every row. `test_all_181_rows_*`
# covers the inverted contract: every row has a prompt, not just the 17 from
# Commit 1.


_LOBBYVIEW_OUTLIER = "lobbyist_filing_distinguishes_in_house_vs_contract_filer"
_OPENSECRETS_OUTLIER = "separate_registrations_for_lobbyists_and_clients"


def _all_v2_row_ids() -> set[str]:
    """Load every row_id from the v2 compendium TSV.

    Mirrors what ``build_cell_spec_registry`` reads as the row-set contract —
    if a row is in the TSV it must have a YAML entry post-Commit-2.
    """
    from lobby_analysis.compendium_loader import load_v2_compendium

    return {row["compendium_row_id"] for row in load_v2_compendium()}


def test_all_181_rows_have_nonempty_prompt():
    """Every row in the v2 compendium TSV must have a non-empty
    ``prompt`` in the YAML SSOT after Commit 2. Catches the
    add-row-to-TSV-but-forget-the-YAML drift class.
    """
    from lobby_analysis.source_quotes_loader import load_source_quotes

    entries = load_source_quotes()
    tsv_rows = _all_v2_row_ids()

    missing_entries = sorted(tsv_rows - set(entries))
    empty_prompts = sorted(
        row_id for row_id in (tsv_rows & set(entries))
        if not entries[row_id].prompt
    )

    assert not missing_entries, (
        f"{len(missing_entries)} of {len(tsv_rows)} TSV rows missing from "
        f"source_quotes.yaml after Commit 2: {missing_entries[:10]}"
        f"{'…' if len(missing_entries) > 10 else ''}"
    )
    assert not empty_prompts, (
        f"{len(empty_prompts)} rows present but have empty prompt: "
        f"{empty_prompts[:10]}{'…' if len(empty_prompts) > 10 else ''}"
    )


def test_all_181_rows_have_nonempty_source_quotes():
    """Every row's ``source_quotes`` dict is non-empty (provenance is
    load-bearing — the loader rejects empty dicts at parse time, but this
    test pins the contract at the all-rows level as a regression guard).
    """
    from lobby_analysis.source_quotes_loader import load_source_quotes

    entries = load_source_quotes()
    tsv_rows = _all_v2_row_ids()

    empty: list[str] = []
    for row_id in tsv_rows & set(entries):
        if not entries[row_id].source_quotes:
            empty.append(row_id)
    assert not empty, (
        f"{len(empty)} rows have empty source_quotes after Commit 2: {empty[:10]}"
    )


def test_no_citations_leaked_into_prompt_strings_across_all_rows():
    """The model-facing ``prompt`` strings must not contain rubric-citation
    prefixes anywhere across the 181 rows. The verbatim quote alone is what
    the model sees; provenance lives in ``source_quotes`` keys.

    Patterns checked are the literal citation prefixes the projection docs
    use after each quoted ``"…"`` block. False positives are possible in
    principle (a verbatim quote could quote a citation), but in practice
    none of the 9 source rubrics' question text quotes a citation marker.
    """
    from lobby_analysis.source_quotes_loader import load_source_quotes

    leaked_patterns = (
        "(CPI 2015",
        "(PRI 2010",
        "(Sunlight 2015",
        "(Newmark 2017",
        "(Newmark 2005",
        "(Hired Guns",
        "(FOCAL",
        "(Suppl",
        "(CPI_2007",
        "(Opheim",
        "projection_mapping.md",
        "hired_guns_methodology.txt",
    )

    entries = load_source_quotes()
    leaks: dict[str, list[str]] = {}
    for row_id, entry in entries.items():
        hits = [pat for pat in leaked_patterns if pat in entry.prompt]
        if hits:
            leaks[row_id] = hits

    assert not leaks, (
        "Citation leakage into model-facing prompt strings — citations should "
        f"live only in source_quotes YAML keys.\n"
        f"Affected rows ({len(leaks)}): "
        f"{dict(list(leaks.items())[:5])}"
        f"{'…' if len(leaks) > 5 else ''}"
    )


def test_lobbyview_outlier_row_has_lobbyview_keyed_source_quote():
    """The LobbyView schema-coverage outlier row (``first_introduced_by =
    lobbyview_schema_coverage.md``) has a ``source_quotes`` entry keyed under
    a ``lobbyview_2018_schema_field`` namespace, per plan step 19. The
    paper's source has no quotable question; provenance is the schema-field
    origin."""
    from lobby_analysis.source_quotes_loader import load_source_quotes

    entries = load_source_quotes()
    assert _LOBBYVIEW_OUTLIER in entries, (
        f"LobbyView outlier row {_LOBBYVIEW_OUTLIER!r} missing from YAML"
    )
    entry = entries[_LOBBYVIEW_OUTLIER]
    matching_keys = [k for k in entry.source_quotes if k.startswith("lobbyview_2018")]
    assert matching_keys, (
        f"{_LOBBYVIEW_OUTLIER!r} source_quotes lacks a `lobbyview_2018_*` key; "
        f"got keys {list(entry.source_quotes)}"
    )


def test_opensecrets_outlier_row_has_opensecrets_keyed_source_quote():
    """The OpenSecrets-tabled outlier row (``first_introduced_by =
    _tabled/opensecrets_2022_tabled.md``) has a ``source_quotes`` entry keyed
    under an ``opensecrets_2022_tabled`` namespace, per plan step 19. Quote
    is lifted from line 48 of the tabled doc."""
    from lobby_analysis.source_quotes_loader import load_source_quotes

    entries = load_source_quotes()
    assert _OPENSECRETS_OUTLIER in entries, (
        f"OpenSecrets-tabled outlier row {_OPENSECRETS_OUTLIER!r} missing from YAML"
    )
    entry = entries[_OPENSECRETS_OUTLIER]
    matching_keys = [k for k in entry.source_quotes if k.startswith("opensecrets_2022_tabled")]
    assert matching_keys, (
        f"{_OPENSECRETS_OUTLIER!r} source_quotes lacks an `opensecrets_2022_tabled*` "
        f"key; got keys {list(entry.source_quotes)}"
    )
