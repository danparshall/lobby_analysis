# B3PW pilot canaries — WY 2010 + FL 2010

**Date:** 2026-05-14
**Plan:** [`plans/20260514_b3_two_pass_discovery_plan_playwright.md`](../plans/20260514_b3_two_pass_discovery_plan_playwright.md)
**Branch:** `api-multi-vintage-retrieval` (worktree: `.worktrees/api-vintage`)
**Cost spent (cumulative across both canaries):** **~$0.07** of $1.00 cap
**Scope:** Phase 4 steps 24–25 of the B3PW plan (WY + FL canaries against real Anthropic + real Justia).

## TL;DR

- **WY 2010: 1/1 ground-truth hit.** Clean B3PW execution end-to-end. Pass-1 picked `Title28/Title28.html` ("Title 28 - Legislature"); pass-2 landed exactly on `Title28/chapter7.html`. Wall time 21.5s. Cost $0.023.
- **FL 2010: 0/6 ground-truth section-leaves, but pass-1 + pass-2 both behaved correctly.** Pass-1 correctly identified BOTH parallel statute bodies (TitleIII/Ch.11 legislative + TitleX/Ch.112 executive). Pass-2 landed on the right chapter-TOC pages (`chapter11.html`, `chapter112.html`). Wall time 38s. Cost $0.043.
- **The FL miss is the chapter-TOC ceiling the original B3 plan named.** `chapter11.html` is a section TOC (~5KB stripped text), not a statute leaf — section bodies live one hop deeper at `chapter11/11_045.html` etc.
- **Two prompt + helper defects surfaced and fixed during this canary**, both documented below.
- **Gate to 10-pair canary**: NOT met (FL fails the ≥80% ground-truth gate). User input needed on B3 vs B4 vs heuristic chapter→sections expansion before further canary spend.

---

## WY 2010 — 1/1 hit

**Ground truth:** `https://law.justia.com/codes/wyoming/2010/Title28/chapter7.html` (single chapter-leaf, the full WY lobbyists statute body)

**Pass-1 chosen title:** `https://law.justia.com/codes/wyoming/2010/Title28/Title28.html`
- Anchor text in TSV: `Title 28 - Legislature` (the `<li>` text already includes the subject — see "Defect 2" below)
- Rationale: "Wyoming's lobbyist registration and disclosure statutes are codified under Title 28 (Legislature), which governs legislative branch activities including lobbying requirements."

**Pass-2 proposed URLs (1):**
- `https://law.justia.com/codes/wyoming/2010/Title28/chapter7.html` `[core_chapter]` ✅ GT-HIT
- Rationale: "Title 28 Ch. 7 Lobbyists: the full chapter-leaf covering lobbyist registration and disclosure requirements for Wyoming."

**Wall time:** 21.5 s. Two Playwright fetches × ~5s rate-limit + Anthropic API latency. No anti-bot incidents.

**Cost:** 1189 input + 82 output tokens = $0.0048 for pass-1, ~$0.018 for pass-2 = **$0.023 total**.

**Verdict:** B3PW works end-to-end on a single-chapter-leaf state. Pass-2's Rule 6 ("only URLs from the snapshot") did not over-constrain — the model correctly inferred `chapter7.html` from the title page's link list.

---

## FL 2010 — 0/6 section-leaves; chapter-TOC ceiling

**Ground truth (6 URLs):**
- `https://law.justia.com/codes/florida/2010/TitleIII/chapter11/11_045.html` (core: lobbying before the Legislature)
- `https://law.justia.com/codes/florida/2010/TitleIII/chapter11/11_0451.html` (support: reinstitution after felony)
- `https://law.justia.com/codes/florida/2010/TitleIII/chapter11/11_0455.html` (support: electronic filing)
- `https://law.justia.com/codes/florida/2010/TitleIII/chapter11/11_047.html` (support: contingency fees)
- `https://law.justia.com/codes/florida/2010/TitleIII/chapter11/11_061.html` (support: state-employee lobbyists)
- `https://law.justia.com/codes/florida/2010/TitleIII/chapter11/11_062.html` (support: state funds for lobbying)

All six are section-level leaves under `chapter11/`.

**Pass-1 chosen titles (2):**
- `TitleIII/TitleIII.html` — "Title III covers the Legislative Branch and its commissions (Ch.10-11), which includes Florida's legislative lobbyist registration and disclosure requirements under Chapter 11."
- `TitleX/TitleX.html` — "Title X covers Public Officers, Employees, and Records (Ch.110-122), which includes the Commission on Ethics provisions and executive-branch lobbyist registration and expenditure reporting requirements under Chapter 112."

Pass-1 availability notes: "Florida splits its lobbying-disclosure regime across two titles: Title III (Legislative Branch, Ch.11) governs legislative lobbyist registration and disclosure, while Title X (Public Officers, Ch.112) governs executive-branch lobbying and the Commission on Ethics rules including gift and expenditure disclosure. Both titles are needed for full coverage of FL's lobbying-disclosure statutes."

**Pass-1 verdict:** ✅ correct. Both regimes identified; both names match Florida's statute structure.

**Pass-2 proposed URLs (2):**
- `TitleIII/chapter11/chapter11.html` `[core_chapter]` — chapter-TOC, not a section leaf
- `TitleX/chapter112/chapter112.html` `[core_chapter]` — chapter-TOC for the other regime

**Pass-2 verdict:** the model picked the right CHAPTERS but stopped at the chapter-TOC level instead of going down to section leaves. Per [`/tmp/probe_fl_chapter11.py`](#diagnostic-chapter-toc-probe) verification:
- `chapter11.html` is **66 KB raw, ~5 KB stripped text**
- Stripped text contains the **section titles** (`11.045 Lobbying before the Legislature; registration and reporting; exemptions; penalties.` etc.) but no section bodies
- Ground-truth section bodies live at `chapter11/11_045.html` (separate Justia leaves)

This is the **chapter-TOC ceiling** the original B3 plan explicitly anticipated (step 26). The title page exposes chapter-level URLs only, so pass-2's "only propose URLs from the snapshot" rule caps the orchestrator at chapter depth.

**Wall time:** 38.0 s (3 Playwright fetches at ~5s rate-limit + 3 Anthropic calls).
**Cost:** ~$0.043 total (pass-1 plus two pass-2 calls).
**Anti-bot incidents:** 0.

---

## Defects surfaced + fixed during canary

### Defect 1 — `_build_justia_link_tsv` rejected Justia's 2-segment title-link pattern

**Symptom:** First WY canary run produced an empty TSV ("Fetched state index" section in the prompt). Pass-1 returned `chosen_titles: []` with the note "snapshot is empty."

**Root cause:** WY's state-year index links use the form `/codes/wyoming/2010/Title28/Title28.html` — two segments deeper than the namespace `/codes/wyoming/2010/`. My helper's "one-segment-deeper only" rule rejected all 43 of them.

**Fix:** added a narrow `Foo/Foo.html` exception (`tests/test_api_retrieval_agent_b3.py::test_build_justia_link_tsv_directory_parent_with_foo_foo_html_children`). Any directory-parent child that is exactly two segments deep AND has the form `X/X.html` (same stem before/after the slash) is now accepted. Chapter URLs like `Title28/chapter7.html` (different segments) remain rejected at the state-year-index level to prevent chapter URLs masquerading as titles.

Re-running WY after the fix produced the 1/1 hit reported above.

### Defect 2 — Terse anchor text starved pass-1 of subject-name context

**Symptom:** Second canary run on FL (after Defect 1 fix) returned pass-1 choice = `TitleIX/TitleIX.html` with the model's own rationale: "Given uncertainty about which Roman-numeral title maps to which chapter without anchor text, Title IX is the best single candidate."

**Root cause:** Justia's FL state-year-index uses table rows:
```
<tr><td><a href=".../TitleIII/TitleIII.html">TITLE III</a></td>
    <td>LEGISLATIVE BRANCH; COMMISSIONS</td></tr>
```
My helper used `anchor.get_text(strip=True)` — got "TITLE III" only. Subject name "LEGISLATIVE BRANCH; COMMISSIONS" sat in a sibling `<td>` and never made it to the prompt.

**Fix:** new `_link_description` helper that walks up to the nearest `<tr>`, `<li>`, or `<dt>` ancestor and uses its full text content. For `<dt>`, also pulls in the next-sibling `<dd>`. Test: `test_build_justia_link_tsv_uses_parent_row_text_when_anchor_is_terse`.

Re-running FL after this fix produced pass-1 picks `[TitleIII, TitleX]` with informed rationales naming the chapter numbers — i.e., the model gained the disambiguation context it needed.

### Defect 3 — Pass-1 prompt's conservatism bias overrode multi-pick when warranted

**Symptom:** Third FL canary run (after Defects 1 + 2 fixed): pass-1 narrative correctly named both Title III and Title X as lobbying-relevant titles, then picked only Title X with the rationale "Title X is the stronger pick."

**Root cause:** pass-1 prompt said "**Prefer to pick a single title** unless you have specific evidence that the state's lobbying statute is split across multiple titles." The model treated this as a strong directive even when its own narrative met the "specific evidence" bar.

**Fix:** rewrote the prompt's Rule 2 to make multi-pick the explicit default when parallel regimes are identified. Cost framing ("each additional title costs ~$0.02 — trivial; the cost of missing a title is structural") replaces the prior "be conservative" framing. The conservatism is retained but redirected: filter out *irrelevant* titles, don't conservatively cap pick count.

Re-running FL produced the `[TitleIII, TitleX]` multi-pick reported above. This answers Question #1 from both the original B3 plan and the playwright revision ("Should pass-1 prompt cap multi-title picks at 2?"): no cap, prompt explicit multi-pick when parallel regimes are named.

---

## What this leaves open — B3 vs B4 vs heuristic

Per the original B3 plan's step 26 framing, FL's 0/6 result is the "chapter-TOC ceiling" outcome that the user should weigh in on. Three viable paths:

### Option A — Accept chapter-TOC URLs as "good enough" for the data layer

The chapter-TOC page itself is structurally regular: every section URL is a direct child of the chapter URL. If the downstream extraction pipeline can enumerate children deterministically (via `justia_client.parse_children_list` or the same TSV-builder), B3PW's chapter-TOC output is enough — no LLM call needed to expand to sections.

- **Cost:** no additional API.
- **Wall time:** +1 Playwright fetch per chapter (for children enumeration), but only at extraction time, not at discovery time.
- **Risk:** chapters that mix lobbying sections with non-lobbying sections (likely the FL case — Ch. 11 covers "Legislative Organization, Procedures, AND Staffing", not just lobbying) would get every section pulled in, requiring downstream filtering.

### Option B — Escalate to B4 (three-pass: state → title → chapter → leaves)

Add a third LLM call per chapter that proposes the in-scope section URLs from the chapter-TOC TSV.

- **Cost:** +1 LLM call per chapter ≈ +$0.025/pair → ~$0.07/pair total. Full 350-pair fan-out: ~$25 instead of ~$17.
- **Wall time:** +1 Playwright fetch + LLM call per chapter. WY (single chapter) goes from 21.5s → ~35s; FL (two chapters) goes from 38s → ~70s. Full 350-pair fan-out: 45–60 min instead of 30–40 min.
- **Reliability:** the model has shown it can read section TOCs and pick the in-scope ones (the pass-2 narrative already correctly identifies which sections are lobbying). Three-pass should hit the section-leaf level cleanly.

### Option C — Hybrid: chapter-TOC by default + per-section LLM pick only when needed

Use B3PW's chapter-TOC output as the "anchor". When the chapter-TOC page itself contains the full statute text (the WY single-chapter-leaf case), we're done. When it's a section TOC (the FL case), follow up with B4-style section picking, or heuristic enumeration if the chapter is purely lobbying.

This requires either:
- LLM judgment on whether `parse_statute_text(chapter_page)` returned "enough" text to count as the full body, or
- A heuristic threshold (e.g., chapter pages with <10 KB stripped text are TOCs; ≥10 KB are full-text)

---

## Recommendation (this implementer's read)

I lean toward **Option B (B4 three-pass)** for the following reasons:

1. **The cost delta is rounding error** at this project's scale (~$25 vs ~$17 for the 50-state × 7-vintage fan-out — both trivial).
2. **The model has the right judgment when given the chapter TOC.** Pass-2's narrative on FL chapter11.html, if it had been given a section-leaf TSV, would clearly have picked the lobbying sections — the model already named "11.045", "11.0451", "11.0455", "11.047", "11.061", "11.062" in its rationale even when it could only emit chapter11.html.
3. **Option A (heuristic enumeration) sweeps in non-lobbying sections** for chapters that mix scopes (FL Ch. 11 has 50+ sections, only 6 of which are lobbying). Filtering those downstream is harder than letting pass-3 do the picking.
4. **Option C (hybrid) is engineering complexity for marginal benefit** — adding a "is this a full-text chapter or a section TOC" classifier introduces a new failure mode (misclassification) without strong evidence it's needed.

But this is the user's call. The 10-pair canary should not run before this decision is made — running it on B3PW as-is would produce a misleading chapter-TOC-ceiling-shaped failure for any state whose chapter pages are section TOCs (likely a majority).

---

## What didn't break / still confidence-inspiring

- **PlaywrightClient handled real Justia at sustained pressure across 5 distinct URLs in <60 s wall time, with zero Cloudflare incidents.** Anti-bot side of the architecture is solid.
- **Pass-1 + pass-2 prompt + parser plumbing all worked correctly on first invocation.** No JSON-parse errors; markdown-fence tolerance was exercised; Justia-hostname schema enforcement filtered nothing because both passes emitted clean URLs.
- **Cost cap mechanism never triggered.** Conservative $3/$15-per-M pricing → reported $0.07 vs actual ~$0.04 (Sonnet 4.6 is cheaper than my upper-bound). The cap design works as a safety net without false alarms.
- **38/38 unit tests still GREEN.** Three new helper-focused tests landed alongside the canary-driven fixes — the test suite is now stronger than it was at the start of this session.

---

## Appendix — exact canary commands

```bash
# WY
CANARY_MODE=B3PW CANARY_TARGET=WY PYTHONPATH=src \
  uv run --active python scripts/canary_discovery.py

# FL
CANARY_MODE=B3PW CANARY_TARGET=FL PYTHONPATH=src \
  uv run --active python scripts/canary_discovery.py
```

The canary script is gitignored (`scripts/canary_discovery.py`) but its current shape is recoverable from this commit (commit message references its mode dispatch).

## Diagnostic: chapter-TOC probe

For reproducibility, the FL chapter-TOC verification used a one-shot script (`/tmp/probe_fl_chapter11.py`) that fetched `chapter11.html` via `PlaywrightClient` and ran it through `justia_client.parse_statute_text`. Output: 66,856 bytes HTML → 4,967 chars stripped text. Stripped text contains section titles ("11.045 Lobbying before the Legislature; registration and reporting; exemptions; penalties.") but no section bodies. Confirms `chapter11.html` is a section TOC, not a statute leaf.
