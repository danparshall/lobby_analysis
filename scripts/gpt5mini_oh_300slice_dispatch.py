"""Phase 2 dispatch: 3 runs of gpt-5-mini over the OH 300-slice.

See `docs/active/leave-behind-prep/plans/20260608_gpt5mini_on_oh_300slice.md`.

Operational shape:
  - Enumerates report_ids by listing `data/oh_portal/extracted/` (the Sonnet
    300-slice). Each report_id has a cached `raw.html` in `data/oh_portal/raw/`
    that the OpenAI extractor reuses (no OLAC re-fetch).
  - Three sequential passes (run_label = "mini_run_1", "mini_run_2",
    "mini_run_3"). Each pass writes per-filing outputs to
    `data/oh_portal/extracted_openai/<report_id>/<run_id>/filing.json`.
  - Resume is idempotent: a run_label that already has a filing.json for a
    given report_id is skipped. Re-invoking after a crash picks up where it
    left off; re-running after success is a no-op.
  - Per-filing error isolation: one failure does not abort the pass.

Operator controls (concern #1 from the pre-dispatch review):
  - --pass {1,2,3,all}     : which pass(es) to run. Default: all.
  - --wall-clock-cap SEC   : abort the current pass after this many seconds
                             of wall clock (default 10800 = 3hr). Outputs
                             produced so far are retained; the next pass is
                             not started.
  - --slice REPORT_IDS     : run on a comma-separated subset (smoke testing).
  - --limit N              : run on the first N report_ids only.
  - --resume               : skip filings that already have output (default).
  - --no-resume            : re-run all filings (rarely needed; will overwrite
                             nothing — output dirs use UUIDs — but doubles cost).
  - --reasoning-effort EFF : minimal | low | medium | high — passed through to
                             gpt-5-mini and used to derive the run_label
                             (e.g., --reasoning-effort=minimal --pass=1 →
                             "mini_minimal_run_1"). Omit to use API default
                             and the legacy "mini_run_<N>" label.
  - --max-concurrent N     : ThreadPoolExecutor worker count. Default 1
                             (serial, byte-identical legacy behavior). 10 is
                             recommended for parallel experiments; drop to 5
                             if rate-limited.

Per-pass summary on completion or wall-clock abort:
  - Total filings attempted / extracted / skipped (resume) / failed.
  - Total prompt + completion tokens, total cost (at $0.25/$2 per Mtok).
  - Wall-clock total.
  - Sanity-check after pass 1: counts of filings where the null-field profile
    diverges materially from the Sonnet baseline (per plan step 11).

Run from repo root: `python -m scripts.gpt5mini_oh_300slice_dispatch --pass 1`
or (if scripts/ isn't on sys.path as a package):
`python scripts/gpt5mini_oh_300slice_dispatch.py --pass 1`.
"""

from __future__ import annotations

import argparse
import json
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

# Resolve project paths and add src/ to sys.path so `python scripts/...` works
# without needing `python -m`.
_REPO_ROOT = Path(__file__).resolve().parents[1]
_SRC = _REPO_ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from lobby_analysis.oh_portal.env_local import load_env_local  # noqa: E402
from lobby_analysis.oh_portal.fetch import DATA_DIR  # noqa: E402
from lobby_analysis.oh_portal.pipeline_openai import (  # noqa: E402
    EXTRACTED_OPENAI_SUBDIR,
    extract_one_filing_from_cache,
)

# OpenAI gpt-5-mini list pricing as of June 2026 (per the plan).
# Update if pricing drifts; the analyze step also reads these constants.
COST_PER_MTOK_PROMPT = 0.25  # USD per 1,000,000 prompt tokens
COST_PER_MTOK_COMPLETION = 2.00  # USD per 1,000,000 completion tokens

# Default per-pass wall-clock cap (seconds). Concern #1 from the pre-dispatch
# review: Phase 2 needs its own hard-stop, not just Phase 1.
DEFAULT_PASS_WALL_CLOCK_CAP_S = 10800  # 3 hours per pass


@dataclass
class FilingResult:
    report_id: str
    status: str  # "extracted" | "skipped" | "failed"
    filing_path: str | None
    prompt_tokens: int | None
    completion_tokens: int | None
    cost_usd: float | None
    duration_s: float | None
    error: str | None


def list_sonnet_slice_report_ids(data_dir: Path) -> list[str]:
    """Return the report_ids covered by the Sonnet 300-slice (sorted)."""
    extracted = data_dir / "extracted"
    if not extracted.is_dir():
        raise FileNotFoundError(
            f"No Sonnet baseline at {extracted}; cannot enumerate the 300-slice. "
            "Run the Sonnet pipeline first."
        )
    return sorted(p.name for p in extracted.iterdir() if p.is_dir())


def already_extracted(
    report_id: str, run_label: str, data_dir: Path
) -> Path | None:
    """Return path to existing filing.json for (report_id, run_label), else None."""
    report_dir = data_dir / EXTRACTED_OPENAI_SUBDIR / report_id
    if not report_dir.is_dir():
        return None
    for run_dir in sorted(report_dir.iterdir()):
        # run_id format: f"{run_label}_{uuid8}"
        if not run_dir.name.startswith(f"{run_label}_"):
            continue
        candidate = run_dir / "filing.json"
        if candidate.exists():
            return candidate
    return None


def _cost_usd(prompt_tokens: int, completion_tokens: int) -> float:
    return (
        prompt_tokens / 1_000_000 * COST_PER_MTOK_PROMPT
        + completion_tokens / 1_000_000 * COST_PER_MTOK_COMPLETION
    )


def _process_one_filing(
    report_id: str,
    *,
    run_label: str,
    data_dir: Path,
    resume: bool,
    reasoning_effort: str | None,
    log: callable,
) -> FilingResult:
    """Process a single filing — used by both serial and parallel paths.

    Returns one of three FilingResult shapes (extracted / skipped / failed).
    Per-filing exceptions are caught here so a worker exception never escapes
    to the executor; the result carries the error for the summary to surface.
    """
    if resume:
        existing = already_extracted(report_id, run_label, data_dir)
        if existing is not None:
            return FilingResult(
                report_id=report_id, status="skipped",
                filing_path=str(existing), prompt_tokens=None,
                completion_tokens=None, cost_usd=None,
                duration_s=None, error=None,
            )

    t0 = time.monotonic()
    try:
        filing_path, usage = extract_one_filing_from_cache(
            report_id,
            run_label=run_label,
            data_dir=data_dir,
            log=lambda m: log(f"  {m}"),
            reasoning_effort=reasoning_effort,
        )
        duration = time.monotonic() - t0
        cost = _cost_usd(usage["prompt_tokens"], usage["completion_tokens"])
        return FilingResult(
            report_id=report_id, status="extracted",
            filing_path=str(filing_path),
            prompt_tokens=usage["prompt_tokens"],
            completion_tokens=usage["completion_tokens"],
            cost_usd=cost,
            duration_s=duration,
            error=None,
        )
    except Exception as exc:  # noqa: BLE001 — isolate per-filing failures
        duration = time.monotonic() - t0
        return FilingResult(
            report_id=report_id, status="failed",
            filing_path=None, prompt_tokens=None,
            completion_tokens=None, cost_usd=None,
            duration_s=duration, error=repr(exc),
        )


def run_one_pass(
    report_ids: list[str],
    *,
    run_label: str,
    data_dir: Path,
    wall_clock_cap_s: float,
    resume: bool,
    log: callable,
    reasoning_effort: str | None = None,
    max_concurrent: int = 1,
) -> list[FilingResult]:
    """Execute one pass of mini extraction over `report_ids`.

    Aborts gracefully (returns partial results) if `wall_clock_cap_s` elapses.
    Per-filing failures are captured and the loop continues.

    `max_concurrent=1` preserves the original serial behavior. Higher values
    dispatch via a `ThreadPoolExecutor` — each filing is HTTP-bound to OpenAI,
    so concurrency scales linearly until rate limits bite. The per-filing
    resume skip-check and on-disk write are concurrency-safe (distinct
    report_ids → distinct paths; the `already_extracted` check is a read-only
    `os.listdir`). Progress logging serializes through `_log_lock` so the
    interleaved per-filing lines don't tear.

    Wall-clock semantics under parallelism: the cap means "stop submitting
    new work after T elapsed". Work already in flight is allowed to finish
    (its output would otherwise be wasted billing). This is the right
    behavior because per-filing cost is fixed and per-filing wall-time is
    bounded — letting in-flight tasks complete prevents abandoned spend.
    """
    results: list[FilingResult] = []
    results_lock = threading.Lock()
    log_lock = threading.Lock()
    pass_started = time.monotonic()

    def safe_log(m: str) -> None:
        with log_lock:
            log(m)

    # Pre-compute total counter for progress lines. We can't use enumerate()
    # under concurrency since completion order != submission order.
    total = len(report_ids)
    completed_counter = {"n": 0}

    def record_and_log(report_id: str, result: FilingResult) -> None:
        with results_lock:
            results.append(result)
            completed_counter["n"] += 1
            i = completed_counter["n"]
        if result.status == "extracted":
            safe_log(
                f"[{run_label}] [{i}/{total}] "
                f"{report_id} OK ({result.duration_s:.1f}s, "
                f"{result.prompt_tokens}+{result.completion_tokens} tok, "
                f"${result.cost_usd:.4f})"
            )
        elif result.status == "failed":
            safe_log(
                f"[{run_label}] [{i}/{total}] {report_id} FAILED :: "
                f"{result.error}"
            )
        # "skipped" intentionally not logged — would be noisy on resume

    # Serial fast path — preserves byte-identical behavior for max_concurrent=1
    # (no executor overhead, no thread-creation, no ordering ambiguity).
    if max_concurrent <= 1:
        for report_id in report_ids:
            elapsed = time.monotonic() - pass_started
            if elapsed > wall_clock_cap_s:
                safe_log(
                    f"[{run_label}] wall-clock cap {wall_clock_cap_s}s "
                    f"exceeded; aborting pass."
                )
                break
            result = _process_one_filing(
                report_id,
                run_label=run_label,
                data_dir=data_dir,
                resume=resume,
                reasoning_effort=reasoning_effort,
                log=safe_log,
            )
            record_and_log(report_id, result)
        return results

    # Parallel path.
    with ThreadPoolExecutor(max_workers=max_concurrent) as executor:
        future_to_rid: dict = {}
        for report_id in report_ids:
            elapsed = time.monotonic() - pass_started
            if elapsed > wall_clock_cap_s:
                safe_log(
                    f"[{run_label}] wall-clock cap {wall_clock_cap_s}s "
                    f"exceeded; not submitting remaining "
                    f"{len(report_ids) - len(future_to_rid)} filings. "
                    f"In-flight work will complete."
                )
                break
            future = executor.submit(
                _process_one_filing,
                report_id,
                run_label=run_label,
                data_dir=data_dir,
                resume=resume,
                reasoning_effort=reasoning_effort,
                log=safe_log,
            )
            future_to_rid[future] = report_id

        for future in as_completed(future_to_rid):
            report_id = future_to_rid[future]
            # _process_one_filing catches per-filing exceptions; future.result()
            # only raises if something pathological happens in the wrapper
            # itself (e.g., the function reference is broken). Surface as
            # failed result rather than crashing the whole pass.
            try:
                result = future.result()
            except Exception as exc:  # noqa: BLE001
                result = FilingResult(
                    report_id=report_id, status="failed",
                    filing_path=None, prompt_tokens=None,
                    completion_tokens=None, cost_usd=None,
                    duration_s=None, error=f"executor-level: {exc!r}",
                )
            record_and_log(report_id, result)

    return results


def summarize_pass(run_label: str, results: list[FilingResult]) -> dict:
    """Compute totals + per-pass summary for the runbook + cost projection."""
    extracted = [r for r in results if r.status == "extracted"]
    skipped = [r for r in results if r.status == "skipped"]
    failed = [r for r in results if r.status == "failed"]
    total_prompt = sum(r.prompt_tokens or 0 for r in extracted)
    total_completion = sum(r.completion_tokens or 0 for r in extracted)
    total_cost = sum(r.cost_usd or 0 for r in extracted)
    total_wall = sum(r.duration_s or 0 for r in extracted)
    return {
        "run_label": run_label,
        "n_attempted": len(results),
        "n_extracted": len(extracted),
        "n_skipped_resume": len(skipped),
        "n_failed": len(failed),
        "total_prompt_tokens": total_prompt,
        "total_completion_tokens": total_completion,
        "total_cost_usd": round(total_cost, 4),
        "total_wall_clock_s": round(total_wall, 1),
        "avg_s_per_filing": (
            round(total_wall / len(extracted), 2) if extracted else None
        ),
        "failed_report_ids": [r.report_id for r in failed],
    }


def post_run1_sanity_diff(
    report_ids: list[str],
    data_dir: Path,
    run_label_prefix: str = "mini_run_1_",
) -> dict:
    """Per plan step 11: compare null-field profile of Run 1 vs Sonnet baseline.

    If many fields are null in mini that Sonnet populated (or vice versa),
    surface it before burning Runs 2+3. This is a structural check, not a
    correctness check — the analyze step (Phase 3) does the latter.

    `run_label_prefix` defaults to the legacy "mini_run_1_" prefix; pass the
    effort-coupled prefix (e.g., "mini_minimal_run_1_") when running with
    --reasoning-effort.
    """
    sonnet_null_counts: dict[str, int] = {}
    mini_null_counts: dict[str, int] = {}
    sonnet_dir = data_dir / "extracted"
    mini_dir = data_dir / EXTRACTED_OPENAI_SUBDIR
    n_compared = 0

    for report_id in report_ids:
        sonnet_filing = _latest_filing_json(sonnet_dir / report_id)
        mini_filing = _latest_filing_json(
            mini_dir / report_id, run_label_prefix=run_label_prefix
        )
        if not (sonnet_filing and mini_filing):
            continue
        s = json.loads(sonnet_filing.read_text())
        m = json.loads(mini_filing.read_text())
        for k, v in s.items():
            if v is None:
                sonnet_null_counts[k] = sonnet_null_counts.get(k, 0) + 1
        for k, v in m.items():
            if v is None:
                mini_null_counts[k] = mini_null_counts.get(k, 0) + 1
        n_compared += 1

    field_divergence = []
    for k in set(sonnet_null_counts) | set(mini_null_counts):
        s_null = sonnet_null_counts.get(k, 0)
        m_null = mini_null_counts.get(k, 0)
        diff = abs(s_null - m_null)
        # Flag if the null-rate differs by >10% of compared filings.
        if n_compared > 0 and diff / n_compared > 0.10:
            field_divergence.append({
                "field": k,
                "sonnet_null_count": s_null,
                "mini_null_count": m_null,
                "n_compared": n_compared,
            })

    return {
        "n_compared": n_compared,
        "fields_with_diverging_null_rate": sorted(
            field_divergence, key=lambda d: -abs(
                d["sonnet_null_count"] - d["mini_null_count"]
            )
        ),
    }


def _latest_filing_json(
    report_dir: Path, run_label_prefix: str | None = None
) -> Path | None:
    """Return the most recent filing.json under report_dir, by file mtime.

    Sorting by name was buggy for legacy bare-UUID run_ids: lex order doesn't
    match temporal order, so when a report had multiple runs, the function
    could return an arbitrary one (e.g., 1492516 returned the old legacy
    extraction instead of the post-schema-fix re-extraction). mtime is the
    actual semantic we want.
    """
    if not report_dir.is_dir():
        return None
    candidates: list[Path] = []
    for d in report_dir.iterdir():
        if not d.is_dir():
            continue
        if run_label_prefix is not None and not d.name.startswith(run_label_prefix):
            continue
        fj = d / "filing.json"
        if fj.exists():
            candidates.append(fj)
    if not candidates:
        return None
    return max(candidates, key=lambda p: p.stat().st_mtime)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--pass",
        dest="which_pass",
        default="all",
        choices=["1", "2", "3", "all"],
        help="Which pass(es) to run. Default: all three sequentially.",
    )
    parser.add_argument(
        "--wall-clock-cap",
        type=float,
        default=DEFAULT_PASS_WALL_CLOCK_CAP_S,
        help=(
            "Per-pass wall-clock abort threshold in seconds "
            f"(default {DEFAULT_PASS_WALL_CLOCK_CAP_S} = 3hr). "
            "If exceeded, the current pass writes its summary and the next "
            "pass is not started."
        ),
    )
    parser.add_argument(
        "--slice", default=None,
        help="Comma-separated report_ids to run on (smoke testing).",
    )
    parser.add_argument(
        "--limit", type=int, default=None,
        help="Run on only the first N report_ids (smoke testing).",
    )
    parser.add_argument("--resume", action="store_true", default=True)
    parser.add_argument("--no-resume", dest="resume", action="store_false")
    parser.add_argument(
        "--data-dir", default=str(DATA_DIR),
        help=f"Data directory (default {DATA_DIR}).",
    )
    parser.add_argument(
        "--out-summary", default=None,
        help="Path to write the run summary JSON. Default: stderr only.",
    )
    parser.add_argument(
        "--reasoning-effort",
        default=None,
        choices=["minimal", "low", "medium", "high"],
        help=(
            "Reasoning effort for gpt-5-family models. When set, the value is "
            "(a) forwarded to chat.completions.parse, and (b) used to derive "
            "the per-pass run_label (e.g., --reasoning-effort=minimal --pass=1 "
            "→ run_label='mini_minimal_run_1'). When omitted (default), the "
            "API's own default applies and the legacy run_label "
            "'mini_run_<N>' is used — preserves byte-identical behavior for "
            "any caller that doesn't opt into the new dial."
        ),
    )
    parser.add_argument(
        "--max-concurrent",
        type=int,
        default=1,
        help=(
            "Number of filings to dispatch concurrently via ThreadPoolExecutor. "
            "Default 1 (serial, byte-identical legacy behavior). Each filing "
            "is HTTP-bound to OpenAI; concurrency scales linearly until "
            "rate-limits engage. Recommended starting point for parallel "
            "experiments: 10. Reduce to 5 if TPM/RPM limits trip."
        ),
    )
    args = parser.parse_args()

    load_env_local()
    data_dir = Path(args.data_dir)

    if args.slice:
        report_ids = [r.strip() for r in args.slice.split(",") if r.strip()]
    else:
        report_ids = list_sonnet_slice_report_ids(data_dir)
    if args.limit:
        report_ids = report_ids[: args.limit]
    print(
        f"[dispatch] {len(report_ids)} report_ids in scope; "
        f"per-pass wall-clock cap = {args.wall_clock_cap:.0f}s",
        file=sys.stderr,
    )

    # Couple run_label to reasoning_effort so the three experimental arms
    # (medium / low / minimal) write to distinct on-disk namespaces and the
    # analyze step can attribute outputs to settings without parsing
    # extraction_run.json. When --reasoning-effort is None (legacy default)
    # the label stays at the bare "mini_run_<N>" form.
    label_prefix = (
        f"mini_{args.reasoning_effort}_run" if args.reasoning_effort
        else "mini_run"
    )
    if args.which_pass == "all":
        passes = [f"{label_prefix}_{n}" for n in (1, 2, 3)]
    else:
        passes = [f"{label_prefix}_{args.which_pass}"]

    log = lambda m: print(m, file=sys.stderr)
    summaries = []
    aborted_early = False
    for run_label in passes:
        print(f"\n========== {run_label} starting ==========", file=sys.stderr)
        run_started = datetime.now(timezone.utc)
        results = run_one_pass(
            report_ids,
            run_label=run_label,
            data_dir=data_dir,
            wall_clock_cap_s=args.wall_clock_cap,
            resume=args.resume,
            log=log,
            reasoning_effort=args.reasoning_effort,
            max_concurrent=args.max_concurrent,
        )
        summary = summarize_pass(run_label, results)
        summary["started_at"] = run_started.isoformat()
        summary["finished_at"] = datetime.now(timezone.utc).isoformat()
        print(
            f"[{run_label}] DONE — {json.dumps(summary, indent=2)}",
            file=sys.stderr,
        )

        # Concern #1 follow-through: did we abort early on wall-clock?
        if len(results) < len(report_ids):
            print(
                f"[{run_label}] aborted early at "
                f"{len(results)}/{len(report_ids)} filings; "
                f"NOT starting subsequent passes.",
                file=sys.stderr,
            )
            aborted_early = True

        if run_label.endswith("_run_1"):
            sanity = post_run1_sanity_diff(
                report_ids, data_dir, run_label_prefix=f"{run_label}_"
            )
            summary["post_run1_sanity"] = sanity
            print(
                f"[{run_label}] post-run sanity diff vs Sonnet:\n"
                f"{json.dumps(sanity, indent=2)}",
                file=sys.stderr,
            )
            if sanity["fields_with_diverging_null_rate"]:
                print(
                    f"[{run_label}] ^^^ Review fields with diverging null rates "
                    f"before launching the next pass. Re-invoke with --pass 2 "
                    "once reviewed.",
                    file=sys.stderr,
                )

        summaries.append(summary)
        if aborted_early:
            break

    full_report = {
        "passes": summaries,
        "aborted_early": aborted_early,
        "total_cost_usd": round(
            sum(s["total_cost_usd"] for s in summaries), 4
        ),
        "total_wall_clock_s": round(
            sum(s["total_wall_clock_s"] for s in summaries), 1
        ),
    }
    if args.out_summary:
        Path(args.out_summary).write_text(json.dumps(full_report, indent=2))
        print(f"[dispatch] summary written to {args.out_summary}", file=sys.stderr)
    print(f"\n[dispatch] FINAL: {json.dumps(full_report, indent=2)}", file=sys.stderr)

    # Exit non-zero if anything failed, so an orchestrating agent can notice.
    any_failed = any(s["n_failed"] > 0 for s in summaries)
    return 1 if (any_failed or aborted_early) else 0


if __name__ == "__main__":
    raise SystemExit(main())

