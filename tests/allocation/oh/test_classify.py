"""TDD tests for the OH Phase-1 classifier (both steps).

Plan: ``docs/active/oh-portal-extraction/plans/20260611_oh_chain_composer_design.md``
§4a (position-shape truth table) and §6 (OAC/JCARR/bill label patterns).

Step A — position-shape classification: maps each ``LobbyingPosition`` to one
of three kinds based on which fields are populated. Required because the
extractor can produce three real position shapes:

    (a) bill-referenced              — ``bill_reference`` is set
    (b) subject_general              — ``bill_reference`` is None, ``general_issue_area`` is set
    (c) subject_hoisted_from_description — both above are None, ``description`` is set
                                       (the mini-model quirk documented in the
                                       2026-06-13 findings doc)

Step B — label-pattern classification: regex-classifies the unified label
string into one of: ``bill`` / ``oac_rule`` / ``jcarr`` / ``subject`` /
``unmatched``. The ``subject`` class is added 2026-06-14 to cover the
non-bill-pattern outputs of Step A (cases b and c).

Source data for the pattern set: the smoke-test in
``docs/active/oh-portal-extraction/results/20260611_plural_policy_data_landed.md``
(74.6% distinct-label / 86.4% row-weighted match against ``OH_136_bills.csv``;
the 13.6% unmatched is exclusively OAC + JCARR per that doc).

These tests are pure-logic — no data files, no network, no fixtures from disk.
They run in any environment with the source tree available.
"""

from __future__ import annotations

import pytest

from lobby_analysis.allocation.oh.classify import (
    BILL_CLASS_BILL,
    BILL_CLASS_JCARR,
    BILL_CLASS_OAC_RULE,
    BILL_CLASS_SUBJECT,
    BILL_CLASS_UNMATCHED,
    POSITION_KIND_BILL_REFERENCED,
    POSITION_KIND_SUBJECT_GENERAL,
    POSITION_KIND_SUBJECT_HOISTED,
    classify_bill_label,
    classify_position_shape,
    extract_position_label,
)
from lobby_analysis.models.entities import BillReference
from lobby_analysis.models.filings import LobbyingPosition


# ---------------------------------------------------------------------------
# Step A — position-shape classification (§4a truth table)
# ---------------------------------------------------------------------------


class TestClassifyPositionShape:
    """Step A: which field carries the lobbying subject?"""

    def test_bill_referenced_canonical(self):
        """Case (a): bill_reference set → bill_referenced."""
        position = LobbyingPosition(
            bill_reference=BillReference(original_text="HB 96"),
        )
        assert classify_position_shape(position) == POSITION_KIND_BILL_REFERENCED

    def test_bill_referenced_with_other_fields_also_populated(self):
        """Case (a) wins over (b) and (c) when bill_reference is present.

        A position can legitimately carry both a bill_reference and a
        general_issue_area / description; bill_reference takes precedence
        because it produces a join-eligible row in the chain.
        """
        position = LobbyingPosition(
            bill_reference=BillReference(original_text="HB 96"),
            general_issue_area="HEALTH CARE",
            description="Supported budget appropriation for Medicaid.",
        )
        assert classify_position_shape(position) == POSITION_KIND_BILL_REFERENCED

    def test_subject_general(self):
        """Case (b): bill_reference None, general_issue_area set."""
        position = LobbyingPosition(
            bill_reference=None,
            general_issue_area="MEDICAID / HOME CARE / HOSPICE",
        )
        assert classify_position_shape(position) == POSITION_KIND_SUBJECT_GENERAL

    def test_subject_general_wins_over_description(self):
        """Case (b) wins over (c) when general_issue_area is populated.

        Sonnet emits the canonical (b); only when general_issue_area is None
        do we fall through to the mini-quirk case (c).
        """
        position = LobbyingPosition(
            bill_reference=None,
            general_issue_area="HEALTH CARE",
            description="Advocated on broader topic of regulatory reform.",
        )
        assert classify_position_shape(position) == POSITION_KIND_SUBJECT_GENERAL

    def test_subject_hoisted_from_description(self):
        """Case (c): both upper fields None, description set (mini quirk)."""
        position = LobbyingPosition(
            bill_reference=None,
            general_issue_area=None,
            description="MEDICAID / HOME CARE / HOSPICE",
        )
        assert classify_position_shape(position) == POSITION_KIND_SUBJECT_HOISTED

    def test_empty_position_raises(self):
        """A position with all three subject-carrying fields empty is invalid.

        The classifier should not silently accept an empty position — it
        should surface the upstream extraction issue rather than emit a
        meaningless row in the chain.
        """
        position = LobbyingPosition(
            bill_reference=None,
            general_issue_area=None,
            description=None,
        )
        with pytest.raises(ValueError, match="empty"):
            classify_position_shape(position)

    def test_whitespace_only_fields_treated_as_empty(self):
        """A position whose only populated field is whitespace is empty.

        Defensive: if mini emits an empty-after-strip string into description,
        treat it the same as None.
        """
        position = LobbyingPosition(
            bill_reference=None,
            general_issue_area=None,
            description="   \n\t ",
        )
        with pytest.raises(ValueError, match="empty"):
            classify_position_shape(position)


# ---------------------------------------------------------------------------
# extract_position_label — unified "what was lobbied" string
# ---------------------------------------------------------------------------


class TestExtractPositionLabel:
    """The unified label string used downstream by the bill-label classifier."""

    def test_bill_referenced_returns_original_text(self):
        position = LobbyingPosition(
            bill_reference=BillReference(original_text="HB 96"),
        )
        assert extract_position_label(position) == "HB 96"

    def test_bill_referenced_strips_whitespace(self):
        position = LobbyingPosition(
            bill_reference=BillReference(original_text="  HB 96  "),
        )
        assert extract_position_label(position) == "HB 96"

    def test_subject_general_returns_general_issue_area(self):
        position = LobbyingPosition(
            general_issue_area="MEDICAID / HOME CARE",
        )
        assert extract_position_label(position) == "MEDICAID / HOME CARE"

    def test_subject_hoisted_returns_description(self):
        position = LobbyingPosition(
            description="HEALTH CARE POLICY",
        )
        assert extract_position_label(position) == "HEALTH CARE POLICY"

    def test_empty_raises(self):
        position = LobbyingPosition()
        with pytest.raises(ValueError, match="empty"):
            extract_position_label(position)


# ---------------------------------------------------------------------------
# Step B — label-pattern classification (§6 OAC table + 2026-06-14 subject row)
# ---------------------------------------------------------------------------


class TestClassifyBillLabelBillPatterns:
    """All eight OH legislative prefixes resolve to bill_class='bill'."""

    @pytest.mark.parametrize(
        "label",
        [
            "HB 96",  # most-lobbied bill per smoke test (FY 26-27 budget)
            "SB 197",
            "HR 12",
            "SR 5",
            "HJR 1",
            "SJR 2",
            "HCR 3",
            "SCR 4",
            "HB 1",
            "HB 11019",  # OH Assembly upper bound for sanity
            "SB 88",
        ],
    )
    def test_bill_pattern_recognized(self, label):
        result = classify_bill_label(label, POSITION_KIND_BILL_REFERENCED)
        assert result == BILL_CLASS_BILL, f"{label!r} should classify as bill"

    def test_bill_pattern_case_insensitive(self):
        """OH AERs sometimes lowercase the prefix; classifier should still match."""
        assert (
            classify_bill_label("hb 96", POSITION_KIND_BILL_REFERENCED)
            == BILL_CLASS_BILL
        )

    def test_bill_pattern_tolerates_extra_internal_space(self):
        """Some filers write 'HB  96' with double space."""
        assert (
            classify_bill_label("HB  96", POSITION_KIND_BILL_REFERENCED)
            == BILL_CLASS_BILL
        )


class TestClassifyBillLabelJCARRPatterns:
    """JC <numbers-dashes> → jcarr; not joinable to OH_136_bills.csv."""

    @pytest.mark.parametrize(
        "label",
        [
            "JC 4731-24-03",
            "JC 4901:1-16-01 THROUGH 4901:1-16-06",  # range, from smoke-test top-10
            "JC 4759-4-01",
            "JC 4731-9-01",
        ],
    )
    def test_jcarr_pattern_recognized(self, label):
        result = classify_bill_label(label, POSITION_KIND_BILL_REFERENCED)
        assert result == BILL_CLASS_JCARR, f"{label!r} should classify as jcarr"


class TestClassifyBillLabelOACPatterns:
    """Bare \\d+-\\d+-\\d+ (no JC prefix) → oac_rule."""

    @pytest.mark.parametrize(
        "label",
        [
            "5160-32-02",
            "5123-4-03",
            "5123-1-03",
            "5160-46-01",
            "5160-46-12",
        ],
    )
    def test_oac_pattern_recognized(self, label):
        result = classify_bill_label(label, POSITION_KIND_BILL_REFERENCED)
        assert result == BILL_CLASS_OAC_RULE, f"{label!r} should classify as oac_rule"


class TestClassifyBillLabelSubjectClass:
    """When position_kind is not bill_referenced, the label is a subject (added 2026-06-14)."""

    @pytest.mark.parametrize(
        "label,kind",
        [
            ("HEALTH CARE", POSITION_KIND_SUBJECT_GENERAL),
            ("MEDICAID / HOME CARE / HOSPICE", POSITION_KIND_SUBJECT_GENERAL),
            ("Education Policy", POSITION_KIND_SUBJECT_HOISTED),
            ("Workers' Compensation Reform", POSITION_KIND_SUBJECT_HOISTED),
        ],
    )
    def test_subject_class_from_non_bill_kind(self, label, kind):
        """Subject content is classified as 'subject' regardless of textual form."""
        assert classify_bill_label(label, kind) == BILL_CLASS_SUBJECT

    def test_subject_class_overrides_bill_pattern_text(self):
        """Even if a subject string happens to contain bill-like text, kind wins.

        e.g., a general_issue_area of 'HB 96 BUDGET ADVOCACY' is still subject-
        only — the position carries no bill_reference, so it doesn't get the
        sponsor cross-product. The bill_id join must remain null.
        """
        result = classify_bill_label("HB 96 BUDGET ADVOCACY", POSITION_KIND_SUBJECT_GENERAL)
        assert result == BILL_CLASS_SUBJECT


class TestClassifyBillLabelUnmatched:
    """Things that don't match any known pattern AND are bill_referenced → unmatched.

    This catches malformed bill_references (e.g., free-text descriptions that
    leaked into bill_reference.original_text) which should be flagged in the
    chain rather than silently joined as bills.
    """

    @pytest.mark.parametrize(
        "label",
        [
            "Various legislation",
            "See attached",
            "TBD",
            "",  # empty — pathological but possible
        ],
    )
    def test_unmatched_pattern(self, label):
        result = classify_bill_label(label, POSITION_KIND_BILL_REFERENCED)
        assert result == BILL_CLASS_UNMATCHED, (
            f"{label!r} should classify as unmatched"
        )


class TestClassifyBillLabelEdgeCases:
    """Pathological inputs that have caused silent misclassification in the past."""

    def test_leading_trailing_whitespace_stripped(self):
        assert (
            classify_bill_label("  HB 96  ", POSITION_KIND_BILL_REFERENCED)
            == BILL_CLASS_BILL
        )

    def test_oac_pattern_does_not_match_when_jc_prefix_present(self):
        """JC 4731-24-03 must be jcarr, not oac_rule (precedence test)."""
        assert (
            classify_bill_label("JC 4731-24-03", POSITION_KIND_BILL_REFERENCED)
            == BILL_CLASS_JCARR
        )

    def test_bill_pattern_does_not_match_two_letter_non_bill(self):
        """'AB 96' (Wisconsin-style) shouldn't classify as an OH bill."""
        # AB doesn't exist in OH's bill prefix set.
        assert (
            classify_bill_label("AB 96", POSITION_KIND_BILL_REFERENCED)
            == BILL_CLASS_UNMATCHED
        )

    def test_partial_match_does_not_qualify(self):
        """'HB' alone without a number is unmatched."""
        assert (
            classify_bill_label("HB", POSITION_KIND_BILL_REFERENCED)
            == BILL_CLASS_UNMATCHED
        )

    def test_oac_pattern_requires_at_least_two_dashes(self):
        """'5160-32' (only one dash) is not a complete OAC citation."""
        assert (
            classify_bill_label("5160-32", POSITION_KIND_BILL_REFERENCED)
            == BILL_CLASS_UNMATCHED
        )
