# HG vintage finding and deferral

**Date:** 2026-05-21
**Branch:** phase-c-projection-tdd

## Summary

Session opened with the user asking for status on `phase-c-projection-tdd`. After the status report (5 of 8 rubrics shipped — CPI 2015 C11, PRI 2010, Sunlight 2015, Newmark 2017, Newmark 2005; HG + FOCAL outstanding; Opheim blocked on 1988-89 vintage), user picked HG 2007 as next implementation. Per the plan's retrieval-gate, started a Path A scorecard retrieval attempt (CPI 2007 per-state per-question matrix from wayback).

The retrieval attempt surfaced a substantial finding: **the "Hired Guns" rubric is a May 2003 survey, not a 2007 one.** No second survey was ever conducted. Wayback evidence (2008 + 2010 captures both titled "Lobby Disclosure Ranking 2003"), CPI's own archives roll-up (no Dec 2007 ranking article), and user's domain knowledge ("Hired Guns" is a persistent CPI topic tag, not a survey name) converged on this conclusion. L-N 2024/2025's "2007" citation appears to be a grad-student misread of CPI's modern page metadata.

Implication: the Path A 1,900-cell ground truth is retrievable (per-state per-question pages exist on wayback at `nationwide.aspx?st=XX&display=DRStateNumbers`), but validation requires 2003-vintage statute data feeding the v2 cells. Justia coverage probe (13-state user-supplied sample) suggests ~7-8 states would be vintage-exact at 2003 — viable for narrow Path A, but most states would be 2005-2006 vintage with non-zero statute drift (CPI's own *States Outpace Congress* Mar 2006 documents 24 states made disclosure changes between 2003 and 2006). User decided to defer HG implementation rather than execute the rename + 50-state 2003-vintage retrieval work now. **FOCAL 2024 becomes the next implementation** on this branch.

## Topics explored

- Pre-flight status check on `phase-c-projection-tdd` — 5 shipped, 3 outstanding (HG, FOCAL, Opheim).
- HG retrieval-gate path selection: attempt Path A scorecard retrieval before committing to implementation.
- Wayback CDX scan of `projects.publicintegrity.org/hiredguns/*` — ~200 captures spanning 2008-2010, all under "Lobby Disclosure Ranking 2003" framing.
- Cross-source vintage triangulation: wayback page titles, CPI archives roll-up, methodology PDF metadata (Firefox print from April 2026 — not informative), L-N 2024/2025 citations.
- L-N citation forensics: three independent academic citations all reference `methodology-5/` URL with "2007" datestamp, accessed Jan 22, 2024. User identified the root cause: CPI uses "Hired Guns" as a topic tag, and the methodology page's "last-updated" stamp probably reflects the Dec 2007 commentary article, not the survey date.
- Justia historical coverage probe — WebFetch + curl both 403'd by Cloudflare bot detection. User did the probe manually from a browser; supplied 13-state sample.
- IP / egress check confirmed bash curl egresses from user's residential Comcast IP, WebFetch from Anthropic infrastructure. Both 403'd on Justia — fingerprint heuristics, not IP geography.
- Sized the Path A vintage-eligibility picture: if 13-state sample generalizes, ~7-8 states at 2003 (vintage-exact), ~35 at 2005-2006 (drift), ~7-8 at 2010+ (unusable for HG 2003 validation).

## Provisional findings

- **HG = CPI 2003 Lobby Disclosure Ranking** (single survey, May 2003 publication, statute data late-2002 / early-2003). The "Q35-Q37 at 2002 vintage" detail from `items_HiredGuns.md §6` becomes coherent — prior-year agency self-report in an early-2003 survey, not a mixed-vintage anomaly.
- **L-N 2024/2025 carries a citation error** (HG dated as 2007 in three independent papers). Doesn't directly impeach L-N's FOCAL framework analysis (the framework-coding factual audit already surfaced and corrected the loadbearing issues), but flags that L-N's citation-quality bar has gaps on non-load-bearing details. Worth keeping in mind when leaning on L-N for FOCAL Suppl File 1's 1,372-cell weight matrix.
- **Path A retrieval target is real** — wayback has all 50 per-state per-question pages captured 2010-07-06 under `nationwide.aspx?st=XX&display=DRStateNumbers`. Not yet scraped.
- **Justia historical depth varies by state** — earliest year ranges from 2003 (FL, WA in user's sample) to 2016 (CO). No uniform "Justia goes back to year X" answer.
- **The Justia 403 is fingerprint-based, not IP-based.** User's home IP would serve a real browser session fine; curl/WebFetch trip Cloudflare TLS-fingerprint heuristics regardless of egress.

## Decisions made

- **Defer HG implementation** on this branch. Joins Opheim as blocked-on-vintage. Mergeable rubric scope on `phase-c-projection-tdd`: 6 rubrics (CPI 2015 C11, PRI 2010, Sunlight 2015, Newmark 2017, Newmark 2005, FOCAL 2024).
- **Defer the cross-cutting `CPI_2007_*` → `CPI_2003_*` rename.** Worth doing as a single sweep when HG implementation resumes, alongside whatever 2003-vintage retrieval branch unblocks it. Touching archived `compendium-source-extracts/` material has higher coordination cost; not worth doing twice.
- **FOCAL 2024 is next.** Plan-set already drafted at [`../plans/20260518_focal_2024_legal_core_plan.md`](../plans/20260518_focal_2024_legal_core_plan.md) + 3 more sub-plans (contact_log, openness_timeliness, aggregation) + aggregation orchestration. Strict order: legal_core → contact_log → openness_timeliness → aggregation, all converging on a single `focal_2024.py` module.
- **HG captured as GH `task` issue** so the deferral has a discoverable handle for resumption.

## Results

- [`../results/20260521_hg_vintage_correction.md`](../results/20260521_hg_vintage_correction.md) — full evidence chain (wayback CDX, archives roll-up, L-N citation triangulation, Justia probe, decision context)

## Open questions

- Does CPI's `methodology-5/` slug imply prior versions (methodology-1 through methodology-4)? Cheap wayback CDX check if it ever matters; not load-bearing.
- 50-state 2003-vintage statute retrieval scope: how much can be filled from Justia (2-state sample: FL, WA), how much from wayback state portal captures, how much requires state archives / law libraries? Future research-line question.
- Does L-N's citation-quality variance affect anywhere else in our use of their work? FOCAL summary already factual-audit-clean for framework coding; this is bibliographic-only carelessness. Don't re-audit unless something surfaces.

## Captured Tasks

<!-- Populated by capture-task skill -->
