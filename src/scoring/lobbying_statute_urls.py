"""Curated per-state URL lists for lobby-statute retrieval.

Each entry maps (state_abbr, vintage_year) to a list of Justia statute-leaf URLs
that together constitute that state's lobby-disclosure statute body for that
vintage. Curated by human review — see
`docs/historical/pri-calibration/convos/20260418_phase2_kickoff_and_subset_selection.md`
for rationale, and the Phase 1 audit CSV
(`docs/historical/pri-calibration/results/20260418_justia_retrieval_audit.csv`) for
vintage-selection logic.

Justia is the project's *operational* statute SSOT — chosen for stable per-vintage
URLs (`/codes/<state>/<year>/...`) and programmatic access. It is NOT the
canonical authority: that role belongs to each state's own legislative
codification (CA leginfo, NY official Legislative Law, TX statutes.capitol, etc.)
— the state-level analog of the Federal Register / U.S. Code. Justia republishes
those.

Start small: minimum viable coverage per state (core registration + disclosure
chapter). Expand only if calibration agreement against PRI 2010 is poor for
that state.
"""

from __future__ import annotations

LOBBYING_STATUTE_URLS: dict[tuple[str, int], list[str]] = {
    # CA - Political Reform Act Ch. 6 (Lobbyists): Art. 1 Definitions/Registration
    # (§§ 86100-86118) + Art. 2 Prohibitions/Reports (§§ 86201-86206). 2010 exact.
    ("CA", 2010): [
        "https://law.justia.com/codes/california/2010/gov/86100-86118.html",
        "https://law.justia.com/codes/california/2010/gov/86201-86206.html",
    ],
    # TX - Gov Code Title 3 Ch. 305 (Registration of Lobbyists). 2010 not hosted
    # on Justia; 2009 is the nearest vintage within ±2 tolerance.
    ("TX", 2009): [
        "https://law.justia.com/codes/texas/2009/government-code/title-3-legislative-branch/chapter-305-registration-of-lobbyists/",
    ],
    # NY - Regulation of Lobbying Act (Ch. 1040/81; codified into Legis. Law
    # Art. 1-A). Justia hosts the full codified Act as a standalone "RLA" slug.
    # Single-page statute body, ~54KB.
    ("NY", 2010): [
        "https://law.justia.com/codes/new-york/2010/rla/",
    ],
    # WI - Statutes Ch. 13 Subch. III (Lobbying Regulation), §§ 13.61-13.75.
    # 16 per-section leaf pages.
    ("WI", 2010): [
        f"https://law.justia.com/codes/wisconsin/2010/13/13.{n}.html"
        for n in (
            "61", "62", "621", "625", "63", "64", "65", "66",
            "67", "68", "685", "69", "695", "71", "74", "75",
        )
    ],
    # WY - Title 28 (Legislature) Ch. 7 (Lobbyists). Single-page chapter-leaf.
    ("WY", 2010): [
        "https://law.justia.com/codes/wyoming/2010/Title28/chapter7.html",
    ],
    # OH - Three separate lobbying statute bodies across two chapters. 2010 exact.
    # URL pattern inferred from confirmed 2010 leaf (101_83.html); needs verification.
    #
    # Legislative lobbying: ORC Ch. 101 §§ 101.70-101.79
    # Retirement system lobbying: ORC Ch. 101 §§ 101.90-101.99
    # Executive agency lobbying: ORC Ch. 121 §§ 121.60-121.69
    ("OH", 2010): [
        # Legislative lobbying (Ch. 101, §§ 101.70-101.79)
        *[
            f"https://law.justia.com/codes/ohio/2010/title1/chapter101/101_{n}.html"
            for n in range(70, 80)
        ],
        # Retirement system lobbying (Ch. 101, §§ 101.90-101.99)
        *[
            f"https://law.justia.com/codes/ohio/2010/title1/chapter101/101_{n}.html"
            for n in range(90, 100)
        ],
        # Executive agency lobbying (Ch. 121, §§ 121.60-121.69)
        *[
            f"https://law.justia.com/codes/ohio/2010/title1/chapter121/121_{n}.html"
            for n in range(60, 70)
        ],
    ],
    # OH 2025 - same three statute bodies as 2010, sourced from the most recent
    # Justia-hosted vintage (Justia hosts up to 2025 for OH; no 2026 available
    # as of 2026-04). Section numbering verified intact 2010 → 2025 by boundary
    # spot-check (§101.70, §101.79, §101.99, §121.60, §121.69 all resolve with
    # subject titles matching the 2010 list). URL pattern identical to 2010
    # with year swapped — Justia redirects newer slug-based URLs back to this
    # legacy underscore form.
    ("OH", 2025): [
        # Legislative lobbying (Ch. 101, §§ 101.70-101.79)
        *[
            f"https://law.justia.com/codes/ohio/2025/title1/chapter101/101_{n}.html"
            for n in range(70, 80)
        ],
        # Retirement system lobbying (Ch. 101, §§ 101.90-101.99)
        *[
            f"https://law.justia.com/codes/ohio/2025/title1/chapter101/101_{n}.html"
            for n in range(90, 100)
        ],
        # Executive agency lobbying (Ch. 121, §§ 121.60-121.69)
        *[
            f"https://law.justia.com/codes/ohio/2025/title1/chapter121/121_{n}.html"
            for n in range(60, 70)
        ],
    ],
}

# Active calibration subset — (state_abbr, vintage_year) pairs that map 1:1
# into LOBBYING_STATUTE_URLS. Used by the calibrate subcommand and by Phase 3.
# Reduced from original 5-state set (CA/TX/NY/WI/WY) to focus on CA, TX (known
# difficult — cross-referenced support chapters), and OH (three separate lobbying
# statute bodies across two chapters).
CALIBRATION_SUBSET: list[tuple[str, int]] = [
    ("CA", 2010),
    ("TX", 2009),
    ("OH", 2010),
]
