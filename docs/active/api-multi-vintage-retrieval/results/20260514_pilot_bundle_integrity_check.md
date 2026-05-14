<!-- Generated during: convos/20260514_api_multi_vintage_kickoff.md -->

# Pilot-state statute bundle integrity check

**Date:** 2026-05-14
**Branch:** `api-multi-vintage-retrieval`
**Convo:** [`../convos/20260514_api_multi_vintage_kickoff.md`](../convos/20260514_api_multi_vintage_kickoff.md)
**Purpose:** Verify that the existing statute bundles under `data/statutes/` survived the user's laptop crash, before scoping any re-retrieval work. The crash dropped the laptop's repo checkout; the `data/` symlink chain (worktree → main → `~/data/lobby_analysis/`) means the canonical data root sits on the desktop, but that assumption needed evidence.

## Method

One-shot Python script (`/tmp/verify_statute_bundles.py`, not committed — re-runnable in 5 min if needed again) that, for each `(state, vintage)` under `data/statutes/`:

1. Loads `manifest.json`.
2. For each artifact: checks file exists, byte size matches manifest, sha256 hash matches manifest.
3. Scans the first 2 KB for Cloudflare challenge-stub markers (`"Just a moment"`, `"Checking your browser"`, `"Enable JavaScript and cookies"`, `"cf-browser-verification"`, `"Attention Required"`).
4. Lists orphan files (present in `sections/` but not in manifest).

## Result: **OK across all 7 bundles**

| State / vintage | Artifacts | Total bytes | Hashes match | Challenge stubs | Orphans |
|---|---:|---:|:---:|:---:|---:|
| CA 2010 | 5 | 94,502 | ✓ | none | 3 (see below) |
| TX 2009 | 8 | 714,305 | ✓ | none | 0 |
| NY 2010 | 1 | 51,917 | ✓ | none | 0 |
| WI 2010 | 16 | 72,995 | ✓ | none | 0 |
| WY 2010 | 1 | 8,526 | ✓ | none | 0 |
| OH 2010 | 39 | 263,103 | ✓ | none | 0 |
| OH 2025 | 30 | 143,408 | ✓ | none | 0 |
| **Total** | **100** | **1,348,756** | **✓** | **none** | **3** |

OH 2025's 143,408 bytes and 30 sections match STATUS.md's prior entry exactly ("~143 KB", "30 sections" — `pri-calibration` 2026-04-30 session), an independent confirmation that disk contents are what was originally retrieved.

## CA 2010 orphan files

Three files in `data/statutes/CA/2010/sections/` are not listed in `manifest.json`:

- `gov-91000-91015.txt` — CA Government Code §§ 91000-91015 (criminal enforcement chapter)
- `gov-82030-82048.5.txt` — CA Government Code §§ 82030-82048.5 (additional definitions slice)
- `gov-82000-82015.txt` — CA Government Code §§ 82000-82015 (definitions, narrower than the 82000-82054 slice in the manifest)

These look like artifacts of an earlier retrieval expansion that didn't make it into the final manifest — the manifest endorses `gov-82000-82054-2007fallback.txt` (broader definitions, 2007 vintage) and `gov-83100-83124.txt` (civil enforcement). The orphans are not corrupting anything; they just aren't part of the official bundle that downstream code reads.

**Not touched per the experiment-data-integrity rule.** User decision pending (leave / re-index into manifest / move to `sections/_unused/`).

## Implications for this branch

- **No re-retrieval needed for pilot states at PRI 2010 vintage.** The 6 pilot bundles (CA/TX/NY/WI/WY 2010 + OH 2010) are intact and usable.
- The discovery + retrieval pipeline this branch is building should **skip these via resume logic** (checkpoint-exists check), not re-fetch them.
- The integrity check pattern is reusable: any future "did we lose statute bundles to a crash?" question can be answered in 5 minutes by re-running the manifest-hash-check approach above.
