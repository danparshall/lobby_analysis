# GPT-5-mini 3x validation on OH 300-slice — results

**Date:** 2026-06-08
**Branch:** leave-behind-prep
**Plan:** [`plans/20260608_gpt5mini_on_oh_300slice.md`](../plans/20260608_gpt5mini_on_oh_300slice.md)
**Sonnet baseline:** [`oh-portal-extraction/results/20260605_slice_validation_300.md`](../../oh-portal-extraction/results/20260605_slice_validation_300.md)

> Template populated by the analyze script. Values inside `<<FILL>>` markers
> are placeholders — replace with values from
> `20260608_gpt5mini_oh_300slice_metrics.json` (the script also prints them
> to stderr at the end of its run). Sections marked **TODO (hand)** require
> manual judgment that can't be automated.

## Pre-registered verdict thresholds

Set in the plan **before** any data was collected, to prevent post-hoc
rationalization:

- σ_noise > 90% AND stable-disagreement < 10% → **plausibly viable**, recommend follow-on hand-validation post-Fellowship.
- σ_noise > 90% AND stable-disagreement 10-25% → **viable on consistency, needs hand-judgment** on disagreement category mix before commitment.
- σ_noise < 90% OR stable-disagreement > 25% → **not suitable at current setup**; deeper investigation needed before further work.

The analyze script applies these and prints the verdict to stderr.

## Execution

| Item | Value |
|---|---|
| Date executed | <<FILL: YYYY-MM-DD>> |
| Model | `gpt-5-mini` (dated version: <<FILL: gpt-5-mini-2026-XX-XX>>) |
| Provider | OpenAI |
| Prompt | identical to Sonnet baseline (`build_oh_legislative_brief`, sha <<FILL>>) |
| Schema enforcement | OpenAI structured outputs, strict mode, `response_format=LobbyingFiling` |
| Filings per run | <<FILL: 300 expected>> |
| Runs | 3 (`mini_run_1`, `mini_run_2`, `mini_run_3`) |
| Source HTML | reused from Sonnet 300-slice cache (no OLAC re-fetch) |

## Cost + wall-clock

| Item | Value | Plan budget |
|---|---|---|
| Total cost | $<<FILL>> | ~$3 (ceiling $5) |
| Total wall-clock | <<FILL>> min | ~2-3 hr expected, 3 hr per-pass cap |
| Per-filing avg | <<FILL>> s | (Sonnet baseline 15.6 s) |
| Per-run prompt tokens (mean of 3) | <<FILL>> | |
| Per-run completion tokens (mean of 3) | <<FILL>> | |

**Projection to full corpus (45,605 AERs):**

$$\text{projected\_cost} = \text{actual\_300\_cost} \times \frac{45605}{300} = \$<<FILL>>$$

Sonnet baseline projection was ~$800 (with Batches API + caching). Mini-tier
projection is the cost-floor candidate for the leave-behind decisions doc.

## Headline metrics

(From `20260608_gpt5mini_oh_300slice_metrics.json`. Definitions in the plan,
section "Validation design".)

| Metric | Value | Interpretation |
|---|---|---|
| n field-paths compared | <<FILL>> | |
| **Mini σ_noise** | <<FILL: 0.XX>> | All 3 mini runs emit the same value |
| Mini run 1 vs Sonnet | <<FILL: 0.XX>> | Asymmetric (Sonnet 1x; not ground truth) |
| Mini run 2 vs Sonnet | <<FILL: 0.XX>> | |
| Mini run 3 vs Sonnet | <<FILL: 0.XX>> | |
| **Stable disagreement rate** | <<FILL: 0.XX>> | mini self-consistent AND disagrees with Sonnet |

**Asymmetric-comparator note (re-stated from plan):** Sonnet is 1x. We treat
the existing Sonnet 300-slice output as a high-quality reference, not as
ground truth. The 93.5% hand-validation on filing 1427844 supports this but
is n=1. The mini-vs-Sonnet numbers cannot be read as "mini ranks X% as good
as Sonnet" — Sonnet's own σ_noise is unknown on this corpus.

## Per-field-type breakdown

Aggregate σ_noise can mask wide field-type variance — currency amounts may
hit 99%+ while free-text descriptions sit at 70%. The per-field-type table
from `metrics.json` field `by_field_type` is the right thing to scan.

<<FILL: top 5 highest-σ_noise field types, top 5 lowest, top 5 stable-disagreement>>

## Stable-disagreement category mix — **TODO (hand)**

Per plan step 13, hand-eyeball 10-20 examples from
`20260608_gpt5mini_oh_300slice_stable_disagreements.json`. Categorize each:

- **(a) Mini consistently wrong** — Sonnet right per source HTML
- **(b) Sonnet wrong / mini right** — mini converges past a Sonnet error
- **(c) Ambiguous** — both defensible interpretations of source

Open the cached `data/oh_portal/raw/<report_id>/<latest>/raw.html` for each
example, decide the category, fill in below:

| # | report_id | field_path | sonnet | mini | category | notes |
|---|---|---|---|---|---|---|
| 1 | <<FILL>> | <<FILL>> | <<FILL>> | <<FILL>> | (a/b/c) | <<FILL>> |
| 2 | ... | | | | | |
| ... | | | | | | |

**Category counts:** (a) <<FILL>>, (b) <<FILL>>, (c) <<FILL>>.

Interpretation guide:
- Mostly (a) → mini is making systematic errors; cost-floor work needs prompt
  iteration or model upgrade before full corpus
- Significant (b) → Sonnet 1x is noisier than the 93.5% hand-validation
  suggested; consider a partial 2nd Sonnet run to bound Sonnet σ_noise
- Mostly (c) → both models are operating within reasonable interpretation
  bounds; the "disagreement" is partly schema ambiguity, not model error

## Pre-registered verdict (computed)

<<FILL: copy the verdict string from the analyze script's stderr output>>

## Recommendation for Suhan decisions doc

The OH extraction strategy options framed in the planning convo:

- **A** — Dispatch Sonnet at $800 now for Fellowship-end `releases/oh/`
- **B** — Defer ~3 weeks, validate mini-tier first (this work), full corpus
  post-Fellowship at ~$<<FILL: projection>>
- **C** — Don't extract; answer questions on-demand via slice extraction

Pre-Day-2 agent recommendation was (B) on cost-efficiency grounds unless
Analogy has strategic reason to need OH as a Fellowship-end artifact.

**Updated recommendation based on this work:** <<FILL: A / B / C, with one-paragraph rationale referencing the verdict + category mix>>

## Methodology notes (for reviewers)

- **Array-row alignment.** Rows in `positions[]`, `expenditures[]`,
  `engagements[]`, `gifts[]` are aligned across providers by identity keys
  (e.g., `(category, recipient_name, expenditure_date)`), NOT by the
  measured fields (`amount`, `value`). This avoids the trap where a
  same-row-different-amount disagreement gets split into two phantom rows.
  Regression test:
  `tests/test_gpt5mini_300slice_analyze.py::test_amount_disagreement_on_same_row_surfaces_as_one_disagreement`.
- **Rows present in only one provider** count toward disagreement (every
  field of the missing row is a stable disagreement with mini values=null).
  Per plan's "array-length differences count as full-row disagreement."
- **Excluded fields.** `raw_text`, `provenance`, top-level `id`, and per-row
  `provenance` are excluded from comparison — they're pipeline-stamped, not
  extracted, so they'd trivially disagree across providers without telling
  us anything about model behavior.
- **Filings used.** Intersection of (Sonnet 300-slice) and (filings where
  all 3 mini runs completed). Filings where any of the 3 mini runs failed
  are excluded from the metrics; the dispatch summary lists their report_ids
  separately.
- **Source identical.** Mini reads from the cached `raw.html` the Sonnet
  baseline used (June 4-5 OLAC fetch), so OLAC drift cannot contaminate the
  comparison.

## Known limitations of this work

1. **n=1 Sonnet reference.** Stable disagreement cannot be cleanly attributed
   to mini-error vs Sonnet-error without ground truth. The category-mix
   eyeball pass is the closest we get.
2. **Same prompt for both providers.** No prompt-engineering for mini.
   Production mini deployment might benefit from a mini-specific prompt
   (different output structure, more aggressive null-handling guidance).
3. **OH legislative regime only.** Says nothing about executive, retirement,
   or other states.
4. **OpenAI structured-output strict mode** forces all fields into `required`
   with nullable types. Sonnet's tool-use API has slightly different
   constraints. Some "stable disagreement" may reflect the model behaving
   differently under strict-mode constraints than under tool-use, not
   model-capability differences.

## Next steps if verdict is "plausibly viable" or "viable on consistency"

1. Hand-validate a 20-50 filing subset of mini outputs against source HTML
   (post-Fellowship work). The 93.5% Sonnet hand-validation was n=1; mini
   needs its own n>=10 anchor before committing to a $100-150 full-corpus run.
2. Consider a partial 2nd Sonnet run (e.g., 50/300 filings) to bound Sonnet
   σ_noise — the asymmetric-comparator caveat is much less limiting if we
   have even a coarse Sonnet noise floor.
3. If both pass, proceed to full-corpus mini extraction via OpenAI Batch API
   (50% discount, similar shape to Anthropic Batches).
