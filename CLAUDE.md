# CLAUDE.md — lobby_analysis

Agent instructions for working in this repo. This file describes **how to work here**, not what we're building. For project scope, see `README.md`.

## What this repo is

`lobby_analysis` is a research project building an LLM pipeline over US state lobbying disclosure data. It is a **group project of the Corda Democracy Fellowship**, led by Suhan Kacholia (Analogy Group), with multiple fellows contributing. Target scope: 5–8 priority states chosen for data quality and political significance. The output is open-source infrastructure for real-time democracy measurement.

See `README.md` for full project framing.

## Collaboration: this is a multi-committer repo

Multiple fellows push to this repo. Treat branch hygiene as load-bearing — your local view of `main` may be behind, and other branches may belong to other people.

- **`git fetch` at session start** so STATUS.md and the active branch list reflect what's actually on the remote, not just your local clone.
- **Never rebase, force-push, or rewrite history on a branch you don't own.** If a branch wasn't created in this session and you don't know whose it is, ask before touching it.
- **Never delete remote branches.** Even merged ones — leave cleanup to the branch owner.
- **Pull before pushing** on any shared branch (including any branch you didn't create this session). If there are conflicts on someone else's work, **stop and surface them** rather than auto-resolving.
- When updating `STATUS.md`, only edit rows for the branch you're working on. Don't rewrite other fellows' entries.
- When in doubt about whether a change affects shared state, ask the user first.

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

## Skills

Shared skill definitions live in `skills/` at the repo root. These are instructions that guide Claude Code through specific workflows. When a skill is relevant to a task, read `skills/<skill-name>/SKILL.md` before proceeding.

Key skills for the researcher workflow:

| Skill | When to use |
|-------|-------------|
| `using-skills` | Read before any conversation — explains how to use skills |
| `add-paper` | Adding a paper to the research collection |
| `audit-docs` | Check `docs/active/` structure for consistency |
| `auditing-paper-summaries` | Check `papers/` structure and summary accuracy |
| `finish-convo` | End a research session — checkpoint, commit, push |
| `update-docs` | Mid-session checkpoint (convo summary, RESEARCH_LOG, STATUS) |
| `write-a-plan` | Turn a research conversation into an implementation plan |
| `use-worktree` | Create an isolated workspace for a research branch |
| `init-research-repo` | Set up the researcher skeleton (already done for this repo) |
| `handle-large-tasks` | Split large plans into context-friendly chunks |

Development skills (use when implementing):

| Skill | When to use |
|-------|-------------|
| `test-driven-development` | Implementing any feature or bugfix |
| `systematic-debugging` | Encountering any bug or unexpected behavior |
| `root-cause-tracing` | Tracing errors backward through call stack |
| `creating-debug-tests-and-iterating` | Replicating a bug to see what's wrong |
| `testing-anti-patterns` | Writing or changing tests — what NOT to do |
| `receiving-code-review` | Before implementing code review feedback |
| `finishing-a-development-branch` | Ready to create a PR |
| `brainstorming` | Before writing code — refine ideas into designs |
| `building-ui-ux` | Implementing user interfaces |
| `webapp-testing` | Building or debugging a webapp frontend |

Meta / maintenance skills:

| Skill | When to use |
|-------|-------------|
| `clean-worktrees` | Clean up accumulated git worktrees |
| `creating-skills` | Create a new custom skill |
| `maintaining-decision-docs` | Keep DOCS_INDEX / DOCS_SUMMARY consistent |
| `updating-noridocs` | Update code documentation after structural changes |
| `nori-info` | Questions about the Nori skills system |
| `using-screenshots` | Capture screen context |

## Tone

You are a collaborative research partner, not a yes-machine. Sycophancy is unhelpful — false confidence costs the project weeks. If a hypothesis has a hole, lead with the hole at full strength, then assess whether it's resolvable. Push back when you disagree.
