"""Behavior tests for the NY ``parties_lobbied`` disclosed-lawmaker edge
(``io/ny/parties``).

The edge ingests NY's disclosed "who was lobbied" free-text field and resolves
the named legislators to an Open States ``ocd-person`` id. Phase 0
(``results/20260606_ny_parties_lobbied_grain.md``) established:

  * grain — ``parties_lobbied`` is a per-filing SET (its own denormalization
    axis), so the edge is ``FILING_KEY -> {distinct resolved parties}``;
  * matching — exact full-name match on the OS bill-sponsorship roster resolves
    only 63%; a deterministic first-name+last-name key (drop the middle initial)
    resolves 93.7% with ZERO collisions, so that is the MVP key;
  * only legislator-titled values (``Senator`` / ``Assembly member`` / …) are
    resolved; executive offices, agencies, committee staff, and "entire
    legislature" broadcasts are kept with ``resolved=False`` and the raw string
    preserved (no taxonomy yet).

Tests assert real resolver behavior on the actual free-text shapes from the recon
doc, the per-filing dedup grain (including supersession), and the on-disk TSV
determinism — never mocks, never type-shape assertions.
"""

from __future__ import annotations

import csv

import pandas as pd

from lobby_analysis.io.ny.parties import (
    build_legislator_roster,
    extract_filing_parties,
    materialize_parties_lobbied,
    resolve_party_lobbied,
)

# A small first+last-keyed roster (the shape build_legislator_roster returns).
ROSTER = {
    "amy paulin": "ocd-person/aaa",
    "karl brabenec": "ocd-person/ccc",
    "shelley mayer": "ocd-person/bbb",
    "pat o'donnell": "ocd-person/ddd",
}


def _read_tsv(path) -> list[dict]:
    with open(path, encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


# ---------------------------------------------------------------------------
# resolve_party_lobbied — (raw, name, person_id|None, resolved)
# ---------------------------------------------------------------------------


def test_resolve_named_legislator_exact():
    raw, name, pid, resolved = resolve_party_lobbied("Assembly member Amy R. Paulin", ROSTER)
    assert resolved is True
    assert pid == "ocd-person/aaa"
    assert name == "Amy R. Paulin"
    assert raw == "Assembly member Amy R. Paulin"


def test_resolve_strips_staff_member_suffix():
    _, name, pid, resolved = resolve_party_lobbied(
        "Assembly member Karl A. Brabenec, staff member", ROSTER
    )
    assert resolved is True
    assert pid == "ocd-person/ccc"
    assert name == "Karl A. Brabenec"


def test_resolve_drops_middle_initial_first_last_key():
    # Roster has "shelley mayer" (no middle initial); disclosure carries "B." —
    # the first+last key is the load-bearing Phase-0 behavior.
    _, _, pid, resolved = resolve_party_lobbied("Senator Shelley B. Mayer", ROSTER)
    assert resolved is True
    assert pid == "ocd-person/bbb"


def test_resolve_staff_suffix_and_middle_initial_together():
    _, _, pid, resolved = resolve_party_lobbied("Senator Shelley B. Mayer, staff member", ROSTER)
    assert resolved is True
    assert pid == "ocd-person/bbb"


def test_resolve_decodes_html_entity():
    # The disclosure field is HTML-encoded; the apostrophe entity must decode
    # before matching (reuses the _clean_name html.unescape path).
    _, name, pid, resolved = resolve_party_lobbied("Assembly member Pat O&#39;Donnell", ROSTER)
    assert resolved is True
    assert pid == "ocd-person/ddd"
    assert name == "Pat O'Donnell"


def test_resolve_executive_office_unresolved():
    raw, name, pid, resolved = resolve_party_lobbied("Executive Chamber/Office of the Governor", ROSTER)
    assert resolved is False
    assert pid is None
    assert name == ""
    assert raw == "Executive Chamber/Office of the Governor"  # preserved


def test_resolve_chamber_broadcast_unresolved():
    _, _, pid, resolved = resolve_party_lobbied("A communication sent to entire NYS Legislature", ROSTER)
    assert resolved is False
    assert pid is None


def test_resolve_agency_unresolved():
    _, _, _, resolved = resolve_party_lobbied("Department of Education (NYSED)", ROSTER)
    assert resolved is False


def test_resolve_executive_title_not_a_legislator():
    # "Governor Kathy Hochul" carries an executive title, not a legislator title —
    # must NOT resolve to a legislator even after parenthetical stripping.
    _, _, pid, resolved = resolve_party_lobbied("Governor Kathy Hochul (effective 8/24/21)", ROSTER)
    assert resolved is False
    assert pid is None


def test_resolve_none_and_empty():
    assert resolve_party_lobbied(None, ROSTER) == ("", "", None, False)
    assert resolve_party_lobbied("   ", ROSTER) == ("", "", None, False)


def test_resolve_legislator_absent_from_roster_unresolved():
    # A named legislator (correct title + format) who simply isn't in the roster
    # (e.g. a non-sponsoring member) stays unresolved — raw preserved.
    raw, name, pid, resolved = resolve_party_lobbied("Senator Elizabeth Krueger", ROSTER)
    assert resolved is False
    assert pid is None
    assert raw == "Senator Elizabeth Krueger"


# ---------------------------------------------------------------------------
# build_legislator_roster — first+last -> ocd-person, from sponsorships CSV
# ---------------------------------------------------------------------------


def _write_sponsorships(csv_dir, rows: list[dict]) -> None:
    path = csv_dir / "NY_2025-2026_bill_sponsorships.csv"
    fields = ["id", "name", "entity_type", "organization_id", "person_id", "bill_id", "primary", "classification"]
    with path.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in fields})


def test_build_roster_keys_first_last(tmp_path):
    _write_sponsorships(tmp_path, [
        {"name": "Amy R. Paulin", "entity_type": "person", "person_id": "ocd-person/aaa"},
        {"name": "Shelley B. Mayer", "entity_type": "person", "person_id": "ocd-person/bbb"},
        # an organization (committee) sponsor — excluded (no person id / not a person)
        {"name": "Rules Committee", "entity_type": "organization", "person_id": ""},
        # a person row with empty person_id — excluded
        {"name": "Ghost Member", "entity_type": "person", "person_id": ""},
    ])
    roster = build_legislator_roster(tmp_path)
    assert roster["amy paulin"] == "ocd-person/aaa"
    assert roster["shelley mayer"] == "ocd-person/bbb"
    assert "rules committee" not in roster
    assert "ghost member" not in roster


def test_build_roster_resolves_a_real_disclosure_value(tmp_path):
    _write_sponsorships(tmp_path, [
        {"name": "Amy R. Paulin", "entity_type": "person", "person_id": "ocd-person/aaa"},
    ])
    roster = build_legislator_roster(tmp_path)
    _, _, pid, resolved = resolve_party_lobbied("Assembly member Amy R. Paulin, staff member", roster)
    assert resolved is True
    assert pid == "ocd-person/aaa"


# ---------------------------------------------------------------------------
# extract_filing_parties — FILING_KEY -> {distinct resolved parties}
# ---------------------------------------------------------------------------


def _norm_row(*, sub, parties, period="Jan/June", firm="THE PARKSIDE GROUP LLC",
              client="GRAHAM WINDHAM;", contractual="GRAHAM WINDHAM", year="2025", focus="S100"):
    return {
        "reporting_year": year,
        "reporting_period": period,
        "form_submission_id": sub,
        "principal_lobbyist": firm,
        "beneficial_client": client,
        "contractual_client_name": contractual,
        "focus_identifying_number": focus,
        "parties_lobbied": parties,
    }


def test_extract_dedups_distinct_parties_per_filing():
    # One filing; the cartesian repeats parties and mixes staff/non-staff forms.
    rows = [
        _norm_row(sub="100", parties="Senator Shelley B. Mayer", focus="S100"),
        _norm_row(sub="100", parties="Senator Shelley B. Mayer, staff member", focus="S100"),
        _norm_row(sub="100", parties="Assembly member Amy R. Paulin", focus="S200"),
        _norm_row(sub="100", parties="Executive Chamber/Office of the Governor", focus="S200"),
        _norm_row(sub="100", parties="Senator Shelley B. Mayer", focus="S300"),
    ]
    out = extract_filing_parties(pd.DataFrame(rows), ROSTER)
    # Mayer (collapsing staff + dup) -> 1; Paulin -> 1; Governor office -> 1.
    assert len(out) == 3
    pids = set(out.loc[out["resolved"], "party_lobbied_person_id"])
    assert pids == {"ocd-person/aaa", "ocd-person/bbb"}
    # the non-individual is kept, not dropped
    unresolved = out.loc[~out["resolved"], "party_lobbied_raw"].tolist()
    assert unresolved == ["Executive Chamber/Office of the Governor"]
    # filing identity carried
    assert set(out["filing_id"]) == {"100"}


def test_extract_drops_superseded_submission():
    # Same business key, two submissions; the amendment (higher id) supersedes.
    rows = [
        _norm_row(sub="100", parties="Senator Shelley B. Mayer"),   # superseded
        _norm_row(sub="200", parties="Assembly member Amy R. Paulin"),  # latest
    ]
    out = extract_filing_parties(pd.DataFrame(rows), ROSTER)
    assert set(out["filing_id"]) == {"200"}
    assert out["party_lobbied_person_id"].tolist() == ["ocd-person/aaa"]


def test_extract_separate_firms_each_get_the_party_set():
    # Co-retained firms on one client submission each carry the client's parties.
    rows = [
        _norm_row(sub="100", firm="FIRM A", parties="Assembly member Amy R. Paulin"),
        _norm_row(sub="100", firm="FIRM B", parties="Assembly member Amy R. Paulin"),
    ]
    out = extract_filing_parties(pd.DataFrame(rows), ROSTER)
    assert len(out) == 2
    assert set(out["lobbyist_id"]) == {"NY-lobbyist-firm-a", "NY-lobbyist-firm-b"}


def test_extract_empty_frame_yields_empty():
    out = extract_filing_parties(pd.DataFrame(columns=list(_norm_row(sub="1", parties="x").keys())), ROSTER)
    assert len(out) == 0


# ---------------------------------------------------------------------------
# materialize_parties_lobbied — the release TSV
# ---------------------------------------------------------------------------

_EXPECTED_COLUMNS = [
    "reporting_year",
    "reporting_period",
    "filing_id",
    "lobbyist_id",
    "client_id",
    "party_lobbied_raw",
    "party_lobbied_name",
    "party_lobbied_person_id",
    "resolved",
]


def _sample_parties_frame():
    rows = [
        _norm_row(sub="100", parties="Senator Shelley B. Mayer"),
        _norm_row(sub="100", parties="Assembly member Amy R. Paulin"),
        _norm_row(sub="100", parties="Executive Chamber/Office of the Governor"),
    ]
    return extract_filing_parties(pd.DataFrame(rows), ROSTER)


def test_materialize_writes_expected_columns(tmp_path):
    counts = materialize_parties_lobbied(_sample_parties_frame(), output_dir=tmp_path)
    path = tmp_path / "NY_filing_parties_lobbied.tsv"
    assert path.exists()
    rows = _read_tsv(path)
    assert list(rows[0].keys()) == _EXPECTED_COLUMNS
    assert counts["filing_parties_lobbied"] == len(rows) == 3


def test_materialize_resolved_flag_round_trips(tmp_path):
    materialize_parties_lobbied(_sample_parties_frame(), output_dir=tmp_path)
    rows = _read_tsv(tmp_path / "NY_filing_parties_lobbied.tsv")
    by_pid = {r["party_lobbied_person_id"]: r for r in rows}
    assert by_pid["ocd-person/bbb"]["resolved"] == "True"
    # the unresolved office row keeps its raw and an empty person id
    office = [r for r in rows if r["resolved"] == "False"]
    assert len(office) == 1
    assert office[0]["party_lobbied_raw"] == "Executive Chamber/Office of the Governor"
    assert office[0]["party_lobbied_person_id"] == ""


def test_materialize_byte_identical_rerun(tmp_path):
    frame = _sample_parties_frame()
    materialize_parties_lobbied(frame, output_dir=tmp_path)
    first = (tmp_path / "NY_filing_parties_lobbied.tsv").read_bytes()
    materialize_parties_lobbied(frame, output_dir=tmp_path)
    second = (tmp_path / "NY_filing_parties_lobbied.tsv").read_bytes()
    assert first == second


def test_materialize_empty_input_header_only(tmp_path):
    empty = extract_filing_parties(
        pd.DataFrame(columns=list(_norm_row(sub="1", parties="x").keys())), ROSTER
    )
    counts = materialize_parties_lobbied(empty, output_dir=tmp_path)
    content = (tmp_path / "NY_filing_parties_lobbied.tsv").read_text(encoding="utf-8")
    assert content == "\t".join(_EXPECTED_COLUMNS) + "\n"
    assert counts["filing_parties_lobbied"] == 0
