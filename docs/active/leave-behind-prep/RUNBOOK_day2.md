# Day 2 operator runbook — gpt-5-mini 3x on OH 300-slice

Step-by-step for the local agent executing the dispatch + analysis.
The full plan with rationale is at
[`plans/20260608_gpt5mini_on_oh_300slice.md`](plans/20260608_gpt5mini_on_oh_300slice.md).

This runbook assumes:
- You are on branch `leave-behind-prep` at the latest commit that includes
  this file, `src/lobby_analysis/oh_portal/extract_openai.py`,
  `src/lobby_analysis/oh_portal/pipeline_openai.py`, and the scripts under
  `scripts/` (`gpt5mini_oh_300slice_{preflight,smoke_diff,dispatch,
  cost_check,analyze}.py`).
- The Sonnet 300-slice baseline already lives at
  `data/oh_portal/extracted/<report_id>/<run_id>/filing.json` and raw HTML
  at `data/oh_portal/raw/<report_id>/<timestamp>/raw.html`.
- `.env.local` has `OPENAI_API_KEY` set.
- **The worktree's venv is activated** (`source .venv/bin/activate` if
  not — your prompt should say `(lobby-analysis)`). The bare `python`
  invocations below assume this; without it, `python` resolves to system
  Python 3.9 and imports will fail. As a defensive alternative every
  command works with `uv run python …` instead, at the cost of a brief
  editable-install re-link each time.

## Phase 0 — Pre-flight (~15 min)

Each Phase 0 step is wrapped in a small operator script under `scripts/`
so the runbook stays free of `python3 -c "…"` blocks and quoted heredocs
(both fragile under the local Bash matcher's anti-obfuscation heuristics,
and easy to break silently when copy-pasted).

### 0.1 Confirm Sonnet baseline is on disk

```bash
python scripts/gpt5mini_oh_300slice_preflight.py --check baseline
```

The script:
- Counts subdirectories under `data/oh_portal/extracted/`.
- Spot-checks the first / middle / last report_id (deterministic, so
  re-runs are comparable across sessions).
- Surfaces any non-OH `state` value as a WARN.

Expected count is **305** (the "300-slice" name is approximate; the
on-disk baseline ended up with 305 clean filings). The dispatch enumerates
report_ids from this directory and will run mini against whatever is here,
so if the count drifts much from 305 surface it before continuing.

### 0.2 Confirm OpenAI SDK + key + dated model id

```bash
python scripts/gpt5mini_oh_300slice_preflight.py --check openai
```

The script loads `.env.local`, lists available `gpt-5-mini*` model ids,
and prints the **recommended pin** — the lexicographically latest dated
variant (e.g., `gpt-5-mini-2025-08-07`). To pin, edit
`src/lobby_analysis/oh_portal/extract_openai.py`:

```python
MODEL_ID_DATED: str | None = "gpt-5-mini-2025-08-07"  # <- replace with the recommended id
```

Commit this pin so the 3 dispatch passes reference the same model snapshot
(undated `gpt-5-mini` rotates under the hood and would confound the
self-consistency measurement).

### 0.3 Run the new tests

```bash
uv run pytest tests/test_oh_portal_extract_openai.py tests/test_gpt5mini_300slice_analyze.py -v
```

All 9 tests should pass before proceeding.

### 0.4 Single-filing smoke + diff (Phase 1 step 8)

```bash
python scripts/gpt5mini_oh_300slice_smoke_diff.py
# or: python scripts/gpt5mini_oh_300slice_smoke_diff.py --report-id 1427844
```

The script runs mini once against the hand-validated baseline filing
1427844, diffs against the Sonnet output, and checks four invariants
(`state=='OH'`, `filer_person.name=='Nathan Aichele'`, `len(positions)==4`,
`len(expenditures)==1`, `expenditures[0].amount==20.0`).

Exit codes:
- `0` — all invariants hold; smoke output is auto-cleaned so it doesn't
  contaminate the 3-run dispatch.
- `1` — at least one invariant failed; smoke output is **left in place**
  for inspection at `data/oh_portal/extracted_openai/1427844/mini_smoke_*`.
- `2` — top-level shape diverges (different keys, wild array-length
  mismatch). Engineering bug in the adapter, not a model finding. Fix and
  re-run before Phase 2.

Pass `--no-cleanup` to keep the smoke output on success (useful when
hand-eyeballing the JSON).

## Phase 1 — Engineering (~45-90 min)

Already done in this session — `extract_openai.py`, `pipeline_openai.py`,
the two scripts, and the tests are committed. Phase 0.4 above is the
plan's Phase 1 step 8 manual diff. If Phase 0.4 passed, move to Phase 2.

**Hard stop (plan):** if Phase 1 (extending the extractor for any
schema-translation issue, prompt adjustment, etc.) eats 3 hours of wall
clock, stop and write up the engineering blocker. Do NOT continue to
Phase 2.

## Phase 2 — Dispatch (~2-3 hr wall-clock)

### 2.1 Run 1

```bash
mkdir -p data/oh_portal/extracted_openai
python scripts/gpt5mini_oh_300slice_dispatch.py \
  --pass 1 \
  --wall-clock-cap 10800 \
  --out-summary data/oh_portal/extracted_openai/_summary_run1.json \
  2>&1 | tee data/oh_portal/extracted_openai/_log_run1.txt
```

When Run 1 completes the script will print a post-run sanity diff against
Sonnet (counts of fields where mini's null-rate diverges from Sonnet by
>10%). **Review this output before launching Runs 2+3.** If fields show
huge null-rate divergence (e.g., mini emits null on `total_compensation`
in 90% of filings while Sonnet populated it in 50%), this is a finding
worth investigating before burning more API spend.

If the sanity diff looks clean, continue:

### 2.2 Runs 2 and 3

```bash
python scripts/gpt5mini_oh_300slice_dispatch.py \
  --pass 2 \
  --wall-clock-cap 10800 \
  --out-summary data/oh_portal/extracted_openai/_summary_run2.json \
  2>&1 | tee data/oh_portal/extracted_openai/_log_run2.txt

python scripts/gpt5mini_oh_300slice_dispatch.py \
  --pass 3 \
  --wall-clock-cap 10800 \
  --out-summary data/oh_portal/extracted_openai/_summary_run3.json \
  2>&1 | tee data/oh_portal/extracted_openai/_log_run3.txt
```

### Per-pass hard-stop (concern #1 from pre-dispatch review)

The `--wall-clock-cap 10800` arg gives each pass 3 hours before it aborts
gracefully. Partial outputs are retained. If Run N aborts mid-pass:

- Filings already extracted are in `data/oh_portal/extracted_openai/`
- The summary JSON records `aborted_early: true`
- The dispatch will NOT continue to Run N+1 automatically (it sees the
  short result list and stops)
- Phase 3 analyze can still run; it'll report `n_report_ids_compared`
  smaller than the full slice size (~305) and the metrics are over the
  subset that completed all 3 runs

If this happens, decide whether to:

- (a) Resume Run N by re-running the same command (idempotent — already-
  written filings are skipped via the resume logic)
- (b) Accept the partial result and proceed to Phase 3 with reduced N

### Cost watchdog

Run between passes to confirm we're inside the **$5** budget ceiling.
Expected per the plan is ~$3; meaningful overage suggests gpt-5-mini is
emitting far more output tokens than Sonnet, which is itself a finding
worth flagging.

```bash
python scripts/gpt5mini_oh_300slice_cost_check.py
# or with an explicit cap: python scripts/gpt5mini_oh_300slice_cost_check.py --budget-usd 5.0
```

The script reads `_summary_run{1,2,3}.json` from
`data/oh_portal/extracted_openai/`, prints per-pass and running totals,
and exits non-zero if the cumulative spend exceeds the cap.

## Phase 3 — Analysis + writeup (~60-90 min)

### 3.1 Run analyze

```bash
python scripts/gpt5mini_oh_300slice_analyze.py
```

Outputs:
- `docs/active/leave-behind-prep/results/20260608_gpt5mini_oh_300slice_metrics.json`
- `docs/active/leave-behind-prep/results/20260608_gpt5mini_oh_300slice_stable_disagreements.json`

The script prints the headline metrics + the pre-registered verdict to
stderr.

### 3.2 Hand-eyeball 10-20 stable disagreements (plan step 13)

Open `..._stable_disagreements.json`. For each of 10-20 examples (sampled
across report_ids, not all from the first one), open the cached HTML:

```bash
REPORT_ID=<from the JSON>
ls data/oh_portal/raw/$REPORT_ID/*/raw.html | head -1 | xargs less
```

Categorize each as:
- (a) mini consistently wrong (Sonnet right per source)
- (b) Sonnet wrong / mini right (mini converges past a Sonnet error)
- (c) ambiguous (both defensible interpretations)

Fill the table in the writeup template at
`docs/active/leave-behind-prep/results/20260608_gpt5mini_oh_300slice.md`.

### 3.3 Complete the writeup

Fill in all `<<FILL>>` markers in the writeup from the metrics JSON +
the summary JSONs. The verdict line comes verbatim from the analyze
script's stderr output (it's pre-registered, so don't second-guess it).

The "Recommendation for Suhan decisions doc" section is the only one
requiring your judgment — write a one-paragraph rationale referencing
the verdict + category mix.

### 3.4 Update STATUS.md

Update the `leave-behind-prep` row in the Active table on `STATUS.md`
with the day's work + headline result. Keep the cherry-pick-to-main
deferred to Day 5 per the existing 5-day plan.

### 3.5 Commit + push

```bash
git add docs/active/leave-behind-prep/results/20260608_gpt5mini_oh_300slice*
git add data/oh_portal/extracted_openai/_summary_run*.json  # if not gitignored
git add STATUS.md  # if updated
git commit -m "validation: gpt-5-mini 3x on OH 300-slice — <verdict-keyword>"
git push origin leave-behind-prep
```

Do NOT cherry-pick to main today. Day 5 wrap-up handles that.

## If anything blows up

- **Schema validation errors on every filing** → `LobbyingFiling` Pydantic
  schema may have grown a field that OpenAI strict mode rejects. Check the
  error message; the regression test
  `test_strict_schema_translates_without_error` should have caught it.
- **Rate limits (`openai.RateLimitError`)** → reduce concurrency (the
  current dispatch is serial; if rate-limited at serial it's a TPM/RPM
  cap issue — check the OpenAI dashboard, request increase if needed).
  The dispatch handles per-filing failures gracefully; one rate-limited
  filing won't abort the pass.
- **Cost run-away (>$5 total before Phase 3)** → stop and surface. Either
  mini's output tokens are much higher than the Sonnet baseline (worth a
  finding writeup) or pricing has changed (check
  `COST_PER_MTOK_*` constants in
  `scripts/gpt5mini_oh_300slice_dispatch.py`).
- **All 3 runs of mini agree but ALL stably disagree with Sonnet on every
  filing** → likely an extraction-brief interpretation difference, not 300
  independent errors. Look at the most common field path in the
  disagreements list and check the brief language for that field.

## Reminder on scope

This run answers **only**: does gpt-5-mini extract OH legislative AERs at
plausible quality, with self-consistency justifying further validation?

It does **not** answer:
- Is mini ready for `releases/oh/`? (needs hand-validation, n>=10)
- Is mini more accurate than Sonnet? (needs matched-N + ground truth)
- Does mini handle other OH regimes or other states? (out of scope)

Resist the urge to read more from the numbers than they support.
