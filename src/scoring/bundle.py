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

You MUST Read every statute file listed above before scoring any rubric item. Lobbying statutes are layered (general rule → exemptions → exceptions to exemptions → separate disclosure triggers in adjacent sections). Skipping files reliably produces under-scoring on the E-series and over-application of exemption-based reasoning.

## Step 4 — write outputs (TWO files)

### 4a. Files-read manifest

First, write a JSON object listing every statute file you Read in step 3, to:

  {output_json_path.parent / "files_read.json"}

Schema:
```json
{{
  "statute_files_read": ["sections/<filename>.txt", "..."],
  "notes": "optional: any file you skipped and why (e.g. 'irrelevant — covers school finance only')"
}}
```

The `statute_files_read` list MUST contain every file from the artifact index above unless you cite a specific reason in `notes`. The orchestrator will fail finalization if any bundle file is missing without explanation.

### 4b. Scored items

Write a single JSON array (one object per rubric item, in rubric order) to:

  {output_json_path}

Use the Write tool. The array must have exactly {len(rubric.items)} objects, each matching the schema defined in the locked prompt. Do NOT include orchestrator-stamped fields (model_version, prompt_sha, rubric_sha, snapshot_manifest_sha, state, rubric_name, run_id, run_timestamp, coverage_tier).

After writing both files, respond with a single line: `DONE <n items written>`. No other text.
"""
    return brief


def build_retrieval_subagent_brief(
    *,
    state: str,
    rubric: Rubric,
    statute: StatuteBundle,
    repo_root: Path,
    retrieval_prompt_path: Path,
    output_json_path: Path,
    hop: int = 1,
) -> str:
    """Return a subagent brief for the cross-reference retrieval agent.

    The brief gives the agent:
    - The locked retrieval prompt
    - The PRI rubric items (so it knows what cross-references are relevant)
    - The current artifact index (so it can read core chapters and skip duplicates)
    - URL pattern examples (so it can construct URLs for referenced sections)
    - The hop number and 2-hop limit
    """
    artifact_index = [
        {
            "role": a.role,
            "local_path": a.local_path,
            "bytes": a.bytes,
            "url": a.url,
            "hop": a.hop,
        }
        for a in statute.artifacts
    ]
    rubric_items = [
        {"item_id": ri.item_id, "category": ri.category, "item_text": ri.item_text}
        for ri in rubric.items
    ]
    url_examples = [a.url for a in statute.artifacts if a.role == "core_chapter"][:3]

    brief = f"""You are a cross-reference retrieval agent.

Read the locked retrieval prompt first, then read the statute artifacts, identify cross-references relevant to the rubric, and write your output JSON.

## Step 1 — read the locked prompt (follow it exactly)

Read this file with the Read tool, in full:
  {retrieval_prompt_path}

All rules in that prompt are load-bearing.

## Step 2 — state and vintage

- State: {state}
- Vintage year: {statute.vintage_year}
- Current hop: {hop} (2-hop limit — {"this is your last pass" if hop >= 2 else "you may be invoked again for hop " + str(hop + 1)})

## Step 3 — rubric items (what the scorer needs to answer)

These are the PRI disclosure-law rubric items. Your job is to find cross-references that provide information the scorer needs for these items.

```json
{json.dumps(rubric_items, indent=2, ensure_ascii=False)}
```

## Step 4 — current statute bundle

Read these artifacts via the Read tool (prepend `{repo_root}/` to each `local_path`):

```json
{json.dumps(artifact_index, indent=2, ensure_ascii=False)}
```

## Step 5 — URL pattern

These are the Justia URLs for this state and vintage. Use them to infer the URL pattern for constructing new URLs:

{chr(10).join(f"  - {u}" for u in url_examples)}

## Step 6 — write output

Write your cross-reference JSON to:

  {output_json_path}

Use the Write tool. Follow the output schema defined in the locked prompt exactly.

After writing the file, respond with: `DONE <n cross-references found>, <m unresolvable>`
"""
    return brief
