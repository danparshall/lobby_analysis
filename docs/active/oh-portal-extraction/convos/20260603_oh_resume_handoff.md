# HANDOFF — Resume the OH (Ohio) data grab

**Date:** 2026-06-03
**Branch:** `oh-portal-extraction`
**Prepared by:** Dan's planning session (while scoping the MI/NC/OH state pulls).
**Status change:** **Dan is taking this branch over from Amina** (decided 2026-06-03). Coordinate
with Amina on the in-flight LLM run, but Dan now drives.
**For:** a fresh agent with zero prior context.

---

## Goal
Finish the **(A') single-filing round-trip**: run the LLM extraction on one real OLAC filing,
validate it against pre-filled ground truth, then decide whether to graduate to **(B')** batch
extraction. The code is already written and the round-trip is already validated against saved
HTML — what's left is running the actual LLM call and filling the validation table.

## What this is
OH lobbying disclosure (Activity & Expenditure Reports, "AERs") lives **only** in the OLAC
portal (Ohio Legislative Ethics Commission / JLEC) as server-rendered HTML at
`/olac/AERs/{report_id}/View` — **no bulk download, no API, no PDF**. Pipeline: fetch one
filing's HTML → LLM-extract into a `LobbyingFiling` → validate.

## Current state (done)
- Extraction code under `src/lobby_analysis/oh_portal/`: `fetch.py`, `extract.py` (single
  Anthropic SDK tool-use call, `claude-opus-4-7`, enforces the `LobbyingFiling` schema),
  `extraction_brief.py`, `provenance.py`, `__main__.py` (CLI).
- Regime confirmed `legislative` (matches `extraction_brief.py:14`); largest filer population;
  statute structurally stable 2010→2025.
- Validation skeleton pre-filled with source-derived ground truth at
  [`results/20260507_oh_a_prime_validation.md`](../results/20260507_oh_a_prime_validation.md).
  Sample filing = **Aichele / ARC Gaming, report_id `1427844`** (4 bills, $20 Section II.D
  aggregate, expected null patterns, pre-flagged schema gaps). The validation step is now pure
  tag-filling.

## The one real blocker to clear first
`fetch.py` does a live `requests.get` (30 s timeout) that **times out from outside the US**, and
**the raw HTML is not on this machine** — `data/oh_portal/` does not exist here. Amina
browser-saved it on her VPN'd machine (at `data/oh_portal/raw/1427844/2026-05-21T18-52-26+00-00/raw.html`)
and it never synced to Dans-MacBook-Pro (same machine-local data gap noted for statutes). So
**before anything else**, get the source HTML one of three ways:

1. **Ask Amina for her saved `raw.html`** for report_id 1427844 (fastest; it's already vetted).
2. **From a US network:** run the CLI (below) — `fetch_olac_aer` will pull it live.
3. **From abroad / no US network:** browser-save the AER HTML (VPN on) into
   `data/oh_portal/raw/{report_id}/{fetched_at_iso}/raw.html` + a `meta.json`
   (sha256, `fetch_method="browser-save-via-vpn-then-local-copy"`), then call
   `extract_oh_legislative_filing(html_path, brief, provenance)` directly to skip the blocked
   fetch — exactly what Amina did on 2026-05-22.

## Steps to finish (A')
1. **Get the HTML** (above). Confirm `ANTHROPIC_API_KEY` is set — the workspace quota cap that
   blocked Amina **reset 2026-06-01**, so the call should go through now.
2. **Run the extraction.** From a US network the whole round-trip is one command:
   ```
   PYTHONPATH=src .venv/bin/python -m lobby_analysis.oh_portal "https://<OLAC host>/olac/AERs/1427844/View"
   ```
   Output lands at `data/oh_portal/extracted/{report_id}/{run_id}/filing.json` +
   `extraction_run.json`. (If using a pre-saved HTML, invoke `extract_oh_legislative_filing`
   directly against the local file instead, per blocker option 3.)
3. **Fill the validation table** in `results/20260507_oh_a_prime_validation.md` — populate the
   Emitted Value + Tag columns against the pre-filled ground truth; compute summary stats
   (% CORRECT / WRONG / MISSING / SCHEMA-GAP). **Target ≥ 80% correct** to graduate.
4. **Schema gaps — do NOT unilaterally fix.** One gap is already known: OH Section II.D has a
   three-sub-row structure (Meals <$50 / Speaking Engagements / National Conference Meals) that
   `LobbyingExpenditure` can't represent. Document it; a v1.4 bump waits for **team consensus**
   (Dan/Gowrav). Flag any new gaps the same way.
5. **Record:** append a session entry to `RESEARCH_LOG.md`, a one-liner to `STATUS.md` Recent
   Sessions, commit, push.
6. **Graduation decision:** if validation passes + gaps are agreed, move to **(B')** batch
   extraction. Pre-vetted (B') seeds: **HART `1459616`**, **LKQ `1405684`**.

## Open coordination items (from Amina's notes)
- **Anthropic SDK vs subagent-dispatch.** Extraction currently uses the Anthropic SDK directly
  (`extract.py`). Dan had floated a subagent-dispatch pattern aligned with Track A; refactor cost
  ~1–2 hr at (A') scale, larger at (B'). Decide before scaling.
- **v1.4 schema-gap protocol:** ad-hoc convo + Dan/Gowrav review, or formal RFC? First concrete
  gap (Section II.D) is ready to be the test case.

## Environment quirks
- Worktree venv editable install is duplicated; tests + CLI work under
  `PYTHONPATH=src .venv/bin/python -m ...`. **Do not** `uv sync --reinstall-package`
  (standing memory — risks the shared editable install).
- `FieldRequirement.regime` is `str | None`, not a constrained `Literal` — convention-policed,
  low-priority hygiene.

## Primary sources (read first)
- Amina's own handoff: [`convos/20260522_phase_3_handoff_prep.md`](20260522_phase_3_handoff_prep.md)
- Plan: [`plans/20260507_oh_a_prime_implementation.md`](../plans/20260507_oh_a_prime_implementation.md)
- Validation skeleton: [`results/20260507_oh_a_prime_validation.md`](../results/20260507_oh_a_prime_validation.md)
- Branch RESEARCH_LOG: [`RESEARCH_LOG.md`](../RESEARCH_LOG.md)

## Why OH matters right now (strategic context)
OH is our **furthest-along activity-data state** — the only place we've validated end-to-end
extraction of real expenditure/bill data. MI structurally can't produce a bill chain (no
bill-level disclosure); NC won't give activity data freely (scrape-prohibited / paywalled). So
OH is the strongest candidate for a first real *spending* dataset, and the `oh_portal`
scrape→LLM-extract pattern is the template MI's scraper should reuse.
