"""Behavior tests for the NY per-dataset column map (``io/ny/columns``).

Phase 0 found the 6 NY datasets use *inconsistent names for the same concept*
(``type_of_lobbying_focus`` vs ``lobbying_focus_type``; ``beneficial_client``
vs ``beneficial_client_name``; ``current_period_compensation`` vs
``compensation``; ``principal_lobbyist`` vs ``principal_lobbyist_name``; etc).
The column map normalizes each dataset's raw columns to ONE canonical schema so
the grain-collapse and parser steps don't have to special-case per dataset.

This increment covers the two datasets the 2025 build uses: ``client_semiannual``
(the chain spine) and ``lobbyist_bimonthly`` (itemized expenses + individual
people). Tests are driven by the real Phase-0 sample rows committed under
``tests/fixtures/ny/`` and assert the canonicalized columns carry the original
values — not that any particular rename call was made.
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from lobby_analysis.io.ny.columns import normalize_columns
from lobby_analysis.io.ny.grain import BUSINESS_KEY

FIXTURE = Path(__file__).parent / "fixtures" / "ny" / "sample_schema_core2_datasets.json"


def _examples(dataset: str) -> list[dict]:
    data = json.loads(FIXTURE.read_text())
    return data[dataset]["examples"]


# Canonical columns the chain spine must expose after normalization (the
# business key + the filing-level money + the bill-focus discriminator/id).
_SPINE_CANONICAL = set(BUSINESS_KEY) | {
    "form_submission_id",
    "filing_type",
    "filing_compensation",
    "focus_type",
    "focus_identifying_number",
}


def test_client_semiannual_maps_money_and_focus_to_canonical():
    """``current_period_compensation`` -> ``filing_compensation`` and
    ``type_of_lobbying_focus`` -> ``focus_type``, carrying the values intact."""
    df = pd.DataFrame(_examples("client_semiannual"))
    raw_comp = df["current_period_compensation"].tolist()
    raw_focus = df.get("type_of_lobbying_focus")

    out = normalize_columns(df, "client_semiannual")

    assert "filing_compensation" in out.columns
    assert "current_period_compensation" not in out.columns
    assert out["filing_compensation"].tolist() == raw_comp
    if raw_focus is not None:
        assert out["focus_type"].tolist() == raw_focus.tolist()


def test_lobbyist_bimonthly_renames_diverging_names_to_canonical():
    """The bimonthly dataset uses ``*_name`` and ``compensation`` /
    ``lobbying_focus_type`` / ``individual_lobbyist_name`` — all must land on the
    canonical names with values preserved."""
    df = pd.DataFrame(_examples("lobbyist_bimonthly"))
    raw_principal = df["principal_lobbyist_name"].tolist()
    raw_client = df["beneficial_client_name"].tolist()
    raw_comp = df["compensation"].tolist()

    out = normalize_columns(df, "lobbyist_bimonthly")

    assert out["principal_lobbyist"].tolist() == raw_principal
    assert out["beneficial_client"].tolist() == raw_client
    assert out["filing_compensation"].tolist() == raw_comp
    assert "focus_type" in out.columns
    assert "individual_lobbyists" in out.columns
    # raw names are gone after canonicalization
    for raw in ("principal_lobbyist_name", "beneficial_client_name", "compensation"):
        assert raw not in out.columns


def test_both_core_datasets_expose_the_same_canonical_spine():
    """The point of the column map: two datasets that disagree on raw names end
    up with the SAME canonical columns, so downstream code is dataset-agnostic."""
    cs = normalize_columns(pd.DataFrame(_examples("client_semiannual")), "client_semiannual")
    lb = normalize_columns(pd.DataFrame(_examples("lobbyist_bimonthly")), "lobbyist_bimonthly")

    assert _SPINE_CANONICAL.issubset(cs.columns)
    assert _SPINE_CANONICAL.issubset(lb.columns)


def test_unknown_dataset_is_rejected_not_passed_through():
    """An unrecognized dataset name must raise — silently returning the frame
    unchanged would let un-normalized raw columns flow downstream undetected."""
    df = pd.DataFrame(_examples("client_semiannual"))

    try:
        normalize_columns(df, "not_a_real_dataset")
    except KeyError:
        return
    raise AssertionError("expected KeyError for unknown dataset")
