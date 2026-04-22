# PRI Phase 4 — Data Collection Prep

**Date:** 2026-04-13
**Branch:** pri-2026-rescore

## Summary

Started Phase 4 of the PRI 2026 re-score plan (scoring-pipeline build). Scoped the work to **data collection only** this session — portal URL discovery (Stage 1) and raw portal snapshotting (Stage 2), deferring the Sonnet scoring function until after the captured evidence has been reviewed.

Architectural pivot early in the session: initial instinct was to scaffold a Python package (`src/pri_scoring/`) using the Anthropic SDK with `web_search` and `playwright` dependencies. User pushed back — the plan's Question 3 had already defaulted to Claude Code Agent subagents over SDK pipelines, and the native tooling (WebSearch, WebFetch, Bash+curl, Write) is sufficient. Tore down the scaffold, saved a feedback memory for future sessions, and executed the whole two-stage pipeline via per-state subagents.

Outcome: 50/50 states have a seed URL JSON and a portal snapshot manifest; 981 HTML/PDF/ZIP/CSV artifacts saved totalling ~350 MB. The data-collection pipeline is prepped; remaining work is Phase 5 (pilot scoring) and downstream.

## Topics Explored

- Scoping "data-collection pipeline" — narrowed to snapshots-first, Sonnet-directed discovery, browser-UA curl for snapshots.
- Agent-subagent architecture vs. Python SDK architecture for LLM-assisted structured data collection.
- Role-vocabulary discipline during URL discovery: `data_dictionary` only for true field-definitions docs (not user manuals); added `compliance_records` to the role list; `historical_archive` URLs only when distinct from the search tool.
- WAF behavior across state portals — Imperva/Incapsula, Akamai, Cloudflare, AWS WAF. Detected as 403s, ECONNRESETs, or (insidiously) 200-with-challenge-stub. Added `suspicious_challenge_stub` flag for HTML payloads <2KB.
- SPA portals that serve byte-identical shells for every route (PeachFile/GA, FirstStop/ND, Sunshine/ID, ethicsfiling/SC, mainelobbying.com, MiTN entellitrak/MI). Curl captures the shell; scoring will need a JS-rendering fetcher.
- Policy-gap framing: a state with no API + no bulk + WAF-protected search form is *technically* compliant with public-records law but practically inaccessible — and the PRI 2026 rubric Q10/Q11/Q12 should score that configuration low. This is the finding, not a pipeline bug.

## Provisional Findings

- **Stage 1 (URL discovery):** 50/50 states complete, all URLs cross-verified by the discovering subagent. Zero fabricated URLs. 15 states have flagged seeds (WAF 403s, DNS fails, auth walls) catalogued in `data/portal_urls/_flagged.md` for collaborator re-verification.
- **Stage 2 (snapshotting):** 50/50 states have a manifest. Full capture on 40 states (≥15 artifacts each, clean 200s). Partial capture on 8 states (WAF/SPA blocks subset of URLs). Near-empty capture on 2 states (AZ: 0 fetches, all 12 seeds pre-403; VT: 1 fetch, rest Incapsula-blocked).
- **Subagent tool-loading is probabilistic:** AK and AZ initially reported no WebSearch/WebFetch access in Stage 1 despite identical `subagent_type`. Retry with explicit "you have these tools" prompt succeeded. Factor in a retry pass when dispatching large numbers of subagents.
- **WAF landscape is worse than anticipated.** A realistic Chrome UA via curl bypasses some WAFs (michigan.gov SOS, hawaiiethics Salesforce) but fails on others (sec.state.ma.us Imperva, *.vermont.gov Incapsula, ilsos.gov HTTP/2 errors, AZ SOS). A JS-capable fetcher (Playwright with stealth) will be needed for Phase 5 pilot on ~10 states.
- **SPA shells are pervasive.** Static HTML captures 0% of the actual data surface on ~12 states whose public portals are Angular/React SPAs. Scoring those states on rubric items that depend on portal content requires JS rendering.

## Decisions Made

- **Subagent-driven pipeline over SDK.** Saved as feedback memory so future sessions default to subagents when either would work.
- **Stage 1 role vocabulary finalized:** `landing, registration, expenditures, search, bulk_download, data_dictionary, api_docs, gift_disclosure, historical_archive, compliance_records, faq, other`. `data_dictionary` reserved for true field-definitions docs; `compliance_records` for advisory opinions / complaints / enforcement.
- **Stage 2 snapshot policy:** curl with realistic Chrome UA, allowed hosts = any host in the state's seed JSON (to capture cross-agency systems), cap 30 fetches per state, same-window capture (2026-04-13 for all 50), flag any HTML <2KB as potential challenge stub.
- **Flag but don't fix.** Missing/WAF'd URLs are catalogued in `_flagged.md` and per-state manifests; collaborator follow-up will handle browser-based verification rather than blocking this session on it.

## Results

- `data/portal_urls/*.json` — 50 seed URL JSONs (one per state, discovered 2026-04-13) with role labels, HTTP verification, per-URL notes, and a per-state observations paragraph.
- `data/portal_urls/_flagged.md` — human-readable list of 15 states with non-200 seed URLs, grouped by state with role + URL + notes + status.
- `data/portal_snapshots/<STATE>/2026-04-13/` — 50 per-state directories containing raw HTML/PDF/XLSX/ZIP/CSV artifacts plus a `manifest.json` with per-fetch sha256, http_status, content_type, bytes, source (seed|linked), and `suspicious_challenge_stub` flag. Total: 981 artifacts, ~350 MB, not committed (`data/` gitignored).
- `docs/active/pri-2026-rescore/results/20260413_stage1_stage2_collection_summary.md` — summary table + findings doc.

## Open Questions

1. **Playwright fallback for the ~10 WAF'd / SPA states.** When and how to run it? Options: (a) spin up a one-shot playwright subagent per blocked state in a follow-up session, (b) have collaborators capture via real browser + save HTML manually, (c) score the blocked states partly from statute + auxiliary sources and note the data gap honestly in the deliverable.
2. **AZ snapshot is entirely empty.** Before Phase 5 pilot, either re-run AZ discovery with a different tool stack, or accept and score it from statute + FOIA.
3. **Stub flagging needs a second pass.** The 2KB heuristic caught CA Imperva stubs and some SC/DE/NE cases, but missed a 3.3KB Louisiana EthicsOpinion ASP.NET error page and several ~5-20KB SPA shells. Refine to combine size + sha256-duplication + content-sniffing for stub detection.
4. **Seed JSON refinements collaborators should make:** (a) add `ethics-form.alabama.gov` endpoints to AL.json (real bulk-export surface), (b) change HI.json Salesforce URL `http_status` from 403 to 200 (WebFetch lied; curl+UA succeeded), (c) verify the MS Akamai-blocked hosts have working `lobbying.sos.ms.gov` equivalents and update seed, (d) verify CA `fppc.ca.gov` manually (sandbox DNS failed, host is real).
5. **Sonnet scoring function build.** Not started this session. Next session: build the scoring prompt, pilot on 3 states using their snapshots as evidence, validate scores match rubric intent before launching full 50-state run.
