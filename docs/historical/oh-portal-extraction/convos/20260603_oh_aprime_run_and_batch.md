# OH (A') first real run + (B') batch scaffolding

**Date:** 2026-06-03
**Branch:** `oh-portal-aprime-batch` (forked off `oh-portal-extraction` — run-and-PR, not a direct push to the parent branch)
**Machine:** Dans-MacBook-Pro (US network — this matters, see below)

## Summary

This is the session where the OH pipeline produced its **first real extracted
data**. Everything before today validated the plumbing against saved HTML; the
LLM extraction call had never actually fired (workspace quota cap until
2026-06-01). Today: the (A') single-filing round-trip ran end-to-end for real,
validated at **93.5% CORRECT / 0 WRONG → graduated**, and the (B') batch runner
was built test-first and proven on 3 real filings.

## The blocker that wasn't (anymore)

The long-running blocker was "OLAC times out from `requests.get`." This session
established that was an **outside-US connectivity problem, not a portal defense**:
from a US network the live `fetch_olac_aer` succeeded on the first try (8.7 KB,
fully server-rendered HTML, no JS/login wall). No VPN, no browser-save, no
manual download needed. The raw HTML Amina browser-saved on 2026-05-21 was never
synced to this machine, but it didn't matter — we just re-fetched live.

**Implication for (B'):** from a US-based machine (or US-hosted CI/cron), OLAC is
directly scrapable with the shipped `requests.get` path. The browser-save
workaround is only needed when running from outside the US.

## (A') validation — graduated

Sample: report 1427844 (Nathan Aichele / ARC Gaming &. Technologies, May–Aug 25).
Run `bd540187`, model `claude-opus-4-7`, 8.06s.

Result: **29/31 rows CORRECT (93.5%), 0 WRONG, 1 MISSING, 1 SCHEMA-GAP.**
Decision gate was ≥80% → **graduate to (B')**. Full tag table in
`results/20260507_oh_a_prime_validation.md`.

The two non-CORRECT rows are not extraction-quality failures:
- **SCHEMA-GAP — employer dropped.** `filer_organization=null`; "ARC Gaming"
  appears nowhere in the output. The model correctly declined to misfile the
  employer into `filer_organization` (that field denotes the filer, who here is
  Aichele the person), but the schema has no slot for the (agent, employer)
  tuple OH files under. **Confirmed systematic** — the two batch filings (HART,
  LKQ) dropped their employers too. This is the leading v1.4 gap.
- **MISSING — `is_itemized=null`** (true value `false`; Section D is headed
  "Non-Itemized"). Single prompt-fixable nit (one brief sentence). Not blocking.

Zero hallucinations, perfect on all 4 bills, correct Section-D collapse to one
`entertainment` row per brief rule 3, correct null discipline. Both pre-flagged
schema gaps reproduced exactly as predicted; neither is a model error.

## (B') batch runner — built test-first, proven on real data

New code (all under `src/lobby_analysis/oh_portal/`):
- **`pipeline.py`** — `extract_one_filing(url, data_dir, *, log)`: the single-
  filing fetch+extract+write, factored out of `__main__` so the CLI and the
  batch share one code path. `__main__.py` refactored to delegate to it
  (behavior preserved; same stderr logs + stdout path).
- **`batch.py`** — `find_existing_extraction` (resume guard, keyed on a written
  `filing.json`, not a bare directory), `run_batch` (skips already-extracted
  report_ids, isolates per-filing failures so one bad filing doesn't abort the
  batch), and a `cli_main` (`python -m lobby_analysis.oh_portal.batch <url>... |
  --file <path>`).
- **`tests/test_oh_portal_batch.py`** — 4 tests on the resume guard + the
  orchestration (skip / failure-isolation), using a real injected worker and a
  real tmp filesystem (no network/LLM mocking).

Real batch run over the 3 pre-vetted seeds:
- `1427844` (ARC Gaming) → **skipped** (resume guard hit the A' extraction)
- `1459616` (HART) → **extracted** — SB 299 (kratom), Sep–Dec 25, $3.50
- `1405684` (LKQ) → **extracted** — HB 54 / HB 96 / HB 210, Jan–Apr 25, $21.94
- 0 failed. Both new filings spot-checked clean against source.

Interesting: all 3 seeds are the **same agent** (Aichele), different employers —
an artifact of how they were vetted, and a vivid illustration of the employer-
tuple gap (one person, three employer filings, employer lost on all three).

## The real open question for (B'): filing-ID discovery

The batch runner consumes a **caller-supplied URL list**. We do not yet have a
way to **enumerate** the universe of OLAC `report_id`s — the 3 seeds were hand-
picked. "Grab OH data at scale" needs a discovery mechanism (OLAC index/search
reverse-engineering, or an agent/employer roster to walk). **Not built** — flagged
as the next decision rather than implemented unilaterally. This is the gating
item between "batch over known IDs" and "batch over all OH filings."

## Tests / hygiene

- oh_portal + batch: 15/15 pass. Full suite: 358 pass, 3 fail.
- The 3 failures are **pre-existing and data-only**: `test_pipeline.py` (Track A
  scoring) defaults to CA snapshot date `2026-04-13`, but the only CA snapshot
  synced to this machine is `2026-05-01`; that data is gitignored/local. Inherited
  from the branch point, untouched by this session's code. Flagged to Dan — fixing
  it means either a data sync or editing another track's shared test.
- ruff clean on all new/changed files.

## Decisions made

- **Fork-and-PR, not direct push** to `oh-portal-extraction` (Dan's call, even
  though the branch was already transferred to Dan per the 2026-06-03 handoff).
- **No unilateral v1.4 schema bump.** Employer-tuple gap + Section-D sub-rows
  documented for Dan/Gowrav review; not fixed in code.
- **Dedup over preserve-untouched:** factored `extract_one_filing` and rewired
  `__main__` rather than copy-pasting orchestration into the batch path.

## Open questions

- **(B') filing-ID enumeration** — the gating item above. How do we discover the
  report_id universe? (OLAC search endpoint vs. agent/employer roster.)
- Still open from 2026-05-07: SDK-vs-subagent-dispatch alignment with Track A;
  v1.4 schema-gap protocol (now with two concrete OH gaps as the first cases).

## Next steps

1. Dan decides on (B') enumeration approach.
2. v1.4 conversation (Dan/Gowrav): employer-tuple slot + Section-D sub-rows.
3. One-line brief tweak for `is_itemized=false` on Non-Itemized-only filings.
