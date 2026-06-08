"""Phase 0 pre-flight checks for the gpt-5-mini OH 300-slice validation.

Covers RUNBOOK_day2.md steps 0.1 (baseline confirmation + spot-check) and 0.2
(OpenAI SDK + key + dated model id discovery). Replaces the inline `python3
-c "..."` blocks in the original runbook draft, which were fragile under the
local Bash matcher's anti-obfuscation heuristics.

Usage:
    python scripts/gpt5mini_oh_300slice_preflight.py --check baseline
    python scripts/gpt5mini_oh_300slice_preflight.py --check openai
    python scripts/gpt5mini_oh_300slice_preflight.py --check all   # default

Exit codes:
    0   all requested checks passed
    1   baseline check failed (missing dir, missing/invalid filing.json)
    2   openai check failed (no key, no gpt-5-mini models available)
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Add src/ to sys.path so this script works from `python scripts/...` without
# requiring an editable install in the current shell. Mirrors dispatch.py.
_REPO_ROOT = Path(__file__).resolve().parents[1]
_SRC = _REPO_ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from lobby_analysis.oh_portal.env_local import load_env_local  # noqa: E402
from lobby_analysis.oh_portal.fetch import DATA_DIR  # noqa: E402

# Pinning workflow (Phase 0 step 0.2): if the openai check finds dated mini
# variants on the account, the operator must commit a single dated id to
# `MODEL_ID_DATED` in src/lobby_analysis/oh_portal/extract_openai.py so the
# three dispatch passes all reference the same model snapshot.
_EXTRACT_OPENAI_REL = "src/lobby_analysis/oh_portal/extract_openai.py"


def check_baseline(data_dir: Path) -> int:
    """Confirm the Sonnet baseline directory + spot-check a handful of filings.

    The runbook's original expectation was 300 filings; on disk it's 305 (clean
    numeric-ID directories, no stray files). This check prints whichever count
    is actually present and does not gate on a hardcoded number — the dispatch
    script enumerates from this directory and will run mini against whatever
    is here.
    """
    extracted = data_dir / "extracted"
    if not extracted.is_dir():
        print(f"[preflight/baseline] FAIL — {extracted} missing", file=sys.stderr)
        return 1
    report_ids = sorted(p.name for p in extracted.iterdir() if p.is_dir())
    n = len(report_ids)
    print(f"[preflight/baseline] {n} report_id dirs under {extracted}",
          file=sys.stderr)
    if n == 0:
        print("[preflight/baseline] FAIL — no report_id dirs", file=sys.stderr)
        return 1

    # Deterministic spot-check: first, middle, last. Avoids the runbook's
    # `shuf -n 3` non-determinism, which made re-runs harder to compare.
    sample_idxs = sorted({0, n // 2, n - 1})
    sample_ids = [report_ids[i] for i in sample_idxs]
    any_failure = False
    for rid in sample_ids:
        rdir = extracted / rid
        # Prefer the latest run by sort order (matches dispatch + analyze).
        run_dirs = sorted(
            (d for d in rdir.iterdir() if d.is_dir()), reverse=True
        )
        filing_path = None
        for rd in run_dirs:
            cand = rd / "filing.json"
            if cand.exists():
                filing_path = cand
                break
        if filing_path is None:
            print(f"[preflight/baseline] FAIL — {rid}: no filing.json",
                  file=sys.stderr)
            any_failure = True
            continue
        try:
            d = json.loads(filing_path.read_text())
        except (json.JSONDecodeError, OSError) as exc:
            print(f"[preflight/baseline] FAIL — {rid}: {exc!r}",
                  file=sys.stderr)
            any_failure = True
            continue
        state = d.get("state")
        filer = (d.get("filer_person") or {}).get("name")
        positions = len(d.get("positions") or [])
        print(
            f"[preflight/baseline] {rid}: state={state} filer={filer!r} "
            f"positions={positions}",
            file=sys.stderr,
        )
        if state != "OH":
            print(
                f"[preflight/baseline] WARN — {rid} state is {state!r}, "
                f"expected 'OH'. Slice may not be pure-OH.",
                file=sys.stderr,
            )

    if any_failure:
        return 1
    print(f"[preflight/baseline] OK — {n} filings, 3 spot-checks valid",
          file=sys.stderr)
    return 0


def check_openai() -> int:
    """Confirm OpenAI SDK works + list available gpt-5-mini variants.

    Does NOT pin `MODEL_ID_DATED` on the operator's behalf — that's a code
    edit the operator should make and commit explicitly. Prints the
    recommended dated id and the file/line to edit, then it's a one-line
    `Edit` call away.
    """
    load_env_local()
    import os
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        print(
            "[preflight/openai] FAIL — OPENAI_API_KEY not set "
            "(and not present in .env.local).",
            file=sys.stderr,
        )
        return 2
    print(f"[preflight/openai] OPENAI_API_KEY present (len={len(key)})",
          file=sys.stderr)

    try:
        from openai import OpenAI
    except ImportError as exc:
        print(f"[preflight/openai] FAIL — openai package not importable: {exc!r}",
              file=sys.stderr)
        return 2

    client = OpenAI()
    try:
        models = client.models.list().data
    except Exception as exc:  # noqa: BLE001 — surface whatever the SDK raises
        print(f"[preflight/openai] FAIL — models.list() raised: {exc!r}",
              file=sys.stderr)
        return 2

    mini_ids = sorted(m.id for m in models if "gpt-5-mini" in m.id)
    if not mini_ids:
        print(
            "[preflight/openai] FAIL — no gpt-5-mini models visible on this "
            "account. Check provisioning / tier access.",
            file=sys.stderr,
        )
        return 2

    print(f"[preflight/openai] mini models available ({len(mini_ids)}):",
          file=sys.stderr)
    for mid in mini_ids:
        print(f"  - {mid}", file=sys.stderr)

    # Pick the latest dated variant. The undated alias "gpt-5-mini" rotates
    # under the hood; for reproducibility across 3 runs we want a snapshot.
    dated = [m for m in mini_ids if m != "gpt-5-mini"
             and any(c.isdigit() for c in m.replace("gpt-5-mini", ""))]
    if not dated:
        print(
            "[preflight/openai] WARN — only the undated alias is exposed. "
            "Three-run consistency may be confounded by silent rotation.",
            file=sys.stderr,
        )
        return 0

    recommended = sorted(dated)[-1]  # lexicographically latest dated id
    print(
        f"[preflight/openai] RECOMMENDED pin: {recommended}\n"
        f"  Edit {_EXTRACT_OPENAI_REL}:\n"
        f"      MODEL_ID_DATED: str | None = {recommended!r}\n"
        f"  then commit so all three dispatch passes share the same snapshot.",
        file=sys.stderr,
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check", choices=["baseline", "openai", "all"], default="all",
        help="Which check to run.",
    )
    parser.add_argument(
        "--data-dir", default=str(DATA_DIR),
        help=f"OH portal data dir (default {DATA_DIR}).",
    )
    args = parser.parse_args()
    data_dir = Path(args.data_dir)

    rc = 0
    if args.check in ("baseline", "all"):
        rc = max(rc, check_baseline(data_dir))
    if args.check in ("openai", "all"):
        rc = max(rc, check_openai())
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
