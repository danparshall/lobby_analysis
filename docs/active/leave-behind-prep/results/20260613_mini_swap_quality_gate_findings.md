# gpt-5-mini swap — quality-gate findings (checkpoint, 2026-06-13)

**Status: provisional findings, not a locked decision.** We expect to make
changes (brief and/or composer-side) and re-run. This records what the
2026-06-12/13 spotcheck + diagnostic round established, what it did *not*, and
the current leaning on each open question, so the next implementation session
starts from evidence rather than re-deriving it. Nothing here is final;
treat the "leaning" lines as the current best read, revisable on new data.

Inputs: spotcheck scripts (`scripts/gpt5mini_oh_300slice_{is_itemized,
total_expenditure,positions}_spotcheck.py`, commit bfdb8b6), their stdout
(`results/20260612_gpt5mini_quality_gap_checks/`), the diagnostics convo
(`convos/20260612_gpt5mini_quality_gap_checks.md`), and the briefv2→v3 prompt
diff (`git diff 4d0c930 211c576 -- .../extraction_brief.py`). Comparison set
throughout: 100 report_ids, sonnet ∩ medium_briefv3, unless noted.

---

## TL;DR

- The is_itemized "regression" is **brief-caused, not model-caused.** The
  entire briefv2→v3 change is a single new bullet (an `is_current` default-True
  rule); it is the sole source of mini's is_itemized abstention. Confirmed by
  the diff plus the 5-rid hand-read (all GROUND_TRUTH_EMITS, briefv3 wrongly
  abstains).
- The field bullet-8 was *added to fix* (`is_current`) **has no variance in the
  live corpus** — the 100-rid slice is 100% `filing_action='original'`,
  100% `supersedes=None`. So bullet 8 spent prompt complexity (and caused a
  real regression on a field that *does* vary) to manage a non-problem in the
  shippable data.
- Current leaning: **base on briefv2, drop bullet 8, set is_current via the
  schema default (True)** for the all-original regime; push the contested
  conventions (positions field-placement, stated-zero totals) to the
  composer/consumer layer rather than into further brief revisions. This is a
  leaning, not a lock — see caveats per question.
- The "stop tuning the brief" through-line: 3 of 5 open questions resolve to
  consumer/composer conventions, not extraction defects. The one genuine
  regression (is_itemized) is best removed (drop bullet 8), not balanced (v4).

---

## What the brief diff actually showed (the core finding)

briefv2→v3 (`4d0c930`→`211c576`) is exactly one new bullet:

> 8. Default is_current to True for original filings. Set is_current=False ONLY
>    if the source explicitly indicates the filing has been superseded ...
>    Absence of evidence is not evidence of supersession ... when in doubt,
>    leave it True.

Mechanism (now concrete, replacing the convo's tentative "step-8" guess):
this bullet teaches a general *abstain-when-uncertain* disposition ("when in
doubt, leave it [at default]"), and the adjacent bullet (renumbered 8→9) cites
**Section II.D Meals** as its worked example — the exact JLEC ethics-form
section the 5 is_itemized regressions live in. The model generalized "default
when uncertain" from is_current to the neighboring optional field discussed in
the next bullet. This is the structural coupling in concrete form: optional-
field emission is governed by one disposition, and a prescriptive bullet aimed
at field X shifts the global emit-vs-abstain threshold, moving field Y with it.

**Important scope note on the coupling:** it perturbs *optional/derived field
emission only*. The 100%-validated structural fields (filing_id, dates,
filer_role, gifts, expenditure line-items, bill references) are read from fixed
form slots and are not disposition-governed. The coupling is a problem for
*brief iteration*; it is largely neutralized by moving contested conventions to
deterministic consumer-side code.

---

## Per-question findings and current leaning

### Q3 (gating) — is_itemized regression & whether v3 ships

**Finding.** Single isolable bullet (above) is the sole cause. Hand-read of the
5 v2-emits/v3-abstains rids: all GROUND_TRUTH_EMITS, ground-truth value present
in source, briefv3 wrongly abstains. All 5 have len(expenditures)==1 (NOT empty
Section II), so the "empty section → abstention correct" shortcut does not
apply — the abstention is a real miss.

**is_current is recomputable / non-varying.** Laptop check: 100-rid slice is
all `filing_action='original'`, all `supersedes=None` — by construction of the
OH portal's active-AER public view. Within this regime
`is_current=True` (schema default) is complete and correct.

**Caveat — do not over-read the agent's "matches sonnet 100/100."** On an
all-original slice the proposed rule `(filing_action=='original' AND
supersedes is None)` evaluates `True AND True → True` for every row; it has
never exercised the False branch. The 100/100 match is a tautology on
zero-variance data, not validation of the rule's amendment behavior. The
`filing_action`/`supersedes` corpus-sweep is the *right design for when
amendments appear*, but it is future-work, untested, and should not be
presented as validated.

**Current leaning.** Base production on briefv2; drop bullet 8; is_current via
schema default for the all-original regime. Prefer *removing* the coupled
instruction over authoring a v4 to counterbalance it. NOT a lock — if the next
slice/vintage contains amendments, re-validate before extending (see Limits).

### Q1 (positions) — field-placement divergence

**Finding.** All 13 positions divergences are in the executive-agency / OAC-rule
/ subject-category class; **zero disagreements on legislative HB/SB references**
in this slice (one apparent exception, 1394434, resolved in Q5/diagnostics:
HB 29 is in source — mini correct). Diagnostic #2 confirmed the '(NO BILL)'
rows are mini placing subjects in `description` rather than `general_issue_area`
— a schema slot tie-break the brief never specified, not information loss.

**Current leaning.** Composer-side normalization, not a brief edit. Rule:
*if `general_issue_area is None and bill_reference is None and description is
not None`, hoist `description` into the subject slot* — unconditional when both
canonical slots are empty, no shape-heuristic (the convo's
"short-and-category-shaped" test misclassifies long agency strings like
1419016). Implement at the Phase-1 classifier seam where OAC routing already
lives, so there is one normalization point, not two.

### Q5 (rule numbers) — OAC granularity

**Finding, and a partial inversion of the "mini is lossy" story.** On 1438098,
mini emitted twelve `5160-46-XX` OAC rule citations; sonnet rolled them to one
subject row. The composer plan's Phase-1 classifier explicitly routes
`\d+-\d+-\d+` OAC citations to `oac_rule` (out of the Plural Policy bill join).
So mini's granular emission is **what the composer needs**; sonnet's rollup
silently drops ~11 regulatory-activity edges. For this composer, mini's
literalism is better, not worse.

**Caveat.** This depends on the composer actually wanting rule-level
granularity for the OAC/JCARR artifact. The plan implies it (separate routing);
Dan owns that design. If the gifts/OAC edge is meant to be subject-rolled, this
read flips.

### Q2 (total_expenditure stated-zero) — null vs 0.0

**Finding.** The 62 sonnet_only rids are uniform: `sonnet=0.0,
len(expenditures)=0/0` — nil filings where the form renders an explicit $0.00
total; sonnet reads the zero, mini abstains. The disqualifying class (mini
missing a stated *non-zero* total) is **empty** in this slice
(both_emit_disagree=0).

**Caveats.** (a) The `VERBATIM_IN_HTML` flag is near-vacuous for 0.0 (the string
"0.00" appears on every form), so the conclusion rests on the 62/62 signature,
not the regex. (b) Only **9** filings in this slice carry a non-zero total —
thin n; a real stated-non-zero miss would most likely surface only at full-
corpus scale.

**Current leaning.** Treat as a consumer-side convention: normalize
(null + empty expenditures) → 0.0 downstream, so nil filings sum correctly and
are distinguishable from genuinely-unknown. Not a brief fight. Keep
`both_emit_disagree` on the #35 full-run monitoring list given thin n.

### Q4 (sample size) — is the is_itemized read generalizable?

**Finding/leaning.** N=5 is decisive *for JLEC ethics forms* (the form header
literally says "Non-Itemized"), but that explicit signal is exactly why it may
not generalize to other OH templates where is_itemized is ambiguous. Note
sonnet itself emits is_itemized on only 39/100 — the field is low-coverage /
advisory-grade in *both* models regardless of brief.

**Cheap follow-up (recommended, $0, data on disk):** run the is_itemized
comparison across all 39 sonnet-emitting rids (not just the 5 v2/v3 split),
bucket by form template, and see whether the regression is JLEC-specific or
global. If JLEC-specific, the "fix" may be the consumer treating is_itemized as
populated-only-for-ethics-forms — no brief change at all.

---

## Cost (for the model-choice framing; verify before any external doc)

- Sonnet 4.6, Batches API + caching: measured reference ≈ **$800** full corpus
  (45,605 AERs).
- mini, medium effort, briefv2: measured ≈ **$0.0066/filing → ~$301** synchronous.
- Batched mini: OpenAI's Batch API is a confirmed flat **50% discount, 24h
  window, stacks with prompt caching** (multiple current pricing sources,
  2026-06). So batched ≈ **~50% of the measured synchronous figure** (~$150).
- **Open reconciliation before this goes in any Suhan-facing doc:** our docs
  label the model "gpt-5-mini" @ $0.25/$2.00 (the Aug-2025 GPT-5 Mini). The
  *current* cost-optimized mini is GPT-5.4 mini @ $0.75/$4.50 — ~3× input.
  The batched estimate is a clean halving of *whatever model the $0.0066
  measurement was actually taken against*; confirm which mini that was so the
  per-token rate and the dollar figure are tied to the measurement, not
  extrapolated.

---

## Honest limitations (what this round did NOT establish)

- **Amendment path untested.** The live slice has zero amendments, so neither
  the extractor's ability to *populate* `supersedes`/`filing_action` on an
  amended filing, nor the corpus-sweep is_current rule's False branch, has been
  exercised. Before extending beyond the all-original regime (new vintage, or a
  full #35 run reaching back to amended filings), re-validate both.
- **Thin non-zero-total n (9 filings).** The "no disqualifying total_expenditure
  miss" claim is from a small money-bearing subset; full-corpus is where a real
  miss would appear.
- **is_itemized generalization (Q4)** untested beyond JLEC forms.
- **Q5 OAC-granularity verdict** is contingent on the composer's intended
  granularity for the OAC/JCARR edge (Dan's call).
- **briefv2's own is_current behavior:** briefv2 reportedly emits ~6/100
  is_current=False "noise." Under the all-original regime the schema-default
  approach (drop the field decision from the model entirely, force True)
  sidesteps this, but it has not been separately validated that forcing True
  is correct for those 6 — confirm they are indeed originals.

---

## Suggested next-session shape (provisional)

1. Pull briefv2 as the working base; remove bullet 8; confirm is_itemized
   returns to v2 behavior on the 100-slice (re-run full cross-arm, ~$0.66 — do
   NOT trust a targeted re-test; that is how v2/v3 each looked clean before
   breaking a neighbor).
2. Composer-side: implement the Q1 description-hoist and Q2 zero-normalize at
   the Phase-1 classifier seam.
3. Run the Q4 39-rid is_itemized-by-template follow-up ($0).
4. Reconcile the cost model's mini identity (which model = the $0.0066
   measurement).
5. Defer the amendment-path / is_current-sweep work as a documented stub until a
   slice with amendments exists.

None of the above is committed; it is the current best path subject to the
caveats above and to Dan's design calls on the composer.
