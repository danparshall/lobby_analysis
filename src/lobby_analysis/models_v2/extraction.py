"""Containers for a complete state-vintage extraction run.

`StateVintageExtraction` is the per-(state, vintage) deliverable unit. Its
`cells` dict is keyed by `(row_id, axis)` tuples matching the canonical
186-cell roster. `ExtractionRun` is a parallel provenance wrapper recording
the model version, prompt sha, and timestamps for the run that produced an
extraction.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, model_validator

from .cells import CompendiumCell


class StateVintageExtraction(BaseModel):
    """The full extraction output for one (state, vintage, run) tuple.

    Each key in `cells` is a `(row_id, axis)` tuple; the cell stored under
    that key must carry the matching `cell_id`. The post-validator enforces
    this consistency rule so drift between key and cell_id surfaces as a
    validation error at construction time rather than downstream.
    """

    model_config = ConfigDict(strict=True)

    state: str
    vintage: int
    run_id: str
    cells: dict[tuple[str, str], CompendiumCell]

    @model_validator(mode="after")
    def _cell_id_matches_key(self) -> StateVintageExtraction:
        for key, cell in self.cells.items():
            if cell.cell_id != key:
                raise ValueError(
                    f"Cell stored under {key!r} carries cell_id={cell.cell_id!r}; "
                    f"key and cell_id must match."
                )
        return self


class ExtractionRun(BaseModel):
    """Provenance record for an extraction run.

    `prompt_sha` is the SHA hash of the prompt template + per-row instructions
    + chunk-frame preamble used for this run, so identical conditions can be
    reproduced. `model_version` carries the exact model used (e.g.
    "claude-opus-4-7"). `completed_at` is None while the run is still in
    flight.
    """

    model_config = ConfigDict(strict=True)

    run_id: str
    model_version: str
    prompt_sha: str
    started_at: datetime
    completed_at: datetime | None = None
