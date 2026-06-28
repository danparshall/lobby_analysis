"""TDD tests for the OH chain composer's deterministic entity-ID derivation.

Plan: ``docs/active/leave-behind-prep/plans/20260615_composer_side_mini_swap_normalizations.md``
Step 1 (entity-ID derivation from name).

Why these exist
---------------

Pre-PR-59 the OH chain composer read ``principal_id`` and ``lobbyist_id``
straight off the model-emitted ``LobbyingFiling.employer.id`` and
``LobbyingFiling.filer_person.id`` schema fields. Sonnet emits a (mostly)
stable kebab-case ID; mini's IDs are inconsistent. The 2026-06-15 chain-
level experiment measured 97.9% / 98.3% per-row disagreement on those two
columns between sonnet-sourced and mini-sourced chains, with **identical
names underneath** — i.e., model-formatting noise, not real disagreement.

The fix is to derive both IDs deterministically from the corresponding
``name`` at composer time, dropping the model-emitted ``.id`` from the
chain output entirely. (The model-emitted ``.id`` remains on the
``LobbyingFiling`` for audit; the composer just stops reading it.)

These tests pin the algorithm contract:

- Returns ``None`` for None / empty / whitespace-only input (no
  ``"org-"`` prefix attached to nothing).
- ASCII-folds accented characters so unicode-name filings don't generate
  IDs that fail downstream tooling that assumes ASCII.
- Collapses any run of non-alphanumerics to a single hyphen and strips
  leading/trailing hyphens — so ``"Coinbase, Inc."`` and ``"Coinbase Inc"``
  collapse to the same ID.
- Adds the ``org-`` / ``person-`` prefix unconditionally so the chain's
  ID column is type-identifiable at a glance.

These are pure-logic tests; no fixtures from disk.
"""
from __future__ import annotations

import pytest

from lobby_analysis.allocation.oh.chain import (
    _slugify,
    derive_org_id,
    derive_person_id,
)


# ---------------------------------------------------------------------------
# derive_org_id
# ---------------------------------------------------------------------------


class TestDeriveOrgId:
    def test_basic_kebab_case(self):
        assert derive_org_id("Cleveland Browns") == "org-cleveland-browns"

    @pytest.mark.parametrize(
        "name,expected",
        [
            ("Coinbase, Inc.", "org-coinbase-inc"),
            ("Coinbase Inc", "org-coinbase-inc"),  # collapses to the same ID
            ("AAA Club Alliance Inc", "org-aaa-club-alliance-inc"),
            ("Smith & Wesson", "org-smith-wesson"),
            ("R&D Corp.", "org-r-d-corp"),
        ],
    )
    def test_punctuation_handling(self, name, expected):
        assert derive_org_id(name) == expected

    def test_accented_characters_ascii_folded(self):
        # NFKD + ASCII-encode strips accents so unicode names don't
        # produce IDs that break downstream ASCII-only tooling.
        assert derive_org_id("Café Société") == "org-cafe-societe"

    @pytest.mark.parametrize("empty_input", [None, "", "   ", "\t\n"])
    def test_empty_or_whitespace_returns_none(self, empty_input):
        assert derive_org_id(empty_input) is None

    def test_leading_trailing_punctuation_stripped(self):
        assert derive_org_id("...Acme Corp...") == "org-acme-corp"

    def test_run_of_separators_collapsed(self):
        assert derive_org_id("Foo   ---   Bar") == "org-foo-bar"


# ---------------------------------------------------------------------------
# derive_person_id
# ---------------------------------------------------------------------------


class TestDerivePersonId:
    def test_basic(self):
        assert derive_person_id("Jane Doe") == "person-jane-doe"

    @pytest.mark.parametrize(
        "name,expected",
        [
            ("Jane Q. Doe", "person-jane-q-doe"),
            ("O'Brien, John", "person-o-brien-john"),
            ("María González", "person-maria-gonzalez"),
        ],
    )
    def test_assorted_names(self, name, expected):
        assert derive_person_id(name) == expected

    @pytest.mark.parametrize("empty_input", [None, "", "   "])
    def test_empty_or_whitespace_returns_none(self, empty_input):
        assert derive_person_id(empty_input) is None


# ---------------------------------------------------------------------------
# _slugify (private helper exposed for direct testing of edge cases)
# ---------------------------------------------------------------------------


class TestSlugify:
    @pytest.mark.parametrize(
        "raw,expected",
        [
            ("Cleveland Browns", "cleveland-browns"),
            ("Coinbase, Inc.", "coinbase-inc"),
            ("Café Société", "cafe-societe"),
            ("ALREADY-KEBAB-CASE", "already-kebab-case"),
            ("123 numeric prefix", "123-numeric-prefix"),
            ("trailing space ", "trailing-space"),
            ("\tleading tab", "leading-tab"),
        ],
    )
    def test_slugify_cases(self, raw, expected):
        assert _slugify(raw) == expected

    def test_slugify_drops_runs_of_non_alphanumeric(self):
        assert _slugify("foo!!!bar???baz") == "foo-bar-baz"

    def test_slugify_empty_string_returns_empty(self):
        # _slugify's contract is "slug or empty string"; the public
        # derive_* helpers handle the None-ification.
        assert _slugify("") == ""
