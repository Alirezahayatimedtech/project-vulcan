from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from vulcan.models.spec import SafetyFinding, SystemSpec


class EvidenceStatus(str, Enum):
    VERIFIED = "verified"
    DISCOVERED = "discovered"
    DECLARED = "declared"
    INFERRED = "inferred"
    CONFLICTING = "conflicting"
    UNKNOWN = "unknown"


class EnvironmentFact(BaseModel):
    key: str
    value: Any | None = None
    status: EvidenceStatus = EvidenceStatus.UNKNOWN
    source_type: str | None = None
    source: str | None = None
    observed_at: str | None = None


class EnvironmentSpec(BaseModel):
    clinic_name: str
    specialty: str = "ophthalmology"
    facts: list[EnvironmentFact] = Field(default_factory=list)

    def fact_map(self) -> dict[str, EnvironmentFact]:
        return {fact.key: fact for fact in self.facts}


class GroundedForgeRequest(BaseModel):
    need: str = Field(min_length=10)
    environment: EnvironmentSpec


class EnvironmentReadiness(BaseModel):
    ready: bool
    required_facts: list[str]
    missing_facts: list[str]
    unusable_facts: list[str]


class GroundedForgeResult(BaseModel):
    environment_ready: bool
    readiness: EnvironmentReadiness
    specification: SystemSpec | None = None
    safety_findings: list[SafetyFinding] = Field(default_factory=list)
    deployable: bool = False
