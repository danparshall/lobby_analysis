#!/usr/bin/env python3
"""3-way × 3-run consensus grouping over the 9 subagent CSVs.

Inputs (9 files, uniform schema):
  results/3way_consensus/m1_cluster_anchored_run{1,2,3}.csv
  results/3way_consensus/m2_blind_run{1,2,3}.csv
  results/3way_consensus/m3_focal_anchored_run{1,2,3}.csv
  Each has columns: source_paper, source_id, source_text, group_id, group_label

Outputs (results/3way_consensus/):
  consensus_summary.csv       — one row per item-pair with agreement counts
  consensus_clusters_strict.csv — transitive closure of pairs with strength ≥ STRICT_THRESHOLD
  consensus_clusters_loose.csv  — transitive closure of pairs with strength ≥ LOOSE_THRESHOLD
  consensus_human_review.csv  — pairs in the 3..5/9 disagreement band
  method_instability_report.md — within-method instability per method, plus
                                  between-method disagreement summary

Two distinct stability metrics are produced (per user direction):
  1. Within-method instability (per method, per pair):
     - For method M with 3 runs, the per-pair "agreement among M's 3 runs"
       takes values in {0, 1, 2, 3}.
     - A pair is INSTABLE within M if that count is in {1, 2} (the 3 runs of
       M disagree about whether the pair is co-grouped). Stable means
       all-3-yes (3) or all-3-no (0).
     - The method-instability rate = fraction of pairs that are instable
       within that method.
  2. Between-method disagreement (cross-method):
     - For each pair, compare the per-method counts (m1_count, m2_count,
       m3_count). The cross-method spread = max - min over the three.
     - A pair is BETWEEN-DISAGREEMENT if the spread is ≥ 2 (one method's
       3 runs strongly differ from another method's 3 runs).
"""
from __future__ import annotations

from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path("docs/active/compendium-source-extracts/results/3way_consensus")
INPUT_FILE = ROOT / "usa_tradition_items.csv"

METHODS = ["m1_cluster_anchored", "m2_blind", "m3_focal_anchored"]
RUNS = [1, 2, 3]

STRICT_THRESHOLD = 8 / 9
LOOSE_THRESHOLD = 6 / 9
HUMAN_REVIEW_LO = 3 / 9
HUMAN_REVIEW_HI = 5 / 9


def load_run(method: str, run: int) -> pd.DataFrame:
    p = ROOT / f"{method}_run{run}.csv"
    df = pd.read_csv(p)
    required = {"source_paper", "source_id", "source_text", "group_id", "group_label"}
    if not required.issubset(df.columns):
        raise SystemExit(f"{p}: missing columns {required - set(df.columns)}")
    df["item_key"] = df["source_paper"].astype(str) + "|" + df["source_id"].astype(str)
    return df


def build_pair_matrix(input_items: pd.DataFrame) -> tuple[list[str], dict[str, int]]:
    """Stable item ordering and key->index lookup."""
    keys = (
        input_items["paper"].astype(str) + "|" + input_items["indicator_id"].astype(str)
    ).tolist()
    if len(set(keys)) != len(keys):
        raise SystemExit("input has duplicate (paper, indicator_id)")
    return keys, {k: i for i, k in enumerate(keys)}


def co_membership_matrix(df: pd.DataFrame, item_index: dict[str, int]) -> np.ndarray:
    """Boolean N×N matrix: True iff items i and j share group_id in this run.

    Stored as upper-triangular only; diagonal ignored.
    """
    n = len(item_index)
    mat = np.zeros((n, n), dtype=bool)
    for _, sub in df.groupby("group_id"):
        idxs = [
            item_index[k]
            for k in sub["item_key"].tolist()
            if k in item_index
        ]
        if len(idxs) < 2:
            continue
        for i, j in combinations(idxs, 2):
            a, b = (i, j) if i < j else (j, i)
            mat[a, b] = True
    return mat


def transitive_closure_clusters(
    pairs_strong: list[tuple[int, int]], n: int
) -> list[list[int]]:
    """Union-find over strong pairs → list of clusters (sorted-by-min-index)."""
    parent = list(range(n))

    def find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(x: int, y: int) -> None:
        rx, ry = find(x), find(y)
        if rx != ry:
            parent[rx] = ry

    for i, j in pairs_strong:
        union(i, j)

    by_root: dict[int, list[int]] = {}
    for i in range(n):
        by_root.setdefault(find(i), []).append(i)
    clusters = [sorted(members) for members in by_root.values() if len(members) >= 2]
    clusters.sort(key=lambda c: (-len(c), c[0]))
    return clusters


def main() -> None:
    input_items = pd.read_csv(INPUT_FILE)
    keys, item_index = build_pair_matrix(input_items)
    n = len(keys)

    runs_meta: list[tuple[str, int]] = [(m, r) for m in METHODS for r in RUNS]
    co_matrices: dict[tuple[str, int], np.ndarray] = {}
    for m, r in runs_meta:
        co_matrices[(m, r)] = co_membership_matrix(load_run(m, r), item_index)

    iu = np.triu_indices(n, k=1)
    pair_count = len(iu[0])

    per_method_counts: dict[str, np.ndarray] = {}
    for m in METHODS:
        stack = np.stack([co_matrices[(m, r)][iu] for r in RUNS], axis=0)
        per_method_counts[m] = stack.sum(axis=0).astype(np.int8)

    total_count = sum(per_method_counts[m] for m in METHODS).astype(np.int8)

    cross_max = np.maximum.reduce([per_method_counts[m] for m in METHODS])
    cross_min = np.minimum.reduce([per_method_counts[m] for m in METHODS])
    cross_spread = (cross_max - cross_min).astype(np.int8)

    item_meta = {
        idx: (
            input_items.iloc[idx]["paper"],
            input_items.iloc[idx]["indicator_id"],
            input_items.iloc[idx]["indicator_text"],
        )
        for idx in range(n)
    }

    summary_rows = []
    for k in range(pair_count):
        i, j = int(iu[0][k]), int(iu[1][k])
        if total_count[k] == 0:
            continue
        pi, idi, ti = item_meta[i]
        pj, idj, tj = item_meta[j]
        summary_rows.append(
            {
                "source_paper_i": pi,
                "source_id_i": idi,
                "source_text_i": ti,
                "source_paper_j": pj,
                "source_id_j": idj,
                "source_text_j": tj,
                "agreement_count": int(total_count[k]),
                "pair_strength": float(total_count[k]) / 9.0,
                "m1_count": int(per_method_counts["m1_cluster_anchored"][k]),
                "m2_count": int(per_method_counts["m2_blind"][k]),
                "m3_count": int(per_method_counts["m3_focal_anchored"][k]),
                "cross_method_spread": int(cross_spread[k]),
            }
        )
    summary = pd.DataFrame(summary_rows)
    summary = summary.sort_values(
        ["agreement_count", "cross_method_spread"], ascending=[False, True]
    )
    summary.to_csv(ROOT / "consensus_summary.csv", index=False)
    print(f"Wrote consensus_summary.csv ({len(summary)} pairs with agreement≥1)")

    strict_pairs = [
        (int(iu[0][k]), int(iu[1][k]))
        for k in range(pair_count)
        if total_count[k] / 9.0 >= STRICT_THRESHOLD
    ]
    loose_pairs = [
        (int(iu[0][k]), int(iu[1][k]))
        for k in range(pair_count)
        if total_count[k] / 9.0 >= LOOSE_THRESHOLD
    ]

    def write_clusters(pairs: list[tuple[int, int]], outpath: Path, label: str) -> None:
        clusters = transitive_closure_clusters(pairs, n)
        rows = []
        for cid, members in enumerate(clusters, start=1):
            for idx in members:
                p, iid, t = item_meta[idx]
                rows.append(
                    {
                        "cluster_id": f"c_{cid:03d}",
                        "cluster_size": len(members),
                        "source_paper": p,
                        "source_id": iid,
                        "source_text": t,
                    }
                )
        df = pd.DataFrame(rows)
        df.to_csv(outpath, index=False)
        print(
            f"Wrote {outpath.name}: {len(clusters)} clusters covering "
            f"{len(rows)} items ({label} threshold)"
        )

    write_clusters(strict_pairs, ROOT / "consensus_clusters_strict.csv", "strict ≥8/9")
    write_clusters(loose_pairs, ROOT / "consensus_clusters_loose.csv", "loose ≥6/9")

    review_mask = (summary["pair_strength"] >= HUMAN_REVIEW_LO) & (
        summary["pair_strength"] <= HUMAN_REVIEW_HI
    )
    review = summary.loc[review_mask].copy()
    review = review.sort_values("cross_method_spread", ascending=False)
    review.to_csv(ROOT / "consensus_human_review.csv", index=False)
    print(f"Wrote consensus_human_review.csv ({len(review)} pairs in 3-5/9 band)")

    instability: dict[str, float] = {}
    pairs_with_any_yes = total_count > 0
    for m in METHODS:
        c = per_method_counts[m]
        instable = (c == 1) | (c == 2)
        denom = int(pairs_with_any_yes.sum())
        instability[m] = float(instable.sum()) / denom if denom else 0.0

    between_disagreement_pairs = int(((cross_spread >= 2) & pairs_with_any_yes).sum())
    between_strong_disagreement_pairs = int(
        ((cross_spread >= 3) & pairs_with_any_yes).sum()
    )
    pairs_any = int(pairs_with_any_yes.sum())

    md = ROOT / "method_instability_report.md"
    with md.open("w") as fh:
        fh.write("# Method-instability and between-method disagreement\n\n")
        fh.write(
            "All denominators below are over **pairs that at least one of the "
            "9 runs put in the same group** (`pair_count_with_any_yes`). "
            "Pairs no run ever co-grouped are excluded from the denominator.\n\n"
        )
        fh.write(f"`pair_count_with_any_yes`: {pairs_any}\n\n")
        fh.write("## 1. Within-method instability\n\n")
        fh.write(
            "For each method M (3 runs), a pair is *instable within M* if M's "
            "3 runs disagree (count ∈ {1,2}). Stable = unanimous {0, 3}.\n\n"
        )
        fh.write("| method | within-method instability |\n")
        fh.write("|---|---:|\n")
        for m in METHODS:
            fh.write(f"| {m} | {instability[m]:.3f} |\n")
        fh.write("\n## 2. Between-method disagreement\n\n")
        fh.write(
            "For each pair, `cross_method_spread = max(m1_count, m2_count, "
            "m3_count) - min(...)` over the per-method counts (each ∈ "
            "{0..3}). Spread ≥ 2 = a method strongly differs from another.\n\n"
        )
        fh.write(
            f"- pairs with cross_method_spread ≥ 2: "
            f"{between_disagreement_pairs} "
            f"({between_disagreement_pairs / pairs_any:.3f})\n"
        )
        fh.write(
            f"- pairs with cross_method_spread ≥ 3 (strong): "
            f"{between_strong_disagreement_pairs} "
            f"({between_strong_disagreement_pairs / pairs_any:.3f})\n"
        )
    print(f"Wrote {md.name}")


if __name__ == "__main__":
    main()
