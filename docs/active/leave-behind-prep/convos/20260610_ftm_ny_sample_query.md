# Convo — FTM NY sample query (#44): blocked at quota, evidence captured

**Date:** 2026-06-10
**Branch:** `leave-behind-prep`
**Participants:** Dan + Claude (claude.ai, claude_researcher workflow, with Claude-in-Chrome driving Dan's browser)
**Task:** [#44](https://github.com/danparshall/lobby_analysis/issues/44) — FTM NY sample query for 50-state portability
**Deliverable:** [`../results/20260610_ftm_ny_sample_query.md`](../results/20260610_ftm_ny_sample_query.md) (§0 + §7 complete; §§2–6 blocked)
**Commits:** `a26a7a0`, `db6422c`, `8669a7f` (+ this finish-convo bundle)
**API spend:** $0 (FTM gate fired pre-flight; no records consumed)

## Narrative

Session opened on Dan's "FTM is back online" with a pointer to the #44 writeup path,
framed as an existing doc. **Corrected: the doc didn't exist on any branch** — it's
the *deliverable* of reminder #44 (fired today), planned in the 2026-06-09 parity
session. Three reminders fired at session start: #44 (this work), #49
(RESEARCH_ARC rewrite), #54 (filing 1423176 cost pathology). **#49 and #54 were
surfaced but not dispositioned — they will re-fire next session (deliberate).**

Pre-staged while blocked: query harness
(`results/ftm_ny_raw/_run_query.py` — raw-capture + redacted JSONL log + gate
detection), writeup skeleton mirroring the WI LeMahieu structure, and the
cross-link IDs from the public openstates/people repo (Stewart-Cousins
`ocd-person/5f3e7bcf-9e43-423b-946b-982cc6ecc154` SD-35; Heastie
`ocd-person/2049da3a-132c-47b4-b53d-c28b574fff63` AD-83; both verified current
incumbents). Target call: **Stewart-Cousins primary** (office-analog of LeMahieu),
**2024 cycle** per the parity-session plan.

## Findings (all in the results doc; headlines here)

1. **FTM blocks datacenter IPs (probable).** www + api both 503/connection-timeout
   from the GCP sandbox; load fine from Dan's residential browser. Pipeline-relevant
   for #43; logged there.
2. **Quota is the hard blocker:** account at **1,083/1,000 records for the year** —
   the WI LeMahieu run consumed the annual budget. Gate semantics confirmed:
   records/year, not API calls (explains WI's "~15 queries" throttle exactly).
3. **Gate wording changed post-OpenSecrets-integration:** the 2026-06-03 "Institute
   will be in contact within two business days" review promise is **gone**; current
   gate is a flat pre-flight refusal at the website-export layer. The probe consumed
   nothing.
4. **No @followthemoney.org contact address exists.** Banner publishes
   info@opensecrets.org; Contact Us page's only mailto is info@crp.org. Follow-up
   sent 2026-06-10 To: info@opensecrets.org CC: info@crp.org (June 3 email never
   answered). **On-site Exemption Request form remains untried.**
5. **FTM API key:** lives behind Dan's login; the Chrome extension (correctly)
   blocks credential query-strings from reaching model context, so Dan
   right-click-copies the results-page JSON API link into `.env.local` himself.
   Execution path when access returns: drive the Ask Anything UI per query and
   click its JSON API link (site injects the key; key never transits chat).
6. **OpenStates/Plural disambiguation:** Dan's "OpenStates" key IS the Plural key
   (one service); nothing was ever pending with Plural. OpenSecrets ≠ Open States.

## Data acquired this session

- **Plural Policy OH bulk-CSV** downloaded by Dan (login required at
  open.pluralpolicy.com/data/session-csv/ — API-key registration is the account).
  Closes `oh-portal-aprime-batch` pending item (b), the lawmaker↔bill leg.

## Outstanding-data sweep (delivered in-session, recorded here)

- Blocked external: FTM NY queries (§§2–6) — await OpenSecrets reply / exemption.
- **`releases/ny/chain/` was never pushed to any branch** — per the 2026-06-09
  review this is deliberate (`.gitignore` 31-35, "re-add at merge", #37 merge
  gate), but the leave-behind packet must either include it or document the gap.
- Money-gated: OH full-corpus (~$301 mini / gated on is_itemized decision + #54);
  cross-state CPI 5 deferred states (~$15).
- Dormant: MI / NC stubs.

## Next steps

1. OpenSecrets reply or exemption grant → rerun the 5-query sequence through Dan's
   browser (~20 min; harness + skeleton staged) → fill writeup §§2–6.
2. Dan: file the on-site Exemption Request form (last untried channel).
3. #49 + #54 re-fire next session for disposition.
