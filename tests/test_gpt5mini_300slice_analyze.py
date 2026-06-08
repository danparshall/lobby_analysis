"""Regression test for the gpt-5-mini-on-300-slice analysis script's array alignment.

The risk this guards against: keying arrays by a field that is *being measured*
for agreement (e.g., expenditures keyed on amount) splits "same logical row
with disagreeing value" into two rows — one per provider — and inflates
disagreement counts by ~5x. See concern #2 in the pre-dispatch review and
the comment block on `_ARRAY_ALIGNMENT_KEYS` in the analyze script.

The synthetic case below is the minimum reproduction of that failure mode:
one expenditure with Sonnet=$100 and mini=$105. With correct keys (category
+ recipient + date, no amount) it surfaces as exactly one stable
disagreement on the `amount` field. With buggy keys including amount, it
surfaces as ~10 disagreements (every field of both phantom rows).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_REPO_ROOT))
sys.path.insert(0, str(_REPO_ROOT / "src"))

from scripts.gpt5mini_oh_300slice_analyze import (  # noqa: E402
    aggregate_metrics,
    assemble_extraction_set,
)


def _filing(amount: float, recipient: str, bill: str) -> dict:
    return {
        "id": f"oh-test",
        "state": "OH",
        "filing_type": "activity_report",
        "filer_role": "lobbyist",
        "filer_person": {"id": "p", "name": "Test", "source_state": "OH"},
        "employer": {"id": "e", "name": "TestCo", "source_state": "OH"},
        "positions": [{
            "description": "Lobbied on the bill",
            "bill_reference": {"original_text": bill, "is_resolved": False},
            "position": None,
        }],
        "expenditures": [{
            "category": "gift",
            "amount": amount,
            "recipient_name": recipient,
            "expenditure_date": "2025-06-01",
            "currency": "USD",
        }],
        "engagements": [],
        "gifts": [],
    }


def _write_tree(data_dir: Path, fixtures: list[tuple[str, str, dict]]) -> None:
    """fixtures: list of (report_id, run_dir_name, filing)."""
    for report_id, run_name, filing in fixtures:
        is_mini = run_name.startswith("mini_run_")
        d = (
            data_dir / "extracted_openai" / report_id / run_name if is_mini
            else data_dir / "extracted" / report_id / run_name
        )
        d.mkdir(parents=True, exist_ok=True)
        (d / "filing.json").write_text(json.dumps(filing))
        (d / "extraction_run.json").write_text(json.dumps({
            "usage": {"prompt_tokens": 6000, "completion_tokens": 1100},
            "duration_seconds": 5.0,
        }))


def test_amount_disagreement_on_same_row_surfaces_as_one_disagreement(
    tmp_path: Path,
) -> None:
    """Sonnet=$100, mini=$105 (3x) on same recipient+category+date.

    Correct behavior: 1 stable-disagreement on the `amount` field.
    Buggy behavior (amount in key): ~10 stable-disagreements (full-row
    splitting + every field of both phantom rows).
    """
    data = tmp_path / "oh_portal"
    fixtures = [
        ("R1", "sonnet_aaa", _filing(100.0, "Bob", "SB 2")),
        ("R1", "mini_run_1_b1", _filing(105.0, "Bob", "SB 2")),
        ("R1", "mini_run_2_b2", _filing(105.0, "Bob", "SB 2")),
        ("R1", "mini_run_3_b3", _filing(105.0, "Bob", "SB 2")),
    ]
    _write_tree(data, fixtures)
    sonnet, mini = assemble_extraction_set(data)
    metrics = aggregate_metrics(sonnet, mini)
    disagreements = metrics["stable_disagreements"]
    # Exactly one disagreement on the amount field of the expenditure row.
    amount_disagreements = [
        d for d in disagreements
        if d["field_path"].endswith(".amount")
    ]
    assert len(amount_disagreements) == 1, (
        f"Expected exactly 1 stable disagreement on .amount; got "
        f"{len(amount_disagreements)} (likely the alignment key included "
        f"amount, splitting the row). All disagreements: {disagreements}"
    )
    sd = amount_disagreements[0]
    assert sd["sonnet_value"] == 100.0
    assert sd["mini_values"] == [105.0, 105.0, 105.0]


def test_mini_internally_noisy_does_not_count_as_stable_disagreement(
    tmp_path: Path,
) -> None:
    """If mini runs disagree among themselves, that lowers sigma_noise but is
    NOT stable disagreement (which requires mini consistency).
    """
    data = tmp_path / "oh_portal"
    fixtures = [
        ("R1", "sonnet_aaa", _filing(75.0, "Carol", "HR 3")),
        ("R1", "mini_run_1_c1", _filing(75.0, "Carol", "HR 3")),
        ("R1", "mini_run_2_c2", _filing(75.5, "Carol", "HR 3")),  # noisy
        ("R1", "mini_run_3_c3", _filing(76.0, "Carol", "HR 3")),  # noisy
    ]
    _write_tree(data, fixtures)
    sonnet, mini = assemble_extraction_set(data)
    metrics = aggregate_metrics(sonnet, mini)
    amount_disagreements = [
        d for d in metrics["stable_disagreements"]
        if d["field_path"].endswith(".amount")
    ]
    assert amount_disagreements == [], (
        "mini-internally-noisy row should not show as stable disagreement"
    )
    # Sigma noise should reflect the inconsistency on that one field.
    assert metrics["headline"]["mini_sigma_noise"] < 1.0


def test_full_agreement_has_zero_stable_disagreement(tmp_path: Path) -> None:
    """All 4 filings agree → sigma_noise = 1.0, stable_disagreement = 0."""
    data = tmp_path / "oh_portal"
    fixtures = [
        ("R1", "sonnet_aaa", _filing(50.0, "Alice", "HB 1")),
        ("R1", "mini_run_1_a1", _filing(50.0, "Alice", "HB 1")),
        ("R1", "mini_run_2_a2", _filing(50.0, "Alice", "HB 1")),
        ("R1", "mini_run_3_a3", _filing(50.0, "Alice", "HB 1")),
    ]
    _write_tree(data, fixtures)
    sonnet, mini = assemble_extraction_set(data)
    metrics = aggregate_metrics(sonnet, mini)
    assert metrics["headline"]["mini_sigma_noise"] == 1.0
    assert metrics["headline"]["stable_disagreement_rate"] == 0.0
    assert metrics["headline"]["mini_run_1_vs_sonnet_agreement"] == 1.0


def test_missing_row_in_one_provider_counts_as_full_row_disagreement(
    tmp_path: Path,
) -> None:
    """If Sonnet emits 2 expenditures and mini emits 1, the missing row's
    fields all count toward disagreement (per plan's "array-length differences
    count as full-row disagreement")."""
    base = _filing(50.0, "Alice", "HB 1")
    base_extra_row = dict(base)
    base_extra_row["expenditures"] = base["expenditures"] + [{
        "category": "travel",
        "amount": 200.0,
        "recipient_name": "Dave",
        "expenditure_date": "2025-06-15",
        "currency": "USD",
    }]
    data = tmp_path / "oh_portal"
    fixtures = [
        ("R1", "sonnet_aaa", base_extra_row),  # 2 rows
        ("R1", "mini_run_1_a1", base),          # 1 row
        ("R1", "mini_run_2_a2", base),
        ("R1", "mini_run_3_a3", base),
    ]
    _write_tree(data, fixtures)
    sonnet, mini = assemble_extraction_set(data)
    metrics = aggregate_metrics(sonnet, mini)
    # The "Dave" row exists in sonnet but not in mini -> every field of that
    # row should appear as stable disagreement (mini values all null,
    # consistent with each other).
    travel_disagreements = [
        d for d in metrics["stable_disagreements"]
        if "travel" in d["field_path"]
    ]
    assert len(travel_disagreements) >= 3, (
        f"Expected at least 3 stable disagreements on the missing travel row "
        f"(amount, recipient_name, expenditure_date); got "
        f"{len(travel_disagreements)}: {travel_disagreements}"
    )
