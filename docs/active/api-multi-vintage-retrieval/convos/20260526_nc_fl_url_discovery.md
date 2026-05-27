# 2026-05-26 — NC + FL URL discovery (intended); CF-fingerprint characterization (delivered)

**Branch:** `api-multi-vintage-retrieval` (worktree `.worktrees/api-vintage`)
**Handoff:** [`plans/_handoffs/20260526_nc_fl_url_discovery.md`](../plans/_handoffs/20260526_nc_fl_url_discovery.md)
**Dispatch template:** [`plans/_handoffs/20260519_subagent_dispatch_prompt.md`](../plans/_handoffs/20260519_subagent_dispatch_prompt.md)
**Machine:** Dans-MacBook-Air
**Picked up from:** `94dc75d` (main, post `20260524` Prong-1 pause weekly update) — worktree was at `291fb7d` (2026-05-19 post-finish-convo with GH issue back-links)
**Commits this session:** `b250070` → `b368aa2` → `b375d70` → `8245459` (4 commits, all pushed)

## Summary

Intended scope: URL discovery for the 4 missing (state, vintage) pairs covering WI/MI/NC/FL × 2015/2025, since WI/MI 2015 were already on disk and WI/MI 2025 had discovery bundles from the 2026-05-19 12-state fan-out.

Actual outcome: **9 consecutive Cloudflare-blocks at pass-1, 0 successful URL discoveries.** Iteratively varied IP (3 distinct egress IPs), Playwright headless flag (True/False), challenge timeout (30s/300s), and tried human-in-the-loop CAPTCHA-solving. Each variable change was falsified as the explanation. Final regular-Chrome ground-truth test confirmed the issue is Playwright's automation fingerprint — the laptop's IP/account can reach Justia cleanly via non-Playwright Chrome.

The 9 stub bundles are preserved with descriptive archival names, and a results doc characterizes the negative-result evidence. Pivot to stealth-Playwright (or tarragon) needs to happen before any further URL-discovery on this branch.

## Topics Explored

- 4-pair URL discovery scoping for NC/FL × 2015/2025 (the 2 missing-from-2026-05-19-fan-out states)
- Mv-over-rm preservation of the existing partial NC 2015 bundle (archived to `NC_2015_20260519_pass3_cf_blocked/`) before fresh retry overwrites
- Wave 1 (3 parallel general-purpose subagents) per the established CF-safe concurrency ceiling
- IP-rotation as a CF mitigation (laptop original IP → laptop new IP → laptop home IP, 3 distinct egresses)
- Playwright headless flag as a CF mitigation (headless=True → headless=False)
- HITL CAPTCHA solving with extended `challenge_timeout_seconds` (30s → 300s)
- Regular-Chrome ground-truth discriminator test (Playwright fingerprint vs. account/IP block)
- Per-call cleanup discipline: each diagnostic edit to `src/scoring/justia_client.py` reverted before commit; each failed bundle moved to date-and-condition-suffixed archival path before next probe

## Provisional Findings

- **Block is Playwright's automation fingerprint, not IP and not account.** Regular Chrome on the same Mac at the same time as the failed Playwright HITL probe loads `https://law.justia.com/codes/florida/2025/` cleanly. This is the load-bearing finding.
- **IP rotation alone is dead as a mitigation.** 3 distinct egress IPs across one session, all blocked identically — the pre-2026-05-18 "IP-state aging may help" framing in the prior handoff is structurally wrong against the current CF posture.
- **Headless flag alone is dead as a mitigation.** Both `headless=True` and `headless=False` blocked. Headless-mode-vs-headed isn't the discriminating fingerprint signal.
- **HITL CAPTCHA-solving in plain Playwright doesn't help on its own.** User observed Turnstile presenting "Verify you are a human" checkboxes REPEATEDLY across a single 5-minute window — each manual pass silently re-fails internally per CF's automation classifier, triggering another challenge. CF is fingerprinting *under* the Turnstile interaction, not just on the initial pageload.
- **NC 2015 is 3-for-3 walled across 2 IPs over 8 days.** 2026-05-18 attempt = pass-3 CF-blocked on all 8 articles; 2026-05-26 first attempt = pass-1 CF-blocked on original IP; 2026-05-26 second attempt = pass-1 CF-blocked on new IP. Strongest single-pair signal in the dataset.
- **The 2026-05-19 12-state success now reads as incidental.** That run cleared 12-for-12 with zero CF blocks. The repo's `justia_client.PlaywrightClient` works on a knife-edge: it's been getting through CF on a session-state cushion that depends on factors outside its design surface.
- **The fingerprint signal is below the layer the helper can fix.** `navigator.webdriver = true`, devtools-protocol traces, missing AudioContext/WebGL signatures, persistent `__playwright__` globals — Playwright leaks ~10–15 known automation tells that a basic `chromium.launch(headless=False)` does nothing to mask.

## Decisions Made

- **Convo name approved:** `20260526_nc_fl_url_discovery` (NC 2015 retry treated as part of NC scope; no separate billing).
- **Existing partial NC 2015 bundle preserved** by renaming `subagent_canaries/NC_2015/` → `subagent_canaries/NC_2015_20260519_pass3_cf_blocked/` (mv-over-rm rule).
- **Each subsequent CF-blocked bundle preserved** with date + condition suffix:
  - `NC_2015_20260526_cf_blocked_pass1/` (wave 1, original IP)
  - `NC_2025_20260526_cf_blocked_pass1/` (wave 1, original IP)
  - `FL_2015_20260526_cf_blocked_pass1/` (wave 1, original IP)
  - `NC_2015_20260526_cf_blocked_pass1_retry_new_ip/` (wave 2)
  - `NC_2025_20260526_cf_blocked_pass1_retry_new_ip/` (wave 2)
  - `FL_2015_20260526_cf_blocked_pass1_retry_new_ip/` (wave 2)
  - `FL_2025_20260526_cf_blocked_pass1_home_ip/` (probe 1)
  - `FL_2025_20260526_cf_blocked_pass1_non_headless/` (probe 2)
  - `FL_2025_20260526_cf_blocked_pass1_hitl_5min/` (probe 3)
- **Wave 2b (FL 2025 in original parallel batch) cancelled** after 6/6 CF blocks established the pattern — would have been a 7th identical stub for no information.
- **`src/scoring/justia_client.py` reverted to canonical state** at end of session (headless=True, challenge_timeout_seconds=30.0). Both diagnostic edits were probe-only, not productionizable as-is.
- **WI 2025 + MI 2025 section fetches deferred to a future session** (user explicit at mid-session ask). Those are unblocked-in-principle but not known to survive the current CF fingerprint posture either; should be re-probed before committing to a section-fetch wave.

## Results

- [`results/20260526_cf_state_characterization.md`](../results/20260526_cf_state_characterization.md) — full score sheet of 9 dispatches × variable changed × outcome; tabular falsified-hypotheses summary; implications for gather-first pivot.
- 9 CF-stub canary bundles under `subagent_canaries/` (listed in Decisions Made above), each containing `pass1_state_index.html` (~31 KB CF challenge interstitial), empty `pass1_state_index.tsv`, and `result.json` documenting the specific variable configuration.

## Open Questions

- **Will stealth-Playwright (rebrowser-playwright / playwright-stealth) mask enough of the fingerprint?** Cheapest single next test. Expected payoff: yes-or-no on whether the laptop is salvageable for Justia work without leaving the machine.
- **Does tarragon's Playwright build clear CF where the laptop's doesn't?** Untested; varies both OS and IP simultaneously. Strongest single-change mitigation if stealth-Playwright doesn't suffice.
- **Has Justia's CF posture globally tightened since 2026-05-19, or is this specifically a laptop-tracked-session-aging effect?** Not distinguishable without testing from a clean fingerprint on a different machine.
- **Are the existing 2025 section URLs from the 2026-05-19 12-state fan-out still fetchable** (the actual statute section pages, not the TOC index pages)? Untested. Section pages are a different URL family than state-year-index pages; CF's posture may differ.
- **Has the 2026-05-18 Justia outreach draft moved?** That's the durable-cooperation path; technical mitigations are workarounds at best.

## Next Steps

- **Stealth-Playwright spike** in a separate session. Try `rebrowser-playwright` (drop-in replacement) first; falls back to `playwright-stealth` (extension) if that doesn't work. Re-probe FL 2025 pass-1; if it clears, fan out the other 3 and the long-deferred WI/MI 2025 section fetches.
- **Tarragon retry** as a parallel/backup path. Pull this branch, set up worktree + uv venv + playwright install, dispatch the same 4 pairs from there.
- **WI 2025 + MI 2025 section-fetch CF re-probe** before any large section-fetch wave (the section pages may have different CF rules than the TOC index pages).
- **Re-engage Justia outreach** (user's 2026-05-18 framing). Technical workarounds buy time; cooperation is the durable solution.

## What could have gone better

- **Could have proposed the regular-Chrome discriminator earlier.** It came up only after 8 dispatches had already burned. Had it run as the second test (after wave 1's 3/3 block established the within-laptop pattern), the IP-rotation wave and the headless-flag-flip wave would have been skipped — saving ~5 subagent dispatches.
- **Probe-first pattern arrived late.** The first wave dispatched 3 subagents in parallel; only after that 3/3 block did the dispatch posture shift to probe-one-then-fan-out. The "probe-one" pattern is the right default for any retry against a known-flaky external service.
- **Helper architecture's fresh-context-per-call** likely makes CF-suspicion *worse*, not better, against the current fingerprint posture — a normal user re-uses browser state. The 2026-05-14 commit comment ("avoid Cloudflare's within-session fingerprinting") was a defensible call against a prior CF posture but is now actively counterproductive. Not changing this session (out of scope), but flagged for the stealth-Playwright session.
- **Could have committed less iteratively.** 4 commits ended up being justified by the user's "commit now" preference and the iterative IP-change ritual, but a single end-of-session commit summarizing all 9 stubs would have been git-cleaner. Trade-off accepted because each commit captured a real decision point.
