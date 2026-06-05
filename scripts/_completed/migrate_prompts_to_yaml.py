"""One-shot migration: 17 narrow-pass `prompt_text` TSV values → YAML sidecar.

Per plan docs/active/wi-tier1-direct-read/plans/20260604_wide_prompt_text_pass.md
Commit 1, step 9: migrate the 17 confirmed-disagreement rows from the
`prompt_text` TSV column to `compendium/source_quotes.yaml`, with citation
suffixes stripped from the model-facing `prompt` field.

This script reads `_SOURCE_QUOTES` + `PATTERN_A_CLARIFIER` + `_PATTERN_A_ROWS`
from `scripts/add_prompt_text_column.py` (the narrow-pass populate script) and
generates the YAML entries. After the YAML lands and Commit 1 GREEN passes,
this script + add_prompt_text_column.py both move to `scripts/_completed/`.

Source-quote key naming convention: ``<rubric>_<vintage>_<section_ref>`` where
``<section_ref>`` keeps the original characters (``§``, ``#``, ``.``,
letters/digits, hyphens) and spaces become underscores. ``§`` is YAML-legal
and matches the projection docs' own notation; staying consistent across all
181 rows when Commit 2 happens.
"""

from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path
from typing import Any

import yaml


_WORKTREE = Path(__file__).resolve().parents[1]
_YAML_OUT = _WORKTREE / "compendium" / "source_quotes.yaml"


def _load_add_prompt_text_module() -> Any:
    """Import the narrow-pass populate script as a module."""
    path = _WORKTREE / "scripts" / "add_prompt_text_column.py"
    if not path.exists():
        # After GREEN, the file moves to _completed/.
        path = _WORKTREE / "scripts" / "_completed" / "add_prompt_text_column.py"
    spec = importlib.util.spec_from_file_location("add_prompt_text_column", path)
    assert spec is not None and spec.loader is not None, f"could not load {path}"
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


# YAML source_quotes key per row_id. Hand-derived from the rubric+section
# tokens visible in each `_SOURCE_QUOTES` citation block. Keeps `§` verbatim
# (matches projection-doc convention).
_SOURCE_QUOTE_KEY_BY_ROW: dict[str, str] = {
    # Pattern A (14) — lobbyist_spending_report_* family
    "lobbyist_spending_report_required": "cpi_2015_IND_201",
    "lobbyist_spending_report_cadence_includes_semiannual": "pri_2010_§III.E2.h.iv",
    "lobbyist_spending_report_categorizes_expenses_by_type": "sunlight_2015_#2_expenditure_transparency_tier_1",
    "lobbyist_spending_report_includes_bill_or_action_identifier": "sunlight_2015_#1_lobbyist_activity_tier_1_2",
    "lobbyist_spending_report_includes_general_issues": "pri_2010_§III.E2.g.i",
    "lobbyist_spending_report_includes_general_subject_matter": "sunlight_2015_#1_lobbyist_activity_tier_0",
    "lobbyist_spending_report_includes_gifts_entertainment_transport_lodging": "pri_2010_§III.E2.f.iii",
    "lobbyist_spending_report_includes_indirect_costs": "pri_2010_§III.E2.f.ii",
    "lobbyist_spending_report_includes_lobbyist_contact_info": "pri_2010_§III.E2.b",
    "lobbyist_spending_report_includes_principal_names": "pri_2010_§III.E2.c",
    "lobbyist_spending_report_includes_specific_bill_number": "pri_2010_§III.E2.g.ii",
    "lobbyist_spending_report_includes_total_compensation": "pri_2010_§III.E2.f.i",
    "lobbyist_spending_report_includes_total_expenditures": "newmark_2017_disclosure_total_expenditures",
    "lobbyist_spending_report_required_when_no_activity": "hiredguns_2007_Q25",
    # Pattern B (3) — lobbyist-side registration rows with inline clarifiers
    "lobbyist_registration_threshold_expenditure_dollars": "newmark_2017_def_expenditure_standard",
    "lobbyist_filing_de_minimis_threshold_time_percent": "pri_2010_§III.D_D2_present",
    "lobbyist_registration_deadline_days_after_first_lobbying": "cpi_2015_IND_200",
}


# Inline clarifier for each of the 3 Pattern B rows, lifted verbatim from the
# citation block in `_SOURCE_QUOTES`. The Pattern B clarifier lives INSIDE
# the citation parens (whereas Pattern A's clarifier is appended after); on
# migration we want only the clarifier text, not the surrounding citation.
_PATTERN_B_CLARIFIER_BY_ROW: dict[str, str] = {
    "lobbyist_registration_threshold_expenditure_dollars": (
        "Asks about the LOBBYIST-DEFINITION expenditure threshold — i.e., the "
        "dollar amount the LOBBYIST spends in lobbying that triggers their "
        "registration as a lobbyist, not a principal-side filing trigger."
    ),
    "lobbyist_filing_de_minimis_threshold_time_percent": (
        "Asks about the LOBBYIST's own filing-de-minimis time-percent "
        "exemption, not a principal-side itemized-reporting threshold."
    ),
    "lobbyist_registration_deadline_days_after_first_lobbying": (
        "Asks about the LOBBYIST's own statutory registration deadline — i.e., "
        "the number of days after first lobbying within which the LOBBYIST "
        "must register, not a principal-side filing trigger."
    ),
}


_TRAILING_CITATION = re.compile(
    r'\s*\((?:CPI |PRI |Sunlight |Newmark |Hired Guns).*\)$',
    re.DOTALL,
)


def _split_source_quote_from_citation(raw: str) -> str:
    """Extract the source-quote portion from a `_SOURCE_QUOTES` value.

    Each `_SOURCE_QUOTES` value has shape: ``"<source quote>" (<citation>)``.
    Returns ``"<source quote>"`` — the quoted text WITH its surrounding
    double-quote characters preserved. The trailing citation block (the
    parenthesized rubric/section/doc reference, possibly including inline
    Pattern B clarifier or cross-rubric notes) is stripped.
    """
    m = _TRAILING_CITATION.search(raw)
    if m is None:
        raise ValueError(
            f"Could not locate trailing citation block in source-quote value: "
            f"{raw!r}"
        )
    return raw[: m.start()]


def _build_yaml_payload() -> dict[str, dict]:
    """Build the YAML payload for the 17 narrow-pass rows."""
    add_prompt = _load_add_prompt_text_module()
    source_quotes_raw: dict[str, str] = add_prompt._SOURCE_QUOTES
    pattern_a_rows: frozenset[str] = add_prompt._PATTERN_A_ROWS
    pattern_a_clarifier: str = add_prompt.PATTERN_A_CLARIFIER

    payload: dict[str, dict] = {}
    missing_keys: list[str] = []
    for row_id, raw_value in source_quotes_raw.items():
        if row_id not in _SOURCE_QUOTE_KEY_BY_ROW:
            missing_keys.append(row_id)
            continue

        source_quote = _split_source_quote_from_citation(raw_value)
        key = _SOURCE_QUOTE_KEY_BY_ROW[row_id]

        # Construct model-facing prompt:
        # - Pattern A rows: <source quote> + Pattern A clarifier (note: the
        #   clarifier already starts with a leading space).
        # - Pattern B rows: <source quote> + inline clarifier (with leading
        #   space inserted here for consistent formatting).
        # - Other rows (none in the narrow pass): <source quote>.
        if row_id in pattern_a_rows:
            prompt = source_quote + pattern_a_clarifier
        elif row_id in _PATTERN_B_CLARIFIER_BY_ROW:
            prompt = source_quote + " " + _PATTERN_B_CLARIFIER_BY_ROW[row_id]
        else:
            prompt = source_quote

        payload[row_id] = {
            "source_quotes": {key: source_quote},
            "prompt": prompt,
        }

    if missing_keys:
        raise SystemExit(
            f"_SOURCE_QUOTE_KEY_BY_ROW missing entries for rows: {missing_keys}"
        )
    return payload


def _str_representer(dumper: yaml.SafeDumper, data: str):
    """Force literal-block style (``|``) for multi-line strings; otherwise
    use double-quoted to keep long-but-single-line strings unambiguous on
    diff inspection. (Default ``plain`` style would emit some strings as
    folded blocks for long lines, which obscures the actual content.)"""
    if "\n" in data:
        return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")
    return dumper.represent_scalar("tag:yaml.org,2002:str", data, style='"')


yaml.SafeDumper.add_representer(str, _str_representer)


def main() -> None:
    payload = _build_yaml_payload()
    assert len(payload) == 17, f"expected 17 narrow-pass rows, got {len(payload)}"

    # Sort by row_id for stable diff output.
    sorted_payload = {k: payload[k] for k in sorted(payload)}

    header = (
        "# compendium/source_quotes.yaml\n"
        "#\n"
        "# Source-quotes sidecar — prompt SSOT for the tier-1 dispatch.\n"
        "#\n"
        "# Per-row schema:\n"
        "#   <compendium_row_id>:\n"
        "#     source_quotes:                            # non-empty dict\n"
        "#       <rubric>_<vintage>_<section_ref>: \"<verbatim quote>\"\n"
        "#     prompt: \"<what the model sees>\"        # non-empty string\n"
        "#\n"
        "# `source_quotes` is immutable reference material; provenance lives\n"
        "# in the keys. `prompt` is mutable — the Ralph loop edits it.\n"
        "# Citations DO NOT appear inside the `prompt` value; they live in\n"
        "# the `source_quotes` keys only. See\n"
        "# `convos/20260604_wide_pass_yaml_sidecar_design.md` for the design.\n"
        "#\n"
        "# Commit 1 (wide-pass plan): 17 narrow-pass rows migrated from the\n"
        "# now-dropped `prompt_text` TSV column. Commit 2 populates the\n"
        "# remaining 164.\n"
        "\n"
    )

    rendered = yaml.safe_dump(
        sorted_payload,
        default_flow_style=False,
        allow_unicode=True,
        width=1000,  # avoid line-wrapping artifacts
        sort_keys=False,
    )
    _YAML_OUT.write_text(header + rendered, encoding="utf-8")
    print(f"Wrote {_YAML_OUT}")
    print(f"  rows populated: {len(sorted_payload)}")


if __name__ == "__main__":
    main()
