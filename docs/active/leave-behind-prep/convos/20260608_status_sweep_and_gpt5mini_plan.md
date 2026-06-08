# 2026-06-08 leave-behind-prep STATUS sweep + gpt-5-mini plan

**Date:** 2026-06-08
**Branch:** leave-behind-prep

## Summary

Session opened with Dan asking the status of `leave-behind-prep`. Agent (first session in this project) executed the claude_researcher session-start sequence; cloned upstream template fine, but mis-diagnosed an empty `$TOKEN` shell variable (didn't persist across bash invocations) as an expired PAT and surfaced "credentials broken" to Dan. After Dan's screenshot showed the PAT was healthy, agent re-ran the auth check with the token in scope, confirmed it works, and acknowledged the over-confident escalation as a sycophancy-adjacent failure of a different kind. Recovered, did the actual session start: fetched `personal_info.md`, STATUS.md, identified `leave-behind-prep` Day 1 work landed but not propagated to main.

Dan's actual ask was to make sure `main` "knows about" the branch + all state branches. Two interpretations surfaced (just STATUS-edit vs. merge code); Dan clarified "STATUS-only" since `leave-behind-prep` has more work pending. Agent flagged `mi-disclosure-explore` + `nc-disclosure-explore` as branches on origin in *neither* STATUS table — real gap, not just propagation. Also noted no `fl-*` branch exists; FL is in `STATE_COVERAGE.md`'s "Prong 1 statute SMR only" bucket along with 6 other states.

Dan also pointed out the agent should test the egress; git CLI clone over HTTPS with the PAT worked fine. Switched to full git CLI workflow for the rest of the session. Cherry-picked the 4 commits from `leave-behind-prep` onto main (all clean), added one new commit with mi/nc stub rows in STATUS.md Active. Pre-push, agent caught CLAUDE.md line 92 "Never make changes directly on `main`" and stopped to surface the norm violation; Dan authorized direct push as the sole Fellow on the project. 5 commits pushed to origin/main.

Pivoted to: "we've got a couple days, I need Suhan to make some decisions, but he needs to know exactly what's open." Agent listed 8 candidate decisions for Suhan (CPI 5-state dispatch, OH $800 extraction, Plural Policy bulk-CSVs, OH chain composer, FOCAL Plans 3+4, post-Fellowship project continuity, Prong-2 state priority, mi/nc fate). Dan then drilled into the OH extraction question specifically.

OH-extraction discussion (the substantive analytic block of the session) unpacked: what 45,605 AERs at $800 actually populate in the 4-node × 6-edge framework (4 of 5 edges; `lawmaker↔bill` is the exception, comes from Plural Policy at $0); what's *structurally* missing in OH (principal↔lobbyist $, stance everywhere) vs. just not-yet-materialized; the ask-then-extract vs extract-then-ask framing (grep raw HTML for entity → cheap targeted slice extraction ~$5-50 per question, vs full $800 extraction for an indexed release); whether classical NLP could replace LLM extraction (yes for most fields, but the LLM's value is in adaptive `extraction_warnings` and graceful form-drift handling — a hybrid is post-Fellowship); whether vendor swap saves money on extraction (no — confirmed pipeline is single-model Sonnet-4-6 already, $800 is the optimized floor); whether a tier-drop (mini-class) saves money (~6-12× cheaper input/output at the same vendor; needs validation).

Dan asked agent to draft a 1-2 hour plan to run gpt-5-mini on the existing 300-slice. Plan drafted; agent flagged scope ambiguity (Sonnet-as-proxy disagreement screen vs. real σ_noise validation), surfaced engineering risk (OpenAI's `response_format` JSON-schema vs Anthropic tool-use isn't a one-line swap — needs parallel `extract_openai.py`), and recommended budgeting 3 hours not 1-2. Agent also noted this displaces Day 2 cross-state CPI dispatch from the 5-day plan; FOCAL Plans 3+4 (Day 4) is the natural cut.

Closing turn: convo summary at this path + canonical name set for both Claude.ai and the file.

## Topics Explored

- Session-start credential diagnostics (and how `$TOKEN` not persisting across bash invocations looked exactly like an expired PAT)
- Git CLI vs Contents API as the user-repo interaction surface — claude_researcher's RESEARCHER.md only documents the curl path; full clone is faster, atomic, and supports cherry-pick
- Cherry-picking `leave-behind-prep` Day 1 onto main: STATUS reconciliation, STATE_COVERAGE.md, RESEARCH_LOG seed, Day 1 finish-convo — all 4 commits clean
- CLAUDE.md norms: "no direct push to main" rule + sole-Fellow exception
- The 8-decision surface for Suhan and which are technical vs strategic
- OH extraction cost decomposition: $800 = single-model Sonnet (not Sonnet+Opus comparison), validated 300/300 on 300-slice, Batches API + caching is what brings it from $1,600 to $800
- The 4-node × 6-edge × 3-attribute framework as the right unit for the Suhan-facing decision
- Which OH edges come from AER data (4 of 5 populated edges) vs Plural Policy (`lawmaker↔bill`)
- Ask-then-extract vs extract-then-ask: targeted slice extraction (~$5-50 per question) as an alternative to indexed-release ($800 upfront)
- Classical NLP vs LLM for AER extraction: BeautifulSoup handles ~80% of cells; LLM's irreducible value is `extraction_warnings` + form-drift robustness + Rule 6 semantic disambiguation
- Vendor swap cost analysis: GPT-5.5 *more* expensive than Sonnet (~2× on output); GPT-5.4 ~15% input savings only; flagship swaps don't save money
- Tier-drop cost analysis: GPT-5-mini at $0.25/$2 ≈ 12×/7.5× cheaper than Sonnet → ~$80-150 projected for full corpus IF validation passes
- Benchmark-substitution trap: SWE-bench / GPQA / Terminal-Bench scores are irrelevant for AER extraction; only relevant signal is the prior σ_noise work on `extraction-harness-brainstorm` (Tier-1: Claude 85.7% vs GPT 73.8% on OH statute reading)

## Provisional Findings

- **STATUS.md on main was substantially divergent from STATUS.md on `leave-behind-prep`** before this session — main was 4 commits behind, missing the Day 1 hygiene reconciliation. Cherry-picking propagated rather than waiting for Day 5 merge to keep main usable as session-start canon for fresh sessions.
- **`mi-disclosure-explore` and `nc-disclosure-explore` exist on origin but appear in neither STATUS Active nor Archived** on either `main` or `leave-behind-prep` pre-session. Day 1 reconciliation missed them. Both are stale (mi base 2026-06-02, nc base 2026-05-25) and need rebase or merge-main before resuming.
- **No `fl-*` branch exists on origin.** FL is documented as "Prong 1 statute SMR only" in `STATE_COVERAGE.md` (alongside CA/TX/CO/IL/WA/NC), not as a per-state Prong-2 branch.
- **OH extraction at $800 is already optimized.** Production pipeline is single-model `claude-sonnet-4-6` (not Sonnet+Opus side-by-side; that was a one-time n=1 validation activity). $800 = Sonnet × 45,605 AERs with Anthropic Batches API + prompt caching. Without these discounts the floor is ~$1,600.
- **Flagship vendor swap doesn't reduce cost.** GPT-5.5 at $5/$30 is more expensive than Sonnet-4-6 at $3/$15. GPT-5.4 input is ~15% cheaper but the task is output-heavy (~1,122 output tokens/filing) so input savings don't dominate. Realistic flagship-swap range $700-$1600.
- **Tier-drop is the real cost lever.** GPT-5-mini at $0.25/$2 input/output = ~12×/7.5× cheaper than Sonnet, projecting to ~$80-150 for full OH corpus IF a mini-tier model handles AER extraction adequately. Currently *no evidence* either way for AER (the prior σ_noise work was on flagship models, on statute text not AER text).
- **For OH, 4 of 5 populated lobbying-chain edges come from AER data** (principal→lawmaker via imputation, principal→bill via allocation, lobbyist↔lawmaker EXACT via Section II.A/B, lobbyist→bill via allocation). `lawmaker↔bill` comes from Plural Policy bulk-CSV at $0 — same path as already-shipped WI.
- **OH has lobbyist↔lawmaker $ flow disclosed natively** (Section II.A gifts: recipient_name + amount per row). WI lacks this leg entirely. This is the structurally-load-bearing OH-vs-WI policy finding for the Fellowship.
- **The $800 is not the cost of `releases/oh/`** — extraction is one of three pending items (per STATUS row on `oh-portal-aprime-batch`): (a) Batches+caching+retry full-corpus run [$800], (b) Plural Policy OH bulk-CSV download [$0, time only], (c) `releases/oh/` chain composer [Day 4 leave-behind work, time only].

## Decisions Made

- **STATUS propagation to main:** cherry-pick all 4 leave-behind-prep commits as-is (not surgically pick STATUS hunks only). Day 5 wrap-up merge will be cleaner; `docs/active/leave-behind-prep/` files landing on main early is acceptable given the branch's leave-behind nature.
- **mi/nc stub rows:** add to STATUS Active with format "exists, scope TBD," include latest-commit + merge-base metadata so fresh sessions can discover the branches. Don't merge their code; just surface that they exist. Format becomes a candidate convention worth standardizing for future stub additions.
- **Direct push to main:** authorized as exception, given Dan is the sole remaining Fellow and the multi-committer rationale for the CLAUDE.md norm no longer applies.
- **OH extraction strategy (deferred to Suhan):** three options frameable — (A) dispatch Sonnet at $800 now for Fellowship-end `releases/oh/`, (B) defer ~3 weeks, validate mini-tier first at ~$5, full corpus post-Fellowship at ~$100-150, (C) don't extract, answer questions on-demand via slice extraction. **Agent recommendation:** (B) on cost-efficiency grounds, unless Analogy has strategic reason to need OH as a Fellowship-end artifact.
- **gpt-5-mini validation work — committed (`5df4f39`).** Plan at `docs/active/leave-behind-prep/plans/20260608_gpt5mini_on_oh_300slice.md`. Three substantive design choices: (1) **3 runs of mini for σ_noise**, not the original 1-run agreement screen — Dan opted for stability characterization. (2) **Sonnet stays at 1x** as the reference rather than 3x — explicit asymmetric comparator with caveat documented in plan; saves +$30 and ~4hr but means writeup can claim mini σ_noise + mini-vs-Sonnet agreement, NOT ranked accuracy. (3) **5-day plan displacement explicitly acknowledged in the plan file**: Day 2 cross-state CPI dispatch slips to Day 3; FOCAL Plans 3+4 (Day 4) cut as the lowest-deliverable-value substitute. Revised plan: Day 2 mini-validation → Day 3 cross-state CPI 5-state dispatch → Day 4 OH chain composer + `releases/oh/` → Day 5 RESEARCH_ARC.md + resumption brief. Budget grew from 1-2hr to 4-5hr engineering + ~$3 API; hard-stop at 3hr on Phase 1 if OpenAI structured-output schema translation blocks.
- **Suhan-facing doc genre clarified:** *decisions doc*, not weekly-update status doc. Audience is Suhan-acting-on-it; structure is per-decision with options + recommendation + deadline, not narrative. Distinct from the Day 5 Fellowship-end retrospective (which is the leave-behind-prep deliverable). Decisions doc not yet drafted.

## Results

- 5 commits pushed to `origin/main` (`83ad0fe` → `6cc5bf0`): Day 1 STATE_COVERAGE.md + STATUS reconciliation + Day 1 finish-convo + NY skeleton fill + new mi/nc stub rows.
- STATUS.md Active table on main now lists all 6 live branches: `cross-state-cpi-2015-validation`, `ny-disclosure-explore`, `oh-portal-aprime-batch`, `leave-behind-prep`, `mi-disclosure-explore`, `nc-disclosure-explore`.
- `STATE_COVERAGE.md` now on `main` (was only on `leave-behind-prep` pre-session).
- gpt-5-mini-on-300-slice plan committed to leave-behind-prep (`5df4f39`) at `docs/active/leave-behind-prep/plans/20260608_gpt5mini_on_oh_300slice.md`. 164 lines, includes Phase 0-3 step-by-step, hard-stop guardrails, asymmetric-comparator caveat, explicit 5-day-plan displacement reasoning. Execution NOT started this session.
- This convo summary itself (`77a5985`, amended in finish-convo turn).
- Docs-vs-reality gap inventory for the claude_researcher workflow: 8 items identified (A: 404-vs-401 diagnostics, B: $TOKEN shell-state trap, C: per-branch STATUS.md routing, D: `docs/active/<branch>/` merge-timing convention undocumented, E: STATE_COVERAGE.md unannounced in CLAUDE.md docs stack, F: mi/nc-style branches-not-in-STATUS systemic gap, G: "push regularly" vs "never push to main" tension, H: no documented stub-row convention). Items A+B candidates for an upstream PR to `claude_researcher/template/RESEARCHER.md`; C-H for `lobby_analysis/CLAUDE.md`.

## Open Questions

- **gpt-5-mini-on-300-slice — execute or defer execution?** Plan committed; execution itself not yet started. Day 2 is today (2026-06-08); if execution doesn't start today, every subsequent day in the revised 5-day shape slides by one (Day 5 → Fri 2026-06-12, *past* Fellowship Thursday). No slack.
- **OpenAI structured-output schema translation risk** is the single highest-impact unknown for plan execution. `LobbyingFiling` has nested Pydantic types (Person, BillReference, LobbyingPosition, LobbyingExpenditure); OpenAI's JSON-schema mode is stricter than Anthropic's tool-use schema. `client.beta.chat.completions.parse(response_format=LobbyingFiling)` is the path-of-least-resistance; if it fails, manual schema flattening can eat the entire Phase 1 budget. Hard-stop at 3hr in the plan is the guardrail.
- **Suhan decisions doc — what's the actual decision list?** Agent's 8-item guess (CPI dispatch, OH extraction, Plural Policy downloads, OH chain composer, FOCAL Plans 3+4, project continuity post-Thursday, Prong-2 state priority, mi/nc fate) needs Dan's filter — honest list might be 2-3 or 10.
- **Post-Fellowship continuity for the project** — is this a Suhan/Analogy decision (continue funding? open-source release? handoff?) or is it Dan's-call?  Frames everything else.
- **`releases/oh/` as a Fellowship-end deliverable — yes or no?** If yes, Option A (dispatch $800 Sonnet now) becomes the right move regardless of mini-validation outcome. If no, Option B (defer + validate) wins on cost grounds.
- **mi/nc resumption plan post-Fellowship** — both branches have real exploratory work, both are stale relative to main. Worth one session each post-Fellowship to either materialize findings into `STATE_COVERAGE.md` or archive cleanly?
- **Plural Policy OH bulk-CSV download** — free, easy, $0-API. Not gated on anything. Worth doing today as a 30-min task, parallel to other work?
- **NY chain composer (`releases/ny/chain/`)** — Day 4 of plan currently allocates time to OH chain composer. NY is more shipped (MVP landed Friday) and arguably should ship first. Worth re-ordering?
- **The 7 statute-only states (CA/TX/CO/IL/WA/FL/NC)** — `STATE_COVERAGE.md` documents them at Prong 1 only. Does Analogy want any of them brought to Prong-2 depth post-Fellowship, or is the WI/OH/NY trio the durable scope?

## Process notes

- **Sycophancy-adjacent failure surfaced + corrected mid-session:** agent's `Bad credentials` diagnostic was correct *for the request actually made* (empty `$TOKEN` in a fresh bash shell), but agent treated the symptom as "PAT expired" and escalated with high confidence. Recovery: Dan's screenshot prompted re-verification with token in scope; agent acknowledged the failure mode (over-confident escalation rather than over-confident agreement, but same root pattern — not stopping to check the cheap diagnostic before recommending a costly action). Logged here because the user-prefs explicitly invite calling out sycophancy patterns, and the asymmetric failure mode (over-eager *escalation*) is worth tracking alongside the more common over-eager *agreement*.
- **Tool-discovery gap:** agent defaulted to GitHub Contents API (per RESEARCHER.md recipes) until Dan suggested testing git clone. Clone worked fine; subsequent work (cherry-pick, multi-file commits, atomic pushes) was substantially cleaner via git CLI. Worth proposing an upstream PR to RESEARCHER.md adding a one-paragraph "prefer git clone for branches-mode write-heavy sessions" subsection.
- **CLAUDE.md `Never make changes directly on main` caught at the right moment** (just before push, after composing all 5 commits). Would have been better to surface the norm *before* composing the commits, but the late-catch worked — Dan gave the sole-Fellow exception and the push proceeded. Procedural lesson: read CLAUDE.md's "Session protocol" + "Coding norms" sections at session start, not just RESEARCHER.md.
