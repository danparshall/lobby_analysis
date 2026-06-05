"""Behavior tests for the NY Phase 2 grain-collapse step (``io/ny/grain``).

NY's Socrata datasets are denormalized ~1,300x: one filing emits hundreds-to-
thousands of rows (the cartesian of bills x subjects x parties-lobbied x ...),
with the filing-level ``current_period_compensation`` replicated on every row.
On top of that, an amendment is filed as a SEPARATE submission (a new
``form_submission_id``) that supersedes the prior submission for the same
business key — and re-amendment is common (1 Original + several Amendments).

The grain-collapse step is the load-bearing dollar-conservation guard. It must:
  1. drop superseded submissions (keep only the latest ``form_submission_id``
     per business key) BEFORE collapsing, so superseded dollars never count;
  2. collapse the row explosion to one row per (filing, bill), so replicated
     compensation is never summed across the explosion.

These facts were verified against live ``client_semiannual`` (2025):
  - no ``form_submission_id`` carries both Original and Amendment rows, so
    "keep latest filing_type per form_submission_id" is a no-op;
  - amendment ids are strictly greater than their superseded original's id
    (monotonic with submission order), so ``max(form_submission_id)`` per
    business key is the latest version.

Tests assert on conserved dollars and surviving grain rows — real behavior —
not on internal calls or data-structure shapes.
"""

from __future__ import annotations

from decimal import Decimal

import pandas as pd

from lobby_analysis.io.ny.grain import collapse_to_filing_grain


def _exploded_rows(
    *,
    form_submission_id: str,
    filing_type: str,
    comp,
    bills: list[str | None],
    principal_lobbyist: str = "THE PARKSIDE GROUP LLC",
    beneficial_client: str = "GRAHAM WINDHAM;",
    contractual_client_name: str = "GRAHAM WINDHAM",
    reporting_year: str = "2025",
    reporting_period: str = "July/Dec",
    subjects: tuple[str, ...] = ("Health", "Budget"),
) -> list[dict]:
    """Build the denormalized rows a single submission would emit.

    Each (bill x subject) pair is one raw row; the filing-level ``comp`` is
    replicated on every one — exactly the ~1,300x explosion the collapse must
    de-duplicate without summing.
    """
    rows = []
    for bill in bills:
        for subject in subjects:
            rows.append(
                {
                    "reporting_year": reporting_year,
                    "reporting_period": reporting_period,
                    "form_submission_id": form_submission_id,
                    "filing_type": filing_type,
                    "principal_lobbyist": principal_lobbyist,
                    "beneficial_client": beneficial_client,
                    "contractual_client_name": contractual_client_name,
                    "bill_id": bill,
                    "lobbying_subject": subject,  # explosion axis, dropped by collapse
                    "filing_compensation": comp,
                }
            )
    return rows


def test_collapse_dedups_row_explosion_to_one_row_per_bill():
    """A single filing that names 2 bills across 2 subjects emits 4 raw rows;
    the collapse must yield exactly one grain row per distinct bill (2), not 4,
    and must not multiply the filing's compensation by the explosion factor."""
    rows = _exploded_rows(
        form_submission_id="793896",
        filing_type="Amendment",
        comp=Decimal("24000"),
        bills=["S550-A", "A100"],
    )
    df = pd.DataFrame(rows)

    out = collapse_to_filing_grain(df)

    assert len(out) == 2
    assert set(out["bill_id"]) == {"S550-A", "A100"}
    # comp is filing-level (replicated), so each surviving bill row still carries
    # the full filing total — and the filing total summed once is 24000, not 4x.
    distinct_comp = out.drop_duplicates("form_submission_id")["filing_compensation"].sum()
    assert distinct_comp == Decimal("24000")


def test_superseded_submission_rows_are_dropped():
    """An Original and an Amendment for the SAME business key are two distinct
    submissions. Only the latest (max form_submission_id) survives the collapse;
    the superseded Original's rows are gone entirely."""
    df = pd.DataFrame(
        _exploded_rows(
            form_submission_id="775553", filing_type="Original",
            comp=Decimal("20000"), bills=["S550-A"],
        )
        + _exploded_rows(
            form_submission_id="793896", filing_type="Amendment",
            comp=Decimal("24000"), bills=["S550-A"],
        )
    )

    out = collapse_to_filing_grain(df)

    assert set(out["form_submission_id"]) == {"793896"}
    assert "775553" not in set(out["form_submission_id"])


def test_filing_comp_conservation_no_amendment_double_count():
    """THE guard. Original $20k superseded by Amendment $24k (same business key)
    must conserve to $24k when summed over distinct filings — never $44k. This
    is the failure mode the plan's per-form_submission_id dedup did not catch."""
    df = pd.DataFrame(
        _exploded_rows(
            form_submission_id="775553", filing_type="Original",
            comp=Decimal("20000"), bills=["S550-A", "A100"],
        )
        + _exploded_rows(
            form_submission_id="793896", filing_type="Amendment",
            comp=Decimal("24000"), bills=["S550-A", "A100"],
        )
    )

    out = collapse_to_filing_grain(df)

    total = out.drop_duplicates("form_submission_id")["filing_compensation"].sum()
    assert total == Decimal("24000")


def test_re_amendment_keeps_only_the_latest_submission():
    """Re-amendment is common (1 Original + several Amendments). The collapse
    must keep only the max form_submission_id — verified to be the latest
    version — not merely 'an Amendment'."""
    df = pd.DataFrame(
        _exploded_rows(
            form_submission_id="729762", filing_type="Original",
            comp=Decimal("265002"), bills=["S550-A"],
        )
        + _exploded_rows(
            form_submission_id="752918", filing_type="Amendment",
            comp=Decimal("265002"), bills=["S550-A"],
        )
        + _exploded_rows(
            form_submission_id="782077", filing_type="Amendment",
            comp=Decimal("255536"), bills=["S550-A"],
        )
    )

    out = collapse_to_filing_grain(df)

    assert set(out["form_submission_id"]) == {"782077"}
    total = out.drop_duplicates("form_submission_id")["filing_compensation"].sum()
    assert total == Decimal("255536")


def test_null_business_key_column_does_not_drop_the_filing():
    """A null in a business-key column (e.g. contractual_client_name, which is
    absent for parts of the data) must NOT cause the filing's rows to be
    silently dropped — that would lose the filing's dollars entirely, the exact
    non-conservation this guard exists to prevent."""
    rows = _exploded_rows(
        form_submission_id="500",
        filing_type="Original",
        comp=Decimal("18000"),
        bills=["S42"],
        contractual_client_name=None,
    )
    df = pd.DataFrame(rows)

    out = collapse_to_filing_grain(df)

    assert set(out["form_submission_id"]) == {"500"}
    total = out.drop_duplicates("form_submission_id")["filing_compensation"].sum()
    assert total == Decimal("18000")


def test_empty_frame_returns_empty_grain():
    """If an upstream filter removed every row, the collapse must return an
    empty frame (with grain columns), not raise — a valid 'nothing here' result."""
    df = pd.DataFrame(
        _exploded_rows(
            form_submission_id="1", filing_type="Original",
            comp=Decimal("1"), bills=["S1"],
        )
    ).iloc[0:0]

    out = collapse_to_filing_grain(df)

    assert len(out) == 0
    assert "filing_compensation" in out.columns


def test_distinct_business_keys_are_not_merged():
    """Supersede resolution must be scoped to a business key. Two different
    lobbyist->client filings, even with overlapping submission-id ranges, must
    both survive — one is not allowed to supersede the other."""
    df = pd.DataFrame(
        _exploded_rows(
            form_submission_id="100", filing_type="Original",
            comp=Decimal("10000"), bills=["S1"],
            principal_lobbyist="FIRM A", beneficial_client="CLIENT A;",
            contractual_client_name="CLIENT A",
        )
        + _exploded_rows(
            form_submission_id="200", filing_type="Original",
            comp=Decimal("30000"), bills=["S2"],
            principal_lobbyist="FIRM B", beneficial_client="CLIENT B;",
            contractual_client_name="CLIENT B",
        )
    )

    out = collapse_to_filing_grain(df)

    assert set(out["form_submission_id"]) == {"100", "200"}
    total = out.drop_duplicates("form_submission_id")["filing_compensation"].sum()
    assert total == Decimal("40000")


def test_n_bills_in_filing_counts_distinct_bills():
    """Each grain row carries the count of distinct bills in its filing — the
    denominator a downstream even-split needs. A filing on 3 bills tags every
    one of its rows with n_bills_in_filing == 3."""
    df = pd.DataFrame(
        _exploded_rows(
            form_submission_id="793896", filing_type="Amendment",
            comp=Decimal("24000"), bills=["S550-A", "A100", "S999"],
        )
    )

    out = collapse_to_filing_grain(df)

    assert len(out) == 3
    assert set(out["n_bills_in_filing"]) == {3}


def test_non_bill_focus_rows_are_preserved_not_dropped():
    """A filing whose focus is subject/funding free text (no real bill number)
    carries a null bill_id. Those rows must be emitted (one collapsed row), not
    silently dropped, and must not inflate n_bills_in_filing."""
    df = pd.DataFrame(
        _exploded_rows(
            form_submission_id="793896", filing_type="Amendment",
            comp=Decimal("24000"), bills=["S550-A", None],
        )
    )

    out = collapse_to_filing_grain(df)

    # one row for the real bill, one for the null-bill bucket
    assert len(out) == 2
    assert out["bill_id"].isna().sum() == 1
    # only the real bill counts toward the split denominator
    assert set(out["n_bills_in_filing"]) == {1}
