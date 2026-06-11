# WI 2025 Tier-1 Direct-Read Extraction — Implementation Plan

**Goal:** Run the existing Tier-1 direct-read legal-axis extraction harness against the Wisconsin 2025 statute bundle, producing per-chunk typed-cell extractions + an inter-run agreement (sigma_noise) metric, mirroring the OH 2025 pilot — but first generalize the script so a new state cannot collide with or resume-skip the OH results.

**Originating conversation:** No formal convo doc exists for this session (it was an orientation/error-correction session on 2026-05-28→30). The fresh session should capture one via `update-docs` before/after implementing. Key reasoning is inlined in the Context + What-could-change sections below.

**Context:** We want to extend the "direct-read" statute-reading method (one of the harness line's methods of answering v2-compendium questions) from the OH 2025 pilot to a second state. WI was chosen because the WI 2025 statute bundle is already on disk and verified, and WI 2025 portal filing data was just released (`releases/wi/`), so a WI statute-side extraction pairs naturally with it. This is a multi-state-uniformity step toward the Compendium 2.0 success criterion ("ONE extraction pipeline applied uniformly across states").

**Confidence:** Medium-high on the *mechanics* (the Tier-1 harness ran clean on OH 2025 on 2026-05-20; the WI bundle loads + sha256-verifies; the loader globs `sections/*.txt` so WI's different filenames are a non-issue). Lower on *WI-specific extractability* — WI ch. 13 has its own qualitative triggers that may stress the legal-axis schema the way OH's "main purpose" gate did (that's Tier-2 territory, out of scope here).

**Architecture:** `scripts/tier_1_direct_read_legal_axis.py` currently hardcodes `_STATE_ABBR = "OH"`, `_VINTAGE_YEAR = 2025`, and an un-state-keyed `_RESULTS_DIR`. Generalize: add `--state`/`--vintage` CLI args and key the results/checkpoint directory by `<STATE>_<VINTAGE>`. Then invoke for WI 2025. The script reuses `tier_0_direct_read_smoke.py` (schemas, SDK tool wrappers, response parser, statute loader, `_instantiate_cell`, cost helpers) and the `chunks_v2` manifest + `models_v2` cells — none of that changes.

**Branch:** Recommend a **new branch off current `origin/main`**, e.g. `wi-tier1-direct-read`. Rationale: `main` already contains the tier scripts + `chunks_v2` + `models_v2` (commit `5a467d6` and later); the local `extraction-harness-brainstorm` worktree is in a messy state (ahead 2 / behind 68) and does **not** have the tier_1 script. A fresh main-based branch avoids that reconciliation entirely. Move this plan file into `docs/active/wi-tier1-direct-read/plans/` after creating the branch (it's written under the harness plans dir only because that dir already exists on main). Per repo CLAUDE.md: never run on `main` itself.

**Tech Stack:** Python 3.12, `uv`, pytest; `anthropic` + `openai` SDKs; v2 compendium (`disclosure_side_compendium_items_v2.tsv`), `chunks_v2`, `models_v2`.

---

## Pre-flight (do before any code or API spend)

1. **Disk space.** This machine hit 100%-full during planning (and a small temp filesystem under `/private/tmp/claude-501/.../tasks` filled, silently truncating command output with ENOSPC). Confirm `df -h /Users/dan` shows comfortable headroom (the run writes ~36 JSON files + checkpoints; small, but the temp FS is fragile). If command output goes missing, suspect ENOSPC, not a logic bug.
2. **Sync `main`.** `git -C <repo> fetch origin`; verify `main == origin/main`; create the new branch off `origin/main`.
3. **Branch + worktree.** Create `wi-tier1-direct-read` (use the `use-worktree` skill; symlink `data/` and `.env.local` into the worktree per repo convention).
4. **WI 2025 bundle present.** Confirm `data/statutes/WI/2025/sections/*.txt` resolves through the `data/` symlink chain to `~/data/lobby_analysis/statutes/WI/2025/sections/` (15 sections, manifest sha256-verified during planning). The script's `_preflight` already fails fast if the bundle dir is absent — "do not substitute another vintage."
5. **API keys.** `.env.local` contains `ANTHROPIC_API_KEY` + `OPENAI_API_KEY`. The script's `_preflight` reads `os.environ`; confirm the runner actually loads `.env.local` into the environment (export both, or use the repo's `load_env_local` helper) — otherwise it aborts before spending.
6. **Model strings.** Script targets `claude-opus-4-7` and `gpt-5.2-2025-12-11` (from `tier_0`). These ran on 2026-05-20; if either now 404s, that's model-version drift, not a WI problem — surface it, don't silently swap models.

---

## Testing Plan

The generalization is a behavioral code change (output-path isolation + CLI parameterization) and gets TDD. The extraction *run itself* is analysis/exploration and does not.

I will add unit tests (in a new `tests/test_tier_1_state_keying.py`) that verify **behavior**, not types or mocks:

- **Collision isolation:** the results/checkpoint directory (and therefore `dispatch_result_path`) for `(WI, 2025)` is a *different path* from `(OH, 2025)` — so a WI run can never write into or read from the OH pilot's result files.
- **Resume isolation:** `is_dispatch_done(...)` returns `False` for a `(WI, 2025, model, chunk, run)` triple when only the corresponding `(OH, 2025, ...)` file exists on disk. (This is the bug the change exists to prevent: today both states share `results/tier_1/`, so OH's `{model}__{chunk}__run{n}.json` files would make the WI run skip every dispatch and silently emit OH answers labeled WI.)
- **Argument threading:** invoking `main()` with `--state WI --vintage 2025` sets the bundle dir to `data/statutes/WI/2025/sections` and the results dir to the WI-keyed path (assert via a dry-run/`--plan-only` path or by inspecting the resolved constants, without dispatching any API call).

These exercise the real path-resolution and resume logic; no network, no model mocking of "did it answer correctly."

NOTE: I will write *all* tests before I add any implementation behavior.

---

## Steps

### Phase 1 — generalize the script (TDD)

1. Write `tests/test_tier_1_state_keying.py::test_results_dir_is_state_vintage_keyed` (asserts WI and OH resolve to different results dirs). Run it; watch it fail.
2. Write `::test_resume_isolation_across_states` (only-OH-files-on-disk ⇒ WI dispatch not "done"). Run; watch it fail.
3. Write `::test_cli_args_set_bundle_and_results_paths` for `--state WI --vintage 2025`. Run; watch it fail.
4. Implement minimally: add `argparse` with `--state` (default `OH`) and `--vintage` (default `2025`); replace the module-level `_STATE_ABBR`/`_VINTAGE_YEAR`/`_STATUTE_BUNDLE_DIR`/`_RESULTS_DIR` constants with values derived from the parsed args inside `main()` (thread into `_preflight` and the runner). Key `_RESULTS_DIR` as `.../results/tier_1/<STATE>_<VINTAGE>/`. Leave `dispatch_result_path` signature unchanged (it already takes `results_dir`).
5. Run the new tests; make them pass.
6. Run the full suite (`uv run pytest`) — fix anything the refactor broke. (Heed the MEMORY note: pytest in a worktree can resolve to main's venv; run with the worktree's `.venv` active.)
7. Confirm the OH default still resolves to the original-style path so the existing OH pilot artifacts are untouched.
8. Commit: "tier-1: parameterize state/vintage + state-key results dir (no cross-state collision)".

### Phase 2 — run WI 2025 (analysis)

9. Dry-run / inspect: confirm `--state WI --vintage 2025` resolves the bundle to the WI sections and the results dir to `results/tier_1/WI_2025/`, and that the 6 `_RESOLVED_CHUNKS` all exist in the `chunks_v2` manifest (state-agnostic; should be fine).
10. Run `uv run python scripts/tier_1_direct_read_legal_axis.py --state WI --vintage 2025` (with both keys exported). 36 dispatches (2 models × 6 chunks × 3 runs), checkpoint/resume per dispatch. Expected cost ~$2–4 (WI's 15 sections / ~73 KB is *smaller* than OH's 30 / 143 KB, so likely toward the low end); ceilings stay at $1/call, $10/session.
11. If it aborts mid-run (cost ceiling, rate limit, crash, ENOSPC): just re-invoke — resume skips completed `(model, chunk, run)` files. Do **not** delete partial outputs.
12. Inspect `results/tier_1/WI_2025/`: per-(model, chunk, run) JSON + the sigma_noise agreement summary.

### Phase 3 — write up + checkpoint

13. Note WI's inter-run agreement (sigma_noise) per model; compare to the OH pilot's numbers.
14. Flag WI-specific surprises: cells frequently `record_unscoreable_cell` (out-of-bundle cross-refs), dict-shape cells (e.g. `TimeThresholdCell`) misemitted, or qualitative-trigger rows where the legal-axis schema can't faithfully encode WI's statute (the OH "main purpose" failure mode — expect analogues; this signals Tier-2 work, not a bug in this run).
15. `update-docs`: write the session convo summary, save the WI results with provenance, update RESEARCH_LOG + STATUS (only the rows for this branch). Commit + push.

---

**Testing Details:** Tests assert path *separation* and resume *isolation* between (WI,2025) and (OH,2025) — real behavior of the checkpoint system — plus CLI argument threading into the resolved bundle/results paths. No test asserts model answer correctness or mocks the SDK boundary for "did it score right."

**Implementation Details:**
- Only `scripts/tier_1_direct_read_legal_axis.py` changes; `tier_0` (loader, schemas, tools, parser, cost helpers), `chunks_v2`, and `models_v2` are reused unchanged.
- The statute loader globs `sections/*.txt` and concatenates — WI's `chapter-13-section-13-*.txt` filenames need no special handling; section order is cosmetic (one concatenated blob).
- The crux is the **un-state-keyed `_RESULTS_DIR`** → state-collision/resume-skip. Keying it by `<STATE>_<VINTAGE>` is the one correctness-critical fix; everything else is ergonomics.
- The 6 `_RESOLVED_CHUNKS` are v2-compendium-level (the CPI-2015 C11 de-jure set), state-agnostic — same chunks for WI.
- Legal axis only; the practical (de facto) axis is Prong 2's job and must not be dispatched here.
- `_preflight` already fails fast on missing keys / missing bundle before any spend — keep that guarantee when threading args.

**What could change:**
- If WI's legal-axis extraction produces many qualitative-trigger encoding failures, the takeaway shifts from "harness generalizes cleanly" to "schema needs Tier-2 treatment for WI" — that's a finding, not a failure.
- Model strings may drift; the run is pinned to whatever `tier_0` declares.
- If the team decides to continue on `extraction-harness-brainstorm` instead of a fresh branch, the parameterization still applies — but that worktree must first reconcile its ahead-2/behind-68 state, which is why a main-based branch is recommended.

**Questions:**
1. New branch off `main` (recommended) vs. continue on `extraction-harness-brainstorm`?
2. Both models (opus-4-7 + gpt-5.2), as in the OH pilot? Or single-model for a cheaper first WI pass?
3. Keep `--state`/`--vintage` defaulting to OH/2025 (backward-compat) or make them required (forces explicit intent, prevents an accidental OH re-run)?

---
