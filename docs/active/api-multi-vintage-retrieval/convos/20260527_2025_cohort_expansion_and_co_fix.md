# 2026-05-27 — 2025 cohort expansion (3→15 states), NC+FL 2015+2025, CO 2025 TOC-page bug

**Branch:** `api-multi-vintage-retrieval` (worktree `.worktrees/api-vintage`)
**Machine:** Dans-MacBook-Pro
**Picked up from:** `3afc77c` (5/26 finish-convo for the NC/FL CF wall on the Air)
**Companion doc:** [`convos/20260526_nc_fl_url_discovery.md`](20260526_nc_fl_url_discovery.md) — yesterday's 9/9 CF wall that this session inverted

## Summary

User asked for 2025 statutes for NC/FL/MI/WI. Inventory showed MI/WI had URL-discovery bundles from the 5/19 fan-out (Method A done), needing only Method B section fetch; NC/FL had no usable bundles (NC partial from 5/19, FL never attempted). The 5/26 retrospective said NC/FL Method A was dead on the Air and recommended stealth-Playwright or tarragon as the next paths.

A CF probe (Method B, single WI 2025 section) cleared from Dans-MacBook-Pro in 62 KB of real text — first significant divergence from yesterday's wall. Proceeded incrementally: MI/WI 2025 Method B (both clean), then a single-pair FL 2025 Method A probe (clean, 18 URLs), then NC 2025 Method A (clean, 30 URLs). Encouraged by the streak, expanded scope: ran Method B against the 10 other states with existing 5/19 2025 URL bundles (AK/AR/CA/CO/IL/MA/PA/TX/WA/WV — 236 URLs, all clean), then dispatched NC 2015 Method A retry + FL 2015 Method A from-scratch (both clean), then Method B for all four NC/FL bundles. Zero CF stubs anywhere across the whole session.

Audit afterward caught **CO 2025**: the 5/19 subagent had produced 3 article-directory URLs instead of section-leaf URLs, and the post-fetch sanity check (`<500 bytes` for CF stubs) missed the 1.5-2 KB TOC pages those URLs returned. Fixed by mechanical `/2016/ → /2024/` URL swap from the CO 2015 bundle (CO 2015 had been substituted to 2016; CO 2025 substitutes to 2024 since Justia doesn't host 2025 for CO). Verified the swap with a probe (84 KB statute body returned), refetched all 11. The broken 5/19 bundle was preserved at `subagent_canaries/CO_2025_20260519_article_dir_urls/` per the mv-over-rm pattern.

## Topics Explored

- Single-section CF probe on WI 2025 to test Method B against the post-5/26 wall, on a new machine
- Method B 2025 section fetch for the original 4-state ask (MI/WI) and the 10-state 5/19-bundled cohort (AK/AR/CA/CO/IL/MA/PA/TX/WA/WV)
- Method A URL discovery (single-subagent probes) for FL 2025, NC 2025, NC 2015 retry, FL 2015 from-scratch
- Method B section fetch for the 4 new NC/FL bundles
- Post-fetch audit of all 2025 bundles for the CO-style "directory-URL masquerading as section-URL" failure mode — classified each state's URLs as section vs directory, cross-checked with median file size
- IL 2025 inspection — confirmed legit (TX-style directory-leaf where Justia inlines section text on article pages)
- CO 2025 mechanical URL swap from CO 2015 (which itself was vintage-substituted to 2016), with a probe to verify the 2016→2024 slug convention held
- Tightening of the post-fetch sanity check in the 2015 handoff doc template to add a median-size <2 KB → STOP rule
- Methodology distinction: Method A (URL discovery, LLM-stochastic) vs Method B (section fetch, deterministic-given-bundle)
- Reproducibility distinction: scripts are derivable from canary bundles; Method B is near-deterministic; Method A is not deterministic at all (CO 2025 vs CO 2015 demonstrates LLM judgment drift across calls)

## Provisional Findings

- **CF posture differs between Dans-MacBook-Air and Dans-MacBook-Pro, or has aged out overnight.** 9/9 wall on the Air on 5/26 → 5/5 Method A dispatches clean + 14/14 Method B bundles clean on the Pro on 5/27. Cannot isolate machine-vs-time-aging vs URL-family with this dataset alone — three confounds in play. Today's evidence does NOT generalize: CF could re-engage on any future dispatch from any machine. The 5/26 stealth-Playwright recommendation is not moot.
- **The original `<500 byte` post-fetch sanity check is too loose.** TOC pages on Justia are ~1.5-2 KB and pass the CF-stub threshold. CO 2025 produced 3 such files and the driver reported `[done]` cleanly. Median file size <2 KB is a better discriminator and was added to the 2015 handoff template.
- **Method A is not deterministic.** Same regime (CO lobbying disclosure, Title 24 Art. 6 Part 3), same workflow, two runs (CO 2015 → 11 section-leaf URLs; CO 2025 → 3 article-directory URLs). LLM judgment drift between dispatches is the root cause of the CO bug. Method B is deterministic given a fixed bundle; the canary bundles ARE the reproducibility unit, not the driver scripts.
- **Justia URL slug convention drifted between 2015 and 2025 for FL.** 2015 uses dot-separated section slugs (`section-11.045/`), 2025 uses hyphen-separated (`section-11-045/`). Spotted by the FL 2015 subagent during Method A. Matters for any downstream code that constructs URLs by template.
- **FL has a structural addition between 2015 and 2025:** sections 112.3121/3122/3123/3124 (post-office lobbying prohibition pair + definitions) appear at 2025 but not 2015 — linked to the 2018 Florida constitutional amendment. The FL 2025 subagent's notes flagged this.
- **NC has structural removals between 2015 and 2025:** sections 120C-215 (Other persons required to register) and 120C-404 (Solicitor's reports) appear at 2015 but not 2025. Same Chapter 120C, same 8 articles; just two sections removed/recodified.
- **CF window held for the entire session.** ~600+ Playwright requests across Method A subagents and Method B sequential fetches, zero CF stubs, zero `[ALERT]` outputs. Most sustained clean run on this branch since 2026-05-19.

## Decisions Made

- **Convo name approved:** `20260527_2025_cohort_expansion_and_co_fix`
- **Probe-one-then-fan-out** for NC/FL Method A (per the 5/26 retrospective's lesson)
- **Mechanical URL swap (Option A) over re-running Method A subagent (Option B)** for the CO fix, on the grounds that (a) CO 2015 bundle was structurally correct, (b) section numbering 24-6-301 through 24-6-309 has been stable for decades, (c) determinism beats LLM stochasticity when we have a known-good shape. Probe before full fetch validated the 2016→2024 slug stability.
- **Preserve the broken CO 2025 bundle** at `subagent_canaries/CO_2025_20260519_article_dir_urls/` (mv-over-rm pattern from 5/26)
- **Tighten the 2015 handoff Step 3 template** to add median-size <2 KB → STOP, with provenance comment pointing back to this convo
- **No PR-readiness work this session** — branch stays on `api-multi-vintage-retrieval`, no merge to main

## Results

- [`results/20260527_statute_inventory.md`](../results/20260527_statute_inventory.md) — final per-state per-vintage file inventory across 2010/2015/2025
- 12 new clean `subagent_canaries/<STATE>_2025/` bundles (FL, NC; plus the 10-state 5/19 fan-out remained unchanged)
- 2 new clean `subagent_canaries/<STATE>_2015/` bundles (NC, FL)
- 1 replacement `subagent_canaries/CO_2025/` bundle (mechanical URL swap)
- 1 preserved-as-evidence `subagent_canaries/CO_2025_20260519_article_dir_urls/`
- Statute section files on disk: 12 new state-vintage dirs at 2025 (10 cohort + NC + FL) + 2 new at 2015 (NC + FL); machine-local under `~/data/lobby_analysis/statutes/`

## Open Questions

- **Why did CF flip from 9/9 blocking to 0/many blocking overnight?** Three plausible confounds (machine, time-of-day/session-aging, URL family); no controlled probe today to disentangle. Worth a deliberate test if/when we have a quiet moment.
- **Is the median-size check the right durable threshold, or should it be size-distribution-aware?** A bundle of mostly real-section URLs with one TOC URL slipping in would still pass median <2 KB. A min/p25-based check would be stricter but might over-fire on legitimately-short subsections. Not a problem today, flagged for future.
- **OH 2025 has 30 files vs OH 2015's 52** — that delta predates this branch (OH 2025 populated months ago from `statute-retrieval`). Out of session scope but worth checking whether OH 2025 has the same TOC-page failure mode or whether Justia genuinely consolidated OH's regime structure between vintages.
- **CO 2025 mechanical-swap provenance** has `prompt_git_rev: "n/a-mechanical-swap-from-CO_2015"` in the result.json — a sentinel string, not a real commit. Downstream consumers that filter on a specific prompt revision will see this as "not from a subagent run." Acceptable today; flag if it breaks anything.
- **The sanity-check tightening lives in the 2015 handoff template, not in production code.** A `scripts/fetch_statute_sections.py` parameterized CLI driver would be the durable home; deferred per "stay focused on closing out" framing.

## Next Steps

- Cross-machine sync of `~/data/lobby_analysis/statutes/` from the Pro to the Air / tarragon before any of those machines try to run downstream Phase C work that assumes the 2025 cohort exists
- OH 2025 spot-check (independent of this branch's session — same audit logic, different provenance)
- Method A retry for the still-deferred states: GA, VA, AZ at 2015 (all CF-blocked on 5/18); WY, NY at 2015 (lossy 3); and 2025 versions of those if a clean Method A window holds
- Phase C downstream can now consume 15 states × 2-3 vintages of statute text; this branch's Method A/B substrate is broadly in shape for the multi-rubric calibration the project is gating on
