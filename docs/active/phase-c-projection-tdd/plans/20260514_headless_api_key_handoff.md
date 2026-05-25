# Headless / API-key handoff for Sub-1 onward

**Date written:** 2026-05-14 on `Dans-MacBook-Air`
**Originating convo:** [`../convos/20260514_rubric_plans_drafting.md`](../convos/20260514_rubric_plans_drafting.md) (Sub-0 of 5)
**Audience:** an agent (or human) on a different machine, picking up `phase-c-projection-tdd` at Sub-1+ where the user wants to bill an `ANTHROPIC_API_KEY` instead of their Claude Code subscription.

> **You are reading this because the user is starting a new Claude Code session for the next sub-session of the rubric-planning workflow.** This doc tells you how to confirm API-key billing, where you are in the multi-sub-session structure, what to read for context, and what to do.

---

## TL;DR for the agent

1. Run `hostname` to identify which machine you're on.
2. Confirm `ANTHROPIC_API_KEY` is set and Claude Code is using it (see "Verifying API-key auth" below). If not, surface to user before doing any work.
3. Do the standard Nori pre-flight reads, **including** the three Sub-0 artifacts listed under "Pre-flight reads" below.
4. Execute the sub-session task per "Which sub-session am I?" below.
5. Run finish-convo at end of session. Each sub-session checkpoints to its own convo file; commits; pushes.

---

## Background — what the multi-sub-session structure is

User motivation: bill API key (work-project budget) instead of Claude Code subscription for the 6 remaining Phase C rubric implementations. Sub-0 (playbook gap audit + data-year audit) ran on subscription and is complete (commit `0af667e` on `origin/phase-c-projection-tdd`). Sub-1 onward run on API key, each in its own fresh-context Claude Code session.

| Sub-session | Task | Status |
|---|---|---|
| **0** | Playbook gap audit + data-year audit | ✅ Complete, commit `0af667e` |
| **1** | Draft Stream 1 plans (Sunlight 2015 + Opheim 1991) | Pending (most likely you) |
| **2** | Draft Stream 2 plans (Newmark 2017 + Newmark 2005) | Pending |
| **3** | Draft FOCAL plan-set (3-4 sub-plans) + HG 2007 plan with retrieval gate | Pending |
| **4** | Build per-rubric prompt template + headless `claude -p` launch script + Sunlight canary | Pending |
| **HG gate** | Retrieve CPI 2007 per-state scorecard before HG plan launches (separate task) | Pending |

You are most likely Sub-1 (Stream 1 plans). The user will confirm in their opening message.

---

## API-key setup

### Where the key lives on the user's machines

**On `Dans-MacBook-Pro` (desktop):** the key is in `.env.local` at the repo root (`/Users/dan/code/lobby_analysis/.env.local`), covered by the `.env*` rule in `.gitignore`. The worktree's `.env.local` is a symlink to the main worktree's file per the `use-worktree` skill, so the same file is reachable from any worktree.

The line is single-quoted without an `export` prefix:

```
ANTHROPIC_API_KEY='sk-ant-...'
```

This shape matters: plain `source .env.local` will set the var in the launching shell but **not** export it to child processes like `claude`. Use one of:

```bash
# auto-export everything sourced (recommended one-shot)
set -a; source /Users/dan/code/lobby_analysis/.env.local; set +a
claude
```

or add `export ` to the line in `.env.local` so plain `source` propagates.

**Verify before launching `claude`:**

```bash
[ -n "$ANTHROPIC_API_KEY" ] && echo "set (${#ANTHROPIC_API_KEY} chars)" || echo "NOT set"
```

**Do not** read the key value, write it to any other file, or include it in commits. `.env.local` itself is gitignored; the *path* is safe to document but the key value is not. The repo is shared with other Corda fellows.

### Verifying API-key auth

In the Claude Code session:

```
/status
```

Inspect the output. If it shows you're billing the API key / a work org, proceed. If it shows the user's personal subscription account, **surface to the user before any rubric work** — they wanted API-key billing. Re-launch the session with `ANTHROPIC_API_KEY` exported.

If `/status` doesn't show auth mode visibly, run `/login` — it'll show which auth methods are active and let you select API key.

**Honest uncertainty:** the writer of this doc (a Sonnet running on the laptop) was ~90% confident about `/status` showing auth mode. If the UX has shifted, fall back to `/login`.

---

## Worktree setup

**If the worktree already exists on this machine:**

```bash
cd /Users/dan/code/lobby_analysis/.worktrees/phase-c-projection-tdd
git fetch origin
git pull --ff-only origin phase-c-projection-tdd
```

Verify with `git -C . log --oneline -5` that you have commit `0af667e` (the Sub-0 close-out) at or near HEAD.

**If the worktree does NOT exist:**

```bash
cd /Users/dan/code/lobby_analysis  # or wherever the repo is on this machine
git fetch origin
git worktree add .worktrees/phase-c-projection-tdd phase-c-projection-tdd
cd .worktrees/phase-c-projection-tdd
```

Per the user's `use-worktree` skill, also create a `data/` symlink to the main repo's `data/` directory if any work depends on gitignored data. Plan-drafting work (Sub-1, Sub-2, Sub-3) does **not** depend on gitignored data — only Sub-4 (Sunlight canary) and Phase C implementation runs do — so the symlink is optional for plan-drafting sub-sessions.

---

## Pre-flight reads (every sub-session)

Per the Nori workflow in your global CLAUDE.md. Three additions specific to this multi-sub-session structure are in **bold**.

1. `STATUS.md` — current focus, branch inventory, Recent Sessions.
2. `README.md` — what this repo does.
3. `docs/active/phase-c-projection-tdd/RESEARCH_LOG.md` — trajectory for this branch. The top entry is Sub-0.
4. **`docs/active/phase-c-projection-tdd/convos/20260514_rubric_plans_drafting.md`** — Sub-0's convo. Read end-to-end. Contains the structural decisions (Structure B, FOCAL split, HG gating, strict-reading scope) and the 7 convention proposals.
5. **`docs/active/phase-c-projection-tdd/results/20260514_playbook_gap_audit.md`** — 5 cross-cutting meta-patterns the playbook missed + per-rubric gaps + implementation implications. Lead with the section for *your* rubric(s).
6. **`docs/active/phase-c-projection-tdd/results/20260514_rubric_data_years.md`** — publication-year vs data-year for each rubric, with confidence levels. Each plan must include a "Data year" section per Sub-0's conventions.
7. `docs/active/phase-c-projection-tdd/plans/20260514_rubric_implementation_playbook.md` — the playbook itself. Use for shared conventions that ARE faithful (architecture decision rubric, validation regime regimes, common patterns cheat-sheet). Override with gap audit findings where the playbook is gappy.
8. Your rubric's spec doc(s) under `docs/historical/compendium-source-extracts/results/projections/` — e.g., `sunlight_2015_projection_mapping.md` for Sub-1. Read end-to-end before drafting the plan.

---

## Which sub-session am I?

The user's opening message should name a sub-session. If they didn't, **ask** — don't assume. The likely sequence is Sub-1 first (Stream 1) since Sub-0 just landed.

### Sub-1: Stream 1 plans (Sunlight 2015 + Opheim 1991)

**Goal:** Two plan docs in `docs/active/phase-c-projection-tdd/plans/`, one per rubric.

**Order:** Sunlight 2015 first; Opheim 1991 second in the same session. Opheim inherits the β AND-projection convention from Sunlight, so Sunlight's plan must concretely specify the bill_id + position cells before Opheim's plan can reference them.

**Key Sunlight gotchas (from Sub-0 gap audit):**
- Item 4 is EXCLUDED per audit decision 2026-05-07. Projection covers 4 items, not 5.
- Cannot reproduce published Total or letter Grade.
- All 4 in-scope items have bespoke compound logic → function-per-item pattern.
- Tier scales are signed (`−1 to 2`, `−2 to 2`), not 0/1.
- Footnote markers on CSV cells need stripping.
- Data year: ~2014-2015 statutes (MEDIUM-LOW confidence; firm up by reading paper methodology section).

**Key Opheim gotchas:**
- 7 enforce.* items + 1 catch-all OUT of scope per disclosure-only Phase B.
- 47 states, NOT 50 (MT/SD/VA missing).
- Weak-inequality validation regime only (paper publishes per-state totals; no sub-aggregates).
- 1 un-projectable catch-all (`other_influence_peddling_or_conflict_of_interest`) → `unable_to_evaluate`, not zeroed.
- `disclosure.frequency` reads PRI cadence at finer cut than Newmark 2005 (2 cells OR vs 8 cells OR).
- β AND-projection on `bill_id AND position` — both pre-existing from Sunlight α split.
- Data year: 1988-89 (HIGH confidence; paper-explicit).

### Sub-2: Stream 2 plans (Newmark 2017 + Newmark 2005)

Newmark 2017 first; 2005 piggybacks. Newmark 2017 introduces 6 new rows (`def_actor_class_*` × 2, `expenditure_threshold_*`, `time_threshold_*`, `lobbyist_spending_report_includes_total_expenditures`, `lobbyist_or_principal_report_includes_contributions_received_for_lobbying`) that Newmark 2005 + Opheim reuse. Newmark 2005's plan should explicitly cover the cadence projection (`freq_reporting_more_than_annual` OR over 8 cells) and the weak-inequality validation regime. **Not a near-clone of 2017** — different aggregation (4 sections vs 3), different validation (weak-inequality vs sub-aggregate), 6 panels vs 1.

### Sub-3: FOCAL plan-set (3-4 sub-plans) + HG 2007 plan with retrieval gate

FOCAL split per Sub-0 decision: (a) legal-side core (scope/descriptors/relationships/financials), (b) contact_log battery (9 new rows), (c) openness battery (practical-side), (d) aggregation + weighted scoring + US LDA validation anchor. Each sub-plan implementable independently then composed.

HG plan drafted with **both retrieval-result paths**:
- If CPI scorecard retrievable: per-state per-item validation regime (1,900 cells).
- If not: weak-inequality only (50 cells × `our_partial ≤ paper_total`).
HG plan launch (Sub-5 or whenever it happens) gated on retrieval result.

### Sub-4: Headless launch infrastructure + Sunlight canary

Per-rubric prompt template; Python `claude -p` launch script with `ANTHROPIC_API_KEY`; fire Sunlight as canary; observe whether headless TDD discipline holds; iterate before fanning out to the other plans.

---

## Conventions every plan must follow (from Sub-0)

These are baked into all 6 plans. Don't re-invent per-rubric.

1. **Scope qualifier section** — open each plan with which items are excluded + reason + max-reproducible total.
2. **`unable_to_evaluate` convention** — OOS items, un-projectable items, and Phase D portal-cells produce `unable_to_evaluate` (not zeroed). Excluded from partial; weak-inequality `our_partial ≤ paper_total` holds.
3. **Validation regime declaration** — Strong / Medium / Weak. Don't promise tolerance checks the regime can't deliver.
4. **Row-promotion delta section** in each plan's results doc — list rows shifted N → N+1 confirmation. Feeds Phase 4 audit.
5. **Spec-doc-vs-v2 cross-check** as Phase 0 — load-bearing. STOP and write a diagnostic if drift exceeds 10% of expected rows.
6. **Per-item helper return signature** — `int` in rubric-specific range OR `Literal["unable_to_evaluate"]`. Reverse-scoring in rollup, NOT in per-item helper.
7. **Data year section** — every plan names the statute vintage for its rubric, with confidence level. Reference [`../results/20260514_rubric_data_years.md`](../results/20260514_rubric_data_years.md). HG specifically has a per-item vintage split (Q35-Q37 = 2002; rest = 2006-2007).

---

## What NOT to do

- **Don't implement.** Sub-1, Sub-2, Sub-3 are plan-drafting only. Implementation (TDD per the plans) is Sub-5+ via headless `claude -p`, driven by Sub-4's launch script.
- **Don't merge to main.** Research-line work stays on `phase-c-projection-tdd` until the user explicitly says ready.
- **Don't modify disclosure-only Phase B scope decisions.** FOCAL-1 precedent (user pulled FOCAL `revolving_door.1` IN as a registration-form disclosure observable) does NOT retroactively apply to Newmark/Opheim/HG enforcement items per Sub-0 decision. If a borderline item surfaces, STOP and ask the user before deciding.
- **Don't touch other branches' work.** Multi-committer repo; only modify `phase-c-projection-tdd` and shared infrastructure (STATUS.md row for this branch, RESEARCH_LOG for this branch).
- **Don't skip pre-flight reads.** Sub-0 spent significant effort producing the gap audit and data-years docs. Skimming them risks re-inventing decisions or missing load-bearing facts (item 4 exclusion, per-item vintage splits, weak-inequality regimes).

---

## After your sub-session

Run finish-convo (`/Users/dan/.claude/skills/finish-convo/SKILL.md`). It will:

1. Run update-docs (writes a convo file in `docs/active/phase-c-projection-tdd/convos/`; updates RESEARCH_LOG; updates STATUS Recent Sessions).
2. Stage + commit (`convo: 20260514_<your-convo-name> — sub-N <one-line>`).
3. Push.

The next sub-session continues from your commit. Each sub-session is structured so it can be picked up by a fresh agent reading only the docs you wrote.

---

## Honest uncertainty disclosures from Sub-0's author

Things I'm not 100% certain about that you should verify:

- Whether `/status` in Claude Code displays auth mode visibly. Fall back to `/login` if not.
- Whether `claude -p` (used in Sub-4's launch script) reliably executes a Nori-style plan end-to-end with TDD discipline. Sub-4's canary on Sunlight is supposed to find out — don't fan out to all 6 plans without seeing the canary result.
- Whether the CPI 2007 per-state scorecard is actually retrievable from any current source. Could be fully lost; if so, HG falls back to weak-inequality validation. The retrieval task surfaces this answer.
- Whether the user wants me/you to think harder about Track A's vintage scope (currently 4 vintages; Phase C across all 8 rubrics needs 12). That's a separate-branch conversation, not in scope for Sub-1+.

> **Resolved 2026-05-14 (later, on `Dans-MacBook-Pro`):** Key location documented under "Where the key lives on the user's machines" above — `.env.local` at repo root, single-quoted without `export`, load via `set -a; source ...; set +a`.
