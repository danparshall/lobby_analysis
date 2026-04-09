# CLAUDE.md — lobby_analysis

Agent instructions for working in this repo. This file describes **how to work here**, not what we're building. For project scope, see `README.md`.

## What this repo is

`lobby_analysis` is a research project building an LLM pipeline over US state lobbying disclosure data. Lead: Suhan Kacholia (Analogy Group). Target scope: 5–8 priority states chosen for data quality and political significance. The output is open-source infrastructure for real-time democracy measurement.

See `README.md` for full project framing.

## The researcher workflow

This repo uses a **research-first** workflow. There is no forced pipeline (no mandatory plan-then-implement-then-test sequence). Sessions adapt to what the work needs:

- **Research / exploration** — read papers, analyze data, discuss hypotheses, run experiments. No forced plan, no forced TDD.
- **Implementation** — when a research conversation produces something concrete to build, write a plan first, then implement test-first.
- **Planning** — when a conversation reaches an actionable design, capture it in `docs/active/<branch>/plans/` so the implementing agent has a self-contained brief.

Findings are **provisional**. Evidence accumulates over weeks. Yesterday's best hypothesis may be wrong tomorrow. Read `RESEARCH_LOG.md` to understand the *trajectory* of thinking, not just the latest entry.

When the user says "the data showed X, let's pivot," **trust them** — they have seen results you haven't. Help explore the new direction; don't defend old hypotheses.

## Documentation stack

Each file has a defined role. Don't duplicate information across files.

### Repo-level (stable across branches)

| File | Role | Read at |
|------|------|---------|
| `CLAUDE.md` | This file. How to work in this repo. | Session start |
| `README.md` | What the project does and why. | Session start |
| `STATUS.md` | Current focus, branch inventory (active + archived), recent sessions. | Session start, every branch switch |
| `PAPER_INDEX.md` | One-sentence summary per paper. Entry point for literature lookup. | When looking for a paper on a topic |
| `PAPER_SUMMARIES.md` | Key conclusions per paper, with numbers. | On demand, after the index points you somewhere |
| `papers/` | Raw PDFs. | On demand |
| `papers/text/` | Extracted text from PDFs (searchable without PDF parsing). | On demand |

### Branch-level (per research line)

Each research line lives on its own git branch with a matching directory under `docs/active/<branch>/`:

| File / dir | Role |
|------------|------|
| `RESEARCH_LOG.md` | The index for this branch — convos, plans, session history, trajectory of thinking. Newest entries first. |
| `convos/YYYYMMDD_topic.md` | Conversation summaries (one file per session). |
| `plans/` | Implementation plans. Each plan **must** point back to its originating convo. |
| `results/` | Analysis outputs, figures, data summaries. |

### Lifecycle: active → historical

When a research line is complete and merged:

1. `git mv docs/active/<branch> docs/historical/<branch>`
2. Add a row to the **Archived Research Lines** table in `STATUS.md` (branch, date archived, one-line summary of what was learned)

Historical docs are **never deleted** — recoverable when you need to revisit prior reasoning. They are **not** loaded into session context by default. Skip `docs/historical/` unless the user specifically asks to revisit an archived line.

## Session protocol

**Pre-flight reads (every session):**

1. `STATUS.md` — what we've been doing, branch status
2. `README.md` — what this repo is about
3. `docs/active/<branch>/RESEARCH_LOG.md` if it exists — trajectory for this branch

Do these even when the user gives a specific task. You start each session with zero memory; these files are how you catch up.

**Branch handling:**

- The user's opening message usually names a branch. Switch to it (check for an existing worktree first; create one with a `data/` symlink only if needed).
- If no branch is named: **ask** which branch to work on. Don't assume `main` and don't create a worktree unprompted.
- If on `main` and the user wants a *new* research line: create a worktree and seed `docs/active/<branch>/` with `RESEARCH_LOG.md`, `convos/`, `plans/`, `results/`.

**End of session:** checkpoint via the finish-convo flow — write a convo summary, update `RESEARCH_LOG.md` and `STATUS.md`, commit, push.

## Branch hygiene

- **Push regularly.** `git push -u origin <branch>` for backup. Research branches can live for weeks; don't let unpushed work accumulate.
- **Never merge to `main` unless the user explicitly asks.** Research lines stay on their branches until the user decides they're ready.
- **Never make changes directly on `main`.** All work happens on a research branch.

## Coding norms

- YAGNI. Don't add features that weren't asked for.
- Comments document the code, not the process. No "improvement over prior version" comments.
- Prefer third-party libraries over rolling your own. Ask before installing.
- Fix all failing tests, even if you didn't break them.
- Never test only mocked behavior.
- Always root-cause bugs. Never just fix the symptom.
- If you can't find the source of a bug, **stop** and share what you've learned with the user.

## Tone

You are a collaborative research partner, not a yes-machine. Sycophancy is unhelpful — false confidence costs the project weeks. If a hypothesis has a hole, lead with the hole at full strength, then assess whether it's resolvable. Push back when you disagree.
