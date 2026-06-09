# Handoff data — 2026-06-09 Day-2 partial Run 1

Tracked copy of session artifacts that normally live under gitignored
`data/oh_portal/`. Lets the next agent (or a re-clone of the repo on a
different machine) inspect this session's outputs without needing access
to Dan's cross-machine `~/data/lobby_analysis/` sync.

**Source of truth is still `data/oh_portal/`.** This copy is for
hand-off and verbosity investigation only — don't edit files here, and
treat it as read-only after restoration.

## What's here

```
handoff/
├── README.md                                       (this file)
├── mini_run_1_partial/                             55 mini extractions
│   ├── <report_id>/mini_run_1_<ts>_<uuid>/
│   │   ├── filing.json                             extracted LobbyingFiling
│   │   └── extraction_run.json                     per-filing metadata + usage
│   ├── _log_run1.txt                               full dispatch log
│   └── _summary_run1.json                          reconstructed via
│                                                   scripts/gpt5mini_oh_300slice_reconstruct_summary.py
│                                                   (dispatch was killed mid-pass; native
│                                                    summary isn't written on SIGKILL)
├── sonnet_re_extracted_legacy_fix/                 5 Sonnet baselines re-run THIS session
│   └── <report_id>/<uuid8>/
│       ├── filing.json                             modern-schema baseline
│       └── extraction_run.json
└── sonnet_baselines_sample/                        10 PRE-EXISTING Sonnet baselines
    └── <report_id>/<uuid8>/                        (for matched-pair mini-vs-Sonnet
        ├── filing.json                              verbosity comparison)
        └── extraction_run.json
```

55 mini extractions = first 55 of the 305-filing Sonnet 300-slice
(alphabetical-by-numeric-report-id order). 5 sonnet re-extractions =
the 5 legacy-schema baselines that were created June 3-4 *before* commit
`e5d2da3` added `employer` / `extraction_warnings` /
`total_hours_communicating` / `total_hours_other` to `LobbyingFiling`. The
10-sample is an evenly-spread selection across the 55 mini-extracted IDs
(skipping the 2 that already appear in `sonnet_re_extracted_legacy_fix/`)
so each sampled Sonnet baseline has a matching mini Run 1 output to
diff against. Provenance distinction matters: the 5 re-extracted are from
THIS session; the 10-sample comes from the original 300-slice extraction
and is just being copied here for portability.

## Restoring to `data/oh_portal/`

If you need the data back under `data/` so the dispatcher's `--resume`
logic can skip the 55 done filings, copy back like this from the repo
root:

```bash
# Mini Run 1 outputs (55 filings + log + summary)
mkdir -p data/oh_portal/extracted_openai
cp -r docs/active/leave-behind-prep/handoff/mini_run_1_partial/* \
      data/oh_portal/extracted_openai/

# Sonnet re-extracted legacy baselines (5 filings)
for rid in 1405684 1427844 1459616 1492516 1492518; do
  mkdir -p data/oh_portal/extracted/$rid
  cp -r docs/active/leave-behind-prep/handoff/sonnet_re_extracted_legacy_fix/$rid/* \
        data/oh_portal/extracted/$rid/
done

# Sonnet 10-sample (only useful if you don't already have the 300-slice
# baseline locally — these are copies of the original extraction)
for rid in 1394434 1396330 1399318 1400948 1402750 \
           1406694 1411320 1413012 1417306 1419738; do
  mkdir -p data/oh_portal/extracted/$rid
  cp -r docs/active/leave-behind-prep/handoff/sonnet_baselines_sample/$rid/* \
        data/oh_portal/extracted/$rid/
done
```

These commands are additive — they won't overwrite anything the
dispatcher has produced more recently (different run-ids), nor will they
clobber the other 300 Sonnet baselines you already have on disk if any.

## What this is NOT

- **Not the full Sonnet 300-slice baseline.** The other 300 modern-schema
  Sonnet baselines were produced by a session prior to 2026-06-09 and live
  in Dan's `~/data/lobby_analysis/oh_portal/extracted/` (via the data/
  symlink). If you don't have them, you'd need to either get them from
  Dan's machine or re-run the Sonnet pipeline (`pipeline.py`) on those
  300 report_ids' cached HTML.
- **Not raw HTML.** The OH portal raw HTML cache lives at
  `data/oh_portal/raw/<report_id>/<timestamp>/raw.html` — same sync-only
  situation. Mini's extractor reads from there via `find_cached_html`,
  not from the network.

## Why this matters for the next agent's task

The plan calls for parallelizing the dispatcher and resuming. With these
55 mini outputs restored, `--resume` skips them and dispatches the
remaining 250 fresh. Without them, dispatching from clean costs an
extra ~$0.39 and ~30 minutes wall-clock (at the current serial rate; ~5
min if parallelized).

For the verbosity investigation (mini's 2,933 avg completion tokens vs
plan's implied ~1,000), pick any `mini_run_1_partial/<rid>/...filing.json`
and diff against `data/oh_portal/extracted/<rid>/<latest>/filing.json`
(or `sonnet_re_extracted_legacy_fix/<rid>/...filing.json` for the 5
report_ids we re-ran here). The bulk of the difference should be
visible.
