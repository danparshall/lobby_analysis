# OH discover --all bulk grab + 300-filing slice validation

**Date:** 2026-06-05
**Branch:** oh-portal-aprime-batch

## Summary

Picked up the post-`sonnet_validation` handoff: the OH scrape→parse pipeline was
"technically unblocked" for the bulk grab pending a robots.txt/ToS check. Did the
check, found the *legal* posture clean but the *crawler etiquette* not matching the
code (the runbook claimed "polite spacing is built in" — it wasn't, and the crawler
spoofed a Chrome User-Agent). Fixed both before crawling, then ran the full
agent-axis `discover --all` and a 300-filing extraction validation slice.

Net result: the OH 2025–2026 AER universe is now enumerated (**45,605 filings**),
and the sonnet-4-6 extraction pipeline is validated at 300-filing scale with an
effective **300/300 extractable** rate (the one first-pass failure was a transient
API 529, recovered on a single retry). The full-universe extraction is *not* run —
the serial batch loop would take ~8 days for 45K, so the recommended route is the
Anthropic Message Batches API + prompt caching + transient-error retry.

(Concurrency note: the regime-splitting memo from the same handoff was committed +
pushed to `main` as `docs/STATE_REGIME_SPLITTING.md` by a *different* session while
this one was doing startup — verified intact, not redone here.)

## Topics Explored

- robots.txt / ToS gate for `www2.jlec-olig.state.oh.us` (OLAC)
- Crawler etiquette: User-Agent honesty + request throttling
- Full agent-axis `discover --all` crawl (roster → surname search → per-agent FormsFiled)
- 300-filing extraction validation slice (sonnet-4-6)
- Failure-mode + throughput + cost characterization for the full universe

## Provisional Findings

- **ToS gate clears.** robots.txt → HTTP 404 (no crawl policy published); no Terms of
  Use anywhere on OLAC (landing page carries only a `©` notice); the data is Ohio
  statutory public record (ORC §§101.70+) published for public access. Checked 2026-06-05.
- **Crawler etiquette was weaker than documented.** `discover_all` fired ~3,000 GETs with
  **no inter-request spacing** (runbook's "polite spacing is built in" was false), and the
  crawler used a spoofed Chrome UA. Fixed: honest `USER_AGENT`, `REQUEST_DELAY_SECONDS=0.5`
  throttle at live-network entry points only (cache hits unthrottled). Commit `4ebd2e3`.
- **Discover universe:** 45,605 AER filings (2025=34,080 / 2026=11,525), 2,684 distinct
  agents, 2,741 distinct employers, **100% employer-populated, 0 duplicate report_ids**.
  The employer-misfile fix from the prior session holds at scale. Output (gitignored):
  `data/oh_portal/discover/recent.tsv`; cold crawl at 0.5s spacing, fully cached/resumable.
- **Extraction validated at 300-filing scale:** 299 extracted first-pass, 1 failed; the
  failure (1396214) was a transient `OverloadedError` (HTTP 529), **recovered on one
  retry** → effectively 300/300 extractable. Zero genuine parse/schema failures.
- **Two robustness gaps surfaced (both pre-existing):**
  1. **No retry on transient API errors** — a single 529/429 permanently drops a filing.
     Resumable re-runs recover, but it's manual. At 45K that's potentially dozens–hundreds.
  2. **Serial throughput** — measured **15.6 s/filing** (300 in 77.8 min). Full 45,605
     serial ≈ ~8 days. Non-starter.
- **Refined cost:** ~$0.035/filing (sonnet-4-6, no caching; measured output avg ~1,122
  tokens). Full universe ≈ $1,600 synchronous / **~$800 via Batches API** (50% off) before
  caching, which would cut it further (static brief+schema ≈ half the input).
- **Pre-existing bug found (not fixed):** `discover._discover_dir()` double-appends
  `oh_portal` (DATA_DIR already ends in it), so the discover cache writes to
  `data/oh_portal/oh_portal/discover/` instead of the documented single path. Harmless to
  the run (cache is self-consistent; `--out` path is correct) but the runbook documents the
  wrong location. Deferred (would orphan the in-progress cache to fix mid-crawl).

## Decisions Made

- Fixed crawler etiquette (honest UA + throttle) **before** the bulk crawl, per user.
- Ran the full `discover --all` (45,605-row index) — the index is itself a deliverable.
- Validated extraction on a representative 300-filing slice rather than auto-running the
  full universe (idempotent, so the 300 count toward any later full run).
- **Full-universe extraction deferred** to a dedicated build: Message Batches API +
  prompt caching + transient-error retry. Not started this session.
- Checkpointed and stopped here (user choice). No plan doc created yet — the Batches API
  build is the natural candidate for one next session.

## Results

- `results/20260605_slice_validation_300.md` — validation metrics, cost, and full-run projection.

## Open Questions

- Full universe via Batches API (~$800, async) vs. concurrency (~$1,600, ~10 hr, hammers
  the portal) — Batches API recommended but not yet built.
- Should transient-retry live in the sync path too (for slice/debug runs), or only in the
  Batches path?
- Fix the doubled discover cache-path bug + migrate the existing cache (deferred task).
- The 45,605-row discover index is gitignored (regenerable via `discover --all`) — is that
  acceptable, or should the index TSV be materialized into `releases/` like the WI chain?

## Captured Tasks

- [#35: Build OH full-universe extraction via Batches API + caching + retry](https://github.com/danparshall/lobby_analysis/issues/35) — captured 2026-06-05
