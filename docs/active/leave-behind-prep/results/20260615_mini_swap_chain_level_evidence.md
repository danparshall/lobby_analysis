# Mini-swap: chain-level evidence (2026-06-15)

**Status:** Substantive update on the 2026-06-13 provisional findings
(`results/20260613_mini_swap_quality_gate_findings.md`). That doc framed the
mini-swap as gated on a 5-step next-session shape (re-validate briefv2 in
isolation, author normalization layers, etc.) and labeled the decision
"provisional, not locked." This doc reports a *direct end-to-end test* of
the mini-swap question — *does the released OH chain artifact actually
change if mini briefv2 is the extractor?* — and answers most of the
remaining open questions with concrete chain-row evidence. The 2026-06-13
provisional doc is not wrong; it is superseded by stronger evidence on
points 3-5 of the open-questions list.

**Originating convo:**
[`convos/20260615_mini_swap_chain_level_experiment.md`](../convos/20260615_mini_swap_chain_level_experiment.md)
(walked the leave-behind-prep punch list → user asked "have we tried
it?" → ran the experiment below).

**Plan for implementation:**
[`plans/20260615_composer_side_mini_swap_normalizations.md`](../plans/20260615_composer_side_mini_swap_normalizations.md)

---

## TL;DR

- **On LUPA (Legislative) AERs — the form type the extraction brief
  targets — mini briefv2 produces chain output that is structurally
  equivalent to sonnet at the chain-row level**: same position count
  (236 = 236), same per-filing median (2.0 = 2.0), same abstention count
  (9 = 9), zero disagreement on bill resolution (bill_id, bill_class,
  bill_title, sponsor_lawmaker_id, num_primary_sponsors all match
  perfectly on shared rows).
- **On EUPA (Executive) AERs — the form type the brief does not directly
  target (#58) — both models mostly abstain.** Sonnet emits zero positions
  on 36/46 EUPA filings; mini briefv2 on 32/46. Position-content sparsity
  is a property of the form, not a mini failure. **Mini is marginally
  better than sonnet on EUPA emit rate** in this slice.
- **The two real residual gaps are composer-side conventions, not
  extraction-quality issues**:
  1. `principal_id` / `lobbyist_id` disagree on ~98% of shared chain rows
     because they are *model-emitted schema fields* (`Organization.id`,
     `Person.id` in `LobbyingFiling`), not composer-minted. Sonnet uses
     a mostly-stable kebab-case convention (`org-cleveland-browns-oh`);
     mini uses inconsistent formats (`org:Cleveland_Browns`, raw name,
     or empty string). The names themselves match. Composer-side fix:
     derive IDs deterministically from name.
  2. **Mini puts subject content into the wrong schema slot** — `bill_reference`
     rather than `general_issue_area`. The chain composer's classifier
     correctly flags these as `bill_referenced + unmatched` (the
     bill_reference label doesn't match HB/SB/JCARR/OAC patterns), so they
     pollute the chain as 59 false-bill rows. **Mini's bill_referenced-
     unmatched rate is 14% (59/416) vs sonnet's 1.2% (18/1,468)** —
     order-of-magnitude difference. **Concentration: 92% of mini's
     unmatched rows come from 3 EUPA filings** with regulatory/policy
     subjects (e.g., "Competency Restoration", "Behavioral Health
     Handbook") that sonnet correctly routes to `general_issue_area`.
     Composer-side fix: demote `unmatched` bill_referenced rows to
     `subject_general` when the bill_reference text contains no digits
     (preserves visibility into "malformed bill with typo'd number" —
     sonnet's 1.2% audit signal — while closing mini's order-of-magnitude
     diff).
  3. (Note: the 2026-06-13 doc's Q1 "description-hoist" framing turned
     out to be the *opposite* slot direction — that fix is already in
     place as `POSITION_KIND_SUBJECT_HOISTED` in the composer's classifier
     and accounts for only 2 of mini's 426 chain rows. The actual residual
     gap is the bill_referenced-unmatched demotion above.)
- **The is_itemized regression that gated the original lock-it decision
  is moot if briefv2 is the production base** — it was caused by
  briefv3's bullet 8 (the `is_current` default), which briefv2 does not
  have. The 2026-06-13 doc already recommended this; this experiment
  confirms that briefv2 as base produces a usable chain artifact.
- **Net read:** the mini-swap is materially closer to ship-ready than
  the 2026-06-13 provisional framing implied — but it requires *one
  composer-side normalization the prior findings doc didn't name*
  (the bill_referenced-unmatched demotion). With both normalizations
  implemented (entity-ID derivation + bill_referenced demotion, per
  the plan doc accompanying this findings doc), the chain artifact's
  remaining mini-vs-sonnet differences would be:
    - 5 subject-text divergences (different subject wording for the same
      source position; content-level, not structural).
    - 2 mini-emitted real bills sonnet missed (mini-wins).
    - 2 mini-emitted OAC rule citations sonnet rolled up — Q5 in the
      2026-06-13 doc, contingent on the composer's intended OAC/JCARR
      edge granularity (Dan's call).
    - The 18 sonnet-only "malformed bill_referenced" rows in the broader
      305-filing chain — preserved by the digit-check escape hatch in
      the demotion rule.
    - The cost-identity reconciliation (which model id = the $0.0066
      measurement?), which gates any external dollar figure.

---

## Experiment setup

**Date:** 2026-06-15.
**Cost:** $0 (no new API spend — used existing briefv2 outputs on disk
from the 2026-06-09 dispatch).
**Wall:** ~15 min including diff scripts.

**Inputs (all on disk in the `leave-behind-prep` worktree, symlinked
to `~/data/lobby_analysis/`):**
- Sonnet baselines at `data/oh_portal/extracted/<rid>/<uuid8>/filing.json`
  (305 OH AERs from the 300-slice validation).
- Mini briefv2 extractions at
  `data/oh_portal/extracted_openai/<rid>/mini_medium_briefv2_*/filing.json`
  (100 OH AERs — the briefv2 cross-arm sample from 2026-06-09).
- Plural Policy 136th GA bundle at `data/bills/OH/136/`.

**Code:**
- OH chain composer shipped 2026-06-15 on `main` via PR #59 (issue #52
  closed). Code at `src/lobby_analysis/allocation/oh/`. CLI:
  `python -m lobby_analysis.allocation.oh.cli materialize`.
- Released sonnet chain at
  `releases/oh/chain/OH_chain_2025_2026_preview.tsv` (1,589 rows × 18
  cols from the full 305 filings).

**Procedure:**
1. Stage briefv2 mini outputs into a parallel
   `data/oh_portal/extracted_briefv2_mini/<rid>/<run_id>/filing.json`
   directory (symlinks). The composer's loader expects
   `<extractions>/<rid>/<run_id>/filing.json`, so a parallel directory
   leaves the sonnet baseline untouched. Staging script:
   `/tmp/stage_briefv2_mini.py` (to move to `scripts/` at commit time).
2. Run the composer on the staged dir, writing to
   `/tmp/oh_release_briefv2_mini/`. Output:
   - chain: 426 rows × 18 cols
   - gifts: 0 rows (empirical base-rate finding consistent with the
     shipped sonnet chain — see PR #59)
   - filings: 100 rows × 14 cols
3. Diff against the shipped sonnet chain, restricted to the 100 rids the
   mini run covers. Diff scripts at `/tmp/diff_mini_vs_sonnet_chain.py`,
   `/tmp/inspect_id_disagreement.py`, `/tmp/inspect_chain_missing_v2.py`,
   `/tmp/sonnet_vs_mini_by_section.py`.

**Caveat on n:** the sonnet baseline covers 305 filings (305 LUPA + 0
EUPA — wait, see below); the mini briefv2 covers 100. The shared 100
overlap is what the comparison runs against. Of those 100: 54 LUPA + 46
EUPA. Of the broader sonnet 305: section breakdown not surveyed here
(the briefv2 100 was sampled across section types per the 2026-06-09
dispatch design, not LUPA-only — so the EUPA observations below are
*about EUPA*, not extrapolations from a LUPA-only sample).

---

## Quantitative results

### Per-filing position counts on the shared 100 rids

| metric | sonnet | mini briefv2 |
|---|---|---|
| total filings | 100 | 100 |
| filings with positions=0 | 45 (45%) | 41 (41%) |
| filings with positions>0 in BOTH | 55 | 55 |
| total positions emitted | 304 | 310 |
| median positions/filing | 1.0 | 1.0 |

### Broken out by section type

| section | n_filings | sonnet_zero | mini_zero | sonnet_pos | mini_pos | sonnet_median | mini_median |
|---|---|---|---|---|---|---|---|
| LUPA (Legislative) | 54 | 9 | 9 | **236** | **236** | 2.0 | 2.0 |
| EUPA (Executive)  | 46 | 36 | 32 | 68 | 74 | 0.0 | 0.0 |

The LUPA columns match exactly. EUPA: both models mostly abstain; mini
emits slightly more positions (74 vs 68) and abstains on 4 fewer
filings. The earlier hypothesis — "mini follows the Legislative-AER
brief literally and over-abstains on Executive AERs" — is *not*
supported by this data. Both models recognize Executive AER position
content as sparse.

### Chain composer output on the shared 100 rids

| metric | sonnet (restricted to 100 rids) | mini briefv2 |
|---|---|---|
| chain rows | 419 | 426 |
| filings present in chain | 59 | 59 |
| filings absent from chain | 41 (= 41 zero-position filings) | 41 (ditto) |

Identical filings appear in chain across both models. The 41 absent are
the 41 filings with zero positions, distributed: 32 EUPA + 9 LUPA. Not
a composer behavior difference, not a model-quality difference — a
property of which filings have position content at all.

### Row-set diff on chain output (key = filing_id × bill_label_normalized × position_kind)

| bucket | rows |
|---|---|
| shared (key present in both) | 240 |
| sonnet-only | 48 |
| mini-only | 61 |

### Position-kind × bill-class breakdown of the diff buckets

**Sonnet-only (48 rows)** — all are subject content routed correctly:
| position_kind | bill_class | rows |
|---|---|---|
| subject_general | subject | 48 |

**Mini-only (61 rows)** — dominated by misrouted subject content in the wrong slot:
| position_kind | bill_class | rows | nature |
|---|---|---|---|
| bill_referenced | unmatched | 59 | mini emits subject content into `bill_reference` slot; composer correctly flags `unmatched` (label has no HB/SB/OAC/JCARR pattern) |
| bill_referenced | bill | 2 | mini extracts real bills sonnet missed |
| bill_referenced | oac_rule | 2 | mini extracts real OAC rule citations sonnet rolled up (Q5 in 2026-06-13 doc) |
| subject_general | subject | 5 | mini emits subject content correctly; sonnet emits different subject text for the same source position |
| subject_hoisted_from_description | subject | 2 | composer hoist already in place; handles the small residual |

**Concentration of the 59 mini-only unmatched rows:**

| filing_id | rows | sonnet's routing of the same content |
|---|---|---|
| `20250528EUPA1412254` | 35 | 36 of 38 rows go to `subject_general`; 2 to `bill_referenced + bill` |
| `20250916EUPA1433628` | 13 | 13 of 13 → `subject_general` |
| `20250530EUPA1419016` |  6 |  6 of  6 → `subject_general` |
| (3 other filings) |  5 | mix |

92% of the 59 mini-only unmatched rows come from 3 EUPA filings. These
filings disclose lobbying on regulatory/policy topics rather than specific
bills — there are no bills to reference, so mini emits the topic label in
`bill_reference` (wrong slot) and sonnet emits the same topic in
`general_issue_area` (correct slot).

**Sonnet-only example** (correct routing, what we want):
- `('20250528EUPA1412254', 'Opioid / State Grant', 'subject_general')`
- Source position: `bill_reference=None`, `general_issue_area='Opioid / OneOhio'`, `description='OneOhio (Governor)'`

**Mini-only example** (wrong slot, what we'd close with composer-side demotion):
- `('20250528EUPA1412254', 'COMPETENCY RESTORATION', 'bill_referenced')` (bill_class=unmatched)
- Source position: `bill_reference={'original_text':'Competency Restoration'}`, `general_issue_area=''`, `description='Competency Restoration'`

The two source positions are extracting the same kind of content — a
regulatory/policy subject — but routing it differently. Sonnet's bill_class
distribution (overall, 305 filings): `bill 1299 + jcarr 88 + oac_rule 34 +
unmatched 18` = 1.2% unmatched. Mini's bill_class distribution (100
filings): `bill 355 + oac_rule 2 + unmatched 59` = 14.2% unmatched.

### Cell-level disagreement on the 240 shared rows

| field | disagreements | %  | comment |
|---|---|---|---|
| bill_class | 0 | 0% | |
| bill_id | 0 | 0% | |
| bill_label_raw | 0 | 0% | |
| bill_title | 0 | 0% | |
| confidence | 0 | 0% | |
| lobbyist_name | 0 | 0% | |
| num_primary_sponsors | 0 | 0% | |
| report_period | 0 | 0% | |
| sponsor_lawmaker_id | 0 | 0% | |
| sponsor_lawmaker_name | 0 | 0% | |
| sponsor_role | 0 | 0% | |
| **principal_id** | **236** | **98.3%** | model-emitted schema field, format-only |
| **lobbyist_id** | **235** | **97.9%** | same |
| principal_name | 4 | 1.7% | minor; sample below |
| position_description | 2 | 0.8% | minor |

The 98% disagreement on `principal_id` / `lobbyist_id` is a single
issue: the schema field `Organization.id` (and analogous on `Person`)
is currently filled by the LLM during extraction, not minted at
composer-time. Sonnet has a mostly-stable convention (kebab-case with
`org-` prefix, sometimes `-oh` state suffix); mini has no convention.

Sample IDs for the same principal name:

| principal_name | sonnet | mini |
|---|---|---|
| AAA Club Alliance Inc | `org-aaa-club-alliance-inc` | `org:AAA_Club_Alliance_Inc` |
| American Chemistry Council | `org-american-chemistry-council-oh` | `org:american-chemistry-council` |
| Cleveland Browns | `org-cleveland-browns-oh` | `Cleveland Browns` |
| Friendship Circle of Cleveland | `org-friendship-circle-of-cleveland-oh` | `Friendship Circle of Cleveland` |
| Coinbase, Inc. | `oh-org-coinbase-inc` | `Coinbase, Inc.` |
| CNA | `org-cna` | `org-cna` |

Names match in every case. IDs are an inconsistent convention layer on
top of names. This is the kind of thing the composer should normalize,
not the extractor should be coached on — the brief is already
prescriptive about regime semantics; piling on an ID-format convention
adds prompt complexity that doesn't survive cross-model.

---

## What this supersedes from the 2026-06-13 findings doc

The 2026-06-13 doc proposed 5 next-session steps; this experiment
answers or revises 3 of them:

1. **"Pull briefv2 as the working base; remove bullet 8; confirm
   is_itemized returns to v2 behavior on the 100-slice (re-run full
   cross-arm, ~$0.66)."** — Re-run is unnecessary: this experiment uses
   briefv2 outputs directly, runs them through the chain composer, and
   confirms the chain artifact is structurally equivalent to sonnet on
   the form type the brief targets. The is_itemized field has zero
   structural impact on the chain TSV (it is a filing-level field, not
   a chain-row-level field), so even if briefv2's is_itemized behavior
   has issues, the chain artifact is unaffected. (The chain composer
   reads `filing.is_itemized` for the filings TSV, not the chain TSV;
   that's a separate concern.)
2. **"Composer-side: implement the Q1 description-hoist and Q2 zero-
   normalize at the Phase-1 classifier seam."** — **Partially revised.**
   The description-hoist (`POSITION_KIND_SUBJECT_HOISTED`) is already
   in the composer's classifier and accounts for only 2 of mini's 426
   chain rows — it was implemented during the OH chain composer
   landing on `oh-chain-composer` (PR #59), with a docstring citing the
   2026-06-13 findings doc. The *actual* residual mini-side mis-routing
   is the *opposite* direction: subject content placed in `bill_reference`
   rather than in `general_issue_area`. The composer-side rescue rule is
   to demote unmatched bill_referenced rows to subject_general when the
   bill_reference text contains no digits. Plan doc accompanying this
   findings doc specifies the implementation.
3. **"Defer the amendment-path / is_current-sweep work as a documented
   stub until a slice with amendments exists."** — Unchanged.

**Items not addressed by this experiment** (still owed for any
external doc):

4. **"Run the Q4 39-rid is_itemized-by-template follow-up ($0)."** —
   Still useful for an external doc, but no longer gates the chain
   release. The chain artifact is the load-bearing deliverable; the
   is_itemized story belongs in a filings-TSV writeup, not the chain
   writeup.
5. **"Reconcile the cost model's mini identity (which model = the
   $0.0066 measurement)."** — Required before *any* dollar figure
   appears in a Suhan-facing doc. Anchor: `~$0.0066/filing` measured
   2026-06-09; identity pinned by `MODEL_ID_DATED` in
   `src/lobby_analysis/oh_portal/extract_openai.py` (was
   `gpt-5-mini-2025-08-07` per the Day-2 runbook — verify it was the
   pin at measurement time). Per-token rate ($0.25/$2.00 input/output
   from Dan's `personal_info.md`) tied to the Aug-2025 model. The
   *current* cost-optimized mini is GPT-5.4 mini at $0.75/$4.50
   (~3× input). If the dollar figure is to mean anything, model id and
   per-token rate must tie to the same snapshot.

---

## Honest limitations

- **n=100 / 305.** The sonnet baseline is 305 filings; the briefv2 mini
  comparison is 100. Within the 100 shared rids the chain artifacts
  are structurally equivalent on LUPA. Extrapolating to the full 305
  (or to the eventual #35 full-corpus 45,605) assumes the LUPA pattern
  generalizes. The 100-rid sample was drawn across section types per
  the 2026-06-09 design, so the LUPA conclusion is on n=54 LUPA
  filings, not n=305.
- **No oh.csv lawmaker resolution.** The composer was run without the
  optional `--oh-csv` Open States legislator roster (gifts edges
  resolve to lawmaker IDs via this roster). Doesn't affect chain;
  affects gifts. Gifts are 0 across the board in this slice (PR #59
  empirical finding), so this is moot for the chain comparison.
- **Single model id, single brief revision.** Briefv2 only. Briefv3
  (with bullet 8) not tested against the composer because the
  2026-06-13 finding that it regresses is_itemized was already
  established; running it through the composer would not change the
  chain rows (is_itemized is not a chain field). If briefv3's `positions`
  emit behavior differs from briefv2 in some unexpected way, this
  experiment does not catch that. The 2026-06-09 cross-arm work
  established that briefv2→briefv3 was a single-bullet diff, and that
  bullet is is_current-related, not positions-related.
- **Q5 / OAC rule-number granularity untested.** The 2026-06-13 doc
  flagged that mini emits granular OAC rule numbers (`5160-46-XX`)
  where sonnet rolls them up. Whether the composer wants granular or
  rolled-up depends on the composer's intended OAC/JCARR edge
  granularity — Dan's call. This experiment does not resolve it.
- **No cost measurement in this experiment.** Composer is local-only;
  no API spend. The $0.0066/filing figure comes from the 2026-06-09
  dispatch and is subject to the cost-identity-reconciliation caveat.

---

## Provenance / reproducibility

**On-disk artifacts (in `~/data/lobby_analysis/`):**
- `oh_portal/extracted/<rid>/<uuid8>/filing.json` — sonnet baseline.
- `oh_portal/extracted_openai/<rid>/mini_medium_briefv2_*/filing.json`
  — mini briefv2 outputs.
- `oh_portal/extracted_briefv2_mini/<rid>/<run_id>/` — symlinks staged
  for this experiment. Safe to delete.

**Released artifact for comparison:**
- `releases/oh/chain/OH_chain_2025_2026_preview.tsv` on `main` (1,589
  rows from 305 filings, shipped via PR #59 at `ac009f5`).

**Generated artifact for comparison (NOT to commit — intermediate):**
- `/tmp/oh_release_briefv2_mini/chain/OH_chain_2025_2026_preview.tsv`
  (426 rows from 100 filings).

**Scripts** (currently at `/tmp/` paths; move to `scripts/` at commit
time if useful as fixture for the implementation plan; otherwise
delete after the experiment):
- `/tmp/stage_briefv2_mini.py` — stage briefv2 outputs into parallel dir.
- `/tmp/diff_mini_vs_sonnet_chain.py` — produce the per-section /
  row-set / cell-level diff tables.
- `/tmp/inspect_id_disagreement.py` — surface the model-emitted-ID
  story.
- `/tmp/inspect_chain_missing_v2.py` — characterize the 41
  zero-position filings.
- `/tmp/sonnet_vs_mini_by_section.py` — per-section position-count
  comparison.

**Reproduction**: from the `leave-behind-prep` worktree,
`uv run python /tmp/stage_briefv2_mini.py` (or whatever path the
scripts move to), then from `main` (where the composer code lives)
`uv run --active python -m lobby_analysis.allocation.oh.cli
materialize --extractions <abs-path-to-staged-dir> --bills
<abs-path-to-OH-136> --out <tmpdir>`, then run the diff scripts.

**Branch-state note for the next agent:** the OH chain composer code
(`src/lobby_analysis/allocation/oh/`) is on `main` (shipped 2026-06-15
via PR #59). It is NOT on `leave-behind-prep` — that branch is ~90
commits behind main. The implementation plan
(`plans/20260615_composer_side_mini_swap_normalizations.md`) addresses
the branch question explicitly.

---

## Decision recommendation

**Provisional ship-with-normalization recommendation.** Briefv2 mini is
the production OH extractor; chain composer takes responsibility for
entity-ID derivation (Step 1 of the implementation plan) and the
bill_referenced-unmatched demotion (Step 2). Cost: $0 new spend,
~half-day implementation. The remaining items (Q4 39-rid is_itemized
follow-up, cost-identity reconciliation, Q5 OAC granularity) are
required for an external Suhan-facing doc but not for an internal
lock-it decision on the chain artifact.

**What this recommendation does NOT cover:**
- Full-corpus run (#35 Batches API; ~$150 batched / ~$300 sync).
- The filings TSV (which carries is_itemized and total_expenditure
  cells where briefv3 vs briefv2 vs sonnet still have open
  conventions).
- Releasing a sonnet/mini-dual artifact (one shipped, one held).
