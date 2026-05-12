#!/usr/bin/env python
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "pdfplumber>=0.11",
#     "pytesseract>=0.3",
#     "Pillow>=10",
# ]
# ///
"""Crop the CA/FL row bands on scan 169 and re-OCR with multiple PSMs.

Goal: distinguish (a) OCR missed dashes that are actually in the bitmap
vs (b) the bitmap genuinely has empty rows for CA/FL in COGEL 1990 T30.

The state labels on scan 169 are at:
  Arkansas y=1155  → cy=1169
  California y=1196 → cy=1211  (CA row band cy ∈ [1190, 1249])
  Colorado y=1271 → cy=1286
  ...
  Delaware y=1354 → cy=1369
  Florida y=1396 → cy=1411  (FL row band cy ∈ [1390, 1434])
  Georgia y=1439 → cy=1457

We crop scan 169 at y=1160-1280 (covers CA band + a bit above/below) and
y=1370-1460 (covers FL band + a bit above/below). Output PNGs to /tmp/
and re-OCR each crop with PSM 3, 6, 11, 12.

Usage: uv run scripts/inspect_scan169_ca_fl.py
"""
from __future__ import annotations

from pathlib import Path

import pdfplumber
import pytesseract

PDF_PATH = Path("COGEL_BlueBook_1990/mdp-39015077214750-169-1777852490.pdf")
RENDER_DPI = 300
ROTATE_DEG = -90  # CW rotation matches v1 extractor

CROPS = {
    "ca_band": (0, 1160, None, 1280),  # full-width, y=1160..1280
    "fl_band": (0, 1370, None, 1460),
}
OUTDIR = Path("/tmp/cogel_inspect")


def main() -> None:
    if not PDF_PATH.exists():
        raise SystemExit(f"PDF not found: {PDF_PATH}")
    OUTDIR.mkdir(exist_ok=True)

    with pdfplumber.open(PDF_PATH) as pdf:
        page = pdf.pages[0]
        img = page.to_image(resolution=RENDER_DPI).original
    img_rot = img.rotate(ROTATE_DEG, expand=True)
    print(f"Rotated image size: {img_rot.size}")

    for name, (x0, y0, x1, y1) in CROPS.items():
        x1 = x1 or img_rot.size[0]
        crop = img_rot.crop((x0, y0, x1, y1))
        out = OUTDIR / f"scan169_{name}.png"
        crop.save(out)
        print(f"\n{'=' * 60}\n--- Crop {name}: {crop.size} -> {out} ---\n{'=' * 60}")

        for psm in [3, 6, 11, 12]:
            text = pytesseract.image_to_string(crop, config=f"--psm {psm}")
            non_empty = "\n".join(line for line in text.splitlines() if line.strip())
            print(f"\n--- psm {psm} ---")
            print(non_empty if non_empty else "(empty)")


if __name__ == "__main__":
    main()
