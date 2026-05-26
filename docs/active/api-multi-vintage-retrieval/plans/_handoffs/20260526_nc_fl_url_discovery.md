# Handoff: NC + FL URL discovery (2015 retry + 2015/2025 fresh)

**Date opened:** 2026-05-26
**Branch:** `api-multi-vintage-retrieval` (worktree `.worktrees/api-vintage`)
**Originating convo:** [`convos/20260526_nc_fl_url_discovery.md`](../../convos/20260526_nc_fl_url_discovery.md)
**Dispatch template:** [`20260519_subagent_dispatch_prompt.md`](20260519_subagent_dispatch_prompt.md) — **read first**; this scope doc only carries deltas.
**Companion docs:**
- [`20260519_fetch_2025_statute_bundles.md`](20260519_fetch_2025_statute_bundles.md) — prior 12-state 2025 fan-out (explicitly excluded NC + FL)
- [`20260518_fetch_2015_section_bodies.md`](20260518_fetch_2015_section_bodies.md) — has the per-state regime notes for NC, FL, and the CF history

---

## Why this handoff exists

User scoped the gather-first pivot's 5–8 priority states to include WI, MI, NC, FL for 2015 + 2025 (this session, 2026-05-26). Inventory of what's already done:

| State | Vintage | URL discovery | Section fetch on disk |
|---|---|---|---|
| WI | 2015 | ✅ done | ✅ `data/statutes/WI/2015/` |
| WI | 2025 | ✅ done (16 URLs, batch 3 on 2026-05-19) | ❌ pending |
| MI | 2015 | ✅ done | ✅ `data/statutes/MI/2015/` |
| MI | 2025 | ✅ done (23 URLs, batch 4 on 2026-05-19) | ❌ pending |
| NC | 2015 | ⚠️ article-level only — pass-3 CF-blocked on all 8 articles (2026-05-18) | ❌ pending |
| NC | 2025 | ❌ not started | ❌ pending |
| FL | 2015 | ❌ "lossy" batch (URLs only, no reproducibility bundle) | ❌ pending |
| FL | 2025 | ❌ not started | ❌ pending |

This handoff covers **URL discovery only** for the 4 missing/incomplete `(state, vintage)` pairs:

1. **NC 2015** — retry full pass-1+pass-2+pass-3 to attempt clearing the CF block that left only article-TOC URLs on 2026-05-18. IP-state aging since may help (the 2026-05-19 12-state run reported 0 CF blocks).
2. **NC 2025** — fresh full discovery (state was excluded from the 2026-05-19 12-state fan-out).
3. **FL 2015** — fresh full discovery (no reproducibility bundle exists; the lossy 2026-05-14 run produced only URL-list output).
4. **FL 2025** — fresh full discovery.

Section fetches for these 4 pairs + the 2 already-discovered 2025 pairs (WI 2025, MI 2025) are **NOT in scope this session**; they're a separate handoff once these bundles land.

---

## NC 2015 preservation

The existing partial NC 2015 bundle has been moved from `subagent_canaries/NC_2015/` to `subagent_canaries/NC_2015_20260519_pass3_cf_blocked/` to preserve the CF-blocked evidence while letting the retry land at the canonical path. **Do not delete the renamed dir** — it's the audit trail for the CF-state characterization of 2026-05-18.

If the retry succeeds: both bundles coexist (canonical + tabled). If it fails again: same outcome, with two CF-blocked records strengthening the "this state's TOCs are durably walled" signal.

---

## Per-state regime context (carry into dispatch prompts)

These give the subagent enough state-specific grounding to sanity-check its pass-1 and pass-2 picks against known regime structure.

### NC — North Carolina

- **Slug:** `north-carolina`
- **Lobbying chapter:** **Chapter 120C** (Lobbying)
  - 8 articles in the post-2006-reform consolidated regime: General Provisions, Registration, Prohibitions and Restrictions, Reporting, Liaison Personnel, Violations and Enforcement, Exemptions, Miscellaneous
  - Pass-2 should pick all 8 article TOCs
  - Pass-3 should enumerate sections under each (the prior canary reported "NC 2010 surfaced 32 sections across the 8 articles" as the expected shape)
- **Out of scope:** Chapter 138A (State Government Ethics Act) — officials-side, not lobbying-side. Pass-1 should NOT pick it.

### FL — Florida

- **Slug:** `florida`
- **Split-regime state — two parallel chapters under different titles:**
  - **Title III** (Legislative Branch) → **Chapter 11** (Legislative Organization, Procedures, and Staffing) — legislative lobbying. FL 2010 ground-truth was 6 section URLs (11.045 etc.) under Ch.11.
  - **Title X** (Public Officers, Employees, and Records) → **Chapter 112** (Public Officers and Employees: General Provisions) — executive-branch lobbyist regulation
- **Pass-1 should pick BOTH Title III and Title X.** Single-title pick is wrong for FL.
- **Pass-3 caveat:** Ch.112 has a sub-TOC layer (Part III), so pass-3 may need to recurse one extra level on that branch (the dispatch prompt's per-state addendum convention applies — see Step 3 recursion note below).
- **Historical recall:** B4 three-pass discovery hit 6/6 GT URLs on FL 2010 Ch.11 in May 2026 with the same prompt set — the recall mechanism works for FL when the model is allowed multi-title picks.

---

## Wave plan

CF concurrency ceiling is 3 (per the 2026-05-19 batch finding). Two waves:

### Wave 1 (3 parallel subagents)

- NC 2015 retry → `<OUT_DIR>/NC_2015/`
- NC 2025 → `<OUT_DIR>/NC_2025/`
- FL 2015 → `<OUT_DIR>/FL_2015/`

**Why this grouping:** mixed states (1 NC + 1 NC + 1 FL would also work; geographic mixing is just defensive — same Justia infra either way). Includes the CF-risk pair (NC 2015 retry) so we learn early whether CF state has changed.

**Commit wave 1 before dispatching wave 2.**

### Wave 2 (1 subagent)

- FL 2025 → `<OUT_DIR>/FL_2025/`

Solo because:
1. CF outcomes from wave 1 may motivate prompt/pacing changes
2. FL 2025 is the only pair where the pass-3 sub-TOC recursion question (Ch.112 Part III) is novel — single-subagent dispatch lets us inject a state-specific addendum if needed

---

## Per-state addenda to inject into the dispatch prompt

Per the 2026-05-19 lesson ("Generic dispatch prompt Step 3 under-specified for deep trees"), each subagent call gets a state-specific addendum block inserted before the procedure section. Templates:

### NC addendum (both 2015 and 2025)

```
STATE-SPECIFIC NOTES (NC):
- The lobbying chapter is Chapter 120C. Pick it at pass-1; do NOT also pick Chapter 138A
  (State Government Ethics Act — officials-side, out of scope).
- Pass-2 should enumerate 8 articles (Art. 1 General Provisions through Art. 8 Miscellaneous).
- Pass-3 must recurse into each article TOC to surface section-level URLs. Expected shape:
  ~32 sections total across the 8 articles (per NC 2010 prior canary).
- If pass-3 hits Cloudflare on any article: record in playwright_errors per the dispatch
  protocol and continue with the remaining articles. Do NOT retry within the subagent.
```

### FL addendum (both 2015 and 2025)

```
STATE-SPECIFIC NOTES (FL):
- FL is a SPLIT-REGIME state. Pass-1 must pick BOTH:
  * Title III (Legislative Branch) → Chapter 11 — legislative lobbying
  * Title X (Public Officers, Employees, and Records) → Chapter 112 — executive lobbying
  Single-title pick is wrong for FL.
- Pass-2 picks Ch.11 and Ch.112 from their respective title TOCs.
- Pass-3 on Ch.11 enumerates sections directly (chapter11/chapter11.html children are section
  leaves like 11.045, 11.0451, etc. — ~6 sections in 2010, likely similar in 2015/2025).
- Pass-3 on Ch.112 may surface a Part III sub-TOC (PARTIII.html) rather than section leaves.
  If pass-3 returns Part-level URLs, recurse pass-3 once more into each Part to surface sections.
  This is the deep-tree pattern the 2026-05-19 generic prompt under-specified for.
```

---

## Done-condition for this handoff

Handoff is complete when 4 bundles exist:

```
subagent_canaries/NC_2015/result.json
subagent_canaries/NC_2025/result.json
subagent_canaries/FL_2015/result.json
subagent_canaries/FL_2025/result.json
```

Each with:
- `proposed_urls` populated (or `playwright_errors` documenting CF if not)
- `actual_vintage_used` set (vintage substitution recorded if applicable)
- `prompt_git_rev` recorded
- Full per-pass HTML + TSV + chosen.json files preserved for reproducibility

Per-pair inventory (URL counts, vintage substitutions, playwright_errors) written up at `docs/active/api-multi-vintage-retrieval/results/20260526_nc_fl_url_discovery_inventory.md` at the end of the session.

---

## Things explicitly NOT in scope

- ❌ Section fetches for WI 2025, MI 2025, NC 2015, NC 2025, FL 2015, FL 2025. Separate handoff.
- ❌ Any direct-API discovery (`scripts/canary_discovery.py`). Anthropic workspace credit still spent per the 2026-05-19 status.
- ❌ Modifying the existing 2015 or 2025 canary bundles for other states. Only NC + FL.
- ❌ Deleting `NC_2015_20260519_pass3_cf_blocked/`. It's the audit trail for the prior CF block.
- ❌ Changes to `src/scoring/api_seed_discovery_pass{1,2}_prompt.md`. URL discovery prompts are frozen.
- ❌ Any work on the `wi-disclosure-explore` or `nc-disclosure-explore` branches — those are Prong-2 (portal extraction) lines, possibly other-fellow work.
