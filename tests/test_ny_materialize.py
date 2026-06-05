"""Behavior tests for the NY Phase 2 materialize step (``io/ny/materialize``).

``materialize_ny`` is the end of the Phase 2 pipeline: it takes a
column-normalized, ``bill_id``-derived, grain-collapsed frame (the output of
``normalize_columns -> add_bill_id_column -> collapse_to_filing_grain``) and
writes the ``releases/ny/`` TSVs, returning a row-count dict. It mirrors WI's
``materialize_tier_2`` conventions: ``csv.DictWriter`` with ``\\t`` delimiter and
``\\n`` lineterminator (byte-identical re-runs), ``None`` -> empty cell, JSON
columns serialized compactly, deterministic sort, entities de-duplicated by id.

The 2025 build draws from ``client_semiannual`` (the chain spine), so the four
emitted files are:

  * ``NY_clients.tsv``           — one row per distinct beneficial client (Organization)
  * ``NY_lobbyists.tsv``         — one row per distinct principal-lobbyist firm (Organization)
  * ``NY_filings.tsv``           — one row per distinct (submission, client) filing,
                                   carrying the de-duplicated filing-level compensation
  * ``NY_filing_bill_links.tsv`` — one row per (filing, real bill) with the even-split
                                   ``comp_per_bill`` + ``filing_compensation`` +
                                   ``n_bills_in_filing`` + ``bill_print_version``

Tests assert real behavior: written files exist, round-trip preserves values,
the dollar-conservation invariants hold (filing-comp summed over distinct
filings == source total; even-split summed over a filing's bills ==
filing_compensation), entities are de-duplicated, and reruns are byte-identical.
"""

from __future__ import annotations

import csv
from decimal import Decimal

import pandas as pd
import pytest

from lobby_analysis.io.ny.columns import normalize_columns
from lobby_analysis.io.ny.grain import collapse_to_filing_grain
from lobby_analysis.io.ny.materialize import materialize_ny
from lobby_analysis.io.ny.parse import add_bill_id_column


def _read_tsv(path) -> list[dict]:
    with open(path, encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def _exploded_rows(
    *,
    form_submission_id: str,
    filing_type: str,
    comp,
    bills: list[str | None],
    focus_types: list[str] | None = None,
    principal_lobbyist: str = "THE PARKSIDE GROUP LLC",
    beneficial_client: str = "GRAHAM WINDHAM;",
    contractual_client_name: str = "GRAHAM WINDHAM",
    reporting_year: str = "2025",
    reporting_period: str = "July/Dec",
    subjects: tuple[str, ...] = ("Health", "Budget"),
) -> list[dict]:
    """Build the denormalized raw rows one ``client_semiannual`` submission
    emits: the cartesian of (bill x subject), filing-level comp replicated on
    each. ``bills`` entries that are real bill ids get ``focus_type='State
    Bill'``; ``None`` entries get a non-bill focus so ``derive_bill_id``
    yields ``None`` (mirroring real ``State Funding`` / ``Discretionary
    Funding`` rows)."""
    if focus_types is None:
        focus_types = ["State Bill" if b else "State Funding" for b in bills]
    rows = []
    for bill, ftype in zip(bills, focus_types):
        focus_number = bill if bill else "Discretionary Funding"
        for subject in subjects:
            rows.append(
                {
                    "reporting_year": reporting_year,
                    "reporting_period": reporting_period,
                    "form_submission_id": form_submission_id,
                    "filing_type": filing_type,
                    "principal_lobbyist": principal_lobbyist,
                    "contractual_client_name": contractual_client_name,
                    "beneficial_client": beneficial_client,
                    "current_period_compensation": comp,
                    "type_of_lobbying_focus": ftype,
                    "focus_identifying_number": focus_number,
                    "lobbying_subjects": subject,
                }
            )
    return rows


def _grain_from_raw(rows: list[dict]) -> pd.DataFrame:
    """Run the real Phase-2 pipeline a raw client_semiannual frame goes through
    before materialize: column-normalize -> derive bill_id -> collapse."""
    df = pd.DataFrame(rows)
    df = normalize_columns(df, "client_semiannual")
    df = add_bill_id_column(df)
    return collapse_to_filing_grain(df)


@pytest.fixture()
def two_filing_grain() -> pd.DataFrame:
    """Two distinct filings: Parkside/Graham Windham ($24k, 2 real bills + 1
    non-bill row) and Akerman/1417-Avenue-U ($17,160, no bills)."""
    rows = _exploded_rows(
        form_submission_id="793896",
        filing_type="Amendment",
        comp="24000",
        bills=["S550-A", "A100", None],
    ) + _exploded_rows(
        form_submission_id="793902",
        filing_type="Amendment",
        comp="17160",
        bills=[None],
        principal_lobbyist="AKERMAN LLP",
        beneficial_client="1417 Avenue U Holding LLC;",
        contractual_client_name="1417 Avenue U Holding LLC",
        reporting_period="Jan/June",
    )
    return _grain_from_raw(rows)


def test_materialize_writes_four_tsvs(tmp_path, two_filing_grain):
    counts = materialize_ny(two_filing_grain, output_dir=tmp_path)

    for name in (
        "NY_clients.tsv",
        "NY_lobbyists.tsv",
        "NY_filings.tsv",
        "NY_filing_bill_links.tsv",
    ):
        assert (tmp_path / name).exists(), f"{name} not written"
    # returned counts match the files on disk
    assert counts["clients"] == len(_read_tsv(tmp_path / "NY_clients.tsv"))
    assert counts["lobbyists"] == len(_read_tsv(tmp_path / "NY_lobbyists.tsv"))
    assert counts["filings"] == len(_read_tsv(tmp_path / "NY_filings.tsv"))
    assert counts["filing_bill_links"] == len(
        _read_tsv(tmp_path / "NY_filing_bill_links.tsv")
    )


def test_entities_are_deduplicated_by_id(tmp_path, two_filing_grain):
    """Two distinct firms and two distinct clients across the grain -> exactly
    two rows each, no duplicates even though the grain has many rows per
    entity."""
    materialize_ny(two_filing_grain, output_dir=tmp_path)

    lobbyists = _read_tsv(tmp_path / "NY_lobbyists.tsv")
    clients = _read_tsv(tmp_path / "NY_clients.tsv")

    assert {row["name"] for row in lobbyists} == {
        "THE PARKSIDE GROUP LLC",
        "AKERMAN LLP",
    }
    assert len(lobbyists) == 2  # no dupes
    assert {row["name"] for row in clients} == {
        "GRAHAM WINDHAM",
        "1417 Avenue U Holding LLC",
    }
    assert len(clients) == 2


def test_one_filing_row_per_submission_client(tmp_path, two_filing_grain):
    """The filings TSV is at filing grain: one row per (submission, client),
    not one row per bill. The 3-bill-row Parkside filing collapses to ONE
    filing row carrying $24,000 once."""
    materialize_ny(two_filing_grain, output_dir=tmp_path)

    filings = _read_tsv(tmp_path / "NY_filings.tsv")
    assert len(filings) == 2

    parkside = [f for f in filings if f["filing_id"] == "793896"]
    assert len(parkside) == 1
    assert parkside[0]["total_compensation"] == "24000"
    assert parkside[0]["filer_role"] == "firm"
    assert parkside[0]["state"] == "NY"


def test_filing_comp_conservation_summed_over_distinct_filings(
    tmp_path, two_filing_grain
):
    """Summing total_compensation over the distinct filing rows equals the
    source total ($24,000 + $17,160 = $41,160) — proves materialize did not
    re-introduce the row-explosion overcount."""
    materialize_ny(two_filing_grain, output_dir=tmp_path)

    filings = _read_tsv(tmp_path / "NY_filings.tsv")
    total = sum(Decimal(f["total_compensation"]) for f in filings)
    assert total == Decimal("41160")


def test_bill_links_even_split_conservation(tmp_path, two_filing_grain):
    """comp_per_bill is the even split filing_compensation / n_bills_in_filing.
    Summing comp_per_bill over a filing's bill links equals that filing's
    compensation exactly — no dollars lost or fabricated. Parkside: 2 real
    bills, $24,000 / 2 = $12,000 each, summing to $24,000."""
    materialize_ny(two_filing_grain, output_dir=tmp_path)

    links = _read_tsv(tmp_path / "NY_filing_bill_links.tsv")
    parkside = [link for link in links if link["filing_id"] == "793896"]
    # 2 real bills only (the None-bill row is not a bill link)
    assert len(parkside) == 2
    assert {link["bill_id"] for link in parkside} == {"S550-A", "A100"}
    per_bill = sorted(Decimal(link["comp_per_bill"]) for link in parkside)
    assert per_bill == [Decimal("12000"), Decimal("12000")]
    assert sum(per_bill) == Decimal("24000")


def test_bill_links_preserve_print_version(tmp_path, two_filing_grain):
    """The amendment-print suffix is preserved as bill_print_version (the raw
    canonical bill_id), so the Phase-4 chain normalizer can strip it for the
    Open States join while the original stays auditable."""
    materialize_ny(two_filing_grain, output_dir=tmp_path)

    links = _read_tsv(tmp_path / "NY_filing_bill_links.tsv")
    s550 = [link for link in links if link["bill_id"] == "S550-A"]
    assert len(s550) == 1
    assert s550[0]["bill_print_version"] == "S550-A"
    assert s550[0]["n_bills_in_filing"] == "2"


def test_filing_with_no_bills_emits_no_bill_links(tmp_path, two_filing_grain):
    """The Akerman filing has only a non-bill focus row (n_bills_in_filing=0).
    It still appears in NY_filings.tsv (the dollars are real) but contributes
    ZERO rows to the bill-links TSV — a filing with no bills cannot be in the
    chain, but its money is not lost from the filings table."""
    materialize_ny(two_filing_grain, output_dir=tmp_path)

    filings = _read_tsv(tmp_path / "NY_filings.tsv")
    links = _read_tsv(tmp_path / "NY_filing_bill_links.tsv")

    assert any(f["filing_id"] == "793902" for f in filings)
    assert all(link["filing_id"] != "793902" for link in links)


@pytest.fixture()
def shared_submission_grain() -> pd.DataFrame:
    """The real NY shape the live 2025 pull exposed: ONE client semi-annual
    report (one ``form_submission_id``) covers MULTIPLE retained firms, each with
    its own compensation and its own bills. ``form_submission_id`` is the
    *client's* report id, NOT a per-firm filing key.

    Submission 800 = ACCENTURE's report, listing two firms: Brown & Weinraub
    ($45,000, lobbying on S550-A and A100) and Accenture in-house ($179, S550-A
    only). They share the same ``beneficial_client`` ("ACCENTURE, LLP;") — the
    only thing distinguishing the two filings is ``principal_lobbyist``."""
    rows = _exploded_rows(
        form_submission_id="800",
        filing_type="Original",
        comp="45000",
        bills=["S550-A", "A100"],
        principal_lobbyist="BROWN & WEINRAUB ADVISORS, LLC",
        beneficial_client="ACCENTURE, LLP;",
        contractual_client_name="ACCENTURE, LLP",
    ) + _exploded_rows(
        form_submission_id="800",
        filing_type="Original",
        comp="179",
        bills=["S550-A"],
        principal_lobbyist="ACCENTURE, LLP",
        beneficial_client="ACCENTURE, LLP;",
        contractual_client_name="ACCENTURE, LLP",
    )
    return _grain_from_raw(rows)


def test_shared_submission_id_does_not_collapse_distinct_firm_filings(
    tmp_path, shared_submission_grain
):
    """Two firms sharing one client's ``form_submission_id`` must produce TWO
    filing rows, each carrying its own compensation — not one row that silently
    drops the other firm's dollars. This is the dollar-loss bug the live 2025
    pull exposed: a filing-dict keyed by (submission, client) without the firm
    collides every co-retained firm onto one row."""
    materialize_ny(shared_submission_grain, output_dir=tmp_path)

    filings = _read_tsv(tmp_path / "NY_filings.tsv")
    sub800 = [f for f in filings if f["filing_id"] == "800"]
    assert len(sub800) == 2, "both firms' filings must survive a shared submission id"

    by_firm = {f["lobbyist_id"]: f for f in sub800}
    assert by_firm["NY-lobbyist-brown-weinraub-advisors-llc"]["total_compensation"] == "45000"
    assert by_firm["NY-lobbyist-accenture-llp"]["total_compensation"] == "179"
    # the two filing rows have distinct ids (the firm disambiguates them)
    assert sub800[0]["id"] != sub800[1]["id"]


def test_shared_submission_comp_conservation(tmp_path, shared_submission_grain):
    """Summing comp over the distinct filings of one shared submission equals the
    sum of every co-retained firm's compensation ($45,000 + $179), not just the
    survivor's."""
    materialize_ny(shared_submission_grain, output_dir=tmp_path)

    filings = _read_tsv(tmp_path / "NY_filings.tsv")
    total = sum(
        Decimal(f["total_compensation"])
        for f in filings
        if f["total_compensation"] not in ("", None)
    )
    assert total == Decimal("45179")


def test_shared_submission_n_bills_is_per_firm_not_per_submission(
    tmp_path, shared_submission_grain
):
    """``n_bills_in_filing`` must count each firm's OWN bills, not the union of
    all firms' bills under the shared submission. Accenture lobbied 1 bill
    (S550-A); Brown & Weinraub lobbied 2 (S550-A, A100). A submission-keyed
    count would wrongly give Accenture 2 and split its $179 across two bills."""
    materialize_ny(shared_submission_grain, output_dir=tmp_path)

    links = _read_tsv(tmp_path / "NY_filing_bill_links.tsv")
    accenture = [
        link for link in links if link["lobbyist_id"] == "NY-lobbyist-accenture-llp"
    ]
    assert len(accenture) == 1
    assert accenture[0]["n_bills_in_filing"] == "1"
    assert accenture[0]["comp_per_bill"] == "179"

    bw = [
        link
        for link in links
        if link["lobbyist_id"] == "NY-lobbyist-brown-weinraub-advisors-llc"
    ]
    assert len(bw) == 2
    assert {link["n_bills_in_filing"] for link in bw} == {"2"}
    assert sum(Decimal(link["comp_per_bill"]) for link in bw) == Decimal("45000")


def test_absent_compensation_is_empty_cell_not_zero(tmp_path):
    """A filing whose compensation coerces to absent ('$') writes an empty
    total_compensation cell, never '0' — a missing comp is not a reported $0.
    comp_per_bill is likewise empty (cannot split an absent total)."""
    grain = _grain_from_raw(
        _exploded_rows(
            form_submission_id="500",
            filing_type="Original",
            comp="$",
            bills=["S42"],
            principal_lobbyist="SOME FIRM LLC",
            beneficial_client="SOME CLIENT;",
            contractual_client_name="SOME CLIENT",
        )
    )

    materialize_ny(grain, output_dir=tmp_path)

    filings = _read_tsv(tmp_path / "NY_filings.tsv")
    assert filings[0]["total_compensation"] == ""

    links = _read_tsv(tmp_path / "NY_filing_bill_links.tsv")
    assert links[0]["bill_id"] == "S42"
    assert links[0]["comp_per_bill"] == ""


def test_clients_tsv_round_trips_organization_fields(tmp_path, two_filing_grain):
    """A client row round-trips the Organization id/name/source_state and the
    contact_details_json column (empty list for NY client_semiannual, which has
    no contact info) — shape-compatible with releases/wi entity TSVs."""
    materialize_ny(two_filing_grain, output_dir=tmp_path)

    clients = _read_tsv(tmp_path / "NY_clients.tsv")
    gw = [c for c in clients if c["name"] == "GRAHAM WINDHAM"][0]
    assert gw["id"] == "NY-client-graham-windham"
    assert gw["source_state"] == "NY"
    assert gw["contact_details_json"] == "[]"


def test_rerun_is_byte_identical(tmp_path, two_filing_grain):
    """Deterministic sort + fixed lineterminator => a second run over the same
    input produces byte-identical files (the WI idempotency contract)."""
    materialize_ny(two_filing_grain, output_dir=tmp_path)
    first = {
        name: (tmp_path / name).read_bytes()
        for name in (
            "NY_clients.tsv",
            "NY_lobbyists.tsv",
            "NY_filings.tsv",
            "NY_filing_bill_links.tsv",
        )
    }

    materialize_ny(two_filing_grain, output_dir=tmp_path)
    for name, content in first.items():
        assert (tmp_path / name).read_bytes() == content, f"{name} not idempotent"


def test_empty_grain_writes_header_only_files(tmp_path):
    """An empty grain (everything upstream-filtered) writes header-only TSVs
    and returns all-zero counts — a valid 'nothing here' result, not a crash."""
    # Build a real grain, then take its empty slice — the shape an upstream
    # filter that removed every row would actually produce (canonical columns
    # present, zero rows), not a raw frame missing the canonical columns.
    empty = _grain_from_raw(
        _exploded_rows(
            form_submission_id="1", filing_type="Original", comp="1", bills=["S1"]
        )
    ).iloc[0:0]

    counts = materialize_ny(empty, output_dir=tmp_path)

    assert counts == {
        "clients": 0,
        "lobbyists": 0,
        "filings": 0,
        "filing_bill_links": 0,
    }
    # files exist with just a header row
    assert _read_tsv(tmp_path / "NY_filings.tsv") == []
