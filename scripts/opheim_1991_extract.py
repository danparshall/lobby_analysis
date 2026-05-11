#!/usr/bin/env python
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "pdfplumber>=0.11",
#     "pytesseract>=0.3",
#     "Pillow>=10",
# ]
# ///
"""Extract Opheim 1991 Table 1 (47-state lobby regulation index) to CSV.

The Table 1 page is an embedded bitmap; pdfplumber's text layer has the
header and footnote but no body. We render the page with pdfplumber, OCR
with tesseract, parse the rank/state/score triplets, normalise the
predictable OCR artifacts (i0 -> 10, il -> 11, Towa -> Iowa,
[Illinois -> Illinois, rank-comma -> rank-period), validate against the
canonical 47 = 50 - {Montana, South Dakota, Virginia}, and write:

  - data/compendium/opheim_1991_published_scores.csv (curated artifact)
  - docs/active/cogel-extraction/results/20260511_opheim_table1_ocr.txt
    (raw OCR provenance dump for the table page)

Usage: uv run scripts/opheim_1991_extract.py
"""
from __future__ import annotations

import csv
import re
from pathlib import Path

import pdfplumber
import pytesseract

PDF_PATH = Path("papers/Opheim_1991__state_lobby_regulation.pdf")
TABLE_PAGE_INDEX = 4  # pdfplumber says page 5 has TABLE 1
RENDER_DPI = 300

CSV_OUT = Path("data/compendium/opheim_1991_published_scores.csv")
OCR_PROVENANCE = Path(
    "docs/active/cogel-extraction/results/20260511_opheim_table1_ocr.txt"
)

# All 50 US states. Opheim excluded MT/SD/VA per the Table 1 footnote.
ALL_50 = {
    "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado",
    "Connecticut", "Delaware", "Florida", "Georgia", "Hawaii", "Idaho",
    "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky", "Louisiana",
    "Maine", "Maryland", "Massachusetts", "Michigan", "Minnesota",
    "Mississippi", "Missouri", "Montana", "Nebraska", "Nevada",
    "New Hampshire", "New Jersey", "New Mexico", "New York",
    "North Carolina", "North Dakota", "Ohio", "Oklahoma", "Oregon",
    "Pennsylvania", "Rhode Island", "South Carolina", "South Dakota",
    "Tennessee", "Texas", "Utah", "Vermont", "Virginia", "Washington",
    "West Virginia", "Wisconsin", "Wyoming",
}
OPHEIM_EXCLUDED = {"Montana", "South Dakota", "Virginia"}
EXPECTED_STATES = ALL_50 - OPHEIM_EXCLUDED  # 47

# OCR artifact normalisation. These are predictable misreads observed in
# the tesseract output on this specific bitmap; applied before parsing.
SCORE_FIXUPS = {"i0": "10", "il": "11"}
STATE_FIXUPS = {
    "Towa": "Iowa",
    "[Illinois": "Illinois",
}


def ocr_page() -> str:
    if not PDF_PATH.exists():
        raise SystemExit(f"PDF not found: {PDF_PATH}")
    with pdfplumber.open(PDF_PATH) as pdf:
        page = pdf.pages[TABLE_PAGE_INDEX]
        img = page.to_image(resolution=RENDER_DPI).original
    return pytesseract.image_to_string(img, config="--psm 6")


def normalise_text(text: str) -> str:
    """Apply OCR-artifact substitutions in a single pass."""
    fixed = text
    # State name fixes (replace whole words / specific bracket prefix)
    for wrong, right in STATE_FIXUPS.items():
        fixed = fixed.replace(wrong, right)
    # Rank punctuation: '34,' / '42,' -> '34.' / '42.'
    fixed = re.sub(r"(\d{1,2})\s*,(?=\s)", r"\1.", fixed)
    return fixed


def parse_rows(text: str) -> list[tuple[int, str, int]]:
    """Find all (rank, state, score) triplets in the OCR'd Table 1 text.

    Two columns per line (ranks 1-24 left, 25-47 right). We use a tolerant
    regex that finds rank-period followed by state words followed by a
    score token. Score tokens may be a plain digit string or the OCR
    artifacts 'i0' (=10) / 'il' (=11).
    """
    # Match: rank-period, then state (letters/spaces/dot), then a score
    # token (digits, 'i0', or 'il'). The state is non-greedy; the score
    # is bounded by digit-or-OCR-artifact tokens.
    pattern = re.compile(
        r"(\d{1,2})\.\s+([A-Z][A-Za-z .]+?)\s+(i0|il|\d{1,2})(?=\s|$)",
        re.MULTILINE,
    )
    rows: list[tuple[int, str, int]] = []
    for m in pattern.finditer(text):
        rank = int(m.group(1))
        state = m.group(2).strip()
        score_raw = m.group(3)
        score = int(SCORE_FIXUPS.get(score_raw, score_raw))
        rows.append((rank, state, score))
    return rows


def validate(rows: list[tuple[int, str, int]]) -> None:
    """Hard-assert the lift is internally consistent and matches the
    Opheim 47-state expectation."""
    if len(rows) != 47:
        raise AssertionError(f"Expected 47 rows, got {len(rows)}")

    ranks = sorted(r for r, _, _ in rows)
    if ranks != list(range(1, 48)):
        raise AssertionError(f"Ranks not 1..47: {ranks}")

    states = {s for _, s, _ in rows}
    if states != EXPECTED_STATES:
        missing = EXPECTED_STATES - states
        extra = states - EXPECTED_STATES
        raise AssertionError(f"State mismatch — missing={missing!r} extra={extra!r}")

    for rank, state, score in rows:
        if not (0 <= score <= 18):
            raise AssertionError(
                f"Score out of range 0..18: rank={rank} state={state!r} score={score}"
            )


def main() -> None:
    raw_ocr = ocr_page()
    normalised = normalise_text(raw_ocr)
    rows = parse_rows(normalised)
    validate(rows)

    # Sort by state name (alphabetical) for the CSV — stable for diffs.
    rows_by_state = sorted(rows, key=lambda r: r[1])

    CSV_OUT.parent.mkdir(parents=True, exist_ok=True)
    with CSV_OUT.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["state", "opheim_1991_score"])
        for _, state, score in rows_by_state:
            writer.writerow([state, score])

    OCR_PROVENANCE.parent.mkdir(parents=True, exist_ok=True)
    OCR_PROVENANCE.write_text(
        f"# Raw tesseract OCR output for Opheim 1991 Table 1\n"
        f"# Source: {PDF_PATH}, page index {TABLE_PAGE_INDEX} (1-indexed: 5)\n"
        f"# Render DPI: {RENDER_DPI}\n"
        f"# Generated by: scripts/opheim_1991_extract.py\n"
        f"# This file is the unnormalised OCR. The curated CSV is at\n"
        f"# {CSV_OUT}.\n\n"
        f"{raw_ocr}\n"
    )

    total = sum(s for _, _, s in rows)
    print(f"Parsed {len(rows)} rows ({len(states := {r[1] for r in rows})} states).")
    print(f"Score total = {total}, mean = {total/len(rows):.4f}")
    print(f"Top 3 (rank 1-3): {[r for r in rows if r[0] <= 3]}")
    print(f"Bottom 3 (rank 45-47): {[r for r in rows if r[0] >= 45]}")
    print(f"Wrote curated CSV: {CSV_OUT}")
    print(f"Wrote raw OCR provenance: {OCR_PROVENANCE}")


if __name__ == "__main__":
    main()
