"""Pydantic models for scoring inputs and outputs."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, model_validator

Confidence = Literal["high", "medium", "low"]
# data_type is author-defined per rubric (e.g. binary, ordinal_0_to_15,
# numeric_percent_or_null, numeric_usd_or_null, text) — kept as free str, the scorer
# reads the literal value + scoring_guidance to decide output shape.
DataType = str
ScoringDirection = Literal["normal", "reverse"]
CoverageTier = Literal["clean", "partial_waf", "spa_pending_playwright", "inaccessible"]


class RubricItem(BaseModel):
    """One row from a rubric CSV. Field names normalized across the three rubrics."""

    item_id: str
    category: str
    item_text: str
    data_type: DataType
    source: str
    scoring_direction: ScoringDirection
    scoring_guidance: str
    notes: str = ""


class Rubric(BaseModel):
    name: Literal["pri_accessibility", "pri_disclosure_law", "focal_indicators"]
    items: list[RubricItem]
    sha: str  # sha256 of the rubric CSV bytes


class SnapshotArtifact(BaseModel):
    """One fetched file in a state's snapshot."""

    url: str
    role: str
    source: Literal["seed", "linked"]
    http_status: int
    content_type: str
    bytes: int
    sha256: str
    local_path: str
    suspicious_challenge_stub: bool = False
    notes: str = ""


class SnapshotBundle(BaseModel):
    """A state's frozen snapshot corpus."""

    state_abbr: str
    snapshot_date: str
    artifacts: list[SnapshotArtifact]
    manifest_sha: str  # sha256 of the manifest.json bytes
    summary: str = ""
    skipped: list[dict] = Field(default_factory=list)


class StatuteArtifact(BaseModel):
    """One retrieved statute-text file in a state's statute bundle."""

    url: str
    role: Literal["statute"] = "statute"
    sha256: str
    bytes: int
    local_path: str  # relative to the bundle directory, e.g. "sections/gov-86100-86118.txt"


class StatuteBundle(BaseModel):
    """A state's retrieved statute-text corpus for a given vintage year.

    Written under `data/statutes/<STATE>/<YEAR>/` alongside `manifest.json`.
    Consumed by the scorer via `statute_loader.load_statute_bundle` and fed to
    `bundle.build_subagent_brief` with role=statute.
    """

    state_abbr: str
    vintage_year: int
    year_delta: int  # 0 if exact, negative for pre-target, positive for post-target
    direction: Literal["exact", "pre", "post"]
    pri_state_reviewed: bool
    retrieved_at: str  # ISO-8601 UTC timestamp
    artifacts: list[StatuteArtifact]
    manifest_sha: str = ""  # sha256 of manifest.json bytes; populated by loader


class ScoredItem(BaseModel):
    """Raw output from the scorer subagent for a single rubric item."""

    item_id: str
    score: int | float | str | None
    evidence_quote_or_url: str | None
    source_artifact: str | None
    confidence: Confidence
    unable_to_evaluate: bool
    notes: str = ""

    @model_validator(mode="after")
    def _check_null_when_unable(self) -> "ScoredItem":
        if self.unable_to_evaluate and self.score is not None:
            raise ValueError(
                f"{self.item_id}: unable_to_evaluate=true requires score=null"
            )
        return self


class ScoredRow(BaseModel):
    """A ScoredItem plus orchestrator-stamped provenance."""

    state: str
    rubric_name: str
    item_id: str
    score: int | float | str | None
    evidence_quote_or_url: str | None
    source_artifact: str | None
    confidence: Confidence
    unable_to_evaluate: bool
    notes: str
    coverage_tier: CoverageTier
    model_version: str
    prompt_sha: str
    rubric_sha: str
    snapshot_manifest_sha: str
    run_id: str
    run_timestamp: str


class RunMetadata(BaseModel):
    state: str
    run_id: str
    run_timestamp: str
    snapshot_date: str
    snapshot_manifest_sha: str
    prompt_sha: str
    prompt_path: str
    model_version: str
    rubric_shas: dict[str, str]
    coverage_tier: CoverageTier
    temperature: float = 0.0
