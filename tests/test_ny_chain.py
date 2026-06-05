"""Behavior tests for the NY Phase-4 chain composer's OS-independent core.

Two concerns are tested here (the parts that do **not** depend on the Open
States bill bundle, so they can be built before that gated download lands):

1. **Coalition beneficiary split (Decision 7).** Some NY ``beneficial_client``
   cells pack many beneficiaries into one semicolon-delimited string (346 such
   client rows in the live 2025 release). The chain layer splits them into one
   beneficiary per entity and allocates credit evenly. ``split_beneficiaries``
   is the splitter; it mirrors ``parse.parse_individual_lobbyists`` (trim, drop
   empties from trailing delimiters, de-dupe by slug, preserve order).

2. **No-loss conservation under the multiplicative split.** A filing with
   compensation ``C``, ``M`` beneficiaries, and ``N`` bills emits ``M·N`` cells
   each carrying ``comp_per_cell``; the cells must sum to ``C`` exactly (no cent
   lost or duplicated). The conservation primitive is ``parse.even_split`` (the
   integer-cent splitter relocated from ``materialize`` so both the Phase-3
   per-bill split and the Phase-4 per-cell split share one implementation). The
   multiplicative case is just ``even_split(C, M*N)``.

These assert real allocated values, not call-shape. The full composer test
(sponsor attachment, unmatched-bill flagging) lands with the OS bundle.
"""

from __future__ import annotations

import csv
from decimal import Decimal
from pathlib import Path

from lobby_analysis.allocation.ny.chain import (
    compose_chain,
    load_os_bills,
    normalize_bill_id_to_os,
    split_beneficiaries,
)
from lobby_analysis.io.ny.parse import even_split


# ---------------------------------------------------------------------------
# tmp_path release/OS fixtures (hermetic — no dependency on the gitignored
# real OS bundle, so these run anywhere)
# ---------------------------------------------------------------------------


def _write_tsv(path: Path, fieldnames, rows) -> None:
    with path.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(fieldnames), delimiter="\t", lineterminator="\n")
        w.writeheader()
        for r in rows:
            w.writerow(r)


def _make_release(dirpath: Path, *, clients, lobbyists, links) -> Path:
    """Write a minimal releases/ny/ trio into ``dirpath``."""
    dirpath.mkdir(parents=True, exist_ok=True)
    _write_tsv(
        dirpath / "NY_clients.tsv",
        ("id", "name", "source_state", "classification", "legal_form", "sector", "contact_details_json"),
        [{"id": c[0], "name": c[1], "source_state": "NY", "classification": "",
          "legal_form": "", "sector": "", "contact_details_json": "[]"} for c in clients],
    )
    _write_tsv(
        dirpath / "NY_lobbyists.tsv",
        ("id", "name", "source_state", "classification", "legal_form", "sector", "contact_details_json"),
        [{"id": lo[0], "name": lo[1], "source_state": "NY", "classification": "",
          "legal_form": "", "sector": "", "contact_details_json": "[]"} for lo in lobbyists],
    )
    _write_tsv(
        dirpath / "NY_filing_bill_links.tsv",
        ("filing_id", "lobbyist_id", "client_id", "bill_id", "bill_print_version",
         "comp_per_bill", "filing_compensation", "n_bills_in_filing",
         "reporting_year", "reporting_period"),
        links,
    )
    return dirpath


# ---------------------------------------------------------------------------
# split_beneficiaries (Decision 7)
# ---------------------------------------------------------------------------


def test_single_client_is_a_one_element_list():
    """A non-coalition ``beneficial_client`` is one beneficiary; the splitter
    returns a single-element list so M=1 and the per-cell split is a no-op."""
    assert split_beneficiaries("Suffolk County Court Employees Association Inc") == [
        "Suffolk County Court Employees Association Inc"
    ]


def test_semicolon_list_splits_into_separate_beneficiaries():
    """The canonical coalition cell: a semicolon-delimited list becomes one
    cleaned beneficiary per element, order preserved."""
    raw = "239 Entertainment LLC; AoK Maintenance Supply"
    assert split_beneficiaries(raw) == ["239 Entertainment LLC", "AoK Maintenance Supply"]


def test_each_beneficiary_is_whitespace_trimmed():
    """Stray internal/leading/trailing whitespace around each element is
    trimmed so the same beneficiary doesn't fork on spacing."""
    assert split_beneficiaries("  ACME LLC ;   Beta Corp  ") == ["ACME LLC", "Beta Corp"]


def test_trailing_delimiter_does_not_emit_empty_beneficiary():
    """A trailing ``;`` (common in NY data) must not produce an empty
    beneficiary token."""
    assert split_beneficiaries("ACME LLC; Beta Corp;") == ["ACME LLC", "Beta Corp"]


def test_duplicate_beneficiaries_are_deduped_by_slug_order_preserving():
    """A beneficiary repeated within one cell collapses to a single entry
    (deduped by slug, like ``parse_individual_lobbyists``), keeping the first
    display form and original order."""
    assert split_beneficiaries("ACME LLC; acme llc; Beta Corp") == ["ACME LLC", "Beta Corp"]


def test_empty_or_missing_cell_yields_empty_list():
    """An empty / whitespace / None cell has no beneficiaries — return []
    (not [""]), so a filing with no usable client contributes no cells."""
    assert split_beneficiaries("") == []
    assert split_beneficiaries("   ") == []
    assert split_beneficiaries(None) == []
    assert split_beneficiaries(";") == []


# ---------------------------------------------------------------------------
# normalize_bill_id_to_os (Decision 8 — calibrated to the real OS format)
# ---------------------------------------------------------------------------
#
# Verified against the staged OS NY 2025-2026 bills.csv (25,250 bills): the OS
# ``identifier`` is ``<LETTER><SPACE><UNPADDED-DIGITS>`` — e.g. "A 48", "A 1668",
# "S 550", "A 11019". A single space, NO zero-padding, NO print suffix (zero OS
# identifiers end in a letter; amendment prints live in ``bill_versions``). The
# normalizer canonicalizes the NY lobbying ``bill_id`` TO that form.


def test_normalizes_to_os_space_separated_unpadded_form():
    """The core mapping: NY lobbying ``A1668`` -> OS ``A 1668`` (letter, single
    space, digits). This is the join key Open States actually uses."""
    assert normalize_bill_id_to_os("A1668") == "A 1668"
    assert normalize_bill_id_to_os("S550") == "S 550"


def test_strips_leading_zeros_to_match_os_unpadded_identifiers():
    """OS is unpadded (``A 48``, never ``A 0048``), and the NY source is
    inconsistently padded (``A00804`` vs ``A804``). Both must collapse to the
    same unpadded OS key so one bill doesn't fork into two."""
    assert normalize_bill_id_to_os("A00804") == "A 804"
    assert normalize_bill_id_to_os("A804") == "A 804"
    assert normalize_bill_id_to_os("A0048") == "A 48"


def test_strips_amendment_print_suffix_for_the_join_key():
    """OS keys by the base bill, not the print. ``S550-A`` (first amended print)
    joins on ``S 550``; the suffixed form is preserved elsewhere as
    ``bill_print_version``, not here."""
    assert normalize_bill_id_to_os("S550-A") == "S 550"
    assert normalize_bill_id_to_os("A00804-C") == "A 804"


def test_already_normalized_or_spaced_input_is_idempotent():
    """Whitespace/case variants and an already-spaced id normalize to the same
    canonical key (idempotent), so re-running can't fork a bill."""
    assert normalize_bill_id_to_os("  a1668 ") == "A 1668"
    assert normalize_bill_id_to_os("A 1668") == "A 1668"


def test_non_bill_or_empty_input_yields_none():
    """A non-parseable identifier (free text, empty, None) yields None — it
    can't be a join key, and the chain flags it as not OS-resolvable rather
    than fabricating a bill."""
    assert normalize_bill_id_to_os("various") is None
    assert normalize_bill_id_to_os("") is None
    assert normalize_bill_id_to_os(None) is None


# ---------------------------------------------------------------------------
# even_split conservation under the multiplicative (M·N) split
# ---------------------------------------------------------------------------


def test_even_split_divides_evenly_when_it_can():
    """C / n with no remainder: each part is exactly C/n and the parts sum to C."""
    parts = even_split(Decimal("100.00"), 4)
    assert parts == [Decimal("25.00")] * 4
    assert sum(parts) == Decimal("100.00")


def test_even_split_distributes_the_remainder_to_the_first_parts():
    """Odd division: the leftover cents go to the first parts so the sum is
    still exactly C (no rounding loss). 100/3 -> 33.34 + 33.33 + 33.33."""
    parts = even_split(Decimal("100.00"), 3)
    assert parts == [Decimal("33.34"), Decimal("33.33"), Decimal("33.33")]
    assert sum(parts) == Decimal("100.00")


def test_multiplicative_split_conserves_C_across_M_times_N_cells():
    """The Decision-7 invariant the plan calls out: a filing with comp C, M
    beneficiaries, and N bills splits into M*N cells summing exactly to C. This
    is just even_split(C, M*N) — the multiplicative split is a single even-split
    over the cell count, so remainders never compound across the two axes."""
    C = Decimal("345762.46")
    M, N = 3, 7  # multi-beneficiary x multi-bill
    cells = even_split(C, M * N)
    assert len(cells) == M * N
    assert sum(cells) == C


def test_even_split_of_zero_parts_is_empty():
    """Degenerate guard: no cells requested -> no parts (a filing with no bills
    or no beneficiaries emits nothing, rather than raising)."""
    assert even_split(Decimal("100.00"), 0) == []


# ---------------------------------------------------------------------------
# load_os_bills (OS bundle -> per-bill primary sponsors, keyed by identifier)
# ---------------------------------------------------------------------------


def _make_os_csvs(dirpath: Path, *, bills, sponsorships) -> Path:
    """Write minimal OS bills.csv + bill_sponsorships.csv (real column shape)."""
    dirpath.mkdir(parents=True, exist_ok=True)
    _write_tsv_csv(
        dirpath / "NY_2025-2026_bills.csv",
        ("id", "identifier", "title", "classification", "session_identifier",
         "jurisdiction", "organization_classification"),
        bills,
    )
    _write_tsv_csv(
        dirpath / "NY_2025-2026_bill_sponsorships.csv",
        ("id", "name", "entity_type", "organization_id", "person_id", "bill_id",
         "primary", "classification"),
        sponsorships,
    )
    return dirpath


def _write_tsv_csv(path: Path, fieldnames, rows) -> None:
    with path.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(fieldnames), lineterminator="\n")
        w.writeheader()
        for r in rows:
            w.writerow(r)


def test_load_os_bills_ignores_the_related_bills_decoy_file(tmp_path):
    """``NY_*_bills.csv`` also globs ``NY_<session>_bill_related_bills.csv`` (a
    different schema). The loader must read the canonical bills file, not the
    decoy — regression guard for the glob-too-loose bug that zeroed the join."""
    osdir = _make_os_csvs(
        tmp_path,
        bills=[{"id": "ocd-bill/1", "identifier": "A 5", "title": "Real Bill",
                "classification": "bill", "session_identifier": "2025-2026",
                "jurisdiction": "NY", "organization_classification": "lower"}],
        sponsorships=[{"id": "s1", "name": "Jane Doe", "entity_type": "person",
                       "organization_id": "", "person_id": "ocd-person/aaa",
                       "bill_id": "ocd-bill/1", "primary": "True", "classification": "primary"}],
    )
    # decoy file: same glob, different schema, lexicographically sorts FIRST
    _write_tsv_csv(
        osdir / "NY_2025-2026_bill_related_bills.csv",
        ("id", "identifier", "related_bill_id", "relation_type"),
        [{"id": "ocd-bill/999", "identifier": "Z 9", "related_bill_id": "ocd-bill/1",
          "relation_type": "companion"}],
    )
    os_bills = load_os_bills(osdir)
    assert "A 5" in os_bills          # canonical file read
    assert "Z 9" not in os_bills      # decoy ignored
    assert os_bills["A 5"].primary_sponsors[0].name == "Jane Doe"


def test_load_os_bills_keys_by_identifier_with_primary_sponsors(tmp_path):
    """The loader keys bills by the OS ``identifier`` ("A 1668") and attaches
    only the *primary* sponsor(s); cosponsors are excluded (v1 scope)."""
    osdir = _make_os_csvs(
        tmp_path,
        bills=[
            {"id": "ocd-bill/1", "identifier": "A 1668", "title": "An Act re X",
             "classification": "bill", "session_identifier": "2025-2026",
             "jurisdiction": "NY", "organization_classification": "lower"},
        ],
        sponsorships=[
            {"id": "s1", "name": "Jane Doe", "entity_type": "person", "organization_id": "",
             "person_id": "ocd-person/aaa", "bill_id": "ocd-bill/1", "primary": "True",
             "classification": "primary"},
            {"id": "s2", "name": "John Roe", "entity_type": "person", "organization_id": "",
             "person_id": "ocd-person/bbb", "bill_id": "ocd-bill/1", "primary": "False",
             "classification": "cosponsor"},
        ],
    )
    os_bills = load_os_bills(osdir)
    assert "A 1668" in os_bills
    bill = os_bills["A 1668"]
    assert bill.title == "An Act re X"
    assert [(s.name, s.person_id) for s in bill.primary_sponsors] == [("Jane Doe", "ocd-person/aaa")]


def test_load_os_bills_keeps_collective_org_sponsor_without_person_id(tmp_path):
    """An ``organization`` primary sponsor (committee bill) has no person_id; it
    is kept as a collective sponsor, not dropped."""
    osdir = _make_os_csvs(
        tmp_path,
        bills=[{"id": "ocd-bill/2", "identifier": "S 9", "title": "Committee Bill",
                "classification": "bill", "session_identifier": "2025-2026",
                "jurisdiction": "NY", "organization_classification": "upper"}],
        sponsorships=[{"id": "s3", "name": "Rules Committee", "entity_type": "organization",
                       "organization_id": "ocd-org/x", "person_id": "", "bill_id": "ocd-bill/2",
                       "primary": "True", "classification": "primary"}],
    )
    os_bills = load_os_bills(osdir)
    sp = os_bills["S 9"].primary_sponsors
    assert len(sp) == 1
    assert sp[0].name == "Rules Committee"
    assert sp[0].person_id is None
    assert sp[0].is_collective is True


# ---------------------------------------------------------------------------
# compose_chain — the join, conservation, and unmatched flagging
# ---------------------------------------------------------------------------


def _os_dict():
    """A small in-memory os_bills dict (bypasses the CSV loader)."""
    from lobby_analysis.allocation.ny.chain import NYBillMeta, NYSponsor

    return {
        "A 100": NYBillMeta(
            identifier="A 100", ocd_bill_id="ocd-bill/100", title="Act A100", chamber="lower",
            primary_sponsors=[NYSponsor(name="Jane Doe", person_id="ocd-person/aaa", is_collective=False)],
        ),
        "S 200": NYBillMeta(
            identifier="S 200", ocd_bill_id="ocd-bill/200", title="Act S200", chamber="upper",
            primary_sponsors=[NYSponsor(name="John Roe", person_id="ocd-person/bbb", is_collective=False)],
        ),
    }


def test_compose_chain_conserves_C_across_M_beneficiaries_x_N_bills(tmp_path):
    """The Decision-7 no-loss invariant on the full composer: a filing with
    comp C, M=2 beneficiaries (one coalition cell) and N=2 bills emits 4 distinct
    (beneficiary, bill) cells whose comp_per_cell sums to exactly C."""
    release = _make_release(
        tmp_path / "rel",
        clients=[("NY-client-acme-llc-beta-corp", "ACME LLC; Beta Corp")],
        lobbyists=[("NY-lobbyist-firm-inc", "Firm Inc")],
        links=[
            {"filing_id": "555", "lobbyist_id": "NY-lobbyist-firm-inc",
             "client_id": "NY-client-acme-llc-beta-corp", "bill_id": "A100",
             "bill_print_version": "A100", "comp_per_bill": "50.00",
             "filing_compensation": "100.00", "n_bills_in_filing": "2",
             "reporting_year": "2025", "reporting_period": "JANUARY-JUNE"},
            {"filing_id": "555", "lobbyist_id": "NY-lobbyist-firm-inc",
             "client_id": "NY-client-acme-llc-beta-corp", "bill_id": "S200",
             "bill_print_version": "S200", "comp_per_bill": "50.00",
             "filing_compensation": "100.00", "n_bills_in_filing": "2",
             "reporting_year": "2025", "reporting_period": "JANUARY-JUNE"},
        ],
    )
    chain = compose_chain(release, _os_dict())

    # 2 beneficiaries x 2 bills = 4 distinct cells, each with one primary sponsor
    assert len(chain) == 4
    assert set(chain["beneficiary_name"]) == {"ACME LLC", "Beta Corp"}
    assert chain["n_beneficiaries_in_filing"].unique().tolist() == [2]
    # distinct (beneficiary, bill) cells sum to C exactly
    cells = chain.drop_duplicates(["filing_id", "beneficiary_id", "bill_id"])
    total = sum(Decimal(str(v)) for v in cells["comp_per_cell"])
    assert total == Decimal("100.00")


def test_compose_chain_two_firms_sharing_a_filing_id_each_conserve(tmp_path):
    """Load-bearing: ``filing_id`` (the client's form_submission_id) is shared
    across every firm the client retains. Two firms under one filing_id, each
    with its own compensation, must each conserve independently — the cell
    identity is (filing_id, lobbyist_id, beneficiary, bill), NEVER filing_id
    alone. (This is the chain-layer analog of the $108.9M Phase-3 firm-collapse
    bug.)"""
    release = _make_release(
        tmp_path / "rel",
        clients=[("NY-client-acme-llc", "ACME LLC")],
        lobbyists=[("NY-lobbyist-firm-a", "Firm A"), ("NY-lobbyist-firm-b", "Firm B")],
        links=[
            {"filing_id": "777", "lobbyist_id": "NY-lobbyist-firm-a",
             "client_id": "NY-client-acme-llc", "bill_id": "A100",
             "bill_print_version": "A100", "comp_per_bill": "40.00",
             "filing_compensation": "40.00", "n_bills_in_filing": "1",
             "reporting_year": "2025", "reporting_period": "JANUARY-JUNE"},
            {"filing_id": "777", "lobbyist_id": "NY-lobbyist-firm-b",
             "client_id": "NY-client-acme-llc", "bill_id": "A100",
             "bill_print_version": "A100", "comp_per_bill": "60.00",
             "filing_compensation": "60.00", "n_bills_in_filing": "1",
             "reporting_year": "2025", "reporting_period": "JANUARY-JUNE"},
        ],
    )
    chain = compose_chain(release, _os_dict())
    # Two firms x one bill x one beneficiary = 2 distinct cells (same filing_id,
    # same beneficiary, same bill — distinguished only by lobbyist_id).
    cells = chain.drop_duplicates(
        ["filing_id", "lobbyist_id", "beneficiary_id", "bill_id"]
    )
    assert len(cells) == 2
    total = sum(Decimal(str(v)) for v in cells["comp_per_cell"])
    assert total == Decimal("100.00")  # 40 + 60, neither firm dropped
    # Deduping on filing_id alone would WRONGLY collapse to one $40 or $60 cell.
    by_firm = {r["lobbyist_id"]: Decimal(str(r["comp_per_cell"])) for _, r in cells.iterrows()}
    assert by_firm["NY-lobbyist-firm-a"] == Decimal("40.00")
    assert by_firm["NY-lobbyist-firm-b"] == Decimal("60.00")


def test_compose_chain_attaches_primary_sponsor(tmp_path):
    """Each matched bill cell attaches its OS primary sponsor (id + name)."""
    release = _make_release(
        tmp_path / "rel",
        clients=[("NY-client-acme-llc", "ACME LLC")],
        lobbyists=[("NY-lobbyist-firm-inc", "Firm Inc")],
        links=[{"filing_id": "1", "lobbyist_id": "NY-lobbyist-firm-inc",
                "client_id": "NY-client-acme-llc", "bill_id": "A100",
                "bill_print_version": "A100", "comp_per_bill": "10.00",
                "filing_compensation": "10.00", "n_bills_in_filing": "1",
                "reporting_year": "2025", "reporting_period": "JANUARY-JUNE"}],
    )
    chain = compose_chain(release, _os_dict())
    assert len(chain) == 1
    row = chain.iloc[0]
    assert row["os_bill_identifier"] == "A 100"
    assert row["sponsor_lawmaker_id"] == "ocd-person/aaa"
    assert row["sponsor_lawmaker_name"] == "Jane Doe"
    assert bool(row["os_matched"]) is True
    assert row["bill_title"] == "Act A100"


def test_compose_chain_flags_unmatched_bill_not_dropped(tmp_path):
    """A bill with no OS match (typo'd id / absent from session) is FLAGGED, not
    dropped: a row is emitted with os_matched False, empty sponsor, and its
    comp_per_cell preserved (so dollars are conserved)."""
    release = _make_release(
        tmp_path / "rel",
        clients=[("NY-client-acme-llc", "ACME LLC")],
        lobbyists=[("NY-lobbyist-firm-inc", "Firm Inc")],
        links=[{"filing_id": "9", "lobbyist_id": "NY-lobbyist-firm-inc",
                "client_id": "NY-client-acme-llc", "bill_id": "A51578",
                "bill_print_version": "A51578", "comp_per_bill": "77.00",
                "filing_compensation": "77.00", "n_bills_in_filing": "1",
                "reporting_year": "2025", "reporting_period": "JANUARY-JUNE"}],
    )
    chain = compose_chain(release, _os_dict())
    assert len(chain) == 1
    row = chain.iloc[0]
    assert bool(row["os_matched"]) is False
    assert row["sponsor_lawmaker_id"] == ""
    assert Decimal(str(row["comp_per_cell"])) == Decimal("77.00")


def test_compose_chain_absent_compensation_yields_empty_comp_cells(tmp_path):
    """A filing with no reported compensation emits cells with an empty
    comp_per_cell (not a fabricated 0), still attaching the sponsor."""
    release = _make_release(
        tmp_path / "rel",
        clients=[("NY-client-acme-llc", "ACME LLC")],
        lobbyists=[("NY-lobbyist-firm-inc", "Firm Inc")],
        links=[{"filing_id": "3", "lobbyist_id": "NY-lobbyist-firm-inc",
                "client_id": "NY-client-acme-llc", "bill_id": "A100",
                "bill_print_version": "A100", "comp_per_bill": "",
                "filing_compensation": "", "n_bills_in_filing": "1",
                "reporting_year": "2025", "reporting_period": "JANUARY-JUNE"}],
    )
    chain = compose_chain(release, _os_dict())
    assert len(chain) == 1
    assert chain.iloc[0]["comp_per_cell"] == ""
