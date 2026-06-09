# gpt-5-mini OH 300-slice Day 2: Phase 0 hardening + partial Run 1

**Date:** 2026-06-09
**Branch:** leave-behind-prep

## Summary

Day 2 of the gpt-5-mini cost-floor validation per the 2026-06-08 plan
(`plans/20260608_gpt5mini_on_oh_300slice.md`). Session opened with an
unrelated environment problem — the worktree had no `.venv/`, so analysis
couldn't run — then moved into the RUNBOOK_day2 walkthrough. Several Phase 0
issues surfaced and were fixed along the way: the runbook itself had a bugged
quoted-heredoc that would have crashed step 0.4, the Sonnet baseline included
5 dev-fixture filings on a pre-`employer/extraction_warnings` schema, and
`_latest_filing_json` (in both dispatch.py and analyze.py) selected by lex
sort of bare-UUID run_ids rather than mtime — silently picking the wrong
run on any report with multiple extractions.

After all of Phase 0 passed cleanly, we launched Phase 2 Run 1 (3-pass
mini dispatch). About 13% in (55/305), surfaced that per-filing cost was
~$0.0070, projecting $317 for one full-corpus pass — 2-3× the plan's
$100-150 estimate. The Sonnet/mini ratio is still favorable (~2.5× cheaper)
but smaller than the 5-8× the plan hoped for; the driver is mini emitting
~3× more completion tokens per filing than Sonnet does (which uses
prompt-caching to keep the brief cheap). User direction was to stop and let
another agent take over after parallelizing the dispatcher (currently serial,
~32s per filing, would parallelize cleanly with ThreadPoolExecutor).

## Topics Explored

- Worktree env setup (`uv venv --python 3.12 && uv sync --extra dev`),
  including the cross-shell limitation that activation can't be propagated
  from one session to another
- RUNBOOK_day2.md walkthrough — found the quoted-heredoc bug in step 0.4
  (`python3 << 'PY'` with `$SONNET_FJ`/`$MINI_FJ` literals inside that
  wouldn't expand), plus several other `python3 -c "..."` blocks fragile
  under the local Bash matcher's anti-obfuscation heuristics
- Reframing the smoke-diff structural check — the original treated key-set
  asymmetry as a hard fail in both directions, which baked in "Sonnet is
  ground truth" against the explicit point of the experiment. User pushback
  led to symmetric WARN (key asymmetry is informational; only wild
  array-length divergence is a real extractor bug)
- The 5 legacy-schema baselines (1405684, 1427844, 1459616, 1492516, 1492518)
  — all extracted on June 3-4 morning before commit e5d2da3 added `employer`,
  `extraction_warnings`, `total_hours_communicating`, `total_hours_other`
  to LobbyingFiling. Decided to re-Sonnet those 5 rather than drop them
- `_latest_filing_json` bug: lex-sorting bare-UUID run_dirs effectively picks
  randomly. For 1492516 specifically, legacy `abc274e2` lex-sorted after
  the new modern-schema `62802a47` because `'a' > '6'` in ASCII, so even
  after re-Sonnet the analyze pipeline would have picked the wrong file.
  Trade-off discussion: rename-the-dir vs fix-the-code; chose code fix
  (mtime selection) + date-prefixed run_ids going forward
- Why mini cost is over plan estimate: looking at per-filing token usage
  (4,585 prompt + 2,933 completion average) vs the plan's implied ~850-1,300
  completion tokens. Sonnet $800 full-corpus baseline implies ~1,000 output
  tokens/filing with prompt caching, so mini is genuinely ~3× chattier
- User's check on the $800 Sonnet number — confirmed via the plan that
  it's a 1× full-corpus extraction cost (not 3×), so mini at $317 still
  wins by 2.5× but materially below the plan's leave-behind framing

## Provisional Findings

- **Mini per-filing cost is 2-3× the plan's projection** (n=55 filings).
  Driver: ~3× more completion tokens than Sonnet emits. Full-corpus
  projection moves from plan's $100-150 to actual $317. The Sonnet/mini
  ratio is real (~2.5× cheaper) but smaller than the 5-8× the plan implied.
- **Sonnet's $800 baseline implies prompt caching on the brief.** Without
  caching, the same-token Sonnet cost per filing would be ~$0.0574
  (4,580 input × $3/M + 2,912 output × $15/M), not the implied $0.0175.
  This is the structural lever that helps Anthropic vs OpenAI on this
  workload — and one we don't have an analog for on the mini side.
- **Mini extraction quality on the smoke filing looks fine.** All 4
  hand-validated invariants on 1427844 pass (state, filer name, positions
  count, expenditures count + amount). Mini correctly populates
  `extraction_warnings` with two thoughtful, accurate notes about the
  Section II.D sub-breakdown and the May-Aug25 reporting period inference
  — meta-awareness of its own interpretive choices.
- **The dispatcher works correctly serial.** 55 filings, 0 failures,
  consistent per-filing duration (~32s). The wall-clock blocker is purely
  HTTP latency to OpenAI, not anything in our code path.

## Decisions Made

- Patched RUNBOOK_day2.md to call new operator scripts instead of inline
  fragile shell. Added new scripts: `gpt5mini_oh_300slice_preflight.py`
  (steps 0.1 + 0.2), `gpt5mini_oh_300slice_smoke_diff.py` (step 0.4),
  `gpt5mini_oh_300slice_cost_check.py` (Phase 2 cost watchdog),
  `gpt5mini_oh_300slice_reconstruct_summary.py` (post-kill summary rebuild)
- Pinned `MODEL_ID_DATED = "gpt-5-mini-2025-08-07"` (only dated mini variant
  on the account)
- Re-extracted the 5 legacy-schema Sonnet baselines from cached HTML —
  305/305 baselines now on the modern schema
- Switched `_latest_filing_json` from name-sort to mtime-based selection
  in 4 places (dispatch.py, analyze.py × 2, smoke_diff.py)
- New run_ids are now date-prefixed (Sonnet: `YYYYMMDDTHHMMSS_<uuid8>`;
  OpenAI: `<run_label>_YYYYMMDDTHHMMSS_<uuid8>` to preserve the existing
  startswith() prefix filters)
- Smoke-diff structural check is now symmetric — key-set asymmetry in
  either direction is a WARN, not a hard fail (the original strict check
  implicitly treated Sonnet as ground truth)
- Stopped Run 1 at 55/305 after surfacing the cost/verbosity finding. Per
  user direction, another agent will parallelize the dispatcher before
  resuming.

## Results

- [`results/20260609_gpt5mini_oh_300slice_partial_run1.md`](../results/20260609_gpt5mini_oh_300slice_partial_run1.md)
  — partial Run 1 finding (cost, verbosity, what's on disk, resume path)

## Open Questions

- **What's driving mini's verbose completion tokens?** Possibilities listed
  in the results note (empty nested-entity full skeletons, long
  extraction_warnings, new schema fields populated even when source is
  silent). Hasn't been investigated yet — any one mini output vs the
  corresponding Sonnet baseline should make the diff visible.
- **Should the schema/brief be trimmed to reduce verbosity?** Trade-off
  is real: trimming nested-entity skeletons would cut mini output by
  maybe 30-50%, but might also reduce the field coverage we want from
  the validation. Worth a small experiment with a single filing.
- **Does the plan's leave-behind framing for Suhan need rewriting?** The
  decisions doc currently uses the $100-150 number; actual $317 changes
  the "opportunistic mini-based extraction" pitch. Not urgent — the
  validation still needs to complete first.
- **Cost watchdog timing.** The current `cost_check.py` only fires after a
  full pass completes — too late to prevent overage. A pre-spend projection
  watchdog (from per-filing average) would be a better gate. Out of
  scope for this session.

## Spend this session

~$0.72 total: $0.31 Anthropic (5 re-Sonnet runs for legacy-baseline cleanup)
+ ~$0.41 OpenAI (3 smoke runs + 55-filing partial Run 1).
