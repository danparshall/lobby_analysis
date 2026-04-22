# 2026-04-17 — Pilot execution and methodology pivot

**Date:** 2026-04-17 (laptop session, continuing from the morning's desktop inventory)
**Branch:** scoring

## Summary

Executed the Phase 3 three-state pilot (CA / CO / WY × 3 temp-0 runs × 3 rubrics = 27 scored cells, using the pre-existing 2026-04-14 CA dry-run as CA's third run). The pipeline itself worked — every raw JSON validated cleanly against pydantic on first attempt and every CSV stamped provenance correctly. The interesting finding is in the inter-run disagreement analysis: **PRI disclosure-law was flagged on all three states (CA 37.7%, CO 11.5%, WY 11.5%) and CO focal_indicators was flagged at 13.0%.** PRI accessibility was stable on CO (8.5%) and WY (3.4%) and flagged on CA (11.9%) purely because of WAF-stub interpretation variance.

A follow-up investigation into the disagreement root cause surfaced a methodology gap. The snapshot corpus is captured with a same-host constraint (we only fetch pages on the state's SOS/ethics portal host), which excludes state legislative sites where the actual statute text lives. In other words, we're not scoring "does the state's law require X" — we're scoring "does the portal's published guidance say the law requires X." Subagents disagreeing on portal silence (is a silent item an `unable_to_evaluate` or a `score=0`?) drives most of the disclosure-law flagged items, and no amount of prompt-sharpening against portal-only evidence will fully resolve it.

Rather than tighten the rubric against a proxy source, the user proposed a pivot: use **PRI 2010's published human-rater scores as ground truth**, retrieve 2010-era statutes (PRI scored against statute source, not portals), iterate the scorer prompt until our LLM output matches PRI's inter-rater reliability window, then apply the calibrated prompt against 2026 statutes. Plan doc captured as `plans/20260417_pri_ground_truth_calibration.md` — a fresh agent will pick it up on a new branch.

## Topics Explored

- Phase 3 pilot execution: 21 initial subagent dispatches → 20 killed by Anthropic API org-level rate-limiting → recovered via batches of 4
- Subagent off-prompt behavior: scorer subagents attempted to shell out to `pdftotext` and `unzip` for PDF and ZIP artifacts, triggering permission prompts. Fix: dispatch prompts must explicitly constrain to Read tool only
- Inter-run consistency analysis across all three pilot triads
- Artifact-source forensics: which snapshot artifacts each rubric actually cited, per run
- Methodology critique: same-host snapshot capture excludes statute sources
- Pivot to PRI 2010 ground-truth calibration

## Provisional Findings

- **Disclosure-law disagreement is unable-vs-zero ambiguity, not scoring disagreement.** CA pri_disclosure_law had unable_to_evaluate counts of 19 / 5 / 2 across the three runs — a 17-item spread on "is this answerable" alone.
- **PRI accessibility is stable when coverage is clean.** WY (clean tier, minimal portal) = 3.4% disagreement; CO (clean tier, richer portal) = 8.5%. CA's 11.9% flag is explicable by WAF-stub handling.
- **FOCAL is generally the most stable rubric** (CA 9.3%, WY 3.7%) except CO at 13.0% — 7 flagged items clustered in 3.x / 4.x / 7.x categories where subagents split 1-1-0 or 0-1-1 on whether CO addresses the indicator.
- **Snapshots capture portal content only.** `data_dictionary_01.pdf` (the CO SoS Lobbyist Guidance Manual) accounted for 55–61 of 61 CO disclosure-law citations across all three runs. That manual *references* Colorado Revised Statutes sections but doesn't include the statute text. Same pattern for CA (CAL-ACCESS glossary + FAQ) and WY (registration form instructions).
- **Rate-limit safe concurrency ≈ 4 subagents.** 21 concurrent triggered org-level throttling (Anthropic API "Server is temporarily limiting requests (not your usage limit)") and killed 20 of 21 dispatches. Recovery batches of 4 completed reliably.
- **Subagents go off-prompt under pressure.** Three times in this session, subagents tried to shell out for PDF/ZIP content (pdftotext, unzip) despite the Read tool handling PDFs natively. Dispatch prompts must explicitly forbid subprocess/shell.

## Decisions Made

- **Pause Phase 4 (50-state scale-up).** Do not launch 141+ runs until the disclosure-law rubric ambiguity is resolved.
- **Pivot to PRI 2010 calibration.** Plan: [`plans/20260417_pri_ground_truth_calibration.md`](../plans/20260417_pri_ground_truth_calibration.md). Fresh agent to continue on a new branch.
- **Scoring orchestrator extended** with reusable subcommands: `prepare-run`, `finalize-run`, `analyze-consistency`. `src/scoring/consistency.py` added. Tests still pass.
- **Memory saved** (global feedback):
  - "Subagent prompts must forbid shelling out — Read tool only for artifacts."
  - "No `---` separator in chained bash output — hiccups on Dan's system."
  - "Batch into existing package CLI, not throwaway scripts/foo.py."

## Results

- [`results/20260417_ca_consistency.md`](../results/20260417_ca_consistency.md) — CA triad (both PRI rubrics flagged)
- [`results/20260417_co_consistency.md`](../results/20260417_co_consistency.md) — CO triad (pri_disc + focal flagged)
- [`results/20260417_wy_consistency.md`](../results/20260417_wy_consistency.md) — WY triad (pri_disc flagged; acc + focal stable)

## Open Questions

- Does PRI 2010 publish item-level per-state codings, or only sub-component totals? Matters for calibration granularity. (Transcription notes from the earlier pri-2026-rescore Phase 1 work may answer this.)
- What is PRI 2010's own inter-rater reliability number? Sets the realistic target agreement window.
- Are 2010-era state statutes retrievable via Wayback Machine / archive.org for all 50 states, or only a subset?
- If PRI published cited-statute-sections per item in their 2010 methodology, that's a much cheaper ground-truth anchor than scraping 2010 state code wholesale.
- The 2026 rubric has 37 new accessibility items (Q9–Q16) with no PRI ground truth. How do we validate those? Separate process (human spot-check, held-out state consistency) — out of scope for the calibration plan itself.
