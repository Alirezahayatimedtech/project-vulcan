from __future__ import annotations

from pydantic import BaseModel, Field

# Design analogy: generated software needs controlled promotion, monitoring and rollback.
# Palantir Apollo/platform architecture: https://www.palantir.com/docs/foundry/architecture-center/platforms


class DeploymentStage(BaseModel):
    name: str
    requires_approval: bool = True
    checks: list[str] = Field(default_factory=list)


class DeploymentPlan(BaseModel):
    stages: list[DeploymentStage]
    rollback_required: bool = True


def default_deployment_plan() -> DeploymentPlan:
    return DeploymentPlan(
        stages=[
            DeploymentStage(
                name="clinicgym",
                requires_approval=False,
                checks=["acceptance_tests", "safety_gate", "environment_contract"],
            ),
            DeploymentStage(
                name="silent_validation",
                checks=["expert_review", "audit_logging", "no_patient_facing_actions"],
            ),
            DeploymentStage(
                name="limited_pilot",
                checks=["human_approval", "monitoring", "rollback_ready"],
            ),
        ],
        rollback_required=True,
    )
