from __future__ import annotations

from enum import Enum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class RiskLevel(str, Enum):
    ADMINISTRATIVE = "administrative"
    CLINICIAN_SUPPORT = "clinician_support"
    CLINICAL_DECISION_SUPPORT = "clinical_decision_support"
    HIGH_RISK_AUTONOMOUS = "high_risk_autonomous"


class ClinicalActionType(str, Enum):
    INFORMATIONAL = "informational"
    RETRIEVE = "retrieve"
    ASSESS = "assess"
    SCHEDULE = "schedule"
    RECORD = "record"
    CLINICAL_ORDER = "clinical_order"
    MEDICATION_CHANGE = "medication_change"
    RESPIRATORY_SUPPORT_CHANGE = "respiratory_support_change"
    DISCHARGE = "discharge"


class AgentRole(str, Enum):
    PLANNER = "planner"
    RESEARCHER = "researcher"
    ENGINEER = "engineer"
    TESTER = "tester"
    CRITIC = "critic"


class DataInput(StrictModel):
    name: str
    source: str
    standard: str | None = None
    required: bool = True


class Integration(StrictModel):
    system: str
    standard: str | None = None
    direction: Literal["read", "write", "read_write"] = "read"


class WorkflowStep(StrictModel):
    id: str
    name: str
    actor: str
    action: str
    action_type: ClinicalActionType = ClinicalActionType.INFORMATIONAL
    requires_human_approval: bool = False


class SystemSpec(StrictModel):
    spec_version: Literal["0.2"] = "0.2"
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


class ForgeRequest(StrictModel):
    need: str = Field(min_length=10)


class ROPCase(StrictModel):
    patient_id: str = Field(min_length=1, max_length=64, pattern=r"^[A-Za-z0-9._-]+$")
    gestational_age_weeks: float = Field(ge=20, le=45)
    birth_weight_g: int = Field(ge=250, le=7000)
    exam_postmenstrual_age_weeks: float | None = Field(default=None, ge=20, le=60)
    sex: Literal["female", "male", "other", "unknown"] = "unknown"


class ROPForgeRequest(StrictModel):
    need: str = Field(min_length=10)
    case: ROPCase
    execute_fhir: bool = False


class SafetyFinding(StrictModel):
    severity: Literal["info", "warning", "block"]
    code: str
    message: str


class IntelligenceTrace(StrictModel):
    source: Literal["model", "deterministic", "deterministic-fallback"]
    provider: str
    model: str | None = None
    role: AgentRole = AgentRole.PLANNER


class ForgeResult(StrictModel):
    specification: SystemSpec
    safety_findings: list[SafetyFinding]
    deployable: bool
    intelligence: IntelligenceTrace | None = None


class ROPForgeResult(StrictModel):
    specification: SystemSpec
    safety_findings: list[SafetyFinding]
    deployable: bool
    fhir_bundle: dict | None = None
    fhir_execution: dict | None = None
    intelligence: IntelligenceTrace | None = None


class IntelligenceRequest(StrictModel):
    role: AgentRole
    task: str = Field(min_length=5)
    context: str | None = None


class IntelligenceResult(StrictModel):
    role: AgentRole
    output: str
    provider: str
    model: str
