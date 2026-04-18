"""Curated per-state URL lists for lobby-statute retrieval.

Each entry maps (state_abbr, vintage_year) to a list of Justia statute-leaf URLs
that together constitute that state's lobby-disclosure statute body for that
vintage. Curated by human review — see
`docs/active/pri-calibration/convos/20260418_phase2_kickoff_and_subset_selection.md`
for rationale, and the Phase 1 audit CSV
(`docs/active/pri-calibration/results/20260418_justia_retrieval_audit.csv`) for
vintage-selection logic.

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
}

# The 5-state calibration subset — (state_abbr, vintage_year) pairs that map 1:1
# into LOBBYING_STATUTE_URLS. Used by the calibrate subcommand and by Phase 3.
CALIBRATION_SUBSET: list[tuple[str, int]] = [
    ("CA", 2010),
    ("TX", 2009),
    ("NY", 2010),
    ("WI", 2010),
    ("WY", 2010),
]
