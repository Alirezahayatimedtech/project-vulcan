from __future__ import annotations

from pydantic import BaseModel, Field

from vulcan.models.environment import EnvironmentReadiness, EnvironmentSpec


class CodingCandidate(BaseModel):
    id: str
    parent_id: str | None = None
    generation: int = 0
    role: str = "seed"
    files: dict[str, str] = Field(default_factory=dict)
    score: float = 0.0
    metrics: dict[str, float] = Field(default_factory=dict)
    hard_gate_passed: bool = False
    logs: list[str] = Field(default_factory=list)


class EvolutionRequest(BaseModel):
    need: str = Field(min_length=10)
    environment: EnvironmentSpec
    iterations: int = Field(default=6, ge=1, le=20)


class EvolutionResult(BaseModel):
    environment_ready: bool
    readiness: EnvironmentReadiness
    method: str = "ERA-inspired Flat-UCB software evolution"
    blocked_reason: str | None = None
    best_candidate: CodingCandidate | None = None
    candidates_evaluated: int = 0
    search_trace: list[CodingCandidate] = Field(default_factory=list)
