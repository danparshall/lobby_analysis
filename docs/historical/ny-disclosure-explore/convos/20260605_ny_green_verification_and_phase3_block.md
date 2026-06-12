# NY — green-claim verification + Phase-3 egress block

**Date:** 2026-06-05
**Branch:** ny-disclosure-explore

## Summary

Picked up the prior session's handoff: settle the owed green claim with a
networked `pytest` run, then do the Phase-3 real pull (`client_semiannual` 2025
bulk CSV → `materialize_cli`) and write `releases/ny/README.md` from the real
aggregates.

**The green claim is now settled; Phase 3 is blocked in this environment.**

This session ran in a sandbox whose bash egress proxy allows GitHub + PyPI but
**not** `data.ny.gov` (confirmed: the proxy returns `HTTP 403` with
`x-deny-reason: host_not_allowed` on the `qym9-xzj6` bulk-CSV URL). git
clone/push is likewise blocked (CONNECT tunnel rejected), so work was done via
the GitHub REST API, same as the prior two NY sessions.

Because the NY test suite is network-mocked and fixture-driven by design ("no
live API in the test suite"), it can be verified fully offline. I reconstructed
the NY surface from the GitHub API into a local tree, installed the real deps,
and ran it:

- **56/56 NY tests pass** across all 7 NY test files — `test_ny_acquire.py` (10),
  `test_ny_bill_id.py` (8), `test_ny_columns.py` (4), `test_ny_entities.py` (7),
  `test_ny_filings.py` (7), `test_ny_grain.py` (9), `test_ny_materialize.py` (11).
  Run against real `pydantic` 2.13.4 + `pandas` 3.0.3, in 0.8 s.
- **`ruff check` clean** on `src/lobby_analysis/io/ny/` and the NY test files.

So commit `f1098b6b27`'s `materialize_ny` + `materialize_cli` work is green
against the real Pydantic models, not just a local assertion. The
"OWED VERIFICATION" item from the prior handoff is discharged for the NY-scoped
surface.

Phase 3 (real pull) and the README-from-real-aggregates step were **not** done,
because they require `data.ny.gov`, which this sandbox cannot reach. Writing the
README now would mean inventing headline aggregates — which the plan explicitly
forbids ("intentionally deferred until after the first real Phase-3 run, so its
headline-aggregates section isn't a placeholder"). Stopped rather than fabricate.

## Topics Explored

- Whether the owed green claim could be settled without a full local checkout —
  yes, by reconstructing the NY-scoped tree (7 source files, 7 test files, 2
  fixtures, + `models/` + `pyproject.toml`) via the Contents API and running
  `pytest` against it under `PYTHONPATH=src`.
- Whether `data.ny.gov` is reachable — no; the egress proxy denies it at the
  host level (`x-deny-reason: host_not_allowed`), distinct from a server-side
  403. The NY data source is simply off this sandbox's allowlist.

## Provisional Findings

- **NY-scoped suite is green at `f1098b6b27`:** 56/56 pass, ruff clean. This is
  a stronger statement than the prior session's "46 green locally" because it
  ran on a clean networked machine against freshly-installed real deps, with all
  7 NY test files collected and counted (nothing skipped).
- The NY modules are self-contained — they import only `io/ny/*` and read from
  `models/{entities,filings}` — so they cannot have regressed unrelated suites.
  I did **not** re-run the full ~1650-test repo suite (it needs the whole tree +
  has the 3 known non-NY `scoring` reds, GH #38); the prior grain-collapse
  session already recorded full-suite green (1659 passed) at an earlier commit,
  and nothing since then touches non-NY code.
- `data.ny.gov` is not on the bash egress allowlist for this environment. An org
  owner can add it; short of that, the live pull needs a networked machine that
  can reach it (the OH branch handled the analogous block by handing the live
  run to a US-based collaborator).

## Decisions Made

- **Settle the green claim, then stop before the data-dependent steps.** Did not
  write `releases/ny/README.md` and did not run Phase 3 — both need real NY data
  that this environment can't fetch, and a placeholder-aggregates README would
  violate the plan's own deferral rule.
- **No code changed.** This was verify-and-checkpoint only; the sole repo
  artifact is this convo + the RESEARCH_LOG update.

## Open Questions / Next Steps

- **Phase 3 real pull is the unchanged next pickup** — on a machine that can
  reach `data.ny.gov` (or after an org owner adds it to the egress allowlist):
  `io/ny/acquire.download_bulk_csv` for `client_semiannual` (`qym9-xzj6`) 2025
  into `data/raw/ny/2025/`, then `materialize_cli`, then sanity-check aggregates
  + spot-check 1–2 large filers against the live portal.
- **Then `releases/ny/README.md`** from the real aggregates.
- **Then Phase 4** chain composer + Open States join.
