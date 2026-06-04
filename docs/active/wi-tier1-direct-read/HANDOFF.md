# HANDOFF — WI 2025 Tier-1 direct-read, Phase 2 (the paid run)

**For:** the next agent/session, on a machine with comfortable disk headroom.
**State:** Phase 1 (state-keying generalization) is committed + verified on branch `wi-tier1-direct-read`. Only the paid extraction run (Phase 2) and write-up (Phase 3) remain.
**Why deferred:** `Dans-MacBook-Pro` was at 98–99% disk and intermittently hit 0-free mid-write (recurring ENOSPC). A checkpoint written in a 0-free window would be corrupt-but-present and silently skipped by resume — unacceptable for a paid run. Run this where disk is healthy.

---

## 0. Pick up the branch

```
git -C <repo> fetch origin
git -C <repo> checkout wi-tier1-direct-read     # or a worktree off it
```

If using a fresh worktree, symlink `data/` and `.env.local` to the main worktree (repo convention; `data/` is where the WI statute bundle lives).

Set up the **worktree-local** venv (the MEMORY note: pytest/uv in a worktree can otherwise resolve to main's venv):

```
uv venv --python 3.12
uv sync --extra dev      # dev extra installs pytest + ruff; plain `uv sync` does NOT
```

Sanity: `uv run pytest tests/test_tier_1_state_keying.py tests/test_tier_1_legal_axis.py -q` → 34 passed.

## 1. Pre-flight (before any API spend)

1. **Disk:** `df -h <home>` — confirm comfortable headroom (the trigger for this handoff). The run writes ~36 small JSON files; the risk was the volume hitting 0-free, not run size.
2. **WI bundle present:** `ls data/statutes/WI/2025/sections/*.txt` → 16 files (resolves through the `data/` symlink chain).
3. **Both API keys loaded into the environment** — the script's `_preflight` aborts before spend if either is unset:
   - `ANTHROPIC_API_KEY` and `OPENAI_API_KEY` must be in `os.environ`. Export them (or source `.env.local`) in the shell that runs the script. `.env.local` is NOT auto-loaded by the script.
4. **Model strings:** script pins `claude-opus-4-7` + `gpt-5.2-2025-12-11` (from `tier_0`). If either 404s, that's model-version drift — surface it, do NOT silently swap models.

## 2. Run

```
# from the worktree root, with both keys exported:
uv run python scripts/tier_1_direct_read_legal_axis.py --state WI --vintage 2025
```

- `--state`/`--vintage` are **required** (no default — prevents an accidental OH re-run).
- 36 dispatches = 2 models × 6 chunks × 3 runs. Expected cost ~$2–4 (WI's 16 sections / ~73 KB is smaller than OH's). Ceilings: $1/call, $10/session (script aborts if exceeded).
- **Checkpoint/resume:** if it aborts (cost ceiling, rate limit, crash, ENOSPC), just re-invoke the same command — completed `(model, chunk, run)` files are skipped. **Do not delete partial outputs.**
- Outputs land in: `docs/active/wi-tier1-direct-read/results/tier_1/WI_2025/`
  (state-keyed — physically separate from the OH pilot's files in `docs/historical/extraction-harness-brainstorm/results/tier_1/`, so no collision/resume-skip).

## 3. Post-run integrity check (recommended given the ENOSPC history)

Before trusting the metric, confirm every checkpoint parses (a 0-free-window write could be truncated). Quick check:

```
uv run python - <<'PY'
import json, glob
bad = []
for p in glob.glob("docs/active/wi-tier1-direct-read/results/tier_1/WI_2025/*.json"):
    try: json.load(open(p))
    except Exception as e: bad.append((p, repr(e)))
print("files:", len(glob.glob("docs/active/wi-tier1-direct-read/results/tier_1/WI_2025/*.json")))
print("corrupt:", bad)
PY
```

Expect 36 files, `corrupt: []`. If any are corrupt, remove ONLY those files and re-invoke the run (resume re-dispatches the missing triples). A corrupt-but-present file would otherwise be skipped by resume and skew sigma_noise.

## 4. Phase 3 — write up + checkpoint

- The script prints per-model `sigma_noise` (= `pct_stable`, % of cells stable across the 3 runs). Record WI's figure per model; compare to the OH pilot's numbers.
- Flag WI-specific surprises: frequent `record_unscoreable_cell` (out-of-bundle cross-refs), dict-shape cell misemission (`TimeThresholdCell`), or qualitative-trigger rows the legal-axis schema can't faithfully encode (WI ch. 13 has its own triggers; expect analogues of OH's "main purpose" gate — this signals Tier-2 work, NOT a bug in this run).
- `update-docs`: write a Phase-2/3 convo summary, save results with provenance, update `RESEARCH_LOG.md` + the STATUS row for this branch. Commit + push.

## Reference: what's already verified (dry-run, no API)

- bundle: `data/statutes/WI/2025/sections` — exists, 16 `.txt`
- results dir: `…/results/tier_1/WI_2025`
- 6 chunks present, **84 legal cells** total: lobbying_definitions(15), registration_thresholds(6), registration_mechanics_and_exemptions(8), lobbyist_spending_report(30), principal_spending_report(23), enforcement_and_audits(2)
- models: `('claude-opus-4-7', 'gpt-5.2-2025-12-11')`; **36 planned dispatches**

## Open / flagged items

- **`tests/test_pipeline.py` failures (3) — FIXED** (commit `a3bc1af`). The `2026-04-13` portal snapshots were lost in the laptop data-loss event and re-fetched as `2026-05-01` across all 8 states; `SNAPSHOT_DATE_DEFAULT` lagged. Bumped to `2026-05-01`; full suite now 1550 passed, 0 failures.
- `_ORIGINATING_CONVO` constant still points at the OH Tier-0 convo (method lineage); stamped into provenance alongside correct `state_abbr`/`vintage_year`. Update post-hoc if a WI-specific pointer is wanted.
