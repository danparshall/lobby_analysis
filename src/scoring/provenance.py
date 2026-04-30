"""Provenance helpers: prompt sha, run ids, row stamping."""

from __future__ import annotations

import hashlib
import uuid
from datetime import datetime, timezone
from pathlib import Path

from scoring.models import CoverageTier, RunMetadata, Rubric, ScoredItem, ScoredRow

PROMPT_PATH = Path("src/scoring/scorer_prompt.md")
# Pinned model for all scoring subagents. Bump deliberately; every change invalidates
# prior runs' comparability.
MODEL_VERSION = "claude-opus-4-7"


def prompt_sha(repo_root: Path) -> str:
    return hashlib.sha256((repo_root / PROMPT_PATH).read_bytes()).hexdigest()


def new_run_id() -> str:
    return uuid.uuid4().hex[:12]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def stamp_rows(
    items: list[ScoredItem],
    *,
    state: str,
    rubric: Rubric,
    coverage_tier: CoverageTier,
    prompt_sha_hex: str,
    snapshot_manifest_sha: str,
    run_id: str,
    run_timestamp: str,
) -> list[ScoredRow]:
    return [
        ScoredRow(
            state=state,
            rubric_name=rubric.name,
            item_id=si.item_id,
            score=si.score,
            evidence_quote_or_url=si.evidence_quote_or_url,
            source_artifact=si.source_artifact,
            confidence=si.confidence,
            unable_to_evaluate=si.unable_to_evaluate,
            notes=si.notes,
            coverage_tier=coverage_tier,
            model_version=MODEL_VERSION,
            prompt_sha=prompt_sha_hex,
            rubric_sha=rubric.sha,
            snapshot_manifest_sha=snapshot_manifest_sha,
            run_id=run_id,
            run_timestamp=run_timestamp,
        )
        for si in items
    ]


def build_run_metadata(
    *,
    state: str,
    run_id: str,
    run_timestamp: str,
    snapshot_date: str,
    snapshot_manifest_sha: str,
    prompt_sha_hex: str,
    rubrics: dict[str, Rubric],
    coverage_tier: CoverageTier,
) -> RunMetadata:
    return RunMetadata(
        state=state,
        run_id=run_id,
        run_timestamp=run_timestamp,
        snapshot_date=snapshot_date,
        snapshot_manifest_sha=snapshot_manifest_sha,
        prompt_sha=prompt_sha_hex,
        prompt_path=str(PROMPT_PATH),
        model_version=MODEL_VERSION,
        rubric_shas={name: r.sha for name, r in rubrics.items()},
        coverage_tier=coverage_tier,
    )
