"""COGEL Blue Book 1990 — table extraction from rotated scanned pages.

Each page (scan numbers 159-178; book pp. 149-168) holds part of one of
four wide tables — Table 28 (Definition/Registration/Prohibitions),
Table 29 (Reporting Requirements), Table 30 (Report Filing), Table 31
(Compliance Authority) — printed in landscape on a portrait page, so the
table reads naturally only after a 90 deg clockwise rotation.

The HathiTrust text layer overlaid on the scan captures most free-text
cells (column headers, jurisdiction names, "Annually", etc.) but drops
the asterisk and em-dash glyphs that encode most of the binary cell
content. We therefore re-OCR the rotated rendering with Tesseract,
which reliably picks up '*' and '-'/'—'.

Pipeline:
  1. pdfplumber renders the page at 300 DPI; PIL rotates 90 deg CW.
  2. pytesseract --psm 3 emits tokens with bbox + confidence.
  3. Rows are anchored on jurisdiction names (matched against a fixed
     state/territory list); multi-word names are stitched by horizontal
     proximity to a state-name word.
  4. Each non-jurisdiction token is assigned the nearest row by y-center.
  5. Output: a TSV of (page, row_jurisdiction, x, y, w, h, conf, text).

Column clustering is intentionally NOT done here — tables 28/29/30/31
each have a different schema, so column inference belongs in a follow-up
script that consumes this TSV.

Usage:
    uv run scripts/cogel_1990_extract.py PDF [PDF ...] [-o OUT.tsv]

Output: TSV to stdout, or to -o path. Rows append across multiple PDFs.
"""

# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "pdfplumber>=0.11",
#   "pytesseract>=0.3.10",
#   "Pillow>=10",
# ]
# ///

from __future__ import annotations

import argparse
import csv
import re
import sys
from dataclasses import dataclass
from pathlib import Path

import pdfplumber
import pytesseract
from PIL import Image

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from lobby_analysis.cogel.ocr_merge import merge_token_passes  # noqa: E402

RENDER_DPI = 300
TESSERACT_PSM = 3  # primary: auto layout — best asterisk recovery on probe
TESSERACT_PSM_SECONDARY = 6  # secondary uniform-block pass; recovers row bands
# that PSM 3 segments out (e.g., California/Florida on scan 169). Tokens
# from the two passes are merged by spatial proximity via
# `lobby_analysis.cogel.ocr_merge.merge_token_passes`.
# Rotation needed to bring the table into natural reading orientation.
# PIL.Image.rotate uses CCW positive, so 90 deg CW = -90.
ROTATE_DEG = -90

# Jurisdictions appearing across COGEL Blue Book 1990 lobbying tables.
# Single-token names plus a few multi-word ones whose second token is
# distinctive (we anchor on the second token and stitch "New"/"North"/
# "South"/"West"/"Rhode" prefixes back on by horizontal adjacency).
SINGLE_WORD_STATES = {
    "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado",
    "Connecticut", "Delaware", "Florida", "Georgia", "Hawaii", "Idaho",
    "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky", "Louisiana",
    "Maine", "Maryland", "Massachusetts", "Michigan", "Minnesota",
    "Mississippi", "Missouri", "Montana", "Nebraska", "Nevada", "Ohio",
    "Oklahoma", "Oregon", "Pennsylvania", "Tennessee", "Texas", "Utah",
    "Vermont", "Virginia", "Washington", "Wisconsin", "Wyoming",
    # Federal/non-state but listed in some tables:
    "Alberta", "Manitoba", "Newfoundland", "Ontario", "Quebec",
    "Saskatchewan",
}
# Known OCR substitutions for state names. Tesseract systematically
# misreads "I" as lowercase "l" on this corpus, and lowercases the leading
# capital on some scans (Alaska -> alaska, Louisiana -> louisiana).
# Keys are normalised tokens; values are the canonical name.
OCR_ALIASES = {
    "lowa": "Iowa",  # 'I' read as lowercase 'l'
    "lllinois": "Illinois",
    "lndiana": "Indiana",
    "ldaho": "Idaho",
}


def _norm(text: str) -> str:
    """Normalise a token for state-name matching: drop trailing footnote
    markers like '(d)' or '.', lowercase the rest. Empty string for tokens
    that are pure punctuation.
    """
    s = re.sub(r"\([a-z]+\)\.?$", "", text)  # strip (d), (l), (ss).
    s = s.rstrip(".,;:")
    return s.lower()


# Multi-word jurisdiction names. Matched ahead of SINGLE_WORD_STATES so
# "West Virginia" wins over a bare "Virginia" when "West" is adjacent.
MULTIWORD_NAMES = [
    "District of Columbia",  # 3-word — list before any 2-word name ending in "Columbia"
    "British Columbia",
    "New Hampshire",
    "New Jersey",
    "New Mexico",
    "New York",
    "North Carolina",
    "North Dakota",
    "South Carolina",
    "South Dakota",
    "Rhode Island",
    "West Virginia",
    "Nova Scotia",
    "New Brunswick",
]


@dataclass(frozen=True)
class Token:
    page: int
    x: int
    y: int
    w: int
    h: int
    conf: int
    text: str

    @property
    def cx(self) -> int:
        return self.x + self.w // 2

    @property
    def cy(self) -> int:
        return self.y + self.h // 2


def render_page(pdf_path: Path, page_index: int = 0) -> Image.Image:
    """Render one PDF page at RENDER_DPI and rotate to natural orientation."""
    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[page_index]
        img = page.to_image(resolution=RENDER_DPI).original
    return img.rotate(ROTATE_DEG, expand=True)


def ocr_tokens(img: Image.Image, page_id: int, psm: int = TESSERACT_PSM) -> list[Token]:
    """Run tesseract on a rotated page image and return Token records."""
    data = pytesseract.image_to_data(
        img,
        config=f"--psm {psm}",
        output_type=pytesseract.Output.DICT,
    )
    tokens: list[Token] = []
    for i in range(len(data["text"])):
        text = data["text"][i].strip()
        conf = int(data["conf"][i])
        if not text or conf < 0:
            continue
        tokens.append(
            Token(
                page=page_id,
                x=int(data["left"][i]),
                y=int(data["top"][i]),
                w=int(data["width"][i]),
                h=int(data["height"][i]),
                conf=conf,
                text=text,
            )
        )
    return tokens


def _adjacent(prev: Token, cur: Token) -> bool:
    """True if `prev` sits immediately to the left of, or stacked just above,
    `cur` — the two arrangements that occur for prefix words in this corpus.
    """
    dx = cur.x - prev.x
    dy = cur.y - prev.y
    same_row_left = (-15 <= (cur.cy - prev.cy) <= 15) and (0 < dx < 300)
    stacked_above = (0 < dy < 90) and (abs(cur.x - prev.x) < 60)
    return same_row_left or stacked_above


def _matches_name(token_text: str, name: str) -> bool:
    """Token text matches a single canonical state-name word, accounting for
    case, footnote suffixes, and known OCR aliases."""
    n = _norm(token_text)
    return n == name.lower() or OCR_ALIASES.get(n) == name


def _walk_prefix(tail: Token, prefix_words: list[str], tokens: list[Token]) -> Token | None:
    """Walk a chain of prefix words backward from `tail`. Each prefix word must
    be adjacent (left or above) the next. Returns the head Token if the full
    chain matches, else None.
    """
    cur = tail
    for word in reversed(prefix_words):
        cands = [t for t in tokens if _matches_name(t.text, word) and _adjacent(t, cur)]
        if not cands:
            return None
        # Nearest neighbour wins.
        cur = min(cands, key=lambda t: (cur.x - t.x) ** 2 + (cur.y - t.y) ** 2)
    return cur


def find_jurisdiction_anchors(tokens: list[Token]) -> list[tuple[Token, str]]:
    """Locate jurisdiction tokens, matching multi-word names ahead of single.

    Returns (last-word-token, full_name) pairs sorted top-to-bottom. Tokens
    consumed by a multi-word match are not re-matched as bare single-word
    states (e.g. the "Virginia" in "West Virginia" won't show up as bare
    "Virginia" too).
    """
    anchors: list[tuple[Token, str]] = []
    consumed: set[Token] = set()

    # Multi-word names first; longest names processed first within each pass.
    for name in sorted(MULTIWORD_NAMES, key=lambda n: -len(n.split())):
        words = name.split()
        for tail in tokens:
            if not _matches_name(tail.text, words[-1]) or tail in consumed:
                continue
            head = _walk_prefix(tail, words[:-1], tokens)
            if head is None:
                continue
            anchors.append((tail, name))
            consumed.add(tail)

    # Single-word states fill in the rest.
    single_word_lookup = {s.lower(): s for s in SINGLE_WORD_STATES}
    for tok in tokens:
        if tok in consumed:
            continue
        n = _norm(tok.text)
        canonical = single_word_lookup.get(n) or OCR_ALIASES.get(n)
        if canonical and canonical in SINGLE_WORD_STATES:
            anchors.append((tok, canonical))

    # Filter footnote-prose false positives. Two signals:
    #
    #  (1) A footnote-prose anchor is immediately preceded by a footnote
    #      key like "(a)", "(jj)" — a token matching ^\([a-z]+\)$ within
    #      ~150 px to the left, at similar y. Real table rows don't have
    #      that pattern; the state name is the leftmost substantive token.
    #
    #  (2) Real anchors cluster in a narrow x-band (the row-label column).
    #      Prose-mention anchors are scattered across various x's.
    # Footnote keys like "(a)", "(jj)". Tesseract often reads lowercase 'l'
    # as uppercase 'I' or as digit '1'; closing ')' as '}' or ']'. Allow
    # any short alphanumeric / pipe payload between opening '(' and a
    # closing bracket-like char.
    footnote_key_re = re.compile(r"^\([A-Za-z0-9|/]{1,4}[)\]}]\.?$")

    def has_footnote_key_to_left(anchor: Token) -> bool:
        for t in tokens:
            if t.conf < 40:
                continue
            if not footnote_key_re.match(t.text):
                continue
            if abs(t.cy - anchor.cy) > 25:
                continue
            if t.x < anchor.x:  # anywhere to the left in the same row
                return True
        return False

    anchors = [a for a in anchors if not has_footnote_key_to_left(a[0])]

    if len(anchors) >= 2:
        xs = [a[0].x for a in anchors]
        clustered: list[tuple[Token, str]] = []
        for a in anchors:
            nearby = sum(1 for x in xs if abs(x - a[0].x) <= 150)
            if nearby >= 2:
                clustered.append(a)
        anchors = clustered
    else:
        # A single anchor on a page is almost always spurious.
        anchors = []

    # Sort top-to-bottom, dedupe by name (first occurrence wins).
    anchors.sort(key=lambda p: p[0].cy)
    seen_names: set[str] = set()
    deduped: list[tuple[Token, str]] = []
    for tok, name in anchors:
        if name in seen_names:
            continue
        seen_names.add(name)
        deduped.append((tok, name))
    return deduped


def assign_rows(
    tokens: list[Token], anchors: list[tuple[Token, str]]
) -> dict[Token, str]:
    """Assign each non-jurisdiction token to its nearest jurisdiction by y.

    Each row's y-band runs from the midpoint to the previous anchor up to
    the midpoint to the next anchor. The topmost row extends *upward* by
    half the inter-row gap, because asterisk and dash glyphs sit a fair
    distance above the letter baseline of the jurisdiction label and would
    otherwise be misclassified as header. Same logic mirrored for the
    bottom row.
    """
    if not anchors:
        return {t: "_unknown" for t in tokens}

    anchor_ys = [a[0].cy for a in anchors]
    anchor_names = [a[1] for a in anchors]
    n = len(anchor_ys)

    # Median inter-row gap; falls back to a reasonable default if there's
    # only one anchor on the page.
    if n >= 2:
        gaps = [anchor_ys[i + 1] - anchor_ys[i] for i in range(n - 1)]
        gaps.sort()
        median_gap = gaps[len(gaps) // 2]
    else:
        median_gap = 120  # ~one row at 300 DPI on this corpus

    midpoints = [
        (anchor_ys[i] + anchor_ys[i + 1]) // 2 for i in range(n - 1)
    ]
    upper_bound = anchor_ys[0] - median_gap // 2
    lower_bound = anchor_ys[-1] + median_gap // 2

    assignments: dict[Token, str] = {}
    anchor_token_set = {a[0] for a in anchors}
    for t in tokens:
        if t in anchor_token_set:
            for a_tok, a_name in anchors:
                if a_tok is t:
                    assignments[t] = a_name
                    break
            continue
        if t.cy < upper_bound:
            assignments[t] = "_header"
            continue
        if t.cy > lower_bound:
            assignments[t] = "_footer"
            continue
        idx = 0
        for i, mp in enumerate(midpoints):
            if t.cy < mp:
                idx = i
                break
        else:
            idx = n - 1
        assignments[t] = anchor_names[idx]
    return assignments


def extract_pdf(pdf_path: Path, page_id: int) -> list[dict]:
    """Process one PDF and yield TSV-shaped row dicts.

    Runs tesseract twice (PSM 3 primary, PSM 6 secondary) and merges the
    token streams by spatial proximity. PSM 3 has the higher asterisk
    recall but on some scans segments specific row bands out (e.g., the
    California and Florida rows on scan 169); PSM 6 reads those bands.
    """
    img = render_page(pdf_path)
    primary = ocr_tokens(img, page_id, psm=TESSERACT_PSM)
    secondary = ocr_tokens(img, page_id, psm=TESSERACT_PSM_SECONDARY)
    tokens = merge_token_passes(primary, secondary)
    anchors = find_jurisdiction_anchors(tokens)
    row_for = assign_rows(tokens, anchors)
    rows = []
    for t in tokens:
        rows.append(
            {
                "scan_page": page_id,
                "row": row_for[t],
                "x": t.x,
                "y": t.y,
                "w": t.w,
                "h": t.h,
                "conf": t.conf,
                "text": t.text,
            }
        )
    return rows


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("pdfs", nargs="+", type=Path, help="Input PDF page(s).")
    ap.add_argument(
        "-o", "--out", type=Path, default=None,
        help="Output TSV path (default: stdout).",
    )
    ap.add_argument(
        "--summary", action="store_true",
        help="Print per-page summary to stderr.",
    )
    args = ap.parse_args()

    all_rows: list[dict] = []
    for pdf_path in args.pdfs:
        # Scan-page id from filename: ...-<scan_id>-<random>.pdf
        try:
            scan_id = int(pdf_path.stem.split("-")[-2])
        except (ValueError, IndexError):
            scan_id = 0
        rows = extract_pdf(pdf_path, scan_id)
        if args.summary:
            anchors = sorted({r["row"] for r in rows if not r["row"].startswith("_")})
            n_ast = sum(1 for r in rows if r["text"] == "*")
            n_dash = sum(1 for r in rows if r["text"] in ("-", "—", "--"))
            print(
                f"  scan {scan_id}: {len(rows)} tokens, {len(anchors)} jurisdictions"
                f" ({', '.join(anchors)}), {n_ast} '*' tokens, {n_dash} '-' tokens",
                file=sys.stderr,
            )
        all_rows.extend(rows)

    fieldnames = ["scan_page", "row", "x", "y", "w", "h", "conf", "text"]
    out_stream = sys.stdout if args.out is None else open(args.out, "w", newline="")
    try:
        writer = csv.DictWriter(out_stream, fieldnames=fieldnames, delimiter="\t")
        writer.writeheader()
        writer.writerows(all_rows)
    finally:
        if args.out is not None:
            out_stream.close()

    return 0


if __name__ == "__main__":
    sys.exit(main())
