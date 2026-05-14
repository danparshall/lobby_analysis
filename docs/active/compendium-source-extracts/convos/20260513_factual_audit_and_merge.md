# Factual-accuracy audit (Phase 1 of merge handoff) — convo

**Date:** 2026-05-13 (factual-audit pre-merge session — same UTC day as the paper-summaries audit predecessor)
**Branch:** `compendium-source-extracts`
**Originating handoff:** [`../plans/_handoffs/20260514_factual_audit_and_merge.md`](../plans/_handoffs/20260514_factual_audit_and_merge.md) — drafted 2026-05-13 in anticipation of next-day execution (filename uses 14 per the prior session's naming pattern); executed 2026-05-13 (same UTC day; convo dated for execution date per the handoff's own naming guidance "or whatever date the next agent's session falls on")
**Predecessor convo:** [`20260513_paper_summaries_audit_premerge.md`](20260513_paper_summaries_audit_premerge.md) — the paper-summaries audit that deferred Stop condition #4 (factual spot-checks) to this session per user redirect post-commit `31ba9ce`
**Skill executed:** [`/Users/dan/.claude/skills/auditing-paper-summaries/SKILL.md`](/Users/dan/.claude/skills/auditing-paper-summaries/SKILL.md) (Step 3 "Verify Each Entry Against Source Paper" + Step 4 "Fix Errors" only — Steps 0–2 done by predecessor session)
**RESEARCH_LOG entry:** [`../RESEARCH_LOG.md`](../RESEARCH_LOG.md) §`2026-05-13 (factual-audit pre-merge)`
**STATUS row update:** `STATUS.md` `compendium-source-extracts` row — promoted from "one factual-audit session away from merge-ready" to **MERGE-READY** (audit landed; this session's commit is Phase 1 of the merge handoff)

## Purpose

Execute Phase 1 of the merge handoff: factually verify the three load-bearing source-rubric summaries (Newmark 2017, Lacy-Nichols 2024 / FOCAL, PRI 2010) against their `papers/text/` extractions before merge, since these summaries feed projection logic on a Phase C successor branch. A factually wrong summary would propagate into projection code where it's much more expensive to catch and fix than at the docs gate.

The user's reasoning for moving the audit BEFORE merge (post-commit `31ba9ce`): the cost asymmetry is large — 45–60 minutes of audit work here vs. potentially weeks of building Phase C projection logic on a wrong foundation. The original "defer to Phase C" plan from the paper-audit session was technically defensible but operationally lower-priority than the audit itself.

## What got done

Direct (non-subagent) reads of all three source `.txt` extractions and the corresponding `PAPER_SUMMARIES.md` entries. Then a checklist walk per the handoff's Stop conditions. Then surface findings to user, decide on corrections, apply, document.

### Newmark 2017 — verdict: 100% accurate

Read `papers/text/Newmark_2017__lobbying_regulation_revisited.txt` (1,173 lines) end-to-end. Walked every numerical claim in the summary against the source.

**All 11 verifiable claims confirmed exactly:**

| Claim | Source location | Verdict |
|---|---|---|
| 19-item index, 0–19 range | p.555-558 | ✓ |
| 7 def + 5 prohib + 7 disclosure structure | enumerated p.515-555 | ✓ |
| Range 7–19, mean 12.96, SD 2.63 | p.565-567 | ✓ exactly |
| Cronbach's α = 0.67, "less than ideal" | p.567 | ✓ exactly (the `0.71` for 2005 comparator is NOT in this PDF — see audit nit below) |
| Top 7 (KY 19, CO 18, CA 17, AZ/ME/MA/WI 16) | Table 2 lines 602-643 | ✓ exactly |
| Bottom 5 (WY 7, ND 7, NV 8, SD 9, FL 9) | Table 2 lines 919-941 | ✓ exactly |
| New ↔ 2003 BOS r=0.54 | p.572 | ✓ |
| New ↔ Sunlight r=0.40 | p.945 | ✓ |
| New ↔ CPI r=0.52 | p.953 | ✓ |
| New ↔ PRI accessibility r=0.27 | p.954-955 | ✓ exactly |
| New ↔ PRI disclosure "essentially zero" | p.956 | ✓ |
| **CPI ↔ PRI disclosure r=0.04** | **p.421-422** | **✓ exactly — load-bearing finding for unification rationale CONFIRMED** |
| Factor analysis: 4–6 factors, not 3 clean dimensions | p.849-851 | ✓ |
| Arizona 6 → 16 mover; recipient-id gaps caveat | Table 2 + p.962-968 | ✓ exactly |
| VA / IL / NC also moved up | p.969-970 | ✓ |

**Sourcing nit (not an error):** the parenthetical "(lower than 2005's 0.71; author flags as 'less than ideal')" — the `0.67` and `less than ideal` ARE in this paper (p.567); the `0.71` comparator for 2005 is NOT in the 2017 PDF — likely sourced from Newmark 2005 (separate paper, also in collection). Worth a note in PAPER_INDEX Audit Notes (added this session) for Phase C agents who go to extract.

### Lacy-Nichols 2024 / FOCAL — 1 real error + 1 clarity issue

Read `papers/text/Lacy_Nichols_2024__focal_scoping_review.txt` (1,468 lines) end-to-end.

**14 of 16 verifiable claims confirmed exactly:**

| Claim | Source location | Verdict |
|---|---|---|
| 1,911 records screened | p.258 | ✓ exactly |
| 15 frameworks (1991–2022) | p.14, p.354, p.400 | ✓ |
| 248 items thematically coded | p.382-383 | ✓ exactly |
| FOCAL = 8-category, 50-indicator | p.22-23 (abstract); Table 3 enumeration | ✓ |
| 19 of 109 GDB countries | p.110-112 | ✓ exactly |
| Financials 14/15 | p.804-805; p.1062-1064 | ✓ exactly |
| Scope 13/15 | p.806; p.860-862 | ✓ exactly |
| 3 weighted frameworks | p.819 | ✓ exactly |
| Highest-weighted categories: timeliness, online availability, financials, enforcement+sanctions | p.820-822 | ✓ |
| FOCAL unweighted, flagged as limitation | p.1194-1196 | ✓ |
| Scope + contact log priority | p.1148-1154 | ✓ |
| Chile as contact-log exemplar | p.1166-1167 | ✓ |
| UK/Australia third-party-only example | p.1156-1161 | ✓ |
| 8 category names + first-two-from-legislation rule | p.22-23, p.386-391, p.831-841 | ✓ |
| Enforcement excluded but in 11/15 | p.815-818 | ✓ exactly (11) |
| Integrity/codes excluded but in 6/15 | p.815-818 | ✓ exactly (6) |

**Real error found (corrected this session):** the parenthetical
> "(The paper does not state a count for contact log; earlier versions of this summary that cited '13/15 contact log' were duplicating the scope figure.)"

is wrong. Paper p.1077-1079 (Contact log subsection of FOCAL Categories) explicitly states: "13 Frameworks included this aspect of disclosure, with only the Hired Guns and Bednářová frameworks omitting it." So the prior "13/15 contact log" was correct — and ironically this revision "fixed" it by removing accurate info AND introducing a false metaclaim about what the paper says. Pattern is a process gap: the prior reviewer didn't read the per-category subsections in §"Framework fOr Comprehensive and Accessible Lobbying" where each category's framework count is independently stated. Worth flagging as a future-audit watchpoint — when "fixing" a count by removing it with a justification, double-check the justification is true.

**Clarity issue (corrected this session):** "openness/data accessibility in 9/15" — paper has TWO numbers:
- p.809: "Nine frameworks included elements of open data (ie, data accessibility)" — narrower open-data sub-theme
- p.886-887: "Eleven frameworks included this element [openness]" — for the FOCAL Openness category itself

Summary picked 9 (correct citation, but conflates the two). Per user direction tightened to "openness in 11/15 (open-data sub-theme specifically in 9/15)."

### PRI 2010 — verdict: 100% accurate on every checked claim

Read `papers/text/PRI_2010__state_lobbying_disclosure.txt` (2,095 lines) in two chunks (lines 1-700 = exec summary; 700-1400 = methodology + state-by-state disclosure law analysis; 1400-2095 = accessibility + comparison + endnotes/appendix).

The handoff flagged this paper as the highest-density numerical-claim summary and the most likely to have transcription errors. **All checked claims verified exactly:**

**Disclosure-law rubric structure:**
- 37-pt max; 5 sub-components A:11 + B:4 + C:1 + D:1 + E:20 = 37 ✓ (executive summary p.158-160 + methodology p.1393-1394; sub-component max counts visible in Table 5 column headers lines 1320-1334)
- B1/B2 reverse-scored per footnotes 85/86 ✓ exactly (paper lines 1977-1978: "Note that the positive answer to this question is 'no' whereas it is 'yes' to all other questions")
- C: 0/1 gate with 3 sub-criteria (Ownership / Structure-or-revenue-composition / Public charter or special protection) ✓ (p.1193-1197)
- D: 0/1 gate with 2 sub-criteria (Financial threshold / Time threshold) ✓ (p.1217-1223)
- E: "higher of E1/E2 + F/G double-count + separate J" ✓ (p.1226-1242 + footnote 87 lines 1981-1983 confirm exactly the rule "we took the higher score of the principal or lobbyist section when both were required to disclose information"; footnote 88 confirms the F/G double-count exception; J question independently confirmed)

**Disclosure-law results:**
- Top: MT 31/37 83.8%, AZ 30/37 81.1%, SC and TX tied 29/37 78.4% ✓ (executive summary p.163-166 + Table 5)
- Bottom: WV and NV tied 11/37 29.7%, NH 12/37 32.4%, MD 13/37 35.1% ✓ (p.170-172 + Table 5)
- Average 21.9/37 (59.3%); 11 states scored below 50% ✓ (paper p.167-169 — note: I count 12 states below 50% from Table 5; the paper itself says 11; summary faithfully repeats the paper's count, so this is paper-side counting curiosity not a summary error)
- Sub-component callouts: 17 vols, 24 principals, 17 lob firms, 6 govt agencies registered (p.181-188); 44 states with govt exemptions (p.197-198); 6 states define public entity (p.208); 32 states have materiality test (p.212); E top 18/20 (AK, MT, NY, TX) and bottom 5/20 (WY, OK) ✓ exactly (executive summary + state-by-state table)

**Accessibility rubric:**
- 22-pt max; 8 questions Q1-Q6 binary + Q7 0-15 sort-criteria + Q8 0-15 simul-sort divided by 15 → 0-1 ✓ (p.1517-1520 confirms the methodology exactly)
- Top: CT 17.3/22 78.5%, NC 14.3, WA 14.3 ✓ (Table 6); Bottom: VT and WY tied 5/22 22.7%, NH 6/22 27.3% ✓
- Average 9.6/22 43.6%; 32 states (64%) below 50% ✓ exactly (p.239)
- 8 category names ✓; 13 states lack historical (37/50 have it) ✓; 17/50 machine-readable ✓; avg 4.4/15 sort vars ✓; avg 1.7/15 simul-sort ✓ (p.245-249)

**Cross-rubric ranks:**
- South Carolina Rank 3 on disclosure (78.4%, tied with TX) ✓ Table 5 line 1378
- South Carolina Rank 46 on accessibility (6.0/22, 27.3%) ✓ **Table 6 line 1616**
- Connecticut Rank 18 on disclosure (64.9%) ✓ Table 5 line 1345
- Connecticut Rank 1 on accessibility (17.3/22, 78.5%) ✓ Table 6 line 1581

**Combined overall:**
- Top 6: CT 71.7%, IN 68.0%, TX 67.1%, WA 66.2%, ME 65.3%, MT 65.2% ✓ exactly (p.256-259, Table 7 line 1690 etc.)
- Bottom 5: NH 29.9%, WY 30.3%, WV 30.8%, NV 35.3%, MD 38.5% ✓ exactly (p.260-262)

**California case study:**
- Total $552.6M (2007+2008) ✓; Government category $92.6M (16.8%) officially ✓ (Table 1 line 768-802); After reclassification of Education + Public Employees + Labor Unions taxpayer-funded portions: $131.4M (23.8%) ✓ (Table 4 line 1027)

## Decisions

| Topic | Decision |
|---|---|
| Newmark 2017 audit verdict | **All numerical claims confirmed exactly.** No corrections needed. The load-bearing r=0.04 CPI ↔ PRI-disclosure correlation is solid. |
| Newmark 2017 0.71 sourcing nit | **Note in PAPER_INDEX.md Audit Notes only.** The 0.71 comparator is sourced from Newmark 2005 (separate paper), not from the 2017 PDF; flag for Phase C agents. Don't edit summary. |
| FOCAL contact-log error | **Restore "contact log in 13/15" + delete the false parenthetical.** Cleanest fix; restores accurate info that a prior revision had removed. |
| FOCAL openness 9 vs 11 | **Tighten to "openness in 11/15 (open-data sub-theme specifically in 9/15)."** Both numbers in the paper; informative, matches source. |
| PRI 2010 audit verdict | **All checked claims confirmed exactly.** No corrections needed. The paper-side curiosity at "11 states below 50%" (vs my count of 12 from Table 5) is a paper-side issue, not a summary issue; summary is faithful. |
| Convo filename | `20260513_factual_audit_and_merge.md` (today's UTC date; handoff explicitly allows execution-date naming). |
| Branch merge-readiness | **Branch is now MERGE-READY.** All Phase 1 Stop conditions in the handoff satisfied. Next: commit + push (Phase 2), then merge → main (Phase 3), then archive (Phase 4), then cut 3 successor branches (Phase 5). |

## Mistakes recorded

None significant. Cross-checked claims using two-stage reads (executive-summary numbers first, then methodology + tables for the inside-baseball claims), which caught the FOCAL contact-log error cleanly. Subagent dispatch wasn't needed since the .txt files were short enough for direct reads (1,173 + 1,468 + 2,095 = 4,736 lines total).

One minor harness-quirk: the `Read` tool's token-counting heuristic over-rejected STATUS.md at 38k tokens for a 100-line slice (it shouldn't have — the file is dense markdown but not THAT dense). Worked around with `grep -n` for the relevant section; no impact on the audit itself.

## Results

- [`PAPER_SUMMARIES.md`](../../../../PAPER_SUMMARIES.md) — line 230 corrected (FOCAL summary: contact-log count restored, openness clarified to 11/15 with 9/15 sub-theme parenthetical).
- [`PAPER_INDEX.md`](../../../../PAPER_INDEX.md) — Audit Notes section "Pending factual-accuracy audits" line replaced with "Factual-accuracy audits landed (2026-05-13)" — full per-summary verdict block including the Newmark 2017 0.71 sourcing nit.
- [`docs/active/compendium-source-extracts/plans/_handoffs/20260514_factual_audit_and_merge.md`](../plans/_handoffs/20260514_factual_audit_and_merge.md) — Phase 1 Stop conditions checked off (factual audits complete on all 3 papers; user-decided dispositions applied; PAPER_INDEX Audit Notes updated; convo + RESEARCH_LOG + STATUS updated; commit pending in this session).
- This convo summary + RESEARCH_LOG entry + STATUS row update + Recent Sessions top entry.

## Next steps (handoff Phase 2 onward, this session)

1. **Audit commit + push** (Phase 2 of handoff). Single commit covering: PAPER_SUMMARIES.md (FOCAL summary correction), PAPER_INDEX.md (Audit Notes block update), STATUS.md (row update + Recent Sessions top entry), RESEARCH_LOG.md (this session entry), this convo, the handoff doc with Phase 1 Stop conditions checked off.
2. **Merge `compendium-source-extracts` → main** (Phase 3 of handoff). Standard merge (no squash; branch commit history is the permanent record). `git fetch` first to verify no other fellow pushed since this session started.
3. **Archive `docs/active/compendium-source-extracts/` → `docs/historical/compendium-source-extracts/`** (Phase 4) via `git mv`. Update STATUS.md Active table (remove row) + Archived table (add row summarizing what was learned).
4. **Cut 3 successor branches in parallel** (Phase 5 of handoff): `oh-statute-retrieval`, `extraction-harness-brainstorm`, `phase-c-projection-tdd`. Seed each with `docs/active/<branch>/` skeleton (RESEARCH_LOG.md stub + convos/ + plans/ + results/ dirs). NO kickoff plans — those are each successor branch's first session's work.

**Honesty note for the next reader:** the audit was much cleaner than the handoff anticipated. The handoff's tone treated factual errors as a real possibility worth scoping. They were rare — 1 real correction in FOCAL, 1 clarity tightening in FOCAL, 1 sourcing note in Newmark 2017, 0 in PRI 2010. The framing rationale for the rubric-unification project (anchored on Newmark 2017's r=0.04) rests on accurately-reported data. Phase C TDD agents can trust the projection-arithmetic values in these three summaries.
