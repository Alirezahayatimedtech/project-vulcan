from __future__ import annotations

from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field


class RiskLevel(str, Enum):
    ADMINISTRATIVE = "administrative"
    CLINICIAN_SUPPORT = "clinician_support"
    CLINICAL_DECISION_SUPPORT = "clinical_decision_support"
    HIGH_RISK_AUTONOMOUS = "high_risk_autonomous"


class AgentRole(str, Enum):
    PLANNER = "planner"
    RESEARCHER = "researcher"
    ENGINEER = "engineer"
    TESTER = "tester"
    CRITIC = "critic"


class DataInput(BaseModel):
    name: str
    source: str
    standard: str | None = None
    required: bool = True


class Integration(BaseModel):
    system: str
    standard: str | None = None
    direction: Literal["read", "write", "read_write"] = "read"


class WorkflowStep(BaseModel):
    id: str
    name: str
    actor: str
    action: str
    requires_human_approval: bool = False


class SystemSpec(BaseModel):
    name: str
    objective: str
    clinical_domain: str = "general"
    actors: list[str] = Field(default_factory=list)
    data_inputs: list[DataInput] = Field(default_factory=list)
    integrations: list[Integration] = Field(default_factory=list)
    workflow_steps: list[WorkflowStep] = Field(default_factory=list)
    output_artifacts: list[str] = Field(default_factory=list)
    human_approval_points: list[str] = Field(default_factory=list)
    risk_level: RiskLevel = RiskLevel.CLINICIAN_SUPPORT
    audit_required: bool = True
    notes: list[str] = Field(default_factory=list)


class ForgeRequest(BaseModel):
    need: str = Field(min_length=10)


class SafetyFinding(BaseModel):
    severity: Literal["info", "warning", "block"]
    code: str
    message: str


class IntelligenceTrace(BaseModel):
    source: Literal["model", "deterministic", "deterministic-fallback"]
    provider: str
    model: str | None = None
    role: AgentRole = AgentRole.PLANNER


class ForgeResult(BaseModel):
    specification: SystemSpec
    safety_findings: list[SafetyFinding]
    deployable: bool
    intelligence: IntelligenceTrace | None = None


class IntelligenceRequest(BaseModel):
    role: AgentRole
    task: str = Field(min_length=5)
    context: str | None = None


class IntelligenceResult(BaseModel):
    role: AgentRole
    output: str
    provider: str
    model: str
