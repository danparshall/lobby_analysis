# σ_noise composition: WI vs OH — decomposition of pct_stable

**Date:** 2026-06-01
**Source plan:** [`../plans/20260601_post_phase3_followups.md`](../plans/20260601_post_phase3_followups.md) Item 6.
**Session convo:** [`../convos/20260601_phase3_followups_execution.md`](../convos/20260601_phase3_followups_execution.md).
**Source artifacts:**
- WI: 36 result JSONs under `tier_1/WI_2025/` (Phase 2 run, 2026-06-01).
- OH: 36 result JSONs under `docs/historical/extraction-harness-brainstorm/results/tier_1/` (post-Step-D state — 18 re-dispatched + 18 untouched; original 18 in `_superseded/`).

**Reproducibility:** [`sigma_noise_composition/sigma_noise_composition_oh_wi.py`](sigma_noise_composition/sigma_noise_composition_oh_wi.py) + saved output at [`sigma_noise_composition/output.txt`](sigma_noise_composition/output.txt). Zero API calls.

---

## TL;DR — three findings

1. **The cross-state OH→WI Δ in the Phase 2 convo is computed against a stale OH baseline.** The convo's "GPT-5.2 73.8% → 84.52%, +10.7 pts" uses the *pre-Step-D* OH GPT number. The Step D writeup explicitly warned its recomputed table is "a **mix** of 3 original-Tier-1 chunks and 3 post-fix chunks — it is not a clean re-measurement." Apples-to-apples baseline candidates: pre-fix OH GPT 73.8% (Δ=+10.7 pts), mixed post-Step-D OH GPT 79.76% (Δ=+4.76 pts). **No clean post-fix OH baseline exists**; Prong 1 was paused before a full OH re-dispatch.

2. **Within-state, the failure-mode mix differs sharply between Claude and GPT on WI.** Same headline % stable, very different compositions:
   - Claude WI: 72 stable / 9 value-unstable / **2 scoreability-unstable** / 1 incomplete.
   - GPT WI: 71 stable / 5 value-unstable / **7 scoreability-unstable** / 1 incomplete.
   - GPT's scoreability instability is **concentrated in `lobbying_definitions` (4 of 7)** — exactly where WI's qualitative §13.62(11) trigger lives.

3. **Claude's composition shifted OH → WI from scoreability-unstable toward value-unstable** (4→2 scor_un, 7→9 val_un), with identical headline % stable (85.71% both states). Worth flagging because the existing "Claude is state-invariant at this resolution" claim in the convo is true at the headline but masks composition movement underneath.

---

## Method

`tier1.classify_cell_runs` already emits four mutually exclusive stability classes per cell — `stable`, `value-unstable`, `scoreability-unstable`, `incomplete`. The headline σ_noise reads only `pct_stable = n_stable / n_cells`; this study reports all four counts side-by-side. No new code; the bundled script re-runs the existing classifier against the saved Tier-1 result JSONs.

For each state, every (model, chunk, run) saved JSON is loaded; per cell on the chunk's legal roster, an outcome list across the N=3 runs is assembled; `classify_cell_runs` classifies each cell; `summarize_sigma_noise` aggregates.

## Headline counts (n_cells = 84 in both states, 6 chunks, N=3)

| State | Model | stable | value-unstable | scoreability-unstable | incomplete | **pct_stable** |
|---|---|---:|---:|---:|---:|---:|
| **OH 2025** (post-Step-D, mixed) | claude-opus-4-7 | 72 | 7 | 4 | 1 | **85.71 %** |
| **OH 2025** (post-Step-D, mixed) | gpt-5.2-2025-12-11 | 67 | 11 | 5 | 1 | **79.76 %** |
| **WI 2025** | claude-opus-4-7 | 72 | 9 | **2** | 1 | **85.71 %** |
| **WI 2025** | gpt-5.2-2025-12-11 | 71 | 5 | **7** | 1 | **84.52 %** |

(The OH numbers replicate Step D writeup §"σ_noise (recomputed — read with care)" exactly: Claude 72/7/4/1, GPT 67/11/5/1. The replication itself is the consistency check on the script.)

## Δ (WI − OH, post-Step-D baseline)

| Model | Δstable | Δval_un | Δscor_un | Δincomp | Δpct_stable |
|---|---:|---:|---:|---:|---:|
| claude-opus-4-7 | +0 | **+2** | **−2** | +0 | +0.00 % |
| gpt-5.2-2025-12-11 | **+4** | **−6** | **+2** | +0 | +4.76 % |

**Read this with the caveat above.** The OH GPT baseline is "post-Step-D mixed" — 3 chunks re-dispatched after Fixes A/B/C, 3 chunks at original-Tier-1 state. If you compare against the original Tier-1 GPT OH (73.8 %), Δpct_stable = +10.7 pts (the figure in the convo). Neither comparison is clean.

## Per-chunk breakdown — scoreability-unstable concentration

For each (model × chunk × state), n_cells / stable / value-unstable / scoreability-unstable:

### Claude (state-invariant headline, composition shifts)

| chunk | n | OH s/v/sc | WI s/v/sc |
|---|---:|---|---|
| lobbying_definitions | 15 | 14 / 1 / 0 | 11 / 3 / 1 |
| lobbyist_spending_report | 30 | 29 / 1 / 0 | 26 / 4 / 0 |
| principal_spending_report | 23 | 19 / 4 / 0 | 22 / 1 / 0 |
| registration_thresholds | 6 | 1 / 0 / **4** | 5 / 0 / 0 |
| registration_mechanics_and_exemptions | 8 | 8 / 0 / 0 | 7 / 0 / 1 |
| enforcement_and_audits | 2 | 1 / 1 / 0 | 1 / 1 / 0 |

Claude's OH **scoreability-unstable=4 was entirely in `registration_thresholds`** — the OH qualitative-trigger chunk that drove Tier-2 Step D in the first place. On WI, Claude's `registration_thresholds` scoreability is 0 (after a single `incomplete` from the `TimeThresholdCell` instantiation failure, item 1 of this branch's followups). The 2 WI scoreability-unstable cells migrated to `lobbying_definitions` (1) and `registration_mechanics_and_exemptions` (1).

### GPT (visible headline change, composition shift)

| chunk | n | OH s/v/sc | WI s/v/sc |
|---|---:|---|---|
| lobbying_definitions | 15 | 11 / 4 / 0 | 9 / 2 / **4** |
| lobbyist_spending_report | 30 | 27 / 1 / 1 | 29 / 0 / 1 |
| principal_spending_report | 23 | 18 / 4 / 1 | 22 / 1 / 0 |
| registration_thresholds | 6 | 5 / 0 / 1 | 4 / 0 / 1 |
| registration_mechanics_and_exemptions | 8 | 6 / 1 / 1 | 6 / 1 / 1 |
| enforcement_and_audits | 2 | 0 / 1 / 1 | 1 / 1 / 0 |

**GPT's WI scoreability-unstable=7 is dominated by `lobbying_definitions` (4 of 7).** This is the chunk that asks "who counts as a lobbyist / what counts as lobbying" — and where WI's §13.62(11) "5 days within a reporting period" qualitative trigger sits. GPT was abstaining inconsistently across runs on the definitional questions; the WI statute structure made that worse than OH.

The other 3 GPT scoreability-unstable cells on WI are spread one each across `lobbyist_spending_report`, `registration_mechanics_and_exemptions`, `registration_thresholds`.

## Why the two interpretations matter

The existing Phase 2 convo (line "The 10.7-point shift is mostly composition. GPT's `n_scoreability_unstable=7` vs Claude's `2`…") makes the right qualitative call — GPT and Claude have different failure-mode mixes — but conflates two things:

- **Cross-state**: 73.8 % → 84.52 % is not a clean cross-state measurement (different post-fix state).
- **Within-state cross-model**: Claude vs GPT on WI is a clean comparison and shows the real finding (2 vs 7 scoreability-unstable).

The within-state cross-model finding is the load-bearing one. The cross-state finding is conditional on a baseline that doesn't fully exist.

## Implications for v2.2 metric design

1. **Report all 4 components alongside the headline.** A single `pct_stable` masks two qualitatively different failure modes (value disagreement vs scoreability disagreement) that have different downstream consequences. The v2.2 metric should surface the breakdown.

2. **Scoreability-unstable cells need different handling from value-unstable cells.** A value-unstable cell is a "which number is right?" problem (debuggable via Citations API per item 3, or via per-run statute-text capture). A scoreability-unstable cell is a "should this even be scored?" problem — closer to abstention-calibration than to extraction accuracy.

3. **Per-chunk breakdowns matter.** Aggregate σ_noise loses signal — the WI GPT scor_un=7 looks moderate as a headline (8.3 % of cells) but reads as "4 of 15 cells in `lobbying_definitions` are scoreability-unstable" (26.7 % of that chunk), which is a much stronger signal. The chunk-level cut shows *where* the model uncertainty concentrates, which is where the schema and prompt redesign effort should land.

4. **Need a clean cross-state baseline.** This study cannot give one. The minimum unblocking measurement is a single full OH re-dispatch with all current Fixes A/B/C in place (~$2.50 wall-time per the WI run cost). That would also unblock honest σ_noise tracking on MI when MI lands.

## Open question — recommend surfacing to Dan

Should the Phase 2 convo be amended to flag the baseline issue? Currently it asserts +10.7 pts as the cross-state Δ; with the post-Step-D baseline, it's +4.76 pts; with no clean baseline, neither is "right." Not amending leaves a misleading number in the canonical convo doc; amending invites a rewrite of "Claude is state-invariant" framing.

## Acceptance criteria from the plan

- [x] Decomposed `pct_stable` into the 4 stability-class components per (state, model).
- [x] Compared across OH and WI; computed deltas.
- [x] Surfaced the GPT scor_un OH→WI movement (5→7, +2) and re-attributed the chunk concentration (`lobbying_definitions`, 4 of 7).
- [x] Flagged the cross-state baseline issue with the Phase 2 convo.
- [x] No API spend; pure analysis of existing artifacts.
