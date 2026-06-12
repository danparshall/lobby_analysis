# RESEARCH_LOG — leave-behind-prep

Newest entries first.

This branch hosts the 5-day pre-wrap cleanup + leave-behind work. Scope:
- Day 1: STATUS reconciliation; triage stale Active rows; STATE_COVERAGE.md drafted; worktree pruning
- Day 2-3: cross-state CPI 5-state extension dispatched in parallel (on `cross-state-cpi-2015-validation` branch, not this one)
- Day 4: OH chain composer + `releases/oh/`; FOCAL Plans 3+4 (likely on dedicated branches)
- Day 5: RESEARCH_ARC.md update; resumption brief; finish-convo on surviving branches

---

## 2026-06-12 — #49 executed: RESEARCH_ARC.md rewritten (Day-5 slot, claude.ai session)

**Session type:** doc rewrite; claude.ai (claude_researcher workflow).

`docs/RESEARCH_ARC.md` rewritten on **main** at `ff498c7` per issue #49's triaged scope (committed to main rather than this branch, following the #48 precedent — the doc describes main's merged state, and this branch is ~90 commits behind after the NY + backend-prototype merges).

**MUST-FIX items:** (1) Status header — "Prong 1 paused 2026-05-24 / gather-first → v2.2" replaced with current truth (Prong 2 leads; Prong 1 in cross-state validation via direct-read on v2.1), with a history note explaining the two supersessions (additive-prompt track resumed extraction on v2.1; SMR-as-canonical mooted the v2.2 gating framing). (2) Prong-1 internals — the retrieval_v2 (Citations) → scoring_v2 path demoted to a clearly-bannered historical-design blockquote (greyed mermaid, "do not build against this"); the actual direct-read path (full bundle in context, YAML SSOT + opaque handles + cell-type-aligned format instructions, `record_cell` parsing, state-keyed 6-chunk × 2-model × 3-run dispatcher) now described as primary; component table marks scoring_v2 "never built; superseded" and retrieval_v2 "shipped but off-path."

**SHOULD-ADD items:** Ralph-loop section reframed "designed, then run" with the empirical record (Phase B iters 1–5 / 4 cell types / additive pattern; Phase A 163 additives; Round 1 180 dispatches / $14.43; post-Phase-1 **19/30 = 63.3%**, per-state breakdown, measured σ_noise ranges); the six failure-mode trends sorted under SMR-as-canonical (1/6/2 = projection-translation engineering, 3/5 = prior-art gaps, 4 = data input). New **Operating principles** section: SMR-as-canonical, Anna Karenina (including a retraction of the old "stairs of leverage" amortization claim), de-jure-only (#51 ref). Prong table + new **three-axis architecture** subsection for Prong 2 (bespoke lobbying / Plural bills / FTM campaign-finance with the #43 sunset caveat); Prong 3 updated for the shipped backend-prototype v0. Phase C table converted to status form (incl. HG 2003-vintage correction; FOCAL 3+4 = #53). Open-questions list pruned of the three Citations-mooted items; replaced with the live set (#50 N=10, Trend-5 §13.74 check, TX corpus, OH IND_203, threshold-for-good-enough, #51, cross-vintage).

Commit message carries `Closes #49`; since it landed directly on main, the issue auto-closed.


## 2026-06-10 — FTM NY sample query (#44): blocked at quota, evidence captured; OH bulk-CSV acquired

**Session type:** browser-assisted data-access session (claude.ai + Claude-in-Chrome); $0 spend, 0 FTM records consumed.

#44's deliverable doc didn't exist on any branch (it was the task's *target*, not a prior artifact). Pre-staged the query harness + writeup skeleton, then hit the real blocker: **FTM account at 1,083/1,000 records/year** (WI LeMahieu run consumed the annual budget; gate counts records, not calls). Gate wording changed post-OpenSecrets-integration — the "Institute will be in contact within two business days" review promise is gone; flat pre-flight refusal captured verbatim in the results doc §7. No @followthemoney.org contact address exists (banner → info@opensecrets.org; Contact Us → info@crp.org); follow-up email sent to both 2026-06-10; **on-site Exemption Request form still untried**. Bonus structural finding for #43 (commented there): followthemoney.org is unreachable from GCP egress (probable datacenter-IP blocking) — a cloud ingest pipeline needs a non-datacenter path. **Data acquired: Plural Policy OH bulk-CSV** (Dan, via login at open.pluralpolicy.com) — closes oh-portal-aprime-batch pending (b). Reminders #49/#54 surfaced, deliberately left fired for next session. Commits: `a26a7a0` `db6422c` `8669a7f` + finish-convo bundle. Convo: [`convos/20260610_ftm_ny_sample_query.md`](convos/20260610_ftm_ny_sample_query.md). Results: [`results/20260610_ftm_ny_sample_query.md`](results/20260610_ftm_ny_sample_query.md).


## 2026-06-09 (later) — Project review (claude.ai) → ticket sweep + STATE_COVERAGE corrections (#48)

**Session type:** review + doc hygiene; claude.ai (claude_researcher workflow), no convo file in-repo.

Full-project review against GitHub state surfaced and **verified** (not just eyeballed): NY release TSVs are deliberately untracked-in-dev (`.gitignore` 31-35, "re-add at merge") — NOT missing; PR #33 (OH) merged 2026-06-05 (STATUS narrative was stale); CO/IL/WA/FL/NC were never dispatched (only 5 state-keyed 2015 result dirs on `cross-state-cpi-2015-validation`); issue #37 is an explicit **merge gate** for `ny-disclosure-explore`; #9 marked closable in-issue 2026-06-07.

**Ticket sweep:** filed **#46–#53** for every outstanding item lacking coverage (NY merge checklist; >100MB hosting policy; STATE_COVERAGE corrections; RESEARCH_ARC triaged rewrite; Round-2 dispatch; Pattern-C splits; OH chain composer + `releases/oh/`; FOCAL Plans 3+4). Close-candidates flagged for Dan: #9 (verified closable), #3 (v1-schema era), #6 (statute half done; portal-snapshot half overlaps #38).

**#48 EXECUTED this session:** `docs/STATE_COVERAGE.md` — Status header rewritten (was "Draft 2026-06-06 / NY skeleton"); CA/TX section header fixed (CO/IL/WA/FL/NC = **pending #50**, not "completed"); post-Phase-1 19/30 (63.3%) added alongside pre-fix Round-1 numbers; de-jure-only decision propagated (#51 ref); NY section gains tracking caveat + #37/#46 merge gates + parties-integration shipped status; NY checklist bimonthly item promoted to MERGE-BLOCKING; new **MI/NC recon section**; new **Access-posture principle** section (promoted from mi/nc branch logs); scorecard rebuilt (NY row had contradicted the NY section header within the same file). `STATUS.md` — Active-table NY row rewritten (chain composer shipped; merge gates), date bumped to 2026-06-09.

**RESEARCH_ARC findings deferred to #49** (Day-5 scope): Status header superseded twice; Prong-1 internals diagram presents the abandoned retrieval_v2→scoring_v2 path as current.



**Plan:** [`plans/release_doc_pattern.md`](plans/release_doc_pattern.md) (authored earlier today by the parity-check session)
**Predecessor convo:** [`convos/20260609_wi_vs_ny_chain_parity.md`](convos/20260609_wi_vs_ny_chain_parity.md)

Fresh-agent execution of the 6-step plan. All 6 steps shipped; 6 commits across 3 branches; ~2 hours wall.

### What shipped

- **Step 1 — `releases/wi/README.md`** on `main` at [`ee507ee`](https://github.com/danparshall/lobby_analysis/commit/ee507eeb0e67ca7c57b515919a4ba360a3c33883). Adds TL;DR, Framework (4 nodes × 6 edges × 3 attributes + 6 quality-convention symbols), per-state "What this release covers for WI" matrix (with all 8 STATE_COVERAGE WI footnotes verbatim), "How to use this release with a Claude agent" naming the two WI silent-mistake traps, and See-also pointers. 119 → 222 lines. Existing Provenance/Files/Aggregates/Caveats/License preserved.
- **Step 2 — `releases/wi/chain/README.md`** on `main` at [`d5bf780`](https://github.com/danparshall/lobby_analysis/commit/d5bf78030a5294e09c9b9106d57ec74a0e522523). New "Conservation rules / aggregator gotchas" section between Schema and "30-second tour" elevates Rule 1 (cell identity is `(semester, principal_id, lobbyist_id, item_id)`, never `bill_id` alone — quantified collision rate ~0.03% from Phase 3.1 measurements) and Rule 2 (don't sum `modeled_hours` across sponsor rows; `modeled_hours_per_sponsor` is the per-sponsor uniform-share modeling assumption, not a disclosed allocation). 5 pandas sample-analyses snippets with protective-pattern comments. New "What this isn't" #7 names the hours-grain (not dollar-grain) shape. 137 → 251 lines.
- **Step 3 — `releases/ny/README.md`** on `ny-disclosure-explore` at [`73490c6`](https://github.com/danparshall/lobby_analysis/commit/73490c6fe58bf9691ca27c74a6f3197e9d387293). Parallel to Step 1 with NY-specific content: TL;DR + Framework + "What this release covers for NY" matrix (all 9 STATE_COVERAGE NY footnotes verbatim) + "How to use" naming NY's three load-bearing gotchas (cell key must include `lobbyist_id` per the −$108.9M smoke-test bug; `comp_per_cell` replicated across sponsor rows; `disclosed_lawmakers` is filing-grain not bill-grain). Existing NY-specific subsections ("Disclosed lawmaker contacts", "`comp_per_bill` — the even-split model", 11 caveats) preserved. 154 → 262 lines.
- **Step 4 — `releases/ny/chain/README.md`** on `ny-disclosure-explore` at [`5a704e6`](https://github.com/danparshall/lobby_analysis/commit/5a704e632f86552460e3a0e859cc2fba36ee5be7). New TL;DR table + audience line + "30-second tour" between Schema and "How dollars are attributed" (explains NY's JOIN-not-IPF construction in three plain-English paragraphs, calls out that per-sponsor replication is 1:1 in 2025 while preserving the rule for forward compatibility). 5 pandas sample-analyses snippets demonstrating cell-key dedupe, `os_matched` filtering, the `disclosed_only_lawmaker_count` base-rate-resistant signal, coalition decomposition, and external joins via `os_bill_identifier`. "Regenerating" section renamed "Reproducer" with section divider for paste-ability, matching WI chain README style. Headline-finding section skipped per plan's "nice-to-have, skip if it would require querying the TSV" guidance. Existing rigor (Conservation rules, Disclosed-vs-inferred semantic warning, Honest limitations, Bill-id normalization) preserved verbatim. 196 → 343 lines.
- **Step 5 — `docs/STATE_COVERAGE.md`** on `main` at [`bdabfa2`](https://github.com/danparshall/lobby_analysis/commit/bdabfa2ae2c4538bd46bf274e8a2ff11e1f62779). Adds two bullets to the See-also header at the top of the file linking the per-state release READMEs as "Suhan-droppable primers." No structural changes; per-state matrices in STATE_COVERAGE.md are unchanged (the duplication into per-state release READMEs is by design — see plan's "Architectural decision").

### Suhan-droppable artifacts

- **WI:** [`releases/wi/`](https://github.com/danparshall/lobby_analysis/tree/main/releases/wi) (on `main`) — drop the directory into a fresh claude.ai Project; the README's framework + matrix + How-to-use + chain README cover the cold-context use case. Upload at minimum `README.md` + `chain/README.md` + `chain/WI_chain_2025.tsv`.
- **NY:** [`releases/ny/`](https://github.com/danparshall/lobby_analysis/tree/ny-disclosure-explore/releases/ny) (on `ny-disclosure-explore`, not yet merged to main). Upload at minimum `README.md` + `chain/README.md` + `chain/NY_chain_2025.tsv`; add `NY_filing_parties_lobbied.tsv` if the question involves disclosed lobbying contacts beyond per-bill sponsors.

### Plan acceptance criteria status

Plan §"Acceptance criteria (whole plan)" enumerates three cold-context tests. The doc work is shipped; actual cold-Project validation is for Dan / Suhan to run when convenient. Self-review:

1. **"Top principal by chain weight on AB 50" cold-Project test (WI).** The new chain README's Conservation rules section names the cell-identity rule + uniform-share-is-a-modeling-assumption framing, and Sample 1 demonstrates the dedupe-then-sum pattern explicitly. A cold agent that reads the chain README should produce a correct snippet. Untested in this session.
2. **"Did Doordash lobby Senator X about S 1234?" cold-Project test (NY).** The chain README's "Disclosed vs inferred" section names `sponsor_in_disclosed_set=True` as base-rate, not bill-specific, and Sample 3 demonstrates the `disclosed_only_lawmaker_count` discipline. A cold agent should correctly caveat. Untested.
3. **"Read just `releases/<state>/README.md` and explain edges/attributes."** The Framework + matrix + footnotes in each per-state release README are self-contained and require no other files. Footnote count: WI 8, NY 9 — all verbatim from STATE_COVERAGE.

### Process notes

- Initially mis-diagnosed a PAT-scope issue at session start (env vars not persisting across `bash_tool` calls — each tool call is a fresh shell; my early curl commands hit empty-token endpoints and 404'd). Dan pushed back with a screenshot; I re-verified inline and confirmed PAT access is correct. Note for future fresh-agent sessions on claude.ai: `bash_tool` calls do NOT persist env vars; inline `TOKEN=...; curl ...` in a single invocation.
- One plan deviation: Step 6's RESEARCH_LOG entry placement guidance ("below the existing 2026-06-09 entry from the parity-check session") was anchored to the state of the file at plan-authoring time. Two newer 2026-06-09 entries (gpt-5-mini work) have since been added above the parity-check entry. Per the file's "Newest entries first" convention, this entry is inserted at the very top.
- Plan §"Risks / known gotchas" item 3 (sample analyses must avoid showing the gotcha as correct): each snippet was reviewed before commit; all use dedupe-to-cell-key before sums when the sponsor isn't the group-by axis. WI Sample 2 (group-by-sponsor case) uses `modeled_hours_per_sponsor` without dedupe; NY Sample 2 (also group-by-sponsor) uses cell-key dedupe explicitly as a "no-op safety net" since N=1 in 2025 data but the discipline still teaches the right pattern.

### Open follow-ups (per plan §"After completion")

- No pre-existing GH issues closed by this work (#42, #43, #44 remain open as cross-state-infra successor tasks).
- When OH chain composer ships and creates `releases/oh/`, the same 3-doc pattern applies. Either extend this plan or write a follow-up `oh_release_doc_pattern.md` that re-uses the same 5 section additions for OH (TL;DR + Framework + What this release covers for OH + How to use + See-also) + the chain README equivalent.

## 2026-06-09 (PM) — gpt-5-mini reasoning_effort threading + 3-arm dispatch (medium/low/minimal × 100)

**Convo:** [`convos/20260609_gpt5mini_reasoning_effort_three_arm_dispatch.md`](convos/20260609_gpt5mini_reasoning_effort_three_arm_dispatch.md)

**Results:** [`results/20260609_cross_arm_agreement.md`](results/20260609_cross_arm_agreement.md)

**Predecessor:** [`convos/20260609_gpt5mini_day2_phase0_hardening_partial_run1.md`](convos/20260609_gpt5mini_day2_phase0_hardening_partial_run1.md) — that session left the dispatch stopped at 55/305 with a cost-over-projection finding; this session followed up.

**Context:** The morning session diagnosed mini cost as 2-3× plan estimate driven by ~3× completion tokens vs Sonnet. The likely root cause was unset `reasoning_effort` → API default `medium` → mini paying for reasoning tokens that are billed as completion but invisible in the structured output. Confirmed by inspecting on-disk artifacts before any new dispatch: bytes-per-completion-token across 5 matched pairs was 1.1-1.5 (vs 2.5-4 typical for dense JSON), consistent with the reasoning-token-overhead hypothesis.

### Code changes (4 commits)

- `extract_openai`: keyword-only `reasoning_effort` param; capture `reasoning_tokens` + `reasoning_effort` in usage dict; default `None` omits the kwarg from `chat.completions.parse` for byte-identical legacy semantics. 4 mock-boundary tests.
- `pipeline_openai`: thread `reasoning_effort` through to the extractor; lands in `extraction_run.json` alongside per-filing tokens.
- `dispatch`: `--reasoning-effort {minimal,low,medium,high}` flag couples to `run_label` (so each arm writes to `mini_<effort>_run_<N>_*`); `--max-concurrent N` adds `ThreadPoolExecutor` (default 1 preserves byte-identical serial path); `_process_one_filing` extracted as shared worker; `post_run1_sanity_diff` parameterized on prefix. 7 tests covering parallel safety, resume concurrency, per-filing failure isolation, and sanity-diff prefix correctness.
- `scripts/_completed/rename_mini_run1_to_medium.py`: idempotent rename of the 55 partial-Run-1 dirs from `mini_run_1_*` → `mini_medium_run_1_*` (they were dispatched at API-default reasoning, which is medium). `--dry-run` + `--reverse` supported.

### Cross-arm field agreement analyzer (5th commit)

`scripts/gpt5mini_oh_300slice_cross_arm_agreement.py` + 7 tests. Per the 2026-06-09 design call:
- Exact equality after JSON canonicalization; no semantic normalization layer (date format, whitespace, etc.).
- Both-null is **NOT** counted as agreement — it gets its own bucket, so null asymmetry stays visible.
- One-null counts as disagreement.
- Named-object fields compared by `.name`; list fields compared by length.
- `agreement_rate = both_emitted_agree / (both_emitted_agree + both_emitted_disagree)` — null cells excluded from denominator so "when both emit, do they agree?" measures separately from "do they both emit?"

### Findings — cost (n=100 per arm, full-corpus extrapolation across 45,605 OH AERs)

| arm | $/filing | full-corpus | vs Sonnet $800 |
|---|---|---|---|
| Sonnet baseline | $0.0175 | $800 | reference |
| mini medium | **$0.0079** | **$359** | 2.2× cheaper |
| mini low | **$0.0047** | **$212** | 3.7× cheaper |
| mini minimal | **$0.0041** | **$188** | 4.2× cheaper |

Minimal hits a cost floor — dropping from low to minimal cut completion tokens 15% but only 12% cost, because the structured-output JSON serialization itself has a ~600-800 completion-token floor that reasoning_effort can't compress.

### Findings — quality (cross-arm agreement on the 100-filing intersection)

**Minimal is below the quality floor**: 97-98% null on `reporting_period_start`/`_end`. Not abstention calibration — the model isn't bothering with the field. **Drop minimal from the leave-behind framing.**

**Medium vs Sonnet on fields where both emit**: 100% agreement on every identity field (filer_role, filing_id, filer_person), 100% agreement on every dollar amount (`total_expenditure` 14/14, `is_itemized` 5/5), 95-100% on list-length and entity-name fields. The genuine gap is `reporting_period_start` (85.1%) and `_end` (90.6%) — 13 and 8 disagreements out of 74-77 both-emitted cells. Worth eyeballing a few to see if they're 1-day-off normalization or genuinely different reads.

**Low vs Sonnet**: similar shape to medium but with worse null asymmetry (`reporting_period_end` one_null 32/100 vs 15/100 on medium). Cost-quality tradeoff is real.

**`extraction_warnings` 30-32% agreement is a brief-design difference, not a quality issue** — mini was instructed to emit interpretive notes; Sonnet emits fewer. Not a worry.

**`filer_organization` is 100% both-null across all arms** — OH AERs don't use that field; the employer lands in the dedicated `employer` slot. Worth flagging so it doesn't surface as a false issue later.

### Long-tail filing 1423176 gets *more* expensive at lower reasoning_effort

| arm | duration | completion tokens | cost |
|---|---|---|---|
| mini low | 181s | 13,698 | $0.0289 |
| mini minimal | **244s** | **21,427** | **$0.0443** |

Pathological. Mini spins in output mode when it can't reason its way through. Full-corpus extrapolations using the median understate the tail; even at 1% pathological filings, that's $20-30 of long-tail cost regardless of setting. Batches API + transient retry (issue #35) is the principled fix.

### Decisions

- **Drop minimal as a shipping setting.** Quality below floor. Keep the data for the writeup as evidence the floor exists.
- **Medium is the production-defensible setting** ($359 full-corpus, 85-91% reporting_period agreement when both emit, 100% agreement on identity + dollar fields).
- **Low stays in the writeup as the budget option** for consumers who can tolerate 30%+ reporting_period null rates.
- **No 3-pass self-consistency** on each arm. The 3-arm × 1-pass shape is already a cross-setting consistency check; burning 6 more passes ($6-8) for inter-run noise floor isn't worth it for the writeup.

### Spend this session

- Arm A medium (45 fresh + 55 resume): $0.3546
- Arm B low (100 fresh): $0.4652
- Arm C minimal (100 fresh): $0.4132
- **Total: ~$1.23 OpenAI** (no Anthropic)

### Next steps

- Spot-check the 13-16 reporting_period disagreements on medium (1-2 filings; ~10 min) to see if a normalization layer would tighten the agreement number.
- Pull filing 1423176's raw HTML and read it; understand the long-tail pathology shape.
- Write Suhan-facing summary using medium-only framing.

### Continuation: filer_organization XOR fix + reporting_period root-cause + briefv2 fix

After the 3-arm cross-arm analysis landed, the session continued into root-causing the reporting_period disagreements. Three findings, summarized — full narrative in the convo doc.

**Schema/brief: filer_organization is independent of filer_person, not XOR** (commit `c541d91`). Cross-arm showed 100% both-null on `filer_organization`. Initial read was "regime-shape correct for OH" but Dan pushed back: the schema docstring framing ("Set if the filer is a natural person" / "Set if the filer is an organization") read as XOR, and the OH brief's "DO NOT put it in filer_organization" prohibition reinforced it. For WI/NY where a registered lobbyist legitimately disclosures alongside their firm, XOR throws away data. Edits: docstrings rewritten as independent in `models/filings.py`; OH brief's prohibition replaced with positive regime-shape guidance; results doc annotated. No validator was enforcing XOR — purely social. Win is structural for downstream pipelines; OH outputs unchanged.

**Root cause of reporting_period disagreements: OH semesterly shorthand misread.** The spot-check script (`f83b265`) classified 12 of 13 medium-arm disagreements as `large_delta` — mini emitting structurally malformed dates like `0501-08-25` (year 501 AD). Raw HTML inspection of filing `1433534` confirmed the source field: `Reporting Period: May-Aug25`. Mini parsed this literally as "May 01 to Aug 25, year `0501`" instead of "May 1 — Aug 31, 2025". Sonnet recognized the OH convention. Pathology was worse at lower reasoning_effort (minimal failed harder → 98% null on this field).

**Brief surgery + schema validator (commits `5a87c79` + `4d0c930`):**
- New brief step 7 (per ORC §101.72) maps OH's three semesterly periods to ISO date ranges. Brief sha `8e564091 → 5606c835`, auto-distinguishing pre/post-fix outputs.
- `ReasonableDate` annotated type (year ∈ [1990, current_year + 1]) on all 10 date fields. Raises ValueError on garbage; turns silent data corruption into loud extraction failure. 9 new tests.

**briefv2 verification on n=100** (commits `e5bce15` / `0bc54ef` / `ac906a4`): 26 known-failures → 100% recovery. Full-medium top-up → 74 new + 26 resume-skip, 0 reporting_period disagreements across the arm. **No regressions on the 74 previously-good filings.**

**Bonus finding: prescriptive brief is also cheaper.** Per-filing cost dropped from $0.0079 → $0.0066 under briefv2 despite the brief being longer. Mini spends fewer reasoning tokens once it has the explicit mapping. Full-corpus extrapolation moves from $359 to **~$301**.

**Cross-arm briefv2 results** (commit `bfe64fa`, doc `20260609_cross_arm_agreement_briefv2.md`):

| field | sonnet vs medium (original) | sonnet vs medium_briefv2 |
|---|---|---|
| reporting_period_start | 85.1% | **100%** |
| reporting_period_end | 90.6% | **100%** |
| filer_role / filing_id / filing_action / filer_person / filed_date | 100% | 100% |
| employer / expenditures / gifts | 99-100% | 99-100% |
| positions, engagements | 95-96% | 96% |
| is_current | 98% | **94%** ← minor regression |
| extraction_warnings | 30% | **13%** ← brief perturbed warning emission |

**Two side-effects worth flagging:**

- `is_current` 98% → 94%: brief change introduced 4-6 new disagreements on a deterministic boolean field. Worth a 5-min spot-check before writeup; probably a brief tweak ("True unless source explicitly marks the filing as amended") fixes it.
- `extraction_warnings` 30% → 13%: brief perturbed warning patterns. Probably benign churn; one-rid eyeball confirms or denies.

**Decisions reaffirmed:**

- Ship medium with briefv2: $301 full-corpus, 100% reporting_period agreement, 99-100% on identity/dollar/list-count fields.
- Drop minimal from shipping framing (pre-existing decision; briefv2 doesn't change it).
- Keep low data on disk; de-emphasize in writeup unless we re-test at briefv2 (~$0.40, ~5 min).
- Schema validator stays regardless — defense-in-depth.

**Incremental spend (continuation):** $0.16 known-failures + $0.50 full-medium top-up = $0.66.
**Session total: ~$1.89 OpenAI.** Cumulative on branch: ~$2.20 including this morning's $0.31 Anthropic.

**Pending follow-ups before writeup:**

- is_current spot-check (the 6 disagreement rids)
- extraction_warnings content sanity-check (one rid)
- Decide whether to re-test low at briefv2
- Filing 1423176 deep-dive (long-tail pathology, source-content-driven)
- Write Suhan-facing summary
- STATUS.md update

### Continuation 2: is_current spot-check → brief-v3 → is_itemized side effect (next-session gate)

After the doc-update commit, the open follow-ups got addressed. Built two read-only diagnostic scripts: `is_current_spotcheck.py` (commit `2944121`) + `extraction_warnings_inspect.py`.

**is_current finding:** 6/6 disagreements were sonnet=True / briefv2=False on filings both arms call filing_action=original / supersedes=None. Unidirectional conservatism bias from briefv2's longer prompt. No text in any brief revision mentions is_current — regression came from briefv2 feeling more rule-heavy and mini becoming less willing to default True without positive evidence.

**extraction_warnings finding (NOT a quality regression):** histogram shows briefv2 emits 0 warnings on 39/100 filings vs 5/100 sonnet, 2/100 original. Lost warnings are procedural confirmations sonnet emitted ("Reporting period given as 'Jan-Apr25', expanded to ..."; "Section II shows No expenditures"). Brief-v2's explicit period-expansion instruction made these no longer "inferences worth flagging" — mini stopped narrating the canonical move. Open framing question for writeup: lost audit-trail signal (concern) vs noise-stripped output (feature).

**Brief-v3 (commit `211c576`):** new step 8 — "Default is_current=True for original filings. Set False ONLY if source explicitly indicates supersession." Brief sha `5606c835` → `57ac0b6c`.

**Brief-v3 verification on full n=100 cross-arm (commit `bfe64fa` + results doc `20260609_cross_arm_agreement_briefv3.md`):**

| field | brief-v2 vs sonnet | brief-v3 vs sonnet | move |
|---|---|---|---|
| is_current | 94% | **100%** | targeted fix generalized |
| reporting_period_start/end | 100%/100% | 100%/100% | no leak |
| **is_itemized** | (5 agree / 34 one-null / 61 both-null) | **(0 agree / 39 one-null / 61 both-null)** | **new side effect** |
| positions | 96% | 94% | -2 (noise) |
| extraction_warnings | 13% | 14% | unchanged |
| everything else | ≥99% | ≥99% | unchanged |

**The is_itemized side effect — open gate.** Brief-v3 made the field fully abstain. briefv2 emitted on 5/100 (all 5 agreeing with sonnet); briefv3 emits on 0. Three readings:
1. Brief-v3 broke a working signal → iterate to brief-v4.
2. Sonnet was guessing. is_itemized may be semantically undefined when Section II is empty (~95% of OH AERs). briefv3's abstention is correct behavior → ship briefv3 unchanged. **Strong prior.**
3. Field too low-coverage to matter (sonnet only emits on 39/100, mini-briefv2 on 5).

**Plan doc** [`plans/20260609_is_itemized_investigation_and_writeup.md`](plans/20260609_is_itemized_investigation_and_writeup.md) walks the next session through the investigation: spot-check script identifies the 5 rids → 5-min raw-HTML eyeball categorizes each as GROUND_TRUTH_EMITS / ABSTAINS / AMBIGUOUS → decision tree ships briefv3 unchanged or motivates brief-v4. Plan also covers the Suhan-writeup that follows.

**Issue [#54](https://github.com/danparshall/lobby_analysis/issues/54)** filed for filing 1423176 cross-arm cost pathology (5-10× median across every config). Labels `task` + `bug`. Asks for raw-HTML eyeball + decision on denylist mechanism.

**Pattern worth naming: brief-iteration whack-a-mole.** Three brief revisions, three rounds of "fixed one field, perturbed another" (v2: fixed period, broke is_current + reduced warnings; v3: fixed is_current, broke is_itemized). Not random — each prescriptive addition makes mini treat the brief as more complete-specification-of-what-to-emit, and unmentioned fields under-emit at the margin. Future brief revisions need a $0.66 full-medium re-extract + cross-arm scan as iteration cost.

**Incremental spend (continuation 2):** $0.05 is_current targeted retest + ~$0.66 briefv3 full-medium = ~$0.71.
**Session total: ~$2.60 OpenAI.** Cumulative on branch: **~$2.91** including this morning's $0.31 Anthropic.

**Next-session pending:**

- is_itemized investigation (spot-check + 5-min HTML eyeball) — gates everything else
- Decide on extraction_warnings framing for the writeup (lost signal vs noise-stripped)
- Suhan writeup itself
- (Conditional) brief-v4 if is_itemized investigation says GROUND_TRUTH_EMITS
- Filing 1423176 denylist mechanism design (#54, separate)
- STATUS.md update (the Active table row says "Day 2 DONE" which is now optimistic — it's "Day 2 DONE pending one investigation step")

---


## 2026-06-09 — gpt-5-mini OH 300-slice Day 2: Phase 0 hardening + partial Run 1 (55/305 then stop)

**Originating discussion:** session conversation 2026-06-09 (this is a separate concurrent session from the WI vs NY parity check below; both on the leave-behind-prep branch).

**Convo:** [`convos/20260609_gpt5mini_day2_phase0_hardening_partial_run1.md`](convos/20260609_gpt5mini_day2_phase0_hardening_partial_run1.md)

**Results note:** [`results/20260609_gpt5mini_oh_300slice_partial_run1.md`](results/20260609_gpt5mini_oh_300slice_partial_run1.md)

**Handoff data (tracked copy of gitignored outputs):** [`handoff/`](handoff/) — 55 mini Run 1 outputs + 5 re-Sonnet runs (this session) + 10-sample of pre-existing Sonnet baselines for matched-pair diffing. Restoration recipes in `handoff/README.md`.

**Context:** Day 2 of the gpt-5-mini cost-floor validation per the 2026-06-08 plan. Worked through Phase 0 pre-flight, surfaced + fixed several issues, launched Run 1 of the 3x mini dispatch, then stopped at 55/305 by user direction after the per-filing cost projection materially exceeded the plan's estimate.

### Hardening done before Phase 2 (committed + pushed)

- Patched RUNBOOK_day2.md to call new operator scripts instead of inline `python3 -c` / quoted heredocs (the 0.4 heredoc was actually broken — quoted PY delimiter killed shell expansion).
- New operator scripts: `gpt5mini_oh_300slice_preflight.py`, `gpt5mini_oh_300slice_smoke_diff.py`, `gpt5mini_oh_300slice_cost_check.py`, `gpt5mini_oh_300slice_reconstruct_summary.py`.
- Pinned `MODEL_ID_DATED = "gpt-5-mini-2025-08-07"` (only dated mini variant visible on the account; undated alias rotates and would confound 3x consistency).
- Re-extracted the 5 legacy-schema Sonnet baselines (1405684, 1427844, 1459616, 1492516, 1492518 — written before commit e5d2da3 added `employer` / `extraction_warnings` / `total_hours_*`); 305/305 now modern.
- `_latest_filing_json` switched to mtime-based selection in 4 places — name-sort of bare-UUID run_ids was misnamed-as-latest; 1492516 was the smoking gun (legacy uuid `abc274e2` lex-sorted after the new `62802a47`).
- Run_id format now date-prefixed (`YYYYMMDDTHHMMSS_<uuid8>`, with `run_label_` first for the OpenAI side to preserve startswith() filters).
- Smoke-diff symmetric WARN (key-set asymmetry in either direction is informational; only wild array-length divergence is a hard fail — original strict check baked in "Sonnet is ground truth" which the validation explicitly doesn't assume).

### Findings (the reason we stopped)

- **Mini per-filing cost: $0.0070** (4,585 prompt + 2,933 completion tokens avg, n=55). Plan estimate implied $0.0022-$0.0033 (i.e. ~$100-150 for full 45,605 corpus). Actual full-corpus 1x mini projection: **$317**.
- Sonnet vs mini *ratio* still favorable (~2.5x cheaper, vs the 5-8x the plan hoped for). $800 Sonnet → $317 mini is real cost reduction, just smaller than the plan's leave-behind framing implied.
- Driver: mini emits **~3x more completion tokens than Sonnet** at the same input. Sonnet's $800 implies ~1K output tokens/filing assuming prompt caching on the brief; mini emits ~2,900. Cause not yet investigated — possibilities in results note (nested-entity full skeletons, verbose extraction_warnings, new schema fields).
- Dispatcher is serial — ~32s per filing → ~2.7 hr per pass at 305 filings. HTTP-bound; a thread pool would cut to ~15-20 min per pass.

### Next steps (deferred, not for this session)

- Parallelize the dispatcher (10-way ThreadPoolExecutor on `run_one_pass`) before resuming.
- Investigate why mini is verbose — look at any one mini output vs the Sonnet baseline for the same report_id; the difference should be visible.
- Decide whether to (a) resume the 3-pass validation at higher actual cost (~$6-7, fine in absolute terms), or (b) trim the schema/brief to reduce verbosity first, or (c) reframe the leave-behind for Suhan around the actual $317 number.

### Decisions Made

- Stop Run 1 mid-pass rather than spend $2 to complete a serial pass on data that's projected to overshoot the budget — partial data is sufficient for the verbosity investigation.
- Don't parallelize in this session; user explicitly asked another agent to take that on.

### Day-2 spend

~$0.72 total: $0.31 Anthropic (5 re-Sonnet runs for legacy-baseline cleanup) + ~$0.41 OpenAI (smoke runs + the 55-filing partial Run 1).

---

## 2026-06-09 — WI vs NY chain parity check; two cross-state-infra tasks captured

**Originating discussion:** session conversation 2026-06-09 (third leave-behind-prep session).

**Convo:** [`convos/20260609_wi_vs_ny_chain_parity.md`](convos/20260609_wi_vs_ny_chain_parity.md)

**Context:** Dan opened the session asking whether WI had reached parity with NY's chain — referencing the 2026-06-08 NY `parties_lobbied` integration on `ny-disclosure-explore`. Session walked through a parity comparison + an IPF-on-dollars false start + cross-state shareable-infrastructure framing, ending with two GH issues captured for successor-Fellow handoff.

### Topics Explored

- WI chain (`releases/wi/chain/`, on main) vs NY chain (`releases/ny/chain/`, on `ny-disclosure-explore`, not yet merged) artifact-level comparison
- Three categories of difference: structural (NY's `parties_lobbied` has no WI analog; WI lobbying disclosure doesn't require disclosing which lawmakers were contacted), modeling-architecture (NY = clean JOIN; WI = IPF because WI lobbyists report only aggregate hours), and a mis-framed "fixable" $-attribution gap
- Dan's IPF-on-dollars idea — falsified because WI lobbyists file Time Reports only (no compensation-received field) → no column marginals; IPF underdetermined without external lobbyist-revenue data
- Hours ∝ spending rule of thumb: structurally untestable across all 10 priority states (each state discloses one of {$, hours} but not both at per-(lobbyist, client, bill) grain)
- CFIS as WI-specific name vs FTM as 50-state aggregator (with API-only access surface, basic-tier quota, Institute review on quota-exceed)
- FTM-in-OpenSecrets-integration sunset mode (banner observation that post-dates the wi-cfis-scoping work — long-term API contract may not survive the merger)
- Architectural axis count: lobbying disclosure (per-state, bespoke), bill sponsorship (shared via Plural Policy), campaign finance (shareable via FTM — not yet built)

### Provisional Findings

- WI chain is structurally complete given WI's disclosure shape. The `comp_per_cell` column I initially proposed would have stacked 4 layers of modeling (IPF + proportional bill attribution + per-sponsor split + per-principal $/hr rescaling) under a number that reads as disclosed — explicitly rejected as surface parity.
- WI vs NY are at parity *relative to their respective data sources*. Differences are data-shape, not pipeline-completeness, and not "gaps" in either direction.
- Cross-state shareable infrastructure confirmed on two of three chain legs: Plural Policy (already in active use on `wi-allocation-matrix` and `ny-disclosure-explore`), FTM (50-state, not yet built). Lobbying disclosure remains per-state Anna Karenina by data-acquisition shape.
- FTM API may not be the long-term contract — site is "not maintained as we integrate with OpenSecrets"; URL/endpoint pattern may change. Worth confirming before #43 implementation starts.
- The third attribute axis is **Stance** (support/oppose/monitor) per STATE_COVERAGE.md — not Counts/Frequency. Structurally absent in WI/NY/OH; chain detects activity, not composition.
- Per-state release-doc architecture decided (3-doc pattern). Suhan-droppable constraint requires self-contained release dirs; the ~15-line framework gets duplicated into each state's release README rather than deferring to STATE_COVERAGE.md. Acceptable cost at N=3 states.

### Results

- GH issue [#42](https://github.com/danparshall/lobby_analysis/issues/42): "Extract Plural Policy bulk-CSV ingest into shared cross-state library"
- GH issue [#43](https://github.com/danparshall/lobby_analysis/issues/43): "Build reusable FollowTheMoney ingest for cross-state campaign-finance leg" (body updated with the OpenSecrets-integration finding)
- GH issue [#44](https://github.com/danparshall/lobby_analysis/issues/44): "[2026-06-10] Pull FTM NY sample query to validate 50-state portability" — closes the WI-vs-NY FTM validation asymmetry
- Plan: [`docs/active/leave-behind-prep/plans/release_doc_pattern.md`](plans/release_doc_pattern.md) — per-state Suhan-droppable release-doc pattern, 22.3KB / 314 lines, 6-step execution spec for fresh-agent pickup

### Next Steps

- Day 4 (OH chain composer + `releases/oh/`) remains the next leave-behind action item per the 2026-06-08 revised 5-day plan. This session's work is captured-task externalization, not Day 4 execution.
- If Day 5 (RESEARCH_ARC.md update) covers Anna Karenina principle propagation, fold in the cross-state shareable axes (Plural Policy + FTM) finding from this session as a sub-point.

### Decisions Made

- No WI chain `comp_per_cell` work. Rejected as surface-parity dressing.
- Two tasks externalized to GH issues (#42, #43) rather than absorbed into Day 4/5 scope — they're successor-Fellow handoff work, not pre-Thursday work.

---

## 2026-06-08 — STATUS sweep to main + gpt-5-mini cost-floor plan

**Originating discussion:** session conversation 2026-06-08 (second leave-behind-prep session).

**Convo:** [`convos/20260608_status_sweep_and_gpt5mini_plan.md`](convos/20260608_status_sweep_and_gpt5mini_plan.md)

**Context:** Session opened on the question "what's our status on leave-behind-prep" but pivoted twice. First to STATUS propagation (Dan: "make sure main knows about this branch + state branches"), then to OH extraction decision space (Dan working through the "$800 dispatch — yes or no?" question for an eventual Suhan decisions doc).

### Topics Explored

- Session-start credential diagnostic failure (empty `$TOKEN` in fresh bash shell looked like an expired PAT; agent over-confidently escalated; corrected after Dan's screenshot)
- Git CLI vs Contents API as the user-repo interaction surface (CLI wins for branches-mode work)
- CLAUDE.md `Never make changes directly on main` norm vs sole-Fellow exception
- OH extraction cost decomposition: $800 = single-model Sonnet-4-6 already; Batches+caching brings it down from $1,600 floor
- 4-node × 6-edge × 3-attribute framework as the right unit for the OH-extraction decision
- Which OH edges come from AER data (4 of 5 populated edges) vs Plural Policy (`lawmaker↔bill`, free)
- Ask-then-extract vs extract-then-ask framing as orthogonal to model choice
- Classical NLP vs LLM extraction: hybrid possible post-Fellowship, false economy before Thursday
- Vendor swap cost analysis: GPT-5.5 *more* expensive than Sonnet; flagship swaps don't save money
- Tier-drop cost analysis: GPT-5-mini ~6-12× cheaper than Sonnet → ~$80-150 full corpus IF validation passes
- Benchmark-substitution trap: SWE-bench / GPQA scores irrelevant for AER extraction; only relevant signal is prior σ_noise work on `extraction-harness-brainstorm`
- Asymmetric comparator design: mini 3x for σ_noise, Sonnet 1x as reference (saves +$30 / +4hr but limits claimable findings)

### Provisional Findings

- STATUS.md on main was 4 commits behind `leave-behind-prep` pre-session (the Day 1 reconciliation hadn't propagated). Treating main's STATUS as session-start canon for fresh sessions required cherry-picking the Day 1 commits across.
- `mi-disclosure-explore` (stale base 2026-06-02) and `nc-disclosure-explore` (stale base 2026-05-25) exist on origin but appeared in neither STATUS table on either branch — real gap that Day 1's reconciliation missed. Both need rebase or merge-main before resuming.
- No `fl-*` branch exists; FL is in `STATE_COVERAGE.md`'s "Prong 1 statute SMR only" bucket along with 6 other states.
- OH full-corpus extraction at $800 is **already optimized** (single-model Sonnet + Batches + prompt caching). Tier-1's two-model side-by-side was a one-time validation, not the production config.
- Flagship vendor swap doesn't reduce cost: GPT-5.5 at $5/$30 is more expensive than Sonnet at $3/$15; GPT-5.4 input ~15% cheaper but task is output-heavy.
- Tier-drop is the real cost lever: GPT-5-mini at $0.25/$2 = ~12×/7.5× cheaper than Sonnet → ~$80-150 projected for full OH corpus IF mini handles AER extraction adequately. **Currently no evidence either way for AER.**
- For OH, 4 of 5 populated lobbying-chain edges come from AER data; `lawmaker↔bill` is the exception (Plural Policy bulk-CSV, $0).
- The $800 is *not* the cost of `releases/oh/` — extraction is one of three pending items: (a) Sonnet full-corpus run [$800], (b) Plural Policy OH bulk-CSV [$0], (c) chain composer [Day 4 leave-behind work, time only].

### Results

- **5 commits pushed to `origin/main`** (`83ad0fe` → `6cc5bf0`): cherry-picked Day 1 STATE_COVERAGE.md + STATUS reconciliation + Day 1 finish-convo + NY skeleton fill from this branch + one new commit adding mi/nc stub rows. STATUS.md on main now lists all 6 live branches.
- **`docs/STATE_COVERAGE.md` now on main** (was leave-behind-prep-only pre-session).
- **gpt-5-mini 3x validation plan committed** (`5df4f39`) at [`plans/20260608_gpt5mini_on_oh_300slice.md`](plans/20260608_gpt5mini_on_oh_300slice.md). 164 lines, Phase 0-3, hard-stop guardrails, asymmetric-comparator caveat documented.

### Decisions Made

- **STATUS propagation strategy:** cherry-pick all 4 leave-behind-prep commits onto main as-is (not surgical-pick STATUS hunks). Day 5 wrap-up merge will be cleaner; `docs/active/leave-behind-prep/` files landing on main early is acceptable given the leave-behind nature.
- **mi/nc stub-row convention:** "exists, scope TBD" + latest-commit + merge-base metadata. Candidate convention worth standardizing for future stub additions.
- **Direct push to main:** authorized as sole-Fellow exception. CLAUDE.md norm preserved for the multi-committer rationale that no longer applies.
- **gpt-5-mini validation: 3 runs of mini, Sonnet stays at 1x.** Asymmetric comparator with explicit caveat — supports σ_noise + agreement claims, NOT ranked accuracy.
- **5-day plan revised:** Day 2 mini-validation → Day 3 cross-state CPI 5-state dispatch → Day 4 OH chain composer + `releases/oh/` (FOCAL Plans 3+4 cut) → Day 5 RESEARCH_ARC + resumption brief. No slack — Day 5 lands on Thursday.
- **Suhan-facing doc genre:** *decisions doc*, not weekly-update status doc. Per-decision structure with options + recommendation + deadline. Distinct from Day 5 resumption brief. Decisions doc not yet drafted.

### Next Steps

- **Execute gpt-5-mini plan today (Day 2).** Hard-stop at Phase 1 + 3 hours if OpenAI structured-output schema translation blocks. If hard-stop hit, write up the engineering blocker as a result file and recover to Day 3.
- **Day 3 (Tue 2026-06-09):** Cross-state CPI 5-state extension dispatch on `cross-state-cpi-2015-validation` (~$15, CO/IL/WA/FL/NC at vintage 2015).
- **Day 4 (Wed 2026-06-10):** OH chain composer (`src/lobby_analysis/oh/`, JOIN-based per Anna Karenina) + `releases/oh/`. Requires Plural Policy OH bulk-CSV downloaded first (~30 min task, free, parallel-able with anything).
- **Day 5 (Thu 2026-06-11):** RESEARCH_ARC.md update with Anna Karenina + SMR-as-canonical principle propagated; resumption brief; finish-convo on surviving branches.
- **Suhan decisions doc** still pending. Genre clarified this session; decision list itself awaits Dan filter. Likely a Wednesday-or-Thursday task; results from Day 2 mini-validation feed directly into the OH-extraction option framing.

---



**Originating discussion:** session conversation 2026-06-06 (this branch's first session).

**Context:** Fellowship ends ~2026-06-11 (presentation Thursday). Three active fronts confirmed empirically:
1. `cross-state-cpi-2015-validation` — 5 states dispatched + trends-at-N=5 doc landed
2. `ny-disclosure-explore` — `parties_lobbied` MVP shipped; chain composer pending
3. `oh-portal-aprime-batch` — extraction pipeline + 300-slice validation done; chain composer pending

Contribution data: Dan 699 non-merge commits (98%); Amina 13 (1.8%); Gowrav 4 (0.6%).

**Convo:** [`convos/20260606_take_stock_and_day1_hygiene.md`](convos/20260606_take_stock_and_day1_hygiene.md)

### Topics Explored

- Pre-flight project stocktake (STATUS Active table reconciliation; 3 active fronts identified vs 4 stale rows)
- 5-day plan shaping (Fellowship-ends-project-continues scope; substantive-push-with-day-1-hygiene framing)
- Cross-state CPI 2015 N=5 trends doc — Trends 1/2/6 unpacked and then reframed per SMR-as-canonical principle
- NY scope — "full chain like WI" with "+ spending"
- OH portal data structure (OLAC discovery; AER detail page; Section I bills; Section II.A-D itemized gifts/meals)
- Plural Policy / OpenStates as the bill→sponsor leg (free bulk-CSV, all 50 states)
- Anna Karenina principle as architectural correction
- Commit-author contribution data (Dan 699 / Amina 13 / Gowrav 4 — 98% Dan)
- 4-node × 6-edge × 3-attribute (money/time/stance) coverage framework
- OH AER header-level compensation field (via subagent — structurally missing)

### Provisional Findings

- Cross-state CPI trends split: Trends 1+6+2 reframed as projection/engineering work (NOT v2.2 schema design); Trends 3/4/5 are prior-art-disagreement noise. Path 2-modified (5 more states at vintage 2015) is the bounded next step.
- OH structurally lacks principal↔lobbyist money disclosure — same shape as WI on this edge. `LobbyingFiling.total_compensation` exists but is null on all OH extractions.
- OH AER has richer lobbyist↔lawmaker transactional layer than WI (Section II.A gifts + II.B meals natively itemize lawmaker recipient + $).
- Plural Policy bulk-CSV covers all 50 states including OH; OH not yet downloaded.
- Anna Karenina: per-state pipelines are bespoke; "stairs of leverage" in RESEARCH_ARC overstates per-state amortization.

### Results

- [`docs/STATE_COVERAGE.md`](../../STATE_COVERAGE.md) — per-state edge×attribute coverage matrix (committed `92b4ff8`; OH cell corrected `546663e`). Lives at repo-root per convention.
- STATUS.md Active+Archived reconciliation (commit `546663e`): 4 stale rows Archived; 4 fresh rows Active.

### Decisions Made

- 5-day plan provisionally locked: Day 1 hygiene → Days 2-3 cross-state CPI N=10 extension (~$15) → Day 4 OH chain composer + FOCAL Plans 3+4 → Day 5 RESEARCH_ARC update + resumption brief.
- B reframed: NOT v2.2 schema design pass; resumption brief + projection-translation convention codification.
- No state-agnostic refactor; per-state modules under `src/lobby_analysis/<state>/`.
- Honest register in resumption brief; diplomatic framing preserved for Thursday presentation + repo-root institutional courtesy.

### Next Steps

- Dan reviews this session's commits (`92b4ff8`, `546663e`).
- Next session: (a) finish Day 1 worktree pruning audit, or (b) jump to Day 2 cross-state CPI 5-state extension dispatch (~$15 — needs cost authorization).
- Day 5 to propagate Anna Karenina + SMR-as-canonical to `docs/RESEARCH_ARC.md`.
