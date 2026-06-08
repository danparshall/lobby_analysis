# Plan: GPT-5-mini 3x cost-floor validation on OH 300-slice

**Date:** 2026-06-08
**Branch:** leave-behind-prep
**Owner:** Dan (with agent execution support)
**Status:** Draft, awaiting green-light on Day 2 displacement (see "5-day plan impact" below)

## What this answers

Does GPT-5-mini extract OH legislative-agent AERs at quality plausibly comparable to validated Sonnet-4-6, with enough self-consistency (σ_noise) to warrant further validation? If yes, post-Fellowship OH full-corpus extraction drops from ~$800 (Sonnet) to ~$100-150 (mini), a >5× cost reduction that materially changes whether `releases/oh/` can be produced opportunistically vs. as a budget-committed project decision.

## What this does NOT answer

- ❌ "Is mini ready to ship `releases/oh/` to production?" — that's a downstream question requiring hand-validation against source HTML on a sample of mini outputs, not just self-consistency + Sonnet-proxy agreement.
- ❌ "Is mini *more accurate* than Sonnet?" — we have Sonnet 1x only on this corpus; we can compare mini-3x to Sonnet-1x but cannot rank model accuracy without ground truth or matched-N.
- ❌ "Does mini handle other OH AER regimes (executive, retirement) or other states?" — scope is OH legislative only.

## Validation design

**Three mini runs over the same 300 filings used in `20260605_slice_validation_300.md`.** Compute:

1. **Mini self-consistency (σ_noise).** Per (filing, field), what fraction of mini's 3 runs agree? This is the metric Tier-1 reported (Claude 85.7%, GPT 73.8% on statute reading). For AER extraction we expect higher absolute numbers because the task is structurally simpler (fixed-section HTML tables, not statute prose interpretation).

2. **Mini-vs-Sonnet agreement (per mini run).** For each of the 3 mini runs separately, what fraction of fields match the existing Sonnet 300-slice output? Three agreement numbers, ideally tightly clustered.

3. **Stable-disagreement rate.** Fraction of fields where all 3 mini runs agree with each other but disagree with Sonnet. This is the most informative single metric — when mini is *consistently* different from Sonnet, that's either (a) mini systematically wrong on a known-type field, or (b) Sonnet wrong in an idiosyncratic way that 3-run mini converges past. Hand-eyeballing 10-20 examples should distinguish these.

**Asymmetric comparator caveat (explicit):** Sonnet is 1x here. We treat Sonnet's 300-slice output as a high-quality reference, not as ground truth. The 93.5% hand-validation on filing 1427844 supports this but it's n=1. The honest framing for the writeup: "mini converged or diverged relative to a single Sonnet run on the same 300 filings; this is a first-pass screen for plausibility, not a ranked accuracy comparison."

## Scope: OH legislative regime only

- ❌ No executive or retirement-system AERs
- ❌ No other states
- ❌ No exploration of GPT-5-nano or other cheaper tiers (focused single-model probe)
- ❌ No refactor of `extract.py` to share code with `extract_openai.py` — copy-paste is fine; refactor lives post-validation

## Time + cost budget

**Total: ~4-5 hours engineering, ~$3 API spend.**

- Phase 0 pre-flight: ~15 min
- Phase 1 engineering: ~45-90 min (OpenAI structured-output adapter is the risk)
- Phase 2 dispatch: ~2-3 hr wall-clock (serial; 3 runs × 300 filings × ~5s/filing minimum)
- Phase 3 analysis + writeup: ~60-90 min

**Hard stop:** if Phase 1 hits 3 hours without a working extractor, stop and write up the engineering blocker. The cost-floor question is real but not worth burning a Day-2 work block on infrastructure.

## 5-day plan impact (acknowledged)

Per the leave-behind-prep RESEARCH_LOG, Day 2 was scheduled for the cross-state CPI 5-state extension dispatch on `cross-state-cpi-2015-validation` (CO/IL/WA/FL/NC at vintage 2015, ~$15). At 4-5 hours, this validation work consumes most of a working day.

**Recommended cut: FOCAL Plans 3+4 (currently Day 4).** Rationale:
- FOCAL Plans 3+4 are clean Phase C closure work; the FOCAL rubric set already has Plans 1+2 shipped (legal-core + contact_log, per the 2026-05-22 weekly update); 3+4 are nice-to-have completeness for the projection-function suite, not load-bearing for any active research line.
- Cross-state CPI 5-state extension produces empirical N=10 trend data that *is* load-bearing — it informs whether the CPI 2015 trends from the N=5 run hold up at higher N, which is the question shaping Prong 1's resumption posture.
- OH chain composer (also Day 4) is more presentation-relevant than FOCAL Plans 3+4 and shouldn't be cut.

**Revised 5-day shape if approved:**
- Day 1 (2026-06-06, ✅ done): STATUS reconciliation + STATE_COVERAGE.md
- Day 2 (2026-06-08): **gpt-5-mini 3x validation** (this plan)
- Day 3 (2026-06-09): Cross-state CPI 5-state extension dispatch (~$15)
- Day 4 (2026-06-10): OH chain composer + `releases/oh/` (skip FOCAL Plans 3+4)
- Day 5 (2026-06-11): RESEARCH_ARC.md update + resumption brief + finish-convo on surviving branches

## Phase 0 — Pre-flight (~15 min)

1. **Confirm Sonnet 300-slice outputs on disk.** `ls data/oh_portal/extracted/ | wc -l` should show 300 filings, each with at least one `<run_id>/filing.json`. Spot-check 3 randomly-chosen filing JSONs to confirm structural validity.

2. **Confirm OpenAI SDK + key.** The `openai` package was added in commit `a7fbbb6` during Tier-0 work; check `pyproject.toml` confirms its presence. Source `.env.local` and verify `OPENAI_API_KEY` is set; do a trivial `client.models.list()` call to verify auth.

3. **Confirm model name.** As of June 2026, the relevant cheaper-tier OpenAI model is `gpt-5-mini` (per OpenAI docs / web). If `client.models.list()` returns a different version suffix (`gpt-5-mini-2026-XX-XX` etc.), use the dated version for reproducibility.

4. **Read the existing `extract.py` once more.** Specifically `extract.extract_oh_legislative_filing()` signature, return type, and how it invokes Anthropic's tool-use API. We're parallelizing this function shape, not refactoring it.

## Phase 1 — Engineering (~45-90 min)

5. **Create `src/lobby_analysis/oh_portal/extract_openai.py`.** Mirror `extract.py`'s public shape:
   ```python
   MODEL_ID = "gpt-5-mini"  # Or dated version from Phase 0 step 3

   def extract_oh_legislative_filing(html: str, *, run_id: str) -> LobbyingFiling:
       ...
   ```
   Implementation:
   - Import the existing `build_oh_legislative_brief()` from `extraction_brief.py` (same prompt content; testing model-difference not prompt-difference)
   - Use OpenAI's structured output: `client.chat.completions.create(model=MODEL_ID, response_format={"type": "json_schema", "json_schema": {...}}, ...)`
   - Translate `LobbyingFiling.model_json_schema()` (Pydantic v2) into OpenAI's expected `json_schema` shape — note OpenAI requires `additionalProperties: false` and named root schema
   - Parse the response into a `LobbyingFiling` via `LobbyingFiling.model_validate_json(response.choices[0].message.content)`
   - Match `extract.py`'s error handling shape (retry-on-transient, raise-on-schema-fail)

6. **Schema translation gotchas to handle up-front.** OpenAI's JSON-schema mode is stricter than Anthropic's tool-use:
   - All object schemas need `additionalProperties: false`
   - All properties must be in `required` array (use `null` types for optionals)
   - `$ref` resolution is supported but limited; may need to inline definitions
   - If Pydantic's auto-generated schema fails OpenAI's validator, use `client.beta.chat.completions.parse()` with a Pydantic class directly (this auto-translates and is the path-of-least-resistance)

   **Recommendation:** start with `client.beta.chat.completions.parse(response_format=LobbyingFiling)`. If that works, you've saved the manual schema translation entirely.

7. **Write 2 unit tests against captured Sonnet output for filing 1427844** (the hand-validated baseline at `data/oh_portal/raw/1427844/2026-06-03T19-31-18+00-00/raw.html`):
   - Test 1: `extract_openai.extract_oh_legislative_filing(html)` returns a structurally valid `LobbyingFiling` (parses without error, has expected nested types)
   - Test 2: The returned filing matches Sonnet's hand-validated invariants — `state == "OH"`, `filer_person.name == "Nathan Aichele"`, `len(positions) == 4`, `len(expenditures) == 1`, `expenditures[0].amount == 20.0`

   These tests are structural sanity, not full correctness. Goal: if Phase 1 ends with both tests green, the extractor is plausibly working and Phase 2 dispatch is safe to start.

8. **Manual diff of filing 1427844.** Run mini once on the cached HTML, diff its `filing.json` against Sonnet's `bd540187/filing.json`. **If structural shape diverges (different field names, missing top-level keys, etc.), STOP — engineering bug, not a model finding.** Fix the adapter and re-run before proceeding.

## Phase 2 — Dispatch (~2-3 hr wall-clock)

9. **Three serial runs of mini on the 300-slice.** Mirror `batch.py`'s loop but call `extract_openai.extract_oh_legislative_filing` instead. Outputs go to a parallel directory tree to avoid colliding with the Sonnet output namespace:
   ```
   data/oh_portal/extracted_openai/<filing_id>/<run_id>/filing.json
   ```
   Use distinct run_ids per pass — e.g., `mini_run_1_<sha>`, `mini_run_2_<sha>`, `mini_run_3_<sha>` — so per-run outputs are separable for analysis.

10. **Track per-run:**
    - Total cost (sum from `response.usage.prompt_tokens × $0.25/1M + completion_tokens × $2/1M`)
    - Wall-clock per filing + total
    - API errors (rate-limit, transient, schema-validation failures)
    - Any filing that errored in 1 or 2 runs but succeeded in others (interesting for stability analysis)

11. **Sanity check after Run 1.** Before launching Runs 2+3, spot-check 5 random filings' output for structural sanity. If many filings have null fields that Sonnet populated, or vice versa, surface — this is a finding *before* burning more API spend.

## Phase 3 — Analysis + writeup (~60-90 min)

12. **Compute the three headline metrics.** Operationally:
    - **Mini σ_noise:** for each (filing_id, field_path) tuple in the union of mini's 3 runs, did all 3 emit the same value? Aggregate to a per-field-type percentage and an overall percentage.
    - **Mini-vs-Sonnet per-run agreement:** for each mini run separately, what fraction of (filing_id, field_path) tuples match the corresponding Sonnet 300-slice value? Three numbers.
    - **Stable-disagreement rate:** fraction of (filing_id, field_path) tuples where mini's 3 runs all agree with each other and disagree with Sonnet.

    Field-path enumeration should include: top-level scalar fields, each `positions[]` row's fields, each `expenditures[]` row's fields. Array-length differences (mini emits 4 positions, Sonnet emits 3) need explicit handling — count as full-row disagreement rather than per-field.

13. **Hand-eyeball 10-20 examples of stable disagreement.** Categorize: (a) mini consistently wrong (Sonnet right per source), (b) Sonnet wrong / mini right (mini converges past a Sonnet error), (c) ambiguous — both defensible interpretations of source. This is the most informative analysis output and the part that can't be automated.

14. **Write `results/20260608_gpt5mini_oh_300slice.md`.** Required content:
    - Actual cost (vs $3 budget)
    - Wall-clock (vs ~2-3 hr expectation)
    - Cost projection to 45,605: `actual_300_cost × (45,605 / 300)` — this is the number for Suhan
    - The three headline metrics (σ_noise, per-run agreement, stable-disagreement rate)
    - Categorized examples of stable disagreement (10-20)
    - **Verdict** (written *before* eyeballing examples to avoid post-hoc rationalization):
      - σ_noise > 90% AND stable-disagreement < 10% → "plausibly viable, recommend follow-on hand-validation post-Fellowship"
      - σ_noise > 90% AND stable-disagreement 10-25% → "viable on consistency, needs hand-judgment on disagreement category mix before commitment"
      - σ_noise < 90% OR stable-disagreement > 25% → "not suitable at current setup; deeper investigation needed before further work"
    - Recommendation for Suhan decisions doc: which option (A: $800 Sonnet now / B: defer + mini path / C: don't extract) the result supports

15. **Update STATUS.md leave-behind-prep row** with the day's work + result.

16. **Commit + push.** Suggested message: `validation: gpt-5-mini 3x on OH 300-slice — <verdict>`.

## Explicit non-goals

- ❌ Don't run mini 1x and "infer" σ_noise from it (defeats the purpose)
- ❌ Don't compute Sonnet σ_noise from a single 300-slice run (1x sample, undefined)
- ❌ Don't try alternative briefs to improve mini's performance (we're testing the production brief, not optimizing for mini)
- ❌ Don't refactor for code reuse between `extract.py` and `extract_openai.py` (experiment-first; refactor lives post-validation when we know if mini is the production target)
- ❌ Don't extend to other regimes or states
- ❌ Don't hand-validate mini outputs against source HTML beyond the 10-20 stable-disagreement examples (that's the post-Fellowship work this plan is trying to *justify*)

## Open risks

- **OpenAI structured-output schema translation fails on the LobbyingFiling Pydantic schema.** Mitigation: try `beta.chat.completions.parse()` first; if it fails, manually flatten the schema. Worst case, this is Phase 1's blocker and consumes the full time budget; the hard-stop at 3 hours prevents Day 2 from being a complete loss.
- **Rate limits on a fresh-ish OpenAI account.** Mini is high-volume-friendly but TPM/RPM caps may bite. Mitigation: pace dispatch to 1 request/sec serially; if hitting caps, request quota increase or accept longer wall-clock.
- **Mini may use a different output token economy than Sonnet** (chattier or more terse), which affects cost projection. The 45,605-cost projection should use *actual* mini cost-per-filing, not assume the Sonnet baseline.
- **Asymmetric comparator (Sonnet 1x vs mini 3x) limits the claims we can make.** This is by design (cost trade-off) and the writeup is explicit about it. Risk: someone reads the result as "mini ranks against Sonnet on accuracy"; mitigation: make the framing limitation prominent in the writeup verdict.
- **Sonnet 1x might itself be noisy on some fields.** If we see stable mini disagreement, we can't rule out "Sonnet got it wrong this one time." Mitigation: the eyeball pass on 10-20 examples should distinguish; if many fall into "ambiguous / Sonnet might be wrong," that's its own valuable finding.
