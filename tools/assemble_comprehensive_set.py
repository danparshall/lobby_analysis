#!/usr/bin/env python3
"""
Assemble the comprehensive item set (compendium 2.0 working draft).

v1 (initial): Core 3 (HG + FOCAL + Newmark2017) + Opheim coverage extension.
v2 (this script): adds all PRI 2010 items (accessibility 22 + disclosure-law 61
    = 83) per explicit user clearance on 2026-05-06.
    PRI is included as a coverage extension only — NOT as a structural anchor,
    NOT as a row-frame contributor. The STATUS.md ⛔ block on PRI remains in
    force for all OTHER uses (no PRI-derived seeding, no "match PRI", no
    bootstrapping new artifacts from PRI rubric structure).

Inputs (read from docs/active/compendium-source-extracts/results/):
  - items_HiredGuns.tsv    atomic items
  - items_FOCAL.tsv        atomic items
  - items_Newmark2017.tsv  atomic items (filtered: drop composites)
  - items_Opheim.tsv       atomic items (filtered: keep only the
                           coverage-gap subset enumerated below)
  - items_PRI_2010.tsv     atomic items (transcribed from historical
                           pri-2026-rescore CSVs; all 83 included)
  - cross_rubric_items_clustered.csv  (used to identify atomic items per
                                       paper, since some TSVs contain
                                       composite/sub-total rows)
  - embed_similarity_matrix__openai__text-embedding-3-large.npy
  - embed_index__openai__text-embedding-3-large.csv

Output (written to results/):
  - <date>_comprehensive_set_v2.tsv
  - <date>_comprehensive_set_v2.md   (assembly note)

Selection logic for Opheim coverage extension:
  Items below sim=0.55 to anything in HiredGuns + FOCAL + Newmark2017 (clear
  coverage gaps), plus two borderline items (sim 0.55-0.60) that add
  conceptually distinct content beyond their lexical near-matches:
    enforcement (6):  subpoena witnesses, subpoena records, administrative
                      hearings, administrative fines, administrative
                      penalties, independent court actions
    income (2):       sources of income, total income
    oversight (1):    thoroughness of reviews of lobby reports
    catch-all (1):    other activities that might constitute influence
                      peddling or conflict of interest

Skipped (covered by core 3):
  - definition criteria (legislative/admin/elected/employees) — Newmark2017
  - lobbyist-status thresholds (compensation/expenditure/time) — Newmark2017
  - frequency of reporting — HiredGuns / FOCAL
  - lobbyist's total spending, spending by category, expenditures benefitting
    public employees — HiredGuns / FOCAL / Newmark2017
  - legislation approved or opposed — partial coverage in HiredGuns subject-
    matter item (skipped pending user review if scope mismatch matters)

Skipped (not in scope):
  - Newmark2005 short-label items — concepts already in Newmark2017 longer text
  - CPI_2015 multi-domain integrity labels (Procurement, State pension fund
    management, etc.) — not lobbying-disclosure items
  - OpenSecrets — fully covered by core 3
  - Sunlight short labels — concepts already in core 3

European-tradition rubrics deferred — most items are out of US-state-lobbying-
disclosure scope (right to participate, EU-specific operational details, Dutch
consultation reform). A future pass should flag a small number for coverage-
comparison reference (e.g. IBAC's MP-meeting-disclosure cluster), but those
are not added to the working set in this round.
"""
import datetime as dt
from pathlib import Path

import numpy as np
import pandas as pd

RESULTS = Path('docs/active/compendium-source-extracts/results')

# Map cross_rubric_items_clustered.csv 'paper' -> items_*.tsv filename
PAPER_TO_FILE = {
    'HiredGuns':   'items_HiredGuns.tsv',
    'FOCAL':       'items_FOCAL.tsv',
    'Newmark2017': 'items_Newmark2017.tsv',
    'Opheim':      'items_Opheim.tsv',
}

# Per-rubric compendium_role tag for the core 3
CORE_ROLE = {
    'HiredGuns':   'core_hg',
    'FOCAL':       'core_focal',
    'Newmark2017': 'core_newmark2017',
}

# Opheim items to pull in. Keys are exact `indicator_id` from items_Opheim.tsv;
# values are (compendium_role, rationale).
OPHEIM_EXTENSIONS = {
    # 6 enforcement items (Opheim section: enforcement)
    'enforce.subpoena_witnesses': ('ext_opheim_enforce',
        'COGEL Blue Book Table 31 — agency subpoena power over witnesses'),
    'enforce.subpoena_records': ('ext_opheim_enforce',
        'COGEL Blue Book Table 31 — agency subpoena power over records'),
    'enforce.conduct_administrative_hearings': ('ext_opheim_enforce',
        'COGEL Blue Book Table 31 — agency authority to conduct hearings'),
    'enforce.impose_administrative_fines': ('ext_opheim_enforce',
        'COGEL Blue Book Table 31 — agency authority to impose fines'),
    'enforce.impose_administrative_penalties': ('ext_opheim_enforce',
        'COGEL Blue Book Table 31 — agency authority to impose penalties'),
    'enforce.file_independent_court_actions': ('ext_opheim_enforce',
        'COGEL Blue Book Table 31 — agency authority to file independent court actions'),
    # 2 income items (Opheim section: disclosure)
    'disclosure.sources_of_income': ('ext_opheim_income',
        'income disclosure — sources (distinct from compensation in core 3)'),
    'disclosure.total_income': ('ext_opheim_income',
        'income disclosure — totals (distinct from compensation in core 3)'),
    # 1 oversight-quality item (sim=0.585; partial overlap with HiredGuns
    # mandatory-audits item but adds an intensity/quality dimension HG does not)
    'enforce.thoroughness_of_reviews': ('ext_opheim_oversight',
        'oversight intensity — quality of report review (distinct from binary '
        'existence of audit in HiredGuns)'),
    # 1 catch-all (sim=0.552; lexical-noise match with FOCAL real-time
    # disclosure; conceptually distinct catch-all)
    'disclosure.other_influence_peddling_or_conflict_of_interest': ('ext_opheim_catchall',
        'compendium escape-hatch for influence-peddling activities not '
        'otherwise enumerated'),
}


def load_cross_rubric_atomics() -> pd.DataFrame:
    """Atomic items per paper, used for the core 3 set membership."""
    return (pd.read_csv(RESULTS / 'cross_rubric_items_clustered.csv')
            .fillna(''))


def best_core_match(paper_id: str, indicator_id: str, sim: np.ndarray,
                    idx: pd.DataFrame, core_idxs: np.ndarray) -> tuple:
    """For an Opheim extension item, find its highest-sim core-3 neighbor."""
    sub = idx[(idx.paper == paper_id) & (idx.indicator_id == indicator_id)]
    if sub.empty:
        return (None, None, None)
    i = sub.index[0]
    sims = sim[i, core_idxs]
    j = int(sims.argmax())
    return (float(sims[j]),
            idx.paper.iloc[core_idxs[j]],
            idx.indicator_id.iloc[core_idxs[j]])


def main():
    today = dt.date.today().strftime('%Y%m%d')
    out_tsv = RESULTS / f'{today}_comprehensive_set_v2.tsv'
    out_md  = RESULTS / f'{today}_comprehensive_set_v2.md'

    # Load similarity + index for best-core-match annotation on extensions
    sim = np.load(RESULTS / 'embed_similarity_matrix__openai__text-embedding-3-large.npy')
    idx = pd.read_csv(RESULTS / 'embed_index__openai__text-embedding-3-large.csv').fillna('')
    core_idxs = np.where(np.isin(idx['paper'].values,
                                 list(CORE_ROLE.keys())))[0]

    # Collect rows
    cross = load_cross_rubric_atomics()
    out_rows = []

    # Core 3 — pull all atomic items from the cross-rubric CSV joined to the
    # full-provenance items_*.tsv
    for paper, role in CORE_ROLE.items():
        atomic_ids = set(cross.loc[cross.paper == paper, 'indicator_id'])
        src = pd.read_csv(RESULTS / PAPER_TO_FILE[paper], sep='\t').fillna('')
        kept = src[src['indicator_id'].isin(atomic_ids)].copy()
        kept['compendium_role'] = role
        kept['extension_rationale'] = ''
        kept['best_core_match_paper'] = ''
        kept['best_core_match_id'] = ''
        kept['best_core_match_sim'] = ''
        out_rows.append(kept)
        print(f'  {paper:14}  +{len(kept)} items  (role={role})')

    # Opheim extensions — keep only the enumerated subset
    src_oph = pd.read_csv(RESULTS / 'items_Opheim.tsv', sep='\t').fillna('')
    for ind_id, (role, rationale) in OPHEIM_EXTENSIONS.items():
        match = src_oph[src_oph['indicator_id'] == ind_id]
        if match.empty:
            print(f'  WARNING: Opheim item not found: {ind_id}')
            continue
        row = match.iloc[0:1].copy()
        row['compendium_role'] = role
        row['extension_rationale'] = rationale
        bm_sim, bm_paper, bm_id = best_core_match('Opheim', ind_id, sim, idx,
                                                  core_idxs)
        row['best_core_match_paper'] = bm_paper or ''
        row['best_core_match_id']    = bm_id or ''
        row['best_core_match_sim']   = f'{bm_sim:.3f}' if bm_sim else ''
        out_rows.append(row)
        print(f'  Opheim         +1 item   ({ind_id})  '
              f'role={role}  best-core-match-sim={bm_sim:.3f}')

    # PRI 2010 — pull all items per explicit user clearance on 2026-05-06.
    # Tagged ext_pri_2010_accessibility / ext_pri_2010_disclosure based on the
    # `accessibility.` / `disclosure.` indicator_id prefix. NOT in the embedding
    # space (PRI was excluded from the 26-paper extraction round), so
    # best_core_match_* is left blank — to be backfilled if/when PRI items get
    # embedded in a follow-up pass.
    src_pri = pd.read_csv(RESULTS / 'items_PRI_2010.tsv', sep='\t').fillna('')
    pri_rows = src_pri.copy()
    pri_rows['compendium_role'] = pri_rows['indicator_id'].apply(
        lambda x: 'ext_pri_2010_accessibility' if x.startswith('accessibility.')
        else 'ext_pri_2010_disclosure')
    pri_rows['extension_rationale'] = (
        'PRI 2010 included as coverage extension per user clearance '
        '2026-05-06 — non-default, NOT a row-frame contributor')
    pri_rows['best_core_match_paper'] = ''
    pri_rows['best_core_match_id'] = ''
    pri_rows['best_core_match_sim'] = ''
    out_rows.append(pri_rows)
    print(f'  PRI 2010      +{len(pri_rows)} items  (accessibility=22, '
          f'disclosure-law=61; not yet embedded)')

    df = pd.concat(out_rows, ignore_index=True)
    cols = ['compendium_role', 'paper_id', 'indicator_id', 'indicator_text',
            'section_or_category', 'indicator_type', 'scoring_rule',
            'source_quote', 'notes', 'extension_rationale',
            'best_core_match_paper', 'best_core_match_id',
            'best_core_match_sim']
    df = df[cols]
    df.to_csv(out_tsv, sep='\t', index=False)
    print(f'\nWrote {out_tsv}  ({len(df)} items, {len(cols)} columns)')

    # Markdown summary
    counts = df.groupby('compendium_role').size().to_dict()
    md = [f'# Comprehensive item set — v2  ({today})\n',
          '',
          'Working draft for compendium 2.0. Assembled from per-rubric source ',
          'extracts shipped 2026-05-03, a coverage-gap extension from Opheim ',
          '1991 (identified via OpenAI `text-embedding-3-large` similarity ',
          'analysis), and all PRI 2010 items (added 2026-05-06 per explicit ',
          'user clearance to use PRI as a non-default coverage source).',
          '',
          '> **PRI inclusion note:** PRI 2010 items are tagged ',
          '> `ext_pri_2010_*` to make their non-default status durable. ',
          '> PRI is NOT a structural anchor here. The STATUS.md ⛔ block ',
          '> on PRI remains in force for all OTHER uses (no PRI-derived ',
          '> seeding, no "match PRI" calibration, no bootstrapping new ',
          '> artifacts from PRI rubric structure).',
          '',
          '## Composition',
          '',
          f'- **Total items:** {len(df)}',
          '',
          '| compendium_role | n | source rubric |',
          '|---|---:|---|',
          f'| core_hg | {counts.get("core_hg", 0)} | CPI Hired Guns 2007 (50-state report-card on lobbying disclosure) |',
          f'| core_focal | {counts.get("core_focal", 0)} | FOCAL / Lacy-Nichols 2024 (cross-jurisdiction normative checklist) |',
          f'| core_newmark2017 | {counts.get("core_newmark2017", 0)} | Newmark 2017 (state lobbying-regulation index, 19-component) |',
          f'| ext_opheim_enforce | {counts.get("ext_opheim_enforce", 0)} | Opheim 1991 — agency enforcement powers (Table 31 of the COGEL Blue Book; Newmark dropped these) |',
          f'| ext_opheim_income | {counts.get("ext_opheim_income", 0)} | Opheim 1991 — income disclosure (distinct from compensation) |',
          f'| ext_opheim_oversight | {counts.get("ext_opheim_oversight", 0)} | Opheim 1991 — review intensity dimension |',
          f'| ext_opheim_catchall | {counts.get("ext_opheim_catchall", 0)} | Opheim 1991 — influence-peddling catch-all |',
          f'| ext_pri_2010_disclosure | {counts.get("ext_pri_2010_disclosure", 0)} | PRI 2010 disclosure-law rubric (61 atomic items; transcribed 2026-04-13 from PRI 2010 §III) |',
          f'| ext_pri_2010_accessibility | {counts.get("ext_pri_2010_accessibility", 0)} | PRI 2010 accessibility rubric (22 atomic items; transcribed 2026-04-13 from PRI 2010 §IV) |',
          '',
          '## Method',
          '',
          'Coverage analysis: for each non-core atomic item, computed cosine ',
          'similarity to every core-3 item under text-embedding-3-large; took ',
          'the per-item argmax as best-core-match. Items with best-core-match ',
          'sim < 0.55 are uncovered; sim 0.55-0.60 are partial; sim ≥ 0.60 are ',
          'covered (with the caveat that single-link clustering at sim ≥ 0.68 ',
          'tends to under-bridge cross-tradition pairs).',
          '',
          'Pulled in: 8 Opheim items at sim < 0.55 (clearly uncovered) plus 2 ',
          'borderline items (sim 0.55-0.60) that add conceptually distinct ',
          'content beyond their lexical near-matches.',
          '',
          'Skipped (covered): all Newmark2005 (short-label artifacts of items ',
          'in Newmark2017), all OpenSecrets (fully covered), all Sunlight ',
          '(short labels), all CPI_2015 (multi-domain integrity scorecard, ',
          'most items not lobbying-specific).',
          '',
          'European-tradition rubrics deferred — most items are out of ',
          'US-state-lobbying-disclosure scope. A future pass may flag a small ',
          'subset (e.g. IBAC MP-meeting-disclosure cluster) for ',
          'coverage-comparison reference; not in this round.',
          '',
          'PRI 2010 added in v2 (this round) per explicit user clearance ',
          '2026-05-06: "include all PRI items, now that we aren\'t locked ',
          'onto them". All 83 PRI atomic items pulled in unfiltered (22 ',
          'accessibility + 61 disclosure-law). They are NOT in the 509-item ',
          'embedding space (PRI was excluded from the 26-paper extraction ',
          'round), so `best_core_match_*` columns are blank for PRI rows. A ',
          'follow-up coverage analysis could embed them and identify which ',
          'PRI items are redundant with existing rows; for now all are kept ',
          'verbatim.',
          '',
          '## Files',
          '',
          f'- TSV: `{out_tsv.name}`  ({len(df)} rows × {len(cols)} cols)',
          f'- Source extracts: `items_HiredGuns.tsv`, `items_FOCAL.tsv`, ',
          '  `items_Newmark2017.tsv`, `items_Opheim.tsv`',
          f'- Embedding artifacts: `embed_*__openai__text-embedding-3-large.{{npy,csv,txt}}`',
          '']
    out_md.write_text('\n'.join(md))
    print(f'Wrote {out_md}')


if __name__ == '__main__':
    main()
