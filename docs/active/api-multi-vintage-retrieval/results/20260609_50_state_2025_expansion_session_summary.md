<!-- Generated during: convos/20260609_2025_50_state_expansion.md -->

# 2026-06-09 — Justia 2025 expansion session summary

**Goal:** Take Justia 2025 statute coverage from 16 → 50 states.
**Result:** +4 clean / +2 partial / 28 remaining. CF tripped mid-session; paused for fresh CF state in a future session.

## Coverage delta this session

| Status | Count | States |
|---|---:|---|
| Pre-session (clean 2025 bundles already on disk) | 16 | AK, AR, CA, CO, FL, IL, MA, MI, NC, NY, OH, PA, TX, WA, WI, WV |
| New clean canaries this session (URL bundles ready for Phase 3 section fetch) | 4 | AL, LA, NE, VA |
| New partial canaries this session (CF-blocked, pass-1 work preserved) | 2 | AZ, GA |
| Remaining for future-session fan-out | 28 | CT, DE, HI, ID, IN, IA, KS, KY, ME, MD, MN, MS, MO, MT, NV, NH, NJ, NM, ND, OK, OR, RI, SC, SD, TN, UT, VT, WY |
| **Effective coverage at session end** | **20 / 50 clean + 2 partial** |  |

WY in the remaining 28 is expected to require vintage substitution (Justia only hosts WY 2010 per current `data/statutes/WY/` state).

## Canary-trio detail (Phase 1)

| State | URLs | Pass-1 pick | Pass-3 invoked | Tree depth | Regime structure |
|---|---:|---|---|---:|---|
| AL | 11 | Title 36 (Public Officers and Employees) | yes | 4 | Single-body, per-section leaves |
| LA | 22 | Revised Statutes → Title 24 + Title 49 | no | 4 | Two-body (legislative + executive branch lobbying); flat per-section URLs within each title (Wisconsin-style "Example D" convention) |
| NE | 17 | Chapter 49 (Law) | no | 4 | Unicameral flat-chapter; per-section leaves directly under chapter; Justia "Chapter 49" labeled "Law" houses NPADA |

All three: `playwright_errors: []`, `actual_vintage_used: 2025`.

## Batch-1 detail (Phase 2)

| State | URLs | Status | Notes |
|---|---:|---|---|
| VA | 18 | CLEAN | Title 2.2 / Chapter 4 / Article 3 (Lobbyists); §§2.2-418 to 2.2-435. **Regime prior in dispatch was stale ("Chapter 4.4") — that slug is now Children's Ombudsman; actual lobbying is Chapter 4 Article 3.** |
| AZ | 0 | CF at pass-2 | Pass-1 picked Title 41 (correct per A.R.S. Title 41 Ch. 7 Art. 8.1); CF fired between pass-1 and pass-2 fetches. Pass-1 work preserved. |
| GA | 0 | CF at pass-1 | pass1_state_index.html is the CF interstitial; no TSV. No discovery work done. |

## Cumulative-cost picture (estimated)

| Phase | subagent_tokens (in+out total) | Est cost @ opus | Est cost @ sonnet |
|---|---:|---:|---:|
| Canary trio (AL/LA/NE) | 275,820 | $1.50–$3.00 | $0.60–$1.20 |
| Batch 1 (AZ/GA/VA) | 213,784 | $1.20–$2.40 | $0.50–$1.00 |
| **Session total** | **489,604** | **~$2.70–$5.40** | **~$1.10–$2.20** |

Per-canary average: ~82K tokens, ~$0.45–$0.90 at opus rates. **5–10× higher than my pre-session $0.10/canary estimate.** Budget was raised mid-session from $5 → $35 to accommodate the recalibration; ~$2.70–$5.40 of that $35 spent.

## CF empirical observations

| Event | Cumulative session fetches (approx) | CF status |
|---|---:|---|
| AL pass-1 probe | 1 | clean |
| Canary 1 dispatch (AL+LA+NE, 3-concurrent) | ~10–15 | all clean |
| AL pass-1 probe #2 (just before batch 1) | ~16 | clean |
| Batch 1 dispatch (AZ+GA+VA, 3-concurrent) | ~25–30 at dispatch | AZ pass-1 clean → AZ pass-2 blocked; GA pass-1 blocked; VA all 3 passes clean |

Working hypothesis: per-IP cumulative-fetch rate-limit (not pure-concurrency). Decays over time but doesn't reset to zero between batches in a session. 2-concurrent + cooldowns might extend the runway but doesn't address the underlying mechanism.

## Phase 3 status

**Deferred.** No section-body fetch this session. The Phase 3 driver (`scripts/fetch_50state_2025_sections.py`, modeled on `fetch_gap_cells_sections.py`) is unwritten; the 4 clean canaries' URLs will land in `data/statutes/<S>/2025/sections/` once a future session runs Phase 3 against all-clean bundles accumulated to date.

## Recommended next-session shape

1. **Cooldown of ≥24h** before resuming Justia fetches from this IP (educated guess; could be shorter or longer depending on how Justia's CF heuristics decay).
2. **First action:** single-fetch probe (one pass-1 on, e.g., HI) to verify CF window is open before any subagent dispatch.
3. **If probe clean:** continue fan-out at **2-concurrent + 5-min cooldown between batches** (per user's directive). 28 remaining + 2 re-canaries (AZ resume from pass-2, GA from pass-1) = 30 dispatches; at 2-concurrent that's 15 batches.
4. **Phase 3 section-body fetch** once all clean bundles in hand. Single Python pass; no API spend.
5. **Cross-machine sync** of the new section bodies to Air/tarragon when Phase 3 runs.

If CF is still firing on the cooldown probe: switch surface (VPN / hotspot) or invest in stealth-playwright before further attempts. Both are explicit forks in the road; the 6-05 doc flagged stealth-playwright as "recommendation not retired."
