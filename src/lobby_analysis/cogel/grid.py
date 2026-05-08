"""Column clustering and per-table CSV emission for COGEL Blue Book 1990.

Consumes the v1 token TSV emitted by `scripts/cogel_1990_extract.py` and
projects each (scan, jurisdiction) row's tokens onto the canonical column
schema for that scan's parent table (`schemas.py`).

Column boundaries are derived from data-row tokens via 1-D agglomerative
clustering on x. Per-page sub-column header text was empirically
unreadable by tesseract on this corpus (the headers face the opposite
rotation axis from the body text and OCR as letter-fragment garbage),
so we rely on the dense cell-marker tokens (`*`, `—`, `-`, `_`) plus
high-confidence free-text tokens to surface column structure.

Pipeline per (scan, table):

  1. Filter tokens to the scan's data rows (jurisdiction-tagged), drop
     state-name tokens themselves (they're the row label), drop low-conf
     non-marker tokens.
  2. Cluster remaining x-centroids 1-D agglomeratively. Tune the gap
     threshold until the cluster count matches the schema column count;
     emit a warning if no threshold gives an exact match.
  3. Boundaries = midpoints between adjacent cluster centroids (outer
     edges extend to the page bounds).
  4. For each jurisdiction in the scan, bucket its tokens into cells by
     x and apply `normalise_cell` per the column's `value_kind`.
"""

from __future__ import annotations

import csv
import re
from collections.abc import Iterable, Iterator
from dataclasses import dataclass, field
from pathlib import Path

from .schemas import Column, Table, ValueKind, table_for_scan


# Tokens we treat as cell markers regardless of confidence. Asterisks +
# dash variants we observed in the v1 TSV: hyphen, em-dash, double hyphen,
# underscore (a known tesseract substitution for a thin em-dash).
MARKER_TEXTS = frozenset({"*"})
DASH_TEXTS = frozenset({"-", "—", "--", "_", "–"})  # last is en-dash
ALL_MARKERS = MARKER_TEXTS | DASH_TEXTS

# Confidence threshold for non-marker tokens. Marker glyphs OCR at low
# confidence often (single char, narrow bbox), so we exempt them.
FREE_TEXT_CONF_THRESHOLD = 40

# Trailing footnote-letter suffix on cell text: "(k)", "(aa)", "(ss)".
_FOOTNOTE_SUFFIX_RE = re.compile(r"\(([a-zA-Z]{1,3})\)$")
# Hyphen-joined OCR artifact in free-text: "3-reports" -> "3 reports".
_HYPHEN_DIGIT_WORD_RE = re.compile(r"\b(\d+)-(\w)")


@dataclass(frozen=True)
class GridToken:
    scan_page: int
    row: str
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

    @property
    def is_marker(self) -> bool:
        return self.text in ALL_MARKERS


@dataclass(frozen=True)
class CellValue:
    value: str = ""
    raw_text: str = ""
    footnote: str = ""
    numeric_value: float | None = None
    flags: tuple[str, ...] = ()


# ---------------------------------------------------------------------------
# TSV loading
# ---------------------------------------------------------------------------

def load_tokens(tsv_path: Path) -> Iterator[GridToken]:
    """Stream GridToken records from a v1 token TSV."""
    with open(tsv_path, newline="") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for r in reader:
            yield GridToken(
                scan_page=int(r["scan_page"]),
                row=r["row"],
                x=int(r["x"]),
                y=int(r["y"]),
                w=int(r["w"]),
                h=int(r["h"]),
                conf=int(r["conf"]),
                text=r["text"],
            )


# ---------------------------------------------------------------------------
# Cell normalisation
# ---------------------------------------------------------------------------

def _strip_footnote(text: str) -> tuple[str, str]:
    """Strip *all* trailing footnote-letter suffixes; return (clean, csv_letters)."""
    letters: list[str] = []
    cur = text
    while True:
        m = _FOOTNOTE_SUFFIX_RE.search(cur)
        if m is None:
            break
        letters.append(m.group(1))
        cur = cur[: m.start()].rstrip()
    return cur, ",".join(reversed(letters))


def normalise_cell(tokens: list[GridToken], value_kind: ValueKind) -> CellValue:
    """Map a list of tokens (already bucketed into one cell) to one CellValue."""
    if value_kind == "marker":
        return _normalise_marker(tokens)
    if value_kind == "currency":
        return _normalise_currency(tokens)
    if value_kind == "frequency":
        return _normalise_frequency(tokens)
    return _normalise_free_text(tokens)


def _normalise_marker(tokens: list[GridToken]) -> CellValue:
    if not tokens:
        return CellValue(value="", raw_text="")
    texts = {t.text for t in tokens}
    raw = " ".join(t.text for t in sorted(tokens, key=lambda t: t.x))
    if texts & MARKER_TEXTS:
        return CellValue(value="*", raw_text=raw)
    if texts & DASH_TEXTS:
        return CellValue(value="—", raw_text=raw)
    # Tokens are present but none look like markers — flag for review but
    # surface the raw text so it isn't silently dropped.
    return CellValue(
        value=tokens[0].text,
        raw_text=raw,
        flags=("unknown_marker",),
    )


def _filter_low_conf(tokens: list[GridToken]) -> list[GridToken]:
    """Keep markers, high-conf tokens, and digit-bearing tokens.

    Digit-bearing low-conf tokens like `"3-reports"` (conf=29 from the v1
    Missouri row) are real data — tesseract OCRs unusual hyphenations at
    moderate confidence — and we must not drop them.
    """
    out: list[GridToken] = []
    for t in tokens:
        if t.is_marker:
            out.append(t)
        elif t.conf >= FREE_TEXT_CONF_THRESHOLD:
            out.append(t)
        elif any(ch.isdigit() for ch in t.text):
            out.append(t)
    return out


# Tokens with `cy` within this many pixels are treated as the same printed
# line for free-text reading-order reconstruction (multi-line cells like
# "3 times a year" stacked across two physical lines).
_LINE_GROUP_PX = 30


def _normalise_free_text(tokens: list[GridToken]) -> CellValue:
    kept = _filter_low_conf(tokens)
    if not kept:
        return CellValue(value="", raw_text=" ".join(t.text for t in tokens))
    # Sort by (line, x): primary key groups tokens onto printed lines via
    # cy bucket; secondary key gives left-to-right reading order within
    # each line.
    kept.sort(key=lambda t: (t.cy // _LINE_GROUP_PX, t.x))
    raw = " ".join(t.text for t in kept)
    text = _HYPHEN_DIGIT_WORD_RE.sub(r"\1 \2", raw)
    text = re.sub(r"\s+", " ", text).strip()
    text, footnote = _strip_footnote(text)
    return CellValue(value=text, raw_text=raw, footnote=footnote)


_FREQ_CANONICAL = {
    "annual", "annually", "biennial", "biennially",
    "quarterly", "monthly", "semiannual", "semiannually",
    "permanent",
}


def _normalise_frequency(tokens: list[GridToken]) -> CellValue:
    cell = _normalise_free_text(tokens)
    base = re.sub(r"[^a-z]", "", cell.value.lower())
    if base in _FREQ_CANONICAL:
        return CellValue(
            value=cell.value.strip(),
            raw_text=cell.raw_text,
            footnote=cell.footnote,
        )
    return cell


_CURRENCY_RE = re.compile(r"\$?([\d,]+(?:\.\d+)?)")


def _normalise_currency(tokens: list[GridToken]) -> CellValue:
    cell = _normalise_free_text(tokens)
    if not cell.value:
        return cell
    m = _CURRENCY_RE.search(cell.value)
    if m is None:
        return cell
    try:
        numeric = float(m.group(1).replace(",", ""))
    except ValueError:
        numeric = None
    return CellValue(
        value=cell.value,
        raw_text=cell.raw_text,
        footnote=cell.footnote,
        numeric_value=numeric,
    )


# ---------------------------------------------------------------------------
# Column-boundary detection
# ---------------------------------------------------------------------------

def midpoint_boundaries(centroids: list[float]) -> list[float]:
    """Midpoints between adjacent centroids, in same order."""
    return [
        (centroids[i] + centroids[i + 1]) / 2
        for i in range(len(centroids) - 1)
    ]


def cell_index_for_x(x: float, boundaries: list[float]) -> int:
    """Return the cell index for a token at x given inter-cell boundaries."""
    for i, b in enumerate(boundaries):
        if x < b:
            return i
    return len(boundaries)


def cluster_x(xs: Iterable[float], gap_threshold: float) -> list[list[float]]:
    """1-D agglomerative clustering by gap between adjacent sorted values."""
    sorted_xs = sorted(xs)
    if not sorted_xs:
        return []
    clusters: list[list[float]] = [[sorted_xs[0]]]
    for x in sorted_xs[1:]:
        if x - clusters[-1][-1] <= gap_threshold:
            clusters[-1].append(x)
        else:
            clusters.append([x])
    return clusters


def _centroid(cluster: list[float]) -> float:
    return sum(cluster) / len(cluster)


def boundaries_from_markers(
    tokens: list[GridToken], table: Table,
) -> tuple[list[float], list[dict]]:
    """Cluster marker tokens by x; emit warnings if cluster count != schema."""
    xs = [t.cx for t in tokens if t.is_marker]
    warnings: list[dict] = []
    if not xs:
        warnings.append({"flag": "no_markers_on_page", "table": table.table_number})
        return [], warnings

    clusters = cluster_x(xs, gap_threshold=40)
    centroids = [_centroid(c) for c in clusters]
    if len(centroids) != table.column_count:
        warnings.append({
            "flag": "column_count_mismatch",
            "table": table.table_number,
            "expected": table.column_count,
            "actual": len(centroids),
        })
    return midpoint_boundaries(centroids), warnings


def _detect_boundaries_for_scan(
    scan_tokens: list[GridToken], table: Table,
) -> tuple[list[float], dict]:
    """Resolve column boundaries: hand-curated schema field if present, else
    auto-cluster marker tokens and interpolate.
    """
    if table.boundaries:
        return list(table.boundaries), {}

    # Auto-clustering fallback. Use only marker tokens (most reliable signal)
    # and require ≥ 2 contributing rows per cluster to suppress page-margin
    # OCR garbage.
    markers = [
        t for t in scan_tokens
        if t.is_marker and not t.row.startswith("_") and not _is_state_name_token(t)
    ]
    if not markers:
        return [], {
            "flag": "no_markers_on_scan",
            "scan_page": scan_tokens[0].scan_page if scan_tokens else None,
            "table": table.table_number,
        }

    xs = [m.cx for m in markers]
    target = table.column_count

    best_clusters: list[list[float]] | None = None
    best_threshold: float | None = None
    for gap in range(15, 121, 5):
        clusters = cluster_x(xs, gap_threshold=gap)
        # Drop low-density clusters (likely OCR garbage at page margins).
        dense = []
        for c in clusters:
            rows = {m.row for m in markers if m.cx in c}
            if len(rows) >= 2:
                dense.append(c)
        if len(dense) == target:
            best_clusters = dense
            best_threshold = gap
            break
        if (best_clusters is None
                or abs(len(dense) - target) < abs(len(best_clusters) - target)):
            best_clusters = dense
            best_threshold = gap

    assert best_clusters is not None
    centroids = [_centroid(c) for c in best_clusters]
    boundaries = midpoint_boundaries(centroids)
    warning: dict = {}
    if len(centroids) != target:
        warning = {
            "flag": "column_count_mismatch",
            "scan_page": scan_tokens[0].scan_page if scan_tokens else None,
            "table": table.table_number,
            "expected": target,
            "actual": len(centroids),
            "best_gap_threshold": best_threshold,
        }
    return boundaries, warning


def _is_state_name_token(token: GridToken) -> bool:
    """True if the token's text is a word in its row name (i.e., the row label).

    These tokens are stitched-on by the v1 anchor logic and should not be
    bucketed into data cells.
    """
    if token.row.startswith("_"):
        return False
    row_words = {_norm(w) for w in token.row.split()}
    return _norm(token.text) in row_words


def _norm(text: str) -> str:
    """Lowercase + strip footnote/punctuation, mirroring v1 extractor."""
    s = re.sub(r"\([a-z]+\)\.?$", "", text)
    s = s.rstrip(".,;:")
    return s.lower()


# ---------------------------------------------------------------------------
# Per-table projection
# ---------------------------------------------------------------------------

def project_table(
    tsv_path: Path, table: Table,
) -> tuple[list[dict], list[dict]]:
    """Emit per-jurisdiction CSV rows + warnings for one Blue Book table."""
    all_tokens = list(load_tokens(tsv_path))
    by_scan: dict[int, list[GridToken]] = {}
    for t in all_tokens:
        by_scan.setdefault(t.scan_page, []).append(t)

    rows: list[dict] = []
    warnings: list[dict] = []

    for scan_page in sorted(by_scan):
        if table_for_scan(scan_page) is not table:
            continue
        scan_tokens = by_scan[scan_page]
        boundaries, warn = _detect_boundaries_for_scan(scan_tokens, table)
        if warn:
            warnings.append(warn)
        if not boundaries:
            continue

        # Group jurisdiction tokens. Drop vertical-text OCR garbage (tall-
        # narrow bbox) and low-confidence non-marker tokens here too — the
        # boundary detection already filtered these for clustering, but the
        # bucketing pass needs the same filter so they don't leak into cells.
        by_juris: dict[str, list[GridToken]] = {}
        for t in scan_tokens:
            if t.row.startswith("_"):
                continue
            if _is_state_name_token(t):
                continue
            if t.h > 2 * max(t.w, 30):
                continue
            if t.conf < 25 and not t.is_marker:
                continue
            by_juris.setdefault(t.row, []).append(t)

        for juris in sorted(by_juris):
            cells = _project_one_row(by_juris[juris], boundaries, table)
            row: dict = {
                "_scan_page": scan_page,
                "jurisdiction": juris,
            }
            footnotes_combined: list[str] = []
            for col, cell in zip(table.columns, cells):
                row[col.key] = cell.value
                if cell.numeric_value is not None:
                    row[f"{col.key}_numeric"] = cell.numeric_value
                if cell.footnote:
                    footnotes_combined.append(f"{col.key}={cell.footnote}")
                for f in cell.flags:
                    warnings.append({
                        "flag": f,
                        "scan_page": scan_page,
                        "table": table.table_number,
                        "jurisdiction": juris,
                        "column": col.key,
                        "raw": cell.raw_text,
                    })
            row["_footnotes"] = "; ".join(footnotes_combined)
            rows.append(row)

    return rows, warnings


def _project_one_row(
    tokens: list[GridToken], boundaries: list[float], table: Table,
) -> list[CellValue]:
    """Bucket a row's tokens into cells, then normalise each cell."""
    n_cells = len(boundaries) + 1
    buckets: list[list[GridToken]] = [[] for _ in range(n_cells)]
    for t in tokens:
        idx = cell_index_for_x(t.cx, boundaries)
        if idx >= n_cells:
            idx = n_cells - 1
        buckets[idx].append(t)

    # If we landed with a different cell count than the schema, pad/trim.
    cells: list[CellValue] = []
    for i, col in enumerate(table.columns):
        bucket = buckets[i] if i < len(buckets) else []
        cells.append(normalise_cell(bucket, col.value_kind))
    return cells


__all__ = [
    "GridToken",
    "CellValue",
    "load_tokens",
    "normalise_cell",
    "midpoint_boundaries",
    "cell_index_for_x",
    "cluster_x",
    "boundaries_from_markers",
    "project_table",
]
