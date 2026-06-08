# Day 2 operator runbook — gpt-5-mini 3x on OH 300-slice

Step-by-step for the local agent executing the dispatch + analysis.
The full plan with rationale is at
[`plans/20260608_gpt5mini_on_oh_300slice.md`](plans/20260608_gpt5mini_on_oh_300slice.md).

This runbook assumes:
- You are on branch `leave-behind-prep` at the latest commit that includes
  this file, `src/lobby_analysis/oh_portal/extract_openai.py`,
  `src/lobby_analysis/oh_portal/pipeline_openai.py`, and the two scripts
  under `scripts/`.
- The Sonnet 300-slice baseline already lives at
  `data/oh_portal/extracted/<report_id>/<run_id>/filing.json` and raw HTML
  at `data/oh_portal/raw/<report_id>/<timestamp>/raw.html`.
- `.env.local` has `OPENAI_API_KEY` set.

## Phase 0 — Pre-flight (~15 min)

### 0.1 Confirm Sonnet baseline is on disk

```bash
ls data/oh_portal/extracted/ | wc -l
# Expected: 300

# Spot-check 3 random filings have valid filing.json
for rid in $(ls data/oh_portal/extracted/ | shuf -n 3); do
  fj=$(find "data/oh_portal/extracted/$rid" -name filing.json | head -1)
  echo "=== $rid ==="
  python3 -c "import json; d=json.load(open('$fj')); print('state:', d['state'], 'filer:', (d.get('filer_person') or {}).get('name'), 'positions:', len(d.get('positions', [])))"
done
```

If `wc -l` is not 300, surface the gap before proceeding — the dispatch
enumerates report_ids from this directory.

### 0.2 Confirm OpenAI SDK + key

```bash
python3 -c "
import os
from openai import OpenAI
from src.lobby_analysis.oh_portal.env_local import load_env_local
load_env_local()
assert os.environ.get('OPENAI_API_KEY'), 'OPENAI_API_KEY not loaded'
c = OpenAI()
models = [m.id for m in c.models.list().data if 'gpt-5-mini' in m.id]
print('mini models available:', models)
"
```

If multiple dated suffixes (e.g., `gpt-5-mini-2026-XX-XX`) appear, **pick
the latest dated one** and set it on `MODEL_ID_DATED` in
`src/lobby_analysis/oh_portal/extract_openai.py`:

```python
MODEL_ID_DATED: str | None = "gpt-5-mini-2026-XX-XX"  # pin the dated version
```

Commit this pin so the 3 runs reference the same dated model.

### 0.3 Run the new tests

```bash
python3 -m pytest tests/test_oh_portal_extract_openai.py tests/test_gpt5mini_300slice_analyze.py -v
```

All 9 tests should pass before proceeding.

### 0.4 Single-filing smoke (Phase 1 step 8 — manual diff on 1427844)

Run mini once on the hand-validated baseline filing 1427844:

```bash
python3 -c "
from pathlib import Path
from src.lobby_analysis.oh_portal.env_local import load_env_local
from src.lobby_analysis.oh_portal.pipeline_openai import extract_one_filing_from_cache
load_env_local()
fp, usage = extract_one_filing_from_cache('1427844', run_label='mini_smoke', log=print)
print('written:', fp)
print('usage:', usage)
"
```

Diff against the Sonnet output:

```bash
# Find the Sonnet output for 1427844
SONNET_FJ=$(find data/oh_portal/extracted/1427844 -name filing.json | head -1)
MINI_FJ=$(find data/oh_portal/extracted_openai/1427844 -name filing.json | head -1)

# Structural diff — focus on top-level keys and array lengths
python3 << 'PY'
import json
sonnet = json.load(open("$SONNET_FJ"))
mini = json.load(open("$MINI_FJ"))
print('sonnet top-level keys:', sorted(sonnet.keys()))
print('mini top-level keys:  ', sorted(mini.keys()))
for k in ['positions', 'expenditures', 'engagements', 'gifts']:
    s = len(sonnet.get(k) or [])
    m = len(mini.get(k) or [])
    print(f'  {k}: sonnet={s}, mini={m}')
# Hand-validated invariants on 1427844:
print()
print('filer_person.name:', (mini.get('filer_person') or {}).get('name'),
      '(expected: Nathan Aichele)')
print('state:', mini.get('state'), '(expected: OH)')
print('len(positions):', len(mini.get('positions') or []), '(expected: 4)')
print('len(expenditures):', len(mini.get('expenditures') or []),
      '(expected: 1)')
exp = (mini.get('expenditures') or [{}])[0]
print('expenditures[0].amount:', exp.get('amount'), '(expected: 20.0)')
PY
```

**Stop and surface to user if:** top-level shape diverges (different
field names, missing keys), or if array lengths differ wildly (e.g., mini
emits 10 positions when Sonnet emits 4). That's an engineering bug, not a
model finding. Fix the adapter and re-run before Phase 2.

If invariants hold, delete the smoke output so it doesn't contaminate the
3-run dispatch:

```bash
rm -rf data/oh_portal/extracted_openai/1427844/mini_smoke_*
```

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
python3 scripts/gpt5mini_oh_300slice_dispatch.py \
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
python3 scripts/gpt5mini_oh_300slice_dispatch.py \
  --pass 2 \
  --wall-clock-cap 10800 \
  --out-summary data/oh_portal/extracted_openai/_summary_run2.json \
  2>&1 | tee data/oh_portal/extracted_openai/_log_run2.txt

python3 scripts/gpt5mini_oh_300slice_dispatch.py \
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
  smaller than 300 and the metrics are over the subset that completed all
  3 runs

If this happens, decide whether to:

- (a) Resume Run N by re-running the same command (idempotent — already-
  written filings are skipped via the resume logic)
- (b) Accept the partial result and proceed to Phase 3 with reduced N

### Cost watchdog

If the cumulative cost across summaries exceeds **$5** (budget ceiling),
stop and surface to user. Expected per the plan is ~$3; meaningful overage
suggests gpt-5-mini is emitting far more output tokens than Sonnet, which
is itself a finding worth flagging.

```bash
python3 -c "
import json
total = 0
for n in (1, 2, 3):
    try:
        s = json.load(open(f'data/oh_portal/extracted_openai/_summary_run{n}.json'))
        total += s['total_cost_usd']
    except FileNotFoundError:
        pass
print(f'total so far: \${total:.2f}')
"
```

## Phase 3 — Analysis + writeup (~60-90 min)

### 3.1 Run analyze

```bash
python3 scripts/gpt5mini_oh_300slice_analyze.py
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
