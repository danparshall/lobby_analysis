<!-- Generated during: convos/20260526_nc_fl_url_discovery.md -->

# Cloudflare-state characterization — 2026-05-26

**Purpose:** Document what the day's 9 CF-stub dispatches actually established about Cloudflare's behavior against Playwright on Justia, since the original NC/FL URL discovery target was not reached.

## Headline finding

> **The block is Playwright's automation fingerprint, not IP and not account.**
>
> Regular Chrome on the same machine loads `https://law.justia.com/codes/florida/2025/` cleanly. Playwright-headed, Playwright-headless, manual CAPTCHA-solving, three distinct egress IPs — all 9/9 CF-blocked at pass-1.

This is a different conclusion than the 2026-05-18 handoff's "IP-state aging may help" framing. IP rotation alone is dead as a mitigation; the next session needs to defeat the **fingerprint** signal (`navigator.webdriver`, devtools-protocol traces, missing AudioContext/WebGL signatures, etc.).

## Score sheet (9 dispatches, 9 CF blocks)

| # | Wave | Pair | Egress IP | Browser config | Outcome | Stub bundle |
|---|---|---|---|---|---|---|
| 1 | Wave 1 | NC 2015 retry | Laptop original | headless=True, timeout=30s | `cloudflare_blocked_at_pass1` | `NC_2015_20260526_cf_blocked_pass1/` |
| 2 | Wave 1 | NC 2025 | Laptop original | headless=True, timeout=30s | `cloudflare_blocked_at_pass1` | `NC_2025_20260526_cf_blocked_pass1/` |
| 3 | Wave 1 | FL 2015 | Laptop original | headless=True, timeout=30s | `cloudflare_blocked_at_pass1` | `FL_2015_20260526_cf_blocked_pass1/` |
| 4 | Wave 2 | NC 2015 (2nd retry) | Laptop new IP | headless=True, timeout=30s | `cloudflare_blocked_at_pass1` | `NC_2015_20260526_cf_blocked_pass1_retry_new_ip/` |
| 5 | Wave 2 | NC 2025 (retry) | Laptop new IP | headless=True, timeout=30s | `cloudflare_blocked_at_pass1` | `NC_2025_20260526_cf_blocked_pass1_retry_new_ip/` |
| 6 | Wave 2 | FL 2015 (retry) | Laptop new IP | headless=True, timeout=30s | `cloudflare_blocked_at_pass1` | `FL_2015_20260526_cf_blocked_pass1_retry_new_ip/` |
| 7 | Probe | FL 2025 | Laptop home IP | headless=True, timeout=30s | `cloudflare_blocked_at_pass1` | `FL_2025_20260526_cf_blocked_pass1_home_ip/` |
| 8 | Probe | FL 2025 (retry) | Laptop home IP | **headless=False**, timeout=30s | `cloudflare_blocked_at_pass1` (timing race: user solved CAPTCHA but the 30s helper window had already expired) | `FL_2025_20260526_cf_blocked_pass1_non_headless/` |
| 9 | Probe | FL 2025 (HITL) | Laptop home IP | headless=False, **timeout=300s** | `cloudflare_blocked_at_pass1_despite_hitl` — user reported Turnstile presenting "Verify you are a human" checkboxes REPEATEDLY across the 5-min window; each "pass" silently re-fails internally per CF's automation classifier, triggering another challenge | `FL_2025_20260526_cf_blocked_pass1_hitl_5min/` |

**Plus the historical NC 2015 from 2026-05-18:** pass-3 CF-blocked on all 8 articles, bundle preserved at `NC_2015_20260519_pass3_cf_blocked/`. So NC 2015 is now **3-for-3 walled across 2 IPs over 8 days**.

## Variables tested and falsified

| Variable | Falsified by | Status |
|---|---|---|
| Pure-IP block (account/network banned) | Regular-Chrome ground truth test loaded the same URL cleanly | ❌ Falsified |
| Per-state path block (e.g., `/codes/north-carolina/` specifically walled) | Dispatch #7 = FL 2025 (never attempted before today, never CF-blocked historically) ALSO failed identically | ❌ Falsified |
| Per-vintage block (e.g., 2025 archives walled but 2015 fine) | Both 2025 AND 2015 failed across both states | ❌ Falsified |
| IP rotation (3 IPs) | Dispatches #1–7 across 3 distinct egress IPs all CF-blocked identically | ❌ Falsified |
| Headless flag alone | Dispatch #8 (headless=False, 30s timeout) CF-blocked; dispatch #9 (headless=False, 5min HITL) ALSO CF-blocked | ❌ Falsified |
| Human-in-the-loop CAPTCHA solving | Dispatch #9 — user observed Turnstile escalating across multiple checkboxes within a single 5min window; CF re-failed each manual click | ❌ Falsified for plain-Playwright headed mode |

## Variables NOT yet tested

| Variable | Testable by | Cost |
|---|---|---|
| Stealth-Playwright fingerprint mitigation | `uv add rebrowser-playwright` (or `playwright-stealth`), patch `PlaywrightClient` to use it, re-probe | ~30min code + 1 subagent dispatch |
| Different OS / Playwright build (tarragon, Linux) | Push branch + worktree on tarragon, re-dispatch | Setup overhead (uv venv + playwright install) |
| Justia outreach (cooperation under public-domain framing) | User has drafted the framing on 2026-05-18; send it | Indefinite lead time, durable solution if accepted |
| CF aging over multiple days | Wait 24-72h, re-test | Time only; uncertain payoff |

## Implications for the gather-first pivot

The 2026-05-19 12-state URL discovery run that succeeded 12-for-12 with zero CF blocks now reads as **incidental fingerprint-detection lag, not a reproducible posture**. The repo's `justia_client.PlaywrightClient` works on a knife-edge: it's been getting through CF on a session-state cushion that depends on factors outside its design surface.

Going forward:

- **WI 2025 + MI 2025 section fetches** (the still-pending downstream of the 2026-05-19 12-state discovery wave) are not yet known to be blocked — Justia section pages are a different URL family than state-year-index pages, and the 2026-05-19 evening section-fetch run was clean. But there's no reason to expect them to be more resilient than the state-year-index pages; they should be re-probed before committing to a large section-fetch wave.
- **The 9 stub bundles** can also serve as a regression rail if a future stealth-Playwright fix lands: the same 4 `(state, vintage)` pairs should yield real bundles once the fingerprint signal is masked.
- **The 9 archival paths** under `subagent_canaries/` are descriptive enough (date + suffix indicating the variable changed) that the chronology can be reconstructed without reading this doc.

## What we did NOT learn

- Whether Justia's CF posture has globally tightened since 2026-05-19. The regular-Chrome ground-truth test shows this machine can still reach Justia, so it's at least not a hard wall. A tarragon test would tell us whether *any* Playwright fingerprint gets through anywhere.
- Whether Turnstile would eventually clear under HITL if the user clicked enough times. Possibly never; possibly after 5-10 retries; not characterized.
- Whether the per-call fresh-browser-context pattern in `PlaywrightClient` is contributing to suspicion (a normal user re-uses session state). Not isolatable without a refactor.
