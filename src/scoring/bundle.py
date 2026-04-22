"""Assemble a per-(state, rubric) prompt bundle for a scoring subagent.

The bundle is a self-contained brief the subagent can read end-to-end:
  - state abbreviation
  - rubric name + items (JSON array)
  - snapshot artifact index (role, path, stub-flag, size)
  - instructions: read the locked scorer prompt, read the artifacts, return JSON

We do NOT inline artifact bodies — the subagent reads them via the Read tool against
the repo-root-relative paths, which keeps the prompt compact and lets the subagent
choose which artifacts to read in depth based on the item under evaluation.
"""

from __future__ import annotations

import json
from pathlib import Path

from scoring.models import Rubric, SnapshotBundle, StatuteBundle


def build_subagent_brief(
    *,
    state: str,
    rubric: Rubric,
    snapshot: SnapshotBundle,
    repo_root: Path,
    scorer_prompt_path: Path,
    output_json_path: Path,
) -> str:
    """Return the full subagent instruction string.

    The subagent writes its JSON output to `output_json_path` so the orchestrator
    can read/parse/validate without relying on text-channel return formatting.
    """
    artifact_index = [
        {
            "role": a.role,
            "local_path": a.local_path,
            "bytes": a.bytes,
            "http_status": a.http_status,
            "content_type": a.content_type,
            "suspicious_challenge_stub": a.suspicious_challenge_stub,
            "url": a.url,
            "notes": a.notes,
        }
        for a in snapshot.artifacts
    ]
    rubric_items = [ri.model_dump() for ri in rubric.items]

    brief = f"""You are a rubric-scoring subagent.

Read the locked scorer prompt first, then read the artifacts you need, then write your output JSON to the specified path.

## Step 1 — read the locked prompt (follow it exactly)

Read this file with the Read tool, in full:
  {scorer_prompt_path}

All rules in that prompt are load-bearing. No preamble in your output.

## Step 2 — state and rubric

- State: {state}
- Rubric name: {rubric.name}
- Rubric item count: {len(rubric.items)}

Rubric items (JSON):

```json
{json.dumps(rubric_items, indent=2, ensure_ascii=False)}
```

## Step 3 — snapshot bundle

Snapshot date: {snapshot.snapshot_date}
Manifest sha256: {snapshot.manifest_sha}
Manifest summary: {snapshot.summary!r}

Artifacts (all paths are relative to repo root `{repo_root}`):

```json
{json.dumps(artifact_index, indent=2, ensure_ascii=False)}
```

Read artifacts you need via the Read tool (prepend `{repo_root}/` to each `local_path`). Prefer artifacts whose `role` matches the rubric item's evidence hint. Skip artifacts with `suspicious_challenge_stub: true` as positive evidence — they indicate WAF blocks, not absence of the feature.

## Step 4 — write output

Write a single JSON array (one object per rubric item, in rubric order) to:

  {output_json_path}

Use the Write tool. The array must have exactly {len(rubric.items)} objects, each matching the schema defined in the locked prompt. Do NOT include orchestrator-stamped fields (model_version, prompt_sha, rubric_sha, snapshot_manifest_sha, state, rubric_name, run_id, run_timestamp, coverage_tier).

After writing the file, respond with a single line: `DONE <n items written>`. No other text.
"""
    return brief


def build_statute_subagent_brief(
    *,
    state: str,
    rubric: Rubric,
    statute: StatuteBundle,
    repo_root: Path,
    scorer_prompt_path: Path,
    output_json_path: Path,
) -> str:
    """Return a subagent brief for scoring against a statute bundle.

    Identical to `build_subagent_brief` except the "corpus" section tells the
    scorer the artifacts are state statute text (not portal content), so the
    scorer interprets source material correctly. The rubric-item prompts and
    the locked scorer prompt body are unchanged.
    """
    artifact_index = [
        {
            "role": a.role,
            "local_path": a.local_path,
            "bytes": a.bytes,
            "url": a.url,
        }
        for a in statute.artifacts
    ]
    rubric_items = [ri.model_dump() for ri in rubric.items]
    brief = f"""You are a rubric-scoring subagent.

Read the locked scorer prompt first, then read the artifacts you need, then write your output JSON to the specified path.

## Step 1 — read the locked prompt (follow it exactly)

Read this file with the Read tool, in full:
  {scorer_prompt_path}

All rules in that prompt are load-bearing. No preamble in your output.

## Step 2 — state and rubric

- State: {state}
- Rubric name: {rubric.name}
- Rubric item count: {len(rubric.items)}

Rubric items (JSON):

```json
{json.dumps(rubric_items, indent=2, ensure_ascii=False)}
```

## Step 3 — statute bundle

The artifacts below are state statute text (not portal content). Score the rubric against the statute text as written — this tells you what the law requires, not what any portal happens to expose.

Vintage year: {statute.vintage_year} ({statute.direction}, delta {statute.year_delta:+d})
Retrieved at: {statute.retrieved_at}
Manifest sha256: {statute.manifest_sha}

Artifacts (all paths are relative to repo root `{repo_root}`):

```json
{json.dumps(artifact_index, indent=2, ensure_ascii=False)}
```

Read artifacts you need via the Read tool (prepend `{repo_root}/` to each `local_path`). These files contain raw statute text extracted from Justia — no WAF stubs, no portal navigation to skip.

## Step 4 — write output

Write a single JSON array (one object per rubric item, in rubric order) to:

  {output_json_path}

Use the Write tool. The array must have exactly {len(rubric.items)} objects, each matching the schema defined in the locked prompt. Do NOT include orchestrator-stamped fields (model_version, prompt_sha, rubric_sha, snapshot_manifest_sha, state, rubric_name, run_id, run_timestamp, coverage_tier).

After writing the file, respond with a single line: `DONE <n items written>`. No other text.
"""
    return brief
