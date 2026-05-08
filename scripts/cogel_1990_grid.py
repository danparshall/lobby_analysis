"""COGEL Blue Book 1990 — per-table CSV emission from the v1 token TSV.

Pipeline driver wrapping `lobby_analysis.cogel.grid.project_table` with a
CLI. Two input modes:

  1. Default — read a previously-emitted v1 token TSV (fastest, deterministic).
  2. `--from-pdfs` — re-OCR a list of PDF pages with the v1 extractor first,
     then run the projection. Useful when iterating on the OCR settings or
     processing newly-added pages.

Outputs (per `--out-dir`):

  - cogel_1990_table28.csv  ... cogel_1990_table31.csv  (one row per jurisdiction)
  - cogel_1990_grid_warnings.tsv  (cells the projection flagged for review)

Usage:
    uv run scripts/cogel_1990_grid.py
    uv run scripts/cogel_1990_grid.py --tsv path/to/v1_tokens.tsv
    uv run scripts/cogel_1990_grid.py --from-pdfs COGEL_BlueBook_1990/*.pdf
    uv run scripts/cogel_1990_grid.py --out-dir docs/active/cogel-extraction/results
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
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from lobby_analysis.cogel import grid, schemas  # noqa: E402


DEFAULT_TSV = REPO_ROOT / "docs" / "active" / "cogel-extraction" / "results" / "20260505_v1_tokens.tsv"
DEFAULT_OUT_DIR = REPO_ROOT / "docs" / "active" / "cogel-extraction" / "results"


def regenerate_tsv_from_pdfs(pdfs: list[Path], dest_tsv: Path) -> Path:
    """Invoke the v1 extractor on `pdfs` to produce a fresh token TSV."""
    extractor = REPO_ROOT / "scripts" / "cogel_1990_extract.py"
    cmd = ["uv", "run", str(extractor), *(str(p) for p in pdfs), "-o", str(dest_tsv)]
    print(f"  $ {' '.join(cmd)}", file=sys.stderr)
    subprocess.run(cmd, check=True)
    return dest_tsv


def write_table_csv(rows: list[dict], table: schemas.Table, out_path: Path) -> None:
    """Write per-jurisdiction rows for one table to a CSV file."""
    base_keys = ["jurisdiction"] + list(table.keys)
    numeric_keys = [
        f"{c.key}_numeric" for c in table.columns
        if c.value_kind in ("currency",)
    ]
    fieldnames = base_keys + numeric_keys + ["_footnotes", "_scan_page"]

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            # Backfill missing keys so each CSV line is uniform.
            for k in fieldnames:
                row.setdefault(k, "")
            writer.writerow({k: row.get(k, "") for k in fieldnames})


def write_warnings_tsv(warnings: list[dict], out_path: Path) -> None:
    if not warnings:
        # Still emit a header-only file so downstream readers can rely on
        # its existence.
        warnings = []
    fieldnames = sorted({k for w in warnings for k in w.keys()}) or [
        "flag", "scan_page", "table", "jurisdiction", "column", "raw",
    ]
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter="\t")
        writer.writeheader()
        for w in warnings:
            writer.writerow({k: w.get(k, "") for k in fieldnames})


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument(
        "--tsv", type=Path, default=DEFAULT_TSV,
        help=f"Input v1 token TSV (default: {DEFAULT_TSV.relative_to(REPO_ROOT)}).",
    )
    ap.add_argument(
        "--from-pdfs", type=Path, nargs="+", default=None,
        help="Regenerate v1 tokens by re-OCRing the listed PDFs first.",
    )
    ap.add_argument(
        "--out-dir", type=Path, default=DEFAULT_OUT_DIR,
        help=f"Output directory (default: {DEFAULT_OUT_DIR.relative_to(REPO_ROOT)}).",
    )
    args = ap.parse_args()

    if args.from_pdfs:
        with tempfile.NamedTemporaryFile(
            "w", suffix=".tsv", delete=False, dir=args.out_dir,
        ) as tmp:
            tsv_path = Path(tmp.name)
        regenerate_tsv_from_pdfs(args.from_pdfs, tsv_path)
    else:
        tsv_path = args.tsv

    if not tsv_path.exists():
        print(f"error: TSV not found at {tsv_path}", file=sys.stderr)
        return 1

    all_warnings: list[dict] = []
    summary_lines: list[str] = []
    for table in schemas.ALL_TABLES:
        rows, warnings = grid.project_table(tsv_path, table)
        all_warnings.extend(warnings)

        out_csv = args.out_dir / f"cogel_1990_table{table.table_number}.csv"
        write_table_csv(rows, table, out_csv)

        n_markers = sum(
            1 for r in rows for col in table.columns
            if col.value_kind == "marker" and r.get(col.key) in ("*", "—")
        )
        summary_lines.append(
            f"  Table {table.table_number}: {len(rows):3d} jurisdictions, "
            f"{n_markers:4d} marker cells -> {out_csv.relative_to(REPO_ROOT)}"
        )

    warnings_tsv = args.out_dir / "cogel_1990_grid_warnings.tsv"
    write_warnings_tsv(all_warnings, warnings_tsv)
    summary_lines.append(
        f"  Warnings: {len(all_warnings)} entries -> {warnings_tsv.relative_to(REPO_ROOT)}"
    )

    print("v2 grid emission complete.")
    print(f"  Source TSV: {tsv_path.relative_to(REPO_ROOT)}")
    for line in summary_lines:
        print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
