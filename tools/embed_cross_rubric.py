#!/usr/bin/env python3
"""
Sentence-embedding cross-rubric clustering.

Local-machine companion to the TF-IDF analysis shipped 2026-05-03 in
docs/active/compendium-source-extracts/results/20260503_cross_rubric_descriptive.md.

The TF-IDF run (which executed in a sandboxed env that couldn't reach HuggingFace)
established that the European-tradition rubrics (AccessInfo / CouncilEurope /
ALTER_EU / FOCAL) and the state-tradition rubrics (Opheim / Newmark / HiredGuns /
Sunlight) use largely non-overlapping vocabulary even when measuring the same
concept. Lexical clustering at sim>=0.30 produced 20 cross-rubric clusters, 13 of
which are within-author-family (Newmark2005<->Newmark2017). Sentence embeddings
should bridge more of the cross-tradition concepts.

Inputs:
  docs/active/compendium-source-extracts/results/cross_rubric_items_clustered.csv
  (committed 2026-05-03 — 509 rubric atomic items + topic tags)

Outputs (in --out-dir, default '.'):
  embed_similarity_matrix.npy          float32 [N, N] cosine-sim, diagonal zeroed
  embed_clusters_at_thresholds.csv     summary stats per threshold
  embed_clusters_full.txt              human-readable cluster dump

Usage:
  pip install sentence-transformers pandas numpy
  python tools/embed_cross_rubric.py
  # optional flags:
  python tools/embed_cross_rubric.py --model BAAI/bge-large-en-v1.5
  python tools/embed_cross_rubric.py --thresholds 0.45,0.55,0.65,0.75
  python tools/embed_cross_rubric.py --items path/to/cross_rubric_items_clustered.csv

Threshold guidance (sentence-embedding cosine-sim is not directly comparable to
TF-IDF cosine-sim — distribution shape is different):
  ~0.30  noise floor; cluster everything-with-everything
  ~0.50  "probably the same concept"; reasonable starting threshold
  ~0.70  "near-paraphrase"
  ~0.85  "essentially identical wording"

What to look for in the output (predictions to falsify):
  1. Does the European<->state-tradition vocabulary divide bridge?
     If yes: clusters spanning 4-5 rubrics from both traditions on shared
     concepts. TF-IDF produced exactly one such cluster at sim>=0.20
     ("lobbyist definition") and only because the literal word "lobbyist"
     appeared in all five.

  2. Does the "expenditures benefiting public officials" concept consolidate?
     Currently scattered across Opheim, FOCAL, Newmark, HiredGuns, Sunlight in
     wildly different vocabulary. TF-IDF caught Newmark<->Opheim<->FOCAL but
     missed HiredGuns and Sunlight.

  3. Does the meeting-log family form? SOMO's disc_leg_footprint, IBAC's
     ministerial-diary items, AccessInfo's "duty to keep a true and detailed
     record of meetings with lobbyists", CouncilEurope's "Recorded contacts",
     FOCAL's contact-log category, TI_2016's "Lobby meeting record must
     include the entity met" — same concept, almost zero lexical overlap.

If MiniLM does NOT bridge these, that itself is a finding worth recording —
it would mean the vocabulary divide reflects genuinely different conceptual
decompositions, not just different words for the same thing.
"""
import argparse
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--model', default='all-MiniLM-L6-v2',
                    help='sentence-transformers model name or local path '
                         '(default: all-MiniLM-L6-v2; ~80MB, 384-dim, fast on CPU)')
    ap.add_argument('--items',
                    default='docs/active/compendium-source-extracts/results/cross_rubric_items_clustered.csv',
                    help='path to the items CSV (default: relative to repo root)')
    ap.add_argument('--thresholds', default='0.50,0.60,0.70,0.80',
                    help='comma-separated similarity thresholds for clustering '
                         '(default: 0.50,0.60,0.70,0.80)')
    ap.add_argument('--out-dir', default='.', help='output directory (default: cwd)')
    args = ap.parse_args()

    items_path = Path(args.items)
    if not items_path.exists():
        # Try resolving relative to script location -> repo root
        script_dir = Path(__file__).resolve().parent
        candidate = (script_dir.parent / items_path).resolve()
        if candidate.exists():
            items_path = candidate
        else:
            sys.exit(f'ERROR: items file not found: {args.items}\n'
                     f'  Tried: {Path(args.items).resolve()}\n'
                     f'  Tried: {candidate}')

    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)

    print(f'Loading items from {items_path}...', flush=True)
    df = pd.read_csv(items_path).fillna('')
    # Match the TF-IDF blob: indicator_text + section
    df['blob'] = (df['indicator_text'].astype(str) + ' ' +
                  df['section'].astype(str)).str.strip()
    print(f'  {len(df)} rubric atomic items')
    print(f'  rubrics: {df["paper"].nunique()}  '
          f'({", ".join(sorted(df["paper"].unique())[:5])}, ...)')

    print(f'\nLoading model {args.model}...', flush=True)
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError:
        sys.exit('ERROR: sentence-transformers not installed.\n'
                 '  Run: pip install sentence-transformers pandas numpy')
    model = SentenceTransformer(args.model)

    print('Encoding...', flush=True)
    embs = model.encode(df['blob'].tolist(),
                        normalize_embeddings=True,
                        show_progress_bar=True,
                        batch_size=64,
                        convert_to_numpy=True)
    print(f'  embeddings: {embs.shape}  dtype={embs.dtype}')

    # Cosine similarity (normalized -> dot product)
    sim = (embs @ embs.T).astype(np.float32)
    np.fill_diagonal(sim, 0.0)
    np.save(out / 'embed_similarity_matrix.npy', sim)
    print(f'\nSaved {out / "embed_similarity_matrix.npy"}')

    # Distribution of nearest-neighbor similarities
    nearest = sim.max(axis=1)
    print('\nMax cross-similarity distribution:')
    for q in [0.40, 0.50, 0.60, 0.70, 0.80, 0.90]:
        n = int((nearest >= q).sum())
        print(f'  items with at least one near-match (sim >= {q:.2f}): {n}  '
              f'({100*n/len(df):.1f}%)')

    # Clustering — single-link union-find restricted to cross-rubric pairs
    papers = df['paper'].values
    thresholds = [float(t.strip()) for t in args.thresholds.split(',')]

    def cluster_at(thr):
        n = len(df)
        parent = list(range(n))
        def find(x):
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x
        def union(a, b):
            a, b = find(a), find(b)
            if a != b:
                parent[a] = b
        ii, jj = np.where(sim >= thr)
        for i, j in zip(ii, jj):
            if i < j and papers[i] != papers[j]:
                union(int(i), int(j))
        clusters = defaultdict(list)
        for i in range(n):
            clusters[find(i)].append(i)
        return [c for c in clusters.values() if len(c) > 1]

    rows = []
    print('\n=== Clusters at each threshold ===')
    print(f'{"Thr":>5}  {"Clusters":>8}  {"Items":>5}  {"Largest":>7}  '
          f'{">=3 rubs":>9}  {">=5 rubs":>9}')
    full_dump_lines = []
    for thr in thresholds:
        cl = cluster_at(thr)
        if not cl:
            print(f'{thr:5.2f}  {0:>8}  {0:>5}  {"-":>7}  {0:>9}  {0:>9}')
            rows.append({'threshold': thr, 'n_clusters': 0, 'items_in_clusters': 0,
                         'largest': 0, 'clusters_ge_3_rubrics': 0,
                         'clusters_ge_5_rubrics': 0})
            continue
        items = sum(len(c) for c in cl)
        largest = max(len(c) for c in cl)
        m3 = sum(1 for c in cl if len({papers[i] for i in c}) >= 3)
        m5 = sum(1 for c in cl if len({papers[i] for i in c}) >= 5)
        print(f'{thr:5.2f}  {len(cl):>8}  {items:>5}  {largest:>7}  '
              f'{m3:>9}  {m5:>9}')
        rows.append({'threshold': thr, 'n_clusters': len(cl),
                     'items_in_clusters': items, 'largest': largest,
                     'clusters_ge_3_rubrics': m3, 'clusters_ge_5_rubrics': m5})

        full_dump_lines.append(f'\n{"=" * 70}\n')
        full_dump_lines.append(f'Threshold {thr:.2f} — {len(cl)} cross-rubric clusters\n')
        full_dump_lines.append(f'{"=" * 70}\n')
        # Sort by descending rubric-span, then descending size
        for ci, c in enumerate(sorted(
                cl,
                key=lambda x: (-len({papers[i] for i in x}), -len(x)))):
            rubrics = sorted({papers[i] for i in c})
            full_dump_lines.append(
                f'\nCluster {ci+1}  size={len(c)}  rubrics({len(rubrics)})='
                f'{", ".join(rubrics)}\n')
            for i in c:
                full_dump_lines.append(
                    f'   [{df.paper.iloc[i]:14s}] '
                    f'{df.indicator_text.iloc[i][:140]}\n')

    pd.DataFrame(rows).to_csv(out / 'embed_clusters_at_thresholds.csv', index=False)
    (out / 'embed_clusters_full.txt').write_text(''.join(full_dump_lines))
    print(f'\nSaved {out / "embed_clusters_at_thresholds.csv"}')
    print(f'Saved {out / "embed_clusters_full.txt"}')

    print('\nNext steps:')
    print('  1. Compare against the TF-IDF baseline in '
          'docs/active/compendium-source-extracts/results/'
          '20260503_cross_rubric_descriptive.md')
    print('  2. Look for 4-5 rubric clusters that span European<->state-tradition')
    print('  3. If interesting cross-tradition clusters surface, integrate the '
          'comparison into a follow-up results doc')


if __name__ == '__main__':
    main()
