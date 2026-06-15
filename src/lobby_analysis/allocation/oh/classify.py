"""Phase-1 classifiers for the OH chain composer (pure-logic, no I/O).

Plan: ``docs/active/oh-portal-extraction/plans/20260611_oh_chain_composer_design.md``
§4a (position-shape truth table) and §6 (label-pattern routing).

Two orthogonal classifications, both invoked at the seam between extraction
JSON and DataFrame composition:

- **Step A — position shape.** Which of the three subject-carrying fields on
  ``LobbyingPosition`` actually carries the lobbying subject for this row.
  The mini-quirk case (`subject_hoisted_from_description`) was documented in
  the 2026-06-13 mini-swap findings: mini emits subject content into
  ``description`` rather than the canonical ``general_issue_area``. Without
  Step A, subject-only positions silently drop from the chain (the original
  plan derived ``bill_label_raw`` from ``bill_reference.original_text``
  alone).

- **Step B — label pattern.** Given a label string + its position-kind,
  classify into ``bill`` / ``oac_rule`` / ``jcarr`` / ``subject`` /
  ``unmatched``. Drives the Plural Policy join (only ``bill`` rows are
  joinable) and downstream ``bill_id`` nullability.

Both functions are pure: no data access, no network, no side effects. They
are the foundation of every downstream phase and are validated only by unit
tests with hand-crafted ``LobbyingPosition`` fixtures.
"""

from __future__ import annotations

import re
from typing import Literal

from lobby_analysis.models.filings import LobbyingPosition


# ---------------------------------------------------------------------------
# String constants for the enum values (Literal typing, codebase convention)
# ---------------------------------------------------------------------------

# Position-shape kinds (§4a truth table)
POSITION_KIND_BILL_REFERENCED = "bill_referenced"
POSITION_KIND_SUBJECT_GENERAL = "subject_general"
POSITION_KIND_SUBJECT_HOISTED = "subject_hoisted_from_description"

PositionKind = Literal[
    "bill_referenced",
    "subject_general",
    "subject_hoisted_from_description",
]

# Bill-class labels (§6 OAC table + 2026-06-14 subject row)
BILL_CLASS_BILL = "bill"
BILL_CLASS_JCARR = "jcarr"
BILL_CLASS_OAC_RULE = "oac_rule"
BILL_CLASS_SUBJECT = "subject"
BILL_CLASS_UNMATCHED = "unmatched"

BillClass = Literal["bill", "jcarr", "oac_rule", "subject", "unmatched"]


# ---------------------------------------------------------------------------
# Regex patterns for Step B
# ---------------------------------------------------------------------------

# OH legislative bill prefixes — eight valid forms per §3 of the plan and
# the smoke-test top-10 sample.
_BILL_PATTERN = re.compile(
    r"^(?:HB|SB|HR|SR|HJR|SJR|HCR|SCR)\s+\d+(?:\s|$)",
    re.IGNORECASE,
)

# JCARR — JC prefix followed by an OAC-shaped rule citation.
# The smoke test's top-10 shows variants like 'JC 4731-24-03' and
# 'JC 4901:1-16-01 THROUGH 4901:1-16-06' (ranges); we match the JC + digit
# prefix and let downstream consumers handle range expansion.
_JCARR_PATTERN = re.compile(r"^JC\s+\d", re.IGNORECASE)

# OAC administrative rule — bare digits-dash-digits-dash-digits, no JC prefix.
# Per the smoke test: '5160-32-02', '5123-4-03'. The OAC structure is
# title-chapter-rule, where each segment is one-or-more digits (chapter and
# rule can also carry letter suffixes in some rules, but the smoke-test
# sample is digit-only; future widening is a defensible v0.1 change).
_OAC_PATTERN = re.compile(r"^\d+-\d+-\d+")


def classify_position_shape(position: LobbyingPosition) -> PositionKind:
    """Step A: map a LobbyingPosition to its position-shape per §4a.

    Precedence (highest → lowest):

    1. ``bill_reference`` is set → ``bill_referenced``. A position can
       legitimately carry both a bill_reference and a general_issue_area /
       description; bill_reference wins because it produces a join-eligible
       row in the chain.
    2. ``general_issue_area`` is set (and bill_reference is None) →
       ``subject_general``. The canonical sonnet shape.
    3. ``description`` is set (and the above are None) →
       ``subject_hoisted_from_description``. The mini-model quirk.

    Raises ``ValueError`` if all three subject-carrying fields are empty or
    whitespace-only — an empty position is an upstream extraction defect and
    should surface, not silently emit an empty chain row.
    """
    if position.bill_reference is not None:
        return POSITION_KIND_BILL_REFERENCED

    if position.general_issue_area and position.general_issue_area.strip():
        return POSITION_KIND_SUBJECT_GENERAL

    if position.description and position.description.strip():
        return POSITION_KIND_SUBJECT_HOISTED

    raise ValueError(
        "LobbyingPosition has empty bill_reference, general_issue_area, "
        "and description — cannot classify position shape. This indicates "
        "an upstream extraction defect; surface to the implementer rather "
        "than silently emitting an empty chain row."
    )


def extract_position_label(position: LobbyingPosition) -> str:
    """Produce the unified 'what was lobbied' string for downstream classify.

    Selection mirrors :func:`classify_position_shape`:

    - ``bill_referenced`` → ``bill_reference.original_text``
    - ``subject_general`` → ``general_issue_area``
    - ``subject_hoisted_from_description`` → ``description``

    Returns the value with surrounding whitespace stripped. Raises on empty
    positions (same contract as ``classify_position_shape``).
    """
    kind = classify_position_shape(position)
    if kind == POSITION_KIND_BILL_REFERENCED:
        # bill_reference is not None per the kind contract.
        return position.bill_reference.original_text.strip()  # type: ignore[union-attr]
    if kind == POSITION_KIND_SUBJECT_GENERAL:
        return position.general_issue_area.strip()  # type: ignore[union-attr]
    # kind == POSITION_KIND_SUBJECT_HOISTED by exhaustion.
    return position.description.strip()  # type: ignore[union-attr]


def classify_bill_label(label: str, position_kind: PositionKind) -> BillClass:
    """Step B: classify a label string into bill / oac_rule / jcarr / subject / unmatched.

    The ``position_kind`` argument is load-bearing: subject-only positions
    (kinds ``subject_general`` and ``subject_hoisted_from_description``)
    always classify as ``subject`` regardless of the label's textual form,
    because they carry no ``bill_reference`` and therefore produce no join-
    eligible row in the chain. This is the §4a "kind wins over text"
    contract — without it, a general_issue_area happening to contain
    'HB 96 BUDGET ADVOCACY' would falsely flag as a bill.

    For ``bill_referenced`` positions, classification is by textual pattern:

    - Eight OH legislative prefixes (HB, SB, HR, SR, HJR, SJR, HCR, SCR)
      followed by digits → ``bill``.
    - ``JC <digits...>`` → ``jcarr`` (joint committee on administrative rule
      review; not joinable to ``OH_136_bills.csv``).
    - Bare ``\\d+-\\d+-\\d+`` → ``oac_rule`` (Ohio Administrative Code; not
      joinable to ``OH_136_bills.csv``).
    - Anything else → ``unmatched`` (flagged in the chain, not dropped, so
      malformed bill_references surface in audit rather than silently
      joining as bills).

    The order of checks matters: JCARR is tested before OAC because a JC
    prefix would otherwise match the OAC pattern's prefix.
    """
    # Subject-kind contract: kind wins over text.
    if position_kind in (
        POSITION_KIND_SUBJECT_GENERAL,
        POSITION_KIND_SUBJECT_HOISTED,
    ):
        return BILL_CLASS_SUBJECT

    # bill_referenced kind: pattern-match the label.
    stripped = label.strip() if label else ""
    if not stripped:
        return BILL_CLASS_UNMATCHED

    # Precedence: JCARR before OAC (JC prefix is a strict superset).
    if _JCARR_PATTERN.match(stripped):
        return BILL_CLASS_JCARR
    if _BILL_PATTERN.match(stripped):
        return BILL_CLASS_BILL
    if _OAC_PATTERN.match(stripped):
        return BILL_CLASS_OAC_RULE
    return BILL_CLASS_UNMATCHED
