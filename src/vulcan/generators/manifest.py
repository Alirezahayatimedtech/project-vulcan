from __future__ import annotations

from vulcan.models.spec import SystemSpec


def build_application_manifest(spec: SystemSpec) -> dict:
    """Produce a vendor-neutral application manifest from a SystemSpec."""
    return {
        "application": {
            "name": spec.name,
            "domain": spec.clinical_domain,
            "objective": spec.objective,
        },
        "data": [item.model_dump() for item in spec.data_inputs],
        "integrations": [item.model_dump() for item in spec.integrations],
        "workflow": [item.model_dump() for item in spec.workflow_steps],
        "ui": {
            "views": [
                "patient_list",
                "patient_detail",
                "assessment_review",
                "audit_log",
            ]
        },
        "governance": {
            "risk_level": spec.risk_level.value,
            "human_approval_points": spec.human_approval_points,
            "audit_required": spec.audit_required,
        },
    }
