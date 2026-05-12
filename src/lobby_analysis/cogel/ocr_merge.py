"""Merge two OCR-token passes by spatial proximity.

The COGEL Blue Book 1990 v1 extractor runs tesseract twice on each rotated
page: PSM 3 (auto layout) as primary and PSM 6 (uniform block) as
secondary. PSM 3 has the higher asterisk recall across the corpus, but on
scan 169 its segmentation drops the California and Florida row bands of
Table 30. PSM 6 reads those rows. Merging by spatial proximity preserves
the PSM-3 primary output and adds PSM-6 tokens that fall in positions
where the primary pass found nothing.

Proximity uses Chebyshev distance on bbox centers (max of |dx|, |dy|).
A secondary token is treated as a duplicate of a primary token when both
center coordinates are within `radius` pixels. Default radius is 15, set
just above the half-width of the smallest in-corpus marker glyph (~13 px)
so that PSM-3 / PSM-6 readings of the same physical asterisk dedupe but
adjacent dashes in a row of dashes do not.
"""
from __future__ import annotations

from typing import Protocol, Sequence, TypeVar


class TokenLike(Protocol):
    """Anything with an integer-bbox `x`, `y`, `w`, `h`."""

    x: int
    y: int
    w: int
    h: int


T = TypeVar("T", bound=TokenLike)

DEFAULT_MERGE_RADIUS = 15


def merge_token_passes(
    primary: Sequence[T],
    secondary: Sequence[T],
    radius: int = DEFAULT_MERGE_RADIUS,
) -> list[T]:
    """Return primary tokens plus any secondary tokens not co-located.

    Co-located = bbox-center Chebyshev distance ≤ `radius` to any primary
    token. Primary order is preserved; new secondary tokens are appended
    in their input order. Inputs are not mutated.
    """
    merged: list[T] = list(primary)
    primary_centers = [(t.x + t.w // 2, t.y + t.h // 2) for t in primary]
    for s in secondary:
        sx = s.x + s.w // 2
        sy = s.y + s.h // 2
        if any(
            abs(sx - px) <= radius and abs(sy - py) <= radius
            for px, py in primary_centers
        ):
            continue
        merged.append(s)
    return merged
